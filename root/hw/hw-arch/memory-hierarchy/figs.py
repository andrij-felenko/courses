# -*- coding: utf-8 -*-
"""Фігури до теми «Ієрархія пам'яті».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Рамки з текстом — лише через textbox()/fitbox() (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_pyramid():
    """Піраміда рівнів: угорі вузька й швидка (регістри), донизу — ширша й повільніша.
    Праворуч — дві осі-стрілки: швидше/дорожче вгору, більше/дешевше вниз."""
    W, H = 820, 470
    f = []
    cx = 280
    apex_y, base_y = 70, 410
    half_top, half_bot = 60, 230
    # рівні згори вниз: (підпис, типова латентність, типовий обсяг, заливка, обведення)
    levels = [
        ("Регістри",            "~0.3 нс",  "сотні байтів", "#fdecea", POS),
        ("Кеш L1 / L2 / L3",    "1–40 нс",  "кБ — десятки МБ", "#fff1da", "#b8860b"),
        ("Оперативна (DRAM)",   "60–100 нс", "ГБ",           "#eafaf1", FIELD),
        ("Накопичувач (SSD/HDD)", "0.1–10 мс", "ТБ",         "#eef4ff", NEG),
    ]
    n = len(levels)
    band_h = (base_y - apex_y) / n
    for i, (name, lat, cap, fill, stroke) in enumerate(levels):
        y0 = apex_y + i * band_h
        y1 = y0 + band_h
        t0 = i / n
        t1 = (i + 1) / n
        w0 = half_top + (half_bot - half_top) * t0
        w1 = half_top + (half_bot - half_top) * t1
        pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            cx - w0, y0, cx + w0, y0, cx + w1, y1, cx - w1, y1)
        f.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (pts, fill, stroke))
        ymid = (y0 + y1) / 2
        f.append(text(cx, ymid - 6, name, size=15, bold=True))
        f.append(text(cx, ymid + 14, lat + "   •   " + cap, size=12, color=MUTED))
    # вершина-трикутник домальована заливкою верхнього рівня вже є; контур піраміди
    # Осі-стрілки праворуч
    ax = cx + half_bot + 40
    f.append(arrow(ax, base_y, ax, apex_y, color=POS, sw=2))
    f.append(text(ax + 12, (apex_y + base_y) / 2 - 30, "швидше", size=13, color=POS,
                  anchor="start"))
    f.append(text(ax + 12, (apex_y + base_y) / 2 - 12, "дорожче / біт", size=13,
                  color=POS, anchor="start"))
    bx = ax + 130
    f.append(arrow(bx, apex_y, bx, base_y, color=NEG, sw=2))
    f.append(text(bx + 12, (apex_y + base_y) / 2 + 14, "більше", size=13, color=NEG,
                  anchor="start"))
    f.append(text(bx + 12, (apex_y + base_y) / 2 + 32, "дешевше / біт", size=13,
                  color=NEG, anchor="start"))
    # підпис до процесора над вершиною
    f.append(text(cx, apex_y - 18, "← ближче до ядра", size=13, color=INK))
    render(os.path.join(OUT, 'pyramid.svg'), W, H, *f)


def fig_locality():
    """Чому ієрархія працює: одна адреса тягне СУСІДІВ у швидкий рівень (просторова),
    і той самий блок читають ще раз скоро (часова). Стрічка пам'яті + вікно-блок."""
    W, H = 740, 340
    f = []
    # Стрічка комірок пам'яті
    x0, y0 = 60, 120
    cw, ch = 46, 46
    n = 12
    hot = {4, 5, 6, 7}   # блок, що поїхав у кеш
    asked = 5            # реально запитана адреса
    for i in range(n):
        x = x0 + i * cw
        if i in hot:
            fill, stroke = ("#fff1da", "#b8860b")
        else:
            fill, stroke = (FILL, LINE)
        f.append(rect(x, y0, cw, ch, fill=fill, stroke=stroke, sw=1.5, rx=4))
        f.append(text(x + cw / 2, y0 + ch / 2 + 5, str(0x10 + i), size=12, color=MUTED))
    # позначка реально запитаної адреси
    ax = x0 + asked * cw + cw / 2
    f.append(arrow(ax, y0 - 34, ax, y0 - 2, color=INK, sw=2))
    f.append(text(ax, y0 - 42, "ядро попросило 1 адресу", size=13, bold=True))
    # дужка над блоком, що поїхав цілком
    bx0 = x0 + min(hot) * cw
    bx1 = x0 + (max(hot) + 1) * cw
    by = y0 + ch + 22
    f.append(line(bx0, by, bx1, by, color="#b8860b", sw=2))
    f.append(line(bx0, by, bx0, by - 8, color="#b8860b", sw=2))
    f.append(line(bx1, by, bx1, by - 8, color="#b8860b", sw=2))
    f.append(text((bx0 + bx1) / 2, by + 20, "цілий блок (рядок кешу) їде у швидкий рівень",
                  size=13, color="#b8860b"))
    # Дві стрілки-висновки
    f.append(fitbox(70, 250, 290, 64,
                    "Просторова близькість:\nсусідні адреси знадобляться скоро",
                    size=13, fill="#eafaf1", stroke=FIELD))
    f.append(fitbox(390, 250, 290, 64,
                    "Часова близькість:\nту саму адресу прочитають ще раз",
                    size=13, fill="#eef4ff", stroke=NEG))
    render(os.path.join(OUT, 'locality.svg'), W, H, *f)


def fig_lookup():
    """Шлях запиту: ядро питає L1 → влучив? віддав за такти. Схибив → униз по рівнях,
    кожен дорожчий. Показує, чому середній час залежить від частки влучань."""
    W, H = 760, 360
    f = []
    # ланцюг рівнів зліва направо
    boxes = [
        ("Ядро",     FILL,      INK),
        ("L1",       "#fdecea", POS),
        ("L2 / L3",  "#fff1da", "#b8860b"),
        ("DRAM",     "#eafaf1", FIELD),
        ("SSD/HDD",  "#eef4ff", NEG),
    ]
    bw, bh = 110, 62
    gap = 30
    x = 40
    y = 80
    centers = []
    for name, fill, stroke in boxes:
        f.append(fitbox(x, y, bw, bh, name, size=15, fill=fill, stroke=stroke, bold=True))
        centers.append(x + bw / 2)
        x += bw + gap
    # стрілки «схибив → униз» уздовж ланцюга
    for i in range(len(boxes) - 1):
        xa = centers[i] + bw / 2
        xb = centers[i + 1] - bw / 2
        f.append(arrow(xa, y + bh / 2, xb, y + bh / 2, color=INK, sw=2))
    f.append(text((centers[1] + centers[-1]) / 2, y - 18,
                  "схибив тут → шукай нижче (повільніше й дорожче)", size=13, color=MUTED))
    # «влучив → назад угору» пунктиром
    for i in range(1, len(boxes)):
        f.append(line(centers[i], y + bh + 4, centers[i], y + bh + 30,
                      color=FIELD, sw=1.5, dash="4 3"))
    f.append(line(centers[1], y + bh + 30, centers[-1], y + bh + 30,
                  color=FIELD, sw=1.5, dash="4 3"))
    f.append(line(centers[1], y + bh + 30, centers[0], y + bh + 30,
                  color=FIELD, sw=1.5, dash="4 3"))
    f.append(line(centers[0], y + bh + 4, centers[0], y + bh + 30,
                  color=FIELD, sw=1.5, dash="4 3"))
    f.append(text(centers[0], y + bh + 48, "влучив → дані повертаються ядру",
                  size=13, color=FIELD, anchor="start"))
    # формула середнього часу
    f.append(fitbox(140, y + bh + 90, 480, 56,
                    "середній час ≈ влучань·(швидко) + промахів·(повільно)",
                    size=14, fill="#fbfcfe", stroke=INK, bold=True))
    render(os.path.join(OUT, 'lookup.svg'), W, H, *f)


def fig_hist_timeline():
    """Вставка «Історія»: часова смуга народження поняття.
    Ідею висловили 1946-го — задовго до того, як залізо змогло її втілити (1965/1968).
    Позиції подій рівномірні — це схема послідовності, не масштаб років."""
    W, H = 900, 380
    f = []
    axis_y = 130
    x0, x1 = 40, W - 30
    f.append(line(x0, axis_y, x1, axis_y, color=INK, sw=2.5))
    f.append(arrow(x1 - 2, axis_y, x1 + 2, axis_y, color=INK, sw=2.5))

    events = [
        ("1946", ["Беркс · Голдстайн", "· фон Нейман:", "«ієрархія пам'ятей»"],
         "ідея", NEG),
        ("1965", ["Вілкс:", "«slave memory»", "— перший кеш"],
         "реалізація", FIELD),
        ("1968–69", ["IBM 360/85:", "кеш у продажу;", "слово «cache»"],
         "назва", "#b8860b"),
        ("1995", ["Вульф · Маккі:", "«стіна пам'яті»"],
         "тривога", POS),
    ]
    n = len(events)
    halfw = 92                       # піввисота картки → тримаємо вузли всередині
    left = x0 + halfw + 6
    right = x1 - halfw - 6
    xs = [left + (right - left) * i / (n - 1) for i in range(n)]

    for (lab, lines, tag, col), x in zip(events, xs):
        f.append(line(x, axis_y - 8, x, axis_y + 8, color=INK, sw=2))
        f.append(circle(x, axis_y, 7, fill=col, stroke=INK, sw=2))
        f.append(text(x, axis_y + 30, lab, size=15, color=INK, bold=True))
        f.append(text(x, axis_y + 48, tag, size=12, color=MUTED, italic=True))
        bx, by, bw, bh = x - halfw, axis_y - 96, 2 * halfw, 76
        f.append(fitbox(bx, by, bw, bh, "\n".join(lines),
                        size=13, fill="#f4f6f8", stroke=col, sw=2))
        f.append(line(x, by + bh, x, axis_y - 9, color=col, sw=1.5, dash="3 3"))

    f.append(text(W / 2, H - 22,
                  "Ідею висловили за десятиліття до того, як залізо змогло її втілити.",
                  size=13, color=INK, italic=True))
    render(os.path.join(OUT, 'timeline.svg'), W, H, *f,
           title="Як народжувалася ієрархія пам'яті")


def fig_hist_scissors():
    """Вставка «Історія»: ножиці швидкодії — логіка «стіни пам'яті».
    Дві експоненти з різним нахилом: ядро круто вгору, пам'ять мляво; розрив
    між ними росте експоненційно. Шкала Y — логарифмічна (схема, не дані)."""
    import math
    W, H = 720, 430
    f = []
    ox, oy = 90, H - 80          # початок координат
    ax, ay = W - 40, 70          # кінці осей
    f.append(line(ox, oy, ox, ay, color=INK, sw=2))
    f.append(arrow(ox, oy, ox, ay - 4, color=INK, sw=2))
    f.append(line(ox, oy, ax, oy, color=INK, sw=2))
    f.append(arrow(ox, oy, ax - 4, oy, color=INK, sw=2))

    f.append(text(ox - 12, ay - 20, "швидкодія", size=13, color=INK,
                  anchor="middle", bold=True))
    f.append(text(ox - 12, ay - 4, "(лог. шкала)", size=11, color=MUTED,
                  anchor="middle"))
    f.append(text((ox + ax) / 2, oy + 44, "рік", size=13, color=INK, bold=True))
    f.append(text(ox, oy + 22, "1980", size=11, color=MUTED))
    f.append(text(ax - 34, oy + 22, "→ сьогодні", size=11, color=MUTED))

    # Спільний масштаб для ОБОХ кривих: ядро (крута експонента) сягає верху,
    # пам'ять (полога) лишається низько — тому вони РОЗХОДЯТЬСЯ, а не сходяться.
    top = oy - ay - 26                        # висота, яку заповнює найкрутіша крива
    core_rate, mem_rate = 2.7, 0.75
    scale = top / (math.exp(core_rate) - 1)   # так, щоб ядро дійшло до самого верху
    endx = ox + (ax - ox - 24)

    def curve(rate, col, sw=3):
        pts = []
        for i in range(0, 101):
            t = i / 100.0
            x = ox + (ax - ox - 24) * t
            y = oy - scale * (math.exp(rate * t) - 1)
            pts.append("%.1f,%.1f" % (x, y))
        return ('<polyline points="%s" fill="none" stroke="%s" '
                'stroke-width="%.1f"/>' % (" ".join(pts), col, sw))

    f.append(curve(core_rate, POS))   # ядро — круто вгору
    f.append(curve(mem_rate, NEG))    # пам'ять — мляво, лишається низько

    ycore = oy - scale * (math.exp(core_rate) - 1)
    ymem = oy - scale * (math.exp(mem_rate) - 1)
    f.append(text(endx - 4, ycore + 4, "швидкодія ядра", size=13, color=POS,
                  anchor="end", bold=True))
    f.append(text(endx - 4, ymem + 24, "швидкодія пам'яті", size=13, color=NEG,
                  anchor="end", bold=True))

    # розрив, що росте — двонапрямна вертикальна стрілка між кривими праворуч
    gx = endx + 4
    f.append(arrow(gx, ymem, gx, ycore, color=MUTED, sw=1.8))
    f.append(arrow(gx, ycore, gx, ymem, color=MUTED, sw=1.8))
    f.append(fitbox(gx - 178, (ycore + ymem) / 2 - 22, 150, 44,
                    "розрив росте\nекспоненційно", size=12,
                    fill="#fff9e6", stroke=MUTED, sw=1.5))

    f.append(text(W / 2, H - 20,
                  "Різниця двох експонент теж експонента — ось чому «стіна» неминуча.",
                  size=13, color=INK, italic=True, anchor="middle"))
    render(os.path.join(OUT, 'scissors.svg'), W, H, *f,
           title="Ножиці швидкодії: логіка «стіни пам'яті»")


if __name__ == '__main__':
    fig_pyramid()
    fig_locality()
    fig_lookup()
    fig_hist_timeline()
    fig_hist_scissors()
    print("OK: figures written to", OUT)
