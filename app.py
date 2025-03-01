from flask import Flask, render_template, jsonify
from datetime import datetime
import requests
import json
import re

app = Flask(__name__)

DATA_URL = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/tem.txt"

def fix_timestamp_format(timestamp_str):
    """Исправление формата даты с паттернами типа '2025-02-27711:34:52+0300'"""
    match = re.match(r"(\d{4}-\d{2}-)(\d{2})(\d{1,2}:\d{2}:\d{2}[+-]\d{4})", timestamp_str)
    if match:
        return f"{match.group(1)}{match.group(2)} {match.group(3)}"
    return timestamp_str

def get_sensor_data():
    try:
        print(f"\n[{datetime.now()}] Инициирован запрос к GitHub")
        response = requests.get(
            DATA_URL,
            headers={'Cache-Control': 'no-cache'}
        )
        print(f"[{datetime.now()}] Ответ получен. Код: {response.status_code}")
        print(f"Заголовки ответа: {json.dumps(dict(response.headers), ensure_ascii=False}")

        raw_data = response.text.strip()
        print(f"Сырые данные: {raw_data}")

        data = json.loads(raw_data)

        if 'temperature' not in data or 'timestamp' not in data:
            return {"error": "Некорректные данные: отсутствуют ключи"}

        # Исправление формата timestamp
        fixed_timestamp = fix_timestamp_format(data['timestamp'])
        dt = datetime.fromisoformat(fixed_timestamp.replace('Z', '+00:00'))

        return {
            "temperature": data['temperature'],
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "error": None
        }

    except json.JSONDecodeError:
        return {"error": "Ошибка формата данных: невалидный JSON"}
    except ValueError as ve:
        return {"error": f"Ошибка формата времени: {str(ve)}"}
    except Exception as e:
        import traceback
        print(f"\n[ERROR] {datetime.now()}")
        print(traceback.format_exc())
        return {"error": f"Системная ошибка: {str(e)}"}

@app.route('/')
def index():
    sensor_data = get_sensor_data()
    return render_template('index.html', data=sensor_data)

@app.route('/data')
def data():
    sensor_data = get_sensor_data()
    return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)