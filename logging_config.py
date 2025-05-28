# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from version_info import __version__
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

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


def configure_logging(app=None):
    # 環境設定ファイルの場所を指定し、環境変数を読み込む
    env_path = Path(__file__).parent / "settings.env"
    load_dotenv(dotenv_path=env_path)

    # logsディレクトリがなければ作成
    os.makedirs("logs", exist_ok=True)

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

    # Discord通知のログレベル設定
    DISCORD_NOTIFY_LEVEL = os.getenv(
        "discord_notify_level", "CRITICAL").upper()
    discord_level = LEVEL_MAP.get(DISCORD_NOTIFY_LEVEL, logging.CRITICAL)

    # ログの保管日数を取得（デフォルト14日、異常値は14日にフォールバック）
    try:
        log_retention_days_str = os.getenv("LOG_RETENTION_DAYS", "14")
        log_retention_days = int(log_retention_days_str)
        if log_retention_days <= 0:
            print(
                f"Warning: LOG_RETENTION_DAYS value '{log_retention_days_str}' is not positive. Defaulting to 14 days.")
            log_retention_days = 14
    except ValueError:
        print(
            f"Warning: Invalid LOG_RETENTION_DAYS value '{
                os.getenv('LOG_RETENTION_DAYS')}'. Defaulting to 14 days.")
        log_retention_days = 14

    # 監査ログ専用ロガーとハンドラの設定
    audit_logger = logging.getLogger("AuditLogger")
    # 監査ログはINFOレベル以上のみ記録
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

    # アプリケーション用ロガーの作成
    logger = logging.getLogger("AppLogger")
    logger.setLevel(log_level)
    logger.propagate = False  # ルートロガーへの伝播を防止

    # エラーログとコンソールハンドラの設定
    error_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # 一般ログファイル（app.log）のハンドラ
    info_file_handler = TimedRotatingFileHandler(
        "logs/app.log",  # アプリケーション全体のログ
        when="D",
        interval=1,
        backupCount=log_retention_days,
        encoding="utf-8",
    )
    info_file_handler.setLevel(log_level)  # 設定されたログレベルを使用
    info_file_handler.setFormatter(error_format)
    logger.addHandler(info_file_handler)

    # エラーログファイル（error.log）のハンドラ
    error_file_handler = TimedRotatingFileHandler(
        "logs/error.log",  # エラー専用ログファイル
        when="D",
        interval=1,
        backupCount=log_retention_days,
        encoding="utf-8",
    )
    error_file_handler.setLevel(logging.ERROR)  # ERROR以上のみ記録
    error_file_handler.setFormatter(error_format)
    logger.addHandler(error_file_handler)  # AppLoggerに追加

    # コンソール出力用ハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)  # 設定されたログレベルを使用
    console_handler.setFormatter(error_format)
    logger.addHandler(console_handler)

    # Discord通知の有効/無効設定
    discord_enabled = os.getenv("DISCORD_NOTIFICATION_ENABLED", "false").lower() == "true"

    # Discord通知用Webhookの設定
    discord_webhook_url = os.getenv("discord_error_notifier_url")
    app_logger_handlers = [info_file_handler,
                           error_file_handler, console_handler]  # Flask用にも使うハンドラリスト

    if discord_enabled and discord_webhook_url and discord_webhook_url.startswith(
            "https://discord.com/api/webhooks/"):
        try:
            from discord_logging.handler import DiscordHandler
            discord_handler = DiscordHandler(
                "StreamApp_ErrorNotifier", discord_webhook_url)
            # 設定されたDiscord通知レベルを使用
            discord_handler.setLevel(discord_level)
            discord_handler.setFormatter(
                # ログフォーマットを統一
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
            logger.addHandler(discord_handler)
            app_logger_handlers.append(
                discord_handler)  # Flask用リストにも追加
        except ImportError:
            msg = "discord_loggingライブラリが見つかりません。Discord通知は無効化されます。'pip install discord-logging-handler'でインストールしてください。"
            logger.warning(msg)
            print(msg)  # ロガーが未初期化の場合も考慮してprint
        except Exception as e:
            msg = f"DiscordHandlerの初期化に失敗しました: {e}。Discord通知は無効化されます。"
            logger.warning(msg)
            print(msg)
    else:
        # ユーザー指定の日本語メッセージで出力
        if not discord_webhook_url or not discord_webhook_url.startswith(
                "https://discord.com/api/webhooks/"):
            msg = "Discord通知はオフになっています。"
        elif not discord_enabled:
            msg = "Discord通知はオフになっています。"
        else:
            msg = "Discord通知はオンになっています。"
        logger.info(msg)  # 設定上の選択なのでINFOで記録

    # tunnel.log用ロガーの設定
    tunnel_logger = logging.getLogger("tunnel.logger")
    tunnel_logger.setLevel(log_level)
    tunnel_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    tunnel_file_handler = TimedRotatingFileHandler(
        "logs/tunnel.log",
        when="D",
        interval=1,
        backupCount=log_retention_days,
        encoding="utf-8",
    )
    tunnel_file_handler.setLevel(log_level)
    tunnel_file_handler.setFormatter(tunnel_format)
    tunnel_logger.addHandler(tunnel_file_handler)

    # Flaskアプリが渡された場合は、Flaskのロガーにも同じハンドラを追加
    if app is not None:
        app.logger.handlers.clear()  # Flaskデフォルトハンドラをクリア
        for h in app_logger_handlers:
            app.logger.addHandler(h)
        app.logger.setLevel(log_level)
        app.logger.propagate = False

    return logger, app_logger_handlers, audit_logger, tunnel_logger
