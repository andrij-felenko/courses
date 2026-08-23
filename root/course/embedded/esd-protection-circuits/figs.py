# -*- coding: utf-8 -*-
"""Фігури до теми «ESD-захист у схемах».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def tvs_symbol_v(cx, ty, by, color=INK, sw=2.2):
    """Вертикальний TVS-символ (зенероподібний) від ty (катод-верх) до by (анод-низ),
    поперек лінії на землю. Трикутник вістрям угору, риска-катод із 'гачками'."""
    h = 22
    midy = (ty + by) / 2
    # анодний провід знизу до трикутника
    out = line(cx, by, cx, midy + h / 2, color=color, sw=sw)
    # трикутник (анод знизу, вістря вгору)
    tri = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (cx - 11, midy + h / 2, cx + 11, midy + h / 2, cx, midy - h / 2)
    out += '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (tri, "#fdecea", color, sw)
    # риска-катод із зенерівськими «гачками»
    ky = midy - h / 2
    out += line(cx - 12, ky, cx + 12, ky, color=color, sw=sw + 0.6)
    out += line(cx - 12, ky, cx - 12, ky - 5, color=color, sw=sw)        # лівий гачок угору
    out += line(cx + 12, ky, cx + 12, ky + 5, color=color, sw=sw)        # правий гачок униз
    out += line(cx, ty, cx, ky, color=color, sw=sw)                       # катодний провід угору
    return out


def ground(cx, y, color=LINE, sw=2.0):
    out = line(cx, y, cx, y + 8, color=color, sw=sw)
    for i, w in enumerate((16, 10, 4)):
        out += line(cx - w / 2, y + 8 + i * 5, cx + w / 2, y + 8 + i * 5, color=color, sw=sw)
    return out


# ── 1. Шлях розряду й місце TVS ──────────────────────────────────────────────
def fig_esd_path():
    W, H = 760, 380
    f = [text(W / 2, 26, "Шлях ESD: палець → роз'єм → лінія → вхід чипа, і де його перехопити",
              size=15.5, bold=True)]

    rail = 150          # рівень сигнальної лінії
    # палець (рука) ліворуч із позначкою кіловольтів
    fx = 70
    f.append('<path d="M %.1f %.1f q -18 -26 6 -40 q 22 -12 34 6" fill="none" stroke="%s" stroke-width="3"/>'
             % (fx, rail, INK))
    b, _, _ = textbox(fx + 4, rail - 74, "тіло ≈ кВ", size=11.5, fill="#fbeee6", stroke=POS, color=POS, bold=True)
    f.append(b)
    # іскра (зигзаг) від пальця до контакту
    sx0, sx1 = fx + 16, 150
    zig = "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
        sx0, rail, sx0 + 18, rail - 10, sx0 + 36, rail + 8, sx0 + 60, rail - 8, sx1, rail)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (zig, POS))
    f.append(text((sx0 + sx1) / 2, rail - 26, "розряд 0.8 нс", size=10.5, color=POS, bold=True))

    # роз'єм (контакт)
    cx = 150
    f.append(rect(cx - 8, rail - 16, 16, 32, fill="#e9edf2", stroke=LINE, sw=1.8, rx=3))
    f.append(text(cx, rail + 44, "роз'єм", size=11, color=MUTED))

    # сигнальна лінія вправо до мікроконтролера
    mcu_x = 600
    f.append(line(cx + 8, rail, mcu_x, rail, color=LINE, sw=2.4))

    # TVS-діод одразу за роз'ємом, на землю
    tvs_x = 210
    gnd_y = 300
    f.append(tvs_symbol_v(tvs_x, rail, gnd_y - 18, color=FIELD, sw=2.4))
    f.append(ground(tvs_x, gnd_y - 18, color=LINE))
    b, _, _ = textbox(tvs_x + 2, rail - 52, "TVS\nвпритул", size=11, fill="#eef6ef", stroke=FIELD, color=INK, bold=True)
    f.append(b)
    # стрілка: сплеск іде в землю крізь TVS
    f.append(arrow(tvs_x - 16, rail + 16, tvs_x - 16, gnd_y - 30, color=FIELD, sw=2.6))
    f.append(text(tvs_x - 60, (rail + gnd_y) / 2, "сплеск", size=11, color=FIELD, bold=True, anchor="middle"))
    f.append(text(tvs_x - 60, (rail + gnd_y) / 2 + 16, "в землю", size=11, color=FIELD, bold=True, anchor="middle"))

    # мікроконтролер
    f.append(rect(mcu_x, rail - 40, 96, 80, fill="#e9edf2", stroke=LINE, sw=1.8, rx=6))
    f.append(text(mcu_x + 48, rail - 6, "МК", size=14, bold=True, color=INK))
    f.append(text(mcu_x + 48, rail + 14, "тонкий", size=10, color=MUTED))
    f.append(text(mcu_x + 48, rail + 28, "оксид входу", size=10, color=MUTED))
    f.append(line(mcu_x + 48, rail + 40, mcu_x + 48, gnd_y - 18, color=LINE, sw=1.6))
    f.append(ground(mcu_x + 48, gnd_y - 18, color=LINE))

    # підпис: що лишається на вході
    b, _, _ = textbox(430, rail - 40, "на лінії лишається\nлише напруга обмеження",
                      size=11, fill=BG, stroke=FIELD, color=INK)
    f.append(b)

    # суцільний полігон землі знизу
    f.append(line(tvs_x, gnd_y + 22, mcu_x + 48, gnd_y + 22, color=MUTED, sw=1.4, dash="3,4"))
    f.append(text((tvs_x + mcu_x) / 2, gnd_y + 40, "суцільний полігон землі", size=10, color=MUTED))

    render(os.path.join(IMG, "esd-path.svg"), W, H, *f)


# ── 2. Вольт-амперна крива TVS: три напруги ──────────────────────────────────
def fig_tvs_vi():
    W, H = 720, 420
    f = [text(W / 2, 26, "Три напруги TVS-діода: робоча, пробою й обмеження",
              size=16, bold=True)]

    ox, oy = 110, 340          # початок осей (нуль)
    ax_w, ax_h = 540, 260
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))     # вісь напруги
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))     # вісь струму
    f.append(text(ox + ax_w / 2, oy + 42, "зворотна напруга на діоді →", size=12, color=INK))
    f.append(text(ox - 74, oy - ax_h / 2, "струм", size=12, color=INK))
    f.append(text(ox - 74, oy - ax_h / 2 + 16, "через", size=11, color=MUTED))
    f.append(text(ox - 74, oy - ax_h / 2 + 30, "діод", size=11, color=MUTED))

    # три характерні напруги по осі X (умовні позиції)
    x_rwm = ox + 0.42 * ax_w
    x_br = ox + 0.52 * ax_w
    x_c = ox + 0.82 * ax_w

    # крива: плоске дно (витік) до V_BR, далі крутий злом до (V_C, пік струму)
    y0 = oy - 6                       # майже нуль (витік)
    y_knee = oy - 0.10 * ax_h         # де починає відчутно текти
    y_peak = oy - 0.92 * ax_h         # піковий струм розряду
    pts = "M %.1f %.1f L %.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f" % (
        ox, y0, x_rwm, y0 - 4, x_br, y_knee, x_br + 18, oy - 0.55 * ax_h, x_c, y_peak)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts, FIELD))

    # вертикалі-маркери трьох напруг
    def vmark(x, label, sub, col, ytop):
        f.append(line(x, oy, x, ytop, color=col, sw=1.4, dash="4,4"))
        f.append(line(x, oy, x, oy + 6, color=col, sw=1.6))
        f.append(text(x, oy + 20, label, size=12, color=col, bold=True))
        f.append(text(x, oy + 36, sub, size=10, color=MUTED))

    vmark(x_rwm, "V_RWM", "робоча", NEG, y0 - 30)
    vmark(x_br, "V_BR", "пробою", "#e08a3c", y_knee - 6)
    vmark(x_c, "V_C", "обмеження", POS, y_peak)

    # горизонталь піку струму до V_C
    f.append(line(ox, y_peak, x_c, y_peak, color=POS, sw=1.2, dash="3,4"))
    f.append(text(ox + 6, y_peak - 8, "піковий струм розряду", size=10.5, color=POS, anchor="start"))

    # зона «прозорий» і зона «обмежує»
    b, _, _ = textbox(ox + 0.20 * ax_w, oy - 0.30 * ax_h, "діод закритий:\nлінія в нормі",
                      size=10.5, fill=BG, stroke=NEG, color=INK)
    f.append(b)

    # гранична напруга входу — праворуч від V_C (запас)
    x_lim = ox + 0.95 * ax_w
    f.append(line(x_lim, oy, x_lim, oy - ax_h, color=POS, sw=1.6, dash="2,3"))
    f.append(text(x_lim, oy - ax_h - 6, "гранична", size=10, color=POS, bold=True))
    f.append(text(x_lim, oy - ax_h + 8, "напруга входу", size=10, color=POS))
    # дужка-запас між V_C і границею
    f.append(line(x_c, oy - ax_h - 14, x_lim, oy - ax_h - 14, color=INK, sw=1.2))
    f.append(text((x_c + x_lim) / 2, oy - ax_h - 20, "запас", size=10, color=INK, bold=True))

    render(os.path.join(IMG, "tvs-vi.svg"), W, H, *f)


# ── 3. Розташування TVS: далеко проти впритул ────────────────────────────────
def fig_placement():
    W, H = 760, 380
    f = [text(W / 2, 26, "Те саме TVS, різне місце: довга доріжка накручує вольти повз захист",
              size=15, bold=True)]

    def panel(x0, title, far, ok):
        col = POS if far else FIELD
        f.append(rect(x0, 50, 340, 300, fill=BG, stroke=col, sw=2, rx=12))
        f.append(text(x0 + 170, 74, title, size=13, bold=True, color=INK))

        rail = 150
        gnd = 296
        cxr = x0 + 36          # роз'єм
        mcu = x0 + 280         # вхід чипа
        # роз'єм
        f.append(rect(cxr - 7, rail - 14, 14, 28, fill="#e9edf2", stroke=LINE, sw=1.6, rx=3))
        f.append(text(cxr, rail + 40, "роз'єм", size=10, color=MUTED))
        # сигнальна лінія
        f.append(line(cxr + 7, rail, mcu, rail, color=LINE, sw=2.2))
        # вхід чипа
        f.append(rect(mcu, rail - 22, 40, 44, fill="#e9edf2", stroke=LINE, sw=1.6, rx=4))
        f.append(text(mcu + 20, rail + 4, "МК", size=12, bold=True, color=INK))
        f.append(line(mcu + 20, rail + 22, mcu + 20, gnd - 16, color=LINE, sw=1.5))
        f.append(ground(mcu + 20, gnd - 16, color=LINE))

        if far:
            # TVS далеко — біля чипа; довгий відрізок доріжки роз'єм→TVS = індуктивність
            tx = x0 + 220
            # позначка індуктивності на довгій доріжці (котушка-петельки)
            ly = rail
            coil = "M %.1f %.1f" % (cxr + 16, ly)
            for k in range(4):
                bx = cxr + 24 + k * 20
                coil += " q 10 -14 20 0"
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (coil, POS))
            f.append(text((cxr + tx) / 2, ly - 22, "довга доріжка = L", size=10.5, color=POS, bold=True))
        else:
            tx = x0 + 70         # TVS упритул до роз'єму

        # сам TVS
        f.append(tvs_symbol_v(tx, rail, gnd - 16, color=col, sw=2.2))
        f.append(ground(tx, gnd - 16, color=LINE))
        f.append(text(tx, rail - 30, "TVS", size=11, color=INK, bold=True))

        # що бачить вхід
        if far:
            b, _, _ = textbox(x0 + 170, 252, "вхід бачить V_C + сотні В\nз індуктивності — пробій",
                              size=10.5, fill="#fbeee6", stroke=POS, color=POS, bold=True)
        else:
            b, _, _ = textbox(x0 + 170, 252, "шлях короткий, L мала —\nвхід бачить майже чисту V_C",
                              size=10.5, fill="#eef6ef", stroke=FIELD, color=INK, bold=True)
        f.append(b)

    panel(20, "Погано: TVS далеко від роз'єму", True, False)
    panel(400, "Добре: TVS упритул до роз'єму", False, True)
    render(os.path.join(IMG, "tvs-placement.svg"), W, H, *f)


if __name__ == "__main__":
    fig_esd_path()
    fig_tvs_vi()
    fig_placement()
    print("OK: 3 figures ->", IMG)
