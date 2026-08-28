# -*- coding: utf-8 -*-
"""Фігури для теми smd-stencil (трафаретний друк паяльної пасти).
Генерує 2 SVG-діаграми:
1. stencil-area-ratio-geometry.svg — геометрія апертури трафарету та розрахунок Area Ratio за IPC-7525.
2. solder-paste-rheology-squeegee.svg — реологія пасти, рух ракеля та гідродинаміка валика пасти.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра стандарту
COPPER      = "#b5763a"
COPPER_FILL = "#f5e6d3"
STENCIL     = "#4a5568"
STENCIL_BG  = "#edf2f7"
SOLDER      = "#475569"
SOLDER_FILL = "#cbd5e1"
PASTE_ROLL  = "#94a3b8"
FORCE_PAD   = "#16a34a"
FORCE_WALL  = "#dc2626"
FR4_FILL    = "#e2e8f0"
FR4_STROKE  = "#94a3b8"
NANO_COAT   = "#0284c7"
SQUEEGEE    = "#334155"


def poly(pts, fill="none", stroke=LINE, sw=1.5):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'


# ── 1. Геометрія апертури: Area Ratio та баланс сил ───────────────────────────
def fig_area_ratio_geometry():
    W, H = 880, 560
    frags = []

    # Фонова панель
    frags.append(rect(10, 10, 860, 540, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))

    # Заголовок
    frags.append(text(440, 34, "Геометрія апертури трафарету та баланс сил вивільнення пасти за IPC-7525", size=15, color=INK, bold=True))

    # ── Ліва секція: Тривимірна ізометрія апертури ──
    frags.append(rect(25, 55, 435, 480, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(40, 78, "Ізометрична модель прямокутної апертури", size=12, color=MUTED, anchor="start", bold=True))

    # Верхня площина трафарету
    frags.append(poly([
        (50, 200), (220, 130), (430, 170), (260, 240)
    ], fill="#e2e8f0", stroke=STENCIL, sw=1.5))

    # Вікно апертури на верхній площині
    ap_top = [(140, 195), (240, 160), (320, 180), (220, 215)]
    frags.append(poly(ap_top, fill="#f1f5f9", stroke=STENCIL, sw=1.2))

    # Товщина фольги трафарету (опускання вниз на T_pix = 80)
    T_pix = 80
    # Бічні стінки апертури
    # Ліва стінка
    frags.append(poly([
        (140, 195), (220, 215), (220, 215 + T_pix), (140, 195 + T_pix)
    ], fill="#fee2e2", stroke=FORCE_WALL, sw=1.2))
    # Задня стінка (права внутрішня)
    frags.append(poly([
        (220, 215), (320, 180), (320, 180 + T_pix), (220, 215 + T_pix)
    ], fill="#fecaca", stroke=FORCE_WALL, sw=1.2))

    # Нижня основа апертури (контактна площадка плати)
    ap_bot = [(140, 195 + T_pix), (240, 160 + T_pix), (320, 180 + T_pix), (220, 215 + T_pix)]
    frags.append(poly(ap_bot, fill=COPPER_FILL, stroke=COPPER, sw=1.8))
    frags.append(text(230, 210 + T_pix, "Площа площадки A_pad = W × L", size=11, color=COPPER, bold=True))

    # Нанопокриття на нижній площині трафарету (синя лінія)
    frags.append(line(48, 200 + T_pix, 260, 240 + T_pix, color=NANO_COAT, sw=3.0))
    frags.append(line(260, 240 + T_pix, 430, 170 + T_pix, color=NANO_COAT, sw=3.0))
    frags.append(text(330, 255 + T_pix, "Гідрофобне нанопокриття (2-10 нм)", size=10, color=NANO_COAT, bold=True))

    # Вектори сил
    # Сила адгезії до площадки (вниз F_pad)
    frags.append(line(230, 220 + T_pix, 230, 275 + T_pix, color=FORCE_PAD, sw=2.5))
    frags.append(poly([(226, 273 + T_pix), (234, 273 + T_pix), (230, 285 + T_pix)], fill=FORCE_PAD, stroke=FORCE_PAD))
    frags.append(text(230, 298 + T_pix, "F_pad (Адгезія до міді)", size=11, color=FORCE_PAD, bold=True))

    # Сили тертя об стінки (вгору F_wall)
    frags.append(line(175, 235, 175, 195, color=FORCE_WALL, sw=2.0))
    frags.append(poly([(172, 197), (178, 197), (175, 187)], fill=FORCE_WALL, stroke=FORCE_WALL))
    frags.append(text(125, 225, "F_wall", size=11, color=FORCE_WALL, bold=True))

    frags.append(line(275, 225, 275, 185, color=FORCE_WALL, sw=2.0))
    frags.append(poly([(272, 187), (278, 187), (275, 177)], fill=FORCE_WALL, stroke=FORCE_WALL))
    frags.append(text(290, 215, "F_wall", size=11, color=FORCE_WALL, bold=True))

    # Розмірні стрілки W, L, T
    frags.append(line(130, 190, 210, 220, color=MUTED, sw=1.0))
    frags.append(text(160, 212, "W", size=11, color=MUTED, bold=True))

    frags.append(line(230, 222, 330, 187, color=MUTED, sw=1.0))
    frags.append(text(285, 210, "L", size=11, color=MUTED, bold=True))

    frags.append(line(45, 200, 45, 200 + T_pix, color=MUTED, sw=1.2))
    frags.append(line(40, 200, 50, 200, color=MUTED, sw=1.0))
    frags.append(line(40, 200 + T_pix, 50, 200 + T_pix, color=MUTED, sw=1.0))
    frags.append(text(35, 200 + T_pix / 2 + 4, "T", size=11, color=MUTED, bold=True, anchor="end"))

    # Пояснення знизу зліва
    box_w, box_h = 405, 100
    frags.append(rect(40, 420, box_w, box_h, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(50, 440, "Умова успішного вивільнення пасти:", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(50, 460, "F_pad > F_wall  ⇒  A_pad · σ_pad > A_walls · τ_wall", size=11, color=FORCE_PAD, anchor="start", bold=True))
    frags.append(text(50, 480, "Площа стінок: A_walls = 2 · (W + L) · T", size=10, color=MUTED, anchor="start"))
    frags.append(text(50, 502, "Площа площадки: A_pad = W · L", size=10, color=MUTED, anchor="start"))

    # ── Права секція: Математика та критерії IPC-7525 ──
    frags.append(rect(475, 55, 380, 480, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(490, 78, "Критерії та пороги стандарту IPC-7525", size=12, color=MUTED, anchor="start", bold=True))

    # Картка 1: Area Ratio прямокутник
    frags.append(rect(490, 95, 350, 90, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(505, 115, "1. Area Ratio (Прямокутна апертура)", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(505, 137, "AR = (W · L) / [ 2 · (W + L) · T ] ≥ 0.66", size=11, color=FORCE_PAD, anchor="start", bold=True))
    frags.append(text(505, 157, "Стандартна фольга без покриття: AR ≥ 0.66", size=10, color=MUTED, anchor="start"))
    frags.append(text(505, 172, "З нанопокриттям (Nano-coating): AR ≥ 0.50–0.55", size=10, color=NANO_COAT, anchor="start", bold=True))

    # Картка 2: Area Ratio коло / квадрат
    frags.append(rect(490, 195, 350, 80, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(505, 215, "2. Area Ratio (Кругла апертура BGA / CSP)", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(505, 237, "AR = D / (4 · T) ≥ 0.66", size=11, color=FORCE_PAD, anchor="start", bold=True))
    frags.append(text(505, 258, "де D — діаметр апертури, T — товщина фольги", size=10, color=MUTED, anchor="start"))

    # Картка 3: Aspect Ratio
    frags.append(rect(490, 285, 350, 70, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(505, 305, "3. Aspect Ratio (Коефіцієнт пропорції)", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(505, 327, "AS = W / T ≥ 1.50", size=11, color=FORCE_PAD, anchor="start", bold=True))
    frags.append(text(505, 344, "де W — ширина вузького боку апертури", size=10, color=MUTED, anchor="start"))

    # Картка 4: Графік Transfer Efficiency vs Area Ratio
    frags.append(rect(490, 365, 350, 155, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(505, 385, "Transfer Efficiency (TE) vs Area Ratio", size=11, color=INK, anchor="start", bold=True))

    # Осі графіка
    gx0, gy0, gw, gh = 530, 485, 280, 80
    frags.append(line(gx0, gy0, gx0 + gw, gy0, color=MUTED, sw=1.0))
    frags.append(line(gx0, gy0, gx0, gy0 - gh, color=MUTED, sw=1.0))
    frags.append(text(gx0 + gw - 10, gy0 + 15, "AR", size=10, color=MUTED, bold=True))
    frags.append(text(gx0 - 15, gy0 - gh + 10, "TE %", size=10, color=MUTED, bold=True))

    # Крива без покриття (сталь)
    frags.append((
        f'<path d="M {gx0} {gy0} '
        f'Q {gx0 + 60} {gy0 - 10}, {gx0 + 110} {gy0 - 25} '
        f'T {gx0 + 160} {gy0 - 65} '
        f'L {gx0 + gw - 20} {gy0 - 70}" '
        f'fill="none" stroke="{FORCE_WALL}" stroke-width="2.0"/>'
    ))

    # Крива з нанопокриттям
    frags.append((
        f'<path d="M {gx0} {gy0 - 10} '
        f'Q {gx0 + 50} {gy0 - 30}, {gx0 + 100} {gy0 - 60} '
        f'T {gx0 + 160} {gy0 - 72} '
        f'L {gx0 + gw - 20} {gy0 - 74}" '
        f'fill="none" stroke="{NANO_COAT}" stroke-width="2.0" stroke-dasharray="4,2"/>'
    ))

    # Лінія порогу AR = 0.66
    thresh_x = gx0 + 130
    frags.append(line(thresh_x, gy0, thresh_x, gy0 - gh + 5, color=FORCE_PAD, sw=1.2, dash="3,2"))
    frags.append(text(thresh_x, gy0 + 15, "0.66", size=9, color=FORCE_PAD, bold=True))
    frags.append(text(thresh_x - 35, gy0 - 72, "Повна передача >85%", size=9, color=FORCE_PAD))

    # Легенда
    frags.append(line(gx0 + 10, gy0 - 65, gx0 + 35, gy0 - 65, color=FORCE_WALL, sw=2.0))
    frags.append(text(gx0 + 40, gy0 - 62, "Лазерна сталь", size=9, color=FORCE_WALL, anchor="start"))
    frags.append(line(gx0 + 10, gy0 - 52, gx0 + 35, gy0 - 52, color=NANO_COAT, sw=2.0, dash="4,2"))
    frags.append(text(gx0 + 40, gy0 - 49, "З нанопокриттям", size=9, color=NANO_COAT, anchor="start"))

    render(os.path.join(OUT, "stencil-area-ratio-geometry.svg"), W, H, *frags)
    print("Generated stencil-area-ratio-geometry.svg")


# ── 2. Реологія пасти та гідродинаміка ракеля ─────────────────────────────────
def fig_solder_paste_rheology():
    W, H = 880, 560
    frags = []

    # Фонова панель
    frags.append(rect(10, 10, 860, 540, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))

    # Заголовок
    frags.append(text(440, 34, "Гідродинаміка ракеля та тиксотропна реологія паяльної пасти під час друку", size=15, color=INK, bold=True))

    # ── Ліва секція: Механіка руху ракеля та заповнення апертури ──
    frags.append(rect(25, 55, 475, 480, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(40, 78, "Гідродинамічний валик пасти (Paste Roll) та заповнення апертури", size=12, color=MUTED, anchor="start", bold=True))

    # Базові шари: Друкована плата (FR-4)
    pcb_y = 380
    frags.append(rect(40, pcb_y, 445, 30, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    frags.append(text(120, pcb_y + 19, "Друкована плата (PCB Substrate)", size=10, color=MUTED))

    # Мідні контактні площадки на платі
    frags.append(rect(70, pcb_y - 6, 80, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.2))
    frags.append(rect(200, pcb_y - 6, 80, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.2))
    frags.append(rect(340, pcb_y - 6, 80, 6, fill=COPPER_FILL, stroke=COPPER, sw=1.2))

    # Трафарет (Фольга 120 мкм)
    st_y = pcb_y - 30
    st_h = 24
    # Ліва частина трафарету
    frags.append(rect(40, st_y, 160, st_h, fill=STENCIL_BG, stroke=STENCIL, sw=1.5))
    # Середня частина трафарету
    frags.append(rect(280, st_y, 60, st_h, fill=STENCIL_BG, stroke=STENCIL, sw=1.5))
    # Права частина трафарету
    frags.append(rect(420, st_y, 65, st_h, fill=STENCIL_BG, stroke=STENCIL, sw=1.5))

    frags.append(text(100, st_y + 16, "Трафарет (Фольга)", size=10, color=STENCIL, bold=True))

    # Відбиток пасти в уже пройденій апертурі ліворуч (залишається після ракеля)
    frags.append(rect(70, st_y, 80, st_h, fill=SOLDER_FILL, stroke=SOLDER, sw=1.2))
    frags.append(text(110, st_y - 8, "Заповнена паста", size=9, color=SOLDER, bold=True))

    # Лезо ракеля (Squeegee Blade)
    sq_tip_x, sq_tip_y = 300, st_y
    sq_path = (
        f'<path d="M {sq_tip_x} {sq_tip_y} '
        f'L {sq_tip_x - 70} {sq_tip_y - 140} '
        f'L {sq_tip_x - 55} {sq_tip_y - 145} '
        f'L {sq_tip_x + 10} {sq_tip_y - 10} Z" '
        f'fill="{SQUEEGEE}" stroke="#1e293b" stroke-width="1.5"/>'
    )
    frags.append(sq_path)
    frags.append(text(sq_tip_x - 70, sq_tip_y - 152, "Сталевий ракель (Squeegee)", size=11, color=INK, bold=True))

    # Кут атаки 60 градусів
    frags.append(line(sq_tip_x, sq_tip_y, sq_tip_x - 50, sq_tip_y, color=MUTED, sw=1.0, dash="3,2"))
    frags.append(line(sq_tip_x, sq_tip_y, sq_tip_x - 35, sq_tip_y - 70, color=MUTED, sw=1.0, dash="3,2"))
    frags.append(text(sq_tip_x - 30, sq_tip_y - 15, "α = 60°", size=10, color=MUTED, bold=True))

    # Вектор швидкості друку (V_print)
    frags.append(line(sq_tip_x - 10, sq_tip_y - 100, sq_tip_x + 60, sq_tip_y - 100, color=FORCE_PAD, sw=2.5))
    frags.append(poly([(sq_tip_x + 58, sq_tip_y - 104), (sq_tip_x + 58, sq_tip_y - 96), (sq_tip_x + 68, sq_tip_y - 100)], fill=FORCE_PAD, stroke=FORCE_PAD))
    frags.append(text(sq_tip_x + 25, sq_tip_y - 108, "V_print (20–100 мм/с)", size=10, color=FORCE_PAD, bold=True))

    # Вектор тиску ракеля (F_down)
    frags.append(line(sq_tip_x - 40, sq_tip_y - 120, sq_tip_x - 15, sq_tip_y - 70, color=FORCE_WALL, sw=2.5))
    frags.append(poly([(sq_tip_x - 20, sq_tip_y - 68), (sq_tip_x - 10, sq_tip_y - 74), (sq_tip_x - 12, sq_tip_y - 64)], fill=FORCE_WALL, stroke=FORCE_WALL))
    frags.append(text(sq_tip_x - 65, sq_tip_y - 85, "Тиск P", size=10, color=FORCE_WALL, bold=True))

    # Валик пасти перед ракелем (Paste Roll з вихором)
    frags.append((
        f'<path d="M {sq_tip_x} {sq_tip_y} '
        f'Q {sq_tip_x + 70} {sq_tip_y - 15}, {sq_tip_x + 80} {sq_tip_y - 75} '
        f'Q {sq_tip_x + 40} {sq_tip_y - 120}, {sq_tip_x - 15} {sq_tip_y - 60} Z" '
        f'fill="{PASTE_ROLL}" stroke="{SOLDER}" stroke-width="1.5"/>'
    ))

    # Вихор циркуляції всередині валика
    frags.append((
        f'<path d="M {sq_tip_x + 45} {sq_tip_y - 45} '
        f'A 22 22 0 1 1 {sq_tip_x + 35} {sq_tip_y - 75}" '
        f'fill="none" stroke="#ffffff" stroke-width="2.0" stroke-dasharray="3,2"/>'
    ))
    frags.append(poly([(sq_tip_x + 32, sq_tip_y - 78), (sq_tip_x + 38, sq_tip_y - 70), (sq_tip_x + 42, sq_tip_y - 80)], fill="#ffffff", stroke="#ffffff"))
    frags.append(text(sq_tip_x + 40, sq_tip_y - 50, "Кочення валика", size=9, color="#ffffff", bold=True))

    # Заповнення поточної апертури під ракелем (Апертура 200..280)
    frags.append(rect(200, st_y, 80, st_h, fill=SOLDER_FILL, stroke=FORCE_PAD, sw=1.8))
    frags.append(text(240, st_y + 15, "Заповнення", size=9, color=FORCE_PAD, bold=True))

    # Гідродинамічний тиск нагнітання пасти в апертуру
    frags.append(line(240, st_y - 15, 240, st_y + 5, color=FORCE_PAD, sw=2.0))
    frags.append(poly([(237, 3), (243, 3), (240, 9)], fill=FORCE_PAD, stroke=FORCE_PAD))
    frags.append(text(240, st_y - 22, "Гідродинамічний тиск P_h", size=9, color=FORCE_PAD, bold=True))

    # Пояснювальний блок знизу
    frags.append(rect(40, 425, 445, 95, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(50, 445, "Етапи циклу трафаретного нанесення:", size=11, color=INK, anchor="start", bold=True))
    frags.append(text(50, 465, "1. Зсув та кочення валика пасти перед лезом (діаметр 15–20 мм)", size=10, color=MUTED, anchor="start"))
    frags.append(text(50, 483, "2. Зсувне розрідження (падіння в'язкості до 50–100 Па·с)", size=10, color=FORCE_PAD, anchor="start", bold=True))
    frags.append(text(50, 503, "3. Заповнення апертури та вертикальне відділення плати", size=10, color=MUTED, anchor="start"))

    # ── Права секція: Криві в'язкості та реологія ──
    frags.append(rect(515, 55, 340, 480, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(530, 78, "Реологічні характеристики пасти", size=12, color=MUTED, anchor="start", bold=True))

    # Графік 1: В'язкість vs Швидкість зсуву (Shear Thinning)
    frags.append(rect(530, 95, 310, 185, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(545, 115, "Зсувне розрідження (Shear Thinning)", size=11, color=INK, anchor="start", bold=True))

    gx1, gy1, gw1, gh1 = 575, 240, 240, 100
    frags.append(line(gx1, gy1, gx1 + gw1, gy1, color=MUTED, sw=1.0))
    frags.append(line(gx1, gy1, gx1, gy1 - gh1, color=MUTED, sw=1.0))
    frags.append(text(gx1 + gw1 - 10, gy1 + 15, "γ̇ (1/с)", size=9, color=MUTED, bold=True))
    frags.append(text(gx1 - 20, gy1 - gh1 + 10, "η (Па·с)", size=9, color=MUTED, bold=True))

    # Крива розрідження
    frags.append((
        f'<path d="M {gx1 + 10} {gy1 - 90} '
        f'Q {gx1 + 40} {gy1 - 20}, {gx1 + 120} {gy1 - 15} '
        f'L {gx1 + gw1 - 10} {gy1 - 10}" '
        f'fill="none" stroke="{FORCE_WALL}" stroke-width="2.2"/>'
    ))
    frags.append(circle(gx1 + 10, gy1 - 90, 3.0, fill=FORCE_WALL, stroke=FORCE_WALL))
    frags.append(text(gx1 + 25, gy1 - 85, "1000 Па·с (Спокій)", size=9, color=FORCE_WALL, anchor="start", bold=True))

    frags.append(circle(gx1 + 160, gy1 - 13, 3.0, fill=FORCE_PAD, stroke=FORCE_PAD))
    frags.append(text(gx1 + 130, gy1 - 25, "80 Па·с (Під ракелем)", size=9, color=FORCE_PAD, anchor="start", bold=True))

    frags.append(text(545, 268, "Закон Гершеля-Балклі: τ = τ₀ + K · γ̇ⁿ (n < 1)", size=10, color=MUTED, anchor="start"))

    # Графік 2: Відновлення в'язкості в часі (Тиксотропія / Thixotropy)
    frags.append(rect(530, 295, 310, 225, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(545, 315, "Тиксотропне відновлення форми (Slump)", size=11, color=INK, anchor="start", bold=True))

    gx2, gy2, gw2, gh2 = 575, 460, 240, 100
    frags.append(line(gx2, gy2, gx2 + gw2, gy2, color=MUTED, sw=1.0))
    frags.append(line(gx2, gy2, gx2, gy2 - gh2, color=MUTED, sw=1.0))
    frags.append(text(gx2 + gw2 - 10, gy2 + 15, "t (c)", size=9, color=MUTED, bold=True))
    frags.append(text(gx2 - 20, gy2 - gh2 + 10, "η (Па·с)", size=9, color=MUTED, bold=True))

    # Зона друку (зсув) -> Зона спокою (відновлення)
    frags.append(rect(gx2, gy2 - gh2, 60, gh2, fill="#fef2f2", stroke="none"))
    frags.append(text(gx2 + 30, gy2 - gh2 + 12, "Друк", size=9, color=FORCE_WALL, bold=True))

    frags.append(rect(gx2 + 60, gy2 - gh2, gw2 - 60, gh2, fill="#f0fdf4", stroke="none"))
    frags.append(text(gx2 + 140, gy2 - gh2 + 12, "Відновлення форми після друку", size=9, color=FORCE_PAD, bold=True))

    # Крива в часі
    frags.append((
        f'<path d="M {gx2} {gy2 - 15} '
        f'L {gx2 + 60} {gy2 - 15} '
        f'Q {gx2 + 100} {gy2 - 70}, {gx2 + gw2 - 10} {gy2 - 85}" '
        f'fill="none" stroke="{FORCE_PAD}" stroke-width="2.2"/>'
    ))

    frags.append(text(545, 490, "Запобігання місткам: швидке повернення високої", size=9, color=MUTED, anchor="start"))
    frags.append(text(545, 505, "в'язкості утримує вертикальні стінки цеглинки пасти", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "solder-paste-rheology-squeegee.svg"), W, H, *frags)
    print("Generated solder-paste-rheology-squeegee.svg")


if __name__ == "__main__":
    fig_area_ratio_geometry()
    fig_solder_paste_rheology()
