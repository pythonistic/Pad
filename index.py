#!/usr/bin/python
import cgi
import logging
import os
import sys
import urllib
import urlparse

libpath = os.getcwd() + os.sep
sys.path.extend([libpath + 'lib', libpath + 'server'])

import web
from jsonpickle import unpickler

urls = ("/(.*)", "index")


class index(object):

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                    filename='pad.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filemode='a')
        self.logger = logging.getLogger("index")
        self.modulePaths = [libpath + "server" + os.sep + "Pad"]

    def GET(self, path=None):
        self.logger.debug("get request " + path)
        return self.handleRequest("Get", path)

    def POST(self, path=None):
        # get the message body
        self.logger.debug("post request " + path)
        body = web.data()
        return self.handleRequest("Post", path, body)
        
    def DELETE(self, path=None):
        self.logger.debug("delete request " + path)
        body = web.data()
        return self.handleRequest("Delete", path, body)

    def getByPath(self, path=None):
        self.logger.debug("getByPath: " + str(path))
        outfile = None
        out = ""
        if path != None:
            if path.startswith("js/"):
                self.logger.debug("getting javascript")
                outfile = file(os.getcwd() + os.sep + path, 'r')
                self.logger.debug("javascript file " + str(outfile))
                web.header('Content-type:', 'application/javascript')
            elif path == "api.html":
                self.logger.debug("getting api docs")
                outfile = file(os.getcwd() + os.sep + 'api.html', 'r')
                web.header('Content-type:', 'text/html')
            else:
                self.logger.debug("getting pad html")
                outfile = file(os.getcwd() + os.sep + 'pad.html', 'r')
                web.header('Content-type:', 'text/html')

        if outfile != None:        
            out = outfile.read()
            outfile.close()
            
        self.logger.debug("returning out, length " + str(len(out)))
        return out

    def handleRequest(self, action, path, body=None):
        sessionId = None
        requestHash = None
        try:
            #queryParams = web.webapi.input()
            env = web.ctx["environ"]
            self.logger.debug("env: " + str(env))
            queryString = env["QUERY_STRING"]
            self.logger.debug("queryString: " + str(queryString))
            #queryParams = urlparse.parse_qs(queryString)
            queryParams = cgi.parse_qs(queryString)
            self.logger.debug('queryParams: ' + str(queryParams))
            if "username" in queryParams:
                username = queryParams["username"][0]
                self.logger.debug("qs username: " + username)
            if (body == None or len(body) < 1) and "body" in queryParams:
                body = queryParams["body"][0]
                self.logger.debug("qs body: " + body)
            elif body != None:
                #body = cgi.parse_qs(body)
                body = urllib.unquote(body)
                self.logger.debug("post body: " + body)
            # session ID header
            if 'HTTP_X_PAD_SESSION_ID' in env:
                sessionId = env['HTTP_X_PAD_SESSION_ID']
            # request content hash
            if 'HTTP_X_PAD_REQUEST_HASH' in env:
                requestHash = env['HTTP_X_PAD_REQUEST_HASH']
        except:
            queryString = ""
            queryParams = {}

        self.logger.debug("request action " + str(action) + " path " + str(path) + " body '" + str(body) + "'")
        if path != None and len(path) > 0:
            # split the path
            parts = path.split('/')
            # remove empty path parts
            while '' in parts:
                parts.remove('')
            # assemble path in most-specific to most-general (shortest) order
            paths = []
            params = []
            while len(parts) > 0:
                apiPath = action + "".join(self.camelCase(parts))
                paths.append((apiPath, list(params)))
                params.insert(0, parts.pop())

            # find the first matching path
            # TODO refactor -- this loop should be inside the previous loop
            self.logger.debug("Looking in " + str(self.modulePaths))
            for apiPathTuple in paths:
                apiPath = apiPathTuple[0]
                apiParams = apiPathTuple[1]
                self.logger.debug("Testing apiPath: " + str(apiPath))
                for modulePath in self.modulePaths:
                    for filename in os.listdir(modulePath):
                        if filename.endswith(".py") and \
                           apiPath == filename[:-3]:
                            packagePrefix = \
                              modulePath[modulePath.rindex(os.sep) + 1:]
                            # create and invoke the handler
                            self.logger.debug("python path " + str(sys.path))
                            self.logger.debug("Finding handler class " + \
                              str(packagePrefix) + "." + str(apiPath))
                            handlerClass = self.getHandlerClass(apiPath, \
                              packagePrefix)
                            self.logger.debug("Found handler class " + \
                              str(handlerClass))
                            if handlerClass != None:
                                handler = handlerClass.__new__(handlerClass)
                                # gotta explicitly call init...
                                handler.__init__()
                                json = handler.invoke(apiParams, body, sessionId, requestHash)

                                self.logger.debug("Callback in query params: " + str("callback" in queryParams))
                                if "callback" in queryParams:
                                    json = queryParams["callback"][0] + "(" + json + ")"

                                web.header('Content-type', 'text/javascript')
                                self.logger.debug('returning json ' + json)
                                return json

        # fallthrough
        # consider returning 404 when handler class isn't found
        #self.logger.debug("fell through on path " + str(path) + " - returning API docs")
        #return self.getApi(path)
        self.logger.debug("fell through on path " + str(path) + " - returning content by path")
        return self.getByPath(path)

    def camelCase(self, parts):
        newParts = []
        for part in parts:
            if len(part) > 0:
                newPart = ""
                newPart = part[0].upper()
                if len(part) > 1:
                    newPart += part[1:].lower()
                newParts.append(newPart)
        return newParts

    def getHandlerClass(self, path, packagePrefix=""):
        className = packagePrefix + "." + path
        clz = None

        try:
            self.logger.debug("Importing " + className)
            __import__(className)
            self.logger.debug("Imported")
            self.logger.debug("Module present? " + str(className in sys.modules))
            clz = getattr(sys.modules[className], path)
        except ImportError, e:
            self.logger.debug("Import error for handler class " + className + ": " + str(e))
        except:
            self.logger.debug("Didn't resolve handler class " + className)
            pass

        return clz


app = web.application(urls, globals(), autoreload=False)

if __name__ == '__main__':
    app.run()
