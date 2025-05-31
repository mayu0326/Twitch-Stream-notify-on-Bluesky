
# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

# Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# このプログラムはフリーソフトウェアです。フリーソフトウェア財団によって発行された
# GNU 一般公衆利用許諾契約書（バージョン2またはそれ以降）に基づき、再配布または
# 改変することができます。
#
# このプログラムは有用であることを願って配布されていますが、
# 商品性や特定目的への適合性についての保証はありません。
# 詳細はGNU一般公衆利用許諾契約書をご覧ください。
#
# このプログラムとともにGNU一般公衆利用許諾契約書が配布されているはずです。
# もし同梱されていない場合は、フリーソフトウェア財団までご請求ください。
# 住所: 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

from version_info import __version__
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
