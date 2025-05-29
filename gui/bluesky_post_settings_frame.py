# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""
from version_info import __version__
from tkinter import ttk, filedialog
import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

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


class BlueskyPostSettingsFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        # --- Twitchタブ ---
        from gui.twitch_notice_frame import TwitchNoticeFrame
        self.twitch_frame = TwitchNoticeFrame(notebook)
        notebook.add(self.twitch_frame, text="Twitch")
        # --- YouTubeタブ ---
        from gui.youtube_notice_frame import YouTubeNoticeFrame
        self.youtube_frame = YouTubeNoticeFrame(notebook)
        notebook.add(self.youtube_frame, text="YouTube")
        # --- ニコニコタブ ---
        from gui.niconico_notice_frame import NiconicoNoticeFrame
        self.nico_frame = NiconicoNoticeFrame(notebook)
        notebook.add(self.nico_frame, text="ニコニコ")
