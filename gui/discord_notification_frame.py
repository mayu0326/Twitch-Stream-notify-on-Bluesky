import tkinter as tk
from tkinter import ttk
import os
from dotenv import load_dotenv


class DiscordNotificationFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        discord_url = os.getenv('discord_error_notifier_url', '')
        discord_level = os.getenv('discord_notify_level', 'CRITICAL')
        discord_enabled = os.getenv(
            'DISCORD_NOTIFY_ENABLED', 'True').lower() == 'true'
        self.var_discord_enabled = tk.BooleanVar(value=discord_enabled)
        ttk.Checkbutton(self, text="Discord通知を有効化", variable=self.var_discord_enabled, style="Big.TCheckbutton").grid(
            row=0, column=0, sticky=tk.W, columnspan=2)
        ttk.Label(self, text="Discord通知レベル:", style="Big.TLabel").grid(
            row=1, column=0, sticky=tk.W)
        self.combo_discord_level = ttk.Combobox(self, values=[
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly", width=12)
        self.combo_discord_level.set(discord_level)
        self.combo_discord_level.grid(row=1, column=1, sticky=tk.W)
        self.combo_discord_level.configure(font=("Meiryo", 12))
        ttk.Label(self, text="Discord Webhook URL:", style="Big.TLabel").grid(
            row=2, column=0, sticky=tk.W, columnspan=2)
        self.entry_discord_url = ttk.Entry(self, width=70)
        self.entry_discord_url.insert(0, discord_url)
        self.entry_discord_url.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self.entry_discord_url.configure(font=("Meiryo", 12))
        ttk.Button(self, text="設定を反映", command=self.save_discord_settings, style="Big.TButton").grid(
            row=4, column=1, sticky=tk.W, pady=(5, 0))
        ttk.Button(self, text="設定を消去", command=self.clear_discord_settings, style="Big.TButton").grid(
            row=4, column=0, sticky=tk.W, pady=(5, 0))

    def save_discord_settings(self):
        url = self.entry_discord_url.get().strip()
        level = self.combo_discord_level.get().strip()
        enabled = self.var_discord_enabled.get()
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found_url = found_level = found_enabled = False
        for line in lines:
            if line.startswith('discord_error_notifier_url='):
                new_lines.append(f'discord_error_notifier_url={url}\n')
                found_url = True
            elif line.startswith('discord_notify_level='):
                new_lines.append(f'discord_notify_level={level}\n')
                found_level = True
            elif line.startswith('DISCORD_NOTIFY_ENABLED='):
                new_lines.append(f'DISCORD_NOTIFY_ENABLED={str(enabled)}\n')
                found_enabled = True
            else:
                new_lines.append(line)
        if not found_url:
            new_lines.append(f'discord_error_notifier_url={url}\n')
        if not found_level:
            new_lines.append(f'discord_notify_level={level}\n')
        if not found_enabled:
            new_lines.append(f'DISCORD_NOTIFY_ENABLED={str(enabled)}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        load_dotenv(env_path, override=True)
        self.entry_discord_url.delete(0, tk.END)
        self.entry_discord_url.insert(0, url)
        self.combo_discord_level.set(level)
        self.var_discord_enabled.set(enabled)

    def clear_discord_settings(self):
        self.entry_discord_url.delete(0, tk.END)
        self.combo_discord_level.set('CRITICAL')
        self.var_discord_enabled.set(False)
        self.save_discord_settings()
