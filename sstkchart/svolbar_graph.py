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

class SVolBarGraph(SBaseTech):

    def __init__(self, paramDict):

        super().__init__(paramDict)

        self.CORD_INFO_COLOR = paramDict.get("CORD_INFO_COLOR") #座標資訊的文字顏色
        self.DATA_INFO_COLOR = paramDict.get("DATA_INFO_COLOR") #資訊的文字顏色
        self.UP_COLOR = paramDict.get("UP_COLOR") #上漲時條狀圖的顏色
        self.DOWN_COLOR = paramDict.get("DOWN_COLOR") #下跌時條狀圖的顏色
        self.EQUAL_COLOR = paramDict.get("EQUAL_COLOR") #持平時條狀圖的顏色
        self.CROSS_LINE_COLOR = paramDict.get("CROSS_LINE_COLOR") #十字線顏色
        self.techType = paramDict.get("TechType") #技術分析類型

        self.info_time = SLabel(text="") #時間
        self.info_time.color = self.DATA_INFO_COLOR 
        self.info_vol = SLabel(text="") #成交量
        self.info_vol.color = self.DATA_INFO_COLOR

    def _calcDrawInfo(self):
        self.highestValue = self.extremeValue[0] * 1.01 #畫面顯示之最大值
        self.lowestValue = 0 #畫面顯示之最小值
        diffValue = self.highestValue - self.lowestValue
        if diffValue != 0:
            self.yscale = 1.0 * self.chartSize[1] / (self.highestValue - self.lowestValue) #線圖y軸縮放比例
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
        minValue = 0
        try:
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                aKey = self.keyList[aIdx]
                aDict = self.dataDict.get(aKey)
                if aDict.get("VOL") > maxValue:
                    maxValue = aDict.get("VOL")
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
        
        isFirst = True
        dispIdx = -1
        for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
            dispIdx += 1
            aKey = self.keyList[aIdx]
            aDict = self.dataDict.get(aKey)
            if isFirst == True:
                isFirst = False
                if aIdx == 0:
                    preClosePrice = 0
                else:
                    tmpKey = self.keyList[aIdx - 1]
                    preClosePrice = self.dataDict.get(tmpKey).get("CP")            
            self._drawLine(preClosePrice, aDict, dispIdx, False)
            preClosePrice = aDict.get("CP")
            self.lastKey = aKey

    def _drawLine(self, preClose, aDict, dispIdx, isLastFlag):
        """
        
        """
        groupStr = self.instGroup
        if isLastFlag == True:
            groupStr += "_lastData"
        else:
            groupStr += "_curvData"
        
        instg = InstructionGroup(group=groupStr)
        color = Color()

        volume = aDict.get("VOL")

        closePrice = aDict.get("CP")
        if closePrice > preClose:
            color.rgba = self.UP_COLOR
            instg.add(color)
            x1 = self.chartPos[0] + dispIdx * (self.tickWide + self.tickGap) + self.tickGap 
            y1 = self.chartPos[1]
            instg.add(Rectangle(pos=(x1,y1), size=(self.tickWide, (volume - self.lowestValue) * self.yscale)))
        elif closePrice < preClose:
            color.rgba = self.DOWN_COLOR
            instg.add(color)
            x1 = self.chartPos[0] + dispIdx * (self.tickWide + self.tickGap) + self.tickGap 
            y1 = self.chartPos[1]
            instg.add(Rectangle(pos=(x1,y1), size=(self.tickWide, (volume - self.lowestValue) * self.yscale)))            
        else:
            color.rgba = self.EQUAL_COLOR
            instg.add(color)
            x1 = self.chartPos[0] + dispIdx * (self.tickWide + self.tickGap) + self.tickGap 
            y1 = self.chartPos[1]
            instg.add(Rectangle(pos=(x1,y1), size=(self.tickWide, (volume - self.lowestValue) * self.yscale)))

        self.canvas.add(instg)
        
    
    def addData(self, paramList):
        """
        添加匯圖之資料，paramList為一list物件，list中為一dict物件，格式如下所示:
        {'TD':'時間','CP':'收盤價','VOL':'成交量'}
        """
        for aDict in paramList:
            aKey = aDict.get("TD")
            self.dataDict[aKey] = aDict
        self.keyList = sorted(list(self.dataDict.keys())) 
    
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

        self.infoLayout.add_widget(self.info_vol)
        volume = aDict.get("VOL")
        valueStr = None
        if self.formatType == 1:            
            valueStr = ("{:7.2f}".format(volume)).strip()
        elif self.formatType == 2:
            valueStr = "${:,}".format(volume)
        else:
            valueStr = str(volume)
        self.info_vol.text = valueStr
        
        maxLength = len(self.info_time.text)
        if maxLength < schartutil.calcCharNum(self.info_vol.text):
            maxLength = schartutil.calcCharNum(self.info_vol.text)
        
        layoutWidth = schartutil.getInfoLayoutWidth(maxLength)
        self.infoLayout.col_default_width = layoutWidth
        self.infoLayout.size = [layoutWidth, 44]
    
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
            refDict["TechType"] = self.techType
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
        y1 = self.chartPos[1] + (aDict.get("VOL") - self.lowestValue) * self.yscale
        x2 = self.chartPos[0] + self.chartSize[0]
        y2 = y1
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)