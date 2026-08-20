# -*- coding: utf-8 -*-
"""Генератор векторних SVG-ілюстрацій для теми «Реляційна модель і нормалізація даних».
Використовує спільну бібліотеку svgkit з scripts/.
"""

import sys
import os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_relational_anatomy():
    """Фігура 1: Анатомія реляційної моделі — домени, схема відношення, кортежі, кардинальність та арність."""
    w, h = 880, 520
    frags = []

    # Заголовок блоку доменів
    frags.append(rect(30, 45, 820, 95, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(440, 68, "ФУНДАМЕНТАЛЬНІ МАТЕМАТИЧНІ ДОМЕНИ (ТИПИ ЗНАЧЕНЬ)", size=13, color=MUTED, bold=True))

    # Окремі домени
    doms = [
        ("D₁: UserID", "INT > 0", 120),
        ("D₂: Email", "VARCHAR(255)", 310),
        ("D₃: Role", "{ADMIN, USER, GUEST}", 520),
        ("D₄: CreatedAt", "TIMESTAMP (UTC)", 730),
    ]
    for name, desc, cx in doms:
        frags.append(rect(cx - 90, 80, 180, 48, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
        frags.append(text(cx, 98, name, size=13, color=NEG, bold=True))
        frags.append(text(cx, 116, desc, size=11, color=MUTED))

    # Стрілки від доменів до схеми таблиці
    for _, _, cx in doms:
        frags.append(arrow(cx, 128, cx, 172, color=MUTED, sw=1.5))

    # Основна таблиця відношення
    frags.append(rect(30, 175, 820, 315, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))

    # Заголовок відношення (Схема R)
    frags.append(rect(30, 175, 820, 45, fill="#0f172a", stroke=LINE, sw=1.8, rx=0))
    frags.append(text(440, 203, "ВІДНОШЕННЯ: Users (Схема R ⊆ D₁ × D₂ × D₃ × D₄)", size=15, color="#ffffff", bold=True))

    # Рядок атрибутів (Заголовки стовпців)
    frags.append(rect(30, 220, 820, 42, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=0))
    cols = [
        ("user_id (PK)", 120, True, POS),
        ("email", 310, False, INK),
        ("role", 520, False, INK),
        ("created_at", 730, False, INK),
    ]
    for cname, cx, is_pk, color in cols:
        frags.append(text(cx, 246, cname, size=13, color=color, bold=True))

    # Вертикальні розділювачі стовпців
    for x_sep in [210, 420, 620]:
        frags.append(line(x_sep, 220, x_sep, 430, color="#cbd5e1", sw=1.2))

    # Рядки даних (Кортежі t₁, t₂, t₃)
    tuples_data = [
        ("101", "alice@example.com", "ADMIN", "2026-01-15 08:30:00", 285),
        ("102", "bob@example.com", "USER", "2026-02-01 14:12:45", 345),
        ("103", "charlie@example.com", "USER", "2026-02-18 19:04:10", 405),
    ]
    for uid, em, rl, ca, y in tuples_data:
        frags.append(line(30, y - 23, 850, y - 23, color="#f1f5f9", sw=1.0))
        frags.append(text(120, y, uid, size=13, color=POS, bold=True))
        frags.append(text(310, y, em, size=13, color=INK))
        frags.append(text(520, y, rl, size=13, color=INK))
        frags.append(text(730, y, ca, size=12, color=INK))

    # Ліва позначка кортежів (Кардинальність |R| = 3)
    frags.append(line(16, 265, 16, 425, color=NEG, sw=2.0))
    frags.append(line(16, 265, 26, 265, color=NEG, sw=2.0))
    frags.append(line(16, 425, 26, 425, color=NEG, sw=2.0))
    frags.append(text(12, 452, "Потужність |R| = 3 (множина кортежів)", size=12, color=NEG, anchor="start", bold=True))

    # Нижня позначка атрибутів (Арність k = 4)
    frags.append(line(35, 475, 845, 475, color=FIELD, sw=2.0))
    frags.append(line(35, 467, 35, 475, color=FIELD, sw=2.0))
    frags.append(line(845, 467, 845, 475, color=FIELD, sw=2.0))
    frags.append(text(440, 497, "Арність ступеня k = 4 (невпорядкована множина атрибутів)", size=12, color=FIELD, bold=True))

    render(os.path.join(OUT_DIR, "relational-anatomy.svg"), w, h, *frags)


def fig_data_anomalies():
    """Фігура 2: Три класичні аномалії денормалізованої схеми — вставка, видалення та оновлення."""
    w, h = 900, 480
    frags = []

    # Верхній блок: ненормалізована таблиця замовлень
    frags.append(rect(20, 30, 860, 160, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(20, 30, 860, 36, fill="#334155", stroke=LINE, sw=1.5, rx=0))
    frags.append(text(450, 53, "НЕНОРМАЛІЗОВАНА ТАБЛИЦЯ: OrderItems (змішування замовлення, клієнта й товару)", size=13, color="#ffffff", bold=True))

    # Стовпці
    headers = [
        ("order_id", 80),
        ("cust_id", 180),
        ("cust_city", 290),
        ("prod_id", 400),
        ("prod_name", 540),
        ("unit_price", 680),
        ("qty", 800),
    ]
    frags.append(rect(20, 66, 860, 30, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=0))
    for hname, cx in headers:
        frags.append(text(cx, 86, hname, size=12, color=INK, bold=True))

    rows_data = [
        ("1001", "C1", "Київ", "P1", "Ноутбук Pro", "45000", "1", 116),
        ("1002", "C1", "Київ", "P2", "Миша Wireless", "1200", "2", 146),
        ("1003", "C2", "Львів", "P1", "Ноутбук Pro", "45000", "1", 176),
    ]
    for oid, cid, city, pid, pname, price, qty, y in rows_data:
        frags.append(line(20, y - 18, 880, y - 18, color="#e2e8f0", sw=1.0))
        frags.append(text(80, y, oid, size=12, color=INK))
        frags.append(text(180, y, cid, size=12, color=INK))
        frags.append(text(290, y, city, size=12, color=INK))
        frags.append(text(400, y, pid, size=12, color=INK))
        frags.append(text(540, y, pname, size=12, color=INK))
        frags.append(text(680, y, price, size=12, color=INK))
        frags.append(text(800, y, qty, size=12, color=INK))

    # Три картки аномалій знизу
    cards = [
        (
            20, 215, 270, 240,
            "1. АНОМАЛІЯ ВСТАВКИ",
            POS,
            [
                "Неможливо додати новий",
                "товар (P3, «Монітор 4K»),",
                "доки його ніхто не купив,",
                "бо order_id є частиною PK",
                "і не може бути NULL.",
                "",
                "→ Фіктивні замовлення або",
                "  втрата каталогу товарів.",
            ]
        ),
        (
            315, 215, 270, 240,
            "2. АНОМАЛІЯ ВИДАЛЕННЯ",
            NEG,
            [
                "Якщо клієнт C2 скасовує",
                "єдине замовлення 1003,",
                "видалення рядка знищує",
                "всі дані про клієнта C2",
                "(місто Львів тощо).",
                "",
                "→ Побічне незворотне",
                "  стирання сутностей.",
            ]
        ),
        (
            610, 215, 270, 240,
            "3. АНОМАЛІЯ ОНОВЛЕННЯ",
            "#d97706",
            [
                "Зміна ціни товару P1",
                "вимагає оновлення тисяч",
                "рядків у таблиці замовлень.",
                "Збій на середині транзакції",
                "створює неузгодженість.",
                "",
                "→ Дублювання веде до",
                "  розбіжності фактів.",
            ]
        ),
    ]

    for x, y, cw, ch, title, color, lines in cards:
        frags.append(rect(x, y, cw, ch, fill="#ffffff", stroke=color, sw=1.8, rx=8))
        frags.append(rect(x, y, cw, 34, fill=color, stroke=color, sw=1.8, rx=0))
        frags.append(text(x + cw / 2, y + 22, title, size=13, color="#ffffff", bold=True))
        ty = y + 56
        for line_txt in lines:
            bold_flag = line_txt.startswith("→")
            col = INK if not bold_flag else color
            frags.append(text(x + 16, ty, line_txt, size=11, color=col, anchor="start", bold=bold_flag))
            ty += 19

    render(os.path.join(OUT_DIR, "data-anomalies.svg"), w, h, *frags)


def fig_normalization_ladder():
    """Фігура 3: Драбина нормалізації — послідовне усунення залежностей від 1NF до BCNF."""
    w, h = 900, 530
    frags = []

    steps = [
        (
            40, 50, 820, 85,
            "1NF (Перша нормальна форма)",
            "Атомарність значень: усунення списків, повторюваних груп та масивів у полях",
            "Правило: Кожен атрибут містить неподільне скалярне значення з базового домену.",
            "#0284c7"
        ),
        (
            40, 160, 820, 85,
            "2NF (Друга нормальна форма)",
            "Усунення часткових функціональних залежностей від складеного первинного ключа",
            "Правило: Кожен неключовий атрибут функціонально повно залежить від усього ключа (X → Y, де X = PK).",
            "#0d9488"
        ),
        (
            40, 270, 820, 85,
            "3NF (Третя нормальна форма)",
            "Усунення транзитивних залежностей між неключовими атрибутами",
            "Правило: Якщо X → Y, то X — суперключ АБО Y — первинний (входить до кандидатного ключа).",
            "#16a34a"
        ),
        (
            40, 380, 820, 85,
            "BCNF (Нормальна форма Бойса–Кодда)",
            "Повне очищення від надлишкових детермінантів при перетині кандидатних ключів",
            "Правило: Для будь-якої нетривіальної залежності X → Y детермінант X обов'язково є суперключем.",
            "#7c3aed"
        ),
    ]

    for x, y, bw, bh, title, subtitle, rule, color in steps:
        frags.append(rect(x, y, bw, bh, fill="#ffffff", stroke=color, sw=1.8, rx=8))
        frags.append(rect(x, y, 220, bh, fill=color, stroke=color, sw=1.8, rx=0))
        frags.append(text(x + 110, y + 48, title, size=13, color="#ffffff", bold=True))
        frags.append(text(x + 240, y + 34, subtitle, size=12, color=INK, anchor="start", bold=True))
        frags.append(text(x + 240, y + 62, rule, size=11, color=MUTED, anchor="start"))

    # Сполучні стрілки між сходами
    for y_arrow in [135, 245, 355]:
        frags.append(arrow(150, y_arrow, 150, y_arrow + 24, color=LINE, sw=2.0))

    # Нижня плашка про безвтратність декомпозиції
    frags.append(rect(40, 480, 820, 38, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(450, 504, "Теорема Хіта: Безвтратний природний зв'язок (Lossless Join) гарантується: R₁ ⋈ R₂ = R ⇔ R₁ ∩ R₂ → R₁ або R₁ ∩ R₂ → R₂", size=11, color=INK, bold=True))

    render(os.path.join(OUT_DIR, "normalization-ladder.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_relational_anatomy()
    fig_data_anomalies()
    fig_normalization_ladder()
    print("Всі фігури успішно згенеровано.")
