# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір моделі розширюваності DH»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

PURPLE = "#7c3aed"
AMBER = "#b45309"
REDF = "#fdecea"     # червона заливка (небезпека)
GREENF = "#eef7f0"
BLUEF = "#eef2fb"
PURPF = "#f2ecfb"


def fig_extension_spectrum():
    """Влада росте вправо; радіус ураження вибухає лише де силу не стримано."""
    W, H = 1240, 540
    frags = []

    cols = [
        ("Конфіг", "дані", GREENF, FIELD),
        ("Декларативні\nправила", "логіка обмеженим\nсловником", BLUEF, NEG),
        ("Плагін\nу процесі", "довільний код\nусередині", REDF, POS),
        ("Поза процесом", "код за стіною\n(вебхук · sidecar)", PURPF, PURPLE),
    ]
    cx = [340, 590, 840, 1090]

    # ── роздільники стовпців ──
    for mx in (465, 715, 965):
        frags.append(line(mx, 150, mx, 470, color=MUTED, sw=1, dash="4,6"))

    # ── рядок 1: моделі ──
    for i, (name, desc, fill, col) in enumerate(cols):
        b, _, _ = textbox(cx[i], 108, name, size=15, bold=True, fill=fill, stroke=col, sw=1.8, min_w=190)
        frags.append(b)
        frags.append(text(cx[i], 150, desc.split("\n")[0], size=11.5, color=MUTED))
        if "\n" in desc:
            frags.append(text(cx[i], 168, desc.split("\n")[1], size=11.5, color=MUTED))

    # ── рядки-атрибути (ліва підпис-колонка + клітини) ──
    def rowlabel(y, s):
        frags.append(text(30, y, s, size=12.5, color=INK, anchor="start", bold=True))

    # влада / виразність
    rowlabel(228, "Влада / виразність")
    power = [("низька", FIELD, False), ("середня", AMBER, False),
             ("повна", POS, True), ("повна", POS, True)]
    for i, (w, c, b) in enumerate(power):
        frags.append(text(cx[i], 232, w, size=15, color=c, bold=b))

    # радіус ураження
    rowlabel(308, "Радіус ураження")
    blast = [("малий", FIELD, False), ("малий", FIELD, False),
             ("ВЕЛИКИЙ", POS, True), ("малий", FIELD, False)]
    for i, (w, c, b) in enumerate(blast):
        frags.append(text(cx[i], 312, w, size=15, color=c, bold=b))

    # чим стримано силу
    rowlabel(388, "Чим стримано силу")
    guard = [("вибором значень", MUTED), ("межею словника", NEG),
             ("нічим · довіра", POS), ("стіною процесу", PURPLE)]
    for i, (w, c) in enumerate(guard):
        frags.append(text(cx[i], 392, w, size=12.5, color=c))

    # ── підсумок ──
    frags.append(line(30, 430, 1210, 430, color=MUTED, sw=1, dash="5,6"))
    frags.append(text(620, 462,
                      "Влада росте вправо — а радіус вибухає ЛИШЕ де силу не стримано: правила тримають словником,",
                      size=12.5, color=INK))
    frags.append(text(620, 484,
                      "«поза процесом» — стіною, і тільки плагін у процесі не тримає нічим.",
                      size=12.5, color=INK))

    render(os.path.join(IMG, "extension-spectrum.svg"), W, H, *frags,
           title="Спектр моделей розширюваності")


def fig_blast_radius_inout():
    """У процесі стіни немає — біда переходить у господаря; поза процесом стіна ловить її."""
    W, H = 1200, 470
    frags = []

    frags.append(line(600, 40, 600, 440, color=MUTED, sw=1, dash="5,6"))

    # ══ Ліва панель: у процесі ══
    frags.append(text(300, 66, "У ПРОЦЕСІ — стіни немає", size=15, bold=True))
    frags.append(rect(70, 96, 470, 300, fill="#fbfcfd", stroke=LINE, sw=1.6))
    frags.append(text(300, 118, "процес хаба DH", size=12, color=MUTED))

    # чужий блок усередині
    b, _, _ = textbox(300, 250, "чужий драйвер\nу процесі", size=13, fill=REDF, stroke=POS, sw=1.8)
    frags.append(b)

    # біда розходиться по господарю (червоні стрілки назовні від блоку)
    frags.append(arrow(255, 228, 150, 165, color=POS, sw=2.0))
    frags.append(text(150, 150, "зависання потоку", size=11.5, color=POS))
    frags.append(arrow(360, 250, 486, 250, color=POS, sw=2.0))
    frags.append(text(432, 234, "крадіжка токена", size=11.5, color=POS))
    frags.append(arrow(300, 286, 300, 356, color=POS, sw=2.0))
    frags.append(text(300, 378, "падіння процесу", size=11.5, color=POS))

    # ══ Права панель: поза процесом ══
    frags.append(text(890, 66, "ПОЗА ПРОЦЕСОМ — стіна ловить біду", size=15, bold=True))

    # господар
    frags.append(rect(640, 150, 200, 200, fill="#fbfcfd", stroke=LINE, sw=1.6))
    frags.append(text(740, 250, "процес", size=13, color=INK))
    frags.append(text(740, 272, "хаба DH", size=13, color=INK))

    # стіна
    frags.append(rect(905, 120, 16, 260, fill="#d1d5db", stroke=MUTED, sw=1.2, rx=3))
    frags.append(text(913, 104, "стіна: процес / мережа", size=11, color=MUTED))

    # чужа коробка
    frags.append(rect(986, 150, 170, 200, fill=REDF, stroke=POS, sw=1.6))
    frags.append(text(1071, 224, "чужий", size=13, color=INK))
    frags.append(text(1071, 246, "адаптер", size=13, color=INK))

    # мережева лінія крізь стіну
    frags.append(arrow(840, 232, 903, 232, color=LINE, sw=1.8))
    frags.append(arrow(986, 250, 923, 250, color=MUTED, sw=1.8))
    frags.append(text(872, 218, "виклик →", size=11, color=MUTED, anchor="start"))
    frags.append(text(872, 300, "← таймаут", size=11, color=MUTED, anchor="start"))

    # збій контейнеровано в чужій коробці (упирається в стіну)
    frags.append(circle(1071, 300, 15, fill="#f8d7d2", stroke=POS, sw=1.6))
    frags.append(text(1071, 305, "збій", size=11, color=POS))
    frags.append(arrow(1053, 300, 927, 300, color=POS, sw=1.8))

    frags.append(text(890, 418, "ціна: затримка + часткова відмова — але хаб живий",
                      size=12, color=MUTED))

    render(os.path.join(IMG, "blast-radius-inout.svg"), W, H, *frags,
           title="Радіус ураження: у процесі проти поза процесом")


def fig_dh_extension_map():
    """Дві осі — довіра до автора й потрібна виразність — розводять потреби DH по моделях."""
    W, H = 940, 620
    ox, oy = 150, 530
    frags = []

    frags.append(arrow(ox, oy, 880, oy, color=LINE, sw=1.8))    # X →
    frags.append(arrow(ox, oy, ox, 90, color=LINE, sw=1.8))     # Y ↑

    # підписи осей
    frags.append(text(162, 108, "довільний код ↑", size=12, color=MUTED, anchor="start"))
    frags.append(text(162, 512, "вибір значення", size=12, color=MUTED, anchor="start"))
    frags.append(text(250, 556, "свій", size=12, color=MUTED))
    frags.append(text(520, 556, "зовнішній постачальник", size=12, color=MUTED))
    frags.append(text(800, 556, "незнайомий", size=12, color=MUTED))
    frags.append(text(500, 590, "хто пише розширення  →", size=13, color=MUTED))
    frags.append(text(60, 300, "потрібна", size=12, color=MUTED, anchor="start"))
    frags.append(text(60, 320, "виразність ↑", size=12, color=MUTED, anchor="start"))

    # потреби DH у координатах (довіра × виразність)
    b, _, _ = textbox(285, 460, "конфіг ·\nпрапорці", size=13, fill=GREENF, stroke=FIELD, sw=1.7)
    frags.append(b)
    b, _, _ = textbox(285, 185, "плагін-драйвер\nу процесі", size=13, fill=REDF, stroke=POS, sw=1.7)
    frags.append(b)
    b, _, _ = textbox(545, 175, "інтеграція\nпоза процесом", size=13, fill=PURPF, stroke=PURPLE, sw=1.7)
    frags.append(b)
    b, _, _ = textbox(760, 300, "декларативні\nправила\n(автоматизації)", size=13, fill=BLUEF, stroke=NEG, sw=1.7)
    frags.append(b)

    render(os.path.join(IMG, "dh-extension-map.svg"), W, H, *frags,
           title="Мапа вибору моделі розширюваності DH")


def fig_extensibility_pendulum():
    """Той самий маятник влада↔стримування — чотири рази за півстоліття."""
    W, H = 1200, 690
    frags = []

    # ── вертикальний роздільник влада | стримування ──
    frags.append(line(612, 100, 612, 662, color=MUTED, sw=1, dash="4,7"))

    # ── шапка: два боки осі ──
    frags.append(text(352, 80, "ВЛАДА — двері відчинили", size=14, bold=True, color=POS))
    frags.append(text(902, 80, "СТРИМУВАННЯ — відвоювали ізоляцією", size=14, bold=True, color=NEG))

    laneY = [180, 322, 464, 606]

    def era(y, l1, l2):
        frags.append(mtext(28, y - 8, [l1, l2], size=12.5, color=MUTED, anchor="start"))

    # ══ Смуга 1 — редактори: розмаху немає, бо автор = користувач ══
    era(laneY[0], "Розширювані", "редактори")
    b, _, _ = textbox(352, laneY[0], "EMACS · 1976\nмакрос у ядрі", size=13,
                      fill=GREENF, stroke=FIELD, sw=1.8, min_w=180)
    frags.append(b)
    frags.append(line(468, laneY[0], 772, laneY[0], color=FIELD, sw=1.6, dash="6,6"))
    frags.append(text(620, laneY[0] - 16, "межа довіри збіглася", size=11.5, color=FIELD))
    b, _, _ = textbox(902, laneY[0], "стримувати\nнічого не треба", size=13,
                      fill=GREENF, stroke=FIELD, sw=1.8, min_w=180)
    frags.append(b)

    # ══ Смуга 2 — офісні макроси: 27 років до стримування ══
    era(laneY[1], "Офісні", "макроси")
    b, _, _ = textbox(352, laneY[1], "Concept 1995\nMelissa 1999", size=13,
                      fill=REDF, stroke=POS, sw=1.8, min_w=180)
    frags.append(b)
    frags.append(arrow(468, laneY[1], 772, laneY[1], color=INK, sw=2.0))
    frags.append(text(620, laneY[1] - 16, "≈ 27 років", size=13, bold=True, color=INK))
    frags.append(text(620, laneY[1] + 26, "чужий макрос у процесі", size=11.5, color=MUTED))
    b, _, _ = textbox(902, laneY[1], "2022: макроси\nз мережі — блок", size=13,
                      fill=BLUEF, stroke=NEG, sw=1.8, min_w=180)
    frags.append(b)

    # ══ Смуга 3 — плагіни браузера: 20 років до видалення ══
    era(laneY[2], "Плагіни", "браузера")
    b, _, _ = textbox(352, laneY[2], "NPAPI · 1995\nнативний код з сайту", size=13,
                      fill=REDF, stroke=POS, sw=1.8, min_w=180)
    frags.append(b)
    frags.append(arrow(468, laneY[2], 772, laneY[2], color=INK, sw=2.0))
    frags.append(text(620, laneY[2] - 16, "≈ 20 років", size=13, bold=True, color=INK))
    frags.append(text(620, laneY[2] + 26, "код у процесі браузера", size=11.5, color=MUTED))
    b, _, _ = textbox(902, laneY[2], "2015 NPAPI знято\n2021 Flash вимкнено", size=13,
                      fill=BLUEF, stroke=NEG, sw=1.8, min_w=180)
    frags.append(b)

    # ══ Смуга 4 — пісочниця: влада і стримування разом ══
    era(laneY[3], "Пісочниця", "(синтез)")
    b, _, _ = textbox(628, laneY[3], "NaCl 2011 → asm.js 2013 →\nWASM 2017 → WASI 2019",
                      size=12.5, fill=GREENF, stroke=FIELD, sw=1.9, min_w=300)
    frags.append(b)
    frags.append(arrow(792, laneY[3], 852, laneY[3], color=FIELD, sw=1.8))
    frags.append(mtext(978, laneY[3] - 8, ["влада + стримування", "разом, за побудовою"],
                       size=12.5, color=FIELD, bold=True))

    frags.append(line(28, 656, 1172, 656, color=MUTED, sw=1, dash="5,7"))
    frags.append(text(600, 682,
                      "Тричі однаковий розмах: влада → ціна → відвойована ізоляція. "
                      "Четвертий раз — обоє відразу.",
                      size=12.5, color=INK))

    render(os.path.join(IMG, "extensibility-pendulum.svg"), W, H, *frags,
           title="Маятник влада ↔ стримування — чотири розмахи за півстоліття")


def fig_action_three_lanes():
    """Одна дія DH трьома моделями: де біжить логіка, чим стримано, який радіус."""
    W, H = 1260, 560
    frags = []
    lanes = [160, 310, 460]

    # спільний тригер — та сама подія руху годує всі три доріжки
    b, _, _ = textbox(96, 310, "рух\nу коридорі\n(подія)", size=13, min_w=130,
                      fill=FILL, stroke=LINE, sw=1.6)
    frags.append(b)
    for cy in lanes:
        frags.append(arrow(164, 310, 298, cy, color=MUTED, sw=1.6))

    # (двигун, заливка, колір, guard, радіус, суб-радіус, колір-радіуса, big?)
    rows = [
        ("Обмежений рушій\nобхід дерева + пальне", BLUEF, NEG,
         "пальне + межа каскаду — не зациклиться",
         "Радіус: межа словника", "чужого коду нема — лише твої дієслова", FIELD, False),
        ("Плагін у процесі хаба", REDF, POS,
         "нічим не стримано — сама лише довіра",
         "Радіус: ВЕСЬ ХАБ", "зависання · виняток · крадіжка токена", POS, True),
        ("Хаб штовхає подію\nчужому адаптеру", PURPF, PURPLE,
         "таймаут + ізоляція — мертвий не тримає решту",
         "Радіус: за стіною", "чужий збій = твій таймаут", PURPLE, False),
    ]

    for cy, (engine, efill, ecol, guard, blast, sub, bcol, big) in zip(lanes, rows):
        b, ew, eh = textbox(465, cy, engine, size=13, min_w=290,
                            fill=efill, stroke=ecol, sw=1.8)
        frags.append(b)
        frags.append(text(465, cy + eh / 2 + 20, guard, size=11.5, color=ecol))

        if cy == 460:                                   # лише 3-тя доріжка має стіну
            frags.append(arrow(612, cy, 644, cy, color=LINE, sw=1.6))
            frags.append(rect(648, cy - 34, 12, 68, fill="#d1d5db", stroke=MUTED, sw=1.1, rx=3))
            frags.append(text(654, cy - 44, "стіна", size=10.5, color=MUTED))
            frags.append(arrow(664, cy, 786, cy, color=MUTED, sw=1.6))
        else:
            frags.append(arrow(612, cy, 786, cy, color=MUTED, sw=1.6))

        bs = 15 if big else 13.5
        b2, bw, bh = textbox(940, cy, blast, size=bs, min_w=300, bold=big,
                             fill=BG, stroke=bcol, sw=1.8 if big else 1.5, color=bcol)
        frags.append(b2)
        frags.append(text(940, cy + bh / 2 + 18, sub, size=11, color=MUTED))

    render(os.path.join(IMG, "action-three-lanes.svg"), W, H, *frags,
           title="Одна дія — три моделі: де біжить логіка й що буде, коли вона зламається")


def fig_hotpath_latency_scale():
    """Затримка на гарячому шляху — логарифмічна лінійка від нс до секунди."""
    import math
    W, H = 1300, 380
    x0, y = 110, 310
    dw = 122
    frags = []

    def X(ns):
        return x0 + math.log10(ns) * dw

    frags.append(line(x0 - 10, y, X(1e9) + 20, y, color=INK, sw=2))
    decades = [(1, "1 нс"), (10, "10 нс"), (100, "100 нс"), (1e3, "1 мкс"),
               (1e4, "10 мкс"), (1e5, "100 мкс"), (1e6, "1 мс"),
               (1e7, "10 мс"), (1e8, "100 мс"), (1e9, "1 с")]
    for val, lab in decades:
        x = X(val)
        frags.append(line(x, y - 6, x, y + 6, color=MUTED, sw=1.4))
        frags.append(text(x, y + 28, lab, size=11.5, color=MUTED))

    # (значення нс, підпис, колір, tier: 1 ближче / 2 вище)
    marks = [
        (50, "плагін у процесі\nпрямий виклик  ~50 нс", FIELD, 1),
        (5e3, "правило в рушії\nобхід дерева  ~5 мкс", NEG, 2),
        (5e5, "вебхук — та сама мережа\n~0.5 мс", AMBER, 1),
        (1.5e8, "вебхук — інший континент\n~150 мс", POS, 2),
    ]
    for val, lab, col, tier in marks:
        x = X(val)
        frags.append(circle(x, y, 6, fill=col, stroke=col, sw=1))
        cyb = 220 if tier == 1 else 125
        frags.append(line(x, y - 8, x, cyb + 26, color=col, sw=1.4, dash="3,4"))
        b, bw, bh = textbox(x, cyb, lab, size=12, fill=BG, stroke=col, sw=1.5, color=INK)
        frags.append(b)

    xa, xb = X(50), X(1.5e8)
    frags.append(line(xa, 72, xb, 72, color=MUTED, sw=1.3))
    frags.append(line(xa, 72, xa, 80, color=MUTED, sw=1.3))
    frags.append(line(xb, 72, xb, 80, color=MUTED, sw=1.3))
    frags.append(text((xa + xb) / 2, 63, "≈ 6–7 порядків різниці", size=12.5, color=INK, bold=True))

    render(os.path.join(IMG, "hotpath-latency-scale.svg"), W, H, *frags,
           title="Затримка на гарячому шляху: наносекунди виклику проти мілісекунд мережі")


if __name__ == "__main__":
    fig_extension_spectrum()
    fig_blast_radius_inout()
    fig_dh_extension_map()
    fig_extensibility_pendulum()
    fig_action_three_lanes()
    fig_hotpath_latency_scale()
    print("OK: extension-spectrum.svg, blast-radius-inout.svg, dh-extension-map.svg, "
          "extensibility-pendulum.svg, action-three-lanes.svg, hotpath-latency-scale.svg")
