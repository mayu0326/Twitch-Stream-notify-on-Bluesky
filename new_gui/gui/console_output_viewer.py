import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import customtkinter as ctk


class ConsoleOutputViewer(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("コンソール出力ビューア（ダミー）")
        self.geometry("600x400")
        # ダミー出力
        dummy_output = """[INFO] サーバー起動\n[INFO] トンネル接続\n[ERROR] 何らかのエラー\n..."""
        # UI部品のみ配置
        ctk.CTkLabel(self, text="コンソール出力:").pack(pady=10)
        textbox = ctk.CTkTextbox(self, width=550, height=300)
        textbox.pack(padx=10, pady=10)
        textbox.insert("0.0", dummy_output)
        textbox.configure(state="disabled")
        ctk.CTkButton(self, text="閉じる", command=self.destroy).pack(pady=10)
