# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from pathlib import Path
from dotenv import load_dotenv
import os
from logging.handlers import TimedRotatingFileHandler
import logging
from version import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

# Twitch Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.


def configure_logging(app=None):
    # 環境設定ファイルの場所
    env_path = Path(__file__).parent / "settings.env"
    load_dotenv(dotenv_path=env_path)

    # ログレベルや保管日数の設定
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LEVEL_MAP = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = LEVEL_MAP.get(LOG_LEVEL, logging.INFO)

    DISCORD_NOTIFY_LEVEL = os.getenv(
        "discord_notify_level", "CRITICAL").upper()
    LEVEL_MAP = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    discord_level = LEVEL_MAP.get(DISCORD_NOTIFY_LEVEL, logging.CRITICAL)
    log_retention_days = int(os.getenv("LOG_RETENTION_DAYS", "14"))
    # 監査ログ専用ロガーとハンドラ
    audit_logger = logging.getLogger("AuditLogger")
    audit_logger.setLevel(logging.INFO)
    audit_format = logging.Formatter("%(asctime)s [AUDIT] %(message)s")
    audit_file_handler = TimedRotatingFileHandler(
        "logs/audit.log",
        when="D",
        interval=1,
        backupCount=log_retention_days,
        encoding="utf-8",
    )
    audit_file_handler.setLevel(logging.INFO)
    audit_file_handler.setFormatter(audit_format)
    audit_logger.addHandler(audit_file_handler)

    # ロガー作成
    logger = logging.getLogger("AppLogger")
    logger.setLevel(log_level)
    logger.propagate = False

    # エラーログとコンソールハンドラ
    error_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    info_file_handler = TimedRotatingFileHandler(
        "logs/app.log",
        when="D",
        interval=1,
        backupCount=log_retention_days,
        encoding="utf-8",
    )
    info_file_handler.setLevel(log_level)
    info_file_handler.setFormatter(error_format)
    logger.addHandler(info_file_handler)

    error_file_handler = TimedRotatingFileHandler(
        "logs/error.log",
        when="D",
        interval=1,
        backupCount=log_retention_days,
        encoding="utf-8",
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(error_format)

    # コンソール出力機能の実装
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(error_format)

    # ハンドラをロガーに追加
    logger.addHandler(error_file_handler)
    logger.addHandler(console_handler)

    # エラー通知用Discord_Webhookの設定
    discord_webhook_url = os.getenv("discord_error_notifier_url")
    if discord_webhook_url:
        from discord_logging.handler import DiscordHandler

        discord_handler = DiscordHandler(
            "StreamApp_ErrorNotifier", discord_webhook_url)
        discord_handler.setLevel(discord_level)
        discord_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(discord_handler)
        app_logger_handlers = [error_file_handler,
                               console_handler, discord_handler]
    else:
        msg = "WebhookURLが読み取れなかったため、Discordへのエラー通知はオフになっています"
        logger.warning(msg)
        print(msg)
        app_logger_handlers = [error_file_handler, console_handler]

    # Flaskアプリが渡された場合のみ、Flaskのロガーにもハンドラを追加
    if app is not None:
        app.logger.handlers.clear()
        for h in app_logger_handlers:
            app.logger.addHandler(h)
        app.logger.setLevel(log_level)
        app.logger.propagate = False

    return logger, app_logger_handlers, audit_logger
