# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
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

# 環境設定ファイルの場所を指定
# settings.envのパスを「eventsub.pyと同じディレクトリ」に修正
env_path = Path(__file__).parent / "settings.env"
load_dotenv(dotenv_path=env_path)

# ログの設定
logger = logging.getLogger("AppLogger")
audit_logger = logging.getLogger("AuditLogger")

# タイムゾーンの設定
TIMEZONE_NAME = os.getenv("TIMEZONE", "system")
if TIMEZONE_NAME.lower() == "system":  # システムのタイムゾーンを自動取得
    try:
        TIMEZONE = get_localzone()
    except Exception as e:
        logger.warning(f"システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
        TIMEZONE = pytz.utc
elif TIMEZONE_NAME:
    try:
        TIMEZONE = pytz.timezone(TIMEZONE_NAME)
    except pytz.UnknownTimeZoneError:
        logger.warning(f"無効なタイムゾーン: {TIMEZONE_NAME}。システムタイムゾーンにフォールバックします。")
        try:
            TIMEZONE = get_localzone()
        except Exception as e:
            logger.warning(f"システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
            TIMEZONE = pytz.utc
    except Exception as e:
        logger.warning(
            f"タイムゾーン '{TIMEZONE_NAME}' の処理中にエラーが発生しました ({e})。UTCにフォールバックします。")
        TIMEZONE = pytz.utc
else:
    logger.warning("TIMEZONE環境変数が空です。システムタイムゾーンにフォールバックします。")
    try:
        TIMEZONE = get_localzone()
    except Exception as e:
        logger.warning(f"システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
        TIMEZONE = pytz.utc

# タイムゾーン付き現在時刻取得関数


def get_current_time():
    # 現在時刻をタイムゾーン付きで取得
    return datetime.datetime.now(TIMEZONE)


# 環境変数の取得
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
def get_app_access_token(logger_to_use=None):
    # Twitchアプリのアクセストークンを取得または更新する
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
        current_logger.info("TwitchAPIアクセストークンを取得・更新しました。")
        return token, expires_at
    else:
        current_logger.error(
            f"Twitchアクセストークン取得失敗: {response.status_code} - {response.text}")
        return None, 0

# アクセストークンの検証


def get_valid_app_access_token(logger_to_use=None):
    # 有効なTwitchアプリのアクセストークンを返す（期限切れなら再取得）
    global TWITCH_APP_ACCESS_TOKEN, TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT
    current_logger = logger_to_use if logger_to_use else logger
    if not TWITCH_APP_ACCESS_TOKEN or time.time() > TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT:
        current_logger.info("TwitchAPIアクセストークンの確認と検証を実行しました。")
        TWITCH_APP_ACCESS_TOKEN, TWITCH_APP_ACCESS_TOKEN_EXPIRES_AT = (
            get_app_access_token(logger_to_use=current_logger)
        )
    return TWITCH_APP_ACCESS_TOKEN

# Twitchのユーザー名からBROADCASTER_IDを取得


def get_broadcaster_id(username, logger_to_use=None):
    # 指定したユーザー名からTwitchのユーザーIDを取得する
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


def setup_broadcaster_id(logger_to_use=None):
    # BROADCASTER_IDがユーザー名の場合は数値IDに変換する
    global TWITCH_BROADCASTER_ID
    current_logger = logger_to_use if logger_to_use else logger
    if TWITCH_BROADCASTER_ID is None or not TWITCH_BROADCASTER_ID.strip():
        current_logger.critical(
            "TWITCH_BROADCASTER_IDが設定されていません。アプリケーションは起動できません。")
        raise ValueError("TWITCH_BROADCASTER_ID is not set.")

    if not TWITCH_BROADCASTER_ID.isdigit():
        original_username = TWITCH_BROADCASTER_ID
        current_logger.info(
            f"TWITCHユーザーIDをAPIアクセス用IDに変換します。")
        try:
            TWITCH_BROADCASTER_ID = get_broadcaster_id(
                original_username, logger_to_use=current_logger)
            current_logger.info(
                f"ユーザーID変換完了: {original_username} -> {TWITCH_BROADCASTER_ID}")
        except Exception as e:
            current_logger.critical(
                f"TWITCHユーザーIDからAPIアクセス用IDへの変換に失敗しました: {e}", exc_info=True)
            raise
    else:
        current_logger.info(
            f"TWITCH_BROADCASTER_ID は既に数値形式です: {TWITCH_BROADCASTER_ID}")
    # os.environも更新して他の箇所でも数値IDを参照できるようにする
    os.environ['TWITCH_BROADCASTER_ID'] = TWITCH_BROADCASTER_ID

# Signatureの検証


def verify_signature(request):
    # Webhookリクエストの署名を検証する
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
    body = request.get_data(as_text=True)  # ボディを文字列で取得

    # タイムスタンプのパース（ナノ秒対応）
    def parse_timestamp(ts: str):
        # タイムスタンプ文字列をdatetimeオブジェクトに変換
        dt_obj = None
        if '.' in ts and ts.endswith('Z'):
            main_part, fractional = ts[:-1].split('.', 1)
            fractional = fractional[:6]  # マイクロ秒まで
            dt_obj = datetime.datetime.fromisoformat(
                f"{main_part}.{fractional}+00:00")
        elif '+' in ts[10:] or '-' in ts[10:]:
            dt_obj = datetime.datetime.fromisoformat(ts)
        else:
            dt_obj = datetime.datetime.fromisoformat(ts)
        return dt_obj.astimezone(TIMEZONE)

    now = datetime.datetime.now(TIMEZONE)

    try:
        event_time = parse_timestamp(timestamp_str)
    except Exception as e:
        current_logger.warning(f"タイムスタンプ '{timestamp_str}' の解析エラー: {str(e)}")
        return False

    # 時間差チェック（5分以内か）
    delta = abs((now - event_time).total_seconds())
    if delta > 300:
        current_logger.warning(
            f"タイムスタンプが許容範囲外: {timestamp_str} (差分: {delta:.2f}秒)")
        return False

    hmac_message = message_id + timestamp_str + body

    current_webhook_secret = os.getenv("WEBHOOK_SECRET")
    if not current_webhook_secret:
        current_logger.critical("WEBHOOK_SECRETが設定されていません。署名検証は不可能です。")
        return False

    digest = hmac.new(
        current_webhook_secret.encode(
            'utf-8'), hmac_message.encode('utf-8'), hashlib.sha256
    ).hexdigest()
    expected_signature = f"sha256={digest}"

    if not hmac.compare_digest(signature, expected_signature):
        current_logger.warning(
            f"Webhook署名不一致。受信: {signature}, 期待値(計算結果): {expected_signature}")
        return False

    current_logger.debug("Webhook署名検証成功")
    return True

# 既存のEventSubサブスクリプション一覧を取得


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


def create_eventsub_subscription(event_type: str, logger_to_use=None):
    # 指定したイベントタイプのEventSubサブスクリプションを作成する
    current_logger = logger_to_use if logger_to_use else logger
    current_audit_logger = logging.getLogger("AuditLogger")

    # 既存サブスクリプション一覧を取得
    existing = get_existing_eventsub_subscriptions(
        logger_to_use=current_logger)
    for sub in existing:
        if (
            sub.get("type") == event_type
            and sub.get("condition", {}).get("broadcaster_user_id")
            == TWITCH_BROADCASTER_ID
            and sub.get("status") == "enabled"
        ):
            current_logger.info(
                f"既に同じ {event_type} サブスクリプションが存在するため新規作成をスキップします"
            )
            current_audit_logger.info(
                f"EventSubサブスクリプション作成: {event_type} (既に存在) 成功")
            return {"status": "already exists", "id": sub.get("id"), "data": [sub]}

    # サブスクリプションがなければ新規作成
    url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    current_webhook_secret = os.getenv("WEBHOOK_SECRET")
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {get_valid_app_access_token(logger_to_use=current_logger)}",
        "Content-Type": "application/json",
    }
    payload = {
        "type": event_type,
        "version": "1",
        "condition": {"broadcaster_user_id": TWITCH_BROADCASTER_ID},
        "transport": {
            "method": "webhook",
            "callback": os.getenv("WEBHOOK_CALLBACK_URL"),
            "secret": current_webhook_secret,
        },
    }

    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=15)  # timeout追加
        response.raise_for_status()
        result = response.json()
        current_audit_logger.info(
            f"EventSubサブスクリプション作成: {event_type} 成功")
        current_logger.info(
            f"EventSubサブスクリプション ({event_type}) を正常に作成しました。ID: {result.get('data', [{}])[0].get('id')}")
        return result
    except requests.exceptions.HTTPError as e:
        error_details = e.response.text if e.response else "N/A"
        reason = f"HTTPError: {e.response.status_code if e.response else 'Unknown status'} - {error_details}"
        current_audit_logger.warning(
            f"EventSubサブスクリプション作成: {event_type} 失敗: {reason}")
        current_logger.error(
            f"EventSubサブスクリプション ({event_type}) 作成失敗: {reason}")
        try:
            error_json = e.response.json() if e.response else {}
            return {"status": "error", "reason": reason, "details": error_json, "http_status": e.response.status_code if e.response else None}
        except ValueError:
            return {"status": "error", "reason": reason, "details": error_details, "http_status": e.response.status_code if e.response else None}
    except Exception as e:
        reason = str(e)
        current_audit_logger.warning(
            f"EventSubサブスクリプション作成: {event_type} 失敗: {reason}")
        current_logger.error(
            f"EventSubサブスクリプション ({event_type}) 作成中に予期せぬエラー: {reason}", exc_info=True)
        return {"status": "error", "reason": reason}

# サブスクリプションの削除


def delete_eventsub_subscription(subscription_id, logger_to_use=None):
    # 指定したIDのEventSubサブスクリプションを削除する
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


def cleanup_eventsub_subscriptions(webhook_callback_url, logger_to_use=None):
    # 指定したWebhook URLに紐づかない、または無効なEventSubサブスクリプションを削除する
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
