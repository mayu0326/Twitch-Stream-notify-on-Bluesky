# -*- coding: utf-8 -*-
"""
Twitch Stream notify on Bluesky

このモジュールはTwitch配信の通知をBlueskyに送信するBotの一部です。
"""

import subprocess
import os
import shlex # Added
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
        # Use shlex.split for proper parsing of command with quotes
        # Redirect stdout and stderr to DEVNULL to prevent pipe buffer issues
        # and to silence tunnel output unless explicitly logged or needed.
        proc = subprocess.Popen(
            shlex.split(tunnel_cmd), 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        if logger:
            logger.info(f"トンネルを起動しました: {tunnel_cmd}")
        else:
            print(f"トンネルを起動しました: {tunnel_cmd}")
        return proc
    except FileNotFoundError: # Specific error for command not found
        err_msg = f"トンネルコマンド '{tunnel_cmd.split()[0] if tunnel_cmd else ''}' が見つかりません。Pathが通っているか確認してください。"
        if logger:
            logger.error(err_msg)
        else:
            print(err_msg)
        return None
    except Exception as e:
        err_msg_generic = f"トンネル起動失敗: {e}"
        if logger:
            logger.error(err_msg_generic)
        else:
            print(err_msg_generic)
        return None


def stop_tunnel(proc, logger=None):
    if proc:
        try:
            proc.terminate() # Try to terminate gracefully
            proc.wait(timeout=5) # Wait for a bit for the process to terminate
            if logger:
                logger.info("トンネルを正常に終了しました。")
            else:
                print("トンネルを正常に終了しました。")
        except subprocess.TimeoutExpired:
            if logger:
                logger.warning("トンネル終了がタイムアウトしました。強制終了します。")
            else:
                print("トンネル終了がタイムアウトしました。強制終了します。")
            proc.kill() # Force kill if terminate doesn't work
            if logger:
                logger.info("トンネルを強制終了しました。")
            else:
                print("トンネルを強制終了しました。")
        except Exception as e:
            err_msg = f"トンネル終了中にエラーが発生しました: {e}"
            if logger:
                logger.error(err_msg)
            else:
                print(err_msg)
    else:
        if logger:
            logger.info("トンネルプロセスが存在しないため、終了処理はスキップされました。")
        else:
            print("トンネルプロセスが存在しないため、終了処理はスキップされました。")
