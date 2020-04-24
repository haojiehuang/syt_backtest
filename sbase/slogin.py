# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !
import sys
import os
sys.path.append(".." + os.sep)
import abxtoolkit
abxtoolkit.load_ini(abxtoolkit.ABX_MODE.AP)

import time
import threading
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty

import sutil
import sdate_utils
import sconsts as CONSTS
from selements import SButton, SLabel, STextInput

import json

with open(os.path.join(os.path.dirname(__file__), "slogin.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class SLogin(BoxLayout):
    
    user_id = ObjectProperty(None)
    saveuser_id = ObjectProperty(None)
    pwd_id = ObjectProperty(None)
    loginbtn_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    userConf = {}
    loginFlag = None
    accountIdList = []

    def __init__(self, paramDict, **kwargs):
        super(SLogin, self).__init__(**kwargs)
    
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        self.initial_data()

    def initial_data(self):
        filePath = os.path.join(os.path.dirname(__file__), "../conf/user.ini")
        self.userConf = sutil.getDictFromFile(filePath)
        account = self.userConf.get("ACCOUNT")
        password = self.userConf.get("PASSWORD")
        if account != None and account != "":
            self.user_id.text = account
            self.saveuser_id.active = True
            self.pwd_id.text = password

    def login(self):
        self.loginFlag = None
        useridTxt = self.user_id.text
        if useridTxt == "":
            self.btmenu.showMsgView(CONSTS.ERR_USER_IS_SPACE)
            return

        if useridTxt.find("@") != -1:
            useridTxt = "1|" + useridTxt
        else:
            useridTxt = "2|" + useridTxt
        
        self.loginDict = {}
        self.loginDict["Host"] = self.userConf.get("DOWNLOAD_URL").strip()
        self.loginDict["Port"] = int(self.userConf.get("DOWNLOAD_PORT").strip())
        self.loginDict["User"] = useridTxt
        self.loginDict["Password"] = self.pwd_id.text
        self.loginDict["ProductId"] = int(self.userConf.get("PRODUCT_ID").strip())
        self.loginDict["UserType"] = int(self.userConf.get("USER_TYPE").strip())
        self.loginDict["LoginType"] = int(self.userConf.get("LOGIN_TYPE").strip())
        
        self.loginEvent()

    def loginEvent(self):
        contentLayout = BoxLayout()
        contentLayout.orientation = "vertical"
        contentLayout.size_hint = (1, 1)
        contentLabel = SLabel(text="登入中...", size_hint=(1, .8))
        contentLayout.add_widget(contentLabel)
        
        sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        self.result = None
        self.dl_popup = Popup(title=sysConfDict.get("MSG_TITLE"), content=contentLayout,
                size_hint=(None, None), size=(160, 120), auto_dismiss=False)
        self.dl_popup.title_font = CONSTS.FONT_NAME
        self.dl_popup.bind(on_open=self.login_open)
        Clock.schedule_once(self.loginStart)

    def loginStart(self, instance):
        self.dl_popup.open()
        threading.Thread(target=self.toolkitLogin).start()
        
    def toolkitLogin(self):
        self.result = abxtoolkit.get_accountid(self.loginDict)
        
    def login_check(self, dt):
        if self.result != None:
            self.dl_popup.dismiss()
            self.event.cancel()   
            errCode = self.result.get("ErrCode")
            if errCode != 0:
                errDesc = self.result.get("ErrDesc")
                self.loginFlag = False
                self.app.showMixedMsg(errCode, errDesc)
            else:
                self.loginFlag = True
                self.accountIdList = self.result.get("AccountID_List")
                if self.accountIdList == None:
                    self.accountIdList = []
                self.saveUserConf()

    def login_open(self, instance):
        self.event = Clock.schedule_interval(self.login_check, .0005)
        
    def saveUserConf(self):
        filePath = os.path.join(os.path.dirname(__file__), "../conf/user.ini")
        userConf = sutil.getDictFromFile(filePath)
        if self.saveuser_id.active:
            userConf["ACCOUNT"] = self.user_id.text
            userConf["PASSWORD"] = self.pwd_id.text
        else:
            userConf["ACCOUNT"] = ""
            userConf["PASSWORD"] = ""
        with open(filePath, 'w', encoding = 'utf-8') as f:
            for key in userConf.keys():
                value = userConf.get(key)
                aStr = key + "=" + value + "\n"
                f.write(aStr)
