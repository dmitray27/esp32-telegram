from flask import Flask, render_template
from datetime import datetime
import requests
import json

app = Flask(__name__)
GITHUB_URL = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/tem.txt"

def fetch_github_data():
    try:
        response = requests.get(
            GITHUB_URL,
            timeout=10,
            headers={'Cache-Control': 'no-cache'}  # Явное отключение кэша GitHub
        )
        response.raise_for_status()  # Генерирует исключение для 4xx/5xx статусов
        return response.text.strip()
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
        raw_data = fetch_github_data()
        sensor_data = parse_sensor_data(raw_data)
    except Exception as e:
        sensor_data = {'error': str(e)}

    return render_template('index.html', data=sensor_data)

if __name__ == '__main__':
    app.run(debug=False)  # В продакшене debug должен быть False