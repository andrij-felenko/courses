# -*- coding: utf-8 -*-
"""Фігури до теми «Data-контракти між продюсером і сховищем даних»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def panel(x, y, w, h, head, stroke="#b8c2cc", fill="#ffffff"):
    s = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=8)
    s += text(x + w / 2, y + 26, head, size=14, bold=True)
    return s, y + 42


# ── 1. Поломка без контракту vs захист із контрактом ─────────────────────────
def fig_break_without_contract():
    W, H = 1100, 500
    s = ""

    # Ліва половина: Без контракту
    p1, top1 = panel(30, 20, 500, 450, "Без контракту: неявне читання репліки", stroke=POS)
    s += p1

    b_prod1, _, _ = textbox(150, top1 + 45, "Сервіс замовлень\n(Продюсер)", size=13, min_w=170, fill="#fdf2f2", stroke=POS)
    b_db1, _, _ = textbox(150, top1 + 185, "Операційна БД\n(OLTP таблиці)", size=13, min_w=170)
    s += b_prod1 + b_db1
    s += arrow(150, top1 + 75, 150, top1 + 155, color=POS)
    s += text(150 + 65, top1 + 115, "Зміна схеми / DDL", size=11, color=POS, anchor="start")

    b_etl1, _, _ = textbox(400, top1 + 185, "Нічний ETL / CDC\n(Скрапінг БД)", size=13, min_w=160, stroke=POS)
    b_dwh1, _, _ = textbox(400, top1 + 335, "Аналітичне DWH\n(Дашборд виторгу)", size=13, min_w=160, fill="#fdf2f2", stroke=POS)
    s += b_etl1 + b_dwh1

    s += line(240, top1 + 185, 315, top1 + 185, color=LINE, dash="4,4")
    s += text(278, top1 + 175, "неявне", size=11, color=MUTED)
    s += arrow(400, top1 + 215, 400, top1 + 305, color=POS)
    s += text(400 + 60, top1 + 260, "Збій типів / Null", size=11, color=POS, bold=True, anchor="start")

    s += mtext(280, top1 + 405, [
        "Продюсер вважає базу суто своєю внутрішньою.",
        "Аналітика ламається о 03:00 при зміні полів.",
    ], size=12, color=POS)

    # Права половина: Із контрактом
    p2, top2 = panel(570, 20, 500, 450, "Із data-контрактом: явний вихідний порт", stroke=FIELD)
    s += p2

    b_prod2, _, _ = textbox(690, top2 + 45, "Сервіс замовлень\n(Продюсер)", size=13, min_w=170, fill="#e8f6ee", stroke=FIELD)
    b_gate, _, _ = textbox(690, top2 + 185, "Шлюз валідації\n(CI + Runtime)", size=13, min_w=170, stroke=FIELD)
    s += b_prod2 + b_gate

    s += arrow(690, top2 + 75, 690, top2 + 155, color=FIELD)
    s += text(690 + 60, top2 + 115, "Контрактні події", size=11, color=FIELD, anchor="start")

    b_reg, _, _ = textbox(930, top2 + 45, "Реєстр схем і SLO\n(Версії контракту)", size=13, min_w=160)
    s += b_reg
    s += line(780, top2 + 45, 845, top2 + 45, color=LINE, dash="3,3")
    s += text(812, top2 + 35, "аудит", size=11, color=MUTED)

    b_dwh2, _, _ = textbox(930, top2 + 185, "Аналітичне DWH\n(Чисті дані)", size=13, min_w=160, fill="#e8f6ee", stroke=FIELD)
    b_dlq, _, _ = textbox(690, top2 + 325, "Карантин (DLQ)\n(Алерти автору)", size=13, min_w=170, fill="#fff9db", stroke="#d97706")
    s += b_dwh2 + b_dlq

    s += arrow(780, top2 + 185, 845, top2 + 185, color=FIELD)
    s += text(812, top2 + 172, "валідовано", size=11, color=FIELD)

    s += arrow(690, top2 + 215, 690, top2 + 295, color="#d97706")
    s += text(690 + 60, top2 + 255, "помилка схеми/SLO", size=11, color="#d97706", anchor="start")

    s += mtext(820, top2 + 405, [
        "Контракт ізолює внутрішню БД від DWH.",
        "Несумісні зміни ловляться до потрапляння у склад.",
    ], size=12, color=FIELD)

    render(os.path.join(OUT, "break-without-contract.svg"), W, H, s)


# ── 2. Анатомія data-контракту: чотири шари ──────────────────────────────────
def fig_contract_anatomy_and_lifecycle():
    W, H = 1060, 480
    s = ""

    p, top = panel(40, 20, 980, 430, "Анатомія Data-контракту: багатошарова структура угоди")
    s += p

    layers = [
        ("1. Синтаксис і типи", "Імена полів, типи даних (int, string, decimal), обов'язковість (nullability), кодування.", "#eef3f8", LINE),
        ("2. Бізнес-семантика", "Одиниці виміру (центи/долари, UTC-час), скінченний автомат статусів, опис сутності.", "#e8f6ee", FIELD),
        ("3. Інваріанти якості (SLO)", "Унікальність первинного ключа, допустимі діапазони, відсоток заповненості, допустимий лаг.", "#fdf8e2", "#d97706"),
        ("4. Володіння та регламент", "Команда-власник (Slack/Email), рівень конфіденційності (PII/GDPR), політика застарівання.", "#f4f6f8", LINE),
    ]

    ly = top + 20
    for title, desc, bg_col, stroke_col in layers:
        s += rect(70, ly, 920, 72, fill=bg_col, stroke=stroke_col, sw=1.5, rx=6)
        s += text(90, ly + 28, title, size=14, bold=True, anchor="start", color=stroke_col)
        s += text(90, ly + 52, desc, size=13, anchor="start", color=INK)
        ly += 88

    s += mtext(530, ly + 15, [
        "Контракт — це не просто схема DDL, а повна специфікація поведінки, якості та відповідальності.",
    ], size=13, color=MUTED, bold=True)

    render(os.path.join(OUT, "contract-anatomy-and-lifecycle.svg"), W, H, s)


# ── 3. Дворівневий контроль: Shift-Left у CI/CD та динамічний шлюз ────────────
def fig_shift_left_enforcement():
    W, H = 1100, 520
    s = ""

    p1, top1 = panel(30, 20, 1040, 470, "Дворівневий захист даних: Статичний аудит (CI/CD) та Динамічний шлюз (Runtime)")
    s += p1

    # Рівень 1: Статичний контроль (Shift-Left)
    s += rect(60, top1 + 20, 980, 175, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=8)
    s += text(80, top1 + 45, "Рівень 1: Статичний контроль у CI/CD продюсера (Shift-Left)", size=13, bold=True, anchor="start", color=NEG)

    b_pr, _, _ = textbox(170, top1 + 115, "Pull Request\nу коді продюсера", size=12, min_w=150)
    b_ci, _, _ = textbox(410, top1 + 115, "CI linter схем і\nBreaking Check", size=12, min_w=160, stroke=NEG)
    b_reg, _, _ = textbox(670, top1 + 115, "Реєстр контрактів\n(Сховище версій)", size=12, min_w=160)
    b_merge, _, _ = textbox(910, top1 + 115, "Успішний реліз /\nОновлення схеми", size=12, min_w=150, fill="#e8f6ee", stroke=FIELD)

    s += b_pr + b_ci + b_reg + b_merge
    s += arrow(250, top1 + 115, 325, top1 + 115, color=LINE)
    s += arrow(495, top1 + 115, 585, top1 + 115, color=NEG)
    s += text(540, top1 + 100, "порівняння", size=11, color=NEG)
    s += arrow(755, top1 + 115, 830, top1 + 115, color=FIELD)
    s += text(792, top1 + 100, "сумісно", size=11, color=FIELD)

    # Рівень 2: Динамічний контроль (Runtime Ingestion Gatekeeper)
    s += rect(60, top1 + 225, 980, 195, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=8)
    s += text(80, top1 + 250, "Рівень 2: Динамічний шлюз під час потокового завантаження (Runtime)", size=13, bold=True, anchor="start", color=FIELD)

    b_evt, _, _ = textbox(170, top1 + 325, "Потік подій /\nБрокер (Kafka)", size=12, min_w=150)
    b_val, _, _ = textbox(430, top1 + 325, "Шлюз валідації\n(Типи, Null, SLO)", size=12, min_w=170, stroke=FIELD)
    b_dwh, _, _ = textbox(720, top1 + 325, "Аналітичне DWH /\nLakehouse", size=12, min_w=160, fill="#e8f6ee", stroke=FIELD)
    b_dlq, _, _ = textbox(950, top1 + 325, "Карантин (DLQ)\n+ Алерти інженерам", size=12, min_w=160, fill="#fff9db", stroke="#d97706")

    s += b_evt + b_val + b_dwh + b_dlq
    s += arrow(250, top1 + 325, 340, top1 + 325, color=LINE)
    s += arrow(520, top1 + 325, 635, top1 + 325, color=FIELD)
    s += text(575, top1 + 310, "валідно", size=11, color=FIELD)

    s += arrow(805, top1 + 325, 865, top1 + 325, color="#d97706")
    s += text(835, top1 + 310, "помилка", size=11, color="#d97706")

    render(os.path.join(OUT, "shift-left-enforcement.svg"), W, H, s)


if __name__ == "__main__":
    fig_break_without_contract()
    fig_contract_anatomy_and_lifecycle()
    fig_shift_left_enforcement()
    print("Figures generated successfully.")
