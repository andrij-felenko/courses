# -*- coding: utf-8 -*-
"""
SVG-фігури для 🔌-вставки §3.6.2c — «Карта пам'яті реального МК».
Окремий скрипт (головний figs.py розділу не чіпаємо). Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; sans-serif; стрілки через marker;
поле — зелене. Допоміжні функції — копія зі стилю figs.py розділу,
щоб вигляд між фігурами розділу був єдиний.

Підписи фігур у вставці — «Рис. 3.6.2c.k»; імена файлів — fig-19-2c-k-*.svg.
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen"}


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


def mono(x, y, s, size=14, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═══ Рис. 3.6.2c.1 — карта-«драбина» адрес реального МК з reference manual ═══
# Показуємо реальну логіку 32-бітної адреси: код-простір (Flash), потім дірки,
# потім SRAM, потім величезний блок периферії — як у таблиці RM.
def fig_ladder():
    W, H = 940, 660
    s = header(W, H)
    s += text(W / 2, 34, "Карта пам'яті в reference manual: один стовпчик адрес від 0 до верху",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "це не вигадка книги — точнісінько таку таблицю «Memory map» ви знайдете в розділі 2–3 будь-якого RM",
              11.5, GREY, "middle", style="italic")

    # вертикальна вісь адрес зліва
    ax = 250
    top, bot = 92, H - 96
    s += line(ax, top, ax, bot, GREY, 2.4)
    s += text(ax - 12, top - 6, "0xFFFF_FFFF", 11, GREY, "end", "bold")
    s += text(ax - 12, bot + 16, "0x0000_0000", 11, GREY, "end", "bold")
    s += text(ax - 150, (top + bot) / 2, "адреса", 11, GREY, "middle", style="italic")

    # смуги регіонів (зверху = вищі адреси). (base, top, колір, назва, що там, бок)
    bands = [
        (0.06, 0.205, "#fdeceb", RED,   "Периферія (APB/AHB)", "GPIO, UART, таймери, RTC — регістри керування", "0x3FF4_xxxx…", True),
        (0.205, 0.34, FAINT,    GREY,   "(не зайнято)", "дірки в просторі — туди не звертайся", "", False),
        (0.34, 0.49,  "#eef4ee", GREEN, "SRAM (внутрішня)", ".data · .bss · купа · СТЕК — змінні", "0x3FFB_0000…", True),
        (0.49, 0.62,  FAINT,    GREY,   "(не зайнято)", "", "", False),
        (0.62, 0.78,  "#eef2fb", BLUE,  "Flash / ROM (код-простір)", ".text · .rodata — програма й сталі", "0x4000_0000…", True),
        (0.78, 0.94,  FAINT,    GREY,   "(зарезервовано / кеш-вікна)", "", "", False),
    ]
    x0, bw = ax + 14, 330
    for b0, b1, bg, col, name, what, addr, big in bands:
        y1 = bot - (bot - top) * b0
        y0 = bot - (bot - top) * b1
        s += rect(x0, y0, bw, y1 - y0, bg, col if big else GREY, 2.4 if big else 1.4, 4)
        yc = (y0 + y1) / 2
        s += text(x0 + 14, yc - 3, name, 14.5 if big else 12.5, col, "start", "bold" if big else "normal")
        if what:
            s += text(x0 + 14, yc + 16, what, 11, INK if big else GREY, "start",
                      style="normal" if big else "italic")
        if big:
            s += mono(x0 + bw - 12, y1 - 8, addr, 12, col, "end", "bold")
            # стрілка-винесення праворуч
            s += arrow(x0 + bw + 12, yc, x0 + bw + 70, yc, col, 2)

    # три виноски-«що шукати» справа
    notes = [
        (RED,   "ПЕРИФЕРІЯ", "адреси, за якими НЕ пам'ять,", "а регістри заліза (§3.6.2)"),
        (GREEN, "SRAM",      "сюди лягають змінні, стек і", "купа — летка, дефіцитна"),
        (BLUE,  "FLASH",     "сюди прошивається код —", "нелетка, читається швидко"),
    ]
    nx = x0 + bw + 78
    for col, t, l1, l2 in notes:
        # позиція приблизно навпроти відповідної смуги
        yc = {RED: bot - (bot - top) * 0.13,
              GREEN: bot - (bot - top) * 0.415,
              BLUE: bot - (bot - top) * 0.70}[col]
        s += rect(nx, yc - 26, 232, 54, "#ffffff", col, 1.8, 7)
        s += text(nx + 12, yc - 7, t, 13, col, "start", "bold")
        s += text(nx + 12, yc + 9, l1, 10.5, INK, "start")
        s += text(nx + 12, yc + 23, l2, 10.5, INK, "start")

    s += rect(60, bot + 30, W - 120, 50, "#f4f7f4", GREEN, 1.6, 9)
    s += text(W / 2, bot + 50, "Ключ до читання: знайди в RM таблицю «Memory map» — у ній рядки з BASE-адресами. "
              "Три, що потрібні щодня:", 11.5, INK, "middle", "bold")
    s += text(W / 2, bot + 68, "де FLASH (код), де SRAM (змінні/стек), де PERIPHERAL (регістри). Решта — дірки й резерв; туди не лізь.",
              11, GREY, "middle", style="italic")
    save("fig-19-2c-1-ladder.svg", s)


# ═══ Рис. 3.6.2c.2 — анатомія рядка таблиці «Memory map» у RM ═══
# Вчимо ЧИТАТИ один рядок: ім'я регіону, base, end (або size), шина/доступ.
def fig_rmrow():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 34, "Як читати один рядок таблиці «Memory map»", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен рядок RM описує один регіон чотирма числами/полями — ось що означає кожне",
              11.5, GREY, "middle", style="italic")

    # заголовок таблиці
    cols = [("Регіон", 70, 235), ("Base address", 235, 415),
            ("End address", 415, 595), ("Доступ / шина", 595, 880)]
    ty = 92
    s += rect(70, ty, 810, 34, "#eef2fb", BLUE, 1.6, 5)
    for name, x0, x1 in cols:
        s += text((x0 + x1) / 2, ty + 22, name, 12.5, BLUE, "middle", "bold")
        if x0 > 70:
            s += line(x0, ty, x0, ty + 34, BLUE, 1.2)

    # один підсвічений рядок-приклад (SRAM)
    ry = ty + 34
    s += rect(70, ry, 810, 40, "#eef4ee", GREEN, 2.0, 0)
    s += text((70 + 235) / 2, ry + 25, "SRAM1", 13.5, GREEN, "middle", "bold")
    s += mono((235 + 415) / 2, ry + 25, "0x3FFB_0000", 13, INK, "middle", "bold")
    s += mono((415 + 595) / 2, ry + 25, "0x3FFD_FFFF", 13, INK, "middle", "bold")
    s += text((595 + 880) / 2, ry + 25, "R/W · data bus", 12, INK, "middle")
    for _, x0, _ in cols[1:]:
        s += line(x0, ry, x0, ry + 40, GREEN, 1.0)

    # ще два бліді рядки для контексту
    for i, (nm, b, e, acc, cc) in enumerate([
        ("Internal ROM", "0x4000_0000", "0x4005_FFFF", "R-only · instr. bus", BLUE),
        ("Peripheral", "0x3FF4_0000", "0x3FF7_FFFF", "R/W · регістри", RED),
    ]):
        yy = ry + 40 + i * 34
        s += rect(70, yy, 810, 34, "#ffffff", FAINT, 1.4, 0)
        s += text((70 + 235) / 2, yy + 22, nm, 12, cc, "middle", "bold")
        s += mono((235 + 415) / 2, yy + 22, b, 11.5, GREY, "middle")
        s += mono((415 + 595) / 2, yy + 22, e, 11.5, GREY, "middle")
        s += text((595 + 880) / 2, yy + 22, acc, 11, GREY, "middle")

    # виноски з поясненням кожного поля підсвіченого рядка
    yb = ry + 150
    fields = [
        (152, "РЕГІОН", "ім'я з RM —", "шукай SRAM/FLASH/тут"),
        (325, "BASE", "перша адреса", "регіону (звідки)"),
        (505, "END", "остання адреса;", "size = end−base+1"),
        (737, "ДОСТУП", "R/W чи R-only;", "яка шина (§3.5.7)"),
    ]
    for cx, t, l1, l2 in fields:
        s += arrow(cx, ry + 40, cx, yb - 26, INK, 1.6)
        s += rect(cx - 78, yb - 22, 156, 60, "#ffffff", INK, 1.4, 6)
        s += text(cx, yb - 4, t, 12, INK, "middle", "bold")
        s += text(cx, yb + 13, l1, 10, GREY, "middle")
        s += text(cx, yb + 27, l2, 10, GREY, "middle")

    s += rect(60, yb + 56, W - 120, 58, "#f4f7f4", GREEN, 1.6, 9)
    s += text(W / 2, yb + 78, "Розмір регіону рахуй сам: size = end − base + 1. Для SRAM вище: "
              "0x3FFD_FFFF − 0x3FFB_0000 + 1 = 0x30000 = 196 608 байт ≈ 192 КБ.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, yb + 98, "Стовпчик «доступ» підказує, що за §3.6.2 буде RO (код, сталі) чи RW (змінні): "
              "instr.-шина — це код-простір, data-шина — пам'ять даних.",
              11, GREY, "middle", style="italic")
    save("fig-19-2c-2-rmrow.svg", s)


if __name__ == "__main__":
    fig_ladder()
    fig_rmrow()
