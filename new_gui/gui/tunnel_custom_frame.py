import sys
import os
import customtkinter as ctk
import tkinter.messagebox as messagebox

try:
    import pyperclip
    _pyperclip_available = True
except ImportError:
    _pyperclip_available = False

class TunnelCustomFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.font = ("Yu Gothic UI", 15, "normal")
        self.cmd_var = ctk.StringVar(value=self._load_cmd())
        # --- 中央寄せ用サブフレーム ---
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")
        self._create_widgets(center_frame)

    def _load_cmd(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        if not os.path.exists(env_path):
            return ''
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('CUSTOM_TUNNEL_CMD='):
                    return line.strip().split('=', 1)[1]
        return ''

    def _create_widgets(self, parent):
        ctk.CTkLabel(parent, text="カスタム設定", font=self.font, anchor="w").grid(row=0, column=0, columnspan=3, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkLabel(parent, text='本設定GUI対応外のトンネルを使用する場合などは、下記のトンネル起動コマンド欄に入力して設定してください。\nなお、カスタムコマンドの実行は動作保証およびサポートの対象外であり、対応追加のご要望にもお答えできません。\nあらかじめご了承ください。', font=("Yu Gothic UI", 14, "normal"), anchor="w", justify="left").grid(row=1, column=0, columnspan=3, sticky='w', padx=(10,0), pady=(5,10))
        ctk.CTkLabel(parent, text="トンネル起動コマンド:", font=self.font, anchor="w").grid(row=2, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.cmd_var, font=self.font, width=320).grid(row=2, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="コマンドコピー", command=self._copy_cmd, font=self.font).grid(row=2, column=2, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="保存", command=self._save_cmd, font=self.font).grid(row=3, column=1, pady=(20,0))

    def _save_cmd(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        cmd = self.cmd_var.get()
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith('CUSTOM_TUNNEL_CMD='):
                new_lines.append(f'CUSTOM_TUNNEL_CMD={cmd}\n')
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f'CUSTOM_TUNNEL_CMD={cmd}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        messagebox.showinfo("保存完了", "CUSTOM_TUNNEL_CMDを保存しました。\n\n※コマンドの実行・監視はサポート対象外です。")

    def _copy_cmd(self):
        cmd = self.cmd_var.get()
        if not cmd:
            messagebox.showwarning("コマンド未入力", "コマンドが空です。")
            return
        if _pyperclip_available:
            pyperclip.copy(cmd)
            messagebox.showinfo("コピー完了", "コマンドをクリップボードにコピーしました。")
        else:
            messagebox.showwarning("pyperclip未インストール", "pyperclipが未インストールのためコピーできません。\n\n'pip install pyperclip'でインストールしてください。")
