from flask import Flask, jsonify, render_template
import json

app = Flask(__name__)

# Путь к файлу с данными
DATA_FILE = "tem.txt"

def read_data():
    """Чтение данных из файла."""
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)  # Парсим JSON
        return data
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def home():
    """Главная страница с отображением данных."""
    data = read_data()
    return render_template("index.html", data=data)

@app.route("/api/data")
def api_data():
    """API для получения данных в формате JSON."""
    data = read_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)