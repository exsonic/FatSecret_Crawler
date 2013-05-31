'''
Created on 2013-5-1
@author: Bobi Pu, bobi.pu@usc.edu
'''
import logging, os

def initLog():
    logging.basicConfig(filename=os.path.join(os.getcwd(), 'log.txt'), level=logging.NOTSET, filemode='a', format='%(asctime)s - %(levelname)s: %(message)s')
    
def closeLog():
    logging.shutdown()

def logException(userId, functionName, e, info=''):
    msg = str(userId) + '\t' + functionName + '\t' + str(e) + '\t' + info
    print msg
    logging.error(msg)
    
def logInfo(userId, info):
    msg = str(userId) + '\t' + info
    print msg
    logging.info(msg)