import json
import Queue

class Colony:

    def __init__(self, HashTable = 'Hash.bak.json', SpiderClass, initargs):
        self.spider = SpiderClass(initargs)
        self.HashTableBackup = HashTable
        try:
            input = open(self.HashTableBackup, 'rb')
            self.Hash = json.load(input)
            input.close()
        except IOError:
            self.Hash = {}
        self.TaskQueue = Queue.Queue(maxsize = 0)

    def __del__(self):
        output = open(HashTableBackup, 'wb')
        json.dump(self.Hash, output)
        output.close()

    def Push(self, Identity):
        self.URLQueue.put(Identity)

    def Manage(self):
        while True:
            Task = self.TaskQueue.get()
