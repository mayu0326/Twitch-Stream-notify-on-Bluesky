
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
初期設定ウィザード（ダミー）
"""
import customtkinter as ctk
from version_info import __version__

DEFAULT_FONT = ("Yu Gothic UI", 12, "normal")


class SetupWizard(ctk.CTkToplevel):
    def __init__(self, master=None, on_finish=None):
        super().__init__(master)
        self.title("セットアップウィザード（ダミー）")
        self.geometry("500x350")
        self.on_finish = on_finish
        self.step = 0
        self._draw_step()

    def _draw_step(self):
        for widget in self.winfo_children():
            widget.destroy()
        steps = [
            "Step 1/5: 配信サービス選択",
            "Step 2/5: API認証情報設定",
            "Step 3/5: Blueskyアカウント設定",
            "Step 4/5: 通知テンプレート設定",
            "Step 5/5: トンネル方式選択・確認"
        ]
        ctk.CTkLabel(self, text=steps[self.step], font=DEFAULT_FONT).pack(pady=20)
        ctk.CTkLabel(self, text="（ダミーUI・入力不可）", text_color="gray").pack(pady=10)
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=30)
        if self.step > 0:
            ctk.CTkButton(btn_frame, text="← 戻る", command=self._back, font=DEFAULT_FONT).pack(side="left", padx=10)
        if self.step < 4:
            ctk.CTkButton(btn_frame, text="次へ →", command=self._next, font=DEFAULT_FONT).pack(side="left", padx=10)
        else:
            ctk.CTkButton(btn_frame, text="完了", command=self._finish, font=DEFAULT_FONT).pack(side="left", padx=10)

    def _next(self):
        if self.step < 4:
            self.step += 1
            self._draw_step()

    def _back(self):
        if self.step > 0:
            self.step -= 1
            self._draw_step()

    def _finish(self):
        if self.on_finish:
            self.on_finish()
        self.destroy()
