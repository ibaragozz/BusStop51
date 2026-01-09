from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
import json
import os

KV = '''
MDBoxLayout:
    orientation: "vertical"

    MDScreenManager:
        id: screen_manager

        MDScreen:
            name: "favorites"
            BoxLayout:
                orientation: "vertical"

                ScrollView:
                    do_scroll_x: False
                    BoxLayout:
                        id: favorites_container
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: "10dp"
                        spacing: "10dp"

        MDScreen:
            name: "stops"
            BoxLayout:
                orientation: "vertical"
                spacing: "8dp"
                padding: "8dp"

                MDTextField:
                    id: search_field
                    hint_text: "Поиск остановки..."
                    mode: "outlined"
                    size_hint_x: 1
                    # Сделаем текст при вводе и курсор чёткими
                    foreground_color: 0, 0, 0, 1      # основной текст (при вводе)
                    cursor_color: 0, 0, 0, 1          # цвет курсора
                    hint_text_color: 0.45, 0.45, 0.45, 1
                    on_text: app.on_search_text(self.text)

                ScrollView:
                    do_scroll_x: False
                    BoxLayout:
                        id: stops_container
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: "10dp"
                        spacing: "10dp"

        MDScreen:
            name: "about"
            BoxLayout:
                orientation: "vertical"
                padding: "20dp"
                Label:
                    text: "Расписание автобусов\\nРазработчик: Вы"
                    halign: "center"
                    font_size: "16sp"

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


class RouteCard(BoxLayout):
    def __init__(self, route_number: str, time_list: list, **kwargs):
        super().__init__(**kwargs)
        self.route_number = str(route_number)
        self.time_list = time_list or []
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(70), dp(50))
        self.padding = dp(5)
        self.spacing = dp(2)

        # Используем ближайшее время только для сегодняшних рейсов
        next_time = self.get_next_time()
        color = self.get_time_color(next_time) if next_time else (0.7, 0.7, 0.7, 1)

        with self.canvas.before:
            Color(*color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])

        self.lbl_number = Label(
            text=self.route_number,
            font_size="16sp",
            bold=True,
            color=(0, 0, 0, 1),
            halign="center",
            size_hint=(1, None),
            height=dp(24),
            text_size=(self.width, None)
        )
        self.lbl_time = Label(
            text=next_time if next_time else "---",
            font_size="12sp",
            color=(0, 0, 0, 1),
            halign="center",
            size_hint=(1, None),
            height=dp(20),
            text_size=(self.width, None)
        )

        self.add_widget(self.lbl_number)
        self.add_widget(self.lbl_time)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, instance, value):
        # обновляем прямоугольник при изменении позиции/размера
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def get_next_time(self, now: datetime = None):
        """
        Находит ближайшее время из self.time_list.
        Учитываются только рейсы **сегодня**, которые ещё не ушли.
        Параметр now позволяет тестировать / передавать текущее время извне.
        """
        if now is None:
            now = datetime.now()
        nearest_time = None
        min_minutes = float('inf')

        for time_str in self.time_list:
            try:
                bus_time = datetime.strptime(time_str, "%H:%M")
                bus_time = bus_time.replace(year=now.year, month=now.month, day=now.day)

                # учитывать только рейсы сегодня, которые ещё не ушли
                if bus_time < now:
                    continue

                minutes = (bus_time - now).total_seconds() / 60
                if minutes < min_minutes:
                    min_minutes = minutes
                    nearest_time = time_str
            except Exception as e:
                # лог для отладки; не прерываем выполнение
                print("parse time error:", e)
                continue

        return nearest_time

    def get_time_color(self, next_time_str, now: datetime = None):
        """
        Возвращает цвет в зависимости от времени до автобуса.
        Если next_time_str None — возвращает серый.
        """
        if not next_time_str:
            return (0.8, 0.8, 0.8, 1)
        try:
            if now is None:
                now = datetime.now()
            bus_time = datetime.strptime(next_time_str, "%H:%M")
            bus_time = bus_time.replace(year=now.year, month=now.month, day=now.day)

            if bus_time < now:
                return (0.8, 0.8, 0.8, 1)

            time_diff = (bus_time - now).total_seconds() / 60

            if time_diff <= 5:
                return (1, 0.3, 0.3, 1)  # Красный
            elif time_diff <= 15:
                return (1, 0.8, 0.3, 1)  # Жёлтый
            else:
                return (0.3, 0.8, 0.3, 1)  # Зелёный

        except Exception as e:
            print("color calc error:", e)
            return (0.8, 0.8, 0.8, 1)

    def update(self, now: datetime = None):
        """
        Обновляет карточку: текст ближайшего рейса и фон.
        Использует переданный now если есть (для тестов/синхронного обновления).
        """
        next_time = self.get_next_time(now=now)
        # пересоздаём canvas.before корректно
        self.canvas.before.clear()
        if next_time:
            self.lbl_time.text = next_time
            with self.canvas.before:
                Color(*self.get_time_color(next_time, now=now))
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        else:
            self.lbl_time.text = "---"
            with self.canvas.before:
                Color(0.7, 0.7, 0.7, 1)
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])


class StopCard(MDCard):
    stop_name = StringProperty("")
    is_favorite = BooleanProperty(False)

    def __init__(self, stop_name: str, app_ref: MDApp, is_favorite=False, **kwargs):
        super().__init__(**kwargs)
        self.stop_name = stop_name
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = dp(10)
        self.spacing = dp(8)
        self.orientation = "vertical"
        self.radius = [12]
        self.app_ref = app_ref
        self.is_favorite = is_favorite
        self.is_expanded = False
        self.routes_data = None

        header = BoxLayout(size_hint_y=None, height=dp(48))
        self.lbl_name = Label(
            text=self.stop_name,
            halign="left",
            valign="middle",
            bold=True,
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=dp(48),
            text_size=(None, None)
        )
        header.add_widget(self.lbl_name)

        self.btn_fav = MDIconButton(
            icon="star" if self.is_favorite else "star-outline",
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_release=self.on_fav_pressed
        )
        header.add_widget(self.btn_fav)
        self.add_widget(header)

        self.routes_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=0,
            spacing=dp(8)
        )
        self.add_widget(self.routes_container)

        # ТОЛЬКО избранные карточки раскрываем при создании
        if self.is_favorite:
            Clock.schedule_once(lambda dt: self.expand(), 0.1)

    def load_routes_data(self):
        if self.routes_data is None:
            self.routes_data = self.app_ref.schedule_data.get(self.stop_name, {})

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.btn_fav.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            self.toggle_expand()
            return True
        return super().on_touch_down(touch)

    def on_fav_pressed(self, instance):
        if self.is_favorite:
            self.is_favorite = False
            self.btn_fav.icon = "star-outline"
            self.app_ref.remove_from_favorites(self.stop_name)
        else:
            self.is_favorite = True
            self.btn_fav.icon = "star"
            self.app_ref.add_to_favorites(self.stop_name)

    def toggle_expand(self):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self, animate=True):
        if self.is_expanded:
            return
        self.is_expanded = True

        self.load_routes_data()
        self.routes_container.clear_widgets()

        # Проверяем наличие активных маршрутов **только сегодня**
        has_active_routes = False
        for time_list in self.routes_data.values():
            next_time = self._get_next_time_for_route(time_list)
            if next_time is not None:
                has_active_routes = True
                break

        if not has_active_routes:
            lbl = Label(
                text="Автобусов на сегодня больше нет",
                halign="center",
                size_hint_y=None,
                height=dp(30),
                color=(0.5, 0.5, 0.5, 1)
            )
            self.routes_container.add_widget(lbl)
            self.routes_container.height = dp(40)
            self.height = dp(60) + dp(40)
            return

        # Иначе — показываем активные маршруты
        active_cards = []
        for route_number, time_list in self.routes_data.items():
            rc = RouteCard(route_number=route_number, time_list=time_list)
            if rc.get_next_time() is not None:
                active_cards.append(rc)

        row_height = dp(60)
        for i in range(0, len(active_cards), 4):
            row = BoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=row_height
            )
            for rc in active_cards[i:i + 4]:
                row.add_widget(rc)
            self.routes_container.add_widget(row)

        num_rows = (len(active_cards) + 3) // 4
        content_height = num_rows * row_height
        self.routes_container.height = content_height
        self.height = dp(60) + content_height

    def _get_next_time_for_route(self, time_list, now: datetime = None):
        """Возвращаем ближайшее время для маршрута только для сегодняшних рейсов."""
        if now is None:
            now = datetime.now()
        nearest_time = None
        min_minutes = float('inf')

        for time_str in time_list:
            try:
                bus_time = datetime.strptime(time_str, "%H:%M")
                bus_time = bus_time.replace(year=now.year, month=now.month, day=now.day)
                if bus_time < now:
                    continue
                minutes = (bus_time - now).total_seconds() / 60
                if minutes < min_minutes:
                    min_minutes = minutes
                    nearest_time = time_str
            except Exception as e:
                print("parse route time error:", e)
                continue

        return nearest_time

    def collapse(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        self.routes_container.clear_widgets()
        self.routes_container.height = 0
        self.height = dp(60)

    def refresh_route_cards(self, now: datetime = None):
        """
        При обновлении пересобираем список карточек маршрутов с учётом текущего времени.
        Если маршрутов сегодня больше нет — показываем сообщение.
        """
        if not self.is_expanded:
            return

        self.load_routes_data()
        self.routes_container.clear_widgets()

        has_active_routes = False
        for time_list in self.routes_data.values():
            next_time = self._get_next_time_for_route(time_list, now=now)
            if next_time is not None:
                has_active_routes = True
                break

        if not has_active_routes:
            lbl = Label(
                text="Автобусов на сегодня больше нет",
                halign="center",
                size_hint_y=None,
                height=dp(30),
                color=(0.5, 0.5, 0.5, 1)
            )
            self.routes_container.add_widget(lbl)
            self.routes_container.height = dp(40)
            self.height = dp(60) + dp(40)
            return

        active_cards = []
        for route_number, time_list in self.routes_data.items():
            rc = RouteCard(route_number=route_number, time_list=time_list)
            if rc.get_next_time(now=now) is not None:
                active_cards.append(rc)

        row_height = dp(60)
        for i in range(0, len(active_cards), 4):
            row = BoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=row_height
            )
            for rc in active_cards[i:i + 4]:
                row.add_widget(rc)
            self.routes_container.add_widget(row)

        num_rows = (len(active_cards) + 3) // 4
        content_height = num_rows * row_height
        self.routes_container.height = content_height
        self.height = dp(60) + content_height


class BusApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule_file = "schedule.json"
        self.favorites_file = "favorites.json"
        self.schedule_data = {}
        self.stop_cards = {}
        self.update_interval = 30
        self.favorites = set()

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        root = Builder.load_string(KV)
        Clock.schedule_once(self._fast_init, 0.1)
        return root

    def _fast_init(self, dt):
        try:
            self.schedule_data = self.load_schedule_structure()
            self.favorites = self.load_favorites()

            stops_container = self.root.ids.stops_container
            stops_container.clear_widgets()
            self.stop_cards.clear()

            # ВСЕ КАРТОЧКИ В "ОСТАНОВКАХ" СОЗДАЮТСЯ СВЕРНУТЫМИ
            for stop_name in self.schedule_data.keys():
                card = StopCard(
                    stop_name=stop_name,
                    app_ref=self,
                    is_favorite=(stop_name in self.favorites)
                )
                self.stop_cards[stop_name] = card
                stops_container.add_widget(card)

            Clock.schedule_once(self._init_favorites, 0.2)
            Clock.schedule_interval(self._periodic_update, self.update_interval)

        except Exception as e:
            print(f"Ошибка инициализации: {e}")

    def _init_favorites(self, dt):
        fav_container = self.root.ids.favorites_container
        fav_container.clear_widgets()
        for stop_name in self.favorites:
            card = StopCard(
                stop_name=stop_name,
                app_ref=self,
                is_favorite=True
            )
            fav_container.add_widget(card)

    def load_schedule_structure(self):
        if not os.path.exists(self.schedule_file):
            return {}
        try:
            with open(self.schedule_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.schedule_data = data
                return data
        except Exception as e:
            print("load schedule error:", e)
            return {}

    def load_favorites(self):
        if not os.path.exists(self.favorites_file):
            return set()
        try:
            with open(self.favorites_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return set(data)
                elif isinstance(data, dict):
                    return set(data.keys())
                return set()
        except Exception as e:
            print("load favorites error:", e)
            return set()

    def save_favorites(self):
        try:
            with open(self.favorites_file, "w", encoding="utf-8") as f:
                json.dump(list(self.favorites), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("save favorites error:", e)

    def add_to_favorites(self, stop_name):
        self.favorites.add(stop_name)
        self.save_favorites()
        fav_container = self.root.ids.favorites_container
        for child in fav_container.children:
            if getattr(child, "stop_name", None) == stop_name:
                return
        card = StopCard(stop_name=stop_name, app_ref=self, is_favorite=True)
        fav_container.add_widget(card)

    def remove_from_favorites(self, stop_name):
        if stop_name in self.favorites:
            self.favorites.remove(stop_name)
            self.save_favorites()
            fav_container = self.root.ids.favorites_container
            for child in list(fav_container.children):
                if getattr(child, "stop_name", None) == stop_name:
                    fav_container.remove_widget(child)
                    break

    def _periodic_update(self, dt):
        now = datetime.now()
        # Обновляем развёрнутые карточки в основном списке
        for stop_card in self.stop_cards.values():
            if stop_card.is_expanded:
                stop_card.refresh_route_cards(now=now)
        # И в избранных
        try:
            fav_container = self.root.ids.favorites_container
            for child in list(fav_container.children):
                if isinstance(child, StopCard) and child.is_expanded:
                    child.refresh_route_cards(now=now)
        except Exception as e:
            print("fav update error:", e)

    def on_search_text(self, text):
        text = (text or "").strip().lower()
        stops_container = self.root.ids.stops_container
        stops_container.clear_widgets()

        for stop_name, card in self.stop_cards.items():
            if not text or text in stop_name.lower():
                stops_container.add_widget(card)

    def on_switch_tabs(self, *args):
        item_text = args[3]
        screen_map = {
            "Избранное": "favorites",
            "Остановки": "stops",
            "О приложении": "about"
        }
        self.root.ids.screen_manager.current = screen_map.get(item_text, "stops")


if __name__ == "__main__":
    BusApp().run()