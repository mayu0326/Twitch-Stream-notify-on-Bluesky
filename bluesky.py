# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from datetime import datetime
from utils import retry_on_exception, is_valid_url 
import os
import csv
import logging
from atproto import Client, exceptions
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


RETRY_MAX = int(os.getenv("RETRY_MAX", 3))
RETRY_WAIT = int(os.getenv("RETRY_WAIT", 2))


logger = logging.getLogger("AppLogger")

# settings.envでテンプレートパスを指定
TEMPLATE_PATH = os.getenv(
    "BLUESKY_TEMPLATE_PATH",
    "templates/default_template.txt"
)


def load_template(path=None):
    if path is None:
        path = TEMPLATE_PATH
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(
            f"テンプレートファイルが見つかりません: {path}"
        )
        # デフォルトテンプレートを返す
        return "" \
            "🔴 放送を開始しました！\nタイトル: {title}\nカテゴリ: {category}\nURL: {url}"


audit_logger = logging.getLogger("AuditLogger")


class BlueskyPoster:
    def __init__(self, username, password):
        self.client = Client()
        self.username = username
        self.password = password

    def upload_image(self, image_path):
        try:
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
            blob = self.client.upload_blob(img_bytes)
            return blob
        except FileNotFoundError:
            logger.error(f"Bluesky画像アップロードエラー: ファイルが見つかりません - {image_path}")
            return None
        except Exception as e: # Catch other potential errors during file read or blob upload
            logger.error(f"Bluesky画像アップロード中に予期せぬエラーが発生しました: {image_path}, エラー: {e}", exc_info=e)
            return None


    @retry_on_exception(
        max_retries=RETRY_MAX,
        wait_seconds=RETRY_WAIT,
        exceptions=(exceptions.AtProtocolError,) # Only retry for AtProto specific errors
    )
    def post_stream_online(
        self,
        title,
        category,
        url,
        username=None,
        display_name=None,
        image_path=None
    ):
        if not title or not category or not is_valid_url(url): 
            logger.warning("Bluesky投稿の入力値が不正です (タイトル、カテゴリ、またはURLが不足または無効)")
            return False
        
        success = False
        try:
            self.client.login(self.username, self.password) # Login should be part of the retry block if it can fail due to network
            
            template = load_template()
            if not template: # If default template also fails to load (empty string)
                logger.error("Bluesky投稿用テンプレートが読み込めませんでした。投稿を中止します。")
                return False

            post_text = template.format(
                title=title,
                category=category,
                url=url,
                username=username or self.username,
                display_name=display_name or self.username
            )
            
            embed = None
            if image_path and os.path.isfile(image_path): # Check if file exists before attempting to upload
                blob = self.upload_image(image_path) # upload_image now handles its own errors and returns None on failure
                if blob: # Only create embed if blob was successfully uploaded
                    embed = {
                        "$type": "app.bsky.embed.images",
                        "images": [
                            {
                                "alt": f"{title} / {category}", # Keep alt text concise
                                "image": blob
                            }
                        ]
                    }
                else:
                    logger.warning(f"画像 '{image_path}' のアップロードに失敗したため、画像なしで投稿します。")
            elif image_path and not os.path.isfile(image_path): # Log if image_path was provided but file doesn't exist
                 logger.warning(f"指定された画像ファイルが見つかりません: {image_path}。画像なしで投稿します。")


            self.client.send_post(post_text, embed=embed)
            logger.info(f"Blueskyへの自動投稿に成功しました: {url}")
            audit_logger.info(f"Bluesky投稿成功: URL - {url}, Title - {title}")
            success = True
            return True
        except exceptions.AtProtocolError as e:
            # This will be caught by retry_on_exception decorator first.
            # If all retries fail, this log line will be executed by the decorator re-raising the exception.
            logger.error(f"Bluesky APIエラー (リトライ超過後): {e}", exc_info=e) # Add exc_info for stack trace
            return False
        except Exception as e: # Catch any other unexpected errors during the posting process
            logger.error(f"Bluesky投稿中に予期せぬエラーが発生しました: {e}", exc_info=e)
            return False
        finally:
            # 履歴をCSVに記録
            self._write_post_history(title, category, url, success)

    def _write_post_history(self, title, category, url, success):
        # logsディレクトリがなければ作成 (configure_logging should handle this, but good for safety)
        os.makedirs("logs", exist_ok=True) 
        csv_path = "logs/post_history.csv"
        is_new_file = not os.path.exists(csv_path)
        
        try:
            with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                # 新規作成時はヘッダー行を書く
                if is_new_file:
                    writer.writerow(["日時", "タイトル", "カテゴリ", "URL", "成功"])
                
                # Get current time in a consistent format (consider timezone if important)
                # For simplicity, using system's local time as before.
                # If timezone consistency is critical, use utils.py's timezone logic here.
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                writer.writerow(
                    [
                        current_time,
                        title,
                        category,
                        url,
                        "○" if success else "×",
                    ]
                )
        except IOError as e: # Catch file I/O specific errors
            logger.error(f"投稿履歴CSVへの書き込みに失敗しました: {csv_path}, エラー: {e}", exc_info=e)
        except Exception as e: # Catch any other unexpected errors during CSV writing
            logger.error(f"投稿履歴CSVへの書き込み中に予期せぬエラーが発生しました: {csv_path}, エラー: {e}", exc_info=e)
