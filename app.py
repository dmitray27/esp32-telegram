# app.py
from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

# URL сырого файла в GitHub
DATA_URL = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/tem.txt"

def get_sensor_data():
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()  # Проверка на ошибки HTTP
        
        data = response.json()
        
        # Парсинг временной метки
        dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        return {
            "temperature": data['temperature'],
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "error": None
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка получения данных: {str(e)}"}
    except ValueError:
        return {"error": "Ошибка формата данных"}
    except KeyError:
        return {"error": "Некорректная структура данных"}

@app.route('/')
def index():
    sensor_data = get_sensor_data()
    return render_template('index.html', data=sensor_data)

if __name__ == '__main__':
    app.run(debug=True)
