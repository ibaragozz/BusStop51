from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class HelloWorldApp(App):
    def build(self):
        # Создаем контейнер
        layout = BoxLayout()

        # Создаем текст
        label = Label(
            text='Hello World!',
            font_size='24sp',
            color=(1, 0.2, 0.2, 1)  # RGB + прозрачность
        )

        # Добавляем текст в контейнер
        layout.add_widget(label)
        return layout


# Запускаем приложение
if __name__ == '__main__':
    HelloWorldApp().run()