# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.graphics import Line, Color, InstructionGroup

from selements import SLabel, SInfoLayout
from sbase_tech import SBaseTech
import schartutil
import sutil

class SCurvGraph(SBaseTech):
    
    def __init__(self, paramDict):

        super().__init__(paramDict)

        self.CORD_INFO_COLOR = paramDict.get("CORD_INFO_COLOR") #座標資訊的文字顏色
        self.DATA_INFO_COLOR = paramDict.get("DATA_INFO_COLOR") #資訊的文字顏色
        self.CURV_COLOR = paramDict.get("CURV_COLOR") #線條顏色
        self.CROSS_LINE_COLOR = paramDict.get("CROSS_LINE_COLOR") #十字線顏色
        self.techType = paramDict.get("TechType") #技術分析類型

        self.info_time = SLabel(text="") #時間
        self.info_time.color = self.DATA_INFO_COLOR 
        self.info_data = SLabel(text="") #訊息的值
        self.info_data.color = self.DATA_INFO_COLOR

    def _calcDrawInfo(self):
        """
        計算繪圖所需之資訊
        """
        if self.extremeValue[0] > 0:
            self.highestValue = self.extremeValue[0] * 1.01
        elif self.extremeValue[0] < 0:
            self.highestValue = self.extremeValue[0] * 0.99
        else:
            self.highestValue = self.extremeValue[0]
        if self.extremeValue[1] > 0:
            self.lowestValue = self.extremeValue[1] * 0.99
        elif self.extremeValue[0] < 0:
            self.lowestValue = self.extremeValue[1] * 1.01
        else:
            self.lowestValue = self.extremeValue[1]
        diffValue = self.highestValue - self.lowestValue
        if diffValue != 0:
            self.yscale = 1.0 * self.chartSize[1] / diffValue #線圖y軸縮放比例
        else:
            self.yscale = 1
        if self.dispNum <= len(self.dataDict):
            self.dispMax = self.dispNum
        else:
            self.dispMax = len(self.dataDict)

    def getExtremeValue(self):
        """
        取得在某一頁次之最大值及最小值，回傳一list物件，格式如下所示:
        [最大值,最小值]
        """
        if len(self.keyList) == 0:
            return [0, 0]
        maxValue = sys.maxsize * -1 - 1
        minValue = sys.maxsize
        try:
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                aKey = self.keyList[aIdx]
                aValue = self.dataDict.get(aKey)
                if aValue > maxValue:
                    maxValue = aValue
                if aValue < minValue:
                    minValue = aValue
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
            aValue = self.dataDict.get(aKey)
            if isFirst == True:
                isFirst = False
                if aIdx == 0:
                    preValue = (self.highestValue - self.lowestValue) / 2 + self.lowestValue
                else:
                    tmpKey = self.keyList[aIdx - 1]
                    preValue = self.dataDict.get(tmpKey)
            self._drawLine(preValue, aValue, dispIdx, False)
            preValue = aValue
            self.lastKey = aKey

    def _drawLine(self, preValue, aValue, dispIdx, isLastFlag):
        """
        繪製曲線
        """
        groupStr = self.instGroup
        if isLastFlag == True:
            groupStr += "_lastData"
        else:
            groupStr += "_curvData"    
        instg = InstructionGroup(group=groupStr)
        color = Color()
        color.rgba = self.CURV_COLOR
        instg.add(color)
        #(self.tickWide + self.tickGap)代表顯示一筆資料，在x軸方向所需的總點數
        x1 = self.chartPos[0] + dispIdx * (self.tickWide + self.tickGap) - self.backGap
        y1 = self.chartPos[1] + (preValue - self.lowestValue) * self.yscale
        x2 = x1 + (self.tickWide + self.tickGap)
        y2 = self.chartPos[1] + (aValue - self.lowestValue) * self.yscale
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
    
    def addData(self, paramList):
        """
        添加匯圖之資料，paramList為一list物件，list中為一dict物件，格式如下所示:
        {'TD':'時間','Value':'值'}
        """
        for aDict in paramList:
            aKey = aDict.get("TD")
            self.dataDict[aKey] = aDict.get("Value")
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
        aValue = self.dataDict.get(aKey)
        
        self.infoLayout.add_widget(self.info_time)
        self.info_time.text = sutil.formatDateTime(aKey)

        self.infoLayout.add_widget(self.info_data)
        valueStr = None
        if self.formatType == 1:            
            valueStr = ("{:7.2f}".format(aValue)).strip()
        elif self.formatType == 2:
            valueStr = "${:,}".format(aValue)
        else:
            valueStr = str(aValue)
        self.info_data.text = valueStr

        maxLength = len(self.info_time.text)
        if maxLength < len(self.info_data.text):
            maxLength = len(self.info_data.text)
        
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
        繪製十字線
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
            aValue = self.dataDict.get(aKey)
            self.infoFunc({"TechType":self.techType, "TD":aKey, "Value":aValue})
        
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
        aValue = self.dataDict.get(aKey)        
        
        instg = InstructionGroup(group=groupStr)
        instg.add(color)
        x1 = self.chartPos[0]
        y1 = self.chartPos[1] + (aValue - self.lowestValue) * self.yscale
        x2 = self.chartPos[0] + self.chartSize[0]
        y2 = y1 
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
        
