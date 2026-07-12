# -*- coding: utf-8 -*-
"""Фігури для кроку «DH v0 → v1: перший рефакторинг межами»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f8ef"
RED_FILL = "#fdecea"


def box(cx, cy, lines, size=14, bold=False, fill=FILL, stroke=LINE, pad=10, min_w=0):
    frag, w, h = textbox(cx, cy, "\n".join(lines) if isinstance(lines, list) else lines,
                         size=size, bold=bold, fill=fill, stroke=stroke, pad=pad, min_w=min_w)
    return frag, w, h


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — v0 (зварений блок) → v1 (модулі з типізованими швами)
# ────────────────────────────────────────────────────────────────────────────
def fig_split():
    W, H = 1000, 420
    f = []

    # ── ліва панель: v0 — один зварений блок ──
    f.append(text(205, 104, "v0", size=16, bold=True))
    f.append(rect(60, 120, 290, 200, fill=FILL, stroke=LINE, sw=2))
    f.append(mtext(205, 208, ["read → decide → act",
                              "поріг 20.0 — усередині",
                              "діалект давача — усередині"], size=12, color=INK))
    f.append(text(205, 344, "жодного шва всередині", size=11, color=MUTED))

    # ── стрілка переходу (у чистому проміжку між панелями) ──
    f.append(text(383, 206, "рефакторинг", size=9, color=MUTED))
    f.append(arrow(352, 220, 410, 220, color=INK, sw=2.2))

    # ── права панель: v1 — чотири шматки + збірка ──
    f.append(text(690, 66, "v1", size=16, bold=True))

    cfg, cw, ch = box(690, 110, ["Config", "поріг 20.0"], size=14)
    drv, dw, dh = box(470, 250, ["Драйвер", "давача"], size=14)
    dec, ew, eh = box(690, 250, ["decide()", "чиста"], size=14, fill="#eef4ff")
    htr, hw, hh = box(905, 250, ["Розетка", "(драйвер)"], size=14)

    # дашкова рамка збірки (композиційний корінь) навколо ряду
    f.append(rect(415, 214, 550, 82, fill="none", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(690, 314, "збірка (run) диригує шматки", size=12, color=MUTED))

    # стрілки-шви
    f.append(arrow(690, 110 + ch / 2, 690, 250 - eh / 2 - 2, color=INK, sw=1.8))  # config → decide
    f.append(arrow(470 + dw / 2, 250, 690 - ew / 2 - 2, 250, color=INK, sw=1.8))   # driver → decide
    f.append(arrow(690 + ew / 2, 250, 905 - hw / 2 - 2, 250, color=INK, sw=1.8))   # decide → heater
    f.append(text(578, 238, "Reading °C", size=12, color=FIELD, bold=True))
    f.append(text(797, 238, "Command", size=12, color=NEG, bold=True))

    f += [cfg, drv, dec, htr]
    render(os.path.join(IMG, "v0-to-v1.svg"), W, H, *f,
           title="Той самий дім: v0 — усе в одному тілі, v1 — модулі з названими швами")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — контракт шва: діалект давача вмирає на краю
# ────────────────────────────────────────────────────────────────────────────
def fig_seam():
    W, H = 940, 360
    f = []

    f.append(text(44, 124, "v1", size=14, bold=True, color=FIELD))
    f.append(text(44, 300, "v0", size=14, bold=True, color=POS))

    dev, vw, vh = box(130, 120, ["давач віддає", "20125 (мілі-°C)"], size=13)
    drv, dw, dh = box(360, 120, ["драйвер:", "÷1000 на краю"], size=13)
    dec, ew, eh = box(730, 120, ["decide()", "бачить лише °C"], size=13, fill="#eef4ff")

    # шов
    f.append(line(520, 58, 520, 192, color=MUTED, sw=2.5, dash="6 5"))
    f.append(text(520, 48, "шов", size=12, bold=True, color=MUTED))

    # стрілки верхнього (v1) шляху
    f.append(text(249, 108, "діалект", size=11, color=MUTED))
    f.append(arrow(130 + vw / 2, 120, 360 - dw / 2 - 2, 120, color=INK, sw=1.8))
    f.append(arrow(360 + dw / 2, 120, 730 - ew / 2 - 2, 120, color=INK, sw=1.8))
    f.append(text(600, 106, "Reading(20.1 °C, ok)", size=12, color=FIELD, bold=True))
    f.append(text(470, 214, "переклад стається ТУТ — далі йде лише °C", size=12, color=INK))

    f += [dev, drv, dec]

    # нижній контраст (v0)
    f.append(fitbox(70, 262, 800, 52,
                    "v0: сирі 20125 течуть просто в  t < 20.0  →  завжди хибно, грілка мовчить",
                    size=13, fill=RED_FILL, stroke=POS))

    render(os.path.join(IMG, "seam-contract.svg"), W, H, *f,
           title="Контракт шва: де вмирає діалект давача")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — локальність зміни: правка лишається у своєму модулі
# ────────────────────────────────────────────────────────────────────────────
def fig_containment():
    W, H = 880, 392
    f = []

    cols = ["Config", "Давач", "decide()", "Розетка", "Збірка"]
    rows = ["Нічний поріг", "Другий давач", "Сповіщати", "Інший вендор"]
    touch = {
        0: {0},        # нічний поріг → Config
        1: {4},        # другий давач → Збірка
        2: {2, 4},     # сповіщати → decide() + Збірка
        3: {1},        # інший вендор → Давач
    }

    x0, y0 = 168, 92          # верх-ліво сітки даних
    cw, rh = 138, 54
    lab_cx = 84               # центр колонки підписів рядків

    # заголовки колонок
    for j, c in enumerate(cols):
        f.append(text(x0 + j * cw + cw / 2, 80, c, size=12, bold=True))

    # рядки + клітини
    for i, r in enumerate(rows):
        cy = y0 + i * rh + rh / 2
        f.append(text(lab_cx, cy + 4, r, size=12, bold=True))
        for j in range(len(cols)):
            cx = x0 + j * cw
            on = j in touch[i]
            f.append(rect(cx + 3, y0 + i * rh + 3, cw - 6, rh - 6,
                          fill=GREEN_FILL if on else BG,
                          stroke=FIELD if on else "#d0d5db", sw=2 if on else 1))
            if on:
                f.append(text(cx + cw / 2, cy + 7, "✓", size=20, bold=True, color=FIELD))

    gb = y0 + len(rows) * rh          # низ сітки

    # легенда
    f.append(rect(168, gb + 16, 22, 16, fill=GREEN_FILL, stroke=FIELD, sw=2))
    f.append(text(200, gb + 29, "правка тут — і не далі свого модуля", size=12, anchor="start"))
    f.append(text(x0, gb + 58,
                  "у v0 ті самі чотири вимоги фарбували майже всю сітку — тут кожна замкнена в одній клітині",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "change-containment.svg"), W, H, *f,
           title="Локальність зміни у v1: правка впирається в стіну свого модуля")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — мокове коло: дім живе в пам'яті, збій вкидається на шві давача
# ────────────────────────────────────────────────────────────────────────────
def fig_mockloop():
    W, H = 1060, 430
    f = []
    cy = 180

    b1, w1, h1 = box(150, cy, ["MockRoom", "спільне повітря", "temp · heating"], size=13)
    b2, w2, h2 = box(430, cy, ["MockThermometer", "÷1000 на краю"], size=13)
    b3, w3, h3 = box(690, cy, ["decide()", "чиста"], size=13, fill="#eef4ff")
    b4, w4, h4 = box(920, cy, ["MockPlug", "ідемпотентна"], size=13)

    # горизонтальні шви (стрілки на центральній лінії ряду)
    f.append(arrow(150 + w1 / 2, cy, 430 - w2 / 2 - 2, cy, color=INK, sw=1.8))
    f.append(arrow(430 + w2 / 2, cy, 690 - w3 / 2 - 2, cy, color=INK, sw=1.8))
    f.append(arrow(690 + w3 / 2, cy, 920 - w4 / 2 - 2, cy, color=INK, sw=1.8))

    # підписи над стрілками — у проміжках, поза рамками
    f.append(text((150 + w1 / 2 + 430 - w2 / 2) / 2, cy - 12, "temp", size=11, color=MUTED))
    f.append(text(600, cy - 12, "Reading °C", size=12, color=FIELD, bold=True))
    f.append(text((690 + w3 / 2 + 920 - w4 / 2) / 2, cy - 12, "Command", size=12, color=NEG, bold=True))

    # тап збою на шві Reading — окремий x від підпису «Reading °C»
    ftap, fw, fh = box(505, 92, ["вкинути ok=false", "(таймаут / CRC=NO)"], size=11,
                       fill=RED_FILL, stroke=POS)
    f.append(ftap)
    f.append(arrow(505, 92 + fh / 2, 505, cy - 4, color=POS, sw=1.8))

    # зворотний шов: heating замикає коло через спільне повітря
    yb = 352
    f.append(line(920, cy + h4 / 2, 920, yb, color=INK, sw=1.8))
    f.append(line(920, yb, 150, yb, color=INK, sw=1.8))
    f.append(arrow(150, yb, 150, cy + h1 / 2 + 2, color=INK, sw=1.8))
    f.append(text(535, yb + 24, "heating — розетка пише у спільне повітря, і коло замикається",
                  size=12, color=MUTED))

    f += [b1, b2, b3, b4]
    render(os.path.join(IMG, "mock-loop.svg"), W, H, *f,
           title="Мокове коло: дім живе в пам'яті, а збій вкидається на шві давача")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 5 — збій крізь шар: залізна поломка → доменне «не вірю» → безпечний спокій
# ────────────────────────────────────────────────────────────────────────────
def fig_faultpath():
    W, H = 1020, 340
    f = []
    cy = 120

    a1, aw1, ah1 = box(140, cy, ["залізо: таймаут", "або CRC=NO"], size=13,
                       fill=RED_FILL, stroke=POS)
    a2, aw2, ah2 = box(400, cy, ["драйвер давача:", "перекладає збій"], size=13)
    a3, aw3, ah3 = box(660, cy, ["Reading(ok=false)", "«числу не вірю»"], size=13,
                       fill="#eef4ff", stroke=FIELD)
    a4, aw4, ah4 = box(890, cy, ["decide:", "not ok → IDLE"], size=13)

    f.append(arrow(140 + aw1 / 2, cy, 400 - aw2 / 2 - 2, cy, color=INK, sw=1.8))
    f.append(arrow(400 + aw2 / 2, cy, 660 - aw3 / 2 - 2, cy, color=INK, sw=1.8))
    f.append(arrow(660 + aw3 / 2, cy, 890 - aw4 / 2 - 2, cy, color=INK, sw=1.8))

    f.append(text((140 + aw1 / 2 + 400 - aw2 / 2) / 2, cy - 14, "переклад", size=11, color=MUTED))
    f.append(text((400 + aw2 / 2 + 660 - aw3 / 2) / 2, cy - 14, "доменне слово", size=11, color=MUTED))
    f.append(text((660 + aw3 / 2 + 890 - aw4 / 2) / 2, cy - 14, "рішення", size=11, color=MUTED))

    # результат — безпечний спокій
    res, rw, rh = box(890, 225, ["безпечний спокій", "грілка off"], size=13,
                      fill=GREEN_FILL, stroke=FIELD)
    f.append(arrow(890, cy + ah4 / 2, 890, 225 - rh / 2 - 2, color=FIELD, sw=1.8))
    f.append(res)

    # контраст v0
    f.append(fitbox(80, 285, 860, 42,
                    "v0: доменного «не вірю» не було — сліпа довіра, і мертвий давач тихо ламав рішення (R2)",
                    size=13, fill=RED_FILL, stroke=POS))

    f += [a1, a2, a3, a4]
    render(os.path.join(IMG, "fault-path.svg"), W, H, *f,
           title="Збій крізь шар: залізна поломка стає доменним «не вірю», а рішення — спокоєм")


if __name__ == "__main__":
    fig_split()
    fig_seam()
    fig_containment()
    fig_mockloop()
    fig_faultpath()
    print("OK: figures written to", IMG)
