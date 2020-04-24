# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex as colorHex

from selements import SButton, SPopup, SFileSelectDialog, SFileInputDialog
import sconsts as CONSTS
import sutil

userConf = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
rowdata_dir = userConf.get("ROWDATA_DIR")
if rowdata_dir == None:
    rowdata_dir = os.path.join(os.path.dirname(__file__), ".." + os.sep + "rowdata")
else:
    if not os.path.exists(os.path.abspath(rowdata_dir)):
        rowdata_dir = os.path.join(os.path.dirname(__file__), ".." + os.sep + "rowdata")
if not os.path.exists(os.path.abspath(rowdata_dir)):
    os.mkdir(os.path.abspath(rowdata_dir))
rowdata_path = os.path.abspath(rowdata_dir)
data_dir = userConf.get("BACKTEST_DIR")
if data_dir == None:
    data_dir = os.path.join(os.path.dirname(__file__), ".." + os.sep + "data")
else:
    if not os.path.exists(os.path.abspath(data_dir)):
        data_dir = os.path.join(os.path.dirname(__file__), ".." + os.sep + "data")
if not os.path.exists(os.path.abspath(data_dir)):
    os.mkdir(os.path.abspath(data_dir))
data_path = os.path.abspath(data_dir)   

with open(os.path.join(os.path.dirname(__file__), "sexectrade.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class SStrategyDropDown(DropDown):
    pass
                        
class SExecTrade(BoxLayout):
    
    rowdata_id = ObjectProperty(None)
    strategy_id = ObjectProperty(None)
    savefile_id = ObjectProperty(None)
    ensurebtn_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    
    def __init__(self, paramDict, **kwargs):
        super(SExecTrade, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        self.sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        self.strategyDict = {}
        
        self.rowdata_id.bind(focus=self.onRowdataFocus)
        
        self.strategyDropDown = SStrategyDropDown()
        firstRecord = True
        strategyList = None
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "strategy.ini")
        alist = sutil.getListFromFile(filePath)
        for astr in alist:
            strategyList = astr.strip().split(",")
            if len(strategyList) < 2:
                continue
            if firstRecord:
                firstRecord = False
                self.strategy_id.text = strategyList[0]
            self.strategyDict[strategyList[0]] = strategyList
            abtn = SButton(text=strategyList[0])
            abtn.size_hint_y = None
            abtn.height = 30
            abtn.bind(on_release=self.strategyDropDown.select)
            self.strategyDropDown.add_widget(abtn)
            
        self.strategy_id.bind(on_release=self.strategyDropDown.open)
        self.strategyDropDown.bind(on_select=self.strategySelect)
        
        self.savefile_id.bind(focus=self.onSavefileFocus)
    
    def onRowdataFocus(self, instance, value):
        if value:
            content = SFileSelectDialog(load=self.loadRowdataDir, cancel=self.dismiss_rowdataPopup)
            content.filechooser_id.path = rowdata_path
            #以下為一奇特的用法，為了解決filechooser中的中文碼顯示問題
            content.filechooser_id.add_widget(Label(text=""))
            popupTitle = self.sysConfDict.get("MSG_DOWNLOAD_FILE")
            self._rowdataPopup = SPopup(title=popupTitle, content=content, size_hint=(0.9, 0.9), title_font=CONSTS.FONT_NAME)
            self._rowdataPopup.open()
    
    def dismiss_rowdataPopup(self):
        self._rowdataPopup.dismiss()
    
    def loadRowdataDir(self, path, filename):
        if len(filename) == 0:
            self.app.showMsgView(CONSTS.ERR_UNSELECT_FILE)
            return        
        self._rowdataPopup.dismiss()
        rowdata_path = path
        filenameTmp = filename[0][len(path) + 1:]
        self.rowdata_id.text = filenameTmp

        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini")
        userConf = sutil.getDictFromFile(filePath)
        userConf["ROWDATA_DIR"] = path
        with open(filePath, 'w', encoding = 'utf-8') as f:
            for key in userConf.keys():
                value = userConf.get(key)
                aStr = key + "=" + value + "\n"
                f.write(aStr)
    
    def strategySelect(self, instance, atext):
        self.strategy_id.text = atext.text
    
    def onSavefileFocus(self, instance, value):
        if value:
            content = SFileInputDialog(load=self.loadSavefileDir, cancel=self.dismiss_savefilePopup)
            content.filechooser_id.path = data_path
            #以下為一奇特的用法，為了解決filechooser中的中文碼顯示問題
            content.filechooser_id.add_widget(Label(text=""))
            popupTitle = self.sysConfDict.get("MSG_DOWNLOAD_FILE")
            self._savefilePopup = SPopup(title=popupTitle, content=content, size_hint=(0.9, 0.9), title_font=CONSTS.FONT_NAME)
            self._savefilePopup.open()
    
    def dismiss_savefilePopup(self):
        self._savefilePopup.dismiss()
    
    def loadSavefileDir(self, path, filename):
        if len(filename) == 0:
            self.app.showMsgView(CONSTS.ERR_UNSELECT_FILE)
            return
        self._savefilePopup.dismiss()
        data_path = path
        self.savefile_id.text = filename

        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini")
        userConf = sutil.getDictFromFile(filePath)
        userConf["BACKTEST_SELECT_DIR"] = path[0:path.rfind(os.sep)]
        userConf["BACKTEST_DIR"] = path
        with open(filePath, 'w', encoding = 'utf-8') as f:
            for key in userConf.keys():
                value = userConf.get(key)
                aStr = key + "=" + value + "\n"
                f.write(aStr)