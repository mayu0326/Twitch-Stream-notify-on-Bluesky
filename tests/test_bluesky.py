# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""

import pytest
import os
from unittest.mock import patch, MagicMock, ANY, mock_open
from bluesky import BlueskyPoster, load_template
from atproto import exceptions as atproto_exceptions
from jinja2 import Template  # Templateを追加
from version import __version__
import asyncio

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

# pytestの警告抑制: mark.asyncio
pytestmark = pytest.mark.filterwarnings(
    r"ignore:Unknown pytest\.mark\.asyncio",
)


@pytest.fixture
def mock_env(monkeypatch):
    # テスト用の環境変数を設定
    monkeypatch.setenv("BLUESKY_USERNAME", "test_user")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "test_pass")
    monkeypatch.setenv("BLUESKY_TEMPLATE_PATH",
                       "templates/default_template.txt")
    monkeypatch.setenv("BLUESKY_OFFLINE_TEMPLATE_PATH",
                       "templates/offline_template.txt")
    # テスト用のデフォルト画像パス
    monkeypatch.setenv("BLUESKY_IMAGE_PATH", "images/test_image.png")
    # テスト時にutil_loggerが出力できるようにログレベルをDEBUGに
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def mock_event_context_online():
    # 配信開始イベント用のダミーcontext
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
    # 配信終了イベント用のダミーcontext
    return {
        "broadcaster_user_id": "12345",
        "broadcaster_user_login": "teststreamer",
        "broadcaster_user_name": "TestStreamer",
        "channel_url": "https://twitch.tv/teststreamer"
    }


class TestBlueskyPoster:

    def test_post_stream_online_invalid_event_context(self, mock_env):
        # 必須キーが不足している場合はFalseを返すことを確認
        poster = BlueskyPoster("user", "pass")
        invalid_context = {"broadcaster_user_name": "Test"}
        assert not poster.post_stream_online(invalid_context)

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    # os.path.isfileの代わりにupload_imageをモック
    @patch("bluesky.BlueskyPoster.upload_image")
    def test_post_stream_online_success_with_image(
        self, mock_upload_image, mock_load_template_func, mock_write_history, mock_atproto_client_class,
        mock_env, mock_event_context_online
    ):
        # テンプレートのモックを作成
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Online Template Text"
        mock_load_template_func.return_value = mock_template_obj

        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        dummy_blob = MagicMock()
        mock_upload_image.return_value = dummy_blob

        poster = BlueskyPoster("user", "pass")
        # os.path.isfileもTrueになるようにパッチ
        with patch("os.path.isfile", return_value=True) as mock_isfile_inner, \
                patch.dict(os.environ, {"BLUESKY_TEMPLATE_PATH": "templates/twitch_online_template.txt"}):
            result = poster.post_stream_online(
                event_context=mock_event_context_online,
                image_path="images/test_image.png"
            )
            mock_isfile_inner.assert_any_call("images/test_image.png")
            # テンプレートの存在確認も呼ばれるので、呼び出し回数は2回以上になる
            assert mock_isfile_inner.call_count >= 1

        assert result is True
        mock_client_instance.login.assert_called_once_with("user", "pass")

        # テンプレートパスが正しく渡されたか確認
        mock_load_template_func.assert_called_once_with(
            path="templates/twitch_online_template.txt")

        # テンプレートのrenderが正しく呼ばれたか
        mock_template_obj.render.assert_called_once_with(
            **mock_event_context_online, template_path="templates/twitch_online_template.txt")

        # upload_imageが呼ばれたか
        mock_upload_image.assert_called_once_with("images/test_image.png")

        mock_client_instance.send_post.assert_called_once()
        call_args = mock_client_instance.send_post.call_args
        # 投稿本文が正しいか
        assert call_args[0][0] == "Rendered Online Template Text"

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
        # 画像なしで投稿が成功するかのテスト
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Online No Image"
        mock_load_template_func.return_value = mock_template_obj

        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("user", "pass")
        with patch.dict(os.environ, {"BLUESKY_TEMPLATE_PATH": "templates/twitch_online_template.txt"}):
            result = poster.post_stream_online(
                event_context=mock_event_context_online, image_path=None
            )
        assert result is True
        mock_template_obj.render.assert_called_once_with(
            **mock_event_context_online, template_path="templates/twitch_online_template.txt")
        mock_client_instance.send_post.assert_called_once_with(
            "Rendered Online No Image", embed=None)
        mock_client_instance.upload_blob.assert_not_called()
        mock_write_history.assert_called_once()

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("bluesky.load_template")
    def test_post_stream_offline_success(
        self, mock_load_template_func, mock_write_history, mock_atproto_client_class,
        mock_env, mock_event_context_offline
    ):
        # 配信終了通知の投稿が成功するかのテスト
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Offline Template Text"
        mock_load_template_func.return_value = mock_template_obj

        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(
            event_context=mock_event_context_offline)

        assert result is True
        mock_client_instance.login.assert_called_once_with(
            "test_user", "test_pass")

        expected_template_path = os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH")
        mock_load_template_func.assert_called_once_with(
            path=expected_template_path)
        mock_template_obj.render.assert_called_once_with(
            **mock_event_context_offline, template_path=expected_template_path)

        mock_client_instance.send_post.assert_called_once_with(
            text="Rendered Offline Template Text")

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
        mock_env, mock_event_context_offline, caplog  # caplogでログを検証
    ):
        # テンプレートファイルが見つからない場合のエラーテンプレートの動作をテスト
        error_template_content = "Error: Template '{{ template_path }}' not found. Please check settings."
        mock_error_template_obj = Template(error_template_content)
        # フィルタを追加してエラーにならないようにする
        mock_error_template_obj.environment.filters['datetimeformat'] = MagicMock(
            return_value="FILTERED_DATE")

        mock_load_template_func.return_value = mock_error_template_obj

        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(
            event_context=mock_event_context_offline)

        assert result is True  # エラーメッセージでも投稿自体は成功扱い

        expected_template_path = os.getenv("BLUESKY_OFFLINE_TEMPLATE_PATH")
        expected_rendered_error_text = f"Error: Template '{expected_template_path}' not found. Please check settings."
        mock_client_instance.send_post.assert_called_once_with(
            text=expected_rendered_error_text)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_template_file_not_found_returns_error_template(self, mock_open_func, caplog, mock_env):
        # テンプレートファイルが存在しない場合のload_templateの動作をテスト
        non_existent_path = "path/to/nothing.txt"
        template_obj = load_template(path=non_existent_path)

        assert f"テンプレートファイルが見つかりません: {non_existent_path}" in caplog.text
        assert isinstance(template_obj, Template)
        rendered_error = template_obj.render(template_path=non_existent_path)
        assert f"Error: Template '{non_existent_path}' not found." in rendered_error

    @patch("builtins.open", side_effect=Exception("Some other read error"))
    def test_load_template_other_error_returns_error_template(self, mock_open_func, caplog, mock_env):
        # テンプレートファイル読み込み時のその他エラーのテスト
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
        # AtProtocolError発生時の動作をテスト
        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance
        mock_client_instance.send_post.side_effect = atproto_exceptions.AtProtocolError(
            "Test ATProto Error")

        poster = BlueskyPoster("test_user", "test_pass")
        result = poster.post_stream_offline(
            event_context=mock_event_context_offline)
        assert result is False
        mock_write_history.assert_called_once_with(
            title=ANY, category="Offline", url=ANY, success=False, event_type="offline"
        )

    @patch("bluesky.Client")
    @patch("bluesky.BlueskyPoster._write_post_history")
    @patch("os.path.isfile")
    @patch("bluesky.load_template")
    def test_upload_image_file_not_found_in_online_post(
        self, mock_load_template_func, mock_isfile, mock_write_history, mock_atproto_client_class,
        mock_env, mock_event_context_online, caplog
    ):
        # 画像ファイルが存在しない場合の動作をテスト
        mock_isfile.side_effect = lambda path: path == "templates/twitch_online_template.txt"

        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Online Text"
        mock_load_template_func.return_value = mock_template_obj

        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance

        poster = BlueskyPoster("user", "pass")
        with patch.dict(os.environ, {"BLUESKY_TEMPLATE_PATH": "templates/twitch_online_template.txt"}):
            result = poster.post_stream_online(
                event_context=mock_event_context_online,
                image_path="non_existent_image.png"
            )

        assert result is True  # 画像がなくても投稿自体は成功
        assert "指定された画像ファイルが見つかりません" in caplog.text
        mock_client_instance.upload_blob.assert_not_called()
        call_args = mock_client_instance.send_post.call_args
        assert call_args[1].get('embed') is None
        mock_write_history.assert_called_once()

    @patch("bluesky.Client")
    @patch("bluesky.load_template")
    def test_write_post_history_io_error(
        self, mock_load_template_func, mock_atproto_client_class, mock_env, caplog,
        mock_event_context_offline
    ):
        # _write_post_historyでIOErrorが発生した場合のログ出力をテスト
        mock_template_obj = MagicMock(spec=Template)
        mock_template_obj.render.return_value = "Rendered Offline Template Text"
        mock_load_template_func.return_value = mock_template_obj

        mock_client_instance = MagicMock()
        mock_atproto_client_class.return_value = mock_client_instance
        mock_client_instance.send_post.return_value = None

        poster = BlueskyPoster("user", "pass")

        # openを条件付きでモックし、CSV書き込み時のみIOErrorを発生させる
        original_open = open

        def conditional_mock_open(file, mode="r", **kwargs):
            if file == "logs/post_history.csv" and mode == "a":
                raise IOError("Test CSV write error")
            return mock_open()(file, mode, **kwargs)

        with patch("builtins.open", side_effect=conditional_mock_open) as mock_file_open_custom:
            poster.post_stream_offline(mock_event_context_offline)

        offline_template_path = os.getenv(
            "BLUESKY_OFFLINE_TEMPLATE_PATH", "templates/offline_template.txt")
        mock_load_template_func.assert_called_once_with(
            path=offline_template_path)

        # エラーログが出力されているか確認
        assert "投稿履歴CSVへの書き込みに失敗しました: logs/post_history.csv, エラー: Test CSV write error" in caplog.text
        assert "Test CSV write error" in caplog.text

        mock_client_instance.send_post.assert_called_once()

    def test_upload_image_actual_file_not_found(self, mock_env, caplog):
        # upload_imageでFileNotFoundErrorが発生した場合のテスト
        poster = BlueskyPoster("user", "pass")
        result_blob = poster.upload_image("path/to/truly_missing_image.png")
        assert result_blob is None
        assert "Bluesky画像アップロードエラー: ファイルが見つかりません - path/to/truly_missing_image.png" in caplog.text


def test_async_post_notification():
    """非同期通知投稿のテスト（同期関数として実行）"""
    from bluesky import BlueskyPoster

    with patch('bluesky.Client') as mock_client:
        mock_client.return_value.send_post = MagicMock(return_value=True)
        poster = BlueskyPoster(username="test", password="test")

        # 複数の投稿をシミュレート
        # 必須キーを含む event_context を渡す
        results = [
            poster.post_stream_online({
                "broadcaster_user_name": f"user{i}",
                "broadcaster_user_login": f"user{i}_login",
                "title": f"title{i}",
                "category_name": "Just Chatting",
                "stream_url": f"https://example.com/stream{i}"
            })
            for i in range(3)
        ]

        # すべての投稿が成功したことを確認
        assert all(results)
        assert mock_client.return_value.send_post.call_count == 3
