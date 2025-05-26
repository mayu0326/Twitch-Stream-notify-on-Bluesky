# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from dotenv import load_dotenv
import os
from tkinter import ttk
import tkinter as tk
from version import __version__

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

"""
メインウィンドウのボット制御・ステータス表示部
"""


class MainControlFrame(ttk.Frame):
    def __init__(self, master=None, bot_manager=None):
        super().__init__(master)
        self.bot_manager = bot_manager
        # 設定ファイルからID等を取得
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        self.twitch_id = os.getenv('TWITCH_BROADCASTER_ID') or '未設定'
        self.yt_id = os.getenv('YOUTUBE_CHANNEL_ID') or '未設定'
        self.nico_id = os.getenv('NICONICO_USER_ID') or '未設定'
        self.bsky_id = os.getenv('BLUESKY_USERNAME') or '未設定'
        discord_url = os.getenv('discord_error_notifier_url')
        if discord_url and discord_url.strip():
            self.discord_status = "有効"
            self.discord_id = "設定されています"
        else:
            self.discord_status = "無効"
            self.discord_id = "設定されていません"
        tunnel_cmd = os.getenv('TUNNEL_CMD')
        if tunnel_cmd and tunnel_cmd.strip():
            self.tunnel_status = "有効"
            self.tunnel_id = "設定済み"
        else:
            self.tunnel_status = "無効"
            self.tunnel_id = "未設定"
        self.create_widgets()

    def create_widgets(self):
        status_font = ("Meiryo", 16)

        # Add heading for account settings
        heading_font = ("Meiryo", 18, "bold")
        self.lbl_heading = ttk.Label(
            self, text="現在のアカウント設定状況", font=heading_font)
        self.lbl_heading.grid(row=0, column=0, sticky=tk.W,
                              pady=(10, 5), columnspan=3)

        # Update Twitch status
        if self.twitch_id != '未設定':
            twitch_text = f"Twitch連携：設定済み　(ID: {self.twitch_id})"
        else:
            twitch_text = "Twitch連携：設定されていません"
        self.lbl_twitch_status = ttk.Label(
            self, text=twitch_text, font=status_font)
        self.lbl_twitch_status.grid(
            row=1, column=0, sticky=tk.W, pady=2, columnspan=3)

        # Update YouTube status
        if self.yt_id != '未設定':
            yt_text = f"YouTube連携：設定済み　(ID: {self.yt_id})"
        else:
            yt_text = "YouTube連携：設定されていません"
        self.lbl_yt_status = ttk.Label(
            self, text=yt_text, font=status_font)
        self.lbl_yt_status.grid(
            row=2, column=0, sticky=tk.W, pady=2, columnspan=3)

        # Update NicoNico status
        if self.nico_id != '未設定':
            nico_text = f"ニコニコ連携：設定済み　(ID: {self.nico_id})"
        else:
            nico_text = "ニコニコ連携：設定されていません"
        self.lbl_nico_status = ttk.Label(
            self, text=nico_text, font=status_font)
        self.lbl_nico_status.grid(
            row=3, column=0, sticky=tk.W, pady=2, columnspan=3)

        # Update Bluesky status
        if self.bsky_id != '未設定':
            bsky_text = f"Bluesky連携：設定済み　(ID: {self.bsky_id})"
        else:
            bsky_text = "Bluesky連携：設定されていません"
        self.lbl_bluesky_status = ttk.Label(
            self, text=bsky_text, font=status_font)
        self.lbl_bluesky_status.grid(
            row=4, column=0, sticky=tk.W, pady=2, columnspan=3)

        # Update Discord status with URL validation and always display URL status
        discord_url = os.getenv('discord_error_notifier_url')
        discord_enabled = os.getenv(
            'DISCORD_NOTIFICATION_ENABLED', 'false').lower() == 'true'

        if discord_enabled:
            discord_text = "Discord連携：有効"
        else:
            discord_text = "Discord連携：無効"

        if discord_url:
            if discord_url.startswith('https://discord.com/api/webhooks/'):
                discord_url_status = "URL形式OK"
            else:
                discord_url_status = "URL形式NG"
        else:
            discord_url_status = "URL未設定"

        self.lbl_discord_status = ttk.Label(
            self, text=f"{discord_text} (URL: {discord_url_status})", font=status_font)
        self.lbl_discord_status.grid(
            row=5, column=0, sticky=tk.W, pady=2, columnspan=3)

        # Update Tunnel Communication status
        tunnel_cmd = os.getenv('TUNNEL_CMD')

        if tunnel_cmd:
            tunnel_status = "有効"
            if "cloudflared" in tunnel_cmd:
                tunnel_service = "Cloudflare Tunnel"
            elif "ngrok" in tunnel_cmd:
                tunnel_service = "ngrok"
            else:
                tunnel_service = "カスタム"
        else:
            tunnel_status = "無効"
            tunnel_service = "設定されていません"

        self.lbl_tunnel_status = ttk.Label(
            self, text=f"トンネル通信機能：{tunnel_status} (サービス: {tunnel_service})", font=status_font)
        self.lbl_tunnel_status.grid(
            row=6, column=0, sticky=tk.W, pady=2, columnspan=3)
