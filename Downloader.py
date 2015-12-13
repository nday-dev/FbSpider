#--coding:utf-8--
import os
import threading

class Downloader(threading.Thread):
    def __init__(self, TaskQueue):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.TaskQueue = TaskQueue
        self.thread_stop = False
        print "Info: Downloader Initialized!"

    def run(self):
        while True:
            try:
                URL, path = self.TaskQueue.get(True)
                os.system("wget -q -O '%s' '%s'" %(path, URL))
                print "Info: Download: ", path
            except ValueError:
                break

    def stop(self):
        print "Info: Exit Downloader"
        self.thread_stop = True
