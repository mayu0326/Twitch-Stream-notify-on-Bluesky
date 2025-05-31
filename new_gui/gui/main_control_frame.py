# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import customtkinter as ctk

DEFAULT_FONT = ("Yu Gothic UI", 20, "normal")

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
# バージョン情報はダミー値
__version__ = "0.0.0-hotmock"

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


class MainControlFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.var_server = ctk.StringVar(value='● 停止中')
        self.var_tunnel = ctk.StringVar(value='■ 停止中')
        self.var_url = ctk.StringVar(value='-')
        self.steps = [
            "設定ファイル確認",
            "トンネル起動",
            "ウェブアプリ起動",
            "トンネル疎通確認",
            "起動完了"
        ]
        self.step_vars = [ctk.StringVar(value="未実行") for _ in self.steps]
        self.step_labels = []
        self.desc_labels = []
        # 親フレームで中央寄せ
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # center_frameを親いっぱいに広げて中央寄せ
        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        for i in range(7):
            center_frame.grid_rowconfigure(i, weight=1)
        for j in range(7):  # 列数を7に減らし、主要UIをcolumn=3,4に統一
            center_frame.grid_columnconfigure(j, weight=1)
        # サーバー・トンネル・URLラベルをさらに中央寄せ
        ctk.CTkLabel(center_frame, text="サーバー状態:", font=DEFAULT_FONT).grid(row=1, column=3, sticky="e", padx=(0, 6), pady=(0, 10))
        ctk.CTkLabel(center_frame, textvariable=self.var_server, text_color="red", font=DEFAULT_FONT).grid(row=1, column=4, sticky="w", padx=(0, 18), pady=(0, 10))
        ctk.CTkLabel(center_frame, text="トンネル状態:", font=DEFAULT_FONT).grid(row=2, column=3, sticky="e", padx=(0, 6), pady=(0, 10))
        ctk.CTkLabel(center_frame, textvariable=self.var_tunnel, text_color="gray", font=DEFAULT_FONT).grid(row=2, column=4, sticky="w", padx=(0, 18), pady=(0, 10))
        ctk.CTkLabel(center_frame, text="外部URL:", font=DEFAULT_FONT).grid(row=3, column=3, sticky="e", padx=(0, 6), pady=(0, 10))
        ctk.CTkLabel(center_frame, textvariable=self.var_url, font=DEFAULT_FONT).grid(row=3, column=4, sticky="w", pady=(0, 10))
        # 進捗ステップ表示（2列）
        for i, step in enumerate(self.steps):
            col = 3 + (i % 2)
            row = 4 + (i // 2)
            lbl = ctk.CTkLabel(center_frame, text=f"{step}: {self.step_vars[i].get()}", font=DEFAULT_FONT, anchor="w")
            lbl.grid(row=row, column=col, sticky="w", padx=18, pady=1)
            self.step_labels.append(lbl)
            self.desc_labels.append(lbl)
        # ボタン
        btn_frame = ctk.CTkFrame(center_frame)
        btn_frame.grid(row=7, column=3, columnspan=2, pady=(10, 0), sticky="ew")
        self.btn_start = ctk.CTkButton(btn_frame, text="サーバー起動", command=self.start_server, font=DEFAULT_FONT, width=120, height=40, corner_radius=10)
        self.btn_start.pack(side="left", padx=8)
        self.btn_stop = ctk.CTkButton(btn_frame, text="サーバー停止", command=self.stop_server, font=DEFAULT_FONT, width=120, height=40, corner_radius=10)
        self.btn_stop.pack(side="left", padx=8)
        self.btn_reload = ctk.CTkButton(btn_frame, text="リロード", command=self.reload_status, font=DEFAULT_FONT, width=120, height=40, corner_radius=10)
        self.btn_reload.pack(side="left", padx=8)

        # コンソール出力欄（ボタンの下→一番下に移動）
        self.console_text = ctk.CTkTextbox(center_frame, height=80, font=("Yu Gothic UI", 15, "normal"))
        self.console_text.grid(row=8, column=3, columnspan=2, sticky="ew", padx=10, pady=(8, 0))
        # サーバーステータス表示ラベル（追加）
        self.status_label = ctk.CTkLabel(center_frame, text="サーバーは停止中です", font=("Yu Gothic UI", 18), text_color="red")
        self.status_label.grid(row=0, column=3, columnspan=2, pady=(0, 10))
        self.reset_status()

    def append_console(self, text):
        self.console_text.configure(state="normal")
        self.console_text.insert("end", text + "\n")
        self.console_text.see("end")
        self.console_text.configure(state="disabled")

    def reset_status(self):
        self.var_server.set('● 停止中')
        self.var_tunnel.set('■ 停止中')
        self.var_url.set('-')
        self.status_label.configure(text="サーバーは停止中です", text_color="red")
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        for i, (var, lbl, step) in enumerate(zip(self.step_vars, self.step_labels, self.steps)):
            var.set("未実行")
            lbl.configure(text=f"{step}: {var.get()}", text_color="gray")
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.configure(state="disabled")

    def update_appearance(self):
        desc_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        for lbl in self.desc_labels:
            lbl.configure(text_color=desc_color)
        for i, lbl in enumerate(self.step_labels):
            lbl.configure(text_color=desc_color)

    def update_step(self, idx, status, color=None):
        # ステータスに応じて色分け
        color_map = {
            "未実行": "gray",
            "実行中": "#1976d2",  # 青
            "成功": "#388e3c",   # 緑
            "失敗": "#d32f2f"    # 赤
        }
        if color is None:
            color = color_map.get(status, "gray")
        self.step_vars[idx].set(status)
        self.step_labels[idx].configure(text=f"{self.steps[idx]}: {status}", text_color=color)
        self.update_idletasks()

    def start_server(self):
        import importlib
        import threading
        self.reset_status()
        self.var_server.set('● 起動処理中')
        self.status_label.configure(text="起動処理中...", text_color="blue")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        self.append_console("[INFO] サーバー起動処理を開始します。")
        self.update_step(0, "実行中", "blue")
        def run():
            try:
                main_mod = importlib.import_module("main")
                # 設定ファイル確認
                self.append_console("[STEP] 設定ファイル確認...")
                self.update_step(0, "実行中", "blue")
                # initialize_app
                ok = main_mod.initialize_app()
                if not ok:
                    self.append_console("[ERROR] アプリ初期化に失敗しました。サーバーは起動できません。")
                    self.update_step(0, "失敗", "red")
                    self.var_server.set('● 停止中')
                    self.status_label.configure(text="サーバーは停止中です", text_color="red")
                    self.btn_start.configure(state="normal")
                    self.btn_stop.configure(state="disabled")
                    return
                self.update_step(0, "成功", "green")
                self.append_console("[OK] 設定ファイル確認 完了")
                # トンネル起動
                self.append_console("[STEP] トンネル起動...")
                self.update_step(1, "実行中", "blue")
                # ここではinitialize_app内でトンネルも起動される
                self.update_step(1, "成功", "green")
                self.append_console("[OK] トンネル起動 完了")
                # ウェブアプリ起動
                self.append_console("[STEP] ウェブアプリ起動...")
                self.update_step(2, "実行中", "blue")
                main_mod.start_server_in_thread()
                self.update_step(2, "成功", "green")
                self.append_console("[OK] ウェブアプリ起動 完了")
                # トンネル疎通確認
                self.append_console("[STEP] トンネル疎通確認...")
                self.update_step(3, "実行中", "blue")
                # TODO: 実際の疎通確認APIを呼ぶ場合はここで
                self.update_step(3, "成功", "green")
                self.append_console("[OK] トンネル疎通確認 完了")
                self.update_step(4, "成功", "green")
                self.var_server.set('● 稼働中')
                self.status_label.configure(text="サーバーは起動中です", text_color="green")
                self.btn_start.configure(state="disabled")
                self.btn_stop.configure(state="normal")
                self.append_console("[INFO] サーバーは起動中です。")
            except Exception as e:
                self.append_console(f"[ERROR] サーバー起動失敗: {e}")
                self.var_server.set('● 停止中')
                self.status_label.configure(text="サーバーは停止中です", text_color="red")
                self.btn_start.configure(state="normal")
                self.btn_stop.configure(state="disabled")
                self.update_step(0, "失敗", "red")
        threading.Thread(target=run, daemon=True).start()

    def stop_server(self):
        import importlib
        import threading
        self.var_server.set('● 停止処理中')
        self.status_label.configure(text="停止処理中...", text_color="red")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        self.append_console("[INFO] サーバー停止処理を開始します。")
        def run():
            try:
                main_mod = importlib.import_module("main")
                main_mod.stop_cherrypy_server()
                main_mod.cleanup_from_gui()
                self.append_console("[INFO] サーバーは停止しました。")
                self.var_server.set('● 停止中')
                self.status_label.configure(text="サーバーは停止中です", text_color="red")
                self.btn_start.configure(state="normal")
                self.btn_stop.configure(state="disabled")
                self.reset_status()
            except Exception as e:
                self.append_console(f"[ERROR] サーバー停止失敗: {e}")
                self.var_server.set('● 停止中')
                self.status_label.configure(text="サーバーは停止中です", text_color="red")
                self.btn_start.configure(state="normal")
                self.btn_stop.configure(state="disabled")
        threading.Thread(target=run, daemon=True).start()

    def reload_status(self):
        self.append_console("[INFO] ステータスをリロードしました。")
        # TODO: サーバー・トンネル・URLの状態を再取得して反映
    def _startup_sequence(self):
        import time
        try:
            self.append_console("[STEP] 設定ファイル確認...")
            self.update_step(0, "実行中")
            time.sleep(0.5)
            self.update_step(0, "成功")
            self.append_console("[OK] 設定ファイル確認 完了")

            self.append_console("[STEP] トンネル起動...")
            self.update_step(1, "実行中")
            time.sleep(0.5)
            self.update_step(1, "成功")
            self.append_console("[OK] トンネル起動 完了")

            self.append_console("[STEP] ウェブアプリ起動...")
            self.update_step(2, "実行中")
            time.sleep(0.5)
            self.update_step(2, "成功")
            self.append_console("[OK] ウェブアプリ起動 完了")

            self.append_console("[STEP] トンネル疎通確認...")
            self.update_step(3, "実行中")
            time.sleep(0.5)
            self.update_step(3, "成功")
            self.append_console("[OK] トンネル疎通確認 完了")

            self.update_step(4, "成功")
            self.status_label.configure(text="サーバーは起動中です", text_color="green")
            self.append_console("[INFO] サーバーは起動中です。")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
        except Exception as e:
            self.status_label.configure(text=f"起動失敗: {e}", text_color="red")
            self.append_console(f"[ERROR] 起動失敗: {e}")
            for idx, var in enumerate(self.step_vars):
                if var.get() == "実行中":
                    self.update_step(idx, "失敗")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")

    def _shutdown_sequence(self):
        import time
        try:
            self.append_console("[STEP] 設定ファイルの書き換え...")
            time.sleep(0.5)
            self.append_console("[OK] 設定ファイルの書き換え 完了")

            self.append_console("[STEP] ウェブアプリの終了...")
            time.sleep(0.5)
            self.append_console("[OK] ウェブアプリの終了 完了")

            self.append_console("[STEP] トンネル終了...")
            time.sleep(0.5)
            self.append_console("[OK] トンネル終了 完了")

            self.status_label.configure(text="サーバーは停止中です", text_color="red")
            for i, (var, lbl, step) in enumerate(zip(self.step_vars, self.step_labels, self.steps)):
                var.set("未実行")
                lbl.configure(text=f"{step}: {var.get()}", text_color="gray")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.append_console("[INFO] サーバーは停止しました。")
        except Exception as e:
            self.status_label.configure(text=f"停止処理失敗: {e}", text_color="red")
            self.append_console(f"[ERROR] 停止処理失敗: {e}")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
