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
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex as colorHex

import sconsts as CONSTS
import sutil
from sgw_popup import SGwPopup
from selements import SLabel, SButton, STableScrollView, STableGridLayout, SPopup
from soption_element import SOptionElement

with open(os.path.join(os.path.dirname(__file__), "soption_select.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class SOptionSelect(BoxLayout):

    contentLayout_id = ObjectProperty(None)
    ensurebtn_id = ObjectProperty(None)
    resetbtn_id = ObjectProperty(None)
    selectbtn_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    sysConfDict = {}
    optionList = None
    kwargs = {}
    
    def __init__(self, refDict, **kwargs):
        super(SOptionSelect, self).__init__(**kwargs)

        self.app = refDict.get(CONSTS.S_APP)
        self.sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
 
        slview = STableScrollView()
        slview.size_hint = (1, 1)
        self.stgLayout = STableGridLayout(cols=1, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.stgLayout.bind(minimum_height=self.stgLayout.setter('height'))
        slview.add_widget(self.stgLayout)
        
        self.contentLayout_id.add_widget(slview)
        
        self._doQueryFormulaId()

    def _doQueryFormulaId(self):
        refParam = {}
        refParam["CONSTS.S_APP"] = self.app
        refParam["TitleMsg"] = self.sysConfDict.get("MSG_TITLE")
        refParam["InfoMsg"] = "  資料讀取中..."
        refParam["PopupSize"] = (160, 120)
        gwParam = {}
        userConf = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
        useridTxt = self.app.account
        if useridTxt.find("@") != -1:
            useridTxt = "1|" + useridTxt
        else:
            useridTxt = "2|" + useridTxt        
        gwParam["Host"] = userConf.get("DOWNLOAD_URL").strip()
        gwParam["Port"] = int(userConf.get("DOWNLOAD_PORT").strip())
        gwParam["User"] = useridTxt
        gwParam["Password"] = self.app.pwd
        gwParam["ProductId"] = int(userConf.get("PRODUCT_ID").strip())
        gwParam["UserType"] = int(userConf.get("USER_TYPE").strip())
        gwParam["LoginType"] = int(userConf.get("TRADE_LOGIN_TYPE").strip())
        gwParam["CateID"] = 8202000        
        refParam["GwParam"] = gwParam
        refParam["GwFunc"] = abxtoolkit.query_formulaid
        refParam["ResultFunc"] = self._finishedQueryFormulaId 

        sgwPopup = SGwPopup(refParam)
        sgwPopup.processEvent()
        
    def _finishedQueryFormulaId(self, gwResult):
        
        if self.optionList == None:
            self.optionList = []
        else:
            self.optionList.clear()

        formulaList = gwResult.get("FormulaList")

        aOption = None
        for adict in formulaList:
            aOption = SOptionElement({"OptionDict":adict})
            aOption.size_hint = (1, None)
            aOption.height = 32
            self.optionList.append(aOption)
            self.stgLayout.add_widget(aOption)
    
    def setToOptionDefault(self):
        if self.optionList == None:
            return
        for aObj in self.optionList:
            aObj.setToDefaultValue()
    
    def showSelectedOptionDesc(self):
        if self.optionList == None:
            return
        mainContent = BoxLayout(size_hint=(1, 1), orientation="vertical")

        slview = STableScrollView()
        slview.size_hint = (1, None)
        slview.size = (480, 160)
        contentLayout = STableGridLayout(cols=1, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        contentLayout.bind(minimum_height=contentLayout.setter('height'))
        slview.add_widget(contentLayout)
        aLabel = None
        rowIndex = 0
        for aObj in self.optionList:
            if aObj.isSelected() != True:
                continue
            rowIndex += 1
            aStr = str(rowIndex) + ". " + aObj.getOptionDesc()
            aLabel = SLabel(text=aStr,size_hint=(1, None), height=30)
            aLabel.color = colorHex("#000000")
            contentLayout.add_widget(aLabel)      
        showSelectFile_popup = SPopup(title="已選條件", content=mainContent,
                size_hint=(None, None), size=(480, 250), auto_dismiss=False)
        showSelectFile_popup.title_font = CONSTS.FONT_NAME
        mainContent.add_widget(slview)
        closeBtn = SButton(text="關閉")
        closeBtn.bind(on_press=showSelectFile_popup.dismiss)
        mainContent.add_widget(closeBtn)
        showSelectFile_popup.open()
