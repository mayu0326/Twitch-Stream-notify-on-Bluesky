import os
import time
import types
import pytest

from youtube_monitor import YouTubeMonitor
from niconico_monitor import NiconicoMonitor


@pytest.fixture
def dummy_youtube_monitor(monkeypatch):
    # ダミーAPIレスポンスを返すようにモンキーパッチ
    monitor = YouTubeMonitor(
        api_key="dummy",
        channel_id="dummy",
        poll_interval=0.1,
        on_live=lambda info: setattr(monitor, "live_called", True),
        on_new_video=lambda vid: setattr(monitor, "video_called", True),
    )
    monitor.live_called = False
    monitor.video_called = False

    def fake_check_live(self):
        # 1回だけTrueを返す
        if not hasattr(self, "_called_live"):
            self._called_live = True
            return True
        return False

    def fake_get_latest_video_id(self):
        # 1回だけ動画IDを返す
        if not hasattr(self, "_called_video"):
            self._called_video = True
            return "dummy_video_id"
        return "dummy_video_id"

    monkeypatch.setattr(YouTubeMonitor, "check_live", fake_check_live)
    monkeypatch.setattr(YouTubeMonitor, "get_latest_video_id",
                        fake_get_latest_video_id)
    return monitor


@pytest.fixture
def dummy_niconico_monitor(monkeypatch):
    monitor = NiconicoMonitor(
        user_id="dummy",
        poll_interval=0.1,
        on_new_live=lambda lid: setattr(monitor, "live_called", True),
        on_new_video=lambda vid: setattr(monitor, "video_called", True),
    )
    monitor.live_called = False
    monitor.video_called = False

    def fake_get_latest_live_id(self):
        if not hasattr(self, "_called_live"):
            self._called_live = True
            return "dummy_live_id"
        return "dummy_live_id"

    def fake_get_latest_video_id(self):
        if not hasattr(self, "_called_video"):
            self._called_video = True
            return "dummy_video_id"
        return "dummy_video_id"

    monkeypatch.setattr(NiconicoMonitor, "get_latest_live_id",
                        fake_get_latest_live_id)
    monkeypatch.setattr(
        NiconicoMonitor, "get_latest_video_id", fake_get_latest_video_id)
    return monitor


def test_youtube_monitor_triggers_callbacks(dummy_youtube_monitor):
    dummy_youtube_monitor.start()
    time.sleep(0.3)
    assert dummy_youtube_monitor.live_called
    assert dummy_youtube_monitor.video_called


def test_niconico_monitor_triggers_callbacks(dummy_niconico_monitor):
    dummy_niconico_monitor.start()
    time.sleep(0.3)
    assert dummy_niconico_monitor.live_called
    assert dummy_niconico_monitor.video_called
