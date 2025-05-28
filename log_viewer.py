"""
ログファイル閲覧用サブウィンドウ
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os


class LogViewer(ttk.Frame):
    def __init__(self, master=None, log_dir="logs"):
        super().__init__(master)
        self.log_dir = log_dir
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frame, text="ログファイルを選択:").pack(anchor=tk.W)
        self.cmb_file = ttk.Combobox(frame, values=self.get_log_files())
        self.cmb_file.pack(fill=tk.X, pady=5)
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="開く", command=self.load_log).pack(side=tk.RIGHT)
        ttk.Button(
            btn_frame,
            text="再読込",
            command=self.reload_log_files).pack(
            side=tk.RIGHT,
            padx=(
                0,
                8))

        self.log_frame = ttk.Frame(self)
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # テーブル表示用Treeview（3列: 日付, レベル, 内容）
        self.tree = ttk.Treeview(
            self.log_frame,
            columns=(
                "date",
                "level",
                "message"),
            show="headings")
        self.tree.heading("date", text="日付")
        self.tree.heading("level", text="レベル")
        self.tree.heading("message", text="内容")
        self.tree.column("date", width=160)
        self.tree.column("level", width=80)
        self.tree.column("message", width=600)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # テキスト表示用（従来のTextウィジェット）
        self.txt_log = tk.Text(self.log_frame, height=20, wrap=tk.WORD, state=tk.DISABLED)
        self.txt_log.pack_forget()  # デフォルト非表示

    def get_log_files(self):
        try:
            files = [f for f in os.listdir(self.log_dir) if f.endswith(('.log', '.csv'))]
            if not files:
                return ["（ログファイルがありません）"]
            return files
        except Exception:
            return ["（ログファイルがありません）"]

    def reload_log_files(self):
        files = self.get_log_files()
        self.cmb_file['values'] = files
        if files:
            self.cmb_file.set(files[0])

    def format_log_content(self, content):
        # Treat multiple consecutive dots as a single Japanese period (。)
        content = content.replace('...', '。')
        # Add line breaks after periods, colons, before brackets, and after ellipses
        formatted_content = content.replace('。', '。')
        formatted_content = formatted_content.replace(':', ':')
        formatted_content = formatted_content.replace('（', '\n（')
        formatted_content = formatted_content.replace('[', '\n[')
        return formatted_content

    def load_log(self):
        filename = self.cmb_file.get()
        if not filename:
            messagebox.showwarning("ファイル未選択", "ログファイルを選択してください")
            return
        path = os.path.join(self.log_dir, filename)
        try:
            # .csvなら投稿履歴としてテーブル表示、.logなら従来のパース
            if filename.endswith('.csv'):
                self.txt_log.pack_forget()
                self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
                for row in self.tree.get_children():
                    self.tree.delete(row)
                with open(path, encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i == 0 and (',' in line):
                            continue  # ヘッダ行はスキップ
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            self.tree.insert('', 'end', values=(
                                parts[0], parts[1], ','.join(parts[2:])))
                        elif len(parts) == 2:
                            self.tree.insert('', 'end', values=(parts[0], parts[1], ''))
                        elif len(parts) == 1:
                            self.tree.insert('', 'end', values=(parts[0], '', ''))
            else:
                self.tree.pack_forget()
                self.txt_log.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                formatted_content = self.format_log_content(content)
                self.txt_log.config(state=tk.NORMAL)
                self.txt_log.delete(1.0, tk.END)
                self.txt_log.insert(tk.END, formatted_content)
                self.txt_log.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルを開けません: {e}")
