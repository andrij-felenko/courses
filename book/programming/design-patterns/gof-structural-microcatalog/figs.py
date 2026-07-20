# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Мапа сімох: біль → патерн ────────────────────────────────────────────
def fig_map():
    """Сім структурних патернів як сім відповідей на «як скласти». Ліворуч —
    конкретний біль, праворуч — патерн; синій = має свою статтю, червоний = Міст (тут)."""
    W, H = 840, 540
    frags = []
    frags.append(text(W / 2, 34, "Сім структурних патернів — сім відповідей на «як скласти»",
                      size=17, bold=True))

    # (біль, патерн, тут?) ; тут=True → Міст живе в цій статті
    rows = [
        ("чужий інтерфейс — треба на наш",        "Адаптер",       False),
        ("дві осі змін множать класи",            "Міст",          True),
        ("дерево частин, а поводитись як з одним", "Компонувальник", False),
        ("додати обов'язок на льоту, без підкласів", "Декоратор",   False),
        ("складну підсистему — за один вхід",      "Фасад",         False),
        ("тьма однакових об'єктів їсть пам'ять",   "Легковаговик",  False),
        ("керувати доступом до об'єкта",           "Проксі",        False),
    ]

    # легенда праворуч угорі
    lx = W - 250
    frags.append(circle(lx, 58, 7, fill="#eaf3ff", stroke=NEG, sw=2))
    frags.append(text(lx + 15, 63, "має свою статтю", size=12, color=INK, anchor="start"))
    frags.append(circle(lx + 150, 58, 7, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(lx + 165, 63, "тут", size=12, color=INK, anchor="start"))

    px = 250          # центр колонки болю
    qx = 640          # центр колонки патерна
    pw, qw = 340, 220
    y0, step = 100, 60
    for i, (pain, pat, here) in enumerate(rows):
        cy = y0 + i * step
        # рамка болю (нейтральна)
        frags.append(fitbox(px - pw / 2, cy - 22, pw, 44, pain, size=13,
                            fill=FILL, stroke=MUTED, sw=1.4))
        # стрілка «болю → патерн», повз рамки
        frags.append(arrow(px + pw / 2 + 6, cy, qx - qw / 2 - 6, cy, color=MUTED, sw=1.7))
        # рамка патерна (колір за приналежністю)
        fill, stroke = ("#fdecea", POS) if here else ("#eaf3ff", NEG)
        frags.append(fitbox(qx - qw / 2, cy - 22, qw, 44, pat, size=15,
                            fill=fill, stroke=stroke, sw=2, bold=True))

    render(os.path.join(IMG, 'structural-map.svg'), W, H, *frags)


# ── 2. Той самий кістяк, різний намір ───────────────────────────────────────
def fig_wrappers():
    """Адаптер, Декоратор, Проксі, Міст мають однаковий кістяк «об'єкт тримає інший
    і передає виклик далі» — а різняться лише наміром."""
    W, H = 820, 500
    frags = []
    frags.append(text(W / 2, 34, "Схожі як обгортки — різні за наміром", size=17, bold=True))

    # спільний кістяк угорі: клієнт → обгортка → ціль
    cb, cw, ch = textbox(150, 92, "клієнт", size=14, pad=12, fill=FILL, stroke=LINE, min_w=120)
    wb, ww, wh = textbox(410, 92, ["обгортка", "(тримає ціль)"], size=13, pad=12,
                         fill="#eef2ff", stroke=NEG, sw=2, min_w=150)
    tb, tw, th = textbox(670, 92, "ціль", size=14, pad=12, fill=FILL, stroke=LINE, min_w=120)
    frags.append(arrow(150 + cw / 2, 92, 410 - ww / 2, 92, color=MUTED, sw=1.8))
    frags.append(arrow(410 + ww / 2, 92, 670 - tw / 2, 92, color=MUTED, sw=1.8))
    frags.append(cb)
    frags.append(wb)
    frags.append(tb)
    frags.append(text(410, 138, "спільний кістяк: об'єкт тримає інший і передає виклик далі",
                      size=12, color=MUTED))

    # чотири смуги: патерн | що РІЗНЕ (намір)
    bands = [
        ("Адаптер",   "міняє ФОРМУ інтерфейсу: чужий → наш", NEG),
        ("Декоратор", "інтерфейс той самий — ДОДАЄ поведінку", NEG),
        ("Проксі",    "інтерфейс той самий — КЕРУЄ доступом", NEG),
        ("Міст",      "не фіксує жоден — дає двом ієрархіям мінятись нарізно", POS),
    ]
    x, w = 70, W - 140
    y0, bh, gap = 178, 62, 12
    for i, (name, diff, col) in enumerate(bands):
        y = y0 + i * (bh + gap)
        fill = "#fdecea" if col is POS else "#f4f6f8"
        frags.append(rect(x, y, w, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        frags.append(text(x + 22, y + bh / 2 + 5, name, size=15, color=col,
                          anchor="start", bold=True))
        frags.append(line(x + 190, y + 12, x + 190, y + bh - 12, color="#d0d5dd", sw=1.2))
        frags.append(text(x + 212, y + bh / 2 + 5, diff, size=14, color=INK, anchor="start"))

    render(os.path.join(IMG, 'wrapper-intent.svg'), W, H, *frags)


# ── 3. Міст: вибух підкласів → дві ієрархії ─────────────────────────────────
def fig_bridge():
    """Ліворуч — підклас на кожну пару фігура×рушій (3×3=9, множиться);
    праворуч — дві ієрархії, з'єднані посиланням-мостом (3+3=6, додається)."""
    W, H = 940, 470
    frags = []
    frags.append(text(W / 2, 30, "Дві осі мінливості: підкласи множаться — Міст додає",
                      size=17, bold=True))

    # розділювач
    frags.append(line(478, 58, 478, H - 40, color="#d0d5dd", sw=1.4, dash="6,6"))

    # ── ліворуч: сітка 3×3 підкласів ──
    frags.append(text(250, 62, "підклас на КОЖНУ пару", size=15, color=INK, bold=True))
    shapes = ["Circle", "Square", "Triangle"]
    rends = ["Vector", "Raster", "OpenGL"]
    x0, y0 = 150, 92
    cw, ch = 100, 58
    # заголовки стовпців (рушії)
    for j, rn in enumerate(rends):
        frags.append(text(x0 + j * cw + cw / 2, y0 - 12, rn, size=12, color=MUTED, bold=True))
    # заголовки рядків (фігури) — ліворуч, anchor end, з запасом
    for i, sn in enumerate(shapes):
        frags.append(text(x0 - 12, y0 + i * ch + ch / 2 + 4, sn, size=12, color=MUTED,
                          anchor="end", bold=True))
    # клітини — комбінований клас (2 рядки)
    for i, sn in enumerate(shapes):
        for j, rn in enumerate(rends):
            x = x0 + j * cw
            y = y0 + i * ch
            frags.append(fitbox(x + 4, y + 4, cw - 8, ch - 8, [rn, sn], size=11,
                                fill="#fdecea", stroke=POS, sw=1.3))
    lbl_l, _, _ = textbox(250, y0 + 3 * ch + 48,
                          ["3 × 3 = 9 класів", "+1 фігура = +3   ·   +1 рушій = +3",
                           "→ множиться"],
                          size=13, pad=11, fill="#fdf0ee", stroke=POS, sw=1.6, min_w=330)
    frags.append(lbl_l)

    # ── праворуч: дві ієрархії + міст ──
    frags.append(text(700, 62, "дві ієрархії + посилання", size=15, color=INK, bold=True))
    scx, rcx = 600, 812
    frags.append(text(scx, 92, "Shape", size=13, color=NEG, bold=True))
    frags.append(text(rcx, 92, "Renderer", size=13, color=NEG, bold=True))
    sy = [120, 178, 236]
    sboxes, rboxes = [], []
    for lab, y in zip(shapes, sy):
        b, w, h = textbox(scx, y, lab, size=13, pad=10, fill="#eaf3ff", stroke=NEG,
                          sw=1.8, min_w=126)
        sboxes.append((y, w, h, b))
    for lab, y in zip(rends, sy):
        b, w, h = textbox(rcx, y, lab, size=13, pad=10, fill="#eef7ee", stroke=FIELD,
                          sw=1.8, min_w=126)
        rboxes.append((y, w, h, b))
    # міст: Shape тримає Renderer (одна показова стрілка від Circle до колонки рушіїв)
    sy0, sw0, sh0, _ = sboxes[0]
    frags.append(arrow(scx + sw0 / 2 + 4, sy0, rcx - rboxes[0][1] / 2 - 4, sy0,
                       color=POS, sw=2.2))
    frags.append(text((scx + rcx) / 2, sy0 - 12, "тримає (міст)", size=12, color=POS, bold=True))
    for _, _, _, b in sboxes:
        frags.append(b)
    for _, _, _, b in rboxes:
        frags.append(b)
    lbl_r, _, _ = textbox(700, y0 + 3 * ch + 48,
                          ["3 + 3 = 6 класів на всі 9 пар", "+1 фігура = +1   ·   +1 рушій = +1",
                           "→ додається"],
                          size=13, pad=11, fill="#eef7ee", stroke=FIELD, sw=1.6, min_w=330)
    frags.append(lbl_r)

    render(os.path.join(IMG, 'bridge-explosion.svg'), W, H, *frags)


# ── 4. [proj] Інтерфейс реалізації: товстий проти примітивного ──────────────
def fig_implementor_interface():
    """Ключ Мосту — НЕ сам факт делегування, а набір операцій реалізації.
    Метод на кожну фігуру → вибух вертається тілами методів (S·R).
    Замкнений набір примітивів → +1 фігура не чіпає жодного рушія (R·P, P стале)."""
    W, H = 980, 610
    frags = []
    frags.append(text(W / 2, 32, "Інтерфейс реалізації вирішує все: товстий вибухає, примітивний — ні",
                      size=17, bold=True))

    frags.append(line(490, 58, 490, H - 96, color="#d0d5dd", sw=1.4, dash="6,6"))

    rends = ["SvgRenderer", "AsciiRenderer", "StatsRenderer"]

    # ── ліворуч: товстий інтерфейс ──
    frags.append(text(250, 68, "метод на КОЖНУ фігуру", size=15, color=POS, bold=True))
    lb, lw, lh = textbox(250, 148, ["Renderer", "drawCircle()", "drawRect()",
                                    "drawTriangle()", "drawStar()   ← нова фігура"],
                         size=13, pad=12, fill="#fdecea", stroke=POS, sw=2, min_w=290)
    frags.append(lb)
    ry = 300
    for i, rn in enumerate(rends):
        cy = ry + i * 62
        b, bw, bh = textbox(250, cy, rn, size=13, pad=10, fill=FILL, stroke=MUTED,
                            sw=1.5, min_w=210)
        # стрілка від інтерфейсу до кожного рушія — повз рамки, ліворуч
        frags.append(arrow(250 - lw / 2 + 18, 148 + lh / 2 + 4, 250 - bw / 2 - 10, cy,
                           color=POS, sw=1.6))
        frags.append(b)
        frags.append(text(250 + bw / 2 + 12, cy + 5, "+1 тіло", size=12, color=POS,
                          anchor="start", bold=True))
    lbl, _, _ = textbox(250, H - 58, ["тіл методів = S · R", "+1 фігура = правка в УСІХ рушіях"],
                        size=13, pad=11, fill="#fdf0ee", stroke=POS, sw=1.6, min_w=380)
    frags.append(lbl)

    # ── праворуч: примітивний інтерфейс ──
    frags.append(text(735, 68, "замкнений набір примітивів", size=15, color=FIELD, bold=True))
    rb, rw, rh = textbox(735, 148, ["Renderer", "begin(w, h) / end()",
                                    "polyline(pts, closed)", "ellipse(cx, cy, rx, ry)"],
                         size=13, pad=12, fill="#eef7ee", stroke=FIELD, sw=2, min_w=290)
    frags.append(rb)
    for i, rn in enumerate(rends):
        cy = ry + i * 62
        b, bw, bh = textbox(735, cy, rn, size=13, pad=10, fill=FILL, stroke=MUTED,
                            sw=1.5, min_w=210)
        frags.append(arrow(735 - rw / 2 + 18, 148 + rh / 2 + 4, 735 - bw / 2 - 10, cy,
                           color=FIELD, sw=1.6))
        frags.append(b)
        frags.append(text(735 + bw / 2 + 12, cy + 5, "без змін", size=12, color=FIELD,
                          anchor="start", bold=True))
    # нова фігура входить лише в абстракцію (праворуч, щоб не перетнути стрілок до рушіїв)
    nb, nw, nh = textbox(800, 226, "Star.draw() → polyline(10 точок)", size=12, pad=8,
                         fill="#eaf3ff", stroke=NEG, sw=1.6, min_w=260)
    frags.append(arrow(800, 226 - nh / 2 - 4, 800, 148 + rh / 2 + 4, color=NEG, sw=1.6))
    frags.append(nb)
    lbl2, _, _ = textbox(735, H - 58, ["тіл методів = R · P, P стале",
                                       "+1 фігура = 0 правок у рушіях"],
                         size=13, pad=11, fill="#eef7ee", stroke=FIELD, sw=1.6, min_w=380)
    frags.append(lbl2)

    render(os.path.join(IMG, 'implementor-interface.svg'), W, H, *frags)


# ── 5. [proj] Де міст окупається: криві зростання й поріг ───────────────────
def fig_crossover():
    """Класів проти кількості фігур при R=3: наївно S·R+1 росте прямою втричі
    крутішою, міст S+R+2 — на одиницю за фігуру. Перетин — там, де (S−1)(R−1) > 2."""
    W, H = 900, 560
    frags = []
    frags.append(text(W / 2, 32, "Де міст починає окупатися (рушіїв R = 3)", size=17, bold=True))

    # легенда — смугою під заголовком, поза полем графіка (щоб нічого не перетинала)
    frags.append(circle(250, 62, 5, fill=POS, stroke=POS, sw=1))
    frags.append(text(262, 66, "наївно: S · R + 1 — клас на кожну пару", size=13,
                      color=INK, anchor="start"))
    frags.append(circle(560, 62, 5, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(572, 66, "міст: S + R + 2 — дві ієрархії", size=13,
                      color=INK, anchor="start"))

    X0, Y0 = 110, 420          # початок координат
    XS, YS = 78, 12.0          # px на одну фігуру / на один клас
    def px(s): return X0 + (s - 1) * XS
    def py(c): return Y0 - c * YS

    # осі з запасом
    frags.append(line(X0, py(27), X0, Y0, color=MUTED, sw=1.4))
    frags.append(line(X0, Y0, px(8) + 30, Y0, color=MUTED, sw=1.4))
    frags.append(text(X0 - 68, py(27) + 4, "класів", size=13, color=MUTED, anchor="start", bold=True))
    frags.append(text(px(8) + 30, Y0 + 34, "фігур (S)", size=13, color=MUTED, anchor="end", bold=True))

    # сітка й підписи осей
    for c in range(0, 27, 5):
        frags.append(line(X0 - 5, py(c), px(8) + 14, py(c), color="#e6e9ee", sw=1))
        frags.append(text(X0 - 12, py(c) + 5, str(c), size=12, color=MUTED, anchor="end"))
    for s in range(1, 9):
        frags.append(text(px(s), Y0 + 26, str(s), size=12, color=MUTED))

    naive = [s * 3 + 1 for s in range(1, 9)]     # S·R + 1  (спільний інтерфейс Drawable)
    bridg = [s + 3 + 2 for s in range(1, 9)]     # S + R + 2 (Renderer + Shape)

    # поріг: до S=2 наївно не дорожче, з S=3 міст дешевший
    frags.append(line(px(2.5), py(27), px(2.5), Y0, color=MUTED, sw=1.3, dash="5,5"))
    frags.append(text(px(2.5) + 8, 88, "→ праворуч міст дешевший", size=12,
                      color=FIELD, anchor="start", bold=True))

    # криві
    for i in range(7):
        frags.append(line(px(i + 1), py(naive[i]), px(i + 2), py(naive[i + 1]), color=POS, sw=2.4))
        frags.append(line(px(i + 1), py(bridg[i]), px(i + 2), py(bridg[i + 1]), color=FIELD, sw=2.4))
    for i in range(8):
        frags.append(circle(px(i + 1), py(naive[i]), 4.5, fill=POS, stroke=POS, sw=1))
        frags.append(circle(px(i + 1), py(bridg[i]), 4.5, fill=FIELD, stroke=FIELD, sw=1))
        frags.append(text(px(i + 1), py(naive[i]) - 13, str(naive[i]), size=12, color=POS, bold=True))
        frags.append(text(px(i + 1), py(bridg[i]) + 21, str(bridg[i]), size=12, color=FIELD, bold=True))

    # умова — у вільному правому нижньому куті, під кривою мосту
    cnd, _, _ = textbox(620, Y0 - 66, ["поріг:  (S − 1)(R − 1) > 2",
                                       "R = 1 → ліва частина 0 → міст не окупиться НІКОЛИ"],
                        size=13, pad=11, fill="#f7fbf7", stroke=FIELD, sw=1.6, min_w=430)
    frags.append(cnd)

    render(os.path.join(IMG, 'bridge-crossover.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_map()
    fig_wrappers()
    fig_bridge()
    fig_implementor_interface()
    fig_crossover()
    print("figures written")
