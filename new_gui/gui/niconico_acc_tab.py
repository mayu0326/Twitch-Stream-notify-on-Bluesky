import os
import customtkinter as ctk
from dotenv import load_dotenv
import tkinter as tk
from tkinter import Text, DISABLED, NORMAL

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")
TITLE_FONT = ("Yu Gothic UI", 17, "normal")
BTN_FONT = ("Yu Gothic UI", 18, "normal")

def create_niconico_tab(parent):
    #ニコニコアカウント設定用のタブを作成し、必要なウィジェットを配置する。
    #設定の保存やRSS取得もこの関数内で管理する。
    niconico_tab = ctk.CTkFrame(parent)
    load_dotenv(os.path.join(os.path.dirname(__file__), '../settings.env'))
    nico_id = os.getenv('NICONICO_USER_ID', '')
    nico_poll = os.getenv('NICONICO_LIVE_POLL_INTERVAL', '60')
    # タイトルラベル
    label_title = ctk.CTkLabel(niconico_tab, text="ニコニコアカウント設定", font=TITLE_FONT)
    label_title.pack(pady=(18, 6))
    # ユーザーIDの入力欄
    label_id = ctk.CTkLabel(niconico_tab, text="ニコニコユーザーID（数字またはユーザーページURL）:", font=DEFAULT_FONT)
    label_id.pack(anchor="w", padx=20, pady=(10, 0))
    entry_id = ctk.CTkEntry(niconico_tab, font=DEFAULT_FONT)
    entry_id.insert(0, nico_id)
    entry_id.pack(fill="x", padx=20, pady=(0, 10))
    def extract_nico_user_id(text):
        import re
        # https://www.nicovideo.jp/user/123456 などから数字部分を抽出
        m = re.search(r'user/(\d+)', text)
        if m:
            return m.group(1)
        # 数字のみも許可
        if re.fullmatch(r'\d+', text):
            return text
        return ''
    def on_id_entry_change(event=None):
        val = entry_id.get().strip()
        extracted = extract_nico_user_id(val)
        if val and extracted and val != extracted:
            entry_id.delete(0, "end")
            entry_id.insert(0, extracted)
    entry_id.bind("<FocusOut>", on_id_entry_change)
    entry_id.bind("<Return>", on_id_entry_change)
    # ポーリング間隔の入力欄
    label_poll = ctk.CTkLabel(niconico_tab, text="ポーリング間隔（秒）:", font=DEFAULT_FONT)
    label_poll.pack(anchor="w", padx=20, pady=(10, 0))
    entry_poll = ctk.CTkEntry(niconico_tab, font=DEFAULT_FONT)
    entry_poll.insert(0, nico_poll)
    entry_poll.pack(fill="x", padx=20, pady=(0, 10))

    def save_niconico_settings():
        # 入力されたユーザーIDとポーリング間隔を.envファイルに保存し、
        # RSSフィードの取得結果を表示する。
        user_id_raw = entry_id.get().strip()
        user_id = extract_nico_user_id(user_id_raw)
        poll = entry_poll.get().strip()
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../settings.env'))
        lines = []
        found_id = found_poll = False
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.startswith('NICONICO_USER_ID='):
                new_lines.append(f'NICONICO_USER_ID={user_id}\n')
                found_id = True
            elif line.startswith('NICONICO_LIVE_POLL_INTERVAL='):
                new_lines.append(f'NICONICO_LIVE_POLL_INTERVAL={poll}\n')
                found_poll = True
            else:
                new_lines.append(line)
        if not found_id:
            new_lines.append(f'NICONICO_USER_ID={user_id}\n')
        if not found_poll:
            new_lines.append(f'NICONICO_LIVE_POLL_INTERVAL={poll}\n')
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        except Exception as e:
            tk.messagebox.showerror('保存エラー', f'ニコニコ設定の保存に失敗しました: {e}')
            return
        tk.messagebox.showinfo('保存完了', 'ニコニコ設定を保存しました。')
        if not user_id:
            set_rss_text('IDが設定されていないため処理をスキップしました')
        else:
            rss_results = fetch_niconico_rss(user_id)
            set_rss_text(rss_results)

    btn_save = ctk.CTkButton(niconico_tab, text="保存", font=BTN_FONT, command=save_niconico_settings)
    btn_save.pack(pady=(10, 0))
    desc_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
    label_rss_title = ctk.CTkLabel(niconico_tab, text="入力IDによる動画検索結果", font=BTN_FONT, anchor="w", justify=tk.LEFT, text_color=desc_color)
    label_rss_title.pack(anchor="w", padx=20, pady=(10, 0))
    # --- appearance更新用 ---
    def update_appearance():
        desc_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        label_title.configure(text_color=desc_color)
        label_id.configure(text_color=desc_color)
        label_poll.configure(text_color=desc_color)
        label_rss_title.configure(text_color=desc_color)
    niconico_tab.update_appearance = update_appearance
    text_rss = Text(niconico_tab, height=10, font=DEFAULT_FONT, wrap="word", cursor="arrow")
    if ctk.get_appearance_mode() == "Dark":
        text_rss.configure(bg="#222222", fg="#FFFFFF", insertbackground="#FFFFFF")
    text_rss.pack(fill="both", padx=20, pady=(2, 0))
    text_rss.config(state=DISABLED)

    def open_url(event):
        """
        テキストウィジェット内のリンクをクリックした際にブラウザで開く。
        """
        import webbrowser
        idx = text_rss.index("@%s,%s" % (event.x, event.y))
        tag_names = text_rss.tag_names(idx)
        for tag in tag_names:
            if tag.startswith("url_"):
                url = tag.split("url_", 1)[1]
                webbrowser.open(url)
                return

    text_rss.tag_configure("link", foreground="blue", underline=True)
    text_rss.bind("<Button-1>", open_url)

    def set_rss_text(results):
        """
        RSS取得結果をテキストウィジェットに表示する。
        リンクはクリック可能にする。
        """
        text_rss.config(state=NORMAL)
        text_rss.delete("1.0", "end")
        if isinstance(results, list):
            for i, (title, link) in enumerate(results):
                text_rss.insert("end", f"・{title}\n  ")
                if link:
                    tag = f"url_{link}"
                    start_idx = text_rss.index("end-1c")
                    text_rss.insert("end", link, tag)
                    end_idx = text_rss.index("end-1c")
                    text_rss.tag_add(tag, start_idx, end_idx)
                    text_rss.tag_config(tag, foreground="blue", underline=True)
                text_rss.insert("end", "\n\n")
        else:
            text_rss.insert("end", results)
        text_rss.config(state=DISABLED)

    def fetch_niconico_rss(user_id):
        """
        指定したユーザーIDのニコニコ動画RSSフィードを取得し、
        タイトルとリンクのリストを返す。
        """
        import requests
        import xml.etree.ElementTree as ET
        try:
            url = f"https://www.nicovideo.jp/user/{user_id}/video?rss=2.0"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            items = root.findall('.//item')
            results = []
            for item in items[:3]:
                title = item.find('title').text if item.find('title') is not None else "(タイトル取得失敗)"
                link = item.find('link').text if item.find('link') is not None else ""
                results.append((title, link))
            if not results:
                return "動画が見つかりませんでした(検索は成功しました)"
            return results
        except Exception as e:
            return f"RSS取得失敗: {e}"

    return niconico_tab
