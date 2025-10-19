from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
import json
from kivy.properties import StringProperty
from datetime import datetime
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout

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
            MDBoxLayout:
                orientation: "vertical"
                spacing: "10dp"
                padding: "10dp"

                MDTextField:
                    id: search_field
                    hint_text: "Поиск остановки..."
                    mode: "outlined"
                    size_hint_x: 0.9
                    pos_hint: {"center_x": 0.5}
                    on_text: app.filter_stops(self.text)

                ScrollView:
                    MDBoxLayout:
                        id: stops_container
                        orientation: "vertical"
                        padding: "10dp"
                        spacing: "10dp"
                        adaptive_height: True

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
        height: 0
        opacity: 0
        orientation: "vertical"
        spacing: "10dp"
        adaptive_height: True
'''


def create_route_card(route_number, time_list):
    """Создает карточку маршрута (только номер + цвет фона)"""
    # Вычисляем ближайшее время
    from datetime import time
    test_time = time(12, 0)  # 12:00 для тестирования
    now = datetime.now().replace(hour=test_time.hour, minute=test_time.minute, second=0, microsecond=0)

    nearest_time = None
    min_minutes = float('inf')

    for time_str in time_list:
        bus_time = datetime.strptime(time_str, "%H:%M").time()
        bus_datetime = datetime.combine(now.date(), bus_time)

        if bus_datetime < now:
            continue

        minutes = (bus_datetime - now).total_seconds() / 60
        if minutes < min_minutes:
            min_minutes = minutes
            nearest_time = time_str

    is_active = nearest_time is not None
    minutes_left = int(min_minutes) if nearest_time else -1

    # Определяем цвет по реальной логике
    if minutes_left < 0:
        color = [0.7, 0.7, 0.7, 1]  # Серый
    elif minutes_left <= 5:
        color = [1, 0.3, 0.3, 1]  # Красный
    elif minutes_left <= 15:
        color = [1, 0.8, 0.3, 1]  # Желтый
    else:
        color = [0.3, 0.8, 0.3, 1]  # Зеленый

    # Создаем карточку
    card = MDCard(
        size_hint=(None, None),
        size=("70dp", "50dp"),
        padding="5dp",
        radius="8dp",
        md_bg_color=color
    )

    # Только номер маршрута по центру
    route_label = MDLabel(
        text=route_number,
        theme_text_color="Primary",
        bold=True,
        halign="center",
        valign="middle"
    )

    card.add_widget(route_label)
    return card, is_active


class StopCard(MDCard):
    stop_name = StringProperty("Остановка")

    def __init__(self, stop_name="Остановка", **kwargs):
        super().__init__(**kwargs)
        self.stop_name = stop_name
        self.is_expanded = False
        self.is_favorite = False

    def toggle_favorite(self):
        if self.is_favorite:
            self.ids.favorite_btn.icon = "star-outline"
            self.is_favorite = False
        else:
            self.ids.favorite_btn.icon = "star"
            self.is_favorite = True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not self.ids.favorite_btn.collide_point(*touch.pos):
                self.toggle_expand()
        return super().on_touch_down(touch)

    def toggle_expand(self):
        routes_container = self.ids.routes_container
        if self.is_expanded:
            routes_container.height = 0
            routes_container.opacity = 0
            self.is_expanded = False
        else:
            self.create_route_cards()
            routes_container.height = routes_container.minimum_height
            routes_container.opacity = 1
            self.is_expanded = True

    def create_route_cards(self):
        """Создает карточки маршрутов в рядах по 4 штуки"""
        routes_container = self.ids.routes_container
        routes_container.clear_widgets()

        app = MDApp.get_running_app()
        stop_data = app.schedule_data.get(self.stop_name, {})

        active_routes = []
        for route_number, time_list in stop_data.items():
            route_card, is_active = create_route_card(route_number, time_list)
            if is_active:
                active_routes.append(route_card)

        if not active_routes:
            self.show_no_buses_message()
            return

        # Создаем ряды по 4 карточки
        for i in range(0, len(active_routes), 4):
            row_cards = active_routes[i:i + 4]

            row = BoxLayout(
                orientation="horizontal",
                spacing="10dp",
                size_hint_y=None,
                height="60dp"
            )

            for card in row_cards:
                row.add_widget(card)

            routes_container.add_widget(row)

    def show_no_buses_message(self):
        """Показывает сообщение что автобусов нет"""
        routes_container = self.ids.routes_container
        message_label = MDLabel(
            text="Автобусов на сегодня больше нет",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height="30dp"
        )
        routes_container.add_widget(message_label)


class BusApp(MDApp):
    def build(self):
        root = Builder.load_string(KV)
        self.schedule_data = self.load_schedule()

        stops_container = root.ids.stops_container
        stops_container.clear_widgets()

        for stop_name in self.schedule_data.keys():
            card = StopCard(stop_name=stop_name)
            stops_container.add_widget(card)

        return root

    def load_schedule(self):
        """Загружает расписание из JSON файла"""
        try:
            with open('schedule.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Файл schedule.json не найден!")
            return {}
        except Exception as e:
            print(f"Ошибка загрузки JSON: {e}")
            return {}

    def filter_stops(self, search_text):
        """Фильтрует карточки по тексту поиска"""
        stops_container = self.root.ids.stops_container
        stops_container.clear_widgets()

        search_text = search_text.lower().strip()

        for stop_name in self.schedule_data.keys():
            if not search_text or search_text in stop_name.lower():
                card = StopCard(stop_name=stop_name)
                stops_container.add_widget(card)

    def on_switch_tabs(self, *args):
        index = list(reversed(args[0].children)).index(args[1])
        screens = ["favorites", "stops", "about"]
        self.root.ids.screen_manager.current = screens[index]


if __name__ == "__main__":
    BusApp().run()