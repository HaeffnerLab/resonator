import urllib2
import feedparser
import time

def get_feed(user, passwd):

    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm="mail.google.com", uri="https://mail.google.com", user= "{0}@gmail.com".format(user), passwd=passwd)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
    feed  =urllib2.urlopen("https://mail.google.com/mail/feed/atom")
    return feed




def get_atom(user, pwd):
    f = get_feed(user, pwd)
    return feedparser.parse(f.read())


def get_subject_lines(atom):
    """return a list of ( subject line, id) tuples"""
    
    return list(map(lambda e: (e.title, e.id), atom.entries))



