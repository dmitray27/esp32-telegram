from flask import Flask
import requests
import base64

app = Flask(__name__)

# Укажите свои данные
GITHUB_TOKEN = ""  # Замените на ваш токен
REPO_OWNER = "dmitray27"  # Замените на ваш логин
REPO_NAME = "esp32-telegram"  # Замените на название репозитория
FILE_PATH = "data.txt"  # Путь к файлу в репозитории

def get_file_from_github():
    # Формируем URL для запроса к GitHub API
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    
    # Заголовки для аутентификации
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Делаем запрос к GitHub API
    response = requests.get(url, headers=headers)
    
    # Проверяем статус ответа
    if response.status_code == 200:
        # Получаем содержимое файла (в формате base64)
        content = response.json()["content"]
        # Декодируем из base64 в строку
        decoded_content = base64.b64decode(content).decode("utf-8")
        return decoded_content
    else:
        # Если произошла ошибка, возвращаем сообщение
        return f"Ошибка: {response.status_code} - {response.text}"

@app.route("/")
def show_data():
    # Получаем данные из файла
    data = get_file_from_github()
    # Выводим данные как текст
    return f"<pre>{data}</pre>"

if __name__ == "__main__":
     app.run(debug=True, host='0.0.0.0', port=5006)
