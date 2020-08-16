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

from selements import SInfoButton, SButton, SLabel, SHeadLabel, SPopup, SContentLabel, SBoxLayout
from selements import STableBoxLayout, SRowConfirmLayout, STableGridLayout, STableScrollView
import sutil
import sconsts as CONSTS

with open(os.path.join(os.path.dirname(__file__), "stradecost.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class SCostSetting(BoxLayout):

    rule_id = ObjectProperty(None)
    tradeunit_id = ObjectProperty(None)
    cost_id = ObjectProperty(None)
    ensureLayout_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    extra_info = None
    ensurebtn_id = None
    
    def __init__(self, paramDict, **kwargs):
        super(SCostSetting, self).__init__(**kwargs)
        
        self.ensurebtn_id = SInfoButton(extra_info=self.extra_info)
        self.ensurebtn_id.text = "確定"
        self.ensurebtn_id.size_hint = (1, 1)
        self.ensurebtn_id.halign = "center"
        self.ensurebtn_id.valign = "middle"
        
        self.ensureLayout_id.clear_widgets()
        self.ensureLayout_id.add_widget(self.ensurebtn_id)

        mode = paramDict.get('mode')
        if mode == "2":
            self.rule_id.disabled = True
        else:
            self.rule_id.disabled = False
    
    def showExplain(self):
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "trade_explain.ini")
        with open(filePath, 'r', encoding = 'utf-8-sig') as f:
            lineList = f.readlines()
        explainStr = ""
        for astr in lineList:
            explainStr += astr
        
        contentLayout = STableBoxLayout(size_hint=(1, 1), orientation="vertical")
        slview = STableScrollView(size_hint=(1, .9))
        contentLayout.add_widget(slview)
        explainLayout = STableBoxLayout(size_hint=(1, None))
        explainLayout.bind(minimum_height=explainLayout.setter('height'))
        explainLabel = SLabel(text=explainStr, size_hint=(1, None))
        explainLabel.font_name = CONSTS.FONT_NAME
        explainLabel.color = colorHex("#000000")
        explainLayout.add_widget(explainLabel)
        slview.add_widget(explainLayout)
        
        bottomLayout = STableBoxLayout(size_hint=(1, .1))
        closebtn_id = SButton(text="關閉", size_hint=(1, .8))
        bottomLayout.add_widget(closebtn_id)
        contentLayout.add_widget(bottomLayout)

        popup = SPopup(title="交易單位/契約乘數 說明", content=contentLayout, size_hint=(None, None),
                    size=(500, 400), pos_hint={'x':0.1, 'y':0.1}, pos=(100.0, 100.0), auto_dismiss=False)
        closebtn_id.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()
        
class STradeCost(BoxLayout):
        
    def __init__(self, paramDict, **kwargs):
        super(STradeCost, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)        

        self.size_hint = (1, 1)
        self.orientation = "vertical"

        headLayout = STableGridLayout(cols=4, rows=1, spacing=2, size_hint=(1, None), height=30)
        headLabel = SHeadLabel(text="功能", size_hint=(.15, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="規則", size_hint=(.4, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="交易單位/契約乘數", size_hint=(.25, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="手續費+交易稅", size_hint=(.2, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        self.add_widget(headLayout)
        
        gapLayout = STableBoxLayout(size_hint=(1, None), height=2)
        self.add_widget(gapLayout)
        
        self.maxIndex = 0
        self.def_ids = {}
        
        slview = STableScrollView()
        slview.size_hint = (1, None)
        slview.size = (540, 350)
        self.contentLayout = STableGridLayout(cols=4, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.contentLayout.bind(minimum_height=self.contentLayout.setter('height'))
        
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "tradecost.ini")
        if not os.path.exists(filePath):
            with open(filePath, 'w'): pass        
            
        alist = sutil.getListFromFile(filePath)
        for astr in alist:
            tmpList = astr.strip().split(",")
            if len(tmpList) < 3:
                continue
            self.addListRow(tmpList, False)
            self.maxIndex += 1            

        self.addInsertRow(str(self.maxIndex))
        slview.add_widget(self.contentLayout)
        
        self.add_widget(slview)
        
        closeLayout = BoxLayout(size_hint=(1, None), height=36)
        self.closebtn_id = SButton(text="關閉", size_hint=(1, 1))
        closeLayout.add_widget(self.closebtn_id)
        self.add_widget(closeLayout)

    def addListRow(self, alist, aflag):
        if aflag:
            self.deleteRow(self.maxIndex)
        
        rowList = []
        funcLayout = SBoxLayout(size_hint=(.15, None), height=30)
        funcLayout.orientation = "horizontal"
        funcLayout.padding = (1, 1, 1, 1)
        funcLayout.add_widget(BoxLayout(size_hint=(.09, 1)))
        btn = SInfoButton(extra_info=self.maxIndex, text = "修", size_hint = (.4, 1))
        btn.halign = "center"
        btn.valign = "middle"
        btn.bind(on_release=self.updateRecordPopup)
        funcLayout.add_widget(btn)
        funcLayout.add_widget(BoxLayout(size_hint=(.02, 1)))
        btn = SInfoButton(extra_info=self.maxIndex, text = "刪", size_hint = (.4, 1))
        btn.halign = "center"
        btn.valign = "middle"
        btn.bind(on_release=self.deleteRecordPopup)
        if alist[0] == "證券普通股" or alist[0] == "台指期貨":
            btn.disabled = True
        funcLayout.add_widget(btn)
        funcLayout.add_widget(BoxLayout(size_hint=(.09, 1)))
        rowList.append(funcLayout)
        self.contentLayout.add_widget(funcLayout)
        contentLabel = SContentLabel(text=alist[0], size_hint=(.4, None), height=30)
        contentLabel.color = colorHex("#000000")
        contentLabel.halign = "left"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        contentLabel = SContentLabel(text=alist[1], size_hint=(.25, None), height=30)
        contentLabel.color = colorHex("#000000")
        contentLabel.halign = "right"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        contentLabel = SContentLabel(text=alist[2], size_hint=(.2, None), height=30)
        contentLabel.color = colorHex("#000000")
        contentLabel.halign = "right"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        
        self.def_ids[self.maxIndex] = rowList

    def deleteRow(self, rowIndex):
        rowList = self.def_ids.get(rowIndex)
        for obj in rowList:
            self.contentLayout.remove_widget(obj)
        self.def_ids.pop(rowIndex)
        self.saveData()

    def saveData(self):
        keylist = self.def_ids.keys()
        keylist = sorted(keylist)
        listLen = len(keylist)
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "tradecost.ini")
        with open(filePath, 'w', encoding = 'utf-8') as f:
            rowList = None
            for i in range(0, listLen - 1):
                rowList = self.def_ids.get(keylist[i])
                astr = rowList[1].text + "," + rowList[2].text + "," + rowList[3].text + "\n"
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
        contentLabel = SContentLabel(text="", size_hint=(.4, None), height=30)
        contentLabel.halign = "left"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        contentLabel = SContentLabel(text="", size_hint=(.25, None), height=30)
        contentLabel.halign = "right"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        contentLabel = SContentLabel(text="", size_hint=(.2, None), height=30)
        contentLabel.halign = "right"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        
        self.def_ids[int(strIndex)] = rowList

    def addRecordPopup(self, instance):
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict.get(key)
        refDict['mode'] = "1"
        self.add_scsLayout = SCostSetting(refDict)
        self.add_popup = SPopup(title="新增規則", content=self.add_scsLayout,
                size_hint=(None, None), size=(480, 360), auto_dismiss=False)
        self.add_scsLayout.ensurebtn_id.bind(on_press=self.addRecordEvent)
        self.add_scsLayout.closebtn_id.bind(on_press=self.add_popup.dismiss)
        self.add_popup.title_font = CONSTS.FONT_NAME
        self.add_popup.open()

    def addRecordEvent(self, instance):
        ruleName = self.add_scsLayout.rule_id.text
        if ruleName == None or ruleName == "":
            self.app.showErrorView(True, CONSTS.ERR_RULE_IS_SPACE)
            return
        costStr = self.add_scsLayout.cost_id.text
        if costStr == None or costStr == "":
            self.app.showErrorView(True, CONSTS.ERR_COST_IS_SPACE)
            return
        dflag = False
        try:
            float(costStr)
        except:
            dflag = True
        if dflag:
            self.app.showErrorView(True, CONSTS.ERR_COST_MUST_NUMBER)
            return
        dflag = False
        for akey in self.def_ids.keys():
            rowList = self.def_ids.get(akey)
            if ruleName == rowList[1].text:
                dflag = True
                break
        if dflag:
            self.app.showErrorView(True, CONSTS.ERR_RULE_DUPLICATED)
            return
        
        tradeUnit = self.add_scsLayout.tradeunit_id.text
        alist = []
        alist.append(ruleName)
        alist.append(tradeUnit)
        alist.append(costStr)
        self.addListRow(alist, True)
        self.maxIndex += 1
        self.addInsertRow(str(self.maxIndex))
        self.saveData()
        self.add_popup.dismiss()
        
    def updateRecordPopup(self, instance):
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict.get(key)
        refDict['mode'] = "2"
        self.update_scsLayout = SCostSetting(refDict)
        self.update_popup = SPopup(title="修改規則", content=self.update_scsLayout,
                size_hint=(None, None), size=(480, 360), auto_dismiss=False)
        self.update_scsLayout.ensurebtn_id.extra_info = instance.extra_info
        self.update_scsLayout.ensurebtn_id.bind(on_press=self.updateRecordEvent)
        self.update_scsLayout.closebtn_id.bind(on_press=self.update_popup.dismiss)
        self.update_popup.title_font = CONSTS.FONT_NAME
        rowList = self.def_ids.get(instance.extra_info)
        self.update_scsLayout.rule_id.text = rowList[1].text
        self.update_scsLayout.tradeunit_id.text = rowList[2].text
        self.update_scsLayout.cost_id.text = rowList[3].text
        if self.update_scsLayout.rule_id.text == "證券普通股" or self.update_scsLayout.rule_id.text == "台指期貨":
            self.update_scsLayout.tradeunit_id.disabled = True
        self.update_popup.open()

    def updateRecordEvent(self, instance):
        costStr = self.update_scsLayout.cost_id.text
        if costStr == None or costStr == "":
            self.app.showErrorView(True, CONSTS.ERR_COST_IS_SPACE)
            return
        dflag = False
        try:
            float(costStr)
        except:
            dflag = True
        if dflag:
            self.app.showErrorView(True, CONSTS.ERR_COST_MUST_NUMBER)
            return
        tradeUnit = self.update_scsLayout.tradeunit_id.text
        rowList = self.def_ids.get(instance.extra_info)
        rowList[2].text = tradeUnit
        rowList[3].text = costStr
        self.saveData()
        self.update_popup.dismiss()        

    def deleteRecordPopup(self, instance):
        self.deleteConfirm = SRowConfirmLayout()
        self.del_popup = SPopup(title="刪除規則", content=self.deleteConfirm,
                size_hint=(None, None), size=(240, 160), auto_dismiss=False)
        self.deleteConfirm.yesbtn_id.extra_info = instance.extra_info
        self.deleteConfirm.yesbtn_id.bind(on_press=self.deleteRecordEvent)
        self.deleteConfirm.nobtn_id.bind(on_press=self.del_popup.dismiss)
        self.del_popup.title_font = CONSTS.FONT_NAME
        self.del_popup.open()

    def deleteRecordEvent(self, instance):
        self.deleteRow(instance.extra_info)
        self.del_popup.dismiss()