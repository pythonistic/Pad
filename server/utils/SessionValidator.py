import logging
import random
import re
import time
from simplejson import JSONDecoder
from simplejson import JSONEncoder
from utils.Authentication import Authentication

class SessionValidator(object):
    
    def __init__(self, sessionId, requestHash):
        self.TABLE_SIZE = 128000
        self.logger = logging.getLogger("SessionValidator")
        self.sessionId = sessionId
        self.requestHash = requestHash
        self.ARBITRARY_HASH_KEY = [
            0xb8f1, 0x18d9, 0xad80, 0xd9a9, 0xe901, 0x257b, 0x5e07, 0x1a31,
            0x70b7, 0x01fd, 0x6080, 0x1cf0, 0x0a15, 0xe16a, 0xa731, 0x8a80,
            0x73ba, 0x1bf0, 0x24e2, 0x7406, 0x660c, 0x1dcd, 0xdba5, 0xc05c,
            0x40c9, 0xcbb4, 0xeb68, 0xc294, 0x3a4b, 0xbf43, 0x904d, 0xffbf,
            0x27a3, 0xfac0, 0x11fe, 0x3e56, 0xb82b, 0x0007, 0xdfe7, 0xe3c0,
            0x183a, 0x46df, 0x515a, 0x46e5, 0xde80, 0x2e11, 0xe95d, 0xf870]

        self.HASH_OUT = [
            0x2c88, 0xc801, 0x14c0, 0x5886, 0x214f, 0x3b8e]
        
    def simpleHash(self, source, size):
        hash = 0
        i = 0
        for ch in source:
            i += 1
            hash += ord(ch) * i
  
        return abs(hash) % size;
        
    def passwordHash(self, source):
        hashOut = ""
        lastHash = 1
        hashIdx = len(source)
        hashOut = self.HASH_OUT[:]
        sHashOut = ""
        idx = 0

        """
          for (var i = 0; i < source.length; i++) {
            var hashKey = ARBITRARY_HASH_KEY[hashIdx % ARBITRARY_HASH_KEY.length];
            lastHash = hashKey ^ (source[i].charCodeAt() + lastHash);
            hashOut[i % hashOut.length] = lastHash ^ hashOut[i % hashOut.length];
            hashIdx++;
          }
        """


        for ch in source:
            hashKey = self.ARBITRARY_HASH_KEY[hashIdx % len(self.ARBITRARY_HASH_KEY)]
            lastHash = hashKey ^ (ord(ch) + lastHash)
            hashOut[idx % len(hashOut)] = lastHash ^ hashOut[idx % len(hashOut)]
            idx += 1
            hashIdx += 1
            
        # format against the output mask
        for num in hashOut:
            self.logger.debug("num: " + str(num) + "  hexed: " + hex(abs(num)))
            sHashOut += hex(abs(num))[2:]
            
        return sHashOut

    def hash(self, source, size):
        self.logger.debug("computing hash for: '" + source + "'")
        return self.passwordHash(source)
    
    def createSessionKey(self, username, password, clientKey, sessionId):
        timestamp = str(time.time())
        hash = self.hash(username + ":" + password + ":" + clientKey + ":" + \
                               sessionId + ":" + timestamp, self.TABLE_SIZE)
        
        return hash * random.randint(1,self.TABLE_SIZE)
        
    def authenticateRequest(self, requestString, noBody = False):
        """
           The request is a map of parameters from the client's JSON.  I expect
           to see the following keys:
           * sessionId
           * requestHash
           * request (map)
           
           This does not validate that the session ID is valid, only that the
           request content hashes to the same value.
        """
        authenticated = False
        
        if noBody:
            # replace the request body for authentication
            requestString = "{}"
        
        if requestString != None and \
           self.requestHash != None and \
           self.sessionId != None:
            
            computedRequestHash = 0
            
            sessionKey = None
            clientKey = None

            # last chance to make sure the JSON values are complete            
            authentication = Authentication()
            (userId, sessionKey, clientKey) = authentication.loadSessionKeys(self.sessionId)
            self.logger.debug("Got session keys: " + str(userId) + "," + str(sessionKey) + "," + str(clientKey))
            
            # ...calculate a hash on what the client sent
            computedRequestHash = self.hash(str(clientKey) + ":" + \
                                    str(sessionKey) + ":" + \
                                    requestString, \
                                    self.TABLE_SIZE)
            self.logger.debug("Content considered for hash: " + str(clientKey) + ":" + \
                              str(sessionKey) + ":" + \
                              requestString)
            self.logger.debug("Calculated hash: " + str(computedRequestHash) + "  client Hash: " + str(self.requestHash))

            authenticated = self.requestHash == str(computedRequestHash)
            
            self.logger.debug("authentication result: " + str(authenticated))
        else:
            self.logger.debug("Missing request body, hash, or session ID")
                
        return authenticated