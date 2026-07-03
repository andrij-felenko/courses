# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: схема сенсора десатурації ──────────────────────────────────────
def fig_sense():
    W, H = 760, 430
    els = []

    # Драйвер (лівий блок)
    els.append(fitbox(30, 150, 150, 130, "Драйвер\nзатвора",
                      size=15, bold=True, fill="#eef2f7"))
    # вивід DESAT назовні праворуч
    els.append(text(105, 300, "вивід DESAT", size=12, color=MUTED))

    # Внутрішнє джерело струму 0.5 мА (у драйвері, символічно біля виводу)
    src_x = 235
    els.append(circle(src_x, 120, 22, fill="#fff8e1", stroke=POS, sw=2))
    els.append(text(src_x, 116, "0.5", size=12, color=POS, bold=True))
    els.append(text(src_x, 131, "мА", size=11, color=POS))
    els.append(text(src_x, 88, "заряд", size=11, color=MUTED))
    els.append(arrow(src_x, 142, src_x, 205, color=POS, sw=2))

    # Компаратор проти 9 В (у драйвері)
    comp = fitbox(30, 300, 150, 70, "Компаратор\n> 9 В  → фолт",
                  size=13, bold=True, fill="#fdecea", stroke=POS)
    els.append(comp)

    # Вузол DESAT (де сходяться струм, кондер, діод, компаратор)
    node_x, node_y = src_x, 235
    els.append(circle(node_x, node_y, 4, fill=INK, stroke=INK))
    # відгалуження вузол → компаратор: горизонталлю ліворуч, тоді вниз у блок (зі стрілкою на вході)
    tap_x = 200
    els.append(line(node_x, node_y, tap_x, node_y, color=INK, sw=1.4))
    els.append(line(tap_x, node_y, tap_x, 300, color=INK, sw=1.4))
    els.append(arrow(tap_x, 300, 180, 300, color=INK, sw=1.4))
    els.append(text(tap_x - 6, 224, "порівняти", size=10, color=MUTED, anchor="end"))

    # Конденсатор C_DESAT (вниз від вузла на землю)
    cap_y = 300
    els.append(line(node_x, node_y, node_x, cap_y, color=INK, sw=1.4))
    # обкладки
    els.append(line(node_x - 16, cap_y, node_x + 16, cap_y, color=INK, sw=2.4))
    els.append(line(node_x - 16, cap_y + 8, node_x + 16, cap_y + 8, color=INK, sw=2.4))
    els.append(line(node_x, cap_y + 8, node_x, cap_y + 30, color=INK, sw=1.4))
    # земля
    gy = cap_y + 30
    els.append(line(node_x - 14, gy, node_x + 14, gy, color=INK, sw=2))
    els.append(line(node_x - 9, gy + 5, node_x + 9, gy + 5, color=INK, sw=2))
    els.append(line(node_x - 4, gy + 10, node_x + 4, gy + 10, color=INK, sw=2))
    els.append(text(node_x + 52, cap_y + 4, "C_DESAT", size=12, color=NEG, bold=True))
    els.append(text(node_x + 52, cap_y + 20, "(вікно)", size=11, color=MUTED))

    # Високовольтний блокувальний діод (від вузла праворуч до колектора)
    d_y = 235
    d_x = 430
    els.append(line(node_x, d_y, d_x - 22, d_y, color=INK, sw=1.6))
    # трикутник діода (анод ліворуч → катод праворуч)
    els.append('<path d="M%d %d L%d %d L%d %d z" fill="#eef2f7" stroke="%s" stroke-width="1.6"/>'
               % (d_x - 22, d_y - 12, d_x - 22, d_y + 12, d_x, d_y, LINE))
    els.append(line(d_x, d_y - 12, d_x, d_y + 12, color=INK, sw=2.4))  # катодна риска
    els.append(text(d_x - 10, d_y - 24, "діод HV", size=12, color=INK, bold=True))
    els.append(line(d_x, d_y, 560, d_y, color=INK, sw=1.6))

    # Силовий ключ IGBT/MOSFET (правий блок), його колектор = верх
    kx, ky, kw, kh = 560, 150, 140, 150
    els.append(rect(kx, ky, kw, kh, fill="#eef2f7", stroke=LINE, sw=1.8))
    els.append(text(kx + kw / 2, ky + 55, "силовий", size=14, bold=True))
    els.append(text(kx + kw / 2, ky + 75, "ключ", size=14, bold=True))
    els.append(text(kx + kw / 2, ky + 100, "V_CE", size=13, color=POS, italic=True))
    # колектор (верхній вузол ключа) — точка приєднання діода
    els.append(circle(kx + 10, d_y, 4, fill=INK, stroke=INK))
    els.append(text(kx + 34, d_y - 12, "колектор", size=11, color=MUTED))
    # шина зверху
    els.append(line(kx + kw / 2, ky, kx + kw / 2, 60, color=POS, sw=2))
    els.append(text(kx + kw / 2, 50, "+ шина", size=12, color=POS, bold=True))
    # емітер вниз
    els.append(line(kx + kw / 2, ky + kh, kx + kw / 2, 350, color=INK, sw=1.6))
    egy = 355
    els.append(line(kx + kw / 2 - 14, egy, kx + kw / 2 + 14, egy, color=INK, sw=2))
    els.append(line(kx + kw / 2 - 9, egy + 5, kx + kw / 2 + 9, egy + 5, color=INK, sw=2))
    els.append(line(kx + kw / 2 - 4, egy + 10, kx + kw / 2 + 4, egy + 10, color=INK, sw=2))

    render(os.path.join(IMG, 'desat-sense.svg'), W, H, *els)


# ── Фігура 2: осцилограма V_CE у часі ────────────────────────────────────────
def fig_waveform():
    W, H = 760, 430
    els = []

    ox, oy = 90, 340        # початок осей
    ax_w, ax_h = 600, 260
    # осі
    els.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    els.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    els.append(text(ox - 18, oy - ax_h + 6, "V_CE", size=13, bold=True, italic=True))
    els.append(text(ox + ax_w - 10, oy + 22, "час", size=13))

    # рівень порога 9 В
    thr_y = oy - 175
    els.append(line(ox, thr_y, ox + ax_w, thr_y, color=POS, sw=1.4, dash="6 5"))
    els.append(text(ox + ax_w + 2, thr_y + 4, "9 В", size=12, color=POS, bold=True))
    els.append(text(ox + ax_w - 118, thr_y - 8, "поріг фолту", size=11, color=POS))

    # рівень насичення ~2 В
    sat_y = oy - 34
    els.append(line(ox, sat_y, ox + ax_w, sat_y, color=MUTED, sw=1.0, dash="3 4"))
    els.append(text(ox + ax_w + 2, sat_y + 4, "~2 В", size=11, color=MUTED))

    # вертикаль кінця бланкування
    t_blank = ox + 150
    els.append(line(t_blank, oy, t_blank, oy - ax_h + 20, color=NEG, sw=1.2, dash="5 5"))
    els.append(text(t_blank, oy - ax_h + 14, "кінець бланку", size=11, color=NEG, anchor="middle"))

    # заштрихована зона бланкування (сенсор сліпий)
    els.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#eaf0fd" opacity="0.55"/>'
               % (ox + 1, oy - ax_h + 20, t_blank - ox - 1, ax_h - 20))
    els.append(text((ox + t_blank) / 2, oy - ax_h + 42, "сенсор", size=11, color=NEG, anchor="middle"))
    els.append(text((ox + t_blank) / 2, oy - ax_h + 56, "сліпий", size=11, color=NEG, anchor="middle"))

    # Крива НОРМА (зелена): високий V_CE, потім за бланк падає до насичення й лишається
    n = []
    n.append((ox, oy - ax_h + 30))                 # старт: ще закритий, V=шина висока
    n.append((ox + 40, oy - ax_h + 30))
    n.append((ox + 95, sat_y))                      # спадає в насичення під час вмикання
    n.append((ox + ax_w, sat_y))                    # лишається низьким
    pts = " ".join("%.0f,%.0f" % p for p in n)
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, FIELD))
    els.append(text(ox + 300, sat_y - 12, "норма: лишається в насиченні", size=12, color=FIELD, bold=True))

    # Крива КЗ (червона): за бланк V_CE не падає, а лізе вгору крізь поріг
    s = []
    s.append((ox, oy - ax_h + 30))
    s.append((ox + 40, oy - ax_h + 30))
    s.append((ox + 95, oy - 120))                   # частково падає...
    s.append((t_blank, oy - 150))                   # ...але лишається високим під час КЗ
    s.append((ox + 300, thr_y - 6))                 # лізе далі вгору
    s.append((ox + 340, thr_y - 6))                 # перетнув поріг
    pts2 = " ".join("%.0f,%.0f" % p for p in s)
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts2, POS))
    els.append(text(ox + 175, oy - 138, "КЗ: V_CE лізе вгору", size=12, color=POS, bold=True))

    # точка перетину порога → фолт
    cross_x = ox + 328
    els.append(circle(cross_x, thr_y, 6, fill="#fff", stroke=POS, sw=2.4))
    els.append(arrow(cross_x, thr_y - 6, cross_x + 60, thr_y - 60, color=INK, sw=1.6))
    els.append(fitbox(cross_x + 40, thr_y - 96, 190, 46,
                      "перетнув 9 В → фолт → м'яке вимкнення", size=11, bold=True,
                      fill="#fdecea", stroke=POS))

    # бюджет часу до руйнування
    els.append(line(t_blank, oy + 26, ox + 470, oy + 26, color=MUTED, sw=1.2))
    els.append(line(t_blank, oy + 21, t_blank, oy + 31, color=MUTED, sw=1.2))
    els.append(line(ox + 470, oy + 21, ox + 470, oy + 31, color=MUTED, sw=1.2))
    els.append(text((t_blank + ox + 470) / 2, oy + 42, "весь захист має вкластися в ~10 мкс витримки КЗ",
                    size=11, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'desat-waveform.svg'), W, H, *els)


# ── Фігура 3: чому V_CE росте — вихідна характеристика ───────────────────────
def fig_curve():
    W, H = 760, 470
    els = []

    ox, oy = 100, 380
    ax_w, ax_h = 590, 300
    els.append(arrow(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    els.append(arrow(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    els.append(text(ox - 22, oy - ax_h + 4, "I_C", size=13, bold=True, italic=True))
    els.append(text(ox + ax_w - 4, oy + 26, "V_CE", size=13, bold=True, italic=True))

    knee_x = ox + 150
    plateau_y = 220

    # Вихідна крива IGBT при робочому V_GE: крутий підйом у насиченні, коліно, пологе плато
    pts = ("M %.0f %.0f Q %.0f %.0f %.0f %.0f L %.0f %.0f" % (
        ox, oy,
        ox + 40, oy - plateau_y * 0.80,
        knee_x, oy - plateau_y * 0.98,
        ox + ax_w - 20, oy - plateau_y))
    els.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts, INK))
    els.append(text(ox + ax_w - 26, oy - plateau_y - 12, "крива при робочому V_GE",
                    size=11, color=INK, anchor="end"))

    # межа «коліна» — вертикаль
    els.append(line(knee_x, oy, knee_x, oy - ax_h + 66, color=MUTED, sw=1.0, dash="4 5"))
    els.append(text(knee_x, oy - ax_h + 58, "коліно", size=11, color=MUTED, anchor="middle"))

    # підписи зон (обидва — під кривою, подалі від ліній і одне від одного)
    els.append(fitbox(ox + 10, oy - 92, 132, 60,
                      "НАСИЧЕННЯ\nмалий V_CE\nздоровий ключ", size=11, bold=True,
                      fill="#eafaf1", stroke=FIELD))
    els.append(fitbox(knee_x + 90, oy - 118, 210, 62,
                      "АКТИВНА зона\nключ обмежує струм —\nV_CE зростає", size=11, bold=True,
                      fill="#fdecea", stroke=POS))

    # Робоча точка НОРМА (лівий низ кривої, малий V_CE) — дроплайн лише вниз
    nx, ny = ox + 44, oy - 112
    els.append(circle(nx, ny, 6, fill="#fff", stroke=FIELD, sw=2.6))
    els.append(text(nx - 20, ny - 6, "норма", size=11, color=FIELD, bold=True, anchor="end"))
    els.append(line(nx, ny + 8, nx, oy - 2, color=FIELD, sw=1.0, dash="3 4"))
    els.append(text(nx, oy + 18, "~2 В", size=10, color=FIELD, anchor="middle"))

    # Робоча точка КЗ (плато, високий струм, великий V_CE) — дроплайн лише вниз
    fx, fy = ox + 430, oy - plateau_y
    els.append(circle(fx, fy, 6, fill="#fff", stroke=POS, sw=2.6))
    els.append(text(fx + 12, fy - 8, "КЗ", size=12, color=POS, bold=True, anchor="start"))
    els.append(line(fx, fy + 8, fx, oy - 2, color=POS, sw=1.0, dash="3 4"))
    els.append(text(fx, oy + 18, "десятки В", size=10, color=POS, anchor="middle"))
    # маркер рівня струму 4–8× ліворуч від осі (короткий, не через увесь графік)
    els.append(text(ox - 12, fy + 4, "4–8×", size=10, color=POS, anchor="end"))
    els.append(line(ox - 4, fy, ox + 4, fy, color=POS, sw=1.4))

    render(os.path.join(IMG, 'desat-curve.svg'), W, H, *els)


if __name__ == '__main__':
    fig_sense()
    fig_waveform()
    fig_curve()
    print("figures written to", IMG)
