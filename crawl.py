'''
Created on 2013-5-1
@author: Bobi Pu, bobi.pu@usc.edu
'''
from CrawlerThread import CrawlerThread
from FSLog import initLog, closeLog
import threading
from argparse import ArgumentParser
from DBController import DBController 

if __name__ == '__main__':
    db = DBController()
    userCount = db.getUserCount() if db.getUserCount() is not None else 0
    parser = ArgumentParser()
    parser.add_argument('-s', '--startid', type=int, required=True, help='start crawling userId, start from 1')
    parser.add_argument('-e', '--endid', type=int, default=userCount, help='end crawling userId, start from 1')
    args = parser.parse_args()
    startId, endId = args.startid, args.endid
    
    if startId is None or startId < 1 or startId > endId:
        print 'Invalid Argument, please use -h to check argument'
    else:
        initLog()
        for userId in range(startId, endId + 1):
            while threading.activeCount() >= 100:
                pass
            crawler = CrawlerThread(userId)
            crawler.start()
        closeLog()