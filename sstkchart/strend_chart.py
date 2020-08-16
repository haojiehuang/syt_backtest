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
from kivy.properties import ObjectProperty

import sconsts as CONSTS
from sminutetime_chart import SMinuteTimeChart
import sutil

stkBase_col_obj = abxtoolkit.stkBaseInfo_columns_sets()
stkRef_col_obj =  abxtoolkit.stkInfo_columns_sets()
trade_col_obj =   abxtoolkit.trade_columns_sets()
order1_col_obj =  abxtoolkit.order_1_columns_sets()
others_col_obj = abxtoolkit.others_columns_sets()

with open(os.path.join(os.path.dirname(__file__), "strend_chart.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class STrendChart(FloatLayout):
    
    stkIdAndName = ObjectProperty(None)
    lastTradeDate_id = ObjectProperty(None)
    time_id = ObjectProperty(None)
    price_id = ObjectProperty(None)
    volume_id = ObjectProperty(None)
    amt_id = ObjectProperty(None)
    upDown_id = ObjectProperty(None)
    body_layout = ObjectProperty(None)
    content_layout = ObjectProperty(None)
    minuteTimeChart = ObjectProperty(None)
    price_xscale = 1
    
    def __init__(self, paramDict, **kwargs):
        super(STrendChart, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        self.stkId = self.paramDict.get("StkId") #股票id
        self.stkName = self.paramDict.get("StkName") #股票名稱
        self.lastTradeDate = self.paramDict.get("LTD") #最後交易日
        self.startTime = self.paramDict.get("StartTime") #起始時間
        self.endTime = self.paramDict.get("EndTime") #截止時間
        self.yesPrice = self.paramDict.get("YesPrice") #昨收價
        self.decimal = self.paramDict.get("Decimal") #小數點位數
        self.chartNum = sutil.calcTimeNum(int(self.startTime), int(self.endTime))
        
        self.stkIdAndName.text = self.stkId[2:] + " " + self.stkName
        self.stkIdAndName.halign = "left"
        self.lastTradeDate_id.text = sutil.formatDate(self.lastTradeDate)
        
        refParam = {}
        for aKey in paramDict.keys():
            refParam[aKey] = paramDict.get(aKey)
        trendGraphDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "strend_chart.ini"))
        self.shift_left = int(trendGraphDict.get("SHIFT_LEFT")) #圖形左邊位移距離
        refParam["SHIFT_LEFT"] = self.shift_left
        refParam["SHIFT_GAPHEIGHT"] = int(trendGraphDict.get("SHIFT_GAPHEIGHT")) #價圖及量圖的間距
        refParam["SHIFT_BOTTOM"] = int(trendGraphDict.get("SHIFT_BOTTOM")) #圖形底部位移距離
        refParam["SHIFT_TOP"] = int(trendGraphDict.get("SHIFT_TOP")) #圖形上方位移距離
        refParam["PRICE_HEIGHT_PER"] = int(trendGraphDict.get("PRICE_HEIGHT_PER")) #價圖高度佔比
        refParam["VOLUME_HEIGHT_PER"] = int(trendGraphDict.get("VOLUME_HEIGHT_PER")) #量圖高度佔比
        refParam["CORD_INFO_COLOR"] = colorHex(trendGraphDict.get("CORD_INFO_COLOR")) #座標資訊的文字顏色
        refParam["DATA_INFO_COLOR"] = colorHex(trendGraphDict.get("DATA_INFO_COLOR")) #資訊的文字顏色
        self.UP_COLOR = colorHex(trendGraphDict.get("UP_COLOR")) #上漲時線條顏色
        self.DOWN_COLOR = colorHex(trendGraphDict.get("DOWN_COLOR")) #下跌時線條顏色
        self.EQUAL_COLOR = colorHex(trendGraphDict.get("EQUAL_COLOR")) #持平時線條顏色
        refParam["UP_COLOR"] = self.UP_COLOR
        refParam["DOWN_COLOR"] = self.DOWN_COLOR
        refParam["EQUAL_COLOR"] = self.EQUAL_COLOR 
        refParam["VOLUME_COLOR"] = colorHex(trendGraphDict.get("VOLUME_COLOR")) #量的線條顏色
        refParam["FRAME_COLOR"] = colorHex(trendGraphDict.get("FRAME_COLOR")) #邊框的線條顏色
        refParam["GRID_COLOR"] = colorHex(trendGraphDict.get("GRID_COLOR")) #格線的線條顏色
        refParam["CROSS_LINE_COLOR"] = colorHex(trendGraphDict.get("CROSS_LINE_COLOR")) #十字線線條顏色
        refParam["UP_DOWN_PER"] = float(trendGraphDict.get("UP_DOWN_PER")) #漲跌幅度
        refParam["InfoFunc"] = self.showInfo #顯示訊息的函式
        refParam["ChartNum"] = self.chartNum #時間總筆數
        refParam["Layout"] = self.body_layout
        refParam["Canvas"] = self.body_layout.canvas

        self.strendChart = SMinuteTimeChart(refParam)
        
        Clock.schedule_once(self.doQuoteStart, .5) #此段用意為讓畫面先顯示出來，再做後續的動作
        
        self.bind(pos=self.charting)
        self.bind(size=self.charting)
        Window.bind(mouse_pos=self.mousePos)

    def mousePos(self, *args):
        if len(args) >= 2:
            index = int((args[1][0] - self.pos[0] - self.shift_left) / self.price_xscale)
            self.strendChart.drawCrossLine(index)

    def charting(self, *args):
        self.price_width = self.width - self.shift_left
        self.price_xscale = 1.0 * self.price_width / self.chartNum #價圖x縮放比例
        sc_x_start_pos = self.pos[0] #走勢圖原點之x軸座標值
        sc_y_start_pos = self.pos[1] + .06 * self.height #走勢圖原點之y軸座標值
        sc_width = self.width #走勢圖的寬度
        sc_height = .82 * self.height #走勢圖之高度
        self.body_layout.canvas.clear()
        self.strendChart.charting([[sc_x_start_pos, sc_y_start_pos], [sc_width, sc_height]])

    def _getPriceColor(self, prePrice, aPrice):
        if aPrice > prePrice:
            return self.UP_COLOR
        elif aPrice < prePrice:
            return self.DOWN_COLOR
        else:
            return self.EQUAL_COLOR

    def showInfo(self, dataDict):
        tmpValue = dataDict.get("TD")
        if tmpValue != None:
            self.time_id.text = sutil.formatTime(tmpValue)
        tmpValue = dataDict.get("CloseP")
        if tmpValue != None:
            aColor = self._getPriceColor(self.yesPrice, tmpValue)
            self.price_id.text = ("{:7.2f}".format(tmpValue)).strip()
            self.price_id.color = aColor
            self.upDown_id.text = ("{:7.2f}".format(tmpValue - self.yesPrice)).strip()
            self.upDown_id.color = aColor
        tmpValue = dataDict.get("Vol")
        if tmpValue != None:
            self.volume_id.text = str(tmpValue)
        tmpValue = dataDict.get("Amt")
        if tmpValue != None:
            self.amt_id.text = "{:,}".format(tmpValue)
        
    def doQuoteStart(self, instance):
        threading.Thread(target=self.doRebuild_mintrade).start()

    def my_callback_func(self, a_result):
        if a_result.errcode != 0:
            self.app.showErrorView(False, a_result.errcode, a_result.errdes)
            return
        if a_result.stkid == None or a_result.stkid != self.stkId:
            return
        if a_result.mesgtype == abxtoolkit.REBUILD_TYPE.rebuild_mintrade:
            self.strendChart.addData(a_result.data)

    def removeListener(self):

        abxtoolkit.remove_listener([self.my_callback_func])
        
    def doRebuild_mintrade(self):
        
        abxtoolkit.add_listener([self.my_callback_func])
        a_result = abxtoolkit.rebuild_mintrade(self.stkId)
        if a_result.get("ErrCode") != 0:
            self.app.showErrorView(False, a_result.get("ErrCode"), a_result.get(ErrDesc))
            return       
