# -*- coding: utf-8 -*-
"""Фігури до теми «Чи потрібні IoT мікросервіси».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

# Палітра для архітектури IoT бекенду
COL_INBOUND  = "#2563eb"  # вхідний телеметричний потік — синій
COL_OUTBOUND = "#d97706"  # вихідні команди керування — бурштиновий
COL_FAIL     = "#dc2626"  # накладні витрати / помилки / затримки — червоний
COL_OK       = "#059669"  # нульовий наклад / оптимізований моноліт — зелений
COL_STORAGE  = "#7c3aed"  # база даних / сховище стану — фіолетовий
COL_BOX_BG   = "#f8fafc"  # нейтральний фон блоків


# ── 1. Профіль навантаження: Web CRUD проти IoT Ingestion ──────────────────────
def fig_iot_workload_profile():
    W, H = 840, 480
    f = [text(W / 2, 28, "Порівняння профілів навантаження: Web CRUD проти IoT Ingestion", 15, INK, "middle", bold=True)]

    # Ліва колонка: Класичний Web CRUD
    f.append(rect(24, 55, 380, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(214, 82, "КЛАСИЧНИЙ WEB CRUD / Е-КОМЕРЦІЯ", 12, INK, "middle", bold=True))
    f.append(text(214, 100, "Людино-орієнтоване, симетричне навантаження", 9.8, MUTED, "middle"))

    web_cards = [
        ("Співвідношення трафіку", "Симетричне: читання (60-80%) та запис (20-40%)", 120),
        ("Характер з'єднань", "Короткоживучі HTTP/1.1-2 запити без утримання стану", 182),
        ("Модель стану (State)", "Безстанкові (Stateless) сервери + токени JWT / Сесії", 244),
        ("Поведінка при збоях", "Поодинокі користувачі оновлюють сторінку вручну", 306),
        ("Оптимальна архітектура", "Мікросервіси за бізнес-доменами (Orders, Auth, Catalog)", 368),
    ]
    for title, desc, y_pos in web_cards:
        f.append(rect(36, y_pos, 356, 52, fill="#ffffff", stroke="#cbd5e1", sw=1.1, rx=4))
        f.append(text(48, y_pos + 20, title, 10, INK, "start", bold=True))
        f.append(text(48, y_pos + 38, desc, 9.2, MUTED, "start"))

    # Права колонка: IoT Ingestion
    f.append(rect(436, 55, 380, 380, fill="#eff6ff", stroke=COL_INBOUND, sw=1.8, rx=6))
    f.append(text(626, 82, "ІНЖЕНЕРНИЙ IOT INGESTION БЕКЕНД", 12, COL_INBOUND, "middle", bold=True))
    f.append(text(626, 100, "Машинний, різко асиметричний потік телеметрії", 9.8, MUTED, "middle"))

    iot_cards = [
        ("Співвідношення трафіку", "Асиметричне: 98% телеметрія вгору, 2% команди вниз", 120, COL_INBOUND),
        ("Характер з'єднань", "Мільйони постійних TCP/TLS, MQTT, CoAP сесій (C100k+)", 182, COL_INBOUND),
        ("Модель стану (State)", "Постійний Device Twin у RAM: онлайн, телеметрія, уставки", 244, COL_STORAGE),
        ("Поведінка при збоях", "Шторм перепідключень (Reconnect Storm / Thundering Herd)", 306, COL_FAIL),
        ("Оптимальна архітектура", "Модульний моноліт з In-Memory шиною та пакетним I/O", 368, COL_OK),
    ]
    for title, desc, y_pos, stroke_c in iot_cards:
        f.append(rect(448, y_pos, 356, 52, fill="#ffffff", stroke=stroke_c, sw=1.3, rx=4))
        f.append(text(460, y_pos + 20, title, 10, stroke_c, "start", bold=True))
        f.append(text(460, y_pos + 38, desc, 9.2, INK, "start"))

    # Підпис
    f.append(text(W / 2, 455, "IoT вимагає оптимізації під тримання мільйонів відкритих сокетів та пакетний запис у часові ряди", 10.2, INK, "middle", italic=True))

    render(os.path.join(IMG, "iot-workload-profile-vs-web-crud.svg"), W, H, *f)


# ── 2. Податок мікросервісів: ланцюжок накладних витрат ────────────────────────
def fig_microservices_tax():
    W, H = 840, 500
    f = [text(W / 2, 28, "Податок мікросервісів у потоці IoT телеметрії (The Microservices Tax)", 15, INK, "middle", bold=True)]

    # Ланцюжок мікросервісів
    services = [
        ("Ingest Gateway", "TCP/TLS термінація", 36),
        ("Auth Service", "Перевірка токена", 198),
        ("Device Registry", "Пошук Device Twin", 360),
        ("Rules Engine", "Перевірка тригерів", 522),
        ("TSDB Ingest", "Запис часових рядів", 684),
    ]

    for title, sub, x_pos in services:
        f.append(rect(x_pos, 65, 120, 72, fill="#fef2f2", stroke=COL_FAIL, sw=1.4, rx=5))
        f.append(text(x_pos + 60, 90, title, 9.8, INK, "middle", bold=True))
        f.append(text(x_pos + 60, 115, sub, 9.0, MUTED, "middle"))

    # Стрілки між сервісами з підписами накладних витрат
    for i in range(4):
        x1 = 156 + i * 162
        x2 = 198 + i * 162
        f.append(line(x1, 101, x2, 101, color=COL_FAIL, sw=1.8))
        f.append(arrow(x2 - 8, 101, x2, 101, color=COL_FAIL, sw=1.8))
        f.append(text((x1 + x2) / 2, 88, "gRPC", 9.2, COL_FAIL, "middle", bold=True))
        f.append(text((x1 + x2) / 2, 118, "+1.5ms", 9.0, COL_FAIL, "middle"))

    # Розбір накладних витрат одного стрибка (Hop breakdown)
    f.append(rect(36, 165, 768, 175, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=6))
    f.append(text(420, 190, "АНАТОМІЯ НАКЛАДНИХ ВИТРАТ НА ОДНОМУ МІЖСЕРВІСНОМУ СТРИБКУ (HOP)", 11.5, "#b45309", "middle", bold=True))

    tax_stages = [
        ("Маршалінг Proto/JSON", "Серіалізація структури C++/Go в байти. Виділення пам'яті в купі (heap).", 56, 212, 168),
        ("Ядро ОС та сокети", "Копіювання буфера у ядро, стек TCP/IP, перемикання контексту процесів.", 244, 212, 168),
        ("Мережевий RTT", "Фізична затримка передачі через віртуальний міст Kubernetes Overlay.", 432, 212, 168),
        ("Демаршалінг сервісу", "Парсинг байтів у нові об'єкти мови. Навантаження на Garbage Collector.", 620, 212, 168),
    ]

    for title, desc, x_pos, y_pos, width in tax_stages:
        f.append(rect(x_pos, y_pos, width, 105, fill="#ffffff", stroke="#fcd34d", sw=1.1, rx=4))
        f.append(text(x_pos + width / 2, y_pos + 22, title, 9.8, INK, "middle", bold=True))
        words = desc.split()
        line1 = " ".join(words[:3])
        line2 = " ".join(words[3:7])
        line3 = " ".join(words[7:])
        f.append(text(x_pos + width / 2, y_pos + 46, line1, 9.0, MUTED, "middle"))
        f.append(text(x_pos + width / 2, y_pos + 64, line2, 9.0, MUTED, "middle"))
        if line3:
            f.append(text(x_pos + width / 2, y_pos + 82, line3, 9.0, MUTED, "middle"))

    # Порівняльний підсумок знизу
    f.append(rect(36, 360, 370, 90, fill="#fef2f2", stroke=COL_FAIL, sw=1.4, rx=5))
    f.append(text(221, 385, "ЛАНЦЮЖОК ІЗ 5 МІКРОСЕРВІСІВ", 10.5, COL_FAIL, "middle", bold=True))
    f.append(text(221, 408, "• Загальна затримка: 6.0 – 12.0 мс на пакет", 9.4, INK, "middle"))
    f.append(text(221, 428, "• 80% CPU витрачається на сокети і серіалізацію", 9.4, COL_FAIL, "middle", bold=True))

    f.append(rect(434, 360, 370, 90, fill="#ecfdf5", stroke=COL_OK, sw=1.4, rx=5))
    f.append(text(619, 385, "МОДУЛЬНИЙ МОНОЛІТ (IN-MEMORY)", 10.5, COL_OK, "middle", bold=True))
    f.append(text(619, 408, "• Загальна затримка: 50 – 150 наносекунд на подію", 9.4, INK, "middle"))
    f.append(text(619, 428, "• 95% CPU витрачається на корисну бізнес-логіку", 9.4, COL_OK, "middle", bold=True))

    # Загальний підпис
    f.append(text(W / 2, 478, "Заміна внутрішньопроцесної передачі покажчиків на мережевий RPC призводить до падіння продуктивності в 10-50 разів", 10, INK, "middle", italic=True))

    render(os.path.join(IMG, "microservices-tax-in-iot-pipeline.svg"), W, H, *f)


# ── 3. Архітектура модульного моноліту ─────────────────────────────────────────
def fig_modular_monolith_architecture():
    W, H = 840, 500
    f = [text(W / 2, 28, "Архітектура модульного IoT-моноліту: нульовий наклад і строгі межі", 15, INK, "middle", bold=True)]

    # Зовнішнє поле: Єдиний процес OS (Single Process Boundary)
    f.append(rect(24, 55, 792, 395, fill="#f8fafc", stroke="#3b82f6", sw=2.2, rx=8))
    f.append(text(420, 80, "ЄДИНИЙ СИСТЕМНИЙ ПРОЦЕС (MODULAR MONOLITH RUNTIME / OS PROCESS)", 12, "#1d4ed8", "middle", bold=True))
    f.append(text(420, 100, "Спільний адресний простір, нульове копіювання, міжпотоковий Lock-free Ring Buffer", 9.8, MUTED, "middle"))

    # Внутрішні модулі
    modules = [
        ("Мережевий шлюз", "(Ingestion Core)", "epoll / io_uring / TLS\n100k+ відкритих з'єднань\nПарсинг бінарного кадру", 40, COL_INBOUND),
        ("Стан пристроїв", "(Device Twin)", "Concurrent Hash Map\nАтомарне оновлення метрик\nІнваріанти режимів роботи", 235, COL_STORAGE),
        ("Рушій правил", "(Rules Engine)", "Порогові тригери й алерти\nЛокальна фільтрація подій\nГенерація зворотних дій", 430, "#d97706"),
        ("Пакетний запис", "(TSDB Batcher)", "Акумуляція мікробатчів\nБуфер запису по 1000 точок\nСкидання на NVMe / SSD", 625, COL_OK),
    ]

    for title_m, title_s, desc, x_pos, col in modules:
        f.append(rect(x_pos, 122, 175, 155, fill="#ffffff", stroke=col, sw=1.5, rx=5))
        f.append(text(x_pos + 87, 144, title_m, 10.2, col, "middle", bold=True))
        f.append(text(x_pos + 87, 162, title_s, 9.2, MUTED, "middle"))
        for line_idx, line_txt in enumerate(desc.split("\n")):
            f.append(text(x_pos + 87, 192 + line_idx * 20, line_txt, 9.0, INK, "middle"))

    # Центральна in-memory шина (Lock-Free Ring Buffer)
    f.append(rect(40, 298, 760, 52, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=6))
    f.append(text(420, 320, "ВНУТРІШНЯ БЕЗБЛОКУВАЛЬНА ШИНА ПОДІЙ (LOCK-FREE IN-MEMORY RING BUFFER / DISRUPTOR)", 10.5, "#1d4ed8", "middle", bold=True))
    f.append(text(420, 338, "Передача std::shared_ptr / Arc без копіювання даних (Zero-Copy Pointers) | Затримка < 100 ns", 9.4, MUTED, "middle"))

    # Стрілки між модулями і шиною
    f.append(line(127, 277, 127, 298, color=COL_INBOUND, sw=1.8))
    f.append(arrow(127, 285, 127, 298, color=COL_INBOUND, sw=1.8))

    f.append(line(322, 298, 322, 277, color=COL_STORAGE, sw=1.8))
    f.append(arrow(322, 290, 322, 277, color=COL_STORAGE, sw=1.8))

    f.append(line(517, 298, 517, 277, color="#d97706", sw=1.8))
    f.append(arrow(517, 290, 517, 277, color="#d97706", sw=1.8))

    f.append(line(712, 298, 712, 277, color=COL_OK, sw=1.8))
    f.append(arrow(712, 290, 712, 277, color=COL_OK, sw=1.8))

    # Нижня частина: База даних і транзакції
    f.append(rect(40, 368, 760, 65, fill="#ffffff", stroke=COL_STORAGE, sw=1.4, rx=5))
    f.append(text(420, 392, "ЄДИНА ТРАНЗАКЦІЙНА БАЗА ДАНИХ (PostgreSQL + TimescaleDB / ClickHouse)", 11, COL_STORAGE, "middle", bold=True))
    f.append(text(420, 414, "Атомарні ACID-транзакції: одночасне оновлення Device Shadow, запис аудиту та черга вихідних команд без розподілених саг", 9.2, INK, "middle"))

    # Підпис
    f.append(text(W / 2, 475, "Модульний моноліт поєднує строгість доменних інтерфейсів із максимальною швидкістю спільної пам'яті", 10, INK, "middle", italic=True))

    render(os.path.join(IMG, "modular-monolith-runtime-layers.svg"), W, H, *f)


# ── 4. Прагматична декомпозиція: коли виносити сервіси ─────────────────────────
def fig_pragmatic_decomposition():
    W, H = 840, 480
    f = [text(W / 2, 28, "Прагматична декомпозиція: точкове винесення важких та ризикованих компонентів", 15, INK, "middle", bold=True)]

    # Центральне надійне ядро (Core Monolith)
    f.append(rect(235, 65, 370, 350, fill="#eff6ff", stroke=COL_INBOUND, sw=2.2, rx=8))
    f.append(text(420, 92, "ОСНОВНИЙ МОНОЛІТ (CORE RUNTIME)", 12, COL_INBOUND, "middle", bold=True))
    f.append(text(420, 110, "Критичний шлях телеметрії (Hot Path)", 9.8, MUTED, "middle"))

    core_units = [
        ("Ingestion & Connection Pool", "Стійкий пул TCP/TLS сокетів"),
        ("Device State & Digital Twin", "Оперативний стан у RAM"),
        ("ACID Database & Batcher", "Пакетний запис у TimescaleDB"),
        ("Downlink Command Queue", "Контроль доставки та тайм-аути"),
    ]
    for i, (title, sub) in enumerate(core_units):
        y_pos = 135 + i * 65
        f.append(rect(250, y_pos, 340, 54, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=4))
        f.append(text(420, y_pos + 22, title, 10.2, INK, "middle", bold=True))
        f.append(text(420, y_pos + 42, sub, 9.2, MUTED, "middle"))

    # Лівий зовнішній блок: Небезпечні протокольні адаптери
    f.append(rect(24, 110, 180, 260, fill="#fef2f2", stroke=COL_FAIL, sw=1.6, rx=6))
    f.append(text(114, 136, "ІЗОЛЬОВАНІ АДАПТЕРИ", 10.5, COL_FAIL, "middle", bold=True))
    f.append(text(114, 154, "(Unsafe / Sandboxes)", 9.2, MUTED, "middle"))

    unsafe_items = [
        ("Legacy Modbus", "Нестабільні парсери"),
        ("Custom Decoders", "C-бібліотеки вендорів"),
        ("Raw UDP Telemetry", "Ризик Segfault / витоків"),
    ]
    for i, (name, desc) in enumerate(unsafe_items):
        y_pos = 175 + i * 58
        f.append(rect(34, y_pos, 160, 50, fill="#ffffff", stroke="#fca5a5", sw=1.1, rx=4))
        f.append(text(114, y_pos + 20, name, 9.6, INK, "middle", bold=True))
        f.append(text(114, y_pos + 38, desc, 9.0, MUTED, "middle"))

    # Правий зовнішній блок: Важкі фонові воркери (ML / Vision)
    f.append(rect(636, 110, 180, 260, fill="#faf5ff", stroke=COL_STORAGE, sw=1.6, rx=6))
    f.append(text(726, 136, "ВАЖКІ АНАЛІТИЧНІ ВОРКЕРИ", 10, COL_STORAGE, "middle", bold=True))
    f.append(text(726, 154, "(GPU / ML / Workers)", 9.2, MUTED, "middle"))

    heavy_items = [
        ("Computer Vision", "GPU-ноди розпізнавання"),
        ("ML Anomaly Detectors", "PyTorch / ONNX воркери"),
        ("PDF / CSV Reports", "Генерація важких звітів"),
    ]
    for i, (name, desc) in enumerate(heavy_items):
        y_pos = 175 + i * 58
        f.append(rect(646, y_pos, 160, 50, fill="#ffffff", stroke="#d8b4fe", sw=1.1, rx=4))
        f.append(text(726, y_pos + 20, name, 9.6, INK, "middle", bold=True))
        f.append(text(726, y_pos + 38, desc, 9.0, MUTED, "middle"))

    # Стрілки взаємодії
    # Ліворуч: Адаптери -> Моноліт (через NATS / IPC)
    f.append(line(204, 240, 235, 240, color=COL_FAIL, sw=2))
    f.append(arrow(227, 240, 235, 240, color=COL_FAIL, sw=2))
    f.append(text(219, 228, "IPC", 9.2, COL_FAIL, "middle", bold=True))

    # Праворуч: Моноліт -> Воркери (асинхронна черга)
    f.append(line(605, 240, 636, 240, color=COL_STORAGE, sw=2))
    f.append(arrow(628, 240, 636, 240, color=COL_STORAGE, sw=2))
    f.append(text(620, 228, "NATS", 9.2, COL_STORAGE, "middle", bold=True))

    # Загальний підпис
    f.append(text(W / 2, 448, "Винесенню підлягають лише компоненти з ризиком аварії або відмінним профілем споживання ресурсів (GPU/CPU)", 10, INK, "middle", italic=True))

    render(os.path.join(IMG, "pragmatic-decomposition-boundaries.svg"), W, H, *f)


if __name__ == "__main__":
    fig_iot_workload_profile()
    fig_microservices_tax()
    fig_modular_monolith_architecture()
    fig_pragmatic_decomposition()
    print("OK: all figures generated successfully.")
