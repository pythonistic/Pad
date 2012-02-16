var HASH_TABLE_SIZE = 128000;

var ARBITRARY_HASH_KEY = [
  0xb8f1, 0x18d9, 0xad80, 0xd9a9, 0xe901, 0x257b, 0x5e07, 0x1a31,
  0x70b7, 0x01fd, 0x6080, 0x1cf0, 0x0a15, 0xe16a, 0xa731, 0x8a80,
  0x73ba, 0x1bf0, 0x24e2, 0x7406, 0x660c, 0x1dcd, 0xdba5, 0xc05c,
  0x40c9, 0xcbb4, 0xeb68, 0xc294, 0x3a4b, 0xbf43, 0x904d, 0xffbf,
  0x27a3, 0xfac0, 0x11fe, 0x3e56, 0xb82b, 0x0007, 0xdfe7, 0xe3c0,
  0x183a, 0x46df, 0x515a, 0x46e5, 0xde80, 0x2e11, 0xe95d, 0xf870];

var HASH_OUT = [
  0x2c88, 0xc801, 0x14c0, 0x5886, 0x214f, 0x3b8e];

var simpleHash = function simpleHash(source, tableSize) {
  var hash = 0;
  
  for (var i = 0; i < source.length; i++) {
    hash += (source[i].charCodeAt() * (i + 1));
  }
  
  return Math.abs(hash) % tableSize;
}

var passwordHash = function passwordHash(source) {
  var hashOut = "";
  var lastHash = 1;
  var hashIdx = source.length;
  var hashOut = HASH_OUT.slice(0);
  var sHashOut = "";
  
  for (var i = 0; i < source.length; i++) {
    var hashKey = ARBITRARY_HASH_KEY[hashIdx % ARBITRARY_HASH_KEY.length];
    lastHash = hashKey ^ (source[i].charCodeAt() + lastHash);
    hashOut[i % hashOut.length] = lastHash ^ hashOut[i % hashOut.length];
    hashIdx++;
  }

  // format against the output mask
  for (var i = 0; i < hashOut.length; i++) {
    var num = hashOut[i];
    
    sHashOut += (Math.abs(hashOut[i])).toString(16);
  }
  
  return sHashOut;
}

/* replace the implementation with a different hash call later */
var hash = function hash(source, tableSize) {
  return passwordHash(source);
}

/* not really used . . . */
var createSessionKey = function createSessionKey(username, password, clientKey, sessionId) {
  return hash(username + ":" + password + ":" + clientKey + ":" + sessionId, HASH_TABLE_SIZE);
}

var createClientKey = function createClientKey() {
  var dt = new Date();
  var key = hash(dt.getTime() + ":" + navigator.appVersion + ":" + navigator.platform + ":" + (Math.random() * HASH_TABLE_SIZE + 1).toString(16), HASH_TABLE_SIZE);
  return (key).toString(16);
}

var createJsonRequest = function createJsonRequest(sessionId, clientKey, sessionKey, jsonBlob) {
  var sJsonBlob = JSON.stringify(jsonBlob);
  // it's important that the server compute this request hash the same way
  var requestHash = hash(clientKey + ":" + sessionKey + ":" + sJsonBlob, HASH_TABLE_SIZE);
  return {"sessionId": sessionId,
          "requestHash": requestHash,
          "request": jsonBlob};
}