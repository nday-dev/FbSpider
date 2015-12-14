#--coding:utf-8--
from __init__ import *
import json
import Queue

RuntimeDataPrefix = './data.runtime/'
LibPrefix = './lib/'

open(RuntimeDataPrefix + 'Chinese.bak.json', 'ab').write('[')
open(RuntimeDataPrefix + 'Foreigner.bak.json', 'ab').write('[')
open(RuntimeDataPrefix + 'Student.bak.json', 'ab').write('[')

Output = open(RuntimeDataPrefix + 'result.json', 'wb')
TaskQueue = Queue.Queue(maxsize = 0)

downloader = Downloader(TaskQueue)
downloader.start()

separatorPath = {
    'Foreigner': RuntimeDataPrefix + 'Foreigner.bak.json',
    'Chineses': RuntimeDataPrefix + 'Chinese.bak.json',
    'Student': RuntimeDataPrefix + 'Student.bak.json'}

colony = Colony(Spider, InfoExtracter, 
        Output, TaskQueue, json.load(open(LibPrefix + 'RegularExpression.json')), json.load(open(LibPrefix + 'InfoExtractorRe.json')), 
            RuntimeDataPrefix + './Icon',
        HashTableBackup = RuntimeDataPrefix + 'Hash.bak.json', TaskQueueBackup = RuntimeDataPrefix + "Task.bak.json", SeparatorPath = separatorPath)

colony.SpiderInit()
try:
    print "Info: Start Colony.Manage()"
    colony.Manage()
except KeyboardInterrupt:
    pass
