#--coding:utf-8--
import re
import sys
import chardet

typeEncode = sys.getfilesystemencoding()

class InfoExtracter:

    def __init__(self, Colony, RegularExpression):

        self.Colony = Colony
        self.RegularExpression = RegularExpression

    def FileDownload(self, URL, path):
        self.DownloaderQueue.put((URL, path))

    def ReGet(self, RegularExpression, Content, group = 0):
        try:
            return re.search(RegularExpression, Content).group(group)
        except AttributeError:
            return 'N.A.'

    def UserInit(self, username, idType = 'username'):
        self.CurrentUser = username
        self.idType = idType
        self.PersonalInfo = {}
        self.Friends = []

    def InfoExtracter(self, content, RegularExpression):
        Info = {}
        for item in RegularExpression.iteritems():
            key, value = item
            if type(value) == str:
                Info[key] = self.ReGet(value, content, group = 1)
            elif type(value) == unicode:
                Info[key] = self.ReGet(value.encode(typeEncode), content, group = 1)
            elif type(value) == tuple or type(value) == list:
                context = re.findall(value[0], content)
                Info[key] = []
                for string in context:
                    Info[key].append(self.InfoExtracter(string, value[1]))
            elif type(value) == dict:
                try:
                    Info[key] = self.InfoExtracter(self.ReGet(value['InfoRange'], content, group = 1), {key: value['RegularExpression']})[key]
                except KeyError:
                    Info[key] = self.InfoExtracter(content, value)
            else:
                print item
                print "Error: InfoExtracter: Unexpected value type!"
                # raise AttributeError, "Unexpected value type!"
        return Info

    def ScanProfile(self, string):
        # Get Personal Info
        self.PersonalInfo = self.InfoExtracter(string, self.RegularExpression)

    def ScanFriendsProfile(self, string):
        # Get Friends Profile Info
        try:
            self.NumberOfFriends = int(re.search(r"好友（([\d]*) 位）", string).group(1))
        except AttributeError:
            print "Error: No Friends for this user!"
            # raise ValueError, "No Friends for this user!"
            self.NumberOfFriends = 0
            self.Download(self.UserPrefix + self.StartIndex, 'Err.html')

    def ScanFirstPage(self, string):
        # Specifically for First Page
        UserInfo = re.findall(r'<div class="w cc">(.*?)</div>', string)
        if len(UserInfo) == 0:
            print "Error: No UserInfo could be matched in this page!"
            # raise ValueError, "No UserInfo could be matched in this page!"

        for Info in UserInfo:
            user = {}
            user['UserName'] = self.ReGet(r'<a class="cd" href="/(.*?)\?fref=.*?">.*?</a>', Info, group = 1)
            user['UID'] = self.ReGet(r'<a class="cd" href="/profile.php\?id=(.*?)&amp;fref=.*?">', Info, group = 1)
            user['NickName'] = self.ReGet(r'<a class="cd".*?>(.*?)</a>', Info, group = 1)
            user['Description'] = self.ReGet(r'<span class="bx">(.*?)</span>', Info, group = 1)
            self.Friends.append(user)
        try:
            StartIndex = re.search(r'<a href=".*?startindex=([\d]*).*?"><span>更多</span></a>', string).group(1)
            return StartIndex
        except AttributeError:
            print "Info: All friends have been scanned for user: %s" %self.CurrentUser
            return None

    def ScanFriends(self, string, FirstPage = False):
        if FirstPage == True:
            return self.ScanFirstPage(string)

        # Read Friends List
        UserInfo = re.findall(r'<td class="w t">(.*?)</div><div class="bq">', string)
        if len(UserInfo) == 0:
            print "Error: No UserInfo could be matched in this page!"
            # raise ValueError, "No UserInfo could be matched in this page!"
        for Info in UserInfo:
            user = {}
            user['UserName'] = self.ReGet(r'<a class="bm" href="/(.*?)\?fref=.*?">', Info, group = 1)
            user['UID'] = self.ReGet(r'<a class="bm" href="/profile.php\?id=(.*?)&amp;fref=.*?">', Info, group = 1)
            user['NickName'] = self.ReGet(r'<a class="bm".*?>(.*?)</a>', Info, group = 1)
            user['Description'] = self.ReGet(r'<span class="bp">(.*?)</span>', Info, group = 1)
            self.Friends.append(user)
        try:
            StartIndex = re.search(r'<a href=".*?startindex=([\d]*).*?"><span>更多</span></a>', string).group(1)
            return StartIndex
        except AttributeError:
            print "Info: All friends have been scanned for user: %s" %self.CurrentUser
            return None

    def ContentMake(self):
        content = {}
        if self.idType == 'username':
            content['UserName'] = self.CurrentUser
            content['UID'] = 'N.A.'
        elif self.idType == 'uid':
            content['UserName'] = 'N.A.'
            content['UID'] = self.CurrentUser
        else:
            print "Error: Unknown User ID Type!"
            # raise AttributeError, "Unknown User ID Type!"
        content['PersonalInfo'] = self.PersonalInfo
        content['Friends'] = self.Friends
        return content
