from base import BaseTestCase
from gaedocstore import GDSDocument, GDSJson
from google.appengine.ext import ndb
import json
import gaedocstore
class testDictGDSDocumentConversions(BaseTestCase):
    
    def test0(self):
        x = ndb.Expando() #GDSDocument()
#        x.fred = [GDSDocument(), 5]
        x.fred = ndb.Expando()
        x.fred.george = ndb.Expando()
        x.fred.george.ringo = "wut"

        x.put()
        
        y = x.key.get()
        
        self.assertEqual(y.fred.george.ringo, "wut")
        
    def test1(self):
        x = GDSDocument()
#        x.fred = [GDSDocument(), 5]
        x.fred = GDSDocument()
        x.fred.george = GDSDocument()
        x.fred.george.ringo = "wut"

        x.put()
        
        gp = ndb.GenericProperty()
        gp._name = "fred.george.ringo"
        y = GDSDocument.query(gp == "wut").get()
        
        self.assertIsNotNone(y)
        self.assertEqual(y.fred.george.ringo, "wut")

    def test2(self):
        x = GDSDocument()
#        x.fred = [GDSDocument(), 5]
        x.fred = GDSDocument()
        x.fred.george = GDSDocument()
        x.fred.george.ringo = "wut"
        x.fred.george.ttt = GDSJson()
        x.fred.george.ttt.json = [3, 4, {'x':'thingo'}]
#        x.fred.george.ttt = ndb.JsonProperty()
#        x.fred.george.ttt = {"item":[3, 4, {'x':'thingo'}]}

        x.put()
        
        gp = ndb.GenericProperty()
        gp._name = "fred.george.ringo"
        y = GDSDocument.query(gp == "wut").get()
        
        self.assertIsNotNone(y)
        self.assertEqual(y.fred.george.ringo, "wut")
        
        z = y.to_dict()
#        s = FixToDict(z)
        json.dumps(z, indent=True)
        #logging.warning(s)

    def convertToGDSAndBack(self, aDict):
        lgdsDocument = gaedocstore.DictToGDSDocument(aDict)
        
        self.assertIsNotNone(lgdsDocument, "lgdsDocument should not be None")
        
        ldict2 = lgdsDocument.to_dict()
        
        self.assertIsNotNone(ldict2, "ldict2 should not be None")

        self.assertDictEqual(aDict, ldict2)

    def convertToGDSAndQuery(self, aDict, aQueryField, aQueryValue):
        lgdsDocument = gaedocstore.DictToGDSDocument(aDict)
        lgdsDocument.put()
        
        self.assertIsNotNone(lgdsDocument, "lgdsDocument should not be None")
        
        lgp = ndb.GenericProperty()
        lgp._name = aQueryField
        lgdsDocument = GDSDocument.query(lgp == aQueryValue).get()
        
        self.assertIsNotNone(lgdsDocument)
        
        ldict2 = lgdsDocument.to_dict()
        
        self.assertIsNotNone(ldict2, "ldict2 should not be None")

        self.assertDictEqual(aDict, ldict2)
        
    def test3(self):
        ldict = {"fred":"george", "bill": True}
        
        self.convertToGDSAndBack(ldict)

    def test4(self):
        ldict = {"fred":"george", "bill": True, "harry": [1, 2, 3]}
        
        self.convertToGDSAndBack(ldict)
        
    def test5(self):
        ldict = {"fred":"george", "larry":{"gertrude": 47}}
        
        self.convertToGDSAndBack(ldict)
        
    def test6(self):
        # need a key because we're actually saving the object here, it'll come back to us with an unexpected generated key otherwise.
        ldict = {"key": "thing", "fred":"george", "larry":{"gertrude": 47}}
        
        self.convertToGDSAndQuery(ldict, "fred", "george")
        
    def test7(self):
        # need a key because we're actually saving the object here, it'll come back to us with an unexpected generated key otherwise.
        ldict = {"key": "thing", "fred":"george", "larry":{"gertrude": 47}}
        
        self.convertToGDSAndQuery(ldict, "larry.gertrude", 47)        
        
    def test8(self):
        # need a key because we're actually saving the object here, it'll come back to us with an unexpected generated key otherwise.
        ldict = {"key": "thing", "fred":"george", "gertrude": [1, 3, {"harry": "thing"}], "larry":{"gertrude": 47}}
        
        self.convertToGDSAndQuery(ldict, "larry.gertrude", 47)
        
    def test9(self):
        ldict = {"fred":"george", "bill": [1, 2], "harry": []}
        
        self.convertToGDSAndBack(ldict)
                        