import tkinter as tk
import tkinter.ttk as ttk
import os
from dotenv import load_dotenv


class TunnelConnection(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
        tunnel_cmd = os.getenv('TUNNEL_CMD', '')
        self.var_tunnel_cmd = tk.StringVar(value=tunnel_cmd)
        center_frame = tk.Frame(self)
        center_frame.pack(expand=True)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(center_frame, text="トンネル起動コマンド:", style="Big.TLabel").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        entry = ttk.Entry(
            center_frame, textvariable=self.var_tunnel_cmd, width=48)
        entry.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        entry.configure(font=("Meiryo", 12))
        label1 = tk.Label(center_frame, text='Cloudflare Tunnelやngrokなど\nトンネル通信アプリケーションを起動するためのコマンドを\nここに入力し設定してください。', font=(
            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
        label1.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        def open_cloudflare_link(event=None):
            import webbrowser
            webbrowser.open_new(
                "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
        link = tk.Label(center_frame, text="[CloudflareTunnelのインストール]がまだの方はこちら", font=(
            "Meiryo", 11, "underline"), fg="blue", cursor="hand2", anchor="w", justify="left", wraplength=420)
        link.grid(row=3, column=0, columnspan=2, sticky=tk.W)
        link.bind("<Button-1>", open_cloudflare_link)
        label2 = tk.Label(center_frame, text='コマンド例: cloudflared tunnel run <トンネル名>', font=(
            "Meiryo", 11, "bold"), anchor="w", justify="left", wraplength=420)
        label2.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        ttk.Button(center_frame, text="保存", command=self.save_tunnel_cmd, style="Big.TButton").grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(15, 0), padx=80)

    def save_tunnel_cmd(self):
        env_path = os.path.join(os.path.dirname(__file__), '../settings.env')
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.startswith('TUNNEL_CMD='):
                new_lines.append(f'TUNNEL_CMD={self.var_tunnel_cmd.get()}\n')
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f'TUNNEL_CMD={self.var_tunnel_cmd.get()}\n')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        load_dotenv(env_path, override=True)
