# RTSP Streaming Proof of Concept (POC) on Windows

This guide demonstrates how to set up an **RTSP streaming server** on Windows using Docker, stream a video to it, and process the stream using an application.

## Prerequisites
- Install **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop)
- Ensure Docker is running properly by testing it with a simple container:
  ```sh
  docker run hello-world
  ```
- Configure **network settings**:
  1. Open **Docker Desktop** → **Settings** → **Resources** → **Network**
  2. Turn on the **subnet** and enable **host networking**

## Setup Steps
### 1. Start the RTSP Server
Open the first terminal and run:
```sh
  docker run -p 8554:8554 -p 1935:1935 bluenviron/mediamtx:latest
```
This starts an **RTSP server** (MediaMTX) that listens on port `8554`.

### 2. Start the RTSP Stream
Open the second terminal and run the `start_stream.py` script:
```sh
  python start_stream.py
```
This will:
- Take a local video file
- Stream it to the **RTSP server** as a simulated IoT camera feed

### 3. Run the Main Application
Open the third terminal and start the RTSP processing application:
```sh
  python app.py
```
This application will:
- Read the **RTSP stream** from the server
- Process the video feed in real-time
- Simulate IoT camera behavior for testing

## Notes
- The RTSP server allows real-time streaming simulation without needing an actual IoT camera.
- If you encounter network issues, try using `rtsp://host.docker.internal:8554/mystream` instead of `localhost` in your scripts.
- To verify that the RTSP stream is working, use VLC Media Player:
  - Open VLC → **Media** → **Open Network Stream**
  - Enter `rtsp://localhost:8554/mystream` and click **Play**.

## Next Steps
- Extend `app.py` to include stream processing features
- Integrate AI/ML models for real-time video analysis
- Deploy the setup on an actual IoT device

## License
This project is licensed under the MIT License.

