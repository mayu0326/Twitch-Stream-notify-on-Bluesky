import tkinter as tk
from tkinter import ttk, filedialog
import os
from dotenv import load_dotenv
from PIL import Image, ImageTk


class YouTubeNoticeFrame(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        load_dotenv(env_path)
        notify_online = os.getenv(
            'NOTIFY_ON_YOUTUBE_ONLINE', 'False').lower() == 'true'
        notify_newvideo = os.getenv(
            'NOTIFY_ON_YOUTUBE_NEW_VIDEO', 'False').lower() == 'true'
        tpl_online = os.getenv(
            'BLUESKY_YT_ONLINE_TEMPLATE_PATH', 'templates/yt_online_template.txt')
        tpl_newvideo = os.getenv(
            'BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH', 'templates/yt_new_video_template.txt')
        img_path = os.getenv('BLUESKY_IMAGE_PATH', 'images/noimage.png')
        self.var_yt_online = tk.BooleanVar(value=notify_online)
        self.var_yt_newvideo = tk.BooleanVar(value=notify_newvideo)
        self.tpl_online = tk.StringVar(value=tpl_online)
        self.tpl_newvideo = tk.StringVar(value=tpl_newvideo)
        self.img_path = tk.StringVar(value=img_path)
        ttk.Checkbutton(self, text="放送開始時に投稿", variable=self.var_yt_online,
                        style="Big.TCheckbutton").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(self, text="新着動画投稿時に投稿", variable=self.var_yt_newvideo,
                        style="Big.TCheckbutton").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(self, text="配信開始時の投稿テンプレート:", style="Big.TLabel").grid(
            row=2, column=0, sticky=tk.W)

        def update_tpl_yt_online_label():
            lbl_yt_tpl.config(text=os.path.basename(self.tpl_online.get()))
        lbl_yt_tpl = ttk.Label(self, text=os.path.basename(
            self.tpl_online.get()), style="Big.TLabel")
        lbl_yt_tpl.grid(row=2, column=1, sticky=tk.W)
        self.tpl_online.trace_add(
            'write', lambda *a: update_tpl_yt_online_label())
        update_tpl_yt_online_label()
        ttk.Button(self, text="テンプレート変更...", command=self.change_template_file_online,
                   style="Big.TButton", width=18).grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        ttk.Label(self, text="配信開始投稿時に使用する画像ファイル:", style="Big.TLabel").grid(
            row=4, column=0, columnspan=2, sticky=tk.W)
        self.img_preview = tk.Label(
            self, width=120, height=90, relief=tk.SOLID, bg='white')
        self.img_preview.grid(row=5, column=0, rowspan=2,
                              sticky=tk.W+tk.N+tk.S, padx=(0, 10), pady=(0, 10))

        def update_img_label():
            lbl_yt_img.config(text=os.path.basename(self.img_path.get()))
        lbl_yt_img = ttk.Label(self, text=os.path.basename(
            self.img_path.get()), style="Big.TLabel")
        lbl_yt_img.grid(row=5, column=1, sticky=tk.W, pady=(0, 5))
        self.img_path.trace_add('write', lambda *a: update_img_label())
        update_img_label()
        ttk.Button(self, text="画像変更...", command=self.change_image_file,
                   style="Big.TButton", width=18).grid(row=6, column=1, sticky=tk.W, pady=(0, 10))

        def update_img_preview(*args):
            path = self.img_path.get()
            try:
                img = Image.open(path)
                img.thumbnail((120, 90))
                self._imgtk = ImageTk.PhotoImage(img)
                self.img_preview.configure(image=self._imgtk)
            except Exception:
                self.img_preview.configure(image='')
        self.img_path.trace_add('write', lambda *a: update_img_preview())
        update_img_preview()
        ttk.Label(self, text="新着動画投稿時の投稿テンプレート:", style="Big.TLabel").grid(
            row=8, column=0, sticky=tk.W)

        def update_tpl_newvideo_label():
            lbl_yt_newvideo_tpl.config(
                text=os.path.basename(self.tpl_newvideo.get()))
        lbl_yt_newvideo_tpl = ttk.Label(self, text=os.path.basename(
            self.tpl_newvideo.get()), style="Big.TLabel")
        lbl_yt_newvideo_tpl.grid(row=8, column=1, sticky=tk.W)
        self.tpl_newvideo.trace_add(
            'write', lambda *a: update_tpl_newvideo_label())
        update_tpl_newvideo_label()
        ttk.Button(self, text="テンプレート変更...", command=self.change_template_file_newvideo,
                   style="Big.TButton", width=18).grid(row=9, column=1, sticky=tk.W, pady=(0, 10))
        ttk.Button(self, text="保存", command=self.save_youtube_settings,
                   style="Big.TButton", width=18).grid(row=10, column=1, sticky=tk.W, pady=(10, 0))

    def change_template_file_online(self):
        path = filedialog.askopenfilename(
            title="テンプレートファイルを選択", filetypes=[("Text files", "*.txt")], initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates')))
        if path:
            self.tpl_online.set(path)

    def change_template_file_newvideo(self):
        path = filedialog.askopenfilename(
            title="テンプレートファイルを選択", filetypes=[("Text files", "*.txt")], initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates')))
        if path:
            self.tpl_newvideo.set(path)

    def change_image_file(self):
        path = filedialog.askopenfilename(title="画像ファイルを選択", filetypes=[
                                          ("Image files", "*.png;*.jpg;*.jpeg;*.gif")], initialdir=os.path.abspath(os.path.join(os.path.dirname(__file__), '../images')))
        if path:
            self.img_path.set(path)

    def _to_templates_relative(self, path):
        """
        templates/配下なら相対パス(templates/以降)を返す。そうでなければそのまま返す。
        """
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
        """
        images/配下なら相対パス(images/以降)を返す。そうでなければそのまま返す。
        """
        if not path:
            return path
        abs_images = os.path.abspath(os.path.join(os.path.dirname(__file__), '../images'))
        abs_path = os.path.abspath(path)
        if abs_path.startswith(abs_images):
            rel = os.path.relpath(abs_path, os.path.dirname(__file__))
            rel = rel.replace('..\\', '').replace('../', '')
            return rel
        return path

    def save_youtube_settings(self):
        from tkinter import messagebox
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found_online = found_newvideo = found_tpl_online = found_tpl_newvideo = found_img = False
        for line in lines:
            if line.startswith('NOTIFY_ON_YOUTUBE_ONLINE='):
                new_lines.append(
                    f'NOTIFY_ON_YOUTUBE_ONLINE={str(self.var_yt_online.get())}\n')
                found_online = True
            elif line.startswith('NOTIFY_ON_YOUTUBE_NEW_VIDEO='):
                new_lines.append(
                    f'NOTIFY_ON_YOUTUBE_NEW_VIDEO={str(self.var_yt_newvideo.get())}\n')
                found_newvideo = True
            elif line.startswith('BLUESKY_YT_ONLINE_TEMPLATE_PATH='):
                new_lines.append(
                    f'BLUESKY_YT_ONLINE_TEMPLATE_PATH={self._to_templates_relative(self.tpl_online.get())}\n')
                found_tpl_online = True
            elif line.startswith('BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH='):
                new_lines.append(
                    f'BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH={self._to_templates_relative(self.tpl_newvideo.get())}\n')
                found_tpl_newvideo = True
            elif line.startswith('BLUESKY_IMAGE_PATH='):
                new_lines.append(f'BLUESKY_IMAGE_PATH={self._to_images_relative(self.img_path.get())}\n')
                found_img = True
            else:
                new_lines.append(line)
        if not found_online:
            new_lines.append(
                f'NOTIFY_ON_YOUTUBE_ONLINE={str(self.var_yt_online.get())}\n')
        if not found_newvideo:
            new_lines.append(
                f'NOTIFY_ON_YOUTUBE_NEW_VIDEO={str(self.var_yt_newvideo.get())}\n')
        if not found_tpl_online:
            new_lines.append(
                f'BLUESKY_YT_ONLINE_TEMPLATE_PATH={self._to_templates_relative(self.tpl_online.get())}\n')
        if not found_tpl_newvideo:
            new_lines.append(
                f'BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH={self._to_templates_relative(self.tpl_newvideo.get())}\n')
        if not found_img:
            new_lines.append(f'BLUESKY_IMAGE_PATH={self._to_images_relative(self.img_path.get())}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        load_dotenv(env_path, override=True)
        self.var_yt_online.set(
            os.getenv('NOTIFY_ON_YOUTUBE_ONLINE', 'False').lower() == 'true')
        self.var_yt_newvideo.set(
            os.getenv('NOTIFY_ON_YOUTUBE_NEW_VIDEO', 'False').lower() == 'true')
        self.tpl_online.set(os.getenv(
            'BLUESKY_YT_ONLINE_TEMPLATE_PATH', 'templates/yt_online_template.txt'))
        self.tpl_newvideo.set(os.getenv(
            'BLUESKY_YT_NEW_VIDEO_TEMPLATE_PATH', 'templates/yt_new_video_template.txt'))
        self.img_path.set(
            os.getenv('BLUESKY_IMAGE_PATH', 'images/noimage.png'))
        messagebox.showinfo('保存完了', 'YouTube通知設定を保存しました。')
