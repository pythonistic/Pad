# POST the changed notes
# Better with PUT?

import datetime
import logging
from simplejson import JSONDecoder
from simplejson import JSONEncoder
from utils.Db import Db
from utils.SessionValidator import SessionValidator


class PostCheckpoint(object):

    def __init__(self):
        self.logger = logging.getLogger("PostCheckpoint")
        db = Db()
        self.conn = db.getMySqlConnection()        
        
        
    def invoke(self, apiParams, body=None, sessionId=None, requestHash=None):
        # API parameters
        self.logger.debug("apiParams: " + str(apiParams) + "  body: " + str(body))
        if body == None or len(body) < 1:
            # fail
            return "No body"

        validator = SessionValidator(sessionId, requestHash)
        if self.conn:
            if validator.authenticateRequest(body):
                # decode the body
                self.logger.debug("body='" + str(body) + "'")
                message = JSONDecoder().decode(body)
                self.logger.debug("message='" + str(message) + "'")
                self.logger.debug("message length: " + str(len(message)))
                
                for note in message:
                    self.logger.debug("note='" + str(note) + "'")
                    self.logger.debug("type: " + str(type(note)))
                    self.logger.debug("keys: " + str(note.keys()))
                    self.logger.debug("note: " + note["top"] + " " + note["left"] + " " + note["height"] + " " + note["width"] + " " + note["id"] + " " + note["html"] + " " + str(note["zIndex"]))
        
                    cursor = self.conn.cursor()
                    sql = "select count(1) from notes where id='" + note['id'] + "'"
                    self.logger.debug("check note count: " + sql)
                    cursor.execute(sql)
                    results = cursor.fetchone()
                    self.logger.debug("note count: " + str(results))
                    count = int(results[0])
                    try:
                        if count > 0:
                            # update
                            #sql = """update notes set topPx=%s, leftPx=%s, heightPx=%s,
                            #         widthPx=%s, html=%s, zIndex=%s where id=%s"""
                            #cursor.execute(sql,
                            #               (note["top"], note["left"], note["height"],
                            #                note["width"], note["html"], note["id"],
                            #                note["zIndex"]))
                            sql = "delete from notes where id=%s" 
                            self.logger.debug("deleting note: " + sql)
                            cursor.execute(sql, (note['id']))
    
                        #else:
                        # insert
                        sql = """insert into notes (id, topPx, leftPx, heightPx,
                                 widthPx, html, zIndex) values (%s, %s, %s, %s, %s, %s, %s)"""
                        cursor.execute(sql,
                                       (note["id"], note["top"], note["left"], note["height"],
                                        note["width"], note["html"], note["zIndex"]))
                        self.logger.debug("writing note: " + sql)
                    except Exception, e:
                        self.logger.error("Couldn't write note: " + str(e))
            else:
                self.logger.debug("Couldn't update -- failed request validation")
                return '{"error": "Failed request validation"}'
        else:
            self.logger.debug("Couldn't update...no database connection")

        return '{"results": "OK}'
        #return JSONEncoder().encode([])

