# -*- coding: utf-8 -*-
"""Фігури для теми switching-noise (шум імпульсного перетворювача).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b5763a"
PURPLE = "#8e44ad"
CYAN = "#00838f"


def cap(x, y, w=28, gap=8, color=INK, sw=3.0):
    """Конденсатор — дві паралельні пластини на вертикальній шині."""
    return (line(x - w / 2, y - gap / 2, x + w / 2, y - gap / 2, color=color, sw=sw) +
            line(x - w / 2, y + gap / 2, x + w / 2, y + gap / 2, color=color, sw=sw))


def coil(x1, y, x2, turns=4, color=COPPER, sw=2.4):
    """Котушка індуктивності — низка напівеліпсів/дуг."""
    seg = (x2 - x1) / turns
    d = "M %.1f %.1f " % (x1, y)
    for k in range(turns):
        d += "A %.1f %.1f 0 0 1 %.1f %.1f " % (seg / 2, seg * 0.55, x1 + seg * (k + 1), y)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


# ── 1. Два типи шуму: низькочастотні пульсації проти дзвіну ─────────────────
def fig_noise_types():
    W, H = 820, 420
    frags = []

    # Тло двох зон
    frags.append(rect(20, 45, 375, 355, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(rect(415, 45, 385, 355, fill="#fdf8f6", stroke="#fed7aa", sw=1.2, rx=8))

    # Заголовки колонок
    b1, _, _ = textbox(207, 72, "1. Низькочастотні пульсації (Ripple)", size=13,
                       fill="#e2e8f0", stroke="#64748b", bold=True)
    frags.append(b1)

    b2, _, _ = textbox(607, 72, "2. Високочастотний дзвін і сплески (Ringing)", size=13,
                       fill="#ffedd5", stroke="#ea580c", color="#c2410c", bold=True)
    frags.append(b2)

    # --- Ліва колонка: Пульсації (Ripple) ---
    # Осцилограма пульсацій (трикутна / плавна хвиля)
    y_sig1 = 150
    frags.append(line(45, y_sig1, 370, y_sig1, color="#94a3b8", sw=1, dash="3,3"))
    frags.append(text(45, y_sig1 - 10, "Vвих(t)", size=11, color=MUTED, anchor="start", bold=True))

    # Форма хвилі: плавний трикутник на частоті f_sw
    pts_ripple = [
        (60, 150), (100, 125), (140, 150), (180, 175), (220, 150),
        (260, 125), (300, 150), (340, 175), (370, 156)
    ]
    d_rip = "M " + " L ".join("%.1f %.1f" % p for p in pts_ripple)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d_rip, NEG))

    # Розмірні стрілки періоду T_sw та амплітуди ΔV
    frags.append(line(100, 115, 260, 115, color=LINE, sw=1.2))
    frags.append(line(100, 110, 100, 120, color=LINE, sw=1.2))
    frags.append(line(260, 110, 260, 120, color=LINE, sw=1.2))
    frags.append(text(180, 108, "T_sw = 1 / f_sw (0.2–2 МГц)", size=10, color=INK, bold=True))

    frags.append(line(360, 125, 360, 175, color=POS, sw=1.2))
    frags.append(text(365, 152, "ΔV_rip ≈ 10–50 мВ", size=10, color=POS, anchor="start", bold=True))

    # Опис причин і природи
    t_box1 = [
        "Природа: заряд і розряд вихідної ємності",
        "та струм трикутника крізь опір ESR.",
        "Частота: основна f_sw та перші гармоніки.",
        "Форма: детермінована, гладка пилкоподібна.",
        "Лікування: більша ємність Cout, менший ESR."
    ]
    frags.append(fitbox(35, 205, 345, 180, "\n".join(t_box1), size=12, pad=10,
                        fill="#ffffff", stroke="#94a3b8", sw=1))

    # --- Права колонка: Дзвін і сплески (Ringing & Spikes) ---
    # Осцилограма сплесків (гострий викид + затухаючий радіочастотний дзвін)
    y_sig2 = 150
    frags.append(line(435, y_sig2, 780, y_sig2, color="#94a3b8", sw=1, dash="3,3"))
    frags.append(text(435, y_sig2 - 10, "Vвих(t)", size=11, color=MUTED, anchor="start", bold=True))

    # Затухаючі синусоїди на кожному фронті перемикання
    pts_ring = [
        (445, 150), (455, 150),
        # перший спалах
        (458, 92), (463, 185), (468, 118), (473, 168), (478, 138), (483, 156), (488, 147), (493, 151), (500, 150),
        (550, 150),
        # другий спалах (інший фронт)
        (553, 200), (558, 110), (563, 175), (568, 132), (573, 160), (578, 144), (583, 153), (590, 150),
        (650, 150),
        # третій спалах
        (653, 94), (658, 182), (663, 122), (668, 165), (673, 140), (678, 155), (685, 150),
        (770, 150)
    ]
    d_ring = "M " + " L ".join("%.1f %.1f" % p for p in pts_ring)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_ring, POS))

    # Маркування викиду V_spike зверху над першим піком
    frags.append(line(458, 90, 458, 78, color=POS, sw=1.2))
    frags.append(text(458, 70, "V_spike (1–3 В)", size=10, color=POS, anchor="middle", bold=True))

    # Маркування частоти коливань f_ring над другим спалахом
    frags.append(text(640, 70, "f_ring ≈ 50–300 МГц (L_par × Coss)", size=10, color="#c2410c", anchor="middle", bold=True))

    # Опис причин і природи
    t_box2 = [
        "Природа: резонанс паразитної індуктивності",
        "доріжок L_par та ємності ключів Coss / Qrr.",
        "Частота: радіочастотний спектр (50–300 МГц).",
        "Форма: наносекундні голки та затухаючий дзвін.",
        "Лікування: RC-снубери, мала петля, LC-фільтри."
    ]
    frags.append(fitbox(430, 205, 355, 180, "\n".join(t_box2), size=12, pad=10,
                        fill="#ffffff", stroke="#f97316", sw=1))

    render(os.path.join(OUT, "noise-types-spectrum.svg"), W, H, *frags,
           title="Два компоненти шуму перетворювача: пульсації та комутаційний дзвін")


# ── 2. Диференційний шум проти синфазного ─────────────────────────────────────
def fig_noise_modes():
    W, H = 820, 420
    frags = []

    # Дві плашки: DM зліва, CM справа
    frags.append(rect(20, 45, 375, 355, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    frags.append(rect(415, 45, 385, 355, fill="#fdf4ff", stroke="#e879f9", sw=1.2, rx=8))

    # Заголовки
    b1, _, _ = textbox(207, 72, "Диференційний шум (Differential Mode)", size=13,
                       fill="#e2e8f0", stroke="#475569", color=INK, bold=True)
    frags.append(b1)

    b2, _, _ = textbox(607, 72, "Синфазний шум (Common Mode)", size=13,
                       fill="#fae8ff", stroke="#c026d3", color=PURPLE, bold=True)
    frags.append(b2)

    # --- Зліва: Диференційна завада (DM) ---
    # Джерело перетворювача
    frags.append(rect(40, 110, 80, 130, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    frags.append(text(80, 165, "SMPS\nДжерело", size=11, color="#0369a1", bold=True))

    # Навантаження
    frags.append(rect(300, 110, 75, 130, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(337, 165, "Load\nНавантаж.", size=11, color=INK, bold=True))

    # Провідники живлення (+ та -)
    frags.append(line(120, 140, 300, 140, color=POS, sw=2.5))
    frags.append(text(125, 132, "V+", size=11, color=POS, bold=True, anchor="start"))

    frags.append(line(120, 210, 300, 210, color=NEG, sw=2.5))
    frags.append(text(125, 226, "GND / V−", size=11, color=NEG, bold=True, anchor="start"))

    # Струм DM: стрілки назустріч у замкненому колі
    frags.append(arrow(180, 140, 240, 140, color=POS, sw=2.5))
    frags.append(text(210, 128, "I_DM →", size=11, color=POS, bold=True))

    frags.append(arrow(240, 210, 180, 210, color=NEG, sw=2.5))
    frags.append(text(210, 228, "← I_DM", size=11, color=NEG, bold=True))

    # Опис DM
    t_dm = [
        "Шлях: струм тече туди шиною живлення V+",
        "і повертається назад шиною землі GND.",
        "Утворює замкнене коло між проводами.",
        "Причина: пульсації струму комутації.",
        "Придушення: паралельні конденсатори (C),",
        "послідовні дроселі (L), феритові намистини."
    ]
    frags.append(fitbox(35, 255, 345, 135, "\n".join(t_dm), size=11, pad=8,
                        fill="#ffffff", stroke="#94a3b8", sw=1))

    # --- Справа: Синфазна завада (CM) ---
    # Джерело перетворювача
    frags.append(rect(435, 105, 80, 120, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=4))
    frags.append(text(475, 145, "SMPS\nКлюч SW", size=11, color=PURPLE, bold=True))

    # Навантаження
    frags.append(rect(695, 105, 85, 120, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(737, 155, "Load\nПрилад", size=11, color=INK, bold=True))

    # Провідники живлення (+ та -)
    frags.append(line(515, 130, 695, 130, color=PURPLE, sw=2))
    frags.append(line(515, 185, 695, 185, color=PURPLE, sw=2))

    # Струм CM: стрілки В ОДИН БІК на обох проводах!
    frags.append(arrow(570, 130, 630, 130, color=PURPLE, sw=2.2))
    frags.append(text(600, 120, "I_CM →", size=10, color=PURPLE, bold=True))

    frags.append(arrow(570, 185, 630, 185, color=PURPLE, sw=2.2))
    frags.append(text(600, 175, "I_CM →", size=10, color=PURPLE, bold=True))

    # Паразитна ємність до шасі / землі (C_par)
    frags.append(line(475, 225, 475, 245, color=PURPLE, sw=1.5))
    frags.append(cap(475, 252, w=24, gap=6, color=PURPLE, sw=2))
    frags.append(text(475, 240, "C_par", size=10, color=PURPLE, anchor="end", bold=True))

    frags.append(line(737, 225, 737, 245, color=PURPLE, sw=1.5))
    frags.append(cap(737, 252, w=24, gap=6, color=PURPLE, sw=2))
    frags.append(text(750, 240, "C_gnd", size=10, color=PURPLE, anchor="start", bold=True))

    # Шасі / Земля заземлення (зворотний шлях CM)
    y_earth = 270
    frags.append(line(435, y_earth, 780, y_earth, color="#475569", sw=2.5, dash="6,3"))
    frags.append(text(605, y_earth - 8, "Шасі / Корпус / Захисна земля (PE)", size=10, color="#475569", bold=True))
    frags.append(arrow(680, y_earth, 520, y_earth, color=PURPLE, sw=2.2))
    frags.append(text(600, y_earth + 14, "← Зворотний струм I_CM (2·I_CM)", size=10, color=PURPLE, bold=True))

    # Опис CM
    t_cm = [
        "Шлях: струм тече В ОДИН БІК обома проводами,",
        "а повертається крізь паразитну ємність C_par",
        "та спільну землю / металеве шасі приладу.",
        "Причина: різке dv/dt вузла SW до радіатора.",
        "Придушення: синфазний дросель (CM Choke),",
        "Y-конденсатори, екранування вузла SW."
    ]
    frags.append(fitbox(430, 292, 355, 100, "\n".join(t_cm), size=11, pad=6,
                        fill="#ffffff", stroke="#c026d3", sw=1))

    render(os.path.join(OUT, "noise-modes-dm-cm.svg"), W, H, *frags,
           title="Шляхи розповсюдження завад: диференційний та синфазний струми")


# ── 3. Методи придушення: снубер та вторинний LC-фільтр ─────────────────────
def fig_snubber_filter():
    W, H = 840, 440
    frags = []

    # 1. Вузол комутації SW і демпфер (снубер)
    frags.append(rect(20, 45, 340, 375, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=8))
    b1, _, _ = textbox(190, 70, "RC-снубер на вузлі SW", size=13,
                       fill="#fee2e2", stroke=POS, color="#991b1b", bold=True)
    frags.append(b1)

    # Силовий вхід Vвх
    frags.append(line(50, 110, 130, 110, color=POS, sw=2.5))
    frags.append(text(45, 110, "Vвх", size=12, color=POS, bold=True, anchor="end"))

    # Ключ Q1 (верхній)
    frags.append(rect(130, 95, 45, 30, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(152, 114, "Q1", size=11, color=NEG, bold=True))

    # Вузол SW
    frags.append(line(175, 110, 210, 110, color=POS, sw=2.5))
    frags.append(circle(210, 110, 4, fill=INK, stroke=INK))
    frags.append(text(210, 98, "SW", size=12, color="#b45309", bold=True))

    # Ключ Q2 (нижній) до землі
    frags.append(line(210, 110, 210, 160, color=LINE, sw=2))
    frags.append(rect(190, 160, 40, 30, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(210, 178, "Q2", size=11, color=NEG, bold=True))
    frags.append(line(210, 190, 210, 250, color=LINE, sw=2))
    frags.append(line(190, 250, 230, 250, color=LINE, sw=2.5)) # GND

    # RC-снубер паралельно нижньому ключу Q2 (SW → GND)
    frags.append(line(210, 135, 280, 135, color=POS, sw=1.8))
    frags.append(rect(265, 150, 30, 24, fill="#ffedd5", stroke="#ea580c", sw=1.5))
    frags.append(text(280, 165, "R_sn", size=10, color="#c2410c", bold=True))
    frags.append(line(280, 135, 280, 150, color=POS, sw=1.8))
    frags.append(line(280, 174, 280, 195, color=POS, sw=1.8))
    frags.append(cap(280, 203, w=22, gap=6, color=POS, sw=2))
    frags.append(text(302, 206, "C_sn", size=10, color=POS, bold=True))
    frags.append(line(280, 211, 280, 250, color=POS, sw=1.8))
    frags.append(line(210, 250, 280, 250, color=LINE, sw=2))

    # Рамка підсвітки снубера (без суцільного fill, щоб не накривати Q2)
    frags.append(rect(250, 125, 95, 110, fill="none", stroke=POS, sw=1.2, rx=4))

    # Опис снубера
    t_snub = [
        "Гасить дзвін 100–300 МГц на SW.",
        "R_sn ≈ √(L_par / C_par) (демпфування),",
        "C_sn ≈ 2–3 · C_par (блокує постійку).",
        "Втрати: P = C_sn · Vвх² · f_sw."
    ]
    frags.append(fitbox(30, 275, 320, 130, "\n".join(t_snub), size=11, pad=8,
                        fill="#ffffff", stroke="#fca5a5", sw=1))

    # 2. Основний вихід і вторинний фільтр
    frags.append(rect(380, 45, 440, 375, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=8))
    b2, _, _ = textbox(600, 70, "Вторинний LC / Pi-фільтр виходу", size=13,
                       fill="#e0f2fe", stroke="#0284c7", color="#0369a1", bold=True)
    frags.append(b2)

    # Головна котушка L1
    frags.append(coil(210, 110, 440, turns=4, color=COPPER, sw=2.5))
    frags.append(text(410, 95, "L1", size=12, color=COPPER, bold=True))

    # Головний конденсатор Cout1
    frags.append(line(440, 110, 480, 110, color=INK, sw=2))
    frags.append(line(480, 110, 480, 185, color=INK, sw=1.8))
    frags.append(cap(480, 193, w=24, gap=6, color=INK, sw=2.2))
    frags.append(text(480, 175, "C_out1", size=11, color=INK, bold=True))
    frags.append(line(480, 201, 480, 250, color=INK, sw=1.8))
    frags.append(line(440, 250, 780, 250, color=LINE, sw=2.5)) # спільна земля

    # Вторинний елемент: Феритова намистина або мала L2
    frags.append(line(480, 110, 540, 110, color=INK, sw=2))
    # Малюємо намистину (циліндр)
    frags.append(rect(540, 98, 48, 24, fill="#334155", stroke=INK, sw=1.5, rx=3))
    frags.append(text(564, 114, "Bead", size=10, color="#ffffff", bold=True))
    frags.append(line(588, 110, 660, 110, color=INK, sw=2))

    # Вторинний конденсатор Cout2 (кераміка C0G/X7R)
    frags.append(line(660, 110, 660, 185, color=FIELD, sw=1.8))
    frags.append(cap(660, 193, w=24, gap=6, color=FIELD, sw=2.2))
    frags.append(text(660, 175, "C_out2", size=11, color=FIELD, bold=True))
    frags.append(line(660, 201, 660, 250, color=FIELD, sw=1.8))

    # Демпфуючий ланцюг паралельно Cout2 (щоб уникнути резонансного піка Q)
    frags.append(line(660, 110, 730, 110, color=MUTED, sw=1.5))
    frags.append(rect(717, 135, 26, 22, fill="#f1f5f9", stroke=MUTED, sw=1.2))
    frags.append(text(730, 149, "R_d", size=9, color=MUTED, bold=True))
    frags.append(line(730, 110, 730, 135, color=MUTED, sw=1.5))
    frags.append(line(730, 157, 730, 185, color=MUTED, sw=1.5))
    frags.append(cap(730, 193, w=20, gap=5, color=MUTED, sw=1.8))
    frags.append(text(730, 175, "C_d", size=9, color=MUTED, bold=True))
    frags.append(line(730, 201, 730, 250, color=MUTED, sw=1.5))

    # Чистий вихід
    frags.append(line(730, 110, 790, 110, color=FIELD, sw=2.5))
    frags.append(text(795, 105, "V_clean", size=12, color=FIELD, bold=True, anchor="start"))
    frags.append(text(795, 122, "(тихе живлення)", size=9, color=MUTED, anchor="start"))

    # Опис вторинного фільтра
    t_filt = [
        "Зрізає залишки високочастотних голок.",
        "Bead/L2 ізолює високочастотні струми від навантаження.",
        "C_out2 шунтує залишковий шум.",
        "Увага: паралельний резонанс Bead + C_out може дати",
        "викид імпедансу — демпфують ланцюгом Rd-Cd."
    ]
    frags.append(fitbox(395, 275, 410, 130, "\n".join(t_filt), size=11, pad=8,
                        fill="#ffffff", stroke="#7dd3fc", sw=1))

    render(os.path.join(OUT, "snubber-and-postfilter.svg"), W, H, *frags,
           title="Схема придушення шуму: RC-снубер та вторинний LC-фільтр")


# ── 4. Гарячі петлі струму: Buck проти Boost ─────────────────────────────────
def fig_hot_loops():
    W, H = 820, 420
    frags = []

    # Ліва половина: Buck (вхідна петля гаряча)
    frags.append(rect(20, 45, 375, 355, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    b1, _, _ = textbox(207, 72, "Знижувальний (Buck): ВХІДНА гаряча петля", size=12,
                       fill="#fee2e2", stroke=POS, color="#991b1b", bold=True)
    frags.append(b1)

    # Buck вхід
    xin, ytop, ybot = 55, 115, 240
    frags.append(line(xin, ytop, xin, ybot, color=LINE, sw=2))
    frags.append(cap(xin, 175, color=COPPER, sw=2.5))
    frags.append(text(xin - 15, 178, "Свх", size=11, color=COPPER, bold=True, anchor="end"))

    # Верхній ключ Q1
    frags.append(line(xin, ytop, 140, ytop, color=POS, sw=3))
    frags.append(rect(140, ytop - 15, 35, 30, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(157, ytop + 4, "Q1", size=11, color=NEG, bold=True))

    # Вузол SW
    xsw = 220
    frags.append(line(175, ytop, xsw, ytop, color=POS, sw=3))
    frags.append(circle(xsw, ytop, 3.5, fill=INK, stroke=INK))
    frags.append(text(xsw, ytop - 12, "SW", size=11, color="#b45309", bold=True))

    # Нижній ключ Q2
    frags.append(line(xsw, ytop, xsw, 160, color=POS, sw=3))
    frags.append(rect(xsw - 17, 160, 35, 30, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(xsw, 178, "Q2", size=11, color=NEG, bold=True))
    frags.append(line(xsw, 190, xsw, ybot, color=POS, sw=3))
    frags.append(line(xin, ybot, xsw, ybot, color=POS, sw=3))

    # Підсвітка гарячої петлі Buck (контур без суцільного fill)
    frags.append(rect(45, 100, 190, 155, fill="none", stroke=POS, sw=1.5, rx=6))
    frags.append(text(138, 225, "di/dt петля: Свх → Q1 → Q2", size=10, color=POS, bold=True))

    # Котушка та вихід (холодна частина)
    frags.append(coil(xsw, ytop, 310, turns=3, color=MUTED, sw=1.8))
    frags.append(line(310, ytop, 360, ytop, color=MUTED, sw=1.5))
    frags.append(cap(360, 175, color=MUTED, sw=2))
    frags.append(line(360, ytop, 360, ybot, color=MUTED, sw=1.5))
    frags.append(line(xsw, ybot, 360, ybot, color=MUTED, sw=1.5))
    frags.append(text(360, ytop - 10, "Vвих", size=11, color=MUTED, bold=True))

    # Опис Buck
    t_bk = [
        "У Buck струм у Свх переривчастий (прямокутний):",
        "він стрибає від 0 до I_load за наносекунди.",
        "Правило: Свх ставлять упритул до Q1 і Q2!",
        "Площа вхідної петлі має бути мінімальною."
    ]
    frags.append(fitbox(35, 275, 345, 110, "\n".join(t_bk), size=11, pad=8,
                        fill="#ffffff", stroke="#fca5a5", sw=1))

    # Права половина: Boost (вихідна петля гаряча)
    frags.append(rect(415, 45, 385, 355, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    b2, _, _ = textbox(607, 72, "Підвищувальний (Boost): ВИХІДНА гаряча петля", size=12,
                       fill="#fee2e2", stroke=POS, color="#991b1b", bold=True)
    frags.append(b2)

    # Boost вхід (котушка на вході — холодна частина)
    xbin = 440
    frags.append(line(xbin, ytop, xbin + 20, ytop, color=MUTED, sw=1.5))
    frags.append(cap(xbin, 175, color=MUTED, sw=2))
    frags.append(line(xbin, ytop, xbin, ybot, color=MUTED, sw=1.5))
    frags.append(text(xbin, ytop - 10, "Vвх", size=11, color=MUTED, bold=True))
    frags.append(coil(xbin + 20, ytop, 530, turns=3, color=MUTED, sw=1.8))
    frags.append(line(xbin, ybot, 530, ybot, color=MUTED, sw=1.5))

    # Вузол SW у Boost
    xb_sw = 530
    frags.append(circle(xb_sw, ytop, 3.5, fill=INK, stroke=INK))
    frags.append(text(xb_sw, ytop - 12, "SW", size=11, color="#b45309", bold=True))

    # Ключ Q1 до землі
    frags.append(line(xb_sw, ytop, xb_sw, 160, color=POS, sw=3))
    frags.append(rect(xb_sw - 17, 160, 35, 30, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(xb_sw, 178, "Q1", size=11, color=NEG, bold=True))
    frags.append(line(xb_sw, 190, xb_sw, ybot, color=POS, sw=3))

    # Діод / синхронний ключ D1/Q2 на вихід
    frags.append(line(xb_sw, ytop, 610, ytop, color=POS, sw=3))
    frags.append(rect(610, ytop - 15, 35, 30, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(627, ytop + 4, "D / Q2", size=10, color=NEG, bold=True))

    # Вихідний конденсатор Cвих
    xb_out = 710
    frags.append(line(645, ytop, xb_out, ytop, color=POS, sw=3))
    frags.append(cap(xb_out, 175, color=COPPER, sw=2.5))
    frags.append(text(xb_out + 15, 178, "Свих", size=11, color=COPPER, bold=True, anchor="start"))
    frags.append(line(xb_out, ytop, xb_out, ybot, color=POS, sw=3))
    frags.append(line(xb_sw, ybot, xb_out, ybot, color=POS, sw=3))

    # Підсвітка гарячої петлі Boost (контур без суцільного fill)
    frags.append(rect(520, 100, 205, 155, fill="none", stroke=POS, sw=1.5, rx=6))
    frags.append(text(625, 225, "di/dt петля: Q1 → D → Свих", size=10, color=POS, bold=True))

    # Опис Boost
    t_bst = [
        "У Boost різаний струм тече у вихідне коло:",
        "діод різко вимикається, обриваючи струм.",
        "Правило: Свих ставлять упритул до діода й ключа!",
        "Гаряча петля зміщується на вихід перетворювача."
    ]
    frags.append(fitbox(430, 275, 355, 110, "\n".join(t_bst), size=11, pad=8,
                        fill="#ffffff", stroke="#fca5a5", sw=1))

    render(os.path.join(OUT, "hot-loops-didt.svg"), W, H, *frags,
           title="Гарячі комутаційні петлі з високим di/dt: порівняння Buck і Boost")


if __name__ == "__main__":
    fig_noise_types()
    fig_noise_modes()
    fig_snubber_filter()
    fig_hot_loops()
    print("Фігури успішно згенеровано.")
