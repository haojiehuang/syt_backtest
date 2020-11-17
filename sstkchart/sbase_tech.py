# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.graphics import Point, Line, Color, Rectangle, InstructionGroup
from kivy.utils import get_color_from_hex as colorHex

from selements import SCordLabel
import sutil
import schartutil

class SBaseTech():
    
    def __init__(self, paramDict):

        self.paramDict = paramDict

        self.infoLayout = None #顯示訊息之layout物件
        self.dataDict = {} #資料之dict
        self.keyList = [] #self.dataDict中之key所組成之list物件
        self.lastKey = None #最後一筆之key
        
        self.FRAME_COLOR = self.paramDict.get("FRAME_COLOR") #邊框的線條顏色
        self.GRID_COLOR = self.paramDict.get("GRID_COLOR") #直線條及橫線條的線條顏色
        self.CORD_INFO_COLOR = self.paramDict.get("CORD_INFO_COLOR") #座標資訊的文字顏色
        
        self._setInitInfo()
    
    def changeDrawInfo(self, refParamDict):
        if refParamDict == None:
            return
        for aKey in refParamDict.keys():
            self.paramDict[aKey] = refParamDict.get(aKey)
        
        self._setInitInfo()
    
    def _setInitInfo(self):
        self.layout = self.paramDict.get("Layout") #繪圖之layout
        self.canvas = self.paramDict.get("Canvas") #繪圖之canvas
        self.chartPos = self.paramDict.get("ChartPos") #圖形原點的位置
        self.chartSize = self.paramDict.get("ChartSize") #圖形的大小
        self.tickWide = self.paramDict.get("TickWide") #一個tick的寬度(共有幾個點)
        self.tickGap = self.paramDict.get("TickGap") #tick與tick之間點數
        self.backGap = self.tickWide / 2 #x軸座標回退值
        self.dispNum = self.paramDict.get("DispNum") #畫面顯示的筆數
        self.currentPage = self.paramDict.get("CurrentPage") #當前的頁數
        self.infoFunc = self.paramDict.get("InfoFunc") #顯示訊息之函式
        self.isDrawRect = self.paramDict.get("IsDrawRect") #是否顯示外框
        self.isDrawXCordLine = self.paramDict.get("IsDrawXCordLine") #是否顯示X軸直線
        self.isDrawXCordInfo = self.paramDict.get("IsDrawXCordInfo") #是否顯示X軸座標訊息
        self.isDrawYCordLine = self.paramDict.get("IsDrawYCordLine") #是否顯示Y軸直線
        self.isDrawYCordInfo = self.paramDict.get("IsDrawYCordInfo") #是否顯示Y軸座標訊息
        self.isDrawCrossLine = self.paramDict.get("IsDrawCrossLine") #是否顯示十字線
        self.instGroup = self.paramDict.get("InstGroup", "") #InstructionGroup所使用之group值
        self.formatType = self.paramDict.get("FormatType") #0.No format,1.float format,2.currency format
        self.techType = self.paramDict.get("TechType") #線圖類型
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
        self.dataType = self.paramDict.get("DataType") #資料類型
        self.isDrawXCordInfo = self.paramDict.get("IsDrawXCordInfo") #是否顯示X軸訊息
        
        self.scopeIdx = self.getScopeIdx() #取得當前頁次之起始索引值及截止索引值，回傳一list物件，格式為 [起始索引值,截止索引值]
        self.extremeValue = self.getExtremeValue() #圖形上的最大值與最小值，為一list物件，格式為 [最大值,最小值]
        aValue = self.paramDict.get("ExtremeValue")
        if aValue != None:
            self.extremeValue = aValue

        self._calcDrawInfo() 
    
    def getDataNum(self):
        """
        取得資料筆數
        """
        return len(self.keyList)
    
    def getDataDict(self):
        """
        取得資料之Dict
        """
        return self.dataDict
    
    def addData(self, paramList):
        """
        添加匯圖之資料，paramList為一list物件，list中為一dict物件，繼承類別必須覆寫此函數
        """
        pass
    
    def clearData(self):
        self.dataDict.clear()
        self.keyList.clear()

        self.canvas.remove_group(self.instGroup + "_lastData")
        self.canvas.remove_group(self.instGroup + "_curvData")
        self.canvas.remove_group(self.instGroup + "_xgrid")
        self.canvas.remove_group(self.instGroup + "_ygrid")
    
    def getScopeIdx(self):
        """
        取得當前頁次之起始索引值及截止索引值，回傳一list物件，格式如下所示:
        [起始索引值,截止索引值]
        程式說明如下：
        pageNum是由最後一筆往前算的，假設一頁顯示10，總共有25筆資料，第一頁顯示的是最後10筆資料，也就是區間為(15, 24)的資料；第二頁的區間為(5, 14)；
        第三頁因為不足10筆資料，所以補足10筆資料，區間為(0, 9)。若資料總筆數不足10筆資料，則第一頁的區間為(0, 總筆數-1)
        """
        if len(self.keyList) <= self.dispNum: #無論頁次是幾頁，若資料總筆數小於等於一頁的筆數，則回傳[0, 總筆數-1]
            if len(self.keyList) == 0:
                return [0, 0]
            else:
                return [0, len(self.keyList) - 1]
        startIdx = len(self.keyList) - self.currentPage * self.dispNum
        endIdx = len(self.keyList) - (self.currentPage - 1) * self.dispNum - 1
        if startIdx < 0:
            startIdx = 0
            endIdx = self.dispNum - 1

        return [startIdx, endIdx]
    
    def getKeyList(self):
        """
        取得當前頁次的key的list
        """
        if len(self.keyList) == 0:
            return []
        keyList = []
        for idx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
            keyList.append(self.keyList[idx])
        
        return keyList
    
    def getExtremeValue(self):
        """
        取得當前頁次之最大值及最小值，回傳一list物件，格式如下所示:
        [最大值,最小值]
        繼承類別必須覆寫此函式
        """
        return [0, 0]
    
    def _calcDrawInfo(self):
        """
        計算繪圖所需之資訊，繼承類別必須覆寫此函式
        """
        pass
    
    def charting(self):
        """
        繪圖函式，繼承類別必須覆寫此函式
        """
        pass

    def drawRectGrid(self):
        """
        繪製一矩形框的函式，paramDict內容如下所示:
        """
        frameGroup = self.instGroup + "_frame"
        self.canvas.remove_group(frameGroup)

        frameColor = Color()
        frameColor.rgba = self.FRAME_COLOR    

        instg = InstructionGroup(group=frameGroup) #左框線
        instg.add(frameColor)
        x1 = self.chartPos[0]
        y1 = self.chartPos[1]
        x2 = self.chartPos[0]
        y2 = self.chartPos[1] + self.chartSize[1]
        instg.add(Line(points=(x1, y1, x2, y2), width=1))        
        self.canvas.add(instg)
        
        instg = InstructionGroup(group=frameGroup) #右框線
        instg.add(frameColor)
        x1 = self.chartPos[0] + self.chartSize[0]
        y1 = self.chartPos[1]
        x2 = self.chartPos[0] + self.chartSize[0]
        y2 = self.chartPos[1] + self.chartSize[1]
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)

        instg = InstructionGroup(group=frameGroup) #下方框線
        instg.add(frameColor)
        x1 = self.chartPos[0]
        y1 = self.chartPos[1]
        x2 = self.chartPos[0] + self.chartSize[0]
        y2 = self.chartPos[1]
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
        
        instg = InstructionGroup(group=frameGroup) #上方框線
        instg.add(frameColor)
        x1 = self.chartPos[0]
        y1 = self.chartPos[1] + self.chartSize[1]
        x2 = self.chartPos[0] + self.chartSize[0]
        y2 = self.chartPos[1] + self.chartSize[1]
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
    
    def drawXCordInfo(self, removeLabelList):      
        """
        依據不同的dataType，畫出X軸直線及顯示座標訊息，dataType類型如下所示：
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
        """        
        keyList = self.getKeyList()
        if keyList == None or len(keyList) == 0:
            return
        
        gridGroup = self.instGroup + "_xgrid"
        self.canvas.remove_group(gridGroup)
        
        if removeLabelList != None: #移除layout上的y軸label物件
            for aLabel in removeLabelList:
                self.layout.remove_widget(aLabel)
        
        labelList = []
        
        procType = self.dataType % 100
        if procType == 2: #周線，第一次第二個月顯示一筆，之後每4個月顯示1筆，顯示到月
            gapNum = 2
            headKey = None
            addNum = None
            dispIdx = -1
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                dispIdx += 1
                aKey = self.keyList[aIdx]
                if headKey == None:
                    headKey = aKey[:6]
                    addNum = 0
                if headKey != aKey[:6]:
                    addNum += 1
                    if addNum == gapNum: #此判斷值代表間隔月數
                        self._drawXLineAndInfo(dispIdx, self._formatYearMonth(aKey[:6]), gridGroup, labelList)
                        addNum = 0                        
                        if gapNum == 2:
                            gapNum = 4
                    headKey = aKey[:6]
        elif procType == 3: #月線顯示每一年的第一筆，顯示年
            headKey = None
            dispIdx = -1
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                dispIdx += 1
                aKey = self.keyList[aIdx]
                if headKey == None:
                    headKey = aKey[:4]
                if headKey != aKey[:4]:
                    self._drawXLineAndInfo(dispIdx, aKey[:4], gridGroup, labelList)
                    headKey = aKey[:4]
        elif procType == 4: #季線，第一次第2年顯示一筆，之後每3年顯示1筆，顯示到年
            gapNum = 2
            headKey = None
            addNum = None
            dispIdx = -1
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                dispIdx += 1
                aKey = self.keyList[aIdx]
                if headKey == None:
                    headKey = aKey[:4]
                    addNum = 0
                if headKey != aKey[:4]:
                    addNum += 1
                    if addNum == gapNum: #此判斷值代表間隔年數
                        if gapNum == 2:
                            gapNum = 3
                        self._drawXLineAndInfo(dispIdx, aKey[:4], gridGroup, labelList)
                        addNum = 0
                    headKey = aKey[:4]
        elif procType == 5: #半年線，第一次第3年顯示一筆，之後每6年顯示1筆，顯示到年
            gapNum = 3
            headKey = None
            addNum = None
            dispIdx = -1
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                dispIdx += 1
                aKey = self.keyList[aIdx]
                if headKey == None:
                    headKey = aKey[:4]
                    addNum = 0
                if headKey != aKey[:4]:
                    addNum += 1
                    if addNum == gapNum: #此判斷值代表間隔年數
                        if gapNum == 3:
                            gapNum = 6
                        self._drawXLineAndInfo(dispIdx, aKey[:4], gridGroup, labelList)
                        addNum = 0
                    headKey = aKey[:4]
        elif procType == 6: #年線，第一次第5年顯示一筆，之後每15年顯示1筆，顯示到年
            gapNum = 5
            headKey = None
            addNum = None
            dispIdx = -1
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                dispIdx += 1
                aKey = self.keyList[aIdx]
                if headKey == None:
                    headKey = aKey[:4]
                    addNum = 0
                if headKey != aKey[:4]:
                    addNum += 1
                    if addNum == gapNum: #此判斷值代表間隔年數
                        if gapNum == 5:
                            gapNum = 15
                        self._drawXLineAndInfo(dispIdx, aKey[:4], gridGroup, labelList)
                        addNum = 0
                    headKey = aKey[:4]
        elif procType == 10 or procType == 11 or procType == 12 or procType == 13 or procType == 14 or procType == 15 or procType == 16:
            #1,5,10,20,30,60分線，第一次5筆顯示座標，之後每20筆顯示座標，顯示日期及時分
            gapNum = 10
            addNum = 0
            dispIdx = -1
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                dispIdx += 1
                aKey = self.keyList[aIdx]
                addNum += 1
                if addNum == gapNum:
                    if gapNum == 10:
                        gapNum = 25
                    self._drawXLineAndInfo(dispIdx, aKey[4:6] + "/" + aKey[6:8] + " " + sutil.formatTime(aKey[8:12]), gridGroup, labelList)
                    addNum = 0
        else: #日線顯示每月的第一筆，顯示到月
            headKey = None
            dispIdx = -1
            for aIdx in range(self.scopeIdx[0], self.scopeIdx[1] + 1):
                dispIdx += 1
                aKey = self.keyList[aIdx]
                if headKey == None:
                    headKey = aKey[:6]
                if headKey != aKey[:6]:
                    self._drawXLineAndInfo(dispIdx, self._formatYearMonth(aKey[:6]), gridGroup, labelList)
                    headKey = aKey[:6]
        
        return labelList

    def _formatYearMonth(self, yyyyMMStr):
        yyyyMM = int(yyyyMMStr)
        aYear = int(yyyyMM / 100)
        aMM = yyyyMM % 100
        aStr = str(aYear) + "/"
        if aMM < 10:
            aStr += "0" + str(aMM)
        else:
            aStr += str(aMM)
        return aStr

    def _drawXLineAndInfo(self, dispIdx, headKey, gridGroup, labelList):
        """
        畫X軸直線及座標訊息
        """
        gridColor = Color()
        gridColor.rgba = self.GRID_COLOR    

        instg = InstructionGroup(group=gridGroup)
        instg.add(gridColor)
        x1 = self.chartPos[0] + (dispIdx + 1) * (self.tickWide + self.tickGap) - self.backGap
        y1 = self.chartPos[1]
        x2 = x1
        y2 = self.chartPos[1] + self.chartSize[1]
        instg.add(Line(points=(x1, y1, x2, y2), width=1))        
        self.canvas.add(instg)
        
        if self.isDrawXCordInfo == False:
            return

        x0 = self.chartPos[0] + (dispIdx + 1) * (self.tickWide + self.tickGap) - self.backGap - 10
        y0 = self.chartPos[1] - 20
        alabel = SCordLabel(pos=(x0,y0),size_hint=(None,None))
        alabel.width = 20
        alabel.height = 20
        alabel.halign = "center"
        alabel.text = headKey
        alabel.color = self.CORD_INFO_COLOR
        self.layout.add_widget(alabel)
        labelList.append(alabel)       

    def drawYCordInfo(self, removeLabelList):
        """
        畫出Y軸的橫線及顯示座標訊息
        """
        if removeLabelList != None: #移除layout上的y軸label物件
            for aLabel in removeLabelList:
                self.layout.remove_widget(aLabel)
    
        gridGroup = self.instGroup + "y_grid"
        self.canvas.remove_group(gridGroup)        
        
        highestValue = None
        lowestValue = None
        if self.extremeValue[0] > 0:
            highestValue = self.extremeValue[0] * 1.01
        elif self.extremeValue[0] < 0:
            highestValue = self.extremeValue[0] * 0.99
        else:
            highestValue = self.extremeValue[0]
        if self.extremeValue[1] > 0:
            lowestValue = self.extremeValue[1] * 0.99
        elif self.extremeValue[0] < 0:
            lowestValue = self.extremeValue[1] * 1.01
        else:
            lowestValue = self.extremeValue[1]

        if lowestValue >= 0 or highestValue <= 0:
            return self._drawYCordInfo_1(gridGroup, highestValue, lowestValue)
        else:
            return self._drawYCordInfo_2(gridGroup, highestValue, lowestValue)
        return removeLabelList

    def _drawYCordInfo_1(self, gridGroup, highestValue, lowestValue):
        """
        畫出Y軸的橫線及顯示座標訊息
        """
        diffValue = highestValue - lowestValue
        if diffValue != 0:
            yscale = 1.0 * self.chartSize[1] / diffValue #線圖y軸縮放比例
        else:
            yscale = 1
        aValue = None
        stepValue = diffValue / 4
        
        gridColor = Color()
        gridColor.rgba = self.GRID_COLOR
        
        addLabelList = []
        for aIdx in range(1, 4):
            if diffValue < 10:
                cordValue = self.extremeValue[1] + aIdx * stepValue
            else:
                cordValue = int(self.extremeValue[1] + aIdx * stepValue)
            
            instg = InstructionGroup(group=gridGroup)
            x1 = self.chartPos[0]
            x2 = self.chartPos[0] + self.chartSize[0]
            y1 = int(self.chartPos[1] + (cordValue - lowestValue) * yscale)
            y2 = y1
            instg.add(gridColor)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))
            self.canvas.add(instg)
            
            if self.isDrawYCordInfo == True:
                if self.techType == "成交金額":
                    cordStr = ("{:7.2f}".format(cordValue / 100000000) + "億").strip()
                else:
                    if diffValue < 10:
                        cordStr = "{:7.2f}".format(cordValue).strip()
                    else:
                        cordStr = str(cordValue).strip()
                labelWidth = schartutil.getInfoLayoutWidth(schartutil.calcCharNum(cordStr))
                x0 = self.chartPos[0] + self.chartSize[0] + 3
                y0 = y1 - 8
                alabel = SCordLabel(text=cordStr,pos=(x0,y0),size_hint=(None,None))
                alabel.width = labelWidth
                alabel.height = 16
                alabel.halign = "left"
                alabel.color = self.CORD_INFO_COLOR
                self.layout.add_widget(alabel)
                addLabelList.append(alabel)                    
        
        return addLabelList

    def _drawYCordInfo_2(self, gridGroup, highestValue, lowestValue):
        """
        畫出Y軸的橫線及顯示座標訊息
        """
        diffValue = highestValue - lowestValue
        if diffValue != 0:
            yscale = 1.0 * self.chartSize[1] / diffValue #線圖y軸縮放比例
        else:
            yscale = 1
        aValue = None
        stepValue = diffValue / 4
        
        gridColor = Color()
        gridColor.rgba = self.GRID_COLOR
        
        addLabelList = []
        
        cordValue = 0
        
        instg = InstructionGroup(group=gridGroup)
        x1 = self.chartPos[0]
        x2 = self.chartPos[0] + self.chartSize[0]
        y1 = int(self.chartPos[1] + (cordValue - lowestValue) * yscale)
        y2 = y1
        instg.add(gridColor)
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
        
        if self.isDrawYCordInfo == True:
            cordStr = str(cordValue).strip()
            labelWidth = schartutil.getInfoLayoutWidth(schartutil.calcCharNum(cordStr))
            x0 = self.chartPos[0] + self.chartSize[0] + 3
            y0 = y1 - 8
            alabel = SCordLabel(text=cordStr,pos=(x0,y0),size_hint=(None,None))
            alabel.width = labelWidth
            alabel.height = 16
            alabel.halign = "left"
            alabel.color = self.CORD_INFO_COLOR
            self.layout.add_widget(alabel)
            addLabelList.append(alabel)
        
        addNum = 0
        while (True):
            addNum -= 1
            cordValue = addNum * stepValue
            if cordValue < lowestValue:
                break
            instg = InstructionGroup(group=gridGroup)
            x1 = self.chartPos[0]
            x2 = self.chartPos[0] + self.chartSize[0]
            y1 = int(self.chartPos[1] + (cordValue - lowestValue) * yscale)
            y2 = y1
            instg.add(gridColor)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))
            self.canvas.add(instg)
            
            if self.isDrawYCordInfo == True:
                if diffValue < 10:
                    cordStr = ("{:7.2f}".format(cordValue)).strip()
                else:
                    cordStr = str(int(cordValue)).strip()
                labelWidth = schartutil.getInfoLayoutWidth(schartutil.calcCharNum(cordStr))
                x0 = self.chartPos[0] + self.chartSize[0] + 3
                y0 = y1 - 8
                alabel = SCordLabel(text=cordStr,pos=(x0,y0),size_hint=(None,None))
                alabel.width = labelWidth
                alabel.height = 16
                alabel.halign = "left"
                alabel.color = self.CORD_INFO_COLOR
                self.layout.add_widget(alabel)
                addLabelList.append(alabel)

        addNum = 0
        while (True):
            addNum += 1
            cordValue = addNum * stepValue
            if cordValue > highestValue:
                break
            instg = InstructionGroup(group=gridGroup)
            x1 = self.chartPos[0]
            x2 = self.chartPos[0] + self.chartSize[0]
            y1 = int(self.chartPos[1] + (cordValue - lowestValue) * yscale)
            y2 = y1
            instg.add(gridColor)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))
            self.canvas.add(instg)
            
            highest_pos_y = self.chartPos[1] + self.chartSize[1]
            if self.isDrawYCordInfo == True and y2 < (highest_pos_y - 8):
                if diffValue < 10:
                    cordStr = ("{:7.2f}".format(cordValue)).strip()
                else:
                    cordStr = str(int(cordValue)).strip()
                labelWidth = schartutil.getInfoLayoutWidth(schartutil.calcCharNum(cordStr))
                x0 = self.chartPos[0] + self.chartSize[0] + 3
                y0 = y1 - 8
                alabel = SCordLabel(text=cordStr,pos=(x0,y0),size_hint=(None,None))
                alabel.width = labelWidth
                alabel.height = 16
                alabel.halign = "left"
                alabel.color = self.CORD_INFO_COLOR
                self.layout.add_widget(alabel)
                addLabelList.append(alabel)        
        
        return addLabelList
    
    def drawKLineYCordInfo(self, removeLabelList):
        """
        畫出Y軸的橫線及顯示座標訊息
        """
        if removeLabelList != None: #移除layout上的y軸label物件
            for aLabel in removeLabelList:
                self.layout.remove_widget(aLabel)
                
        gridGroup = self.instGroup + "y_grid"
        self.canvas.remove_group(gridGroup)
        
        highestValue = self.extremeValue[0] * 1.01
        lowestValue = self.extremeValue[1] * 0.99
        diffValue = highestValue - lowestValue
        if diffValue != 0:
            yscale = 1.0 * self.chartSize[1] / diffValue #線圖y軸縮放比例
        else:
            yscale = 1
        
        cordValue = None
        stepValue = diffValue / 9
        
        gridColor = Color()
        gridColor.rgba = self.GRID_COLOR
        
        addLabelList = []
        for aIdx in range(1, 9):
            cordValue = lowestValue + aIdx * stepValue
            
            instg = InstructionGroup(group=gridGroup)
            x1 = self.chartPos[0]
            x2 = self.chartPos[0] + self.chartSize[0]
            y1 = int(self.chartPos[1] + (cordValue - lowestValue) * yscale)
            y2 = y1
            instg.add(gridColor)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))
            self.canvas.add(instg)
            
            if self.isDrawYCordInfo == True:
                cordStr = ("{:7.2f}".format(cordValue)).strip()
                labelWidth = schartutil.getInfoLayoutWidth(schartutil.calcCharNum(cordStr))
                x0 = self.chartPos[0] + self.chartSize[0] + 3
                y0 = y1 - 8
                alabel = SCordLabel(text=cordStr,pos=(x0,y0),size_hint=(None,None))
                alabel.width = labelWidth
                alabel.height = 16
                alabel.halign = "left"
                alabel.color = self.CORD_INFO_COLOR
                self.layout.add_widget(alabel)
                addLabelList.append(alabel)                
        
        return addLabelList
        
    
    
    
    
        