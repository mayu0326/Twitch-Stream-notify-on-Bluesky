# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from bluesky import BlueskyPoster
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


def test_post_stream_online_invalid_url(monkeypatch):
    poster = BlueskyPoster("user", "pass")
    assert not poster.post_stream_online("title", "cat", "ftp://example.com")
    assert not poster.post_stream_online("title", "cat", "")


def test_post_stream_online_valid(monkeypatch):
    poster = BlueskyPoster("user", "pass")
    # Bluesky APIを実際に叩かないようにsend_postをモンキーパッチ
    monkeypatch.setattr(poster.client, "login", lambda u, p: None)
    monkeypatch.setattr(poster.client, "send_post", lambda x, embed=None: None)
    assert poster.post_stream_online("title", "cat", "https://example.com")
