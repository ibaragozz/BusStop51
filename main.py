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


class RouteInfo(MDBoxLayout):
    def __init__(self, route_number, next_time, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = ("70dp", "50dp")
        self.spacing = "2dp"
        self.padding = "5dp"
        self.radius = [8]
        self.md_bg_color = (0.95, 0.95, 0.95, 1)  # Светло-серый фон

        # Номер маршрута (крупный текст) - используем обычный Label
        self.add_widget(Label(
            text=str(route_number),
            font_size='18sp',
            bold=True,
            color=(0, 0, 0, 1),  # Черный цвет
            halign="center",
            size_hint_y=0.6
        ))

        # Время следующего автобуса (мелкий текст) - используем обычный Label
        self.add_widget(Label(
            text=next_time,
            font_size='12sp',
            color=(0.3, 0.3, 0.3, 1),  # Темно-серый цвет
            halign="center",
            size_hint_y=0.4
        ))


class StopCard(MDCard):
    def __init__(self, stop_name, routes, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 140
        self.padding = "10dp"
        self.spacing = "10dp"
        self.radius = [15]

        # Заголовок остановки - используем обычный Label
        self.add_widget(Label(
            text=stop_name,
            font_size='16sp',
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=30
        ))

        # Контейнер для маршрутов
        routes_container = MDBoxLayout(
            orientation="horizontal",
            spacing="10dp",
            size_hint_y=None,
            height=60
        )

        # Добавляем информацию о маршрутах
        for route_info in routes:
            route_number, next_time = route_info
            route_widget = RouteInfo(route_number, next_time)
            routes_container.add_widget(route_widget)

        self.add_widget(routes_container)


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

        # Тестовые данные: (номер_маршрута, время_следующего)
        stops_data = [
            ("Остановка Центральная", [("12", "15:30"), ("25", "15:42"), ("7", "15:55")]),
            ("Остановка Северная", [("3", "16:10"), ("18", "16:25")]),
            ("Остановка Южная", [("5", "15:38"), ("12", "15:45"), ("22", "16:00"), ("31", "16:15")]),
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
        # Используем обычный Label вместо MDLabel
        self.favorites_box.add_widget(Label(
            text="Здесь будут избранные остановки",
            halign="center",
            color=(0.5, 0.5, 0.5, 1)
        ))


class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Используем обычный Label вместо MDLabel
        self.add_widget(Label(
            text="Расписание автобусов\nРазработчик: Вы",
            halign="center",
            font_size='16sp'
        ))


class BusApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        # Создаем ScreenManager
        screen_manager = ScreenManager()

        # Создаем экраны - избранное первым
        favorites_screen = FavoritesScreen(name="favorites")
        stops_screen = AllStopsScreen(name="stops")
        about_screen = AboutScreen(name="about")

        # Добавляем экраны в менеджер
        screen_manager.add_widget(favorites_screen)
        screen_manager.add_widget(stops_screen)
        screen_manager.add_widget(about_screen)

        # Устанавливаем стартовый экран - Избранное
        screen_manager.current = "favorites"

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

        # Кнопки навигации с иконками - избранное первое
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