# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Синтаксичне проти логічного зачеплення ───────────────────────────
def fig_logical_vs_structural():
    W, H = 960, 480
    frags = []

    # Фон і розділювач двох світів
    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))
    frags.append(line(W / 2, 40, W / 2, H - 40, color="#d0d7de", sw=1.5, dash="6,6"))

    # ── ЛІВА ЧАСТИНА: Синтаксичне (структурне) зачеплення
    lx, ly, lw, lh = 30, 40, 420, 400
    frags.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=12))
    frags.append(text(lx + lw / 2, ly + 32, "Синтаксичне зачеплення (AST / Компілятор)", size=15, bold=True, color=NEG))
    frags.append(text(lx + lw / 2, ly + 52, "видиме в тексті коду та графі викликів", size=12, color=MUTED))

    # Блоки модулів ліворуч
    b1_body, b1_w, b1_h = textbox(lx + lw / 2, ly + 120, "Модуль A\n(OrderService)", size=13, pad=12,
                                  fill="#eff6ff", stroke=NEG, sw=1.8, min_w=180)
    frags.append(b1_body)

    b2_body, b2_w, b2_h = textbox(lx + lw / 2, ly + 250, "Модуль B\n(PaymentGateway)", size=13, pad=12,
                                  fill="#eff6ff", stroke=NEG, sw=1.8, min_w=180)
    frags.append(b2_body)

    # Прямий виклик
    frags.append(arrow(lx + lw / 2, ly + 120 + b1_h / 2, lx + lw / 2, ly + 250 - b2_h / 2, color=NEG, sw=2.2))
    frags.append(text(lx + lw / 2 + 75, ly + 185, "import / call", size=12, bold=True, color=NEG))

    # Підсумок ліворуч
    frags.append(rect(lx + 20, ly + 310, lw - 40, 70, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=8))
    frags.append(text(lx + lw / 2, ly + 336, "Аналізатор: бачить явне ребро в графі", size=12, bold=True, color=INK))
    frags.append(text(lx + lw / 2, ly + 358, "Зміна інтерфейсу → помилка компіляції", size=11, color=FIELD))

    # ── ПРАВА ЧАСТИНА: Логічне (еволюційне) зачеплення
    rx, ry, rw, rh = 510, 40, 420, 400
    frags.append(rect(rx, ry, rw, rh, fill="#fffaf9", stroke="#fed7aa", sw=1.5, rx=12))
    frags.append(text(rx + rw / 2, ry + 32, "Логічне зачеплення (Історія Git / Co-Change)", size=15, bold=True, color=POS))
    frags.append(text(rx + rw / 2, ry + 52, "невидиме компілятору, живе в спільних правках", size=12, color=MUTED))

    # Блоки модулів праворуч (розділені)
    b3_body, b3_w, b3_h = textbox(rx + 110, ry + 130, "Сервіс A\n(Billing)", size=13, pad=12,
                                  fill="#fff1f2", stroke=POS, sw=1.8, min_w=140)
    frags.append(b3_body)

    b4_body, b4_w, b4_h = textbox(rx + 310, ry + 130, "Сервіс B\n(InvoicePDF)", size=13, pad=12,
                                  fill="#fff1f2", stroke=POS, sw=1.8, min_w=140)
    frags.append(b4_body)

    # Перекреслений прямий зв'язок
    frags.append(line(rx + 180, ry + 130, rx + 240, ry + 130, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(text(rx + 210, ry + 118, "немає імпорту", size=10, color=MUTED))

    # Прихований спільний концепт (магічні константи / неявний формат)
    frags.append(rect(rx + 60, ry + 210, rw - 120, 60, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(rx + rw / 2, ry + 234, "Неявне припущення / Магічний код", size=12, bold=True, color=POS))
    frags.append(text(rx + rw / 2, ry + 252, "формат статусу 'PAID_V2' = 0x4F", size=11, color=MUTED))

    # Пунктирні стрілки до прихованого знання
    frags.append(arrow(rx + 110, ry + 130 + b3_h / 2, rx + 120, ry + 210, color=POS, sw=1.6))
    frags.append(arrow(rx + 310, ry + 130 + b4_h / 2, rx + 300, ry + 210, color=POS, sw=1.6))

    # Підсумок праворуч
    frags.append(rect(rx + 20, ry + 310, rw - 40, 70, fill="#ffffff", stroke="#f87171", sw=1.2, rx=8))
    frags.append(text(rx + rw / 2, ry + 336, "Аналізатор: бачить 0 залежностей (хибний спокій)", size=12, bold=True, color=POS))
    frags.append(text(rx + rw / 2, ry + 358, "Git-журнал: файли змінюються разом у 95% комітів", size=11, color=INK))

    render(os.path.join(IMG, 'logical-vs-structural.svg'), W, H, *frags,
           title="Порівняння синтаксичного та логічного зачеплення")


# ── Фігура 2: Хронологія комітів і матриця спільних змін ───────────────────────
def fig_co_change_matrix():
    W, H = 960, 460
    frags = []

    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    # ── ЛІВА ЧАСТИНА: Часова шкала комітів
    lx, ly, lw, lh = 30, 30, 450, 400
    frags.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=12))
    frags.append(text(lx + lw / 2, ly + 28, "Транзакції в системі контролю версій (Git)", size=14, bold=True, color=INK))

    commits = [
        ("C1", "feat(tax): нова ставка ПДВ", ["TaxCalculator.cs", "InvoicePdf.cs"]),
        ("C2", "fix(auth): таймаут токена", ["AuthToken.cs", "UserSession.cs"]),
        ("C3", "feat(tax): пільговий експорт", ["TaxCalculator.cs", "InvoicePdf.cs", "AuditLog.cs"]),
        ("C4", "refactor(auth): ротація ключів", ["AuthToken.cs", "UserSession.cs"]),
        ("C5", "feat(tax): заокруглення копійок", ["TaxCalculator.cs", "InvoicePdf.cs"]),
    ]

    for i, (cid, desc, files) in enumerate(commits):
        cy = ly + 65 + i * 64
        frags.append(rect(lx + 20, cy, 50, 48, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
        frags.append(text(lx + 45, cy + 28, cid, size=13, bold=True, color=NEG))

        frags.append(text(lx + 85, cy + 18, desc, size=12, bold=True, anchor="start", color=INK))
        file_str = " + ".join(files)
        frags.append(text(lx + 85, cy + 38, file_str, size=11, anchor="start", color="#475569"))

    # ── ПРАВА ЧАСТИНА: Матриця та розраховані метрики
    rx, ry, rw, rh = 510, 30, 420, 400
    frags.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=12))
    frags.append(text(rx + rw / 2, ry + 28, "Матриця та метрики еволюційного зачеплення", size=14, bold=True, color=INK))

    # Таблиця метрик для ключових пар
    headers = ["Пара файлів", "Support", "Confidence", "Висновки"]
    col_x = [rx + 20, rx + 175, rx + 245, rx + 325]

    frags.append(rect(rx + 15, ry + 50, rw - 30, 28, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(col_x[0] + 50, ry + 68, headers[0], size=11, bold=True, color=INK))
    frags.append(text(col_x[1] + 25, ry + 68, headers[1], size=11, bold=True, color=INK))
    frags.append(text(col_x[2] + 30, ry + 68, headers[2], size=11, bold=True, color=INK))
    frags.append(text(col_x[3] + 40, ry + 68, headers[3], size=11, bold=True, color=INK))

    rows = [
        ("TaxCalc ↔ InvoicePdf", "3 / 5 (60%)", "100%", "Критичне зачеплення", POS),
        ("AuthToken ↔ UserSession", "2 / 5 (40%)", "100%", "Тісна зв'язка", POS),
        ("TaxCalc ↔ AuditLog", "1 / 5 (20%)", "33%", "Випадковий збіг", FIELD),
    ]

    for i, (pair, sup, conf, concl, col) in enumerate(rows):
        r_y = ry + 86 + i * 56
        frags.append(rect(rx + 15, r_y, rw - 30, 48, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
        frags.append(text(col_x[0], r_y + 28, pair, size=11, bold=True, anchor="start", color=INK))
        frags.append(text(col_x[1] + 25, r_y + 28, sup, size=11, color=INK))
        frags.append(text(col_x[2] + 30, r_y + 28, conf, size=11, bold=True, color=col))
        frags.append(text(col_x[3] + 40, r_y + 28, concl, size=11, color=col))

    # Нижній висновок
    frags.append(rect(rx + 20, ry + 275, rw - 40, 105, fill="#fef2f2", stroke=POS, sw=1.2, rx=8))
    frags.append(text(rx + rw / 2, ry + 300, "Правило виявлення прихованого зв'язку:", size=12, bold=True, color=POS))
    frags.append(text(rx + rw / 2, ry + 324, "Якщо Confidence(A → B) ≥ 75% та Support ≥ 3,", size=11, color=INK))
    frags.append(text(rx + rw / 2, ry + 344, "модулі ділять спільне знання поза контрактом", size=11, color=INK))
    frags.append(text(rx + rw / 2, ry + 364, "і потребують архітектурного рефакторингу.", size=11, bold=True, color=POS))

    render(os.path.join(IMG, 'co-change-matrix.svg'), W, H, *frags,
           title="Хронологія комітів і матриця спільних змін")


# ── Фігура 3: Стратегії розв'язання логічного зачеплення ───────────────────────
def fig_decoupling_strategies():
    W, H = 960, 470
    frags = []

    frags.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff", sw=0))

    # Стовпчик 1: Розірване знання (Проблема)
    c1_x, c1_y, cw, ch = 30, 30, 280, 410
    frags.append(rect(c1_x, c1_y, cw, ch, fill="#fffaf9", stroke="#fed7aa", sw=1.5, rx=10))
    frags.append(text(c1_x + cw / 2, c1_y + 30, "1. Стан проблеми", size=15, bold=True, color=POS))
    frags.append(text(c1_x + cw / 2, c1_y + 50, "Неявні дублікати логіки", size=11, color=MUTED))

    box1_a, _, _ = textbox(c1_x + cw / 2, c1_y + 110, "Модуль A\n(Валідація знижки)", size=12, pad=10,
                           fill="#ffffff", stroke=POS, sw=1.5, min_w=220)
    box1_b, _, _ = textbox(c1_x + cw / 2, c1_y + 210, "Модуль B\n(Дзеркальна валідація)", size=12, pad=10,
                           fill="#ffffff", stroke=POS, sw=1.5, min_w=220)
    frags.append(box1_a)
    frags.append(box1_b)
    frags.append(arrow(c1_x + cw / 2, c1_y + 140, c1_x + cw / 2, c1_y + 180, color=POS, sw=1.8))
    frags.append(text(c1_x + cw / 2 + 55, c1_y + 163, "co-change", size=10, bold=True, color=POS))

    frags.append(rect(c1_x + 15, c1_y + 290, cw - 30, 95, fill="#ffffff", stroke="#fed7aa", sw=1.2, rx=6))
    frags.append(text(c1_x + cw / 2, c1_y + 314, "Симптом: Shotgun Surgery", size=12, bold=True, color=POS))
    frags.append(text(c1_x + cw / 2, c1_y + 338, "Зміна бізнес-правила", size=11, color=INK))
    frags.append(text(c1_x + cw / 2, c1_y + 356, "вимагає правок у 2+ місцях", size=11, color=INK))

    # Стовпчик 2: Стратегія Schema-First / Спільний контракт
    c2_x, c2_y = 340, 30
    frags.append(rect(c2_x, c2_y, cw, ch, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=10))
    frags.append(text(c2_x + cw / 2, c2_y + 30, "2. Єдине джерело правди", size=15, bold=True, color=FIELD))
    frags.append(text(c2_x + cw / 2, c2_y + 50, "Schema-First / Контракт", size=11, color=MUTED))

    box2_schema, _, _ = textbox(c2_x + cw / 2, c2_y + 110, "Схема / Спільна модель\n(OpenAPI / Protobuf / DTO)", size=12, pad=10,
                                fill="#ffffff", stroke=FIELD, sw=2, min_w=240)
    box2_a, _, _ = textbox(c2_x + 70, c2_y + 220, "Клієнт A", size=12, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.5, min_w=100)
    box2_b, _, _ = textbox(c2_x + 210, c2_y + 220, "Клієнт B", size=12, pad=10, fill="#ffffff", stroke="#94a3b8", sw=1.5, min_w=100)
    frags.append(box2_schema)
    frags.append(box2_a)
    frags.append(box2_b)
    frags.append(arrow(c2_x + cw / 2 - 30, c2_y + 140, c2_x + 70, c2_y + 195, color=FIELD, sw=1.8))
    frags.append(arrow(c2_x + cw / 2 + 30, c2_y + 140, c2_x + 210, c2_y + 195, color=FIELD, sw=1.8))

    frags.append(rect(c2_x + 15, c2_y + 290, cw - 30, 95, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(c2_x + cw / 2, c2_y + 314, "Результат: Кодогенерація", size=12, bold=True, color=FIELD))
    frags.append(text(c2_x + cw / 2, c2_y + 338, "Приховане зачеплення", size=11, color=INK))
    frags.append(text(c2_x + cw / 2, c2_y + 356, "стало явним типізованим контрактом", size=11, color=INK))

    # Стовпчик 3: Стратегія CCP / Консолідація концепту
    c3_x, c3_y = 650, 30
    frags.append(rect(c3_x, c3_y, cw, ch, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=10))
    frags.append(text(c3_x + cw / 2, c3_y + 30, "3. Спільне закриття (CCP)", size=15, bold=True, color=NEG))
    frags.append(text(c3_x + cw / 2, c3_y + 50, "Інкапсуляція в один модуль", size=11, color=MUTED))

    # Об'єднаний контейнер
    frags.append(rect(c3_x + 20, c3_y + 85, cw - 40, 160, fill="#ffffff", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(c3_x + cw / 2, c3_y + 110, "Єдиний модуль домену", size=13, bold=True, color=NEG))
    box3_in, _, _ = textbox(c3_x + cw / 2, c3_y + 175, "Інкапсульоване правило\n(розрахунок + валідація)", size=12, pad=10,
                            fill="#eff6ff", stroke="#3b82f6", sw=1.5, min_w=200)
    frags.append(box3_in)

    frags.append(rect(c3_x + 15, c3_y + 290, cw - 30, 95, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=6))
    frags.append(text(c3_x + cw / 2, c3_y + 314, "Результат: Локальність змін", size=12, bold=True, color=NEG))
    frags.append(text(c3_x + cw / 2, c3_y + 338, "Те, що змінюється разом,", size=11, color=INK))
    frags.append(text(c3_x + cw / 2, c3_y + 356, "живе в одному модулі", size=11, color=INK))

    render(os.path.join(IMG, 'decoupling-strategies.svg'), W, H, *frags,
           title="Стратегії розв'язання логічного зачеплення")


if __name__ == "__main__":
    fig_logical_vs_structural()
    fig_co_change_matrix()
    fig_decoupling_strategies()
    print("All figures generated successfully in", IMG)
