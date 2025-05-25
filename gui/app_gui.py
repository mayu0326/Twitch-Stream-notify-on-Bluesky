"""
エントリポイント: 初回起動時はSetupWizard、設定済みならMainWindowを表示
"""
import tkinter as tk
from setup_wizard import SetupWizard
from main_control_frame import MainControlFrame
from notification_customization_frame import NotificationCustomizationFrame
from settings_editor_dialog import SettingsEditorDialog
from log_viewer import LogViewer
from bluesky_post_settings_frame import BlueskyPostSettingsFrame
import os
from account_settings_frame import AccountSettingsFrame
from timezone_settings import TimeZoneSettings
from tunnel_connection import TunnelConnection


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stream notify on Bluesky - GUI版")
        self.geometry("596x535")
        self.resizable(False, False)
        self.create_menu()
        self.create_tabs()
        self._main_control_frame = None

    def on_bot_status_change(self, status):
        # MainControlFrameのステータス欄を更新
        if self._main_control_frame:
            self._main_control_frame.update_status_from_bot(status)

    def create_menu(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="設定の編集", command=self.open_settings_editor)
        filemenu.add_command(label="ログ閲覧", command=self.open_log_viewer)
        filemenu.add_separator()
        filemenu.add_command(label="終了", command=self.quit)
        menubar.add_cascade(label="ファイル", menu=filemenu)
        self.config(menu=menubar)

    def create_tabs(self):
        # タブのフォントサイズを10ptに設定
        style = tk.ttk.Style()
        style.configure("TNotebook.Tab", font=("Meiryo", 10))
        notebook = tk.ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # アプリ管理
        self._main_control_frame = MainControlFrame(
            notebook)
        notebook.add(self._main_control_frame, text="アプリ管理")
        # 一般設定（サブタブ構成）

        class GeneralSettingsFrame(tk.Frame):
            def __init__(self, master=None):
                super().__init__(master)
                sub_notebook = tk.ttk.Notebook(self)
                sub_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                # タイムゾーン設定タブ
                tz_frame = TimeZoneSettings(sub_notebook)
                sub_notebook.add(tz_frame, text="タイムゾーン設定")
                # トンネル通信設定タブ
                tunnel_frame = TunnelConnection(sub_notebook)
                sub_notebook.add(tunnel_frame, text="トンネル通信設定")
        self.tab_general = GeneralSettingsFrame(notebook)
        notebook.add(self.tab_general, text="一般設定")
        # アカウント設定

        class AccountSettingsFrameWrapper(AccountSettingsFrame):
            pass
        self.tab_account = AccountSettingsFrameWrapper(notebook)
        notebook.add(self.tab_account, text="アカウント設定")
        # Bluesky投稿設定
        self.tab_bluesky_post = BlueskyPostSettingsFrame(notebook)
        notebook.add(self.tab_bluesky_post, text="Bluesky投稿設定")
        # ログ・通知設定
        self.tab_notify = NotificationCustomizationFrame(notebook)
        notebook.add(self.tab_notify, text="ログ・通知設定")

    def open_settings_editor(self):
        SettingsEditorDialog(self)

    def open_log_viewer(self):
        LogViewer(self)


def is_first_setup():
    return not os.path.exists("settings.env")


if __name__ == "__main__":
    if is_first_setup():
        root = tk.Tk()
        root.withdraw()

        def on_finish():
            root.destroy()
            MainWindow().mainloop()

        SetupWizard(master=root, on_finish=on_finish)
        root.mainloop()
    else:
        MainWindow().mainloop()
