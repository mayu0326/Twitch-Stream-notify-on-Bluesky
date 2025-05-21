# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

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

from eventsub import setup_broadcaster_id
from utils import rotate_secret_if_needed
from flask import jsonify
from eventsub import (
    get_valid_app_access_token,
    create_eventsub_subscription,
    verify_signature,
)
from logging_config import configure_logging
from eventsub import cleanup_eventsub_subscriptions
from tunnel import start_tunnel, stop_tunnel
from bluesky import BlueskyPoster # Ensure BlueskyPoster is imported
from flask import Flask, request
import os
import sys 
from version import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

# Flaskアプリの生成
app = Flask(__name__)


def validate_settings():
    required_keys = [
        "BLUESKY_USERNAME", 
        "BLUESKY_PASSWORD",
        "TWITCH_CLIENT_ID",
        "TWITCH_CLIENT_SECRET",
        "TWITCH_BROADCASTER_ID", 
        "WEBHOOK_CALLBACK_URL"
    ]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        raise ValueError(f"settings.envの必須設定が未設定です: {', '.join(missing_keys)}")
    
    numeric_keys_defaults = {
        "RETRY_MAX": "3",
        "RETRY_WAIT": "2",
        "LOG_RETENTION_DAYS": "14"
    }
    for key, default_value in numeric_keys_defaults.items():
        try:
            value_str = os.getenv(key, default_value)
            int(value_str) 
        except ValueError:
            raise ValueError(f"settings.envの数値設定値 '{key}' (値: {value_str}) が不正です")


@app.errorhandler(404)
def handle_404(e):
    try:
        app.logger.warning(f"404エラー発生: {request.url} (User agent: {request.user_agent.string})")
    except AttributeError: 
        print(f"Warning: 404 error for URL {request.url}")
    return "Not Found", 404


@app.route("/webhook", methods=["POST", "GET"])
def handle_webhook():
    if request.method == "GET":
        app.logger.info("Webhookエンドポイントは正常に稼働しています。")
        return "Webhook endpoint is working! POST requests only.", 200

    if not verify_signature(request): 
        return jsonify({"status": "signature mismatch"}), 403

    try:
        data = request.get_json()
        if data is None: 
            app.logger.warning("Webhook受信: 無効なJSONデータまたは空のボディ")
            return jsonify({"error": "Invalid JSON or empty body"}), 400
    except Exception as e:
        app.logger.error(f"Webhook受信: JSON解析エラー: {e}", exc_info=e)
        return jsonify({"error": "Invalid JSON"}), 400

    message_type = request.headers.get("Twitch-Eventsub-Message-Type")
    subscription_payload = data.get("subscription", {}) if isinstance(data, dict) else {}
    subscription_type = subscription_payload.get("type")

    if message_type == "webhook_callback_verification":
        challenge = data.get("challenge", "") if isinstance(data, dict) else ""
        app.logger.info(f"Webhook検証チャレンジ受信 ({subscription_type if subscription_type else 'タイプ不明'}): {challenge[:50]}...") 
        return challenge, 200, {"Content-Type": "text/plain"}

    if message_type == "notification":
        event_data = data.get("event", {}) if isinstance(data, dict) else {}
        broadcaster_user_login = event_data.get("broadcaster_user_login")
        broadcaster_user_name = event_data.get("broadcaster_user_name", broadcaster_user_login) 

        if not broadcaster_user_login:
            app.logger.warning(f"Webhook通知 ({subscription_type}): 'event.broadcaster_user_login' が不足しています。処理をスキップします。イベントデータ: {event_data}")
            return jsonify({"error": "Missing required field: event.broadcaster_user_login"}), 400

        app.logger.info(f"通知受信 ({subscription_type}) for {broadcaster_user_name or broadcaster_user_login}")

        # Read notification settings
        notify_on_online_str = os.getenv("NOTIFY_ON_ONLINE", "True").lower()
        NOTIFY_ON_ONLINE = notify_on_online_str == "true"

        notify_on_offline_str = os.getenv("NOTIFY_ON_OFFLINE", "False").lower()
        NOTIFY_ON_OFFLINE = notify_on_offline_str == "true"

        if subscription_type == "stream.online":
            if NOTIFY_ON_ONLINE:
                online_specific_fields = ["title", "category_name"]
                missing_online_fields = [f"event.{f}" for f in online_specific_fields if event_data.get(f) is None]
                
                if missing_online_fields:
                    app.logger.warning(f"Webhook通知 (stream.online): 必須フィールドが不足しています: {', '.join(missing_online_fields)}. イベントデータ: {event_data}")
                    return jsonify({"error": f"Missing required field(s) for stream.online: {', '.join(missing_online_fields)}"}), 400
                
                try:
                    bluesky_poster = BlueskyPoster(
                        os.getenv("BLUESKY_USERNAME"),
                        os.getenv("BLUESKY_PASSWORD")
                    )
                    success = bluesky_poster.post_stream_online(
                        event_data["title"],
                        event_data["category_name"],
                        f"https://twitch.tv/{broadcaster_user_login}", 
                        username=broadcaster_user_login,
                        display_name=broadcaster_user_name,
                        image_path=os.getenv("BLUESKY_IMAGE_PATH")
                    )
                    if success:
                        app.logger.info(f"Bluesky投稿成功 (stream.online): {broadcaster_user_login}")
                        return jsonify({"status": "success"}), 200
                    else:
                        app.logger.error(f"Bluesky投稿処理失敗 (stream.online - BlueskyPoster.post_stream_online returned False): {broadcaster_user_login}")
                        return jsonify({"status": "bluesky error processing stream.online"}), 500
                except Exception as e:
                    app.logger.error(f"Bluesky投稿中の未処理例外 (stream.online): {str(e)}", exc_info=e)
                    return jsonify({"error": "Internal server error during stream.online processing"}), 500
            else:
                app.logger.info(f"stream.online通知は設定によりスキップされました: {broadcaster_user_login}")
                return jsonify({"status": "skipped, online notifications disabled"}), 200

        elif subscription_type == "stream.offline":
            if NOTIFY_ON_OFFLINE:
                display_name_for_offline = broadcaster_user_name 
                login_name_for_offline = broadcaster_user_login

                app.logger.info(f"stream.offlineイベント処理開始: {display_name_for_offline} ({login_name_for_offline})")
                try:
                    bluesky_poster = BlueskyPoster(
                        os.getenv("BLUESKY_USERNAME"),
                        os.getenv("BLUESKY_PASSWORD")
                    )
                    success = bluesky_poster.post_stream_offline(
                        broadcaster_display_name=display_name_for_offline,
                        broadcaster_username=login_name_for_offline
                    )
                    app.logger.info(
                        f"Bluesky投稿試行 (stream.offline): {login_name_for_offline}, 成功: {success}")
                    # Return 200 even on Bluesky error to ack notification to Twitch,
                    # but reflect actual success in status.
                    return jsonify(
                        {"status": "success, offline notification posted" if success else "bluesky error, offline notification not posted"}
                    ), 200 
                except Exception as e:
                    app.logger.error(f"Bluesky投稿エラー (stream.offline): {str(e)}", exc_info=True)
                    return jsonify({"error": "Internal server error during stream.offline processing"}), 500
            else:
                app.logger.info(f"stream.offline通知は設定によりスキップされました: {broadcaster_user_login}")
                return jsonify({"status": "skipped, offline notifications disabled"}), 200
        
        else:
            app.logger.warning(f"不明なサブスクリプションタイプ ({subscription_type}) の通知受信: {broadcaster_user_login}")
            return jsonify({"status": "error", "message": f"Unknown or unhandled subscription type: {subscription_type}"}), 400

    if message_type == 'revocation':
        revocation_status = subscription_payload.get("status", "不明なステータス")
        app.logger.warning(f"Twitch EventSubサブスクリプション失効通知受信: タイプ - {subscription_type}, ステータス - {revocation_status}, ユーザー - {data.get('event', {}).get('broadcaster_user_login', 'N/A')}")
        return jsonify({"status": "revocation notification received"}), 200

    app.logger.info(f"受信した未処理のTwitch EventSubメッセージタイプ: {message_type if message_type else '不明'}. データ: {data}")
    return jsonify({"status": "unhandled message type or event"}), 200


logger = None
audit_logger = None

if __name__ == "__main__":
    tunnel_proc = None 
    try:
        logger, app_logger_handlers, audit_logger = configure_logging(app)
        WEBHOOK_SECRET = rotate_secret_if_needed(logger)
        os.environ["WEBHOOK_SECRET"] = WEBHOOK_SECRET

        setup_broadcaster_id(logger=logger) 
        validate_settings()
        logger.info("設定ファイルの検証が完了しました。")
        
        TWITCH_APP_ACCESS_TOKEN = get_valid_app_access_token(logger=logger)
        if not TWITCH_APP_ACCESS_TOKEN:
            logger.critical("Twitchアプリのアクセストークン取得に失敗しました。アプリケーションは起動できません。")
            sys.exit(1)
        logger.info("Twitchアプリのアクセストークンを正常に取得しました。")

        WEBHOOK_CALLBACK_URL = os.getenv("WEBHOOK_CALLBACK_URL")
        cleanup_eventsub_subscriptions(WEBHOOK_CALLBACK_URL, logger=logger)

        tunnel_proc = start_tunnel(logger)
        if not tunnel_proc: 
            logger.critical("トンネルの起動に失敗しました。アプリケーションは起動できません。")
            sys.exit(1)
        
        event_types_to_subscribe = ["stream.online", "stream.offline"]
        all_subscriptions_successful = True
        for event_type in event_types_to_subscribe:
            logger.info(f"{event_type} のEventSubサブスクリプションを作成します...")
            sub_response = create_eventsub_subscription(event_type, logger_to_use=logger)
            
            if not sub_response or not isinstance(sub_response, dict) or \
               not sub_response.get("data") or not isinstance(sub_response["data"], list) or not sub_response["data"]:
                twitch_error_status = sub_response.get("status") if isinstance(sub_response, dict) else None
                twitch_error_message = sub_response.get("message") if isinstance(sub_response, dict) else None
                log_message = f"{event_type} EventSubサブスクリプションの作成に失敗しました。"
                if twitch_error_status:
                    log_message += f" ステータス: {twitch_error_status}."
                if twitch_error_message:
                    log_message += f" メッセージ: {twitch_error_message}."
                logger.critical(log_message + f" 詳細: {sub_response}")
                all_subscriptions_successful = False
                break 
            
            if sub_response.get("status") == "already exists":
                 logger.info(f"{event_type} EventSubサブスクリプションは既に存在します。ID: {sub_response.get('id')}")
            else:
                subscription_details = sub_response['data'][0]
                logger.info(f"{event_type} EventSubサブスクリプション作成成功。ID: {subscription_details.get('id')}, ステータス: {subscription_details.get('status')}")

        if not all_subscriptions_successful:
            logger.critical("必須EventSubサブスクリプションの作成に失敗したため、アプリケーションは起動できません。")
            sys.exit(1)

        logger.info("Flask (waitress) サーバーを起動します。ポート: 3000")
        from waitress import serve
        serve(app, host="0.0.0.0", port=3000)

    except ValueError as ve: 
        log_msg = f"設定エラー: {ve}. アプリケーションは起動できません。"
        if logger: logger.critical(log_msg)
        else: print(f"CRITICAL: {log_msg}")
        sys.exit(1)
    except Exception as e:
        log_msg_critical = "初期化中の未処理例外によりアプリケーションの起動に失敗しました。"
        if logger: logger.critical(log_msg_critical, exc_info=e)
        else: print(f"CRITICAL: {log_msg_critical} {e}")
        sys.exit(1)
    finally:
        if tunnel_proc: 
             if logger: logger.info("アプリケーション終了前にトンネルを停止します。")
             else: print("アプリケーション終了前にトンネルを停止します。")
             stop_tunnel(tunnel_proc, logger)


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error("リクエスト処理中に未処理例外発生", exc_info=e)
    return (
        jsonify(
            {
                "error": "予期せぬサーバーエラーが発生しました。"
            }
        ),
        500,
    )
