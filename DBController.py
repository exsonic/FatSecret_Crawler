'''
Created on 2013-4-29
@author: Bobi Pu, bobi.pu@usc.edu
'''

from pymongo import MongoClient
import sys

class DBController(object):
    def __init__(self):
        try:
            self.db = MongoClient().FatSecret
        except Exception as e:
            print e
            sys.exit()

    def loadUserListToDB(self, userListFileDir, removeDB=False):
        if removeDB:
            self.db.user.remove()
            self.db.groups.remove()
        with open(userListFileDir) as f:
            newUserId = 1
            for line in f.readlines():
                userName = line.strip()
                self.db.user.remove({'id': newUserId})
                self.db.user.insert({'id' : newUserId, 'name' : userName})
                newUserId += 1
    
    def getUserCount(self):
        return self.db.user.count()
                
    def getUserById(self, userId):
        return self.db.user.find_one({'id' : userId})
    
    def getUserByName(self, userName):
        return self.db.user.find_one({'name' : userName})
    
    def getAllUserList(self):
        return list(self.db.user.find())
    
    def addNewUser(self, userName):
        user = self.getUserByName(userName)
        if user is None:
            newUserId = self.db.user.count() + 1
            user = {'id' : newUserId, 'name' : userName}
            self.db.user.insert(user)
        return user
    
    def getAllGroupList(self):
        return list(self.db.groups.find())
    
    def getGroupById(self, groupId):
        return self.db.groups.find_one({'id' : groupId})
    
    def getGroupByName(self, groupName):
        return self.db.groups.find_one({'name' : groupName})
    
    def addNewGroup(self, groupName):
        group = self.getGroupByName(groupName)
        if group is None:
            newGroupId = self.db.groups.count() + 1
            group = {'id' : newGroupId, 'name' : groupName, 'member' : []}
            self.db.groups.insert(group)
        return group
    
    def addUserInGroup(self, userId, groupId):
        memberList = self.getGroupById(groupId)['member']
        if userId not in memberList:
            memberList.append(userId)
            self.db.groups.update({'id' : groupId}, {'$set' : {'member' : memberList}})

    def addGroupInUser(self, userId, groupIdList):
        user = self.getUserById(userId)
        if 'group' not in user:
            self.db.user.update({'id' : userId}, {'$set' : {'group' : groupIdList}})
        else:
            mergedGroupIdList = list(set(groupIdList + user['group']))
            self.db.user.update({'id' : userId}, {'$set' : {'group' : mergedGroupIdList}})

    def updateServerId(self, userId, serverId):
        self.db.user.update({'id' : userId} , {'$set': {'serverId' : serverId}})
    
    def getAllUserIter(self):
        return self.db.user.find()
    
    def updateWeightHistory(self, userId, diet, startWeight, goalWeight, weightHistory):
        self.db.user.update({'id' : userId}, {'$set' : {'diet' : diet, 'startWeight' : startWeight, 'goalWeight' : goalWeight, 'weightHistory' : weightHistory}})
    
    def updateDietHistory(self, userId, dietHistory):
        self.db.user.update({'id' : userId}, {'$set' : {'dietHistory' : dietHistory}})

    def getChallengeByName(self, challengeName):
        return self.db.challenge.find_one({'name' : challengeName})
    
    def getChallengeById(self, challengeId):
        return self.db.challenge.find_one({'id' : challengeId})
    
    def getAllChallengeList(self):
        return list(self.db.challenge.find())
    
    def addNewChallenge(self, challengeName):
        challenge = self.getChallengeByName(challengeName)
        if challenge is None:
            newChallengeId = self.db.challenge.count() + 1
            challenge = {'id' : newChallengeId, 'name' : challengeName, 'member' : []}
            self.db.challenge.insert(challenge)
        return challenge
    
    def addUserInChallenge(self, userId, challengeId):
        memberList = self.getChallengeById(challengeId)['member']
        if 'userId' not in memberList:
            memberList.append(userId)
            self.db.challenge.update({'id' : challengeId}, {'$set' : {'member' : memberList}})
    
    def addChallengeInUser(self, userId, challengeIdList):
        user = self.getUserById(userId)
        if 'challenge' not in user:
            self.db.user.update({'id' : userId}, {'$set' : {'challenge' : challengeIdList}})
        else:
            mergedChallengeIdList = list(set(challengeIdList + user['challenge']))
            self.db.user.update({'id' : userId}, {'$set' : {'challenge' : mergedChallengeIdList}})
    
    def addBuddyInUser(self, userId, buddyIdList):
        user = self.getUserById(userId)
        if 'buddy' not in user:
            self.db.user.update({'id' : userId}, {'$set' : {'buddy' : buddyIdList}})
        else:
            mergedBuddyList = list(set(buddyIdList + user['buddy']))
            self.db.user.update({'id' : userId}, {'$set' : {'buddy' : mergedBuddyList}})
        
    
if __name__ == '__main__':
    db = DBController()
    db.loadUserListToDB('userList_small.txt', True)    
    
    