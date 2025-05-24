"""
ボットプロセス管理（main.py等の起動・停止・監視）
"""
import subprocess
import threading
import sys


class BotProcessManager:
    def __init__(self, main_py_path="main.py"):
        self.main_py_path = main_py_path
        self.process = None
        self.stdout = ""
        self.stderr = ""
        self._stdout_thread = None
        self._stderr_thread = None
        self.running = False

    def start(self):
        if self.running:
            return
        self.process = subprocess.Popen(
            [sys.executable, self.main_py_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.running = True
        self._stdout_thread = threading.Thread(
            target=self._read_stdout, daemon=True)
        self._stderr_thread = threading.Thread(
            target=self._read_stderr, daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()

    def stop(self):
        if self.process and self.running:
            self.process.terminate()
            self.process.wait(timeout=10)
            self.running = False

    def restart(self):
        self.stop()
        self.start()

    def _read_stdout(self):
        for line in self.process.stdout:
            self.stdout += line

    def _read_stderr(self):
        for line in self.process.stderr:
            self.stderr += line

    def get_stdout(self):
        return self.stdout

    def get_stderr(self):
        return self.stderr

    def is_running(self):
        return self.running and self.process and self.process.poll() is None
