# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Нескінченна драбина квитування у задачі двох генералів ───────────────
def fig_ack_ladder():
    W, H = 960, 490
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 26, "Нескінченна драбина квитування (ACK ladder) у задачі двох генералів", size=16, color=INK, bold=True))

    # Стовпчик Генерал 1 (Вузол A)
    g1_x, g1_y, g1_w, g1_h = 30, 48, 220, 420
    p.append(rect(g1_x, g1_y, g1_w, g1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(rect(g1_x, g1_y, g1_w, 34, fill="#2457d6", stroke="#2457d6", sw=0, rx=6))
    p.append(text(g1_x + g1_w / 2, g1_y + 22, "Генерал 1 (Вузол A)", size=13.5, color="#ffffff", bold=True))

    # Стовпчик Генерал 2 (Вузол B)
    g2_x, g2_y, g2_w, g2_h = 710, 48, 220, 420
    p.append(rect(g2_x, g2_y, g2_w, g2_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    p.append(rect(g2_x, g2_y, g2_w, 34, fill="#c0392b", stroke="#c0392b", sw=0, rx=6))
    p.append(text(g2_x + g2_w / 2, g2_y + 22, "Генерал 2 (Вузол B)", size=13.5, color="#ffffff", bold=True))

    # Середня зона: Ненадійний канал зв'язку
    ch_x, ch_y, ch_w, ch_h = 265, 48, 430, 420
    p.append(rect(ch_x, ch_y, ch_w, ch_h, fill="#fdfbf7", stroke="#f1e3cc", sw=1.2, rx=8))
    p.append(text(ch_x + ch_w / 2, ch_y + 22, "Ненадійний канал (втрата пакетів p > 0)", size=12.5, color="#b45309", bold=True))

    # Лінії часової шкали на стику з каналом (без перетину з боксами генералів)
    t1_x = 258
    t2_x = 702
    p.append(line(t1_x, g1_y + 40, t1_x, g1_y + g1_h - 15, color="#94a3b8", sw=1.5, dash="4,4"))
    p.append(line(t2_x, g2_y + 40, t2_x, g2_y + g2_h - 15, color="#94a3b8", sw=1.5, dash="4,4"))

    # Крок 1: Запит атаки
    y1_start, y1_end = 100, 130
    p.append(arrow(t1_x, y1_start, t2_x, y1_end, color="#2457d6", sw=1.8))
    p.append(textbox(ch_x + ch_w / 2, 108, "1. Повідомлення: «Атака о 06:00»", size=11.5, pad=5, fill="#ffffff", stroke="#2457d6", color="#2457d6", bold=True)[0])
    p.append(fitbox(g1_x + 8, 90, g1_w - 16, 52, "Не може атакувати:\nякщо лист перехоплено,\nзагине на самоті.", size=10.5, fill="#eff6ff", stroke="#bfdbfe", color=INK))

    # Крок 2: Квитанція ACK1
    y2_start, y2_end = 168, 198
    p.append(arrow(t2_x, y2_start, t1_x, y2_end, color="#c0392b", sw=1.8))
    p.append(textbox(ch_x + ch_w / 2, 176, "2. Квитанція ACK: «Згоден на 06:00»", size=11.5, pad=5, fill="#ffffff", stroke="#c0392b", color="#c0392b", bold=True)[0])
    p.append(fitbox(g2_x + 8, 158, g2_w - 16, 52, "Не може атакувати:\nякщо ACK загубиться,\nГенерал 1 не вийде.", size=10.5, fill="#fef2f2", stroke="#fecaca", color=INK))

    # Крок 3: Квитанція ACK2 (підтвердження на квитанцію)
    y3_start, y3_end = 236, 266
    p.append(arrow(t1_x, y3_start, t2_x, y3_end, color="#2457d6", sw=1.8))
    p.append(textbox(ch_x + ch_w / 2, 244, "3. Квитанція ACK2: «Отримав твій ACK»", size=11.5, pad=5, fill="#ffffff", stroke="#2457d6", color="#2457d6", bold=True)[0])
    p.append(fitbox(g1_x + 8, 226, g1_w - 16, 52, "Не може атакувати:\nчи дійшов ACK2 до\nГенерала 2?", size=10.5, fill="#eff6ff", stroke="#bfdbfe", color=INK))

    # Крок 4: Квитанція ACK3
    y4_start, y4_end = 304, 334
    p.append(arrow(t2_x, y4_start, t1_x, y4_end, color="#c0392b", sw=1.8))
    p.append(textbox(ch_x + ch_w / 2, 312, "4. Квитанція ACK3: «Отримав твій ACK2»", size=11.5, pad=5, fill="#ffffff", stroke="#c0392b", color="#c0392b", bold=True)[0])
    p.append(fitbox(g2_x + 8, 294, g2_w - 16, 52, "Не може атакувати:\nчи отримав Генерал 1\nцей ACK3?", size=10.5, fill="#fef2f2", stroke="#fecaca", color=INK))

    # Підсумок у нижній частині
    p.append(fitbox(ch_x + 12, 375, ch_w - 24, 80,
                    "Рекурсивна невизначеність: останній відправник завжди сумнівається.\n"
                    "Жодна скінченна кількість квитанцій k не забезпечує\n"
                    "гарантованого одночасного наступу.",
                    size=11, fill="#ffffff", stroke="#dc2626", color="#dc2626", bold=True))

    render(os.path.join(OUT, "two-generals-ack-ladder.svg"), W, H, *p,
           title="Нескінченна драбина квитування у задачі двох генералів")


# ── Фіг. 2: Ієрархія станів знання (Epistemic Logic & Common Knowledge) ──────────
def fig_common_knowledge():
    W, H = 960, 430
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 26, "Ієрархія станів епістемічного знання у розподіленій системі", size=16, color=INK, bold=True))

    levels = [
        ("Рівень 0: Одиничне знання", "K_1(m)",
         "Генерал 1 знає час m.\nГенерал 2 не знає\nпро плани першого.",
         "Спільних дій немає", "#64748b"),
        ("Рівень 1: Взаємне знання 1-го порядку", "E^1(m) = K_1(m) ∧ K_2(m)",
         "Генерал 2 отримав лист.\nОбидва знають m.\nАле перший не знає,\nчи лист дійшов.",
         "Немає взаємної довіри", "#2563eb"),
        ("Рівень 2: Взаємне знання 2-го порядку", "E^2(m) = K_1(K_2(m)) ∧ ...",
         "Генерал 1 отримав ACK.\nВін знає, що другий знає.\nАле другий не знає,\nчи дійшов його ACK.",
         "Синхронний наступ неможливий", "#7c3aed"),
        ("Рівень ∞: Спільне знання", "C(m) = ⋀_{k=1}^∞ E^k(m)",
         "Усі знають, що всі знають,\nщо всі знають... до ∞.\nОбов'язкова вимога\nдетермінізму.",
         "НЕДОСЯЖНЕ при p > 0", "#dc2626"),
    ]

    card_w = 215.0
    card_h = 335.0
    gap = 20.0
    start_x = (W - (4 * card_w + 3 * gap)) / 2
    top_y = 55.0

    for i, (title, formula, body, status_text, col) in enumerate(levels):
        cx = start_x + i * (card_w + gap)
        p.append(rect(cx, top_y, card_w, card_h, fill="#fbfcfd", stroke="#cbd5e1", sw=1.5, rx=8))
        # Top color accent
        p.append(rect(cx, top_y, card_w, 7, fill=col, stroke=col, sw=0, rx=4))

        # Title and formula
        p.append(fitbox(cx + 8, top_y + 14, card_w - 16, 44, title, size=11.5, fill="#ffffff", stroke="#e2e8f0", color=col, bold=True))
        p.append(fitbox(cx + 8, top_y + 64, card_w - 16, 36, formula, size=11, fill="#f8fafc", stroke="#cbd5e1", color=INK, bold=True))

        # Body explanation
        p.append(fitbox(cx + 8, top_y + 108, card_w - 16, 130, body, size=11, fill="#ffffff", stroke="#f1f5f9", color=INK))

        # Status note at bottom
        p.append(fitbox(cx + 8, top_y + 248, card_w - 16, 72, status_text, size=11,
                        fill="#fef2f2" if col == "#dc2626" else "#f0fdf4",
                        stroke=col, color=col, bold=True))

        # Arrow between cards
        if i < 3:
            arrow_x = cx + card_w + 2
            arrow_y = top_y + card_h / 2
            p.append(arrow(arrow_x, arrow_y, arrow_x + gap - 4, arrow_y, color="#94a3b8", sw=1.8))

    render(os.path.join(OUT, "common-knowledge-hierarchy.svg"), W, H, *p,
           title="Ієрархія станів знання у розподіленій системі")


# ── Фіг. 3: Практичні інженерні патерни обходу проблеми ─────────────────────────
def fig_practical_patterns():
    W, H = 960, 420
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, 26, "Практичні інженерні стратегії обходу задачі двох генералів", size=16, color=INK, bold=True))

    patterns = [
        ("1. Ідемпотентність і повтори", "At-Least-Once + Дедуплікація",
         "Клієнт генерує ключ запиту.\n"
         "Сервер фіксує дію в сховищі.\n"
         "Якщо відповідь загубилась,\n"
         "клієнт надсилає повтор.\n"
         "Сервер повертає кеш\n"
         "без повторного списання.",
         "Захист від подвійних транзакцій", "#2563eb"),

        ("2. Оренди та фізичний час", "Часові лізи (Leases)",
         "Вузол отримує право на дію\n"
         "на фіксований інтервал T.\n"
         "Після T право автоматично гасне.\n"
         "Не потребує фінального\n"
         "підтвердження звільнення.",
         "Автономне рішення за таймером", "#16a34a"),

        ("3. Оптимістичні Саги", "Компенсаційні транзакції",
         "Сервіси фіксують дію локально\n"
         "без блокуючого очікування.\n"
         "У разі аварії чи таймауту\n"
         "запускається компенсація.\n"
         "Система сходиться з часом.",
         "Кінцева узгодженість замість блокування", "#d97706"),
    ]

    card_w = 285.0
    card_h = 330.0
    gap = 26.0
    start_x = (W - (3 * card_w + 2 * gap)) / 2
    top_y = 55.0

    for i, (title, sub, body, benefit, col) in enumerate(patterns):
        cx = start_x + i * (card_w + gap)
        p.append(rect(cx, top_y, card_w, card_h, fill="#fbfcfd", stroke="#cbd5e1", sw=1.5, rx=8))
        # Top color accent
        p.append(rect(cx, top_y, card_w, 7, fill=col, stroke=col, sw=0, rx=4))

        p.append(text(cx + card_w / 2, top_y + 28, title, size=13, color=col, bold=True))
        p.append(text(cx + card_w / 2, top_y + 46, sub, size=11, color=MUTED, italic=True))
        p.append(line(cx + 15, top_y + 56, cx + card_w - 15, top_y + 56, color="#e2e8f0", sw=1.2))

        # Body explanation
        p.append(fitbox(cx + 12, top_y + 66, card_w - 24, 175, body, size=11.5,
                        fill="#ffffff", stroke="#f1f5f9", color=INK))

        # Bottom benefit box
        p.append(fitbox(cx + 12, top_y + 250, card_w - 24, 66, benefit, size=11,
                        fill="#eff6ff" if col == "#2563eb" else ("#f0fdf4" if col == "#16a34a" else "#fffbeb"),
                        stroke=col, color=INK, bold=True))

    render(os.path.join(OUT, "two-generals-practical-patterns.svg"), W, H, *p,
           title="Практичні інженерні стратегії обходу задачі двох генералів")


if __name__ == "__main__":
    fig_ack_ladder()
    fig_common_knowledge()
    fig_practical_patterns()
    print("All figures generated successfully.")
