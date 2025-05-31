import customtkinter as ctk
from .twitch_acc_tab import create_twitch_tab
from .bluesky_acc_tab import create_bluesky_tab
from .youtube_acc_tab import create_youtube_tab
from .niconico_acc_tab import create_niconico_tab
from .webhook_acc_tab import WebhookAccTab
from .webhookurl_acc_tab import create_webhookurl_tab

DEFAULT_FONT = ("Yu Gothic UI", 15, "normal")

class WebhookTabsFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=0, pady=0)
        tabview._segmented_button.configure(font=DEFAULT_FONT)
        # Webhookサブタブ
        tabview.add("Webhook")
        self.webhook_tab = WebhookAccTab(tabview.tab("Webhook"))
        self.webhook_tab.pack(fill="both", expand=True)
        # WebhookURLサブタブ
        tabview.add("WebhookURL")
        self.webhookurl_tab = create_webhookurl_tab(tabview.tab("WebhookURL"))
        self.webhookurl_tab.pack(fill="both", expand=True)
        self.tabview = tabview
        # appearanceに応じてサブタブボタンの文字色を初期化時にも設定
        seg_color = "black" if ctk.get_appearance_mode() == "Light" else "white"
        self.tabview._segmented_button.configure(text_color=seg_color)

    def update_appearance(self):
        if hasattr(self.webhook_tab, 'update_appearance'):
            self.webhook_tab.update_appearance()
        # WebhookURLタブは現状appearance未対応だが、必要ならここで拡張
        seg_color = "black" if ctk.get_appearance_mode() == "Light" else "white"
        self.tabview._segmented_button.configure(text_color=seg_color)

class AccountSettingsFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        tabview._segmented_button.configure(font=DEFAULT_FONT)
        # Twitchタブ
        tabview.add("Twitch")
        self.twitch_tab = create_twitch_tab(tabview.tab("Twitch"))
        self.twitch_tab.pack(fill="both", expand=True)
        # Blueskyタブ
        tabview.add("Bluesky")
        self.bluesky_tab = create_bluesky_tab(tabview.tab("Bluesky"))
        self.bluesky_tab.pack(fill="both", expand=True)
        # YouTubeタブ
        tabview.add("YouTube")
        self.youtube_tab = create_youtube_tab(tabview.tab("YouTube"))
        self.youtube_tab.pack(fill="both", expand=True)
        # ニコニコタブ
        tabview.add("ニコニコ")
        self.niconico_tab = create_niconico_tab(tabview.tab("ニコニコ"))
        self.niconico_tab.pack(fill="both", expand=True)
        # Webhookタブ（サブタブ付き）
        tabview.add("Webhook")
        self.webhook_tabs = WebhookTabsFrame(tabview.tab("Webhook"))
        self.webhook_tabs.pack(fill="both", expand=True)
        self.tabview = tabview

    def update_appearance(self):
        # 各タブのappearance更新
        if hasattr(self.twitch_tab, 'update_appearance'):
            self.twitch_tab.update_appearance()
        if hasattr(self.bluesky_tab, 'update_appearance'):
            self.bluesky_tab.update_appearance()
        if hasattr(self.youtube_tab, 'update_appearance'):
            self.youtube_tab.update_appearance()
        if hasattr(self.niconico_tab, 'update_appearance'):
            self.niconico_tab.update_appearance()
        # Webhookサブタブ群のappearance
        if hasattr(self, 'webhook_tabs') and hasattr(self.webhook_tabs, 'update_appearance'):
            self.webhook_tabs.update_appearance()
        # タブボタンの色も必要ならここで更新
        seg_color = "black" if ctk.get_appearance_mode() == "Light" else "white"
        self.tabview._segmented_button.configure(text_color=seg_color)