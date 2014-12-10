# coding: utf-8
import os
import sys
import re
import uuid
from org.xml.sax.helpers import XMLReaderFactory
from org.xml.sax.ext import DefaultHandler2
from org.xml.sax import InputSource
from  javax.xml.stream import XMLOutputFactory
from java.io import FileInputStream, StringWriter, FileOutputStream, OutputStreamWriter
from java.lang import String
from ru.curs.celesta import CelestaException


class settingsManager():
    u'''Класс получения настроек свойств для всех гранул'''
    def _getSettingsFilePath(self, isNew=''):
        u'''Функция получения пути с файлом настроек'''
        settingsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grainsSettings%s.xml' % isNew)
        return settingsPath

    def _createReader(self, path, value, xmlWriter):
        u'''функция создания ридера для чтения файла настроек, с учетом указанного пути'''
        pathList = list()
        name = "[a-zA-Z_А-Яа-я][a-zA-Z_А-Яа-я_0-9-]+"
        elementPatern = re.compile(r"""(%s)(?:\[(?:@(%s)=(?:'([^']+)'|\"([^\"]+)\")|([0-9]+))\])?(?:/@(%s))?""" % (name, name, name), re.UNICODE)
        lastEnd = -1
        for a in elementPatern.finditer(unicode(path)):
            if lastEnd + 1 != a.start(0) or (lastEnd > 0 and path[lastEnd]not in ('/', '\\')) :
                raise CelestaException('Bad XPath expression')
            pathList.append(NodeProperties(a.groups()))
            lastEnd = a.end(0)

        parser = XMLReaderFactory.createXMLReader()
        handler = WriteSettings(pathList, xmlWriter, value)
        parser.setContentHandler(handler)
        parser.setErrorHandler(handler)
        parser.setFeature("http://xml.org/sax/features/namespace-prefixes", True)
        parser.setProperty("http://xml.org/sax/properties/lexical-handler", handler)
        stream = FileInputStream(self._getSettingsFilePath())
        parser.parse(InputSource(stream))

        return handler.result

    def _getSettings(self, path):
        return self._createReader(path, None, None)

    def getGeneralSettings(self, path):
        return self._getSettings('grainSettings/generalSettings/%s' % path)

    def getGrainSettings(self, grain, path):
        return self._getSettings('grainSettings/grains/grain[@name="%s"]/%s' % (grain, path))

    def _setSettings(self, path, value):

        newFilePath = self._getSettingsFilePath(uuid.uuid1())
        stringWriter = OutputStreamWriter(FileOutputStream(newFilePath), "UTF8")
        xmlWriter = XMLOutputFactory.newInstance().createXMLStreamWriter(stringWriter)

        result = self._createReader(path, value, xmlWriter)

        xmlWriter.close()
        stringWriter.close()

        os.rename(self._getSettingsFilePath(), self._getSettingsFilePath('_old'))
        os.rename(newFilePath, self._getSettingsFilePath())
        os.remove(self._getSettingsFilePath('_old'))

        return result

    def setGeneralSettings(self, path, value):
        return self._setSettings('grainSettings/generalSettings/%s' % path, value)

    def setGrainSettings(self, grain, path, value):
        return self._setSettings('grainSettings/grains/[@name="%s"]/%s' % (grain, path), value)

class NodeProperties():
    def __init__(self, properties, newValue=None):
        self.node = properties[0]
        self.attrCond = properties[1]
        self.attrValue1 = properties[2]
        self.attrValue2 = properties[3]
        self.index = int(properties[4]) if properties[4] else None
        self.attr = properties[5]
        self.curIndex = 0

class ReadSettings(DefaultHandler2):
    u'''SAX-parser для xforms, в которую необходимо вставить правила'''
    def __init__(self, pathList):
        self.pathList = pathList
        self.result = []
        self.curResult = u''
        self.isFind = False
        self.curNum = 0
        self.curLevel = 0

    def compareNames(self, expected, actual, attrs):
        if actual == expected.node:
            expected.curIndex += 1
        if actual != expected.node:
            return False
        elif expected.attrCond is not None and attrs.getValue(expected.attrCond) is None:
            return False
        elif attrs.getValue(expected.attrCond)  is not None and attrs.getValue(expected.attrCond) != expected.attrValue1 and \
            attrs.getValue(expected.attrCond) != expected.attrValue2:
            return False
        elif expected.index is not None and expected.index != expected.curIndex:
            return False
        elif expected.attr is not None and attrs.getValue(expected.attr) is None:
            return False

        return True
    def startDocument(self):
        pass
    def endDocument(self):
        pass

    def startElement(self, namespaceURI, lname, qname, attrs):
        self.curLevel += 1
        if not self.isFind and len(self.pathList) > self.curNum and self.compareNames(self.pathList[self.curNum], lname, attrs):
            self.curNum += 1
            if len(self.pathList) == self.curNum:
                if self.pathList[self.curNum - 1].attr is not None:
                    self.result.append(attrs.getValue(self.pathList[self.curNum - 1].attr))
                    self.curNum -= 1
                else:
                    self.isFind = True




    def endElement(self, uri, lname, qname):

        if lname == self.pathList[self.curNum - 1].node:
            if len(self.pathList) > self.curNum + 1:
                self.pathList[self.curNum + 1].curIndex = 0
            self.curNum -= 1

        if self.isFind and self.curLevel == len(self.pathList):
            self.result.append(self.curResult.strip())
            self.curResult = u''
            self.isFind = False

        self.curLevel -= 1

    def comment(self, ch, start, length):
        pass

    def startPrefixMapping(self, prefix, uri):
        pass

    def characters(self, ch, start, length):
        if self.isFind:
            self.curResult += unicode(String(ch[start:start + length]))

    def processingInstruction(self, target, data):
        pass

    def skippedEntity(self, name):
        pass

class WriteSettings(DefaultHandler2):
    u'''SAX-parser для xforms, в которую необходимо вставить правила'''
    def __init__(self, pathList, xmlWriter=None, newValue=None):
        self.pathList = pathList
        self.result = []
        self.curResult = u''
        self.isFind = False
        self.curNum = 0
        self.curLevel = 0
        self.xmlWriter = xmlWriter
        self.newValue = newValue
        self.isWrite = False if xmlWriter is None else True

    def compareNames(self, expected, actual, attrs):
        if actual == expected.node:
            expected.curIndex += 1
        if actual != expected.node:
            return False
        elif expected.attrCond is not None and attrs.getValue(expected.attrCond) is None:
            return False
        elif attrs.getValue(expected.attrCond)  is not None and attrs.getValue(expected.attrCond) != expected.attrValue1 and \
            attrs.getValue(expected.attrCond) != expected.attrValue2:
            return False
        elif expected.index is not None and expected.index != expected.curIndex:
            return False
        elif expected.attr is not None and attrs.getValue(expected.attr) is None:
            return False

        return True
    def startDocument(self):
        if self.isWrite:
            self.xmlWriter.writeStartDocument("UTF-8", "1.0")
    def endDocument(self):
        if self.isWrite:
            self.xmlWriter.writeEndDocument()

    def startElement(self, namespaceURI, lname, qname, attrs):
        self.curLevel += 1

        if not self.isFind and len(self.pathList) > self.curNum and self.compareNames(self.pathList[self.curNum], lname, attrs):
            self.curNum += 1
            if self.isWrite:
                self.xmlWriter.writeStartElement(qname)
            if len(self.pathList) == self.curNum:
                if self.pathList[self.curNum - 1].attr is not None:
                    self.result.append(attrs.getValue(self.pathList[self.curNum - 1].attr))
                    if self.isWrite:
                        for i in range(0, attrs.getLength()):
                            if self.pathList[self.curNum - 1].attr == attrs.getQName(i):
                                self.xmlWriter.writeAttribute(attrs.getQName(i), self.newValue)
                            else:
                                self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
                    self.curNum -= 1

                else:
                    self.isFind = True
                    if self.isWrite:
                        for i in range(0, attrs.getLength()):
                            self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
                        self.xmlWriter.writeCharacters(self.newValue)
                        self.xmlWriter.writeEndElement()

            elif self.isWrite:
                for i in range(0, attrs.getLength()):
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))

        elif not self.isFind and self.isWrite:
            self.xmlWriter.writeStartElement(qname)
            for i in range(0, attrs.getLength()):
                    self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))
        #else:
            #for i in range(0, attrs.getLength()):
                #self.xmlWriter.writeAttribute(attrs.getQName(i), attrs.getValue(i))



    def endElement(self, uri, lname, qname):
        if lname == self.pathList[self.curNum - 1].node:
            if len(self.pathList) > self.curNum + 1:
                self.pathList[self.curNum + 1].curIndex = 0
            self.curNum -= 1

        if not self.isFind and self.isWrite:
            self.xmlWriter.writeEndElement()
        elif self.isFind and self.curLevel == len(self.pathList):
            self.result.append(self.curResult.strip())
            self.curResult = u''
            self.isFind = False


        self.curLevel -= 1

    def comment(self, ch, start, length):
        if not self.isFind and self.isWrite:
            self.xmlWriter.writeComment(''.join(ch[start:start + length]))

    def startPrefixMapping(self, prefix, uri):
        if prefix == "" and self.isWrite:
            self.xmlWriter.setDefaultNamespace(uri)
        elif  self.isWrite:
            self.xmlWriter.setPrefix(prefix, uri)

    def characters(self, ch, start, length):
        if self.isFind:
            self.curResult += unicode(String(ch[start:start + length]))
        elif self.isWrite:
            self.xmlWriter.writeCharacters(ch, start, length)

    def processingInstruction(self, target, data):
        if not self.isFind and self.isWrite:
            self.xmlWriter.writeProcessingInstruction(target, data)

    def skippedEntity(self, name):
        if not self.isFind and self.isWrite:
            self.xmlWriter.writeEntityRef(name)

class ReadXMLError(Exception):
    pass


