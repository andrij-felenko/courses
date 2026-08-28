# e2e_smoke.py — жене справжнє значення від HTTP-краю крізь усі вузли й СТВЕРДЖУЄ вихід.
# Запуск ПРОТИ вже розгорнутої нитки (SMOKE_URL); торкаємось лише двох країв.
import os, random, sys, time, urllib.request

BASE = os.environ.get("SMOKE_URL", "http://localhost:8080")

# (1) Унікальне значення на прогін: читаємо СВІЙ запис, а не леглий з минулого разу.
sent = str(1000 + random.randrange(9000))

def post(v: str) -> int:
    req = urllib.request.Request(f"{BASE}/temp", data=v.encode(), method="POST")
    return urllib.request.urlopen(req, timeout=5).status

def get() -> str:
    with urllib.request.urlopen(f"{BASE}/temp", timeout=5) as r:
        return r.read().decode().strip()

# (2) справжній вхід у перший вузол — HTTP-край
if post(sent) != 200:
    sys.exit("ДИМОВИЙ ТЕСТ ЧЕРВОНИЙ: POST не пройшов")

# (3) опитуємо останній край з дедлайном на МОНОТОННОМУ годиннику (не сон, не
# настінний час), поки значення пройде API → брокер → воркер → сховище.
deadline = time.monotonic() + 10
while time.monotonic() < deadline:
    try:
        if get() == sent:                 # СТВЕРДЖЕННЯ: повернулось саме наше значення
            print(f"нитка пройшла наскрізь: {sent}")
            sys.exit(0)                   # зелено
    except OSError:
        pass                              # система ще підводиться — пробуємо далі
    time.sleep(0.2)

sys.exit(f"ДИМОВИЙ ТЕСТ ЧЕРВОНИЙ: нитка не пройшла, {sent} не з'явилось")
