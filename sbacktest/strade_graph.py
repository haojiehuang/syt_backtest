# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Point, Line, Color, Rectangle, InstructionGroup
from kivy.utils import get_color_from_hex as colorHex
import sconsts as CONSTS
import sutil
import math
from kivy.core.text import Label as CoreLabel
from selements import SLabel, SCordLabel, SInfoLayout

class STradeGraph(FloatLayout):
    
    isFocus = True
    infoLayout = None
    profitPerNumDict = {}
    xcordDict = {}
    
    def __init__(self, paramDict, **kwargs):
        super(STradeGraph, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.btmenu = self.paramDict.get(CONSTS.S_BTMENU)
        self.dataList = self.paramDict.get("dataList")
        # 1001-Start: 計算最大及最小獲利率
        self.min_profitPer = 0
        self.max_profitPer = 0
        tmpProfitPer = None
        if self.dataList != None and len(self.dataList) != 0:
            for profitPer in self.dataList:
                if profitPer < 0:
                    tmpProfitPer = math.floor(profitPer)
                else:
                    tmpProfitPer = math.ceil(profitPer)
                if tmpProfitPer > self.max_profitPer:
                    self.max_profitPer = tmpProfitPer
                if tmpProfitPer < self.min_profitPer:
                    self.min_profitPer = tmpProfitPer
        self.min_profitPer = int(self.min_profitPer)
        self.max_profitPer = int(self.max_profitPer)
        # 1001-End.
        self.maxNum = 5
        self.yscale = 1

        tradeGraphDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "trade_graph.ini"))
        self.shift_left = int(tradeGraphDict.get("SHIFT_LEFT"))
        self.shift_right = int(tradeGraphDict.get("SHIFT_RIGHT"))
        self.shift_bottom = int(tradeGraphDict.get("SHIFT_BOTTOM"))
        self.shift_top = int(tradeGraphDict.get("SHIFT_TOP"))
        self.ycordWidth = int(tradeGraphDict.get("YCORD_WIDTH"))
        self.pillarPoint = int(tradeGraphDict.get("PILLAR_POINT"))
        self.pillarGapPoint = int(tradeGraphDict.get("PILLAR_GAP_POINT"))
        self.pillarSumPoint = self.pillarPoint + self.pillarGapPoint
        self.FRAME_COLOR = colorHex(tradeGraphDict.get("FRAME_COLOR"))
        self.GRID_COLOR = colorHex(tradeGraphDict.get("GRID_COLOR"))
        self.CORD_INFO_COLOR = colorHex(tradeGraphDict.get("CORD_INFO_COLOR"))
        self.CROSS_LINE_COLOR = colorHex(tradeGraphDict.get("CROSS_LINE_COLOR"))
        self.TRADE_INFO_FGCOLOR = colorHex(tradeGraphDict.get("TRADE_INFO_FGCOLOR"))

        self.info_tradeNum = SLabel(text="") #交易次數
        self.info_tradeNum.color = self.TRADE_INFO_FGCOLOR 
        self.info_profitPer = SLabel(text="") #獲利率
        self.info_profitPer.color = self.TRADE_INFO_FGCOLOR 

        self.bind(pos=self.charting)
        self.bind(size=self.charting)
        Window.bind(mouse_pos=self.mousePos)
        
    def calcMaxTick(self):
        """
        依據容器的寬度及傳入之數據，計算圖形可畫出之最大及最小的tick值
        """
        
        all_tickNum = (int)((self.width - self.ycordWidth * 2 - self.shift_left - self.shift_right) / self.pillarSumPoint)
        half_tickNum = (int)((all_tickNum - 1) / 2)
        all_tickNum = half_tickNum * 2
        self.min_tickNum = half_tickNum * -1
        self.max_tickNum = half_tickNum
        
        if self.min_profitPer < self.min_tickNum and self.max_profitPer < self.max_tickNum:
            diff = self.max_profitPer - self.min_profitPer
            if diff >= all_tickNum: 
                self.max_tickNum = self.max_profitPer
                self.min_tickNum = (half_tickNum * 2 - self.max_tickNum) * -1
            else:
                shift_num = self.min_tickNum - self.min_profitPer
                self.max_tickNum = self.max_tickNum - shift_num
                self.min_tickNum = self.min_tickNum - shift_num
        elif self.min_profitPer > self.min_tickNum and self.max_profitPer > self.max_tickNum:
            diff = self.max_profitPer - self.min_profitPer
            if diff >= all_tickNum: 
                self.min_tickNum = self.min_profitPer
                self.max_tickNum = half_tickNum * 2 + self.min_profitPer
            else:
                shift_num = self.max_profitPer - self.max_tickNum
                self.max_tickNum = self.max_tickNum + shift_num
                self.min_tickNum = self.min_tickNum + shift_num

        self.max_tickNum = int(self.max_tickNum)
        self.min_tickNum = int(self.min_tickNum)

    def drawNoDataGraph(self):
        """
        繪製一個沒有數據之圖形
        """
        self.calcMaxTick()
        self.drawCordFrame()
        self.yscale = (self.height - self.shift_bottom - self.shift_top) / self.maxNum
        self.drawCordInfo()
        
    def charting(self, *args):
        """
        繪圖
        """
        self.canvas.clear()

        if self.dataList == None or len(self.dataList) == 0:
            self.drawNoDataGraph()
            return

        self.calcMaxTick()
        self.drawCordFrame()
        
        self.profitPerNumDict.clear()
        self.maxNum = 5
        tmpProfitPer = None
        aNum = None
        for profitPer in self.dataList:
            if profitPer < 0:
                tmpProfitPer = math.floor(profitPer)
                if tmpProfitPer < self.min_tickNum:
                    tmpProfitPer = self.min_tickNum
            else:
                tmpProfitPer = math.ceil(profitPer)
                if tmpProfitPer > self.max_tickNum:
                    tmpProfitPer = self.max_tickNum
                
            tmpProfitPer = int(tmpProfitPer)
            aNum = self.profitPerNumDict.get(str(tmpProfitPer))
            if aNum == None:
                aNum = 0
            aNum += 1
            self.profitPerNumDict[str(tmpProfitPer)] = aNum
            if aNum > self.maxNum:
                self.maxNum = aNum

        self.yscale = (self.height - self.shift_bottom - self.shift_top) / self.maxNum
        
        self.drawCordInfo()
        
        index = None
        shift_xpos = None
        center_pos = int(self.pillarPoint / 2)
        for i in range(self.min_tickNum, self.max_tickNum + 1):
            if i == 0:
                shift_xpos = self.ycordWidth
            elif i > 0:
                shift_xpos = self.ycordWidth * 2
            else:
                shift_xpos = 0
            index = i - self.min_tickNum
            aNum = self.profitPerNumDict.get(str(i))
            if aNum != None:
                lineColor = Color()
                lineColor.rgba = self.GRID_COLOR                
                
                instg = InstructionGroup(group="data")
                instg.add(lineColor)
                
                x1 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + shift_xpos)
                y1 = int(self.pos[1] + self.shift_bottom)
                x2 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + shift_xpos)
                y2 = int(self.pos[1] + self.shift_bottom + aNum * self.yscale)
                instg.add(Line(points=(x1, y1, x2, y2), width=1))
                self.canvas.add(instg)
                
                instg = InstructionGroup(group="data")
                instg.add(lineColor)
                
                x1 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + shift_xpos)
                y1 = int(self.pos[1] + self.shift_bottom + aNum * self.yscale)
                x2 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + self.pillarPoint - 1 + shift_xpos)
                y2 = int(self.pos[1] + self.shift_bottom + aNum * self.yscale)
                instg.add(Line(points=(x1, y1, x2, y2), width=1))
                self.canvas.add(instg)
                
                instg = InstructionGroup(group="data")
                instg.add(lineColor)
                
                x1 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + self.pillarPoint - 1 + shift_xpos)
                y1 = int(self.pos[1] + self.shift_bottom)
                x2 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + self.pillarPoint - 1 + shift_xpos)
                y2 = int(self.pos[1] + self.shift_bottom + aNum * self.yscale)
                instg.add(Line(points=(x1, y1, x2, y2), width=1))
                self.canvas.add(instg)

            x1 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + shift_xpos + center_pos)
            self.xcordDict[str(i)] = x1
    def drawCordFrame(self):
        
        # 畫一條橫線
        instg = InstructionGroup(group="frame")
        frameColor = Color()
        frameColor.rgba = self.FRAME_COLOR
        instg.add(frameColor)
        x1 = int(self.pos[0] + self.shift_left)
        y1 = int(self.pos[1] + self.shift_bottom)
        x2 = int(self.pos[0] + self.width - self.shift_right)
        y2 = int(self.pos[1] + self.shift_bottom)
        instg.add(Line(points=(x1, y1, x2, y2), width=1))        
        self.canvas.add(instg)
        
        # 畫一條豎線
        instg = InstructionGroup(group="frame")
        instg.add(frameColor)
        center_pos = int(self.pillarPoint / 2)
        self.center_xpos = int(self.pos[0] + self.shift_left + (self.min_tickNum * -1) * self.pillarSumPoint + self.ycordWidth + center_pos)
        x1 = self.center_xpos
        y1 = int(self.pos[1] + self.shift_bottom)
        x2 = self.center_xpos
        y2 = int(self.pos[1] + self.height - self.shift_top)
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)

    def drawCordInfo(self):
        
        # 100-Start: 標示y軸資訊 
        
        initStepUp = 1
        if self.maxNum < 8:
            initStepUp = 1
        elif self.maxNum < 10:
            initStepUp = 2
        else:
            initStepUp = int(self.maxNum / 5)
        
        x0 = self.pos[0] + ((self.width - self.shift_left - self.shift_right) / 2) + self.shift_left - 30
        y0 = self.pos[1] + self.height - self.shift_top + 5           
        alabel = SCordLabel(pos=(x0,y0),size_hint=(None,None))
        alabel.width = 60
        alabel.height = 20        
        alabel.text = "(X軸:獲利率,Y軸:交易次數)"
        alabel.color = self.CORD_INFO_COLOR
        self.add_widget(alabel)
            
        frameColor = Color()
        frameColor.rgba = self.FRAME_COLOR
        stepUp = initStepUp
        while(stepUp <= self.maxNum):
            instg = InstructionGroup(group="frame")            
            instg.add(frameColor)            
            x1 = self.center_xpos - 5
            y1 = int(self.pos[1] + self.shift_bottom + stepUp * self.yscale)
            x2 = self.center_xpos
            y2 = int(self.pos[1] + self.shift_bottom + stepUp * self.yscale)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))        
            self.canvas.add(instg)
            
            x0 = self.center_xpos - self.ycordWidth
            y0 = int(self.pos[1] + self.shift_bottom + stepUp * self.yscale) - 10
            alabel = SCordLabel(pos=(x0,y0),size_hint=(None,None))
            alabel.width = 36
            alabel.height = 20
            alabel.text = str(stepUp)
            alabel.color = self.CORD_INFO_COLOR
            self.add_widget(alabel)
            stepUp += initStepUp
        # 100-End.
        
        # 200-Start: 標示x軸資訊 
        center_pos = int(self.pillarPoint / 2)
        remainder = None
        for i in range(self.min_tickNum, self.max_tickNum + 1):
            remainder = i % 10
            if remainder != 0 and i != -1 and i != 0 and i != 1 and i != self.min_tickNum and i != self.max_tickNum:
                continue
            index = i - self.min_tickNum
            if i >= 0:
                tmp = self.max_tickNum - i
                if tmp <= 8 and i != self.max_tickNum:
                    continue
                if i == 0:
                    shift_xpos = self.ycordWidth
                else:
                    shift_xpos = self.ycordWidth * 2
            else:
                if index <= 8 and i != self.min_tickNum:
                    continue
                shift_xpos = 0            
            instg = InstructionGroup(group="frame")            
            instg.add(frameColor)            
            x1 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + center_pos + shift_xpos)
            y1 = int(self.pos[1] + self.shift_bottom)
            x2 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + center_pos + shift_xpos)
            y2 = int(self.pos[1] + self.shift_bottom - 5)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))        
            self.canvas.add(instg)
            
            x0 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + center_pos + shift_xpos - 18)
            y0 = int(self.pos[1] + self.shift_bottom) - 25
            alabel = SCordLabel(pos=(x0,y0),size_hint=(None,None))
            alabel.width = 36
            alabel.height = 20
            if i == self.min_tickNum:
                alabel.text = "<=" + str(i) + "%"
            elif i == self.max_tickNum:
                alabel.text = ">=" + str(i) + "%"
            else:
                alabel.text = str(i) + "%"
            alabel.color = self.CORD_INFO_COLOR
            self.add_widget(alabel)
        # 200-End.

    def drawCrossLine(self, key):
        if len(self.profitPerNumDict) == 0:
            return
        
        aNum = self.profitPerNumDict.get(key)
        if aNum == None:
            return
        
        keyInt = int(key)
        
        index = keyInt - self.min_tickNum
        if keyInt == 0:
            shift_xpos = self.ycordWidth
        elif keyInt > 0:
            shift_xpos = self.ycordWidth * 2
        else:
            shift_xpos = 0
        
        color = Color()
        color.rgba = self.CROSS_LINE_COLOR

        self.canvas.remove_group("cross_line")
        
        center_pos = int(self.pillarPoint / 2)
        instg = InstructionGroup(group="cross_line")
        instg.add(color)
        x1 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + shift_xpos + center_pos)
        y1 = int(self.pos[1] + self.shift_bottom)
        x2 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + shift_xpos + center_pos)
        y2 = int(self.pos[1] + self.shift_bottom + self.maxNum * self.yscale)
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
                
        instg = InstructionGroup(group="cross_line")
        instg.add(color)
        x1 = self.pos[0] + self.shift_left
        y1 = int(self.pos[1] + self.shift_bottom + aNum * self.yscale)
        x2 = self.pos[0] + self.width - self.shift_right
        y2 = int(self.pos[1] + self.shift_bottom + aNum * self.yscale)
        instg.add(Line(points=(x1, y1, x2, y2), width=1))        
        self.canvas.add(instg)

    def clearCrossLineAndInfo(self):
        self.canvas.remove_group("cross_line")
        if self.infoLayout != None:
            if self.infoLayout.parent != None:
                self.remove_widget(self.infoLayout)   

    def mousePos(self, *args):
        if len(args) >= 2:
            key = None
            xcord = None
            if len(self.profitPerNumDict) != 0 and len(self.xcordDict) != 0:
                for xkey in self.xcordDict.keys():
                    xcord = self.xcordDict.get(xkey)
                    if args[1][0] < (xcord + 0.5) and args[1][0] < (xcord - 0.5):
                        key = int(xkey)
                        break
                if key == None:
                    self.clearCrossLineAndInfo()
                    return
                aNum = self.profitPerNumDict.get(str(key))
                if aNum == None:
                    self.clearCrossLineAndInfo()
                    return
                                
                self.drawCrossLine(str(key))

                if self.infoLayout == None:
                    self.infoLayout = SInfoLayout(cols=1)
                    self.infoLayout.row_force_default = True
                    self.infoLayout.row_default_height = 20
                    self.infoLayout.col_force_default = True
                    self.infoLayout.col_default_width = 110
                    self.infoLayout.padding = [2, 1, 2, 1]
                    self.infoLayout.size_hint = (None, None)
                else:
                    self.infoLayout.clear_widgets()
                if self.infoLayout.parent == None:
                    self.add_widget(self.infoLayout)
                index = key - self.min_tickNum
                center_pos = int(self.pillarPoint / 2)
                if key == 0:
                    shift_xpos = self.ycordWidth
                elif key > 0:
                    shift_xpos = self.ycordWidth * 2
                else:
                    shift_xpos = 0                
                x1 = int(self.pos[0] + self.shift_left + index * self.pillarSumPoint + shift_xpos + center_pos)
                if (self.width - x1) < (self.infoLayout.width + self.shift_right):
                    pos_x = x1 - self.infoLayout.width
                else:
                    pos_x = x1 + 5
                y1 = int(self.pos[1] + self.shift_bottom + aNum * self.yscale) 
                if (self.height - y1) < (self.infoLayout.height + self.shift_top):
                    pos_y = y1 - self.infoLayout.height
                else:
                    pos_y = y1 + 5
                self.infoLayout.pos = (pos_x, pos_y)

                self.info_tradeNum = SLabel(text="") #交易次數
                self.info_tradeNum.color = self.TRADE_INFO_FGCOLOR 
                self.info_profitPer = SLabel(text="") #獲利率
                self.info_profitPer.color = self.TRADE_INFO_FGCOLOR 
                    
                rowNum = 1                    
                self.infoLayout.add_widget(self.info_profitPer)
                self.info_profitPer.text = "獲利率:" + str(key) + "%"
                    
                rowNum += 1
                self.infoLayout.add_widget(self.info_tradeNum)
                self.info_tradeNum.text = "交易次數:" + str(aNum)
                        
                self.infoLayout.size = (110, rowNum * 20)