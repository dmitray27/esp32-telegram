app = Flask(__name__)
GITHUB_URL = "https://raw.githubusercontent.com/dmitray27/esp32/main/tem.txt"

# Ограничим историю последними 10 записями
data_history = deque(maxlen=10)

def fetch_github_data():
    try:
        start_time = time.time()  # Засекаем время начала загрузки
        response = requests.get(
            GITHUB_URL,
            timeout=3,
            headers={'Cache-Control': 'no-cache'}
        )
        response.raise_for_status()
        load_time = time.time() - start_time  # Вычисляем время загрузки
        return response.text.strip(), load_time
    except requests.RequestException as e:
        raise Exception(f"Ошибка получения данных: {str(e)}")

def parse_sensor_data(raw_data):
    try:
        data = json.loads(raw_data)
        dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

        return {
            'temperature': data['temperature'],
            'date': dt.strftime("%Y-%m-%d"),
            'time': dt.strftime("%H:%M:%S"),
            'error': None
        }
    except (KeyError, json.JSONDecodeError) as e:
        raise ValueError("Некорректный формат данных")
    except ValueError as e:
        raise ValueError(f"Ошибка времени: {str(e)}")

@app.after_request
def disable_caching(response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response

# Путь к локальной копии репозитория
REPO_PATH = "."  # Замените на реальный путь
REPO_SSH_URL = "git@github.com:dmitray27/esp32-telegram.git"  # Замените на ваш SSH-URL

@app.route('/')
def index():
    return
    <h1>Обновление файла на GitHub через SSH</h1>
    <form method="POST" action="/update">
        <textarea name="data" rows="10" cols="30"></textarea><br>
        <input type="submit" value="Отправить">
    </form>


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


@app.route('/')
def index():
    try:
        raw_data, load_time = fetch_github_data()  # Получаем данные и время загрузки
        sensor_data = parse_sensor_data(raw_data)
        data_history.append(sensor_data)  # Добавляем данные в историю
    except Exception as e:
        sensor_data = {'error': str(e)}
        load_time = 0  # В случае ошибки время загрузки = 0

    return render_template('index.html', data=sensor_data, history=list(data_history), load_time=load_time)


if __name__ == '__main__':
    app.run(debug=False)
