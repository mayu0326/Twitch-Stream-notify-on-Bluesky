
# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

# Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# このプログラムはフリーソフトウェアです。フリーソフトウェア財団によって発行された
# GNU 一般公衆利用許諾契約書（バージョン2またはそれ以降）に基づき、再配布または
# 改変することができます。
#
# このプログラムは有用であることを願って配布されていますが、
# 商品性や特定目的への適合性についての保証はありません。
# 詳細はGNU一般公衆利用許諾契約書をご覧ください。
#
# このプログラムとともにGNU一般公衆利用許諾契約書が配布されているはずです。
# もし同梱されていない場合は、フリーソフトウェア財団までご請求ください。
# 住所: 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

from version_info import __version__
import os
import customtkinter as ctk
from dotenv import load_dotenv
import tkinter.messagebox as messagebox

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
TITLE_FONT = ("Yu Gothic UI", 17, "normal")
BTN_FONT = ("Yu Gothic UI", 16, "normal")

class WebhookAccTab(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
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
        retry_wait = os.getenv('RETRY_WAIT', '3')

        ctk.CTkLabel(self, text="Twitch EventSub Webhook設定", font=TITLE_FONT).pack(anchor="w", pady=(10, 0), padx=16)
        ctk.CTkLabel(self, text=url_label, font=DEFAULT_FONT).pack(anchor="w", pady=(10, 0), padx=16)
        self.entry_callback = ctk.CTkEntry(self, font=DEFAULT_FONT)
        self.entry_callback.insert(0, callback_url)
        self.entry_callback.configure(state="readonly")
        self.entry_callback.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkLabel(self, text="Webhookシークレットキー", font=DEFAULT_FONT).pack(anchor="w", pady=(10, 0), padx=16)
        self.entry_secret = ctk.CTkEntry(self, font=DEFAULT_FONT)
        self.entry_secret.insert(0, webhook_secret)
        self.entry_secret.configure(state="readonly")
        self.entry_secret.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkLabel(self, text="シークレット最終ローテーション日時", font=DEFAULT_FONT).pack(anchor="w", pady=(10, 0), padx=16)
        self.entry_rotated = ctk.CTkEntry(self, font=DEFAULT_FONT)
        self.entry_rotated.insert(0, secret_last_rotated)
        self.entry_rotated.configure(state="readonly")
        self.entry_rotated.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkLabel(self, text="APIリクエスト失敗時のリトライ回数", font=DEFAULT_FONT).pack(anchor="w", pady=(10, 0), padx=16)
        vcmd = (self.register(self._validate_2digit), '%P')
        self.entry_retry_max = ctk.CTkEntry(self, font=DEFAULT_FONT, validate="key", validatecommand=vcmd)
        self.entry_retry_max.insert(0, retry_max)
        self.entry_retry_max.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkLabel(self, text="リトライ時の待機秒数", font=DEFAULT_FONT).pack(anchor="w", pady=(10, 0), padx=16)
        self.entry_retry_wait = ctk.CTkEntry(self, font=DEFAULT_FONT, validate="key", validatecommand=vcmd)
        self.entry_retry_wait.insert(0, retry_wait)
        self.entry_retry_wait.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkButton(self, text="保存", font=BTN_FONT, command=self.save_webhook_settings).pack(pady=(16, 10))
        ctk.CTkButton(self, text="シークレット消去", font=("Yu Gothic UI", 12), command=self.clear_secret_and_rotated).pack(pady=(0, 10))

    def save_webhook_settings(self):
        cb_url = self.entry_callback.get().strip()
        retry_m = self.entry_retry_max.get().strip()
        retry_w = self.entry_retry_wait.get().strip()
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
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
        messagebox.showinfo("保存完了", "Webhook設定を保存しました。")

    def clear_secret_and_rotated(self):
        self.entry_secret.configure(state="normal")
        self.entry_secret.delete(0, "end")
        self.entry_secret.configure(state="readonly")
        self.entry_rotated.configure(state="normal")
        self.entry_rotated.delete(0, "end")
        self.entry_rotated.configure(state="readonly")
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
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
        ctk.CTkMessagebox(title='消去完了', message='Webhookシークレットとローテーション日時を消去しました。', icon='info')

    def _validate_2digit(self, value):
        return value.isdigit() and len(value) <= 2 or value == ""
