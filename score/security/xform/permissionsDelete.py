# coding: utf-8


import simplejson as json
import base64

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from ru.curs.celesta.syscursors import PermissionsCursor

def cardData(context, main, add, filterinfo=None, session=None, elementId=None):
    xformsdata = {"schema":{"@xmlns":""}}
    xformssettings = {"properties":{"event":[{"@name":"single_click",
                                             "@linkId": "1",
                                             "action":{"main_context": "current",
                                                       "datapanel": {"@type": "current",
                                                                     "@tab": "current",
                                                                     "element": {"@id":"permGrid",
                                                                                 "add_context": ""
                                                                                 }
                                                                     }
                                                       }
                                             }]
                                    }
                      }
    jsonData = XMLJSONConverter.jsonToXml(json.dumps(xformsdata))
    jsonSettings = XMLJSONConverter.jsonToXml(json.dumps(xformssettings))
    return JythonDTO(jsonData, jsonSettings)

def cardDelete(context, main=None, add=None, filterinfo=None, session=None, elementId=None, xformsdata=None):
    currentRecordId = json.loads(session)['sessioncontext']['related']['gridContext']['currentRecordId']    
    currId = json.loads(base64.b64decode(currentRecordId))    
    permission = PermissionsCursor(context)
    permission.get(*currId)
    permission.delete()