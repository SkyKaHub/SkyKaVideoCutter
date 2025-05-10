import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import toml

import my_module.utils as utils
from my_module import subtitle_processing, video_processing
from my_module.config_manager import set_language

BASE_DIR = Path(__file__).resolve().parent.parent
config = toml.load(BASE_DIR / "config" / "config.toml")
BASE_OUTPUT_DIR = (BASE_DIR / config["paths"]["output_dir_base"]).as_posix()
SOURCES_DIR = (BASE_DIR / config["paths"]["sources_dir"]).as_posix()


def create_app():
    app = tk.Tk()
    app.title("SkyCutter")
    app.geometry("1200x700")

    style = ttk.Style()
    style.configure("Blue.TLabel", foreground="blue")
    style.configure("Green.TLabel", foreground="green")

    # === Main layout with two columns ===
    main_frame = ttk.Frame(app)
    main_frame.pack(fill="both", expand=True)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # === Left: scrollable ===
    left_canvas = tk.Canvas(main_frame)
    left_scrollbar = ttk.Scrollbar(
        main_frame, orient="vertical", command=left_canvas.yview
    )
    left_scrollable_frame = ttk.Frame(left_canvas)

    left_scrollable_frame.bind(
        "<Configure>",
        lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")),
    )

    left_canvas.create_window((0, 0), window=left_scrollable_frame, anchor="nw")
    left_canvas.configure(yscrollcommand=left_scrollbar.set)

    left_canvas.grid(row=0, column=0, sticky="nsew")
    left_scrollbar.grid(row=0, column=0, sticky="nse")

    # === Right: static (logs) ===
    right_frame = ttk.Frame(main_frame)
    right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    right_frame.columnconfigure(0, weight=1)
    right_frame.rowconfigure(1, weight=1)

    log_frame = ttk.LabelFrame(right_frame, text="Logs")
    log_frame.grid(row=0, column=0, sticky="nsew")
    log_box = tk.Text(log_frame, height=40, wrap="word", state="disabled")
    log_box.pack(fill="both", expand=True)

    # === Section: Video Input ===
    video_frame = ttk.LabelFrame(left_scrollable_frame, text="1. Video Input")
    video_frame.pack(fill="x", padx=10, pady=10)

    language = tk.StringVar(value=config["default"]["language"])
    language.trace_add("write", lambda *_: set_language(language.get()))
    ttk.Label(video_frame, text="Select video language:").grid(
        row=1, column=0, columnspan=2, sticky="w", pady=5
    )
    tk.Radiobutton(video_frame, text="English", variable=language, value="en").grid(
        row=2, column=1, sticky="w"
    )
    tk.Radiobutton(video_frame, text="Russian", variable=language, value="ru").grid(
        row=2, column=0, sticky="w"
    )

    ttk.Button(
        video_frame,
        text="Choose video for subtitles",
        command=lambda: utils.select_file(
            file_type="source", file_label=selected_file_label
        ),
    ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
    selected_file_label = ttk.Label(
        video_frame, text="No file selected", foreground="red"
    )
    selected_file_label.grid(row=4, column=0, columnspan=2, sticky="w")

    ttk.Label(video_frame, text="Or paste a YouTube link:").grid(
        row=5, column=0, columnspan=2, sticky="w", pady=5
    )
    url_entry = ttk.Entry(video_frame, width=50)
    url_entry.grid(row=6, column=0, columnspan=2, sticky="ew")

    url_button_frame = ttk.Frame(video_frame)
    url_button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(5, 10))
    ttk.Button(
        url_button_frame,
        text="Download",
        command=lambda: utils.download_video(
            url=url_entry.get().strip(),
            log_box=log_box,
            tk=tk,
            labels={
                "downloaded_file_label": downloaded_file_label,
                "selected_file_label": selected_file_label,
            },
        ),
    ).pack(side="left", padx=(0, 5))
    ttk.Button(
        url_button_frame,
        text="Open source folder",
        command=lambda: utils.open_folder(SOURCES_DIR),
    ).pack(side="left", padx=(0, 5))
    downloaded_file_label = ttk.Label(
        url_button_frame, text="Not downloaded", foreground="red"
    )
    downloaded_file_label.pack(side="left", padx=(0, 5))

    # === Section: Subtitles ===
    subs_frame = ttk.LabelFrame(left_scrollable_frame, text="2. Subtitles")
    subs_frame.pack(fill="x", padx=10, pady=10)

    ttk.Button(
        subs_frame,
        text="Generate Subtitles",
        command=lambda: subtitle_processing.transcribe_video(
            labels={
                "subtitle_label": subtitle_label,
                "selected_subs_label": selected_subs_label,
            },
            log_box=log_box,
            tk=tk,
        ),
    ).grid(row=0, column=0, sticky="w", pady=5)
    subtitle_label = ttk.Label(subs_frame, text="Status: Not started")
    subtitle_label.grid(row=0, column=1, sticky="w")

    # ttk.Button(subs_frame, text="Generate full video with subtitles").grid(row=1, column=0, sticky="w")
    # ttk.Button(subs_frame, text="Open subtitles folder").grid(row=1, column=1, sticky="w")

    # === Section: Detect interesting moments ===
    interesting_frame = ttk.LabelFrame(
        left_scrollable_frame, text="3. Interesting moments"
    )
    interesting_frame.pack(fill="x", padx=10, pady=10)

    ttk.Button(
        interesting_frame,
        text="Choose subs file",
        command=lambda: utils.select_file(
            file_type="subs", file_label=selected_subs_label
        ),
    ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

    selected_subs_label = ttk.Label(
        interesting_frame, text="No file selected", foreground="red"
    )
    selected_subs_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=5)

    interests_status_label = ttk.Label(
        interesting_frame, text="Not started", foreground="red"
    )
    interests_status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

    ttk.Button(
        interesting_frame,
        text="Detect moments",
        command=lambda: threading.Thread(
            target=subtitle_processing.get_interests,
            args=(interests_status_label, timecodes_textbox, tk),  # её аргументы
            daemon=True,
        ).start(),
    ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

    # === Section: Clip Cutting ===
    cut_frame = ttk.LabelFrame(left_scrollable_frame, text="3. Clip Cutting")
    cut_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(cut_frame, text="Timecodes (format: 00:00:00.000 - 00:00:10.000):").grid(
        row=0, column=0, sticky="w"
    )
    timecodes_textbox = tk.Text(cut_frame, height=5, width=40)
    timecodes_textbox.grid(row=1, column=0, columnspan=2, sticky="ew")
    clip_cutting_label = ttk.Label(cut_frame, text="Not started")
    clip_cutting_label.grid(row=2, column=1, sticky="w", pady=5)
    ttk.Button(
        cut_frame,
        text="Cut Clips",
        command=lambda: threading.Thread(
            target=video_processing.cut_video,
            args=(
                {
                    "clip_cutting_label": clip_cutting_label,
                    "clips_json": clips_json_label,
                    "embedding_clips_label": embedding_clips_label,
                    "embedding_clips_statuses_label": embedding_clips_statuses_label,
                },
                log_box,
                tk,
            ),
            daemon=True,
        ).start(),
    ).grid(row=2, column=0, sticky="w", pady=5)

    # === Section: Subtitle Embedding ===
    convert_frame = ttk.LabelFrame(left_scrollable_frame, text="4. Subtitle Embedding")
    convert_frame.pack(fill="x", padx=10, pady=10)
    ttk.Button(
        convert_frame,
        text="Select JSON file",
        command=lambda: utils.select_file(
            file_type="clips_json",
            file_label=clips_json_label,
            additional_labels={
                "embedding_clips_label": embedding_clips_label,
                "embedding_clips_statuses_label": embedding_clips_statuses_label,
            },
        ),
    ).grid(row=0, column=0, sticky="w", pady=5)
    clips_json_label = ttk.Label(
        convert_frame, text="No JSON selected", style="Red.TLabel"
    )
    clips_json_label.grid(row=0, column=1, sticky="w", pady=5)

    embedding_clips_label = ttk.Label(
        convert_frame, text="No clips", style="Red.TLabel"
    )
    embedding_clips_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
    embedding_clips_statuses_label = ttk.Label(
        convert_frame, text="Not started", style="Red.TLabel"
    )
    embedding_clips_statuses_label.grid(
        row=1, column=2, columnspan=2, sticky="w", pady=5
    )
    ttk.Button(
        convert_frame,
        text="Embed Subtitles",
        command=lambda: threading.Thread(
            target=video_processing.hardcode_subs,
            args=(
                {
                    "embedding_clips_label": embedding_clips_label,
                    "embedding_clips_statuses_label": embedding_clips_statuses_label,
                },
                log_box,
                tk,
            ),
            daemon=True,
        ).start(),
    ).grid(row=2, column=0, sticky="w", pady=5)

    # === Section: TikTok Upload ===
    #
    # account = tk.StringVar(value=config["default"]["account"])
    # account.trace_add("write", lambda *_: set_account(account.get()))
    # ttk.Label(video_frame, text="Select account:").grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
    #
    # for idx, account_name in enumerate(config['accounts']):
    #     print(idx)
    #     acc_data = config['accounts'][account_name]
    #     tk.Radiobutton(
    #         video_frame,
    #         text=acc_data['accountname'],
    #         variable=account,
    #         value=account_name
    #     ).grid(row=1, column=idx, sticky="w")
    # upload_frame = ttk.LabelFrame(left_scrollable_frame, text="5. TikTok Upload")
    # upload_frame.pack(fill="x", padx=10, pady=10)

    # ttk.Button(upload_frame, text="Upload to TikTok").grid(row=0, column=0, sticky="w", pady=5)

    return app


if __name__ == "__main__":
    create_app()
