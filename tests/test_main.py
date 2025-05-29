# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

from main import app
import os
import pytest
from unittest.mock import patch, MagicMock
from app_version import __app_version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __app_version__


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

# テスト用のデフォルト環境変数を設定
# 個別のテスト関数でmonkeypatchにより上書き可能
@pytest.fixture(autouse=True)
def default_env_vars(monkeypatch):
    monkeypatch.setenv("BLUESKY_USERNAME", "test_bsky_user")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "test_bsky_pass")
    monkeypatch.setenv("TWITCH_CLIENT_ID", "test_twitch_id")
    monkeypatch.setenv("TWITCH_CLIENT_SECRET", "test_twitch_secret")
    monkeypatch.setenv("TWITCH_BROADCASTER_ID", "12345678")  # 数値ID
    monkeypatch.setenv("WEBHOOK_CALLBACK_URL", "https://example.com/webhook")
    monkeypatch.setenv(
        "WEBHOOK_SECRET", "testsecret1234567890testsecret1234567890")
    monkeypatch.setenv("NOTIFY_ON_TWITCH_ONINE", "True")
    monkeypatch.setenv("NOTIFY_ON_TWITCH_OFFLINE", "True")
    # 重要なロギング設定値も未設定ならセット
    monkeypatch.setenv("LOG_LEVEL", os.getenv("LOG_LEVEL", "DEBUG"))
    monkeypatch.setenv("LOG_RETENTION_DAYS",
                       os.getenv("LOG_RETENTION_DAYS", "1"))


@pytest.fixture
def client():
    # Flaskアプリをテスト用に設定
    app.config["TESTING"] = True
    # Flask本体のINFOログはテスト時は抑制（必要な場合はコメントアウト）
    # app.logger.setLevel(logging.WARNING)
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def mock_eventsub_utils(monkeypatch):
    # main.pyのテストでeventsubの外部呼び出しをモック
    monkeypatch.setattr("eventsub.setup_broadcaster_id",
                        lambda logger=None: None)
    # 必要に応じて他のeventsub関数もモック可能
    # monkeypatch.setattr("eventsub.get_valid_app_access_token", MagicMock(return_value="dummy_token"))
    # monkeypatch.setattr("eventsub.cleanup_eventsub_subscriptions", MagicMock())
    # monkeypatch.setattr("eventsub.create_eventsub_subscription", MagicMock(return_value={"data": [{"id": "123"}]}))
    pass


class TestWebhookHandler:
    # 共通で使うヘッダー
    COMMON_HEADERS = {
        "Twitch-Eventsub-Message-Id": "dummy-id",
        "Twitch-Eventsub-Message-Timestamp": "2023-01-01T12:00:00.123456789Z",
        # verify_signatureでモックされる
        "Twitch-Eventsub-Message-Signature": "sha256=dummyvalidsignature",
        "Twitch-Eventsub-Message-Type": "notification",
    }

    # 配信開始イベント用のダミーペイロード
    STREAM_ONLINE_PAYLOAD = {
        "subscription": {
            "id": "f1c2a387-161a-49f9-a165-0f21d7a4e1c4",
            "type": "stream.online",
            "app_version": "1",
            "status": "enabled",
            "cost": 1,
            "condition": {"broadcaster_user_id": "12345"},
            "transport": {"method": "webhook", "callback": "https://example.com/webhooks/twitch"},
            "created_at": "2019-11-16T10:11:12.123Z",
        },
        "event": {
            "id": "9001",
            "broadcaster_user_id": "12345",
            "broadcaster_user_login": "teststreamer",
            "broadcaster_user_name": "TestStreamer",
            "type": "live",
            "started_at": "2020-10-11T10:11:12.123Z",
            "title": "Best Stream Ever",
            "category_name": "Science & Technology"
        },
    }

    # 配信終了イベント用のダミーペイロード
    STREAM_OFFLINE_PAYLOAD = {
        "subscription": {
            "id": "f1c2a387-161a-49f9-a165-0f21d7a4e1c5",  # 異なるID
            "type": "stream.offline",
            "app_version": "1",
            "status": "enabled",
            "cost": 1,
            "condition": {"broadcaster_user_id": "12345"},
            "transport": {"method": "webhook", "callback": "https://example.com/webhooks/twitch"},
            "created_at": "2019-11-16T10:11:13.123Z",
        },
        "event": {
            "broadcaster_user_id": "12345",
            "broadcaster_user_login": "teststreamer",
            "broadcaster_user_name": "TestStreamer",
        },
    }

    def test_webhook_get(self, client):
        # GETリクエストでエンドポイントの正常応答を確認
        response = client.get("/webhook")
        assert response.status_code == 200
        assert b"Webhook endpoint is working!" in response.data

    def test_webhook_invalid_signature(self, client, monkeypatch):
        # 署名検証が失敗した場合403を返すことを確認
        monkeypatch.setattr("main.verify_signature", lambda req: False)
        response = client.post(
            "/webhook", headers=self.COMMON_HEADERS, json=self.STREAM_ONLINE_PAYLOAD)
        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data == {"status": "signature mismatch"}

    def test_webhook_invalid_json(self, client, monkeypatch):
        # 不正なJSONの場合400を返すことを確認
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        response = client.post("/webhook", headers=self.COMMON_HEADERS,
                               data="not a valid json", content_type="application/json")
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data == {"error": "Invalid JSON"}

    def test_webhook_empty_json_body(self, client, monkeypatch):
        # 空のJSONボディの場合400を返すことを確認
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        response = client.post("/webhook", headers=self.COMMON_HEADERS,
                               data="{}", content_type="application/json")
        # 空のeventでbroadcaster_user_loginが不足しているため400
        json_data = response.get_json()
        assert response.status_code == 400
        assert "Missing required field: event.broadcaster_user_login" in json_data.get(
            "error", "")

    def test_webhook_verification_challenge(self, client, monkeypatch):
        # webhook_callback_verification時にchallenge文字列を返すことを確認
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        challenge_payload = {
            "challenge": "test_challenge_string",
            "subscription": {"type": "stream.online"}
        }
        headers = {**self.COMMON_HEADERS,
                   "Twitch-Eventsub-Message-Type": "webhook_callback_verification"}
        response = client.post(
            "/webhook", headers=headers, json=challenge_payload)
        assert response.status_code == 200
        assert response.data.decode() == "test_challenge_string"
        assert response.content_type == "text/plain"

    # === stream.online のテスト ===
    @patch("main.BlueskyPoster")
    def test_webhook_stream_online_success(self, mock_bluesky_poster_class, client, monkeypatch):
        # 配信開始イベントでBluesky投稿が成功する場合のテスト
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_TWITCH_ONINE", "True")

        mock_poster_instance = MagicMock()
        mock_poster_instance.post_stream_online.return_value = True
        mock_bluesky_poster_class.return_value = mock_poster_instance

        response = client.post(
            "/webhook", headers=self.COMMON_HEADERS, json=self.STREAM_ONLINE_PAYLOAD)

        assert response.status_code == 200
        assert response.get_json() == {"status": "success"}
        mock_bluesky_poster_class.assert_called_once_with(
            os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD"))

        payload_event_data = self.STREAM_ONLINE_PAYLOAD["event"]

        # main.pyのevent_context生成ロジックを再現
        derived_broadcaster_login = payload_event_data.get(
            "broadcaster_user_login")
        derived_broadcaster_name = payload_event_data.get(
            "broadcaster_user_name", derived_broadcaster_login)

        expected_event_context = {
            "broadcaster_user_id": payload_event_data.get("broadcaster_user_id"),
            "broadcaster_user_login": derived_broadcaster_login,
            "broadcaster_user_name": derived_broadcaster_name,
            "title": payload_event_data.get("title"),
            "category_name": payload_event_data.get("category_name"),
            "game_id": payload_event_data.get("game_id"),
            "game_name": payload_event_data.get(
                "game_name",
                payload_event_data.get("category_name")),
            "language": payload_event_data.get("language"),
            "started_at": payload_event_data.get("started_at"),
            "type": payload_event_data.get("type"),
            "is_mature": payload_event_data.get("is_mature"),
            "tags": payload_event_data.get(
                "tags",
                []),
            "stream_url": f"https://twitch.tv/{derived_broadcaster_login}"}

        mock_poster_instance.post_stream_online.assert_called_once_with(
            event_context=expected_event_context,
            image_path=os.getenv("BLUESKY_IMAGE_PATH")
        )

    @patch("main.BlueskyPoster")
    def test_webhook_stream_online_skipped_by_setting(
            self, mock_bluesky_poster_class, client, monkeypatch):
        # 配信開始通知が設定で無効の場合のテスト
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_TWITCH_ONINE", "False")

        mock_poster_instance = MagicMock()
        mock_bluesky_poster_class.return_value = mock_poster_instance

        response = client.post(
            "/webhook", headers=self.COMMON_HEADERS, json=self.STREAM_ONLINE_PAYLOAD)

        assert response.status_code == 200
        assert response.get_json() == {
            "status": "skipped, online notifications disabled"}
        mock_poster_instance.post_stream_online.assert_not_called()

    def test_webhook_stream_online_missing_fields(self, client, monkeypatch):
        # 必須フィールド(title)が不足している場合のテスト
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_TWITCH_ONINE", "True")

        payload_missing_title = {
            "subscription": self.STREAM_ONLINE_PAYLOAD["subscription"],
            "event": {k: v for k, v in self.STREAM_ONLINE_PAYLOAD["event"].items() if k != "title"}
        }
        response = client.post(
            "/webhook", headers=self.COMMON_HEADERS, json=payload_missing_title)
        assert response.status_code == 400
        json_data = response.get_json()
        assert "Missing title or category_name for stream.online event" in json_data.get(
            "error", "")

    # === stream.offline のテスト ===

    @patch("main.BlueskyPoster")
    def test_webhook_stream_offline_success(self, mock_bluesky_poster_class, client, monkeypatch):
        # 配信終了イベントでBluesky投稿が成功する場合のテスト
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_TWITCH_OFFLINE", "True")

        mock_poster_instance = MagicMock()
        mock_poster_instance.post_stream_offline.return_value = True
        mock_bluesky_poster_class.return_value = mock_poster_instance

        headers = {**self.COMMON_HEADERS,
                   "Twitch-Eventsub-Message-Type": "notification"}
        response = client.post("/webhook", headers=headers,
                               json=self.STREAM_OFFLINE_PAYLOAD)

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data == {"status": "success, offline notification posted"}
        mock_bluesky_poster_class.assert_called_once_with(
            os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD"))

        payload_event_data = self.STREAM_OFFLINE_PAYLOAD["event"]

        # main.pyのevent_context生成ロジックを再現
        derived_broadcaster_login = payload_event_data.get(
            "broadcaster_user_login")
        derived_broadcaster_name = payload_event_data.get(
            "broadcaster_user_name", derived_broadcaster_login)

        expected_event_context = {
            "broadcaster_user_id": payload_event_data.get("broadcaster_user_id"),
            "broadcaster_user_login": derived_broadcaster_login,
            "broadcaster_user_name": derived_broadcaster_name,
            "channel_url": f"https://twitch.tv/{derived_broadcaster_login}"
        }

        mock_poster_instance.post_stream_offline.assert_called_once_with(
            event_context=expected_event_context
        )

    @patch("main.BlueskyPoster")
    def test_webhook_stream_offline_skipped_by_setting(
            self, mock_bluesky_poster_class, client, monkeypatch):
        # 配信終了通知が設定で無効の場合のテスト
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_TWITCH_OFFLINE", "False")

        mock_poster_instance = MagicMock()
        mock_bluesky_poster_class.return_value = mock_poster_instance

        headers = {**self.COMMON_HEADERS,
                   "Twitch-Eventsub-Message-Type": "notification"}
        response = client.post("/webhook", headers=headers,
                               json=self.STREAM_OFFLINE_PAYLOAD)

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data == {
            "status": "skipped, offline notifications disabled"}
        mock_poster_instance.post_stream_offline.assert_not_called()

    def test_webhook_stream_offline_missing_broadcaster_login(self, client, monkeypatch):
        # 配信終了イベントでbroadcaster_user_loginが不足している場合のテスト
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_TWITCH_OFFLINE", "True")

        payload_missing_login = {
            "subscription": self.STREAM_OFFLINE_PAYLOAD["subscription"],
            "event": {"broadcaster_user_name": "TestStreamer"}
        }
        headers = {**self.COMMON_HEADERS,
                   "Twitch-Eventsub-Message-Type": "notification"}
        response = client.post("/webhook", headers=headers,
                               json=payload_missing_login)
        assert response.status_code == 400  # broadcaster_user_loginが不足
        json_data = response.get_json()
        assert "Missing required field: event.broadcaster_user_login" in json_data.get(
            "error", "")

    def test_webhook_revocation(self, client, monkeypatch):
        # サブスクリプション失効通知のテスト
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        revocation_payload = {
            "subscription": {
                "id": "f1c2a387-161a-49f9-a165-0f21d7a4e1c4",
                "type": "stream.online",
                "app_version": "1",
                "status": "authorization_revoked",
                "condition": {
                    "broadcaster_user_id": "12345"},
                "transport": {
                    "method": "webhook",
                    "callback": "https://example.com/webhooks/twitch"},
                "created_at": "2019-11-16T10:11:12.123Z",
            }}
        headers = {**self.COMMON_HEADERS,
                   "Twitch-Eventsub-Message-Type": "revocation"}
        response = client.post(
            "/webhook", headers=headers, json=revocation_payload)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data == {"status": "revocation notification received"}

    def test_webhook_unhandled_notification_type(self, client, monkeypatch):
        # 未対応の通知タイプ(user.updateなど)のテスト
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        unknown_type_payload = {
            "subscription": {
                "id": "f1c2a387-161a-49f9-a165-0f21d7a4e1c6",
                "type": "user.update",
                "app_version": "1",
                "status": "enabled",
                "condition": {
                    "user_id": "12345"},
                "transport": {
                    "method": "webhook",
                    "callback": "https://example.com/webhooks/twitch"},
                "created_at": "2019-11-16T10:11:14.123Z",
            },
            "event": {
                "user_id": "12345",
                "user_login": "testuser",
                "user_name": "TestUser"}}
        headers = {**self.COMMON_HEADERS,
                   "Twitch-Eventsub-Message-Type": "notification"}
        response = client.post("/webhook", headers=headers,
                               json=unknown_type_payload)
        assert response.status_code == 400
        json_data = response.get_json()
        # user.updateイベントはbroadcaster_user_loginがないためエラー
        assert json_data == {
            "error": "Missing required field: event.broadcaster_user_login"}
