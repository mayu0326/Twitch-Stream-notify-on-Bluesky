# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

import pytest
import os
from unittest.mock import patch, MagicMock, mock_open, ANY # Added ANY
from bluesky import BlueskyPoster, load_template 
from atproto import exceptions as atproto_exceptions 
from jinja2 import Template # Added Template
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
    monkeypatch.setenv("BLUESKY_IMAGE_PATH", "images/test_image.png") # Default image path for tests
    # Ensure util_logger (child of AppLogger) can output during tests if needed
    monkeypatch.setenv("LOG_LEVEL", "DEBUG") 


@pytest.fixture
def mock_event_context_online():
    return {
        "broadcaster_user_id": "12345",
        "broadcaster_user_login": "teststreamer",
        "broadcaster_user_name": "TestStreamer",
        "title": "Live Stream Title",
        "category_name": "Gaming Category",
        "game_id": "gid123",
        "game_name": "Gaming Category",
        "language": "en",
        "started_at": "2023-10-27T10:00:00Z",
        "type": "live",
        "is_mature": False,
        "tags": ["tag1", "tag2"],
        "stream_url": "https://twitch.tv/teststreamer"
    }

@pytest.fixture
def mock_event_context_offline():
    return {
        "broadcaster_user_id": "12345",
        "broadcaster_user_login": "teststreamer",
        "broadcaster_user_name": "TestStreamer",
        "channel_url": "https://twitch.tv/teststreamer"
    }


class TestBlueskyPoster:

    def test_post_stream_online_invalid_event_context(self, mock_env):
        poster = BlueskyPoster("user", "pass")
        invalid_context = {"broadcaster_user_name": "Test"} # Missing many required keys
        assert not poster.post_stream_online(invalid_context)

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    @patch("bluesky.BlueskyPoster.upload_image") # Changed from os.path.isfile
    def test_post_stream_online_success_with_image(
        self, mock_upload_image, mock_load_template_func, mock_write_history, mock_atproto_client_class, # mock_isfile removed, mock_upload_image added
        mock_env, mock_event_context_online
    ):
        # Mock for Jinja2 Template object returned by load_template
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Online Template Text"
        mock_load_template_func.return_value = mock_template_obj

        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        dummy_blob = MagicMock()
        # mock_client_instance.upload_blob.return_value = dummy_blob # No longer needed here
        mock_upload_image.return_value = dummy_blob # upload_image will return the dummy_blob

        poster = BlueskyPoster("user", "pass")
        # We still need to mock os.path.isfile for the condition before upload_image is called
        with patch("os.path.isfile", return_value=True) as mock_isfile_inner:
            result = poster.post_stream_online(
                event_context=mock_event_context_online,
                image_path="images/test_image.png"
            )
            mock_isfile_inner.assert_called_once_with("images/test_image.png")


        assert result is True
        mock_client_instance.login.assert_called_once_with("user", "pass")
        
        # Assert load_template was called with the correct path
        expected_template_path = os.getenv("BLUESKY_TEMPLATE_PATH")
        mock_load_template_func.assert_called_once_with(path=expected_template_path)
        
        # Assert template.render was called with the event_context
        mock_template_obj.render.assert_called_once_with(**mock_event_context_online, template_path=expected_template_path)

        # Assert that our mock_upload_image was called
        mock_upload_image.assert_called_once_with("images/test_image.png")
        
        mock_client_instance.send_post.assert_called_once()
        call_args = mock_client_instance.send_post.call_args
        assert call_args[0][0] == "Rendered Online Template Text" # Check text arg
        
        embed_arg = call_args[1].get('embed')
        assert embed_arg is not None
        assert embed_arg["images"][0]["image"] == dummy_blob
        
        mock_write_history.assert_called_once_with(
            title=mock_event_context_online["title"], 
            category=mock_event_context_online["category_name"], 
            url=mock_event_context_online["stream_url"], 
            success=True, 
            event_type="online"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    def test_post_stream_online_success_no_image(
        self, mock_load_template_func, mock_write_history, mock_atproto_client_class, 
        mock_env, mock_event_context_online
    ):
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Online No Image"
        mock_load_template_func.return_value = mock_template_obj
        
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("user", "pass")
        result = poster.post_stream_online(
            event_context=mock_event_context_online, image_path=None
        )
        assert result is True
        mock_template_obj.render.assert_called_once_with(**mock_event_context_online, template_path=os.getenv("BLUESKY_TEMPLATE_PATH"))
        mock_client_instance.send_post.assert_called_once_with("Rendered Online No Image", embed=None)
        mock_client_instance.upload_blob.assert_not_called()
        mock_write_history.assert_called_once()


    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    def test_post_stream_offline_success(
        self, mock_load_template_func, mock_write_history, mock_atproto_client_class, 
        mock_env, mock_event_context_offline
    ):
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Offline Template Text"
        mock_load_template_func.return_value = mock_template_obj
        
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(event_context=mock_event_context_offline)

        assert result is True
        mock_client_instance.login.assert_called_once_with("test_user", "test_pass")
        
        expected_template_path = os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH")
        mock_load_template_func.assert_called_once_with(path=expected_template_path)
        mock_template_obj.render.assert_called_once_with(**mock_event_context_offline, template_path=expected_template_path)
        
        mock_client_instance.send_post.assert_called_once_with(text="Rendered Offline Template Text")
        
        mock_write_history.assert_called_once_with(
            title=f"配信終了: {mock_event_context_offline['broadcaster_user_name']}", 
            category="Offline", 
            url=mock_event_context_offline['channel_url'], 
            success=True, 
            event_type="offline"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    def test_post_stream_offline_template_render_error_uses_fallback_text(
        self, mock_load_template_func, mock_write_history, mock_atproto_client_class, 
        mock_env, mock_event_context_offline, caplog # caplog to check logged errors
    ):
        # Simulate load_template returning the error template string, which then gets rendered
        # The error template string is: "Error: Template '{{ template_path }}' not found. Please check settings."
        error_template_content = "Error: Template '{{ template_path }}' not found. Please check settings."
        # The load_template function itself returns a Template object.
        # The Template object is then rendered.
        # So, we mock the Template object that load_template returns.
        mock_error_template_obj = Template(error_template_content) 
        # Attach the filter like the real load_template does, so render doesn't fail on filter not found
        mock_error_template_obj.environment.filters['datetimeformat'] = MagicMock(return_value="FILTERED_DATE")


        mock_load_template_func.return_value = mock_error_template_obj
        
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(event_context=mock_event_context_offline)

        assert result is True # Post should still succeed with the error message as content
        
        expected_template_path = os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH")
        # The error message itself is rendered, with template_path passed to it
        expected_rendered_error_text = f"Error: Template '{expected_template_path}' not found. Please check settings."
        mock_client_instance.send_post.assert_called_once_with(text=expected_rendered_error_text)
        
        # Check that an error was logged by load_template (if it was called with a non-existent path)
        # This part is tricky because load_template is mocked.
        # If we want to test the fallback within load_template, we need a different approach.
        # The current test tests that if load_template *returns* an error template, it's rendered.
        # To test load_template's own fallback, we'd unpatch it and mock `open` to raise FileNotFoundError.

    # Test for load_template's behavior when a file is not found
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_template_file_not_found_returns_error_template(self, mock_open_func, caplog, mock_env):
        # This test directly tests load_template's error handling
        non_existent_path = "path/to/nothing.txt"
        template_obj = load_template(path=non_existent_path)
        
        assert f"テンプレートファイルが見つかりません: {non_existent_path}" in caplog.text
        assert isinstance(template_obj, Template)
        # Render the error template to check its content
        rendered_error = template_obj.render(template_path=non_existent_path)
        assert f"Error: Template '{non_existent_path}' not found." in rendered_error

    # Test for load_template's behavior when a file is empty or other error
    @patch("builtins.open", side_effect=Exception("Some other read error"))
    def test_load_template_other_error_returns_error_template(self, mock_open_func, caplog, mock_env):
        error_path = "path/to/problem.txt"
        template_obj = load_template(path=error_path)
        
        assert f"テンプレート '{error_path}' の読み込み中に予期せぬエラー" in caplog.text
        assert isinstance(template_obj, Template)
        rendered_error = template_obj.render(template_path=error_path)
        assert f"Error: Failed to load template '{error_path}' due to an unexpected error." in rendered_error


    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    def test_post_stream_offline_atproto_error(
        self, mock_write_history, mock_atproto_client_class, mock_env, mock_event_context_offline
    ):
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance
        mock_client_instance.send_post.side_effect = atproto_exceptions.AtProtocolError("Test ATProto Error")

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(event_context=mock_event_context_offline)
        assert result is False 
        mock_write_history.assert_called_once_with(
            title=ANY, category="Offline", url=ANY, success=False, event_type="offline"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("os.path.isfile")
    @patch("bluesky.load_template") # Mock load_template as it's not focus here
    def test_upload_image_file_not_found_in_online_post(
        self, mock_load_template_func, mock_isfile, mock_write_history, mock_atproto_client_class, 
        mock_env, mock_event_context_online, caplog
    ):
        mock_isfile.return_value = False # Image file does NOT exist
        
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Online Text"
        mock_load_template_func.return_value = mock_template_obj
        
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("user", "pass")
        result = poster.post_stream_online(
            event_context=mock_event_context_online,
            image_path="non_existent_image.png" 
        )
        
        assert result is True # Post should still succeed without image
        assert "指定された画像ファイルが見つかりません: non_existent_image.png" in caplog.text
        mock_client_instance.upload_blob.assert_not_called() 
        call_args = mock_client_instance.send_post.call_args
        assert call_args[1].get('embed') is None
        mock_write_history.assert_called_once()

    @patch("bluesky.Client")
    # We are testing the internals of _write_post_history, so we don't mock it directly here.
    # Instead, we mock what it uses (like builtins.open) or what leads to it.
    @patch("bluesky.load_template") # Mock load_template to prevent file access there
    def test_write_post_history_io_error(
        self, mock_load_template_func, mock_atproto_client_class, mock_env, caplog,
        mock_event_context_offline
    ):
        # Setup mock for load_template to return a functional Template object
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Offline Template Text"
        mock_load_template_func.return_value = mock_template_obj

        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance
        # Make send_post succeed so it tries to write history
        mock_client_instance.send_post.return_value = None

        poster = BlueskyPoster("user", "pass")

        # Custom mock for builtins.open to control when IOError is raised
        original_open = open
        def conditional_mock_open(file, mode="r", **kwargs):
            if file == "logs/post_history.csv" and mode == "a":
                raise IOError("Test CSV write error")
            # For any other file call, use a generic mock_open like behavior or fall back to original if specific paths are known
            # For this test, we only expect the CSV to be opened by the tested code path after load_template is mocked.
            # If other files were opened by the function under test (not by load_template), 
            # more sophisticated handling might be needed. Here, we'll use a pass-through mock for non-CSV files.
            return mock_open()(file, mode, **kwargs)


        # We patch _write_post_history directly to ensure it's called,
        # but the actual test of IOError is by patching `open` which it uses.
        # This is a bit of a mix, let's refine.
        # The goal is to have post_stream_offline call the *real* _write_post_history,
        # and _write_post_history fails due to our mocked `open`.

        with patch("builtins.open", side_effect=conditional_mock_open) as mock_file_open_custom:
            # Call a method that triggers _write_post_history
            # post_stream_offline will call load_template (mocked), then send_post (mocked to succeed),
            # then in `finally` it calls the *real* _write_post_history.
            # The real _write_post_history will then try to open "logs/post_history.csv",
            # which our conditional_mock_open will intercept and raise IOError for.
            poster.post_stream_offline(mock_event_context_offline)

        # Assert that load_template was called (ensuring it was bypassed for file open)
        offline_template_path = os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH", "templates/offline_template.txt") # Default from bluesky.py
        mock_load_template_func.assert_called_once_with(path=offline_template_path)

        # Check the log for the specific error from _write_post_history
        assert "投稿履歴CSVへの書き込みに失敗しました: logs/post_history.csv, エラー: Test CSV write error" in caplog.text
        # Optionally, ensure the "Test CSV write error" is part of the logged message.
        assert "Test CSV write error" in caplog.text
        
        # Ensure that send_post was called, meaning the main logic of post_stream_offline executed
        mock_client_instance.send_post.assert_called_once()


    def test_upload_image_actual_file_not_found(self, mock_env, caplog):
        # This tests upload_image directly for FileNotFoundError
        poster = BlueskyPoster("user", "pass")
        # No need to mock Client for this specific error, as open() fails first
        result_blob = poster.upload_image("path/to/truly_missing_image.png")
        assert result_blob is None
        assert "Bluesky画像アップロードエラー: ファイルが見つかりません - path/to/truly_missing_image.png" in caplog.text
