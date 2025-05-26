# -*- coding: utf-8 -*-
"""
Stream notify on Bluesky - Tunnel Tests
"""
import pytest
from unittest.mock import patch, MagicMock
import subprocess
import signal
from tunnel import start_tunnel, stop_tunnel, TunnelError

@pytest.fixture
def mock_cloudflared():
    with patch('tunnel.subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # プロセスが実行中を示す
        mock_popen.return_value = mock_process
        yield mock_process

def test_tunnel_start_success(mock_cloudflared):
    # トンネル開始の正常系テスト
    with patch('tunnel.TUNNEL_CMD', 'cloudflared tunnel --config config.yml'):
        start_tunnel()
        mock_cloudflared.assert_called_once_with(
            ['cloudflared', 'tunnel', '--config', 'config.yml'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

def test_tunnel_start_failure(mock_cloudflared):
    # トンネル開始の異常系テスト
    mock_cloudflared.side_effect = subprocess.SubprocessError()
    
    with pytest.raises(TunnelError) as exc_info:
        with patch('tunnel.TUNNEL_CMD', 'cloudflared tunnel --config config.yml'):
            start_tunnel()
    
    assert "トンネルの開始に失敗しました" in str(exc_info.value)

def test_tunnel_stop_success(mock_cloudflared):
    # トンネル停止の正常系テスト
    stop_tunnel()
    mock_cloudflared.terminate.assert_called_once()
    mock_cloudflared.wait.assert_called_once()

def test_tunnel_stop_force_kill(mock_cloudflared):
    # 通常の終了が失敗した場合のフォースキルテスト
    mock_cloudflared.terminate.side_effect = ProcessLookupError()
    
    stop_tunnel()
    mock_cloudflared.kill.assert_called_once()