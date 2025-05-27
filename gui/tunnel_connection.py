import tkinter as tk
import tkinter.ttk as ttk

from tunnel_cloudflare_frame import TunnelCloudflareFrame
from tunnel_custom_frame import TunnelCustomFrame
from tunnel_localtunnel_frame import TunnellocaltunnelFrame
from tunnel_ngrok_frame import TunnelNgrokFrame


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
            ttk.Radiobutton(radio_frame, text=label, variable=self.selected_service, value=value, command=self.switch_service, style="TRadiobutton").grid(row=0, column=i, padx=8)
        # サービスごとのフレーム
        self.frame_area = ttk.Frame(self)
        self.frame_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.switch_service()

    def switch_service(self):
        for child in self.frame_area.winfo_children():
            child.destroy()
        val = self.selected_service.get()
        if val == "cloudflare":
            frame = TunnelCloudflareFrame(self.frame_area)
        elif val == "ngrok":
            frame = TunnelNgrokFrame(self.frame_area)
        elif val == "localtunnel":
            frame = TunnellocaltunnelFrame(self.frame_area)
        elif val == "custom":
            frame = TunnelCustomFrame(self.frame_area)
        else:
            frame = ttk.Label(self.frame_area, text="未対応のサービスです")
        frame.pack(fill=tk.BOTH, expand=True)
