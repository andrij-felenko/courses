# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для історичної вставки до теми 2.9.6
«Pentium FDIV (1994): баг на пів мільярда доларів, що навчив індустрію публікувати errata».
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена fig-r09-6i-*).
Головний figs.py розділу НЕ чіпаємо; допоміжні функції скопійовано звідти (AUTHORING §9).
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
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LYEL  = "#fdf4dd"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 2.9.6i.1 — хроніка 1994-го: від тихого багу до повного відкликання ──
def fig_timeline():
    W, H = 760, 470
    s = header(W, H)
    s += text(W / 2, 30, "Хроніка FDIV: як «рідкісний» баг за три місяці став відкликанням №1",
              16, INK, "middle", "bold")

    # горизонтальна вісь часу
    ax0, ax1, ay = 70, 690, 95
    s += line(ax0, ay, ax1, ay, INK, 3)
    s += arrow(ax1 - 2, ay, ax1 + 14, ay, INK, 3)
    s += text(ax1 + 18, ay + 5, "час", 12, INK, "start", "italic")

    # події: (x, мітка-дата, заголовок, рядки опису, колір, висота картки)
    events = [
        (150, "Берез. 1994", "Pentium у продажу",
         ["Чип уже масово", "стоїть у ПК"], BLUE, "down"),
        (300, "Жовт. 1994", "Т. Найслі бачить помилку",
         ["рахунок простих чисел", "ділення «бреше»"], SUN, "up"),
        (450, "Лист. 1994", "Розголос + приклад Коу",
         ["4195835 / 3145727", "стає мемом"], SUN, "down"),
        (600, "20 груд. 1994", "Повне відкликання",
         ["заміна «без питань»", "−$475 млн"], RED, "up"),
    ]
    for x, date, title, lines, col, side in events:
        s += circle(x, ay, 7, col, INK, 2)
        if side == "up":
            cy = ay - 130
            s += line(x, ay - 7, x, cy + 62, GREY, 1.5, "3 3")
        else:
            cy = ay + 28
            s += line(x, ay + 7, x, cy, GREY, 1.5, "3 3")
        bw = 150
        bg = LRED if col == RED else (LYEL if col == SUN else LBLUE)
        s += rect(x - bw / 2, cy, bw, 92, bg, col, 2, 8)
        s += text(x, cy + 20, date, 12, col, "middle", "bold")
        s += text(x, cy + 40, title, 12.5, INK, "middle", "bold")
        for i, ln in enumerate(lines):
            s += text(x, cy + 58 + i * 16, ln, 11.5, INK, "middle")

    # нижня смуга-висновок
    by = 360
    s += rect(60, by, 640, 86, LGRN, GREEN, 2, 10)
    s += text(80, by + 26, "Що з цього лишилося галузі:", 14, GREEN, "start", "bold")
    s += text(80, by + 50,
              "складний чип завжди має відомі баги — і відповідальний виробник їх ПУБЛІКУЄ.",
              13.5, INK, "start")
    s += text(80, by + 71,
              "Так «errata sheet» / «specification update» став обов'язковим супутником даташита (§2.9.6).",
              12.5, INK, "start", style="italic")
    save("fig-r09-6i-1-timeline.svg", s)


# ── Рис. 2.9.6i.2 — механізм: п'ять порожніх клітинок таблиці ділення ─────────
def fig_table():
    W, H = 760, 460
    s = header(W, H)
    s += text(W / 2, 30, "Чому баг ховався: п'ять порожніх клітинок у таблиці ділення",
              16, INK, "middle", "bold")

    # зліва — сітка-«таблиця пошуку» (PLA) з кількома порожніми клітинками
    gx, gy = 60, 70
    cols, rows = 11, 8
    cw, ch = 24, 24
    s += text(gx, gy - 12, "Таблиця SRT: 1066 клітинок", 13, INK, "start", "bold")
    # порожні (не зашиті) клітинки — умовні позиції для ілюстрації
    holes = {(3, 2), (3, 3), (4, 2), (4, 3), (5, 3)}
    for r in range(rows):
        for c in range(cols):
            x = gx + c * cw
            y = gy + r * ch
            if (c, r) in holes:
                s += rect(x, y, cw, ch, LRED, RED, 2)
                s += text(x + cw / 2, y + cw / 2 + 4, "0", 12, RED, "middle", "bold")
            else:
                s += rect(x, y, cw, ch, LGRN, GREEN, 1)
    # рамка навколо «дірок»
    s += rect(gx + 3 * cw - 3, gy + 2 * ch - 3, 3 * cw + 6, 2 * ch + 6, "none", RED, 2.4)
    s += text(gx, gy + rows * ch + 22, "5 клітинок не зашили в чип →", 12.5, RED, "start", "bold")
    s += text(gx, gy + rows * ch + 40, "повертають 0 замість +2.", 12.5, RED, "start", "bold")
    s += text(gx, gy + rows * ch + 62, "Решта 1061 — правильні (зелені).", 12, GREEN, "start")
    s += text(gx, gy + rows * ch + 80, "Причина: помилка в скрипті", 11.5, GREY, "start", style="italic")
    s += text(gx, gy + rows * ch + 96, "переносу таблиці в PLA.", 11.5, GREY, "start", style="italic")

    # справа — наслідок: лише деякі дільники падають у дірку
    rx = 420
    s += text(rx, gy - 12, "Що відчував користувач", 13, INK, "start", "bold")
    # випадок «усе добре»
    s += rect(rx, gy + 6, 280, 78, LGRN, GREEN, 2, 8)
    s += text(rx + 14, gy + 30, "Майже завжди:", 12.5, GREEN, "start", "bold")
    s += text(rx + 14, gy + 52, "ділення влучає в зашиту клітинку", 12, INK, "start")
    s += text(rx + 14, gy + 70, "→ результат точний", 12, INK, "start")
    # випадок «рідкісне влучання»
    s += rect(rx, gy + 100, 280, 110, LRED, RED, 2, 8)
    s += text(rx + 14, gy + 124, "Зрідка (≈1 на 9 млрд):", 12.5, RED, "start", "bold")
    s += text(rx + 14, gy + 146, "операнд тягне до порожньої клітинки", 12, INK, "start")
    s += text(rx + 14, gy + 168, "4195835 / 3145727:", 12, INK, "start", "bold")
    s += text(rx + 14, gy + 186, "1.333739  замість  1.3338204…", 12.5, RED, "start", "bold")
    s += text(rx + 14, gy + 204, "помилка вже в 5-й значущій цифрі", 11.5, INK, "start", style="italic")

    # стрілка-мораль
    s += rect(rx, gy + 226, 280, 64, LYEL, SUN, 2, 8)
    s += text(rx + 14, gy + 250, "Рідкісний ≠ неможливий.", 12.5, INK, "start", "bold")
    s += text(rx + 14, gy + 270, "А «typ»-цифра з даташита тут мовчить —", 11.5, INK, "start")
    s += text(rx + 14, gy + 285, "межі шукай у дрібному шрифті й errata.", 11.5, INK, "start")
    save("fig-r09-6i-2-table.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_table()
    print("done")
