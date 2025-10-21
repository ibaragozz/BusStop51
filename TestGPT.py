from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.uix.label import Label
from kivy.metrics import dp
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


# ---------------------------
# Помощники по времени/цветам
# ---------------------------
def parse_time_str_to_dt(time_str, base_date):
    """Парсит 'HH:MM' в datetime на base_date. Возвращает None при ошибке."""
    try:
        t = datetime.strptime(time_str.strip(), "%H:%M").time()
        return datetime.combine(base_date, t)
    except Exception:
        return None


def compute_next_time_and_minutes(time_list, now=None):
    """
    time_list: список строк "HH:MM"
    Возвращает (nearest_time_str_or_None, minutes_left_int_or_None)
    """
    now = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    if now is None:
        now = datetime.now()

    base_date = now.date()
    min_minutes = None
    nearest_str = None

    for ts in time_list:
        dt = parse_time_str_to_dt(ts, base_date)
        if dt is None:
            continue
        # если автобус уже ушёл сегодня, пропускаем
        if dt < now:
            continue
        minutes = (dt - now).total_seconds() / 60
        if min_minutes is None or minutes < min_minutes:
            min_minutes = minutes
            nearest_str = ts

    if nearest_str is None:
        print(f"DEBUG: Нет активных автобусов для {time_list}")
        return None, None

    print(f"DEBUG: Ближайший {nearest_str}, через {int(min_minutes)} мин")
    return nearest_str, int(min_minutes)


def urgency_color_by_minutes(minutes):
    """Возвращает rgba tuple по числу минут (int)."""
    if minutes is None:
        return (0.7, 0.7, 0.7, 1)  # серый
    if minutes <= 5:
        return (1, 0.3, 0.3, 1)  # красный
    if minutes <= 15:
        return (1, 0.8, 0.3, 1)  # желтый
    return (0.3, 0.8, 0.3, 1)  # зеленый


# ---------------------------
# Виджеты: RouteCard, StopCard
# ---------------------------
class RouteCard(MDCard):
    """
    Маленькая карточка маршрута: номер сверху, ближайшее время снизу.
    Имеет метод update() — пересчитывает ближайшее время и цвет.
    """
    route_number = StringProperty("")
    time_list = ListProperty([])  # список строк "HH:MM"

    def __init__(self, route_number: str, time_list: list, **kwargs):
        super().__init__(**kwargs)
        self.route_number = str(route_number)
        self.time_list = time_list or []
        self.size_hint = (None, None)
        self.size = (dp(70), dp(50))
        self.padding = dp(5)
        self.radius = [8]
        self.md_bg_color = (0.7, 0.7, 0.7, 1)  # Серый по умолчанию

        # Контент
        self.container = BoxLayout(orientation="vertical")
        self.lbl_number = Label(
            text=self.route_number,
            font_size="16sp",
            bold=True,
            color=(0, 0, 0, 1),
            halign="center",
            size_hint_y=0.6
        )
        self.lbl_time = Label(
            text="---",  # По умолчанию ---
            font_size="12sp",
            color=(0, 0, 0, 1),
            halign="center",
            size_hint_y=0.4
        )

        self.container.add_widget(self.lbl_number)
        self.container.add_widget(self.lbl_time)
        self.add_widget(self.container)

    def update(self, now=None):
        # Вычисляем время только когда вызывается явно
        nearest_str, minutes_left = compute_next_time_and_minutes(self.time_list, now=now)
        if nearest_str is None:
            self.lbl_time.text = "---"
            self.md_bg_color = (0.7, 0.7, 0.7, 1)  # Серый
        else:
            self.lbl_time.text = nearest_str
            self.md_bg_color = urgency_color_by_minutes(minutes_left)


class StopCard(MDCard):
    stop_name = StringProperty("")
    is_favorite = BooleanProperty(False)

    def __init__(self, stop_name: str, schedule_for_stop: dict, app_ref: MDApp, is_favorite=False, **kwargs):
        super().__init__(**kwargs)
        self.stop_name = stop_name
        self.size_hint_y = None
        self.height = dp(60)  # Фиксированная начальная высота
        self.padding = dp(10)
        self.spacing = dp(8)
        self.orientation = "vertical"
        self.radius = [12]
        self.app_ref = app_ref
        self.schedule_for_stop = schedule_for_stop or {}
        self.is_favorite = is_favorite
        self.is_expanded = False

        # header
        header = BoxLayout(size_hint_y=None, height=dp(48))
        self.lbl_name = Label(
            text=self.stop_name,
            halign="left",
            valign="middle",
            bold=True,
            color=(0, 0, 0, 1)
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

        # routes container (скрыт по умолчанию)
        self.routes_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=0,
            spacing=dp(8)
        )
        self.add_widget(self.routes_container)

        self.route_cards = []
        self._prepare_route_cards()

        if self.is_favorite:
            self.expand(animate=False)

    def _prepare_route_cards(self):
        """Создаёт RouteCard'ы для всех маршрутов этой остановки"""
        self.route_cards.clear()
        # schedule_for_stop: dict route-> list of times
        for rnum, times in self.schedule_for_stop.items():
            rc = RouteCard(route_number=rnum, time_list=times)
            self.route_cards.append(rc)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # исключаем нажатие по кнопке избранного
            if self.btn_fav.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            # переключаем раскрытие
            self.toggle_expand()
            return True
        return super().on_touch_down(touch)

    def on_fav_pressed(self, instance):
        if self.is_favorite:
            self.is_favorite = False
            self.btn_fav.icon = "star-outline"
            self.app_ref.remove_from_favorites(self.stop_name)
            # при убирании из избранного не нужно автоматически сворачивать
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

        self.routes_container.clear_widgets()
        self._prepare_route_cards()

        active_cards = []
        for rc in self.route_cards:
            # ВЫЗЫВАЕМ UPDATE ТОЛЬКО ЗДЕСЬ - при раскрытии!
            rc.update()
            if rc.lbl_time.text != "---":
                active_cards.append(rc)

        if not active_cards:
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

        # строки по 4 карточки
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

    def collapse(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        self.routes_container.clear_widgets()
        self.routes_container.height = 0
        self.height = dp(60)  # только заголовок

    def refresh_route_cards(self, now=None):
        """Обновляет существующие RouteCard'ы (цвет/текст) в текущем состоянии (если раскрыто)"""
        # обновим данные route_cards
        for rc in self.route_cards:
            rc.update(now=now)
        # если раскрыто — также обновить визуал контейнера (но не перестраивать)
        if self.is_expanded:
            # Здесь мы не перестраиваем активные/неактивные — но обновляем тексты/цвета.
            # Если во время работы некоторые маршруты перестали быть активны (все ушли) -
            # логика текущей реализации оставит их на месте до повторного открытия/перестроения.
            # Для простоты — при каждом refresh не перестраиваем ряды, чтобы избежать мерцания.
            pass


# ---------------------------
# Основное приложение
# ---------------------------
class BusApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule_file = "schedule.json"
        self.favorites_file = "favorites.json"
        self.schedule_data = {}
        self.stop_cards = {}
        self.update_interval = 30
        self.favorites = set()
        self._root_initialized = False  # Добавляем этот флаг

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        root = Builder.load_string(KV)

        # Быстрая загрузка данных
        self.schedule_data = self.load_schedule()
        self.favorites = self.load_favorites()

        # Откладываем построение интерфейса для скорости
        Clock.schedule_once(self._finish_build, 0.1)
        return root

    def _finish_build(self, dt):
        """Быстрая инициализация UI"""
        try:
            # Основной экран остановок
            stops_container = self.root.ids.stops_container
            stops_container.clear_widgets()
            self.stop_cards.clear()

            # ТОЛЬКО создаем карточки, без лишней логики
            for stop_name, routes in self.schedule_data.items():
                card = StopCard(
                    stop_name=stop_name,
                    schedule_for_stop=routes,
                    app_ref=self,
                    is_favorite=(stop_name in self.favorites)
                )
                self.stop_cards[stop_name] = card
                stops_container.add_widget(card)

            # Экран избранного
            fav_container = self.root.ids.favorites_container
            fav_container.clear_widgets()
            for stop_name in self.favorites:
                routes = self.schedule_data.get(stop_name, {})
                card = StopCard(
                    stop_name=stop_name,
                    schedule_for_stop=routes,
                    app_ref=self,
                    is_favorite=True
                )
                card.expand()
                fav_container.add_widget(card)

            # Запускаем периодическое обновление
            Clock.schedule_interval(self._periodic_update, self.update_interval)
            Clock.schedule_once(lambda dt: self._periodic_update(0), 0.5)

            self._root_initialized = True  # Устанавливаем флаг

        except Exception as e:
            print(f"Ошибка инициализации: {e}")

    # ---------------------------
    # Файловые операции
    # ---------------------------
    def load_schedule(self):
        if not os.path.exists(self.schedule_file):
            print(f"Файл {self.schedule_file} не найден!")
            return {}
        try:
            with open(self.schedule_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Ошибка загрузки schedule.json:", e)
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
        except Exception:
            return set()

    def save_favorites(self):
        try:
            with open(self.favorites_file, "w", encoding="utf-8") as f:
                json.dump(list(self.favorites), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Ошибка сохранения favorites.json:", e)

    def add_to_favorites(self, stop_name):
        self.favorites.add(stop_name)
        self.save_favorites()
        # Обновляем экран избранного
        fav_container = self.root.ids.favorites_container
        # Проверяем дубли
        for child in fav_container.children:
            if getattr(child, "stop_name", None) == stop_name:
                return
        routes = self.schedule_data.get(stop_name, {})
        card = StopCard(stop_name=stop_name, schedule_for_stop=routes, app_ref=self, is_favorite=True)
        card.expand()
        fav_container.add_widget(card)

    def remove_from_favorites(self, stop_name):
        if stop_name in self.favorites:
            self.favorites.remove(stop_name)
            self.save_favorites()
            # Удаляем из экрана избранного
            fav_container = self.root.ids.favorites_container
            for child in list(fav_container.children):
                if getattr(child, "stop_name", None) == stop_name:
                    fav_container.remove_widget(child)
                    break

    # ---------------------------
    # Обновление UI
    # ---------------------------
    def _periodic_update(self, dt):
        if not self._root_initialized:
            return

        now = datetime.now()
        # Обновляем все карточки остановок
        for stop_card in self.stop_cards.values():
            if stop_card.is_expanded:  # ТОЛЬКО если раскрыта!
                stop_card.refresh_route_cards(now=now)
        # Обновляем карточки в избранном
        try:
            fav_container = self.root.ids.favorites_container
            for child in fav_container.children:
                if isinstance(child, StopCard):
                    child.refresh_route_cards(now=now)
        except Exception as e:
            print(f"Ошибка обновления избранного: {e}")

    # ---------------------------
    # Поиск и навигация
    # ---------------------------
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
