# -*- coding: utf-8 -*-
"""Фігури до теми «Відцентрова сила».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ────────────────────────────────────────────────────────
def head_at(x, y, dx, dy, color=INK, size=11):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.6, head=11, dash=None):
    return line(x1, y1, x2, y2, color=color, sw=sw, dash=dash) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def arc_arrow(cx, cy, r, a0_deg, a1_deg, color=LINE, sw=2.2, head=9):
    a0 = math.radians(a0_deg); a1 = math.radians(a1_deg)
    x0 = cx + r * math.cos(a0); y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1); y1 = cy - r * math.sin(a1)
    sweep_ccw = 1 if a1_deg > a0_deg else 0
    sweep = 0 if sweep_ccw else 1
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    path = ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (x0, y0, r, r, large, sweep, x1, y1, color, sw))
    dir_sign = 1 if sweep_ccw else -1
    tx = -math.sin(a1) * dir_sign; ty = -math.cos(a1) * dir_sign
    L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
    px, py = x1 - tx * head, y1 - ty * head
    nx, ny = -ty, tx
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * head / 2.2, py + ny * head / 2.2,
            px - nx * head / 2.2, py - ny * head / 2.2, color))
    return path + h


# ── Фігура 1: той самий поворот у двох системах відліку ──────────────────────
def fig_two_frames():
    W, H = 800, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Один поворот — дві системи відліку", size=17, bold=True))

    R = 100
    cy = 220

    def disk(cx):
        out = circle(cx, cy, R, fill="#fbfcfe", stroke=MUTED, sw=1.6)
        out += circle(cx, cy, 4.5, fill=INK, stroke=INK, sw=1)         # вісь/центр
        out += arc_arrow(cx, cy, 40, 40, 150, color=FIELD, sw=1.9, head=8)  # сенс обертання
        return out

    # ── ЛІВОРУЧ: інерціальна система ──
    cxL = 210
    f.append(text(cxL, 66, "погляд із тротуару", size=14, bold=True))
    f.append(text(cxL, 84, "(інерціальна система)", size=12, color=MUTED))
    f.append(disk(cxL))
    bx, by = cxL + R, cy                       # тіло на ободі (схід)
    f.append(circle(bx, by, 6, fill=INK, stroke=INK, sw=1))
    # інерція — дотична (вгору), пунктир
    f.append(varrow(bx, by - 6, bx, by - 66, color=MUTED, sw=2, head=9, dash="5 4"))
    f.append(text(bx, by - 74, "інерція: прямо", size=11, color=MUTED))
    # центрострімка — усередину
    f.append(varrow(bx - 8, by, bx - 70, by, color=NEG, sw=3, head=12))
    f.append(text(cxL + 30, by + 24, "до центра", size=12, bold=True, color=NEG))
    f.append(text(cxL + 30, by + 39, "(реальна)", size=10, color=MUTED))
    f.append(text(cxL, cy + R + 40, "єдина реальна сила — до центра;", size=11, color=MUTED))
    f.append(text(cxL, cy + R + 56, "вона й гне прямий рух у дугу", size=11, color=MUTED))

    # ── ПРАВОРУЧ: обертова система ──
    cxR = 590
    f.append(text(cxR, 66, "погляд із машини", size=14, bold=True))
    f.append(text(cxR, 84, "(обертова система)", size=12, color=MUTED))
    f.append(disk(cxR))
    bx2, by2 = cxR + R, cy
    f.append(circle(bx2, by2, 6, fill=INK, stroke=INK, sw=1))
    # двері — усередину
    f.append(varrow(bx2 - 8, by2, bx2 - 70, by2, color=NEG, sw=3, head=12))
    f.append(text(cxR + 34, by2 + 24, "двері", size=12, bold=True, color=NEG))
    f.append(text(cxR + 34, by2 + 39, "(реальна)", size=10, color=MUTED))
    # відцентрова — назовні
    f.append(varrow(bx2 + 8, by2, bx2 + 70, by2, color=POS, sw=3, head=12))
    f.append(text(bx2 + 40, by2 + 24, "відцентрова", size=12, bold=True, color=POS))
    f.append(text(bx2 + 40, by2 + 39, "(вигадана)", size=10, color=MUTED))
    f.append(text(cxR, cy + R + 40, "рівновага: у цій системі", size=11, color=MUTED))
    f.append(text(cxR, cy + R + 56, "тіло нерухоме", size=11, color=MUTED))

    b, w, h = textbox(W / 2, H - 22,
                      "назовні тіло ніщо не штовхає — відцентрову дописують, щоб урятувати F = m·a в обертовій системі",
                      size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "two-frames.svg"), W, H, *f)


# ── Фігура 2: три схожі назви — три різні сили (камінь на мотузці) ────────────
def fig_three_forces():
    W, H = 800, 410
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Камінь на мотузці: три сили, які плутають", size=17, bold=True))

    hx, hy = 205, 195                 # рука (центр обертання)
    bxx, byy = 560, 195               # камінь
    # мотузка
    f.append(line(hx + 16, hy, bxx - 14, byy, color="#b8bec9", sw=1.6))
    # рука й камінь
    f.append(circle(hx, hy, 15, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(hx, hy + 34, "рука", size=11, color=MUTED))
    f.append(circle(bxx, byy, 13, fill=INK, stroke=INK, sw=1))
    f.append(text(bxx, byy + 34, "камінь", size=11, color=MUTED))
    # сенс обертання
    f.append(arc_arrow(hx, hy, 62, 18, 74, color=FIELD, sw=2, head=8))
    f.append(text(hx + 66, hy - 44, "обертання", size=11, color=FIELD, anchor="start"))

    # центрострімка (на камінь, до центра) — синя
    f.append(varrow(bxx - 14, byy, bxx - 90, byy, color=NEG, sw=3.2, head=12))
    f.append(text(bxx - 52, byy - 12, "центрострімка", size=12, bold=True, color=NEG))
    # відцентрова (на камінь, від центра) — червона, пунктир
    f.append(varrow(bxx + 14, byy, bxx + 90, byy, color=POS, sw=3.2, head=12, dash="6 4"))
    f.append(text(bxx + 52, byy - 12, "відцентрова", size=12, bold=True, color=POS))
    # реактивна відцентрова (на мотузку/руку, назовні) — зелена, зсунута вгору
    f.append(varrow(hx + 20, hy - 24, hx + 96, hy - 24, color=FIELD, sw=3.2, head=12))
    f.append(text(hx + 58, hy - 32, "реактивна", size=12, bold=True, color=FIELD))

    # легенда — три рядки з кольоровими маркерами
    lx, ly, dy = 92, 288, 32
    f.append(line(lx - 6, ly - 22, W - 60, ly - 22, color="#e4e7ec", sw=1.2))
    rows = [
        (NEG,   "центрострімка — реальна, до центра, діє на камінь (тримає його на колі)"),
        (POS,   "відцентрова — вигадана, від центра, діє на камінь (лише в обертовій системі)"),
        (FIELD, "реактивна відцентрова — реальна, від центра, діє на мотузку й руку (3-й закон)"),
    ]
    for i, (col, s) in enumerate(rows):
        yy = ly + i * dy
        f.append(circle(lx, yy - 4, 6, fill=col, stroke=col, sw=1))
        f.append(text(lx + 16, yy, s, size=13, color=INK, anchor="start"))
    return render(os.path.join(IMG, "three-forces.svg"), W, H, *f)


# ── Фігура 3: тяжіння + відцентрова = ефективне «вниз» ────────────────────────
def fig_effective_gravity():
    W, H = 830, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Тяжіння + відцентрова = ефективне «вниз» (виска)", size=17, bold=True))

    cx, cy, R = 250, 232, 145
    # земна куля
    f.append(circle(cx, cy, R, fill="#f4f8fb", stroke=MUTED, sw=1.8))
    # вісь обертання (пунктир) + ω на полюсі
    f.append(line(cx, cy + R + 30, cx, cy - R - 34, color=INK, sw=1.5, dash="6 5"))
    f.append(varrow(cx, cy - R - 6, cx, cy - R - 52, color=FIELD, sw=3, head=12))
    f.append(text(cx + 12, cy - R - 30, "ω", size=15, bold=True, italic=True, color=FIELD, anchor="start"))
    # екватор (сплюснутий еліпс)
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="4 4"/>'
             % (cx, cy, R, R * 0.28, MUTED))

    # відцентрові стрілки-патерн на кількох широтах: довжина ∝ відстані до осі (cos φ)
    def cf_arrow(phi_deg, sign, lab=None):
        a = math.radians(phi_deg)
        px = cx + sign * R * math.cos(a)
        py = cy - R * math.sin(a)
        Lp = 58 * math.cos(a)                     # ∝ відстань до осі
        f.append(varrow(px + sign * 6, py, px + sign * (6 + Lp), py, color=POS, sw=2.8, head=10))
        if lab:
            f.append(text(px + sign * (6 + Lp) + sign * 6, py + 4, lab,
                          size=11, color=POS, anchor="start" if sign > 0 else "end"))
        return px, py

    cf_arrow(0, +1, "макс (r = R)")
    cf_arrow(0, -1)
    cf_arrow(70, -1)
    # полюс — відцентрової немає
    f.append(circle(cx, cy - R, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(cx - 10, cy - R + 4, "0 на полюсі", size=11, color=MUTED, anchor="end"))

    # ── у точці на 45° — повний розклад: тяжіння + відцентрова = виска ──
    a = math.radians(45)
    Px, Py = cx + R * math.cos(a), cy - R * math.sin(a)
    f.append(circle(Px, Py, 5, fill=INK, stroke=INK, sw=1))
    ug = (-(Px - cx), -(Py - cy))                 # до центра
    Lg = math.hypot(*ug); ug = (ug[0] / Lg, ug[1] / Lg)
    G = 78
    Cf = 40
    gx, gy = Px + ug[0] * G, Py + ug[1] * G       # кінець тяжіння
    cfx, cfy = Px + Cf, Py                         # кінець відцентрової (назовні від осі, +x)
    ex, ey = Px + (ug[0] * G + Cf), Py + ug[1] * G  # кінець ефективної (сума)
    # паралелограм (пунктирні добудови)
    f.append(line(gx, gy, ex, ey, color=POS, sw=1.2, dash="4 3"))
    f.append(line(cfx, cfy, ex, ey, color=NEG, sw=1.2, dash="4 3"))
    # тяжіння (синя, до центра)
    f.append(varrow(Px, Py, gx, gy, color=NEG, sw=3, head=11))
    f.append(text(gx - 6, gy + 14, "тяжіння", size=12, bold=True, color=NEG, anchor="end"))
    # відцентрова (червона, від осі)
    f.append(varrow(Px, Py, cfx, cfy, color=POS, sw=3, head=11))
    f.append(text(cfx + 8, cfy - 6, "відцентрова", size=12, bold=True, color=POS, anchor="start"))
    # ефективна (зелена, сума)
    f.append(varrow(Px, Py, ex, ey, color=FIELD, sw=3.4, head=12))
    f.append(text(ex + 6, ey + 16, "виска", size=12, bold=True, color=FIELD, anchor="start"))

    # ── права колонка ──
    px, pw = 548, 258
    f.append(fitbox(px, 66, pw, 58, "справжнє тяжіння —\nзавжди до центра Землі",
                    size=12, pad=9, fill="#eef1fb", stroke=NEG, sw=1.4, bold=True))
    f.append(fitbox(px, 138, pw, 66, "відцентрова — від осі, ω²·r:\nмакс на екваторі, нуль на полюсі",
                    size=12, pad=9, fill="#fdecea", stroke=POS, sw=1.4, bold=True))
    f.append(fitbox(px, 218, pw, 72, "сума = ефективне тяжіння (виска).\nЕкватор: ω²R ≈ 0.034 м/с² ≈ 0.3% g",
                    size=12, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True))
    f.append(fitbox(px, 304, pw, 58, "наслідок: на екваторі легше;\nЗемля сплюснута (екв. радіус +21 км)",
                    size=12, pad=9, fill=FILL, stroke=INK, sw=1.3, bold=True))
    f.append(text(cx, cy + R + 48, "(відхилення виски показано перебільшено)", size=10, color=MUTED))
    return render(os.path.join(IMG, "effective-gravity.svg"), W, H, *f)


# ── Фігура 4 (hist): дзеркало назв — vis centrifuga ↔ vis centripeta ──────────
def fig_naming_mirror():
    W, H = 860, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Одна дуга — дві латинські назви, протилежні напрями", size=17, bold=True))
    f.append(text(W / 2, 50, "Ньютон свідомо перевернув Гюйгенсову назву: fugere → petere", size=12, color=MUTED))

    cx, cy, R = 430, 196, 98
    f.append(circle(cx, cy, R, fill="#fbfcfe", stroke=MUTED, sw=1.6))
    f.append(arc_arrow(cx, cy, R, 32, 88, color=FIELD, sw=1.8, head=8))       # сенс руху
    f.append(circle(cx, cy, 5, fill=INK, stroke=INK, sw=1))
    f.append(text(cx - 12, cy + 4, "центр", size=11, color=MUTED, anchor="end"))

    bx, by = cx + R, cy                                                        # тіло на дузі (схід)
    f.append(circle(bx, by, 7, fill=INK, stroke=INK, sw=1))
    # інерція — дотична вгору, пунктир
    f.append(varrow(bx, by - 7, bx, by - 72, color=MUTED, sw=2, head=9, dash="5 4"))
    f.append(text(bx + 8, by - 60, "рух по інерції — прямо", size=11, color=MUTED, anchor="start"))
    # відцентрова — назовні (червона)
    f.append(varrow(bx + 12, by, bx + 120, by, color=POS, sw=3.4, head=13))
    f.append(text(bx + 74, by - 12, "vis centrifuga", size=13, bold=True, color=POS))
    # центрострімка — усередину (синя)
    f.append(varrow(bx - 12, by, bx - 88, by, color=NEG, sw=3.4, head=13))
    f.append(text(bx - 50, by - 12, "vis centripeta", size=13, bold=True, color=NEG))

    # пояснювальні картки
    f.append(fitbox(70, 300, 330, 132,
                    "vis centripeta — «прагнути до центра»\n(centrum + petere).\nНьютон, 1684: сила всередину,\nщо гне рух у коло — тяжіння.",
                    size=13, pad=12, fill="#eaf0fd", stroke=NEG, sw=1.5, bold=True))
    f.append(fitbox(460, 300, 330, 132,
                    "vis centrifuga — «тікати від центра»\n(centrum + fugere).\nГюйгенс, 1659: тенденція тіла\nназовні, з величиною v²/r.",
                    size=13, pad=12, fill="#fdecea", stroke=POS, sw=1.5, bold=True))
    return render(os.path.join(IMG, "naming-mirror.svg"), W, H, *f)


# ── Фігура 5 (hist): як мінявся статус поняття за 350 років ────────────────────
def fig_concept_status():
    W, H = 920, 348
    PURPLE = "#8e44ad"
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Триста п'ятдесят років: як мінявся статус відцентрової сили", size=17, bold=True))
    f.append(varrow(36, 66, 884, 66, color=MUTED, sw=2, head=11))
    f.append(text(W / 2, 58, "розуміння з часом →", size=12, color=MUTED))

    cols = [
        ("Реальна сила,\nщо жене назовні", POS, "#fdecea", "1644 – 1689",
         ["Декарт (Descartes)", "Гюйгенс (Huygens)", "Ляйбніц (Leibniz)"]),
        ("Ознака справжнього,\nабсолютного обертання", PURPLE, "#f3e8f8", "1687",
         ["Ньютон (Newton):", "відро з водою"]),
        ("Фіктивний доданок\nобертової системи", MUTED, "#eef0f2", "1721 – 1883",
         ["Барклі (Berkeley)", "д'Аламбер (d'Alembert)", "Коріоліс (Coriolis)", "Мах (Mach)"]),
        ("Локально нероздільна\nз тяжінням", FIELD, "#eef6ef", "1915",
         ["Айнштайн (Einstein):", "загальна відносність"]),
    ]
    x0, cw, gap = 30, 200, 20
    for i, (status, col, light, years, people) in enumerate(cols):
        x = x0 + i * (cw + gap)
        f.append(fitbox(x, 86, cw, 64, status, size=13, pad=9, fill=light, stroke=col, sw=1.6, bold=True))
        f.append(text(x + cw / 2, 172, years, size=12, bold=True, color=INK))
        f.append(rect(x, 184, cw, 132, fill=light, stroke=col, sw=1.3))
        for j, p in enumerate(people):
            f.append(text(x + 16, 212 + j * 22, p, size=12, color=INK, anchor="start"))
    return render(os.path.join(IMG, "concept-status.svg"), W, H, *f)


def polyline(pts, color=LINE, sw=2.4, dash=None):
    if not pts:
        return ""
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


# ── Фігура (proj): зона комфорту — радіус станції проти обертів ───────────────
def fig_comfort_zone():
    W, H = 900, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Зона комфорту: радіус станції проти швидкості обертання",
                  size=17, bold=True))

    x0, y0, x1, y1 = 100, 428, 604, 86           # межі поля графіка (пікселі)
    rmin, rmax, ymax = 2.0, 1000.0, 14.0
    lr0, lr1 = math.log10(rmin), math.log10(rmax)
    K = 60.0 / (2 * math.pi)                       # рад/с → об/хв (= 9.5493)

    def X(r):    return x0 + (math.log10(r) - lr0) / (lr1 - lr0) * (x1 - x0)
    def Yr(rpm): return y0 - rpm / ymax * (y0 - y1)

    # смуги комфорту (низькі оберти внизу графіка)
    f.append(rect(x0, Yr(2), x1 - x0, y0 - Yr(2), fill="#e9f6ee", stroke='none', sw=0, rx=0))
    f.append(rect(x0, Yr(6), x1 - x0, Yr(2) - Yr(6), fill="#fdf3e2", stroke='none', sw=0, rx=0))

    # сітка X (радіус, лог)
    for r in (2, 5, 10, 20, 50, 100, 200, 500, 1000):
        xx = X(r)
        f.append(line(xx, y0, xx, y1, color="#e6e9ee", sw=1))
        f.append(text(xx, y0 + 18, str(r), size=11, color=MUTED))
    f.append(text((x0 + x1) / 2, y0 + 40, "радіус станції r, м  (лог-шкала)", size=12, color=INK))
    # сітка Y (оберти)
    for rpm in range(0, int(ymax) + 1, 2):
        yy = Yr(rpm)
        f.append(line(x0, yy, x1, yy, color="#e6e9ee", sw=1))
        f.append(text(x0 - 10, yy + 4, str(rpm), size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 6, y1 - 12, "оберти, об/хв", size=12, color=INK, anchor="start"))
    # осі поверх сітки
    f.append(line(x0, y0, x1, y0, color=INK, sw=1.6))
    f.append(line(x0, y0, x0, y1, color=INK, sw=1.6))

    # межі смуг
    f.append(line(x0, Yr(2), x1, Yr(2), color=FIELD, sw=2.2))
    f.append(text(x0 + 8, Yr(2) + 16, "≤ 2 об/хв — комфорт", size=11, color=FIELD, anchor="start", bold=True))
    f.append(line(x0, Yr(6), x1, Yr(6), color="#c9871a", sw=1.8, dash="6 4"))
    f.append(text(x0 + 8, Yr(6) - 7, "≤ 6 об/хв — терпимо (з адаптацією)", size=11, color="#c9871a", anchor="start"))

    # криві сталого тяжіння  ω = √(f·g/r),  в об/хв
    def gcurve(fr, color, dash=None):
        pts = []
        for i in range(0, 81):
            rr = rmin * (rmax / rmin) ** (i / 80.0)
            rpm = K * math.sqrt(fr * 9.81 / rr)
            if rpm <= ymax:
                pts.append((X(rr), Yr(rpm)))
        return polyline(pts, color=color, sw=2.8, dash=dash)

    f.append(gcurve(1.0, NEG))
    f.append(gcurve(0.38, "#8e44ad", dash="7 4"))
    f.append(text(X(5.4), Yr(K * math.sqrt(9.81 / 5.4)) - 10, "1 g", size=13, color=NEG, bold=True, anchor="start"))
    f.append(mtext(X(2.81), 152, ["0.38 g", "(Марс)"], size=12, color="#8e44ad",
                   anchor="start", bold=True, lh=1.15))

    # характерні точки — маркер + короткий номер (сам підпис див. у переліку праворуч,
    # щоб не тіснити текст поруч із частою вертикальною сіткою)
    def pt(r, rpm, num, color, dx, dy, anch):
        f.append(circle(X(r), Yr(rpm), 5.5, fill=color, stroke=BG, sw=1.6))
        f.append(text(X(r) + dx, Yr(rpm) + dy, num, size=11, color=color, anchor=anch, bold=True))

    pt(224, 2.0, "1", NEG, 11, -10, "start")
    pt(100, K * math.sqrt(9.81 / 100), "2", INK, 13, -9, "start")
    pt(38, 3.0, "3", "#8e44ad", -11, 17, "end")
    pt(10, K * math.sqrt(9.81 / 10), "4", POS, 13, 4, "start")

    # права колонка — як читати графік
    px, pw = 640, 236
    f.append(fitbox(px, 96, pw, 60, "криві — сталі g: на кривій\nобід дає рівно це тяжіння",
                    size=12, pad=9, fill=FILL, stroke=INK, sw=1.2, bold=True))
    f.append(fitbox(px, 172, pw, 60, "униз по кривій = більший радіус\n= повільніші, спокійніші оберти",
                    size=12, pad=9, fill="#eef1fb", stroke=NEG, sw=1.3, bold=True))
    f.append(fitbox(px, 248, pw, 76, "зелене — комфорт (≤2 об/хв);\nповне 1 g входить у нього лише\nвід r ≈ 224 м (∅ ~450 м)",
                    size=12, pad=9, fill="#e9f6ee", stroke=FIELD, sw=1.4, bold=True))
    f.append(fitbox(px, 340, pw, 68, "малий радіус жене криву вгору,\nу дискомфорт: швидкі оберти,\nсильний Коріоліс, крутий градієнт",
                    size=12, pad=9, fill="#fdecea", stroke=POS, sw=1.3, bold=True))

    # перелік номерів — поза тісною сіткою графіка, тому без перетинів
    f.append(text(px + 4, 428, "1 — 1 g тут: r ≈ 224 м", size=11, color=NEG, anchor="start"))
    f.append(text(px + 4, 448, "2 — станція 100 м", size=11, color=INK, anchor="start"))
    f.append(text(px + 4, 468, "3 — колесо фон Брауна", size=11, color="#8e44ad", anchor="start"))
    f.append(text(px + 4, 488, "4 — тіснота 10 м", size=11, color=POS, anchor="start"))
    return render(os.path.join(IMG, "habitat-comfort-zone.svg"), W, H, *f)


# ── Фігура (proj): астронавт на ободі — градієнт голова-ноги і Коріоліс ходи ──
def fig_habitat_astronaut():
    W, H = 840, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Астронавт на ободі: градієнт «тяжіння» і Коріоліс ходи",
                  size=17, bold=True))

    def floor(cx):
        """Пологий шматок обода-підлоги (вісь високо вгорі → майже плоско)."""
        R = 900.0
        yc = 372 - R
        pts = []
        for i in range(0, 41):
            th = -0.16 + 0.32 * i / 40.0
            pts.append((cx + R * math.sin(th), yc + R * math.cos(th)))
        return pts, 372

    def person(cx, feetY, Hp=104):
        """Проста постать: ноги на підлозі, голова до осі (вгору)."""
        headY = feetY - Hp
        out = line(cx, feetY, cx, headY + 14, color=INK, sw=3)            # тулуб
        out += circle(cx, headY + 8, 9, fill=FILL, stroke=INK, sw=2)      # голова
        out += line(cx, feetY - 62, cx - 15, feetY - 34, color=INK, sw=2.4)   # руки
        out += line(cx, feetY - 62, cx + 15, feetY - 34, color=INK, sw=2.4)
        out += line(cx, feetY, cx - 12, feetY + 2, color=INK, sw=2.6)     # ступні
        out += line(cx, feetY, cx + 12, feetY + 2, color=INK, sw=2.6)
        return out, headY

    # ── ЛІВА сцена: градієнт голова-ноги ──
    cxL = 232
    ptsL, fyL = floor(cxL)
    f.append(polyline(ptsL, color=MUTED, sw=2.4))
    f.append(text(cxL, fyL + 30, "підлога-обід", size=11, color=MUTED))
    f.append(text(cxL, 86, "стоїш нерухомо", size=13, bold=True))
    f.append(varrow(cxL - 150, fyL - 24, cxL - 150, fyL - 118, color=MUTED, sw=1.8, head=9, dash="5 4"))
    f.append(text(cxL - 150, fyL - 126, "до осі", size=10.5, color=MUTED))
    bodyL, hyL = person(cxL, fyL)
    f.append(bodyL)
    ax = cxL + 82
    f.append(varrow(ax, hyL + 6, ax, hyL + 56, color=POS, sw=2.8, head=10))
    f.append(text(ax + 8, hyL + 32, "g голови = ω²(r−h)", size=11, color=POS, anchor="start"))
    f.append(varrow(ax, fyL - 8, ax, fyL + 58, color=POS, sw=3.2, head=11))
    f.append(text(ax + 8, fyL + 30, "g ніг = ω²·r", size=11, color=POS, anchor="start", bold=True))
    b, w, h = textbox(cxL, 414, "різниця Δg = ω²·h  (голова легша за ноги)",
                      size=12, pad=8, fill="#fdecea", stroke=POS, sw=1.3, bold=True)
    f.append(b)

    # ── ПРАВА сцена: Коріоліс під час ходи ──
    cxR = 612
    ptsR, fyR = floor(cxR)
    f.append(polyline(ptsR, color=MUTED, sw=2.4))
    f.append(text(cxR, fyR + 30, "підлога-обід", size=11, color=MUTED))
    f.append(text(cxR, 86, "ідеш уздовж обода", size=13, bold=True))
    bodyR, hyR = person(cxR, fyR)
    f.append(bodyR)
    f.append(varrow(cxR + 14, fyR - 52, cxR + 92, fyR - 52, color=NEG, sw=3, head=11))
    f.append(text(cxR + 96, fyR - 52, "v (хода)", size=11, color=NEG, anchor="start", bold=True))
    f.append(varrow(cxR - 10, fyR - 52, cxR - 10, fyR - 118, color=FIELD, sw=3.2, head=11))
    f.append(text(cxR - 16, fyR - 126, "Коріоліс 2mΩv", size=11, color=FIELD, anchor="middle", bold=True))
    b2, w2, h2 = textbox(cxR, 414, "бічний штовхан росте з ω: на малому радіусі валить із ніг",
                         size=12, pad=8, fill="#e9f6ee", stroke=FIELD, sw=1.3, bold=True)
    f.append(b2)
    f.append(text(W / 2, H - 8, "(градієнт і нахил показано перебільшено)", size=10, color=MUTED))
    return render(os.path.join(IMG, "habitat-astronaut.svg"), W, H, *f)


# ── Фігура (math): розклад −m·ω×(ω×r) = m·Ω²·r⊥ — назовні ВІД ОСІ ─────────────
def fig_axis_centrifugal():
    W, H = 840, 490
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Відцентрова сила дивиться від осі, а не від центра", size=17, bold=True))

    AX = 300
    Ox, Oy = 300, 300
    P1x, P1y = 520, 165
    Fx, Fy = AX, P1y
    P2x, P2y = 520, 250

    # вісь обертання (пунктир) + ω зверху
    f.append(line(AX, 430, AX, 96, color=INK, sw=1.5, dash="6 5"))
    f.append(varrow(AX, 124, AX, 80, color=FIELD, sw=3, head=12))
    f.append(text(AX + 13, 100, "ω", size=15, bold=True, italic=True, color=FIELD, anchor="start"))
    f.append(text(AX - 12, 100, "вісь", size=11, color=MUTED, anchor="end"))

    # екваторіальна площина (пунктир) крізь центр
    f.append(line(AX - 150, Oy, AX + 165, Oy, color=MUTED, sw=1.3, dash="4 4"))
    f.append(text(AX + 32, Oy + 18, "екваторіальна площина", size=10, color=MUTED))

    # центр O
    f.append(circle(Ox, Oy, 5, fill=INK, stroke=INK, sw=1))
    f.append(text(Ox - 12, Oy + 22, "O (на осі)", size=11, color=MUTED, anchor="end"))

    # r — повний радіус-вектор O→P1
    f.append(varrow(Ox, Oy, P1x, P1y, color=MUTED, sw=2, head=9))
    f.append(text(372, 218, "r", size=13, italic=True, color=MUTED, anchor="end"))

    # r∥ — осьова частина (O→F), r⊥ — поперечна (F→P1)
    f.append(varrow(Ox, Oy, Fx, Fy, color=NEG, sw=2.8, head=10))
    f.append(text(AX - 12, 236, "r∥", size=13, italic=True, color=NEG, anchor="end"))
    f.append(varrow(Fx, Fy, P1x, P1y, color=INK, sw=2.6, head=10))
    f.append(text(412, 152, "r⊥ = ρ (до осі)", size=12, color=INK))
    # прямий кут при F
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.4"/>' % (Fx + 13, Fy, Fx + 13, Fy + 13, Fx, Fy + 13, MUTED))

    # P1 і відцентрова на ньому
    f.append(circle(P1x, P1y, 6, fill=INK, stroke=INK, sw=1))
    f.append(text(P1x + 13, P1y - 8, "P", size=12, bold=True))
    f.append(varrow(P1x + 8, P1y, 650, P1y, color=POS, sw=3.4, head=13))
    f.append(text(594, P1y - 13, "F_вц = m·Ω²·r⊥", size=13, bold=True, color=POS))

    # P2 — та сама ρ, інша висота: та сама сила
    f.append(line(P2x, P1y + 14, P2x, P2y + 12, color=MUTED, sw=1.2, dash="4 3"))
    f.append(circle(P2x, P2y, 5, fill="#ffffff", stroke=INK, sw=1.6))
    f.append(varrow(P2x + 8, P2y, 650, P2y, color=POS, sw=2.6, head=11))
    f.append(text(594, P2y + 24, "та сама ρ  ⇒  та сама сила", size=11, color=MUTED))

    b, w, h = textbox(W / 2, 462,
                      "ω×(ω×r) = ω(ω·r) − Ω²·r = −Ω²·r⊥      ⇒      |F_вц| = m·Ω²·ρ  (висота над віссю не входить)",
                      size=12, pad=9, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "axis-centrifugal.svg"), W, H, *f)


# ── Фігура (math): складові відцентрової за широтою ──────────────────────────
def fig_latitude_components():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Як відцентрова ділиться між «вагою» і «виском» за широтою", size=16, bold=True))

    x0, x1 = 110, 560
    ytop, ybot = 78, 366
    ymax = 1.05

    def X(phi):
        return x0 + (phi / 90.0) * (x1 - x0)

    def Y(v):
        return ybot - (v / ymax) * (ybot - ytop)

    # осі
    f.append(line(x0, ybot, x1 + 6, ybot, color=INK, sw=1.6))
    f.append(line(x0, ybot, x0, ytop - 6, color=INK, sw=1.6))
    for phi in (0, 15, 30, 45, 60, 75, 90):
        xx = X(phi)
        f.append(line(xx, ybot, xx, ybot + 5, color=INK, sw=1.2))
        f.append(text(xx, ybot + 20, "%d°" % phi, size=11, color=MUTED))
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        yy = Y(v)
        f.append(line(x0 - 5, yy, x0, yy, color=INK, sw=1.2))
        f.append(text(x0 - 9, yy + 4, ("%.2f" % v), size=10, color=MUTED, anchor="end"))
    f.append(text((x0 + x1) / 2, ybot + 42, "широта φ (від екватора)", size=12, color=INK))
    f.append(text(x0 - 4, ytop - 16, "частка від Ω²R", size=11, color=MUTED, anchor="start"))

    N = 91
    total = [(X(p), Y(math.cos(math.radians(p)))) for p in range(N)]
    radial = [(X(p), Y(math.cos(math.radians(p)) ** 2)) for p in range(N)]
    tang = [(X(p), Y(math.cos(math.radians(p)) * math.sin(math.radians(p)))) for p in range(N)]
    f.append(polyline(total, MUTED, sw=2.0, dash="6 4"))
    f.append(polyline(radial, NEG, sw=2.8))
    f.append(polyline(tang, POS, sw=2.8))

    # пік дотичної на 45°
    x45, y45 = X(45), Y(0.5)
    f.append(line(x45, ybot, x45, y45, color=MUTED, sw=1.1, dash="3 3"))
    f.append(circle(x45, y45, 4.5, fill=POS, stroke=POS, sw=1))
    f.append(text(x45 + 9, y45 - 6, "45°: макс виска (½)", size=11, color=POS, anchor="start"))
    # радіальна на екваторі
    f.append(circle(X(0), Y(1.0), 4.5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(X(0) + 9, Y(1.0) + 4, "макс ваги", size=11, color=NEG, anchor="start"))

    # легенда
    lx, ly, dy = 592, 108, 32
    for i, (col, dash, s) in enumerate([
        (MUTED, "6 4", "повна:  cosφ"),
        (NEG, None, "радіальна:  cos²φ  (вага)"),
        (POS, None, "дотична:  ½sin2φ  (виска)"),
    ]):
        yy = ly + i * dy
        f.append(line(lx, yy - 4, lx + 30, yy - 4, color=col, sw=2.8, dash=dash))
        f.append(text(lx + 38, yy, s, size=12, color=INK, anchor="start"))

    f.append(fitbox(lx, 218, 200, 112,
                    "Ω²R ≈ 0.034 м/с²\n\nрадіальна max на екваторі\n(−0.35% ваги)\nдотична max на 45°\n(виска ≈ 6′)",
                    size=12, pad=10, fill=FILL, stroke=INK, sw=1.2))
    return render(os.path.join(IMG, "latitude-components.svg"), W, H, *f)


# ── Фігура (math): чому куля нестійка → сплюснутий геоїд ──────────────────────
def fig_geoid_equilibrium():
    W, H = 860, 460
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Чому куля нестійка, а рівновага — сплюснутий еліпсоїд", size=16, bold=True))

    cy = 232
    cxL, R = 215, 122
    cxR, rx, ry = 636, 140, 112

    def axis(cx, half):
        return (line(cx, cy + half + 16, cx, cy - half - 22, color=INK, sw=1.4, dash="6 5")
                + varrow(cx, cy - half - 4, cx, cy - half - 40, color=FIELD, sw=2.4, head=9)
                + text(cx + 11, cy - half - 20, "ω", size=13, bold=True, italic=True, color=FIELD, anchor="start"))

    # ── ЛІВОРУЧ: куля ──
    f.append(circle(cxL, cy, R, fill="#f4f8fb", stroke=MUTED, sw=1.8))
    f.append(axis(cxL, R))
    a = math.radians(45)
    PLx, PLy = cxL + R * math.cos(a), cy - R * math.sin(a)
    f.append(circle(PLx, PLy, 5, fill=INK, stroke=INK, sw=1))
    f.append(line(PLx, PLy, cxL, cy, color=MUTED, sw=1.3, dash="4 3"))
    f.append(varrow(PLx, PLy, cxL + 16, cy + 52, color=FIELD, sw=3, head=11))
    f.append(text(cxL + 24, cy + 40, "виска", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(text(cxL + 8, cy - 4, "на центр", size=10, color=MUTED, anchor="start"))
    f.append(arc_arrow(cxL, cy, R + 3, 40, 22, color=POS, sw=2.4, head=9))
    f.append(text(PLx + 34, PLy + 22, "вода тече", size=11, color=POS, anchor="start"))
    f.append(text(cxL, cy + R + 42, "КУЛЯ: виска не ⟂ поверхні", size=12, bold=True))
    f.append(text(cxL, cy + R + 59, "→ вода стікає до екватора", size=11, color=MUTED))

    # ── стрілка переходу ──
    f.append(text(428, cy + 6, "⇒", size=30, color=MUTED, bold=True))

    # ── ПРАВОРУЧ: сплюснутий еліпсоїд ──
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#eef6ef" '
             'stroke="%s" stroke-width="1.8"/>' % (cxR, cy, rx, ry, FIELD))
    f.append(axis(cxR, ry))
    PRx, PRy = cxR + rx * math.cos(a), cy - ry * math.sin(a)
    f.append(circle(PRx, PRy, 5, fill=INK, stroke=INK, sw=1))
    nx, ny = (PRx - cxR) / rx ** 2, (PRy - cy) / ry ** 2
    Ln = math.hypot(nx, ny)
    nx, ny = nx / Ln, ny / Ln
    f.append(varrow(PRx, PRy, PRx - nx * 92, PRy - ny * 92, color=FIELD, sw=3, head=11))
    f.append(text(PRx - nx * 92 - 4, PRy - ny * 92 + 17, "виска ⟂ поверхні", size=12, bold=True, color=FIELD))
    f.append(varrow(cxR, cy, cxR + rx, cy, color=NEG, sw=2, head=9))
    f.append(text(cxR + rx / 2, cy + 16, "екв.", size=10, color=NEG))
    f.append(varrow(cxR, cy, cxR, cy - ry, color=NEG, sw=2, head=9))
    f.append(text(cxR - 14, cy - ry / 2, "пол.", size=10, color=NEG, anchor="end"))
    f.append(text(cxR, cy + ry + 42, "РІВНОВАГА: сплюснутий еліпсоїд", size=12, bold=True))
    f.append(text(cxR, cy + ry + 59, "виска ⟂ поверхні скрізь", size=11, color=MUTED))

    b, w, h = textbox(W / 2, H - 22,
                      "Δh ≈ ½·Ω²·R²/g ≈ 11 км (жорстке поле);  самопритягання здуття  →  реальні ≈ 21 км",
                      size=12, pad=9, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "geoid-equilibrium.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_two_frames(), fig_three_forces(), fig_effective_gravity(),
          fig_naming_mirror(), fig_concept_status(),
          fig_comfort_zone(), fig_habitat_astronaut(),
          fig_axis_centrifugal(), fig_latitude_components(), fig_geoid_equilibrium()]
    print("written:")
    for p in ps:
        print("  ", p)
