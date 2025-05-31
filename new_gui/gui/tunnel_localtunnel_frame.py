import sys
import os
import subprocess
import threading
import customtkinter as ctk
import tkinter.messagebox as messagebox

try:
    import pyperclip
    _pyperclip_available = True
except ImportError:
    _pyperclip_available = False

SETTINGS_ENV_FILE = os.path.join(os.path.dirname(__file__), '../settings.env')
LOCALTUNNEL_KEY = "LOCALTUNNEL_CMD"


class TunnelLocalTunnelFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.font = ("Yu Gothic UI", 15, "normal")
        self.port = ctk.StringVar(value=self._load_port())
        self.generated_cmd = ctk.StringVar()
        self.url_var = ctk.StringVar(value=self._load_temporary_url())
        self.status_var = ctk.StringVar(value="準備中…")
        # --- 中央寄せ用サブフレーム ---
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")
        self._create_widgets(center_frame)
        self._update_cmd()
        self.port.trace_add('write', lambda *a: self._update_cmd())

    def _load_port(self):
        if not os.path.exists(SETTINGS_ENV_FILE):
            return ""
        with open(SETTINGS_ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('LOCALTUNNEL_PORT='):
                    return line.strip().split('=', 1)[1]
        return ""

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
        ctk.CTkLabel(parent, text="ポート番号:", font=self.font, anchor="w").grid(row=0, column=0, sticky='w', pady=(10,0), padx=(10,0))
        port_entry = ctk.CTkEntry(parent, textvariable=self.port, font=self.font, width=120)
        port_entry.grid(row=0, column=1, padx=(0,10), pady=(10,0))
        port_entry.configure(validate="key", validatecommand=(self.register(self._validate_port), "%P"))
        ctk.CTkLabel(parent, text="localtunnel起動コマンド:", font=self.font, anchor="w").grid(row=1, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.generated_cmd, font=self.font, width=320, state="readonly").grid(row=1, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="localtunnel公開URL:", font=self.font, anchor="w").grid(row=2, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.url_var, font=self.font, width=320, state="readonly").grid(row=2, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="URLコピー", command=self._copy_url, font=self.font).grid(row=2, column=2, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="保存", command=self._save_cmd, font=self.font).grid(row=3, column=1, pady=(20,0))
        ctk.CTkButton(parent, text="トンネル開始", command=self._start_localtunnel, font=self.font).grid(row=3, column=2, pady=(20,0))
        ctk.CTkLabel(parent, textvariable=self.status_var, font=self.font, anchor="w").grid(row=4, column=0, columnspan=3, sticky='w', padx=(10,0), pady=(10,0))

    def _update_cmd(self, *args):
        port = self.port.get()
        cmd = f"lt --port {port}" if port else ""
        self.generated_cmd.set(cmd)

    def _save_cmd(self):
        # ltコマンドの存在チェック
        try:
            result = subprocess.run(["where", "lt"], capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                raise FileNotFoundError
        except Exception:
            messagebox.showerror("エラー", "localtunnel (lt) がインストールされていません。\n公式サイトの手順でインストールし、Pathを通してください。\nhttps://github.com/localtunnel/localtunnel")
            return
        port_value = self.port.get()
        cmd = self.generated_cmd.get()
        lines = []
        if os.path.exists(SETTINGS_ENV_FILE):
            with open(SETTINGS_ENV_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        new_lines = []
        found_cmd = found_port = False
        for line in lines:
            if line.startswith('LOCALTUNNEL_CMD='):
                new_lines.append(f'LOCALTUNNEL_CMD={cmd}\n')
                found_cmd = True
            elif line.startswith('LOCALTUNNEL_PORT='):
                new_lines.append(f'LOCALTUNNEL_PORT={port_value}\n')
                found_port = True
            else:
                new_lines.append(line)
        if not found_cmd:
            new_lines.append(f'LOCALTUNNEL_CMD={cmd}\n')
        if not found_port:
            new_lines.append(f'LOCALTUNNEL_PORT={port_value}\n')
        with open(SETTINGS_ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        messagebox.showinfo("保存完了", "LocalTunnelの設定とコマンドが保存されました。")

    def _start_localtunnel(self):
        port = self.port.get()
        if not port:
            messagebox.showerror("エラー", "ポート番号を入力してください。")
            return
        self.status_var.set("LocalTunnel起動中…")
        self.url_var.set("")
        threading.Thread(target=self._run_localtunnel, args=(port,), daemon=True).start()

    def _run_localtunnel(self, port):
        cmd = self.generated_cmd.get().strip().replace("{port}", port)
        if not cmd:
            self.status_var.set("コマンド未設定")
            return
        try:
            proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.stdout is not None:
                for line in proc.stdout:
                    if "your url is:" in line:
                        url = line.strip().split("your url is:")[-1].strip()
                        self.url_var.set(url)
                        self.status_var.set("LocalTunnel稼働中")
                        self._save_temporary_url(url)
                        break
        except Exception as e:
            self.status_var.set("起動エラー")
            messagebox.showerror("エラー", f"LocalTunnelの起動に失敗しました: {e}")

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
