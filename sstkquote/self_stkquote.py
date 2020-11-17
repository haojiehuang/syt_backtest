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
from sgw_popup import SGwPopup
from selements import SLabel, SInfoButton, STextInput, SPopup
from stkquote import StkQuote
from self_stksetting import SelfStkSetting
from self_fieldsetting import SFieldSetting
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
        
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "stkfields_setting.ini")
        alist = sutil.getListFromFile(filePath)
        headDefineDict = {}
        for astr in alist:
            astrList = astr.strip().split(",")
            if len(astrList) < 2:
                continue
            headDefineDict[astrList[0]] = astrList[1]
        headDict = {}
        headDict["id"] = headDefineDict.get("id")#SID
        headDict["name"] = headDefineDict.get("name")#SNT
        seqStr = headDefineDict.get("_SEQ_")
        seqStrList = seqStr.split("|")
        for headId in seqStrList:
            headDict[headId] = headDefineDict.get(headId)
        self.stkquote = StkQuote({CONSTS.S_APP:self.app,'headDict':headDict,'dispIdName':True})
        
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
            self._doQueryStktbl()
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

    def _fieldsSetting(self):
        refParam = {}
        refParam[CONSTS.S_APP] = self.app
        sfsLayout = SFieldSetting(refParam)
        self.sfsLayout = sfsLayout
        self.self_fieldsetting_popup = SPopup(title="欄位排序", content=sfsLayout,
            size_hint=(None, None), size=(300, 480), auto_dismiss=False)
        sfsLayout.ensurebtn_id.bind(on_press=self._changeFields)
        sfsLayout.closebtn_id.bind(on_press=self.self_fieldsetting_popup.dismiss)
        self.self_fieldsetting_popup.title_font = CONSTS.FONT_NAME
        self.self_fieldsetting_popup.open()

    def _doQueryStktbl(self):

        gwParam = {}
        gwParam['PinyinType'] = "1"
        gwParam['LanguageID'] = "T"
        gwParam['ExchangeID'] = "TW"

        sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        refParam = {}
        refParam["CONSTS.S_APP"] = self.app
        refParam["TitleMsg"] = sysConfDict.get("MSG_TITLE")
        refParam["InfoMsg"] = "  股名檔下載中..."
        refParam["PopupSize"] = (160, 120)
        refParam["GwParam"] = gwParam
        refParam["GwFunc"] = abxtoolkit.query_stktbl1
        refParam["ResultFunc"] = self._finishedQueryStktbl

        sgwPopup = SGwPopup(refParam)
        sgwPopup.processEvent()

    def _finishedQueryStktbl(self, gwResult):
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
        self._calcPageInfo()
        self.subscribeQuote() #重新訂閱股票

    def _changeFields(self, instance):
        self.sfsLayout.saveData()
        self.self_fieldsetting_popup.dismiss(instance)

        self.stkquote.resetFieldsSeq(self.sfsLayout.fieldSeqList) #變更欄位順序

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

    def my_callback_func(self, a_result):
        if a_result.errcode != 0:
            self.app.showErrorView(False, a_result.errcode, a_result.errdes)
            return
        if a_result.stkid == None:
            return
        if a_result.stkid not in self.selfStkList:
            return
        if a_result.mesgtype == abxtoolkit.WATCH_TYPE.stkBase:
            aQuoteDict = self.quoteDataDict.get(a_result.stkid)
            if aQuoteDict == None:
                aQuoteDict = {}
                self.quoteDataDict[a_result.stkid] = aQuoteDict
            quoteList = []
            aDict = {}
            baseList = []
            baseDict = {}
            aDict["id"] = [a_result.stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            baseDict["id"] = a_result.stkid
            if "SID" in a_result.data:
                aDict["id"] = [a_result.data["SID"], DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
                aQuoteDict["id"] = a_result.data["SID"]
            if "SNT" in a_result.data:
                aDict["name"] = [a_result.data["SNT"], DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
                aQuoteDict["name"] = a_result.data["SNT"]
                baseDict["name"] = a_result.data["SNT"]
            if "OT" in a_result.data:
                baseDict["OT"] = a_result.data["OT"]
            if "CloseT" in a_result.data:
                baseDict["CloseT"] = a_result.data["CloseT"]
            if "Dec" in a_result.data:
                baseDict["Dec"] = a_result.data["Dec"]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)
            baseList.append(baseDict)
            self.stkquote.updateBaseQuote(baseList)
        if a_result.mesgtype == abxtoolkit.WATCH_TYPE.stkInfo:
            aQuoteDict = self.quoteDataDict.get(a_result.stkid)
            if aQuoteDict == None:
                aQuoteDict = {}
                self.quoteDataDict[a_result.stkid] = aQuoteDict
            quoteList = []
            aDict = {}
            baseList = []
            baseDict = {}
            aDict["id"] = [a_result.stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            baseDict["id"] = a_result.stkid
            if "YP" in a_result.data:
                aDict["YP"] = ["{:.2f}".format(a_result.data["YP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
                aQuoteDict["YP"] = a_result.data["YP"]
                self._calcUpDown(a_result.stkid, aDict)
                baseDict["YP"] = a_result.data["YP"]
            if "USP" in a_result.data:
                aDict["USP"] = ["{:.2f}".format(a_result.data["USP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "DSP" in a_result.data:
                aDict["DSP"] = ["{:.2f}".format(a_result.data["DSP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "LTD" in a_result.data:
                baseDict["LTD"] = a_result.data["LTD"]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)
            baseList.append(baseDict)
            self.stkquote.updateBaseQuote(baseList)
        if a_result.mesgtype == abxtoolkit.WATCH_TYPE.trade:
            aQuoteDict = self.quoteDataDict.get(a_result.stkid)
            if aQuoteDict == None:
                aQuoteDict = {}
                self.quoteDataDict[a_result.stkid] = aQuoteDict            
            quoteList = []
            aDict = {}
            aDict["id"] = [a_result.stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "TT" in a_result.data:
                aDict["TT"] = [sutil.formatTime(a_result.data["TT"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "TP" in a_result.data:
                aDict["TP"] = ["{:.2f}".format(a_result.data["TP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
                aQuoteDict["TP"] = a_result.data["TP"]
                self._calcUpDown(a_result.stkid, aDict)
            if "TV" in a_result.data:
                aDict["TV"] = [str(a_result.data["TV"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)
        if a_result.mesgtype == abxtoolkit.WATCH_TYPE.others:
            quoteList = []
            aDict = {}
            aDict["id"] = [a_result.stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "OP" in a_result.data:
                aDict["OP"] = ["{:.2f}".format(a_result.data["OP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "HP" in a_result.data:
                aDict["HP"] = ["{:.2f}".format(a_result.data["HP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "LP" in a_result.data:
                aDict["LP"] = ["{:.2f}".format(a_result.data["LP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            quoteList.append(aDict)
            self.stkquote.updateQuote(quoteList)
        if a_result.mesgtype == abxtoolkit.WATCH_TYPE.order_1:
            quoteList = []
            aDict = {}
            aDict["id"] = [a_result.stkid, DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "BP" in a_result.data:
                aDict["BP"] = ["{:.2f}".format(a_result.data["BP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "BV" in a_result.data:
                aDict["BV"] = [str(a_result.data["BV"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "AP" in a_result.data:
                aDict["AP"] = ["{:.2f}".format(a_result.data["AP"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]
            if "AV" in a_result.data:
                aDict["AV"] = [str(a_result.data["AV"]), DEFAULT_FGCOLOR, DEFAULT_BGCOLOR]            
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

    def closeStkQuote(self):

        abxtoolkit.remove_all_listener()
        
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
            subscribeList = []
            quote_condition = []
            for idx in range(startIdx, endIdx):
                stkId = self.selfStkList[idx]
                if stkId == "" or len(stkId) == 0:
                    continue
                a_sub_stock = abxtoolkit.abx_quote_condition()
                a_sub_stock.stockID = stkId
                a_sub_stock.quoteID = ['stkBase', 'stkInfo', 'order_1', 'trade', 'others']
                quote_condition.append(a_sub_stock)
                subscribeList.append(stkId)

            self.stkquote.setStkList(self.selfStkList)
            self.stkquote.setSubscribeList(subscribeList)
            self.stkquote.setGroupName(self.selfgroup_id.text)

        r = abxtoolkit.subscribe_quote(quote_condition)