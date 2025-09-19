from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

# Предзаданные остановки
all_stops = [f"Остановка {i}" for i in range(1, 26)]
terminal_stops = ["Морвокзал", "Комсомольская", "Авиагородок", "Полярная"]

# Виджет для строки остановки с кнопкой "избранное"
class StopRow(BoxLayout):
    def __init__(self, stop_name, callback, is_favorite=False, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=40, **kwargs)
        self.stop_name = stop_name
        self.callback = callback
        self.is_favorite = is_favorite

        self.name_button = Button(text=stop_name, size_hint_x=0.8)
        self.name_button.bind(on_release=self.expand_info)

        self.fav_button = Button(text=self.get_icon(), size_hint_x=0.2)
        self.fav_button.bind(on_release=self.toggle_favorite)

        self.add_widget(self.name_button)
        self.add_widget(self.fav_button)

    def get_icon(self):
        # Если не отображаются звезды, используем символы-заглушки
        return "Изб" if self.is_favorite else "+"

    def toggle_favorite(self, instance):
        self.is_favorite = not self.is_favorite
        self.fav_button.text = self.get_icon()
        self.callback("favorite", self.stop_name, self.is_favorite)

    def expand_info(self, instance):
        self.callback("expand", self.stop_name)

# Экран "Избранное"
class FavoriteScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Избранные остановки", size_hint_y=None, height=40)
        self.layout.add_widget(self.label)
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def update_favorites(self, favorites):
        self.grid.clear_widgets()
        if not favorites:
            self.grid.add_widget(Label(
                text="Добавьте остановки в избранное, нажав кнопку '+'.",
                size_hint_y=None, height=40))
        else:
            for stop in favorites:
                title = Label(text=stop, size_hint_y=None, height=30)
                info = Label(text="Ближайший автобус: 10:00", size_hint_y=None, height=30)
                self.grid.add_widget(title)
                self.grid.add_widget(info)

# Экран "Все остановки"
class AllStopsScreen(Screen):
    def __init__(self, update_favorites_callback, **kwargs):
        super().__init__(**kwargs)
        self.favorites = set()
        self.callback = update_favorites_callback

        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Все остановки", size_hint_y=None, height=40)
        self.layout.add_widget(self.label)
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        sorted_stops = terminal_stops + sorted(set(all_stops) - set(terminal_stops))
        self.info_labels = {}

        for stop in sorted_stops:
            row = StopRow(stop_name=stop, callback=self.button_callback)
            self.grid.add_widget(row)

            info_label = Label(text="", size_hint_y=None, height=0)
            self.grid.add_widget(info_label)
            self.info_labels[stop] = info_label

        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def button_callback(self, action, stop_name, is_favorite=None):
        if action == "expand":
            for key, label in self.info_labels.items():
                if key == stop_name:
                    if label.height == 0:
                        label.text = f"Ближайший автобус на {stop_name}: 10:00"
                        label.height = 30
                    else:
                        label.text = ""
                        label.height = 0
                else:
                    label.text = ""
                    label.height = 0
        elif action == "favorite":
            if is_favorite:
                self.favorites.add(stop_name)
            else:
                self.favorites.discard(stop_name)
            self.callback(list(self.favorites))

# Экран "О приложении"
class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        label = Label(text="Приложение расписания автобусов\nРазработчик: Вы\nКонтакты: example@example.com")
        layout.add_widget(label)
        self.add_widget(layout)

# Главное приложение
class MainApp(App):
    def build(self):
        self.favorites = []

        self.sm = ScreenManager(transition=FadeTransition())
        self.favorite_screen = FavoriteScreen(name='favorite')
        self.all_stops_screen = AllStopsScreen(update_favorites_callback=self.update_favorites, name='all_stops')
        self.about_screen = AboutScreen(name='about')

        self.sm.add_widget(self.favorite_screen)
        self.sm.add_widget(self.all_stops_screen)
        self.sm.add_widget(self.about_screen)

        root = BoxLayout(orientation='vertical')
        root.add_widget(self.sm)

        menu = BoxLayout(size_hint_y=None, height=50)
        menu.add_widget(Button(text="Избранное", on_press=lambda x: self.change_screen('favorite')))
        menu.add_widget(Button(text="Остановки", on_press=lambda x: self.change_screen('all_stops')))
        menu.add_widget(Button(text="О приложении", on_press=lambda x: self.change_screen('about')))
        root.add_widget(menu)

        return root

    def change_screen(self, screen_name):
        self.sm.current = screen_name

    def update_favorites(self, new_favorites):
        self.favorites = new_favorites
        self.favorite_screen.update_favorites(self.favorites)

if __name__ == '__main__':
    MainApp().run()
