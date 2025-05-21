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
from bluesky import BlueskyPoster
from flask import Flask, request
import os
import sys # Added for sys.exit
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
        "TWITCH_BROADCASTER_ID", # Added from setup_broadcaster_id logic
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
            int(value_str) # Try converting to int
        except ValueError:
            raise ValueError(f"settings.envの数値設定値 '{key}' (値: {value_str}) が不正です")


@app.errorhandler(404)
def handle_404(e):
    # Ensure logger is available or use print
    try:
        app.logger.warning(f"404エラー発生: {request.url} (User agent: {request.user_agent.string})")
    except AttributeError: # app.logger might not be configured if error occurs very early
        print(f"Warning: 404 error for URL {request.url}")
    return "Not Found", 404


@app.route("/webhook", methods=["POST", "GET"])
def handle_webhook():
    if request.method == "GET":
        app.logger.info("Webhookエンドポイントは正常に稼働しています。")
        return "Webhook endpoint is working! POST requests only.", 200

    # 1. 署名検証（最優先）
    if not verify_signature(request): # verify_signature should handle logging internally
        return jsonify({"status": "signature mismatch"}), 403

    # 2. JSONデータ取得（例外処理付き）
    try:
        data = request.get_json()
        if data is None: # Handle cases where get_json returns None for non-JSON or empty body
            app.logger.warning("Webhook受信: 無効なJSONデータまたは空のボディ")
            return jsonify({"error": "Invalid JSON or empty body"}), 400
    except Exception as e:
        app.logger.error(f"Webhook受信: JSON解析エラー: {e}", exc_info=e)
        return jsonify({"error": "Invalid JSON"}), 400

    # 3. メッセージタイプ取得
    message_type = request.headers.get("Twitch-Eventsub-Message-Type")

    # 4. 検証用チャレンジ処理
    if message_type == "webhook_callback_verification":
        challenge = data.get("challenge", "")
        app.logger.info(f"Webhook検証チャレンジ受信: {challenge[:50]}...") # Log part of challenge
        return challenge, 200, {"Content-Type": "text/plain"}

    # 5. 通知処理
    if message_type == "notification":
        # 必須フィールドチェック（ネスト構造対応）
        required_fields = [
            "subscription.type",
            "event.title",
            "event.category_name",
            "event.broadcaster_user_login"
        ]

        # ネスト構造チェック（再帰的検証）
        missing_data_fields = []
        for field in required_fields:
            keys = field.split('.')
            value = data
            valid_path = True
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value.get(key)
                else:
                    missing_data_fields.append(field)
                    valid_path = False
                    break
            if not valid_path: # No need to check further if path is broken
                continue
        
        if missing_data_fields:
            app.logger.warning(f"Webhook通知: 必須フィールドが不足しています: {', '.join(missing_data_fields)}. 受信データ: {data}")
            return jsonify(
                {"error": f"Missing required field(s): {', '.join(missing_data_fields)}"}
            ), 400

        # Bluesky投稿処理（例外処理追加）
        try:
            bluesky_poster = BlueskyPoster(
                os.getenv("BLUESKY_USERNAME"),
                os.getenv("BLUESKY_PASSWORD")
            )
            success = bluesky_poster.post_stream_online(
                data["event"]["title"],
                data["event"]["category_name"],
                f"https://twitch.tv/{data['event']['broadcaster_user_login']}",
                username=data['event'].get('broadcaster_user_name'), # Pass username if available
                display_name=data['event'].get('broadcaster_user_name'), # Pass display_name if available
                image_path=os.getenv("BLUESKY_IMAGE_PATH")
            )
            if success:
                app.logger.info(
                    f"Bluesky投稿成功: {data['event']['broadcaster_user_login']}")
                return jsonify({"status": "success"}), 200
            else:
                app.logger.error(f"Bluesky投稿処理失敗 (BlueskyPoster.post_stream_online returned False): {data['event']['broadcaster_user_login']}")
                return jsonify({"status": "bluesky error"}), 500 # Or another appropriate error code
        except Exception as e:
            app.logger.error(f"Bluesky投稿中の未処理例外: {str(e)}", exc_info=e)
            return jsonify({"error": "Internal server error during Bluesky post"}), 500

    # 6. 未知のメッセージタイプ or リボークなどその他
    app.logger.info(f"受信したTwitch EventSubメッセージタイプ: {message_type if message_type else '不明'}. データ: {data}")
    # For 'revocation' or other types, just acknowledge receipt.
    if message_type == 'revocation':
        app.logger.warning(f"Twitch EventSubサブスクリプション失効通知受信: サブスクリプションタイプ - {data.get('subscription', {}).get('type')}, ステータス - {data.get('subscription', {}).get('status')}")
        return jsonify({"status": "revocation notification received"}), 200

    return jsonify({"status": "unhandled message type or event"}), 200 # Return 200 for unhandled but valid Twitch messages to prevent retries


# This should be defined before it's used in the if __name__ == "__main__": block
logger = None
audit_logger = None

if __name__ == "__main__":
    try:
        logger, app_logger_handlers, audit_logger = configure_logging(app)
        WEBHOOK_SECRET = rotate_secret_if_needed(logger)
        os.environ["WEBHOOK_SECRET"] = WEBHOOK_SECRET

        # ブロードキャスターID設定 (TWITCH_BROADCASTER_IDがここで設定される)
        setup_broadcaster_id(logger=logger) 

        # 設定検証 (setup_broadcaster_id の後で、TWITCH_BROADCASTER_ID が設定されるため)
        validate_settings()
        logger.info("設定ファイルの検証が完了しました。")

        # 既存サブスクリプション削除
        WEBHOOK_CALLBACK_URL = os.getenv("WEBHOOK_CALLBACK_URL")
        # cleanup_eventsub_subscriptions needs token, so get it first.
        
        tunnel_proc = None # Initialize tunnel_proc
        TWITCH_APP_ACCESS_TOKEN = get_valid_app_access_token(logger=logger)
        if not TWITCH_APP_ACCESS_TOKEN:
            logger.critical("Twitchアプリのアクセストークン取得に失敗しました。アプリケーションは起動できません。")
            # tunnel_proc is not started yet, so no need to stop it here.
            sys.exit(1)
        logger.info("Twitchアプリのアクセストークンを正常に取得しました。")

        cleanup_eventsub_subscriptions(WEBHOOK_CALLBACK_URL, logger=logger) # Now with token and logger

        # トンネル起動とメイン処理
        tunnel_proc = start_tunnel(logger) # tunnel_proc is now defined
        
        # EventSubサブスクリプション作成
        sub_response = create_eventsub_subscription(logger=logger) # Pass logger
        # logger.info(f"サブスクリプション作成試行結果: {sub_response}") # Log raw response for debugging

        # Check for successful subscription
        # A successful response usually has a 'data' list with the subscription details.
        # An error response might have a 'status' field indicating an error code, or 'message'.
        if not sub_response or not isinstance(sub_response, dict) or \
           not sub_response.get("data") or not isinstance(sub_response["data"], list) or not sub_response["data"]:
            # If 'data' is missing, empty, or not a list, or if the response itself is bad
            # Also check if Twitch returned an error status explicitly
            twitch_error_status = sub_response.get("status") if isinstance(sub_response, dict) else None
            twitch_error_message = sub_response.get("message") if isinstance(sub_response, dict) else None

            log_message = f"EventSubサブスクリプション作成に失敗しました。"
            if twitch_error_status:
                log_message += f" ステータス: {twitch_error_status}."
            if twitch_error_message:
                log_message += f" メッセージ: {twitch_error_message}."
            # Log the full response for more details if it's not too large or sensitive
            # For now, just logging the status and message should be enough for critical log
            logger.critical(log_message + " アプリケーションは起動できません。")
            
            if tunnel_proc: # Check if tunnel_proc was defined and is not None
                stop_tunnel(tunnel_proc, logger)
            sys.exit(1)

        logger.info(f"EventSubサブスクリプション作成成功: {sub_response['data'][0].get('type')}, ID: {sub_response['data'][0].get('id')}")


        logger.info("Flask (waitress) サーバーを起動します。ポート: 3000")
        from waitress import serve
        serve(app, host="0.0.0.0", port=3000)

    except ValueError as ve: # Catch validation errors specifically
        # Logger might not be fully configured if error is in logging_config itself or early settings.
        log_msg = f"設定エラー: {ve}. アプリケーションは起動できません。"
        try:
            if logger:
                logger.critical(log_msg)
            else:
                print(f"CRITICAL: {log_msg}")
        except NameError:
             print(f"CRITICAL: {log_msg}")
        if 'tunnel_proc' in locals() and tunnel_proc:
            stop_tunnel(tunnel_proc, logger if 'logger' in locals() and logger else None)
        sys.exit(1)
    except Exception as e:
        # Use logger if available, otherwise print
        log_msg_critical = "初期化中の未処理例外によりアプリケーションの起動に失敗しました。"
        try:
            if logger:
                logger.critical(log_msg_critical, exc_info=e)
            else:
                print(f"CRITICAL: {log_msg_critical} {e}")
        except NameError: # logger might not be defined if configure_logging failed
            print(f"CRITICAL: {log_msg_critical} {e}")
        if 'tunnel_proc' in locals() and tunnel_proc: # Check if tunnel_proc was defined
            stop_tunnel(tunnel_proc, logger if 'logger' in locals() and logger else None)
        sys.exit(1) # Exit with a non-zero code to indicate failure
    finally:
        # Ensure tunnel is stopped if it was started and the application is exiting for any reason
        # other than a sys.exit() call that already handled it.
        # This block might be redundant if sys.exit() is called in all error paths that start the tunnel.
        if 'tunnel_proc' in locals() and tunnel_proc and 'serve' not in locals(): # if server didn't start
             if logger:
                logger.info("アプリケーション終了前にトンネルを停止します。")
             else:
                print("アプリケーション終了前にトンネルを停止します。")
             stop_tunnel(tunnel_proc, logger if 'logger' in locals() and logger else None)


@app.errorhandler(Exception)
def handle_exception(e):
    # This handler is for exceptions during request processing by Flask, not startup.
    app.logger.error("リクエスト処理中に未処理例外発生", exc_info=e)
    return (
        jsonify(
            {
                "error": "予期せぬサーバーエラーが発生しました。" # Generic message to user
            }
        ),
        500,
    )
