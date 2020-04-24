# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex as colorHex

from selements import SLabel, SOptionTextInput

class SOptionElement(BoxLayout):

    formulaId = None
    paraDesc = None
    paraDict = None
    paraStrDict = None
    paraList = None

    def __init__(self, paramDict, **kwargs):
        super(SOptionElement, self).__init__(**kwargs)
        
        optionDict = paramDict.get("OptionDict")
        self.formulaId = optionDict.get("FormulaID")
        self.paraDesc = optionDict.get("ParaDesc")
        self.paraDict = {}
        self.paraStrDict = {}
        self.paraList = optionDict.get("ParameterList")
        for aDict in self.paraList:
            self.paraDict[aDict.get("Name")] = aDict
        
        self._objDict = {}
        self.size_hint = (1, .98)
        self.orientation = "horizontal"

        self._isSelected_id = CheckBox()
        self._isSelected_id.active = False
        self._isSelected_id.size_hint = (.1, 1)
        self._isSelected_id.color = colorHex("#000000")
        self.add_widget(self._isSelected_id)
        
        self.add_widget(BoxLayout(size_hint = (.01, 1)))

        self.contentLayout = BoxLayout(size_hint = (.89, 1), orientation = "horizontal")
        self.add_widget(self.contentLayout)
        
        if self.hasFunc(self.paraDesc):
            strList = self.paraDesc.split(" ")
            for astr in strList:
                if self.hasFunc(astr):
                    paraName = astr[astr.find("#")+1:]
                    self.paraStrDict[paraName] = astr
                    _atextInput = SOptionTextInput(paraName = paraName,size_hint = (None, 1))
                    _atextInput.text = self.paraDict.get(paraName).get("Def")
                    _atextInput.width = 60
                    self.contentLayout.add_widget(_atextInput)
                    self._objDict[paraName] = _atextInput
                else:                    
                    _alabel = SLabel(text = astr, size_hint = (None, 1))
                    _alabel.width = self.calcStrWidth(astr)
                    _alabel.color = colorHex("#000000")
                    self.contentLayout.add_widget(_alabel)
        else:
            _alabel = SLabel(text=self.paraDesc, size_hint=(1, 1))
            _alabel.color = colorHex("#000000")
            self.contentLayout.add_widget(_alabel)

    def hasFunc(self, paraDesc):
        if paraDesc.find("#") != -1:
            return True
        else:
            return False

    def calcStrWidth(self, astr):
        strWidth = 0
        for i in range(len(astr)):
            if astr[i].isascii():
                strWidth += 10
            else:
                strWidth += 16
        return strWidth

    def isSelected(self):
        return self._isSelected_id.active

    def setToDefaultValue(self):
        self._isSelected_id.active = False
        if len(self._objDict) != 0:
            aObj = None
            for aKey in self._objDict.keys():
                aObj = self._objDict.get(aKey)
                aObj.text = self.paraDict.get(aObj.paraName).get("Def")

    def getOptionDesc(self):
        if len(self._objDict) == 0:
            return self.paraDesc
        result = self.paraDesc
        aObj = None
        for aKey in self._objDict.keys():
            aObj = self._objDict.get(aKey)
            paraStr = self.paraStrDict.get(aObj.paraName)
            result = result.replace(paraStr, aObj.text)
        return result

    def getValueDict(self):
        valueDict = {}
        paraStr = ""
        for adict in self.paraList:
            nameStr = adict.get("Name")
            atextInput = self._objDict.get(nameStr)
            if atextInput == None:
                paraStr += adict.get("Def")
                paraStr += "|"
            else:
                paraStr += atextInput.text
                paraStr += "|"                
        if paraStr != "":
            paraStr = paraStr[:-1]
        valueDict["FormulaID"] = int(self.formulaId)
        valueDict["Parameter"] = paraStr
        return valueDict