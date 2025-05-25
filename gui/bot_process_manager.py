"""
ボットプロセス管理（main.py等の起動・停止・監視）
"""
import subprocess
import threading
import sys
import os
import signal


class BotProcessManager:
    def __init__(self, main_py_path="main.py", on_status_change=None):
        # main.pyの絶対パスを取得
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))
        self.main_py_path = os.path.join(project_root, main_py_path)
        self.process = None
        self.stdout = ""
        self.stderr = ""
        self._stdout_thread = None
        self._stderr_thread = None
        self.running = False
        self.project_root = project_root
        self.on_status_change = on_status_change

    def start(self):
        if self.running:
            return
        if self.on_status_change:
            self.on_status_change("starting")
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        self.process = subprocess.Popen(
            [sys.executable, self.main_py_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
            cwd=self.project_root,
            creationflags=creationflags
        )
        self.running = True
        self._stdout_thread = threading.Thread(
            target=self._read_stdout, daemon=True)
        self._stderr_thread = threading.Thread(
            target=self._read_stderr, daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()
        if self.on_status_change:
            self.on_status_change("running")

    def stop(self):
        if self.process and self.running:
            if self.on_status_change:
                self.on_status_change("stopping")

            def _stop_proc():
                try:
                    # Windows: SIGINT (Ctrl+C) を送信してgraceful shutdownを促す
                    if os.name == 'nt':
                        self.process.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        self.process.send_signal(signal.SIGINT)
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
                except Exception as e:
                    print(f"プロセス停止時に例外: {e}")
                    if self.on_status_change:
                        self.on_status_change("error")
                finally:
                    # stdout/stderrスレッドもjoinしてクリーンアップ
                    if self._stdout_thread:
                        self._stdout_thread.join(timeout=2)
                    if self._stderr_thread:
                        self._stderr_thread.join(timeout=2)
                    self.running = False
                    self.process = None
                    if self.on_status_change:
                        self.on_status_change("stopped")
            # 停止処理は別スレッドで実行し、GUIフリーズを防ぐ
            threading.Thread(target=_stop_proc, daemon=True).start()

    def restart(self):
        if self.on_status_change:
            self.on_status_change("restarting")
        self.stop()
        self.start()
        # running状態はstartで通知

    def _read_stdout(self):
        for line in self.process.stdout:
            self.stdout += line

    def _read_stderr(self):
        for line in self.process.stderr:
            # Decode with error handling to avoid UnicodeDecodeError
            self.stderr += line.decode("utf-8", errors="replace")

    def get_stdout(self):
        return self.stdout

    def get_stderr(self):
        return self.stderr

    def is_running(self):
        return self.running and self.process and self.process.poll() is None
