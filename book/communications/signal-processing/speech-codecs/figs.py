# -*- coding: utf-8 -*-
"""Фігури до теми «Мовний кодек: G.711, G.729, Opus».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль та помічники — зі спільного svgkit.
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

BORDER = "#cbd5e1"


# ── 1. g711-companding-curve.svg ──────────────────────────────────────────────
def fig_g711_companding_curve():
    W, H = 780, 400
    path = os.path.join(IMG, 'g711-companding-curve.svg')
    f = []

    f.append(rect(0, 0, W, H, fill=BG))

    # Рамка графіка
    x0, y0 = 90, 340
    w_chart, h_chart = 340, 280

    # Осі координат
    f.append(line(x0, y0, x0 + w_chart + 20, y0, color=INK, sw=1.5))
    f.append(line(x0, y0, x0, y0 - h_chart - 20, color=INK, sw=1.5))
    f.append(text(x0 + w_chart + 25, y0 + 18, "Вхідний сигнал x (вхід PCM)", size=11, color=INK, anchor="end"))
    f.append(text(x0 - 10, y0 - h_chart - 25, "Стиснута амплітуда y", size=11, color=INK, anchor="start"))

    # Сітка та мітки
    for val in [0.25, 0.5, 0.75, 1.0]:
        px = x0 + val * w_chart
        py = y0 - val * h_chart
        f.append(line(px, y0, px, y0 - h_chart, color=MUTED, sw=0.8, dash="3,3"))
        f.append(line(x0, py, x0 + w_chart, py, color=MUTED, sw=0.8, dash="3,3"))
        f.append(text(px, y0 + 16, f"{val:.2f}", size=10, color=MUTED))
        f.append(text(x0 - 8, py + 4, f"{val:.2f}", size=10, color=MUTED, anchor="end"))

    # Лінійна крива (без компандування)
    f.append(line(x0, y0, x0 + w_chart, y0 - h_chart, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(x0 + 220, y0 - 190, "Лінійне (без стиснення)", size=11, color=MUTED, anchor="start"))

    # Крива A-law: y = (1 + ln(A*x)) / (1 + ln(A)) for x > 1/A, else A*x / (1 + ln(A))
    A = 87.6
    lnA_1 = 1.0 + math.log(A)

    def alaw(x):
        if x <= 0:
            return 0.0
        if x < 1.0 / A:
            return (A * x) / lnA_1
        return (1.0 + math.log(A * x)) / lnA_1

    pts_alaw = []
    N = 100
    for i in range(N + 1):
        x = i / float(N)
        y = alaw(x)
        px = x0 + x * w_chart
        py = y0 - y * h_chart
        pts_alaw.append((px, py))

    poly_alaw = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts_alaw)
    f.append(f'<polyline points="{poly_alaw}" fill="none" stroke="{POS}" stroke-width="2.8"/>')

    # Крива mu-law: y = ln(1 + mu*x) / ln(1 + mu)
    mu = 255.0
    ln_mu1 = math.log(1.0 + mu)

    def mulaw(x):
        if x <= 0:
            return 0.0
        return math.log(1.0 + mu * x) / ln_mu1

    pts_mulaw = []
    for i in range(N + 1):
        x = i / float(N)
        y = mulaw(x)
        px = x0 + x * w_chart
        py = y0 - y * h_chart
        pts_mulaw.append((px, py))

    poly_mulaw = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts_mulaw)
    f.append(f'<polyline points="{poly_mulaw}" fill="none" stroke="{NEG}" stroke-width="2.2" stroke-dasharray="6,3"/>')

    # Інформаційна панель праворуч
    px_info = 470
    py_info = 50
    f.append(rect(px_info, py_info, 290, 290, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(px_info + 145, py_info + 25, "Принцип компандування G.711", size=13, bold=True, color=INK))

    # Легенда
    f.append(line(px_info + 20, py_info + 55, px_info + 60, py_info + 55, color=POS, sw=3))
    f.append(text(px_info + 70, py_info + 59, "A-law (Європа / ITU-T)", size=11, color=INK, anchor="start", bold=True))

    f.append(line(px_info + 20, py_info + 80, px_info + 60, py_info + 80, color=NEG, sw=2.5, dash="6,3"))
    f.append(text(px_info + 70, py_info + 84, "µ-law (США / Японія)", size=11, color=INK, anchor="start", bold=True))

    f.append(line(px_info + 20, py_info + 105, px_info + 60, py_info + 105, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(px_info + 70, py_info + 109, "Лінійний PCM (13/14 біт)", size=11, color=MUTED, anchor="start"))

    # Пояснення характеристик
    f.append(line(px_info + 15, py_info + 125, px_info + 275, py_info + 125, color=BORDER, sw=1))

    desc_lines = [
        "• Дрібні амплітуди (тихий звук):",
        "  крутий нахил -> висока роздільність",
        "• Великі амплітуди (гучний звук):",
        "  пологий нахил -> грубе квантування",
        "• Динамічний діапазон: ~72 дБ",
        "• Вхід: 13-14 біт -> Вихід: 8 біт PCM",
        "• Частота дискретизації: 8000 Гц",
        "• Потік даних: 64 кбіт/с (сталий)"
    ]
    for idx, dline in enumerate(desc_lines):
        f.append(text(px_info + 20, py_info + 148 + idx * 16, dline, size=10, color=INK, anchor="start"))

    render(path, W, H, *f)
    print(f"Generated {path}")


# ── 2. g729-acelp-pipeline.svg ────────────────────────────────────────────────
def fig_g729_acelp_pipeline():
    W, H = 800, 420
    path = os.path.join(IMG, 'g729-acelp-pipeline.svg')
    f = []

    f.append(rect(0, 0, W, H, fill=BG))

    # Заголовок
    f.append(text(W / 2, 25, "Кодер G.729 CS-ACELP: Модель аналізу через синтез (AbS)", size=14, bold=True, color=INK))

    # Блок 1: Вхідна мова та LPC аналіз
    f.append(rect(30, 60, 140, 50, fill="#e0f2fe", stroke=POS, rx=5))
    f.append(text(100, 82, "Вхідний мовний", size=11, bold=True, color=INK))
    f.append(text(100, 97, "сигнал s[n]", size=11, color=INK))

    # Блок LPC аналізу
    f.append(rect(30, 140, 140, 55, fill="#f1f5f9", stroke=INK, rx=5))
    f.append(text(100, 160, "LPC Аналізатор", size=11, bold=True, color=INK))
    f.append(text(100, 178, "Коефіцієнти A(z)", size=10, color=MUTED))

    # Лінія від входу до LPC
    f.append(arrow(100, 110, 100, 140, color=INK, sw=1.5))

    # Блок Зважувального фільтра для входу
    f.append(rect(220, 60, 130, 50, fill="#fef3c7", stroke="#d97706", rx=5))
    f.append(text(285, 82, "Зважувальний", size=11, bold=True, color=INK))
    f.append(text(285, 97, "фільтр W(z)", size=11, color=INK))

    f.append(arrow(170, 85, 220, 85, color=INK, sw=1.5))

    # Лінія LPC -> Synthesis / Weighting
    f.append(line(170, 167, 390, 167, color=INK, sw=1.5, dash="4,3"))
    f.append(text(260, 160, "Параметри A(z) -> LSP", size=10, color=MUTED))

    # Генератори збудження: Adaptive & Algebraic Codebooks
    f.append(rect(30, 230, 150, 50, fill="#dcfce7", stroke="#16a34a", rx=5))
    f.append(text(105, 250, "Адаптивний кодбук", size=11, bold=True, color=INK))
    f.append(text(105, 266, "Основний тон (Pitch)", size=10, color=MUTED))

    f.append(rect(30, 300, 150, 50, fill="#fae8ff", stroke="#c026d3", rx=5))
    f.append(text(105, 320, "Алгебраїчний кодбук", size=11, bold=True, color=INK))
    f.append(text(105, 336, "Шумовий залишок (ACELP)", size=10, color=MUTED))

    # Множники підсилення g_p та g_c
    f.append(circle(230, 255, 16, fill="#ffffff", stroke=INK))
    f.append(text(230, 259, "× g_p", size=10, bold=True, color=INK))

    f.append(circle(230, 325, 16, fill="#ffffff", stroke=INK))
    f.append(text(230, 329, "× g_c", size=10, bold=True, color=INK))

    f.append(arrow(180, 255, 214, 255, color=INK, sw=1.5))
    f.append(arrow(180, 325, 214, 325, color=INK, sw=1.5))

    # Суматор збудження
    f.append(circle(290, 290, 16, fill="#ffffff", stroke=INK))
    f.append(text(290, 294, "+", size=14, bold=True, color=INK))

    f.append(arrow(246, 255, 290, 274, color=INK, sw=1.5))
    f.append(arrow(246, 325, 290, 306, color=INK, sw=1.5))

    # Синтезуючий фільтр 1/A(z)
    f.append(rect(350, 265, 140, 50, fill="#e0f2fe", stroke=POS, rx=5))
    f.append(text(420, 287, "Фільтр синтезу", size=11, bold=True, color=INK))
    f.append(text(420, 302, "1 / A(z)", size=11, color=INK))

    f.append(arrow(306, 290, 350, 290, color=INK, sw=1.5))

    # Зважувальний фільтр після синтезу W(z)
    f.append(rect(520, 265, 120, 50, fill="#fef3c7", stroke="#d97706", rx=5))
    f.append(text(580, 287, "Зважування", size=11, bold=True, color=INK))
    f.append(text(580, 302, "W(z)", size=11, color=INK))

    f.append(arrow(490, 290, 520, 290, color=INK, sw=1.5))

    # Суматор помилки (різниця між цільовим та синтезованим)
    f.append(circle(680, 180, 18, fill="#fee2e2", stroke=NEG))
    f.append(text(680, 185, "−", size=16, bold=True, color=NEG))

    # Зважений вхід -> суматор (+)
    f.append(line(350, 85, 680, 85, color=INK, sw=1.5))
    f.append(arrow(680, 85, 680, 162, color=INK, sw=1.5))
    f.append(text(665, 120, "+", size=12, bold=True, color=INK))

    # Зважений синтез -> суматор (-)
    f.append(line(640, 290, 680, 290, color=INK, sw=1.5))
    f.append(arrow(680, 290, 680, 198, color=INK, sw=1.5))
    f.append(text(690, 240, "− (синтез)", size=10, bold=True, color=NEG))

    # Блок Мінімізації Помилки (Feedback Loop)
    f.append(rect(560, 345, 210, 55, fill="#fee2e2", stroke=NEG, rx=6))
    f.append(text(665, 366, "Мінімізація середньокв. помилки E", size=10, bold=True, color=NEG))
    f.append(text(665, 383, "Пошук оптимальних індексів і g_p, g_c", size=9, color=INK))

    f.append(arrow(680, 198, 680, 345, color=NEG, sw=1.8))

    # Зворотний зв'язок від блоку мінімізації до кодбуків
    f.append(line(560, 372, 105, 372, color=NEG, sw=1.5, dash="4,3"))
    f.append(arrow(105, 372, 105, 350, color=NEG, sw=1.5))
    f.append(text(330, 388, "Зворотний зв'язок: вибір векторів кодбука", size=10, color=NEG))

    # Вихідний бітовий потік
    f.append(rect(680, 30, 100, 35, fill="#1e293b", stroke=INK, rx=4))
    f.append(text(730, 52, "RTP 8 кбіт/с", size=10, bold=True, color="#ffffff"))
    f.append(line(680, 180, 730, 180, color=INK, sw=1.5))
    f.append(arrow(730, 180, 730, 65, color=INK, sw=1.5))

    render(path, W, H, *f)
    print(f"Generated {path}")


# ── 3. opus-architecture-modes.svg ────────────────────────────────────────────
def fig_opus_architecture_modes():
    W, H = 820, 420
    path = os.path.join(IMG, 'opus-architecture-modes.svg')
    f = []

    f.append(rect(0, 0, W, H, fill=BG))

    # Заголовок
    f.append(text(W / 2, 25, "Гібридна архітектура кодека Opus (IETF RFC 6716)", size=14, bold=True, color=INK))

    # Вхідний аудіосигнал
    f.append(rect(30, 180, 130, 60, fill="#e0f2fe", stroke=POS, rx=6))
    f.append(text(95, 205, "Аудіовхід PCM", size=11, bold=True, color=INK))
    f.append(text(95, 222, "8 – 48 кГц (8-16 біт)", size=10, color=MUTED))

    # Блок розподілу частот / вибору режиму
    f.append(rect(190, 180, 110, 60, fill="#f1f5f9", stroke=INK, rx=6))
    f.append(text(245, 205, "Сепаратор полос /", size=10, bold=True, color=INK))
    f.append(text(245, 222, "Селектор режиму", size=10, color=INK))

    f.append(arrow(160, 210, 190, 210, color=INK, sw=1.8))

    # Верхній шлях: SILK Engine (Мовний LPC кодек)
    f.append(rect(330, 60, 280, 90, fill="#dcfce7", stroke="#16a34a", rx=6))
    f.append(text(470, 83, "Мовний рушій SILK (LPC / Skype)", size=12, bold=True, color="#15803d"))
    f.append(text(470, 103, "• Оптимізовано для мовлення (6 – 20 кбіт/с)", size=10, color=INK))
    f.append(text(470, 120, "• Частоти мовлення: 0 – 8 кГц (NB / WB)", size=10, color=INK))
    f.append(text(470, 137, "• Лінійне передбачення + Noise Shaping", size=10, color=MUTED))

    # Нижній шлях: CELT Engine (Музичний MDCT кодек)
    f.append(rect(330, 270, 280, 90, fill="#fae8ff", stroke="#c026d3", rx=6))
    f.append(text(470, 293, "Музичний рушій CELT (MDCT / Xiph.Org)", size=12, bold=True, color="#a21caf"))
    f.append(text(470, 313, "• Оптимізовано для звуку/музики (> 32 кбіт/с)", size=10, color=INK))
    f.append(text(470, 330, "• Спектр: 8 – 20 кГц (Superwide / Fullband)", size=10, color=INK))
    f.append(text(470, 347, "• Ультранизька затримка (від 2.5 мс)", size=10, color=MUTED))

    # Середній шлях: Гібридний режим
    f.append(rect(330, 170, 280, 80, fill="#fef3c7", stroke="#d97706", rx=6))
    f.append(text(470, 193, "Гібридний режим (Hybrid Mode)", size=12, bold=True, color="#b45309"))
    f.append(text(470, 213, "• 0–8 кГц кодує SILK (LPC для мовного ядра)", size=10, color=INK))
    f.append(text(470, 230, "• >8 кГц кодує CELT (MDCT для ВЧ деталей)", size=10, color=INK))

    # Лінії розгалуження
    f.append(arrow(300, 210, 330, 105, color=INK, sw=1.6))
    f.append(arrow(300, 210, 330, 210, color=INK, sw=1.6))
    f.append(arrow(300, 210, 330, 315, color=INK, sw=1.6))

    # Ентропійний кодер (Range Encoder)
    f.append(rect(650, 160, 140, 100, fill="#1e293b", stroke=INK, rx=6))
    f.append(text(720, 190, "Арифметичний", size=11, bold=True, color="#ffffff"))
    f.append(text(720, 207, "кодер (Range Coder)", size=11, color="#38bdf8"))
    f.append(text(720, 230, "+ Вбудований FEC", size=9, color="#cbd5e1"))
    f.append(text(720, 245, "+ Детектор тиші DTX", size=9, color="#cbd5e1"))

    # Лінії сходження до кодера
    f.append(arrow(610, 105, 650, 190, color=INK, sw=1.6))
    f.append(arrow(610, 210, 650, 210, color=INK, sw=1.6))
    f.append(arrow(610, 315, 650, 230, color=INK, sw=1.6))

    # Вихідний кадр Opus
    f.append(arrow(720, 260, 720, 370, color=POS, sw=2))
    f.append(rect(640, 375, 160, 35, fill="#dcfce7", stroke=POS, rx=4))
    f.append(text(720, 397, "Пакет Opus (6-510 кбіт/с)", size=10, bold=True, color=INK))

    render(path, W, H, *f)
    print(f"Generated {path}")


# ── 4. speech-codecs-tradeoffs.svg ────────────────────────────────────────────
def fig_speech_codecs_tradeoffs():
    W, H = 790, 410
    path = os.path.join(IMG, 'speech-codecs-tradeoffs.svg')
    f = []

    f.append(rect(0, 0, W, H, fill=BG))

    # Заголовок
    f.append(text(W / 2, 25, "Порівняння мовних кодеків: Якість (MOS) vs Бітрейт vs Затримка", size=14, bold=True, color=INK))

    # Осі координат
    x0, y0 = 80, 350
    w_axis, h_axis = 440, 290

    f.append(line(x0, y0, x0 + w_axis + 20, y0, color=INK, sw=1.5))
    f.append(line(x0, y0, x0, y0 - h_axis - 10, color=INK, sw=1.5))

    f.append(text(x0 + w_axis + 25, y0 + 18, "Бітрейт (кбіт/с, лог. шкала)", size=11, color=INK, anchor="end"))
    f.append(text(x0 - 15, y0 - h_axis - 15, "Оцінка якості мови MOS (1.0 – 5.0)", size=11, color=INK, anchor="start"))

    # Мітки MOS на осі Y (2.0, 3.0, 4.0, 4.5, 5.0)
    for mos, label in [(2.0, "2.0"), (3.0, "3.0 (GSM)"), (4.0, "4.0 (Toll)"), (4.5, "4.5 (HD)"), (5.0, "5.0 (Orig)")]:
        py = y0 - (mos - 1.0) * (h_axis / 4.0)
        f.append(line(x0 - 4, py, x0 + w_axis, py, color=MUTED, sw=0.8, dash="3,3"))
        f.append(text(x0 - 8, py + 4, label, size=10, color=MUTED, anchor="end"))

    # Кодеки та їх позиції (x_kbps -> log scale pos, mos)
    def map_x(kbps):
        log_val = math.log2(kbps / 4.0)
        return x0 + log_val * (w_axis / 5.0)

    def map_y(mos):
        return y0 - (mos - 1.0) * (h_axis / 4.0)

    # Точки кодеків: (назва, kbps, mos, delay_ms, color, pos_offset)
    codecs_data = [
        ("G.729 (CS-ACELP)", 8.0, 3.92, "15 мс", NEG, (10, -12)),
        ("G.711 (A/µ-law)", 64.0, 4.10, "0.125 мс", POS, (-60, 20)),
        ("GSM-FR (RPT-LTP)", 13.0, 3.50, "20 мс", MUTED, (10, 15)),
        ("AMR-WB (G.722.2)", 12.65, 4.25, "25 мс", "#d97706", (-40, -15)),
        ("Opus (Narrowband)", 8.0, 4.15, "5-20 мс", "#16a34a", (-70, -15)),
        ("Opus (Wideband)", 20.0, 4.55, "5-20 мс", "#16a34a", (10, -12)),
        ("Opus (Fullband)", 48.0, 4.80, "2.5-20 мс", "#16a34a", (10, -10))
    ]

    # З'єднувальна лінія для Opus динамічного діапазону
    px_op1, py_op1 = map_x(8.0), map_y(4.15)
    px_op2, py_op2 = map_x(20.0), map_y(4.55)
    px_op3, py_op3 = map_x(48.0), map_y(4.80)
    f.append(f'<polyline points="{px_op1:.1f},{py_op1:.1f} {px_op2:.1f},{py_op2:.1f} {px_op3:.1f},{py_op3:.1f}" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-dasharray="4,2"/>')

    for name, kbps, mos, delay, clr, (dx, dy) in codecs_data:
        px = map_x(kbps)
        py = map_y(mos)

        f.append(circle(px, py, 6, fill=clr, stroke=INK))
        f.append(text(px + dx, py + dy, f"{name}", size=10, bold=True, color=clr, anchor="start" if dx > 0 else "end"))
        f.append(text(px + dx, py + dy + 12, f"({kbps} кбіт/с, {delay})", size=9, color=MUTED, anchor="start" if dx > 0 else "end"))

    # Мітки осі Х (кбіт/с)
    for kbps in [4, 8, 16, 32, 64, 128]:
        px = map_x(kbps)
        f.append(line(px, y0, px, y0 + 5, color=INK, sw=1.2))
        f.append(text(px, y0 + 18, f"{kbps}", size=10, color=MUTED))

    # Справа: Легенда та критерії оцінювання MOS
    px_side = 550
    py_side = 60
    f.append(rect(px_side, py_side, 225, 290, fill="#f8fafc", stroke=BORDER, rx=6))
    f.append(text(px_side + 112, py_side + 22, "Шкала якості MOS", size=12, bold=True, color=INK))

    mos_levels = [
        ("5.0", "Відмінно", "Непомітні спотворення", "#15803d"),
        ("4.0–4.5", "Toll Quality", "Якість дротового зв'язку", "#16a34a"),
        ("3.5–4.0", "Задовільно", "Зв'язок мобільної мережі", "#d97706"),
        ("3.0–3.5", "Прийнятно", "Помітні шуми/компресія", "#c026d3"),
        ("< 3.0", "Погано", "Важко розібрати слова", NEG)
    ]

    for idx, (m_val, m_label, m_desc, m_clr) in enumerate(mos_levels):
        y_item = py_side + 50 + idx * 46
        f.append(rect(px_side + 12, y_item, 50, 22, fill=m_clr, stroke="none", rx=3))
        f.append(text(px_side + 37, y_item + 15, m_val, size=10, bold=True, color="#ffffff"))
        f.append(text(px_side + 70, y_item + 14, m_label, size=10, bold=True, color=INK, anchor="start"))
        f.append(text(px_side + 70, y_item + 28, m_desc, size=9, color=MUTED, anchor="start"))

    render(path, W, H, *f)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_g711_companding_curve()
    fig_g729_acelp_pipeline()
    fig_opus_architecture_modes()
    fig_speech_codecs_tradeoffs()
