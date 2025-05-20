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
                        f"リトライ{
                            attempt}/{
                                max_retries}回目: {
                                    func.__name__
                        } 例外: {e}"
                    )
                    last_exception = e
                    time.sleep(wait_seconds)
            if last_exception is not None:
                raise last_exception
            else:
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
    env = read_env()
    # JSTタイムゾーンで現在時刻を取得
    jst = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(jst)
    last_rotated = env.get(ROTATED_KEY_NAME)
    need_rotate = force

    if not env.get(SECRET_KEY_NAME):
        need_rotate = True
    else:
        if last_rotated:
            try:
                # 既存値がUTC表記ならパース方法に注意
                dt = None
                try:
                    dt = datetime.datetime.strptime(
                        last_rotated, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).astimezone(jst)
                except Exception:
                    dt = datetime.datetime.strptime(
                        last_rotated, "%Y-%m-%dT%H:%M:%S%z")
                if (now - dt).days >= 30:
                    need_rotate = True
            except Exception:
                need_rotate = True
        else:
            need_rotate = True

    if need_rotate:
        new_secret = generate_secret(32)
        # JSTでフォーマット
        env[SECRET_KEY_NAME] = new_secret
        env[ROTATED_KEY_NAME] = now.strftime("%Y-%m-%dT%H:%M:%S%z")
        update_env_file_preserve_comments(SETTINGS_ENV_PATH, {
            SECRET_KEY_NAME: new_secret,
            ROTATED_KEY_NAME: env[ROTATED_KEY_NAME]
        })
        if logger:
            audit_logger.info("WEBHOOK_SECRETを自動生成・ローテーションしました")
        print("WEBHOOK_SECRETを自動生成・ローテーションしました")
        return env[SECRET_KEY_NAME]
    else:
        return env[SECRET_KEY_NAME]


def is_valid_url(url):
    return isinstance(url, str) and (url.startswith("http://") or url.startswith("https://"))
