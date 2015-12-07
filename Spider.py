#--coding:utf-8--
import re
import sys
import time
import chardet
import getpass
import mechanize

typeEncode = sys.getfilesystemencoding()

class Spider:

    def __init__(self, DownloaderQueue, debug = False):

        self.DownloaderQueue = DownloaderQueue

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

    def Login(self, Email = None, Pass = None):
        self.br.open("http://m.facebook.com/")
        self.br.select_form(nr=0)
        #self.br['locale'] = 'en_US'
        #self.br['non_com_login'] = ''
        if (Email == None):
            self.br['email'] = raw_input('E-mail Address: ')
        else:
            self.br['email'] = Email
        if (Pass == None):
            self.br['pass'] = getpass.getpass('Password: ')
        else:
            self.br['pass'] = Pass
        #self.br['lsd'] = '20TO1'
        response = self.br.submit()

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
        content = self.br.open(URL).read()
        infoencode = chardet.detect(content).get('encoding', 'utf-8')
        return content.decode(infoencode, 'ignore').encode(typeEncode)

    def ReGet(RegularExpression, Content, group = 0):
        try:
            return re.search(RegularExpression, Content).group(group)
        except AttributeError:
            return 'N.A.'

    def UserInit(self, username, startindex = '0'):
        self.CurrentUser = username
        self.PersonalInfo = []
        self.HaveFriends = True
        self.StartIndex = startindex
        self.UserPrefix = self.Prefix + username + "/friends?all=1&startindex=" 
        self.Friends = []

    def Scan(self, username, startindex = '0'):
        self.UserInit(username, startindex)

        # Get Personal Info
        string = self.Load(self.Prefix + self.CurrentUser + '/')

        self.PersonalInfo.append({'NickName': self.ReGet(r'<div class="bi">.*?<strong class="br">(.*?)</strong>.*?</div>', string, group = 1)})
        self.PersonalInfo.append({'Gender': self.ReGet(r'<tr>.*?性别.*?<div class="dp">(.*?)</div>.*?</tr>', string, group = 1)})
        self.PersonalInfo.append({'UsingLanguage': self.ReGet(r'<tr>.*?使用语言.*?<div class="dp">(.*?)</div>.*?</tr>', string, group = 1)})

        # Get Friends Profile Info
        string = self.Load(self.UserPrefix + self.StartIndex)

        try:
            self.NumberOfFriends = int(re.search(r"好友（([\d]*) 位）", string).group(1))
        except AttributeError:
            self.NumberOfFriends = 0
            self.HaveFriends = False
            self.Download(self.UserPrefix + self.StartIndex, 'Err.html')

        # Read Friends List
        while (self.HaveFriends):
            string = self.Load(self.UserPrefix + self.StartIndex)
            UserInfo = re.findall(r'<div class="w cc">(.*?)</div>', string)
            for Info in UserInfo:
                user = {}
                user['UserName'] = self.ReGet(r'<a class="cd" href="/(.*?)\?fref=fr_tab">.*?</a>', string, group = 1)
                user['NickName'] = self.ReGet(r'<a class="cd".*?>(.*?)</a>', string, group = 1)
                user['Description'] = self.ReGet(r'<div class="ce cf"><span class="bx">(.*?)</span></div>', string, group = 1)
                self.Friends.append(user)
            try:
                self.StartIndex = re.search(r'<a href="/thelyad/friends\?all=1&amp;startindex=([\d]*?)"><span>更多</span></a>', string).group(1)
            except AttributeError:
                self.HaveFriends = False
                return self.Friends
            time.sleep(5)

    def ContentMake(self):
        content = []
        content.append({'UserName': self.CurrentUser})
        content.append({'PersonalInfo': self.PersonalInfo})
        content.append({'Friends': self.Friends})
        return content

    def Output(self, WriteHandle, content):
        WriteHandle.write(r'{')
        for element in content[:-1]:
            WriteHandle.write(r'"%s"' %element.keys()[0])
            if type(element.values()[0]) == type([]):
                self.Output(WriteHandle, element.values()[0])
            else:
                WriteHandle.write(r': "%r"; ' %element.values()[0])
        WriteHandle.write(r'}')
