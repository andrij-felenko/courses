import os
import sys

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

img_dir = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(img_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# Figure 1: Dual-write Failure Modes (Crash Window & Out-of-Order Race)
# -----------------------------------------------------------------------------
def gen_fig1():
    w, h = 820, 360
    frags = []

    # Title card / Context
    frags.append(rect(20, 15, 780, 45, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(410, 42, "Аномалії підходу «Подвійний запис» (Dual-Write Anti-Pattern)", size=15, bold=True, color="#0f172a"))

    # Left Column: Crash Window (Inconsistency)
    frags.append(rect(30, 75, 365, 265, fill="#ffffff", stroke="#ef4444", sw=1.8, rx=8))
    frags.append(rect(30, 75, 365, 34, fill="#fee2e2", stroke="#ef4444", sw=1.8, rx=8))
    frags.append(text(212, 98, "1. Аварійне вікно (Втрата події)", size=13, bold=True, color="#991b1b"))

    frags.append(fitbox(45, 120, 335, 42, "Застосунок: виконує COMMIT у БД\n(Замовлення #101 збережено у PostgreSQL)", size=11, fill="#f1f5f9", stroke="#94a3b8"))
    frags.append(arrow(212, 163, 212, 182, color="#ef4444", sw=2))
    
    # Crash marker
    frags.append(rect(45, 183, 335, 45, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(212, 202, "⚡ КРАХ СЕРВЕРА АБО МЕРЕЖІ", size=12, bold=True, color="#b91c1c"))
    frags.append(text(212, 218, "(виклик kafka.send() не відбувся)", size=11, color="#7f1d1d"))

    frags.append(arrow(212, 229, 212, 248, color="#94a3b8", sw=1.5))
    frags.append(fitbox(45, 249, 335, 75, "Наслідок: База даних має запис,\nале Kafka, Redis та Elasticsearch\nніколи не отримають подію.\nДані безповоротно розійшлися.", size=11, fill="#fff1f2", stroke="#f43f5e", bold=True, color="#881337"))

    # Right Column: Out-of-Order Race (Concurrency)
    frags.append(rect(425, 75, 365, 265, fill="#ffffff", stroke="#f59e0b", sw=1.8, rx=8))
    frags.append(rect(425, 75, 365, 34, fill="#fef3c7", stroke="#f59e0b", sw=1.8, rx=8))
    frags.append(text(607, 98, "2. Перегони паралельних оновлень", size=13, bold=True, color="#92400e"))

    frags.append(fitbox(440, 120, 335, 42, "Потік А: UPDATE status = 'PAID' (12:00:01)\nПотік Б: UPDATE status = 'CANCELLED' (12:00:02)", size=11, fill="#f1f5f9", stroke="#94a3b8"))
    frags.append(arrow(607, 163, 607, 182, color="#f59e0b", sw=2))

    frags.append(rect(440, 183, 335, 45, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=6))
    frags.append(text(607, 202, "Мережева затримка: Подія Б випередила А", size=11, bold=True, color="#b45309"))
    frags.append(text(607, 218, "(У Kafka: спершу CANCELLED, потім PAID)", size=10, color="#92400e"))

    frags.append(arrow(607, 229, 607, 248, color="#94a3b8", sw=1.5))
    frags.append(fitbox(440, 249, 335, 75, "Наслідок у споживача:\nБД має фінальний стан CANCELLED,\nале кеш/пошук отримав останнім PAID.\nПовна втрата консистентності!", size=11, fill="#fffbeb", stroke="#d97706", bold=True, color="#78350f"))

    out_path = os.path.join(img_dir, "cdc-dual-write-race.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

# -----------------------------------------------------------------------------
# Figure 2: CDC Approaches Comparison (Polling vs Triggers vs Log Tailing)
# -----------------------------------------------------------------------------
def gen_fig2():
    w, h = 820, 340
    frags = []

    frags.append(rect(20, 15, 780, 42, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(410, 40, "Порівняння архітектур захоплення змін (CDC Approaches)", size=15, bold=True, color="#0f172a"))

    col_w = 245
    # Approach 1: Polling
    x1 = 30
    frags.append(rect(x1, 70, col_w, 250, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(rect(x1, 70, col_w, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, 91, "1. Опитування (Polling)", size=12, bold=True, color="#334155"))
    p1_text = "Механізм:\nSELECT WHERE updated_at > :ts\n\nНедоліки:\n• Пропуск проміжних станів\n• Не бачить Hard DELETE\n• Навантаження на CPU/диск\n• Аномалії довгих транзакцій\n\nЗатримка: висока (секунди/хв)"
    frags.append(fitbox(x1 + 10, 110, col_w - 20, 195, p1_text, size=11, fill="#fafafa", stroke="#e2e8f0"))

    # Approach 2: Triggers
    x2 = 288
    frags.append(rect(x2, 70, col_w, 250, fill="#ffffff", stroke="#f59e0b", sw=1.5, rx=8))
    frags.append(rect(x2, 70, col_w, 32, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, 91, "2. Тригери (DB Triggers)", size=12, bold=True, color="#92400e"))
    p2_text = "Механізм:\nAFTER INSERT/UPDATE/DELETE\nзапис у тіньову таблицю аудиту\n\nНедоліки:\n• Подвоєння записів (2x IOPS)\n• Зростання латентності транзакцій\n• Блокування рядків у таблиці\n• Крихкість при міграціях DDL\n\nЗатримка: середня"
    frags.append(fitbox(x2 + 10, 110, col_w - 20, 195, p2_text, size=11, fill="#fafafa", stroke="#e2e8f0"))

    # Approach 3: Log Tailing
    x3 = 545
    frags.append(rect(x3, 70, col_w, 250, fill="#ffffff", stroke="#10b981", sw=2, rx=8))
    frags.append(rect(x3, 70, col_w, 32, fill="#d1fae5", stroke="#10b981", sw=2, rx=8))
    frags.append(text(x3 + col_w/2, 91, "3. Вичитування WAL / Binlog", size=12, bold=True, color="#065f46"))
    p3_text = "Механізм:\nАсинхронне вичитування журналу\n(PostgreSQL WAL / MySQL Binlog)\n\nПереваги:\n• 0% впливу на час COMMIT\n• 100% захоплення (DELETE, DDL)\n• Суворий порядок за LSN/GTID\n• Доступні всі проміжні стани\n\nЗатримка: мінімальна (<50 мс)"
    frags.append(fitbox(x3 + 10, 110, col_w - 20, 195, p3_text, size=11, fill="#f0fdf4", stroke="#86efac", bold=False, color="#064e3b"))

    out_path = os.path.join(img_dir, "cdc-approaches-comparison.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

# -----------------------------------------------------------------------------
# Figure 3: Deep Log-based CDC Architecture (Logical Decoding Pipeline)
# -----------------------------------------------------------------------------
def gen_fig3():
    w, h = 820, 370
    frags = []

    frags.append(rect(20, 15, 780, 42, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(410, 40, "Конвеєр логічного декодування транзакційного журналу (WAL CDC)", size=15, bold=True, color="#0f172a"))

    # Block 1: Source Database
    frags.append(rect(30, 75, 210, 265, fill="#ffffff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(rect(30, 75, 210, 30, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(text(135, 95, "OLTP База даних (PostgreSQL)", size=11, bold=True, color="#1e40af"))

    frags.append(fitbox(42, 115, 186, 45, "Клієнтські транзакції:\nINSERT, UPDATE, DELETE", size=10, fill="#f8fafc", stroke="#cbd5e1"))
    frags.append(arrow(135, 161, 135, 178, color="#3b82f6", sw=1.5))
    frags.append(fitbox(42, 179, 186, 50, "Фізичний журнал WAL:\nПослідовні бінарні записи LSN\n(wal_level = logical)", size=10, fill="#dbeafe", stroke="#93c5fd", bold=True, color="#1e3a8a"))
    frags.append(arrow(135, 230, 135, 247, color="#3b82f6", sw=1.5))
    frags.append(fitbox(42, 248, 186, 75, "Replication Slot & Plugin:\n• Каталог знімків (Catalog)\n• Декодер pgoutput / test_dec\n• Гарантія збереження WAL", size=10, fill="#f8fafc", stroke="#cbd5e1"))

    # Arrow from DB to CDC Engine
    frags.append(arrow(241, 285, 284, 285, color="#10b981", sw=2.5))
    frags.append(text(262, 275, "Streaming", size=9, bold=True, color="#059669"))

    # Block 2: CDC Engine
    frags.append(rect(285, 75, 240, 265, fill="#ffffff", stroke="#10b981", sw=2, rx=8))
    frags.append(rect(285, 75, 240, 30, fill="#ecfdf5", stroke="#10b981", sw=2, rx=8))
    frags.append(text(405, 95, "Рушій CDC (Debezium / Custom)", size=11, bold=True, color="#065f46"))

    frags.append(fitbox(298, 115, 214, 55, "Парсинг логічного протоколу:\nВідтворення меж транзакцій\n(BEGIN → Кортежі → COMMIT)", size=10, fill="#f0fdf4", stroke="#a7f3d0"))
    frags.append(arrow(405, 171, 405, 188, color="#10b981", sw=1.5))
    frags.append(fitbox(298, 189, 214, 60, "Конвертація схеми та подій:\nФормування Before/After образу,\nметаданих LSN, ts_ms, source", size=10, fill="#f0fdf4", stroke="#a7f3d0"))
    frags.append(arrow(405, 250, 405, 267, color="#10b981", sw=1.5))
    frags.append(fitbox(298, 268, 214, 58, "Підтвердження позиції:\nОновлення confirmed_flush_lsn\n(Звільнення відпрацьованого WAL)", size=10, fill="#d1fae5", stroke="#6ee7b7", bold=True, color="#064e3b"))

    # Arrow from CDC Engine to Consumers
    frags.append(arrow(526, 219, 569, 219, color="#6366f1", sw=2.5))
    frags.append(text(548, 209, "Events", size=9, bold=True, color="#4f46e5"))

    # Block 3: Consumers / Sinks
    frags.append(rect(570, 75, 220, 265, fill="#ffffff", stroke="#6366f1", sw=1.5, rx=8))
    frags.append(rect(570, 75, 220, 30, fill="#eef2ff", stroke="#6366f1", sw=1.5, rx=8))
    frags.append(text(680, 95, "Цільові системи (Sinks)", size=11, bold=True, color="#3730a3"))

    frags.append(fitbox(582, 115, 196, 45, "Брокер подій (Apache Kafka):\nПартиціонування за Primary Key", size=10, fill="#f8fafc", stroke="#cbd5e1"))
    frags.append(fitbox(582, 170, 196, 45, "Пошуковий рушій (Elasticsearch):\nМиттєве оновлення пошукового індексу", size=10, fill="#f8fafc", stroke="#cbd5e1"))
    frags.append(fitbox(582, 225, 196, 45, "Розподілений кеш (Redis):\nІнвалідація або write-through кеш", size=10, fill="#f8fafc", stroke="#cbd5e1"))
    frags.append(fitbox(582, 280, 196, 48, "Аналітичне сховище (ClickHouse):\nСтрімінг сирих подій для OLAP", size=10, fill="#f8fafc", stroke="#cbd5e1"))

    out_path = os.path.join(img_dir, "cdc-log-decoding-pipeline.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

# -----------------------------------------------------------------------------
# Figure 4: Transactional Outbox + Watermark Snapshotting
# -----------------------------------------------------------------------------
def gen_fig4():
    w, h = 820, 350
    frags = []

    frags.append(rect(20, 15, 780, 42, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(410, 40, "Патерн Transactional Outbox та інкрементні знімки (Watermarking)", size=15, bold=True, color="#0f172a"))

    # Left: Transactional Outbox
    frags.append(rect(30, 75, 365, 255, fill="#ffffff", stroke="#8b5cf6", sw=1.8, rx=8))
    frags.append(rect(30, 75, 365, 32, fill="#f5f3ff", stroke="#8b5cf6", sw=1.8, rx=8))
    frags.append(text(212, 96, "А. Патерн Transactional Outbox", size=12, bold=True, color="#5b21b6"))

    ob_txt = "Єдина локальна ACID транзакція:\n1. INSERT INTO orders (id, customer, total)\n2. INSERT INTO outbox (aggregate_id, event_payload)\n\nCOMMIT відбувається атомарно."
    frags.append(fitbox(45, 118, 335, 75, ob_txt, size=11, fill="#faf5ff", stroke="#ddd6fe"))
    frags.append(arrow(212, 194, 212, 215, color="#8b5cf6", sw=2))
    
    ob_res = "CDC вичитує лише таблицю outbox з WAL,\nвидобуває доменну подію (Domain Event)\nі спрямовує в Kafka з ключем aggregate_id.\nЖодного подвійного запису в коді!"
    frags.append(fitbox(45, 216, 335, 95, ob_res, size=11, fill="#ede9fe", stroke="#c4b5fd", bold=True, color="#4c1d95"))

    # Right: Incremental Watermark Snapshotting
    frags.append(rect(425, 75, 365, 255, fill="#ffffff", stroke="#0284c7", sw=1.8, rx=8))
    frags.append(rect(425, 75, 365, 32, fill="#e0f2fe", stroke="#0284c7", sw=1.8, rx=8))
    frags.append(text(607, 96, "Б. Інкрементний знімок без блокувань (DBLog)", size=12, bold=True, color="#0369a1"))

    wm_txt = "1. Сигнал Low Watermark у таблицю сигналів\n2. SELECT * FROM table WHERE id BETWEEN p0 AND p1\n3. Сигнал High Watermark у таблицю сигналів\n(Ніяких LOCK TABLE! Застосунок вільно пише)"
    frags.append(fitbox(440, 118, 335, 80, wm_txt, size=10.5, fill="#f0f9ff", stroke="#bae6fd"))
    frags.append(arrow(607, 199, 607, 220, color="#0284c7", sw=2))

    wm_res = "Узгодження в потоці CDC:\nПодії WAL між Low та High водяними знаками\nмають пріоритет над даними з SELECT.\nЗнімок мільйонів рядків створюється без простою!"
    frags.append(fitbox(440, 221, 335, 90, wm_res, size=11, fill="#e0f2fe", stroke="#7dd3fc", bold=True, color="#0c4a6e"))

    out_path = os.path.join(img_dir, "cdc-outbox-watermark-snapshot.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

if __name__ == "__main__":
    gen_fig1()
    gen_fig2()
    gen_fig3()
    gen_fig4()
    print("All CDC SVGs successfully generated.")
