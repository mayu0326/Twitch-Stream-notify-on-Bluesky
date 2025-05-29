import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
.env編集用ダイアログ（バリデーション・マスク表示対応）
"""
import tkinter as tk
from tkinter import ttk, messagebox


class SettingsEditorDialog(tk.Toplevel):
    def __init__(self, master=None, env_data=None, on_save=None):
        super().__init__(master)
        self.title("設定エディタ")
        self.geometry("400x350")
        self.resizable(False, False)
        self.env_data = env_data or {}
        self.on_save = on_save
        self.vars = {}
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.vars['twitch_id'] = tk.StringVar(
            value=self.env_data.get('TWITCH_CLIENT_ID', ''))
        self.vars['twitch_secret'] = tk.StringVar(
            value=self.env_data.get('TWITCH_CLIENT_SECRET', ''))
        self.vars['bsky_user'] = tk.StringVar(
            value=self.env_data.get('BSKY_USER', ''))
        self.vars['bsky_pass'] = tk.StringVar(
            value=self.env_data.get('BSKY_APP_PASSWORD', ''))
        # YouTube/ニコニコ/Discordの設定項目追加
        self.vars['yt_api_key'] = tk.StringVar(
            value=self.env_data.get('YOUTUBE_API_KEY', ''))
        self.vars['yt_channel_id'] = tk.StringVar(
            value=self.env_data.get('YOUTUBE_CHANNEL_ID', ''))
        self.vars['yt_poll_interval'] = tk.StringVar(
            value=self.env_data.get('YOUTUBE_POLL_INTERVAL', '60'))
        self.vars['nico_user_id'] = tk.StringVar(
            value=self.env_data.get('NICONICO_USER_ID', ''))
        self.vars['nico_poll_interval'] = tk.StringVar(
            value=self.env_data.get('NICONICO_LIVE_POLL_INTERVAL', '60'))
        self.vars['discord_webhook'] = tk.StringVar(
            value=self.env_data.get('DISCORD_ERROR_NOTIFIER_URL', ''))
        self.vars['discord_level'] = tk.StringVar(
            value=self.env_data.get('DISCORD_NOTIFY_LEVEL', 'CRITICAL'))
        ttk.Label(frame, text="TwitchクライアントID").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['twitch_id']).pack(fill=tk.X)
        ttk.Label(frame, text="Twitchクライアントシークレット").pack(anchor=tk.W)
        ttk.Entry(
            frame, textvariable=self.vars['twitch_secret'], show='*').pack(fill=tk.X)
        ttk.Label(frame, text="Blueskyユーザー名").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['bsky_user']).pack(fill=tk.X)
        ttk.Label(frame, text="Blueskyアプリパスワード").pack(anchor=tk.W)
        ttk.Entry(
            frame, textvariable=self.vars['bsky_pass'], show='*').pack(fill=tk.X)
        # YouTube/ニコニコ/Discordの設定項目
        ttk.Label(frame, text="YouTube APIキー").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['yt_api_key']).pack(fill=tk.X)
        ttk.Label(frame, text="YouTubeチャンネルID").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['yt_channel_id']).pack(
            fill=tk.X)
        ttk.Label(frame, text="YouTubeポーリング間隔(秒)").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['yt_poll_interval']).pack(
            fill=tk.X)
        ttk.Label(frame, text="ニコニコユーザーID").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['nico_user_id']).pack(
            fill=tk.X)
        ttk.Label(frame, text="ニコニコポーリング間隔(秒)").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['nico_poll_interval']).pack(
            fill=tk.X)
        ttk.Label(frame, text="Discord Webhook URL").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['discord_webhook']).pack(
            fill=tk.X)
        ttk.Label(frame, text="Discord通知レベル").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.vars['discord_level']).pack(
            fill=tk.X)
        btn_save = ttk.Button(self, text="保存", command=self.save)
        btn_save.pack(side=tk.RIGHT, padx=10, pady=10)
        btn_cancel = ttk.Button(self, text="キャンセル", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=10, pady=10)

    def save(self):
        # TODO: バリデーション・保存処理
        if self.on_save:
            self.on_save({k: v.get() for k, v in self.vars.items()})
        self.destroy()
