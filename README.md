gaedocstore
===========

_See MIT license at the bottom of this document. It applies to all code in this repo._

gaedocstore is a lightweight document database implementation that sits on top of  ndb in google appengine.

## Introduction

If you are using appengine for your platform, but you need to store arbitrary (data defined) entities, 
rather than pre-defined schema based entities, then gaedocstore can help.

gaedocstore takes arbitrary JSON object structures, and stores them to a single ndb datastore object called GDSDocument.

## Simple Put

When JSON is stored to the document store, it is converted to a GDSDocument object (an Expando model subclass) as follows:

- Say we are storing an object called Input.

- Input must be a dictionary.

- Input must include a key at minimum. If no key is provided, the put is rejected.

    - If the key already exists for a GDSDocument, then that object is updated using the new JSON. 

    - With an update, you can indicate "Replace" or "Update" (default is Replace). 
Replace entirely replaces the existing entity. "Update"
merges the entity with the existing stored entity, preferentially including information from the new JSON.

    - If the key doesn't already exist, then a new GDSDocument is created for that key.


- The top level dict is mapped to the GDSDocument (which is an expando).

- The GDSDocument property structure is built recursively to match the JSON object structure.
    - Simple values become simple property values
    
    - Arrays of simple values become a repeated GenericProperty. ie: you can search on the contents. 
    
    - Arrays which include dicts or arrays become JSON in a GDSJson object, which just hold "json", a JsonProperty (nothing inside is indexed, or searchable)
    
    - Dictionaries become another GDSDocument

    - So nested dictionary fields are fully indexed and searchable, including where their values are lists of simple types,
but anything inside a complex array is not.

eg:

    ldictPerson = {
        "key": "897654",
        "type": "Person",
        "name": "Fred",
        "address": 
        {
            "addr1": "1 thing st",
            "city": "stuffville",
            "zipcode": 54321,
            "tags": ['some', 'tags']
        }
    }
    
    lperson = GDSDocument.ConstructFromDict(ldictPerson)
    lperson.put()    

This will create a new person. If a GDSDocument with key "897654" already existed then this will overwrite it. If you'd
like to instead merge over the top of an existing GDSDocument, you can use aReplace = False, eg:

        lperson = GDSDocument.ConstructFromDict(lperson, aReplace = False)

## Simple Get

All GDSDocument objects have a top level key. Normal ndb.get is used to get objects by their key.

## Querying

Normal ndb querying can be used on the GDSDocument entities. It is recommended that different types of data (eg Person, Address) 
are denoted using a top level attribute "type". This is only a recommended convention however, and is in no way
required.

You can query on properties in the GDSDocument, ie: properties from the original JSON.

Querying based on properties in nested dictionaries is fully supported. 

eg: Say I store the following JSON:

    {
        "key": "897654",
        "type": "Person",
        "name": "Fred",
        "address": 
        {
            "key": "1234567",
            "type": "Address",
            "addr1": "1 thing st",
            "city": "stuffville",
            "zipcode": 54321
        }
    }

A query that would return potentially multiple objects including this one is:

    GDSDocument.gql("WHERE address.zipcode = 54321").fetch()

or 

    s = GenericProperty()
    s._name = 'address.zipcode'
    GDSDocument.query(s == 54321).fetch()

Note that if you are querying on properties below the top level, you cannot do the more standard
    GDSDocument.query(GenericProperty('address.zipcode') == 54321).fetch()  # fails

due to a [limitation of ndb] (http://stackoverflow.com/questions/13631884/ndb-querying-a-genericproperty-in-repeated-expando-structuredproperty)

If you need to get the json back from a GDSDocument, just do this:

    json = lgdsDocument.to_dict()

## Denormalized Object Linking

You can directly support denormalized object linking.

Say you have two entities, an Address:
    {
        "key": "1234567",
        "type": "Address",
        "addr1": "1 thing st",
        "city": "stuffville",
        "zipcode": 54321
    }

and a Person:
    {
        "key": "897654",
        "type": "Person",
        "name": "Fred"
        "address": // put the address with key "1234567" here
    }

You'd like to store the Person so the correct linked address is there; not just the key, but the values (type, addr1, city, zipcode).

If you store the Person as:

    {
        "key": "897654",
        "type": "Person",
        "name": "Fred",
        "address": {"key": "1234567"}
    }

then this will automatically be expanded to 

    {
        "key": "897654",
        "type": "Person",
        "name": "Fred",
        "address": 
        {
            "key": "1234567",
            "type": "Address",
            "addr1": "1 thing st",
            "city": "stuffville",
            "zipcode": 54321
        }
    }

Furthermore, gaedocstore will update these values if you change address. So if address changes to:

    {
        "key": "1234567",
        "type": "Address",
        "addr1": "2 thing st",
        "city": "somewheretown",
        "zipcode": 12345
    }

then the person will automatically update to

    {
        "key": "897654",
        "type": "Person",
        "name": "Fred",
        "address": 
        {
            "key": "1234567",
            "addr1": "2 thing st",
            "city": "somewheretown",
            "zipcode": 12345
        }
    }

Denormalized Object Linking also supports [pybOTL transform templates] (https://github.com/emlynoregan/pybOTL). gaedocstore
can take a list of "name", "transform" pairs. When a key appears like 
    {
        ...
        "something": { key: XXX },
        ...
    }
    
then gaedocstore loads the key referenced. If found, it looks in its list of transform names. If it finds one, it applies
that transform to the loaded object, and puts the output into the stored GDSDocument. If no transform was found, then the 
entire object is put into the stored GDSDocument as described above.

eg:

Say we have the transform "address" as follows:

    ltransform = {
        "fulladdr": "{{.addr1}}, {{.city}} {{.zipcode}}"
    }
    
You can store this transform against the name "address" for gaedocstore to find as follows:

    GDSDocument.StorebOTLTransform("address", ltransform)
    
Then when Person above is stored, it'll have its address placed inline as follows:

    {
        "key": "897654",
        "type": "Person",
        "name": "Fred",
        "address": 
        {
            "key": "1234567",
            "fulladdr": "2 thing st, somewheretown 12345"
        }
    }

An analogous process happens to embedded addresses whenever the Address object is updated.

You can lookup the bOTL Transform with:

    ltransform = GDSDocument.GetbOTLTransform("address")
    
and delete it with

    GDSDocument.DeletebOTLTransform("address")

Desired feature (not yet implemented): If the template itself is updated, then all objects affected by that template are also updated.

### Deletion

If an object is deleted, then all denormalized links will be updated with a special key "link_missing": True. For example, say 
we delete address "1234567" . Then Person will become:

    {
        "key": "897654",
        "type": "Person",
        "name": "Fred",
        "address": 
        {
            "key": "1234567",
            "link_missing": True
        }
    }

And if the object is recreated in the future, then that linked data will be reinstated as expected.

Similarly, if an object is saved with a link, but the linked object can't be found, "link_missing": True will be included as above.

### updating denormalized linked data back to parents

The current version does not support this, but in a future version we may support the ability to change the denormalized information,
and have it flow back to the original object. eg: you could change addr1 in address inside person, and it would 
fix the source address. Note this wont work when transforms are being used (you would need inverse transforms).

# License

Copyright (c) 2013 Emlyn O'Regan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
