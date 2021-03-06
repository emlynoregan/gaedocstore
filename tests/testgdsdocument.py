from base import BaseTestCase
from gaedocstore import GDSDocument
from google.appengine.ext import ndb
import gaedocstore
class testGDSDocument(BaseTestCase):
    
    def test0(self):
        ldict = {"fred":"george", "gertrude": [1, 3, {"harry": "thing"}], "larry":{"gertrude": 47}}

        lgdsdocument = gaedocstore.GDSDocument.ConstructFromDict(ldict)
        
        self.assertIsNotNone(lgdsdocument, "Constructed document should not be none")
        
        ldict2 = lgdsdocument.to_dict()
        
        self.assertIsNotNone(ldict2, "new dict mustn't be None")
        
        self.assertDictEqual(ldict, ldict2)
                
    def test1(self):
        ldictPerson = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": {"key": "1234567"}
        }
        
        ldictAddress = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "stuffville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
        
        ldictPersonWithAddress = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": 
            {
                "key": "1234567",
                "type": "Address",
                "addr1": "1 thing st",
                "city": "stuffville",
                "zipcode": 54321,
                "tags": ['some', 'tags']
            }
        }
        
        # first store the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress)
        self.assertIsNotNone(laddress)
        laddress.put()
        
        # next store the person
        lperson = gaedocstore.GDSDocument.ConstructFromDict(ldictPerson)
        self.assertIsNotNone(lperson)
        
        # lperson should now be populated to match ldictPersonWithAddress
        lpersonDict2 = lperson.to_dict()
        self.assertIsNotNone(lpersonDict2)
        self.assertDictEqual(lpersonDict2, ldictPersonWithAddress, "person has not been correctly updated with address")
        
    def test2(self):
        ldictPerson = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": {"key": "1234567"}
        }
        
        ldictAddress = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "stuffville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
        
        ldictPersonWithAddress = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": 
            {
                "key": "1234567",
                "type": "Address",
                "addr1": "1 thing st",
                "city": "stuffville",
                "zipcode": 54321,
                "tags": ['some', 'tags']
            }
        }
        
        # first store the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress)
        self.assertIsNotNone(laddress)
        laddress.put()
        
        # next store the person
        lperson = gaedocstore.GDSDocument.ConstructFromDict(ldictPerson)
        self.assertIsNotNone(lperson)
        lperson.put()
        
        lgp = ndb.GenericProperty()
        lgp._name = "address.zipcode"
        lqueriedPerson = GDSDocument.query(lgp == 54321).get() 
        self.assertIsNotNone(lqueriedPerson, "could not find person with query")
        
        # lperson should now be populated to match ldictPersonWithAddress
        lpersonDict2 = lqueriedPerson.to_dict()
        self.assertIsNotNone(lpersonDict2)
        self.assertDictEqual(lpersonDict2, ldictPersonWithAddress, "person has not been correctly updated with address")
        
    def test3(self):
        ldictAddress = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "stuffville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
        
        ldictAddressUpdate = {
            "key": "1234567", 
            "city": "thingville"
        }
        
        ldictAddressUpdated = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "thingville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
                
        # first store the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress)
        self.assertIsNotNone(laddress)
        laddress.put()
        
        # next update the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddressUpdate, aReplace=False)
        self.assertIsNotNone(laddress)
        laddress.put()
                        
        # laddress should now be populated to match ldictAddressUpdated
        laddressDict2 = laddress.to_dict()
        self.assertIsNotNone(laddressDict2)
        self.assertDictEqual(laddressDict2, ldictAddressUpdated, "address has not been correctly updated")
        

    def test4(self):
        ldictAddress = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "stuffville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
        
        ldictAddress2 = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "2 something st", 
            "city": "otherton", 
            "zipcode": 11111
        }
                
        # first store the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress)
        self.assertIsNotNone(laddress)
        laddress.put()
        
        # next update the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress2)
        self.assertIsNotNone(laddress)
        laddress.put()
                        
        # laddress should now be populated to match ldictAddressUpdated
        laddressDict2 = laddress.to_dict()
        self.assertIsNotNone(laddressDict2)
        self.assertDictEqual(laddressDict2, ldictAddress2, "address has not been correctly updated")

    def test5(self):
        ldictPerson = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": {"key": "1234567"}
        }
        
        ldictAddress = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "stuffville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
        
        ldictAddressUpdate = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "2 something st",
            "city": "thingville",
            "zipcode": 12345
        }
        
        ldictPersonWithAddressUpdated = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": 
            {
                "key": "1234567",
                "type": "Address",
                "addr1": "2 something st",
                "city": "thingville",
                "zipcode": 12345
            }
        }
        
        # first store the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress)
        self.assertIsNotNone(laddress)
        laddress.put()
        
        # next store the person
        lperson = gaedocstore.GDSDocument.ConstructFromDict(ldictPerson)
        self.assertIsNotNone(lperson)
        lperson.put()
        
        # now update the address
        laddressUpdated = gaedocstore.GDSDocument.ConstructFromDict(ldictAddressUpdate)
        self.assertIsNotNone(laddressUpdated)
        laddressUpdated.put()
        
        lpersonUpdated = lperson.key.get() # reload person
                
        # lperson should now be populated to match ldictPersonWithAddress
        lpersonDict2 = lpersonUpdated.to_dict()
        self.assertIsNotNone(lpersonDict2)
        self.assertDictEqual(lpersonDict2, ldictPersonWithAddressUpdated, "person has not been correctly updated with updated address")
        
    def test6(self):
        ldict = {"fred":["111", "222"], "larry":{"gertrude": 47}}

        lgdsdocument = gaedocstore.GDSDocument.ConstructFromDict(ldict)
        self.assertIsNotNone(lgdsdocument, "Constructed document should not be none")
        lgdsdocument.put()

        lgp = ndb.GenericProperty()
        lgp._name = "fred"
        lqueriedDocument = GDSDocument.query(lgp == "111").get() 
        self.assertIsNotNone(lqueriedDocument, "could not find document with query")
        
    def test7(self):
        ldictPerson = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": {"key": "1234567"}
        }
        
        ldictAddress = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "stuffville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
        
        ldictPersonWithoutAddress = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": 
            {
                "key": "1234567",
                "link_missing": True
            }
        }

        ldictPersonWithAddress = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": 
            {
                "key": "1234567",
                "type": "Address",
                "addr1": "1 thing st",
                "city": "stuffville",
                "zipcode": 54321,
                "tags": ['some', 'tags']
            }
        }
        
        # first store the person
        lperson = gaedocstore.GDSDocument.ConstructFromDict(ldictPerson)
        self.assertIsNotNone(lperson)
        lperson.put()
        
        # lperson should now be populated to match ldictPersonWithoutAddress
        lperson = lperson.key.get()
        lpersonDict2 = lperson.to_dict()
        self.assertIsNotNone(lpersonDict2)
        self.assertDictEqual(lpersonDict2, ldictPersonWithoutAddress, "person without address incorrect, first time")

        # now store the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress)
        self.assertIsNotNone(laddress)
        laddress.put()
        
        # lperson should now be populated to match ldictPersonWithAddress
        lperson = lperson.key.get()
        lpersonDict2 = lperson.to_dict()
        self.assertIsNotNone(lpersonDict2)
        self.assertDictEqual(lpersonDict2, ldictPersonWithAddress, "person with address incorrect")

        # delete the address
        laddress.key.delete()

        # lperson should now be populated to match ldictPersonWithoutAddress
        lperson = lperson.key.get()
        lpersonDict2 = lperson.to_dict()
        self.assertIsNotNone(lpersonDict2)
        self.assertDictEqual(lpersonDict2, ldictPersonWithoutAddress, "person without address incorrect, second time")

    def test8(self):
        ldictPerson = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": {"key": "1234567"}
        }
        
        ldictAddress = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "stuffville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }

        laddressTransform = {
            "fulladdress": "{{.addr1}}, {{.city}} {{.zipcode}}"
        }
        
        ldictPersonWithTransformedAddress = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": 
            {
                "key": "1234567",
                "fulladdress": "1 thing st, stuffville 54321"
            }
        }
        
        GDSDocument.StorebOTLTransform("address", laddressTransform)
        
        # first store the address
        laddress = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress)
        self.assertIsNotNone(laddress)
        laddress.put()
        
        # next store the person
        lperson = gaedocstore.GDSDocument.ConstructFromDict(ldictPerson)
        self.assertIsNotNone(lperson)
        
        # lperson should now be populated to match ldictPersonWithAddress
        lpersonDict2 = lperson.to_dict()
        self.assertIsNotNone(lpersonDict2)
        self.assertDictEqual(lpersonDict2, ldictPersonWithTransformedAddress, "person has not been correctly updated with transformed address")
        
    # test that a person can be updated with two addresses in an array
    def test9(self):
        ldictPerson = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": [{"key": "1234567"}, {"key": "2345678"}]
        }
        
        ldictAddress1 = {
            "key": "1234567", 
            "type": "Address", 
            "addr1": "1 thing st", 
            "city": "stuffville", 
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
        
        ldictAddress2 = {
            "key": "2345678", 
            "type": "Address", 
            "addr1": "99 NinetyNine St", 
            "city": "Hundred City", 
            "zipcode": 99999
        }

        ldictPersonWithAddresses = {
            "key": "897654",
            "type": "Person",
            "name": "Fred",
            "address": 
            [
                {
                    "key": "1234567", 
                    "type": "Address", 
                    "addr1": "1 thing st", 
                    "city": "stuffville", 
                    "zipcode": 54321,
                    "tags": ['some', 'tags']
                },
                {
                    "key": "2345678", 
                    "type": "Address", 
                    "addr1": "99 NinetyNine St", 
                    "city": "Hundred City", 
                    "zipcode": 99999
                }
            ]
        }
        
        # first store the addresses
        laddress1 = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress1)
        self.assertIsNotNone(laddress1)
        laddress1.put()
        laddress2 = gaedocstore.GDSDocument.ConstructFromDict(ldictAddress2)
        self.assertIsNotNone(laddress2)
        laddress2.put()
        
        # next store the person
        lperson = gaedocstore.GDSDocument.ConstructFromDict(ldictPerson)
        self.assertIsNotNone(lperson)
        lperson.put()
        
        lperson = lperson.key.get() # reload person
                
        # lperson should now be populated to match ldictPersonWithAddresses
        lpersonDict2 = lperson.to_dict()
        self.assertIsNotNone(lpersonDict2)
        self.assertDictEqual(lpersonDict2, ldictPersonWithAddresses, "person has not been correctly updated with multiple addresses")

    # test that a long string is stored properly (there is a 500 byte limit on indexed properties)
    def test10(self):
        ldict = {
            "key": "thing",
            "longthing": "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
        }
        
        lobj = gaedocstore.GDSDocument.ConstructFromDict(ldict)
        lobj.put()
        
        # now try reloading it and check it matches the input
        ldict2 = lobj.key.get().to_dict()
        self.assertIsNotNone(ldict2)
        self.assertDictEqual(ldict2, ldict)
