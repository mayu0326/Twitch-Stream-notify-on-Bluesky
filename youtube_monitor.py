import time
import requests
from threading import Thread


class YouTubeMonitor(Thread):
    """
    YouTubeライブ配信および動画投稿の新着を監視するスレッド。
    """

    def __init__(self, api_key, channel_id, poll_interval, on_live, on_new_video):
        super().__init__(daemon=True)
        self.api_key = api_key
        self.channel_id = channel_id
        self.poll_interval = poll_interval
        self.on_live = on_live
        self.on_new_video = on_new_video
        self.last_live_status = False
        self.last_video_id = None

    def run(self):
        while True:
            try:
                # ライブ配信の有無を確認
                live = self.check_live()
                if live and not self.last_live_status:
                    self.on_live(live)
                self.last_live_status = live

                # 新着動画の有無を確認
                video_id = self.get_latest_video_id()
                if video_id and video_id != self.last_video_id:
                    self.on_new_video(video_id)
                    self.last_video_id = video_id

            except Exception as e:
                print(f"[YouTubeMonitor] Error: {e}")
            time.sleep(self.poll_interval)

    def check_live(self):
        """
        チャンネルで現在ライブ配信中かどうかを判定。
        """
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={self.channel_id}&eventType=live&type=video&key={self.api_key}"
        )
        resp = requests.get(url)
        data = resp.json()
        return len(data.get("items", [])) > 0

    def get_latest_video_id(self):
        """
        チャンネルの最新動画IDを取得。
        """
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={self.channel_id}&order=date&type=video&key={self.api_key}&maxResults=1"
        )
        resp = requests.get(url)
        data = resp.json()
        items = data.get("items", [])
        if items:
            return items[0]["id"]["videoId"]
        return None
