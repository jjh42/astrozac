"""Models of the datastore."""

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore
import logging
import hashlib

class User(db.Model):    
    class InitialsProperty(db.StringProperty):
        def validate(self, value):
            logging.info('Validating %s, type %s' % (value, type(value)))
            if  not((type(value) == str) or type(value) == unicode) or (len(value) < 2) or (len(value) > 3):
                logging.warning('User entered invalid initials.')
                raise Exception('Invalid length initials')
            
            return value
            
    user = db.UserProperty()
    initials = InitialsProperty(default='XXX')




class Log(db.Model):
    owner = db.UserProperty(required=True)
    raw = blobstore.BlobReferenceProperty(required=True) # For data security the raw input of every log file is kept.


class Image(db.Model):
    owner = db.UserProperty(required=True)
    data = blobstore.BlobReferenceProperty(required=True)
