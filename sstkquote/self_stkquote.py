# -*- coding: utf-8 -*-

import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(".." + os.sep)
import abxtoolkit

abxtoolkit.load_ini(abxtoolkit.ABX_MODE.AP)
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

import time
import threading

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty

import sconsts as CONSTS
from selements import SLabel, SInfoButton, STextInput, SPopup
from stkquote import StkQuote
from self_stksetting import SelfStkSetting
import sutil

stkBase_col_obj = abxtoolkit.stkBaseInfo_columns_sets()
stkRef_col_obj =  abxtoolkit.stkInfo_columns_sets()
trade_col_obj =   abxtoolkit.trade_columns_sets()
order1_col_obj =  abxtoolkit.order_1_columns_sets()
others_col_obj = abxtoolkit.others_columns_sets()

with open(os.path.join(os.path.dirname(__file__), "self_stkquote.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

NUM_PER_PAGE = 15 #一頁筆數
DEFAULT_FGCOLOR = "#000000" #黑色
DEFAULT_BGCOLOR = "#FFFFFF" #白色
DEFAULT_UPCOLOR = "#FF0000" #紅色
DEFAULT_DOWNCOLOR = "#00FF00" #綠色

class SSelfDropDown(DropDown):
    pass

class SelfStkQuote(BoxLayout):
    
    body_layout = ObjectProperty(None)
    content_layout = ObjectProperty(None)
    selfgroup_id = ObjectProperty(None)
    page_id = ObjectProperty(None)
    totalpage_id = ObjectProperty(None)
    prepage_id = ObjectProperty(None)
    nextpage_id = ObjectProperty(None)
    fieldRight_id = ObjectProperty(None)
    fieldLeft_id = ObjectProperty(None)
    selfgroup_index = 0
    selfStkList = []
    
    def __init__(self, paramDict, **kwargs):
        super(SelfStkQuote, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        
        self.quoteDataDict = {}
        self.selfDict = {}
        self.selfDropDown = SSelfDropDown()
        self.dropDownDict = {}
        firstRecord = True
        selfGroupList = None
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "self_stkquote.ini")
        alist = sutil.getListFromFile(filePath)
        for astr in alist:
            selfGroupList = astr.strip().split(",")
            if len(selfGroupList) < 3:
                continue
            if firstRecord:
                firstRecord = False
                self.selfgroup_id.text = selfGroupList[1]
                self.selfgroup_index = int(selfGroupList[0])
            self.selfDict[int(selfGroupList[0])] = selfGroupList
            abtn = SInfoButton(extra_info=int(selfGroupList[0]), text=selfGroupList[1])
            abtn.size_hint_y = None
            abtn.height = 30
            abtn.bind(on_release=self.selfDropDown.select)
            self.selfDropDown.add_widget(abtn)
            self.dropDownDict[str(abtn.extra_info)] = abtn
            
        self.selfgroup_id.bind(on_release=self.selfDropDown.open)
        self.selfDropDown.bind(on_select=self.selfSelect)

        self.stkidList = []
        self.num_per_page = NUM_PER_PAGE
        self.page_num = 1
        self.max_page_num = 1

        self.page_id.bind(on_text_validate=self._on_page_id_enter)
        
        headDict = {}
        headDict["id"] = "股票代碼"#SID
        headDict["name"] = "股票名稱"#SNT
        headDict["TT"] = "成交時間"
        headDict["TP"] = "成交價"
        headDict["TV"] = "成交量"
        headDict["YP"] = "昨收價"
        headDict["UD"] = "漲跌"
        headDict["USP"] = "漲停價"
        headDict["DSP"] = "跌停價"
        headDict["OP"] = "開盤價"
        headDict["HP"] = "最高價"
        headDict["LP"] = "最低價"
        headDict["BP"] = "買進"
        headDict["AP"] = "賣出"
        self.stkquote = StkQuote({CONSTS.S_APP:self,'headDict':headDict,'dispIdName':True})
        
        self.body_layout.remove_widget(self.content_layout)
        self.content_layout = self.stkquote
        self.content_layout.size_hint = (1, 1)
        self.body_layout.add_widget(self.content_layout)
        
        Clock.schedule_once(self.doQuoteStart, .5) #此段用意為讓畫面先顯示出來，再做後續的動作
    
    def selfSelect(self, instance, atext):
        self.selfgroup_id.text = atext.text
        self.selfgroup_index = atext.extra_info        
        self.stkquote.clearQuote() #變更自選組合，先清掉之前的畫面        
        selfStkListStr = self.selfDict.get(self.selfgroup_index)[2] #取得新的自選組合
        if selfStkListStr == "" or len(selfStkListStr) == 0:
            self.selfStkList = []
        else:
            self.selfStkList = selfStkListStr.split("|")

        self._calcPageInfo()
        self.subscribeQuote() #重新訂閱股票

    def _stkSetting(self):
        if len(self.app.stkNameDict) == 0:
            self.doQueryStktbl()
        else:
            refParam = {}
            refParam[CONSTS.S_APP] = self.app
            refParam["SelfGroupIndex"] = self.selfgroup_index
            refParam["SelfGroupName"] = self.selfgroup_id.text
            refParam["SelfStkList"] = list(self.selfStkList)
            stcLayout = SelfStkSetting(refParam)
            self.stcLayout = stcLayout
            self.self_setting_popup = SPopup(title="自選設定", content=stcLayout,
                size_hint=(None, None), size=(360, 480), auto_dismiss=False)
            stcLayout.ensurebtn_id.bind(on_press=self._changeGroup)
            stcLayout.cancelbtn_id.bind(on_press=self._self_setting_popup_dismiss)
            self.self_setting_popup.title_font = CONSTS.FONT_NAME
            self.self_setting_popup.open()

    def doQueryStktbl(self):
        contentLayout = BoxLayout()
        contentLayout.orientation = "vertical"
        contentLayout.size_hint = (1, 1)
        contentLabel = SLabel(text="  股名檔下載中...", size_hint=(1, .8))
        contentLayout.add_widget(contentLabel)
        
        sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        self.result = None
        self.ss_popup = SPopup(title=sysConfDict.get("MSG_TITLE"), content=contentLayout,
                size_hint=(None, None), size=(160, 120), auto_dismiss=False)
        self.ss_popup.title_font = CONSTS.FONT_NAME
        self.ss_popup.bind(on_open=self.ss_open)
        Clock.schedule_once(self.doQueryStktblStart)
    
    def doQueryStktblStart(self, instance):
        self.ss_popup.open()
        threading.Thread(target=self.toolkitQueryStktbl).start()
        
    def toolkitQueryStktbl(self):
        qdict = {}
        qdict['PinyinType'] = "1"
        qdict['LanguageID'] = "T"
        qdict['ExchangeID'] = "TW"
        self.result = abxtoolkit.query_stktbl1(qdict)
        
    def doQueryStktbl_check(self, dt):
        if self.result != None:
            self.ss_popup.dismiss()
            self.event.cancel()            
            errCode = self.result.get("ErrCode")
            if errCode != 0:
                errDesc = self.result.get("ErrDesc")
                self.app.showMixedMsg(errCode, errDesc)
            else:
                self.finishedQueryStktbl()

    def ss_open(self, instance):
        self.event = Clock.schedule_interval(self.doQueryStktbl_check, .0005)

    def finishedQueryStktbl(self):
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "rowdata" + os.sep + "stktbl1TTW.dat")
        alist = sutil.getListFromFile(filePath)
        alist.pop(0)
        tmpList = None
        for astr in alist:
            if astr == "" or len(astr) == 0:
                continue
            tmpList = astr.strip().split("|")
            if len(tmpList) < 2:
                continue
            self.app.stkNameDict[tmpList[0]] = tmpList[1]
        
        refParam = {}
        refParam[CONSTS.S_APP] = self.app
        refParam["SelfGroupIndex"] = self.selfgroup_index
        refParam["SelfGroupName"] = self.selfgroup_id.text
        refParam["SelfStkList"] = list(self.selfStkList)
        stcLayout = SelfStkSetting(refParam)
        self.stcLayout = stcLayout
        self.self_setting_popup = SPopup(title="自選設定", content=stcLayout,
            size_hint=(None, None), size=(360, 480), auto_dismiss=False)
        stcLayout.ensurebtn_id.bind(on_press=self._changeGroup)
        stcLayout.cancelbtn_id.bind(on_press=self._self_setting_popup_dismiss)
        self.self_setting_popup.title_font = CONSTS.FONT_NAME
        self.self_setting_popup.open()

    def _self_setting_popup_dismiss(self, instance):
        self.self_setting_popup.dismiss()
        self.self_setting_popup.clear_widgets()
        
    def _changeGroup(self, instance):
        self.stcLayout.saveData()
        self._self_setting_popup_dismiss(instance)
        selfgroup_index = self.stcLayout.selfgroup_index
        selfgroup_name = self.stcLayout.selfgroup_name_id.text
        self.selfgroup_id.text = selfgroup_name
        adropdownBtn = self.dropDownDict[str(selfgroup_index)]
        adropdownBtn.text = selfgroup_name
        self.selfStkList = list(self.stcLayout.selfStkList)
        self.selfDict[selfgroup_index][1] = selfgroup_name
        stkListStr = ""
        for stkId in self.selfStkList:
            stkListStr += stkId + "|"
        if len(stkListStr) != 0:
            stkListStr = stkListStr[0:-1]
        self.selfDict[selfgroup_index][2] = stkListStr
        self.stkquote.clearQuote() #變更自選組合，先清掉之前的畫面 
        self.subscribeQuote() #重新訂閱股票

    def doQuoteStart(self, instance):
        threading.Thread(target=self.doQuote).start()

    def _on_page_id_enter(self, instance):
        topage_num = int(instance.text)
        pageNum = 0
        if topage_num < 1:
            pageNum = 1
        elif topage_num > self.max_page_num:
            pageNum = self.max_page_num
        else:
            pageNum = topage_num
        self.page_id.text = str(pageNum)
        if pageNum == self.page_num:
            return

        self.page_num = pageNum

        self.stkquote.clearQuote() #變更自選組合，先清掉之前的畫面
        self.subscribeQuote() #重新訂閱股票

    def _onChangePage(self, changePage):
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
        
        self.prepage_id.disabled = True
        self.nextpage_id.disabled = True

        self.stkquote.clearQuote() #變更自選組合，先清掉之前的畫面 
        self.subscribeQuote() #重新訂閱股票

        self.prepage_id.disabled = False
        self.nextpage_id.disabled = False

    def _calcPageInfo(self):
        stkListNum = len(self.selfStkList)
        if stkListNum == 0:
            self.prepage_id.disabled = True
            self.nextpage_id.disabled = True
            self.fieldRight_id.disabled = True
            self.fieldLeft_id.disabled = True
            self.page_id.text = "1"
            self.page_id.disabled = True
            self.totalpage_id.text = "1"                
            return

        self.max_page_num = int(stkListNum / self.num_per_page )
        tmpNum = stkListNum % self.num_per_page
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
        
        if self.max_page_num == 1:
            self.page_id.disabled = True
        else:
            self.page_id.disabled = False
        self.fieldRight_id.disabled = False
        self.fieldLeft_id.disabled = False

    def _onFieldShift(self, changePage):
        if changePage == "fieldRight":
            self.fieldRight_id.disabled = True
            self.stkquote.nextField()
            self.fieldRight_id.disabled = False
        elif changePage == "fieldLeft":
            self.fieldLeft_id.disabled = True
            self.stkquote.previousField()
            self.fieldLeft_id.disabled = False

    def my_callback_func(self, mesgtype, stkid, data):
        if stkid not in self.selfStkList:
            return
        if mesgtype == abxtoolkit.WATCH_TYPE.stkBase:
            aQuoteDict = self.quoteDataDict.get(stkid)
            if aQuoteDict == None:
                aQuoteDict = {}
                self.quoteDataDict[stkid] = aQuoteDict
            quoteList = []
            aDict = {}
            if "SID" in data:
                aDict["id"] = [data["SID"], DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
                aQuoteDict["id"] = data["SID"]
            if "SNT" in data:
                aDict["name"] = [data["SNT"], DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
                aQuoteDict["id"] = data["SNT"]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)
        if mesgtype == abxtoolkit.WATCH_TYPE.stkInfo:
            aQuoteDict = self.quoteDataDict.get(stkid)
            if aQuoteDict == None:
                aQuoteDict = {}
                self.quoteDataDict[stkid] = aQuoteDict
            quoteList = []
            aDict = {}
            aDict["id"] = [stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "YP" in data:
                aDict["YP"] = ["{:.2f}".format(data["YP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
                aQuoteDict["YP"] = data["YP"]
                self._calcUpDown(stkid, aDict)
            if "USP" in data:
                aDict["USP"] = ["{:.2f}".format(data["USP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "DSP" in data:
                aDict["DSP"] = ["{:.2f}".format(data["DSP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)
        if mesgtype == abxtoolkit.WATCH_TYPE.trade:
            aQuoteDict = self.quoteDataDict.get(stkid)
            if aQuoteDict == None:
                aQuoteDict = {}
                self.quoteDataDict[stkid] = aQuoteDict            
            quoteList = []
            aDict = {}
            aDict["id"] = [stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "TT" in data:
                aDict["TT"] = [sutil.formatTime(data["TT"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "TP" in data:
                aDict["TP"] = ["{:.2f}".format(data["TP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
                aQuoteDict["TP"] = data["TP"]
                self._calcUpDown(stkid, aDict)
            if "TV" in data:
                aDict["TV"] = [str(data["TV"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)
        if mesgtype == abxtoolkit.WATCH_TYPE.others:
            quoteList = []
            aDict = {}
            aDict["id"] = [stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "OP" in data:
                aDict["OP"] = ["{:.2f}".format(data["OP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "HP" in data:
                aDict["HP"] = ["{:.2f}".format(data["HP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "LP" in data:
                aDict["LP"] = ["{:.2f}".format(data["LP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)
        if mesgtype == abxtoolkit.WATCH_TYPE.order_1:
            quoteList = []
            aDict = {}
            aDict["id"] = [stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "BP" in data:
                aDict["BP"] = ["{:.2f}".format(data["BP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "AP" in data:
                aDict["AP"] = ["{:.2f}".format(data["AP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)

    def _calcUpDown(self, stkid, aDict):
        aQuoteDict = self.quoteDataDict.get(stkid)
        yp = aQuoteDict.get("YP") #昨收價
        if yp == None:
            return
        tp = aQuoteDict.get("TP") #成交價
        if tp == None:
            return
        upDown = tp - yp
        fgColor = None
        if upDown < 0:
            fgColor = DEFAULT_DOWNCOLOR
        elif upDown > 0:
            fgColor = DEFAULT_UPCOLOR
        else:
            fgColor = DEFAULT_FGCOLOR
        aDict["UD"] = ["{:.2f}".format(upDown), fgColor, DEFAULT_BGCOLOR]
        aDict["TP"] = ["{:.2f}".format(tp), fgColor, DEFAULT_BGCOLOR]
        
    def doQuote(self):
        
        r = abxtoolkit.add_listener([self.my_callback_func])

        if self.selfgroup_index not in self.selfDict:
            return
        selfStkListStr = self.selfDict.get(self.selfgroup_index)[2]
        if selfStkListStr == "" or len(selfStkListStr) == 0:
            self._calcPageInfo()
            return
        
        self.selfStkList = selfStkListStr.split("|")
        self._calcPageInfo()
        self.subscribeQuote()
        
    def subscribeQuote(self):

        if len(self.selfStkList) == 0:
            quote_condition = []
        else:
            startIdx = (self.page_num - 1) * NUM_PER_PAGE
            endIdx = self.page_num * NUM_PER_PAGE
            if endIdx > len(self.selfStkList):
                endIdx = len(self.selfStkList)
            quote_condition = []
            for idx in range(startIdx, endIdx):
                stkId = self.selfStkList[idx]
                if stkId == "" or len(stkId) == 0:
                    continue
                a_sub_stock = abxtoolkit.abx_quote_condition()
                a_sub_stock.stockID = stkId
                a_sub_stock.quoteID = ['stkBase', 'stkInfo', 'order_1', 'trade', 'others']
                quote_condition.append(a_sub_stock)

        r = abxtoolkit.subscribe_quote(quote_condition)