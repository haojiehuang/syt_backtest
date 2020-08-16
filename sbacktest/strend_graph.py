# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sstkchart" + os.sep))


from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Point, Line, Color, Rectangle, InstructionGroup
from kivy.utils import get_color_from_hex as colorHex
import sconsts as CONSTS
import sutil
from schartutil import SMinTimeCordUtil
import math
from kivy.core.text import Label as CoreLabel
from selements import SLabel, SCordLabel, SInfoLayout

class STrendGraph(FloatLayout):
    
    isFocus = True
    infoLayout = None
    rectGridList = None
    
    def __init__(self, paramDict, **kwargs):
        super(STrendGraph, self).__init__(**kwargs)
        
        with self.canvas:
            Color(0, 20/255, 45/255)
            Rectangle(pos=self.pos, size=self.size)
            
        self.paramDict = paramDict
        self.btmenu = self.paramDict.get(CONSTS.S_BTMENU)
        self.tickNum = self.paramDict.get("ticknum")
        self.dataList = self.paramDict.get("datalist")
        if self.tickNum == 600:
            self.xgrid_num = 100
        elif self.tickNum == 500:
            self.xgrid_num = 90
        elif self.tickNum == 400:
            self.xgrid_num = 70
        elif self.tickNum == 300:
            self.xgrid_num = 50
        elif self.tickNum == 200:
            self.xgrid_num = 40
        else:
            self.xgrid_num = 30

        self.crossLineXIndex = -1
        self.crossLineYIndex = -1

        trendGraphDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "trend_graph.ini"))
        self.shift_left = int(trendGraphDict.get("SHIFT_LEFT"))
        self.shift_right = int(trendGraphDict.get("SHIFT_RIGHT"))
        self.shift_bottom = int(trendGraphDict.get("SHIFT_BOTTOM"))
        self.shift_top = int(trendGraphDict.get("SHIFT_TOP"))
        self.CORD_INFO_COLOR = colorHex(trendGraphDict.get("CORD_INFO_COLOR"))
        self.UP_COLOR = colorHex(trendGraphDict.get("UP_COLOR"))
        self.DOWN_COLOR = colorHex(trendGraphDict.get("DOWN_COLOR"))
        self.EQUAL_COLOR = colorHex(trendGraphDict.get("EQUAL_COLOR"))
        self.VOLUME_COLOR = colorHex(trendGraphDict.get("VOLUME_COLOR"))
        self.FRAME_COLOR = colorHex(trendGraphDict.get("FRAME_COLOR"))
        self.GRID_COLOR = colorHex(trendGraphDict.get("GRID_COLOR"))
        self.CROSS_LINE_COLOR = colorHex(trendGraphDict.get("CROSS_LINE_COLOR"))
        self.TRADEB_SIG_COLOR = colorHex(trendGraphDict.get("TRADEB_SIG_COLOR"))
        self.TRADES_SIG_COLOR = colorHex(trendGraphDict.get("TRADES_SIG_COLOR"))
        self.TRADE_INFO_FGCOLOR = colorHex(trendGraphDict.get("TRADE_INFO_FGCOLOR"))

        self.info_date = SLabel(text="")#日期
        self.info_date.color = self.TRADE_INFO_FGCOLOR 
        self.info_time = SLabel(text="")#時間
        self.info_time.color = self.TRADE_INFO_FGCOLOR 
        self.info_price = SLabel(text="")#成交價
        self.info_price.color = self.TRADE_INFO_FGCOLOR 
        self.info_vol = SLabel(text="")#成交量
        self.info_vol.color = self.TRADE_INFO_FGCOLOR 
        self.info_amt = SLabel(text="")#金額
        self.info_amt.color = self.TRADE_INFO_FGCOLOR 
        self.info_bs = SLabel(text="")#買賣訊號及買(賣)價
        self.info_bs.color = self.TRADE_INFO_FGCOLOR 
        
        self.calcMaxTick()

        self.bind(pos=self.charting)
        self.bind(size=self.charting)
        Window.bind(mouse_pos=self.mousePos)
        
    def calcMaxTick(self):
        self.max_tickNum = 0
        if self.dataList == None:
            self.max_tickNum = self.tickNum
        elif self.tickNum > len(self.dataList):
            self.max_tickNum = self.tickNum
        else:
            self.max_tickNum = len(self.dataList)        
        
    def charting(self, *args):
        self.canvas.clear()

        if self.dataList == None or len(self.dataList) == 0:
            return

        self.max_price_s = -1
        self.min_price_s = sys.maxsize
        self.max_volume = 0
        
        for data in self.dataList:
            price = data.get("price")
            if price > self.max_price_s:
                self.max_price_s = price
            if price < self.min_price_s:
                self.min_price_s = price
            vol = data.get("vol")
            if vol > self.max_volume:
                self.max_volume = vol
        
        diffMaxMin = (self.max_price_s - self.min_price_s) / 100.0
        self.max_price = self.max_price_s + diffMaxMin * 6
        self.min_price = self.min_price_s - diffMaxMin * 14
        self.xscale = 1.0 * (self.width - self.shift_left - self.shift_right) / self.max_tickNum
        self.yscale = 1.0 * (self.height - self.shift_bottom - self.shift_top) / (self.max_price - self.min_price)
        self.vscale = self.yscale * (self.min_price_s - self.min_price) * .8 / self.max_volume

        self.drawFrameGrid()
        
        curIndex = preIndex = -1
        prePrice = 0
        
        x1 = 0
        y1 = 0
        x2 = 0
        y2 = 0

        for data in self.dataList:
            curIndex += 1
            if curIndex == 0:
                self.drawXCoordinateInfo(0)
                preIndex = curIndex
                prePrice = data.get("price")
                self.drawVolumeGraph(data, 0)
                self.addBSPoint(0)
                continue
            
            instg = InstructionGroup(group="data")
            curPrice = data.get("price")
            color = self.getLineColor(prePrice, curPrice)
            instg.add(color)
            
            x1 = int(self.pos[0] + self.shift_left + preIndex * self.xscale)
            y1 = int(self.pos[1] + self.shift_bottom + (prePrice - self.min_price) * self.yscale)
            x2 = int(self.pos[0] + self.shift_left + curIndex * self.xscale)
            y2 = int(self.pos[1] + self.shift_bottom + (curPrice - self.min_price) * self.yscale)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))
            self.canvas.add(instg)
            
            self.drawVolumeGraph(data, curIndex)

            if (curIndex % self.xgrid_num) == 0:
                self.drawXCoordinateInfo(curIndex)
                
            self.addBSPoint(curIndex)
            
            preIndex = curIndex
            prePrice = curPrice
        
        self.drawCrossLine(curIndex)

    def drawVolumeGraph(self, data, curIndex):
        instg = InstructionGroup(group="data")
        volume = data.get("vol")
        color = Color()
        color.rgba = self.VOLUME_COLOR
        instg.add(color)
        
        x1 = int(self.pos[0] + self.shift_left + curIndex * self.xscale)
        y1 = int(self.pos[1] + self.shift_bottom)
        x2 = int(self.pos[0] + self.shift_left + curIndex * self.xscale)
        y2 = int(self.pos[1] + self.shift_bottom + volume * self.vscale)
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
    
    def addBSPoint(self, index):
        data = self.dataList[index]
        bstype = data.get("bs")
        if bstype != "":
            price = data.get("price")
            x1 = int(self.pos[0] + self.shift_left + index * self.xscale) - 5
            alabel = Label(text="",size_hint=(None,None),size=(5,10),markup=True)  
            if bstype == "B":
                y1 = int(self.pos[1] + self.shift_bottom + (price - self.min_price) * self.yscale) - 20
                alabel.pos = (x1, y1)
                alabel.color = self.TRADEB_SIG_COLOR
                alabel.text = "[b]" + "B" + "[/b]"
            elif bstype == "S":
                y1 = int(self.pos[1] + self.shift_bottom + (price - self.min_price) * self.yscale) + 10
                alabel.pos = (x1, y1)                
                alabel.color = self.TRADES_SIG_COLOR
                alabel.text = "[b]" + "S" + "[/b]"
            self.add_widget(alabel)
    
    def drawXCoordinateInfo(self, index):
        
        x0 = int(self.pos[0] + self.shift_left + index * self.xscale - 30)
        y0 = int(self.pos[1] + self.shift_bottom - 20)
        dateStr = self.dataList[index].get("date")              
        alabel = SCordLabel(pos=(x0,y0),size_hint=(None,None))
        alabel.width = 60
        alabel.height = 20        
        alabel.text = sutil.formatDate(dateStr)
        alabel.color = self.CORD_INFO_COLOR
        self.add_widget(alabel)
        
        timeStr = self.dataList[index].get("time")
        if timeStr != "0":
            x0 = int(self.pos[0] + self.shift_left + index * self.xscale - 30)
            y0 = int(self.pos[1] + self.shift_bottom - 40)            
            alabel = SCordLabel(pos=(x0,y0),size_hint=(None,None))
            alabel.width = 60
            alabel.height = 20
            alabel.text = sutil.formatTime(timeStr)
            alabel.color = self.CORD_INFO_COLOR
            self.add_widget(alabel)   
        
    def drawFrameGrid(self):
        
        # Start-01: 產生一繪製外框,線條及座標之物件
        rectParamDict = {}
        rectParamDict["canvas"] = self.canvas
        rectParamDict["width"] = self.width - self.shift_left - self.shift_right
        rectParamDict["height"] = self.height - self.shift_bottom - self.shift_top
        rectParamDict["x_start_pos"] = self.pos[0] + self.shift_left
        rectParamDict["y_start_pos"] = self.pos[1] + self.shift_bottom
        rectParamDict["rectColor"] = self.FRAME_COLOR
        rectParamDict["rectWidth"] = 1
        rectParamDict["gridColor"] = self.GRID_COLOR
        rectParamDict["gridWidth"] = 1        
        rectParamDict["instGroup"] = "StrendGraph"
        smintimeChartUtil = SMinTimeCordUtil(rectParamDict)     
        # End-01.

        smintimeChartUtil.drawRectGrid() #繪製一矩形框  

        gridColor = Color()
        gridColor.rgba = self.GRID_COLOR        
        tmpNum = self.xgrid_num
        while (tmpNum < self.max_tickNum):
            instg = InstructionGroup(group="grid")
            x1 = int(self.pos[0] + self.shift_left + tmpNum * self.xscale)
            y1 = self.pos[1] + self.shift_bottom
            x2 = int(self.pos[0] + self.shift_left + tmpNum * self.xscale)
            y2 = self.pos[1] + self.height - self.shift_top
            instg.add(gridColor)
            instg.add(Line(points=(x1, y1, x2, y2), width=1))
            self.canvas.add(instg)
            tmpNum += self.xgrid_num
        
        pscale = (self.max_price - self.min_price) / 4.0
        for i in range(0, 5):
            y1 = int(self.pos[1] + self.shift_bottom + (i * pscale * self.yscale))
            y2 = int(self.pos[1] + self.shift_bottom + (i * pscale * self.yscale))
            if i != 0 and i != 4:
                instg = InstructionGroup(group="grid")
                x1 = self.pos[0] + self.shift_left
                x2 = self.pos[0] + self.width - self.shift_right 
                instg.add(gridColor)
                instg.add(Line(points=(x1, y1, x2, y2), width=1))
                self.canvas.add(instg)

            cordPrice = i * pscale + self.min_price
            cordPriceStr = "{:7.2f}".format(cordPrice)
            x0 = self.pos[0] + 2
            #y0 = y1 - 8
            y0 = y1
            alabel = SCordLabel(text=cordPriceStr,pos=(x0,y0),size_hint=(None,None))
            alabel.width = self.shift_left - 2
            alabel.height = 16
            alabel.halign = "right"
            alabel.color = self.CORD_INFO_COLOR
            self.add_widget(alabel)
        
        smintimeChartUtil = None
        
    def getLineColor(self, price1, price2):
        color = Color()
        
        if price1 > price2:            
            color.rgba = self.DOWN_COLOR
        elif price1 < price2:
            color.rgba = self.UP_COLOR
        else:
            color.rgba = self.EQUAL_COLOR
        return color

    def drawCrossLine(self, index):
        if self.dataList == None or index >= len(self.dataList):
            return
        
        data = self.dataList[index]
        
        price = data.get("price")
        
        color = Color()
        color.rgba = self.CROSS_LINE_COLOR

        self.canvas.remove_group("cross_line")
        
        instg = InstructionGroup(group="cross_line")
        instg.add(color)
        x1 = int(self.pos[0] + self.shift_left + index * self.xscale)
        y1 = self.pos[1] + self.shift_bottom
        x2 = int(self.pos[0] + self.shift_left + index * self.xscale)
        y2 = self.pos[1] + self.height - self.shift_top      
        instg.add(Line(points=(x1, y1, x2, y2), width=1))
        self.canvas.add(instg)
                
        instg = InstructionGroup(group="cross_line")
        instg.add(color)
        x1 = self.pos[0] + self.shift_left
        y1 = int(self.pos[1] + self.shift_bottom + (price - self.min_price) * self.yscale)
        x2 = self.pos[0] + self.width - self.shift_right
        y2 = int(self.pos[1] + self.shift_bottom + (price - self.min_price) * self.yscale)
        instg.add(Line(points=(x1, y1, x2, y2), width=1))        
        self.canvas.add(instg)
        
    def mousePos(self, *args):
        if len(args) >= 2:
            if self.dataList != None and len(self.dataList) != 0:  
                index = int((args[1][0] - self.pos[0] - self.shift_left) / self.xscale)
                if index < len(self.dataList) and index >= 0:
                    data = self.dataList[index]
                    dateStr = str(data.get("date"))
                    timeStr = str(data.get("time"))
                    price = data.get("price")                    
                    self.drawCrossLine(index)

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
                    x1 = int(self.pos[0] + self.shift_left + index * self.xscale)
                    if (self.width - x1) < (self.infoLayout.width + self.shift_right):
                        pos_x = x1 - self.infoLayout.width
                    else:
                        pos_x = x1 + 5
                    y1 = int(self.pos[1] + self.shift_bottom + (price - self.min_price) * self.yscale)
                    if (self.height - y1) < (self.infoLayout.height + self.shift_top):
                        pos_y = y1 - self.infoLayout.height
                    else:
                        pos_y = y1 + 5
                    self.infoLayout.pos = (pos_x, pos_y)
                    
                    rowNum = 1                    
                    self.infoLayout.add_widget(self.info_date)
                    self.info_date.text = sutil.formatDate(dateStr)
                    
                    if timeStr != "" and timeStr != "0":
                        rowNum += 1
                        self.infoLayout.add_widget(self.info_time)
                        self.info_time.text = sutil.formatTime(timeStr)
                    
                    rowNum += 1    
                    self.infoLayout.add_widget(self.info_price)
                    self.info_price.text = "價:" + ("{:7.2f}".format(price)).strip()
                    
                    rowNum += 1
                    self.infoLayout.add_widget(self.info_vol)
                    self.info_vol.text = "量:" + ("{:13.0f}".format(data.get("vol"))).strip()
                    
                    rowNum += 1
                    self.infoLayout.add_widget(self.info_amt)
                    self.info_amt.text = "金:" + ("{:13.0f}".format(data.get("amt"))).strip()

                    bs = data.get("bs")
                    bsprice = data.get("bsprice")                    
                    if bs != "":
                        rowNum += 1
                        self.infoLayout.add_widget(self.info_bs)
                        self.info_bs.text = bs + ":" + ("{:7.2f}".format(bsprice)).strip()
                        
                    self.infoLayout.size = (110, rowNum * 20)
                else:
                    self.canvas.remove_group("cross_line")
                    if self.infoLayout != None:
                        if self.infoLayout.parent != None:
                            self.remove_widget(self.infoLayout)