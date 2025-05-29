import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import subprocess
import tkinter as tk
import tkinter.ttk as ttk
import threading
from tkinter import messagebox

SETTINGS_ENV_FILE = os.path.join(os.path.dirname(__file__), '../settings.env')
LOCALTUNNEL_KEY = "LOCALTUNNEL_CMD"


class TunnelLocaltunnelFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.process = None
        self.url_var = tk.StringVar()
        self.port = tk.StringVar()
        self.cmd_var = tk.StringVar(value=self.read_localtunnel_cmd())
        self.status_var = tk.StringVar(value="準備中…")
        self.port_entry = None
        self.cmd_entry = None
        self.start_btn = None
        self.status_label = None
        self.url_entry = None
        self.load_settings()
        self.create_widgets()

    def load_settings(self):
        """settings.envからlocaltunnel設定を読み込む"""
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        if not os.path.exists(env_path):
            return
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('LOCALTUNNEL_PORT='):
                    self.port.set(line.strip().split('=', 1)[1])
                elif line.startswith('LOCALTUNNEL_CMD='):
                    self.cmd_var.set(line.strip().split('=', 1)[1])

    @staticmethod
    def validate_port(value):
        # 空欄は許可（削除時のため）
        if value == "":
            return True
        # 数字のみ、最大5桁
        return value.isdigit() and len(value) <= 5

    def create_widgets(self) -> None:
        # ポート番号の設定
        ttk.Label(
            self,
            text="ポート番号:",
            font=(
                "Meiryo",
                12,
                "bold")).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky=tk.W,
            pady=(
                10,
                5),
            padx=20)
        # バリデーション関数
        vcmd = (self.register(self.validate_port), "%P")
        self.port_entry = ttk.Entry(
            self, textvariable=self.port, width=50, font=(
                "Meiryo", 11), validate="key", validatecommand=vcmd)
        self.port_entry.grid(row=1, column=0, padx=20, pady=(0, 10), columnspan=2, sticky="ew")

        # コマンド自動生成欄のみ表示
        self.generated_cmd = tk.StringVar()
        self.update_cmd()
        ttk.Label(self, text="localtunnel起動コマンド:", font=("Meiryo", 12, "bold")).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, padx=20, pady=(10, 0))
        ttk.Entry(self, textvariable=self.generated_cmd, width=50, font=("Meiryo", 11)).grid(
            row=3, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="ew")

        # 一時URL表示欄
        self.url_var = tk.StringVar()
        ttk.Label(
            self,
            text="localtunnel一時URL:",
            font=("Meiryo", 11, "bold")).grid(
            row=4,
            column=0,
            sticky=tk.W,
            padx=20)
        ttk.Entry(
            self,
            textvariable=self.url_var,
            width=50,
            font=("Meiryo", 11),
            state="readonly").grid(
            row=5,
            column=0,
            columnspan=2,
            padx=20,
            pady=(0, 10),
            sticky="ew")
        # ボタン横並びフレーム（最下部に移動）
        button_frame = ttk.Frame(self)
        button_frame.grid(row=20, column=0, columnspan=3, pady=(10, 20), padx=20, sticky="ew")
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
            text="localtunnelトンネル開始",
            command=self.start_localtunnel,
            style="Large.TButton").grid(
            row=0,
            column=1,
            padx=(10, 0),
            ipadx=30,
            ipady=10,
            sticky="ew")
        # ウィンドウサイズ調整（削除）
        # self.master.geometry("700x600")

    def update_cmd(self):
        port = self.port.get()
        cmd = f"lt --port {port}" if port else ""
        self.generated_cmd.set(cmd)

    @staticmethod
    def read_localtunnel_cmd() -> str:
        try:
            with open(SETTINGS_ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(f"{LOCALTUNNEL_KEY}="):
                        return line.strip().split("=", 1)[1]
        except (FileNotFoundError, IOError):
            return ""
        return ""

    def save_localtunnel_cmd(self) -> None:
        # ltコマンドの存在チェック
        lt_path = None
        try:
            lt_path = subprocess.run(["where", "lt"], capture_output=True, text=True, shell=True)
            if lt_path.returncode != 0:
                raise FileNotFoundError
        except Exception:
            messagebox.showerror(
                "エラー",
                "localtunnel (lt) がインストールされていません。\n公式サイトの手順でインストールし、Pathを通してください。\nhttps://github.com/localtunnel/localtunnel")
            return

        try:
            lines = []
            found_cmd = False
            found_port = False
            port_value = self.port.get()  # ←ここを修正
            with open(SETTINGS_ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(f"{LOCALTUNNEL_KEY}="):
                        lines.append(f"{LOCALTUNNEL_KEY}={self.cmd_var.get()}\n")
                        found_cmd = True
                    elif line.strip().startswith("LOCALTUNNEL_PORT="):
                        lines.append(f"LOCALTUNNEL_PORT={port_value}\n")
                        found_port = True
                    else:
                        lines.append(line)
            if not found_cmd:
                lines.append(f"{LOCALTUNNEL_KEY}={self.cmd_var.get()}\n")
            if not found_port:
                lines.append(f"LOCALTUNNEL_PORT={port_value}\n")
            with open(SETTINGS_ENV_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)
            # コマンドも保存
            cmd = self.generated_cmd.get()
            found_cmd = False
            for i, line in enumerate(lines):
                if line.startswith('LOCALTUNNEL_CMD='):
                    lines[i] = f'LOCALTUNNEL_CMD={cmd}\n'
                    found_cmd = True
            if not found_cmd:
                lines.append(f'LOCALTUNNEL_CMD={cmd}\n')
            with open(SETTINGS_ENV_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)
            messagebox.showinfo("保存完了", "LocalTunnelの設定とコマンドが保存されました。")
        except (FileNotFoundError, IOError) as e:
            messagebox.showerror("エラー", f"保存に失敗しました: {e}")

    def save_settings(self):
        import tkinter as tk
        tk.messagebox.showinfo("保存完了", "localtunnelの設定が保存されました（ダミー実装）")

    def start_localtunnel(self) -> None:
        port = self.port_entry.get()
        self.status_var.set("LocalTunnel起動中…")
        self.url_var.set("")
        threading.Thread(target=self.run_localtunnel, args=(port,), daemon=True).start()

    def run_localtunnel(self, port: str) -> None:
        cmd_text = self.cmd_var.get().strip().replace("{port}", port)
        cmd = cmd_text.split()
        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if self.process.stdout is not None:
                for line in self.process.stdout:
                    if "your url is:" in line:
                        url = line.strip().split("your url is:")[-1].strip()
                        self.url_var.set(url)
                        self.status_var.set("LocalTunnel稼働中")
                        self.status_label.configure(font=("Meiryo", 11))
                        self.status_label.grid(row=5, column=0, pady=3, padx=20, sticky="w")
                        # LocalTunnel一時URLをsettings.envに保存
                        if self.url_var.get():
                            env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
                            lines = []
                            if os.path.exists(env_path):
                                with open(env_path, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                            new_lines = []
                            found = False
                            for line in lines:
                                if line.startswith('WEBHOOK_CALLBACK_URL_TEMPORARY='):
                                    new_lines.append(f'WEBHOOK_CALLBACK_URL_TEMPORARY={self.url_var.get()}\n')
                                    found = True
                                else:
                                    new_lines.append(line)
                            if not found:
                                new_lines.append(f'WEBHOOK_CALLBACK_URL_TEMPORARY={self.url_var.get()}\n')
                            with open(env_path, 'w', encoding='utf-8') as f:
                                f.writelines(new_lines)
                        break
        except (subprocess.SubprocessError, OSError) as e:
            self.status_var.set("LocalTunnel起動エラー")
            self.status_label.configure(font=("Meiryo", 11))
            self.status_label.grid(row=5, column=0, pady=3, padx=20, sticky="w")
            messagebox.showerror("エラー", f"LocalTunnelの起動に失敗しました: {e}")

    def destroy(self) -> None:
        if self.process:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass
        super().destroy()

        # ポート番号変更時にコマンド自動更新
        self.port.trace_add('write', lambda *a: self.update_cmd())
