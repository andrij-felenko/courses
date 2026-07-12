# -*- coding: utf-8 -*-
"""Фігури для кроку «DH під тестом: збираємо тестованість, що її заклали шви»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_FILL = "#e8f8ef"
RED_FILL = "#fdecea"
BLUE_FILL = "#eef4ff"
AMBER_FILL = "#fff4e0"


def box(cx, cy, lines, size=14, bold=False, fill=FILL, stroke=LINE, pad=10, min_w=0):
    frag, w, h = textbox(cx, cy, "\n".join(lines) if isinstance(lines, list) else lines,
                         size=size, bold=bold, fill=fill, stroke=stroke, pad=pad, min_w=min_w)
    return frag, w, h


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 1 — шов як гніздо: одна проводка, два набори штепселів
# ────────────────────────────────────────────────────────────────────────────
def fig_double_at_seam():
    W, H = 1060, 500
    f = []
    cy = 250

    # центральний ряд: гніздо Sensor → tick → гніздо Heater
    ss, sw, sh = box(250, cy, ["гніздо", "порт Sensor"], size=13)
    tk, tw, th = box(540, cy, ["tick()", "read → decide → act", "політика — та сама"],
                     size=13, fill=BLUE_FILL, stroke=FIELD)
    hs, hw, hh = box(830, cy, ["гніздо", "порт Heater"], size=13)

    # горизонтальні шви
    f.append(arrow(250 + sw / 2, cy, 540 - tw / 2 - 2, cy, sw=1.8))
    f.append(arrow(540 + tw / 2, cy, 830 - hw / 2 - 2, cy, sw=1.8))
    f.append(text((250 + sw / 2 + 540 - tw / 2) / 2, cy - 13, "Reading °C", size=12, color=FIELD, bold=True))
    f.append(text((540 + tw / 2 + 830 - hw / 2) / 2, cy - 13, "Command", size=12, color=NEG, bold=True))

    # верх — прод-драйвери, що вставляються у гнізда
    yp = 96
    ps, pw, ph = box(250, yp, ["OneWireThermometer"], size=12)
    pl, plw, plh = box(830, yp, ["SmartPlug"], size=12)
    f.append(line(250, yp + ph / 2, 250, cy - sh / 2 - 8, color=MUTED, sw=1.6, dash="5 4"))
    f.append(arrow(250, cy - sh / 2 - 9, 250, cy - sh / 2 - 2, color=MUTED, sw=1.6))
    f.append(line(830, yp + plh / 2, 830, cy - hh / 2 - 8, color=MUTED, sw=1.6, dash="5 4"))
    f.append(arrow(830, cy - hh / 2 - 9, 830, cy - hh / 2 - 2, color=MUTED, sw=1.6))
    f.append(text(96, yp + 4, "у проді:", size=13, bold=True, color=INK))

    # низ — дублери на час тесту
    yt = 404
    ts, tsw, tsh = box(250, yt, ["FakeSensor"], size=12, fill=GREEN_FILL, stroke=FIELD)
    sp, spw, sph = box(830, yt, ["SpyHeater"], size=12, fill=GREEN_FILL, stroke=FIELD)
    f.append(line(250, yt - tsh / 2, 250, cy + sh / 2 + 8, color=MUTED, sw=1.6, dash="5 4"))
    f.append(arrow(250, cy + sh / 2 + 9, 250, cy + sh / 2 + 2, color=MUTED, sw=1.6))
    f.append(line(830, yt - sph / 2, 830, cy + hh / 2 + 8, color=MUTED, sw=1.6, dash="5 4"))
    f.append(arrow(830, cy + hh / 2 + 9, 830, cy + hh / 2 + 2, color=MUTED, sw=1.6))
    f.append(text(96, yt + 4, "у тесті:", size=13, bold=True, color=FIELD))

    # точка ввімкнення — під центром, у чистому проміжку
    f.append(text(540, 348, "точка ввімкнення ззовні обирає, який набір вставити в гнізда",
                  size=12, color=MUTED))

    f += [ss, tk, hs, ps, pl, ts, sp]
    render(os.path.join(IMG, "double-at-seam.svg"), W, H, *f,
           title="Шов — це гніздо: та сама проводка, підмінені лише кінці")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 2 — рефакторинг під характеризацією: чотири кадри
# ────────────────────────────────────────────────────────────────────────────
def fig_char_refactor():
    W, H = 1100, 300
    f = []
    cy = 118
    cxs = [155, 415, 675, 935]

    frames = [
        (["характеризація", "ЗЕЛЕНА"], GREEN_FILL, FIELD,
         ["фіксує ваду:", "застиглий гріє вічно"]),
        (["+ FreshnessGuard", "у збірці"], FILL, LINE,
         ["структуру змінено,", "decide не чіпали"]),
        (["та сама —", "ЧЕРВОНА"], RED_FILL, POS,
         ["зміна дотяглася", "саме до пришпиленого"]),
        (["пін оновлено", "+ регресія"], GREEN_FILL, FIELD,
         ["бажану поведінку", "закріплено"]),
    ]
    labels = ["додаємо вартового", "той самий тест", "оновлюємо пін"]

    boxes, widths = [], []
    for cx, (title, fill, stroke, _) in zip(cxs, frames):
        b, w, h = box(cx, cy, title, size=13, bold=True, fill=fill, stroke=stroke)
        boxes.append((b, w, h))
        widths.append(w)

    # стрілки-переходи + підписи в проміжках
    for i in range(3):
        x1 = cxs[i] + widths[i] / 2
        x2 = cxs[i + 1] - widths[i + 1] / 2
        f.append(arrow(x1 + 2, cy, x2 - 2, cy, sw=1.8))
        f.append(text((x1 + x2) / 2, cy - 12, labels[i], size=10, color=MUTED))

    f += [b for b, _, _ in boxes]

    # підписи під кадрами
    for cx, (_, _, _, cap) in zip(cxs, frames):
        f.append(mtext(cx, 188, cap, size=11, color=INK))

    render(os.path.join(IMG, "char-refactor.svg"), W, H, *f,
           title="Рефакторинг під характеризацією: пришпилити → змінити → упіймати червоне → закріпити")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 3 — рівні тестування на прикладі DH (пірамідою)
# ────────────────────────────────────────────────────────────────────────────
def fig_test_levels():
    W, H = 1000, 340
    f = []
    cx = 300

    top, tw, thh = box(cx, 84, ["справжнє залізо", "під навантаженням"], size=13,
                       fill=AMBER_FILL, stroke=POS, min_w=250)
    mid, mw, mhh = box(cx, 168, ["tick + фейк давача,", "шпигун розетки", "проводка в пам'яті"], size=13,
                       fill=BLUE_FILL, stroke=FIELD, min_w=400)
    bas, bw, bhh = box(cx, 258, ["чиста decide", "миттєві, без вводу-виводу", "їх — сотні"], size=13,
                       fill=GREEN_FILL, stroke=FIELD, min_w=540)

    f += [bas, mid, top]

    # бічна нотатка про вершину: офлайн недосяжне
    note, nw, nh = box(760, 84, ["офлайн не дістати →", "спостережність у проді", "+ рядок у реєстрі боргу"],
                       size=12, fill=FILL, stroke=MUTED)
    f.append(arrow(cx + tw / 2 + 2, 84, 760 - nw / 2 - 2, 84, color=MUTED, sw=1.6))
    f.append(note)

    # вісь «дешевше/дорожче» ліворуч
    f.append(text(70, 100, "дорожче,", size=11, color=MUTED))
    f.append(text(70, 116, "рідше", size=11, color=MUTED))
    f.append(text(70, 250, "дешевше,", size=11, color=MUTED))
    f.append(text(70, 266, "частіше", size=11, color=MUTED))

    render(os.path.join(IMG, "test-levels.svg"), W, H, *f,
           title="Рівні тестування DH: форма v1 сама розкладає шматки по висоті піраміди")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 4 — потактова семантика stale_after=3: лічильник повторів дереться до порога
# ────────────────────────────────────────────────────────────────────────────
def fig_tick_freshness():
    W, H = 1060, 470
    f = []
    xs = [170, 350, 530, 710, 890]          # п'ять тактів
    same_vals = [0, 1, 2, 3, 4]             # _same після кожного такту
    heat = ["on", "on", "on", "off", "off"]
    base = 380                              # лінія нуля для стовпчиків
    unit = 50                              # px на одиницю лічильника
    stale_after = 3

    # горизонтальна вісь
    f.append(line(90, base, 980, base, color=MUTED, sw=1.4))

    # поріг застою — пунктир на рівні 3
    ty = base - stale_after * unit
    f.append(line(120, ty, 950, ty, color=POS, sw=1.6, dash="6 5"))
    f.append(text(950, ty - 8, "поріг: _same ≥ 3  (= stale_after)", size=12,
                  color=POS, anchor="end", bold=True))

    # ряд чипів «розетка» вгорі
    for x, h in zip(xs, heat):
        fill = AMBER_FILL if h == "on" else BLUE_FILL
        strk = POS if h == "on" else NEG
        chip, cw, ch = box(x, 92, ["розетка", h], size=12, fill=fill, stroke=strk)
        f.append(chip)

    # стовпчики лічильника
    for x, v in zip(xs, same_vals):
        red = v >= stale_after
        fill = RED_FILL if red else GREEN_FILL
        strk = POS if red else FIELD
        bw = 78
        if v == 0:
            f.append(line(x - bw / 2, base, x + bw / 2, base, color=FIELD, sw=3))
        else:
            top = base - v * unit
            f.append(rect(x - bw / 2, top, bw, v * unit, fill=fill, stroke=strk, sw=1.8))
        f.append(text(x, base - v * unit - 10, str(v), size=15, bold=True,
                      color=POS if red else FIELD))

    # межа спрацювання — між тактами 3 і 4
    dx = (xs[2] + xs[3]) / 2
    f.append(line(dx, 150, dx, base + 4, color=POS, sw=1.6, dash="4 4"))

    # підписи тактів під віссю
    for i, x in enumerate(xs):
        f.append(text(x, base + 24, "такт %d" % (i + 1), size=13, bold=True))
        f.append(text(x, base + 44, "19.9 °C", size=12, color=MUTED))

    f.append(text(dx, 440, "після 3-го повтору вартовий каже «не вірю» — уперше на 4-му вимірі",
                  size=12, color=POS))

    render(os.path.join(IMG, "tick-freshness.svg"), W, H, *f,
           title="Потактова семантика stale_after = 3: лічильник повторів дереться до порога")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 5 — зелено крізь структурний рух, окрім одного навмисного червоного
# ────────────────────────────────────────────────────────────────────────────
def fig_green_except_one_red():
    W, H = 900, 360
    f = []
    col_x = [360, 570, 780]
    row_y = [120, 178, 236, 294]
    cw, ch = 168, 44

    heads = [["v1", "(до вартового)"],
             ["+ FreshnessGuard", "у збірці"],
             ["пін → бажане", "+ регресія"]]
    for x, h in zip(col_x, heads):
        f.append(mtext(x, 62, h, size=12, bold=True, color=INK))

    rows = ["характеризація (пін)", "холодна кімната → on",
            "збій давача → спокій", "регресія вартового"]
    for y, r in zip(row_y, rows):
        f.append(text(250, y + 5, r, size=13, anchor="end", color=INK))

    # G=зелено, R=червоно, N=ще не існує
    grid = [
        ["G", "R", "G"],   # характеризація: зелена → навмисний червоний → знову зелена
        ["G", "G", "G"],   # холодна кімната
        ["G", "G", "G"],   # збій → спокій
        ["N", "N", "G"],   # регресія — з'являється лише на 3-й стадії
    ]
    for gy, y in zip(grid, row_y):
        for st, x in zip(gy, col_x):
            if st == "G":
                f.append(rect(x - cw / 2, y - ch / 2, cw, ch, fill=GREEN_FILL, stroke=FIELD, sw=1.6))
                f.append(text(x, y + 7, "✓", size=20, bold=True, color=FIELD))
            elif st == "R":
                f.append(rect(x - cw / 2, y - ch / 2, cw, ch, fill=RED_FILL, stroke=POS, sw=2.6))
                f.append(text(x, y + 7, "✗", size=20, bold=True, color=POS))
            else:
                f.append(rect(x - cw / 2, y - ch / 2, cw, ch, fill=FILL, stroke=MUTED, sw=1.2))
                f.append(text(x, y + 6, "—", size=15, color=MUTED))

    f.append(text(W / 2, 342, "єдиний червоний — і рівно там, де пришпилили; решта тримає зелене крізь рух",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "green-except-one-red.svg"), W, H, *f,
           title="Зелено крізь структурний рух, окрім одного навмисного червоного")


# ────────────────────────────────────────────────────────────────────────────
# Фіг. 6 — контракт межі замикає простір, з якого будуються фейки
# ────────────────────────────────────────────────────────────────────────────
def fig_contract_space():
    W, H = 960, 380
    f = []

    # зовнішня область — усе, що можна вписати в Reading вручну
    ox, oy, ow, oh = 150, 74, 660, 250
    f.append(rect(ox, oy, ow, oh, fill=AMBER_FILL, stroke=POS, sw=1.6, rx=12))
    f.append(text(ox + ow / 2, oy + 26, "усе, що можна вписати в Reading(…) вручну",
                  size=13, bold=True, color=INK))
    f.append(mtext(ox + ow / 2, oy + 58,
                   ["неможливі стани — зелений тест ТУТ бреше",
                    "напр. Reading(500 °C, ok=True)"],
                   size=12, color=POS))

    # внутрішня область — те, що межа реально породжує
    inner, iw, ih = box(ox + ow / 2, 248,
                        ["що межа РЕАЛЬНО породжує:",
                         "ok=True ∧ −40…85 °C   ·   або ok=False"],
                        size=13, fill=GREEN_FILL, stroke=FIELD, min_w=460)
    inner_left = ox + ow / 2 - iw / 2
    f.append(inner)

    # фабрика reading() ліворуч, стрілка веде лише в зелену область
    fb, fbw, fbh = box(78, 248, ["reading()", "фабрика"], size=12,
                       fill=BLUE_FILL, stroke=NEG)
    f.append(fb)
    f.append(arrow(78 + fbw / 2 + 2, 248, inner_left - 2, 248, color=NEG, sw=1.8))
    f.append(text((78 + fbw / 2 + inner_left) / 2, 237, "лише сюди", size=10, color=NEG))

    render(os.path.join(IMG, "contract-space.svg"), W, H, *f,
           title="Контракт межі замикає простір, з якого будуються фейки")


if __name__ == "__main__":
    fig_double_at_seam()
    fig_char_refactor()
    fig_test_levels()
    fig_tick_freshness()
    fig_green_except_one_red()
    fig_contract_space()
    print("OK: figures written to", IMG)
