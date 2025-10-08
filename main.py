from kivy.clock import Clock
from datetime import datetime
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.label import Label

from kivy.core.window import Window
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

        # Определяем цвет на основе времени до автобуса
        self.md_bg_color = self.get_time_color(next_time)

        # Номер маршрута
        self.add_widget(Label(
            text=str(route_number),
            font_size='18sp',
            bold=True,
            color=(0, 0, 0, 1),
            halign="center",
            size_hint_y=0.6
        ))

        # Время следующего автобуса
        self.add_widget(Label(
            text=next_time,
            font_size='12sp',
            color=(0, 0, 0, 1),
            halign="center",
            size_hint_y=0.4
        ))

    def get_time_color(self, next_time_str):
        """Возвращает цвет в зависимости от времени до автобуса"""
        try:
            # Получаем текущее время
            now = datetime.now()

            # Парсим время автобуса
            bus_time = datetime.strptime(next_time_str, "%H:%M")
            bus_time = bus_time.replace(year=now.year, month=now.month, day=now.day)

            # Если время автобуса уже прошло сегодня, предполагаем что это на следующий день
            if bus_time < now:
                bus_time = bus_time.replace(day=now.day + 1)

            # Вычисляем разницу в минутах
            time_diff = (bus_time - now).total_seconds() / 60

            # Определяем цвет на основе времени
            if time_diff <= 5:
                return (1, 0.3, 0.3, 1)  # Красный - меньше 5 минут
            elif time_diff <= 15:
                return (1, 0.8, 0.3, 1)  # Желтый - 6-15 минут
            else:
                return (0.3, 0.8, 0.3, 1)  # Зеленый - больше 15 минут

        except ValueError:
            # Если время в неправильном формате, возвращаем серый цвет
            return (0.8, 0.8, 0.8, 1)

    def is_bus_coming_today(self, next_time_str):
        """Проверяет, будет ли автобус сегодня"""
        try:
            now = datetime.now()
            bus_time = datetime.strptime(next_time_str, "%H:%M")
            bus_time = bus_time.replace(year=now.year, month=now.month, day=now.day)

            # Если время уже прошло, проверяем есть ли автобусы позже сегодня
            if bus_time < now:
                return False
            return True
        except ValueError:
            return False


class StopCard(MDCard):
    def __init__(self, stop_name, routes, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.padding = "10dp"
        self.spacing = "10dp"
        self.radius = [15]

        # Заголовок остановки
        self.add_widget(Label(
            text=stop_name,
            font_size='16sp',
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=30
        ))

        # Фильтруем маршруты - оставляем только те, у которых есть автобусы сегодня
        active_routes = self.filter_active_routes(routes)

        if active_routes:
            # Создаем контейнер для активных маршрутов
            self.routes_container = MDBoxLayout(
                orientation="vertical",
                spacing="10dp",
                size_hint_y=None,
                adaptive_height=True
            )

            # Создаем строки маршрутов
            self.create_route_rows(active_routes)
            self.add_widget(self.routes_container)

            # Вычисляем высоту карточки
            self.calculate_height(active_routes)
        else:
            # Если нет активных маршрутов, показываем сообщение
            self.show_no_buses_message()
            self.height = 80  # Минимальная высота для сообщения

    def filter_active_routes(self, routes):
        """Фильтрует маршруты, оставляя только те, у которых есть автобусы сегодня"""
        active_routes = []
        for route_number, next_time in routes:
            route_info = RouteInfo(route_number, next_time)
            if route_info.is_bus_coming_today(next_time):
                active_routes.append((route_number, next_time))
        return active_routes

    def create_route_rows(self, routes):
        """Создает строки с маршрутами (максимум 4 в строке)"""
        row = MDBoxLayout(
            orientation="horizontal",
            spacing="10dp",
            size_hint_y=None,
            height="50dp"
        )

        for i, route_info in enumerate(routes):
            route_number, next_time = route_info
            route_widget = RouteInfo(route_number, next_time)
            row.add_widget(route_widget)

            # Если в строке уже 4 маршрута или это последний маршрут, создаем новую строку
            if (i + 1) % 4 == 0 and (i + 1) < len(routes):
                self.routes_container.add_widget(row)
                row = MDBoxLayout(
                    orientation="horizontal",
                    spacing="10dp",
                    size_hint_y=None,
                    height="50dp"
                )

        # Добавляем последнюю строку
        if len(row.children) > 0:
            self.routes_container.add_widget(row)

    def calculate_height(self, routes):
        """Вычисляет высоту карточки на основе количества строк маршрутов"""
        # Высота заголовка + отступы
        base_height = 30 + 20  # заголовок + padding

        # Вычисляем количество строк (максимум 4 маршрута в строке)
        num_rows = (len(routes) + 3) // 4  # Округление вверх

        # Высота строк маршрутов + отступы между строками
        routes_height = num_rows * 50 + (num_rows - 1) * 10

        # Общая высота карточки
        self.height = base_height + routes_height + 20  # + дополнительный отступ

    def show_no_buses_message(self):
        """Показывает сообщение, что автобусов больше нет сегодня"""
        message_label = Label(
            text="Автобусов больше нет сегодня",
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            halign="center",
            size_hint_y=None,
            height=40
        )
        self.add_widget(message_label)


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

        # Тестовые данные с разным количеством маршрутов
        stops_data = [
            ("Остановка Центральная", [("12", "15:30"), ("25", "20:42"), ("7", "15:55")]),
            ("Остановка с 5 маршрутами",
             [("1", "16:00"), ("2", "16:05"), ("3", "17:10"), ("4", "16:15"), ("5", "16:20")]),
            ("Остановка с 8 маршрутами", [("6", "16:25"), ("7", "16:30"), ("8", "16:35"), ("9", "16:40"),
                                          ("10", "17:45"), ("11", "17:50"), ("12", "17:55"), ("13", "17:00")]),
            ("Остановка Северная", [("3", "16:10"), ("18", "16:25")]),
            ("Остановка Южная", [("5", "20:38"), ("12", "20:45"), ("22", "20:00"), ("31", "20:15")]),
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
        self.favorites_box.add_widget(Label(
            text="Здесь будут избранные остановки",
            halign="center",
            color=(0.5, 0.5, 0.5, 1)
        ))


class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

        # Создаем экраны
        favorites_screen = FavoritesScreen(name="favorites")
        stops_screen = AllStopsScreen(name="stops")
        about_screen = AboutScreen(name="about")

        # Добавляем экраны в менеджер
        screen_manager.add_widget(favorites_screen)
        screen_manager.add_widget(stops_screen)
        screen_manager.add_widget(about_screen)

        # Устанавливаем стартовый экран
        screen_manager.current = "favorites"

        # Создаем основной layout
        main_layout = MDBoxLayout(orientation="vertical")
        main_layout.add_widget(screen_manager)

        # Создаем нижнюю панель навигации
        nav_bar = MDBoxLayout(
            size_hint_y=None,
            height="56dp",
            md_bg_color=(0.95, 0.95, 0.95, 1),
            spacing="5dp",
            padding="5dp"
        )

        # Кнопки навигации
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