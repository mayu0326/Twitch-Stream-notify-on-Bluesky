
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

"""
ログファイル閲覧用サブウィンドウ（本番実装）
"""
from version_info import __version__
import customtkinter as ctk
import os
from tkinter import messagebox

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
LOG_FILES = [
    ("アプリケーションログ (app.log)", "../../logs/app.log"),
    ("監査ログ (audit.log)", "../../logs/audit.log"),
    ("エラーログ (error.log)", "../../logs/error.log"),
    ("Bluesky投稿履歴 (post_history.csv)", "../../logs/post_history.csv"),
]


class LogViewer(ctk.CTkFrame):
    def __init__(self, master=None, width=700, height=500):
        try:
            super().__init__(master, width=width, height=height)
            ctk.CTkLabel(self, text="ログファイル選択:", font=DEFAULT_FONT).pack(pady=(10, 0))
            self.file_var = ctk.StringVar(value=LOG_FILES[0][1])
            self.file_combo = ctk.CTkComboBox(
                self,
                values=[f[0] for f in LOG_FILES],
                font=DEFAULT_FONT,
                dropdown_font=DEFAULT_FONT,
                command=self.on_file_change,
                state="readonly",
                width=340
            )
            self.file_combo.pack(pady=(0, 5))
            self.file_combo.set(LOG_FILES[0][0])
            self.textbox = ctk.CTkTextbox(self, width=650, height=350, font=DEFAULT_FONT)
            self.textbox.pack(padx=10, pady=10)
            btn_frame = ctk.CTkFrame(self)
            btn_frame.pack(pady=5)
            ctk.CTkButton(btn_frame, text="再読込", command=lambda: self.load_log(True), font=DEFAULT_FONT).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="クリア", command=self.clear_log, font=DEFAULT_FONT).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="保存先を開く", command=self.open_log_dir, font=DEFAULT_FONT).pack(side="left", padx=5)
            self.load_log()
        except Exception as e:
            messagebox.showerror("LogViewer初期化エラー", str(e))

    def get_selected_log_path(self):
        idx = self.file_combo.cget("values").index(self.file_combo.get())
        return os.path.abspath(os.path.join(os.path.dirname(__file__), LOG_FILES[idx][1]))

    def load_log(self, show_message=False):
        try:
            log_path = self.get_selected_log_path()
            self.textbox.configure(state="normal")
            self.textbox.delete("1.0", "end")
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    self.textbox.configure(font=DEFAULT_FONT)
                    self.textbox.insert("end", f.read())
            else:
                self.textbox.configure(font=DEFAULT_FONT)
                self.textbox.insert("end", "ログファイルがありません\n")
                self.textbox.configure(font=DEFAULT_FONT)
            self.textbox.configure(state="disabled")
            if show_message:
                messagebox.showinfo("情報", "ログファイルを再読込しました。")
        except Exception as e:
            messagebox.showerror("ログ読込エラー", str(e))

    def clear_log(self):
        log_path = self.get_selected_log_path()
        if os.path.exists(log_path):
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("")
        self.load_log()
        messagebox.showinfo("情報", "ログファイルをクリアしました。")

    def open_log_dir(self):
        log_path = self.get_selected_log_path()
        log_dir = os.path.dirname(log_path)
        import subprocess
        subprocess.Popen(f'explorer "{log_dir}"')
        
    def on_file_change(self, *args):
        self.load_log()

# --- Toplevel用途で使いたい場合のサンプル ---
#class LogViewerDialog(ctk.CTkToplevel):
#    def __init__(self, master=None):
#        super().__init__(master)
#        self.title("ログビューア")
#        self.geometry("700x500")
#        viewer = LogViewer(self)
#        viewer.pack(fill="both", expand=True)
