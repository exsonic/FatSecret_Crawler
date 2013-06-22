"""
Created on 2013-4-10
@author: Bobi Pu, bobi.pu@usc.edu
"""

from DBController import DBController
from datetime import datetime
import os

class DataExporter(object):
    def __init__(self):
        self.db = DBController()
    
    def valueToCSVFormat(self, value):
        if value == '' or value is None:
            return ''
        elif isinstance(value, str) or isinstance(value, unicode):
            return '\"' + value.encode('utf-8', 'ignore') + '\"'
        elif isinstance(value, int) or isinstance(value, float):
            return str(value)
        elif isinstance(value, datetime):
            return datetime.strftime(value, '%Y-%m-%d')
        else:
            raise Exception('Value data type ERROR, must be string, int, float or datetime')
        
    def exportHistory(self, isDietHistory):
        if isDietHistory:
            key = 'dietHistory'
            fileName = key + '.csv'
            attributeLine = 'id,name,count,lastUpdateDate,updateTime,food,RDI,fat,protein,carbs,exercise,net\n'
        else:
            key = 'weightHistory'
            fileName = key + '.csv'
            attributeLine = 'id,name,count,lastUpdateDate,lastUpdateWeight,startWeight,goalWeight,updateTime,weight\n'
        
        with open(fileName, 'w') as f:
            f.write(attributeLine)
            users = self.db.getAllUserList()
            users = sorted(users, key=lambda user : user['id'])
            for user in users:
                lineList = [user['id'], user['name']]
                try:
                    if key in user and user[key] is not None and len(user[key]) > 0:
                        lineList.append(len(user[key]))
                        lineList.append(user[key][-1][0])
                        if not isDietHistory:
                            lineList.append(user[key][-1][1])
                            lineList.append(user['startWeight'])
                            lineList.append(user['goalWeight'])
                        for detailInfoTuple in user[key]:
                            lineList.extend(detailInfoTuple)                            
                    else:
                        
                        lineList.append(0)
                    line = ','.join([self.valueToCSVFormat(value) for value in lineList]) + '\n'
                    f.write(line)
                except Exception as e:
                    print e, user['id']
    
    def exportGroupChallenge(self, isGroup):
        items = self.db.getAllGroupList() if isGroup else self.db.getAllChallengeList()
        items = sorted(items, key=lambda item : item['id'])
        fileName = 'group.csv' if isGroup else 'challenge.csv'
        with open(fileName, 'w') as f:
            f.write('id,name,count,memberId\n')
            for item in items:
                lineList = [item['id'], item['name']]
                if 'member' in item and item['member'] is not None:
                    lineList.append(len(item['member']))
                    lineList.extend(item['member'])
                else:
                    lineList.append(0)
                line = ','.join([self.valueToCSVFormat(value) for value in lineList]) + '\n'
                f.write(line)
    
#     def exportUserGroupChallenge(self, isGroup):
#         users = self.db.getAllUserIter()
#         directory = 'userGroup/' if isGroup else 'userChallenge/'
#         key = 'group' if isGroup else 'challenge'
#         if not os.path.exists(directory):
#             os.mkdir(directory)
#         for user in users:
#             fileName = directory + str(user['id']) + '.txt'
#             if key in user and user[key] is not None:
#                 with open(fileName, 'w') as f:
#                     itemList = sorted(user[key])
#                     for itemId in itemList:
#                         line = str(itemId) + '\n'
#                         f.write(line)
#             else:
#                 with open(fileName, 'w') as f:
#                     pass

    def exportUserGroupChallenge(self, isGroup):
        key = 'group' if isGroup else 'challenge'
        fileName = 'userGroup.csv' if isGroup else 'userChallenge.csv'
        attributeLine = 'id,count,group\n' if isGroup else 'id,count,challenge\n'
        with open(fileName, 'w') as f:
            users = self.db.getAllUserList()
            users = sorted(users, key=lambda user : user['id'])
            f.write(attributeLine)
            for user in users:
                lineList = [user['id']]
                if key in user and user[key] is not None:
                    lineList.append(len(user[key])) 
                    lineList.extend(user[key])
                else:
                    lineList.append(0)
                line = ','.join([self.valueToCSVFormat(value) for value in lineList]) + '\n'
                f.write(line)
    
    def exportBuddy(self):
        users = self.db.getAllUserIter()
        if not os.path.exists('buddy/'):
            os.mkdir('buddy/')
        for user in users:
            fileName = 'buddy/' + str(user['id']) + '.txt'
            if 'buddy' in user and user['buddy'] is not None:
                with open(fileName, 'w') as f:
                    buddyIdList = sorted(user['buddy'])
                    for userId in buddyIdList:
                        line = str(user['id']) + ' ' + str(userId) + '\n'
                        f.write(line)
            else:
                with open(fileName, 'w') as f:
                    pass

    def getUserIdNameDict(self):
        users = self.db.getAllUserIter()
        userIdNameDict = {}
        for user in users:
            userIdNameDict[user['id']] = user['name']
        return userIdNameDict
