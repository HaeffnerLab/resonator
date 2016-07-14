"""this script will check USERNAME@gmail.com for specific subject lines
and respond to them. PASS needs to be the password for the corresponding gmail
account"""




from readmail import TargetInbox, parseFromString
import labrad

import smtplib
import email.utils
from email.mime.text import MIMEText

import time
import numpy as np
import collections

USERNAME = "resonatorcomm"
PASS = "S12D52111333"
#WINDOWS_MACHINE_IP = '192.168.169.30'    # use this on other computers
WINDOWS_MACHINE_IP = 'localhost'

DEBUG = False
def dprint(s):
    if DEBUG:
        print s

def getClientAddr(msg):
    return parseFromString(msg.author)


def makeMSG(pt, text, to, subject):

    msg = MIMEText(text)
    msg['To'] = email.utils.formataddr(('Client', to))
    msg['From'] = email.utils.formataddr(('Resonator', pt.gmail_acc))
    msg['Subject'] = subject
    return msg






#########################


def sendErrMsg(pt, msg):
    """Tells the client that they sent a bad request"""

    to = getClientAddr(msg)

    errstr = """Error: the subject line of your previous email was not 
                a valid request or command. For help, send a blank email
                with the subject line "help?" to this address
                ( {0} ) """.format(pt.gmail_acc)
    subject = "Invalid request"
    msg = makeMSG(pt, errstr, to, subject)

    pt.send(msg, to)


def unsubscribePI(pt, msg):
    """unsubscribe from the pressure-increasing mailing list"""
    to = getClientAddr(msg)
    lst = pt.mailingListNames['PI']
    
    try:
        lst.unsubscribe(to)
        text = "You have been unsubscribed from the PI mailing list"""
        subject = "PI mailing list: Unsubscription succeeded"
    except ValueError:
        text = "your email address ({0}) is not subscribed to the PI mailing list"
        subject = "PI mailing list: unsubscription failed"
    msg = makeMSG(pt, text, to , subject)

    pt.send(msg, to)


def subscribePI(pt, msg):
    """Subscribe to the pressure-increasing mailing list"""
    to = getClientAddr(msg)

    lst = pt.mailingListNames['PI']
    lst.subscribe(to)

    text = """You have been subscribed to the resonator  pressure-increasing 
              mailing list. You will be notified if the pressure decreases in
              {0} consecutive samples. The minimum time between notifications
              is {1} minutes.

              To unsubscribe, send a blank email with subject line
              'unsubscribe:PI'

              to this address (resonatorcomm@gmail.com)""".format(pt.NRECENT, lst.waitTime/60)

    subject = "PI mailing list subscription"
    msg = makeMSG(pt, text, to, subject)
    pt.send(msg, to)



def sendvalues(pt, msg):
    """Request the pressure and temperature of the apparatus, recorded at the time
    that the request is processed."""
    to = getClientAddr(msg)
    infotext = pt.getValsText(msg)
    (p, t) = pt.getVals()
    valstext = "pressure = {0} mbar, temperature = {1} K\n".format(p, t)
    text = infotext + "\n" + valstext

    subject = "Pressure and Temp Values"
    msg = makeMSG(pt, text, to, subject)

    pt.send(msg, to)


def sendinfo(pt, msg):
    """Request information about the mail server"""
    to = getClientAddr(msg)

    infostr = """ resonatorcomm@gmail.com is a mail server running on the linux machine at the resonator
                  experiment workstation. Every {0} seconds it checks this address and looks for emails
                  with specific subject lines, that either request some kind of data or issue a command.
                  It processes these requests and commands and then waits again.
                  To request data or any other information, send a blank email 
                  with one of the following subject lines (case-sensitive, please match exactly): \n""".format(pt.timeout)
    for s in pt.getTargets():
        infostr += "Subject line: '{0}' ...\n".format(s)
        infostr += "...      " + pt.getResponseFunc(s).__doc__ + "\n" 
    infostr += """\n A response will be issued in about {0} sec.""".format(pt.timeout)


    subject = "Help"
    msg = makeMSG(pt, infostr, to, subject)

    pt.send(msg, to)

def sendRecentPressures(pt, msg ):
    """Request the  most recent pressure values and the times at which they were recorded."""
    to = getClientAddr(msg)
    s = 'Pressure, mbar     @  Time\n --------------------\n'
    P = pt.recentPressures
    tm = pt.recentTimes
    for i in range(len(P)):
        s = s + "{0}     @  {1}\n".format(str(P[i]), tm[i])
    
    

    subject = "Recent Pressures"
    msg = makeMSG(pt, s, to, subject)
    pt.send(msg, to)

def sendRecentTemps(pt, msg ):
    """Request the most recent temperature values and the times at which they are recorded."""
    to = getClientAddr(msg)
    s = 'Temp, K     @  Time\n --------------------\n'
    T = pt.recentTemps
    tm = pt.recentTimes
    for i in range(len(T)):
        s = s + "{0}     @  {1}\n".format(str(T[i]), tm[i])
    
    
    subject = "Recent Temperatures"
    msg = makeMSG(pt, s, to, subject)

    pt.send(msg, to)




class PT(TargetInbox):
    """responds with pressure and temp to inquiries"""
    
    ResponseFuncs = { 'vals?': sendvalues, 'help?': sendinfo, 'recent:T?': sendRecentTemps, 'recent:P?':sendRecentPressures, 'subscribe:PI': subscribePI,
                      'unsubscribe:PI':unsubscribePI}
    timeout =10
    NRECENT = 20

    def __init__(self, username, pwd):
        TargetInbox.__init__(self, username, pwd)
        self.gmail_acc = self.username + "@gmail.com"
        c = labrad.connect(WINDOWS_MACHINE_IP)
        self.gauge = c.pfeiffer_pressure_gauge
        
        from keithley_helper import voltage_conversion as VC
        self.vc = VC()
    
        self.dmm = c.keithley_2100_dmm
        self.dmm.select_device()

        #finite length FIFO (or rolling) buffers to store recent values
        self.recentTimes = collections.deque(self.NRECENT*[None], self.NRECENT)
        self.recentTemps = collections.deque(self.NRECENT*[None], self.NRECENT)
        self.recentPressures = collections.deque(self.NRECENT*[None], self.NRECENT)

        self.mailingLists = []
        self.mailingListNames = {}

    def getP(self):
        """pressure in mbar as a float"""
        return self.gauge.readpressure().inUnitsOf('bar').value * 1000.0
    
    def getPStr(self):
        try:
            p = self.getP()
            return "{0:.2E}".format(p)
        except AttributeError:
            return "Gauge off or not present."
    
    def getTStr(self):
        t = self.getT()
        return "{0:.2E}".format(t)

    def getT(self):
        """ temp in Kelvin as a float"""
        v = self.dmm.get_dc_volts()
        return self.vc.conversion(v)

    def getVals(self):
        p = self.getPStr()
        t = self.getTStr()
        return (p, t)

    def send(self, msg, to):
        """ send msg to address to"""
        self.authenticate()
        self.sendStr(to, msg.as_string())
        self.closeAcc()

    def authenticate(self):
        
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()

        self.server.login(self.gmail_acc, self.pwd)

    def sendStr(self, to, s):
        self.server.sendmail(self.gmail_acc, to, s)

    def closeAcc(self):
        self.server.close()

    def getValsText(self, msg):
        return "Values recorded at " + time.strftime("%Y - %m - %d, %H:%M:%S") 

    def getTargets(self):
        return self.ResponseFuncs.keys()

    def addMailingList(self, lst):
        if lst.name in self.mailingListNames.keys():
            raise ValueError('mailing list already exists')
        self.mailingLists.append(lst)
        
        self.mailingListNames[lst.name] = lst

    def update(self):
        """take care of stuff not related to responding"""
        T = self.getTStr()
        P = self.getPStr()
        tm = time.strftime("%Y - %m - %d, %H:%M:%S")
        #update buffers
        self.recentTemps.appendleft(T)
        self.recentPressures.appendleft(P)
        self.recentTimes.appendleft(tm)

        for lst in self.mailingLists:
            lst.act()


    def respondWithError(self, msg):
        """this is called when someone sends a bad request"""

        print "Handling bad request {0}".format(msg.title)
        sendErrMsg(self, msg)

    def loop(self):
        """ check periodically and respond"""
        print "Listening at ", self.gmail_acc
        
        try:
            while(1):

                self.update()
                self.respondChronological()
                dprint("Response completed")
                time.sleep(self.timeout)
        except KeyboardInterrupt:
            return

class MailingList(object):

    def __init__(self, parent):
        """parent = email client, has to implement a send() method"""
        self.parent = parent
        self.recipients = []
        self.parent.addMailingList(self)

    def subscribe(self, addr):
        """addr ~ name@example.com"""
        self.recipients.append(addr)
        dprint("subscribed address " + addr)

    def unsubscribe(self, addr):
        self.recipients.remove(addr)
        dprint("unsubscribed address " + addr)

    def mail(self):
        text = self.getText()
        subject = self.getSubject()
        dprint("mailing")
        for addr in self.recipients:
            m = self.makeMSG(text, subject, addr)
            self.parent.send(m, addr)



    def makeMSG(self, text,subject, to):

        
        msg = MIMEText(text)
        msg['To'] = email.utils.formataddr(('Client', to))
        msg['From'] = email.utils.formataddr(('Res. mailing list {0}'.format(self.name), self.parent.gmail_acc))
        msg['Subject'] = subject
        return msg
    
    def act(self):
        if self.needToMail():
            self.mail()
            self.maintenance()
    def getText(self):
        pass
    def getSubject(self):
        pass
    def needToMail(self):
        pass

    def maintenance(self):
        pass


class PressureIncreasingList(MailingList):
    """notifies listeners when the pressure increases steadily"""
    name = 'PI'
    waitTime = 30 * 60

    def __init__(self, parent):
        MailingList.__init__(self, parent)
        self.lastMailTime = time.time()



    def needToMail(self):
        return self.pressureIsRising() and self.waitedLongEnough()
    def pressureIsRising(self):
        try:
            vals = np.array(list(map( float, self.parent.recentPressures)))
        except ValueError:
            vals = np.zeros(np.size(self.parent.recentPressures))
        
        deltaP = np.diff(vals)
        dprint(deltaP)
        dprint( vals)
        # the pressures start at the most recent, so negative differences mean older values are 
        # less than newer ones
        return np.all(deltaP < 0)

    def waitedLongEnough(self):
        
        return (time.time() - self.lastMailTime) > self.waitTime

    def maintenance(self):
        self.lastMailTime = time.time()

    def getSubject(self):
        return self.name
    def getText(self):
        s = "pressure has been rising recently.\n"
        for i in range(len(self.parent.recentPressures)):
            p = self.parent.recentPressures[i]
            t = self.parent.recentTimes[i]
            s += "{0}   |   {1} \n".format(str(p), str(t))
        return s
    

handler = PT(USERNAME, PASS)

PIncreasingList = PressureIncreasingList(handler)
handler.loop()
