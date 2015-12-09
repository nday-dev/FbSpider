from __init__ import *
import Queue

TaskQueue = Queue.Queue(maxsize = 0)

downloader = Downloader(TaskQueue)

spider = Spider(TaskQueue, debug = False)

spider.Login()
Output = open('result.json', 'wb')
Output.write('[')
spider.Scan('thelyad', idType = 'username', startindex = '0')
spider.Output(Output, spider.ContentMake())
Output.write(',')
spider.Scan('100001117121252', idType='uid', startindex = '0')
spider.Output(Output, spider.ContentMake())
Output.write(']')
