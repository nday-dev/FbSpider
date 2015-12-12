from __init__ import *
import json
import Queue

Output = open('result.json', 'wb')
TaskQueue = Queue.Queue(maxsize = 0)

downloader = Downloader(TaskQueue)
colony = Colony(Spider, InfoExtracter, 
        Output, TaskQueue, json.load(open('RegularExpression.json')))

colony.Push(('thelyad', 'username', ))
colony.Push(('100000965387047', 'uid', ))
colony.SpiderInit()
colony.Manage()
colony = None

del colony
