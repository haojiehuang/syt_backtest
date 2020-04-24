# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.lang import Builder
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex as colorHex

from selements import SRowButton, SButton, SLabel, SHeadLabel, SPopup, SContentLabel, SBoxLayout, SBoxLayout2
from selements import STextInput, STableBoxLayout, SRowConfirmLayout, STableGridLayout, STableScrollView
import sutil
import sconsts as CONSTS

MAX_SELECT_STK_NUM = 500

with open(os.path.join(os.path.dirname(__file__), "self_stksetting.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class StkQuery(BoxLayout):

    queryStr_id = ObjectProperty(None)
    query_id = ObjectProperty(None)
    body_layout = ObjectProperty(None)
    content_layout = ObjectProperty(None)
    ensureBtn_id = ObjectProperty(None)
    cancelBtn_id = ObjectProperty(None)
    
    def __init__(self, paramDict, **kwargs):
        super(StkQuery, self).__init__(**kwargs)
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        self.resultObjDict = {}
        self.resultIdNameList = []
        
    def _queryStk(self):
        
        queryStr = self.queryStr_id.text
        resultDict = {}
        stkName = None
        resultNum = 0
        for stkId in self.app.stkNameDict.keys():
            if resultNum > MAX_SELECT_STK_NUM:
                break
            stkName = self.app.stkNameDict.get(stkId)
            if stkName.find(queryStr) != -1:
                resultNum += 1
                resultDict[stkId] = stkName
        self.body_layout.remove_widget(self.content_layout)
        if len(resultDict) == 0:
            return
        contentView = STableBoxLayout(size_hint=(1, 1), orientation="vertical")
        
        headLayout = STableGridLayout(cols=3, rows=1, spacing=2, size_hint=(1, None), height=30)
        headLabel = SHeadLabel(text="選擇", size_hint=(.15, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="代碼", size_hint=(.2, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="名稱", size_hint=(.65, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        contentView.add_widget(headLayout)
        
        slview = STableScrollView()
        slview.size_hint = (1, .95)
        contentLayout = STableGridLayout(cols=3, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        contentLayout.bind(minimum_height=contentLayout.setter('height'))
        
        slview.add_widget(contentLayout)
        
        contentView.add_widget(slview)
        
        self.resultObjDict.clear()
        
        rowList = None
        for stkId in resultDict.keys():
            rowList = []
            stkName = resultDict.get(stkId)
            funcLayout = SBoxLayout(size_hint=(.15, None), height=30)
            funcLayout.orientation = "horizontal"
            funcLayout.padding = (1, 1, 1, 1)
            funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
            acbObj = CheckBox()
            acbObj.color = colorHex("#000000")
            acbObj.active = False
            acbObj.size_hint = (1, 1)
            funcLayout.add_widget(acbObj)
            funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
            rowList.append(acbObj)
            contentLayout.add_widget(funcLayout)
            contentLabel = SContentLabel(text=stkId, size_hint=(.2, None), height=30)
            contentLabel.color = colorHex("#000000")
            contentLabel.halign = "center"
            contentLabel.valign = "middle"
            rowList.append(contentLabel)
            contentLayout.add_widget(contentLabel)
            contentLabel = SContentLabel(text=stkName, size_hint=(.65, None), height=30)
            contentLabel.color = colorHex("#000000")
            contentLabel.halign = "left"
            contentLabel.valign = "middle"
            rowList.append(contentLabel)
            contentLayout.add_widget(contentLabel)
        
            self.resultObjDict[stkId] = rowList
        
        self.content_layout = contentView
        self.body_layout.add_widget(self.content_layout)
    
    def doSelectStk(self):
        if len(self.resultObjDict) == 0:
            return
        self.resultIdNameList.clear()     
        rowList = None
        for stkId in self.resultObjDict.keys():
            rowList = self.resultObjDict.get(stkId)
            if rowList[0].active == True:
                self.resultIdNameList.append([stkId, rowList[2].text])

class SelfStkSetting(BoxLayout):
        
    def __init__(self, paramDict, **kwargs):
        super(SelfStkSetting, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        self.selfgroup_index = self.paramDict.get("SelfGroupIndex")
        self.selfgroup_name = self.paramDict.get("SelfGroupName")   
        self.selfStkList = self.paramDict.get("SelfStkList")

        self.size_hint = (1, 1)
        self.orientation = "vertical"

        self.add_widget(STableBoxLayout(size_hint=(1, None), height=1)) 

        nameLayout = SBoxLayout(size_hint=(1, None), height=30)
        nameLayout.orientation = "horizontal"
        
        nameLayout.add_widget(STableBoxLayout(size_hint=(.02, 1))) 
        
        nameLabel = SLabel(text="名稱:", size_hint=(.15, 1))
        nameLabel.color = colorHex("#000000")
        nameLayout.add_widget(nameLabel)
        
        self.selfgroup_name_id = STextInput(text=self.selfgroup_name, size_hint=(.65, 1))
        nameLayout.add_widget(self.selfgroup_name_id)
        
        nameLayout.add_widget(STableBoxLayout(size_hint=(.23, 1))) 

        self.add_widget(nameLayout)
        
        self.add_widget(STableBoxLayout(size_hint=(1, None), height=1))        
        
        headLayout = STableGridLayout(cols=3, rows=1, spacing=2, size_hint=(1, None), height=30)
        headLabel = SHeadLabel(text="功能", size_hint=(.15, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="代碼", size_hint=(.2, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="名稱", size_hint=(.65, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        self.add_widget(headLayout)
        
        self.add_widget(STableBoxLayout(size_hint=(1, None), height=2))
        
        self.maxIndex = 0
        self.def_ids = {}
        
        slview = STableScrollView()
        slview.size_hint = (1, None)
        slview.size = (360, 320)
        self.contentLayout = STableGridLayout(cols=3, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.contentLayout.bind(minimum_height=self.contentLayout.setter('height'))

        tmpList = None
        stkName = None
        for stkId in self.selfStkList:
            tmpList = []
            tmpList.append(stkId)
            stkName = self.app.stkNameDict.get(stkId)
            if stkName == None:
                tmpList.append("")
            else:
                tmpList.append(stkName)
            self.addListRow(tmpList, False)
            self.maxIndex += 1            

        self.addInsertRow(str(self.maxIndex))
        slview.add_widget(self.contentLayout)
        
        self.add_widget(slview)
        
        bottomLayout = BoxLayout(size_hint=(1, None), height=30)
        self.ensurebtn_id = SButton(text="確定", size_hint=(.49, 1))
        bottomLayout.add_widget(self.ensurebtn_id)
        bottomLayout.add_widget(BoxLayout(size_hint=(.02, 1)))
        self.cancelbtn_id = SButton(text="取消", size_hint=(.49, 1))
        bottomLayout.add_widget(self.cancelbtn_id)
        self.add_widget(bottomLayout)

    def addListRow(self, alist, aflag):
        if aflag:
            self.deleteRow(self.maxIndex)
        
        rowList = []
        funcLayout = SBoxLayout(size_hint=(.15, None), height=30)
        funcLayout.orientation = "horizontal"
        funcLayout.padding = (1, 1, 1, 1)
        funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        btn = SRowButton(infoIndex=self.maxIndex, text = "刪", size_hint = (.8, 1))
        btn.halign = "center"
        btn.valign = "middle"
        btn.bind(on_release=self.deleteRecordPopup)
        funcLayout.add_widget(btn)
        funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        rowList.append(funcLayout)
        self.contentLayout.add_widget(funcLayout)
        contentLabel = SContentLabel(text=alist[0], size_hint=(.2, None), height=30)
        contentLabel.color = colorHex("#000000")
        contentLabel.halign = "center"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        contentLabel = SContentLabel(text=alist[1], size_hint=(.65, None), height=30)
        contentLabel.color = colorHex("#000000")
        contentLabel.halign = "left"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        
        self.def_ids[self.maxIndex] = rowList

    def deleteRow(self, rowIndex):
        rowList = self.def_ids.get(rowIndex)
        for obj in rowList:
            self.contentLayout.remove_widget(obj)
        self.def_ids.pop(rowIndex)
        if rowIndex < len(self.selfStkList):
            self.selfStkList.pop(rowIndex)

    def saveData(self):
        stkListStr = ""
        for stkId in self.selfStkList:
            stkListStr += stkId + "|"
        if len(stkListStr) != 0:
            stkListStr = stkListStr[0:-1]
            
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "self_stkquote.ini")
        alist = sutil.getListFromFile(filePath)        
        with open(filePath, 'w', encoding = 'utf-8') as f:
            for tmpStr in alist:
                aList = tmpStr.split(",")
                if int(aList[0]) == self.selfgroup_index:
                    astr = str(self.selfgroup_index) + "," + self.selfgroup_name_id.text + "," + stkListStr + "\n"
                else:
                    astr = tmpStr + "\n"
                f.write(astr)

    def addInsertRow(self, strIndex):
        rowList = []
        funcLayout = SBoxLayout(size_hint=(.15, None), height=30)
        funcLayout.orientation = "horizontal"
        funcLayout.padding = (1, 1, 1, 1)
        funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        btn = SButton(text="新增", size_hint=(.8, 1))
        btn.halign = "center"
        btn.valign = "middle"
        btn.bind(on_release=self.addRecordPopup)
        funcLayout.add_widget(btn)
        funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        rowList.append(funcLayout)
        self.contentLayout.add_widget(funcLayout)
        contentLabel = SContentLabel(text="", size_hint=(.2, None), height=30)
        contentLabel.halign = "center"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        contentLabel = SContentLabel(text="", size_hint=(.65, None), height=30)
        contentLabel.halign = "left"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        
        self.def_ids[int(strIndex)] = rowList

    def addRecordPopup(self, instance):
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict.get(key)
        self.add_scsLayout = StkQuery(refDict)
        self.add_popup = SPopup(title="新增自選股票", content=self.add_scsLayout,
                size_hint=(None, None), size=(480, 360), auto_dismiss=False)
        self.add_scsLayout.ensureBtn_id.bind(on_press=self.addRecordEvent)
        self.add_scsLayout.cancelBtn_id.bind(on_press=self.add_popup.dismiss)
        self.add_popup.title_font = CONSTS.FONT_NAME
        self.add_popup.open()

    def addRecordEvent(self, instance):
        self.add_scsLayout.doSelectStk()
        
        if len(self.add_scsLayout.resultIdNameList) == 0:
            return
        
        for aList in self.add_scsLayout.resultIdNameList:
            self.addListRow(aList, True)
            self.selfStkList.append(aList[0])
            self.maxIndex += 1
            self.addInsertRow(str(self.maxIndex))

        self.add_popup.dismiss()        

    def deleteRecordPopup(self, instance):
        self.deleteConfirm = SRowConfirmLayout()
        self.del_popup = SPopup(title="刪除自選股票", content=self.deleteConfirm,
                size_hint=(None, None), size=(240, 160), auto_dismiss=False)
        self.deleteConfirm.yesbtn_id.infoIndex = instance.infoIndex
        self.deleteConfirm.yesbtn_id.bind(on_press=self.deleteRecordEvent)
        self.deleteConfirm.nobtn_id.bind(on_press=self.del_popup.dismiss)
        self.del_popup.title_font = CONSTS.FONT_NAME
        self.del_popup.open()

    def deleteRecordEvent(self, instance):
        self.deleteRow(instance.infoIndex)
        self.del_popup.dismiss()