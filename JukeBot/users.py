import time
import json

class Users:
    def __init__(self):
        self.authUsers = {}
        self.adminLogin = []
        self.blacklisted = {}
        self.connected = []

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
            return True
        return False


    def removeOld(self):
        expireTime = int(time.time()) - 43200
        for key in list(self.authUsers):
            if (self.authUsers[key] < expireTime):
                del self.authUsers[key]


    def userConnect(self, sid, session, ip):
        for user in self.connected:
            if user.session == session:
                user.sid = sid
                user.ip = ip
                return
        self.connected.append(User(session, sid, ip))


    def getSidSession(self, sid):
        for user in list(self.connected):
            if user.sid == sid:
                return user.session
        return None


    def isSidAdmin(self, sid):
        for user in list(self.connected):
            if (user.sid == sid) and (user.session in self.authUsers):
                return True
        return False


    def getSidName(self, sid):
        for user in list(self.connected):
            if user.sid == sid:
                return user.ip
        return None


    def isBlacklisted(self, session):
        if session in self.blacklisted:
            return True
        return False


    def addBlacklist(self, session):
        self.blacklisted['session'] = int(time.time())
        self.saveBlacklist()


    def removeBlacklist(self, session):
        del self.blacklisted[session]
        self.saveBlacklist()


    def saveBlacklist(self):
        with open('config.json', 'r') as file:
            Tosave = json.load(file)
        
        Tosave['blacklist'] = self.blacklisted

        with open('config.json', 'w') as file:
            json.dump(Tosave, file, indent="\t")


class User:
    def __init__(self, session, sid, ip):
        self.session = session
        self.sid = sid
        self.ip = ip