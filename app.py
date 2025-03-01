from flask import Flask, render_template
from datetime import datetime
import requests
import json
from collections import deque
import time

app = Flask(__name__)
GITHUB_URL = "https://raw.githubusercontent.com/dmitray27/esp32/main/tem.txt"

# Ограничим историю последними 10 записями
data_history = deque(maxlen=10)

def fetch_github_data():
    try:
        start_time = time.time()  # Засекаем время начала загрузки
        response = requests.get(
            GITHUB_URL,
            timeout=3,
            headers={'Cache-Control': 'no-cache'}
        )
        response.raise_for_status()
        load_time = time.time() - start_time  # Вычисляем время загрузки
        return response.text.strip(), load_time
    except requests.RequestException as e:
        raise Exception(f"Ошибка получения данных: {str(e)}")

def parse_sensor_data(raw_data):
    try:
        data = json.loads(raw_data)
        dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

        return {
            'temperature': data['temperature'],
            'date': dt.strftime("%Y-%m-%d"),
            'time': dt.strftime("%H:%M:%S"),
            'error': None
        }
    except (KeyError, json.JSONDecodeError) as e:
        raise ValueError("Некорректный формат данных")
    except ValueError as e:
        raise ValueError(f"Ошибка времени: {str(e)}")

@app.after_request
def disable_caching(response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response

@app.route('/')
def index():
    try:
        raw_data, load_time = fetch_github_data()  # Получаем данные и время загрузки
        sensor_data = parse_sensor_data(raw_data)
        data_history.append(sensor_data)  # Добавляем данные в историю
    except Exception as e:
        sensor_data = {'error': str(e)}
        load_time = 0  # В случае ошибки время загрузки = 0

    return render_template('index.html', data=sensor_data, history=list(data_history), load_time=load_time)

if __name__ == '__main__':
    app.run(debug=False)