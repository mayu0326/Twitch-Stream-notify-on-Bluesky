# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

import re
import datetime as dt_module # Alias to avoid conflict with datetime class
from datetime import datetime, timezone # Specific imports
import os
import secrets
import logging
import time
import pytz 
from tzlocal import get_localzone 
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

# Logger for utility functions, can be configured by the main app
util_logger = logging.getLogger("AppLogger.Utils") # Create a child logger

def format_datetime_filter(iso_datetime_str, fmt="%Y-%m-%d %H:%M %Z"):
    if not iso_datetime_str:
        return ""
    try:
        # Assume iso_datetime_str is like "2023-10-27T10:00:00Z" from Twitch
        dt_utc = datetime.fromisoformat(iso_datetime_str.replace('Z', '+00:00'))
        
        # Get target timezone from environment or default to system local
        target_tz_name = os.getenv("TIMEZONE", "system")
        target_tz = None

        if target_tz_name.lower() == "system":
            try:
                target_tz = get_localzone()
                if target_tz is None: # tzlocal can return None if it can't determine the timezone
                    util_logger.warning("format_datetime_filter: tzlocal.get_localzone() returned None. Falling back to UTC.")
                    target_tz = timezone.utc
            except Exception as e: # Catch any error from get_localzone()
                util_logger.warning(f"format_datetime_filter: Error getting system timezone with tzlocal: {e}. Falling back to UTC.")
                target_tz = timezone.utc
        else:
            try:
                target_tz = pytz.timezone(target_tz_name)
            except pytz.UnknownTimeZoneError:
                util_logger.warning(f"format_datetime_filter: Unknown timezone '{target_tz_name}' in settings. Falling back to UTC.")
                target_tz = timezone.utc
            except Exception as e: # Catch other potential errors from pytz.timezone
                util_logger.warning(f"format_datetime_filter: Error processing timezone '{target_tz_name}': {e}. Falling back to UTC.")
                target_tz = timezone.utc
        
        dt_localized = dt_utc.astimezone(target_tz)
        return dt_localized.strftime(fmt)
    except ValueError as e: 
        util_logger.error(f"format_datetime_filter: Error formatting datetime string '{iso_datetime_str}' with format '{fmt}': {e}")
        return iso_datetime_str # Return original on error
    except Exception as e: # Catch any other unexpected error
        util_logger.error(f"format_datetime_filter: Unexpected error processing datetime string '{iso_datetime_str}': {e}")
        return iso_datetime_str


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
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    # Assuming logger is configured and accessible
                    logging.getLogger("AppLogger").warning(
                        f"リトライ{attempt}/{max_retries}回目: {func.__name__} "
                        f"例外: {e}"
                    )
                    last_exception = e
                    time.sleep(wait_seconds)
            if last_exception is not None:
                raise last_exception
            # This else might not be reached if an exception is always raised.
            # Consider what should happen if func never succeeds but doesn't raise an exception
            # that's caught by the 'exceptions' tuple. For now, it implies a logic error
            # or unexpected success after retries (which should have returned earlier).
            return None # Or raise a generic error if this path means failure
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
    logger_to_use = logger if logger else logging.getLogger("AppLogger")

    env = read_env()
    
    TIMEZONE_NAME = os.getenv("TIMEZONE", "system")
    tz_object = None
    if TIMEZONE_NAME.lower() == "system":
        try:
            tz_object = get_localzone()
            if tz_object is None:
                logger_to_use.warning("rotate_secret: tzlocal.get_localzone() returned None. Falling back to UTC.")
                tz_object = timezone.utc
        except Exception as e:
            logger_to_use.warning(f"rotate_secret: Error getting system timezone with tzlocal: {e}. Falling back to UTC.")
            tz_object = timezone.utc
    else:
        try:
            tz_object = pytz.timezone(TIMEZONE_NAME)
        except pytz.UnknownTimeZoneError:
            logger_to_use.warning(
                f"rotate_secret: 指定されたタイムゾーン '{TIMEZONE_NAME}' は無効です。"
                f"システムタイムゾーンにフォールバックします。"
            )
            try:
                tz_object = get_localzone()
                if tz_object is None:
                    logger_to_use.warning("rotate_secret: tzlocal.get_localzone() (fallback) returned None. Falling back to UTC.")
                    tz_object = timezone.utc
            except Exception as e:
                logger_to_use.warning(f"rotate_secret: システムタイムゾーンの取得に失敗しました ({e})。UTCにフォールバックします。")
                tz_object = timezone.utc
        except Exception as e: 
            logger_to_use.warning(f"rotate_secret: タイムゾーン '{TIMEZONE_NAME}' の処理中にエラーが発生しました ({e})。UTCにフォールバックします。")
            tz_object = timezone.utc

    if tz_object is None: 
        logger_to_use.warning("rotate_secret: タイムゾーン解決に最終的に失敗しました。UTCを使用します。")
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
                    logger_to_use.info(f"WEBHOOK_SECRETが30日以上経過しているため ({ (now - last_rotated_dt).days } 日)、ローテーションします。")
            except ValueError:
                logger_to_use.warning(
                    f"SECRET_LAST_ROTATED の日付形式 '{last_rotated_str}' が不正です。"
                    "WEBHOOK_SECRETをローテーションします。"
                )
                need_rotate = True 
            except Exception as e: 
                logger_to_use.warning(
                    f"SECRET_LAST_ROTATED の処理中にエラーが発生しました ({e})。"
                    "WEBHOOK_SECRETをローテーションします。"
                )
                need_rotate = True
        else:
            need_rotate = True 
            logger_to_use.info("SECRET_LAST_ROTATED が未設定のため、WEBHOOK_SECRETをローテーションします。")


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
    return isinstance(url, str) and (
        url.startswith("http://") or url.startswith("https://"))

# Example of how to use the logger for this function if called directly for testing
if __name__ == '__main__':
    # Configure a basic logger for testing format_datetime_filter
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    util_logger.info("Testing format_datetime_filter...")
    
    # Test cases for format_datetime_filter
    test_iso_str = "2023-10-27T10:00:00Z"
    print(f"Original ISO: {test_iso_str}")

    os.environ["TIMEZONE"] = "Asia/Tokyo"
    print(f"To Asia/Tokyo: {format_datetime_filter(test_iso_str)}")
    print(f"To Asia/Tokyo (custom format): {format_datetime_filter(test_iso_str, fmt='%Y年%m月%d日 %H時%M分%S秒 %Z%z')}")
    
    os.environ["TIMEZONE"] = "America/New_York"
    print(f"To America/New_York: {format_datetime_filter(test_iso_str)}")

    os.environ["TIMEZONE"] = "system" # Assuming system is something valid like Europe/London for this test
    print(f"To System Local: {format_datetime_filter(test_iso_str)}")
    
    os.environ["TIMEZONE"] = "Invalid/Timezone"
    print(f"To Invalid Timezone (fallback to UTC): {format_datetime_filter(test_iso_str)}")

    print(f"Empty string input: '{format_datetime_filter('')}'")
    print(f"Invalid ISO string input: '{format_datetime_filter('not a date')}'")
    print(f"Valid ISO, invalid fmt: '{format_datetime_filter(test_iso_str, fmt='%%InvalidFormat')}'") #ValueError from strftime

    # Test rotate_secret_if_needed
    util_logger.info("\nTesting rotate_secret_if_needed...")
    # Ensure TIMEZONE is set for rotate_secret_if_needed tests
    os.environ["TIMEZONE"] = "UTC" 
    print(f"Rotation Test (forced): New secret is {rotate_secret_if_needed(logger=util_logger, force=True)}")
    # Clean up dummy settings.env if created by rotate_secret_if_needed
    if os.path.exists(SETTINGS_ENV_PATH):
        os.remove(SETTINGS_ENV_PATH)

    util_logger.info("Util tests complete.")
