# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)
import abxtoolkit

abxtoolkit.load_ini(abxtoolkit.ABX_MODE.AP)
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

import threading
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex as colorHex

from selements import SLabel, SHeadLabel, SHeadSortedButton, SPopup, SContentLabel
from selements import STableBoxLayout, STableGridLayout, STableScrollView
from sortinfo import SortInfo
import sutil
import sconsts as CONSTS

class SSelectStock(BoxLayout):
        
    def __init__(self, paramDict, **kwargs):
        super(SSelectStock, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        self.fidList = self.paramDict.get("fidList")

        self.size_hint = (1, 1)
        self.orientation = "vertical"

        self.doSelectStock()

    def doSelectStock(self):
        contentLayout = BoxLayout()
        contentLayout.orientation = "vertical"
        contentLayout.size_hint = (1, 1)
        contentLabel = SLabel(text="  資料讀取中...", size_hint=(1, .8))
        contentLayout.add_widget(contentLabel)
        
        sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        self.result = None
        self.ss_popup = SPopup(title=sysConfDict.get("MSG_TITLE"), content=contentLayout,
                size_hint=(None, None), size=(160, 120), auto_dismiss=False)
        self.ss_popup.title_font = CONSTS.FONT_NAME
        self.ss_popup.bind(on_open=self.ss_open)
        Clock.schedule_once(self.doSelectStockStart)
    
    def doSelectStockStart(self, instance):
        self.ss_popup.open()
        threading.Thread(target=self.toolkitSelectStock).start()
        
    def toolkitSelectStock(self):
        userConf = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
        useridTxt = self.app.account
        if useridTxt.find("@") != -1:
            useridTxt = "1|" + useridTxt
        else:
            useridTxt = "2|" + useridTxt          
        aDict = {}
        aDict["Host"] = userConf.get("DOWNLOAD_URL").strip()
        aDict["Port"] = int(userConf.get("DOWNLOAD_PORT").strip())
        aDict["User"] = useridTxt
        aDict["Password"] = self.app.pwd
        aDict["ProductId"] = int(userConf.get("PRODUCT_ID").strip())
        aDict["UserType"] = int(userConf.get("USER_TYPE").strip())
        aDict["LoginType"] = int(userConf.get("TRADE_LOGIN_TYPE").strip())
        aDict["Source"] = ""
        aDict["StockCount"] = 0
        aDict["Condition"] = self.fidList
        self.result = abxtoolkit.select_stock(aDict)
        
    def doSelectStock_check(self, dt):
        if self.result != None:
            self.ss_popup.dismiss()
            self.event.cancel()            
            errCode = self.result.get("ErrCode")
            if errCode != 0:
                errDesc = self.result.get("ErrDesc")
                self.app.showErrorView(False, errCode, errDesc)
            else:
                self.finishedSelectStock()

    def ss_open(self, instance):
        self.event = Clock.schedule_interval(self.doSelectStock_check, .0005)

    def finishedSelectStock(self):
        
        dataFields = self.result.get("DataFields")
        headNum = len(dataFields)
        
        self.currentHeadIndex = 0
        self.sortedDirection = 1
        self.headButtonList = []
        headLayout = STableGridLayout(cols=headNum, rows=1, spacing=2, size_hint=(1, None), height=30)
        headIndex = -1
        for field in dataFields:            
            headIndex += 1
            headButton = SHeadSortedButton(headText = field, headIndex = headIndex, text = field, size_hint = (1.0 / headNum, 1))
            if headIndex == 0:
                headButton.text = field + " ▼"
            headButton.bind(on_release=self.sortedData)
            headLayout.add_widget(headButton)
            self.headButtonList.append(headButton)
        self.add_widget(headLayout)
        
        gapLayout = STableBoxLayout(size_hint=(1, None), height=2)
        self.add_widget(gapLayout)

        slview = STableScrollView()
        slview.size_hint = (1, .9)
        self.contentLayout = STableGridLayout(cols=headNum, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.contentLayout.bind(minimum_height=self.contentLayout.setter('height'))
        
        stockData = self.result.get("StockData")
        self.currStockDataList = stockData.split(";")
        self.addStockData()

        slview.add_widget(self.contentLayout)
        
        self.add_widget(slview)

    def addStockData(self):
        self.contentLayout.clear_widgets()
        dataFields = self.result.get("DataFields")
        headNum = len(dataFields)       
        for aData in self.currStockDataList:
            if aData == "":
                continue
            aFieldList = aData.split("|")
            num = -1
            for aField in aFieldList:
                if aField == "":
                    continue
                num += 1
                contentLabel = SContentLabel(size_hint=(1.0 / headNum, None), height=30)
                contentLabel.color = colorHex("#000000")
                if dataFields[num] == "ID" or dataFields[num] == "NAME":
                    contentLabel.text = aField
                    contentLabel.halign = "center"
                else:
                    contentLabel.text = "{:.2f}".format(float(aField))
                    contentLabel.halign = "right"
                contentLabel.valign = "middle"
                self.contentLayout.add_widget(contentLabel)

    def sortedData(self, instance):
        if instance.headIndex == self.currentHeadIndex:
            if self.sortedDirection == 1:
                self.sortedDirection = -1
                aBtn = self.headButtonList[self.currentHeadIndex]
                aBtn.text = aBtn.headText + " ▲"
            else:
                self.sortedDirection = 1
                aBtn = self.headButtonList[self.currentHeadIndex]
                aBtn.text = aBtn.headText + " ▼"                
            self.currStockDataList.reverse()
        else:
            aBtn = self.headButtonList[self.currentHeadIndex]
            aBtn.text = aBtn.headText            
            self.currentHeadIndex = instance.headIndex
            aBtn = self.headButtonList[self.currentHeadIndex]
            aBtn.text = aBtn.headText + " ▼"            
            self.sortedDirection = 1
            dataFields = self.result.get("DataFields")
            headNum = len(dataFields)              
            stockData = self.result.get("StockData")
            stockDataList = stockData.split(";")
            sortinfoList = []
            dataDict = {}
            for aData in stockDataList:
                if aData == "":
                    continue
                aFieldList = aData.split("|")
                stkId = ""
                num = -1
                for aField in aFieldList:
                    if aField == "":
                        continue
                    num += 1                   
                    if dataFields[num] == "ID":
                        stkId = aField
                        break
                aHeader = dataFields[self.currentHeadIndex]
                aValue = aFieldList[self.currentHeadIndex]
                if aHeader == "ID" or aHeader == "NAME":
                    sortinfoList.append(SortInfo(stkId, aValue))
                else:
                    sortinfoList.append(SortInfo(stkId, float(aValue)))
                dataDict[stkId] = aData
            sortList = sorted(sortinfoList)
            self.currStockDataList.clear()
            for aObj in sortList:
                self.currStockDataList.append(dataDict.get(aObj.pKey))
        self.addStockData()
                        
            
            
            