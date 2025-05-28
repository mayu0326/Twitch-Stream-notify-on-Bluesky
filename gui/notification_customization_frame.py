import sys
import os
# sys.pathの調整（親ディレクトリをパスに追加）
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

"""
テンプレート・画像カスタマイズUI
"""
from gui.timezone_settings import TimeZoneSettings
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
try:
    from utils import change_template_file, change_image_file
except ModuleNotFoundError:
    # 相対import fallback（パッケージ実行時用）
    from ..utils import change_template_file, change_image_file


class NotificationCustomizationFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- タイムゾーン設定タブ（最左） ---
        tz_frame = TimeZoneSettings(notebook)
        notebook.add(tz_frame, text="タイムゾーン設定")

        # --- ログ/コンソール設定タブ ---
        from gui.logging_console_frame import LoggingConsoleFrame
        log_console_frame = LoggingConsoleFrame(notebook)
        notebook.add(log_console_frame, text="ログ/コンソール設定")

        # --- Discordタブ ---
        from gui.discord_notification_frame import DiscordNotificationFrame
        discord_frame = DiscordNotificationFrame(notebook)
        notebook.add(discord_frame, text="Discord通知設定")

        # --- ログビューアタブ ---
        from gui.log_viewer import LogViewer
        log_viewer_frame = LogViewer(notebook)
        notebook.add(log_viewer_frame, text="ログビューア")

        # フォント・ボタンサイズをさらに小さく（2回りダウン）
        small_font = ("Meiryo", 12)
        small_btn_style = ttk.Style()
        small_btn_style.configure("Big.TButton", font=small_font, padding=4)
        small_lbl_style = ttk.Style()
        small_lbl_style.configure("Big.TLabel", font=small_font)
        small_chk_style = ttk.Style()
        small_chk_style.configure("Big.TCheckbutton", font=small_font)
