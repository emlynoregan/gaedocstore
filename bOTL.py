import re

def Transform(aSource, aTransform, aScope = {}):
    ltargetvalue = None
    
    ltargetlist = TransformList(aSource, aTransform, aScope)
    if ltargetlist:
        ltargetvalue = ltargetlist[0]
    
    return ltargetvalue

def TransformList(aSource, aTransform, aScope):
    ltargetlist = []
    
    if IsLiteralString(aTransform):
        ltargetvalue = ProcessLiteralString(aSource, aTransform, aScope)
        ltargetlist.append(ltargetvalue)
    elif IsLiteralValue(aTransform):
        ltargetlist.append(aTransform)
    elif IsLiteralArray(aTransform) or IsLiteralTuple(aTransform):
        ltargetvalue = []
        for ltransformElement in aTransform:
            lchildTargetList = TransformList(aSource, ltransformElement, aScope)
            ltargetvalue.extend(lchildTargetList)
        ltargetlist.append(ltargetvalue)
    elif IsLiteralDict(aTransform):
        ltargetvalue = {}
        for lkey, lvalue in aTransform.iteritems():
            lchildTargetValue = Transform(aSource, lvalue, aScope)
            ltargetvalue[lkey] = lchildTargetValue
        ltargetlist.append(ltargetvalue)
    elif IsSimpleRef(aTransform):
        lselectorexpression = GetSelectorExpressionFromSimpleRef(aTransform)
        ltargetlist = EvaluateSelectorExpression(aSource, lselectorexpression, aScope)
    elif IsComplexRef(aTransform):
        
        ## need to remove "_lit_" prefixes here.
        
        lselectorexpression = aTransform["ref"]
        lselectorsourcelist = EvaluateSelectorExpression(aSource, lselectorexpression, aScope)
        
        if "transform" in aTransform:
            # we're going to transform every selected object
            for lselectorsourceobject in lselectorsourcelist:
                if "id" in aTransform:
                    lchildscope = {}
                    lchildscope.update(aScope) # shallow clone
                    lchildscope[aTransform["id"]] = lselectorsourceobject
                else:
                    lchildscope = aScope
                
                lchildTargetList = TransformList(aSource, aTransform["transform"], lchildscope)
                ltargetlist.extend(lchildTargetList)
        else:
            # no transform, just return all the source objects we found.
            ltargetlist.extend(lselectorsourcelist)
    
    return ltargetlist

def EvaluateSelectorExpression(aSource, aSelectorExpression, aScope = {}):
    lselectedlist = None
    
    if not aSelectorExpression is None:
        lselectedlist = []
        
        lselectorterms = TokenizeSelectorExpression(aSelectorExpression)
        
        if lselectorterms:
            lselectedlist = EvaluateSelector(aSource, lselectorterms[0], lselectorterms[1:], aScope)
        else:
            lselectedlist.append(aSource)
        
    return lselectedlist

def EvaluateSelector(aSource, aSelectorTerm, aFollowingSelectorTerms, aScope):
    llocalselectedlist = []
    
    lselectortermtype, lselectortermvalue = ParseSelectorTerm(aSelectorTerm)
    
    if lselectortermtype == ".":
        if IsLiteralDict(aSource) and lselectortermvalue in aSource:
            llocalselectedlist.append(aSource[lselectortermvalue])
    elif lselectortermtype == ">":
        llocalselectedlist = GetObjectsByNameRecursive(aSource, lselectortermvalue)
    elif lselectortermtype == "@":
        llocalselectedlist = ApplyIndexExpressionToArray(aSource, lselectortermvalue)
    elif lselectortermtype == "!":
        if IsLiteralDict(aScope) and lselectortermvalue in aScope:
            llocalselectedlist.append(aScope[lselectortermvalue])
            
    lselectedlist = []
    if aFollowingSelectorTerms:
        lnextSelectorTerm = aFollowingSelectorTerms[0]
        lnextFollowingSelectorTerms = aFollowingSelectorTerms[1:]
        for llocalselectedobject in llocalselectedlist:
            lchildselectedlist = EvaluateSelector(llocalselectedobject, lnextSelectorTerm, lnextFollowingSelectorTerms, aScope)
            for lchildselectedobject in lchildselectedlist:
                if not lchildselectedobject in lselectedlist:
                    lselectedlist.append(lchildselectedobject)
    else:
        for llocalselectedobject in llocalselectedlist:
            if not llocalselectedobject in lselectedlist:
                lselectedlist.append(llocalselectedobject)
    
    return lselectedlist
    
def ProcessLiteralString(aSource, aLiteralString, aScope):
    retval = None
    if IsLiteralString(aLiteralString):
        if ContainsLiteralPrefix(aLiteralString):
            retval = RemoveLiteralPrefixFromString(aLiteralString)
        else:
            # do selector substitutions here
            lworkingCopyOfString = aLiteralString
            
            # find a substitution
            import re
            
            #lregex = re.compile("({{.*?}})")
            lregex = re.compile("{{(.*?)}}")
            lmatch = lregex.search(lworkingCopyOfString)
            while lmatch:
                lselectorExpression = lmatch.group(1)
                lselectedlist = EvaluateSelectorExpression(aSource, lselectorExpression, aScope)
                if not lselectedlist:
                    lreplacevalue = ""
                else:
                    lreplacevalue = unicode(lselectedlist[0])
                
                lworkingCopyOfString = lworkingCopyOfString.replace("{{%s}}" % lselectorExpression, lreplacevalue)
                #
                # get next match
                lmatch = lregex.search(lworkingCopyOfString) # should now be a new string
            retval = lworkingCopyOfString
    return retval
        
def TokenizeSelectorExpression(aSelectorExpression):
    retval = None
    if not aSelectorExpression is None:
        retval = []
        lselectorExpressionTrimmed = aSelectorExpression.strip()
        if lselectorExpressionTrimmed:
            retval = re.split(r'\s+', lselectorExpressionTrimmed)
    return retval

def ParseSelectorTerm(aSelectorTerm):
    lselectortermtype = ""
    lselectortermvalue = ""

    if aSelectorTerm:
        lselectortermtype = aSelectorTerm[0]
        lselectortermvalue = aSelectorTerm[1:]
        
    return lselectortermtype, lselectortermvalue
    
def GetObjectsByNameRecursive(aSource, aName):
    lselectedobjects = []
    
    if IsLiteralDict(aSource):
#        if aName in aSource:
#            lselectedobjects.append(aSource[aName])
#        else:
        for lkey, lvalue in aSource.iteritems():
            if lkey == aName:
                lselectedobjects.append(aSource[aName])
            else:
                lselectedobjects.extend(GetObjectsByNameRecursive(lvalue, aName))
    elif IsLiteralArray(aSource) or IsLiteralTuple(aSource):
#        if aName in aSource:
#            lselectedobjects.append(aSource[aName])
#        else:
        for lchild in aSource:
            lselectedobjects.extend(GetObjectsByNameRecursive(lchild, aName))
    
    return lselectedobjects

def ApplyIndexExpressionToArray(aSource, aIndexExpression):
    retval = []
    lindexTerms = aIndexExpression.split(":")
    if lindexTerms and len(lindexTerms) > 0:
        lstart = None
        lend = None
        lstep = None

        if len(lindexTerms) >= 1:
            try:
                lstart = int(lindexTerms[0])
            except:
                pass
        if len(lindexTerms) >= 2:
            try:
                lend = int(lindexTerms[1])
            except:
                pass
        
        if len(lindexTerms) >= 3:
            try:
                lstep = int(lindexTerms[2])
            except:
                pass

        if lstep is None:
            lstep = 1


        if len(lindexTerms) == 1:
            try:
                retval.append(aSource[lstart])
            except:
                pass
            
        elif len(lindexTerms) >= 2:
            try:
                if lstart is None:
                    if lend is None:
                        retval = aSource[::lstep]
                    else:
                        retval = aSource[:lend:lstep]
                else:
                    if lend is None:
                        retval = aSource[lstart::lstep]
                    else:
                        retval = aSource[lstart:lend:lstep]
            except:
                pass

#    try:
#        lindex = int(aIndexExpression)
#        retval.append(aSource[lindex])
#    except:
#        pass
    return retval

def ContainsLiteralPrefix(aString):
    retval = None
    
    retval = IsString(aString) and aString[:4] == "lit="

    return retval
    
def RemoveLiteralPrefixFromString(aString):
    retval = None
    
    if IsString(aString):
        if (aString[:4] == "lit="):
            retval = aString[4:]
        else:
            retval = aString

    return retval

def RemoveLiteralPrefixFromDict(aDict):
    retval = None
    
    if IsDict(aDict):
        retval = {}
        for lkey, lvalue in aDict.iteritems():
            if (lkey[:5] == "_lit_"):
                retval[lkey[5:]] = lvalue
            else:
                retval[lkey] = lvalue

    return retval

def GetSelectorExpressionFromSimpleRef(aSimpleRefString):
    retval = None
    
    if IsString(aSimpleRefString) and aSimpleRefString[:1] == "#":
        retval = aSimpleRefString[1:]

    return retval

#########################################################################################

def IsLiteralValue(aTransform):
    retval = IsLiteralString(aTransform) or \
            IsLiteralInt(aTransform) or \
            IsLiteralFloat(aTransform) or \
            IsLiteralBool(aTransform) or \
            IsLiteralNull(aTransform)
        
    return retval

def IsLiteralString(aTransform):
    retval = isinstance(aTransform, basestring)
    
    if retval:
        retval = not (aTransform[:1] == "#") # a string that starts with # is a SimpleRef.
    
    return retval

def IsString(aTransform):
    retval = isinstance(aTransform, basestring)

    return retval

def IsLiteralInt(aTransform):
    retval = isinstance( aTransform, ( int, long ) )
    
    return retval

def IsLiteralFloat(aTransform):
    retval = isinstance(aTransform, float)
    
    return retval

def IsLiteralBool(aTransform):
    retval = isinstance(aTransform, bool)
    
    return retval

def IsLiteralNull(aTransform):
    retval = aTransform is None
    
    return retval

# also allow tuples here
def IsLiteralArray(aTransform):
    retval = isinstance(aTransform, list)
    
    return retval

def IsLiteralTuple(aTransform):
    retval = isinstance(aTransform, tuple)
    
    return retval

def IsLiteralDict(aTransform):
    retval = isinstance(aTransform, dict)
    
    if retval:
        retval = not "ref" in aTransform # if it has "ref" in it, then it's a complex transform
    
    return retval

def IsDict(aTransform):
    retval = isinstance(aTransform, dict)
    
    return retval

def IsSimpleRef(aTransform):
    retval = isinstance(aTransform, basestring)
    
    if retval:
        retval = (aTransform[:1] == "#") # a string that starts with "#" is a SimpleRef.
    
    return retval

def IsComplexRef(aTransform):
    retval = isinstance(aTransform, dict)
    
    if retval:
        retval = "ref" in aTransform
    
    return retval



if __name__ == '__main__':
    print "Try running ./main.py"