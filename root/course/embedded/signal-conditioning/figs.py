# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def block(cx, cy, w, h, title, sub, fill=FILL, stroke=LINE):
    """Прямокутник-блок із заголовком (жирним) і підписом-функцією під ним."""
    x, y = cx - w / 2, cy - h / 2
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.8)
    out += text(cx, cy - 4, title, size=14, bold=True)
    if sub:
        out += mtext(cx, cy + 15, sub, size=11, color=MUTED, lh=1.15)
    return out


# ── Фігура 1: тракт кондиціонування як ланцюг ────────────────────────────────
def fig_chain():
    W, H = 940, 320
    f = []
    f.append(text(W / 2, 28, "Тракт кондиціонування: від давача до АЦП", size=17, bold=True))

    yc = 130
    bw, bh = 140, 80
    # позиції центрів п'яти блоків
    gap = 30
    total = 5 * bw + 4 * gap
    x0 = (W - total) / 2
    xs = [x0 + bw / 2]
    for _ in range(4):
        xs.append(xs[-1] + bw + gap)

    blocks = [
        ("Давач", "мкВ–мВ\nвисокий опір\nшум, біполярний", "#fdf3ea", "#b9770e"),
        ("Буфер", "розв'язує\nджерело\n×1", "#eaf0fd", NEG),
        ("Підсилювач\n+ зсув", "×K, у вікно\nближче\nдо давача", "#eafaf0", FIELD),
        ("Фільтр", "шум +\nантиаліасинг\nперед АЦП", "#eaf0fd", NEG),
        ("АЦП", "0…3.3 В\n12 біт\nчисло в код", "#f4f6f8", INK),
    ]
    # блоки малюємо вручну (заголовок може бути на 2 рядки)
    for (cx, (title, sub, fill, stroke)) in zip(xs, blocks):
        x, y = cx - bw / 2, yc - bh / 2
        f.append(rect(x, y, bw, bh, fill=fill, stroke=stroke, sw=1.8))
        tlines = title.split("\n")
        ty = yc - bh / 2 + 18
        f.append(mtext(cx, ty, tlines, size=14, bold=True, lh=1.1))
        f.append(mtext(cx, ty + (len(tlines)) * 15 + 2, sub, size=10.5, color=MUTED, lh=1.18))

    # стрілки між блоками
    for i in range(len(xs) - 1):
        x1 = xs[i] + bw / 2
        x2 = xs[i + 1] - bw / 2
        f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
                 % (x1, yc, x2 - 2, yc, INK))

    # нижня смуга-висновок
    f.append(fitbox(70, 232, W - 140, 62,
        "Порядок не випадковий: РОЗВ'ЯЗАТИ джерело → ПІДСИЛИТИ й поставити у вікно → ВІДФІЛЬТРУВАТИ перед АЦП.\n"
        "Правило: підсилюй якомога РАНІШЕ, псуй (додавай свій шум) якомога ПІЗНІШЕ.",
        size=13.5, fill="#f4f6f8", stroke=MUTED))
    render(os.path.join(OUT, "chain.svg"), W, H, *f)


# ── Фігура 2: зсув рівня — повертає втрачену половину сигналу ─────────────────
def fig_level_shift():
    W, H = 820, 360
    f = []
    f.append(text(W / 2, 28, "Зсув рівня саджає сигнал у вікно АЦП", size=17, bold=True))

    # дві панелі
    def panel(ox, title, offset_v, color):
        pw, ph = 300, 220
        oy = 300              # низ панелі (0 В)
        top = oy - ph        # верх панелі
        # вікно АЦП 0..3.3 В: показуємо як зелену смугу від 0 до верху
        vtop = 3.3
        def vy(v):           # напруга -> y
            return oy - (v / vtop) * ph
        # рамка вікна
        f.append(rect(ox, top, pw, ph, fill="#eafaf0", stroke=FIELD, sw=1.6))
        f.append(text(ox + 6, top - 8, "вікно АЦП 0…3.3 В", size=11, color=FIELD, anchor="start", bold=True))
        # вісь 0
        f.append(line(ox, vy(0), ox + pw, vy(0), INK, 1.6))
        f.append(text(ox - 6, vy(0) + 4, "0 В", size=11, anchor="end", color=MUTED))
        f.append(text(ox - 6, vy(3.3) + 4, "3.3", size=11, anchor="end", color=MUTED))
        # середина вікна
        f.append(line(ox, vy(1.65), ox + pw, vy(1.65), MUTED, 1, dash="4 4"))
        f.append(text(ox + pw + 4, vy(1.65) + 4, "1.65", size=10, anchor="start", color=MUTED))
        # синусоїда ±1 В навколо offset
        amp = 1.0
        pts = []
        N = 80
        for i in range(N + 1):
            t = i / N
            v = offset_v + amp * math.sin(2 * math.pi * 2 * t)
            px = ox + 10 + t * (pw - 20)
            py = vy(v)
            pts.append((px, py))
        d = "M " + " L ".join("%.1f %.1f" % p for p in pts)
        # частини, що ВИЙШЛИ за вікно (нижче 0), уже візуально обрізані рамкою — лишаємо як є
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, color))
        f.append(text(ox + pw / 2, top + 18, title, size=13, bold=True))

    panel(70, "навколо 0 В: пів-хвилі за кадром", 0.0, POS)
    panel(450, "+1.65 В: уся хвиля у вікні", 1.65, FIELD)

    # стрілка між панелями
    f.append('<line x1="375" y1="170" x2="445" y2="170" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>' % INK)
    f.append(text(410, 158, "+1.65 В", size=11, bold=True, color=NEG))
    f.append(text(W / 2, 345, "Форма не змінилась — сигнал лише піднято на середину вікна.", size=12, color=MUTED))
    render(os.path.join(OUT, "level-shift.svg"), W, H, *f)


# ── Фігура 3 (вставка hist): дві шкали — 3–15 psi і 4–20 мА — один родовід ────
def fig_live_zero():
    W, H = 820, 480
    f = []
    f.append(text(W / 2, 30, "Одна логіка, дві доби: 3–15 psi → 4–20 мА", size=17, bold=True))

    # Спільна геометрія двох вертикальних шкал.
    top = 78          # y повної шкали (верх стовпчика)
    bot = 330         # y живого нуля (низ робочого стовпчика)
    zero = 388        # y мертвого нуля (0 psi / 0 мА)

    def scale(cx, lo_lbl, hi_lbl, unit, color, zero_lbl):
        bw = 62
        x = cx - bw / 2
        # робоча смуга: живий нуль → повна шкала (кольорова)
        f.append(rect(x, top, bw, bot - top, fill="#eafaf0", stroke=color, sw=1.8))
        # зона відмови: нижче живого нуля до нуля (штрихована червона)
        f.append(rect(x, bot, bw, zero - bot, fill="#fdecea", stroke=POS, sw=1.4, rx=0))
        f.append(line(x, bot, x + bw, bot, POS, 2.2))     # межа живого нуля
        # підписи справа від стовпчика
        f.append(text(cx + bw / 2 + 10, top + 6, hi_lbl, size=13, anchor="start", bold=True, color=color))
        f.append(text(cx + bw / 2 + 10, top + 24, "повна шкала", size=10.5, anchor="start", color=MUTED))
        f.append(text(cx + bw / 2 + 10, bot + 5, lo_lbl, size=13, anchor="start", bold=True, color=POS))
        f.append(text(cx + bw / 2 + 10, bot + 22, "живий нуль", size=10.5, anchor="start", color=POS))
        f.append(text(cx + bw / 2 + 10, zero + 5, zero_lbl, size=12, anchor="start", color=MUTED))
        # підпис одиниці зверху
        f.append(text(cx, top - 14, unit, size=13, bold=True))
        # відношення 5:1 усередині смуги
        f.append(mtext(cx, (top + bot) / 2 - 6, ["робочий", "діапазон", "5 : 1"], size=11, color=MUTED, lh=1.25))

    scale(200, "3 psi", "15 psi", "Пневматика (з 1930-х)", "#b9770e", "0 psi — трубка лопнула")
    scale(560, "4 мА", "20 мА", "Струм (з 1950-х)", NEG, "0 мА — обрив дроту")

    # стрілка спадкоємності між шкалами
    f.append('<line x1="262" y1="204" x2="528" y2="204" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % INK)
    f.append(text(395, 194, "та сама ідея", size=12, bold=True))
    f.append(text(395, 222, "живий нуль + 5:1", size=11, color=MUTED))

    # нижня смуга-висновок (два рядки — щоб шрифт не падав нижче 8)
    f.append(fitbox(50, zero + 24, W - 100, 60,
        "Червона зона внизу — не «нуль шкали», а ВІДМОВА:\n"
        "справний контур туди не заходить, тож один погляд відрізняє «нуль» від «зламалося».",
        size=13, fill="#fdf4f2", stroke=POS))
    render(os.path.join(OUT, "live-zero.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chain()
    fig_level_shift()
    fig_live_zero()
    print("figs done")
