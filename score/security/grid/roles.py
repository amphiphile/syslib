# coding: utf-8

import simplejson as json
from ru.curs.celesta.showcase.utils import XMLJSONConverter
from common.sysfunctions import toHexForXml
from ru.curs.celesta.syscursors import RolesCursor

try:
    from ru.curs.showcase.core.jython import JythonDTO
except:
    from ru.curs.celesta.showcase import JythonDTO


def gridData(context, main=None, add=None, filterinfo=None,
             session=None, elementId=None, sortColumnList=None, firstrecord=None, pagesize=None):
    u'''Функция получения данных для грида. '''

    # Создание экземпляра курсора разрешения
    roles = RolesCursor(context)    
    # Определяем переменную для JSON данных
    data = {"records":{"rec":[]}}
    # Проходим по таблице и заполняем data
    specialRoles = ["!'editor'", "!'reader'"]    

    roles.setFilter("id", '&'.join(specialRoles))
    columnsDict={u"Роль":"id",
                 u"Описание":"description"}
    for column in sortColumnList:
        sortindex = '%s' % column.getSorting()        
        roles.orderBy(columnsDict[column.getId()] +' '+sortindex)
    if roles.tryFirst():
        while True:
            rolesDict = {}
            rolesDict[toHexForXml('~~id')] = roles.id
            rolesDict[u"Роль"] = roles.id
            rolesDict[u"Описание"] = roles.description
            
            rolesDict['properties'] = {"event":{"@name":"row_single_click",
                                                "action":{"#sorted":[{"main_context": 'current'},
                                                                     {"datapanel":{'@type':"current",
                                                                                   '@tab':"current",
                                                                                   "element":{"@id":"id_perm_roles_grid"}
                                                                                   }
                                                                      }]
                                                          }
                                                }
                                      }
            data["records"]["rec"].append(rolesDict)
            if not roles.next():
                break


    res = XMLJSONConverter.jsonToXml(json.dumps(data))
    return JythonDTO(res, None)

def gridMeta(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Функция получения настроек грида. '''

    # Курсор таблицы directories
    roles = RolesCursor(context)
    # Вычисляем количества записей в таблице
    totalcount = roles.count()
    # Заголовок таблицы
    header = "Роли"
    # В случае если таблица пустая
    if totalcount == 0 or totalcount is None:
        totalcount = "0"
        header = header + " ПУСТ"

    # Определяем список полей таблицы для отображения
    settings = {}
    settings["gridsettings"] = {"columns": {"col":[]},
    "properties": {"@pagesize":"50", "@gridWidth": "900px", "@totalCount": totalcount, "@profile":"default.properties"},
    "labels":{"header":header}
    }
    # Добавляем поля для отображения в gridsettings
    settings["gridsettings"]["columns"]["col"].append({"@id":"Роль", "@width": "80px"})
    settings["gridsettings"]["columns"]["col"].append({"@id":"Описание", "@width": "400px"})

    res = XMLJSONConverter.jsonToXml(json.dumps(settings))
    return JythonDTO(None, res)

def gridToolBar(context, main=None, add=None, filterinfo=None, session=None, elementId=None):
    u'''Toolbar для грида. '''

    if 'currentRecordId' not in json.loads(session)['sessioncontext']['related']['gridContext']:
        style = "true"
    else:
        style = "false"

    data = {"gridtoolbar":{"item":[{"@img": 'gridToolBar/addDirectory.png',
                                    "@text":"Добавить",
                                    "@hint":"Добавить",
                                    "@disable": "false",
                                    "action":{"@show_in": "MODAL_WINDOW",
                                              "#sorted":[{"main_context":"current"},
                                                         {"modalwindow":{"@caption": "Добавление роли",
                                                                         "@height": "300",
                                                                         "@width": "450"
                                                                         }
                                                          },
                                                         {"datapanel":{"@type": "current",
                                                                       "@tab": "current",
                                                                       "element": {"@id": "id_roles_form",
                                                                                   "add_context":"add"}
                                                                       }
                                                          }]
                                              }
                                    },
                                   {"@img": 'gridToolBar/editDocument.png',
                                    "@text":"Редактировать",
                                    "@hint":"Редактировать",
                                    "@disable": style,
                                    "action":{"@show_in": "MODAL_WINDOW",
                                              "#sorted":[{"main_context":"current"},
                                                         {"modalwindow":{"@caption": "Редактирование роли",
                                                                         "@height": "300",
                                                                         "@width": "450"
                                                                         }
                                                          },
                                                         {"datapanel":{"@type": "current",
                                                                       "@tab": "current",
                                                                       "element": {"@id": "id_roles_form",
                                                                                   "add_context":"edit"}
                                                                       }
                                                          }]
                                              }
                                    },
                                   {"@img": 'gridToolBar/deleteDocument.png',
                                    "@text":"Удалить",
                                    "@hint":"Удалить",
                                    "@disable": style,
                                    "action":{"@show_in": "MODAL_WINDOW",
                                              "#sorted":[{"main_context":"current"},
                                                         {"modalwindow":{"@caption": "Удаление роли",
                                                                         "@height": "300",
                                                                         "@width": "450"
                                                                         }
                                                          },
                                                         {"datapanel":{"@type": "current",
                                                                       "@tab": "current",
                                                                       "element": {"@id": "id_roles_form_delete",
                                                                                   "add_context":"delete"}
                                                                       }
                                                          }]
                                              }
                                    },
                                   {"@img": 'gridToolBar/addDirectory.png',
                                    "@text":"Пользователи",
                                    "@hint":"Пользователи",
                                    "@disable": style,
                                    "action":{"@show_in": "MODAL_WINDOW",
                                              "#sorted":[{"main_context":"current"},
                                                         {"modalwindow":{"@caption": "Назначение пользователей для роли",
                                                                         "@height": "400",
                                                                         "@width": "450"
                                                                         }
                                                          },
                                                         {"datapanel":{"@type": "current",
                                                                       "@tab": "current",
                                                                       "element": {"@id": "id_roles_users_form",
                                                                                   "add_context":"users"}
                                                                       }
                                                          }]
                                              }
                                    }]
                           }
            }
    
    data["gridtoolbar"]["item"].append(    {"@img": 'gridToolBar/arrowDown.png',
                                            "@text":"Скачать",
                                            "@hint":"Скачать роли в xml",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Скачать роли",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "rolesDownloadXform",
                                                                                           "add_context":"download"}
                                                                               }
                                                                  }]
                                                      }
                                            }
                                       )    
    data["gridtoolbar"]["item"].append(    {"@img": 'gridToolBar/arrowUp.png',
                                            "@text":"Загрузить",
                                            "@hint":"Загрузить роли из xml",
                                            "@disable": "false",
                                            "action":{"@show_in": "MODAL_WINDOW",
                                                      "#sorted":[{"main_context":"current"},
                                                                 {"modalwindow":{"@caption": "Загрузить роли",
                                                                                 "@height": "300",
                                                                                 "@width": "450"}
                                                                  },
                                                                 {"datapanel":{"@type": "current",
                                                                               "@tab": "current",
                                                                               "element": {"@id": "rolesUploadXform",
                                                                                           "add_context":"upload"}
                                                                               }
                                                                  }]
                                                      }
                                            }
                                       )

    return XMLJSONConverter.jsonToXml(json.dumps(data))
