# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

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

import time
import feedparser
from threading import Thread, Event
from version_info import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__


class NiconicoMonitor(Thread):
    """
    ニコニコ生放送およびニコニコ動画の新着を監視するスレッド。
    """

    def __init__(self, user_id, poll_interval, on_new_live, on_new_video, shutdown_event=None):
        # 監視対象ユーザーID、ポーリング間隔、コールバック関数を初期化
        super().__init__(daemon=True)
        self.user_id = user_id
        self.poll_interval = poll_interval
        self.on_new_live = on_new_live
        self.on_new_video = on_new_video
        self.last_live_id = None
        self.last_video_id = None
        self.shutdown_event = shutdown_event if shutdown_event is not None else Event()

    def run(self):
        # スレッドのメインループ。shutdown_eventがセットされたら安全に終了
        while not self.shutdown_event.is_set():
            try:
                # 生放送RSSから最新IDを取得し、前回と異なればコールバック実行
                live_id = self.get_latest_live_id()
                if live_id and live_id != self.last_live_id:
                    self.on_new_live(live_id)
                    self.last_live_id = live_id

                # 動画RSSから最新IDを取得し、前回と異なればコールバック実行
                video_id = self.get_latest_video_id()
                if video_id and video_id != self.last_video_id:
                    self.on_new_video(video_id)
                    self.last_video_id = video_id

            except Exception as e:
                print(f"[NiconicoMonitor] エラー発生: {e}")
            self.shutdown_event.wait(self.poll_interval)

    def get_latest_live_id(self):
        """
        ユーザーの最新生放送IDを取得。
        """
        url = f"https://live.nicovideo.jp/feeds/user/{self.user_id}"
        feed = feedparser.parse(url)
        if feed.entries:
            return feed.entries[0].id  # 最新の生放送IDを返す
        return None

    def get_latest_video_id(self):
        """
        ユーザーの最新動画IDを取得。
        """
        url = f"https://www.nicovideo.jp/user/{self.user_id}/video?rss=2.0"
        feed = feedparser.parse(url)
        if feed.entries:
            return feed.entries[0].id  # 最新の動画IDを返す
        return None
