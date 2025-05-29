import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
import tkinter.ttk as ttk

from gui.tunnel_cloudflare_frame import TunnelCloudflareFrame
from gui.tunnel_custom_frame import TunnelCustomFrame
from gui.tunnel_localtunnel_frame import TunnelLocaltunnelFrame
from gui.tunnel_ngrok_frame import TunnelNgrokFrame


class TunnelConnection(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.selected_service = tk.StringVar(value="cloudflare")
        self.service_frames = {}

        # スタイルでラジオボタンのフォントサイズを大きく
        style = ttk.Style(self)
        style.configure("TRadiobutton", font=("Meiryo", 12))
        # 見出し
        headline = ttk.Label(self, text="使用するトンネルサービス", font=("Meiryo", 13, "bold"), anchor="w")
        headline.pack(fill=tk.X, padx=0, pady=(5, 0))
        # ラジオボタン
        radio_frame = ttk.Frame(self)
        radio_frame.pack(padx=10, pady=(10, 0), anchor="w")
        services = [
            ("Cloudflare", "cloudflare"),
            ("ngrok", "ngrok"),
            ("localtunnel", "localtunnel"),
            ("カスタム", "custom")
        ]
        for i, (label, value) in enumerate(services):
            ttk.Radiobutton(
                radio_frame,
                text=label,
                variable=self.selected_service,
                value=value,
                command=self.switch_service,
                style="TRadiobutton").grid(
                row=0,
                column=i,
                padx=8)
        # サービスごとのフレーム
        self.frame_area = ttk.Frame(self)
        self.frame_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.switch_service()

    def switch_service(self):
        for child in self.frame_area.winfo_children():
            child.destroy()
        val = self.selected_service.get()
        # settings.envにTUNNEL_SERVICEを書き込む
        import os
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        found_service = False
        for line in lines:
            if line.startswith('TUNNEL_SERVICE='):
                new_lines.append(f'TUNNEL_SERVICE={val}\n')
                found_service = True
            else:
                new_lines.append(line)
        if not found_service:
            new_lines.append(f'TUNNEL_SERVICE={val}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        # サービスに応じたフレームの表示
        if val == "cloudflare":
            frame = TunnelCloudflareFrame(self.frame_area)
        elif val == "ngrok":
            frame = TunnelNgrokFrame(self.frame_area)
        elif val == "localtunnel":
            frame = TunnelLocaltunnelFrame(self.frame_area)
        elif val == "custom":
            frame = TunnelCustomFrame(self.frame_area)
        else:
            frame = ttk.Label(self.frame_area, text="未対応のサービスです")
        frame.pack(fill=tk.BOTH, expand=True)
        # 設定状況タブも即時再描画
        parent = self.master
        while parent is not None:
            if hasattr(parent, 'tab_status') and hasattr(parent.tab_status, 'create_widgets'):
                parent.tab_status.create_widgets()
                break
            parent = getattr(parent, 'master', None)
