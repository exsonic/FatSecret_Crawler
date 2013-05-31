'''
Created on 2013-5-7
@author: Bobi Pu, bobi.pu@usc.edu
'''

from argparse import ArgumentParser
from DataExporter import DataExporter

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-t', '--type', choices=['diet', 'weight', 'group', 'challenge', 'buddy', 'userGroup', 'userChallenge'], required=True, 
                        help='export data type, one of diet, weight, group, challenge, buddy, userGroup and userChallenge')
    exportType = parser.parse_args().type
    de = DataExporter()
    print 'Start to export....'
    if exportType == 'diet':
        de.exportHistory(isDietHistory=True)
    elif exportType == 'weight':
        de.exportHistory(isDietHistory=False)
    elif exportType == 'group':
        de.exportGroupChallenge(isGroup=True)
    elif exportType == 'challenge':
        de.exportGroupChallenge(isGroup=False)
    elif exportType == 'buddy':
        de.exportBuddy()
    elif exportType == 'userGroup':
        de.exportUserGroupChallenge(isGroup=True)
    elif exportType == 'userChallenge':
        de.exportUserGroupChallenge(isGroup=False)
    print 'Done!'