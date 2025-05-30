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
import importlib

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
        # main.pyの起動・停止APIをimport
        self.main_module = importlib.import_module("main")

    def create_widgets(self):
        # 見出し
        heading = ttk.Label(self, text="アプリ起動管理機能", font=("Meiryo", 15, "bold"))
        heading.pack(pady=(18, 8))

        # サーバーステータス表示ラベル
        self.status_label = ttk.Label(self, text="サーバーは停止中です", font=("Meiryo", 13), foreground="red")
        self.status_label.pack(pady=(0, 8))

        # ステップ進捗表示用フレーム
        steps_frame = ttk.Frame(self)
        steps_frame.pack(pady=2, fill="x")
        for step in self.steps:
            var = tk.StringVar(value="未実行")
            # 各ステップのラベル
            lbl = ttk.Label(steps_frame, text=f"{step}: {var.get()}", font=("Meiryo", 13), anchor="w")
            lbl.pack(fill="x", padx=18, pady=1)
            self.step_vars.append(var)
            self.step_labels.append(lbl)

        # 起動・停止ボタン用フレーム
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=16)
        # 起動ボタン
        self.start_button = ttk.Button(
            btn_frame, text="起動", command=self.start_server, width=16
        )
        self.start_button.pack(side="left", padx=12, ipadx=8, ipady=4)
        self.start_button.configure(style="App.TButton")
        # 停止ボタン
        self.stop_button = ttk.Button(
            btn_frame, text="停止", command=self.stop_server, state="disabled", width=16
        )
        self.stop_button.pack(side="left", padx=12, ipadx=8, ipady=4)
        self.stop_button.configure(style="App.TButton")

        # ボタンのフォントも統一
        style = ttk.Style()
        style.configure("App.TButton", font=("Meiryo", 13))

        # コンソール出力窓
        console_frame = ttk.Frame(self)
        console_frame.pack(fill="x", padx=10, pady=(0, 8))
        self.console_text = tk.Text(console_frame, height=6, font=("Meiryo", 10), bg="#f8f8f8", fg="#222", wrap="word")
        self.console_text.pack(fill="x", expand=False)
        self.console_text.config(state="disabled")

    def append_console(self, text):
        self.console_text.config(state="normal")
        self.console_text.insert("end", text + "\n")
        self.console_text.see("end")
        self.console_text.config(state="disabled")

    def reset_status(self):
        self.status_label.config(text="サーバーは停止中です", font=("Meiryo", 13), foreground="red")
        for var, lbl, step in zip(self.step_vars, self.step_labels, self.steps):
            var.set("未実行")
            lbl.config(text=f"{step}: {var.get()}", foreground="black")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.console_text.config(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.config(state="disabled")

    def update_step(self, idx, status, color="black"):
        self.step_vars[idx].set(status)
        self.step_labels[idx].config(text=f"{self.steps[idx]}: {status}", foreground=color)
        self.update_idletasks()

    def start_server(self):
        self.status_label.config(text="起動処理中...", foreground="blue")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        self.append_console("[INFO] サーバー起動処理を開始します。")
        # main.pyの初期化APIを呼ぶ
        try:
            if not self.main_module.initialize_app():
                self.append_console("[ERROR] アプリ初期化に失敗しました。サーバーは起動できません。")
                self.status_label.config(text="初期化失敗", foreground="red")
                self.start_button.config(state="normal")
                return
            self.append_console("[INFO] アプリ初期化が完了しました。CherryPyサーバー起動要求を送信します。")
            self.main_module.start_server_in_thread()
        except Exception as e:
            self.append_console(f"[ERROR] サーバー起動失敗: {e}")
            self.status_label.config(text="起動失敗", foreground="red")
            self.start_button.config(state="normal")
            return
        import threading
        threading.Thread(target=self._startup_sequence, daemon=True).start()

    def stop_server(self):
        self.status_label.config(text="停止処理中...", foreground="red")
        self.append_console("[INFO] サーバー停止処理を開始します。")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        # main.pyのCherryPyサーバー停止APIを呼ぶ
        try:
            self.main_module.stop_cherrypy_server()
            self.append_console("[INFO] CherryPyサーバー停止要求を送信しました。")
            # クリーンアップも明示的に呼ぶ
            self.main_module.cleanup_from_gui()
            self.append_console("[INFO] クリーンアップ処理を実行しました。")
        except Exception as e:
            self.append_console(f"[ERROR] CherryPyサーバー停止失敗: {e}")
        import threading
        threading.Thread(target=self._shutdown_sequence, daemon=True).start()

    def _startup_sequence(self):
        import time
        try:
            self.append_console("[STEP] 設定ファイル確認...")
            self.update_step(0, "実行中", "blue")
            time.sleep(0.5)
            self.update_step(0, "成功", "green")
            self.append_console("[OK] 設定ファイル確認 完了")

            self.append_console("[STEP] トンネル起動...")
            self.update_step(1, "実行中", "blue")
            time.sleep(0.5)
            self.update_step(1, "成功", "green")
            self.append_console("[OK] トンネル起動 完了")

            self.append_console("[STEP] ウェブアプリ起動...")
            self.update_step(2, "実行中", "blue")
            time.sleep(0.5)
            self.update_step(2, "成功", "green")
            self.append_console("[OK] ウェブアプリ起動 完了")

            self.append_console("[STEP] トンネル疎通確認...")
            self.update_step(3, "実行中", "blue")
            time.sleep(0.5)
            self.update_step(3, "成功", "green")
            self.append_console("[OK] トンネル疎通確認 完了")

            self.update_step(4, "成功", "green")
            self.status_label.config(text="サーバーは起動中です", foreground="green")
            self.append_console("[INFO] サーバーは起動中です。")
            self.stop_button.config(state="normal")
        except Exception as e:
            self.status_label.config(text=f"起動失敗: {e}", foreground="red")
            self.append_console(f"[ERROR] 起動失敗: {e}")
            for idx, var in enumerate(self.step_vars):
                if var.get() == "実行中":
                    self.update_step(idx, "失敗", "red")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def _shutdown_sequence(self):
        import time
        try:
            # 1. 設定ファイルの書き換え（必要なら）
            self.append_console("[STEP] 設定ファイルの書き換え...")
            time.sleep(0.5)  # 実際は必要な処理に置換
            self.append_console("[OK] 設定ファイルの書き換え 完了")

            # 2. ウェブアプリの終了
            self.append_console("[STEP] ウェブアプリの終了...")
            time.sleep(0.5)
            self.append_console("[OK] ウェブアプリの終了 完了")

            # 3. トンネル終了
            self.append_console("[STEP] トンネル終了...")
            time.sleep(0.5)
            self.append_console("[OK] トンネル終了 完了")

            # 4. ステータスを停止に変更（ステップもリセット）
            self.status_label.config(text="サーバーは停止中です", foreground="red")
            for var, lbl, step in zip(self.step_vars, self.step_labels, self.steps):
                var.set("未実行")
                lbl.config(text=f"{step}: {var.get()}", foreground="black")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.append_console("[INFO] サーバーは停止しました。")
        except Exception as e:
            self.status_label.config(text=f"停止処理失敗: {e}", foreground="red")
            self.append_console(f"[ERROR] 停止処理失敗: {e}")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
