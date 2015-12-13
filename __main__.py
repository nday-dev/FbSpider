from __init__ import *
import json
import Queue

Output = open('result.json', 'wb')
TaskQueue = Queue.Queue(maxsize = 0)

downloader = Downloader(TaskQueue)
downloader.start()

colony = Colony(Spider, InfoExtracter, 
        Output, TaskQueue, json.load(open('RegularExpression.json')), './Icon')

colony.Push(('thelyad', 'username', ))
colony.Push(('100000965387047', 'uid', ))
colony.SpiderInit()
try:
    print "Info: Start Colony.Manage()"
    colony.Manage()
finally:
    colony.End()
    downloader.stop()
