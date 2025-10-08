from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.lang import Builder

KV = '''
MDScreen:
    MDLabel:
        text: "Избранные остановки"
        theme_text_color: "Secondary"
        pos_hint: {"center_x": 0.5, "center_y": 0.9}
    MDRaisedButton:
        text: "Добавить"
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
'''

class MainApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

MainApp().run()
