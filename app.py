import sys
import cv2
import sqlite3
import datetime
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|timeout;5000000"

class StreamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stream Catcher")
        self.setGeometry(100, 100, 800, 600)
        self.init_db()
        self.init_ui()
        self.load_saved_urls()
        self.timer = QTimer(self)
        self.timer.start(1000)  # Check every second
        
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
        self.layout.addWidget(self.video_label)
        
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
            threading.Thread(target=self.display_stream, args=(url,), daemon=True).start()
    
    def display_stream(self, url):
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            print("Không thể mở stream:", url)

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                self.video_label.setPixmap(pixmap)
            else:
                break
        cap.release()
    
        
    def closeEvent(self, event):
        self.conn.close()
        event.accept()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StreamApp()
    window.show()
    sys.exit(app.exec_())
