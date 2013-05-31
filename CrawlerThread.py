'''
Created on 2013-5-1
@author: Bobi Pu, bobi.pu@usc.edu
'''
from threading import Thread
from DataExtractor import DataExtractor
from FSLog import logInfo, logException

class CrawlerThread(Thread):
    def __init__(self, userId):
        super(CrawlerThread, self).__init__()
        self.userId = userId
    
    def run(self):
        try:
            logInfo(self.userId, 'start crawling')
            de = DataExtractor()
            de.getServerId(self.userId)
            de.getWeightHistory(self.userId)
            de.getDietHistory(self.userId)
            de.getGroup(self.userId)
            de.getChallenge(self.userId)
            de.getBuddy(self.userId)
            logInfo(self.userId, 'Done crawling')
        except Exception as e:
            logException(self.userId, self.run.__name__, e)