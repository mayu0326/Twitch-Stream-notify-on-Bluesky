import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
import tkinter.ttk as ttk
import os
import subprocess
import requests
import time

class TunnelNgrokFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.auth_token = tk.StringVar()
        self.port = tk.StringVar()
        self.protocol = tk.StringVar(value="http")
        self.load_settings()  # 追加: 設定ファイルから読み込む

        self.create_widgets()

    def load_settings(self):
        """settings.envからngrok設定を読み込む"""
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        if not os.path.exists(env_path):
            return
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('NGROK_AUTH_TOKEN='):
                    self.auth_token.set(line.strip().split('=', 1)[1])
                elif line.startswith('NGROK_PORT='):
                    self.port.set(line.strip().split('=', 1)[1])
                elif line.startswith('NGROK_PROTOCOL='):
                    self.protocol.set(line.strip().split('=', 1)[1])

    @staticmethod
    def validate_port(value):
        # 空欄は許可（削除時のため）
        if value == "":
            return True
        # 数字のみ、最大5桁
        return value.isdigit() and len(value) <= 5

    def create_widgets(self):
        # 認証トークンの設定（ラベル＋入力欄 横並び）
        ttk.Label(
            self,
            text="認証トークン:",
            font=("Meiryo", 12, "bold")
        ).grid(row=0, column=0, sticky=tk.W, pady=(20, 5), padx=(20, 5))
        entry1 = ttk.Entry(self, textvariable=self.auth_token, width=32, font=("Meiryo", 11))
        entry1.grid(row=0, column=1, padx=(0, 20), pady=(20, 5), sticky="ew")

        # ポート番号（ラベル＋入力欄 横並び）
        ttk.Label(
            self,
            text="ポート番号:",
            font=("Meiryo", 12, "bold")
        ).grid(row=1, column=0, sticky=tk.W, padx=(20, 5), pady=(5, 5))
        vcmd = (self.register(self.validate_port), "%P")
        entry2 = ttk.Entry(
            self,
            textvariable=self.port,
            width=12,
            font=("Meiryo", 11),
            validate="key",
            validatecommand=vcmd)
        entry2.grid(row=1, column=1, padx=(0, 20), pady=(5, 5), sticky="ew")

        # プロトコル（ラベル＋ラジオボタン 横並び）
        ttk.Label(
            self,
            text="プロトコル:",
            font=("Meiryo", 12, "bold")
        ).grid(row=2, column=0, sticky=tk.W, padx=(20, 5), pady=(5, 5))
        radio_frame = ttk.Frame(self)
        radio_frame.grid(row=2, column=1, padx=(0, 20), pady=(5, 5), sticky="w")
        style = ttk.Style(self)
        style.configure("My.TRadiobutton", font=("Meiryo", 12))
        protocols = ["http", "tcp", "tls"]
        for proto in protocols:
            ttk.Radiobutton(radio_frame, text=proto.upper(), value=proto, variable=self.protocol,
                            style="My.TRadiobutton").pack(side="left", padx=5)

        # コマンド自動生成欄（ラベル＋入力欄 横並び）
        self.generated_cmd = tk.StringVar()
        self.update_cmd()
        ttk.Label(self, text="ngrok起動コマンド:", font=("Meiryo", 12, "bold")).grid(
            row=3, column=0, sticky=tk.W, padx=(20, 5), pady=(10, 0))
        ttk.Entry(self, textvariable=self.generated_cmd, width=32, font=("Meiryo", 11)).grid(
            row=3, column=1, padx=(0, 20), pady=(10, 0), sticky="ew")

        # 一時URL表示欄（ラベル＋入力欄 横並び）
        self.url_var = tk.StringVar()
        ttk.Label(
            self,
            text="ngrok一時URL:",
            font=("Meiryo", 11, "bold")).grid(
            row=4,
            column=0,
            sticky=tk.W,
            padx=(20, 5),
            pady=(10, 0))
        ttk.Entry(
            self,
            textvariable=self.url_var,
            width=32,
            font=("Meiryo", 11),
            state="readonly").grid(
            row=4,
            column=1,
            padx=(0, 20),
            pady=(10, 0),
            sticky="ew")

        # ボタン横並びフレーム（2カラムで中央寄せ）
        button_frame = ttk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 20), padx=20, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        ttk.Button(
            button_frame,
            text="保存",
            command=self.save_settings,
            style="Large.TButton").grid(
            row=0,
            column=0,
            padx=(0, 10),
            ipadx=30,
            ipady=10,
            sticky="ew")
        ttk.Button(
            button_frame,
            text="ngrokトンネル開始",
            command=self.start_ngrok_tunnel,
            style="Large.TButton").grid(
            row=0,
            column=1,
            padx=(10, 0),
            ipadx=30,
            ipady=10,
            sticky="ew")

    def update_cmd(self):
        port = self.port.get()
        protocol = self.protocol.get()
        cmd = f"ngrok {protocol} {port}" if port and protocol else ""
        self.generated_cmd.set(cmd)

    def save_settings(self):
        # 設定を保存する処理
        auth_token = self.auth_token.get()
        port = self.port.get()
        protocol = self.protocol.get()

        if not auth_token or not port or not protocol:
            tk.messagebox.showerror("エラー", "すべての項目を入力してください。")
            return

        # ngrokコマンドの存在チェック
        ngrok_path = None
        try:
            ngrok_path = subprocess.run(
                ["where", "ngrok"], capture_output=True, text=True, shell=True)
            if ngrok_path.returncode != 0:
                raise FileNotFoundError
        except Exception:
            tk.messagebox.showerror(
                "エラー", "ngrokがインストールされていません。公式サイトからダウンロードし、Pathを通してください。\nhttps://ngrok.com/download")
            return

        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        # settings.envにNGROK_AUTH_TOKEN, NGROK_PORT, NGROK_PROTOCOLを書き込む
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        found_token = found_port = found_proto = False
        for line in lines:
            if line.startswith('NGROK_AUTH_TOKEN='):
                new_lines.append(f'NGROK_AUTH_TOKEN={auth_token}\n')
                found_token = True
            elif line.startswith('NGROK_PORT='):
                new_lines.append(f'NGROK_PORT={port}\n')
                found_port = True
            elif line.startswith('NGROK_PROTOCOL='):
                new_lines.append(f'NGROK_PROTOCOL={protocol}\n')
                found_proto = True
            else:
                new_lines.append(line)
        if not found_token:
            new_lines.append(f'NGROK_AUTH_TOKEN={auth_token}\n')
        if not found_port:
            new_lines.append(f'NGROK_PORT={port}\n')
        if not found_proto:
            new_lines.append(f'NGROK_PROTOCOL={protocol}\n')
        # コマンドも保存
        cmd = self.generated_cmd.get()
        found_cmd = False
        for i, line in enumerate(new_lines):
            if line.startswith('NGROK_CMD='):
                new_lines[i] = f'NGROK_CMD={cmd}\n'
                found_cmd = True
        if not found_cmd:
            new_lines.append(f'NGROK_CMD={cmd}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        tk.messagebox.showinfo("保存完了", "ngrokの設定とコマンドが保存されました。")

    def start_ngrok_tunnel(self):
        # ngrok起動→APIから一時URL取得→settings.envのWEBHOOK_CALLBACK_URL_TEMPORARYを書き換え
        port = self.port.get()
        protocol = self.protocol.get()
        auth_token = self.auth_token.get()
        if not port or not protocol:
            tk.messagebox.showerror("エラー", "ポート番号とプロトコルを入力してください。")
            return
        # ngrok authtoken設定（初回のみ）
        if auth_token:
            subprocess.run(["ngrok", "config", "add-authtoken", auth_token], shell=True)
        # ngrok起動
        tunnel_cmd = ["ngrok", protocol, port]
        self.ngrok_proc = subprocess.Popen(
            tunnel_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True)
        # ngrok APIから一時URL取得（最大10秒リトライ）
        url = None
        for _ in range(20):
            try:
                resp = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=0.5)
                tunnels = resp.json().get("tunnels", [])
                for t in tunnels:
                    if t.get("public_url"):
                        url = t["public_url"]
                        break
                if url:
                    break
            except Exception:
                pass
            time.sleep(0.5)
        if not url:
            tk.messagebox.showerror("エラー", "ngrokの一時URL取得に失敗しました。ngrokが正しく起動しているか確認してください。")
            return
        self.url_var.set(url)
        # settings.envのWEBHOOK_CALLBACK_URL_TEMPORARYを書き換え
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith('WEBHOOK_CALLBACK_URL_TEMPORARY='):
                new_lines.append(f'WEBHOOK_CALLBACK_URL_TEMPORARY={url}\n')
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f'WEBHOOK_CALLBACK_URL_TEMPORARY={url}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        tk.messagebox.showinfo("ngrokトンネル開始",
                               f"ngrok一時URLを取得し、WEBHOOK_CALLBACK_URL_TEMPORARYに保存しました:\n{url}")
        # 各設定値変更時にコマンド自動更新
        self.auth_token.trace_add('write', lambda *a: self.update_cmd())
        self.port.trace_add('write', lambda *a: self.update_cmd())
        self.protocol.trace_add('write', lambda *a: self.update_cmd())
