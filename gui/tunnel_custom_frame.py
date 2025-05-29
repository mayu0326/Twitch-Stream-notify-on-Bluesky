import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
import tkinter.ttk as ttk
from dotenv import load_dotenv


class TunnelCustomFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        # カスタム設定ラベル
        ttk.Label(self, text="カスタム設定", font=("Meiryo", 12, "bold")).pack(pady=(10, 0))

        # 説明文ラベル（selfにpackで直後に配置）
        tk.Label(
            self,
            text='本設定GUI対応外のトンネルを使用する場合などは、\n下記のトンネル起動コマンド欄に入力して設定してください。\nなお、カスタムコマンドの実行は動作保証およびサポートの\n対象外であり、対応追加のご要望にもお答えできませんので\nあらかじめご了承ください。',
            font=(
                "Meiryo",
                11,
                "bold"),
            anchor="w",
            justify="left",
            wraplength=420).pack(
            fill="x",
            padx=10,
            pady=(
                5,
                10),
            anchor="w")

        # .envファイルの読み込み
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        tunnel_cmd = os.getenv('CUSTOM_TUNNEL_CMD', '')
        self.custom_tunnel_cmd = tk.StringVar(value=tunnel_cmd)

        # 入力欄などをまとめるフレーム
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=1)

        # トンネル起動コマンド入力欄
        ttk.Label(center_frame, text="トンネル起動コマンド:", font=("Meiryo", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        entry = ttk.Entry(
            center_frame, textvariable=self.custom_tunnel_cmd, width=48, font=("Meiryo", 12)
        )
        entry.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # 保存ボタン（下部中央・大きめに統一）
        ttk.Button(
            center_frame,
            text="保存",
            command=self.save_tunnel_cmd,
            style="Large.TButton"
        ).grid(row=10, column=0, columnspan=2, pady=(30, 20), padx=80, ipadx=30, ipady=10, sticky="ew")
        style = ttk.Style(self)
        style.configure("Large.TButton", font=("Meiryo", 11))

    def save_tunnel_cmd(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith('CUSTOM_TUNNEL_CMD='):
                new_lines.append(f'CUSTOM_TUNNEL_CMD={self.custom_tunnel_cmd.get()}\n')
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f'CUSTOM_TUNNEL_CMD={self.custom_tunnel_cmd.get()}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        tk.messagebox.showinfo("保存完了", "CUSTOM_TUNNEL_CMDを保存しました。")
