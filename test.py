from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard

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
                md_bg_color: '#3ecf62'

        MDScreen:
            name: "stops"
            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "10dp"
                    spacing: "10dp"
                    adaptive_height: True

                    StopCard:
                        stop_name: "ТЕСТ Остановка"

                    StopCard:
                        stop_name: "ТЕСТ Остановка 2"

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

<StopCard>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: "10dp"
    spacing: "10dp"

    MDBoxLayout:
        size_hint_y: None
        height: "50dp"

        MDLabel:
            text: root.stop_name
            halign: "left"
            theme_text_color: "Primary"
            bold: True

        MDIconButton:
            id: favorite_btn
            icon: "star-outline"
            size_hint: None, None
            size: "40dp", "40dp"
            on_release: root.toggle_favorite()

    MDBoxLayout:
        id: routes_container
        size_hint_y: None
        height: "0dp"
        opacity: 0
        orientation: "vertical"
        spacing: "5dp"

        MDLabel:
            text: "Маршрут 15 - 5 мин"
            size_hint_y: None
            height: "30dp"

        MDLabel:
            text: "Маршрут 27 - 8 мин" 
            size_hint_y: None
            height: "30dp"
'''


class StopCard(MDCard):
    stop_name = "Остановка"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_expanded = False
        self.is_favorite = False

    def toggle_favorite(self):
        # Переключение звезды
        if self.is_favorite:
            self.ids.favorite_btn.icon = "star-outline"
            self.is_favorite = False
        else:
            self.ids.favorite_btn.icon = "star"
            self.is_favorite = True

    def on_touch_down(self, touch):
        # Разворачиваем при нажатии на карточку (кроме кнопки)
        if self.collide_point(*touch.pos):
            if not self.ids.favorite_btn.collide_point(*touch.pos):
                self.toggle_expand()
        return super().on_touch_down(touch)

    def toggle_expand(self):
        # Переключение развернутого состояния
        routes_container = self.ids.routes_container
        if self.is_expanded:
            # Сворачиваем
            routes_container.height = "0dp"
            routes_container.opacity = 0
            self.is_expanded = False
        else:
            # Разворачиваем
            routes_container.height = "100dp"
            routes_container.opacity = 1
            self.is_expanded = True


class BusApp(MDApp):
    def on_switch_tabs(self, *args):
        index = list(reversed(args[0].children)).index(args[1])
        screens = ["favorites", "stops", "about"]
        self.root.ids.screen_manager.current = screens[index]

    def build(self):
        return Builder.load_string(KV)


if __name__ == "__main__":
    BusApp().run()