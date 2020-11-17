# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

from kivy.app import App
import threading
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sstkchart" + os.sep))

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex as colorHex

from selements import SLabel, SHeadLabel, SHeadSortedButton, SPopup, SContentLabel, SButton, SInfoButton
from selements import STableBoxLayout, STableGridLayout, STableScrollView
from stk_group_view import StkGroupView
from stech_chart import STechChart
import sutil
import sconsts as CONSTS

def synchronized_with_attr(lock_name):

    def decorator(method):

        def synced_method(self, *args, **kws):
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

        return synced_method

    return decorator

COLUMN_NUM = 9
DEFAULT_FGCOLOR = "#000000"
DEFAULT_BGCOLOR = "#FFFFFF"

with open(os.path.join(os.path.dirname(__file__), "stkquote.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class StkIDDropDown(DropDown):
    
    def __init__(self, stkId, **kwargs):
        super(StkIDDropDown, self).__init__(**kwargs)
        self.stkId = stkId
        
class StkQuote(BoxLayout):

    head_layout = ObjectProperty(None)
    body_layout = ObjectProperty(None)
    selfStkList = ObjectProperty(None)
    subscribeList = ObjectProperty(None)
        
    def __init__(self, paramDict, **kwargs):
        super(StkQuote, self).__init__(**kwargs)
        
        self.lock = threading.RLock()

        self.size_hint = (1, 1)
        self.orientation = "vertical"

        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        self.dispIdName = self.paramDict.get("dispIdName", True)
        self.headDict = self.paramDict.get("headDict")
        self.headIdList = []
        self.headIdList.append("id")
        self.headIdList.append("name")
        
        for aKey in self.headDict.keys():
            if aKey == "id" or aKey == "name":
                continue
            else:
                self.headIdList.append(aKey)
        
        self.fieldIdList = [] #記錄資料的欄位列表(不包含id及name欄位)
        self.dispIdList = [] #記錄顯示的欄位列表
        """
        if self.dispIdName == True:
            self.dispIdList內容為 ['id','name','price','vol', ...]
        else:
            self.dispIdList內容為 ['id'(or 'name'),'price','vol', ...]
        """
        self.fieldMapping = {} #記錄資料欄位與顯示欄位的對應，''代表畫面不顯示此欄位
        """
        if self.dispIdName == True:
            {'id':'0', 'name':'1', 'price':'2', 'vol':'3', ...,}
        else:
            {'name':'0'(or 'id':'0'), 'price':'1', 'vol':'2', ...,}
        """
        self.dispFieldMapping = {} #記錄顯示欄位與資料欄位的對應
        """
        if self.dispIdName == True:
            {'0':'id', '1':'name', '2':'price', '3':'vol', ...}
        else:
            {'0':'name'(or '0':'id'), '1':'price', '2':'vol', ...}
        """
        # 1001-Begin: 以下將欄位訊息儲存至相關的變數中
        shiftIdx = 1
        self.fieldMapping["name"] = "0"
        if self.dispIdName == True:
            self.fieldMapping["id"] = "0"
            self.dispFieldMapping["0"] = "id"
            self.dispIdList.append("id")
            self.fieldMapping["name"] = "1"
            self.dispFieldMapping["1"] = "name"
            self.dispIdList.append("name")
            shiftIdx = 0
        else:
            self.dispIdList.append("name")
            self.fieldMapping["id"] = ""
            self.dispFieldMapping["0"] = "name"
        for idx in range(2, len(self.headIdList)):
            self.fieldIdList.append(self.headIdList[idx])
            if (idx - shiftIdx) >= COLUMN_NUM:
                self.fieldMapping[self.headIdList[idx]] = ""
            else:
                self.fieldMapping[self.headIdList[idx]] = str(idx - shiftIdx)
                self.dispFieldMapping[str(idx - shiftIdx)] = self.headIdList[idx]
                self.dispIdList.append(self.headIdList[idx])

        self.headButtonList = [] #記錄標題之Button List
        self.quoteBaseDict = {} #記錄股票基本資料之字典
        self.quoteDataDict = {} #記錄所有報價資料之字典
        """self.quoteDataDict資料格式如下所示:
           stkid: {'id': [stkId,fg_color,bg_color],'name': [stkName,fg_color,bg_color],'price': [priceValue,fg_color,bg_color], ...}
           example: 'T11101': {'id':['T11101','#000000','#FFFFFF'],'name':['台泥','#000000','#FFFFFF'],'price':[10.0,'#000000','#FFFFFF']}
        """
        self.dispDict = {} #記錄顯示物件的字典
        """self.dispDict資料格式如下所示:
        {stkid:{'0':Kivy Object, '1': Kivy Object, ....},stkid:{'0':Kivy Object, '1': Kivy Object, ....}}
        """

        headNum = len(self.dispFieldMapping) #取得畫面顯示的欄位數
        self.headLayout = STableGridLayout(cols=headNum, rows=1, spacing=2, size_hint=(1, 1))
        #1000-Start: 計算欄位寬度的size_hint
        if headNum < COLUMN_NUM: #如果欄位數比預設欄位數少
            self.idWidth_hint = 1.0 / headNum
            self.otherWidth_hint = self.idWidth_hint
        else:
            self.idWidth_hint = 0.1
            addWidth_hint = 0.1
            addField = 1
            if self.dispIdName == True:
                addWidth_hint += 0.1
                addField += 1
            self.otherWidth_hint = (1.0 - addWidth_hint) / (headNum - addField)
        #1000-End.
        for colIndexStr in self.dispFieldMapping.keys():
            headId = self.dispFieldMapping.get(colIndexStr)
            field = self.headDict.get(headId)
            if headId == "id" or headId == "name":
                headButton = SHeadSortedButton(headText = field, headIndex = headId, text = field, size_hint = (self.idWidth_hint, 1))
            else:
                headButton = SHeadSortedButton(headText = field, headIndex = headId, text = field, size_hint = (self.otherWidth_hint, 1))
            self.headLayout.add_widget(headButton)
            self.headButtonList.append(headButton)
        self.head_layout.add_widget(self.headLayout)

        self.contentLayout = STableGridLayout(cols=headNum, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.contentLayout.bind(minimum_height=self.contentLayout.setter('height'))
        
        self.body_layout.add_widget(self.contentLayout)

    def setStkList(self, selfStkList):
        self.selfStkList = selfStkList
    
    def setSubscribeList(self, subscribeList):
        self.subscribeList = subscribeList

    def setGroupName(self, groupName):
        self.groupName = groupName

    def _getDefaultDict(self):
        aDict = {}
        for headId in self.headIdList:
            aDict[headId] = ['', DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
        return aDict 

    @synchronized_with_attr("lock")
    def _getDefaultRowDict(self, aDict):
        dispObjDict = {}
        for colIndexStr in self.dispFieldMapping.keys():                     
            headId = self.dispFieldMapping.get(colIndexStr)
            fieldList = aDict.get(headId)
            contentObj = None
            if headId == "id":
                contentObj = SButton(size_hint = (self.idWidth_hint, None), height=30)
                contentObj.text = fieldList[0]
                contentObj.halign = "center"
                contentObj.bind(on_press=self._id_press)
            elif headId == "name":
                contentObj = SButton(size_hint = (self.idWidth_hint, None), height=30)
                contentObj.text = fieldList[0]
                contentObj.halign = "center"
                contentObj.bind(on_press=self._name_press)                
            else:
                contentObj = SContentLabel(size_hint = (self.otherWidth_hint, None), height=30)
                contentObj.text = fieldList[0]
                contentObj.color = colorHex(fieldList[1])
                if headId == "TT":
                    contentObj.halign = "center"
                else:
                    contentObj.halign = "right"
            dispObjDict[colIndexStr] = contentObj
        return dispObjDict

    def _openOptionPopup(self):
        content = BoxLayout(size_hint=(1, 1), orientation="vertical")
        
        strendBtn = SButton(text="走勢圖", size_hint=(1, None), height=30)
        strendBtn.bind(on_press=self._openStrendChart)
        content.add_widget(strendBtn)
        
        content.add_widget(BoxLayout(size_hint=(1, None), height=1))
        
        stechBtn = SButton(text="技術分析", size_hint=(1, None), height=30)
        stechBtn.bind(on_press=self._openStechChart)
        content.add_widget(stechBtn)
        
        content.add_widget(BoxLayout(size_hint=(1, None), height=1))

        closeBtn = SButton(text="關閉", size_hint=(1, None), height=30)
        content.add_widget(closeBtn)

        titleName = self.oneStkDict.get("id") + " " + self.oneStkDict.get("name")
        self.option_popup = SPopup(title=titleName, content=content, title_font=CONSTS.FONT_NAME,
                        size_hint=(None, None), size=(240, 152), auto_dismiss=False)
        closeBtn.bind(on_press=self.option_popup.dismiss)
        self.option_popup.open()

    def _id_press(self, instance):
        self.oneStkDict = {}
        currIdx = -1
        for aKey in self.quoteBaseDict.keys():
            currIdx += 1
            if instance.text == aKey[2:]:
                self.oneStkDict = self.quoteBaseDict.get(aKey)
                break
        
        self.currIndex = currIdx
        self._openOptionPopup()

    def _name_press(self, instance):
        self.oneStkDict = {}
        currIdx = -1
        for aKey in self.quoteBaseDict.keys():
            currIdx += 1
            aDict = self.quoteBaseDict.get(aKey)
            if instance.text == aDict.get("name"):
                self.oneStkDict = aDict
                break

        self.currIndex = currIdx
        self._openOptionPopup()
    
    def _openStrendChart(self, instance):
        self.option_popup.dismiss()
        
        refParam = {}
        refParam[CONSTS.S_APP] = self.app
        refParam["ChartType"] = "1"
        refParam["GroupName"] = self.groupName
        refParam["SelfStkList"] = self.selfStkList
        refParam["SubscribeList"] = self.subscribeList
        refParam["QuoteBaseDict"] = self.quoteBaseDict
        refParam["OneStkDict"] = self.oneStkDict
      
        self.stcLayout = StkGroupView(refParam)
        self.strend_popup = SPopup(title="走勢圖&技術分析", content=self.stcLayout,
            size_hint=(None, None), size=(720, 540), auto_dismiss=False)
        self.stcLayout.closebtn_id.bind(on_press=self._strend_popup_dismiss)
        self.strend_popup.title_font = CONSTS.FONT_NAME
        self.strend_popup.open()

    def _strend_popup_dismiss(self, instance):
        self.strend_popup.dismiss()
        self.stcLayout.removeListener()    

    def _openStechChart(self, instance):
        self.option_popup.dismiss()
        
        refParam = {}
        refParam[CONSTS.S_APP] = self.app
        refParam["ChartType"] = "2"
        refParam["GroupName"] = self.groupName
        refParam["SelfStkList"] = self.selfStkList
        refParam["SubscribeList"] = self.subscribeList
        refParam["QuoteBaseDict"] = self.quoteBaseDict
        refParam["OneStkDict"] = self.oneStkDict

        self.sttLayout = StkGroupView(refParam)
        self.stech_popup = SPopup(title="走勢圖&技術分析", content=self.sttLayout,
            size_hint=(None, None), size=(720, 540), auto_dismiss=False)
        self.sttLayout.closebtn_id.bind(on_press=self._stech_popup_dismiss)
        self.stech_popup.title_font = CONSTS.FONT_NAME
        self.stech_popup.open()
    
    def _stech_popup_dismiss(self, instance):
        self.stech_popup.dismiss()
        self.sttLayout.removeListener()    

    @synchronized_with_attr("lock")
    def updateBaseQuote(self, baseList):
        for aDict in baseList:
            stkId = aDict.get("id")
            if stkId == None:
                continue
            else:
                existDict = self.quoteBaseDict.get(stkId)
                if existDict == None: #若無報價基本資料，創建一新的字典
                    existDict = {}
                tmpId = None
                for headId in aDict.keys():
                    existDict[headId] = aDict.get(headId)               
                self.quoteBaseDict[stkId] = existDict
        
    @synchronized_with_attr("lock")
    def updateQuote(self, quoteList):
        """
        
        """
        if quoteList == None or len(quoteList) == 0:
            return
        #5001-Start: 若無id欄位，則不添加至報價列表；若資料已存在，則更新資料
        for aDict in quoteList:
            id_dataList = aDict.get("id")
            if id_dataList == None:
                continue
            else:
                existFlag = True
                stkId = id_dataList[0]
                existDict = self.quoteDataDict.get(stkId)
                if existDict == None: #若無報價資料，初始化一筆報價資料
                    existFlag = False
                    existDict = self._getDefaultDict() # 初始化報價資料
                dispObjDict = None
                if existFlag == True: #若已存在報價資料，則直接取得畫面上顯示之物件
                    dispObjDict = self.dispDict.get(stkId)
                else: #若無報價資料，則初始化一筆畫面上顯示之物件
                    dispObjDict = self._getDefaultRowDict(existDict)
                    self.dispDict[stkId] = dispObjDict
                    for rowNum in dispObjDict.keys():
                        self.contentLayout.add_widget(dispObjDict.get(rowNum))
                tmpId = None
                for headId in aDict.keys():
                    tmpHeadId = existDict.get(headId)
                    if tmpHeadId != None:
                        existDict[headId] = aDict.get(headId)
                        fieldIdx = self.fieldMapping.get(headId) #取得欄位對應之顯示欄位的index
                        if fieldIdx != None and fieldIdx != "":
                            kvObj = dispObjDict.get(fieldIdx)
                            valueList = aDict.get(headId)
                            if headId == "id":
                                kvObj.text = valueList[0][2:]
                            else:
                                kvObj.text = valueList[0]
                            if headId != "id" and headId != "name":
                                kvObj.color = colorHex(valueList[1])
                            time.sleep(0.0001) # 2020/10/28 調整，因應欄位顯示空白問題
                self.quoteDataDict[stkId] = existDict
        #5001-End.

    @synchronized_with_attr("lock")
    def clearQuote(self):
        if self.contentLayout != None:
            self.contentLayout.clear_widgets()
        self.quoteBaseDict.clear()
        self.quoteDataDict.clear()
        self.dispDict.clear()

    @synchronized_with_attr("lock")
    def resetFieldsSeq(self, fieldIdList):
        self.fieldIdList = fieldIdList
        headIdIndex = -1
        for aObj in self.headButtonList:
            if aObj.headIndex == "id" or aObj.headIndex == "name":
                continue
            headIdIndex += 1
            headId = self.fieldIdList[headIdIndex]
            aObj.headIndex = headId
            aObj.text = self.headDict.get(headId)

        self._shiftDispField()        

    @synchronized_with_attr("lock")
    def nextField(self):
        removeId = self.fieldIdList.pop(0)
        self.fieldIdList.append(removeId)
        headIdIndex = -1
        for aObj in self.headButtonList:
            if aObj.headIndex == "id" or aObj.headIndex == "name":
                continue
            headIdIndex += 1
            headId = self.fieldIdList[headIdIndex]
            aObj.headIndex = headId
            aObj.text = self.headDict.get(headId)

        self._shiftDispField()
    
    @synchronized_with_attr("lock")
    def previousField(self):
        removeId = self.fieldIdList.pop(-1)
        self.fieldIdList.insert(0, removeId)
        headIdIndex = -1
        for aObj in self.headButtonList:
            if aObj.headIndex == "id" or aObj.headIndex == "name":
                continue
            headIdIndex += 1
            headId = self.fieldIdList[headIdIndex]
            aObj.headIndex = headId
            aObj.text = self.headDict.get(headId)
        
        self._shiftDispField()  

    def _shiftDispField(self):
        for headId in self.fieldMapping.keys(): #將id及name以外的欄位，重新設置欄位對應
            if headId == "id" or headId == "name":
                continue
            self.fieldMapping[headId] = ""

        headIdIndex = -1
        for colIndexStr in self.dispFieldMapping.keys():
            headId = self.dispFieldMapping.get(colIndexStr)
            if headId == "id" or headId == "name":
                continue
            headIdIndex += 1
            headId = self.fieldIdList[headIdIndex]
            self.dispFieldMapping[colIndexStr] = headId
            self.fieldMapping[headId] = colIndexStr
        for stkId in self.dispDict.keys():
            dispObjDict = self.dispDict.get(stkId)
            aQuoteDict = self.quoteDataDict.get(stkId)
            for rowNum in dispObjDict.keys():
                kvObj = dispObjDict.get(rowNum)
                headId = self.dispFieldMapping.get(rowNum)
                aDataList = aQuoteDict.get(headId)
                if headId == "id":
                    kvObj.text = aDataList[0][2:]
                else:
                    kvObj.text = aDataList[0]                
                kvObj.color = colorHex(aDataList[1])
                if headId == "id" or headId == "name" or headId == "TT":
                    kvObj.halign = "center"
                else:
                    kvObj.halign = "right"
        
class TestStkQuote(App):

    stkQuote = None

    def build(self):
        headDict = {}
        headDict["id"] = "股票代碼" #SID
        headDict["name"] = "股票名稱" #SNT
        headDict["TT"] = "成交時間"
        headDict["TP"] = "成交價"
        headDict["TV"] = "成交量"
        headDict["YP"] = "昨收價"
        headDict["UD"] = "漲跌"
        headDict["USP"] = "漲停價"
        headDict["DSP"] = "跌停價"
        headDict["OP"] = "開盤價"
        headDict["HP"] = "最高價"
        headDict["LP"] = "最低價"
        headDict["BP"] = "買進"
        headDict["AP"] = "賣出"
        self.stkQuote = StkQuote({CONSTS.S_APP:self,'headDict':headDict,'dispIdName':True})
        return self.stkQuote
    

if __name__ == '__main__':
    testStkQuote = TestStkQuote()
    testStkQuote.run()

            