# -*- coding: utf-8 -*-
"""Фігури до теми «DRAM: транзистор і конденсатор» та її математичної вставки.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── допоміжне: маленький конденсатор (дві пластини) ─────────────────────────
def cap(cx, cy, gap=8, plate=22, sw=2.4, color=INK):
    return (line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, color=color, sw=sw) +
            line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, color=color, sw=sw))


def mosfet(cx, cy, color=INK):
    """Схематичний транзистор-ключ: вертикальний канал + затвор збоку."""
    s = []
    s.append(line(cx, cy - 22, cx, cy + 22, color=color, sw=2.4))          # канал
    s.append(line(cx - 16, cy, cx - 4, cy, color=color, sw=2.2))           # затвор
    s.append(line(cx - 4, cy - 12, cx - 4, cy + 12, color=color, sw=2.2))  # пластина затвора
    return "".join(s)


# ════════════════════════════════════════════════════════════════════════════
# СТАТТЯ
# ════════════════════════════════════════════════════════════════════════════

# ── 1. SRAM (6 транзисторів) проти DRAM (1 транзистор + конденсатор) ─────────
def fig_cell_compare():
    W, H = 860, 470
    f = [text(W / 2, 30, "Один біт: шість транзисторів проти «транзистор + конденсатор»",
              size=17, bold=True)]

    # ── ліва панель: SRAM ──
    lx, ly, lw, lh = 40, 56, 380, 340
    f.append(rect(lx, ly, lw, lh, fill="#fbfbfd", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(lx + lw / 2, ly + 30, "SRAM — біт на засувці", size=15, bold=True, color=NEG))

    # два інвертори як два трикутники «носик до носика»
    def inverter(x, y, flip=False):
        d = -1 if flip else 1
        p1 = (x, y - 22); p2 = (x, y + 22); p3 = (x + d * 46, y)
        tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" stroke-width="2"/>'
               % (p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], "#eef2fb", NEG))
        bub = circle(x + d * 52, y, 5, fill=BG, stroke=NEG, sw=2)
        return tri + bub

    iy = ly + 150
    f.append(inverter(lx + 120, iy, flip=False))
    f.append(inverter(lx + 260, iy, flip=True))
    # кільце зворотного зв'язку
    f.append(line(lx + 172, iy, lx + 200, iy, color=NEG, sw=2))
    f.append(line(lx + 200, iy - 40, lx + 200, iy + 40, color=NEG, sw=2))
    f.append(line(lx + 208, iy, lx + 180, iy, color=NEG, sw=2))
    f.append(text(lx + lw / 2, iy - 64,
                  "два інвертори тримають одне одного", size=12, color=MUTED))
    f.append(text(lx + lw / 2, iy + 78, "+ 2 транзистори на доступ", size=12, color=MUTED))

    box, _, _ = textbox(lx + lw / 2, ly + lh - 46, "6 транзисторів · біт стоїть сам",
                        size=13, bold=True, fill="#eef2fb", stroke=NEG)
    f.append(box)

    # ── права панель: DRAM ──
    rx, ry, rw, rh = 440, 56, 380, 340
    f.append(rect(rx, ry, rw, rh, fill="#fbfdfb", stroke=MUTED, sw=1.6, rx=10))
    f.append(text(rx + rw / 2, ry + 30, "DRAM — біт як заряд", size=15, bold=True, color=FIELD))

    # лінія слова згори, розрядна лінія зліва
    wl_y = ry + 96
    bl_x = rx + 90
    node_x = rx + 200
    f.append(line(rx + 40, wl_y, rx + rw - 40, wl_y, color=MUTED, sw=1.6))
    f.append(text(rx + rw - 40, wl_y - 10, "лінія слова", size=11, color=MUTED, anchor="end"))
    f.append(line(bl_x, ry + 70, bl_x, ry + rh - 60, color=MUTED, sw=1.6))
    f.append(text(bl_x, ry + rh - 44, "розрядна", size=11, color=MUTED))

    # транзистор-ключ між розрядною лінією і вузлом
    f.append(mosfet(node_x - 40, wl_y + 70, color=INK))
    f.append(line(bl_x, wl_y + 70, node_x - 56, wl_y + 70, color=INK, sw=2))   # від розрядної до стоку
    f.append(line(node_x - 56, wl_y, node_x - 56, wl_y + 48, color=INK, sw=2)) # затвор до лінії слова
    f.append(line(node_x - 40, wl_y + 92, node_x, wl_y + 92, color=INK, sw=2)) # до вузла
    f.append(line(node_x, wl_y + 70, node_x, wl_y + 110, color=INK, sw=2))

    # конденсатор зберігання
    f.append(cap(node_x, wl_y + 122, gap=9, plate=30, color=FIELD))
    f.append(line(node_x, wl_y + 70, node_x, wl_y + 116, color=INK, sw=2))
    f.append(line(node_x, wl_y + 130, node_x, wl_y + 150, color=INK, sw=2))
    # земля
    for i, wgnd in enumerate((22, 14, 6)):
        f.append(line(node_x - wgnd / 2, wl_y + 150 + i * 5, node_x + wgnd / 2, wl_y + 150 + i * 5,
                      color=INK, sw=2))
    f.append(text(node_x + 26, wl_y + 122, "Cₛ", size=14, color=FIELD, anchor="start", italic=True))
    f.append(text(node_x - 70, wl_y + 56, "1 ключ", size=11, color=MUTED, anchor="middle"))

    box, _, _ = textbox(rx + rw / 2, ry + rh - 46, "1 транзистор + 1 конденсатор · заряд тече",
                        size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    f.append(box)

    f.append(text(W / 2, H - 14,
                  "Менше деталей на біт → більше бітів на пластині → нижча ціна за мегабайт. Платня: конденсатор тече.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "cell-compare.svg"), W, H, *f)


# ── 2. Заряд тече по експоненті; регенерація поновлює його вчасно ───────────
def fig_leak_refresh():
    W, H = 860, 440
    f = [text(W / 2, 30, "Заряд комірки спадає — регенерація встигає його поновити",
              size=17, bold=True)]

    # осі
    ox, oy = 90, 360
    axw, axh = 700, 250
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))          # вісь часу
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.8))          # вісь напруги
    f.append(text(ox + axw, oy + 24, "час", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy - axh + 6, "заряд", size=12, color=MUTED, anchor="end"))

    top = oy - axh + 26          # рівень «повна 1»
    thr = oy - 70                # поріг читання
    f.append(line(ox, top, ox + axw, top, color=MUTED, sw=1.0, dash="3,4"))
    f.append(text(ox + axw, top - 8, "повна «1»", size=11, color=MUTED, anchor="end"))
    f.append(line(ox, thr, ox + axw, thr, color=NEG, sw=1.4, dash="6,4"))
    f.append(text(ox + 6, thr - 8, "поріг читання", size=11, color=NEG, anchor="start"))

    V0 = top
    span = oy - top
    # червоний: без поновлення — експонента вниз
    tau = 210.0
    pts = []
    for i in range(0, axw + 1, 6):
        v = oy - span * math.exp(-i / tau)
        pts.append("%.1f,%.1f" % (ox + i, v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7,5"/>'
             % (" ".join(pts), POS))
    f.append(text(ox + 350, oy - 36, "без поновлення — біт згублено", size=12, color=POS))

    # зелена «пилка»: розряд до моменту регенерації, потім стрибок угору
    period = 150
    seg = []
    x = 0
    while x < axw:
        # спад від повного рівня протягом одного періоду
        sub = []
        for i in range(0, period + 1, 5):
            if x + i > axw:
                break
            v = oy - span * math.exp(-i / tau)
            sub.append("%.1f,%.1f" % (ox + x + i, v))
        seg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                   % (" ".join(sub), FIELD))
        # вертикальний стрибок назад до повного
        if x + period < axw:
            xx = ox + x + period
            vend = oy - span * math.exp(-period / tau)
            seg.append(line(xx, vend, xx, top, color=FIELD, sw=2.6))
        x += period
    f.extend(seg)
    f.append(text(ox + 120, top + 20, "регенерація: читання → запис назад",
                  size=12, color=FIELD, anchor="start"))

    f.append(text(W / 2, H - 14,
                  "Поки поновлення встигає (типово раз на ~64 мс на весь масив), біти живі.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "leak-refresh.svg"), W, H, *f)


# ── 3. Масив: лінія слова активує ряд → буфер-підсилювач → вибір стовпця ────
def fig_array_rowcol():
    W, H = 880, 500
    f = [text(W / 2, 30, "Звернення до комірки: спершу ряд (RAS), потім стовпець (CAS)",
              size=17, bold=True)]

    # решітка комірок
    gx, gy = 150, 80
    n = 5
    cellw, cellh = 90, 56
    active_row = 1
    for r in range(n):
        for c in range(n):
            x = gx + c * cellw
            y = gy + r * cellh
            on = (r == active_row)
            fill = "#eafaf0" if on else "#fafafa"
            stroke = FIELD if on else "#cccccc"
            f.append(rect(x + 6, y + 6, cellw - 12, cellh - 12, fill=fill, stroke=stroke,
                          sw=1.8 if on else 1.0, rx=4))
            # крапка-комірка
            f.append(circle(x + cellw / 2, y + cellh / 2, 4,
                            fill=FIELD if on else MUTED, stroke="none", sw=0))

    grid_w = n * cellw
    grid_h = n * cellh

    # лінія слова активного ряду
    wl_y = gy + active_row * cellh + cellh / 2
    f.append(line(gx - 70, wl_y, gx + grid_w, wl_y, color=FIELD, sw=2.6))
    f.append(text(gx - 74, wl_y - 8, "лінія слова", size=12, color=FIELD, anchor="end"))
    f.append(text(gx - 74, wl_y + 14, "(RAS → ряд)", size=11, color=MUTED, anchor="end"))

    # буфер-підсилювач знизу
    by = gy + grid_h + 24
    f.append(rect(gx, by, grid_w, 40, fill="#fff7e6", stroke="#d98c00", sw=2, rx=6))
    f.append(text(gx + grid_w / 2, by + 25, "буфер-підсилювач (увесь ряд)", size=13, bold=True, color="#a86a00"))
    # розрядні лінії вниз від кожного стовпця
    for c in range(n):
        xx = gx + c * cellw + cellw / 2
        f.append(line(xx, gy, xx, by, color="#d9d9d9", sw=1.0))
        f.append(arrow(xx, wl_y + 6, xx, by - 4, color="#bbbbbb", sw=1.2))

    # вибір стовпця (CAS)
    sel_c = 3
    sx = gx + sel_c * cellw + cellw / 2
    f.append(line(sx, by + 40, sx, by + 86, color=NEG, sw=2.4))
    f.append(arrow(sx, by + 50, sx, by + 86, color=NEG, sw=2.4))
    f.append(text(sx + 10, by + 80, "CAS → стовпець = байт", size=12, color=NEG, anchor="start"))

    # напис про регенерацію
    f.append(text(W / 2, H - 36,
                  "Запис ряду назад заразом ПОНОВЛЮЄ його заряд → регенерація йде по рядах.",
                  size=12.5, bold=True, color=INK))
    f.append(text(W / 2, H - 14,
                  "Адресу шлють у два прийоми тими самими ніжками — ліній удвічі менше.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "array-rowcol.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# МАТЕМАТИЧНА ВСТАВКА
# ════════════════════════════════════════════════════════════════════════════

# ── 4. Комірка 1T1C та її подання як RC-кола, що розряджається ─────────────
def fig_cell_rc():
    W, H = 860, 480
    f = [text(W / 2, 30, "Комірка 1T1C — це конденсатор за неідеальним ключем",
              size=17, bold=True)]

    # ── ліворуч: фізична комірка ──
    lx, ly, lw, lh = 40, 56, 380, 300
    f.append(rect(lx, ly, lw, lh, fill="#fbfbfd", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(lx + lw / 2, ly + 28, "фізична комірка", size=14, bold=True))

    bl_x = lx + 70
    node_x = lx + 210
    wl_y = ly + 80
    f.append(line(bl_x, ly + 56, bl_x, ly + lh - 30, color=MUTED, sw=1.6))
    f.append(text(bl_x, ly + lh - 14, "розрядна лінія", size=11, color=MUTED))
    f.append(line(lx + 40, wl_y, lx + lw - 30, wl_y, color=MUTED, sw=1.6))
    f.append(text(lx + lw - 30, wl_y - 8, "лінія слова", size=11, color=MUTED, anchor="end"))

    f.append(mosfet(node_x - 40, wl_y + 60, color=INK))
    f.append(line(bl_x, wl_y + 60, node_x - 56, wl_y + 60, color=INK, sw=2))
    f.append(line(node_x - 56, wl_y, node_x - 56, wl_y + 38, color=INK, sw=2))
    f.append(line(node_x - 40, wl_y + 82, node_x, wl_y + 82, color=INK, sw=2))
    f.append(line(node_x, wl_y + 60, node_x, wl_y + 100, color=INK, sw=2))
    f.append(cap(node_x, wl_y + 112, gap=9, plate=30, color=FIELD))
    f.append(line(node_x, wl_y + 120, node_x, wl_y + 140, color=INK, sw=2))
    for i, wgnd in enumerate((22, 14, 6)):
        f.append(line(node_x - wgnd / 2, wl_y + 140 + i * 5, node_x + wgnd / 2, wl_y + 140 + i * 5,
                      color=INK, sw=2))
    f.append(text(node_x + 26, wl_y + 112, "Cₛ ≈ 25 фФ", size=12, color=FIELD, anchor="start"))
    f.append(text(node_x + 26, wl_y + 60, "вузол: Q = Cₛ·V", size=11, color=MUTED, anchor="start"))

    # ── праворуч: RC-подання ──
    rx, ry, rw, rh = 460, 56, 360, 300
    f.append(rect(rx, ry, rw, rh, fill="#fbfdfb", stroke=MUTED, sw=1.4, rx=10))
    f.append(text(rx + rw / 2, ry + 28, "те саме як RC-коло", size=14, bold=True))

    nx = rx + 130
    topy = ry + 80
    boty = ry + rh - 60
    # верхня шина
    f.append(line(nx, topy, rx + rw - 70, topy, color=INK, sw=2))
    f.append(line(nx, topy, nx, topy + 20, color=INK, sw=2))
    # конденсатор Cs (ліва вітка)
    f.append(cap(nx, topy + 32, gap=9, plate=30, color=FIELD))
    f.append(line(nx, topy + 40, nx, boty, color=INK, sw=2))
    f.append(text(nx - 12, topy + 32, "Cₛ", size=13, color=FIELD, anchor="end", italic=True))
    # резистор витоку (права вітка) — зигзаг
    rrx = rx + rw - 70
    f.append(line(rrx, topy, rrx, topy + 16, color=INK, sw=2))
    zig = "M%.1f %.1f" % (rrx, topy + 16)
    yy = topy + 16
    for k in range(6):
        yy += 10
        zig += " L%.1f %.1f" % (rrx + (8 if k % 2 == 0 else -8), yy)
    zig += " L%.1f %.1f" % (rrx, yy + 8)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (zig, POS))
    f.append(line(rrx, yy + 8, rrx, boty, color=INK, sw=2))
    f.append(text(rrx + 10, topy + 50, "R_leak", size=12, color=POS, anchor="start"))
    f.append(text(rrx + 10, topy + 66, "≈ 10¹²–10¹³ Ω", size=10.5, color=MUTED, anchor="start"))
    # нижня шина + земля
    f.append(line(nx, boty, rrx, boty, color=INK, sw=2))
    gx2 = (nx + rrx) / 2
    f.append(line(gx2, boty, gx2, boty + 14, color=INK, sw=2))
    for i, wgnd in enumerate((22, 14, 6)):
        f.append(line(gx2 - wgnd / 2, boty + 14 + i * 5, gx2 + wgnd / 2, boty + 14 + i * 5,
                      color=INK, sw=2))

    # три шляхи витоку (підпис унизу)
    f.append(text(W / 2, H - 38,
                  "Три шляхи витоку: підпороговий струм ключа · витік p–n-переходу · витік діелектрика.",
                  size=12.5, color=INK))
    f.append(text(W / 2, H - 16,
                  "Їхня сума — той «нещільний вимикач», крізь який Cₛ повільно розряджається.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "cell-rc.svg"), W, H, *f)


# ── 5. Експоненційний спад V(t) та вікно до регенерації ────────────────────
def fig_decay_window():
    W, H = 860, 470
    f = [text(W / 2, 30, "Напруга на комірці тане по експоненті: V(t) = V₀·e^(−t/τ)",
              size=17, bold=True)]

    ox, oy = 90, 370
    axw, axh = 700, 270
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw, oy + 24, "час t", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 12, oy - axh + 6, "V", size=13, color=MUTED, anchor="end", )) if False else None
    f.append(text(ox - 14, oy - axh + 10, "V", size=13, color=INK, anchor="end"))

    top = oy - axh + 30
    span = oy - top
    tau_px = 230.0

    # рівень V0
    f.append(line(ox, top, ox + axw, top, color=MUTED, sw=1.0, dash="3,4"))
    f.append(text(ox - 8, top + 4, "V₀", size=12, color=INK, anchor="end"))

    # рівень 37 % (за τ)
    v37 = oy - span * math.exp(-1.0)
    f.append(line(ox, v37, ox + tau_px, v37, color=MUTED, sw=1.0, dash="2,4"))
    f.append(text(ox - 8, v37 + 4, "37 %", size=11, color=MUTED, anchor="end"))

    # поріг V0/2
    vhalf = oy - span * 0.5
    f.append(line(ox, vhalf, ox + axw, vhalf, color=NEG, sw=1.4, dash="6,4"))
    f.append(text(ox + axw - 4, vhalf - 8, "поріг підсилювача (½ розмаху)", size=11, color=NEG, anchor="end"))

    # крива
    pts = []
    for i in range(0, axw + 1, 5):
        v = oy - span * math.exp(-i / tau_px)
        pts.append("%.1f,%.1f" % (ox + i, v))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), INK))

    # вертикаль на τ
    f.append(line(ox + tau_px, oy, ox + tau_px, v37, color=MUTED, sw=1.0, dash="3,3"))
    f.append(text(ox + tau_px, oy + 18, "τ", size=13, color=INK, anchor="middle", italic=True))

    # момент t_retain (де крива перетинає поріг)
    t_ret = -tau_px * math.log(0.5)
    f.append(line(ox + t_ret, oy, ox + t_ret, vhalf, color=POS, sw=1.4, dash="4,3"))
    f.append(text(ox + t_ret, oy + 18, "t_retain ≈ 0.7·τ", size=12, color=POS, anchor="middle"))

    # зелена зона (вікно до регенерації) і рожева (втрачено)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#27ae60" opacity="0.10"/>'
             % (ox, top, t_ret, oy - top))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c0392b" opacity="0.08"/>'
             % (ox + t_ret, top, axw - t_ret, oy - top))
    f.append(text(ox + t_ret / 2, top - 6, "вікно для регенерації", size=11, color=FIELD, anchor="middle"))
    f.append(text(ox + t_ret + (axw - t_ret) / 2, top - 6, "біт утрачено", size=11, color=POS, anchor="middle"))

    f.append(text(W / 2, H - 14,
                  "Біт «згублено» не коли заряд вичерпано, а щойно крива впаде нижче порога. Стандарт кладе на це 64 мс.",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "decay-window.svg"), W, H, *f)


# ── 6. Час утримання: DRAM, SRAM, Flash — той самий розряд, різний R ───────
def fig_retention_spectrum():
    W, H = 860, 430
    f = [text(W / 2, 30, "Та сама комірка-конденсатор, різна «герметичність» вузла",
              size=17, bold=True)]

    rows = [
        ("DRAM", "заряд за\nнещільним ключем", "десятки мс — потрібна регенерація", POS, "#fdecea"),
        ("SRAM", "петля з двох\nінверторів", "тримає, доки є живлення", NEG, "#eaf0fd"),
        ("Flash", "заряд замкнено\nв ізоляторі", "роки без живлення", FIELD, "#eafaf0"),
    ]
    y = 90
    barx, barw = 230, 540
    for name, mech, life, col, fill in rows:
        f.append(rect(40, y, 180, 92, fill=fill, stroke=col, sw=1.8, rx=8))
        f.append(text(130, y + 30, name, size=18, bold=True, color=col))
        f.append(mtext(130, y + 52, mech, size=11, color=MUTED))
        # «герметичність» як шкала логарифму часу утримання
        f.append(rect(barx, y + 26, barw, 34, fill="#fafafa", stroke="#dddddd", sw=1.0, rx=6))
        # довжина бруска ~ логарифм часу: DRAM коротко, Flash на всю
        frac = {"DRAM": 0.18, "SRAM": 0.5, "Flash": 1.0}[name]
        f.append(rect(barx, y + 26, barw * frac, 34, fill=fill, stroke=col, sw=1.6, rx=6))
        f.append(text(barx + barw * frac + 10, y + 48, life, size=12, color=col, anchor="start")
                 if frac < 0.7 else
                 text(barx + barw * frac - 10, y + 48, life, size=12, color="#ffffff", anchor="end", bold=True))
        y += 110

    f.append(text(barx, y - 6, "← коротший час утримання            довший час утримання →",
                  size=11, color=MUTED, anchor="start"))
    f.append(text(W / 2, H - 12,
                  "Один RC-механізм із кардинально різним опором витоку: від «оновлюй щомиті» до «зберігає десятиліттями».",
                  size=12.5, color=INK))
    render(os.path.join(IMG, "retention-spectrum.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cell_compare()
    fig_leak_refresh()
    fig_array_rowcol()
    fig_cell_rc()
    fig_decay_window()
    fig_retention_spectrum()
    print("Готово: 6 SVG у", IMG)
