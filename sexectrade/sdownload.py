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
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex as colorHex

import sutil
import sdate_utils
import sconsts as CONSTS
from sgw_popup import SGwPopup
from selements import SButton, SLabel, STextInput, SPopup
from selements import STableBoxLayout, STableScrollView
from sdatepicker import SDatePicker

import json

download_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." + os.sep + "rowdata"))

with open(os.path.join(os.path.dirname(__file__), "sdownload.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class SAccountIDDropDown(DropDown):
    pass

class DatatypeDropDown(DropDown):
    pass

class SDownload(BoxLayout):
    
    account_id = ObjectProperty(None)
    stock_id = ObjectProperty(None)
    datatypebtn_id = ObjectProperty(None)
    startdate_id = ObjectProperty(None)
    totaldays_id = ObjectProperty(None)
    datestr_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    dataType = "m"
    userConf = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
    
    def datatypeSelect(self, instance, atext):
        self.datatypebtn_id.text = atext
        if atext == "月線":
            self.totaldays_id.text = "全部"
            self.totaldays_id.disabled = False
            self.datestr_id.text = "月"
            self.dataType = "m"
        elif atext == "週線":
            self.totaldays_id.text = "全部"
            self.totaldays_id.disabled = False
            self.datestr_id.text = "週"
            self.dataType = "w"
        elif atext == "日線":
            self.totaldays_id.text = "90"
            self.totaldays_id.disabled = False
            self.datestr_id.text = "天"
            self.dataType = "d"
        elif atext == "tick線":
            self.totaldays_id.text = "1"
            self.totaldays_id.disabled = True
            self.datestr_id.text = "天"
            self.dataType = "0"
        else:
            self.totaldays_id.text = "5"
            self.totaldays_id.disabled = False
            self.datestr_id.text = "天"
            index = atext.find("分線")
            self.dataType = atext[0:index]
        
    def __init__(self, paramDict, **kwargs):
        super(SDownload, self).__init__(**kwargs)
    
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)

        self.datatype_dropdown = DatatypeDropDown()
        self.datatypebtn_id.bind(on_release=self.datatype_dropdown.open)
        self.datatype_dropdown.bind(on_select=self.datatypeSelect)
        
        self.accountIDDropDown = SAccountIDDropDown()
        firstRecord = True
        accountIdList = self.app.accountIdList
        for astr in accountIdList:
            if firstRecord == True:
                firstRecord = False
                self.account_id.text = astr
            abtn = SButton(text=astr)
            abtn.size_hint_y = None
            abtn.height = 30
            abtn.bind(on_release=self.accountIDDropDown.select)
            self.accountIDDropDown.add_widget(abtn)
            
        self.account_id.bind(on_release=self.accountIDDropDown.open)
        self.accountIDDropDown.bind(on_select=self.accountSelect)        
        
        self.startdate_id.bind(focus=self.onFocus)
        
        self.initial_data()
    
    def accountSelect(self, instance, atext):
        self.account_id.text = atext.text
        
    def onFocus(self, instance, value):
        if value:
            content = BoxLayout(size_hint=(1, 1), orientation="vertical")
            self.datePicker = SDatePicker(self.startdate_id.text)
            self.datePicker.size_hint = (1, .8)
            content.add_widget(self.datePicker)
            
            bottomLayout = BoxLayout(size_hint=(1, .1), orientation="horizontal")
            ensurebtn = SButton(text="確定", size_hint=(.49, .8))
            bottomLayout.add_widget(ensurebtn)
            bottomLayout.add_widget(BoxLayout(size_hint=(.02, 1)))
            closebtn = SButton(text="關閉", size_hint=(.49, .8))
            bottomLayout.add_widget(closebtn)
            content.add_widget(bottomLayout)

            self._popup = SPopup(title="日期選擇", content=content, title_font=CONSTS.FONT_NAME,
                            size_hint=(None, None), size=(250, 330), auto_dismiss=False)
            ensurebtn.bind(on_press=self.datePickerEvent)
            closebtn.bind(on_press=self._popup.dismiss)            
            self._popup.open()
    
    def datePickerEvent(self, instance):
        self.startdate_id.text = self.datePicker.date_text
        self._popup.dismiss()
            
    def initial_data(self):
        self.startdate_id.text = str(sdate_utils.getPrevDate(sdate_utils.getCurrentDate()))
        self.totaldays_id.text = "全部"
    
    def downloadData(self):
        useridTxt = self.account_id.text
        if useridTxt == "":
            self.app.showErrorView(True, CONSTS.ERR_USER_IS_SPACE)
            return
        
        stockidTxt = self.stock_id.text
        if stockidTxt == "":
            self.app.showErrorView(True, CONSTS.ERR_STOCKID_IS_SPACE)
            return
        
        if useridTxt.find("@") != -1:
            useridTxt = "1|" + useridTxt
        else:
            useridTxt = "2|" + useridTxt
        
        gwParam = {}
        gwParam["Host"] = self.userConf.get("DOWNLOAD_URL").strip()
        gwParam["Port"] = int(self.userConf.get("DOWNLOAD_PORT").strip())
        gwParam["User"] = useridTxt
        gwParam["Password"] = self.app.pwd
        gwParam["ProductId"] = int(self.userConf.get("PRODUCT_ID").strip())
        gwParam["UserType"] = int(self.userConf.get("USER_TYPE").strip())
        gwParam["LoginType"] = int(self.userConf.get("TRADE_LOGIN_TYPE").strip())
        exchange = "ZZ"
        gwParam["StockFullID"] = exchange + stockidTxt
        gwParam["DataType"] = self.dataType
        startDate = self.startdate_id.text
        if self.dataType == "m" or self.dataType == "w":
            startDate = "0"
        gwParam["StartDate"] = startDate
        totalDaysStr = self.totaldays_id.text
        if totalDaysStr == "全部":
            totalDays = "0"
        else:
            totalDays = totalDaysStr
        if self.dataType != "m" and self.dataType != "w" and self.dataType != "d":
            if int(totalDays) > 5:
                totalDays = "5"
                self.totaldays_id.text = "5"
        gwParam["DataDays"] = totalDays
        
        sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        refParam = {}
        refParam["CONSTS.S_APP"] = self.app
        refParam["TitleMsg"] = sysConfDict.get("MSG_TITLE")
        refParam["InfoMsg"] = "  資料下載中..."
        refParam["PopupSize"] = (160, 120)
        refParam["GwParam"] = gwParam
        refParam["GwFunc"] = abxtoolkit.request_rowdata
        refParam["ResultFunc"] = self._finishedDownload

        sgwPopup = SGwPopup(refParam)
        sgwPopup.processEvent()

    def _finishedDownload(self, gwResult):
        fileName = gwResult.get("FileName")
        fileLen = gwResult.get("FileLen")
        
        content = BoxLayout(size_hint=(1, 1), orientation="vertical")
        content.add_widget(BoxLayout(size_hint=(1, .05)))
        
        fileLayout = GridLayout(cols=2, spacing=2, size_hint=(1, None))
        fileLayout.bind(minimum_height=fileLayout.setter('height'))
        fileLayout.add_widget(SLabel(text="檔案目錄:", size_hint=(.22, None), height=30))
        fileLayout.add_widget(SLabel(text=download_path, size_hint=(.78, None), height=30))
        fileLayout.add_widget(SLabel(text="檔案名稱:", size_hint=(.22, None), height=30))
        fileLayout.add_widget(SLabel(text=fileName, size_hint=(.78, None), height=30))
        fileLayout.add_widget(SLabel(text="檔案長度:", size_hint=(.22, None), height=30))
        fileLayout.add_widget(SLabel(text=str(fileLen), size_hint=(.78, None), height=30))
        content.add_widget(fileLayout)
        
        content.add_widget(BoxLayout(size_hint=(1, .05)))
        
        bottomLayout = BoxLayout(size_hint=(1, .1), orientation="horizontal")
        ensurebtn = SButton(text="確定", size_hint=(1, .8))
        bottomLayout.add_widget(ensurebtn)
        content.add_widget(bottomLayout)

        self.fin_popup = Popup(title="下載完成", content=content, title_font=CONSTS.FONT_NAME,
                        size_hint=(None, None), size=(360, 200), auto_dismiss=False)
        ensurebtn.bind(on_press=self.fin_popup.dismiss)
        self.fin_popup.open()
    
    def showExplain(self):
        filePath = os.path.join(os.path.dirname(__file__), "../conf/explain.ini")
        with open(filePath, 'r', encoding = 'utf-8-sig') as f:
            lineList = f.readlines()
        explainStr = ""
        for astr in lineList:
            explainStr += astr
        
        contentLayout = STableBoxLayout(size_hint=(1, 1), orientation="vertical")
        slview = STableScrollView(size_hint=(1, .92))
        contentLayout.add_widget(slview)
        explainLayout = STableBoxLayout(size_hint=(1, None))
        explainLayout.bind(minimum_height=explainLayout.setter('height'))
        explainLabel = SLabel(text=explainStr, size_hint=(1, None))
        explainLabel.font_name = CONSTS.FONT_NAME
        explainLabel.color = colorHex("#000000")
        explainLayout.add_widget(explainLabel)
        slview.add_widget(explainLayout)
        
        bottomLayout = BoxLayout(size_hint=(1, .08))
        closebtn_id = SButton(text="關閉", size_hint=(1, .8))
        bottomLayout.add_widget(closebtn_id)
        contentLayout.add_widget(bottomLayout)

        popup = SPopup(title="股票代碼說明", content=contentLayout, size_hint=(None, None),
                    size=(500, 400), auto_dismiss=False)
        closebtn_id.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()