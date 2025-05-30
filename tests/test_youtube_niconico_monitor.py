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

from niconico_monitor import NiconicoMonitor
from youtube_monitor import YouTubeMonitor
import pytest
import types
import time
from version_info import __version__
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__


@pytest.fixture
def dummy_youtube_monitor(monkeypatch):
    # ダミーAPIレスポンスを返すようにYouTubeMonitorをモンキーパッチ
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

    # モックメソッドをYouTubeMonitorに差し替え
    monkeypatch.setattr(YouTubeMonitor, "check_live", fake_check_live)
    monkeypatch.setattr(YouTubeMonitor, "get_latest_video_id",
                        fake_get_latest_video_id)
    return monitor


@pytest.fixture
def dummy_niconico_monitor(monkeypatch):
    # ダミーAPIレスポンスを返すようにNiconicoMonitorをモンキーパッチ
    monitor = NiconicoMonitor(
        user_id="dummy",
        poll_interval=0.1,
        on_new_live=lambda lid: setattr(monitor, "live_called", True),
        on_new_video=lambda vid: setattr(monitor, "video_called", True),
    )
    monitor.live_called = False
    monitor.video_called = False

    def fake_get_latest_live_id(self):
        # 1回だけ生放送IDを返す
        if not hasattr(self, "_called_live"):
            self._called_live = True
            return "dummy_live_id"
        return "dummy_live_id"

    def fake_get_latest_video_id(self):
        # 1回だけ動画IDを返す
        if not hasattr(self, "_called_video"):
            self._called_video = True
            return "dummy_video_id"
        return "dummy_video_id"

    # モックメソッドをNiconicoMonitorに差し替え
    monkeypatch.setattr(NiconicoMonitor, "get_latest_live_id",
                        fake_get_latest_live_id)
    monkeypatch.setattr(
        NiconicoMonitor, "get_latest_video_id", fake_get_latest_video_id)
    return monitor


def test_youtube_monitor_triggers_callbacks(dummy_youtube_monitor):
    # YouTubeMonitorがコールバックを正しく呼び出すかテスト
    dummy_youtube_monitor.start()
    time.sleep(0.3)
    assert dummy_youtube_monitor.live_called
    assert dummy_youtube_monitor.video_called


def test_niconico_monitor_triggers_callbacks(dummy_niconico_monitor):
    # NiconicoMonitorがコールバックを正しく呼び出すかテスト
    dummy_niconico_monitor.start()
    time.sleep(0.3)
    assert dummy_niconico_monitor.live_called
    assert dummy_niconico_monitor.video_called
