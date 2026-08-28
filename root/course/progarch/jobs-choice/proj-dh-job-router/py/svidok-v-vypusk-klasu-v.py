sys = make_system()
count = lambda t: len(sys.db.table(t))

# notify ще в базі-дефолті — сповіщення осідає в таблиці jobs:
sys.enqueue(Job("notify", {"kind": "smoke"}, "notify:smoke-1"))
print("notify ДО випуску   → jobs у базі:", count("jobs"),
      " брокер notify:", sys.broker.depth("notify"))

sys.route["notify"] = sys.broker   # ← ЄДИНА правка; жоден виклик enqueue не чіпаємо

# той САМИЙ виклик — тепер їде брокером:
sys.enqueue(Job("notify", {"kind": "smoke"}, "notify:smoke-2"))
print("notify ПІСЛЯ випуску → jobs у базі:", count("jobs"),
      " брокер notify:", sys.broker.depth("notify"))
