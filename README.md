# Fabel

A simple PyQt6 application for downloading videos and audio from YouTube, implemented in Python.

## Introduction

Fabel is a desktop application built using PyQt6 that allows users to download videos and audio from YouTube. It provides a user-friendly interface for searching YouTube videos, playlists, and channels, and downloading them directly to the user's device.

## Features

- Search and download videos from YouTube.
- Download multiple audio files and merge them into a single audio file.
- Download audio files from YouTube videos.
- Download entire playlists from YouTube.
- User-friendly interface with progress tracking.
- Option to specify download format and quality.
- Download multiple videos simultaneously.
- Cross-platform support (Windows, macOS, Linux).
- Open-source and free to use.
- No ads or hidden costs.
- Lightweight and easy to use.

## Installation

To install the YouTube Downloader application, follow these steps:

1. Clone the repository to your local machine:

``git clone https://github.com/ShariarShuvo1/fable.git``

2. Install the required dependencies:

``pip install -r requirements.txt``

3. Run the application:
    
``python main.py``

or

Download the latest release from the [releases](https://github.com/ShariarShuvo1/fable/releases) page and run the executable file.

## Usage

1. Launch the application by running `main.py`.
2. Use the search feature to find videos on YouTube.
3. Select the desired video from the search results.
4. Choose the download format and quality.
5. Click the download button to start the download process.
6. Monitor the progress of downloads in the application interface.

## Dependencies

The YouTube Downloader application relies on the following dependencies:

- PyQt6: Python bindings for the Qt application framework.
- yt-dlp: A fork of youtube-dl for downloading videos from YouTube.
- proglog: A progress bar logger library for tracking download progress.
- moviepy: A video editing library used for merging audio and video files.
- eyed3: A library for working with ID3 tags in audio files.

These dependencies are automatically installed when you run `pip install -r requirements.txt`.

## License

This project is licensed under the [MIT License](LICENSE).