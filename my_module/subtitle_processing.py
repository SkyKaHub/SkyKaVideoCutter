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


def transcribe_video(labels, log_box, tk):
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    video = config_manager.get_source_file_path()
    if not video:
        messagebox.showerror("Error", "Select video file")
        return

    labels["subtitle_label"].config(text="Status: In progress", style="Blue.TLabel")

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
            labels["subtitle_label"].after(
                0,
                lambda: labels["subtitle_label"].config(
                    text=status_text, foreground=fg_color
                ),
            )
            labels["selected_subs_label"].config(
                text=Path(output_srt).name, style="Green.TLabel"
            )
            config_manager.set_subs_file_path(output_srt)
        except Exception as e:
            labels["subtitle_label"].after(
                0,
                lambda: labels["subtitle_label"].config(
                    text=f"Error: {e}", foreground="red"
                ),
            )

    threading.Thread(target=worker, daemon=True).start()


# def get_interests(label, timecodes_textbox, tk):
#     label.config(text="Processing", foreground="blue")
#     if config_manager.get_language() == "ru":
#         nlp = spacy.load("ru_core_news_sm")
#     else:
#         nlp = spacy.load("en_core_web_sm")
#     subs = pysrt.open(config_manager.get_subs_file_path(), encoding="utf-8")
#     blocks = []
#     block_text = ""
#     block_start = None
#
#     for sub in subs:
#         if not block_text:
#             block_start = sub.start.to_time()
#         block_text += sub.text + " "
#         if sub.text.endswith((".", "!", "?")):
#             block_end = sub.end.to_time()
#             blocks.append(
#                 {
#                     "text": block_text.strip(),
#                     "start": block_start,
#                     "end": block_end,
#                     "duration": timedelta(
#                         hours=block_end.hour,
#                         minutes=block_end.minute,
#                         seconds=block_end.second,
#                     )
#                     - timedelta(
#                         hours=block_start.hour,
#                         minutes=block_start.minute,
#                         seconds=block_start.second,
#                     ),
#                 }
#             )
#             block_text = ""
#     interesting_blocks = []
#
#     for block in blocks:
#         doc = nlp(block["text"])
#         sents = list(doc.sents)
#
#         # Rule 1: fragment must be 1 to 50 sentences long
#         if not (1 <= len(sents) <= 100):
#             continue
#
#         # Rule 2: must contain at least one content word (NOUN, VERB, PROPN)
#         has_content_word = any(tok.pos_ in {"NOUN", "VERB", "PROPN"} for tok in doc)
#         if not has_content_word:
#             continue
#
#         # Rule 3: at least one sentence ends with “?” or “!”
#         ends_with_emotion = any(
#             sent.text.strip().endswith(("?", "!")) for sent in sents
#         )
#         if not ends_with_emotion:
#             continue
#
#         interesting_blocks.append(block)
#
#     interesting_timecodes = []
#     for index, interesting_block in enumerate(interesting_blocks, 1):
#         interesting_timecodes.append(
#             f"{interesting_block['start'].strftime('%H:%M:%S')}.000 - {interesting_block['end'].strftime('%H:%M:%S')}.000"
#         )
#
#     config_manager.set_timecodes(interesting_timecodes)
#
#     if not interesting_timecodes:
#         label.config(text="No timecodes", foreground="red")
#     else:
#         label.config(text="Done", foreground="green")
#         timecodes_textbox.delete("1.0", tk.END)
#         timecodes_textbox.insert("1.0", "\n".join(interesting_timecodes))


import spacy
import numpy as np
import pysrt
from datetime import timedelta
from tkinter import messagebox

def get_interests(label, timecodes_textbox, tk, threshold: float = 0.5):
    """
    Load subtitles, split into blocks on sentence boundaries,
    then cluster by semantic similarity to keep one topic per segment.
    """
    label.config(text="Processing…", foreground="blue")

    # load appropriate spaCy model with vectors
    if config_manager.get_language() == "ru":
        nlp = spacy.load("ru_core_news_sm")
    else:
        nlp = spacy.load("en_core_web_sm")

    # read .srt and build text blocks
    subs = pysrt.open(config_manager.get_subs_file_path(), encoding="utf-8")
    blocks = []
    buf_text = ""
    buf_start = None
    for sub in subs:
        if not buf_text:
            buf_start = sub.start.to_time()
        buf_text += sub.text + " "
        if sub.text.rstrip().endswith((".", "!", "?")):
            buf_end = sub.end.to_time()
            blocks.append({
                "text": buf_text.strip(),
                "start": buf_start,
                "end": buf_end,
            })
            buf_text = ""

    if not blocks:
        label.config(text="No subtitles found", foreground="red")
        return

    # segment into topic‐coherent clusters
    segments = []
    current = []
    prev_vec = None
    min_duration = timedelta(minutes=1)

    for blk in blocks:
        vec = nlp(blk["text"]).vector
        if prev_vec is None:
            current = [blk]
        else:
            # cosine similarity
            sim = np.dot(prev_vec, vec) / (
                    np.linalg.norm(prev_vec) * np.linalg.norm(vec) + 1e-8
            )

            start = current[0]["start"]
            end = blk["end"]
            dur = (
                    timedelta(hours=end.hour, minutes=end.minute, seconds=end.second)
                    - timedelta(hours=start.hour, minutes=start.minute, seconds=start.second)
            )

            if sim < threshold and dur >= min_duration:
                segments.append(current)
                current = [blk]
            else:
                current.append(blk)
        prev_vec = vec

    # append last
    if current:
        segments.append(current)

    # build timecodes: from first start to last end in each segment
    interesting_timecodes = []
    for seg in segments:
        start = seg[0]["start"].strftime("%H:%M:%S") + ".000"
        end   = seg[-1]["end"].strftime("%H:%M:%S") + ".000"
        interesting_timecodes.append(f"{start} - {end}")

    # save & display
    config_manager.set_timecodes(interesting_timecodes)

    if not interesting_timecodes:
        label.config(text="No timecodes", foreground="red")
    else:
        label.config(text="Done", foreground="green")
        timecodes_textbox.delete("1.0", tk.END)
        timecodes_textbox.insert("1.0", "\n".join(interesting_timecodes))
