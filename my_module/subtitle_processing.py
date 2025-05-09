import threading
import os
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import messagebox

import pysrt
import spacy

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
    current_output_dir = (
        BASE_DIR
        / config["paths"]["output_dir_base"]
        / datetime.today().strftime("%d.%m.%Y")
        / base_name
    )
    os.makedirs(current_output_dir, exist_ok=True)
    output_wav = current_output_dir / f"{base_name}.wav"
    output_srt = current_output_dir / f"{base_name}.srt"

    def worker():
        try:
            utils.make_wav_from_video(
                input_video_path=video,
                output_audio_path=output_wav,
                log_box=log_box,
                tk=tk,
            )
            utils.make_srt_file_from_audio(
                input_file_path=output_wav,
                output_file_path=output_srt,
                log_box=log_box,
                tk=tk,
            )
            os.remove(output_wav)
            status_text = (
                "Status: Ready ✅" if output_srt.exists() else "Status: Not ready ❌"
            )
            fg_color = "green" if output_srt.exists() else "red"
            label.after(0, lambda: label.config(text=status_text, foreground=fg_color))
        except Exception as e:
            label.after(0, lambda: label.config(text=f"Error: {e}", foreground="red"))

    threading.Thread(target=worker, daemon=True).start()


def get_interests():
    nlp = spacy.load("ru_core_news_sm")
    subs = pysrt.open(config_manager.get_subs_file_path(), encoding="utf-8")
    blocks = []
    block_text = ""
    block_start = None

    for sub in subs:
        if not block_text:
            block_start = sub.start.to_time()
        block_text += sub.text + " "
        if sub.text.endswith((".", "!", "?")):
            block_end = sub.end.to_time()
            blocks.append(
                {
                    "text": block_text.strip(),
                    "start": block_start,
                    "end": block_end,
                    "duration": timedelta(
                        hours=block_end.hour,
                        minutes=block_end.minute,
                        seconds=block_end.second,
                    )
                    - timedelta(
                        hours=block_start.hour,
                        minutes=block_start.minute,
                        seconds=block_start.second,
                    ),
                }
            )
            block_text = ""
    # Обработка текста и фильтрация
    interesting_blocks = []
    for block in blocks:
        doc = nlp(block["text"])
        # Примитивный критерий: больше 1 предложения и ключевые слова
        if len(list(doc.sents)) > 1 and any(
            token.pos_ in {"NOUN", "VERB", "PROPN"} for token in doc
        ):
            interesting_blocks.append(block)

    # Вывод результатов
    for i, b in enumerate(interesting_blocks, 1):
        print(f"[{i}] {b['start']} – {b['end']} | {b['duration']}")
        print(b["text"])
        print("—" * 50)
