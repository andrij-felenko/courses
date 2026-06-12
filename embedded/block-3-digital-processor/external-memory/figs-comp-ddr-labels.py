# -*- coding: utf-8 -*-
"""
Генератор SVG для 🔌-вставки «Читаємо маркування DDR-модуля» (до теми 3.8.3).
Окремий скрипт вставки — головний figs.py розділу r08 НЕ чіпаємо (AUTHORING §9).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з розділів Модуля 3 (за §9 — кожен скрипт самодостатній).
Нумерація фігур вставки: Рис. 3.8.3c.k  (файли — з суфіксом -3-8-3c-).
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
PCB = "#1f6b3a"      # колір текстоліту плати
PCBLT = "#2f8a4d"
GOLD = "#c9a227"
ORANGE = "#e08030"
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = "Consolas, 'Courier New', monospace" if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 3.8.3c.1 — розбираємо рядок «DDR4-3200 CL22» на поля ─────────────────
def fig_label_decode():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Маркування модуля: що в ньому зашифровано", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "той самий рядок із наклейки розкладаємо на три незалежні поля",
              12.5, GREY, "middle", style="italic")

    # центральний рядок маркування
    label = "PC4-25600   DDR4-3200   CL22-22-22"
    ly = 110
    s += rect(70, ly - 30, W - 140, 52, "#f3f7f3", PCB, 2, 8)
    s += text(W / 2, ly + 4, label, 23, INK, "middle", "bold", mono=True)

    # три «прапорці» вниз до пояснень
    cols = [
        # (x-центр поля у рядку, заголовок, формула/значення, пояснення-рядки, колір)
        (218, "PC4-25600", "= пік ГБ/с × 1000", ["сімейство модуля (PC4 = DDR4)",
                                                  "25600 МБ/с = 3200 × 8 байт"], GREEN),
        (468, "DDR4-3200", "тип і швидкість", ["DDR4 — покоління (з §3.8.2)",
                                               "3200 — переходів даних за",
                                               "секунду, у млн (МТ/с)"], BLUE),
        (700, "CL22", "затримка, у тактах", ["CAS Latency — пауза від",
                                            "запиту до першого слова;",
                                            "22 такти, не наносекунд!"], RED),
    ]
    boxy = 250
    bw, bh = 232, 150
    bx0 = 60
    for i, (cx, head, sub, lines, col) in enumerate(cols):
        bx = bx0 + i * (bw + 18)
        # лінія від поля рядка до блоку
        s += line(cx, ly + 26, cx, ly + 48, col, 2)
        s += arrow(cx, ly + 48, bx + bw / 2, boxy - 6, col, 2.2)
        # блок пояснення
        s += rect(bx, boxy, bw, bh, "#ffffff", col, 2.4, 10)
        s += rect(bx, boxy, bw, 30, col, col, 0, 0)
        s += text(bx + bw / 2, boxy + 21, head, 16, "#ffffff", "middle", "bold", mono=True)
        s += text(bx + bw / 2, boxy + 50, sub, 12.5, INK, "middle", style="italic")
        yy = boxy + 74
        for ln in lines:
            s += text(bx + 14, yy, ln, 12.6, INK, "start")
            yy += 19

    # нижня плашка-висновок
    cy = 440
    s += rect(60, cy - 22, W - 120, 38, "#fff7ef", ORANGE, 1.8, 8)
    s += text(W / 2, cy + 3,
              "Швидкість (3200) і затримка (CL22) — це РІЗНІ числа: одне про потік, друге про паузу перед першим словом.",
              13, INK, "middle", "bold")
    save("fig-3-8-3c-1-label-decode.svg", s)


# ── Рис. 3.8.3c.2 — клас «модуль DRAM»: з чого він зібраний ───────────────────
def fig_module_anatomy():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 32, "Клас «модуль DRAM»: плата, а не один чіп", 20, INK, "middle", "bold")
    s += text(W / 2, 53, "DIMM/SO-DIMM — це планка з кількома чіпами DRAM, спільною шиною та мікросхемою SPD",
              12.5, GREY, "middle", style="italic")

    # плата (текстоліт)
    px, py, pw, ph = 70, 95, W - 140, 150
    s += rect(px, py, pw, ph, PCB, "#0f3a1f", 2, 6)
    # ключ-проріз (вирізка в роз'ємі)
    notch_x = px + pw * 0.46
    s += rect(notch_x, py + ph - 26, 14, 26, "#ffffff", "#ffffff", 0, 0)
    s += rect(notch_x, py + ph - 26, 14, 26, "none", "#0f3a1f", 1.5, 0)

    # чіпи DRAM (8 шт.)
    nchip = 8
    cw, gap = 74, 14
    total = nchip * cw + (nchip - 1) * gap
    cx0 = px + (pw - total) / 2
    chy = py + 30
    for i in range(nchip):
        x = cx0 + i * (cw + gap)
        s += rect(x, chy, cw, 56, "#222222", "#000000", 1.5, 4)
        s += text(x + cw / 2, chy + 26, "DRAM", 11, "#dddddd", "middle", "bold")
        s += text(x + cw / 2, chy + 42, "die", 10, "#aaaaaa", "middle", style="italic")
    # підпис до ряду чіпів — над ними, по центру плати
    s += text(px + pw / 2, chy - 9, "8 однакових чіпів × по 8 біт → разом 64-бітне слово",
              13, "#eafff0", "middle", "bold")

    # SPD — маленька мікросхема в кутку
    spdx = px + 16
    s += rect(spdx, py + ph - 46, 58, 30, "#3a2a55", "#000000", 1.5, 3)
    s += text(spdx + 29, py + ph - 26, "SPD", 11, "#ffffff", "middle", "bold")
    s += text(spdx + 70, py + ph - 24, "← крихітна EEPROM: тут лежить «паспорт» планки", 12, "#eafff0", "start")

    # золоті контакти знизу
    cony = py + ph
    n = 30
    for i in range(n):
        gx = px + 18 + i * ((pw - 36) / n)
        if abs(gx - (notch_x + 7)) < 16:
            continue
        s += rect(gx, cony, 6, 12, GOLD, GOLD, 0, 1)
    s += text(px + pw / 2, cony + 30, "сотні золочених контактів: дані, адреси, команди, такт, живлення",
              12, GREY, "middle", style="italic")

    # нижній блок: що читає система ще ДО роботи з пам'яттю
    by = 330
    s += rect(70, by, W - 140, 78, "#f3f7f3", PCB, 2, 8)
    s += text(90, by + 24, "«Перший байт» тут — не з пам'яті, а з SPD:", 14, INK, "start", "bold")
    s += text(90, by + 46,
              "контролер по простій шині I²C читає з SPD-EEPROM тип, обсяг, рядки таймінгу (CL, частоту)",
              12.8, INK, "start")
    s += text(90, by + 65,
              "і лише потім, налаштувавшись за цим «паспортом», починає звертатися до самих чіпів DRAM.",
              12.8, INK, "start")
    save("fig-3-8-3c-2-module-anatomy.svg", s)


if __name__ == "__main__":
    fig_label_decode()
    fig_module_anatomy()
    print("done.")
