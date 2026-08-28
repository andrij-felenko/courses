# topology.py — ЄДИНЕ джерело правди про фінальну топологію DH.
# З нього живуть і сторож (валить збірку), і картинка (з тих самих даних).
# style: "sync" (запит-відповідь) | "async" (подія/повідомлення)
# place: "client" | "door" | "cloud" | "edge" | "external";  db = база, якою розгортання ВОЛОДІЄ

DEPLOYMENTS = {                                                   # ЩО котиться в прод самостійно
    "app":       {"place": "client",   "db": None, "owns": []},
    "dashboard": {"place": "client",   "db": None, "owns": []},
    "gateway":   {"place": "door",     "db": None, "owns": []},           # TLS, токен, ліміт, маршрут
    "core":      {"place": "cloud",    "db": "core_db",                   # ← ТРИ хмарні розгортання
                  "owns": ["control","twin","automations","notifications","billing","identity"]},
    "telemetry": {"place": "cloud",    "db": "telemetry_db", "owns": ["telemetry"]},
    "video":     {"place": "cloud",    "db": "video_db",     "owns": ["video"]},
    "hub":       {"place": "edge",     "db": None, "owns": ["hub"]},      # на полиці у власника
    "payments":  {"place": "external", "db": None, "owns": []},           # чужий, за ACL
    "push":      {"place": "external", "db": None, "owns": []},
}

SEAMS = [                        # КОЖЕН дозволений шов і його СТИЛЬ — те, чого мапа моноліта не знала
    {"from":"app",       "to":"gateway",   "style":"sync",  "why":"людина дивиться на екран"},
    {"from":"dashboard", "to":"gateway",   "style":"sync",  "why":"людина чекає відповіді"},
    {"from":"gateway",   "to":"core",      "style":"sync",  "why":"BFF складає екран із ядра"},
    {"from":"gateway",   "to":"telemetry", "style":"sync",  "why":"BFF читає вимір — терпить таймаут"},
    {"from":"gateway",   "to":"video",     "style":"sync",  "why":"клієнт відкриває потік камери"},
    {"from":"core", "to":"telemetry", "style":"async", "topic":"DeviceEvent", "why":"ядро публікує факт і йде"},
    {"from":"core", "to":"video",     "style":"async", "topic":"DeviceEvent", "why":"відео чує про камери з того ж потоку"},
    {"from":"core", "to":"hub",       "style":"async", "topic":"HubCommand",  "why":"команда вниз; поганий Wi-Fi"},
    {"from":"hub",  "to":"core",      "style":"async", "topic":"HubEvent",    "why":"стан вгору, ретрай + ідемпотентність"},
    {"from":"core", "to":"payments",  "style":"sync",  "why":"тверде «так/ні» від чужого, за ACL"},
    {"from":"core", "to":"push",      "style":"async", "topic":"Notify",      "why":"вистрелив-забув"},
]
