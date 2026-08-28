# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра теми
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── 1. manual-drift-decay: дрейф середовища розробника ────────────────────────
def fig_manual_drift_decay():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 30, "Дрейф середовища: чому ручна збірка на ноутбуці не є джерелом правди", size=15, color=INK, bold=True))

    # Ліва колонка: Ноутбук інженера (суб'єктивний стан)
    p.append(rect(30, 65, 360, 260, fill=REDBG, stroke=POS, sw=2, rx=10))
    p.append(text(210, 95, "Робоча станція розробника", size=13.5, color=POS, bold=True))
    
    dev_items = [
        "• Локальні незакомічені правки у хедері",
        "• Застарілий кеш об'єктних файлів (.o)",
        "• Компілятор GCC 12.2 замість 12.3 на CI",
        "• Змінні середовища: унікальний CFLAGS",
        "• Ручний вибір профілю (Debug vs Release)",
        "• Забутий тестовий лог або знятий Watchdog",
    ]
    for j, item in enumerate(dev_items):
        p.append(text(48, 130 + j * 24, item, size=11, color=INK, anchor="start"))
    
    p.append(text(210, 295, "Вердикт: «Працює на моєму столі»", size=11.5, color=POS, bold=True))

    # Стрілка дрейфу / розриву
    p.append(arrow(400, 195, 440, 195, color=POS, sw=2.5))
    p.append(text(420, 180, "передача", size=10, color=POS, bold=True))
    p.append(text(420, 215, "через чат", size=9.5, color=MUTED))

    # Права колонка: Заводський конвеєр / Реальне поле
    p.append(rect(450, 65, 360, 260, fill=FILL, stroke=LINE, sw=2, rx=10))
    p.append(text(630, 95, "Серійний виріб у полі", size=13.5, color=INK, bold=True))

    field_items = [
        "• Оптимізатор викинув порожній цикл затримки",
        "• Інша структура RAM спричинила зависання",
        "• Залишений debug-код переповнив Flash",
        "• Невідповідність протоколу між платами",
        "• Збій таймінгу шини без логів UART",
        "• Закирпичений завантажувач при OTA",
    ]
    for j, item in enumerate(field_items):
        p.append(text(468, 130 + j * 24, item, size=11, color=INK, anchor="start"))

    p.append(text(630, 295, "Підсумок: дорогий польовий збій", size=11.5, color=POS, bold=True))

    render(os.path.join(OUT, "manual-drift-decay.svg"), W, H, *p)


# ── 2. checklist-fatigue-risk: експоненційне падіння надійності ручного чеклиста ─
def fig_checklist_fatigue_risk():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 30, "Втома чеклиста: експоненційне зростання ризику помилки", size=15, color=INK, bold=True))

    # Формула надійності вгорі
    p.append(rect(50, 60, 740, 48, fill=BLUEBG, stroke=NEG, sw=1.5, rx=8))
    p.append(text(420, 89, "Імовірність безпомилкового випуску:  P = (1 − p)ᴺ ,  де p — ризик на кроці, N — кількість кроків", size=11.5, color=NEG, bold=True))

    # Стовпчики кроків чеклиста
    steps_data = [
        (5, "5 кроків", "86%", "14%", FIELD, GREENBG),
        (10, "10 кроків", "74%", "26%", AMBER, AMBERBG),
        (15, "15 кроків", "63%", "37%", AMBER, AMBERBG),
        (20, "20 кроків", "54%", "46%", POS, REDBG),
        (30, "30 кроків", "40%", "60%", POS, REDBG),
    ]

    base_x = 70
    col_w = 124
    gap = 20

    for i, (n, label, p_succ, p_fail, col, bg) in enumerate(steps_data):
        cx = base_x + i * (col_w + gap)
        p.append(rect(cx, 130, col_w, 190, fill=bg, stroke=col, sw=1.8, rx=8))
        p.append(text(cx + col_w / 2, 155, label, size=12.5, color=INK, bold=True))
        p.append(text(cx + col_w / 2, 175, f"N = {n}", size=10, color=MUTED))

        # Успіх
        p.append(text(cx + col_w / 2, 210, "Успіх", size=10.5, color=MUTED))
        p.append(text(cx + col_w / 2, 235, p_succ, size=16, color=col, bold=True))

        # Помилка
        p.append(line(cx + 10, 255, cx + col_w - 10, 255, color=col, sw=1, dash="3,3"))
        p.append(text(cx + col_w / 2, 278, "Ризик браку:", size=10, color=MUTED))
        p.append(text(cx + col_w / 2, 300, p_fail, size=13, color=POS, bold=True))

    render(os.path.join(OUT, "checklist-fatigue-risk.svg"), W, H, *p)


# ── 3. incident-blast-radius: ціна помилки на різних етапах життя ─────────────
def fig_incident_blast_radius():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 30, "Радіус ураження: геометричне зростання вартості релізного дефекту", size=15, color=INK, bold=True))

    stages = [
        (40, "1. Лабораторний стіл", "1×", "Хвилини", "Перекомпіляція на місці", FIELD, GREENBG),
        (235, "2. Серійний конвеєр", "50×", "Години / дні", "Зупинка лінії, розпайка", AMBER, AMBERBG),
        (430, "3. Склад і логістика", "500×", "Тижні", "Розпакування, перепрошивка", POS, REDBG),
        (625, "4. Експлуатація в полі", "10 000×", "Місяці", "Фізичний відклик, втрата репутації", POS, REDBG),
    ]

    box_w = 175
    box_h = 245
    for x, title, cost, time_loss, desc, col, bg in stages:
        p.append(rect(x, 70, box_w, box_h, fill=bg, stroke=col, sw=2, rx=10))
        p.append(text(x + box_w / 2, 98, title, size=11.5, color=INK, bold=True))
        
        p.append(line(x + 12, 115, x + box_w - 12, 115, color=col, sw=1.2))

        p.append(text(x + box_w / 2, 140, "Множник ціни:", size=9.5, color=MUTED))
        p.append(text(x + box_w / 2, 172, cost, size=20, color=col, bold=True))

        p.append(text(x + box_w / 2, 205, "Час усунення:", size=9.5, color=MUTED))
        p.append(text(x + box_w / 2, 225, time_loss, size=11.5, color=INK, bold=True))

        p.append(line(x + 12, 245, x + box_w - 12, 245, color=col, sw=1, dash="2,2"))
        p.append(text(x + box_w / 2, 275, desc, size=9.5, color=INK))

    # Стрілки переходу вартості
    p.append(arrow(215, 192, 235, 192, color=INK, sw=2))
    p.append(arrow(410, 192, 430, 192, color=INK, sw=2))
    p.append(arrow(605, 192, 625, 192, color=INK, sw=2))

    render(os.path.join(OUT, "incident-blast-radius.svg"), W, H, *p)


# ── 4. hermetic-pipeline-contract: автоматизований конвеєр випуску ────────────
def fig_hermetic_pipeline_contract():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 30, "Герметичний конвеєр: нульова довіра до робочих станцій", size=15, color=INK, bold=True))

    steps = [
        (30, "Git Tag / SHA", BLUEBG, NEG, ["Чистий клон", "Зафіксований коміт", "Без локальних правок"]),
        (190, "Ізольоване оточення", BLUEBG, NEG, ["Docker-контейнер", "Фіксований тулчейн", "Замкнені бібліотеки"]),
        (350, "Автоматична збірка", GREENBG, FIELD, ["Крос-компіляція", "Release-прапорці", "Статичний аналіз"]),
        (510, "Верифікація", AMBERBG, AMBER, ["Перевірка мапи пам'яті", "DWARF-символи у сховище", "Розрахунок SHA-256"]),
        (670, "Підписаний реліз", GREENBG, FIELD, ["Криптографічний підпис", "Генерація SBOM", "Готовий пакет"]),
    ]

    sw, sh = 135, 190
    sy = 80
    for i, (x, title, bg, col, lines_b) in enumerate(steps):
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, sy, sw, sh, fill=bg, stroke=col, sw=1.8, rx=8))
        p.append(text(x + sw / 2, sy + 25, title, size=11, color=tagcol, bold=True))
        p.append(line(x + 10, sy + 38, x + sw - 10, sy + 38, color=col, sw=1))

        for j, l in enumerate(lines_b):
            p.append(text(x + sw / 2, sy + 65 + j * 24, l, size=9.5, color=INK))

        p.append(rect(x + 10, sy + 145, sw - 20, 32, fill=BG, stroke=col, sw=1, rx=4))
        p.append(text(x + sw / 2, sy + 165, f"Фаза {i+1}", size=10, color=tagcol, bold=True))

        if i < len(steps) - 1:
            p.append(arrow(x + sw, sy + sh / 2, x + sw + 25, sy + sh / 2, color=INK, sw=2))

    # Нижній висновок-гарантія
    p.append(rect(30, 290, 775, 48, fill=FILL, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(420, 320, "Гарантія: однаковий вхід завжди дає побайтово однаковий образ незалежно від того, хто натиснув кнопку", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "hermetic-pipeline-contract.svg"), W, H, *p)


if __name__ == "__main__":
    fig_manual_drift_decay()
    fig_checklist_fatigue_risk()
    fig_incident_blast_radius()
    fig_hermetic_pipeline_contract()
    print("All figures generated successfully.")
