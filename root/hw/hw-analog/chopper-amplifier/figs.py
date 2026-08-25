# -*- coding: utf-8 -*-
"""Фігури до статті «Чопперний підсилювач» (book/electronics/analog/chopper-amplifier).
Чотири фігури:
  why.svg      — суть: дрейф і 1/f живуть на постійці; сигнал піднімають на несучу, де чисто
  spectrum.svg — частотна картина: 1/f-кут і де сидить сигнал ДО і ПІСЛЯ чоппінга
  loop.svg     — тракт: модулятор → AC-підсилювач → демодулятор (два кільця ключів в такт)
  ripple.svg   — реальність: зрізаний офсет лишає брижі на несучій → нотч-фільтр прибирає
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── локальні помічники ───────────────────────────────────────────────────────
def switch(cx, cy, closed=True, label=None, col=NEG):
    """Символ ключа-перемикача: дві клеми й важіль (замкнено/розімкнено)."""
    r = 3.0
    out = [circle(cx - 14, cy, r, fill="#ffffff", stroke=INK, sw=1.4),
           circle(cx + 14, cy, r, fill="#ffffff", stroke=INK, sw=1.4)]
    if closed:
        out.append(line(cx - 14, cy, cx + 14, cy, color=col, sw=2.4))
    else:
        out.append(line(cx - 14, cy, cx + 9, cy - 12, color=col, sw=2.4))
    if label:
        out.append(text(cx, cy + 22, label, size=11, color=col, bold=True))
    return "".join(out)


def block(x, y, w, h, lines, fill=FILL, stroke=INK, size=12, bold=True, col=INK):
    out = [rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8, rx=8)]
    if isinstance(lines, str):
        lines = [lines]
    cy = y + h / 2 - (len(lines) - 1) * size * 1.25 / 2 + size * 0.35
    out.append(mtext(x + w / 2, cy, lines, size=size, color=col, bold=bold))
    return "".join(out), (x, y + h / 2), (x + w, y + h / 2)


# ════════════════════════════════════════════════════════════════════════════
# 1. why.svg — навіщо: офсет і дрейф нерухомі на постійці, сигнал тікає на несучу
# ════════════════════════════════════════════════════════════════════════════
def fig_why():
    W, H = 680, 340
    f = []
    f.append(text(W / 2, 30, "Підступ постійного струму", size=16, bold=True))

    # вісь частоти знизу
    ax, ay, aw = 70, 250, 540
    f.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=1.8))
    f.append(text(ax + aw, ay + 22, "частота", size=12, color=INK, anchor="end"))
    f.append(text(ax - 6, ay + 22, "0 (постійка)", size=11, color=MUTED, anchor="start"))

    # «зона бруду» біля нуля: офсет + 1/f
    bw = 150
    f.append(rect(ax, ay - 150, bw, 150, fill="#fdecea", stroke=POS, sw=0, rx=0))
    f.append(text(ax + bw / 2, ay - 120, "офсет", size=12, color=POS, bold=True))
    f.append(text(ax + bw / 2, ay - 100, "+ дрейф", size=12, color=POS, bold=True))
    f.append(text(ax + bw / 2, ay - 78, "+ 1/f шум", size=12, color=POS, bold=True))
    f.append(text(ax + bw / 2, ay - 52, "усе тут,", size=11, color=MUTED))
    f.append(text(ax + bw / 2, ay - 36, "коло нуля", size=11, color=MUTED))

    # стрілка «піднімаємо сигнал на несучу»
    fc = ax + 360
    f.append(line(fc, ay, fc, ay - 170, color=FIELD, sw=2.0, dash="5 4"))
    f.append(text(fc, ay - 182, "несуча f_chop", size=12, color=FIELD, bold=True))
    # дельта корисного сигналу на несучій
    f.append(line(fc, ay, fc, ay - 120, color=FIELD, sw=6))
    f.append(text(fc + 78, ay - 110, "корисний сигнал —", size=11, color=FIELD, bold=True))
    f.append(text(fc + 78, ay - 94, "перенесений сюди,", size=11, color=FIELD))
    f.append(text(fc + 78, ay - 78, "де чисто", size=11, color=FIELD))

    # зігнута стрілка з зони-бруду до несучої
    f.append('<path d="M %.0f %.0f Q %.0f %.0f %.0f %.0f" fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
             % (ax + bw + 4, ay - 90, (ax + bw + fc) / 2, ay - 210, fc - 6, ay - 124, NEG))
    f.append(text((ax + bw + fc) / 2, ay - 216, "чоппінг переносить", size=11, color=NEG, bold=True))

    body, _, _ = textbox(W / 2, 306,
                         "Підсилювач шумить найдужче там, де живе постійний сигнал.\nВиносимо сигнал ВГОРУ — і підсилюємо вже не поруч із брудом.",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "why.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. spectrum.svg — частотний портрет: 1/f-кут, і сигнал ДО/ПІСЛЯ переносу
# ════════════════════════════════════════════════════════════════════════════
def fig_spectrum():
    W, H = 680, 360
    f = []
    f.append(text(W / 2, 30, "Де сидить шум, а де — сигнал", size=16, bold=True))

    ox, oy = 80, 290
    axw, axh = 540, 220
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw, oy + 22, "частота →", size=12, color=INK, anchor="end"))
    f.append(text(ox - 10, oy - axh + 4, "шум", size=12, color=INK, anchor="end", bold=True))

    # крива шуму: 1/f-спад зліва до плаского теплового «дна» справа
    pts = []
    floor = oy - 40
    for i in range(0, axw - 8, 6):
        x = ox + 6 + i
        # 1/f: великий зліва, спадає; додаємо плато
        ff = (i + 8) / 40.0
        y = floor - 150 / (ff ** 0.9)
        if y > floor:
            y = floor
        pts.append((x, y))
    path = "M %.0f %.0f " % pts[0] + " ".join("L %.0f %.0f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, POS))
    f.append(text(ox + 70, oy - 175, "1/f (фліккер)", size=12, color=POS, bold=True))
    f.append(text(ox + 350, floor - 14, "теплове дно", size=11, color=MUTED))

    # 1/f-кут (corner)
    fk = ox + 150
    f.append(line(fk, oy, fk, floor - 6, color=MUTED, sw=1.3, dash="4 4"))
    f.append(text(fk, oy + 18, "1/f-кут", size=11, color=MUTED, anchor="middle"))

    # сигнал ДО: коло нуля, у самій гущі 1/f (червона стрілка вгору)
    f.append(line(ox + 18, oy, ox + 18, oy - 120, color=NEG, sw=6))
    f.append(text(ox + 18, oy - 130, "сигнал", size=10, color=NEG, bold=True, anchor="middle"))
    f.append(text(ox + 18, oy + 18, "ДО", size=11, color=NEG, bold=True, anchor="middle"))
    f.append(text(ox + 18, oy + 33, "(тоне)", size=10, color=POS, anchor="middle"))

    # сигнал ПІСЛЯ: на несучій, далеко праворуч, де дно (зелена стрілка)
    fc = ox + 410
    f.append(line(fc, oy, fc, oy - 120, color=FIELD, sw=6))
    f.append(line(fc, oy, fc, oy - axh + 10, color=FIELD, sw=1.4, dash="5 4"))
    f.append(text(fc, oy - axh + 4, "f_chop", size=11, color=FIELD, bold=True, anchor="middle"))
    f.append(text(fc, oy + 18, "ПІСЛЯ", size=11, color=FIELD, bold=True, anchor="middle"))
    f.append(text(fc, oy + 33, "(чисто)", size=10, color=FIELD, anchor="middle"))

    body, _, _ = textbox(W / 2, 336,
                         "Той самий сигнал: на постійці його накриває 1/f; на несучій під ним — лише рівне теплове дно.",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "spectrum.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. loop.svg — тракт: модулятор → AC-підсилювач → демодулятор у такт
# ════════════════════════════════════════════════════════════════════════════
def fig_loop():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 28, "Як це працює: підняв → підсилив → опустив", size=16, bold=True))

    yline = 150
    # вхід
    f.append(text(40, yline - 16, "вхід", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(40, yline + 2, "U_in", size=12, color=NEG, anchor="start"))
    f.append(line(40, yline + 18, 110, yline + 18, color=INK, sw=1.8))

    # модулятор (ключ 1)
    f.append(switch(130, yline + 18, closed=True, col=NEG))
    f.append(text(130, yline - 14, "МОДУЛЯТОР", size=11, color=NEG, bold=True))
    f.append(text(130, yline + 46, "рве на ±", size=10, color=MUTED))

    # AC-підсилювач
    blk, bin_, bout = block(180, yline - 8, 150, 54, ["AC-підсилювач", "(великий G)"],
                            fill="#f4f6f8", col=INK)
    f.append(line(144, yline + 18, 180, yline + 18, color=INK, sw=1.8))
    f.append(blk)
    f.append(text(255, yline + 70, "тут немає постійки —", size=10, color=FIELD))
    f.append(text(255, yline + 84, "офсет і 1/f не множаться", size=10, color=FIELD, bold=True))

    # демодулятор (ключ 2) — у такт із модулятором
    f.append(line(330, yline + 18, 396, yline + 18, color=INK, sw=1.8))
    f.append(switch(416, yline + 18, closed=True, col=NEG))
    f.append(text(416, yline - 14, "ДЕМОДУЛЯТОР", size=11, color=NEG, bold=True))
    f.append(text(416, yline + 46, "складає назад", size=10, color=MUTED))

    # ФНЧ + вихід
    blk2, b2in, b2out = block(470, yline - 8, 120, 54, ["ФНЧ", "(згладити)"],
                              fill="#eef7f0", stroke=FIELD, col=INK)
    f.append(line(430, yline + 18, 470, yline + 18, color=INK, sw=1.8))
    f.append(blk2)
    f.append(line(590, yline + 18, 660, yline + 18, color=INK, sw=1.8))
    f.append(text(680, yline + 22, "U_out", size=12, color=FIELD, bold=True, anchor="middle"))

    # тактовий генератор знизу, керує ОБОМА ключами в один такт
    clky = 270
    f.append(rect(250, clky, 120, 40, fill="#fff7e6", stroke=POS, sw=1.8, rx=8))
    # квадратний меандр всередині
    mx = 262
    f.append('<path d="M %d %d h10 v-14 h12 v14 h12 v-14 h12 v14 h12" fill="none" stroke="%s" stroke-width="2"/>'
             % (mx, clky + 28, POS))
    f.append(text(310, clky + 14, "такт f_chop", size=11, color=POS, bold=True))
    # лінії керування до обох ключів (один такт!)
    f.append(line(130, yline + 30, 130, clky + 20, color=POS, sw=1.4, dash="4 4"))
    f.append(line(130, clky + 20, 250, clky + 20, color=POS, sw=1.4, dash="4 4"))
    f.append(line(416, yline + 30, 416, clky + 20, color=POS, sw=1.4, dash="4 4"))
    f.append(line(370, clky + 20, 416, clky + 20, color=POS, sw=1.4, dash="4 4"))
    f.append(text(W / 2, clky + 64, "Обидва ключі клацають в один такт — тому демодулятор «знає», що складати назад",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "loop.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. ripple.svg — реальність: зрізаний офсет → брижі на несучій → нотч прибирає
# ════════════════════════════════════════════════════════════════════════════
def fig_ripple():
    W, H = 680, 320
    f = []
    f.append(text(W / 2, 28, "Ціна методу: брижі на несучій", size=16, bold=True))

    # ліва панель: вихід ДО фільтра — постійка з пилкою/меандром брижів
    ox, oy = 70, 170
    pw, ph = 230, 120
    f.append(rect(ox, oy - ph, pw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=6))
    f.append(line(ox, oy, ox + pw, oy, color="#d0d3d8", sw=1))
    mid = oy - ph / 2
    # меандр брижів навколо середнього рівня
    seg = 18
    pts = []
    up = True
    x = ox + 8
    while x < ox + pw - 8:
        y = mid - 16 if up else mid + 16
        pts.append((x, y)); pts.append((x + seg, y))
        x += seg; up = not up
    path = "M %.0f %.0f " % pts[0] + " ".join("L %.0f %.0f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, POS))
    f.append(line(ox + 4, mid, ox + pw - 4, mid, color=FIELD, sw=2, dash="6 4"))
    f.append(text(ox + pw / 2, oy - ph - 8, "вихід ДО фільтра", size=11, color=INK, bold=True))
    f.append(text(ox + pw / 2, mid - 24, "брижі на f_chop", size=10, color=POS, anchor="middle"))
    f.append(text(ox + pw + 6, mid + 4, "← правда", size=10, color=FIELD, anchor="start"))

    # стрілка крізь нотч/ФНЧ
    nx = ox + pw + 40
    f.append(rect(nx, mid - 26, 96, 52, fill="#eef7f0", stroke=FIELD, sw=1.8, rx=8))
    f.append(mtext(nx + 48, mid - 4, ["нотч на", "f_chop", "+ ФНЧ"], size=11, color=INK, bold=True))
    f.append(arrow(ox + pw + 2, mid, nx - 2, mid, color=INK, sw=2))
    f.append(arrow(nx + 96 + 2, mid, nx + 96 + 36, mid, color=INK, sw=2))

    # права панель: чистий вихід
    rx = nx + 96 + 40
    rw = 150
    f.append(rect(rx, oy - ph, rw, ph, fill="#fcfcfd", stroke=MUTED, sw=1.2, rx=6))
    f.append(line(rx + 6, mid, rx + rw - 6, mid, color=FIELD, sw=2.6))
    f.append(text(rx + rw / 2, oy - ph - 8, "після фільтра", size=11, color=INK, bold=True))
    f.append(text(rx + rw / 2, mid + 22, "рівно", size=10, color=FIELD, anchor="middle"))

    body, _, _ = textbox(W / 2, 284,
                         "Залишковий офсет ключів не зникає — він стає брижами на несучій.\nНотч на f_chop їх вирізає, лишаючи чистий постійний вихід.",
                         size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "ripple.svg"), W, H, *f)


if __name__ == "__main__":
    fig_why()
    fig_spectrum()
    fig_loop()
    fig_ripple()
    print("OK: 4 фігури у", IMG)
