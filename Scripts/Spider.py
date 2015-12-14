#--coding:utf-8--
import re
import sys
import json
import time
import chardet
import getpass
import keyring
import mechanize

# typeEncode = sys.getfilesystemencoding()
typeEncode = 'utf-8'

class Spider:

    def __init__(self, DownloaderQueue, InfoExtractor, debug = False):

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

        # Info Extractor
        self.Extractor = InfoExtractor

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
        print "Info: Load Page. URL: %s" %URL
        content = ''
        try:
            content = self.br.open(URL).read()
        except mechanize.URLError, Info:
            print "Error: mechanize._mechanize.LinkNotFoundError ", Info
            return ''

        infoencode = chardet.detect(content).get('encoding', 'utf-8')
        return content.decode(infoencode, 'ignore').encode(typeEncode)

    def UserInit(self, username, idType = 'username', startindex = '0'):
        self.CurrentUser = username
        self.idType = idType
        self.StartIndex = startindex
        self.UserPrefix = ''
        self.FriendsPrefix = ''
        if (idType == 'username'):
            self.UserPrefix = self.Prefix
            self.FriendsPrefix = self.UserPrefix + self.CurrentUser + "/friends?all=1&startindex=" 
        elif (idType == 'uid'):
            self.UserPrefix = self.Prefix + 'profile.php?id='
            self.FriendsPrefix = self.UserPrefix + self.CurrentUser + '&v=friends&all=1&startindex='
        else:
            print "Error: Unknown User Identification Type!"

    def Scan(self, username, idType = 'username', startindex = '0'):
        startindex = str(startindex)
        self.UserInit(username, idType = idType, startindex = startindex)
        self.Extractor.UserInit(username = username, idType = idType)

        # Get Personal Info
        string = self.Load(self.Prefix + self.CurrentUser + '/')
        Flag = self.Extractor.ScanProfile(string)

        # Get Friends Profile Info
        if (Flag):
            string = self.Load(self.UserPrefix + self.StartIndex)

            Flag = self.Extractor.ScanFriendsProfile(string)

        # Read Friends List
        while (Flag):
            print "Info: Sleep: 5 Sec"
            time.sleep(5)
            if (self.StartIndex != 'N.A.'):
                string = self.Load(self.FriendsPrefix + self.StartIndex)
            else:
                return

            self.StartIndex = self.Extractor.ScanFriends(string)

    def Output(self, WriteHandle):
        json.dump(self.Extractor.ContentMake(), WriteHandle)
        print "Info: Output User: ", self.CurrentUser, ', ', self.idType
