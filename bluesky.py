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
        if path == TEMPLATE_PATH: 
             return "🔴 放送を開始しました！\nタイトル: {title}\nカテゴリ: {category}\nURL: {url}" 
        return "" 



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
        except Exception as e: 
            logger.error(f"Bluesky画像アップロード中に予期せぬエラーが発生しました: {image_path}, エラー: {e}", exc_info=e)
            return None


    @retry_on_exception(
        max_retries=RETRY_MAX,
        wait_seconds=RETRY_WAIT,
        exceptions=(exceptions.AtProtocolError,) 
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

            self.client.login(self.username, self.password) 
            
            template_text = load_template() 
            if not template_text: 
                logger.error("オンライン通知用テンプレートが読み込めませんでした。投稿を中止します。")
                return False

            post_text = template_text.format(
                title=title,
                category=category,
                url=url,
                username=username or self.username, 
                display_name=display_name or self.username 
            )
            
            embed = None

            if image_path and os.path.isfile(image_path): 
                blob = self.upload_image(image_path) 
                if blob: 
                    embed = {
                        "$type": "app.bsky.embed.images",
                        "images": [
                            {
                                "alt": f"{title} / {category}", 
                                "image": blob
                            }
                        ]
                    }
                else:
                    logger.warning(f"画像 '{image_path}' のアップロードに失敗したため、画像なしで投稿します。")

            elif image_path and not os.path.isfile(image_path): 
                 logger.warning(f"指定された画像ファイルが見つかりません: {image_path}。画像なしで投稿します。")

            self.client.send_post(post_text, embed=embed)
            logger.info(f"Blueskyへの自動投稿に成功しました (stream.online): {url}")
            audit_logger.info(f"Bluesky投稿成功 (stream.online): URL - {url}, Title - {title}")
            success = True
            return True
        except exceptions.AtProtocolError as e:
            logger.error(f"Bluesky APIエラー (stream.online投稿): {e}", exc_info=True) 
            return False
        except Exception as e: 
            logger.error(f"Bluesky投稿中 (stream.online)に予期せぬエラーが発生しました: {e}", exc_info=e)
            return False
        finally:
            self._write_post_history(
                title=title, 
                category=category, 
                url=url, 
                success=success,
                event_type="online" # Corrected event_type
            )

    @retry_on_exception(
        max_retries=RETRY_MAX,
        wait_seconds=RETRY_WAIT,
        exceptions=(exceptions.AtProtocolError,)
    )
    def post_stream_offline(self, broadcaster_display_name, broadcaster_username):
        if not broadcaster_display_name or not broadcaster_username: # broadcaster_username is needed for URL
            logger.warning("Blueskyオフライン投稿の入力値が不正です (配信者情報が不足)。")
            return False

        offline_template_path = os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH", "templates/offline_template.txt")
        template_text = load_template(path=offline_template_path) 

        if not template_text: 
            logger.error(f"オフライン通知用テンプレートが読み込めませんでした: {offline_template_path}。デフォルトのメッセージを使用します。")
            template_text = "{display_name}さんの配信が終了しました。" # Fallback

        post_text = template_text.format(
            display_name=broadcaster_display_name,
            username=broadcaster_username 
        )
        
        success = False
        try:
            self.client.login(self.username, self.password) 
            self.client.send_post(text=post_text) 
            logger.info(f"Blueskyへの自動投稿成功 (stream.offline): {broadcaster_display_name}")
            audit_logger.info(f"Bluesky投稿成功 (stream.offline): User - {broadcaster_display_name}")
            success = True
            return True
        except exceptions.AtProtocolError as e:
            logger.error(f"Bluesky APIエラー (stream.offline投稿): {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Bluesky投稿中 (stream.offline)に予期せぬエラーが発生しました: {e}", exc_info=e)
            return False
        finally:
            self._write_post_history(
                title=f"配信終了: {broadcaster_display_name}", 
                category="Offline", 
                url=f"https://twitch.tv/{broadcaster_username}", 
                success=success,
                event_type="offline" # Corrected event_type
            )

    def _write_post_history(self, title: str, category: str, url: str, success: bool, event_type: str):
        os.makedirs("logs", exist_ok=True) 
        csv_path = "logs/post_history.csv"
        is_new_file = not os.path.exists(csv_path)
        
        try:
            with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                if is_new_file:
                    writer.writerow(["日時", "イベントタイプ", "タイトル", "カテゴリ", "URL", "成功"]) # Corrected header
      
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                writer.writerow(
                    [
                        current_time,
                        event_type, 
                        title, 
                        category, 
                        url,
                        "○" if success else "×",
                    ]
                )

        except IOError as e: 
            logger.error(f"投稿履歴CSVへの書き込みに失敗しました: {csv_path}, エラー: {e}", exc_info=e)
        except Exception as e: 
            logger.error(f"投稿履歴CSVへの書き込み中に予期せぬエラーが発生しました: {csv_path}, エラー: {e}", exc_info=e)
