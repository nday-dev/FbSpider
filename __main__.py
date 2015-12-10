from __init__ import *
import json
import Queue

TaskQueue = Queue.Queue(maxsize = 0)

downloader = Downloader(TaskQueue)
extracter = InfoExtracter(json.load(open('RegularExpression.json')))

spider = Spider(TaskQueue, extracter, debug = False)

spider.Login(UsingSavedAccount = True, UsingSavedPass = True)
Output = open('result.json', 'wb')
Output.write('[')
spider.Scan('thelyad', idType = 'username', startindex = '0')
spider.Output(Output, spider.ContentMake())
Output.write(',')
spider.Scan('100000965387047', idType='uid', startindex = '0')
spider.Output(Output, spider.ContentMake())
Output.write(']')
