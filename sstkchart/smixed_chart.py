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
from scurv_graph import SCurvGraph
from sbar_graph import SBarGraph
from svolbar_graph import SVolBarGraph
import sutil

class SMixedChart():
    
    removeXCordList = None
    removeYCordList = None
    crossLineIndex = None
    mixedGraphList = None
    klineDict = None
    refParam = None
    
    def __init__(self, paramDict):
        
        self.layout = paramDict.get("Layout")

        self.isPriceMA = paramDict.get("IsPriceMA")
        self.isDrawRect = paramDict.get("IsDrawRect") #是否畫外框
        if self.isDrawRect == None:
            self.isDrawRect = False
        self.isDrawXCordLine = paramDict.get("IsDrawXCordInfo") #是否顯示X軸直線
        if self.isDrawXCordLine == None:
            self.isDrawXCordLine = False
        self.isDrawXCordInfo = paramDict.get("IsDrawXCordInfo") #是否顯示X軸座標訊息
        if self.isDrawXCordInfo == None:
            self.isDrawXCordInfo = False
        self.isDrawYCordLine = paramDict.get("IsDrawYCordInfo") #是否顯示Y軸直線
        if self.isDrawYCordLine == None:
            self.isDrawYCordLine = False
        self.isDrawYCordInfo = paramDict.get("IsDrawYCordInfo") #是否顯示Y軸座標訊息
        if self.isDrawYCordInfo == None:
            self.isDrawYCordInfo = False
        self.isDrawCrossLine = paramDict.get("IsDrawCrossLine") #是否顯示十字線
        if self.isDrawCrossLine == None:
            self.isDrawCrossLine = False

        self.refParam = {}
        for aKey in paramDict.keys():
            self.refParam[aKey] = paramDict.get(aKey)

        aGraph = None
        mixedParam = None
        self.mixedGraphList = []
        self.lineSetup = paramDict.get("LineSetup")
        self.setLineSetup(self.lineSetup)

    def changeDrawInfo(self, refParamDict):
        if self.mixedGraphList == None or refParamDict == None:
            return
        for aGraph in self.mixedGraphList:
            aGraph.changeDrawInfo(refParamDict)

    def setLineSetup(self, lineSetup):
        
        self.mixedGraphList.clear()
        lineSetupList = lineSetup.split(";")
        isFirstRecord = True
        aIdx = -1
        for aStr in lineSetupList:
            if aStr == "":
                continue
            aList = aStr.split("|")
            if len(aList) < 2:
                continue
            mixedParam = {}
            for aKey in self.refParam.keys():
                mixedParam[aKey] = self.refParam.get(aKey)
            if isFirstRecord == True:
                isFirstRecord = False
                if self.isDrawRect == True:
                    mixedParam["IsDrawRect"] = True
                else:
                    mixedParam["IsDrawRect"] = False
                if self.isDrawXCordLine == True:
                    mixedParam["IsDrawXCordLine"] = True
                else:
                    mixedParam["IsDrawXCordLine"] = False
                if self.isDrawXCordInfo == True:
                    mixedParam["IsDrawXCordInfo"] = True
                else:
                    mixedParam["IsDrawXCordInfo"] = False
                if self.isDrawYCordLine == True:
                    mixedParam["IsDrawYCordLine"] = True
                else:
                    mixedParam["IsDrawYCordLine"] = False
                if self.isDrawYCordInfo == True:
                    mixedParam["IsDrawYCordInfo"] = True
                else:
                    mixedParam["IsDrawYCordInfo"] = False                
                if self.isDrawCrossLine == True:
                    mixedParam["IsDrawCrossLine"] = True
                else:
                    mixedParam["IsDrawCrossLine"] = False
            else:
                mixedParam["IsDrawRect"] = False
                mixedParam["IsDrawXCordLine"] = False
                mixedParam["IsDrawXCordInfo"] = False
                mixedParam["IsDrawYCordLine"] = False
                mixedParam["IsDrawYCordInfo"] = False                
                mixedParam["IsDrawCrossLine"] = False
            aIdx += 1
            if aList[1] == "LINE":
                mixedParam["TechType"] = aList[0]
                mixedParam["CURV_COLOR"] = colorHex("#" + aList[2])
                mixedParam["InstGroup"] = self.refParam.get("InstGroup") + "_" + str(aIdx)
                aGraph = SCurvGraph(mixedParam)
                self.mixedGraphList.append(aGraph)
            elif aList[1] == "VOLSTICK":
                mixedParam["TechType"] = aList[0]
                mixedParam["UP_COLOR"] = colorHex("#" + aList[2])
                mixedParam["DOWN_COLOR"] = colorHex("#" + aList[3])
                mixedParam["EQUAL_COLOR"] = colorHex("#" + aList[4])
                mixedParam["InstGroup"] = self.refParam.get("InstGroup") + "_" + str(aIdx)
                aGraph = SVolBarGraph(mixedParam)
                self.mixedGraphList.append(aGraph)
            elif aList[1] == "STICK":
                mixedParam["TechType"] = aList[0]
                mixedParam["UP_COLOR"] = colorHex("#" + aList[2])
                mixedParam["DOWN_COLOR"] = colorHex("#" + aList[3])
                mixedParam["EQUAL_COLOR"] = colorHex("#" + aList[3])
                mixedParam["InstGroup"] = self.refParam.get("InstGroup") + "_" + str(aIdx)
                aGraph = SBarGraph(mixedParam)
                self.mixedGraphList.append(aGraph)

    def charting(self):
        """
        繪圖
        """
        if self.mixedGraphList == None:
            return
        extremeValue = None
        tmpExtremeValue = None
        for aGraph in self.mixedGraphList:
            tmpExtremeValue = aGraph.extremeValue
            if extremeValue == None:
                extremeValue = tmpExtremeValue
            else:
                if extremeValue[0] < tmpExtremeValue[0]:
                    extremeValue[0] = tmpExtremeValue[0]
                if extremeValue[1] > tmpExtremeValue[1]:
                    extremeValue[1] = tmpExtremeValue[1]
        for aGraph in self.mixedGraphList:
            aGraph.changeDrawInfo({"ExtremeValue":extremeValue})
            if aGraph.isDrawRect == True:
                aGraph.drawRectGrid() #繪製一矩形框
            if aGraph.isDrawXCordLine == True:
                self.removeXCordList = aGraph.drawXCordInfo(self.removeXCordList) #繪製X軸直線及座標訊息
            if aGraph.isDrawYCordLine == True:
                self.removeYCordList = aGraph.drawYCordInfo(self.removeYCordList) #繪製Y軸直線及座標訊息
            aGraph.charting()
        
    def addData(self, paramList):
        if self.mixedGraphList == None:
            return
        dataList = []
        aList = None
        isFirstRecord = True
        for astr in paramList:
            aList = astr.split("|")
            if (len(aList) - 1) != len(self.mixedGraphList):
                continue
            if isFirstRecord == True:
                isFristRecord = False
                for idx in range(0, len(aList)):
                    dataList.append([])
            aDateTime = aList[0]
            for aIdx in range(1, len(aList)):
                tmpIdx = aIdx - 1
                aGraph = self.mixedGraphList[tmpIdx]
                if aGraph.techType == "VOL" or aGraph.techType == "成交金額":
                    aDict = {}
                    aDict["TD"] = aDateTime
                    aDict["VOL"] = float(aList[aIdx])
                    # 1001-Begin: 20201022調整，因應數據庫資料異常
                    #aDict["CP"] = self.klineDict.get(aDateTime).get("CP")
                    if self.klineDict.get(aDateTime) != None:
                        aDict["CP"] = self.klineDict.get(aDateTime).get("CP")
                    else:
                        aDict["CP"] = 0
                    # 1001-End.
                    dataList[tmpIdx].append(aDict)
                else:
                    dataList[tmpIdx].append({"TD":aDateTime,"Value":float(aList[aIdx])})
        aIdx = -1
        for aGraph in self.mixedGraphList:
            aIdx += 1
            aGraph.addData(dataList[aIdx])

    def clearData(self):
        if self.mixedGraphList != None:
            for aGraph in self.mixedGraphList:
                aGraph.clearData()
            self.mixedGraphList.clear()
        if self.removeXCordList != None:
            for aLabel in self.removeXCordList:
                self.layout.remove_widget(aLabel)
        if self.removeYCordList != None:
            for aLabel in self.removeYCordList:
                self.layout.remove_widget(aLabel)           
        if self.klineDict != None:
            self.klineDict.clear()

    def getExtremeValue(self):
        if self.mixedGraphList == None:
            return
        extremeValue = None
        tmpExtremeValue = None
        for aGraph in self.mixedGraphList:
            tmpExtremeValue = aGraph.getExtremeValue()
            if extremeValue == None:
                extremeValue = tmpExtremeValue
            else:
                if extremeValue[0] < tmpExtremeValue[0]:
                    extremeValue[0] = tmpExtremeValue[0]
                if extremeValue[1] > tmpExtremeValue[1]:
                    extremeValue[1] = tmpExtremeValue[1]
        return extremeValue
        
    def drawCrossLine(self, aIndex):
        if self.mixedGraphList == None:
            return
        for aGraph in self.mixedGraphList:
            aGraph.drawCrossLine(aIndex)

    def setKLineDict(self, aDict):
        if aDict != None:
            self.klineDict = {}
            for aKey in aDict.keys():
                self.klineDict[aKey] = aDict.get(aKey)