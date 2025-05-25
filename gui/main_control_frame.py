"""
メインウィンドウのボット制御・ステータス表示部
"""
import tkinter as tk
from tkinter import ttk
import os
from dotenv import load_dotenv


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
        # サービスごとの状態表示（1行ずつ、ID欄付き）
        self.lbl_twitch_status = ttk.Label(
            self, text=f"Twitch連携：切断　(ID: {self.twitch_id})", font=status_font)
        self.lbl_twitch_status.grid(
            row=2, column=0, sticky=tk.W, pady=2, columnspan=3)
        self.lbl_yt_status = ttk.Label(
            self, text=f"YouTube連携：切断　(ID: {self.yt_id})", font=status_font)
        self.lbl_yt_status.grid(
            row=3, column=0, sticky=tk.W, pady=2, columnspan=3)
        self.lbl_nico_status = ttk.Label(
            self, text=f"ニコニコ連携：切断　(ID: {self.nico_id})", font=status_font)
        self.lbl_nico_status.grid(
            row=4, column=0, sticky=tk.W, pady=2, columnspan=3)
        self.lbl_bluesky_status = ttk.Label(
            self, text=f"Bluesky連携：未接続　(ID: {self.bsky_id})", font=status_font)
        self.lbl_bluesky_status.grid(
            row=5, column=0, sticky=tk.W, pady=2, columnspan=3)
        self.lbl_discord_status = ttk.Label(
            self, text=f"Discord連携：{self.discord_status}　(URL: {self.discord_id})", font=status_font)
        self.lbl_discord_status.grid(
            row=6, column=0, sticky=tk.W, pady=2, columnspan=3)
        self.lbl_tunnel_status = ttk.Label(
            self, text=f"トンネル通信機能：{self.tunnel_status}　(ID: {self.tunnel_id})", font=status_font)
        self.lbl_tunnel_status.grid(
            row=7, column=0, sticky=tk.W, pady=2, columnspan=3)
