# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def tbox(cx, cy, s, **kw):
    """textbox повертає (frag,w,h) — беремо лише фрагмент."""
    return textbox(cx, cy, s, **kw)[0]


def nmos(cx, cy, on=False, label="N"):
    """n-канальний ключ: вертикальний канал, затвор зліва. on → зелений (відкритий)."""
    col = FIELD if on else MUTED
    ch = INK if on else MUTED
    out = [line(cx, cy - 30, cx, cy + 30, color=ch, sw=2.6)]
    out.append(line(cx - 26, cy, cx - 9, cy, color=ch, sw=2))
    out.append(line(cx - 9, cy - 14, cx - 9, cy + 14, color=ch, sw=2.6))
    out.append(text(cx + 12, cy - 20, label, size=12, color=col, bold=True, anchor="start"))
    return "".join(out)


def pmos(cx, cy, on=False, label="P"):
    """p-канальний ключ: кружок на затворі. on → зелений (відкритий)."""
    col = FIELD if on else MUTED
    ch = INK if on else MUTED
    out = [line(cx, cy - 30, cx, cy + 30, color=ch, sw=2.6)]
    out.append(line(cx - 26, cy, cx - 14, cy, color=ch, sw=2))
    out.append(circle(cx - 11, cy, 4.5, fill=BG, stroke=ch, sw=2))
    out.append(line(cx - 6.5, cy - 14, cx - 6.5, cy + 14, color=ch, sw=2.6))
    out.append(text(cx + 12, cy - 20, label, size=12, color=col, bold=True, anchor="start"))
    return "".join(out)


def pp_stack(cx, top_on, bot_on, head, head_col, path_col):
    """Стовпчик push-pull VDD—P—вузол—N—GND; активна вітка кольорова, шлях до низу."""
    out = []
    yv, yp, ynode, yn, yg = 70, 108, 165, 222, 260
    out.append(text(cx, yv - 8, "VDD", size=12, color=MUTED))
    out.append(text(cx, 52, head, size=13, color=head_col, bold=True))
    # верх: VDD → P → вузол
    tcol = INK if top_on else MUTED
    out.append(line(cx, yv, cx, yp - 30, color=tcol, sw=2,
                    dash=None if top_on else "4,4"))
    out.append(pmos(cx, yp, on=top_on, label="P"))
    out.append(line(cx, yp + 30, cx, ynode, color=tcol, sw=2,
                    dash=None if top_on else "4,4"))
    # вузол-ніжка
    out.append(circle(cx, ynode, 4, fill=INK, stroke=INK))
    # низ: вузол → N → GND
    bcol = INK if bot_on else MUTED
    out.append(line(cx, ynode, cx, yn - 30, color=bcol, sw=2,
                    dash=None if bot_on else "4,4"))
    out.append(nmos(cx, yn, on=bot_on, label="N"))
    out.append(line(cx, yn + 30, cx, yg, color=bcol, sw=2,
                    dash=None if bot_on else "4,4"))
    out.append(text(cx, yg + 16, "GND", size=12, color=MUTED))
    return "".join(out), ynode


# ─────────────────────────────────────────────────────────────────────────────
# 1) contention.svg — два push-pull виходи на спільному дроті → коротке
# ─────────────────────────────────────────────────────────────────────────────
def fig_contention():
    W, H = 720, 380
    f = []
    lx, rx = 190, 530
    ly = 165  # рівень спільного вузла-дроту

    left, ynode = pp_stack(lx, True, False, "вихід A → «1»", POS, POS)
    right, _ = pp_stack(rx, False, True, "вихід B → «0»", NEG, NEG)
    f.append(left)
    f.append(right)

    # спільний дріт між вузлами обох виходів
    f.append(line(lx, ly, rx, ly, color=INK, sw=3.2))
    f.append(text(360, ly - 12, "спільний дріт", size=13, color=MUTED))

    # A тягне вгору (червоний доходить від VDD до вузла), B тягне вниз (синій від вузла до GND)
    # позначки напрямку зусиль на дроті
    f.append(text(lx + 60, ly + 5, "тягне ↑ VDD", size=12, color=POS, anchor="start"))
    f.append(text(rx - 60, ly + 5, "тягне ↓ GND", size=12, color=NEG, anchor="end"))

    # блискавка конфлікту посередині
    zx = 360
    f.append(text(zx, ly + 40, "⚡ конфлікт на шині", size=15, color=POS, bold=True))
    box = tbox(zx, ly + 92,
               "наскрізний струм VDD → GND крізь\nобидва ключі; напруга — в забороненій зоні",
               size=13, color=POS, stroke=POS, fill="#fdecea")
    f.append(box)
    render(os.path.join(OUT, "contention.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2) three-states.svg — HIGH / LOW / Hi-Z однієї пари транзисторів
# ─────────────────────────────────────────────────────────────────────────────
def one_stage(cx, top_on, bot_on, cap, cap_col, pin_txt, pin_col):
    """Один стовпчик push-pull: VDD — P — ніжка — N — GND."""
    out = []
    yv, yp, ypin, yn, yg = 78, 120, 180, 240, 282
    out.append(text(cx, 58, "VDD", size=12, color=MUTED))
    out.append(line(cx, yv, cx, yp - 30, color=INK if top_on else MUTED, sw=2))
    out.append(pmos(cx, yp, on=top_on, label="P"))
    out.append(line(cx, yp + 30, cx, ypin, color=INK if top_on else MUTED,
                    sw=2, dash=None if top_on else "4,4"))
    # ніжка (вузол)
    out.append(circle(cx, ypin, 4, fill=INK, stroke=INK))
    out.append(line(cx, ypin, cx + 52, ypin, color=INK, sw=2.4))
    out.append(text(cx + 58, ypin - 8, pin_txt, size=13, color=pin_col, bold=True, anchor="start"))
    out.append(line(cx, ypin, cx, yn - 30, color=INK if bot_on else MUTED,
                    sw=2, dash=None if bot_on else "4,4"))
    out.append(nmos(cx, yn, on=bot_on, label="N"))
    out.append(line(cx, yn + 30, cx, yg, color=INK if bot_on else MUTED, sw=2))
    out.append(text(cx, yg + 16, "GND", size=12, color=MUTED))
    # підпис стану
    out.append(tbox(cx + 6, 330, cap, size=13, color=cap_col, stroke=cap_col, bold=True))
    return "".join(out)


def fig_three_states():
    W, H = 760, 370
    f = []
    f.append(one_stage(150, True, False, "HIGH\nверхній відкритий", POS,
                       "1", POS))
    f.append(one_stage(400, False, True, "LOW\nнижній відкритий", NEG,
                       "0", NEG))
    f.append(one_stage(650, False, False, "Hi-Z\nобидва закриті", FIELD,
                       "Z", FIELD))
    # роздільники
    f.append(line(275, 50, 275, 300, color="#dddddd", sw=1))
    f.append(line(525, 50, 525, 300, color="#dddddd", sw=1))
    render(os.path.join(OUT, "three-states.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3) tristate-buffer.svg — символ буфера з входом дозволу
# ─────────────────────────────────────────────────────────────────────────────
def buffer_symbol(cx, cy, oe_on, out_txt, out_col):
    """Трикутник-буфер із входом даних зліва, дозволом знизу, виходом справа."""
    out = []
    # трикутник
    p = "%d,%d %d,%d %d,%d" % (cx - 34, cy - 30, cx - 34, cy + 30, cx + 40, cy)
    out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>'
               % (p, FILL, INK))
    # вхід даних
    out.append(line(cx - 90, cy, cx - 34, cy, color=INK, sw=2.4))
    out.append(text(cx - 96, cy + 4, "дані", size=13, color=INK, anchor="end"))
    # вихід
    out.append(line(cx + 40, cy, cx + 96, cy, color=out_col, sw=2.6))
    out.append(text(cx + 102, cy + 4, out_txt, size=14, color=out_col, bold=True, anchor="start"))
    # вхід дозволу знизу
    oe_col = FIELD if oe_on else MUTED
    out.append(line(cx - 3, cy + 60, cx - 3, cy + 15, color=oe_col, sw=2.4))
    out.append(text(cx - 3, cy + 76, "OE", size=13, color=oe_col, bold=True))
    return "".join(out)


def fig_tristate_buffer():
    W, H = 720, 340
    f = []
    # лівий: дозвіл активний → активний вихід
    f.append(text(190, 55, "дозвіл активний (OE = 1)", size=13, color=FIELD, bold=True))
    f.append(buffer_symbol(190, 150, True, "0 / 1", INK))
    f.append(tbox(190, 250, "вихід повторює вхід —\nміцно, активно", size=13,
                  color=INK, stroke=FIELD))
    # правий: дозвіл знятий → Hi-Z
    f.append(text(540, 55, "дозвіл знятий (OE = 0)", size=13, color=MUTED, bold=True))
    f.append(buffer_symbol(540, 150, False, "Z", FIELD))
    f.append(tbox(540, 250, "вихід відірваний від лінії —\nHi-Z, хай там що на вході",
                  size=13, color=FIELD, stroke=FIELD))
    f.append(line(365, 50, 365, 290, color="#dddddd", sw=1))
    render(os.path.join(OUT, "tristate-buffer.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4) shared-bus.svg — багато чіпів на одному дроті, активний один
# ─────────────────────────────────────────────────────────────────────────────
def fig_shared_bus():
    W, H = 760, 340
    f = []
    busy = 230
    f.append(line(70, busy, 690, busy, color=INK, sw=3.5))
    f.append(text(380, busy - 12, "спільна шина (один дріт)", size=13, color=MUTED))

    xs = [130, 300, 470, 640]
    active = 1  # другий говорить
    labels = ["A", "B", "C", "D"]
    for i, x in enumerate(xs):
        on = (i == active)
        col = POS if on else FIELD
        state = "активний → «1»" if on else "Hi-Z"
        # блок чіпа
        f.append(rect(x - 52, 78, 104, 60, fill=("#fdecea" if on else FILL),
                      stroke=(POS if on else MUTED), sw=2))
        f.append(text(x, 100, "чіп " + labels[i], size=14, bold=True,
                      color=(POS if on else INK)))
        f.append(text(x, 122, state, size=12, color=col, bold=on))
        # ніжка до шини
        if on:
            f.append(arrow(x, 138, x, busy, color=POS, sw=2.6))
        else:
            f.append(line(x, 138, x, busy - 14, color=MUTED, sw=1.6, dash="4,4"))
            f.append(text(x + 4, busy - 20, "⟂", size=13, color=FIELD, anchor="start"))

    # підпис-правило
    f.append(tbox(380, 300,
                  "правило шини: активний рівно ОДИН, решта — у Hi-Z",
                  size=14, color=INK, stroke=INK, bold=True))
    render(os.path.join(OUT, "shared-bus.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 5) tri-state-timeline.svg — хроніка «третього стану» й марки TRI-STATE
#    Суцільні віхи = документовані (патенти/марка); пунктир = приписуване.
# ─────────────────────────────────────────────────────────────────────────────
def fig_timeline():
    W, H = 760, 430
    f = []
    ax_y = 250
    x0, x1 = 70, 690
    f.append(line(x0, ax_y, x1, ax_y, color=INK, sw=3))
    f.append(text(x1 + 4, ax_y + 5, "час", size=12, color=MUTED, anchor="start"))

    # (позиція_x, рік, підпис, «догори?», надійно?)
    ev = [
        (110, "1964", ["TI: серія", "SN5400 (TTL)"], True,  True),
        (215, "1966", ["SN7400 —", "дешевий пластик"], False, True),
        (335, "~1967", ["приписують", "3-й стан (Mrazek?)"], True, False),
        (455, "VIII.1970", ["перше вживання", "марки TRI-STATE"], False, True),
        (545, "V.1971", ["у продажу", "(в обігу)"], True,  True),
        (635, "1972", ["марку", "зареєстровано"], False, True),
    ]
    for x, yr, lbl, up, solid in ev:
        col = INK if solid else MUTED
        dash = None if solid else "5,4"
        # віха на осі
        f.append(circle(x, ax_y, 6, fill=(INK if solid else BG), stroke=col, sw=2.4))
        # виноска
        ly = ax_y - 96 if up else ax_y + 44
        f.append(line(x, ax_y + (-6 if up else 6), x, ly + (34 if up else -4),
                      color=col, sw=1.6, dash=dash))
        # рік
        yry = ax_y + (-104 if up else 96)
        f.append(text(x, yry, yr, size=13, color=col, bold=True))
        # підпис у рамці, що влазить
        bh = 34
        by = (ly if up else ly)
        f.append(fitbox(x - 62, by, 124, bh, "\n".join(lbl), size=11,
                        color=col, stroke=col,
                        fill=(FILL if solid else BG)))

    # легенда доказовості
    f.append(circle(120, 350, 6, fill=INK, stroke=INK, sw=2))
    f.append(text(134, 355, "суцільне — документовано (патент/марка USPTO)",
                  size=12, color=INK, anchor="start"))
    f.append(circle(120, 376, 6, fill=BG, stroke=MUTED, sw=2))
    f.append(text(134, 381, "пунктир — приписувано, первинно не підтверджено",
                  size=12, color=MUTED, anchor="start"))

    f.append(text(W / 2, 405,
                  "TRI-STATE™ — марка National Semiconductor; родова назва — three-state / Hi-Z",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "tri-state-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_contention()
    fig_three_states()
    fig_tristate_buffer()
    fig_shared_bus()
    fig_timeline()
    print("done:", os.listdir(OUT))
