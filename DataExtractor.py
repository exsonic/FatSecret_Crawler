'''
Created on 2013-4-8
@author: Bobi Pu, bobi.pu@usc.edu
'''
from DBController import DBController
from bs4 import BeautifulSoup, element
import re, cookielib
from FSLog import logException
from mechanize import Browser, _http
from dateutil import parser
from datetime import datetime


class DataExtractor(object):
    def __init__(self):
        self.db = DBController()
        self.br = self.login()
    
    def login(self):
        br = Browser()
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)
        
        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.set_handle_refresh(_http.HTTPRefreshProcessor(), max_time=2)
        
        br.open('http://www.fatsecret.com/Auth.aspx?pa=s')
        br.select_form(nr=0)
        #name attr of login tr 
        br['_ctl0:_ctl1:Logincontrol1:Name'] = 'exsonic'
        br['_ctl0:_ctl1:Logincontrol1:Password'] = 'pbbfs2012'
        br.submit()
        return br
    
    #========================================================================================
    # URLType: 0 memberURL, 1 weightHistory, 2 dietHistory, 3 groups, 4 challenges, 5 buddies
    #========================================================================================
    def getURL(self, user, URLType):
        if URLType == 0:
            return 'http://fatsecret.com/member/' + '+'.join(user['name'].encode('utf-8', 'ignore').split())
        if user['serverId'] is None:
            return None
        elif URLType == 1:
            return 'http://www.fatsecret.com/Default.aspx?pa=memh&id=' + user['serverId']
        elif URLType == 2:
            return 'http://www.fatsecret.com/Diary.aspx?pa=mdcs&id=' + user['serverId']
        elif URLType == 3:
            return 'http://www.fatsecret.com/Default.aspx?pa=memgrps&id=' + user['serverId']
        elif URLType == 4:
            return 'http://www.fatsecret.com/Default.aspx?pa=memchals&id=' + user['serverId']
        elif URLType == 5:
            return 'http://www.fatsecret.com/Default.aspx?pa=memb&id=' + user['serverId']
        else:
            raise Exception('invalid URL type')
        
    def convertUserIdToUserList(self, userId):
        if userId is None or userId == []:
            return self.db.getAllUserList()
        elif isinstance(userId, list) and userId != []:
            userList = []
            for v in userId:
                user = self.db.getUserById(v)
                if user is not None:
                    userList.append(user)
            return userList
        elif isinstance(userId, int):
            user = self.db.getUserById(userId)
            return [user] if user is not None else []
        else:
            raise Exception('invalid input userId')
            
    def getServerId(self, userId=None):
        users = self.convertUserIdToUserList(userId)
        for user in users:
            if 'serverId' in user and user['serverId'] is not None:
                continue
            serverId = None
            try:
                memberURL = self.getURL(user, 0)
                page = self.br.open(memberURL)
                soup = BeautifulSoup(page.read())
                result = soup.find('div', attrs={'align' : 'right', 'class' : 'smallText', 'style' : 'padding-top:5px'})
                if result is not None:
                    for tag in result.contents:
                        if isinstance(tag, element.Tag) and 'href' in tag.attrs and tag.attrs['href'].find('id') != -1:
                            serverId = tag.attrs['href'].split('id=')[1]
                            break     
            except Exception as e:
                logException(user['id'], self.getServerId.__name__, e)
            finally:      
                self.db.updateServerId(user['id'], serverId)
    
    def getWeightHistory(self, userId=None):
        users = self.convertUserIdToUserList(userId)
        for user in users:
            diet, startWeight, goalWeight, weightHistory = None, None, None, None
            try:
                if user['serverId'] is not None:
                    weightHistoryURL = self.getURL(user, 1)
                    page = self.br.open(weightHistoryURL)
                    soup = BeautifulSoup(page.read())
                    tag = soup.find('b')
                    diet = tag.contents[1].text
                    tag = soup.find(attrs={'style' : 'padding:0px 10px'})
                    startWeight = float(tag.contents[1].split(': ')[1].split()[0])
                    goalWeight = float(tag.contents[0].text.split(': ')[1].split()[0])
                    weightList, dateList = [], []
                    for tag in soup.findAll(attrs={'class' : 'borderBottom date'}):
                        dateList.append(parser.parse(tag.text))
                    for tag in soup.findAll(attrs={'class' : 'borderBottom weight'}):
                        weightList.append(float(tag.text.split()[0]))
                    weightHistory = zip(dateList, weightList)
                    weightHistory = sorted(weightHistory, key= lambda record : record[0])
            except Exception as e:
                logException(user['id'], self.getWeightHistory.__name__, e)
            finally:
                self.db.updateWeightHistory(user['id'], diet, startWeight, goalWeight, weightHistory)
    
    def getDietHistory(self, userId=None):
        users = self.convertUserIdToUserList(userId)
        for user in users:
            dietHistory = None
            try:
                if user['serverId'] is not None:
                    dietHistoryURL = self.getURL(user, 2)
                    page = self.br.open(dietHistoryURL)
                    soup = BeautifulSoup(page.read())
                    months = soup.findAll('td', attrs={'colspan' : '6', 'class' : 'borderBottom'})
                    monthList = []
                    if months == []:
                        raise Exception('no diet history records')
                    for month in months:
                        monthList.append(datetime.strptime(month.text, '%B %Y'))
                    rows = soup.findAll('tr', attrs={'valign' : 'middle'})
                    prevDay = 32
                    monthIndex = 0
                    dietHistory = []
                    for row in rows:
                        try:
                            if len(row.contents) != 13:
                                continue
                            day = int(re.sub('[^0-9]', '', row.contents[1].text))
                            if day >= prevDay:
                                monthIndex += 1 
                            prevDay = day
                            date = datetime(monthList[monthIndex].year, monthList[monthIndex].month, day)
                            food = self.getIntFromRawString(row.contents[3].text)
                            RDI = self.getDecimalFromPercentageString(row.contents[5].text)
                            fat, protein, carbs = self.getDataFromNutrionalSummary(row.contents[7].text)
                            exercise = self.getIntFromRawString(row.contents[9].text)
                            net = self.getIntFromRawString(row.contents[11].text)
                            dietHistory.append((date, food, RDI, fat, protein, carbs, exercise, net))
                        except Exception as e:
                            logException(user['id'], self.getDietHistory.__name__, e, 'scrape row error')
                    if 'dietHistory' in user and user['dietHistory'] is not None:
                        dietHistory = self.mergeDietTrack(user['dietHistory'], dietHistory)
                    else:
                        dietHistory.sort(key=lambda item : item[0])
            except Exception as e:
                logException(user['id'], self.getDietHistory.__name__, e)
            finally:
                self.db.updateDietHistory(user['id'], dietHistory)
    
    def getGroup(self, userId=None):
        users = self.convertUserIdToUserList(userId)
        for user in users:
            groupIdList = []
            try:
                if user['serverId'] is not None:
                    groupURL = self.getURL(user, 3)
                    page = self.br.open(groupURL)
                    soup = BeautifulSoup(page.read())
                    results = soup.findAll('td', attrs={'width' : '50', 'align' : 'center'})
                    for tag in results:
                        groupName =  tag.contents[1].attrs['title']
                        group = self.db.addNewGroup(groupName)
                        self.db.addUserInGroup(user['id'], group['id'])
                        groupIdList.append(group['id'])
            except Exception as e:
                logException(user['id'],self.getGroup. __name__, e)
            finally:
                self.db.addGroupInUser(user['id'], groupIdList)
    
    def getChallenge(self, userId=None):
        users = self.convertUserIdToUserList(userId)
        for user in users:
            challengeIdList = []
            try:
                if user['serverId'] is not None:
                    challengeURL = self.getURL(user, 4)
                    page = self.br.open(challengeURL)
                    soup = BeautifulSoup(page.read())
                    results = soup.findAll('td', attrs={'width' : '50', 'align' : 'center'})
                    for tag in results:
                        challengeName = tag.contents[1].attrs['title']
                        challenge = self.db.addNewChallenge(challengeName)
                        self.db.addUserInChallenge(user['id'], challenge['id'])
                        challengeIdList.append(challenge['id'])
            except Exception as e:
                logException(user['id'], self.getChallenge.__name__, e)
            finally:
                self.db.addChallengeInUser(user['id'], challengeIdList)
    
    def getBuddy(self, userId=None):
        users = self.convertUserIdToUserList(userId)
        for user in users:
            buddyIdList = []
            try:
                if user['serverId'] is not None:
                    buddyURL = self.getURL(user, 5)
                    while True:
                        page = self.br.open(buddyURL)
                        soup = BeautifulSoup(page.read())
                        results = soup.findAll('a', attrs={'class' : 'member', 'onmouseout' : 'hideTip()'})
                        for tag in results:
                            if tag.text != '':
                                buddyName = tag.text.strip()
                                buddy = self.db.addNewUser(buddyName)
                                buddyIdList.append(buddy['id'])
                                if 'serverId' not in buddy:
                                    self.getServerId(buddy['id'])
                        result = soup.find('span', attrs={'class' : 'next'})
                        if result is None:
                            break
                        else:
                            buddyURL = 'http://fatsecret.com/' + result.contents[0].attrs['href']
            except Exception as e:
                logException(user['id'], self.getBuddy.__name__, e)
            finally:
                self.db.addBuddyInUser(user['id'], buddyIdList)
    
    def mergeDietTrack(self, oldTrack, newTrack):
        oldTrack, newTrack = sorted(oldTrack, key= lambda item : item[0]), sorted(newTrack, key= lambda item: item[0])
        i = 0
        for item in oldTrack:
            if item[0] >= newTrack[0][0]:
                break
            i += 1
        return oldTrack[0 : i] + newTrack
    
    def cleanNonNumercial(self, dataString):
        return re.sub('[^0-9.]', '', dataString.strip())
    
    def getIntFromRawString(self, dataString):
        dataString = self.cleanNonNumercial(dataString)
        return int(dataString) if dataString != '' else None
    
    def getDataFromNutrionalSummary(self, dataString):
        if dataString.strip() == '':
            return None, None, None
        fat = float(dataString.split('fat: ')[1].split('g')[0])
        protein = float(dataString.split('protein: ')[1].split('g')[0])
        carbs = float(dataString.split('carbs: ')[1].split('g')[0])
        return fat, protein, carbs
    
    def getDecimalFromPercentageString(self, dataString):
        dataString = self.cleanNonNumercial(dataString)
        return float(self.cleanNonNumercial(dataString)) / 100 if dataString != '' else None
        
    
if __name__ == '__main__':
    de = DataExtractor()
    de.getServerId(34890)
    
    
    
    