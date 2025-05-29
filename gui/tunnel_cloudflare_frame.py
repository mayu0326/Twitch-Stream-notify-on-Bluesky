import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog


class TunnelCloudflareFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        # cloudflared.exeの初期値
        default_cloudflared = r"C:/Program Files (x86)/cloudflared/cloudflared.exe"
        cloudflared_dir = r"C:/Program Files (x86)/cloudflared"
        if not os.path.exists(cloudflared_dir):
            cloudflared_dir = "C:/"
        userprofile = os.environ.get('USERPROFILE', 'C:/Users')
        default_config_path = os.path.join(userprofile, '.cloudflared', 'config.yml')
        config_dir = os.path.join(userprofile, '.cloudflared')
        if not os.path.exists(config_dir):
            config_dir = userprofile
        self.cloudflared_path = tk.StringVar(value=default_cloudflared)
        self.config_path = tk.StringVar(value=default_config_path)
        self.generated_cmd = tk.StringVar()
        self._cloudflared_dir = cloudflared_dir
        self._config_dir = config_dir
        self.tunnel_name = tk.StringVar(value="my-tunnel")  # トンネル名の初期値
        self.load_tunnel_name()            # 追加: 設定ファイルからトンネル名を読み込む
        self.create_widgets()

    def load_tunnel_name(self):
        """settings.envからTUNNEL_NAMEを読み込んでself.tunnel_nameにセット"""
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        if not os.path.exists(env_path):
            return
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('TUNNEL_NAME='):
                    self.tunnel_name.set(line.strip().split('=', 1)[1])
                    break

    def create_widgets(self):
        # フレームの列設定 (中央寄せのため)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # cloudflared.exeの場所
        ttk.Label(
            self,
            text="cloudflared.exeの場所:",
            font=(
                "Meiryo",
                12,
                "bold")).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky=tk.W,
            pady=(
                20,
                5),
            padx=20)
        entry1 = ttk.Entry(self, textvariable=self.cloudflared_path, width=60, font=("Meiryo", 11))
        entry1.grid(row=1, column=0, padx=20, pady=(0, 10), columnspan=2, sticky="ew")
        ttk.Button(
            self,
            text="参照",
            command=self.select_cloudflared,
            style="Large.TButton").grid(
            row=1,
            column=2,
            padx=(
                0,
                20),
            pady=(
                0,
                10),
            ipadx=10,
            ipady=5)

        # config.ymlの場所
        ttk.Label(self, text="config.ymlの場所:", font=("Meiryo", 12, "bold")).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 5), padx=20)
        entry2 = ttk.Entry(self, textvariable=self.config_path, width=60, font=("Meiryo", 11))
        entry2.grid(row=3, column=0, padx=20, pady=(0, 10), columnspan=2, sticky="ew")
        ttk.Button(
            self,
            text="参照",
            command=self.select_config_file,
            style="Large.TButton").grid(
            row=3,
            column=2,
            padx=(
                0,
                20),
            pady=(
                0,
                10),
            ipadx=10,
            ipady=5)

        # トンネル名の設定
        ttk.Label(
            self,
            text="トンネル名:",
            font=(
                "Meiryo",
                12,
                "bold")).grid(
            row=4,
            column=0,
            columnspan=3,
            sticky=tk.W,
            pady=(
                10,
                5),
            padx=20)
        entry_tunnel_name = ttk.Entry(
            self,
            textvariable=self.tunnel_name,
            width=60,
            font=(
                "Meiryo",
                11))
        entry_tunnel_name.grid(
            row=5,
            column=0,
            padx=20,
            pady=(
                0,
                10),
            columnspan=3,
            sticky="ew")  # トンネル名は参照ボタンがないのでcolumnspan=3

        # 保存ボタンの位置を調整
        ttk.Button(
            self,
            text="保存",
            command=self.save_cmd,
            style="Large.TButton").grid(
            row=9,
            column=0,
            columnspan=3,
            pady=(
                20,
                20),
            ipadx=30,
            ipady=10)

        # スタイル設定 (ボタンを大きくするため)
        style = ttk.Style(self)
        style.configure("Large.TButton", font=("Meiryo", 11))

        self.update_cmd()

    def select_cloudflared(self):
        # cloudflared.exeのあるディレクトリを初期値に
        path = filedialog.askopenfilename(
            initialdir=self._cloudflared_dir,
            filetypes=[("実行ファイル", "*.exe"), ("すべてのファイル", "*.*")],
            title="cloudflared.exeを選択してください"
        )
        if path:
            self.cloudflared_path.set(path)
            self.update_cmd()

    def select_config_file(self):
        # config.ymlのあるディレクトリを初期値に
        path = filedialog.askopenfilename(
            initialdir=self._config_dir,
            filetypes=[("YAMLファイル", "*.yml;*.yaml"), ("すべてのファイル", "*.*")],
            title="config.ymlを選択してください"
        )
        if path:
            self.config_path.set(path)
            self.update_cmd()

    def update_cmd(self):
        exe = self.cloudflared_path.get()
        conf = self.config_path.get()
        tunnel = self.tunnel_name.get()
        if exe and conf and tunnel:
            cmd = f'cloudflared.exe tunnel --config {conf} run {tunnel}'
            self.generated_cmd.set(cmd)
        else:
            self.generated_cmd.set("")

    def save_cmd(self):
        self.update_cmd()  # 保存時に最新のコマンドを生成
        cmd = self.generated_cmd.get()
        tunnel = self.tunnel_name.get()
        if not cmd:
            tk.messagebox.showerror("エラー", "cloudflared.exe、config.yml、トンネル名を指定してください。")
            return
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found_cmd = found_name = False
        for line in lines:
            if line.startswith('TUNNEL_CMD='):
                new_lines.append(f'TUNNEL_CMD={cmd}\n')
                found_cmd = True
            elif line.startswith('TUNNEL_NAME='):
                new_lines.append(f'TUNNEL_NAME={tunnel}\n')
                found_name = True
            else:
                new_lines.append(line)
        if not found_cmd:
            new_lines.append(f'TUNNEL_CMD={cmd}\n')
        if not found_name:
            new_lines.append(f'TUNNEL_NAME={tunnel}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        tk.messagebox.showinfo("保存完了", "TUNNEL_CMD, TUNNEL_NAMEを保存しました。")
