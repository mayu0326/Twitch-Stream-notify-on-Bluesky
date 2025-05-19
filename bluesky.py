# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from version import __version__

__author__    = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__   = "GPLv2"
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from atproto import Client, exceptions
import logging
import csv
import os
from utils import retry_on_exception

RETRY_MAX = int(os.getenv("RETRY_MAX", 3))
RETRY_WAIT = int(os.getenv("RETRY_WAIT", 2))

from datetime import datetime

logger = logging.getLogger("AppLogger")

# settings.envでテンプレートパスを指定
TEMPLATE_PATH = os.getenv("BLUESKY_TEMPLATE_PATH", "templates/default_template.txt")

def load_template(path=None):
    if path is None:
        path = TEMPLATE_PATH
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"テンプレートファイルが見つかりません: {path}")
        # デフォルトテンプレートを返す
        return "🔴 放送を開始しました！\nタイトル: {title}\nカテゴリ: {category}\nURL: {url}"

def is_valid_url(url):
    return isinstance(url, str) and (url.startswith("http://") or url.startswith("https://"))

audit_logger = logging.getLogger("AuditLogger")

class BlueskyPoster:
    def __init__(self, username, password):
        self.client = Client()
        self.username = username
        self.password = password
    def upload_image(self, image_path):
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()
        blob = self.client.upload_blob(img_bytes)
        return blob
        
    @retry_on_exception(
        max_retries=RETRY_MAX,
        wait_seconds=RETRY_WAIT,
        exceptions=(exceptions.AtProtocolError,)
    )

    def post_stream_online(self, title, category, url,username=None, display_name=None, image_path=None):
        if not title or not category or not is_valid_url(url):
            logger.warning("Bluesky投稿の入力値が不正です")
            return False
        success = False
        try:
            self.client.login(self.username, self.password)
            template = load_template()
            post_text = template.format(
                title=title,
                category=category,
                url=url,
                username=username or self.username,
                display_name=display_name or self.username
            )
            embed = None
            if image_path and os.path.isfile(image_path):
                blob = self.upload_image(image_path)
                embed = {
                    "$type": "app.bsky.embed.images",
                    "images": [
                        {
                            "alt": f"{title} / {category}",
                            "image": blob
                        }
                    ]
                }
            self.client.send_post(post_text)
            logger.info("Blueskyへの自動投稿に成功しました")
            success = True
            return True
        except exceptions.AtProtocolError as e:
            logger.error(f"Blueskyエラー: {e}")
            return False
        finally:
            # 履歴をCSVに記録
            self._write_post_history(title, category, url, success)

    def _write_post_history(self, title, category, url, success):
        # logsディレクトリがなければ作成
        os.makedirs("logs", exist_ok=True)
        csv_path = "logs/post_history.csv"
        is_new = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # 新規作成時はヘッダー行を書く
            if is_new:
                writer.writerow(["日時", "タイトル", "カテゴリ", "URL", "成功"])
            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    title,
                    category,
                    url,
                    "○" if success else "×",
                ]
            )
