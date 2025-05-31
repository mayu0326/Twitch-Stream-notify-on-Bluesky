import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
import customtkinter as ctk


DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
HEADING_FONT = ("Yu Gothic UI", 17, "bold")


class SettingStatusFrame(ctk.CTkFrame):
    """
    設定状況を表示するUIフレーム。
    参照元Tkinter版の機能をCustomTkinterで再現。
    """

    def __init__(self, master=None):
        super().__init__(master)
        # フレーム全体を中央寄せするための設定
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # 中央寄せ用のラッパーフレーム
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=0, column=0, sticky="nsew")
        self.center_frame.grid_rowconfigure(tuple(range(7)), weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        # new_gui/settings.env を優先して読み込む
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        if not os.path.exists(env_path):
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../settings.env'))
        load_dotenv(env_path, override=True)
        for child in self.center_frame.winfo_children():
            child.destroy()
        ctk.CTkLabel(self.center_frame, text="現在のアカウント設定状況", font=HEADING_FONT, anchor="center").grid(row=0, column=0, sticky="nsew", pady=(30, 10), padx=30)
        # Twitch
        twitch_id = os.getenv('TWITCH_BROADCASTER_ID') or '未設定'
        twitch_conv_id = os.getenv('TWITCH_BROADCASTER_ID_CONVERTED') or '未設定'
        twitch_text = f"Twitch連携：設定済み　(ユーザー名: {twitch_id} / ID: {twitch_conv_id})" if twitch_id != '未設定' else "Twitch連携：設定されていません"
        ctk.CTkLabel(self.center_frame, text=twitch_text, font=DEFAULT_FONT, anchor="center").grid(row=1, column=0, sticky="nsew", pady=6, padx=30)
        # YouTube
        yt_id = os.getenv('YOUTUBE_CHANNEL_ID') or '未設定'
        yt_text = f"YouTube連携：設定済み　(ID: {yt_id})" if yt_id != '未設定' else "YouTube連携：設定されていません"
        ctk.CTkLabel(self.center_frame, text=yt_text, font=DEFAULT_FONT, anchor="center").grid(row=2, column=0, sticky="nsew", pady=6, padx=30)
        # ニコニコ
        nico_id = os.getenv('NICONICO_USER_ID') or '未設定'
        nico_text = f"ニコニコ連携：設定済み　(ID: {nico_id})" if nico_id != '未設定' else "ニコニコ連携：設定されていません"
        ctk.CTkLabel(self.center_frame, text=nico_text, font=DEFAULT_FONT, anchor="center").grid(row=3, column=0, sticky="nsew", pady=6, padx=30)
        # Bluesky
        bsky_id = os.getenv('BLUESKY_USERNAME') or '未設定'
        bsky_text = f"Bluesky連携：設定済み　(ID: {bsky_id})" if bsky_id != '未設定' else "Bluesky連携：設定されていません"
        ctk.CTkLabel(self.center_frame, text=bsky_text, font=DEFAULT_FONT, anchor="center").grid(row=4, column=0, sticky="nsew", pady=6, padx=30)
        # Discord
        discord_url = os.getenv('discord_error_notifier_url')
        discord_enabled = os.getenv('DISCORD_NOTIFY_ENABLED', 'True').lower() == 'true'
        discord_text = "Discord連携：有効" if discord_enabled else "Discord連携：無効"
        if discord_url:
            if discord_url.startswith('https://discord.com/api/webhooks/'):
                discord_url_status = "URL形式OK"
            else:
                discord_url_status = "URL形式NG"
        else:
            discord_url_status = "URL未設定"
        ctk.CTkLabel(self.center_frame, text=f"{discord_text} (URL: {discord_url_status})", font=DEFAULT_FONT, anchor="center").grid(row=5, column=0, sticky="nsew", pady=6, padx=30)
        # トンネル
        tunnel_cmd = os.getenv('TUNNEL_CMD')
        tunnel_service_env = os.getenv('TUNNEL_SERVICE')
        ngrok_cmd = os.getenv('NGROK_CMD')
        localtunnel_cmd = os.getenv('LOCALTUNNEL_CMD')
        custom_cmd = os.getenv('CUSTOM_TUNNEL_CMD')
        # TUNNEL_SERVICEがnoneまたは空の場合は無効扱い
        if (tunnel_service_env is not None and tunnel_service_env.strip().lower() == "none") or (tunnel_service_env is not None and tunnel_service_env.strip() == ""):
            tunnel_status = "無効"
            tunnel_service = "設定されていません"
        elif tunnel_cmd or ngrok_cmd or localtunnel_cmd or custom_cmd:
            tunnel_status = "有効"
            if tunnel_service_env:
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
        ctk.CTkLabel(self.center_frame, text=f"トンネル通信機能：{tunnel_status} (サービス: {tunnel_service})", font=DEFAULT_FONT, anchor="center").grid(row=6, column=0, sticky="nsew", pady=6, padx=30)
