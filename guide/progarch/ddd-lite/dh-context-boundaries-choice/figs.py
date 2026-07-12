# -*- coding: utf-8 -*-
"""Фігури до кроку «Де провести межі контекстів DH»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_word_fracture():
    """Слово «пристрій» роздвоюється: три значення + три різні годинники зміни."""
    W, H = 1000, 560
    frags = []

    # вузол-слово ліворуч
    b, bw, bh = textbox(150, 285, "«пристрій»?", size=20, bold=True,
                        fill="#fff8e1", stroke=MUTED, sw=2, min_w=180)
    node_right = 150 + bw / 2

    # три панелі праворуч, кожна зі своїм значенням і своїм годинником зміни
    panels = [
        (140, "#eafaf0", FIELD,
         ["ХАБ · КЕРУВАННЯ",
          "жива річ: можливості,",
          "поточний стан, команди",
          "тут живе інваріант",
          "змінюється: новий протокол / залізо"]),
        (285, "#eef2fb", NEG,
         ["ТЕЛЕМЕТРІЯ",
          "джерело ряду вимірів у часі",
          "ні стану, ні життєвого циклу",
          "змінюється: retention / аналітика"]),
        (430, "#fdecea", POS,
         ["БІЛІНГ · ЛІЧБА",
          "рядок тарифу проти плану дому",
          "байдуже, лампа то чи замок",
          "змінюється: ціни / плани"]),
    ]
    for cy, fillc, strokec, lines in panels:
        b2, w2, h2 = textbox(700, cy, "\n".join(lines), size=13,
                             fill=fillc, stroke=strokec, sw=2, min_w=360)
        left = 700 - w2 / 2
        frags.append(arrow(node_right + 8, 285, left - 10, cy, color=strokec, sw=2))
        frags.append(b2)

    frags.append(b)
    frags.append(text(W / 2, 540,
                      "де слово роздвоюється І годинники зміни різні — там і має пройти стіна",
                      size=13, color=MUTED))

    render(os.path.join(IMG, "word-fracture.svg"), W, H, *frags,
           title="Одне слово — три несумісні значення")


def fig_boundary_thickness():
    """Товщина стіни за сортом піддомену: ядро — товста, загальне — тонка."""
    W, H = 1000, 560
    frags = []

    def chip(cx, cy, label, fillc):
        b, w, h = textbox(cx, cy, label, size=13, fill=fillc, stroke=MUTED, sw=1.2)
        return b

    # смуга 1 — ЯДРО (найтовща стіна)
    frags.append(rect(70, 70, 700, 120, fill="#f4fbf6", stroke=FIELD, sw=4))
    frags.append(text(120, 96, "ЯДРО", size=15, bold=True, color=FIELD, anchor="start"))
    frags.append(chip(260, 140, "Керування\nпристроєм", "#eafaf0"))
    frags.append(chip(430, 140, "Автоматизації", "#eafaf0"))
    frags.append(chip(600, 140, "Твін дому", "#eafaf0"))
    frags.append(text(800, 130, "власна модель,", size=13, color=INK, anchor="start"))
    frags.append(text(800, 150, "найтовща стіна", size=13, color=INK, anchor="start"))

    # смуга 2 — ДОПОМІЖНЕ (середня стіна)
    frags.append(rect(70, 230, 700, 90, fill="#eef2fb", stroke=NEG, sw=2))
    frags.append(text(120, 256, "ДОПОМІЖНЕ", size=15, bold=True, color=NEG, anchor="start"))
    frags.append(chip(430, 278, "Телеметрія", "#eef2fb"))
    frags.append(text(800, 270, "пишемо самі,", size=13, color=INK, anchor="start"))
    frags.append(text(800, 290, "простіше", size=13, color=INK, anchor="start"))

    # смуга 3 — ЗАГАЛЬНЕ (тонка, штрихова стіна)
    frags.append(rect(70, 360, 700, 120, fill="#f7f7f8", stroke=MUTED, sw=1.2, ))
    frags.append(text(120, 386, "ЗАГАЛЬНЕ", size=15, bold=True, color=MUTED, anchor="start"))
    frags.append(chip(300, 430, "Білінг · лічба", "#f0f0f2"))
    frags.append(chip(520, 430, "Ідентичність", "#f0f0f2"))
    # маркер перекладача на межі із ядром
    b, bw, bh = textbox(640, 430, "ACL", size=12, fill="#fff8e1", stroke=POS, sw=1.6, min_w=56)
    frags.append(b)
    frags.append(text(800, 420, "беремо готове,", size=13, color=INK, anchor="start"))
    frags.append(text(800, 440, "за перекладачем", size=13, color=INK, anchor="start"))

    render(os.path.join(IMG, "boundary-thickness.svg"), W, H, *frags,
           title="Товщина стіни — за сортом піддомену")


def fig_seam_test():
    """Де стіна доречна (три сигнали збіглись), а де ні (крізь інваріант)."""
    W, H = 960, 500
    frags = [line(480, 60, 480, 470, color=MUTED, sw=1, dash="5,6")]

    # ── ЛІВОРУЧ: стіна тут — так ──
    frags.append(text(240, 84, "Стіна ТУТ — так", size=16, bold=True, color=FIELD))
    checks = [
        "слово роздвоюється у значенні",
        "різні годинники зміни",
        "різна потреба в узгодженні",
    ]
    cy = 130
    for c in checks:
        frags.append(plus(120, cy))
        frags.append(text(146, cy + 5, c, size=13, anchor="start"))
        cy += 44
    # дві межі з чистою стіною між ними
    b, _, _ = textbox(175, 350, "Керування", size=13, fill="#eafaf0", stroke=FIELD, sw=2)
    frags.append(b)
    b, _, _ = textbox(345, 350, "Білінг", size=13, fill="#fdecea", stroke=POS, sw=2)
    frags.append(b)
    frags.append(line(260, 316, 260, 384, color=FIELD, sw=4))
    frags.append(text(240, 428, "стіна між різними світами", size=12, color=MUTED))

    # ── ПРАВОРУЧ: стіна тут — ні ──
    frags.append(text(720, 84, "Стіна ТУТ — ні", size=16, bold=True, color=POS))
    frags.append(minus(600, 140))
    frags.append(text(626, 145, "крізь один інваріант", size=13, anchor="start"))
    # агрегат «замок», розрізаний стіною
    frags.append(rect(590, 220, 260, 150, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(720, 246, "агрегат «замок»", size=13, bold=True))
    b, _, _ = textbox(655, 300, "власник", size=12, fill=BG, stroke=MUTED, sw=1.2)
    frags.append(b)
    b, _, _ = textbox(785, 300, "стан", size=12, fill=BG, stroke=MUTED, sw=1.2)
    frags.append(b)
    # червона стіна крізь агрегат
    frags.append(line(720, 214, 720, 376, color=POS, sw=4, dash="7,5"))
    frags.append(text(720, 400, "«замок не буває нічий» — рветься", size=12, color=POS))
    frags.append(text(720, 420, "через стіну одну транзакцію не провести", size=12, color=MUTED))

    render(os.path.join(IMG, "seam-test.svg"), W, H, *frags,
           title="Тест шва: між агрегатами — можна, крізь агрегат — ні")


def fig_guarded_graph():
    """Стіна billing→control, яку тримає CI; contracts — легальні двері."""
    W, H = 1020, 600
    frags = []

    ctrl, cw, ch = textbox(240, 150, "control · ЯДРО\nбагата Device, інваріанти",
                           size=13, fill="#f4fbf6", stroke=FIELD, sw=4, min_w=210)
    bill, bw, bh = textbox(520, 150, "billing · загальне\nлічба за планом",
                           size=13, fill="#fdecea", stroke=POS, sw=2, min_w=180)
    tele, tw, th = textbox(840, 150, "telemetry\nчасові ряди",
                           size=13, fill="#eef2fb", stroke=NEG, sw=2, min_w=150)
    con, conw, conh = textbox(520, 400, "contracts — двері\nопубліковані події / DTO",
                              size=13, fill="#f7f7f8", stroke=MUTED, sw=2, min_w=320)

    # зелені дозволені ребра до спільного листа contracts
    frags.append(arrow(240, 150 + ch / 2, 470, 400 - conh / 2, color=FIELD, sw=2))
    frags.append(arrow(520, 150 + bh / 2, 520, 400 - conh / 2, color=FIELD, sw=2))
    frags.append(arrow(840, 150 + th / 2, 590, 400 - conh / 2, color=FIELD, sw=2))
    frags.append(text(610, 292, "дозволено", size=12, color=FIELD))

    # заборонене червоне ребро billing → control (у проміжку між боксами)
    cx_r = 240 + cw / 2
    bx_l = 520 - bw / 2
    ymid = 150
    frags.append(line(bx_l - 4, ymid, cx_r + 4, ymid, color=POS, sw=3, dash="7,5"))
    mx = (bx_l + cx_r) / 2
    frags.append(line(mx - 9, ymid - 9, mx + 9, ymid + 9, color=POS, sw=3))
    frags.append(line(mx + 9, ymid - 9, mx - 9, ymid + 9, color=POS, sw=3))
    frags.append(text(mx, 98, "заборонено: ADR-014", size=13, color=POS, bold=True))
    frags.append(text(mx, 118, "billing → control", size=11, color=MUTED))

    gate, gw, gh = textbox(520, 520,
                           "CI-сторож ловить червоне ребро → білд червоний\n"
                           "lint-imports · depcruise · ArchUnit",
                           size=13, fill="#fff8e1", stroke=INK, sw=1.6, min_w=560)

    frags += [ctrl, bill, tele, con, gate]
    render(os.path.join(IMG, "guarded-graph.svg"), W, H, *frags,
           title="Стіну «billing → control» тримає збірка")


def fig_door_leak():
    """Пастка: contracts реекспортує Control.Device — модель тікає крізь двері."""
    W, H = 1000, 420
    frags = []

    bill, bw, bh = textbox(160, 150, "billing", size=14, fill="#fdecea",
                           stroke=POS, sw=2, min_w=140)

    # двері з червоним реекспортом усередині
    frags.append(rect(360, 108, 300, 96, fill="#fff8e1", stroke=MUTED, sw=2))
    frags.append(text(510, 138, "contracts — двері", size=14, color=INK, bold=True))
    frags.append(text(510, 167, "reexport Control.Device", size=13, color=POS))
    frags.append(text(510, 187, "(нутро тікає назовні)", size=11, color=MUTED))

    ctrl, cw, ch = textbox(850, 150, "control\nControl.Device", size=13,
                           fill="#f4fbf6", stroke=FIELD, sw=3, min_w=160)

    frags.append(arrow(160 + bw / 2, 150, 358, 150, color=FIELD, sw=2.4))
    frags.append(text((160 + bw / 2 + 358) / 2, 128, "дозволено", size=12, color=FIELD))
    frags.append(arrow(662, 150, 850 - cw / 2, 150, color=POS, sw=2.4))
    frags.append(text((662 + 850 - cw / 2) / 2, 128, "протягує нутро", size=12, color=POS))

    frags.append(bill)
    frags.append(ctrl)
    frags.append(text(500, 268,
                      "правило billing → control зелене — а модель вже в руках білінгу",
                      size=13, color=MUTED))
    fix, fw, fh = textbox(500, 335, "лік: стерегти й двері — правило «contracts не знає control»",
                          size=13, fill="#eafaf0", stroke=FIELD, sw=2, min_w=440)
    frags.append(fix)

    render(os.path.join(IMG, "door-leak.svg"), W, H, *frags,
           title="Двері, лишені без нагляду, зводять стіну нанівець")


if __name__ == "__main__":
    fig_word_fracture()
    fig_boundary_thickness()
    fig_seam_test()
    fig_guarded_graph()
    fig_door_leak()
    print("OK: word-fracture.svg, boundary-thickness.svg, seam-test.svg, "
          "guarded-graph.svg, door-leak.svg")
