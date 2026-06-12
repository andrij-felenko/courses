# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для 🧮-вставки «Закон Мура як графік» (до §3.10.8, Модуль 3).
Окремий скрипт вставки (головний figs.py розділу не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Імена файлів — з токеном "r10-s8m", щоб не конфліктувати з фігурами теми й сусідів.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif; єдиний вигляд з рештою розділів.
Нумерація підписів у тексті — Рис. 3.10.8m.k (на диску імена не перенумеровуються).
Хелпери — копія зі спільного набору розділу (за §9 кожен скрипт самодостатній).
"""
import math
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
PURPLE = "#7a3ea8"
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         AMBER: "aAmber", PURPLE: "aPurple"}


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


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.8m.1 — закон Мура як ПРЯМА на лог-осі.
# По осі X — рік (1971..2023), по осі Y — log10 числа транзисторів.
# Експонента (подвоєння кожні ~2 роки) перетворюється на пряму; реальні чіпи
# лягають уздовж неї. Праворуч — лінійна вісь у тих самих координатах, де та
# сама крива «злітає в небо»: одна функція, дві осі, дві історії.
# ═══════════════════════════════════════════════════════════════════════════
def fig_moore_line():
    W, H = 940, 580
    s = header(W, H)
    s += text(W / 2, 32, "Закон Мура: експонента, випрямлена логарифмічною віссю",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 54, "подвоєння числа транзисторів кожні ~2 роки — це стала кутова швидкість угору, тож на лог-осі вийде пряма",
              12.3, GREY, "middle", style="italic")

    # ── опорні чіпи: (рік, транзисторів) — порядок величини, ілюстративно ──
    chips = [
        (1971, 2.3e3,   "ранній МП"),
        (1978, 2.9e4,   ""),
        (1989, 1.2e6,   ""),
        (1999, 9.5e6,   ""),
        (2006, 2.9e8,   ""),
        (2012, 1.4e9,   ""),
        (2017, 1.9e10,  ""),
        (2023, 8.0e10,  "сучасний SoC"),
    ]

    # ── ЛІВА панель: лог-вісь (пряма) ──
    ax, ay = 78, 92
    aw, ah = 470, 388
    y0, y1 = 1971, 2024
    lo, hi = 3.0, 11.0          # log10 діапазон (10³ .. 10¹¹)

    def px(year):
        return ax + aw * (year - y0) / (y1 - y0)

    def py_log(n):
        return ay + ah * (1 - (math.log10(n) - lo) / (hi - lo))

    s += line(ax, ay, ax, ay + ah, GREY, 1.6)
    s += line(ax, ay + ah, ax + aw, ay + ah, GREY, 1.6)
    s += text(ax + aw / 2, ay - 14, "Лог-вісь: рівний крок = ×10", 13.5, BLUE, "middle", "bold")
    # сітка Y — степені десятки
    labels = {3: "10³", 4: "10⁴", 5: "10⁵", 6: "10⁶ (1 млн)",
              7: "10⁷", 8: "10⁸", 9: "10⁹ (1 млрд)", 10: "10¹⁰", 11: "10¹¹"}
    for e in range(3, 12):
        yg = ay + ah * (1 - (e - lo) / (hi - lo))
        s += line(ax, yg, ax + aw, yg, FAINT, 1.0)
        s += text(ax - 8, yg + 4, labels[e], 10.5, GREY, "end")
    # сітка X — роки
    for yr in range(1971, 2025, 13):
        xg = px(yr)
        s += line(xg, ay + ah, xg, ay + ah + 5, GREY, 1.2)
        s += text(xg, ay + ah + 20, f"{yr}", 11, GREY, "middle")
    s += text(ax + aw / 2, ay + ah + 42, "рік", 12.5, INK, "middle")

    # ідеальна пряма «подвоєння за 2 роки» через першу точку
    n_start = chips[0][1]
    def ideal(year):
        return n_start * (2.0 ** ((year - y0) / 2.0))
    s += polyline([(px(y0), py_log(ideal(y0))), (px(y1), py_log(min(ideal(y1), 10 ** hi)))],
                  AMBER, 2.2, "6 4")
    s += text(px(2007) + 4, py_log(ideal(2007)) - 8,
              "× 2 кожні 2 роки", 11, AMBER, "start", "bold")

    # реальні точки + з'єднувальна лінія
    pts = [(px(y), py_log(n)) for y, n, _ in chips]
    s += polyline(pts, BLUE, 2.6)
    for (y, n, lab), (xg, yg) in zip(chips, pts):
        s += circle(xg, yg, 4.5, BLUE, BLUE, 0)
        if lab:
            s += text(xg, yg + (18 if y == y0 else -10), lab, 10, INK,
                      "start" if y == y0 else "end", "bold")
    s += text(ax + 6, ay + 16, "пряма ⇒ стала швидкість зростання", 11, BLUE, "start")

    # ── ПРАВА панель: лінійна вісь (та сама функція) ──
    bx, by = 612, 92
    bw, bh = 300, 388
    s += line(bx, by, bx, by + bh, GREY, 1.6)
    s += line(bx, by + bh, bx + bw, by + bh, GREY, 1.6)
    s += text(bx + bw / 2, by - 14, "Лінійна вісь: той самий ряд", 13.5, RED, "middle", "bold")
    n_top = chips[-1][1]
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        yg = by + bh * (1 - frac)
        s += line(bx, yg, bx + bw, yg, FAINT, 1.0)
        s += text(bx - 8, yg + 4, f"{frac * n_top / 1e9:.0f}", 10, GREY, "end")
    s += text(bx - 8, by - 2, "млрд", 9.5, GREY, "end")

    def bpx(year):
        return bx + bw * (year - y0) / (y1 - y0)

    def bpy_lin(n):
        return by + bh * (1 - n / n_top)

    bpts = [(bpx(y), bpy_lin(n)) for y, n, _ in chips]
    s += polyline(bpts, RED, 2.6)
    for (y, n, lab), (xg, yg) in zip(chips, bpts):
        s += circle(xg, yg, 4.0, RED, RED, 0)
    for yr in (1971, 2000, 2023):
        s += text(bpx(yr), by + bh + 20, f"{yr}", 10.5, GREY, "middle")
    # пояснення: до 2005 «нічого не видно», бо все притиснуте до нуля
    s += line(bpx(1971), bpy_lin(0) - 1, bpx(2005), bpy_lin(0) - 1, GREY, 1.4, "3 3")
    s += text(bpx(1990), by + bh - 16,
              "перші 30 років злиплися біля нуля —", 10, GREY, "middle")
    s += text(bpx(1990), by + bh - 4,
              "лінійна вісь ховає експоненту", 10, GREY, "middle")
    s += text(bpx(2019), bpy_lin(n_top) + 16, "«стіна»", 10.5, RED, "middle", "bold")

    # підсумкова стрічка
    s += rect(ax, H - 32, W - 2 * ax + 0, 22, "#eef3fb", BLUE, 0, 6)
    s += text(W / 2, H - 17,
              "Одна й та сама крива. Лог-вісь випрямляє експоненту в пряму й робить нахил (темп подвоєння) видимим оком.",
              11.5, INK, "middle")
    save("fig-r10-s8m-1-moore-line.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.8m.2 — масштабування Деннарда як «безкоштовний обід» і його кінець.
# Дві ери на одній часовій осі. Зліва (до ~2005): крок техпроцесу ×0.7 по
# лінійному розміру → площа ×0.5, ще й напруга падає, тож потужність на мм²
# лишається СТАЛОЮ, а частота вільно росте. Справа: напруга вперлася в поріг
# (≈1 В) і витоки — щільність потужності полізла вгору («power wall»),
# частота стала на місці. Це і є «злам» закону Мура зсередини.
# ═══════════════════════════════════════════════════════════════════════════
def fig_dennard():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 32, "Масштабування Деннарда: чому зменшення транзистора колись було «безкоштовним» — і чому перестало",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "правила Деннарда (1974): лінійний розмір ×0.7 за крок → площа ×0.5, напруга ×0.7 — і потужність на одиницю площі НЕ росте",
              11.8, GREY, "middle", style="italic")

    # вертикаль-вододіл «~2005»
    split = 472
    s += line(split, 80, split, 470, INK, 1.6, "5 4")
    s += text(split, 74, "≈ 2005", 12.5, INK, "middle", "bold")

    # ── ЛІВА ера: правила діють ──
    s += rect(40, 84, split - 64, 196, "#f1f8f3", GREEN, 1.5, 12)
    s += text(40 + (split - 64) / 2, 108, "Доба «безкоштовного обіду» (≈1974–2005)", 14, INK, "middle", "bold")
    rules = [
        ("розмір (довжина)", "× 0.7", GREEN),
        ("площа транзистора", "× 0.5  (0.7²)", GREEN),
        ("напруга живлення V", "× 0.7", GREEN),
        ("потужність / транзистор", "× 0.5", GREEN),
        ("потужність на 1 мм²", "× 1  — стала!", BLUE),
        ("частота f", "× 1.4  росте вільно", GREEN),
    ]
    yy = 134
    for name, val, col in rules:
        s += text(64, yy, name, 11.8, INK, "start")
        s += text(split - 90, yy, val, 12, col, "end", "bold")
        yy += 24
    s += text(40 + (split - 64) / 2, 272,
              "транзисторів удвічі більше — а гріє та сама площа так само", 10.6, GREEN, "middle", style="italic")

    # ── ПРАВА ера: правила зламані ──
    s += rect(split + 24, 84, W - 40 - (split + 24), 196, "#fdf6f5", RED, 1.5, 12)
    s += text(split + 24 + (W - 40 - (split + 24)) / 2, 108, "Після зламу (≈2005 →)", 14, INK, "middle", "bold")
    broken = [
        ("напруга V", "застрягла ≈ 1 В", RED),
        ("(поріг транзистора не дає падати нижче)", "", GREY),
        ("витоки (leakage)", "ростуть", RED),
        ("потужність на 1 мм²", "↑ лізе вгору", RED),
        ("частота f", "стала ≈ 3–4 ГГц", RED),
        ("ціна виходу", "плата за транзистори", AMBER),
    ]
    yy = 134
    bx0 = split + 40
    bxr = W - 56
    for name, val, col in broken:
        sz = 10.4 if name.startswith("(") else 11.8
        st = "italic" if name.startswith("(") else "normal"
        s += text(bx0, yy, name, sz, GREY if name.startswith("(") else INK, "start", style=st)
        if val:
            s += text(bxr, yy, val, 12, col, "end", "bold")
        yy += 22 if name.startswith("(") else 24
    s += text(split + 24 + (W - 40 - (split + 24)) / 2, 272,
              "транзистори ще множаться — але всі разом увімкнути не можна", 10.4, RED, "middle", style="italic")

    # ── НИЖНЯ панель: дві криві в часі — частота (стала) vs щільність потужності ──
    gx, gy = 78, 318
    gw, gh = W - 78 - 48, 150
    s += line(gx, gy, gx, gy + gh, GREY, 1.6)
    s += line(gx, gy + gh, gx + gw, gy + gh, GREY, 1.6)
    y0, y1 = 1990, 2024

    def gpx(yr):
        return gx + gw * (yr - y0) / (y1 - y0)

    for yr in range(1990, 2025, 5):
        xg = gpx(yr)
        s += line(xg, gy + gh, xg, gy + gh + 5, GREY, 1.0)
        s += text(xg, gy + gh + 18, f"{yr}", 10, GREY, "middle")
    # вертикаль 2005 на нижній панелі
    s += line(gpx(2005), gy, gpx(2005), gy + gh, INK, 1.2, "4 4")

    # частота: росте до 2005, далі плато (нормовано до висоти панелі)
    fpts = []
    for yr in range(1990, 2025):
        if yr <= 2005:
            v = 0.10 + 0.78 * ((yr - 1990) / 15.0) ** 1.1
        else:
            v = 0.88 + 0.02 * math.sin((yr - 2005) * 0.6)
        fpts.append((gpx(yr), gy + gh * (1 - min(v, 0.96))))
    s += polyline(fpts, BLUE, 2.6)
    s += text(gpx(2001), gy + gh * (1 - 0.62), "частота ядра", 11, BLUE, "start", "bold")
    s += text(gpx(2015), gy + gh * (1 - 0.92), "плато ≈ 3–4 ГГц", 10.5, BLUE, "middle")

    # щільність потужності: повільно, потім після 2005 вгору
    ppts = []
    for yr in range(1990, 2025):
        if yr <= 2005:
            v = 0.16 + 0.20 * ((yr - 1990) / 15.0)
        else:
            v = 0.36 + 0.52 * ((yr - 2005) / 19.0) ** 0.9
        ppts.append((gpx(yr), gy + gh * (1 - min(v, 0.94))))
    s += polyline(ppts, RED, 2.6)
    s += text(gpx(2009), gy + gh * (1 - 0.80), "щільність потужності, Вт/мм²", 11, RED, "start", "bold")
    s += text(gpx(1994), gy + gh * (1 - 0.20), "поки V падала — рівна", 10, RED, "start")

    s += text(gx - 8, gy - 4, "відносні величини", 10.5, GREY, "start", style="italic")
    s += text(gpx(2005) + 6, gy + 14, "тут Деннард ламається", 10.5, INK, "start", "bold")

    save("fig-r10-s8m-2-dennard.svg", s)


# ═══════════════════════════════════════════════════════════════════════════
# Рис. 3.10.8m.3 — «злами» однієї прямої: лінія транзисторів іде далі, але те,
# що вона давала «у подарунок», відвалюється шарами. Діаграма-розклад:
# транзистори ↑ (тривають) → частота (стала з ~2005) → одне ядро (стало) →
# відповідь індустрії: багатоядерність, спеціалізовані блоки, чиплети.
# Показує, що «кінець закону Мура» — це насправді кінець ДОДАТКОВИХ подарунків,
# а не самої лінії транзисторів.
# ═══════════════════════════════════════════════════════════════════════════
def fig_kinks():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "«Кінець закону Мура» — це відмова бонусів, а не зупинка лінії транзисторів",
              18, INK, "middle", "bold")
    s += text(W / 2, 54, "лінія транзисторів (нехай і повільніше) триває; натомість по черзі насичуються вигоди, що йшли з нею «у комплекті»",
              11.8, GREY, "middle", style="italic")

    # п'ять смуг-«трендів», кожна як міні-крива росте/насичується
    rows = [
        ("Транзисторів на чіп", "росте далі (хай і повільніше за 2 роки)", GREEN, "rise"),
        ("Тактова частота", "стала ≈ з 2005 (упёрлася в потужність)", RED, "plateau"),
        ("Швидкодія одного ядра", "майже стала (ILP вичерпано)", RED, "plateau"),
        ("Кількість ядер", "пішла вгору — відповідь на плато", BLUE, "rise_late"),
        ("Спеціалізовані блоки + чиплети", "беруть на себе ефективність", PURPLE, "rise_late"),
    ]
    lx = 300
    rx = 905
    rw = rx - lx
    y0, y1 = 1990, 2024
    top = 92
    rh = 58
    for i, (name, note, col, kind) in enumerate(rows):
        cy = top + i * rh
        # ярлик
        s += text(40, cy + 22, name, 13, INK, "start", "bold")
        s += text(40, cy + 38, note, 10.3, col, "start", style="italic")
        # доріжка
        s += rect(lx, cy + 6, rw, 40, "#fafafa", FAINT, 1.2, 6)
        # вертикаль 2005
        x05 = lx + rw * (2005 - y0) / (y1 - y0)
        s += line(x05, cy + 6, x05, cy + 46, GREY, 1.0, "3 3")
        # крива тренду
        pts = []
        for yr in range(1990, 2025):
            t = (yr - y0) / (y1 - y0)
            if kind == "rise":
                v = 0.12 + 0.80 * t
            elif kind == "plateau":
                v = (0.12 + 0.78 * (t / ((2005 - y0) / (y1 - y0)))) if yr <= 2005 else 0.88
                v = min(v, 0.9)
            elif kind == "rise_late":
                v = 0.12 if yr <= 2005 else 0.12 + 0.78 * ((yr - 2005) / (y1 - 2005))
            pts.append((lx + rw * t, cy + 6 + 40 * (1 - min(v, 0.92)) - 0))
        s += polyline(pts, col, 2.6)
        # маркер кінця
        s += circle(pts[-1][0], pts[-1][1], 3.6, col, col, 0)
    # роки під останньою доріжкою
    cy = top + (len(rows) - 1) * rh
    for yr in (1990, 2005, 2024):
        xg = lx + rw * (yr - y0) / (y1 - y0)
        s += text(xg, cy + 60, f"{yr}", 10.5, GREY, "middle")
    s += text(lx + rw * (2005 - y0) / (y1 - y0), cy + 74, "↑ кінець масштабування Деннарда", 11, INK, "middle", "bold")

    save("fig-r10-s8m-3-kinks.svg", s)


if __name__ == "__main__":
    fig_moore_line()
    fig_dennard()
    fig_kinks()
    print("r10-s8-m moore-dennard figures done.")
