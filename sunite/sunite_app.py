# -*- coding: utf-8 -*-

import win32timezone
import kivy
kivy.require('1.11.0') # replace with your current kivy version !
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbacktest" + os.sep))
import sutil
aDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
backend_type = aDict.get("BACKEND_TYPE")
if backend_type == None:
    backend_type = "glew"
os.environ['KIVY_GL_BACKEND'] = backend_type
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0') #設定esc鍵，不結束應用程式
Config.set('graphics', 'multisamples', '0') #設定部分電腦無法使用opengl的問題
Config.set('input', 'mouse', 'mouse,multitouch_on_demand') #消除點擊滑鼠右鍵會產生紅色圓點的問題

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex as colorHex

from sunitemenu import SUniteMenu
from selements import SLabel, SButton, STableGridLayout
from kivy.core.window import Window

import sconsts as CONSTS

class SUniteApp(App):

    suMenu = ObjectProperty(None)

    confDict = {}
    filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "msgcode.ini")
    confDict[CONSTS.MSG_CODE_DICT] = sutil.getDictFromFile(filePath)
    filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "sysconf_zh_tw.ini")
    confDict[CONSTS.SYS_CONF_DICT] = sutil.getDictFromFile(filePath)
    loginFlag = False
    account = ""
    pwd = ""
    accountIdList = []
    stkNameDict = {}
    
    def build(self):
        self.suMenu = SUniteMenu({CONSTS.S_APP:self})
        return self.suMenu

    def closeWindows(self):
        self.get_running_app().stop()

    def showErrorView(self, isGetMsgDesc, msgCode, msgDesc=None):
        contentLayout = BoxLayout()
        contentLayout.orientation = "vertical"
        contentLayout.size_hint = (1, 1)        
        if isGetMsgDesc == True:
            msgCodeDict = self.confDict.get(CONSTS.MSG_CODE_DICT)
            msgText = msgCodeDict.get(msgCode)
            if msgText == None:
                msgText = "Unknow error code->" + str(msgCode)
            else:
                msgText = str(msgCode) + "->" + msgText
            if msgDesc == None or msgDesc == "":
                contentLabel = SLabel(text=msgText, size_hint=(1, .8))
                contentLabel.halign = "center"
                contentLayout.add_widget(contentLabel)
            else:
                titleLabel = SLabel(text=msgText, size_hint=(1, .2))
                titleLabel.halign = "center"
                contentLayout.add_widget(titleLabel)            
                slview = ScrollView(size_hint=(1, .6))
                contentLayout.add_widget(slview)
                explainLayout = STableGridLayout(cols=1, spacing=1, size_hint_y=None)
                explainLayout.bind(minimum_height=explainLayout.setter('height'))
                for aStr in msgDesc:
                    explainLabel = SLabel(text=aStr, size_hint=(1, None), height=20)
                    explainLabel.halign = "center"
                    explainLabel.color = colorHex("#000000")
                    explainLabel.font_name = CONSTS.FONT_NAME
                    explainLayout.add_widget(explainLabel)
                slview.add_widget(explainLayout)                
        else:
            msgText = str(msgCode) + "->" + msgDesc
            contentLabel = SLabel(text=msgText, size_hint=(1, .8))
            contentLabel.halign = "center"
            contentLayout.add_widget(contentLabel)
        
        sysConfDict = self.confDict.get(CONSTS.SYS_CONF_DICT)

        contentBtn = SButton(text=sysConfDict.get("MSG_CONFIRM"), size_hint=(1, .2))
        contentLayout.add_widget(contentBtn)    
        popup = Popup(title=sysConfDict.get("MSG_TITLE"), content=contentLayout,
                      size_hint=(None, None), size=(200, 200), auto_dismiss=False)
        contentBtn.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()
        
if __name__ == '__main__':
    SUniteApp().run()