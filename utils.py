# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from tkinter import filedialog
import requests
from version_info import __version__
import re
import datetime as dt_module  # datetimeクラスとの衝突を避けるためのエイリアス
from datetime import datetime, timezone  # 必要なクラスのみインポート
import os
import secrets
import logging
import time
import pytz
from tzlocal import get_localzone
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

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

# ユーティリティ関数用のロガー（メインアプリから設定可能）
util_logger = logging.getLogger("AppLogger.Utils")  # サブロガーを作成


def format_datetime_filter(iso_datetime_str, fmt="%Y-%m-%d %H:%M %Z"):
    """
    ISO形式の日時文字列を指定タイムゾーン・フォーマットで整形して返す
    """
    if not iso_datetime_str:
        return ""
    try:
        # 例: "2023-10-27T10:00:00Z" のような文字列をUTCとして解釈
        dt_utc = datetime.fromisoformat(
            iso_datetime_str.replace('Z', '+00:00'))

        # 環境変数からタイムゾーンを取得（未指定ならシステムローカル）
        target_tz_name = os.getenv("TIMEZONE", "system")
        target_tz = None

        if target_tz_name.lower() == "system":
            try:
                target_tz = get_localzone()
                if target_tz is None:
                    util_logger.warning(
                        "format_datetime_filter: tzlocal.get_localzone()がNoneを返しました。UTCにフォールバックします。")
                    target_tz = timezone.utc
            except Exception as e:
                util_logger.warning(
                    f"format_datetime_filter: tzlocalでシステムタイムゾーン取得エラー: {e}。UTCにフォールバックします。")
                target_tz = timezone.utc
        else:
            try:
                target_tz = pytz.timezone(target_tz_name)
            except pytz.UnknownTimeZoneError:
                util_logger.warning(
                    f"format_datetime_filter: 設定のタイムゾーン '{target_tz_name}' が不明です。UTCにフォールバックします。")
                target_tz = timezone.utc
            except Exception as e:
                util_logger.warning(
                    f"format_datetime_filter: pytz.timezoneでエラー: '{target_tz_name}': {e}。UTCにフォールバックします。")
                target_tz = timezone.utc

        dt_localized = dt_utc.astimezone(target_tz)
        return dt_localized.strftime(fmt)
    except ValueError as e:
        util_logger.error(
            f"format_datetime_filter: 日時文字列 '{iso_datetime_str}' のフォーマット '{fmt}' 変換エラー: {e}")
        return iso_datetime_str  # エラー時は元の文字列を返す
    except Exception as e:
        util_logger.error(
            f"format_datetime_filter: 予期せぬエラー: '{iso_datetime_str}': {e}")
        return iso_datetime_str


def update_env_file_preserve_comments(file_path, updates):
    """
    .envファイルのコメント・空行を保持したまま、指定キーのみ値を更新する
    file_path: .envファイルのパス
    updates: 更新するkey-valueの辞書
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    key_pattern = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=')
    new_lines = []
    updated_keys = set()

    for line in lines:
        match = key_pattern.match(line)
        if match:
            key = match.group(1)
            if key in updates:
                new_value = updates[key]
                new_line = f'{key}={new_value}\n'
                new_lines.append(new_line)
                updated_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    for key, value in updates.items():
        if key not in updated_keys:
            new_lines.append(f'{key}={value}\n')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


SETTINGS_ENV_PATH = "settings.env"
SECRET_KEY_NAME = "WEBHOOK_SECRET"
ROTATED_KEY_NAME = "SECRET_LAST_ROTATED"


def retry_on_exception(
        max_retries: int = 3,
        wait_seconds: float = 2,
        exceptions=(Exception,)
):
    """
    指定した例外が発生した場合にリトライするデコレータ
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    # ロガーが設定されている前提で警告を出力
                    logging.getLogger("AppLogger").warning(
                        f"リトライ{attempt}/{max_retries}回目: {func.__name__} "
                        f"例外: {e}"
                    )
                    last_exception = e
                    time.sleep(wait_seconds)
            if last_exception is not None:
                raise last_exception
            return None  # ここに到達するのは想定外
        return wrapper
    return decorator


def generate_secret(length=32):
    """
    指定バイト長のランダムな16進シークレット文字列を生成
    """
    return secrets.token_hex(length)


def read_env(path=SETTINGS_ENV_PATH):
    """
    .envファイルを辞書として読み込む
    """
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v
    return env


audit_logger = logging.getLogger("AuditLogger")


def rotate_secret_if_needed(logger=None, force=False):
    """
    WEBHOOK_SECRETの自動ローテーション（30日ごと or 強制時）
    """
    logger_to_use = logger if logger else logging.getLogger("AppLogger")

    env = read_env()

    TIMEZONE_NAME = os.getenv("TIMEZONE", "system")
    tz_object = None
    if TIMEZONE_NAME.lower() == "system":
        try:
            tz_object = get_localzone()
            if tz_object is None:
                logger_to_use.warning(
                    "rotate_secret: tzlocal.get_localzone()がNoneを返しました。UTCにフォールバックします。")
                tz_object = timezone.utc
        except Exception as e:
            logger_to_use.warning(
                f"rotate_secret: tzlocalでシステムタイムゾーン取得エラー: {e}。UTCにフォールバックします。")
            tz_object = timezone.utc
    else:
        try:
            tz_object = pytz.timezone(TIMEZONE_NAME)
        except pytz.UnknownTimeZoneError:
            logger_to_use.warning(
                f"rotate_secret: 指定タイムゾーン '{TIMEZONE_NAME}' は無効です。システムタイムゾーンにフォールバックします。"
            )
            try:
                tz_object = get_localzone()
                if tz_object is None:
                    logger_to_use.warning(
                        "rotate_secret: tzlocal.get_localzone() (fallback)がNoneを返しました。UTCにフォールバックします。")
                    tz_object = timezone.utc
            except Exception as e:
                logger_to_use.warning(
                    f"rotate_secret: システムタイムゾーン取得失敗 ({e})。UTCにフォールバックします。")
                tz_object = timezone.utc
        except Exception as e:
            logger_to_use.warning(
                f"rotate_secret: pytz.timezoneでエラー: '{TIMEZONE_NAME}' ({e})。UTCにフォールバックします。")
            tz_object = timezone.utc

    if tz_object is None:
        logger_to_use.warning("rotate_secret: タイムゾーン解決に失敗。UTCを使用します。")
        tz_object = timezone.utc

    now = datetime.now(tz_object)
    last_rotated_str = env.get(ROTATED_KEY_NAME)
    need_rotate = force

    if not env.get(SECRET_KEY_NAME):
        need_rotate = True
        logger_to_use.info("WEBHOOK_SECRETが見つからないため、新規生成します。")
    else:
        if last_rotated_str:
            try:
                last_rotated_dt = datetime.fromisoformat(last_rotated_str)
                if last_rotated_dt.tzinfo is None:
                    last_rotated_dt = tz_object.localize(last_rotated_dt)
                else:
                    last_rotated_dt = last_rotated_dt.astimezone(tz_object)

                if (now - last_rotated_dt).days >= 30:
                    need_rotate = True
                    logger_to_use.info(
                        f"WEBHOOK_SECRETが30日以上経過しているため ({(now - last_rotated_dt).days} 日)、ローテーションします。")
            except ValueError:
                logger_to_use.warning(
                    f"SECRET_LAST_ROTATED の日付形式 '{last_rotated_str}' が不正です。WEBHOOK_SECRETをローテーションします。"
                )
                need_rotate = True
            except Exception as e:
                logger_to_use.warning(
                    f"SECRET_LAST_ROTATED の処理中にエラーが発生しました ({e})。WEBHOOK_SECRETをローテーションします。"
                )
                need_rotate = True
        else:
            need_rotate = True
            logger_to_use.info(
                "SECRET_LAST_ROTATED が未設定のため、WEBHOOK_SECRETをローテーションします。")

    if need_rotate:
        new_secret = generate_secret(32)
        new_rotated_time_str = now.isoformat()

        env[SECRET_KEY_NAME] = new_secret
        env[ROTATED_KEY_NAME] = new_rotated_time_str

        update_env_file_preserve_comments(SETTINGS_ENV_PATH, {
            SECRET_KEY_NAME: new_secret,
            ROTATED_KEY_NAME: new_rotated_time_str
        })
        logger_to_use.info("WEBHOOK_SECRETを自動生成・ローテーションしました")
        audit_logger.info("WEBHOOK_SECRETを自動生成・ローテーションしました")
        return env[SECRET_KEY_NAME]
    else:
        return env[SECRET_KEY_NAME]


def is_valid_url(url):
    """
    URLがhttpまたはhttpsで始まるか判定
    """
    return isinstance(url, str) and (
        url.startswith("http://") or url.startswith("https://"))


def notify_discord_error(message: str):
    """
    DiscordのWebhookでエラー通知を送信
    """
    webhook_url = os.getenv("discord_error_notifier_url")
    if not webhook_url:
        return
    try:
        requests.post(webhook_url, json={"content": message})
    except Exception as e:
        util_logger.error(f"Discord通知に失敗: {e}")


def change_template_file(var):
    """
    テンプレートファイル選択ダイアログを開き、選択したパスをStringVar等にセットする共通関数
    """
    path = filedialog.askopenfilename(
        title="テンプレートファイルを選択", filetypes=[("Text files", "*.txt")])
    if path:
        var.set(path)


def change_image_file(var):
    """
    画像ファイル選択ダイアログを開き、選択したパスをStringVar等にセットする共通関数
    """
    path = filedialog.askopenfilename(
        title="画像ファイルを選択", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
    if path:
        var.set(path)


def get_ngrok_public_url(api_url="http://127.0.0.1:4040/api/tunnels", timeout=0.5, retries=20, logger=None):
    """
    ngrokのローカルAPIからpublic_urlを取得する（最大retries回リトライ）
    """
    import time
    logger = logger or util_logger
    for _ in range(retries):
        try:
            resp = requests.get(api_url, timeout=timeout)
            tunnels = resp.json().get("tunnels", [])
            for t in tunnels:
                if t.get("public_url"):
                    return t["public_url"]
        except Exception as e:
            logger.debug(f"ngrok APIからURL取得失敗: {e}")
        time.sleep(timeout)
    return None


def get_localtunnel_url_from_stdout(stdout_line):
    """
    localtunnelのstdoutからURLを抽出する（'your url is:'以降）
    """
    if "your url is:" in stdout_line:
        return stdout_line.strip().split("your url is:")[-1].strip()
    return None


def set_webhook_callback_url_temporary(url, env_path="settings.env"):
    """
    settings.envのWEBHOOK_CALLBACK_URL_TEMPORARYを指定URLで更新
    """
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    new_lines = []
    found = False
    for line in lines:
        if line.startswith('WEBHOOK_CALLBACK_URL_TEMPORARY='):
            new_lines.append(f'WEBHOOK_CALLBACK_URL_TEMPORARY={url}\n')
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f'WEBHOOK_CALLBACK_URL_TEMPORARY={url}\n')
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)


# このファイルを直接実行した場合のテストコード例
if __name__ == '__main__':
    # format_datetime_filterのテスト用ロガー設定
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    util_logger.info("Testing format_datetime_filter...")

    # format_datetime_filterのテストケース
    test_iso_str = "2023-10-27T10:00:00Z"
    # print(f"Original ISO: {test_iso_str}")

    os.environ["TIMEZONE"] = "Asia/Tokyo"
    # print(f"To Asia/Tokyo: {format_datetime_filter(test_iso_str)}")
    # print(
    #     f"To Asia/Tokyo (custom format): {format_datetime_filter(test_iso_str, fmt='%Y年%m月%d日 %H時%M分%S秒 %Z%z')}")

    os.environ["TIMEZONE"] = "America/New_York"
    # print(f"To America/New_York: {format_datetime_filter(test_iso_str)}")

    # システムローカルタイムゾーンでのテスト
    os.environ["TIMEZONE"] = "system"
    # print(f"To System Local: {format_datetime_filter(test_iso_str)}")

    os.environ["TIMEZONE"] = "Invalid/Timezone"
    # print(
    #     f"To Invalid Timezone (fallback to UTC): {format_datetime_filter(test_iso_str)}")

    # print(f"Empty string input: '{format_datetime_filter('')}'")
    # print(
    #     f"Invalid ISO string input: '{format_datetime_filter('not a date')}'")
    # strftimeでValueErrorが出るケース
    # print(
    #     f"Valid ISO, invalid fmt: '{format_datetime_filter(test_iso_str, fmt='%%InvalidFormat')}'")

    # rotate_secret_if_neededのテスト
    util_logger.info("\nTesting rotate_secret_if_needed...")
    # rotate_secret_if_neededのテスト用にTIMEZONEをUTCに設定
    os.environ["TIMEZONE"] = "UTC"
    # セキュリティ上の理由でシークレット値は表示しない
    rotate_secret_if_needed(logger=util_logger, force=True)
    # print("Rotation Test (forced): 新しいシークレットが生成されました（値は表示しません）")
    # テストで作成されたsettings.envを削除
    if os.path.exists(SETTINGS_ENV_PATH):
        os.remove(SETTINGS_ENV_PATH)

    util_logger.info("Util tests complete.")
