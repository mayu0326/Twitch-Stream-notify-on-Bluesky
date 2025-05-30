# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from gui.account_settings_frame import AccountSettingsFrame
from gui.tunnel_connection import TunnelConnection
from gui.bluesky_post_settings_frame import BlueskyPostSettingsFrame
from gui.log_viewer import LogViewer
from gui.settings_editor_dialog import SettingsEditorDialog
from gui.logging_notification_frame import LoggingNotificationFrame
from gui.setup_wizard import SetupWizard
from gui.setting_status import SettingStatusFrame
from gui.main_control_frame import MainControlFrame
from version_info import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

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


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stream notify on Bluesky - 設定用GUI")
        self.geometry("596x535")
        self.resizable(False, False)
        self.create_menu()
        self.create_tabs()
        self._main_control_frame = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_menu(self):
        menubar = tk.Menu(self)
        pass
        self.config(menu=menubar)

    def create_tabs(self):
        style = tk.ttk.Style()
        style.configure("TNotebook.Tab", font=("Meiryo", 10))
        notebook = tk.ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.notebook = notebook  # ←インスタンス変数で保持

        # アプリ管理タブ（サーバー起動・停止・ステータス管理）
        self.tab_app_control = MainControlFrame(notebook)
        notebook.add(self.tab_app_control, text="アプリ管理")

        # 設定状況タブ
        self.tab_status = SettingStatusFrame(notebook)
        notebook.add(self.tab_status, text="設定状況")
        # アカウント設定タブ

        class AccountSettingsFrameWrapper(AccountSettingsFrame):
            pass
        self.tab_account = AccountSettingsFrameWrapper(notebook)
        notebook.add(self.tab_account, text="アカウント設定")
        # Bluesky投稿設定タブ
        self.tab_bluesky_post = BlueskyPostSettingsFrame(notebook)
        notebook.add(self.tab_bluesky_post, text="Bluesky投稿設定")
        # トンネル通信設定タブ（一般設定から移動）
        self.tab_tunnel = TunnelConnection(notebook)
        notebook.add(self.tab_tunnel, text="トンネル通信設定")
        # ログ・通知設定タブ
        self.tab_notify = LoggingNotificationFrame(notebook)
        notebook.add(self.tab_notify, text="ログ・通知設定")

        # タブ切り替え時に設定状況タブをリロード
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        notebook = event.widget
        # 現在選択されているタブのインデックス
        idx = notebook.index(notebook.select())
        # 設定状況タブが選択された場合のみ再描画
        if notebook.tab(idx, "text") == "設定状況":
            # SettingStatusFrameの内容を再描画
            self.tab_status.create_widgets()

    def open_settings_editor(self):
        SettingsEditorDialog(self)

    def open_log_viewer(self):
        LogViewer(self)

    def on_close(self):
        self.destroy()


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
