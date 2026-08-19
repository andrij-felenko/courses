# -*- coding: utf-8 -*-
"""Фігури до статті «Синфазний дросель» (book/electronics/components/common-mode-choke).
Генерує векторні SVG-ілюстрації у ./img/ за допомогою svgkit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (text, mtext, rect, line, render, INK, MUTED, POS, NEG,
                    FIELD, FILL, BG)  # noqa: E402

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CORECOL = "#374151"   # темно-сірий ферит
COPPER1 = "#b45309"   # мідь обмотки 1
COPPER2 = "#d97706"   # мідь обмотки 2
FLUXCOL = "#059669"   # зелений магнітний потік
PANELBG = "#f8fafc"


def fig_mode_cancellation():
    """Фігура 1: Компенсація потоків у диференційному ладі проти підсумовування у синфазному."""
    W, H = 860, 440
    frags = []

    # Тло панелей
    frags.append(rect(20, 20, 395, 400, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(rect(445, 20, 395, 400, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))

    # ── ЛІВА ПАНЕЛЬ: Диференційний лад (DM) ──
    frags.append(text(217.5, 48, "Диференційний лад (DM)", size=15, color=NEG, bold=True))
    frags.append(text(217.5, 68, "Корисний струм петлі: I₁ = −I₂ = I_dm", size=12, color=INK))

    # Тороїдне осердя (ліве)
    cx1, cy1 = 217.5, 175.0
    frags.append('<circle cx="%.1f" cy="%.1f" r="70" fill="none" stroke="%s" stroke-width="26"/>' % (cx1, cy1, CORECOL))
    frags.append('<circle cx="%.1f" cy="%.1f" r="70" fill="none" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="4,4"/>' % (cx1, cy1))

    # Обмотка 1 (верхня половина, вхід зліва, вихід справа)
    frags.append('<path d="M 110,135 L 170,135 A 55 55 0 0 1 265,135 L 325,135" fill="none" stroke="%s" stroke-width="3.5"/>' % COPPER1)
    frags.append(text(125, 125, "I_dm →", size=12, color=NEG, bold=True))
    frags.append(text(305, 125, "→ I_dm", size=12, color=NEG, bold=True))

    # Обмотка 2 (нижня половина, вхід справа, вихід зліва)
    frags.append('<path d="M 325,215 L 265,215 A 55 55 0 0 1 170,215 L 110,215" fill="none" stroke="%s" stroke-width="3.5"/>' % COPPER2)
    frags.append(text(305, 235, "← I_dm", size=12, color=NEG, bold=True))
    frags.append(text(125, 235, "I_dm ←", size=12, color=NEG, bold=True))

    # Потоки (гасяться)
    frags.append(text(217.5, 145, "Φ₁ (за годинниковою)", size=11, color=FIELD, bold=True))
    frags.append(text(217.5, 205, "Φ₂ (проти годинникової)", size=11, color=POS, bold=True))
    frags.append('<circle cx="%.1f" cy="%.1f" r="16" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % (cx1, cy1, MUTED))
    frags.append(text(cx1, cy1 + 5, "Φ=0", size=11, color=INK, bold=True))

    # Підсумок лівої панелі
    frags.append(rect(35, 280, 365, 125, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(mtext(217.5, 305, [
        "Магнітні потоки зустрічні: Φ_net = Φ₁ − Φ₂ = 0",
        "• Осердя НЕ намагнічується (B ≈ 0)",
        "• L_dm ≈ L_leak (мізерна індуктивність розсіювання)",
        "• Корисний сигнал проходить майже без втрат",
        "• Робочий струм НЕ насичує магнітопровід"
    ], size=11.5, color=INK, lh=1.35))

    # ── ПРАВА ПАНЕЛЬ: Синфазний лад (CM) ──
    frags.append(text(642.5, 48, "Синфазний лад (CM)", size=15, color=POS, bold=True))
    frags.append(text(642.5, 68, "Завада в один бік: I₁ = I₂ = I_cm / 2", size=12, color=INK))

    # Тороїдне осердя (праве)
    cx2, cy2 = 642.5, 175.0
    frags.append('<circle cx="%.1f" cy="%.1f" r="70" fill="none" stroke="%s" stroke-width="26"/>' % (cx2, cy2, CORECOL))
    frags.append('<circle cx="%.1f" cy="%.1f" r="70" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4"/>' % (cx2, cy2, FIELD))

    # Обмотка 1 (верхня, вхід зліва)
    frags.append('<path d="M 535,135 L 595,135 A 55 55 0 0 1 690,135 L 750,135" fill="none" stroke="%s" stroke-width="3.5"/>' % COPPER1)
    frags.append(text(550, 125, "I_cm/2 →", size=12, color=POS, bold=True))
    frags.append(text(730, 125, "→ I_cm/2", size=12, color=POS, bold=True))

    # Обмотка 2 (нижня, вхід зліва!)
    frags.append('<path d="M 535,215 L 595,215 A 55 55 0 0 0 690,215 L 750,215" fill="none" stroke="%s" stroke-width="3.5"/>' % COPPER2)
    frags.append(text(550, 235, "I_cm/2 →", size=12, color=POS, bold=True))
    frags.append(text(730, 235, "→ I_cm/2", size=12, color=POS, bold=True))

    # Потоки (додаються)
    frags.append(text(642.5, 145, "Φ₁ (за годинниковою)", size=11, color=FIELD, bold=True))
    frags.append(text(642.5, 205, "Φ₂ (за годинниковою)", size=11, color=FIELD, bold=True))
    frags.append('<circle cx="%.1f" cy="%.1f" r="18" fill="#ffffff" stroke="%s" stroke-width="1.5"/>' % (cx2, cy2, FIELD))
    frags.append(text(cx2, cy2 + 5, "Φ=2Φ₁", size=11, color=FIELD, bold=True))

    # Підсумок правої панелі
    frags.append(rect(460, 280, 365, 125, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(mtext(642.5, 305, [
        "Магнітні потоки сумуються: Φ_net = Φ₁ + Φ₂ = 2Φ",
        "• Осердя відчуває повний сумарний потік",
        "• L_cm = 2·(L + M) ≈ 4·L_витка (величезна індуктивність)",
        "• Блокуючий опір Z_cm = 2πf L_cm душитиме шум",
        "• Завада відбивається назад або розсіюється в тепло"
    ], size=11.5, color=INK, lh=1.35))

    render(os.path.join(IMG, "mode-flux-cancellation.svg"), W, H, *frags,
           title="Компенсація потоків у диференційному ладі проти підсумовування у синфазному")


def fig_winding_topologies():
    """Фігура 2: Топології намотки — біфілярна проти секційної."""
    W, H = 860, 420
    frags = []

    frags.append(rect(20, 20, 395, 380, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(rect(445, 20, 395, 380, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))

    # ── ЛІВА: Біфілярна ──
    frags.append(text(217.5, 48, "Біфілярна намотка (Bifilar)", size=15, color=INK, bold=True))
    frags.append(text(217.5, 68, "Паралельне / скручене намотування пари разом", size=11.5, color=MUTED))

    # Рисунок тороїда з біфілярною парою
    cx1, cy1 = 217.5, 160.0
    frags.append('<circle cx="%.1f" cy="%.1f" r="62" fill="none" stroke="%s" stroke-width="22"/>' % (cx1, cy1, CORECOL))
    # Витки біфілярні навколо кільця
    for ang in range(0, 360, 45):
        rad = ang * 3.14159 / 180.0
        import math
        px = cx1 + 62 * math.cos(rad)
        py = cy1 + 62 * math.sin(rad)
        frags.append('<circle cx="%.1f" cy="%.1f" r="6.5" fill="%s" stroke="#ffffff" stroke-width="1"/>' % (px - 3, py - 3, COPPER1))
        frags.append('<circle cx="%.1f" cy="%.1f" r="6.5" fill="%s" stroke="#ffffff" stroke-width="1"/>' % (px + 3, py + 3, COPPER2))

    frags.append(rect(35, 245, 365, 140, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(mtext(217.5, 268, [
        "Властивості та компроміси:",
        "• Магнітний зв'язок k ≈ 0.999 ... 0.9999 (майже ідеальний)",
        "• Мінімальна L_leak (< 0.5% L_cm) — не псує швидкі фронти",
        "• Підвищена міжобмоткова ємність C_ww (20 ... 60 пФ)",
        "• Обмежена ізоляція між проводами (≤ 500 ... 1000 В)",
        "Застосування: USB 2.0/3.x, CAN FD, Ethernet, HDMI, LVDS"
    ], size=11.5, color=INK, lh=1.32))

    # ── ПРАВА: Секційна (секторна) ──
    frags.append(text(642.5, 48, "Секційна / секторна намотка", size=15, color=INK, bold=True))
    frags.append(text(642.5, 68, "Роздільні сектори з ізоляційним бар'єром", size=11.5, color=MUTED))

    # Рисунок тороїда з двома секторами
    cx2, cy2 = 642.5, 160.0
    frags.append('<circle cx="%.1f" cy="%.1f" r="62" fill="none" stroke="%s" stroke-width="22"/>' % (cx2, cy2, CORECOL))
    # Бар'єр зверху й знизу
    frags.append(rect(cx2 - 5, cy2 - 80, 10, 36, fill="#ef4444", stroke="#b91c1c", sw=1))
    frags.append(rect(cx2 - 5, cy2 + 44, 10, 36, fill="#ef4444", stroke="#b91c1c", sw=1))
    frags.append(text(cx2, cy2 - 2, "Бар'єр", size=10, color=POS, bold=True))

    # Лівий сектор — обмотка 1
    for ang in [135, 165, 195, 225]:
        import math
        rad = ang * 3.14159 / 180.0
        px = cx2 + 62 * math.cos(rad)
        py = cy2 + 62 * math.sin(rad)
        frags.append('<circle cx="%.1f" cy="%.1f" r="7.5" fill="%s" stroke="#ffffff" stroke-width="1.2"/>' % (px, py, COPPER1))

    # Правий сектор — обмотка 2
    for ang in [315, 345, 15, 45]:
        import math
        rad = ang * 3.14159 / 180.0
        px = cx2 + 62 * math.cos(rad)
        py = cy2 + 62 * math.sin(rad)
        frags.append('<circle cx="%.1f" cy="%.1f" r="7.5" fill="%s" stroke="#ffffff" stroke-width="1.2"/>' % (px, py, COPPER2))

    frags.append(rect(460, 245, 365, 140, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(mtext(642.5, 268, [
        "Властивості та компроміси:",
        "• Висока діелектрична ізоляція (1.5 ... 4.0 кВ AC/DC)",
        "• Дуже мала міжобмоткова ємність C_ww (< 1 ... 3 пФ)",
        "• Помітна L_leak (1 ... 3% L_cm) через рознесення витків",
        "• L_leak працює як вбудований диференціальний фільтр",
        "Застосування: мережеві фільтри живлення AC-DC (L-N 230 В)"
    ], size=11.5, color=INK, lh=1.32))

    render(os.path.join(IMG, "winding-topologies.svg"), W, H, *frags,
           title="Топології намотки синфазного дроселя: біфілярна проти секційної")


def fig_cmc_impedance_frequency():
    """Фігура 3: Крива імпедансу |Z_cm| та |Z_dm| від частоти."""
    W, H = 860, 450
    frags = []

    frags.append(rect(20, 20, 820, 410, fill=BG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(430, 48, "Частотна характеристика імпедансу синфазного дроселя", size=16, color=INK, bold=True))

    # Осі координат
    # X: 100 .. 760 (частота 10 кГц .. 1 ГГц: 5 декад)
    # Y: 340 .. 90 (імпеданс 0.1 Ом .. 100 кОм: 6 декад)
    ox, oy = 110.0, 350.0
    w_axis = 650.0
    h_axis = 250.0

    frags.append(line(ox, oy, ox + w_axis, oy, INK, 1.8))
    frags.append(line(ox, oy, ox, oy - h_axis, INK, 1.8))

    # Позначки осі X (log частоти: 10k, 100k, 1M, 10M, 100M, 1G)
    freqs = [("10 кГц", 0), ("100 кГц", 130), ("1 МГц", 260), ("10 МГц", 390), ("100 МГц", 520), ("1 ГГц", 650)]
    for lbl, dx in freqs:
        x = ox + dx
        frags.append(line(x, oy, x, oy + 6, INK, 1.2))
        frags.append(line(x, oy, x, oy - h_axis, "#e5e7eb", 1, dash="3,3"))
        frags.append(text(x, oy + 22, lbl, size=11, color=MUTED))
    frags.append(text(ox + w_axis - 10, oy + 36, "Частота f →", size=12, color=INK, bold=True, anchor="end"))

    # Позначки осі Y (log імпедансу: 1 Ом, 10 Ом, 100 Ом, 1 кОм, 10 кОм)
    z_marks = [("1 Ом", 0), ("10 Ом", 60), ("100 Ом", 120), ("1 кОм", 180), ("10 кОм", 240)]
    for lbl, dy in z_marks:
        y = oy - dy
        frags.append(line(ox - 6, y, ox, y, INK, 1.2))
        frags.append(line(ox, y, ox + w_axis, y, "#e5e7eb", 1, dash="3,3"))
        frags.append(text(ox - 10, y + 4, lbl, size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, oy - h_axis - 10, "|Z| (Ом) ↑", size=12, color=INK, bold=True, anchor="end"))

    # Крива Z_cm (зелена, висока: індуктивна зона -> горб SRF -> ємнісний спад)
    # Шлях: (110, 320) -> (370, 120) -> (500, 110) [SRF пік біля 10-30 МГц] -> (760, 260)
    frags.append('<path d="M 110,310 C 220,250 380,120 480,115 C 520,113 560,130 630,200 C 700,260 740,290 760,305" '
                 'fill="none" stroke="%s" stroke-width="3.5"/>' % FIELD)
    frags.append(text(460, 95, "|Z_cm| Синфазний імпеданс", size=13, color=FIELD, bold=True))

    # Крива Z_dm (синя, низька: прозора в робочій смузі, повільно росте на leakage)
    # Шлях: (110, 345) -> (370, 340) -> (500, 310) -> (760, 230)
    frags.append('<path d="M 110,345 C 260,345 420,335 500,310 C 580,285 680,245 760,225" '
                 'fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,3"/>' % NEG)
    frags.append(text(680, 210, "|Z_dm| (через L_leak)", size=12, color=NEG, bold=True))

    # Анотаційні рамки
    # Резонансний пік SRF
    frags.append('<circle cx="490" cy="114" r="5" fill="%s"/>' % POS)
    frags.append(text(490, 80, "SRF_cm", size=12, color=POS, bold=True))

    frags.append(rect(125, 130, 105, 75, fill=FILL, stroke=MUTED, sw=1, rx=5))
    frags.append(mtext(177.5, 148, [
        "Індуктивна зона:",
        "|Z_cm| ≈ 2πf L_cm",
        "Опір росте з f"
    ], size=10.5, color=INK, lh=1.3))

    frags.append(rect(645, 95, 105, 75, fill=FILL, stroke=MUTED, sw=1, rx=5))
    frags.append(mtext(697.5, 113, [
        "Ємнісна зона:",
        "f > SRF",
        "Спад 1/(2πf C_par)"
    ], size=10.5, color=POS, lh=1.3))

    render(os.path.join(IMG, "cmc-impedance-frequency.svg"), W, H, *frags,
           title="Частотна характеристика синфазного дроселя: Z_cm та Z_dm")


def fig_mains_filter_topology():
    """Фігура 4: Схема мережевого фільтра (CMC + X/Y конденсатори)."""
    W, H = 860, 440
    frags = []

    frags.append(rect(20, 20, 820, 400, fill=BG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(430, 48, "Топологія мережевого EMC-фільтра живлення з синфазним дроселем", size=16, color=INK, bold=True))

    # Мережеві лінії: L (Line, y=140), N (Neutral, y=280), PE (Earth, y=370)
    # Вхід (AC Mains) зліва (x=60), Вихід (SMPS) справа (x=780)

    # Лінії живлення
    frags.append(line(60, 140, 800, 140, POS, 2.5))  # L
    frags.append(line(60, 280, 800, 280, NEG, 2.5))  # N
    frags.append(line(60, 380, 800, 380, FIELD, 2, dash="6,4"))  # PE

    frags.append(text(75, 125, "L (Фаза 230 В)", size=12, color=POS, bold=True, anchor="start"))
    frags.append(text(75, 265, "N (Нейтраль)", size=12, color=NEG, bold=True, anchor="start"))
    frags.append(text(75, 402, "PE (Захисне заземлення / шасі)", size=12, color=FIELD, bold=True, anchor="start"))

    # Вхідний X-конденсатор C_X1 (x=190)
    frags.append(line(190, 140, 190, 190, INK, 1.8))
    frags.append(line(190, 230, 190, 280, INK, 1.8))
    frags.append(rect(170, 190, 40, 40, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(190, 214, "C_X1", size=11, color=INK, bold=True))
    frags.append(text(190, 248, "DM-фільтр", size=10, color=MUTED))

    # Розрядний резистор R_bleed (x=270)
    frags.append(line(270, 140, 270, 190, INK, 1.8))
    frags.append(line(270, 230, 270, 280, INK, 1.8))
    frags.append(rect(255, 190, 30, 40, fill=FILL, stroke=INK, sw=1.5))
    frags.append(text(270, 214, "R_bl", size=10, color=INK, bold=True))

    # Синфазний дросель CMC (x=370 .. 490)
    frags.append(rect(350, 100, 160, 220, fill="#f1f5f9", stroke=CORECOL, sw=2, rx=6))
    frags.append(text(430, 122, "Синфазний дросель", size=12, color=CORECOL, bold=True))

    # Обмотка 1 на L (x=370..490, y=140)
    # Зображення індуктивності: 3 півкола
    for i in range(3):
        frags.append('<path d="M %d,140 A 15 15 0 0 1 %d,140" fill="none" stroke="%s" stroke-width="3"/>' % (385 + i * 30, 415 + i * 30, COPPER1))
    frags.append(text(430, 162, "L_cm (обмотка 1)", size=10.5, color=COPPER1, bold=True))

    # Осердя посередині
    frags.append(line(375, 205, 485, 205, CORECOL, 3))
    frags.append(line(375, 213, 485, 213, CORECOL, 3))

    # Обмотка 2 на N (x=370..490, y=280)
    for i in range(3):
        frags.append('<path d="M %d,280 A 15 15 0 0 1 %d,280" fill="none" stroke="%s" stroke-width="3"/>' % (385 + i * 30, 415 + i * 30, COPPER2))
    frags.append(text(430, 305, "L_cm (обмотка 2)", size=10.5, color=COPPER2, bold=True))

    # Вихідний X-конденсатор C_X2 (x=570)
    frags.append(line(570, 140, 570, 190, INK, 1.8))
    frags.append(line(570, 230, 570, 280, INK, 1.8))
    frags.append(rect(550, 190, 40, 40, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(570, 214, "C_X2", size=11, color=INK, bold=True))

    # Y-конденсатори C_Y1 (L -> PE) та C_Y2 (N -> PE) на x=680
    frags.append(line(680, 140, 680, 220, INK, 1.8))
    frags.append(rect(660, 165, 40, 35, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    frags.append(text(680, 187, "C_Y1", size=10.5, color=NEG, bold=True))

    frags.append(line(680, 280, 680, 380, INK, 1.8))
    frags.append(rect(660, 310, 40, 35, fill="#dbeafe", stroke="#2563eb", sw=1.5))
    frags.append(text(680, 332, "C_Y2", size=10.5, color=NEG, bold=True))

    frags.append(line(680, 200, 680, 380, INK, 1.8))
    frags.append('<circle cx="680" cy="380" r="4" fill="%s"/>' % FIELD)
    frags.append(text(715, 365, "CM-стік на PE", size=10.5, color=FIELD, bold=True))

    # Стрілки призначення
    frags.append(text(775, 125, "До джерела SMPS →", size=11, color=POS, bold=True, anchor="end"))
    frags.append(text(775, 265, "До джерела SMPS →", size=11, color=NEG, bold=True, anchor="end"))

    render(os.path.join(IMG, "mains-filter-topology.svg"), W, H, *frags,
           title="Повна топологія вхідного мережевого EMC-фільтра")


def fig_dc_bias_saturation():
    """Фігура 5: Насичення осердя під дією струмового дисбалансу або постійного зміщення."""
    W, H = 860, 430
    frags = []

    frags.append(rect(20, 20, 395, 390, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))
    frags.append(rect(445, 20, 395, 390, fill=PANELBG, stroke=MUTED, sw=1.5, rx=8))

    # ── ЛІВА ПАНЕЛЬ: Збалансований струм навантаження ──
    frags.append(text(217.5, 48, "Збалансований струм (I_dm)", size=15, color=NEG, bold=True))
    frags.append(text(217.5, 68, "I₁ = I₂, струми рівні та протилежні", size=11.5, color=MUTED))

    # Графік B-H петлі
    ox1, oy1 = 217.5, 175.0
    frags.append(line(ox1 - 130, oy1, ox1 + 130, oy1, INK, 1.2))  # H вісь
    frags.append(line(ox1, oy1 + 80, ox1, oy1 - 80, INK, 1.2))    # B вісь
    frags.append(text(ox1 + 135, oy1 + 4, "H →", size=10, color=MUTED, anchor="start"))
    frags.append(text(ox1, oy1 - 88, "B ↑", size=10, color=MUTED, anchor="middle"))

    # Петля B-H високої проникності в центрі (0,0)
    frags.append('<path d="M 180,225 C 190,195 210,135 255,125 C 245,155 225,215 180,225" '
                 'fill="#dcfce7" stroke="%s" stroke-width="2"/>' % FIELD)
    frags.append('<circle cx="%.1f" cy="%.1f" r="6" fill="%s"/>' % (ox1, oy1, FIELD))
    frags.append(text(ox1 + 8, oy1 - 12, "Робоча точка (0,0)", size=11, color=FIELD, bold=True, anchor="start"))

    frags.append(rect(35, 265, 365, 130, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(mtext(217.5, 286, [
        "Стан магнітної системи:",
        "• Потоки від струму навантаження взаємно скомпенсовані",
        "• H_net = 0, робоча точка сидить точно в нулі",
        "• Осердя зберігає максимальну проникність μ_r ≈ 10 000",
        "• Дросель ефективно душить завади навіть при 10–30 А струму"
    ], size=11.5, color=INK, lh=1.32))

    # ── ПРАВА ПАНЕЛЬ: Асиметрія або синфазний струм зміщення ──
    frags.append(text(642.5, 48, "Незбалансований струм (ΔI або I_cm)", size=15, color=POS, bold=True))
    frags.append(text(642.5, 68, "I₁ ≠ I₂ (витік на землю / асиметрія лінії)", size=11.5, color=MUTED))

    # Графік B-H зі зсувом у насичення
    ox2, oy2 = 642.5, 175.0
    frags.append(line(ox2 - 130, oy2, ox2 + 130, oy2, INK, 1.2))  # H вісь
    frags.append(line(ox2, oy2 + 80, ox2, oy2 - 80, INK, 1.2))    # B вісь
    frags.append(text(ox2 + 135, oy2 + 4, "H →", size=10, color=MUTED, anchor="start"))
    frags.append(text(ox2, oy2 - 88, "B ↑", size=10, color=MUTED, anchor="middle"))

    # Крива насичення: зсув у правий верхній кут
    frags.append('<path d="M 540,240 C 600,230 630,190 660,130 L 750,118" '
                 'fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    # Зсунута робоча точка на ділянці насичення
    frags.append('<circle cx="710" cy="122" r="6" fill="%s"/>' % POS)
    frags.append(line(ox2, oy2, 710, oy2, POS, 1.5, dash="3,3"))
    frags.append(line(710, oy2, 710, 122, POS, 1.5, dash="3,3"))
    frags.append(text(710, 105, "Насичення! B ≈ B_sat", size=11, color=POS, bold=True))
    frags.append(text(675, oy2 + 16, "H_bias = N·ΔI / l_e", size=10.5, color=POS))

    frags.append(rect(460, 265, 365, 130, fill=FILL, stroke=MUTED, sw=1, rx=6))
    frags.append(mtext(642.5, 286, [
        "Катастрофічна втрата фільтрації:",
        "• Нескомпенсований струм ΔI зміщує осердя в область B_sat",
        "• Диференційна проникність падає: μ_r від 10 000 → 15 ... 30",
        "• Синфазна індуктивність L_cm обвалюється на 99%",
        "• Дросель стає прозорим для завад — пристрій не проходить EMC"
    ], size=11.5, color=INK, lh=1.32))

    render(os.path.join(IMG, "dc-bias-saturation.svg"), W, H, *frags,
           title="Насичення осердя синфазного дроселя при струмовому дисбалансі")


if __name__ == "__main__":
    fig_mode_cancellation()
    fig_winding_topologies()
    fig_cmc_impedance_frequency()
    fig_mains_filter_topology()
    fig_dc_bias_saturation()
    print("All 5 common-mode choke figures successfully written to ./img/")
