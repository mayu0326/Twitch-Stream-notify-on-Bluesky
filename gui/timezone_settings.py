import tkinter as tk
import tkinter.ttk as ttk
import os
from dotenv import load_dotenv


class TimeZoneSettings(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        timezone = os.getenv('TIMEZONE', 'system')
        self.var_timezone = tk.StringVar(value=timezone)
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True)
        ttk.Label(center_frame, text="タイムゾーン設定:", style="Big.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(10, 0))
        presets = ["system", "Asia/Tokyo", "UTC",
                   "America/New_York", "Europe/London"]
        self.combo_tz = ttk.Combobox(
            center_frame, values=presets, textvariable=self.var_timezone, width=24)
        self.combo_tz.grid(row=0, column=1, sticky=tk.W, pady=(10, 0))
        self.combo_tz.configure(font=("Meiryo", 12))
        ttk.Label(center_frame, text="任意のタイムゾーンを直接入力も可", style="Big.TLabel").grid(
            row=1, column=0, columnspan=2, sticky=tk.W)
        label1 = tk.Label(center_frame, text='"system" を指定すると、実行環境のシステムタイムゾーンを自動的に使用します。', font=(
            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
        label1.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        label2 = tk.Label(center_frame, text='無効な値や空の場合は\nシステムタイムゾーンまたはUTCにフォールバックします。', font=(
            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
        label2.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        ttk.Button(center_frame, text="保存", command=self.save_timezone, style="Big.TButton").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(15, 0), padx=40)

    def save_timezone(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith('TIMEZONE='):
                new_lines.append(f'TIMEZONE={self.var_timezone.get()}\n')
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f'TIMEZONE={self.var_timezone.get()}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        load_dotenv(env_path, override=True)
