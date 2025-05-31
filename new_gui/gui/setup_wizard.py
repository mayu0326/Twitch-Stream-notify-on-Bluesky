"""
初期設定ウィザード（ダミー）
"""
import customtkinter as ctk

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
