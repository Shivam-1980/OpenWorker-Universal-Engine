import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

class WorkspaceEventHandler(FileSystemEventHandler):
    def __init__(self, websocket, loop):
        self.websocket = websocket
        self.loop = loop

    def broadcast_update(self):
        # Fire and forget WS message to trigger a UI File Explorer refresh
        asyncio.run_coroutine_threadsafe(
            self.websocket.send_text(json.dumps({"action": "refresh_tree"})),
            self.loop
        )

    def on_created(self, event):
        self.broadcast_update()

    def on_deleted(self, event):
        self.broadcast_update()

class DirectoryWatcher:
    def __init__(self, watch_path: str, websocket):
        self.watch_path = watch_path
        self.websocket = websocket
        self.observer = Observer()
        self.loop = asyncio.get_event_loop()

    def start(self):
        event_handler = WorkspaceEventHandler(self.websocket, self.loop)
        self.observer.schedule(event_handler, self.watch_path, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
