from google.appengine.ext.ndb import Expando, JsonProperty

class GDSDocument (Expando):
    pass

class GDSJson (Expando):
    json = JsonProperty()
    
    def _to_dict(self):
        retval = super(GDSJson, self).to_dict()
        retval = retval["json"]
        return retval

def DictToGDSDocument(aSource):
    def _objectToGDSDocument(aSource):
        retval = None
        if IsDict(aSource):
            retval = GDSDocument()
            for lkey, lvalue in aSource.iteritems():
                lconvertedValue = _objectToGDSDocument(lvalue)
                retval.populate(**{lkey: lconvertedValue})
        elif IsList(aSource):
            retval = GDSJson()
            retval.json = aSource
        else:
            retval = aSource
        return retval
    
    if IsDict(aSource):
        return _objectToGDSDocument(aSource)
    else:
        raise Exception("Source must be a Dict")

def GDSDocumentToDict(aGDSDocument):
    if not isinstance(aGDSDocument, GDSDocument):
        raise Exception("Input must be a GDSDocument")

    retval = aGDSDocument.to_dict()
    
    return retval
            

#def FixToDict(aInput):
#    retval = None
#    
#    if IsDict(aInput):
#        retval = {}
#        for lkey, lvalue in aInput.iteritems():
#            retval[lkey] = FixToDict(lvalue)
#    elif IsList(aInput):
#        retval = []
#        for litem in aInput:
#            if hasattr(litem, "to_dict"):
#                retval.append(FixToDict(litem.to_dict()))
#            else:
#                retval.append(litem)
#    else:
#        retval = aInput
#        
#    return retval
    
def IsDict(aTransform):
    retval = isinstance(aTransform, dict)
    
    return retval

def IsList(aTransform):
    retval = isinstance(aTransform, list)
    
    return retval
