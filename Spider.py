#--coding:utf-8--
import re
import sys
import json
import time
import chardet
import getpass
import keyring
import mechanize

typeEncode = sys.getfilesystemencoding()

class Spider:

    def __init__(self, DownloaderQueue, debug = False):

        self.DownloaderQueue = DownloaderQueue
        self.RegularExpression = json.load(open('RegularExpression.json'))

        self.Prefix = "https://m.facebook.com/"

        #Browser
        self.br = mechanize.Browser()
        self.cookies = mechanize.CookieJar()

        #options
        self.br.set_handle_robots(False)

        #Follows refresh 0 but not hangs on refresh > 0
        self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        #debugging?
        self.br.set_debug_http(debug)
        self.br.set_debug_redirects(debug)
        self.br.set_debug_responses(debug)

        #User-Agent (this is cheating, ok?)

        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    def Login(self, Email = None, Pass = None, UsingSavedAccount = False, UsingSavedPass = False):
        self.br.open("http://m.facebook.com/")
        self.br.select_form(nr=0)
        #self.br['locale'] = 'en_US'
        #self.br['non_com_login'] = ''
        if (Email != None):
            self.br['email'] = Email
        elif UsingSavedAccount:
            self.br['email'] = keyring.get_password('FbSpider', 'Account')
        else:
            self.br['email'] = raw_input('E-mail Address: ')

        if (Pass != None):
            self.br['pass'] = Pass
        elif UsingSavedPass:
            self.br['pass'] = keyring.get_password('FbSpider', self.br['email'])
        else:
            self.br['pass'] = getpass.getpass('Password: ')
        #self.br['lsd'] = '20TO1'
        response = self.br.submit()
        if (self.Load(self.Prefix).find('个人主页')) > 0:
            print "Info: Login Success!"
        else:
            print "Warning: Login Insuccess"

    def FileDownload(self, URL, path):
        self.DownloaderQueue.put((URL, path))

    def Download(self, URL, path):
        content = self.br.open(URL).read()
        infoencode = chardet.detect(content).get('encoding','utf-8')
        A = content.decode(infoencode,'ignore').encode(typeEncode)
        f = open(path,'w')
        f.write(A)
        f.close()
   
    def Load(self, URL):
        print "URL = %s" %URL
        content = ''
        try:
            content = self.br.open(URL).read()
        except mechanize._mechanize.LinkNotFoundError, Info:
            print "Error: mechanize._mechanize.LinkNotFoundError ", Info
            return ''

        infoencode = chardet.detect(content).get('encoding', 'utf-8')
        return content.decode(infoencode, 'ignore').encode(typeEncode)

    def ReGet(self, RegularExpression, Content, group = 0):
        try:
            return re.search(RegularExpression, Content).group(group)
        except AttributeError:
            return 'N.A.'

    def UserInit(self, username, idType = 'username', startindex = '0'):
        self.CurrentUser = username
        self.idType = idType
        self.HaveFriends = True
        self.StartIndex = startindex
        self.UserPrefix = ''
        if (idType == 'username'):
            self.UserPrefix = self.Prefix + username + "/friends?all=1&startindex=" 
        elif (idType == 'uid'):
            self.UserPrefix = self.Prefix + 'profile.php?v=friends&all=1&id=' + self.CurrentUser + '&startindex='
        else:
            print "Error: Unknown User Identification Type!"
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
        return Info

    def Scan(self, username, idType = 'username', startindex = '0'):
        startindex = str(startindex)
        self.UserInit(username, idType = idType, startindex = startindex)

        # Get Personal Info
        string = self.Load(self.Prefix + self.CurrentUser + '/')
        self.PersonalInfo = self.InfoExtracter(string, self.RegularExpression)

        # Get Friends Profile Info
        string = self.Load(self.UserPrefix + self.StartIndex)

        try:
            self.NumberOfFriends = int(re.search(r"好友（([\d]*) 位）", string).group(1))
        except AttributeError:
            print "Error: No Friends for this user!"
            self.NumberOfFriends = 0
            self.HaveFriends = False
            self.Download(self.UserPrefix + self.StartIndex, 'Err.html')

        # Specifically for First Page
        UserInfo = re.findall(r'<div class="w cc">(.*?)</div>', string)
        if len(UserInfo) == 0:
            print "Error: No UserInfo could be matched in this page!"
            print "URL: %s" %(self.UserPrefix + self.StartIndex)

        for Info in UserInfo:
            user = {}
            user['UserName'] = self.ReGet(r'<a class="cd" href="/(.*?)\?fref=.*?">.*?</a>', Info, group = 1)
            user['UID'] = self.ReGet(r'<a class="cd" href="/profile.php\?id=(.*?)&amp;fref=.*?">', Info, group = 1)
            user['NickName'] = self.ReGet(r'<a class="cd".*?>(.*?)</a>', Info, group = 1)
            user['Description'] = self.ReGet(r'<span class="bx">(.*?)</span>', Info, group = 1)
            self.Friends.append(user)
        try:
            self.StartIndex = re.search(r'<a href=".*?startindex=([\d]*).*?"><span>更多</span></a>', string).group(1)
        except AttributeError:
            print "Info: All friends have been scanned for user: %s" %self.CurrentUser
            self.HaveFriends = False
            return self.Friends
        print "Info: Sleep: 5 Sec"
        time.sleep(5)

       # Read Friends List
        while (self.HaveFriends):
            string = self.Load(self.UserPrefix + self.StartIndex)

            UserInfo = re.findall(r'<td class="w t">(.*?)</div><div class="bq">', string)
            if len(UserInfo) == 0:
                print "Error: No UserInfo could be matched in this page!"
                print "URL: %s" %(self.UserPrefix + self.StartIndex)
            for Info in UserInfo:
                user = {}
                user['UserName'] = self.ReGet(r'<a class="bm" href="/(.*?)\?fref=.*?">', Info, group = 1)
                user['UID'] = self.ReGet(r'<a class="bm" href="/profile.php\?id=(.*?)&amp;fref=.*?">', Info, group = 1)
                user['NickName'] = self.ReGet(r'<a class="bm".*?>(.*?)</a>', Info, group = 1)
                user['Description'] = self.ReGet(r'<span class="bp">(.*?)</span>', Info, group = 1)
                self.Friends.append(user)
            try:
                self.StartIndex = re.search(r'<a href=".*?startindex=([\d]*).*?"><span>更多</span></a>', string).group(1)
            except AttributeError:
                print "Info: All friends have been scanned for user: %s" %self.CurrentUser
                self.HaveFriends = False
                return self.Friends
            print "Info: Sleep: 5 Sec"
            time.sleep(5)

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
        content['PersonalInfo'] = self.PersonalInfo
        content['Friends'] = self.Friends
        return content

    def Output(self, WriteHandle, content):
        json.dump(content, WriteHandle)
