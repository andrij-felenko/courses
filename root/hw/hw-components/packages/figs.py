# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BROWN = "#b5732e"   # мідь / припій
COPPER = "#c9923f"
DARK = "#3a3a3a"    # корпус деталі


# ── tht-vs-smd: дві родини в розрізі плати ────────────────────────────────────
# Ідея: THT прошиває плату й паяється знизу — галтель тримає й контачить водночас;
# SMD лежить на майданчиках і паяється з того ж боку. Видно, чому паяльник легко
# заходить у THT і чому в SMD усе вирішує крок виводів.

def fig_tht_vs_smd():
    W, H = 720, 360
    p = []
    board_y, board_h = 250, 24          # розріз плати

    # ── ЛІВА половина: THT ──
    lx = 180
    p.append(text(lx, 64, "THT — крізь дірку", size=15, color=NEG, bold=True))
    p.append(text(lx, 84, "(through-hole)", size=11, color=MUTED, italic=True))
    p.append(rect(60, board_y, 240, board_h, fill="#efe6d6", stroke=BROWN, sw=1.4, rx=0))
    # корпус деталі
    p.append(rect(lx - 60, 108, 120, 56, fill="#e9eefb", stroke=NEG, sw=1.8))
    p.append(text(lx, 142, "корпус", size=12, color=INK))
    # два виводи прошивають плату
    for vx in (lx - 34, lx + 34):
        p.append(line(vx, 164, vx, board_y + board_h + 30, color=INK, sw=3))
        # металізований отвір
        p.append(rect(vx - 6, board_y - 1, 12, board_h + 2, fill=BG, stroke=BROWN, sw=1.3, rx=0))
        # галтель припою знизу
        p.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="#d8d8d8" stroke="%s" stroke-width="1.3"/>'
                 % (vx - 13, board_y + board_h + 26, vx, board_y + board_h + 4,
                    vx + 13, board_y + board_h + 26, MUTED))
    p.append(text(lx, board_y + board_h + 52, "припій знизу: тримає й проводить",
                  size=11, color=FIELD))
    p.append(text(lx, board_y + board_h + 70, "паяльник заходить вільно",
                  size=11, color=NEG, bold=True))

    # ── ПРАВА половина: SMD ──
    rx = 540
    p.append(text(rx, 64, "SMD — на поверхню", size=15, color=POS, bold=True))
    p.append(text(rx, 84, "(surface-mount)", size=11, color=MUTED, italic=True))
    p.append(rect(420, board_y, 240, board_h, fill="#efe6d6", stroke=BROWN, sw=1.4, rx=0))
    # майданчики на поверхні (отворів немає)
    for vx in (rx - 56, rx + 56):
        p.append(rect(vx - 22, board_y - 6, 44, 7, fill=COPPER, stroke=BROWN, sw=1.2, rx=0))
    # корпус лежить на майданчиках
    p.append(rect(rx - 70, board_y - 56, 140, 50, fill="#fbecec", stroke=POS, sw=1.8))
    p.append(text(rx, board_y - 28, "корпус", size=12, color=INK))
    # виводи-крила вниз на майданчики
    p.append(line(rx - 70, board_y - 12, rx - 56, board_y - 4, color=INK, sw=3))
    p.append(line(rx + 70, board_y - 12, rx + 56, board_y - 4, color=INK, sw=3))
    p.append(text(rx, board_y + board_h + 24, "усе паяння — згори, поряд із сусідами",
                  size=11, color=FIELD))
    p.append(text(rx, board_y + board_h + 44, "отворів немає; крок виводів вирішує все",
                  size=11, color=POS, bold=True))

    # роздільник
    p.append(line(360, 100, 360, 330, color="#e0e0e0", sw=1.4, dash="5 5"))

    render(os.path.join(OUT, "tht-vs-smd.svg"), W, H, *p,
           title="Дві родини монтажу в розрізі плати")


# ── solder-ladder: сходинка ручного паяння за кроком виводів ──────────────────
# Ідея: три SMD-корпуси шикуються за одним числом — кроком виводів + чи назовні.
# SOT-23 і SOIC (виводи назовні, крок ≥ ~0.95 мм) — паяльник; QFN (під корпусом,
# 0.4–0.5 мм) — лише фен/піч/паста.

def fig_solder_ladder():
    W, H = 760, 380
    p = []

    # вісь складності згори
    p.append(arrow(70, 70, 690, 70, color=INK, sw=1.8))
    p.append(text(70, 56, "крок великий, виводи назовні — легко",
                  size=11, color=FIELD, anchor="start"))
    p.append(text(690, 56, "крок дрібний, виводи сховані — важко",
                  size=11, color=POS, anchor="end"))

    cards = [
        # x, заголовок, рядки, колір рамки, заливка, інструмент, колір інструм.
        (60,  "SOT-23", ["виводи назовні", "крок ≈ 0.95 мм", "транзистор, регулятор"],
         INK, "#eef6ef", "паяльник", FIELD),
        (290, "SOIC",   ["«крила» обабіч", "крок 1.27 мм", "ОП, логіка, пам'ять"],
         INK, "#eef6ef", "паяльник", FIELD),
        (520, "QFN",    ["майданчики ПІД корпусом", "крок 0.4–0.5 мм", "МК, радіочипи"],
         INK, "#fbecec", "фен / піч", POS),
    ]
    cw, cy, ch = 190, 100, 220
    for cx, head, rows, col, fill, tool, tcol in cards:
        p.append(rect(cx, cy, cw, ch, fill=fill, stroke=col, sw=1.8, rx=10))
        p.append(text(cx + cw / 2, cy + 30, head, size=18, color=INK, bold=True))
        # схема корпусу
        mx = cx + cw / 2
        if head == "SOT-23":
            p.append(rect(mx - 26, cy + 48, 52, 30, fill=DARK, stroke=INK, sw=1.3, rx=3))
            for dy in (cy + 56, cy + 70):
                p.append(line(mx - 26, dy, mx - 42, dy, color=INK, sw=2.6))
            p.append(line(mx + 26, cy + 63, mx + 42, cy + 63, color=INK, sw=2.6))
        elif head == "SOIC":
            p.append(rect(mx - 28, cy + 46, 56, 36, fill=DARK, stroke=INK, sw=1.3, rx=3))
            for i in range(4):
                dy = cy + 52 + i * 8
                p.append(line(mx - 28, dy, mx - 44, dy, color=INK, sw=2.2))
                p.append(line(mx + 28, dy, mx + 44, dy, color=INK, sw=2.2))
            p.append(circle(mx - 20, cy + 53, 2.2, fill=INK, stroke=INK, sw=1))
        else:  # QFN — майданчики під корпусом + центральний thermal pad
            p.append(rect(mx - 28, cy + 46, 56, 40, fill=DARK, stroke=INK, sw=1.3, rx=4))
            for i in range(4):
                dy = cy + 52 + i * 9
                p.append(rect(mx - 34, dy, 7, 5, fill=COPPER, stroke=BROWN, sw=1, rx=0))
                p.append(rect(mx + 27, dy, 7, 5, fill=COPPER, stroke=BROWN, sw=1, rx=0))
            p.append(rect(mx - 12, cy + 56, 24, 20, fill="#4a4a4a", stroke=MUTED, sw=1, rx=3))
        # рядки опису
        for i, r in enumerate(rows):
            p.append(text(cx + 14, cy + 116 + i * 20, "• " + r, size=11.5, color=DARK, anchor="start"))
        # бирка інструмента
        p.append(rect(cx + 20, cy + 178, cw - 40, 28, fill=BG, stroke=tcol, sw=1.8, rx=6))
        p.append(text(cx + cw / 2, cy + 197, "→ " + tool, size=13, color=tcol, bold=True))

    # підсумок
    p.append(line(60, 348, 710, 348, color="#e4e4e4", sw=1.4))
    p.append(text(60, 370, "Поки крок ≥ ~0.8 мм і виводи назовні — паяльник, флюс, обплетення. "
                           "Під корпусом (QFN, BGA) — лише розплав знизу.",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "solder-ladder.svg"), W, H, *p,
           title="Сходинка ручного паяння: усе вирішує крок виводів")


# ── chip-sizes: типорозміри дрібних SMD і як читати код ───────────────────────
# Ідея: код 0402/0603/0805 — це габарит у сотих частках дюйма (imperial). Покажемо
# реальний масштаб трьох прямокутників і розшифруємо число, попередивши про пастку
# «imperial проти metric».

def fig_chip_sizes():
    W, H = 700, 330
    p = []
    base_y = 150                      # спільна нижня лінія прямокутників

    # масштаб: 1 мм = px; 0805 = 2.0×1.25, 0603 = 1.6×0.8, 0402 = 1.0×0.5
    scale = 70
    sizes = [
        ("0402", 1.0, 0.5, 150),
        ("0603", 1.6, 0.8, 350),
        ("0805", 2.0, 1.25, 560),
    ]
    for code, mm_l, mm_w, cx in sizes:
        w = mm_l * scale
        h = mm_w * scale
        x = cx - w / 2
        y = base_y - h
        p.append(rect(x, y, w, h, fill="#eef4ff", stroke=NEG, sw=1.8, rx=3))
        # металізовані торці
        p.append(rect(x, y, w * 0.18, h, fill=COPPER, stroke=BROWN, sw=1, rx=0))
        p.append(rect(x + w * 0.82, y, w * 0.18, h, fill=COPPER, stroke=BROWN, sw=1, rx=0))
        p.append(text(cx, base_y + 24, code, size=16, color=INK, bold=True))
        p.append(text(cx, base_y + 44, "%.1f × %.1f мм" % (mm_l, mm_w), size=12, color=MUTED))

    # розшифровка коду під фігурою
    p.append(line(60, base_y + 70, 640, base_y + 70, color="#e4e4e4", sw=1.4))
    p.append(text(W / 2, base_y + 96,
                  "Код = габарит у сотих частках дюйма: 0603 → 0.06″ × 0.03″ ≈ 1.6 × 0.8 мм.",
                  size=12, color=INK))
    p.append(text(W / 2, base_y + 118,
                  "Пастка: imperial 0402 (1.0×0.5) ≠ metric 0402 (0.4×0.2) — завжди питай, у яких одиницях.",
                  size=11, color=POS))

    render(os.path.join(OUT, "chip-sizes.svg"), W, H, *p,
           title="Типорозміри дрібних SMD: число — це габарит")


# ── mcu-package-map: чотири корпуси МК на одній осі (для вставки) ──────────────
# Ідея: DIP → QFP → QFN → BGA — контакти дрібнішають і ховаються; права частина
# осі = лише завод.

def fig_mcu_package_map():
    W, H = 720, 320
    p = []
    p.append(arrow(70, 70, 650, 70, color=INK, sw=1.8))
    p.append(text(70, 56, "у руках", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(650, 56, "лише завод", size=11, color=POS, anchor="end", bold=True))

    items = [
        (60,  "DIP", "2.54 мм", "виводи крізь плату", FIELD, "#eef6ef"),
        (230, "QFP", "0.8 / 0.5", "крила по периметру", FIELD, "#eef6ef"),
        (400, "QFN", "0.5 / 0.4", "майданчики під краєм\n+ теплова площадка", "#c97b1e", "#fdf3e6"),
        (560, "BGA", "≤0.8…0.35", "кульки під усім дном", POS, "#fbecec"),
    ]
    cw, cy, ch = 140, 100, 170
    for cx, head, pitch, desc, col, fill in items:
        p.append(rect(cx, cy, cw, ch, fill=fill, stroke=col, sw=1.8, rx=10))
        p.append(text(cx + cw / 2, cy + 28, head, size=17, color=INK, bold=True))
        mx, my = cx + cw / 2, cy + 60
        if head == "DIP":
            p.append(rect(mx - 24, my - 12, 48, 24, fill=DARK, stroke=INK, sw=1.3, rx=2))
            for i in range(3):
                dx = mx - 16 + i * 16
                p.append(line(dx, my + 12, dx, my + 26, color=INK, sw=2.6))
                p.append(line(dx, my - 12, dx, my - 26, color=INK, sw=2.6))
        elif head == "QFP":
            p.append(rect(mx - 18, my - 14, 36, 28, fill=DARK, stroke=INK, sw=1.3, rx=3))
            for i in range(4):
                d = my - 11 + i * 7
                p.append(line(mx - 18, d, mx - 30, d, color=INK, sw=1.8))
                p.append(line(mx + 18, d, mx + 30, d, color=INK, sw=1.8))
        elif head == "QFN":
            p.append(rect(mx - 20, my - 15, 40, 30, fill=DARK, stroke=INK, sw=1.3, rx=3))
            for i in range(4):
                d = my - 11 + i * 7
                p.append(rect(mx - 26, d, 5, 4, fill=COPPER, stroke=BROWN, sw=0.8, rx=0))
                p.append(rect(mx + 21, d, 5, 4, fill=COPPER, stroke=BROWN, sw=0.8, rx=0))
            p.append(rect(mx - 9, my - 8, 18, 16, fill="#4a4a4a", stroke=MUTED, sw=1, rx=2))
        else:  # BGA — сітка кульок
            p.append(rect(mx - 22, my - 16, 44, 32, fill=DARK, stroke=INK, sw=1.3, rx=3))
            for r in range(3):
                for c in range(4):
                    p.append(circle(mx - 15 + c * 10, my - 8 + r * 8, 2.6, fill=COPPER, stroke=BROWN, sw=0.8))
        p.append(text(cx + cw / 2, cy + 122, pitch, size=12, color=INK, bold=True))
        p.append(mtext(cx + cw / 2, cy + 142, desc, size=10, color=MUTED, lh=1.15))

    render(os.path.join(OUT, "mcu-package-map.svg"), W, H, *p,
           title="Чотири корпуси МК: контакти дрібнішають і ховаються")


# ── mcu-package-cross: де живе контакт, у перетині (для вставки) ───────────────
# Ідея: один погляд збоку на кожен клас — DIP крізь плату, QFP крило збоку, QFN
# майданчик + thermal pad під корпусом, BGA кулька під корпусом.

def fig_mcu_package_cross():
    W, H = 720, 340
    p = []
    cells = [
        (60,  "DIP",  NEG,  "паяй з будь-якого боку"),
        (230, "QFP",  FIELD, "крило збоку — видно й доступно"),
        (400, "QFN",  "#c97b1e", "майданчик + pad під корпусом"),
        (560, "BGA",  POS,  "кулька під корпусом — лише рентген"),
    ]
    cw, cy, ch = 140, 90, 200
    by = cy + 120                    # лінія плати в кожній клітинці
    for cx, head, col, note in cells:
        p.append(rect(cx, cy, cw, ch, fill=BG, stroke="#dcdcdc", sw=1.4, rx=8))
        p.append(text(cx + cw / 2, cy + 26, head, size=16, color=col, bold=True))
        mx = cx + cw / 2
        # плата
        p.append(rect(cx + 14, by, cw - 28, 14, fill="#efe6d6", stroke=BROWN, sw=1.2, rx=0))
        if head == "DIP":
            p.append(rect(mx - 22, by - 36, 44, 24, fill=DARK, stroke=INK, sw=1.2, rx=2))
            for dx in (mx - 12, mx + 12):
                p.append(line(dx, by - 12, dx, by + 26, color=INK, sw=2.6))
                p.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f Z" fill="#d8d8d8" stroke="%s" stroke-width="1"/>'
                         % (dx - 8, by + 24, dx, by + 14, dx + 8, by + 24, MUTED))
        elif head == "QFP":
            p.append(rect(mx - 22, by - 30, 44, 22, fill=DARK, stroke=INK, sw=1.2, rx=2))
            for sgn in (-1, 1):
                ex = mx + sgn * 22
                p.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f" fill="none" stroke="%s" stroke-width="2.4"/>'
                         % (ex, by - 22, ex + sgn * 14, by - 8, ex + sgn * 22, by - 8, INK))
                p.append(rect(mx + sgn * 30 - 6, by - 2, 12, 4, fill=COPPER, stroke=BROWN, sw=0.8, rx=0))
        elif head == "QFN":
            p.append(rect(mx - 24, by - 26, 48, 22, fill=DARK, stroke=INK, sw=1.2, rx=2))
            # периметрові майданчики
            for sgn in (-1, 1):
                p.append(rect(mx + sgn * 24 - (6 if sgn > 0 else 0), by - 6, 6, 4, fill=COPPER, stroke=BROWN, sw=0.8, rx=0))
            # центральний thermal pad + via
            p.append(rect(mx - 10, by - 6, 20, 4, fill=COPPER, stroke=BROWN, sw=0.8, rx=0))
            p.append(line(mx, by - 4, mx, by + 14, color=BROWN, sw=2.2))
            p.append(text(mx, by + 34, "thermal pad", size=9, color="#c97b1e"))
        else:  # BGA
            p.append(rect(mx - 26, by - 26, 52, 20, fill=DARK, stroke=INK, sw=1.2, rx=2))
            for c in range(4):
                bx = mx - 15 + c * 10
                p.append(circle(bx, by - 3, 3.4, fill=COPPER, stroke=BROWN, sw=0.9))
        p.append(mtext(cx + cw / 2, by + 52, note, size=9.5, color=MUTED, lh=1.15))

    render(os.path.join(OUT, "mcu-package-cross.svg"), W, H, *p,
           title="Де живе контакт: один перетин на клас")


if __name__ == "__main__":
    fig_tht_vs_smd()
    fig_solder_ladder()
    fig_chip_sizes()
    fig_mcu_package_map()
    fig_mcu_package_cross()
    print("OK: figures written to", OUT)
