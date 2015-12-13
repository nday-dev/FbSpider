import json
import Queue

class Colony:

    def __init__(self, SpiderClass, ExtracterClass, 
            WriteHandle, DownloadQueue, RegularExpression, IconFolder, 
            HashTableBackup = 'Hash.bak.json', TaskQueueBackup = 'Task.bak.json', debug = False):

        self.Spider = SpiderClass
        self.Extracter = ExtracterClass

        self.WriteHandle = WriteHandle
        self.DownloadQueue = DownloadQueue
        self.RegularExpression = RegularExpression
        self.IconFolder = IconFolder

        self.HashTableBackup = HashTableBackup
        self.TaskQueueBackup = TaskQueueBackup
        self.DebugMode = debug

        try:
            input = open(self.HashTableBackup, 'rb')
            self.Hash = json.load(input)
            input.close()
        except IOError:
            self.Hash = {}
        self.TaskQueue = Queue.Queue(maxsize = 0)
        try:
            input = open(self.TaskQueueBackup, 'rb')
            Q = json.load(input)
            input.close()
            for task in Q:
                self.TaskQueue.put(task)
        except:
            pass
        self.SpiderQueue = Queue.Queue(maxsize = 0)

        self.WriteHandle.write('[')

    def __del__(self):
        self.End()

    def End(self):
        output = open(self.HashTableBackup, 'wb')
        json.dump(self.Hash, output)
        output.close()
        output = open(self.TaskQueueBackup, 'wb')
        Q = []
        while not self.TaskQueue.empty():
            Q.append(self.TaskQueue.get())
        json.dump(Q, output)
        output.close()

        print "Info: Destroy Colony"
        self.WriteHandle.write(']')


    def Download(self, arg):
        self.DownloadQueue.put(arg)

    def SpiderInit(self):
        Spider = self.Spider(self.TaskQueue, self.ExtracterInit(), self.DebugMode)
        Spider.Login(UsingSavedAccount = True, UsingSavedPass = True)
        self.SpiderQueue.put(Spider)

    def ExtracterInit(self):
        return self.Extracter(self, self.RegularExpression, self.IconFolder)

    def Push(self, Identity):
        identity = '%s, %s' %(Identity[0], Identity[1])
        if not self.Hash.has_key(identity):
            self.Hash[identity] = True
            self.TaskQueue.put(Identity)
            return True
        return False

    def Manage(self):
        Flag = ''
        while not self.TaskQueue.empty():
            Task = self.TaskQueue.get()
            print "Info: Current Task: ", Task
            Spider = self.SpiderQueue.get()
            Spider.Scan(Task[0], Task[1]) # Task should be a tuple object, with [0]: user identity; [1]: idType
            self.WriteHandle.write(Flag)
            Flag = ','
            Spider.Output(self.WriteHandle)
            self.SpiderQueue.put(Spider)
