from google.appengine.ext.ndb import Expando, JsonProperty, Key, GenericProperty
from google.appengine.ext.ndb.model import put_multi
import bOTL
from google.appengine.ext.ndb.blobstore import delete_multi

LINKS_KEY = "denormalizedobjectlinks__"
BOTLTRANSFORM_TYPE = "bOTLTransform"

class GDSDocument (Expando):
    def Update(self):
        aDict = self.to_dict()
        aUpdatedDict = UpdateDenormalizedObjectLinking(aDict)
        retval = DictToGDSDocument(aUpdatedDict)
        return retval
    
    @classmethod
    def ConstructFromDict(cls, aDict, aReplace=True):
        aDenormalizedDict = UpdateDenormalizedObjectLinking(aDict)
        
        
        if aReplace:
            retval = DictToGDSDocument(aDenormalizedDict)
        else:
            lgdsDocument = None
            if aDict and IsDict(aDict) and "key" in aDict:
                lkeyid = aDict["key"]
                lkey = Key(GDSDocument, lkeyid)
                lgdsDocument = lkey.get()

            retval = DictToGDSDocument(aDenormalizedDict, lgdsDocument)
        
        return retval

    @classmethod
    def _post_put_hook(cls, future):
        # here, we've done the update. Now, fix all objects that have denormalized links to this object.
        lgdsDocumentKey = future.get_result()
        if lgdsDocumentKey:
#            lgdsDocument = lgdsDocumentKey.get()
#            if lgdsDocument:
            FixAllLinkingGDSDocuments(lgdsDocumentKey)

    @classmethod
    def _post_delete_hook(cls, key, future):
        # here, we've done the delete. Now, fix all objects that have denormalized links to this object.
        if key:
            FixAllLinkingGDSDocuments(key)

    def to_dict(self, *args, **kwargs):
        retval = super(GDSDocument, self).to_dict(*args, **kwargs)
        # add in the key, we want it. But only if there is one; nested objects may not have one.
        if self.key:
            retval["key"] = self.key.id()

        if LINKS_KEY in retval:
            del retval[LINKS_KEY]

        return retval

    def _to_dict(self, *args, **kwargs):
        retval = super(GDSDocument, self)._to_dict(*args, **kwargs)
        # add in the key, we want it. But only if there is one; nested objects may not have one.
        if self.key:
            retval["key"] = self.key.id()
        return retval
    
    @classmethod
    def StorebOTLTransform(cls, aTransformName, aTransform):
        if not (aTransform and IsDict(aTransform)):
            raise Exception("Transform must be a dictionary")
        
        ltransformDict = {"type": BOTLTRANSFORM_TYPE, "name": aTransformName, "transform": aTransform}
        
        ltransformDocument = GDSDocument.query().filter(GenericProperty("type") == BOTLTRANSFORM_TYPE).filter(GenericProperty("name") == aTransformName).get()
        
        if ltransformDocument:
            ltransformDict["key"] = ltransformDocument.key().id
            
        ltransformDocument = cls.ConstructFromDict(ltransformDict)
        if ltransformDocument:
            ltransformDocument.put()
        
    @classmethod
    def GetbOTLTransform(cls, aTransformName):
        retval = None

        ltransformDocument = GDSDocument.query().filter(GenericProperty("type") == BOTLTRANSFORM_TYPE).filter(GenericProperty("name") == aTransformName).get()
        
        if ltransformDocument and "transform" in ltransformDocument._properties:
            retval = ltransformDocument.transform.to_dict()
        
        return retval

    @classmethod
    def DeletebOTLTransform(cls, aTransformName):
        ldocuments, lcursor, lmore = GDSDocument.query().filter(GenericProperty("type") == BOTLTRANSFORM_TYPE).filter(GenericProperty("name") == aTransformName).fetch_page(10)
        
        while ldocuments:
            delete_multi(ldocuments)
            #
            if lmore:
                ldocuments, lcursor, lmore = GDSDocument.query().filter(GenericProperty("type") == BOTLTRANSFORM_TYPE).filter(GenericProperty("name") == aTransformName).fetch_page(10, start_cursor=lcursor)
            else:
                ldocuments = []

class GDSJson (Expando):
    json = JsonProperty()
    
    def _to_dict(self, *args, **kwargs):
        retval = super(GDSJson, self)._to_dict(*args, **kwargs)
        retval = retval["json"]
        return retval

def FixAllLinkingGDSDocuments(aGDSDocumentKey):
    if aGDSDocumentKey:
        lkeyid = aGDSDocumentKey.id()
        if lkeyid:
            lgp = GenericProperty()
            lgp._name = LINKS_KEY
            ldocuments, lcursor, lmore = GDSDocument.query(lgp == lkeyid).fetch_page(10)
            while ldocuments:
                lnewDocuments = []
                for ldocument in ldocuments:
                    lnewDocuments.append(ldocument.Update())
                if lnewDocuments:
                    put_multi(lnewDocuments)
                #
                if lmore:
                    ldocuments, lcursor, lmore = GDSDocument.query(lgp == lkeyid).fetch_page(10, start_cursor=lcursor)
                else:
                    ldocuments = []
                    
def DictToGDSDocument(aDict, aBaseGDSDocument = None):
    def _objectToGDSDocument(aSource, aBaseGDSDocument = None):
        retval = None
        if IsDict(aSource):
            if aBaseGDSDocument:
                retval = aBaseGDSDocument
            else:
                retval = GDSDocument()
                
            for lkey, lvalue in aSource.iteritems():
                if lkey == "key":
                    retval.key = Key(GDSDocument, lvalue)
                else:
                    lchildBaseDocument = None
                    if aBaseGDSDocument and IsDict(aBaseGDSDocument) and lkey in aBaseGDSDocument:
                        lchildBaseDocument = aBaseGDSDocument[lkey]
                    lconvertedValue = _objectToGDSDocument(lvalue, lchildBaseDocument)                    
                    retval.populate(**{lkey: lconvertedValue})
        elif IsList(aSource):
            if IsListOfSimpleValues(aSource):
                retval = aSource
            else:
                retval = GDSJson()
                retval.json = aSource
        else:
            retval = aSource
        return retval
    
    if IsDict(aDict):
        retval = _objectToGDSDocument(aDict, aBaseGDSDocument)
        return retval
    else:
        raise Exception("Input must be a Dict")

def UpdateDenormalizedObjectLinking(aDict):
    def _updateDenormalizedObjectLinking(aSource, aLinksList):
        retval = None
        if IsDict(aSource):
            retval = {}
            for lkey, lvalue in aSource.iteritems():
                # anywhere where the lvalue is a dict containing a key "key", we need to do denormalized object linking
                if IsDict(lvalue) and "key" in lvalue:
                    aTarget = {}
                    aTarget["key"] = lvalue["key"]
                    #aTarget.update(lvalue)
                    
                    llinkkeyid = lvalue["key"]
                    
                    aLinksList.append(llinkkeyid)
                    
                    llinkobj = None
                    if llinkkeyid:
                        llinkkey = Key(GDSDocument, llinkkeyid)
                        llinkobj = llinkkey.get()
                    
                    if llinkobj:
                        # we have a linked object. Populate aTarget with values from the linked object.
                        llinkdict = llinkobj.to_dict()

                        # do transform if ther is one
                        ltransform = GDSDocument.GetbOTLTransform(lkey)
                        if ltransform:
                            llinkdict = bOTL.Transform(llinkdict, ltransform)
                        
                        if "key" in llinkdict:
                            del llinkdict["key"]
                        aTarget.update(llinkdict)
                    else:
                        aTarget["link_missing"] = True
                        
                    retval[lkey] = aTarget
                else:
                    retval[lkey] = _updateDenormalizedObjectLinking(lvalue, aLinksList)
        elif IsList(aSource):
            retval = []
            for lvalue in aSource:
                retval.append(_updateDenormalizedObjectLinking(lvalue, aLinksList))
        else:
            retval = aSource
        return retval
    
    if IsDict(aDict):
        llinksList = []
        retval = _updateDenormalizedObjectLinking(aDict, llinksList)
        if llinksList:
            retval[LINKS_KEY] = llinksList
        return retval
    else:
        raise Exception("Input must be a Dict")
    
def IsDict(aTransform):
    retval = isinstance(aTransform, dict)
    
    return retval

def IsList(aTransform):
    retval = isinstance(aTransform, list)
    
    return retval

def IsListOfSimpleValues(aList):
    retval = isinstance(aList, list)
    
    if retval:
        for aItem in aList:
            retval = not IsDict(aItem) and not IsList(aItem)
            if not retval:
                break
    
    return retval
