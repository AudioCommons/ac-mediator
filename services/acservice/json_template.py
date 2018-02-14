# Small utils to apply JSON template language
# author: Miguel Ceriani miguel.ceriani@gmail.com https://github.com/miguel76
# TODO: make standalone library

import time

# Separates a path in the first step and the rest
def headTailOfPath(path):
    parts = path.split('/')
    head = ''
    tail = ''
    headEnded = False
    parCount = 0
    for part in parts:
        if (headEnded):
            tail += '/' + part
        else:
            head += '/' + part
            if not part.endswith('\\'):
                parCount = parCount + part.count('(') - part.count(')')
                if parCount == 0:
                    headEnded = True
    return (head[1:], tail[1:])

def normalizeKeyValue(key, value):
    (keyHead, keyTail) = headTailOfPath(key)
    if (keyTail == ''):
        return (keyHead, value)
    else:
        (normKeyTail, normValue) = normalizeKeyValue(keyTail, value)
        return (keyHead, {normKeyTail: normValue})

def itemsCool(someDict):
    newList = []
    for key, value in someDict.items():
        if isinstance(value, list):
            for singleValue in value:
                newList.append((key, singleValue))
        else:
            newList.append((key, value))
    return newList

def dictCool(somePairList):
    newDict = {}
    for key, value in somePairList:
        if key in newDict:
            if not isinstance(newDict[key], list):
                newDict[key] = [newDict[key]]
            newDict[key].append(value)
        else:
            newDict[key] = value
    return newDict

# Normalize a template by replacing all paths in key positions with full representation
def normalizeTemplate(template):
    if not isinstance(template, dict):
        return template
    else:
        return dictCool(map(lambda keyValuePair: normalizeKeyValue(keyValuePair[0],normalizeTemplate(keyValuePair[1])), itemsCool(template)))

def simpleReplace(outTemplate, input):
    # print(outTemplate)
    if outTemplate == '$':
        # print('catched!')
        # print(input)
        return input
    elif isinstance(outTemplate, dict):
        return dict(map(lambda keyValue: (keyValue[0], simpleReplace(keyValue[1], input)), outTemplate.items()))
    elif isinstance(outTemplate, list):
        return list(map(lambda item: simpleReplace(item, input), outTemplate))
    else:
        return outTemplate

def getDateTime(dateTimeStr):
    try:
        return time.strptime(dateTimeStr, '%Y-%m-%dT%H:%M:%S %Z')
    except:
        try:
            return time.strptime(dateTimeStr, '%Y-%m-%dT%H:%M:%S')
        except:
            try:
                return time.strptime(dateTimeStr, '%Y-%m-%d %Z')
            except:
                try:
                    return time.strptime(dateTimeStr, '%Y-%m-%d')
                except:
                    try:
                        return time.strptime(dateTimeStr, '%H:%M:%S %Z')
                    except:
                        try:
                            return time.strptime(dateTimeStr, '%H:%M:%S')
                        except:
                            return None

def getNumeric(numberStr):
    try:
        return int(numberStr)
    except:
        try:
            return float(numberStr)
        except:
            return None

def xs_dateTime(input, args):
    arg = input if len(args) == 0 else args[0]
    return time.strftime('%Y-%m-%dT%H:%M:%S %Z', getDateTime(arg)).strip()

def fn_concat(input, args):
    return ''.join(map(str,args))

def op_numeric_multiply(input, args):
    argsNumeric = map(getNumeric, args)
    result = 1
    for number in argsNumeric:
        result = None if number == None else result * number
    return result

# dateTime format '-'? yyyy '-' mm '-' dd 'T' hh ':' mm ':' ss ('.' s+)? (zzzzzz)?

definedFunctions = {
    'xs:dateTime': xs_dateTime,
    'fn:concat': fn_concat,
    'op:numeric-multiply': op_numeric_multiply
}

def applyFunctionCall(input, functionName, args):
    if functionName in definedFunctions:
        return definedFunctions[functionName](input, args)
    else:
        return None

def splitConsideringQuotes(text, separator):
    textParts = text.split(separator)
    # TODO do the actual thing, now it's too dumb
    return textParts

def parseAndComputeScalar(input, code):
    code = code.strip()
    if code == '.':
        return input
    elif code.endswith(')'):
        return parseAndApplyFunctionCall(input, code)
    elif code.startswith('\'') and code.endswith('\''):
        return code[1:len(code)-1].replace('\\\'', '\'')
    elif code.startswith('"') and code.endswith('"'):
        return code[1:len(code)-1].replace('\\"', '"')
    elif code == 'true':
        return True
    elif code == 'false':
        return False
    elif code == 'null':
        return None
    else:
        try:
            return int(code)
        except:
            try:
                return float(code)
            except:
                return code

def parseAndApplyFunctionCall(input, code):
    startParPos = code.find('(');
    if startParPos > -1:
        return applyFunctionCall(input, code[:startParPos], list(map(
            lambda parCode: parseAndComputeScalar(input, parCode),
            splitConsideringQuotes(code[startParPos + 1: len(code) - 1], ','))))

def applyPath(input, path):
    path = path.strip()
    returnSeq = []
    if path == '.':
        returnSeq = input
    elif path.endswith(')'):
        returnSeq = parseAndApplyFunctionCall(input, path)
    elif path in input:
        returnSeq = input[path]
    if isinstance(returnSeq, list):
        return returnSeq
    else:
        return [returnSeq]

def applyCreate(input, createPathList):
    # print('applyCreate(')
    # print(input)
    # print(createPathList)
    # print(')')
    if createPathList == '.' or createPathList == '':
        return input
    else:
        inputList = input if isinstance(input, list) else [input]
        if isinstance(createPathList, dict):
            merge = []
            for input in inputList:
                merge = addToDictionary(merge, simpleReplace(createPathList, input))
            return merge
        else:
            if not isinstance(createPathList, list):
                createPathList = [createPathList]
            return dictCool((createPath,input) for createPath in createPathList for input in inputList)

def addToDictionary(mainDict, dictToAdd):
    # print('addToDictionary(')
    # print(mainDict)
    # print(dictToAdd)
    # print(')')
    if isinstance(dictToAdd, dict):
        if not isinstance(mainDict, dict):
            if isinstance(mainDict, list) and len(mainDict) == 0:
                mainDict = {}
            else:
                mainDict = {'@id': mainDict}
        for keyToAdd, valuesToAdd in dictToAdd.items():
            if keyToAdd in mainDict:
                if not isinstance(mainDict[keyToAdd], list):
                    mainDict[keyToAdd] = [mainDict[keyToAdd]]
                if not isinstance(valuesToAdd, list):
                    valuesToAdd = [valuesToAdd]
                mainDict[keyToAdd].extend(valuesToAdd)
            else:
                mainDict[keyToAdd] = valuesToAdd
    else:
        if not isinstance(mainDict, dict):
            if isinstance(mainDict, list) and len(mainDict) == 0:
                mainDict = dictToAdd
            else:
                if not isinstance(mainDict, list):
                    mainDict = [mainDict]
                mainDict.extend(dictToAdd if isinstance(dictToAdd, list) else [dictToAdd])
        else:
            if '@id' in mainDict:
                if not isinstance(mainDict['@id'], list):
                    mainDict['@id'] = [mainDict['@id']]
                mainDict['@id'].extend(dictToAdd if isinstance(dictToAdd, list) else [dictToAdd])
            else:
                mainDict['@id'] = dictToAdd
    return mainDict


def applyTemplate(input, template, normalizeIn = True, normalizeOut = True):
    if normalizeIn:
        template = normalizeTemplate(template)
    if not isinstance(template, dict):
        return applyCreate(input, template)
    createPath = template['@out'] if '@out' in template else '.'
    merge = []
    for selectPath, case in filter(lambda keyValuePair: keyValuePair[0] != '@out', itemsCool(template)):
        for match in applyPath(input, selectPath):
            merge = addToDictionary(merge, applyTemplate(match, case, False, False))
    if merge == []:
        merge = input
    result = applyCreate(merge, createPath)
    if normalizeOut:
        result = normalizeTemplate(result)
    return result

# print(headTailOfPath('musicinfo/tags/pluto'))
# print(headTailOfPath('musicinfo\/tags/pluto'))
# print(headTailOfPath('musicinfo\\/tags/pluto'))
# print(headTailOfPath('musicinfo'))

print(normalizeTemplate({
  "id/fn:concat('soundClips:Jamendo/',.)": "@id",
  "shareurl": "ac:homepage",
  "audiodownload": {
    "@out": {
      "ac:availableAs": {
        "@id": "$",
        "@type": "ac:AudioFile"
      }
    }
  },
  "name": "dc:title",
  ".": {
    "@out": "ac:author",
    "artist_id": "@id",
    "artist_name": "dc:name"
  },
  "image": "ac:image",
  "duration": "ac:duration",
  "license_ccurl": "cc:license",
  "releasedate/xs:dateTime(.)": {
    "@out": {
      "ac_isPublishedAudioManifestation": {
        "@type": "event:Event",
        "event:time": {
          "@type": ["time:TemporalEntity", "time:Instant"],
          "time:inXSDDateTimeStamp": "$"
        }
      }
    }
  },
  "musicinfo/tags": {
    "@out": "ac:audioCategory",
    "genres": ".",
    "instruments": ".",
    "vartags": "."
  }
}))

print(applyTemplate({
    "id": "23123123",
    "shareurl": "http..shareurl",
    "name": "the_name",
    "artist_id": "23423423",
    "artist_name": "the_artist_name",
    "image": "the_image",
    "audiodownload": "the_audiodownload",
    "duration": "192",
    "license_ccurl": "the_license_ccurl",
    "releasedate": "2011-12-29",
    "musicinfo":{
        "tags": {
            "genres": ["rock", "pop"],
            "instruments": ["electric_guitar", "drum set", "harp"],
            "vartags": "happy"
        }
    },
    "pippo": 5
},{
  "id/fn:concat('soundClips:Jamendo/',.)": "@id",
  "shareurl": "ac:homepage",
  "audiodownload": {
    "@out": {
      "ac:availableAs": {
        "@id": "$",
        "@type": "ac:AudioFile"
      }
    }
  },
  "name": "dc:title",
  ".": {
    "@out": "ac:author",
    "artist_id/fn:concat('agents:Jamendo/',.)": "@id",
    "artist_name": "dc:name"
  },
  "image": "ac:image",
  "duration/op:numeric-multiply(.,1000)": "ac:duration",
  "license_ccurl": "cc:license",
  "releasedate/xs:dateTime(.)": {
    "@out": {
      "ac_isPublishedAudioManifestation": {
        "@type": "event:Event",
        "event:time": {
          "@type": ["time:TemporalEntity", "time:Instant"],
          "time:inXSDDateTimeStamp": "$"
        }
      }
    }
  },
  "musicinfo/tags": {
    "@out": "ac:audioCategory",
    "genres/fn:concat('categories:Jamendo/genres/',.)": ".",
    "instruments/fn:concat('categories:Jamendo/instruments/',.)": ".",
    "vartags/fn:concat('categories:Jamendo/vartags/',.)": "."
  }
})) #, True, False))
