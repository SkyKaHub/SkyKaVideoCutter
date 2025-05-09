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
    log_box.insert(tk.END, message + '\n')
    log_box.see(tk.END)
    log_box.config(state="disabled")

def select_file(file_type, file_label=None):
    files_path = ""
    match file_type:
        case "source":
            files_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
            config_manager.set_source_file_path(files_path)
            if file_label:
                file_label.configure(foreground="green", text=Path(files_path).name)
        case _:
            messagebox.showerror("Error", "Select type of file")
    return files_path

def open_folder(path):
    os.makedirs(path, exist_ok=True)
    os.startfile(path)

def download_video(url, log_box, tk, label=None):
    if not url:
        messagebox.showerror("Error", "No link!")
        return

    os.makedirs(BASE_DIR / config["paths"]["sources_dir"], exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': BASE_DIR / config["paths"]["sources_dir"] + '/%(title)s.%(ext)s',
        'noplaylist': True,
        'logger': YTDLPLogger(log_box, tk)
    }

    threading.Thread(
        target=download_and_mark,
        args=(url, ydl_opts, label),
        daemon=True
    ).start()

def download_and_mark(url, ydl_opts, label):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        if label:
            label.after(0, lambda: label.configure(foreground="green", text="Downloaded"))
    except Exception as e:

        if label:
            label.after(0, lambda: label.configure(foreground="red", text=f"Error: {e}"))

        label.after(0, lambda: messagebox.showerror("Ошибка", str(e)))

def make_wav_from_video(input_video_path, output_audio_path, log_box, tk):
    cmd = [
        "ffmpeg",
        "-i", input_video_path,  # входной файл
        "-ar", "16000",  # частота дискретизации 16 кГц
        "-ac", "1",  # моно
        "-b:a", "32k",  # битрейт 32 кбит/с
        output_audio_path  # выходной файл
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    for output_line in process.stdout:
        log_message(message=output_line.strip(), log_box=log_box, tk=tk)
    process.wait()
    return output_audio_path

def make_srt_file_from_audio(input_file_path, output_file_path, log_box, tk):
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio=input_file_path, language=config_manager.get_language(), beam_size=5,
                                      word_timestamps=False)
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