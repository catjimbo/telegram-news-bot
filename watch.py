import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.restart_script()

    def restart_script(self):
        if self.process:
            print("Перезапуск бота...")
            self.process.terminate()
            self.process.wait()
        print("Запуск бота...")
        venv_python = 0
        self.process = subprocess.Popen([venv_python, self.script])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self.restart_script()

if __name__ == "__main__":
    path = "."
    script = "bot.py"
    event_handler = ReloadHandler(script)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()

    print(f"Слежение за изменениями в {path} запущено. Ctrl+C для выхода.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()
