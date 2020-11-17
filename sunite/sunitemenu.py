# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import webbrowser
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as colorHex
import time
import threading
import sys
import os
sys.path.append(".." + os.sep)
import abxtoolkit
abxtoolkit.load_ini(abxtoolkit.ABX_MODE.AP, 'h94_ab')

sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbacktest" + os.sep))
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sexectrade" + os.sep))
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sstkchoose" + os.sep))
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sstkquote" + os.sep))
import sutil
import sconsts as CONSTS
from selements import SPopup, SLabel, SButton
from slogin import SLogin
from sdownload import SDownload
from sstrategy import SStrategy
from sexectrade import SExecTrade
from sbacktest import SBacktest
from sselect_file import SSelectFile
from stradecost import STradeCost
from stradereport import STradeReport
from soption_select import SOptionSelect
from sselect_stock import SSelectStock
from self_stkquote import SelfStkQuote

with open(os.path.join(os.path.dirname(__file__), "sunitemenu.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class MenuButton(Button):

    isMouseInFlag = False
    suniteMenu = None
    menuLayout = None
        
    def __init__(self, suniteMenu, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.suniteMenu = suniteMenu
        Window.bind(mouse_pos=self.on_mouse_pos)
        
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            if self.isMouseInFlag == True:
                return
            else:
                self.isMouseInFlag = True
                self.color = colorHex("#0000FF")
                self.suniteMenu.removeMenu()
                if self.text == "用戶中心":
                    self.menuLayout = self.suniteMenu.userMenu(self)
                elif self.text == "交易執行":
                    self.menuLayout = self.suniteMenu.executeMenu(self)
                elif self.text == "交易分析":
                    self.menuLayout = self.suniteMenu.analyzeMenu(self)
        else:
            if self.isMouseInFlag == True:
                self.isMouseInFlag = False
                self.color = colorHex("#000000")
                if self.menuLayout != None:
                    layoutWidth_posX = self.menuLayout.pos[0] + self.menuLayout.size[0]
                    if pos[1] > self.pos[1] or pos[1] < self.menuLayout.pos[1] or pos[0] < self.pos[0] or pos[0] > layoutWidth_posX:
                        self.suniteMenu.removeMenu()
                
class SubMenuButton(Button):

    isMouseInFlag = False
        
    def __init__(self, **kwargs):
        super(SubMenuButton, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            if self.isMouseInFlag == True:
                return
            else:
                self.isMouseInFlag = True
                self.color = colorHex("#0000FF")
        else:
            if self.isMouseInFlag == True:
                self.isMouseInFlag = False
                self.color = colorHex("#000000")

class MenuLayout(BoxLayout):
    
    isOpenFlag = False
    isMouseInFlag = False
    suniteMenu = None
    layoutHeight = 0
    
    def __init__(self, suniteMenu, **kwargs):
        super(MenuLayout, self).__init__(**kwargs)
        self.isOpenFlag = True
        self.suniteMenu = suniteMenu
        self.layoutHeight = self.size[1]
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            if self.isMouseInFlag == True:
                return
            else:
                self.isOpenFlag = False
                self.isMouseInFlag = True
        else:
            if self.isOpenFlag == True:
                return
            if self.isMouseInFlag == True:
                widthRange = self.pos[0] + self.size[0]
                heightRange = self.pos[1] + self.layoutHeight
                if pos[0] < self.pos[0] or pos[0] > widthRange or pos[1] > heightRange or pos[1] < self.pos[1]:
                    self.isMouseInFlag = False
                    self.suniteMenu.removeMenu()
        
class SUniteMenu(FloatLayout):
    
    menuId = ObjectProperty(None)
    body_layout = ObjectProperty(None)
    content_layout = ObjectProperty(None)
    btMenu = ObjectProperty(None)
    app = None    
    menuLayout = ObjectProperty(None)
    sosLayout = None
    sosPopup = None
    sbacktest = None
    selfStkQuote = None
    sselectStock = None
    fileList = None
    
    def __init__(self, paramDict, **kwargs):
        super(SUniteMenu, self).__init__(**kwargs)

        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        self.menuId.add_widget(BoxLayout(size_hint=(.01, 1)))
        mbtn = MenuButton(suniteMenu=self, text="用戶中心", size_hint=(.15, 1), halign="center", valign="middle")
        self.menuId.add_widget(mbtn)

        self.menuId.add_widget(BoxLayout(size_hint=(.01, 1)))
        mbtn = MenuButton(suniteMenu=self, text="交易執行", size_hint=(.15, 1), halign="center", valign="middle")
        self.menuId.add_widget(mbtn)
        
        self.menuId.add_widget(BoxLayout(size_hint=(.01, 1)))
        mbtn = MenuButton(suniteMenu=self, text="交易分析", size_hint=(.15, 1), halign="center", valign="middle")
        self.menuId.add_widget(mbtn)
        
        self.menuId.add_widget(BoxLayout(size_hint=(.01, 1)))
        mbtn = MenuButton(suniteMenu=self, text="智慧選股", size_hint=(.15, 1), halign="center", valign="middle")
        mbtn.bind(on_release=self.optionSelect)
        self.menuId.add_widget(mbtn)
        
        self.menuId.add_widget(BoxLayout(size_hint=(.01, 1)))
        mbtn = MenuButton(suniteMenu=self, text="股票報價", size_hint=(.15, 1), halign="center", valign="middle")
        mbtn.bind(on_release=self.stockQuote)
        self.menuId.add_widget(mbtn)

        self.menuId.add_widget(BoxLayout(size_hint=(.01, 1)))
        mbtn = MenuButton(suniteMenu=self, text="離開", size_hint=(.15, 1), halign="center", valign="middle")
        mbtn.bind(on_release=self.closeWindows)
        self.menuId.add_widget(mbtn)
        
        self.menuId.add_widget(BoxLayout(size_hint=(.04, 1)))

    def closeWindows(self, instance):
        if self.app != None:
            self.app.closeWindows()
    
    def login(self, execType):
        self.execType = execType
        self.loginLayout = SLogin({CONSTS.S_APP:self.app})
        self.loginPopup = Popup(title="登入", content=self.loginLayout, size_hint=(None, None),
                      size=(400, 300), auto_dismiss=False)
        self.loginLayout.closebtn_id.bind(on_press=self.loginPopup.dismiss)
        self.loginLayout.loginbtn_id.bind(on_press=self.loginProcess)
        self.loginPopup.title_font = CONSTS.FONT_NAME
        self.loginPopup.open()

    def loginProcess(self, instance):
        Clock.schedule_once(self.loginSchedule)

    def loginSchedule(self, instance):
        self.event = Clock.schedule_interval(self.loginCheck, .0005)
        threading.Thread(target=self.toolkitLogin).start()
    
    def loginCheck(self, dt):
        if self.loginLayout.loginFlag != None:
            self.event.cancel()
            if self.loginLayout.loginFlag == True:
                self.app.loginFlag = True
                self.app.accountIdList = self.loginLayout.accountIdList
                self.app.account = self.loginLayout.user_id.text
                self.app.pwd = self.loginLayout.pwd_id.text
                self.loginPopup.dismiss()
                if self.execType == "query":
                    self.openWebBrowser()
                elif self.execType == "download":
                    self.downloadData()
                elif self.execType == "optionSelect":
                    self.doOptionSelect()
                elif self.execType == "stockQuote":
                    self.doStockQuote()
    
    def toolkitLogin(self):
        self.loginLayout.login()

    def removeMenu(self):
        if self.menuLayout == None:
            return
        self.remove_widget(self.menuLayout)

    def userMenu(self, instance):
        
        width = instance.size[0] + 10
        x1 = instance.pos[0]
        y1 = instance.pos[1] - 63
        self.menuLayout = MenuLayout(suniteMenu = self, size_hint=(None, None), size=(width, instance.size[1]), pos=[x1, y1], orientation="vertical")
        
        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1, None), height=30, text="用戶註冊")
        btn.bind(on_press=self.registerUser)
        self.menuLayout.add_widget(btn)
        
        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1, None), height=30, text="帳務查詢")
        btn.bind(on_press=self.query)
        self.menuLayout.add_widget(btn)

        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
    
        self.add_widget(self.menuLayout)
        self.menuLayout.layoutHeight = 63
        
        return self.menuLayout

    def registerUser(self, instance):
        self.removeMenu()
        aDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
        webbrowser.open(aDict.get("WEB_REGISTER_URL"))    

    def query(self, instance):
        self.removeMenu()
        if self.app.loginFlag == False:
            self.login("query")
        else:
            self.openWebBrowser()   
    
    def openWebBrowser(self):
        urlParam = "dataID=" + self.app.account + "&dataCheck=" + self.app.pwd
        aDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
        webbrowser.open(aDict.get("WEB_LOGIN_URL") + urlParam, new=0)
    
    def executeMenu(self, instance):
        
        width = instance.size[0] + 40
        x1 = instance.pos[0]
        y1 = instance.pos[1] - 125
        self.menuLayout = MenuLayout(suniteMenu = self, size_hint=(None, None), size=(width, instance.size[1]), pos=[x1, y1], orientation="vertical")
        
        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1, None), height=30, text="歷史報價下載")
        btn.bind(on_press=self.downloadProcess)
        self.menuLayout.add_widget(btn)
        
        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1, None), height=30, text="ABXToolkit使用說明")
        btn.bind(on_press=self.explain)
        self.menuLayout.add_widget(btn)
        
        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1, None), height=30, text="交易策略設定")
        btn.bind(on_press=self.strategySetting)
        self.menuLayout.add_widget(btn)
        
        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1, None), height=30, text="執行交易程式")
        btn.bind(on_press=self.executeTrade)
        self.menuLayout.add_widget(btn)    

        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))

        self.add_widget(self.menuLayout)
        self.menuLayout.layoutHeight = 125
        
        return self.menuLayout

    def downloadProcess(self, instance):
        self.removeMenu()
        if self.app.loginFlag == False:
            self.login("download")
        else:
            self.downloadData()
    
    def downloadData(self):
        downloadLayout = SDownload({CONSTS.S_APP:self.app})
        popup = SPopup(title="下載歷史報價資料", content=downloadLayout, size_hint=(None, None),
                size=(540, 400), auto_dismiss=False)
        downloadLayout.closebtn_id.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()

    def explain(self, instance):
        self.removeMenu()
        aDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
        webbrowser.open(aDict.get("WEB_EXPLAIN_URL"), new=0)

    def strategySetting(self, instance):
        self.removeMenu()
        self.ssyLayout = SStrategy({CONSTS.S_APP:self.app})
        popup = SPopup(title="交易策略設定", content=self.ssyLayout,
                size_hint=(None, None), size=(640, 480), auto_dismiss=False)
        self.ssyLayout.closebtn_id.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()

    def executeTrade(self, instance):
        self.removeMenu()
        self.etLayout = SExecTrade({CONSTS.S_APP:self.app})
        self.et_popup = SPopup(title="執行交易程式", content=self.etLayout,
                size_hint=(None, None), size=(360, 280), auto_dismiss=False)
        self.etLayout.ensurebtn_id.bind(on_press=self.execTradeEvent)
        self.etLayout.closebtn_id.bind(on_press=self.et_popup.dismiss)
        self.et_popup.title_font = CONSTS.FONT_NAME
        self.et_popup.open()

    def execTradeEvent(self, instance):
        
        rowdataName = self.etLayout.rowdata_id.text
        strategyName = self.etLayout.strategy_id.text
        savefileName = self.etLayout.savefile_id.text
        if rowdataName == "":
            self.app.showErrorView(True, CONSTS.ERR_UNSELECT_HISTORY_DATA)
            return
        elif strategyName == "":
            self.app.showErrorView(True, CONSTS.ERR_UNSELECT_STRATEGY)
            return
        elif savefileName == "":
            self.app.showErrorView(True, CONSTS.ERR_UNSELECT_SAVEFILE)
            return
        
        strategy_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "strategy"))
        strategyData = None
        if strategyName != "":
            alist = sutil.getListFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "strategy.ini"))
            for astr in alist:
                strategyList = astr.strip().split(",")
                if len(strategyList) < 2:
                    continue
                if strategyName == strategyList[0]:
                    strategyData = strategyList[1]
            isExistFlag = True
            if strategyData != None:
                filePath = os.path.join(strategy_dir, strategyData)
                if os.path.exists(filePath) != True:
                    isExistFlag = False
            else:
                isExistFlag = False
            if isExistFlag == False:
                msgCodeDict = self.app.confDict.get(CONSTS.MSG_CODE_DICT)
                msgText = msgCodeDict.get(CONSTS.ERR_STRATEGY_FILE_NOT_FOUND)               
                self.app.showErrorView(False, strategyName, msgText)
                return

        userConf = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
        rowdata_dir = userConf.get("ROWDATA_DIR")
        data_dir = userConf.get("BACKTEST_DIR")

        self.rowdata_file = os.path.join(rowdata_dir, rowdataName)
        self.strategy_file = os.path.join(strategy_dir, strategyData)
        self.savefile_file = os.path.join(data_dir, savefileName)
        
        self.doPtradeEvent()

    def doPtradeEvent(self):
        contentLayout = BoxLayout()
        contentLayout.orientation = "vertical"
        contentLayout.size_hint = (1, 1)
        contentLabel = SLabel(text="  交易執行中...", size_hint=(1, .8))
        contentLayout.add_widget(contentLabel)
        
        sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        self.result = None
        self.dp_popup = Popup(title=sysConfDict.get("MSG_TITLE"), content=contentLayout,
                size_hint=(None, None), size=(160, 120), auto_dismiss=False)
        self.dp_popup.title_font = CONSTS.FONT_NAME
        self.dp_popup.bind(on_open=self.dp_open)
        Clock.schedule_once(self.doPtradeStart)

    def doPtradeStart(self, instance):
        self.dp_popup.open()
        threading.Thread(target=self.toolkitPtrade).start()
        
    def toolkitPtrade(self):
        self.result = abxtoolkit.do_ptrade(self.rowdata_file, self.strategy_file, self.savefile_file)
        
    def doPtrade_check(self, dt):
        if self.result != None:
            self.dp_popup.dismiss()
            self.event.cancel()            
            errCode = self.result.get("ErrCode")
            if errCode != 0:
                errDesc = self.result.get("ErrDesc")
                self.app.showErrorView(False, errCode, errDesc)
            else:
                self.finishedPopup()                

    def dp_open(self, instance):
        self.event = Clock.schedule_interval(self.doPtrade_check, .0005)

    def finishedPopup(self):
        content = BoxLayout(size_hint=(1, 1), orientation="vertical")
        
        content.add_widget(BoxLayout(size_hint=(1, .4)))
        
        bottomLayout = BoxLayout(size_hint=(1, .2), orientation="horizontal")
        bottomLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        ensurebtn = SButton(text="確定", size_hint=(.8, .8))
        bottomLayout.add_widget(ensurebtn)
        bottomLayout.add_widget(BoxLayout(size_hint=(.1, 1)))
        content.add_widget(bottomLayout)

        content.add_widget(BoxLayout(size_hint=(1, .4)))

        self.fin_popup = SPopup(title="執行完成", content=content, title_font=CONSTS.FONT_NAME,
                        size_hint=(None, None), size=(200, 100), auto_dismiss=False)
        ensurebtn.bind(on_press=self.fin_popup.dismiss)
        self.fin_popup.open()

    def analyzeMenu(self, instance):

        width = instance.size[0] + 10
        x1 = instance.pos[0]
        y1 = instance.pos[1] - 94
        self.menuLayout = MenuLayout(suniteMenu = self, size_hint=(None, None), size=(width, instance.size[1]), pos=[x1, y1], orientation="vertical")

        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1,None), height=30, text="回測")
        btn.bind(on_press=self.sselectFile)
        self.menuLayout.add_widget(btn)

        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1,None), height=30, text="交易分析")
        btn.bind(on_press=self.analyzeBacktest)
        self.menuLayout.add_widget(btn)

        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))
        btn = SubMenuButton(size_hint=(1,None), height=30, text="交易成本設定")
        btn.bind(on_press=self.stradeCost)
        self.menuLayout.add_widget(btn) 

        self.menuLayout.add_widget(BoxLayout(size_hint=(1, None), height=1))

        self.add_widget(self.menuLayout)
        self.menuLayout.layoutHeight = 94

        return self.menuLayout

    def sselectFile(self, instance):
        self.removeMenu()
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
            self.app.showErrorView(True, CONSTS.ERR_UNSELECT_FILE)
            return
        self.ssf_popup.dismiss()
        self.saveUserConf()
        
        if self.selfStkQuote != None:
            self.selfStkQuote.closeStkQuote()
        
        if self.fileList != None:
            self.fileList.clear()
        else:
            self.fileList = []
        for adict in self.ssfLayout.rightrv_id.data:
            self.fileList.append(adict.get("text"))
        if self.sbacktest == None:
            self.body_layout.remove_widget(self.content_layout)
            refDict = {}
            for key in self.paramDict.keys():
                refDict[key] = self.paramDict[key]
            refDict["fileDir"] = self.ssfLayout.filepath
            refDict["fileList"] = self.fileList
            self.sbacktest = SBacktest(refDict)
            self.content_layout = self.sbacktest
            self.content_layout.size_hint = (1, 1)
            self.body_layout.add_widget(self.content_layout)
        else:
            self.sbacktest.loadFile(self.ssfLayout.filepath, self.fileList)
        """if self.sbacktest == None:
            self.body_layout.remove_widget(self.content_layout)
            refDict = {}
            for key in self.paramDict.keys():
                refDict[key] = self.paramDict[key]
            refDict["fileDir"] = self.ssfLayout.filepath
            refDict["fileList"] = self.fileList
            self.sbacktest = SBacktest(refDict)
            self.content_layout = self.sbacktest
            self.content_layout.size_hint = (1, 1)
            self.body_layout.add_widget(self.content_layout)
        else:
            self.sbacktest.loadFile(self.ssfLayout.filepath, self.fileList)
        """
        self.body_layout.remove_widget(self.content_layout)
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict[key]
        refDict["fileDir"] = self.ssfLayout.filepath
        refDict["fileList"] = self.fileList
        self.sbacktest = SBacktest(refDict)
        self.content_layout = self.sbacktest
        self.content_layout.size_hint = (1, 1)
        self.body_layout.add_widget(self.content_layout)

    def saveUserConf(self):
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini")
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

    def analyzeBacktest(self, instance):
        self.removeMenu()
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
                self.app.showErrorView(True, CONSTS.ERR_NO_BACKTEST_DATA)
        else:
            self.app.showErrorView(True, CONSTS.ERR_NOT_EXECUTE_BACKTEST)

    def stradeCost(self, instance):
        self.removeMenu()
        self.stcLayout = STradeCost({CONSTS.S_APP:self.app})
        popup = SPopup(title="交易成本設定", content=self.stcLayout,
                size_hint=(None, None), size=(640, 480), auto_dismiss=False)
        self.stcLayout.closebtn_id.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()
        
    def optionSelect(self, instance):
        if self.app.loginFlag == False:
            self.login("optionSelect")
        else:
            self.doOptionSelect()
    
    def doOptionSelect(self):
        if self.sosLayout == None:
            self.sosLayout = SOptionSelect({CONSTS.S_APP:self.app})
        else:
            self.sosPopup.open()
            return
        self.sosPopup = SPopup(title="智慧選股", content=self.sosLayout,
                size_hint=(None, None), size=(640, 480), auto_dismiss=False)
        self.sosLayout.ensurebtn_id.bind(on_press=self.execOptionResult)
        self.sosLayout.resetbtn_id.bind(on_press=self.resetOptionSelect)
        self.sosLayout.selectbtn_id.bind(on_press=self.showOptionSelect)
        self.sosLayout.closebtn_id.bind(on_press=self.optionPopupDismiss)
        self.sosPopup.title_font = CONSTS.FONT_NAME
        self.sosPopup.open()
    
    def execOptionResult(self, instance):
        if self.sosLayout.optionList == None:
            self.app.showErrorView(True, CONSTS.ERR_UNSELECT_OPTION)
            return
        else:
            isSelectFlag = False
            for aObj in self.sosLayout.optionList:
                if aObj.isSelected():
                    isSelectFlag = True
                    break
            if isSelectFlag == False:
                self.app.showErrorView(True, CONSTS.ERR_UNSELECT_OPTION)
                return                 
        self.optionPopupDismiss(instance)
        
        fidList = []
        for aObj in self.sosLayout.optionList:
            if aObj.isSelected():
                fidList.append(aObj.getValueDict())
        
        self.body_layout.remove_widget(self.content_layout)
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict[key]
        refDict["fidList"] = fidList
        self.sselectStock = SSelectStock(refDict)
        self.content_layout = self.sselectStock
        self.content_layout.size_hint = (1, 1)
        self.body_layout.add_widget(self.content_layout)        
    
    def resetOptionSelect(self, instance):
        self.sosLayout.setToOptionDefault()
    
    def showOptionSelect(self, instance):
        if self.sosLayout.optionList == None:
            self.app.showErrorView(True, CONSTS.ERR_UNSELECT_OPTION)
            return
        else:
            isSelectFlag = False
            for aObj in self.sosLayout.optionList:
                if aObj.isSelected():
                    isSelectFlag = True
                    break
            if isSelectFlag == False:
                self.app.showErrorView(True, CONSTS.ERR_UNSELECT_OPTION)
                return                         
        self.sosLayout.showSelectedOptionDesc()
    
    def optionPopupDismiss(self, instance):
        self.sosPopup.dismiss()
    
    def stockQuote(self, instance):
        self.removeMenu()
        if self.app.loginFlag == False:
            self.login("stockQuote")
        else:
            self.doStockQuote()
    
    def doStockQuote(self):
        self.body_layout.remove_widget(self.content_layout)
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict[key]
        self.selfStkQuote = SelfStkQuote(refDict)
        self.content_layout = self.selfStkQuote
        self.content_layout.size_hint = (1, 1)
        self.body_layout.add_widget(self.content_layout)  
        
