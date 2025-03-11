# Патчинг gevent должен быть выполнен ПЕРВЫМ
from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from datetime import datetime
import requests
import json
import os
import logging

app = Flask(__name__)
GITHUB_URL = "https://raw.githubusercontent.com/dmitray27/esp32/main/tem.txt"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

@app.route('/health')
def health_check():
    return 'OK', 200

def fetch_github_data():
    try:
        # Добавляем уникальный параметр для обхода кэша
        timestamp = int(datetime.now().timestamp())
        url = f"{GITHUB_URL}?nocache={timestamp}"

        response = requests.get(
            url,
            timeout=5,
            headers={'Cache-Control': 'no-cache'}
        )
        response.raise_for_status()
        
        # Обработка закомментированных строк
        lines = response.text.strip().split('\n')
        valid_lines = [
            line.strip()
            for line in lines
            if line.strip() and not line.startswith(('#', '//'))
        ]
        
        if not valid_lines:
            raise ValueError("Микроконтроллер ESP32 выключен.")
            
        # Берем последнюю актуальную запись
        return valid_lines[-1]
        
    except requests.RequestException as e:
        logging.error(f"Ошибка запроса: {str(e)}")
        raise Exception("Не удалось получить данные")

def parse_sensor_data(raw_data):
    try:
        data = json.loads(raw_data)
        # Исправление формата времени (удаление смещения +0300)
        dt_str = data['timestamp'].replace('+0300', '')
        dt = datetime.fromisoformat(dt_str)

        # Преобразование uptime в "ч. м."
        uptime = data['uptime'].replace("h", "ч.").replace("m", "м.")

        return {
            'temperature': data['temperature'],
            'voltage': data['voltage'],
            'free_heap': data['free_heap'],
            'cpu_freq': data['cpu_freq'],
            'wifi_rssi': data['wifi_rssi'],
            'uptime': uptime,
            'date': dt.strftime("%d.%m.%Y"),  # Измененный формат
            'time': dt.strftime("%H:%M:%S"),
            'error': None
        }
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Ошибка парсинга: {str(e)}")
        raise ValueError("Некорректные данные")

@app.after_request
def disable_caching(response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response

@app.route('/')
def index():
    sensor_data = {'error': None}
    try:
        raw_data = fetch_github_data()
        sensor_data = parse_sensor_data(raw_data)
    except Exception as e:
        sensor_data['error'] = str(e)
        logging.error(f"Ошибка в маршруте /: {str(e)}")

    return render_template('index.html', data=sensor_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
