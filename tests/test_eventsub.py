# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from eventsub import verify_signature
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


class DummyRequest:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body # Changed from _body to body for clarity, matching usage

    def get_data(self, as_text=None): # Added as_text parameter
        if as_text:
            return self.body # Return string body if as_text is True
        return self.body.encode("utf-8") # Return bytes otherwise

    @property
    def remote_addr(self):
        return "127.0.0.1"


def test_verify_signature_missing_headers():
    req = DummyRequest(headers={}, body="{}")
    assert not verify_signature(req)


def test_verify_signature_invalid_timestamp():
    headers = {
        "Twitch-Eventsub-Message-Id": "abc",
        "Twitch-Eventsub-Message-Timestamp": "invalid", # This timestamp will cause parsing to fail
        "Twitch-Eventsub-Message-Signature": "sig"
    }
    req = DummyRequest(headers=headers, body="{}") # Body is simple JSON string
    assert not verify_signature(req)
