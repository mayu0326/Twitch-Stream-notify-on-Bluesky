import customtkinter as ctk
from .timezone_settings import TimezoneSettingsFrame

DEFAULT_FONT = ("Yu Gothic UI", 12, "normal")

class NotificationCustomizationFrame(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        tabview = ctk.CTkTabview(self, width=800, height=500)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        # --- タイムゾーン設定タブ ---
        tz_frame = TimezoneSettingsFrame(tabview)
        tabview.add("タイムゾーン設定")
        tz_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("タイムゾーン設定"))
        # --- ログ/コンソール設定タブ ---
        from .logging_console_frame import LoggingConsoleFrame
        log_console_frame = LoggingConsoleFrame(tabview)
        tabview.add("ログ/コンソール設定")
        log_console_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("ログ/コンソール設定"))
        # --- Discordタブ ---
        from .discord_notification_frame import DiscordNotificationFrame
        discord_frame = DiscordNotificationFrame(tabview)
        tabview.add("Discord通知設定")
        discord_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("Discord通知設定"))
        # --- ログビューアタブ ---
        from .log_viewer import LogViewerFrame
        log_viewer_frame = LogViewerFrame(tabview)
        tabview.add("ログビューア")
        log_viewer_frame.pack(fill="both", expand=True, padx=10, pady=10, in_=tabview.tab("ログビューア"))
