"""
初期設定ウィザード（複数ステップ、バリデーション付き）
"""
import tkinter as tk
from tkinter import ttk, messagebox


class SetupWizard(tk.Toplevel):
    def __init__(self, master=None, on_finish=None):
        super().__init__(master)
        self.title("StreamNotify on Bluesky 初期設定ウィザード")
        self.geometry("500x350")
        self.resizable(False, False)
        self.on_finish = on_finish
        self.current_step = 0
        # ステップ構成を要望通りに細分化
        self.steps = [
            self.step_intro,
            self.step_twitch_account,
            self.step_webhook,
            self.step_bluesky_account,
            self.step_youtube_account,
            self.step_niconico_account,
            self.step_service_notify,
            self.step_tunnel_settings,  # 追加: トンネル通信設定
            self.step_summary,          # 追加: 最終確認
        ]
        self.vars = {}
        self.create_widgets()
        self.show_step(0)
        # ウィンドウの×ボタン押下時にも on_finish を呼ぶ
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_cancel(self):
        self.destroy()
        # 終了時はメイン画面を開かず、アプリ全体を終了
        import sys
        sys.exit(0)

    def create_widgets(self):
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        btn_font = ("Meiryo", 12, "bold")
        # ボタン用のフレームを下部中央に配置（fill=tk.Xで横幅いっぱいに）
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side=tk.BOTTOM, pady=18, fill=tk.X)
        # 中央寄せ用の中間フレーム
        self.inner_button_frame = ttk.Frame(self.button_frame)
        self.inner_button_frame.pack(expand=True)
        # ボタンはinner_button_frameを親にして生成
        self.btn_prev = ttk.Button(
            self.inner_button_frame, text="前へ", command=self.prev_step)
        self.btn_prev.configure(width=10)
        self.btn_next = ttk.Button(
            self.inner_button_frame, text="次へ", command=self.next_step)
        self.btn_next.configure(width=10)
        self.btn_skip = ttk.Button(
            self.inner_button_frame, text="スキップ", command=self.skip_step)
        self.btn_skip.configure(width=10)
        self.btn_cancel = ttk.Button(
            self.inner_button_frame, text="キャンセル", command=self._on_cancel)
        self.btn_cancel.configure(width=10)
        for btn in [self.btn_prev, self.btn_next, self.btn_skip, self.btn_cancel]:
            btn.configure(style="Big.TButton")
        style = ttk.Style()
        style.configure("Big.TButton", font=btn_font, padding=8)
        # 初期表示はshow_stepで制御

    def show_step(self, idx):
        for widget in self.frame.winfo_children():
            widget.destroy()
        # ボタンはdestroyせず、pack_forgetで非表示に
        for btn in [self.btn_prev, self.btn_next, self.btn_skip, self.btn_cancel]:
            btn.pack_forget()
        self.current_step = idx
        self.steps[idx]()
        self.btn_prev.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        # 1ステップ目（idx==0）: 前へ・キャンセル・次へ
        if idx == 0:
            self.btn_prev.pack(in_=self.inner_button_frame,
                               side=tk.LEFT, padx=12)
            self.btn_cancel.pack(
                in_=self.inner_button_frame, side=tk.LEFT, padx=12)
            self.btn_next.pack(in_=self.inner_button_frame,
                               side=tk.LEFT, padx=12)
        # 2〜8ステップ目: 前へ・次へ・スキップ
        elif 1 <= idx <= 7:
            self.btn_prev.pack(in_=self.inner_button_frame,
                               side=tk.LEFT, padx=12)
            self.btn_next.pack(in_=self.inner_button_frame,
                               side=tk.LEFT, padx=12)
            self.btn_skip.pack(in_=self.inner_button_frame,
                               side=tk.LEFT, padx=12)
        # 9ステップ目: 前へ・ファイルを作成
        elif idx == 8:
            self.btn_prev.pack(in_=self.inner_button_frame,
                               side=tk.LEFT, padx=12)
            self.btn_next.pack(in_=self.inner_button_frame,
                               side=tk.LEFT, padx=12)
        # ボタンテキスト切り替え
        if idx == len(self.steps) - 1:
            self.btn_next.config(text="ファイルを作成")
        else:
            self.btn_next.config(text="次へ")

    def skip_step(self):
        # 2〜8ステップ目のみ有効
        if 1 <= self.current_step <= 7:
            # 入力内容を破棄
            step_vars = [
                ['twitch_id', 'twitch_secret'],
                ['webhook_url'],
                ['bsky_user', 'bsky_pass'],
                ['yt_api_key', 'yt_channel_id'],
                ['nico_user_id'],
                ['notify_twitch_online', 'notify_twitch_offline',
                    'notify_yt_online', 'notify_yt_video', 'notify_nico_online', 'notify_nico_video'],
                ['tunnel_cmd'],
            ]
            idx = self.current_step - 1
            if 0 <= idx < len(step_vars):
                for k in step_vars[idx]:
                    if k in self.vars:
                        del self.vars[k]
            self.show_step(self.current_step + 1)

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def next_step(self):
        # 2〜8ステップ目はバリデーション必須
        if 1 <= self.current_step <= 7:
            if not self.validate_step():
                return
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.save_settings()
            # self.destroy() や self.on_finish() はsave_settings内でポップアップのOK/バツで呼ぶ

    def step_intro(self):
        ttk.Label(self.frame, text="StreamNotify on Bluesky 初期設定ウィザード",
                  font=("Meiryo", 14, "bold")).pack(anchor=tk.W, pady=10)
        ttk.Label(
            self.frame,
            text="このセットアップウィザードでは、\n各種サービスのアカウント、サービスごとの通知可否、\nトンネル通信機能のみを設定します。\nそれ以外の設定は、\nファイル作成後に開くメイン画面から設定してください。",
            font=(
                "Meiryo",
                10),
            justify="left").pack(
            anchor=tk.W,
            pady=10)

    def step_twitch_account(self):
        ttk.Label(self.frame, text="Twitchアカウント設定", font=(
            "Meiryo", 12, "bold")).pack(anchor=tk.W, pady=5)
        self.vars['twitch_id'] = self.vars.get('twitch_id', tk.StringVar())
        self.vars['twitch_secret'] = self.vars.get(
            'twitch_secret', tk.StringVar())
        ttk.Label(self.frame, text="TwitchクライアントID").pack(anchor=tk.W)
        ttk.Entry(self.frame, textvariable=self.vars['twitch_id']).pack(
            fill=tk.X)
        ttk.Label(self.frame, text="Twitchクライアントシークレット").pack(anchor=tk.W)
        ttk.Entry(
            self.frame, textvariable=self.vars['twitch_secret'], show='*').pack(fill=tk.X)

    def step_webhook(self):
        ttk.Label(self.frame, text="TwitchWebhookアカウント設定", font=(
            "Meiryo", 12, "bold")).pack(anchor=tk.W, pady=5)
        self.vars['webhook_url'] = self.vars.get('webhook_url', tk.StringVar())
        ttk.Label(self.frame, text="WebhookコールバックURL").pack(anchor=tk.W)
        ttk.Entry(self.frame, textvariable=self.vars['webhook_url']).pack(
            fill=tk.X)

    def step_bluesky_account(self):
        ttk.Label(self.frame, text="Blueskyアカウント設定", font=(
            "Meiryo", 12, "bold")).pack(anchor=tk.W, pady=5)
        self.vars['bsky_user'] = self.vars.get('bsky_user', tk.StringVar())
        self.vars['bsky_pass'] = self.vars.get('bsky_pass', tk.StringVar())
        ttk.Label(self.frame, text="Blueskyユーザー名").pack(anchor=tk.W)
        ttk.Entry(self.frame, textvariable=self.vars['bsky_user']).pack(
            fill=tk.X)
        ttk.Label(self.frame, text="Blueskyアプリパスワード").pack(anchor=tk.W)
        ttk.Entry(
            self.frame, textvariable=self.vars['bsky_pass'], show='*').pack(fill=tk.X)

    def step_youtube_account(self):
        ttk.Label(self.frame, text="YouTubeアカウント設定", font=(
            "Meiryo", 12, "bold")).pack(anchor=tk.W, pady=5)
        self.vars['yt_api_key'] = self.vars.get('yt_api_key', tk.StringVar())
        self.vars['yt_channel_id'] = self.vars.get(
            'yt_channel_id', tk.StringVar())
        ttk.Label(self.frame, text="YouTube APIキー").pack(anchor=tk.W)
        ttk.Entry(self.frame, textvariable=self.vars['yt_api_key']).pack(
            fill=tk.X)
        ttk.Label(self.frame, text="YouTubeチャンネルID").pack(anchor=tk.W)
        ttk.Entry(self.frame, textvariable=self.vars['yt_channel_id']).pack(
            fill=tk.X)

    def step_niconico_account(self):
        ttk.Label(self.frame, text="ニコニコアカウント設定", font=(
            "Meiryo", 12, "bold")).pack(anchor=tk.W, pady=5)
        self.vars['nico_user_id'] = self.vars.get(
            'nico_user_id', tk.StringVar())
        ttk.Label(self.frame, text="ニコニコユーザーID").pack(anchor=tk.W)
        ttk.Entry(self.frame, textvariable=self.vars['nico_user_id']).pack(
            fill=tk.X)

    def step_service_notify(self):
        label_font = ("Meiryo", 12, "bold")
        item_font = ("Meiryo", 9)
        # 通知設定用変数を必ず初期化
        for key in [
            'notify_twitch_online', 'notify_twitch_offline',
            'notify_yt_online', 'notify_yt_video',
                'notify_nico_online', 'notify_nico_video']:
            self.vars[key] = self.vars.get(key, tk.BooleanVar())
        # 見出しを上に詰める
        ttk.Label(self.frame, text="サービスごとの通知設定", font=label_font).pack(
            anchor=tk.W, pady=(2, 4))
        # グリッド配置用フレーム（右寄せ＆横幅活用）
        grid_frame = ttk.Frame(self.frame)
        grid_frame.pack(anchor=tk.N, pady=2, padx=24, fill=tk.X, expand=True)
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        # 2列3行で配置
        # 1列目
        ttk.Label(grid_frame, text="Twitch：放送開始通知", font=item_font).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 24), pady=2)
        ttk.Checkbutton(
            grid_frame,
            text="通知する",
            variable=self.vars['notify_twitch_online'],
            style="BigCheck.TCheckbutton").grid(
            row=1,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                24),
            pady=2)
        ttk.Label(grid_frame, text="YouTube：放送開始通知", font=item_font).grid(
            row=2, column=0, sticky=tk.W, padx=(0, 24), pady=2)
        ttk.Checkbutton(
            grid_frame,
            text="通知する",
            variable=self.vars['notify_yt_online'],
            style="BigCheck.TCheckbutton").grid(
            row=3,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                24),
            pady=2)
        ttk.Label(grid_frame, text="ニコニコ：放送開始通知", font=item_font).grid(
            row=4, column=0, sticky=tk.W, padx=(0, 24), pady=2)
        ttk.Checkbutton(
            grid_frame,
            text="通知する",
            variable=self.vars['notify_nico_online'],
            style="BigCheck.TCheckbutton").grid(
            row=5,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                24),
            pady=2)
        # 2列目
        ttk.Label(grid_frame, text="Twitch：放送終了通知", font=item_font).grid(
            row=0, column=1, sticky=tk.W, padx=(0, 0), pady=2)
        ttk.Checkbutton(
            grid_frame,
            text="通知する",
            variable=self.vars['notify_twitch_offline'],
            style="BigCheck.TCheckbutton").grid(
            row=1,
            column=1,
            sticky=tk.W,
            padx=(
                0,
                0),
            pady=2)
        ttk.Label(grid_frame, text="YouTube：動画投稿通知", font=item_font).grid(
            row=2, column=1, sticky=tk.W, padx=(0, 0), pady=2)
        ttk.Checkbutton(
            grid_frame,
            text="通知する",
            variable=self.vars['notify_yt_video'],
            style="BigCheck.TCheckbutton").grid(
            row=3,
            column=1,
            sticky=tk.W,
            padx=(
                0,
                0),
            pady=2)
        ttk.Label(grid_frame, text="ニコニコ：動画投稿通知", font=item_font).grid(
            row=4, column=1, sticky=tk.W, padx=(0, 0), pady=2)
        ttk.Checkbutton(
            grid_frame,
            text="通知する",
            variable=self.vars['notify_nico_video'],
            style="BigCheck.TCheckbutton").grid(
            row=5,
            column=1,
            sticky=tk.W,
            padx=(
                0,
                0),
            pady=2)
        # チェックボックスのフォント拡大スタイル
        style = ttk.Style()
        style.configure("BigCheck.TCheckbutton", font=item_font, padding=6)

    def step_tunnel_settings(self):
        ttk.Label(
            self.frame,
            text="トンネル通信設定",
            font=(
                "Meiryo",
                12,
                "bold")).pack(
            anchor=tk.W,
            pady=5)
        # サービス選択
        if 'tunnel_service' not in self.vars:
            self.vars['tunnel_service'] = tk.StringVar(value="cloudflare")
        services = [
            ("Cloudflare Tunnel", "cloudflare"),
            ("ngrok", "ngrok"),
            ("localtunnel", "localtunnel"),
            ("カスタム", "custom")
        ]
        radio_frame = ttk.Frame(self.frame)
        radio_frame.pack(anchor=tk.W, pady=(0, 8))
        for i, (label, value) in enumerate(services):
            ttk.Radiobutton(
                radio_frame,
                text=label,
                variable=self.vars['tunnel_service'],
                value=value,
                style="TRadiobutton",
                command=self._update_tunnel_service_fields).grid(
                row=0,
                column=i,
                padx=8)
        # サービスごとの入力欄
        self.tunnel_fields_area = ttk.Frame(self.frame)
        self.tunnel_fields_area.pack(fill=tk.X, expand=True)
        self._update_tunnel_service_fields()

    def _update_tunnel_service_fields(self):
        for child in self.tunnel_fields_area.winfo_children():
            child.destroy()
        service = self.vars['tunnel_service'].get()
        font10 = ("Meiryo", 10)
        if service == "cloudflare":
            if 'tunnel_cmd' not in self.vars:
                self.vars['tunnel_cmd'] = tk.StringVar()
            ttk.Label(
                self.tunnel_fields_area,
                text="Cloudflare Tunnel起動コマンド (TUNNEL_CMD)").pack(
                anchor=tk.W)
            ttk.Entry(
                self.tunnel_fields_area,
                textvariable=self.vars['tunnel_cmd'],
                width=48).pack(
                fill=tk.X)
            ttk.Label(
                self.tunnel_fields_area,
                text='コマンド例: cloudflared tunnel run <トンネル名>',
                font=font10,
                anchor="w",
                justify="left",
                wraplength=420).pack(
                anchor=tk.W,
                pady=(
                    5,
                    0))
            link = tk.Label(self.tunnel_fields_area,
                            text="[CloudflareTunnelのインストール]がまだの方はこちら",
                            font=font10 + ("underline",
                                           ),
                            fg="blue",
                            cursor="hand2",
                            anchor="w",
                            justify="left",
                            wraplength=420)
            link.pack(anchor=tk.W)

            def open_cloudflare_link(event=None):
                import webbrowser
                webbrowser.open_new(
                    "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
            link.bind("<Button-1>", open_cloudflare_link)
        elif service == "ngrok":
            if 'ngrok_cmd' not in self.vars:
                self.vars['ngrok_cmd'] = tk.StringVar()
            ttk.Label(self.tunnel_fields_area, text="ngrok起動コマンド (NGROK_CMD)").pack(anchor=tk.W)
            ttk.Entry(
                self.tunnel_fields_area,
                textvariable=self.vars['ngrok_cmd'],
                width=48).pack(
                fill=tk.X)
            ttk.Label(
                self.tunnel_fields_area,
                text='コマンド例: ngrok http 8080',
                font=font10,
                anchor="w",
                justify="left",
                wraplength=420).pack(
                anchor=tk.W,
                pady=(
                    5,
                    0))
            link = tk.Label(self.tunnel_fields_area,
                            text="[ngrokのインストール]はこちら",
                            font=font10 + ("underline",
                                           ),
                            fg="blue",
                            cursor="hand2",
                            anchor="w",
                            justify="left",
                            wraplength=420)
            link.pack(anchor=tk.W)

            def open_ngrok_link(event=None):
                import webbrowser
                webbrowser.open_new("https://ngrok.com/download")
            link.bind("<Button-1>", open_ngrok_link)
        elif service == "localtunnel":
            if 'localtunnel_cmd' not in self.vars:
                self.vars['localtunnel_cmd'] = tk.StringVar()
            ttk.Label(
                self.tunnel_fields_area,
                text="localtunnel起動コマンド (LOCALTUNNEL_CMD)").pack(
                anchor=tk.W)
            ttk.Entry(
                self.tunnel_fields_area,
                textvariable=self.vars['localtunnel_cmd'],
                width=48).pack(
                fill=tk.X)
            ttk.Label(
                self.tunnel_fields_area,
                text='コマンド例: lt --port 8080',
                font=font10,
                anchor="w",
                justify="left",
                wraplength=420).pack(
                anchor=tk.W,
                pady=(
                    5,
                    0))
            link = tk.Label(self.tunnel_fields_area,
                            text="[localtunnelのインストール]はこちら",
                            font=font10 + ("underline",
                                           ),
                            fg="blue",
                            cursor="hand2",
                            anchor="w",
                            justify="left",
                            wraplength=420)
            link.pack(anchor=tk.W)

            def open_lt_link(event=None):
                import webbrowser
                webbrowser.open_new("https://github.com/localtunnel/localtunnel")
            link.bind("<Button-1>", open_lt_link)
        elif service == "custom":
            if 'custom_tunnel_cmd' not in self.vars:
                self.vars['custom_tunnel_cmd'] = tk.StringVar()
            ttk.Label(
                self.tunnel_fields_area,
                text="カスタムトンネル起動コマンド (CUSTOM_TUNNEL_CMD)").pack(
                anchor=tk.W)
            ttk.Entry(
                self.tunnel_fields_area,
                textvariable=self.vars['custom_tunnel_cmd'],
                width=48).pack(
                fill=tk.X)
            ttk.Label(
                self.tunnel_fields_area,
                text='任意のトンネルアプリケーションのコマンドを入力してください。',
                font=font10,
                anchor="w",
                justify="left",
                wraplength=420).pack(
                anchor=tk.W,
                pady=(
                    5,
                    0))

    def step_summary(self):
        ttk.Label(self.frame, text="セットアップ最終確認", font=(
            "Meiryo", 12, "bold")).pack(anchor=tk.W, pady=5)
        summary = tk.Text(self.frame, height=7, width=60,
                          font=("Meiryo", 10))  # 高さを7行に縮小
        summary.pack(fill=tk.BOTH, expand=False)  # expand=Falseで高さ固定
        summary.insert(tk.END, self.generate_summary_skipped())
        summary.config(state=tk.DISABLED)
        # 案内文を追加
        ttk.Label(self.frame, text="アカウント設定はいつでも設定GUIから変更することができます。", font=(
            "Meiryo", 10), foreground="#444").pack(anchor=tk.W, pady=(8, 0))
        self.btn_next.config(text="ファイルを作成")
        # 9ステップ目はキャンセルボタン非表示
        self.btn_cancel.pack_forget()

    def generate_summary_skipped(self):
        # ステップごとに「入力済み」or「スキップしました」だけを表示
        v = self.vars

        def is_filled(keys):
            for k in keys:
                if k not in v or not v[k].get():
                    return False
            return True
        lines = []
        # 1. Twitch
        lines.append("【Twitchアカウント】" +
                     (" 入力済み" if is_filled(['twitch_id', 'twitch_secret']) else " スキップしました"))
        # 2. Webhook
        lines.append("【Webhook設定】" +
                     (" 入力済み" if is_filled(['webhook_url']) else " スキップしました"))
        # 3. Bluesky
        lines.append("【Blueskyアカウント】" +
                     (" 入力済み" if is_filled(['bsky_user', 'bsky_pass']) else " スキップしました"))
        # 4. YouTube
        lines.append("【YouTubeアカウント】" +
                     (" 入力済み" if is_filled(['yt_api_key', 'yt_channel_id']) else " スキップしました"))
        # 5. ニコニコ
        lines.append("【ニコニコアカウント】" +
                     (" 入力済み" if is_filled(['nico_user_id']) else " スキップしました"))
        # 6. 通知設定
        notify_keys = [
            'notify_twitch_online',
            'notify_twitch_offline',
            'notify_yt_online',
            'notify_yt_video',
            'notify_nico_online',
            'notify_nico_video']
        lines.append(
            "【通知設定】" + (" 入力済み" if is_filled(notify_keys) else " スキップしました"))
        # 7. トンネル
        lines.append("【トンネル通信設定】" +
                     (" 入力済み" if is_filled(['tunnel_cmd']) else " スキップしました"))
        return '\n'.join(lines)

    def validate_step(self):
        # 各ステップごとに必須入力チェック
        if self.current_step == 0:
            # はじめにステップはバリデーションなし
            return True
        elif self.current_step == 1:
            if not self.vars['twitch_id'].get():
                messagebox.showerror("入力エラー", "TwitchクライアントIDを入力してください")
                return False
            if not self.vars['twitch_secret'].get():
                messagebox.showerror("入力エラー", "Twitchクライアントシークレットを入力してください")
                return False
        elif self.current_step == 2:
            if not self.vars['webhook_url'].get():
                messagebox.showerror("入力エラー", "WebhookコールバックURLを入力してください")
                return False
        elif self.current_step == 3:
            if not self.vars['bsky_user'].get():
                messagebox.showerror("入力エラー", "Blueskyユーザー名を入力してください")
                return False
            if not self.vars['bsky_pass'].get():
                messagebox.showerror("入力エラー", "Blueskyアプリパスワードを入力してください")
                return False
        elif self.current_step == 4:
            if not self.vars['yt_api_key'].get():
                messagebox.showerror("入力エラー", "YouTube APIキーを入力してください")
                return False
            if not self.vars['yt_channel_id'].get():
                messagebox.showerror("入力エラー", "YouTubeチャンネルIDを入力してください")
                return False
        elif self.current_step == 5:
            if not self.vars['nico_user_id'].get():
                messagebox.showerror("入力エラー", "ニコニコユーザーIDを入力してください")
                return False
        elif self.current_step == 7:
            if not self.vars['tunnel_cmd'].get():
                messagebox.showerror(
                    "入力エラー", "トンネル起動コマンド(TUNNEL_CMD)を入力してください")
                return False
        # 最終確認ステップではバリデーションなし
        return True

    def save_settings(self):
        # settings.env.exampleをベースに、ウィザード入力値で上書きしてsettings.envを生成
        import re
        v = self.vars

        def getval(key):
            # トンネル関連の分岐
            if key == 'TUNNEL_SERVICE':
                return v.get('tunnel_service', tk.StringVar()).get()
            if key == 'TUNNEL_CMD':
                return v.get(
                    'tunnel_cmd',
                    tk.StringVar()).get() if v.get(
                    'tunnel_service',
                    tk.StringVar()).get() == 'cloudflare' else ''
            if key == 'NGROK_CMD':
                return v.get(
                    'ngrok_cmd',
                    tk.StringVar()).get() if v.get(
                    'tunnel_service',
                    tk.StringVar()).get() == 'ngrok' else ''
            if key == 'LOCALTUNNEL_CMD':
                return v.get('localtunnel_cmd', tk.StringVar()).get() if v.get(
                    'tunnel_service', tk.StringVar()).get() == 'localtunnel' else ''
            if key == 'CUSTOM_TUNNEL_CMD':
                return v.get('custom_tunnel_cmd', tk.StringVar()).get() if v.get(
                    'tunnel_service', tk.StringVar()).get() == 'custom' else ''
            # ...既存の値取得...
            return v.get(key, tk.StringVar()).get() if key in v else ''

        # キー名: ウィザード変数名の対応
        keymap = {
            'BLUESKY_USERNAME': 'bsky_user',
            'BLUESKY_APP_PASSWORD': 'bsky_pass',
            'TWITCH_CLIENT_ID': 'twitch_id',
            'TWITCH_CLIENT_SECRET': 'twitch_secret',
            'WEBHOOK_CALLBACK_URL': 'webhook_url',
            'YOUTUBE_API_KEY': 'yt_api_key',
            'YOUTUBE_CHANNEL_ID': 'yt_channel_id',
            'NICONICO_USER_ID': 'nico_user_id',
            'NOTIFY_ON_TWITCH_ONINE': 'notify_twitch_online',
            'NOTIFY_ON_TWITCH_OFFLINE': 'notify_twitch_offline',
            'NOTIFY_ON_YOUTUBE_ONLINE': 'notify_yt_online',
            'NOTIFY_ON_YOUTUBE_NEW_VIDEO': 'notify_yt_video',
            'NOTIFY_ON_NICONICO_ONLINE': 'notify_nico_online',
            'NOTIFY_ON_NICONICO_NEW_VIDEO': 'notify_nico_video',
            'TUNNEL_SERVICE': 'tunnel_service',
            'TUNNEL_CMD': 'tunnel_cmd',
            'NGROK_CMD': 'ngrok_cmd',
            'LOCALTUNNEL_CMD': 'localtunnel_cmd',
            'CUSTOM_TUNNEL_CMD': 'custom_tunnel_cmd',
        }
        # exampleファイルを読み込む
        with open('settings.env.example', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            m = re.match(r'^([A-Z_]+)=', line)
            if m:
                key = m.group(1)
                if key in keymap:
                    val = getval(key)
                    # BooleanVarの場合はTrue/False文字列に
                    if isinstance(v.get(keymap[key], None), tk.BooleanVar):
                        val = str(val)
                    new_lines.append(f"{key}={val}\n")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        with open('settings.env', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        from tkinter import messagebox
        messagebox.showinfo("完了", "設定ファイルを作成しました。\nメイン画面を開きます")
        if self.on_finish:
            self.on_finish()
        # self.destroy() は呼ばない（on_finishでroot.destroy() or MainWindow起動するため）
