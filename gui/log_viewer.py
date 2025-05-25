"""
ログファイル閲覧用サブウィンドウ
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re


class LogViewer(ttk.Frame):
    def __init__(self, master=None, log_dir="logs"):
        super().__init__(master)
        self.log_dir = log_dir
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="ログファイルを選択:").pack(anchor=tk.W)
        self.cmb_file = ttk.Combobox(frame, values=self.get_log_files())
        self.cmb_file.pack(fill=tk.X, pady=5)
        ttk.Button(frame, text="開く", command=self.load_log).pack(anchor=tk.E)

        # Enhanced log display with a scrollable Text widget
        log_frame = ttk.Frame(self)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.txt_log = tk.Text(log_frame, height=20,
                               wrap=tk.WORD, state=tk.DISABLED)
        self.txt_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.txt_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_log["yscrollcommand"] = scrollbar.set

    def get_log_files(self):
        try:
            return [f for f in os.listdir(self.log_dir) if f.endswith(('.log', '.csv'))]
        except Exception:
            return []

    def format_log_content(self, content):
        # Treat multiple consecutive dots as a single Japanese period (。)
        content = content.replace('...', '。')
        # Add line breaks after periods, colons, before brackets, and after ellipses
        formatted_content = content.replace('。', '。')
        formatted_content = formatted_content.replace(':', ':')
        formatted_content = formatted_content.replace('（', '\n（')
        formatted_content = formatted_content.replace('[', '\n[')
        return formatted_content

    def load_log(self):
        filename = self.cmb_file.get()
        if not filename:
            messagebox.showwarning("ファイル未選択", "ログファイルを選択してください")
            return
        path = os.path.join(self.log_dir, filename)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            formatted_content = self.format_log_content(content)
            self.txt_log.config(state=tk.NORMAL)
            self.txt_log.delete(1.0, tk.END)
            self.txt_log.insert(tk.END, formatted_content)
            self.txt_log.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルを開けません: {e}")
