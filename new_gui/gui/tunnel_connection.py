import customtkinter as ctk
from .tunnel_cloudflare_frame import TunnelCloudflareFrame
from .tunnel_ngrok_frame import TunnelNgrokFrame
from .tunnel_localtunnel_frame import TunnelLocalTunnelFrame
from .tunnel_custom_frame import TunnelCustomFrame
import os

DEFAULT_FONT = "Yu Gothic UI", 17, "normal"

def remove_tunnel_settings(env_path):
    tunnel_keys = [
        "TUNNEL_SERVICE", "TUNNEL_CMD", "TUNNEL_NAME",
        "NGROK_AUTH_TOKEN", "NGROK_PORT", "NGROK_PROTOCOL",
        "LOCALTUNNEL_PORT", "LOCALTUNNEL_CMD", "CUSTOM_TUNNEL_CMD"
    ]
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            key = line.split("=", 1)[0].strip()
            if key not in tunnel_keys:
                new_lines.append(line)
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

class TunnelConnection(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True, fill="both")
        # settings.envからTUNNEL_SERVICEを取得し、なければ"none"に
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        service = "none"
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('TUNNEL_SERVICE='):
                        val = line.strip().split('=', 1)[1]
                        if val:
                            service = val
                        break
        self.var_service = ctk.StringVar(value=service)
        # ラベルとプルダウンは常に上部に固定
        label_service = ctk.CTkLabel(self.center_frame, text="トンネルサービス:", font=DEFAULT_FONT)
        label_service.pack(pady=(30, 5), anchor="center")
        self.combo = ctk.CTkComboBox(
            self.center_frame,
            values=["none","cloudflare", "ngrok", "localtunnel", "custom"],
            variable=self.var_service,
            font=DEFAULT_FONT,
            width=400,
            command=self.on_service_change,
            state="readonly",
            justify="center"
        )
        self.combo.pack(pady=5, anchor="center")
        # サービスごとの内容を表示するエリア
        self.dynamic_area = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.dynamic_area.pack(expand=True, fill="both")
        self.current_frame = None
        self.on_service_change()

    def on_service_change(self, *args):
        for child in self.dynamic_area.winfo_children():
            child.destroy()
        service = self.var_service.get()
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        self.save_tunnel_service_to_env(env_path, service)
        frame = None
        if service == "cloudflare":
            frame = TunnelCloudflareFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "ngrok":
            frame = TunnelNgrokFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "localtunnel":
            frame = TunnelLocalTunnelFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "custom":
            frame = TunnelCustomFrame(self.dynamic_area)
            frame.pack(expand=True)
        elif service == "none":
            frame = ctk.CTkFrame(self.dynamic_area)
            frame.pack(expand=True, fill="both")
            label_explain = ctk.CTkLabel(frame, text="トンネル関連設定を初期化するには下記のボタンを押してください", font=DEFAULT_FONT)
            label_explain.pack(pady=(30, 20), anchor="center")
            def on_remove_tunnel_settings():
                from tkinter import messagebox
                result = messagebox.askyesno("確認", "トンネル関連設定を本当に削除しますか？\nこの操作は元に戻せません。", icon='warning')
                if result:
                    remove_tunnel_settings(env_path)
                    messagebox.showinfo("削除完了", "トンネル関連設定を削除しました。")
            btn = ctk.CTkButton(frame, text="トンネル設定を初期化", font=DEFAULT_FONT, width=200,
                                command=on_remove_tunnel_settings)
            btn.pack(anchor="center")
        else:
            # 想定外の値の場合は空フレーム
            frame = ctk.CTkFrame(self.dynamic_area)
            frame.pack(expand=True, fill="both")
        self.current_frame = frame

    def save_tunnel_service_to_env(self, env_path, service):
        # TUNNEL_SERVICEをsettings.envに保存
        lines = []
        found = False
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip().startswith("TUNNEL_SERVICE="):
                    lines[i] = f"TUNNEL_SERVICE={service}\n"
                    found = True
                    break
        if not found:
            lines.append(f"TUNNEL_SERVICE={service}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def load_last_service(self):
        # settings.envからTUNNEL_SERVICEを読み込む
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("TUNNEL_SERVICE="):
                        value = line.strip().split("=", 1)[1]
                        if value in ["cloudflare", "ngrok", "localtunnel", "custom", "none"]:
                            self.var_service.set(value)
                        break

    def after(self, ms, func):
        # afterメソッドのラッパー（CustomTkinterのFrameにafterがない場合用）
        self.master.after(ms, func)

    def pack(self, *args, **kwargs):
        # pack時に前回のサービスを復元
        self.load_last_service()
        super().pack(*args, **kwargs)
        # サービス復元後にon_service_changeを呼ぶ
        self.after(100, self.on_service_change)
