from flask import Flask, render_templa
te
from datetime import datetime
import requests

app = Flask(__name__)

def get_temp_data():
    url = "https://raw.githubusercontent.com/dmitray27/esp32-telegram/main/log_s/temp_log.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        last_line = lines[-1] if lines else None
        
        if last_line:
            parts = last_line.split(',')
            if len(parts) >= 3:
                return {
                    'temp': parts[0].split(':')[-1].strip(),
                    'date': parts[1].split(':')[-1].strip(),
                    'time': parts[2].split(':')[-1].strip()
                }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    temp_data = get_temp_data()
    return render_template('index.html', 
                         temperature=temp_data['temp'] if temp_data else 'N/A',
                         date=temp_data['date'] if temp_data else 'N/A',
                         time=temp_data['time'] if temp_data else 'N/A')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
