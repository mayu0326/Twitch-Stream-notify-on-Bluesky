# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky

このモジュールはTwitch/YouTube/Niconicoの放送と動画投稿の通知をBlueskyに送信するBotの一部です。
"""
import logging  # caplog.set_level用
import pytest
import os
import pytz  # pytzのインポート
from unittest.mock import patch, MagicMock  # patchの追加
from utils import (
    update_env_file_preserve_comments,
    rotate_secret_if_needed,
    format_datetime_filter  # format_datetime_filterの追加
)
from version_info import __version__

__author__ = "mayuneco(mayunya)"
__copyright__ = "Copyright (C) 2025 mayuneco(mayunya)"
__license__ = "GPLv2"
__app_version__ = __version__


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


# settings.envのテスト用パス
TEST_ENV_PATH = "test_settings.env"


@pytest.fixture
def env_file():
    # テスト用の settings.env を作成
    with open(TEST_ENV_PATH, "w", encoding='utf-8') as f:
        f.write("# これはコメントです\n")
        f.write("KEY1=VALUE1\n")
        f.write("\n")  # 空行
        f.write("KEY2=VALUE2 # インラインコメント\n")
    yield TEST_ENV_PATH
    # テスト後にファイルを削除
    os.remove(TEST_ENV_PATH)


def test_update_env_file_preserve_comments_existing_key(env_file):
    updates = {"KEY1": "NEW_VALUE1"}
    update_env_file_preserve_comments(env_file, updates)
    with open(env_file, "r", encoding='utf-8') as f:
        lines = f.readlines()
    assert lines[0] == "# これはコメントです\n"
    assert lines[1] == "KEY1=NEW_VALUE1\n"
    assert lines[2] == "\n"
    assert lines[3] == "KEY2=VALUE2 # インラインコメント\n"


def test_update_env_file_preserve_comments_new_key(env_file):
    updates = {"KEY3": "VALUE3"}
    update_env_file_preserve_comments(env_file, updates)
    with open(env_file, "r", encoding='utf-8') as f:
        lines = f.readlines()
    # KEY3が末尾に追加されていることを確認
    assert "KEY3=VALUE3\n" in lines
    # 元の行が保持されていることを確認
    assert "# これはコメントです\n" in lines
    assert "KEY1=VALUE1\n" in lines


def test_update_env_file_preserve_comments_multiple_updates(env_file):
    updates = {"KEY1": "UPDATED_K1", "KEY_NEW": "NEW_K_VAL"}
    update_env_file_preserve_comments(env_file, updates)
    with open(env_file, "r", encoding='utf-8') as f:
        content = f.read()
    assert "KEY1=UPDATED_K1\n" in content
    assert "KEY_NEW=NEW_K_VAL\n" in content
    assert "KEY2=VALUE2 # インラインコメント\n" in content  # 元のkey2も保持されている


@pytest.fixture
def mock_env_for_rotate(monkeypatch, env_file):
    # rotate_secret_if_needed 内の SETTINGS_ENV_PATH をテスト用パスに差し替え
    monkeypatch.setattr("utils.SETTINGS_ENV_PATH", env_file)
    # read_env と update_env_file_preserve_comments はそのままテスト対象の関数を使う
    # generate_secretはテストメソッド内で直接モック
    # os.getenv for TIMEZONE
    # テストの一貫性のためデフォルトはUTC
    monkeypatch.setenv("TIMEZONE", "UTC")
    return env_file


# utilsモジュールの中でsecrets.token_hexをモック
@patch('utils.secrets.token_hex')
def test_rotate_secret_if_needed_no_secret(mock_secrets_token_hex, mock_env_for_rotate, caplog):
    # モックを設定して静的な値を返す
    mock_secrets_token_hex.return_value = "mocked_secret_key_123"

    # caplogでINFOレベルのログを取得
    caplog.set_level(logging.INFO, logger="AppLogger")
    caplog.set_level(logging.INFO, logger="AuditLogger")

    # settings.env に SECRET_KEY_NAME がない状態
    with open(mock_env_for_rotate, "w", encoding='utf-8') as f:
        # WEBHOOK_SECRETが存在しないことを保証
        f.write("OTHER_KEY=some_value\n")

    # テスト対象関数を呼び出し
    new_secret = rotate_secret_if_needed(force=False)

    # 関数がモック値を返すことを確認
    assert new_secret == "mocked_secret_key_123"

    # secrets.token_hexが1回呼ばれていることを確認
    mock_secrets_token_hex.assert_called_once_with(32)

    # .envファイルの内容を確認
    with open(mock_env_for_rotate, "r", encoding='utf-8') as f:
        content = f.read()
    assert "WEBHOOK_SECRET=mocked_secret_key_123" in content
    assert "SECRET_LAST_ROTATED=" in content  # last rotatedも設定されている

    # ログメッセージを確認
    assert "WEBHOOK_SECRETが見つからないため、新規生成します。" in caplog.text


# utilsモジュールの中でsecrets.token_hexをモック
@patch('utils.secrets.token_hex')
def test_rotate_secret_if_needed_no_secret(mock_secrets_token_hex, mock_env_for_rotate, caplog):
    # モックを設定して静的な値を返す
    mock_secrets_token_hex.return_value = "mocked_secret_key_123"

    # caplogでINFOレベルのログを取得
    caplog.set_level(logging.INFO, logger="AppLogger")
    caplog.set_level(logging.INFO, logger="AuditLogger")


# このテストでもsecrets.token_hexをモック
@patch('utils.secrets.token_hex')
def test_rotate_secret_if_needed_force_rotation(
        mock_secrets_token_hex, mock_env_for_rotate, caplog):
    mock_secrets_token_hex.return_value = "mocked_secret_key_123"  # モック値

    # caplogでINFOレベルのログを取得
    caplog.set_level(logging.INFO, logger="AppLogger")
    caplog.set_level(logging.INFO, logger="AuditLogger")

    with open(mock_env_for_rotate, "w", encoding='utf-8') as f:
        f.write("WEBHOOK_SECRET=old_secret\n")
        # ダミーの古い日付
        f.write("SECRET_LAST_ROTATED=2023-01-01T00:00:00+00:00\n")

    new_secret = rotate_secret_if_needed(force=True)  # 強制ローテーション

    assert new_secret == "mocked_secret_key_123"
    mock_secrets_token_hex.assert_called_once_with(32)

    with open(mock_env_for_rotate, "r", encoding='utf-8') as f:
        content = f.read()
    assert "WEBHOOK_SECRET=mocked_secret_key_123" in content
    # ローテーションが行われたことを示すログ
    assert "WEBHOOK_SECRETを自動生成・ローテーションしました" in caplog.text


class TestFormatDateTimeFilter:
    def test_basic_formatting_default_utc(self, monkeypatch):
        monkeypatch.setenv("TIMEZONE", "UTC")
        iso_str = "2023-10-27T10:00:00Z"
        # デフォルトフォーマットは "%Y-%m-%d %H:%M %Z"
        # TIMEZONEがUTCなので、%ZはUTC（または環境によっては空文字列）
        formatted_str = format_datetime_filter(iso_str)
        assert "2023-10-27 10:00" in formatted_str
        # UTCの場合、%Zは"UTC"または空文字列。もし"UTC"なら末尾がUTCであることを確認
        if "UTC" in formatted_str:
            assert formatted_str.endswith("UTC")
        elif formatted_str.strip().endswith("0000"):  # 一部のstrftime実装では+0000
            assert "2023-10-27 10:00:00 UTC" or "2023-10-27 10:00:00 +0000"

    def test_custom_formatting(self, monkeypatch):
        # フォーマット指定のテスト
        monkeypatch.setenv("TIMEZONE", "UTC")
        iso_str = "2023-10-27T10:30:45Z"
        custom_fmt = "%H時%M分"
        assert format_datetime_filter(iso_str, fmt=custom_fmt) == "10時30分"

    def test_timezone_conapp_version_tokyo(self, monkeypatch):
        monkeypatch.setenv("TIMEZONE", "Asia/Tokyo")
        iso_str_utc = "2023-10-27T00:00:00Z"  # UTCの深夜
        # 期待値: 2023-10-27 09:00 JST（または+0900、Asia/Tokyoなど）
        result = format_datetime_filter(iso_str_utc)
        assert "2023-10-27 09:00" in result
        assert "JST" in result or "+0900" in result or "Asia/Tokyo" in result

    def test_timezone_conapp_version_new_york(self, monkeypatch):
        monkeypatch.setenv("TIMEZONE", "America/New_York")
        iso_str_utc = "2023-10-27T10:00:00Z"  # 10時UTC
        # 期待値: 2023-10-27 06:00 EDT（DST期間中）
        result = format_datetime_filter(iso_str_utc)
        assert "06:00" in result  # 10時UTCはEDTで6時
        assert "EDT" in result or "-0400" in result or "America/New_York" in result

    def test_system_timezone(self, monkeypatch):
        # システムタイムゾーンのテスト（実行環境依存なのでget_localzoneをモック）
        mock_local_tz = MagicMock()
        mock_local_tz.zone = "Europe/London"  # 例としてロンドン

        with patch('utils.get_localzone', return_value=pytz.timezone("Europe/London")):
            monkeypatch.setenv("TIMEZONE", "system")
            iso_str_utc = "2023-10-27T10:00:00Z"
            # 期待値: 2023-10-27 11:00 BST（DST期間中）
            result = format_datetime_filter(iso_str_utc)
            assert "11:00" in result
            assert "BST" in result or "+0100" in result or "Europe/London" in result

    def test_invalid_inputs_for_filter(self, monkeypatch):
        # 無効な入力値のテスト
        monkeypatch.setenv("TIMEZONE", "UTC")
        assert format_datetime_filter(None) == ""  # Noneの場合は空文字
        assert format_datetime_filter("") == ""    # 空文字の場合も空文字

        malformed_date = "not-a-date-string"
        # エラー時は元の文字列を返す
        assert format_datetime_filter(malformed_date) == malformed_date

        # fromisoformatでパースできるがZ形式でない場合
        non_z_iso = "2023-10-27T10:00:00+05:00"
        # UTCに変換されるので05:00が含まれる
        assert "05:00" in format_datetime_filter(non_z_iso)

    def test_unknown_timezone_fallback(self, monkeypatch, caplog):
        monkeypatch.setenv("TIMEZONE", "Mars/OlympusMons")  # 存在しないタイムゾーン
        iso_str = "2023-10-27T10:00:00Z"
        # UTCにフォールバックすることを期待
        result = format_datetime_filter(iso_str)
        assert "設定のタイムゾーン 'Mars/OlympusMons' が不明です。UTCにフォールバックします。" in caplog.text
        assert "2023-10-27 10:00" in result
        if "UTC" in result:
            assert result.endswith("UTC")

    def test_get_localzone_returns_none(self, monkeypatch, caplog):
        monkeypatch.setenv("TIMEZONE", "system")
        with patch('utils.get_localzone', return_value=None):
            iso_str = "2023-10-27T10:00:00Z"
            result = format_datetime_filter(iso_str)
        assert "tzlocal.get_localzone()がNoneを返しました。UTCにフォールバックします。" in caplog.text
        assert "2023-10-27 10:00" in result
        if "UTC" in result:
            assert result.endswith("UTC")

    def test_get_localzone_raises_exception(self, monkeypatch, caplog):
        monkeypatch.setenv("TIMEZONE", "system")
        with patch('utils.get_localzone', side_effect=Exception("tzlocal failed")):
            iso_str = "2023-10-27T10:00:00Z"
            result = format_datetime_filter(iso_str)
        assert "tzlocalでシステムタイムゾーン取得エラー: tzlocal failed。UTCにフォールバックします。" in caplog.text
        assert "2023-10-27 10:00" in result
        if "UTC" in result:
            assert result.endswith("UTC")


# pytestの警告抑制: mark.asyncio
pytestmark = pytest.mark.filterwarnings(
    r"ignore:Unknown pytest\.mark\.asyncio",
)


@pytest.mark.parametrize("retry_count,expected_calls", [
    (1, 1),  # 初回成功
    (2, 2),  # 1回失敗後成功
    (3, 3),  # 2回失敗後成功
])
def test_retry_mechanism(retry_count, expected_calls):
    """リトライメカニズムのテスト"""
    from utils import retry_on_exception as retry_decorator

    # テスト用の失敗カウンター
    failure_count = 0

    @retry_decorator(max_retries=3, wait_seconds=0.1)
    def test_function():
        nonlocal failure_count
        if failure_count < retry_count - 1:
            failure_count += 1
            raise Exception("Temporary failure")
        return "Success"

    result = test_function()
    assert result == "Success"
    assert failure_count == retry_count - 1
