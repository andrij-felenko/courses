# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = "#0f172a"    # темне тло «кадру»
GOOD = "#16a34a"    # правильний зв'язок
BAD  = "#c0392b"    # хибний зв'язок
KP   = "#e08a1e"    # ключова точка


def _frame(x, y, w, h, fill=DARK):
    return rect(x, y, w, h, fill=fill, stroke=INK, sw=1.2, rx=8)


def _kp(cx, cy, r=5, col=KP):
    # ключова точка: кружечок із хрестиком-центром
    return (circle(cx, cy, r, fill="none", stroke=col, sw=2) +
            line(cx - r - 2, cy, cx + r + 2, cy, color=col, sw=1) +
            line(cx, cy - r - 2, cx, cy + r + 2, color=col, sw=1))


# ── what-is-matching: та сама сцена з двох боків → пари тих самих точок ─────────
# Ідея: два знімки однієї сцени з різних ракурсів; на кожному знайдено ключові
# точки, а лінії з'єднують ті, що показують ОДНЕ Й ТЕ САМЕ фізичне місце.

def fig_what_is_matching():
    W, H = 820, 380
    p = []
    bw, bh = 320, 236
    ys = 74
    xL, xR = 40, W - 40 - bw
    p.append(text(xL + bw / 2, ys - 14, "знімок A", size=11, color=NEG, bold=True))
    p.append(text(xR + bw / 2, ys - 14, "знімок B — та сама сцена, інший ракурс",
                  size=11, color=NEG, bold=True))
    p.append(_frame(xL, ys, bw, bh))
    p.append(_frame(xR, ys, bw, bh))

    # силует «будиночка» на обох — на правому зсунутий і трохи менший (інший ракурс)
    def house(ox, oy, s):
        pts = [(40, 160), (40, 80), (100, 40), (160, 80), (160, 160)]
        pts = [(ox + qx * s, oy + qy * s) for (qx, qy) in pts]
        poly = " ".join("%.0f,%.0f" % q for q in pts)
        out = ('<polygon points="%s" fill="#1e293b" stroke="#475569" '
               'stroke-width="1.4"/>' % poly)
        out += rect(ox + 88 * s, oy + 96 * s, 24 * s, 24 * s,
                    fill="#334155", stroke="#64748b", sw=1, rx=2)
        return out

    p.append(house(xL + 40, ys + 34, 1.0))
    p.append(house(xR + 74, ys + 60, 0.82))

    # чотири прикметні кути будиночка + їхні відповідники на правому знімку
    kpL = [(xL + 80, ys + 194), (xL + 140, ys + 74),
           (xL + 200, ys + 114), (xL + 80, ys + 114)]
    kpR = [(xR + 107, ys + 191), (xR + 156, ys + 93),
           (xR + 205, ys + 126), (xR + 107, ys + 126)]

    # ще по одній фоновій точці, яка є лише на одному знімку (без пари)
    kpL.append((xL + 270, ys + 56))
    kpR.append((xR + 44, ys + 206))

    # лінії-зв'язки для чотирьох справжніх пар
    for (ax, ay), (bx, by) in zip(kpL[:4], kpR[:4]):
        p.append(line(ax, ay, bx, by, color=GOOD, sw=1.6))
    for (qx, qy) in kpL:
        p.append(_kp(qx, qy))
    for (qx, qy) in kpR:
        p.append(_kp(qx, qy))
    # позначити безпарні точки
    p.append(text(kpL[4][0], kpL[4][1] - 10, "без пари", size=8, color=MUTED))
    p.append(text(kpR[4][0], kpR[4][1] + 16, "без пари", size=8, color=MUTED))

    p.append(fitbox(40, ys + bh + 18, W - 80, 40,
                    "Зіставлення знаходить на двох знімках ОДНІ Й ТІ САМІ фізичні місця й "
                    "з'єднує їх у пари (зелене).\nКожна пара каже: «ось цей куточок стіни тут "
                    "— і він же там». Що не має відповідника — лишається без пари.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "what-is-matching.svg"), W, H, *p,
           title="Зіставлення: знайти ту саму точку сцени на двох знімках")


# ── detect-describe-match: три стадії — знайти, описати, звірити ────────────────
# Ідея: спершу детектор знаходить прикметні точки; тоді кожну описують вектором-
# «відбитком» околу; тоді пари шукають за найближчим описом.

def fig_detect_describe_match():
    W, H = 820, 372
    p = []
    pw, ph = 232, 200
    ys = 92
    xs = [24, 294, 564]
    cols = [NEG, "#d98a00", GOOD]
    heads = ["1. ЗНАЙТИ точки", "2. ОПИСАТИ окіл", "3. ЗВІРИТИ описи"]
    for i in range(3):
        p.append(rect(xs[i], ys, pw, ph, fill="#fbfbfd", stroke=cols[i], sw=1.7, rx=12))
        p.append(text(xs[i] + pw / 2, ys + 22, heads[i], size=10.5, color=cols[i], bold=True))

    # 1) детектор: кадр із кількома прикметними точками
    x = xs[0]
    ix, iy, iw, ih = x + 24, ys + 40, pw - 48, 108
    p.append(_frame(ix, iy, iw, ih))
    for (dx, dy) in [(28, 34), (96, 26), (150, 62), (60, 84), (120, 92)]:
        p.append(_kp(ix + dx, iy + dy, r=5))
    p.append(text(x + pw / 2, ys + ph - 14, "кути, плями — те, що впізнати легко",
                  size=8.5, color=MUTED))

    # 2) дескриптор: клапоть околу → вектор чисел
    x = xs[1]
    px, py = x + 40, ys + 58
    p.append(_frame(px, py, 56, 56))
    p.append(_kp(px + 28, py + 28, r=5))
    p.append(arrow(px + 62, py + 28, px + 96, py + 28, color=INK, sw=1.7))
    # стовпчики-вектор
    vals = [0.6, 0.9, 0.3, 0.7, 0.5, 0.85, 0.4]
    gx, gy, gw, gh = px + 104, py + 4, 78, 52
    bw_ = gw / len(vals) - 3
    for j, v in enumerate(vals):
        bx = gx + j * (bw_ + 3)
        p.append(rect(bx, gy + gh - v * gh, bw_, v * gh, fill="#d98a00", stroke="none", sw=0, rx=1))
    p.append(text(x + pw / 2, py + 88, "«відбиток» околу —", size=9, color=MUTED))
    p.append(text(x + pw / 2, py + 102, "вектор чисел", size=9, color=MUTED))
    p.append(text(x + pw / 2, ys + ph - 14, "той самий куточок → той самий відбиток",
                  size=8.5, color=MUTED))

    # 3) звіряння: два набори векторів, стрілка до найближчого
    x = xs[2]
    lx, rx = x + 44, x + pw - 60
    ysv = ys + 52
    for i in range(3):
        p.append(rect(lx - 10, ysv + i * 34, 20, 22, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=3))
        p.append(rect(rx - 10, ysv + i * 34, 20, 22, fill="#dcfce7", stroke=GOOD, sw=1.4, rx=3))
    # найближча пара (середні), решта — тонко
    p.append(line(lx + 10, ysv + 34 + 11, rx - 10, ysv + 34 + 11, color=GOOD, sw=2.4))
    p.append(line(lx + 10, ysv + 11, rx - 10, ysv + 2 * 34 + 11, color="#cbd5e1", sw=1))
    p.append(line(lx + 10, ysv + 2 * 34 + 11, rx - 10, ysv + 11, color="#cbd5e1", sw=1))
    p.append(text(x + pw / 2, ysv - 8, "хто до кого найближчий", size=9, color=MUTED))
    p.append(text(x + pw / 2, ys + ph - 14, "найближчий опис = та сама точка",
                  size=8.5, color=MUTED))

    for i in range(2):
        p.append(arrow(xs[i] + pw + 2, ys + ph / 2, xs[i + 1] - 4, ys + ph / 2,
                       color=INK, sw=1.8))

    p.append(fitbox(40, ys + ph + 18, W - 80, 22,
                    "Три стадії конвеєра: знайти прикметні точки → описати окіл кожної стійким "
                    "вектором → з'єднати ті, чиї описи найближчі.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "detect-describe-match.svg"), W, H, *p,
           title="Три стадії: знайти точки → описати окіл → звірити описи")


# ── ratio-test: найближчий сам по собі бреше; рятує відрив від другого ─────────
# Ідея: якщо найкращий і другий-за-близькістю майже однакові — збіг неоднозначний
# (повторюваний візерунок); приймаємо лише коли найкращий помітно ближчий.

def fig_ratio_test():
    W, H = 820, 356
    p = []
    pw, ph = 344, 210
    ys = 88
    xs = [40, W - 40 - pw]
    heads = ["НЕОДНОЗНАЧНО — відкинути", "ВПЕВНЕНО — прийняти"]
    hcol = [BAD, GOOD]
    for i in range(2):
        p.append(rect(xs[i], ys, pw, ph, fill="#fbfbfd", stroke=hcol[i], sw=1.8, rx=12))
        p.append(text(xs[i] + pw / 2, ys + 24, heads[i], size=11.5, color=hcol[i], bold=True))

    def scene(x, d1, d2, ok):
        # ліворуч точка-запит, праворуч два кандидати на відстанях d1<d2
        qx, qy = x + 46, ys + 118
        c1x, c1y = x + pw - 150, ys + 84
        c2x, c2y = x + pw - 90, ys + 152
        col = GOOD if ok else BAD
        p.append(_kp(qx, qy, r=6, col=NEG))
        p.append(text(qx, qy + 26, "запит", size=9, color=NEG))
        # найкращий
        p.append(_kp(c1x, c1y, r=6, col=col))
        p.append(line(qx + 6, qy - 2, c1x - 6, c1y + 4, color=col, sw=2.4))
        p.append(text((qx + c1x) / 2, (qy + c1y) / 2 - 8, "d₁", size=11, color=col, bold=True))
        p.append(text(c1x + 12, c1y, "1-й", size=9, color=col, anchor="start"))
        # другий
        p.append(_kp(c2x, c2y, r=6, col=MUTED))
        p.append(line(qx + 6, qy + 4, c2x - 6, c2y - 4, color=MUTED, sw=1.6, dash="4,3"))
        p.append(text((qx + c2x) / 2 + 6, (qy + c2y) / 2 + 14, "d₂", size=11, color=MUTED, bold=True))
        p.append(text(c2x + 12, c2y, "2-й", size=9, color=MUTED, anchor="start"))

    # ліва панель: d1 ≈ d2 (0.92)
    scene(xs[0], 0.9, 1.0, False)
    p.append(text(xs[0] + pw / 2, ys + ph - 40, "d₁ / d₂ ≈ 0.92", size=12, color=BAD, bold=True))
    p.append(text(xs[0] + pw / 2, ys + ph - 20,
                  "майже нічия — хто з двох «той самий»?", size=9.5, color=MUTED))

    # права панель: d1 << d2 (0.4)
    scene(xs[1], 0.5, 1.0, True)
    p.append(text(xs[1] + pw / 2, ys + ph - 40, "d₁ / d₂ ≈ 0.40", size=12, color=GOOD, bold=True))
    p.append(text(xs[1] + pw / 2, ys + ph - 20,
                  "найкращий помітно ближчий — довіряємо", size=9.5, color=MUTED))

    p.append(fitbox(40, ys + ph + 18, W - 80, 40,
                    "Проба відношення (Lowe): збіг приймають лише коли найближчий опис помітно "
                    "ближчий за ДРУГИЙ-за-близькістю (d₁/d₂ < ≈0.8).\nЯкщо перший і другий майже "
                    "однакові — окіл не унікальний (візерунок, що повторюється), і пару відкидають.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "ratio-test.svg"), W, H, *p,
           title="Проба відношення: довіряти лише виразному відриву від другого")


# ── ransac-inliers: серед пар є хибні; геометрія відсіює їх як викиди ──────────
# Ідея: навіть після проби відношення лишаються хибні пари; RANSAC підбирає єдину
# геометричну модель (як зсунулась сцена) і лишає тільки узгоджені з нею пари.

def fig_ransac_inliers():
    W, H = 820, 412
    p = []
    bw, bh = 344, 236
    ys = 74
    xL, xR = 40, W - 40 - bw
    p.append(text(xL + bw / 2, ys - 14, "знімок A", size=11, color=NEG, bold=True))
    p.append(text(xR + bw / 2, ys - 14, "знімок B", size=11, color=NEG, bold=True))
    p.append(_frame(xL, ys, bw, bh))
    p.append(_frame(xR, ys, bw, bh))

    # погоджені пари (inliers): однаковий зсув вправо-вниз
    import random
    inl = [(70, 60), (150, 50), (230, 90), (110, 140), (200, 170), (60, 190), (270, 130)]
    shift = (0, 26)  # у координатах правого кадру пара «та сама» точка нижча
    for (ax, ay) in inl:
        p.append(_kp(xL + ax, ys + ay, r=5, col=KP))
        bx, by = ax - 10, ay + shift[1]
        p.append(_kp(xR + bx, ys + by, r=5, col=KP))
        p.append(line(xL + ax, ys + ay, xR + bx, ys + by, color=GOOD, sw=1.5))

    # хибні пари (outliers): випадкові напрямки, що не слухаються моделі
    out = [((300, 40), (40, 200)), ((40, 100), (300, 60)), ((180, 210), (120, 40))]
    for (a, b) in out:
        p.append(_kp(xL + a[0], ys + a[1], r=5, col=BAD))
        p.append(_kp(xR + b[0], ys + b[1], r=5, col=BAD))
        p.append(line(xL + a[0], ys + a[1], xR + b[0], ys + b[1], color=BAD, sw=1.5, dash="5,4"))

    # легенда
    p.append(line(xL + 20, ys + bh + 22, xL + 50, ys + bh + 22, color=GOOD, sw=2.2))
    p.append(text(xL + 56, ys + bh + 26, "згодні з моделлю (inliers)", size=9.5,
                  color=INK, anchor="start"))
    p.append(line(xR - 4, ys + bh + 22, xR + 26, ys + bh + 22, color=BAD, sw=2, dash="5,4"))
    p.append(text(xR + 32, ys + bh + 26, "суперечать (outliers) — геть", size=9.5,
                  color=INK, anchor="start"))

    p.append(fitbox(40, ys + bh + 40, W - 80, 40,
                    "Навіть по пробі відношення частина пар — хибні. RANSAC питає: чи є ЄДИНИЙ "
                    "геометричний зсув сцени,\nз яким згодна більшість пар? Ті, що згодні "
                    "(паралельні зелені), лишаються; поодинокі бунтарі (пунктир) — викиди.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "ransac-inliers.svg"), W, H, *p,
           title="Геометрична перевірка (RANSAC): лишити узгоджені пари, відсіяти викиди")


# ── two-best-scan: як за один прохід оновлюються два рекорди best/second ────────
# Ідея (для proj-orb-match-c): кандидати з відстанями Гаммінга проходять по черзі;
# два рекорди — найкращий і другий — оновлюються за правилом гілок, і саме на їх
# відриві тримається проба відношення. Показуємо стан best/second після кожного
# кандидата на прикладі [47, 12, 190, 61].

def fig_two_best_scan():
    W, H = 820, 396
    p = []
    cands = [47, 12, 190, 61]                 # відстані кандидатів по черзі
    # стан (best, second) ПІСЛЯ обробки кожного кандидата
    states = [(47, 257), (12, 47), (12, 47), (12, 47)]
    notes  = ["новий рекорд", "новий рекорд — старий best → second",
              "гірший за обидва — повз", "гірший за обидва — повз"]
    ncol   = [GOOD, GOOD, MUTED, MUTED]

    ys = 66
    colw = 176
    x0 = 44
    p.append(text(W / 2, ys - 20, "прохід по кандидатах набору B  →  два рекорди",
                  size=12, color=INK, bold=True))

    # верхній рядок: самі кандидати як «плитки» з відстанню
    for k, d in enumerate(cands):
        cx = x0 + k * colw + colw / 2
        tile = GOOD if d == 12 else ("#eef2f7")
        tcol = "#ffffff" if d == 12 else INK
        p.append(rect(cx - 40, ys, 80, 46, fill=tile, stroke=INK, sw=1.4, rx=8))
        p.append(text(cx, ys + 20, "кандидат %d" % k, size=9,
                      color=(tcol if d == 12 else MUTED)))
        p.append(text(cx, ys + 39, "d = %d" % d, size=13, color=tcol, bold=True))
        if k < len(cands) - 1:
            p.append(arrow(cx + 46, ys + 23, cx + colw - 46, ys + 23, color=INK, sw=1.6))

    # два рядки рекордів: best і second після кожного кроку
    ry_best = ys + 104
    ry_sec  = ys + 168
    p.append(text(x0 - 8, ry_best + 20, "best", size=11, color=NEG, bold=True, anchor="end"))
    p.append(text(x0 - 8, ry_sec + 20, "second", size=11, color=MUTED, bold=True, anchor="end"))

    for k in range(len(cands)):
        cx = x0 + k * colw + colw / 2
        b, s = states[k]
        # best-плитка
        p.append(rect(cx - 34, ry_best, 68, 40, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
        p.append(text(cx, ry_best + 26, "%d" % b, size=15, color=NEG, bold=True))
        # second-плитка (257 → показуємо як ∞-заглушку)
        sec_txt = "257" if s == 257 else "%d" % s
        p.append(rect(cx - 34, ry_sec, 68, 40, fill="#f4f6f8", stroke=MUTED, sw=1.4, rx=6))
        p.append(text(cx, ry_sec + 26, sec_txt, size=15, color=MUTED, bold=True))
        if s == 257:
            p.append(text(cx, ry_sec + 55, "заглушка", size=8, color=MUTED))
        # підпис-рішення під колонкою
        p.append(text(cx, ry_best - 12, notes[k], size=8, color=ncol[k]))

    p.append(fitbox(44, ry_sec + 66, W - 88, 44,
                    "За прохід ведемо два рекорди. Новий кандидат, кращий за best, СТАЄ best, "
                    "а старий best з'їжджає в second (крок 1→2).\nКандидат, гірший за обидва, "
                    "не міняє нічого. Підсумок best=12, second=47 — виразний відрив, і проба "
                    "відношення (12 < 0.8·47) приймає збіг.",
                    size=10, fill=FILL, stroke=INK, sw=1.3, color=INK))

    render(os.path.join(OUT, "two-best-scan.svg"), W, H, *p,
           title="Пошук двох найкращих за один прохід: best і second")


if __name__ == "__main__":
    fig_what_is_matching()
    fig_detect_describe_match()
    fig_ratio_test()
    fig_ransac_inliers()
    fig_two_best_scan()
    print("OK: figures written to", OUT)
