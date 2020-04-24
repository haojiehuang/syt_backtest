# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))
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
from kivy.properties import ObjectProperty

from sbtmenu import SBTMenu
import sconsts as CONSTS

class SMainApp(App):

    btMenu = ObjectProperty(None)

    confDict = {}
    filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "msgcode.ini")
    confDict[CONSTS.MSG_CODE_DICT] = sutil.getDictFromFile(filePath)
    filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "sysconf_zh_tw.ini")
    confDict[CONSTS.SYS_CONF_DICT] = sutil.getDictFromFile(filePath)
    loginFlag = False
    account = ""
    pwd = ""
    accountIdList = []    

    def build(self):
        self.btMenu = SBTMenu({CONSTS.S_APP:self, "SUBMENU":False})
        return self.btMenu

    def closeWindows(self):
        self.get_running_app().stop()
    
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
        popup = Popup(title=sysConfDict.get("MSG_TITLE"), content=contentLayout,
                size_hint=(None, None), size=(200, 200), auto_dismiss=False)
        contentBtn.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()
    
    def showMixedMsg(self, errCode, errDesc):
        msgText = str(errCode) + "->" + errDesc
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
        popup = Popup(title=sysConfDict.get("MSG_TITLE"), content=contentLayout,
                size_hint=(None, None), size=(200, 200), auto_dismiss=False)
        contentBtn.bind(on_press=popup.dismiss)
        popup.title_font = CONSTS.FONT_NAME
        popup.open()    
        
if __name__ == '__main__':
    SMainApp().run()