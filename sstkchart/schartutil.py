# -*- coding: utf-8 -*-

"""
@author: jason
"""

from kivy.graphics import Point, Line, Color, Rectangle, InstructionGroup
from kivy.utils import get_color_from_hex as colorHex

from selements import SCordLabel

def getInfoLayoutWidth(charNum):
    
    return charNum * 7.8

def calcCharNum(aStr):
    charNum = 0
    for idx in range(0, len(aStr)):
        if ord(aStr[idx]) > 255:
            charNum += 2
        else:
            charNum += 1
    
    return charNum

class SMinTimeCordUtil():
    
    paramDict = None
    
    layout = None
    canvas = None
    width = 800
    height = 600
    x_start_pos = 0
    y_start_pos = 0
    xscale = 1.0
    yscale = 1.0
    rectColor = colorHex("#000000")
    rectWidth = 1
    gridColor = colorHex("#000000")
    gridWidth = 1    
    cordColor = colorHex("#000000")
    instGroup = ""
    shift_left = 1
    drawFlagList = [False, False]
    formatFlag = True
    
    def __init__(self, paramDict):
        """
        建構式: 參數如下所示:
        1."layout": 添加座標資訊之layout物件
        2."canvas": 繪圖之canvas物件
        3."width": 繪圖之寬度
        4."height": 繪圖之高度
        5."x_start_pos": 繪圖之起始x軸位置
        6."y_start_pos": 繪圖之起始y軸位置
        7."xscale": x軸縮放比例
        8."yscale": y軸縮放比例
        9."rectColor": 外框線的顏色
        10."rectWidth": 外框線的寬度
        11."gridColor": 線條的顏色
        12."gridWidth": 線條的寬度
        13."cordColor": 座標訊息的文字顏色
        14."instGroup": InstructionGroup所使用之group值
        15."shift_left": 左位移值
        16."drawFlagList": 一list物件，只有[0]及[1]，y軸座標資訊的第一筆及最後一筆是否要繪出橫線
        17."formatFlag": 欄位是否要格式化
        """
        self.paramDict = paramDict
        self.layout = paramDict.get("layout")
        self.canvas = paramDict.get("canvas")
        self.width = paramDict.get("width")
        self.height = paramDict.get("height")
        self.x_start_pos = paramDict.get("x_start_pos")
        self.y_start_pos = paramDict.get("y_start_pos")
        self.xscale = paramDict.get("xscale")
        self.yscale = paramDict.get("yscale")
        self.rectColor = paramDict.get("rectColor")
        self.rectWidth = paramDict.get("rectWidth")
        self.gridColor = paramDict.get("gridColor")
        self.gridWidth = paramDict.get("gridWidth")
        self.cordColor = paramDict.get("cordColor")
        self.instGroup = paramDict.get("instGroup", "instGroup")
        self.shift_left = paramDict.get("shift_left")
        self.drawFlagList = paramDict.get("drawFlagList")
        self.formatFlag = paramDict.get("formatFlag")

    def drawRectGrid(self):
        """
        繪製一矩形框的函式，paramDict內容如下所示:
        """
        frameGroup = self.instGroup + "_frame"
        self.canvas.remove_group(frameGroup)
    
        frameColor = Color()
        frameColor.rgba = self.rectColor    
    
        instg = InstructionGroup(group=frameGroup) #左框線
        instg.add(frameColor)
        x1 = self.x_start_pos
        y1 = self.y_start_pos
        x2 = self.x_start_pos
        y2 = self.y_start_pos + self.height
        instg.add(Line(points=(x1, y1, x2, y2), width=self.rectWidth))        
        self.canvas.add(instg)
        
        instg = InstructionGroup(group=frameGroup) #右框線
        instg.add(frameColor)
        x1 = self.x_start_pos + self.width
        y1 = self.y_start_pos
        x2 = self.x_start_pos + self.width
        y2 = self.y_start_pos + self.height
        instg.add(Line(points=(x1, y1, x2, y2), width=self.rectWidth))
        self.canvas.add(instg)

        instg = InstructionGroup(group=frameGroup) #下方框線
        instg.add(frameColor)
        x1 = self.x_start_pos
        y1 = self.y_start_pos
        x2 = self.x_start_pos + self.width
        y2 = self.y_start_pos
        instg.add(Line(points=(x1, y1, x2, y2), width=self.rectWidth))
        self.canvas.add(instg)
        
        instg = InstructionGroup(group=frameGroup) #上方框線
        instg.add(frameColor)
        x1 = self.x_start_pos
        y1 = self.y_start_pos + self.height
        x2 = self.x_start_pos + self.width
        y2 = self.y_start_pos + self.height
        instg.add(Line(points=(x1, y1, x2, y2), width=self.rectWidth))
        self.canvas.add(instg)

    def drawYGridCord(self, paramDict):
        """
        繪製一y軸座標訊息及橫線的函式，paramDict內容如下所示:
        1."infoList": 顯示座標訊息之list物件
        2."lowestValue": 資訊之最小值 
        3."removeLabelList": layout要移除之label的list
        """
        infoList = paramDict.get("infoList")
        lowestValue = paramDict.get("lowestValue")
        removeLabelList = paramDict.get("removeLabelList")
    
        if removeLabelList != None: #移除layout上的y軸label物件
            for aLabel in removeLabelList:
                self.layout.remove_widget(aLabel)
    
        gridGroup = self.instGroup + "y_grid"
        self.canvas.remove_group(gridGroup)
    
        _gridColor = Color()
        _gridColor.rgba = self.gridColor
    
        addLabelList = []
        for i in range(0, len(infoList)):
            y1 = int(self.y_start_pos + (infoList[i] - lowestValue) * self.yscale)
            y2 = y1
            flag = False
            infoFlag = True
            if i == 0:
                if self.drawFlagList[0] == True:
                    flag = True
                else:
                    infoFlag = False
            if i == (len(infoList) - 1) and self.drawFlagList[1] == True:
                flag = True
            if i != 0 and i != (len(infoList) - 1):
                flag = True
            if flag == True:
                instg = InstructionGroup(group=gridGroup)
                x1 = self.x_start_pos
                x2 = self.x_start_pos + self.width 
                instg.add(_gridColor)
                instg.add(Line(points=(x1, y1, x2, y2), width=self.gridWidth))
                self.canvas.add(instg)

            if infoFlag == False:
                continue

            cordValue = infoList[i]
            labelWidth = None
            if self.formatFlag == True:
                cordStr = "{:7.2f}".format(cordValue)     
                labelWidth = self.shift_left - 2
                x0 = self.x_start_pos - self.shift_left + 2
            else:
                cordStr = str(cordValue)
                labelWidth = self.shift_left - 10
                x0 = self.x_start_pos - self.shift_left + 18
            y0 = y1 - 8
            #y0 = y1
            alabel = SCordLabel(text=cordStr,pos=(x0,y0),size_hint=(None,None))
            alabel.width = labelWidth
            alabel.height = 16
            alabel.halign = "right"
            alabel.color = self.cordColor
            self.layout.add_widget(alabel)
            addLabelList.append(alabel)
    
        return addLabelList

    def drawXTimeCord(self, paramDict):
        """
        繪製一走勢圖之x軸座標訊息及直線的函式，paramDict內容如下所示:
        1."infoList": 顯示座標訊息之list物件，格式如下所示：
          [[timeIndex, time], [timeIndex, time] .....]
        2."removeLabelList": layout要移除之label的list
        """
        infoList = paramDict.get("infoList")
        removeLabelList = paramDict.get("removeLabelList")
    
        if removeLabelList != None: #移除layout上的x軸label物件
            for aLabel in removeLabelList:
                self.layout.remove_widget(aLabel)
    
        gridGroup = self.instGroup + "x_grid"
        self.canvas.remove_group(gridGroup)
    
        _gridColor = Color()
        _gridColor.rgba = self.gridColor
    
        addLabelList = []
        for aInfo in infoList:
            x0 = self.x_start_pos + aInfo[0] * self.xscale - 10
            y0 = self.y_start_pos - 20
            dateStr = str(aInfo[1])
            alabel = SCordLabel(pos=(x0,y0),size_hint=(None,None))
            alabel.width = 20
            alabel.height = 20
            alabel.halign = "center"
            alabel.text = dateStr
            alabel.color = self.cordColor
            self.layout.add_widget(alabel)
            addLabelList.append(alabel)
            
            instg = InstructionGroup(group=gridGroup)
            if aInfo[0] == 0:
                continue
            x1 = self.x_start_pos + aInfo[0] * self.xscale
            y1 = self.y_start_pos
            x2 = x1
            y2 = y1 + self.height
            instg.add(_gridColor)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))
            self.canvas.add(instg)
    
        return addLabelList