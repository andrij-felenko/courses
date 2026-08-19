# -*- coding: utf-8 -*-
"""Фігури теми «CDM-модель ESD (заряджений прилад)».
Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def diode_sym(cx, cy, up=True, color=INK, sw=1.6, size=10):
    """Символ діода: анод/катод."""
    out = []
    if up:   # анод знизу, катод угорі
        out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdecea" stroke="%s" stroke-width="%.1f"/>'
                   % (cx - size, cy + size, cx + size, cy + size, cx, cy - size, color, sw))
        out.append(line(cx - size, cy - size, cx + size, cy - size, color=color, sw=sw + 0.4))
    else:    # анод угорі, катод знизу
        out.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdecea" stroke="%s" stroke-width="%.1f"/>'
                   % (cx - size, cy - size, cx + size, cy - size, cx, cy + size, color, sw))
        out.append(line(cx - size, cy + size, cx + size, cy + size, color=color, sw=sw + 0.4))
    return "".join(out)


def gnd_sym(cx, cy, color=INK, sw=1.5):
    """Символ землі."""
    out = [
        line(cx, cy, cx, cy + 10, color=color, sw=sw),
        line(cx - 12, cy + 10, cx + 12, cy + 10, color=color, sw=sw + 0.5),
        line(cx - 8, cy + 14, cx + 8, cy + 14, color=color, sw=sw),
        line(cx - 4, cy + 18, cx + 4, cy + 18, color=color, sw=sw - 0.3)
    ]
    return "".join(out)


def res_sym(cx, cy, vert=False, length=30, color=INK, sw=1.5):
    """Символ резистора (прямокутник)."""
    if vert:
        w, h = 10, length
    else:
        w, h = length, 10
    return rect(cx - w/2, cy - h/2, w, h, fill="#ffffff", stroke=color, sw=sw, rx=2)


def cap_sym(cx, cy, vert=False, color=INK, sw=1.5):
    """Символ конденсатора."""
    out = []
    if vert:
        out.append(line(cx - 10, cy - 3, cx + 10, cy - 3, color=color, sw=sw + 0.5))
        out.append(line(cx - 10, cy + 3, cx + 10, cy + 3, color=color, sw=sw + 0.5))
    else:
        out.append(line(cx - 3, cy - 10, cx - 3, cy + 10, color=color, sw=sw + 0.5))
        out.append(line(cx + 3, cy - 10, cx + 3, cy + 10, color=color, sw=sw + 0.5))
    return "".join(out)


# ── Фігура 1: Накопичення заряду та розряд через один вивід ─────────────────
def fig_cdm_mechanism():
    W, H = 760, 360
    P = []

    # Ліва панель: Фаза 1 — Накопичення заряду
    lx, ly, lw, lh = 30, 45, 335, 290
    P.append(rect(lx, ly, lw, lh, fill="#fafbfc", stroke="#d0d7de", sw=1.4))
    P.append(text(lx + lw / 2, ly + 22, "1. Накопичення заряду (+Q)", size=13, bold=True, color=POS))
    P.append(text(lx + lw / 2, ly + 40, "тертя об лоток або наведене поле", size=11, color=MUTED))

    # Корпус чипа
    cx1, cy1 = lx + lw / 2, ly + 115
    P.append(rect(cx1 - 90, cy1 - 40, 180, 80, fill="#2c3e50", stroke="#1a252f", sw=2, rx=4))
    P.append(text(cx1, cy1 - 10, "Корпус мікросхеми (IC)", size=12, color="#ffffff", bold=True))
    P.append(text(cx1, cy1 + 14, "Кристал + рамка виводів", size=10, color="#bdc3c7"))

    # Заряди на корпусі
    P.append(plus(cx1 - 70, cy1 - 25, r=6))
    P.append(plus(cx1 - 35, cy1 - 25, r=6))
    P.append(plus(cx1 + 35, cy1 - 25, r=6))
    P.append(plus(cx1 + 70, cy1 - 25, r=6))
    P.append(plus(cx1 - 70, cy1 + 25, r=6))
    P.append(plus(cx1 + 70, cy1 + 25, r=6))

    # Виводи чипа (ізольовані в повітрі)
    for i, offset in enumerate([-60, -30, 0, 30, 60]):
        px = cx1 + offset
        P.append(line(px, cy1 + 40, px, cy1 + 65, color="#7f8c8d", sw=2.5))
        P.append(circle(px, cy1 + 67, 3, fill="#95a5a6", stroke="#7f8c8d", sw=1))

    # Паразитна ємність до землі
    P.append(line(cx1, cy1 + 40, cx1, cy1 + 85, color=MUTED, sw=1.2, dash="3,3"))
    P.append(cap_sym(cx1, cy1 + 95, vert=True, color=MUTED, sw=1.4))
    P.append(text(cx1 + 45, cy1 + 98, "C_pkg ≈ 1–10 пФ", size=10, color=MUTED, bold=True))
    P.append(line(cx1, cy1 + 105, cx1, cy1 + 120, color=MUTED, sw=1.2, dash="3,3"))
    P.append(gnd_sym(cx1, cy1 + 120, color=MUTED, sw=1.2))

    tb1, _, _ = textbox(lx + lw / 2, ly + 255, "Потенціал чипа V_CDM = 250–1000 В\nЗаряд рівномірно розподілений на кристалі", size=10, pad=6)
    P.append(tb1)

    # Права панель: Фаза 2 — Надшвидкий розряд
    rx, ry, rw, rh = 395, 45, 335, 290
    P.append(rect(rx, ry, rw, rh, fill="#fafbfc", stroke="#d0d7de", sw=1.4))
    P.append(text(rx + rw / 2, ry + 22, "2. Блискавичний розряд через 1 вивід", size=13, bold=True, color=POS))
    P.append(text(rx + rw / 2, ry + 40, "дотик до заземленого металу / плати", size=11, color=MUTED))

    # Корпус чипа
    cx2, cy2 = rx + rw / 2, ry + 115
    P.append(rect(cx2 - 90, cy2 - 40, 180, 80, fill="#2c3e50", stroke="#1a252f", sw=2, rx=4))
    P.append(text(cx2, cy2 - 10, "Корпус мікросхеми (IC)", size=12, color="#ffffff", bold=True))
    P.append(text(cx2, cy2 + 14, "Стік заряду в одну точку!", size=10, color="#e74c3c", bold=True))

    # Виводи, один торкається землі
    for i, offset in enumerate([-60, -30, 30, 60]):
        px = cx2 + offset
        P.append(line(px, cy2 + 40, px, cy2 + 65, color="#7f8c8d", sw=2.5))
        P.append(circle(px, cy2 + 67, 3, fill="#95a5a6", stroke="#7f8c8d", sw=1))

    # Заземлений контактний вивід (центр)
    px_gnd = cx2
    P.append(line(px_gnd, cy2 + 40, px_gnd, cy2 + 75, color=POS, sw=3))
    # Іскра
    P.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#f39c12" stroke="#e67e22" stroke-width="1.2"/>'
             % (px_gnd - 5, cy2 + 75, px_gnd + 5, cy2 + 81, px_gnd - 3, cy2 + 87, px_gnd + 2, cy2 + 95))
    # Заземлена контактна площадка
    P.append(rect(px_gnd - 30, cy2 + 95, 60, 8, fill="#95a5a6", stroke="#7f8c8d", sw=1.5, rx=1))
    P.append(line(px_gnd, cy2 + 103, px_gnd, cy2 + 118, color=POS, sw=2))
    P.append(gnd_sym(px_gnd, cy2 + 118, color=POS, sw=1.8))

    # Стрілка розрядного струму
    P.append(arrow(px_gnd + 18, cy2 + 55, px_gnd + 18, cy2 + 90, color=POS, sw=2.2))
    P.append(text(px_gnd + 65, cy2 + 75, "I_peak = 5–15 A\nt_r < 200 пс", size=10, color=POS, bold=True))

    tb2, _, _ = textbox(rx + rw / 2, ly + 255, "Весь заряд Q вилітає крізь один пін!\nСтрум досягає піку за частки наносекунди", size=10, pad=6)
    P.append(tb2)

    return render(os.path.join(IMG, "cdm-charging-and-discharge.svg"), W, H, *P)


# ── Фігура 2: Порівняння хвильових форм і схем HBM vs CDM ───────────────────
def fig_cdm_vs_hbm():
    W, H = 760, 360
    P = []

    # Ліва частина: Графік розрядного струму в часі
    gx, gy, gw, gh = 30, 45, 365, 275
    P.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#d0d7de", sw=1.2))
    P.append(text(gx + gw / 2, gy + 22, "Форма розрядного струму: CDM проти HBM", size=12, bold=True))

    # Осі
    ox, oy = gx + 60, gy + gh - 40
    P.append(line(ox, oy, ox + gw - 80, oy, color=LINE, sw=1.5))       # Вісь часу
    P.append(line(ox, oy, ox, gy + 45, color=LINE, sw=1.5))             # Вісь струму
    P.append(text(ox + gw - 75, oy + 18, "Час t", size=11, color=INK, anchor="end"))
    P.append(text(ox + 10, gy + 42, "Струм I (А)", size=10, color=INK, anchor="start", bold=True))

    # Позначки шкали струму
    P.append(line(ox - 4, oy - 150, ox, oy - 150, color=LINE, sw=1))
    P.append(text(ox - 8, oy - 146, "15 А", size=9, color=POS, anchor="end", bold=True))
    P.append(line(ox - 4, oy - 25, ox, oy - 25, color=LINE, sw=1))
    P.append(text(ox - 8, oy - 22, "1.3 А", size=9, color=NEG, anchor="end", bold=True))
    P.append(text(ox - 8, oy + 4, "0", size=9, color=MUTED, anchor="end"))

    # Крива CDM (дуже вузький, високий гострий пік)
    cdm_path = (
        'M %.1f %.1f '
        'C %.1f %.1f, %.1f %.1f, %.1f %.1f '
        'C %.1f %.1f, %.1f %.1f, %.1f %.1f '
        'C %.1f %.1f, %.1f %.1f, %.1f %.1f'
        % (ox, oy,
           ox + 4, oy - 80, ox + 8, oy - 160, ox + 12, oy - 160,
           ox + 16, oy - 160, ox + 22, oy - 40, ox + 32, oy - 10,
           ox + 40, oy + 5, ox + 55, oy - 3, ox + 75, oy)
    )
    P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (cdm_path, POS))
    P.append(text(ox + 35, oy - 145, "CDM (500 В)", size=11, color=POS, bold=True, anchor="start"))
    P.append(text(ox + 35, oy - 130, "I_pk ≈ 10–15 А\nтривалість < 1 нс", size=9, color=POS, anchor="start"))

    # Крива HBM (низька, широка)
    hbm_path = (
        'M %.1f %.1f '
        'C %.1f %.1f, %.1f %.1f, %.1f %.1f '
        'C %.1f %.1f, %.1f %.1f, %.1f %.1f '
        'C %.1f %.1f, %.1f %.1f, %.1f %.1f'
        % (ox, oy,
           ox + 15, oy - 20, ox + 30, oy - 25, ox + 45, oy - 25,
           ox + 90, oy - 25, ox + 140, oy - 18, ox + 180, oy - 10,
           ox + 210, oy - 4, ox + 240, oy - 1, ox + 260, oy)
    )
    P.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,2"/>' % (hbm_path, NEG))
    P.append(text(ox + 130, oy - 38, "HBM (2 кВ)", size=11, color=NEG, bold=True, anchor="start"))
    P.append(text(ox + 130, oy - 24, "I_pk ≈ 1.3 А, ~150 нс", size=9, color=NEG, anchor="start"))

    # Права частина: Порівняння параметрів та еквівалентних схем
    px, py, pw, ph = 410, 45, 320, 275
    P.append(rect(px, py, pw, ph, fill="#fafbfc", stroke="#d0d7de", sw=1.2))
    P.append(text(px + pw / 2, py + 22, "Фундаментальна відмінність", size=12, bold=True))

    # Блок HBM
    P.append(rect(px + 12, py + 38, pw - 24, 100, fill="#eaf0fd", stroke="#b9c6e6", sw=1.1, rx=4))
    P.append(text(px + 22, py + 56, "HBM (Human Body Model)", size=11, bold=True, color=NEG, anchor="start"))
    P.append(text(px + 22, py + 74, "• Джерело: C = 100 пФ, R = 1500 Ом", size=10, color=INK, anchor="start"))
    P.append(text(px + 22, py + 91, "• Обмеження: опір тіла 1.5 кОм стримує струм", size=10, color=INK, anchor="start"))
    P.append(text(px + 22, py + 108, "• Характер пошкоджень: теплове вигорання", size=10, color=INK, anchor="start"))
    P.append(text(px + 22, py + 125, "• Імпульс: t_r ≈ 2–10 нс, тривалість ~150 нс", size=9, color=MUTED, anchor="start"))

    # Блок CDM
    P.append(rect(px + 12, py + 150, pw - 24, 110, fill="#fdecea", stroke="#e2a59f", sw=1.1, rx=4))
    P.append(text(px + 22, py + 168, "CDM (Charged Device Model)", size=11, bold=True, color=POS, anchor="start"))
    P.append(text(px + 22, py + 186, "• Джерело: C_pkg = 1–10 пФ (на кристалі)", size=10, color=INK, anchor="start"))
    P.append(text(px + 22, py + 203, "• Обмеження: R_spark < 10 Ом, L_pin ≈ 1–3 нГн", size=10, color=INK, anchor="start"))
    P.append(text(px + 22, py + 220, "• Струм розряду сягає 15 Ампер!", size=10, color=POS, bold=True, anchor="start"))
    P.append(text(px + 22, py + 237, "• Руйнування: пробій підзатворного оксиду", size=10, color=POS, anchor="start"))
    P.append(text(px + 22, py + 252, "• Імпульс: t_r < 200 пс, тривалість < 1 нс", size=9, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "cdm-vs-hbm-comparison.svg"), W, H, *P)


# ── Фігура 3: Чому класичний захист не рятує оксид затвора ──────────────────
def fig_gate_oxide_rupture():
    W, H = 760, 360
    P = []

    # Головна лінія схеми
    P.append(text(W / 2, 25, "Шлях CDM-розряду при класичному однорівневому захисті", size=13, bold=True))

    # Контактний майданчик (Pad)
    pad_x, pad_y = 60, 140
    P.append(rect(pad_x - 20, pad_y - 20, 40, 40, fill="#f1c40f", stroke="#d4ac0d", sw=1.8, rx=3))
    P.append(text(pad_x, pad_y + 4, "PAD", size=10, bold=True))
    P.append(text(pad_x, pad_y + 35, "Заземлений пін", size=10, color=POS, bold=True))

    # Індуктивність розварки / виводу L_pin
    P.append(line(pad_x + 20, pad_y, pad_x + 55, pad_y, color=INK, sw=2))
    # Зображення котушки (індуктивності)
    lx = pad_x + 75
    P.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2"/>'
             % (lx - 20, pad_y,
                lx - 15, pad_y - 14, lx - 5, pad_y - 14, lx, pad_y,
                lx + 5, pad_y - 14, lx + 15, pad_y - 14, lx + 20, pad_y,
                lx + 25, pad_y - 14, lx + 35, pad_y - 14, lx + 40, pad_y,
                INK))
    P.append(text(lx + 10, pad_y - 20, "L_pkg ≈ 2 нГн", size=10, color=POS, bold=True))
    P.append(line(lx + 40, pad_y, lx + 70, pad_y, color=INK, sw=2))

    # Вузол 1: Контакт первинного захисту
    n1_x = lx + 70
    P.append(circle(n1_x, pad_y, 4, fill=INK, stroke=INK))

    # Первинний затискач HBM (Primary Clamp: великий діод / GGNMOS)
    P.append(line(n1_x, pad_y, n1_x, pad_y + 30, color=INK, sw=2))
    P.append(diode_sym(n1_x, pad_y + 45, up=False, color=INK, sw=1.6, size=11))
    P.append(line(n1_x, pad_y + 60, n1_x, pad_y + 80, color=INK, sw=2))
    P.append(res_sym(n1_x, pad_y + 92, vert=True, length=20, color=INK, sw=1.5))
    P.append(text(n1_x + 28, pad_y + 94, "R_dyn ≈ 1.5 Ом", size=9, color=MUTED))
    P.append(line(n1_x, pad_y + 105, n1_x, pad_y + 120, color=INK, sw=2))
    P.append(gnd_sym(n1_x, pad_y + 120, color=INK, sw=1.5))
    P.append(text(n1_x + 55, pad_y + 45, "Первинний\nзатискач HBM", size=10, bold=True, color=NEG))

    # Шина до внутрішнього приймача (з паразитною індуктивністю та опором)
    P.append(line(n1_x, pad_y, n1_x + 80, pad_y, color=INK, sw=2))
    P.append(res_sym(n1_x + 100, pad_y, vert=False, length=26, color=INK, sw=1.5))
    P.append(text(n1_x + 100, pad_y - 12, "R_bus", size=9, color=MUTED))
    P.append(line(n1_x + 115, pad_y, n1_x + 180, pad_y, color=INK, sw=2))

    # Вхідний приймач (MOSFET Inverter Gate)
    gate_x = n1_x + 220
    P.append(circle(gate_x, pad_y, 4, fill=INK, stroke=INK))
    P.append(text(gate_x, pad_y - 28, "Вузол затвора (Gate)", size=11, bold=True, color=POS))

    # Підзатворний оксид (тонкий конденсатор C_ox)
    P.append(line(gate_x, pad_y, gate_x, pad_y + 40, color=INK, sw=2))
    P.append(cap_sym(gate_x, pad_y + 50, vert=True, color=POS, sw=2))
    P.append(text(gate_x + 45, pad_y + 52, "C_ox (t_ox ≈ 2 нм)", size=10, bold=True, color=POS))
    P.append(line(gate_x, pad_y + 60, gate_x, pad_y + 85, color=INK, sw=2))
    P.append(gnd_sym(gate_x, pad_y + 85, color=INK, sw=1.5))

    # Знак пробою (червона блискавка на оксиді)
    P.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.2"/>'
             % (gate_x - 4, pad_y + 42, gate_x + 4, pad_y + 49, gate_x - 3, pad_y + 54, gate_x + 3, pad_y + 60, POS, "#962d22"))
    P.append(text(gate_x, pad_y + 115, "ПРОБІЙ ОКСИДУ!\nV_ox > V_breakdown (3–4 В)", size=10, color=POS, bold=True))

    # Розрахункові блоки причин перенапруги
    box_x, box_y, box_w, box_h = 490, 160, 240, 175
    P.append(rect(box_x, box_y, box_w, box_h, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    P.append(text(box_x + box_w / 2, box_y + 18, "Чому напруга зашкалює:", size=11, bold=True, color=POS))
    P.append(text(box_x + 12, box_y + 38, "1. Затримка вмикання затискача:", size=9, bold=True, color=INK, anchor="start"))
    P.append(text(box_x + 22, box_y + 52, "t_on ≈ 1–2 нс > фронту CDM (200 пс)", size=9, color=MUTED, anchor="start"))
    P.append(text(box_x + 12, box_y + 72, "2. Індуктивний викид напруги:", size=9, bold=True, color=INK, anchor="start"))
    P.append(text(box_x + 22, box_y + 86, "V_L = L · (dI/dt) = 2 нГн · 50 А/нс = 100 В!", size=9, color=POS, bold=True, anchor="start"))
    P.append(text(box_x + 12, box_y + 106, "3. Динамічне падіння напруги:", size=9, bold=True, color=INK, anchor="start"))
    P.append(text(box_x + 22, box_y + 120, "V_R = I · R_dyn = 10 А · 1.5 Ом = 15 В", size=9, color=MUTED, anchor="start"))
    P.append(text(box_x + 12, box_y + 142, "Сумарно на затворі: десятки вольтів,", size=9, bold=True, color=POS, anchor="start"))
    P.append(text(box_x + 12, box_y + 158, "що миттєво руйнує діелектрик 2 нм!", size=9, color=POS, anchor="start"))

    return render(os.path.join(IMG, "gate-oxide-rupture-path.svg"), W, H, *P)


# ── Фігура 4: Дворівневий захист CDM ─────────────────────────────────────────
def fig_dual_stage_protection():
    W, H = 760, 360
    P = []

    P.append(text(W / 2, 25, "Дворівнева архітектура ESD/CDM захисту (Dual-Stage Protection)", size=13, bold=True))

    # Контактний майданчик (PAD)
    pad_x, pad_y = 60, 150
    P.append(rect(pad_x - 20, pad_y - 20, 40, 40, fill="#f1c40f", stroke="#d4ac0d", sw=1.8, rx=3))
    P.append(text(pad_x, pad_y + 4, "PAD", size=10, bold=True))

    # Шина від Pad до первинного захисту
    n1_x = 180
    P.append(line(pad_x + 20, pad_y, n1_x, pad_y, color=INK, sw=2.5))
    P.append(circle(n1_x, pad_y, 4, fill=INK, stroke=INK))

    # Ступінь 1: Первинний затискач (Primary ESD Clamp)
    P.append(line(n1_x, pad_y, n1_x, pad_y - 45, color=POS, sw=2.5))
    P.append(diode_sym(n1_x, pad_y - 60, up=True, color=POS, sw=1.8, size=11))
    P.append(line(n1_x, pad_y - 75, n1_x, pad_y - 95, color=POS, sw=2.5))
    P.append(text(n1_x, pad_y - 102, "VDD", size=10, bold=True))

    P.append(line(n1_x, pad_y, n1_x, pad_y + 45, color=POS, sw=2.5))
    P.append(diode_sym(n1_x, pad_y + 60, up=False, color=POS, sw=1.8, size=11))
    P.append(line(n1_x, pad_y + 75, n1_x, pad_y + 95, color=POS, sw=2.5))
    P.append(gnd_sym(n1_x, pad_y + 95, color=POS, sw=1.8))

    P.append(text(n1_x - 65, pad_y + 75, "Первинний\nзатискач\n(відводить ~14.9 А)", size=10, color=POS, bold=True))

    # Розділовий резистор затвора R_gate (Isolation Resistor)
    r_x = 310
    P.append(line(n1_x, pad_y, r_x - 25, pad_y, color=INK, sw=2))
    P.append(res_sym(r_x, pad_y, vert=False, length=44, color=FIELD, sw=2))
    P.append(text(r_x, pad_y - 14, "R_gate ≈ 100–300 Ом", size=10, bold=True, color=FIELD))
    P.append(text(r_x, pad_y + 20, "Гасить перепад ΔV", size=9, color=MUTED))
    P.append(line(r_x + 25, pad_y, 450, pad_y, color=INK, sw=2))

    # Ступінь 2: Вторинний затискач біля самого затвора (Secondary Local Clamp)
    n2_x = 460
    P.append(circle(n2_x, pad_y, 4, fill=INK, stroke=INK))

    P.append(line(n2_x, pad_y, n2_x, pad_y - 35, color=FIELD, sw=1.8))
    P.append(diode_sym(n2_x, pad_y - 48, up=True, color=FIELD, sw=1.5, size=9))
    P.append(line(n2_x, pad_y - 60, n2_x, pad_y - 75, color=FIELD, sw=1.8))
    P.append(text(n2_x, pad_y - 82, "VDD_local", size=9, bold=True))

    P.append(line(n2_x, pad_y, n2_x, pad_y + 35, color=FIELD, sw=1.8))
    P.append(diode_sym(n2_x, pad_y + 48, up=False, color=FIELD, sw=1.5, size=9))
    P.append(line(n2_x, pad_y + 60, n2_x, pad_y + 75, color=FIELD, sw=1.8))
    P.append(gnd_sym(n2_x, pad_y + 75, color=FIELD, sw=1.5))

    P.append(text(n2_x + 55, pad_y + 55, "Вторинний\nзатискач CDM\n(струм < 100 мА)", size=9, color=FIELD, bold=True))

    # Вхідний інвертор / тонкий затвор
    gate_x = 610
    P.append(line(n2_x, pad_y, gate_x, pad_y, color=INK, sw=2))

    # Схематичний інвертор
    P.append(rect(gate_x - 5, pad_y - 40, 70, 80, fill="#ffffff", stroke="#2c3e50", sw=1.5, rx=3))
    P.append(text(gate_x + 30, pad_y - 20, "Вхідний", size=10, bold=True))
    P.append(text(gate_x + 30, pad_y - 5, "буфер", size=10, bold=True))
    P.append(text(gate_x + 30, pad_y + 15, "КМОН", size=10, color=MUTED))
    P.append(text(gate_x + 30, pad_y + 30, "(t_ox ~ 2 нм)", size=9, color=MUTED))

    # Фіксація напруги на затворі
    P.append(rect(430, 275, 290, 60, fill="#eafaf1", stroke=FIELD, sw=1.4, rx=4))
    P.append(text(575, 295, "Безпечна напруга на затворі:", size=11, bold=True, color=FIELD))
    P.append(text(575, 318, "V_gate = V_clamp,sec ≈ 1.2–1.8 В < V_breakdown", size=10, bold=True, color=INK))

    return render(os.path.join(IMG, "dual-stage-cdm-protection.svg"), W, H, *P)


# ── Фігура 5: Міждоменний CDM-розряд ──────────────────────────────────────────
def fig_cross_domain_cdm():
    W, H = 760, 360
    P = []

    P.append(text(W / 2, 25, "Міждоменний CDM-розряд між доменами живлення (Cross-Domain ESD)", size=13, bold=True))

    # Домен 1: I/O Домен (3.3 В)
    d1_x, d1_y, d1_w, d1_h = 40, 55, 310, 265
    P.append(rect(d1_x, d1_y, d1_w, d1_h, fill="#fafbfc", stroke="#3498db", sw=1.5, rx=5))
    P.append(text(d1_x + d1_w / 2, d1_y + 20, "Домен вводу-виводу (I/O Domain, 3.3 В)", size=11, bold=True, color=NEG))

    # Домен 2: Core Домен (0.8 В)
    d2_x, d2_y, d2_w, d2_h = 410, 55, 310, 265
    P.append(rect(d2_x, d2_y, d2_w, d2_h, fill="#fafbfc", stroke="#e67e22", sw=1.5, rx=5))
    P.append(text(d2_x + d2_w / 2, d2_y + 20, "Ядровий домен (Core Domain, 0.8 В)", size=11, bold=True, color=POS))

    # I/O Pad, що заземлюється при CDM
    pad_x, pad_y = d1_x + 50, d1_y + 90
    P.append(rect(pad_x - 18, pad_y - 18, 36, 36, fill="#f1c40f", stroke="#d4ac0d", sw=1.5, rx=2))
    P.append(text(pad_x, pad_y + 4, "PAD", size=9, bold=True))
    P.append(line(pad_x, pad_y + 18, pad_x, pad_y + 45, color=POS, sw=2))
    P.append(gnd_sym(pad_x, pad_y + 45, color=POS, sw=1.5))
    P.append(text(pad_x + 45, pad_y + 50, "Заземлений\nпін I/O", size=9, color=POS, bold=True))

    # Сигнальна лінія через межу доменів (наприклад, рівневий перетворювач або лінія шини)
    sig_y = d1_y + 90
    P.append(line(pad_x + 18, sig_y, d2_x + 70, sig_y, color=INK, sw=2))
    P.append(arrow(d1_x + d1_w - 20, sig_y, d2_x + 30, sig_y, color=INK, sw=2))
    P.append(text(380, sig_y - 12, "Сигнал", size=9, color=MUTED))

    # Тонкий транзистор ядра на стороні домену 2
    gate_x = d2_x + 90
    P.append(circle(gate_x, sig_y, 4, fill=INK, stroke=INK))
    P.append(line(gate_x, sig_y, gate_x, sig_y + 35, color=INK, sw=2))
    P.append(cap_sym(gate_x, sig_y + 45, vert=True, color=POS, sw=2))
    P.append(line(gate_x, sig_y + 55, gate_x, sig_y + 80, color=INK, sw=2))
    P.append(line(gate_x, sig_y + 80, d2_x + 230, sig_y + 80, color=INK, sw=2))
    P.append(text(gate_x + 45, sig_y + 45, "Оксид ядра\n(1.2 нм)", size=9, color=POS, bold=True))

    # Шина землі ядра VSS_CORE
    core_gnd_x = d2_x + 230
    P.append(line(core_gnd_x, sig_y + 80, core_gnd_x, d2_y + 220, color="#e67e22", sw=2))
    P.append(gnd_sym(core_gnd_x, d2_y + 220, color="#e67e22", sw=1.5))
    P.append(text(core_gnd_x, d2_y + 245, "VSS_CORE", size=10, bold=True, color="#e67e22"))

    # Шина землі I/O VSS_IO
    io_gnd_x = d1_x + 230
    P.append(line(io_gnd_x, pad_y + 45, io_gnd_x, d1_y + 220, color="#3498db", sw=2))
    P.append(gnd_sym(io_gnd_x, d1_y + 220, color="#3498db", sw=1.5))
    P.append(text(io_gnd_x, d1_y + 245, "VSS_IO", size=10, bold=True, color="#3498db"))

    # Міждоменний затискач між VSS_IO та VSS_CORE (Anti-parallel cross-domain diodes)
    cx_mid = 380
    P.append(line(io_gnd_x, d1_y + 190, cx_mid - 25, d1_y + 190, color=INK, sw=1.8))
    P.append(line(core_gnd_x, d2_y + 190, cx_mid + 25, d2_y + 190, color=INK, sw=1.8))

    # Зустрічно-паралельні діоди
    P.append(line(cx_mid - 25, d1_y + 175, cx_mid - 25, d1_y + 205, color=INK, sw=1.8))
    P.append(line(cx_mid + 25, d1_y + 175, cx_mid + 25, d1_y + 205, color=INK, sw=1.8))

    P.append(line(cx_mid - 25, d1_y + 175, cx_mid - 10, d1_y + 175, color=FIELD, sw=1.8))
    P.append(diode_sym(cx_mid, d1_y + 175, up=False, color=FIELD, sw=1.5, size=8))
    P.append(line(cx_mid + 10, d1_y + 175, cx_mid + 25, d1_y + 175, color=FIELD, sw=1.8))

    P.append(line(cx_mid + 25, d1_y + 205, cx_mid + 10, d1_y + 205, color=FIELD, sw=1.8))
    P.append(diode_sym(cx_mid, d1_y + 205, up=True, color=FIELD, sw=1.5, size=8))
    P.append(line(cx_mid - 10, d1_y + 205, cx_mid - 25, d1_y + 205, color=FIELD, sw=1.8))

    P.append(text(cx_mid, d1_y + 155, "Міждоменні діоди", size=9, bold=True, color=FIELD))
    P.append(text(cx_mid, d1_y + 235, "Шлях стікання заряду ядра", size=9, color=MUTED))

    # Стрілка шляху повернення заряду ядра через міждоменні діоди
    P.append(arrow(core_gnd_x, d2_y + 180, cx_mid + 30, d2_y + 180, color=POS, sw=2))
    P.append(arrow(cx_mid - 30, d1_y + 180, io_gnd_x, d1_y + 180, color=POS, sw=2))

    return render(os.path.join(IMG, "cross-domain-cdm.svg"), W, H, *P)


if __name__ == "__main__":
    fig_cdm_mechanism()
    fig_cdm_vs_hbm()
    fig_gate_oxide_rupture()
    fig_dual_stage_protection()
    fig_cross_domain_cdm()
    print("All CDM figures generated successfully.")
