# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.0') # replace with your current kivy version !

import os

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex as colorHex

with open(os.path.join(os.path.dirname(__file__), "selements.kv"), encoding = "utf-8") as f:
    Builder.load_string(f.read())

DEFAULT_PADDING = 6

class SInfoButton(Button):
    
    infoIndex = None
    
    def __init__(self, infoIndex, **kwargs):
        super(SInfoButton, self).__init__(**kwargs)
        self.infoIndex = infoIndex

class SRowButton(Button):
    
    infoIndex = None
    
    def __init__(self, infoIndex, **kwargs):
        super(SRowButton, self).__init__(**kwargs)
        self.infoIndex = infoIndex

class SButton(Button):
    pass

class SButton2(Button):
    pass

class SHeadSortedButton(Button):
    def __init__(self, headText, headIndex, **kwargs):
        super(SHeadSortedButton, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.headText = headText
        self.headIndex = headIndex
    
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            self.color = colorHex("##0000FF")
        else:
            self.color = colorHex("#000000")    

class MButton(Button):
    def __init__(self, **kwargs):
        super(MButton, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
    
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            self.color = colorHex("#FFFFFF")
        else:
            self.color = colorHex("#000000")

class SLabel(Label):
    pass

class SCordLabel(Label):
    pass

class STextInput(TextInput):
    pass

class SOptionTextInput(TextInput):
    halign = StringProperty('left')
    valign = StringProperty('center')

    def __init__(self, paraName, **kwargs):
        self.halign = kwargs.get("halign", "left")
        self.valign = kwargs.get("valign", "center")
        self.multiline = False

        self.bind(on_text=self.on_text)

        super(SOptionTextInput, self).__init__(**kwargs)
        self.paraName = paraName
        
    def on_text(self, instance, value):
        self.redraw()
        
    def on_size(self, instance, value):
        self.redraw()

    def redraw(self):
        """ 
        Note: This methods depends on internal variables of its TextInput
        base class (_lines_rects and _refresh_text())
        """

        self._refresh_text(self.text)

        max_size = max(self._lines_rects, key=lambda r: r.size[0]).size
        num_lines = len(self._lines_rects)
        
        px = [DEFAULT_PADDING, DEFAULT_PADDING]
        py = [DEFAULT_PADDING, DEFAULT_PADDING]
        
        if self.halign == 'center':
            d = (self.width - max_size[0]) / 2.0 - DEFAULT_PADDING
            px = [d, d]
        elif self.halign == 'right':
            px[0] = self.width - max_size[0] - DEFAULT_PADDING
            
        if self.valign == 'middle':
            d = (self.height - max_size[1] * num_lines) / 2.0 - DEFAULT_PADDING
            py = [d, d]
        elif self.valign == 'bottom':
            py[0] = self.height - max_size[1] * num_lines - DEFAULT_PADDING

        self.padding_x = px
        self.padding_y = py

class SInfoLayout(GridLayout):
    pass

class STableGridLayout(GridLayout):
    pass

class STableBoxLayout(BoxLayout):
    pass

class STableScrollView(ScrollView):
    pass

class SPopup(Popup):
    pass

class SHeadLabel(Label):
    pass

class SContentLabel(Label):
    pass

class SBoxLayout(BoxLayout):
    pass

class SBoxLayout2(BoxLayout):
    pass

class SConfirmLayout(BoxLayout):
    
    yesbtn_id = ObjectProperty(None)
    nobtn_id = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(SConfirmLayout, self).__init__()
        self.kwargs = kwargs

class SRowConfirmLayout(BoxLayout):
    yesLayout_id = ObjectProperty(None)
    nobtn_id = ObjectProperty(None)
    yesbtn_id = None
    infoIndex = None
    
    def __init__(self, **kwargs):
        super(SRowConfirmLayout, self).__init__()
        self.kwargs = kwargs
        
        self.yesbtn_id = SRowButton(infoIndex = self.infoIndex)
        self.yesbtn_id.text = "是"
        self.yesbtn_id.size_hint = (.20, 1)
        self.yesbtn_id.halign = "center"
        self.yesbtn_id.valign = "middle"

        self.yesLayout_id.clear_widgets()
        self.yesLayout_id.add_widget(self.yesbtn_id)
        
class SDirSelectDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    filechooser_id = ObjectProperty(None)
    
    def selected(self, directory, filename):
        os.path.dirname(filename)

class SFileSelectDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    filechooser_id = ObjectProperty(None)
    
    """def selected(self, filename):
        if len(filename) == 0:
            return
        #self.filename_id.text = os.path.basename(filename[0])"""

class SFileInputDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    filechooser_id = ObjectProperty(None)
    filename_id = ObjectProperty(None)
    
    def selected(self, filename):
        if len(filename) == 0:
            return
        self.filename_id.text = os.path.basename(filename[0])
