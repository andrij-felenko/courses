# -*- coding: utf-8 -*-
"""Фігури до вставки «ESD-збірки й діодні масиви» (comp-tvs-array.md).
Окремий генератор, щоб не чіпати figs.py теми. Запуск:  python figs_tvs_array.py
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def diode_up(cx, y0, y1, color=INK, sw=2.0):
    """Діод вістрям УГОРУ (проводить знизу→вгору), від y0 (низ) до y1 (верх)."""
    midy = (y0 + y1) / 2
    h = 13
    out = line(cx, y0, cx, midy + h / 2, color=color, sw=sw)
    tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx - 7, midy + h / 2, cx + 7, midy + h / 2, cx, midy - h / 2)
    out += '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (tri, "#eef2f7", color, sw)
    out += line(cx - 7, midy - h / 2, cx + 7, midy - h / 2, color=color, sw=sw + 0.4)  # катодна риска
    out += line(cx, midy - h / 2, cx, y1, color=color, sw=sw)
    return out


def ground(cx, y, color=LINE, sw=2.0):
    out = line(cx, y, cx, y + 7, color=color, sw=sw)
    for i, w in enumerate((15, 9, 4)):
        out += line(cx - w / 2, y + 7 + i * 4.5, cx + w / 2, y + 7 + i * 4.5, color=color, sw=sw)
    return out


def tvs_clamp_v(cx, ty, by, color=INK, sw=2.2):
    """Вертикальний TVS-символ (рейковий клам) від ty (верх, катод) до by (низ, анод)."""
    h = 18
    midy = (ty + by) / 2
    out = line(cx, by, cx, midy + h / 2, color=color, sw=sw)
    tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx - 9, midy + h / 2, cx + 9, midy + h / 2, cx, midy - h / 2)
    out += '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (tri, "#fdecea", color, sw)
    ky = midy - h / 2
    out += line(cx - 10, ky, cx + 10, ky, color=color, sw=sw + 0.6)
    out += line(cx - 10, ky, cx - 10, ky - 4, color=color, sw=sw)
    out += line(cx + 10, ky, cx + 10, ky + 4, color=color, sw=sw)
    out += line(cx, ty, cx, ky, color=color, sw=sw)
    return out


# ── 1. Внутрішня топологія масиву: steering-діоди на шини + центральний TVS ──
def fig_array_topology():
    W, H = 780, 470
    f = [text(W / 2, 26, "Усередині ESD-збірки: пара steering-діодів на канал + один TVS на шини",
              size=15, bold=True)]

    vcc_y = 86            # шина VCC згори
    gnd_y = 398           # шина GND знизу
    rail_x0, rail_x1 = 70, 600
    # шини
    f.append(line(rail_x0, vcc_y, rail_x1, vcc_y, color=POS, sw=2.6))
    f.append(line(rail_x0, gnd_y, rail_x1, gnd_y, color=NEG, sw=2.6))
    f.append(text(rail_x0 - 4, vcc_y - 10, "шина V+", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(rail_x0 - 4, gnd_y + 22, "шина GND (спільний вивід)", size=12, color=NEG, bold=True, anchor="start"))

    # три канали I/O
    chans = [(150, "I/O 1"), (270, "I/O 2"), (390, "I/O 3")]
    sig_y = 242
    for cx, name in chans:
        # вивід каналу зліва
        f.append(circle(cx, sig_y, 4, fill=BG, stroke=INK, sw=1.6))
        f.append(text(cx, sig_y + 34, name, size=11, color=INK, bold=True))
        f.append(line(cx - 28, sig_y, cx, sig_y, color=LINE, sw=2.0))
        f.append(text(cx - 40, sig_y - 8, "→", size=14, color=MUTED, anchor="middle"))
        # верхній steering-діод: сигнал → V+ (вістря вгору)
        f.append(diode_up(cx, sig_y - 6, vcc_y, color=POS, sw=2.0))
        # нижній steering-діод: GND → сигнал (вістря вгору, проводить знизу вгору)
        f.append(diode_up(cx, gnd_y, sig_y + 6, color=NEG, sw=2.0))

    # центральний TVS між шинами (праворуч)
    tvs_x = 520
    f.append(tvs_clamp_v(tvs_x, vcc_y, gnd_y, color=FIELD, sw=2.4))
    b, _, _ = textbox(tvs_x + 60, (vcc_y + gnd_y) / 2 - 30, "центральний TVS\n(рейковий клам)",
                      size=11, fill="#eef6ef", stroke=FIELD, color=INK, bold=True)
    f.append(b)

    # шлях додатного розряду: I/O1 → вгору → V+ → TVS → GND
    pulse_x = 150
    f.append(text(pulse_x, sig_y - 70, "+ESD", size=12, color=POS, bold=True))
    f.append(arrow(pulse_x + 14, sig_y - 64, pulse_x + 14, vcc_y + 8, color=POS, sw=2.2))
    f.append(arrow(tvs_x + 16, vcc_y + 16, tvs_x + 16, gnd_y - 8, color=FIELD, sw=2.2))
    b, _, _ = textbox(640, (vcc_y + gnd_y) / 2 + 50, "+розряд: вгору\nна V+, далі TVS\nзливає на GND",
                      size=10.5, fill=BG, stroke=POS, color=INK)
    f.append(b)

    # підпис унизу
    f.append(text(W / 2, gnd_y + 56, "кожен канал — лише дві маленькі діодні риски; уся енергія йде в один спільний TVS",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "tvs-array-topology.svg"), W, H, *f)


# ── 2. Чому послідовний діод збиває ємність (послідовне з'єднання C) ──────────
def fig_series_cap():
    W, H = 760, 360
    f = [text(W / 2, 26, "Чому низькоємнісна збірка: послідовний діод ділить ємність на лінії",
              size=15, bold=True)]

    def panel(x0, title, single, col):
        f.append(rect(x0, 50, 340, 280, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 170, 74, title, size=12.5, bold=True, color=INK))
        sig_y = 150
        gnd = 286
        sx = x0 + 40
        ex = x0 + 300
        f.append(circle(sx, sig_y, 4, fill=BG, stroke=INK, sw=1.6))
        f.append(text(sx, sig_y - 14, "лінія", size=10.5, color=MUTED))
        f.append(line(sx, sig_y, ex, sig_y, color=LINE, sw=2.0))
        f.append(circle(ex, sig_y, 4, fill=BG, stroke=INK, sw=1.6))
        cx = (sx + ex) / 2

        def cap(cy0, cy1, label, cval, ccol):
            # символ конденсатора (дві риски)
            midy = (cy0 + cy1) / 2
            out = line(cx, cy0, cx, midy - 6, color=ccol, sw=2.0)
            out += line(cx - 12, midy - 6, cx + 12, midy - 6, color=ccol, sw=2.4)
            out += line(cx - 12, midy + 6, cx + 12, midy + 6, color=ccol, sw=2.4)
            out += line(cx, midy + 6, cx, cy1, color=ccol, sw=2.0)
            out += text(cx + 26, midy, label, size=11, color=ccol, bold=True, anchor="start")
            out += text(cx + 26, midy + 15, cval, size=10, color=MUTED, anchor="start")
            return out

        if single:
            # звичайний TVS: велика ємність прямо на землю
            f.append(line(cx, sig_y, cx, sig_y + 18, color=POS, sw=2.0))
            f.append(cap(sig_y + 18, gnd - 12, "C_TVS", "≈ 30 пФ", POS))
            f.append(ground(cx, gnd - 12, color=LINE))
            b, _, _ = textbox(x0 + 170, 250, "лінія бачить усі 30 пФ —\nфронти завалено",
                              size=10.5, fill="#fbeee6", stroke=POS, color=POS, bold=True)
            f.append(b)
        else:
            # послідовний діод + TVS: дві ємності послідовно
            f.append(line(cx, sig_y, cx, sig_y + 14, color=FIELD, sw=2.0))
            f.append(cap(sig_y + 14, sig_y + 56, "C_діода", "≈ 0.5 пФ", FIELD))
            f.append(cap(sig_y + 70, gnd - 12, "C_TVS", "≈ 30 пФ", MUTED))
            f.append(ground(cx, gnd - 12, color=LINE))
            b, _, _ = textbox(x0 + 170, 250, "послідовно: ~0.5 пФ\nкерує — лінія їх майже не чує",
                              size=10.5, fill="#eef6ef", stroke=FIELD, color=INK, bold=True)
            f.append(b)

    panel(20, "Звичайний TVS на швидкій лінії", True, POS)
    panel(400, "Низькоємнісна збірка (діод послідовно)", False, FIELD)

    # формула посередині знизу
    f.append(text(W / 2, 348, "послідовно:  1/C = 1/C_діода + 1/C_TVS  →  C ≈ менша з двох",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(IMG, "tvs-array-series-cap.svg"), W, H, *f)


# ── 3. Орієнтація на платі: спільний GND упритул до полігона ─────────────────
def fig_layout():
    W, H = 760, 380
    f = [text(W / 2, 26, "Орієнтація збірки: спільний вивід GND — найкоротшим шляхом у полігон",
              size=15, bold=True)]

    def panel(x0, title, bad, col):
        f.append(rect(x0, 50, 340, 300, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 170, 74, title, size=12.5, bold=True, color=INK))

        conn_x = x0 + 26
        rail = 130
        # роз'єм-гребінка ліворуч (4 контакти)
        for i in range(4):
            cy = rail + i * 34
            f.append(rect(conn_x - 6, cy - 7, 12, 14, fill="#e9edf2", stroke=LINE, sw=1.4, rx=2))
        f.append(text(conn_x, rail - 22, "роз'єм", size=10.5, color=MUTED))

        # корпус збірки
        arr_x = x0 + 150
        arr_w, arr_h = 70, 150
        arr_y = rail - 8
        f.append(rect(arr_x, arr_y, arr_w, arr_h, fill="#eef2f7", stroke=INK, sw=1.8, rx=6))
        f.append(text(arr_x + arr_w / 2, arr_y + arr_h / 2 - 6, "ESD", size=12, color=INK, bold=True))
        f.append(text(arr_x + arr_w / 2, arr_y + arr_h / 2 + 10, "збірка", size=11, color=INK))

        # 4 канали від роз'єму у збірку
        for i in range(4):
            cy = rail + i * 34
            f.append(line(conn_x + 6, cy, arr_x, cy, color=LINE, sw=1.8))
        # далі канали йдуть праворуч до чипа
        for i in range(4):
            cy = rail + i * 34
            f.append(line(arr_x + arr_w, cy, x0 + 318, cy, color=LINE, sw=1.6))

        # полігон землі знизу
        poly_y = 318
        f.append(rect(x0 + 20, poly_y - 6, 300, 18, fill="#e7efe9", stroke=FIELD, sw=1.2, rx=3))
        f.append(text(x0 + 170, poly_y + 6, "полігон землі", size=10, color=FIELD))

        # вивід GND збірки → полігон
        gx = arr_x + arr_w / 2
        if bad:
            # довгий звивистий шлях GND
            path = "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
                gx, arr_y + arr_h, gx, arr_y + arr_h + 36, x0 + 300, arr_y + arr_h + 36, x0 + 300, poly_y - 6)
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, POS))
            f.append(text(gx + 30, arr_y + arr_h + 30, "довгий GND = L", size=10.5, color=POS, bold=True))
            b, _, _ = textbox(x0 + 170, 286, "спільний GND кружляє —\nна ньому накручується спад",
                              size=10.5, fill="#fbeee6", stroke=POS, color=POS, bold=True)
            f.append(b)
        else:
            f.append(line(gx, arr_y + arr_h, gx, poly_y - 6, color=FIELD, sw=2.8))
            f.append(text(gx + 36, (arr_y + arr_h + poly_y) / 2, "короткий GND", size=10.5, color=FIELD, bold=True))
            b, _, _ = textbox(x0 + 170, 286, "GND упритул у полігон —\nшлях розряду найкоротший",
                              size=10.5, fill="#eef6ef", stroke=FIELD, color=INK, bold=True)
            f.append(b)

    panel(20, "Погано: GND-вивід далеко від полігона", True, POS)
    panel(400, "Добре: збірка GND-виводом до полігона", False, FIELD)
    render(os.path.join(IMG, "tvs-array-layout.svg"), W, H, *f)


if __name__ == "__main__":
    fig_array_topology()
    fig_series_cap()
    fig_layout()
    print("OK: 3 figures ->", IMG)
