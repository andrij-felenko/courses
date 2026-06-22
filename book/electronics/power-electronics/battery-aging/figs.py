# -*- coding: utf-8 -*-
"""Фігури до теми «Старіння батарей».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Два старіння: календарне (від часу) і циклічне (зверху) ───────────────────
def fig_two_agings():
    W, H = 780, 420
    f = [text(W / 2, 28, "Два старіння: від часу й від циклів", size=16, bold=True)]
    ox, oy = 90, 320          # початок осей
    span_x, top = 620, 70
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox - 8, top + 6, "ємність", size=11, color=MUTED, anchor="end"))
    f.append(text(ox + span_x, oy + 22, "час / використання →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 8, top + 2, "", size=10))  # spacer
    # рівень 100%
    full = top + 6
    f.append(text(ox - 8, full + 4, "100%", size=10, color=MUTED, anchor="end"))
    # поріг кінця життя 80%
    eol = full + (oy - full) * 0.30
    f.append(line(ox, eol, ox + span_x, eol, color=MUTED, sw=1.0, dash="5,4"))
    f.append(text(ox + span_x, eol - 6, "кінець життя ~80%", size=10, color=MUTED, anchor="end"))
    # календарна крива (зелена, пунктир): повільний спад √часу
    cal = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ox + t * span_x
        yy = full + (oy - full) * 0.34 * math.sqrt(t)
        cal.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in cal), FIELD))
    f.append(text(ox + span_x * 0.52, full + (oy - full) * 0.34 * math.sqrt(0.52) - 8,
                  "лише час (календарне)", size=11, color=FIELD, anchor="middle", bold=True))
    # сумарна крива (червона): календар + цикли, з прискоренням під кінець
    tot = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ox + t * span_x
        yy = full + (oy - full) * (0.34 * math.sqrt(t) + 0.42 * t * t)
        tot.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in tot), POS))
    f.append(text(ox + span_x * 0.74,
                  full + (oy - full) * (0.34 * math.sqrt(0.74) + 0.42 * 0.74 * 0.74) + 16,
                  "час + цикли", size=11.5, color=POS, anchor="middle", bold=True))
    b, _, _ = textbox(W / 2, 388,
                      "комірка старіє двома шляхами одразу: просто від часу й від кожного циклу заряд-розряд.\nобидва тягнуть ємність донизу, а опір — догори; тепло множить і те, і те.",
                      size=10.5, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "two-agings.svg"), W, H, *f)


# ── Спад ємності та зростання опору ──────────────────────────────────────────
def fig_fade():
    W, H = 780, 420
    f = [text(W / 2, 28, "Спад ємності та зростання опору", size=16, bold=True)]
    ox, oy = 90, 320
    span_x, top = 620, 70
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 22, "цикли / роки →", size=11, color=MUTED, anchor="end"))
    full = top + 10
    # шкала ємності
    for pct, lab in ((0.0, "100%"), (0.30, "80%"), (0.60, "60%")):
        yy = full + (oy - full) * pct
        f.append(line(ox - 4, yy, ox, yy, color=MUTED, sw=1.0))
        f.append(text(ox - 8, yy + 4, lab, size=9.5, color=MUTED, anchor="end"))
    # поріг 80%
    eol = full + (oy - full) * 0.30
    f.append(line(ox, eol, ox + span_x, eol, color=MUTED, sw=1.0, dash="6,4"))
    f.append(text(ox + span_x, eol - 6, "кінець життя ≈ 80%", size=10, color=MUTED, anchor="end"))
    # «коліно»: спершу повільно, тоді швидше
    cap = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ox + t * span_x
        yy = full + (oy - full) * (0.12 * t + 0.55 * t * t * t)
        cap.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in cap), NEG))
    f.append(text(ox + span_x * 0.30, full + (oy - full) * (0.12 * 0.30 + 0.55 * 0.30**3) - 8,
                  "ємність", size=11, color=NEG, anchor="middle", bold=True))
    # опір росте (червоний пунктир) — окрема довільна шкала, знизу вгору
    res = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ox + t * span_x
        yy = oy - 24 - (oy - full - 90) * (0.10 * t + 0.55 * t * t * t)
        res.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="5,3"/>'
             % (" ".join("%.1f,%.1f" % p for p in res), POS))
    f.append(text(ox + span_x * 0.62, oy - 24 - (oy - full - 90) * (0.10 * 0.62 + 0.55 * 0.62**3) - 8,
                  "Rвн росте", size=11, color=POS, anchor="middle", bold=True))
    b, _, _ = textbox(W / 2, 388,
                      "з циклами й роками ємність повзе вниз, а внутрішній опір — угору.\n«кінець життя» традиційно беруть за падіння ємності до 80% від початкової —\nце поріг для планування заміни, а не «смерть» комірки.",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "fade.svg"), W, H, *f)


# ── Що пришвидшує старіння літію ─────────────────────────────────────────────
def fig_killers():
    W, H = 800, 380
    f = [text(W / 2, 28, "Що пришвидшує старіння літію", size=16, bold=True)]
    cards = [
        ("Спека", "кожні +10 °C\n≈ вдвічі швидше\n(Арреніус)", POS, "#fbeee6"),
        ("Зберігання на 100%", "повний заряд\nстарить найшвидше,\nнадто в теплі", POS, "#fbeee6"),
        ("Глибокий розряд", "висадка «в нуль»\nі нижче\nушкоджує комірку", NEG, "#eef3fb"),
        ("Струм і холодний заряд", "великий C-rate,\nзаряд на морозі —\nстрес і осад літію", NEG, "#eef3fb"),
    ]
    n = len(cards)
    bw, bh, gap = 178, 150, 16
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    cy = 165
    for i, (title_, body, col, fill) in enumerate(cards):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        f.append(fitbox(x + 8, cy - bh / 2 + 12, bw - 16, 30, title_, size=13, bold=True,
                        color=col, fill=fill, stroke=fill, sw=0))
        f.append(line(x + 14, cy - bh / 2 + 46, x + bw - 14, cy - bh / 2 + 46, color=MUTED, sw=0.8))
        f.append(mtext(x + bw / 2, cy - 2, body, size=10.5, color=INK))
    b, _, _ = textbox(W / 2, 350,
                      "головний прискорювач — ТЕПЛО: воно множить швидкість усіх реакцій старіння; найгірша пара — гаряче І повне.\nза календарною частиною стоїть невідворотний ріст шару SEI, що поволі з'їдає літій і піднімає опір.",
                      size=10.5, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "killers.svg"), W, H, *f)


# ── Глибина розряду проти ресурсу циклів ─────────────────────────────────────
def fig_dod():
    W, H = 780, 410
    f = [text(W / 2, 28, "Глибина розряду вирішує: мілкі цикли живуть довше",
              size=16, bold=True)]
    ox, oy = 110, 330
    f.append(line(ox, oy, ox + 600, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, 80, color=MUTED, sw=1.4))
    f.append(text(ox - 8, 86, "циклів", size=11, color=MUTED, anchor="end"))
    bars = [
        ("100% DoD", "~500", 500, POS, "#fbeee6"),
        ("80% DoD", "~1000", 1000, "#caa24a", "#fbf3df"),
        ("50% DoD", "~3000", 3000, FIELD, "#e9f7ef"),
        ("20% DoD", "~10000+", 10000, NEG, "#eef3fb"),
    ]
    maxv = 10000.0
    bw, gap = 110, 30
    x = ox + 40
    top_lim = 95
    for lab, num, val, col, fill in bars:
        h = (oy - top_lim) * (val / maxv)
        y = oy - h
        f.append(rect(x, y, bw, h, fill=fill, stroke=col, sw=2))
        f.append(text(x + bw / 2, y - 8, num, size=12, bold=True, color=col))
        f.append(text(x + bw / 2, oy + 18, lab, size=11, bold=True, color=col))
        x += bw + gap
    b, _, _ = textbox(W / 2, 384,
                      "розряджати на півглибини замість «у нуль» — і та сама комірка витримає в рази більше циклів.\nзвідси прийом: користуватися лише СЕРЕДИНОЮ заряду (напр. 20–80%),\nжертвуючи частиною ємності заради довшого життя.",
                      size=10.5, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "dod.svg"), W, H, *f)


# ── Зберігання: заряд × температура → швидкість старіння ──────────────────────
def fig_storage():
    W, H = 860, 410
    f = [text(W / 2, 28, "Зберігання: заряд × температура", size=16, bold=True)]
    cols = ["прохолодно", "тепло", "спека"]
    rows = ["100% (повна)", "~50% (краще)", "низька"]
    # клітинка: (текст, заливка, обводка)
    G, Y, R = "#e9f7ef", "#fbf3df", "#fbeee6"
    grid = [
        [("помірно", Y, "#caa24a"), ("швидко", R, POS), ("найшвидше", R, POS)],
        [("повільно", G, FIELD),   ("помірно", Y, "#caa24a"), ("швидко", R, POS)],
        [("помірно", Y, "#caa24a"), ("помірно", Y, "#caa24a"), ("швидко", R, POS)],
    ]
    cw, ch, gap = 165, 62, 8
    x0, y0 = 300, 78
    for j, c in enumerate(cols):
        f.append(text(x0 + j * (cw + gap) + cw / 2, y0 - 8, c, size=11.5, bold=True))
    for i, r in enumerate(rows):
        yy = y0 + i * (ch + gap)
        f.append(text(x0 - 12, yy + ch / 2 + 4, r, size=11, bold=True, anchor="end"))
        for j in range(3):
            lab, fill, col = grid[i][j]
            x = x0 + j * (cw + gap)
            f.append(rect(x, yy, cw, ch, fill=fill, stroke=col, sw=1.6))
            f.append(text(x + cw / 2, yy + ch / 2 + 5, lab, size=11.5, bold=True, color=col))
    b, _, _ = textbox(W / 2, 356,
                      "найкраще для довгого зберігання — комірка НАПОЛОВИНУ (~50%, 3.7–3.8 В) і ПРОХОЛОДНА; найгірше — повна й гаряча.\nдуже низький заряд теж погано: за місяці саморозряду комірка може просісти нижче безпечного й померти.",
                      size=10.5, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "storage.svg"), W, H, *f)


# ── Проєктувати під деградацію: робоче вікно + ходи ──────────────────────────
def fig_design():
    W, H = 820, 420
    f = [text(W / 2, 28, "Проєктувати «під деградацію»", size=16, bold=True)]
    # ліворуч — батарея з робочим вікном усередині
    bx, by, bw, bh = 70, 80, 130, 230
    f.append(text(bx + bw / 2, by - 12, "користуйся серединою", size=11, bold=True))
    f.append(rect(bx, by, bw, bh, fill="#f6f6f6", stroke=MUTED, sw=1.5))
    f.append(rect(bx, by, bw, bh * 0.20, fill="#fbeee6", stroke="none", sw=0))
    f.append(text(bx + bw / 2, by + bh * 0.10 + 4, "не до 100%", size=9.5, color=POS, bold=True))
    f.append(rect(bx, by + bh * 0.20, bw, bh * 0.55, fill="#e9f7ef", stroke="none", sw=0))
    f.append(text(bx + bw / 2, by + bh * 0.45, "робоче вікно", size=11, color=FIELD, bold=True))
    f.append(text(bx + bw / 2, by + bh * 0.45 + 18, "(напр. 20–80%)", size=9.5, color=INK))
    f.append(rect(bx, by + bh * 0.75, bw, bh * 0.25, fill="#fbeee6", stroke="none", sw=0))
    f.append(text(bx + bw / 2, by + bh * 0.875 + 4, "не в нуль", size=9.5, color=POS, bold=True))
    f.append(rect(bx, by, bw, bh, fill="none", stroke=MUTED, sw=1.5))
    # праворуч — список ходів
    px, py, pw, ph = 250, 70, 500, 248
    f.append(rect(px, py, pw, ph, fill="#f6f6f6", stroke=MUTED, sw=1.4))
    f.append(text(px + pw / 2, py + 26, "Шість ходів довговічності", size=13, bold=True))
    moves = [
        "Бери батарею БІЛЬШУ — щоб і на 80% EoL вистачало",
        "Заряджай нижче (4.1 В) — життя в рази довше",
        "Циклюй серединою, не «0–100%»",
        "Тримай прохолодно; уникай «спека + повна»",
        "Зберігай на ~50%, не повною",
        "Передбач ЗАМІНУ батареї в конструкції",
    ]
    for i, m in enumerate(moves):
        yy = py + 56 + i * 30
        f.append(text(px + 22, yy, "•", size=13, color=FIELD, anchor="start", bold=True))
        f.append(text(px + 40, yy, m, size=11, color=INK, anchor="start"))
    b, _, _ = textbox(W / 2, 390,
                      "деградація неминуча — її ПЛАНУЮТЬ: запас ємності на кінець життя, лагідний режим, доступ до заміни.\nздоров'я (SoH) тим часом стежить за двома знаками — спадом ємності та зростанням Rвн.",
                      size=10.5, fill="#e9f7ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "design.svg"), W, H, *f)


# ── (для вставки math-calendar-arrhenius) Арреніус + √часу ────────────────────
def fig_calendar_law():
    W, H = 800, 400
    f = [text(W / 2, 28, "Календарне старіння: множник тепла × хід часу", size=16, bold=True)]
    # ЛІВА панель: Арреніус — швидкість подвоюється кожні +10 °C (стовпчики)
    f.append(text(220, 60, "темп старіння від температури", size=11.5, bold=True))
    ox, oy = 90, 250
    f.append(line(ox, oy, ox + 280, oy, color=MUTED, sw=1.3))
    f.append(line(ox, oy, ox, 80, color=MUTED, sw=1.3))
    temps = [("15 °C", 1), ("25 °C", 2), ("35 °C", 4), ("45 °C", 8)]
    maxv = 8.0
    bw, gap = 46, 22
    x = ox + 26
    for lab, val in temps:
        h = (oy - 90) * (val / maxv)
        y = oy - h
        col = FIELD if val <= 2 else (("#caa24a") if val == 4 else POS)
        fill = "#e9f7ef" if val <= 2 else ("#fbf3df" if val == 4 else "#fbeee6")
        f.append(rect(x, y, bw, h, fill=fill, stroke=col, sw=1.8))
        f.append(text(x + bw / 2, y - 7, "×%d" % val, size=11, bold=True, color=col))
        f.append(text(x + bw / 2, oy + 17, lab, size=10, color=INK))
        x += bw + gap
    f.append(text(ox + 140, oy + 40, "кожні +10 °C → темп ×2", size=10.5, color=POS,
                  italic=True, anchor="middle"))
    # розділювач
    f.append(line(W / 2, 70, W / 2, 300, color="#dddddd", sw=1.2, dash="4,4"))
    # ПРАВА панель: спад ємності ∝ √часу (корінь — спершу швидко, тоді вповільнюється)
    f.append(text(W / 2 + 200, 60, "втрата ємності з часом", size=11.5, bold=True))
    ax, ay = W / 2 + 60, 250
    span = 250
    f.append(line(ax, ay, ax + span, ay, color=MUTED, sw=1.3))
    f.append(line(ax, ay, ax, 80, color=MUTED, sw=1.3))
    f.append(text(ax + span, ay + 18, "час →", size=10, color=MUTED, anchor="end"))
    f.append(text(ax - 8, 92, "втрата", size=10, color=MUTED, anchor="end"))
    pts = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ax + t * span
        yy = ay - (ay - 95) * math.sqrt(t)
        pts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts), NEG))
    f.append(text(ax + span * 0.55, ay - (ay - 95) * math.sqrt(0.55) - 10,
                  "∝ √часу", size=11.5, color=NEG, bold=True, anchor="middle"))
    b, _, _ = textbox(W / 2, 370,
                      "календарну втрату ємності описують добутком: множник температури (Арреніус, ×2 на кожні +10 °C)\nна хід у часі (≈ корінь із часу — SEI росте дедалі повільніше).",
                      size=10.5, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "calendar-law.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_agings()
    fig_fade()
    fig_killers()
    fig_dod()
    fig_storage()
    fig_design()
    fig_calendar_law()
    print("OK: 7 figures ->", IMG)
