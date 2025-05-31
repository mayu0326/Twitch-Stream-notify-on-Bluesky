
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
import tkinter as tk
import re

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
TITLE_FONT = ("Yu Gothic UI", 17, "normal")
DESC_FONT = ("Meiryo", 15, "normal")
BTN_FONT = ("Yu Gothic UI", 18, "normal")

def create_youtube_tab(parent):
    youtube_tab = ctk.CTkFrame(parent)
    load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
    yt_key = os.getenv('YOUTUBE_API_KEY', '')
    yt_channel = os.getenv('YOUTUBE_CHANNEL_ID', '')
    yt_poll = os.getenv('YOUTUBE_POLL_INTERVAL', '60')
    # タイトルラベル
    label_title = ctk.CTkLabel(youtube_tab, text="YouTube APIキー/チャンネル設定", font=TITLE_FONT)
    label_title.pack(pady=(18, 6))
    # APIキーラベル＋バリデーション＋エントリ＋表示切替ボタンを横並びで1行に
    key_row = ctk.CTkFrame(youtube_tab, fg_color="transparent")
    key_row.pack(fill="x", padx=20, pady=(10, 0))
    label_key = ctk.CTkLabel(key_row, text="YouTubeDataAPIのAPIキー:", font=DEFAULT_FONT)
    label_key.pack(side="left")
    label_key_status = ctk.CTkLabel(key_row, text="", font=DEFAULT_FONT, width=30)
    label_key_status.pack(side="left", padx=(8,0))
    entry_key = ctk.CTkEntry(key_row, font=DEFAULT_FONT, show="*")
    entry_key.insert(0, yt_key)
    entry_key.pack(side="left", fill="x", expand=True, padx=(8,0))
    def toggle_key_visibility():
        if entry_key.cget("show") == "*":
            entry_key.configure(show="")
            btn_show_key.configure(text="非表示")
        else:
            entry_key.configure(show="*")
            btn_show_key.configure(text="表示")
    btn_show_key = ctk.CTkButton(key_row, text="表示", width=60, font=DEFAULT_FONT, command=toggle_key_visibility)
    btn_show_key.pack(side="left", padx=(8,0))
    # チャンネルIDラベル＋バリデーション
    channel_row = ctk.CTkFrame(youtube_tab, fg_color="transparent")
    channel_row.pack(fill="x", padx=20, pady=(10, 0))
    label_channel = ctk.CTkLabel(channel_row, text="YouTubeチャンネルID:", font=DEFAULT_FONT)
    label_channel.pack(side="left")
    label_channel_status = ctk.CTkLabel(channel_row, text="", font=DEFAULT_FONT, width=30)
    label_channel_status.pack(side="left", padx=(8,0))
    entry_channel = ctk.CTkEntry(youtube_tab, font=DEFAULT_FONT)
    entry_channel.insert(0, yt_channel)
    entry_channel.pack(fill="x", padx=20, pady=(0, 2))
    desc_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
    label_channel_desc = ctk.CTkLabel(youtube_tab, text="例: UCxxxx... /channel/UCxxxx... /user/xxxx /c/xxxx @handle も可 (URL貼付もOK)", font=("Meiryo", 12), text_color=desc_color)
    label_channel_desc.pack(anchor="w", padx=28, pady=(0, 8))
    # ポーリング間隔ラベル＋バリデーション
    poll_row = ctk.CTkFrame(youtube_tab, fg_color="transparent")
    poll_row.pack(fill="x", padx=20, pady=(10, 0))
    ctk.CTkLabel(poll_row, text="ポーリング間隔（秒）:", font=DEFAULT_FONT).pack(side="left")
    label_poll_status = ctk.CTkLabel(poll_row, text="", font=DEFAULT_FONT, width=30)
    label_poll_status.pack(side="left", padx=(8,0))
    entry_poll = ctk.CTkEntry(youtube_tab, font=DEFAULT_FONT)
    entry_poll.insert(0, yt_poll)
    entry_poll.pack(fill="x", padx=20, pady=(0, 10))
    def extract_channel_id_or_url(text):
        """
        入力がチャンネルID（UC...）か、URL（/channel/UC...、/user/...、/c/...、/hoge、/@handle）かを判定し、
        チャンネルIDまたは有効なURL/ハンドルを返す。無効ならNone。
        """
        # 公式ID
        if re.fullmatch(r'^UC[a-zA-Z0-9_-]{22}$', text):
            return text
        url = text.strip()
        # プロトコル・www有無を除去
        url = re.sub(r'^https?://(www\.)?', '', url)
        # @ハンドル（例: youtube.com/@example）
        m = re.search(r'^youtube\.com/(@[\w\-]+)', url)
        if m:
            return m.group(1)
        # /channel/UC... パターン
        m = re.search(r'^youtube\.com/channel/(UC[a-zA-Z0-9_-]{22})', url)
        if m:
            return m.group(1)
        # /user/...
        m = re.search(r'^youtube\.com/(user/[\w\-%]+)', url)
        if m:
            return m.group(1)
        # /c/...
        m = re.search(r'^youtube\.com/(c/[\w\-%]+)', url)
        if m:
            return m.group(1)
        # /hoge（予約語除外）
        m = re.search(r'^youtube\.com/([\w\-%]+)', url)
        reserved = [
            'watch', 'feed', 'playlist', 'user', 'c', 'channel', 'paid_memberships'
        ]
        if m and m.group(1) not in reserved:
            return m.group(1)
        # 直接@handle入力も許可
        if re.fullmatch(r'@([\w\-]+)', text):
            return text
        return None

    def validate_youtube():
        key = entry_key.get().strip()
        channel = entry_channel.get().strip()
        poll = entry_poll.get().strip()
        ok = True
        channel_valid = extract_channel_id_or_url(channel)
        if channel and channel_valid and channel != channel_valid:
            entry_channel.delete(0, "end")
            entry_channel.insert(0, channel_valid)
            channel = channel_valid
        if key:
            label_key_status.configure(text="✓", font=DESC_FONT, text_color="green")
        else:
            label_key_status.configure(text="✗", font=DESC_FONT, text_color="red")
            ok = False
        if channel and channel_valid and (channel_valid.startswith("UC") or channel_valid.startswith("@") or channel_valid.startswith("user/") or channel_valid.startswith("c/")):
            label_channel_status.configure(text="✓", font=DESC_FONT, text_color="green")
        else:
            label_channel_status.configure(text="✗", font=DESC_FONT, text_color="red")
            ok = False
        # ポーリング間隔のバリデーションは撤廃
        label_poll_status.configure(text="", font=DESC_FONT, text_color="green")
        return ok
    # ポーリング間隔は数字のみ・最大3桁に制限
    def poll_validate_char(new_value):
        return new_value.isdigit() and len(new_value) <= 3 or new_value == ""
    entry_poll.configure(validate="key", validatecommand=(entry_poll.register(poll_validate_char), '%P'))
    entry_key.bind("<KeyRelease>", lambda e: validate_youtube())
    entry_channel.bind("<KeyRelease>", lambda e: validate_youtube())
    entry_poll.bind("<KeyRelease>", lambda e: validate_youtube())
    validate_youtube()
    label_connect_status = ctk.CTkLabel(youtube_tab, text="", font=DEFAULT_FONT)
    def test_youtube_connect():
        import requests
        key = entry_key.get().strip()
        channel = entry_channel.get().strip()
        poll = entry_poll.get().strip()
        if not validate_youtube():
            label_connect_status.configure(text="✗ 入力エラー", font=DEFAULT_FONT, text_color="red")
            return
        test_channel_id = channel
        # UC以外の場合はAPIでUC IDに変換
        if not channel.startswith("UC"):
            # @handle
            if channel.startswith("@"):  # ハンドル
                url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={channel[1:]}&key={key}"
            # user/xxx
            elif channel.startswith("user/"):
                url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={channel[5:]}&key={key}"
            # c/xxx やその他
            else:
                # c/xxxやその他は検索APIで取得
                q = channel[2:] if channel.startswith("c/") else channel
                url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={q}&key={key}"
                resp = requests.get(url, timeout=10)
                data = resp.json()
                # 最初のチャンネルIDを取得
                items = data.get("items", [])
                if items:
                    test_channel_id = items[0]["snippet"]["channelId"]
                else:
                    label_connect_status.configure(text="✗ UC ID変換失敗", text_color="red")
                    return
            if not channel.startswith("c/") and not channel.startswith("user/"):
                resp = requests.get(url, timeout=10)
                data = resp.json()
                items = data.get("items", [])
                if data.get("items"):
                    test_channel_id = data["items"][0]["id"]
                elif data.get("id"):
                    test_channel_id = data["id"]
                elif data.get("items") is None and data.get("id"):
                    test_channel_id = data["id"]
                elif data.get("items") is None and data.get("items"):
                    test_channel_id = data["items"][0]["id"]
                elif data.get("items") is None and data.get("items") is None:
                    label_connect_status.configure(text="✗ UC ID変換失敗", text_color="red")
                    return
                else:
                    label_connect_status.configure(text="✗ UC ID変換失敗", text_color="red")
                    return
        try:
            url = f"https://www.googleapis.com/youtube/v3/channels?part=id&id={test_channel_id}&key={key}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if resp.status_code == 200 and data.get("items"):
                label_connect_status.configure(text="✓ 接続に成功しました", font=DEFAULT_FONT, text_color="green")
            elif resp.status_code == 403:
                label_connect_status.configure(text="✗ APIキーの権限エラーです", font=DEFAULT_FONT, text_color="red")
            else:
                label_connect_status.configure(text="✗ 認証に失敗しました", font=DEFAULT_FONT, text_color="red")
        except Exception as e:
            label_connect_status.configure(text=f"✗ 接続に失敗しました: {e}", font=DEFAULT_FONT, text_color="red")
    def save_youtube_settings():
        key = entry_key.get().strip()
        channel = entry_channel.get().strip()
        poll = entry_poll.get().strip()
        if not validate_youtube():
            tk.messagebox.showerror("エラー", "全ての項目を正しく入力してください。")
            return
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
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
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        except Exception as e:
            tk.messagebox.showerror('保存エラー', f'YouTube設定の保存に失敗しました: {e}')
            return
        tk.messagebox.showinfo('保存完了', 'YouTube設定を保存しました。')
    # ボタンを横並びにする
    spacer = ctk.CTkLabel(youtube_tab, text="", font=DEFAULT_FONT)
    spacer.pack(pady=(0, 10))
    label_connect_status.pack(anchor="w", padx=20, pady=(0, 10))
    # ↓ 結果表示をボタンの上に移動し、ボタン行を中央寄せ
    label_connect_status.pack_forget()
    label_connect_status.pack(pady=(0, 10))
    btn_row = ctk.CTkFrame(youtube_tab, fg_color="transparent")
    btn_row.pack(pady=(0, 10))
    btn_test = ctk.CTkButton(btn_row, text="接続テスト", font=BTN_FONT, command=test_youtube_connect)
    btn_test.pack(side="left", padx=(0, 10))
    btn_save = ctk.CTkButton(btn_row, text="保存", font=BTN_FONT, command=save_youtube_settings)
    btn_save.pack(side="left")
    btn_row.pack_configure(anchor="center")
    # --- appearance更新用 ---
    def update_appearance():
        desc_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        label_title.configure(text_color=desc_color)
        label_key.configure(text_color=desc_color)
        label_channel.configure(text_color=desc_color)
        label_channel_desc.configure(text_color=desc_color)
    youtube_tab.update_appearance = update_appearance
    return youtube_tab
