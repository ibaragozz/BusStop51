from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemIcon, MDNavigationItemLabel
from kivymd.uix.screen import MDScreen
from kivy.uix.label import Label
from datetime import datetime
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
        self.padding = "0dp"
        self.spacing = "0dp"
        self.radius = [15]
        self.stop_name = stop_name
        self.routes_data = routes
        self.is_expanded = False

        # Основная кнопка-заголовок
        self.header_button = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="50dp",
            md_bg_color=(0.9, 0.9, 0.9, 1),
            radius=[15],
            padding="10dp"
        )

        # Название остановки
        self.header_button.add_widget(Label(
            text=stop_name,
            font_size='16sp',
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_x=0.9,
            halign="left"
        ))

        # Стрелка для индикации состояния
        self.arrow_label = Label(
            text="▼",  # или "▽"
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_x=0.1,
            halign="right",
            font_name="arial"  # Укажи шрифт, который поддерживает Unicode
        )
        self.header_button.add_widget(self.arrow_label)

        # Обработчик нажатия на заголовок
        self.header_button.bind(on_touch_down=self.on_header_touch)
        self.add_widget(self.header_button)

        # Контейнер для содержимого (изначально скрыт)
        self.content_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=0,
            opacity=0,
            padding="10dp",
            spacing="10dp"
        )
        self.add_widget(self.content_container)

        # Начальная высота карточки (только заголовок)
        self.height = 50

    def on_header_touch(self, instance, touch):
        """Обработчик нажатия на заголовок"""
        if instance.collide_point(*touch.pos):
            self.toggle_content()
            return True
        return False

    def toggle_content(self):
        """Переключает состояние развернуто/свернуто"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Разворачивает карточку"""
        if not self.is_expanded:
            self.is_expanded = True
            self.arrow_label.icon = "chevron-up"

            # Очищаем предыдущее содержимое
            self.content_container.clear_widgets()

            # Фильтруем маршруты
            active_routes = self.filter_active_routes(self.routes_data)

            if active_routes:
                # Создаем контейнер для активных маршрутов
                routes_container = MDBoxLayout(
                    orientation="vertical",
                    spacing="10dp",
                    size_hint_y=None,
                    adaptive_height=True
                )

                # Создаем строки маршрутов
                self.create_route_rows(routes_container, active_routes)
                self.content_container.add_widget(routes_container)

                # Вычисляем высоту содержимого
                content_height = self.calculate_content_height(active_routes)
            else:
                # Если нет активных маршрутов, показываем сообщение
                self.show_no_buses_message()
                content_height = 40

            # БЕЗ АНИМАЦИИ - сразу устанавливаем значения
            self.content_container.height = content_height
            self.content_container.opacity = 1

            # Общая высота карточки = заголовок + контент
            self.height = 50 + content_height

    def collapse(self):
        """Сворачивает карточку"""
        if self.is_expanded:
            self.is_expanded = False
            self.arrow_label.icon = "chevron-down"

            # БЕЗ АНИМАЦИИ - сразу устанавливаем значения
            self.content_container.height = 0
            self.content_container.opacity = 0

            # Общая высота карточки = только заголовок
            self.height = 50

    def filter_active_routes(self, routes):
        """Фильтрует маршруты, оставляя только те, у которых есть автобусы сегодня"""
        active_routes = []
        for route_number, next_time in routes:
            route_info = RouteInfo(route_number, next_time)
            if route_info.is_bus_coming_today(next_time):
                active_routes.append((route_number, next_time))
        return active_routes

    def create_route_rows(self, container, routes):
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
                container.add_widget(row)
                row = MDBoxLayout(
                    orientation="horizontal",
                    spacing="10dp",
                    size_hint_y=None,
                    height="50dp"
                )

        # Добавляем последнюю строку
        if len(row.children) > 0:
            container.add_widget(row)

    def calculate_content_height(self, routes):
        """Вычисляет высоту содержимого на основе количества строк маршрутов"""
        if not routes:
            return 40

        # Вычисляем количество строк (максимум 4 маршрута в строке)
        num_rows = (len(routes) + 3) // 4

        # Высота строк маршрутов + отступы
        routes_height = num_rows * 50 + (num_rows - 1) * 10

        return routes_height + 20

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
        self.content_container.add_widget(message_label)


class AllStopsScreen(MDScreen):
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
            ("Остановка Центральная", [("12", "15:30"), ("25", "15:42"), ("7", "15:55")]),
            ("Остановка с 5 маршрутами",
             [("1", "16:00"), ("2", "16:05"), ("3", "16:10"), ("4", "16:15"), ("5", "16:20")]),
            ("Остановка с 8 маршрутами", [("6", "16:25"), ("7", "16:30"), ("8", "16:35"), ("9", "16:40"),
                                          ("10", "16:45"), ("11", "16:50"), ("12", "16:55"), ("13", "17:00")]),
            ("Остановка Северная", [("3", "16:10"), ("18", "16:25")]),
            ("Остановка Южная", [("5", "15:38"), ("12", "15:45"), ("22", "16:00"), ("31", "16:15")]),
        ]

        for stop_name, routes in stops_data:
            card = StopCard(stop_name, routes)
            self.stops_box.add_widget(card)


class FavoritesScreen(MDScreen):
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


class AboutScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(
            text="Расписание автобусов\nРазработчик: Вы",
            halign="center",
            font_size='16sp'
        ))


KV = '''
MDBoxLayout:
    orientation: "vertical"
    md_bg_color: self.theme_cls.backgroundColor

    MDScreenManager:
        id: screen_manager

        FavoritesScreen:
            name: "favorites"

        AllStopsScreen:
            name: "stops"

        AboutScreen:
            name: "about"

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
        item_text = args[3]
        screen_map = {
            "Избранное": "favorites",
            "Остановки": "stops",
            "О приложении": "about"
        }
        self.root.ids.screen_manager.current = screen_map.get(item_text, "favorites")

    def build(self):
        return Builder.load_string(KV)


if __name__ == "__main__":
    BusApp().run()