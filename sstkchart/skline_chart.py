# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.graphics import Line, Color, InstructionGroup
from kivy.utils import get_color_from_hex as colorHex

from selements import SLabel, SInfoLayout
from skline_graph import SKLineGraph
import sutil

class SKLineChart():
    
    klineGraph = None
    removeXCordList = None
    removeYCordList = None
    crossLineIndex = None    
    
    def __init__(self, paramDict):

        self.layout = paramDict.get("Layout")

        refParam = {}
        for aKey in paramDict.keys():
            refParam[aKey] = paramDict.get(aKey)   

        klineChartDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "skline_chart.ini"))
        refParam["FRAME_COLOR"] = colorHex(klineChartDict.get("FRAME_COLOR")) #邊框的線條顏色
        refParam["CORD_INFO_COLOR"] = colorHex(klineChartDict.get("CORD_INFO_COLOR")) #座標資訊的文字顏色
        refParam["DATA_INFO_COLOR"] = colorHex(klineChartDict.get("DATA_INFO_COLOR")) #資訊的文字顏色
        refParam["KLINE_COLOR"] = colorHex(klineChartDict.get("KLINE_COLOR")) #線條顏色
        refParam["SOLID_COLOR"] = colorHex(klineChartDict.get("SOLID_COLOR")) #K線中陽線的顏色
        refParam["VIRTUAL_COLOR"] = colorHex(klineChartDict.get("VIRTUAL_COLOR")) #K線中陰線的顏色
        refParam["CROSS_LINE_COLOR"] = colorHex(klineChartDict.get("CROSS_LINE_COLOR")) #十字線顏色
        
        self.klineGraph = SKLineGraph(refParam)

    def changeDrawInfo(self, refParamDict):
        if self.klineGraph == None or refParamDict == None:
            return
        self.klineGraph.changeDrawInfo(refParamDict)
        
    def charting(self):
        """
        繪圖
        """
        if self.klineGraph == None:
            return
        
        print("1111", self.klineGraph.extremeValue, self.klineGraph.dataType, self.klineGraph.chartSize)
        self.klineGraph.charting()
        if self.klineGraph.isDrawRect == True:
            self.klineGraph.drawRectGrid() #繪製一矩形框
        if self.klineGraph.isDrawXCordLine == True:
            self.removeXCordList = self.klineGraph.drawXCordInfo(self.removeXCordList) #繪製X軸直線及資訊
        if self.klineGraph.isDrawYCordLine == True:
            self.removeYCordList = self.klineGraph.drawKLineYCordInfo(self.removeYCordList) #繪製Y軸直線及資訊

    def getScopeIdx(self):
        if self.klineGraph != None:
            return self.klineGraph.getScopeIdx()
        return [0, 0]
    
    def getDataNum(self):
        if self.klineGraph != None:
            return self.klineGraph.getDataNum()
        return 0
    
    def getDataDict(self):
        if self.klineGraph != None:
            return self.klineGraph.getDataDict()

    def addData(self, paramList):
        if self.klineGraph != None:
            self.klineGraph.addData(paramList)

    def clearData(self):
        if self.klineGraph != None:
            if self.removeXCordList != None:
                for aLabel in self.removeXCordList:
                    self.layout.remove_widget(aLabel)
            if self.removeYCordList != None:
                for aLabel in self.removeYCordList:
                    self.layout.remove_widget(aLabel)             
            self.klineGraph.clearData()

    def getExtremeValue(self):
        if self.klineGraph != None:
            return self.klineGraph.getExtremeValue()
        
    def drawCrossLine(self, aIndex):
        if self.klineGraph != None:
            self.klineGraph.drawCrossLine(aIndex)

