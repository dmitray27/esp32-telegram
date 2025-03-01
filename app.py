from flask import Flask, render_template, jsonify
from datetime import datetime
import requests
import json
import re

app = Flask(__name__)

DATA_URL = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/tem.txt"

def fix_timestamp_format(timestamp_str):
    match = re.match(r"(\d{4}-\d{2}-)(\d{2})(\d{1,2}:\d{2}:\d{2}[+-]\d{4})", timestamp_str)
    return f"{match.group(1)}{match.group(2)} {match.group(3)}" if match else timestamp_str

def get_sensor_data():
    try:
        response = requests.get(
            DATA_URL,
            headers={'Cache-Control': 'no-cache'},
            timeout=5
        )
        response.raise_for_status()
        
        raw_data = response.text.lstrip('\ufeff').strip()
        print(f"Raw data received:\n{raw_data}")  # Для диагностики
        
        data = json.loads(raw_data)

        if not isinstance(data.get('temperature'), (float, int)):
            raise ValueError("Некорректный формат температуры")
            
        fixed_timestamp = fix_timestamp_format(data['timestamp'])
        dt = datetime.fromisoformat(fixed_timestamp.replace('Z', '+00:00'))

        return {
            "temperature": float(data['temperature']),
            "unit": "°C",
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "error": None
        }

    except json.JSONDecodeError as e:
        return {"error": f"Ошибка формата JSON: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Сетевая ошибка: {str(e)}"}
    except Exception as e:
        return {"error": f"Ошибка обработки: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def api_data():
    return jsonify(get_sensor_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)