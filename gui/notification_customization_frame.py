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

        # --- ログ/コンソール設定タブ ---
        from logging_console_frame import LoggingConsoleFrame
        log_console_frame = LoggingConsoleFrame(notebook)
        notebook.add(log_console_frame, text="ログ/コンソール設定")
        # --- Discordタブ（分割後） ---
        from discord_notification_frame import DiscordNotificationFrame
        discord_frame = DiscordNotificationFrame(notebook)
        notebook.add(discord_frame, text="Discord通知設定")
        # Discord通知設定のUI・保存処理はdiscord_notification_frame.pyに完全移行済み
        # ここでself.save_discord_settings等は不要

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
        # 放送終了時の投稿テンプレートラベル
        # --- ここから下（Twitchの放送終了時テンプレートUI）はtwitch_notice_frame.pyへ移行済みのため削除 ---
        # ttk.Label(twitch_frame, text="放送終了時の投稿テンプレート:", style="Big.TLabel").grid(
        #     row=7, column=0, sticky=tk.W)
        # lbl_offline_tpl = ttk.Label(
        #     twitch_frame, text=os.path.basename(twitch_frame.tpl_offline.get()), style="Big.TLabel")
        # lbl_offline_tpl.grid(row=7, column=1, sticky=tk.W)
        # twitch_frame.tpl_offline.trace_add(
        #     'write', lambda *a: lbl_offline_tpl.config(text=os.path.basename(twitch_frame.tpl_offline.get())))
        # lbl_offline_tpl.config(text=os.path.basename(
        #     twitch_frame.tpl_offline.get()))
        # 放送終了時テンプレート変更ボタン
        # ttk.Button(twitch_frame, text="テンプレート変更...", command=lambda: cls.change_template_file(twitch_frame.tpl_offline), style="Big.TButton", width=18).grid(
        #     row=8, column=1, sticky=tk.W, pady=(0, 10))
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
        # --- この関数はYouTubeNoticeFrameへ完全移行のため削除 ---
        pass

    @staticmethod
    def save_youtube_settings(frame):
        # --- この関数はYouTubeNoticeFrameへ完全移行のため削除 ---
        pass

    @classmethod
    def create_nico_tab(cls, notebook):
        # --- この関数はNiconicoNoticeFrameへ完全移行のため削除 ---
        pass

    @staticmethod
    def save_nico_settings(frame):
        # --- この関数はNiconicoNoticeFrameへ完全移行のため削除 ---
        pass
    # --- YouTube/ニコニコ個別テンプレート処理は各notice_frame.pyへ移植済み ---
