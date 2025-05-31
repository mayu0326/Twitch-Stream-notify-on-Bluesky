
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

DEFAULT_FONT = ("Yu Gothic UI", 17, "normal")
TITLE_FONT = ("Yu Gothic UI", 17, "normal")
DESC_FONT = ("Meiryo", 13, "normal")
BTN_FONT = ("Yu Gothic UI", 20, "normal")

class TwitchAccTab(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.btn_font = ctk.CTkFont(family="Yu Gothic UI", size=15, weight="normal")
        # 環境変数の読み込み
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        client_id = os.getenv('TWITCH_CLIENT_ID', '')
        client_secret = os.getenv('TWITCH_CLIENT_SECRET', '')
        broadcaster_id = os.getenv('TWITCH_BROADCASTER_ID', '')
        broadcaster_id_converted = os.getenv('TWITCH_BROADCASTER_ID_CONVERTED', '')

        # タイトルラベル
        self.label_title = ctk.CTkLabel(self, text="TwitchAPIキー/アカウント設定", font=TITLE_FONT)
        self.label_title.pack(pady=(10, 0))

        # クライアントID入力欄
        self.label_id = ctk.CTkLabel(self, text="TwitchクライアントID:", font=DEFAULT_FONT)
        self.label_id.pack(anchor="w", padx=20, pady=(10, 0))
        id_frame = ctk.CTkFrame(self)
        id_frame.pack(fill="x", padx=20, pady=(0, 10))
        entry_id = ctk.CTkEntry(id_frame, font=DEFAULT_FONT, show="*")
        entry_id.insert(0, client_id)
        entry_id.pack(side="left", fill="x", expand=True)

        # クライアントID表示/非表示切替ボタン
        def toggle_id_mask():
            if entry_id.cget("show") == "*":
                entry_id.configure(show="")
                btn_id_eye.configure(text="非表示")
            else:
                entry_id.configure(show="*")
                btn_id_eye.configure(text="表示")

        btn_id_eye = ctk.CTkButton(id_frame, text="表示", width=60, command=toggle_id_mask, font=self.btn_font)
        btn_id_eye.pack(side="right", padx=(5, 0))

        # クライアントシークレット入力欄
        self.label_secret = ctk.CTkLabel(self, text="Twitchクライアントシークレット:", font=DEFAULT_FONT)
        self.label_secret.pack(anchor="w", padx=20, pady=(10, 0))
        secret_frame = ctk.CTkFrame(self)
        secret_frame.pack(fill="x", padx=20, pady=(0, 10))
        entry_secret = ctk.CTkEntry(secret_frame, font=DEFAULT_FONT, show="*")
        entry_secret.insert(0, client_secret)
        entry_secret.pack(side="left", fill="x", expand=True)

        def toggle_secret_mask():
            if entry_secret.cget("show") == "*":
                entry_secret.configure(show="")
                btn_secret_eye.configure(text="非表示")
            else:
                entry_secret.configure(show="*")
                btn_secret_eye.configure(text="表示")

        btn_secret_eye = ctk.CTkButton(secret_frame, text="表示", width=60, command=toggle_secret_mask, font=self.btn_font)
        btn_secret_eye.pack(side="right", padx=(5, 0))

        self.label_broadcaster = ctk.CTkLabel(self, text="TwitchID（ユーザー名またはID）:", font=DEFAULT_FONT)
        self.label_broadcaster.pack(anchor="w", padx=20, pady=(10, 0))
        entry_broadcaster = ctk.CTkEntry(self, font=DEFAULT_FONT)
        entry_broadcaster.insert(0, broadcaster_id)
        entry_broadcaster.pack(fill="x", padx=20, pady=(0, 10))
        self.label_broadcaster_conv = ctk.CTkLabel(self, text="変換後のAPIアクセス用ID(表示用):", font=DEFAULT_FONT)
        self.label_broadcaster_conv.pack(anchor="w", padx=20, pady=(10, 0))
        entry_broadcaster_conv = ctk.CTkEntry(self, font=DEFAULT_FONT, state="readonly")
        entry_broadcaster_conv.insert(0, broadcaster_id_converted)
        entry_broadcaster_conv.pack(fill="x", padx=20, pady=(0, 10))
        self.status_label = ctk.CTkLabel(self, text="", font=DEFAULT_FONT)
        self.status_label.pack(pady=(5, 0))
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
        import eventsub
        def save_twitch_account():
            cid = entry_id.get().strip()
            csecret = entry_secret.get().strip()
            user_input = entry_broadcaster.get().strip()
            if not cid or not csecret or not user_input:
                self.status_label.configure(text="全ての項目を入力してください。", text_color="red")
                import tkinter.messagebox as messagebox
                messagebox.showerror("エラー", "全ての項目を入力してください。")
                return
            def is_numeric(s):
                return s.isdigit()
            converted_id = user_input
            os.environ['TWITCH_CLIENT_ID'] = cid
            os.environ['TWITCH_CLIENT_SECRET'] = csecret
            os.environ['TWITCH_BROADCASTER_ID'] = user_input
            try:
                if not is_numeric(user_input):
                    try:
                        converted_id = eventsub.get_broadcaster_id(user_input)
                        self.status_label.configure(text=f"Twitchユーザー名からID変換成功:", font=DESC_FONT, text_color="green")
                    except Exception as e:
                        self.status_label.configure(text=f"Twitchユーザー名からID変換失敗: {e}", font=DESC_FONT, text_color="red")
                        import tkinter.messagebox as messagebox
                        messagebox.showerror("変換エラー", f"Twitchユーザー名からID変換に失敗しました: {e}")
                        return
            except Exception as e:
                self.status_label.configure(text=f"Twitch API通信失敗: {e}", font=DESC_FONT, text_color="red")
                import tkinter.messagebox as messagebox
                messagebox.showerror("通信エラー", f"Twitch API通信に失敗: {e}")
                return
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../settings.env'))
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
                    new_lines.append(f'TWITCH_BROADCASTER_ID_CONVERTED={converted_id}\n')
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
                new_lines.append(f'TWITCH_BROADCASTER_ID_CONVERTED={converted_id}\n')
            try:
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
            except Exception as e:
                import tkinter.messagebox as messagebox
                messagebox.showerror('保存エラー', f'Twitch設定の保存に失敗しました: {e}')
                self.status_label.configure(text=f"Twitch設定の保存に失敗しました: {e}", text_color="red")
                return
            from dotenv import load_dotenv
            load_dotenv(env_path, override=True)
            broadcaster_id_converted_new = os.getenv('TWITCH_BROADCASTER_ID_CONVERTED', '')
            entry_broadcaster_conv.configure(state="normal")
            entry_broadcaster_conv.delete(0, "end")
            entry_broadcaster_conv.insert(0, broadcaster_id_converted_new)
            entry_broadcaster_conv.configure(state="readonly")
            # 保存完了時のメッセージ
            self.status_label.configure(text="TwitchユーザーID変換成功。情報を保存しました。", text_color="green")
            import tkinter.messagebox as messagebox
            messagebox.showinfo("保存完了", "Twitchアカウント情報を保存しました。")
        ctk.CTkButton(self, text="保存", font=BTN_FONT, command=save_twitch_account).pack(pady=(10, 10))

    def update_appearance(self):
        desc_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        self.label_title.configure(text_color=desc_color)
        self.label_id.configure(text_color=desc_color)
        self.label_secret.configure(text_color=desc_color)
        self.label_broadcaster.configure(text_color=desc_color)
        self.label_broadcaster_conv.configure(text_color=desc_color)
        self.status_label.configure(text_color=desc_color)

def create_twitch_tab(parent):
    return TwitchAccTab(parent)
