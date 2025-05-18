# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

__author__    = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__   = "GPLv2"
__version__   = "1.0.0"

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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import pytest
from utils import is_valid_url, retry_on_exception

def test_is_valid_url():
    assert is_valid_url("http://example.com")
    assert is_valid_url("https://example.com")
    assert not is_valid_url("ftp://example.com")
    assert not is_valid_url("example.com")
    assert not is_valid_url("")

def test_retry_on_exception_success():
    @retry_on_exception(max_retries=2, wait_seconds=0.1)
    def always_ok():
        return 42
    assert always_ok() == 42

def test_retry_on_exception_retry():
    calls = {"count": 0}
    @retry_on_exception(max_retries=2, wait_seconds=0.1)
    def fail_once():
        if calls["count"] < 1:
            calls["count"] += 1
            raise ValueError("fail")
        return 99
    assert fail_once() == 99

def test_retry_on_exception_fail():
    @retry_on_exception(max_retries=2, wait_seconds=0.1)
    def always_fail():
        raise ValueError("fail")
    with pytest.raises(ValueError):
        always_fail()

