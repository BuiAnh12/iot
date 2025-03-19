import subprocess
import time
import cv2
import os

FFMPEG_PATH = r"D:/ffmpeg/bin/ffmpeg.exe"

def start_stream(video_path, stream_id, localhost_url):
    command = [
    FFMPEG_PATH, "-re", "-stream_loop", "-1", "-i", video_path,
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
    "-b:v", "500k", "-maxrate", "500k", "-bufsize", "1000k",
    "-c:a", "aac", "-f", "rtsp", "-rtsp_transport", "tcp", localhost_url
]
    
    try:
        subprocess.Popen(command, shell=True)
        print(f"Streaming started: {localhost_url}")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy FFmpeg. Kiểm tra đường dẫn.")
    except Exception as e:
        print(f"Lỗi khác: {e}")

def check_stream(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    time.sleep(2)  # Allow some time for the stream to initialize
    if cap.isOpened():
        print(f"Stream {rtsp_url} is running.")
        cap.release()
    else:
        print(f"Failed to connect to stream {rtsp_url}.")


if __name__ == "__main__":
    video_file = "D:/Workspace Embedded/iot/video/1010(1)-1.mp4"
    stream_id = "mystream"
    localhost_url = f"rtsp://localhost:8554/{stream_id}"
    
    start_stream(video_file, stream_id, localhost_url)
    time.sleep(5)  # Wait for stream to start
    check_stream(localhost_url)