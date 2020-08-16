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
from kivy.uix.filechooser import FileChooser
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

import sconsts as CONSTS
import sutil
from selements import SLabel, SButton, SConfirmLayout, SDirSelectDialog

with open(os.path.join(os.path.dirname(__file__), "sselect_file.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

class LeftRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class LeftSelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(LeftSelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(LeftSelectableLabel, self).on_touch_down(touch):
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
    
class LeftRV(RecycleView):
    
    isSelectDict = {}
    
    def __init__(self, **kwargs):
        super(LeftRV, self).__init__(**kwargs)
        #self.data = [{'text': str(x)} for x in range(100)]

class RightRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''

class RightSelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(RightSelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(RightSelectableLabel, self).on_touch_down(touch):
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
    
class RightRV(RecycleView):
    
    isSelectDict = {}
    
    def __init__(self, **kwargs):
        super(RightRV, self).__init__(**kwargs)
        #self.data = [{'text': str(x)} for x in range(100)]

class SSelectFile(BoxLayout):

    filepath_id = ObjectProperty(None)
    leftrv_id = ObjectProperty(None)
    rightrv_id = ObjectProperty(None)
    ensurebtn_id = ObjectProperty(None)
    closebtn_id = ObjectProperty(None)
    filedir = ObjectProperty(None)
    filepath = ObjectProperty(None)
    sysConfDict = {}
    kwargs = {}
    
    def __init__(self, refDict, **kwargs):
        super(SSelectFile, self).__init__(**kwargs)

        self.app = refDict.get(CONSTS.S_APP)
        self.sysConfDict = self.app.confDict.get(CONSTS.SYS_CONF_DICT)
        
        bk_select_dir, bk_file_dir = sutil.checkBacktestDir()
        self.filedir = os.path.abspath(bk_select_dir)
        self.filepath = os.path.abspath(bk_file_dir)        
        
        self.filepath_id.text = self.filepath
        self.filepath_id.bind(focus=self.onFocus)
        
        if os.path.exists(self.filepath):
            files = os.listdir(self.filepath)
            full_path = ""
            adict = None
            for name in files:
                full_path = os.path.join(self.filepath, name)
                if os.path.isdir(full_path):
                    continue
                adict = {}
                adict['text'] = name
                self.leftrv_id.data.append(adict)
    
    def onFocus(self, instance, value):
        if value:
            content = SDirSelectDialog(load=self.loadDir, cancel=self.dismiss_popup)
            content.filechooser_id.path = self.filedir
            popupTitle = self.sysConfDict.get("MSG_DOWNLOAD_DIR")
            self._popup = Popup(title=popupTitle, content=content, size_hint=(0.9, 0.9), title_font=CONSTS.FONT_NAME)
            self._popup.open()
    
    def dismiss_popup(self):
        self._popup.dismiss()
        
    def loadDir(self, path, filename):
        if len(filename) == 0:
            self.app.showErrorView(True, CONSTS.ERR_UNSELECT_DIR)
            return
        self.dismiss_popup()
        
        if self.filedir != path or self.filepath != filename[0]:        
            self.filedir = path
            self.filepath = filename[0]
            self.filepath_id.text = filename[0]
        
            adata = []
            files = os.listdir(self.filepath)
            full_path = ""
            adict = None
            for name in files:
                full_path = os.path.join(self.filepath, name)
                if os.path.isdir(full_path):
                    continue
                adict = {}
                adict['text'] = name
                adata.append(adict)
            self.leftrv_id.layout_manager.clear_selection()
            self.leftrv_id.data = adata
            self.leftrv_id.isSelectDict.clear()

            self.rightrv_id.layout_manager.clear_selection()
            self.rightrv_id.data = []
            self.rightrv_id.isSelectDict.clear()
        
    def toRight(self):
        isSelectDict = self.leftrv_id.isSelectDict
        if len(isSelectDict) == 0:
            return
        
        keylist = sorted(isSelectDict.keys())
        adict = None
        for key in keylist:
            adict = {}
            adict['text'] = isSelectDict.get(key)
            self.rightrv_id.data.append(adict)        
        keylist.reverse()
        for key in keylist:
            self.leftrv_id.data.pop(key)
        self.leftrv_id.isSelectDict.clear()
        self.leftrv_id.layout_manager.clear_selection()
        
    def toLeft(self):
        isSelectDict = self.rightrv_id.isSelectDict
        if len(isSelectDict) == 0:
            return
        
        keylist = sorted(isSelectDict.keys())
        adict = None
        for key in keylist:
            adict = {}
            adict['text'] = isSelectDict.get(key)
            self.leftrv_id.data.append(adict)
        
        keylist.reverse()
        for key in keylist:
            self.rightrv_id.data.pop(key)
        self.rightrv_id.isSelectDict.clear()
        self.rightrv_id.layout_manager.clear_selection()
        
        #1000-01-Start: 處理左移後重新排序
        keylist = []
        for adict in self.leftrv_id.data:
            keylist.append(adict.get('text'))
        keylist = sorted(keylist)
        aData = []
        for key in keylist:
            adict = {}
            adict['text'] = key
            aData.append(adict)
        self.leftrv_id.data = aData
        #1000-01-End.
    
    def deleteFiles(self):
        isSelectDict = self.leftrv_id.isSelectDict
        if len(isSelectDict) == 0:
            self.app.showErrorView(True, CONSTS.ERR_UNSELECT_FILE)
            return
        self.deleteConfirm = SConfirmLayout()
        self.del_popup = Popup(title="刪除檔案", content=self.deleteConfirm,
                size_hint=(None, None), size=(240, 160), auto_dismiss=False)
        self.deleteConfirm.yesbtn_id.bind(on_press=self.deleteRecordEvent)
        self.deleteConfirm.nobtn_id.bind(on_press=self.del_popup.dismiss)
        self.del_popup.title_font = CONSTS.FONT_NAME
        self.del_popup.open()
        
    def deleteRecordEvent(self, instance):
        isSelectDict = self.leftrv_id.isSelectDict
        keylist = sorted(isSelectDict.keys())

        # 刪除檔案
        adict = None
        for key in keylist:
            full_path = os.path.join(self.filepath, isSelectDict.get(key))
            if os.path.exists(full_path):
                os.remove(full_path)

        # 刪除檔案後重新list files
        adata = []
        files = os.listdir(self.filepath)
        full_path = ""
        adict = None
        for name in files:
            full_path = os.path.join(self.filepath, name)
            if os.path.isdir(full_path):
                continue
            adict = {}
            adict['text'] = name
            adata.append(adict)
        
        self.del_popup.dismiss()
        
        self.leftrv_id.layout_manager.clear_selection()
        self.leftrv_id.data = adata
        self.leftrv_id.isSelectDict.clear()
    
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
    
    def toSort(self):
        dataList = self.rightrv_id.data
        if len(dataList) == 0:
            return
        
        valueList = []
        for adata in dataList:
            valueList.append(adata.get('text'))
        valueList = sorted(valueList)
        dataList = []
        adict = None
        for avalue in valueList:
            adict = {}
            adict['text'] = avalue
            dataList.append(adict)
        self.rightrv_id.data = dataList
        self.rightrv_id.isSelectDict.clear()
        self.rightrv_id.layout_manager.clear_selection()        
        