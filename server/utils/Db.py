import logging
import MySQLdb

class Db:
    
    def __init__(self):
        self.logger = logging.getLogger("Db")
    
    
    def getMySqlConnection(self):
        # read the database configuration -- this is ugly and cheap
        f = open('db.cfg', 'r')
        hostname = f.readline().strip()
        portno = int(f.readline().strip())
        userid = f.readline().strip()
        password = f.readline().strip()
        dbname = f.readline().strip()
        f.close()
        
        conn = None
        
        try:
            conn = MySQLdb.connect(host=hostname, port=portno,
                                   user=userid, passwd=password,
                                   db=dbname)
        except Exception, e:
            self.logger.error("Failed to connect to database: " + str(e))
        
        self.logger.debug("conn: " + str(conn))
                
        return conn