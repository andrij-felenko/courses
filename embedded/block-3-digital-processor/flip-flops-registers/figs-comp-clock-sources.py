# -*- coding: utf-8 -*-
"""
SVG-фігури для 🔌-вставки §3.3.6.c — «Звідки береться такт: кварц, кераміка, RC і MEMS».
Окремий генератор (головний figs.py не чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1»/«+» червоний, «0»/«−» синій;
дійсне/висновок — зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів — за темою: Рис. 3.3.6.c.k.

Фігури:
  fig-16-6c-1-accuracy.svg  — драбина точності: RC → кераміка → кварц → TCXO/MEMS (ppm, лог-шкала)
  fig-16-6c-2-pierce.svg    — 🔌: кварц (2 ніжки) + Pierce-осцилятор у МК (інвертор, Rf, 2× CL) і розпіновка
  fig-16-6c-3-drift.svg     — що таке ppm на практиці: відхід годинника й запас швидкості шини (UART)
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: трикутник-інвертор (підсилювач осцилятора) ────────────────────
def inverter(x, y, scale=1.0, color=INK):
    """Трикутник вершиною праворуч + кружок інверсії. Вхід зліва (x,y), вихід справа."""
    w = 46 * scale
    h = 40 * scale
    out = (f'<path d="M{x:.1f},{y - h/2:.1f} L{x:.1f},{y + h/2:.1f} '
           f'L{x + w:.1f},{y:.1f} Z" fill="#fff" stroke="{color}" stroke-width="2"/>\n')
    out += circle(x + w + 4, y, 4, "#fff", color, 2)
    return out, (x, y), (x + w + 8, y)  # body, in-pin, out-pin


# ── Фігура 1: драбина точності (ppm) на логарифмічній шкалі ──────────────────
def fig1_accuracy():
    import math
    W, H = 900, 486
    b = header(W, H)
    b += text(W/2, 30, "Драбина точності джерел такту: похибка частоти у ppm",
              17, INK, "middle", "bold")
    b += text(W/2, 50, "ppm = частка на мільйон: 1 ppm = 0.0001 % = ±1 такт на кожен мільйон",
              12, GREY, "middle", "italic")

    # ліва колонка під назви сімейств; логарифмічна вісь ppm праворуч від неї
    name_x = 16                  # назви — ліворуч, вирівняні по лівому краю
    ax0, ax1 = 322, 802          # x-діапазон осі ppm
    ay = 426                     # рівень осі
    lo, hi = -1, 5               # 10^-1 .. 10^5 ppm
    def X(ppm):
        return ax0 + (math.log10(ppm) - lo) / (hi - lo) * (ax1 - ax0)

    # легка вертикальна межа між колонкою назв і полем графіка
    b += line(ax0 - 14, 66, ax0 - 14, ay + 6, FAINT, 1.4)

    # сама вісь + поділки 10^k
    b += line(ax0, ay, ax1, ay, INK, 2)
    for k in range(lo, hi + 1):
        x = ax0 + (k - lo) / (hi - lo) * (ax1 - ax0)
        b += line(x, ay - 5, x, ay + 5, INK, 1.6)
        # легка вертикальна сітка вгору
        b += line(x, 66, x, ay - 6, FAINT, 1)
        lab = {-1: "0.1", 0: "1", 1: "10", 2: "100", 3: "1 000", 4: "10 000", 5: "100 000"}[k]
        b += text(x, ay + 22, lab, 11, GREY, "middle")
    b += text(ax1 + 6, ay + 5, "ppm", 12, INK, "start", "bold")
    b += arrow(ax0, ay, ax1 + 2, ay, INK, 2)
    b += text(ax0, ay + 42, "← точніше", 11, GREEN, "start", "bold")
    b += text(ax1, ay + 42, "грубіше →", 11, RED, "end", "bold")

    # рядки-сімейства: (підпис, lo_ppm, hi_ppm, колір, нота)
    rows = [
        ("RC-генератор у чипі", 10000, 50000, RED,
         "вбудований, безкоштовний; «гуляє» з T° і живленням"),
        ("RC після калібрування", 1000, 20000, RED,
         "підправлений на заводі, та все одно повзе"),
        ("Керамічний резонатор", 3000, 5000, AMBER,
         "дешевий, CL уже всередині; точність середня"),
        ("Кварцовий резонатор", 10, 50, GREEN,
         "робоча конячка точного такту в МК"),
        ("Годинниковий кварц 32768 Гц", 5, 20, GREEN,
         "для лічби реального часу (RTC)"),
        ("TCXO: кварц + термокомпенсація", 0.5, 2, BLUE,
         "тримає точність і в спеку, і в холод"),
        ("MEMS-генератор", 5, 30, GREEN,
         "кремнієва балка замість кристала; міцний до ударів"),
    ]

    y = 86
    dy = 46
    for name, plo, phi, col, note in rows:
        # назва — у лівій колонці
        b += text(name_x, y + 4, name, 12.5, INK, "start", "bold")
        xa, xb = X(plo), X(phi)
        # смуга діапазону
        b += rect(min(xa, xb), y - 9, abs(xb - xa) + 1, 18, "#fff", col, 2, 4)
        b += line(min(xa, xb), y, max(xa, xb), y, col, 6)
        # підпис діапазону — праворуч від смуги, або ліворуч якщо тиснемо в правий край
        rng = f"±{plo:g}–{phi:g} ppm"
        right_crowded = max(xa, xb) > ax1 - 90
        if right_crowded:
            b += text(min(xa, xb) - 8, y + 4, rng, 11, col, "end", "bold")
        else:
            b += text(max(xa, xb) + 8, y + 4, rng, 11, col, "start", "bold")
        # нота — дрібним курсивом під смугою. Якщо смуга стоїть праворуч, вирівнюємо
        # текст по правому краю смуги; інакше — від лівого краю поля графіка (ax0),
        # щоб довгий рядок мав усю ширину й не вибігав за полотно.
        if note:
            if min(xa, xb) > 560:
                b += text(max(xa, xb), y + 17, note, 9.5, GREY, "end", "italic")
            else:
                b += text(max(min(xa, xb), ax0), y + 17, note, 9.5, GREY, "start", "italic")
        y += dy

    # орієнтир «годиться для UART/RTC» — вертикаль біля кварцу (±50 ppm)
    xg = X(50)
    b += line(xg, 78, xg, ay - 6, GREEN, 1.4, "4,4")
    b += text(xg - 6, 78, "лівіше — вистачає для UART і RTC", 10, GREEN, "end", "italic")

    save("fig-16-6c-1-accuracy.svg", b)


# ── Фігура 2: 🔌 кварц + Pierce-осцилятор у МК, розпіновка ───────────────────
def fig2_pierce():
    W, H = 820, 480
    b = header(W, H)
    b += text(W/2, 28, "Кварц під'єднують до МК як зворотний зв'язок інвертора (схема Пірса)",
              16, INK, "middle", "bold")

    # — лівий блок: умовне позначення кварцу (дві ніжки) —
    qx, qy = 90, 120
    b += text(qx, qy - 28, "Кварцовий резонатор", 12, INK, "middle", "bold")
    b += text(qx, qy - 12, "(2 ніжки, без полярності)", 10, GREY, "middle")
    # символ: дві пластини + прямокутник кристала
    b += line(qx, qy + 10, qx, qy + 30, INK, 2)
    b += line(qx - 16, qy + 30, qx + 16, qy + 30, INK, 3)       # верхня обкладка
    b += rect(qx - 11, qy + 36, 22, 26, "#eef7ee", INK, 2, 2)   # кристал
    b += line(qx - 16, qy + 68, qx + 16, qy + 68, INK, 3)       # нижня обкладка
    b += line(qx, qy + 68, qx, qy + 88, INK, 2)
    b += text(qx + 22, qy + 50, "кристал", 10, GREEN, "start")
    b += text(qx, qy + 108, "XTAL1   XTAL2", 10, GREY, "middle")
    b += arrow(qx + 40, qy + 50, qx + 110, qy + 50, GREY, 1.8, "5,4")
    b += text(qx + 5, qy + 124, "напис на корпусі:", 9.5, GREY, "middle")
    b += text(qx + 5, qy + 138, "напр. «40.000» = 40 МГц", 9.5, GREY, "middle")

    # — центр: інвертор МК з резистором Rf і двома навісними CL —
    inv, pin_in, pin_out = inverter(360, 150, 1.3, INK)
    b += inv
    xi, yi = pin_in
    xo, yo = pin_out
    b += text((xi + xo) / 2, yi - 38, "інвертор-підсилювач (усередині МК)", 11, INK, "middle", "italic")

    # вузли XTAL1 (вхід інвертора) і XTAL2 (вихід)
    x1, x2 = xi, xo
    # лінії від інвертора вгору до шини кварцу
    busY = 100
    b += line(x1, yi, x1, busY, INK, 2)
    b += line(x2, yo, x2, busY, INK, 2)
    b += text(x1, busY - 8, "XTAL1", 11, INK, "middle", "bold")
    b += text(x2, busY - 8, "XTAL2", 11, INK, "middle", "bold")
    # кварц між вузлами (зверху)
    b += line(x1, busY, x1 + 18, busY, INK, 2)
    b += rect(x1 + 18, busY - 10, x2 - x1 - 36, 20, "#eef7ee", GREEN, 2, 3)
    b += text((x1 + x2) / 2, busY + 5, "КВАРЦ", 11, GREEN, "middle", "bold")
    b += line(x2 - 18, busY, x2, busY, INK, 2)

    # Rf паралельно інвертору (петля зворотного зв'язку)
    b += line(x1, yi, x1 - 30, yi, INK, 2)
    b += line(x1 - 30, yi, x1 - 30, yi + 70, INK, 2)
    b += rect(x1 - 46, yi + 70, 32, 16, "#fff", AMBER, 2, 3)
    b += text(x1 - 30, yi + 82, "Rf", 11, AMBER, "middle", "bold")
    b += line(x1 - 30, yi + 86, x1 - 30, yi + 120, INK, 2)
    b += line(x1 - 30, yi + 120, x2, yi + 120, INK, 2)
    b += line(x2, yo, x2, yi + 120, INK, 2)
    b += text(x1 - 70, yi + 30, "Rf: тримає інвертор", 9.5, AMBER, "start")
    b += text(x1 - 70, yi + 44, "у лінійному режимі", 9.5, AMBER, "start")
    b += text(x1 - 70, yi + 58, "(часто вже в чипі)", 9.5, GREY, "start")

    # два навантажувальні конденсатори CL на землю
    gndY = busY + 86
    for xc, lab in ((x1, "CL"), (x2, "CL")):
        b += line(xc, busY, xc, busY + 30, INK, 1.6)
        # символ конденсатора
        b += line(xc - 12, busY + 30, xc + 12, busY + 30, INK, 2.4)
        b += line(xc - 12, busY + 38, xc + 12, busY + 38, INK, 2.4)
        b += line(xc, busY + 38, xc, gndY, INK, 1.6)
        # земля
        b += line(xc - 12, gndY, xc + 12, gndY, BLUE, 2.4)
        b += line(xc - 8, gndY + 5, xc + 8, gndY + 5, BLUE, 2)
        b += line(xc - 4, gndY + 10, xc + 4, gndY + 10, BLUE, 2)
        b += text(xc + 16, busY + 38, lab, 11, INK, "start", "bold")
    b += text((x1 + x2) / 2, gndY + 30, "два CL (≈ 12–22 пФ) задають «навантаження» кварцу",
              10, GREY, "middle")
    b += text((x1 + x2) / 2, gndY + 46, "номінал бере зі специфікації кварцу (load capacitance)",
              9.5, GREY, "middle")

    # — правий блок: розпіновка корпусу МК (тільки потрібні ніжки) —
    px, py, pw, ph = 600, 95, 150, 210
    b += rect(px, py, pw, ph, "#fbfbfb", INK, 2, 8)
    b += circle(px + pw/2, py + 12, 6, "#fff", INK, 1.6)
    b += text(px + pw/2, py + 34, "МК", 14, INK, "middle", "bold")
    b += text(px + pw/2, py + 50, "(фрагмент)", 10, GREY, "middle")
    pins = [("XTAL1 / XIN", "вхід осц.", INK),
            ("XTAL2 / XOUT", "вихід осц.", INK),
            ("GND", "земля під осц.", BLUE),
            ("VDD", "живлення", RED)]
    yy = py + 78
    for nm, role, col in pins:
        b += line(px - 24, yy, px, yy, INK, 2)
        b += circle(px - 24, yy, 3, INK, INK, 1)
        b += text(px + 8, yy + 4, nm, 11, col, "start", "bold")
        b += text(px - 28, yy + 4, role, 9, GREY, "end")
        yy += 36
    b += text(px + pw/2, py + ph + 22, "кварц і два CL — упритул до ніжок,",
              10, GREEN, "middle", "italic")
    b += text(px + pw/2, py + ph + 38, "коротка земляна петля під ними",
              10, GREEN, "middle", "italic")

    # стрілка-зв'язка від схеми до розпіновки
    b += arrow(x2 + 30, busY, px - 30, py + 78, GREY, 1.8, "5,4")

    save("fig-16-6c-2-pierce.svg", b)


# ── Фігура 3: що таке ppm на практиці — відхід годинника й запас UART ────────
def fig3_drift():
    W, H = 820, 430
    b = header(W, H)
    b += text(W/2, 28, "Що означає ppm на практиці: два наслідки тієї самої похибки",
              16, INK, "middle", "bold")

    # — ЛІВА панель: відхід годинника за добу/місяць —
    lx = 60
    b += rect(lx, 56, 330, 320, "#fff", FAINT, 1.5, 8)
    b += text(lx + 165, 80, "1) Годинник «пливе»", 14, INK, "middle", "bold")
    b += text(lx + 165, 100, "похибка × час = накопичений відхід", 11, GREY, "middle", "italic")
    b += text(lx + 165, 116, "1 ppm ≈ 0.0864 с за добу", 11, GREEN, "middle")

    # таблиця: джерело → ppm → за добу → за рік
    cols_x = [lx + 14, lx + 150, lx + 226, lx + 300]
    head_y = 146
    b += text(cols_x[0], head_y, "джерело", 11, INK, "start", "bold")
    b += text(cols_x[1], head_y, "ppm", 11, INK, "middle", "bold")
    b += text(cols_x[2], head_y, "/добу", 11, INK, "middle", "bold")
    b += text(cols_x[3], head_y, "/рік", 11, INK, "middle", "bold")
    b += line(lx + 10, head_y + 8, lx + 320, head_y + 8, FAINT, 1.4)

    drift_rows = [
        ("RC у чипі", 30000, RED),
        ("кераміка", 4000, AMBER),
        ("кварц МК", 30, GREEN),
        ("кварц RTC", 20, GREEN),
        ("TCXO", 1, BLUE),
    ]
    yy = head_y + 30
    for nm, ppm, col in drift_rows:
        per_day_s = ppm * 86400e-6        # секунд за добу
        per_year_s = ppm * 31557600e-6    # секунд за рік
        # форматування
        if per_day_s >= 60:
            d_txt = f"{per_day_s/60:.1f} хв"
        else:
            d_txt = f"{per_day_s:.2g} с"
        if per_year_s >= 86400:
            y_txt = f"{per_year_s/86400:.1f} дн"
        elif per_year_s >= 3600:
            y_txt = f"{per_year_s/3600:.1f} год"
        elif per_year_s >= 60:
            y_txt = f"{per_year_s/60:.0f} хв"
        else:
            y_txt = f"{per_year_s:.0f} с"
        b += text(cols_x[0], yy, nm, 11, INK, "start")
        b += text(cols_x[1], yy, f"±{ppm:g}", 11, col, "middle", "bold")
        b += text(cols_x[2], yy, d_txt, 11, INK, "middle")
        b += text(cols_x[3], yy, y_txt, 11, col, "middle", "bold")
        yy += 30
    b += text(lx + 165, yy + 16, "RC на рік «з'їде» на тижні —", 10, RED, "middle", "italic")
    b += text(lx + 165, yy + 32, "тримати реальний час на ньому не можна", 10, RED, "middle", "italic")

    # — ПРАВА панель: запас швидкості UART —
    rx = 430
    b += rect(rx, 56, 330, 320, "#fff", FAINT, 1.5, 8)
    b += text(rx + 165, 80, "2) Зв'язок «розсинхрониться»", 14, INK, "middle", "bold")
    b += text(rx + 165, 100, "два боки шини рахують біти своїми тактами", 10.5, GREY, "middle", "italic")

    # шкала допустимого розходження для UART (типово до ~±2…3 % сумарно)
    bar_x0, bar_x1 = rx + 30, rx + 300
    bar_y = 150
    b += text(rx + 165, bar_y - 18, "сумарне розходження двох боків", 11, INK, "middle")
    # зелена зона до 2 %, жовта 2..3 %, червона далі
    full = bar_x1 - bar_x0
    g_end = bar_x0 + full * (2.0/4.0)
    a_end = bar_x0 + full * (3.0/4.0)
    b += rect(bar_x0, bar_y, g_end - bar_x0, 20, "#e8f6ec", GREEN, 1.5, 0)
    b += rect(g_end, bar_y, a_end - g_end, 20, "#fbf3df", AMBER, 1.5, 0)
    b += rect(a_end, bar_y, bar_x1 - a_end, 20, "#fae8e6", RED, 1.5, 0)
    for frac, lab in ((0, "0"), (2.0/4, "2 %"), (3.0/4, "3 %"), (1.0, "4 %")):
        x = bar_x0 + full * frac
        b += line(x, bar_y + 20, x, bar_y + 26, GREY, 1.4)
        b += text(x, bar_y + 38, lab, 10, GREY, "middle")
    b += text(bar_x0 + (g_end - bar_x0)/2, bar_y + 14, "надійно", 10, GREEN, "middle", "bold")
    b += text((a_end + bar_x1)/2, bar_y + 14, "збій", 10, RED, "middle", "bold")

    # маркери-засічки під смугою: кожна пара тактів стає на свій сумарний %.
    # Сумарне розходження ≈ (ppmA + ppmB) / 10000  [у відсотках]; frac = % / 4.
    def tick(pct, col):
        frac = min(pct, 4.0) / 4.0
        x = bar_x0 + full * frac
        out = line(x, bar_y + 20, x, bar_y + 28, col, 2)
        out += circle(x, bar_y + 28, 3.2, col, col, 1)
        return out, x

    # 2×кварц: (30+30)/10000 = 0.006 %; кераміка+кварц ≈ 0.40 %;
    # 2×кераміка ≈ 0.80 %; RC+кварц ≈ 3.0 % (на межі зриву)
    t1, x1 = tick(0.006, GREEN); b += t1
    t2, x2 = tick(0.40,  GREEN); b += t2
    t3, x3 = tick(0.80,  AMBER); b += t3
    t4, x4 = tick(3.00,  RED);   b += t4
    # три ліві засічки тісняться біля нуля — підпишемо їх однією дужкою-зноскою
    b += text((x1 + x3) / 2, bar_y + 46, "кварц/кераміка — тут", 9, GREEN, "middle")
    b += text(x4, bar_y + 46, "RC", 9, RED, "middle", "bold")

    b += text(rx + 165, bar_y + 78, "Пара тактів і де вона лягає:", 11, INK, "middle", "bold")
    notes = [
        ("два кварци: 0.006 %  — величезний запас", GREEN),
        ("кераміка + кварц: ~0.4 %  — ще надійно", GREEN),
        ("дві кераміки: ~0.8 %  — теж проходить", GREEN),
        ("RC + кварц: ~3 %  — уже на межі зриву", RED),
    ]
    ny = bar_y + 100
    for txt_, col in notes:
        b += circle(rx + 24, ny - 4, 3.5, col, col, 1)
        b += text(rx + 36, ny, txt_, 10.5, col, "start")
        ny += 24
    b += text(rx + 165, ny + 8, "ось чому UART на «голому» RC часто не злітає",
              10, GREY, "middle", "italic")

    save("fig-16-6c-3-drift.svg", b)


if __name__ == "__main__":
    fig1_accuracy()
    fig2_pierce()
    fig3_drift()
    print("ch16-s6-c-clock-sources figures done.")
