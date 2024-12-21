import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    DIRECTORY_TO_WATCH = "/home/ubuntu/bsm/test"
    LOG_FILE = "/home/ubuntu/bsm/logs/changes.json"

    def __init__(self):
        self.event_handler = Handler()
        self.observer = Observer()

    def run(self):
        self.observer.schedule(self.event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    last_event = {}

    def on_any_event(self, event):
        # Dizini filtrele
        if event.src_path == Watcher.DIRECTORY_TO_WATCH:
            return

        # Geçici dosyaları filtrele
        if event.src_path.endswith((".swp", "~", ".tmp")) or "/.goutputstream-" in event.src_path:
            return

        # Sadece belirli olay türlerini işle
        if event.event_type in ("created", "modified", "deleted"):
            current_time = time.time()

            # Aynı dosyada çok sık tetiklenen olayları filtrele
            if event.src_path in self.last_event:
                last_time, last_type = self.last_event[event.src_path]
                if event.event_type == "modified" and last_type == "created" and current_time - last_time < 1:
                    return  # 'created' olayından hemen sonra gelen 'modified' olayını atla

            self.last_event[event.src_path] = (current_time, event.event_type)

            print(f"Event detected: {event.event_type} on {event.src_path}")
            log_entry = {
                "event_type": event.event_type,
                "src_path": event.src_path,
                "time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(Watcher.LOG_FILE, "a") as log_file:
                log_file.write(json.dumps(log_entry) + "\n")



if __name__ == "__main__":
    watcher = Watcher()
    watcher.run()
