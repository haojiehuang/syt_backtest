# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbacktest" + os.sep))

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex as colorHex
import threading

from selements import SInfoButton, SButton, SLabel, SHeadLabel, SPopup, SContentLabel, SBoxLayout
from selements import STableBoxLayout, SRowConfirmLayout, STableGridLayout, STableScrollView
import sutil
import sconsts as CONSTS

with open(os.path.join(os.path.dirname(__file__), 'sstrategy.kv'), encoding='utf-8') as f:
    Builder.load_string(f.read())

save_dir = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "strategy")
file_head = "strategy"

class SStrategySetting(BoxLayout):

    strategy_id = ObjectProperty(None)
    filename_id = ObjectProperty(None)
    ensureLayout_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    extra_info = None
    ensurebtn_id = None
    
    def __init__(self, paramDict, **kwargs):
        super(SStrategySetting, self).__init__(**kwargs)

        self.ensurebtn_id = SInfoButton(extra_info=self.extra_info)
        self.ensurebtn_id.text = "確定"
        self.ensurebtn_id.size_hint = (1, 1)
        self.ensurebtn_id.halign = "center"
        self.ensurebtn_id.valign = "middle"
        
        self.ensureLayout_id.clear_widgets()
        self.ensureLayout_id.add_widget(self.ensurebtn_id)
        
        mode = paramDict.get('mode')
        if mode == "1":
            self.filename_id.text = self.getFilename()
        self.filename_id.disabled = True
            
    def getFilename(self):
        filename = ""
        numTmp = 0
        while(True):
            numTmp += 1
            filename = file_head + str(numTmp) + ".txt"
            filepath = os.path.join(save_dir, filename)
            if os.path.exists(filepath):
                continue
            else:
                break
            
        return filename  
        
class SStrategy(BoxLayout):
        
    def __init__(self, paramDict, **kwargs):
        super(SStrategy, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)        

        self.size_hint = (1, 1)
        self.orientation = "vertical"

        headLayout = STableGridLayout(cols=3, rows=1, spacing=2, size_hint=(1, None), height=30)
        headLabel = SHeadLabel(text="功能", size_hint=(.15, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="策略名稱", size_hint=(.6, 1))
        headLabel.halign: 'center'
        headLabel.valign: 'middle'
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="檔案名稱", size_hint=(.25, 1))
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
        self.contentLayout = STableGridLayout(cols=3, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.contentLayout.bind(minimum_height=self.contentLayout.setter('height'))
        
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "strategy.ini")
        if not os.path.exists(filePath):
            with open(filePath, 'w'): pass        
            
        alist = sutil.getListFromFile(filePath)
        for astr in alist:
            tmpList = astr.strip().split(",")
            if len(tmpList) < 2:
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
        funcLayout = SBoxLayout(size_hint=(.25, None), height=30)
        funcLayout.orientation = "horizontal"
        funcLayout.padding = (1, 1, 1, 1)
        funcLayout.add_widget(BoxLayout(size_hint=(.06, 1)))
        btn = SInfoButton(extra_info=self.maxIndex, text="修", size_hint=(.14, 1))
        btn.halign = "center"
        btn.valign = "middle"
        btn.bind(on_release=self.updateRecordPopup)
        funcLayout.add_widget(btn)
        funcLayout.add_widget(BoxLayout(size_hint=(.02, 1)))
        btn = SInfoButton(extra_info=self.maxIndex, text="刪", size_hint=(.14, 1))
        btn.halign = "center"
        btn.valign = "middle"
        btn.bind(on_release=self.deleteRecordPopup)
        funcLayout.add_widget(btn)
        funcLayout.add_widget(BoxLayout(size_hint=(.02, 1)))        
        btn = SInfoButton(extra_info=self.maxIndex, text="編輯策略", size_hint=(.56, 1))
        btn.halign = "center"
        btn.valign = "middle"
        btn.bind(on_release=self.editContent)
        funcLayout.add_widget(btn)
        funcLayout.add_widget(BoxLayout(size_hint=(.06, 1)))
        rowList.append(funcLayout)
        self.contentLayout.add_widget(funcLayout)
        contentLabel = SContentLabel(text=alist[0], size_hint=(.5, None), height=30)
        contentLabel.color = colorHex("#000000")
        contentLabel.halign = "left"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        contentLabel = SContentLabel(text=alist[1], size_hint=(.25, None), height=30)
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
        if rowList[2].text != "":
            filePath = os.path.abspath(os.path.join(save_dir, rowList[2].text))
            if os.path.exists(filePath):
                os.remove(filePath)
        self.saveData()

    def saveData(self):
        keylist = self.def_ids.keys()
        keylist = sorted(keylist)
        listLen = len(keylist)
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "strategy.ini")
        with open(filePath, 'w', encoding = 'utf-8') as f:
            rowList = None
            for i in range(0, listLen - 1):
                rowList = self.def_ids.get(keylist[i])
                astr = rowList[1].text + "," + rowList[2].text + "\n"
                f.write(astr)

    def addInsertRow(self, strIndex):
        rowList = []
        funcLayout = SBoxLayout(size_hint=(.25, None), height=30)
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
        contentLabel = SContentLabel(text="", size_hint=(.5, None), height=30)
        contentLabel.halign = "left"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        contentLabel = SContentLabel(text="", size_hint=(.25, None), height=30)
        contentLabel.halign = "left"
        contentLabel.valign = "middle"
        rowList.append(contentLabel)
        self.contentLayout.add_widget(contentLabel)
        
        self.def_ids[int(strIndex)] = rowList

    def addRecordPopup(self, instance):
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict.get(key)
        refDict['mode'] = "1"
        self.add_scsLayout = SStrategySetting(refDict)
        self.add_popup = SPopup(title="新增策略", content=self.add_scsLayout,
                size_hint=(None, None), size=(560, 440), auto_dismiss=False)
        self.add_scsLayout.ensurebtn_id.bind(on_press=self.addRecordEvent)
        self.add_scsLayout.closebtn_id.bind(on_press=self.add_popup.dismiss)
        self.add_popup.title_font = CONSTS.FONT_NAME
        self.add_popup.open()

    def addRecordEvent(self, instance):
        strategyName = self.add_scsLayout.strategy_id.text
        if strategyName == None or strategyName == "":
            self.app.showMsgView(CONSTS.ERR_STRATEGY_IS_SPACE)
            return
        
        dflag = False
        for akey in self.def_ids.keys():
            rowList = self.def_ids.get(akey)
            if strategyName == rowList[1].text:
                dflag = True
                break
        if dflag:
            self.app.showMsgView(CONSTS.ERR_STRATEGY_DUPLICATED)
            return
        
        fileName = self.add_scsLayout.filename_id.text
        alist = []
        alist.append(strategyName)
        alist.append(fileName)
        self.addListRow(alist, True)
        self.maxIndex += 1
        self.addInsertRow(str(self.maxIndex))
        self.saveData()
        self.add_popup.dismiss()
        self.filePathTmp = os.path.abspath(os.path.join(save_dir, fileName))
        open(self.filePathTmp, 'a').close()
        threading.Thread(target=self.openFile).start()

    def openFile(self):
        os.system(self.filePathTmp)

    def updateRecordPopup(self, instance):
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict.get(key)
        refDict['mode'] = "2"
        self.update_scsLayout = SStrategySetting(refDict)
        self.update_popup = SPopup(title="修改策略", content=self.update_scsLayout,
                size_hint=(None, None), size=(560, 440), auto_dismiss=False)
        self.update_scsLayout.ensurebtn_id.extra_info = instance.extra_info
        self.update_scsLayout.ensurebtn_id.bind(on_press=self.updateRecordEvent)
        self.update_scsLayout.closebtn_id.bind(on_press=self.update_popup.dismiss)
        self.update_popup.title_font = CONSTS.FONT_NAME
        rowList = self.def_ids.get(instance.extra_info)
        self.update_scsLayout.strategy_id.text = rowList[1].text
        self.update_scsLayout.filename_id.text = rowList[2].text
        self.update_popup.open()

    def updateRecordEvent(self, instance):
        rowIndex = instance.extra_info
        strategyName = self.update_scsLayout.strategy_id.text
        if strategyName == None or strategyName == "":
            self.app.showMsgView(CONSTS.ERR_STRATEGY_IS_SPACE)
            return
        fileName = self.update_scsLayout.filename_id.text
        dflag = False
        for akey in self.def_ids.keys():
            if akey == rowIndex:
                continue
            rowList = self.def_ids.get(akey)
            if strategyName == rowList[1].text and fileName == rowList[2].text:
                dflag = True
                break
        if dflag:
            self.app.showMsgView(CONSTS.ERR_STRATEGY_DUPLICATED)
            return
        rowList = self.def_ids.get(rowIndex)
        rowList[1].text = strategyName
        self.saveData()
        self.update_popup.dismiss()
        self.filePathTmp = os.path.abspath(os.path.join(save_dir, fileName))
        threading.Thread(target=self.openFile).start()        

    def deleteRecordPopup(self, instance):
        self.deleteConfirm = SRowConfirmLayout()
        self.del_popup = SPopup(title="刪除策略", content=self.deleteConfirm,
                size_hint=(None, None), size=(240, 160), auto_dismiss=False)
        self.deleteConfirm.yesbtn_id.extra_info = instance.extra_info
        self.deleteConfirm.yesbtn_id.bind(on_press=self.deleteRecordEvent)
        self.deleteConfirm.nobtn_id.bind(on_press=self.del_popup.dismiss)
        self.del_popup.title_font = CONSTS.FONT_NAME
        self.del_popup.open()

    def deleteRecordEvent(self, instance):
        self.deleteRow(instance.extra_info)
        self.del_popup.dismiss()
    
    def editContent(self, instance):
        rowList = self.def_ids.get(int(instance.extra_info))
        filePath = os.path.join(save_dir, rowList[2].text)
        os.system(os.path.abspath(filePath))