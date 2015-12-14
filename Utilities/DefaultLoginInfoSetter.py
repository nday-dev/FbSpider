#--coding:utf-8--
import getpass
import keyring

n = int(raw_input("Number of Accounts: "))
keyring.set_password('FbSpider', 'Account', n)
for i in range(0, n):
    Email = raw_input("Email: ")
    keyring.set_password('FbSpider', 'Account' + str(i), Email)
    keyring.set_password('FbSpider', Email, getpass.getpass("Password: "))

