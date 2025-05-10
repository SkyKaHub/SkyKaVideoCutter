from gui.app_ui import create_app
from my_module import video_processing

if __name__ == "__main__":
    # video_processing.hardcode_subs()
    app = create_app()
    app.mainloop()
