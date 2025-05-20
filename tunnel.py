# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

import subprocess
import os
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


def start_tunnel(logger=None):
    tunnel_cmd = os.getenv("TUNNEL_CMD")
    if not tunnel_cmd:
        if logger:
            logger.warning("TUNNEL_CMDが設定されていません。トンネルは起動しません。")
        else:
            print("TUNNEL_CMDが設定されていません。トンネルは起動しません。")
        return None
    try:
        proc = subprocess.Popen(
            tunnel_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if logger:
            logger.info(f"トンネルを起動しました: {tunnel_cmd}")
        else:
            print(f"トンネルを起動しました: {tunnel_cmd}")
        return proc
    except Exception as e:
        if logger:
            logger.error(f"トンネル起動失敗: {e}")
        else:
            print(f"トンネル起動失敗: {e}")
        return None


def stop_tunnel(proc, logger=None):
    if proc:
        proc.terminate()
        if logger:
            logger.info("トンネルを終了しました。")
        else:
            print("トンネルを終了しました。")
