# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

# Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# このプログラムはフリーソフトウェアです。フリーソフトウェア財団によって発行された
# GNU 一般公衆利用許諾契約書（バージョン2またはそれ以降）に基づき、再配布または
# 改変することができます。
#
# このプログラムは有用であることを願って配布されていますが、
# 商品性や特定目的への適合性についての保証はありません。
# 詳細はGNU一般公衆利用許諾契約書をご覧ください。
#
# このプログラムとともにGNU一般公衆利用許諾契約書が配布されているはずです。
# もし同梱されていない場合は、フリーソフトウェア財団までご請求ください。
# 住所: 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

"""
テンプレート・画像カスタマイズUI
"""
from version_info import __version__
from gui.timezone_settings import TimezoneSettingsFrame
import sys
import os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import subprocess

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")


# sys.pathの調整（親ディレクトリをパスに追加）
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


class LoggingNotificationFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        notebook = ctk.CTkTabview(self, width=700, height=500, corner_radius=8)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        # サブタブのボタンフォントを明示的にnormal指定
        notebook._segmented_button.configure(font=DEFAULT_FONT)
        # タイムゾーン設定タブ
        notebook.add("タイムゾーン設定")
        tz_tab = notebook.tab("タイムゾーン設定")
        tz_inner = ctk.CTkFrame(tz_tab)
        tz_inner.grid(row=0, column=0, sticky="nsew")
        tz_tab.grid_rowconfigure(0, weight=1)
        tz_tab.grid_columnconfigure(0, weight=1)
        tz_frame = TimezoneSettingsFrame(tz_inner)
        tz_frame.pack(fill="both", expand=True)
        # ログ/コンソール設定タブ
        notebook.add("ログ/コンソール設定")
        log_tab = notebook.tab("ログ/コンソール設定")
        log_inner = ctk.CTkFrame(log_tab)
        log_inner.grid(row=0, column=0, sticky="nsew")
        log_tab.grid_rowconfigure(0, weight=1)
        log_tab.grid_columnconfigure(0, weight=1)
        from gui.logging_console_frame import LoggingConsoleFrame
        log_console_frame = LoggingConsoleFrame(log_inner)
        log_console_frame.pack(fill="both", expand=True)
        # Discord通知設定タブ
        notebook.add("Discord通知設定")
        discord_tab = notebook.tab("Discord通知設定")
        discord_inner = ctk.CTkFrame(discord_tab)
        discord_inner.grid(row=0, column=0, sticky="nsew")
        discord_tab.grid_rowconfigure(0, weight=1)
        discord_tab.grid_columnconfigure(0, weight=1)
        from gui.discord_notification_frame import DiscordNotificationFrame
        discord_frame = DiscordNotificationFrame(discord_inner)
        discord_frame.pack(fill="both", expand=True)
        # ログビューアタブ
        notebook.add("ログビューア")
        logv_tab = notebook.tab("ログビューア")
        logv_inner = ctk.CTkFrame(logv_tab)
        logv_inner.grid(row=0, column=0, sticky="nsew")
        logv_tab.grid_rowconfigure(0, weight=1)
        logv_tab.grid_columnconfigure(0, weight=1)
        from .log_viewer import LogViewer
        log_viewer_frame = LogViewer(logv_inner)
        log_viewer_frame.pack(fill="both", expand=True)
