from flask import Flask, render_template, jsonify
from datetime import datetime
import requests
import json

app = Flask(__name__)

DATA_URL = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/tem.txt"

def get_sensor_data():
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
        raw_data = response.text.strip()
        data = json.loads(raw_data)

        temperature = data.get('temperature')
        timestamp = data.get('timestamp')

        if not temperature or not timestamp:
            return {"error": "Некорректные данные в файле"}

        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        return {
            "temperature": temperature,
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка подключения: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Ошибка формата данных"}
    except Exception as e:
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
    app.run(host='0.0.0.0', port=5000)