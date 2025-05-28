import tkinter as tk
import tkinter.ttk as ttk
import os
from dotenv import load_dotenv
import datetime
import pytz
from tkinter import messagebox  # 追加


class TimeZoneSettings(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        timezone = os.getenv('TIMEZONE', 'system')
        self.var_timezone = tk.StringVar(value=timezone)
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True)
        ttk.Label(center_frame, text="タイムゾーン設定:", style="Big.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(10, 0))
        presets = ["system", "Asia/Tokyo", "UTC",
                   "America/New_York", "Europe/London"]
        self.combo_tz = ttk.Combobox(
            center_frame, values=presets, textvariable=self.var_timezone, width=24)
        self.combo_tz.grid(row=0, column=1, sticky=tk.W, pady=(10, 0))
        self.combo_tz.configure(font=("Meiryo", 12))
        ttk.Label(center_frame, text="任意のタイムゾーンを直接入力も可", style="Big.TLabel").grid(
            row=1, column=0, columnspan=2, sticky=tk.W)

        # 見出しラベル追加
        self.lbl_heading = ttk.Label(
            center_frame, text="指定のタイムゾーンの現在時刻", style="Big.TLabel")
        self.lbl_heading.grid(row=2, column=0, columnspan=2,
                              sticky=tk.W, pady=(10, 0))

        # 現在日時表示ラベル
        self.lbl_now = ttk.Label(center_frame, text="", style="Big.TLabel")
        self.lbl_now.grid(row=3, column=0, columnspan=2,
                          sticky=tk.W, pady=(5, 0))
        self._now_label_updating = False
        self.update_now_label(auto=True)
        self.var_timezone.trace_add(
            'write', lambda *a: self.update_now_label(auto=False))
        self.combo_tz.bind('<<ComboboxSelected>>',
                           lambda e: self.update_now_label(auto=False))

        label1 = tk.Label(center_frame, text='"system" を指定すると、実行環境のシステムタイムゾーンを自動的に使用します。', font=(
            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
        label1.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        label2 = tk.Label(center_frame, text='無効な値や空の場合は\nシステムタイムゾーンまたはUTCにフォールバックします。', font=(
            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
        label2.grid(row=5, column=0, columnspan=2, sticky=tk.W)
        ttk.Button(center_frame, text="保存", command=self.save_timezone, style="Big.TButton").grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(15, 0), padx=40)

    def update_now_label(self, auto=True):
        import calendar
        tzname = self.var_timezone.get().strip()
        try:
            if not tzname or tzname == 'system':
                import tzlocal
                tz = tzlocal.get_localzone()
            else:
                tz = pytz.timezone(tzname)
            now = datetime.datetime.now(tz)
            # 曜日（日本語）
            weekday_jp = ['月', '火', '水', '木', '金', '土', '日']
            weekday = weekday_jp[now.weekday()]
            # 午前/午後
            ampm = '午前' if now.hour < 12 else '午後'
            hour12 = now.hour if 1 <= now.hour <= 12 else (now.hour - 12 if now.hour > 12 else 12)
            # フォーマット
            now_str = f"{
                now.year}年{
                now.month:02d}月{
                now.day:02d}日({weekday}){ampm}{
                hour12:02d}時{
                    now.minute:02d}分{
                        now.second:02d}秒"
        except Exception:
            now_str = '(タイムゾーンが無効です)'
        self.lbl_now.config(text=f"現在日時: {now_str}")
        # 1秒ごとに自動更新
        if auto:
            if not self._now_label_updating:
                self._now_label_updating = True
            self.after(1000, self.update_now_label)
        else:
            self._now_label_updating = False

    def save_timezone(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith('TIMEZONE='):
                new_lines.append(f'TIMEZONE={self.var_timezone.get()}\n')
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f'TIMEZONE={self.var_timezone.get()}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        load_dotenv(env_path, override=True)
        self.update_now_label()
        messagebox.showinfo('保存', '保存しました')  # 追加
