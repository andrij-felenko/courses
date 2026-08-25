# -*- coding: utf-8 -*-
"""Фігури до теми «Узгодження імпедансу антени».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Кольори
WAVE = "#c0392b"      # падаюча хвиля / струм
WAVE_REF = "#2980b9"  # відбита хвиля
ACCENT = "#8e44ad"    # реактивність / реактивні елементи
GOOD = FIELD          # узгоджений стан
BORDER = INK

# ── 1. Неузгоджений фідер: виникнення стоячої хвилі та відбиття потужності ───────
def fig_mismatch_reflection():
    W, H = 760, 360
    f = [text(W / 2, 26, "Неузгодження у фідері: відбиття хвилі та утворення стоячої хвилі", size=15, bold=True)]

    # Схема передавача, фідеру та антени
    # Передавач (ліворуч)
    f.append(rect(30, 80, 120, 160, fill="#f4f6f7", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(90, 115, "Генератор", size=13, bold=True, color=INK))
    f.append(text(90, 138, "Z_g = 50 Ом", size=11, color=MUTED))
    f.append(circle(90, 180, 20, fill="none", stroke=INK, sw=1.5))
    f.append('<path d="M 78 180 Q 84 170 90 180 T 102 180" stroke="%s" stroke-width="1.5" fill="none"/>' % INK)

    # Лінія передачі (центр)
    f.append(line(150, 110, 580, 110, color=INK, sw=2)) # Верхній провідник
    f.append(line(150, 210, 580, 210, color=INK, sw=2)) # Нижній провідник (земля/екран)
    f.append(text(365, 95, "Фідер Z_0 = 50 Ом", size=12, bold=True, color=INK))

    # Хвильовий envelopes стоячої хвилі у фідері
    sine_pts_top = []
    sine_pts_bot = []
    for x_px in range(160, 575, 4):
        # 2 періоди стоячої хвилі
        phase = (x_px - 160) * (4 * math.pi / 415)
        # стояча хвиля з КСХ ~ 3
        v_env = 22 + 14 * math.cos(phase)
        sine_pts_top.append("%.1f,%.1f" % (x_px, 160 - v_env))
        sine_pts_bot.append("%.1f,%.1f" % (x_px, 160 + v_env))

    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' %
             (" L ".join(sine_pts_top), WAVE))
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' %
             (" L ".join(sine_pts_bot), WAVE))

    # Стрілки хвилі: Падаюча (червона вправо), Відбита (синя вліво)
    f.append(arrow(220, 135, 340, 135, color=WAVE, sw=2.5))
    f.append(text(280, 127, "Падаюча хвиля P_inc", size=11, bold=True, color=WAVE))

    f.append(arrow(340, 185, 220, 185, color=WAVE_REF, sw=2))
    f.append(text(280, 197, "Відбита хвиля P_ref", size=11, bold=True, color=WAVE_REF))

    # Антена (праворуч)
    f.append(rect(580, 80, 140, 160, fill="#fdfefe", stroke=ACCENT, sw=2, rx=6))
    f.append(text(650, 110, "Навантаження", size=12, bold=True, color=ACCENT))
    f.append(text(650, 130, "(Антена)", size=12, bold=True, color=ACCENT))
    f.append(text(650, 165, "Z_A = R_A + j X_A", size=12, bold=True, color=WAVE))
    f.append(text(650, 190, "(≠ Z_0)", size=12, bold=True, color=WAVE))

    # Позначки вузла та пучності
    f.append(text(264, 158, "V_max", size=10, bold=True, color=WAVE))
    f.append(text(368, 164, "V_min", size=10, bold=True, color=WAVE))

    # Інформаційна картка внизу
    f.append(fitbox(30, 260, 690, 80,
                    "Наслідки неузгодження (Z_A ≠ Z_0):\n"
                    "1. Коефіцієнт відбиття: Γ = (Z_A − Z_0) / (Z_A + Z_0)   |   "
                    "2. КСХ (VSWR): S = (1 + |Γ|) / (1 − |Γ|) > 1.0\n"
                    "3. Частина потужності відбивається назад до генератора, викликаючи перегрів передавача та втрати сигналу.",
                    size=11, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "mismatch-reflection.svg"), W, H, *f)


# ── 2. Топології L-подібного узгоджувального вузла ────────────────────────────
def fig_l_network_topologies():
    W, H = 760, 360
    f = [text(W / 2, 26, "Дві основні топології двоелементного L-вузла узгодження", size=15, bold=True)]

    # Ліва топологія: R_A > Z_0 (Паралельний елемент з боку навантаження)
    f.append(rect(20, 50, 350, 215, fill="#fcfcfd", stroke=MUTED, sw=1, rx=8))
    f.append(text(195, 72, "Топологія А: при R_A > Z_0", size=13, bold=True, color=ACCENT))
    f.append(text(195, 90, "(Паралельний елемент біля антени)", size=11, color=MUTED))

    # Лінії топології А
    f.append(line(40, 150, 110, 150, color=INK, sw=2))
    # Послідовний елемент X_s
    f.append(rect(110, 135, 60, 30, fill="#e8daef", stroke=ACCENT, sw=1.8))
    f.append(text(140, 155, "X_s", size=12, bold=True, color=ACCENT))
    f.append(line(170, 150, 290, 150, color=INK, sw=2))

    # Паралельний елемент B_p
    f.append(line(230, 150, 230, 175, color=INK, sw=1.8))
    f.append(rect(215, 175, 30, 45, fill="#e8daef", stroke=ACCENT, sw=1.8))
    f.append(text(230, 202, "B_p", size=12, bold=True, color=ACCENT))
    f.append(line(230, 220, 230, 240, color=INK, sw=1.8))

    # Входи та виходи A
    f.append(line(40, 240, 290, 240, color=INK, sw=2)) # земля
    f.append(circle(40, 150, 4, fill=INK, stroke=INK, sw=0))
    f.append(circle(40, 240, 4, fill=INK, stroke=INK, sw=0))
    f.append(text(40, 125, "Вхід Z_0", size=11, bold=True, color=INK, anchor="start"))

    f.append(rect(290, 125, 60, 130, fill="#fdfefe", stroke=BORDER, sw=1.5))
    f.append(text(320, 180, "Z_A", size=13, bold=True, color=WAVE))
    f.append(text(320, 200, "R_A > Z_0", size=10.5, color=MUTED))

    # Права топологія: R_A < Z_0 (Паралельний елемент з боку генератора)
    f.append(rect(390, 50, 350, 215, fill="#fcfcfd", stroke=MUTED, sw=1, rx=8))
    f.append(text(565, 72, "Топологія Б: при R_A < Z_0", size=13, bold=True, color=ACCENT))
    f.append(text(565, 90, "(Паралельний елемент біля фідеру)", size=11, color=MUTED))

    # Лінії топології Б
    f.append(line(410, 150, 470, 150, color=INK, sw=2))

    # Паралельний елемент B_p (ліворуч)
    f.append(line(470, 150, 470, 175, color=INK, sw=1.8))
    f.append(rect(455, 175, 30, 45, fill="#e8daef", stroke=ACCENT, sw=1.8))
    f.append(text(470, 202, "B_p", size=12, bold=True, color=ACCENT))
    f.append(line(470, 220, 470, 240, color=INK, sw=1.8))

    # Послідовний елемент X_s
    f.append(line(470, 150, 520, 150, color=INK, sw=2))
    f.append(rect(520, 135, 60, 30, fill="#e8daef", stroke=ACCENT, sw=1.8))
    f.append(text(550, 155, "X_s", size=12, bold=True, color=ACCENT))
    f.append(line(580, 150, 660, 150, color=INK, sw=2))

    # Входи та виходи Б
    f.append(line(410, 240, 660, 240, color=INK, sw=2)) # земля
    f.append(circle(410, 150, 4, fill=INK, stroke=INK, sw=0))
    f.append(circle(410, 240, 4, fill=INK, stroke=INK, sw=0))
    f.append(text(410, 125, "Вхід Z_0", size=11, bold=True, color=INK, anchor="start"))

    f.append(rect(660, 125, 60, 130, fill="#fdfefe", stroke=BORDER, sw=1.5))
    f.append(text(690, 180, "Z_A", size=13, bold=True, color=WAVE))
    f.append(text(690, 200, "R_A < Z_0", size=10.5, color=MUTED))

    # Узагальнення внизу
    f.append(fitbox(20, 278, 720, 70,
                    "Властивість L-вузла: 2 реактивні елементи (L та C) забезпечують точне узгодження на одній частоті.\n"
                    "Конфігурація ФНЧ (серійне L, паралельне C) додатково пригнічує вищі гармоніки генератора.",
                    size=11, fill="#ffffff", stroke=ACCENT))

    render(os.path.join(IMG, "l-network-topologies.svg"), W, H, *f)


# ── 3. Чвертьхвильовий трансформатор та паралельний шлейф ────────────────────
def fig_quarter_wave_stub():
    W, H = 760, 360
    f = [text(W / 2, 26, "Розподілене узгодження: чвертьхвильова лінія та узгоджувальний шлейф", size=15, bold=True)]

    # Ліва панель: Чвертьхвильовий трансформатор λ/4
    f.append(rect(20, 50, 350, 280, fill="#fcfcfd", stroke=MUTED, sw=1, rx=8))
    f.append(text(195, 74, "Чвертьхвильовий трансформатор (λ/4)", size=13, bold=True, color=INK))

    # Головна лінія
    f.append(line(40, 140, 120, 140, color=INK, sw=2))
    f.append(line(40, 210, 120, 210, color=INK, sw=2))
    f.append(text(80, 125, "Z_0", size=11, bold=True, color=INK))

    # Секція λ/4
    f.append(rect(120, 130, 150, 90, fill="#ebf5fb", stroke=WAVE_REF, sw=2))
    f.append(text(195, 165, "Лінія Z_w", size=13, bold=True, color=WAVE_REF))
    f.append(text(195, 190, "Довжина ℓ = λ / 4", size=11, bold=True, color=ACCENT))

    # Активне навантаження R_A
    f.append(rect(270, 125, 80, 100, fill="#fdfefe", stroke=BORDER, sw=1.5))
    f.append(text(310, 175, "R_A", size=13, bold=True, color=WAVE))

    f.append(fitbox(35, 238, 320, 78,
                    "Формула трансформації λ/4:\n"
                    "Z_w = √(Z_0 · R_A)\n\n"
                    "Трансформує активний опір R_A у хвильовий опір фідеру Z_0.",
                    size=11, fill="#ffffff", stroke=WAVE_REF))

    # Права панель: Шлейфове узгодження (Stub Matching)
    f.append(rect(390, 50, 350, 280, fill="#fcfcfd", stroke=MUTED, sw=1, rx=8))
    f.append(text(565, 74, "Паралельний узгоджувальний шлейф", size=13, bold=True, color=INK))

    # Головна лінія
    f.append(line(410, 140, 640, 140, color=INK, sw=2))
    f.append(line(410, 230, 640, 230, color=INK, sw=2))

    # Шлейф відгалуження (Stub)
    f.append(line(530, 140, 530, 75, color=ACCENT, sw=2.5))
    f.append(line(560, 140, 560, 75, color=ACCENT, sw=2.5))
    f.append(line(530, 75, 560, 75, color=ACCENT, sw=2.5)) # короткозамкнений кінець (K3)
    f.append(mtext(545, 62, "КЗ шлейф (Stub)", size=10.5, bold=True, color=ACCENT))

    # Відстані d та length_stub
    f.append(arrow(545, 155, 640, 155, color=INK, sw=1.2))
    f.append(arrow(545, 155, 450, 155, color=INK, sw=1.2))
    f.append(mtext(510, 172, "Відстань d", size=10.5, color=INK))

    # Навантаження Z_A
    f.append(rect(640, 125, 80, 120, fill="#fdfefe", stroke=BORDER, sw=1.5))
    f.append(mtext(680, 185, "Z_A", size=13, bold=True, color=WAVE))

    f.append(fitbox(405, 238, 320, 78,
                    "Принцип шлейфового узгодження:\n"
                    "1. Відстань d обирається так, щоб Re(Y) = 1/Z_0.\n"
                    "2. Шлейф створює реактивність −jB, що повністю компенсує +jB антени.",
                    size=10.5, fill="#ffffff", stroke=ACCENT))

    render(os.path.join(IMG, "quarter-wave-stub.svg"), W, H, *f)


# ── 4. Захист від струмів затікання: Балун (Current Balun) ────────────────────
def fig_balun_choke():
    W, H = 760, 360
    f = [text(W / 2, 26, "Синхронізація симетрії: робота струмового балуна (Choke Balun)", size=15, bold=True)]

    # Верхня панель: Без балуна (Струм затікання по зовнішній поверхні оплетки)
    f.append(rect(20, 50, 720, 135, fill="#fdfefe", stroke=MUTED, sw=1, rx=6))
    f.append(mtext(140, 68, "Без балуна (несиметричне живлення):", size=12, bold=True, color=WAVE))

    # Коаксіальний кабель
    f.append(rect(40, 95, 220, 30, fill="#d5dbdb", stroke=INK, sw=1.5)) # Оплетка
    f.append(line(40, 110, 270, 110, color=WAVE, sw=3)) # Центральна жила

    # Диполь
    f.append(line(270, 110, 270, 70, color=GOOD, sw=3.5)) # Верхнє плече
    f.append(line(270, 110, 270, 165, color=GOOD, sw=3.5)) # Нижнє плече
    f.append(mtext(330, 68, "Диполь (симетричний)", size=11, bold=True, color=GOOD))

    # Струми
    f.append(arrow(140, 103, 220, 103, color=WAVE, sw=2))
    f.append(mtext(180, 90, "I_1 (жила)", size=10, bold=True, color=WAVE))

    f.append(arrow(220, 117, 140, 117, color=WAVE_REF, sw=2))
    f.append(mtext(180, 130, "I_2 (внутр. оплетка)", size=10, bold=True, color=WAVE_REF))

    # Струм затікання I_3 по зовнішності кабелю!
    f.append(arrow(250, 132, 100, 132, color=WAVE, sw=2.5))
    f.append(mtext(380, 115, "Струм затікання I_3 = I_1 − I_2 розтікається по зовнішній оплетці!\nКабель випромінює як частина антени → спотворення ДН та завади.", size=10.5, color=WAVE, bold=True))

    # Нижня панель: З балуном (Феритове кільце / дросель)
    f.append(rect(20, 195, 720, 145, fill="#fcfcfd", stroke=MUTED, sw=1, rx=6))
    f.append(mtext(140, 212, "З струмовим балуном (Choke Balun 1:1):", size=12, bold=True, color=POS))

    # Коаксіальний кабель розділений на 2 частини, щоб феритове кільце не налазило як окремий блоковий рект
    f.append(rect(40, 245, 100, 30, fill="#d5dbdb", stroke=INK, sw=1.5))
    # Феритовий блочок між ними
    f.append('<rect x="145" y="238" width="85" height="44" rx="4" fill="#5d6d7e" stroke="%s" stroke-width="1.5"/>' % INK)
    f.append(mtext(187, 264, "Ферит", size=11, bold=True, color="#ffffff"))
    f.append(rect(235, 245, 35, 30, fill="#d5dbdb", stroke=INK, sw=1.5))

    f.append(line(40, 260, 270, 260, color=WAVE, sw=3))

    # Диполь
    f.append(line(270, 260, 270, 215, color=GOOD, sw=3.5))
    f.append(line(270, 260, 270, 315, color=GOOD, sw=3.5))

    # Рівні струми
    f.append(arrow(60, 253, 120, 253, color=POS, sw=2))
    f.append(mtext(90, 242, "I_1", size=10, bold=True, color=POS))

    f.append(arrow(120, 267, 60, 267, color=POS, sw=2))
    f.append(mtext(90, 279, "I_2 = I_1", size=10, bold=True, color=POS))

    f.append(fitbox(280, 230, 440, 95,
                    "Механізм придушення:\n"
                    "Ферит створює високий синфазний опір (Z_cm ≫ 500 Ом) для зовнішньої поверхні оплетки.\n"
                    "Струм затікання I_3 ≈ 0. Струми у плечах диполя строго симетричні (I_1 = I_2).",
                    size=10.5, fill="#ffffff", stroke=POS))

    render(os.path.join(IMG, "balun-choke.svg"), W, H, *f)


# ── 5. Узгодження на діаграмі Сміта: траєкторія реактивних елементів ──────────
def fig_smith_chart_l_match():
    W, H = 760, 360
    f = [text(W / 2, 26, "Узгодження на діаграмі Сміта: траєкторія від Z_A до центра 50 Ом", size=15, bold=True)]

    cx, cy, R = 230, 195, 120

    # Зовнішнє коло |Γ| = 1
    f.append(circle(cx, cy, R, fill="#fdfefe", stroke=INK, sw=2))
    f.append(line(cx - R, cy, cx + R, cy, color=INK, sw=1.5)) # Горизонтальна вісь активного опору

    # Внутрішній центр (50 Ом, z = 1.0)
    f.append(circle(cx, cy, 5, fill=POS, stroke=POS, sw=0))
    f.append(text(cx + 12, cy - 14, "Центр (50 Ом)", size=11, bold=True, color=POS, anchor="start"))

    # Коло активного опору R = 1 (проходить через центр та правий край)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' %
             (cx + R / 2, cy, R / 2, MUTED))

    # Коло провідності G = 1 (проходить через центр та лівий край)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' %
             (cx - R / 2, cy, R / 2, MUTED))

    # Початкова точка Z_A (наприклад, z = 0.4 - j1.0)
    zx, zy = cx - 40, cy + 80
    f.append(circle(zx, zy, 5, fill=WAVE, stroke=WAVE, sw=0))
    f.append(text(zx - 12, zy + 18, "Z_A (неузгоджено)", size=11, bold=True, color=WAVE, anchor="end"))

    # Проміжна точка при додаванні паралельного C (рух по колу G=const до кола R=1)
    px, py = cx + R / 2, cy + R / 2
    # Дуга 1: додавання паралельної реактивності
    f.append('<path d="M %d,%d A 75 75 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="2.5"/>' % (zx, zy, px, py, ACCENT))
    f.append(circle(px, py, 4, fill=ACCENT, stroke=ACCENT, sw=0))
    f.append(text(px + 10, py + 16, "Крок 1: +B_p (C)", size=10, bold=True, color=ACCENT, anchor="start"))

    # Дуга 2: додавання послідовної реактивності (рух по колу R=1 до центра)
    f.append('<path d="M %d,%d A 60 60 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="2.5"/>' % (px, py, cx, cy, POS))
    f.append(text(255, 225, "Крок 2: +X_s (L)", size=10, bold=True, color=POS, anchor="start"))

    # Картка з поясненням праворуч
    f.append(fitbox(410, 55, 330, 270,
                    "Як працює діаграма Сміта:\n\n"
                    "• Центр діаграми — точка ідеального узгодження (50 Ом, Γ = 0).\n"
                    "• Послідовна індуктивність L — рух за годинниковою стрілкою по колу R = const.\n"
                    "• Послідовна ємність C — рух проти годинникової стрілки по колу R = const.\n"
                    "• Паралельна ємність C — рух за годинниковою стрілкою по колу G = const.\n"
                    "• Паралельна індуктивність L — рух проти годинникової стрілки по колу G = const.\n\n"
                    "Будь-який імпеданс Z_A переводиться в центр за 2 кроки L-вузла!",
                    size=10.5, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "smith-chart-l-match.svg"), W, H, *f)


if __name__ == "__main__":
    fig_mismatch_reflection()
    fig_l_network_topologies()
    fig_quarter_wave_stub()
    fig_balun_choke()
    fig_smith_chart_l_match()
    print("OK: 5 figures created ->", IMG)
