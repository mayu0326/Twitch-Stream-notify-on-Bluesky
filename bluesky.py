# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from datetime import datetime
from utils import retry_on_exception, is_valid_url, format_datetime_filter # Added format_datetime_filter
import os
import csv
import logging
from atproto import Client, exceptions
from jinja2 import Template # Jinja2 Template import
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

# Default template paths, specific paths are fetched within methods
DEFAULT_ONLINE_TEMPLATE_PATH = "templates/default_template.txt"
DEFAULT_OFFLINE_TEMPLATE_PATH = "templates/offline_template.txt"

def load_template(path=None): 
    template_string = ""
    if path is None: 
        path = DEFAULT_ONLINE_TEMPLATE_PATH
        logger.warning(f"load_templateにパスが指定されませんでした。デフォルトのオンラインテンプレートパス '{path}' を使用します。")

    try:
        with open(path, encoding="utf-8") as f:
            template_string = f.read()
    except FileNotFoundError:
        logger.error(
            f"テンプレートファイルが見つかりません: {path}. フォールバックエラーテンプレートを使用します。"
        )
        template_string = "Error: Template '{{ template_path }}' not found. Please check settings."
    except Exception as e:
        logger.error(f"テンプレート '{path}' の読み込み中に予期せぬエラー: {e}", exc_info=True)
        template_string = "Error: Failed to load template '{{ template_path }}' due to an unexpected error."
    
    # Create Jinja2 Template object
    template_obj = Template(template_string)
    # Attach the custom filter to the template's environment
    template_obj.environment.filters['datetimeformat'] = format_datetime_filter
    return template_obj


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
    def post_stream_online(self, event_context: dict, image_path=None):
        required_keys = ["title", "category_name", "stream_url", "broadcaster_user_login", "broadcaster_user_name"]
        missing_keys = [key for key in required_keys if key not in event_context or event_context[key] is None]
        if missing_keys:
            logger.warning(f"Blueskyオンライン投稿の入力event_contextが不正です。不足キー: {', '.join(missing_keys)}")
            return False
        
        success = False
        template_path = os.getenv("BLUESKY_TEMPLATE_PATH", DEFAULT_ONLINE_TEMPLATE_PATH)
        template_obj = load_template(path=template_path)

        try:
            self.client.login(self.username, self.password) 
            
            # Pass template_path for context in case of error template rendering
            post_text = template_obj.render(**event_context, template_path=template_path) 
            
            embed = None
            if image_path and os.path.isfile(image_path): 
                blob = self.upload_image(image_path) 
                if blob: 
                    embed = {
                        "$type": "app.bsky.embed.images",
                        "images": [
                            { 
                                "alt": f"{event_context.get('title', event_context.get('broadcaster_user_name', 'Stream Image'))[:250]}", 
                                "image": blob
                            }
                        ]
                    }
                else:
                    logger.warning(f"画像 '{image_path}' のアップロードに失敗したため、画像なしで投稿します。")
            elif image_path and not os.path.isfile(image_path): 
                 logger.warning(f"指定された画像ファイルが見つかりません: {image_path}。画像なしで投稿します。")

            self.client.send_post(post_text, embed=embed)
            logger.info(f"Blueskyへの自動投稿に成功しました (stream.online): {event_context.get('stream_url')}")
            audit_logger.info(f"Bluesky投稿成功 (stream.online): URL - {event_context.get('stream_url')}, Title - {event_context.get('title')}")
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
                title=event_context.get("title", "N/A"), 
                category=event_context.get("category_name", event_context.get("game_name", "N/A")), 
                url=event_context.get("stream_url", f"https://twitch.tv/{event_context.get('broadcaster_user_login', '')}"), 
                success=success,
                event_type="online"
            )

    @retry_on_exception(
        max_retries=RETRY_MAX,
        wait_seconds=RETRY_WAIT,
        exceptions=(exceptions.AtProtocolError,)
    )
    def post_stream_offline(self, event_context: dict):
        required_keys = ["broadcaster_user_name", "broadcaster_user_login", "channel_url"]
        missing_keys = [key for key in required_keys if key not in event_context or event_context[key] is None]
        if missing_keys:
            logger.warning(f"Blueskyオフライン投稿の入力event_contextが不正です。不足キー: {', '.join(missing_keys)}")
            return False

        offline_template_path = os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH", DEFAULT_OFFLINE_TEMPLATE_PATH)
        template_obj = load_template(path=offline_template_path) 
        
        success = False
        try:
            self.client.login(self.username, self.password) 
            post_text = template_obj.render(**event_context, template_path=offline_template_path)
            
            self.client.send_post(text=post_text) 
            logger.info(f"Blueskyへの自動投稿成功 (stream.offline): {event_context.get('broadcaster_user_name')}")
            audit_logger.info(f"Bluesky投稿成功 (stream.offline): User - {event_context.get('broadcaster_user_name')}")
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
                title=f"配信終了: {event_context.get('broadcaster_user_name', 'N/A')}", 
                category="Offline", 
                url=event_context.get("channel_url", f"https://twitch.tv/{event_context.get('broadcaster_user_login', '')}"), 
                success=success,
                event_type="offline"
            )

    def _write_post_history(self, title: str, category: str, url: str, success: bool, event_type: str):
        os.makedirs("logs", exist_ok=True) 
        csv_path = "logs/post_history.csv"
        is_new_file = not os.path.exists(csv_path)
        
        try:
            with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                if is_new_file:
                    writer.writerow(["日時", "イベントタイプ", "タイトル", "カテゴリ", "URL", "成功"])
                
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
