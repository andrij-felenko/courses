# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «KY-038 — мікрофонний давач звуку».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Дві доріжки сигналу: сирий мікрофон → AO; мікрофон → компаратор → DO ────
def fig_block():
    W, H = 940, 470
    f = [text(W / 2, 30, "Що всередині KY-038: дві доріжки з одного мікрофона",
              size=17, bold=True)]

    # мікрофон (ліворуч, спільне джерело обох доріжок)
    mx, my = 130, H / 2
    f.append(circle(mx, my, 46, fill="#eef2f6", stroke=INK, sw=2.5))
    f.append(circle(mx, my, 30, fill="#dbe3ea", stroke=MUTED, sw=1.5))
    f.append(text(mx, my - 60, "електретний", size=13, bold=True))
    f.append(text(mx, my + 74, "мікрофон", size=13, bold=True))
    f.append(text(mx, my + 5, "MIC", size=13, color=MUTED, bold=True))

    # вузол розгалуження
    jx = mx + 90
    f.append(line(mx + 46, my, jx, my, color=INK, sw=2.5))
    f.append(circle(jx, my, 4.5, fill=INK, stroke=INK))

    # ── верхня доріжка: прямо на AO (сира, без підсилення) ──
    ay = my - 110
    b, bw, bh = textbox(360, ay, ["дільник напруги", "VR1 (100 кΩ) + R3"],
                        size=13, pad=12, fill="#eaf0fd", stroke=NEG, min_w=210)
    bl, br = 360 - bw / 2, 360 + bw / 2          # ліва/права межа блоку
    f.append(line(jx, my, jx, ay, color=NEG, sw=2.5))
    f.append(line(jx, ay, bl, ay, color=NEG, sw=2.5))     # вхід у блок зліва
    f.append(b)
    f.append(arrow(br, ay, 690, ay, color=NEG, sw=2.5))   # вихід із блоку справа
    b2, bw2, bh2 = textbox(760, ay, ["AO", "сира напруга"], size=14, pad=12,
                           fill="#eaf0fd", stroke=NEG, min_w=140, bold=True)
    f.append(b2)
    f.append(text(760, ay - 44, "аналоговий вихід", size=12, color=MUTED))
    f.append(text(360, ay + 42, "жодного підсилювача — лише поділ і зсув", size=12, color=MUTED, italic=True))

    # ── нижня доріжка: у компаратор LM393 → DO ──
    dy = my + 110
    b3, bw3, bh3 = textbox(400, dy, ["компаратор LM393", "(порівняти з порогом)"],
                           size=13, pad=12, fill="#fdecea", stroke=POS, min_w=240)
    cl, cr = 400 - bw3 / 2, 400 + bw3 / 2
    f.append(line(jx, my, jx, dy, color=POS, sw=2.5))
    f.append(line(jx, dy, cl, dy, color=POS, sw=2.5))     # вхід у компаратор зліва
    f.append(b3)
    # поріг від гвинтика заходить у компаратор знизу
    f.append(line(400, dy + bh3 / 2, 400, dy + 74, color=MUTED, sw=1.8, dash="4,3"))
    f.append(text(400, dy + 90, "поріг ← гвинтик (VR1, R2/R6)", size=12, color=MUTED))
    f.append(arrow(cr, dy, 690, dy, color=POS, sw=2.5))   # вихід компаратора справа
    b4, bw4, bh4 = textbox(760, dy, ["DO", "0 / 1"], size=14, pad=12,
                           fill="#fdecea", stroke=POS, min_w=140, bold=True)
    f.append(b4)
    f.append(text(760, dy - 44, "цифровий вихід", size=12, color=MUTED))

    render(os.path.join(IMG, 'block.svg'), W, H, *f)


# ── 2. Схема устрою (спрощена принципова) ─────────────────────────────────────
def fig_schematic():
    W, H = 900, 520
    f = [text(W / 2, 30, "Спрощена схема KY-038: живлення мікрофона, дільник, компаратор",
              size=16, bold=True)]

    # шини живлення й землі
    vcc_y, gnd_y = 70, H - 60
    f.append(line(70, vcc_y, W - 70, vcc_y, color=POS, sw=2.5))
    f.append(text(80, vcc_y - 10, "+V (3.3–5 В)", size=13, color=POS, bold=True, anchor="start"))
    f.append(line(70, gnd_y, W - 70, gnd_y, color=INK, sw=2.5))
    f.append(text(80, gnd_y + 22, "GND", size=13, color=INK, bold=True, anchor="start"))

    # ── мікрофон із підтяжкою R (живиться від +V через резистор) ──
    mx = 180
    # R живлення мікрофона
    f.append(line(mx, vcc_y, mx, 150, color=INK, sw=2))
    f.append(rect(mx - 14, 150, 28, 48, fill=FILL, stroke=INK, sw=1.8))
    f.append(text(mx + 40, 176, "R (живлення MIC)", size=12, color=MUTED, anchor="start"))
    # вузол сигналу мікрофона
    node_y = 230
    f.append(line(mx, 198, mx, node_y, color=INK, sw=2))
    f.append(circle(mx, node_y, 4.5, fill=INK, stroke=INK))
    # мікрофон між вузлом і землею
    f.append(circle(mx, node_y + 70, 30, fill="#eef2f6", stroke=INK, sw=2))
    f.append(text(mx, node_y + 74, "MIC", size=12, color=MUTED, bold=True))
    f.append(line(mx, node_y, mx, node_y + 40, color=INK, sw=2))
    f.append(line(mx, node_y + 100, mx, gnd_y, color=INK, sw=2))
    f.append(text(mx - 40, node_y + 74, "електрет", size=12, color=MUTED, anchor="end"))

    # сигнал мікрофона йде праворуч до дільника й до компаратора
    f.append(line(mx, node_y, 340, node_y, color=INK, sw=2))
    f.append(circle(340, node_y, 4.5, fill=INK, stroke=INK))

    # ── дільник VR1 + R3 → AO ──
    vrx = 340
    f.append(line(vrx, node_y, vrx, 300, color=NEG, sw=2))
    f.append(rect(vrx - 16, 300, 32, 46, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(vrx + 26, 322, "VR1 100 кΩ (гвинтик)", size=11, color=NEG, anchor="start"))
    # відбір AO з движка
    ao_y = 346
    f.append(line(vrx, ao_y, vrx + 90, ao_y, color=NEG, sw=2))
    f.append(circle(vrx + 90, ao_y, 4.5, fill=NEG, stroke=NEG))
    f.append(line(vrx + 90, ao_y, vrx + 90, gnd_y - 40, color=NEG, sw=2))
    f.append(rect(vrx + 90 - 14, gnd_y - 40, 28, 40, fill=FILL, stroke=INK, sw=1.6))
    f.append(text(vrx + 118, gnd_y - 18, "R3 150 Ω", size=11, color=MUTED, anchor="start"))
    f.append(line(vrx + 90, gnd_y - 0, vrx + 90, gnd_y, color=INK, sw=2))
    # лінія на пін AO
    f.append(line(vrx + 90, ao_y, 720, ao_y, color=NEG, sw=2))
    b, bw, bh = textbox(770, ao_y, "AO", size=15, pad=12, fill="#eaf0fd",
                        stroke=NEG, bold=True, min_w=70)
    f.append(b)

    # ── компаратор LM393 → DO ──
    cx, cy = 500, node_y + 30
    # трикутник компаратора
    tri = ('<path d="M%.0f %.0f L%.0f %.0f L%.0f %.0f Z" fill="#fdecea" '
           'stroke="%s" stroke-width="2"/>' % (cx, cy - 40, cx, cy + 40, cx + 90, cy, POS))
    f.append(tri)
    f.append(text(cx + 34, cy + 16, "LM393", size=12, color=POS, bold=True, anchor="start"))
    # вхід сигналу (−): дріт спиняється на лівій грані трикутника; знак — усередині
    f.append(line(340, node_y, cx, cy - 22, color=INK, sw=2))
    f.append(text(cx + 12, cy - 14, "−", size=16, color=NEG, bold=True, anchor="start"))
    # опорна напруга (+) від дільника R2/R6
    f.append(line(cx - 70, cy + 22, cx, cy + 22, color=INK, sw=2))
    f.append(text(cx + 12, cy + 28, "+", size=16, color=POS, bold=True, anchor="start"))
    f.append(text(cx - 74, cy + 40, "опора (R2/R6)", size=11, color=MUTED, anchor="start"))
    # вихід компаратора → DO
    f.append(line(cx + 90, cy, 720, cy, color=POS, sw=2))
    b2, bw2, bh2 = textbox(770, cy, "DO", size=15, pad=12, fill="#fdecea",
                           stroke=POS, bold=True, min_w=70)
    f.append(b2)
    # світлодіоди-індикатори (підпис)
    f.append(text(W / 2, H - 18, "L1 — живлення · L2 — спрацювання порога (світить, коли DO активний)",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'schematic.svg'), W, H, *f)


# ── 3. Розводка пін-у-пін до мікроконтролера ──────────────────────────────────
def fig_wiring():
    W, H = 900, 430
    f = [text(W / 2, 30, "Підключення KY-038 чотирма дротами до мікроконтролера",
              size=16, bold=True)]

    # плата KY-038 (ліворуч)
    bx, by, bw, bh = 70, 90, 250, 250
    f.append(rect(bx, by, bw, bh, fill="#e8f0fe", stroke=NEG, sw=2))
    f.append(text(bx + bw / 2, by + 28, "KY-038", size=16, bold=True, color=NEG))
    f.append(circle(bx + 60, by + 90, 26, fill="#dbe3ea", stroke=INK, sw=2))
    f.append(text(bx + 60, by + 94, "MIC", size=11, color=MUTED, bold=True))
    f.append(rect(bx + 150, by + 70, 26, 40, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(bx + 163, by + 128, "гвинтик", size=11, color=MUTED))

    # 4 піни праворуч на платі
    pins = [("AO", NEG, "аналоговий вихід"),
            ("G", INK, "земля"),
            ("+", POS, "живлення 3.3–5 В"),
            ("DO", POS, "цифровий вихід 0/1")]
    px = bx + bw
    p0 = by + 150
    dp = 32
    # цільові точки на боці МК
    mcux = 660
    mcu_y = [128, 196, 244, 300]
    targets = [("A0  (АЦП)", NEG), ("GND", INK), ("+5 В / +3.3 В", POS), ("D2  (цифр. вхід)", POS)]

    for i, (name, col, desc) in enumerate(pins):
        yy = p0 + i * dp
        # штир на правому краї плати
        f.append(rect(px - 6, yy - 9, 26, 18, fill="#fff", stroke=col, sw=1.8, rx=3))
        f.append(text(px + 7, yy + 5, name, size=12, color=col, bold=True))
        # підпис піна — УСЕРЕДИНІ плати, ліворуч від штиря (не на шляху дроту)
        f.append(text(px - 16, yy + 4, desc, size=11, color=MUTED, anchor="end"))

    # плата МК (праворуч)
    mx, mw, mh = mcux, 200, 250
    f.append(rect(mx, 90, mw, mh, fill="#eef7ee", stroke=FIELD, sw=2))
    f.append(text(mx + mw / 2, 118, "мікроконтролер", size=14, bold=True, color=FIELD))
    for i, (lbl, col) in enumerate(targets):
        yy = mcu_y[i] + 20
        f.append(rect(mx - 20, yy - 9, 18, 18, fill="#fff", stroke=col, sw=1.8, rx=3))
        f.append(text(mx + 8, yy + 5, lbl, size=12, color=col, anchor="start", bold=True))

    # дроти пін→ціль (без перетинів написів: різні висоти)
    wire_map = [(p0 + 0 * dp, mcu_y[0] + 20, NEG),   # AO → A0
                (p0 + 1 * dp, mcu_y[1] + 20, INK),   # G → GND
                (p0 + 2 * dp, mcu_y[2] + 20, POS),   # + → 5V
                (p0 + 3 * dp, mcu_y[3] + 20, POS)]   # DO → D2
    for sy, ty, col in wire_map:
        midx = (px + 20 + mx - 20) / 2
        f.append(line(px + 20, sy, midx, sy, color=col, sw=2))
        f.append(line(midx, sy, midx, ty, color=col, sw=2))
        f.append(line(midx, ty, mx - 20, ty, color=col, sw=2))

    f.append(text(W / 2, H - 16,
                  "Читаєш AO аналоговим входом (АЦП) АБО DO — цифровим. + узгоджуй з логікою плати.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, 'wiring.svg'), W, H, *f)


# ── 4. Форма сигналу на AO: тихий зсув, інверсія, крихітний розмах ─────────────
def fig_waveform():
    W, H = 900, 420
    f = [text(W / 2, 30, "Аналоговий вихід KY-038: слабкий і перевернутий",
              size=16, bold=True)]

    # осі
    ox, oy = 90, H - 70
    ax_top = 70
    f.append(line(ox, ax_top, ox, oy, color=INK, sw=2))         # вісь напруги
    f.append(line(ox, oy, W - 60, oy, color=INK, sw=2))         # вісь часу
    f.append(text(ox - 10, ax_top + 4, "U", size=13, anchor="end", bold=True))
    f.append(text(W - 55, oy + 4, "t", size=13, anchor="start", bold=True))

    # рівень спокою (DC-зсув приблизно посередині)
    bias_y = (ax_top + oy) / 2 + 20
    f.append(line(ox, bias_y, W - 60, bias_y, color=MUTED, sw=1.6, dash="5,4"))
    # підпис лінії спокою — ліворуч над тишею, де жоден маркер її не перетинає
    f.append(text(ox + 8, bias_y - 8, "рівень спокою (зсув ≈ ½·V)", size=12, color=MUTED, anchor="start"))

    # тиша: майже рівна лінія на зсуві
    import math
    silence = []
    x = ox + 6
    while x < ox + 230:
        y = bias_y + 3 * math.sin((x - ox) * 0.25)
        silence.append((x, y))
        x += 3
    d = "M %.1f %.1f " % silence[0] + " ".join("L %.1f %.1f" % p for p in silence[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, NEG))
    f.append(text(ox + 118, oy + 22, "тиша", size=12, color=MUTED))

    # звук: коливання НАВКОЛО зсуву, невеликий розмах, ПЕРЕВЕРНУТО
    # (гучніше → нижча напруга: пік звуку тягне лінію ВНИЗ)
    sound = []
    x = ox + 236
    while x < W - 70:
        env = 26  # маленький розмах — «немає справжнього підсилення»
        # інверсія: гучний фронт = провал донизу
        y = bias_y - env * math.sin((x - (ox + 236)) * 0.16) * (-1)
        sound.append((x, y))
        x += 3
    d2 = "M %.1f %.1f " % sound[0] + " ".join("L %.1f %.1f" % p for p in sound[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d2, POS))
    f.append(text((ox + 236 + W - 70) / 2, oy + 22, "звук (гучно)", size=12, color=POS))

    # позначка малого розмаху праворуч
    arrx = W - 110
    f.append(line(arrx, bias_y - 26, arrx, bias_y + 26, color=INK, sw=1.4))
    f.append(line(arrx - 5, bias_y - 26, arrx + 5, bias_y - 26, color=INK, sw=1.4))
    f.append(line(arrx - 5, bias_y + 26, arrx + 5, bias_y + 26, color=INK, sw=1.4))
    f.append(text(arrx - 12, bias_y + 4, "малий", size=11, color=INK, anchor="end"))
    f.append(text(arrx - 12, bias_y + 18, "розмах", size=11, color=INK, anchor="end"))

    # стрілка «гучніше → нижче»
    f.append(text(ox + 40, ax_top + 26, "гучніше = НИЖЧА напруга (сигнал перевернутий)",
                  size=12, color=POS, anchor="start", italic=True))

    render(os.path.join(IMG, 'waveform.svg'), W, H, *f)


# ── 5. DO-дребезг: сирий біт торохтить, вікно лишає одну подію ─────────────────
def fig_debounce():
    import math
    W, H = 940, 430
    f = [text(W / 2, 30, "Один оплеск, сирий DO і чистий результат після вікна",
              size=16, bold=True)]

    ox = 90
    t0, t1 = ox + 20, W - 60                 # межі осі часу
    def X(u): return t0 + (t1 - t0) * u      # u ∈ [0,1] → піксель

    # три доріжки
    lanes = [
        ("сирий DO (з компаратора)", 110, POS),
        ("програма без вікна", 230, INK),
        ("програма з вікном 300 мс", 350, FIELD),
    ]
    for name, y, col in lanes:
        f.append(line(ox, y, t1, y, color=MUTED, sw=1.2))          # базова лінія «0»
        f.append(text(ox - 8, y + 4, name, size=12, color=col, anchor="end"))

    # позиції фронтів «оплеску» — торохтіння навколо порога (u-координати)
    chatter = [0.20, 0.225, 0.245, 0.27, 0.30, 0.34, 0.39]
    hi = 44   # висота імпульсу

    # доріжка 1: сирий DO — пачка коротких імпульсів
    y = 110
    for i, u in enumerate(chatter):
        w = 0.012
        f.append(rect(X(u), y - hi, X(u + w) - X(u), hi, fill="#fdecea", stroke=POS, sw=1.6, rx=2))
    f.append(text(X(0.30), y - hi - 10, "торохтіння біля порога", size=11, color=POS))

    # доріжка 2: наївний код рахує КОЖЕН фронт → 7 подій
    y = 230
    for i, u in enumerate(chatter):
        f.append(line(X(u), y, X(u), y - hi, color=INK, sw=2))
        f.append(circle(X(u), y - hi, 4, fill=INK, stroke=INK))
    f.append(text(X(0.30), y - hi - 10, "7 «подій» з одного оплеску — брехня", size=11, color=INK))

    # доріжка 3: з вікном — лише перший фронт, решта в «мертвій зоні»
    y = 350
    u_first = chatter[0]
    f.append(line(X(u_first), y, X(u_first), y - hi, color=FIELD, sw=2.5))
    f.append(circle(X(u_first), y - hi, 5, fill=FIELD, stroke=FIELD))
    f.append(text(X(u_first), y - hi - 10, "1 подія", size=12, color=FIELD, bold=True, anchor="start"))
    # заштрихована «мертва зона» 300 мс після першого фронту
    dead_end = 0.39 + 0.02
    f.append(rect(X(u_first), y - hi, X(dead_end) - X(u_first), hi, fill="#eafaf0",
                  stroke=FIELD, sw=1.2, rx=3))
    f.append(text((X(u_first) + X(dead_end)) / 2, y + 20,
                  "вікно 300 мс: нові фронти ігноруються", size=11, color=FIELD))

    # вісь часу
    f.append(arrow(ox, H - 50, t1 + 10, H - 50, color=INK, sw=1.8))
    f.append(text(t1 + 14, H - 46, "t", size=13, bold=True, anchor="start"))

    render(os.path.join(IMG, 'debounce.svg'), W, H, *f)


# ── 6. AO-амплітуда: плаваючий зсув і розмах max−min за вікно ──────────────────
def fig_envelope():
    import math
    W, H = 940, 440
    f = [text(W / 2, 30, "Груба гучність із AO: розмах (max−min) навколо плаваючого зсуву",
              size=15, bold=True)]

    ox, oy = 90, H - 70
    ax_top = 66
    f.append(line(ox, ax_top, ox, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, W - 60, oy, color=INK, sw=1.8))
    f.append(text(ox - 10, ax_top + 2, "АЦП", size=12, anchor="end", bold=True))
    f.append(text(W - 55, oy + 4, "t", size=13, anchor="start", bold=True))

    bias_y = (ax_top + oy) / 2 + 14
    # плаваючий зсув (повільна лінія)
    f.append(line(ox, bias_y, W - 60, bias_y, color=NEG, sw=1.8, dash="6,4"))
    f.append(text(W - 66, bias_y - 8, "плаваючий зсув (повільне середнє)",
                  size=11, color=NEG, anchor="end"))

    # сигнал: коливання навколо зсуву, у вікні — сильніші
    pts = []
    x = ox + 6
    while x < W - 62:
        u = (x - ox) / (W - 62 - ox)
        env = 8 + 40 * math.exp(-((u - 0.55) ** 2) / 0.010)   # сплеск гучності всередині
        y = bias_y - env * math.sin((x - ox) * 0.5)
        pts.append((x, y))
        x += 2.5
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (d, INK))

    # вікно вимірювання
    wl, wr = ox + (W - 62 - ox) * 0.44, ox + (W - 62 - ox) * 0.66
    f.append(rect(wl, ax_top + 6, wr - wl, oy - ax_top - 6, fill="none",
                  stroke=FIELD, sw=1.6, rx=4))
    f.append(text((wl + wr) / 2, ax_top + 22, "вікно (напр. 50 мс)", size=12, color=FIELD, bold=True))

    # max та min усередині вікна — горизонтальні маркери
    ymax = bias_y - 48   # найвище відхилення (пік угору)
    ymin = bias_y + 48   # найнижче
    f.append(line(wl, ymax, wr, ymax, color=POS, sw=1.4, dash="3,3"))
    f.append(line(wl, ymin, wr, ymin, color=POS, sw=1.4, dash="3,3"))
    f.append(text(wr + 8, ymax + 4, "max", size=12, color=POS, anchor="start", bold=True))
    f.append(text(wr + 8, ymin + 4, "min", size=12, color=POS, anchor="start", bold=True))

    # подвійна стрілка розмаху
    arrx = wr + 60
    f.append(line(arrx, ymax, arrx, ymin, color=POS, sw=2))
    f.append(line(arrx - 5, ymax, arrx + 5, ymax, color=POS, sw=2))
    f.append(line(arrx - 5, ymin, arrx + 5, ymin, color=POS, sw=2))
    f.append(text(arrx + 12, (ymax + ymin) / 2 - 4, "розмах", size=12, color=POS, anchor="start", bold=True))
    f.append(text(arrx + 12, (ymax + ymin) / 2 + 12, "= гучність", size=12, color=POS, anchor="start"))

    render(os.path.join(IMG, 'envelope.svg'), W, H, *f)


if __name__ == "__main__":
    fig_block()
    fig_schematic()
    fig_wiring()
    fig_waveform()
    fig_debounce()
    fig_envelope()
    print("OK: figures written to", IMG)
