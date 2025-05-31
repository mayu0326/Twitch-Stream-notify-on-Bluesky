# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

# Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# このプログラムはフリーソフトウェアです。フリーソフトウェア財団によって発行された
# GNU 一般公衆利用許諾契約書（バージョン2またはそれ以降）に基づき、再配布または
# 改変することができます。
#
# このプログラムは有用であることを願って配布されていますが、
# 商品性や特定目的への適合性についての保証はありません。
# 詳細はGNU一般公衆利用許諾契約書をご覧ください。
#
# このプログラムとともにGNU一般公衆利用許諾契約書が配布されているはずです。
# もし同梱されていない場合は、フリーソフトウェア財団までご請求ください。
# 住所: 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__


from version_info import __version__
import customtkinter as ctk
import os
import webbrowser
from tkinter import messagebox  # 追加

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")


class DiscordNotificationFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.var_enabled = ctk.BooleanVar()
        self.var_level = ctk.StringVar()
        self.var_webhook = ctk.StringVar()
        self.status_label = None
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")
        ctk.CTkLabel(center_frame, text="Discord通知設定", font=DEFAULT_FONT).pack(fill="x", pady=(30, 10), padx=40, expand=True)
        ctk.CTkSwitch(center_frame, text="Discord通知を有効化", variable=self.var_enabled, font=DEFAULT_FONT, onvalue=True, offvalue=False).pack(fill="x", padx=80, pady=5, expand=True)
        ctk.CTkLabel(center_frame, text="通知レベル:", font=DEFAULT_FONT).pack(fill="x", padx=40, pady=(20, 5), expand=True)
        ctk.CTkComboBox(
            center_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            variable=self.var_level,
            font=DEFAULT_FONT,
            width=320,
            state="readonly",
            justify="center"
        ).pack(fill="x", padx=80, pady=5, expand=True)
        ctk.CTkLabel(center_frame, text="Webhook URL:", font=DEFAULT_FONT).pack(fill="x", padx=40, pady=(20, 5), expand=True)
        ctk.CTkEntry(center_frame, width=320, font=DEFAULT_FONT, textvariable=self.var_webhook, justify="center").pack(fill="x", padx=80, pady=5, expand=True)
        btn_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="保存", command=self.save_settings, font=DEFAULT_FONT, width=120).pack(side="left", padx=10, expand=True)
        ctk.CTkButton(btn_frame, text="設定消去", command=self.clear_settings, font=DEFAULT_FONT, width=120).pack(side="left", padx=10, expand=True)
        self.status_label = ctk.CTkLabel(center_frame, text="", font=DEFAULT_FONT)
        self.status_label.pack(pady=10, fill="x", expand=True)
        self.load_settings()

    def load_settings(self):
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        enabled = False
        level = "CRITICAL"
        webhook = ""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('DISCORD_NOTIFY_ENABLED='):
                        enabled = line.strip().split('=', 1)[1].lower() == 'true'
                    elif line.startswith('discord_notify_level='):
                        level = line.strip().split('=', 1)[1]
                    elif line.startswith('discord_error_notifier_url='):
                        webhook = line.strip().split('=', 1)[1]
        self.var_enabled.set(enabled)
        self.var_level.set(level)
        self.var_webhook.set(webhook)

    def save_settings(self, show_message=True):
        enabled = self.var_enabled.get()
        level = self.var_level.get().strip()
        webhook = self.var_webhook.get().strip()
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        lines = []
        found_enabled = found_level = found_webhook = False
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('DISCORD_NOTIFY_ENABLED='):
                        lines.append(f'DISCORD_NOTIFY_ENABLED={str(enabled)}\n')
                        found_enabled = True
                    elif line.startswith('discord_notify_level='):
                        lines.append(f'discord_notify_level={level}\n')
                        found_level = True
                    elif line.startswith('discord_error_notifier_url='):
                        lines.append(f'discord_error_notifier_url={webhook}\n')
                        found_webhook = True
                    else:
                        lines.append(line)
        if not found_enabled:
            lines.append(f'DISCORD_NOTIFY_ENABLED={str(enabled)}\n')
        if not found_level:
            lines.append(f'discord_notify_level={level}\n')
        if not found_webhook:
            lines.append(f'discord_error_notifier_url={webhook}\n')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        # UI値を再セット
        self.var_enabled.set(enabled)
        self.var_level.set(level)
        self.var_webhook.set(webhook)
        self.status_label.configure(text="保存しました")
        if show_message:
            messagebox.showinfo("保存完了", "Discord通知設定を保存しました。")

    def clear_settings(self):
        self.var_enabled.set(False)
        self.var_level.set("CRITICAL")
        self.var_webhook.set("")
        self.save_settings(show_message=False)
        self.status_label.configure(text="初期化しました")
        messagebox.showinfo("初期化完了", "Discord通知設定を初期化しました。")
