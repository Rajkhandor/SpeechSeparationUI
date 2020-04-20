from facenet_pytorch import MTCNN
import torch
import numpy as np
import mmcv, cv2
from PIL import Image, ImageDraw
import subprocess
import os
from pydub import AudioSegment


class Audio_Processing:

	def __init__(self):
		pass


	def preprocessing(self, path):
		# Separate audio from video

		#command = f'ffmpeg -i {path} preprocessing/audio/original.mp3'
		#subprocess.call(command)
		pass

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
		device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
		print('Running on device: {}'.format(device))

		self.mtcnn = MTCNN(keep_all=True, device=device)


	def preprocessing(self, path):
		video = mmcv.VideoReader(path)
		frame0 = Image.fromarray(cv2.cvtColor(video[0], cv2.COLOR_BGR2RGB))  # Assumption - First frame has all the speaker's faces.

		bouding_box, prob = self.mtcnn.detect(frame0)
		print(bouding_box)
		print(prob)

		count=0

		for box in bouding_box:
			x1,y1,x2,y2 = box
			if(x1 > x2):
				x1, x2 = x2, x1
			if(y1 > y2):
				y1, y2 = y2, y1

			print(x1,y1)
			print(x2,y2)

			cropped = frame0.crop((x1,y1,x2,y2))
			cropped.save("preprocessing/faces/Cropped" + str(count) + ".png")
			count+=1

		# Seperate video with no audio

		#command = f'ffmpeg -i {path} -c copy -an preprocessing/video/a.mp4'
		#subprocess.call(command)



if __name__ == '__main__':
	c = Audio_Processing()
	c.preprocessing('a.mp4')	

	c = Video_Processing()
	c.preprocessing('a.mp4')