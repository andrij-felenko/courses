# -*- coding: utf-8 -*-
"""Фігури до статті «Інтегральна схема» (book/electronics/analog/integrated-circuit).
Чотири фігури:
  monolith.json -> monolith.svg — розсип деталей із купою паяних з'єднань  ПРОТИ  однієї цілої схеми в кристалі
  inside.svg    — що всередині: один кремній родить R, C, транзистори тими самими шарами
  matching.svg  — серцевина для аналогу: абсолютне значення «гуляє», ВІДНОШЕННЯ сусідів — майже точне
  zoo.svg       — і аналогові, і цифрові ІС — усі монолітні (ОП, опора, дзеркало / логіка, MCU, пам'ять)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ─────────────────────────────────────────────────────────
def chip(cx, cy, w, h, pins=4, label=None, sub=None, body="#222831"):
    """Корпус мікросхеми з ніжками з обох боків (чорний прямокутник, сріблясті виводи)."""
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill=body, stroke="#000000", sw=1.6, rx=5)]
    # ніжки ліворуч/праворуч
    leg = 12
    step = h / (pins + 1)
    for i in range(1, pins + 1):
        yy = cy - h / 2 + i * step
        out.append(line(cx - w / 2, yy, cx - w / 2 - leg, yy, color="#9aa0a6", sw=3))
        out.append(line(cx + w / 2, yy, cx + w / 2 + leg, yy, color="#9aa0a6", sw=3))
    # «крапка-ключ» 1-ї ніжки
    out.append(circle(cx - w / 2 + 11, cy - h / 2 + 11, 3.2, fill="#cfd3d8", stroke="#cfd3d8"))
    if label:
        out.append(text(cx, cy + (0 if not sub else -5), label, size=13, color="#f1f3f4", bold=True))
    if sub:
        out.append(text(cx, cy + 13, sub, size=10, color="#aeb4bb"))
    return "".join(out)


def res_box(x, y, w, h, label=None):
    """Маленький резистор-зигзаг у рамці (схематично)."""
    out = [rect(x, y, w, h, fill="#fff", stroke=INK, sw=1.4, rx=3)]
    n = 5
    seg = w / (n + 1)
    yc = y + h / 2
    amp = h * 0.26
    px, py = x + seg * 0.5, yc
    out.append(line(x, yc, px, py, color=POS, sw=1.6))
    for i in range(n):
        nx = px + seg
        ny = yc - amp if i % 2 == 0 else yc + amp
        out.append(line(px, py, nx, ny, color=POS, sw=1.6))
        px, py = nx, ny
    out.append(line(px, py, x + w, yc, color=POS, sw=1.6))
    if label:
        out.append(text(x + w / 2, y - 6, label, size=11, color=INK))
    return "".join(out)


def cap_box(x, y, w, h, label=None):
    out = [rect(x, y, w, h, fill="#fff", stroke=INK, sw=1.4, rx=3)]
    cx = x + w / 2
    g = 5
    out.append(line(x + 6, y + h / 2, cx - g, y + h / 2, color=NEG, sw=1.6))
    out.append(line(cx - g, y + 8, cx - g, y + h - 8, color=NEG, sw=2.6))
    out.append(line(cx + g, y + 8, cx + g, y + h - 8, color=NEG, sw=2.6))
    out.append(line(cx + g, y + h / 2, x + w - 6, y + h / 2, color=NEG, sw=1.6))
    if label:
        out.append(text(x + w / 2, y - 6, label, size=11, color=INK))
    return "".join(out)


def npn_mini(cx, cy, r=15, label=None):
    out = [circle(cx, cy, r, fill="#fff", stroke=INK, sw=1.5)]
    bx = cx - 4
    out.append(line(bx, cy - 9, bx, cy + 9, color=INK, sw=2.2))
    out.append(line(cx - r, cy, bx, cy, color=INK, sw=1.4))
    out.append(line(bx, cy - 4, cx + 7, cy - 12, color=INK, sw=1.4))
    out.append(line(bx, cy + 4, cx + 7, cy + 12, color=INK, sw=1.4))
    out.append(arrow(cx + 2, cy + 7, cx + 7, cy + 12, color=INK, sw=1.5))
    if label:
        out.append(text(cx, cy + r + 14, label, size=11, color=INK))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. monolith.svg — розсип + паяння  ПРОТИ  одна ціла схема в кристалі
# ════════════════════════════════════════════════════════════════════════════
def fig_monolith():
    W, H = 720, 360
    f = []

    # ── ЛІВОРУЧ: «зшита» з окремих деталей плата ──
    f.append(text(180, 40, "Із окремих деталей", size=14, bold=True, color=POS))
    f.append(text(180, 58, "кожне з'єднання — паяти вручну", size=11, color=MUTED))
    bx, by, bw, bh = 60, 80, 240, 200
    f.append(rect(bx, by, bw, bh, fill="#eef2e6", stroke="#7a8b5a", sw=2, rx=8))

    import random
    random.seed(7)
    # вузли-деталі
    nodes = [(110, 130), (180, 115), (250, 140), (95, 200), (165, 185),
             (240, 205), (130, 245), (210, 250)]
    parts = ["R", "C", "Q", "R", "Q", "C", "R", "Q"]
    cols = {"R": POS, "C": NEG, "Q": INK}
    # дротики-перемички (хаотична павутина) — джерело крихкості
    pairs = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 6), (4, 5), (4, 7), (6, 7), (3, 4)]
    for a, b in pairs:
        x1, y1 = nodes[a]; x2, y2 = nodes[b]
        f.append(line(x1, y1, x2, y2, color="#b08968", sw=1.6))
    # точки паяння (помітні, їх багато)
    for (x, y), p in zip(nodes, parts):
        f.append(circle(x, y, 9, fill="#fff", stroke=cols[p], sw=2))
        f.append(text(x, y + 4, p, size=11, bold=True, color=cols[p]))
        f.append(circle(x, y, 13, fill="none", stroke="#c0392b", sw=0.0))
    f.append(text(bx + bw / 2, by + bh + 22, "багато деталей · багато паяних швів", size=11, color=MUTED))

    # ── стрілка-перехід ──
    f.append(arrow(312, 180, 372, 180, color=FIELD, sw=3.2))
    f.append(text(342, 168, "монолітно", size=11, color=FIELD, bold=True))

    # ── ПРАВОРУЧ: одна ціла схема в кристалі ──
    f.append(text(545, 40, "Як одне ціле в кремнії", size=14, bold=True, color=FIELD))
    f.append(text(545, 58, "деталі народжуються вже з'єднаними", size=11, color=MUTED))
    # кристал (die) у корпусі
    dx, dy, dw, dh = 430, 90, 230, 180
    f.append(rect(dx, dy, dw, dh, fill="#0f1622", stroke="#000", sw=1.6, rx=8))   # корпус
    # сам кристал
    kx, ky, kw, kh = dx + 34, dy + 28, dw - 68, dh - 70
    f.append(rect(kx, ky, kw, kh, fill="#1f6f4f", stroke="#27ae60", sw=1.6, rx=4))
    # «доріжки» метала по поверхні — сітка
    for i in range(1, 5):
        gx = kx + i * kw / 5
        f.append(line(gx, ky + 6, gx, ky + kh - 6, color="#7fe3b0", sw=1.2))
    for j in range(1, 3):
        gy = ky + j * kh / 3
        f.append(line(kx + 6, gy, kx + kw - 6, gy, color="#7fe3b0", sw=1.2))
    f.append(text(dx + dw / 2, ky + kh / 2 + 4, "одна схема", size=12, color="#eafff4", bold=True))
    # ніжки корпусу
    for i in range(1, 6):
        yy = dy + i * dh / 6
        f.append(line(dx, yy, dx - 12, yy, color="#9aa0a6", sw=3))
        f.append(line(dx + dw, yy, dx + dw + 12, yy, color="#9aa0a6", sw=3))
    f.append(text(dx + dw / 2, dy + dh + 22, "один кристал · жодного ручного дроту", size=11, color=MUTED))

    render(os.path.join(IMG, "monolith.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. inside.svg — один кремній родить R, C, транзистори тими самими шарами
# ════════════════════════════════════════════════════════════════════════════
def fig_inside():
    W, H = 700, 340
    f = []
    f.append(text(W / 2, 38, "Усе з одного кремнію — за один процес", size=15, bold=True))

    # підкладка-кремній унизу на всю ширину
    sx, sw_, sy, sh = 70, 560, 250, 46
    f.append(rect(sx, sy, sw_, sh, fill="#cfe0d6", stroke="#27ae60", sw=1.6, rx=4))
    f.append(text(sx + sw_ / 2, sy + sh / 2 + 4, "спільна кремнієва підкладка (один кристал)", size=12, color="#1f6f4f", bold=True))

    # три «деталі», вирощені на ній тими самими шарами
    bw, bh, top = 150, 86, 120
    spots = [(120, "Резистор", res_box, POS, "смужка кремнію\nіз заданим опором"),
             (335, "Конденсатор", cap_box, NEG, "два провідники\nкрізь тонкий оксид"),
             (550, "Транзистор", None, INK, "переходи в товщі\nлегованого кремнію")]
    for bxc, name, draw, col, note in spots:
        # колодязь до підкладки
        f.append(line(bxc, top + bh, bxc, sy, color="#9aa0a6", sw=1.4, dash="4 4"))
        if draw is res_box:
            f.append(res_box(bxc - bw / 2, top, bw, bh))
        elif draw is cap_box:
            f.append(cap_box(bxc - bw / 2, top, bw, bh))
        else:
            f.append(rect(bxc - bw / 2, top, bw, bh, fill="#fff", stroke=INK, sw=1.4, rx=3))
            f.append(npn_mini(bxc, top + bh / 2))
        f.append(text(bxc, top - 12, name, size=12, bold=True, color=col))
        f.append(mtext(bxc, sy + sh + 22, note.split("\n"), size=10, color=MUTED))

    render(os.path.join(IMG, "inside.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. matching.svg — абсолютне значення «гуляє», ВІДНОШЕННЯ сусідів — майже точне
# ════════════════════════════════════════════════════════════════════════════
def fig_matching():
    W, H = 700, 380
    f = []
    f.append(text(W / 2, 36, "Що погане в кремнії, а що — чудове", size=15, bold=True))

    # ── ЛІВА панель: абсолютне значення гуляє широко ──
    ax, ay, aw, ah = 70, 80, 250, 210
    f.append(rect(ax, ay, aw, ah, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    f.append(text(ax + aw / 2, ay + 24, "Абсолютне значення", size=13, bold=True, color=POS))
    f.append(text(ax + aw / 2, ay + 42, "погане: ±20 % від партії до партії", size=10, color=MUTED))
    # шкала «номінал» з широким розкидом
    base = ay + 120
    nom = ax + aw / 2
    f.append(line(ax + 20, base, ax + aw - 20, base, color=INK, sw=1.6))
    f.append(line(nom, base - 8, nom, base + 8, color=INK, sw=1.6))
    f.append(text(nom, base + 24, "10 кОм (номінал)", size=10, color=INK))
    # «справжні» значення розкидані широко
    import random
    random.seed(3)
    for dx in (-66, -40, -12, 22, 50, 70):
        f.append(circle(nom + dx, base - 30, 5, fill=POS, stroke=POS))
    f.append(text(nom, base - 52, "реально: 8…12 кОм", size=10, color=POS, bold=True))

    # ── ПРАВА панель: відношення сусідів точне ──
    bx, by, bw, bh = 380, 80, 250, 210
    f.append(rect(bx, by, bw, bh, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(bx + bw / 2, by + 24, "Відношення сусідів", size=13, bold=True, color=FIELD))
    f.append(text(bx + bw / 2, by + 42, "чудове: ~0.1 % між парою поряд", size=10, color=MUTED))
    # два майже однакові стовпчики
    c1 = bx + bw / 2 - 46
    c2 = bx + bw / 2 + 46
    h1 = 86
    for cx_, lab in ((c1, "R1"), (c2, "R2")):
        f.append(rect(cx_ - 18, by + 150 - h1, 36, h1, fill="#fff", stroke=FIELD, sw=1.8, rx=3))
        f.append(text(cx_, by + 168, lab, size=11, bold=True, color=INK))
    f.append(text(bx + bw / 2, by + 150 - h1 - 12, "R1 / R2 = 1.000 ± 0.001", size=11, bold=True, color=FIELD))
    # «пливуть разом» — стрілка
    f.append(arrow(c1, by + 150 - h1 - 26, c1, by + 150 - h1 - 40, color=MUTED, sw=1.6))
    f.append(arrow(c2, by + 150 - h1 - 26, c2, by + 150 - h1 - 40, color=MUTED, sw=1.6))
    f.append(text(bx + bw / 2, by + 150 - h1 - 48, "пливуть разом", size=9, color=MUTED))

    # підпис-висновок
    body, _, _ = textbox(W / 2, 350,
                         "Тому аналог на чипі будують на ВІДНОШЕННЯХ однакових сусідів,\nа не на точних номіналах: дзеркала, дільники, опори",
                         size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "matching.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. zoo.svg — і аналогові, і цифрові ІС — усі монолітні
# ════════════════════════════════════════════════════════════════════════════
def fig_zoo():
    W, H = 720, 330
    f = []
    f.append(text(W / 2, 36, "Усе це — інтегральні схеми", size=15, bold=True))

    # дві родини
    f.append(text(190, 74, "Аналогові (лінійні)", size=13, bold=True, color=NEG))
    f.append(text(190, 92, "працюють із суцільним сигналом", size=10, color=MUTED))
    f.append(text(540, 74, "Цифрові", size=13, bold=True, color=POS))
    f.append(text(540, 92, "працюють із нулями й одиницями", size=10, color=MUTED))

    f.append(line(360, 64, 360, 300, color="#e3e6ea", sw=1.4))

    analog = [(110, "ОП", "підсилювач"), (200, "ОПОРА", "еталон В"), (290, "ДЗЕРКАЛО", "копія струму")]
    digital = [(450, "ЛОГІКА", "вентилі"), (540, "MCU", "процесор"), (630, "ПАМ'ЯТЬ", "біти")]
    for cx_, lab, sub in analog:
        f.append(chip(cx_, 150, 64, 56, pins=3, label=lab, sub=sub))
    for cx_, lab, sub in digital:
        f.append(chip(cx_, 150, 64, 56, pins=3, label=lab, sub=sub))

    body, _, _ = textbox(W / 2, 250,
                         "Різні за призначенням — однакові за суттю: ціла схема, вирощена\nв одному кристалі кремнію. «Лінійна» чи «цифрова» — це про те, ЩО робить чип, а не з чого він",
                         size=11, color=INK, fill=FILL, stroke=MUTED)
    f.append(body)
    render(os.path.join(IMG, "zoo.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. pelgrom.svg — закон Пелгрома: σ(ΔP) спадає як 1/√площа (корінь = дорого)
# ════════════════════════════════════════════════════════════════════════════
def fig_pelgrom():
    import math
    W, H = 720, 400
    f = []
    f.append(text(W / 2, 34, "Неузгодження спадає як 1 / √(W·L)", size=15, bold=True))

    # осі
    ox, oy = 100, 320          # початок координат
    ax_w, ax_h = 520, 230
    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.6))          # X (площа)
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.6))          # Y (розкид)
    f.append(text(ox + ax_w - 6, oy + 26, "площа пари  W·L  →", size=11, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - ax_h + 4, "σ(ΔP)", size=11, color=INK, anchor="end"))
    f.append(text(ox - 14, oy - ax_h + 20, "розкид", size=10, color=MUTED, anchor="end"))

    # крива σ = A/√площа на сітці площ 1..16 (у відносних одиницях)
    amax = 16.0
    s_at = lambda a: 1.0 / math.sqrt(a)            # σ у частках від σ(площа=1)
    def X(a): return ox + (a / amax) * ax_w
    def Y(s): return oy - s * (ax_h - 16)          # s∈(0..1] від верху осі
    pts = []
    a = 1.0
    while a <= amax + 1e-6:
        pts.append((X(a), Y(s_at(a))))
        a += 0.25
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, FIELD))

    # ключові точки: площа ×1, ×4, ×16 → розкид 1, 1/2, 1/4
    marks = [(1.0, "×1", "розкид 1.0"), (4.0, "×4 площі", "½ розкиду"), (16.0, "×16 площі", "¼ розкиду")]
    for a_, la, lb in marks:
        x, y = X(a_), Y(s_at(a_))
        f.append(line(x, oy, x, y, color=MUTED, sw=1.0, dash="3 3"))
        f.append(line(ox, y, x, y, color=MUTED, sw=1.0, dash="3 3"))
        f.append(circle(x, y, 5, fill=FIELD, stroke=FIELD))
        f.append(text(x, oy + 16, la, size=10, color=INK, bold=True))
        f.append(text(min(x + 4, ox + ax_w - 4), y - 10, lb, size=10, color=FIELD, bold=True,
                      anchor="start" if a_ < amax else "end"))

    # формула в рамці
    body, _, _ = textbox(ox + 330, oy - ax_h + 36,
                         "σ(ΔP) = A_P / √(W·L)\nучетверо площі  →  удвічі менший розкид",
                         size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    # підпис про ціну кореня
    f.append(text(W / 2, 378, "корінь = дорого: ×10 точності коштує ×100 площі (кристал)",
                  size=11, color=POS))
    render(os.path.join(IMG, "pelgrom.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. centroid.svg — спільний центроїд (A B B A) зануляє лінійний градієнт
# ════════════════════════════════════════════════════════════════════════════
def fig_centroid():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 34, "Спільний центроїд: як скоротити градієнт по пластині", size=15, bold=True))

    # фон-градієнт (стрілка «параметр пливе вздовж пластини»)
    gx = 60
    f.append(arrow(gx, 300, gx + 600, 300, color=MUTED, sw=2))
    f.append(text(gx + 300, 322, "параметр процесу плавно пливе вздовж кристала →", size=11, color=MUTED))

    cA, cB = NEG, POS

    # ── ЛІВОРУЧ: наївно, два поряд ──
    f.append(text(190, 74, "Наївно: A та B поряд", size=13, bold=True, color=INK))
    nx, ny, cw, ch = 110, 110, 70, 110
    f.append(rect(nx, ny, cw, ch, fill="#eaf0fd", stroke=cA, sw=1.8, rx=4))
    f.append(text(nx + cw / 2, ny + ch / 2 + 6, "A", size=22, bold=True, color=cA))
    f.append(rect(nx + cw + 10, ny, cw, ch, fill="#fdecea", stroke=cB, sw=1.8, rx=4))
    f.append(text(nx + cw + 10 + cw / 2, ny + ch / 2 + 6, "B", size=22, bold=True, color=cB))
    # центри на різних позиціях градієнта
    xA = nx + cw / 2
    xB = nx + cw + 10 + cw / 2
    f.append(line(xA, ny + ch + 6, xA, 296, color=cA, sw=1.2, dash="3 3"))
    f.append(line(xB, ny + ch + 6, xB, 296, color=cB, sw=1.2, dash="3 3"))
    f.append(text((xA + xB) / 2, ny - 12, "центри різні → A і B ловлять різне", size=10, color=POS))

    # ── ПРАВОРУЧ: A B B A, спільний центр ──
    f.append(text(540, 74, "Центроїд: A B B A", size=13, bold=True, color=INK))
    bx, by, sw_, sh = 410, 110, 60, 110
    order = [("A", cA, "#eaf0fd"), ("B", cB, "#fdecea"), ("B", cB, "#fdecea"), ("A", cA, "#eaf0fd")]
    centers = {"A": [], "B": []}
    for i, (lab, col, fillc) in enumerate(order):
        x = bx + i * (sw_ + 6)
        f.append(rect(x, by, sw_, sh, fill=fillc, stroke=col, sw=1.8, rx=4))
        f.append(text(x + sw_ / 2, by + sh / 2 + 6, lab, size=18, bold=True, color=col))
        centers[lab].append(x + sw_ / 2)
    # спільний центр мас (середина) — однаковий для A і B
    mid = bx + (4 * (sw_ + 6) - 6) / 2
    f.append(line(mid, by + sh + 6, mid, 296, color=FIELD, sw=2.2))
    f.append(text(mid, by - 12, "центр маси A = центр маси B", size=10, color=FIELD, bold=True))

    # висновок
    body, _, _ = textbox(W / 2, 344,
                         "Звели центри обох деталей в одну точку — лінійний градієнт додає до A і B порівну й скорочується у відношенні",
                         size=11, color=INK, fill=FILL, stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "centroid.svg"), W, H, *f)


if __name__ == "__main__":
    fig_monolith()
    fig_inside()
    fig_matching()
    fig_zoo()
    fig_pelgrom()
    fig_centroid()
    print("OK: 6 фігур у", IMG)
