#!/usr/bin/env python

# POST the login submission

import datetime
import logging
from utils.Authentication import Authentication
from utils.Db import Db
from utils.FailedLoginException import FailedLoginException
from simplejson import JSONDecoder
from simplejson import JSONEncoder


class PostLogin(object):

    def __init__(self):
        self.logger = logging.getLogger("PostLogin")
        db = Db()
        self.conn = db.getMySqlConnection()
        
        
    def invoke(self, apiParams, body=None, sessionId=None, requestHash=None):
        # API parameters
        self.logger.debug("apiParams: " + str(apiParams) + "  body: " + str(body))
        
        results = {}

        if body != None and len(body) > 1:
            if self.conn:
                cursor = self.conn.cursor()
            
                # look for a current session (before login)
                if sessionId:
                    # invalidate the session
                    expireTime = db.getDatetime()
                    sql = "update sessions set expire_time = %s where id = %i"
                    self.logger.debug("invalidate session sql %s %s %i", sql, expireTime, sessionId)
                    cursor.execute(sql)
            
                # look for a client key, username, password
                request = JSONDecoder().decode(body)
                if "clientKey" in request and \
                   "username" in request and \
                   "password" in request:
                    # verify the login request
                    authentication = Authentication()
                    
                    try:
                        (newSessionId, newSessionKey) = authentication.login(request["username"], request["password"], "", request["clientKey"])
                        results["results"] = "OK"
                        results["sessionId"] = newSessionId
                        results["sessionKey"] = newSessionKey
                    except FailedLoginException:
                        results["results"] = "FAILED"
                else:
                    # missing keys
                    results["results"] = "FAILED"

            else:
                self.logger.debug("Couldn't process login:  no database connection")
                results["results"] = "FAILED"

        return JSONEncoder().encode(results)

