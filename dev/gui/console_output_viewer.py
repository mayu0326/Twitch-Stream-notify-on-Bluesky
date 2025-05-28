import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk


class ConsoleOutputViewer(tk.Toplevel):
    def __init__(self, master=None, bot_manager=None):
        super().__init__(master)
        self.title("コンソール出力ビューア")
        self.geometry("800x400")
        self.bot_manager = bot_manager
        self.create_widgets()
        self.after(500, self.update_output)

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.txt_console = tk.Text(
            frame, height=24, width=100, bg="#222", fg="#eee", font=("Consolas", 11))
        self.txt_console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.txt_console.config(state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(
            frame, orient=tk.VERTICAL, command=self.txt_console.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_console.config(yscrollcommand=scrollbar.set)

    def update_output(self):
        if self.bot_manager:
            stdout = self.bot_manager.get_stdout()
            stderr = self.bot_manager.get_stderr()
            output = "[STDOUT]\n" + stdout + "\n[STDERR]\n" + stderr
            self.txt_console.config(state=tk.NORMAL)
            self.txt_console.delete(1.0, tk.END)
            self.txt_console.insert(tk.END, output)
            self.txt_console.config(state=tk.DISABLED)
            self.txt_console.see(tk.END)
        self.after(1000, self.update_output)
