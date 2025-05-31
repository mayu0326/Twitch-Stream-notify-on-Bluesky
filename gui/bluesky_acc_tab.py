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

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
TITLE_FONT = ("Yu Gothic UI", 17, "normal")
DESC_FONT = ("Meiryo", 15, "normal")
BTN_FONT = ("Yu Gothic UI", 18, "normal")

class BlueskyAccTab(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        # 設定ファイルから初期値を取得
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        bsky_user = os.getenv('BLUESKY_USERNAME', '')
        bsky_pass = os.getenv('BLUESKY_APP_PASSWORD', '')
        # タイトルラベル
        self.label_title = ctk.CTkLabel(self, text="Blueskyアカウント設定", font=TITLE_FONT)
        self.label_title.pack(pady=(18, 6))
        # --- UI部品の生成 ---
        user_row = ctk.CTkFrame(self, fg_color="transparent")
        user_row.pack(fill="x", padx=28, pady=(8, 0))
        ctk.CTkLabel(user_row, text="Blueskyユーザー名:", font=DEFAULT_FONT).pack(side="left")
        label_user_status = ctk.CTkLabel(user_row, text="", font=DEFAULT_FONT, width=30)
        label_user_status.pack(side="left", padx=(8,0))
        # ユーザー名説明文
        desc_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        self.label_user_desc = ctk.CTkLabel(self, text="(例: your-handle.bsky.social または 独自ドメインID)", font=DESC_FONT, text_color=desc_color)
        self.label_user_desc.pack(anchor="w", padx=32, pady=(0, 4))
        entry_user = ctk.CTkEntry(self, font=DEFAULT_FONT)
        entry_user.insert(0, bsky_user)
        entry_user.pack(fill="x", padx=28, pady=(0, 10))
        # パスワードラベル
        pass_row = ctk.CTkFrame(self, fg_color="transparent")
        pass_row.pack(fill="x", padx=28, pady=(8, 0))
        ctk.CTkLabel(pass_row, text="Blueskyアプリパスワード:", font=DEFAULT_FONT).pack(side="left")
        label_pass_status = ctk.CTkLabel(pass_row, text="", font=DEFAULT_FONT, width=30)
        label_pass_status.pack(side="left", padx=(8,0))
        # パスワード説明文
        self.label_pass_desc = ctk.CTkLabel(self, text="（ログインパスワードではありません）", font=DESC_FONT, text_color=desc_color)
        self.label_pass_desc.pack(anchor="w", padx=32, pady=(0, 4))
        entry_pass = ctk.CTkEntry(self, show="*", font=DEFAULT_FONT)
        entry_pass.insert(0, bsky_pass)
        entry_pass.pack(fill="x", padx=28, pady=(0, 14))
        # --- 入力バリデーション関数 ---
        def validate_bluesky():
            user = entry_user.get().strip()
            pw = entry_pass.get().strip()
            ok = True
            if user and ("." in user or ":" in user):
                label_user_status.configure(text="✓", text_color="green")
            else:
                label_user_status.configure(text="✗", text_color="red")
                ok = False
            if pw and len(pw) >= 10:
                label_pass_status.configure(text="✓", text_color="green")
            else:
                label_pass_status.configure(text="✗", text_color="red")
                ok = False
            return ok
        entry_user.bind("<KeyRelease>", lambda e: validate_bluesky())
        entry_pass.bind("<KeyRelease>", lambda e: validate_bluesky())
        validate_bluesky()
        # --- 接続テストボタンと結果表示 ---
        self.label_connect_status = ctk.CTkLabel(self, text="", font=DESC_FONT)
        def test_bluesky_connect():
            import requests
            user = entry_user.get().strip()
            pw = entry_pass.get().strip()
            self.label_connect_status.configure(text="")
            if not validate_bluesky():
                self.label_connect_status.configure(text="✗ 入力エラー", text_color="red")
                return
            try:
                resp = requests.post(
                    "https://bsky.social/xrpc/com.atproto.server.createSession",
                    json={"identifier": user, "password": pw}, timeout=10)
                if resp.status_code == 200 and resp.json().get("accessJwt"):
                    label_user_status.configure(text="✓", text_color="green")
                    label_pass_status.configure(text="✓", text_color="green")
                    self.label_connect_status.configure(text="✓ 接続成功", text_color="green")
                else:
                    label_user_status.configure(text="✗", text_color="red")
                    label_pass_status.configure(text="✗", text_color="red")
                    self.label_connect_status.configure(text="✗ 認証失敗", text_color="red")
            except Exception as e:
                label_user_status.configure(text="✗", text_color="red")
                label_pass_status.configure(text="✗", text_color="red")
                self.label_connect_status.configure(text=f"✗ 接続失敗: {e}", text_color="red")
        # --- 設定保存処理 ---
        def save_bluesky_settings():
            user = entry_user.get().strip()
            pw = entry_pass.get().strip()
            if not validate_bluesky():
                tk.messagebox.showerror("エラー", "ユーザー名・アプリパスワードを正しく入力してください。")
                return
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../settings.env'))
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
            try:
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
            except Exception as e:
                tk.messagebox.showerror('保存エラー', f'Bluesky設定の保存に失敗しました: {e}')
                return
            tk.messagebox.showinfo('保存完了', 'Bluesky設定を保存しました。')
        # --- ボタン横並び配置 ---
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=(0, 10))
        btn_test = ctk.CTkButton(btn_frame, text="接続テスト", font=BTN_FONT, command=test_bluesky_connect)
        btn_test.pack(side="left", padx=(0, 10))
        btn_save = ctk.CTkButton(btn_frame, text="保存", font=BTN_FONT, command=save_bluesky_settings)
        btn_save.pack(side="left")
        spacer = ctk.CTkLabel(self, text="", font=DESC_FONT)
        spacer.pack(pady=(0, 4))
        self.label_connect_status.pack(anchor="w", padx=32, pady=(0, 10))
        # --- 初期化処理 ---
        def on_load_bluesky_settings():
            load_dotenv(os.path.join(os.path.dirname(__file__), '../../settings.env'))
            bsky_user = os.getenv('BLUESKY_USERNAME', '')
            bsky_pass = os.getenv('BLUESKY_APP_PASSWORD', '')
            entry_user.delete(0, "end")
            entry_user.insert(0, bsky_user)
            entry_pass.delete(0, "end")
            entry_pass.insert(0, bsky_pass)
        on_load_bluesky_settings()

    # --- appearance更新用メソッド ---
    def update_appearance(self):
        desc_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        self.label_user_desc.configure(text_color=desc_color)
        self.label_pass_desc.configure(text_color=desc_color)
        self.label_connect_status.configure(text_color=desc_color)
        # タイトルや他のラベルも必要に応じて追加
        # self.label_title.configure(text_color=desc_color)  # タイトル色も変えたい場合

# Blueskyタブ生成用関数

def create_bluesky_tab(parent):
    return BlueskyAccTab(parent)
