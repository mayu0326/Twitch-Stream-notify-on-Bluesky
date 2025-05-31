import customtkinter as ctk
import os
from tkinter import filedialog
from PIL import Image, ImageTk

DEFAULT_FONT = ("Yu Gothic UI", 18, "normal")

class YouTubeNoticeFrame(ctk.CTkFrame):
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
        notify_online = get_env('NOTIFY_ON_YT_ONINE', 'False').lower() == 'true'
        notify_newvideo = get_env('NOTIFY_ON_YT_NEWVIDEO', 'False').lower() == 'true'
        tpl_online = get_env('BLUESKY_YT_ONLINE_TEMPLATE_PATH', 'templates/yt_online_template.txt')
        tpl_newvideo = get_env('BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH', 'templates/yt_new_video_template.txt')
        img_path = get_env('BLUESKY_IMAGE_PATH', 'images/noimage.png')
        # 変数
        self.var_online = ctk.BooleanVar(value=notify_online)
        self.var_newvideo = ctk.BooleanVar(value=notify_newvideo)
        self.tpl_online = ctk.StringVar(value=tpl_online)
        self.tpl_newvideo = ctk.StringVar(value=tpl_newvideo)
        self.img_path = ctk.StringVar(value=img_path)
        # UI
        ctk.CTkSwitch(self, text="YouTubeLive：開始通知を送信する", variable=self.var_online, font=DEFAULT_FONT, onvalue=True, offvalue=False).grid(row=0, column=0, sticky="w", pady=5)
        ctk.CTkSwitch(self, text="YouTube動画：動画投稿通知を送信する", variable=self.var_newvideo, font=DEFAULT_FONT, onvalue=True, offvalue=False).grid(row=1, column=0, sticky="w", pady=5)
        ctk.CTkLabel(self, text="放送開始時投稿テンプレート:", font=DEFAULT_FONT).grid(row=2, column=0, sticky="w")
        self.lbl_online_tpl = ctk.CTkLabel(self, text=os.path.basename(self.tpl_online.get()), font=DEFAULT_FONT)
        self.lbl_online_tpl.grid(row=2, column=1, sticky="w")
        ctk.CTkButton(self, text="テンプレート変更...", command=self.change_template_file_online, font=DEFAULT_FONT, width=140).grid(row=3, column=1, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self, text="動画投稿時テンプレート:", font=DEFAULT_FONT).grid(row=4, column=0, sticky="w")
        self.lbl_newvideo_tpl = ctk.CTkLabel(self, text=os.path.basename(self.tpl_newvideo.get()), font=DEFAULT_FONT)
        self.lbl_newvideo_tpl.grid(row=4, column=1, sticky="w")
        ctk.CTkButton(self, text="テンプレート変更...", command=self.change_template_file_newvideo, font=DEFAULT_FONT, width=140).grid(row=5, column=1, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self, text="画像ファイル:", font=DEFAULT_FONT).grid(row=6, column=0, sticky="w")
        self.img_preview = ctk.CTkLabel(self, width=200, height=112.5, text="", fg_color="white")
        self.img_preview.grid(row=7, column=0, rowspan=2, sticky="w", padx=(0, 10), pady=(0, 10))
        self.lbl_img = ctk.CTkLabel(self, text=os.path.basename(self.img_path.get()), font=DEFAULT_FONT)
        self.lbl_img.grid(row=7, column=1, sticky="w", pady=(0, 5))
        ctk.CTkButton(self, text="画像変更...", command=self.change_image_file, font=DEFAULT_FONT, width=140).grid(row=8, column=1, sticky="w", pady=(0, 10))
        ctk.CTkButton(self, text="保存", command=self.save_yt_settings, font=DEFAULT_FONT, width=140).grid(row=9, column=1, sticky="w", pady=(10, 0))
        self.status_label = ctk.CTkLabel(self, text="", font=DEFAULT_FONT)
        self.status_label.grid(row=10, column=0, columnspan=2, sticky="w", pady=(5, 0))
        # traceでラベル・画像プレビューを更新
        self.tpl_online.trace_add('write', lambda *a: self.lbl_online_tpl.configure(text=os.path.basename(self.tpl_online.get())))
        self.tpl_newvideo.trace_add('write', lambda *a: self.lbl_newvideo_tpl.configure(text=os.path.basename(self.tpl_newvideo.get())))
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

    def change_template_file_newvideo(self):
        path = filedialog.askopenfilename(
            title="テンプレートファイルを選択",
            filetypes=[("Text files", "*.txt")],
            initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
        )
        if path:
            self.tpl_newvideo.set(path)

    def change_image_file(self):
        path = filedialog.askopenfilename(
            title="画像ファイルを選択",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")],
            initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), '../images'))
        )
        if path:
            self.img_path.set(path)

    def update_img_label_and_preview(self):
        self.lbl_img.configure(text=os.path.basename(self.img_path.get()))
        try:
            from customtkinter import CTkImage
            img = Image.open(self.img_path.get())
            ctk_img = CTkImage(light_image=img, size=(200, 112.5))
            self.img_preview.configure(image=ctk_img, text="")
            self.img_preview._image = ctk_img
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

    def save_yt_settings(self):
        from tkinter import messagebox
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
        new_lines = []
        found_online = found_newvideo = found_tpl_online = found_tpl_newvideo = found_img = False
        for line in lines:
            if line.startswith('NOTIFY_ON_YT_ONINE='):
                new_lines.append(f'NOTIFY_ON_YT_ONINE={str(self.var_online.get())}\n')
                found_online = True
            elif line.startswith('NOTIFY_ON_YT_NEWVIDEO='):
                new_lines.append(f'NOTIFY_ON_YT_NEWVIDEO={str(self.var_newvideo.get())}\n')
                found_newvideo = True
            elif line.startswith('BLUESKY_YT_ONLINE_TEMPLATE_PATH='):
                new_lines.append(f'BLUESKY_YT_ONLINE_TEMPLATE_PATH={self._to_templates_relative(self.tpl_online.get())}\n')
                found_tpl_online = True
            elif line.startswith('BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH='):
                new_lines.append(f'BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH={self._to_templates_relative(self.tpl_newvideo.get())}\n')
                found_tpl_newvideo = True
            elif line.startswith('BLUESKY_IMAGE_PATH='):
                new_lines.append(f'BLUESKY_IMAGE_PATH={self._to_images_relative(self.img_path.get())}\n')
                found_img = True
            else:
                new_lines.append(line)
        if not found_online:
            new_lines.append(f'NOTIFY_ON_YT_ONINE={str(self.var_online.get())}\n')
        if not found_newvideo:
            new_lines.append(f'NOTIFY_ON_YT_NEWVIDEO={str(self.var_newvideo.get())}\n')
        if not found_tpl_online:
            new_lines.append(f'BLUESKY_YT_ONLINE_TEMPLATE_PATH={self._to_templates_relative(self.tpl_online.get())}\n')
        if not found_tpl_newvideo:
            new_lines.append(f'BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH={self._to_templates_relative(self.tpl_newvideo.get())}\n')
        if not found_img:
            new_lines.append(f'BLUESKY_IMAGE_PATH={self._to_images_relative(self.img_path.get())}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        messagebox.showinfo('保存完了', 'YouTube通知設定を保存しました。')
        self.status_label.configure(text="保存しました")
