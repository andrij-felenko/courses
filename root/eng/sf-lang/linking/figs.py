# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── overview: багато .o + бібліотеки → лінкер → одна програма ──────────────────
# Ідея: лінкер уперше збирає ЦІЛЕ з частин — на вхід купка об'єктних файлів плюс
# бібліотеки, на виході один образ, де дірки заповнено й адреси роздано.

def fig_overview():
    W, H = 720, 320
    p = []
    cy = 168

    # вхідні .o (стос) + бібліотека
    ins = [("main.o", FILL), ("blink.o", FILL), ("sensor.o", FILL)]
    iy = [96, 150, 204]
    rights = []
    for (lab, fill), y in zip(ins, iy):
        b, bw, bh = textbox(120, y, lab, size=12, bold=True, fill=fill, stroke=INK, sw=1.5, min_w=120)
        p.append(b)
        rights.append((120 + bw / 2, y))
    lib, lw, lh = textbox(120, 268, "бібліотеки\n(Arduino, IDF…)", size=11, bold=True,
                          fill="#fdf6e3", stroke="#b79a5e", color="#8a6a14", min_w=120)
    p.append(lib)
    rights.append((120 + lw / 2, 268))

    # лінкер у центрі
    box, cw, ch = textbox(380, cy, "ЛІНКЕР\nзшиває все", size=14, bold=True,
                          fill="#fff6e0", stroke="#caa24a", sw=2.2, color="#8a6a14", min_w=150)
    # стрілки від входів до лівого краю лінкера
    for rx, ry in rights:
        p.append(arrow(rx + 4, ry, 380 - cw / 2 - 4, cy, color=MUTED, sw=1.6))
    p.append(box)

    # вихід — одна програма
    out, ow, oh = textbox(600, cy, "одна повна\nпрограма", size=12, bold=True,
                          fill="#eafaf0", stroke=FIELD, sw=2, color=FIELD, min_w=150)
    p.append(arrow(380 + cw / 2 + 4, cy, 600 - ow / 2 - 4, cy, color=FIELD, sw=2.6))
    p.append(out)
    p.append(text(600, cy + oh / 2 + 18, "дірки заповнено, адреси роздано", size=10, color=MUTED))

    render(os.path.join(OUT, "overview.svg"), W, H, *p,
           title="Лінкер: багато об'єктних файлів + бібліотеки → одна програма")


# ── symbols: таблиця символів одного .o — визначає / потребує ──────────────────
# Ідея: кожен .o водночас постачальник одних імен і прохач інших; «потребує» —
# це і є незаповнені дірки.

def fig_symbols():
    W, H = 640, 300
    p = []
    # рамка файлу
    p.append(rect(40, 70, W - 80, H - 110, fill=BG, stroke=INK, sw=1.6))
    p.append(text(W / 2, 92, "blink.o", size=13, bold=True))

    colw = (W - 80) / 2
    lx = 40 + colw / 2
    rx = 40 + colw + colw / 2

    p.append(text(lx, 124, "ВИЗНАЧАЄ (дає)", size=11, bold=True, color=FIELD))
    p.append(text(rx, 124, "ПОТРЕБУЄ (кличе)", size=11, bold=True, color=POS))
    p.append(line(W / 2, 110, W / 2, H - 50, color=MUTED, sw=1.2, dash="5 4"))

    p.append(fitbox(lx - colw / 2 + 24, 142, colw - 48, 40, "blink",
                    size=12, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD))
    p.append(mtext(lx, 206, "тут написана — місце є", size=10, color=MUTED))

    p.append(fitbox(rx - colw / 2 + 24, 142, colw - 48, 40, "digitalWrite",
                    size=12, bold=True, fill="#fdecea", stroke=POS, color=POS))
    p.append(mtext(rx, 206, "кличе ззовні —\nадреса поки порожня (дірка)", size=10, color=MUTED))

    p.append(text(W / 2, H - 24,
                  "кожен .o — і постачальник, і прохач імен водночас",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "symbols.svg"), W, H, *p,
           title="Таблиця символів об'єктного файлу")


# ── resolution: з'єднати кожне «потребує» з «визначає» ─────────────────────────
# Ідея: серце лінкування — на кожне «треба X» знайти «є X» рівно один раз; без
# пари → undefined reference, два визначення → multiple definition.

def fig_resolution():
    W, H = 700, 320
    p = []
    needs = ["main → blink", "main → digitalWrite", "blink → digitalWrite"]
    defs = ["blink (у blink.o)", "digitalWrite (у бібліотеці)"]

    p.append(text(165, 78, "ПОТРЕБУЄ", size=12, bold=True, color=POS))
    p.append(text(535, 78, "ВИЗНАЧАЄ", size=12, bold=True, color=FIELD))

    ny, dy = [120, 178, 236], [140, 216]
    npos, dpos = [], []
    for lab, y in zip(needs, ny):
        b, bw, bh = textbox(165, y, lab, size=11, fill="#fdecea", stroke=POS, color=POS, min_w=210)
        p.append(b); npos.append((165 + bw / 2, y))
    for lab, y in zip(defs, dy):
        b, bw, bh = textbox(535, y, lab, size=11, fill="#eafaf0", stroke=FIELD, color=FIELD, min_w=210)
        p.append(b); dpos.append((535 - bw / 2, y))

    # зв'язки: 0→0, 1→1, 2→1
    pairs = [(0, 0), (1, 1), (2, 1)]
    for ni, di in pairs:
        (x1, y1), (x2, y2) = npos[ni], dpos[di]
        p.append(line(x1 + 4, y1, x2 - 4, y2, color=INK, sw=1.8))
        p.append(text((x1 + x2) / 2, (y1 + y2) / 2 - 6, "✓", size=13, color=FIELD, bold=True))

    p.append(text(W / 2, H - 26,
                  "без пари → undefined reference · два визначення → multiple definition",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "resolution.svg"), W, H, *p,
           title="Розв'язання символів: кожне «потребує» — до свого «визначає»")


# ── libraries: бібліотека = склад готових .o; беруть лише потрібне ─────────────
# Ідея: архів наперед скомпільованих .o; на «потребує X» лінкер витягує саму X
# (і її залежності), а не весь архів — звідси і швидкість, і ощадність.

def fig_libraries():
    W, H = 700, 300
    p = []
    # склад — сітка функцій, одну підсвічено
    sx, sy, cols = 60, 90, 3
    cw, chh, gap = 150, 40, 14
    names = ["digitalWrite", "pinMode", "Serial.print",
             "millis", "analogRead", "delay"]
    take_xy = None
    for i, nm in enumerate(names):
        r, c = divmod(i, cols)
        x = sx + c * (cw + gap)
        y = sy + r * (chh + gap)
        hot = (nm == "digitalWrite")
        p.append(fitbox(x, y, cw, chh, nm, size=11, bold=hot,
                        fill="#eafaf0" if hot else FILL,
                        stroke=FIELD if hot else MUTED,
                        color=FIELD if hot else INK))
        if hot:
            take_xy = (x + cw / 2, y + chh / 2)
    p.append(rect(sx - 16, sy - 28, cols * (cw + gap) - gap + 32,
                  2 * (chh + gap) - gap + 44, fill="none", stroke="#b79a5e", sw=1.6))
    p.append(text(sx - 16 + (cols * (cw + gap)) / 2 - 8, sy - 36,
                  "бібліотека — склад наперед скомпільованих .o", size=11, color="#8a6a14", bold=True))

    # запит знизу → витягуємо лише digitalWrite
    qx, qy = W / 2, 250
    p.append(fitbox(qx - 110, qy, 220, 38, "потребує: digitalWrite",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))
    if take_xy:
        p.append(arrow(qx, qy, take_xy[0], take_xy[1] + chh / 2 + 2, color=POS, sw=2.0))
    p.append(text(W / 2, H - 14, "у прошивку йде лише використане — решта складу лишається",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "libraries.svg"), W, H, *p,
           title="Бібліотека як склад: лінкер бере лише потрібне")


# ── addresses: лінкер кладе шматки на карту пам'яті чипа ───────────────────────
# Ідея: друга робота — дати кожному фрагменту остаточну адресу; код у Flash,
# дані в RAM; орієнтир — сценарій лінкування, що знає карту саме цього чипа.

def fig_addresses():
    W, H = 700, 360
    p = []
    # дві смуги пам'яті
    fx, rx = 90, 400
    top, bw, bh = 84, 220, 190
    p.append(rect(fx, top, bw, bh, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(text(fx + bw / 2, top - 12, "Flash (код)", size=12, bold=True, color=NEG))
    p.append(rect(rx, top, bw, bh, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(rx + bw / 2, top - 12, "RAM (дані)", size=12, bold=True, color=FIELD))

    # шматки коду у Flash із адресами
    chunks = [("main", "0x4000_0100"), ("blink", "0x4000_0140"),
              ("digitalWrite", "0x4000_0190")]
    yy = top + 18
    for nm, addr in chunks:
        p.append(fitbox(fx + 18, yy, bw - 36, 34, nm, size=11, bold=True,
                        fill=BG, stroke=INK))
        p.append(text(fx + bw - 6, yy + 22, addr, size=9, color=MUTED, anchor="end"))
        yy += 46

    # дані у RAM
    p.append(fitbox(rx + 18, top + 18, bw - 36, 34, "змінні", size=11, bold=True,
                    fill=BG, stroke=INK))

    # сценарій лінкування — орієнтир
    p.append(fitbox(W / 2 - 95, top + bh + 16, 190, 38,
                    "сценарій лінкування\n(карта саме цього чипа)", size=10, bold=True,
                    fill="#fdf6e3", stroke="#b79a5e", color="#8a6a14"))
    p.append(arrow(W / 2, top + bh + 16, W / 2, top + bh + 4, color="#b79a5e", sw=1.6))

    render(os.path.join(OUT, "addresses.svg"), W, H, *p,
           title="Розкладання по адресах: кожному шматку — своє місце")


# ── trace: лінкування крок за кроком на прикладі ──────────────────────────────
# Ідея: спершу символи розв'язано (потребує→визначає), тоді роздано адреси й
# вписано їх у місця викликів — на виході один повний образ.

def fig_trace():
    W, H = 700, 280
    p = []
    bw, bh = 180, 96
    y = 80
    xs = [40, 260, 480]

    # крок 1
    p.append(fitbox(xs[0], y, bw, bh,
                    "КРОК 1\nрозв'язання символів\n(потребує → визначає)",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))
    # крок 2
    p.append(fitbox(xs[1], y, bw, bh,
                    "КРОК 2\nроздати адреси\n(заповнити дірки)",
                    size=11, bold=True, fill="#eef4ff", stroke=NEG, color=NEG))
    # результат
    p.append(fitbox(xs[2], y, bw, bh,
                    "РЕЗУЛЬТАТ\nодин повний образ\n(готовий у прошивку)",
                    size=11, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD))

    p.append(arrow(xs[0] + bw, y + bh / 2, xs[1], y + bh / 2, color=INK, sw=2.0))
    p.append(arrow(xs[1] + bw, y + bh / 2, xs[2], y + bh / 2, color=INK, sw=2.0))

    p.append(text(W / 2, y + bh + 40,
                  "спершу всі імена з'єднано, тоді всі адреси роздано — дірок не лишилось",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "trace.svg"), W, H, *p,
           title="Лінкування крок за кроком")


if __name__ == "__main__":
    fig_overview()
    fig_symbols()
    fig_resolution()
    fig_libraries()
    fig_addresses()
    fig_trace()
    print("OK: figures written to", OUT)
