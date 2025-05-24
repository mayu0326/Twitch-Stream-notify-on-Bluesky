"""
テンプレート・画像カスタマイズUI
"""
import tkinter as tk
from tkinter import ttk, filedialog
import os
from dotenv import load_dotenv


class NotificationCustomizationFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        # サービスごとにタブ分割
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- Twitchタブ ---
        twitch_frame = self.create_twitch_tab(notebook)

        # --- YouTubeタブ ---
        yt_frame = self.create_youtube_tab(notebook)

        # --- ニコニコタブ ---
        nico_frame = self.create_nico_tab(notebook)

        # --- ログ/コンソール設定タブ ---
        class LogConsoleSettingsFrame(ttk.Frame):
            def __init__(self, master=None):
                super().__init__(master)
                load_dotenv(os.path.join(
                    os.path.dirname(__file__), '../settings.env'))
                log_level = os.getenv('LOG_LEVEL', 'INFO')
                log_retention = os.getenv('LOG_RETENTION_DAYS', '14')
                self.var_log_level = tk.StringVar(value=log_level)
                self.var_log_retention = tk.StringVar(value=log_retention)
                ttk.Label(self, text="アプリケーションのログレベル:", style="Big.TLabel").grid(
                    row=0, column=0, sticky=tk.W, pady=(10, 0))
                self.combo_log_level = ttk.Combobox(self, values=[
                                                    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly", width=12, textvariable=self.var_log_level)
                self.combo_log_level.grid(
                    row=0, column=1, sticky=tk.W, pady=(10, 0))
                self.combo_log_level.configure(font=("Meiryo", 12))
                ttk.Label(self, text="ログファイルのローテーション保持日数:", style="Big.TLabel").grid(
                    row=1, column=0, sticky=tk.W, pady=(10, 0))
                self.spin_retention = tk.Spinbox(
                    self, from_=1, to=365, width=8, textvariable=self.var_log_retention, font=("Meiryo", 12))
                self.spin_retention.grid(
                    row=1, column=1, sticky=tk.W, pady=(10, 0))
                ttk.Button(self, text="保存", command=self.save_log_settings, style="Big.TButton").grid(
                    row=2, column=1, sticky=tk.W, pady=(15, 0))

            def save_log_settings(self):
                env_path = os.path.join(
                    os.path.dirname(__file__), '../settings.env')
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                new_lines = []
                found_level = found_retention = False
                for line in lines:
                    if line.startswith('LOG_LEVEL='):
                        new_lines.append(
                            f'LOG_LEVEL={self.var_log_level.get()}\n')
                        found_level = True
                    elif line.startswith('LOG_RETENTION_DAYS='):
                        new_lines.append(
                            f'LOG_RETENTION_DAYS={self.var_log_retention.get()}\n')
                        found_retention = True
                    else:
                        new_lines.append(line)
                if not found_level:
                    new_lines.append(f'LOG_LEVEL={self.var_log_level.get()}\n')
                if not found_retention:
                    new_lines.append(
                        f'LOG_RETENTION_DAYS={self.var_log_retention.get()}\n')
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                load_dotenv(env_path, override=True)

        log_console_frame = LogConsoleSettingsFrame(notebook)
        notebook.add(log_console_frame, text="ログ/コンソール設定")
        # --- Discordタブ（分割後） ---
        from discord_notification_frame import DiscordNotificationFrame
        discord_frame = DiscordNotificationFrame(notebook)
        notebook.add(discord_frame, text="Discord通知設定")
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        discord_url = os.getenv('discord_error_notifier_url', '')
        discord_level = os.getenv('discord_notify_level', 'CRITICAL')
        discord_enabled = os.getenv(
            'DISCORD_NOTIFY_ENABLED', 'True').lower() == 'true'
        self.var_discord_enabled = tk.BooleanVar(value=discord_enabled)
        ttk.Checkbutton(discord_frame, text="Discord通知を有効化", variable=self.var_discord_enabled, style="Big.TCheckbutton").grid(
            row=0, column=0, sticky=tk.W, columnspan=2)
        ttk.Label(discord_frame, text="Discord通知レベル:", style="Big.TLabel").grid(
            row=1, column=0, sticky=tk.W)
        self.combo_discord_level = ttk.Combobox(discord_frame, values=[
                                                "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly", width=12)
        self.combo_discord_level.set(discord_level)
        self.combo_discord_level.grid(row=1, column=1, sticky=tk.W)
        # フォントサイズを他のボタンと同じに
        self.combo_discord_level.configure(font=("Meiryo", 12))
        ttk.Label(discord_frame, text="Discord Webhook URL:", style="Big.TLabel").grid(
            row=2, column=0, sticky=tk.W, columnspan=2)
        self.entry_discord_url = ttk.Entry(discord_frame, width=70)
        self.entry_discord_url.insert(0, discord_url)
        self.entry_discord_url.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        # フォントサイズを他のボタンと同じに
        self.entry_discord_url.configure(font=("Meiryo", 12))
        ttk.Button(discord_frame, text="設定を反映", command=self.save_discord_settings, style="Big.TButton").grid(
            row=4, column=1, sticky=tk.W, pady=(5, 0))
        ttk.Button(discord_frame, text="設定を消去", command=self.clear_discord_settings, style="Big.TButton").grid(
            row=4, column=0, sticky=tk.W, pady=(5, 0))

        # フォント・ボタンサイズをさらに小さく（2回りダウン）
        small_font = ("Meiryo", 12)
        small_btn_style = ttk.Style()
        small_btn_style.configure("Big.TButton", font=small_font, padding=4)
        small_lbl_style = ttk.Style()
        small_lbl_style.configure("Big.TLabel", font=small_font)
        small_chk_style = ttk.Style()
        small_chk_style.configure("Big.TCheckbutton", font=small_font)

    @classmethod
    def create_twitch_tab(cls, notebook):
        import os
        from dotenv import load_dotenv
        from PIL import Image, ImageTk
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        load_dotenv(env_path)
        notify_online = os.getenv(
            'NOTIFY_ON_ONLINE', 'False').lower() == 'true'
        notify_offline = os.getenv(
            'NOTIFY_ON_OFFLINE', 'False').lower() == 'true'
        tpl_online = os.getenv('BLUESKY_TEMPLATE_PATH',
                               'templates/twitch_online_template.txt')
        tpl_offline = os.getenv(
            'BLUESKY_OFFLINE_TEMPLATE_PATH', 'templates/twitch_offline_template.txt')
        img_path = os.getenv('BLUESKY_IMAGE_PATH', 'images/noimage.png')
        twitch_frame = ttk.Frame(notebook)
        big_font = ("Meiryo", 16)
        big_btn_style = ttk.Style()
        big_btn_style.configure("Big.TButton", font=big_font, padding=8)
        big_lbl_style = ttk.Style()
        big_lbl_style.configure("Big.TLabel", font=big_font)
        big_chk_style = ttk.Style()
        big_chk_style.configure("Big.TCheckbutton", font=big_font)
        # --- 変数をインスタンス属性で保持 ---
        twitch_frame.var_online = tk.BooleanVar(value=notify_online)
        twitch_frame.var_offline = tk.BooleanVar(value=notify_offline)
        twitch_frame.tpl_online = tk.StringVar(value=tpl_online)
        twitch_frame.tpl_offline = tk.StringVar(value=tpl_offline)
        twitch_frame.img_path = tk.StringVar(value=img_path)
        ttk.Checkbutton(twitch_frame, text="放送開始時に投稿", variable=twitch_frame.var_online, style="Big.TCheckbutton").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(twitch_frame, text="放送終了時に投稿", variable=twitch_frame.var_offline, style="Big.TCheckbutton").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(twitch_frame, text="配信開始時の投稿テンプレート:", style="Big.TLabel").grid(
            row=2, column=0, sticky=tk.W)
        # テンプレートファイル名（ファイル名のみ表示）

        def update_tpl_online_label():
            path = twitch_frame.tpl_online.get()
            lbl_online_tpl.config(text=os.path.basename(path))
        lbl_online_tpl = ttk.Label(
            twitch_frame, text=os.path.basename(twitch_frame.tpl_online.get()), style="Big.TLabel")
        lbl_online_tpl.grid(row=2, column=1, sticky=tk.W)
        twitch_frame.tpl_online.trace_add(
            'write', lambda *a: update_tpl_online_label())
        update_tpl_online_label()
        ttk.Button(twitch_frame, text="テンプレート変更...", command=lambda: cls.change_template_file(twitch_frame.tpl_online), style="Big.TButton", width=18).grid(
            row=3, column=1, sticky=tk.W, pady=(0, 10))
        # 画像ファイルラベル（上部に2列分）
        ttk.Label(twitch_frame, text="配信開始投稿時に使用する画像ファイル:", style="Big.TLabel").grid(
            row=4, column=0, columnspan=2, sticky=tk.W)
        # プレビュー用ラベル（左側2行分）
        twitch_frame.img_preview = tk.Label(
            twitch_frame, width=120, height=90, relief=tk.SOLID, bg='white')
        twitch_frame.img_preview.grid(
            row=5, column=0, rowspan=2, sticky=tk.W+tk.N+tk.S, padx=(0, 10), pady=(0, 10))
        # 画像ファイル名（右側）
        import os

        def update_img_label():
            path = twitch_frame.img_path.get()
            lbl_online_img.config(text=os.path.basename(path))
        lbl_online_img = ttk.Label(
            twitch_frame, text=os.path.basename(twitch_frame.img_path.get()), style="Big.TLabel")
        lbl_online_img.grid(row=5, column=1, sticky=tk.W, pady=(0, 5))
        twitch_frame.img_path.trace_add('write', lambda *a: update_img_label())
        update_img_label()
        # 画像変更ボタン（右側）
        ttk.Button(twitch_frame, text="画像変更...", command=lambda: cls.change_image_file(twitch_frame.img_path), style="Big.TButton", width=18).grid(
            row=6, column=1, sticky=tk.W, pady=(0, 10))

        def update_img_preview(*args):
            path = twitch_frame.img_path.get()
            try:
                img = Image.open(path)
                img.thumbnail((120, 90))
                twitch_frame._imgtk = ImageTk.PhotoImage(img)
                twitch_frame.img_preview.configure(image=twitch_frame._imgtk)
            except Exception:
                twitch_frame.img_preview.configure(image='')
        twitch_frame.img_path.trace_add(
            'write', lambda *a: update_img_preview())
        update_img_preview()
        # 放送終了時の投稿テンプレートラベルを追加
        ttk.Label(twitch_frame, text="放送終了時の投稿テンプレート:", style="Big.TLabel").grid(
            row=7, column=0, sticky=tk.W)
        lbl_offline_tpl = ttk.Label(
            twitch_frame, text=os.path.basename(twitch_frame.tpl_offline.get()), style="Big.TLabel")
        lbl_offline_tpl.grid(row=7, column=1, sticky=tk.W)
        twitch_frame.tpl_offline.trace_add(
            'write', lambda *a: lbl_offline_tpl.config(text=os.path.basename(twitch_frame.tpl_offline.get())))
        lbl_offline_tpl.config(text=os.path.basename(
            twitch_frame.tpl_offline.get()))
        # --- 保存ボタン ---
        ttk.Button(twitch_frame, text="保存", command=lambda: cls.save_twitch_settings(twitch_frame), style="Big.TButton", width=18).grid(
            row=9, column=1, sticky=tk.W, pady=(10, 0))
        return twitch_frame

    @staticmethod
    def change_template_file(var):
        path = filedialog.askopenfilename(
            title="テンプレートファイルを選択", filetypes=[("Text files", "*.txt")])
        if path:
            var.set(path)

    @staticmethod
    def change_image_file(var):
        path = filedialog.askopenfilename(title="画像ファイルを選択", filetypes=[
                                          ("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if path:
            var.set(path)

    @staticmethod
    def save_twitch_settings(frame):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found_online = found_offline = found_tpl_online = found_tpl_offline = found_img = False
        for line in lines:
            if line.startswith('NOTIFY_ON_ONLINE='):
                new_lines.append(
                    f'NOTIFY_ON_ONLINE={str(frame.var_online.get())}\n')
                found_online = True
            elif line.startswith('NOTIFY_ON_OFFLINE='):
                new_lines.append(
                    f'NOTIFY_ON_OFFLINE={str(frame.var_offline.get())}\n')
                found_offline = True
            elif line.startswith('BLUESKY_TEMPLATE_PATH='):
                new_lines.append(
                    f'BLUESKY_TEMPLATE_PATH={frame.tpl_online.get()}\n')
                found_tpl_online = True
            elif line.startswith('BLUESKY_OFFLINE_TEMPLATE_PATH='):
                new_lines.append(
                    f'BLUESKY_OFFLINE_TEMPLATE_PATH={frame.tpl_offline.get()}\n')
                found_tpl_offline = True
            elif line.startswith('BLUESKY_IMAGE_PATH='):
                new_lines.append(
                    f'BLUESKY_IMAGE_PATH={frame.img_path.get()}\n')
                found_img = True
            else:
                new_lines.append(line)
        if not found_online:
            new_lines.append(
                f'NOTIFY_ON_ONLINE={str(frame.var_online.get())}\n')
        if not found_offline:
            new_lines.append(
                f'NOTIFY_ON_OFFLINE={str(frame.var_offline.get())}\n')
        if not found_tpl_online:
            new_lines.append(
                f'BLUESKY_TEMPLATE_PATH={frame.tpl_online.get()}\n')
        if not found_tpl_offline:
            new_lines.append(
                f'BLUESKY_OFFLINE_TEMPLATE_PATH={frame.tpl_offline.get()}\n')
        if not found_img:
            new_lines.append(f'BLUESKY_IMAGE_PATH={frame.img_path.get()}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        # 反映後、再読み込み
        load_dotenv(env_path, override=True)
        frame.var_online.set(
            os.getenv('NOTIFY_ON_ONLINE', 'False').lower() == 'true')
        frame.var_offline.set(
            os.getenv('NOTIFY_ON_OFFLINE', 'False').lower() == 'true')
        frame.tpl_online.set(
            os.getenv('BLUESKY_TEMPLATE_PATH', 'templates/twitch_online_template.txt'))
        frame.tpl_offline.set(os.getenv(
            'BLUESKY_OFFLINE_TEMPLATE_PATH', 'templates/twitch_offline_template.txt'))
        frame.img_path.set(
            os.getenv('BLUESKY_IMAGE_PATH', 'images/noimage.png'))

    @classmethod
    def create_youtube_tab(cls, notebook):
        import os
        from dotenv import load_dotenv
        from PIL import Image, ImageTk
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        load_dotenv(env_path)
        notify_online = os.getenv(
            'NOTIFY_ON_YOUTUBE_ONLINE', 'False').lower() == 'true'
        notify_newvideo = os.getenv(
            'NOTIFY_ON_YOUTUBE_NEW_VIDEO', 'False').lower() == 'true'
        tpl_online = os.getenv(
            'BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH', 'templates/yt_nico_online_template.txt')
        tpl_newvideo = os.getenv(
            'BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH', 'templates/yt_nico_new_video_template.txt')
        img_path = os.getenv('BLUESKY_IMAGE_PATH', 'images/noimage.png')
        yt_frame = ttk.Frame(notebook)
        yt_frame.var_yt_online = tk.BooleanVar(value=notify_online)
        yt_frame.var_yt_newvideo = tk.BooleanVar(value=notify_newvideo)
        yt_frame.tpl_online = tk.StringVar(value=tpl_online)
        yt_frame.tpl_newvideo = tk.StringVar(value=tpl_newvideo)
        yt_frame.img_path = tk.StringVar(value=img_path)
        ttk.Checkbutton(yt_frame, text="放送開始時に投稿", variable=yt_frame.var_yt_online, style="Big.TCheckbutton").grid(
            row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(yt_frame, text="新着動画投稿時に投稿", variable=yt_frame.var_yt_newvideo, style="Big.TCheckbutton").grid(
            row=1, column=0, sticky=tk.W)
        ttk.Label(yt_frame, text="配信開始時の投稿テンプレート:", style="Big.TLabel").grid(
            row=2, column=0, sticky=tk.W)
        # テンプレートファイル名（ファイル名のみ表示）

        def update_tpl_yt_online_label():
            path = yt_frame.tpl_online.get()
            lbl_yt_tpl.config(text=os.path.basename(path))
        lbl_yt_tpl = ttk.Label(
            yt_frame, text=os.path.basename(yt_frame.tpl_online.get()), style="Big.TLabel")
        lbl_yt_tpl.grid(row=2, column=1, sticky=tk.W)
        yt_frame.tpl_online.trace_add(
            'write', lambda *a: update_tpl_yt_online_label())
        update_tpl_yt_online_label()
        ttk.Button(yt_frame, text="テンプレート変更...", command=lambda: cls.change_template_file(yt_frame.tpl_online), style="Big.TButton", width=18).grid(
            row=3, column=1, sticky=tk.W, pady=(0, 10))
        # 画像ファイルラベル（上部に2列分）
        ttk.Label(yt_frame, text="配信開始投稿時に使用する画像ファイル:", style="Big.TLabel").grid(
            row=4, column=0, columnspan=2, sticky=tk.W)
        # プレビュー用ラベル（左側2行分）
        yt_frame.img_preview = tk.Label(
            yt_frame, width=120, height=90, relief=tk.SOLID, bg='white')
        yt_frame.img_preview.grid(
            row=5, column=0, rowspan=2, sticky=tk.W+tk.N+tk.S, padx=(0, 10), pady=(0, 10))
        # 画像ファイル名（右側）
        import os

        def update_img_label():
            path = yt_frame.img_path.get()
            lbl_yt_img.config(text=os.path.basename(path))
        lbl_yt_img = ttk.Label(
            yt_frame, text=os.path.basename(yt_frame.img_path.get()), style="Big.TLabel")
        lbl_yt_img.grid(row=5, column=1, sticky=tk.W, pady=(0, 5))
        yt_frame.img_path.trace_add('write', lambda *a: update_img_label())
        update_img_label()
        # 画像変更ボタン（右側）
        ttk.Button(yt_frame, text="画像変更...", command=lambda: cls.change_image_file(yt_frame.img_path), style="Big.TButton", width=18).grid(
            row=6, column=1, sticky=tk.W, pady=(0, 10))

        def update_img_preview(*args):
            path = yt_frame.img_path.get()
            try:
                img = Image.open(path)
                img.thumbnail((120, 90))
                yt_frame._imgtk = ImageTk.PhotoImage(img)
                yt_frame.img_preview.configure(image=yt_frame._imgtk)
            except Exception:
                yt_frame.img_preview.configure(image='')
        yt_frame.img_path.trace_add('write', lambda *a: update_img_preview())
        update_img_preview()
        ttk.Label(yt_frame, text="新着動画投稿時の投稿テンプレート:", style="Big.TLabel").grid(
            row=8, column=0, sticky=tk.W)
        # テンプレートファイル名（ファイル名のみ表示）

        def update_tpl_newvideo_label():
            path = yt_frame.tpl_newvideo.get()
            lbl_yt_newvideo_tpl.config(text=os.path.basename(path))
        lbl_yt_newvideo_tpl = ttk.Label(
            yt_frame, text=os.path.basename(yt_frame.tpl_newvideo.get()), style="Big.TLabel")
        lbl_yt_newvideo_tpl.grid(row=8, column=1, sticky=tk.W)
        yt_frame.tpl_newvideo.trace_add(
            'write', lambda *a: update_tpl_newvideo_label())
        update_tpl_newvideo_label()
        ttk.Button(yt_frame, text="テンプレート変更...", command=lambda: cls.change_template_file(yt_frame.tpl_newvideo), style="Big.TButton", width=18).grid(
            row=9, column=1, sticky=tk.W, pady=(0, 10))
        # --- 保存ボタン ---
        ttk.Button(yt_frame, text="保存", command=lambda: cls.save_youtube_settings(yt_frame), style="Big.TButton", width=18).grid(
            row=10, column=1, sticky=tk.W, pady=(10, 0))
        return yt_frame

    @staticmethod
    def save_youtube_settings(frame):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found_online = found_newvideo = found_tpl_online = found_tpl_newvideo = found_img = False
        for line in lines:
            if line.startswith('NOTIFY_ON_YOUTUBE_ONLINE='):
                new_lines.append(
                    f'NOTIFY_ON_YOUTUBE_ONLINE={str(frame.var_yt_online.get())}\n')
                found_online = True
            elif line.startswith('NOTIFY_ON_YOUTUBE_NEW_VIDEO='):
                new_lines.append(
                    f'NOTIFY_ON_YOUTUBE_NEW_VIDEO={str(frame.var_yt_newvideo.get())}\n')
                found_newvideo = True
            elif line.startswith('BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH='):
                new_lines.append(
                    f'BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH={frame.tpl_online.get()}\n')
                found_tpl_online = True
            elif line.startswith('BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH='):
                new_lines.append(
                    f'BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH={frame.tpl_newvideo.get()}\n')
                found_tpl_newvideo = True
            elif line.startswith('BLUESKY_IMAGE_PATH='):
                new_lines.append(
                    f'BLUESKY_IMAGE_PATH={frame.img_path.get()}\n')
                found_img = True
            else:
                new_lines.append(line)
        if not found_online:
            new_lines.append(
                f'NOTIFY_ON_YOUTUBE_ONLINE={str(frame.var_yt_online.get())}\n')
        if not found_newvideo:
            new_lines.append(
                f'NOTIFY_ON_YOUTUBE_NEW_VIDEO={str(frame.var_yt_newvideo.get())}\n')
        if not found_tpl_online:
            new_lines.append(
                f'BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH={frame.tpl_online.get()}\n')
        if not found_tpl_newvideo:
            new_lines.append(
                f'BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH={frame.tpl_newvideo.get()}\n')
        if not found_img:
            new_lines.append(f'BLUESKY_IMAGE_PATH={frame.img_path.get()}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        # 反映後、再読み込み
        load_dotenv(env_path, override=True)
        frame.var_yt_online.set(
            os.getenv('NOTIFY_ON_YOUTUBE_ONLINE', 'False').lower() == 'true')
        frame.var_yt_newvideo.set(
            os.getenv('NOTIFY_ON_YOUTUBE_NEW_VIDEO', 'False').lower() == 'true')
        frame.tpl_online.set(os.getenv(
            'BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH', 'templates/yt_nico_online_template.txt'))
        frame.tpl_newvideo.set(os.getenv(
            'BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH', 'templates/yt_nico_new_video_template.txt'))
        frame.img_path.set(
            os.getenv('BLUESKY_IMAGE_PATH', 'images/noimage.png'))

    @classmethod
    def create_nico_tab(cls, notebook):
        import os
        from dotenv import load_dotenv
        from PIL import Image, ImageTk
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        load_dotenv(env_path)
        notify_online = os.getenv(
            'NOTIFY_ON_NICONICO_ONLINE', 'False').lower() == 'true'
        notify_newvideo = os.getenv(
            'NOTIFY_ON_NICONICO_NEW_VIDEO', 'False').lower() == 'true'
        tpl_online = os.getenv(
            'BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH', 'templates/yt_nico_online_template.txt')
        tpl_newvideo = os.getenv(
            'BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH', 'templates/yt_nico_new_video_template.txt')
        img_path = os.getenv('BLUESKY_IMAGE_PATH', 'images/noimage.png')
        nico_frame = ttk.Frame(notebook)
        nico_frame.var_nico_online = tk.BooleanVar(value=notify_online)
        nico_frame.var_nico_newvideo = tk.BooleanVar(value=notify_newvideo)
        nico_frame.tpl_online = tk.StringVar(value=tpl_online)
        nico_frame.tpl_newvideo = tk.StringVar(value=tpl_newvideo)
        nico_frame.img_path = tk.StringVar(value=img_path)
        ttk.Checkbutton(nico_frame, text="放送開始時に投稿", variable=nico_frame.var_nico_online, style="Big.TCheckbutton").grid(
            row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(nico_frame, text="新着動画投稿時に投稿", variable=nico_frame.var_nico_newvideo, style="Big.TCheckbutton").grid(
            row=1, column=0, sticky=tk.W)
        ttk.Label(nico_frame, text="配信開始時の投稿テンプレート:", style="Big.TLabel").grid(
            row=2, column=0, sticky=tk.W)
        # テンプレートファイル名（ファイル名のみ表示）

        def update_tpl_nico_online_label():
            path = nico_frame.tpl_online.get()
            lbl_nico_tpl.config(text=os.path.basename(path))
        lbl_nico_tpl = ttk.Label(
            nico_frame, text=os.path.basename(nico_frame.tpl_online.get()), style="Big.TLabel")
        lbl_nico_tpl.grid(row=2, column=1, sticky=tk.W)
        nico_frame.tpl_online.trace_add(
            'write', lambda *a: update_tpl_nico_online_label())
        update_tpl_nico_online_label()
        ttk.Button(nico_frame, text="テンプレート変更...", command=lambda: cls.change_template_file(nico_frame.tpl_online), style="Big.TButton", width=18).grid(
            row=3, column=1, sticky=tk.W, pady=(0, 10))
        # 画像ファイルラベル（上部に2列分）
        ttk.Label(nico_frame, text="配信開始投稿時に使用する画像ファイル:", style="Big.TLabel").grid(
            row=4, column=0, columnspan=2, sticky=tk.W)
        # プレビュー用ラベル（左側2行分）
        nico_frame.img_preview = tk.Label(
            nico_frame, width=120, height=90, relief=tk.SOLID, bg='white')
        nico_frame.img_preview.grid(
            row=5, column=0, rowspan=2, sticky=tk.W+tk.N+tk.S, padx=(0, 10), pady=(0, 10))
        # 画像ファイル名（右側）
        import os

        def update_img_label():
            path = nico_frame.img_path.get()
            lbl_nico_img.config(text=os.path.basename(path))
        lbl_nico_img = ttk.Label(
            nico_frame, text=os.path.basename(nico_frame.img_path.get()), style="Big.TLabel")
        lbl_nico_img.grid(row=5, column=1, sticky=tk.W, pady=(0, 5))
        nico_frame.img_path.trace_add('write', lambda *a: update_img_label())
        update_img_label()
        # 画像変更ボタン（右側）
        ttk.Button(nico_frame, text="画像変更...", command=lambda: cls.change_image_file(nico_frame.img_path), style="Big.TButton", width=18).grid(
            row=6, column=1, sticky=tk.W, pady=(0, 10))

        def update_img_preview(*args):
            path = nico_frame.img_path.get()
            try:
                img = Image.open(path)
                img.thumbnail((120, 90))
                nico_frame._imgtk = ImageTk.PhotoImage(img)
                nico_frame.img_preview.configure(image=nico_frame._imgtk)
            except Exception:
                nico_frame.img_preview.configure(image='')
        nico_frame.img_path.trace_add('write', lambda *a: update_img_preview())
        update_img_preview()
        ttk.Label(nico_frame, text="新着動画投稿時の投稿テンプレート:", style="Big.TLabel").grid(
            row=8, column=0, sticky=tk.W)
        # テンプレートファイル名（ファイル名のみ表示）

        def update_tpl_newvideo_label():
            path = nico_frame.tpl_newvideo.get()
            lbl_nico_newvideo_tpl.config(text=os.path.basename(path))
        lbl_nico_newvideo_tpl = ttk.Label(
            nico_frame, text=os.path.basename(nico_frame.tpl_newvideo.get()), style="Big.TLabel")
        lbl_nico_newvideo_tpl.grid(row=8, column=1, sticky=tk.W)
        nico_frame.tpl_newvideo.trace_add(
            'write', lambda *a: update_tpl_newvideo_label())
        update_tpl_newvideo_label()
        # --- 保存ボタン ---
        ttk.Button(nico_frame, text="保存", command=lambda: cls.save_nico_settings(nico_frame), style="Big.TButton", width=18).grid(
            row=10, column=1, sticky=tk.W, pady=(10, 0))
        return nico_frame

    @staticmethod
    def save_nico_settings(frame):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found_online = found_newvideo = found_tpl_online = found_tpl_newvideo = found_img = False
        for line in lines:
            if line.startswith('NOTIFY_ON_NICONICO_ONLINE='):
                new_lines.append(
                    f'NOTIFY_ON_NICONICO_ONLINE={str(frame.var_nico_online.get())}\n')
                found_online = True
            elif line.startswith('NOTIFY_ON_NICONICO_NEW_VIDEO='):
                new_lines.append(
                    f'NOTIFY_ON_NICONICO_NEW_VIDEO={str(frame.var_nico_newvideo.get())}\n')
                found_newvideo = True
            elif line.startswith('BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH='):
                new_lines.append(
                    f'BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH={frame.tpl_online.get()}\n')
                found_tpl_online = True
            elif line.startswith('BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH='):
                new_lines.append(
                    f'BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH={frame.tpl_newvideo.get()}\n')
                found_tpl_newvideo = True
            elif line.startswith('BLUESKY_IMAGE_PATH='):
                new_lines.append(
                    f'BLUESKY_IMAGE_PATH={frame.img_path.get()}\n')
                found_img = True
            else:
                new_lines.append(line)
        if not found_online:
            new_lines.append(
                f'NOTIFY_ON_NICONICO_ONLINE={str(frame.var_nico_online.get())}\n')
        if not found_newvideo:
            new_lines.append(
                f'NOTIFY_ON_NICONICO_NEW_VIDEO={str(frame.var_nico_newvideo.get())}\n')
        if not found_tpl_online:
            new_lines.append(
                f'BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH={frame.tpl_online.get()}\n')
        if not found_tpl_newvideo:
            new_lines.append(
                f'BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH={frame.tpl_newvideo.get()}\n')
        if not found_img:
            new_lines.append(f'BLUESKY_IMAGE_PATH={frame.img_path.get()}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        # 反映後、再読み込み
        load_dotenv(env_path, override=True)
        frame.var_nico_online.set(
            os.getenv('NOTIFY_ON_NICONICO_ONLINE', 'False').lower() == 'true')
        frame.var_nico_newvideo.set(
            os.getenv('NOTIFY_ON_NICONICO_NEW_VIDEO', 'False').lower() == 'true')
        frame.tpl_online.set(os.getenv(
            'BLUESKY_YT_NICO_ONLINE_TEMPLATE_PATH', 'templates/yt_nico_online_template.txt'))
        frame.tpl_newvideo.set(os.getenv(
            'BLUESKY_YT_NICO_NEW_VIDEO_TEMPLATE_PATH', 'templates/yt_nico_new_video_template.txt'))
        frame.img_path.set(
            os.getenv('BLUESKY_IMAGE_PATH', 'images/noimage.png'))

    def change_online_template(self):
        filedialog.askopenfilename(title="オンライン通知テンプレートを選択", filetypes=[
                                   ("Text files", "*.txt")])
        # TODO: ファイルコピー・設定反映

    def change_online_image(self):
        filedialog.askopenfilename(title="オンライン通知画像を選択", filetypes=[
                                   ("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        # TODO: ファイルコピー・設定反映

    def change_offline_template(self):
        filedialog.askopenfilename(title="オフライン通知テンプレートを選択", filetypes=[
                                   ("Text files", "*.txt")])
        # TODO: ファイルコピー・設定反映

    def change_yt_template(self):
        filedialog.askopenfilename(title="YouTube通知テンプレートを選択", filetypes=[
                                   ("Text files", "*.txt")])
        # TODO: ファイルコピー・設定反映

    def change_yt_image(self):
        filedialog.askopenfilename(title="YouTube通知画像を選択", filetypes=[
                                   ("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        # TODO: ファイルコピー・設定反映

    def change_nico_template(self):
        filedialog.askopenfilename(title="ニコニコ通知テンプレートを選択", filetypes=[
                                   ("Text files", "*.txt")])
        # TODO: ファイルコピー・設定反映

    def change_nico_image(self):
        filedialog.askopenfilename(title="ニコニコ通知画像を選択", filetypes=[
                                   ("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        # TODO: ファイルコピー・設定反映

    def change_yt_newvideo_template(self):
        filedialog.askopenfilename(title="YouTube新着動画テンプレートを選択", filetypes=[
                                   ("Text files", "*.txt")])
        # TODO: ファイルコピー・設定反映

    def change_nico_newvideo_template(self):
        filedialog.askopenfilename(title="ニコニコ新着動画テンプレートを選択", filetypes=[
                                   ("Text files", "*.txt")])
        # TODO: ファイルコピー・設定反映

    def save_discord_settings(self):
        """Webhook URL・通知レベル・DISCORD_NOTIFY_ENABLEDをsettings.envに保存"""
        url = self.entry_discord_url.get().strip()
        level = self.combo_discord_level.get().strip()
        enabled = self.var_discord_enabled.get()
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found_url = found_level = found_enabled = False
        for line in lines:
            if line.startswith('discord_error_notifier_url='):
                new_lines.append(f'discord_error_notifier_url={url}\n')
                found_url = True
            elif line.startswith('discord_notify_level='):
                new_lines.append(f'discord_notify_level={level}\n')
                found_level = True
            elif line.startswith('DISCORD_NOTIFY_ENABLED='):
                new_lines.append(f'DISCORD_NOTIFY_ENABLED={str(enabled)}\n')
                found_enabled = True
            else:
                new_lines.append(line)
        if not found_url:
            new_lines.append(f'discord_error_notifier_url={url}\n')
        if not found_level:
            new_lines.append(f'discord_notify_level={level}\n')
        if not found_enabled:
            new_lines.append(f'DISCORD_NOTIFY_ENABLED={str(enabled)}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        # 反映後、再読み込み
        load_dotenv(env_path, override=True)
        self.entry_discord_url.delete(0, tk.END)
        self.entry_discord_url.insert(0, url)
        self.combo_discord_level.set(level)
        self.var_discord_enabled.set(enabled)

    def clear_discord_settings(self):
        """Webhook URL・通知レベル・DISCORD_NOTIFY_ENABLEDを初期化してsettings.envに保存"""
        self.entry_discord_url.delete(0, tk.END)
        self.combo_discord_level.set('CRITICAL')
        self.var_discord_enabled.set(False)
        self.save_discord_settings()
