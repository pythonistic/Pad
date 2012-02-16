# DELETE the content

import datetime
import logging
from utils.Db import Db
from utils.SessionValidator import SessionValidator
from simplejson import JSONDecoder
from simplejson import JSONEncoder

class DeleteDelete(object):

    def __init__(self):
        self.logger = logging.getLogger("DeleteDelete")
        db = Db()
        self.conn = db.getMySqlConnection()
        
        
    def invoke(self, apiParams, body=None, sessionId=None, requestHash=None):
        # API parameters
        self.logger.debug("apiParams: " + str(apiParams) + "  body: " + str(body))
        #if body == None or len(body) < 1:
        #    # fail
        #    return "No body"

        if len(apiParams) < 1:
            return '{"error": "Missing content ID"}'
        
        if len(body) < 1:
            return '{"error": "Missing request body"}'
        
        contentId = apiParams[0]

        # get the notes
        validator = SessionValidator(sessionId, requestHash)
        if self.conn:
            if validator.authenticateRequest(body):
                cursor = self.conn.cursor()
                sql = "delete from notes where id=%s" 
                self.logger.debug("deleting note: " + sql % (contentId))
                cursor.execute(sql, (contentId))
            else:
                self.logger.debug("Couldn't delete note -- failed request validation")
                return '{"error": "Failed request validation"}'
        else:
            self.logger.debug("Couldn't delete note -- no database connection")
            
        return '{"results": "OK"}'

