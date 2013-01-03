import unittest
import logging

from google.appengine.ext import testbed

class BaseTestCase(unittest.TestCase):
    fredBloggs = None
    
    def setUp(self):
        logging.debug("inherited setUp")

        self.testbed = testbed.Testbed()
        
        self.testbed.activate()
        
        self.testbed.init_datastore_v3_stub()
        
        self.testbed.init_memcache_stub()
        
        self.constructModel()
        
    def constructModel(self):
#        x = NdbThing(thingo = "fred")
#        x.put()
#        
#        logging.warning(x.key)
        pass
    
#        lperson1 = XPerson(title = "Mr", firstname = "Fred", lastname = "Bloggs")
#        lperson1.put()
#        
#        self.fredBloggs = db.get(lperson1.key())
#        
#        laddress1 = XAddress(type = "HOME", person = lperson1, addr1 = "1 One St", addr2 = "Oneville", postcode = "1234")
#        laddress1.put()
#        
#        laddress2 = XAddress(type = "WORK", person = lperson1, addr1 = "2 Two St", addr2 = "Twoville", postcode = "2345")
#        laddress2.put()
#
#        self.fredBloggsAddr1 = db.get(laddress1.key())
#        self.fredBloggsAddr2 = db.get(laddress2.key())
#        