"""
初期設定ウィザード（複数ステップ、バリデーション付き）
"""
import tkinter as tk
from tkinter import ttk, messagebox


class SetupWizard(tk.Toplevel):
    def __init__(self, master=None, on_finish=None):
        super().__init__(master)
        self.title("初期設定ウィザード")
        self.geometry("500x350")
        self.resizable(False, False)
        self.on_finish = on_finish
        self.current_step = 0
        self.steps = [self.step1, self.step2, self.step3]
        self.vars = {}
        self.create_widgets()
        self.show_step(0)
        # ウィンドウの×ボタン押下時にも on_finish を呼ぶ
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_cancel(self):
        self.destroy()
        if self.on_finish:
            self.on_finish()

    def create_widgets(self):
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.btn_prev = ttk.Button(self, text="前へ", command=self.prev_step)
        self.btn_next = ttk.Button(self, text="次へ", command=self.next_step)
        self.btn_prev.pack(side=tk.LEFT, padx=20, pady=10)
        self.btn_next.pack(side=tk.RIGHT, padx=20, pady=10)
        # キャンセルボタン追加
        self.btn_cancel = ttk.Button(
            self, text="キャンセル", command=self._on_cancel)
        self.btn_cancel.pack(side=tk.BOTTOM, pady=10)

    def show_step(self, idx):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.current_step = idx
        self.steps[idx]()
        self.btn_prev.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        if idx == len(self.steps) - 1:
            self.btn_next.config(text="保存して完了")
        else:
            self.btn_next.config(text="次へ")

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def next_step(self):
        if not self.validate_step():
            return
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.save_settings()
            self.destroy()
            if self.on_finish:
                self.on_finish()

    def step1(self):
        ttk.Label(
            self.frame, text="Twitch/YouTube/ニコニコ/Bluesky認証情報を入力").pack(anchor=tk.W, pady=5)
        self.vars['twitch_id'] = tk.StringVar()
        self.vars['twitch_secret'] = tk.StringVar()
        self.vars['bsky_user'] = tk.StringVar()
        self.vars['bsky_pass'] = tk.StringVar()
        ttk.Label(self.frame, text="TwitchクライアントID").pack(anchor=tk.W)
        ttk.Entry(self.frame, textvariable=self.vars['twitch_id']).pack(
            fill=tk.X)
        ttk.Label(self.frame, text="Twitchクライアントシークレット").pack(anchor=tk.W)
        ttk.Entry(
            self.frame, textvariable=self.vars['twitch_secret'], show='*').pack(fill=tk.X)
        ttk.Label(self.frame, text="Blueskyユーザー名").pack(anchor=tk.W)
        ttk.Entry(self.frame, textvariable=self.vars['bsky_user']).pack(
            fill=tk.X)
        ttk.Label(self.frame, text="Blueskyアプリパスワード").pack(anchor=tk.W)
        ttk.Entry(
            self.frame, textvariable=self.vars['bsky_pass'], show='*').pack(fill=tk.X)

    def step2(self):
        ttk.Label(self.frame, text="通知設定・テンプレート選択").pack(anchor=tk.W, pady=5)
        self.vars['notify_online'] = tk.BooleanVar(value=True)
        self.vars['notify_offline'] = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frame, text="ストリームオンライン時に通知",
                        variable=self.vars['notify_online']).pack(anchor=tk.W)
        ttk.Checkbutton(self.frame, text="ストリームオフライン時に通知",
                        variable=self.vars['notify_offline']).pack(anchor=tk.W)
        ttk.Label(self.frame, text="テンプレートファイル: (ダミー)").pack(anchor=tk.W)
        ttk.Label(self.frame, text="画像ファイル: (ダミー)").pack(anchor=tk.W)

    def step3(self):
        ttk.Label(self.frame, text="設定内容確認").pack(anchor=tk.W, pady=5)
        summary = f"Twitch ID: {self.vars['twitch_id'].get()}\nBluesky: {self.vars['bsky_user'].get()}\n通知: オンライン={self.vars['notify_online'].get()} オフライン={self.vars['notify_offline'].get()}"
        ttk.Label(self.frame, text=summary).pack(anchor=tk.W)

    def validate_step(self):
        if self.current_step == 0:
            if not self.vars['twitch_id'].get() or not self.vars['twitch_secret'].get() or not self.vars['bsky_user'].get() or not self.vars['bsky_pass'].get():
                messagebox.showerror("入力エラー", "すべての必須項目を入力してください")
                return False
        return True

    def save_settings(self):
        # TODO: settings.envへ保存処理
        pass
