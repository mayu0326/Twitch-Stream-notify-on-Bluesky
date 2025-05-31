
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
import tkinter.messagebox as messagebox  # 追加

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
TITLE_FONT = ("Yu Gothic UI", 17, "normal")
BTN_FONT = ("Yu Gothic UI", 16, "normal")

def create_webhookurl_tab(parent):
    frame = ctk.CTkFrame(parent)
    load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
    permanent_url = os.getenv('WEBHOOK_CALLBACK_URL_PERMANENT', '')
    temporary_url = os.getenv('WEBHOOK_CALLBACK_URL_TEMPORARY', '')
    # 恒久用
    ctk.CTkLabel(frame, text="WebhookコールバックURL（恒久用: Cloudflare/custom）", font=DEFAULT_FONT).pack(anchor="w", pady=(10, 0), padx=16)
    entry_perm = ctk.CTkEntry(frame, font=DEFAULT_FONT)
    entry_perm.insert(0, permanent_url)
    entry_perm.pack(fill="x", padx=16, pady=(0, 10))
    # 一時用（編集不可）
    ctk.CTkLabel(frame, text="WebhookコールバックURL（一時用: ngrok/localtunnel）", font=DEFAULT_FONT).pack(anchor="w", pady=(10, 0), padx=16)
    entry_temp = ctk.CTkEntry(frame, font=DEFAULT_FONT)
    entry_temp.insert(0, temporary_url)
    entry_temp.configure(state="readonly")
    entry_temp.pack(fill="x", padx=16, pady=(0, 10))
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
        messagebox.showinfo('保存完了', 'WEBHOOK_CALLBACK_URL_PERMANENTを保存しました。')
    ctk.CTkButton(frame, text="保存", font=BTN_FONT, command=save_perm_url).pack(pady=(10, 10))
    return frame
