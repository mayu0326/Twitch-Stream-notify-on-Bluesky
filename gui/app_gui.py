"""
エントリポイント: 初回起動時はSetupWizard、設定済みならMainWindowを表示
"""
import tkinter as tk
from setup_wizard import SetupWizard
from main_control_frame import MainControlFrame
from notification_customization_frame import NotificationCustomizationFrame
from settings_editor_dialog import SettingsEditorDialog
from log_viewer import LogViewer
from bot_process_manager import BotProcessManager
from bluesky_post_settings_frame import BlueskyPostSettingsFrame
import os


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stream notify on Bluesky - GUI版")
        self.geometry("596x535")
        self.resizable(False, False)
        self.bot_manager = BotProcessManager()
        self.create_menu()
        self.create_tabs()

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
        self.tab_control = MainControlFrame(
            notebook, bot_manager=self.bot_manager)
        notebook.add(self.tab_control, text="アプリ管理")
        # Bluesky投稿設定
        self.tab_bluesky_post = BlueskyPostSettingsFrame(notebook)
        notebook.add(self.tab_bluesky_post, text="Bluesky投稿設定")
        # ログ・通知設定（旧:Discord通知設定）
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
