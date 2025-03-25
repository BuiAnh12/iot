import sys
import cv2
import sqlite3
import threading
import numpy as np
import mediapipe as mp
from keras.models import load_model
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import time


# Load trained model
model = load_model("./ml_pipeline/model.h5")

# Mediapipe Pose Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

class PoseStreamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pose Detection Stream")
        self.setGeometry(100, 100, 800, 600)
        self.init_db()
        self.init_ui()
        self.load_saved_urls()
        self.timer = QTimer(self)
        self.sequence = []
        self.no_of_timesteps = 100
        self.num_features = 132  # Ensure input shape matches model

    def init_db(self):
        self.conn = sqlite3.connect("streams.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS streams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE
            )
        """)
        self.conn.commit()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.url_input = QLineEdit(self)
        self.layout.addWidget(self.url_input)
        
        self.add_stream_btn = QPushButton("Add Stream", self)
        self.add_stream_btn.clicked.connect(self.add_stream)
        self.layout.addWidget(self.add_stream_btn)
        
        self.stream_list = QListWidget(self)
        self.layout.addWidget(self.stream_list)
        
        self.delete_stream_btn = QPushButton("Delete Selected Stream", self)
        self.delete_stream_btn.clicked.connect(self.delete_stream)
        self.layout.addWidget(self.delete_stream_btn)
        
        self.start_stream_btn = QPushButton("Watch Stream", self)
        self.start_stream_btn.clicked.connect(self.watch_stream)
        self.layout.addWidget(self.start_stream_btn)
        
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.layout.addWidget(self.video_label)
        
        self.result_label = QLabel("Status: Not Started", self)
        self.layout.addWidget(self.result_label)
        
        self.setLayout(self.layout)
    
    def load_saved_urls(self):
        self.stream_list.clear()
        self.cursor.execute("SELECT url FROM streams")
        for row in self.cursor.fetchall():
            self.stream_list.addItem(row[0])
    
    def add_stream(self):
        url = self.url_input.text().strip()
        if url:
            try:
                self.cursor.execute("INSERT INTO streams (url) VALUES (?)", (url,))
                self.conn.commit()
                self.load_saved_urls()
                self.url_input.clear()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "Stream URL already exists!")
    
    def delete_stream(self):
        selected_item = self.stream_list.currentItem()
        if selected_item:
            url = selected_item.text()
            self.cursor.execute("DELETE FROM streams WHERE url = ?", (url,))
            self.conn.commit()
            self.load_saved_urls()
    
    def watch_stream(self):
        selected_item = self.stream_list.currentItem()
        if selected_item:
            url = selected_item.text()
            print(f"Đang xem stream từ URL: {url}")  # Debug log
            threading.Thread(target=self.display_stream, args=(url,), daemon=True).start()
        else:
            print("Lỗi: Không có stream nào được chọn!")
    
    def display_stream(self, url):
        cap = cv2.VideoCapture(url)

        # Kiểm tra xem có mở được stream hay không
        if not cap.isOpened():
            print(f"Lỗi: Không mở được stream từ {url}")
            self.result_label.setText("Lỗi: Không mở được stream")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(frame_rgb)
                
                if results.pose_landmarks:
                    print("Pose detected successfully")
                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    landmarks = []
                    for lm in results.pose_landmarks.landmark:
                        landmarks.append(lm.x)
                        landmarks.append(lm.y)
                        landmarks.append(lm.z)
                        landmarks.append(lm.visibility)
                    
                    while len(landmarks) < self.num_features:
                        landmarks.append(0.0)
                    landmarks = np.array(landmarks[:self.num_features])
                    
                    self.sequence.append(landmarks)
                    if len(self.sequence) > self.no_of_timesteps:
                        self.sequence.pop(0)
                    
                    if len(self.sequence) == self.no_of_timesteps:
                        prediction = model.predict(np.expand_dims(self.sequence, axis=0))
                        label = np.argmax(prediction)
                        labels = ["Falling", "Sitting", "Standing"]
                        detected_label = labels[label]
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        print(f"[{timestamp}] Phát hiện: {detected_label}")
                        self.result_label.setText(f"Detected: {labels[label]}")
                else:
                    print("No pose detected")

                # Draw Grid
                h, w, _ = frame.shape
                step_size = 50
                for x in range(0, w, step_size):
                    cv2.line(frame, (x, 0), (x, h), (200, 200, 200), 1)
                for y in range(0, h, step_size):
                    cv2.line(frame, (0, y), (w, y), (200, 200, 200), 1)
                
                # Chuyển đổi frame sang dạng grayscale và hiển thị
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                qimg = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_Grayscale8)
                self.video_label.setPixmap(QPixmap.fromImage(qimg))
                
                # Kiểm tra xem frame có hiển thị thành công không
                if self.video_label.pixmap() is None:
                    print("Lỗi: Không hiển thị được hình ảnh trên QLabel")
                    
            else:
                print("Lỗi: Không đọc được frame từ stream")
                break
        cap.release()
        print("Stream đã kết thúc.")
    
    def closeEvent(self, event):
        self.conn.close()
        event.accept()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoseStreamApp()
    window.show()
    sys.exit(app.exec_())
