from flask import Flask, render_template
from datetime import datetime
import requests  # Добавляем импорт
import json

app = Flask(__name__)

# URL к файлу в репозитории GitHub (RAW-ссылка)
DATA_URL = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/tem.txt"

def get_sensor_data():
    try:
        # Загружаем данные из GitHub
        response = requests.get(DATA_URL)
        response.raise_for_status()  # Проверка на ошибки HTTP
        
        raw_data = response.text.strip()
        data = json.loads(raw_data)
        
        # Остальная логика остается без изменений
        temperature = data.get('temperature')
        timestamp = data.get('timestamp')
        
        if not temperature or not timestamp:
            return {"error": "Некорректная структура JSON"}
            
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        return {
            "temperature": temperature,
            "date": dt.strftime("%Y-%m-%d"),
            "time": dt.strftime("%H:%M:%S"),
            "error": None
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка загрузки файла: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Ошибка декодирования JSON"}
    except ValueError as e:
        return {"error": f"Ошибка формата времени: {str(e)}"}
    except Exception as e:
        return {"error": f"Неизвестная ошибка: {str(e)}"}