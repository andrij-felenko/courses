# hub.py — підрослий хаб Digital Homes (фрагмент): пристрої, розклад, БД, кеш
import json, sqlite3
from time import time as now

TIMEOUT_S = 90                          # мовчить довше — вважаємо офлайн
db = sqlite3.connect("hub.db")          # ← джерело правди про пристрої: на диску

class Device:                           # сесія пристрою — живе в ПАМʼЯТІ процесу
    def __init__(self, id, name, relay):
        self.id, self.name, self.relay = id, name, relay
        self.last_seen = 0.0
        self.online = False             # ← похідне від last_seen, а ЗБЕРІГАЄМО окремо
        self.temp = None

devices = {}                            # ← список у памʼяті: ДУБЛЬ таблиці devices
status_cache = {}                       # ← кеш статусів для застосунку: похідне
schedule = json.load(open("schedule.json"))   # ← розклад гріння: з ФАЙЛУ
heated_since = None                     # ← лічильник «2 год поспіль»: ТІЛЬКИ в памʼяті

def reload_devices():                   # тягнемо список із БД у памʼятний кеш
    devices.clear()
    for id, name, relay in db.execute("SELECT id, name, relay FROM devices"):
        devices[id] = Device(id, name, relay)

def poll():                             # опитувач: раз на виток питає кожен пристрій
    for d in devices.values():
        t = ping(d)                     # локальна змінна — живе один виток
        if t is not None:
            d.temp, d.last_seen, d.online = t, now(), True     # писар online №1
        status_cache[d.id] = {"temp": d.temp, "online": d.online, "ts": now()}

def on_push(msg):                       # пристрій сам штовхнув пакет
    d = devices.get(msg["id"])
    if d:
        d.last_seen, d.online = now(), True                    # писар online №2
        status_cache[d.id]["temp"] = msg["temp"]               # писар у кеш повз опитувач

def api_status(device_id):              # застосунок питає статус — читає кеш
    return status_cache.get(device_id)
