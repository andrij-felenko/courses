# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── uneven-to-even: джитер на вході → рівний потік на виході ──────────────────
# Ідея: пакети приходять із нерівним інтервалом (джитер). Буфер притримує їх і
# випускає через однакові проміжки — ціною сталої затримки (зсув смуг управо).
def fig_uneven_to_even():
    W, H = 720, 320
    p = []
    x0, x1 = 70, 650
    span = x1 - x0

    # мітки пакетів: момент НАДСИЛАННЯ (рівний) vs момент ПРИБУТТЯ (плаває)
    sent = [0.04, 0.18, 0.32, 0.46, 0.60, 0.74, 0.88]          # рівний крок
    arr  = [0.09, 0.20, 0.40, 0.49, 0.71, 0.79, 0.99]          # з джитером
    play = [0.30, 0.42, 0.54, 0.66, 0.78, 0.90, 1.02]          # рівний, зі зсувом

    def axis(y, lab, color):
        out = [line(x0, y, x1 + 8, y, color=INK, sw=1.8)]
        out.append(text(x0 - 8, y + 4, lab, size=11, color=color, anchor="end", bold=True))
        return out

    def pkt(x, y, n, color, fill):
        return (rect(x - 9, y - 11, 18, 22, fill=fill, stroke=color, sw=1.6, rx=3) +
                text(x, y + 4, str(n), size=10, color=color, bold=True))

    # 1) надіслано — рівномірно
    ys = 70
    p += axis(ys, "надіслано", FIELD)
    for i, f in enumerate(sent):
        p.append(pkt(x0 + f * span, ys, i + 1, FIELD, "#eafaf0"))
    p.append(text(x1 + 14, ys + 4, "рівний крок", size=10, color=MUTED, anchor="start"))

    # 2) прибуло — з джитером (підкреслюємо нерівні проміжки)
    ya = 160
    p += axis(ya, "прибуло", POS)
    for i, f in enumerate(arr):
        p.append(pkt(x0 + f * span, ya, i + 1, POS, "#fdecea"))
    p.append(text(x1 + 14, ya + 4, "крок «плаває»\n(джитер)", size=10, color=MUTED, anchor="start"))

    # 3) відтворено — знову рівномірно, але пізніше (зсув = глибина буфера)
    yp = 250
    p += axis(yp, "відтворено", NEG)
    for i, f in enumerate(play):
        p.append(pkt(x0 + min(f, 0.995) * span, yp, i + 1, NEG, "#eaf0fd"))
    p.append(text(x1 + 14, yp + 4, "рівний крок\n(вирівняно)", size=10, color=MUTED, anchor="start"))

    # стрілка зсуву в часі = затримка буфера (від 1-го прибулого до 1-го виданого)
    xa = x0 + arr[0] * span
    xb = x0 + play[0] * span
    p.append(arrow(xa, 205, xb, 205, color="#8a5fb0", sw=2.0))
    p.append(text((xa + xb) / 2, 200, "затримка буфера", size=11, color="#8a5fb0", bold=True))

    render(os.path.join(OUT, "uneven-to-even.svg"), W, H, *p,
           title="Буфер міняє нерівний приплив на рівний потік — ціною затримки")


# ── depth-tradeoff: мілкий проти глибокого буфера ─────────────────────────────
# Ідея: розкид затримки — це розподіл; глибину ставлять на високий перцентиль.
# Мілко = малий лаг, але хвіст не влазить (underrun); глибоко = все влазить, але
# великий лаг. Компроміс — лінія перцентиля.
def fig_depth_tradeoff():
    W, H = 720, 340
    p = []
    ox, oy = 80, 250
    aw, ah = 560, 196

    # осі: горизонталь — затримка пакета, вертикаль — як часто така затримка
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 8, color=INK, sw=1.6))
    p.append(text(ox + aw, oy + 20, "затримка пакета", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 10, oy - ah - 2, "частота", size=11, color=INK, anchor="end", italic=True))

    # розподіл затримки: пік зліва, довгий хвіст управо
    def dens(t):  # t у [0..1]
        a = math.exp(-((t - 0.28) ** 2) / (2 * 0.10 ** 2))      # основна маса
        b = 0.22 * math.exp(-((t - 0.62) ** 2) / (2 * 0.22 ** 2))  # довгий хвіст
        return (a + b) / 1.0

    xs = [i / 300.0 for i in range(301)]
    base = max(dens(t) for t in xs)
    pts = []
    for t in xs:
        pts.append("%.1f,%.1f" % (ox + t * aw, oy - dens(t) / base * ah * 0.9))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), MUTED))

    # дві кандидат-глибини
    shallow = 0.30
    deep = 0.78
    xsh = ox + shallow * aw
    xdp = ox + deep * aw

    # мілкий буфер — заливка того, що ВЛАЗИТЬ; хвіст справа = underrun
    p.append(line(xsh, oy, xsh, oy - ah - 4, color=FIELD, sw=2.0, dash="5 4"))
    p.append(text(xsh, oy - ah - 12, "мілко", size=11, color=FIELD, bold=True))
    p.append(text(xsh, oy + 36, "малий лаг,\nале хвіст не влазить\n→ underrun",
                  size=10, color=FIELD))

    # глибокий буфер
    p.append(line(xdp, oy, xdp, oy - ah - 4, color=NEG, sw=2.0, dash="5 4"))
    p.append(text(xdp, oy - ah - 12, "глибоко", size=11, color=NEG, bold=True))
    p.append(text(xdp, oy + 36, "усе влазить,\nале великий лаг",
                  size=10, color=NEG))

    # заштрихований хвіст за «мілко» — частка пакетів, що спізняться
    tail = []
    for t in [i / 100.0 for i in range(int(shallow * 100), 101)]:
        tail.append("%.1f,%.1f" % (ox + t * aw, oy - dens(t) / base * ah * 0.9))
    tail = ["%.1f,%.1f" % (xsh, oy)] + tail + ["%.1f,%.1f" % (ox + aw, oy)]
    p.append('<polygon points="%s" fill="#fdecea" stroke="none" opacity="0.7"/>' % " ".join(tail))

    render(os.path.join(OUT, "depth-tradeoff.svg"), W, H, *p,
           title="Глибину буфера ставлять на перцентиль розкиду затримки")


# ── underrun-overrun: дві аварії буфера ───────────────────────────────────────
# Ідея: буфер як черга комірок. Порожньо → нічого видати (затинання). Повно →
# новий пакет нікуди покласти (скид). Здоровий стан — між цими краями.
def fig_underrun_overrun():
    W, H = 720, 300
    p = []
    cell = 26
    n = 7

    def buffer(cx, top, filled, lab, col, note):
        x0 = cx - n * cell / 2
        out = []
        for i in range(n):
            fill = col if i < filled else "#ffffff"
            out.append(rect(x0 + i * cell, top, cell, cell, fill=fill, stroke=INK, sw=1.4, rx=2))
        out.append(text(cx, top - 12, lab, size=12, color=INK, bold=True))
        out.append(text(cx, top + cell + 22, note, size=10, color=MUTED))
        return out, x0

    top = 120

    # 1) порожньо → underrun
    b1, x1 = buffer(170, top, 0, "порожньо", FIELD, "")
    p += b1
    p.append(arrow(x1 - 34, top + cell / 2, x1 - 6, top + cell / 2, color=MUTED, sw=1.6))   # приплив став
    p.append(text(x1 - 36, top + cell / 2 - 12, "немає\nпакетів", size=9, color=POS, anchor="end"))
    p.append(arrow(x1 + n * cell + 6, top + cell / 2, x1 + n * cell + 34, top + cell / 2, color=MUTED, sw=1.6))
    p.append(text(170, top + cell + 44, "UNDERRUN: нічого видати → затинання",
                  size=11, color=POS, bold=True))

    # 2) повно → overrun
    b2, x2 = buffer(545, top, n, "повно", NEG, "")
    p += b2
    # пакет, що не влазить
    p.append(rect(x2 + n * cell + 10, top, cell, cell, fill="#fdecea", stroke=POS, sw=1.8, rx=2))
    p.append(text(x2 + n * cell + 10 + cell / 2, top + cell + 14, "✕", size=14, color=POS, bold=True))
    p.append(arrow(x2 + n * cell + 10 + cell / 2, top - 8,
                   x2 + n * cell + 10 + cell / 2, top - 2, color=POS, sw=1.6))
    p.append(text(x2 + n * cell + 10 + cell / 2, top - 14, "новий\nпакет", size=9, color=POS))
    p.append(text(545, top + cell + 44, "OVERRUN: нікуди покласти → скид (і лаг)",
                  size=11, color=NEG, bold=True))

    # здоровий стан — між краями
    p.append(text(W / 2, H - 28,
                  "Здоровий буфер тримається між краями: не пустіє й не переповнюється",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "underrun-overrun.svg"), W, H, *p,
           title="Дві аварії буфера: порожньо й повно")


if __name__ == "__main__":
    fig_uneven_to_even()
    fig_depth_tradeoff()
    fig_underrun_overrun()
    print("OK: figures written to", OUT)
