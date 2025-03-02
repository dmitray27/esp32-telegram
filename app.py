from flask import Flask, request, render_template
import requests
import json
from datetime import datetime
from collections import deque
import git
import os
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')

# Конфигурация GitHub
GITHUB_RAW_URL = "https://raw.githubusercontent.com/dmitray27/esp32/main/tem.txt"
REPO_PATH = "/full/path/to/your/local/repo"  # Абсолютный путь к локальной копии репозитория
REPO_SSH_URL = "git@github.com:dmitray27/esp32-telegram.git"

# Ограничим историю последними 10 записями
data_history = deque(maxlen=10)

def fetch_github_data():
    try:
        start_time = time.time()
        response = requests.get(
            f"{GITHUB_RAW_URL}?t={int(time.time())}",  # Добавляем временную метку против кэширования
            timeout=3,
            headers={'Cache-Control': 'no-cache'}
        )
        response.raise_for_status()
        return response.text.strip(), time.time() - start_time
    except requests.RequestException as e:
        raise Exception(f"Ошибка получения данных: {str(e)}")

def parse_sensor_data(raw_data):
    try:
        data = json.loads(raw_data)
        # Исправляем формат временной зоны
        timestamp = data['timestamp'].replace("+0300", "+03:00")
        dt = datetime.fromisoformat(timestamp)
        
        return {
            'temperature': data['temperature'],
            'date': dt.strftime("%Y-%m-%d"),
            'time': dt.strftime("%H:%M:%S"),
            'error': None
        }
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Ошибка формата данных: {str(e)}")

@app.after_request
def disable_caching(response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    sensor_data = {}
    load_time = 0
    
    try:
        # Для GET-запросов получаем данные
        if request.method == 'GET':
            raw_data, load_time = fetch_github_data()
            sensor_data = parse_sensor_data(raw_data)
            data_history.append(sensor_data)
            
    except Exception as e:
        sensor_data = {'error': str(e)}
    
    return render_template('index.html', 
                         data=sensor_data,
                         history=list(data_history),
                         load_time=load_time)

@app.route('/update', methods=['POST'])
def update_file():
    try:
        new_data = request.form['data']
        
        # Проверяем существование локального репозитория
        if not os.path.exists(REPO_PATH):
            raise Exception("Локальный репозиторий не найден")
            
        repo = git.Repo(REPO_PATH)
        
        # Обновляем файл
        file_path = os.path.join(REPO_PATH, "data.txt")
        with open(file_path, "w") as f:
            f.write(new_data)
            
        # Git операции
        repo.git.add("--all")
        repo.git.commit("-m", "Обновление через Flask-приложение")
        origin = repo.remote(name="origin")
        origin.push()
        
        return "Файл успешно обновлен и отправлен на GitHub!"
        
    except Exception as e:
        return f"Ошибка: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)
