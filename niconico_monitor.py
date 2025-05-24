import time
import feedparser
from threading import Thread


class NiconicoMonitor(Thread):
    """
    ニコニコ生放送およびニコニコ動画の新着を監視するスレッド。
    """

    def __init__(self, user_id, poll_interval, on_new_live, on_new_video):
        super().__init__(daemon=True)
        self.user_id = user_id
        self.poll_interval = poll_interval
        self.on_new_live = on_new_live
        self.on_new_video = on_new_video
        self.last_live_id = None
        self.last_video_id = None

    def run(self):
        while True:
            try:
                # 生放送RSS
                live_id = self.get_latest_live_id()
                if live_id and live_id != self.last_live_id:
                    self.on_new_live(live_id)
                    self.last_live_id = live_id

                # 動画RSS
                video_id = self.get_latest_video_id()
                if video_id and video_id != self.last_video_id:
                    self.on_new_video(video_id)
                    self.last_video_id = video_id

            except Exception as e:
                print(f"[NiconicoMonitor] Error: {e}")
            time.sleep(self.poll_interval)

    def get_latest_live_id(self):
        """
        ユーザーの最新生放送IDを取得。
        """
        url = f"https://live.nicovideo.jp/feeds/user/{self.user_id}"
        feed = feedparser.parse(url)
        if feed.entries:
            return feed.entries[0].id
        return None

    def get_latest_video_id(self):
        """
        ユーザーの最新動画IDを取得。
        """
        url = f"https://www.nicovideo.jp/user/{self.user_id}/video?rss=2.0"
        feed = feedparser.parse(url)
        if feed.entries:
            return feed.entries[0].id
        return None
