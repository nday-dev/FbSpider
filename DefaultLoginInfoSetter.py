import getpass
import keyring

Email = raw_input("Email: ")
keyring.set_pass('FbSpider', 'Account', Email)
keyring.set_pass('FbSpider', Email, getpass.getpass("Password: "))

