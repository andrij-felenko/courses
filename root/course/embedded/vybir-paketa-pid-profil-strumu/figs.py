# -*- coding: utf-8 -*-
"""Фігури до теми «Вибір пакета під профіль струму».
Запуск: python figs.py   → пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольорова палітра для хімій та графіків
C_SOCL2 = "#8e44ad"  # фіолетовий — Li-SOCl2
C_MNO2  = "#2980b9"  # синій — Li-MnO2 (CR2032 / CR123A)
C_LION  = POS        # червоний — Li-Ion / Li-Po
C_LFP   = "#d35400"  # помаранчевий — LiFePO4
C_LTO   = FIELD      # зелений — LTO
C_ALK   = "#7f8c8d"  # сірий — Alkaline


# ── 1. Перехідний процес просідання напруги та TMV ───────────────────────────
def fig_voltage_sag_transient():
    """Динаміка напруги під час імпульсу струму передавача (RF TX):
    порівняння пасивованої Li-SOCl2 (глибокий провал TMV нижче порогу Brownout),
    активної батареї та гібридної системи Li-SOCl2 + HLC."""
    W, H = 840, 480
    f = [text(W / 2, 26, "Динамічне просідання напруги під час імпульсу радіопередавача", size=16, bold=True)]
    
    ox, oy = 90, 390
    pw, ph = 700, 310
    
    # Осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    f.append(text(ox + pw / 2, oy + 40, "Час від початку імпульсу передавача (t) →", size=11, color=MUTED))
    
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">Напруга живлення V_bat (В)</text>'
             % (ox - 48, oy - ph / 2, FONT, MUTED, ox - 48, oy - ph / 2))
    
    # Шкала напруги: 0..4.0 В
    def vy(v):
        return oy - (v / 4.0) * ph
    
    for v in [1.5, 2.0, 2.5, 3.0, 3.6]:
        y_val = vy(v)
        f.append(line(ox - 5, y_val, ox + pw, y_val, color="#e5e7eb", sw=1, dash="4 4"))
        f.append(text(ox - 10, y_val + 4, "%.1f В" % v, size=10, color=MUTED, anchor="end"))
    
    # Позначення імпульсу навантаження (фонова область)
    tx_start, tx_end = ox + 100, ox + 430
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fef3c7" fill-opacity="0.35"/>'
             % (tx_start, oy - ph, tx_end - tx_start, ph))
    f.append(line(tx_start, oy - ph, tx_start, oy, color="#d97706", sw=1.2, dash="3 3"))
    f.append(line(tx_end, oy - ph, tx_end, oy, color="#d97706", sw=1.2, dash="3 3"))
    f.append(text((tx_start + tx_end) / 2, oy - ph + 18, "TX Burst (100–500 мА)", size=10.5, color="#b45309", bold=True))
    
    # Поріг перезавантаження МК (Brownout Reset = 2.0 В)
    y_bor = vy(2.0)
    f.append(line(ox, y_bor, ox + pw, y_bor, color=POS, sw=1.6, dash="5 4"))
    f.append(text(ox + pw - 10, y_bor - 8, "Поріг скидання МК (Brownout = 2.0 В)", size=10, color=POS, bold=True, anchor="end"))
    
    # Крива 1: Пасивована Li-SOCl2
    pts_pass = [
        (ox, vy(3.65)),
        (tx_start, vy(3.65)),
        (tx_start + 14, vy(1.60)),  # TMV провал!
        (tx_start + 70, vy(2.15)),
        (tx_start + 200, vy(2.70)),
        (tx_end, vy(2.85)),
        (tx_end + 15, vy(3.55)),
        (ox + pw, vy(3.65))
    ]
    p_pass = " ".join("%.1f,%.1f" % (x, y) for x, y in pts_pass)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-linejoin="round"/>' % (p_pass, C_SOCL2))
    
    # Точка TMV і винесений напис знизу
    tmv_x, tmv_y = tx_start + 14, vy(1.60)
    f.append(circle(tmv_x, tmv_y, 5, fill=POS, stroke=POS, sw=1))
    f.append(fitbox(tmv_x + 10, tmv_y + 14, 210, 24, "TMV (1.6 В): Скидання МК!", size=9.5, fill="#fdecea", stroke=POS, sw=1.1, bold=True))
    
    # Крива 2: Свіжа / депасивована Li-SOCl2
    pts_act = [
        (ox, vy(3.65)),
        (tx_start, vy(3.65)),
        (tx_start + 10, vy(2.95)),
        (tx_end, vy(2.88)),
        (tx_end + 10, vy(3.63)),
        (ox + pw, vy(3.65))
    ]
    p_act = " ".join("%.1f,%.1f" % (x, y) for x, y in pts_act)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round" stroke-dasharray="4 3"/>' % (p_act, C_MNO2))
    
    # Крива 3: Гібрид Li-SOCl2 + HLC
    pts_hlc = [
        (ox, vy(3.65)),
        (tx_start, vy(3.65)),
        (tx_start + 10, vy(3.45)),
        (tx_end, vy(3.38)),
        (tx_end + 10, vy(3.62)),
        (ox + pw, vy(3.65))
    ]
    p_hlc = " ".join("%.1f,%.1f" % (x, y) for x, y in pts_hlc)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % (p_hlc, FIELD))
    
    # Легенда у верхньому правому куті (праворуч від tx_end = ox + 430 = 520)
    lx, ly = ox + 445, oy - ph + 10
    f.append(rect(lx, ly, 245, 68, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6))
    leg_items = [
        ("Li-SOCl₂ пасивована (TMV провал)", C_SOCL2, None),
        ("Li-SOCl₂ депасивована (R_int)", C_MNO2, "4 3"),
        ("Li-SOCl₂ + HLC (стабільна шина)", FIELD, None)
    ]
    for i, (name, col, dash) in enumerate(leg_items):
        yy = ly + 14 + i * 19
        f.append(line(lx + 8, yy, lx + 30, yy, color=col, sw=2.5, dash=dash))
        f.append(text(lx + 36, yy + 3, name, size=9.5, color=col, bold=True, anchor="start"))
    
    # Підсумковий блок
    f.append(fitbox(ox, oy + 54, pw, 28,
                    "TMV (Transient Minimum Voltage) виникає в перші мілісекунди імпульсу; гібридний конденсатор HLC зрізає пік струму з батареї.",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.3))
    
    render(os.path.join(IMG, "voltage-sag-transient.svg"), W, H, *f)


# ── 2. Механізм пасивації: кристал LiCl на літієвому аноді ───────────────────
def fig_passivation_mechanism():
    """Схематичне зображення росту плівки LiCl на літієвому аноді та її руйнування:
    1) Свіжий літій контактує з SOCl2;
    2) Формування щільного шару кристалів LiCl (пасивація);
    3) Розчинення та механічний пробій шару під час депасиваційного струму."""
    W, H = 820, 360
    f = [text(W / 2, 28, "Хімічний механізм пасивації літієвого анода плівкою LiCl", size=16, bold=True)]
    
    cards = [
        ("1. Початок реакції", "Свіжий Li контактує з SOCl₂.\nМиттєве окиснення:\n4Li + 2SOCl₂ → 4LiCl + S + SO₂", "#eef2ff", NEG),
        ("2. Шар пасивації (LiCl)", "Кристали LiCl утворюють плівку.\nІони Li⁺ блокуються, R_int > 100 Ом.\nСаморозряд падає до < 1%/рік!", "#fdf4ff", C_SOCL2),
        ("3. Депасивація струмом", "Струм руйнує шар LiCl.\nКристали розчиняються.\nВнутрішній опір падає до норми.", "#ecfdf5", FIELD)
    ]
    
    cw = 240
    gap = 20
    x0 = (W - 3 * cw - 2 * gap) / 2
    cy = 60
    ch = 250
    
    for i, (title, desc, bg_col, border_col) in enumerate(cards):
        cx = x0 + i * (cw + gap)
        f.append(rect(cx, cy, cw, ch, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        f.append(text(cx + cw / 2, cy + 24, title, size=13, color=border_col, bold=True))
        
        # Схематичний рисунок шарів усередині картки
        sx, sy, sw_box, sh_box = cx + 15, cy + 45, cw - 30, 95
        f.append(rect(sx, sy, sw_box, sh_box, fill="#ffffff", stroke="#cbd5e1", sw=1.2))
        
        # Електроліт
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e0f2fe"/>' % (sx, sy, sw_box, 45))
        f.append(text(sx + sw_box / 2, sy + 22, "Рідкий католіт SOCl₂", size=10, color="#0369a1"))
        
        # Металевий літій (анод)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#94a3b8"/>' % (sx, sy + 55, sw_box, 40))
        f.append(text(sx + sw_box / 2, sy + 80, "Металевий Li (анод)", size=10, color="#1e293b", bold=True))
        
        # Проміжний шар (LiCl)
        if i == 0:
            for k in range(5):
                kx = sx + 20 + k * 38
                f.append(circle(kx, sy + 50, 4, fill=C_SOCL2, stroke="#4a044e", sw=1))
        elif i == 1:
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="#4a044e" stroke-width="1.2"/>'
                     % (sx, sy + 43, sw_box, 14, C_SOCL2))
            f.append(text(sx + sw_box / 2, sy + 54, "Плівка LiCl (бар'єр)", size=9.5, color="#ffffff", bold=True))
        elif i == 2:
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="#4a044e" stroke-width="1" stroke-dasharray="6 3"/>'
                     % (sx, sy + 45, sw_box, 10, C_SOCL2))
            for k in range(3):
                kx = sx + 30 + k * 65
                f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                         % (kx, sy + 65, kx, sy + 25, FIELD))
                f.append(text(kx + 12, sy + 38, "Li⁺", size=9.5, color=FIELD, bold=True))
        
        # Текстовий опис
        f.append(mtext(cx + cw / 2, cy + 165, desc, size=10.5, color=INK, lh=1.35))
    
    render(os.path.join(IMG, "passivation-mechanism.svg"), W, H, *f)


# ── 3. Бобінна проти спіральної конструкції ───────────────────────────────────
def fig_bobbin_vs_spiral():
    """Порівняння внутрішньої геометрії та характеристик:
    Бобінна (Bobbin — циліндричний стрижень, висока ємність, малий струм) vs
    Спіральна (Spiral — намотка рулетом, велика площа, високий імпульсний струм)."""
    W, H = 820, 390
    f = [text(W / 2, 28, "Конструкція циліндричних елементів: Бобінна проти Спіральної", size=16, bold=True)]
    
    # Ліва панель: Бобінна (Bobbin)
    bx0, by0, bw, bh = 40, 55, 350, 310
    f.append(rect(bx0, by0, bw, bh, fill="#f8fafc", stroke=C_SOCL2, sw=1.8, rx=8))
    f.append(text(bx0 + bw / 2, by0 + 24, "Бобінна конструкція (Bobbin)", size=14, color=C_SOCL2, bold=True))
    f.append(text(bx0 + bw / 2, by0 + 42, "Максимальна ємність під мікроструми", size=10.5, color=MUTED, italic=True))
    
    # Рисунок бобінного зрізу
    cx_b, cy_b = bx0 + 90, by0 + 130
    f.append(circle(cx_b, cy_b, 55, fill="#94a3b8", stroke="#475569", sw=2))
    f.append(circle(cx_b, cy_b, 42, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    f.append(circle(cx_b, cy_b, 20, fill="#334155", stroke="#0f172a", sw=1.5))
    f.append(text(cx_b, cy_b + 4, "Катод", size=9.5, color="#ffffff", bold=True))
    f.append(text(cx_b + 58, cy_b - 35, "Li анод на стінці", size=9.5, color="#475569", anchor="start"))
    f.append(text(cx_b + 46, cy_b + 35, "Площа контакту мала (~10 см²)", size=9.5, color=C_SOCL2, bold=True, anchor="start"))
    
    traits_b = [
        "• Питома енергія: до 650–700 Вт·год/кг",
        "• Саморозряд: < 1% на рік (до 20 років)",
        "• Неперервний струм: 2–10 мА",
        "• Максимальний імпульс: 20–50 мА",
        "• Схильність до пасивації: висока"
    ]
    for k, tr in enumerate(traits_b):
        f.append(text(bx0 + 20, by0 + 215 + k * 18, tr, size=10.5, color=INK, anchor="start"))
    
    # Права панель: Спіральна (Spiral)
    sx0 = 430
    f.append(rect(sx0, by0, bw, bh, fill="#f8fafc", stroke=C_MNO2, sw=1.8, rx=8))
    f.append(text(sx0 + bw / 2, by0 + 24, "Спіральна конструкція (Spiral)", size=14, color=C_MNO2, bold=True))
    f.append(text(sx0 + bw / 2, by0 + 42, "Велика площа під імпульси в ампери", size=10.5, color=MUTED, italic=True))
    
    cx_s, cy_s = sx0 + 90, by0 + 130
    f.append(circle(cx_s, cy_s, 55, fill="#f1f5f9", stroke="#475569", sw=2))
    for r in [12, 22, 32, 42, 50]:
        f.append(circle(cx_s, cy_s, r, fill="none", stroke=(C_MNO2 if r % 20 == 2 else "#94a3b8"), sw=2))
    f.append(text(cx_s + 58, cy_s - 35, "Намотка рулетом (jelly roll)", size=9.5, color="#475569", anchor="start"))
    f.append(text(cx_s + 58, cy_s - 15, "Анод + Сепаратор + Катод", size=9.5, color=MUTED, anchor="start"))
    f.append(text(cx_s + 46, cy_s + 35, "Площа контакту велика (~150 см²)", size=9.5, color=C_MNO2, bold=True, anchor="start"))
    
    traits_s = [
        "• Питома енергія: ~400–450 Вт·год/кг (−30%)",
        "• Саморозряд: 2–3% на рік (5–10 років)",
        "• Неперервний струм: 500–1000 мА",
        "• Максимальний імпульс: 2000–3000 мА (до 3 А)",
        "• Схильність до пасивації: низька"
    ]
    for k, tr in enumerate(traits_s):
        f.append(text(sx0 + 20, by0 + 215 + k * 18, tr, size=10.5, color=INK, anchor="start"))
    
    render(os.path.join(IMG, "bobbin-vs-spiral.svg"), W, H, *f)


# ── 4. Схема гібридного вузла: Li-SOCl2 + HLC / суперконденсатор ──────────────
def fig_hlc_hybrid_circuit():
    """Схемотехніка паралельного з'єднання Li-SOCl2 та гібридного конденсатора (HLC):
    розподіл струмів під час глибокого сну (підзаряд HLC мікрострумом)
    та під час радіопередачі (HLC живить TX burst без участі високого R_int батареї)."""
    W, H = 820, 420
    f = [text(W / 2, 28, "Архітектура живлення: Батарея Li-SOCl₂ паралельно з HLC / Supercap", size=16, bold=True)]
    
    cx0, cy0, cw, ch = 40, 60, 420, 330
    f.append(rect(cx0, cy0, cw, ch, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(cx0 + cw / 2, cy0 + 24, "Еквівалентна схема підключення", size=13, color=INK, bold=True))
    
    f.append(line(cx0 + 40, cy0 + 70, cx0 + 380, cy0 + 70, color=POS, sw=2.2))
    f.append(text(cx0 + 385, cy0 + 74, "VCC", size=11, color=POS, bold=True, anchor="start"))
    
    f.append(line(cx0 + 40, cy0 + 270, cx0 + 380, cy0 + 270, color=LINE, sw=2.2))
    f.append(text(cx0 + 385, cy0 + 274, "GND", size=11, color=LINE, bold=True, anchor="start"))
    
    # Гілка 1: Li-SOCl2
    bx = cx0 + 90
    f.append(line(bx, cy0 + 70, bx, cy0 + 100, color=POS, sw=1.6))
    f.append(rect(bx - 20, cy0 + 100, 40, 25, fill="#f8fafc", stroke=C_SOCL2, sw=1.5))
    f.append(text(bx, cy0 + 116, "R_int", size=9.5, color=C_SOCL2, bold=True))
    f.append(line(bx, cy0 + 125, bx, cy0 + 150, color=LINE, sw=1.6))
    
    f.append(line(bx - 18, cy0 + 150, bx + 18, cy0 + 150, color=POS, sw=2.5))
    f.append(line(bx - 10, cy0 + 158, bx + 10, cy0 + 158, color=LINE, sw=2.5))
    f.append(line(bx - 18, cy0 + 166, bx + 18, cy0 + 166, color=POS, sw=2.5))
    f.append(line(bx - 10, cy0 + 174, bx + 10, cy0 + 174, color=LINE, sw=2.5))
    f.append(text(bx, cy0 + 196, "Li-SOCl₂", size=10.5, color=C_SOCL2, bold=True))
    f.append(text(bx, cy0 + 210, "3.6 В (первинна)", size=9.5, color=MUTED))
    f.append(line(bx, cy0 + 174, bx, cy0 + 270, color=LINE, sw=1.6))
    
    # Гілка 2: HLC
    hx = cx0 + 220
    f.append(line(hx, cy0 + 70, hx, cy0 + 100, color=POS, sw=1.6))
    f.append(rect(hx - 20, cy0 + 100, 40, 25, fill="#ecfdf5", stroke=FIELD, sw=1.5))
    f.append(text(hx, cy0 + 116, "ESR<0.1Ω", size=9.5, color=FIELD, bold=True))
    f.append(line(hx, cy0 + 125, hx, cy0 + 150, color=LINE, sw=1.6))
    
    f.append(line(hx - 16, cy0 + 150, hx + 16, cy0 + 150, color=FIELD, sw=2.5))
    f.append(line(hx - 16, cy0 + 158, hx + 16, cy0 + 158, color=FIELD, sw=2.5))
    f.append(text(hx, cy0 + 182, "HLC / Supercap", size=10.5, color=FIELD, bold=True))
    f.append(text(hx, cy0 + 196, "10–100 Фарадей", size=9.5, color=MUTED))
    f.append(line(hx, cy0 + 158, hx, cy0 + 270, color=LINE, sw=1.6))
    
    # Гілка 3: Навантаження
    lx = cx0 + 340
    f.append(line(lx, cy0 + 70, lx, cy0 + 130, color=POS, sw=1.6))
    f.append(rect(lx - 30, cy0 + 130, 60, 60, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(lx, cy0 + 155, "MCU + RF", size=10.5, color="#b45309", bold=True))
    f.append(text(lx, cy0 + 172, "LoRa/NB-IoT", size=9.5, color="#b45309"))
    f.append(line(lx, cy0 + 190, lx, cy0 + 270, color=LINE, sw=1.6))
    
    # Права частина: Текстовий блок
    rx0, ry0, rw, rh = 480, 60, 300, 330
    f.append(rect(rx0, ry0, rw, rh, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(rx0 + rw / 2, ry0 + 24, "Розподіл фаз струму", size=13, color=INK, bold=True))
    
    f.append(fitbox(rx0 + 15, ry0 + 45, rw - 30, 110,
                    "Фаза 1: Глибокий сон (99.9% часу)\n"
                    "• Навантаження споживає ~2–5 мкА.\n"
                    "• Батарея плавно підзаряджає HLC до 3.6 В.\n"
                    "• Струм батареї мізерний, пасивація під контролем.",
                    size=10, fill="#eff6ff", stroke=C_MNO2, sw=1.2))
    
    f.append(fitbox(rx0 + 15, ry0 + 170, rw - 30, 130,
                    "Фаза 2: Радіопередача TX (100–500 мс)\n"
                    "• Стрибок струму до 150–2000 мА.\n"
                    "• 98% струму миттєво віддає HLC з ультранизьким ESR.\n"
                    "• Батарея не бачить перевантаження, напруга VCC тримається стабільною.",
                    size=10, fill="#fef2f2", stroke=POS, sw=1.2))
    
    render(os.path.join(IMG, "hlc-hybrid-circuit.svg"), W, H, *f)


# ── 5. Матриця вибору хімії джерела живлення ─────────────────────────────────
def fig_chemistry_selection_matrix():
    """Зведена матриця прийняття рішень:
    2D простір (Питома енергія проти Імпульсної навантажувальної здатності)
    з колірними зонами застосування та ключовими хіміями."""
    W, H = 840, 470
    f = [text(W / 2, 28, "Матриця вибору хімії під профіль струму та умови експлуатації", size=16, bold=True)]
    
    ox, oy = 100, 400
    pw, ph = 690, 330
    
    # Осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    f.append(text(ox + pw / 2, oy + 40, "Імпульсна навантажувальна здатність (C-Rate / Піковий струм) →", size=11, color=MUTED))
    
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">Питома енергія (Вт·год/кг) →</text>'
             % (ox - 48, oy - ph / 2, FONT, MUTED, ox - 48, oy - ph / 2))
    
    cells = [
        (ox + 30,  oy - 310, 160, 80, "Li-SOCl₂ (Bobbin)", "650 Вт·год/кг | < 0.05C\n10–20 років, лічильники\nПотрібна депасивація / HLC", C_SOCL2),
        (ox + 230, oy - 240, 170, 80, "Li-SOCl₂ (Spiral) /\nLi-MnO₂ (CR123A)", "400 Вт·год/кг | 1C–3C\nДатчики LoRaWAN, дим, газ\nПомірний саморозряд", C_MNO2),
        (ox + 450, oy - 280, 190, 80, "Li-Ion / Li-Po (NMC)", "220 Вт·год/кг | 1C–5C\nНосимі гаджети, дрони\nЗаряд лише 0..+45 °C!", C_LION),
        (ox + 450, oy - 170, 190, 75, "LiFePO₄ (LFP)", "120 Вт·год/кг | 3C–10C\n3000+ циклів, безпека\nСонячні вузли, автономки", C_LFP),
        (ox + 470, oy - 80,  180, 70, "LTO (Титанат)", "70 Вт·год/кг | 10C–30C\n20000+ циклів, заряд при -30 °C\nЕкстремальний холод", C_LTO),
        (ox + 30,  oy - 115, 160, 70, "Alkaline (Zn-MnO₂)", "90 Вт·год/кг | < 0.2C\nДешеві побутові пульти\nВисокий R_int на холоді", C_ALK)
    ]
    
    for cx, cy, cw, ch, name, note, col in cells:
        f.append(rect(cx, cy, cw, ch, fill="#ffffff", stroke=col, sw=2, rx=6))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="%s" fill-opacity="0.12"/>'
                 % (cx, cy, cw, ch, col))
        f.append(text(cx + cw / 2, cy + 20, name, size=11, color=col, bold=True))
        f.append(mtext(cx + cw / 2, cy + 38, note, size=9.5, color=INK, lh=1.3))
    
    # Розділові зони
    f.append(line(ox + 210, oy, ox + 210, oy - ph, color="#cbd5e1", sw=1, dash="4 4"))
    f.append(text(ox + 105, oy - ph + 16, "Мікроструми (IoT sleep)", size=9.5, color=MUTED))
    f.append(text(ox + 320, oy - ph + 16, "Середні імпульси (RF)", size=9.5, color=MUTED))
    f.append(text(ox + 555, oy - ph + 16, "Високі струми (GSM / Двигуни)", size=9.5, color=MUTED))
    
    render(os.path.join(IMG, "chemistry-selection-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_voltage_sag_transient()
    fig_passivation_mechanism()
    fig_bobbin_vs_spiral()
    fig_hlc_hybrid_circuit()
    fig_chemistry_selection_matrix()
    print("OK: 5 figures ->", IMG)
