import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer
from keras.models import load_model


class PoseCaptureApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pose Detection")
        self.setGeometry(100, 100, 800, 600)
        self.model = load_model('./model.h5')
        
        # UI Components
        self.video_label = QLabel(self)
        self.result_label = QLabel(self)  # Label for the result text
        
        # Set large font for result label
        self.result_label.setFont(QFont("Arial", 40, QFont.Bold))
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.result_label)  # Add result label under the video
        self.setLayout(layout)
        
        # Video capture setup
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # Pose detection setup
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils

        self.lm_list = []
        self.capture_active = False

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)

            if results.pose_landmarks:
                self.mp_draw.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                self.lm_list.append(self.extract_landmarks(results))
                
                if len(self.lm_list) == 10:  # Fixed the condition check here
                    self.start_detect()
                    
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            image = QImage(gray_frame, gray_frame.shape[1], gray_frame.shape[0], QImage.Format_Grayscale8)
            self.video_label.setPixmap(QPixmap.fromImage(image))

    def extract_landmarks(self, results):
        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z, lm.visibility])
        return landmarks

    def start_detect(self):
        df_data = np.array(self.lm_list[:100])  # Only keep the last 10 frames
        df_data = np.expand_dims(df_data, axis=0)
        self.lm_list = []  # Clear the list after processing
        prediction = self.model.predict(df_data)
        label = np.argmax(prediction)
        labels = ["Falling", "Sitting", "Standing"]
        
        # Update the result label with a large font
        self.result_label.setText(labels[label])
        self.result_label.setAlignment(Qt.AlignCenter)  # Center-align the text
        print(labels[label])

    def closeEvent(self, event):
        self.cap.release()  # Properly release video capture
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoseCaptureApp()
    window.show()
    sys.exit(app.exec_())
