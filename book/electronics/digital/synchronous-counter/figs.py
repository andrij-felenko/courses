# -*- coding: utf-8 -*-
"""Фігури до теми «Синхронний лічильник».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def _ff(x, y, w, h, label):
    """Прямокутник тригера з трикутником такту знизу-зліва і підписом усередині."""
    out = rect(x, y, w, h, fill="#eef2f7", sw=1.6)
    out += text(x + w / 2, y + h / 2 + 5, label, size=14, bold=True)
    # трикутник «по фронту» на тактовому вході (ліва грань, низ)
    ty = y + h - 14
    out += ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
            'stroke="%s" stroke-width="1.4"/>' % (x, ty - 6, x + 11, ty, x, ty + 6, INK))
    out += text(x + 16, ty + 4, "T", size=11, color=MUTED, anchor="start")
    return out


# ── 1. Кістяк: спільний такт + ланцюг AND, що збирає умову перемикання ──────
def fig_architecture():
    W, H = 760, 430
    parts = []
    parts.append(text(W / 2, 28, "Синхронний лічильник: спільний такт + ланцюг дозволу", size=16, bold=True))

    # чотири T-тригери в ряд (молодший ліворуч)
    ffw, ffh = 86, 64
    ys = 150
    xs = [70, 230, 400, 570]
    labels = ["Q0", "Q1", "Q2", "Q3"]
    for x, lab in zip(xs, labels):
        parts.append(_ff(x, ys, ffw, ffh, lab))

    # спільна тактова шина внизу — до кожного трикутника
    clky = ys + ffh + 46
    parts.append(line(40, clky, W - 30, clky, color=POS, sw=2.4))
    parts.append(text(46, clky - 8, "ТАКТ (спільний для всіх)", size=12, color=POS, anchor="start", bold=True))
    for x in xs:
        parts.append(line(x, ys + ffh - 14, x, clky, color=POS, sw=2.0))
        parts.append(circle(x, clky, 3.2, fill=POS, stroke=POS))

    # вхід T кожного тригера — згори; T0=1, далі — AND усіх нижчих Q
    ty = ys - 58
    # ланцюг AND-вентилів між тригерами (над ними)
    def andgate(cx, cy):
        # маленький символ AND (D-подібний)
        r = 13
        s = ('<path d="M%.1f %.1f L%.1f %.1f A%.1f %.1f 0 0 1 %.1f %.1f L%.1f %.1f z" '
             'fill="#fff" stroke="%s" stroke-width="1.5"/>'
             % (cx - r, cy - r, cx, cy - r, r, r, cx, cy + r, cx - r, cy + r, INK))
        s += text(cx - 4, cy + 4, "&", size=13, bold=True)
        return s

    # T0 = 1 (молодший завжди перемикається)
    parts.append(line(xs[0] + ffw / 2, ty, xs[0] + ffw / 2, ys, color=FIELD, sw=2.0))
    box, bw, bh = textbox(xs[0] + ffw / 2, ty - 6, "T0 = 1", size=12, fill="#eafaf0",
                          stroke=FIELD, color=FIELD, bold=True, pad=7)
    parts.append(box)

    # для Q1,Q2,Q3 — AND-вентиль, що дає сигнал «усі нижчі = 1»
    andx = [xs[1] + ffw / 2, xs[2] + ffw / 2, xs[3] + ffw / 2]
    for i, ax in enumerate(andx):
        gy = ty
        parts.append(andgate(ax, gy))
        # вихід вентиля → вниз у T тригера
        parts.append(line(ax, gy + 13, ax, ys, color=FIELD, sw=2.0))
        parts.append(text(ax + 18, ys - 6, "T", size=11, color=MUTED, anchor="start"))

    # підпис до ланцюга AND
    cap, cw, ch = textbox(W / 2, 372,
                          "T кожного старшого біта = «усі нижчі біти зараз = 1»  (це і є перенос)",
                          size=12.5, fill="#eafaf0", stroke=FIELD, color="#1e6b40", pad=9)
    parts.append(cap)

    # стрілочки «усі нижчі Q» у кожен AND (схематично — від попередніх Q)
    for i, ax in enumerate(andx):
        # від найближчого нижчого тригера вгору-вбік у вентиль (схематична лінія дозволу)
        srcx = xs[i] + ffw / 2
        parts.append(line(srcx, ys - 6, srcx, ty + 24, color=MUTED, sw=1.2, dash="3,3"))
        parts.append(line(srcx, ty + 24, ax - 13, ty + 24, color=MUTED, sw=1.2, dash="3,3"))
        parts.append(line(ax - 13, ty + 24, ax - 13, ty, color=MUTED, sw=1.2, dash="3,3"))

    parts.append(text(W / 2, 405, "молодший Q0 ◄———————————————————————————► старший Q3",
                      size=11, color=MUTED))
    return render(os.path.join(IMG, "architecture.svg"), W, H, *parts)


# ── 2. Часова діаграма: усі біти міняються РАЗОМ (синхр.) проти зсуву (ripple)
def fig_timing():
    W, H = 760, 470
    parts = []
    parts.append(text(W / 2, 26, "Усі біти міняються разом (синхронний) проти зсуву (ланцюговий)", size=15, bold=True))

    x0, span = 70, 600
    n = 8                      # тактів
    step = span / n
    # тактова лінія зверху
    def wave(y, bits, color=INK, hi=24):
        pts = [(x0, y)]
        prev = bits[0]
        cur = x0
        # будуємо меандр за списком рівнів на кожен такт (рівень тримається весь такт)
        ptsl = []
        x = x0
        lvl = bits[0]
        ptsl.append((x, y - hi if lvl else y))
        for b in bits:
            yy = y - hi if b else y
            ptsl.append((x, yy))
            ptsl.append((x + step, yy))
            x += step
        d = " ".join("%.1f,%.1f" % p for p in ptsl)
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, color)

    # послідовність рахунку 0..7 → біти Q0,Q1,Q2 по тактах
    counts = list(range(n + 1))
    q0 = [(c >> 0) & 1 for c in counts]
    q1 = [(c >> 1) & 1 for c in counts]
    q2 = [(c >> 2) & 1 for c in counts]

    # ── СИНХРОННИЙ блок ──
    ytop = 80
    parts.append(text(x0 - 4, ytop - 14, "СИНХРОННИЙ — край фронту спільний", size=12.5,
                      color=FIELD, anchor="start", bold=True))
    rows = [("Q2", q2), ("Q1", q1), ("Q0", q0)]
    for i, (lab, bits) in enumerate(rows):
        yy = ytop + i * 44
        parts.append(text(x0 - 12, yy - 6, lab, size=12, anchor="end", bold=True))
        parts.append(wave(yy, bits[:n + 1]))
    # вертикальні штрихи фронтів — усі переходи строго на лінії такту
    for k in range(1, n + 1):
        xx = x0 + k * step
        parts.append(line(xx, ytop - 28, xx, ytop + 3 * 44 - 20, color="#cfd6df", sw=1, dash="2,3"))
    parts.append(text(x0 + span / 2, ytop + 3 * 44 + 6,
                      "усі біти перемикаються РАЗОМ на фронті — числа «битого» нема", size=12,
                      color="#1e6b40"))

    # ── ЛАНЦЮГОВИЙ блок (зі зсувом) ──
    ybot = 290
    parts.append(text(x0 - 4, ybot - 14, "ЛАНЦЮГОВИЙ — старші біти відстають (затримки складаються)",
                      size=12.5, color=POS, anchor="start", bold=True))
    # імітуємо зсув: Q1 відстає на d, Q2 — на 2d від ідеального фронту
    d = step * 0.16

    def wave_skew(y, bits, delay, hi=24, color=POS):
        ptsl = []
        x = x0
        ptsl.append((x, y - hi if bits[0] else y))
        for k, b in enumerate(bits):
            xx = x0 + k * step + (delay if k > 0 else 0)
            yy = y - hi if b else y
            ptsl.append((xx, yy))
            nextx = x0 + (k + 1) * step + delay
            ptsl.append((nextx, yy))
        d2 = " ".join("%.1f,%.1f" % p for p in ptsl)
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d2, color)

    parts.append(text(x0 - 12, ybot - 6, "Q2", size=12, anchor="end", bold=True))
    parts.append(wave_skew(ybot, q2[:n + 1], 2 * d))
    parts.append(text(x0 - 12, ybot + 44 - 6, "Q1", size=12, anchor="end", bold=True))
    parts.append(wave_skew(ybot + 44, q1[:n + 1], d))
    parts.append(text(x0 - 12, ybot + 88 - 6, "Q0", size=12, anchor="end", bold=True))
    parts.append(wave(ybot + 88, q0[:n + 1], color=POS))
    for k in range(1, n + 1):
        xx = x0 + k * step
        parts.append(line(xx, ybot - 28, xx, ybot + 3 * 44 - 20, color="#f0d0cc", sw=1, dash="2,3"))
    parts.append(text(x0 + span / 2, ybot + 3 * 44 + 6,
                      "перенос біжить розрядами — на мить виходить хибне число (глітч)",
                      size=12, color=POS))
    return render(os.path.join(IMG, "timing.svg"), W, H, *parts)


# ── 3. Каскад і стеля частоти: одна логіка переносу, бюджет такту незмінний ──
def fig_cascade():
    W, H = 760, 360
    parts = []
    parts.append(text(W / 2, 26, "Каскад: перенос між блоками — стеля частоти від ОДНОГО шляху", size=15, bold=True))

    # два блоки-лічильники, з'єднані переносом
    bw, bh = 200, 92
    y = 90
    x1, x2 = 80, 470
    parts.append(rect(x1, y, bw, bh, fill="#eef2f7", sw=1.6))
    parts.append(text(x1 + bw / 2, y + 26, "Лічильник 0..3", size=13, bold=True))
    parts.append(text(x1 + bw / 2, y + 50, "Q0 Q1 Q2 Q3", size=12, color=MUTED))
    parts.append(rect(x2, y, bw, bh, fill="#eef2f7", sw=1.6))
    parts.append(text(x2 + bw / 2, y + 26, "Лічильник 4..7", size=13, bold=True))
    parts.append(text(x2 + bw / 2, y + 50, "Q4 Q5 Q6 Q7", size=12, color=MUTED))

    # перенос (carry-out → carry-in)
    parts.append(arrow(x1 + bw, y + 70, x2, y + 70, color=FIELD, sw=2.2))
    co, cw, ch = textbox((x1 + bw + x2) / 2, y + 70, "перенос\n(дозвіл лічити)", size=11,
                         fill="#eafaf0", stroke=FIELD, color="#1e6b40", pad=7)
    parts.append(co)

    # спільний такт під обидва
    clky = y + bh + 40
    parts.append(line(50, clky, W - 40, clky, color=POS, sw=2.4))
    parts.append(text(56, clky - 8, "ТАКТ — спільний для ВСІХ розрядів", size=12, color=POS, anchor="start", bold=True))
    for cx in (x1 + bw / 2, x2 + bw / 2):
        parts.append(line(cx, y + bh, cx, clky, color=POS, sw=2.0))
        parts.append(circle(cx, clky, 3.2, fill=POS, stroke=POS))

    # підсумкова рамка про стелю частоти
    note, nw, nh = textbox(W / 2, 300,
                           "f_макс = 1 / (t_тригера + t_переносу + t_setup) — НЕ залежить від числа розрядів",
                           size=12.5, fill="#eef2f7", color=INK, bold=False, pad=10)
    parts.append(note)
    return render(os.path.join(IMG, "cascade.svg"), W, H, *parts)


# ── 4. Блок-схема класу: що всередині корпусу синхронного лічильника-чипа ─────
def fig_ic_block():
    W, H = 760, 400
    parts = []
    parts.append(text(W / 2, 26, "Усередині чипа: чотири тригери + перенос + мультиплексор завантаження", size=14.5, bold=True))

    # великий корпус
    bx, by, bw, bh = 150, 70, 460, 250
    parts.append(rect(bx, by, bw, bh, fill="#f7f9fc", sw=1.8))

    # ряд із 4 тригерів усередині
    ffw, ffh = 78, 52
    ffy = by + 150
    ffxs = [bx + 30, bx + 140, bx + 250, bx + 360]
    for x, lab in zip(ffxs, ["Q0", "Q1", "Q2", "Q3"]):
        parts.append(_ff(x, ffy, ffw, ffh, lab))

    # мультиплексор завантаження над кожним тригером (смужка)
    muxy = by + 96
    mux, mw, mh = textbox(bx + bw / 2, muxy, "мультиплексор: рахувати  або  завантажити Dn", size=12,
                          fill="#eef2f7", stroke=LINE, color=INK, pad=8, min_w=bw - 70)
    parts.append(mux)
    for x in ffxs:
        parts.append(line(x + ffw / 2, muxy + mh / 2, x + ffw / 2, ffy, color=MUTED, sw=1.4))

    # ланцюг прискореного переносу (внизу всередині)
    coy = ffy + ffh + 26
    co, cw, ch = textbox(bx + bw / 2, coy, "прискорений перенос (look-ahead): «усі біти = максимум»",
                         size=11.5, fill="#eafaf0", stroke=FIELD, color="#1e6b40", pad=7, min_w=bw - 90)
    parts.append(co)

    # входи ліворуч
    inlabels = ["CLK  (такт)", "LOAD (заванта-\nження)", "CLR  (скид)", "EN   (дозвіл)"]
    iny = [by + 40, by + 95, by + 150, by + 205]
    for lab, yy in zip(inlabels, iny):
        parts.append(arrow(30, yy, bx, yy, color=NEG, sw=1.8))
        parts.append(mtext(30, yy - 8, lab, size=11, color=NEG, anchor="start"))

    # входи даних Dn — знизу
    parts.append(arrow(bx + bw / 2, H - 20, bx + bw / 2, by + bh, color=NEG, sw=1.8))
    parts.append(text(bx + bw / 2, H - 26, "D0..D3 (число для завантаження)", size=11, color=NEG))

    # виходи праворуч: Q0..Q3 і RCO
    outy = [by + 60, by + 110, by + 160, by + 210]
    for i, yy in enumerate(outy):
        parts.append(arrow(bx + bw, yy, bx + bw + 90, yy, color=POS, sw=1.8))
        parts.append(text(bx + bw + 96, yy + 4, "Q%d" % i, size=11, color=POS, anchor="start", bold=True))
    ry = by + 235
    parts.append(arrow(bx + bw, ry, bx + bw + 90, ry, color=FIELD, sw=2.0))
    parts.append(text(bx + bw + 96, ry + 4, "RCO", size=11, color="#1e6b40", anchor="start", bold=True))

    parts.append(text(W / 2, H - 6, "керма — жменя входів; майже все решта корпусу — виходи Q і перенос RCO",
                      size=11, color=MUTED))
    return render(os.path.join(IMG, "ic-block.svg"), W, H, *parts)


# ── 5. Типова розпіновка DIP-16 (узагальнена, без партномера) ────────────────
def fig_ic_pinout():
    W, H = 620, 470
    parts = []
    parts.append(text(W / 2, 26, "Типова розпіновка: 4-розрядний синхронний лічильник (DIP-16)", size=14, bold=True))

    # корпус
    bx, by, bw, bh = 210, 60, 200, 370
    parts.append(rect(bx, by, bw, bh, fill="#eef2f7", sw=1.8))
    # виїмка-ключ згори
    parts.append('<path d="M%.1f %.1f A14 14 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (bx + bw / 2 - 14, by, bx + bw / 2 + 14, by, LINE))

    left = [("1", "CLR  скид"), ("2", "CLK  такт"), ("3", "LOAD заванта-ж."),
            ("4", "ENP  дозвіл-1"), ("5", "ENT  дозвіл-2"),
            ("6", "D0"), ("7", "D1"), ("8", "GND")]
    right = [("16", "VCC"), ("15", "RCO  перенос"), ("14", "Q0"), ("13", "Q1"),
             ("12", "Q2"), ("11", "Q3"), ("10", "D3"), ("9", "D2")]

    n = 8
    ph = (bh - 30) / (n - 1)
    y0 = by + 24
    pin_w, pin_h = 20, 12
    for i, (num, lab) in enumerate(left):
        yy = y0 + i * ph
        parts.append(rect(bx - pin_w, yy - pin_h / 2, pin_w, pin_h, fill="#cfd6df", sw=1.0, rx=2))
        parts.append(text(bx - pin_w - 6, yy + 4, num, size=10, color=MUTED, anchor="end"))
        col = NEG if lab not in ("GND",) else INK
        parts.append(text(bx + 8, yy + 4, lab, size=10.5, color=col, anchor="start"))
    for i, (num, lab) in enumerate(right):
        yy = y0 + i * ph
        parts.append(rect(bx + bw, yy - pin_h / 2, pin_w, pin_h, fill="#cfd6df", sw=1.0, rx=2))
        parts.append(text(bx + bw + pin_w + 6, yy + 4, num, size=10, color=MUTED, anchor="start"))
        if lab.startswith("Q") or lab.startswith("RCO"):
            col = POS if lab.startswith("Q") else "#1e6b40"
        elif lab == "VCC":
            col = INK
        else:
            col = NEG
        parts.append(text(bx + bw - 8, yy + 4, lab, size=10.5, color=col, anchor="end", bold=lab.startswith("RCO")))

    # легенда кольору
    ly = H - 40
    parts.append(text(bx + bw / 2, by + bh / 2 - 8, "синхронний", size=12, color=MUTED, bold=True))
    parts.append(text(bx + bw / 2, by + bh / 2 + 10, "лічильник", size=12, color=MUTED, bold=True))
    leg, lw, lh = textbox(W / 2, ly, "сині — входи керма й даних · червоні — виходи Q · зелений — перенос RCO",
                          size=10.5, fill="#ffffff", stroke=LINE, color=INK, pad=8)
    parts.append(leg)
    return render(os.path.join(IMG, "ic-pinout.svg"), W, H, *parts)


# ── 6. Каскад двох чипів: RCO → ENT, спільний такт, ENP як головний дозвіл ────
def fig_ic_cascade():
    W, H = 760, 380
    parts = []
    parts.append(text(W / 2, 26, "Каскад чипів: RCO молодшого → ENT старшого, такт спільний", size=14, bold=True))

    bw, bh = 210, 120
    y = 80
    x1, x2 = 70, 470
    for x, tag, bits in ((x1, "молодший чип", "Q0..Q3"), (x2, "старший чип", "Q4..Q7")):
        parts.append(rect(x, y, bw, bh, fill="#eef2f7", sw=1.6))
        parts.append(text(x + bw / 2, y + 24, tag, size=12.5, bold=True))
        parts.append(text(x + bw / 2, y + 48, bits, size=11.5, color=MUTED))
        parts.append(text(x + 12, y + 82, "ENT", size=10.5, color=NEG, anchor="start"))
        parts.append(text(x + 12, y + 100, "ENP", size=10.5, color=NEG, anchor="start"))
        parts.append(text(x + bw - 12, y + 88, "RCO", size=10.5, color="#1e6b40", anchor="end", bold=True))

    # RCO молодшого → ENT старшого
    parts.append(arrow(x1 + bw, y + 88, x2, y + 82, color=FIELD, sw=2.2))
    rc, rw, rh = textbox((x1 + bw + x2) / 2, y + 60,
                         "RCO: один такт «переповнено»\n→ дозволяє старшому лічити крок", size=10.5,
                         fill="#eafaf0", stroke=FIELD, color="#1e6b40", pad=7)
    parts.append(rc)

    # головний дозвіл на ENP обох
    eny = y + bh + 34
    parts.append(line(40, eny, W - 40, eny, color=NEG, sw=2.0))
    parts.append(text(46, eny - 8, "EN (головний дозвіл рахунку) → ENP обох чипів + ENT молодшого",
                      size=11, color=NEG, anchor="start", bold=True))
    for cx in (x1 + 34, x2 + 34):
        parts.append(line(cx, y + bh, cx, eny, color=NEG, sw=1.6))
        parts.append(circle(cx, eny, 3.0, fill=NEG, stroke=NEG))

    # спільний такт
    clky = eny + 40
    parts.append(line(40, clky, W - 40, clky, color=POS, sw=2.4))
    parts.append(text(46, clky - 8, "ТАКТ — спільний для ВСІХ чипів (усі біти клацають разом)",
                      size=11, color=POS, anchor="start", bold=True))
    for cx in (x1 + bw / 2, x2 + bw / 2):
        parts.append(line(cx, y + bh, cx, clky, color=POS, sw=2.0))
        parts.append(circle(cx, clky, 3.2, fill=POS, stroke=POS))

    parts.append(text(W / 2, H - 8,
                      "хиба-пастка: RCO ворухне ENT, але НЕ ENP — головний «стоп» вішають на ENP",
                      size=10.5, color=MUTED))
    return render(os.path.join(IMG, "ic-cascade.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_architecture()
    fig_timing()
    fig_cascade()
    fig_ic_block()
    fig_ic_pinout()
    fig_ic_cascade()
    print("OK: 6 SVG ->", IMG)
