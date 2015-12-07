import os
import threading

class Downloader(threading.Thread):
    def __init__(self, TaskQueue):
        threading.Thread.__init__(self)
        self.TaskQueue = TaskQueue

    def run(self):
        while True:
            try:
                URL, path = self.TaskQueue.get(True)
                os.system("wget '%s' -O '%s'" %(URL, path))
            except ValueError:
                break
