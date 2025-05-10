# SkyCutter

## Overview

SkyCutter is a desktop GUI application for automating the preparation and publication of short-form video content on TikTok. It enables you to download source videos, extract and convert audio, generate and embed subtitles using Whisper, trim clips according to custom timecodes, and schedule uploads across multiple TikTok accounts.

## Key Features

* **Video Download**
  Download source videos from YouTube and other platforms using `yt-dlp`.
* **Audio Extraction & Conversion**
  Extract audio tracks from videos and convert them to WAV format.
* **Automatic Transcription**
  Generate SRT subtitle files with Whisper (Hugging Face).
* **Subtitle Embedding**
  Burn subtitles directly into the video stream.
* **Clip Trimming**
  Trim videos based on user-defined start and end timecodes.
* **Configuration Import/Export**
  Save and load clip settings and timecodes in JSON format.
* **Publication Scheduling**
  Automate video uploads to TikTok on a configurable schedule.
* **Multilingual Interface**
  Support for English and Russian for both the interface and subtitle generation.
* **Multi-Account Management**
  Manage credentials and schedules for multiple TikTok accounts.

## Requirements

* **Python 3.10**
* **FFmpeg** installed and available in the system `PATH`
* **Internet Connection** for video downloads and transcription API calls

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/SkyKaHub/SkyKaVideoCutter.git
   cd SkyKaVideoCutter
   ```
2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
3. **Verify FFmpeg installation**

   ```bash
   ffmpeg -version
   ```

## Configuration

Edit the `config/config.toml` file to specify:

* **Input/Output Paths**: Directories for source videos and processed clips.
* **TikTok Credentials**: API keys or cookies for automated uploads.
* **Subtitle Settings**: Language code (`en` or `ru`), model selection, and formatting options.
* **Video Quality**: Resolution, frame rate, and encoding parameters.

## Usage

Run the application:

```bash
python main.py
```

1. **Add Source Videos**: Enter URLs or select local video files.
2. **Define Clips**: Specify start and end timecodes for each segment.
3. **Generate & Embed Subtitles**: Transcribe and hardcode subtitles into your clips.
4. **Export Configuration**: Save your clip list as a JSON file for future reuse.
5. **Schedule Uploads**: Assign each clip to a date/time and TikTok account.

## Project Structure

```
SkyKaVideoCutter/
├── config/
│   └── config.toml           # Application settings
├── gui/
│   └── app_ui.py             # Tkinter-based interface
├── my_module/
│   ├── utils.py              # Download, trimming, and conversion logic
│   ├── subtitle_processing.py# Transcription and SRT generation
│   └── config_manager.py     # TOML configuration loader
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── .gitignore
```

## Contributing

Contributions are welcome:

1. Open an issue to discuss your proposal.
2. Fork the repository and create a feature branch (`feature/...`).
3. Commit your changes with tests (if applicable) and submit a pull request.
4. Adhere to the existing code style and project guidelines.

## License

This project is currently unlicensed. Add a `LICENSE` file to define usage terms.

## Contact

For support or inquiries, please open an issue at:
[https://github.com/SkyKaHub/SkyKaVideoCutter/issues](https://github.com/SkyKaHub/SkyKaVideoCutter/issues)
