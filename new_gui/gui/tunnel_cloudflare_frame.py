import os
import customtkinter as ctk
import tkinter.messagebox as messagebox

DEFAULT_FONT = "Yu Gothic UI", 15, "normal"

try:
    import pyperclip
    _pyperclip_available = True
except ImportError:
    _pyperclip_available = False

class TunnelCloudflareFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.font =DEFAULT_FONT
        self.cloudflared_path = ctk.StringVar(value=self._get_default_cloudflared())
        self.config_path = ctk.StringVar(value=self._get_default_config())
        self.tunnel_name = ctk.StringVar(value="my-tunnel")
        self.generated_cmd = ctk.StringVar()
        self.url_var = ctk.StringVar(value=self._load_permanent_url())
        self._load_tunnel_name()
        # --- 中央寄せ用サブフレーム ---
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(fill="both", expand=True)
        self._create_widgets(center_frame)
        self._update_cmd()

    def _get_default_cloudflared(self):
        default = r"C:/Program Files (x86)/cloudflared/cloudflared.exe"
        return default if os.path.exists(default) else ""

    def _get_default_config(self):
        userprofile = os.environ.get('USERPROFILE', 'C:/Users')
        default = os.path.join(userprofile, '.cloudflared', 'config.yml')
        return default if os.path.exists(default) else ""

    def _load_tunnel_name(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        if not os.path.exists(env_path):
            return
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('TUNNEL_NAME='):
                    self.tunnel_name.set(line.strip().split('=', 1)[1])
                    break

    def _load_permanent_url(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        if not os.path.exists(env_path):
            return ''
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('WEBHOOK_CALLBACK_URL_PERMANENT='):
                    return line.strip().split('=', 1)[1]
        return ''

    def _create_widgets(self, parent):
        ctk.CTkLabel(parent, text="cloudflared.exeの場所:", font=self.font, anchor="w").grid(row=0, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.cloudflared_path, font=self.font, width=320).grid(row=0, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="参照", command=self._select_cloudflared, font=self.font).grid(row=0, column=2, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="config.ymlの場所:", font=self.font, anchor="w").grid(row=1, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.config_path, font=self.font, width=320).grid(row=1, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="参照", command=self._select_config, font=self.font).grid(row=1, column=2, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="トンネル名:", font=self.font, anchor="w").grid(row=2, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.tunnel_name, font=self.font, width=320).grid(row=2, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkLabel(parent, text="cloudflared起動コマンド:", font=self.font, anchor="w").grid(row=3, column=0, sticky='w', pady=(10,0), padx=(10,0))
        ctk.CTkEntry(parent, textvariable=self.generated_cmd, font=self.font, width=320, state="readonly").grid(row=3, column=1, padx=(0,10), pady=(10,0))
        ctk.CTkButton(parent, text="保存", command=self._save_cmd, font=self.font).grid(row=4, column=1, pady=(20,0))

    def _to_relative_path(self, abspath):
        # プロジェクトルート（settings.envのあるディレクトリ）からの相対パスに変換
        if not abspath:
            return ''
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        try:
            rel = os.path.relpath(abspath, root)
            return rel if not rel.startswith('..') else abspath
        except Exception:
            return abspath

    def _update_cmd(self):
        exe = self.cloudflared_path.get()
        conf = self.config_path.get()
        tunnel = self.tunnel_name.get()
        exe_rel = self._to_relative_path(exe)
        conf_rel = self._to_relative_path(conf)
        if exe_rel and conf_rel and tunnel:
            cmd = f'cloudflared.exe tunnel --config {conf_rel} run {tunnel}'
            self.generated_cmd.set(cmd)
        else:
            self.generated_cmd.set("")

    def _select_cloudflared(self):
        import tkinter.filedialog as fd
        path = fd.askopenfilename(
            initialdir=self._cloudflared_dir,
            filetypes=[("実行ファイル", "*.exe"), ("すべてのファイル", "*.*")],
            title="cloudflared.exeを選択してください"
        )
        if path:
            rel_path = self._to_relative_path(path)
            self.cloudflared_path.set(rel_path)
            self._update_cmd()

    def _select_config(self):
        import tkinter.filedialog as fd
        path = fd.askopenfilename(
            initialdir=self._config_dir,
            filetypes=[("YAMLファイル", "*.yml;*.yaml"), ("すべてのファイル", "*.*")],
            title="config.ymlを選択してください"
        )
        if path:
            rel_path = self._to_relative_path(path)
            self.config_path.set(rel_path)
            self._update_cmd()

    def _save_cmd(self):
        self._update_cmd()
        cmd = self.generated_cmd.get()
        tunnel = self.tunnel_name.get()
        url = self.url_var.get()
        if not cmd or not tunnel:
            messagebox.showerror("エラー", "cloudflared.exe、config.yml、トンネル名を指定してください。")
            return
        env_path = 'settings.env'
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        found_cmd = found_name = found_url = False
        for line in lines:
            if line.startswith('TUNNEL_CMD='):
                new_lines.append(f'TUNNEL_CMD={cmd}\n')
                found_cmd = True
            elif line.startswith('TUNNEL_NAME='):
                new_lines.append(f'TUNNEL_NAME={tunnel}\n')
                found_name = True
            elif line.startswith('WEBHOOK_CALLBACK_URL_PERMANENT='):
                new_lines.append(f'WEBHOOK_CALLBACK_URL_PERMANENT={url}\n')
                found_url = True
            else:
                new_lines.append(line)
        if not found_cmd:
            new_lines.append(f'TUNNEL_CMD={cmd}\n')
        if not found_name:
            new_lines.append(f'TUNNEL_NAME={tunnel}\n')
        if not found_url:
            new_lines.append(f'WEBHOOK_CALLBACK_URL_PERMANENT={url}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        messagebox.showinfo("保存完了", "TUNNEL_CMD, TUNNEL_NAME, 公開URLを保存しました。")

    def _copy_url(self):
        url = self.url_var.get()
        if not url:
            messagebox.showwarning("URL未入力", "公開URLが空です。")
            return
        if _pyperclip_available:
            pyperclip.copy(url)
            messagebox.showinfo("コピー完了", "公開URLをクリップボードにコピーしました。")
        else:
            messagebox.showwarning("pyperclip未インストール", "pyperclipが未インストールのためコピーできません。\n\n'pip install pyperclip'でインストールしてください。")
