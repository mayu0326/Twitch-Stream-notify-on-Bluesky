"""
ログファイル閲覧用サブウィンドウ
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os


class LogViewer(tk.Toplevel):
    def __init__(self, master=None, log_dir="logs"):
        super().__init__(master)
        self.title("ログビューア")
        self.geometry("600x400")
        self.log_dir = log_dir
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="ログファイルを選択:").pack(anchor=tk.W)
        self.cmb_file = ttk.Combobox(frame, values=self.get_log_files())
        self.cmb_file.pack(fill=tk.X, pady=5)
        ttk.Button(frame, text="開く", command=self.load_log).pack(anchor=tk.E)
        self.txt_log = tk.Text(self, height=20, width=80)
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def get_log_files(self):
        try:
            return [f for f in os.listdir(self.log_dir) if f.endswith(('.log', '.csv'))]
        except Exception:
            return []

    def load_log(self):
        filename = self.cmb_file.get()
        if not filename:
            messagebox.showwarning("ファイル未選択", "ログファイルを選択してください")
            return
        path = os.path.join(self.log_dir, filename)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.txt_log.delete(1.0, tk.END)
            self.txt_log.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルを開けません: {e}")
