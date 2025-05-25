import tkinter as tk
from tkinter import ttk
import os
from dotenv import load_dotenv


class LoggingConsoleFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_retention = os.getenv('LOG_RETENTION_DAYS', '14')
        self.var_log_level = tk.StringVar(value=log_level)
        self.var_log_retention = tk.StringVar(value=log_retention)
        ttk.Label(self, text="アプリケーションのログレベル:", style="Big.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(10, 0))
        self.combo_log_level = ttk.Combobox(self, values=[
                                            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly", width=12, textvariable=self.var_log_level)
        self.combo_log_level.grid(row=0, column=1, sticky=tk.W, pady=(10, 0))
        self.combo_log_level.configure(font=("Meiryo", 12))
        ttk.Label(self, text="ログファイルのローテーション保持日数:", style="Big.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.spin_retention = tk.Spinbox(
            self, from_=1, to=365, width=8, textvariable=self.var_log_retention, font=("Meiryo", 12))
        self.spin_retention.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        ttk.Button(self, text="保存", command=self.save_log_settings, style="Big.TButton").grid(
            row=2, column=1, sticky=tk.W, pady=(15, 0))

    def save_log_settings(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found_level = found_retention = False
        for line in lines:
            if line.startswith('LOG_LEVEL='):
                new_lines.append(f'LOG_LEVEL={self.var_log_level.get()}\n')
                found_level = True
            elif line.startswith('LOG_RETENTION_DAYS='):
                new_lines.append(
                    f'LOG_RETENTION_DAYS={self.var_log_retention.get()}\n')
                found_retention = True
            else:
                new_lines.append(line)
        if not found_level:
            new_lines.append(f'LOG_LEVEL={self.var_log_level.get()}\n')
        if not found_retention:
            new_lines.append(
                f'LOG_RETENTION_DAYS={self.var_log_retention.get()}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        load_dotenv(env_path, override=True)
