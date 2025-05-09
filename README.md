# SkyCutter

SkyCutter is a desktop GUI application for automated preparation and publication of short-form video clips, optimized for TikTok. The application enables you to:

* Download and process source videos using custom timecodes (in dev)
* Automatically generate subtitles via Whisper (Hugging Face)
* Hardcode (embed) subtitles into the video (in dev)
* Support multiple languages (English and Russian)
* Schedule TikTok uploads according to a timetable (in dev)
* Manage multiple TikTok accounts (in dev)

## 🚀 Key Features

* **Video Download**: Fetch source videos using `yt-dlp`.
* **Audio Conversion**: Extract and convert video audio to `.wav` format.
* **Transcription**: Generate `.srt` subtitle files automatically.
* **Subtitle Embedding**: Burn subtitles directly onto the video track.
* **Clip Trimming**: Trim videos at user-defined start and end points.
* **Project Management**: Import and export clip configurations in JSON.
* **Publication Scheduling**: Automate video uploads to TikTok on a schedule.
* **Configurable Settings**: Modify behavior via `config/config.toml`.

## 📋 System Requirements

* **Python**: Version 3.10 or higher
* **FFmpeg**: Must be installed and available in your system `PATH`
* **Internet Connection**: Required for video downloads and API transcription requests

## 🔧 Python Dependencies

Install the required Python packages with:

```bash
pip install -r requirements.txt
```

## ⚙️ Installation and Usage

1. **Clone the repository**:

   ```bash
   ```

git clone [https://github.com/SkyKaHub/SkyKaVideoCutter.git](https://github.com/SkyKaHub/SkyKaVideoCutter.git)
cd SkyKaVideoCutter

````
2. **Install dependencies**:
   ```bash
pip install -r requirements.txt
````

3. **Verify FFmpeg installation**:

   ```bash
   ```

ffmpeg -version

````
4. **Configure the application**:
   - Edit `config/config.toml` to set:
     - Paths for input and output directories
     - API credentials for TikTok (if required)
     - Subtitle language and video quality preferences
5. **Run the application**:
   ```bash
python main.py
````

## 🗂 Project Structure

```
SkyKaVideoCutter/
├── config/
│   └── config.toml           # Application settings (paths, API keys, etc.)
├── gui/
│   └── app_ui.py             # Tkinter-based GUI components
├── my_module/
│   ├── utils.py              # Video/audio utilities and download logic
│   ├── subtitle_processing.py# Transcription and subtitle generation logic
│   └── config_manager.py     # Configuration manager
├── main.py                   # Application entry point
├── requirements.txt          # Python dependency list
└── .gitignore
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Open an issue to discuss your proposed changes.
2. Fork the repository and create a feature branch.
3. Commit your changes and submit a pull request.
4. Adhere to the existing coding style and include tests where applicable.

## 📄 License

This project currently does not include a license. Please add a `LICENSE` file with your preferred license terms.

## ✉️ Contact

Maintainer: [SkyKaHub](https://github.com/SkyKaHub)
