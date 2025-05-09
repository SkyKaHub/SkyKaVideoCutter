import threading
import os
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import toml
from slugify import slugify

from my_module import utils, config_manager

BASE_DIR = Path(__file__).resolve().parent.parent
config = toml.load(BASE_DIR / "config" / "config.toml")

def transcribe_video(label, log_box, tk):
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    video = config_manager.get_source_file_path()
    if not video:
        messagebox.showerror("Error", "Select video file")
        return

    label.config(text="Status: In progress", style="Blue.TLabel")

    video_path = Path(video)
    base_name = slugify(video_path.stem)
    current_output_dir = BASE_DIR / config["paths"]["output_dir_base"] / datetime.today().strftime('%d.%m.%Y') / base_name
    os.makedirs(current_output_dir, exist_ok=True)
    output_wav = current_output_dir / f"{base_name}.wav"
    output_srt = current_output_dir / f"{base_name}.srt"

    def worker():
        try:
            utils.make_wav_from_video(
                input_video_path=video,
                output_audio_path=output_wav,
                log_box=log_box,
                tk=tk
            )
            utils.make_srt_file_from_audio(
                input_file_path=output_wav,
                output_file_path=output_srt,
                log_box=log_box,
                tk=tk
            )
            os.remove(output_wav)
            status_text = "Status: Ready ✅" if output_srt.exists() else "Status: Not ready ❌"
            fg_color = "green" if output_srt.exists() else "red"
            label.after(0, lambda: label.config(text=status_text, foreground=fg_color))
        except Exception as e:
            label.after(0, lambda: label.config(text=f"Error: {e}", foreground="red"))

    threading.Thread(target=worker, daemon=True).start()
