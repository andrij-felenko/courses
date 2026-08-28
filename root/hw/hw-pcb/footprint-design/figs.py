# -*- coding: utf-8 -*-
"""Фігури для теми footprint-design (посадкові місця компонентів).
Генерує 2 SVG-діаграми:
1. toe-heel-side-geometry.svg — геометрія пайки виводу (Toe, Heel, Side, меніск).
2. smd-vs-nsmd-pads.svg — порівняння SMD та NSMD контактних площадок для BGA.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER      = "#b5763a"
COPPER_FILL = "#e8c9a3"
SOLDER      = "#7f8c8d"
SOLDER_FILL = "#bdc3c7"
MASK        = "#2d6a4f"
MASK_FILL   = "#d8f3dc"
LEAD_FILL   = "#95a5a6"
LEAD_STROKE = "#4a5568"
FR4_FILL    = "#e2e8f0"
FR4_STROKE  = "#94a3b8"


# ── 1. Геометрія пайки: Toe, Heel, Side ──────────────────────────────────────
def fig_toe_heel_side():
    W, H = 860, 540
    frags = []

    # Фонова рамка
    frags.append(rect(10, 10, 840, 520, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=8))

    # Заголовок
    frags.append(text(430, 32, "Анатомія контактної площадки та паяного з'єднання за IPC-7351", size=15, color=INK, bold=True))

    # ── Верхня половина: Бічний переріз (Cross-section) ──────────────────────
    x_sec, y_sec = 30, 52
    frags.append(rect(x_sec, y_sec, 800, 220, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(x_sec + 20, y_sec + 22, "Бічний переріз виводу (Cross-Section): галтелі Toe та Heel", size=12, color=MUTED, anchor="start", bold=True))

    # Діелектрик плати FR-4
    frags.append(rect(x_sec + 30, y_sec + 155, 740, 30, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    frags.append(text(x_sec + 120, y_sec + 174, "Діелектрик плати (FR-4)", size=11, color=MUTED, anchor="start"))

    # Мідна контактна площадка (Copper Pad)
    pad_x, pad_y, pad_w, pad_h = x_sec + 170, y_sec + 143, 460, 12
    frags.append(rect(pad_x, pad_y, pad_w, pad_h, fill=COPPER_FILL, stroke=COPPER, sw=1.5, rx=1))
    frags.append(text(pad_x + pad_w / 2, pad_y + 9, "Мідна контактна площадка (Land Pad)", size=10, color=COPPER, bold=True))

    # Паяльна маска
    frags.append(rect(x_sec + 30, y_sec + 138, 110, 17, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))
    frags.append(text(x_sec + 85, y_sec + 130, "Паяльна маска", size=10, color=MASK, bold=True))

    frags.append(rect(x_sec + 660, y_sec + 138, 110, 17, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))
    frags.append(text(x_sec + 715, y_sec + 130, "Паяльна маска", size=10, color=MASK, bold=True))

    # Вивід компонента (Lead)
    lead_x1, lead_x2 = pad_x + 130, pad_x + 330
    lead_body = (
        f'<path d="M {lead_x1 - 50} {y_sec + 55} '
        f'L {lead_x1} {y_sec + 55} '
        f'C {lead_x1 + 15} {y_sec + 55}, {lead_x1 + 25} {y_sec + 85}, {lead_x1 + 40} {y_sec + 120} '
        f'L {lead_x2} {y_sec + 120} '
        f'C {lead_x2 + 10} {y_sec + 120}, {lead_x2 + 15} {y_sec + 126}, {lead_x2 + 15} {y_sec + 136} '
        f'L {lead_x1 + 20} {y_sec + 136} '
        f'C {lead_x1 + 5} {y_sec + 136}, {lead_x1 - 10} {y_sec + 85}, {lead_x1 - 50} {y_sec + 75} Z" '
        f'fill="{LEAD_FILL}" stroke="{LEAD_STROKE}" stroke-width="1.5"/>'
    )
    frags.append(lead_body)
    frags.append(text(lead_x1 + 110, y_sec + 112, "Вивід деталі (Lead)", size=11, color=INK, bold=True))

    # Припій: Heel
    heel_solder = (
        f'<path d="M {pad_x} {pad_y} '
        f'L {lead_x1 + 20} {pad_y} '
        f'L {lead_x1 + 20} {y_sec + 136} '
        f'C {lead_x1 + 5} {y_sec + 125}, {lead_x1 - 30} {y_sec + 105}, {pad_x + 35} {pad_y} Z" '
        f'fill="{SOLDER_FILL}" stroke="{SOLDER}" stroke-width="1.2"/>'
    )
    frags.append(heel_solder)

    # Припій під виводом
    frags.append(rect(lead_x1 + 20, pad_y, lead_x2 - lead_x1 - 5, 4, fill=SOLDER_FILL, stroke=SOLDER, sw=1.0, rx=0))

    # Припій: Toe
    toe_solder = (
        f'<path d="M {lead_x2 + 15} {y_sec + 136} '
        f'L {pad_x + pad_w} {pad_y} '
        f'L {lead_x2 + 15} {pad_y} Z" '
        f'fill="{SOLDER_FILL}" stroke="{SOLDER}" stroke-width="1.2"/>'
    )
    frags.append(toe_solder)

    # Розмірні лінії над виводом:
    # 1. Heel Jh
    frags.append(line(pad_x, y_sec + 72, pad_x, pad_y, color=NEG, sw=1.0, dash="3,2"))
    frags.append(line(lead_x1 + 20, y_sec + 72, lead_x1 + 20, pad_y, color=NEG, sw=1.0, dash="3,2"))
    frags.append(line(pad_x, y_sec + 78, lead_x1 + 20, y_sec + 78, color=NEG, sw=1.5))
    frags.append(circle(pad_x, y_sec + 78, 2.5, fill=NEG, stroke=NEG))
    frags.append(circle(lead_x1 + 20, y_sec + 78, 2.5, fill=NEG, stroke=NEG))
    frags.append(text((pad_x + lead_x1 + 20) / 2, y_sec + 70, "Heel Jh (П'ята)", size=10, color=NEG, bold=True))

    # 2. Lead Contact Length L
    frags.append(line(lead_x1 + 20, y_sec + 78, lead_x2 + 15, y_sec + 78, color=INK, sw=1.5))
    frags.append(line(lead_x2 + 15, y_sec + 72, lead_x2 + 15, pad_y, color=INK, sw=1.0, dash="3,2"))
    frags.append(circle(lead_x2 + 15, y_sec + 78, 2.5, fill=INK, stroke=INK))
    frags.append(text((lead_x1 + 20 + lead_x2 + 15) / 2, y_sec + 70, "Довжина виводу L", size=10, color=INK, bold=True))

    # 3. Toe Jt
    frags.append(line(pad_x + pad_w, y_sec + 72, pad_x + pad_w, pad_y, color=POS, sw=1.0, dash="3,2"))
    frags.append(line(lead_x2 + 15, y_sec + 78, pad_x + pad_w, y_sec + 78, color=POS, sw=1.5))
    frags.append(circle(pad_x + pad_w, y_sec + 78, 2.5, fill=POS, stroke=POS))
    frags.append(text((lead_x2 + 15 + pad_x + pad_w) / 2, y_sec + 70, "Toe Jt (Носок)", size=10, color=POS, bold=True))

    # Загальна довжина площадки (Land Length X)
    frags.append(line(pad_x, y_sec + 198, pad_x + pad_w, y_sec + 198, color=INK, sw=1.5))
    frags.append(line(pad_x, y_sec + 155, pad_x, y_sec + 204, color=INK, sw=1.0, dash="3,2"))
    frags.append(line(pad_x + pad_w, y_sec + 155, pad_x + pad_w, y_sec + 204, color=INK, sw=1.0, dash="3,2"))
    frags.append(circle(pad_x, y_sec + 198, 2.5, fill=INK, stroke=INK))
    frags.append(circle(pad_x + pad_w, y_sec + 198, 2.5, fill=INK, stroke=INK))
    frags.append(text(pad_x + pad_w / 2, y_sec + 212, "Довжина контактної площадки X = L + Jt + Jh + допуски", size=11, color=INK, bold=True))

    # ── Нижня половина: Вид зверху (Top View) ────────────────────────────────
    x_top, y_top = 30, 285
    frags.append(rect(x_top, y_top, 800, 235, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=6))
    frags.append(text(x_top + 20, y_top + 22, "Вид зверху (Top View): ширина площадки Y та бокові галтелі Side Js", size=12, color=MUTED, anchor="start", bold=True))

    # Контур дворика (Courtyard Boundary)
    cy_x, cy_y, cy_w, cy_h = x_top + 30, y_top + 38, 480, 180
    frags.append(rect(cy_x, cy_y, cy_w, cy_h, fill="none", stroke="#ea580c", sw=1.2, rx=4))
    frags.append(text(cy_x + 12, cy_y + 18, "Courtyard Boundary (Межа дворика компонента)", size=10, color="#ea580c", anchor="start", bold=True))

    # Апертура паяльної маски (Solder Mask Opening)
    mask_x, mask_y, mask_w, mask_h = cy_x + 40, cy_y + 30, 400, 125
    frags.append(rect(mask_x, mask_y, mask_w, mask_h, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=3))
    frags.append(text(mask_x + 12, mask_y + 16, "Вікно паяльної маски (Solder Mask Opening)", size=10, color=MASK, anchor="start", bold=True))

    # Мідна площадка (Copper Pad)
    cp_x, cp_y, cp_w, cp_h = mask_x + 20, mask_y + 18, 360, 90
    frags.append(rect(cp_x, cp_y, cp_w, cp_h, fill=COPPER_FILL, stroke=COPPER, sw=1.5, rx=2))

    # Вивід деталі (Lead)
    cl_x, cl_y, cl_w, cl_h = cp_x + 70, cp_y + 20, 220, 50
    frags.append(rect(cl_x, cl_y, cl_w, cl_h, fill=LEAD_FILL, stroke=LEAD_STROKE, sw=1.5, rx=2))
    frags.append(text(cl_x + cl_w / 2, cl_y + cl_h / 2 + 4, "Вивід компонента (Ширина W)", size=11, color="#ffffff", bold=True))

    # Бокові галтелі (Side Js)
    # Верхня галтель
    frags.append(line(cl_x + 30, cp_y, cl_x + 30, cl_y, color=FIELD, sw=1.5))
    frags.append(circle(cl_x + 30, cp_y, 2.0, fill=FIELD, stroke=FIELD))
    frags.append(circle(cl_x + 30, cl_y, 2.0, fill=FIELD, stroke=FIELD))
    frags.append(text(cl_x + 65, cp_y + 12, "Side Js", size=10, color=FIELD, bold=True))

    # Нижня галтель
    frags.append(line(cl_x + 30, cl_y + cl_h, cl_x + 30, cp_y + cp_h, color=FIELD, sw=1.5))
    frags.append(circle(cl_x + 30, cl_y + cl_h, 2.0, fill=FIELD, stroke=FIELD))
    frags.append(circle(cl_x + 30, cp_y + cp_h, 2.0, fill=FIELD, stroke=FIELD))
    frags.append(text(cl_x + 65, cp_y + cp_h - 4, "Side Js", size=10, color=FIELD, bold=True))

    # Ширина площадки Y (виносна лінія праворуч від площадки)
    frags.append(line(cp_x + cp_w + 12, cp_y, cp_x + cp_w + 12, cp_y + cp_h, color=INK, sw=1.5))
    frags.append(line(cp_x + cp_w, cp_y, cp_x + cp_w + 16, cp_y, color=INK, sw=1.0, dash="3,2"))
    frags.append(line(cp_x + cp_w, cp_y + cp_h, cp_x + cp_w + 16, cp_y + cp_h, color=INK, sw=1.0, dash="3,2"))
    frags.append(circle(cp_x + cp_w + 12, cp_y, 2.5, fill=INK, stroke=INK))
    frags.append(circle(cp_x + cp_w + 12, cp_y + cp_h, 2.5, fill=INK, stroke=INK))
    frags.append(text(cp_x + cp_w + 24, cp_y + cp_h / 2 + 4, "Ширина Y", size=10, color=INK, anchor="start", bold=True))

    # Права інформаційна панель
    info_x, info_y, info_w, info_h = x_top + 530, y_top + 38, 240, 180
    frags.append(rect(info_x, info_y, info_w, info_h, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    frags.append(text(info_x + info_w / 2, info_y + 22, "Три правила IPC-7351:", size=11, color=INK, bold=True))
    frags.append(text(info_x + 12, info_y + 50, "1. Toe (Jt): утримує меніск", size=10, color=POS, anchor="start", bold=True))
    frags.append(text(info_x + 24, info_y + 68, "і захищає від відриву при вигині.", size=9, color=MUTED, anchor="start"))
    frags.append(text(info_x + 12, info_y + 92, "2. Heel (Jh): сприймає зсув", size=10, color=NEG, anchor="start", bold=True))
    frags.append(text(info_x + 24, info_y + 110, "при тепловому розширенні (CTE).", size=9, color=MUTED, anchor="start"))
    frags.append(text(info_x + 12, info_y + 134, "3. Side (Js): центрує деталь", size=10, color=FIELD, anchor="start", bold=True))
    frags.append(text(info_x + 24, info_y + 152, "силами поверхневого натягу.", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "toe-heel-side-geometry.svg"), W, H, *frags)


# ── 2. Порівняння SMD та NSMD контактних площадок ────────────────────────────
def fig_smd_vs_nsmd():
    W, H = 860, 480
    frags = []

    # Фонова рамка
    frags.append(rect(10, 10, 840, 460, fill="#ffffff", stroke="#d1d5db", sw=1.0, rx=8))

    # Головний заголовок
    frags.append(text(430, 32, "Порівняння контактних площадок BGA: SMD проти NSMD", size=15, color=INK, bold=True))

    # ── Ліва панель: SMD (Solder Mask Defined) ────────────────────────────────
    lx, ly, pw, ph = 30, 52, 385, 400
    frags.append(rect(lx, ly, pw, ph, fill="#fbfbfc", stroke="#cbd5e1", sw=1.2, rx=6))

    # Шапка SMD
    frags.append(rect(lx + 10, ly + 10, pw - 20, 28, fill="#fee2e2", stroke="#fca5a5", sw=1.0, rx=4))
    frags.append(text(lx + pw / 2, ly + 28, "SMD: Solder Mask Defined (Задано маскою)", size=12, color=POS, bold=True))

    # FR-4
    frags.append(rect(lx + 20, ly + 175, pw - 40, 35, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    frags.append(text(lx + 30, ly + 197, "Діелектрик плати (FR-4)", size=10, color=MUTED, anchor="start"))

    # Мідні ділянки: ліва захована під маску, відкрита середня, права захована
    # Відкрита середня мідь: x = lx + 105 .. lx + 280 (W = 175)
    frags.append(rect(lx + 105, ly + 160, 175, 15, fill=COPPER_FILL, stroke=COPPER, sw=1.5, rx=0))
    frags.append(text(lx + pw / 2, ly + 171, "Мідна площадка", size=10, color=COPPER, bold=True))

    # Паяльна маска зліва і справа
    frags.append(rect(lx + 20, ly + 152, 85, 23, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))
    frags.append(rect(lx + 280, ly + 152, 85, 23, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))
    frags.append(text(lx + 62, ly + 142, "Маска", size=10, color=MASK, bold=True))
    frags.append(text(lx + 322, ly + 142, "Маска", size=10, color=MASK, bold=True))

    # Кулька припою BGA (сидить у вікні маски)
    solder_smd = (
        f'<path d="M {lx + 105} {ly + 160} '
        f'C {lx + 95} {ly + 105}, {lx + 130} {ly + 65}, {lx + pw/2} {ly + 65} '
        f'C {lx + 255} {ly + 65}, {lx + 290} {ly + 105}, {lx + 280} {ly + 160} Z" '
        f'fill="{SOLDER_FILL}" stroke="{SOLDER}" stroke-width="1.5"/>'
    )
    frags.append(solder_smd)
    frags.append(text(lx + pw / 2, ly + 110, "Кулька BGA", size=11, color=INK, bold=True))

    # Точки концентрації напружень (червоні кола)
    frags.append(circle(lx + 105, ly + 160, 4, fill=POS, stroke="#991b1b"))
    frags.append(circle(lx + 280, ly + 160, 4, fill=POS, stroke="#991b1b"))
    frags.append(text(lx + pw / 2, ly + 150, "Концентрація напружень на краї маски", size=10, color=POS, bold=True))

    # Розмір апертури маски
    frags.append(line(lx + 105, ly + 225, lx + 280, ly + 225, color=POS, sw=1.5))
    frags.append(line(lx + 105, ly + 160, lx + 105, ly + 230, color=POS, sw=1.0, dash="3,2"))
    frags.append(line(lx + 280, ly + 160, lx + 280, ly + 230, color=POS, sw=1.0, dash="3,2"))
    frags.append(circle(lx + 105, ly + 225, 2.5, fill=POS, stroke=POS))
    frags.append(circle(lx + 280, ly + 225, 2.5, fill=POS, stroke=POS))
    frags.append(text(lx + pw / 2, ly + 240, "Розмір площадки задає маска (D_mask)", size=10, color=POS, bold=True))

    # Інформаційний блок SMD
    info_smd_x, info_smd_y = lx + 15, ly + 258
    frags.append(rect(info_smd_x, info_smd_y, pw - 30, 130, fill="#ffffff", stroke="#fecaca", sw=1.0, rx=4))
    frags.append(text(info_smd_x + 12, info_smd_y + 20, "• Мідь затиснута маскою: висока міцність", size=10, color=INK, anchor="start"))
    frags.append(text(info_smd_x + 24, info_smd_y + 36, "на відрив при падінні й ударах.", size=9, color=MUTED, anchor="start"))
    frags.append(text(info_smd_x + 12, info_smd_y + 56, "• Гострий кут маски провокує тріщини", size=10, color=POS, anchor="start", bold=True))
    frags.append(text(info_smd_x + 24, info_smd_y + 72, "при циклічних змінах температури (CTE).", size=9, color=MUTED, anchor="start"))
    frags.append(text(info_smd_x + 12, info_smd_y + 92, "• Вузький проміжок для трасування доріжок.", size=10, color=INK, anchor="start"))
    frags.append(text(info_smd_x + 12, info_smd_y + 112, "• Застосування: кнопки, важкі роз'єми.", size=10, color=INK, anchor="start", bold=True))

    # ── Права панель: NSMD (Non-Solder Mask Defined) ──────────────────────────
    rx, ry = 445, 52
    frags.append(rect(rx, ry, pw, ph, fill="#fbfbfc", stroke="#cbd5e1", sw=1.2, rx=6))

    # Шапка NSMD
    frags.append(rect(rx + 10, ry + 10, pw - 20, 28, fill="#dcfce7", stroke="#86efac", sw=1.0, rx=4))
    frags.append(text(rx + pw / 2, ry + 28, "NSMD: Non-Solder Mask Defined (Задано міддю)", size=12, color=FIELD, bold=True))

    # FR-4
    frags.append(rect(rx + 20, ry + 175, pw - 40, 35, fill=FR4_FILL, stroke=FR4_STROKE, sw=1.2, rx=2))
    frags.append(text(rx + 30, ry + 197, "Діелектрик плати (FR-4)", size=10, color=MUTED, anchor="start"))

    # Мідна площадка (окремо розташована)
    frags.append(rect(rx + 110, ry + 160, 165, 15, fill=COPPER_FILL, stroke=COPPER, sw=1.5, rx=1))
    frags.append(text(rx + pw / 2, ry + 171, "Мідний пад", size=10, color=COPPER, bold=True))

    # Паяльна маска (відкрита із зазором)
    frags.append(rect(rx + 20, ly + 152, 65, 23, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))
    frags.append(rect(rx + 300, ly + 152, 65, 23, fill=MASK_FILL, stroke=MASK, sw=1.2, rx=1))
    frags.append(text(rx + 52, ry + 142, "Маска", size=10, color=MASK, bold=True))
    frags.append(text(rx + 332, ry + 142, "Маска", size=10, color=MASK, bold=True))

    # Зазор маски (Clearance gap)
    frags.append(rect(rx + 87, ry + 168, 21, 6, fill="#fef08a", stroke="#eab308", sw=0.8, rx=1))
    frags.append(rect(rx + 277, ry + 168, 21, 6, fill="#fef08a", stroke="#eab308", sw=0.8, rx=1))

    # Кулька припою BGA (обтікає бокові грані міді)
    solder_nsmd = (
        f'<path d="M {rx + 105} {ry + 175} '
        f'L {rx + 110} {ry + 160} '
        f'C {rx + 100} {ry + 105}, {rx + 135} {ly + 65}, {rx + pw/2} {ly + 65} '
        f'C {rx + 250} {ly + 65}, {rx + 285} {ly + 105}, {rx + 275} {ry + 160} '
        f'L {rx + 280} {ry + 175} Z" '
        f'fill="{SOLDER_FILL}" stroke="{SOLDER}" stroke-width="1.5"/>'
    )
    frags.append(solder_nsmd)
    frags.append(text(rx + pw / 2, ry + 110, "Кулька BGA", size=11, color=INK, bold=True))

    # 3D-змочування бічних граней (зелені кола)
    frags.append(circle(rx + 105, ry + 170, 3.5, fill=FIELD, stroke="#15803d"))
    frags.append(circle(rx + 280, ry + 170, 3.5, fill=FIELD, stroke="#15803d"))
    frags.append(text(rx + pw / 2, ry + 146, "3D-змочування бічних стінок міді", size=10, color=FIELD, bold=True))

    # Розмір площадки (D_copper)
    frags.append(line(rx + 110, ry + 225, rx + 275, ry + 225, color=FIELD, sw=1.5))
    frags.append(line(rx + 110, ry + 175, rx + 110, ry + 230, color=FIELD, sw=1.0, dash="3,2"))
    frags.append(line(rx + 275, ry + 175, rx + 275, ry + 230, color=FIELD, sw=1.0, dash="3,2"))
    frags.append(circle(rx + 110, ry + 225, 2.5, fill=FIELD, stroke=FIELD))
    frags.append(circle(rx + 275, ry + 225, 2.5, fill=FIELD, stroke=FIELD))
    frags.append(text(rx + pw / 2, ry + 240, "Розмір задає травлення міді (D_copper)", size=10, color=FIELD, bold=True))

    # Інформаційний блок NSMD
    info_nsmd_x, info_nsmd_y = rx + 15, ry + 258
    frags.append(rect(info_nsmd_x, info_nsmd_y, pw - 30, 130, fill="#ffffff", stroke="#bbf7d0", sw=1.0, rx=4))
    frags.append(text(info_nsmd_x + 12, info_nsmd_y + 20, "• Прецизійний розмір (фотолітографія ±12 мкм)", size=10, color=INK, anchor="start"))
    frags.append(text(info_nsmd_x + 24, info_nsmd_y + 36, "проти маски з допуском ±50 мкм.", size=9, color=MUTED, anchor="start"))
    frags.append(text(info_nsmd_x + 12, info_nsmd_y + 56, "• Припій охоплює боковини (механічний замок):", size=10, color=FIELD, anchor="start", bold=True))
    frags.append(text(info_nsmd_x + 24, info_nsmd_y + 72, "висока втомна міцність при термоциклах.", size=9, color=MUTED, anchor="start"))
    frags.append(text(info_nsmd_x + 12, info_nsmd_y + 92, "• Ширший канал для трасування BGA-сигналів.", size=10, color=INK, anchor="start"))
    frags.append(text(info_nsmd_x + 12, info_nsmd_y + 112, "• Стандарт для BGA, QFN, WLCSP, 0402/0201.", size=10, color=INK, anchor="start", bold=True))

    render(os.path.join(OUT, "smd-vs-nsmd-pads.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_toe_heel_side()
    fig_smd_vs_nsmd()
    print("All figures generated successfully.")
