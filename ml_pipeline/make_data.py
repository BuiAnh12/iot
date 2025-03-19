import sys
import cv2
import mediapipe as mp
import pandas as pd
import os
import time
import threading
import winsound
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QListWidget, QMessageBox, QComboBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

class PoseCaptureApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pose Capture")
        self.setGeometry(100, 100, 800, 600)

        # UI Components
        self.video_label = QLabel(self)
        self.start_button = QPushButton("Start Capture", self)
        self.tag_selector = QComboBox(self)
        self.tag_selector.addItems(["falling", "sitting", "standing"])
        self.file_list = QListWidget(self)
        self.delete_button = QPushButton("Delete Selected", self)
        self.merge_button = QPushButton("Merge by Label", self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.tag_selector)
        layout.addWidget(self.start_button)
        layout.addWidget(self.file_list)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.merge_button)
        self.setLayout(layout)

        # Connect buttons
        self.start_button.clicked.connect(self.start_capture)
        self.delete_button.clicked.connect(self.delete_file)
        self.merge_button.clicked.connect(self.merge_files)

        # Video capture setup
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # Pose detection setup
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils


        # Init params
        self.max_frame_file = 100
        self.frame_count = 1
        self.lm_list = []
        self.capture_active = False
        self.start_time = 0
        self.video_writer = None

        self.load_file_list()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)

            if results.pose_landmarks:
                self.mp_draw.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                if self.capture_active and time.time() - self.start_time < 10 and self.frame_count <= self.max_frame_file:
                    self.lm_list.append(self.extract_landmarks(results))
                    self.frame_count += 1
                    if self.video_writer:
                        self.video_writer.write(frame)
                elif self.capture_active:
                    self.save_data()
                    self.capture_active = False

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            image = QImage(gray_frame, gray_frame.shape[1], gray_frame.shape[0], QImage.Format_Grayscale8)
            self.video_label.setPixmap(QPixmap.fromImage(image))

    def extract_landmarks(self, results):
        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z, lm.visibility])
        return landmarks

    def start_capture(self):
        threading.Thread(target=self.start_capture_sequence).start()

    def start_capture_sequence(self):
        self.lm_list = []
        self.capture_active = False
        self.play_sound()
        time.sleep(5)  # Wait 5 seconds before starting capture
        self.play_sound()
        self.capture_active = True
        self.start_time = time.time()
        # self.start_video_recording()
        self.play_sound()

    def play_sound(self):
        winsound.Beep(1000, 500)  # Beep sound to indicate start/stop

    def start_video_recording(self):
        tag = self.tag_selector.currentText()
        count = sum(1 for file in os.listdir("data") if file.startswith(f"video_{tag}_"))
        filename = f"data/video_{tag}_{count + 1}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

    def save_data(self):
        tag = self.tag_selector.currentText()
        count = sum(1 for file in os.listdir("data") if file.startswith(f"data_{tag}_"))
        filename = f"data/data_{tag}_{count + 1}.csv"
        df = pd.DataFrame(self.lm_list)
        df.to_csv(filename, index=False)
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        self.load_file_list()
        self.play_sound()
        QMessageBox.information(self, "Capture Complete", f"Data and video saved as {filename}")

    def load_file_list(self):
        self.file_list.clear()
        for file in os.listdir("data"):
            if file.endswith(".csv") or file.endswith(".avi"):
                self.file_list.addItem(file)

    def delete_file(self):
        selected_item = self.file_list.currentItem()
        if selected_item:
            os.remove(os.path.join("data", selected_item.text()))
            self.load_file_list()

    def merge_files(self):
        tag = self.tag_selector.currentText()
        merged_data = []
        for file in os.listdir("data"):
            if file.startswith(f"data_{tag}_") and file.endswith(".csv"):
                df = pd.read_csv(os.path.join("data", file))
                merged_data.append(df)
        if merged_data:
            final_df = pd.concat(merged_data, ignore_index=True)
            final_df.to_csv(f"data/data_{tag}_merged.csv", index=False)
            QMessageBox.information(self, "Merge Complete", f"Merged data saved as data/{tag}_merged.csv")

    def closeEvent(self, event):
        self.cap.release()
        if self.video_writer:
            self.video_writer.release()
        event.accept()

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    app = QApplication(sys.argv)
    window = PoseCaptureApp()
    window.show()
    sys.exit(app.exec_())