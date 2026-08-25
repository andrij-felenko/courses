# -*- coding: utf-8 -*-
"""Фігури до статті «Чотирипровідне (Кельвінове) підключення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def _wire(f, x1, y1, x2, y2, col=INK, sw=2.4):
    f.append(line(x1, y1, x2, y2, color=col, sw=sw))


def _res(f, x, y, w=54, h=20, label=None, col=INK, lblcol=None):
    """Прямокутний резистор по горизонталі, центр (x,y)."""
    f.append(rect(x - w / 2, y - h / 2, w, h, fill="#fafafa", stroke=col, sw=2, rx=3))
    if label:
        f.append(text(x, y - h / 2 - 8, label, size=11, color=lblcol or col, bold=True))


def _meter(f, x, y, r, sym, col=INK):
    f.append(circle(x, y, r, fill="#ffffff", stroke=col, sw=2.2))
    f.append(text(x, y + r * 0.34, sym, size=int(r * 1.0), color=col, bold=True))


# ── 1. Двопровідна біда: опір дротів додається до вимірюваного ───────────────
def fig_two_wire():
    W, H = 880, 430
    f = [text(W / 2, 30, "Двопровідний вимір: опір дротів зливається з вимірюваним",
              size=17, bold=True),
         text(W / 2, 52, "ті самі дроти несуть струм І ВИМІРЮЮТЬ напругу — омметр бачить R_дрт + R_x + R_дрт",
              size=11, color=MUTED, italic=True)]

    # омметр зліва
    mx, my, mr = 120, 215, 46
    _meter(f, mx, my, mr, "Ω", col=FIELD)
    f.append(text(mx, my + mr + 18, "омметр (2 клеми)", size=10, color=FIELD, bold=True))

    # дві клеми омметра
    tA_x, tA_y = mx + mr, my - 26
    tB_x, tB_y = mx + mr, my + 26

    # верхній провід до Rx
    rx_x = 640
    _wire(f, tA_x, tA_y, 300, tA_y)                  # горизонталь
    _res(f, 360, tA_y, w=70, label="R_дрт", col=POS, lblcol=POS)  # опір дроту
    _wire(f, 395, tA_y, rx_x - 26, tA_y)
    _wire(f, rx_x - 26, tA_y, rx_x - 26, my - 40)    # вниз до Rx
    # нижній провід
    _wire(f, tB_x, tB_y, 300, tB_y)
    _res(f, 360, tB_y, w=70, label="R_дрт", col=POS, lblcol=POS)
    _wire(f, 395, tB_y, rx_x - 26, tB_y)
    _wire(f, rx_x - 26, tB_y, rx_x - 26, my + 40)

    # вимірюваний опір Rx (вертикальний)
    f.append(rect(rx_x - 26 - 22, my - 40, 44, 80, fill="#eef7f0", stroke=INK, sw=2.4, rx=4))
    f.append(text(rx_x - 26, my, "R_x", size=15, color=INK, bold=True))
    f.append(mtext(rx_x + 34, my - 6, ["вимірюваний", "(малий!)"], size=10, color=MUTED, anchor="start"))

    # стрілка струму вздовж петлі
    f.append(text(360, tA_y + 30, "→ І тече тут →", size=10, color=POS, bold=True))
    f.append(text(360, tB_y - 14, "← І тече тут ←", size=10, color=POS, bold=True))

    # рамка-висновок
    f.append(fitbox(150, 330, 580, 64,
                    "Струм тече ЧЕРЕЗ дроти, тож на кожному падає І·R_дрт. Той самий дріт міряє напругу —\n"
                    "тому омметр зчитує R_дрт + R_x + R_дрт. Коли R_x — міліоми, а дроти — десяті ома,\n"
                    "уся «вимірювана» величина — це майже самі дроти. Вимір зіпсовано.",
                    size=11, fill="#fdecea", stroke=POS))
    render(os.path.join(IMG, "two-wire.svg"), W, H, *f)


# ── 2. Чотирипровідний лад: розвели струм і вимір ────────────────────────────
def fig_four_wire():
    W, H = 900, 470
    f = [text(W / 2, 30, "Чотири проводи: окремо «силові», окремо «чутливі»",
              size=17, bold=True),
         text(W / 2, 52, "струм женемо однією парою (Force), напругу знімаємо іншою (Sense) — прямо на тілі R_x",
              size=11, color=MUTED, italic=True)]

    # джерело струму зліва зверху
    sx, sy, sr = 110, 150, 34
    _meter(f, sx, sy, sr, "I", col=POS)
    f.append(text(sx, sy - sr - 10, "джерело струму", size=10, color=POS, bold=True))

    # вольтметр зліва знизу
    vx, vy, vr = 110, 330, 34
    _meter(f, vx, vy, vr, "V", col=NEG)
    f.append(text(vx, vy + vr + 16, "вольтметр (R_вх велике)", size=10, color=NEG, bold=True))

    # вимірюваний опір праворуч
    rxc_x, rx_top, rx_bot = 720, 175, 305
    f.append(rect(rxc_x - 24, rx_top, 48, rx_bot - rx_top, fill="#eef7f0", stroke=INK, sw=2.6, rx=4))
    f.append(text(rxc_x, (rx_top + rx_bot) / 2, "R_x", size=16, color=INK, bold=True))

    # точки дотику на краях Rx: силова — зовні (далі), чутлива — всередині (ближче до тіла)
    fp_y, sp_y = rx_top, rx_top + 26          # верхній край
    sn_y, fn_y = rx_bot - 26, rx_bot          # нижній край

    # СИЛОВІ проводи (Force) — товсті червоні: джерело I → F+ ... F− → назад до джерела
    _wire(f, sx + sr, sy, 320, sy, col=POS, sw=3.2)
    _res(f, 400, sy, w=64, label="R_дрт", col=POS, lblcol=POS)
    _wire(f, 432, sy, rxc_x - 24, sy, col=POS, sw=3.2)
    f.append(line(rxc_x - 24, sy, rxc_x - 24, fp_y, color=POS, sw=3.2))     # до F+
    # нижня силова гілка: від джерела I донизу й праворуч до F−
    f.append(line(sx, sy + sr, sx, 415, color=POS, sw=3.2))
    _wire(f, sx, 415, 368, 415, col=POS, sw=3.2)
    _res(f, 400, 415, w=64, label="R_дрт", col=POS, lblcol=POS)
    _wire(f, 432, 415, rxc_x - 24, 415, col=POS, sw=3.2)
    f.append(line(rxc_x - 24, 415, rxc_x - 24, fn_y, color=POS, sw=3.2))    # до F−

    # ЧУТЛИВІ проводи (Sense) — тонкі сині, окремі точки дотику ближче до тіла R_x
    _wire(f, vx + vr, vy - 14, 250, vy - 14, col=NEG, sw=1.8)
    _wire(f, 250, vy - 14, 250, sp_y, col=NEG, sw=1.8)
    _wire(f, 250, sp_y, rxc_x + 24, sp_y, col=NEG, sw=1.8)
    f.append(circle(rxc_x + 24, sp_y, 4, fill=NEG, stroke=NEG, sw=1))       # S+
    _wire(f, vx + vr, vy + 14, 285, vy + 14, col=NEG, sw=1.8)
    _wire(f, 285, vy + 14, 285, sn_y, col=NEG, sw=1.8)
    _wire(f, 285, sn_y, rxc_x + 24, sn_y, col=NEG, sw=1.8)
    f.append(circle(rxc_x + 24, sn_y, 4, fill=NEG, stroke=NEG, sw=1))       # S−

    # підписи клем
    f.append(text(rxc_x - 36, fp_y - 4, "F+", size=10, color=POS, anchor="end", bold=True))
    f.append(text(rxc_x - 36, fn_y + 14, "F−", size=10, color=POS, anchor="end", bold=True))
    f.append(text(rxc_x + 36, sp_y - 4, "S+", size=10, color=NEG, anchor="start", bold=True))
    f.append(text(rxc_x + 36, sn_y + 14, "S−", size=10, color=NEG, anchor="start", bold=True))

    # ключові підказки
    f.append(text(180, sy - 14, "І тече товстими дротами", size=10, color=POS, bold=True, anchor="start"))
    f.append(mtext(265, 235, ["≈0 струму", "у Sense →", "падіння І·R_дрт", "тут зникає"],
                   size=9, color=NEG, anchor="middle"))
    render(os.path.join(IMG, "four-wire.svg"), W, H, *f)


# ── 3. Числа: 2 дроти проти 4 на малому опорі ───────────────────────────────
def fig_numbers():
    W, H = 860, 360
    f = [text(W / 2, 30, "Ті самі дроти, той самий R_x — різниця в десятки відсотків",
              size=17, bold=True),
         text(W / 2, 52, "R_x = 0.10 Ω, кожен дріт 0.20 Ω, струм 1 А; що бачить кожен метод",
              size=11, color=MUTED, italic=True)]

    cols = [(90, "метод", "start"), (340, "що міряє", "middle"),
            (540, "показ", "middle"), (720, "похибка", "middle")]
    for x, lbl, anc in cols:
        f.append(text(x, 100, lbl, size=11, color=MUTED, anchor=anc, bold=True))

    rows = [
        ("2 проводи", "R_дрт + R_x + R_дрт", "0.50 Ω", "+400 %", POS),
        ("4 проводи", "лише R_x", "0.10 Ω", "≈ 0 %", FIELD),
    ]
    y = 120
    for name, what, shown, err, col in rows:
        f.append(rect(70, y, 740, 56, fill="#fafafa", stroke="#dddddd", sw=1.3))
        cy = y + 34
        f.append(text(90, cy, name, size=12, color=col, anchor="start", bold=True))
        f.append(text(340, cy, what, size=12))
        f.append(text(540, cy, shown, size=13, color=col, bold=True))
        f.append(text(720, cy, err, size=13, color=col, bold=True))
        y += 66

    f.append(fitbox(120, 268, 620, 66,
                    "Двопровідний показ 0.50 Ω — це на 80 % дроти, лише на 20 % сам R_x: вимір неприданий.\n"
                    "Чотирипровідний бачить рівно 0.10 Ω, бо струм у чутливих проводах майже нульовий,\n"
                    "тож їхній І·R_дрт зникає. Що менший R_x, то більший виграш.",
                    size=11, fill="#eef7f0", stroke=FIELD))
    render(os.path.join(IMG, "numbers.svg"), W, H, *f)


# ── 4. Кельвінів подвійний міст (узагальнено) ────────────────────────────────
def fig_kelvin_bridge():
    W, H = 860, 420
    f = [text(W / 2, 30, "Кельвінів подвійний міст: міст Вітстона для дрібних опорів",
              size=17, bold=True),
         text(W / 2, 52, "друга пара плечей (a, b) відводить струм від чутливих з'єднань, і опір перемичок скорочується",
              size=11, color=MUTED, italic=True)]

    # нижня товста гілка: джерело I → Rx → Rs (зразковий) → назад
    yI = 320
    f.append(text(120, yI + 26, "сильний струм І", size=10, color=POS, bold=True, anchor="start"))
    _wire(f, 110, yI, 250, yI, col=POS, sw=3.2)
    _res(f, 320, yI, w=90, h=24, label="R_x (невідомий)", col=INK)
    _wire(f, 365, yI, 470, yI, col=POS, sw=3.2)       # «перемичка» між Rx і Rs
    f.append(text(417, yI + 22, "перемичка r", size=9, color=MUTED))
    _res(f, 560, yI, w=90, h=24, label="R_s (зразковий)", col=INK)
    _wire(f, 605, yI, 760, yI, col=POS, sw=3.2)
    f.append(circle(110, yI, 5, fill=POS, stroke=POS, sw=1))
    f.append(circle(760, yI, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(110, yI - 14, "I+", size=10, color=POS, bold=True))
    f.append(text(760, yI - 14, "I−", size=10, color=POS, bold=True))

    # верхні плечі відношення P, Q (звичайний міст)
    yT = 150
    nodeP_x, nodeQ_x = 275, 605          # точки знімання напруги з Rx та Rs
    galv_x = 440
    _res(f, 360, yT, w=70, h=20, label="P", col=NEG, lblcol=NEG)
    _res(f, 520, yT, w=70, h=20, label="Q", col=NEG, lblcol=NEG)
    _wire(f, nodeP_x, yI - 12, nodeP_x, yT, col=NEG, sw=1.8)   # знімаємо з краю Rx
    _wire(f, nodeP_x, yT, 325, yT, col=NEG, sw=1.8)
    _wire(f, 395, yT, galv_x, yT, col=NEG, sw=1.8)
    _wire(f, galv_x, yT, 485, yT, col=NEG, sw=1.8)
    _wire(f, 555, yT, nodeQ_x, yT, col=NEG, sw=1.8)
    _wire(f, nodeQ_x, yT, nodeQ_x, yI - 12, col=NEG, sw=1.8)   # до краю Rs

    # гальванометр посередині
    _meter(f, galv_x, yT, 20, "G", col=FIELD)
    f.append(text(galv_x, yT - 30, "детектор нуля", size=10, color=FIELD, bold=True))

    # друга пара плечей a, b — навколо перемички
    _res(f, 417, 235, w=44, h=16, label=None, col="#e08030")
    f.append(text(396, 232, "a", size=10, color="#e08030", bold=True))
    f.append(text(446, 232, "b", size=10, color="#e08030", bold=True))
    _wire(f, 380, yI - 12, 380, 235, col="#e08030", sw=1.6)
    _wire(f, 395, 235, 417 - 22, 235, col="#e08030", sw=1.6)
    _wire(f, 417 + 22, 235, 470, 235, col="#e08030", sw=1.6)
    _wire(f, 470, 235, 470, yI - 12, col="#e08030", sw=1.6)
    _wire(f, galv_x, yT + 20, galv_x, 235, col="#e08030", sw=1.6)
    _wire(f, galv_x, 235, 439, 235, col="#e08030", sw=1.6)

    f.append(fitbox(140, 350, 580, 56,
                    "Звичайний міст на дрібному R_x зіпсувала б перемичка r між зразком і невідомим.\n"
                    "Друга пара a, b бере на себе якраз стільки, щоб дія r у балансі зникла:\n"
                    "лишається чисте R_x = R_s · (P/Q), як у простому мості — але для міліомів.",
                    size=11, fill="#fff7ee", stroke="#e08030"))
    render(os.path.join(IMG, "kelvin-bridge.svg"), W, H, *f)


# ── 5. Історія: ідея → реалізація → назва (для вставки hist-) ─────────────────
def fig_kelvin_history():
    W, H = 900, 470
    f = [text(W / 2, 30, "Кельвінове ім'я: ідея, реалізація, назва — три різні речі",
              size=17, bold=True),
         text(W / 2, 52, "ім'я вшановує не першість в ідеї, а прилад, що зробив ідею практичною",
              size=11, color=MUTED, italic=True)]

    # три колонки-картки
    cards = [
        (155, "ІДЕЯ", "#777777", "#f4f4f4",
         ["Розвести струм", "і вимір по різних", "проводах.", "", "Випливає з закону",
          "Ома — НІЧИЯ,", "до неї міг дійти", "будь-хто."]),
        (450, "РЕАЛІЗАЦІЯ", FIELD, "#eef7f0",
         ["Подвійний міст", "(~1861), праця", "1862 р.", "", "Робочий прилад для",
          "опорів від мкОм", "до десятків ом.", "СПРАВЖНЯ заслуга."]),
        (745, "НАЗВА", NEG, "#eaf0fd",
         ["«Кельвінове»", "під'єднання,", "контакт, кліпс.", "", "Ім'я мосту",
          "розповзлося на", "ВЕСЬ чотирививідний", "спосіб."]),
    ]
    cw, cy0, ch = 250, 90, 230
    cxs = []
    for cx, head, col, fill, body in cards:
        cxs.append(cx)
        f.append(rect(cx - cw / 2, cy0, cw, ch, fill=fill, stroke=col, sw=2, rx=8))
        f.append(text(cx, cy0 + 26, head, size=14, color=col, bold=True))
        f.append(line(cx - cw / 2 + 14, cy0 + 36, cx + cw / 2 - 14, cy0 + 36, color=col, sw=1.4))
        f.append(mtext(cx, cy0 + 58, body, size=11, color=INK, lh=1.28))

    # стрілки між картками
    f.append(arrow(cxs[0] + cw / 2 + 4, cy0 + ch / 2, cxs[1] - cw / 2 - 4, cy0 + ch / 2,
                   color=MUTED, sw=2.2))
    f.append(arrow(cxs[1] + cw / 2 + 4, cy0 + ch / 2, cxs[2] - cw / 2 - 4, cy0 + ch / 2,
                   color=MUTED, sw=2.2))
    f.append(text((cxs[0] + cxs[1]) / 2, cy0 + ch / 2 - 10, "втілив у", size=9,
                  color=MUTED, italic=True))
    f.append(text((cxs[1] + cxs[2]) / 2, cy0 + ch / 2 - 10, "дала ім'я", size=9,
                  color=MUTED, italic=True))

    # стрічка-таймлайн знизу
    ty = 372
    f.append(line(120, ty, 780, ty, color=INK, sw=2))
    marks = [(120, "1824", "народився", "у Белфасті"),
             (300, "1846", "професор", "у Глазго (22 р.)"),
             (470, "1858", "дзеркальний", "гальванометр"),
             (610, "~1861", "подвійний", "міст Кельвіна"),
             (780, "1866/92", "лицар, тоді", "барон Кельвін")]
    for x, yr, l1, l2 in marks:
        f.append(circle(x, ty, 4, fill=INK, stroke=INK, sw=1))
        f.append(text(x, ty - 12, yr, size=11, color=INK, bold=True))
        f.append(mtext(x, ty + 18, [l1, l2], size=9, color=MUTED, lh=1.2))
    render(os.path.join(IMG, "kelvin-history.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_wire()
    fig_four_wire()
    fig_numbers()
    fig_kelvin_bridge()
    fig_kelvin_history()
    print("OK: 5 фігур у", IMG)
