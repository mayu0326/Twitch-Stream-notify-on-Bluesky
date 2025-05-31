# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import customtkinter as ctk
from gui.account_settings_frame import AccountSettingsFrame
from gui.tunnel_connection import TunnelConnection
from gui.bluesky_post_settings_frame import BlueskyPostSettingsFrame
from gui.log_viewer import LogViewer  # 正しいクラス名に修正
from gui.logging_notification_frame import LoggingNotificationFrame
from gui.setup_wizard import SetupWizard
from gui.setting_status import SettingStatusFrame
from gui.main_control_frame import MainControlFrame
from gui.notification_customization_frame import NotificationCustomizationFrame
from gui.niconico_notice_frame import NiconicoNoticeFrame
from gui.twitch_notice_frame import TwitchNoticeFrame
from gui.youtube_notice_frame import YouTubeNoticeFrame
import configparser

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = "0.0.0-hotmock"

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

"""
エントリポイント: 初回起動時はSetupWizard、設定済みならMainWindowを表示
"""

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
SETTINGS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))

def load_user_settings():
    settings = {}
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        settings[k.strip()] = v.strip()
    return settings

def save_user_settings(settings):
    # 既存envを読み込み、該当キーだけ上書き
    lines = []
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, encoding='utf-8') as f:
            lines = f.readlines()
    keys = set(settings.keys())
    new_lines = []
    for line in lines:
        if '=' in line and not line.strip().startswith('#'):
            k = line.split('=', 1)[0].strip()
            if k in keys:
                new_lines.append(f"{k}={settings[k]}\n")
                keys.remove(k)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    for k in keys:
        new_lines.append(f"{k}={settings[k]}\n")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

class MainWindow(ctk.CTk):
    def __init__(self):
        user_settings = load_user_settings()
        appearance = user_settings.get('APPEARANCE_MODE', 'system')
        language = user_settings.get('LANGUAGE', '日本語')
        ctk.set_appearance_mode(appearance)
        self._user_settings = user_settings
        self._appearance = appearance
        self._language = language
        super().__init__()
        self.title("StreamNotifyonBluesky CustomTkinter ホットモック")
        self.geometry("740x650")
        self.resizable(False, False)
        self.tabview = ctk.CTkTabview(self)
        self._create_tabs()
        self.tabview.pack(fill="both", expand=True, pady=(0, 0))
        self._set_tabview_button_color()

    def _set_tabview_button_color(self):
        # appearanceに応じてタブメニューの文字色を切り替え
        mode = ctk.get_appearance_mode().lower()
        if mode == "light":
            fg = "#222"
        else:
            fg = "#fff"
        try:
            self.tabview._segmented_button.configure(text_color=fg)
        except Exception:
            pass

    def on_appearance_change(self, value):
        ctk.set_appearance_mode(value)
        self._appearance = value
        self._user_settings['APPEARANCE_MODE'] = value
        save_user_settings(self._user_settings)
        self._set_tabview_button_color()
        if hasattr(self, 'main_control_frame'):
            self.main_control_frame.update_appearance()
        if hasattr(self, 'account_settings_frame'):
            self.account_settings_frame.update_appearance()

    def on_language_change(self, value):
        self._language = value
        self._user_settings['LANGUAGE'] = value
        save_user_settings(self._user_settings)
        print(f"Language changed to: {value}")

    def _create_tabs(self):
        self.tabview.add("アプリ管理")
        self.tabview.add("状況")
        self.tabview.add("アカウント")
        self.tabview.add("Bluesky投稿")
        self.tabview.add("トンネル通信")
        self.tabview.add("ログ・通知")
        self.tabview.add("オプション")
        # アプリ管理
        self.tabview.tab("アプリ管理").grid_rowconfigure(0, weight=1)
        self.tabview.tab("アプリ管理").grid_columnconfigure(0, weight=1)
        self.main_control_frame = MainControlFrame(self.tabview.tab("アプリ管理"))
        self.main_control_frame.grid(row=0, column=0, sticky="nsew")
        # 状況
        self.tabview.tab("状況").grid_rowconfigure(0, weight=1)
        self.tabview.tab("状況").grid_columnconfigure(0, weight=1)
        self.setting_status_frame = SettingStatusFrame(self.tabview.tab("状況"))
        self.setting_status_frame.grid(row=0, column=0, sticky="nsew")
        # アカウント
        self.account_settings_frame = AccountSettingsFrame(self.tabview.tab("アカウント"))
        self.account_settings_frame.pack(fill="both", expand=True)
        # Bluesky投稿
        self.bluesky_post_settings_frame = BlueskyPostSettingsFrame(self.tabview.tab("Bluesky投稿"))
        self.bluesky_post_settings_frame.pack(fill="both", expand=True)
        # トンネル通信
        self.tabview.tab("トンネル通信").grid_rowconfigure(0, weight=1)
        self.tabview.tab("トンネル通信").grid_columnconfigure(0, weight=1)
        self.tunnel_connection = TunnelConnection(self.tabview.tab("トンネル通信"))
        self.tunnel_connection.grid(row=0, column=0, sticky="nsew")
        # ログ・通知
        self.logging_notification_frame = LoggingNotificationFrame(self.tabview.tab("ログ・通知"))
        self.logging_notification_frame.grid(row=0, column=0, sticky="nsew")
        # メインタブのフォント・サイズ・間隔を調整（被り防止）
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            height=24,
            corner_radius=4
        )

        # タブ切り替え時に設定状況タブをリロード
        original_command = self.tabview._segmented_button.cget("command")
        def on_tab_changed(value=None):
            self.tabview.set(value)  # まずタブを切り替える
            if self.tabview.get() == "設定状況":
                self.setting_status_frame.create_widgets()
        self.tabview._segmented_button.configure(command=on_tab_changed)
        # オプションタブの内容
        option_tab = self.tabview.tab("オプション")
        option_tab.grid_rowconfigure(0, weight=1)
        option_tab.grid_columnconfigure(0, weight=1)
        # 画面中央に大きく配置（空列を増やし、中央寄せをより厳密に）
        option_frame = ctk.CTkFrame(option_tab)
        option_frame.grid(row=0, column=0, sticky="nsew")
        for i in range(7):
            option_frame.grid_rowconfigure(i, weight=1)
        for j in range(7):
            option_frame.grid_columnconfigure(j, weight=1)
        # ダークモード切替
        ctk.CTkLabel(option_frame, text="外観モード:", font=("Yu Gothic UI", 18)).grid(row=2, column=2, sticky="e", pady=20, padx=(10,10))
        appearance_combo = ctk.CTkComboBox(
            option_frame,
            values=["system", "light", "dark"],
            width=180,
            font=("Yu Gothic UI", 18),
            command=self.on_appearance_change
        )
        appearance_combo.set(self._appearance)
        appearance_combo.grid(row=2, column=3, sticky="w", pady=20, padx=(10,10))
        # 言語切替
        ctk.CTkLabel(option_frame, text="言語:", font=("Yu Gothic UI", 18)).grid(row=4, column=2, sticky="e", pady=20, padx=(10,10))
        language_combo = ctk.CTkComboBox(
            option_frame,
            values=["日本語", "English"],
            width=180,
            font=("Yu Gothic UI", 18),
            command=self.on_language_change
        )
        language_combo.set(self._language)
        language_combo.grid(row=4, column=3, sticky="w", pady=20, padx=(10,10))

    def open_log_viewer(self):
        LogViewer(self)

    def on_close(self):
        self.destroy()

# python-dotenvの警告回避: settings.envの先頭に空行や不正な行がないかチェック
settings_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../settings.env'))
if os.path.exists(settings_env_path):
    with open(settings_env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 先頭に空行や#以外の不正な行、または「//」で始まる行があれば削除
    cleaned = []
    for line in lines:
        if (line.strip() == '' or line.strip().startswith('//')) and not cleaned:
            continue  # 先頭の空行や//コメントはスキップ
        if line.strip().startswith('#') and not cleaned:
            continue  # 先頭の#コメントもスキップ
        cleaned.append(line)
    # さらに先頭が#で始まるコメント行だけの場合もスキップ
    while cleaned and cleaned[0].strip().startswith('#'):
        cleaned.pop(0)
    if cleaned != lines:
        with open(settings_env_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned)

def is_first_setup():
    return not os.path.exists("settings.env")


if __name__ == "__main__":
    if is_first_setup():
        # --- 一時的な処理: 設定ファイルがなければ空ファイルを作成し、そのままMainWindowを開く ---
        if not os.path.exists("settings.env"):
            with open("settings.env", "w", encoding="utf-8") as f:
                pass  # 空ファイル作成
        MainWindow().mainloop()
        # --- 元のウィザード起動処理（新GUI完成後に復活させる） ---
        # import tkinter.messagebox as messagebox
        # root = tk.Tk()
        # root.withdraw()
        # result = messagebox.askokcancel(
        #     "初期セットアップ",
        #     "設定ファイルが見つかりません。\n初期セットアップを実行します。"
        # )
        # if result:
        #     def on_finish():
        #         root.destroy()
        #         MainWindow().mainloop()
        #     SetupWizard(master=root, on_finish=on_finish)
        #     root.mainloop()
        # else:
        #     root.destroy()
    else:
        MainWindow().mainloop()
