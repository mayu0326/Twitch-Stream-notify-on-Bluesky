import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk


class SettingStatusFrame(ttk.Frame):
    """
    設定状況を表示するUIフレーム。
    旧MainControlFrameの機能を移植。
    """

    def __init__(self, master=None):
        super().__init__(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        self.create_widgets()

    def create_widgets(self):
        # settings.envの最新値を毎回反映
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'), override=True)
        # 既存ウィジェットを全削除
        for child in self.winfo_children():
            child.destroy()
        status_font = ("Meiryo", 16)
        heading_font = ("Meiryo", 18, "bold")
        ttk.Label(self, text="現在のアカウント設定状況", font=heading_font).grid(
            row=0, column=0, sticky=tk.W, pady=(10, 5), columnspan=3)
        # 最新のID情報を毎回取得
        twitch_id = os.getenv('TWITCH_BROADCASTER_ID') or '未設定'
        yt_id = os.getenv('YOUTUBE_CHANNEL_ID') or '未設定'
        nico_id = os.getenv('NICONICO_USER_ID') or '未設定'
        bsky_id = os.getenv('BLUESKY_USERNAME') or '未設定'
        # Twitch
        twitch_text = f"Twitch連携：設定済み　(ID: {twitch_id})" if twitch_id != '未設定' else "Twitch連携：設定されていません"
        ttk.Label(self, text=twitch_text, font=status_font).grid(
            row=1, column=0, sticky=tk.W, pady=2, columnspan=3)
        # YouTube
        yt_text = f"YouTube連携：設定済み　(ID: {yt_id})" if yt_id != '未設定' else "YouTube連携：設定されていません"
        ttk.Label(self, text=yt_text, font=status_font).grid(
            row=2, column=0, sticky=tk.W, pady=2, columnspan=3)
        # ニコニコ
        nico_text = f"ニコニコ連携：設定済み　(ID: {nico_id})" if nico_id != '未設定' else "ニコニコ連携：設定されていません"
        ttk.Label(self, text=nico_text, font=status_font).grid(
            row=3, column=0, sticky=tk.W, pady=2, columnspan=3)
        # Bluesky
        bsky_text = f"Bluesky連携：設定済み　(ID: {bsky_id})" if bsky_id != '未設定' else "Bluesky連携：設定されていません"
        ttk.Label(self, text=bsky_text, font=status_font).grid(
            row=4, column=0, sticky=tk.W, pady=2, columnspan=3)
        # Discord
        discord_url = os.getenv('discord_error_notifier_url')
        discord_enabled = os.getenv(
            'DISCORD_NOTIFY_ENABLED', 'True').lower() == 'true'
        discord_text = "Discord連携：有効" if discord_enabled else "Discord連携：無効"
        if discord_url:
            if discord_url.startswith('https://discord.com/api/webhooks/'):
                discord_url_status = "URL形式OK"
            else:
                discord_url_status = "URL形式NG"
        else:
            discord_url_status = "URL未設定"
        ttk.Label(self, text=f"{discord_text} (URL: {discord_url_status})", font=status_font).grid(
            row=5, column=0, sticky=tk.W, pady=2, columnspan=3)
        # トンネル
        tunnel_cmd = os.getenv('TUNNEL_CMD')
        tunnel_service_env = os.getenv('TUNNEL_SERVICE')
        ngrok_cmd = os.getenv('NGROK_CMD')
        localtunnel_cmd = os.getenv('LOCALTUNNEL_CMD')
        custom_cmd = os.getenv('CUSTOM_TUNNEL_CMD')
        # いずれかのコマンドが設定されていれば有効
        if tunnel_cmd or ngrok_cmd or localtunnel_cmd or custom_cmd:
            tunnel_status = "有効"
            if tunnel_service_env:
                # TUNNEL_SERVICEがあればそれを優先表示
                if tunnel_service_env == "cloudflare":
                    tunnel_service = "Cloudflare Tunnel"
                elif tunnel_service_env == "ngrok":
                    tunnel_service = "ngrok"
                elif tunnel_service_env == "localtunnel":
                    tunnel_service = "localtunnel"
                elif tunnel_service_env == "custom":
                    tunnel_service = "カスタム"
                else:
                    tunnel_service = tunnel_service_env
            else:
                # コマンドから判定
                if tunnel_cmd and "cloudflared" in tunnel_cmd:
                    tunnel_service = "Cloudflare Tunnel"
                elif ngrok_cmd or (tunnel_cmd and "ngrok" in tunnel_cmd):
                    tunnel_service = "ngrok"
                elif localtunnel_cmd or (tunnel_cmd and "localtunnel" in tunnel_cmd):
                    tunnel_service = "localtunnel"
                elif custom_cmd or (tunnel_cmd and ("custom" in tunnel_cmd or "CUSTOM_TUNNEL_CMD" in tunnel_cmd)):
                    tunnel_service = "カスタム"
                else:
                    tunnel_service = "不明"
        else:
            tunnel_status = "無効"
            tunnel_service = "設定されていません"
        ttk.Label(
            self,
            text=f"トンネル通信機能：{tunnel_status} (サービス: {tunnel_service})",
            font=status_font).grid(
            row=6,
            column=0,
            sticky=tk.W,
            pady=2,
            columnspan=3)
