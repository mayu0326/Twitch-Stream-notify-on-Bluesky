# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

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

from eventsub import setup_broadcaster_id
from utils import rotate_secret_if_needed
from flask import jsonify
from eventsub import (
    get_valid_app_access_token,
    create_eventsub_subscription,
    verify_signature,
)
from logging_config import configure_logging
from eventsub import cleanup_eventsub_subscriptions
from tunnel import start_tunnel, stop_tunnel
from bluesky import BlueskyPoster  # BlueskyPosterクラスのインポート
from flask import Flask, request
from youtube_monitor import YouTubeMonitor
from niconico_monitor import NiconicoMonitor
import os
import sys
import signal
from version_info import __version__
from markupsafe import escape
from dotenv import load_dotenv
import threading
from utils import get_ngrok_public_url, get_localtunnel_url_from_stdout, set_webhook_callback_url_temporary

# 設定ファイルの存在チェック
if not os.path.exists('settings.env'):
    print('設定ファイルが見つかりません。初期セットアップを実行します。')
    try:
        import tkinter as tk
        from gui.setup_wizard import SetupWizard
        root = tk.Tk()
        root.withdraw()
        def on_finish():
            root.destroy()
        SetupWizard(master=root, on_finish=on_finish)
        root.mainloop()
    except Exception as e:
        print(f"セットアップウィザードの起動に失敗しました: {e}")
    if __name__ == "__main__":
        sys.exit(1)

# 存在すれば読み込む
load_dotenv('settings.env')

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__version__ = __version__

# Flaskアプリケーションの生成
app = Flask(__name__)


def validate_settings():
    # 必須設定値がすべて存在するか検証する
    required_keys = [
        "BLUESKY_USERNAME",
        "BLUESKY_APP_PASSWORD",
        "TWITCH_CLIENT_ID",
        "TWITCH_CLIENT_SECRET",
        "TWITCH_BROADCASTER_ID"
    ]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    # Webhook URLの必須判定をトンネル種別で分岐
    tunnel_service = os.getenv("TUNNEL_SERVICE", "").lower()
    if tunnel_service in ("cloudflare", "custom"):
        if not os.getenv("WEBHOOK_CALLBACK_URL_PERMANENT"):
            missing_keys.append("WEBHOOK_CALLBACK_URL_PERMANENT")
    elif tunnel_service in ("ngrok", "localtunnel"):
        if not os.getenv("WEBHOOK_CALLBACK_URL_TEMPORARY"):
            missing_keys.append("WEBHOOK_CALLBACK_URL_TEMPORARY")
    else:
        if not os.getenv("WEBHOOK_CALLBACK_URL"):
            missing_keys.append("WEBHOOK_CALLBACK_URL")

    if missing_keys:
        raise ValueError(f"settings.envの必須設定が未設定です: {', '.join(missing_keys)}")

    # 数値設定値が正しいか検証する
    numeric_keys_defaults = {
        "RETRY_MAX": "3",
        "RETRY_WAIT": "2",
        "LOG_RETENTION_DAYS": "14"
    }
    for key, default_value in numeric_keys_defaults.items():
        try:
            value_str = os.getenv(key, default_value)
            int(value_str)
        except ValueError:
            raise ValueError(
                f"settings.envの数値設定値 '{key}' (値: {value_str}) が不正です")


@app.errorhandler(404)
def handle_404(e):
    # 404エラー発生時の処理
    try:
        safe_url = escape(request.url)
        safe_ua = escape(request.user_agent.string)
        app.logger.warning(
            f"404エラー発生: {safe_url} (User agent: {safe_ua})")
    except AttributeError:
        print("Warning: 404 error (URL情報取得不可)")
    return "Not Found", 404


@app.route("/webhook", methods=["POST", "GET"])
def handle_webhook():
    # Webhookエンドポイントの処理
    if request.method == "GET":
        app.logger.info("Webhookエンドポイントは正常に稼働しています。")
        return "Webhook endpoint is working! POST requests only.", 200

    # 署名検証
    if not verify_signature(request):
        return jsonify({"status": "signature mismatch"}), 403

    try:
        data = request.get_json()
        if data is None:
            app.logger.warning("Webhook受信: 無効なJSONデータまたは空のボディ")
            return jsonify({"error": "Invalid JSON or empty body"}), 400
    except Exception as e:
        app.logger.error(f"Webhook受信: JSON解析エラー: {e}", exc_info=e)
        return jsonify({"error": "Invalid JSON"}), 400

    message_type = request.headers.get("Twitch-Eventsub-Message-Type")
    subscription_payload = data.get(
        "subscription", {}) if isinstance(data, dict) else {}
    subscription_type = subscription_payload.get("type")

    # Webhook検証チャレンジ
    if message_type == "webhook_callback_verification":
        challenge = data.get("challenge", "") if isinstance(data, dict) else ""
        app.logger.info(
            f"Webhook検証チャレンジ受信 ({subscription_type if subscription_type else 'タイプ不明'}): {challenge[:50]}...")
        return challenge, 200, {"Content-Type": "text/plain"}

    # 通知イベントの処理
    if message_type == "notification":
        event_data = data.get("event", {}) if isinstance(data, dict) else {}
        broadcaster_user_login_from_event = event_data.get(
            "broadcaster_user_login")

        if not broadcaster_user_login_from_event:
            app.logger.warning(
                f"Webhook通知 ({subscription_type}): 'event.broadcaster_user_login' が不足しています。処理をスキップします。イベントデータ: {event_data}")
            return jsonify({"error": "Missing required field: event.broadcaster_user_login"}), 400

        broadcaster_user_name_from_event = event_data.get(
            "broadcaster_user_name", broadcaster_user_login_from_event)
        app.logger.info(
            f"通知受信 ({subscription_type}) for {
                broadcaster_user_name_from_event or broadcaster_user_login_from_event}")

        notify_on_online_str = os.getenv("NOTIFY_ON_TWITCH_ONINE", "True").lower()
        NOTIFY_ON_ONLINE = notify_on_online_str == "true"
        notify_on_offline_str = os.getenv("NOTIFY_ON_TWITCH_OFFLINE", "False").lower()
        NOTIFY_ON_OFFLINE = notify_on_offline_str == "true"

        # 配信開始イベント
        if subscription_type == "stream.online":
            if NOTIFY_ON_ONLINE:
                # stream.online用の必須項目チェック
                if event_data.get("title") is None or event_data.get("category_name") is None:
                    app.logger.warning(
                        f"Webhook通知 (stream.online): 'title' または 'category_name' が不足しています. イベントデータ: {event_data}")
                    return jsonify(
                        {"error": "Missing title or category_name for stream.online event"}), 400

                event_context = {
                    "broadcaster_user_id": event_data.get("broadcaster_user_id"),
                    "broadcaster_user_login": broadcaster_user_login_from_event,
                    "broadcaster_user_name": broadcaster_user_name_from_event,
                    "title": event_data.get("title"),
                    "category_name": event_data.get("category_name"),
                    "game_id": event_data.get("game_id"),
                    "game_name": event_data.get("game_name", event_data.get("category_name")),
                    "language": event_data.get("language"),
                    "started_at": event_data.get("started_at"),
                    "type": event_data.get("type"),
                    "is_mature": event_data.get("is_mature"),
                    "tags": event_data.get("tags", []),
                    "stream_url": f"https://twitch.tv/{broadcaster_user_login_from_event}"
                }

                try:
                    bluesky_poster = BlueskyPoster(
                        os.getenv("BLUESKY_USERNAME"),
                        os.getenv("BLUESKY_APP_PASSWORD")
                    )
                    success = bluesky_poster.post_stream_online(
                        event_context=event_context,
                        image_path=os.getenv("BLUESKY_IMAGE_PATH")
                    )
                    if success:
                        app.logger.info(
                            f"Bluesky投稿成功 (stream.online): {broadcaster_user_login_from_event}")
                        return jsonify({"status": "success"}), 200
                    else:
                        app.logger.error(
                            f"Bluesky投稿処理失敗 (stream.online - BlueskyPoster.post_stream_online returned False): {broadcaster_user_login_from_event}")
                        return jsonify({"status": "bluesky error processing stream.online"}), 500
                except Exception as e:
                    app.logger.error(
                        f"Bluesky投稿中の未処理例外 (stream.online): {str(e)}", exc_info=e)
                    return jsonify(
                        {"error": "Internal server error during stream.online processing"}), 500
            else:
                app.logger.info(
                    f"stream.online通知は設定によりスキップされました: {broadcaster_user_login_from_event}")
                return jsonify({"status": "skipped, online notifications disabled"}), 200

        # 配信終了イベント
        elif subscription_type == "stream.offline":
            if NOTIFY_ON_OFFLINE:
                event_context = {
                    "broadcaster_user_id": event_data.get("broadcaster_user_id"),
                    "broadcaster_user_login": broadcaster_user_login_from_event,
                    "broadcaster_user_name": broadcaster_user_name_from_event,
                    "channel_url": f"https://twitch.tv/{broadcaster_user_login_from_event}"
                }
                app.logger.info(
                    f"stream.offlineイベント処理開始: {
                        event_context.get('broadcaster_user_name')} ({
                        event_context.get('broadcaster_user_login')})")
                try:
                    bluesky_poster = BlueskyPoster(
                        os.getenv("BLUESKY_USERNAME"),
                        os.getenv("BLUESKY_APP_PASSWORD")
                    )
                    success = bluesky_poster.post_stream_offline(
                        event_context=event_context
                    )
                    app.logger.info(
                        f"Bluesky投稿試行 (stream.offline): {
                            event_context.get('broadcaster_user_login')}, 成功: {success}")
                    return jsonify(
                        {"status": "success, offline notification posted" if success else "bluesky error, offline notification not posted"}
                    ), 200
                except Exception as e:
                    app.logger.error(
                        f"Bluesky投稿エラー (stream.offline): {str(e)}", exc_info=True)
                    return jsonify(
                        {"error": "Internal server error during stream.offline processing"}), 500
            else:
                app.logger.info(
                    f"stream.offline通知は設定によりスキップされました: {broadcaster_user_login_from_event}")
                return jsonify({"status": "skipped, offline notifications disabled"}), 200

        # 未対応イベントタイプ
        else:
            app.logger.warning(
                f"不明なサブスクリプションタイプ ({subscription_type}) の通知受信: {broadcaster_user_login_from_event}")
            return jsonify(
                {"status": "error", "message": f"Unknown or unhandled subscription type: {subscription_type}"}), 400

    # サブスクリプション失効通知
    if message_type == 'revocation':
        revocation_status = subscription_payload.get("status", "不明なステータス")
        app.logger.warning(
            f"Twitch EventSubサブスクリプション失効通知受信: タイプ - {subscription_type}, ステータス - {revocation_status}, ユーザー - {
                data.get(
                    'event',
                    {}).get(
                    'broadcaster_user_login',
                    'N/A')}")
        return jsonify({"status": "revocation notification received"}), 200

    # 未処理のメッセージタイプ
    app.logger.info(
        f"受信した未処理のTwitch EventSubメッセージタイプ: {message_type if message_type else '不明'}. データ: {data}")
    return jsonify({"status": "unhandled message type or event"}), 200


logger = None
audit_logger = None

# グローバル変数としてプロセスやスレッドを保持
tunnel_proc = None
yt_monitor_thread = None
nn_monitor_thread = None
flask_server_thread = None  # Flaskサーバーを別スレッドで動かす場合
tunnel_monitor_thread = None  # ngrok/localtunnel監視用


def cleanup_application():
    global tunnel_proc, yt_monitor_thread, nn_monitor_thread, flask_server_thread
    if logger:
        logger.info("アプリケーションのクリーンアップ処理を開始します。")

    # トンネルを停止
    if tunnel_proc:
        if logger:
            logger.info("トンネルを停止します。")
        else:
            print("トンネルを停止します。")
        stop_tunnel(tunnel_proc, logger)
        tunnel_proc = None

    # YouTube監視スレッドの停止 (is_aliveを確認し、必要であればjoin)
    if yt_monitor_thread and yt_monitor_thread.is_alive():
        if logger:
            logger.info("YouTube監視スレッドを停止します。")
        # スレッドに停止を通知する仕組みがあればここで呼び出す
        # yt_monitor_thread.stop() # 例: もしstopメソッドがあれば
        yt_monitor_thread.join(timeout=5)  # タイムアウト付きで待機

    # ニコニコ監視スレッドの停止 (同様に)
    if nn_monitor_thread and nn_monitor_thread.is_alive():
        if logger:
            logger.info("ニコニコ監視スレッドを停止します。")
        # nn_monitor_thread.stop() # 例
        nn_monitor_thread.join(timeout=5)

    # EventSubサブスクリプションのクリーンアップ (必要に応じて)
    # WEBHOOK_CALLBACK_URL = os.getenv("WEBHOOK_CALLBACK_URL")
    # if WEBHOOK_CALLBACK_URL:
    #     cleanup_eventsub_subscriptions(WEBHOOK_CALLBACK_URL, logger_to_use=logger)

    # Flaskサーバーのスレッドを停止 (もし別スレッドで動かしている場合)
    # if flask_server_thread and flask_server_thread.is_alive():
    #     if logger:
    #         logger.info("Flaskサーバーを停止します。")
        # ここでFlaskサーバーを安全に停止する処理 (例: waitressのshutdown)
        # flask_server_thread.join(timeout=5)

    if logger:
        logger.info("アプリケーションのクリーンアップ処理が完了しました。")
    else:
        print("アプリケーションのクリーンアップ処理が完了しました。")


def signal_handler(sig, frame):
    if logger:
        logger.info(f"シグナル {sig} を受信しました。アプリケーションを終了します。")
    else:
        print(f"シグナル {sig} を受信しました。アプリケーションを終了します。")
    cleanup_application()
    sys.exit(0)


def tunnel_monitor_loop(
        tunnel_service,
        tunnel_cmd,
        logger,
        proc_getter,
        proc_setter,
        env_path="settings.env"):
    """
    ngrok/localtunnelプロセスの死活監視・自動再起動・新URL自動反映ループ
    proc_getter: 現在のプロセスを取得する関数
    proc_setter: 新しいプロセスをセットする関数
    """
    import time
    while True:
        proc = proc_getter()
        if proc is None or proc.poll() is not None:
            logger.warning(f"トンネルプロセス({tunnel_service})が停止しました。自動再起動します。")
            # 再起動
            from tunnel import start_tunnel
            new_proc = start_tunnel(logger)
            proc_setter(new_proc)
            time.sleep(2)  # 起動待ち
            # 新しい一時URLを取得してenv反映
            url = None
            if tunnel_service == "ngrok":
                url = get_ngrok_public_url(logger=logger)
            elif tunnel_service == "localtunnel":
                # localtunnelはコマンドのstdoutからURLを取得する必要があるが、
                # ここでは再起動直後は取得できないため、ユーザーが別途反映する運用も許容
                # TODO: より堅牢にする場合はPopenのstdoutを監視する設計に拡張
                pass
            if url:
                set_webhook_callback_url_temporary(url, env_path=env_path)
                logger.info(f"新しい一時URL({tunnel_service}): {url} をsettings.envに反映しました。")
        time.sleep(5)


if __name__ == "__main__":
    # Register the global exception handler before starting the app
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log unhandled exceptions
        app.logger.error("リクエスト処理中に未処理例外発生", exc_info=e)
        return (
            jsonify({"error": "予期せぬサーバーエラーが発生しました。"}),
            500,
        )

    if os.name == "nt":
        sys.stdout = open(sys.stdout.fileno(), mode='w',
                          encoding='cp932', buffering=1)
        sys.stderr = open(sys.stderr.fileno(), mode='w',
                          encoding='cp932', buffering=1)
    # シグナルハンドラの設定
    signal.signal(signal.SIGINT, signal_handler)
    # Windowsの場合、CTRL_BREAK_EVENTも同様に処理することが考えられる
    if os.name == 'nt':
        signal.signal(signal.SIGBREAK, signal_handler)

    # メイン処理（初期化・監視・サーバ起動）
    # tunnel_proc = None # グローバル変数として定義したのでここでは不要
    try:
        # ロギング設定
        logger, app_logger_handlers, audit_logger, tunnel_logger = configure_logging(app)
        # シークレットのローテーション
        WEBHOOK_SECRET = rotate_secret_if_needed(logger)
        os.environ["WEBHOOK_SECRET"] = WEBHOOK_SECRET

        # BROADCASTER_IDのセットアップ
        setup_broadcaster_id(logger_to_use=logger)
        # 設定ファイルの検証
        validate_settings()
        logger.info("設定ファイルの検証が完了しました。")

        # Twitchアクセストークンの取得
        TWITCH_APP_ACCESS_TOKEN = get_valid_app_access_token(
            logger_to_use=logger)
        if not TWITCH_APP_ACCESS_TOKEN:
            logger.critical("TwitchAPIアクセストークンの取得に失敗しました。アプリケーションは起動できません。")
            sys.exit(1)
        logger.info("TwitchAPIアクセストークン取得を確認しました。")

        # EventSubサブスクリプションのクリーンアップ
        webhook_url = None
        tunnel_service = os.getenv("TUNNEL_SERVICE", "").lower()
        if tunnel_service in ("cloudflare", "custom"):
            webhook_url = os.getenv("WEBHOOK_CALLBACK_URL_PERMANENT")
        elif tunnel_service in ("ngrok", "localtunnel"):
            webhook_url = os.getenv("WEBHOOK_CALLBACK_URL_TEMPORARY")
        else:
            webhook_url = os.getenv("WEBHOOK_CALLBACK_URL")
        cleanup_eventsub_subscriptions(
            webhook_url, logger_to_use=logger)

        # トンネルの起動
        tunnel_proc = start_tunnel(tunnel_logger)
        if not tunnel_proc:
            tunnel_logger.critical("トンネルの起動に失敗しました。アプリケーションは起動できません。")
            sys.exit(1)
        # ngrok/localtunnelの場合は監視スレッドを起動
        tunnel_service = os.getenv("TUNNEL_SERVICE", "").lower()
        if tunnel_service in ("ngrok", "localtunnel"):
            def get_proc():
                return tunnel_proc

            def set_proc(p):
                global tunnel_proc
                tunnel_proc = p
            tunnel_monitor_thread = threading.Thread(
                target=tunnel_monitor_loop,
                args=(
                    tunnel_service,
                    os.getenv("NGROK_CMD") if tunnel_service == "ngrok" else os.getenv("LOCALTUNNEL_CMD"),
                    tunnel_logger,
                    get_proc,
                    set_proc),
                daemon=True)
            tunnel_monitor_thread.start()

        # 必須EventSubサブスクリプションの作成
        event_types_to_subscribe = ["stream.online", "stream.offline"]
        all_subscriptions_successful = True
        for event_type in event_types_to_subscribe:
            logger.info(f"{event_type} のEventSubサブスクリプションを作成します...")
            # サブスクリプション作成時も同様にURLを分岐
            if tunnel_service in ("cloudflare", "custom"):
                webhook_url = os.getenv("WEBHOOK_CALLBACK_URL_PERMANENT")
            elif tunnel_service in ("ngrok", "localtunnel"):
                webhook_url = os.getenv("WEBHOOK_CALLBACK_URL_TEMPORARY")
            else:
                webhook_url = os.getenv("WEBHOOK_CALLBACK_URL")
            sub_response = create_eventsub_subscription(
                event_type, logger_to_use=logger, webhook_url=webhook_url)

            if not sub_response or not isinstance(
                    sub_response, dict) or not sub_response.get("data") or not isinstance(
                    sub_response["data"], list) or not sub_response["data"]:
                twitch_error_status = sub_response.get(
                    "status") if isinstance(sub_response, dict) else None
                twitch_error_message = sub_response.get(
                    "message") if isinstance(sub_response, dict) else None
                log_message = f"{event_type} EventSubサブスクリプションの作成に失敗しました。"
                if twitch_error_status:
                    pass
                if twitch_error_message:
                    pass
                logger.critical(log_message + f" 詳細: {sub_response}")
                all_subscriptions_successful = False
                break

            if sub_response.get("status") == "already exists":
                logger.info(
                    f"{event_type} EventSubサブスクリプションは既に存在します。ID: {sub_response.get('id')}")
            else:
                subscription_details = sub_response['data'][0]
                logger.info(
                    f"{event_type} EventSubサブスクリプション作成成功。ID: {
                        subscription_details.get('id')}, ステータス: {
                        subscription_details.get('status')}")

        if not all_subscriptions_successful:
            logger.critical("必須EventSubサブスクリプションの作成に失敗したため、アプリケーションは起動できません。")
            sys.exit(1)

        # --- YouTube・ニコニコ監視スレッド起動 ---
        def on_youtube_live(live_info):
            # YouTubeライブ配信開始時のコールバック
            if os.getenv("NOTIFY_ON_YOUTUBE_ONLINE", "False") == "True":
                logger.info("[YouTube] 配信開始検出！")
                try:
                    bluesky_poster = BlueskyPoster(
                        os.getenv("BLUESKY_USERNAME"),
                        os.getenv("BLUESKY_APP_PASSWORD")
                    )
                    # 投稿内容を組み立て
                    event_context = {
                        "title": "YouTubeライブ配信開始",
                        "channel_id": youtube_channel_id,
                        "stream_url": f"https://www.youtube.com/channel/{youtube_channel_id}/live"
                    }
                    success = bluesky_poster.post_stream_online(
                        event_context=event_context,
                        image_path=os.getenv("BLUESKY_IMAGE_PATH"),
                        platform="yt_nico"
                    )
                    if success:
                        logger.info("[YouTube] Bluesky投稿成功（配信開始）")
                    else:
                        logger.error("[YouTube] Bluesky投稿失敗（配信開始）")
                except Exception as e:
                    logger.error(f"[YouTube] Bluesky投稿中に例外発生: {e}", exc_info=e)

        def on_youtube_new_video(video_id):
            # YouTube新着動画検出時のコールバック
            if os.getenv("NOTIFY_ON_YOUTUBE_NEW_VIDEO", "False") == "True":
                logger.info(f"[YouTube] 新着動画検出: {video_id}")
                try:
                    bluesky_poster = BlueskyPoster(
                        os.getenv("BLUESKY_USERNAME"),
                        os.getenv("BLUESKY_APP_PASSWORD")
                    )
                    event_context = {
                        "title": "YouTube新着動画投稿",
                        "video_id": video_id,
                        "video_url": f"https://www.youtube.com/watch?v={video_id}"
                    }
                    success = bluesky_poster.post_new_video(
                        event_context=event_context,
                        image_path=os.getenv("BLUESKY_IMAGE_PATH")
                    )
                    if success:
                        logger.info("[YouTube] Bluesky投稿成功（新着動画）")
                    else:
                        logger.error("[YouTube] Bluesky投稿失敗（新着動画）")
                except Exception as e:
                    logger.error(f"[YouTube] Bluesky投稿中に例外発生: {e}", exc_info=e)

        def on_niconico_live(live_id):
            # ニコニコ生放送配信開始時のコールバック
            if os.getenv("NOTIFY_ON_NICONICO_ONLINE", "False") == "True":
                logger.info(f"[ニコ生] 配信開始検出: {live_id}")
                try:
                    bluesky_poster = BlueskyPoster(
                        os.getenv("BLUESKY_USERNAME"),
                        os.getenv("BLUESKY_APP_PASSWORD")
                    )
                    event_context = {
                        "title": "ニコニコ生放送配信開始",
                        "live_id": live_id,
                        "stream_url": f"https://live.nicovideo.jp/watch/{live_id}"
                    }
                    success = bluesky_poster.post_stream_online(
                        event_context=event_context,
                        image_path=os.getenv("BLUESKY_IMAGE_PATH"),
                        platform="yt_nico"
                    )
                    if success:
                        logger.info("[ニコ生] Bluesky投稿成功（配信開始）")
                    else:
                        logger.error("[ニコ生] Bluesky投稿失敗（配信開始）")
                except Exception as e:
                    logger.error(f"[ニコ生] Bluesky投稿中に例外発生: {e}", exc_info=e)

        def on_niconico_new_video(video_id):
            # ニコニコ動画新着投稿検出時のコールバック
            if os.getenv("NOTIFY_ON_NICONICO_NEW_VIDEO", "False") == "True":
                logger.info(f"[ニコ動] 新着動画検出: {video_id}")
                try:
                    bluesky_poster = BlueskyPoster(
                        os.getenv("BLUESKY_USERNAME"),
                        os.getenv("BLUESKY_APP_PASSWORD")
                    )
                    event_context = {
                        "title": "ニコニコ動画新着投稿",
                        "video_id": video_id,
                        "video_url": f"https://www.nicovideo.jp/watch/{video_id}"
                    }
                    success = bluesky_poster.post_new_video(
                        event_context=event_context,
                        image_path=os.getenv("BLUESKY_IMAGE_PATH")
                    )
                    if success:
                        logger.info("[ニコ動] Bluesky投稿成功（新着動画）")
                    else:
                        logger.error("[ニコ動] Bluesky投稿失敗（新着動画）")
                except Exception as e:
                    logger.error(f"[ニコ動] Bluesky投稿中に例外発生: {e}", exc_info=e)

        # YouTube監視設定の取得
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        youtube_channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
        youtube_poll_interval = int(os.getenv("YOUTUBE_POLL_INTERVAL", 60))
        niconico_user_id = os.getenv("NICONICO_USER_ID")
        niconico_poll_interval = int(
            os.getenv("NICONICO_LIVE_POLL_INTERVAL", 60))

        # YouTube監視スレッドの起動
        if youtube_api_key and youtube_channel_id:
            yt_monitor = YouTubeMonitor(
                youtube_api_key, youtube_channel_id, youtube_poll_interval,
                on_youtube_live, on_youtube_new_video
            )
            yt_monitor.start()

        # ニコニコ監視スレッドの起動
        if niconico_user_id:
            nn_monitor = NiconicoMonitor(
                niconico_user_id, niconico_poll_interval,
                on_niconico_live, on_niconico_new_video
            )
            nn_monitor.start()

        # Flask (waitress) サーバーの起動
        logger.info("アプリケーションの起動を完了しました。")
        from waitress import serve
        serve(app, host="0.0.0.0", port=3000)  # 現状のまま直接実行

    except ValueError as ve:
        # 設定値エラー時の処理
        log_msg = f"設定エラー: {ve}. アプリケーションは起動できません。"
        if logger:
            logger.critical(log_msg)
        else:
            app.logger.critical(log_msg)
        sys.exit(1)
    except Exception as e:
        # その他の初期化エラー時の処理
        log_msg_critical = "初期化中の未処理例外によりアプリケーションの起動に失敗しました。"
        if logger:
            logger.critical(log_msg_critical, exc_info=e)
            # ログローテーションハンドラを閉じる
            for handler in app_logger_handlers:
                handler.close()
        else:
            app.logger.critical(f"CRITICAL: {log_msg_critical} {e}")
        # cleanup_application() # エラー発生時もクリーンアップを試みる
        sys.exit(1)
    finally:
        # クリーンアップ時もtunnel_loggerを渡す
        stop_tunnel(tunnel_proc, tunnel_logger)
        cleanup_application()  # finallyブロックでも呼び出す
