# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── safe-state-actuators: найменш шкідливий вихід кожного актуатора ────────────
# Ідея: «безпечний стан» не береться з довідника — для кожного актуатора своя
# відповідь, і навіть правило «знеструмлено = безпечно» має винятки.

def fig_safe_state_actuators():
    W = 720
    rows = [
        # (актуатор, безпечний стан, знеструм.=безпека?, ok?)
        ("Мотор (DC/BLDC)",   "СТОП  (PWM duty = 0)",      "так",            True),
        ("Нагрівач",          "OFF  (реле розімкнуто)",    "так",            True),
        ("Клапан н/закритий", "ЗАКРИТО",                   "так",            True),
        ("Клапан н/відкритий","ВІДКРИТО  ← навпаки!",      "так, інша пружина", "warn"),
        ("Гальмо пружинне",   "ПРИТИСНУТО",                "так (de-energize)", True),
        ("Шасі літака",       "залежить від фази польоту", "ні  ← резерв!",  False),
    ]
    top = 76
    rh = 38
    H = top + len(rows) * rh + 56
    cx_name, cx_state, cx_de = 168, 410, 622
    p = []

    # шапка стовпців
    p.append(text(cx_name, top - 12, "Актуатор", size=12, bold=True))
    p.append(text(cx_state, top - 12, "Безпечний стан", size=12, bold=True))
    p.append(text(cx_de, top - 12, "знеструм. = безпека?", size=12, bold=True))
    p.append(line(36, top, 684, top, color=MUTED, sw=1.0))

    for i, (name, state, de, ok) in enumerate(rows):
        y = top + i * rh
        band = "#eef4ff" if i % 2 == 0 else BG
        p.append(rect(36, y, 648, rh, fill=band, stroke=MUTED, sw=0.8, rx=4))
        p.append(text(cx_name, y + rh / 2 + 4, name, size=11))
        if ok is True:
            col = FIELD
        elif ok == "warn":
            col = "#c07000"
        else:
            col = POS
        p.append(text(cx_state, y + rh / 2 + 4, state, size=11, color=col,
                      bold=(ok is not True)))
        p.append(text(cx_de, y + rh / 2 + 4, de, size=11, color=col))

    # підсумкова рамка
    by = top + len(rows) * rh + 12
    box, bw, bh = textbox(W / 2, by + 14,
                          "Безпечний стан визначає інженер під конкретну систему — не довідник.",
                          size=12, bold=True, fill="#fff3cd", stroke="#c07000", sw=2)
    p.append(box)

    render(os.path.join(OUT, "safe-state-actuators.svg"), W, H, *p,
           title="Який вихід кожного актуатора найменш шкідливий при невідомому збої")


# ── reset-glitch: вікно небезпеки від reset до ініціалізації GPIO ──────────────
# Ідея: від скидання до gpio_set_direction() ніжки в Hi-Z і можуть смикнутись;
# апаратна підтяжка тримає «OFF» весь цей час — задарма, без коду.

def fig_reset_glitch():
    W, H = 760, 330
    p = []

    # три фази часу
    phases = [
        (60,  130, "RESET\n(чіп скинуто)",     "#fdecea", POS),
        (190, 180, "BOOTLOADER\n(не наш код)",  "#fff3cd", "#c07000"),
        (370, 330, "НАШ КОД\n(ініціалізація)",  "#eafaf0", FIELD),
    ]
    band_y, band_h = 120, 80
    for x, w, lab, fill, col in phases:
        p.append(rect(x, band_y, w, band_h, fill=fill, stroke=col, sw=2))
        p.append(mtext(x + w / 2, band_y + band_h / 2 - 2, lab, size=11, color=col, bold=True))

    # верхня лінія GPIO: рвана (Hi-Z) до 360, потім чиста зелена
    import random
    random.seed(7)
    seg, x = [], 60
    py = 90
    pts_top = []
    while x <= 360:
        jitter = random.uniform(-8, 8)
        pts_top.append((x, py + jitter))
        x += 15
    for a, b in zip(pts_top, pts_top[1:]):
        p.append(line(a[0], a[1], b[0], b[1], color=POS, sw=1.5, dash="3 2"))
    p.append(text(56, 90, "GPIO\n(Hi-Z)", size=10, color=POS, anchor="end"))
    # після ініціалізації — чисто
    p.append(line(370, 95, 700, 95, color=FIELD, sw=2.5))
    p.append(text(704, 95, "OK", size=11, color=FIELD, anchor="start", bold=True))

    # «вікно небезпеки» дужка зверху
    p.append(line(60, 58, 360, 58, color=POS, sw=1.5, dash="5 3"))
    p.append(text(210, 46, "вікно небезпеки — вихід може смикнути!", size=11,
                  color=POS, anchor="middle", bold=True))

    # нижня лінія: апаратна підтяжка тримає OFF весь час
    p.append(line(60, 235, 700, 235, color=FIELD, sw=3.0))
    p.append(text(56, 235, "Апаратна\nпідтяжка\n→ «OFF»", size=10, color=FIELD,
                  anchor="end", bold=True))
    p.append(text(380, 253, "тримає безпечний рівень навіть під час reset",
                  size=10, color=FIELD, italic=True))

    p.append(text(W / 2, 312, "Прошивка під час reset мовчить — безпеку виходу дає залізо",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "reset-glitch.svg"), W, H, *p,
           title="Вікно небезпеки reset: GPIO невизначений до ініціалізації")


# ── safe-mode-layers: safe mode = живий мінімум, основна функція вимкнена ──────
# Ідея: при тяжкому збої пристрій підіймає лише те, без чого до нього не
# дістатись (зв'язок, оновлення, індикація, безпечні виходи); решта — вимкнена.

def fig_safe_mode_layers():
    W, H = 720, 360
    p = []
    cx_alive, cx_off = 200, 520
    top = 70

    p.append(text(cx_alive, top - 8, "SAFE MODE — живе", size=13, bold=True, color=FIELD))
    p.append(text(cx_off, top - 8, "вимкнено", size=13, bold=True, color=MUTED))

    alive = [
        "зв'язок для діагностики",
        "канал оновлення (OTA)",
        "індикація аварії",
        "безпечні виходи",
    ]
    off = [
        "основна функція",
        "керування актуаторами",
        "складна логіка / автоматика",
        "усе, що не рятує",
    ]
    bw, bh, gap = 280, 46, 14
    y = top + 10
    for i in range(4):
        ay = y + i * (bh + gap)
        p.append(fitbox(cx_alive - bw / 2, ay, bw, bh, alive[i], size=12,
                        fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True, color=INK))
        p.append(fitbox(cx_off - bw / 2, ay, bw, bh, off[i], size=12,
                        fill="#f3f4f5", stroke=MUTED, sw=1.2, color=MUTED))

    # роздільна вертикаль
    p.append(line(W / 2, top + 4, W / 2, y + 4 * (bh + gap) - gap, color=MUTED, sw=1.0, dash="4 4"))

    # підсумок
    by = y + 4 * (bh + gap) + 6
    box, _, _ = textbox(W / 2, by + 12,
                        "Підіймаємо рівно стільки, щоб полагодити проблему — і ні рядком більше.",
                        size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=2)
    p.append(box)

    render(os.path.join(OUT, "safe-mode-layers.svg"), W, H, *p,
           title="Safe mode: підіймається мінімум, основна функція мовчить")


if __name__ == "__main__":
    fig_safe_state_actuators()
    fig_reset_glitch()
    fig_safe_mode_layers()
    print("OK: figures written to", OUT)
