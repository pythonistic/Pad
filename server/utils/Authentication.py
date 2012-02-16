from datetime import datetime
import logging
import MySQLdb
import time
import hashlib
from utils.Db import Db
from utils.FailedLoginException import FailedLoginException


class Authentication(object):

    def __init__(self):
        self.logger = logging.getLogger("Authentication")
        db = Db()
        self.conn = db.getMySqlConnection()
        
    def isSessionActive(self, sessionId):
        if self.conn:
            cursor = self.conn.cursor()
            currentTime = time.strftime('%Y-%m-%d %H:%M:%S')
            sql = "select count(1) from sessions where id = %s and expire_time < %s"
            self.logger.debug("getting session: " + sql % (sessionId, currentTime))
            cursor.execute(sql, (sessionId, currentTime))
            results = cursor.fetchone()
            count = int(results[0])
            
            if count > 1:
                self.logger.warn("More than one session found with id %s and expire_time < %s" %
                                 (sessionId, currentTime))
            
            return count == 1
                
        else:
            self.logger.debug("Couldn't retrieve session -- no database connection")
            
    def invalidateSession(self, sessionId):
        if self.conn:
            expireTime = time.time().strftime('%Y-%m-%d %H:%M:%S')
            sql = "update sessions set expire_time = %s where id = %s"
            self.logger.debug("invalidate session " + sql % (expireTime, sessionId))
            cursor.execute(sql)        
            
    def login(self, username, passwordHash, clientHost, clientKey):
        self.logger.debug("logging in " + str(username))
        if self.conn:
            cursor = self.conn.cursor()
            currentTime = time.strftime('%Y-%m-%d %H:%M:%S')
            sql = "select userid from users where username=%s and password=%s"
            self.logger.debug("logging in user name %s: %s" % (username, sql))
            cursor.execute(sql, (username, passwordHash))
            results = cursor.fetchall()
            if len(results) > 1:
                self.logger.warn("More than one user found with username %s and password" %s (username))
            if len(results) > 0:                
                # successful login
                userId = int(results[0][0])
                
                # does the user already have a session?  (last two hours)
                sql = "select id from sessions where userid = %s and login_time >= (now() - 7200)"
                self.logger.debug("Does the user already have a session? " + sql % (userId))
                cursor.execute(sql, (userId))
                results = cursor.fetchall()
                if len(results) > 0:
                    idsToInvalidate = []
                    for result in results:
                        idsToInvalidate.append(result[0])
                    # invalidate the sessions
                    sql = "update sessions set expire_time = now() where id in (%s)"
                    idsList = ",".join(['%s'] * len(idsToInvalidate))
                    self.logger.debug("invalidating sessions with " + sql % (idsList))
                    cursor.execute(sql % idsList, tuple(idsToInvalidate))
                
                # create a session ID
                sessionTime = time.time()
                sessionId = hex(int(sessionTime * 10000000))[2:]
                
                # create a session expiration time (+2 hours)
                expireTimeSecs = sessionTime + 7200
                
                # format the session expiration time
                loginTime = datetime.fromtimestamp(sessionTime).strftime('%Y-%m-%d %H:%M:%S')
                expireTime = datetime.fromtimestamp(expireTimeSecs).strftime('%Y-%m-%d %H:%M:%S')
                
                # create a session key
                hasher = hashlib.sha1()
                hasher.update(sessionId + ":" + username + ":" + passwordHash + ":" + clientKey)
                sessionKey = hasher.hexdigest()
                
                # create the session
                sql = "insert into sessions (id, expire_time, userid, login_time, client_host, session_key, client_key) " + \
                      "values (%s, %s, %s, %s, %s, %s, %s)"
                self.logger.debug("creating session: " + sql % (sessionId, expireTime, userId, loginTime, clientHost, sessionKey, clientKey))
                cursor.execute(sql, (sessionId, expireTime, userId, loginTime, clientHost, sessionKey, clientKey))
                
                return (sessionId, sessionKey)
            else:
                # failed login
                raise FailedLoginException()
        else:
            self.logger("Couldn't log in -- no database connection")
            raise FailedLoginException()

    def loadSessionKeys(self, sessionId):
        sessionKey = None
        clientKey = None
        userId = None
        
        if sessionId and self.conn:
            cursor = self.conn.cursor()
            sql = "select userid, session_key, client_key from sessions where id = %s"
            self.logger.debug("Loading session keys: " + sql % (sessionId))
            cursor.execute(sql, (sessionId))
            results = cursor.fetchall()
            if len(results) > 1:
                self.logger.error("More than one session returned for ID " + str(sessionId))
            elif len(results) == 1:
                userId = results[0][0]
                sessionKey = results[0][1]
                clientKey = results[0][2]
                
        return (userId, sessionKey, clientKey)