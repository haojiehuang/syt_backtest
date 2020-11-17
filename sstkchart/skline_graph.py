# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.graphics import Line, Color, Rectangle, InstructionGroup

from selements import SLabel, SInfoLayout
from sbase_tech import SBaseTech
import schartutil
import sutil

class SKLineGraph(SBaseTech):
    
    def __init__(self, paramDict):

        super().__init__(paramDict)

        self.CORD_INFO_COLOR = paramDict.get("CORD_INFO_COLOR") #座標資訊的文字顏色
        self.DATA_INFO_COLOR = paramDict.get("DATA_INFO_COLOR") #資訊的文字顏色
        self.KLINE_COLOR = paramDict.get("KLINE_COLOR") #線條顏色
        self.SOLID_COLOR = paramDict.get("SOLID_COLOR") #K線中陽線的顏色
        self.VIRTUAL_COLOR = paramDict.get("VIRTUAL_COLOR") #K線中陰線的顏色
        self.CROSS_LINE_COLOR = paramDict.get("CROSS_LINE_COLOR") #十字線顏色

        self.info_time = SLabel(text="") #時間
        self.info_time.color = self.DATA_INFO_COLOR 
        self.info_openPrice = SLabel(text="") #開盤價
        self.info_openPrice.color = self.DATA_INFO_COLOR
        self.info_highPrice = SLabel(text="") #最高價
        self.info_highPrice.color = self.DATA_INFO_COLOR
        self.info_lowPrice = SLabel(text="") #最低價
        self.info_lowPrice.color = self.DATA_INFO_COLOR
        self.info_closePrice = SLabel(text="") #收盤價
        self.info_closePrice.color = self.DATA_INFO_COLOR

    def _calcDrawInfo(self):
        """
        計算繪圖所需之資訊
        """
        self.highestValue = self.extremeValue[0] * 1.01 #畫面顯示之最大值
        self.lowestValue = self.extremeValue[1] * .99 #畫面顯示之最小值
        diffValue = self.highestValue - self.lowestValue
        if diffValue != 0:
            self.yscale = 1.0 * self.chartSize[1] / diffValue #K線圖y軸縮放比例
        else:
            self.yscale = 1
        if self.dispNum <= len(self.dataDict):
            self.dispMax = self.dispNum
        else:
            self.dispMax = len(self.dataDict)

    def getExtremeValue(self):
        """
        取得當前頁次之最大值及最小值，回傳一list物件，格式如下所示:
        [最大值,最小值]
        """
        if len(self.keyList) == 0:
            return [0, 0]
        maxValue = sys.maxsize * -1 - 1
        minValue = sys.maxsize
        try:
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                aKey = self.keyList[aIdx]
                aDict = self.dataDict.get(aKey)
                if aDict.get("HP") > maxValue:
                    maxValue = aDict.get("HP")
                if aDict.get("LP") < minValue:
                    minValue = aDict.get("LP")
        except:
            pass
        return [maxValue, minValue]

    def charting(self):
        """
        繪圖
        """
        super().charting()
        
        self.canvas.remove_group(self.instGroup + "_lastData")
        self.canvas.remove_group(self.instGroup + "_curvData")
        
        if self.keyList == None or len(self.keyList) == 0: #無資料時，不作任何動作
            return

        dispIdx = -1
        for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
            dispIdx += 1
            aKey = self.keyList[aIdx]
            aDict = self.dataDict.get(aKey)
            self._drawLine(aDict, dispIdx, False)
            self.lastKey = aKey

    def _drawLine(self, aDict, dispIdx, isLastFlag):
        """
        
        """
        groupStr = self.instGroup
        if isLastFlag == True:
            groupStr += "_lastData"
        else:
            groupStr += "_curvData"    
        instg = InstructionGroup(group=groupStr)
        color = Color()
        color.rgba = self.KLINE_COLOR
        instg.add(color)
        #(self.tickWide + self.tickGap)代表顯示一筆資料，在x軸方向所需的總點數
        x1 = self.chartPos[0] + (dispIdx + 1) * (self.tickWide + self.tickGap) - self.backGap
        y1 = self.chartPos[1] + (aDict.get("HP") - self.lowestValue) * self.yscale
        x2 = x1
        y2 = self.chartPos[1] + (aDict.get("LP") - self.lowestValue) * self.yscale
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
        
        instg = InstructionGroup(group=groupStr)
        color = Color()

        openPrice = aDict.get("OP")
        closePrice = aDict.get("CP")
        if closePrice > openPrice:
            color.rgba = self.SOLID_COLOR
            instg.add(color)
            x1 = self.chartPos[0] + dispIdx * (self.tickWide + self.tickGap) + self.tickGap 
            y1 = self.chartPos[1] + (openPrice - self.lowestValue) * self.yscale
            instg.add(Rectangle(pos=(x1,y1), size=(self.tickWide, (closePrice - openPrice) * self.yscale)))
        elif closePrice < openPrice:
            color.rgba = self.VIRTUAL_COLOR
            instg.add(color)
            x1 = self.chartPos[0] + dispIdx * (self.tickWide + self.tickGap) + self.tickGap 
            y1 = self.chartPos[1] + (closePrice - self.lowestValue) * self.yscale
            instg.add(Rectangle(pos=(x1,y1), size=(self.tickWide, (openPrice - closePrice) * self.yscale)))            
        else:
            color.rgba = self.KLINE_COLOR
            instg.add(color)
            x1 = self.chartPos[0] + dispIdx * (self.tickWide + self.tickGap) + self.tickGap            
            y1 = self.chartPos[1] + (closePrice - self.lowestValue) * self.yscale
            x2 = self.chartPos[0] + (dispIdx + 1) * (self.tickWide + self.tickGap)
            y2 = y1
            instg.add(Line(points=(x1, y1, x2, y2), width=1))

        self.canvas.add(instg)
        
    
    def addData(self, paramList):
        """
        添加匯圖之資料，paramList為一list物件，list中為一dict物件，格式如下所示:
        {'TD':'時間','OP':'開盤價','HP':'最高價','LP':'最低價','CP':'收盤價','RP':'開盤參考價',
        'VOL':'成交量','AMT':'成交金額','UDF':'漲停跌符號','RT':'換手率'}
        """
        for aDict in paramList:
            aKey = aDict.get("TD")
            self.dataDict[aKey] = aDict
        self.keyList = sorted(list(self.dataDict.keys()))
    
    def clearData(self):
        super().clearData()
        
        self.canvas.remove_group(self.instGroup + "_lastData")
        self.canvas.remove_group(self.instGroup + "_curvData") 

    def _showInfo(self, index):
        if self.infoLayout == None:
            self.infoLayout = SInfoLayout(cols=1)
            self.infoLayout.row_force_default = True
            self.infoLayout.row_default_height = 20
            self.infoLayout.col_force_default = True
            self.infoLayout.padding = [2, 1, 2, 1]
            self.infoLayout.size_hint = (None, None)
        else:
            self.infoLayout.clear_widgets()
        if self.infoLayout.parent == None:
            self.layout.add_widget(self.infoLayout)
        
        aKey = self.keyList[self.scopeIdx[0] + index]
        aDict = self.dataDict.get(aKey)
        
        self.infoLayout.add_widget(self.info_time)
        self.info_time.text = sutil.formatDateTime(aKey)

        self.infoLayout.add_widget(self.info_openPrice)
        openPrice = aDict.get("OP")
        valueStr = None
        if self.formatType == 1:            
            valueStr = ("{:7.2f}".format(openPrice)).strip()
        elif self.formatType == 2:
            valueStr = "${:,}".format(openPrice)
        else:
            valueStr = str(openPrice)
        self.info_openPrice.text = "開:" + valueStr
        
        self.infoLayout.add_widget(self.info_highPrice)
        highPrice = aDict.get("HP")
        valueStr = None
        if self.formatType == 1:            
            valueStr = ("{:7.2f}".format(highPrice)).strip()
        elif self.formatType == 2:
            valueStr = "${:,}".format(highPrice)
        else:
            valueStr = str(highPrice)
        self.info_highPrice.text = "高:" + valueStr
        
        self.infoLayout.add_widget(self.info_lowPrice)
        lowPrice = aDict.get("LP")
        valueStr = None
        if self.formatType == 1:            
            valueStr = ("{:7.2f}".format(lowPrice)).strip()
        elif self.formatType == 2:
            valueStr = "${:,}".format(lowPrice)
        else:
            valueStr = str(lowPrice)
        self.info_lowPrice.text = "低:" + valueStr
        
        self.infoLayout.add_widget(self.info_closePrice)
        closePrice = aDict.get("CP")
        valueStr = None
        if self.formatType == 1:            
            valueStr = ("{:7.2f}".format(closePrice)).strip()
        elif self.formatType == 2:
            valueStr = "${:,}".format(closePrice)
        else:
            valueStr = str(closePrice)
        self.info_closePrice.text = "收:" + valueStr
        
        maxLength = len(self.info_time.text)
        if maxLength < schartutil.calcCharNum(self.info_openPrice.text):
            maxLength = schartutil.calcCharNum(self.info_openPrice.text)
        if maxLength < schartutil.calcCharNum(self.info_highPrice.text):
            maxLength = schartutil.calcCharNum(self.info_highPrice.text)
        if maxLength < schartutil.calcCharNum(self.info_lowPrice.text):
            maxLength = schartutil.calcCharNum(self.info_lowPrice.text)
        if maxLength < schartutil.calcCharNum(self.info_closePrice.text):
            maxLength = schartutil.calcCharNum(self.info_closePrice.text)
        
        layoutWidth = schartutil.getInfoLayoutWidth(maxLength)
        self.infoLayout.col_default_width = layoutWidth
        self.infoLayout.size = [layoutWidth, 104]
    
        x1 = self.chartPos[0] + (index + 1) * (self.tickWide + self.tickGap) - self.backGap
        halfNum = int(self.dispNum / 2)
        if index > halfNum:
            pos_x = x1 - self.infoLayout.width
        else:
            pos_x = x1 + 5
        pos_y = self.chartPos[1] + self.chartSize[1] - self.infoLayout.height
        self.infoLayout.pos = (pos_x, pos_y)
        
    def drawCrossLine(self, aIndex):
        """
        """
        dataNum = len(self.dataDict)
        if dataNum == 0:
            return
        if aIndex >= self.dispMax:
            index = self.dispMax - 1
        elif aIndex >= self.dispNum:            
            index = self.dispNum - 1
        elif aIndex < 0:
            index = 0
        else:
            index = aIndex
        self.crossLineIndex = index
        if self.infoFunc == None:
            self._showInfo(index)
        else:
            aKey = self.keyList[self.scopeIdx[0] + index]
            aDict = self.dataDict.get(aKey)
            refDict = {}
            for aKey in aDict.keys():
                refDict[aKey] = aDict.get(aKey)
            preIndex = self.scopeIdx[0] + index - 1
            if preIndex < 0:
                refDict["UD"] = 0
            else:
                aKey = self.keyList[preIndex]
                preDict = self.dataDict.get(aKey)
                refDict["UD"] = aDict.get("CP") - preDict.get("CP") 
            self.infoFunc(refDict)
        
        if self.isDrawCrossLine == False:
            return
        groupStr = self.instGroup + "cross_line"
        self.canvas.remove_group(groupStr)

        color = Color()
        color.rgba = self.CROSS_LINE_COLOR
        
        instg = InstructionGroup(group=groupStr)
        instg.add(color)
        x1 = self.chartPos[0] + (index + 1) * (self.tickWide + self.tickGap) - self.backGap
        y1 = self.chartPos[1]
        x2 = x1
        y2 = self.chartPos[1] + self.chartSize[1]
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)

        aKey = self.keyList[self.scopeIdx[0] + index]
        aDict = self.dataDict.get(aKey)

        instg = InstructionGroup(group=groupStr)
        instg.add(color)
        x1 = self.chartPos[0]
        y1 = self.chartPos[1] + (aDict.get("CP") - self.lowestValue) * self.yscale
        x2 = self.chartPos[0] + self.chartSize[0]
        y2 = y1
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
        
        
        
