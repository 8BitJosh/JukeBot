import time


class Users:
    def __init__(self):
        self.authUsers = {}

        self.adminLogins = ['63e780c3f321d13109c71bf81805476e']  # user,pass


    def isAdmin(self, session):
        if session in self.authUsers:
            return True
        return False


    def userLogin(self, passhash, session):
        if passhash in self.adminLogins:
            self.authUsers[session] = int(time.time())
            return True
        return False


    def removeOld(self):
        expireTime = int(time.time()) - 43200
        for key in list(self.authUsers):
            keyCreation = int(key.split('-')[-1])
            if (self.authUsers[key] < expireTime) or (keyCreation < expireTime):
                del self.authUsers[key]


    def isBlacklisted(self, session):
        pass
