import torch
import numpy as np
import mmcv, cv2
from PIL import Image, ImageDraw
import subprocess
import os
from pydub import AudioSegment
from facenet_pytorch import MTCNN, InceptionResnetV1, extract_face
from numpy.linalg import norm


class Audio_Processing:

	def __init__(self):
		pass


	def preprocessing(self, path):
		# Separate audio from video
		command = f'ffmpeg -i {path} -ar 16000 preprocessing/audio/original.wav'
		subprocess.call(command, shell=True)


	def mix_audio(self, curr_dir, seq):
		audio_sequence = []
		for i in seq:
			audio_sequence.append(os.path.join(curr_dir, "preprocessing/audio/" + str(i) + ".wav"))

		# Doing it naively to simplify mixing of audios
		output = AudioSegment.from_wav(audio_sequence[0])

		for audio in audio_sequence[1:]:
			s = AudioSegment.from_wav(audio)
			output = output.overlay(s)

		# Saving audio file locally and then opening it again for playing
		output.export(os.path.join(curr_dir, 'preprocessing/audio/mixed.wav'), format="wav")



class Video_Processing:

	def __init__(self):
		self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
		print('Running on device: {}'.format(self.device))

		self.mtcnn = MTCNN(keep_all=True, device=self.device).eval()
		self.resnet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)

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
			cropped_tensors = self.resnet(cropped_tensors)
			cropped_tensors = cropped_tensors.detach()
			if self.device.type == "cuda":
				cropped_tensors = cropped_tensors.cpu()
			cropped_tensors = cropped_tensors.numpy()
			self.embeddings_initial.append((cropped_tensors,((x1+x2)/2, (y1+y2)/2)))
			self.total_people += 1

		# Seperate video with no audio

		command = f'ffmpeg -i {path} -r 25 -c copy -an preprocessing/video/a.mp4'
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
			bouding_box = [x for _,x in sorted(zip(prob,bouding_box), reverse=True)] #Sorting reverse as per prob

			f1 = frame.copy()
			draw = ImageDraw.Draw(f1)

			for box in bouding_box[:self.total_people]:
				x1,y1,x2,y2 = box
				if(x1 > x2):
					x1, x2 = x2, x1
				if(y1 > y2):
					y1, y2 = y2, y1

				pos = ((x1+x2)/2, (y1+y2)/2)

				draw.rectangle(box.tolist(), outline=(255, 0, 0), width=3)

				cropped_tensors = extract_face(frame, (x1,y1,x2,y2)).to(self.device).view(-1,3,160,160)
				emb = self.resnet(cropped_tensors)
				emb = emb.detach()
				if self.device.type == "cuda":
					emb = emb.cpu()
				emb = emb.numpy()
				
				idx = -1
				min_dist = 10**9
				for i,e in enumerate(self.embeddings_initial):
					d = emb-e[0]
					d = d.reshape(512)

					# https://github.com/cmusatyalab/openface/blob/master/demos/compare.py
					dist = np.dot(d,d)  # https://cmusatyalab.github.io/openface/demo-2-comparison/
					x11, y11 = e[1]
					x22, y22 = pos

					# Adding spatial information
					dist += abs(x11-x22) + abs(y11-y22)
					#print(dist, min_dist)
					if(dist < min_dist):
						idx = i
						min_dist = dist
				a[idx].append(emb)

				# testing for face tracking
				
				crop = frame.crop((x1,y1,x2,y2))
				crop = cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2BGR)
				cv2.imshow(str(idx), crop)
				cv2.waitKey(1)
				
			cv2.imshow("Frames", cv2.cvtColor(np.array(f1), cv2.COLOR_RGB2BGR))
			cv2.waitKey(1)
			print(len(a[0]))


		for i in range(self.total_people):
			print(len(a[i]))
		return a


if __name__ == '__main__':
	c = Audio_Processing()
	c.preprocessing('a.mp4')	

	c = Video_Processing()
	c.preprocessing('a.mp4')
