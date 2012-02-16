import SessionValidator
import unittest

class TestSessionValidator(unittest.TestCase):
    
    def test_simpleHash(self):
        validator = SessionValidator.SessionValidator()
        hashValue = 1585
        
        self.assertEqual(hashValue, validator.simpleHash("Hello", validator.TABLE_SIZE))
        
    def test_createSessionKey(self):
        username = "chris"
        password = "password"
        clientKey = "37618"
        sessionId = "100"
        
        validator = SessionValidator.SessionValidator()
        self.assertNotEqual(None, validator.createSessionKey(username, password, clientKey, sessionId))
    
    def test_authenticateRequest(self):
        requestString = "{\"sessionId\":\"100\",\"requestHash\":117693,\"request\":{\"param\":\"value\",\"param2\":\"value2\"}}"
        sessionKey = 873463899
        clientKey = 98349023
        
        validator = SessionValidator.SessionValidator()
        self.assertTrue(validator.authenticateRequest(requestString, sessionKey, clientKey))
        
    def test_authenticateRequestWithSpace(self):
        requestString = "{\"sessionId\":\"100\", \"requestHash\":117693, \"request\": {\"param\":\"value\",\"param2\":\"value2\"}}"
        sessionKey = 873463899
        clientKey = 98349023
        
        validator = SessionValidator.SessionValidator()
        self.assertTrue(validator.authenticateRequest(requestString, sessionKey, clientKey))
        
    def test_failedAuthenticationRequestByHash(self):
        requestString = "{\"sessionId\": \"100\", \"requestHash\": 117693, \"request\": {\"param\": \"value\", \"param2\": \"value2\"}}"
        sessionKey = 873463899
        clientKey = 98349023
        
        validator = SessionValidator.SessionValidator()
        self.assertFalse(validator.authenticateRequest(requestString, sessionKey, clientKey))
        
    def test_failedAuthenticationRequestByKey(self):
        requestString = "{\"sessionId\":\"100\",\"requestHash\":117693,\"request\":{\"param\":\"value\",\"param2\":\"value2\"}}"
        sessionKey = 873463898
        clientKey = 98349023
        
        validator = SessionValidator.SessionValidator()
        self.assertFalse(validator.authenticateRequest(requestString, sessionKey, clientKey))
        
    def test_failedAuthenticationRequestBadRequest(self):
        requestString = "{\"sessionId\":\"100\",\"requestHash\":117693}"
        sessionKey = 873463898
        clientKey = 98349023
        
        validator = SessionValidator.SessionValidator()
        self.assertFalse(validator.authenticateRequest(requestString, sessionKey, clientKey))
        
    
if __name__ == '__main__':
    unittest.main()