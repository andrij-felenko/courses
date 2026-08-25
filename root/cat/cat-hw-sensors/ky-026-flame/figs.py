# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-026 — давач полумʼя».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Що бачить давач: полумʼя світить у ближньому ІЧ, фототранзистор ловить ────
def fig_flame_ir():
    W, H = 1080, 470
    f = [text(W / 2, 30, "Полумʼя яскраве в ближньому інфрачервоному — саме там фототранзистор чутливий",
              size=15, bold=True)]

    # --- Ліворуч: полумʼя-джерело ---
    fx, fy = 160, 230          # основа полумʼя
    flame = ('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f '
             'C %.0f %.0f, %.0f %.0f, %.0f %.0f Z" fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (fx, fy, fx - 44, fy - 60, fx - 26, fy - 150, fx, fy - 200,
                fx + 26, fy - 150, fx + 44, fy - 60, fx, fy, POS))
    f.append(flame)
    f.append(('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f '
              'C %.0f %.0f, %.0f %.0f, %.0f %.0f Z" fill="#fff6d8" stroke="none"/>'
              % (fx, fy - 4, fx - 20, fy - 46, fx - 12, fy - 110, fx, fy - 150,
                 fx + 12, fy - 110, fx + 20, fy - 46, fx, fy - 4)))
    f.append(text(fx, fy + 28, "полумʼя", size=12, bold=True, color=POS))
    f.append(text(fx, fy + 46, "гаряча сажа ≈ 1000–1500 K", size=10, color=MUTED))

    # промені: видиме (мало) і ІЧ (багато) — стрілки вправо
    def ray(y, color, sw, dash=None, lab=None):
        f.append(line(fx + 54, y, 640, y, color=color, sw=sw, dash=dash))
        f.append(arrow(620, y, 646, y, color=color, sw=sw))
        if lab:
            f.append(text(fx + 62, y - 8, lab, size=10, color=color, anchor="start", bold=True))
    ray(120, MUTED, 1.4, "3,4", "трохи видимого світла")
    ray(164, POS, 2.6, None, "багато ближнього ІЧ (760–1100 нм)")
    ray(200, POS, 2.6)
    ray(236, POS, 2.6)

    # --- Праворуч: фототранзистор ---
    px, py = 770, 176
    f.append(rect(px, py, 160, 100, fill="#f7f9fc", stroke=INK, sw=1.6, rx=12))
    f.append(circle(px + 36, py + 50, 24, fill="#111111", stroke=INK, sw=1.4))
    f.append(text(px + 36, py + 90, "чорна лінза", size=9, color=MUTED))
    f.append(text(px + 108, py + 32, "YG1006", size=12, bold=True, color=INK))
    f.append(text(px + 108, py + 52, "фото-", size=11, color=INK))
    f.append(text(px + 108, py + 68, "транзистор", size=11, color=INK))
    f.append(line(px + 26, py + 100, px + 26, py + 126, color=INK, sw=2.2))
    f.append(line(px + 52, py + 100, px + 52, py + 126, color=INK, sw=2.2))

    b, _, _ = textbox(px + 80, py + 182, "ІЧ падає на перехід →\nтранзистор відкривається дужче →\nструм крізь нього росте",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    # нижня нота — короткі рядки, щоб рамка влізла у виводок
    b, _, _ = textbox(W / 2, 438, "Чорна лінза глушить видиме, а ближній ІЧ пропускає — давач «сліпий» до кольору, зате бачить жар.\n"
                                  "Тому так само яскраво для нього світять сонце й лампа розжарення (звідси хибні спрацювання).",
                      size=10.5, fill=BG, stroke=INK)
    f.append(b)

    render(os.path.join(IMG, "flame-ir.svg"), W, H, *f)


# ── 2. Внутрішня схема KY-026: фототранзистор → дільник → LM393 → AO і DO ────────
def fig_ky026_schematic():
    W, H = 1080, 580
    f = [text(W / 2, 30, "Що всередині KY-026: фототранзистор дає напругу, LM393 порівнює її з порогом",
              size=15, bold=True)]

    bx, by, bw, bh = 70, 60, 940, 410
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.6, rx=14))
    f.append(text(bx + 14, by + 20, "плата KY-026", size=11, bold=True, color=MUTED, anchor="start"))

    # шини (лишаю поля з боків, щоб горизонтальні виходи не проходили крізь підписи шин)
    vcc_y = by + 60
    gnd_y = by + bh - 46
    rail_l, rail_r = bx + 210, bx + bw - 360
    f.append(line(rail_l, vcc_y, rail_r, vcc_y, color=POS, sw=2.2))
    f.append(text(rail_l, vcc_y - 10, "+  (VCC 3.3–5.5 В)", size=11, bold=True, color=POS, anchor="start"))
    f.append(line(rail_l, gnd_y, rail_r, gnd_y, color=NEG, sw=2.2))
    f.append(text(rail_l, gnd_y + 22, "−  (GND)", size=11, bold=True, color=NEG, anchor="start"))

    # --- ліва вітка: фототранзистор + резистор (дільник), вузол сигналу ---
    col_x = bx + 250
    node_y = (vcc_y + gnd_y) / 2
    f.append(line(col_x, vcc_y, col_x, node_y - 52, color=INK, sw=1.8))
    f.append(circle(col_x, node_y - 32, 20, fill="#111111", stroke=INK, sw=1.4))
    f.append(text(col_x - 30, node_y - 38, "фото-", size=10, color=INK, anchor="end"))
    f.append(text(col_x - 30, node_y - 24, "транзистор", size=10, color=INK, anchor="end"))
    f.append(line(col_x, node_y - 12, col_x, node_y, color=INK, sw=1.8))
    f.append(circle(col_x, node_y, 3.4, fill=INK, stroke=INK, sw=1))
    f.append(rect(col_x - 15, node_y + 18, 30, 42, fill=BG, stroke=INK, sw=1.6, rx=3))
    f.append(line(col_x, node_y, col_x, node_y + 18, color=INK, sw=1.8))
    f.append(line(col_x, node_y + 60, col_x, gnd_y, color=INK, sw=1.8))
    f.append(text(col_x + 24, node_y + 44, "R", size=11, bold=True, color=INK, anchor="start"))
    # горизонталь сигналу до компаратора
    sig_r = col_x + 150
    f.append(line(col_x, node_y, sig_r, node_y, color=FIELD, sw=1.8))
    f.append(text(col_x + 46, node_y - 8, "U (сигнал)", size=10, color=FIELD, anchor="start"))

    # --- компаратор LM393 (трикутник) ---
    cx0 = sig_r + 8
    cyc = node_y
    tri = ('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#eef3fb" stroke="%s" stroke-width="1.8"/>'
           % (cx0, cyc - 46, cx0, cyc + 46, cx0 + 96, cyc, INK))
    f.append(tri)
    f.append(text(cx0 + 30, cyc + 5, "LM393", size=12, bold=True, color=INK, anchor="start"))
    # вхід «+» (сигнал) і «−» (поріг)
    f.append(line(sig_r, node_y, cx0, cyc - 22, color=FIELD, sw=1.8))
    f.append(text(cx0 - 8, cyc - 20, "+", size=13, bold=True, color=FIELD, anchor="end"))
    # потенціометр-поріг зліва-знизу від трикутника (нижче шин, нічого не перетинає)
    pot_x = cx0 - 120
    pot_y = cyc + 70
    f.append(rect(pot_x, pot_y, 50, 30, fill=BG, stroke=POS, sw=1.6, rx=3))
    f.append(text(pot_x + 25, pot_y + 20, "поріг", size=9.5, bold=True, color=POS))
    f.append(text(pot_x + 25, pot_y + 46, "синій гвинтик", size=9, color=MUTED))
    f.append(line(pot_x + 50, pot_y + 15, cx0 - 40, pot_y + 15, color=POS, sw=1.6))
    f.append(line(cx0 - 40, pot_y + 15, cx0 - 40, cyc + 22, color=POS, sw=1.6))
    f.append(line(cx0 - 40, cyc + 22, cx0, cyc + 22, color=POS, sw=1.6))
    f.append(text(cx0 - 14, cyc + 18, "−", size=13, bold=True, color=POS, anchor="end"))

    # --- виходи: AO (сирий) та DO (цифровий), правий стовпчик поза шинами ---
    out_x = bx + bw - 330
    ao_y = by + 92
    do_y = by + 150
    # AO — з вузла сигналу вгору-вправо, вище VCC, потім до краю
    f.append(line(col_x, node_y, col_x, ao_y, color=FIELD, sw=1.6))
    f.append(line(col_x, ao_y, out_x, ao_y, color=FIELD, sw=1.6))
    f.append(circle(out_x, ao_y, 5, fill=BG, stroke=FIELD, sw=2))
    f.append(text(out_x + 12, ao_y + 4, "AO — сира напруга (АЦП)", size=11, bold=True, color=FIELD, anchor="start"))
    # DO — з вершини компаратора
    f.append(line(cx0 + 96, cyc, cx0 + 140, cyc, color=NEG, sw=1.8))
    f.append(line(cx0 + 140, cyc, cx0 + 140, do_y, color=NEG, sw=1.8))
    f.append(line(cx0 + 140, do_y, out_x, do_y, color=NEG, sw=1.8))
    f.append(circle(out_x, do_y, 5, fill=BG, stroke=NEG, sw=2))
    f.append(text(out_x + 12, do_y + 4, "DO — «0/1» (поріг?)", size=11, bold=True, color=NEG, anchor="start"))

    # пояснення станів унизу окремим блоком — короткі рядки
    b, _, _ = textbox(W / 2, 548, "Більше ІЧ від полумʼя → фототранзистор відкривається → напруга U росте.\n"
                                  "Перейшла поріг (гвинтик) → DO перемикається; AO весь час показує силу жару.",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)

    render(os.path.join(IMG, "ky026-schematic.svg"), W, H, *f)


# ── 3. Підключення пін-у-пін: KY-026 (4 піни) ↔ мікроконтролер ──────────────────
def fig_ky026_wiring():
    W, H = 1040, 470
    f = [text(W / 2, 30, "Підключення KY-026: DO — на цифровий пін, AO — на аналоговий (потрібне те чи те)",
              size=15, bold=True)]

    mx, my, mw, mh = 90, 86, 270, 250
    f.append(rect(mx, my, mw, mh, fill="#eef3fb", stroke=NEG, sw=2.0, rx=14))
    f.append(text(mx + mw / 2, my + 28, "KY-026", size=15, bold=True, color=NEG))
    f.append(text(mx + mw / 2, my + 48, "давач полумʼя", size=10, color=MUTED))
    pads = [("AO", FIELD, my + 92),
            ("DO", NEG, my + 138),
            ("+", POS, my + 184),
            ("−", INK, my + 230)]
    for lab, col, py in pads:
        f.append(circle(mx + mw, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(mx + mw - 18, py + 4, lab, size=13, bold=True, color=col, anchor="end"))

    bx, by, bw, bh = 700, 86, 250, 250
    f.append(rect(bx, by, bw, bh, fill="#f7f9fc", stroke=INK, sw=1.8, rx=14))
    f.append(text(bx + bw / 2, by + 28, "плата (Arduino / ESP32…)", size=11, bold=True, color=INK))
    tgts = [("A0", FIELD, by + 92, "аналог. вхід (АЦП)"),
            ("D2", NEG, by + 138, "цифровий вхід"),
            ("3.3–5 В", POS, by + 184, "живлення"),
            ("GND", INK, by + 230, "земля")]
    for lab, col, py, sub in tgts:
        f.append(circle(bx, py, 6, fill=BG, stroke=col, sw=2.2))
        f.append(text(bx + 16, py + 4, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(bx + 16, py + 19, sub, size=9, color=MUTED, anchor="start"))

    for (lab, col, py), (_, _, ty, _) in zip(pads, tgts):
        f.append(line(mx + mw + 6, py, bx - 6, ty, color=col, sw=2.4))

    # нота — короткі рядки, щоб рамка влізла
    b, _, _ = textbox(W / 2, 400, "Береш зазвичай ОДИН вихід: DO для «є вогонь / нема», AO — коли треба міряти силу жару.\n"
                                  "Живлення — під логіку плати: на 5 В вихід бʼє 5-вольтовими рівнями; для ESP32 став +3.3 В.",
                      size=10.5, fill="#fdecea", stroke=POS)
    f.append(b)

    render(os.path.join(IMG, "ky026-wiring.svg"), W, H, *f)


if __name__ == "__main__":
    fig_flame_ir()
    fig_ky026_schematic()
    fig_ky026_wiring()
    print("KY-026 figs done ->", IMG)
