from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout

kv = '''
RootWidget:
    orientation: 'vertical'
    BoxLayout:
        TextInput:
            id: txtinpt
        Label:
            id: lbl
            text: root.stored_data.get('mydata')['text'] if root.stored_data.exists('mydata') else ''
    Button:
        size_hint_y: .3
        text: 'Submit'
        on_press:
            root.stored_data.put('mydata', text=txtinpt.text)
            lbl.text = txtinpt.text
'''


class RootWidget(BoxLayout):
    stored_data = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(BoxLayout, self).__init__(*args, **kwargs)
        self.stored_data = JsonStore('data.json')


runTouchApp(Builder.load_string(kv))
