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
        from notification_customization_frame import NotificationCustomizationFrame
        self.twitch_frame = NotificationCustomizationFrame.create_twitch_tab(
            notebook)
        notebook.add(self.twitch_frame, text="Twitch")
        self.youtube_frame = NotificationCustomizationFrame.create_youtube_tab(
            notebook)
        notebook.add(self.youtube_frame, text="YouTube")
        self.nico_frame = NotificationCustomizationFrame.create_nico_tab(
            notebook)
        notebook.add(self.nico_frame, text="ニコニコ")
