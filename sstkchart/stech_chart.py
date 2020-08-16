# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)
import abxtoolkit

abxtoolkit.load_ini(abxtoolkit.ABX_MODE.AP)
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

import time
import threading

from kivy.utils import get_color_from_hex as colorHex
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty

from selements import SInfoButton, SLabel, SSysBoxLayout
import sconsts as CONSTS
import schartutil
from skline_chart import SKLineChart
from smixed_chart import SMixedChart
import sutil

DEFAULT_COLOR = colorHex("#FFFFFF")
DEFAULT_WIDTH = 80
DEFAULT_WIDTH2 = 110

stkBase_col_obj = abxtoolkit.stkBaseInfo_columns_sets()
stkRef_col_obj =  abxtoolkit.stkInfo_columns_sets()
trade_col_obj =   abxtoolkit.trade_columns_sets()
order1_col_obj =  abxtoolkit.order_1_columns_sets()
others_col_obj = abxtoolkit.others_columns_sets()

with open(os.path.join(os.path.dirname(__file__), "stech_chart.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class STechChart(FloatLayout):
    
    head_layout = ObjectProperty(None)
    body_layout = ObjectProperty(None)
    mixedChartInfo_layout = ObjectProperty(None)
    idNameDate_id = ObjectProperty(None)
    klineDataType_id = ObjectProperty(None)
    techType_id = ObjectProperty(None)
    previous_id = ObjectProperty(None)
    next_id = ObjectProperty(None)
    bigger_id = ObjectProperty(None)
    smaller_id = ObjectProperty(None)
    dateTime_id = ObjectProperty(None)
    openPrice_id = ObjectProperty(None)
    highPrice_id = ObjectProperty(None)
    lowPrice_id = ObjectProperty(None)
    closePrice_id = ObjectProperty(None)
    upDown_id = ObjectProperty(None)
    klineDataType_index = ObjectProperty(None)
    techType_index = ObjectProperty(None)
    klineChart = ObjectProperty(None)
    priceMixedChart = ObjectProperty(None)
    secMixedChart = ObjectProperty(None)
    formulaMapping = ObjectProperty(None)
    priceFormulaId = 8001000
    priceInfoObjDict = ObjectProperty(None)
    mixedChartInfoObjDict = ObjectProperty(None)
    currentPage = 1
    tickGap = None
    tickWide = 3
    dispNum = None
    recordCount = None
    
    def __init__(self, paramDict, **kwargs):
        super(STechChart, self).__init__(**kwargs)
        
        self.mixedChartInfo_layout = SSysBoxLayout(size_hint=(1, .05), pos_hint={'x':0,'y':.29})
        self.add_widget(self.mixedChartInfo_layout)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        self.stkId = self.paramDict.get("StkId") #股票id
        self.stkName = self.paramDict.get("StkName") #股票名稱
        self.lastTradeDate = self.paramDict.get("LTD") #最後交易日
        self.decimal = self.paramDict.get("Decimal") #小數點位數
        
        self.idNameDate_id.text = self.stkId[2:] + " " + self.stkName + " " + sutil.formatDate(self.lastTradeDate)
        self.idNameDate_id.halign = "left"
        
        techChartDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "stech_chart.ini"))
        techChartParam = {}
        techChartParam["FRAME_COLOR"] = colorHex(techChartDict.get("FRAME_COLOR")) #邊框的線條顏色
        techChartParam["GRID_COLOR"] = colorHex(techChartDict.get("GRID_COLOR")) #直線條及橫線條的線條顏色
        techChartParam["CORD_INFO_COLOR"] = colorHex(techChartDict.get("CORD_INFO_COLOR")) #座標資訊的文字顏色
        techChartParam["DATA_INFO_COLOR"] = colorHex(techChartDict.get("DATA_INFO_COLOR")) #資訊的文字顏色
        techChartParam["CROSS_LINE_COLOR"] = colorHex(techChartDict.get("CROSS_LINE_COLOR")) #十字線顏色
        
        self.tickGap = int(techChartDict.get("TICK_GAP")) #每筆資料間之間隔點數
        self.shift_right = int(techChartDict.get("SHIFT_RIGHT")) #繪圖右邊位移距離
        self.shift_bottom = int(techChartDict.get("SHIFT_BOTTOM")) #繪圖下方位移距離
        self.shift_gap = int(techChartDict.get("SHIFT_GAP")) #兩圖形之間距
        self.recordCount = int(techChartDict.get("RECORD_COUNT")) #下載筆數
        
        self.next_id.disabled = True
        self.smaller_id.disabled = True
        
        self._klineDataTypeDropDown()
        self._technicalDropDown()

        refParam = {}
        for aKey in paramDict.keys():
            refParam[aKey] = paramDict.get(aKey)
        for aKey in techChartParam.keys():
            refParam[aKey] = techChartParam.get(aKey)

        refParam["Layout"] = self.body_layout #繪圖之layout
        refParam["Canvas"] = self.body_layout.canvas #繪圖之canvas
        refParam["TickWide"] = self.tickWide #一個tick的寬度(共有幾個點)
        refParam["TickGap"] = self.tickGap #tick與tick之間點數
        self._calcDispNum()
        refParam["DispNum"] = self.dispNum #畫面顯示筆數
        refParam["CurrentPage"] = self.currentPage #當前的頁次
        refParam["InfoFunc"] = self._showInfo #顯示訊息之函式
        refParam["IsDrawRect"] = True #是否畫外框
        refParam["IsDrawXCordLine"] = True #是否顯示X軸直線
        refParam["IsDrawXCordInfo"] = False #是否顯示X軸座標訊息
        refParam["IsDrawYCordLine"] = True #是否顯示Y軸直線
        refParam["IsDrawYCordInfo"] = True #是否顯示Y軸座標訊息
        refParam["IsDrawCrossLine"] = True #是否顯示十字線
        refParam["InstGroup"] = "KLine_chart" #InstructionGroup所使用之group值
        refParam["FormatType"] = 1 #0.No format,1.float format,2.currency format
        refParam["DataType"] = self.klineDataType_index #資料類型

        self.klineChart = SKLineChart(refParam)
        
        priceRefParam = {}
        for aKey in refParam.keys():
            priceRefParam[aKey] = refParam.get(aKey)
        priceRefParam["InfoFunc"] = self._showPriceInfo #顯示訊息之函式
        priceRefParam["IsDrawRect"] = False #是否畫外框
        priceRefParam["IsDrawXCordLine"] = False #是否顯示X軸直線
        priceRefParam["IsDrawXCordInfo"] = False #是否顯示X軸座標
        priceRefParam["IsDrawYCordLine"] = False #是否顯示Y軸直線
        priceRefParam["IsDrawYCordInfo"] = False #是否顯示Y軸座標
        priceRefParam["IsDrawCrossLine"] = False #是否顯示十字線
        priceRefParam["InstGroup"] = "PriceMaChart"
        lineSetup = self.formulaMapping.get(str(self.priceFormulaId))[0]
        priceRefParam["LineSetup"] = lineSetup
        self._createPriceInfoObj(self._getLineSetupList(lineSetup))
        self.priceMixedChart = SMixedChart(priceRefParam)
        
        secRefParam = {}
        for aKey in refParam.keys():
            secRefParam[aKey] = refParam.get(aKey)
        secRefParam["InfoFunc"] = self._showMixedChartInfo #顯示訊息之函式
        secRefParam["IsDrawRect"] = True #是否畫外框
        secRefParam["IsDrawXCordLine"] = True #是否顯示X軸直線
        secRefParam["IsDrawXCordInfo"] = True #是否顯示X軸座標訊息
        secRefParam["IsDrawYCordLine"] = True #是否顯示Y軸直線
        secRefParam["IsDrawYCordInfo"] = True #是否顯示Y軸座標訊息
        secRefParam["IsDrawCrossLine"] = True #是否顯示十字線
        secRefParam["InstGroup"] = "SecMixedChart" #InstructionGroup所使用之group值
        lineSetup = self.formulaMapping.get(str(self.techType_index))[0]
        secRefParam["LineSetup"] = lineSetup
        self._createMixedChartInfoObj(self._getLineSetupList(lineSetup))
        self.secMixedChart = SMixedChart(secRefParam)

        Clock.schedule_once(self.doQuoteStart, .5) #此段用意為讓畫面先顯示出來，再做後續的動作
        
        self.bind(pos=self._charting)
        self.bind(size=self._charting)
        Window.bind(mouse_pos=self._mousePos)

    def _createPriceInfoObj(self, lineSetupList):
        if lineSetupList == None or len(lineSetupList) == 0:
            return
        self.head_layout.clear_widgets()
        aLabel = SLabel(text=" ", size_hint=(None,1), width=10)
        aLabel.color = colorHex("#00142D")
        self.head_layout.add_widget(aLabel)
        self.priceInfoObjDict = {}
        for aDict in lineSetupList:
            aName = aDict.get("name")
            lwidth = schartutil.getInfoLayoutWidth(schartutil.calcCharNum(aName))
            aLabel = SLabel(text=aName + " ", size_hint=(None, 1), width=lwidth)
            aLabel.color = aDict.get("color")
            self.head_layout.add_widget(aLabel)
            aLabel = SLabel(text="", size_hint=(None, 1), width=DEFAULT_WIDTH)
            aLabel.color = DEFAULT_COLOR
            aLabel.halign = "left"
            self.head_layout.add_widget(aLabel)
            self.priceInfoObjDict[aName] = aLabel

    def _getLineSetupList(self, lineSetup):
        lineSetupList = lineSetup.split(";")
        tarLineSetupList = []
        aDict = None
        for aStr in lineSetupList:
            if aStr == "":
                continue
            aList = aStr.split("|")
            if len(aList) < 3:
                continue
            aDict = {}
            if len(aList) > 3:
                aDict["name"] = aList[0]
                aDict["color"] = colorHex("#FFFFFF")
            else:
                aDict["name"] = aList[0]
                aDict["color"] = colorHex("#" + aList[2])
            tarLineSetupList.append(aDict)

        return tarLineSetupList

    def _klineDataTypeDropDown(self):
        """
        資料類型:
        1.日線(ABGW_PRICEDATA_DAY)
        2.周線(ABGW_PRICEDATA_WEEK)
        3.月線(ABGW_PRICEDATA_MONTH)
        4.季線(ABGW_PRICEDATA_QUARTER)
        5.半年線(ABGW_PRICEDATA_HYEAR)
        6.年線(ABGW_PRICEDATA_YEAR)
        10.1分線(ABGW_PRICEDATA_MIN)
        11.5分線(ABGW_PRICEDATA_MIN5)
        12.10分線(ABGW_PRICEDATA_MIN10)
        13.15分線(ABGW_PRICEDATA_MIN15)
        14.20分線(ABGW_PRICEDATA_MIN20)
        15.30分線(ABGW_PRICEDATA_MIN30)
        16.60分線(ABGW_PRICEDATA_MIN60)
        100.往前復權基準值(ABGW_PRICEDATA_FRBASE)
        200.往後復權基準值(ABGW_PRICEDATA_BRBASE)
        復權需加上復權基準值,如 往前復權日線: 101,往後復權日線: 201
        """
        self.kdtDropDown = DropDown()
        self.dataTypeDict = {}        
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "kline_datatype.ini")
        alist = sutil.getListFromFile(filePath)
        firstRecord = True
        for astr in alist:
            aIdx = astr.find("=")
            if aIdx == -1:
                continue
            aKey = astr[:aIdx]
            aValue = astr[aIdx+1:]
            if firstRecord:
                firstRecord = False
                self.klineDataType_id.text = aValue
                self.klineDataType_index = int(aKey)
            abtn = SInfoButton(extra_info=int(aKey), text=aValue)
            abtn.size_hint_y = None
            abtn.height = 30
            abtn.bind(on_release=self.kdtDropDown.select)
            self.kdtDropDown.add_widget(abtn)
            self.dataTypeDict[str(abtn.extra_info)] = abtn
        
        self.klineDataType_id.bind(on_release=self.kdtDropDown.open)
        self.kdtDropDown.bind(on_select=self._kdtDropDownSelect)
    
    def _kdtDropDownSelect(self, instance, atext):
        self.klineDataType_id.text = atext.text
        self.klineDataType_index = atext.extra_info
        
        self.currentPage = 1
        self.previous_id.disabled = False
        self.next_id.disabled = True
        refParam = {}
        refParam["CurrentPage"] = self.currentPage
        refParam["DataType"] = self.klineDataType_index
        refParam["ExtremeValue"] = None
        
        self.klineChart.clearData()
        self.klineChart.changeDrawInfo(refParam)
        self.priceMixedChart.clearData()
        self.priceMixedChart.changeDrawInfo(refParam)
        
        aList = self.formulaMapping.get(str(self.techType_index))
        self.secMixedChart.clearData()
        self.secMixedChart.setLineSetup(aList[0])
        self._createMixedChartInfoObj(self._getLineSetupList(aList[0]))        
        self.secMixedChart.changeDrawInfo(refParam)        
        
        self.doQuery_history() #重新下載資料

    def _technicalDropDown(self):
        self.techDropDown = DropDown()
        self.techTypeDict = {}        
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "formula_id.ini")
        alist = sutil.getListFromFile(filePath)
        firstRecord = True
        aKey = None
        aValue = None
        for astr in alist:
            aIdx = astr.find("=")
            if aIdx == -1:
                continue
            aKey = astr[:aIdx]
            aValue = astr[aIdx+1:]
            if firstRecord:
                firstRecord = False
                self.techType_id.text = aValue
                self.techType_index = int(aKey)
            abtn = SInfoButton(extra_info=int(aKey), text=aValue)
            abtn.size_hint_y = None
            abtn.height = 30
            abtn.bind(on_release=self.techDropDown.select)
            self.techDropDown.add_widget(abtn)
            self.techTypeDict[str(abtn.extra_info)] = abtn
        
        self.techType_id.bind(on_release=self.techDropDown.open)
        self.techDropDown.bind(on_select=self._techDropDownSelect)
        
        self.formulaMapping = {}
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "formula_mapping.ini")
        alist = sutil.getListFromFile(filePath)
        for astr in alist:
            aIdx = astr.find("=")
            if aIdx == -1:
                continue
            aKey = astr[:aIdx]
            aValue = astr[aIdx+1:]
            self.formulaMapping[aKey] = aValue.split(",")

    def _techDropDownSelect(self, instance, atext):
        self.techType_id.text = atext.text
        self.techType_index = atext.extra_info        
        aList = self.formulaMapping.get(str(self.techType_index))
        self.secMixedChart.clearData()
        self.secMixedChart.setLineSetup(aList[0])
        self._createMixedChartInfoObj(self._getLineSetupList(aList[0]))
        refParam = {}
        refParam["CurrentPage"] = self.currentPage
        refParam["DispNum"] = self.dispNum
        refParam["DataType"] = self.klineDataType_index
        refParam["TickWide"] = self.tickWide
        refParam["ExtremeValue"] = None
        self.secMixedChart.changeDrawInfo(refParam)
        self.doQuery_TechData(self.techType_index, aList[1]) #重新下載資料

    def _createMixedChartInfoObj(self, lineSetupList):
        if lineSetupList == None or len(lineSetupList) == 0:
            return
        self.mixedChartInfo_layout.clear_widgets()
        aLabel = SLabel(text=" ", size_hint=(None,1), width=10)
        aLabel.color = colorHex("#00142D")
        self.mixedChartInfo_layout.add_widget(aLabel)
        self.mixedChartInfoObjDict = {}
        isAmt = False
        for aDict in lineSetupList:
            aName = aDict.get("name")
            if aName == "成交金額":
                isAmt = True
            lwidth = schartutil.getInfoLayoutWidth(schartutil.calcCharNum(aName))
            aLabel = SLabel(text=aName + " ", size_hint=(None, 1), width=lwidth)
            aLabel.color = aDict.get("color")
            self.mixedChartInfo_layout.add_widget(aLabel)            
            if isAmt == True:
                lwidth = DEFAULT_WIDTH2
            else:
                lwidth = DEFAULT_WIDTH
            aLabel = SLabel(text="", size_hint=(None, 1), width=lwidth)
            aLabel.color = DEFAULT_COLOR
            aLabel.halign = "left"
            self.mixedChartInfo_layout.add_widget(aLabel)
            self.mixedChartInfoObjDict[aName] = aLabel    

    def _onChangePage(self, aStr):
        if aStr == "PrePage":
            self.next_id.disabled = False
            self.currentPage += 1
            refParamDict = {}
            refParamDict["CurrentPage"] = self.currentPage
            refParamDict["ExtremeValue"] = None
            self._recharting(refParamDict)            
            scopeIdx = self.klineChart.getScopeIdx()
            if scopeIdx[0] == 0:
                self.previous_id.disabled = True
        else:
            self.previous_id.disabled = False
            self.currentPage -= 1
            refParamDict = {}
            refParamDict["CurrentPage"] = self.currentPage
            refParamDict["ExtremeValue"] = None
            self._recharting(refParamDict)            
            scopeIdx = self.klineChart.getScopeIdx()
            dataLength = self.klineChart.getDataNum()
            if scopeIdx[1] == (dataLength - 1):
                self.next_id.disabled = True
    
    def _onChangeSize(self, aStr):
        if aStr == "Bigger":
            self.smaller_id.disabled = False
            self.tickWide += 2
            if self.tickWide == 13:
                self.bigger_id.disabled = True    
        else:
            self.bigger_id.disabled = False
            self.tickWide -= 2
            if self.tickWide == 3:
                self.smaller_id.disabled = True
        refParamDict = {}
        refParamDict["TickWide"] = self.tickWide
        self._calcDispNum()
        refParamDict["DispNum"] = self.dispNum
        self.currentPage = 1
        refParamDict["CurrentPage"] = self.currentPage
        refParamDict["ExtremeValue"] = None
        self._recharting(refParamDict)

        self.next_id.disabled = True
        scopeIdx = self.klineChart.getScopeIdx()
        if scopeIdx[0] == 0:
            self.previous_id.disabled = True
        else:
            self.previous_id.disabled = False
            
    def _mousePos(self, *args):
        if len(args) >= 2:
            index = int((args[1][0] - self.pos[0]) / (self.tickWide + self.tickGap))
            self.klineChart.drawCrossLine(index)
            self.priceMixedChart.drawCrossLine(index)
            self.secMixedChart.drawCrossLine(index)

    def _calcDispNum(self):
        self.dispNum = int((self.size[0] - self.shift_right) / (self.tickWide + self.tickGap))
        
    def _calcDrawInfo(self):
        kline_width = self.size[0] - self.shift_right
        draw_Height = self.size[1] * .78 - self.shift_bottom - self.shift_gap
        kline_height = draw_Height * .75
        secChart_height = draw_Height - kline_height
        kline_pos_x = self.pos[0]
        kline_pos_y = self.pos[1] + self.size[1] * .06 + self.shift_bottom + secChart_height + self.shift_gap
        secChart_pos_x = self.pos[0]
        secChart_pos_y = self.pos[1] + self.size[1] * .06 + self.shift_bottom
        refParam = {}
        refParam["kline_pos"] = [kline_pos_x, kline_pos_y]
        refParam["kline_size"] = [kline_width, kline_height]
        refParam["secChart_pos"] = [secChart_pos_x, secChart_pos_y]
        refParam["secChart_size"] = [kline_width, secChart_height]

        return refParam

    def _recharting(self, paramDict):
        refParam = {}
        for aKey in paramDict.keys():
            refParam[aKey] = paramDict.get(aKey)
        refParam["ExtremeValue"] = None
        self.klineChart.changeDrawInfo(refParam)
        self.klineChart.charting()
        self.priceMixedChart.changeDrawInfo(refParam)
        
        extremeValue = []
        kline_extremeValue = self.klineChart.getExtremeValue()
        price_extremeValue = self.priceMixedChart.getExtremeValue()
        if kline_extremeValue[0] < price_extremeValue[0]:
            extremeValue.append(price_extremeValue[0])
        else:
            extremeValue.append(kline_extremeValue[0])
        if kline_extremeValue[1] > price_extremeValue[1]:
            extremeValue.append(price_extremeValue[1])
        else:
            extremeValue.append(kline_extremeValue[1])

        refParam = {}
        refParam["ExtremeValue"] = extremeValue
        self.priceMixedChart.changeDrawInfo(refParam)
        self.priceMixedChart.charting()
        if kline_extremeValue[0] != extremeValue[0] or kline_extremeValue[1] != extremeValue[1]:
            self.klineChart.changeDrawInfo(refParam)
            self.klineChart.charting()
        
        self.secMixedChart.changeDrawInfo(paramDict)
        self.secMixedChart.charting()
        
    def _charting(self, *args):
        self._calcDispNum()
        calcParam = self._calcDrawInfo()
        refParam = {}
        refParam["ChartPos"] = calcParam.get("kline_pos")
        refParam["ChartSize"] = calcParam.get("kline_size")
        refParam["DispNum"] = self.dispNum
        refParam["CurrentPage"] = self.currentPage
        self.klineChart.changeDrawInfo(refParam)
        self.klineChart.charting()
        self.priceMixedChart.changeDrawInfo(refParam)
        self.priceMixedChart.charting()
        secParam = {}
        secParam["ChartPos"] = calcParam.get("secChart_pos")
        secParam["ChartSize"] = calcParam.get("secChart_size")
        secParam["DispNum"] = self.dispNum
        secParam["CurrentPage"] = self.currentPage
        self.secMixedChart.changeDrawInfo(secParam)
        self.secMixedChart.charting()

    def _getPriceColor(self, prePrice, aPrice):
        if aPrice > prePrice:
            return self.UP_COLOR
        elif aPrice < prePrice:
            return self.DOWN_COLOR
        else:
            return self.EQUAL_COLOR

    def _showInfo(self, dataDict):
        tmpValue = dataDict.get("TD")
        if tmpValue != None:
            self.dateTime_id.text = sutil.formatDateTime(tmpValue)
        tmpValue = dataDict.get("OP")
        if tmpValue != None:
            self.openPrice_id.text = ("{:7.2f}".format(tmpValue)).strip()
        tmpValue = dataDict.get("HP")
        if tmpValue != None:
            self.highPrice_id.text = ("{:7.2f}".format(tmpValue)).strip()
        tmpValue = dataDict.get("LP")
        if tmpValue != None:
            self.lowPrice_id.text = ("{:7.2f}".format(tmpValue)).strip()
        tmpValue = dataDict.get("CP")
        if tmpValue != None:
            self.closePrice_id.text = ("{:7.2f}".format(tmpValue)).strip()
        tmpValue = dataDict.get("UD")
        if tmpValue != None:
            self.upDown_id.text = ("{:7.2f}".format(tmpValue)).strip()
    
    def _showPriceInfo(self, dataDict):
        techType = dataDict.get("TechType")
        if techType == None:
            return
        aValue = dataDict.get("Value")
        if aValue != None:
            aLabel = self.priceInfoObjDict.get(techType)
            aLabel.text = ("{:7.2f}".format(aValue)).strip()
    
    def _showMixedChartInfo(self, dataDict):
        techType = dataDict.get("TechType")
        if techType == None:
            return
        aValue = dataDict.get("Value")
        if aValue != None:
            aLabel = self.mixedChartInfoObjDict.get(techType)
            aLabel.text = ("{:7.2f}".format(aValue)).strip()
        aValue = dataDict.get("VOL")
        if aValue != None:
            aLabel = self.mixedChartInfoObjDict.get(techType)
            aLabel.text = ("{:7.2f}".format(aValue)).strip() 
        
    def doQuoteStart(self, instance):
        threading.Thread(target=self.doQuery_history).start()

    def my_callback_func(self, a_result):
        if a_result.errcode != 0:
            self.app.showErrorView(False, a_result.errcode, a_result.errdes)
            return
        if a_result.stkid == None or a_result.stkid != self.stkId:
            return
        if a_result.mesgtype == abxtoolkit.REBUILD_TYPE.history_data:
            priceData = a_result.data.get("PriceData")
            if priceData != None:
                paramList = []
                aDict = None
                for aStr in priceData:
                    aList = aStr.split("|")
                    aDict = {}
                    aDict["TD"] = aList[0]
                    aDict["OP"] = int(aList[1]) * 1.0 / pow(10, self.decimal)
                    aDict["HP"] = int(aList[2]) * 1.0 / pow(10, self.decimal)
                    aDict["LP"] = int(aList[3]) * 1.0 / pow(10, self.decimal)
                    aDict["CP"] = int(aList[4]) * 1.0 / pow(10, self.decimal)
                    paramList.append(aDict)

                self.klineChart.addData(paramList)
                calcParam = self._calcDrawInfo()
                refParam = {}
                refParam["ChartPos"] = calcParam.get("kline_pos")
                refParam["ChartSize"] = calcParam.get("kline_size")
                self._calcDispNum()
                refParam["DispNum"] = self.dispNum
                self.klineChart.changeDrawInfo(refParam)
                self.klineChart.charting()
                scopeIdx = self.klineChart.getScopeIdx()
                if scopeIdx[0] == 0:
                    self.previous_id.disabled = True
                self.doQuery_TechData(self.priceFormulaId, self.formulaMapping.get(str(self.priceFormulaId))[1])
                
        if a_result.mesgtype == abxtoolkit.REBUILD_TYPE.query_Technicaldata:
            if a_result.data.get("FormulaID") == self.priceFormulaId:
                aList = self.formulaMapping.get(str(self.priceFormulaId))
                self.priceMixedChart.setLineSetup(aList[0])                
                self.priceMixedChart.addData(a_result.data.get("LineData"))
               
                calcParam = self._calcDrawInfo()
                refParam = {}
                refParam["ChartPos"] = calcParam.get("kline_pos")
                refParam["ChartSize"] = calcParam.get("kline_size")
                self._calcDispNum()
                refParam["DispNum"] = self.dispNum   
                refParam["CurrentPage"] = self.currentPage
                self.priceMixedChart.changeDrawInfo(refParam)
                
                extremeValue = []
                kline_extremeValue = self.klineChart.getExtremeValue()
                price_extremeValue = self.priceMixedChart.getExtremeValue()
                if kline_extremeValue[0] < price_extremeValue[0]:
                    extremeValue.append(price_extremeValue[0])
                else:
                    extremeValue.append(kline_extremeValue[0])
                if kline_extremeValue[1] > price_extremeValue[1]:
                    extremeValue.append(price_extremeValue[1])
                else:
                    extremeValue.append(kline_extremeValue[1])
                
                refParam["ExtremeValue"] = extremeValue
                self.priceMixedChart.changeDrawInfo({"ExtremeValue":extremeValue})
                self.priceMixedChart.charting()
                if kline_extremeValue[0] != extremeValue[0] or kline_extremeValue[1] != extremeValue[1]:
                    self.klineChart.changeDrawInfo(refParam)
                    self.klineChart.charting()
                aList = self.formulaMapping.get(str(self.techType_index))
                self.secMixedChart.clearData()
                self.secMixedChart.setLineSetup(aList[0])
                self._createMixedChartInfoObj(self._getLineSetupList(aList[0]))
                refParam = {}
                refParam["TickWide"] = self.tickWide
                refParam["CurrentPage"] = self.currentPage
                refParam["DispNum"] = self.dispNum
                refParam["DataType"] = self.klineDataType_index
                refParam["ExtremeValue"] = None                
                self.secMixedChart.changeDrawInfo(refParam)
                self.doQuery_TechData(self.techType_index, aList[1])
                
            if a_result.data.get("FormulaID") == self.techType_index:
                self.secMixedChart.setKLineDict(self.klineChart.getDataDict())
                self.secMixedChart.addData(a_result.data.get("LineData"))
                calcParam = self._calcDrawInfo()
                refParam = {}
                refParam["ChartPos"] = calcParam.get("secChart_pos")
                refParam["ChartSize"] = calcParam.get("secChart_size")
                self._calcDispNum()
                refParam["DispNum"] = self.dispNum
                self.secMixedChart.changeDrawInfo(refParam)
                self.secMixedChart.charting()      

    def removeListener(self):

        abxtoolkit.remove_listener([self.my_callback_func])

    def doQuery_history(self):
        
        abxtoolkit.add_listener([self.my_callback_func])
        qdict = {}
        qdict['StockFullID'] = self.stkId
        qdict['DataType'] = self.klineDataType_index
        qdict['RecoverDate'] = 0
        qdict['StartDate'] = 0
        qdict['EndDate'] = 0
        qdict['RecordCount'] = self.recordCount                
        a_result = abxtoolkit.query_history(qdict)
        if a_result.get("ErrCode") != 0:
            self.app.showErrorView(False, a_result.get("ErrCode"), a_result.get(ErrDesc))
            return           
        
    def doQuery_TechData(self, formulaId, param):
        
        abxtoolkit.add_listener([self.my_callback_func])
        qdict = {}
        qdict['StockFullID'] = self.stkId
        qdict['DataType'] = self.klineDataType_index
        qdict['FormulaID'] = formulaId
        qdict['Parameter'] = param
        qdict['DataDate'] = 0
        qdict['RecoverDate'] = 0
        qdict['StartDate'] = 0
        qdict['EndDate'] = 0
        qdict['RecordCount'] = self.recordCount         
 
        a_result = abxtoolkit.query_technicalindex_data(qdict)
        if a_result.get("ErrCode") != 0:
            self.app.showErrorView(False, a_result.get("ErrCode"), a_result.get(ErrDesc))
            return       
