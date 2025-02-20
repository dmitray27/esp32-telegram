from flask import Flask

# Создаём экземпляр приложения Flask
app = Flask(__name__)

# Определяем маршрут для главной страницы
@app.route('/')
def hello_world():
    return 'Привет, мир от vin!'

# Запускаем приложение, если файл запущен напрямую
if __name__ == '__main__':
    app.run(debug=True)
