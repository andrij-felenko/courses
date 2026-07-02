# -*- coding: utf-8 -*-
"""Фігури до теми «КІХ проти БІХ».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math, random

# Локальні відтінки понад палітру svgkit
KIH = "#27ae60"      # КІХ — безпека, зелене
BIH = "#c0392b"      # БІХ — гострота/ризик, гаряче
GOLD = "#b9770e"     # затримка / тепле акцентування


# ── 1. Двобій критеріями: дзеркальна таблиця ─────────────────────────────────
def fig_comparison():
    W, H = 720, 430
    f = [text(W / 2, 26, "КІХ і БІХ: дзеркало переваг", size=15, bold=True)]

    cols = [("КІХ", 430, KIH), ("БІХ", 600, BIH)]
    for name, cx, col in cols:
        f.append(rect(cx - 70, 44, 140, 36, fill=FILL, stroke=col, sw=1.8))
        f.append(text(cx, 67, name, size=13, color=col, bold=True))

    rows = [
        ("Стійкість гарантована",   "++", "x"),
        ("Лінійна фаза (форма ціла)", "++", "x"),
        ("Гострий зріз дешево",      "x",  "++"),
        ("Малі обчислення",          "~",  "++"),
        ("Мала пам'ять",             "~",  "++"),
        ("Мала затримка",            "x",  "++"),
        ("Простота й передбачуваність", "++", "~"),
        ("Копіює аналоговий прототип", "x", "++"),
    ]
    glyph = {"++": ("сильно", KIH), "x": ("слабко", BIH), "~": ("так собі", GOLD)}

    y = 86
    for i, (label, a, b) in enumerate(rows):
        if i % 2 == 0:
            f.append(rect(16, y, 688, 36, fill="#f6f6f8", stroke="none", sw=0, rx=4))
        f.append(text(28, y + 24, label, size=12, anchor="start"))
        for v, cx in ((a, 430), (b, 600)):
            txt, col = glyph[v]
            f.append(text(cx, y + 24, txt, size=12, color=col, bold=True))
        y += 40

    f.append(text(W / 2, 418,
                  "усе, у чому сильний один, — слабке місце другого",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "comparison.svg"), W, H, *f)


# ── 2. Дерево рішення: два питання вирішують усе ──────────────────────────────
def fig_decision_tree():
    W, H = 760, 430
    f = [text(W / 2, 26, "Два питання вирішують вибір", size=15, bold=True)]

    # питання 1
    f.append(rect(40, 70, 230, 60, fill=FILL, stroke=INK, sw=2))
    f.append(text(155, 95, "Форма сигналу важлива?", size=12, bold=True))
    f.append(text(155, 114, "(фаза, фронти, точна хвиля)", size=9.5, color=MUTED, italic=True))

    # так → КІХ
    f.append(arrow(155, 130, 155, 178, color=KIH, sw=1.8))
    f.append(text(168, 158, "так", size=10.5, color=KIH, anchor="start", italic=True))
    f.append(rect(40, 180, 230, 58, fill=FILL, stroke=KIH, sw=1.8))
    f.append(text(155, 205, "КІХ", size=14, color=KIH, bold=True))
    f.append(text(155, 224, "лінійна фаза не псує форму", size=9.5, color=MUTED, italic=True))

    # ні → питання 2
    f.append(arrow(270, 100, 470, 100, color=MUTED, sw=1.8))
    f.append(text(360, 88, "ні", size=10.5, color=MUTED, anchor="middle", italic=True))
    f.append(rect(470, 70, 250, 60, fill=FILL, stroke=INK, sw=2))
    f.append(text(595, 92, "Гострий зріз", size=12, bold=True))
    f.append(text(595, 110, "за тісних ресурсів?", size=12, bold=True))

    # питання 2 → так → БІХ
    f.append(arrow(595, 130, 595, 178, color=BIH, sw=1.8))
    f.append(text(608, 158, "так", size=10.5, color=BIH, anchor="start", italic=True))
    f.append(rect(480, 180, 230, 58, fill=FILL, stroke=BIH, sw=1.8))
    f.append(text(595, 205, "БІХ", size=14, color=BIH, bold=True))
    f.append(text(595, 224, "крутість за кілька коефіцієнтів", size=9.5, color=MUTED, italic=True))

    # питання 2 → ні → байдуже
    f.append(arrow(595, 130, 595, 130, color=MUTED, sw=0.1))
    f.append(line(720, 100, 738, 100, color=MUTED, sw=1.6))
    f.append(text(729, 88, "ні", size=9, color=MUTED, italic=True))

    # нижній ряд: стабільність + проста задача
    f.append(rect(40, 300, 330, 60, fill=BG, stroke=KIH, sw=1.5))
    f.append(text(205, 324, "Критична безпека / стабільність?", size=11.5, bold=True))
    f.append(text(205, 344, "→ теж КІХ (не вибухне за визначенням)", size=10.5, color=KIH, italic=True))

    f.append(rect(400, 300, 320, 60, fill=BG, stroke=MUTED, sw=1.5))
    f.append(text(560, 324, "Жодне питання не «гостре»?", size=11.5, bold=True))
    f.append(text(560, 344, "→ найдешевше й найпростіше (EMA)", size=10.5, color=MUTED, italic=True))

    f.append(text(W / 2, 410,
                  "форма головніша за все: не можна псувати — БІХ відпадає одразу",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "decision-tree.svg"), W, H, *f)


# ── 3. Готові рецепти: задача → сімейство ─────────────────────────────────────
def fig_recipes():
    W, H = 820, 260
    f = [text(W / 2, 26, "Готові рецепти: задача підказує сімейство", size=15, bold=True)]

    cards = [
        (["ЕКГ,", "форма хвилі"], "КІХ", "діагноз — за QRS", KIH),
        (["Notch 50 Гц,", "дешевий чип"], "БІХ-біквад", "гостро за копійки", BIH),
        (["Просте", "згладжування"], "EMA", "найдешевший БІХ", GOLD),
        (["Безпека", "в керуванні"], "КІХ", "стійкість гарантовано", KIH),
        (["Копія", "аналогового"], "БІХ", "Баттерворт тощо", BIH),
    ]
    cw = 152
    x = 16
    for task, fam, note, col in cards:
        f.append(rect(x, 52, cw, 176, fill=FILL, stroke=col, sw=1.6))
        f.append(mtext(x + cw / 2, 76, task, size=12, color=INK, bold=True))
        f.append(line(x + 14, 108, x + cw - 14, 108, color="#dddddd", sw=1.2))
        f.append(text(x + cw / 2, 150, fam, size=14, color=col, bold=True))
        f.append(text(x + cw / 2, 204, note, size=9.5, color=MUTED, italic=True))
        x += cw + 8

    f.append(text(W / 2, 252,
                  "той самий тип задачі, протилежні рішення — бо протилежні пріоритети",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "recipes.svg"), W, H, *f)


# ── 4. Старі знайомі: ковзне середнє — КІХ, EMA — БІХ ─────────────────────────
def fig_already_know():
    W, H = 740, 300
    f = [text(W / 2, 26, "Ви вже знаєте обидва сімейства", size=15, bold=True)]

    # ліва панель: ковзне середнє = КІХ
    f.append(rect(30, 50, 330, 210, fill="#f3faf5", stroke=KIH, sw=1.8))
    f.append(text(195, 76, "Ковзне середнє = КІХ", size=13, color=KIH, bold=True))
    f.append(text(195, 100, "скінченна пам'ять · рівні відводи", size=10.5, color=MUTED, italic=True))
    f.append(text(195, 118, "лінійна фаза · завжди стійкий", size=10.5, color=MUTED, italic=True))
    # вікно зі скінченних відводів
    for i in range(5):
        bx = 70 + i * 46
        f.append(rect(bx, 150, 38, 60, fill="#d8f0e0", stroke=KIH, sw=1.4, rx=3))
        f.append(text(bx + 19, 186, "1/N", size=11, color=KIH, bold=True))
    f.append(text(195, 238, "пам'ять обривається рівно — скінченна", size=10, color=KIH, italic=True))

    # права панель: EMA = БІХ
    f.append(rect(380, 50, 330, 210, fill="#fdf2f1", stroke=BIH, sw=1.8))
    f.append(text(545, 76, "EMA = БІХ", size=13, color=BIH, bold=True))
    f.append(text(545, 100, "зворотний зв'язок · один коефіцієнт α", size=10.5, color=MUTED, italic=True))
    f.append(text(545, 118, "нескінченний хвіст · гранична ощадливість", size=10.5, color=MUTED, italic=True))
    # експоненційно спадний хвіст
    base = 210
    x0 = 410
    for i in range(11):
        h = 60 * (0.72 ** i)
        bx = x0 + i * 26
        f.append(rect(bx, base - h, 20, h, fill="#f6d4d1", stroke=BIH, sw=1.2, rx=2))
    f.append(text(545, 238, "хвіст згасає, але вічно — нескінченна", size=10, color=BIH, italic=True))

    f.append(text(W / 2, 286,
                  "прості часові фільтри — окремі випадки двох великих сімейств",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "already-know.svg"), W, H, *f)


# ── 5. Терези: фундаментальний розмін ─────────────────────────────────────────
def fig_tradeoff():
    W, H = 720, 320
    f = [text(W / 2, 26, "Безплатного фільтра не буває", size=15, bold=True)]

    fx, fy = W / 2, 110          # точка опори
    beam_w = 250
    tilt = 16                     # нахил коромисла

    # стійка й опора
    f.append(line(fx, fy, fx, 250, color=INK, sw=3))
    f.append('<polygon points="%.0f,250 %.0f,250 %.0f,236 %.0f,236" fill="%s"/>'
             % (fx - 26, fx + 26, fx + 14, fx - 14, INK))
    # коромисло (нахилене вліво — обидва однаково вагомі, символічно врівноважене)
    lx, ly = fx - beam_w, fy + tilt
    rx, ry = fx + beam_w, fy - tilt
    f.append(line(lx, ly, rx, ry, color=INK, sw=3))

    # ліва шалька — КІХ
    f.append(line(lx, ly, lx, ly + 24, color=MUTED, sw=1.4))
    box, bw, bh = textbox(lx, ly + 64, "КІХ\nбезпека + форма\n(дорожчий)",
                          size=11.5, color=KIH, stroke=KIH, sw=1.8, fill="#f3faf5", bold=True)
    f.append(box)

    # права шалька — БІХ
    f.append(line(rx, ry, rx, ry + 24, color=MUTED, sw=1.4))
    box2, bw2, bh2 = textbox(rx, ry + 64, "БІХ\nгострота + ощадливість\n(ризик + фаза)",
                             size=11.5, color=BIH, stroke=BIH, sw=1.8, fill="#fdf2f1", bold=True)
    f.append(box2)

    f.append(text(W / 2, 300,
                  "схиляючи терези в один бік, ви відмовляєтесь від переваг другого",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "tradeoff.svg"), W, H, *f)


# ── 6. Тракт: кожна ланка — свій фільтр ───────────────────────────────────────
def fig_pipeline():
    W, H = 780, 250
    f = [text(W / 2, 26, "Вибір — для кожної ланки тракту окремо", size=15, bold=True)]

    stages = [
        ("медіана", "проти викидів", "нелінійна", GOLD),
        ("БІХ-notch 50 Гц", "гострий зріз мережі", "ефективність", BIH),
        ("КІХ-згладжування", "чиста форма", "лінійна фаза", KIH),
    ]
    x = 24
    for title_, note, tag, col in stages:
        f.append(rect(x, 84, 220, 80, fill=FILL, stroke=col, sw=1.8))
        f.append(text(x + 110, 112, title_, size=13, color=col, bold=True))
        f.append(text(x + 110, 132, note, size=10, color=MUTED, italic=True))
        f.append(text(x + 110, 152, tag, size=9.5, color=col, italic=True))
        x += 245
    f.append(arrow(244, 124, 268, 124, color=INK, sw=2))
    f.append(arrow(489, 124, 513, 124, color=INK, sw=2))

    f.append(text(W / 2, 200,
                  "не «один фільтр на все» — ланцюжок, де кожна ланка найкраща у своїй ролі",
                  size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 224,
                  "КІХ, БІХ і нелінійна медіана уживаються в одному тракті",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "pipeline.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЛЯ ДЕТАЛЬНОЇ ВЕРСІЇ (fir-vs-iir-d.md) — глибша механіка
# ════════════════════════════════════════════════════════════════════════════

# ── D1. Структура: КІХ — пряма сума; БІХ — сума + петля назад ─────────────────
def d_structure():
    W, H = 760, 340
    f = [text(W / 2, 26, "Звідки скінченність і нескінченність", size=15, bold=True)]

    # ліва панель — КІХ (без петлі)
    f.append(rect(24, 50, 350, 260, fill="#f3faf5", stroke=KIH, sw=1.8))
    f.append(text(199, 74, "КІХ — тільки вперед", size=13, color=KIH, bold=True))
    f.append(circle(70, 150, 14, fill=BG, stroke=INK, sw=1.6))
    f.append(text(70, 155, "x", size=12, bold=True))
    # ланцюг затримок
    for i, bx in enumerate((120, 180, 240)):
        f.append(rect(bx, 136, 30, 28, fill="#d8f0e0", stroke=KIH, sw=1.4, rx=3))
        f.append(text(bx + 15, 155, "z⁻¹", size=10, color=KIH))
    f.append(arrow(84, 150, 120, 150, color=INK, sw=1.5))
    f.append(arrow(150, 150, 180, 150, color=INK, sw=1.5))
    f.append(arrow(210, 150, 240, 150, color=INK, sw=1.5))
    # суматор
    f.append(circle(199, 235, 16, fill=BG, stroke=INK, sw=1.6))
    f.append(text(199, 241, "Σ", size=15, bold=True))
    for bx, y_tap in ((70, 164), (135, 164), (195, 164), (255, 164)):
        f.append(line(bx, y_tap, bx, 192, color=MUTED, sw=1.1, dash="3 3"))
        f.append(arrow(bx, 192, 199, 231, color=MUTED, sw=1.0))
    f.append(arrow(199, 251, 199, 285, color=INK, sw=1.6))
    f.append(text(199, 302, "y — сума скінченного вікна входів", size=9.5, color=KIH, italic=True))

    # права панель — БІХ (з петлею)
    f.append(rect(400, 50, 336, 260, fill="#fdf2f1", stroke=BIH, sw=1.8))
    f.append(text(568, 74, "БІХ — з петлею назад", size=13, color=BIH, bold=True))
    f.append(circle(440, 130, 14, fill=BG, stroke=INK, sw=1.6))
    f.append(text(440, 135, "x", size=12, bold=True))
    f.append(circle(568, 130, 16, fill=BG, stroke=INK, sw=1.6))
    f.append(text(568, 136, "Σ", size=15, bold=True))
    f.append(arrow(454, 130, 552, 130, color=INK, sw=1.6))
    f.append(arrow(584, 130, 690, 130, color=INK, sw=1.6))
    f.append(text(700, 134, "y", size=12, bold=True, color=BIH))
    # петля зворотного зв'язку
    f.append(line(660, 130, 660, 210, color=BIH, sw=1.8))
    f.append(rect(553, 196, 30, 28, fill="#f6d4d1", stroke=BIH, sw=1.4, rx=3))
    f.append(text(568, 215, "z⁻¹", size=10, color=BIH))
    f.append(line(660, 210, 583, 210, color=BIH, sw=1.8))
    f.append(line(553, 210, 500, 210, color=BIH, sw=1.8))
    f.append(line(500, 210, 500, 146, color=BIH, sw=1.8))
    f.append(arrow(500, 146, 553, 132, color=BIH, sw=1.8))
    f.append(text(568, 250, "вихід вертається на вхід суматора", size=9.5, color=BIH, italic=True))
    f.append(text(568, 272, "один імпульс живить себе — хвіст вічний", size=9.5, color=BIH, italic=True))

    f.append(text(W / 2, 330,
                  "немає петлі → пам'ять уривається; є петля → характеристика нескінченна",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "d-structure.svg"), W, H, *f)


# ── D2. Симетрія відводів → лінійна фаза (стала групова затримка) ─────────────
def d_symmetry_phase():
    W, H = 760, 360
    f = [text(W / 2, 26, "Симетрія відводів = лінійна фаза", size=15, bold=True)]

    # верх: симетрична імпульсна характеристика (стовпчики-дзеркало)
    cx = W / 2
    base = 150
    hs = [14, 26, 44, 66, 90, 66, 44, 26, 14]
    n = len(hs)
    bw = 26
    x0 = cx - (n * (bw + 8) - 8) / 2
    mid = (n - 1) / 2
    for i, h in enumerate(hs):
        bx = x0 + i * (bw + 8)
        col = KIH if i != mid else GOLD
        f.append(rect(bx, base - h, bw, h, fill="#d8f0e0" if i != mid else "#fdf1dd",
                      stroke=col, sw=1.4, rx=2))
        f.append(text(bx + bw / 2, base + 14, "b%d" % i, size=8.5, color=MUTED))
    f.append(line(x0 - 10, base, x0 + n * (bw + 8), base, color=INK, sw=1.4))
    # вісь симетрії
    f.append(line(cx, 44, cx, base + 4, color=GOLD, sw=1.4, dash="4 4"))
    f.append(text(cx, 40, "вісь симетрії (центр)", size=9.5, color=GOLD, italic=True))
    f.append(text(x0 - 4, base - 100, "b[k] = b[M−k]", size=11, color=KIH, bold=True, anchor="start"))

    # низ: наслідок — усі частоти зсунуті на однакову затримку M/2
    f.append(text(cx, 200, "наслідок: усі частоти запізнюються ОДНАКОВО", size=12, bold=True))
    f.append(line(120, 300, 640, 300, color=INK, sw=1.3))              # вісь часу
    f.append(text(640, 316, "час", size=9.5, color=MUTED, anchor="end"))
    # три синусоїди різної частоти, зсунуті на одну величину
    import math as _m
    def wave(y0c, freq, color, shift):
        pts = []
        for px in range(0, 260, 3):
            yy = y0c - 18 * _m.sin((px / 260.0) * freq * 2 * _m.pi - shift)
            pts.append("%.1f,%.1f" % (150 + px, yy))
        return '<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (" ".join(pts), color)
    f.append(wave(250, 2, KIH, 0))
    f.append(wave(300, 4, NEG, 0))
    f.append(wave(350, 6, BIH, 0))
    # маркер спільної затримки M/2
    f.append(line(150, 232, 150, 366, color=MUTED, sw=1.1, dash="3 3"))
    f.append(line(196, 232, 196, 360, color=GOLD, sw=1.6, dash="5 3"))
    f.append(text(430, 270, "усі зсунуті рівно на M/2 відліків", size=10, color=GOLD, italic=True, anchor="start"))
    f.append(text(430, 330, "→ форма хвилі ціла, лише запізнилась", size=10, color=MUTED, italic=True, anchor="start"))
    render(os.path.join(IMG, "d-symmetry-phase.svg"), W, H, *f)


# ── D3. Площина полюсів-нулів: полюс біля кола — гострий пік дешево ───────────
def d_pole_zero():
    W, H = 760, 360
    f = [text(W / 2, 26, "Полюс біля кола: гострий пік за копійки", size=15, bold=True)]

    # ліва: z-площина з одиничним колом
    cx, cy, R = 210, 200, 120
    f.append(circle(cx, cy, R, fill=BG, stroke=INK, sw=1.6))
    f.append(line(cx - R - 20, cy, cx + R + 20, cy, color=MUTED, sw=1.0))
    f.append(line(cx, cy - R - 20, cx, cy + R + 20, color=MUTED, sw=1.0))
    f.append(text(cx + R + 24, cy + 4, "Re", size=9.5, color=MUTED, anchor="start"))
    f.append(text(cx + 6, cy - R - 22, "Im", size=9.5, color=MUTED, anchor="start"))
    f.append(text(cx + R + 4, cy + 18, "|z|=1", size=9, color=INK, italic=True, anchor="start"))
    # полюс близько до кола (× БІХ)
    ang = 1.05
    pr = R * 0.93
    px, py = cx + pr * math.cos(ang), cy - pr * math.sin(ang)
    f.append(line(px - 7, py - 7, px + 7, py + 7, color=BIH, sw=2.2))
    f.append(line(px - 7, py + 7, px + 7, py - 7, color=BIH, sw=2.2))
    f.append(text(px + 10, py - 6, "полюс ×", size=9.5, color=BIH, anchor="start", bold=True))
    # спряжений полюс
    px2, py2 = cx + pr * math.cos(ang), cy + pr * math.sin(ang)
    f.append(line(px2 - 7, py2 - 7, px2 + 7, py2 + 7, color=BIH, sw=2.2))
    f.append(line(px2 - 7, py2 + 7, px2 + 7, py2 - 7, color=BIH, sw=2.2))
    # нуль на колі (○ notch)
    zx, zy = cx + R * math.cos(0.7), cy - R * math.sin(0.7)
    f.append(circle(zx, zy, 7, fill=BG, stroke=NEG, sw=2.0))
    f.append(text(zx + 10, zy - 6, "нуль ○", size=9.5, color=NEG, anchor="start", bold=True))
    f.append(text(cx, cy + R + 40, "що ближче полюс до кола — тим гостріший пік", size=9.5, color=MUTED, italic=True))

    # права: спектр — гострий резонанс від полюса + провал від нуля
    gx, gy, gw, gh = 420, 90, 300, 210
    f.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=1.3))
    f.append(line(gx, gy, gx, gy + gh, color=INK, sw=1.3))
    f.append(text(gx + gw, gy + gh + 16, "частота", size=9.5, color=MUTED, anchor="end"))
    f.append(text(gx - 6, gy + 4, "|H|", size=9.5, color=MUTED, anchor="end"))
    pts = []
    for i in range(0, gw + 1, 3):
        fr = i / float(gw)
        # гострий резонанс біля fr≈0.32, глибокий нуль біля fr≈0.62
        peak = 1.0 / (1 + 900 * (fr - 0.32) ** 2)
        notch = (fr - 0.62) ** 2 / ((fr - 0.62) ** 2 + 0.0009)
        val = 0.25 + 0.75 * peak
        val *= (0.15 + 0.85 * notch)
        yy = gy + gh - val * gh
        pts.append("%.1f,%.1f" % (gx + i, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts), BIH))
    f.append(text(gx + 96, gy + 8, "гострий пік ← полюс", size=9, color=BIH, italic=True, anchor="middle"))
    f.append(text(gx + 210, gy + gh - 10, "провал ← нуль", size=9, color=NEG, italic=True, anchor="middle"))
    render(os.path.join(IMG, "d-pole-zero.svg"), W, H, *f)


# ── D4. Вартість notch наочно: стовпчики БІХ vs КІХ у лог-масштабі ────────────
def d_cost_breakdown():
    W, H = 720, 320
    f = [text(W / 2, 26, "Ціна гострого notch: БІХ проти КІХ", size=15, bold=True)]

    metrics = [
        ("множень/відлік", 5, 400),
        ("чисел стану", 4, 400),
        ("затримка, відл.", 0.5, 199),
    ]
    base = 250
    maxh = 170
    import math as _m
    def barh(v):  # логарифмічна висота (щоб 5 і 400 обидва було видно)
        return 14 + maxh * (_m.log10(v + 1) / _m.log10(401))
    gw = 200
    x = 60
    for label, vb, vf in metrics:
        # БІХ
        hb = barh(vb)
        f.append(rect(x, base - hb, 56, hb, fill="#f6d4d1", stroke=BIH, sw=1.5, rx=3))
        f.append(text(x + 28, base - hb - 8, str(vb), size=11, color=BIH, bold=True))
        f.append(text(x + 28, base + 16, "БІХ", size=9.5, color=BIH))
        # КІХ
        hf = barh(vf)
        f.append(rect(x + 66, base - hf, 56, hf, fill="#d8f0e0", stroke=KIH, sw=1.5, rx=3))
        f.append(text(x + 94, base - hf - 8, str(vf), size=11, color=KIH, bold=True))
        f.append(text(x + 94, base + 16, "КІХ", size=9.5, color=KIH))
        f.append(text(x + 61, base + 36, label, size=10, color=INK, bold=True))
        x += gw
    f.append(line(40, base, 700, base, color=INK, sw=1.2))
    f.append(text(W / 2, 300,
                  "той самий виріз 50 Гц на 1 кГц — БІХ дешевший на два порядки (лог-шкала)",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "d-cost-breakdown.svg"), W, H, *f)


# ── D5. Граничний цикл: квантування в петлі БІХ проти чистого КІХ ─────────────
def d_limit_cycle():
    W, H = 760, 320
    f = [text(W / 2, 26, "Пастка fixed-point: граничний цикл у петлі", size=15, bold=True)]
    import math as _m

    # ліва: КІХ — згасає в нуль
    f.append(rect(24, 48, 350, 240, fill="#f3faf5", stroke=KIH, sw=1.6))
    f.append(text(199, 70, "КІХ — без петлі, згасає в нуль", size=12, color=KIH, bold=True))
    ax, ay, aw = 60, 200, 270
    f.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.2))
    pts = []
    for i in range(30):
        v = 60 * (0.7 ** i) if i < 9 else 0    # рівно нуль після вікна
        pts.append((ax + i * 9, ay - v))
    for i, (bx, by) in enumerate(pts):
        f.append(line(bx, ay, bx, by, color=KIH, sw=2))
    f.append(text(199, 236, "після M відліків — рівно 0", size=9.5, color=KIH, italic=True))
    f.append(text(199, 258, "похибці ніде накопичуватись", size=9.5, color=MUTED, italic=True))

    # права: БІХ — застряг у незгасному циклі
    f.append(rect(400, 48, 336, 240, fill="#fdf2f1", stroke=BIH, sw=1.6))
    f.append(text(568, 70, "БІХ — квант у петлі не гасне", size=12, color=BIH, bold=True))
    bx0, by0, bw2 = 430, 170, 280
    f.append(line(bx0, by0, bx0 + bw2, by0, color=INK, sw=1.2))
    for i in range(30):
        v = 55 * (0.6 ** i)
        if v < 10:                              # округлення в петлі лишає незгасний «зубчик»
            v = 10 * (1 if i % 2 else -1)
        f.append(line(bx0 + i * 9, by0, bx0 + i * 9, by0 - v, color=BIH, sw=2))
    f.append(text(568, 236, "застряг на ±1 молодшому біті — вічно", size=9.5, color=BIH, italic=True))
    f.append(text(568, 258, "тихий трiск, якого нема в математиці", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 306,
                  "округлення всередині зворотного зв'язку живить саме себе — граничний цикл",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "d-limit-cycle.svg"), W, H, *f)


# ── M1. Геометрія: мінімальна відстань до полюса ≈ 1−r, смуга ≈ 2(1−r) ────────
def m_pole_distance():
    """Наближення дуги кола прямою біля полюса: чому найближча відстань точки
    e^(jω) до полюса r·e^(jω0) дорівнює приблизно 1−r, а на рівні −3 дБ
    відстань зростає в √2 разів, звідки смуга ≈ 2(1−r)."""
    W, H = 760, 380
    f = [text(W / 2, 26, "Чому найближча відстань до полюса ≈ 1−r", size=15, bold=True)]

    # Локальна «лупа»: коло майже пряме біля полюса. Малюємо горизонтально:
    # верхня лінія — одиничне коло (радіус 1), полюс нижче на глибині (1−r).
    x0, x1 = 90, 660           # відрізок дуги кола (майже пряма в лупі)
    yc = 130                   # рівень одиничного кола (|z|=1)
    dr = 78                    # екранна «глибина» 1−r (сильно збільшена)
    yp = yc + dr               # рівень полюса

    # одиничне коло як майже пряма дуга
    f.append(('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" '
              'stroke-width="1.8"/>' % (x0, yc + 10, (x0 + x1) // 2, yc - 8, x1, yc + 10, INK)))
    f.append(text(x1 + 6, yc + 14, "|z| = 1", size=10, color=INK, anchor="start", italic=True))

    # полюс
    pcx = (x0 + x1) // 2
    f.append(line(pcx - 8, yp - 8, pcx + 8, yp + 8, color=BIH, sw=2.6))
    f.append(line(pcx - 8, yp + 8, pcx + 8, yp - 8, color=BIH, sw=2.6))
    f.append(text(pcx, yp + 30, "полюс  r·e^(jω₀)", size=11, color=BIH, bold=True))

    # робоча точка в резонансі — прямо над полюсом
    f.append(circle(pcx, yc - 2, 5, fill=BIH, stroke=BIH, sw=1))
    f.append(text(pcx, yc - 14, "робоча точка e^(jω₀)", size=10, color=INK))

    # мінімальна відстань 1−r (вертикаль)
    f.append(line(pcx, yc - 2, pcx, yp, color=FIELD, sw=2.4))
    f.append(text(pcx + 10, (yc + yp) // 2 + 4, "1 − r", size=12, color=FIELD,
                  anchor="start", bold=True))
    f.append(text(pcx - 12, (yc + yp) // 2 + 4, "d_min", size=10, color=MUTED,
                  anchor="end", italic=True))

    # точки −3 дБ: точка на колі зсунута вбік так, що відстань = √2·(1−r)
    off = int(dr)              # горизонтальний зсув = 1−r (бо √2·d ⇒ катет = d)
    for sgn in (-1, +1):
        bx = pcx + sgn * off
        f.append(circle(bx, yc - 2, 4.5, fill="#fff", stroke=NEG, sw=2))
        f.append(line(bx, yc - 2, pcx, yp, color=NEG, sw=1.8, dash="4,3"))
    f.append(text(pcx + off + 8, yc - 10, "√2·(1−r)", size=10.5, color=NEG,
                  anchor="start", bold=True))
    f.append(text(pcx - off - 8, yc - 10, "√2·(1−r)", size=10.5, color=NEG,
                  anchor="end", bold=True))
    # дужка смуги вздовж кола між −3 дБ точками
    yb = yc - 40
    f.append(line(pcx - off, yb, pcx + off, yb, color=GOLD, sw=1.6))
    f.append(line(pcx - off, yb, pcx - off, yc - 6, color=GOLD, sw=1, dash="3,3"))
    f.append(line(pcx + off, yb, pcx + off, yc - 6, color=GOLD, sw=1, dash="3,3"))
    f.append(text(pcx, yb - 8, "смуга −3 дБ  Δω ≈ 2(1−r)", size=11.5, color=GOLD, bold=True))

    # підпис-висновок унизу
    bb = fitbox(60, 300, 640, 56,
                "У лупі коло майже пряме, а полюс — на глибині 1−r під ним. Найближче "
                "точка підходить рівно над полюсом: d_min ≈ 1−r. Відстань виростає в √2 "
                "(потужність удвічі менша, −3 дБ), коли точка відходить убік теж на ≈ 1−r "
                "→ ширина піка Δω ≈ 2(1−r).",
                size=11, fill="#fbf7ee", stroke=GOLD, sw=1.4)
    f.append(bb)
    render(os.path.join(IMG, "m-pole-distance.svg"), W, H, *f)


# ── M2. Q вибухає, коли r→1: три радіуси на числах ───────────────────────────
def m_q_vs_r():
    """Наочно: як звуження 1−r удесятеро загострює пік удесятеро (Q, смуга в Гц)
    для notch 50 Гц при fs = 1 кГц. ω₀ = 2π·50/1000 = 0.3142 рад/відлік."""
    W, H = 760, 360
    f = [text(W / 2, 26, "Гострота вибухає, коли полюс тулиться до кола", size=15, bold=True)]
    import math as _m

    w0 = 2 * _m.pi * 50 / 1000.0
    rows = [(0.90, "#2457d6"), (0.98, "#b9770e"), (0.999, "#c0392b")]

    # таблиця
    cols_x = [70, 210, 350, 500, 650]
    heads = ["r", "1 − r", "Q ≈ ω₀/2(1−r)", "смуга −3 дБ, Гц", "запас до кола"]
    ty = 66
    f.append(rect(40, ty - 22, 680, 30, fill="#eef1f4", stroke="none", sw=0, rx=4))
    for cx, h in zip(cols_x, heads):
        f.append(text(cx, ty, h, size=11, bold=True))

    y = ty + 34
    for r, col in rows:
        onemr = 1 - r
        Q = w0 / (2 * onemr)
        bw_rad = 2 * onemr                     # рад/відлік
        bw_hz = bw_rad / (2 * _m.pi) * 1000    # у Гц при fs=1кГц
        f.append(text(cols_x[0], y, "%.3f" % r if r > 0.99 else "%.2f" % r,
                      size=12, color=col, bold=True))
        f.append(text(cols_x[1], y, "%.3f" % onemr, size=12, color=col))
        f.append(text(cols_x[2], y, "%.1f" % Q, size=12, color=col, bold=True))
        f.append(text(cols_x[3], y, "%.1f" % bw_hz, size=12, color=col))
        f.append(text(cols_x[4], y, "%.3f" % onemr, size=12, color=col))
        y += 40

    # смуги-«гребінці»: висота піка ~ Q, ширина ~ 1−r (наочно, не в масштабі осей)
    gx, gy, gw = 70, 330, 620
    f.append(line(gx, gy, gx + gw, gy, color=INK, sw=1.2))
    peaks = [(0.90, "#2457d6", 40, 45), (0.98, "#b9770e", 200, 120), (0.999, "#c0392b", 335, 215)]
    for r, col, px, h in peaks:
        onemr = 1 - r
        half = max(2, 900 * onemr)             # напівширина в px (наочно ~ 1−r)
        cxp = gx + px
        f.append(('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                  'stroke="%s" stroke-width="2.2"/>' %
                  (cxp - half, gy, cxp, gy - h, cxp + half, gy, col)))
        f.append(text(cxp, gy - h - 6, "r=%.3g" % r, size=9.5, color=col, bold=True))

    f.append(text(W / 2, 352,
                  "удесятеро тонше 1−r → удесятеро вищий Q і вужчий виріз — тими самими 5 коефіцієнтами",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "m-q-vs-r.svg"), W, H, *f)


# ── Вставка math-linear-phase-proof ─────────────────────────────────────────
def m_pair_vectors():
    """Фазорна суть: дзеркальна пара дає два вектори e^{±jωτ}, сума яких лягає
    на дійсну вісь → 2cos(ωτ). Уявні частини гасяться → фаза зникає."""
    W, H = 720, 400
    f = [text(W / 2, 26, "Чому в дзеркальної пари зникає фаза", size=15, bold=True)]

    # ── ліворуч: комплексна площина з двома векторами ─────────────────────────
    cx, cy, R = 205, 210, 120
    f.append(circle(cx, cy, R, fill="none", stroke="#d7dbe0", sw=1.2))
    f.append(line(cx - R - 22, cy, cx + R + 22, cy, color=INK, sw=1.2))   # Re
    f.append(line(cx, cy + R + 22, cx, cy - R - 30, color=INK, sw=1.2))   # Im
    f.append(text(cx + R + 28, cy + 4, "Re", size=11, color=MUTED, anchor="start"))
    f.append(text(cx + 6, cy - R - 22, "Im", size=11, color=MUTED, anchor="start"))

    ang = 38 * math.pi / 180
    dx, dy = R * math.cos(ang), R * math.sin(ang)
    # два вектори пари: зсунутий раніше (+фаза) і пізніше (−фаза)
    f.append(arrow(cx, cy, cx + dx, cy - dy, color=KIH, sw=2.2))
    f.append(arrow(cx, cy, cx + dx, cy + dy, color=BIH, sw=2.2))
    f.append(text(cx + dx + 8, cy - dy - 4, "e", size=12, color=KIH, anchor="start", italic=True))
    f.append(text(cx + dx + 20, cy - dy - 10, "+jωτ", size=9, color=KIH, anchor="start"))
    f.append(text(cx + dx + 8, cy + dy + 12, "e", size=12, color=BIH, anchor="start", italic=True))
    f.append(text(cx + dx + 20, cy + dy + 6, "−jωτ", size=9, color=BIH, anchor="start"))
    # сума — уздовж дійсної осі
    f.append(arrow(cx, cy, cx + 2 * dx, cy, color=GOLD, sw=3))
    f.append(text(cx + 2 * dx + 6, cy - 8, "2cos(ωτ)", size=11, color=GOLD, anchor="start", bold=True))
    # пунктири-складові (паралелограм)
    f.append(line(cx + dx, cy - dy, cx + 2 * dx, cy, color=MUTED, sw=1, dash="3,3"))
    f.append(line(cx + dx, cy + dy, cx + 2 * dx, cy, color=MUTED, sw=1, dash="3,3"))
    f.append(text(cx, cy + R + 44,
                  "уявні частини ±sin(ωτ) гасяться",
                  size=10.5, color=MUTED, italic=True))

    # ── праворуч: ланцюжок наслідків ──────────────────────────────────────────
    bx = 415
    f.append(fitbox(bx, 70, 285, 52,
                    "пара x[n−k] і x[n−(M−k)]\nоднаково далеко від центра x[n−M/2]",
                    size=11, fill="#eef7f0", stroke=KIH, sw=1.5))
    f.append(arrow(bx + 142, 124, bx + 142, 150, color=INK, sw=1.6))
    f.append(fitbox(bx, 152, 285, 50,
                    "cos(θ+ωτ) + cos(θ−ωτ)\n= 2·cos(ωτ)·cos(θ)",
                    size=12, fill=FILL, stroke=INK, sw=1.5, bold=True))
    f.append(arrow(bx + 142, 204, bx + 142, 230, color=INK, sw=1.6))
    f.append(fitbox(bx, 232, 285, 52,
                    "множник 2cos(ωτ) — ДІЙСНИЙ:\nміняє амплітуду, не фазу",
                    size=11, fill="#fff6e9", stroke=GOLD, sw=1.5))
    f.append(arrow(bx + 142, 286, bx + 142, 312, color=INK, sw=1.6))
    f.append(fitbox(bx, 314, 285, 50,
                    "спільна затримка = центр вікна\nрівно M/2 для всіх частот",
                    size=11, fill="#eef7f0", stroke=KIH, sw=1.5, bold=True))

    render(os.path.join(IMG, "m-pair-vectors.svg"), W, H, *f)


# ── Вставка: чотири типи лінійно-фазових КІХ та їхні обов'язкові нулі ─────────
def m_four_types():
    """Карта 2×2: (симетрія/антисиметрія) × (парна/непарна довжина) → типи I–IV.
    У кожній клітинці — ескіз відводів і де амплітуда мусить занулитися."""
    W, H = 730, 470
    f = [text(W / 2, 26, "Чотири типи лінійно-фазових КІХ", size=15, bold=True)]

    # підписи осей
    f.append(text(28, 150, "симетричні", size=12, color=KIH, bold=True, anchor="start"))
    f.append(text(28, 166, "b[k]=b[M−k]", size=9.5, color=MUTED, anchor="start"))
    f.append(text(28, 330, "антисиметр.", size=12, color=BIH, bold=True, anchor="start"))
    f.append(text(28, 346, "b[k]=−b[M−k]", size=9.5, color=MUTED, anchor="start"))
    f.append(text(280, 62, "непарна довжина (є центр)", size=11, bold=True))
    f.append(text(545, 62, "парна довжина (центра нема)", size=11, bold=True))

    def stems(x0, y0, vals, col):
        """Стовпчики імпульсної характеристики (± висоти) навколо базової лінії."""
        out = [line(x0, y0, x0 + 130, y0, color=INK, sw=1)]
        n = len(vals)
        step = 130 / (n + 1)
        for i, v in enumerate(vals):
            xx = x0 + step * (i + 1)
            out.append(line(xx, y0, xx, y0 - v, color=col, sw=3))
            out.append(circle(xx, y0 - v, 2.6, fill=col, stroke=col, sw=1))
        return "".join(out)

    cell_w, cell_h = 250, 150
    cells = [
        # (x, y, назва, ескіз-висоти, нулі-текст, колір нулів, застосування)
        (150, 78, "Тип I", [16, 28, 38, 28, 16], KIH,
         "жодних обов'язкових нулів", MUTED, "ФНЧ, ФВЧ, смуга, notch"),
        (415, 78, "Тип II", [20, 36, 36, 20], KIH,
         "нуль при ω=π", BIH, "ФВЧ неможливий (сам гасне на π)"),
        (150, 258, "Тип III", [20, 32, 0, -32, -20], BIH,
         "нулі при ω=0 і ω=π", BIH, "диференціатор, Гільберт"),
        (415, 258, "Тип IV", [24, 38, -38, -24], BIH,
         "нуль при ω=0", BIH, "диференціатор, ФВЧ (на π вільний)"),
    ]
    for x, y, name, vals, symcol, zeros, zcol, use in cells:
        f.append(rect(x, y, cell_w, cell_h, fill="#fbfcfd", stroke="#d7dbe0", sw=1.4))
        f.append(text(x + 12, y + 22, name, size=12.5, color=symcol, bold=True, anchor="start"))
        f.append(stems(x + 55, y + 92, vals, symcol))
        f.append(text(x + 12, y + 122, zeros, size=10.5, color=zcol, bold=True, anchor="start"))
        f.append(text(x + 12, y + 140, use, size=9, color=MUTED, italic=True, anchor="start"))

    f.append(text(W / 2, 462,
                  "антисиметрія додає фазі сталі +90°; нуль там, де дзеркальна сума сама себе гасить",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "m-four-types.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДЛЯ ВСТАВКИ proj-cascade-notch-fir.md — тракт у fixed-point (Q31)
# ════════════════════════════════════════════════════════════════════════════

# ── P1. Повний тракт у fixed-point: формат і акумулятор на кожній ланці ───────
def p_sos_pipeline():
    W, H = 820, 340
    f = [text(W / 2, 26, "Тракт давача у fixed-point: формат і захист на кожній ланці", size=15, bold=True)]

    # три ланки; під кожною — формат стану й акумулятора
    stages = [
        ("медіана-3", "нелінійна", "int32, без петлі", ("сортування, не сума —", "переповнення нема"), GOLD),
        ("БІХ-notch 50 Гц", "каскад біквадів, DF1", "стан Q31, акум. int64", ("петля назад —", "насичення в петлі!"), BIH),
        ("КІХ-згладжування", "лінійна фаза", "стан Q31, акум. int64", ("без петлі —", "похибка локальна"), KIH),
    ]
    x = 22
    boxw = 250
    for title_, tag, fmt, warn, col in stages:
        f.append(rect(x, 66, boxw, 96, fill=FILL, stroke=col, sw=1.9))
        f.append(text(x + boxw / 2, 92, title_, size=13.5, color=col, bold=True))
        f.append(text(x + boxw / 2, 112, tag, size=10, color=MUTED, italic=True))
        f.append(line(x + 16, 122, x + boxw - 16, 122, color=col, sw=1))
        f.append(text(x + boxw / 2, 142, fmt, size=10.5, color=INK, bold=True))
        # нижня примітка-попередження (два рядки курсивом)
        f.append(text(x + boxw / 2, 184, warn[0], size=10, color=col, italic=True))
        f.append(text(x + boxw / 2, 198, warn[1], size=10, color=col, italic=True))
        x += boxw + 22
    f.append(arrow(272, 114, 294, 114, color=INK, sw=2.2))
    f.append(arrow(544, 114, 566, 114, color=INK, sw=2.2))

    # вхід/вихід підписи
    f.append(text(22, 58, "сирий відлік АЦП →", size=10, color=MUTED, anchor="start", italic=True))
    f.append(text(W - 22, 58, "→ чистий Q31", size=10, color=MUTED, anchor="end", italic=True))

    f.append(text(W / 2, 250,
                  "єдиний масштаб Q31 крізь увесь тракт; проміжні суми — у 64-бітному акумуляторі",
                  size=11, color=INK, italic=True))
    f.append(text(W / 2, 274,
                  "нелінійна медіана переповнення не боїться; обидва лінійні фільтри — бояться,",
                  size=10, color=MUTED, italic=True))
    f.append(text(W / 2, 294,
                  "а найгостріше боїться БІХ, бо його вихід вертається у власний вхід",
                  size=10, color=MUTED, italic=True))
    f.append(text(W / 2, 322,
                  "той самий ланцюжок, що в базовій темі, — тепер цілими числами на чипі без FPU",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "p-sos-pipeline.svg"), W, H, *f)


# ── P2. Пряма форма I проти транспонованої II: чому в Q31 беруть DF1 ──────────
def p_df1_vs_df2():
    W, H = 820, 360
    f = [text(W / 2, 26, "Форма біквада: чому в цілій арифметиці — пряма форма I", size=15, bold=True)]

    # ── ліворуч: DF1 ──
    lx = 24
    f.append(rect(lx, 48, 372, 264, fill="#f3faf5", stroke=KIH, sw=1.8))
    f.append(text(lx + 186, 72, "Пряма форма I", size=13.5, color=KIH, bold=True))
    f.append(text(lx + 186, 90, "4 комірки стану: x1 x2 y1 y2", size=10.5, color=INK))
    # одна точка підсумовування
    cx = lx + 186
    f.append(circle(cx, 150, 20, fill="#eafaf0", stroke=KIH, sw=2))
    f.append(text(cx, 156, "Σ", size=20, color=KIH, bold=True))
    f.append(text(cx, 190, "ОДНА точка підсумовування", size=10, color=KIH, bold=True))
    # входи в суму
    for dxp, lab in [(-120, "b·x"), (120, "−a·y")]:
        f.append(arrow(cx + (dxp / abs(dxp)) * 100, 150, cx + (18 if dxp < 0 else -18), 150, color=INK, sw=1.6))
        f.append(text(cx + dxp, 145, lab, size=11, color=INK, bold=True))
    f.append(text(lx + 186, 232, "усе множиться на ВХОДІ,", size=10.5, color=INK, italic=True))
    f.append(text(lx + 186, 250, "сумується РАЗ → 64-біт акум.,", size=10.5, color=INK, italic=True))
    f.append(text(lx + 186, 268, "одне насичення на записі", size=10.5, color=INK, italic=True))
    f.append(text(lx + 186, 294, "стан вузький → безпечний у Q31", size=11, color=KIH, bold=True))

    # ── праворуч: DF2T ──
    rx = 424
    f.append(rect(rx, 48, 372, 264, fill="#fdf2f1", stroke=BIH, sw=1.8))
    f.append(text(rx + 186, 72, "Транспонована форма II", size=13.5, color=BIH, bold=True))
    f.append(text(rx + 186, 90, "2 комірки стану: d1 d2", size=10.5, color=INK))
    # два вузли-стани
    for i, dlab in enumerate(["d1", "d2"]):
        nx = rx + 110 + i * 150
        f.append(circle(nx, 150, 18, fill="#fde9e7", stroke=BIH, sw=2))
        f.append(text(nx, 156, dlab, size=13, color=BIH, bold=True))
    f.append(text(rx + 186, 190, "стан несе ЧАСТКОВІ суми", size=10, color=BIH, bold=True))
    f.append(text(rx + 186, 232, "ощадніша — 2 комірки замість 4,", size=10.5, color=INK, italic=True))
    f.append(text(rx + 186, 250, "але стан має ВЕЛИКИЙ розмах,", size=10.5, color=INK, italic=True))
    f.append(text(rx + 186, 268, "не влазить у Q31 без переповнення", size=10.5, color=INK, italic=True))
    f.append(text(rx + 186, 294, "у CMSIS-DSP — лише float", size=11, color=BIH, bold=True))

    f.append(text(W / 2, 336,
                  "та сама передавальна функція — та в Q31 надійна лише DF1: один вузол суми, вузький стан",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "p-df1-vs-df2.svg"), W, H, *f)


if __name__ == "__main__":
    fig_comparison()
    fig_decision_tree()
    fig_recipes()
    fig_already_know()
    fig_tradeoff()
    fig_pipeline()
    # детальна версія
    d_structure()
    d_symmetry_phase()
    d_pole_zero()
    d_cost_breakdown()
    d_limit_cycle()
    # вставка math-pole-sharpness
    m_pole_distance()
    m_q_vs_r()
    # вставка math-linear-phase-proof
    m_pair_vectors()
    m_four_types()
    # вставка proj-cascade-notch-fir
    p_sos_pipeline()
    p_df1_vs_df2()
    print("OK: 17 figures ->", IMG)
