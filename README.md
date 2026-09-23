# Universal Video & Audio Downloader Pro

A Python desktop application that provides a unified GUI workflow for media downloads through yt-dlp across multiple supported platforms.

## Features

- Multi-platform URL handling through yt-dlp
- Video and audio-only workflows
- Quality and audio-format selection
- Playlist and live-stream handling where supported by the source
- Platform detection
- Download progress reporting
- Background download execution
- Custom download location
- Persistent local configuration
- FFmpeg integration for media conversion and stream merging

## Architecture

~~~text
User interface
      │
      ▼
PlatformDetector
      │
      ▼
DownloadManager
      │
      ▼
yt-dlp + FFmpeg
      │
      ▼
Local output files
~~~

## Technology

- Python
- Tkinter
- yt-dlp
- FFmpeg
- psutil
- Optional tkinterdnd2

## Getting started

Install Python dependencies:

~~~bash
pip install -r requirements.txt
~~~

Install FFmpeg and make sure it is available on PATH.

Run the application:

~~~bash
python video_downloader.py
~~~

## Code organization

The main module separates responsibilities into concepts such as:

- Platform detection
- Download orchestration
- Progress callbacks
- GUI state and configuration
- Error and process handling

## Responsible use

Platform support can change with upstream services and yt-dlp releases. Users are responsible for respecting each platform's terms of service, access controls, and applicable copyright rules.

## Portfolio context

This is the main media-downloader project in the portfolio. It demonstrates desktop Python development, external process integration, network-facing workflows, and stateful GUI design. Other downloader repositories are intentionally treated as supporting/legacy experiments rather than separate flagship projects.
