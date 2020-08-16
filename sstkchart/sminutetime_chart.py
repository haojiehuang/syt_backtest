# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.graphics import Line, Color, InstructionGroup

from selements import SLabel, SInfoLayout
from schartutil import SMinTimeCordUtil
import sutil

class SMinuteTimeChart():
    
    removeXCordList = None
    removePriceYCordList = None
    removeVolumeYCordList = None
    maxVolume = None
    crossLineIndex = None
    infoLayout = None
    
    def __init__(self, paramDict):

        self.paramDict = paramDict

        self.layout = self.paramDict.get("Layout") #繪圖之layout
        self.canvas = self.paramDict.get("Canvas") #繪圖之canvas
        self.shift_left = self.paramDict.get("SHIFT_LEFT") #圖形左邊位移距離
        self.shift_gapheight = self.paramDict.get("SHIFT_GAPHEIGHT") #價圖及量圖的間距
        self.shift_bottom = self.paramDict.get("SHIFT_BOTTOM") #圖形底部位移距離
        self.shift_top = self.paramDict.get("SHIFT_TOP") #圖形上方位移距離
        self.price_height_per = self.paramDict.get("PRICE_HEIGHT_PER") #價圖高度佔比
        self.volume_height_per = self.paramDict.get("VOLUME_HEIGHT_PER") #量圖高度佔比
        self.CORD_INFO_COLOR = self.paramDict.get("CORD_INFO_COLOR") #座標資訊的文字顏色
        self.DATA_INFO_COLOR = self.paramDict.get("DATA_INFO_COLOR") #資訊的文字顏色
        self.UP_COLOR = self.paramDict.get("UP_COLOR") #上漲時線條顏色
        self.DOWN_COLOR = self.paramDict.get("DOWN_COLOR") #下跌時線條顏色
        self.EQUAL_COLOR = self.paramDict.get("EQUAL_COLOR") #持平時線條顏色
        self.VOLUME_COLOR = self.paramDict.get("VOLUME_COLOR") #量的線條顏色
        self.FRAME_COLOR = self.paramDict.get("FRAME_COLOR") #邊框的線條顏色
        self.GRID_COLOR = self.paramDict.get("GRID_COLOR") #格線的線條顏色
        self.CROSS_LINE_COLOR = self.paramDict.get("CROSS_LINE_COLOR") #十字線線條顏色
        self.UP_DOWN_PER = self.paramDict.get("UP_DOWN_PER") #漲跌幅度
        
        self.chartNum = self.paramDict.get("ChartNum") #時間總筆數
        self.yesPrice = self.paramDict.get("YesPrice") #昨收價
        self.startTime = self.paramDict.get("StartTime") #起始時間
        self.endTime = self.paramDict.get("EndTime") #截止時間
        self.infoFunc = self.paramDict.get("InfoFunc") #顯示訊息之函式
        self.instGroup = self.paramDict.get("InstGroup", "") #InstructionGroup所使用之group值
        
        self.minTimeList = [] #分時資料List
        self.volumeList = [] #成交量的List
        self.lastMinTime = None #最後一筆之時間
        
        self.info_time = SLabel(text="")#時間
        self.info_time.color = self.DATA_INFO_COLOR 
        self.info_price = SLabel(text="")#成交價
        self.info_vol = SLabel(text="")#成交量
        self.info_vol.color = self.DATA_INFO_COLOR

    def _calcChartInfo(self):
        self.price_width = self.chart_size[0] - self.shift_left
        drawHeight = self.chart_size[1] - self.shift_bottom - self.shift_gapheight - self.shift_top
        self.price_height = drawHeight * self.price_height_per / (self.price_height_per + self.volume_height_per)
        self.volume_height = drawHeight * self.volume_height_per / (self.price_height_per + self.volume_height_per)
        self.xscale = 1.0 * self.price_width / self.chartNum #走勢圖x軸縮放比例
        maxPrice = self.yesPrice * (1 + self.UP_DOWN_PER) #最高價
        self.lowestPrice = self.yesPrice * (1 - self.UP_DOWN_PER) #最低價
        self.price_yscale = 1.0 * self.price_height / (maxPrice - self.lowestPrice) #價圖y軸縮放比例
        self._calcVolumeYScale()
        self.start_xaxis = self.chart_start_pos[0] + self.shift_left #價圖及量圖之原點的x座標值
        self.price_yaxis = self.chart_start_pos[1] + self.shift_bottom + self.volume_height + self.shift_gapheight #價圖之原點的y座標值
        self.volume_yaxis = self.chart_start_pos[1] + self.shift_bottom #量圖之原點的y座標值
        self.crossLine_height = self.chart_size[1] - self.shift_bottom - self.shift_top #十字線的高度
        
    def _calcVolumeYScale(self):
        if self.maxVolume == None:
            self.volume_yscale = 1.0 * self.volume_height / 100
        else:
            self.volume_yscale = 1.0 * self.volume_height / self.maxVolume        

    def _drawNoDataGraph(self):
        """
        繪製一個沒有數據之圖形
        """
        self._calcChartInfo()
        self._drawFrameGrid() #繪製一矩形
        self._drawPriceCord() #繪製價圖y軸資訊及線條
        self._drawVolumeCord() #繪製量圖y軸資訊及線條

    def _drawFrameGrid(self):
        # Start-01: 產生一繪製外框,線條及座標之物件
        rectParamDict = {}
        rectParamDict["layout"] = self.layout
        rectParamDict["canvas"] = self.canvas
        rectParamDict["width"] = self.price_width
        rectParamDict["height"] = self.crossLine_height
        rectParamDict["x_start_pos"] = self.start_xaxis
        rectParamDict["y_start_pos"] = self.volume_yaxis
        rectParamDict["xscale"] = self.xscale
        rectParamDict["yscale"] = self.price_yscale
        rectParamDict["rectColor"] = self.FRAME_COLOR
        rectParamDict["rectWidth"] = 1
        rectParamDict["gridColor"] = self.GRID_COLOR
        rectParamDict["gridWidth"] = 1
        rectParamDict["cordColor"] = self.CORD_INFO_COLOR
        rectParamDict["instGroup"] = self.instGroup + "_SMTC_Rect"
        rectParamDict["shift_left"] = self.shift_left
        rectParamDict["drawFlagList"] = [False, False]
        rectParamDict["formatFlag"] = True
      
        smintimeCordUtil = SMinTimeCordUtil(rectParamDict)
        # End-01.

        smintimeCordUtil.drawRectGrid() #繪製一矩形框
        
        xCordDict = {}
        
        infoList = []
        aNum = -1
        for aTime in range(int(self.startTime), int(self.endTime) + 1):
            aRoundNum = aTime % 100
            if aRoundNum <= 59:
                aNum += 1
                if aRoundNum == 0:
                    infoList.append([aNum, int(aTime / 100)])
        
        xCordDict["infoList"] = infoList
        xCordDict["removeLabelList"] = self.removeXCordList
        self.removeXCordList = smintimeCordUtil.drawXTimeCord(xCordDict) #繪製x軸資訊

    def _drawPriceCord(self):
        """
        """        
        rectParamDict = {}
        rectParamDict["layout"] = self.layout
        rectParamDict["canvas"] = self.canvas
        rectParamDict["width"] = self.price_width
        rectParamDict["height"] = self.price_height
        rectParamDict["x_start_pos"] = self.start_xaxis
        rectParamDict["y_start_pos"] = self.volume_yaxis + self.volume_height + self.shift_gapheight
        rectParamDict["xscale"] = self.xscale
        rectParamDict["yscale"] = self.price_yscale
        rectParamDict["rectColor"] = self.FRAME_COLOR
        rectParamDict["rectWidth"] = 1
        rectParamDict["gridColor"] = self.GRID_COLOR
        rectParamDict["gridWidth"] = 1
        rectParamDict["cordColor"] = self.CORD_INFO_COLOR
        rectParamDict["instGroup"] = "SMTC_Price"
        rectParamDict["shift_left"] = self.shift_left
        rectParamDict["drawFlagList"] = [True, False]
        rectParamDict["formatFlag"] = True
        
        smintimeCordUtil = SMinTimeCordUtil(rectParamDict)
        # 繪製y軸資訊
        price_yCordDict = {}
        infoList = []
        priceStep = 1.0 * (self.yesPrice - self.lowestPrice) / 4
        for idx in range(0, 9):
            if idx == 4:
                infoList.append(self.yesPrice)
            else:
                aPrice = self.lowestPrice + priceStep * idx * 1.0
                infoList.append(aPrice)
        price_yCordDict["infoList"] = infoList
        price_yCordDict["lowestValue"] = self.lowestPrice
        price_yCordDict["removeLabelList"] = self.removePriceYCordList
        self.removePriceYCordList = smintimeCordUtil.drawYGridCord(price_yCordDict)        

    def _drawVolumeCord(self):
        """
        """        
        rectParamDict = {}
        rectParamDict["layout"] = self.layout
        rectParamDict["canvas"] = self.canvas
        rectParamDict["width"] = self.price_width
        rectParamDict["height"] = self.volume_height
        rectParamDict["x_start_pos"] = self.start_xaxis
        rectParamDict["y_start_pos"] = self.volume_yaxis
        rectParamDict["xscale"] = self.xscale
        rectParamDict["yscale"] = self.volume_yscale
        rectParamDict["rectColor"] = self.FRAME_COLOR
        rectParamDict["rectWidth"] = 1
        rectParamDict["gridColor"] = self.GRID_COLOR
        rectParamDict["gridWidth"] = 1
        rectParamDict["cordColor"] = self.CORD_INFO_COLOR
        rectParamDict["instGroup"] = "SMTC_Volume"
        rectParamDict["shift_left"] = self.shift_left
        rectParamDict["drawFlagList"] = [False, True]
        rectParamDict["formatFlag"] = False
        
        smintimeCordUtil = SMinTimeCordUtil(rectParamDict)
        # 繪製y軸資訊
        volume_yCordDict = {}
        infoList = []
        infoList.append(0)
        if self.maxVolume == None:
            infoList.append(50)
            infoList.append(100)
        else:
            infoList.append(int(self.maxVolume / 2))
            infoList.append(self.maxVolume)
        
        volume_yCordDict["infoList"] = infoList
        volume_yCordDict["lowestValue"] = 0
        volume_yCordDict["removeLabelList"] = self.removeVolumeYCordList
        self.removeVolumeYCordList = smintimeCordUtil.drawYGridCord(volume_yCordDict)

    def charting(self, systemInfoList):
        """
        繪圖
        """
        #self.canvas.clear() 改由呼叫charting的那一層控制

        self.chart_start_pos = systemInfoList[0] #走勢圖的原點座標，為一list物件，[0]為x座標，[1]為y座標
        self.chart_size = systemInfoList[1] #走勢圖的size，為一list物件，[0]為寬度，[1]為高度

        if self.minTimeList == None or len(self.minTimeList) == 0:
            self._drawNoDataGraph()
            return
    
        self._calcChartInfo()
        self._drawFrameGrid() #繪製一矩形
        self._drawPriceCord() #繪製價圖y軸資訊及線條

        isFirst = True
        for aIdx in range(0, len(self.minTimeList)):
            aDict = self.minTimeList[aIdx]
            if isFirst == True:
                isFirst = False
                preDict = {}
                preDict["TD"] = "0900"
                preDict["CloseP"] = self.yesPrice                
            if aIdx == (len(self.minTimeList) - 1): #最後一筆資料
                self._drawPriceLine(preDict, aDict, aIdx, True) 
                self._drawVolumeLine(aDict, aIdx, True)
            else: #其它筆資料
                self._drawPriceLine(preDict, aDict, aIdx, False)
                self._drawVolumeLine(aDict, aIdx, False)
            preDict = aDict
            self.lastMinTime = aDict.get("TD")
        if self.crossLineIndex != None:
            self.drawCrossLine(self.crossLineIndex)

    def _reChartVolume(self):
        self.canvas.remove_group(self.instGroup + "volume_curvData")
        for aIdx in range(0, len(self.minTimeList)):
            aDict = self.minTimeList[aIdx]             
            self._drawVolumeLine(aDict, aIdx, False)

    def _getPriceColor(self, prePrice, aPrice):
        if aPrice > prePrice:
            return self.UP_COLOR
        elif aPrice < prePrice:
            return self.DOWN_COLOR
        else:
            return self.EQUAL_COLOR
    
    def _drawPriceLine(self, preDict, aDict, aIdx, isLastFlag):
        groupStr = self.instGroup
        if isLastFlag == True:
            groupStr += "price_lastData"
        else:
            groupStr += "price_curvData"    
        instg = InstructionGroup(group=groupStr)
        color = Color()
        color.rgba = self._getPriceColor(preDict.get("CloseP"), aDict.get("CloseP"))
        instg.add(color)
        if aIdx == 0:
            x1 = self.start_xaxis
        else:
            x1 = self.start_xaxis + (aIdx - 1) * self.xscale
        y1 = self.price_yaxis + (preDict.get("CloseP") - self.lowestPrice) * self.price_yscale
        x2 = self.start_xaxis + aIdx * self.xscale
        y2 = self.price_yaxis + (aDict.get("CloseP") - self.lowestPrice) * self.price_yscale
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)

    def _drawVolumeLine(self, aDict, aIdx, isLastFlag):
        groupStr = self.instGroup
        if isLastFlag == True:
            groupStr += "volume_lastData"
        else:
            groupStr += "volume_curvData"    
        instg = InstructionGroup(group=groupStr)
        color = Color()
        color.rgba = self.VOLUME_COLOR
        instg.add(color)
        x1 = self.start_xaxis + aIdx * self.xscale
        y1 = self.volume_yaxis
        x2 = x1
        y2 = self.volume_yaxis + aDict.get("Vol") * self.volume_yscale
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
    
    def addData(self, paramMinTimeList):
        """
        添加匯圖之資料，list中之資料為一dict，資料內容如下所示：
        1.'TD': 時間
        2.'OpenP': 開盤價
        3.'HighP': 最高價
        4.'LowP': 最低價
        5.'CloseP': 收盤價
        6.'OpenRefP': 開盤參考價
        7.'Vol': 成交量
        8.'Amt': 成交金額
        9.'PriceFlag': 漲跌停符號
        10.'VolCRate': 成交量換手率
        11.'TtVolume': 成交總量(此欄位暫不使用)
        12.'TtAmount': 成交總金額(此欄位暫不使用)
        """
        preDict = None
        aDict = None
        if self.lastMinTime == None: #第一次添加資料時
            for aDict in paramMinTimeList:
                aVol = aDict.get("Vol")
                if self.maxVolume == None:
                    self.maxVolume = aVol
                else:
                    if self.maxVolume < aVol:
                        self.maxVolume = aVol
            self._calcVolumeYScale()
            self._drawVolumeCord()
            isFirst = True
            for aIdx in range(0, len(paramMinTimeList)):
                aDict = paramMinTimeList[aIdx]
                aVol = aDict.get("Vol")
                if isFirst == True:
                    isFirst = False
                    preDict = {}
                    preDict["TD"] = "0900"
                    preDict["CloseP"] = self.yesPrice
                    self.maxVolume = aVol
                if aIdx == (len(paramMinTimeList) - 1): #最後一筆資料
                    self._drawPriceLine(preDict, aDict, aIdx, True)
                    self._drawVolumeLine(aDict, aIdx, True)
                else: #其它筆資料
                    self._drawPriceLine(preDict, aDict, aIdx, False)
                    self._drawVolumeLine(aDict, aIdx, False)
                preDict = aDict
                self.lastMinTime = aDict.get("TD")
                self.minTimeList.append(aDict)
                if self.maxVolume < aVol:
                    self.maxVolume = aVol
        else: #非第一次添加資料
            self.canvas.remove_group(self.instGroup + "price_lastData")
            self.canvas.remove_group(self.instGroup + "volume_lastData")
            isFirst = True
            for aIdx in range(0, len(paramMinTimeList)):
                aDict = paramMinTimeList[aIdx]
                aVol = aDict.get("Vol")
                if isFirst == True:
                    isFirst = False                    
                    if self.lastMinTime == aDict.get("TD"):
                        self.minTimeList.pop(len(self.minTimeList) - 1)
                        dataLength = len(self.minTimeList)
                        if dataLength == 0:
                            preDict = {}
                            preDict["TD"] = "0900"
                            preDict["CloseP"] = self.yesPrice
                        else:
                            preDict = self.minTimeList[dataLength - 1]                    
                    else:
                        dataLength = len(self.minTimeList)
                        if dataLength == 1:
                            preDict = {}
                            preDict["TD"] = "0900"
                            preDict["CloseP"] = self.yesPrice
                            tmpDict = self.minTimeList[dataLength - 1]
                        else:
                            preDict = self.minTimeList[dataLength - 2]
                            tmpDict = self.minTimeList[dataLength - 1]
                        self._drawPriceLine(preDict, tmpDict, dataLength - 1, False) #將price_lastData轉為price_curvData
                        self._drawVolumeLine(tmpDict, dataLength - 1, False) #將volume_lastData轉為volume_curvData
                if self.maxVolume < aVol:
                    self.maxVolume = aVol
                    self._calcVolumeYScale()
                    self._drawVolumeCord()
                    self._reChartVolume()
                dataLength = len(self.minTimeList)
                if aIdx == (len(paramMinTimeList) - 1): #最後一筆資料
                    self._drawPriceLine(preDict, aDict, dataLength, True)
                    self._drawVolumeLine(aDict, dataLength, True)
                else: #其它筆資料
                    self._drawPriceLine(preDict, aDict, dataLength, False)
                    self._drawVolumeLine(aDict, dataLength, False)
                preDict = aDict
                self.lastMinTime = aDict.get("TD")
                if self.crossLineIndex != None and self.crossLineIndex == (len(self.minTimeList) - 1):
                    self.crossLineIndex += 1
                self.minTimeList.append(aDict)
        if self.crossLineIndex != None:
            if self.crossLineIndex == (len(self.minTimeList) - 1):
                self.drawCrossLine(len(self.minTimeList) - 1)
    
    def _showInfo(self, index):
        if self.infoLayout == None:
            self.infoLayout = SInfoLayout(cols=1)
            self.infoLayout.row_force_default = True
            self.infoLayout.row_default_height = 20
            self.infoLayout.col_force_default = True
            self.infoLayout.col_default_width = 90
            self.infoLayout.size = [90, 64]
            self.infoLayout.padding = [2, 1, 2, 1]
            self.infoLayout.size_hint = (None, None)
        else:
            self.infoLayout.clear_widgets()
        if self.infoLayout.parent == None:
            self.layout.add_widget(self.infoLayout)
        x1 = self.start_xaxis + index * self.xscale
        halfNum = int(self.chartNum / 2)
        if index > halfNum:
            pos_x = x1 - self.infoLayout.width
        else:
            pos_x = x1 + 5
        pos_y = self.volume_yaxis + self.crossLine_height - self.infoLayout.height
        self.infoLayout.pos = (pos_x, pos_y)
        
        dataDict = self.minTimeList[index]
        
        self.infoLayout.add_widget(self.info_time)
        self.info_time.text = "時:" + sutil.formatTime(dataDict.get("TD"))
        
        price = dataDict.get("CloseP")
        self.infoLayout.add_widget(self.info_price)
        self.info_price.text = "價:" + ("{:7.2f}".format(price)).strip()
        self.info_price.color = self._getPriceColor(self.yesPrice, price)
        
        self.infoLayout.add_widget(self.info_vol)
        self.info_vol.text = "量:" + ("{:13.0f}".format(dataDict.get("Vol"))).strip()
        
    def drawCrossLine(self, aIndex):
        """
        """
        dataNum = len(self.minTimeList)
        if dataNum == 0:
            return
        if aIndex >= dataNum:
            index = dataNum - 1
        elif aIndex < 0:
            index = 0
        else:
            index = aIndex
        self.crossLineIndex = index
        if self.infoFunc == None:
            self._showInfo(index)
        else:
            self.infoFunc(self.minTimeList[index])
        
        groupStr = self.instGroup + "cross_line"
        self.canvas.remove_group(groupStr)        

        instg = InstructionGroup(group=groupStr)
        
        color = Color()
        color.rgba = self.CROSS_LINE_COLOR
        instg.add(color)
        x1 = self.start_xaxis + index * self.xscale
        y1 = self.volume_yaxis
        x2 = self.start_xaxis + index * self.xscale
        y2 = self.volume_yaxis + self.crossLine_height
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
        
