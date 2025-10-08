from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.metrics import dp
from kivy.lang import Builder
import json, os
from datetime import datetime


with open("schedule.json", "r", encoding="utf-8") as f:
    schedule = json.load(f)

terminal_stops = ["Морвокзал", "ул.Комсомольская", "Авиагородок", "ул.Полярная"]


def minutes_until(time_str):
    """Вычисляет минуты до времени автобуса"""
    now = datetime.now()
    try:
        bus_time = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        diff = (bus_time - now).total_seconds() / 60
        if diff < 0:
            diff += 24 * 60  # если уже прошло — на завтра
        return int(diff)
    except:
        return 999


class StopCard(MDCard):
    def __init__(self, stop_name, routes, favorite=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(10)
        self.radius = [15]
        self.md_bg_color = (1, 1, 1, 1)
        self.elevation = 3
        self.stop_name = stop_name
        self.routes = routes
        self.favorite = favorite

        # Разделим название и сторону
        if "(" in stop_name and ")" in stop_name:
            name_part = stop_name.split("(")[0].strip()
            direction = stop_name[stop_name.find("(")+1:stop_name.find(")")]
        else:
            name_part = stop_name
            direction = ""

        # Верхняя строка: название и звезда
        top_row = MDBoxLayout(orientation="horizontal", adaptive_height=True)
        top_row.add_widget(MDLabel(text=name_part, font_style="TitleMedium", bold=True))
        star_icon = "star" if favorite else "star-outline"
        self.star_button = MDIconButton(icon=star_icon)
        top_row.add_widget(self.star_button)
        self.add_widget(top_row)

        # Подзаголовок (сторона)
        if direction:
            self.add_widget(MDLabel(text=direction, font_style="BodySmall", theme_text_color="Secondary"))

        # Раздел маршрутов
        route_row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(6), padding=(0, dp(6)))
        for route_num, times in routes.items():
            next_time = times[0]
            mins = minutes_until(next_time)
            if mins <= 5:
                color = (1, 0.4, 0.4, 1)
            elif mins <= 10:
                color = (1, 0.7, 0.3, 1)
            else:
                color = (0.5, 0.9, 0.5, 1)

            # Кнопка маршрута
            btn = MDRaisedButton(
                text=f"{route_num} ({mins} мин)",
                md_bg_color=color,
                text_color=(0, 0, 0, 1),
                elevation=0,
            )
            route_row.add_widget(btn)

        self.add_widget(route_row)


class AllStopsScreen(MDScreen):
    def on_pre_enter(self):
        self.ids.stops_box.clear_widgets()
        for stop, routes in schedule.items():
            card = StopCard(stop, routes)
            self.ids.stops_box.add_widget(card)


class BusApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_file("main.kv")


if __name__ == "__main__":
    BusApp().run()
