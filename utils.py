# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

import re
import datetime
import os
import secrets
import logging
import time
import pytz # Added
from tzlocal import get_localzone # Added
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


def update_env_file_preserve_comments(file_path, updates):
    """
    file_path: path to the .env file
    updates: dict of key-value pairsを更新
    コメント・空行はそのまま残す
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
            # コメントまたは空行
            new_lines.append(line)

    # 新規追加が必要なキー（既存にないもの）は末尾に追加
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
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logging.getLogger("AppLogger").warning(
                        f"リトライ{attempt}/{max_retries}回目: {func.__name__} "
                        f"例外: {e}"
                    )
                    last_exception = e
                    time.sleep(wait_seconds)
            if last_exception is not None:
                raise last_exception
            else:
                # This else block might not be reachable if all retries fail and last_exception is always set.
                # Consider re-raising last_exception directly after the loop if it's set.
                raise Exception("リトライ回数を超過したため、処理を終了します。")
        return wrapper
    return decorator


def generate_secret(length=32):
    return secrets.token_hex(length)


def read_env(path=SETTINGS_ENV_PATH):
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
    if logger is None:
        logger_to_use = logging.getLogger("AppLogger")
    else:
        logger_to_use = logger

    env = read_env()
    
    TIMEZONE_NAME = os.getenv("TIMEZONE", "system")
    tz_object = None
    if TIMEZONE_NAME.lower() == "system":
        try:
            tz_object = get_localzone()
        except Exception as e:
            logger_to_use.warning(f"システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
            tz_object = pytz.utc
    else:
        try:
            tz_object = pytz.timezone(TIMEZONE_NAME)
        except pytz.UnknownTimeZoneError:
            logger_to_use.warning(
                f"指定されたタイムゾーン '{TIMEZONE_NAME}' は無効です。"
                f"システムタイムゾーンにフォールバックします。"
            )
            try:
                tz_object = get_localzone()
            except Exception as e:
                logger_to_use.warning(f"システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
                tz_object = pytz.utc
        except Exception as e: # Catch other potential errors from pytz.timezone
            logger_to_use.warning(f"タイムゾーン '{TIMEZONE_NAME}' の処理中にエラーが発生しました ({e})。UTCにフォールバックします。")
            tz_object = pytz.utc

    if tz_object is None: # Final fallback if all attempts fail
        logger_to_use.warning("タイムゾーン解決に失敗しました。UTCを使用します。")
        tz_object = pytz.utc

    now = datetime.datetime.now(tz_object)
    last_rotated_str = env.get(ROTATED_KEY_NAME)
    need_rotate = force

    if not env.get(SECRET_KEY_NAME):
        need_rotate = True
        logger_to_use.info("WEBHOOK_SECRETが見つからないため、新規生成します。")
    else:
        if last_rotated_str:
            try:
                # Attempt to parse with timezone info first (ISO 8601 format)
                last_rotated_dt = datetime.datetime.fromisoformat(last_rotated_str)
                # If naive, assume it was stored in the determined tz_object's timezone or convert if different
                if last_rotated_dt.tzinfo is None:
                    last_rotated_dt = tz_object.localize(last_rotated_dt)
                else: # Ensure it's in the same timezone as 'now' for correct comparison
                    last_rotated_dt = last_rotated_dt.astimezone(tz_object)

                if (now - last_rotated_dt).days >= 30:
                    need_rotate = True
                    logger_to_use.info(f"WEBHOOK_SECRETが30日以上経過しているため ({ (now - last_rotated_dt).days } 日)、ローテーションします。")
            except ValueError:
                logger_to_use.warning(
                    f"SECRET_LAST_ROTATED の日付形式 '{last_rotated_str}' が不正です。"
                    "WEBHOOK_SECRETをローテーションします。"
                )
                need_rotate = True # Force rotation if format is invalid
            except Exception as e: # Catch other potential errors during date parsing
                logger_to_use.warning(
                    f"SECRET_LAST_ROTATED の処理中にエラーが発生しました ({e})。"
                    "WEBHOOK_SECRETをローテーションします。"
                )
                need_rotate = True
        else:
            need_rotate = True # No last_rotated date, so rotate
            logger_to_use.info("SECRET_LAST_ROTATED が未設定のため、WEBHOOK_SECRETをローテーションします。")


    if need_rotate:
        new_secret = generate_secret(32)
        # Format with timezone information
        new_rotated_time_str = now.strftime("%Y-%m-%dT%H:%M:%S%z") 
        if not new_rotated_time_str.endswith("+0000") and not new_rotated_time_str.endswith("-0000") and len(new_rotated_time_str) > 19+5 : # ensure proper format
            # Python's %z can produce HHMM, but ISO 8601 often prefers HH:MM.
            # For simplicity and consistency with previous format if it was just Z, let's check.
            # If timezone is UTC, strftime %z might be empty or +0000. If it has offset, ensure it's formatted.
            # This part might need adjustment based on desired strictness of %z output.
            # A simpler approach for ISO 8601 is `now.isoformat()`
            new_rotated_time_str = now.isoformat()


        env[SECRET_KEY_NAME] = new_secret
        env[ROTATED_KEY_NAME] = new_rotated_time_str 
        
        update_env_file_preserve_comments(SETTINGS_ENV_PATH, {
            SECRET_KEY_NAME: new_secret,
            ROTATED_KEY_NAME: new_rotated_time_str
        })
        # Use the passed or determined logger
        logger_to_use.info("WEBHOOK_SECRETを自動生成・ローテーションしました")
        audit_logger.info("WEBHOOK_SECRETを自動生成・ローテーションしました") # Keep audit log as it was
        return env[SECRET_KEY_NAME]
    else:
        return env[SECRET_KEY_NAME]


def is_valid_url(url):
    return isinstance(url, str) and (
        url.startswith("http://") or url.startswith("https://"))

# Example of how to use the logger for this function if called directly for testing
if __name__ == '__main__':
    # Configure a basic logger for testing
    test_logger = logging.getLogger("TestLogger")
    test_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    test_logger.addHandler(handler)
    
    # Test with system timezone
    os.environ["TIMEZONE"] = "system"
    print(f"System Timezone Test: New secret is {rotate_secret_if_needed(logger=test_logger, force=True)}")

    # Test with a specific valid timezone
    os.environ["TIMEZONE"] = "America/New_York"
    print(f"America/New_York Test: New secret is {rotate_secret_if_needed(logger=test_logger, force=True)}")

    # Test with an invalid timezone
    os.environ["TIMEZONE"] = "Invalid/Timezone"
    print(f"Invalid Timezone Test: New secret is {rotate_secret_if_needed(logger=test_logger, force=True)}")

    # Test without TIMEZONE env var (should default to system)
    if "TIMEZONE" in os.environ:
        del os.environ["TIMEZONE"]
    print(f"Default (System) Timezone Test: New secret is {rotate_secret_if_needed(logger=test_logger, force=True)}")

    # Test with UTC
    os.environ["TIMEZONE"] = "UTC"
    print(f"UTC Test: New secret is {rotate_secret_if_needed(logger=test_logger, force=True)}")

    # Create a dummy settings.env for testing rotation logic based on date
    with open(SETTINGS_ENV_PATH, "w", encoding="utf-8") as f:
        f.write(f"{SECRET_KEY_NAME}=oldsecret\n")
        old_date = (datetime.datetime.now(pytz.utc) - datetime.timedelta(days=35)).isoformat()
        f.write(f"{ROTATED_KEY_NAME}={old_date}\n")
    
    print(f"Rotation due to age test: New secret is {rotate_secret_if_needed(logger=test_logger)}")
    
    # Clean up dummy settings.env
    if os.path.exists(SETTINGS_ENV_PATH):
        os.remove(SETTINGS_ENV_PATH)

    test_logger.info("Test complete.")
