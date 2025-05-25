# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

import subprocess
import os
import shlex  # コマンドライン引数の安全な分割用
from version import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__


# Stream notify on Bluesky
# Copyright (C) 2025 mayuneco(mayunya)
#
# このプログラムはフリーソフトウェアです。フリーソフトウェア財団によって発行された
# GNU 一般公衆利用許諾契約書（バージョン2またはそれ以降）に基づき、再配布または
# 改変することができます。
#
# このプログラムは有用であることを願って配布されていますが、
# 商品性や特定目的への適合性についての保証はありません。
# 詳細はGNU一般公衆利用許諾契約書をご覧ください。
#
# このプログラムとともにGNU一般公衆利用許諾契約書が配布されているはずです。
# もし同梱されていない場合は、フリーソフトウェア財団までご請求ください。
# 住所: 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


def start_tunnel(logger=None):
    """
    TUNNEL_CMDで指定されたコマンドでトンネルプロセスを起動する
    loggerが指定されていればログ出力も行う
    """
    tunnel_cmd = os.getenv("TUNNEL_CMD")
    if not tunnel_cmd:
        if logger:
            logger.warning("TUNNEL_CMDが設定されていません。トンネルは起動しません。")
        else:
            print("TUNNEL_CMDが設定されていません。トンネルは起動しません。")
        return None
    try:
        # shlex.splitでコマンドラインを安全に分割
        # 標準出力・標準エラーはDEVNULLにリダイレクトしてサイレント起動
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
    except FileNotFoundError:  # コマンドが見つからない場合のエラー
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
    """
    トンネルプロセスを終了させる
    proc: start_tunnelで返されたPopenオブジェクト
    logger: ログ出力用ロガー
    """
    if proc:
        try:
            proc.terminate()  # 正常終了を試みる
            proc.wait(timeout=5)  # 最大5秒待機
            if logger:
                logger.info("トンネルを正常に終了しました。")
            else:
                print("トンネルを正常に終了しました。")
        except subprocess.TimeoutExpired:
            # 終了がタイムアウトした場合は強制終了
            if logger:
                logger.warning("トンネル終了がタイムアウトしました。強制終了します。")
            else:
                print("トンネル終了がタイムアウトしました。強制終了します。")
            proc.kill()  # 強制終了
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
        # プロセスがNoneの場合は何もしない
        if logger:
            logger.info("トンネルプロセスが存在しないため、終了処理はスキップされました。")
        else:
            print("トンネルプロセスが存在しないため、終了処理はスキップされました。")
