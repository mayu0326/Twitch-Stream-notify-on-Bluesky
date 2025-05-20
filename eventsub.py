# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from tzlocal import get_localzone
import pytz
from pathlib import Path
from dotenv import load_dotenv
from utils import retry_on_exception
import datetime
import logging
import time
import hashlib
import hmac
import requests
import os
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


# 環境設定ファイルの場所
env_path = Path(__file__).parent / "settings.env"
load_dotenv(dotenv_path=env_path)

# ログの設定
logger = logging.getLogger("AppLogger")
audit_logger = logging.getLogger("AuditLogger")

# タイムゾーンの設定
TIMEZONE_NAME = os.getenv("TIMEZONE", "system")
if TIMEZONE_NAME == "system":
    TIMEZONE = get_localzone()  # システムのタイムゾーンを自動取得
else:
    try:
        TIMEZONE = pytz.timezone(TIMEZONE_NAME)
    except pytz.UnknownTimeZoneError:
        logger.warning(f"無効なタイムゾーン: {TIMEZONE_NAME}。システムタイムゾーンを使用します")
        TIMEZONE = get_localzone()

# タイムゾーン付き現在時刻取得関数


def get_current_time():
    return datetime.datetime.now(TIMEZONE)


# 環境変数
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_BROADCASTER_ID = os.getenv("TWITCH_BROADCASTER_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
RETRY_MAX = int(os.getenv("RETRY_MAX", 3))
RETRY_WAIT = int(os.getenv("RETRY_WAIT", 2))

TWITCH_APP_ACCESS_TOKEN = None
TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT = 0


@retry_on_exception(
    max_retries=RETRY_MAX,
    wait_seconds=RETRY_WAIT,
    exceptions=(requests.RequestException,)
)
# アクセストークンの管理
def get_app_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        expires_in = data["expires_in"]
        expires_at = time.time() + expires_in - 60  # 1分前に失効扱い
        return token, expires_at
    else:
        logger.error(f"Twitchアクセストークン取得失敗: {response.text}")
        return None, 0

# アクセストークンの検証


def get_valid_app_access_token():
    global TWITCH_APP_ACCESS_TOKEN, TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT
    if not TWITCH_APP_ACCESS_TOKEN or time.time(
    ) > TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT:
        TWITCH_APP_ACCESS_TOKEN, TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT = (
            get_app_access_token()
        )
    return TWITCH_APP_ACCESS_TOKEN

# Twitchのユーザー名からBROADCASTER_IDを取得


def get_broadcaster_id(username):
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token()}",
    }
    params = {"login": username}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data")
        if not isinstance(data, list) or not data:
            logger.error("Twitch APIレスポンスにユーザーデータがありません")
            raise ValueError("Twitch APIレスポンスにユーザーデータがありません")
        return data[0]["id"]
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        logger.error(f"ユーザーID取得エラー: {str(e)}")
        raise


# ユーザー名が入力されていた場合に数値IDに変換
def setup_broadcaster_id():
    global TWITCH_BROADCASTER_ID
    if TWITCH_BROADCASTER_ID is None or not TWITCH_BROADCASTER_ID.isdigit():
        try:
            TWITCH_BROADCASTER_ID = get_broadcaster_id(TWITCH_BROADCASTER_ID)
            logger.info(f"ユーザーID変換完了: {TWITCH_BROADCASTER_ID}")
        except Exception as e:
            logger.critical(f"ユーザーID変換に失敗しました: {e}", exc_info=True)
            raise

# Signatureの検証


def verify_signature(request):
    required_headers = [
        "Twitch-Eventsub-Message-Id",
        "Twitch-Eventsub-Message-Timestamp",
        "Twitch-Eventsub-Message-Signature"
    ]
    for h in required_headers:
        if h not in request.headers:
            logger.warning(f"Webhookリクエストにヘッダー {h} がありません")
            return False

    signature = request.headers.get("Twitch-Eventsub-Message-Signature", "")
    message_id = request.headers["Twitch-Eventsub-Message-Id"]
    timestamp = request.headers["Twitch-Eventsub-Message-Timestamp"]
    body = request.get_data().decode("utf-8")

    # タイムスタンプのパース（ナノ秒対応）
    def parse_timestamp(ts: str):
        if '.' in ts and ts.endswith('Z'):
            ts = ts[:-1]  # 'Z'を除去
            main_part, fractional = ts.split('.')
            fractional = fractional[:6]  # マイクロ秒（6桁）に切り捨て
            return datetime.datetime.fromisoformat(
                f"{main_part}.{fractional}+00:00").astimezone(TIMEZONE)
        return datetime.datetime.fromisoformat(
            ts.replace('Z', '+00:00')).astimezone(TIMEZONE)

    # 現在時刻をJSTで取得
    now = datetime.datetime.now(TIMEZONE)

    try:
        event_time = parse_timestamp(timestamp).astimezone(TIMEZONE)
    except Exception as e:
        logger.warning(f"タイムスタンプ解析エラー: {str(e)}")
        return False

    # 時間差チェック（5分以内か）
    delta = abs((now - event_time).total_seconds())
    if delta > 300:  # 5分（300秒）を超えていれば拒否
        logger.warning(f"タイムスタンプが許容範囲外: {timestamp} (差分: {delta}秒)")
        return False

    hmac_message = message_id + timestamp + body

    if not WEBHOOK_SECRET:
        logger.critical("WEBHOOK_SECRETが設定されていません。settings.envを確認してください。")
        raise ValueError(
            "WEBHOOK_SECRET is None or empty. Please set it in settings.env")

    digest = hmac.new(
        WEBHOOK_SECRET.encode(), hmac_message.encode(), hashlib.sha256
    ).hexdigest()
    expected_signature = f"sha256={digest}"

    return hmac.compare_digest(signature, expected_signature)


def get_existing_eventsub_subscriptions():
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token()}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        logger.error(f"既存サブスクリプション取得エラー: {response.text}")
        return []


# サブスクリプションの追加
def create_eventsub_subscription():
    # 既存サブスクリプション一覧を取得
    existing = get_existing_eventsub_subscriptions()
    for sub in existing:
        if (
            sub.get("type") == "stream.online"
            and sub.get("condition", {}).get("broadcaster_user_id")
            == TWITCH_BROADCASTER_ID
            and sub.get("status") == "enabled"
        ):
            logger.info(
                "既に同じサブスクリプションが存在するため新規作成をスキップします"
            )
            audit_logger.info(
                "EventSubサブスクリプション作成: stream.online (既に存在) 成功")
            return {"status": "already exists", "id": sub.get("id")}

    # なければ新規作成
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token()}",
        "Content-Type": "application/json",
    }
    payload = {
        "type": "stream.online",
        "version": "1",
        "condition": {"broadcaster_user_id": TWITCH_BROADCASTER_ID},
        "transport": {
            "method": "webhook",
            "callback": os.getenv("WEBHOOK_CALLBACK_URL"),
            "secret": WEBHOOK_SECRET,
        },
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        audit_logger.info("EventSubサブスクリプション作成: stream.online 成功")
        return result
    except requests.exceptions.HTTPError as e:
        reason = f"{e} | {getattr(e.response, 'text', '')}"
        audit_logger.warning(
            f"EventSubサブスクリプション作成: stream.online 失敗: {reason}")
        logger.error(f"EventSubサブスクリプション作成失敗: {reason}")
        return {"status": "error", "reason": reason}
    except Exception as e:
        reason = str(e)
        audit_logger.warning(
            f"EventSubサブスクリプション作成: stream.online 失敗: {reason}")
        logger.error(f"EventSubサブスクリプション作成失敗: {reason}")
        return {"status": "error", "reason": reason}

# サブスクリプションの削除


def delete_eventsub_subscription(subscription_id):
    url = f"https://api.twitch.tv/helix/eventsub/subscriptions?id={
        subscription_id}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token()}"
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        logger.info(f"EventSubサブスクリプション削除: {subscription_id} 成功")
        audit_logger.info(f"EventSubサブスクリプション削除: {subscription_id}")
    else:
        logger.warning(
            f"EventSubサブスクリプション削除: {subscription_id} 失敗: {response.text}")
        audit_logger.warning(
            f"EventSubサブスクリプション削除: {subscription_id} 失敗: {response.text}")

# サブスクリプションの確認と削除の処理


def cleanup_eventsub_subscriptions(webhook_callback_url):
    subs = get_existing_eventsub_subscriptions()
    for sub in subs:
        # 自分のWebhook URLと異なるもの、またはstatusが"enabled"でないものを削除
        if sub.get(
            "transport", {}
        ).get("callback") != webhook_callback_url or sub.get(
                "status") != "enabled":
            delete_eventsub_subscription(sub["id"])
