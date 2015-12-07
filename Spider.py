#--coding:utf-8--
import re
import sys
import time
import chardet
import getpass
import mechanize

typeEncode = sys.getfilesystemencoding()

class Spider():

    def __init__(self, debug = False):

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

    def UserInit(self, username, startindex = '0'):
        self.CurrentUser = username
        self.HaveFriends = True
        self.NumberOfFriends = 0
        self.StartIndex = startindex
        self.UserPrefix = self.Prefix + username + "/friends?all=1&startindex=" 
        self.Friends = []

    def Scan(self, username, startindex = '0'):
        self.UserInit(username, startindex)
        string = self.Load(self.UserPrefix + self.StartIndex)

        try:
            self.NumberOfFriends = int(re.search(r"好友（([\d]*) 位）", string).group(1))
        except AttributeError:
            self.NumberOfFriends = 0
            self.HaveFriends = False
            self.Download(self.UserPrefix + self.StartIndex, 'Err.html')

        while (self.HaveFriends):
            string = self.Load(self.UserPrefix + self.StartIndex)
            UserInfo = re.findall(r'<div class="w cc">(.*?)</div>', string)
            for Info in UserInfo:
                user = {}
                user['UserName'] = re.search(r'<a class="cd" href="/(.*?)\?fref=fr_tab">.*?</a>', string).group(1)
                user['NickName'] = re.search(r'<a class="cd".*?>(.*?)</a>', string).group(1)
                user['Location'] = re.search(r'<div class="ce cf"><span class="bx">(.*?)</span></div>', string).group(1)
                self.Friends.append(user)
            try:
                self.StartIndex = re.search(r'<a href="/thelyad/friends\?all=1&amp;startindex=([\d]*?)"><span>更多</span></a>', string).group(1)
            except AttributeError:
                self.HaveFriends = False
                return self.Friends

            time.sleep(5)

    def Output(self, WriteHandle, content):
        WriteHandle.write(r'{'UserName':'%s',



spider = Spider(debug = False)

spider.Login()

spider.Scan('thelyad')
