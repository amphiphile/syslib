# coding: utf-8
import os
from ru.curs.celesta import CelestaException

def toHexForXml(s):
    '''Функция модифицирует спецсимволы в строке в формат пригодный для имен тегов xml'''
    lst = []
    for ch in s:
        numCh = ord(ch)
        if numCh not in xrange (48, 58) and\
        numCh not in xrange (65, 91) and\
        numCh not in xrange (97, 123) and \
        numCh not in xrange (1040, 1104):
            lst.append('_x%s_' % ('000%s' % hex(numCh)[2:])[-4:])
        else:
            lst.append(ch)

    return reduce(lambda x, y:x + y, lst)

def tableCursorImport(grainName, tableName):
    u'''Функция, импортирующая  класс курсора на таблицу'''

    # Bмпорт гранулы
    _grain_orm = __import__("%s._%s_orm" % (grainName, grainName), globals(), locals(), "%sCursor" % tableName, -1)

    return getattr(_grain_orm, "%sCursor" % tableName)

