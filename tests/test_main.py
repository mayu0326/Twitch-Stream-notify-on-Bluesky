# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from main import app
import os
import pytest
from unittest.mock import patch, MagicMock
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

# Set default environment variables for tests
# These can be overridden in specific test functions using monkeypatch
@pytest.fixture(autouse=True)
def default_env_vars(monkeypatch):
    monkeypatch.setenv("BLUESKY_USERNAME", "test_bsky_user")
    monkeypatch.setenv("BLUESKY_PASSWORD", "test_bsky_pass")
    monkeypatch.setenv("TWITCH_CLIENT_ID", "test_twitch_id")
    monkeypatch.setenv("TWITCH_CLIENT_SECRET", "test_twitch_secret")
    monkeypatch.setenv("TWITCH_BROADCASTER_ID", "12345678") # Numeric ID
    monkeypatch.setenv("WEBHOOK_CALLBACK_URL", "https://example.com/webhook")
    monkeypatch.setenv("WEBHOOK_SECRET", "testsecret1234567890testsecret1234567890")
    monkeypatch.setenv("NOTIFY_ON_ONLINE", "True")
    monkeypatch.setenv("NOTIFY_ON_OFFLINE", "True")
    # Ensure critical logging config vars are set if not already
    monkeypatch.setenv("LOG_LEVEL", os.getenv("LOG_LEVEL", "DEBUG"))
    monkeypatch.setenv("LOG_RETENTION_DAYS", os.getenv("LOG_RETENTION_DAYS", "1"))


@pytest.fixture
def client():
    # Configure Flask app for testing
    app.config["TESTING"] = True
    # Suppress INFO logs from Flask app itself during tests for cleaner output,
    # unless specifically testing logging. Our app logger will still work.
    # app.logger.setLevel(logging.WARNING) 
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def mock_eventsub_utils(monkeypatch):
    # Mock external calls in eventsub that are not the focus of main.py tests
    monkeypatch.setattr("eventsub.setup_broadcaster_id", lambda logger=None: None)
    # If main.py directly calls other eventsub functions at startup that need mocking:
    # monkeypatch.setattr("eventsub.get_valid_app_access_token", MagicMock(return_value="dummy_token"))
    # monkeypatch.setattr("eventsub.cleanup_eventsub_subscriptions", MagicMock())
    # monkeypatch.setattr("eventsub.create_eventsub_subscription", MagicMock(return_value={"data": [{"id": "123"}]}))
    pass

# setup_broadcaster_idやget_broadcaster_idをモック

@pytest.fixture(autouse=True)
def mock_broadcaster_id(monkeypatch):
    # eventsub.get_broadcaster_idを常に"dummy_id"を返すようにモック
    monkeypatch.setattr("eventsub.setup_broadcaster_id", lambda: None)

class TestWebhookHandler:
    COMMON_HEADERS = {
        "Twitch-Eventsub-Message-Id": "dummy-id",
        "Twitch-Eventsub-Message-Timestamp": "2023-01-01T12:00:00.123456789Z",
        "Twitch-Eventsub-Message-Signature": "sha256=dummyvalidsignature", # Will be mocked by verify_signature
        "Twitch-Eventsub-Message-Type": "notification",
    }
    
    STREAM_ONLINE_PAYLOAD = {
        "subscription": {
            "id": "f1c2a387-161a-49f9-a165-0f21d7a4e1c4",
            "type": "stream.online",
            "version": "1",
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

    STREAM_OFFLINE_PAYLOAD = {
        "subscription": {
            "id": "f1c2a387-161a-49f9-a165-0f21d7a4e1c5", # Different ID
            "type": "stream.offline",
            "version": "1",
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
        response = client.get("/webhook")
        assert response.status_code == 200
        assert b"Webhook endpoint is working!" in response.data

    def test_webhook_invalid_signature(self, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: False)
        response = client.post("/webhook", headers=self.COMMON_HEADERS, json=self.STREAM_ONLINE_PAYLOAD)
        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data == {"status": "signature mismatch"}

    def test_webhook_invalid_json(self, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        response = client.post("/webhook", headers=self.COMMON_HEADERS, data="not a valid json", content_type="application/json")
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data == {"error": "Invalid JSON"}
        
    def test_webhook_empty_json_body(self, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        response = client.post("/webhook", headers=self.COMMON_HEADERS, data="{}", content_type="application/json")
        # Empty JSON is valid JSON, but might be missing required fields for specific types
        # The current test_webhook_missing_fields for stream.online covers this more specifically
        # For a generic empty body, it depends on how early broadcaster_user_login is checked.
        # Current code checks broadcaster_user_login after message_type == "notification"
        # So an empty event {} would fail there.
        json_data = response.get_json()
        assert response.status_code == 400 # Expecting 400 due to missing event.broadcaster_user_login
        assert "Missing required field: event.broadcaster_user_login" in json_data.get("error", "")


    def test_webhook_verification_challenge(self, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        challenge_payload = {
            "challenge": "test_challenge_string",
            "subscription": {"type": "stream.online"} # Type is useful for logging
        }
        headers = {**self.COMMON_HEADERS, "Twitch-Eventsub-Message-Type": "webhook_callback_verification"}
        response = client.post("/webhook", headers=headers, json=challenge_payload)
        assert response.status_code == 200
        assert response.data.decode() == "test_challenge_string"
        assert response.content_type == "text/plain"

    # === Stream.Online Tests ===
    @patch("main.BlueskyPoster")
    def test_webhook_stream_online_success(self, mock_bluesky_poster_class, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_ONLINE", "True")
        
        mock_poster_instance = MagicMock()
        mock_poster_instance.post_stream_online.return_value = True
        mock_bluesky_poster_class.return_value = mock_poster_instance

        response = client.post("/webhook", headers=self.COMMON_HEADERS, json=self.STREAM_ONLINE_PAYLOAD)
        
        assert response.status_code == 200
        assert response.get_json() == {"status": "success"}
        mock_bluesky_poster_class.assert_called_once_with(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))
        event = self.STREAM_ONLINE_PAYLOAD["event"]
        mock_poster_instance.post_stream_online.assert_called_once_with(
            event["title"],
            event["category_name"],
            f"https://twitch.tv/{event['broadcaster_user_login']}",
            username=event["broadcaster_user_login"],
            display_name=event["broadcaster_user_name"],
            image_path=os.getenv("BLUESKY_IMAGE_PATH")
        )

    @patch("main.BlueskyPoster")
    def test_webhook_stream_online_skipped_by_setting(self, mock_bluesky_poster_class, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_ONLINE", "False")
        
        mock_poster_instance = MagicMock()
        mock_bluesky_poster_class.return_value = mock_poster_instance

        response = client.post("/webhook", headers=self.COMMON_HEADERS, json=self.STREAM_ONLINE_PAYLOAD)
        
        assert response.status_code == 200
        assert response.get_json() == {"status": "skipped, online notifications disabled"}
        mock_poster_instance.post_stream_online.assert_not_called()

    def test_webhook_stream_online_missing_fields(self, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_ONLINE", "True")
        
        # Missing "title"
        payload_missing_title = {
            "subscription": self.STREAM_ONLINE_PAYLOAD["subscription"],
            "event": {k: v for k, v in self.STREAM_ONLINE_PAYLOAD["event"].items() if k != "title"}
        }
        response = client.post("/webhook", headers=self.COMMON_HEADERS, json=payload_missing_title)
        assert response.status_code == 400
        json_data = response.get_json()
        assert "Missing required field(s) for stream.online" in json_data.get("error", "")
        assert "event.title" in json_data.get("error", "")


    # === Stream.Offline Tests ===
    @patch("main.BlueskyPoster")
    def test_webhook_stream_offline_success(self, mock_bluesky_poster_class, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_OFFLINE", "True")
        
        mock_poster_instance = MagicMock()
        mock_poster_instance.post_stream_offline.return_value = True
        mock_bluesky_poster_class.return_value = mock_poster_instance

        headers = {**self.COMMON_HEADERS, "Twitch-Eventsub-Message-Type": "notification"}
        response = client.post("/webhook", headers=headers, json=self.STREAM_OFFLINE_PAYLOAD)
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data == {"status": "success, offline notification posted"}
        mock_bluesky_poster_class.assert_called_once_with(os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_PASSWORD"))
        event = self.STREAM_OFFLINE_PAYLOAD["event"]
        mock_poster_instance.post_stream_offline.assert_called_once_with(
            broadcaster_display_name=event["broadcaster_user_name"],
            broadcaster_username=event["broadcaster_user_login"]
        )

    @patch("main.BlueskyPoster")
    def test_webhook_stream_offline_skipped_by_setting(self, mock_bluesky_poster_class, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_OFFLINE", "False")
        
        mock_poster_instance = MagicMock()
        mock_bluesky_poster_class.return_value = mock_poster_instance

        headers = {**self.COMMON_HEADERS, "Twitch-Eventsub-Message-Type": "notification"}
        response = client.post("/webhook", headers=headers, json=self.STREAM_OFFLINE_PAYLOAD)
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data == {"status": "skipped, offline notifications disabled"}
        mock_poster_instance.post_stream_offline.assert_not_called()

    def test_webhook_stream_offline_missing_broadcaster_login(self, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        monkeypatch.setenv("NOTIFY_ON_OFFLINE", "True")
        
        payload_missing_login = {
            "subscription": self.STREAM_OFFLINE_PAYLOAD["subscription"],
            "event": {"broadcaster_user_name": "TestStreamer"} # broadcaster_user_login is missing
        }
        headers = {**self.COMMON_HEADERS, "Twitch-Eventsub-Message-Type": "notification"}
        response = client.post("/webhook", headers=headers, json=payload_missing_login)
        assert response.status_code == 400 # broadcaster_user_login is checked early
        json_data = response.get_json()
        assert "Missing required field: event.broadcaster_user_login" in json_data.get("error", "")


    def test_webhook_revocation(self, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        revocation_payload = {
            "subscription": {
                "id": "f1c2a387-161a-49f9-a165-0f21d7a4e1c4",
                "type": "stream.online", # or any type
                "version": "1",
                "status": "authorization_revoked", # Example status
                "condition": {"broadcaster_user_id": "12345"},
                "transport": {"method": "webhook", "callback": "https://example.com/webhooks/twitch"},
                "created_at": "2019-11-16T10:11:12.123Z",
            }
        }
        headers = {**self.COMMON_HEADERS, "Twitch-Eventsub-Message-Type": "revocation"}
        response = client.post("/webhook", headers=headers, json=revocation_payload)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data == {"status": "revocation notification received"}

    def test_webhook_unhandled_notification_type(self, client, monkeypatch):
        monkeypatch.setattr("main.verify_signature", lambda req: True)
        unknown_type_payload = {
            "subscription": {
                "id": "f1c2a387-161a-49f9-a165-0f21d7a4e1c6",
                "type": "user.update", # An example of an unhandled type
                "version": "1",
                "status": "enabled",
                "condition": {"user_id": "12345"},
                "transport": {"method": "webhook", "callback": "https://example.com/webhooks/twitch"},
                "created_at": "2019-11-16T10:11:14.123Z",
            },
            "event": {"user_id": "12345", "user_login": "testuser", "user_name": "TestUser"}
        }
        headers = {**self.COMMON_HEADERS, "Twitch-Eventsub-Message-Type": "notification"}
        response = client.post("/webhook", headers=headers, json=unknown_type_payload)
        assert response.status_code == 400 # Changed to 400 as per main.py logic for unknown types
        json_data = response.get_json()
        assert json_data == {"status": "error", "message": "Unknown or unhandled subscription type: user.update"}
