# -*- coding: utf-8 -*-
"""Фігури до теми «TFT-дисплей» (активноматрична рідкокристалічна панель).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Схема одного пікселя: транзистор-засувка + Cs + комірка рідкого кристала ──
def fig_pixel():
    W, H = 760, 430
    f = [text(W / 2, 28, "Один підпіксель: транзистор-засувка тримає напругу на кристалі весь кадр",
              size=15.5, bold=True)]

    # рядкова (gate) лінія — горизонтальна, керує затвором
    yg = 120
    f.append(line(60, yg, 700, yg, color=FIELD, sw=2.4))
    f.append(text(60, yg - 12, "рядкова лінія (gate) — вибирає рядок", size=12, color=FIELD, anchor="start"))

    # стовпцева (source) лінія — вертикальна, несе напругу пікселя
    xs = 180
    f.append(line(xs, 60, xs, 360, color=NEG, sw=2.4))
    f.append(text(xs, 52, "стовпцева лінія (source) — несе напругу", size=12, color=NEG, anchor="middle"))

    # транзистор у перетині
    tx, ty = 300, yg
    f.append(rect(tx - 34, ty - 26, 68, 52, fill="#f7f9fb", stroke=LINE, sw=1.6, rx=8))
    f.append(text(tx, ty - 34, "TFT", size=12, bold=True))
    # затвор від gate-лінії
    f.append(line(tx, yg, tx, ty - 26, color=FIELD, sw=2))
    # вхід стоку від source-лінії
    f.append(line(xs, ty, tx - 34, ty, color=NEG, sw=2))
    f.append(text((xs + tx) / 2, ty + 16, "стік", size=10.5, color=MUTED))
    # витік далі до пікселя
    nx = tx + 90        # вузол пікселя
    f.append(line(tx + 34, ty, nx, ty, color=INK, sw=2))
    f.append(circle(nx, ty, 4, fill=INK, stroke=INK, sw=1))
    f.append(text((tx + 34 + nx) / 2, ty - 8, "витік", size=10.5, color=MUTED))

    # від вузла вниз — дві паралельні ємності: комірка LC і запасний Cs
    f.append(line(nx, ty, nx, 210, color=INK, sw=2))
    # розгалуження
    xL, xC = nx - 60, nx + 60
    f.append(line(xL, 210, xC, 210, color=INK, sw=2))
    f.append(line(nx, ty + 90, nx, 210, color=INK, sw=2))
    f.append(circle(nx, 210, 4, fill=INK, stroke=INK, sw=1))

    # комірка рідкого кристала (Clc) — ліворуч
    f.append(line(xL, 210, xL, 250, color=INK, sw=2))
    f.append(line(xL - 22, 250, xL + 22, 250, color=INK, sw=3))   # верхня обкладка
    f.append(line(xL - 22, 262, xL + 22, 262, color=INK, sw=3))   # нижня обкладка
    f.append(line(xL, 262, xL, 300, color=INK, sw=2))
    f.append(text(xL - 30, 240, "C_LC", size=11.5, color=INK, anchor="end", italic=True))
    f.append(text(xL + 30, 256, "комірка\nрідкого кристала".split("\n")[0], size=10, color=MUTED, anchor="start"))
    f.append(text(xL + 30, 268, "рідкого кристала", size=10, color=MUTED, anchor="start"))

    # запасний конденсатор (Cs) — праворуч
    f.append(line(xC, 210, xC, 250, color=POS, sw=2))
    f.append(line(xC - 22, 250, xC + 22, 250, color=POS, sw=3))
    f.append(line(xC - 22, 262, xC + 22, 262, color=POS, sw=3))
    f.append(line(xC, 262, xC, 300, color=POS, sw=2))
    f.append(text(xC + 30, 240, "Cs", size=11.5, color=POS, anchor="start", italic=True))
    f.append(text(xC + 30, 256, "запасний", size=10, color=POS, anchor="start"))
    f.append(text(xC + 30, 268, "конденсатор", size=10, color=POS, anchor="start"))

    # спільна нижня шина (common / Vcom)
    f.append(line(xL, 300, xC, 300, color=MUTED, sw=2))
    f.append(line(nx, 300, nx, 320, color=MUTED, sw=2))
    f.append(line(nx - 26, 320, nx + 26, 320, color=MUTED, sw=2.6))
    f.append(text(nx, 340, "спільний електрод (Vcom)", size=11, color=MUTED))

    # пояснення-рамка
    b, _, _ = textbox(610, 200,
                      "Рядок відкриває\nтранзистор → напруга\nзі стовпця заряджає\nC_LC і Cs. Рядок\nзнято — Cs ТРИМАЄ\nцю напругу весь кадр.",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "pixel.svg"), W, H, *f)


# ── 2. Пасивна vs активна матриця: шпаруватість 1/N проти 100 % ──────────────
def fig_passive_active():
    W, H = 760, 400
    f = [text(W / 2, 26, "Чому активна матриця перемогла пасивну", size=16, bold=True)]

    # ── ЛІВА панель: пасивна ──
    lx = 24
    f.append(rect(lx, 50, 350, 318, fill="#fffaf9", stroke=POS, sw=1.6, rx=10))
    f.append(text(lx + 175, 74, "Пасивна: піксель живе лише свою мить", size=12.5, bold=True))
    # часова шкала рядків
    ox, oy, aw = lx + 40, 250, 270
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    f.append(text(ox + aw / 2, oy + 60, "один кадр = всі N рядків по черзі", size=10.5, color=MUTED))
    # імпульс одного рядка — вузький
    pw = aw / 8
    f.append(rect(ox + pw, oy - 70, pw, 70, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(ox + pw * 1.5, oy - 80, "наш рядок", size=10, color=POS))
    f.append(text(ox + pw * 1.5, oy + 16, "1/N часу", size=10.5, color=POS, bold=True))
    # решта рядків — пунктир-сходинки
    for i in [0, 2, 3, 4, 5, 6]:
        f.append(rect(ox + pw * i, oy - 22, pw, 22, fill="#f2f2f2", stroke=MUTED, sw=1))
    b, _, _ = textbox(lx + 175, 322,
                      "решту кадру піксель згасає; сусіди підсвічуються\nкрізь спільні дроти → розмиття й перехресні завади",
                      size=10, fill="#fdecea", stroke=POS)
    f.append(b)

    # ── ПРАВА панель: активна ──
    rx = 388
    f.append(rect(rx, 50, 350, 318, fill="#fbfdfb", stroke=FIELD, sw=1.6, rx=10))
    f.append(text(rx + 175, 74, "Активна: транзистор тримає піксель весь кадр", size=12.5, bold=True))
    ox2 = rx + 40
    f.append(line(ox2, oy, ox2 + aw, oy, color=INK, sw=1.6))
    f.append(text(ox2 + aw / 2, oy + 60, "той самий кадр", size=10.5, color=MUTED))
    # короткий імпульс заряду + утримання на весь кадр
    f.append(rect(ox2 + pw, oy - 70, pw * 0.4, 70, fill="#eef2f8", stroke=NEG, sw=1.4))
    f.append(text(ox2 + pw * 1.2, oy - 80, "заряд", size=10, color=NEG))
    # рівень утримання — на всю ширину
    f.append(rect(ox2, oy - 40, aw, 40, fill="#eaf6ee", stroke=FIELD, sw=1.6))
    f.append(text(ox2 + aw / 2, oy - 18, "Cs ТРИМАЄ напругу — 100 % часу", size=10.5, color=FIELD, bold=True))
    b2, _, _ = textbox(rx + 175, 322,
                       "транзистор ізолює піксель від сусідів: без перехресних\nзавад, повний контраст, годиться для великих панелей",
                       size=10, fill="#eef6ef", stroke=FIELD)
    f.append(b2)
    render(os.path.join(IMG, "passive-active.svg"), W, H, *f)


# ── 3. Три основи (backplane): a-Si / IGZO / LTPS — рухливість vs ціна ───────
def fig_backplanes():
    W, H = 760, 410
    f = [text(W / 2, 26, "Три основи активної матриці: чим швидші електрони, тим складніше робити",
              size=15, bold=True)]

    ox, oy = 90, 330
    aw, ah = 600, 250
    # вісь рухливості (логарифмічна на око) — горизонтальна шкала-стрілка
    f.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.8))
    f.append(text(ox + aw / 2, oy + 54, "рухливість електронів — більша = швидший і дрібніший піксель →",
                  size=11.5, color=INK))
    f.append(arrow(ox, oy, ox, oy - ah, color=INK, sw=1.8))
    f.append(mtext(ox - 56, oy - ah / 2, ["складність", "і ціна", "↑"], size=11, color=MUTED, anchor="middle"))

    # три точки
    def node(x, y, name, mob, note, col):
        f.append(circle(x, y, 6, fill=col, stroke=col, sw=1))
        b, _, _ = textbox(x, y - 44, name + "\n" + mob, size=11.5, fill="#ffffff", stroke=col, bold=True)
        f.append(b)
        f.append(mtext(x, y + 26, note, size=10, color=MUTED, anchor="middle"))

    node(ox + 110, oy - 40, "a-Si", "~1 см²/В·с",
         ["аморфний кремній:", "дешево, великі панелі,", "але повільний"], MUTED)
    node(ox + 330, oy - 130, "IGZO", "~10–30 см²/В·с",
         ["оксид (In-Ga-Zn-O):", "у 20–50× рухливіший,", "малий витік → ниж. споживання"], FIELD)
    node(ox + 530, oy - 210, "LTPS", "~100 см²/В·с",
         ["низькотемп. полікремній:", "найшвидший, дрібний піксель,", "лазер → дорого, дрібні екрани"], POS)

    # сходинка-лінія тренду
    f.append(line(ox + 110, oy - 40, ox + 330, oy - 130, color=LINE, sw=1.4, dash="5,4"))
    f.append(line(ox + 330, oy - 130, ox + 530, oy - 210, color=LINE, sw=1.4, dash="5,4"))
    render(os.path.join(IMG, "backplanes.svg"), W, H, *f)


# ── 4. Детальна схема пікселя: три ємності + паразитний місток Cgd ───────────
def fig_pixel_detail():
    W, H = 760, 440
    f = [text(W / 2, 26, "Схема пікселя як коло: три ємності у вузлі, паразитна Cgd — місток за затвором",
              size=14, bold=True)]

    yg = 130          # рядкова лінія (gate)
    xs = 170          # стовпцева лінія (source)
    tx = 320          # транзистор
    nx = 440          # вузол пікселя

    # лінії
    f.append(line(70, yg, 700, yg, color=FIELD, sw=2.4))
    f.append(text(70, yg - 12, "рядкова (gate): Vgh / Vgl", size=11.5, color=FIELD, anchor="start"))
    f.append(line(xs, 70, xs, 350, color=NEG, sw=2.4))
    f.append(text(xs, 62, "стовпцева (source)", size=11.5, color=NEG, anchor="middle"))

    # транзистор
    f.append(rect(tx - 32, yg - 24, 64, 48, fill="#f7f9fb", stroke=LINE, sw=1.6, rx=8))
    f.append(text(tx, yg - 32, "TFT", size=12, bold=True))
    f.append(line(tx, yg, tx, yg - 24, color=FIELD, sw=2))     # затвор
    f.append(line(xs, yg, tx - 32, yg, color=NEG, sw=2))       # стік від source
    f.append(line(tx + 32, yg, nx, yg, color=INK, sw=2))       # витік до вузла
    f.append(circle(nx, yg, 4, fill=INK, stroke=INK, sw=1))

    # паразитний місток Cgd: від gate-лінії до вузла, дугою
    f.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>'
             % (tx, yg + 30, (tx + nx) / 2 + 10, yg + 70, nx, yg + 6, POS))
    f.append(line(tx, yg, tx, yg + 30, color=POS, sw=1.4, dash="3,3"))
    bcgd, _, _ = textbox((tx + nx) / 2 + 10, yg + 92, "Cgd — паразитна\nзатвор↔стік", size=10.5,
                         fill="#fdecea", stroke=POS)
    f.append(bcgd)

    # від вузла вниз — дві корисні ємності
    f.append(line(nx, yg, nx, 215, color=INK, sw=2))
    xL, xC = nx - 55, nx + 55
    f.append(line(xL, 215, xC, 215, color=INK, sw=2))
    f.append(circle(nx, 215, 4, fill=INK, stroke=INK, sw=1))

    def cap(x, top, col, lab):
        f.append(line(x, top, x, top + 30, color=col, sw=2))
        f.append(line(x - 20, top + 30, x + 20, top + 30, color=col, sw=3))
        f.append(line(x - 20, top + 42, x + 20, top + 42, color=col, sw=3))
        f.append(line(x, top + 42, x, top + 80, color=col, sw=2))
        f.append(text(x + (28 if col == POS else -28), top + 22, lab, size=11.5, color=col,
                      anchor=("start" if col == POS else "end"), italic=True))

    cap(xL, 215, INK, "C_LC")
    cap(xC, 215, POS, "Cs")
    f.append(text(xL, 215 + 96, "комірка", size=10, color=MUTED))
    f.append(text(xL, 215 + 108, "кристала", size=10, color=MUTED))
    f.append(text(xC, 215 + 96, "запасний", size=10, color=POS))

    # спільний електрод Vcom
    f.append(line(xL, 215 + 80, xC, 215 + 80, color=MUTED, sw=2))
    f.append(line(nx, 215 + 80, nx, 215 + 100, color=MUTED, sw=2))
    f.append(line(nx - 24, 215 + 100, nx + 24, 215 + 100, color=MUTED, sw=2.6))
    f.append(text(nx, 215 + 120, "спільний електрод Vcom", size=11, color=MUTED))

    b, _, _ = textbox(630, 235, "корисні: C_LC + Cs\nтримають заряд.\n\nпаразитна Cgd\nкраде напругу,\nколи затвор падає.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "pixel-detail.svg"), W, H, *f)


# ── 5. Чотири схеми інверсії полярності на сітці пікселів ────────────────────
def fig_inversion():
    W, H = 760, 470
    f = [text(W / 2, 26, "Чотири схеми інверсії полярності: де поряд є + і −, мерехтіння зникає",
              size=14.5, bold=True)]

    cell = 26
    N = 5               # 5×5 сітка
    grid = N * cell

    def panel(px, py, title, signfn, note):
        f.append(text(px + grid / 2, py - 12, title, size=12, bold=True))
        for r in range(N):
            for c in range(N):
                s = signfn(r, c)
                col = POS if s > 0 else NEG
                fill = "#fdecea" if s > 0 else "#eef2f8"
                x, y = px + c * cell, py + r * cell
                f.append(rect(x, y, cell, cell, fill=fill, stroke=col, sw=1.2, rx=2))
                f.append(text(x + cell / 2, y + cell / 2 + 5, "+" if s > 0 else "−",
                              size=14, color=col, bold=True))
        f.append(mtext(px + grid / 2, py + grid + 18, note, size=10, color=MUTED, anchor="middle"))

    y1 = 70
    panel(60, y1, "кадрова (frame)", lambda r, c: 1, ["уся панель одного знака", "→ найгірше мерехтіння"])
    panel(300, y1, "рядкова (line)", lambda r, c: 1 if r % 2 == 0 else -1,
          ["знак чергується по рядках", "→ слабкі горизонт. смуги"])
    y2 = 280
    panel(60, y2, "стовпцева (column)", lambda r, c: 1 if c % 2 == 0 else -1,
          ["знак чергується по стовпцях", "→ слабкі вертик. смуги"])
    panel(300, y2, "точкова (dot)", lambda r, c: 1 if (r + c) % 2 == 0 else -1,
          ["шахівниця сусідніх знаків", "→ мерехтіння майже зникає"])

    b, _, _ = textbox(620, 200,
                      "Що дрібніше\nперемішані + і −,\nто краще око\nусереднює їх\nу просторі —\nі не бачить\nпульсації.\n\nАле точкова\nгріє драйвер:\nрозмах напруги\nна кожному кроці.",
                      size=10.5, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "inversion.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pixel()
    fig_passive_active()
    fig_backplanes()
    fig_pixel_detail()
    fig_inversion()
    print("OK: 5 figures ->", IMG)
