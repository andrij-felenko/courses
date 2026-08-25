# -*- coding: utf-8 -*-
"""Фігури до теми «Модель зосереджених елементів».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

ACCENT = "#16a34a"  # зелений
DARK   = "#0f172a"  # темно-синій/чорний
BLUE   = "#2563eb"  # синій
ORANGE = "#ea580c"  # помаранчевий
RED    = "#dc2626"  # червоний
MUTED  = "#6b7280"  # сірий
FILL_L = "#f8fafc"  # світлий фон для рамок

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Порівняння 3D фізичного поля та зосередженої кільної абстракції ──────
def fig_lumped_vs_distributed():
    W, H = 760, 420
    elements = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    elements.append(text(W / 2, 26, "Перехід від 3D електромагнітного поля до 0D зосередженої схеми", size=16, bold=True))

    # Ліва панель: Фізичний 3D простір
    p1_x, p1_y, p1_w, p1_h = 20, 50, 350, 350
    elements.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fafaf9", stroke="#d6d3d1", sw=1.5, rx=8))
    elements.append(text(p1_x + p1_w / 2, p1_y + 24, "1. Фізична система у 3D просторі (Поля)", size=13, bold=True, color=DARK))

    # Схема хвилі/поля у 3D
    elements.append(line(p1_x + 40, p1_y + 110, p1_x + 310, p1_y + 110, color=DARK, sw=3))
    elements.append(line(p1_x + 40, p1_y + 230, p1_x + 310, p1_y + 230, color=DARK, sw=3))
    elements.append(text(p1_x + 45, p1_y + 98, "Провідник A", size=11, color=DARK, bold=True, anchor="start"))
    elements.append(text(p1_x + 45, p1_y + 245, "Провідник B", size=11, color=DARK, bold=True, anchor="start"))

    # Хвиля E(r,t) між провідниками
    for x_off in range(90, 300, 35):
        elements.append(arrow(p1_x + x_off, p1_y + 115, p1_x + x_off, p1_y + 225, color=RED, sw=1.5))
        elements.append(text(p1_x + x_off + 8, p1_y + 170, "E(r,t)", size=10, color=RED, anchor="start"))

    # Магнітні вихори B(r,t)
    for x_off in [110, 180, 250]:
        elements.append('<ellipse cx="%.1f" cy="%.1f" rx="14" ry="8" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,2"/>' % (p1_x + x_off, p1_y + 110, BLUE))
        elements.append('<ellipse cx="%.1f" cy="%.1f" rx="14" ry="8" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,2"/>' % (p1_x + x_off, p1_y + 230, BLUE))
    elements.append(text(p1_x + 220, p1_y + 92, "B(r,t)", size=10, color=BLUE, bold=True))

    # Габарит розміру d і хвилі λ
    elements.append(line(p1_x + 40, p1_y + 270, p1_x + 310, p1_y + 270, color=ORANGE, sw=1.5))
    elements.append(line(p1_x + 40, p1_y + 265, p1_x + 40, p1_y + 275, color=ORANGE, sw=1.5))
    elements.append(line(p1_x + 310, p1_y + 265, p1_x + 310, p1_y + 275, color=ORANGE, sw=1.5))
    elements.append(text(p1_x + 175, p1_y + 264, "Характерний розмір d ≪ λ", size=11, bold=True, color=ORANGE))

    # Картка умов
    b_cond, _, _ = textbox(p1_x + p1_w / 2, p1_y + 315,
                           "Умови: ∇×E = −∂B/∂t ≠ 0 всюди у просторі,\n"
                           "хвильове запізнення τ = d/c порівнянне з T",
                           size=10, pad=6, fill="#fff7ed", stroke=ORANGE, sw=1)
    elements.append(b_cond)

    # Стрілка переходу між панелями
    elements.append(arrow(380, 220, 410, 220, color=ACCENT, sw=3))
    elements.append(text(395, 205, "Абстракція", size=11, bold=True, color=ACCENT))

    # Права панель: Зосереджена схема (0D)
    p2_x, p2_y, p2_w, p2_h = 420, 50, 320, 350
    elements.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    elements.append(text(p2_x + p2_w / 2, p2_y + 24, "2. Зосереджена еквівалентна схема (0D)", size=13, bold=True, color=DARK))

    # Дискретні елементи
    cx = p2_x + p2_w / 2
    # Вузол 1 (вхід)
    elements.append(circle(p2_x + 50, p2_y + 100, 5, fill=DARK, stroke=DARK, sw=1))
    elements.append(text(p2_x + 50, p2_y + 85, "Вузол A", size=11, bold=True))
    elements.append(circle(p2_x + 50, p2_y + 230, 5, fill=DARK, stroke=DARK, sw=1))
    elements.append(text(p2_x + 50, p2_y + 248, "Вузол B", size=11, bold=True))

    # Резистор R та Індуктивність L зверху
    elements.append(line(p2_x + 50, p2_y + 100, p2_x + 90, p2_y + 100, color=DARK, sw=2))
    # Зигзаг R
    r_pts = [(90, 100), (95, 92), (105, 108), (115, 92), (125, 108), (135, 92), (140, 100)]
    r_path = "M " + " L ".join("%d %d" % (p2_x + x, p2_y + y) for x, y in r_pts)
    elements.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (r_path, DARK))
    elements.append(text(p2_x + 115, p2_y + 82, "R", size=12, bold=True, color=DARK))

    elements.append(line(p2_x + 140, p2_y + 100, p2_x + 170, p2_y + 100, color=DARK, sw=2))
    # Спіраль L
    elements.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2"/>' %
                    (p2_x + 170, p2_y + 100, p2_x + 180, p2_y + 85, p2_x + 190, p2_y + 100,
                     p2_x + 200, p2_y + 85, p2_x + 210, p2_y + 100,
                     p2_x + 220, p2_y + 85, p2_x + 230, p2_y + 100, DARK))
    elements.append(text(p2_x + 200, p2_y + 82, "L", size=12, bold=True, color=DARK))
    elements.append(line(p2_x + 230, p2_y + 100, p2_x + 270, p2_y + 100, color=DARK, sw=2))

    # Провідник знизу
    elements.append(line(p2_x + 50, p2_y + 230, p2_x + 270, p2_y + 230, color=DARK, sw=2))

    # Ємність C посередині
    elements.append(line(p2_x + 270, p2_y + 100, p2_x + 270, p2_y + 155, color=DARK, sw=2))
    elements.append(line(p2_x + 270, p2_y + 230, p2_x + 270, p2_y + 175, color=DARK, sw=2))
    elements.append(line(p2_x + 255, p2_y + 155, p2_x + 285, p2_y + 155, color=DARK, sw=2.5))
    elements.append(line(p2_x + 255, p2_y + 175, p2_x + 285, p2_y + 175, color=DARK, sw=2.5))
    elements.append(text(p2_x + 295, p2_y + 168, "C", size=12, bold=True, color=DARK, anchor="start"))

    # Напруга V(t) та Струм I(t)
    elements.append(arrow(p2_x + 35, p2_y + 110, p2_x + 35, p2_y + 220, color=BLUE, sw=1.5))
    elements.append(text(p2_x + 20, p2_y + 168, "V(t)", size=12, bold=True, color=BLUE))

    elements.append(arrow(p2_x + 55, p2_y + 112, p2_x + 85, p2_y + 112, color=RED, sw=1.5))
    elements.append(text(p2_x + 70, p2_y + 126, "I(t)", size=11, bold=True, color=RED))

    # Картка законів
    b_laws, _, _ = textbox(p2_x + p2_w / 2, p2_y + 315,
                           "Скелет: Звичайні диференціальні рівняння (ЗДУ)\n"
                           "Закони Кірхгофа: KCL (∑I=0) та KVL (∑V=0)\n"
                           "Поля локалізовані всередині елементів R, L, C",
                           size=10, pad=6, fill="#f0fdf4", stroke=ACCENT, sw=1)
    elements.append(b_laws)

    return render(os.path.join(IMG, "lumped-vs-distributed.svg"), W, H, *elements)


# ── Фігура 2: Від рівнянь Максвелла до законів Кірхгофа (KCL та KVL) ───────────────
def fig_maxwell_to_kirchhoff():
    W, H = 760, 400
    elements = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    elements.append(text(W / 2, 26, "Фізична редукція Максвелла до законів Кірхгофа", size=16, bold=True))

    # Лівий блок: KCL (Закон струмів Кірхгофа)
    b1_x, b1_y, b1_w, b1_h = 20, 55, 350, 325
    elements.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    elements.append(text(b1_x + b1_w / 2, b1_y + 24, "KCL: Збереження заряду у вузлі", size=13, bold=True, color=BLUE))

    # Вузол як замкнена поверхня S
    cx1, cy1 = b1_x + 175, b1_y + 130
    elements.append('<ellipse cx="%.1f" cy="%.1f" rx="65" ry="45" fill="#dbeafe" stroke="%s" stroke-width="1.5" stroke-dasharray="4,3"/>' % (cx1, cy1, BLUE))
    elements.append(circle(cx1, cy1, 6, fill=DARK, stroke=DARK, sw=1))
    elements.append(text(cx1, cy1 - 12, "Вузол K", size=11, bold=True))
    elements.append(text(cx1 + 50, cy1 - 32, "Поверхня S", size=10, color=BLUE, bold=True))

    # Струми, що входять і виходять
    elements.append(arrow(cx1 - 110, cy1 - 25, cx1 - 55, cy1 - 10, color=RED, sw=2))
    elements.append(text(cx1 - 90, cy1 - 32, "I₁", size=12, bold=True, color=RED))

    elements.append(arrow(cx1 - 100, cy1 + 30, cx1 - 55, cy1 + 15, color=RED, sw=2))
    elements.append(text(cx1 - 85, cy1 + 42, "I₂", size=12, bold=True, color=RED))

    elements.append(arrow(cx1 + 55, cy1 - 5, cx1 + 110, cy1 - 20, color=RED, sw=2))
    elements.append(text(cx1 + 90, cy1 - 28, "I₃", size=12, bold=True, color=RED))

    elements.append(arrow(cx1 + 55, cy1 + 15, cx1 + 105, cy1 + 35, color=RED, sw=2))
    elements.append(text(cx1 + 85, cy1 + 42, "I₄", size=12, bold=True, color=RED))

    # Формули KCL
    b_kcl_math, _, _ = textbox(b1_x + b1_w / 2, b1_y + 250,
                               "1. Рівняння неперервності: ∮ S J·dA = −dQ/dt\n"
                               "2. Умова вузла: dQ_node/dt = 0 (немає накопичення)\n"
                               "3. Висновок: ∑ I_k = 0  (I₁ + I₂ − I₃ − I₄ = 0)",
                               size=11, pad=8, fill=BG, stroke=BLUE, sw=1.2)
    elements.append(b_kcl_math)

    # Правий блок: KVL (Закон напруг Кірхгофа)
    b2_x, b2_y, b2_w, b2_h = 390, 55, 350, 325
    elements.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    elements.append(text(b2_x + b2_w / 2, b2_y + 24, "KVL: Потенціальність контуру", size=13, bold=True, color=RED))

    # Контур Г
    cx2, cy2 = b2_x + 175, b2_y + 130
    elements.append(rect(cx2 - 80, cy2 - 45, 160, 90, fill="none", stroke=RED, sw=1.8, rx=6))
    elements.append(text(cx2, cy2 - 55, "Контур Γ", size=11, bold=True, color=RED))

    # Елементи на контурі
    # Джерело V1
    elements.append(rect(cx2 - 90, cy2 - 12, 20, 24, fill="#fee2e2", stroke=RED, sw=1))
    elements.append(text(cx2 - 80, cy2, "V₁", size=10, bold=True))
    # R1
    elements.append(rect(cx2 - 15, cy2 - 53, 30, 16, fill="#fee2e2", stroke=RED, sw=1))
    elements.append(text(cx2, cy2 - 45, "R₁", size=10, bold=True))
    # R2
    elements.append(rect(cx2 + 70, cy2 - 12, 20, 24, fill="#fee2e2", stroke=RED, sw=1))
    elements.append(text(cx2 + 80, cy2, "R₂", size=10, bold=True))

    # Відсутність магнітного потоку поза елементами
    elements.append(text(cx2, cy2, "∂B/∂t = 0 зовні", size=11, bold=True, color=MUTED))

    # Формули KVL
    b_kvl_math, _, _ = textbox(b2_x + b2_w / 2, b2_y + 250,
                               "1. Закон Фарадея: ∮ Γ E·dl = −dΦ_B/dt\n"
                               "2. Умова зосередженості: dΦ_B/dt = 0 (поза L)\n"
                               "3. Поле потенціальне (∇×E=0) ⇒ ∑ V_k = 0",
                               size=11, pad=8, fill=BG, stroke=RED, sw=1.2)
    elements.append(b_kvl_math)

    return render(os.path.join(IMG, "maxwell-to-kirchhoff.svg"), W, H, *elements)


# ── Фігура 3: Неідеальні компоненти та паразитні еквівалентні схеми ───────────────
def fig_parasitic_model():
    W, H = 760, 430
    elements = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    elements.append(text(W / 2, 26, "Паразитні параметри реальних компонентів на високих частотах", size=16, bold=True))

    # 1. Реальний Резистор (зверху ліворуч)
    c1_x, c1_y, c1_w, c1_h = 20, 55, 350, 170
    elements.append(rect(c1_x, c1_y, c1_w, c1_h, fill=FILL_L, stroke=MUTED, sw=1.2, rx=6))
    elements.append(text(c1_x + 15, c1_y + 20, "1. Реальний Резистор", size=12, bold=True, color=DARK, anchor="start"))

    # Еквівалентна схема: R послідовно з ESL, і паралельно Cp
    # Вхідний провід
    elements.append(line(c1_x + 30, c1_y + 80, c1_x + 60, c1_y + 80, color=DARK, sw=1.5))
    elements.append(circle(c1_x + 60, c1_y + 80, 3, fill=DARK, stroke=DARK, sw=1))

    # Паралельне розгалуження
    elements.append(line(c1_x + 60, c1_y + 80, c1_x + 60, c1_y + 60, color=DARK, sw=1.5))
    elements.append(line(c1_x + 60, c1_y + 80, c1_x + 60, c1_y + 110, color=DARK, sw=1.5))

    # Нижня гілка: R + ESL
    elements.append(line(c1_x + 60, c1_y + 110, c1_x + 90, c1_y + 110, color=DARK, sw=1.5))
    elements.append(rect(c1_x + 90, c1_y + 102, 35, 16, fill="#ffffff", stroke=DARK, sw=1.2))
    elements.append(text(c1_x + 107, c1_y + 114, "R_nominal", size=9, bold=True))
    elements.append(line(c1_x + 125, c1_y + 110, c1_x + 150, c1_y + 110, color=DARK, sw=1.5))

    # ESL
    elements.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.5"/>' %
                    (c1_x + 150, c1_y + 110, c1_x + 160, c1_y + 98, c1_x + 170, c1_y + 110,
                     c1_x + 180, c1_y + 98, c1_x + 190, c1_y + 110, DARK))
    elements.append(text(c1_x + 170, c1_y + 126, "ESL (L_s)", size=9, bold=True, color=RED))
    elements.append(line(c1_x + 190, c1_y + 110, c1_x + 220, c1_y + 110, color=DARK, sw=1.5))

    # Верхня гілка: Паразитна ємність Cp
    elements.append(line(c1_x + 60, c1_y + 60, c1_x + 125, c1_y + 60, color=DARK, sw=1.5))
    elements.append(line(c1_x + 125, c1_y + 52, c1_x + 125, c1_y + 68, color=DARK, sw=2))
    elements.append(line(c1_x + 135, c1_y + 52, c1_x + 135, c1_y + 68, color=DARK, sw=2))
    elements.append(text(c1_x + 130, c1_y + 44, "C_p (паразитна)", size=9, bold=True, color=BLUE))
    elements.append(line(c1_x + 135, c1_y + 60, c1_x + 220, c1_y + 60, color=DARK, sw=1.5))

    # З'єднання на виході
    elements.append(line(c1_x + 220, c1_y + 60, c1_x + 220, c1_y + 110, color=DARK, sw=1.5))
    elements.append(circle(c1_x + 220, c1_y + 80, 3, fill=DARK, stroke=DARK, sw=1))
    elements.append(line(c1_x + 220, c1_y + 80, c1_x + 250, c1_y + 80, color=DARK, sw=1.5))

    # Опис
    elements.append(text(c1_x + 175, c1_y + 150, "На ВЧ: паразитна C_p шунтує R, ESL дає індуктивний опір", size=9, color=MUTED, anchor="middle"))


    # 2. Реальний Конденсатор (зверху праворуч)
    c2_x, c2_y, c2_w, c2_h = 390, 55, 350, 170
    elements.append(rect(c2_x, c2_y, c2_w, c2_h, fill=FILL_L, stroke=MUTED, sw=1.2, rx=6))
    elements.append(text(c2_x + 15, c2_y + 20, "2. Реальний Конденсатор (модель RLC)", size=12, bold=True, color=DARK, anchor="start"))

    # Послідовний ланцюг: C + ESR + ESL + Паралельний Rp (витік)
    elements.append(line(c2_x + 30, c2_y + 80, c2_x + 60, c2_y + 80, color=DARK, sw=1.5))

    # Ideal C
    elements.append(line(c2_x + 60, c2_y + 70, c2_x + 60, c2_y + 90, color=DARK, sw=2))
    elements.append(line(c2_x + 70, c2_y + 70, c2_x + 70, c2_y + 90, color=DARK, sw=2))
    elements.append(text(c2_x + 65, c2_y + 60, "C_nominal", size=9, bold=True))
    elements.append(line(c2_x + 70, c2_y + 80, c2_x + 110, c2_y + 80, color=DARK, sw=1.5))

    # ESR
    elements.append(rect(c2_x + 110, c2_y + 72, 35, 16, fill="#ffffff", stroke=DARK, sw=1.2))
    elements.append(text(c2_x + 127, c2_y + 62, "ESR (R_s)", size=9, bold=True, color=RED))
    elements.append(line(c2_x + 145, c2_y + 80, c2_x + 175, c2_y + 80, color=DARK, sw=1.5))

    # ESL
    elements.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.5"/>' %
                    (c2_x + 175, c2_y + 80, c2_x + 185, c2_y + 68, c2_x + 195, c2_y + 80,
                     c2_x + 205, c2_y + 68, c2_x + 215, c2_y + 80, DARK))
    elements.append(text(c2_x + 195, c2_y + 62, "ESL (L_s)", size=9, bold=True, color=BLUE))
    elements.append(line(c2_x + 215, c2_y + 80, c2_x + 250, c2_y + 80, color=DARK, sw=1.5))

    # SRF формула
    elements.append(text(c2_x + 175, c2_y + 120, "Частота власного резонансу: f_srf = 1 / (2π √(ESL · C))", size=10, bold=True, color=DARK))
    elements.append(text(c2_x + 175, c2_y + 145, "Вище f_srf конденсатор стає ІНДУКТИВНІСТЮ!", size=10, bold=True, color=RED))


    # 3. Реальна Індуктивність (знизу посередині)
    c3_x, c3_y, c3_w, c3_h = 150, 240, 460, 175
    elements.append(rect(c3_x, c3_y, c3_w, c3_h, fill=FILL_L, stroke=MUTED, sw=1.2, rx=6))
    elements.append(text(c3_x + 15, c3_y + 20, "3. Реальна Індуктивність (дросель / котушка)", size=12, bold=True, color=DARK, anchor="start"))

    # Послідовно L_nom + DCR (R_s), паралельно Cp (міжвиткова ємність)
    elements.append(line(c3_x + 40, c3_y + 90, c3_x + 80, c3_y + 90, color=DARK, sw=1.5))
    elements.append(circle(c3_x + 80, c3_y + 90, 3, fill=DARK, stroke=DARK, sw=1))

    # Розгалуження
    elements.append(line(c3_x + 80, c3_y + 90, c3_x + 80, c3_y + 55, color=DARK, sw=1.5))
    elements.append(line(c3_x + 80, c3_y + 90, c3_x + 80, c3_y + 125, color=DARK, sw=1.5))

    # Нижня гілка: L + DCR
    elements.append(line(c3_x + 80, c3_y + 125, c3_x + 120, c3_y + 125, color=DARK, sw=1.5))
    elements.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.5"/>' %
                    (c3_x + 120, c3_y + 125, c3_x + 130, c3_y + 110, c3_x + 140, c3_y + 125,
                     c3_x + 150, c3_y + 110, c3_x + 160, c3_y + 125,
                     c3_x + 170, c3_y + 110, c3_x + 180, c3_y + 125, DARK))
    elements.append(text(c3_x + 150, c3_y + 143, "L_nominal", size=9, bold=True))
    elements.append(line(c3_x + 180, c3_y + 125, c3_x + 220, c3_y + 125, color=DARK, sw=1.5))

    elements.append(rect(c3_x + 220, c3_y + 117, 45, 16, fill="#ffffff", stroke=DARK, sw=1.2))
    elements.append(text(c3_x + 242, c3_y + 129, "DCR (R_dc)", size=9, bold=True, color=RED))
    elements.append(line(c3_x + 265, c3_y + 125, c3_x + 360, c3_y + 125, color=DARK, sw=1.5))

    # Верхня гілка: Паразитна міжвиткова ємність C_p
    elements.append(line(c3_x + 80, c3_y + 55, c3_x + 215, c3_y + 55, color=DARK, sw=1.5))
    elements.append(line(c3_x + 215, c3_y + 45, c3_x + 215, c3_y + 65, color=DARK, sw=2))
    elements.append(line(c3_x + 225, c3_y + 45, c3_x + 225, c3_y + 65, color=DARK, sw=2))
    elements.append(text(c3_x + 220, c3_y + 38, "C_p (міжвиткова)", size=9, bold=True, color=BLUE))
    elements.append(line(c3_x + 225, c3_y + 55, c3_x + 360, c3_y + 55, color=DARK, sw=1.5))

    # З'єднання
    elements.append(line(c3_x + 360, c3_y + 55, c3_x + 360, c3_y + 125, color=DARK, sw=1.5))
    elements.append(circle(c3_x + 360, c3_y + 90, 3, fill=DARK, stroke=DARK, sw=1))
    elements.append(line(c3_x + 360, c3_y + 90, c3_x + 420, c3_y + 90, color=DARK, sw=1.5))

    elements.append(text(c3_x + 230, c3_y + 162, "Вище власного резонансу дросель перетворюється на КОНДЕНСАТОР", size=10, bold=True, color=RED))

    return render(os.path.join(IMG, "parasitic-model.svg"), W, H, *elements)


# ── Фігура 4: Частотні режими та межі квазістаціонарності ──────────────────────────
def fig_frequency_regimes():
    W, H = 760, 380
    elements = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]

    elements.append(text(W / 2, 26, "Спектр режимів електродинаміки за відношенням d / λ", size=16, bold=True))

    # Осі частоти / розміру
    ax_x, ax_y, ax_w = 60, 100, 640
    elements.append(arrow(ax_x, ax_y, ax_x + ax_w, ax_y, color=DARK, sw=2))
    elements.append(text(ax_x + ax_w - 20, ax_y - 12, "Частота f (або розмір d / λ) →", size=11, bold=True, color=DARK))

    # Три основні зони на осі
    z1_w, z2_w, z3_w = 200, 220, 200
    z1_x = ax_x + 10
    z2_x = z1_x + z1_w
    z3_x = z2_x + z2_w

    # Зона 1: Квазістаціонарна зосереджена область
    elements.append(rect(z1_x, ax_y + 20, z1_w - 10, 220, fill="#f0fdf4", stroke=ACCENT, sw=1.5, rx=6))
    elements.append(text(z1_x + (z1_w-10)/2, ax_y + 42, "ЗОСЕРЕДЖЕНА МОДЕЛЬ", size=12, bold=True, color=ACCENT))
    elements.append(text(z1_x + (z1_w-10)/2, ax_y + 60, "d ≪ λ  (d < λ / 10)", size=11, bold=True, color=DARK))

    b1_info, _, _ = textbox(z1_x + (z1_w-10)/2, ax_y + 145,
                            "• Поля локалізовані\n"
                            "• Запізнення τ ≪ T\n"
                            "• Закони Кірхгофа KCL/KVL\n"
                            "• Ззвичайні ДУ (ODE)\n"
                            "• Схеми R, L, C, M",
                            size=10, pad=6, fill=BG, stroke=ACCENT, sw=1)
    elements.append(b1_info)

    # Зона 2: Розподілена область (Лінії передачі)
    elements.append(rect(z2_x, ax_y + 20, z2_w - 10, 220, fill="#fff7ed", stroke=ORANGE, sw=1.5, rx=6))
    elements.append(text(z2_x + (z2_w-10)/2, ax_y + 42, "РОЗПОДІЛЕНА МОДЕЛЬ", size=12, bold=True, color=ORANGE))
    elements.append(text(z2_x + (z2_w-10)/2, ax_y + 60, "d ~ λ  (0.1λ < d < 10λ)", size=11, bold=True, color=DARK))

    b2_info, _, _ = textbox(z2_x + (z2_w-10)/2, ax_y + 145,
                            "• Хвильове запізнення τ ~ T\n"
                            "• Відбиття та хвильовий опір Z₀\n"
                            "• Телеграфні рівняння (1D PDE)\n"
                            "• Коаксіал, полоскові лінії\n"
                            "• Матриці розсіювання (S-параметри)",
                            size=10, pad=6, fill=BG, stroke=ORANGE, sw=1)
    elements.append(b2_info)

    # Зона 3: Повнохвильова випромінювальна область
    elements.append(rect(z3_x, ax_y + 20, z3_w - 10, 220, fill="#fef2f2", stroke=RED, sw=1.5, rx=6))
    elements.append(text(z3_x + (z3_w-10)/2, ax_y + 42, "ПОВНОХВИЛЬОВА МОДЕЛЬ", size=12, bold=True, color=RED))
    elements.append(text(z3_x + (z3_w-10)/2, ax_y + 60, "d ≫ λ  (d > 10λ)", size=11, bold=True, color=DARK))

    b3_info, _, _ = textbox(z3_x + (z3_w-10)/2, ax_y + 145,
                            "• Вільні електромагнітні хвилі\n"
                            "• Повне випромінювання (Антени)\n"
                            "• Хвилеводи, резонатори\n"
                            "• 3D рівняння Максвелла (PDE)\n"
                            "• Чисельні методи (FEM / FDTD)",
                            size=10, pad=6, fill=BG, stroke=RED, sw=1)
    elements.append(b3_info)

    # Позначки на осі
    elements.append(line(z1_x + z1_w - 5, ax_y - 8, z1_x + z1_w - 5, ax_y + 8, color=DARK, sw=2))
    elements.append(text(z1_x + z1_w - 5, ax_y - 14, "d = 0.1 λ", size=10, bold=True, color=DARK))

    elements.append(line(z2_x + z2_w - 5, ax_y - 8, z2_x + z2_w - 5, ax_y + 8, color=DARK, sw=2))
    elements.append(text(z2_x + z2_w - 5, ax_y - 14, "d = 10 λ", size=10, bold=True, color=DARK))

    return render(os.path.join(IMG, "frequency-regimes.svg"), W, H, *elements)


if __name__ == "__main__":
    fig_lumped_vs_distributed()
    fig_maxwell_to_kirchhoff()
    fig_parasitic_model()
    fig_frequency_regimes()
    print("Всі 4 фігури згенеровано у ./img/")
