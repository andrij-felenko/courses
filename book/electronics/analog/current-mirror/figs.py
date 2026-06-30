# -*- coding: utf-8 -*-
"""Фігури до статті «Дзеркало струмів» (book/electronics/analog/current-mirror).
Чотири фігури:
  copy.svg     — ідея: опорний струм ліворуч → точна копія праворуч (модель-цеглинка)
  diode.svg    — як працює: діодно-увімкнений лівий ставить U_BE, правий її повторює
  bank.svg     — масштаб: один опорний струм роздає кілька різних струмів по чипу
  early.svg    — реальність: копія трохи росте з вихідною напругою (ефект Ерлі)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ───────────────────────────────────────────────────
def gnd(cx, y, label=None):
    out = [line(cx, y, cx, y + 7, color=INK, sw=1.8),
           line(cx - 13, y + 7, cx + 13, y + 7, color=INK, sw=2.4),
           line(cx - 8, y + 12, cx + 8, y + 12, color=INK, sw=2.0),
           line(cx - 3, y + 17, cx + 3, y + 17, color=INK, sw=1.8)]
    if label:
        out.append(text(cx, y + 31, label, size=11, color=MUTED))
    return "".join(out)


def npn(cx, cy, label=None, emit_arrow=True, lab_dx=24):
    """NPN-транзистор: вертикальна «база-лінія», колектор зверху, емітер знизу.
    Повертає (svg, dict-вузлів base/coll/emit як (x,y))."""
    r = 22
    bar_x = cx - 4                    # вертикальна риска бази (всередині кружечка)
    bx_top, bx_bot = cy - 14, cy + 14
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.6),
           line(bar_x, bx_top, bar_x, bx_bot, color=INK, sw=2.6)]      # риска бази
    # вивід бази вліво
    out.append(line(cx - r, cy, bar_x, cy, color=INK, sw=1.6))
    # колектор: від риски вгору-вправо до верху
    cjx, cjy = bar_x, cy - 7
    out.append(line(cjx, cjy, cx + 9, cy - 18, color=INK, sw=1.6))
    out.append(line(cx + 9, cy - 18, cx + 9, cy - r - 6, color=INK, sw=1.6))
    # емітер: від риски вниз-вправо, зі стрілкою назовні
    ejx, ejy = bar_x, cy + 7
    out.append(line(ejx, ejy, cx + 9, cy + 18, color=INK, sw=1.6))
    if emit_arrow:
        out.append(arrow(cx + 4, cy + 11, cx + 9, cy + 18, color=INK, sw=1.8))
    out.append(line(cx + 9, cy + 18, cx + 9, cy + r + 6, color=INK, sw=1.6))
    if label:
        out.append(text(cx - r - lab_dx, cy + 4, label, size=13, color=INK, bold=True, anchor="middle"))
    nodes = {"base": (cx - r, cy), "coll": (cx + 9, cy - r - 6), "emit": (cx + 9, cy + r + 6)}
    return "".join(out), nodes


def isrc(cx, cy, label=None, down=True):
    """Символ джерела струму: кружечок зі стрілкою всередині (напрям струму)."""
    r = 16
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.8)]
    if down:
        out.append(arrow(cx, cy - 9, cx, cy + 9, color=NEG, sw=2.2))
    else:
        out.append(arrow(cx, cy + 9, cx, cy - 9, color=NEG, sw=2.2))
    if label:
        out.append(text(cx - r - 8, cy + 4, label, size=12, color=NEG, bold=True, anchor="end"))
    return "".join(out), (cx, cy - r), (cx, cy + r)


def rail(y, x0, x1, label=None, top=True):
    out = [line(x0, y, x1, y, color=INK, sw=2.4)]
    if label:
        out.append(text(x1 + 6, y + 4, label, size=12, color=INK, bold=True, anchor="start"))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. copy.svg — ідея цеглинки: задав струм тут, отримав копію там
# ════════════════════════════════════════════════════════════════════════════
def fig_copy():
    W, H = 640, 300
    f = []
    # рамка-«пристрій»
    bx, by, bw, bh = 220, 90, 200, 130
    f.append(rect(bx, by, bw, bh, fill="#f4f6f8", stroke=INK, sw=2, rx=12))
    f.append(text(bx + bw / 2, by + 26, "ДЗЕРКАЛО", size=15, bold=True))
    f.append(text(bx + bw / 2, by + 46, "струму", size=12, color=MUTED))

    # ліворуч: вхід — опорний струм
    f.append(text(70, 70, "задаємо тут", size=12, color=MUTED))
    f.append(arrow(60, 155, bx - 4, 155, color=POS, sw=3))
    f.append(text(135, 145, "I_REF", size=14, color=POS, bold=True, anchor="middle"))
    f.append(text(135, 178, "опорний", size=11, color=MUTED, anchor="middle"))

    # праворуч: вихід — копія
    f.append(text(560, 70, "з’являється тут", size=12, color=MUTED))
    f.append(arrow(bx + bw + 4, 155, 600, 155, color=FIELD, sw=3))
    f.append(text(510, 145, "I_OUT ≈ I_REF", size=14, color=FIELD, bold=True, anchor="middle"))
    f.append(text(510, 178, "точна копія", size=11, color=MUTED, anchor="middle"))

    # підпис-суть унизу
    body, w0, h0 = textbox(W / 2, 262, "Не залежить від навантаження праворуч —\nце майже ідеальне джерело струму",
                           size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "copy.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. diode.svg — механізм: спільна U_BE
# ════════════════════════════════════════════════════════════════════════════
def fig_diode():
    W, H = 640, 380
    f = []
    top = 60
    f.append(rail(top, 90, 540, "+V"))

    q1x, q2x, qy = 210, 430, 210
    s1, n1 = npn(q1x, qy, label="Q1", lab_dx=20)
    s2, n2 = npn(q2x, qy, label="Q2", lab_dx=20)
    f.append(s1); f.append(s2)

    # опорна гілка над Q1: джерело струму від +V до колектора Q1
    src, src_top, src_bot = isrc(q1x + 9, top + 55, label="I_REF", down=True)
    f.append(line(q1x + 9, top, src_top[0], src_top[1], color=INK, sw=1.8))
    f.append(src)
    f.append(line(src_bot[0], src_bot[1], n1["coll"][0], n1["coll"][1], color=INK, sw=1.8))

    # діодне з'єднання: база Q1 ↔ колектор Q1 (перемичка)
    bx1 = n1["base"][0]
    f.append(line(bx1 - 26, qy, bx1 - 26, n1["coll"][1] + 6, color=POS, sw=2.2))
    f.append(line(bx1 - 26, qy, bx1, qy, color=POS, sw=2.2))
    f.append(line(bx1 - 26, n1["coll"][1] + 6, q1x + 9, n1["coll"][1] + 6, color=POS, sw=2.2))
    f.append(text(bx1 - 70, qy - 30, "база =", size=11, color=POS, anchor="middle"))
    f.append(text(bx1 - 70, qy - 16, "колектор", size=11, color=POS, anchor="middle"))

    # спільна шина баз Q1—Q2
    by = qy + 2
    f.append(line(bx1 - 26, by, n2["base"][0], by, color=POS, sw=2.2))
    f.append(text((bx1 + n2["base"][0]) / 2 - 20, by - 8, "спільна U_BE", size=12, color=POS, bold=True, anchor="middle"))

    # вихідна гілка: колектор Q2 → навантаження → стрілка копії
    f.append(line(n2["coll"][0], n2["coll"][1], n2["coll"][0], top + 30, color=INK, sw=1.8))
    f.append(arrow(n2["coll"][0], top + 30, n2["coll"][0], top + 4, color=FIELD, sw=2.6))
    f.append(text(n2["coll"][0] + 14, top + 60, "I_OUT", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(n2["coll"][0] + 14, top + 76, "= копія", size=11, color=MUTED, anchor="start"))

    # емітери — на землю
    e1 = n1["emit"]; e2 = n2["emit"]
    f.append(line(e1[0], e1[1], e1[0], 320, color=INK, sw=1.8))
    f.append(line(e2[0], e2[1], e2[0], 320, color=INK, sw=1.8))
    f.append(line(e1[0], 320, e2[0], 320, color=INK, sw=1.8))
    f.append(gnd((e1[0] + e2[0]) / 2, 320))

    # +V вертикалі
    f.append(line(q1x + 9, top, q1x + 9, src_top[1], color=INK, sw=1.8))

    render(os.path.join(IMG, "diode.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. bank.svg — масштаб: один опорний → кілька різних струмів
# ════════════════════════════════════════════════════════════════════════════
def fig_bank():
    W, H = 660, 320
    f = []
    # опорна «форма» ліворуч
    refx = 110
    f.append(rect(refx - 46, 70, 92, 170, fill="#fdecea", stroke=POS, sw=2, rx=10))
    f.append(text(refx, 96, "I_REF", size=14, bold=True, color=POS))
    f.append(text(refx, 116, "опорний", size=11, color=MUTED))
    f.append(arrow(refx, 200, refx, 150, color=POS, sw=2.6))
    f.append(text(refx, 230, "одна\nнастройка", size=11, color=MUTED) if False else
             mtext(refx, 226, ["одна", "настройка"], size=11, color=MUTED))

    # спільна шина баз
    busx = refx + 46
    busy = 155
    f.append(line(busx, busy, 590, busy, color=POS, sw=2.4))
    f.append(text(busx + 8, busy - 10, "спільна U_BE  →  роздаємо копії", size=12, color=POS, bold=True, anchor="start"))

    # три виходи різного масштабу
    outs = [(300, "×1", "I", FIELD), (430, "×2", "2·I", FIELD), (550, "×3", "3·I", FIELD)]
    for ox, mul, lab, col in outs:
        # «ширина» транзистора показує масштаб
        wmul = {"×1": 18, "×2": 30, "×3": 42}[mul]
        f.append(rect(ox - wmul / 2, busy + 8, wmul, 46, fill="#ffffff", stroke=INK, sw=1.6, rx=3))
        f.append(line(ox, busy, ox, busy + 8, color=POS, sw=2.0))           # від шини до бази
        f.append(line(ox, busy + 54, ox, 270, color=INK, sw=1.6))           # емітер вниз
        f.append(arrow(ox, busy - 8, ox, busy - 38, color=col, sw=2.4))     # вихід вгору
        f.append(text(ox, busy - 48, lab, size=13, color=col, bold=True))
        f.append(text(ox, busy + 36, mul, size=12, color=INK, bold=True))
    f.append(line(300, 270, 550, 270, color=INK, sw=1.6))
    f.append(gnd(425, 270))

    f.append(text(W / 2, 300, "Більший транзистор (чи кілька паралельно) → пропорційно більша копія",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "bank.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. early.svg — реальність: похила характеристика (ефект Ерлі)
# ════════════════════════════════════════════════════════════════════════════
def fig_early():
    W, H = 600, 360
    f = []
    ox, oy = 90, 290           # початок осей
    axw, axh = 440, 220
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))            # вісь X
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))           # вісь Y
    f.append(text(ox + axw - 6, oy + 24, "U_OUT (напруга на виході)", size=12, color=INK, anchor="end"))
    f.append(text(ox - 12, oy - axh + 6, "I_OUT", size=13, color=INK, bold=True, anchor="end"))

    # рівень I_REF (ідеал — горизонталь)
    yref = oy - 150
    f.append(line(ox, yref, ox + axw, yref, color=MUTED, sw=1.6, dash="6 5"))
    f.append(text(ox + axw, yref - 8, "ідеал: I_OUT = I_REF", size=11, color=MUTED, anchor="end"))

    # реальна крива: різко вгору в зоні насичення, далі майже горизонталь із легким нахилом
    # точки
    knee = ox + 70
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f L %.0f %.0f" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ox, oy - 6, knee - 20, yref + 20, knee, yref + 6, ox + axw - 6, yref - 34, POS))
    f.append(text(knee + 120, yref - 6, "реальне дзеркало:", size=12, color=POS, bold=True, anchor="middle"))
    f.append(text(knee + 120, yref + 12, "копія трохи росте з напругою", size=11, color=POS, anchor="middle"))

    # зона «надто мало напруги» ліворуч від коліна
    f.append(line(knee, oy, knee, oy - axh + 30, color=NEG, sw=1.4, dash="4 4"))
    f.append(text(knee, oy + 16, "U_min", size=11, color=NEG, anchor="middle"))
    body, w0, h0 = textbox((ox + knee) / 2 + 4, oy - 70,
                           "тут напруги\nзамало —\nкопія падає", size=10, color=NEG,
                           fill="#eaf0fd", stroke=NEG)
    f.append(body)

    # підпис нахилу = ефект Ерлі
    f.append(text(W / 2, 338, "Нахил «полиці» задає ефект Ерлі — що він менший, то ближче дзеркало до ідеального джерела струму",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "early.svg"), W, H, *f)


def resistor(x, y0, y1, label=None, side="left"):
    """Вертикальний резистор-зигзаг між (x,y0) та (x,y1)."""
    out = []
    n = 6
    seg = (y1 - y0) / (n + 1)
    out.append(line(x, y0, x, y0 + seg, color=INK, sw=1.6))
    amp = 6
    yy = y0 + seg
    for i in range(n):
        nx = x + (amp if i % 2 == 0 else -amp)
        out.append(line(x if i == 0 else (x - amp if i % 2 == 1 else x + amp),
                        yy, nx, yy + seg, color=INK, sw=1.6))
        yy += seg
    out.append(line(x + (amp if (n - 1) % 2 == 0 else -amp), yy, x, yy + seg, color=INK, sw=1.6))
    out.append(line(x, yy + seg, x, y1, color=INK, sw=1.6))
    if label:
        lx = x - 16 if side == "left" else x + 16
        an = "end" if side == "left" else "start"
        out.append(text(lx, (y0 + y1) / 2 + 4, label, size=12, color=POS, bold=True, anchor=an))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 5. widlar.svg — джерело Відлара: резистор в емітері ЛИШЕ вихідного транзистора
# ════════════════════════════════════════════════════════════════════════════
def fig_widlar():
    W, H = 660, 430
    f = []
    top = 56
    f.append(rail(top, 90, 560, "+V"))

    q1x, q2x, qy = 220, 450, 220
    s1, n1 = npn(q1x, qy, label="Q1", lab_dx=20)
    s2, n2 = npn(q2x, qy, label="Q2", lab_dx=20)
    f.append(s1); f.append(s2)

    # опорна гілка над Q1
    src, src_top, src_bot = isrc(q1x + 9, top + 52, label="I_REF", down=True)
    f.append(line(q1x + 9, top, src_top[0], src_top[1], color=INK, sw=1.8))
    f.append(src)
    f.append(line(src_bot[0], src_bot[1], n1["coll"][0], n1["coll"][1], color=INK, sw=1.8))

    # діодне з'єднання Q1
    bx1 = n1["base"][0]
    f.append(line(bx1 - 26, qy, bx1 - 26, n1["coll"][1] + 6, color=POS, sw=2.2))
    f.append(line(bx1 - 26, qy, bx1, qy, color=POS, sw=2.2))
    f.append(line(bx1 - 26, n1["coll"][1] + 6, q1x + 9, n1["coll"][1] + 6, color=POS, sw=2.2))

    # спільна шина баз
    by = qy + 2
    f.append(line(bx1 - 26, by, n2["base"][0], by, color=POS, sw=2.2))
    f.append(text((bx1 + n2["base"][0]) / 2 - 10, by - 8, "спільна U_BE", size=12, color=POS, bold=True, anchor="middle"))

    # вихід Q2
    f.append(line(n2["coll"][0], n2["coll"][1], n2["coll"][0], top + 26, color=INK, sw=1.8))
    f.append(arrow(n2["coll"][0], top + 26, n2["coll"][0], top + 4, color=FIELD, sw=2.6))
    f.append(text(n2["coll"][0] + 14, top + 50, "I_OUT", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(n2["coll"][0] + 14, top + 66, "(мала копія)", size=11, color=MUTED, anchor="start"))

    # емітер Q1 — прямо на землю
    e1 = n1["emit"]
    f.append(line(e1[0], e1[1], e1[0], 360, color=INK, sw=1.8))
    # емітер Q2 — крізь резистор R на землю (ОСЬ ХІТ Відлара)
    e2 = n2["emit"]
    f.append(resistor(e2[0], e2[1] + 4, 340, label="R_E", side="right"))
    f.append(line(e2[0], 340, e2[0], 360, color=INK, sw=1.8))
    f.append(line(e1[0], 360, e2[0], 360, color=INK, sw=1.8))
    f.append(gnd((e1[0] + e2[0]) / 2, 360))

    f.append(line(q1x + 9, top, q1x + 9, src_top[1], color=INK, sw=1.8))

    # винесений підпис-суть
    body, w0, h0 = textbox(W / 2, 405,
                           "Резистор лише в емітері Q2 «з’їдає» крихітну частку U_BE —\nі копія виходить набагато меншою за опорний струм",
                           size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "widlar.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. wilson.svg — дзеркало Вілсона: трійка транзисторів, петля ВЗЗ
# ════════════════════════════════════════════════════════════════════════════
def fig_wilson():
    # Канонічна BJT-схема Вілсона:
    #   Q1 (ліворуч), Q2 (праворуч) — спарена пара, емітери на землю, бази спільні.
    #   Q2 діодний: його колектор замкнено на спільну шину баз.
    #   I_REF входить у вузол «колектор Q1 = база Q3» (вхід-сенс).
    #   Q3 згори: емітер сідає на колектор Q2 (діодний вузол), колектор Q3 — вихід.
    W, H = 680, 450
    f = []
    top = 56
    f.append(rail(top, 90, 590, "+V"))

    q1x, q2x, qy = 250, 430, 260
    s1, n1 = npn(q1x, qy, label="Q1", lab_dx=20)
    s2, n2 = npn(q2x, qy, label="Q2", lab_dx=18)
    f.append(s1); f.append(s2)

    q3x, q3y = q2x, qy - 120
    s3, n3 = npn(q3x, q3y, label="Q3", lab_dx=18)
    f.append(s3)

    # вхід-сенс: спільний вузол «колектор Q1 = база Q3», у який згори вганяють I_REF
    inx = n1["coll"][0]
    sense_y = q3y
    # опорне джерело згори в той вузол
    src, src_top, src_bot = isrc(inx, top + 40, label="I_REF", down=True)
    f.append(line(inx, top, src_top[0], src_top[1], color=INK, sw=1.8))
    f.append(src)
    # увесь спинний провід вузла входу — синій (вузол сенсу), від джерела до колектора Q1
    f.append(line(inx, src_bot[1], inx, n1["coll"][1], color=NEG, sw=2.2))
    # відгалуження на базу Q3
    f.append(line(inx, sense_y, n3["base"][0], sense_y, color=NEG, sw=2.2))
    f.append(circle(inx, sense_y, 2.6, fill=NEG, stroke=NEG))
    f.append(text(inx - 8, sense_y - 14, "вузол", size=11, color=NEG, bold=True, anchor="end"))
    f.append(text(inx - 8, sense_y, "входу", size=11, color=NEG, bold=True, anchor="end"))

    # емітер Q3 → колектор Q2 (діодний вузол, тут зрівнюються струми)
    e3 = n3["emit"]
    midnode_y = (e3[1] + n2["coll"][1]) / 2
    f.append(line(e3[0], e3[1], e3[0], n2["coll"][1], color=INK, sw=1.8))
    f.append(circle(e3[0], n2["coll"][1], 2.6, fill=INK, stroke=INK))

    # вихід — колектор Q3 вгору
    f.append(line(n3["coll"][0], n3["coll"][1], n3["coll"][0], top + 26, color=INK, sw=1.8))
    f.append(arrow(n3["coll"][0], top + 26, n3["coll"][0], top + 4, color=FIELD, sw=2.6))
    f.append(text(n3["coll"][0] + 14, top + 50, "I_OUT", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(n3["coll"][0] + 14, top + 66, "≈ I_REF", size=11, color=MUTED, anchor="start"))

    # спільна шина баз Q1—Q2, замкнена на колектор Q2 (діодне ввімкнення Q2)
    bx1 = n1["base"][0]
    busx = bx1 - 28
    by = qy + 2
    f.append(line(busx, by, bx1, by, color=POS, sw=2.2))               # вивід бази Q1
    f.append(line(busx, by, n2["base"][0], by, color=POS, sw=2.2))     # шина до бази Q2
    # від шини вгору до колектора Q2 (діод Q2)
    f.append(line(n2["coll"][0], by, n2["coll"][0], n2["coll"][1], color=POS, sw=2.2))
    f.append(circle(n2["coll"][0], n2["coll"][1], 2.6, fill=POS, stroke=POS))
    f.append(text((busx + n2["base"][0]) / 2 - 6, by + 22, "спільні бази  (Q2 — діодний)", size=11, color=POS, bold=True, anchor="middle"))

    # емітери Q1,Q2 на землю
    e1 = n1["emit"]; e2 = n2["emit"]
    f.append(line(e1[0], e1[1], e1[0], 370, color=INK, sw=1.8))
    f.append(line(e2[0], e2[1], e2[0], 370, color=INK, sw=1.8))
    f.append(line(e1[0], 370, e2[0], 370, color=INK, sw=1.8))
    f.append(gnd((e1[0] + e2[0]) / 2, 370))

    # підпис петлі
    body, w0, h0 = textbox(W / 2, 420,
                           "Зросте I_OUT → більший струм у Q2 → вища напруга баз → Q1 спускає вузол входу →\nQ3 пригальмовує: петля від’ємного зв’язку тримає I_OUT = I_REF і піднімає вихідний опір",
                           size=11, color=INK, fill="#eaf0fd", stroke=NEG)
    f.append(body)
    render(os.path.join(IMG, "wilson.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 7. cascode.svg — каскодне дзеркало: другий поверх «екранує» вихід від напруги
# ════════════════════════════════════════════════════════════════════════════
def fig_cascode():
    W, H = 660, 440
    f = []
    top = 56
    f.append(rail(top, 90, 560, "+V"))

    # нижній поверх — звичайне дзеркало Q1(діод)/Q2
    q1x, q2x, qy = 220, 440, 300
    s1, n1 = npn(q1x, qy, label="Q1", lab_dx=20)
    s2, n2 = npn(q2x, qy, label="Q2", lab_dx=18)
    f.append(s1); f.append(s2)

    # верхній поверх — Q3 над Q1 (діодний), Q4 над Q2 (вихідний)
    q3y = qy - 120
    s3, n3 = npn(q1x, q3y, label="Q3", lab_dx=20)
    s4, n4 = npn(q2x, q3y, label="Q4", lab_dx=18)
    f.append(s3); f.append(s4)

    # опорна гілка над Q3
    src, src_top, src_bot = isrc(q1x + 9, top + 40, label="I_REF", down=True)
    f.append(line(q1x + 9, top, src_top[0], src_top[1], color=INK, sw=1.8))
    f.append(src)
    f.append(line(src_bot[0], src_bot[1], n3["coll"][0], n3["coll"][1], color=INK, sw=1.8))
    f.append(line(q1x + 9, top, q1x + 9, src_top[1], color=INK, sw=1.8))

    # колектор Q3 = бази Q3,Q4 (верхній діод і верхня спільна шина баз)
    bx3 = n3["base"][0]
    f.append(line(bx3 - 26, q3y, bx3 - 26, n3["coll"][1] + 6, color=POS, sw=2.2))
    f.append(line(bx3 - 26, q3y, bx3, q3y, color=POS, sw=2.2))
    f.append(line(bx3 - 26, n3["coll"][1] + 6, q1x + 9, n3["coll"][1] + 6, color=POS, sw=2.2))
    f.append(line(bx3 - 26, q3y, n4["base"][0], q3y, color=POS, sw=2.2))
    f.append(text((bx3 + n4["base"][0]) / 2, q3y - 8, "верхня шина", size=10, color=POS, anchor="middle"))

    # емітер Q3 → колектор Q1 ; емітер Q4 → колектор Q2 (поверхи послідовно)
    f.append(line(n3["emit"][0], n3["emit"][1], n1["coll"][0], n1["coll"][1], color=INK, sw=1.8))
    f.append(line(n4["emit"][0], n4["emit"][1], n2["coll"][0], n2["coll"][1], color=INK, sw=1.8))

    # нижня спільна шина баз Q1,Q2 — і діодне Q1 (база Q1 ↔ колектор Q1)
    bx1 = n1["base"][0]
    by = qy + 2
    f.append(line(bx1 - 26, by, bx1, by, color=NEG, sw=2.2))
    f.append(line(bx1 - 26, by, bx1 - 26, n1["coll"][1], color=NEG, sw=2.2))
    f.append(line(bx1 - 26, n1["coll"][1], q1x + 9, n1["coll"][1], color=NEG, sw=2.2))
    f.append(line(bx1 - 26, by, n2["base"][0], by, color=NEG, sw=2.2))
    f.append(text((bx1 + n2["base"][0]) / 2, by + 22, "нижня шина", size=10, color=NEG, anchor="middle"))

    # вихід — колектор Q4 вгору
    f.append(line(n4["coll"][0], n4["coll"][1], n4["coll"][0], top + 26, color=INK, sw=1.8))
    f.append(arrow(n4["coll"][0], top + 26, n4["coll"][0], top + 4, color=FIELD, sw=2.6))
    f.append(text(n4["coll"][0] + 14, top + 50, "I_OUT", size=13, color=FIELD, bold=True, anchor="start"))

    # емітери Q1,Q2 на землю
    e1 = n1["emit"]; e2 = n2["emit"]
    f.append(line(e1[0], e1[1], e1[0], 360, color=INK, sw=1.8))
    f.append(line(e2[0], e2[1], e2[0], 360, color=INK, sw=1.8))
    f.append(line(e1[0], 360, e2[0], 360, color=INK, sw=1.8))
    f.append(gnd((e1[0] + e2[0]) / 2, 360))

    # підпис
    f.append(text(W / 2, 396, "Верхній поверх (Q3·Q4) тримає на нижньому майже сталу напругу —",
                  size=11, color=MUTED))
    f.append(text(W / 2, 414, "тож вихід Q2 майже не «бачить» гойдання U_OUT, і нахил від ефекту Ерлі різко падає",
                  size=11, color=MUTED))
    render(os.path.join(IMG, "cascode.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 8. hist-timeline.svg — дві незалежні «колиски» дзеркала струму (для hist-вставки)
#    Верхня доріжка: Fairchild / Widlar (масове виробництво ОП → джерело Відлара).
#    Нижня доріжка: Tektronix / Wilson (нічне парі з Gilbert → дзеркало Вілсона).
# ════════════════════════════════════════════════════════════════════════════
def fig_hist_timeline():
    W, H = 720, 430
    f = []

    x0, x1 = 96, 648
    years = [1963, 1964, 1965, 1966, 1967]

    def xy(year):
        return x0 + (x1 - x0) * (year - years[0]) / (years[-1] - years[0])

    # верхня доріжка — Fairchild / Widlar
    yA = 150
    f.append(line(x0, yA, x1, yA, color=POS, sw=2.6))
    f.append(text(x0 - 6, yA - 20, "Fairchild · Каліфорнія", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(x0 - 6, yA - 4, "Bob Widlar — як здешевити перші ОП", size=11, color=MUTED, anchor="start"))

    # нижня доріжка — Tektronix / Wilson
    yB = 300
    f.append(line(x0, yB, x1, yB, color=NEG, sw=2.6))
    f.append(text(x0 - 6, yB + 30, "Tektronix · Беавертон, Орегон", size=12, color=NEG, bold=True, anchor="start"))
    f.append(text(x0 - 6, yB + 46, "George Wilson — нічне парі з Barrie Gilbert", size=11, color=MUTED, anchor="start"))

    # сітка років
    for yr in years:
        xx = xy(yr)
        f.append(line(xx, yA - 6, xx, yB + 6, color="#e3e6ea", sw=1.2))
        f.append(text(xx, H - 18, str(yr), size=12, color=INK, bold=True))

    def node(xx, yy, col):
        return circle(xx, yy, 6, fill="#ffffff", stroke=col, sw=2.6)

    # події верхньої доріжки
    f.append(node(xy(1964), yA, POS))
    bb, _, _ = textbox(xy(1964), yA - 54, "μA702\nперший монолітний ОП", size=10, color=INK,
                       fill="#fdecea", stroke=POS)
    f.append(bb)

    f.append(node(xy(1965), yA, POS))
    bb, _, _ = textbox(xy(1965) + 8, yA + 50, "μA709 — масовий ринок;\nстаття про джерело струму", size=10, color=INK,
                       fill="#fdecea", stroke=POS)
    f.append(bb)

    f.append(node(xy(1967), yA, POS))
    bb, _, _ = textbox(xy(1967) - 34, yA - 54, "патент 3 320 439\nджерело Відлара", size=10, color=INK,
                       fill="#fdecea", stroke=POS)
    f.append(bb)

    # подія нижньої доріжки — лише 1967
    f.append(node(xy(1967), yB, NEG))
    bb, _, _ = textbox(xy(1967) - 34, yB + 58, "дзеркало Вілсона\n(за одну ніч)", size=10, color=INK,
                       fill="#eaf0fd", stroke=NEG)
    f.append(bb)

    f.append(text(W / 2, 36, "Дві незалежні колиски однієї цеглинки", size=16, bold=True))

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_copy()
    fig_diode()
    fig_bank()
    fig_early()
    fig_widlar()
    fig_wilson()
    fig_cascode()
    fig_hist_timeline()
    print("OK: 8 фігур у", IMG)
