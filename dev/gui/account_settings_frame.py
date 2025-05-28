import tkinter as tk
import tkinter.ttk as ttk
import os
from dotenv import load_dotenv
import requests


class AccountSettingsFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        big_font = ("Meiryo", 10)
        notebook.add(self._twitch_tab(notebook, big_font), text="Twitch")
        notebook.add(self._webhook_tab(notebook, big_font), text="Webhook")
        notebook.add(self._webhookurl_tab(notebook, big_font), text="WebhookURL")
        # Blueskyタブ: entry_passをselfで保持
        self._bluesky_frame, self._bluesky_entry_pass = self._bluesky_tab(
            notebook, big_font)
        notebook.add(self._bluesky_frame, text="Bluesky")
        notebook.add(self._youtube_tab(notebook, big_font), text="YouTube")
        notebook.add(self._niconico_tab(notebook, big_font), text="ニコニコ")

        # タブ切り替え時にBluesky/Webhookアプリパスワード・URLを再読込
        def on_tab_changed(event):
            selected = event.widget.select()
            tab_text = event.widget.tab(selected, "text")
            if tab_text == "Bluesky":
                from dotenv import load_dotenv
                import os
                load_dotenv(
                    os.path.join(
                        os.path.dirname(__file__),
                        '../settings.env'),
                    override=True)
                bsky_pass = os.getenv('BLUESKY_APP_PASSWORD', '')
                self._bluesky_entry_pass.delete(0, tk.END)
                self._bluesky_entry_pass.insert(0, bsky_pass)
            elif tab_text == "Webhook":
                from dotenv import load_dotenv
                import os
                load_dotenv(
                    os.path.join(
                        os.path.dirname(__file__),
                        '../settings.env'),
                    override=True)
                tunnel_service = os.getenv('TUNNEL_SERVICE', '').lower()
                if tunnel_service in ("cloudflare", "custom"):
                    callback_url = os.getenv('WEBHOOK_CALLBACK_URL_PERMANENT', '')
                else:
                    callback_url = os.getenv('WEBHOOK_CALLBACK_URL_TEMPORARY', '')
                if self._webhook_entry_callback is not None:
                    self._webhook_entry_callback.config(state="normal")
                    self._webhook_entry_callback.delete(0, tk.END)
                    self._webhook_entry_callback.insert(0, callback_url)
                    self._webhook_entry_callback.config(state="readonly")
        notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    def _twitch_tab(self, master, big_font):
        frame = tk.Frame(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        client_id = os.getenv('TWITCH_CLIENT_ID', '')
        client_secret = os.getenv('TWITCH_CLIENT_SECRET', '')
        broadcaster_id = os.getenv('TWITCH_BROADCASTER_ID', '')
        broadcaster_id_converted = os.getenv(
            'TWITCH_BROADCASTER_ID_CONVERTED', '')

        # 見出し: TwitchAPI
        lbl_api = tk.Label(frame, text="TwitchAPI",
                           font=("Meiryo", 12, "bold"))
        lbl_api.grid(row=1, column=0, sticky=tk.W, pady=(10, 0), columnspan=2)
        # --- 検証用アイコンラベルを用意 ---
        label_id_status = tk.Label(frame, text="", font=("Meiryo", 10))
        label_secret_status = tk.Label(frame, text="", font=("Meiryo", 10))
        label_broadcaster_status = tk.Label(
            frame, text="", font=("Meiryo", 10))
        label_conv_status = tk.Label(
            frame, text="", font=("Meiryo", 10, "bold"), fg="green")

        # ラベル＋アイコンを同じ行に配置
        tk.Label(frame, text="TwitchクライアントID:", font=big_font).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 0))
        label_id_status.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        entry_id = tk.Entry(frame, font=big_font)
        entry_id.insert(0, client_id)
        entry_id.grid(row=3, column=0, sticky=tk.EW,
                      pady=(0, 10), columnspan=2)

        tk.Label(frame, text="Twitchクライアントシークレット:", font=big_font).grid(
            row=4, column=0, sticky=tk.W, pady=(10, 0))
        label_secret_status.grid(row=4, column=1, sticky=tk.W, pady=(10, 0))
        entry_secret = tk.Entry(frame, show="*", font=big_font)
        entry_secret.insert(0, client_secret)
        entry_secret.grid(row=5, column=0, sticky=tk.EW,
                          pady=(0, 10), columnspan=2)

        # 見出し: Twitchアカウント
        lbl_account = tk.Label(frame, text="Twitchアカウント",
                               font=("Meiryo", 12, "bold"))
        lbl_account.grid(row=6, column=0, sticky=tk.W,
                         pady=(20, 0), columnspan=2)
        tk.Label(frame, text="TwitchID（ユーザー名またはID）:", font=big_font).grid(
            row=7, column=0, sticky=tk.W, pady=(10, 0))
        label_broadcaster_status.grid(
            row=7, column=1, sticky=tk.W, pady=(10, 0))
        entry_broadcaster = tk.Entry(frame, font=big_font)
        entry_broadcaster.insert(0, broadcaster_id)
        entry_broadcaster.grid(
            row=8, column=0, sticky=tk.EW, pady=(0, 10), columnspan=2)

        tk.Label(frame, text="変換後のブロードキャスターID:", font=big_font).grid(
            row=9, column=0, sticky=tk.W, pady=(10, 0))
        label_conv_status.grid(row=9, column=1, sticky=tk.W, pady=(10, 0))
        # 変換後IDの保存・表示
        entry_broadcaster_conv = tk.Entry(
            frame, font=big_font, state="readonly")
        entry_broadcaster_conv.insert(0, broadcaster_id_converted)
        entry_broadcaster_conv.grid(
            row=10, column=0, sticky=tk.EW, pady=(0, 10), columnspan=2)

        # --- バリデーション用関数 ---
        def validate():
            ok = True
            if entry_id.get().strip():
                label_id_status.config(text="✓", fg="green")
            else:
                label_id_status.config(text="✗", fg="red")
                ok = False
            if entry_secret.get().strip():
                label_secret_status.config(text="✓", fg="green")
            else:
                label_secret_status.config(text="✗", fg="red")
                ok = False
            if entry_broadcaster.get().strip():
                label_broadcaster_status.config(text="✓", fg="green")
            else:
                label_broadcaster_status.config(text="✗", fg="red")
                ok = False
            return ok

        # Entryの内容が変わったらバリデーション
        entry_id.bind("<KeyRelease>", lambda e: validate())
        entry_secret.bind("<KeyRelease>", lambda e: validate())
        entry_broadcaster.bind("<KeyRelease>", lambda e: validate())
        validate()

        def save_twitch_account():
            cid = entry_id.get().strip()
            csecret = entry_secret.get().strip()
            user_input = entry_broadcaster.get().strip()
            # バリデーション
            if not validate():
                tk.messagebox.showerror("エラー", "全ての項目を入力してください。")
                return
            # ユーザー名→ID変換

            def is_numeric(s):
                return s.isdigit()
            converted_id = user_input
            conv_message = ""
            if not is_numeric(user_input):
                # まずアクセストークンを取得
                try:
                    token_url = "https://id.twitch.tv/oauth2/token"
                    params = {
                        "client_id": cid,
                        "client_secret": csecret,
                        "grant_type": "client_credentials"
                    }
                    token_resp = requests.post(
                        token_url, params=params, timeout=10)
                    token_data = token_resp.json()
                    if token_resp.status_code == 200 and "access_token" in token_data:
                        access_token = token_data["access_token"]
                    else:
                        tk.messagebox.showerror(
                            "認証エラー", f"Twitchアクセストークン取得に失敗しました: {token_data}")
                        label_conv_status.config(text="", fg="green")
                        return
                except Exception as e:
                    tk.messagebox.showerror(
                        "通信エラー", f"Twitchアクセストークン取得に失敗: {e}")
                    label_conv_status.config(text="", fg="green")
                    return
                # アクセストークンでユーザー名→ID変換
                try:
                    url = f"https://api.twitch.tv/helix/users?login={user_input}"
                    headers = {
                        "Client-ID": cid,
                        "Authorization": f"Bearer {access_token}"
                    }
                    resp = requests.get(url, headers=headers, timeout=10)
                    data = resp.json()
                    if resp.status_code == 200 and data.get("data"):
                        converted_id = data["data"][0]["id"]
                        conv_message = "変換完了！"
                    else:
                        tk.messagebox.showerror(
                            "変換エラー", f"Twitchユーザー名からID変換に失敗しました: {data}")
                        label_conv_status.config(text="", fg="green")
                        return
                except Exception as e:
                    tk.messagebox.showerror("通信エラー", f"Twitch API通信に失敗: {e}")
                    label_conv_status.config(text="", fg="green")
                    return
            # 保存
            env_path = os.path.join(
                os.path.dirname(__file__), '../settings.env')
            lines = []
            found_id = found_secret = found_broadcaster = found_conv = False
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith('TWITCH_CLIENT_ID='):
                    new_lines.append(f'TWITCH_CLIENT_ID={cid}\n')
                    found_id = True
                elif line.startswith('TWITCH_CLIENT_SECRET='):
                    new_lines.append(f'TWITCH_CLIENT_SECRET={csecret}\n')
                    found_secret = True
                elif line.startswith('TWITCH_BROADCASTER_ID='):
                    new_lines.append(f'TWITCH_BROADCASTER_ID={user_input}\n')
                    found_broadcaster = True
                elif line.startswith('TWITCH_BROADCASTER_ID_CONVERTED='):
                    new_lines.append(
                        f'TWITCH_BROADCASTER_ID_CONVERTED={converted_id}\n')
                    found_conv = True
                else:
                    new_lines.append(line)
            if not found_id:
                new_lines.append(f'TWITCH_CLIENT_ID={cid}\n')
            if not found_secret:
                new_lines.append(f'TWITCH_CLIENT_SECRET={csecret}\n')
            if not found_broadcaster:
                new_lines.append(f'TWITCH_BROADCASTER_ID={user_input}\n')
            if not found_conv:
                new_lines.append(
                    f'TWITCH_BROADCASTER_ID_CONVERTED={converted_id}\n')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            # 変換後IDを表示（保存した値を再読込して常に最新を表示）
            load_dotenv(os.path.join(os.path.dirname(__file__),
                        '../settings.env'), override=True)
            broadcaster_id_converted_new = os.getenv(
                'TWITCH_BROADCASTER_ID_CONVERTED', '')
            entry_broadcaster_conv.config(state="normal")
            entry_broadcaster_conv.delete(0, tk.END)
            entry_broadcaster_conv.insert(0, broadcaster_id_converted_new)
            entry_broadcaster_conv.config(state="readonly")
            # 変換完了メッセージ
            label_conv_status.config(text=conv_message, fg="green")
            tk.messagebox.showinfo("保存完了", "Twitchアカウント情報を保存しました。")

        # 保存ボタンもwidth=40で統一
        btn_save = tk.Button(frame, text="保存", font=(
            "Meiryo", 10), command=save_twitch_account)
        btn_save.grid(row=11, column=0, columnspan=2,
                      sticky=tk.EW, pady=(10, 10), padx=(0, 0))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        return frame

    def _webhook_tab(self, master, big_font):
        frame = tk.Frame(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        tunnel_service = os.getenv('TUNNEL_SERVICE', '').lower()
        if tunnel_service in ("cloudflare", "custom"):
            callback_url = os.getenv('WEBHOOK_CALLBACK_URL_PERMANENT', '')
            url_label = "WebhookコールバックURL（恒久用: Cloudflare/custom）"
        else:
            callback_url = os.getenv('WEBHOOK_CALLBACK_URL_TEMPORARY', '')
            url_label = "WebhookコールバックURL（一時用: ngrok/localtunnel）"
        webhook_secret = os.getenv('WEBHOOK_SECRET', '')
        secret_last_rotated = os.getenv('SECRET_LAST_ROTATED', '')
        retry_max = os.getenv('RETRY_MAX', '3')
        retry_wait = os.getenv('RETRY_WAIT', '2')
        lbl_section = tk.Label(
            frame, text="Twitch EventSub Webhook設定", font=("Meiryo", 12, "bold"))
        lbl_section.grid(row=0, column=0, sticky=tk.W,
                         pady=(10, 0), columnspan=2)
        tk.Label(frame, text=url_label, font=big_font).grid(
            row=1, column=0, sticky=tk.W, pady=(10, 0))
        entry_callback = tk.Entry(frame, font=big_font, state="readonly")
        entry_callback.insert(0, callback_url)
        entry_callback.grid(row=2, column=0, sticky=tk.EW,
                            pady=(0, 10), columnspan=2)
        self._webhook_entry_callback = entry_callback

        # Webhookシークレット
        tk.Label(frame, text="Webhookシークレットキー", font=big_font).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 0))
        entry_secret = tk.Entry(frame, font=big_font, state="readonly")
        entry_secret.insert(0, webhook_secret)
        entry_secret.grid(row=4, column=0, sticky=tk.EW,
                          pady=(0, 10), columnspan=2)
        btn_clear_secret = tk.Button(frame, text="シークレット消去", font=(
            "Meiryo", 9), command=lambda: clear_secret_and_rotated())
        btn_clear_secret.grid(row=4, column=2, sticky=tk.W, padx=(5, 0))

        # シークレット最終ローテーション日時
        tk.Label(frame, text="シークレット最終ローテーション日時", font=big_font).grid(
            row=5, column=0, sticky=tk.W, pady=(10, 0))
        entry_rotated = tk.Entry(frame, font=big_font, state="readonly")
        entry_rotated.insert(0, secret_last_rotated)
        entry_rotated.grid(row=6, column=0, sticky=tk.EW,
                           pady=(0, 10), columnspan=2)

        def clear_secret_and_rotated():
            entry_secret.config(state="normal")
            entry_secret.delete(0, tk.END)
            entry_secret.config(state="readonly")
            entry_rotated.config(state="normal")
            entry_rotated.delete(0, tk.END)
            entry_rotated.config(state="readonly")
            # .envからも消去
            env_path = os.path.join(
                os.path.dirname(__file__), '../settings.env')
            lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith('WEBHOOK_SECRET='):
                    new_lines.append('WEBHOOK_SECRET=\n')
                elif line.startswith('SECRET_LAST_ROTATED='):
                    new_lines.append('SECRET_LAST_ROTATED=\n')
                else:
                    new_lines.append(line)
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            tk.messagebox.showinfo('消去完了', 'Webhookシークレットとローテーション日時を消去しました。')

        # リトライ回数
        tk.Label(frame, text="APIリクエスト失敗時のリトライ回数", font=big_font).grid(
            row=7, column=0, sticky=tk.W, pady=(10, 0))
        entry_retry_max = tk.Entry(frame, font=big_font)
        entry_retry_max.insert(0, retry_max)
        entry_retry_max.grid(row=8, column=0, sticky=tk.EW,
                             pady=(0, 10), columnspan=2)

        # リトライ待機秒数
        tk.Label(frame, text="リトライ時の待機秒数", font=big_font).grid(
            row=9, column=0, sticky=tk.W, pady=(10, 0))
        entry_retry_wait = tk.Entry(frame, font=big_font)
        entry_retry_wait.insert(0, retry_wait)
        entry_retry_wait.grid(row=10, column=0, sticky=tk.EW,
                              pady=(0, 10), columnspan=2)

        # 保存ボタン
        def save_webhook_settings():
            cb_url = entry_callback.get().strip()
            retry_m = entry_retry_max.get().strip()
            retry_w = entry_retry_wait.get().strip()
            env_path = os.path.join(
                os.path.dirname(__file__), '../settings.env')
            lines = []
            found_cb = found_rm = found_rw = False
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith('WEBHOOK_CALLBACK_URL='):
                    new_lines.append(f'WEBHOOK_CALLBACK_URL={cb_url}\n')
                    found_cb = True
                elif line.startswith('RETRY_MAX='):
                    new_lines.append(f'RETRY_MAX={retry_m}\n')
                    found_rm = True
                elif line.startswith('RETRY_WAIT='):
                    new_lines.append(f'RETRY_WAIT={retry_w}\n')
                    found_rw = True
                else:
                    new_lines.append(line)
            if not found_cb:
                new_lines.append(f'WEBHOOK_CALLBACK_URL={cb_url}\n')
            if not found_rm:
                new_lines.append(f'RETRY_MAX={retry_m}\n')
            if not found_rw:
                new_lines.append(f'RETRY_WAIT={retry_w}\n')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            tk.messagebox.showinfo('保存完了', 'Webhook設定を保存しました。')

        btn_save = tk.Button(frame, text="保存", font=(
            "Meiryo", 10), command=save_webhook_settings)
        btn_save.grid(row=11, column=0, columnspan=2,
                      sticky=tk.EW, pady=(10, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        return frame

    def _webhookurl_tab(self, master, big_font):
        frame = tk.Frame(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        permanent_url = os.getenv('WEBHOOK_CALLBACK_URL_PERMANENT', '')
        temporary_url = os.getenv('WEBHOOK_CALLBACK_URL_TEMPORARY', '')
        # 恒久用
        tk.Label(
            frame,
            text="WebhookコールバックURL（恒久用: Cloudflare/custom）",
            font=big_font).grid(
            row=0,
            column=0,
            sticky=tk.W,
            pady=(
                10,
                0))
        entry_perm = tk.Entry(frame, font=big_font)
        entry_perm.insert(0, permanent_url)
        entry_perm.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))
        # 一時用（編集不可）
        tk.Label(
            frame,
            text="WebhookコールバックURL（一時用: ngrok/localtunnel）",
            font=big_font).grid(
            row=2,
            column=0,
            sticky=tk.W,
            pady=(
                10,
                0))
        entry_temp = tk.Entry(frame, font=big_font, state="readonly")
        entry_temp.insert(0, temporary_url)
        entry_temp.grid(row=3, column=0, sticky=tk.EW, pady=(0, 10))

        # 保存ボタン（PERMANENTのみ保存）
        def save_perm_url():
            url = entry_perm.get().strip()
            env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
            lines = []
            found = False
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith('WEBHOOK_CALLBACK_URL_PERMANENT='):
                    new_lines.append(f'WEBHOOK_CALLBACK_URL_PERMANENT={url}\n')
                    found = True
                else:
                    new_lines.append(line)
            if not found:
                new_lines.append(f'WEBHOOK_CALLBACK_URL_PERMANENT={url}\n')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            tk.messagebox.showinfo('保存完了', 'WEBHOOK_CALLBACK_URL_PERMANENTを保存しました。')
        btn_save = tk.Button(frame, text="保存", font=("Meiryo", 10), command=save_perm_url)
        btn_save.grid(row=4, column=0, sticky=tk.EW, pady=(10, 10))
        frame.grid_columnconfigure(0, weight=1)
        return frame

    def _bluesky_tab(self, master, big_font):
        frame = tk.Frame(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        bsky_user = os.getenv('BLUESKY_USERNAME', '')
        bsky_pass = os.getenv('BLUESKY_APP_PASSWORD', '')
        # Blueskyユーザー名ラベル（2行）
        tk.Label(frame, text="Blueskyユーザー名:", font=big_font).grid(
            row=0, column=0, sticky=tk.W, pady=(10, 0))
        tk.Label(
            frame,
            text="(例: your-handle.bsky.social or 独自ドメイン等ご利用中のID）",
            font=(
                "Meiryo",
                9),
            fg="gray").grid(
            row=1,
            column=0,
            sticky=tk.W,
            pady=(
                0,
                0))
        label_user_status = tk.Label(frame, text="", font=("Meiryo", 10))
        label_user_status.grid(row=0, column=1, sticky=tk.W, pady=(10, 0))
        entry_user = tk.Entry(frame, font=big_font)
        entry_user.insert(0, bsky_user)
        entry_user.grid(row=2, column=0, sticky=tk.EW,
                        pady=(0, 10), columnspan=2)
        # アプリパスワードラベル（2行）
        tk.Label(frame, text="Blueskyアプリパスワード:", font=big_font).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 0))
        tk.Label(frame, text="（ログインパスワードではありません）", font=("Meiryo", 9), fg="gray").grid(
            row=4, column=0, sticky=tk.W, pady=(0, 0))
        label_pass_status = tk.Label(frame, text="", font=("Meiryo", 10))
        label_pass_status.grid(row=3, column=1, sticky=tk.W, pady=(10, 0))
        entry_pass = tk.Entry(frame, show="*", font=big_font)
        entry_pass.insert(0, bsky_pass)
        entry_pass.grid(row=5, column=0, sticky=tk.EW,
                        pady=(0, 10), columnspan=2)

        # バリデーション&接続確認
        def validate_bluesky():
            user = entry_user.get().strip()
            pw = entry_pass.get().strip()
            ok = True
            if user and ("." in user or ":" in user):
                label_user_status.config(text="✓", fg="green")
            else:
                label_user_status.config(text="✗", fg="red")
                ok = False
            if pw and len(pw) >= 10:
                label_pass_status.config(text="✓", fg="green")
            else:
                label_pass_status.config(text="✗", fg="red")
                ok = False
            return ok

        entry_user.bind("<KeyRelease>", lambda e: validate_bluesky())
        entry_pass.bind("<KeyRelease>", lambda e: validate_bluesky())
        validate_bluesky()

        # 接続テスト
        label_connect_status = tk.Label(
            frame, text="", font=("Meiryo", 10, "bold"))

        def test_bluesky_connect():
            import requests
            user = entry_user.get().strip()
            pw = entry_pass.get().strip()
            label_connect_status.config(text="")  # ←毎回クリア
            if not validate_bluesky():
                label_connect_status.config(text="✗ 入力エラー", fg="red")
                return
            try:
                resp = requests.post(
                    "https://bsky.social/xrpc/com.atproto.server.createSession",
                    json={"identifier": user, "password": pw}, timeout=10)
                if resp.status_code == 200 and resp.json().get("accessJwt"):
                    label_user_status.config(text="✓", fg="green")
                    label_pass_status.config(text="✓", fg="green")
                    label_connect_status.config(text="✓ 接続成功", fg="green")
                else:
                    label_user_status.config(text="✗", fg="red")
                    label_pass_status.config(text="✗", fg="red")
                    label_connect_status.config(text="✗ 認証失敗", fg="red")
            except Exception as e:
                label_user_status.config(text="✗", fg="red")
                label_pass_status.config(text="✗", fg="red")
                label_connect_status.config(text=f"✗ 接続失敗: {e}", fg="red")

        btn_test = tk.Button(frame, text="接続テスト", font=(
            "Meiryo", 10), command=test_bluesky_connect)
        btn_test.grid(row=6, column=0, columnspan=2,
                      sticky=tk.EW, pady=(0, 10))
        # スペース用の空ラベル
        spacer = tk.Label(frame, text="", font=("Meiryo", 10))
        spacer.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        # 接続テスト結果をスペースに表示
        label_connect_status.grid(row=7, column=0, columnspan=2, sticky=tk.W)

        def save_bluesky_settings():
            user = entry_user.get().strip()
            pw = entry_pass.get().strip()
            if not validate_bluesky():
                tk.messagebox.showerror("エラー", "ユーザー名・アプリパスワードを正しく入力してください。")
                return
            env_path = os.path.join(
                os.path.dirname(__file__), '../settings.env')
            lines = []
            found_user = found_pass = False
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith('BLUESKY_USERNAME='):
                    new_lines.append(f'BLUESKY_USERNAME={user}\n')
                    found_user = True
                elif line.startswith('BLUESKY_APP_PASSWORD='):
                    new_lines.append(f'BLUESKY_APP_PASSWORD={pw}\n')
                    found_pass = True
                else:
                    new_lines.append(line)
            if not found_user:
                new_lines.append(f'BLUESKY_USERNAME={user}\n')
            if not found_pass:
                new_lines.append(f'BLUESKY_APP_PASSWORD={pw}\n')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            tk.messagebox.showinfo('保存完了', 'Bluesky設定を保存しました。')

        btn_save = tk.Button(frame, text="保存", font=(
            "Meiryo", 10), command=save_bluesky_settings)
        btn_save.grid(row=8, column=0, columnspan=2,
                      sticky=tk.EW, pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        return frame, entry_pass

    def _youtube_tab(self, master, big_font):
        frame = tk.Frame(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        yt_key = os.getenv('YOUTUBE_API_KEY', '')
        yt_channel = os.getenv('YOUTUBE_CHANNEL_ID', '')
        yt_poll = os.getenv('YOUTUBE_POLL_INTERVAL', '60')
        # --- 検証用アイコンラベルを用意 ---
        label_key_status = tk.Label(frame, text="", font=("Meiryo", 10))
        label_channel_status = tk.Label(frame, text="", font=("Meiryo", 10))
        label_poll_status = tk.Label(frame, text="", font=("Meiryo", 10))
        # APIキー
        tk.Label(frame, text="YouTube APIキー:", font=big_font).grid(
            row=0, column=0, sticky=tk.W, pady=(10, 0))
        label_key_status.grid(row=0, column=1, sticky=tk.W, pady=(10, 0))
        entry_key = tk.Entry(frame, font=big_font)
        entry_key.insert(0, yt_key)
        entry_key.grid(row=1, column=0, sticky=tk.EW,
                       pady=(0, 10), columnspan=2)
        # チャンネルID
        tk.Label(frame, text="YouTubeチャンネルID:", font=big_font).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 0))
        label_channel_status.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        entry_channel = tk.Entry(frame, font=big_font)
        entry_channel.insert(0, yt_channel)
        entry_channel.grid(row=3, column=0, sticky=tk.EW,
                           pady=(0, 10), columnspan=2)
        # ポーリング間隔
        tk.Label(frame, text="ポーリング間隔（秒）:", font=big_font).grid(
            row=4, column=0, sticky=tk.W, pady=(10, 0))
        label_poll_status.grid(row=4, column=1, sticky=tk.W, pady=(10, 0))
        entry_poll = tk.Entry(frame, font=big_font)
        entry_poll.insert(0, yt_poll)
        entry_poll.grid(row=5, column=0, sticky=tk.EW,
                        pady=(0, 10), columnspan=2)

        # バリデーション関数
        def validate_youtube():
            key = entry_key.get().strip()
            channel = entry_channel.get().strip()
            poll = entry_poll.get().strip()
            ok = True
            if key:
                label_key_status.config(text="✓", fg="green")
            else:
                label_key_status.config(text="✗", fg="red")
                ok = False
            if channel and (channel.startswith('UC') and len(channel) >= 24):
                label_channel_status.config(text="✓", fg="green")
            else:
                label_channel_status.config(text="✗", fg="red")
                ok = False
            if poll.isdigit() and int(poll) > 0:
                label_poll_status.config(text="✓", fg="green")
            else:
                label_poll_status.config(text="✗", fg="red")
                ok = False
            return ok

        entry_key.bind("<KeyRelease>", lambda e: validate_youtube())
        entry_channel.bind("<KeyRelease>", lambda e: validate_youtube())
        entry_poll.bind("<KeyRelease>", lambda e: validate_youtube())
        validate_youtube()

        # 接続テスト
        label_connect_status = tk.Label(
            frame, text="", font=("Meiryo", 10, "bold"))

        def test_youtube_connect():
            import requests
            key = entry_key.get().strip()
            channel = entry_channel.get().strip()
            poll = entry_poll.get().strip()
            if not validate_youtube():
                label_connect_status.config(text="✗ 入力エラー", fg="red")
                return
            try:
                url = f"https://www.googleapis.com/youtube/v3/channels?part=id&id={channel}&key={key}"
                resp = requests.get(url, timeout=10)
                data = resp.json()
                if resp.status_code == 200 and data.get("items"):
                    label_connect_status.config(text="✓ 接続成功", fg="green")
                elif resp.status_code == 403:
                    label_connect_status.config(text="✗ APIキー権限エラー", fg="red")
                else:
                    label_connect_status.config(text="✗ 認証失敗", fg="red")
            except Exception as e:
                label_connect_status.config(text=f"✗ 接続失敗: {e}", fg="red")

        btn_test = tk.Button(frame, text="接続テスト", font=(
            "Meiryo", 10), command=test_youtube_connect)
        btn_test.grid(row=6, column=0, columnspan=2,
                      sticky=tk.EW, pady=(0, 10))
        # スペース用の空ラベル
        spacer = tk.Label(frame, text="", font=("Meiryo", 10))
        spacer.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        # 接続テスト結果をスペースに表示
        label_connect_status.grid(row=7, column=0, columnspan=2, sticky=tk.W)

        def save_youtube_settings():
            key = entry_key.get().strip()
            channel = entry_channel.get().strip()
            poll = entry_poll.get().strip()
            if not validate_youtube():
                tk.messagebox.showerror("エラー", "全ての項目を正しく入力してください。")
                return
            env_path = os.path.join(
                os.path.dirname(__file__), '../settings.env')
            lines = []
            found_key = found_channel = found_poll = False
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith('YOUTUBE_API_KEY='):
                    new_lines.append(f'YOUTUBE_API_KEY={key}\n')
                    found_key = True
                elif line.startswith('YOUTUBE_CHANNEL_ID='):
                    new_lines.append(f'YOUTUBE_CHANNEL_ID={channel}\n')
                    found_channel = True
                elif line.startswith('YOUTUBE_POLL_INTERVAL='):
                    new_lines.append(f'YOUTUBE_POLL_INTERVAL={poll}\n')
                    found_poll = True
                else:
                    new_lines.append(line)
            if not found_key:
                new_lines.append(f'YOUTUBE_API_KEY={key}\n')
            if not found_channel:
                new_lines.append(f'YOUTUBE_CHANNEL_ID={channel}\n')
            if not found_poll:
                new_lines.append(f'YOUTUBE_POLL_INTERVAL={poll}\n')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            tk.messagebox.showinfo('保存完了', 'YouTube設定を保存しました。')

        btn_save = tk.Button(frame, text="保存", font=(
            "Meiryo", 10), command=save_youtube_settings)
        btn_save.grid(row=8, column=0, columnspan=2,
                      sticky=tk.EW, pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        return frame

    def _niconico_tab(self, master, big_font):
        frame = tk.Frame(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        nico_id = os.getenv('NICONICO_USER_ID', '')
        nico_poll = os.getenv('NICONICO_LIVE_POLL_INTERVAL', '60')
        # ユーザーID
        tk.Label(frame, text="ニコニコユーザーID（数字のみ）:", font=big_font).grid(
            row=0, column=0, sticky=tk.W, pady=(10, 0))
        entry_id = tk.Entry(frame, font=big_font)
        entry_id.insert(0, nico_id)
        entry_id.grid(row=1, column=0, sticky=tk.EW,
                      pady=(0, 10), columnspan=2)
        # ポーリング間隔
        tk.Label(frame, text="ポーリング間隔（秒）:", font=big_font).grid(
            row=2, column=0, sticky=tk.W, pady=(10, 0))
        entry_poll = tk.Entry(frame, font=big_font)
        entry_poll.insert(0, nico_poll)
        entry_poll.grid(row=3, column=0, sticky=tk.EW,
                        pady=(0, 10), columnspan=2)

        def save_niconico_settings():
            user_id = entry_id.get().strip()
            poll = entry_poll.get().strip()
            env_path = os.path.join(
                os.path.dirname(__file__), '../settings.env')
            lines = []
            found_id = found_poll = False
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith('NICONICO_USER_ID='):
                    new_lines.append(f'NICONICO_USER_ID={user_id}\n')
                    found_id = True
                elif line.startswith('NICONICO_LIVE_POLL_INTERVAL='):
                    new_lines.append(f'NICONICO_LIVE_POLL_INTERVAL={poll}\n')
                    found_poll = True
                else:
                    new_lines.append(line)
            if not found_id:
                new_lines.append(f'NICONICO_USER_ID={user_id}\n')
            if not found_poll:
                new_lines.append(f'NICONICO_LIVE_POLL_INTERVAL={poll}\n')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            tk.messagebox.showinfo('保存完了', 'ニコニコ設定を保存しました。')
            # RSS取得・表示
            if not user_id:
                set_rss_text('IDが設定されていないため処理をスキップしました')
            else:
                rss_results = fetch_niconico_rss(user_id)
                set_rss_text(rss_results)

        # 保存ボタン
        btn_save = tk.Button(frame, text="保存", font=(
            "Meiryo", 10), command=save_niconico_settings)
        btn_save.grid(row=4, column=0, columnspan=2,
                      sticky=tk.EW, pady=(10, 0), padx=(0, 0))

        # 検索結果見出し
        label_rss_title = tk.Label(frame, text="入力IDによる動画検索結果", font=(
            "Meiryo", 10, "bold"), anchor="w", justify=tk.LEFT)
        label_rss_title.grid(row=5, column=0, columnspan=2,
                             sticky=tk.W, pady=(10, 0))
        # RSS取得結果表示用ラベル（リンク化対応）
        from tkinter import Text, DISABLED, NORMAL
        text_rss = Text(frame, height=10, font=(
            "Meiryo", 9), wrap="word", cursor="arrow")
        text_rss.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=(2, 0))
        text_rss.config(state=DISABLED)

        def open_url(event):
            import webbrowser
            idx = text_rss.index("@%s,%s" % (event.x, event.y))
            tag_names = text_rss.tag_names(idx)
            for tag in tag_names:
                if tag.startswith("url_"):
                    url = tag.split("url_", 1)[1]
                    webbrowser.open(url)
                    return

        text_rss.tag_configure("link", foreground="blue", underline=True)
        text_rss.bind("<Button-1>", open_url)

        def set_rss_text(results):
            text_rss.config(state=NORMAL)
            text_rss.delete("1.0", "end")
            if isinstance(results, list):
                for i, (title, link) in enumerate(results):
                    text_rss.insert("end", f"・{title}\n  ")
                    if link:
                        tag = f"url_{link}"
                        start_idx = text_rss.index("end-1c")
                        text_rss.insert("end", link, tag)
                        end_idx = text_rss.index("end-1c")
                        text_rss.tag_add(tag, start_idx, end_idx)
                        text_rss.tag_config(
                            tag, foreground="blue", underline=True)
                    text_rss.insert("end", "\n\n")
            else:
                text_rss.insert("end", results)
            text_rss.config(state=DISABLED)

        def fetch_niconico_rss(user_id):
            import requests
            import xml.etree.ElementTree as ET
            try:
                url = f"https://www.nicovideo.jp/user/{user_id}/video?rss=2.0"
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
                items = root.findall('.//item')
                results = []
                for item in items[:3]:
                    title = item.find('title').text if item.find(
                        'title') is not None else "(タイトル取得失敗)"
                    link = item.find('link').text if item.find(
                        'link') is not None else ""
                    results.append((title, link))
                if not results:
                    return "動画が見つかりませんでした(検索は成功しました)"
                return results
            except Exception as e:
                return f"RSS取得失敗: {e}"

        return frame
