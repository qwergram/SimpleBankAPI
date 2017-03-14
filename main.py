# Simple Account Balance Quick Access

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
}

class SimpleBank(object):
    
    targets = {
        "login": "https://bank.simple.com/signin",
        "balances": "https://bank.simple.com/txs-api/users/{}/accounts/primary/balances",
        "logout": "https://bank.simple.com/signout"
    }
    
    def __init__(self, username, password, session):
        self.session = session
        self.username = username
        self.password = password
        self.setCsrf()
        self.loggedIn = False
        
    def login(self):
        if not self.loggedIn:
            payload = self.createPayload()
            result = self.session.post(self.targets['login'], headers=HEADERS, data=payload)
            self.homepageContent = BeautifulSoup(result.text, "html5lib")
            self.loggedIn = True
        
    def logout(self):
        if self.loggedIn:
            self.session.get(self.targets["logout"], headers=HEADERS)
            self.loggedIn = False
    
    def getFeatureIdLink(self):
        datauuid = self.homepageContent.find("body")['data-uuid']
        return self.targets['balances'].format(datauuid)
               
    def getBalances(self):
        if self.loggedIn:
            link = self.getFeatureIdLink()
            balances = self.session.get(link, headers=HEADERS).json()
            for key, value in balances.items():
                balances[key] /= 10000
            return balances
        else:
            raise Exception("Not logged in!")
            
    def setCsrf(self):
        html_page = self.session.get(self.targets["login"]).text
        soup = BeautifulSoup(html_page, "html5lib")
        self.loginCsrf = soup.find('input', {"name": "_csrf"})['value']
        
    def createPayload(self):
        return {
            "username": self.username,
            "password": self.password,
            "_csrf": self.loginCsrf
        }

if __name__ == "__main__":
    session = requests.Session()
    SimpleAPI = SimpleBank("yourUsernameHere", "yourPasswordHere", session)
    SimpleAPI.login()
    balances = SimpleAPI.getBalances()
    SimpleAPI.logout()
    print(balances)
