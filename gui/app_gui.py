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
        # 一般設定（サブタブ構成）

        class GeneralSettingsFrame(tk.Frame):
            def __init__(self, master=None):
                super().__init__(master)
                sub_notebook = tk.ttk.Notebook(self)
                sub_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                # タイムゾーン設定タブ
                import os
                from dotenv import load_dotenv

                class TimezoneSettingsFrame(tk.Frame):
                    def __init__(self, master=None):
                        super().__init__(master)
                        import tkinter.ttk as ttk
                        load_dotenv(os.path.join(
                            os.path.dirname(__file__), '../settings.env'))
                        timezone = os.getenv('TIMEZONE', 'system')
                        self.var_timezone = tk.StringVar(value=timezone)
                        # 中央寄せ用のサブフレーム
                        center_frame = tk.Frame(self)
                        center_frame.pack(expand=True)
                        ttk.Label(center_frame, text="タイムゾーン設定:", style="Big.TLabel").grid(
                            row=0, column=0, sticky=tk.W, pady=(10, 0))
                        presets = ["system", "Asia/Tokyo", "UTC",
                                   "America/New_York", "Europe/London"]
                        self.combo_tz = ttk.Combobox(
                            center_frame, values=presets, textvariable=self.var_timezone, width=24)
                        self.combo_tz.grid(
                            row=0, column=1, sticky=tk.W, pady=(10, 0))
                        self.combo_tz.configure(font=("Meiryo", 12))
                        ttk.Label(center_frame, text="任意のタイムゾーンを直接入力も可", style="Big.TLabel").grid(
                            row=1, column=0, columnspan=2, sticky=tk.W)
                        # 案内文を改行・太字・wraplength指定で見切れ防止
                        label1 = tk.Label(center_frame, text='"system" を指定すると、実行環境のシステムタイムゾーンを自動的に使用します。', font=(
                            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
                        label1.grid(row=2, column=0, columnspan=2,
                                    sticky=tk.W, pady=(5, 0))
                        label2 = tk.Label(center_frame, text='無効な値や空の場合は\nシステムタイムゾーンまたはUTCにフォールバックします。', font=(
                            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
                        label2.grid(row=3, column=0, columnspan=2, sticky=tk.W)
                        ttk.Button(center_frame, text="保存", command=self.save_timezone, style="Big.TButton").grid(
                            row=4, column=0, columnspan=2, sticky="ew", pady=(15, 0), padx=40)

                    def save_timezone(self):
                        env_path = os.path.join(
                            os.path.dirname(__file__), '../settings.env')
                        with open(env_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        new_lines = []
                        found = False
                        for line in lines:
                            if line.startswith('TIMEZONE='):
                                new_lines.append(
                                    f'TIMEZONE={self.var_timezone.get()}\n')
                                found = True
                            else:
                                new_lines.append(line)
                        if not found:
                            new_lines.append(
                                f'TIMEZONE={self.var_timezone.get()}\n')
                        with open(env_path, 'w', encoding='utf-8') as f:
                            f.writelines(new_lines)
                        load_dotenv(env_path, override=True)
                tz_frame = TimezoneSettingsFrame(sub_notebook)
                sub_notebook.add(tz_frame, text="タイムゾーン設定")
                # トンネル通信設定タブ

                class TunnelSettingsFrame(tk.Frame):
                    def __init__(self, master=None):
                        super().__init__(master)
                        import tkinter.ttk as ttk
                        import os
                        from dotenv import load_dotenv
                        load_dotenv(os.path.join(
                            os.path.dirname(__file__), '../settings.env'))
                        tunnel_cmd = os.getenv('TUNNEL_CMD', '')
                        self.var_tunnel_cmd = tk.StringVar(value=tunnel_cmd)
                        # 中央寄せ用のサブフレーム
                        center_frame = tk.Frame(self)
                        center_frame.pack(expand=True)
                        ttk.Label(center_frame, text="トンネル起動コマンド:", style="Big.TLabel").grid(
                            row=0, column=0, sticky=tk.W, pady=(10, 0))
                        entry = ttk.Entry(
                            center_frame, textvariable=self.var_tunnel_cmd, width=48)
                        entry.grid(row=0, column=1, sticky=tk.W, pady=(10, 0))
                        entry.configure(font=("Meiryo", 12))
                        # 案内文
                        label1 = tk.Label(center_frame, text='Cloudflare Tunnelやngrokなど\nトンネル通信アプリケーションを起動するためのコマンドを\nここに入力し設定してください。', font=(
                            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
                        label1.grid(row=1, column=0, columnspan=2,
                                    sticky=tk.W, pady=(5, 0))
                        label2 = tk.Label(center_frame, text='設定しない場合はトンネルを起動しません。', font=(
                            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
                        label2.grid(row=2, column=0, columnspan=2, sticky=tk.W)
                        ttk.Button(center_frame, text="保存", command=self.save_tunnel_cmd, style="Big.TButton").grid(
                            row=3, column=0, columnspan=2, sticky="ew", pady=(15, 0), padx=40)

                    def save_tunnel_cmd(self):
                        env_path = os.path.join(
                            os.path.dirname(__file__), '../settings.env')
                        with open(env_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        new_lines = []
                        found = False
                        for line in lines:
                            if line.startswith('TUNNEL_CMD='):
                                new_lines.append(
                                    f'TUNNEL_CMD={self.var_tunnel_cmd.get()}\n')
                                found = True
                            else:
                                new_lines.append(line)
                        if not found:
                            new_lines.append(
                                f'TUNNEL_CMD={self.var_tunnel_cmd.get()}\n')
                        with open(env_path, 'w', encoding='utf-8') as f:
                            f.writelines(new_lines)
                        load_dotenv(env_path, override=True)
                tunnel_frame = TunnelSettingsFrame(sub_notebook)
                sub_notebook.add(tunnel_frame, text="トンネル通信設定")
        self.tab_general = GeneralSettingsFrame(notebook)
        notebook.add(self.tab_general, text="一般設定")
        # アカウント設定

        class AccountSettingsFrame(tk.Frame):
            def __init__(self, master=None):
                super().__init__(master)
                tk.Label(self, text="ここにアカウント設定UIを実装", font=(
                    "Meiryo", 14)).pack(padx=20, pady=20)
        self.tab_account = AccountSettingsFrame(notebook)
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
