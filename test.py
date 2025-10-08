from kivy.lang import Builder
from kivymd.app import MDApp


KV = '''
MDBoxLayout:
    orientation: "vertical"

    MDScreenManager:
        id: screen_manager

        MDScreen:
            name: "favorites"
            MDLabel:
                text: "Избранное"
                halign: "center"
                theme_text_color: "Primary"

        MDScreen:
            name: "stops"
            MDLabel:
                text: "Все остановки" 
                halign: "center"
                theme_text_color: "Primary"

        MDScreen:
            name: "about"
            MDLabel:
                text: "О приложении"
                halign: "center"
                theme_text_color: "Primary"
                

    MDNavigationBar:
        on_switch_tabs: app.on_switch_tabs(*args)

        MDNavigationItem:
            MDNavigationItemIcon:
                icon: "star"
            MDNavigationItemLabel:
                text: "Избранное"

        MDNavigationItem:
            MDNavigationItemIcon:
                icon: "bus"
            MDNavigationItemLabel:
                text: "Остановки"

        MDNavigationItem:
            MDNavigationItemIcon:
                icon: "information"
            MDNavigationItemLabel:
                text: "О приложении"
'''

class BusApp(MDApp):
    def on_switch_tabs(self, *args):
        index = list(reversed(args[0].children)).index(args[1])
        screens = ["favorites", "stops", "about"]
        self.root.ids.screen_manager.current = screens[index]

    def build(self):
        return Builder.load_string(KV)

if __name__ == "__main__":
    BusApp().run()