# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── three-paths: три способи дістати USB на ESP32 і що кожен дає ──────────────
# Ідея: USB на ESP32 — не одне рішення, а три різні шляхи. Зовнішній міст лишає
# стек поза чипом (лише Serial); нативний OTG робить чип повноцінним USB-вузлом
# (будь-який клас, навіть хост); USB-Serial-JTAG дає фіксований CDC+JTAG даром.
def fig_three_paths():
    W, H = 760, 430
    rows = [
        ("Зовнішній USB-UART-міст", MUTED, "#f4f6f8",
         ["ESP32", "UART", "CP2102 / CH340", "USB", "ПК: COM-порт"],
         "Стек USB живе в мості, не в чипі — лише текстовий Serial"),
        ("Нативний USB-OTG (S2 / S3)", FIELD, "#eafaf1",
         ["ESP32-S2/S3", "USB FS PHY", "роз'єм USB", "", "ПК: будь-який клас"],
         "Чип сам — USB-вузол: CDC / HID / MSC, навіть хост"),
        ("USB-Serial-JTAG (S3 / C3 / C6 / H2)", NEG, "#eaf0fd",
         ["ESP32-S3/C3/C6", "вбудований блок", "роз'єм USB", "", "ПК: COM + JTAG"],
         "З коробки: прошивка, лог і відлагодження; функція фіксована"),
    ]
    p = []
    top = 56
    rh = 112
    for i, (name, col, fill, chain, note) in enumerate(rows):
        y = top + i * rh
        p.append(rect(20, y, W - 40, rh - 14, fill=fill, stroke=col, sw=2.0, rx=10))
        p.append(text(34, y + 24, name, size=14, color=col, anchor="start", bold=True))
        # ланцюжок блоків зліва направо
        boxes = [c for c in chain if c]
        bw, gap = 118, 26
        bx = 34
        by = y + 44
        for j, label in enumerate(boxes):
            sz = fit_font(label, bw - 10, 11, bold=True)
            p.append(rect(bx, by, bw, 30, fill=BG, stroke=col, sw=1.4, rx=5))
            p.append(text(bx + bw / 2, by + 20, label, size=sz, color=INK, bold=True))
            if j < len(boxes) - 1:
                p.append(arrow(bx + bw + 3, by + 15, bx + bw + gap - 3, by + 15, color=col, sw=1.6))
            bx += bw + gap
        p.append(text(34, y + rh - 22, note, size=11, color=MUTED, anchor="start", italic=True))
    return render(os.path.join(OUT, "three-paths.svg"), W, H, *p,
                  title="Три способи дістати USB на ESP32")


# ── family-matrix: чип × можливість USB (хто що реально вміє) ─────────────────
# Ідея: рішення «який чип під задачу» = читання цієї матриці. Зелене коло —
# вміє, сіра риска — ні. Видно межу: хост лише S2/S3/P4; класичний ESP32 — лише
# через міст; C6 має ОКРЕМИЙ device-блок (TinyUSB-класи), але не хост.
def fig_family_matrix():
    cols = ["Зовн.\nміст", "USB-Serial-\nJTAG", "Нативний OTG\n(device)",
            "Окремий USB\ndevice", "OTG host"]
    rows = [
        ("ESP32 (класич.)", [1, 0, 0, 0, 0]),
        ("ESP32-S2",        [1, 0, 1, 1, 1]),
        ("ESP32-S3",        [1, 1, 1, 1, 1]),
        ("ESP32-C3",        [1, 1, 0, 0, 0]),
        ("ESP32-C6 / H2",   [1, 1, 0, 1, 0]),
        ("ESP32-P4",        [1, 1, 1, 1, 1]),
    ]
    W = 820
    left = 150
    colw = (W - left - 24) / len(cols)
    top = 92
    rh = 44
    H = top + len(rows) * rh + 56
    p = []
    # заголовки колонок
    for j, c in enumerate(cols):
        cx = left + colw * (j + 0.5)
        p.append(mtext(cx, 52, c.split("\n"), size=11, color=INK, bold=True, lh=1.2))
    # рядки
    for i, (name, cells) in enumerate(rows):
        y = top + i * rh
        if i % 2 == 0:
            p.append(rect(20, y, W - 40, rh, fill="#f4f6f8", stroke="none", sw=0, rx=4))
        p.append(text(left - 12, y + rh / 2 + 4, name, size=12, color=INK, anchor="end", bold=True))
        for j, v in enumerate(cells):
            cx = left + colw * (j + 0.5)
            cy = y + rh / 2
            if v:
                p.append(circle(cx, cy, 13, fill="#eafaf1", stroke=FIELD, sw=2.0))
                p.append(text(cx, cy + 5, "✓", size=14, color=FIELD, bold=True))
            else:
                p.append(circle(cx, cy, 13, fill="#fdecea", stroke=MUTED, sw=1.0))
                p.append(text(cx, cy + 5, "—", size=14, color=MUTED))
    # підсумкова смужка
    by = top + len(rows) * rh + 12
    note = "Хост — лише S2 / S3 / P4 · класичний ESP32 — тільки через міст · C6/H2: окремий device-блок, але не хост"
    p.append(fitbox(40, by, W - 80, 32, note, size=12, fill="#fdecea", stroke=POS, sw=1.5, bold=True))
    return render(os.path.join(OUT, "family-matrix.svg"), W, H, *p,
                  title="Чип × можливість USB: хто що реально вміє")


# ── one-cable-three-roles: один кабель, той самий S3, три ролі через стек ─────
# Ідея: залізо незмінне — змінюється лише tusb_config.h. Той самий роз'єм і ті
# самі D+/D− дають COM-порт, клавіатуру або диск — бо клас задають дескриптори.
def fig_one_cable():
    W, H = 760, 360
    p = []
    # незмінне залізо в центрі
    cx, cy = W / 2, 132
    b, bw, bh = textbox(cx, cy, ["ESP32-S3", "той самий кабель", "ті самі D+ / D−"],
                        size=13, bold=True, fill="#eafaf1", stroke=FIELD, sw=2.0, min_w=200)
    p.append(b)
    p.append(text(cx, cy - bh / 2 - 12, "Залізо незмінне", size=12, color=MUTED, italic=True))
    # три ролі знизу — різняться лише конфігом стека
    roles = [
        ("CFG_TUD_CDC = 1", "CDC", "ПК бачить COM-порт\n(логи, консоль)", NEG),
        ("CFG_TUD_HID = 1", "HID", "ПК бачить клавіатуру\n/ геймпад", POS),
        ("CFG_TUD_MSC = 1", "MSC", "ПК бачить диск\n(SD-картка)", FIELD),
    ]
    ry = 250
    slot = (W - 80) / 3
    for i, (cfg, kls, desc, col) in enumerate(roles):
        rx = 40 + slot * (i + 0.5)
        p.append(arrow(cx, cy + bh / 2 + 4, rx, ry - 44, color=col, sw=1.6))
        p.append(fitbox(rx - slot * 0.42, ry - 40, slot * 0.84, 26, cfg, size=11,
                        fill=BG, stroke=col, sw=1.3, bold=True))
        cb, cbw, cbh = textbox(rx, ry + 4, kls, size=15, bold=True, color=col,
                               fill="#ffffff", stroke=col, sw=1.8, min_w=70)
        p.append(cb)
        p.append(mtext(rx, ry + 44, desc.split("\n"), size=11, color=MUTED, lh=1.25))
    return render(os.path.join(OUT, "one-cable-three-roles.svg"), W, H, *p,
                  title="Один кабель, той самий S3 — три ролі через стек")


# ── pins-power: пастки D+/D−, GPIO19/20 і живлення USB ───────────────────────
# Ідея: дві типові поразки. Зайняв GPIO19/20 під периферію — USB не підніметься;
# а ще USB дає лише ~500 мА на 5 В, після LDO на 3.3 В сплески Wi-Fi легко
# просідають шину, тож потрібен запас по конденсаторах.
def fig_pins_power():
    W, H = 760, 340
    p = []
    # ліворуч: фіксовані виводи USB
    p.append(rect(28, 60, 330, 250, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=10))
    p.append(text(44, 84, "Виводи USB закріплені", size=13, color=INK, anchor="start", bold=True))
    pins = [
        ("D+ → GPIO20", "S2/S3: OTG і S-J"),
        ("D− → GPIO19", " те саме коло"),
        ("C6 device: D−/D+", "→ GPIO12 / GPIO13"),
    ]
    for i, (a, b) in enumerate(pins):
        y = 110 + i * 46
        p.append(rect(44, y, 150, 34, fill=BG, stroke=NEG, sw=1.4, rx=5))
        p.append(text(119, y + 22, a, size=12, color=INK, bold=True))
        p.append(text(206, y + 22, b, size=11, color=MUTED, anchor="start"))
    p.append(fitbox(44, 256, 298, 40,
                    "Зайняв ці GPIO під периферію → USB не підніметься",
                    size=11, fill="#fdecea", stroke=POS, sw=1.4, bold=True))
    # праворуч: бюджет живлення
    p.append(rect(402, 60, 330, 250, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=10))
    p.append(text(418, 84, "Бюджет живлення з USB", size=13, color=INK, anchor="start", bold=True))
    steps = [
        ("USB порт", "5 В, типово до ~500 мА"),
        ("LDO ↓", "5 В → 3.3 В, решта — у тепло"),
        ("Сплеск Wi-Fi", "піки струму просаджують шину"),
    ]
    for i, (a, b) in enumerate(steps):
        y = 110 + i * 46
        col = POS if i == 2 else NEG
        p.append(rect(418, y, 130, 34, fill=BG, stroke=col, sw=1.4, rx=5))
        p.append(text(483, y + 22, a, size=12, color=col, bold=True))
        p.append(text(560, y + 22, b, size=10, color=MUTED, anchor="start"))
    p.append(fitbox(418, 256, 298, 40,
                    "Лік: запас по С-конденсаторах на 3.3 В і 5 В",
                    size=11, fill="#eafaf1", stroke=FIELD, sw=1.4, bold=True))
    return render(os.path.join(OUT, "pins-power.svg"), W, H, *p,
                  title="Пастки: фіксовані D+/D− і бюджет живлення")


if __name__ == "__main__":
    fig_three_paths()
    fig_family_matrix()
    fig_one_cable()
    fig_pins_power()
    print("ok: three-paths, family-matrix, one-cable-three-roles, pins-power")
