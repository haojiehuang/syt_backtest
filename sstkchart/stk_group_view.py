# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)
import abxtoolkit

abxtoolkit.load_ini(abxtoolkit.ABX_MODE.AP)
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty

import sconsts as CONSTS
from strend_chart import STrendChart
from stech_chart import STechChart
import sutil

with open(os.path.join(os.path.dirname(__file__), "stk_group_view.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class StkGroupView(FloatLayout):
    
    body_layout = ObjectProperty(None)
    typeName_id = ObjectProperty(None)
    groupName_id = ObjectProperty(None)
    changeType_btn_id = ObjectProperty(None)
    previous_btn_id = ObjectProperty(None)
    next_btn_id = ObjectProperty(None)
    strendChart = ObjectProperty(None)
    stechChart = ObjectProperty(None)
    stkId = ObjectProperty(None)
    isAddListener = False
    isBack1 = False
    isBack2 = False
    
    def __init__(self, paramDict, **kwargs):
        super(StkGroupView, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        self.chartType = self.paramDict.get("ChartType")
        self.typeName_id.halign = "left"
        
        self.groupName = self.paramDict.get("GroupName")
        self.groupName_id.text = self.groupName
        self.groupName_id.halign = "left"
        
        self.selfStkList = self.paramDict.get("SelfStkList")
        if len(self.selfStkList) == 1:
            self.next_btn_id.disabled = True
            self.previous_btn_id.disabled = True
        self.subscribeList = self.paramDict.get("SubscribeList")
        self.quoteBaseDict = self.paramDict.get("QuoteBaseDict")
        self.oneStkDict = self.paramDict.get("OneStkDict")
        self.currIndex = -1
        for stkId in self.selfStkList:
            self.currIndex += 1
            if stkId == self.oneStkDict.get("id"):
                break
        if self.currIndex == -1:
            self.currIndex = 0
        self.stkId = stkId

        if self.chartType == "2":# 技術分析
            self.typeName_id.text = "技術分析"
            self.changeType_btn_id.text = "走勢圖"
            self._addTech()
        else:# 走勢圖
            self.typeName_id.text = "走勢圖"
            self.changeType_btn_id.text = "技術分析"
            self._addTrend()

    def _addTrend(self):
        self.body_layout.clear_widgets()
        if self.strendChart != None:
            self.strendChart.removeListener()            
        
        refParam = {}
        refParam[CONSTS.S_APP] = self.app
        refParam["StkId"] = self.oneStkDict.get("id", "")
        refParam["StkName"] = self.oneStkDict.get("name", "")
        refParam["StartTime"] = self.oneStkDict.get("OT")
        refParam["EndTime"] = self.oneStkDict.get("CloseT")
        refParam["LTD"] = self.oneStkDict.get("LTD")
        refParam["YesPrice"] = self.oneStkDict.get("YP")
        refParam["Decimal"] = self.oneStkDict.get("Dec")

        self.strendChart = STrendChart(refParam)
        self.strendChart.size_hint = (1, 1)
        self.strendChart.pos_hint = {'x':0, 'y':0}       

        self.body_layout.add_widget(self.strendChart)

    def _addTech(self):
        self.body_layout.clear_widgets()
        if self.stechChart != None:
            self.stechChart.removeListener()        
        
        refParam = {}
        refParam[CONSTS.S_APP] = self.app
        refParam["StkId"] = self.oneStkDict.get("id", "")
        refParam["StkName"] = self.oneStkDict.get("name", "")
        refParam["LTD"] = self.oneStkDict.get("LTD")
        refParam["Decimal"] = self.oneStkDict.get("Dec")        

        self.stechChart = STechChart(refParam)
        self.stechChart.size_hint = (1, 1)
        self.stechChart.pos_hint = {'x':0, 'y':0}       

        self.body_layout.add_widget(self.stechChart)
        
    def _onChangeStock(self, aStr):
        stkLength = len(self.selfStkList)
        if aStr == "PreStock":
            if self.currIndex == 0:
                self.currIndex = stkLength - 1
            else:
                self.currIndex -= 1
        else:
            if self.currIndex == (stkLength - 1):
                self.currIndex = 0
            else:
                self.currIndex += 1
        inFlag = False
        self.stkId = self.selfStkList[self.currIndex]
        for tmpId in self.subscribeList:
            if tmpId == self.stkId:
                inFlag = True
        if inFlag == True:
            self.oneStkDict = self.quoteBaseDict.get(self.stkId)
            if self.chartType == "2":
                self._addTech()
            else:
                self._addTrend()
        else:
            if self.isAddListener == False:
                r = abxtoolkit.add_listener([self.group_view_callback_func])
                self.isAddListener = True
            quote_condition = []
            for tmpId in self.subscribeList:
                a_sub_stock = abxtoolkit.abx_quote_condition()
                a_sub_stock.stockID = tmpId
                a_sub_stock.quoteID = ['stkBase', 'stkInfo', 'order_1', 'trade', 'others']
                quote_condition.append(a_sub_stock)
    
            a_sub_stock = abxtoolkit.abx_quote_condition()
            a_sub_stock.stockID = self.stkId
            a_sub_stock.quoteID = ['stkBase', 'stkInfo', 'order_1', 'trade', 'others']
            quote_condition.append(a_sub_stock)
    
            self.isBack1 = False
            self.isBack2 = False            
            r = abxtoolkit.subscribe_quote(quote_condition)
    
    def _changeType(self):
        if self.chartType == "2":
            self.chartType = "1"
            self.typeName_id.text = "走勢圖"
            self.changeType_btn_id.text = "技術分析"
            self._addTrend()
        else:
            self.chartType = "2"
            self.typeName_id.text = "技術分析"
            self.changeType_btn_id.text = "走勢圖"
            self._addTech()

    def group_view_callback_func(self, a_result):
        if a_result.errcode != 0:
            self.app.showErrorView(False, a_result.errcode, a_result.errdes)
            return
        if a_result.stkid == None:
            return
        if a_result.stkid != self.stkId:
            return
        if self.isBack1 == False and self.isBack2 == False:
            if self.oneStkDict == None:
                self.oneStkDict = {}
            else:
                self.oneStkDict.clear()        
        if a_result.mesgtype == abxtoolkit.WATCH_TYPE.stkBase:
            self.oneStkDict["id"] = a_result.stkid            
            if "SNT" in a_result.data:
                self.oneStkDict["name"] = a_result.data["SNT"]
            if "OT" in a_result.data:
                self.oneStkDict["OT"] = a_result.data["OT"]
            if "CloseT" in a_result.data:
                self.oneStkDict["CloseT"] = a_result.data["CloseT"]
            if "Dec" in a_result.data:
                self.oneStkDict["Dec"] = a_result.data["Dec"]
            self.isBack1 = True     
        if a_result.mesgtype == abxtoolkit.WATCH_TYPE.stkInfo:     
            if "YP" in a_result.data:
                self.oneStkDict["YP"] = a_result.data["YP"]
            if "LTD" in a_result.data:
                self.oneStkDict["LTD"] = a_result.data["LTD"]
            self.isBack2 = True
        
        if self.isBack1 == True and self.isBack2 == True:
            self.isAddListener = False
            abxtoolkit.remove_listener([self.group_view_callback_func])
            if self.chartType == "2":# 技術分析
                self._addTech()
            else:# 走勢圖
                self._addTrend()       

    def removeListener(self):
        if self.strendChart != None:
            self.strendChart.removeListener()
        if self.stechChart != None:
            self.stechChart.removeListener()
        