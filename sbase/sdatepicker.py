# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import os, time, datetime
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex as colorHex

import sconsts as CONSTS

Builder.load_string('''
#:kivy 1.10.0
#:import os os
#:import colorHex kivy.utils.get_color_from_hex
<SWeekLabel>:
    color: colorHex("#000000")
    font_name: os.environ["WINDIR"] + os.sep + "Fonts" + os.sep + "mingliu.ttc"           
    canvas.before:
        Color:
            rgba: colorHex("#BFE0D1")
        Rectangle:
            pos: self.pos
            size: self.size       
<SDayButton>:
    background_normal: ""
    background_color: colorHex("#576161")
    color: colorHex("#FFFFFF")
    halign: "center"
<SLRButton>:
    background_normal: ""
    background_color: colorHex("#576161")
    color: colorHex("#FFFFFF")
    halign: "center"
''')

def isLeapYear(aYear):
    isLeap = False
    if (aYear % 400) == 0:
        isLeap = True
    elif (aYear % 100) == 0:
        isLeap = False
    elif (aYear % 4) == 0:
        isLeap = True
    return isLeap

def getMonthDays(aYear):
    daysList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if isLeapYear(aYear):
        daysList[1] = 29
    return daysList

class SWeekLabel(Label):
    pass

class SDayButton(Button):
    pass

class SLRButton(Button):
    pass

class SDatePicker(BoxLayout):

    date_text = None
    
    def __init__(self, paramDateText, **kwargs):
        super(SDatePicker, self).__init__(**kwargs)
        
        self.element_height = 28

        self.orientation = "vertical"

        self.date_text = paramDateText
        if paramDateText != None:
            self.date_text = paramDateText
        else:
            self.date_text = time.strftime(format('%Y%m%d'))
        self.yearInt = int(int(self.date_text) / 10000)
        self.monthInt = int(int(self.date_text) % 10000 / 100)
        self.dayInt = int(self.date_text) % 100

        yearMonthLayout = BoxLayout(size_hint=(1, None), orientation="horizontal", height=self.element_height)
        
        yearMonthLayout.add_widget(BoxLayout(size_hint=(.11, 1))) #左邊間隙
        
        yearLeftBtn = SLRButton(text="<", size_hint=(.08, .8)) #年<
        yearLeftBtn.bind(on_press=self.yearLeftEvent)
        yearMonthLayout.add_widget(yearLeftBtn)
        yearMonthLayout.add_widget(BoxLayout(size_hint=(.01, 1))) #間隔
        self.yearLabel = Label(text=str(self.yearInt), size_hint=(.2, 1)) #西元年的數字
        yearMonthLayout.add_widget(self.yearLabel)
        alabel = Label(text="年", size_hint=(.05, 1)) #年
        alabel.font_name = CONSTS.FONT_NAME
        yearMonthLayout.add_widget(alabel)
        yearMonthLayout.add_widget(BoxLayout(size_hint=(.01, 1))) #間隔
        yearRightBtn = SLRButton(text=">", size_hint=(.08, .8)) #年>
        yearRightBtn.bind(on_press=self.yearRightEvent)
        yearMonthLayout.add_widget(yearRightBtn)
        yearMonthLayout.add_widget(BoxLayout(size_hint=(.03, 1))) #年月之間隔
        monthLeftBtn = SLRButton(text="<", size_hint=(.08, .8)) #月<
        monthLeftBtn.bind(on_press=self.monthLeftEvent)
        yearMonthLayout.add_widget(monthLeftBtn)
        self.monthLabel = Label(text=str(self.monthInt), size_hint=(.1, 1)) #月的數字
        yearMonthLayout.add_widget(self.monthLabel)
        alabel = Label(text="月", size_hint=(.05, 1)) #月
        alabel.font_name = CONSTS.FONT_NAME
        yearMonthLayout.add_widget(alabel)
        yearMonthLayout.add_widget(BoxLayout(size_hint=(.01, 1))) #間隔
        monthRightBtn = SLRButton(text=">", size_hint=(.08, .8)) #月>
        monthRightBtn.bind(on_press=self.monthRightEvent)
        yearMonthLayout.add_widget(monthRightBtn)
        yearMonthLayout.add_widget(BoxLayout(size_hint=(.11, 1))) #右邊間隙
        
        self.add_widget(yearMonthLayout)
        
        self.add_widget(BoxLayout(size_hint=(1, .01)))
        
        self.addWeekHead()
        
        self.add_widget(BoxLayout(size_hint=(1, .01)))
        
        self.selectDateDict = {}
        for i in range(1, 32):
            self.selectDateDict[i] = SDayButton(text=str(i), size_hint=(.14, None), height=self.element_height)
            self.selectDateDict[i].bind(on_release=self.dateSelectEvent)
        self.dateSelectEvent(self.selectDateDict[self.dayInt])
        
        slview = ScrollView()
        slview.size_hint = (1, .8)
        self.contentLayout = GridLayout(cols=7, spacing=2, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        self.contentLayout.bind(minimum_height=self.contentLayout.setter('height'))

        self.addContent()

        slview.add_widget(self.contentLayout)
        
        self.add_widget(slview)

    def yearLeftEvent(self, instance):
        yearInt = int(self.yearLabel.text) - 1
        if yearInt <= 0:
            return
        self.yearLabel.text = str(yearInt)
        self.yearInt = yearInt
        self.addContent()
        
    def yearRightEvent(self, instance):
        yearInt = int(self.yearLabel.text) + 1
        self.yearLabel.text = str(yearInt)
        self.yearInt = yearInt
        self.addContent()        
    
    def monthLeftEvent(self, instance):
        monthInt = int(self.monthLabel.text) - 1
        if monthInt < 1:
            self.yearInt -= 1
            if self.yearInt < 1:
                self.yearInt = 1
                monthInt = 1
            else:
                monthInt = 12
            self.yearLabel.text = str(self.yearInt)
        self.monthLabel.text = str(monthInt)
        self.monthInt = monthInt
        self.addContent()
    
    def monthRightEvent(self, instance):
        monthInt = int(self.monthLabel.text) + 1
        if monthInt > 12:
            self.yearInt += 1
            self.yearLabel.text = str(self.yearInt)
            monthInt = 1
        self.monthLabel.text = str(monthInt)
        self.monthInt = monthInt
        self.addContent()  
        
    def dateSelectEvent(self, instance):        
        self.selectDateDict[self.dayInt].background_color = colorHex("#576161")
        self.dayInt = int(instance.text)
        self.selectDateDict[self.dayInt].background_color = colorHex("#137F83")
        self.changeDateText()
    
    def changeDateText(self):
        date_text = str(self.yearInt)
        if self.monthInt < 10:
            date_text += "0"
        date_text += str(self.monthInt)
        if self.dayInt < 10:
            date_text += "0"
        date_text += str(self.dayInt)
        self.date_text = date_text 
        
    def addWeekHead(self):
        headLayout = GridLayout(cols=7, rows=1, spacing=2, size_hint=(1, None), height=self.element_height)
        headLabel = SWeekLabel(text="日", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        headLabel = SWeekLabel(text="一", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        headLabel = SWeekLabel(text="二", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        headLabel = SWeekLabel(text="三", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        headLabel = SWeekLabel(text="四", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        headLabel = SWeekLabel(text="五", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        headLabel = SWeekLabel(text="六", size_hint=(.14, 1))
        headLayout.add_widget(headLabel)
        
        self.add_widget(headLayout)

    def addDaysContent(self, monthDays):
        for i in range(monthDays):
            akey = i + 1
            self.contentLayout.add_widget(self.selectDateDict[akey])        
    
    def addSpaceElement(self):
        abtn = SDayButton(text=" ", size_hint=(.14, None), height=self.element_height)
        abtn.disabled = True
        self.contentLayout.add_widget(abtn)

    def addContent(self):

        self.contentLayout.clear_widgets()     

        firstMonthDate = datetime.date(self.yearInt, self.monthInt, 1)
        weekday = firstMonthDate.weekday()
        
        daysList = getMonthDays(self.yearInt)
        monthDays = daysList[self.monthInt - 1]
        
        if weekday == 6:
            self.addDaysContent(monthDays)
            for i in range(monthDays + 1, 43):
                self.addSpaceElement()
        else:
            for i in range(weekday + 1):
                self.addSpaceElement()            
            self.addDaysContent(monthDays)
            for i in range(42 - monthDays - (weekday + 1)):
                self.addSpaceElement()
        
        if self.dayInt > monthDays:
            self.dateSelectEvent(self.selectDateDict[monthDays])

        self.changeDateText()