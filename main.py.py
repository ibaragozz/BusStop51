from kivy.app import App

from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import escape_markup
from datetime import datetime, time

current_time = datetime.now().time() #Текущее время
week = datetime.now().isoweekday() #Текущий день недели

# РАСПИСАНИЕ АВТОБУСА №1
# Расписание автобуса 1 от Комсомольской

K1d_1 = time(7, 5)
K1d_2 = time(7, 48)
K1d_3 = time(8, 31)
K1d_4 = time(11, 9)
K1d_5 = time(11, 52)
K1d_6 = time(12, 35)
K1d_7 = time(14, 37)
K1d_8 = time(15, 20)
K1d_9 = time(16, 3)
K1d_10 = time(18, 31)
K1d_11 = time(19, 14)
K1d_12 = time(21, 30)

K1d = [K1d_1,K1d_2,K1d_3,K1d_4,K1d_5,K1d_6,K1d_7,K1d_8,K1d_9,K1d_10,K1d_11,K1d_12]

if week == 7:
        K1d.remove(K1d_1)
        K1d.remove(K1d_2)
        K1d.remove(K1d_3)
        K1d.remove(K1d_12)

# Расписание автобуса 1 от Морвокзала

М1d_1 = time(7, 20)
М1d_2 = time(8, 3)
М1d_3 = time(8, 46)
М1d_4 = time(10, 8)
М1d_5 = time(11, 24)
М1d_6 = time(12, 7)
М1d_7 = time(12, 50)
М1d_8 = time(14, 6)
М1d_9 = time(14, 52)
М1d_10 = time(15, 35)
М1d_11 = time(16, 18)
М1d_12 = time(17, 30)
М1d_13 = time(18, 46)
М1d_14 = time(19, 29)
М1d_15 = time(21, 50)

M1d = [М1d_1,М1d_2,М1d_3,М1d_4,М1d_5,М1d_6,М1d_7,М1d_8,М1d_9,М1d_10,М1d_11,М1d_12,М1d_13,М1d_14,М1d_15]

if week == 7:
        M1d.remove(М1d_1)
        M1d.remove(М1d_2)
        M1d.remove(М1d_3)
        M1d.remove(М1d_15)

# РАСПИСАНИЕ АВТОБУСА №2
# Расписание автобуса 2 от Комсомольской

K2d_1 = time(6, 40)
K2d_2 = time(7, 27)
K2d_3 = time(8, 15)
K2d_4 = time(8, 54)
K2d_5 = time(9, 33)
K2d_6 = time(10, 18)
K2d_7 = time(10, 51)
K2d_8 = time(11, 29)
K2d_9 = time(12, 7)
K2d_10 = time(12, 48)
K2d_11 = time(13, 30)
K2d_12 = time(14, 17)
K2d_13 = time(15, 5)
K2d_14 = time(15, 44)
K2d_15 = time(16, 22)
K2d_16 = time(17, 40)
K2d_17 = time(18, 40)

K2d = [K2d_1,K2d_2,K2d_3,K2d_4,K2d_5,K2d_6,K2d_7,K2d_8,K2d_9,K2d_10,K2d_11,K2d_12,K2d_13,K2d_14,K2d_15,K2d_16,K2d_17]

# Расписание автобуса 2 от Морвокзала
M2d_1 = time(6, 55)
M2d_2 = time(7, 42)
M2d_3 = time(8, 31)
M2d_4 = time(9, 10)
M2d_5 = time(10, 0)
M2d_6 = time(10, 29)
M2d_7 = time(11, 7)
M2d_8 = time(11, 45)
M2d_9 = time(12, 23)
M2d_10 = time(13, 5)
M2d_11 = time(13, 55)
M2d_12 = time(14, 33)
M2d_13 = time(15, 21)
M2d_14 = time(16, 0)
M2d_15 = time(17, 8)
M2d_16 = time(18, 6)

M2d = [M2d_1,M2d_2,M2d_3,M2d_4,M2d_5,M2d_6,M2d_7,M2d_8,M2d_9,M2d_10,M2d_11,M2d_12,M2d_13,M2d_14,M2d_15,M2d_16]

# РАСПИСАНИЕ АВТОБУСА №7
# Расписание автобуса 7 от Комсомольской

K7d_0 = time(9, 4)
K7d_1 = time(9, 14)
K7d_2 = time(13, 51)
K7d_3 = time(16, 46)

K7d = [K7d_1,K7d_2,K7d_3]

if week == 7:
        K7d.insert(0,K7d_0)
        K7d.remove(K7d_1)

# РАСПИСАНИЕ АВТОБУСА №8
# Расписание автобуса 8 от Комсомольской

K8d_0 = time(8, 31)
K8d_1 = time(10, 36)
K8d_2 = time(13, 18)
K8d_3 = time(17, 58)
K8d_4 = time(20, 10)
K8d_5 = time(20, 58)


K8d = [K8d_1,K8d_2,K8d_3,K8d_4,K8d_5]

if week == 7:
        K8d.insert(0,K8d_0)

# Расписание автобуса 8 от Морвокзала
М8d_00 = time(8, 13)
М8d_0 = time(8, 46)
М8d_1 = time(10, 51)
М8d_2 = time(13, 33)
М8d_3 = time(18, 13)
М8d_4 = time(20, 25)
М8d_5 = time(21, 15)

M8d = [М8d_1, М8d_2, М8d_3, М8d_4, М8d_5]

if week == 7:
        M8d.insert(0,М8d_00)
        M8d.insert(1,М8d_0)

class BusStopApp(App):
        result = ""

        def build(self):
                self.bl = BoxLayout(orientation='vertical', padding=25)
                self.lb = Label(text = 'Выберите остановку:', font_size= 15, size_hint=(1, .03))
                self.bl.add_widget(self.lb)

                self.gl = GridLayout(rows=2, spacing = 20, size_hint=(1,.06))

                self.button1 = ToggleButton(text="ул.Комсомольская", font_size= 13, group = 'BS', size_hint=(.5,.1))
                self.button1.bind(on_press=self.button1_pressed)

                self.button2 = ToggleButton(text="Морвокзал", font_size=13, group='BS', size_hint=(.5, .1))
                self.button2.bind(on_press=self.button2_pressed)

                self.gl.add_widget(self.button1)
                self.gl.add_widget(self.button2)
                self.bl.add_widget(self.gl)

                self.label = Label(text='', font_size=15, halign='center', valign='top', size_hint=(1, .1), text_size=(400, 130))



                self.bl.add_widget(self.label)

                return self.bl



        def Комсомольская(self):
                result = ""
                for el in K1d:
                        if current_time < el:
                                result += '[color=#ffbfaa]Автобус №1 : {}[/color]\n'.format(el)
                                break
                if current_time > K1d[-1]:
                        result += '[color=#ff0000]Последний автобус №1 ушел[/color]\n'
                for el in K2d:
                        if current_time < el:
                                result += '[color=#ffff00]Автобус №2 : {}[/color]\n'.format(el)
                                break
                if current_time > K2d[-1]:
                        result += '[color=#ff0000]Последний автобус №2 ушел[/color]\n'
                for el in K7d:
                        if current_time < el:
                                result += '[color=#00ff00]Автобус №7 : {}[/color]\n'.format(el)
                                break
                if current_time > K7d[-1]:
                        result += '[color=#ff0000]Последний автобус №7 ушел[/color]\n'
                for el in K8d:
                        if current_time < el:
                                result += '[color=#9966cc]Автобус №8 : {}[/color]\n'.format(el)
                                break
                if current_time > K8d[-1]:
                        result += '[color=#ff0000]Последний автобус №8 ушел[/color]\n'
                self.label.markup = True
                self.label.text = result


        def Морвокзал(self):
                result = ""
                for el in M1d:
                        if current_time < el:
                                result += '[color=#ffbfaa]Автобус №1 : {}[/color]\n'.format(el)
                                break
                if current_time > M1d[-1]:
                        result += '[color=#ff0000]Последний автобус №1 ушел[/color]\n'

                for el in M2d:
                        if current_time < el:
                                result += '[color=#ffff00]Автобус №2 : {}[/color]\n'.format(el)
                                break
                if current_time > M2d[-1]:
                        result += '[color=#ff0000]Последний автобус №2 ушел[/color]\n'

                for el in M8d:
                        if current_time < el:
                                result += '[color=#9966cc]Автобус №8 : {}[/color]\n'.format(el)
                                break
                if current_time > M8d[-1]:
                        result += '[color=#ff0000]Последний автобус №8 ушел[/color]\n'
                self.label.markup = True
                self.label.text = result

        def button1_pressed(self, instance):
                        self.Комсомольская()

        def button2_pressed(self, instance):
                        self.Морвокзал()






if __name__ == '__main__':
    BusStopApp().run()