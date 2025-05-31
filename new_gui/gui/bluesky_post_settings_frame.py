# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = "0.0.0-hotmock"

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


import customtkinter as ctk

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")

TEMPLATE_KEYS = {
    "Twitch": [
        ("配信開始テンプレート", "BLUESKY_TEMPLATE_PATH"),
        ("配信終了テンプレート", "BLUESKY_OFFLINE_TEMPLATE_PATH"),
        ("画像ファイル", "BLUESKY_IMAGE_PATH"),
    ],
    "YouTube": [
        ("配信開始テンプレート", "BLUESKY_YT_ONLINE_TEMPLATE_PATH"),
        ("新着動画テンプレート", "BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH"),
        ("画像ファイル", "BLUESKY_IMAGE_PATH"),
    ],
    "ニコニコ": [
        ("配信開始テンプレート", "BLUESKY_NICO_ONLINE_TEMPLATE_PATH"),
        ("新着動画テンプレート", "BLUESKY_NICO_NEW_VIDEO_TEMPLATE_PATH"),
        ("画像ファイル", "BLUESKY_IMAGE_PATH"),
    ],
}

class BlueskyPostSettingsFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True)
        # --- Twitchタブ ---
        tabview.add("Twitch")
        from .twitch_notice_frame import TwitchNoticeFrame
        self.twitch_frame = TwitchNoticeFrame(tabview)
        self.twitch_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("Twitch"))
        # --- YouTubeタブ ---
        tabview.add("YouTube")
        from .youtube_notice_frame import YouTubeNoticeFrame
        self.youtube_frame = YouTubeNoticeFrame(tabview)
        self.youtube_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("YouTube"))
        # --- ニコニコタブ ---
        tabview.add("ニコニコ")
        from .niconico_notice_frame import NiconicoNoticeFrame
        self.nico_frame = NiconicoNoticeFrame(tabview)
        self.nico_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("ニコニコ"))

        # タブボタンのサイズとフォントを変更
        for button in tabview._segmented_button._buttons_dict.values():
            button.configure(font=DEFAULT_FONT)