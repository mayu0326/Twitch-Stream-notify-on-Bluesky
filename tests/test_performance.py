# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky - Performance Tests
"""
import pytest
import time
from unittest.mock import patch, MagicMock
from main import app

# pytestの警告抑制: mark.performance
pytestmark = pytest.mark.filterwarnings(
    r"ignore:Unknown pytest\.mark\.performance",
)


@pytest.mark.performance
def test_webhook_response_time():
    """Webhookエンドポイントのレスポンス時間テスト"""
    with patch('main.verify_signature', return_value=True), \
            patch('bluesky.BlueskyPoster') as mock_bluesky_cls, \
            patch('main.BlueskyPoster') as mock_main_bluesky_cls:
        poster = MagicMock()
        poster.post_stream_online.return_value = True
        mock_bluesky_cls.return_value = poster
        mock_main_bluesky_cls.return_value = poster
        with app.test_client() as client:
            start_time = time.time()
            response = client.post('/webhook',
                                   json={
                                       'subscription': {'type': 'stream.online'},
                                       'event': {
                                           'broadcaster_user_login': 'testuser',
                                           'broadcaster_user_name': 'Test User',
                                           'started_at': '2024-03-20T12:00:00Z',
                                           'title': 'テスト配信',
                                           'category_name': 'ゲーム'
                                       }
                                   },
                                   headers={
                                       "Twitch-Eventsub-Message-Type": "notification",
                                       "Twitch-Eventsub-Message-Id": "dummy-id",
                                       "Twitch-Eventsub-Message-Timestamp": "2024-05-26T13:45:00Z",
                                       "Twitch-Eventsub-Message-Signature": "sha256=dummy"
                                   }
                                   )
            end_time = time.time()
            processing_time = end_time - start_time
            assert response.status_code == 200
            assert processing_time < 1.0  # 1秒以内にレスポンスを返すことを期待


@pytest.mark.performance
def test_concurrent_notifications():
    """同時複数通知のパフォーマンステスト"""
    from concurrent.futures import ThreadPoolExecutor
    import requests

    def send_notification():
        with patch('main.verify_signature', return_value=True), \
                patch('bluesky.BlueskyPoster') as mock_bluesky_cls, \
                patch('main.BlueskyPoster') as mock_main_bluesky_cls:
            poster = MagicMock()
            poster.post_stream_online.return_value = True
            mock_bluesky_cls.return_value = poster
            mock_main_bluesky_cls.return_value = poster
            with app.test_client() as client:
                return client.post('/webhook',
                                   json={
                                       'subscription': {'type': 'stream.online'},
                                       'event': {
                                           'broadcaster_user_login': 'testuser',
                                           'broadcaster_user_name': 'Test User',
                                           'started_at': '2024-03-20T12:00:00Z',
                                           'title': 'テスト配信',
                                           'category_name': 'ゲーム'
                                       }
                                   },
                                   headers={
                                       "Twitch-Eventsub-Message-Type": "notification",
                                       "Twitch-Eventsub-Message-Id": "dummy-id",
                                       "Twitch-Eventsub-Message-Timestamp": "2024-05-26T13:45:00Z",
                                       "Twitch-Eventsub-Message-Signature": "sha256=dummy"
                                   }
                                   )
    with ThreadPoolExecutor(max_workers=10) as executor:
        start_time = time.time()
        futures = [executor.submit(send_notification) for _ in range(10)]
        results = [f.result() for f in futures]
        end_time = time.time()
        assert all(r.status_code == 200 for r in results)
        total_time = end_time - start_time
        assert total_time < 5.0  # 10件の同時処理を5秒以内に完了
