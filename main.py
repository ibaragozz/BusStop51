from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
import json


class RouteButton(MDButton):
    def __init__(self, route, minutes, color, **kwargs):
        super().__init__(**kwargs)
        self.text = f"{route} ({minutes} мин)"
        self.md_bg_color = color
        self.theme_text_color = "Custom"
        self.text_color = (1, 1, 1, 1)
        self.size_hint = (None, None)
        self.size = ("80dp", "40dp")


class StopCard(MDCard):
    def __init__(self, stop_name, routes, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 120
        self.padding = 10
        self.spacing = 5

        # Заголовок остановки
        self.add_widget(MDLabel(
            text=stop_name,
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=30
        ))

        # Кнопки маршрутов
        btn_row = BoxLayout(orientation="horizontal", spacing=5, size_hint_y=None, height=40)
        for route, minutes, color in routes:
            btn = RouteButton(route, minutes, color)
            btn_row.add_widget(btn)
        self.add_widget(btn_row)


class AllStopsScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.update_stops())

    def update_stops(self):
        stops_box = self.ids.stops_box
        stops_box.clear_widgets()

        # Тестовые данные
        stops_data = [
            ("Остановка 1", [("12", 5, (0.8, 0.3, 0.3, 1)), ("25", 12, (0.3, 0.8, 0.3, 1))]),
            ("Остановка 2", [("7", 3, (0.3, 0.3, 0.8, 1))]),
        ]

        for stop_name, routes in stops_data:
            card = StopCard(stop_name, routes)
            stops_box.add_widget(card)


class FavoritesScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.update_favorites())

    def update_favorites(self):
        favorites_box = self.ids.favorites_box
        favorites_box.clear_widgets()

        favorites_box.add_widget(MDLabel(
            text="Здесь будут избранные остановки",
            halign="center"
        ))


class AboutScreen(Screen):
    pass


class BusApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        return Builder.load_file("main.kv")


if __name__ == "__main__":
    BusApp().run()