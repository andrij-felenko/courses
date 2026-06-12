# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки «Які ISA живуть у хобі-платах»
(до теми 3.5.4, Модуль 3). Самодостатній: палітра й хелпери скопійовані зі
стилю figs.py розділу (AUTHORING §9), щоб НЕ чіпати головний figs.py.
Вивід → ./img/.

Фігури нумеруються як у вставках (Рис. 3.5.4c.k):
  fig-18-4c-1-isa-map.svg        — карта: яка плата якою ISA говорить (ISA ≠ плата)
  fig-18-4c-2-esp32-split.svg    — розкол сімейства ESP32: Xtensa → RISC-V
  fig-18-4c-3-block-firstword.svg — блок-схема хобі-плати МК + «перший байт» (вибір ISA-цілі)
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (як у figs.py розділу) ───────────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
PALE_R = "#f6dcd9"
PALE_B = "#dfe6f6"
PALE_G = "#dcefe0"
PALE_A = "#f4ecd4"
PALE_V = "#e9e1f3"   # бліда фіалкова — третя «нейтральна» родина (Xtensa)
VIOLET = "#6b4fa0"
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
        f'  <marker id="aViolet" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOLET}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", VIOLET: "aViolet"}


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


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.5.4c.1 — карта: яка хобі-плата якою ISA говорить
#   головна думка: ISA ≠ плата. Одна ISA (ARM Cortex-M) накриває тисячі різних
#   чипів; одна родина плат (Pico 2, ESP32) уміщає різні ISA.
# ─────────────────────────────────────────────────────────────────────────────
def fig_isa_map():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 30, "Яку ISA «говорить» популярна хобі-плата", 20, INK, "middle", "bold")
    s += text(W / 2, 51, "ISA — це мова ядра, а не сама плата: одна мова накриває багато різних чипів",
              13, GREY, "middle", "normal", "italic")

    # три колонки-ISA згори
    col_y = 78
    col_h = 50
    isa_cols = [
        ("ARM Cortex-M",  "(ARMv6-M … ARMv8-M)", 60,  300, BLUE,   PALE_B),
        ("RISC-V",        "(RV32, відкрита)",     330, 250, GREEN,  PALE_G),
        ("Xtensa",        "(Tensilica, фірмова)", 600, 160, VIOLET, PALE_V),
    ]
    isa_cx = {}
    for name, sub, x, w, col, fill in isa_cols:
        s += rect(x, col_y, w, col_h, fill, col, 2.4, 8)
        s += text(x + w / 2, col_y + 22, name, 16.5, col, "middle", "bold")
        s += text(x + w / 2, col_y + 40, sub, 11.5, col, "middle", "normal", "italic")
        isa_cx[name] = (x + w / 2, col_y + col_h, col)

    # плати знизу
    board_y = 250
    board_h = 64
    boards = [
        # (назва, підпис-чип, x, w, [ISA, …])
        ("Raspberry Pi Pico",  "RP2040 · 2×Cortex-M0+", 40,  168, ["ARM Cortex-M"]),
        ("STM32-плати",        "Cortex-M0…M7/M33",      222, 150, ["ARM Cortex-M"]),
        ("Raspberry Pi Pico 2","RP2350 · M33 АБО RV",   386, 176, ["ARM Cortex-M", "RISC-V"]),
        ("ESP32-C3 / C6",      "RISC-V RV32",           576, 110, ["RISC-V"]),
        ("ESP32 / -S2 / -S3",  "Xtensa LX6 / LX7",      700, 96,  ["Xtensa"]),
    ]
    bx_c = {}
    for name, chip, x, w, isas in boards:
        s += rect(x, board_y, w, board_h, "#ffffff", INK, 1.8, 7)
        s += text(x + w / 2, board_y + 25, name, 13.5, INK, "middle", "bold")
        s += text(x + w / 2, board_y + 44, chip, 11, GREY, "middle")
        bx_c[name] = (x + w / 2, board_y, isas)

    # з'єднання плата → ISA
    for name, chip, x, w, isas in boards:
        cx = x + w / 2
        n = len(isas)
        for k, isa in enumerate(isas):
            top_cx, top_bot, col = isa_cx[isa]
            # точка виходу з плати трохи рознесена, якщо ISA дві
            off = 0 if n == 1 else (-22 if k == 0 else 22)
            s += arrow(cx + off, board_y - 2, top_cx, top_bot + 2, col, 2,
                       None if n == 1 else "5,4")

    # підпис для Pico 2 — «перемикач» (під рядом плат, не наїжджаючи на рамку)
    p2cx = bx_c["Raspberry Pi Pico 2"][0]
    s += text(p2cx, board_y + board_h + 18, "↑ перемикане ядро: M33 або RISC-V",
              10.5, AMBER, "middle", "bold")

    # контраст-врізка: Arduino Uno — інша мова (AVR), сюди не лягає
    cx0, cy0, cw0, ch0 = 40, 392, 360, 58
    s += rect(cx0, cy0, cw0, ch0, PALE_A, AMBER, 1.8, 7)
    s += text(cx0 + 14, cy0 + 22, "Для контрасту: Arduino Uno → AVR (8-біт)", 13, INK, "start", "bold")
    s += text(cx0 + 14, cy0 + 41, "ще одна, окрема мова — у цю карту 32-бітних ISA не лягає (§3.5.4).",
              11.5, INK, "start")

    # висновок-плашка
    bx1, by1, bw1, bh1 = 420, 392, 360, 58
    s += rect(bx1, by1, bw1, bh1, PALE_G, GREEN, 1.8, 7)
    s += text(bx1 + bw1 / 2, by1 + 22, "Читати згори вниз, не навпаки:", 12.5, GREEN, "middle", "bold")
    s += text(bx1 + bw1 / 2, by1 + 41, "плата → ядро → ISA. Цільову ISA й обираєш у IDE.",
              11.5, INK, "middle")

    save("fig-18-4c-1-isa-map.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.5.4c.2 — розкол сімейства ESP32: Xtensa (старі) → RISC-V (нові «C»)
#   нетривіальний факт: один бренд, дві різні ISA в межах однієї родини.
# ─────────────────────────────────────────────────────────────────────────────
def fig_esp32_split():
    W, H = 820, 440
    s = header(W, H)
    s += text(W / 2, 30, "Одна родина ESP32 — дві різні ISA", 20, INK, "middle", "bold")
    s += text(W / 2, 51, "однаковий бренд і середовище, та машинний код несумісний між гілками",
              13, GREY, "middle", "normal", "italic")

    # корінь
    rx, ry, rw, rh = W / 2 - 90, 70, 180, 44
    s += rect(rx, ry, rw, rh, FAINT, INK, 2, 8)
    s += text(W / 2, ry + 20, "Espressif ESP", 15, INK, "middle", "bold")
    s += text(W / 2, ry + 37, "сімейство Wi-Fi МК", 11, GREY, "middle")

    # дві гілки
    yL = 168   # рівень заголовків гілок
    # ── гілка Xtensa ──
    xL = 195
    s += arrow(W / 2 - 30, ry + rh, xL, yL - 8, VIOLET, 2.2)
    s += rect(xL - 130, yL, 260, 44, PALE_V, VIOLET, 2.2, 8)
    s += text(xL, yL + 20, "Гілка Xtensa (фірмова Tensilica)", 13.5, VIOLET, "middle", "bold")
    s += text(xL, yL + 37, "класичні й «великі» моделі", 11, VIOLET, "middle")
    # листя Xtensa
    leaves_x = [
        ("ESP8266", "Xtensa L106 · 80 МГц · 1 ядро"),
        ("ESP32",   "Xtensa LX6 · 240 МГц · 2 ядра"),
        ("ESP32-S2","Xtensa LX7 · 1 ядро"),
        ("ESP32-S3","Xtensa LX7 · 2 ядра"),
    ]
    ly = 236
    for i, (nm, sub) in enumerate(leaves_x):
        yy = ly + i * 46
        s += rect(xL - 150, yy, 300, 38, "#ffffff", VIOLET, 1.5, 6)
        s += text(xL - 138, yy + 16, nm, 12.5, INK, "start", "bold")
        s += text(xL - 138, yy + 32, sub, 10.8, GREY, "start")
        s += line(xL, yL + 44, xL, ly - 6, VIOLET, 1.4, "3,3") if i == 0 else ""

    # ── гілка RISC-V ──
    xR = 625
    s += arrow(W / 2 + 30, ry + rh, xR, yL - 8, GREEN, 2.2)
    s += rect(xR - 130, yL, 260, 44, PALE_G, GREEN, 2.2, 8)
    s += text(xR, yL + 20, "Гілка RISC-V (відкрита ISA)", 13.5, GREEN, "middle", "bold")
    s += text(xR, yL + 37, "новіші моделі серії «C»", 11, GREEN, "middle")
    leaves_r = [
        ("ESP32-C3", "RISC-V RV32IMC · 1 ядро"),
        ("ESP32-C6", "RISC-V · + Wi-Fi 6"),
        ("ESP32-H2", "RISC-V · Thread/Zigbee"),
    ]
    for i, (nm, sub) in enumerate(leaves_r):
        yy = ly + i * 46
        s += rect(xR - 150, yy, 300, 38, "#ffffff", GREEN, 1.5, 6)
        s += text(xR - 138, yy + 16, nm, 12.5, INK, "start", "bold")
        s += text(xR - 138, yy + 32, sub, 10.8, GREY, "start")
        s += line(xR, yL + 44, xR, ly - 6, GREEN, 1.4, "3,3") if i == 0 else ""

    # розділова «блискавка» посередині — несумісність коду
    midx = W / 2
    s += line(midx, 150, midx, 410, AMBER, 1.6, "2,6")
    s += rect(midx - 92, 250, 184, 60, PALE_A, AMBER, 1.8, 8)
    s += text(midx, 272, "Код НЕ переносний", 12.5, AMBER, "middle", "bold")
    s += text(midx, 290, "між гілками:", 11, INK, "middle")
    s += text(midx, 305, "перекомпілюй під ціль", 10.5, INK, "middle")

    save("fig-18-4c-2-esp32-split.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.5.4c.3 — блок-схема типової хобі-плати МК + «перший байт» (вибір ISA)
# ─────────────────────────────────────────────────────────────────────────────
def fig_block_firstword():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 30, "Хобі-плата МК зсередини й «перший байт»", 20, INK, "middle", "bold")
    s += text(W / 2, 51, "однаковий каркас плати; ISA живе всередині ядра — і її ж обираєш як ціль",
              13, GREY, "middle", "normal", "italic")

    # рамка-плата
    bx, by, bw, bh = 36, 74, 470, 356
    s += rect(bx, by, bw, bh, "#fafafa", INK, 2.2, 10)
    s += text(bx + 14, by + 22, "плата (модуль розробника)", 12.5, GREY, "start", "bold")

    # USB-роз'єм зліва
    ux, uy = bx, by + 150
    s += rect(ux - 14, uy, 22, 44, FAINT, INK, 1.8, 3)
    s += text(ux - 3, uy - 6, "USB", 11, INK, "middle", "bold")

    # міст USB↔UART
    brx, bry, brw, brh = bx + 40, by + 150, 96, 46
    s += rect(brx, bry, brw, brh, PALE_B, BLUE, 1.8, 6)
    s += text(brx + brw / 2, bry + 20, "USB↔UART", 11.5, BLUE, "middle", "bold")
    s += text(brx + brw / 2, bry + 37, "(або вбуд.)", 10, GREY, "middle")
    s += arrow(ux + 8, uy + 22, brx - 2, bry + 23, INK, 1.8)

    # стабілізатор 3.3 В згори
    rgx, rgy, rgw, rgh = bx + 40, by + 36, 120, 42
    s += rect(rgx, rgy, rgw, rgh, PALE_R, RED, 1.8, 6)
    s += text(rgx + rgw / 2, rgy + 18, "Стабілізатор", 11.5, RED, "middle", "bold")
    s += text(rgx + rgw / 2, rgy + 34, "5 В → 3.3 В", 11, INK, "middle")

    # ЦЕНТР: чип МК із ядром+ISA
    cx, cy, cw, ch = bx + 196, by + 110, 230, 150
    s += rect(cx, cy, cw, ch, "#ffffff", INK, 2.4, 10)
    s += text(cx + cw / 2, cy + 24, "Чип МК (SoC)", 14, INK, "middle", "bold")
    # ядро-серце з ISA
    kx, ky, kw, kh = cx + 26, cy + 40, cw - 52, 60
    s += rect(kx, ky, kw, kh, PALE_G, GREEN, 2, 8)
    s += text(kx + kw / 2, ky + 23, "ЯДРО + ISA", 13.5, GREEN, "middle", "bold")
    s += text(kx + kw / 2, ky + 42, "Cortex-M / RISC-V / Xtensa", 11, INK, "middle")
    s += text(cx + cw / 2, cy + ch - 14, "+ Flash, RAM, периферія на кристалі", 10.5, GREY, "middle")

    # живлення до чипа
    s += arrow(rgx + rgw / 2, rgy + rgh, cx + cw / 2, cy - 2, RED, 1.8)
    s += text(cx + cw / 2 + 6, cy - 8, "3.3 В", 10.5, RED, "start", "bold")
    # UART до чипа (прошивка/лог)
    s += arrow(brx + brw, bry + 23, cx - 2, ky + kh / 2, BLUE, 1.8)
    s += text((brx + brw + cx) / 2, ky + kh / 2 - 6, "прошивка/лог", 10, BLUE, "middle")

    # GPIO-гребінки по боках чипа → краї плати
    for i in range(5):
        yy = cy + 24 + i * 26
        s += line(cx + cw, yy, bx + bw - 10, yy, INK, 1.6)
        s += circle(bx + bw - 6, yy, 3, "#ffffff", INK, 1.4)
    s += text(bx + bw - 8, cy + ch + 16, "GPIO-піни", 10.5, GREY, "end", "bold")

    # рівні-нагадування
    s += text(bx + 14, by + bh - 14, "рівні логіки 3.3 В (§3.1.4) — не 5 В на входи!",
              10.5, AMBER, "start", "bold")

    # ── праворуч: «перший байт» — драбина вибору ISA-цілі ─────────────────────
    px, py, pw, ph = 528, 74, 256, 356
    s += rect(px, py, pw, ph, "#ffffff", GREY, 1.8, 10)
    s += text(px + pw / 2, py + 26, "«Перший байт»:", 15, INK, "middle", "bold")
    s += text(px + pw / 2, py + 45, "як заговорити з платою", 12, GREY, "middle", "normal", "italic")

    steps = [
        ("1. Дізнайся ядро плати", "RP2040 → ARM; ESP32-C3 → RISC-V;", "ESP32 → Xtensa."),
        ("2. Обери ту саму ISA-ціль", "у IDE: «board / target» = саме", "цей чип, не «якийсь ESP»."),
        ("3. Постав потрібний toolchain", "компілятор кодує під ISA;", "чужий дасть несумісний код."),
        ("4. Залий і поглянь у лог", "перший рядок по UART (115200)", "= плата ожила й говорить."),
    ]
    sy = py + 64
    for i, (h, l1, l2) in enumerate(steps):
        yy = sy + i * 70
        s += rect(px + 12, yy, pw - 24, 60, PALE_B if i % 2 == 0 else PALE_G,
                  BLUE if i % 2 == 0 else GREEN, 1.5, 6)
        s += text(px + 22, yy + 19, h, 12, INK, "start", "bold")
        s += text(px + 22, yy + 36, l1, 10.5, INK, "start")
        s += text(px + 22, yy + 51, l2, 10.5, INK, "start")

    save("fig-18-4c-3-block-firstword.svg", s)


if __name__ == "__main__":
    fig_isa_map()
    fig_esp32_split()
    fig_block_firstword()
    print("done.")
