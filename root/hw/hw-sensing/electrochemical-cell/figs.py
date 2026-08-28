# -*- coding: utf-8 -*-
"""Фігури до теми «Електрохімічна комірка: CO, O2».
Запуск:  python figs.py   → створює SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WARM = "#c0392b"
COOL = "#2457d6"
GOLD = "#d97706"
GRAY = "#4b5563"
GREEN = "#15803d"
DARK = "#1e293b"


# ── 1. Внутрішня будова 3-електродної електрохімічної комірки ────────────────
def fig_cell_structure():
    W, H = 880, 500
    f = [text(W / 2, 28, "Внутрішня будова амперометричної триелектродної газової комірки", size=15, bold=True)]

    # Корпус комірки
    cx, cy, cw, ch = 50, 75, 440, 375
    f.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke=LINE, sw=2, rx=10))

    # Вхідний капіляр (дифузійний бар'єр над корпусом)
    f.append(rect(cx + cw / 2 - 30, cy - 25, 60, 25, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=3))
    f.append(line(cx + cw / 2, cy - 42, cx + cw / 2, cy - 25, color=COOL, sw=2))
    f.append(text(cx + cw / 2, cy - 48, "Аналізований газ (CO, O₂, NO₂)", size=11, bold=True, color=COOL))

    # Дифузійний отвір і пориста мембрана
    f.append(rect(cx + 40, cy + 20, cw - 80, 18, fill="#cbd5e1", stroke="#94a3b8", sw=1.2, rx=2))
    f.append(text(cx + cw / 2, cy + 33, "Гідрофобна пориста PTFE-мембрана", size=10.5, color=DARK))

    # Робочий електрод (WE)
    f.append(rect(cx + 40, cy + 45, cw - 80, 22, fill="#fef3c7", stroke=GOLD, sw=1.5, rx=3))
    f.append(text(cx + cw / 2, cy + 60, "Робочий електрод (WE): Pt-чорнь / каталізатор", size=11.5, bold=True, color="#92400e"))

    # Хімічний фільтр (наприклад, активоване вугілля)
    f.append(rect(cx + 50, cy + 80, cw - 100, 35, fill="#e2e8f0", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(cx + cw / 2, cy + 102, "Селективний хімічний фільтр (поглинач SO₂, H₂S, VOC)", size=10.5, color=GRAY))

    # Резервуар з електролітом і сепаратором
    f.append(rect(cx + 30, cy + 130, cw - 60, 195, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    f.append(text(cx + cw / 2, cy + 150, "Рідкий кислотний електроліт (H₂SO₄) у пористому ґноті", size=11, bold=True, color=COOL))

    # Електрод порівняння (RE)
    f.append(rect(cx + 60, cy + 180, cw - 120, 22, fill="#dcfce7", stroke=GREEN, sw=1.5, rx=3))
    f.append(text(cx + cw / 2, cy + 195, "Електрод порівняння (RE): стабільний потенціал (I = 0)", size=11, bold=True, color=GREEN))

    # Допоміжний електрод (CE)
    f.append(rect(cx + 60, cy + 255, cw - 120, 22, fill="#fee2e2", stroke=WARM, sw=1.5, rx=3))
    f.append(text(cx + cw / 2, cy + 270, "Допоміжний електрод (CE): балансує струм комірки", size=11, bold=True, color=WARM))

    # Виводи контактів знизу
    f.append(line(cx + 80, cy + 67, cx + 80, cy + ch + 20, color=GOLD, sw=2))
    f.append(circle(cx + 80, cy + ch + 20, 5, fill=GOLD, stroke=LINE, sw=1.5))
    f.append(text(cx + 80, cy + ch + 36, "WE", size=12, bold=True, color=GOLD))

    f.append(line(cx + cw / 2, cy + 202, cx + cw / 2, cy + ch + 20, color=GREEN, sw=2))
    f.append(circle(cx + cw / 2, cy + ch + 20, 5, fill=GREEN, stroke=LINE, sw=1.5))
    f.append(text(cx + cw / 2, cy + ch + 36, "RE", size=12, bold=True, color=GREEN))

    f.append(line(cx + cw - 80, cy + 277, cx + cw - 80, cy + ch + 20, color=WARM, sw=2))
    f.append(circle(cx + cw - 80, cy + ch + 20, 5, fill=WARM, stroke=LINE, sw=1.5))
    f.append(text(cx + cw - 80, cy + ch + 36, "CE", size=12, bold=True, color=WARM))

    # Права панель — пояснення ролей
    rx0, ry0, rw, rh = 525, 75, 310, 375
    f.append(rect(rx0, ry0, rw, rh, fill="#ffffff", stroke="#cbd5e1", sw=1.4, rx=8))
    f.append(text(rx0 + rw / 2, ry0 + 26, "Функції електродів", size=13, bold=True, color=DARK))

    b1, _, _ = textbox(rx0 + rw / 2, ry0 + 78,
                       "WE (Робочий електрод):\n"
                       "Трикапілярна межа газ/метал/рідина.\n"
                       "Тут іде окиснення CO чи відновлення O₂.\n"
                       "Струм I_WE строго ∝ концентрації газу.",
                       size=10.5, pad=6, fill="#fef3c7", stroke=GOLD, min_w=280)
    f.append(b1)

    b2, _, _ = textbox(rx0 + rw / 2, ry0 + 168,
                       "RE (Електрод порівняння):\n"
                       "Неполяризовний електрод з фіксованим\n"
                       "потенціалом рівноваги. Струм у RE = 0,\n"
                       "тому падіння I·R на ньому немає.",
                       size=10.5, pad=6, fill="#dcfce7", stroke=GREEN, min_w=280)
    f.append(b2)

    b3, _, _ = textbox(rx0 + rw / 2, ry0 + 258,
                       "CE (Допоміжний електрод):\n"
                       "Замикає струмове коло в електроліті.\n"
                       "Потенціостат жене через CE струм I_CE = -I_WE,\n"
                       "утримуючи напругу між WE та RE стабільною.",
                       size=10.5, pad=6, fill="#fee2e2", stroke=WARM, min_w=280)
    f.append(b3)

    b4, _, _ = textbox(rx0 + rw / 2, ry0 + 340,
                       "Дифузійне обмеження:\n"
                       "Швидкість реакції на каталізаторі >> дифузії.\n"
                       "Тому струм лінійно пропорційний [Газу].",
                       size=10, pad=5, fill="#eff6ff", stroke="#93c5fd", min_w=280)
    f.append(b4)

    render(os.path.join(IMG, "electrochemical-cell-structure.svg"), W, H, *f)
    print("Generated electrochemical-cell-structure.svg")


# ── 2. Механізм окисно-відновних реакцій на трифазній межі ──────────────────
def fig_redox_mechanism():
    W, H = 860, 420
    f = [text(W / 2, 26, "Кінетика реакцій на трифазній межі розділу фаз (газ / каталізатор / електроліт)", size=15, bold=True)]

    # Ліва панель: Окиснення CO
    lx0, ly0, pw, ph = 24, 50, 395, 350
    f.append(rect(lx0, ly0, pw, ph, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(lx0 + pw / 2, ly0 + 24, "Окиснення CO (Робочий електрод WE)", size=13, bold=True, color=GOLD))
    f.append(text(lx0 + pw / 2, ly0 + 44, "CO + H₂O → CO₂ + 2H⁺ + 2e⁻  (n = 2)", size=11.5, bold=True, color="#92400e"))

    # Схема часток на WE
    bx0, by0 = lx0 + 20, ly0 + 60
    f.append(rect(bx0, by0, 355, 170, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(rect(bx0, by0, 355, 45, fill="#fef9c3", stroke="#fde047", sw=1))
    f.append(text(bx0 + 177, by0 + 26, "Газова фаза: молекули CO дифундують крізь пори", size=10.5, color="#854d0e"))

    # Каталізатор (Pt гранули)
    f.append(rect(bx0, by0 + 45, 355, 30, fill="#334155", stroke=DARK, sw=1))
    f.append(text(bx0 + 177, by0 + 64, "Твердий каталізатор (Pt-чорнь) — провідник електронів", size=10.5, bold=True, color="#ffffff"))

    # Електроліт
    f.append(rect(bx0, by0 + 75, 355, 95, fill="#eff6ff", stroke="#93c5fd", sw=1))
    f.append(text(bx0 + 177, by0 + 95, "Рідкий електроліт (H₂SO₄ / H₂O) — провідник іонів H⁺", size=10.5, color=COOL))

    # Стрілки реакції CO
    f.append(arrow(bx0 + 70, by0 + 35, bx0 + 70, by0 + 55, color=GOLD, sw=2))
    f.append(text(bx0 + 70, by0 + 20, "CO", size=11, bold=True, color="#b45309"))

    f.append(arrow(bx0 + 100, by0 + 60, bx0 + 160, by0 + 60, color=GOLD, sw=2))
    f.append(text(bx0 + 130, by0 + 52, "2e⁻ → коло", size=10.5, bold=True, color=GOLD))

    f.append(arrow(bx0 + 70, by0 + 75, bx0 + 70, by0 + 120, color=COOL, sw=2))
    f.append(text(bx0 + 100, by0 + 115, "2H⁺ (в розчин)", size=10.5, bold=True, color=COOL))

    f.append(arrow(bx0 + 250, by0 + 60, bx0 + 250, by0 + 25, color=DARK, sw=2))
    f.append(text(bx0 + 250, by0 + 16, "CO₂ (вихід)", size=10.5, bold=True, color=DARK))

    b_co, _, _ = textbox(lx0 + pw / 2, ly0 + 290,
                         "Реакція на протилежному CE (відновлення кисню):\n"
                         "½O₂ + 2H⁺ + 2e⁻ → H₂O\n"
                         "Сумарно: CO + ½O₂ → CO₂ (мікропаливний елемент).\n"
                         "Струм виходить з WE у зовнішнє коло (I_WE > 0).",
                         size=10, pad=6, fill="#fffbeb", stroke="#fcd34d", min_w=365)
    f.append(b_co)

    # Права панель: Відновлення O2 / NO2
    rx0, ry0 = 441, 50
    f.append(rect(rx0, ry0, pw, ph, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(rx0 + pw / 2, ry0 + 24, "Відновлення O₂ або NO₂ (Катодний процес)", size=13, bold=True, color=COOL))
    f.append(text(rx0 + pw / 2, ry0 + 44, "O₂ + 4H⁺ + 4e⁻ → 2H₂O  або  NO₂ + 2H⁺ + 2e⁻ → NO + H₂O", size=10.5, bold=True, color=COOL))

    # Схема часток на O2/NO2
    rbx0, rby0 = rx0 + 20, ry0 + 60
    f.append(rect(rbx0, rby0, 355, 170, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(rect(rbx0, rby0, 355, 45, fill="#eff6ff", stroke="#bfdbfe", sw=1))
    f.append(text(rbx0 + 177, rby0 + 26, "Газова фаза: O₂ або NO₂ дифундує до каталізатора", size=10.5, color=COOL))

    # Каталізатор
    f.append(rect(rbx0, rby0 + 45, 355, 30, fill="#334155", stroke=DARK, sw=1))
    f.append(text(rbx0 + 177, rby0 + 64, "Твердий каталізатор (Pt / Au) під негативним зміщенням", size=10.5, bold=True, color="#ffffff"))

    # Електроліт
    f.append(rect(rbx0, rby0 + 75, 355, 95, fill="#f0fdf4", stroke="#bbf7d0", sw=1))
    f.append(text(rbx0 + 177, rby0 + 95, "Електроліт постачає іони H⁺ або OH⁻", size=10.5, color=GREEN))

    # Стрілки реакції O2
    f.append(arrow(rbx0 + 70, rby0 + 35, rbx0 + 70, rby0 + 55, color=COOL, sw=2))
    f.append(text(rbx0 + 70, rby0 + 20, "O₂", size=11, bold=True, color=COOL))

    f.append(arrow(rbx0 + 200, rby0 + 60, rbx0 + 130, rby0 + 60, color=WARM, sw=2))
    f.append(text(rbx0 + 165, rby0 + 52, "4e⁻ з кола", size=10.5, bold=True, color=WARM))

    f.append(arrow(rbx0 + 70, rby0 + 135, rbx0 + 70, rby0 + 85, color=GREEN, sw=2))
    f.append(text(rbx0 + 105, rby0 + 125, "4H⁺ (споживаються)", size=10.5, bold=True, color=GREEN))

    f.append(arrow(rbx0 + 260, rby0 + 75, rbx0 + 260, rby0 + 125, color=COOL, sw=2))
    f.append(text(rbx0 + 260, rby0 + 140, "2H₂O утворюється", size=10.5, bold=True, color=COOL))

    b_o2, _, _ = textbox(rx0 + pw / 2, ry0 + 290,
                         "Реакція на протилежному CE (окиснення води):\n"
                         "2H₂O → O₂ + 4H⁺ + 4e⁻\n"
                         "Потребує негативного зміщення V_bias (наприклад, −600 мВ).\n"
                         "Струм входить у WE із зовнішнього кола (I_WE < 0).",
                         size=10, pad=6, fill="#eff6ff", stroke="#93c5fd", min_w=365)
    f.append(b_o2)

    render(os.path.join(IMG, "redox-reaction-mechanism.svg"), W, H, *f)
    print("Generated redox-reaction-mechanism.svg")


# ── 3. Дифузійний профіль газу за 1-м законом Фіка ──────────────────────────
def fig_diffusion_fick():
    W, H = 840, 400
    f = [text(W / 2, 28, "Дифузійне обмеження швидкості: профіль концентрації газу в капілярі", size=15, bold=True)]

    # Координатні осі графіка
    gx0, gy0, gw, gh = 90, 70, 420, 240
    f.append(rect(gx0, gy0, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))

    # Сітка
    for ystep in range(1, 5):
        yval = gy0 + gh - ystep * (gh / 4)
        f.append(line(gx0, yval, gx0 + gw, yval, color="#f1f5f9", sw=1))

    # Осі
    f.append(line(gx0, gy0 + gh, gx0 + gw + 20, gy0 + gh, color=DARK, sw=1.8))
    f.append(arrow(gx0 + gw + 20, gy0 + gh, gx0 + gw + 35, gy0 + gh, color=DARK, sw=1.8))
    f.append(text(gx0 + gw + 25, gy0 + gh + 22, "Відстань у капілярі (x)", size=11, bold=True, color=DARK))

    f.append(line(gx0, gy0 + gh, gx0, gy0 - 15, color=DARK, sw=1.8))
    f.append(arrow(gx0, gy0 - 15, gx0, gy0 - 25, color=DARK, sw=1.8))
    f.append(text(gx0 - 15, gy0 - 18, "Концентрація C(x)", size=11, bold=True, color=DARK, anchor="end"))

    # Позначки на осі X: x=0 (вхід з атмосфери), x=δ (каталізатор WE)
    f.append(line(gx0, gy0 + gh, gx0, gy0 + gh + 6, color=DARK, sw=1.5))
    f.append(text(gx0, gy0 + gh + 18, "x = 0 (Повітря)", size=11, color=GRAY))

    f.append(line(gx0 + gw, gy0 + gh, gx0 + gw, gy0 + gh + 6, color=DARK, sw=1.5))
    f.append(text(gx0 + gw, gy0 + gh + 18, "x = δ (Каталізатор WE)", size=11, bold=True, color=GOLD))

    # Лінійний спад концентрації C(x)
    f.append(line(gx0, gy0 + 40, gx0 + gw, gy0 + gh, color=WARM, sw=3))
    f.append(circle(gx0, gy0 + 40, 5, fill=WARM, stroke=DARK, sw=1.5))
    f.append(text(gx0 + 10, gy0 + 30, "C_bulk (зовнішня концентрація газу)", size=11, bold=True, color=WARM, anchor="start"))

    f.append(circle(gx0 + gw, gy0 + gh, 5, fill=GOLD, stroke=DARK, sw=1.5))
    f.append(text(gx0 + gw - 15, gy0 + gh - 15, "C_surface ≈ 0", size=11, bold=True, color=GOLD, anchor="end"))

    # Тіньова зона капіляра
    f.append(rect(gx0, gy0 + gh + 35, gw, 30, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(gx0 + gw / 2, gy0 + gh + 54, "Капілярний бар'єр завдовжки δ (дифузійний опір R_diff = δ / (D·A))", size=10.5, color=DARK))

    # Права панель з формулами
    fx0, fy0, fw, fh = 540, 70, 275, 295
    f.append(rect(fx0, fy0, fw, fh, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(fx0 + fw / 2, fy0 + 26, "Виведення струму комірки", size=13, bold=True, color=DARK))

    b_math, _, _ = textbox(fx0 + fw / 2, fy0 + 155,
                           "1. Закон дифузії Фіка:\n"
                           "J = -D · (dC/dx) = D · C_bulk / δ\n\n"
                           "2. Закон Фарадея:\n"
                           "I = n · F · A · J\n\n"
                           "3. Граничний струм:\n"
                           "I = (n·F·A·D / δ) · C_bulk\n\n"
                           "ВИСНОВОК:\n"
                           "Оскільки n, F, A, D, δ — сталі,\n"
                           "струм I СТРОГО ЛІНІЙНИЙ\n"
                           "до концентрації газу C_bulk!",
                           size=10.5, pad=8, fill="#ffffff", stroke="#93c5fd", min_w=255)
    f.append(b_math)

    render(os.path.join(IMG, "diffusion-profile-fick.svg"), W, H, *f)
    print("Generated diffusion-profile-fick.svg")


# ── 4. Повна схемотехніка потенціостата (Control Amp + TIA) ──────────────────
def fig_potentiostat_circuit():
    W, H = 880, 470
    f = [text(W / 2, 28, "Принципова схемотехніка 3-електродного потенціостата та TIA", size=15, bold=True)]

    # Блок сенсора (комірки)
    cx, cy, cw, ch = 290, 80, 240, 250
    f.append(rect(cx, cy, cw, ch, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(cx + cw / 2, cy + 24, "Електрохімічна комірка", size=13, bold=True, color=DARK))

    # Електроди всередині
    # CE зверху
    f.append(rect(cx + 30, cy + 50, cw - 60, 30, fill="#fee2e2", stroke=WARM, sw=1.4, rx=4))
    f.append(text(cx + cw / 2, cy + 70, "CE (Counter Electrode)", size=11, bold=True, color=WARM))

    # RE посередині
    f.append(rect(cx + 30, cy + 115, cw - 60, 30, fill="#dcfce7", stroke=GREEN, sw=1.4, rx=4))
    f.append(text(cx + cw / 2, cy + 135, "RE (Reference Electrode)", size=11, bold=True, color=GREEN))

    # WE знизу
    f.append(rect(cx + 30, cy + 180, cw - 60, 30, fill="#fef3c7", stroke=GOLD, sw=1.4, rx=4))
    f.append(text(cx + cw / 2, cy + 200, "WE (Working Electrode)", size=11, bold=True, color=GOLD))

    # Електроліт між ними
    f.append(text(cx + cw / 2, cy + 235, "Електроліт (H⁺ / OH⁻ транспорт)", size=10, color=GRAY))

    # ── Лівий ОП: Підсилювач керування (Control Amplifier) ──
    cax, cay = 130, 150
    f.append(rect(cax - 80, cay - 70, 170, 180, fill="#eff6ff", stroke="#93c5fd", sw=1.4, rx=6))
    f.append(text(cax + 5, cay - 50, "Control Amplifier (CA)", size=11, bold=True, color=COOL))

    # Трикутник ОП1
    op1_x, op1_y = cax, cay + 15
    f.append(line(op1_x - 30, op1_y - 30, op1_x - 30, op1_y + 30, color=DARK, sw=1.5))
    f.append(line(op1_x - 30, op1_y - 30, op1_x + 25, op1_y, color=DARK, sw=1.5))
    f.append(line(op1_x - 30, op1_y + 30, op1_x + 25, op1_y, color=DARK, sw=1.5))
    f.append(text(op1_x - 22, op1_y - 12, "−", size=14, bold=True, color=COOL))
    f.append(text(op1_x - 22, op1_y + 16, "+", size=14, bold=True, color=WARM))

    # Входи CA: "+" на V_bias, "−" на RE
    f.append(line(op1_x - 70, op1_y + 15, op1_x - 30, op1_y + 15, color=DARK, sw=1.5))
    f.append(circle(op1_x - 70, op1_y + 15, 3, fill=DARK))
    f.append(text(op1_x - 75, op1_y + 19, "V_bias", size=11, bold=True, color=DARK, anchor="end"))

    f.append(line(op1_x - 30, op1_y - 15, op1_x - 55, op1_y - 15, color=GREEN, sw=1.5))
    f.append(line(op1_x - 55, op1_y - 15, op1_x - 55, cy + 130, color=GREEN, sw=1.5))
    f.append(line(op1_x - 55, cy + 130, cx + 30, cy + 130, color=GREEN, sw=1.5))
    f.append(circle(cx + 30, cy + 130, 4, fill=GREEN))
    f.append(text(cax + 5, cy + 120, "Зворотний зв'язок RE (I_RE ≈ 0)", size=9.5, color=GREEN))

    # Вихід CA на CE через R_CE
    f.append(line(op1_x + 25, op1_y, op1_x + 55, op1_y, color=WARM, sw=1.5))
    f.append(line(op1_x + 55, op1_y, op1_x + 55, cy + 65, color=WARM, sw=1.5))
    f.append(line(op1_x + 55, cy + 65, cx + 30, cy + 65, color=WARM, sw=1.5))
    f.append(circle(cx + 30, cy + 65, 4, fill=WARM))
    f.append(text(cax + 5, cy + 55, "I_CE = -I_WE", size=10, bold=True, color=WARM))

    # ── Правий ОП: Трансімпедансний підсилювач (TIA) ──
    tiax, tiay = 670, 200
    f.append(rect(tiax - 50, tiay - 110, 220, 240, fill="#fffbeb", stroke="#fcd34d", sw=1.4, rx=6))
    f.append(text(tiax + 55, tiay - 90, "Transimpedance Amp (TIA)", size=11, bold=True, color="#92400e"))

    # Трикутник ОП2
    op2_x, op2_y = tiax + 30, tiay + 15
    f.append(line(op2_x - 30, op2_y - 30, op2_x - 30, op2_y + 30, color=DARK, sw=1.5))
    f.append(line(op2_x - 30, op2_y - 30, op2_x + 25, op2_y, color=DARK, sw=1.5))
    f.append(line(op2_x - 30, op2_y + 30, op2_x + 25, op2_y, color=DARK, sw=1.5))
    f.append(text(op2_x - 22, op2_y - 12, "−", size=14, bold=True, color=COOL))
    f.append(text(op2_x - 22, op2_y + 16, "+", size=14, bold=True, color=WARM))

    # Входи TIA: "−" до WE, "+" до V_ref
    f.append(line(cx + cw - 30, cy + 195, op2_x - 30, op2_y - 15, color=GOLD, sw=2))
    f.append(circle(cx + cw - 30, cy + 195, 4, fill=GOLD))
    f.append(text(cx + cw + 15, cy + 185, "I_WE", size=11, bold=True, color=GOLD))

    f.append(line(op2_x - 55, op2_y + 15, op2_x - 30, op2_y + 15, color=DARK, sw=1.5))
    f.append(circle(op2_x - 55, op2_y + 15, 3, fill=DARK))
    f.append(text(op2_x - 60, op2_y + 19, "V_ref (віртуальна земля)", size=10, bold=True, color=DARK, anchor="end"))

    # Зворотний зв'язок TIA: R_f паралельно з C_f
    f.append(line(op2_x - 15, op2_y - 15, op2_x - 15, op2_y - 65, color=DARK, sw=1.5))
    f.append(line(op2_x - 15, op2_y - 65, op2_x + 15, op2_y - 65, color=DARK, sw=1.5))

    # Резистор Rf
    f.append(rect(op2_x + 15, op2_y - 75, 40, 20, fill="#ffffff", stroke=DARK, sw=1.2))
    f.append(text(op2_x + 35, op2_y - 61, "R_f", size=10.5, bold=True, color=DARK))

    # Конденсатор Cf (паралельно)
    f.append(line(op2_x - 15, op2_y - 40, op2_x + 25, op2_y - 40, color=COOL, sw=1.2))
    f.append(line(op2_x + 25, op2_y - 48, op2_x + 25, op2_y - 32, color=COOL, sw=2))
    f.append(line(op2_x + 31, op2_y - 48, op2_x + 31, op2_y - 32, color=COOL, sw=2))
    f.append(line(op2_x + 31, op2_y - 40, op2_x + 70, op2_y - 40, color=COOL, sw=1.2))
    f.append(text(op2_x + 28, op2_y - 25, "C_f", size=10, bold=True, color=COOL))

    f.append(line(op2_x + 55, op2_y - 65, op2_x + 85, op2_y - 65, color=DARK, sw=1.5))
    f.append(line(op2_x + 85, op2_y - 65, op2_x + 85, op2_y, color=DARK, sw=1.5))
    f.append(line(op2_x + 70, op2_y - 40, op2_x + 85, op2_y - 40, color=COOL, sw=1.2))
    f.append(line(op2_x + 25, op2_y, op2_x + 115, op2_y, color=DARK, sw=1.8))
    f.append(arrow(op2_x + 115, op2_y, op2_x + 130, op2_y, color=DARK, sw=1.8))
    f.append(text(op2_x + 135, op2_y + 4, "V_out → АЦП", size=11, bold=True, color=DARK, anchor="start"))

    # Пояснення знизу
    bx0, by0, bw, bh = 50, 360, 780, 85
    f.append(rect(bx0, by0, bw, bh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(bx0 + bw / 2, by0 + 22, "Основні інваріанти схеми потенціостата:", size=11.5, bold=True, color=DARK))
    f.append(text(bx0 + bw / 2, by0 + 44, "1. V_RE стабілізується петлею CA на рівні V_bias відносно WE (I_RE = 0 pA, тому нема IR-падіння).", size=10.5, color=GREEN))
    f.append(text(bx0 + bw / 2, by0 + 64, "2. TIA утримує WE на потенціалі V_ref. Вихідна напруга: V_out = V_ref ± I_WE · R_f.", size=10.5, color="#92400e"))

    render(os.path.join(IMG, "potentiostat-circuit-topology.svg"), W, H, *f)
    print("Generated potentiostat-circuit-topology.svg")


# ── 5. Структурна блок-схема AFE LMP91000 ────────────────────────────────────
def fig_lmp91000_afe():
    W, H = 860, 460
    f = [text(W / 2, 28, "Архітектура інтегрованого аналогового фронтенду (AFE LMP91000)", size=15, bold=True)]

    # Корпус мікросхеми
    mx0, my0, mw, mh = 140, 60, 580, 370
    f.append(rect(mx0, my0, mw, mh, fill="#f8fafc", stroke=LINE, sw=2, rx=10))
    f.append(text(mx0 + mw / 2, my0 + 26, "LMP91000: Програмований потенціостат для електрохімічних комірок", size=13, bold=True, color=DARK))

    # Ліва частина всередині: I2C та керування
    f.append(rect(mx0 + 25, my0 + 50, 150, 90, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=6))
    f.append(text(mx0 + 100, my0 + 75, "I²C Інтерфейс", size=11, bold=True, color=COOL))
    f.append(text(mx0 + 100, my0 + 95, "Регістри конфігурації:", size=9.5, color=GRAY))
    f.append(text(mx0 + 100, my0 + 112, "TIACN, REFCN, MODECN", size=9.5, bold=True, color=DARK))

    # Зв'язок I2C ззовні
    f.append(line(mx0 - 40, my0 + 70, mx0 + 25, my0 + 70, color=COOL, sw=1.5))
    f.append(text(mx0 - 45, my0 + 74, "SDA", size=10, bold=True, color=COOL, anchor="end"))
    f.append(line(mx0 - 40, my0 + 95, mx0 + 25, my0 + 95, color=COOL, sw=1.5))
    f.append(text(mx0 - 45, my0 + 99, "SCL", size=10, bold=True, color=COOL, anchor="end"))

    # Джерело опорної напруги й Internal Zero DAC
    f.append(rect(mx0 + 25, my0 + 160, 150, 95, fill="#fef3c7", stroke=GOLD, sw=1.2, rx=6))
    f.append(text(mx0 + 100, my0 + 185, "Internal Zero DAC", size=11, bold=True, color=GOLD))
    f.append(text(mx0 + 100, my0 + 205, "V_ref / Zero Selection:", size=9.5, color=GRAY))
    f.append(text(mx0 + 100, my0 + 225, "20%, 50%, 67% від V_REF", size=9.5, bold=True, color="#92400e"))

    # Програмоване зміщення Bias Generator
    f.append(rect(mx0 + 25, my0 + 275, 150, 85, fill="#dcfce7", stroke=GREEN, sw=1.2, rx=6))
    f.append(text(mx0 + 100, my0 + 298, "Bias Generator", size=11, bold=True, color=GREEN))
    f.append(text(mx0 + 100, my0 + 318, "Зміщення: 0% .. 24% V_REF", size=9.5, color=GRAY))
    f.append(text(mx0 + 100, my0 + 338, "Полярність: ± (Direct / Reverse)", size=9.5, bold=True, color=GREEN))

    # Центральна частина: Control Amp
    f.append(rect(mx0 + 210, my0 + 80, 155, 125, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(mx0 + 287, my0 + 105, "Control Amp (CA)", size=11, bold=True, color=COOL))
    f.append(text(mx0 + 287, my0 + 125, "Керування CE", size=10, color=GRAY))

    # Виводи CE, RE праворуч
    f.append(line(mx0 + 365, my0 + 115, mx0 + mw + 40, my0 + 115, color=WARM, sw=2))
    f.append(circle(mx0 + mw + 40, my0 + 115, 4, fill=WARM))
    f.append(text(mx0 + mw + 48, my0 + 119, "CE (Counter)", size=11, bold=True, color=WARM, anchor="start"))

    f.append(line(mx0 + 365, my0 + 155, mx0 + mw + 40, my0 + 155, color=GREEN, sw=2))
    f.append(circle(mx0 + mw + 40, my0 + 155, 4, fill=GREEN))
    f.append(text(mx0 + mw + 48, my0 + 159, "RE (Reference)", size=11, bold=True, color=GREEN, anchor="start"))

    # Права частина: TIA з програмованим Rf
    f.append(rect(mx0 + 395, my0 + 210, 160, 135, fill="#fffbeb", stroke="#fcd34d", sw=1.2, rx=6))
    f.append(text(mx0 + 475, my0 + 235, "TIA (Підсилювач WE)", size=11, bold=True, color="#92400e"))
    f.append(text(mx0 + 475, my0 + 255, "R_f: 2.75 kΩ .. 350 kΩ", size=9.5, bold=True, color=DARK))
    f.append(text(mx0 + 475, my0 + 275, "R_L: 10 Ω .. 100 Ω", size=9.5, color=GRAY))

    # Вивід WE
    f.append(line(mx0 + mw + 40, my0 + 250, mx0 + 555, my0 + 250, color=GOLD, sw=2))
    f.append(circle(mx0 + mw + 40, my0 + 250, 4, fill=GOLD))
    f.append(text(mx0 + mw + 48, my0 + 254, "WE (Working)", size=11, bold=True, color=GOLD, anchor="start"))

    # Вивід VOUT до АЦП
    f.append(line(mx0 + 475, my0 + 345, mx0 + 475, my0 + mh + 25, color=DARK, sw=2))
    f.append(arrow(mx0 + 475, my0 + mh + 25, mx0 + 475, my0 + mh + 35, color=DARK, sw=2))
    f.append(text(mx0 + 475, my0 + mh + 48, "VOUT → АЦП МК", size=11, bold=True, color=DARK))

    # Закорочувальний FET (Shorting FET) між WE та RE
    f.append(rect(mx0 + 210, my0 + 230, 155, 60, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=4))
    f.append(text(mx0 + 287, my0 + 252, "FET-закорочувач WE-RE", size=10, bold=True, color=DARK))
    f.append(text(mx0 + 287, my0 + 270, "Активний у режимі Deep Sleep", size=9, color=GRAY))

    # Вбудований термосенсор
    f.append(rect(mx0 + 210, my0 + 310, 155, 50, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=4))
    f.append(text(mx0 + 287, my0 + 332, "Діодний термодавач", size=10, bold=True, color=WARM))
    f.append(text(mx0 + 287, my0 + 348, "Вивід на VOUT (-8.2 мВ/°C)", size=9, color=GRAY))

    render(os.path.join(IMG, "afe-lmp91000-block-diagram.svg"), W, H, *f)
    print("Generated afe-lmp91000-block-diagram.svg")


if __name__ == "__main__":
    fig_cell_structure()
    fig_redox_mechanism()
    fig_diffusion_fick()
    fig_potentiostat_circuit()
    fig_lmp91000_afe()
