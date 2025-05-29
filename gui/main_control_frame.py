# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from version_info import __version__
from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

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

"""
メインウィンドウのボット制御・ステータス表示部
"""


class MainControlFrame(ttk.Frame):
    def __init__(self, master=None, bot_manager=None):
        super().__init__(master)
        self.bot_manager = bot_manager
        self.steps = [
            "設定ファイル確認",
            "トンネル起動",
            "ウェブアプリ起動",
            "トンネル疎通確認",
            "起動完了"
        ]
        self.step_vars = []
        self.step_labels = []
        self.create_widgets()
        self.reset_status()

    def create_widgets(self):
        self.status_label = ttk.Label(self, text="サーバーは停止中です", foreground="gray")
        self.status_label.pack(pady=5)

        steps_frame = ttk.Frame(self)
        steps_frame.pack(pady=5, fill="x")
        for step in self.steps:
            var = tk.StringVar(value="未実行")
            lbl = ttk.Label(steps_frame, text=f"{step}: {var.get()}", anchor="w")
            lbl.pack(fill="x", padx=10, pady=1)
            self.step_vars.append(var)
            self.step_labels.append(lbl)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        self.start_button = ttk.Button(btn_frame, text="起動", command=self.start_server)
        self.start_button.pack(side="left", padx=10)
        self.stop_button = ttk.Button(btn_frame, text="停止", command=self.stop_server, state="disabled")
        self.stop_button.pack(side="left", padx=10)

    def reset_status(self):
        self.status_label.config(text="サーバーは停止中です", foreground="gray")
        for var, lbl, step in zip(self.step_vars, self.step_labels, self.steps):
            var.set("未実行")
            lbl.config(text=f"{step}: {var.get()}", foreground="black")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def update_step(self, idx, status, color="black"):
        self.step_vars[idx].set(status)
        self.step_labels[idx].config(text=f"{self.steps[idx]}: {status}", foreground=color)
        self.update_idletasks()

    def start_server(self):
        self.status_label.config(text="起動処理中...", foreground="blue")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        import threading
        threading.Thread(target=self._startup_sequence, daemon=True).start()

    def stop_server(self):
        self.status_label.config(text="停止処理中...", foreground="red")
        # 実際の停止処理はここで実装（今はダミー）
        import time
        time.sleep(0.5)
        self.reset_status()

    def _startup_sequence(self):
        import time
        try:
            # 1. 設定ファイル確認
            self.update_step(0, "実行中", "blue")
            time.sleep(0.5)  # 実際は設定ファイルの存在・内容チェック
            self.update_step(0, "成功", "green")

            # 2. トンネル起動
            self.update_step(1, "実行中", "blue")
            time.sleep(0.5)  # 実際はstart_tunnel()呼び出し
            self.update_step(1, "成功", "green")

            # 3. ウェブアプリ起動
            self.update_step(2, "実行中", "blue")
            time.sleep(0.5)  # 実際はFlask/Waitress起動
            self.update_step(2, "成功", "green")

            # 4. トンネル疎通確認
            self.update_step(3, "実行中", "blue")
            time.sleep(0.5)  # 実際はHTTP GETで疎通確認
            self.update_step(3, "成功", "green")

            # 5. 起動完了
            self.update_step(4, "成功", "green")
            self.status_label.config(text="サーバーは起動中です", foreground="green")
            self.stop_button.config(state="normal")
        except Exception as e:
            self.status_label.config(text=f"起動失敗: {e}", foreground="red")
            for idx, var in enumerate(self.step_vars):
                if var.get() == "実行中":
                    self.update_step(idx, "失敗", "red")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
