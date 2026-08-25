# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «MEMS».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Імена файлів — slug-only, без номерів (AUTHORING §2/§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── scale: наскільки воно мале (рухомий шар проти волосини) ──────────────────
# Ідея: рухома деталь MEMS — мікрометри, у десятки разів тонша за волосину.
# Показуємо лінійку масштабу: волосина (~70 мкм) поряд із рухомим шаром (~2 мкм).
def fig_scale():
    W, H = 760, 360
    parts = []

    base = 250
    left = 90

    # волосина — товстий стовпчик
    hair_w = 210
    parts.append(rect(left, base - 70, hair_w, 70, fill="#e8d9c0", stroke="#9c7a45", sw=2, rx=4))
    parts.append(text(left + hair_w / 2, base - 70 - 12, "людська волосина", size=14, bold=True, color="#9c7a45"))
    parts.append(text(left + hair_w / 2, base - 70 / 2 + 5, "≈ 70 мкм", size=14, color=INK))

    # рухомий шар MEMS — тонесенька смужка
    mx = left + hair_w + 120
    mems_w = 210
    parts.append(rect(mx, base - 6, mems_w, 6, fill="#cfe0f5", stroke=NEG, sw=2, rx=2))
    parts.append(arrow(mx + mems_w / 2, base - 60, mx + mems_w / 2, base - 10, color=NEG, sw=1.8))
    parts.append(text(mx + mems_w / 2, base - 70, "рухомий шар MEMS", size=14, bold=True, color=NEG))
    parts.append(text(mx + mems_w / 2, base - 88, "лічені мкм (≈ 2)", size=13, color=INK))

    # спільна підкладка-«земля» під обома
    parts.append(line(left - 20, base, mx + mems_w + 20, base, color=MUTED, sw=1.4))

    # висновок
    box, bw, bh = textbox(W / 2, H - 44,
                          "у десятки разів тонше за волосину — і це справжня машина, з вантажем і пружинами",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/scale.svg", W, H, *parts,
           title="Наскільки мале: рухома деталь MEMS проти волосини")


# ── micromachining: три кроки поверхневої мікрообробки ───────────────────────
# Жертовний шар: (1) нанести, (2) сформувати структуру згори, (3) розчинити —
# і деталь звисає вільно. Три панелі зліва направо.
def fig_micromachining():
    W, H = 900, 360
    parts = []

    pw = 250                      # ширина панелі
    gap = (W - 3 * pw) / 4
    top = 70
    floor = 250

    def substrate(x):
        return rect(x, floor, pw, 36, fill="#d7dde3", stroke=INK, sw=1.8, rx=3)

    # (1) нанесли жертовний шар
    x = gap
    parts.append(substrate(x))
    parts.append(rect(x + 30, floor - 26, pw - 60, 26, fill="#fde9c8", stroke="#c98a1e", sw=1.8, rx=2))
    parts.append(text(x + pw / 2, floor - 26 - 10, "жертовний шар", size=12, color="#c98a1e"))
    parts.append(text(x + pw / 2, top, "1. нанести", size=14, bold=True))
    parts.append(text(x + pw / 2, floor + 58, "підкладка", size=11, color=MUTED))

    # (2) структурний шар згори, якому надали форми (вантаж + балки)
    x = gap * 2 + pw
    parts.append(substrate(x))
    parts.append(rect(x + 30, floor - 26, pw - 60, 26, fill="#fde9c8", stroke="#c98a1e", sw=1.8, rx=2))
    # вантаж із пружинками поверх жертовного
    bx, bw = x + 60, pw - 120
    parts.append(rect(bx, floor - 26 - 22, bw, 22, fill="#cfe0f5", stroke=NEG, sw=2, rx=3))
    parts.append(text(x + pw / 2, floor - 26 - 22 - 8, "структурний шар", size=12, color=NEG))
    parts.append(text(x + pw / 2, top, "2. сформувати", size=14, bold=True))

    # (3) розчинили жертовний — структура звисає на якорях
    x = gap * 3 + pw * 2
    parts.append(substrate(x))
    bx = x + 60
    # два якорі по краях
    parts.append(rect(bx - 14, floor - 26, 14, 26, fill="#cfe0f5", stroke=NEG, sw=1.6, rx=2))
    parts.append(rect(bx + bw, floor - 26, 14, 26, fill="#cfe0f5", stroke=NEG, sw=1.6, rx=2))
    # вантаж висить над зазором
    parts.append(rect(bx, floor - 26 - 22, bw, 22, fill="#cfe0f5", stroke=NEG, sw=2, rx=3))
    parts.append(line(bx, floor - 14, bx + bw, floor - 14, color=MUTED, sw=1.0, dash="3,4"))
    parts.append(text(x + pw / 2, floor - 26 - 22 - 8, "звисає вільно", size=12, bold=True, color=FIELD))
    parts.append(text(x + pw / 2, top, "3. розчинити", size=14, bold=True))

    # стрілки між панелями
    parts.append(arrow(gap + pw + 6, floor - 14, gap * 2 + pw - 6, floor - 14, color=INK, sw=1.8))
    parts.append(arrow(gap * 2 + 2 * pw + 6, floor - 14, gap * 3 + 2 * pw - 6, floor - 14, color=INK, sw=1.8))

    box, bw2, bh2 = textbox(W / 2, H - 40,
                            "та сама літографія й травлення, що й мікросхеми → тисячі давачів на одній пластині",
                            size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/micromachining.svg", W, H, *parts,
           title="Поверхнева мікрообробка: жертовний шар розчиняють — деталь оживає")


# ── proof-mass: інерційна маса на пружинках ─────────────────────────────────
# Серце давача руху: вантаж на двох пружинах; сила зсуває, пружина повертає,
# зсув ∝ прискоренню (F = ma).
def fig_proof_mass():
    W, H = 760, 320
    parts = []

    cy = 150
    mx, mw, mh = W / 2 - 70, 140, 64
    # якорі
    parts.append(rect(150, cy - 16, 16, 32, fill="#d7dde3", stroke=INK, sw=2, rx=2))
    parts.append(rect(W - 166, cy - 16, 16, 32, fill="#d7dde3", stroke=INK, sw=2, rx=2))

    # пружини (зигзаги) — зелені
    def spring(x1, x2, y):
        n = 6
        step = (x2 - x1) / n
        pts = ["%.1f,%.1f" % (x1, y)]
        for i in range(1, n):
            yy = y - 9 if i % 2 else y + 9
            pts.append("%.1f,%.1f" % (x1 + i * step, yy))
        pts.append("%.1f,%.1f" % (x2, y))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
                'stroke-linejoin="round"/>' % (" ".join(pts), FIELD))

    parts.append(spring(166, mx, cy))
    parts.append(spring(mx + mw, W - 166, cy))
    parts.append(text(166 + (mx - 166) / 2, cy - 16, "пружина", size=11, italic=True, color=FIELD))
    parts.append(text(mx + mw + (W - 166 - mx - mw) / 2, cy - 16, "пружина", size=11, italic=True, color=FIELD))

    # вантаж
    parts.append(rect(mx, cy - mh / 2, mw, mh, fill="#cfe0f5", stroke=NEG, sw=2, rx=4))
    parts.append(text(mx + mw / 2, cy + 5, "інерційна маса", size=13, bold=True, color=NEG))

    # прискорення → сила
    parts.append(arrow(mx + mw / 2, cy + 70, mx + mw / 2 + 90, cy + 70, color=POS, sw=2.4))
    parts.append(text(mx + mw / 2 + 96, cy + 74, "прискорення → сила", size=12, bold=True, color=POS, anchor="start"))

    # зсув ∝ силі
    parts.append(arrow(mx + mw / 2, cy - 56, mx + mw / 2 + 40, cy - 56, color=MUTED, sw=1.5))
    parts.append(text(mx + mw / 2 + 46, cy - 53, "зсув ∝ силі", size=11, italic=True, color=MUTED, anchor="start"))

    box, bw, bh = textbox(W / 2, H - 34,
                          "F = ma, зрівноважена пружиною → зсув маси прямо пропорційний прискоренню",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/proof-mass.svg", W, H, *parts,
           title="Серце давача руху: інерційна маса на пружинках")


# ── comb: ємнісні гребінці (диференційне знімання) ──────────────────────────
# Зсув маси зближує пальці з одного боку й віддаляє з другого; ємність росте з
# одного боку, падає з другого — різницю читає електроніка.
def fig_comb():
    W, H = 820, 380
    parts = []

    cy = 180
    # центральна рухома планка з пальцями вгору й униз
    beam_x, beam_w = W / 2 - 150, 300
    parts.append(rect(beam_x, cy - 9, beam_w, 18, fill="#cfe0f5", stroke=NEG, sw=2, rx=3))
    parts.append(text(beam_x + beam_w / 2, cy - 16, "рухома маса", size=12, bold=True, color=NEG))

    finger_len = 54
    n = 6
    step = beam_w / (n + 1)
    # рухомі пальці (сині) — трохи зсунуті праворуч (показуємо зсув)
    shift = 6
    for i in range(1, n + 1):
        fx = beam_x + i * step + shift
        parts.append(line(fx, cy - 9, fx, cy - 9 - finger_len, color=NEG, sw=3))   # вгору
        parts.append(line(fx, cy + 9, fx, cy + 9 + finger_len, color=NEG, sw=3))   # вниз

    # нерухомі пальці (сірі) — стоять симетрично між рухомими
    for i in range(1, n + 1):
        fx = beam_x + i * step - step / 2
        parts.append(line(fx, cy - 9 - 14, fx, cy - 9 - 14 - finger_len, color="#8a8a8a", sw=3))
        parts.append(line(fx, cy + 9 + 14, fx, cy + 9 + 14 + finger_len, color="#8a8a8a", sw=3))

    parts.append(text(beam_x - 14, cy - 9 - finger_len - 6, "нерухомі", size=11, italic=True, color="#8a8a8a", anchor="end"))

    # боки: зазор меншає / більшає → ємність ↑ / ↓
    parts.append(text(W / 2, cy - 9 - finger_len - 30, "зазор ↓  →  ємність ↑", size=12, bold=True, color=POS))
    parts.append(text(W / 2, cy + 9 + finger_len + 36, "зазор ↑  →  ємність ↓", size=12, bold=True, color=NEG))

    # кожна пара пальців = конденсатор
    parts.append(text(beam_x + beam_w + 16, cy, "кожна пара\nпальців —\nконденсатор", size=11, color=MUTED, anchor="start"))
    # багаторядково через mtext
    parts.pop()  # прибрати однорядковий text, дати mtext
    parts.append(mtext(beam_x + beam_w + 16, cy - 10, "кожна пара\nпальців —\nконденсатор", size=11, color=MUTED, anchor="start"))

    box, bw, bh = textbox(W / 2, H - 34,
                          "електроніка читає РІЗНИЦЮ ємностей (диференційно) → нанометри зсуву стають напругою",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/comb.svg", W, H, *parts,
           title="Ємнісні гребінці: зсув маси міняє ємність між пальцями")


# ── platform: одна технологія → родина давачів ──────────────────────────────
# Той самий фундамент (вантаж + ємнісне знімання + електроніка) дає різні давачі.
def fig_platform():
    W, H = 920, 380
    parts = []

    # фундамент
    fx, fw = W / 2 - 300, 600
    fy = 70
    parts.append(rect(fx, fy, fw, 52, fill="#eef2f7", stroke=INK, sw=2, rx=10))
    parts.append(mtext(W / 2, fy + 22,
                       "одна мікромеханіка: вантаж на пружинках + ємнісне знімання + електроніка на чипі",
                       size=12.5, bold=True, color=INK))

    # чотири нащадки
    kids = [
        ("акселерометр", "маса зсувається\nвід прискорення", POS, "#fdecea"),
        ("гіроскоп", "вібрівна маса\nвідхиляється (Коріоліс)", NEG, "#eaf0fd"),
        ("давач тиску", "прогин\nмембрани", FIELD, "#e9f7ef"),
        ("мікрофон", "звукові коливання\nмембрани", "#8a5a1e", "#fbeedd"),
    ]
    kw, kh = 190, 96
    gap = (fw - 4 * kw) / 3 if len(kids) > 1 else 0
    ky = 230
    for i, (name, what, col, fill) in enumerate(kids):
        x = fx + i * (kw + gap)
        parts.append(rect(x, ky, kw, kh, fill=fill, stroke=col, sw=2, rx=8))
        parts.append(text(x + kw / 2, ky + 26, name, size=13.5, bold=True, color=col))
        parts.append(mtext(x + kw / 2, ky + 50, what, size=11.5, color=INK))
        # стрілка від фундаменту
        parts.append(arrow(x + kw / 2, fy + 56, x + kw / 2, ky - 4, color=MUTED, sw=1.5))

    box, bw, bh = textbox(W / 2, H - 28,
                          "один технологічний фундамент → десятки давачів, і всі копійчані з міркувань масштабу",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/platform.svg", W, H, *parts,
           title="Одна платформа MEMS — ціла родина давачів")


# ── strengths: сила й межі MEMS (дві сторони крихітності) ────────────────────
def fig_strengths():
    W, H = 880, 360
    parts = []

    colw = 360
    lx = W / 2 - colw / 2 - 20      # центр лівої
    rx = W / 2 + colw / 2 + 20      # центр правої
    top = 70

    parts.append(text(lx, top, "СИЛА", size=16, bold=True, color=FIELD))
    parts.append(fitbox(lx - colw / 2, top + 16, colw, 150,
                        "малі  ·  копійчані (пакетне виробництво)\n"
                        "інтегровані з електронікою  ·  маловитратні\n\n"
                        "→ звідси їхня всюдисущість",
                        size=13, fill="#e9f7ef", stroke=FIELD, sw=2))

    parts.append(text(rx, top, "МЕЖІ", size=16, bold=True, color=POS))
    parts.append(fitbox(rx - colw / 2, top + 16, colw, 150,
                        "слабкий сигнал → шум (теплове тремтіння)\n"
                        "дрейф від температури (кремній розширюється)\n"
                        "зсув нуля у кожного свій (виробничий розкид)\n"
                        "крихкість до ударів",
                        size=13, fill="#fdecea", stroke=POS, sw=2))

    box, bw, bh = textbox(W / 2, H - 36,
                          "та сама крихітність дає і дешевизну, і шум, дрейф, крихкість → давачі доводиться поєднувати",
                          size=13, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/strengths.svg", W, H, *parts,
           title="Дві сторони мікромеханіки: сила й межі MEMS")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки hist-mems-airbag.md (історія: як подушка здешевила MEMS)
# ════════════════════════════════════════════════════════════════════════════

# ── silicon-machining: кремній як механічний матеріал ───────────────────────
# Тими ж методами, що й мікросхеми, у кремнії виточують не схеми, а рухомі деталі.
def fig_silicon_machining():
    W, H = 820, 340
    parts = []

    # пластина-вхід
    wx, wy = 80, 150
    parts.append(rect(wx, wy - 40, 150, 80, fill="#d7dde3", stroke=INK, sw=2, rx=6))
    parts.append(text(wx + 75, wy + 5, "кремнієва\nпластина", size=12, color=INK))
    parts.pop()
    parts.append(mtext(wx + 75, wy - 5, "кремнієва\nпластина", size=12, color=INK))

    # «машина» літо+травлення
    parts.append(arrow(wx + 150 + 6, wy, wx + 150 + 90, wy, color=INK, sw=1.8))
    bx = wx + 150 + 96
    parts.append(fitbox(bx, wy - 36, 200, 72,
                        "фотолітографія\n+ травлення", size=13, fill=FILL, stroke=LINE, sw=1.8, bold=True))

    # два виходи: схеми (звичайно) і рухомі деталі (MEMS)
    ox = bx + 200 + 96
    parts.append(arrow(bx + 200 + 6, wy - 18, ox - 6, wy - 60, color=MUTED, sw=1.6))
    parts.append(arrow(bx + 200 + 6, wy + 18, ox - 6, wy + 60, color=FIELD, sw=2))

    parts.append(fitbox(ox, wy - 92, 200, 56, "транзистори, схеми\n(звичайний чип)",
                        size=12, fill="#eef2f7", stroke=MUTED, sw=1.6))
    parts.append(fitbox(ox, wy + 36, 200, 56, "балки, пружини, вантажі\n(рухомі деталі — MEMS)",
                        size=12, fill="#e9f7ef", stroke=FIELD, sw=2, bold=True))

    box, bw, bh = textbox(W / 2, H - 28,
                          "кремній — не лише для схем, а й чудовий механічний матеріал",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/silicon-machining.svg", W, H, *parts,
           title="Кремній як механічний матеріал: ті самі методи — рухомі деталі")


# ── airbag: вбивча задача — давач удару ─────────────────────────────────────
# При ударі різке від'ємне прискорення; давач ловить сплеск і надуває подушку.
def fig_airbag():
    W, H = 860, 360
    parts = []

    # графік прискорення в часі: спокій → різкий сплеск
    ox, oy = 90, 200
    axw = 360
    parts.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    parts.append(text(ox + axw + 6, oy + 5, "час", size=12, anchor="start", color=INK))
    parts.append(arrow(ox, oy, ox, oy - 130, color=INK, sw=1.6))
    parts.append(text(ox - 8, oy - 130, "|a|", size=12, anchor="end", color=INK))

    # лінія: рівно, потім гострий пік
    pk = ox + axw * 0.55
    parts.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                 'fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>'
                 % (ox + 6, oy - 6, pk - 40, oy - 6, pk, oy - 116, pk + 30, oy - 8, ox + axw - 6, oy - 6, POS))
    parts.append(text(pk, oy - 124, "удар: різкий сплеск (десятки g)", size=12, bold=True, color=POS))

    # стрілка → подушка
    parts.append(arrow(ox + axw + 30, oy - 40, ox + axw + 110, oy - 40, color=INK, sw=2))
    parts.append(fitbox(ox + axw + 116, oy - 70, 180, 60,
                        "давач ловить сплеск\n→ надути подушку", size=12.5,
                        fill="#fdecea", stroke=POS, sw=2, bold=True))

    box, bw, bh = textbox(W / 2, H - 30,
                          "мільйони машин × дві подушки = гарантований ринок на десятки мільйонів давачів щороку",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/airbag.svg", W, H, *parts,
           title="«Вбивча задача»: давач удару для подушки безпеки")


# ── adxl50: машина й мозок на одному чипі ───────────────────────────────────
def fig_adxl50():
    W, H = 820, 360
    parts = []

    # контур чипа
    cx, cy = W / 2, 180
    cw, ch = 520, 200
    parts.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill="#eef2f7", stroke=INK, sw=2, rx=12))
    parts.append(text(cx, cy - ch / 2 - 12, "один кремнієвий кристал (ADXL50)", size=13, bold=True, color=MUTED))

    # ліворуч — механіка (вантаж + гребінці)
    mxL = cx - cw / 2 + 40
    parts.append(rect(mxL, cy - 30, 150, 60, fill="#cfe0f5", stroke=NEG, sw=2, rx=4))
    parts.append(text(mxL + 75, cy + 4, "вантаж-проба", size=12, bold=True, color=NEG))
    # пальці-гребінці
    for i in range(5):
        fx = mxL + 18 + i * 30
        parts.append(line(fx, cy - 30, fx, cy - 48, color=NEG, sw=2.4))
        parts.append(line(fx + 15, cy + 30, fx + 15, cy + 48, color="#8a8a8a", sw=2.4))
    parts.append(text(mxL + 75, cy - 58, "ємнісні гребінці", size=11, italic=True, color=MUTED))

    # праворуч — електроніка
    exR = cx + cw / 2 - 40 - 180
    parts.append(fitbox(exR, cy - 40, 180, 80,
                        "електроніка\nчитає ємність\n(+ самотест)", size=12.5,
                        fill="#e9f7ef", stroke=FIELD, sw=2, bold=True))

    # стрілка механіка → електроніка
    parts.append(arrow(mxL + 150 + 6, cy, exR - 6, cy, color=INK, sw=1.8))
    parts.append(text((mxL + 150 + exR) / 2, cy - 10, "зсув → Δємність", size=11, italic=True, color=INK))

    box, bw, bh = textbox(W / 2, H - 30,
                          "уперше механіка й електроніка на ОДНОМУ чипі — менший за макове зерно, ≈ 5 $",
                          size=13, pad=12, fill=FILL)
    parts.append(box)

    render("img/adxl50.svg", W, H, *parts,
           title="ADXL50: вантаж, ємнісні гребінці й електроніка на одному чипі")


# ── scaling-cycle: доброчесне коло масштабу ─────────────────────────────────
# Ринок подушок → об'єми → падіння ціни → давач їде всюди → ще більший об'єм.
def fig_scaling_cycle():
    W, H = 820, 360
    parts = []

    stages = [
        "обов'язкові\nподушки безпеки",
        "масовий\nринок (об'єми)",
        "падіння ціни\nй розміру",
        "давач їде\nвсюди",
    ]
    bw, bh = 170, 70
    cyc = 170
    xs = [70, 70 + 190, 70 + 380, 70 + 570]
    for i, (x, s) in enumerate(zip(xs, stages)):
        col = FIELD if i == len(stages) - 1 else INK
        fill = "#e9f7ef" if i == len(stages) - 1 else FILL
        parts.append(fitbox(x, cyc - bh / 2, bw, bh, s, size=12.5, fill=fill, stroke=col, sw=2,
                            bold=(i == len(stages) - 1)))
        if i < len(stages) - 1:
            parts.append(arrow(x + bw + 4, cyc, xs[i + 1] - 4, cyc, color=INK, sw=1.8))

    # зворотна дуга «ще більший об'єм»
    parts.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2" stroke-dasharray="6,5" marker-end="url(#arrow)"/>'
                 % (xs[3] + bw / 2, cyc + bh / 2, xs[3] + bw / 2, cyc + 120,
                    xs[1] + bw / 2, cyc + 120, xs[1] + bw / 2, cyc + bh / 2 + 4, MUTED))
    parts.append(text((xs[1] + xs[3]) / 2 + bw / 2, cyc + 116, "ще дешевше → ще більший об'єм",
                      size=12, italic=True, color=MUTED))

    box, bw2, bh2 = textbox(W / 2, H - 28,
                            "не телефон здешевив акселерометр — здешевлений акселерометр зробив можливими телефони",
                            size=12.5, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/scaling-cycle.svg", W, H, *parts,
           title="Доброчесне коло масштабу: ринок → об'єм → дешевизна")


# ── everywhere: з машини — у всю споживчу електроніку ───────────────────────
def fig_everywhere():
    W, H = 880, 340
    parts = []

    # джерело
    sx, sy = 90, 160
    parts.append(fitbox(sx, sy - 45, 180, 90,
                        "здешевлений\nMEMS-давач\n(з авто)", size=13,
                        fill="#e9f7ef", stroke=FIELD, sw=2, bold=True))

    dests = ["ігрові пульти\n(Wii, 2006)", "смартфони\n(iPhone, 2007)",
             "дрони", "фітнес-браслети", "стабілізатори камер"]
    dx = sx + 180 + 110
    dw, dh = 200, 46
    n = len(dests)
    span = 250
    y0 = sy - span / 2
    for i, d in enumerate(dests):
        y = y0 + i * (span / (n - 1))
        parts.append(fitbox(dx, y - dh / 2, dw, dh, d, size=12, fill=FILL, stroke=LINE, sw=1.5))
        parts.append(arrow(sx + 180 + 6, sy, dx - 6, y, color=MUTED, sw=1.4))

    box, bw, bh = textbox(W / 2, H - 24,
                          "до акселерометра додали MEMS-гіроскоп і магнітометр → дев'ятиосьовий IMU за пару доларів",
                          size=12.5, pad=12, fill=FILL)
    parts.append(box)

    render("img/everywhere.svg", W, H, *parts,
           title="З машини — у всю споживчу електроніку")


# ── lesson: винахід → вбивча задача → всюдисущість ──────────────────────────
def fig_lesson():
    W, H = 860, 300
    parts = []

    oy = 150
    ox, axw = 80, 700
    parts.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))

    marks = [
        (0.04, "винахід", "кремнієва\nмікромеханіка, 1982", MUTED),
        (0.42, "вбивча задача", "подушки безпеки,\n1990-ті", POS),
        (0.86, "всюдисущість", "телефони, дрони,\nігри, 2000-ні", FIELD),
    ]
    for frac, head, sub, col in marks:
        x = ox + axw * frac
        parts.append(circle(x, oy, 7, fill=col, stroke=col, sw=1))
        parts.append(text(x, oy - 40, head, size=14, bold=True, color=col))
        parts.append(mtext(x, oy + 30, sub, size=11, color=INK))

    box, bw, bh = textbox(W / 2, H - 30,
                          "винахід запалює іскру, але вогонь розгоряється лише там, де є чому горіти — масова потреба",
                          size=13, pad=12, fill=FILL, bold=True)
    parts.append(box)

    render("img/lesson.svg", W, H, *parts,
           title="Як технологія стає масовою: винахід → ринок → всюдисущість")


if __name__ == "__main__":
    # фігури статті mems.md
    fig_scale()
    fig_micromachining()
    fig_proof_mass()
    fig_comb()
    fig_platform()
    fig_strengths()
    # фігури вставки hist-mems-airbag.md
    fig_silicon_machining()
    fig_airbag()
    fig_adxl50()
    fig_scaling_cycle()
    fig_everywhere()
    fig_lesson()
    print("OK: scale, micromachining, proof-mass, comb, platform, strengths, "
          "silicon-machining, airbag, adxl50, scaling-cycle, everywhere, lesson")
