import time
import json

class Users:
    def __init__(self):
        self.authUsers = {}
        self.adminLogin = []
        self.blacklisted = {}

        with open('config.json') as file:
            configfile = json.load(file)

        self.adminLogin.append(configfile['users']['pass'])
        self.blacklisted = configfile['blacklist']


    def isAdmin(self, session):
        # somewhere " " is added to the ends of the session cookie
        # this took me over an hour of my life to find and debug
        # this error only occurs on mobile devices, but this fix will do for now
        # session.strip('"')
        # most mobile browsers also create a cookie named session that would change 
        # this stopped my session tracker from working. The cookie is now named Jukebot

        if session.strip('"') in list(self.authUsers):
            return True
        return False


    def userLogin(self, passhash, session):
        if passhash in self.adminLogin:
            self.authUsers[session] = int(time.time())
            return True
        return False


    def userLogout(self, session):
        if session in self.authUsers:
            del self.authUsers[session]
            return True


    def updatePass(self, session, oldPasshash, newPasshash):
        if (oldPasshash in self.adminLogin) and (session in self.authUsers):
            self.adminLogin[0] = newPasshash
            
            with open('config.json', 'r') as file:
                Tosave = json.load(file)
        
            Tosave['users']['pass'] = self.adminLogin[0]

            with open('config.json', 'w') as file:
                json.dump(Tosave, file, indent="\t")
        else:
            return False


    def removeOld(self):
        expireTime = int(time.time()) - 43200
        for key in list(self.authUsers):
            keyCreation = int(key.split('-')[-1])
            if (self.authUsers[key] < expireTime) or (keyCreation < expireTime):
                del self.authUsers[key]


    def isBlacklisted(self, session):
        pass


    def addBlacklist(self, session):
        pass


    def removeBlacklist(self, session):
        pass