import getpass
import keyring

Email = raw_input("Email: ")
keyring.set_password('FbSpider', 'Account', Email)
keyring.set_password('FbSpider', Email, getpass.getpass("Password: "))

