# -*- coding: utf-8 -*-
"""
Генератор SVG для Розділу 3.8 «Зовнішня пам'ять».
Чистий Python, без залежностей (matplotlib НЕ використовується). Вивід → ./img/.
Імена файлів: fig-<М>-<Р>-<Т>-<k>-<slug>.svg  (модуль-розділ-тема-номер).
Стиль (AUTHORING §9): білий фон; «+»/гаряче червоний, «−»/холодне синій;
поле/висновок/«добре» зелене; стрілки через marker; шрифт sans-serif.
Допоміжні функції — самодостатні в цьому файлі (за §9 кожен скрипт автономний).
Нумерація підписів у тексті: Рис. 3.8.Т.k.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # гаряче / запис / увага / «1»
BLUE  = "#1f47b5"   # холодне / читання / «0»
GREEN = "#1f8a3b"   # висновок / «добре» / поле
AMBER = "#caa24a"   # акцент / попередження
PURPLE = "#6a3fb5"  # контролер / прошарок
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
PALEB = "#eef2fb"   # бліде блакитне тло
PALER = "#fdeef0"   # бліде червоне тло
PALEG = "#eef6ef"   # бліде зелене тло
PALEP = "#f1ecfa"   # бліде фіолетове тло
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen", BLUE: "aBlue",
         GREY: "aGrey", PURPLE: "aPurple", AMBER: "aAmber"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def polygon(pts, fill="none", stroke=INK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d} stroke-linejoin="round"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def roundrect(x, y, w, h, color=GREEN, sw=3, rx=14, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def chip(x, y, w, h, label, sub="", fill=PALEP, stroke=PURPLE, tcol=PURPLE):
    """Прямокутник-чіп із заголовком і підзаголовком."""
    s = rect(x, y, w, h, fill, stroke, 2.2, rx=8)
    s += text(x + w / 2, y + h / 2 - (3 if sub else -5), label, 14, tcol, "middle", "bold")
    if sub:
        s += text(x + w / 2, y + h / 2 + 15, sub, 10.5, GREY, "middle")
    return s


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def bar(x, y_base, w, h, color, label_top=None, top_size=12):
    """Стовпчик діаграми, що росте вгору від y_base."""
    s = rect(x, y_base - h, w, h, color, color, 0)
    if label_top:
        s += text(x + w / 2, y_base - h - 8, label_top, top_size, color, "middle", "bold")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.1 — Коли вбудованої пам'яті мало
# ════════════════════════════════════════════════════════════════════════════

def fig_811_appetite():
    """Рис. 3.8.1.1 — апетит задач (кадр, аудіо, лог) проти кишені вбудованої RAM."""
    W, H = 1000, 560
    s = header(W, H)
    s += text(W / 2, 34, "Апетит реальних задач проти вбудованої RAM",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "Стовпчики — скільки байтів просить одна задача; пунктир — типова кишеня SRAM мікроконтролера (лог-шкала)",
              12.5, GREY, "middle", style="italic")

    ox, oy = 120, 470
    axw, axh = 760, 360
    s += arrow(ox, oy, ox + axw + 12, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh - 16, INK, 2)
    s += text(ox - 76, oy - axh - 2, "байтів", 12, INK, "start", "bold")
    s += text(ox - 76, oy - axh + 16, "(лог)", 11, GREY, "start")

    # лог-шкала від 1 КБ (10^3) до 8 МБ (~8·10^6)
    def ylog(val):
        lo, hi = math.log10(512), math.log10(16 * 1024 * 1024)
        return oy - axh * (math.log10(val) - lo) / (hi - lo)

    # горизонтальні рівні-сітка
    for val, lab in [(1024, "1 КБ"), (16 * 1024, "16 КБ"),
                     (256 * 1024, "256 КБ"), (1024 * 1024, "1 МБ"),
                     (8 * 1024 * 1024, "8 МБ")]:
        yy = ylog(val)
        s += line(ox, yy, ox + axw, yy, FAINT, 1)
        s += text(ox - 10, yy + 4, lab, 11, GREY, "end")

    items = [
        ("кадр\n160×128×2", 160 * 128 * 2, BLUE, "екран\n40 КБ"),
        ("кадр\n320×240×2", 320 * 240 * 2, BLUE, "екран\n150 КБ"),
        ("аудіо-буфер\n1 с @ 44.1к·16", 44100 * 2, GREEN, "звук\n88 КБ"),
        ("буфер логів\n1 хв @ 1 КБ/с", 60 * 1024, AMBER, "логи\n60 КБ"),
        ("кадр RGB888\n640×480", 640 * 480 * 3, RED, "камера\n900 КБ"),
    ]
    bw = 96
    gap = (axw - len(items) * bw) / (len(items) + 1)
    for i, (lab, val, col, tag) in enumerate(items):
        bx = ox + gap + i * (bw + gap)
        yy = ylog(val)
        s += rect(bx, yy, bw, oy - yy, col, col, 0)
        # двосходинковий підпис зверху
        for j, ln in enumerate(tag.split("\n")):
            s += text(bx + bw / 2, yy - 24 + j * 15, ln, 11.5, col, "middle", "bold")
        for j, ln in enumerate(lab.split("\n")):
            s += text(bx + bw / 2, oy + 22 + j * 15, ln, 11, INK, "middle")

    # лінія «типова SRAM МК» ≈ 256–520 КБ
    ysram = ylog(400 * 1024)
    s += line(ox, ysram, ox + axw, ysram, RED, 2.4, "8,5")
    s += text(ox + axw + 4, ysram + 4, "стеля SRAM", 11.5, RED, "start", "bold")
    s += text(ox + axw + 4, ysram + 20, "(сотні КБ)", 10.5, GREY, "start")

    s += text(W / 2, H - 14,
              "Один кадр кольорового екрана з'їдає більше, ніж уся SRAM дрібного МК. Звідси й потреба у зовнішній пам'яті.",
              12.5, GREEN, "middle", "bold")
    save("fig-3-8-1-1-appetite.svg", s)


def fig_812_framebuffer():
    """Рис. 3.8.1.2 — звідки беруться байти кадру: піксель × глибина × роздільність."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "Звідки беруться байти кадру дисплея",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Кадровий буфер тримає колір КОЖНОГО пікселя; помножте піксель на роздільність — ось і весь обсяг",
              12.5, GREY, "middle", style="italic")

    # один піксель RGB565
    px, py = 80, 130
    s += rect(px, py, 60, 60, "#7fb0ff", INK, 1.6)
    s += text(px + 30, py - 12, "1 піксель", 13, INK, "middle", "bold")
    s += text(px + 30, py + 84, "RGB565", 12, BLUE, "middle", "bold")
    s += text(px + 30, py + 100, "= 2 байти", 12, BLUE, "middle")
    # розклад бітів
    bits = [("R", 5, RED), ("G", 6, GREEN), ("B", 5, BLUE)]
    bx = px + 90
    bw = 18
    s += text(bx + 8 * bw, py - 12, "16 біт = R5 G6 B5", 12, INK, "start")
    cx = bx
    for nm, n, col in bits:
        for k in range(n):
            s += rect(cx, py + 14, bw - 2, 28, "#ffffff", col, 1.4)
            cx += bw
        s += text(cx - n * bw / 2, py + 60, nm + str(n), 12, col, "middle", "bold")

    s += text(px + 30 + 250, py + 30, "×", 26, INK, "middle", "bold")

    # сітка роздільності
    gx, gy = 470, 110
    gw, gh = 200, 150
    cols, rows = 10, 8
    s += rect(gx, gy, gw, gh, PALEB, BLUE, 2)
    for c in range(1, cols):
        s += line(gx + c * gw / cols, gy, gx + c * gw / cols, gy + gh, "#cfd9f5", 0.8)
    for r in range(1, rows):
        s += line(gx, gy + r * gh / rows, gx + gw, gy + r * gh / rows, "#cfd9f5", 0.8)
    s += text(gx + gw / 2, gy - 12, "320 × 240 пікселів", 13, INK, "middle", "bold")
    s += text(gx + gw / 2, gy + gh + 22, "= 76 800 пікселів", 12, BLUE, "middle")

    s += text(gx + gw + 30, gy + gh / 2, "=", 26, INK, "middle", "bold")

    # результат
    rx, ry = gx + gw + 70, gy + 30
    s += roundrect(rx, ry, 210, 110, GREEN, 2.6, 12, fill=PALEG)
    s += text(rx + 105, ry + 30, "76 800 × 2 Б", 15, INK, "middle", "bold")
    s += text(rx + 105, ry + 58, "≈ 150 КБ", 22, GREEN, "middle", "bold")
    s += text(rx + 105, ry + 84, "на ОДИН кадр", 12, GREY, "middle")

    s += text(W / 2, H - 56,
              "А плавна анімація — це десятки кадрів за секунду, і часто потрібні ДВА буфери (поки один показуємо, інший малюємо).",
              12.5, INK, "middle")
    s += text(W / 2, H - 32,
              "150 КБ × 2 = 300 КБ — уже впритул до межі SRAM звичайного мікроконтролера або за нею.",
              12.5, GREEN, "middle", "bold")
    save("fig-3-8-1-2-framebuffer.svg", s)


def fig_813_three_loads():
    """Рис. 3.8.1.3 — три класи зовнішніх навантажень і яка пам'ять кожному пасує."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "Три класи навантажень — три різні вимоги до пам'яті",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Кадри й аудіо просять ШВИДКОЇ робочої пам'яті; логи — ЄМНОГО сховища, що переживе вимкнення",
              12.5, GREY, "middle", style="italic")

    cards = [
        (70, "Кадри дисплея", BLUE, PALEB,
         ["великий обсяг (КБ–МБ)", "дуже швидке читання", "оновлюються щокадру", "при вимкненні — байдуже"],
         "→ потрібна швидка RAM"),
        (370, "Аудіо-потік", GREEN, PALEG,
         ["безперервні буфери", "стабільна швидкість", "не можна «затинатись»", "тимчасові дані"],
         "→ потрібна швидка RAM"),
        (670, "Логи й записи", AMBER, "#fbf4e2",
         ["ростуть із часом", "запис рідший за читання", "МУСЯТЬ пережити збій", "обсяг — мегабайти"],
         "→ потрібне нелетке сховище"),
    ]
    for x, title, col, bg, lines, concl in cards:
        s += roundrect(x, 90, 260, 300, col, 2.4, 14, fill=bg)
        s += text(x + 130, 120, title, 15.5, col, "middle", "bold")
        s += line(x + 24, 132, x + 236, 132, col, 1.4)
        for i, ln in enumerate(lines):
            s += text(x + 24, 162 + i * 30, "•", 14, col, "start", "bold")
            s += text(x + 40, 162 + i * 30, ln, 12.5, INK, "start")
        s += line(x + 24, 300, x + 236, 300, FAINT, 1.4)
        s += text(x + 130, 332, concl, 13, col, "middle", "bold")

    s += text(W / 2, H - 28,
              "Немає однієї «правильної» пам'яті: робочі дані просять швидкості, а сховище — ємності й нелеткості. Тому далі ми вивчимо обидва роди.",
              12.5, INK, "middle")
    save("fig-3-8-1-3-three-loads.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.2 — DRAM: транзистор і конденсатор
# ════════════════════════════════════════════════════════════════════════════

def fig_821_cell_compare():
    """Рис. 3.8.2.1 — комірка SRAM (6 транзисторів) vs DRAM (1 транзистор + конденсатор)."""
    W, H = 1000, 520
    s = header(W, H)
    s += text(W / 2, 34, "Чому DRAM дешевша: одна комірка проти шести транзисторів",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "SRAM тримає біт на засувці з 6 транзисторів; DRAM — як заряд на одному крихітному конденсаторі",
              12.5, GREY, "middle", style="italic")

    # ліворуч: SRAM 6T
    sx, sy = 90, 110
    s += roundrect(sx, sy, 360, 350, BLUE, 2.2, 14, fill=PALEB)
    s += text(sx + 180, sy + 28, "SRAM — комірка з 6 транзисторів", 14.5, BLUE, "middle", "bold")
    # схематична засувка: два інвертори назустріч
    cx1, cx2 = sx + 110, sx + 250
    cyb = sy + 150
    for cx in (cx1, cx2):
        s += rect(cx - 30, cyb - 30, 60, 60, "#ffffff", INK, 1.8, rx=6)
    s += text(cx1, cyb + 2, "INV", 12, INK, "middle", "bold")
    s += text(cx2, cyb + 2, "INV", 12, INK, "middle", "bold")
    s += arrow(cx1 + 30, cyb - 12, cx2 - 30, cyb - 12, INK, 1.8)
    s += arrow(cx2 - 30, cyb + 12, cx1 + 30, cyb + 12, INK, 1.8)
    s += text((cx1 + cx2) / 2, cyb - 22, "тримають одне одного", 10.5, GREY, "middle", style="italic")
    # два транзистори доступу
    for cx in (cx1 - 30, cx2 + 30):
        s += circle(cx, cyb + 70, 14, "#ffffff", BLUE, 1.6)
        s += text(cx, cyb + 74, "T", 11, BLUE, "middle", "bold")
    s += text(sx + 180, sy + 268, "4 транзистори тримають біт + 2 на доступ", 11.5, INK, "middle")
    s += text(sx + 180, sy + 300, "СТАТИЧНА: поки є живлення — біт стоїть,", 12, BLUE, "middle", "bold")
    s += text(sx + 180, sy + 320, "регенерація НЕ потрібна. Зате велика й дорога.", 12, INK, "middle")

    # праворуч: DRAM 1T1C
    dx, dy = 550, 110
    s += roundrect(dx, dy, 360, 350, RED, 2.2, 14, fill=PALER)
    s += text(dx + 180, dy + 28, "DRAM — 1 транзистор + 1 конденсатор", 14.5, RED, "middle", "bold")
    # транзистор-ключ
    txr = dx + 110
    tyr = dy + 150
    s += circle(txr, tyr, 22, "#ffffff", INK, 1.8)
    s += text(txr, tyr + 5, "T", 15, INK, "middle", "bold")
    s += text(txr, tyr - 34, "ключ", 11, GREY, "middle")
    # конденсатор (дві пластини)
    capx = dx + 240
    s += line(txr + 22, tyr, capx, tyr, INK, 2)
    s += line(capx, tyr - 28, capx, tyr + 28, INK, 3)
    s += line(capx + 10, tyr - 28, capx + 10, tyr + 28, INK, 3)
    s += line(capx + 10, tyr, capx + 40, tyr, INK, 2)
    s += line(capx + 40, tyr + 20, capx + 40, tyr - 20, GREY, 2)  # земля
    s += text(capx + 5, tyr - 38, "конденсатор", 11, RED, "middle", "bold")
    s += text(capx + 5, tyr + 50, "заряд = біт", 11, RED, "middle")
    # лінія слова / лінія біта
    s += arrow(dx + 40, tyr, txr - 22, tyr, GREY, 1.6)
    s += text(dx + 40, tyr - 10, "лінія біта", 10, GREY, "start")
    s += arrow(txr, dy + 250, txr, tyr + 22, GREY, 1.6)
    s += text(txr + 6, dy + 246, "лінія слова", 10, GREY, "start")
    s += text(dx + 180, dy + 300, "ДИНАМІЧНА: заряд стікає за мілісекунди —", 12, RED, "middle", "bold")
    s += text(dx + 180, dy + 320, "треба регенерація. Зате крихітна й дешева.", 12, INK, "middle")

    s += text(W / 2, H - 18,
              "Менше деталей на біт → більше бітів на тій самій пластині → нижча ціна за мегабайт. Платня — конденсатор тече.",
              12.5, GREEN, "middle", "bold")
    save("fig-3-8-2-1-cell-compare.svg", s)


def fig_822_leak_refresh():
    """Рис. 3.8.2.2 — заряд комірки стікає; регенерація поновлює його до втрати біта."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "Заряд тече — регенерація встигає поновити його вчасно",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Без поновлення рівень падає нижче порога й біт губиться; регенерація читає-й-перезаписує ряд кожні кілька мс",
              12.5, GREY, "middle", style="italic")

    ox, oy = 110, 360
    axw, axh = 800, 280
    s += arrow(ox, oy, ox + axw + 12, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh - 16, INK, 2)
    s += text(ox - 14, oy - axh - 4, "заряд", 12, INK, "end", "bold")
    s += text(ox + axw + 6, oy + 22, "час", 12, INK, "middle", "bold")

    # рівень «1» і поріг
    y1 = oy - axh + 30
    ythr = oy - 80
    s += line(ox, y1, ox + axw, y1, GREY, 1.2, "4,4")
    s += text(ox - 8, y1 + 4, "повний «1»", 11, GREY, "end")
    s += line(ox, ythr, ox + axw, ythr, RED, 1.6, "6,4")
    s += text(ox - 8, ythr + 4, "поріг", 11, RED, "end", "bold")
    s += text(ox - 8, ythr + 18, "читання", 10, GREY, "end")

    # БЕЗ регенерації — спад нижче порога (пунктир, червоний)
    pts = []
    for k in range(0, 60):
        t = k / 59
        xx = ox + t * axw * 0.55
        # експоненційний спад
        yy = y1 + (oy - y1) * (1 - math.exp(-t * 3.4))
        pts.append((xx, yy))
    s += polyline(pts, RED, 2.4, dash="2,3")
    s += text(pts[-1][0] + 6, pts[-1][1] + 4, "біт згублено!", 12, RED, "start", "bold")
    # точка перетину порога
    s += circle(ox + 0.30 * axw, ythr, 4, RED, RED)

    # З регенерацією — пилка (зелена): спад і поновлення
    sawx0 = ox
    period = axw * 0.18
    saw = []
    xx = ox
    drop_to = y1 + (ythr - y1) * 0.45
    n_saw = 4
    for i in range(n_saw):
        x0 = ox + i * period
        x1 = x0 + period
        saw.append((x0, y1))
        saw.append((x1 - 2, drop_to))
        # вертикальне поновлення
        saw.append((x1 - 2, y1))
    # обрізати до осі
    saw = [(min(x, ox + axw), y) for x, y in saw]
    s += polyline(saw, GREEN, 2.6)
    for i in range(n_saw):
        x1 = ox + (i + 1) * period
        if x1 <= ox + axw:
            s += arrow(x1 - 2, drop_to, x1 - 2, y1 + 4, GREEN, 1.6)
    s += text(ox + 2.4 * period, y1 - 14, "з регенерацією: поновлюємо вчасно", 12, GREEN, "middle", "bold")
    s += text(ox + period - 2, drop_to + 22, "кожні ~64 мс — увесь масив", 10.5, GREEN, "middle")

    s += text(W / 2, H - 30,
              "Регенерація (refresh) — це фонове «прочитати ряд і записати назад». Поки вона встигає, біти живі; це робота контролера, не вашого коду.",
              12.5, INK, "middle")
    save("fig-3-8-2-2-leak-refresh.svg", s)


def fig_823_array_rowcol():
    """Рис. 3.8.2.3 — масив комірок: рядки й стовпці, регенерація йде по рядках."""
    W, H = 1000, 500
    s = header(W, H)
    s += text(W / 2, 34, "Масив DRAM: рядки й стовпці — і чому регенерація йде рядками",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Одне звернення активує цілий РЯД у буфер-підсилювач; регенерація просто проходить усі ряди по черзі",
              12.5, GREY, "middle", style="italic")

    gx, gy = 250, 110
    n = 8
    cell = 34
    # сітка комірок
    for r in range(n):
        for c in range(n):
            x = gx + c * cell
            y = gy + r * cell
            fill = "#ffffff"
            if r == 3:
                fill = PALEG
            s += rect(x, y, cell - 3, cell - 3, fill, FAINT, 1)
            # крихітний конденсатор-крапка
            s += circle(x + (cell - 3) / 2, y + (cell - 3) / 2, 3.2,
                        GREEN if r == 3 else "#cfcfcf",
                        GREEN if r == 3 else "#bdbdbd", 1)
    # лінії слова (рядки) ліворуч
    for r in range(n):
        y = gy + r * cell + (cell - 3) / 2
        col = GREEN if r == 3 else GREY
        s += arrow(gx - 70, y, gx - 4, y, col, 1.6 if r == 3 else 1)
    s += text(gx - 76, gy + 3 * cell + (cell - 3) / 2 + 4, "ряд 3", 11, GREEN, "end", "bold")
    s += text(gx - 76, gy - 12, "лінії слова", 11, INK, "end", "bold")
    s += text(gx - 76, gy + 4, "(рядки)", 10, GREY, "end")
    # лінії біта (стовпці) знизу → буфер
    bufy = gy + n * cell + 24
    s += rect(gx, bufy, n * cell - 3, 30, PALEB, BLUE, 1.8, rx=4)
    s += text(gx + (n * cell - 3) / 2, bufy + 20, "буфер-підсилювач (рядок цілком)", 11.5, BLUE, "middle", "bold")
    for c in range(n):
        x = gx + c * cell + (cell - 3) / 2
        s += line(x, gy + n * cell - 3, x, bufy, "#cfd9f5", 1)

    # пояснення праворуч
    px = gx + n * cell + 60
    s += roundrect(px, gy, 270, 300, INK, 1.8, 12)
    s += text(px + 135, gy + 28, "Як це працює", 14, INK, "middle", "bold")
    txt = [
        ("1.", "активуємо ОДИН ряд лінією слова", GREEN),
        ("2.", "увесь ряд «зливається» в буфер", BLUE),
        ("3.", "з буфера беремо потрібний стовпець", INK),
        ("4.", "буфер записує ряд назад —", GREY),
        ("", "  саме це й поновлює заряд!", GREEN),
    ]
    for i, (n_, ln, col) in enumerate(txt):
        s += text(px + 18, gy + 64 + i * 32, n_, 13, col, "start", "bold")
        s += text(px + 44, gy + 64 + i * 32, ln, 11.5, INK, "start")
    s += line(px + 18, gy + 240, px + 252, gy + 240, FAINT, 1.4)
    s += text(px + 135, gy + 264, "Регенерація = пройти всі ряди.", 12, GREEN, "middle", "bold")
    s += text(px + 135, gy + 284, "Адресу шлють у два прийоми: RAS, потім CAS.", 10.5, GREY, "middle")

    save("fig-3-8-2-3-array-rowcol.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.3 — SDRAM і DDR якісно
# ════════════════════════════════════════════════════════════════════════════

def fig_831_async_vs_sync():
    """Рис. 3.8.3.1 — асинхронна DRAM (чекаємо відгук) vs синхронна (по такту, конвеєр)."""
    W, H = 1000, 480
    s = header(W, H)
    s += text(W / 2, 34, "Синхронна пам'ять: працюємо в такт, а не «питання — пауза — відповідь»",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Стара DRAM відповідала «коли встигне»; SDRAM прив'язана до такту, тож звернення вишиковуються конвеєром",
              12.5, GREY, "middle", style="italic")

    # верх: асинхронна
    ax, ay = 90, 130
    s += text(ax, ay - 18, "Асинхронна DRAM — чекаємо невідому затримку", 13.5, RED, "start", "bold")
    s += rect(ax, ay, 820, 70, PALER, RED, 1.6, rx=8)
    seq = [("адреса", 40, INK), ("?", 150, GREY), ("дані", 230, RED),
           ("адреса", 360, INK), ("?", 470, GREY), ("дані", 550, RED)]
    for lab, dx, col in seq:
        s += rect(ax + dx, ay + 18, 80, 34, "#ffffff", col, 1.4, rx=4)
        s += text(ax + dx + 40, ay + 40, lab, 11.5, col, "middle", "bold")
    s += text(ax + 150 + 40, ay + 66, "«коли?»", 10, GREY, "middle", style="italic")
    s += text(ax + 700, ay + 35, "повільно й непевно", 12, RED, "middle", "bold")

    # низ: синхронна з тактом
    by = 290
    s += text(ax, by - 18, "SDRAM — кожна дія прив'язана до фронту такту (конвеєр)", 13.5, GREEN, "start", "bold")
    # такт
    clk_y = by
    clk = []
    per = 70
    for i in range(12):
        x = ax + i * per
        clk.append((x, clk_y))
        clk.append((x, clk_y - 22))
        clk.append((x + per / 2, clk_y - 22))
        clk.append((x + per / 2, clk_y))
    s += polyline(clk, BLUE, 2)
    s += text(ax - 10, clk_y - 10, "CLK", 11, BLUE, "end", "bold")
    # конвеєр команд під тактом
    cmds = ["ACT", "RD", "—", "D0", "D1", "D2", "D3", "RD", "—", "D0", "D1", "D2"]
    cy = by + 50
    for i, c in enumerate(cmds):
        x = ax + i * per
        col = GREEN if c.startswith("D") else (PURPLE if c in ("ACT", "RD") else GREY)
        bg = PALEG if c.startswith("D") else ("#ffffff")
        s += rect(x + 4, cy, per - 8, 34, bg, col, 1.4, rx=4)
        s += text(x + per / 2, cy + 22, c, 11.5, col, "middle", "bold")
        s += line(x, clk_y, x, cy, FAINT, 1)
    s += text(ax + 3.5 * per, cy + 56, "пакет (burst): один запит → потік слів підряд, по одному за такт",
              12, GREEN, "middle", "bold")

    s += text(W / 2, H - 18,
              "Прив'язка до такту дає головне: відгук передбачуваний, а звернення можна КОНВЕЄРИЗУВАТИ — поки одне віддає дані, наступне вже готується.",
              12, INK, "middle")
    save("fig-3-8-3-1-async-vs-sync.svg", s)


def fig_832_banks():
    """Рис. 3.8.3.2 — кілька банків працюють з перекриттям (поки один активний, інший готується)."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "Банки: поки один віддає дані, інший уже відкриває ряд",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Масив поділено на банки; їхні затримки перекриваються, тож шина даних майже не простоює",
              12.5, GREY, "middle", style="italic")

    # 4 банки ліворуч
    bx, by = 80, 110
    bnames = ["Bank 0", "Bank 1", "Bank 2", "Bank 3"]
    bcols = [BLUE, GREEN, AMBER, PURPLE]
    for i, (nm, col) in enumerate(zip(bnames, bcols)):
        y = by + i * 64
        s += rect(bx, y, 150, 50, "#ffffff", col, 2, rx=6)
        # сітка-натяк
        for r in range(3):
            s += line(bx + 10, y + 12 + r * 12, bx + 140, y + 12 + r * 12, FAINT, 0.8)
        s += text(bx + 75, y + 30, nm, 13, col, "middle", "bold")

    # шина даних спільна
    busx = bx + 200
    s += line(busx, by - 10, busx, by + 4 * 64 - 14, INK, 2.4)
    for i in range(4):
        y = by + i * 64 + 25
        s += arrow(bx + 150, y, busx, y, bcols[i], 1.6)
    s += text(busx + 6, by - 16, "спільна шина даних", 11.5, INK, "start", "bold")

    # часова діаграма перекриття праворуч
    tx, ty = busx + 40, 110
    tw = 540
    lane_h = 56
    s += text(tx, ty - 14, "час →", 12, INK, "start", "bold")
    s += arrow(tx, ty - 30, tx + tw, ty - 30, GREY, 1.6)
    for i, (nm, col) in enumerate(zip(bnames, bcols)):
        ly = ty + i * (lane_h)
        s += text(tx - 4, ly + 18, nm, 10.5, col, "end", "bold")
        # фаза «відкриття ряду» (світла) + «віддача даних» (насичена)
        offset = i * 60
        s += rect(tx + offset, ly + 4, 56, 14, "#ffffff", col, 1.4, rx=3)
        s += text(tx + offset + 28, ly + 14, "ACT", 8.5, col, "middle", "bold")
        s += rect(tx + offset + 56, ly + 4, 110, 14, col, col, 0, rx=3)
        s += text(tx + offset + 56 + 55, ly + 14, "дані", 8.5, "#ffffff", "middle", "bold")
    # лінія «шина зайнята майже завжди»
    busy_y = ty + 4 * lane_h + 6
    s += line(tx, busy_y, tx + tw, busy_y, FAINT, 1)
    for i in range(4):
        offset = i * 60
        s += rect(tx + offset + 56, busy_y + 4, 110, 12, bcols[i], bcols[i], 0, rx=2)
    s += text(tx + tw / 2, busy_y + 38, "шина даних зайнята майже без пауз — банки перекривають затримки одне одного",
              11.5, GREEN, "middle", "bold")

    save("fig-3-8-3-2-banks.svg", s)


def fig_833_ddr_edges():
    """Рис. 3.8.3.3 — SDR (дані по одному фронту) vs DDR (по обох фронтах: подвоєння)."""
    W, H = 1000, 460
    s = header(W, H)
    s += text(W / 2, 34, "DDR: дані на ОБОХ фронтах такту — удвічі більше за ту саму частоту",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "SDR віддає одне слово за такт (на висхідному фронті); DDR — по слову й на висхідному, і на спадному",
              12.5, GREY, "middle", style="italic")

    per = 100
    n = 6
    # такт спільний угорі обох панелей? зробимо дві панелі
    # --- панель SDR ---
    ax, ay = 90, 130
    s += text(ax, ay - 16, "SDR — одне слово за такт", 13.5, BLUE, "start", "bold")
    clk = []
    for i in range(n):
        x = ax + i * per
        clk += [(x, ay), (x, ay - 30), (x + per / 2, ay - 30), (x + per / 2, ay)]
    s += polyline(clk, INK, 2)
    s += text(ax - 8, ay - 14, "CLK", 10.5, INK, "end", "bold")
    # дані: один блок на період, на висхідному фронті
    dy = ay + 30
    for i in range(n):
        x = ax + i * per
        s += rect(x + 4, dy, per - 8, 26, PALEB, BLUE, 1.4, rx=3)
        s += text(x + per / 2, dy + 18, f"D{i}", 11, BLUE, "middle", "bold")
        s += arrow(x, ay, x, dy, GREEN, 1.2)  # тригер на фронті
    s += text(ax + n * per + 10, dy + 16, f"{n} слів", 12, BLUE, "start", "bold")

    # --- панель DDR ---
    by = ay + 150
    s += text(ax, by - 16, "DDR — слово і на висхідному, і на спадному фронті", 13.5, RED, "start", "bold")
    clk2 = []
    for i in range(n):
        x = ax + i * per
        clk2 += [(x, by), (x, by - 30), (x + per / 2, by - 30), (x + per / 2, by)]
    s += polyline(clk2, INK, 2)
    s += text(ax - 8, by - 14, "CLK", 10.5, INK, "end", "bold")
    dy2 = by + 30
    half = per / 2
    for i in range(n * 2):
        x = ax + i * half
        s += rect(x + 3, dy2, half - 6, 26, PALER, RED, 1.4, rx=3)
        s += text(x + half / 2, dy2 + 18, f"D{i}", 9.5, RED, "middle", "bold")
        # стрілки на обидва фронти
        s += arrow(x, by, x, dy2, GREEN, 1.1)
    s += text(ax + n * per + 10, dy2 + 16, f"{2*n} слів", 12, RED, "start", "bold")
    s += text(ax + n * per + 10, dy2 + 34, "за той самий час!", 10.5, RED, "start")

    s += text(W / 2, H - 22,
              "Частота тактового сигналу та сама — а пропускна здатність подвоюється. DDR2/3/4/5 розвивають ту саму ідею з усе вищими частотами.",
              12, GREEN, "middle", "bold")
    save("fig-3-8-3-3-ddr-edges.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.4 — Контролер пам'яті
# ════════════════════════════════════════════════════════════════════════════

def fig_841_controller_role():
    """Рис. 3.8.4.1 — контролер між ядром і DRAM: перекладає прості запити в складний протокол."""
    W, H = 1000, 460
    s = header(W, H)
    s += text(W / 2, 34, "Контролер пам'яті — перекладач між «дай байт» і протоколом DRAM",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Ядро хоче просто читати й писати за адресою; контролер перетворює це на ACT/RD/CAS, таймінги й регенерацію",
              12.5, GREY, "middle", style="italic")

    # ядро ліворуч
    s += chip(70, 170, 150, 110, "Ядро / шина", "read/write addr", PALEB, BLUE, BLUE)
    s += text(145, 300, "проста мова:", 11, INK, "middle")
    s += text(145, 318, "«дай слово за адресою A»", 11, BLUE, "middle", "bold")

    # контролер посередині
    cx = 360
    s += roundrect(cx, 140, 280, 200, PURPLE, 2.6, 14, fill=PALEP)
    s += text(cx + 140, 168, "Контролер пам'яті", 15, PURPLE, "middle", "bold")
    s += line(cx + 20, 180, cx + 260, 180, PURPLE, 1.4)
    duties = ["• розкласти адресу: банк / ряд / стовпець",
              "• видати ACT → RD/WR із потрібними паузами",
              "• витримати таймінги (tRCD, tRP, CAS…)",
              "• періодично слати REFRESH усім рядам",
              "• провести ініціалізацію при старті"]
    for i, d in enumerate(duties):
        s += text(cx + 18, 204 + i * 26, d, 10.8, INK, "start")

    # DRAM праворуч
    s += chip(770, 170, 160, 110, "DRAM-чіп", "ACT / RD / CAS / REF", PALER, RED, RED)
    s += text(850, 300, "складна мова:", 11, INK, "middle")
    s += text(850, 318, "команди + жорсткі таймінги", 11, RED, "middle", "bold")

    # стрілки
    s += arrow(220, 215, cx, 215, BLUE, 2.2)
    s += text((220 + cx) / 2, 205, "запит", 10.5, BLUE, "middle", "bold")
    s += arrow(cx, 255, 220, 255, GREEN, 2.2)
    s += text((220 + cx) / 2, 273, "дані", 10.5, GREEN, "middle", "bold")
    s += arrow(cx + 280, 215, 770, 215, PURPLE, 2.2)
    s += text((cx + 280 + 770) / 2, 205, "команди", 10.5, PURPLE, "middle", "bold")
    s += arrow(770, 255, cx + 280, 255, RED, 2.2)
    s += text((cx + 280 + 770) / 2, 273, "слова", 10.5, RED, "middle", "bold")

    s += text(W / 2, H - 18,
              "Ось чому DDR не підключиш до простих ніжок GPIO: між ядром і чіпом мусить стояти спеціальний контролер, що знає весь цей протокол.",
              12, INK, "middle")
    save("fig-3-8-4-1-controller-role.svg", s)


def fig_842_timings():
    """Рис. 3.8.4.2 — таймінги одного читання: ACT → tRCD → RD → CL → дані; tRP перед наступним рядом."""
    W, H = 1000, 440
    s = header(W, H)
    s += text(W / 2, 34, "Таймінги читання: чому між командами обов'язкові паузи",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Між «відкрити ряд» і «читати стовпець» мусить минути tRCD; між командою RD і даними — затримка CAS (CL)",
              12.5, GREY, "middle", style="italic")

    ox, oy = 90, 150
    per = 78
    n = 9
    # такт
    clk = []
    for i in range(n):
        x = ox + i * per
        clk += [(x, oy), (x, oy - 26), (x + per / 2, oy - 26), (x + per / 2, oy)]
    s += polyline(clk, INK, 1.8)
    s += text(ox - 8, oy - 12, "CLK", 10.5, INK, "end", "bold")
    for i in range(n):
        s += text(ox + i * per + per / 2, oy + 16, f"T{i}", 9, GREY, "middle")

    # рядок команд
    cmdy = oy + 36
    cmds = [(0, "ACT", PURPLE), (3, "RD", PURPLE), (8, "PRE", AMBER)]
    s += text(ox - 8, cmdy + 22, "CMD", 10.5, INK, "end", "bold")
    for col, lab, c in cmds:
        x = ox + col * per
        s += rect(x + 4, cmdy, per - 8, 32, "#ffffff", c, 1.6, rx=4)
        s += text(x + per / 2, cmdy + 21, lab, 11.5, c, "middle", "bold")

    # рядок даних: дані з'являються через CL після RD
    dy = oy + 96
    s += text(ox - 8, dy + 22, "DQ", 10.5, INK, "end", "bold")
    cl_start = 5  # RD на T3, CL=2 → дані з T5
    for k in range(4):
        x = ox + (cl_start + k) * per
        if (cl_start + k) < n:
            s += rect(x + 4, dy, per - 8, 30, PALEG, GREEN, 1.4, rx=4)
            s += text(x + per / 2, dy + 20, f"D{k}", 11, GREEN, "middle", "bold")

    # позначки інтервалів
    def span(x0col, x1col, y, label, col):
        x0 = ox + x0col * per + per / 2
        x1 = ox + x1col * per + per / 2
        out = line(x0, y, x1, y, col, 1.6)
        out += line(x0, y - 5, x0, y + 5, col, 1.6)
        out += line(x1, y - 5, x1, y + 5, col, 1.6)
        out += text((x0 + x1) / 2, y - 8, label, 11, col, "middle", "bold")
        return out
    s += span(0, 3, oy - 50, "tRCD (ряд готовий)", PURPLE)
    s += span(3, 5, dy + 52, "CL (затримка CAS)", GREEN)
    s += span(8, 8.0, oy - 50, "", AMBER)
    s += text(ox + 8 * per + per / 2, oy - 58, "PRE+tRP:", 10.5, AMBER, "middle", "bold")
    s += text(ox + 8 * per + per / 2, oy - 44, "закрити ряд", 9.5, AMBER, "middle")

    s += text(W / 2, H - 40,
              "Кожен інтервал — фізика конкретного чіпа (час відкриття ряду, заряд буфера). Порушиш таймінг — дані спотворяться.",
              12, INK, "middle")
    s += text(W / 2, H - 18,
              "Тому числа таймінгів (як «CL22» на модулі) контролер мусить знати наперед — звідки й береться крок ініціалізації.",
              12, GREEN, "middle", "bold")
    save("fig-3-8-4-2-timings.svg", s)


def fig_843_init_sequence():
    """Рис. 3.8.4.3 — послідовність ініціалізації + чому регенерація йде фоном вічно."""
    W, H = 1000, 430
    s = header(W, H)
    s += text(W / 2, 34, "Ініціалізація: розбудити чіп, потім вічно його регенерувати",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "До першого корисного звернення контролер веде чіп через фіксовану процедуру; далі — нескінченний фоновий refresh",
              12.5, GREY, "middle", style="italic")

    steps = [
        ("живлення +\nстабільний CLK", BLUE),
        ("витримати\nпаузу (~100 мкс)", GREY),
        ("PRECHARGE\nусіх банків", AMBER),
        ("кілька циклів\nREFRESH", GREEN),
        ("записати\nMode Register\n(CL, burst)", PURPLE),
        ("ГОТОВО:\nчитання й запис", GREEN),
    ]
    x0, y = 50, 120
    bw, bh = 138, 90
    gap = (W - 2 * x0 - len(steps) * bw) / (len(steps) - 1)
    centers = []
    for i, (lab, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        fill = PALEG if "ГОТОВО" in lab else "#ffffff"
        s += roundrect(x, y, bw, bh, col, 2.2, 10, fill=fill)
        for j, ln in enumerate(lab.split("\n")):
            s += text(x + bw / 2, y + bh / 2 - (len(lab.split("\n")) - 1) * 8 + j * 16,
                      ln, 11.5, col, "middle", "bold")
        centers.append((x + bw, x, y + bh / 2))
        if i > 0:
            px = x0 + (i - 1) * (bw + gap) + bw
            s += arrow(px, y + bh / 2, x, y + bh / 2, INK, 2)

    # фоновий refresh-цикл під останнім блоком
    fy = y + bh + 70
    s += roundrect(x0, fy, W - 2 * x0, 70, GREEN, 2, 12, dash="6,4", fill="#f4fbf5")
    s += text((W) / 2, fy + 26, "…і паралельно, поки чіп живий — контролер сам шле REFRESH кожному ряду кожні ~64 мс",
              12.5, GREEN, "middle", "bold")
    s += text((W) / 2, fy + 48, "Ваш код цього не бачить: для нього зовнішня DRAM виглядає просто як ще один шмат адрес.",
              12, INK, "middle")
    # стрілка від «ГОТОВО» вниз у цикл
    lastx = x0 + (len(steps) - 1) * (bw + gap) + bw / 2
    s += arrow(lastx, y + bh, lastx, fy, GREEN, 1.8, "4,3")

    save("fig-3-8-4-3-init-sequence.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.5 — NOR vs NAND
# ════════════════════════════════════════════════════════════════════════════

def fig_851_nor_nand_arch():
    """Рис. 3.8.5.1 — NOR (комірки паралельно, прямий доступ) vs NAND (послідовно, щільно)."""
    W, H = 1000, 500
    s = header(W, H)
    s += text(W / 2, 34, "NOR vs NAND: як з'єднані комірки — так і відрізняється характер",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "У NOR кожна комірка має прямий вихід (швидке випадкове читання); у NAND вони низкою — щільно, але доступ сторінками",
              12.5, GREY, "middle", style="italic")

    # NOR ліворуч: комірки паралельно на спільну лінію біта
    nx, ny = 90, 110
    s += roundrect(nx, ny, 380, 330, BLUE, 2.2, 14, fill=PALEB)
    s += text(nx + 190, ny + 28, "NOR — комірки паралельно", 14.5, BLUE, "middle", "bold")
    busx = nx + 60
    s += line(busx, ny + 60, busx, ny + 250, INK, 2.4)
    s += text(busx, ny + 274, "лінія біта", 10.5, INK, "middle")
    for i in range(5):
        cy = ny + 70 + i * 38
        s += circle(busx + 60, cy, 13, "#ffffff", BLUE, 1.6)
        s += text(busx + 60, cy + 4, "T", 10, BLUE, "middle", "bold")
        s += line(busx, cy, busx + 47, cy, GREY, 1.4)
        s += arrow(busx + 130, cy, busx + 73, cy, GREY, 1.2)
        s += text(busx + 136, cy + 4, f"слово {i}", 9.5, GREY, "start")
    s += text(nx + 190, ny + 290, "кожну комірку видно з шини напряму", 11, INK, "middle")
    s += text(nx + 190, ny + 312, "→ ШВИДКЕ випадкове читання будь-якого слова", 11.5, BLUE, "middle", "bold")

    # NAND праворуч: комірки послідовно в низку
    dx, dy = 550, 110
    s += roundrect(dx, dy, 380, 330, RED, 2.2, 14, fill=PALER)
    s += text(dx + 190, dy + 28, "NAND — комірки в низку", 14.5, RED, "middle", "bold")
    chainx = dx + 70
    topy = dy + 70
    s += line(chainx, topy, chainx, topy + 200, INK, 2.4)
    for i in range(6):
        cy = topy + 14 + i * 32
        s += rect(chainx - 12, cy - 10, 24, 20, "#ffffff", RED, 1.4, rx=3)
        s += text(chainx, cy + 4, "•", 12, RED, "middle", "bold")
    s += text(chainx, topy - 8, "одна низка", 10, GREY, "middle")
    s += text(chainx + 30, topy + 100, "комірки", 10.5, INK, "start")
    s += text(chainx + 30, topy + 116, "стоять", 10.5, INK, "start")
    s += text(chainx + 30, topy + 132, "ланцюгом —", 10.5, INK, "start")
    s += text(chainx + 30, topy + 148, "майже без", 10.5, INK, "start")
    s += text(chainx + 30, topy + 164, "проводів між", 10.5, INK, "start")
    s += text(chainx + 30, topy + 180, "ними", 10.5, INK, "start")
    # сторінка
    s += rect(dx + 210, dy + 70, 150, 200, "#ffffff", AMBER, 1.6, rx=6)
    s += text(dx + 285, dy + 60, "доступ — СТОРІНКАМИ", 10.5, AMBER, "middle", "bold")
    for r in range(8):
        s += line(dx + 222, dy + 90 + r * 22, dx + 348, dy + 90 + r * 22, FAINT, 0.9)
    s += text(dx + 285, dy + 250, "ціла сторінка за раз", 10, GREY, "middle")
    s += text(dx + 190, dy + 290, "тісно впаковано → дешево за біт, ВЕЛИКА ємність", 11.5, RED, "middle", "bold")
    s += text(dx + 190, dy + 312, "але читаємо/пишемо лише сторінками, не словами", 11, INK, "middle")

    save("fig-3-8-5-1-nor-nand-arch.svg", s)


def fig_852_xip_vs_storage():
    """Рис. 3.8.5.2 — XIP: процесор виконує код прямо з NOR; NAND — сховище через буфер у RAM."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "Дві ролі: виконувати код на місці (XIP) vs зберігати дані",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "NOR віддає будь-який байт миттєво, тож процесор вибирає інструкції прямо з неї; NAND спершу копіюють у RAM",
              12.5, GREY, "middle", style="italic")

    # ліворуч: NOR + XIP
    s += roundrect(70, 90, 400, 320, BLUE, 2.2, 14, fill=PALEB)
    s += text(270, 116, "NOR + XIP (execute in place)", 14.5, BLUE, "middle", "bold")
    s += chip(110, 150, 120, 80, "Процесор", "fetch", "#ffffff", INK, INK)
    s += chip(300, 150, 130, 80, "NOR-флеш", "код .text", "#ffffff", BLUE, BLUE)
    s += arrow(300, 178, 230, 178, BLUE, 2)
    s += text(265, 168, "адреса", 9.5, BLUE, "middle")
    s += arrow(230, 205, 300, 205, GREEN, 2)
    s += text(265, 225, "інструкція", 9.5, GREEN, "middle")
    s += text(270, 280, "Процесор вибирає команди ПРЯМО з NOR,", 11.5, INK, "middle")
    s += text(270, 300, "як із внутрішньої Flash (§3.6.3).", 11.5, INK, "middle")
    s += text(270, 326, "→ код не треба нікуди копіювати", 12, BLUE, "middle", "bold")
    s += text(270, 348, "→ але NOR дорога за мегабайт", 11.5, GREY, "middle")
    s += text(270, 386, "Тому в NOR тримають ПРОШИВКУ.", 12.5, BLUE, "middle", "bold")

    # праворуч: NAND як сховище
    s += roundrect(530, 90, 400, 320, RED, 2.2, 14, fill=PALER)
    s += text(730, 116, "NAND — сховище через буфер у RAM", 14.5, RED, "middle", "bold")
    s += chip(560, 150, 110, 70, "NAND", "сторінки", "#ffffff", RED, RED)
    s += chip(720, 150, 100, 70, "RAM", "буфер", "#ffffff", GREEN, GREEN)
    s += chip(850, 150, 60, 70, "ядро", "", "#ffffff", INK, INK)
    s += arrow(670, 185, 720, 185, AMBER, 2)
    s += text(695, 175, "копія", 9, AMBER, "middle")
    s += arrow(820, 185, 850, 185, GREEN, 2)
    s += text(730, 250, "Сторінку спершу КОПІЮЮТЬ у RAM,", 11.5, INK, "middle")
    s += text(730, 270, "і вже звідти з нею працює ядро.", 11.5, INK, "middle")
    s += text(730, 296, "→ виконувати код напряму НЕ можна", 12, RED, "middle", "bold")
    s += text(730, 318, "→ зате дешево й дуже ємно", 11.5, GREY, "middle")
    s += text(730, 356, "Тому в NAND тримають ДАНІ:", 12.5, RED, "middle", "bold")
    s += text(730, 378, "файли, медіа, великі масиви.", 12, INK, "middle")

    save("fig-3-8-5-2-xip-vs-storage.svg", s)


def fig_853_nor_nand_table():
    """Рис. 3.8.5.3 — порівняльна таблиця NOR vs NAND за ключовими осями."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "NOR vs NAND: коротка таблиця рішення",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Жодна не «краща» — вони для різного: одна виконує код, друга зберігає гори даних",
              12.5, GREY, "middle", style="italic")

    rows = [
        ("Властивість", "NOR", "NAND"),
        ("Випадкове читання слова", "швидке, напряму", "ні — лише сторінками"),
        ("Виконання коду (XIP)", "так", "ні (копія в RAM)"),
        ("Ємність за ту саму ціну", "менша", "велика"),
        ("Швидкість запису/стирання", "повільніша", "швидша, блоками"),
        ("Дефектні комірки", "практично немає", "є завжди (треба ECC)"),
        ("Типове застосування", "прошивка, код", "файли, медіа, SSD/SD"),
    ]
    tx, ty = 80, 90
    colw = [330, 260, 280]
    rh = 50
    xs = [tx, tx + colw[0], tx + colw[0] + colw[1]]
    for r, row in enumerate(rows):
        ry = ty + r * rh
        if r == 0:
            for j in range(3):
                col = INK if j == 0 else (BLUE if j == 1 else RED)
                s += rect(xs[j], ry, colw[j], rh, "#eef0f4", GREY, 1.6)
                s += text(xs[j] + colw[j] / 2, ry + rh / 2 + 6, row[j], 14.5, col, "middle", "bold")
        else:
            bg = "#ffffff" if r % 2 else "#fafafa"
            for j in range(3):
                s += rect(xs[j], ry, colw[j], rh, bg, FAINT, 1)
            s += text(xs[0] + 16, ry + rh / 2 + 5, row[0], 12.5, INK, "start")
            s += text(xs[1] + colw[1] / 2, ry + rh / 2 + 5, row[1], 12.5, BLUE, "middle", "bold")
            s += text(xs[2] + colw[2] / 2, ry + rh / 2 + 5, row[2], 12.5, RED, "middle", "bold")
    s += rect(tx, ty, sum(colw), len(rows) * rh, "none", GREY, 1.6)

    s += text(W / 2, H - 20,
              "Запам'ятайте різницю одним рядком: NOR — щоб ВИКОНУВАТИ, NAND — щоб ЗБЕРІГАТИ.",
              13, GREEN, "middle", "bold")
    save("fig-3-8-5-3-nor-nand-table.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.6 — SD-картка зсередини
# ════════════════════════════════════════════════════════════════════════════

def fig_861_inside_sd():
    """Рис. 3.8.6.1 — усередині SD: NAND-кристал(и) + контролер, що ховає складність."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "Усередині SD-картки: NAND-кристали плюс власний контролер",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Картка — це не «гола» пам'ять: контролер усередині веде ECC, ремонт дефектів і відображення адрес",
              12.5, GREY, "middle", style="italic")

    # корпус картки
    s += roundrect(120, 100, 540, 290, INK, 2.4, 16, fill="#f7f7f7")
    # «зрізаний кут»
    s += polygon([(120 + 40, 100), (120, 100 + 40)], fill="#ffffff", stroke=INK, sw=2.4)
    s += text(390, 126, "SD-картка (корпус)", 14, INK, "middle", "bold")

    # NAND-кристали
    s += chip(160, 160, 150, 90, "NAND-кристал", "гори комірок", PALER, RED, RED)
    s += chip(160, 270, 150, 90, "NAND-кристал", "(може бути кілька)", PALER, RED, RED)
    # контролер
    s += roundrect(360, 175, 250, 170, PURPLE, 2.6, 12, fill=PALEP)
    s += text(485, 202, "Контролер картки", 13.5, PURPLE, "middle", "bold")
    duties = ["• ECC: ловить і виправляє биті біти",
              "• ховає дефектні блоки, ставить запасні",
              "• відображає «сектори» на реальні комірки",
              "• рівномірно розкидає запис (знос)"]
    for i, d in enumerate(duties):
        s += text(375, 226 + i * 26, d, 10.5, INK, "start")
    s += arrow(310, 205, 360, 205, AMBER, 2)
    s += arrow(310, 315, 360, 315, AMBER, 2)

    # назовні — прості контакти
    s += chip(720, 200, 200, 120, "Назовні: проста шина", "«читай сектор N»", PALEG, GREEN, GREEN)
    s += arrow(610, 260, 720, 260, GREEN, 2.4)
    s += text(665, 250, "проста", 10, GREEN, "middle")
    s += text(665, 276, "команда", 10, GREEN, "middle")

    s += text(W / 2, H - 40,
              "Для вашого МК картка виглядає як проста «блокова» пам'ять: «дай сектор», «запиши сектор». Усю каверзу NAND контролер бере на себе.",
              12, INK, "middle")
    s += text(W / 2, H - 18,
              "Та сама ідея, що в §3.8.5 змушувала копіювати NAND у RAM, тут уже розв'язана — всередині картки.",
              12, GREEN, "middle", "bold")
    save("fig-3-8-6-1-inside-sd.svg", s)


def fig_862_two_modes():
    """Рис. 3.8.6.2 — SPI-режим (повільно, 1 лінія, будь-який МК) vs нативний SD (4 лінії, швидко)."""
    W, H = 1000, 460
    s = header(W, H)
    s += text(W / 2, 34, "Два способи говорити з карткою: простий SPI чи швидкий нативний SD",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Той самий чіп розуміє обидва; SPI — повільніший, зате його має кожен МК, нативний SD — ширша шина й вища швидкість",
              12.5, GREY, "middle", style="italic")

    # ліворуч: SPI
    s += roundrect(80, 100, 400, 300, BLUE, 2.2, 14, fill=PALEB)
    s += text(280, 126, "SPI-режим", 15, BLUE, "middle", "bold")
    s += chip(110, 160, 110, 70, "будь-який", "МК", "#ffffff", INK, INK)
    s += chip(360, 160, 90, 70, "картка", "", "#ffffff", BLUE, BLUE)
    # 4 лінії SPI
    spil = [("CLK", 0), ("MOSI", 1), ("MISO", 2), ("CS", 3)]
    for nm, i in spil:
        ly = 175 + i * 14
        col = GREEN if nm == "MISO" else BLUE
        s += line(220, ly, 360, ly, col, 1.6)
        s += text(290, ly - 3, nm, 8.5, col, "middle")
    s += text(280, 270, "1 лінія даних у кожний бік", 11.5, INK, "middle")
    s += text(280, 292, "проста, всюди є (§Модуль 6 — деталі SPI)", 11, GREY, "middle")
    s += text(280, 326, "→ повільніше, але працює скрізь", 12, BLUE, "middle", "bold")
    s += text(280, 350, "ідеально для дрібних МК і логів", 11.5, INK, "middle")
    s += text(280, 382, "Швидкість: одиниці МБ/с", 11.5, BLUE, "middle", "bold")

    # праворуч: нативний SD
    s += roundrect(520, 100, 400, 300, GREEN, 2.2, 14, fill=PALEG)
    s += text(720, 126, "Нативний SD-режим", 15, GREEN, "middle", "bold")
    s += chip(550, 160, 110, 70, "SD-host", "контролер", "#ffffff", PURPLE, PURPLE)
    s += chip(800, 160, 90, 70, "картка", "", "#ffffff", GREEN, GREEN)
    # 4 лінії даних
    for i in range(4):
        ly = 172 + i * 12
        s += line(660, ly, 800, ly, GREEN, 1.8)
    s += text(730, 165, "DAT0–DAT3", 8.5, GREEN, "middle", "bold")
    s += text(720, 270, "4 лінії даних паралельно + CMD + CLK", 11.5, INK, "middle")
    s += text(720, 292, "потрібен апаратний SD-контролер у МК", 11, GREY, "middle")
    s += text(720, 326, "→ помітно швидше", 12, GREEN, "middle", "bold")
    s += text(720, 350, "для відео, камер, об'ємних даних", 11.5, INK, "middle")
    s += text(720, 382, "Швидкість: десятки–сотні МБ/с", 11.5, GREEN, "middle", "bold")

    save("fig-3-8-6-2-two-modes.svg", s)


def fig_863_speed_classes():
    """Рис. 3.8.6.3 — класи швидкості: що гарантує число (мінімальний потік запису)."""
    W, H = 1000, 460
    s = header(W, H)
    s += text(W / 2, 34, "Класи швидкості: число — це ГАРАНТОВАНИЙ мінімум запису",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Маркування каже не «як швидко в піку», а «не повільніше за стільки МБ/с при безперервному записі» — це і важить для відео",
              12.5, GREY, "middle", style="italic")

    ox, oy = 130, 360
    axh = 250
    s += arrow(ox, oy, ox, oy - axh - 16, INK, 2)
    s += text(ox - 14, oy - axh - 2, "МБ/с", 12, INK, "end", "bold")
    s += text(ox - 14, oy - axh + 14, "(мін. запис)", 10, GREY, "end")

    classes = [
        ("Class 2", 2, GREY),
        ("Class 4", 4, GREY),
        ("Class 6", 6, BLUE),
        ("Class 10\nU1", 10, GREEN),
        ("U3 / V30", 30, AMBER),
        ("V60", 60, RED),
        ("V90", 90, PURPLE),
    ]
    maxv = 90
    bw = 80
    gap = 30
    x = ox + 40
    for nm, v, col in classes:
        h = axh * v / maxv
        s += rect(x, oy - h, bw, h, col, col, 0)
        s += text(x + bw / 2, oy - h - 10, f"{v}", 13, col, "middle", "bold")
        for j, ln in enumerate(nm.split("\n")):
            s += text(x + bw / 2, oy + 22 + j * 15, ln, 11, INK, "middle", "bold")
        x += bw + gap

    # лінії-вимоги застосувань
    def need(v, label, col):
        yy = oy - axh * v / maxv
        out = line(ox, yy, x, yy, col, 1.6, "6,4")
        out += text(x + 6, yy + 4, label, 11, col, "start", "bold")
        return out
    s += need(6, "Full HD відео", BLUE)
    s += need(30, "4K відео", AMBER)
    s += need(60, "4K 60 к/с / 8K", RED)

    s += text(W / 2, H - 18,
              "Запис відео не можна «доганяти» потім: якщо картка хоч на мить просіла нижче потоку — кадр загублено. Тому гарантують саме МІНІМУМ.",
              12, INK, "middle")
    save("fig-3-8-6-3-speed-classes.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.7 — eMMC і SSD якісно: FTL
# ════════════════════════════════════════════════════════════════════════════

def fig_871_ftl_layer():
    """Рис. 3.8.7.1 — FTL: прошарок, що показує систему «диск із секторів», ховаючи NAND."""
    W, H = 1000, 490
    s = header(W, H)
    s += text(W / 2, 34, "FTL — прошарок, що вдає диск над «незручною» NAND",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Зверху система бачить рівні пронумеровані сектори; знизу — реальна NAND зі сторінками, блоками й дефектами",
              12.5, GREY, "middle", style="italic")

    # верхній шар: логічні сектори
    s += roundrect(110, 90, 780, 80, GREEN, 2.2, 12, fill=PALEG)
    s += text(500, 114, "Що бачить операційна система / файлова система:", 12.5, GREEN, "middle", "bold")
    for i in range(10):
        x = 150 + i * 70
        s += rect(x, 128, 60, 30, "#ffffff", GREEN, 1.4, rx=4)
        s += text(x + 30, 148, f"{i}", 11, GREEN, "middle", "bold")
    s += text(810, 148, "сектор N", 10.5, GREEN, "middle")
    s += text(500, 184, "«рівний диск»: читай/пиши будь-який сектор, перезаписуй на місці", 11, INK, "middle")

    # середній шар: FTL
    s += roundrect(110, 210, 780, 90, PURPLE, 2.8, 14, fill=PALEP)
    s += text(500, 238, "FTL (Flash Translation Layer) — усередині контролера", 13.5, PURPLE, "middle", "bold")
    s += text(280, 264, "таблиця: логічний сектор → фізична сторінка", 11, INK, "middle")
    s += text(700, 264, "+ ховає дефекти, розкидає знос, прибирає сміття", 11, INK, "middle")
    s += text(500, 288, "увесь бруд NAND залишається тут, нагору не просочується", 11, PURPLE, "middle", "bold")

    # нижній шар: NAND
    s += roundrect(110, 340, 780, 100, RED, 2.2, 12, fill=PALER)
    s += text(500, 364, "Реальна NAND: сторінки, блоки, дефекти, обмежений ресурс", 12.5, RED, "middle", "bold")
    bx = 150
    for b in range(6):
        s += rect(bx + b * 122, 378, 110, 48, "#ffffff", RED, 1.4, rx=5)
        s += text(bx + b * 122 + 55, 372, f"блок {b}", 9, GREY, "middle")
        for p in range(4):
            pcol = AMBER if (b == 2 and p == 1) else FAINT
            s += rect(bx + b * 122 + 6 + p * 26, 398, 22, 22, "#ffffff", pcol, 1.2 if pcol == AMBER else 1)
        if b == 2:
            s += text(bx + b * 122 + 55, 436, "дефект", 8.5, AMBER, "middle", "bold")

    # стрілки між шарами
    s += arrow(500, 170, 500, 210, INK, 2)
    s += arrow(500, 300, 500, 340, INK, 2)
    s += text(520, 195, "запити секторів", 9.5, GREY, "start")
    s += text(520, 325, "операції зі сторінками", 9.5, GREY, "start")

    s += text(W / 2, H - 14,
              "Головна ідея: контролер ВДАЄ диск. eMMC, SSD і навіть SD роблять це всередині; деталі рівномірного зносу — окрема тема §4.3.3.",
              12, GREEN, "middle", "bold")
    save("fig-3-8-7-1-ftl-layer.svg", s)


def fig_872_emmc_ssd():
    """Рис. 3.8.7.2 — родина «NAND + контролер»: SD, eMMC, SSD — однакова ідея, різний масштаб."""
    W, H = 1000, 440
    s = header(W, H)
    s += text(W / 2, 34, "SD, eMMC, SSD — одна ідея в трьох масштабах",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Скрізь «NAND + контролер із FTL»; різняться корпусом, шиною, кількістю кристалів і потужністю контролера",
              12.5, GREY, "middle", style="italic")

    cards = [
        (80, "SD-картка", BLUE, PALEB,
         ["знімна, у слот", "1 контролер + 1–кілька NAND", "шина SD/SPI", "десятки МБ/с", "фото, логи, носій"]),
        (385, "eMMC", PURPLE, PALEP,
         ["впаяна в плату", "контролер+NAND в 1 корпусі", "шина як SD, ширша", "сотні МБ/с", "пам'ять телефонів, IoT"]),
        (690, "SSD", GREEN, PALEG,
         ["окремий накопичувач", "потужний контролер, RAM-кеш", "шина SATA / NVMe", "тисячі МБ/с", "ПК, сервери"]),
    ]
    for x, title, col, bg, lines in cards:
        s += roundrect(x, 90, 240, 300, col, 2.4, 14, fill=bg)
        s += text(x + 120, 120, title, 16, col, "middle", "bold")
        s += line(x + 24, 132, x + 216, 132, col, 1.4)
        for i, ln in enumerate(lines):
            s += text(x + 22, 162 + i * 34, "•", 13, col, "start", "bold")
            s += text(x + 38, 162 + i * 34, ln, 12, INK, "start")

    # стрілка «складність контролера росте»
    s += arrow(120, 410, 880, 410, GREY, 2)
    s += text(500, 432, "складність контролера, ширина шини й швидкість зростають →", 12, GREY, "middle", style="italic")

    save("fig-3-8-7-2-emmc-ssd.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.8 — EEPROM і FRAM
# ════════════════════════════════════════════════════════════════════════════

def fig_881_byte_write():
    """Рис. 3.8.8.1 — Flash пише блоками (стерти→писати), EEPROM/FRAM — окремими байтами."""
    W, H = 1000, 460
    s = header(W, H)
    s += text(W / 2, 34, "Побайтовий запис: чому для дрібних налаштувань зручніша EEPROM/FRAM",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Flash мусить СПЕРШУ стерти цілий блок, щоб змінити один байт; EEPROM і FRAM міняють окремий байт напряму",
              12.5, GREY, "middle", style="italic")

    # верх: Flash — змінити 1 байт = стерти блок
    s += text(90, 110, "Flash (NOR/NAND): один байт не змінити окремо", 13.5, RED, "start", "bold")
    fx, fy = 110, 130
    # блок із 16 байтів
    for i in range(16):
        x = fx + i * 34
        col = RED if i == 5 else "#cfcfcf"
        fill = PALER if i == 5 else "#ffffff"
        s += rect(x, fy, 30, 30, fill, col, 1.4 if i == 5 else 1, rx=3)
    s += text(fx + 5 * 34 + 15, fy - 8, "хочу змінити цей", 9.5, RED, "middle", "bold")
    s += text(fx + 8 * 34, fy + 54, "крок 1: стерти ВЕСЬ блок (усі 16 → 0xFF)", 11, AMBER, "middle", "bold")
    s += text(fx + 8 * 34, fy + 74, "крок 2: записати блок наново", 11, INK, "middle")
    s += rect(fx, fy + 88, 16 * 34 - 4, 24, "#fff7e6", AMBER, 1.4, rx=4)
    s += text(fx + 8 * 34, fy + 104, "багато зайвої роботи заради одного байта", 10.5, AMBER, "middle", style="italic")

    # низ: EEPROM/FRAM — один байт
    ey = 320
    s += text(90, ey - 16, "EEPROM / FRAM: пишемо РІВНО потрібний байт", 13.5, GREEN, "start", "bold")
    for i in range(16):
        x = fx + i * 34
        col = GREEN if i == 5 else "#cfcfcf"
        fill = PALEG if i == 5 else "#ffffff"
        s += rect(x, ey, 30, 30, fill, col, 1.4 if i == 5 else 1, rx=3)
    s += arrow(fx + 5 * 34 + 15, ey - 16, fx + 5 * 34 + 15, ey - 2, GREEN, 2)
    s += text(fx + 5 * 34 + 15, ey - 22, "записали — і все", 9.5, GREEN, "middle", "bold")
    s += text(fx + 11 * 34, ey + 50, "решта байтів недоторкані; нічого стирати", 11, GREEN, "middle", "bold")

    s += text(W / 2, H - 16,
              "Для лічильника напрацювання чи окремої уставки це безцінно: оновив одне число — і не переписав увесь блок.",
              12, INK, "middle")
    save("fig-3-8-8-1-byte-write.svg", s)


def fig_882_eeprom_vs_fram():
    """Рис. 3.8.8.2 — EEPROM vs FRAM: ресурс циклів, швидкість запису, енергія."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "EEPROM проти FRAM: де межа ресурсу й чому FRAM швидша",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "FRAM витримує практично необмежено перезаписів і пише миттєво; EEPROM дешевша, але цикли її зношують",
              12.5, GREY, "middle", style="italic")

    rows = [
        ("Вісь порівняння", "EEPROM", "FRAM"),
        ("Ресурс перезапису комірки", "~10⁴–10⁶ циклів", "~10¹²–10¹⁴ (≈ безмежно)"),
        ("Час запису байта", "мілісекунди", "як читання, наносекунди"),
        ("Енергія на запис", "помітна", "дуже мала"),
        ("Нелеткість", "так", "так"),
        ("Ціна за біт", "низька", "вища"),
        ("Коли брати", "рідкі уставки, дешево", "часті записи, лог по живленню"),
    ]
    tx, ty = 80, 92
    colw = [330, 270, 290]
    rh = 48
    xs = [tx, tx + colw[0], tx + colw[0] + colw[1]]
    for r, row in enumerate(rows):
        ry = ty + r * rh
        if r == 0:
            for j in range(3):
                col = INK if j == 0 else (BLUE if j == 1 else GREEN)
                s += rect(xs[j], ry, colw[j], rh, "#eef0f4", GREY, 1.6)
                s += text(xs[j] + colw[j] / 2, ry + rh / 2 + 6, row[j], 14, col, "middle", "bold")
        else:
            bg = "#ffffff" if r % 2 else "#fafafa"
            for j in range(3):
                s += rect(xs[j], ry, colw[j], rh, bg, FAINT, 1)
            s += text(xs[0] + 16, ry + rh / 2 + 5, row[0], 12, INK, "start")
            s += text(xs[1] + colw[1] / 2, ry + rh / 2 + 5, row[1], 12, BLUE, "middle", "bold")
            s += text(xs[2] + colw[2] / 2, ry + rh / 2 + 5, row[2], 12, GREEN, "middle", "bold")
    s += rect(tx, ty, sum(colw), len(rows) * rh, "none", GREY, 1.6)

    s += text(W / 2, H - 16,
              "FRAM сяє там, де треба часто й безпечно зберігати стан — наприклад, дописувати лічильник при кожному циклі чи рятувати дані при зникненні живлення.",
              11.5, GREEN, "middle", "bold")
    save("fig-3-8-8-2-eeprom-vs-fram.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  ТЕМА 3.8.9 — Як обрати пам'ять для проєкту
# ════════════════════════════════════════════════════════════════════════════

def fig_891_decision_tree():
    """Рис. 3.8.9.1 — дерево рішення: робоче чи сховище? великий обсяг? код? часті записи?"""
    W, H = 1000, 560
    s = header(W, H)
    s += text(W / 2, 34, "Дерево вибору: яку пам'ять додати до проєкту",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Ідіть від призначення даних; кілька питань — і ви на потрібній гілці",
              12.5, GREY, "middle", style="italic")

    def node(x, y, w, h, txt, col, fill):
        out = roundrect(x, y, w, h, col, 2.2, 10, fill=fill)
        lines = txt.split("\n")
        for j, ln in enumerate(lines):
            out += text(x + w / 2, y + h / 2 - (len(lines) - 1) * 8 + j * 16, ln,
                        11.5, col, "middle", "bold")
        return out

    # корінь
    s += node(400, 86, 200, 56, "Що це за дані?", INK, "#f3f3f3")
    # гілка 1: робочі (швидко, тимчасово)
    s += node(120, 190, 220, 64, "Робочі, швидкі,\nзникають з живленням", BLUE, PALEB)
    s += arrow(470, 142, 230, 190, INK, 1.8)
    s += text(330, 175, "робота", 10, BLUE, "middle", style="italic")
    # гілка 2: сховище (нелетке)
    s += node(640, 190, 240, 64, "Сховище: мусить\nпережити вимкнення", AMBER, "#fbf4e2")
    s += arrow(540, 142, 760, 190, INK, 1.8)
    s += text(680, 175, "зберегти", 10, AMBER, "middle", style="italic")

    # під робочими: скільки?
    s += node(70, 300, 150, 60, "До сотень КБ?", BLUE, "#ffffff")
    s += node(250, 300, 170, 60, "Мегабайти\n(кадри, відео)?", BLUE, "#ffffff")
    s += arrow(190, 254, 145, 300, GREY, 1.4)
    s += arrow(270, 254, 320, 300, GREY, 1.4)
    s += node(70, 410, 150, 56, "вистачить\nвбудованої SRAM", GREEN, PALEG)
    s += node(250, 410, 170, 56, "зовнішня\nSDRAM/DDR + контролер", GREEN, PALEG)
    s += arrow(145, 360, 145, 410, GREY, 1.4)
    s += arrow(335, 360, 335, 410, GREY, 1.4)

    # під сховищем: код? обсяг? часто?
    s += node(470, 300, 150, 60, "Виконувати\nкод (XIP)?", AMBER, "#ffffff")
    s += node(650, 300, 150, 60, "Гори даних,\nфайли?", AMBER, "#ffffff")
    s += node(830, 300, 150, 60, "Дрібні часті\nуставки?", AMBER, "#ffffff")
    s += arrow(720, 254, 545, 300, GREY, 1.4)
    s += arrow(760, 254, 725, 300, GREY, 1.4)
    s += arrow(800, 254, 905, 300, GREY, 1.4)
    s += node(470, 410, 150, 56, "NOR-флеш", GREEN, PALEG)
    s += node(650, 410, 150, 56, "NAND / SD /\neMMC", GREEN, PALEG)
    s += node(830, 410, 150, 56, "EEPROM /\nFRAM", GREEN, PALEG)
    s += arrow(545, 360, 545, 410, GREY, 1.4)
    s += arrow(725, 360, 725, 410, GREY, 1.4)
    s += arrow(905, 360, 905, 410, GREY, 1.4)

    s += text(W / 2, H - 26,
              "Перше питання завжди те саме: дані РОБОЧІ (потрібна швидка летка пам'ять) чи це СХОВИЩЕ (потрібна нелетка)? Далі — обсяг, код і частота запису.",
              12, INK, "middle")
    save("fig-3-8-9-1-decision-tree.svg", s)


def fig_892_tradeoff_map():
    """Рис. 3.8.9.2 — карта компромісів: швидкість vs ємність, з нелеткістю як кольором."""
    W, H = 1000, 540
    s = header(W, H)
    s += text(W / 2, 34, "Карта пам'ятей: швидкість проти ємності (і хто нелеткий)",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Що швидше — те зазвичай дрібніше й дорожче; сховища ємні, та повільніші. Колір — летка (синє) чи нелетка (зелене)",
              12.5, GREY, "middle", style="italic")

    ox, oy = 130, 460
    axw, axh = 760, 380
    s += arrow(ox, oy, ox + axw + 12, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh - 16, INK, 2)
    s += text(ox + axw + 6, oy + 24, "ємність →", 12.5, INK, "middle", "bold")
    s += text(ox - 90, oy - axh - 2, "швидкість", 12.5, INK, "start", "bold")
    s += text(ox - 90, oy - axh + 16, "доступу ↑", 11, GREY, "start")

    # точки: (відносна ємність 0..1, відносна швидкість 0..1, назва, летка?)
    pts = [
        (0.06, 0.97, "Регістри/кеш", True),
        (0.16, 0.86, "Вбудована SRAM", True),
        (0.55, 0.70, "SDRAM / DDR", True),
        (0.40, 0.42, "NOR-флеш", False),
        (0.10, 0.30, "EEPROM/FRAM", False),
        (0.80, 0.40, "NAND-флеш", False),
        (0.72, 0.30, "SD-картка", False),
        (0.90, 0.50, "eMMC / SSD", False),
    ]
    for cx, cy, nm, vol in pts:
        x = ox + cx * axw
        y = oy - cy * axh
        col = BLUE if vol else GREEN
        fill = PALEB if vol else PALEG
        s += circle(x, y, 10, fill, col, 2.2)
        # підпис розміщуємо так, щоб не налазив
        anchor = "start"
        ddx = 16
        if cx > 0.7:
            anchor = "end"
            ddx = -16
        s += text(x + ddx, y - 8, nm, 11.5, col, anchor, "bold")
        s += text(x + ddx, y + 8, "нелетка" if not vol else "летка", 9.5, GREY, anchor)

    # діагональна «лінія компромісу»
    s += line(ox + 0.04 * axw, oy - 0.98 * axh, ox + 0.92 * axw, oy - 0.34 * axh,
              GREY, 1.4, "7,5")
    s += text(ox + 0.5 * axw, oy - 0.5 * axh - 40, "типовий компроміс: швидше ⇄ ємніше",
              11.5, GREY, "middle", style="italic")

    # легенда
    s += rect(ox + axw - 200, oy - axh + 6, 196, 56, "#ffffff", FAINT, 1.2, rx=6)
    s += circle(ox + axw - 182, oy - axh + 24, 7, PALEB, BLUE, 2)
    s += text(ox + axw - 168, oy - axh + 28, "летка (робоча RAM)", 11, INK, "start")
    s += circle(ox + axw - 182, oy - axh + 46, 7, PALEG, GREEN, 2)
    s += text(ox + axw - 168, oy - axh + 50, "нелетка (сховище)", 11, INK, "start")

    s += text(W / 2, H - 16,
              "Реальний пристрій майже завжди поєднує кілька рівнів: швидка летка RAM для роботи + ємне нелетке сховище для того, що має лишитися.",
              12, GREEN, "middle", "bold")
    save("fig-3-8-9-2-tradeoff-map.svg", s)


def fig_893_budget_example():
    """Рис. 3.8.9.3 — приклад комплекту пам'яті для пристрою-реєстратора (worked-картинка)."""
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 34, "Приклад: комплект пам'яті для реєстратора з екраном",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "Один пристрій — кілька пам'ятей, кожна закриває свою потребу; так і збирають реальну специфікацію",
              12.5, GREY, "middle", style="italic")

    # центральний МК
    s += chip(420, 210, 160, 90, "Мікроконтролер", "ядро + трохи SRAM", "#ffffff", INK, INK)

    slots = [
        (120, 90, "Кадри екрана 320×240", "зовнішня SDRAM", "швидко, об'ємно, летко — байдуже", BLUE, PALEB, "лів"),
        (120, 330, "Прошивка (код)", "внутрішня / NOR-флеш", "XIP, не копіюючи", PURPLE, PALEP, "лів"),
        (680, 90, "Журнал вимірів (МБ)", "SD-картка", "ємно, знімно, дешево", GREEN, PALEG, "прав"),
        (680, 330, "Калібрування й лічильник", "FRAM / EEPROM", "часті дрібні записи", AMBER, "#fbf4e2", "прав"),
    ]
    for x, y, need, mem, why, col, bg, side in slots:
        s += roundrect(x, y, 200, 90, col, 2.2, 12, fill=bg)
        s += text(x + 100, y + 24, need, 11.5, INK, "middle", "bold")
        s += text(x + 100, y + 46, mem, 13, col, "middle", "bold")
        s += text(x + 100, y + 68, why, 10, GREY, "middle", style="italic")
        # стрілка до МК
        if side == "лів":
            s += arrow(x + 200, y + 45, 420, 255 if y < 200 else 255, col, 2)
        else:
            s += arrow(x, y + 45, 580, 255, col, 2)

    s += text(W / 2, H - 40,
              "Жодна окрема пам'ять не закрила б усі чотири потреби: різні вимоги — різні чіпи, зведені в один пристрій.",
              12, INK, "middle")
    s += text(W / 2, H - 18,
              "Саме так і виглядає підсумок розділу: знаєш характер даних — знаєш, яку пам'ять ставити.",
              12, GREEN, "middle", "bold")
    save("fig-3-8-9-3-budget-example.svg", s)


if __name__ == "__main__":
    # 3.8.1
    fig_811_appetite()
    fig_812_framebuffer()
    fig_813_three_loads()
    # 3.8.2
    fig_821_cell_compare()
    fig_822_leak_refresh()
    fig_823_array_rowcol()
    # 3.8.3
    fig_831_async_vs_sync()
    fig_832_banks()
    fig_833_ddr_edges()
    # 3.8.4
    fig_841_controller_role()
    fig_842_timings()
    fig_843_init_sequence()
    # 3.8.5
    fig_851_nor_nand_arch()
    fig_852_xip_vs_storage()
    fig_853_nor_nand_table()
    # 3.8.6
    fig_861_inside_sd()
    fig_862_two_modes()
    fig_863_speed_classes()
    # 3.8.7
    fig_871_ftl_layer()
    fig_872_emmc_ssd()
    # 3.8.8
    fig_881_byte_write()
    fig_882_eeprom_vs_fram()
    # 3.8.9
    fig_891_decision_tree()
    fig_892_tradeoff_map()
    fig_893_budget_example()
    print("done.")
