from __init__ import *
import Queue

TaskQueue = Queue.Queue(maxsize = 0)

downloader = Downloader(TaskQueue)

spider = Spider(TaskQueue, debug = False)

spider.Login()

spider.Scan('thelyad')
spider.Output(open('result.json', 'wb'), spider.ContentMake())
