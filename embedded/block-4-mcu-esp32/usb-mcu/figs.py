# -*- coding: utf-8 -*-
"""
figs.py — Розділ 4.12 USB на мікроконтролері
Генерує всі фігури тем 4.12.1–4.12.8 у ./img/
НЕ перевизначає примітиви svgkit — лише генерує специфічні для теми SVG.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

def out(name):
    return os.path.join(OUT, name)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.1.1 — Асиметрія USB: хост ініціює, пристрій лише відповідає
# ══════════════════════════════════════════════════════════════════════════════
def fig_1211_host_device_roles():
    W, H = 820, 400
    parts = []

    parts.append(text(W/2, 30, "Рис. 4.12.1.1. Асиметрія USB: хост ініціює, пристрій лише відповідає",
                      size=15, bold=True))

    # ── Хост (ліворуч) ──
    hx, hy, hw, hh = 60, 100, 200, 200
    parts.append(rect(hx, hy, hw, hh, fill="#eaf0fd", stroke=NEG, sw=2.5, rx=10))
    parts.append(text(hx + hw/2, hy + 30, "ХОС Т", size=18, bold=True, color=NEG))
    parts.append(text(hx + hw/2, hy + 60, "(ПК, смартфон)", size=11, color=MUTED))
    parts.append(mtext(hx + hw/2, hy + 95, ["Ініціює ВСЕ:", "• запити", "• таймінг", "• адреси"], size=12, color=INK))

    # ── Пристрій (праворуч) ──
    dx, dy, dw, dh = 560, 100, 200, 200
    parts.append(rect(dx, dy, dw, dh, fill="#fef9ec", stroke="#e67e22", sw=2.5, rx=10))
    parts.append(text(dx + dw/2, dy + 30, "ПРИ СТРІЙ", size=18, bold=True, color="#e67e22"))
    parts.append(text(dx + dw/2, dy + 60, "(ESP32, флешка…)", size=11, color=MUTED))
    parts.append(mtext(dx + dw/2, dy + 95, ["Лише ВІДПОВІДАЄ:", "• ніколи не першим", "• реактивна логіка"], size=12, color=INK))

    # ── Стрілки запитів (суцільні, від хоста) ──
    mid_y1, mid_y2 = 155, 195
    ax1, ax2 = hx + hw, dx
    mid_x = (ax1 + ax2) / 2

    parts.append(arrow(ax1 + 5, mid_y1 - 10, ax2 - 5, mid_y1 - 10, color=NEG, sw=2))
    parts.append(text(mid_x, mid_y1 - 22, "ЗАПИТ (хост → пристрій)", size=11, bold=True, color=NEG))

    # ── Стрілки відповіді (пунктир) ──
    parts.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="1.8" stroke-dasharray="8,4" marker-end="url(#arrow)"/>'
                  % (ax2 - 5, mid_y2 + 10, ax1 + 5, mid_y2 + 10, "#e67e22")))
    parts.append(text(mid_x, mid_y2 + 32, "ВІДПОВІДЬ (лише у відповідь!)", size=11, bold=True, color="#e67e22"))

    # ── Контраст: I²C / SPI ──
    cx2, cy2, cw, ch = 240, 320, 340, 62
    parts.append(rect(cx2, cy2, cw, ch, fill="#f0f9f0", stroke=FIELD, sw=1.5, rx=8))
    parts.append(text(cx2 + cw/2, cy2 + 20, "Контраст: I²C / SPI (§Модуль 3)", size=12, bold=True, color=FIELD))
    parts.append(text(cx2 + cw/2, cy2 + 42, "Кілька рівноправних учасників → арбітраж шини", size=11, color=MUTED))

    # ── Висновок ──
    bfrag, _, _ = textbox(W/2, H - 28, "Пристрій реактивний — звідси проста прошивка-device", size=13, bold=True,
                          fill="#eaf0fd", stroke=NEG, sw=2, pad=12)
    parts.append(bfrag)

    render(out('fig-r12-1-1-host-device-roles.svg'), W, H, *parts)
    print("fig-r12-1-1-host-device-roles.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.1.2 — Топологія USB: дерево з коренем у хості й хабами
# ══════════════════════════════════════════════════════════════════════════════
def fig_1212_usb_tree():
    W, H = 820, 480
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.1.2. Топологія USB — дерево з коренем у хості й хабами",
                      size=15, bold=True))

    # ── Рівні (зверху вниз) ──
    levels = [
        (W/2,    70,  "Хост (ПК)",            NEG,    "#eaf0fd"),
        (W/2,   150,  "Кореневий хаб\n(root hub)",  "#8e44ad", "#f5eef8"),
        (280,   250,  "Хаб монітора\n(рівень 2)",    "#27ae60", "#eafaf1"),
        (540,   250,  "Хаб клавіатури\n(рівень 2)",  "#e67e22", "#fef9ec"),
        (160,   360,  "Клавіатура + тачпад\n(композит, адр. 3)", "#c0392b", "#fdecea"),
        (380,   360,  "Флешка\n(адр. 4)",             "#2457d6", "#eaf0fd"),
        (540,   360,  "Веб-камера\n(адр. 5)",          MUTED,    FILL),
        (680,   360,  "Геймпад\n(адр. 6)",             "#27ae60", "#eafaf1"),
    ]

    node_info = levels  # (x, y, label, stroke, fill)

    def draw_node(x, y, label, stroke, fill, w=170, h=56):
        frg = rect(x - w/2, y - h/2, w, h, fill=fill, stroke=stroke, sw=2, rx=8)
        frg += mtext(x, y - 4, label, size=12, color=INK)
        return frg

    # Координати вузлів:
    nodes = {
        'host':    (W/2,  70),
        'root':    (W/2, 155),
        'hub1':    (280,  255),
        'hub2':    (560,  255),
        'dev1':    (150,  365),
        'dev2':    (380,  365),
        'dev3':    (560,  365),
        'dev4':    (700,  365),
    }

    # З'єднання
    connections = [
        ('host', 'root'),
        ('root', 'hub1'), ('root', 'hub2'),
        ('hub1', 'dev1'), ('hub1', 'dev2'),
        ('hub2', 'dev3'), ('hub2', 'dev4'),
    ]
    for a, b in connections:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        parts.append(line(x1, y1 + 28, x2, y2 - 28, color=MUTED, sw=1.5))

    # Вузли
    parts.append(draw_node(*nodes['host'], "Хост (ПК)", NEG, "#eaf0fd"))
    parts.append(draw_node(*nodes['root'], "Кореневий хаб\n(root hub)", "#8e44ad", "#f5eef8"))
    parts.append(draw_node(*nodes['hub1'], "Хаб монітора\n(рівень 2)", "#27ae60", "#eafaf1"))
    parts.append(draw_node(*nodes['hub2'], "Хаб клавіатури\n(рівень 2)", "#e67e22", "#fef9ec"))
    parts.append(draw_node(*nodes['dev1'], "Клавіатура+тачпад\n(композит, адр.3)", "#c0392b", "#fdecea", w=185))
    parts.append(draw_node(*nodes['dev2'], "Флешка\n(адр.4)", "#2457d6", "#eaf0fd"))
    parts.append(draw_node(*nodes['dev3'], "Веб-камера\n(адр.5)", MUTED, FILL))
    parts.append(draw_node(*nodes['dev4'], "Геймпад\n(адр.6)", "#27ae60", "#eafaf1"))

    # Підписи рівнів
    for lvl, lbl in [(70, "Рівень 0"), (155, "Рівень 1"), (255, "Рівень 2"), (365, "Рівень 3")]:
        parts.append(text(38, lvl + 5, lbl, size=11, color=MUTED, anchor="middle"))

    # Примітка
    bfrag, _, _ = textbox(W/2, H - 26, "До 127 адрес · до 5–7 рівнів · хаб — теж пристрій · один порт ПК = ціле дерево",
                          size=12, bold=False, fill=FILL, stroke=MUTED, sw=1.2, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-1-2-usb-tree.svg'), W, H, *parts)
    print("fig-r12-1-2-usb-tree.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.1.3 — Підрахунок адрес: один порт ноутбука
# ══════════════════════════════════════════════════════════════════════════════
def fig_1213_enum_count():
    W, H = 760, 380
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.1.3. Один порт ноутбука — скільки адрес зайнято",
                      size=15, bold=True))

    rows = [
        ("#",   "Пристрій",                     "Адреса", "Рівень", NEG),
        ("—",   "Хост (ноутбук)",               "—",      "0",      NEG),
        ("1",   "Кореневий хаб",                "1",      "1",      "#8e44ad"),
        ("2",   "Хаб монітора",                 "2",      "2",      "#27ae60"),
        ("3",   "Клавіатура (CDC? HID+тачпад)", "3",      "3",      "#c0392b"),
        ("4",   "Флешка",                       "4",      "3",      "#2457d6"),
        ("5",   "Веб-камера",                   "5",      "3",      "#e67e22"),
        ("6",   "Кореневий хаб #2 (USB 3)",     "6",      "1",      "#8e44ad"),
    ]

    col_x = [40, 90, 480, 590, 670]
    col_labels = ["#", "Пристрій", "Адреса", "Рівень", ""]
    row_h = 42
    start_y = 60

    # заголовки колонок
    for xi, lbl in zip(col_x, col_labels):
        parts.append(text(xi, start_y, lbl, size=13, bold=True, color=INK, anchor="start"))

    # роздільник
    parts.append(line(32, start_y + 8, W - 32, start_y + 8, color=MUTED, sw=1))

    for i, (num, dev, addr, lvl, color) in enumerate(rows[1:], 1):
        y = start_y + i * row_h
        bg = "#f8faff" if i % 2 == 0 else BG
        parts.append(rect(32, y - 24, W - 64, row_h - 4, fill=bg, stroke="none", sw=0, rx=4))
        parts.append(text(col_x[0], y, num, size=13, color=color, anchor="start", bold=True))
        parts.append(text(col_x[1], y, dev, size=12, color=INK, anchor="start"))
        parts.append(text(col_x[2], y, addr, size=13, bold=True, color=color, anchor="start"))
        parts.append(text(col_x[3], y, lvl, size=13, color=MUTED, anchor="start"))

    # Висновок
    bfrag, _, _ = textbox(W/2, H - 28,
                          "Ліміт 127 — про адреси на дереві, не про фізичні гнізда",
                          size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=2, pad=12)
    parts.append(bfrag)

    render(out('fig-r12-1-3-enum-count.svg'), W, H, *parts)
    print("fig-r12-1-3-enum-count.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.2.1 — Чотири дроти USB
# ══════════════════════════════════════════════════════════════════════════════
def fig_1221_four_wires():
    W, H = 680, 320
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.2.1. Чотири дроти USB: живлення і дані",
                      size=15, bold=True))

    # Кабель (прямокутник-труба)
    cable_x, cable_y, cable_w, cable_h = 200, 70, 280, 180
    parts.append(rect(cable_x, cable_y, cable_w, cable_h, fill="#f0f0f0", stroke=LINE, sw=2, rx=4))
    parts.append(text(cable_x + cable_w/2, cable_y - 12, "USB кабель", size=12, bold=True, color=MUTED))

    # Дроти всередині кабелю
    wires = [
        (cable_x + 40,  cable_y + 35,  "VBUS (+5 В)",  "#c0392b", "#fdecea"),
        (cable_x + 40,  cable_y + 80,  "GND",           "#333333", "#e0e0e0"),
        (cable_x + 40,  cable_y + 125, "D+",            FIELD,     "#eafaf1"),
        (cable_x + 40,  cable_y + 162, "D−",            FIELD,     "#eafaf1"),
    ]
    for wx, wy, wlabel, wcol, wfill in wires:
        parts.append(rect(wx, wy - 14, 200, 28, fill=wfill, stroke=wcol, sw=2, rx=5))
        parts.append(text(wx + 100, wy + 5, wlabel, size=13, bold=True, color=wcol))

    # Скобка «дані»
    bx = cable_x + cable_w + 10
    parts.append(line(bx, cable_y + 111, bx + 12, cable_y + 111, color=FIELD, sw=2))
    parts.append(line(bx + 12, cable_y + 111, bx + 12, cable_y + 176, color=FIELD, sw=2))
    parts.append(line(bx + 12, cable_y + 176, bx, cable_y + 176, color=FIELD, sw=2))
    parts.append(text(bx + 38, cable_y + 144, "дані\n(вита пара)", size=11, color=FIELD, anchor="start"))

    # Скобка «живлення»
    px = cable_x - 10
    parts.append(line(px, cable_y + 21, px - 12, cable_y + 21, color="#c0392b", sw=2))
    parts.append(line(px - 12, cable_y + 21, px - 12, cable_y + 94, color="#c0392b", sw=2))
    parts.append(line(px - 12, cable_y + 94, px, cable_y + 94, color="#c0392b", sw=2))
    parts.append(text(px - 60, cable_y + 58, "живлення\n(§4.12.7)", size=11, color="#c0392b", anchor="middle"))

    # Примітка
    parts.append(text(W/2, H - 16, "Дані — лише D+/D−; живлення — окремо VBUS/GND",
                      size=12, color=MUTED))

    render(out('fig-r12-2-1-four-wires.svg'), W, H, *parts)
    print("fig-r12-2-1-four-wires.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.2.2 — Диференційна пара б'є завади
# ══════════════════════════════════════════════════════════════════════════════
def fig_1222_differential():
    W, H = 820, 420
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.2.2. Диференційна пара: важлива різниця D+−D−, не рівень",
                      size=15, bold=True))

    # Часова вісь
    tx0, tx1, ty_base = 60, 720, 90
    parts.append(line(tx0, ty_base, tx1, ty_base, color=MUTED, sw=1, dash="4,3"))
    parts.append(text(tx0 - 30, ty_base + 4, "t", size=13, color=MUTED))

    import math

    def wave_pts(x0, x1, y_base, amp, phase=0, n=300):
        pts = []
        for i in range(n):
            x = x0 + (x1 - x0) * i / (n - 1)
            t_val = (x - x0) / (x1 - x0)
            # NRZI-подібна прямокутна хвиля
            seg = int(t_val * 8)
            bit = [1, 1, -1, 1, -1, -1, 1, 1][seg % 8]
            y = y_base - amp * bit + phase
            pts.append((x, y))
        return pts

    def noise_pts(x0, x1, y_base, amp_noise, n=300):
        pts = []
        for i in range(n):
            x = x0 + (x1 - x0) * i / (n - 1)
            t_val = (x - x0) / (x1 - x0)
            seg = int(t_val * 8)
            bit = [1, 1, -1, 1, -1, -1, 1, 1][seg % 8]
            # синфазна завада
            noise = amp_noise * math.sin(t_val * 30)
            y = y_base - 20 * bit + noise
            pts.append((x, y))
        return pts

    def polyline(pts, color, sw=2):
        path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (path_d, color, sw)

    row_labels = [
        (ty_base + 0,  "D+ (без завади)", FIELD),
        (ty_base + 90, "D− (без завади)", "#2457d6"),
        (ty_base + 185,"D+ із завадою",   "#e67e22"),
        (ty_base + 270,"D− із завадою",   "#e67e22"),
        (ty_base + 355,"Різниця D+−D−",   INK),
    ]

    amp = 25
    y_rows = [ty_base + 50, ty_base + 135, ty_base + 230, ty_base + 315, ty_base + 390]
    mid_y = [r for r in y_rows]

    # D+ і D− без завади (протифаза)
    pts_dp = wave_pts(tx0, tx1, mid_y[0], amp)
    pts_dm = wave_pts(tx0, tx1, mid_y[1], amp, phase=0)
    # зробити D− протилежним
    pts_dm_inv = [(x, 2*mid_y[1] - y) for x, y in pts_dm]

    parts.append(polyline(pts_dp, FIELD, 2))
    parts.append(polyline(pts_dm_inv, NEG, 2))

    # Мітки рядків
    for (ry, rlbl, rcol) in row_labels:
        parts.append(text(tx0 - 10, ry + 4, rlbl, size=11, color=rcol, anchor="end"))

    # D+ і D− із синфазною завадою
    amp_n = 12
    pts_dp_n = noise_pts(tx0, tx1, mid_y[2], amp_n)
    pts_dm_n_raw = noise_pts(tx0, tx1, mid_y[3], amp_n)
    pts_dm_n = [(x, y + (mid_y[3] - mid_y[2])) for x, y in pts_dp_n]
    # інвертувати сигнальну частину, лишити завadu
    pts_dp_n2 = []
    pts_dm_n2 = []
    for i in range(len(pts_dp_n)):
        xv = pts_dp_n[i][0]
        t_v = (xv - tx0) / (tx1 - tx0)
        seg = int(t_v * 8)
        bit = [1, 1, -1, 1, -1, -1, 1, 1][seg % 8]
        noise = amp_n * math.sin(t_v * 30)
        pts_dp_n2.append((xv, mid_y[2] - amp * bit + noise))
        pts_dm_n2.append((xv, mid_y[3] + amp * bit + noise))

    parts.append(polyline(pts_dp_n2, "#e67e22", 2))
    parts.append(polyline(pts_dm_n2, "#e67e22", 2))

    # Різниця (завада зникає)
    pts_diff = []
    for i in range(len(pts_dp_n2)):
        xv = pts_dp_n2[i][0]
        diff_y = (pts_dp_n2[i][1] + pts_dm_n2[i][1]) / 2  # середнє відхилення скасовується
        # сигнал чистий
        t_v = (xv - tx0) / (tx1 - tx0)
        seg = int(t_v * 8)
        bit = [1, 1, -1, 1, -1, -1, 1, 1][seg % 8]
        pts_diff.append((xv, mid_y[4] - amp * bit))

    parts.append(polyline(pts_diff, INK, 2.5))

    # Анотація завади
    bfrag, _, _ = textbox(550, mid_y[2] - 40, "Синфазна завада\nзсуває ОБИДВІ лінії однаково", size=11,
                          fill="#fff8e8", stroke="#e67e22", sw=1.5, pad=8)
    parts.append(bfrag)
    bfrag2, _, _ = textbox(550, mid_y[4] - 10, "Різниця → завада зникла\nБіт цілий!", size=11,
                           fill="#eafaf1", stroke=FIELD, sw=1.5, pad=8)
    parts.append(bfrag2)

    # Підсумок
    parts.append(text(W/2, H - 12, "Глибша фізика диф. пар — §6.4.7", size=11, color=MUTED))

    render(out('fig-r12-2-2-differential.svg'), W, H, *parts)
    print("fig-r12-2-2-differential.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.2.3 — Підтяжка 1.5 кОм: присутність і швидкість
# ══════════════════════════════════════════════════════════════════════════════
def fig_1223_pullup_speed():
    W, H = 760, 360
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.2.3. Підтяжка 1.5 кОм оголошує присутність і швидкість",
                      size=15, bold=True))

    # ── Ліва колонка: Full-Speed (D+ підтягнутий) ──
    lx = 150
    parts.append(text(lx, 62, "Full-Speed (12 Мбіт/с)", size=14, bold=True, color=FIELD))
    # схема: D+ піднятий через резистор
    parts.append(line(lx - 30, 110, lx + 30, 110, color=FIELD, sw=2.5))  # D+
    parts.append(text(lx - 60, 113, "D+", size=13, bold=True, color=FIELD, anchor="end"))
    # підтяжка вгору
    parts.append(line(lx, 110, lx, 80, color=LINE, sw=2))
    parts.append(rect(lx - 14, 80, 28, 18, fill="#fff", stroke=LINE, sw=1.5, rx=3))
    parts.append(text(lx, 92, "1.5 кОм", size=9, color=INK))
    parts.append(line(lx, 80, lx, 68, color=LINE, sw=2))
    parts.append(text(lx, 60, "3.3 В", size=11, color=POS, bold=True))
    # D− плаваючий
    parts.append(line(lx - 30, 140, lx + 30, 140, color=MUTED, sw=1.5, dash="6,4"))
    parts.append(text(lx - 60, 143, "D−", size=13, color=MUTED, anchor="end"))
    parts.append(text(lx, 158, "(плаваючий)", size=10, color=MUTED))

    # Момент підключення (сигнал D+ піднімається)
    tx0, tx1, ty = lx - 60, lx + 60, 195
    parts.append(line(tx0, ty + 25, tx1, ty + 25, color=MUTED, sw=1))
    parts.append(line(tx0, ty + 25, tx0 + 40, ty + 25, color=FIELD, sw=2))
    parts.append(line(tx0 + 40, ty + 25, tx0 + 40, ty, color=FIELD, sw=2))
    parts.append(line(tx0 + 40, ty, tx1, ty, color=FIELD, sw=2))
    parts.append(text(lx, ty + 42, "D+ піднімається → хост бачить → енумерація (→§4.12.3)",
                      size=10, color=FIELD))

    # ── Права колонка: Low-Speed (D− підтягнутий) ──
    rx = 580
    parts.append(text(rx, 62, "Low-Speed (1.5 Мбіт/с)", size=14, bold=True, color=NEG))
    parts.append(line(rx - 30, 110, rx + 30, 110, color=MUTED, sw=1.5, dash="6,4"))
    parts.append(text(rx - 60, 113, "D+", size=13, color=MUTED, anchor="end"))
    parts.append(line(rx - 30, 140, rx + 30, 140, color=NEG, sw=2.5))
    parts.append(text(rx - 60, 143, "D−", size=13, bold=True, color=NEG, anchor="end"))
    # підтяжка D−
    parts.append(line(rx, 140, rx, 110, color=LINE, sw=2))
    parts.append(rect(rx - 14, 110, 28, 18, fill="#fff", stroke=LINE, sw=1.5, rx=3))
    parts.append(text(rx, 122, "1.5 кОм", size=9, color=INK))
    parts.append(line(rx, 110, rx, 98, color=LINE, sw=2))
    parts.append(text(rx, 92, "3.3 В", size=11, color=POS, bold=True))
    parts.append(text(rx - 60, 113, "D+", size=13, color=MUTED, anchor="end"))
    parts.append(text(rx + 50, 143, "(підтягнутий)", size=10, color=NEG, anchor="start"))

    # Висновок
    bfrag, _, _ = textbox(W/2, H - 30,
                          "Вибір лінії підтяжки = заявлена швидкість\nOdна підтяжка — і присутність, і клас швидкості",
                          size=13, bold=True, fill="#f5f5f5", stroke=LINE, sw=1.5, pad=12)
    parts.append(bfrag)

    render(out('fig-r12-2-3-pullup-speed.svg'), W, H, *parts)
    print("fig-r12-2-3-pullup-speed.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.2.4 — Три швидкості USB 2.0: LS / FS / HS
# ══════════════════════════════════════════════════════════════════════════════
def fig_1224_speeds_table():
    W, H = 780, 320
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.2.4. Три швидкості USB 2.0: LS / FS / HS",
                      size=15, bold=True))

    speeds = [
        ("Low-Speed",  "LS",  "1.5 Мбіт/с",   "Миші, клавіатури",             "#9b59b6", "#f5eef8",  8),
        ("Full-Speed", "FS",  "12 Мбіт/с",     "Більшість МК (ESP32-OTG!)",     FIELD,     "#eafaf1", 55),
        ("High-Speed", "HS",  "480 Мбіт/с",    "Камери, диски",                 NEG,       "#eaf0fd", 220),
    ]

    bar_x0, bar_y, bar_max_w, bar_h = 120, 70, 550, 64
    row_gap = 82

    for i, (name, abbr, speed, use, color, fill, bar_w) in enumerate(speeds):
        by = bar_y + i * row_gap
        # назва
        parts.append(text(bar_x0 - 8, by + 30, abbr, size=16, bold=True, color=color, anchor="end"))
        parts.append(text(bar_x0 - 8, by + 50, name, size=10, color=MUTED, anchor="end"))
        # смуга (логарифмічна по bar_w)
        parts.append(rect(bar_x0, by, bar_w, bar_h, fill=fill, stroke=color, sw=2, rx=6))
        parts.append(text(bar_x0 + bar_w/2, by + 26, speed, size=15, bold=True, color=color))
        parts.append(text(bar_x0 + bar_w/2, by + 48, use, size=11, color=INK))

    # Мітка: ESP32 — Full-Speed
    fx = bar_x0 + 55 + 10
    fy = bar_y + row_gap + 4
    parts.append(line(fx, fy, fx + 30, fy - 18, color=FIELD, sw=1.5))
    parts.append(text(fx + 34, fy - 18, "ESP32 нативно — лише FS (важить для §4.12.6)",
                      size=11, color=FIELD, anchor="start"))

    # Примітка SuperSpeed
    parts.append(text(W/2, H - 16,
                      "SuperSpeed 5 Гбіт/с+ (USB 3.x) — інша фізика, поза обсягом цього розділу",
                      size=11, color=MUTED))

    render(out('fig-r12-2-4-speeds-table.svg'), W, H, *parts)
    print("fig-r12-2-4-speeds-table.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.3.1 — Послідовність енумерації
# ══════════════════════════════════════════════════════════════════════════════
def fig_1231_enum_sequence():
    W, H = 820, 520
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.3.1. Послідовність енумерації: від підключення до configured",
                      size=15, bold=True))

    hx, dx = 180, 600
    # Колонки
    parts.append(text(hx, 60, "Хост", size=14, bold=True, color=NEG))
    parts.append(text(dx, 60, "Пристрій", size=14, bold=True, color="#e67e22"))
    parts.append(line(hx, 68, hx, H - 40, color=NEG, sw=1.5, dash="4,3"))
    parts.append(line(dx, 68, dx, H - 40, color="#e67e22", sw=1.5, dash="4,3"))

    steps = [
        (78,  "Підключення → підтяжка D+",  True,  "D+ піднявся → хост бачить пристрій"),
        (122, "Reset (скидання)",             True,  "Пристрій у початковому стані"),
        (166, "GET_DESCRIPTOR(device) @addr0",True,  "Відповідь: перші 8 байтів дескриптора"),
        (210, "SET_ADDRESS (наприклад, 5)",   True,  "Пристрій запам'ятовує нову адресу"),
        (254, "GET_DESCRIPTOR(device) @addr5",True,  "Повний 18-байтний device descriptor"),
        (298, "GET_DESCRIPTOR(config)…",      True,  "Config + Interface + Endpoint"),
        (342, "SET_CONFIGURATION(1)",         True,  "Пристрій у стані configured ✓"),
    ]

    mid_x = (hx + dx) / 2

    for (sy, hst_label, to_dev, dev_label) in steps:
        if to_dev:
            # хост → пристрій
            parts.append(arrow(hx + 5, sy, dx - 5, sy, color=NEG, sw=1.8))
            parts.append(text(mid_x, sy - 10, hst_label, size=11, color=NEG))
            # відповідь (пунктир)
            parts.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                          'stroke-width="1.5" stroke-dasharray="6,4" marker-end="url(#arrow)"/>'
                          % (dx - 5, sy + 22, hx + 5, sy + 22, "#e67e22")))
            parts.append(text(mid_x, sy + 36, dev_label, size=10, color="#e67e22"))

    # Фінальна рамка
    bfrag, _, _ = textbox(dx, H - 28, "CONFIGURED ✓\nГотовий до роботи", size=13, bold=True,
                          fill="#eafaf1", stroke=FIELD, sw=2.5, pad=10)
    parts.append(bfrag)

    # EP0 підпис
    parts.append(text(W/2, H - 8, "Вся енумерація — через EP0 (control transfer)",
                      size=11, color=MUTED))

    render(out('fig-r12-3-1-enum-sequence.svg'), W, H, *parts)
    print("fig-r12-3-1-enum-sequence.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.3.2 — Дерево дескрипторів
# ══════════════════════════════════════════════════════════════════════════════
def fig_1232_descriptor_tree():
    W, H = 780, 460
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.3.2. Дерево дескрипторів: Device → Config → Interface → Endpoint",
                      size=15, bold=True))

    # Device descriptor (корінь)
    dev_x, dev_y = 390, 80
    parts.append(fitbox(dev_x - 180, dev_y - 28, 360, 56,
                        "Device Descriptor\nVID / PID · bcdUSB · bDeviceClass · bMaxPacketSize",
                        size=12, bold=False, fill="#eaf0fd", stroke=NEG, sw=2.5, rx=8))
    parts.append(text(dev_x, dev_y - 36, "Рівень 1", size=10, color=MUTED))

    # Configuration descriptor
    cfg_x, cfg_y = 390, 180
    parts.append(fitbox(cfg_x - 160, cfg_y - 24, 320, 48,
                        "Configuration Descriptor\nbNumInterfaces · bMaxPower · bmAttributes",
                        size=12, fill="#f5eef8", stroke="#8e44ad", sw=2, rx=8))
    parts.append(line(dev_x, dev_y + 28, cfg_x, cfg_y - 24, color=MUTED, sw=1.5))

    # Два Interface (і рядкові дескриптори збоку)
    iface_positions = [(230, 290), (550, 290)]
    iface_labels = [
        "Interface 0 (CDC)\nbInterfaceClass=0x02",
        "Interface 1 (HID)\nbInterfaceClass=0x03",
    ]
    iface_colors = [FIELD, "#e67e22"]
    iface_fills = ["#eafaf1", "#fef9ec"]

    for (ix, iy), ilbl, icol, ifill in zip(iface_positions, iface_labels, iface_colors, iface_fills):
        parts.append(fitbox(ix - 130, iy - 24, 260, 48, ilbl, size=11, fill=ifill, stroke=icol, sw=2, rx=8))
        parts.append(line(cfg_x, cfg_y + 24, ix, iy - 24, color=MUTED, sw=1.5))

    # Endpoint-и під кожним Interface
    ep_data = [
        # (x_offset_від_interface, y, label)
        (230 - 70, 385, "EP1 bulk-IN"),
        (230 + 70, 385, "EP1 bulk-OUT"),
        (550, 385, "EP2 interrupt-IN"),
    ]
    ep_parents = [230, 230, 550]
    ep_iface_y = 290
    for (ex, ey, elbl), ep_x in zip(ep_data, ep_parents):
        parts.append(fitbox(ex - 60, ey - 22, 120, 44, elbl, size=11, fill=FILL, stroke=MUTED, sw=1.5, rx=6))
        parts.append(line(ep_x, ep_iface_y + 24, ex, ey - 22, color=MUTED, sw=1.2, dash="5,3"))

    # String дескриптори збоку
    parts.append(rect(640, 175, 120, 46, fill="#fffde7", stroke="#f39c12", sw=1.5, rx=6))
    parts.append(mtext(700, 200, ["String Desc.", "назва / серійник"], size=11, color="#b7770d"))
    parts.append(line(dev_x + 180, dev_y, 640, 198, color=MUTED, sw=1, dash="5,3"))

    # Підпис
    parts.append(text(W/2, H - 16, "VID/PID і клас — у Device Descriptor (→§4.12.5)",
                      size=11, color=MUTED))

    render(out('fig-r12-3-2-descriptor-tree.svg'), W, H, *parts)
    print("fig-r12-3-2-descriptor-tree.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.3.3 — 18 байтів device-дескриптора
# ══════════════════════════════════════════════════════════════════════════════
def fig_1233_device_descriptor_bytes():
    W, H = 820, 400
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.3.3. 18 байтів device-дескриптора (worked-приклад)",
                      size=15, bold=True))

    fields = [
        ("00", "0x12", "bLength=18"),
        ("01", "0x01", "bDescriptorType=DEVICE"),
        ("02", "0x00", "bcdUSB (lo)"),
        ("03", "0x02", "bcdUSB (hi) → USB 2.0"),
        ("04", "0x00", "bDeviceClass"),
        ("05", "0x00", "bDeviceSubClass"),
        ("06", "0x00", "bDeviceProtocol"),
        ("07", "0x40", "bMaxPacketSize0=64"),
        ("08", "0x83", "idVendor (lo)  ← VID"),
        ("09", "0x04", "idVendor (hi)  ← VID = 0x0483"),
        ("0A", "0x11", "idProduct (lo) ← PID"),
        ("0B", "0x57", "idProduct (hi) ← PID = 0x5711"),
        ("0C", "0x00", "bcdDevice (lo)"),
        ("0D", "0x02", "bcdDevice (hi)"),
        ("0E", "0x01", "iManufacturer (String idx)"),
        ("0F", "0x02", "iProduct (String idx)"),
        ("10", "0x03", "iSerialNumber (String idx)"),
        ("11", "0x01", "bNumConfigurations=1"),
    ]

    cols = 2
    col_w = W / cols
    row_h = 18
    start_y = 60
    highlight_bytes = {"08", "09", "0A", "0B"}  # VID/PID

    for i, (offset, hexval, desc) in enumerate(fields):
        col = i % cols
        row = i // cols
        x = 20 + col * col_w
        y = start_y + row * row_h

        fill = "#fffde7" if offset in highlight_bytes else (FILL if row % 2 == 0 else BG)
        color_hex = "#c0392b" if offset in highlight_bytes else NEG
        color_desc = "#c0392b" if offset in highlight_bytes else INK
        bold_flag = offset in highlight_bytes

        parts.append(rect(x, y - 13, col_w - 8, row_h - 1, fill=fill, stroke="none", sw=0, rx=3))
        parts.append(text(x + 8,        y, "[" + offset + "]", size=11, color=MUTED, anchor="start"))
        parts.append(text(x + 54,       y, hexval, size=12, color=color_hex, anchor="start", bold=bold_flag))
        parts.append(text(x + 104,      y, desc,   size=11, color=color_desc, anchor="start", bold=bold_flag))

    # Виноска VID/PID
    bfrag, _, _ = textbox(W/2, H - 26,
                          "Байти 08–0B: VID=0x0483 (STMicro) · PID=0x5711 — пара визначає драйвер у ОС",
                          size=12, bold=True, fill="#fffde7", stroke="#f39c12", sw=2, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-3-3-device-descriptor-bytes.svg'), W, H, *parts)
    print("fig-r12-3-3-device-descriptor-bytes.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.4.1 — Endpoint'и пристрою: IN/OUT і EP0
# ══════════════════════════════════════════════════════════════════════════════
def fig_1241_endpoints():
    W, H = 760, 360
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.4.1. Endpoint'и пристрою: однонапрямні труби та EP0",
                      size=15, bold=True))

    # Пристрій (коробка)
    box_x, box_y, box_w, box_h = 280, 60, 220, 260
    parts.append(rect(box_x, box_y, box_w, box_h, fill="#fef9ec", stroke="#e67e22", sw=2.5, rx=10))
    parts.append(text(box_x + box_w/2, box_y + 22, "Пристрій", size=14, bold=True, color="#e67e22"))

    # EP0 (двонапрямний, посередині)
    ep0_y = box_y + 65
    parts.append(rect(box_x + 30, ep0_y - 18, 160, 36, fill="#f5eef8", stroke="#8e44ad", sw=2, rx=6))
    parts.append(text(box_x + 110, ep0_y + 5, "EP0 (control, ↕)", size=12, bold=True, color="#8e44ad"))

    # EP1-IN
    ep1in_y = box_y + 130
    parts.append(rect(box_x + 30, ep1in_y - 18, 160, 36, fill="#eafaf1", stroke=FIELD, sw=2, rx=6))
    parts.append(text(box_x + 110, ep1in_y + 5, "EP1-IN (bulk →)", size=12, color=FIELD))

    # EP1-OUT
    ep1out_y = box_y + 185
    parts.append(rect(box_x + 30, ep1out_y - 18, 160, 36, fill="#eafaf1", stroke=FIELD, sw=2, rx=6))
    parts.append(text(box_x + 110, ep1out_y + 5, "EP1-OUT (bulk ←)", size=12, color=FIELD))

    # EP2-IN (interrupt)
    ep2in_y = box_y + 240
    parts.append(rect(box_x + 30, ep2in_y - 18, 160, 36, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    parts.append(text(box_x + 110, ep2in_y + 5, "EP2-IN (interrupt →)", size=12, color=NEG))

    # Хост (зліва)
    hx, hy, hw, hh = 60, 120, 140, 140
    parts.append(rect(hx, hy, hw, hh, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    parts.append(text(hx + hw/2, hy + 40, "Хост", size=14, bold=True, color=NEG))
    parts.append(text(hx + hw/2, hy + 70, "(ПК)", size=12, color=MUTED))
    parts.append(text(hx + hw/2, hy + 92, "ініціює", size=12, color=MUTED))

    # Стрілки IN = до хоста (праворуч → ліворуч)
    for ep_y in [ep1in_y, ep2in_y]:
        parts.append(arrow(box_x - 5, ep_y, hx + hw + 5, hy + 70, color=FIELD, sw=1.8))

    # Стрілки OUT = від хоста (ліворуч → праворуч)
    parts.append(arrow(hx + hw + 5, hy + 90, box_x - 5, ep1out_y, color="#e67e22", sw=1.8))

    # EP0 двонапрямний
    parts.append(('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="1.8" marker-end="url(#arrow)" marker-start="url(#arrow)"/>'
                  % (hx + hw + 5, hy + 50, box_x - 5, ep0_y, "#8e44ad")))

    # Легенда напрямів
    parts.append(text(W - 20, 80, "IN = до хоста",   size=12, color=FIELD,     anchor="end"))
    parts.append(text(W - 20, 100, "OUT = від хоста", size=12, color="#e67e22", anchor="end"))

    # Підпис EP0
    bfrag, _, _ = textbox(W/2, H - 22,
                          "EP0 — завжди є, двонапрямний, службовий (енумерація, §4.12.3)",
                          size=12, bold=True, fill="#f5eef8", stroke="#8e44ad", sw=1.5, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-4-1-endpoints.svg'), W, H, *parts)
    print("fig-r12-4-1-endpoints.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.4.2 — Хост диктує темп: кадри 1 мс
# ══════════════════════════════════════════════════════════════════════════════
def fig_1242_frames_polling():
    W, H = 820, 340
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.4.2. Хост диктує темп: кадри 1 мс — пристрій мовчить до запиту",
                      size=15, bold=True))

    # Вісь часу
    ax0, ax1, ay = 60, 760, 160
    parts.append(arrow(ax0, ay, ax1, ay, color=INK, sw=1.8))
    parts.append(text(ax1 + 12, ay + 5, "час", size=13, color=MUTED, anchor="start"))

    frame_w = 136
    frame_colors = [NEG, FIELD, "#8e44ad", "#e67e22", NEG]
    frame_labels = [
        ["SOF", "IN EP1", "OUT EP1", "IN EP2"],
        ["SOF", "IN EP1", "OUT EP1"],
        ["SOF", "IN EP2", "IN EP1"],
        ["SOF", "OUT EP1", "IN EP2"],
    ]

    for fi in range(4):
        fx = ax0 + fi * (frame_w + 6)
        # рамка кадру
        parts.append(rect(fx, ay - 60, frame_w, 52, fill=FILL, stroke=LINE, sw=1.5, rx=4))
        parts.append(text(fx + frame_w/2, ay - 78, "Кадр %d (1 мс)" % (fi + 1), size=11, color=MUTED))

        # транзакції всередині кадру
        slot_w = (frame_w - 8) / max(len(frame_labels[fi]), 1)
        for ti, tlbl in enumerate(frame_labels[fi]):
            tx = fx + 4 + ti * slot_w
            tcol = NEG if tlbl == "SOF" else (FIELD if "IN" in tlbl else "#e67e22")
            tfill = "#eaf0fd" if tlbl == "SOF" else ("#eafaf1" if "IN" in tlbl else "#fef9ec")
            parts.append(rect(tx, ay - 56, slot_w - 2, 44, fill=tfill, stroke=tcol, sw=1, rx=3))
            parts.append(text(tx + slot_w/2, ay - 30, tlbl, size=9, color=tcol, bold=(tlbl=="SOF")))

    # Пояснення
    parts.append(mtext(W/2, ay + 50,
                       ["Пристрій МОВЧИТЬ, доки хост не надіслав запит (SOF = Start Of Frame)",
                        "Це причина, чому device не може 'запушити' дані сам (→§4.12.1, §4.12.4)"],
                       size=12, color=MUTED))

    # Підпис HS мікрокадрів
    bfrag, _, _ = textbox(W/2, H - 22,
                          "HS (480 Мбіт/с): мікрокадри 125 мкс замість 1 мс",
                          size=12, fill=FILL, stroke=MUTED, sw=1, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-4-2-frames-polling.svg'), W, H, *parts)
    print("fig-r12-4-2-frames-polling.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.4.3 — Чотири типи передач
# ══════════════════════════════════════════════════════════════════════════════
def fig_1243_transfer_types():
    W, H = 820, 420
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.4.3. Чотири типи передач: гарантії часу проти доставки",
                      size=15, bold=True))

    types_data = [
        {
            "name": "Control",
            "time_g": False, "delivery_g": True,
            "retransmit": True,
            "use": "Енумерація, команди\n(EP0)",
            "color": "#8e44ad", "fill": "#f5eef8",
        },
        {
            "name": "Bulk",
            "time_g": False, "delivery_g": True,
            "retransmit": True,
            "use": "Флешка, CDC-порт\n(велика смуга, без гарантії часу)",
            "color": FIELD, "fill": "#eafaf1",
        },
        {
            "name": "Interrupt",
            "time_g": True, "delivery_g": True,
            "retransmit": True,
            "use": "Миша, HID-клавіатура\n(гарантована макс. затримка)",
            "color": "#e67e22", "fill": "#fef9ec",
        },
        {
            "name": "Isochronous",
            "time_g": True, "delivery_g": False,
            "retransmit": False,
            "use": "Аудіо, відео\n(гарантована смуга, без ретрансмісії)",
            "color": POS, "fill": "#fdecea",
        },
    ]

    row_h = 82
    start_y = 65
    name_w, flag_w, use_w = 140, 80, 320

    # Заголовки
    hdrs = [("Тип", 80), ("Гарантія\nдоставки", 225), ("Гарантія\nчасу", 310),
            ("Ретрансмісія", 395), ("Застосування", 570)]
    for lbl, hx in hdrs:
        parts.append(mtext(hx, start_y - 10, lbl, size=12, bold=True, color=INK))
    parts.append(line(32, start_y + 8, W - 32, start_y + 8, color=LINE, sw=1))

    yes = "✓"; no = "—"
    for i, td in enumerate(types_data):
        y = start_y + 16 + i * row_h
        bg = td["fill"] if i % 2 == 0 else BG
        parts.append(rect(32, y, W - 64, row_h - 4, fill=bg, stroke="none", sw=0, rx=4))
        parts.append(text(80, y + row_h/2, td["name"], size=15, bold=True, color=td["color"], anchor="middle"))
        parts.append(text(225, y + row_h/2, yes if td["delivery_g"] else no,
                          size=16, bold=True, color=FIELD if td["delivery_g"] else MUTED, anchor="middle"))
        parts.append(text(310, y + row_h/2, yes if td["time_g"] else no,
                          size=16, bold=True, color="#e67e22" if td["time_g"] else MUTED, anchor="middle"))
        parts.append(text(395, y + row_h/2, yes if td["retransmit"] else no,
                          size=16, bold=True, color=FIELD if td["retransmit"] else POS, anchor="middle"))
        parts.append(mtext(570, y + row_h/2 - 6, td["use"], size=11, color=INK))

    # Примітка Interrupt
    parts.append(text(W/2, H - 16,
                      "USB «interrupt» ≠ апаратне переривання: це гарантований опит хостом (→§4.5)",
                      size=11, color=MUTED))

    render(out('fig-r12-4-3-transfer-types.svg'), W, H, *parts)
    print("fig-r12-4-3-transfer-types.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.4.4 — Миша 125 Гц і 1000 Гц: bInterval
# ══════════════════════════════════════════════════════════════════════════════
def fig_1244_mouse_polling_rate():
    W, H = 760, 320
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.4.4. Чому миша «125 Гц» і «1000 Гц»: bInterval interrupt-EP",
                      size=15, bold=True))

    cases = [
        ("bInterval = 8 мс",  8,  "125 опитувань/с → «звичайна» миша",   "#e67e22"),
        ("bInterval = 1 мс",  1,  "1000 опитувань/с → «1000 Hz mouse»",   NEG),
    ]

    for ci, (label, interval, note, color) in enumerate(cases):
        base_y = 80 + ci * 110
        parts.append(text(60, base_y - 12, label, size=13, bold=True, color=color, anchor="start"))
        parts.append(text(60, base_y + 8, note, size=12, color=color, anchor="start"))

        # Часова шкала з тиками
        t_start, t_end = 260, 700
        parts.append(line(t_start, base_y, t_end, base_y, color=MUTED, sw=1))
        parts.append(text(t_end + 10, base_y + 5, "t", size=12, color=MUTED, anchor="start"))

        # Кількість тиків на шкалі
        n_ticks = 8 if interval == 8 else 16
        tick_gap = (t_end - t_start) / n_ticks

        for ti in range(n_ticks + 1):
            tx = t_start + ti * tick_gap
            parts.append(line(tx, base_y - 16, tx, base_y + 6, color=color, sw=2))

        parts.append(text((t_start + t_end)/2, base_y + 24,
                          "%d мс між опитуваннями → %d Гц" % (interval, 1000//interval),
                          size=11, color=MUTED))

    # Компроміс
    bfrag, _, _ = textbox(W/2, H - 26,
                          "Частіше = менша затримка руху курсора; але більше навантаження на шину й CPU хоста",
                          size=12, bold=False, fill=FILL, stroke=MUTED, sw=1.2, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-4-4-mouse-polling-rate.svg'), W, H, *parts)
    print("fig-r12-4-4-mouse-polling-rate.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.5.1 — Клас → готовий драйвер ОС
# ══════════════════════════════════════════════════════════════════════════════
def fig_1251_class_driver_match():
    W, H = 820, 380
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.5.1. Клас у дескрипторі → готовий драйвер ОС, без встановлення",
                      size=15, bold=True))

    # ── Пристрій зліва ──
    dx, dy, dw, dh = 40, 80, 210, 220
    parts.append(rect(dx, dy, dw, dh, fill="#fef9ec", stroke="#e67e22", sw=2, rx=10))
    parts.append(text(dx + dw/2, dy + 22, "Пристрій", size=13, bold=True, color="#e67e22"))
    parts.append(text(dx + dw/2, dy + 42, "(дескриптор)", size=11, color=MUTED))

    classes = [
        ("bDeviceClass=0x00", "CDC", FIELD,    "#eafaf1"),
        ("bDeviceClass=0x03", "HID", "#e67e22","#fef9ec"),
        ("bDeviceClass=0x08", "MSC", NEG,      "#eaf0fd"),
    ]
    for ci, (code, cls, ccol, cfill) in enumerate(classes):
        cy = dy + 68 + ci * 50
        parts.append(rect(dx + 14, cy, dw - 28, 38, fill=cfill, stroke=ccol, sw=1.5, rx=6))
        parts.append(text(dx + dw/2, cy + 14, code, size=10, color=MUTED))
        parts.append(text(dx + dw/2, cy + 29, cls, size=13, bold=True, color=ccol))

    # ── ОС посередині ──
    ox, oy, ow, oh = 330, 80, 220, 220
    parts.append(rect(ox, oy, ow, oh, fill="#f5f5f5", stroke=LINE, sw=2, rx=10))
    parts.append(text(ox + ow/2, oy + 22, "ОС", size=14, bold=True, color=INK))
    parts.append(text(ox + ow/2, oy + 40, "вбудовані драйвери", size=11, color=MUTED))

    drv_labels = ["CDC ACM драйвер", "HID драйвер", "Mass Storage Driver"]
    drv_cols   = [FIELD, "#e67e22", NEG]
    for di, (dlbl, dcol) in enumerate(zip(drv_labels, drv_cols)):
        dy2 = oy + 68 + di * 50
        parts.append(rect(ox + 14, dy2, ow - 28, 38, fill=BG, stroke=dcol, sw=1.5, rx=6))
        parts.append(text(ox + ow/2, dy2 + 22, dlbl, size=11, bold=True, color=dcol))

    # Стрілки клас → драйвер
    for ci in range(3):
        fy = dy + 68 + ci * 50 + 19
        ty = oy + 68 + ci * 50 + 19
        parts.append(arrow(dx + dw, fy, ox, ty, color=MUTED, sw=1.5))

    # ── Результат у користувача праворуч ──
    rx2, ry2, rw, rh = 600, 80, 190, 220
    parts.append(rect(rx2, ry2, rw, rh, fill="#eafaf1", stroke=FIELD, sw=2, rx=10))
    parts.append(text(rx2 + rw/2, ry2 + 22, "Бачить користувач", size=12, bold=True, color=FIELD))

    results = ["COM / ttyACM порт", "Клавіатура / миша", "Диск / флешка"]
    for ri, rlbl in enumerate(results):
        ry3 = ry2 + 68 + ri * 50
        parts.append(rect(rx2 + 14, ry3, rw - 28, 38, fill=BG, stroke=FIELD, sw=1, rx=6))
        parts.append(text(rx2 + rw/2, ry3 + 22, rlbl, size=11, color=INK))

    for ci in range(3):
        fy = oy + 68 + ci * 50 + 19
        ty = ry2 + 68 + ci * 50 + 19
        parts.append(arrow(ox + ow, fy, rx2, ty, color=MUTED, sw=1.5))

    # Підсумок
    bfrag, _, _ = textbox(W/2, H - 22,
                          "Клас = безкоштовна сумісність з будь-яким ПК — без встановлення драйвера",
                          size=13, bold=True, fill=FILL, stroke=LINE, sw=1.5, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-5-1-class-driver-match.svg'), W, H, *parts)
    print("fig-r12-5-1-class-driver-match.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.5.2 — Три робочі класи для МК: CDC, HID, MSC
# ══════════════════════════════════════════════════════════════════════════════
def fig_1252_three_classes():
    W, H = 820, 420
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.5.2. Три класи для МК: CDC, HID, MSC — EP, дані, вигляд в ОС",
                      size=15, bold=True))

    cls_data = [
        {
            "name": "CDC",
            "full": "Communications\nDevice Class",
            "ep": "bulk-IN, bulk-OUT\n+interrupt-IN (стан лінії)",
            "data": "текстові байти\n(ASCII, бінарний)",
            "os": "COM1 / ttyACM0",
            "color": FIELD, "fill": "#eafaf1",
        },
        {
            "name": "HID",
            "full": "Human Interface\nDevice",
            "ep": "interrupt-IN\n(маленькі звіти)",
            "data": "HID Reports\n(репорт-дескриптор)",
            "os": "Клавіатура / миша",
            "color": "#e67e22", "fill": "#fef9ec",
        },
        {
            "name": "MSC",
            "full": "Mass Storage\nClass",
            "ep": "bulk-IN, bulk-OUT",
            "data": "SCSI команди\n+ блоки даних",
            "os": "Диск / флешка (→§4.3)",
            "color": NEG, "fill": "#eaf0fd",
        },
    ]

    col_w = W / 3
    row_labels = ["Клас", "Endpoint-и", "Дані", "Як видно в ОС"]
    row_ys = [68, 150, 225, 300]
    row_h_each = [60, 64, 64, 68]

    for ri, (rlbl, ry) in enumerate(zip(row_labels, row_ys)):
        parts.append(text(8, ry + 20, rlbl, size=12, bold=True, color=MUTED, anchor="start"))

    for ci, cd in enumerate(cls_data):
        cx = ci * col_w + col_w/2
        # Назва класу
        parts.append(fitbox(ci*col_w + 10, row_ys[0], col_w - 20, row_h_each[0],
                            cd["name"] + "\n" + cd["full"], size=13, bold=True,
                            fill=cd["fill"], stroke=cd["color"], sw=2.5, rx=8))
        # EP-и
        parts.append(fitbox(ci*col_w + 10, row_ys[1], col_w - 20, row_h_each[1],
                            cd["ep"], size=12, fill=cd["fill"], stroke=cd["color"], sw=1.5, rx=6))
        # Дані
        parts.append(fitbox(ci*col_w + 10, row_ys[2], col_w - 20, row_h_each[2],
                            cd["data"], size=12, fill=FILL, stroke=MUTED, sw=1, rx=6))
        # ОС
        parts.append(fitbox(ci*col_w + 10, row_ys[3], col_w - 20, row_h_each[3],
                            cd["os"], size=13, bold=True, fill=cd["fill"], stroke=cd["color"], sw=2, rx=8))

    # Підпис
    bfrag, _, _ = textbox(W/2, H - 22,
                          "Набір EP у кожному класі визначений стандартом і закладений у дескриптори (→§4.12.4)",
                          size=12, fill=FILL, stroke=MUTED, sw=1, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-5-2-three-classes.svg'), W, H, *parts)
    print("fig-r12-5-2-three-classes.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.5.3 — Композитний пристрій: кілька класів-інтерфейсів
# ══════════════════════════════════════════════════════════════════════════════
def fig_1253_composite():
    W, H = 760, 380
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.5.3. Композитний пристрій: один роз'єм — кілька класів",
                      size=15, bold=True))

    # Пристрій (велика коробка)
    px, py, pw, ph = 240, 60, 280, 230
    parts.append(rect(px, py, pw, ph, fill="#f8f9fa", stroke=LINE, sw=2, rx=12))
    parts.append(text(px + pw/2, py + 22, "Один фізичний пристрій", size=13, bold=True, color=INK))
    parts.append(text(px + pw/2, py + 40, "(один USB-з'єднувач)", size=11, color=MUTED))

    # Interface 0 — CDC
    parts.append(rect(px + 18, py + 56, pw - 36, 70, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    parts.append(text(px + pw/2, py + 80, "Interface 0: CDC", size=13, bold=True, color=FIELD))
    parts.append(text(px + pw/2, py + 100, "bulk-IN/OUT + interrupt", size=11, color=MUTED))
    parts.append(text(px + pw/2, py + 118, "→ COM-лог / Serial", size=11, color=FIELD))

    # Interface 1 — HID
    parts.append(rect(px + 18, py + 140, pw - 36, 70, fill="#fef9ec", stroke="#e67e22", sw=2, rx=8))
    parts.append(text(px + pw/2, py + 163, "Interface 1: HID", size=13, bold=True, color="#e67e22"))
    parts.append(text(px + pw/2, py + 183, "interrupt-IN (звіти)", size=11, color=MUTED))
    parts.append(text(px + pw/2, py + 201, "→ Макро-пад / клавіатура", size=11, color="#e67e22"))

    # ОС бачить два драйвери
    os_x, os_y = 600, 90
    parts.append(rect(os_x, os_y, 140, 56, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    parts.append(text(os_x + 70, os_y + 22, "CDC драйвер", size=12, bold=True, color=FIELD))
    parts.append(text(os_x + 70, os_y + 40, "(COM-порт)", size=11, color=MUTED))

    parts.append(rect(os_x, os_y + 70, 140, 56, fill="#fef9ec", stroke="#e67e22", sw=1.5, rx=6))
    parts.append(text(os_x + 70, os_y + 92, "HID драйвер", size=12, bold=True, color="#e67e22"))
    parts.append(text(os_x + 70, os_y + 110, "(клавіатура)", size=11, color=MUTED))

    # Стрілки
    parts.append(arrow(px + pw, py + 91, os_x, os_y + 28, color=FIELD, sw=1.8))
    parts.append(arrow(px + pw, py + 175, os_x, os_y + 98, color="#e67e22", sw=1.8))

    # Лінія від USB роз'єму (зліва)
    usb_x = 60
    parts.append(rect(usb_x, py + 100, 80, 50, fill="#eaf0fd", stroke=NEG, sw=2, rx=6))
    parts.append(text(usb_x + 40, py + 128, "USB\nкабель", size=12, bold=True, color=NEG))
    parts.append(arrow(usb_x + 80, py + 125, px, py + 125, color=NEG, sw=2))

    # Підсумок
    bfrag, _, _ = textbox(W/2, H - 22,
                          "ОС вантажить два незалежні драйвери на один фізичний пристрій (→§4.12.1)",
                          size=12, fill=FILL, stroke=LINE, sw=1, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-5-3-composite.svg'), W, H, *parts)
    print("fig-r12-5-3-composite.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.6.1 — Три способи мати USB на ESP32
# ══════════════════════════════════════════════════════════════════════════════
def fig_1261_three_usb_paths():
    W, H = 820, 440
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.6.1. Три способи мати USB на ESP32 і що кожен дає",
                      size=15, bold=True))

    paths_data = [
        {
            "title": "1. Зовнішній UART-міст",
            "chips": "Класичний ESP32\nбудь-який варіант",
            "chain": ["ESP32", "→ UART →", "CP210x / CH340", "→ USB →", "USB-CDC"],
            "color": "#e67e22", "fill": "#fef9ec",
            "note": "Просто й дешево\nАле: лише Serial, не справжній USB",
        },
        {
            "title": "2. Нативний USB-OTG",
            "chips": "ESP32-S2 / S3",
            "chain": ["ESP32-S2/S3", "→ USB FS PHY →", "USB роз'єм"],
            "color": FIELD, "fill": "#eafaf1",
            "note": "Справжній USB 2.0 FS\nCDC / HID / MSC / host",
        },
        {
            "title": "3. USB-Serial-JTAG",
            "chips": "S3, C3, C6 (вбудований)",
            "chain": ["ESP32-S3/C3/C6", "→ USB-Serial-JTAG →", "CDC + JTAG"],
            "color": NEG, "fill": "#eaf0fd",
            "note": "З коробки: прошивка + лог\nФіксована функція",
        },
    ]

    row_h = 108
    start_y = 70

    for pi, pd in enumerate(paths_data):
        ry = start_y + pi * row_h
        parts.append(rect(18, ry, W - 36, row_h - 8, fill=pd["fill"], stroke=pd["color"], sw=2, rx=10))
        parts.append(text(24, ry + 22, pd["title"], size=14, bold=True, color=pd["color"], anchor="start"))
        parts.append(text(24, ry + 40, pd["chips"], size=11, color=MUTED, anchor="start"))

        # Ланцюжок
        chain_x = 250
        for ci, seg in enumerate(pd["chain"]):
            cx = chain_x + ci * 120
            if "→" in seg:
                parts.append(text(cx, ry + 55, seg, size=12, color=MUTED))
            else:
                bfrag = fitbox(cx - 52, ry + 38, 104, 34, seg, size=11, bold=True,
                               fill=BG, stroke=pd["color"], sw=1.5, rx=5)
                parts.append(bfrag)

        # Примітка
        parts.append(mtext(W - 24, ry + 50, pd["note"], size=11, color=pd["color"], anchor="end"))

    # Підсумок
    bfrag, _, _ = textbox(W/2, H - 22,
                          "Класичний ESP32 не має свого USB — лише через зовнішній міст (→§4.2.5)",
                          size=12, bold=True, fill=FILL, stroke=LINE, sw=1.2, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-6-1-three-usb-paths.svg'), W, H, *parts)
    print("fig-r12-6-1-three-usb-paths.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.6.2 — Матриця сімейства ESP32 × можливості USB
# ══════════════════════════════════════════════════════════════════════════════
def fig_1262_family_usb_matrix():
    W, H = 820, 360
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.6.2. Матриця сімейства ESP32 × можливості USB",
                      size=15, bold=True))

    chips = ["ESP32\n(класич.)", "ESP32-S2", "ESP32-S3", "ESP32-C3", "ESP32-C6"]
    cols_hdr = ["Зовн. UART-міст", "USB-Serial-JTAG", "Native OTG device", "Native OTG host"]
    matrix = [
        # міст   JTAG    dev    host
        [True,   False,  False, False],  # ESP32 класич.
        [True,   False,  True,  True],   # S2
        [True,   True,   True,  True],   # S3
        [True,   True,   False, False],  # C3
        [True,   True,   False, False],  # C6
    ]

    col_x0 = 180
    col_w  = 145
    row_h  = 52
    start_y = 68

    # Заголовки стовпців
    for ci, ch in enumerate(cols_hdr):
        cx = col_x0 + ci * col_w + col_w/2
        parts.append(mtext(cx, start_y - 12, ch, size=11, bold=True, color=INK))

    # Рядки
    for ri, (chip, row_vals) in enumerate(zip(chips, matrix)):
        ry = start_y + ri * row_h
        bg = FILL if ri % 2 == 0 else BG
        parts.append(rect(18, ry, W - 36, row_h - 2, fill=bg, stroke="none", sw=0, rx=4))
        parts.append(mtext(col_x0 - 16, ry + row_h/2 - 2, chip, size=12, bold=True, color=INK, anchor="end"))

        for ci, val in enumerate(row_vals):
            cx = col_x0 + ci * col_w + col_w/2
            cy = ry + row_h/2
            if val:
                parts.append(circle(cx, cy, 14, fill="#eafaf1", stroke=FIELD, sw=2))
                parts.append(text(cx, cy + 5, "✓", size=14, bold=True, color=FIELD))
            else:
                parts.append(circle(cx, cy, 14, fill="#fdecea", stroke=MUTED, sw=1))
                parts.append(text(cx, cy + 5, "—", size=14, color=MUTED))

    # Підпис
    bfrag, _, _ = textbox(W/2, H - 22,
                          "OTG host і довільний клас — лише S2/S3 (→§4.12.8)",
                          size=12, bold=True, fill="#fdecea", stroke=POS, sw=1.5, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-6-2-family-usb-matrix.svg'), W, H, *parts)
    print("fig-r12-6-2-family-usb-matrix.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.7.1 — Бюджет струму з шини
# ══════════════════════════════════════════════════════════════════════════════
def fig_1271_current_budget():
    W, H = 820, 420
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.7.1. Бюджет струму з шини: до/після енумерації і USB-C",
                      size=15, bold=True))

    # Вісь часу
    ax0, ax1, ay = 60, 760, 320
    parts.append(arrow(ax0, ay, ax1, ay, color=INK, sw=2))
    parts.append(text(ax1 + 14, ay + 5, "час", size=13, color=MUTED, anchor="start"))

    # Сходинки дозволеного струму
    steps = [
        (ax0,      280, ax0 + 220,  280, "До енумерації: 100 мА\n(1 unit)", "#e67e22"),
        (ax0 + 220, 210, ax0 + 540, 210, "Після SET_CONF: до 500 мА\n(USB 2.0)", FIELD),
        (ax0 + 540, 140, ax1,        140, "USB-C дефолт: 3 А\n(через CC резистори)", NEG),
    ]

    for (x1, y1, x2, y2, lbl, col) in steps:
        parts.append(line(x1, y1, x2, y2, color=col, sw=3.5))
        parts.append(line(x2, y1, x2, y2, color=col, sw=2, dash="4,3"))
        bfrag, _, _ = textbox((x1 + x2)/2, y1 - 30, lbl, size=11, bold=True,
                              fill=BG, stroke=col, sw=1.5, pad=8)
        parts.append(bfrag)

    # Профіль ESP32 (пунктир)
    profile_pts = [
        (ax0,      305),  # під'єднано — сон
        (ax0 + 100, 305),
        (ax0 + 100, 235),  # Wi-Fi сплеск
        (ax0 + 180, 235),
        (ax0 + 180, 290),
        (ax0 + 220, 290),  # після конфігурації
        (ax0 + 220, 220),
        (ax0 + 380, 220),
        (ax0 + 380, 258),
        (ax0 + 540, 258),
    ]
    path_d = "M " + " L ".join("%.1f,%.1f" % (x, y) for x, y in profile_pts)
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="7,4"/>'
                 % (path_d, "#c0392b"))
    parts.append(text(ax0 + 290, 242, "ESP32: сон 20 мА, Wi-Fi-пік ~250 мА", size=11, color="#c0392b"))

    # Мітки осі Y
    for (ma, lbl) in [(300, "100 мА"), (205, "500 мА"), (145, "3 А"), (ay + 6, "0")]:
        parts.append(line(ax0 - 5, ma, ax0 + 5, ma, color=MUTED, sw=1))
        parts.append(text(ax0 - 8, ma + 4, lbl, size=11, color=MUTED, anchor="end"))

    # Момент SET_CONFIGURATION
    sc_x = ax0 + 220
    parts.append(line(sc_x, 150, sc_x, ay, color=MUTED, sw=1, dash="4,3"))
    parts.append(text(sc_x, ay + 18, "SET_CONF", size=10, color=MUTED))

    # Підсумок
    bfrag, _, _ = textbox(W/2, H - 22,
                          "До енумерації — лише 100 мА: важкий старт планувати після configured",
                          size=12, bold=True, fill="#fef9ec", stroke="#e67e22", sw=2, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-7-1-current-budget.svg'), W, H, *parts)
    print("fig-r12-7-1-current-budget.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.7.2 — Шлях живлення VBUS → LDO → чип
# ══════════════════════════════════════════════════════════════════════════════
def fig_1272_vbus_ldo_chip():
    W, H = 820, 340
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.7.2. Шлях живлення: VBUS 5 В → LDO → 3.3 В чипа",
                      size=15, bold=True))

    nodes = [
        (80,  160, "USB\nроз'єм\nVBUS\n5 В",   "#c0392b", "#fdecea"),
        (230, 160, "Кабель\n(опір ~0.2 Ом)",   MUTED,     FILL),
        (390, 160, "Вхідний\nконденсатор\n(inrush)", "#8e44ad", "#f5eef8"),
        (560, 160, "LDO\n3.3 В",               "#27ae60", "#eafaf1"),
        (720, 160, "ESP32\n3.3 В",             NEG,       "#eaf0fd"),
    ]

    node_w, node_h = 110, 90

    for i, (nx, ny, lbl, col, fill) in enumerate(nodes):
        parts.append(rect(nx - node_w/2, ny - node_h/2, node_w, node_h, fill=fill, stroke=col, sw=2, rx=8))
        parts.append(mtext(nx, ny, lbl, size=11, color=col, bold=False))
        if i < len(nodes) - 1:
            nx2 = nodes[i+1][0]
            parts.append(arrow(nx + node_w/2 + 2, ny, nx2 - node_w/2 - 2, ny, color=MUTED, sw=2))

    # Вектор просадки напруги (над кабелем)
    parts.append(text(230, 100, "просадка ≈ I · R_cable", size=11, color=MUTED, italic=True))

    # Точка brownout
    bx, by = 560, 115
    parts.append(circle(bx, by, 10, fill="#fdecea", stroke=POS, sw=2))
    parts.append(text(bx, by + 4, "!", size=12, bold=True, color=POS))
    parts.append(text(bx + 14, by - 14, "brownout → ресет МК", size=11, color=POS, anchor="start"))
    parts.append(text(bx + 14, by,      "(якщо VIN просів нижче порога, →§4.1.8)", size=10, color=MUTED, anchor="start"))

    # Inrush пояснення
    bfrag, _, _ = textbox(390, 265,
                          "Inrush: при підключенні C заряджається → стрибок струму → \"іскра\" або просадка",
                          size=11, fill=FILL, stroke="#8e44ad", sw=1, pad=8)
    parts.append(bfrag)

    # Wi-Fi пік
    bfrag2, _, _ = textbox(660, H - 26,
                           "Wi-Fi пік ~250 мА\nможе \"провалити\" слабкий порт / кабель",
                           size=11, fill="#eafaf1", stroke=FIELD, sw=1.2, pad=8)
    parts.append(bfrag2)

    render(out('fig-r12-7-2-vbus-ldo-chip.svg'), W, H, *parts)
    print("fig-r12-7-2-vbus-ldo-chip.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.8.1 — Перевертання ролей: device ↔ host
# ══════════════════════════════════════════════════════════════════════════════
def fig_1281_roles_swapped():
    W, H = 820, 400
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.8.1. Перевертання ролей: ESP32 як device і як host",
                      size=15, bold=True))

    # ── Ліва половина: ESP32 як device ──
    lw = W/2 - 20
    parts.append(rect(10, 60, lw - 10, H - 90, fill="#fef9ec", stroke="#e67e22", sw=1.5, rx=10))
    parts.append(text(lw/2 + 10, 82, "Device mode (§4.12.1–4.12.7)", size=13, bold=True, color="#e67e22"))

    # ПК (хост)
    parts.append(rect(30, 110, 120, 70, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    parts.append(text(90, 150, "ПК\n(хост)", size=13, bold=True, color=NEG))
    # ESP32 device
    parts.append(rect(230, 110, 140, 70, fill="#fef9ec", stroke="#e67e22", sw=2, rx=8))
    parts.append(text(300, 150, "ESP32\n(device)", size=13, bold=True, color="#e67e22"))
    # Стрілки
    parts.append(arrow(150, 140, 228, 140, color=NEG, sw=2))
    parts.append(('<line x1="228" y1="162" x2="150" y2="162" stroke="%s" '
                  'stroke-width="1.8" stroke-dasharray="6,3" marker-end="url(#arrow)"/>' % "#e67e22"))
    parts.append(text(189, 132, "запит", size=10, color=NEG))
    parts.append(text(189, 175, "відповідь", size=10, color="#e67e22"))

    # Характеристика
    bfrag = fitbox(20, 215, lw - 20, 56,
                   "Простіше: прошивка реактивна\nМало коду, без арбітражу, без живлення VBUS",
                   size=12, fill="#fef9ec", stroke="#e67e22", sw=1, rx=6)
    parts.append(bfrag)

    # ── Права половина: ESP32 як host ──
    rx2 = W/2 + 10
    parts.append(rect(rx2, 60, lw - 10, H - 90, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=10))
    parts.append(text(rx2 + (lw - 10)/2, 82, "Host mode (§4.12.8, лише S2/S3)", size=13, bold=True, color=FIELD))

    # ESP32 host
    parts.append(rect(rx2 + 20, 110, 140, 70, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    parts.append(text(rx2 + 90, 150, "ESP32-S3\n(host)", size=13, bold=True, color=FIELD))
    # флешка/клавіатура
    parts.append(rect(rx2 + 230, 110, 120, 70, fill=FILL, stroke=MUTED, sw=2, rx=8))
    parts.append(text(rx2 + 290, 150, "флешка /\nклавіатура", size=12, color=MUTED))
    # Стрілки (тепер ESP32 ініціює)
    parts.append(arrow(rx2 + 162, 138, rx2 + 228, 138, color=FIELD, sw=2))
    parts.append(('<line x1="%.1f" y1="162" x2="%.1f" y2="162" stroke="%s" '
                  'stroke-width="1.8" stroke-dasharray="6,3" marker-end="url(#arrow)"/>'
                  % (rx2 + 228, rx2 + 162, MUTED)))

    # Характеристика
    bfrag2 = fitbox(rx2 + 2, 215, lw - 12, 56,
                    "Складніше: МК сам енумерує, подає VBUS, розбирає дескриптори\nБільше коду, пам'яті й живлення",
                    size=11, fill="#eafaf1", stroke=FIELD, sw=1, rx=6)
    parts.append(bfrag2)

    # Підпис
    bfrag3, _, _ = textbox(W/2, H - 22,
                           "Складність USB живе у хості — саме тому бути device посильно для МК",
                           size=12, bold=True, fill=FILL, stroke=LINE, sw=1.2, pad=10)
    parts.append(bfrag3)

    render(out('fig-r12-8-1-roles-swapped.svg'), W, H, *parts)
    print("fig-r12-8-1-roles-swapped.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.8.2 — OTG: контакт ID визначає роль
# ══════════════════════════════════════════════════════════════════════════════
def fig_1282_otg_id_pin():
    W, H = 760, 360
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.8.2. OTG: контакт ID вирішує, хто host, а хто device",
                      size=15, bold=True))

    cases = [
        {
            "title": "ID плаваючий → Device",
            "id_lbl": "ID = плаває\n(не підключений)",
            "role": "ESP32 = DEVICE\nне подає VBUS",
            "color": "#e67e22", "fill": "#fef9ec",
            "cx": 200,
        },
        {
            "title": "ID заземлений → Host",
            "id_lbl": "ID заземлений\n(OTG-кабель)",
            "role": "ESP32 = HOST\nподає VBUS 5 В",
            "color": FIELD, "fill": "#eafaf1",
            "cx": 560,
        },
    ]

    for cd in cases:
        cx = cd["cx"]
        parts.append(text(cx, 64, cd["title"], size=14, bold=True, color=cd["color"]))

        # Схема роз'єму (5 контактів)
        pin_names = ["VBUS", "D−", "D+", "ID", "GND"]
        for pi, pn in enumerate(pin_names):
            py = 90 + pi * 30
            col = POS if pn == "VBUS" else (NEG if pn == "D-" else (FIELD if pn == "D+" else
                  ("#c0392b" if pn == "ID" else "#555")))
            parts.append(circle(cx - 48, py, 10, fill=col, stroke=col, sw=1))
            parts.append(text(cx - 18, py + 5, pn, size=12, color=col, anchor="start"))

        # ID-контакт — підключення або плаває
        id_py = 90 + 3 * 30
        if "плаваючий" in cd["id_lbl"]:
            parts.append(text(cx + 60, id_py + 5, "↑ (плаває)", size=11, color=MUTED, anchor="start"))
        else:
            parts.append(line(cx - 48, id_py + 10, cx - 48, id_py + 30, color="#c0392b", sw=2))
            parts.append(line(cx - 60, id_py + 30, cx - 36, id_py + 30, color="#c0392b", sw=2))
            parts.append(text(cx - 48, id_py + 45, "GND", size=10, color="#c0392b"))

        # Роль
        bfrag, _, _ = textbox(cx, 280, cd["role"], size=14, bold=True,
                              fill=cd["fill"], stroke=cd["color"], sw=2, pad=12)
        parts.append(bfrag)

    # Примітка
    parts.append(text(W/2, H - 22,
                      "Деталі OTG-кабелів і host-модулів — 🔌 r12-s8-c-otg.md · Host лише на S2/S3 (→§4.12.6)",
                      size=11, color=MUTED))

    render(out('fig-r12-8-2-otg-id-pin.svg'), W, H, *parts)
    print("fig-r12-8-2-otg-id-pin.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.12.8.3 — МК-host: читати флешку (MSC) і клавіатуру (HID)
# ══════════════════════════════════════════════════════════════════════════════
def fig_1283_host_use_cases():
    W, H = 820, 380
    parts = []

    parts.append(text(W/2, 28, "Рис. 4.12.8.3. Найчастіші ролі МК-хоста: флешка (MSC) і клавіатура (HID)",
                      size=15, bold=True))

    # ESP32-S3 у центрі
    cx, cy = W/2, 185
    parts.append(rect(cx - 90, cy - 50, 180, 100, fill="#eafaf1", stroke=FIELD, sw=2.5, rx=12))
    parts.append(text(cx, cy - 18, "ESP32-S3", size=16, bold=True, color=FIELD))
    parts.append(text(cx, cy + 4,  "(USB HOST)", size=13, bold=True, color=FIELD))
    parts.append(text(cx, cy + 24, "Native OTG · Full-Speed", size=11, color=MUTED))

    # USB флешка (ліворуч)
    fx, fy = 130, 185
    parts.append(rect(fx - 90, fy - 46, 180, 92, fill="#fef9ec", stroke="#e67e22", sw=2, rx=10))
    parts.append(text(fx, fy - 18, "USB-флешка", size=14, bold=True, color="#e67e22"))
    parts.append(text(fx, fy + 4,  "Клас MSC (→§4.12.5)", size=11, color=MUTED))
    parts.append(text(fx, fy + 24, "лог / оновлення", size=11, color="#e67e22"))

    parts.append(arrow(fx + 90 + 4, fy, cx - 90 - 4, cy, color="#e67e22", sw=2))
    parts.append(text((fx + 90 + cx - 90)/2, fy - 16, "bulk-IN/OUT", size=11, color=MUTED))

    # USB клавіатура (праворуч)
    kx, ky = 680, 185
    parts.append(rect(kx - 90, ky - 46, 180, 92, fill="#eaf0fd", stroke=NEG, sw=2, rx=10))
    parts.append(text(kx, ky - 18, "USB-клавіатура", size=14, bold=True, color=NEG))
    parts.append(text(kx, ky + 4,  "Клас HID (→§4.12.5)", size=11, color=MUTED))
    parts.append(text(kx, ky + 24, "ввід без матриці (→§4.4.8)", size=11, color=NEG))

    parts.append(arrow(kx - 90 - 4, ky, cx + 90 + 4, cy, color=NEG, sw=2))
    parts.append(text((kx - 90 + cx + 90)/2, ky - 16, "interrupt-IN", size=11, color=MUTED))

    # VBUS
    parts.append(text(cx, cy - 70, "ESP32 подає VBUS 5 В ↕ (потрібне зовнішнє 5 В джерело, →§4.12.7)",
                      size=11, color="#c0392b", italic=True))

    # Обмеження
    bfrag, _, _ = textbox(W/2, H - 24,
                          "Обмеження host-режиму: Full-Speed, обмежені класи, немає повного хаб-стеку",
                          size=12, fill=FILL, stroke=MUTED, sw=1, pad=10)
    parts.append(bfrag)

    render(out('fig-r12-8-3-host-use-cases.svg'), W, H, *parts)
    print("fig-r12-8-3-host-use-cases.svg — OK")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # 4.12.1
    fig_1211_host_device_roles()
    fig_1212_usb_tree()
    fig_1213_enum_count()
    # 4.12.2
    fig_1221_four_wires()
    fig_1222_differential()
    fig_1223_pullup_speed()
    fig_1224_speeds_table()
    # 4.12.3
    fig_1231_enum_sequence()
    fig_1232_descriptor_tree()
    fig_1233_device_descriptor_bytes()
    # 4.12.4
    fig_1241_endpoints()
    fig_1242_frames_polling()
    fig_1243_transfer_types()
    fig_1244_mouse_polling_rate()
    # 4.12.5
    fig_1251_class_driver_match()
    fig_1252_three_classes()
    fig_1253_composite()
    # 4.12.6
    fig_1261_three_usb_paths()
    fig_1262_family_usb_matrix()
    # 4.12.7
    fig_1271_current_budget()
    fig_1272_vbus_ldo_chip()
    # 4.12.8
    fig_1281_roles_swapped()
    fig_1282_otg_id_pin()
    fig_1283_host_use_cases()
    print("\nУсі фігури розділу 4.12 згенеровано.")
