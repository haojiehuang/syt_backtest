# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
import threading

import sutil
import sconsts as CONSTS
from selements import SLabel, SButton, SPopup
from sbacktest import SBacktest
from stradecost import STradeCost
from sselect_file import SSelectFile
from stradereport import STradeReport

bk_select_dir, bk_file_dir = sutil.checkBacktestDir()

with open(os.path.join(os.path.dirname(__file__), "sbtmenu.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class SBTMenu(BoxLayout):
    
    body_layout = ObjectProperty(None)
    exitLayout_id = ObjectProperty(None)
    sbacktest = None
    fileList = None
    app = None
    
    confDict = {}
    filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "msgcode.ini")
    confDict[CONSTS.MSG_CODE_DICT] = sutil.getDictFromFile(filePath)
    filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "sysconf_zh_tw.ini")
    confDict[CONSTS.SYS_CONF_DICT] = sutil.getDictFromFile(filePath)    

    def __init__(self, paramDict, **kwargs):
        super(SBTMenu, self).__init__(**kwargs)

        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        userConf = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
        bt_file = userConf.get("BACKTEST_FILE")
        if bt_file != None and bt_file != "":
            self.fileList = bt_file.split(",")
            aflag = False
            for afile in self.fileList:
                afilePath = os.path.join(bk_file_dir, afile)
                if not os.path.exists(afilePath):
                    aflag = True
                    break
            if not aflag:
                if self.body_layout != None:
                    self.remove_widget(self.body_layout)
                refDict = {}
                for key in self.paramDict.keys():
                    refDict[key] = self.paramDict[key]
                refDict["fileDir"] = bk_file_dir
                refDict["fileList"] = self.fileList
                refDict[CONSTS.S_BTMENU] = self
                self.sbacktest = SBacktest(refDict)
                self.body_layout = self.sbacktest
                self.body_layout.size_hint = (1, .95)
                self.body_layout.pos_hint = {'x':0,'y':0}
                self.add_widget(self.body_layout, index=0)
        
        subMenu = self.paramDict.get("SUBMENU")
        if subMenu != None:
            if subMenu == False:
                exitBtn = SButton(text="離開", size_hint=(1, 1))
                exitBtn.halign = "center"
                exitBtn.valign = "middle"
                exitBtn.bind(on_release=self.closeWindows)
                self.exitLayout_id.add_widget(exitBtn)
    
    def showMsgView(self, msgCode):
        msgCodeDict = self.confDict.get(CONSTS.MSG_CODE_DICT)
        msgText = msgCodeDict.get(msgCode)
        if msgText == None:
            msgText = "Unknow error code->" + str(msgCode)
        contentLayout = BoxLayout()
        contentLayout.orientation = "vertical"
        contentLayout.size_hint = (1, 1)
        from selements import SLabel
        contentLabel = SLabel(text=msgText, size_hint=(1, .8))
        contentLabel.halign = "center"
        contentLayout.add_widget(contentLabel)

        sysConfDict = self.confDict.get(CONSTS.SYS_CONF_DICT)

        from selements import SButton
        contentBtn = SButton(text=sysConfDict.get("MSG_CONFIRM"), size_hint=(1, .2))
        contentLayout.add_widget(contentBtn)    
        popup = SPopup(title=sysConfDict.get("MSG_TITLE"), content=contentLayout,
                size_hint=(None, None), size=(200, 200), auto_dismiss=False)
        contentBtn.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()

    def closeWindows(self, obj):
        if self.app != None:
            self.app.closeWindows()

    def stradeCost(self):
        self.stcLayout = STradeCost({CONSTS.S_APP:self.app})
        popup = SPopup(title="交易成本設定", content=self.stcLayout,
                size_hint=(None, None), size=(640, 480), auto_dismiss=False)
        self.stcLayout.closebtn_id.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()
    
    def sselectFile(self):
        self.ssfLayout = SSelectFile({CONSTS.S_APP:self.app})
        self.ssf_popup = SPopup(title="選擇回測檔案", content=self.ssfLayout,
                size_hint=(None, None), size=(540, 480), auto_dismiss=False)
        self.ssfLayout.ensurebtn_id.bind(on_press=self.finishedSelectFiles)
        self.ssfLayout.closebtn_id.bind(on_press=self.ssf_popup.dismiss)
        self.ssf_popup.title_font = CONSTS.FONT_NAME
        self.ssf_popup.open()
    
    def finishedSelectFiles(self, instance):
        fileCount = len(self.ssfLayout.rightrv_id.data)
        if fileCount == 0:
            self.showMsgView(CONSTS.ERR_UNSELECT_FILE)
            return
        self.ssf_popup.dismiss()
        self.saveUserConf()
        
        if self.fileList != None:
            self.fileList.clear()
        else:
            self.fileList = []
        for adict in self.ssfLayout.rightrv_id.data:
            self.fileList.append(adict.get("text"))
        if self.sbacktest == None:
            self.remove_widget(self.body_layout)
            refDict = {}
            for key in self.paramDict.keys():
                refDict[key] = self.paramDict[key]
            refDict["fileDir"] = self.ssfLayout.filepath
            refDict["fileList"] = self.fileList
            refDict[CONSTS.S_BTMENU] = self
            self.sbacktest = SBacktest(refDict)
            self.body_layout = self.sbacktest
            self.body_layout.size_hint = (1, .96)
            self.body_layout.pos_hint = {'x':0,'y':0}
            self.add_widget(self.body_layout, index=0)
        else:
            self.sbacktest.loadFile(self.ssfLayout.filepath, self.fileList)
    
    def saveUserConf(self):
        filePath = os.path.join(os.path.dirname(__file__), "../conf/user.ini")
        userConf = sutil.getDictFromFile(filePath)
        userConf["BACKTEST_SELECT_DIR"] = self.ssfLayout.filedir
        userConf["BACKTEST_DIR"] = self.ssfLayout.filepath
        backtest_file = ""        
        for adict in self.ssfLayout.rightrv_id.data:
            backtest_file += adict.get("text") 
            backtest_file += ","
        backtest_file = backtest_file[0:-1]
        userConf["BACKTEST_FILE"] = backtest_file
        with open(filePath, 'w', encoding = 'utf-8') as f:
            for key in userConf.keys():
                value = userConf.get(key)
                aStr = key + "=" + value + "\n"
                f.write(aStr)
        
    def analyzeBacktest(self):
        if self.sbacktest != None:
            if self.sbacktest.dataList != None and len(self.sbacktest.dataList) != 0:
                refDict = {}
                for key in self.paramDict.keys():
                    refDict[key] = self.paramDict.get(key)
                refDict["dataList"] = self.sbacktest.dataList
                refDict["fileList"] = self.fileList
                refDict[CONSTS.S_BTMENU] = self
                self.strLayout = STradeReport(refDict)
                self.str_popup = SPopup(title="分析報表", content=self.strLayout,
                        size_hint=(None, None), size=(800, 600), auto_dismiss=False)
                self.strLayout.closebtn_id.bind(on_press=self.str_popup.dismiss)
                self.str_popup.title_font = CONSTS.FONT_NAME
                self.str_popup.open()
            else:
                self.showMsgView(CONSTS.ERR_NO_BACKTEST_DATA)
        else:
            self.showMsgView(CONSTS.ERR_NOT_EXECUTE_BACKTEST)