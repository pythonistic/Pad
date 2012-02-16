# GET the content

import datetime
import logging
import GetLogin
from simplejson import JSONDecoder
from simplejson import JSONEncoder
from utils.Db import Db
from utils.SessionValidator import SessionValidator


class GetContent(object):

    def __init__(self):
        #self.repository = Repository.Repository("chats")
        self.logger = logging.getLogger("GetContent")
        db = Db()
        self.conn = db.getMySqlConnection()
        
        
    def invoke(self, apiParams, body="", sessionId=None, requestHash=None):
        # API parameters
        self.logger.debug("apiParams: " + str(apiParams) + "  body: " + str(body) + "  sessionId: " + str(sessionId) + "  requestHash: " + str(requestHash))

        if sessionId == None or len(sessionId) < 1:
            # fail
            loginHandler = GetLogin.GetLogin()
            return loginHandler.invoke(apiParams, body, sessionId, requestHash)

        notes = []
        output = {}

        # get the notes
        validator = SessionValidator(sessionId, requestHash)
        if self.conn:
            if validator.authenticateRequest(body, noBody = True):
                cursor = self.conn.cursor()
                sql = "select id, topPx, leftPx, heightPx, widthPx, html, zIndex from notes"
                self.logger.debug("getting notes: " + sql)
                cursor.execute(sql)
                results = cursor.fetchall()
                self.logger.debug("rows: " + str(results))
                for row in results:
                    self.logger.debug("row: " + str(row))
                    note = {}
                    note["id"] = row[0]
                    note["top"] = row[1]
                    note["left"] = row[2]
                    note["height"] = row[3]
                    note["width"] = row[4]
                    note["html"] = row[5]
                    note["zIndex"] = row[6]
                    notes.append(note)
                    self.logger.debug("note: " + str(note))
                self.logger.debug("retrieved " + str(len(notes)) + " notes")
                output["results"] = "OK"
                output["notes"] = notes
            else:
                self.logger.debug("Couldn't retrieve notes -- failed request validation")
                return '{"error": "Failed request validation"}'
        else:
            self.logger.debug("Couldn't retrieve notes -- no database connection")
            output["error"] = "No database connection"
            
        return JSONEncoder().encode(output)

