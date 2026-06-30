# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Мертва зона: вхід → вихід із пласкою «полицею» ±VBE ───────────────────
def fig_deadzone():
    W, H = 760, 360
    frags = []

    # Ліва панель: передавальна крива vin -> vout з мертвою зоною
    px, py, pw, phh = 60, 70, 300, 240
    cx0 = px + pw / 2          # центр (vin=0)
    cy0 = py + phh / 2         # центр (vout=0)
    frags.append(rect(px, py, pw, phh, fill="#ffffff", stroke=MUTED, sw=1.2))
    # осі
    frags.append(line(px + 10, cy0, px + pw - 10, cy0, color=MUTED, sw=1.2))   # vin
    frags.append(line(cx0, py + 10, cx0, py + phh - 10, color=MUTED, sw=1.2))   # vout
    frags.append(text(px + pw - 12, cy0 - 6, "vᵢₙ", size=12, color=MUTED, anchor="end", italic=True))
    frags.append(text(cx0 + 8, py + 18, "vₒᵤₜ", size=12, color=MUTED, anchor="start", italic=True))

    dz = 46     # пів-ширина мертвої зони у px (≈ VBE)
    sl = 150    # розмах активної ділянки
    # передавальна крива (3 відрізки): нахил, полиця, нахил
    frags.append(line(cx0 - dz - 95, cy0 - 95, cx0 - dz, cy0, color=POS, sw=2.6))
    frags.append(line(cx0 - dz, cy0, cx0 + dz, cy0, color=POS, sw=2.6))
    frags.append(line(cx0 + dz, cy0, cx0 + dz + 95, cy0 + 95, color=POS, sw=2.6))
    # ідеал (пунктир — пряма через нуль)
    frags.append(line(cx0 - 110, cy0 - 110, cx0 + 110, cy0 + 110, color=MUTED, sw=1.2, dash="4,4"))
    # позначити мертву зону
    frags.append(line(cx0 - dz, cy0 - 4, cx0 - dz, cy0 + 4, color=INK, sw=1.4))
    frags.append(line(cx0 + dz, cy0 - 4, cx0 + dz, cy0 + 4, color=INK, sw=1.4))
    bx, by, bw, bh = cx0 - 62, py + phh + 8, 124, 0
    frags.append(text(cx0, py + phh + 22, "−0.6 В … +0.6 В", size=12, color=INK, bold=True))
    frags.append(text(cx0, py + phh + 38, "мертва зона", size=11, color=MUTED))
    frags.append(text(px + pw / 2, py - 12, "Передавальна крива (клас B)", size=14, color=INK, bold=True))
    # підпис ідеалу
    frags.append(text(cx0 + 96, cy0 + 96, "ідеал", size=11, color=MUTED, anchor="start", italic=True))

    # Права панель: вхідна синусоїда (сіра) та вихід зі «східцем» біля нуля
    qx, qy, qw, qhh = 420, 70, 300, 240
    mid = qy + qhh / 2
    frags.append(rect(qx, qy, qw, qhh, fill="#ffffff", stroke=MUTED, sw=1.2))
    frags.append(line(qx + 8, mid, qx + qw - 8, mid, color=MUTED, sw=1.0))
    frags.append(text(qx + qw - 12, mid - 6, "t", size=12, color=MUTED, anchor="end", italic=True))

    n = 160
    amp = 92
    dead = 0.20            # частка амплітуди, що «з'їдається» мертвою зоною
    # вхід (чистий синус, сірий)
    pin = []
    pout = []
    for i in range(n + 1):
        t = i / n
        s = math.sin(2 * math.pi * t)
        x = qx + 12 + (qw - 24) * t
        pin.append((x, mid - amp * s))
        # вихід: відняти мертву зону навколо нуля (м'яке стискання біля 0)
        if s > dead:
            o = (s - dead) / (1 - dead)
        elif s < -dead:
            o = (s + dead) / (1 - dead)
        else:
            o = 0.0
        pout.append((x, mid - amp * o))
    din = "M %.1f %.1f " % pin[0] + " ".join("L %.1f %.1f" % p for p in pin[1:])
    dout = "M %.1f %.1f " % pout[0] + " ".join("L %.1f %.1f" % p for p in pout[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4,4"/>' % (din, MUTED))
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dout, POS))
    frags.append(text(qx + qw / 2, qy - 12, "Що чути на виході", size=14, color=INK, bold=True))
    # стрілка на «східець» біля переходу через нуль
    zx = qx + 12 + (qw - 24) * 0.5
    frags.append(text(qx + qw / 2, qy + qhh + 22, "сходинка на кожному переході через нуль", size=11, color=MUTED))
    frags.append(text(qx + 16, mid - amp - 4, "вхід (чистий)", size=11, color=MUTED, anchor="start", italic=True))

    render(os.path.join(OUT, 'crossover-deadzone.svg'), W, H, *frags,
           title="Перехідне спотворення: пласка «полиця» там, де обидва прилади закриті")


# ── 2. Двотактний вихід ОП із зміщенням (діоди / VBE-помножувач) ─────────────
def fig_pushpull():
    W, H = 780, 400
    frags = []
    midx = 360
    vtop, vbot = 60, 350
    # шини живлення
    frags.append(line(120, vtop, 720, vtop, color=POS, sw=2.0))
    frags.append(text(116, vtop + 4, "+V", size=13, color=POS, anchor="end", bold=True))
    frags.append(line(120, vbot, 720, vbot, color=NEG, sw=2.0))
    frags.append(text(116, vbot + 4, "−V", size=13, color=NEG, anchor="end", bold=True))

    # NPN (верхній, штовхає вгору) — спрощений блок
    npn_y = 120
    bnpn, wn, hn = midx + 30, 116, 56
    frags.append(rect(bnpn, npn_y, wn, hn, fill="#fdecea", stroke=POS, sw=1.6))
    frags.append(text(bnpn + wn / 2, npn_y + 22, "NPN", size=14, color=POS, bold=True))
    frags.append(text(bnpn + wn / 2, npn_y + 42, "тягне до +V", size=11, color=MUTED))
    # колектор до +V
    frags.append(line(bnpn + wn / 2, vtop, bnpn + wn / 2, npn_y, color=INK, sw=1.6))

    # PNP (нижній, тягне вниз)
    pnp_y = 224
    bpnp = bnpn
    frags.append(rect(bpnp, pnp_y, wn, hn, fill="#eaf0fd", stroke=NEG, sw=1.6))
    frags.append(text(bpnp + wn / 2, pnp_y + 22, "PNP", size=14, color=NEG, bold=True))
    frags.append(text(bpnp + wn / 2, pnp_y + 42, "тягне до −V", size=11, color=MUTED))
    frags.append(line(bpnp + wn / 2, pnp_y + hn, bpnp + wn / 2, vbot, color=INK, sw=1.6))

    # спільний вихід (емітери разом) праворуч до навантаження
    outx = bnpn + wn + 30
    oy = (npn_y + hn + pnp_y) / 2
    frags.append(line(bnpn + wn, npn_y + hn / 2, outx, npn_y + hn / 2, color=INK, sw=1.6))
    frags.append(line(bpnp + wn, pnp_y + hn / 2, outx, pnp_y + hn / 2, color=INK, sw=1.6))
    frags.append(line(outx, npn_y + hn / 2, outx, pnp_y + hn / 2, color=INK, sw=1.6))
    frags.append(circle(outx, oy, 3.5, fill=INK, stroke=INK, sw=1))
    frags.append(line(outx, oy, outx + 70, oy, color=INK, sw=1.6))
    frags.append(text(outx + 76, oy + 4, "вихід", size=13, color=INK, anchor="start", bold=True))
    # навантаження
    frags.append(rect(outx + 132, oy - 22, 18, 44, fill="#ffffff", stroke=INK, sw=1.4, rx=3))
    frags.append(line(outx + 141, oy + 22, outx + 141, oy + 44, color=INK, sw=1.6))
    frags.append(line(outx + 124, oy + 44, outx + 158, oy + 44, color=INK, sw=1.6))
    frags.append(text(outx + 165, oy + 4, "Rн", size=12, color=MUTED, anchor="start"))

    # блок зміщення між базами (діоди / VBE-помножувач)
    bxw = 116
    bbx = midx - 150
    bby = oy - 56
    bb, w2, h2 = bbx, bxw, 112
    frags.append(rect(bb, bby, w2, h2, fill="#e3f4e9", stroke=FIELD, sw=1.8))
    frags.append(text(bb + w2 / 2, bby + 26, "зміщення", size=13, color=FIELD, bold=True))
    frags.append(text(bb + w2 / 2, bby + 46, "≈ 2·VBE", size=12, color=INK, bold=True))
    frags.append(text(bb + w2 / 2, bby + 64, "діоди або", size=11, color=MUTED))
    frags.append(text(bb + w2 / 2, bby + 80, "VBE-помножувач", size=11, color=MUTED))
    # з'єднання верх блока -> база NPN, низ блока -> база PNP
    frags.append(line(bb + w2, bby + 14, bnpn, npn_y + hn / 2, color=INK, sw=1.6))
    frags.append(text(bnpn - 6, npn_y + hn / 2 - 6, "база", size=10, color=MUTED, anchor="end"))
    frags.append(line(bb + w2, bby + h2 - 14, bpnp, pnp_y + hn / 2, color=INK, sw=1.6))
    frags.append(text(bpnp - 6, pnp_y + hn / 2 + 14, "база", size=10, color=MUTED, anchor="end"))
    # вхід (сигнал від попереднього каскаду) -> в середину блока зміщення
    frags.append(line(120, oy, bb, oy, color=INK, sw=1.6))
    frags.append(circle(bb + w2 / 2, oy, 0))  # noop keep symmetry
    frags.append(text(118, oy - 8, "сигнал", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(118, oy + 18, "(від каскаду", size=10, color=MUTED, anchor="start"))
    frags.append(text(118, oy + 31, "підсилення)", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'pushpull-bias.svg'), W, H, *frags,
           title="Двотактний вихід: NPN угору, PNP униз, зміщення тримає обидва ледь відкритими")


# ── 3. Клас B vs клас AB: як мале зміщення зшиває дві половинки ──────────────
def fig_b_vs_ab():
    W, H = 760, 350
    frags = []

    def panel(px, title, bias):
        py, pw, phh = px[1], 300, 230
        x0 = px[0]
        cx0 = x0 + pw / 2
        cy0 = py + phh / 2
        frags.append(rect(x0, py, pw, phh, fill="#ffffff", stroke=MUTED, sw=1.2))
        frags.append(line(x0 + 10, cy0, x0 + pw - 10, cy0, color=MUTED, sw=1.0))
        frags.append(line(cx0, py + 10, cx0, py + phh - 10, color=MUTED, sw=1.0))
        frags.append(text(x0 + pw - 12, cy0 - 6, "vᵢₙ", size=11, color=MUTED, anchor="end", italic=True))
        frags.append(text(cx0 + 8, py + 18, "iₙₐв", size=11, color=MUTED, anchor="start", italic=True))

        span = 120
        # половинка NPN (верхня, +), PNP (нижня, −) — кожна вмикається з порога VBE
        thr = max(0.0, 46 - bias)   # поріг у px: при bias=0 порожнеча 2*46; при AB майже стик
        # NPN: від +thr вправо вгору
        frags.append(line(cx0 + thr, cy0, cx0 + thr + span, cy0 - span, color=POS, sw=2.4))
        # PNP: від −thr вліво вниз
        frags.append(line(cx0 - thr, cy0, cx0 - thr - span, cy0 + span, color=NEG, sw=2.4))
        if bias == 0:
            # пласка полиця між порогами
            frags.append(line(cx0 - thr, cy0, cx0 + thr, cy0, color=INK, sw=2.4))
            frags.append(text(cx0, cy0 + 22, "розрив", size=11, color=INK, bold=True))
        else:
            # перекриття: обидві ведуть, сума гладка через нуль
            frags.append(line(cx0 - thr, cy0 + 6, cx0 + thr, cy0 - 6, color=FIELD, sw=2.4))
            frags.append(text(cx0 + 2, cy0 + 24, "обидві ведуть", size=11, color=FIELD, bold=True))
        frags.append(text(cx0, py - 12, title, size=14, color=INK, bold=True))
        # підписи половинок
        frags.append(text(cx0 + span - 6, cy0 - span + 4, "NPN", size=10, color=POS, anchor="end", bold=True))
        frags.append(text(cx0 - span + 6, cy0 + span - 2, "PNP", size=10, color=NEG, anchor="start", bold=True))

    panel((50, 70), "Клас B — без зміщення", 0)
    panel((420, 70), "Клас AB — мале зміщення", 40)
    frags.append(text(W / 2, H - 16,
                      "Те саме коло, різниця лише в струмі спокою: AB накладає кінці двох половинок і прибирає сходинку",
                      size=12, color=MUTED))
    render(os.path.join(OUT, 'class-b-vs-ab.svg'), W, H, *frags,
           title="Чим клас AB кращий за клас B: перекриття замість розриву")


# ── 4. Три схеми зміщення поряд: резистор / діоди / VBE-помножувач ───────────
def fig_three_biases():
    W, H = 780, 360
    frags = []

    def frame(x0, title, sub, ok):
        py, pw, phh = 64, 226, 214
        frags.append(rect(x0, py, pw, phh, fill="#ffffff", stroke=MUTED, sw=1.2))
        frags.append(text(x0 + pw / 2, py - 30, title, size=14, color=INK, bold=True))
        frags.append(text(x0 + pw / 2, py - 13, sub, size=11, color=MUTED))
        # шильдик термостеження внизу
        col = FIELD if ok else POS
        mark = "стежить за t°" if ok else "НЕ стежить за t°"
        frags.append(text(x0 + pw / 2, py + phh + 20, mark, size=12, color=col, bold=True))
        return x0 + pw / 2, py, pw, phh

    # дві бази (входи зверху/знизу) і підпис струму підпору
    def bases(cx, py, phh):
        topy = py + 34
        boty = py + phh - 34
        frags.append(line(cx - 70, topy, cx + 70, topy, color=INK, sw=1.6))
        frags.append(line(cx - 70, boty, cx + 70, boty, color=INK, sw=1.6))
        frags.append(text(cx - 74, topy + 4, "база NPN", size=10, color=MUTED, anchor="end"))
        frags.append(text(cx - 74, boty + 4, "база PNP", size=10, color=MUTED, anchor="end"))
        # стрілка струму підпору
        frags.append(arrow(cx + 92, topy + 6, cx + 92, boty - 6, color=MUTED, sw=1.4))
        frags.append(text(cx + 98, (topy + boty) / 2, "I_bias", size=10, color=MUTED, anchor="start", italic=True))
        return topy, boty

    # ── панель 1: резистор ──
    cx1, py1, pw1, ph1 = frame(28, "Резистори", "грубо", False)
    t1, b1 = bases(cx1, py1, ph1)
    frags.append(line(cx1, t1, cx1, t1 + 26, color=INK, sw=1.6))
    rw, rh = 26, 56
    frags.append(rect(cx1 - rw / 2, t1 + 26, rw, rh, fill=FILL, stroke=INK, sw=1.5, rx=3))
    frags.append(text(cx1, t1 + 26 + rh / 2 + 4, "R", size=13, color=INK, bold=True))
    frags.append(line(cx1, t1 + 26 + rh, cx1, b1, color=INK, sw=1.6))
    frags.append(text(cx1, (t1 + b1) / 2 + 4, "I·R ≈ 1.2 В", size=11, color=INK, anchor="start", bold=True))

    # ── панель 2: два діоди ──
    cx2, py2, pw2, ph2 = frame(278, "Два діоди", "самозадавальне", True)
    t2, b2 = bases(cx2, py2, ph2)
    midd = (t2 + b2) / 2
    frags.append(line(cx2, t2, cx2, midd - 18, color=INK, sw=1.6))
    # діод 1 (трикутник + риска), діод 2
    def diode(cx, cy, col=INK):
        s = 11
        frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                     % (cx - s, cy - s, cx + s, cy - s, cx, cy + s, "#eef1f4"))
        frags.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
                     % (cx - s, cy - s, cx + s, cy - s, cx, cy + s, col))
        frags.append(line(cx - s, cy + s, cx + s, cy + s, color=col, sw=1.8))
    diode(cx2, midd - 18)
    diode(cx2, midd + 18)
    frags.append(line(cx2, midd + 29, cx2, b2, color=INK, sw=1.6))
    frags.append(text(cx2 + 22, midd - 14, "VBE", size=10, color=MUTED, anchor="start"))
    frags.append(text(cx2 + 22, midd + 22, "VBE", size=10, color=MUTED, anchor="start"))
    frags.append(text(cx2 - 18, midd + 4, "≈2·VBE", size=11, color=INK, anchor="end", bold=True))

    # ── панель 3: VBE-помножувач ──
    cx3, py3, pw3, ph3 = frame(528, "VBE-помножувач", "точно, регульовано", True)
    t3, b3 = bases(cx3, py3, ph3)
    # транзистор Q як кружок
    qy = (t3 + b3) / 2
    frags.append(line(cx3, t3, cx3, qy - 16, color=INK, sw=1.6))
    frags.append(line(cx3, qy + 16, cx3, b3, color=INK, sw=1.6))
    frags.append(circle(cx3, qy, 16, fill="#e3f4e9", stroke=FIELD, sw=1.8))
    frags.append(text(cx3, qy + 5, "Q", size=13, color=FIELD, bold=True))
    # Дільник R1/R2 у боковій рейці: верх(колектор) → R1 → відвід на базу → R2 → низ(емітер)
    rx0 = cx3 + 46
    # рейка від верхнього вузла донизу
    frags.append(line(cx3, qy - 16, rx0, qy - 16, color=INK, sw=1.4))   # верх Q → рейка
    frags.append(line(cx3, qy + 16, rx0, qy + 16, color=INK, sw=1.4))   # низ Q → рейка
    # R1 (між верхнім вузлом і відводом бази)
    frags.append(rect(rx0 - 9, qy - 12, 18, 22, fill=FILL, stroke=INK, sw=1.3, rx=3))
    frags.append(text(rx0 + 15, qy + 1, "R1", size=10, color=INK, anchor="start", bold=True))
    frags.append(line(rx0, qy - 16, rx0, qy - 12, color=INK, sw=1.4))
    # відвід середньої точки дільника на базу Q
    baseY = qy + 10
    frags.append(line(rx0, qy + 10, rx0, qy + 10, color=INK, sw=1.4))
    frags.append(line(cx3 + 16, qy, rx0, baseY, color=INK, sw=1.4))     # база Q ← середина дільника
    # R2 (між відводом бази й нижнім вузлом)
    frags.append(rect(rx0 - 9, qy + 18, 18, 22, fill=FILL, stroke=INK, sw=1.3, rx=3))
    frags.append(text(rx0 + 15, qy + 31, "R2", size=10, color=INK, anchor="start", bold=True))
    frags.append(line(rx0, qy + 10, rx0, qy + 18, color=INK, sw=1.4))
    frags.append(line(rx0, qy + 40, rx0, qy + 16, color=INK, sw=1.4))
    frags.append(text(cx3 - 22, qy + 4, "VBE·(1+R1/R2)", size=10, color=INK, anchor="end", bold=True))

    frags.append(text(W / 2, H - 12,
                      "Усі три тримають ≈2·VBE між базами; резистор не стежить за теплом, діоди й помножувач — стежать (на спільному радіаторі)",
                      size=11, color=MUTED))
    render(os.path.join(OUT, 'three-biases.svg'), W, H, *frags,
           title="Три схеми зміщення класу AB: резистори, діоди, VBE-помножувач")


if __name__ == '__main__':
    fig_deadzone()
    fig_pushpull()
    fig_b_vs_ab()
    fig_three_biases()
    print("OK figures written to", OUT)
