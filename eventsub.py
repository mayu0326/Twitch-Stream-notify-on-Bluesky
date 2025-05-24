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
if TIMEZONE_NAME.lower() == "system":  # Make comparison case-insensitive
    try:
        TIMEZONE = get_localzone()  # システムのタイムゾーンを自動取得
    except Exception as e:
        logger.warning(f"システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
        TIMEZONE = pytz.utc
elif TIMEZONE_NAME:  # Ensure TIMEZONE_NAME is not empty
    try:
        TIMEZONE = pytz.timezone(TIMEZONE_NAME)
    except pytz.UnknownTimeZoneError:
        logger.warning(f"無効なタイムゾーン: {TIMEZONE_NAME}。システムタイムゾーンにフォールバックします。")
        try:
            TIMEZONE = get_localzone()
        except Exception as e:
            logger.warning(f"システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
            TIMEZONE = pytz.utc
    except Exception as e:  # Catch other potential errors from pytz.timezone
        logger.warning(
            f"タイムゾーン '{TIMEZONE_NAME}' の処理中にエラーが発生しました ({e})。UTCにフォールバックします。")
        TIMEZONE = pytz.utc
else:  # If TIMEZONE_NAME is empty or None after os.getenv
    logger.warning("TIMEZONE環境変数が空です。システムタイムゾーンにフォールバックします。")
    try:
        TIMEZONE = get_localzone()
    except Exception as e:
        logger.warning(f"システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
        TIMEZONE = pytz.utc

# タイムゾーン付き現在時刻取得関数


def get_current_time():  # Not currently used, but good to have if needed elsewhere
    return datetime.datetime.now(TIMEZONE)


# 環境変数
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
# This might be updated by setup_broadcaster_id
TWITCH_BROADCASTER_ID = os.getenv("TWITCH_BROADCASTER_ID")
# This is updated by rotate_secret_if_needed in main.py
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
def get_app_access_token(logger_to_use=None):  # Allow passing logger
    current_logger = logger_to_use if logger_to_use else logger
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, params=params, timeout=20)  # timeout追加
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        expires_in = data["expires_in"]
        expires_at = time.time() + expires_in - 60  # 1分前に失効扱い
        current_logger.info("Twitchアプリのアクセストークンを正常に取得または更新しました。")
        return token, expires_at
    else:
        current_logger.error(
            f"Twitchアクセストークン取得失敗: {response.status_code} - {response.text}")
        return None, 0

# アクセストークンの検証


def get_valid_app_access_token(logger_to_use=None):  # Allow passing logger
    global TWITCH_APP_ACCESS_TOKEN, TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT
    current_logger = logger_to_use if logger_to_use else logger
    if not TWITCH_APP_ACCESS_TOKEN or time.time() > TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT:
        current_logger.info("Twitchアプリのアクセストークンが無効または期限切れです。新しいトークンを取得します。")
        TWITCH_APP_ACCESS_TOKEN, TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT = (
            get_app_access_token(logger_to_use=current_logger)
        )
    return TWITCH_APP_ACCESS_TOKEN

# Twitchのユーザー名からBROADCASTER_IDを取得


def get_broadcaster_id(username, logger_to_use=None):  # Allow passing logger
    current_logger = logger_to_use if logger_to_use else logger
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token(logger_to_use=current_logger)}",
    }
    params = {"login": username}
    try:
        response = requests.get(url, headers=headers,
                                params=params, timeout=20)  # timeout追加
        response.raise_for_status()
        data = response.json().get("data")
        if not isinstance(data, list) or not data:
            current_logger.error(
                f"Twitch APIレスポンスにユーザーデータがありません (ユーザー名: {username})")
            raise ValueError(
                f"Twitch APIレスポンスにユーザーデータがありません (ユーザー名: {username})")
        return data[0]["id"]
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        current_logger.error(f"ユーザーID取得エラー (ユーザー名: {username}): {str(e)}")
        raise


# ユーザー名が入力されていた場合に数値IDに変換
def setup_broadcaster_id(logger_to_use=None):  # Allow passing logger
    global TWITCH_BROADCASTER_ID
    current_logger = logger_to_use if logger_to_use else logger
    # TWITCH_BROADCASTER_ID is loaded from os.getenv at the module level
    # This function updates the global variable if it's not a digit.
    if TWITCH_BROADCASTER_ID is None or not TWITCH_BROADCASTER_ID.strip():  # Check if None or empty
        current_logger.critical(
            "TWITCH_BROADCASTER_IDが設定されていません。アプリケーションは起動できません。")
        raise ValueError("TWITCH_BROADCASTER_ID is not set.")

    if not TWITCH_BROADCASTER_ID.isdigit():
        original_username = TWITCH_BROADCASTER_ID
        current_logger.info(
            f"TWITCH_BROADCASTER_ID '{original_username}' は数値ではありません。ユーザーIDの取得を試みます。")
        try:
            TWITCH_BROADCASTER_ID = get_broadcaster_id(
                original_username, logger_to_use=current_logger)
            current_logger.info(
                f"ユーザーID変換完了: {original_username} -> {TWITCH_BROADCASTER_ID}")
        except Exception as e:
            current_logger.critical(
                f"ユーザー名 '{original_username}' からユーザーIDへの変換に失敗しました: {e}", exc_info=True)
            raise
    else:
        current_logger.info(
            f"TWITCH_BROADCASTER_ID は既に数値形式です: {TWITCH_BROADCASTER_ID}")
    # Update os.environ as well so other parts of the app see the numeric ID if it was converted
    os.environ['TWITCH_BROADCASTER_ID'] = TWITCH_BROADCASTER_ID


# Signatureの検証
# Assuming logger is available via app.logger in Flask context
def verify_signature(request):
    # Use request.app.logger if available, otherwise global logger
    current_logger = request.logger if hasattr(request, 'logger') else logger

    required_headers = [
        "Twitch-Eventsub-Message-Id",
        "Twitch-Eventsub-Message-Timestamp",
        "Twitch-Eventsub-Message-Signature"
    ]
    for h in required_headers:
        if h not in request.headers:
            current_logger.warning(f"Webhookリクエストにヘッダー {h} がありません")
            return False

    signature = request.headers.get("Twitch-Eventsub-Message-Signature", "")
    message_id = request.headers["Twitch-Eventsub-Message-Id"]
    timestamp_str = request.headers["Twitch-Eventsub-Message-Timestamp"]
    body = request.get_data(as_text=True)  # Get body as string

    # タイムスタンプのパース（ナノ秒対応）
    def parse_timestamp(ts: str):  # Inner function, uses TIMEZONE from outer scope
        dt_obj = None
        # Try ISO 8601 format with 'Z'
        if '.' in ts and ts.endswith('Z'):
            # Handle nanoseconds by truncating to microseconds
            main_part, fractional = ts[:-1].split('.', 1)
            fractional = fractional[:6]  # Keep up to 6 digits for microseconds
            dt_obj = datetime.datetime.fromisoformat(
                f"{main_part}.{fractional}+00:00")
        # Try ISO 8601 format without 'Z' but with timezone offset
        elif '+' in ts[10:] or '-' in ts[10:]:  # Check for explicit timezone offset
            dt_obj = datetime.datetime.fromisoformat(ts)
        else:  # If no 'Z' and no explicit offset, assume UTC if it's a common format without them
            # This case might be ambiguous, Twitch usually provides 'Z' or offset.
            # Fallback or raise error if format is unexpected.
            # For now, attempt fromisoformat, it might raise ValueError if not compliant.
            dt_obj = datetime.datetime.fromisoformat(ts)

        return dt_obj.astimezone(TIMEZONE)  # Convert to configured TIMEZONE

    now = datetime.datetime.now(TIMEZONE)

    try:
        event_time = parse_timestamp(timestamp_str)
    except Exception as e:
        current_logger.warning(f"タイムスタンプ '{timestamp_str}' の解析エラー: {str(e)}")
        return False

    # 時間差チェック（5分以内か）
    delta = abs((now - event_time).total_seconds())
    if delta > 300:  # 5分（300秒）を超えていれば拒否
        current_logger.warning(
            f"タイムスタンプが許容範囲外: {timestamp_str} (差分: {delta:.2f}秒)")
        return False

    hmac_message = message_id + timestamp_str + body

    # WEBHOOK_SECRET is loaded at module level and updated by main.py via os.environ
    current_webhook_secret = os.getenv("WEBHOOK_SECRET")
    if not current_webhook_secret:
        current_logger.critical("WEBHOOK_SECRETが設定されていません。署名検証は不可能です。")
        # This is a critical setup error, should ideally prevent startup.
        return False  # Or raise an exception

    digest = hmac.new(
        current_webhook_secret.encode(
            'utf-8'), hmac_message.encode('utf-8'), hashlib.sha256
    ).hexdigest()
    expected_signature = f"sha256={digest}"

    if not hmac.compare_digest(signature, expected_signature):
        current_logger.warning(
            f"Webhook署名不一致。受信: {signature}, 期待値(計算結果): {expected_signature}")
        return False

    current_logger.debug("Webhook署名検証成功")  # Log success at debug level
    return True


# Allow passing logger
def get_existing_eventsub_subscriptions(logger_to_use=None):
    current_logger = logger_to_use if logger_to_use else logger
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token(logger_to_use=current_logger)}",
    }
    response = requests.get(url, headers=headers, timeout=20)  # timeout追加
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        current_logger.error(
            f"既存サブスクリプション取得エラー: {response.status_code} - {response.text}")
        return []


# サブスクリプションの追加
# Added event_type parameter and logger
def create_eventsub_subscription(event_type: str, logger_to_use=None):
    current_logger = logger_to_use if logger_to_use else logger
    current_audit_logger = logging.getLogger(
        "AuditLogger")  # Get audit logger instance

    # 既存サブスクリプション一覧を取得
    existing = get_existing_eventsub_subscriptions(
        logger_to_use=current_logger)
    for sub in existing:
        if (
            sub.get("type") == event_type  # Use event_type
            and sub.get("condition", {}).get("broadcaster_user_id")
            == TWITCH_BROADCASTER_ID  # Global TWITCH_BROADCASTER_ID
            and sub.get("status") == "enabled"
        ):
            current_logger.info(
                f"既に同じ {event_type} サブスクリプションが存在するため新規作成をスキップします"  # Updated log
            )
            current_audit_logger.info(
                # Updated audit log
                f"EventSubサブスクリプション作成: {event_type} (既に存在) 成功")
            # Return similar structure as new sub
            return {"status": "already exists", "id": sub.get("id"), "data": [sub]}

    # なければ新規作成
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    current_webhook_secret = os.getenv("WEBHOOK_SECRET")  # Get current secret
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token(logger_to_use=current_logger)}",
        "Content-Type": "application/json",
    }
    payload = {
        "type": event_type,  # Use event_type
        "version": "1",  # Assuming version "1" is applicable for all types used
        "condition": {"broadcaster_user_id": TWITCH_BROADCASTER_ID},
        "transport": {
            "method": "webhook",
            "callback": os.getenv("WEBHOOK_CALLBACK_URL"),
            "secret": current_webhook_secret,  # Use current secret
        },
    }

    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=15)  # timeout追加
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        current_audit_logger.info(
            f"EventSubサブスクリプション作成: {event_type} 成功")  # Updated audit log
        current_logger.info(
            f"EventSubサブスクリプション ({event_type}) を正常に作成しました。ID: {result.get('data', [{}])[0].get('id')}")
        return result
    except requests.exceptions.HTTPError as e:
        # Try to get more details from response if possible
        error_details = e.response.text if e.response else "N/A"
        reason = f"HTTPError: {e.response.status_code if e.response else 'Unknown status'} - {error_details}"
        current_audit_logger.warning(
            # Updated audit log
            f"EventSubサブスクリプション作成: {event_type} 失敗: {reason}")
        current_logger.error(
            f"EventSubサブスクリプション ({event_type}) 作成失敗: {reason}")
        # Return a more structured error, possibly including the response JSON if available
        try:
            error_json = e.response.json() if e.response else {}
            return {"status": "error", "reason": reason, "details": error_json, "http_status": e.response.status_code if e.response else None}
        except ValueError:  # If response is not JSON
            return {"status": "error", "reason": reason, "details": error_details, "http_status": e.response.status_code if e.response else None}
    except Exception as e:  # Catch other exceptions like requests.ConnectionError, etc.
        reason = str(e)
        current_audit_logger.warning(
            # Updated audit log
            f"EventSubサブスクリプション作成: {event_type} 失敗: {reason}")
        current_logger.error(
            f"EventSubサブスクリプション ({event_type}) 作成中に予期せぬエラー: {reason}", exc_info=True)
        return {"status": "error", "reason": reason}

# サブスクリプションの削除


# Allow passing logger
def delete_eventsub_subscription(subscription_id, logger_to_use=None):
    current_logger = logger_to_use if logger_to_use else logger
    current_audit_logger = logging.getLogger("AuditLogger")

    url = (
        f"https://api.twitch.tv/helix/eventsub/subscriptions?"
        f"id={subscription_id}"
    )
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token(logger_to_use=current_logger)}"
    }
    response = requests.delete(url, headers=headers, timeout=15)  # timeout追加
    if response.status_code == 204:
        current_logger.info(f"EventSubサブスクリプション削除: {subscription_id} 成功")
        current_audit_logger.info(f"EventSubサブスクリプション削除: {subscription_id}")
    else:
        current_logger.warning(
            f"EventSubサブスクリプション削除: {subscription_id} 失敗: {response.status_code} - {response.text}")
        current_audit_logger.warning(
            f"EventSubサブスクリプション削除: {subscription_id} 失敗: {response.status_code} - {response.text}")

# サブスクリプションの確認と削除の処理


# Allow passing logger
def cleanup_eventsub_subscriptions(webhook_callback_url, logger_to_use=None):
    current_logger = logger_to_use if logger_to_use else logger
    current_logger.info("既存のEventSubサブスクリプションのクリーンアップを開始します...")
    subs = get_existing_eventsub_subscriptions(logger_to_use=current_logger)
    deleted_count = 0
    if not subs:
        current_logger.info("クリーンアップ対象の既存サブスクリプションはありませんでした。")
        return

    for sub in subs:
        sub_id = sub.get("id", "ID不明")
        sub_type = sub.get("type", "タイプ不明")
        sub_status = sub.get("status", "ステータス不明")
        sub_callback = sub.get("transport", {}).get("callback", "コールバック不明")

        # 自分のWebhook URLと異なるもの、またはstatusが"enabled"でないものを削除
        # "webhook_callback_verification_failed" や "notification_failures_exceeded" なども対象
        if sub_callback != webhook_callback_url or sub_status not in ["enabled", "webhook_callback_verification_pending"]:
            current_logger.info(
                f"サブスクリプションID {sub_id} (タイプ: {sub_type}, ステータス: {sub_status}, コールバック: {sub_callback}) は無効または古い設定のため削除します。")
            delete_eventsub_subscription(sub_id, logger_to_use=current_logger)
            deleted_count += 1
        else:
            current_logger.info(
                f"サブスクリプションID {sub_id} (タイプ: {sub_type}, ステータス: {sub_status}) は有効なため保持します。")

    current_logger.info(
        f"EventSubサブスクリプションのクリーンアップ完了。{deleted_count}件のサブスクリプションを削除しました。")
