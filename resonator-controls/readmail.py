import poplib
from email import parser
import getmail
import time
import sys
import calendar
import collections
"""a dumb, non-asynchronous client which periodically checks a fixed email address
and replied appropriately to messages with a specific target"""
import email.utils
from email.mime.text import MIMEText



DEBUG = False

def dprint(s):
    if DEBUG:
        print s


def getTime(e):
    """get GM time, in seconds, from atom entry e"""
    return calendar.timegm(e.published_parsed)




class Inbox(object):
    """interface to read from one gmail account"""


    def __init__(self, username, pwd):
        self.username = username
        self.pwd = pwd
         



class TargetInbox(Inbox):
    """Inbox which periodically searches for and replies to emails with a certain subject line"""

    ResponseFuncs = {}

    def __init__(self, username, pwd):
        Inbox.__init__(self, username, pwd)

        # first index at which to stop checking mail
        self._read = collections.deque(20*[None], 20)
        self._init = True



    def haveRead(self, e):
        """returns True if this email has been read before"""
        return (e.id in self._read)

    def markRead(self, e):
        """indicate that e has been read"""
        self._read.appendleft(e.id)

   
    def findStopIndex(self, msg_list):
        """find the first index at which a message has been read"""
        for i in range(len(msg_list)):
            if self.haveRead(msg_list[i]):
                return i
        raise ValueError("too many new messages!")





    def respondChronological(self):
        """ Sorts through recent emails, picks those which have 
        a subject line in self.targets and replies. Also deletes old messages"""
        
        
        # these are in chronological order, most recent first
        atom = getmail.get_atom(self.username, self.pwd)
        targets = self.ResponseFuncs.keys()
       
        allmsg = atom.entries
        if self._init:
            stopindex = 0
            self._init = False
            for m in allmsg:
                self.markRead(m)
        else:
            stopindex = self.findStopIndex(allmsg)


        #new messages
        dprint("stopindex " + str(stopindex))
        #process new messages...
        for i in range(0, stopindex):
            msg = allmsg[i]
            if str(msg.title) in targets:
                self.respondWith(self.getResponseFunc(str(msg.title)), msg)
            else:
                self.respondWithError(msg)
            self.markRead(msg)

        

    def respondWithError(self, msg):
        pass

    def getResponseFunc(self,targetstr):
        """ returns a function of self and other args"""
        return self.ResponseFuncs[targetstr]

    def respondWith(self, f, msg):
        print "Responding to message {0} ".format(msg.title)
        f(self, msg)
   


def parseFromString( s):
    """ get email address of author"""
    return s.split('(')[1].split(')')[0].strip()



