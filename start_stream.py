import subprocess
import time
import cv2
import os

def start_stream(video_path, stream_id, localhost_url):
    command = [
        "ffmpeg", "-re", "-stream_loop", "-1", "-i", video_path,
        "-c", "copy", "-f", "rtsp", "-rtsp_transport", "tcp", localhost_url
    ]
    
    try:
        subprocess.Popen(command)
        print(f"Streaming started: {localhost_url}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def check_stream(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    time.sleep(2)  # Allow some time for the stream to initialize
    if cap.isOpened():
        print(f"Stream {rtsp_url} is running.")
        cap.release()
    else:
        print(f"Failed to connect to stream {rtsp_url}.")


if __name__ == "__main__":
    video_file = "E:/PTITv2/iot/video/loitering_people.mp4"
    stream_id = "mystream"
    localhost_url = f"rtsp://localhost:8554/{stream_id}"
    
    start_stream(video_file, stream_id, localhost_url)
    time.sleep(5)  # Wait for stream to start
    check_stream(localhost_url)