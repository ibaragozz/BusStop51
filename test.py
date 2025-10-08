# test_imports.py
from kivymd.uix.button import *

print("Доступные классы кнопок:")
for item in dir():
    if 'Button' in item and not item.startswith('_'):
        print(f"  - {item}")