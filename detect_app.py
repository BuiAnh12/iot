import numpy as np
import pandas as pd
import os
import cv2
import sys
import mediapipe as mp
from keras.models import load_model
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

# Load trained model
model = load_model("./model/model.h5")

# Mediapipe Pose Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

class PoseDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.detect_pose)
        self.sequence = []
        self.no_of_timesteps = 10
        self.num_features = 131  # Ensure input shape matches model

    def initUI(self):
        self.setWindowTitle("Pose Detector")
        self.setGeometry(100, 100, 800, 600)

        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)

        self.result_label = QLabel("Status: Not Started", self)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_detection)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_detection)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.result_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

    def start_detection(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)

    def stop_detection(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.video_label.clear()

    def detect_pose(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.append(lm.x)
                landmarks.append(lm.y)
                landmarks.append(lm.z)
                landmarks.append(lm.visibility)
            
            # Ensure we have exactly 131 features
            while len(landmarks) < self.num_features:
                landmarks.append(0.0)  # Pad with zeros if needed
            landmarks = np.array(landmarks[:self.num_features])  # Trim if too long
            
            self.sequence.append(landmarks)
            if len(self.sequence) > self.no_of_timesteps:
                self.sequence.pop(0)
            
            if len(self.sequence) == self.no_of_timesteps:
                prediction = model.predict(np.expand_dims(self.sequence, axis=0))
                label = np.argmax(prediction)
                labels = ["Falling", "Sitting", "Standing"]
                self.result_label.setText(f"Detected: {labels[label]}")
        
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_Grayscale8)
        self.video_label.setPixmap(QPixmap.fromImage(image))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoseDetectorApp()
    window.show()
    sys.exit(app.exec_())
