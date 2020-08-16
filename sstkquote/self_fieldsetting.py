# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".." + os.sep + "sbase" + os.sep))

from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

import sconsts as CONSTS
import sutil
from selements import SLabel, SButton, SConfirmLayout, SDirSelectDialog

with open(os.path.join(os.path.dirname(__file__), "self_fieldsetting.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class FieldSettingRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class FieldSettingLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(FieldSettingLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(FieldSettingLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.isSelectDict[index] = rv.data[index].get('text')
        else:
            rv.isSelectDict.pop(index, None)
    
class FieldSettingRV(RecycleView):
    
    isSelectDict = {}
    
    def __init__(self, **kwargs):
        super(FieldSettingRV, self).__init__(**kwargs)
        #self.data = [{'text': str(x)} for x in range(100)]

class SFieldSetting(BoxLayout):

    rightrv_id = ObjectProperty(None)
    ensurebtn_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    sysConfDict = {}
    fieldSeqList = None
    kwargs = {}
    
    def __init__(self, refDict, **kwargs):
        super(SFieldSetting, self).__init__(**kwargs)

        self.app = refDict.get(CONSTS.S_APP)
        self.sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "stkfields_setting.ini")
        alist = sutil.getListFromFile(filePath)
        idDict = {}
        self.nameDict = {}
        seqList = []
        for astr in alist:
            tmpList = astr.strip().split(",")
            if len(tmpList) < 2:
                continue
            if tmpList[0] == "_SEQ_":
                seqList = tmpList[1].strip().split("|")
            else:
                idDict[tmpList[0]] = tmpList[1]
                self.nameDict[tmpList[1]] = tmpList[0]
        
        for seqId in seqList:
            adict = {}
            adict["text"] = idDict.get(seqId, "")
            self.rightrv_id.data.append(adict)

    def toUp(self):
        isSelectDict = self.rightrv_id.isSelectDict
        if len(isSelectDict) != 1:
            return
        
        selectIndex = list(isSelectDict.keys())[0]
        if selectIndex == 0:
            return
        adict = {}
        adict['text'] = isSelectDict.get(selectIndex)
        self.rightrv_id.data.pop(selectIndex)
        self.rightrv_id.data.insert(selectIndex - 1, adict)
        self.rightrv_id.layout_manager.selected_nodes = [selectIndex - 1]
        
    def toDown(self):
        isSelectDict = self.rightrv_id.isSelectDict
        if len(isSelectDict) != 1:
            return
    
        selectIndex = list(isSelectDict.keys())[0]
        if selectIndex == (len(self.rightrv_id.data) - 1):
            return
        adict = {}
        adict['text'] = isSelectDict.get(selectIndex)
        self.rightrv_id.data.pop(selectIndex)
        self.rightrv_id.data.insert(selectIndex + 1, adict)
        self.rightrv_id.layout_manager.selected_nodes = [selectIndex + 1]
    
    def toTop(self):
        isSelectDict = self.rightrv_id.isSelectDict
        if len(isSelectDict) != 1:
            return
        
        selectIndex = list(isSelectDict.keys())[0]
        if selectIndex == 0:
            return
        adict = {}
        adict['text'] = isSelectDict.get(selectIndex)
        self.rightrv_id.data.pop(selectIndex)
        self.rightrv_id.data.insert(0, adict)
        self.rightrv_id.layout_manager.selected_nodes = [0]
    
    def toBottom(self):
        isSelectDict = self.rightrv_id.isSelectDict
        if len(isSelectDict) != 1:
            return
        
        selectIndex = list(isSelectDict.keys())[0]
        if selectIndex == (len(self.rightrv_id.data) - 1):
            return
        adict = {}
        adict['text'] = isSelectDict.get(selectIndex)
        self.rightrv_id.data.pop(selectIndex)
        self.rightrv_id.data.append(adict)
        self.rightrv_id.layout_manager.selected_nodes = [len(self.rightrv_id.data) - 1]
    
    def saveData(self):
        filePath = os.path.join(os.path.dirname(__file__), ".." + os.sep + "conf" + os.sep + "stkfields_setting.ini")
        alist = sutil.getListFromFile(filePath)        
        with open(filePath, 'w', encoding = 'utf-8') as f:
            for tmpStr in alist:
                tmpList = tmpStr.strip().split(",")
                if len(tmpList) < 2:
                    astr = tmpStr + "\n"
                    f.write(astr)
                    continue
                if tmpList[0] == "_SEQ_":
                    aFieldId = None
                    self.fieldSeqList = []
                    astr = "_SEQ_,"
                    for aDict in self.rightrv_id.data:
                        aFieldId = self.nameDict.get(aDict.get("text"))
                        astr += aFieldId + "|"
                        self.fieldSeqList.append(aFieldId)
                    astr = astr[0:-1] + "\n"
                else:
                    astr = tmpStr + "\n"           

                f.write(astr)