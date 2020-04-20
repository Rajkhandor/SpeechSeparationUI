from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *

from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QStyle, QFileDialog, QCheckBox
from PyQt5.QtGui import QIcon

import os
import sys
import shutil
import json
import main
from PyQt5.QtGui import QPainter, QBrush, QPen

from PyQt5 import QtCore, QtGui, QtWidgets

from utility import Video_Processing, Audio_Processing

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


        c = Video_Processing()
        c.preprocessing(self.input_file_name)

        c = Audio_Processing()
        c.preprocessing(self.input_file_name)


        # Hide all the previous shown face checkboxes
        for face in self.face_cb:
            face.hide()

        # Extracted faces from first frame are stored in preprocessing/faces/
        faces = os.listdir('preprocessing/faces/')
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

        if(self.is_preprocessing_done == False):
            return

        # TODO: Call to the model

        self.is_audio_separated = True



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
        for checkbox in self.face_cb:
            if(checkbox.isChecked()):
                audio_sequence.append(c)
            c+=1

        if(len(audio_sequence) == 0):
            return

        c = Audio_Processing()
        c.mix_audio(self.curr_dir, audio_sequence) # Mixed audio is saved at `mixed.mp3`

        url = QUrl.fromLocalFile(os.path.join(self.curr_dir, 'preprocessing/audio/mixed.mp3'))

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
