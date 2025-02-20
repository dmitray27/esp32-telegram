from flask import Flask, request
import git
import os

app = Flask(__name__)

# Путь к локальной копии репозитория
REPO_PATH = "."  # Замените на реальный путь
REPO_SSH_URL = "git@github.com:dmitray27/esp32-telegram.git"  # Замените на ваш SSH-URL

@app.route('/')
def index():
    return '''
    <h1>Обновление файла на GitHub через SSH</h1>
    <form method="POST" action="/update">
        <textarea name="data" rows="10" cols="30"></textarea><br>
        <input type="submit" value="Отправить">
    </form>
    '''


@app.route('/update', methods=['POST'])
def update_file():
    # Получаем данные из формы
    new_data = request.form['data']

    # Открываем репозиторий
    repo = git.Repo(REPO_PATH)

    # Обновляем файл data.txt
    file_path = os.path.join(REPO_PATH, "data.txt")
    with open(file_path, "w") as file:
        file.write(new_data)

    # Добавляем все изменения в Git
    repo.git.add("--all")

    # Коммитим изменения
    repo.git.commit("-m", "Обновление файла data.txt через Flask")

    # Пушим изменения на GitHub
    origin = repo.remote(name="origin")
    origin.push()

    return "Файл успешно обновлен и отправлен на GitHub!"


if __name__ == '__main__':
    app.run(debug=True)
