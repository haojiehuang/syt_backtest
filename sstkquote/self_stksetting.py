# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex as colorHex

from selements import SInfoButton, SButton, SLabel, SHeadLabel, SPopup, SContentLabel
from selements import SBoxLayout, SSysBoxLayout, SCheckBox
from selements import STextInput, STableBoxLayout, SRowConfirmLayout, STableGridLayout, STableScrollView
import sutil
import sconsts as CONSTS

NUM_PER_PAGE = 100
INSERT_ROW_ID = "新增"

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
        
        self.num_per_page = NUM_PER_PAGE
        self.page_num = 1
        self.max_page_num = 1        
        
        self.resultIdNameList = []
        self.selectDict = {}
        self.selectIdNameList = []
        self.contentView = None
        self.pageLayout = None
        self.enterPageLayout = None
        self.nextPreLayout = None
        
    def _queryStk(self):
        
        queryStr = self.queryStr_id.text
        self.resultIdNameList.clear()
        self.selectDict.clear()
        stkName = None
        for stkId in self.app.stkNameDict.keys():
            stkName = self.app.stkNameDict.get(stkId)
            if stkId[2:].find(queryStr) != -1 or stkName.find(queryStr) != -1:
                self.resultIdNameList.append([stkId, stkName])
        self.body_layout.remove_widget(self.content_layout)
        if self.contentView != None:
            self.contentView.clear_widgets()
        if self.pageLayout != None:
            self.pageLayout.clear_widgets()
        if self.enterPageLayout != None:
            self.enterPageLayout.clear_widgets()
        if self.nextPreLayout != None:
            self.nextPreLayout.clear_widgets()
        if len(self.resultIdNameList) == 0:
            return
        
        self.contentView = STableBoxLayout(size_hint=(1, 1), orientation="vertical")
        
        if len(self.resultIdNameList) > NUM_PER_PAGE:
            self.pageLayout = SSysBoxLayout(orientation="horizontal", size_hint=(1, None), height=30, padding=2)
            self.pageLayout.add_widget(BoxLayout(size_hint=(.50, 1)))
            self.enterPageLayout = BoxLayout(orientation="horizontal", size_hint=(.20, 1))
            self.enterPageLayout.add_widget(SLabel(text="第", color=colorHex("#FFFFFF"), size_hint=(.16, 1), halign="right"))
            self.page_id = STextInput(text="1", multiline=False, size_hint=(.32, 1))
            self.page_id.bind(on_text_validate=self._on_page_id_enter)
            self.enterPageLayout.add_widget(self.page_id)
            self.enterPageLayout.add_widget(SLabel(text="/", color=colorHex("#FFFFFF"), size_hint=(.16, 1), halign="center"))
            self.totalpage_id = SLabel(text="1", color=colorHex("#FFFFFF"), size_hint=(.32, 1), halign="left")
            self.enterPageLayout.add_widget(self.totalpage_id)
            self.enterPageLayout.add_widget(BoxLayout(size_hint=(.04, 1)))
            self.pageLayout.add_widget(self.enterPageLayout)
            self.nextPreLayout = BoxLayout(orientation="horizontal", size_hint=(.3, 1))
            self.prepage_id = SButton(text="上一頁", size_hint=(.28, 1), halign="center", valign="middle")
            self.prepage_id.bind(on_release=self._onChangePage)
            self.nextPreLayout.add_widget(self.prepage_id)
            self.nextPreLayout.add_widget(BoxLayout(size_hint=(.01, 1)))
            self.nextpage_id = SButton(text="下一頁", size_hint=(.28, 1), halign="center", valign="middle")
            self.nextpage_id.bind(on_release=self._onChangePage)
            self.nextPreLayout.add_widget(self.nextpage_id)
            self.pageLayout.add_widget(self.nextPreLayout)
            self.contentView.add_widget(self.pageLayout)

            self._calcPageInfo()
        
        headLayout = STableGridLayout(cols=3, rows=1, spacing=2, size_hint=(1, None), height=30)
        headLabel = SHeadLabel(text="勾選", size_hint=(.15, 1))
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
        self.contentView.add_widget(headLayout)
        
        slview = STableScrollView()
        if len(self.resultIdNameList) > NUM_PER_PAGE:
            slview.size_hint = (1, .95)
        else:
            slview.size_hint = (1, .95)
        self.gridLayout = STableGridLayout(cols=3, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.gridLayout.bind(minimum_height=self.gridLayout.setter('height'))
        
        slview.add_widget(self.gridLayout)
        
        self.contentView.add_widget(slview)

        self._addContentData()
        self.content_layout = self.contentView
        self.body_layout.add_widget(self.content_layout)
    
    def _calcPageInfo(self):
        stkListNum = len(self.resultIdNameList)

        self.max_page_num = int(stkListNum / self.num_per_page)
        tmpNum = stkListNum % self.num_per_page
        if tmpNum != 0:
            self.max_page_num += 1
        if self.page_num > self.max_page_num:
            self.page_num = self.max_page_num
    
        self.page_id.text = str(self.page_num) 
        self.totalpage_id.text = str(self.max_page_num)
    
    def _on_page_id_enter(self, instance):
        topage_num = int(instance.text)
        pageNum = 0
        if topage_num < 1:
            pageNum = 1
        elif topage_num > self.max_page_num:
            pageNum = self.max_page_num
        else:
            pageNum = topage_num
        self.page_id.text = str(pageNum)
        if pageNum == self.page_num:
            return

        self.page_num = pageNum

        self._addContentData()

    def _onChangePage(self, instance):
        if instance.text == "下一頁":
            if self.page_num == self.max_page_num:
                self.page_num = 1
            else:
                self.page_num += 1
        elif instance.text == "上一頁":
            if self.page_num == 1:
                self.page_num = self.max_page_num
            else:
                self.page_num -= 1
        else:
            topage_num = int(changePage)
            if topage_num < 1:
                self.page_num = 1
            elif topage_num > self.max_page_num:
                self.page_num = self.max_page_num
            self.topage_txt = str(self.page_num)

        self.page_id.text = str(self.page_num)

        self._addContentData()

    def _addContentData(self):
        
        self.gridLayout.clear_widgets()
        
        startIdx = (self.page_num - 1) * NUM_PER_PAGE
        endIdx = self.page_num * NUM_PER_PAGE
        if endIdx > len(self.resultIdNameList):
            endIdx = len(self.resultIdNameList)        
        
        idNameList = None
        refParam = None
        for aIdx in range(startIdx, endIdx):
            idNameList = self.resultIdNameList[aIdx]
            funcLayout = SBoxLayout(size_hint=(.15, None), height=30)
            funcLayout.orientation = "horizontal"
            funcLayout.padding = (1, 1, 1, 1)
            funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
            refParam = {}
            refParam["idNameList"] = idNameList
            acbObj = SCheckBox(refParam)
            acbObj.size_hint = (1, 1)
            if idNameList[0] in self.selectDict:
                acbObj.active = True
            else:
                acbObj.active = False
            acbObj.bind(active=self._on_checkbox_active)
            funcLayout.add_widget(acbObj)
            funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
            self.gridLayout.add_widget(funcLayout)
            contentLabel = SContentLabel(text=idNameList[0][2:], size_hint=(.2, None), height=30)
            contentLabel.color = colorHex("#000000")
            contentLabel.halign = "center"
            contentLabel.valign = "middle"
            self.gridLayout.add_widget(contentLabel)
            contentLabel = SContentLabel(text=idNameList[1], size_hint=(.65, None), height=30)
            contentLabel.color = colorHex("#000000")
            contentLabel.halign = "left"
            contentLabel.valign = "middle"
            self.gridLayout.add_widget(contentLabel)        
    
    def _on_checkbox_active(self, acheckbox, value):
        
        if value:
            self.selectDict[acheckbox.idNameList[0]] = acheckbox.idNameList
        else:
            self.selectDict.pop(acheckbox.idNameList[0])
        
    def doSelectStk(self):
        if len(self.selectDict) == 0:
            return
        self.selectIdNameList.clear()     
        aList = None
        for stkId in self.selectDict.keys():
            aList = self.selectDict.get(stkId)
            self.selectIdNameList.append(aList)

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
            self.addListRow(tmpList)       

        self.addInsertRow()
        slview.add_widget(self.contentLayout)
        
        self.add_widget(slview)
        
        bottomLayout = BoxLayout(size_hint=(1, None), height=30)
        self.ensurebtn_id = SButton(text="確定", size_hint=(.49, 1))
        bottomLayout.add_widget(self.ensurebtn_id)
        bottomLayout.add_widget(BoxLayout(size_hint=(.02, 1)))
        self.cancelbtn_id = SButton(text="取消", size_hint=(.49, 1))
        bottomLayout.add_widget(self.cancelbtn_id)
        self.add_widget(bottomLayout)

    def addListRow(self, alist):
        
        rowList = []
        funcLayout = SBoxLayout(size_hint=(.15, None), height=30)
        funcLayout.orientation = "horizontal"
        funcLayout.padding = (1, 1, 1, 1)
        funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        btn = SInfoButton(extra_info=alist[0], text = "刪", size_hint = (.8, 1))
        btn.halign = "center"
        btn.valign = "middle"
        btn.bind(on_release=self.deleteRecordPopup)
        funcLayout.add_widget(btn)
        funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        rowList.append(funcLayout)
        self.contentLayout.add_widget(funcLayout)
        contentLabel = SContentLabel(text=alist[0][2:], size_hint=(.2, None), height=30)
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
        
        self.def_ids[alist[0]] = rowList

    def deleteRow(self, rowId):
        rowList = self.def_ids.get(rowId)
        for obj in rowList:
            self.contentLayout.remove_widget(obj)
        self.def_ids.pop(rowId)
        if rowId in self.selfStkList:
            self.selfStkList.remove(rowId)

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

    def addInsertRow(self):
        rowList = []
        funcLayout = SBoxLayout(size_hint=(.15, None), height=30)
        funcLayout.orientation = "horizontal"
        funcLayout.padding = (1, 1, 1, 1)
        funcLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        btn = SInfoButton(extra_info=INSERT_ROW_ID, text="新增", size_hint=(.8, 1))
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
        
        self.def_ids[INSERT_ROW_ID] = rowList

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
        
        if len(self.add_scsLayout.selectIdNameList) == 0:
            return
        
        duplicatedIds = []
        for aList in self.add_scsLayout.selectIdNameList:
            if aList[0] in self.selfStkList:
                duplicatedIds.append(aList[0][2:])
        if len(duplicatedIds) != 0:
            self.app.showErrorMsg(CONSTS.ERR_STKID_DUPLICATED, ", ".join(duplicatedIds))
            return
        
        self.deleteRow(INSERT_ROW_ID)

        for aList in self.add_scsLayout.selectIdNameList:
            self.addListRow(aList)
            self.selfStkList.append(aList[0])
        
        self.addInsertRow()
        
        self.add_popup.dismiss()        

    def deleteRecordPopup(self, instance):
        self.deleteConfirm = SRowConfirmLayout()
        self.del_popup = SPopup(title="刪除自選股票", content=self.deleteConfirm,
                size_hint=(None, None), size=(240, 160), auto_dismiss=False)
        self.deleteConfirm.yesbtn_id.extra_info = instance.extra_info
        self.deleteConfirm.yesbtn_id.bind(on_press=self.deleteRecordEvent)
        self.deleteConfirm.nobtn_id.bind(on_press=self.del_popup.dismiss)
        self.del_popup.title_font = CONSTS.FONT_NAME
        self.del_popup.open()

    def deleteRecordEvent(self, instance):
        self.deleteRow(instance.extra_info)
        self.del_popup.dismiss()