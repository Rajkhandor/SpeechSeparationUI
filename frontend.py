from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *

from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QStyle, QFileDialog
from PyQt5.QtGui import QIcon

from pydub import AudioSegment

import sys
import main


class VideoPlayer(main.Ui_window, QMainWindow):
    def __init__(self):
        super(VideoPlayer, self).__init__()
        self.setupUi(self)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.audio_file_path = []
        self.audio_player = None

        self.openAction.triggered.connect(self.openFile)
        self.exitAction.triggered.connect(self.exitCall)
        self.pre_pb.clicked.connect(lambda x: self.pre_processing())
        self.post_pb.clicked.connect(lambda x: self.post_processing())
        self.separate_audio_pb.clicked.connect(lambda x: self.separate_audio())
        self.play_chosen_pb.clicked.connect(self.mix_audio)

        self.media_player.setVideoOutput(self.videoWidget)
        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.media_player.error.connect(self.handleError)


    def pre_processing(self):
        pass

    def post_processing(self):
        pass

    def separate_audio(self):
        #Check if the video file is opened or not
        #Check if the pre-processing is done or not
        #Pass the pre-processed file for separation of audio
        #Return a list of separated audio files which are saved locally
        #Save the names of each audio file in list `audio_file_path`
        #For each returned audio file create a checkbox on the main window
        self.audio_file_path = ["/home/raj/a.mp3", "/home/raj/b.mp3"]
        pass


    def mix_audio(self):
        #Choose which audio files to mix from the status of checkboxes on main window
        audio_sequence = [0,1]

        # Doing it naively to simplify mixing of audios
        output = AudioSegment.from_mp3(self.audio_file_path[audio_sequence[0]])
        for audio in audio_sequence[1:]:
            s = AudioSegment.from_mp3(self.audio_file_path[audio])
            output = output.overlay(s)

        #Definitely there might be some way to avoid this
        output.export("/home/raj/mixed_sounds.mp3", format="mp3")
        
        url = QUrl.fromLocalFile("/home/raj/mixed_sounds.mp3")

        self.playlist = QMediaPlaylist()
        self.playlist.addMedia(QMediaContent(url))

        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

        self.audio_player = QMediaPlayer()
        self.audio_player.setPlaylist(self.playlist)


    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())

        if fileName != '':
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)


    def play(self):
        #Need to change the structure of this function
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
        self.media_player.setPosition(position)


    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.media_player.errorString())



if __name__ == '__main__':
    app = QApplication(sys.argv)
    videoplayer = VideoPlayer()
    videoplayer.show()
    sys.exit(app.exec_())
