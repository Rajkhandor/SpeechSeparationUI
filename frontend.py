from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *

from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QStyle, QFileDialog, QCheckBox, QSizePolicy
from PyQt5.QtGui import QIcon

import os
import sys
import shutil
import json
import main
from PyQt5.QtGui import QPainter, QBrush, QPen

from PyQt5 import QtCore, QtGui, QtWidgets

from utility import Video_Processing, Audio_Processing

import librosa
import numpy as np
from src import generate_audio, load_model

import torch

MODEL_PATH = "/tmp/last_full.pth"

class VideoPlayer(main.Ui_window, QMainWindow):

    def __init__(self):
        super(VideoPlayer, self).__init__()
        self.setupUi(self)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # ---------------------------------------------------------------------------
        # Do not modify UI elements at all

        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.openAction.triggered.connect(self.openFile)
        self.exitAction.triggered.connect(self.exitCall)
        self.pre_pb.clicked.connect(lambda x: self.pre_processing())
        self.post_pb.clicked.connect(lambda x: self.post_processing())
        self.separate_audio_pb.clicked.connect(lambda x: self.separate_audio())
        self.play_chosen_pb.clicked.connect(self.mix_audio_and_play)

        self.media_player.setVideoOutput(self.videoWidget)
        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.media_player.error.connect(self.handleError)


        # ---------------------------------------------------------------------------
        
        self.audio_player = None

        self.curr_dir = os.getcwd()

        self.face_cb = []
        self.input_file_name = ''
        self.is_preprocessing_done = False
        self.is_audio_separated = False



    def pre_processing(self):

        if(self.input_file_name == ''):
            return

        if(os.path.exists('preprocessing')):
            shutil.rmtree('preprocessing')
        os.makedirs('preprocessing/audio')
        os.makedirs('preprocessing/faces')
        os.makedirs('preprocessing/video')


        video_processing = Video_Processing()
        video_processing.preprocessing(self.input_file_name)
        self.emb = video_processing.embeddings(self.input_file_name)
        self.device = video_processing.device

        del video_processing

        c = Audio_Processing()
        c.preprocessing(self.input_file_name)


        # Hide all the previous shown face checkboxes
        for face in self.face_cb:
            face.hide()

        # Extracted faces from first frame are stored in preprocessing/faces/
        faces = os.listdir('preprocessing/faces/')
        faces.sort()
        self.face_cb = [QCheckBox(self.wid) for i in range(len(faces))]
        
        c=0
        for face, image_path in zip(self.face_cb, faces):
            face.setGeometry(QtCore.QRect(640, 50+c*40, 141, 31))
            face.setText("Person " + str(c))
            face.setIcon(QIcon('preprocessing/faces/' + image_path))
            face.show()
            #face.setIconSize(QtCore.QSize(30, 30))
            c+=1

        self.is_preprocessing_done = True



    def post_processing(self):
        pass



    def separate_audio(self):
        #Return a list of separated audio files which are saved locally in folder `preprocessing/audio/`
        #Name of each audio file corresponds to the number given to the checkbox.
        MODEL = load_model(MODEL_PATH, self.device)
        def _pad(arr, cur_len, exp_len):
            ref = np.zeros((exp_len, *arr.shape[1:]), dtype=np.float32)
            print(ref.shape, arr.shape)
            if len(arr) != 0:
                ref[:cur_len] = arr.copy()
            arr = ref.copy()
            return arr

        if(self.is_preprocessing_done == False):
            return

        if len(self.emb) == 2:
            frames = 75
            sr = 16_000
            audio_frames = 3*sr

            person_1, person_2 = tuple(self.emb.values())
            mixed_audio, _ = librosa.load("preprocessing/audio/original.wav", sr=sr)

            # stereo to mono
            if len(mixed_audio.shape) == 2 and mixed_audio.shape[1] == 2:
                mixed_audio = mixed_audio.sum(axis=1) / 2

            duration = len(mixed_audio) // sr
            n_slices = duration // 3
            remainder = duration % 3
            separated_audio = {"first": [], "second": []}
            print(n_slices, duration, sr, len(mixed_audio), len(person_1))

            for n in range(n_slices):
                emb_1, emb_2 = person_1[n*frames: (n+1)*frames], person_2[n*frames: (n+1)*frames]
                inp_audio = mixed_audio[n*audio_frames: (n+1)*audio_frames]

                emb_1, emb_2 = np.array(emb_1), np.array(emb_2)

                print(emb_1.shape, emb_2.shape, inp_audio.shape)
                output_audios = generate_audio(MODEL, inp_audio, [emb_1, emb_2],
                                               device=self.device, save=False)
                separated_audio["first"].append(output_audios[0])
                separated_audio["second"].append(output_audios[1])

            # remainder
            if 0:
                emb_1, emb_2 = person_1[n_slices*frames:], person_2[n_slices*frames:]
                print(n, frames, len(person_1), len(emb_1))
                inp_audio = mixed_audio[n_slices*audio_frames:]

                emb_len = len(emb_1)

                #pad
                emb_1 = _pad(np.squeeze(np.array(emb_1)), emb_len, frames)
                emb_2 = _pad(np.squeeze(np.array(emb_2)), emb_len, frames)

                inp_audio = _pad(inp_audio, len(inp_audio), sr*3)

                emb_1, emb_2, inp_audio = np.expand_dims(emb_1, axis=1), np.expand_dims(emb_2, axis=1), np.expand_dims(inp_audio, axis=1)
                print(emb_1.shape, emb_2.shape, inp_audio.shape)
                output_audios = generate_audio(MODEL, inp_audio, [emb_1, emb_2],
                                               device=self.device, save=False)
                separated_audio["first"].append(output_audios[0])
                separated_audio["second"].append(output_audios[1])
        else:
            pass
            # TODO: 1 v all
        
        separated_audio = {k: np.hstack(v) for k, v in separated_audio.items()}
        for i, (k, v) in enumerate(separated_audio.items()):
            librosa.output.write_wav(f"preprocessing/audio/{i+1}.wav", v, sr=16000)
        self.is_audio_separated = True
        return separated_audio



    def mix_audio_and_play(self):
        
        if(self.is_preprocessing_done == False):
            return
        if(self.is_audio_separated == False):
            return

        # Set video file (no audio must be present in it)
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.join(self.curr_dir, 'preprocessing/video/a.mp4'))))
        self.playButton.setEnabled(True)

        # Choose which audio files to mix from the status of checkboxes on main window
        audio_sequence = []
        c=0
        no=0
        for checkbox in self.face_cb:
            no = no*2
            if(checkbox.isChecked()):
                audio_sequence.append(c)
                no += 1
            c+=1

        if(len(audio_sequence) == 0):
            return

        url = None

        if(len(audio_sequence) < len(self.face_cb)):
            c = Audio_Processing()
            #c.mix_audio(self.curr_dir, audio_sequence) # Mixed audio is saved at `no.wav`
            url = QUrl.fromLocalFile(os.path.join(self.curr_dir, 'preprocessing/audio/' + str(no) + '.wav'))
        else:
            url = QUrl.fromLocalFile(os.path.join(self.curr_dir, 'preprocessing/audio/original.wav'))

        self.playlist = QMediaPlaylist()
        self.playlist.addMedia(QMediaContent(url))
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        
        self.audio_player = QMediaPlayer()
        self.audio_player.setPlaylist(self.playlist)





    def openFile(self):
        self.input_file_name, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())

        if self.input_file_name != '':
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.input_file_name)))
            self.playButton.setEnabled(True)


    def play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            if self.audio_player is not None:
                self.audio_player.pause()
        else:
            self.media_player.play()
            if self.audio_player is not None:
                self.audio_player.play()


    def exitCall(self):
        sys.exit(app.exec_())


    def mediaStateChanged(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


    def positionChanged(self, position):
        self.positionSlider.setValue(position)


    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)


    def setPosition(self, position):
        #self.media_player.setPosition(position)
        pass

    def handleError(self):
        self.playButton.setEnabled(False)
        print("Error: " + self.media_player.errorString())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    videoplayer = VideoPlayer()
    videoplayer.show()
    sys.exit(app.exec_())
