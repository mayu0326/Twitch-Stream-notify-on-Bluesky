import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

"""
.env編集用ダイアログ（バリデーション・マスク表示対応）
"""
import customtkinter as ctk


class SettingsEditorDialog(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("設定エディタ（ダミー）")
        self.geometry("400x300")
        # ダミー変数
        self.var_setting1 = ctk.StringVar(value='値1')
        self.var_setting2 = ctk.StringVar(value='値2')
        # UI部品のみ配置
        ctk.CTkLabel(self, text="設定項目1:").pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.var_setting1).pack(pady=5)
        ctk.CTkLabel(self, text="設定項目2:").pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.var_setting2).pack(pady=5)
        ctk.CTkButton(self, text="保存", command=self._dummy).pack(pady=20)
        ctk.CTkButton(self, text="閉じる", command=self.destroy).pack(pady=5)

    def _dummy(self, *args, **kwargs):
        # 何も動作しないダミー
        pass
