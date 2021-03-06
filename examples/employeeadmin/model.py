"""
PureMVC Python Demo - wxPython Employee Admin 
By Toby de Havilland <toby.de.havilland@puremvc.org>
Copyright(c) 2007-08 Toby de Havilland, Some rights reserved.
Addapted for pyjamas: Kees Bos
"""

import puremvc.patterns.proxy
import consts, vo, EmployeeAdmin

class UserProxy(puremvc.patterns.proxy.Proxy):
    
    NAME = "UserProxy"
    def __init__(self):
        super(UserProxy, self).__init__(UserProxy.NAME, [])
        self.data = []
        self.addItem(vo.UserVO('lstooge','Larry', 'Stooge', "larry@stooges.com", 'ijk456',consts.DEPT_ACCT))
        self.addItem(vo.UserVO('cstooge','Curly', 'Stooge', "curly@stooges.com", 'xyz987',consts.DEPT_SALES))
        self.addItem(vo.UserVO('mstooge','Moe', 'Stooge', "moe@stooges.com", 'abc123',consts.DEPT_PLANT))

    def getUsers(self):
        return self.data
   
    def addItem(self, item):
        self.data.append(item)

    def updateItem(self, user):
        for i in range(0,len(self.data)):
            if self.data[i].username == user.username:
                self.data[i] = user
		break

    def deleteItem(self, user):
        for i in range(0,len(self.data)):
            if self.data[i].username == user.username:
                del self.data[i]
		break

class RoleProxy(puremvc.patterns.proxy.Proxy):

    NAME = "RoleProxy"
    def __init__(self):
        super(RoleProxy, self).__init__(RoleProxy.NAME, [])
        self.data = []
        self.addItem(vo.RoleVO('lstooge', [consts.ROLE_PAYROLL,consts.ROLE_EMP_BENEFITS]))
        self.addItem(vo.RoleVO('cstooge', [consts.ROLE_ACCT_PAY,consts.ROLE_ACCT_RCV,consts.ROLE_GEN_LEDGER]))
        self.addItem(vo.RoleVO('mstooge', [consts.ROLE_INVENTORY,consts.ROLE_PRODUCTION,consts.ROLE_SALES,consts.ROLE_SHIPPING]))

    def getRoles(self):
        print self.data
        return self.data

    def addItem(self, item):
        self.data.append(item)

    def deleteItem(self, item):
        for i in range(len(self.data)):
            if self.data[i].username == item.username:
                del self.data[i]
                break

    def doesUserHaveRole(self, user, role):
        hasRole = False;
        for i in range(len(self.data)):
            if self.data[i].username == user.username:
                userRoles = self.data[i].roles
                for j in range(len(userRoles)):
                    if userRoles[j] == role:
                        hasRole = True
                        break
        return hasRole

    def addRoleToUser(self, user, role):
        result = False;
        if not self.doesUserHaveRole(user, role):
            for i in range(0,len(self.data)):
                if self.data[i].username == user.username:
                    userRoles = self.data[i].roles
                    userRoles.append(role)
                    result = True;
                    break
        self.sendNotification(EmployeeAdmin.AppFacade.ADD_ROLE_RESULT, result)

    def removeRoleFromUser(self, user, role):
        if self.doesUserHaveRole(user, role):
            for i in range(0,len(self.data)):
                if self.data[i].username == user.username:
                    userRoles = self.data[i].roles
                    for j in range(0,len(userRoles)):
                        if userRoles[j] == role:
                            del userRoles[j]
                            break

    def getUserRoles(self, username):
        userRoles = []
        for i in range(0,len(self.data)):
            if self.data[i].username == username:
                userRoles = self.data[i].roles
                break
        return userRoles
