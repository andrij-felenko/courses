# -*- coding: utf-8 -*-
"""
SVG-фігури для 📜-вставки §3.3.8 — «Метастабільність: явище, в яке інженери
відмовлялися вірити» (Чейні й Молнар, 1973). Окремий генератор: головний
figs.py НЕ чіпаємо. Чистий Python без залежностей. Вивід → ./img/.

Стиль за AUTHORING §9: білий фон; «1» червоний, «0» синій; висновок/поле — зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції — копія спільного набору
розділу (щоб не залежати від головного figs.py).

Фігури (нумерація історії до теми — Рис. 3.3.8i.k):
  fig-16-8i-1-timeline.svg     — ланцюг від «не може бути» до «вимірюємо й приборкуємо»
  fig-16-8i-2-scope.svg        — що Чейні й Молнар побачили на осцилографі: «хвіст» розв'язань
  fig-16-8i-3-buridan.svg      — чому неминуче: кулька на вершині (принцип Бурідана)
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
PURP  = "#7a3da8"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 3.3.8i.1 — ланцюг: від «не може бути» до «вимірюємо й приборкуємо» ──
def fig_timeline():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 30, "Дорога одного «неможливого» явища: від заперечення до інженерної норми",
              17, INK, "middle", "bold")

    # горизонтальна вісь часу
    ax0, ax1, ay = 70, 810, 95
    s += arrow(ax0, ay, ax1, ay, INK, 2.4)
    s += text(ax1, ay - 10, "час", 13, INK, "end", style="italic")

    # вузли: (x, рік, заголовок, рядки, колір)
    nodes = [
        (140, "1950–60-ті", "Перші чутки", ["синхронні машини", "інколи «глючать»", "— списують на шум"], GREY),
        (320, "1966", "Перші виміри", ["Чейні: «glitch", "phenomenon»; Кетт", "ловить аномалію"], BLUE),
        (510, "1973", "Чейні й Молнар", ["осцилограф показує", "«хвіст» зависань —", "це РЕАЛЬНО"], RED),
        (700, "1981", "Доказ неминучості", ["Маріно: жодна схема", "не уникне / не розв'яже /", "не виявить надійно"], PURP),
    ]
    for x, yr, ttl, lines, col in nodes:
        s += line(x, ay, x, ay + 14, col, 2)
        s += circle(x, ay, 7, "#fff", col, 3)
        s += text(x, ay - 14, yr, 14, col, "middle", "bold")
        # картка
        bw, bh = 168, 92
        bx, by = x - bw / 2, ay + 28
        s += rect(bx, by, bw, bh, "#fafafa", col, 1.8, 8)
        s += text(x, by + 22, ttl, 13.5, col, "middle", "bold")
        for i, ln in enumerate(lines):
            s += text(x, by + 42 + i * 16, ln, 11, INK, "middle")

    # підсумкова смуга «сьогодні»
    by2 = 300
    s += rect(70, by2, 740, 64, "#eef7f0", GREEN, 2, 10)
    s += text(90, by2 + 26, "Сьогодні — інженерна норма:", 14, GREEN, "start", "bold")
    s += text(90, by2 + 48,
              "будь-який асинхронний вхід заводять у логіку через СИНХРОНІЗАТОР; надійність рахують через MTBF.",
              13, INK, "start")

    # стрічка-висновок
    s += text(W / 2, 420,
              "Спільна нитка: спершу — «такого не буває», потім — «бачимо на екрані», далі — «доведено, що неминуче»,",
              13, INK, "middle", style="italic")
    s += text(W / 2, 440,
              "і нарешті — «приборкуємо ймовірнісно». Класична доля відкриття, що суперечить «здоровому глузду».",
              13, INK, "middle", style="italic")
    save("fig-16-8i-1-timeline.svg", s)


# ── Рис. 3.3.8i.2 — що побачили на осцилографі ──
def fig_scope():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 30, "Що Чейні й Молнар побачили на осцилографі: «хвіст» розв'язань",
              17, INK, "middle", "bold")

    # ── ліворуч: установка ──
    s += text(70, 66, "Установка вимірювання", 14, INK, "start", "bold")
    # тригер
    fx, fy, fw, fh = 90, 90, 120, 80
    s += rect(fx, fy, fw, fh, "#fafafa", INK, 2, 6)
    s += text(fx + fw / 2, fy + 30, "тригер", 13, INK, "middle", "bold")
    s += text(fx + fw / 2, fy + 50, "(D-латч)", 11, GREY, "middle")
    # вхід D — навмисно з'їжджає на фронт
    s += arrow(fx - 46, fy + 22, fx, fy + 22, BLUE, 2)
    s += text(fx - 50, fy + 18, "D", 13, BLUE, "end", "bold")
    s += text(fx - 50, fy + 34, "(зсуваємо", 9.5, GREY, "end")
    s += text(fx - 50, fy + 46, "до фронту)", 9.5, GREY, "end")
    # такт
    s += arrow(fx - 46, fy + 58, fx, fy + 58, RED, 2)
    s += text(fx - 50, fy + 62, "CLK", 12, RED, "end", "bold")
    # вихід Q → на осцилограф
    s += arrow(fx + fw, fy + 40, fx + fw + 46, fy + 40, INK, 2)
    s += text(fx + fw + 50, fy + 36, "Q →", 12, INK, "start", "bold")
    s += text(fx + fw + 50, fy + 52, "осцилограф", 11, GREY, "start")
    s += text(90, 210, "Запуск розгортки — від фронту такту;", 11.5, INK, "start")
    s += text(90, 226, "багато прогонів накладають на екран.", 11.5, INK, "start")

    # ── праворуч: екран осцилографа з накладеними слідами ──
    ox, oy, ow, oh = 360, 80, 460, 250
    s += rect(ox, oy, ow, oh, "#0b1410", "#0b1410", 2, 6)  # темний екран
    # рівні
    yhi, ylo = oy + 40, oy + oh - 40
    ymid = (yhi + ylo) / 2
    for yy, lab in [(yhi, "VOH (1)"), (ylo, "VOL (0)")]:
        s += line(ox + 10, yy, ox + ow - 10, yy, "#2e5d3e", 1, "4 4")
    s += line(ox + 10, ymid, ox + ow - 10, ymid, "#7a5a2a", 1, "2 4")
    s += text(ox + ow - 14, yhi - 6, "1", 11, "#6fdf95", "end", "bold")
    s += text(ox + ow - 14, ylo + 16, "0", 11, "#7fb6ff", "end", "bold")
    s += text(ox + 14, ymid - 6, "поріг", 10, "#d9b46a", "start")

    # момент фронту
    xf = ox + 70
    s += line(xf, oy + 12, xf, oy + oh - 12, "#c84", 1.4, "3 3")
    s += text(xf, oy + oh - 6, "фронт", 10, "#e0a85a", "middle")

    GHI = "#6fdf95"
    # сліди, що швидко вирішилися (норма) — у 1 і в 0
    import math
    def tail_to(level, t_res, col, wln=2.0):
        # від xf тримається ~ymid, тоді експоненційно тікає до level після t_res
        pts = [(xf, ymid)]
        x = xf
        steps = 60
        span = ox + ow - 16 - xf
        for i in range(1, steps + 1):
            x = xf + span * i / steps
            tt = (x - xf) / span  # 0..1 уздовж екрана
            if tt < t_res:
                y = ymid + (1 if level == "lo" else -1) * 1.5  # майже плаский «горб»
            else:
                k = (tt - t_res) / max(1e-3, (1 - t_res))
                target = ylo if level == "lo" else yhi
                y = ymid + (target - ymid) * (1 - math.exp(-3.2 * k))
            pts.append((x, y))
        return polyline(pts, col, wln)

    # пучок «нормальних» розв'язань (різний час, але швидко)
    for tr in (0.06, 0.10, 0.14):
        s += tail_to("hi", tr, GHI, 1.6)
        s += tail_to("lo", tr, GHI, 1.6)
    # кілька «довгих хвостів» — метастабільні зависання
    s += tail_to("hi", 0.34, "#f2e24a", 2.2)
    s += tail_to("lo", 0.30, "#f2e24a", 2.2)
    s += tail_to("hi", 0.55, "#f06a4a", 2.6)
    s += tail_to("lo", 0.50, "#f06a4a", 2.6)
    # один, що завис аж до краю
    long_pts = [(xf, ymid)]
    span = ox + ow - 16 - xf
    for i in range(1, 61):
        x = xf + span * i / 60
        long_pts.append((x, ymid - 2 + (i / 60) * 3))
    s += polyline(long_pts, "#ff4d3a", 2.8)
    s += text(ox + ow - 16, ymid + 18, "застряг до кінця розгортки!", 10.5, "#ff8a78", "end", "bold")

    # легенда під екраном
    ly = oy + oh + 26
    s += rect(ox, ly, ow, 18, "none", "none")
    s += line(ox + 6, ly, ox + 30, ly, GHI, 2.4)
    s += text(ox + 36, ly + 4, "швидко в 0/1 (норма)", 11, INK, "start")
    s += line(ox + 210, ly, ox + 234, ly, "#d8c43e", 2.4)
    s += text(ox + 240, ly + 4, "довший хвіст", 11, INK, "start")
    s += line(ox + 350, ly, ox + 374, ly, "#f06a4a", 2.6)
    s += text(ox + 380, ly + 4, "метастабільне зависання", 11, INK, "start")

    # підсумок
    s += rect(70, 380, 740, 64, "#fdf3f1", RED, 1.8, 10)
    s += text(90, 404, "Висновок експерименту:", 13.5, RED, "start", "bold")
    s += text(90, 426,
              "час розв'язання НЕ обмежений зверху — інколи слід «висить» біля порога як завгодно довго. Це й заперечували.",
              12.5, INK, "start")
    save("fig-16-8i-2-scope.svg", s)


# ── Рис. 3.3.8i.3 — чому неминуче: принцип Бурідана (кулька на вершині) ──
def fig_buridan():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 30, "Чому метастабільність неминуча: принцип Бурідана (кулька на вершині)",
              17, INK, "middle", "bold")

    # рельєф з двома ямами і горбом
    def hill(cx, cy):
        # повертає шлях рельєфу і координати вершини
        return cx, cy
    gx0, gx1 = 80, 470
    base = 300
    # крива: ліва яма — горб — права яма
    d = (f"M {gx0},{base} "
         f"C {gx0+70},{base} {gx0+95},{base-12} {gx0+120},{base-20} "
         f"C {gx0+150},{base-30} {gx0+170},{base-118} {gx0+195},{base-118} "  # ліва стінка до вершини
         f"C {gx0+220},{base-118} {gx0+240},{base-30} {gx0+270},{base-20} "
         f"C {gx0+295},{base-12} {gx0+320},{base} {gx1},{base}")
    s += path(d, INK, 2.6)
    # дно ям (заливка-натяк)
    s += text(gx0 + 60, base + 26, "стан «0»", 13, BLUE, "middle", "bold")
    s += text(gx1 - 60, base + 26, "стан «1»", 13, RED, "middle", "bold")
    topx, topy = gx0 + 195, base - 118
    s += text(topx, topy - 50, "метастабільна", 12.5, PURP, "middle", "bold")
    s += text(topx, topy - 34, "вершина", 12.5, PURP, "middle", "bold")

    # кулька на вершині
    s += circle(topx, topy - 11, 11, AMBER, INK, 2)
    s += line(topx, topy - 22, topx, topy - 40, PURP, 1.4, "3 3")

    # стрілки «впаде ліворуч / праворуч / або балансує»
    s += arrow(topx - 16, topy + 4, topx - 70, base - 40, BLUE, 2)
    s += arrow(topx + 16, topy + 4, topx + 70, base - 40, RED, 2)
    s += text(topx, topy + 84, "…а балансувати може", 11, GREY, "middle", style="italic")
    s += text(topx, topy + 100, "як завгодно довго", 11, GREY, "middle", style="italic")

    # права колонка: аргумент неперервності
    cx = 540
    s += rect(cx, 70, 300, 300, "#faf7fc", PURP, 1.8, 10)
    s += text(cx + 150, 96, "Аргумент неперервності", 14, PURP, "middle", "bold")
    bullets = [
        "Початковий стан схеми плавно",
        "залежить від миті приходу даних",
        "відносно фронту (це число!).",
        "",
        "Один бік цього числа → впаде в 0,",
        "інший → впаде в 1.",
        "",
        "Між «0» і «1» немає стрибка —",
        "отже існує проміжне положення,",
        "де кулька не падає ні туди, ні",
        "сюди скільки завгодно довго.",
    ]
    for i, b in enumerate(bullets):
        col = INK
        w = "normal"
        if "впаде в 0" in b:
            col = BLUE
        if "впаде в 1" in b:
            col = RED
        s += text(cx + 16, 124 + i * 21, b, 12, col, "start", w)

    # нижня смуга-висновок
    s += rect(80, 386, 760, 34, "#f1eef6", PURP, 1.6, 8)
    s += text(W / 2, 408,
              "Тож НЕ ІСНУЄ схеми з гарантованим часом рішення (Маріно, 1981) — метастабільність можна лише зробити рідкісною.",
              12.5, PURP, "middle", "bold")
    save("fig-16-8i-3-buridan.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_scope()
    fig_buridan()
    print("done.")
