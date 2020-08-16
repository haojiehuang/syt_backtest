# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex as colorHex

from selements import SLabel, SButton, SButton2, SHeadLabel, SContentLabel, SBoxLayout
from selements import SPopup, STableGridLayout, STableBoxLayout, STableScrollView, SFileInputDialog
from strade_graph import STradeGraph
import sconsts as CONSTS
import sutil

userConf = sutil.getDictFromFile(os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini"))
export_dir = userConf.get("EXPORT_DIR")
if export_dir == None:
    export_dir = os.path.join(os.path.dirname(__file__), ".." + os.sep + "export")
else:
    if not os.path.exists(os.path.abspath(export_dir)):
        export_dir = os.path.join(os.path.dirname(__file__), ".." + os.sep + "export")
if not os.path.exists(os.path.abspath(export_dir)):
    os.mkdir(os.path.abspath(export_dir))
export_path = os.path.abspath(export_dir)    

LABEL_COLOR = "#000000"
NEGATIVE_COLOR = "#FF0000"
GRID_HEIGHT = 30

with open(os.path.join(os.path.dirname(__file__), "stradereport.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class SRuleDropDown(DropDown):
    pass
                        
class SReportFile(BoxLayout):
    
    stkname_id = ObjectProperty(None)
    strategy_id = ObjectProperty(None)
    period_id = ObjectProperty(None)
    filename_id = ObjectProperty(None)
    ensurebtn_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    
    def __init__(self, paramDict, **kwargs):
        super(SReportFile, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        self.sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        self.filename_id.bind(focus=self.onFocus)
    
    def onFocus(self, instance, value):
        if value:
            content = SFileInputDialog(load=self.loadDir, cancel=self.dismiss_popup)
            content.filechooser_id.path = export_path
            content.filename_id.text = ".csv"
            popupTitle = self.sysConfDict.get("MSG_DOWNLOAD_FILE")
            self._popup = SPopup(title=popupTitle, content=content, size_hint=(0.9, 0.9), title_font=CONSTS.FONT_NAME)
            self._popup.open()
    
    def dismiss_popup(self):
        self._popup.dismiss()
    
    def loadDir(self, path, filename):
        self._popup.dismiss()
        export_path = path
        self.filename_id.text = filename

        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "user.ini")
        userConf = sutil.getDictFromFile(filePath)
        userConf["EXPORT_DIR"] = path
        with open(filePath, 'w', encoding = 'utf-8') as f:
            for key in userConf.keys():
                value = userConf.get(key)
                aStr = key + "=" + value + "\n"
                f.write(aStr)
    
class STradeReport(BoxLayout):

    body_layout = ObjectProperty(None)
    rule_id = ObjectProperty(None)
    reportFile_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
        
    def __init__(self, paramDict, **kwargs):
        super(STradeReport, self).__init__(**kwargs)
        
        self.paramDict = paramDict
        self.app = self.paramDict.get(CONSTS.S_APP)
        self.dataList = self.paramDict.get("dataList")
        self.fileList = self.paramDict.get("fileList")
        self.ruleDict = {}
        
        self.ruleDropDown = SRuleDropDown()
        firstRecord = True
        ruleList = None
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "tradecost.ini")
        alist = sutil.getListFromFile(filePath)
        for astr in alist:
            ruleList = astr.strip().split(",")
            if len(ruleList) < 3:
                continue
            if firstRecord:
                firstRecord = False
                self.rule_id.text = ruleList[0]
            self.ruleDict[ruleList[0]] = ruleList
            abtn = SButton(text=ruleList[0])
            abtn.size_hint_y = None
            abtn.height = 30
            abtn.bind(on_release=self.ruleDropDown.select)
            self.ruleDropDown.add_widget(abtn)
            
        self.rule_id.bind(on_release=self.ruleDropDown.open)
        self.ruleDropDown.bind(on_select=self.ruleSelect)
        
        self.bookmarkHead = BoxLayout(size_hint=(1, .06), orientation="horizontal") #頁籤
        self.tradeAnalyze = BoxLayout(size_hint=(1, .93), orientation="vertical") #交易分析
        self.tradeRecord = BoxLayout(size_hint=(1, .93), orientation="vertical") #交易記錄
        self.tlGraph = BoxLayout(size_hint=(1, .87), orientation="vertical") #交易記錄圖表
        self.monthReport = BoxLayout(size_hint=(1, .93), orientation="vertical") #月報酬率
        self.yearReport = BoxLayout(size_hint=(1, .93), orientation="vertical") #年報酬率
        self.now_bookmark = None
        self.now_bookmarkLayout = None

    def showSelectFile(self):
        mainContent = BoxLayout(size_hint=(1, 1), orientation="vertical")

        slview = STableScrollView()
        slview.size_hint = (1, None)
        slview.size = (250, 160)
        contentLayout = STableGridLayout(cols=1, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        contentLayout.bind(minimum_height=contentLayout.setter('height'))
        slview.add_widget(contentLayout)
        aLabel = None
        for aStr in self.fileList:
            aLabel = SLabel(text=aStr,size_hint=(1, None), height=30)
            aLabel.color = colorHex("#000000")
            contentLayout.add_widget(aLabel)
        showSelectFile_popup = SPopup(title="回測檔案", content=mainContent,
                size_hint=(None, None), size=(250, 250), auto_dismiss=False)
        showSelectFile_popup.title_font = CONSTS.FONT_NAME
        mainContent.add_widget(slview)
        closeBtn = SButton(text="關閉")
        closeBtn.bind(on_press=showSelectFile_popup.dismiss)
        mainContent.add_widget(closeBtn)
        showSelectFile_popup.open()
        
    def ruleSelect(self, instance, atext):
        self.rule_id.text = atext.text

    def analyzeBTData(self):#分析回測資料
        
        self.reportFile_id.disabled = False

        self.allTradeList = []#儲存分析結果之List物件
        
        self.volumeNum = int(self.ruleDict.get(self.rule_id.text)[1])
        tradeCost = float(self.ruleDict.get(self.rule_id.text)[2]) #交易手續費
        
        signalFlag = None #買賣訊號旗標，每完成一次交易要將旗標改為None
        signalNum = 0 #一次交易買或賣之次數，每完成一次交易要清為0
        tradeSum = 0.0 #一次交易之交易金額
        tradeCostSum = 0.0 #一次交易之交易手續費總和，每完成一次交易要清為0
        tradeList = None
        tradeDict = None
        tradeAmt = None
        tradeDate = None
        tradeTime = None
        tmpDict = None
        self.startDate = None
        self.endDate = None
        for adict in self.dataList:
            tradeDate = adict.get("date")
            if self.startDate == None:
                self.startDate = tradeDate
            self.endDate = tradeDate
            bs = adict.get("bs")
            if bs != "":
                bsprice = adict.get("bsprice")
                if bsprice == 0:
                    bsprice = adict.get("price")
                bsqty = adict.get("bsqty")
                tradeAmt = 1.0 * bsprice * self.volumeNum
                tradeTime = adict.get("time")
                tradeDict = {}
                tradeDict["bs"] = bs
                tradeDict["date"] = tradeDate
                tradeDict["time"] = tradeTime
                tradeDict["price"] = bsprice
                if signalFlag == None:
                    signalFlag = bs
                    #signalNum += 1
                    signalNum += bsqty
                    if bs == "B":
                        tradeSum = -1.0 * tradeAmt * bsqty
                    else:
                        tradeSum = 1.0 * tradeAmt * bsqty
                    tradeCostSum += tradeCost
                    tradeList = []
                    tradeDict["vol"] = bsqty
                    tradeDict["cost"] = tradeCost
                    tradeList.append(tradeDict)                    
                else:
                    if bs == signalFlag:
                        #signalNum += 1
                        signalNum += bsqty
                        if bs == "B":
                            tradeSum -= tradeAmt * bsqty
                        else:
                            tradeSum += tradeAmt * bsqty
                        tradeCostSum += tradeCost
                        tradeDict["vol"] = bsqty
                        tradeDict["cost"] = tradeCost
                        tradeList.append(tradeDict)                        
                    else:
                        tmpDict = {}
                        if bs == "B": #但signalFlag為S，完成一次交易，資料加入空單
                            tradeSum -= 1.0 * tradeAmt * signalNum
                            tmpDict["tradeType"] = "S" #空單
                        else: #但signalFlag為B，完成一次交易，資料加入多單
                            tradeSum += 1.0 * tradeAmt * signalNum
                            tmpDict["tradeType"] = "L" #多單
                        tradeCostSum += tradeCost
                        tradeDict["vol"] = signalNum
                        tradeDict["cost"] = tradeCost
                        tradeList.append(tradeDict)                        
                        tmpDict["tradeDate"] = tradeDate
                        tmpDict["tradeTime"] = tradeTime
                        tmpDict["tradeSum"] = tradeSum
                        tmpDict["tradeCost"] = tradeCostSum
                        tmpDict["tradeList"] = tradeList
                        self.allTradeList.append(tmpDict)

                        signalFlag = None
                        signalNum = 0
                        tradeCostSum = 0.0

        self.generateReportData()
        
        self.body_layout.clear_widgets()
        self.addBookmarkHead()
        self.addTradeAnalyze()
        self.addTradeList()
        self.addMonthReport()
        self.addYearReport()
        
    def generateReportData(self): #產生報表所需資料

        self.longNetProfit = 0.0 #多單淨利
        self.longEqualNum = 0 #多單無獲利也無虧損次數
        self.longProfitNum = 0 #多單獲利次數
        self.longProfitSum = 0.0 #多單獲利總額
        self.longLoseNum = 0 #多單虧損次數
        self.longLoseSum = 0.0 #多單虧損總額
        self.longMaxProfit = 0.0 #多單最大獲利
        self.longMaxLose = 0.0 #多單最大虧損
        self.longCostSum = 0.0 #多單總成本
        self.shortNetProfit = 0.0 #空單淨利
        self.shortEqualNum = 0 #空單無獲利也無虧損次數
        self.shortProfitNum = 0 #空單獲利次數
        self.shortProfitSum = 0.0 #空單獲利總額
        self.shortLoseNum = 0 #空單虧損次數
        self.shortLoseSum = 0.0 #空單虧損總額
        self.shortMaxProfit = 0.0 #空單最大獲利
        self.shortMaxLose = 0.0 #空單最大虧損
        self.shortCostSum = 0.0 #空單總成本
        self.shortEqualNum = 0 #空單持平次數
        self.longMonthDict = {}
        self.shortMonthDict = {}

        tradeCost = None
        longSum = None
        shortSum = None
        for tradeDict in self.allTradeList:
            tradeType = tradeDict.get("tradeType")
            tradeCost = tradeDict.get("tradeCost") #交易成本
            tradeDate = tradeDict.get("tradeDate")
            tradeMonth = int(int(tradeDate) / 100)
            if tradeType == "L": #多單
                alist = self.longMonthDict.get(tradeMonth)
                if alist == None:
                    alist = []
                alist.append(tradeDict)
                self.longMonthDict[tradeMonth] = alist
                longSum = tradeDict.get("tradeSum")
                self.longNetProfit += (longSum - tradeCost) #淨利需扣除交易成本
                if longSum < 0:
                    longSum = -1 * longSum
                    self.longLoseNum += 1
                    self.longLoseSum += longSum
                    if longSum > self.longMaxLose:
                        self.longMaxLose = longSum
                elif longSum > 0:
                    self.longProfitNum += 1
                    self.longProfitSum += longSum
                    if longSum > self.longMaxProfit:
                        self.longMaxProfit = longSum
                else:
                    self.longEqualNum += 1
                self.longCostSum += tradeCost
            else: #空單
                alist = self.shortMonthDict.get(tradeMonth)
                if alist == None:
                    alist = []
                alist.append(tradeDict)
                self.shortMonthDict[tradeMonth] = alist                
                shortSum = tradeDict.get("tradeSum")
                self.shortNetProfit += (shortSum - tradeCost) #淨利需扣除交易成本
                if shortSum < 0:
                    shortSum = -1 * shortSum
                    self.shortLoseNum += 1
                    self.shortLoseSum += shortSum
                    if shortSum > self.shortMaxLose:
                        self.shortMaxLose = shortSum
                elif shortSum > 0:
                    self.shortProfitNum += 1
                    self.shortProfitSum += shortSum
                    if shortSum > self.shortMaxProfit:
                        self.shortMaxProfit = shortSum
                else:
                    self.shortEqualNum += 1
                self.shortCostSum += tradeCost
        
        self.generateYearMonthData()
        self.generateYearMonthList()
        
    def generateYearMonthData(self):
        
        monthDict = {}
        longYearDict = {}
        shortYearDict = {}
        yearDict = {}
        yearInt = None
        monthRewardsSum = 0.0
        
        rewardsNum = 0
        rewardsSum = 0.0
        for monthKey in self.longMonthDict.keys():
            rewardsNum += 1
            alist = self.longMonthDict.get(monthKey)
            monthRewardsSum = 0.0
            for tradeDict in alist:
                tradeSum = tradeDict.get("tradeSum") # 交易金額
                monthRewardsSum += tradeSum            
            rewardsSum += monthRewardsSum
            monthSum = monthDict.get(monthKey)
            if monthSum == None:
                monthSum = 0
            monthSum += monthRewardsSum
            monthDict[monthKey] = monthSum
            yearKey = int(monthKey / 100)
            yearSum = longYearDict.get(yearKey)
            if yearSum == None:
                yearSum = 0.0
            yearSum += monthRewardsSum
            longYearDict[yearKey] = yearSum
            yearSum = yearDict.get(yearKey)
            if yearSum == None:
                yearSum = 0.0
            yearSum += monthRewardsSum
            yearDict[yearKey] = yearSum
        
        self.longRewardsAvg = 0.0
        if rewardsNum != 0:
            self.longRewardsAvg = rewardsSum / rewardsNum
            
        rewardsNum = 0
        rewardsSum = 0.0
        for monthKey in self.shortMonthDict.keys():
            rewardsNum += 1
            alist = self.shortMonthDict.get(monthKey)
            monthRewardsSum = 0.0
            for tradeDict in alist:
                tradeSum = tradeDict.get("tradeSum") # 交易金額
                monthRewardsSum += tradeSum
            rewardsSum += monthRewardsSum
            monthSum = monthDict.get(monthKey)
            if monthSum == None:
                monthSum = 0
            monthSum += monthRewardsSum
            monthDict[monthKey] = monthSum            
            yearKey = int(monthKey / 100)
            yearSum = shortYearDict.get(yearKey)
            if yearSum == None:
                yearSum = 0.0
            yearSum += monthRewardsSum
            shortYearDict[yearKey] = yearSum
            yearSum = yearDict.get(yearKey)
            if yearSum == None:
                yearSum = 0.0
            yearSum += monthRewardsSum
            yearDict[yearKey] = yearSum            
        
        self.shortRewardsAvg = 0.0
        if rewardsNum != 0:
            self.shortRewardsAvg = rewardsSum / rewardsNum        
        
        rewardsNum = 0
        rewardsSum = 0.0
        for monthKey in monthDict.keys():
            rewardsNum += 1
            rewardsSum += monthDict.get(monthKey)

        self.rewardsAvg = 0.0
        if rewardsNum != 0:
            self.rewardsAvg = rewardsSum / rewardsNum
        
        rewardsNum = 0
        rewardsSum = 0.0
        for yearKey in longYearDict.keys():
            rewardsNum += 1
            rewardsSum += longYearDict.get(yearKey)
        
        self.longYearAvg = 0.0
        if rewardsNum != 0:
            self.longYearAvg = rewardsSum / rewardsNum
            
        rewardsNum = 0
        rewardsSum = 0.0
        for yearKey in shortYearDict.keys():
            rewardsNum += 1
            rewardsSum += shortYearDict.get(yearKey)

        self.shortYearAvg = 0.0
        if rewardsNum != 0:
            self.shortYearAvg = rewardsSum / rewardsNum
            
        rewardsNum = 0
        rewardsSum = 0.0
        for yearKey in yearDict.keys():
            rewardsNum += 1
            rewardsSum += yearDict.get(yearKey)

        self.yearAvg = 0.0
        if rewardsNum != 0:
            self.yearAvg = rewardsSum / rewardsNum
    
    def generateYearMonthList(self):
        
        self.mlMonthDict = {}
        self.mlLongDict = {}
        self.mlShortDict = {}
        self.ylYearDict = {}
        self.ylLongDict = {}
        self.ylShortDict = {}        
        profitSum = None
        profitNum = None
        loseSum = None
        for monthKey in self.longMonthDict.keys():
            alist = self.longMonthDict.get(monthKey)
            tradeNum = len(alist)
            profitSum = 0
            profitNum = 0
            loseSum = 0
            for tradeDict in alist:
                tradeMon = tradeDict.get("tradeSum")
                if tradeMon < 0:
                    loseSum += -1 * tradeMon
                elif tradeMon > 0:
                    profitNum += 1
                    profitSum += tradeMon
            tmpList = []
            tmpList.append(tradeNum)
            tmpList.append(profitSum)
            tmpList.append(loseSum)
            tmpList.append(profitNum)
            self.mlMonthDict[monthKey] = monthKey
            self.mlLongDict[monthKey] = tmpList
            yearKey = int(monthKey / 100)
            tmpList = self.ylLongDict.get(yearKey)
            if tmpList == None:
                tmpList = []
                tmpList.extend([0, 0.0, 0.0, 0])
            tmpList[0] += tradeNum
            tmpList[1] += profitSum
            tmpList[2] += loseSum
            tmpList[3] += profitNum
            self.ylYearDict[yearKey] = yearKey
            self.ylLongDict[yearKey] = tmpList

        for monthKey in self.shortMonthDict.keys():
            alist = self.shortMonthDict.get(monthKey)
            tradeNum = len(alist)
            profitSum = 0
            profitNum = 0
            loseSum = 0
            for tradeDict in alist:
                tradeMon = tradeDict.get("tradeSum")
                if tradeMon < 0:
                    loseSum += -1 * tradeMon
                elif tradeMon > 0:
                    profitNum += 1
                    profitSum += tradeMon
            tmpList = []
            tmpList.append(tradeNum)
            tmpList.append(profitSum)
            tmpList.append(loseSum)
            tmpList.append(profitNum)
            self.mlMonthDict[monthKey] = monthKey
            self.mlShortDict[monthKey] = tmpList
            yearKey = int(monthKey / 100)
            tmpList = self.ylShortDict.get(yearKey)
            if tmpList == None:
                tmpList = []
                tmpList.extend([0, 0.0, 0.0, 0])
            tmpList[0] += tradeNum
            tmpList[1] += profitSum
            tmpList[2] += loseSum
            tmpList[3] += profitNum
            self.ylYearDict[yearKey] = yearKey
            self.ylShortDict[yearKey] = tmpList

    def reportFile(self):
        self.rfLayout = SReportFile(self.paramDict)
        self.rf_popup = SPopup(title="匯出檔案", content=self.rfLayout,
                size_hint=(None, None), size=(360, 320), auto_dismiss=False)
        self.rfLayout.ensurebtn_id.bind(on_press=self.reportFileEvent)
        self.rfLayout.closebtn_id.bind(on_press=self.rf_popup.dismiss)
        self.rf_popup.title_font = CONSTS.FONT_NAME
        self.rf_popup.open()

    def reportFileEvent(self, instance):
        stkName = self.rfLayout.stkname_id.text
        strategyName = self.rfLayout.strategy_id.text
        periodName = self.rfLayout.period_id.text
        fileName = self.rfLayout.filename_id.text
        if fileName == "":
            self.app.showErrorView(True, CONSTS.ERR_FILENAME_IS_SPACE)
            return
        self.rf_popup.dismiss()
        
        self.outputReportFile(stkName, strategyName, periodName, fileName)
        
        self.finishedPopup(fileName)

    def outputReportFile(self, stkName, strategyName, periodName, fileName):
        outList = []
        
        astr = "交易分析,,,,,,,\n"
        outList.append(astr)
        
        stkNameTar = ""
        if stkName != "":
            stkNameTar = "[" + stkName + "]"
        astr = "股票名稱," + stkNameTar + ",,,,,,\n"
        outList.append(astr)
        
        strategyNameTar = ""
        if strategyName != "":
            strategyNameTar = "[" + strategyName + "]"
        astr = "策略名稱," + strategyNameTar + ",,,,,,\n"
        outList.append(astr)
        
        astr = "回測區間,"
        if self.startDate == self.endDate:
            astr += str(self.startDate)
        else:
            astr += str(self.startDate) + "-" + str(self.endDate)
        astr += ",,,,,,\n"
        outList.append(astr)
        
        astr = "回測週期," + periodName + ",,,,,,\n"
        outList.append(astr)
        
        astr = ",所有交易,多單,空單,,,,\n"
        outList.append(astr)
        
        astr = "淨利,"
        netProfit = self.longNetProfit + self.shortNetProfit
        astr += ("{:.2f}".format(netProfit)).strip()
        astr += ","
        astr += ("{:.2f}".format(self.longNetProfit)).strip()
        astr += ","
        astr += ("{:.2f}".format(self.shortNetProfit)).strip()
        astr += ",,,,\n"
        outList.append(astr)
        
        longTradeNum = self.longProfitNum + self.longLoseNum + self.longEqualNum #多單交易次數
        shortTradeNum = self.shortProfitNum + self.shortLoseNum + self.shortEqualNum #空單交易次數
        tradeNum = longTradeNum + shortTradeNum #交易總次數
        astr = "交易總次數," + str(tradeNum) + "," + str(longTradeNum) + "," + str(shortTradeNum)
        astr += ",,,,\n"
        outList.append(astr)
        
        astr = "獲利交易次數," + str(self.longProfitNum + self.shortProfitNum)
        astr += "," + str(self.longProfitNum) + "," + str(self.shortProfitNum)
        astr += ",,,,\n"
        outList.append(astr)
        
        astr = "虧損交易次數," + str(self.longLoseNum + self.shortLoseNum)
        astr += "," + str(self.longLoseNum) + "," + str(self.shortLoseNum)
        astr += ",,,,\n"
        outList.append(astr)
        
        astr = "持平交易次數," + str(self.longEqualNum + self.shortEqualNum)
        astr += "," + str(self.longEqualNum) + "," + str(self.shortEqualNum)
        astr += ",,,,\n"
        outList.        append(astr)
        
        astr = "勝率,"
        apercent = 0.0
        if tradeNum != 0:
            apercent = 100.0 * (self.longProfitNum + self.shortProfitNum) / tradeNum #總勝率
        astr += ("{:3.2f}".format(apercent)).strip() + "%"
        astr += ","
        apercent = 0.0
        if longTradeNum != 0:
            apercent = 100.0 * self.longProfitNum / longTradeNum #多單勝率
        astr += ("{:3.2f}".format(apercent)).strip() + "%"
        astr += ","
        apercent = 0.0
        if shortTradeNum != 0:
            apercent = 100.0 * self.shortProfitNum / shortTradeNum #空單勝率
        astr += ("{:3.2f}".format(apercent)).strip() + "%"
        astr += ",,,,\n"
        outList.append(astr)
        
        astr = "平均獲利,"
        profitAverage = 0.0
        if (self.longProfitNum + self.shortProfitNum) != 0:
            profitAverage = 1.0 * (self.longProfitSum + self.shortProfitSum) / (self.longProfitNum + self.shortProfitNum) #平均獲利
        astr += ("{:.2f}".format(profitAverage)).strip()
        astr += ","
        longProfitAverage = 0.0
        if self.longProfitNum != 0:
            longProfitAverage = 1.0 * self.longProfitSum / self.longProfitNum #多單平均獲利
        astr += ("{:.2f}".format(longProfitAverage)).strip()
        astr += ","
        shortProfitAverage = 0.0
        if self.shortProfitNum != 0:
            shortProfitAverage = 1.0 * self.shortProfitSum / self.shortProfitNum #空單平均獲利
        astr += ("{:.2f}".format(shortProfitAverage)).strip()
        astr += ",,,,\n"
        outList.append(astr)        
        
        astr = "平均虧損,"
        loseAverage = 0.0
        if (self.longLoseNum + self.shortLoseNum) != 0:
            loseAverage = 1.0 * (self.longLoseSum + self.shortLoseSum) / (self.longLoseNum + self.shortLoseNum) #平均虧損
        astr += ("{:.2f}".format(loseAverage)).strip()
        astr += ","
        longLoseAverage = 0.0
        if self.longLoseNum != 0:
            longLoseAverage = 1.0 * self.longLoseSum / self.longLoseNum #多單平均虧損
        astr += ("{:.2f}".format(longLoseAverage)).strip()
        astr += ","
        shortLoseAverage = 0.0
        if self.shortLoseNum != 0:
            shortLoseAverage = 1.0 * self.shortLoseSum / self.shortLoseNum #空單平均虧損
        astr += ("{:.2f}".format(shortLoseAverage)).strip()
        astr += ",,,,\n"
        outList.append(astr)        
        
        astr = "平均獲利/平均虧損=盈虧比,"
        if loseAverage != 0:
            apercent = 1.0 * profitAverage / loseAverage #總盈虧比
            astr += ("{:.2f}".format(apercent)).strip()
        else:
            astr += "NA"
        astr += ","
        if longLoseAverage != 0:
            apercent = 1.0 * longProfitAverage / longLoseAverage #多單盈虧比
            astr += ("{:.2f}".format(apercent)).strip()
        else:
            astr += "NA"
        astr += ","
        if shortLoseAverage != 0:
            apercent = 1.0 * shortProfitAverage / shortLoseAverage #空單盈虧比
            astr += ("{:.2f}".format(apercent)).strip()
        else:
            astr += "NA"
        astr += ",,,,\n"
        outList.append(astr)
        
        profitPerDict = self.calcProfitPercent()

        avgProfitPer = profitPerDict.get("avgProfitPer") #平均報酬率
        lavgProfitPer = profitPerDict.get("lavgProfitPer") #多單平均報酬率
        savgProfitPer = profitPerDict.get("savgProfitPer") #空單平均報酬率
         
        astr = "平均報酬率,"
        astr += ("{:.2f}".format(avgProfitPer)).strip() + "%,"
        astr += ("{:.2f}".format(lavgProfitPer)).strip() + "%,"
        astr += ("{:.2f}".format(savgProfitPer)).strip() + "%,"
        astr += ",,,\n"
        outList.append(astr)
        
        astr = "最大獲利,"
        if self.longMaxProfit < self.shortMaxProfit: #最大獲利
            astr += ("{:.2f}".format(self.shortMaxProfit)).strip()
        else:
            astr += ("{:.2f}".format(self.longMaxProfit)).strip()
        astr += ","
        astr += ("{:.2f}".format(self.longMaxProfit)).strip() #多單最大獲利
        astr += ","
        astr += ("{:.2f}".format(self.shortMaxProfit)).strip() #空單最大獲利
        astr += ",,,,\n"
        outList.append(astr)
        
        maxProfitPer = profitPerDict.get("maxProfitPer") #最大報酬率
        lMaxProfitPer = profitPerDict.get("lMaxProfitPer") #多單最大報酬率
        sMaxProfitPer = profitPerDict.get("sMaxProfitPer") #空單最大報酬率
         
        astr = "最大報酬率,"
        astr += ("{:.2f}".format(maxProfitPer)).strip() + "%,"
        astr += ("{:.2f}".format(lMaxProfitPer)).strip() + "%,"
        astr += ("{:.2f}".format(sMaxProfitPer)).strip() + "%,"
        astr += ",,,\n"
        outList.append(astr)
        
        astr = "最大虧損,"
        if self.longMaxLose < self.shortMaxLose: #最大虧損
            astr += ("{:.2f}".format(self.shortMaxLose)).strip()
        else:
            astr += ("{:.2f}".format(self.longMaxLose)).strip()
        astr += ","
        astr += ("{:.2f}".format(self.longMaxLose)).strip() #多單最大虧損
        astr += ","
        astr += ("{:.2f}".format(self.shortMaxLose)).strip() #空單最大虧損
        astr += ",,,,\n"
        outList.append(astr)
        
        minProfitPer = profitPerDict.get("minProfitPer") #最小報酬率
        lMinProfitPer = profitPerDict.get("lMinProfitPer") #多單最小報酬率
        sMinProfitPer = profitPerDict.get("sMinProfitPer") #空單最小報酬率
         
        astr = "最小報酬率,"
        astr += ("{:.2f}".format(minProfitPer)).strip() + "%,"
        astr += ("{:.2f}".format(lMinProfitPer)).strip() + "%,"
        astr += ("{:.2f}".format(sMinProfitPer)).strip() + "%,"
        astr += ",,,\n"
        outList.append(astr)
        
        astr = "平均月報酬,"
        astr += ("{:.2f}".format(self.rewardsAvg)).strip()
        astr += ","
        astr += ("{:.2f}".format(self.longRewardsAvg)).strip()
        astr += ","
        astr += ("{:.2f}".format(self.shortRewardsAvg)).strip()
        astr += ",,,,\n"
        outList.append(astr)

        astr = "平均年報酬,"
        astr += ("{:.2f}".format(self.yearAvg)).strip()
        astr += ","
        astr += ("{:.2f}".format(self.longYearAvg)).strip()
        astr += ","
        astr += ("{:.2f}".format(self.shortYearAvg)).strip()
        astr += ",,,,\n"
        outList.append(astr)
        
        astr = "手續費+交易稅,"
        astr += ("{:.2f}".format(self.longCostSum + self.shortCostSum)).strip() #總成本
        astr += ","
        astr += ("{:.2f}".format(self.longCostSum)).strip() #多單成本
        astr += ","
        astr += ("{:.2f}".format(self.shortCostSum)).strip() #空單成本
        astr += ",,,,\n"
        outList.append(astr)
        
        astr = "交易記錄,,,,,,,\n"
        outList.append(astr)
        
        astr = "日期,訊號,時間,價格,數量,獲利金額,獲利%,\n"
        outList.append(astr)
        
        adict = None
        buyCostSum = None
        aVariable = None
        aPrice = None
        aVol = None
        for tradeDict in self.allTradeList:
            tradeList = tradeDict.get("tradeList")

            astr = ""
            buyCostSum = 0.0
            tradeListLen = len(tradeList)
            for i in range(tradeListLen):
                adict = tradeList[i]
                astr = sutil.formatDate(adict.get("date"))
                astr += ","
                bs = adict.get("bs")
                if bs == "B":
                    aPrice = adict.get("price")
                    aVol = adict.get("vol")
                    buyCostSum += 1.0 * aPrice * aVol * self.volumeNum
                    atext = "買進"
                else:
                    atext = "賣出"
                astr += atext
                astr += ","
                astr += sutil.formatTime(adict.get("time"))
                astr += ","
                astr += str(adict.get("price"))
                astr += ","
                astr += str(adict.get("vol"))
                if i != (tradeListLen - 1):
                    astr += ",,,\n"
                    outList.append(astr)
                else:
                    astr += ","

            tradeSum = tradeDict.get("tradeSum")
            astr += ("{:.2f}".format(tradeSum)).strip()
            astr += ","

            aVariable = 1.0 * tradeSum * 100 / buyCostSum
            astr += ("{:.2f}".format(aVariable)).strip() + "%"
            astr += ",\n"
            outList.append(astr)
        
        astr = "月報酬率,,,,,,,\n"
        outList.append(astr)
        
        astr = "期間,獲利,毛利,毛損,交易次數,勝率,,\n"
        outList.append(astr)
        
        keyList = self.mlMonthDict.keys()
        keyList = sorted(keyList)
        for monthKey in keyList:
            longList = self.mlLongDict.get(monthKey)
            if longList == None:
                longTradeNum = 0
                longProfitSum = 0
                longLoseSum = 0
                longProfitNum = 0
            else:
                longTradeNum = longList[0]
                longProfitSum = longList[1]
                longLoseSum = longList[2]
                longProfitNum = longList[3]
            shortList = self.mlShortDict.get(monthKey)
            if shortList == None:
                shortTradeNum = 0
                shortProfitSum = 0
                shortLoseSum = 0
                shortProfitNum = 0
            else:
                shortTradeNum = shortList[0]
                shortProfitSum = shortList[1]
                shortLoseSum = shortList[2]
                shortProfitNum = shortList[3]

            astr = str(monthKey)
            astr += ","
            
            aVariable = longProfitSum + shortProfitSum - longLoseSum - shortLoseSum #獲利
            astr += ("{:.2f}".format(aVariable)).strip()
            astr += ","
            
            astr += ("{:.2f}".format(longProfitSum + shortProfitSum)).strip() #毛利
            astr += ","
            
            aVariable = longLoseSum + shortLoseSum #毛損
            astr += ("{:.2f}".format(aVariable)).strip()
            astr += ","            
            
            tradeNum = longTradeNum + shortTradeNum #交易次數
            astr += str(tradeNum)
            astr += ","
            
            aVariable = 100.0 * (longProfitNum + shortProfitNum) / tradeNum #勝率
            astr += ("{:.2f}".format(aVariable)).strip() + "%"
            astr += ",,\n"
            outList.append(astr)
        
        astr = "年報酬率,,,,,,,\n"
        outList.append(astr)
        
        astr = "期間,獲利,毛利,毛損,交易次數,勝率,,\n"
        outList.append(astr)

        keyList = self.ylYearDict.keys()
        keyList = sorted(keyList)
        for yearKey in keyList:
            longList = self.ylLongDict.get(yearKey)
            if longList == None:
                longTradeNum = 0
                longProfitSum = 0
                longLoseSum = 0
                longProfitNum = 0
            else:
                longTradeNum = longList[0]
                longProfitSum = longList[1]
                longLoseSum = longList[2]
                longProfitNum = longList[3]
            shortList = self.ylShortDict.get(yearKey)
            if shortList == None:
                shortTradeNum = 0
                shortProfitSum = 0
                shortLoseSum = 0
                shortProfitNum = 0
            else:
                shortTradeNum = shortList[0]
                shortProfitSum = shortList[1]
                shortLoseSum = shortList[2]
                shortProfitNum = shortList[3]
                
            astr = str(yearKey)
            astr += ","
            
            aVariable = longProfitSum + shortProfitSum - longLoseSum - shortLoseSum #獲利
            astr += ("{:.2f}".format(aVariable)).strip()
            astr += ","
            
            astr += ("{:.2f}".format(longProfitSum + shortProfitSum)).strip() #毛利
            astr += ","
            
            aVariable = longLoseSum + shortLoseSum #毛損
            astr += ("{:.2f}".format(aVariable)).strip()
            astr += ","
            
            tradeNum = longTradeNum + shortTradeNum #交易次數
            astr += str(tradeNum)
            astr += ","
            
            aVariable = 100.0 * (longProfitNum + shortProfitNum) / tradeNum #勝率
            astr += ("{:.2f}".format(aVariable)).strip() + "%"
            astr += ",,\n"
            outList.append(astr)
        
        with open(os.path.join(export_path, fileName), 'w', encoding = 'utf-8') as f:
            for astr in outList:
                f.write(astr)

    def finishedPopup(self, fileName):
        content = BoxLayout(size_hint=(1, 1), orientation="vertical")
        content.add_widget(BoxLayout(size_hint=(1, .05)))
        
        fileLayout = GridLayout(cols=2, spacing=2, size_hint=(1, None))
        fileLayout.bind(minimum_height=fileLayout.setter('height'))
        fileLayout.add_widget(SLabel(text="匯出目錄:", size_hint=(.22, None), height=30))
        fileLayout.add_widget(SLabel(text=export_path, size_hint=(.78, None), height=30))
        fileLayout.add_widget(SLabel(text="檔案名稱:", size_hint=(.22, None), height=30))
        fileLayout.add_widget(SLabel(text=fileName, size_hint=(.78, None), height=30))
        content.add_widget(fileLayout)
        
        content.add_widget(BoxLayout(size_hint=(1, .05)))
        
        bottomLayout = BoxLayout(size_hint=(1, .1), orientation="horizontal")
        ensurebtn = SButton(text="確定", size_hint=(1, .8))
        bottomLayout.add_widget(ensurebtn)
        content.add_widget(bottomLayout)

        self.fin_popup = SPopup(title="匯出完成", content=content, title_font=CONSTS.FONT_NAME,
                        size_hint=(None, None), size=(360, 180), auto_dismiss=False)
        ensurebtn.bind(on_press=self.fin_popup.dismiss)
        self.fin_popup.open()

    def addBookmarkHead(self):

        self.bookmarkHead.clear_widgets()

        self.bookmarkHead.add_widget(BoxLayout(size_hint=(.01, 1)))
        
        abtn = SButton2(text="交易分析", size_hint=(.16, 1))
        abtn.disabled = True
        self.now_bookmark = abtn
        abtn.bind(on_release=self.changeBookmark)
        self.bookmarkHead.add_widget(abtn)
        
        self.bookmarkHead.add_widget(BoxLayout(size_hint=(.01, 1)))
        
        abtn = SButton2(text="交易記錄", size_hint=(.16, 1))
        abtn.bind(on_release=self.changeBookmark)
        self.bookmarkHead.add_widget(abtn)
        
        self.bookmarkHead.add_widget(BoxLayout(size_hint=(.01, 1)))
        
        abtn = SButton2(text="月報酬率", size_hint=(.16, 1))
        abtn.bind(on_release=self.changeBookmark)
        self.bookmarkHead.add_widget(abtn)
        
        self.bookmarkHead.add_widget(BoxLayout(size_hint=(.01, 1)))
        
        abtn = SButton2(text="年報酬率", size_hint=(.16, 1))
        abtn.bind(on_release=self.changeBookmark)
        self.bookmarkHead.add_widget(abtn)
        
        self.bookmarkHead.add_widget(BoxLayout(size_hint=(.32, 1)))
        
        self.body_layout.add_widget(self.bookmarkHead)
        self.body_layout.add_widget(BoxLayout(size_hint=(1, .01)))
        self.body_layout.add_widget(self.tradeAnalyze)
        self.now_bookmarkLayout = self.tradeAnalyze

    def changeBookmark(self, instance):
        self.now_bookmark.disabled = False
        self.now_bookmark = instance
        self.now_bookmark.disabled = True        
        if instance.text == "交易分析":            
            self.body_layout.remove_widget(self.now_bookmarkLayout)
            self.body_layout.add_widget(self.tradeAnalyze)
            self.now_bookmarkLayout = self.tradeAnalyze
        elif instance.text == "交易記錄":
            self.body_layout.remove_widget(self.now_bookmarkLayout)
            self.body_layout.add_widget(self.tradeRecord)
            self.now_bookmarkLayout = self.tradeRecord
        elif instance.text == "月報酬率":
            self.body_layout.remove_widget(self.now_bookmarkLayout)
            self.body_layout.add_widget(self.monthReport)
            self.now_bookmarkLayout = self.monthReport
        elif instance.text == "年報酬率":            
            self.body_layout.remove_widget(self.now_bookmarkLayout)
            self.body_layout.add_widget(self.yearReport)
            self.now_bookmarkLayout = self.yearReport

    def addTradeAnalyze(self):

        self.tradeAnalyze.clear_widgets()

        self.tradeAnalyze.add_widget(BoxLayout(size_hint=(1, None), height=2))
        
        headLayout = STableGridLayout(cols=4, rows=1, spacing=2, size_hint=(1, None), height=GRID_HEIGHT)
        headLabel = SHeadLabel(text="", size_hint=(.28, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="所有交易", size_hint=(.24, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="多單", size_hint=(.24, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="空單", size_hint=(.24, 1))
        headLayout.add_widget(headLabel)
        self.tradeAnalyze.add_widget(headLayout)
        
        self.tradeAnalyze.add_widget(STableBoxLayout(size_hint=(1, None), height=2))
        
        slview = STableScrollView()
        slview.size_hint = (1, .9)
        self.taContent = STableGridLayout(cols=4, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.taContent.bind(minimum_height=self.taContent.setter('height'))   

        self.addTaContent()
        slview.add_widget(self.taContent)        
        self.tradeAnalyze.add_widget(slview)

    def addTaContent(self):
        
        allContentList = []
        
        contentList = []
        contentList.append("淨利")
        contentList.append(LABEL_COLOR)
        netProfit = self.longNetProfit + self.shortNetProfit
        if netProfit < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * netProfit)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(netProfit)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        if self.longNetProfit < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * self.longNetProfit)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(self.longNetProfit)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)            
        if self.shortNetProfit < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * self.shortNetProfit)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(self.shortNetProfit)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)        
        allContentList.append(contentList)
        
        longTradeNum = self.longProfitNum + self.longLoseNum + self.longEqualNum #多單交易次數
        shortTradeNum = self.shortProfitNum + self.shortLoseNum + self.shortEqualNum #空單交易次數
        tradeNum = longTradeNum + shortTradeNum #交易總次數
        contentList = []
        contentList.append("交易總次數")
        contentList.append(LABEL_COLOR)
        contentList.append(str(tradeNum))
        contentList.append(LABEL_COLOR)
        contentList.append(str(longTradeNum))
        contentList.append(LABEL_COLOR)
        contentList.append(str(shortTradeNum))
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("獲利交易次數")
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.longProfitNum + self.shortProfitNum))
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.longProfitNum))
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.shortProfitNum))
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("虧損交易次數")
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.longLoseNum + self.shortLoseNum))
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.longLoseNum))
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.shortLoseNum))
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("持平交易次數")
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.longEqualNum + self.shortEqualNum))
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.longEqualNum))
        contentList.append(LABEL_COLOR)
        contentList.append(str(self.shortEqualNum))
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("勝率")
        contentList.append(LABEL_COLOR)
        apercent = 0.0
        if tradeNum != 0:
            apercent = 100.0 * (self.longProfitNum + self.shortProfitNum) / tradeNum #總勝率
        apercentStr = ("{:3.2f}".format(apercent)).strip() + "%"
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        apercent = 0.0
        if longTradeNum != 0:
            apercent = 100.0 * self.longProfitNum / longTradeNum #多單勝率
        apercentStr = ("{:3.2f}".format(apercent)).strip() + "%"
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        apercent = 0.0
        if shortTradeNum != 0:
            apercent = 100.0 * self.shortProfitNum / shortTradeNum #空單勝率
        apercentStr = ("{:3.2f}".format(apercent)).strip() + "%"
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("平均獲利")
        contentList.append(LABEL_COLOR)
        profitAverage = 0.0
        if (self.longProfitNum + self.shortProfitNum) != 0:
            profitAverage = 1.0 * (self.longProfitSum + self.shortProfitSum) / (self.longProfitNum + self.shortProfitNum) #平均獲利
        apercentStr = ("${:,.2f}".format(profitAverage)).strip()
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        longProfitAverage = 0.0
        if self.longProfitNum != 0:
            longProfitAverage = 1.0 * self.longProfitSum / self.longProfitNum #多單平均獲利
        apercentStr = ("${:,.2f}".format(longProfitAverage)).strip()
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        shortProfitAverage = 0.0
        if self.shortProfitNum != 0:
            shortProfitAverage = 1.0 * self.shortProfitSum / self.shortProfitNum #空單平均獲利
        apercentStr = ("${:,.2f}".format(shortProfitAverage)).strip()
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("平均虧損")
        contentList.append(LABEL_COLOR)
        loseAverage = 0.0
        if (self.longLoseNum + self.shortLoseNum) != 0:
            loseAverage = 1.0 * (self.longLoseSum + self.shortLoseSum) / (self.longLoseNum + self.shortLoseNum) #平均虧損
        apercentStr = ("(${:,.2f})".format(loseAverage)).strip()
        contentList.append(apercentStr)
        contentList.append(NEGATIVE_COLOR)
        longLoseAverage = 0.0
        if self.longLoseNum != 0:
            longLoseAverage = 1.0 * self.longLoseSum / self.longLoseNum #多單平均虧損
        apercentStr = ("(${:,.2f})".format(longLoseAverage)).strip()
        contentList.append(apercentStr)
        contentList.append(NEGATIVE_COLOR)
        shortLoseAverage = 0.0
        if self.shortLoseNum != 0:
            shortLoseAverage = 1.0 * self.shortLoseSum / self.shortLoseNum #空單平均虧損
        apercentStr = ("(${:,.2f})".format(shortLoseAverage)).strip()
        contentList.append(apercentStr)
        contentList.append(NEGATIVE_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("平均獲利/平均虧損=盈虧比")
        contentList.append(LABEL_COLOR)
        if loseAverage != 0:
            apercent = 1.0 * profitAverage / loseAverage #總盈虧比
            apercentStr = ("{:.2f}".format(apercent)).strip()
        else:
            apercentStr = "NA"
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        if longLoseAverage != 0:
            apercent = 1.0 * longProfitAverage / longLoseAverage #多單盈虧比
            apercentStr = ("{:.2f}".format(apercent)).strip()
        else:
            apercentStr = "NA"
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        if shortLoseAverage != 0:
            apercent = 1.0 * shortProfitAverage / shortLoseAverage #空單盈虧比
            apercentStr = ("{:.2f}".format(apercent)).strip()
        else:
            apercentStr = "NA"
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)

        profitPerDict = self.calcProfitPercent()
        
        avgProfitPer = profitPerDict.get("avgProfitPer") #平均報酬率
        lavgProfitPer = profitPerDict.get("lavgProfitPer") #多單平均報酬率
        savgProfitPer = profitPerDict.get("savgProfitPer") #空單平均報酬率
         
        contentList = []
        contentList.append("平均報酬率")
        contentList.append(LABEL_COLOR)
        #平均報酬率
        if avgProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * avgProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(avgProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        #多單平均報酬率
        if lavgProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * lavgProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(lavgProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        #空單平均報酬率
        if savgProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * savgProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(savgProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)   
        allContentList.append(contentList)

        contentList = []
        contentList.append("最大獲利")
        contentList.append(LABEL_COLOR)
        if self.longMaxProfit < self.shortMaxProfit: #最大獲利
            apercentStr = ("${:,.2f}".format(self.shortMaxProfit)).strip()
        else:
            apercentStr = ("${:,.2f}".format(self.longMaxProfit)).strip()
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        apercentStr = ("${:,.2f}".format(self.longMaxProfit)).strip() #多單最大獲利
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        apercentStr = ("${:,.2f}".format(self.shortMaxProfit)).strip() #空單最大獲利
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        maxProfitPer = profitPerDict.get("maxProfitPer") #最大報酬率
        lMaxProfitPer = profitPerDict.get("lMaxProfitPer") #多單最大報酬率
        sMaxProfitPer = profitPerDict.get("sMaxProfitPer") #空單最大報酬率
         
        contentList = []
        contentList.append("最大報酬率")
        contentList.append(LABEL_COLOR)
        #最大報酬率
        if maxProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * maxProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(maxProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        #多單最大報酬率
        if lMaxProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * lMaxProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(lMaxProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        #空單最大報酬率
        if sMaxProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * sMaxProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(sMaxProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("最大虧損")
        contentList.append(LABEL_COLOR)
        if self.longMaxLose < self.shortMaxLose: #最大虧損
            apercentStr = ("(${:,.2f})".format(self.shortMaxLose)).strip()
        else:
            apercentStr = ("(${:,.2f})".format(self.longMaxLose)).strip()
        contentList.append(apercentStr)
        contentList.append(NEGATIVE_COLOR)
        apercentStr = ("(${:,.2f})".format(self.longMaxLose)).strip() #多單最大虧損
        contentList.append(apercentStr)
        contentList.append(NEGATIVE_COLOR)
        apercentStr = ("(${:,.2f})".format(self.shortMaxLose)).strip() #空單最大虧損
        contentList.append(apercentStr)
        contentList.append(NEGATIVE_COLOR)
        allContentList.append(contentList)
        
        minProfitPer = profitPerDict.get("minProfitPer") #最小報酬率
        lMinProfitPer = profitPerDict.get("lMinProfitPer") #多單最小報酬率
        sMinProfitPer = profitPerDict.get("sMinProfitPer") #空單最小報酬率
         
        contentList = []
        contentList.append("最小報酬率")
        contentList.append(LABEL_COLOR)
        #最小報酬率
        if minProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * minProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(minProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        #多單最小報酬率
        if lMinProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * lMinProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(lMinProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        #空單最小報酬率
        if sMinProfitPer < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * sMinProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(sMinProfitPer)).strip() + "%"
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("平均月報酬")
        contentList.append(LABEL_COLOR)
        if self.rewardsAvg < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * self.rewardsAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(self.rewardsAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        if self.longRewardsAvg < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * self.longRewardsAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(self.longRewardsAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        if self.shortRewardsAvg < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * self.shortRewardsAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(self.shortRewardsAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)        
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("平均年報酬")
        contentList.append(LABEL_COLOR)
        if self.yearAvg < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * self.yearAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(self.yearAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        if self.longYearAvg < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * self.longYearAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(self.longYearAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)
        if self.shortYearAvg < 0:
            apercentStr = ("(${:,.2f})".format(-1.0 * self.shortYearAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(NEGATIVE_COLOR)            
        else:
            apercentStr = ("${:,.2f}".format(self.shortYearAvg)).strip()
            contentList.append(apercentStr)
            contentList.append(LABEL_COLOR)        
        allContentList.append(contentList)
        
        contentList = []
        contentList.append("手續費+交易稅")
        contentList.append(LABEL_COLOR)
        apercentStr = ("${:,.2f}".format(self.longCostSum + self.shortCostSum)).strip() #總成本
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        apercentStr = ("${:,.2f}".format(self.longCostSum)).strip() #多單成本
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        apercentStr = ("${:,.2f}".format(self.shortCostSum)).strip() #空單成本
        contentList.append(apercentStr)
        contentList.append(LABEL_COLOR)
        allContentList.append(contentList)
        
        self.addTA_AllRows(allContentList)

    def calcProfitPercent(self): #處理 平均報酬率,最大報酬率及最小報酬率
        buyCostSum = None
        aVariable = None
        aPrice = None
        aVol = None
        maxProfitPer = 0.0 #最大報酬率
        minProfitPer = 0.0 #最小報酬率
        lMaxProfitPer = 0.0 #多單最大報酬率
        lMinProfitPer = 0.0 #多單最小報酬率
        lProfitSum = 0.0 #多單報酬率加總
        lTradeNum = 0 #多單交易次數
        sMaxProfitPer = 0.0 #空單最大報酬率
        sMinProfitPer = 0.0 #空單最小報酬率
        sProfitSum = 0.0 #空單報酬率加總
        sTradeNum = 0 #空單交易次數
        for tradeDict in self.allTradeList:
            tradeList = tradeDict.get("tradeList")
            tradeType = tradeDict.get("tradeType")
            
            buyCostSum = 0.0
            for adict in tradeList:
                aVariable = adict.get("date")
                bs = adict.get("bs")
                if bs == "B":
                    aPrice = adict.get("price")
                    aVol = adict.get("vol")
                    buyCostSum += 1.0 * aPrice * aVol * self.volumeNum
            
            tradeSum = tradeDict.get("tradeSum")
            aVariable = 1.0 * tradeSum * 100 / buyCostSum
            if tradeType == "S": #空單
                sTradeNum += 1
                if aVariable > maxProfitPer:
                    maxProfitPer = aVariable                
                if aVariable > sMaxProfitPer:
                    sMaxProfitPer = aVariable
                if aVariable < minProfitPer:
                    minProfitPer = aVariable
                if aVariable < sMinProfitPer:
                    sMinProfitPer = aVariable                
                sProfitSum += aVariable
            else: #多單
                lTradeNum += 1
                if aVariable > maxProfitPer:
                    maxProfitPer = aVariable                
                if aVariable > lMaxProfitPer:
                    lMaxProfitPer = aVariable
                if aVariable < minProfitPer:
                    minProfitPer = aVariable
                if aVariable < lMinProfitPer:
                    lMinProfitPer = aVariable                
                lProfitSum += aVariable
        
        aDict = {}
        tolTradeNum = lTradeNum + sTradeNum
        avgProfitPer = 0.0
        if tolTradeNum != 0:
            avgProfitPer = (lProfitSum + sProfitSum) / (lTradeNum + sTradeNum) #全部的平均報酬率
        lavgProfitPer = 0.0
        if lTradeNum != 0:
            lavgProfitPer = lProfitSum / lTradeNum #多單平均報酬率
        savgProfitPer = 0.0
        if sTradeNum != 0:
            savgProfitPer = sProfitSum / sTradeNum #空單平均報酬率
        aDict["avgProfitPer"] = avgProfitPer #平均報酬率
        aDict["lavgProfitPer"] = lavgProfitPer #多單平均報酬率
        aDict["savgProfitPer"] = savgProfitPer #空單平均報酬率
        aDict["maxProfitPer"] = maxProfitPer #最大報酬率
        aDict["lMaxProfitPer"] = lMaxProfitPer #多單最大報酬率
        aDict["sMaxProfitPer"] = sMaxProfitPer #空單最大報酬率
        aDict["minProfitPer"] = minProfitPer #最小報酬率
        aDict["lMinProfitPer"] = lMinProfitPer #多單最小報酬率
        aDict["sMinProfitPer"] = sMinProfitPer #空單最小報酬率
        
        return aDict
        
    def addTA_AllRows(self, allContentList):
        
        for alist in allContentList:
            contentLabel = SContentLabel(text=alist[0], size_hint=(.28, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(alist[1])
            contentLabel.halign = "center"
            contentLabel.valign = "middle"
            self.taContent.add_widget(contentLabel)
            contentLabel = SContentLabel(text=alist[2], size_hint=(.24, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(alist[3])
            contentLabel.halign = "right"
            contentLabel.valign = "middle"
            self.taContent.add_widget(contentLabel)
            contentLabel = SContentLabel(text=alist[4], size_hint=(.24, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(alist[5])
            contentLabel.halign = "right"
            contentLabel.valign = "middle"            
            self.taContent.add_widget(contentLabel)
            contentLabel = SContentLabel(text=alist[6], size_hint=(.24, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(alist[7])
            contentLabel.halign = "right"
            contentLabel.valign = "middle"            
            self.taContent.add_widget(contentLabel)
    
    def addTradeList(self):

        self.tradeRecord.clear_widgets()

        self.tradeRecord.add_widget(BoxLayout(size_hint=(1, None), height=2))
        tlBookmarkHead = BoxLayout(size_hint=(1, .06), orientation="horizontal") #頁籤
        tlBookmarkHead.add_widget(BoxLayout(size_hint=(.01, 1)))
        
        abtn = SButton(text="交易列表", size_hint=(.16, 1))
        abtn.color = colorHex("#00FFFF")
        abtn.disabled = True
        self.now_tlBookmark = abtn
        abtn.bind(on_release=self.tlChangeBookmark)
        tlBookmarkHead.add_widget(abtn)
        
        tlBookmarkHead.add_widget(BoxLayout(size_hint=(.01, 1)))
        
        abtn = SButton(text="交易圖表", size_hint=(.16, 1))
        abtn.color = colorHex("#00FFFF")
        abtn.bind(on_release=self.tlChangeBookmark)
        tlBookmarkHead.add_widget(abtn)
        
        tlBookmarkHead.add_widget(BoxLayout(size_hint=(.67, 1)))
        
        self.tradeRecord.add_widget(tlBookmarkHead)
        
        self.tradeRecord.add_widget(BoxLayout(size_hint=(1, None), height=4))
        
        self.addTlList()
    
    def tlChangeBookmark(self, instance):
        self.now_tlBookmark.disabled = False
        self.now_tlBookmark = instance
        self.now_tlBookmark.disabled = True        
        if instance.text == "交易列表":            
            self.addTlList()
        elif instance.text == "交易圖表":
            self.addTlGraph()
    
    def addTlList(self):
        
        if self.tlGraph != None:
            self.tradeRecord.remove_widget(self.tlGraph)
        
        self.tlHeadLayout = STableGridLayout(cols=7, rows=1, spacing=1, size_hint=(1, None), height=GRID_HEIGHT)
        headLabel = SHeadLabel(text="日期", size_hint=(None, 1), width=100)
        self.tlHeadLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="訊號", size_hint=(None, 1), width=90)
        self.tlHeadLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="時間", size_hint=(None, 1), width=120)
        self.tlHeadLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="價格", size_hint=(None, 1), width=120)
        self.tlHeadLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="數量", size_hint=(None, 1), width=90)
        self.tlHeadLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="獲利金額", size_hint=(None, 1), width=138)
        self.tlHeadLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="獲利%", size_hint=(None, 1), width=110)
        self.tlHeadLayout.add_widget(headLabel)
        self.tradeRecord.add_widget(self.tlHeadLayout)

        self.tlSpaceLayout = STableBoxLayout(size_hint=(1, None), height=2)
        self.tradeRecord.add_widget(self.tlSpaceLayout)
        
        self.tlSlview = STableScrollView()
        self.tlSlview.size_hint = (1, .84)
        self.tradeRecord.add_widget(self.tlSlview)
        
        self.addTlContent(self.tlSlview)
    
    def addTlContent(self, slview):
        slview.clear_widgets()
        
        if len(self.allTradeList) == 0:
            return
        
        tlContent = BoxLayout(size_hint_y=None, orientation="vertical")
        # Make sure the height is such that there is something to scroll.
        tlContent.bind(minimum_height=tlContent.setter('height'))
        slview.add_widget(tlContent)
        
        recordHeight = None
        buyCostSum = None
        aVariable = None
        aPrice = None
        aVol = None
        for tradeDict in self.allTradeList:
            tradeList = tradeDict.get("tradeList")
            tradeType = tradeDict.get("tradeType")

            recordHeight = (GRID_HEIGHT + 1) * len(tradeList)
            oneTradeLayout = STableBoxLayout(size_hint=(1, None), height=recordHeight, orientation="horizontal")
            
            bsLayout = STableGridLayout(cols=5, spacing=1, size_hint=(None, None), width=525)
            bsLayout.bind(minimum_height=bsLayout.setter('height'))
            
            buyCostSum = 0.0
            for adict in tradeList:
                aVariable = adict.get("date")
                contentLabel = SContentLabel(text=sutil.formatDate(aVariable), size_hint=(None, None), size=(100, GRID_HEIGHT))
                contentLabel.color = colorHex(LABEL_COLOR)
                contentLabel.halign = "center"
                contentLabel.valign = "middle"                
                bsLayout.add_widget(contentLabel)
                bs = adict.get("bs")
                if bs == "B":
                    aPrice = adict.get("price")
                    aVol = adict.get("vol")
                    buyCostSum += 1.0 * aPrice * aVol * self.volumeNum
                    atext = "買進"
                else:
                    atext = "賣出"
                contentLabel = SContentLabel(text=atext, size_hint=(None, None), size=(90, GRID_HEIGHT))
                contentLabel.color = colorHex(LABEL_COLOR)
                contentLabel.halign = "center"
                contentLabel.valign = "middle"                
                bsLayout.add_widget(contentLabel)
                aVariable = adict.get("time")
                contentLabel = SContentLabel(text=sutil.formatTime(aVariable), size_hint=(None, None), size=(120, GRID_HEIGHT))
                contentLabel.color = colorHex(LABEL_COLOR)
                contentLabel.halign = "center"
                contentLabel.valign = "middle"                
                bsLayout.add_widget(contentLabel)
                contentLabel = SContentLabel(text=str(adict.get("price")), size_hint=(None, None), size=(120, GRID_HEIGHT))
                contentLabel.color = colorHex(LABEL_COLOR)
                contentLabel.halign = "right"
                contentLabel.valign = "middle"                
                bsLayout.add_widget(contentLabel)
                contentLabel = SContentLabel(text=str(adict.get("vol")), size_hint=(None, None), size=(90, GRID_HEIGHT))
                contentLabel.color = colorHex(LABEL_COLOR)
                contentLabel.halign = "right"
                contentLabel.valign = "middle"                
                bsLayout.add_widget(contentLabel)
            
            oneTradeLayout.add_widget(bsLayout)
            
            profitLayout = STableGridLayout(cols=2, spacing=1, padding=1, size_hint=(None, None), size=(259, recordHeight))
            tradeSum = tradeDict.get("tradeSum")
            contentLabel = SContentLabel(size_hint=(None, 1), width=138)
            if tradeSum < 0:
                aVariable = ("(${:,.2f})".format(-1.0 * tradeSum)).strip()
                contentLabel.color = colorHex(NEGATIVE_COLOR)
            else:
                aVariable = ("${:,.2f}".format(tradeSum)).strip()
                contentLabel.color = colorHex(LABEL_COLOR)            
            contentLabel.text = aVariable
            contentLabel.halign = "right"
            contentLabel.valign = "middle"            
            profitLayout.add_widget(contentLabel)
            
            contentLabel = SContentLabel(size_hint=(None, 1), width=120)
            if tradeSum < 0:
                aVariable = -1.0 * tradeSum * 100 / buyCostSum
                aVariable = ("({:,.2f})".format(aVariable)).strip() + "%"
                contentLabel.color = colorHex(NEGATIVE_COLOR)
            else:
                aVariable = 1.0 * tradeSum * 100 / buyCostSum
                aVariable = ("{:,.2f}".format(aVariable)).strip() + "%"
                contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.text = aVariable
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            profitLayout.add_widget(contentLabel)
            
            oneTradeLayout.add_widget(profitLayout)
            
            tlContent.add_widget(oneTradeLayout)
            tlContent.add_widget(STableBoxLayout(size_hint=(1, None), height=1))

    def addTlGraph(self):
        self.tradeRecord.remove_widget(self.tlHeadLayout)
        self.tradeRecord.remove_widget(self.tlSpaceLayout)
        self.tradeRecord.remove_widget(self.tlSlview)

        if self.tlGraph != None:
            self.tlGraph.clear_widgets()

        profitPerList = []
        tradeList = None
        tradeType = None
        buyCostSum = None
        bs = None
        aPrice = None
        aVol = None
        tradeSum = None
        profitPer = None
        for tradeDict in self.allTradeList:
            tradeList = tradeDict.get("tradeList")
            tradeType = tradeDict.get("tradeType")

            buyCostSum = 0.0
            for adict in tradeList:
                bs = adict.get("bs")
                if bs == "B":
                    aPrice = adict.get("price")
                    aVol = adict.get("vol")
                    buyCostSum += 1.0 * aPrice * aVol * self.volumeNum
            tradeSum = tradeDict.get("tradeSum")
            profitPer = 1.0 * tradeSum * 100 / buyCostSum
            profitPerList.append(profitPer)

        refDict = {}
        for key in self.paramDict.keys():
            refDict[key] = self.paramDict.get(key)
        refDict["dataList"] = profitPerList    
        strade_graph = STradeGraph(refDict)
        strade_graph.size_hint = (1, 1)
        self.tlGraph.add_widget(strade_graph)

        self.tradeRecord.add_widget(self.tlGraph)
    
    def addMonthReport(self):
        self.monthReport.clear_widgets()

        self.monthReport.add_widget(BoxLayout(size_hint=(1, None), height=2))
        
        headLayout = STableGridLayout(cols=6, rows=1, spacing=2, size_hint=(1, None), height=GRID_HEIGHT)
        headLabel = SHeadLabel(text="期間", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="獲利", size_hint=(.22, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="毛利", size_hint=(.22, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="毛損", size_hint=(.22, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="交易次數", size_hint=(.1, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="勝率", size_hint=(.1, 1))
        headLayout.add_widget(headLabel)
        self.monthReport.add_widget(headLayout)
        
        self.monthReport.add_widget(STableBoxLayout(size_hint=(1, None), height=2))
        
        slview = STableScrollView()
        slview.size_hint = (1, .9)
        self.monthReport.add_widget(slview)
        
        self.addMrContent(slview)
    
    def addMrContent(self, slview):
        slview.clear_widgets()
        
        if len(self.mlMonthDict) == 0:
            return
        
        mrContent = STableGridLayout(cols=6, spacing=2, size_hint=(1, None))
        # Make sure the height is such that there is something to scroll.
        mrContent.bind(minimum_height=mrContent.setter('height'))
        slview.add_widget(mrContent)
        
        keyList = self.mlMonthDict.keys()
        keyList = sorted(keyList)
        for monthKey in keyList:
            longList = self.mlLongDict.get(monthKey)
            if longList == None:
                longTradeNum = 0
                longProfitSum = 0
                longLoseSum = 0
                longProfitNum = 0
            else:
                longTradeNum = longList[0]
                longProfitSum = longList[1]
                longLoseSum = longList[2]
                longProfitNum = longList[3]
            shortList = self.mlShortDict.get(monthKey)
            if shortList == None:
                shortTradeNum = 0
                shortProfitSum = 0
                shortLoseSum = 0
                shortProfitNum = 0
            else:
                shortTradeNum = shortList[0]
                shortProfitSum = shortList[1]
                shortLoseSum = shortList[2]
                shortProfitNum = shortList[3]
            
            contentLabel = SContentLabel(text=str(monthKey), size_hint=(.14, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.halign = "center"
            contentLabel.valign = "middle"             
            mrContent.add_widget(contentLabel)
            
            contentLabel = SContentLabel(size_hint=(.22, None), height=GRID_HEIGHT)         
            aVariable = longProfitSum + shortProfitSum - longLoseSum - shortLoseSum #獲利
            if aVariable < 0:
                aVariable = ("(${:,.2f})".format(-1.0 * aVariable)).strip()
                contentLabel.color = colorHex(NEGATIVE_COLOR)
            else:
                aVariable = ("${:,.2f}".format(aVariable)).strip()
                contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.text = aVariable
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            mrContent.add_widget(contentLabel)
            
            contentLabel = SContentLabel(size_hint=(.22, None), height=GRID_HEIGHT)
            aVariable = longProfitSum + shortProfitSum #毛利
            aVariable = ("${:,.2f}".format(aVariable)).strip()
            contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.text = aVariable
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            mrContent.add_widget(contentLabel)

            contentLabel = SContentLabel(size_hint=(.22, None), height=GRID_HEIGHT)
            aVariable = longLoseSum + shortLoseSum #毛損
            if aVariable != 0:
                aVariable = ("(${:,.2f})".format(aVariable)).strip()
                contentLabel.color = colorHex(NEGATIVE_COLOR)
            else:
                aVariable = ("${:,.2f}".format(aVariable)).strip()
                contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.text = aVariable
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            mrContent.add_widget(contentLabel)
            
            tradeNum = longTradeNum + shortTradeNum #交易次數
            contentLabel = SContentLabel(text=str(tradeNum), size_hint=(.1, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            mrContent.add_widget(contentLabel)
            
            aVariable = 100.0 * (longProfitNum + shortProfitNum) / tradeNum #勝率
            aVariable = ("{:,.2f}".format(aVariable)).strip() + "%"
            contentLabel = SContentLabel(text=aVariable, size_hint=(.1, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            mrContent.add_widget(contentLabel)
    
    def addYearReport(self):
        self.yearReport.clear_widgets()

        self.yearReport.add_widget(BoxLayout(size_hint=(1, None), height=2))
        
        headLayout = STableGridLayout(cols=6, rows=1, spacing=2, size_hint=(1, None), height=GRID_HEIGHT)
        headLabel = SHeadLabel(text="期間", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="獲利", size_hint=(.22, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="毛利", size_hint=(.22, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="毛損", size_hint=(.22, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="交易次數", size_hint=(.1, 1))
        headLayout.add_widget(headLabel)
        headLabel = SHeadLabel(text="勝率", size_hint=(.1, 1))
        headLayout.add_widget(headLabel)
        self.yearReport.add_widget(headLayout)
        
        self.yearReport.add_widget(STableBoxLayout(size_hint=(1, None), height=2))
        
        slview = STableScrollView()
        slview.size_hint = (1, .9)
        self.yearReport.add_widget(slview)
        
        self.addYrContent(slview)
    
    def addYrContent(self, slview):
        slview.clear_widgets()
        
        if len(self.ylYearDict) == 0:
            return
        
        yrContent = STableGridLayout(cols=6, spacing=2, size_hint=(1, None))
        # Make sure the height is such that there is something to scroll.
        yrContent.bind(minimum_height=yrContent.setter('height'))
        slview.add_widget(yrContent)
        
        keyList = self.ylYearDict.keys()
        keyList = sorted(keyList)
        for yearKey in keyList:
            longList = self.ylLongDict.get(yearKey)
            if longList == None:
                longTradeNum = 0
                longProfitSum = 0
                longLoseSum = 0
                longProfitNum = 0
            else:
                longTradeNum = longList[0]
                longProfitSum = longList[1]
                longLoseSum = longList[2]
                longProfitNum = longList[3]
            shortList = self.ylShortDict.get(yearKey)
            if shortList == None:
                shortTradeNum = 0
                shortProfitSum = 0
                shortLoseSum = 0
                shortProfitNum = 0
            else:
                shortTradeNum = shortList[0]
                shortProfitSum = shortList[1]
                shortLoseSum = shortList[2]
                shortProfitNum = shortList[3]
                
            contentLabel = SContentLabel(text=str(yearKey), size_hint=(.14, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.halign = "center"
            contentLabel.valign = "middle"             
            yrContent.add_widget(contentLabel)
            
            contentLabel = SContentLabel(size_hint=(.22, None), height=GRID_HEIGHT)         
            aVariable = longProfitSum + shortProfitSum - longLoseSum - shortLoseSum #獲利
            if aVariable < 0:
                aVariable = ("(${:,.2f})".format(-1.0 * aVariable)).strip()
                contentLabel.color = colorHex(NEGATIVE_COLOR)
            else:
                aVariable = ("${:,.2f}".format(aVariable)).strip()
                contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.text = aVariable
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            yrContent.add_widget(contentLabel)
            
            contentLabel = SContentLabel(size_hint=(.22, None), height=GRID_HEIGHT)
            aVariable = longProfitSum + shortProfitSum #毛利
            aVariable = ("${:,.2f}".format(aVariable)).strip()
            contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.text = aVariable
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            yrContent.add_widget(contentLabel)

            contentLabel = SContentLabel(size_hint=(.22, None), height=GRID_HEIGHT)
            aVariable = longLoseSum + shortLoseSum #毛損
            if aVariable != 0:
                aVariable = ("(${:,.2f})".format(aVariable)).strip()
                contentLabel.color = colorHex(NEGATIVE_COLOR)
            else:
                aVariable = ("${:,.2f}".format(aVariable)).strip()
                contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.text = aVariable
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            yrContent.add_widget(contentLabel)
            
            tradeNum = longTradeNum + shortTradeNum #交易次數
            contentLabel = SContentLabel(text=str(tradeNum), size_hint=(.1, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            yrContent.add_widget(contentLabel)
            
            aVariable = 100.0 * (longProfitNum + shortProfitNum) / tradeNum #勝率
            aVariable = ("{:,.2f}".format(aVariable)).strip() + "%"
            contentLabel = SContentLabel(text=aVariable, size_hint=(.1, None), height=GRID_HEIGHT)
            contentLabel.color = colorHex(LABEL_COLOR)
            contentLabel.halign = "right"
            contentLabel.valign = "middle"             
            yrContent.add_widget(contentLabel)
        