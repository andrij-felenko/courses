# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 📜-вставки до теми 1.8.3 —
«1984: неодимовий магніт відкривають двічі — Сагава і Кроут».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — самодостатній скрипт).
Нумерація підписів у тексті: Рис. 1.8.3i.k (історія до теми 1.8.3).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPPER = "#cf8b5e"
ORANGE = "#e08030"
PURPLE = "#7a3ea8"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange", PURPLE: "aPurple"}


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


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.8.3i.1 — дві незалежні дороги до однієї сполуки Nd₂Fe₁₄B
#                  (Сумітомо/Сагава — спікання; GM/Кроут — гартування з розплаву),
#                  що зустрілися на одній конференції 1983-го
# ════════════════════════════════════════════════════════════════════════════
def fig_two_roads():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 30, "Одне відкриття, дві лабораторії, жодного списування",
              18, INK, "middle", "bold")
    s += text(W / 2, 51, "Японія і США незалежно дійшли до тієї самої сполуки Nd₂Fe₁₄B і зустрілися на конференції в Піттсбурзі, 1983",
              11.5, GREY, "middle", style="italic")

    # спільний старт-проблема (угорі по центру)
    s += rect(W / 2 - 235, 70, 470, 52, "#fff7e6", ORANGE, 1.6, 10)
    s += text(W / 2, 90, "СПІЛЬНА ПРОБЛЕМА (кінець 1970-х)", 12.5, ORANGE, "middle", "bold")
    s += text(W / 2, 110, "найкращий магніт — самарій-кобальт (SmCo): сильний, але самарій і кобальт дорогі й дефіцитні",
              11, INK, "middle")

    # ── ЛІВА колонка: Сумітомо / Сагава ──
    lx = 235
    s += rect(40, 150, 390, 250, "#eef2fb", BLUE, 1.8, 12)
    s += text(lx, 176, "ЯПОНІЯ · Sumitomo Special Metals", 13, BLUE, "middle", "bold")
    s += text(lx, 196, "Масато Сагава (Masato Sagawa)", 12.5, INK, "middle", "bold")
    s += text(lx, 220, "ідея: «замінити дорогі Sm і Co", 11.5, INK, "middle")
    s += text(lx, 237, "на дешеве й рясне залізо Fe»", 11.5, INK, "middle")
    s += text(lx, 261, "ключ: додати трохи бору (B ≈ 1%)", 11.5, GREEN, "middle", "bold")
    s += text(lx, 278, "→ нова стабільна тверда фаза", 11, INK, "middle")
    # метод: спікання
    s += rect(70, 296, 330, 56, "#ffffff", BLUE, 1.5, 9)
    s += text(lx, 315, "МЕТОД: спікання (sintering)", 12, BLUE, "middle", "bold")
    s += text(lx, 332, "порошок → пресування → випал у вакуумі", 10.5, INK, "middle")
    s += text(lx, 347, "(шлях від магнітів SmCo)", 10, GREY, "middle", style="italic")
    s += text(lx, 374, "дає щільні монолітні магніти —", 11, INK, "middle")
    s += text(lx, 390, "найсильніші у світі", 11, INK, "middle", "bold")

    # ── ПРАВА колонка: GM / Кроут ──
    rx = 685
    s += rect(490, 150, 390, 250, "#fdecea", RED, 1.8, 12)
    s += text(rx, 176, "США · General Motors (дослідні лаб.)", 13, RED, "middle", "bold")
    s += text(rx, 196, "Джон Кроут (John J. Croat)", 12.5, INK, "middle", "bold")
    s += text(rx, 220, "ідея: метастабільні фази зі", 11.5, INK, "middle")
    s += text(rx, 237, "швидко загартованих сплавів Nd–Fe", 11.5, INK, "middle")
    s += text(rx, 261, "ключ: той самий бор (B)", 11.5, GREEN, "middle", "bold")
    s += text(rx, 278, "→ та сама фаза Nd₂Fe₁₄B", 11, INK, "middle")
    # метод: гартування з розплаву
    s += rect(520, 296, 330, 56, "#ffffff", RED, 1.5, 9)
    s += text(rx, 315, "МЕТОД: гартування з розплаву", 12, RED, "middle", "bold")
    s += text(rx, 332, "струмінь розплаву на швидкий диск", 10.5, INK, "middle")
    s += text(rx, 347, "(melt spinning) → тонка стрічка", 10, GREY, "middle", style="italic")
    s += text(rx, 374, "дає порошок для зв'язаних", 11, INK, "middle")
    s += text(rx, 390, "(bonded) магнітів складної форми", 11, INK, "middle")

    # стрілки від спільної проблеми вниз у дві колонки
    s += arrow(W / 2 - 90, 122, lx + 70, 150, ORANGE, 1.8, "4 3")
    s += arrow(W / 2 + 90, 122, rx - 70, 150, ORANGE, 1.8, "4 3")

    # дві стрілки сходяться в одну сполуку
    s += arrow(lx, 400, W / 2 - 70, 446, BLUE, 2.4)
    s += arrow(rx, 400, W / 2 + 70, 446, RED, 2.4)

    # спільний результат — одна сполука
    s += rect(W / 2 - 200, 446, 400, 70, "#eef6ef", GREEN, 2.0, 12)
    s += text(W / 2, 470, "ОДНА Й ТА САМА СПОЛУКА:  Nd₂Fe₁₄B", 14.5, GREEN, "middle", "bold")
    s += text(W / 2, 491, "тетрагональна кристалічна ґратка; структуру визначили обидві групи 1984 року",
              11, INK, "middle")
    s += text(W / 2, 508, "оголошено разом на конференції MMM, Піттсбург, листопад 1983 — на подив одне одному",
              10.5, GREY, "middle", style="italic")
    save("hist-neo-two-roads.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.8.3i.2 — чому Nd-Fe-B переміг: дешеві й рясні елементи замість дорогих,
#                  рекордна енергія — але слабка пляма: низька температура Кюрі
# ════════════════════════════════════════════════════════════════════════════
def fig_why_and_weakness():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 30, "Чому неодим переміг — і де його слабке місце",
              18, INK, "middle", "bold")
    s += text(W / 2, 51, "Рекордна сила з дешевих елементів; розплата — найгірша теплова стійкість серед сильних магнітів",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВА панель: заміна елементів ──
    s += rect(36, 72, 410, 210, "#f7f7f7", INK, 1.4, 12)
    s += text(241, 96, "Заміна рідкісного на рясне", 13.5, INK, "middle", "bold")

    # було: SmCo
    s += text(140, 124, "БУЛО: SmCo", 12.5, RED, "middle", "bold")
    s += circle(110, 158, 22, "#fdecea", RED, 2)
    s += text(110, 163, "Sm", 13, RED, "middle", "bold")
    s += text(110, 196, "самарій —", 10, INK, "middle")
    s += text(110, 209, "рідкісний", 10, INK, "middle")
    s += circle(172, 158, 22, "#fdecea", RED, 2)
    s += text(172, 163, "Co", 13, RED, "middle", "bold")
    s += text(172, 196, "кобальт —", 10, INK, "middle")
    s += text(172, 209, "дорогий", 10, INK, "middle")

    # стрілка заміни
    s += arrow(214, 168, 268, 168, GREEN, 2.6)
    s += text(241, 156, "B", 11, GREEN, "middle", "bold")

    # стало: NdFeB
    s += text(360, 124, "СТАЛО: Nd-Fe-B", 12.5, GREEN, "middle", "bold")
    s += circle(312, 158, 22, "#eef6ef", GREEN, 2)
    s += text(312, 163, "Nd", 13, GREEN, "middle", "bold")
    s += text(312, 196, "неодим —", 10, INK, "middle")
    s += text(312, 209, "доступніший", 10, INK, "middle")
    s += circle(374, 158, 22, "#eef6ef", GREEN, 2)
    s += text(374, 163, "Fe", 13, GREEN, "middle", "bold")
    s += text(374, 196, "залізо —", 10, INK, "middle")
    s += text(374, 209, "найрясніше", 10, INK, "middle")
    s += circle(415, 134, 13, "#eef6ef", GREEN, 1.6)
    s += text(415, 139, "B", 10, GREEN, "middle", "bold")
    s += text(241, 240, "бор (B) — лише ~1% за масою,", 11, INK, "middle")
    s += text(241, 256, "але без нього потрібна фаза не утворюється", 11, GREEN, "middle", "bold")
    s += text(241, 274, "→ та сама сила за меншу ціну", 11, INK, "middle", style="italic")

    # ── ПРАВА панель: рекордна енергія (стовпчики (BH)max) ──
    s += rect(474, 72, 410, 210, "#eef6ef", GREEN, 1.4, 12)
    s += text(679, 96, "Запас енергії (BH)max — груба шкала", 13, GREEN, "middle", "bold")
    base = 250
    bx = 540
    bars = [
        ("ферит", 30, GREY),
        ("AlNiCo", 45, GREY),
        ("SmCo", 200, ORANGE),
        ("Nd-Fe-B", 400, GREEN),
    ]
    maxv = 400.0
    scale = 130.0
    for i, (lab, v, col) in enumerate(bars):
        x = bx + i * 78
        hgt = v / maxv * scale
        s += rect(x, base - hgt, 50, hgt, col, col, 1)
        s += text(x + 25, base + 16, lab, 10.5, INK, "middle",
                  "bold" if lab == "Nd-Fe-B" else "normal")
    s += line(bx - 14, base, bx + 4 * 78, base, INK, 1.4)
    s += text(679, base + 36, "Nd-Fe-B тримає найбільше поля в найменшому об'ємі —",
              10.5, INK, "middle")
    s += text(679, base + 51, "звідси крихітні навушники, жорсткі диски й мотори дронів",
              10.5, INK, "middle", style="italic")

    # ── НИЖНЯ панель: слабке місце — температура Кюрі ──
    by = 312
    s += rect(36, by, 848, 188, "#fdecea", RED, 1.6, 12)
    s += text(460, by + 24, "Слабке місце: тепло. Найнижча температура Кюрі серед сильних магнітів",
              13.5, RED, "middle", "bold")

    # шкала температур
    ax0, ax1 = 110, 800
    ay = by + 92
    s += line(ax0, ay, ax1, ay, INK, 2)
    s += arrow(ax1, ay, ax1 + 12, ay, INK, 2)
    s += text(ax1 + 16, ay + 5, "°C", 12, INK, "start", "bold")

    def tx(tc):
        return ax0 + tc / 850.0 * (ax1 - ax0)

    for tc in (0, 200, 310, 400, 600, 800):
        s += line(tx(tc), ay - 5, tx(tc), ay + 5, INK, 1.4)
        s += text(tx(tc), ay + 20, str(tc), 10, INK, "middle")

    # точки Кюрі
    s += line(tx(310), ay, tx(310), ay - 46, RED, 2)
    s += circle(tx(310), ay - 46, 5, RED, RED, 1)
    s += text(tx(310), ay - 54, "Nd-Fe-B ≈ 310 °C", 11, RED, "middle", "bold")

    s += line(tx(800), ay, tx(800), ay - 70, ORANGE, 2)
    s += circle(tx(800), ay - 70, 5, ORANGE, ORANGE, 1)
    s += text(tx(800), ay - 78, "SmCo ≈ 800 °C", 11, ORANGE, "middle", "bold")

    s += text(460, by + 156, "Вище точки Кюрі феромагнетизм зникає (з §1.8.2); та Nd-Fe-B помітно слабшає вже на сотні °C нижче.",
              10.5, INK, "middle")
    s += text(460, by + 174, "Тому в гарячих моторах беруть або SmCo, або Nd-Fe-B із домішкою диспрозію (Dy) — про класи й межі див. §1.8.3.",
              10.5, GREY, "middle", style="italic")
    save("hist-neo-why-weakness.svg", s)


if __name__ == "__main__":
    fig_two_roads()
    fig_why_and_weakness()
    print("done")
