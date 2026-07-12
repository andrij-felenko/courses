# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER = "#e08a1e"


def fig_cycle():
    """Замкнуте коло залежностей, яке розриває характеризаційний тест."""
    W, H = 860, 520
    frags = []
    cx, bw = 330, 280

    frags.append(fitbox(cx - bw / 2, 70, bw, 60, "змінити успадкований код безпечно",
                        size=14, fill="#fbfcfd", stroke=INK, sw=2))
    frags.append(fitbox(cx - bw / 2, 225, bw, 60, "автоматичні тести як страхувальна сітка",
                        size=14, fill="#fbfcfd", stroke=INK, sw=2))
    frags.append(fitbox(cx - bw / 2, 380, bw, 60, "рефакторинг заради тестопридатності",
                        size=14, fill="#fbfcfd", stroke=INK, sw=2))

    frags.append(arrow(cx, 130, cx, 223))
    frags.append(text(cx + 18, 182, "потребує", size=12.5, color=MUTED, anchor="start"))
    frags.append(arrow(cx, 285, cx, 378))
    frags.append(text(cx + 18, 337, "потребує", size=12.5, color=MUTED, anchor="start"))

    # зворотний лікоть — коло замикається
    lx = 90
    frags.append(line(cx - bw / 2, 410, lx, 410, color=LINE, sw=1.6))
    frags.append(line(lx, 410, lx, 100, color=LINE, sw=1.6))
    frags.append(arrow(lx, 100, cx - bw / 2, 100))

    # зелений клин — вхід у вузол «тести», в обхід рефакторингу
    gx = 650
    frags.append(fitbox(gx - 150, 213, 300, 84,
                        "характеризаційний тест входить сюди —\nфіксує поведінку ЯК Є,\nбез рефакторингу",
                        size=12.5, fill="#eafaf1", stroke=FIELD, sw=2.2))
    frags.append(arrow(gx - 150, 255, cx + bw / 2, 255, color=FIELD, sw=2.4))
    frags.append(text(gx, 322, "розриває коло", size=12.5, color=FIELD, italic=True))

    frags.append(text(430, 488,
                      "стрілки «потребує» замкнулись у коло — почати нема звідки",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'cycle.svg'), W, H, *frags,
           title="Коло, яке розриває характеризаційний тест")


def fig_mechanism():
    """Механізм навпаки: код сам диктує, що має бути в assert."""
    W, H = 1000, 430
    frags = []
    y0, bh = 92, 84
    steps = [
        (40, 210, "1. пиши assert,\nсвідомо ХИБНИЙ", POS),
        (280, 190, "2. прогони —\nтест ПАДАЄ", INK),
        (560, 200, "3. встав СПРАВЖНЄ\nзначення в assert", INK),
        (800, 170, "4. зелено —\nповедінку пришпилено", FIELD),
    ]
    for (x, w, txt, col) in steps:
        frags.append(fitbox(x, y0, w, bh, txt, size=13, stroke=col, sw=2,
                            fill="#fbfcfd", color=INK))

    frags.append(arrow(steps[0][0] + steps[0][1], y0 + bh / 2, steps[1][0], y0 + bh / 2))
    frags.append(arrow(steps[1][0] + steps[1][1], y0 + bh / 2, steps[2][0], y0 + bh / 2))
    frags.append(arrow(steps[2][0] + steps[2][1], y0 + bh / 2, steps[3][0], y0 + bh / 2))

    # виноска: повідомлення про падіння несе справжнє значення
    frags.append(fitbox(340, 250, 340, 96,
                        "повідомлення про падіння:\nexpected \"?\" — насправді «19.4»\n↑ ось справжня поведінка коду",
                        size=12.5, stroke=NEG, sw=1.8, fill="#eef2f6"))
    frags.append(arrow(steps[1][0] + steps[1][1] / 2, y0 + bh, 425, 248, color=NEG, sw=1.8))
    frags.append(arrow(645, 248, steps[2][0] + steps[2][1] / 2, y0 + bh, color=NEG, sw=1.8))

    frags.append(text(W / 2, 402,
                      "звичайний тест знає очікуване наперед; характеризаційний — питає його в самого коду",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'mechanism.svg'), W, H, *frags,
           title="Механізм навпаки: не ти кажеш коду очікуване — код каже тобі")


def fig_net():
    """Сітка ловить ЗМІНУ поведінки, але не її неправильність."""
    W, H = 940, 452
    frags = []
    frags.append(line(470, 66, 470, 408, color=LINE, sw=1.2, dash="4 5"))

    # ЛІВА панель: рефакторинг змінив поведінку → сітка червона
    frags.append(text(255, 88, "рефакторинг ЗМІНИВ поведінку", size=14, bold=True))
    frags.append(fitbox(115, 118, 280, 56, "код: інші кишки", size=13,
                        fill="#fbfcfd", stroke=INK, sw=1.8))
    frags.append(fitbox(115, 210, 280, 52, "вихід: було 42 → стало 37", size=13,
                        fill="#fdecea", stroke=POS, color=INK))
    frags.append(arrow(255, 262, 255, 298, color=MUTED, sw=1.5))
    frags.append(fitbox(115, 300, 280, 56, "золоте значення: 42", size=13,
                        fill="#eef2f6", stroke=NEG))
    frags.append(text(255, 392, "СІТКА ЧЕРВОНА — зміну спіймано",
                      size=13.5, bold=True, color=POS))

    # ПРАВА панель: поведінка від початку хибна → сітка зелена, баг пришпилено
    frags.append(text(685, 88, "поведінка від початку НЕПРАВИЛЬНА", size=14, bold=True))
    frags.append(fitbox(545, 118, 280, 56, "код: той самий баг", size=13,
                        fill="#fbfcfd", stroke=INK, sw=1.8))
    frags.append(fitbox(545, 210, 280, 52, "вихід: 42 = 42, хоч це БАГ", size=13,
                        fill="#fff6e6", stroke=AMBER, color=INK))
    frags.append(arrow(685, 262, 685, 298, color=MUTED, sw=1.5))
    frags.append(fitbox(545, 300, 280, 56, "золоте значення: 42", size=13,
                        fill="#eef2f6", stroke=NEG))
    frags.append(text(685, 392, "СІТКА ЗЕЛЕНА — баг пришпилено теж",
                      size=13.5, bold=True, color=FIELD))

    render(os.path.join(OUT, 'net.svg'), W, H, *frags,
           title="Сітка стереже СТАЛІСТЬ поведінки, а не її ПРАВИЛЬНІСТЬ")


def fig_lineage():
    """Родовід прийому: золотий еталон старший за термін; ідея/інструмент/популяризація — різні роки й люди."""
    W, H = 1090, 445
    frags = []

    base_y = 250
    frags.append(arrow(58, base_y, 1028, base_y, color=LINE, sw=2))

    bw, bh = 200, 82
    # (x, місце, заливка, обвід, рядки)
    nodes = [
        (150, "TOP", "#eef2f6", MUTED, "≈1988 · золотий еталон\nз фабрики платівок:\nмайстер, з якого тиснуть"),
        (360, "BOT", "#ffffff", INK,   "2004 · Майкл Фезерс\nтермін «characterization\ntest» + «код без тестів»"),
        (570, "TOP", "#eaf0fd", NEG,   "2007 · Llewellyn Falco\nApprovalTests + термін\n«approval testing»"),
        (780, "BOT", "#eafaf1", FIELD, "2011 · Gilded Rose\nTerry Hughes → мультимовна\nката Emily Bache"),
        (970, "TOP", "#fff6e6", AMBER, "2016 · Jest 14.0\ntoMatchSnapshot —\nзнімки для фронтенду"),
    ]
    for (x, place, fill, stroke, s) in nodes:
        frags.append(circle(x, base_y, 6, fill=INK, stroke=INK, sw=1))
        if place == "TOP":
            by = 122
            frags.append(line(x, base_y - 6, x, by + bh + 2, color=stroke, sw=1.6))
        else:
            by = 296
            frags.append(line(x, base_y + 6, x, by - 2, color=stroke, sw=1.6))
        frags.append(fitbox(x - bw / 2, by, bw, bh, s, size=12,
                            fill=fill, stroke=stroke, sw=2, color=INK))

    frags.append(text(W / 2, 418,
                      "золотий еталон старший за сам термін; ідея, інструмент і популяризація "
                      "прийшли різними роками й від різних людей",
                      size=12.5, color=MUTED, italic=True))

    render(os.path.join(OUT, 'lineage.svg'), W, H, *frags,
           title="Родовід характеризаційного тесту: слово, метафора, інструмент, знімок")


def fig_doubles():
    """Два дублери, що роблять сітку детермінованою: застиглий годинник і сталеве зерно."""
    W, H = 1040, 520
    frags = []

    frags.append(fitbox(40, 210, 180, 100, "plan(sensors, rules)\n(успадкований код)",
                        size=13, fill="#fbfcfd", stroke=INK, sw=2))

    # ── ряд «годинник» (центр y=150) ──
    frags.append(fitbox(250, 112, 175, 76, "годинник\ndatetime.now()", size=13,
                        fill=FILL, stroke=INK, sw=1.8))
    frags.append(fitbox(478, 112, 225, 76, "07:41 → 07:42 → …\n(щопрогону інше)", size=13,
                        fill="#fff6e6", stroke=AMBER, sw=2))
    frags.append(fitbox(800, 112, 210, 76, "FrozenClock → 07:00\n(застигле)", size=13,
                        fill="#eafaf1", stroke=FIELD, sw=2.2))
    frags.append(arrow(425, 150, 478, 150))
    frags.append(arrow(703, 150, 800, 150, color=FIELD, sw=2.2))
    frags.append(text(751, 138, "monkeypatch", size=11, color=MUTED))

    # ── ряд «генератор» (центр y=360) ──
    frags.append(fitbox(250, 322, 175, 76, "генератор\nrandom.random()", size=13,
                        fill=FILL, stroke=INK, sw=1.8))
    frags.append(fitbox(478, 322, 225, 76, "0.83? 0.19? …\n(від історії процесу)", size=13,
                        fill="#fff6e6", stroke=AMBER, sw=2))
    frags.append(fitbox(800, 322, 210, 76, "Random(0) → 0.844, …\n(відтворне)", size=13,
                        fill="#eafaf1", stroke=FIELD, sw=2.2))
    frags.append(arrow(425, 360, 478, 360))
    frags.append(arrow(703, 360, 800, 360, color=FIELD, sw=2.2))
    frags.append(text(751, 348, "monkeypatch", size=11, color=MUTED))

    frags.append(arrow(220, 235, 250, 152))
    frags.append(arrow(220, 285, 250, 358))

    frags.append(text(520, 470,
                      "детермінізм настає лише коли ОБИДВА диких входи підмінено дублером у шві",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'doubles.svg'), W, H, *frags,
           title="Годинник і генератор — два входи, які тест підмінює дублером")


def fig_bugfix():
    """Баг-затирання порога у відпустці й свідома правка, що фліпає золоте значення."""
    W, H = 1000, 600
    frags = []
    lx, rx = 245, 725                       # центри колонок
    bx_l, bx_r, bw = 70, 550, 350

    frags.append(text(lx, 66, "як воно є — баг пришпилено", size=14, bold=True, color=POS))
    frags.append(text(rx, 66, "після свідомої правки", size=14, bold=True, color=FIELD))

    tops = [92, 164, 236, 308, 380]
    left = [
        ("base = rules['threshold'] = 20.0", FILL, INK),
        ("ніч? не цей такт → лишається 20.0", FILL, LINE),
        ("vacation → thr = 12.0  (антизамерзання труб)", "#eaf0fd", NEG),
        ("6 ≤ 7 < 9 → thr = 21.0   ← ЗАТИРАЄ 12.0", "#fdecea", POS),
        ("рішення: 15.0 < 21.0  →  HEAT", "#fdecea", POS),
    ]
    right = [
        ("base = rules['threshold'] = 20.0", FILL, INK),
        ("ніч? не цей такт → лишається 20.0", FILL, LINE),
        ("vacation → thr = 12.0  (антизамерзання труб)", "#eaf0fd", NEG),
        ("6 ≤ 7 < 9 AND NOT vacation → пропущено", "#eafaf1", FIELD),
        ("рішення: 15.0 < 12.0? ні  →  IDLE", "#eafaf1", FIELD),
    ]
    for i, top in enumerate(tops):
        t, fill, st = left[i]
        frags.append(fitbox(bx_l, top, bw, 54, t, size=12.5, fill=fill, stroke=st, sw=2))
        t, fill, st = right[i]
        frags.append(fitbox(bx_r, top, bw, 54, t, size=12.5, fill=fill, stroke=st, sw=2))
        if i < len(tops) - 1:
            frags.append(arrow(lx, top + 56, lx, top + 70, color=MUTED, sw=1.4))
            frags.append(arrow(rx, top + 56, rx, top + 70, color=MUTED, sw=1.4))

    frags.append(arrow(lx, 436, lx, 454, color=MUTED, sw=1.4))
    frags.append(arrow(rx, 436, rx, 454, color=MUTED, sw=1.4))
    frags.append(fitbox(bx_l, 456, bw, 60, "золоте значення: hall:HEAT\n(порожній дім гріється у відпустці)",
                        size=12.5, fill="#fff6e6", stroke=AMBER, sw=2))
    frags.append(fitbox(bx_r, 456, bw, 60, "золоте значення: hall:IDLE\n(переприйнято з приміткою)",
                        size=12.5, fill="#eafaf1", stroke=FIELD, sw=2))

    frags.append(text(500, 560,
                      "єдина правка — `and not vacation`; еталон свідомо HEAT → IDLE, решта днів не зрушила",
                      size=13, color=MUTED, italic=True))

    render(os.path.join(OUT, 'bug-threshold.svg'), W, H, *frags,
           title="Пізніше правило затерло поріг відпустки — сітка тримала баг зеленим")


if __name__ == '__main__':
    fig_cycle()
    fig_mechanism()
    fig_net()
    fig_lineage()
    fig_doubles()
    fig_bugfix()
    print("figures written to", OUT)
