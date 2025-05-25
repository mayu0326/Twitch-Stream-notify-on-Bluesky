"""
メインウィンドウのボット制御・ステータス表示部
"""
import tkinter as tk
from tkinter import ttk
import os
from dotenv import load_dotenv
from console_output_viewer import ConsoleOutputViewer


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
        # フォント・ボタンサイズの拡大設定
        big_font = ("Meiryo", 18)
        big_btn_style = ttk.Style()
        big_btn_style.configure("Big.TButton", font=big_font, padding=20)
        big_lbl_style = ttk.Style()
        big_lbl_style.configure("Big.TLabel", font=big_font)
        big_chk_style = ttk.Style()
        big_chk_style.configure("Big.TCheckbutton", font=big_font)

        # ボタン用のサブフレームを2行構成で作成
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, columnspan=5, pady=10)
        # 1行目: 起動・停止
        self.btn_start = ttk.Button(
            button_frame, text="アプリ起動", command=self.start_app, style="Big.TButton")
        self.btn_stop = ttk.Button(
            button_frame, text="アプリ停止", command=self.stop_app, state=tk.DISABLED, style="Big.TButton")
        self.btn_start.grid(row=0, column=0, padx=10,
                            ipadx=20, ipady=10, sticky=tk.EW)
        self.btn_stop.grid(row=0, column=1, padx=10,
                           ipadx=20, ipady=10, sticky=tk.EW)
        # 2行目: 再起動・コンソール出力
        self.btn_restart = ttk.Button(
            button_frame, text="アプリ再起動", command=self.restart_app, state=tk.DISABLED, style="Big.TButton")
        self.btn_console = ttk.Button(
            button_frame, text="コンソール出力表示", command=self.open_console_output, style="Big.TButton")
        self.btn_restart.grid(row=1, column=0, padx=10,
                              ipadx=20, ipady=10, sticky=tk.EW)
        self.btn_console.grid(row=1, column=1, padx=10,
                              ipadx=20, ipady=10, sticky=tk.EW)

        status_font = ("Meiryo", 16)
        self.lbl_status = ttk.Label(
            self, text="アプリステータス: 停止中", foreground="red", font=status_font)
        self.lbl_status.grid(row=1, column=0, columnspan=5, pady=(20, 0))

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

    def start_app(self):
        if self.bot_manager:
            self.bot_manager.start()
        self.lbl_status.config(text="アプリステータス: 実行中", foreground="green")
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_restart.config(state=tk.NORMAL)

    def stop_app(self):
        if self.bot_manager:
            self.bot_manager.stop()
        self.lbl_status.config(text="アプリステータス: 停止中", foreground="red")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_restart.config(state=tk.DISABLED)

    def restart_app(self):
        if self.bot_manager:
            self.bot_manager.restart()
        self.lbl_status.config(text="アプリステータス: 再起動中", foreground="orange")

    def open_console_output(self):
        if self.bot_manager:
            ConsoleOutputViewer(self, bot_manager=self.bot_manager)

    def update_status_from_bot(self, status):
        # Botプロセスの状態変化に応じてステータス欄を更新
        if status == "starting":
            self.lbl_status.config(
                text="アプリステータス: 起動中...", foreground="orange")
        elif status == "running":
            self.lbl_status.config(text="アプリステータス: 実行中", foreground="blue")
        elif status == "stopping":
            self.lbl_status.config(
                text="アプリステータス: 停止中...", foreground="orange")
        elif status == "stopped":
            self.lbl_status.config(text="アプリステータス: 停止", foreground="red")
        elif status == "restarting":
            self.lbl_status.config(
                text="アプリステータス: 再起動中...", foreground="orange")
        elif status == "error":
            self.lbl_status.config(text="アプリステータス: 異常終了", foreground="red")
        else:
            self.lbl_status.config(text="アプリステータス: 不明", foreground="gray")
