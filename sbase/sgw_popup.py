# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)

import time
import threading
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

import sconsts as CONSTS
from selements import SLabel

class SGwPopup(BoxLayout):
    
    def __init__(self, paramDict, **kwargs):
        super(SGwPopup, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        
        self.app = self.paramDict.get(CONSTS.S_APP)
        self.titleMsg = self.paramDict.get("TitleMsg")
        self.infoMsg = self.paramDict.get("InfoMsg")
        self.popupSize = self.paramDict.get("PopupSize")
        self.gwParam = self.paramDict.get("GwParam") 
        self.gwFunc = self.paramDict.get("GwFunc")
        self.resultFunc = self.paramDict.get("ResultFunc")
        
    def processEvent(self):

        contentLayout = BoxLayout()
        contentLayout.orientation = "vertical"
        contentLayout.size_hint = (1, 1)
        contentLabel = SLabel(text=self.infoMsg, size_hint=(1, .8))
        contentLayout.add_widget(contentLabel)
    
        self.result = None
        self.dl_popup = Popup(title=self.titleMsg, content=contentLayout, 
            size_hint=(None, None), size=self.popupSize, auto_dismiss=False)
        self.dl_popup.title_font = CONSTS.FONT_NAME
        self.dl_popup.bind(on_open=self._openFunc)
        Clock.schedule_once(self._startFunc)

    def _startFunc(self, instance):
        self.dl_popup.open()
        threading.Thread(target=self._toolkitFunc).start()
        
    def _toolkitFunc(self):
        self.result = self.gwFunc(self.gwParam)
        
    def _result_check(self, dt):
        if self.result != None:
            self.dl_popup.dismiss()
            self.event.cancel()   
            errCode = self.result.get("ErrCode")
            if errCode != 0:
                errDesc = self.result.get("ErrDesc")
                self.loginFlag = False
                self.app.showErrorView(False, errCode, errDesc)
            else:
                self.loginFlag = True
                self.resultFunc(self.result)

    def _openFunc(self, instance):
        self.event = Clock.schedule_interval(self._result_check, .0005)
