from flask import Flask, render_template, request
import subprocess
import os
import tempfile
from datetime import datetime

app = Flask(__name__)

# Настройки GitHub
GITHUB_REPO_SSH = "git@github.com:dmitray27/esp32-telegram.git"  # SSH-URL вашего репозитория
BRANCH = "main"  # Ветка, в которую отправляем данные

def push_to_github(data):
    """Отправляет данные в GitHub через временный репозиторий."""
    try:
        # Создаем временную папку
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Клонируем репозиторий через SSH
            subprocess.run(
                ["git", "clone", "--depth", "1", GITHUB_REPO_SSH, tmp_dir],
                check=True,
                capture_output=True,
                text=True,
            )

            # Записываем данные в файл
            data_file = os.path.join(tmp_dir, "data.txt")
            with open(data_file, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n[{timestamp}]\n{data}\n")

            # Git-команды
            subprocess.run(["git", "add", "data.txt"], cwd=tmp_dir, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Update data.txt: {timestamp}"],
                cwd=tmp_dir,
                check=True,
            )
            subprocess.run(["git", "push", "origin", BRANCH], cwd=tmp_dir, check=True)

            return True, "Данные отправлены в GitHub!"
    except subprocess.CalledProcessError as e:
        return False, f"Git ошибка: {e.stderr}"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    if request.method == "POST":
        user_data = request.form.get("data", "").strip()
        if user_data:
            success, msg = push_to_github(user_data)
            message = msg if success else f"Ошибка: {msg}"
        else:
            message = "Ошибка: данные не введены."

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)