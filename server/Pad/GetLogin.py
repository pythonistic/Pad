#!/usr/bin/env python

# GET the content

import datetime
import logging
from utils.Authentication import Authentication
from utils.Db import Db
from simplejson import JSONDecoder
from simplejson import JSONEncoder


class GetLogin(object):

    def __init__(self):
        self.logger = logging.getLogger("GetLogin")
        db = Db()
        self.conn = db.getMySqlConnection()
        
        
    def invoke(self, apiParams, body=None, sessionId=None, requestHash=None):
        # API parameters
        self.logger.debug("apiParams: " + str(apiParams) + "  body: " + str(body))

        if body != None and len(body) > 1:
            # look for a session
            request = JSONDecoder().decode(body)
            if sessionId:
                # invalidate the session
                authentication = Authentication()
                authentication.invalidateSession(sessionId)

        output = {"results": "LOGIN"}
            
        return JSONEncoder().encode(output)

