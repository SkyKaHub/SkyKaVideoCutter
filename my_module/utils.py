import json
import os
import subprocess
import threading
from datetime import timedelta

import toml
from pathlib import Path
from tkinter import filedialog, messagebox
import yt_dlp
from faster_whisper import WhisperModel
import srt
from humanfriendly.terminal import output

from my_module import config_manager

BASE_DIR = Path(__file__).resolve().parent.parent
config = toml.load(BASE_DIR / "config" / "config.toml")


class YTDLPLogger:
    def __init__(self, log_box, tk):
        self.log_box = log_box
        self.tk = tk

    def debug(self, msg):
        log_message(str(msg), self.log_box, self.tk)

    def info(self, msg):
        log_message(str(msg), self.log_box, self.tk)

    def warning(self, msg):
        log_message("WARNING: " + str(msg), self.log_box, self.tk)

    def error(self, msg):
        log_message("ERROR: " + str(msg), self.log_box, self.tk)


def log_message(message, log_box, tk):
    log_box.config(state="normal")
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)
    log_box.config(state="disabled")


def select_file(file_type, file_label=None, additional_labels=None):
    files_path = []
    if not file_type:
        messagebox.showerror("Error", "Select type of file")
        return files_path
    if file_type == "source":
        source_dir = BASE_DIR / config["paths"]["sources_dir"]
        os.makedirs(source_dir, exist_ok=True)
        files_path = filedialog.askopenfilenames(filetypes=[("All Files", "*.*")], initialdir=source_dir)
        config_manager.set_source_file_path(files_path[0])
        if file_label:
            file_label.configure(foreground="green", text=Path(files_path[0]).name)
    if file_type == "subs":
        output_dir = BASE_DIR / config["paths"]["output_dir_base"]
        os.makedirs(output_dir, exist_ok=True)
        files_path = filedialog.askopenfilenames(filetypes=[("SRT Files", "*.srt")], initialdir=output_dir)
        config_manager.set_subs_file_path(files_path[0])
        if file_label:
            file_label.configure(foreground="green", text=Path(files_path[0]).name)
    if file_type == "clips_json":
        files_path = filedialog.askopenfilenames(filetypes=[("JSON Files", "*.json")])
        config_manager.set_clips_json_path(files_path[0])
        with open(files_path[0], "r", encoding="utf-8") as f:
            clip_times = json.load(f)
            f.close()

        clips = []
        clips_statuses = []
        for clip_info in clip_times:
            clips.append(clip_info["filename"])
            clips_statuses.append("Not started")
        additional_labels["embedding_clips_label"].config(
            text="\n".join([Path(v).name for v in clips])
        )
        additional_labels["embedding_clips_statuses_label"].config(
            text="\n".join([v for v in clips_statuses])
        )
        if file_label:
            file_label.configure(foreground="green", text=Path(files_path[0]).name)

    return files_path


def open_folder(path):
    os.makedirs(path, exist_ok=True)
    os.startfile(path)


def download_video(url, log_box, tk, labels=None):
    if not url:
        messagebox.showerror("Error", "No link!")
        return

    os.makedirs(BASE_DIR / config["paths"]["sources_dir"], exist_ok=True)

    ydl_opts = {
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "outtmpl": Path(BASE_DIR / config["paths"]["sources_dir"]).as_posix()
        + "/%(title)s.%(ext)s",
        "noplaylist": True,
        "logger": YTDLPLogger(log_box, tk),
    }

    threading.Thread(
        target=download_and_mark, args=(url, ydl_opts, labels), daemon=True
    ).start()


def download_and_mark(url, ydl_opts, labels):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        output_path = info.get("filepath")
        if not output_path:
            rd = info.get("requested_downloads") or []
            if rd:
                output_path = rd[0].get("filepath")
        output_path = Path(output_path)
        config_manager.set_source_file_path(output_path.as_posix())
        labels["downloaded_file_label"].config(text="Ready", style="Green.TLabel")
        labels["selected_file_label"].config(
            text=output_path.name, style="Green.TLabel"
        )
    except Exception as e:
        err_text = str(e)
        messagebox.showerror("Ошибка", str(err_text))


def make_wav_from_video(input_video_path, output_audio_path, log_box, tk):
    cmd = [
        "ffmpeg",
        "-i",
        input_video_path,
        "-ar",
        "16000",
        "-ac",
        "1",
        "-b:a",
        "32k",
        output_audio_path,
    ]

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8"
    )
    for output_line in process.stdout:
        log_message(message=output_line.strip(), log_box=log_box, tk=tk)
    process.wait()
    return output_audio_path


def make_srt_file_from_audio(input_file_path, output_file_path, log_box, tk):
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        audio=input_file_path,
        language=config_manager.get_language(),
        beam_size=5,
        word_timestamps=False,
    )
    subtitles = []
    for i, segment in enumerate(segments):
        start = timedelta(seconds=segment.start)
        end = timedelta(seconds=segment.end)
        content = segment.text.strip()

        log_message(message=f"[{start} -> {end}] {content}", log_box=log_box, tk=tk)

        subtitle = srt.Subtitle(index=i + 1, start=start, end=end, content=content)
        subtitles.append(subtitle)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))
        f.close()

    return output_file_path
