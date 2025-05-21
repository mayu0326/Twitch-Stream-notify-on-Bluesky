# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

import pytest
import os
from unittest.mock import patch, MagicMock, mock_open
from bluesky import BlueskyPoster, load_template # Ensure load_template is imported if testing its behavior directly
from atproto import exceptions as atproto_exceptions # For mocking specific exceptions
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

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("BLUESKY_USERNAME", "test_user")
    monkeypatch.setenv("BLUESKY_PASSWORD", "test_pass")
    monkeypatch.setenv("BLUESKY_TEMPLATE_PATH", "templates/default_template.txt")
    monkeypatch.setenv("BLUESKY_OFFLINE_TEMPLATE_PATH", "templates/offline_template.txt")
    monkeypatch.setenv("BLUESKY_IMAGE_PATH", "images/test_image.png")


class TestBlueskyPoster:

    def test_post_stream_online_invalid_url(self, mock_env): # Added mock_env
        poster = BlueskyPoster("user", "pass")
        # No need to mock client.login or send_post as it should fail before that
        assert not poster.post_stream_online("title", "cat", "ftp://example.com")
        assert not poster.post_stream_online("title", "cat", "") # Empty URL

    @patch("bluesky.Client") # Mocks atproto.Client where BlueskyPoster uses it
    @patch("bluesky.BlueskyPoster._write_post_history") # Mock history writing
    @patch("bluesky.load_template") # Mock template loading
    @patch("os.path.isfile") # Mock os.path.isfile
    def test_post_stream_online_success_with_image(
        self, mock_isfile, mock_load_template, mock_write_history, mock_atproto_client_class, mock_env
    ):
        mock_isfile.return_value = True # Assume image file exists
        mock_load_template.return_value = "Online: {title} in {category} at {url} by {display_name}"
        
        # Configure the mock atproto Client instance
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance
        
        # Mock upload_blob to return a dummy blob object
        dummy_blob = MagicMock()
        dummy_blob.cid = "dummy_cid_string" # Example attribute if your code uses it
        mock_client_instance.upload_blob.return_value = dummy_blob

        poster = BlueskyPoster("user", "pass")
        result = poster.post_stream_online(
            title="Live Stream", 
            category="Gaming", 
            url="https://twitch.tv/teststreamer",
            username="teststreamer",
            display_name="TestStreamer",
            image_path="images/test_image.png"
        )

        assert result is True
        mock_client_instance.login.assert_called_once_with("user", "pass")
        mock_load_template.assert_called_once_with() # Called with no args for online
        
        expected_post_text = "Online: Live Stream in Gaming at https://twitch.tv/teststreamer by TestStreamer"
        # Check that send_post was called, and inspect its 'embed' argument
        call_args = mock_client_instance.send_post.call_args
        assert call_args is not None
        assert call_args[0][0] == expected_post_text # First positional argument (text)
        
        # Check embed structure
        embed_arg = call_args[1].get('embed') # Keyword argument 'embed'
        assert embed_arg is not None
        assert embed_arg["$type"] == "app.bsky.embed.images"
        assert len(embed_arg["images"]) == 1
        assert embed_arg["images"][0]["alt"] == "Live Stream / Gaming"
        assert embed_arg["images"][0]["image"] == dummy_blob
        
        mock_client_instance.upload_blob.assert_called_once() # Ensure image was "uploaded"
        mock_write_history.assert_called_once_with(
            title="Live Stream", category="Gaming", url="https://twitch.tv/teststreamer", success=True, event_type="online"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    def test_post_stream_online_success_no_image(
        self, mock_load_template, mock_write_history, mock_atproto_client_class, mock_env
    ):
        mock_load_template.return_value = "Online: {title} by {display_name}"
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("user", "pass")
        result = poster.post_stream_online(
            title="Live Stream", category="Gaming", url="https://twitch.tv/teststreamer",
            username="teststreamer", display_name="TestStreamer", image_path=None # No image path
        )
        assert result is True
        mock_client_instance.login.assert_called_once_with("user", "pass")
        expected_post_text = "Online: Live Stream by TestStreamer"
        mock_client_instance.send_post.assert_called_once_with(expected_post_text, embed=None)
        mock_client_instance.upload_blob.assert_not_called() # No image, so no upload
        mock_write_history.assert_called_once_with(
            title="Live Stream", category="Gaming", url="https://twitch.tv/teststreamer", success=True, event_type="online"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template") # Mock template loading
    def test_post_stream_offline_success(
        self, mock_load_template, mock_write_history, mock_atproto_client_class, mock_env
    ):
        mock_load_template.return_value = "Offline: {display_name} ({username}) is now offline."
        
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(
            broadcaster_display_name="TestStreamer",
            broadcaster_username="teststreamer"
        )

        assert result is True
        mock_client_instance.login.assert_called_once_with("test_user", "test_pass")
        mock_load_template.assert_called_once_with(path=os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH"))
        
        expected_post_text = "Offline: TestStreamer (teststreamer) is now offline."
        mock_client_instance.send_post.assert_called_once_with(text=expected_post_text) # Ensure text kwarg is used
        
        mock_write_history.assert_called_once_with(
            title="配信終了: TestStreamer", 
            category="Offline", 
            url="https://twitch.tv/teststreamer", 
            success=True, 
            event_type="offline"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    def test_post_stream_offline_missing_template_uses_fallback(
        self, mock_load_template, mock_write_history, mock_atproto_client_class, mock_env
    ):
        # Simulate load_template returning empty string for the specified offline template path
        # and then the internal fallback in post_stream_offline being used.
        def custom_load_template(path=None):
            if path == os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH"):
                return "" # Simulate file not found / empty
            return "This should not be called for offline" 
        mock_load_template.side_effect = custom_load_template
        
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(
            broadcaster_display_name="TestStreamer",
            broadcaster_username="teststreamer"
        )

        assert result is True
        mock_client_instance.login.assert_called_once_with("test_user", "test_pass")
        
        # Check that the fallback message hardcoded in post_stream_offline is used
        expected_post_text = "TestStreamerさんの配信が終了しました。" 
        mock_client_instance.send_post.assert_called_once_with(text=expected_post_text)
        
        mock_write_history.assert_called_once_with(
            title="配信終了: TestStreamer", 
            category="Offline", 
            url="https://twitch.tv/teststreamer", 
            success=True, 
            event_type="offline"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    def test_post_stream_offline_atproto_error(
        self, mock_write_history, mock_atproto_client_class, mock_env
    ):
        # No need to mock load_template if the error happens before/during send_post
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance
        # Simulate an AtProtocolError during send_post
        mock_client_instance.send_post.side_effect = atproto_exceptions.AtProtocolError("Test ATProto Error")

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(
            broadcaster_display_name="TestStreamer",
            broadcaster_username="teststreamer"
        )
        assert result is False # Should return False on error
        mock_client_instance.login.assert_called_once() # Login attempt
        mock_client_instance.send_post.assert_called_once() # send_post attempt
        mock_write_history.assert_called_once_with(
            title="配信終了: TestStreamer", 
            category="Offline", 
            url="https://twitch.tv/teststreamer", 
            success=False, # Ensure success is False
            event_type="offline"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    @patch("os.path.isfile")
    def test_upload_image_file_not_found(
        self, mock_isfile, mock_load_template, mock_write_history, mock_atproto_client_class, mock_env
    ):
        mock_isfile.return_value = False # Simulate image file DOES NOT exist
        mock_load_template.return_value = "Online: {title}" # Irrelevant for this specific test focus
        
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("user", "pass")
        # Call post_stream_online, which internally calls upload_image
        result = poster.post_stream_online(
            title="Live Stream", category="Gaming", url="https://twitch.tv/teststreamer",
            image_path="non_existent_image.png" 
        )
        
        assert result is True # Post should still succeed without image
        mock_client_instance.upload_blob.assert_not_called() # upload_blob should not be called
        # send_post should be called without embed
        call_args = mock_client_instance.send_post.call_args
        assert call_args[1].get('embed') is None
        mock_write_history.assert_called_once() # History should still be written

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    def test_write_post_history_io_error(
        self, mock_write_history_method_itself, mock_atproto_client_class, mock_env, caplog
    ):
        # We want to test the _write_post_history method's own error handling,
        # so we patch open within its scope or cause an IOError.
        # For simplicity, let's mock open to raise IOError.
        
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance
        
        poster = BlueskyPoster("user", "pass")
        
        # This time, we are not mocking _write_post_history itself, but the `open` call within it.
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Test CSV write error")
            
            # Call a method that triggers _write_post_history
            # post_stream_offline is simpler for this purpose
            poster.post_stream_offline("TestUser", "testuser") 
            # We don't care about the return value of post_stream_offline here,
            # just that _write_post_history was called and handled the error.

        assert "投稿履歴CSVへの書き込みに失敗しました" in caplog.text
        assert "Test CSV write error" in caplog.text
        # The original mock_write_history_method_itself is not used here as we test the real one.

# Test for load_template standalone if needed, though covered by other tests implicitly.
def test_load_template_file_not_found(monkeypatch, caplog):
    monkeypatch.setenv("BLUESKY_TEMPLATE_PATH", "non_existent_template.txt")
    # Explicitly call with the non-existent path
    template_content = load_template(path="non_existent_template.txt")
    assert "テンプレートファイルが見つかりません: non_existent_template.txt" in caplog.text
    assert template_content == "" # Fallback for general case in load_template

def test_load_template_default_online_fallback(monkeypatch, caplog):
    # Set a non-existent path for the default online template
    monkeypatch.setenv("BLUESKY_TEMPLATE_PATH", "this_default_online_template_is_missing.txt")
    # Call load_template without path argument to trigger default logic
    template_content = load_template() 
    assert "テンプレートファイルが見つかりません: this_default_online_template_is_missing.txt" in caplog.text
    # Check if it returns the specific fallback for online template
    assert "🔴 放送を開始しました！" in template_content
