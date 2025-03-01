print("1. Скрипт начал выполнение")  # Добавьте эту строку в САМОЕ НАЧАЛО файла

from flask import Flask, render_template
from datetime import datetime
import requests
import json

print("2. Библиотеки загружены")  # После импортов

app = Flask(__name__)

DATA_URL = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/tem.txt"

def get_sensor_data():
    # ... оставьте функцию как есть ...

@app.route('/')
def index():
    # ... оставьте функцию как есть ...

if __name__ == '__main__':
    print("3. Запуск сервера...")  # Перед app.run()
    app.run(debug=True, host='0.0.0.0', port=5000)