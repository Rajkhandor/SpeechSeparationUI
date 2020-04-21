import torch
import numpy as np
import mmcv, cv2
from PIL import Image, ImageDraw
import subprocess
import os
from pydub import AudioSegment
from facenet_pytorch import MTCNN, InceptionResnetV1, extract_face


class Audio_Processing:

	def __init__(self):
		pass


	def preprocessing(self, path):
		# Separate audio from video
		command = f'ffmpeg -i {path} preprocessing/audio/original.mp3'
		subprocess.call(command, shell=True)


	def mix_audio(self, curr_dir, seq):
		audio_sequence = []
		for i in seq:
			audio_sequence.append(os.path.join(curr_dir, "preprocessing/audio/" + str(i) + ".mp3"))

		# Doing it naively to simplify mixing of audios
		output = AudioSegment.from_mp3(audio_sequence[0])

		for audio in audio_sequence[1:]:
			s = AudioSegment.from_mp3(audio)
			output = output.overlay(s)

		# Saving audio file locally and then opening it again for playing
		output.export(os.path.join(curr_dir, 'preprocessing/audio/mixed.mp3'), format="mp3")



class Video_Processing:

	def __init__(self):
		self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
		print('Running on device: {}'.format(self.device))

		self.mtcnn = MTCNN(keep_all=True, device=self.device)
		self.resnet = InceptionResnetV1(pretrained="vggface2").eval()

		self.total_people = 0
		self.embeddings_initial = []


	def preprocessing(self, path):
		video = mmcv.VideoReader(path)
		frame0 = Image.fromarray(cv2.cvtColor(video[0], cv2.COLOR_BGR2RGB))  # Assumption - First frame has all the speaker's faces.

		bouding_box, prob = self.mtcnn.detect(frame0)
		print(bouding_box)
		print(prob)

		self.total_people = 0
		for box in bouding_box:
			x1,y1,x2,y2 = box
			if(x1 > x2):
				x1, x2 = x2, x1
			if(y1 > y2):
				y1, y2 = y2, y1

			print(x1,y1)
			print(x2,y2)

			cropped = frame0.crop((x1,y1,x2,y2))

			cropped.save("preprocessing/faces/Cropped" + str(self.total_people) + ".png")

			cropped_tensors = extract_face(frame0, (x1,y1,x2,y2)).to(self.device).view(-1,3,160,160)
			self.embeddings_initial.append(self.resnet(cropped_tensors))
			self.total_people += 1

		# Seperate video with no audio

		command = f'ffmpeg -i {path} -c copy -an preprocessing/video/a.mp4'
		subprocess.call(command, shell=True)



	def embeddings(self, path):
		video = mmcv.VideoReader(path)
		frames = [Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) for frame in video[1:]]

		a = dict()
		for i in range(self.total_people):
			a[i] = []

		count = 0 
		for frame in frames:
			bouding_box, prob = self.mtcnn.detect(frame)

			for box in bouding_box:
				x1,y1,x2,y2 = box
				if(x1 > x2):
					x1, x2 = x2, x1
				if(y1 > y2):
					y1, y2 = y2, y1

				cropped_tensors = extract_face(frame, (x1,y1,x2,y2)).to(self.device).view(-1,3,160,160)
				emb = self.resnet(cropped_tensors)
				
				idx = -1
				min_dist = 10**9
				for i,e in enumerate(self.embeddings_initial):
					d = emb-e
					d = d.detach().numpy().reshape(512)

					# https://github.com/cmusatyalab/openface/blob/master/demos/compare.py
					dist = np.dot(d,d)  # https://cmusatyalab.github.io/openface/demo-2-comparison/
					if(dist < min_dist):
						idx = i
						min_dist = dist
				a[idx].append(emb)
		return a


if __name__ == '__main__':
	c = Audio_Processing()
	c.preprocessing('a.mp4')	

	c = Video_Processing()
	c.preprocessing('a.mp4')