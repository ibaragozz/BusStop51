from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.label import Label
import json


class RouteButton(MDBoxLayout):
    def __init__(self, route, minutes, color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (None, None)
        self.size = ("80dp", "40dp")
        self.md_bg_color = color
        self.radius = [10]

        # Простой текст
        self.add_widget(Label(
            text=f"{route} ({minutes} мин)",
            color=(1, 1, 1, 1),
            bold=True,
            size_hint=(1, 1)
        ))


class StopCard(MDCard):
    def __init__(self, stop_name, routes, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 120
        self.padding = "10dp"
        self.spacing = "5dp"
        self.radius = [15]

        # Заголовок остановки - используем правильный стиль
        self.add_widget(MDLabel(
            text=stop_name,
            font_style="Title",  # Используем "Title" вместо "H6"
            size_hint_y=None,
            height=30
        ))

        # Кнопки маршрутов
        btn_row = MDBoxLayout(orientation="horizontal", spacing="5dp", size_hint_y=None, height=40)
        for route, minutes, color in routes:
            btn = RouteButton(route, minutes, color)
            btn_row.add_widget(btn)
        self.add_widget(btn_row)


class AllStopsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll = MDScrollView()
        self.stops_box = MDBoxLayout(
            orientation="vertical",
            padding="10dp",
            spacing="10dp",
            size_hint_y=None
        )
        self.stops_box.bind(minimum_height=self.stops_box.setter('height'))
        self.scroll.add_widget(self.stops_box)
        self.add_widget(self.scroll)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.update_stops())

    def update_stops(self):
        self.stops_box.clear_widgets()

        # Тестовые данные
        stops_data = [
            ("Остановка 1", [("12", 5, (0.8, 0.3, 0.3, 1)), ("25", 12, (0.3, 0.8, 0.3, 1))]),
            ("Остановка 2", [("7", 3, (0.3, 0.3, 0.8, 1))]),
        ]

        for stop_name, routes in stops_data:
            card = StopCard(stop_name, routes)
            self.stops_box.add_widget(card)


class FavoritesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll = MDScrollView()
        self.favorites_box = MDBoxLayout(
            orientation="vertical",
            padding="10dp",
            spacing="10dp",
            size_hint_y=None
        )
        self.favorites_box.bind(minimum_height=self.favorites_box.setter('height'))
        self.scroll.add_widget(self.favorites_box)
        self.add_widget(self.scroll)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.update_favorites())

    def update_favorites(self):
        self.favorites_box.clear_widgets()
        self.favorites_box.add_widget(MDLabel(
            text="Здесь будут избранные остановки",
            halign="center"
        ))


class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(MDLabel(
            text="Расписание автобусов\nРазработчик: Вы",
            halign="center"
        ))


class BusApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        # Создаем ScreenManager
        screen_manager = ScreenManager()

        # Создаем экраны
        stops_screen = AllStopsScreen(name="stops")
        favorites_screen = FavoritesScreen(name="favorites")
        about_screen = AboutScreen(name="about")

        # Добавляем экраны в менеджер
        screen_manager.add_widget(favorites_screen)
        screen_manager.add_widget(stops_screen)
        screen_manager.add_widget(about_screen)

        # Создаем основной layout
        main_layout = MDBoxLayout(orientation="vertical")
        main_layout.add_widget(screen_manager)

        # Создаем нижнюю панель навигации с иконками
        nav_bar = MDBoxLayout(
            size_hint_y=None,
            height="56dp",
            md_bg_color=(0.95, 0.95, 0.95, 1),
            spacing="5dp",
            padding="5dp"
        )

        # Кнопки навигации с иконками
        favorites_btn = MDIconButton(
            icon="star",
            on_release=lambda x: setattr(screen_manager, 'current', 'favorites')
        )
        stops_btn = MDIconButton(
            icon="bus",
            on_release=lambda x: setattr(screen_manager, 'current', 'stops')
        )
        about_btn = MDIconButton(
            icon="information",
            on_release=lambda x: setattr(screen_manager, 'current', 'about')
        )

        nav_bar.add_widget(favorites_btn)
        nav_bar.add_widget(stops_btn)
        nav_bar.add_widget(about_btn)

        main_layout.add_widget(nav_bar)

        return main_layout


if __name__ == "__main__":
    BusApp().run()