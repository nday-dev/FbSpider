import sys
import chardet
import getpass
import mechanize

typeEncode = sys.getfilesystemencoding()

#Browser
br = mechanize.Browser()
cookies = mechanize.CookieJar()

#options
br.set_handle_robots(False)

#Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

#debugging?
br.set_debug_http(True)
br.set_debug_redirects(True)
br.set_debug_responses(True)
#User-Agent (this is cheating, ok?)

br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

br.open("http://m.facebook.com/")
br.select_form(nr=0)
#br['locale'] = 'en_US'
#br['non_com_login'] = ''
br['email'] = raw_input('E-mail Address: ')
br['pass'] = getpass.getpass('Password: ')
#br['lsd'] = '20TO1'
response = br.submit()

content = br.open("https://m.facebook.com/thelyad/friends").read()
infoencode = chardet.detect(content).get('encoding','utf-8')
A = content.decode(infoencode,'ignore').encode(typeEncode)
f = open('test.html','w')
f.write(A)
f.close()
