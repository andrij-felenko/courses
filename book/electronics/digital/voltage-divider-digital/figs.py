# -*- coding: utf-8 -*-
"""Фігури до теми «Дільник напруги як зсувач рівнів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Вікно попадання: вихід має лягти між VIH і абсолютним максимумом ──────
def fig_design_window():
    W, H = 720, 430
    f = [text(W / 2, 28, "Ціль дільника — не «рівно 3.3 В», а попасти у вікно над VIH", size=15.5, bold=True)]

    # вертикальна шкала напруги приймача (3.3-В CMOS-вхід)
    base = 370          # 0 В
    topv = 70           # верх шкали (~4 В)
    vmax_scale = 4.0
    cx = 250
    bw = 96

    def y(v):
        return base - (v / vmax_scale) * (base - topv)

    # смуга шкали
    f.append(rect(cx - bw / 2, topv, bw, base - topv, fill="#f4f6f8", stroke=LINE, sw=1.6))
    f.append(text(cx, base + 20, "0 В (GND)", size=11, color=MUTED))

    VIL, VIH = 0.83, 2.48
    VABS = 3.6          # абсолютний максимум на піні (VDD 3.3 + 0.3)
    # зони: нуль (зелена), невизначеність (сіра), одиниця (синя до VABS), небезпека (червона понад)
    f.append(rect(cx - bw / 2, y(VIL), bw, base - y(VIL), fill="#eaf6ee", stroke=None, sw=0))
    f.append(rect(cx - bw / 2, y(VABS), bw, y(VIH) - y(VABS), fill="#eaf0fd", stroke=None, sw=0))
    f.append(rect(cx - bw / 2, topv, bw, y(VABS) - topv, fill="#fdecea", stroke=None, sw=0))
    f.append(rect(cx - bw / 2, topv, bw, base - topv, fill="none", stroke=LINE, sw=1.6))

    for v, lab, col in [(VIL, "VIL 0.83", FIELD), (VIH, "VIH 2.48", NEG), (VABS, "макс 3.6", POS)]:
        f.append(line(cx - bw / 2, y(v), cx + bw / 2, y(v), color=col, sw=2))
        f.append(text(cx - bw / 2 - 8, y(v) + 4, lab, size=11, color=col, anchor="end", bold=True))

    # підписи зон праворуч від смуги
    f.append(text(cx + bw / 2 + 10, (y(VIH) + y(VABS)) / 2 + 4, "робоче вікно «1»", size=11.5,
                  color=NEG, anchor="start", bold=True))
    f.append(text(cx + bw / 2 + 10, (y(VIL) + base) / 2, "зона «0»", size=10.5, color=FIELD, anchor="start"))
    f.append(text(cx + bw / 2 + 10, (y(VIH) + y(VIL)) / 2, "невизначено", size=10.5, color=MUTED, anchor="start"))
    f.append(text(cx + bw / 2 + 10, (topv + y(VABS)) / 2, "перенапруга", size=10.5, color=POS, anchor="start"))

    # розкид виходу дільника через допуски: номінал 2.97, спред 2.7..3.25
    nom, lo, hi = 2.97, 2.72, 3.22
    xb = cx + bw / 2 + 150
    f.append(line(xb, y(hi), xb, y(lo), color=INK, sw=6))
    f.append(circle(xb, y(nom), 5, fill=POS, stroke=INK, sw=1))
    f.append(text(xb + 14, y(nom) + 4, "номінал 2.97 В", size=11, color=INK, anchor="start", bold=True))
    f.append(text(xb + 14, y(hi) - 2, "верх 3.22 В", size=10, color=MUTED, anchor="start"))
    f.append(text(xb + 14, y(lo) + 12, "низ 2.72 В", size=10, color=MUTED, anchor="start"))
    # підпис бруса розкиду
    f.append(mtext(xb, base + 18, ["розкид виходу", "(± живлення, ± резистори)"], size=10, color=MUTED))

    b, _, _ = textbox(W / 2, H - 26,
                      "увесь брус розкиду лежить між VIH і максимумом → одиниця певна, пін цілий",
                      size=11.5, fill="#eef6ef", stroke=FIELD, bold=True)
    f.append(b)
    render(os.path.join(IMG, "design-window.svg"), W, H, *f)


# ── 2. RC-стеля: власний опір дільника + ємність = млявий фронт ──────────────
def fig_rc_ceiling():
    W, H = 720, 400
    f = [text(W / 2, 26, "Власний опір дільника заряджає ємність лінії — і гальмує фронт", size=15, bold=True)]

    ox, oy = 92, 300
    ax_w, ax_h = 470, 220
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 36, "час (умовні одиниці)", size=12, color=INK))
    f.append(mtext(ox - 60, oy - ax_h / 2, ["напруга", "на виході"], size=11, color=INK))

    yVDD = oy - ax_h
    yVIH = oy - 0.75 * ax_h
    f.append(line(ox, yVDD, ox + ax_w, yVDD, color=MUTED, sw=1.2, dash="4,5"))
    f.append(text(ox + ax_w, yVDD - 6, "3.3 В", size=11, color=MUTED, anchor="end"))
    f.append(line(ox, yVIH, ox + ax_w, yVIH, color=NEG, sw=1.4, dash="3,4"))
    f.append(text(ox + ax_w, yVIH - 6, "VIH", size=11, color=NEG, anchor="end"))

    def curve(tau, color, sw=2.6):
        pts = []
        for i in range(0, int(ax_w) + 1, 5):
            t = i / ax_w * 6.0
            v = 1 - math.exp(-t / tau)
            pts.append("%.1f,%.1f" % (ox + i, oy - v * ax_h))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' %
                 (" ".join(pts), color, sw))

    curve(0.6, FIELD)     # малий R (жорсткий дільник) — швидко
    curve(2.4, POS)       # великий R (ощадний) — мляво
    f.append(mtext(ox + 60, oy - 0.92 * ax_h, ["малі R (напр. 1.7 / 3.3 кОм):", "фронт швидкий"],
                   size=10.5, color=FIELD, anchor="start"))
    f.append(mtext(ox + 250, oy - 0.40 * ax_h, ["великі R (напр. 100 / 200 кОм):", "фронт лінивий → пізно VIH"],
                   size=10.5, color=POS, anchor="start"))

    # права колонка: стеля частоти в числах
    b, _, _ = textbox(645, 150,
                      "стеля ≈ 1/(10·τ)\nτ = (R1∥R2)·C\n\nмалі R: τ≈1.1 нс\n→ до ~90 МГц\nвеликі R: τ≈65 нс\n→ до ~1.5 МГц",
                      size=11, fill="#eef2f8", stroke=NEG, min_w=140)
    f.append(b)
    render(os.path.join(IMG, "rc-ceiling.svg"), W, H, *f)


# ── 3. Двобічний затиск: який опір плечей брати ──────────────────────────────
def fig_stiffness():
    W, H = 720, 380
    f = [text(W / 2, 28, "Опір плечей: завеликий — повільно й похибка; замалий — жере струм", size=14.5, bold=True)]

    ox, oy = 100, 300
    ax_w, ax_h = 520, 210
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))
    f.append(text(ox + ax_w / 2, oy + 36, "опір плечей R  (мале → велике)", size=12, color=INK))
    f.append(mtext(ox - 62, oy - ax_h / 2, ["ціна", "(гірше →)"], size=11, color=INK))

    # ліва крива — струм/споживання росте при малому R
    ptsI = []
    for i in range(0, int(ax_w) + 1, 5):
        x = i / ax_w
        v = math.exp(-x * 5.0)               # спадає з ростом R
        ptsI.append("%.1f,%.1f" % (ox + i, oy - v * ax_h * 0.92))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ptsI), POS))
    # права крива — RC-млявість + похибка від струму входу росте при великому R
    ptsR = []
    for i in range(0, int(ax_w) + 1, 5):
        x = i / ax_w
        v = math.exp((x - 1.0) * 5.0)        # росте з ростом R
        ptsR.append("%.1f,%.1f" % (ox + i, oy - v * ax_h * 0.92))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(ptsR), NEG))

    # зелена «долина» посередині
    vx1, vx2 = ox + ax_w * 0.40, ox + ax_w * 0.62
    f.append(rect(vx1, oy - ax_h, vx2 - vx1, ax_h, fill="#eaf6ee", stroke=None, sw=0))
    f.append(line(vx1, oy - ax_h, vx1, oy, color=FIELD, sw=1.2, dash="3,4"))
    f.append(line(vx2, oy - ax_h, vx2, oy, color=FIELD, sw=1.2, dash="3,4"))
    f.append(text((vx1 + vx2) / 2, oy - ax_h - 8, "розумний діапазон", size=11, color=FIELD, bold=True))

    f.append(mtext(ox + 40, oy - 0.80 * ax_h, ["малий R:", "зайвий струм,", "нагрів, вантажить драйвер"],
                   size=10.5, color=POS, anchor="start"))
    f.append(mtext(ox + ax_w - 210, oy - 0.80 * ax_h, ["великий R:", "млявий фронт (RC) +", "похибка від струму входу"],
                   size=10.5, color=NEG, anchor="start"))
    f.append(mtext((vx1 + vx2) / 2, oy - 26, ["одиниці кОм", "(типово)"], size=10.5, color=FIELD))
    render(os.path.join(IMG, "stiffness.svg"), W, H, *f)


# ── 4. Компенсований дільник: конденсатор проти R1 вирівнює фронт ────────────
def fig_compensated():
    W, H = 720, 380
    f = [text(W / 2, 28, "Компенсація: конденсатор над R1 знімає RC-штраф (прийом щупа осцилографа)", size=13.5, bold=True)]

    sx = 175
    vtop, vout, vbot = 80, 200, 320
    # вхід
    f.append(text(sx, vtop - 14, "вхід 5 В", size=12, bold=True, color=POS))
    f.append(line(sx, vtop, sx, vtop + 20, color=LINE, sw=2))
    # R1 з паралельним C1
    f.append(rect(sx - 16, vtop + 20, 32, 60, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(sx + 40, vtop + 52, "R1", size=12, color=INK, anchor="start"))
    # C1 як дві пластини збоку від R1
    cxx = sx - 52
    f.append(line(sx, vtop + 20, cxx, vtop + 20, color=NEG, sw=1.6))
    f.append(line(cxx, vtop + 20, cxx, vtop + 42, color=NEG, sw=1.6))
    f.append(line(cxx - 12, vtop + 42, cxx + 12, vtop + 42, color=NEG, sw=2.2))
    f.append(line(cxx - 12, vtop + 50, cxx + 12, vtop + 50, color=NEG, sw=2.2))
    f.append(line(cxx, vtop + 50, cxx, vtop + 80, color=NEG, sw=1.6))
    f.append(line(cxx, vtop + 80, sx, vtop + 80, color=NEG, sw=1.6))
    f.append(text(cxx - 20, vtop + 46, "C1", size=11, color=NEG, anchor="end", bold=True))
    # вузол виходу
    f.append(line(sx, vtop + 80, sx, vout, color=LINE, sw=2))
    f.append(circle(sx, vout, 4, fill=INK, stroke=INK, sw=1))
    f.append(line(sx, vout, sx + 120, vout, color=NEG, sw=2))
    f.append(text(sx + 130, vout + 4, "вихід → 3.3-В вхід", size=11, color=NEG, anchor="start", bold=True))
    # R2 з паразитною C2 (ємність входу+лінії)
    f.append(rect(sx - 16, vout + 10, 32, 60, fill=FILL, stroke=LINE, sw=1.6))
    f.append(text(sx + 40, vout + 42, "R2", size=12, color=INK, anchor="start"))
    f.append(mtext(sx + 130, vout + 22, ["C2 = ємність", "лінії + входу"], size=10, color=MUTED, anchor="start"))
    f.append(line(sx, vout + 70, sx, vbot, color=LINE, sw=2))
    # GND
    f.append(line(sx - 18, vbot, sx + 18, vbot, color=INK, sw=2.4))
    f.append(line(sx - 11, vbot + 6, sx + 11, vbot + 6, color=INK, sw=2))
    f.append(line(sx - 5, vbot + 12, sx + 5, vbot + 12, color=INK, sw=2))

    b, _, _ = textbox(540, 150,
                      "УМОВА БАЛАНСУ:\nR1·C1 = R2·C2\n\nтоді поділ ОДНАКОВИЙ\nна DC і на HF —\nфронт не розмивається",
                      size=12, fill="#eef6ef", stroke=FIELD, bold=True, min_w=180)
    f.append(b)
    b2, _, _ = textbox(540, 285,
                       "перекрут → викид/завал;\nсаме це «крутять»\nна щупі ×10",
                       size=11, fill="#eef2f8", stroke=NEG)
    f.append(b2)
    render(os.path.join(IMG, "compensated.svg"), W, H, *f)


# ── 5. (вставка math) Три стани компенсації: недо / баланс / пере ────────────
def fig_compensation_states():
    W, H = 720, 360
    f = [text(W / 2, 26, "Три стани дільника з ємностями: як фронт залежить від R1·C1 vs R2·C2", size=13.5, bold=True)]

    # три однакові панелі з відгуком на вхідну сходинку
    pw, ph = 200, 190
    py = 70
    gap = 20
    x0 = (W - 3 * pw - 2 * gap) / 2

    panels = [
        ("недокомпенсація", "R1·C1 < R2·C2", POS, "under"),
        ("баланс", "R1·C1 = R2·C2", FIELD, "match"),
        ("перекомпенсація", "R1·C1 > R2·C2", NEG, "over"),
    ]

    for i, (name, cond, col, kind) in enumerate(panels):
        px = x0 + i * (pw + gap)
        # рамка панелі
        f.append(rect(px, py, pw, ph, fill=BG, stroke=LINE, sw=1.4))
        # осі всередині панелі
        ax_l, ax_r = px + 22, px + pw - 12
        ax_b, ax_t = py + ph - 26, py + 22
        f.append(line(ax_l, ax_b, ax_r, ax_b, color=INK, sw=1.4))   # час
        f.append(line(ax_l, ax_b, ax_l, ax_t, color=INK, sw=1.4))   # напруга

        # рівень усталення (кінцевий, резистивний поділ) — пунктир
        y_final = ax_t + (ax_b - ax_t) * 0.40
        f.append(line(ax_l, y_final, ax_r, y_final, color=MUTED, sw=1.1, dash="4,4"))
        f.append(text(ax_r, y_final - 5, "рівень", size=9, color=MUTED, anchor="end"))

        # момент фронту
        x_edge = ax_l + (ax_r - ax_l) * 0.30

        # до фронту — нуль
        f.append(line(ax_l, ax_b, x_edge, ax_b, color=col, sw=2.4))

        # висота миттєвого ємнісного стрибка залежно від стану
        if kind == "under":
            y_jump = ax_b - (ax_b - y_final) * 0.45      # стрибок нижчий за рівень
        elif kind == "match":
            y_jump = y_final                              # стрибок = рівень
        else:
            y_jump = y_final - (ax_b - y_final) * 0.55    # стрибок вище рівня (викид)

        # вертикаль стрибка
        f.append(line(x_edge, ax_b, x_edge, y_jump, color=col, sw=2.4))

        # перехідна крива від стрибка до рівня (експонента)
        pts = []
        seg = ax_r - x_edge
        for k in range(0, int(seg) + 1, 3):
            t = k / seg * 4.0
            v = y_final + (y_jump - y_final) * math.exp(-t / 1.1)
            pts.append("%.1f,%.1f" % (x_edge + k, v))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' %
                 (" ".join(pts), col))

        # мітка характеру фронту
        if kind == "under":
            note = "фронт заокруглено"
        elif kind == "match":
            note = "фронт чистий"
        else:
            note = "викид на фронті"
        f.append(text(px + pw / 2, py + ph + 18, note, size=10.5, color=col, bold=True))
        # заголовок панелі + умова
        f.append(text(px + pw / 2, py - 24, name, size=11.5, color=col, bold=True))
        f.append(text(px + pw / 2, py - 8, cond, size=10.5, color=INK))

    b, _, _ = textbox(W / 2, H - 20,
                      "стрибок = ємнісний поділ C1/(C1+C2);  рівень = резистивний поділ R2/(R1+R2);  збіглися → фронт цілий",
                      size=10.5, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "compensation-states.svg"), W, H, *f)


if __name__ == "__main__":
    fig_design_window()
    fig_rc_ceiling()
    fig_stiffness()
    fig_compensated()
    fig_compensation_states()
    print("OK: 5 figures ->", IMG)
