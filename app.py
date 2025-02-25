# app.py
from flask import Flask, render_template
from datetime import datetime
import os

app = Flask(__name__)

# Путь к локальному файлу tem.txt
DATA_FILE = os.path.join(os.path.dirname(__file__), 'tem.txt')

def get_sensor_data():
    try:
        # Читаем данные из локального файла
        with open(DATA_FILE, 'r') as f:
            content = f.read().strip().split(',')
            
            # Проверяем формат данных (ожидаем: температура,timestamp)
            if len(content) != 2:
                return {"error": "Некорректный формат файла"}
                
            temperature, timestamp = content
            
            # Парсим временную метку
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            return {
                "temperature": temperature,
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M:%S"),
                "error": None
            }
            
    except FileNotFoundError:
        return {"error": "Файл tem.txt не найден"}
    except ValueError as e:
        return {"error": f"Ошибка формата данных: {str(e)}"}
    except Exception as e:
        return {"error": f"Неизвестная ошибка: {str(e)}"}

@app.route('/')
def index():
    sensor_data = get_sensor_data()
    return render_template('index.html', data=sensor_data)

if __name__ == '__main__':
    app.run(debug=True)
