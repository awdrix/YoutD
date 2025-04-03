# YouTube Downloader

A simple YouTube video and audio downloader using `yt-dlp` and `Streamlit`.

## Features
- Download videos in MP4 format
- Download audio in MP3 format
- Embedded video preview before downloading

## Preview

![Application Screenshot](https://raw.githubusercontent.com/awdrix/YoutD/main/demo/demo.png)

### Requirements
- Python 3.8+
- `ffmpeg` installed and in system PATH

### Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Running the application
```bash
streamlit run youtd.py
```

## Platform-specific Instructions

### Linux
Ensure `ffmpeg` is installed:
```bash
sudo apt install ffmpeg
```

Run the app:
```bash
streamlit run youtd.py
```


