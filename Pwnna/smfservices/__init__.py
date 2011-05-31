import urllib, urllib2, cookielib
import re
import quopri
import hashlib
import time

class Error(Exception): pass

# Because this is probably gonna be used as a trolling tool. YOU'RE NOT ALLOWED TO USE THIS.
# Code is purely for studying.

class SMFService:
    """ SMF Services like posting and reply """
                                                        # LOLOL TOR!!
    def __init__(self, index, username, password, proxy="localhost:8118", userAgent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; OfficeLiveConnector.1.4; OfficeLivePatch.1.3; yie8)", simulation=False, outputlevel=1):
        self.initTime = time.time()
        self.outputlevel = outputlevel
        self.output("SMFService Initializing")
        self.ip = "Unknown"
        self.index = index
        self.simulation = simulation
        if self.simulation:
            self.output("Simulation mode active. No posts will be made.")
        self.username = username
        self.password = password
        self.proxy = proxy
        self.userAgent = userAgent
        self.sessionID = None
        self.opener = self.buildOpener()
        if self.outputlevel >= 2:
            self.output("Noisy output active.")
            # self.ip = "".join(self.openURL("http://research.thekks.net/ip.php").readlines())
            # self.output("My IP is: " + self.ip, 2) ... Let's not flood my fucking server.
            
        self.loggedIn = self.loginToSMF()
        self.buildRegexPattern()

    def output(self, msg, outputlevel=1):
        # Because logging is not hardcore enough.
        """ Print message. msg->message to be printed. outputlevel->message level"""
        if outputlevel <= self.outputlevel:
            print msg

    def buildOpener(self):
        """ Builds an opener with proxy and cookie """
        cookies = cookielib.CookieJar()
        if self.proxy:
            proxyHandle = urllib2.ProxyHandler({"http":"http://%s" % self.proxy})
            opener = urllib2.build_opener(proxyHandle, urllib2.HTTPCookieProcessor(cookies))
        else:
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))

        return opener

    def buildRegexPattern(self):
        
        self.titlePattern = re.compile("<title>(.+?)</title>")
        
        self.replySubjectPattern = re.compile('<input type="text" name="subject" value="(.+?)"')

    
    def openURL(self, url, data=None, opener=None):
        """ Opens and URL with opener and user agent """
        if not opener:
            opener = self.opener
            
        if data:
            data = urllib.urlencode(data)

        self.output("Opening %s" % url)
        startTime = time.time()
        
        headers = {'User-Agent' : self.userAgent}
        req = urllib2.Request(url, data, headers)
        response = opener.open(req)
        endTime = time.time()
        self.output("Response received. Time: %.1f ms" % ((endTime - startTime)*1000))
        return response

    def getSMFLoginSessionID(self, html):
        """ Gets the Login Session ID """
        pattern = "onsubmit=\"hashLoginPassword[\(]this, '(\w+)'[\)];"
        result = re.search(pattern, html)
        sessionID = result.group(1)
        self.output("Session ID is %s" % sessionID)
        return sessionID
    
    @staticmethod
    def hashLoginPassword(username, password, sessionid):
        """ Hashes login password """
        username = quopri.decodestring(username)
        username = username.lower()
        password = quopri.decodestring(password)
        sha = hashlib.sha1(username + password).hexdigest()
        sha = hashlib.sha1(sha + sessionid).hexdigest()
        return sha

    def loginToSMF(self):
        """ Login to SMF """
        html = "".join(self.openURL(self.index + "?action=login").readlines())
        self.sessionID = self.getSMFLoginSessionID(html)
        resp = self.openURL(self.index + "?action=login2", {"user": self.username, "hash_passwrd": self.hashLoginPassword(self.username, self.password, self.sessionID)})
        html = "".join(resp.readlines())
        if re.search("<title>Login</title>", html):
            self.output("Failed to authenticate to SMF.")
            self.debug(html)
            return False
        else:
            self.output("Authenticated to SMF.")
            return True

    def replyPost(self, topicID, msg):
        """ Post reply """
        if not self.loggedIn:
            raise Error("You're not logged in!")
        
        
        data = {}
        if self.outputlevel >= 2:
            postpage = self.openURL(self.index + "?action=post;topic=%.1f" % float(topicID))
            html = "".join(postpage.readlines())
            data['subject'] = self.replySubjectPattern.search(html).group(1)
        else:
            data['subject'] = "Re: "
        
        data['message'] = str(msg)
        data['additional_options'] = 0
        data['topic'] = topicID
        data['sc'] = self.sessionID
        response, title = self._postStuff('http://research.thekks.net/testsmf/index.php?action=post2;start=0', data)
        if response:
            if self.outputlevel >= 2:
                self.output("Replied to the thread %s" % (data['subject'].split(":")[1].strip()))
            else:
                self.output("Replied to thread id: %.1f" % float(topicID))
        return response
        

    def newPost(self, board, title, msg):
        """ New Post """
        if not self.loggedIn:
            raise Error("You're not logged in!")          
        data = {}
        data['subject'] = str(title)
        data['message'] = str(msg)
        data['additional_options'] = 0
        data['sc'] = self.sessionID
        response, title = self._postStuff(self.index + "?action=post2;start=0;board=%d" % int(board), data)
        if response:
            self.output("Post posted to %s" % title)
        return response

    def debug(self, html, filename="test.html"):
        """ Debug html to a file """
        f = open(filename, "w")
        f.write(html)
        f.close()
        
    def _getHiddenInput(self, html):
        """ Get the seqnum """
        return None
        self.output("Getting hidden inputs.")
        seqnum = self.seqnumPattern.search(html).group(1)
        self.output("Received Hidden Input: seqnum: %s | Time: %.1f ms" % (seqnum, (time.time() - startTime)*1000))
        return {'seqnum' : seqnum}

    def _postStuff(self, posturl, data):
        """ Actually post stuff """
        if self.simulation:
            self.output("Simulation mode active. No posts will be made.")
            response = self.openURL(posturl, None)
            return response, "Simulation"
        response = self.openURL(posturl, data)
        html = "".join(response.readlines())
        title = self.titlePattern.search(html).group(1)
        if "error" not in title.lower():
            return response, title
        else:
            self.output("Post failed to post. See the test.html for details")
            self.debug(html)
            return False, False
    
def average(l):
    """ Find average """
    return sum(l)/float(len(l))
   
if __name__ == "__main__":

    url = raw_input("SMF URL: ")
    user = raw_input("SMF User: ")
    password = raw_input("Password: ")
    board = int(raw_input("Board ID: "))
    
    smf = SMFService(url, user, password)
    t = ""
    i = 0
    timeTaken = time.time() - smf.initTime
    timeInterval = time.time()
    while t.lower() != "x":
        i += 1
        smf.newPost(board, "Test Post", "SPAM [b]SPAM POSTED FROM PYTHON[/b]")
        timeTaken += (time.time() - timeInterval)
        t = raw_input("Press any key to continue or x to quit.")
        timeInterval = time.time()
        
    smf.output("Time taken: %.1f seconds for %d posts" % (timeTaken, i))
    raw_input("press enter to exit...")
