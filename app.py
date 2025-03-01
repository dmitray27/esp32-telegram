from flask import Flask, render_template, jsonify
from datetime import datetime
import requests
import json

app = Flask(__name__)

DATA_URL = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/tem.txt"

def get_sensor_data():
    try:
        print(f"\n[{datetime.now()}] Инициирован запрос к GitHub")
        response = requests.get(
            DATA_URL,
            headers={'Cache-Control': 'no-cache'}
        )
        print(f"[{datetime.now()}] Ответ получен. Код: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        
        raw_data = response.text.strip()
        print(f"Сырые данные: {raw_data}")
        
        data = json.loads(raw_data)
        
        if 'temperature' not in data or 'timestamp' not in data:
            return {"error": "Некорректные данные: отсутствуют ключи"}
            
        dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        return {
            "temperature": data['temperature'],
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "error": None
        }

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