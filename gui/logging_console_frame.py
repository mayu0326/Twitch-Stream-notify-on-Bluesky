
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
import tkinter as tk
from tkinter import ttk
import os
from tkinter import messagebox  # 追加
import customtkinter as ctk

DEFAULT_FONT = "Yu Gothic UI", 15, "normal"

class LoggingConsoleFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.var_log_level = ctk.StringVar()
        self.var_log_retention = ctk.StringVar()
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")
        ctk.CTkLabel(center_frame, text="アプリケーションのログレベル:", font=DEFAULT_FONT).pack(fill="x", padx=40, pady=(30, 5), expand=True)
        ctk.CTkComboBox(
            center_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            variable=self.var_log_level,
            font=DEFAULT_FONT,
            width=320,
            state="readonly",
            justify="center"
        ).pack(fill="x", padx=80, pady=5, expand=True)
        ctk.CTkLabel(center_frame, text="ログファイルのローテーション保持日数:", font=DEFAULT_FONT).pack(fill="x", pady=(20, 5), padx=40, expand=True)
        # --- ここからバリデーション追加 ---
        vcmd = (self.register(self.validate_retention), '%P')
        ctk.CTkEntry(
            center_frame,
            textvariable=self.var_log_retention,
            font=DEFAULT_FONT,
            width=320,
            justify="center",
            validate="key",
            validatecommand=vcmd
        ).pack(fill="x", padx=80, pady=5, expand=True)
        # --- ここまで ---
        ctk.CTkButton(
            center_frame,
            text="保存",
            command=self.save_log_settings,
            font=DEFAULT_FONT,
            width=120,
        ).pack(pady=(30, 0), fill="x", padx=200, expand=True)
        self.load_settings()

    def validate_retention(self, value):
        # 空欄は許可（初期化時や削除時）
        if value == "":
            return True
        # 数字のみ、最大3桁
        return value.isdigit() and len(value) <= 3

    def load_settings(self):
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        log_level = "INFO"
        log_retention = "14"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("LOG_LEVEL="):
                        log_level = line.strip().split("=", 1)[1]
                    elif line.startswith("LOG_RETENTION_DAYS="):
                        log_retention = line.strip().split("=", 1)[1]
        self.var_log_level.set(log_level)
        self.var_log_retention.set(log_retention)

    def save_log_settings(self):
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        log_level = self.var_log_level.get().strip()
        log_retention = self.var_log_retention.get().strip()
        lines = []
        found_level = found_retention = False
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("LOG_LEVEL="):
                        lines.append(f"LOG_LEVEL={log_level}\n")
                        found_level = True
                    elif line.startswith("LOG_RETENTION_DAYS="):
                        lines.append(f"LOG_RETENTION_DAYS={log_retention}\n")
                        found_retention = True
                    else:
                        lines.append(line)
        if not found_level:
            lines.append(f"LOG_LEVEL={log_level}\n")
        if not found_retention:
            lines.append(f"LOG_RETENTION_DAYS={log_retention}\n")
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        self.var_log_level.set(log_level)
        self.var_log_retention.set(log_retention)
        messagebox.showinfo("保存", "保存しました")
