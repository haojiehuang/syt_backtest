# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

import sconsts as CONSTS
import sutil
from selements import SLabel, SButton
from sbt_graph import SbtGraph

with open(os.path.join(os.path.dirname(__file__), "sbacktest.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class SBacktest(FloatLayout):
    
    body_layout = ObjectProperty(None)
    dataList = None
    kwargs = {}
    
    def __init__(self, paramDict, **kwargs):
        super(SBacktest, self).__init__(**kwargs)

        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        fileDir = self.paramDict.get("fileDir")
        self.fileList = self.paramDict.get("fileList")
        self.loadFile(fileDir, self.fileList)

    def loadFile(self, fileDir, fileList):
        
        lineList = []
        errNo = "0"
        for afile in fileList:
            try:
                with open(os.path.join(fileDir, afile), encoding = "utf-8-sig") as f:
                    tmpList = f.readlines()
                    lineList.extend(tmpList)
            except IOError:
                errNo = CONSTS.ERR_IO_EXCEPTION
            except UnicodeDecodeError:
                errNo = CONSTS.ERR_DECODE_ERROR
        
        if errNo != "0":
            self.app.showMsgView(errNo)
        
        if errNo == "0":
            self.analyze(lineList)

    def showErrMsg(self, errList):
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "err_explain.ini")
        with open(filePath, 'r', encoding = 'utf-8-sig') as f:
            lineList = f.readlines()
        explainStr = ""
        for astr in lineList:
            explainStr += astr
        explainStr += "\n\n"
        for astr in errList:
            explainStr += astr + "\n"
        
        contentLayout = BoxLayout(size_hint=(1, 1), orientation="vertical")
        slview = ScrollView(size_hint=(1, .92))
        contentLayout.add_widget(slview)
        explainLayout = BoxLayout(size_hint=(1, None))
        explainLayout.bind(minimum_height=explainLayout.setter('height'))
        explainLabel = SLabel(text=explainStr, size_hint=(1, None))
        explainLabel.halign = "center"
        explainLabel.font_name = CONSTS.FONT_NAME
        explainLayout.add_widget(explainLabel)
        slview.add_widget(explainLayout)
        
        bottomLayout = BoxLayout(size_hint=(1, .08))
        closebtn_id = SButton(text="關閉", size_hint=(1, .8))
        bottomLayout.add_widget(closebtn_id)
        contentLayout.add_widget(bottomLayout)

        popup = Popup(title="錯誤格式說明", content=contentLayout, size_hint=(None, None),
                    size=(680, 400), auto_dismiss=False)
        closebtn_id.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()
            
    def analyze(self, lineList):
        if len(lineList) == 0:
            self.app.showMsgView(CONSTS.ERR_NO_DATA)
            return

        index = None
        tmpStr = None
        aList = None
        listLen = None
        aDict = None

        self.dataList = []
        tmpPrice = 0
        tmpVol = 0
        tmpAmt = 0
        lineNum = 0
        errNum = 0 #錯誤筆數
        errList = [] #有錯誤的行數

        for aStr in lineList:
            tmpStr = aStr.strip()
            lineNum += 1
            if tmpStr == "":
                continue
            index = tmpStr.rfind(",")
            if index != -1 and index == (len(tmpStr) - 1):
                tmpStr = tmpStr[0:index]
            aList = tmpStr.split(",")
            listLen = len(aList)
            if listLen < 10 or listLen > 13:
                errNum += 1
                if listLen < 10:
                    errStr = tmpStr + "-->第" + str(lineNum) + "行，欄位數小於10"
                    errList.append(errStr)
                else:
                    errStr = tmpStr + "-->第" + str(lineNum) + "行，欄位數大於13"
                    errList.append(errStr)
                if errNum > 20:
                    break
                else:
                    continue
            try:
                tmpValue = int(aList[0].strip())
                tmpValue = int(aList[1].strip())
                tmpValue = float(aList[2].strip())
                tmpValue = float(aList[3].strip())
                tmpValue = float(aList[4].strip())
                tmpValue = float(aList[5].strip())
                tmpValue = int(aList[6].strip())
                tmpValue = float(aList[7].strip())
                tmpValue = float(aList[8].strip())
                tmpValue = float(aList[9].strip())
                if listLen == 11:
                    tmpbs = aList[10].strip() #買(賣)訊號
                    if tmpbs != "B" and tmpbs != "S":
                        errNum += 1
                        errStr = tmpStr + "-->第" + str(lineNum) + "行，買(賣)訊號錯誤"
                        errList.append(errStr)
                        continue
            except ValueError:
                errNum += 1
                errStr = tmpStr + "-->第" + str(lineNum) + "行，數值資料中有非數字"
                errList.append(errStr)
                continue

            aDict = {}
            aDict['date'] = aList[0].strip() #日期
            aDict['time'] = aList[1].strip() #時間
            tmpPrice = float(aList[2].strip()) #成交價
            #aList[3] #開
            #aList[4] #高
            #aList[5] #低
            aDict['price'] = tmpPrice
            tmpVol = int(aList[6].strip()) #成交量
            aDict['vol'] = tmpVol
            tmpAmt = float(aList[7].strip()) #金額
            aDict['amt'] = tmpAmt
            #aList[8] #委買價
            #aList[9] #委賣價
            tmpbs = '' #買(賣)訊號
            tmpbsprice = 0.0 #買(賣)價
            tmpbsqty = 0 #買(賣)進量
            if listLen == 10:
                tmpbs = ''
                tmpbsprice = 0.0
                tmpbsqty = 1
            elif listLen == 11:
                tmpbs = aList[10].strip() #買(賣)訊號
                tmpbsprice = tmpPrice
                tmpbsqty = 1
            elif listLen == 12:
                tmpbs = aList[10].strip() #買(賣)訊號
                tmpbsprice = float(aList[11].strip()) #買(賣)價
                tmpbsqty = 1
            elif listLen == 13:
                tmpbs = aList[10].strip() #買(賣P訊號
                tmpbsprice = float(aList[11].strip()) #買(賣)價
                tmpbsqty = int(aList[12].strip()) #買(賣)進量

            aDict['bs'] = tmpbs
            aDict['bsprice'] = tmpbsprice
            aDict['bsqty'] = tmpbsqty

            self.dataList.append(aDict)

        if errNum != 0:
            self.showErrMsg(errList)
            return

        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict.get(key)
        refDict["datalist"] = self.dataList
        refDict["fileList"] = self.fileList

        if self.body_layout.parent != None:
            self.remove_widget(self.body_layout)
        self.body_layout = SbtGraph(refDict)
        self.body_layout.size_hint = (1, 1)
        self.body_layout.pos_hint = {'x':0, 'y':0}
        self.add_widget(self.body_layout)