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


if __name__ == "__main__":
    fig_chain()
    fig_level_shift()
    print("figs done")
