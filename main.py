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
from version import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

# Flaskアプリの生成
app = Flask(__name__)


def validate_settings():
    required_keys = ["BLUESKY_USERNAME", "BLUESKY_PASSWORD"]
    for key in required_keys:
        if not os.getenv(key):
            raise ValueError(f"settings.envの{key}が未設定です")
    try:
        int(os.getenv("RETRY_MAX", 3))
        int(os.getenv("RETRY_WAIT", 2))
        int(os.getenv("LOG_RETENTION_DAYS", 14))
    except ValueError:
        raise ValueError("settings.envの数値設定値が不正です")


@app.errorhandler(404)
def handle_404(e):
    return "Not Found", 404


@app.route("/webhook", methods=["POST", "GET"])
def handle_webhook():
    if request.method == "GET":
        app.logger.info("Webhookエンドポイントは正常に稼働しています。")
        return "Webhook endpoint is working! POST requests only.", 200

    # 1. 署名検証（最優先）
    if not verify_signature(request):
        return jsonify({"status": "signature mismatch"}), 403

    # 2. JSONデータ取得（例外処理付き）
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    # 3. メッセージタイプ取得
    message_type = request.headers.get("Twitch-Eventsub-Message-Type")

    # 4. 検証用チャレンジ処理
    if message_type == "webhook_callback_verification":
        challenge = data.get("challenge", "")
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
        for field in required_fields:
            keys = field.split('.')
            value = data
            for key in keys:
                value = value.get(key)
                if value is None:
                    return jsonify(
                        {"error": f"Missing required field: {field}"}
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
                image_path=os.getenv("BLUESKY_IMAGE_PATH")
            )
            app.logger.info(
                f"Bluesky投稿成功: {data['event']['broadcaster_user_login']}")
            return jsonify(
                {"status": "success" if success else "bluesky error"}
            ), 200 if success else 500
        except Exception as e:
            app.logger.error(f"Bluesky投稿エラー: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    # 6. 未知のメッセージタイプ
    return jsonify({"status": "unknown message type"}), 400


if __name__ == "__main__":
    logger, app_logger_handlers, audit_logger = configure_logging(app)
    WEBHOOK_SECRET = rotate_secret_if_needed(logger)
    os.environ["WEBHOOK_SECRET"] = WEBHOOK_SECRET


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error("未処理例外発生", exc_info=e)
    # ユーザーには詳細を返さず、一般的なメッセージのみ
    return (
        jsonify(
            {
                "error": "予期せぬエラーが発生しました。しばらくしてから再度お試しください。"
            }
        ),
        500,
    )


# 環境変数を読み込む
BLUESKY_USERNAME = os.getenv("BLUESKY_USERNAME")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")
BLUESKY_IMAGE_PATH = os.getenv("BLUESKY_IMAGE_PATH")

# ブロードキャスターID設定
setup_broadcaster_id()

# 設定検証
validate_settings()

# 既存サブスクリプション削除
WEBHOOK_CALLBACK_URL = os.getenv("WEBHOOK_CALLBACK_URL")
cleanup_eventsub_subscriptions(WEBHOOK_CALLBACK_URL)

# トンネル起動とメイン処理
try:
    tunnel_proc = start_tunnel(logger)
    try:
        TWITCH_APP_ACCESS_TOKEN = get_valid_app_access_token()
        if TWITCH_APP_ACCESS_TOKEN:
            sub_response = create_eventsub_subscription()
            app.logger.info(f"サブスクリプション作成: {sub_response}")

        from waitress import serve
        serve(app, host="0.0.0.0", port=3000)
    finally:
        stop_tunnel(tunnel_proc, logger)
except Exception:
    pass
