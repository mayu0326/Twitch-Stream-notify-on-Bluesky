import customtkinter as ctk
import os
from tkinter import filedialog
from PIL import Image

DEFAULT_FONT = ("Yu Gothic UI", 18, "normal")


class TwitchNoticeFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        # 設定値の初期化
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../settings.env'))
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            def get_env(key, default):
                for line in lines:
                    if line.startswith(key + '='):
                        return line.strip().split('=', 1)[1]
                return default
        else:
            def get_env(key, default):
                return default
        notify_online = get_env('NOTIFY_ON_TWITCH_ONINE', 'False').lower() == 'true'
        notify_offline = get_env('NOTIFY_ON_TWITCH_OFFLINE', 'False').lower() == 'true'
        tpl_online = get_env('BLUESKY_TEMPLATE_PATH', 'templates/twitch_online_template.txt')
        tpl_offline = get_env('BLUESKY_OFFLINE_TEMPLATE_PATH', 'templates/twitch_offline_template.txt')
        img_path = get_env('BLUESKY_IMAGE_PATH', 'images/noimage.png')
        # 変数
        # 通知ON/OFFスイッチ
        self.var_online = ctk.BooleanVar(value=notify_online)
        self.var_offline = ctk.BooleanVar(value=notify_offline)
        self.tpl_online = ctk.StringVar(value=tpl_online)
        self.tpl_offline = ctk.StringVar(value=tpl_offline)
        self.img_path = ctk.StringVar(value=img_path)
        # UI
        ctk.CTkSwitch(self, text="Twitch：放送開始時に通知を送信する", variable=self.var_online, font=DEFAULT_FONT, onvalue=True, offvalue=False).grid(row=0, column=0, sticky="w", pady=5)
        ctk.CTkSwitch(self, text="Twitch：放送終了時に通知を送信する", variable=self.var_offline, font=DEFAULT_FONT, onvalue=True, offvalue=False).grid(row=1, column=0, sticky="w", pady=5)
        ctk.CTkLabel(self, text="放送開始時投稿テンプレート:", font=DEFAULT_FONT).grid(row=2, column=0, sticky="w")
        self.lbl_online_tpl = ctk.CTkLabel(self, text=os.path.basename(self.tpl_online.get()), font=DEFAULT_FONT)
        self.lbl_online_tpl.grid(row=2, column=1, sticky="w")
        ctk.CTkButton(self, text="テンプレート変更...", command=self.change_template_file_online, font=DEFAULT_FONT, width=140).grid(row=3, column=1, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self, text="放送終了時投稿テンプレート:", font=DEFAULT_FONT).grid(row=4, column=0, sticky="w")
        self.lbl_offline_tpl = ctk.CTkLabel(self, text=os.path.basename(self.tpl_offline.get()), font=DEFAULT_FONT)
        self.lbl_offline_tpl.grid(row=4, column=1, sticky="w")
        ctk.CTkButton(self, text="テンプレート変更...", command=self.change_template_file_offline, font=DEFAULT_FONT, width=140).grid(row=5, column=1, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self, text="画像ファイル:", font=DEFAULT_FONT).grid(row=6, column=0, columnspan=2, sticky="w")
        self.img_preview = ctk.CTkLabel(self, width=200, height=112.5, text="", fg_color="white", image=None)
        self.img_preview._image = None  # Prevent garbage collection, 明示的に初期化
        self.img_preview.grid(row=7, column=0, rowspan=2, sticky="w", padx=(0, 10), pady=(0, 10))
        self.lbl_online_img = ctk.CTkLabel(self, text=os.path.basename(self.img_path.get()), font=DEFAULT_FONT)
        self.lbl_online_img.grid(row=7, column=1, sticky="w", pady=(0, 5))
        ctk.CTkButton(self, text="画像変更...", command=self.change_image_file, font=DEFAULT_FONT, width=140).grid(row=8, column=1, sticky="w", pady=(0, 10))
        ctk.CTkButton(self, text="保存", command=self.save_twitch_settings, font=DEFAULT_FONT, width=140).grid(row=9, column=1, sticky="w", pady=(10, 0))
        self.status_label = ctk.CTkLabel(self, text="", font=DEFAULT_FONT)
        self.status_label.grid(row=10, column=0, columnspan=2, sticky="w", pady=(5, 0))
        # traceでラベル・画像プレビューを更新
        self.tpl_online.trace_add('write', lambda *a: self.lbl_online_tpl.configure(text=os.path.basename(self.tpl_online.get())))
        self.tpl_offline.trace_add('write', lambda *a: self.lbl_offline_tpl.configure(text=os.path.basename(self.tpl_offline.get())))
        self.img_path.trace_add('write', lambda *a: self.update_img_label_and_preview())
        self.update_img_label_and_preview()

    def change_template_file_online(self):
        path = filedialog.askopenfilename(
            title="テンプレートファイルを選択",
            filetypes=[("Text files", "*.txt")],
            initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
        )
        if path:
            self.tpl_online.set(path)

    def change_template_file_offline(self):
        path = filedialog.askopenfilename(
            title="テンプレートファイルを選択",
            filetypes=[("Text files", "*.txt")],
            initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
        )
        if path:
            self.tpl_offline.set(path)

    def change_image_file(self):
        path = filedialog.askopenfilename(
            title="画像ファイルを選択",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")],
            initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), '../images'))
        )
        if path:
            self.img_path.set(path)

    def update_img_label_and_preview(self):
        self.lbl_online_img.configure(text=os.path.basename(self.img_path.get()))
        try:
            from customtkinter import CTkImage
            img = Image.open(self.img_path.get())
            # PIL.Image.open() で開いた画像をそのまま渡す（thumbnail等は不要）
            ctk_img = CTkImage(light_image=img, size=(200, 112.5))
            self.img_preview.configure(image=ctk_img, text="")
            self.img_preview._image = ctk_img  # Prevent garbage collection (正しい属性名)
        except Exception:
            self.img_preview.configure(image=None, text="(画像プレビューなし)")

    def _to_templates_relative(self, path):
        if not path:
            return path
        abs_templates = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
        abs_path = os.path.abspath(path)
        if abs_path.startswith(abs_templates):
            rel = os.path.relpath(abs_path, os.path.dirname(__file__))
            rel = rel.replace('..\\', '').replace('../', '')
            return rel
        return path

    def _to_images_relative(self, path):
        if not path:
            return path
        abs_images = os.path.abspath(os.path.join(os.path.dirname(__file__), '../images'))
        abs_path = os.path.abspath(path)
        if abs_path.startswith(abs_images):
            rel = os.path.relpath(abs_path, os.path.dirname(__file__))
            rel = rel.replace('..\\', '').replace('../', '')
            return rel
        return path

    def save_twitch_settings(self):
        from tkinter import messagebox
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
        new_lines = []
        found_online = found_offline = found_tpl_online = found_tpl_offline = found_img = False
        for line in lines:
            if line.startswith('NOTIFY_ON_TWITCH_ONINE='):
                new_lines.append(f'NOTIFY_ON_TWITCH_ONINE={str(self.var_online.get())}\n')
                found_online = True
            elif line.startswith('NOTIFY_ON_TWITCH_OFFLINE='):
                new_lines.append(f'NOTIFY_ON_TWITCH_OFFLINE={str(self.var_offline.get())}\n')
                found_offline = True
            elif line.startswith('BLUESKY_TEMPLATE_PATH='):
                new_lines.append(f'BLUESKY_TEMPLATE_PATH={self._to_templates_relative(self.tpl_online.get())}\n')
                found_tpl_online = True
            elif line.startswith('BLUESKY_OFFLINE_TEMPLATE_PATH='):
                new_lines.append(f'BLUESKY_OFFLINE_TEMPLATE_PATH={self._to_templates_relative(self.tpl_offline.get())}\n')
                found_tpl_offline = True
            elif line.startswith('BLUESKY_IMAGE_PATH='):
                new_lines.append(f'BLUESKY_IMAGE_PATH={self._to_images_relative(self.img_path.get())}\n')
                found_img = True
            else:
                new_lines.append(line)
        if not found_online:
            new_lines.append(f'NOTIFY_ON_TWITCH_ONINE={str(self.var_online.get())}\n')
        if not found_offline:
            new_lines.append(f'NOTIFY_ON_TWITCH_OFFLINE={str(self.var_offline.get())}\n')
        if not found_tpl_online:
            new_lines.append(f'BLUESKY_TEMPLATE_PATH={self._to_templates_relative(self.tpl_online.get())}\n')
        if not found_tpl_offline:
            new_lines.append(f'BLUESKY_OFFLINE_TEMPLATE_PATH={self._to_templates_relative(self.tpl_offline.get())}\n')
        if not found_img:
            new_lines.append(f'BLUESKY_IMAGE_PATH={self._to_images_relative(self.img_path.get())}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        messagebox.showinfo('保存完了', 'Twitch通知設定を保存しました。')
        self.status_label.configure(text="保存しました")
