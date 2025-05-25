import tkinter as tk
from tkinter import ttk, filedialog


class BlueskyPostSettingsFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        # --- Twitchタブ ---
        from twitch_notice_frame import TwitchNoticeFrame
        self.twitch_frame = TwitchNoticeFrame(notebook)
        notebook.add(self.twitch_frame, text="Twitch")
        # --- YouTubeタブ ---
        from youtube_notice_frame import YouTubeNoticeFrame
        self.youtube_frame = YouTubeNoticeFrame(notebook)
        notebook.add(self.youtube_frame, text="YouTube")
        # --- ニコニコタブ ---
        from niconico_notice_frame import NiconicoNoticeFrame
        self.nico_frame = NiconicoNoticeFrame(notebook)
        notebook.add(self.nico_frame, text="ニコニコ")
