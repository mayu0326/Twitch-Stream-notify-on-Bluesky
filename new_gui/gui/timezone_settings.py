import os
import datetime
import pytz
import customtkinter as ctk
from tkinter import messagebox

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")


class TimezoneSettingsFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.timezone_var = ctk.StringVar()
        self.status_var = ctk.StringVar()
        self.now_var = ctk.StringVar()
        self.timezone_list = [
            "system", "Asia/Tokyo", "UTC", "America/New_York", "Europe/London"
        ]
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(expand=True, fill="both")
        ctk.CTkLabel(center_frame, text="タイムゾーン設定", font=DEFAULT_FONT).pack(pady=(30, 10), anchor="center")
        # タイムゾーンラベルとプルダウンを横並びに中央寄せ
        tz_row = ctk.CTkFrame(center_frame, fg_color="transparent")
        tz_row.pack(pady=0, anchor="center")
        ctk.CTkLabel(tz_row, text="タイムゾーン:", font=DEFAULT_FONT).pack(side="left", anchor="center")
        self.tz_entry = ctk.CTkComboBox(tz_row, values=self.timezone_list, variable=self.timezone_var, font=DEFAULT_FONT, width=220, justify="center")
        self.tz_entry.pack(side="left", padx=(8,0), anchor="center")
        self.tz_entry.bind("<KeyRelease>", lambda e: self.update_now_label())
        self.tz_entry.bind("<<ComboboxSelected>>", lambda e: self.update_now_label())
        ctk.CTkLabel(center_frame, text="指定のタイムゾーンの現在時刻", font=DEFAULT_FONT).pack(pady=(20, 5), anchor="center")
        self.now_label = ctk.CTkLabel(center_frame, textvariable=self.now_var, font=DEFAULT_FONT)
        self.now_label.pack(pady=5, anchor="center")
        ctk.CTkLabel(center_frame, text='"system" を指定すると、実行環境のシステムタイムゾーンを自動的に使用します。', font=("Yu Gothic UI", 13, "bold"), anchor="center", justify="center", wraplength=420).pack(pady=(10,0), anchor="center")
        ctk.CTkLabel(center_frame, text='無効な値や空の場合はシステムタイムゾーンまたはUTCにフォールバックします。', font=("Yu Gothic UI", 13, "bold"), anchor="center", justify="center", wraplength=420).pack(anchor="center")
        ctk.CTkButton(center_frame, text="保存", command=self.save_timezone, font=DEFAULT_FONT, width=120).pack(pady=(30,0), anchor="center")
        self.status_label = ctk.CTkLabel(center_frame, textvariable=self.status_var, font=DEFAULT_FONT)
        self.status_label.pack(pady=10, anchor="center")
        self.load_timezone()
        self.update_now_label(auto=True)
        self.timezone_var.trace_add('write', lambda *a: self.update_now_label())

    def update_now_label(self, auto=False):
        tzname = self.timezone_var.get().strip()
        try:
            if not tzname or tzname == 'system':
                import tzlocal
                tz = tzlocal.get_localzone()
            else:
                tz = pytz.timezone(tzname)
            now = datetime.datetime.now(tz)
            weekday_jp = ['月', '火', '水', '木', '金', '土', '日']
            weekday = weekday_jp[now.weekday()]
            ampm = '午前' if now.hour < 12 else '午後'
            hour12 = now.hour if 1 <= now.hour <= 12 else (now.hour - 12 if now.hour > 12 else 12)
            now_str = f"{now.year}年{now.month:02d}月{now.day:02d}日({weekday}){ampm}{hour12:02d}時{now.minute:02d}分{now.second:02d}秒"
        except Exception:
            now_str = '(タイムゾーンが無効です)'
        self.now_var.set(f"現在日時: {now_str}")
        if auto:
            self.after(1000, lambda: self.update_now_label(auto=True))

    def save_timezone(self):
        tz = self.timezone_var.get().strip()
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        lines = []
        found = False
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('TIMEZONE='):
                        lines.append(f'TIMEZONE={tz}\n')
                        found = True
                    else:
                        lines.append(line)
        if not found:
            lines.append(f'TIMEZONE={tz}\n')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        self.status_var.set("保存しました")
        messagebox.showinfo("保存完了", "タイムゾーン設定を保存しました。")

    def load_timezone(self):
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        tz = "system"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('TIMEZONE='):
                        tz = line.strip().split('=', 1)[1]
                        break
        self.timezone_var.set(tz)
        self.status_var.set("")
