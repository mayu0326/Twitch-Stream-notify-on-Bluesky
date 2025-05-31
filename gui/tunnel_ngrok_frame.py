
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

from version_info import __version__
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
import customtkinter as ctk
import subprocess
import requests
import time
import tkinter.messagebox as messagebox

try:
    import pyperclip
    _pyperclip_available = True
except ImportError:
    _pyperclip_available = False

SETTINGS_ENV_FILE = os.path.join(os.path.dirname(__file__), '../settings.env')

class TunnelNgrokFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.font = ("Yu Gothic UI", 15, "normal")
        self.auth_token = ctk.StringVar(value=self._load_auth_token())
        self.port = ctk.StringVar(value=self._load_port())
        self.protocol = ctk.StringVar(value=self._load_protocol())
        self.generated_cmd = ctk.StringVar()
        self.url_var = ctk.StringVar(value=self._load_temporary_url())
        self.status_var = ctk.StringVar(value="準備中…")
        # --- 中央寄せ用サブフレーム ---
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")
        self._create_widgets(center_frame)
        self._update_cmd()
        self.port.trace_add('write', lambda *a: self._update_cmd())
        self.protocol.trace_add('write', lambda *a: self._update_cmd())

    def _load_auth_token(self):
        if not os.path.exists(SETTINGS_ENV_FILE):
            return ""
        with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('NGROK_AUTH_TOKEN='):
                    return line.strip().split('=', 1)[1]
        return ""

    def _load_port(self):
        if not os.path.exists(SETTINGS_ENV_FILE):
            return ""
        with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('NGROK_PORT='):
                    return line.strip().split('=', 1)[1]
        return ""

    def _load_protocol(self):
        if not os.path.exists(SETTINGS_ENV_FILE):
            return "http"
        with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('NGROK_PROTOCOL='):
                    return line.strip().split('=', 1)[1]
        return "http"

    def _load_temporary_url(self):
        if not os.path.exists(SETTINGS_ENV_FILE):
            return ""
        with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('WEBHOOK_CALLBACK_URL_TEMPORARY='):
                    return line.strip().split('=', 1)[1]
        return ""

    def _validate_port(self, value):
        if value == "":
            return True
        return value.isdigit() and len(value) <= 5

    def _create_widgets(self, parent):
        ctk.CTkLabel(parent, text="認証トークン:", font=self.font, anchor="w").grid(row=0, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.auth_token, font=self.font, width=220).grid(row=0, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="ポート番号:", font=self.font, anchor="w").grid(row=1, column=0, sticky='w', pady=(10,0), padx=(10,0))
        port_entry = ctk.CTkEntry(parent, textvariable=self.port, font=self.font, width=120)
        port_entry.grid(row=1, column=1, padx=(0,10), pady=(10,0))
        port_entry.configure(validate="key", validatecommand=(self.register(self._validate_port), "%P"))
        ctk.CTkLabel(parent, text="プロトコル:", font=self.font, anchor="w").grid(row=2, column=0, sticky='w', pady=(10,0), padx=(10,0))
        proto_menu = ctk.CTkOptionMenu(parent, variable=self.protocol, values=["http", "tcp", "tls"], font=self.font, width=120)
        proto_menu.grid(row=2, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="ngrok起動コマンド:", font=self.font, anchor="w").grid(row=3, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.generated_cmd, font=self.font, width=320, state="readonly").grid(row=3, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="ngrok公開URL:", font=self.font, anchor="w").grid(row=4, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.url_var, font=self.font, width=320, state="readonly").grid(row=4, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="URLコピー", command=self._copy_url, font=self.font).grid(row=4, column=2, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="保存", command=self._save_settings, font=self.font).grid(row=5, column=1, pady=(20,0))
        ctk.CTkButton(parent, text="トンネル開始", command=self._start_ngrok_tunnel, font=self.font).grid(row=5, column=2, pady=(20,0))
        ctk.CTkLabel(parent, textvariable=self.status_var, font=self.font, anchor="w").grid(row=6, column=0, columnspan=3, sticky='w', padx=(10,0), pady=(10,0))

    def _update_cmd(self, *args):
        port = self.port.get()
        protocol = self.protocol.get()
        cmd = f"ngrok {protocol} {port}" if port and protocol else ""
        self.generated_cmd.set(cmd)

    def _save_settings(self):
        # ngrokコマンドの存在チェック
        try:
            result = subprocess.run(["where", "ngrok"], capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                raise FileNotFoundError
        except Exception:
            messagebox.showerror("エラー", "ngrokがインストールされていません。\n公式サイトからダウンロードし、Pathを通してください。\nhttps://ngrok.com/download")
            return
        auth_token = self.auth_token.get()
        port = self.port.get()
        protocol = self.protocol.get()
        cmd = self.generated_cmd.get()
        lines = []
        if os.path.exists(SETTINGS_ENV_FILE):
            with open(SETTINGS_ENV_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        new_lines = []
        found_token = found_port = found_proto = found_cmd = False
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
            elif line.startswith('NGROK_CMD='):
                new_lines.append(f'NGROK_CMD={cmd}\n')
                found_cmd = True
            else:
                new_lines.append(line)
        if not found_token:
            new_lines.append(f'NGROK_AUTH_TOKEN={auth_token}\n')
        if not found_port:
            new_lines.append(f'NGROK_PORT={port}\n')
        if not found_proto:
            new_lines.append(f'NGROK_PROTOCOL={protocol}\n')
        if not found_cmd:
            new_lines.append(f'NGROK_CMD={cmd}\n')
        with open(SETTINGS_ENV_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        messagebox.showinfo("保存完了", "ngrokの設定とコマンドが保存されました。")

    def _start_ngrok_tunnel(self):
        port = self.port.get()
        protocol = self.protocol.get()
        auth_token = self.auth_token.get()
        if not port or not protocol:
            messagebox.showerror("エラー", "ポート番号とプロトコルを入力してください。")
            return
        # ngrok authtoken設定（初回のみ）
        if auth_token:
            subprocess.run(["ngrok", "config", "add-authtoken", auth_token], shell=True)
        # ngrok起動
        tunnel_cmd = ["ngrok", protocol, port]
        try:
            self.status_var.set("ngrok起動中…")
            proc = subprocess.Popen(tunnel_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
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
                self.status_var.set("ngrok一時URL取得失敗")
                messagebox.showerror("エラー", "ngrokの一時URL取得に失敗しました。ngrokが正しく起動しているか確認してください。")
                return
            self.url_var.set(url)
            self.status_var.set("ngrok稼働中")
            self._save_temporary_url(url)
        except Exception as e:
            self.status_var.set("起動エラー")
            messagebox.showerror("エラー", f"ngrokの起動に失敗しました: {e}")

    def _save_temporary_url(self, url):
        lines = []
        if os.path.exists(SETTINGS_ENV_FILE):
            with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
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
        with open(SETTINGS_ENV_FILE, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    def _copy_url(self):
        url = self.url_var.get()
        if not url:
            messagebox.showwarning("URL未入力", "公開URLが空です。")
            return
        if _pyperclip_available:
            pyperclip.copy(url)
            messagebox.showinfo("コピー完了", "公開URLをクリップボードにコピーしました。")
        else:
            messagebox.showwarning("pyperclip未インストール", "pyperclipが未インストールのためコピーできません。\n\n'pip install pyperclip'でインストールしてください。")
