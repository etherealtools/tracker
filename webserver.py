from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Discord Tracker ok!"

def ru():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=ru)  # Corrected function call
    t.start()
