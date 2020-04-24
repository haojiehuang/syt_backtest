# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

import sconsts as CONSTS
import sutil
from selements import SLabel, SButton, STextInput
from strend_graph import STrendGraph

with open(os.path.join(os.path.dirname(__file__), "sbt_graph.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())
    
class SbtGraph(BoxLayout):
    
    body_layout = ObjectProperty(None)
    content_layout = ObjectProperty(None)
    bt_file_id = ObjectProperty(None)
    page_id = ObjectProperty(None)
    totalpage_id = ObjectProperty(None)
    prepage_id = ObjectProperty(None)
    nextpage_id = ObjectProperty(None)
    bigsize_id = ObjectProperty(None)
    smallsize_id = ObjectProperty(None)
    popup = ObjectProperty(None)
    contentLayout = None
    
    kwargs = {}
    
    MAX_NUM_PER_PAGE = 600
    MIN_NUM_PER_PAGE = 100
    UP_DOWN_NUM = 100
    
    charttype = 1
    data_num = 0
    num_per_page = MIN_NUM_PER_PAGE
    page_num = 1
    max_page_num = 1
    decimalShow = 0
    firstFlag = True

    def __init__(self, paramDict, **kwargs):
        super(SbtGraph, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.btmenu = self.paramDict.get(CONSTS.S_BTMENU)
        trendGraphDict = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "trend_graph.ini"))        
        self.MAX_NUM_PER_PAGE = int(trendGraphDict.get("MAX_NUM_PER_PAGE"))
        self.MIN_NUM_PER_PAGE = int(trendGraphDict.get("MIN_NUM_PER_PAGE"))
        self.UP_DOWN_NUM = int(trendGraphDict.get("UP_DOWN_NUM"))
        self.num_per_page = int(trendGraphDict.get("DEFAULT_NUM_PER_PAGE"))

        self.dataList = self.paramDict.get("datalist")
        self.fileList = self.paramDict.get("fileList")
        self.data_num = len(self.dataList)

        self.firstFlag = True
        self.calcPageInfo()
        
        self.page_id.bind(on_text_validate=self.on_page_id_enter)
        self.bt_file_id.text = "[b]" + self.fileList[0] + "[/b]"
        
    def on_page_id_enter(self, instance):
        topage_num = int(instance.text)
        if topage_num < 1:
            self.page_num = 1
        elif topage_num > self.max_page_num:
            self.page_num = self.max_page_num
        else:
            self.page_num = topage_num
        self.page_id.text = str(self.page_num)
        
        self.addSTrendGraph()

    def getShowDataList(self, pageNum):
        
        startIdx = int((pageNum - 1) * self.num_per_page)
        endIdx = int(pageNum * self.num_per_page)
        if endIdx > self.data_num:
            endIdx = self.data_num
        tarList = []
        for i in range(startIdx, endIdx):
            tarList.append(self.dataList[i])
        
        return tarList
    
    def calcPageInfo(self):
        
        if self.num_per_page == self.MIN_NUM_PER_PAGE:
            self.bigsize_id.disabled = True
        else:
            self.bigsize_id.disabled = False
        if self.num_per_page == self.MAX_NUM_PER_PAGE:
            self.smallsize_id.disabled = True
        else:
            self.smallsize_id.disabled = False
        self.max_page_num = int(self.data_num / self.num_per_page )
        tmpNum = self.data_num % self.num_per_page
        if tmpNum != 0:
            self.max_page_num += 1
        if self.max_page_num == 1:
            self.prepage_id.disabled = True
            self.nextpage_id.disabled = True
        else:
            self.prepage_id.disabled = False
            self.nextpage_id.disabled = False
        if self.page_num > self.max_page_num:
            self.page_num = self.max_page_num

        self.page_id.text = str(self.page_num) 
        self.totalpage_id.text = str(self.max_page_num)
        
        self.addSTrendGraph()

    def addSTrendGraph(self):
        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict.get(key)
        refDict["ticknum"] = self.num_per_page        
        refDict['datalist'] = self.getShowDataList(self.page_num)
        self.body_layout.remove_widget(self.content_layout)
        self.content_layout.clear_widgets()
        self.content_layout = STrendGraph(refDict)
        self.content_layout.size_hint = (1, 1)
        self.body_layout.add_widget(self.content_layout, index=0)
        
    def onChangePage(self, changePage):
        if changePage == "NextPage":
            if self.page_num == self.max_page_num:
                self.page_num = 1
            else:
                self.page_num += 1
        elif changePage == "PrePage":
            if self.page_num == 1:
                self.page_num = self.max_page_num
            else:
                self.page_num -= 1
        else:
            topage_num = int(changePage)
            if topage_num < 1:
                self.page_num = 1
            elif topage_num > self.max_page_num:
                self.page_num = self.max_page_num
            self.topage_txt = str(self.page_num)

        self.page_id.text = str(self.page_num)
        
        self.addSTrendGraph()

    def onChangeDrawSize(self, changeSize):
        if changeSize == "bigSize":
            self.num_per_page -= self.UP_DOWN_NUM
        elif changeSize == "smallSize":
            self.num_per_page += self.UP_DOWN_NUM
        else:
            return

        self.calcPageInfo()