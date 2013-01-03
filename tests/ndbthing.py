from google.appengine.ext.ndb import Expando
from google.appengine.ext.db import StringProperty

class NdbThing (Expando):
    thingo = StringProperty()
    
