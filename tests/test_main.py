# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

from main import app
import os
import pytest
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


os.environ["BLUESKY_USERNAME"] = "dummy_user"
os.environ["BLUESKY_PASSWORD"] = "dummy_password"
os.environ["BLUESKY_IMAGE_PATH"] = ""


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_webhook_get(client):
    response = client.get("/webhook")
    assert response.status_code == 200
    assert b"Webhook endpoint is working!" in response.data


def test_webhook_invalid_signature(client, monkeypatch):
    # verify_signatureを常にFalseを返すようモック
    monkeypatch.setattr("main.verify_signature", lambda req: False)
    response = client.post("/webhook", json={})
    assert response.status_code == 403


def test_webhook_invalid_json(client, monkeypatch):
    # 署名検証を常にTrueにモック
    monkeypatch.setattr("main.verify_signature", lambda req: True)
    response = client.post("/webhook", data="notjson",
                           content_type="application/json")
    assert response.status_code == 400


def test_webhook_missing_fields(client, monkeypatch):
    # verify_signatureをTrueにモック
    monkeypatch.setattr("main.verify_signature", lambda req: True)
    # 必須フィールドがない場合
    response = client.post("/webhook", json={"subscription": {}, "event": {}})
    assert response.status_code == 400
