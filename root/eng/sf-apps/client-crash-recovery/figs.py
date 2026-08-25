# -*- coding: utf-8 -*-
"""Фігури до теми «Документ переживає крах: автозбереження і журнал» (client-architecture)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def panel(x, y, w, h, head):
    """Панель із заголовком угорі; повертає (svg, внутрішній верх)."""
    s = rect(x, y, w, h, fill="#ffffff", stroke="#b8c2cc", sw=1.6, rx=10)
    s += text(x + w / 2, y + 28, head, size=15, bold=True)
    return s, y + 44


# ── 1. Розірваний запис vs Атомарне перейменування ──────────────────────────
def fig_torn_write_vs_atomic_rename():
    W, H = 1080, 480
    P, PW, PH, PY = [30, 560], 490, 410, 40
    s = ""

    # Ліва панель: Прямий запис (Torn Write)
    px = P[0]
    p, top = panel(px, PY, PW, PH, "Прямий запис у файл (небезпечно)")
    s += p
    cx = px + PW / 2

    b1, _, _ = textbox(cx, top + 35, "Оригінальний файл: doc.dat (v1)", size=13, min_w=340, fill="#eef3f8")
    s += b1
    s += arrow(cx, top + 60, cx, top + 105, color=POS)
    s += text(cx + 10, top + 88, "open(..., 'w') + write()", size=12, color=POS, anchor="start")

    # Зіпсований блок
    b2, _, _ = textbox(cx, top + 135, "Записано 40% нових байтів...", size=13, min_w=340, fill="#fff2f0", stroke=POS)
    s += b2
    s += arrow(cx, top + 160, cx, top + 205, color=POS)
    s += text(cx + 10, top + 188, "⚡ КРАХ (SIGKILL / вимкнення живлення)", size=12, color=POS, bold=True, anchor="start")

    b3, _, _ = textbox(cx, top + 245, "Файл doc.dat пошкоджено!\nСтарі дані затерто, нові не до кінця.\nДокумент втрачено назавжди.", size=12, min_w=340, fill="#ffeef0", stroke=POS, bold=True, color=POS)
    s += b3

    s += mtext(cx, top + 325, [
        "Немає ані попередньої версії (v1),",
        "ані коректної нової (v2).",
        "Torn Write залишає битий хвіст на диску.",
    ], size=12, color=MUTED)

    # Права панель: 4 кроки атомарної заміни
    px = P[1]
    p, top = panel(px, PY, PW, PH, "Атомарна заміна (Atomic Rename)")
    s += p
    cx = px + PW / 2

    steps = [
        ("1. write(doc.tmp)", "Запис повної копії v2 у тимчасовий файл поруч", "#eef3f8", LINE),
        ("2. fsync(doc.tmp)", "Скидання буферів ОС на фізичний диск", "#e8f6ee", FIELD),
        ("3. rename(doc.tmp, doc.dat)", "Атомарна підміна inode в каталозі", "#e8f4fc", NEG),
        ("4. fsync(dir_fd)", "Фіксація метаданих каталогу на диску", "#e8f6ee", FIELD),
    ]

    for i, (st_head, st_desc, bg_col, br_col) in enumerate(steps):
        y_box = top + 30 + i * 66
        b, _, _ = textbox(cx, y_box, f"{st_head}\n{st_desc}", size=12, min_w=430, fill=bg_col, stroke=br_col)
        s += b
        if i < 3:
            s += arrow(cx, y_box + 24, cx, y_box + 42, color=LINE, sw=1.3)

    s += mtext(cx, top + 315, [
        "Крах на кроках 1-2: старий doc.dat лишається цілим.",
        "Крах на кроці 3: атомарно існує або стара, або нова версія.",
    ], size=12, color=MUTED)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" '
           'markerHeight="6" orient="auto-start-reverse">\n'
           '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n</marker></defs>\n'
           '<rect width="100%%" height="100%%" fill="%s"/>\n%s\n</svg>'
           % (W, H, W, H, LINE, BG, s))
    with open(os.path.join(OUT, "torn-write-vs-atomic-rename.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


# ── 2. Життєвий цикл WAL і Snapshot ─────────────────────────────────────────
def fig_wal_and_snapshot_lifecycle():
    W, H = 1080, 520
    s = ""

    # Заголовок зверху
    s += text(W / 2, 35, "Життєвий цикл: Базовий знімок (Snapshot) + Журнал операцій (WAL)", size=16, bold=True)

    # Верхній часовий графік (Нормальна робота)
    p1, top1 = panel(40, 60, 1000, 190, "Фаза 1: Накопичення операцій у Write-Ahead Log")
    s += p1

    # Чекпойнт 0
    bx0, _, _ = textbox(130, top1 + 60, "Знімок doc.snap\nСтан на час T₀", size=12, min_w=140, fill="#e8f6ee", stroke=FIELD)
    s += bx0

    # Записи WAL
    wal_entries = ["Op #1: Insert('A')", "Op #2: Style(Bold)", "Op #3: Delete(w1)", "Op #4: Move(p2)"]
    for i, op in enumerate(wal_entries):
        wx = 330 + i * 145
        wb, _, _ = textbox(wx, top1 + 60, f"WAL-запис #{i+1}\n{op}\n[CRC32: ok]", size=11, min_w=130, fill="#eef3f8", stroke=LINE)
        s += wb
        if i == 0:
            s += arrow(205, top1 + 60, 260, top1 + 60, color=LINE)
        else:
            s += arrow(wx - 75, top1 + 60, wx - 68, top1 + 60, color=LINE)

    s += arrow(885, top1 + 60, 940, top1 + 60, color=POS)
    s += text(950, top1 + 55, "⚡ КРАХ", size=13, color=POS, bold=True, anchor="start")
    s += text(950, top1 + 72, "(Op #5 обірвано)", size=11, color=POS, anchor="start")

    s += text(500, top1 + 130, "Дисковий запис: кожен крок дописується послідовно (append-only) і захищається CRC32", size=12, color=MUTED)

    # Нижня панель: Відновлення після краху
    p2, top2 = panel(40, 270, 1000, 210, "Фаза 2: Відновлення (Replay) при наступному запуску")
    s += p2

    # Крок відновлення 1: Читання знімка
    r1, _, _ = textbox(160, top2 + 55, "Крок 1: Завантаження\nБазовий стан doc.snap\n(документ на T₀)", size=12, min_w=190, fill="#e8f6ee", stroke=FIELD)
    s += r1

    s += arrow(260, top2 + 55, 315, top2 + 55, color=LINE)

    # Крок відновлення 2: Replay журналу
    r2, _, _ = textbox(470, top2 + 55, "Крок 2: Програвання (Replay) WAL\nЗастосування Op #1, #2, #3, #4 послідовно.\nОбрізаний Op #5 відкидається за CRC32.", size=12, min_w=280, fill="#e8f4fc", stroke=NEG)
    s += r2

    s += arrow(615, top2 + 55, 670, top2 + 55, color=LINE)

    # Крок відновлення 3: Новий чекпойнт
    r3, _, _ = textbox(820, top2 + 55, "Крок 3: Новий знімок\nАтомарний запис doc.snap\nОчищення (truncate) WAL", size=12, min_w=200, fill="#f9f0ff", stroke="#8e44ad")
    s += r3

    s += text(500, top2 + 135, "Результат: 100% відновлення даних без втрати жодної підтвердженої правки", size=13, bold=True, color=FIELD)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" '
           'markerHeight="6" orient="auto-start-reverse">\n'
           '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n</marker></defs>\n'
           '<rect width="100%%" height="100%%" fill="%s"/>\n%s\n</svg>'
           % (W, H, W, H, LINE, BG, s))
    with open(os.path.join(OUT, "wal-and-snapshot-lifecycle.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


# ── 3. Конкурентний доступ і блокування ────────────────────────────────────
def fig_multi_process_lock_conflict():
    W, H = 1080, 460
    s = ""

    P, PW, PH, PY = [40, 560], 480, 390, 40

    # Ліва панель: Конфлікт без блокування (Split-brain)
    px = P[0]
    p, top = panel(px, PY, PW, PH, "Без блокування: Split-Brain руйнація")
    s += p
    cx = px + PW / 2

    b_p1, _, _ = textbox(cx - 120, top + 40, "Процес A\n(Вкладка 1)", size=12, min_w=120, fill="#ffeef0", stroke=POS)
    b_p2, _, _ = textbox(cx + 120, top + 40, "Процес B\n(Вкладка 2)", size=12, min_w=120, fill="#ffeef0", stroke=POS)
    s += b_p1 + b_p2

    s += arrow(cx - 120, top + 75, cx - 40, top + 130, color=POS)
    s += arrow(cx + 120, top + 75, cx + 40, top + 130, color=POS)
    s += text(cx - 110, top + 105, "пише WAL #1", size=11, color=POS)
    s += text(cx + 110, top + 105, "пише WAL #2", size=11, color=POS)

    b_file, _, _ = textbox(cx, top + 160, "Спільний файл журналу doc.wal\nПерехресні записи в один дескриптор!\nПозиції зсуву змішуються.", size=12, min_w=340, fill="#fff2f0", stroke=POS, bold=True)
    s += b_file

    s += mtext(cx, top + 265, [
        "Невизначений порядок байтів (race condition).",
        "Жоден процес не знає про правки іншого.",
        "Відновлення після краху розпізнає файл як сміття.",
    ], size=12, color=MUTED)

    # Права панель: Ексклюзивне блокування (Lease / Lock)
    px = P[1]
    p, top = panel(px, PY, PW, PH, "З блокуванням (flock / Web Locks / SQLite)")
    s += p
    cx = px + PW / 2

    b_p1_ok, _, _ = textbox(cx - 120, top + 40, "Процес A\n(Власник блокування)", size=12, min_w=150, fill="#e8f6ee", stroke=FIELD)
    b_p2_no, _, _ = textbox(cx + 120, top + 40, "Процес B\n(Другий екземпляр)", size=12, min_w=150, fill="#f4f6f8", stroke=MUTED)
    s += b_p1_ok + b_p2_no

    s += arrow(cx - 120, top + 75, cx - 50, top + 130, color=FIELD)
    s += line(cx + 120, top + 75, cx + 60, top + 120, color=POS, sw=1.5, dash="4,3")
    s += text(cx + 120, top + 105, "❌ LOCK_NB: BUSY", size=11, color=POS, bold=True)

    b_lock, _, _ = textbox(cx, top + 160, "Файл doc.lock (LOCK_EX) / Web Lock\nЕксклюзивне право на запис у WAL.\nПроцес B переходить у режим «Лише читання».", size=12, min_w=380, fill="#e8f4fc", stroke=NEG)
    s += b_lock

    s += mtext(cx, top + 265, [
        "Один активний записувач (Single Writer).",
        "Другий процес попереджає користувача про блокування",
        "або відкриває документ як копію для перегляду.",
    ], size=12, color=MUTED)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" '
           'markerHeight="6" orient="auto-start-reverse">\n'
           '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n</marker></defs>\n'
           '<rect width="100%%" height="100%%" fill="%s"/>\n%s\n</svg>'
           % (W, H, W, H, LINE, BG, s))
    with open(os.path.join(OUT, "multi-process-lock-conflict.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


# ── 4. Анатомія стану: Документ vs Сесія ────────────────────────────────────
def fig_session_restore_anatomy():
    W, H = 1080, 480
    s = ""

    s += text(W / 2, 35, "Розподіл стану при відновленні: Канонічні дані vs Стан взаємодії (Сесія)", size=16, bold=True)

    P, PW, PH, PY = [40, 560], 480, 390, 60

    # Ліва колонка: Канонічний документ
    px = P[0]
    p, top = panel(px, PY, PW, PH, "1. Канонічний стан (Документ)")
    s += p
    cx = px + PW / 2

    items_doc = [
        ("Дерево вузлів / параграфів", "Текстовий зміст, розмітка, атрибути"),
        ("Графічні об'єкти та шари", "Векторні криві, координати, палітри"),
        ("Таблиці та схеми", "Зв'язки сутностей, формули комірок"),
        ("Історія версій / лог змін", "Незмінні комбінації дій"),
    ]

    for i, (title, desc) in enumerate(items_doc):
        y_b = top + 25 + i * 58
        b, _, _ = textbox(cx, y_b, f"{title}\n{desc}", size=11, min_w=400, fill="#e8f6ee", stroke=FIELD)
        s += b

    s += mtext(cx, top + 275, [
        "Зберігається у doc.snap + doc.wal.",
        "Сувора валідація схем і контрольних сум.",
        "Джерело істини для експорту та синхронізації.",
    ], size=12, color=MUTED)

    # Права колонка: Ефемерний стан інтерфейсу
    px = P[1]
    p, top = panel(px, PY, PW, PH, "2. Стан робочої сесії (UI Context)")
    s += p
    cx = px + PW / 2

    items_ui = [
        ("Позиція курсору та виділення", "Рядок, колонка, активний діапазон символів"),
        ("Зсув прокрутки (Scroll Offset)", "Поточні координати X/Y вікна перегляду"),
        ("Відкриті панелі та масштаб", "Дерево відкритих вкладок, Zoom 125%"),
        ("Черга відправки (Outbox)", "Локальні мутації, що чекають на мережу"),
    ]

    for i, (title, desc) in enumerate(items_ui):
        y_b = top + 25 + i * 58
        b, _, _ = textbox(cx, y_b, f"{title}\n{desc}", size=11, min_w=400, fill="#e8f4fc", stroke=NEG)
        s += b

    s += mtext(cx, top + 275, [
        "Зберігається окремо (session.json / localStorage).",
        "Якщо пошкоджено — скидається до значень за замовчуванням.",
        "Відновлює відчуття неперервності роботи людини.",
    ], size=12, color=MUTED)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" '
           'markerHeight="6" orient="auto-start-reverse">\n'
           '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/>\n</marker></defs>\n'
           '<rect width="100%%" height="100%%" fill="%s"/>\n%s\n</svg>'
           % (W, H, W, H, LINE, BG, s))
    with open(os.path.join(OUT, "session-restore-anatomy.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    fig_torn_write_vs_atomic_rename()
    fig_wal_and_snapshot_lifecycle()
    fig_multi_process_lock_conflict()
    fig_session_restore_anatomy()
    print("Згенеровано 4 фігури в img/")
