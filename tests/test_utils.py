# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""
import pytest
import os
from unittest.mock import patch, MagicMock # Added patch
from utils import (
    update_env_file_preserve_comments, 
    rotate_secret_if_needed,
    format_datetime_filter # Added format_datetime_filter
)
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


# settings.envのテスト用パス
TEST_ENV_PATH = "test_settings.env"


@pytest.fixture
def env_file():
    # テスト用の settings.env を作成
    with open(TEST_ENV_PATH, "w", encoding='utf-8') as f:
        f.write("# This is a comment\n")
        f.write("KEY1=VALUE1\n")
        f.write("\n")  # Empty line
        f.write("KEY2=VALUE2 # Inline comment\n")
    yield TEST_ENV_PATH
    # テスト後にファイルを削除
    os.remove(TEST_ENV_PATH)


def test_update_env_file_preserve_comments_existing_key(env_file):
    updates = {"KEY1": "NEW_VALUE1"}
    update_env_file_preserve_comments(env_file, updates)
    with open(env_file, "r", encoding='utf-8') as f:
        lines = f.readlines()
    assert lines[0] == "# This is a comment\n"
    assert lines[1] == "KEY1=NEW_VALUE1\n"
    assert lines[2] == "\n"
    assert lines[3] == "KEY2=VALUE2 # Inline comment\n"


def test_update_env_file_preserve_comments_new_key(env_file):
    updates = {"KEY3": "VALUE3"}
    update_env_file_preserve_comments(env_file, updates)
    with open(env_file, "r", encoding='utf-8') as f:
        lines = f.readlines()
    # KEY3が末尾に追加されていることを確認
    assert "KEY3=VALUE3\n" in lines
    # 元の行が保持されていることを確認
    assert "# This is a comment\n" in lines
    assert "KEY1=VALUE1\n" in lines


def test_update_env_file_preserve_comments_multiple_updates(env_file):
    updates = {"KEY1": "UPDATED_K1", "KEY_NEW": "NEW_K_VAL"}
    update_env_file_preserve_comments(env_file, updates)
    with open(env_file, "r", encoding='utf-8') as f:
        content = f.read()
    assert "KEY1=UPDATED_K1\n" in content
    assert "KEY_NEW=NEW_K_VAL\n" in content
    assert "KEY2=VALUE2 # Inline comment\n" in content # Original key2 preserved


@pytest.fixture
def mock_env_for_rotate(monkeypatch, env_file):
    # rotate_secret_if_needed 内の SETTINGS_ENV_PATH をテスト用パスに差し替え
    monkeypatch.setattr("utils.SETTINGS_ENV_PATH", env_file)
    # read_env と update_env_file_preserve_comments はそのままテスト対象の関数を使う
    # generate_secret は固定値を返すようにモック
    monkeypatch.setattr("utils.generate_secret", lambda length=32: "mocked_secret_key_123")
    # os.getenv for TIMEZONE
    monkeypatch.setenv("TIMEZONE", "UTC") # Default to UTC for consistent testing
    return env_file


def test_rotate_secret_if_needed_no_secret(mock_env_for_rotate, caplog):
    # settings.env に SECRET_KEY_NAME がない状態
    with open(mock_env_for_rotate, "w", encoding='utf-8') as f:
        f.write("OTHER_KEY=some_value\n")
    
    new_secret = rotate_secret_if_needed(force=False)
    assert new_secret == "mocked_secret_key_123"
    with open(mock_env_for_rotate, "r", encoding='utf-8') as f:
        content = f.read()
    assert "WEBHOOK_SECRET=mocked_secret_key_123" in content
    assert "SECRET_LAST_ROTATED=" in content # Check if last rotated is also set
    assert "WEBHOOK_SECRETが見つからないため、新規生成します。" in caplog.text


def test_rotate_secret_if_needed_force_rotation(mock_env_for_rotate, caplog):
    with open(mock_env_for_rotate, "w", encoding='utf-8') as f:
        f.write("WEBHOOK_SECRET=old_secret\n")
        f.write("SECRET_LAST_ROTATED=2023-01-01T00:00:00+00:00\n") # Dummy old date
    
    new_secret = rotate_secret_if_needed(force=True) # Force rotation
    assert new_secret == "mocked_secret_key_123"
    with open(mock_env_for_rotate, "r", encoding='utf-8') as f:
        content = f.read()
    assert "WEBHOOK_SECRET=mocked_secret_key_123" in content
    assert "WEBHOOK_SECRETを自動生成・ローテーションしました" in caplog.text


class TestFormatDateTimeFilter:
    def test_basic_formatting_default_utc(self, monkeypatch):
        monkeypatch.setenv("TIMEZONE", "UTC")
        iso_str = "2023-10-27T10:00:00Z"
        # Default format is "%Y-%m-%d %H:%M %Z"
        # Since TIMEZONE is UTC, %Z should be UTC (or empty depending on platform's strftime for UTC)
        # Python's %Z for naive UTC datetime or UTC tzinfo object usually returns empty string or "UTC".
        # Let's check for the main part.
        formatted_str = format_datetime_filter(iso_str)
        assert "2023-10-27 10:00" in formatted_str 
        # For UTC, %Z can be "UTC" or sometimes empty. If it's there, it should be UTC.
        if "UTC" in formatted_str:
            assert formatted_str.endswith("UTC")
        elif formatted_str.strip().endswith("0000"): # some strftime might produce +0000
             assert "2023-10-27 10:00:00 UTC" or "2023-10-27 10:00:00 +0000"

    def test_custom_formatting(self, monkeypatch):
        monkeypatch.setenv("TIMEZONE", "UTC") # Keep it simple for format testing
        iso_str = "2023-10-27T10:30:45Z"
        custom_fmt = "%H時%M分"
        assert format_datetime_filter(iso_str, fmt=custom_fmt) == "10時30分"

    def test_timezone_conversion_tokyo(self, monkeypatch):
        monkeypatch.setenv("TIMEZONE", "Asia/Tokyo")
        iso_str_utc = "2023-10-27T00:00:00Z" # Midnight UTC
        # Expected: 2023-10-27 09:00 JST (or +0900, or Asia/Tokyo depending on pytz/system)
        # Default format is "%Y-%m-%d %H:%M %Z"
        result = format_datetime_filter(iso_str_utc)
        assert "2023-10-27 09:00" in result
        assert "JST" in result or "+0900" in result or "Asia/Tokyo" in result # pytz specific name for JST

    def test_timezone_conversion_new_york(self, monkeypatch):
        monkeypatch.setenv("TIMEZONE", "America/New_York")
        iso_str_utc = "2023-10-27T10:00:00Z" # 10 AM UTC
        # Expected: 2023-10-27 06:00 EDT (if DST is active for that date, otherwise EST)
        # For simplicity, we'll check the hour, assuming conversion logic is correct
        # Oct 27 is before DST ends in US (usually first Sunday in Nov)
        result = format_datetime_filter(iso_str_utc)
        assert "06:00" in result # 10 AM UTC is 6 AM EDT (UTC-4)
        assert "EDT" in result or "-0400" in result or "America/New_York" in result

    def test_system_timezone(self, monkeypatch):
        # This test is a bit more volatile as it depends on the runner's system timezone
        # We'll patch get_localzone to return a known timezone for predictability
        mock_local_tz = MagicMock()
        mock_local_tz.zone = "Europe/London" # Example known timezone
        
        with patch('utils.get_localzone', return_value=pytz.timezone("Europe/London")):
            monkeypatch.setenv("TIMEZONE", "system")
            iso_str_utc = "2023-10-27T10:00:00Z" # 10 AM UTC
            # Expected: 2023-10-27 11:00 BST (if DST active for London on that date)
            # Oct 27, UK is on BST (UTC+1) as DST ends last Sunday in Oct.
            result = format_datetime_filter(iso_str_utc)
            assert "11:00" in result 
            assert "BST" in result or "+0100" in result or "Europe/London" in result


    def test_invalid_inputs_for_filter(self, monkeypatch):
        monkeypatch.setenv("TIMEZONE", "UTC") # Consistent base for invalid tests
        assert format_datetime_filter(None) == "" # As per filter's behavior
        assert format_datetime_filter("") == ""   # As per filter's behavior
        
        malformed_date = "not-a-date-string"
        assert format_datetime_filter(malformed_date) == malformed_date # Returns original on error
        
        # Test with a date string that fromisoformat might parse but is not Twitch's 'Z' format
        # This should ideally be handled by the `replace('Z', '+00:00')`
        # If it's truly unparseable by fromisoformat after that, it will return original.
        non_z_iso = "2023-10-27T10:00:00+05:00" # This is valid ISO, filter should handle it
        # If TIMEZONE is UTC, it should convert +05:00 to UTC
        # 10:00+05:00 is 05:00 UTC
        assert "05:00" in format_datetime_filter(non_z_iso)

    def test_unknown_timezone_fallback(self, monkeypatch, caplog):
        monkeypatch.setenv("TIMEZONE", "Mars/OlympusMons") # Invalid timezone
        iso_str = "2023-10-27T10:00:00Z"
        # Expect fallback to UTC
        result = format_datetime_filter(iso_str)
        assert "Unknown timezone 'Mars/OlympusMons'" in caplog.text
        assert "2023-10-27 10:00" in result # Should be UTC time
        if "UTC" in result:
            assert result.endswith("UTC")


    def test_get_localzone_returns_none(self, monkeypatch, caplog):
        monkeypatch.setenv("TIMEZONE", "system")
        with patch('utils.get_localzone', return_value=None):
            iso_str = "2023-10-27T10:00:00Z"
            result = format_datetime_filter(iso_str)
            assert "tzlocal.get_localzone() returned None" in caplog.text
            assert "2023-10-27 10:00" in result # Fallback to UTC
            if "UTC" in result:
                assert result.endswith("UTC")

    def test_get_localzone_raises_exception(self, monkeypatch, caplog):
        monkeypatch.setenv("TIMEZONE", "system")
        with patch('utils.get_localzone', side_effect=Exception("tzlocal failed")):
            iso_str = "2023-10-27T10:00:00Z"
            result = format_datetime_filter(iso_str)
            assert "Error getting system timezone with tzlocal: tzlocal failed" in caplog.text
            assert "2023-10-27 10:00" in result # Fallback to UTC
            if "UTC" in result:
                assert result.endswith("UTC")
