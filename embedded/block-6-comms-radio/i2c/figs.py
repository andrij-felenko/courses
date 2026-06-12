# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 36 — «Шина I2C» (Модуль 6).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; висновок зелений;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N); для історії до розділу — секція 0 (Рис. 36.0.N).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
METAL = "#9a9aa0"
PCB   = "#1f6b4a"   # зелена плата
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LGREY = "#f3f3f3"
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


def chip(cx, cy, w, h, label, sub=None, fill="#23262b", col="#e8e8e8"):
    s = rect(cx - w / 2, cy - h / 2, w, h, fill, "#111", 1.6, 5)
    # ніжки
    for i in range(4):
        px = cx - w / 2 + w * (i + 1) / 5
        s += line(px, cy - h / 2, px, cy - h / 2 - 7, METAL, 2)
        s += line(px, cy + h / 2, px, cy + h / 2 + 7, METAL, 2)
    s += text(cx, cy + (2 if not sub else -4), label, 12.5, col, "middle", "bold")
    if sub:
        s += text(cx, cy + 13, sub, 9.5, "#b9b9b9", "middle")
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 36.0.1 — таймлайн «ланцюг рішень» ───────────────────────────────────
def fig_timeline():
    W, H = 900, 660
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг рішень: від дротового жаху телевізора до двох ліній I2C", 20, INK, "middle", "bold")
    s += text(W / 2, 60, "як потреба здешевити телевізор народила шину, що сьогодні скрізь — і чому в неї стільки імен",
              12.5, GREY, "middle", style="italic")
    spine = 230
    top, bot = 96, H - 28
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("кінець 1970-х", "Проблема в телевізорі",
         "Цифрові чіпи витісняють аналог; кожному треба керування — а паралельних дротів НЕСТЕРПНО багато", False, False),
        ("1982", "Philips Labs, Ейндговен",
         "Дві лінії на ВСІХ: SDA (дані) і SCL (такт); кожен чіп має власну адресу", False, True),
        ("1980-ті", "Торгова марка й ліцензія",
         "Назву «I²C» зареєстровано; за право робити I²C-чіп і за адреси Philips бере плату", False, False),
        ("1990-ті", "TWI та SMBus",
         "Atmel зве ту саму шину «Two-Wire Interface», Intel робить варіант SMBus — щоб обійти збір", False, False),
        ("2006", "NXP і згасання патентів",
         "Philips виокремлює NXP; згодом плату за назву скасовують, патенти спливають", False, False),
        ("Розділ 36", "Шина I2C сьогодні",
         "Ті самі два дроти: давачі, дисплеї, годинники реального часу — як із ними «заговорити»", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = GREY if dest else INK
        if accent:
            s += circle(spine, y, 10, "#fff", RED, 3)
            s += circle(spine, y, 4.5, RED, RED, 0)
        elif dest:
            s += rect(spine - 8, y - 8, 16, 16, "#fff", GREEN, 2.6, 3)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, (GREEN if dest else GREY), "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5,
                  (RED if accent else (GREEN if dest else col)), "start", "bold")
        s += text(spine + 26, y + 17, q, 12, (INK if not dest else GREY), "start", style="italic")
    save("fig-36-0-1-timeline.svg", s)


# ── Рис. 36.0.2 — дротовий жах: паралельне керування чіпами ──────────────────
def fig_problem():
    W, H = 880, 480
    s = header(W, H)
    s += text(W / 2, 36, "Дротовий жах: керувати кожним чіпом окремою паралельною шиною", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "телевізор кінця 1970-х: тюнер, звук, відео, дисплей — і до кожного жмут дротів від процесора",
              12.5, GREY, "middle", style="italic")
    # плата
    s += rect(60, 90, W - 120, 330, "#eef3ee", PCB, 2, 12)
    # процесор
    s += chip(180, 250, 110, 90, "процесор", "керує всім")
    # периферія
    chips = [("тюнер", 560, 150), ("звук", 720, 150), ("відео", 560, 350), ("дисплей", 720, 350)]
    for name, cx, cy in chips:
        s += chip(cx, cy, 96, 64, name)
        # паралельна шина: 5 ліній
        for k in range(5):
            oy = cy - 24 + k * 12
            s += line(238, 210 + k * 8, cx - 52, oy, AMBER, 1.6)
    s += text(400, 110, "≈ 5 ліній × 4 чіпи = 20+ доріжок (плюс адреси/строби)", 12, RED, "middle", "bold")

    s += rect(60, 432, W - 120, 36, LRED, RED, 1.4, 8)
    s += text(W / 2, 455, "Багато ніжок, дорога плата, тісне трасування — і так у КОЖНОМУ масовому виробі.",
              12.5, INK, "middle", "bold")
    save("fig-36-0-2-problem.svg", s)


# ── Рис. 36.0.3 — рішення: дві лінії на всіх ─────────────────────────────────
def fig_solution():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 36, "Рішення Philips: дві спільні лінії — SDA і SCL — на всі чіпи", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "кожен пристрій просто «висить» на тих самих двох дротах; розрізняють їх АДРЕСОЮ",
              12.5, GREY, "middle", style="italic")
    s += rect(60, 90, W - 120, 320, "#eef3ee", PCB, 2, 12)
    # дві шини
    sda_y, scl_y = 180, 220
    s += line(150, sda_y, 800, sda_y, RED, 3)
    s += line(150, scl_y, 800, scl_y, BLUE, 3)
    s += text(150, sda_y - 8, "SDA (дані)", 12.5, RED, "start", "bold")
    s += text(150, scl_y + 22, "SCL (такт)", 12.5, BLUE, "start", "bold")
    # підтяжки
    s += line(150, 120, 150, sda_y, INK, 2)
    s += line(120, scl_y, 120, 130, INK, 2)
    for x, yb in [(150, 120), (120, 130)]:
        s += rect(x - 8, yb - 30, 16, 26, "#fff", INK, 1.4, 3)
    s += text(135, 110, "+V", 11, RED, "middle", "bold")
    s += text(135, 96, "підтяжки", 10.5, GREY, "middle")
    # пристрої
    devs = [("процесор", 230, "master"), ("тюнер", 380, "0x60"), ("звук", 520, "0x40"),
            ("дисплей", 660, "0x3C"), ("EEPROM", 770, "0x50")]
    for name, cx, addr in devs:
        s += chip(cx, 320, 90, 56, name, addr)
        s += line(cx - 16, 292, cx - 16, sda_y, RED, 2)
        s += line(cx + 16, 292, cx + 16, scl_y, BLUE, 2)

    s += rect(60, 424, W - 120, 38, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, 448, "20+ доріжок → ДВІ. Додати пристрій = просто причепити його до тих самих ліній і дати адресу.",
              12, INK, "middle", "bold")
    save("fig-36-0-3-solution.svg", s)


# ── Рис. 36.0.4 — сага імен: I2C / TWI / SMBus ───────────────────────────────
def fig_naming():
    W, H = 880, 450
    s = header(W, H)
    s += text(W / 2, 36, "Сага імен: чому та сама шина зветься по-різному", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "«I²C» — торгова марка Philips із ліцензійним збором; інші робили сумісне під своїми назвами",
              12.5, GREY, "middle", style="italic")
    # корінь
    s += rect(330, 96, 220, 60, LGREY, INK, 2, 10)
    s += text(440, 122, "та сама дворотова шина", 13, INK, "middle", "bold")
    s += text(440, 142, "SDA + SCL, адреси, ACK", 10.5, GREY, "middle")
    # три гілки
    branches = [
        (150, "I²C", "Philips / NXP", "оригінал; назва — торгова\nмарка, за яку платили", RED, LRED),
        (440, "TWI", "Atmel (AVR)", "«Two-Wire Interface» —\nщоб обійти ліцензію", "#b08900", "#fbf3df"),
        (730, "SMBus", "Intel (ПК)", "варіант I²C для керування\nживленням, суворіші таймінги", BLUE, LBLUE),
    ]
    for cx, name, who, note, col, fill in branches:
        s += arrow(440, 156, cx, 214, GREY, 1.8)
        s += rect(cx - 110, 216, 220, 110, fill, col, 2, 10)
        s += text(cx, 244, name, 17, col, "middle", "bold")
        s += text(cx, 266, who, 11.5, INK, "middle", "bold")
        for j, ln in enumerate(note.split("\n")):
            s += text(cx, 288 + j * 16, ln, 10.5, GREY, "middle")

    s += rect(60, 366, W - 120, 66, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 390, "Тому на даташиті AVR ти бачиш «TWI», а не «I²C» — це той самий протокол, лише без торгової назви.",
              12, INK, "middle", "bold")
    s += text(W / 2, 412, "Сьогодні патенти згасли, плату за назву скасовано — лишився переважно логотип як марка.",
              11.5, GREY, "middle", style="italic")
    save("fig-36-0-4-naming.svg", s)


# ── Рис. 36.0.5 — як шина росла: швидкості й адреси ──────────────────────────
def fig_evolution():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 36, "Як шина росла: швидкості й адресний простір", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "ядро лишилося тим самим — додавали лише швидші режими й ширші адреси",
              12.5, GREY, "middle", style="italic")
    ox, oy, axw = 110, 300, 700
    s += line(ox, oy, ox + axw, oy, INK, 2)
    s += text(ox + axw, oy + 22, "час →", 12, INK, "start")
    steps = [
        ("1982", "Standard", "100 кГц", "7-біт · 112 пристроїв", RED),
        ("1992", "Fast", "400 кГц", "+ 10-біт адреси", "#b08900"),
        ("1998", "High-speed", "3.4 МГц", "великі потоки", BLUE),
        ("2007", "Fast-mode+", "1 МГц", "простий і швидкий", GREEN),
    ]
    n = len(steps)
    for i, (yr, mode, spd, note, col) in enumerate(steps):
        x = ox + 60 + (axw - 120) * i / (n - 1)
        s += circle(x, oy, 7, "#fff", col, 2.6)
        s += text(x, oy + 24, yr, 12, GREY, "middle", "bold")
        by = oy - 150
        s += rect(x - 78, by, 156, 96, "#fbfbfb", col, 1.8, 10)
        s += text(x, by + 24, mode, 13.5, col, "middle", "bold")
        s += text(x, by + 48, spd, 14, INK, "middle", "bold")
        s += text(x, by + 70, note, 10, GREY, "middle")
        s += line(x, by + 96, x, oy - 8, col, 1.4, dash="3,3")

    s += rect(60, 354, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 378, "Старий 100-кГц чіп 1982 року й сучасний прекрасно живуть на одній шині — сумісність зберегли.",
              12, INK, "middle", "bold")
    s += text(W / 2, 399, "Саме ця стабільність ядра й зробила I2C всюдисущою на десятиліття.",
              11.5, GREY, "middle", style="italic")
    save("fig-36-0-5-evolution.svg", s)


# ============================================================================
#  §36.1 — Двопровідна шина: лінія даних і лінія такту
# ============================================================================
def _wave(x0, y_hi, y_lo, unit, segs, color=INK, w=2.6):
    """segs: список (level, width_units). 1=високо, 0=низько. Повертає (svg, centers)."""
    s = ""
    x = x0
    prev = None
    centers = []
    for level, wid in segs:
        y = y_hi if level else y_lo
        xe = x + wid * unit
        if prev is not None and prev != level:
            s += line(x, y_hi, x, y_lo, color, w)
        s += line(x, y, xe, y, color, w)
        centers.append(((x + xe) / 2, level, x, xe))
        prev = level
        x = xe
    return s, centers


def _pullup(x, y_top, y_bus, label):
    s = line(x, y_top, x, y_top + 14, INK, 2)
    s += rect(x - 7, y_top + 14, 14, 26, "#fff", INK, 1.5, 3)
    s += line(x, y_top + 40, x, y_bus, INK, 2)
    s += text(x, y_top - 4, "+V", 11, RED, "middle", "bold")
    s += text(x + 12, y_top + 30, label, 10.5, GREY, "start")
    return s


# ── Рис. 36.1.1 — топологія шини: дві лінії, ведучий і ведені ─────────────────
def fig11_topology():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Двопровідна шина: SDA, SCL і багато пристроїв на них", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "один ведучий задає такт і починає обмін; ведені відгукуються за своєю адресою",
              12.5, GREY, "middle", style="italic")
    sda_y, scl_y = 150, 188
    s += line(150, sda_y, 850, sda_y, RED, 3)
    s += line(150, scl_y, 850, scl_y, BLUE, 3)
    s += text(858, sda_y + 4, "SDA", 12.5, RED, "start", "bold")
    s += text(858, scl_y + 4, "SCL", 12.5, BLUE, "start", "bold")
    # підтяжки
    s += _pullup(120, 96, sda_y, "Rp")
    s += _pullup(96, 100, scl_y, "Rp")
    # пристрої
    devs = [("ведучий\n(MCU)", 230, "master", GREEN),
            ("гіроскоп", 400, "0x68", INK),
            ("баро", 540, "0x76", INK),
            ("дисплей", 680, "0x3C", INK),
            ("EEPROM", 800, "0x50", INK)]
    for name, cx, addr, col in devs:
        nm = name.split("\n")
        s += rect(cx - 48, 260, 96, 66, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 8)
        for j, ln in enumerate(nm):
            s += text(cx, 286 + j * 15 - (len(nm) - 1) * 7, ln, 11.5, col, "middle", "bold")
        s += text(cx, 318, addr, 10.5, ("#7a7a7a" if col != GREEN else GREEN), "middle", style="italic")
        s += line(cx - 16, 260, cx - 16, sda_y, RED, 2)
        s += line(cx + 16, 260, cx + 16, scl_y, BLUE, 2)
    s += rect(60, 360, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 384, "Усі — на тих самих двох лініях. SCL веде ведучий; SDA по черзі тримає той, хто зараз говорить.",
              12, INK, "middle", "bold")
    s += text(W / 2, 404, "У спокої обидві лінії високі (підтяжки Rp); пристрої вміють лише ПРИТЯГУВАТИ їх до нуля.",
              11.5, GREY, "middle", style="italic")
    save("fig-36-1-1-topology.svg", s)


# ── Рис. 36.1.2 — синхронно: такт несе час (на відміну від UART) ─────────────
def fig12_sync():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Синхронна шина: окрема лінія такту несе час", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "на відміну від UART, тут не треба наперед домовлятися про швидкість — її задає SCL",
              12.5, GREY, "middle", style="italic")
    x0, unit = 170, 56
    s += text(x0 - 16, 130, "SCL", 12.5, BLUE, "end", "bold")
    clk = []
    for _ in range(6):
        clk += [(0, 0.5), (1, 0.5)]
    s += _wave(x0, 112, 148, unit, clk, BLUE, 2.6)[0]
    s += text(x0 - 16, 210, "SDA", 12.5, RED, "end", "bold")
    bits = [1, 0, 1, 1, 0, 0]
    s += _wave(x0, 192, 228, unit, [(b, 1.0) for b in bits], RED, 2.6)[0]
    # точки вибірки на високому SCL
    for k in range(6):
        sx = x0 + (k + 0.5) * unit
        s += line(sx, 112, sx, 228, GREEN, 1, dash="3,3")
        s += arrow(sx, 258, sx, 230, GREEN, 1.5)
    s += text(x0 + 3 * unit, 278, "↑ ведений бере відлік, поки SCL високий", 11.5, GREEN, "middle", "bold")

    s += rect(520, 96, 350, 70, LGREY, GREY, 1.3, 10)
    s += text(695, 120, "UART (§35): такту нема", 12, INK, "middle", "bold")
    s += text(695, 140, "→ обидві сторони мусять", 11, GREY, "middle")
    s += text(695, 156, "наперед збігтися у baud", 11, GREY, "middle")

    s += rect(60, 348, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 372, "Такт у дроті знімає потребу в спільному baud: ведучий може йти повільно чи швидко — ведений встигне.",
              12, INK, "middle", "bold")
    s += text(W / 2, 392, "Ціна — третій дріт (SCL) проти UART; зате на ньому вживається БАГАТО пристроїв.",
              11.5, GREY, "middle", style="italic")
    save("fig-36-1-2-sync.svg", s)


# ── Рис. 36.1.3 — фундаментальне правило: дані дійсні при високому SCL ────────
def fig13_datavalid():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Головне правило I2C: дані на SDA стабільні, поки SCL високий", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "SDA дозволено мінятися ЛИШЕ коли SCL низький; коли SCL високий — біт читають",
              12.5, GREY, "middle", style="italic")
    x0, unit = 150, 90
    bits = [1, 0, 1, 0]
    # SCL
    s += text(x0 - 16, 130, "SCL", 12.5, BLUE, "end", "bold")
    clk = []
    for _ in bits:
        clk += [(0, 0.5), (1, 0.5)]
    s += _wave(x0, 112, 150, unit, clk, BLUE, 2.6)[0]
    # SDA: міняється під час low, тримається під час high
    s += text(x0 - 16, 215, "SDA", 12.5, RED, "end", "bold")
    sda = []
    for b in bits:
        sda += [(b, 0.5), (b, 0.5)]
    s += _wave(x0, 196, 234, unit, sda, RED, 2.6)[0]
    # вікна «дійсно» (high) і «можна міняти» (low)
    for k in range(len(bits)):
        hx0 = x0 + (k + 0.5) * unit
        s += rect(hx0, 188, unit / 2, 54, "#eef6ef", GREEN, 1.2)
        s += rect(x0 + k * unit, 188, unit / 2, 54, "#f3f3f3", GREY, 1)
    s += text(x0 + 0.75 * unit, 262, "дійсно", 10.5, GREEN, "middle", "bold")
    s += text(x0 + 0.25 * unit, 262, "зміна", 10.5, GREY, "middle")
    s += text(x0 + 2.5 * unit, 280, "зелене — SCL високий: SDA читають   ·   сіре — SCL низький: SDA готують",
              11, INK, "middle", "bold")

    s += rect(60, 352, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 376, "Це правило — основа всього I2C: біт «знімають», поки такт високий, тож SDA саме тоді мусить стояти.",
              12, INK, "middle", "bold")
    s += text(W / 2, 396, "Виняток — навмисна зміна SDA при високому SCL: це сигнали СТАРТ і СТОП (§36.4).",
              11.5, GREY, "middle", style="italic")
    save("fig-36-1-3-datavalid.svg", s)


# ── Рис. 36.1.4 — один біт зблизька: підготувати при low, зняти при high ─────
def fig14_bit():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Один біт зблизька: підготувати на низькому такті, зняти на високому", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "поки SCL низький — той, хто говорить, виставляє біт; SCL піднявся — інший його зчитує",
              12.5, GREY, "middle", style="italic")
    x0, unit = 200, 200
    s += text(x0 - 16, 140, "SCL", 12.5, BLUE, "end", "bold")
    s += _wave(x0, 120, 168, unit, [(0, 0.5), (1, 1.0), (0, 0.5)], BLUE, 2.8)[0]
    s += text(x0 - 16, 235, "SDA", 12.5, RED, "end", "bold")
    s += _wave(x0, 216, 264, unit, [(1, 0.4), (0, 1.6)], RED, 2.8)[0]
    # фази
    s += rect(x0, 290, unit * 0.5, 28, "#f3f3f3", GREY, 1, 4)
    s += text(x0 + unit * 0.25, 309, "виставити SDA", 10.5, GREY, "middle", "bold")
    s += rect(x0 + unit * 0.5, 290, unit, 28, "#eef6ef", GREEN, 1.2, 4)
    s += text(x0 + unit, 309, "SCL високий → зчитування", 11, GREEN, "middle", "bold")
    s += rect(x0 + unit * 1.5, 290, unit * 0.5, 28, "#f3f3f3", GREY, 1, 4)
    s += text(x0 + unit * 1.75, 309, "готувати наступний", 10, GREY, "middle")
    # стрілка зчитування
    sx = x0 + unit
    s += line(sx, 120, sx, 264, GREEN, 1, dash="3,3")
    s += arrow(sx, 350, sx, 266, GREEN, 1.8)
    s += text(sx, 366, "відлік біта", 11, GREEN, "middle", "bold")

    s += rect(60, 340, 150, 36, "none", "none", 0)  # spacer
    save("fig-36-1-4-bit.svg", s)


# ── Рис. 36.1.5 — ролі: ведучий веде такт, ведений відгукується ──────────────
def fig15_roles():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Ролі на шині: ведучий веде такт, ведений відгукується", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ведучий (master/controller) завжди керує SCL і починає обмін; SDA тримають по черзі",
              12.5, GREY, "middle", style="italic")
    s += rect(90, 110, 200, 150, "#eef6ef", GREEN, 2.2, 12)
    s += text(190, 138, "ВЕДУЧИЙ", 14, GREEN, "middle", "bold")
    s += text(190, 158, "(master / controller)", 10.5, GREY, "middle")
    s += text(110, 186, "• завжди генерує SCL", 11, INK, "start")
    s += text(110, 208, "• починає й завершує обмін", 11, INK, "start")
    s += text(110, 230, "• називає адресу ВЕДЕНОГО", 11, INK, "start")
    s += rect(590, 110, 200, 150, "#fbfbfb", INK, 2.2, 12)
    s += text(690, 138, "ВЕДЕНИЙ", 14, INK, "middle", "bold")
    s += text(690, 158, "(slave / target)", 10.5, GREY, "middle")
    s += text(610, 186, "• слухає свою адресу", 11, INK, "start")
    s += text(610, 208, "• відповідає (ACK, дані)", 11, INK, "start")
    s += text(610, 230, "• такт не генерує*", 11, INK, "start")
    # лінії
    s += arrow(290, 150, 590, 150, BLUE, 2.4)
    s += text(440, 140, "SCL (такт) — лише від ведучого", 11, BLUE, "middle", "bold")
    s += arrow(290, 200, 590, 200, RED, 2.2)
    s += arrow(590, 224, 290, 224, RED, 2.2)
    s += text(440, 192, "SDA (дані) — по черзі в обидва боки", 11, RED, "middle", "bold")

    s += rect(60, 300, W - 120, 80, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 324, "Зазвичай ведучий — мікроконтролер, ведені — давачі та дисплеї.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 346, "* виняток: ведений може ПРИТРИМАТИ такт (clock stretching) — про це у §36.6.", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, 366, "Сучасна специфікація вживає «controller/target», даташити досі — «master/slave».", 11, GREY, "middle", style="italic")
    save("fig-36-1-5-roles.svg", s)


# ── Рис. 36.1.6 — напівдуплекс проти повного дуплексу UART ───────────────────
def fig16_duplex():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Напівдуплекс I2C проти повного дуплексу UART", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "одна лінія даних → говорять по черзі; дві лінії → можна одночасно в обидва боки",
              12.5, GREY, "middle", style="italic")
    # I2C
    s += rect(60, 90, 360, 200, "none", FAINT, 2, 12)
    s += text(240, 116, "I2C: одна SDA — по черзі", 13, INK, "middle", "bold")
    s += rect(90, 150, 90, 60, "#eef6ef", GREEN, 2, 8); s += text(135, 185, "ведучий", 11.5, GREEN, "middle", "bold")
    s += rect(300, 150, 90, 60, "#fbfbfb", INK, 2, 8); s += text(345, 185, "ведений", 11.5, INK, "middle", "bold")
    s += arrow(180, 170, 300, 170, RED, 2.2)
    s += text(240, 162, "то так…", 10.5, RED, "middle", "bold")
    s += arrow(300, 196, 180, 196, RED, 2.2)
    s += text(240, 212, "…то так (не водночас)", 10.5, RED, "middle", "bold")

    # UART
    s += rect(460, 90, 360, 200, "none", FAINT, 2, 12)
    s += text(640, 116, "UART: TX і RX — водночас", 13, INK, "middle", "bold")
    s += rect(490, 150, 90, 60, "#fbfbfb", INK, 2, 8); s += text(535, 185, "A", 12, INK, "middle", "bold")
    s += rect(700, 150, 90, 60, "#fbfbfb", INK, 2, 8); s += text(745, 185, "B", 12, INK, "middle", "bold")
    s += arrow(580, 166, 700, 166, BLUE, 2.2)
    s += text(640, 158, "TX →", 10.5, BLUE, "middle", "bold")
    s += arrow(700, 194, 580, 194, GREEN, 2.2)
    s += text(640, 210, "← RX (одночасно)", 10.5, GREEN, "middle", "bold")

    s += rect(60, 312, W - 120, 50, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 337, "I2C економить лінію ціною одночасності: у кожну мить говорить лише ОДИН бік SDA.",
              12, INK, "middle", "bold")
    save("fig-36-1-6-duplex.svg", s)


# ── Рис. 36.1.7 — I2C проти UART: коротке зведення ───────────────────────────
def fig17_vs_uart():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "I2C проти UART: дві різні відповіді на «як зв'язати чіпи»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "не «краще/гірше», а різні компроміси під різні задачі",
              12.5, GREY, "middle", style="italic")
    rows = [
        ("такт", "немає (асинхронно)", "окрема лінія SCL"),
        ("домовленість про baud", "потрібна", "не потрібна"),
        ("скільки пристроїв", "2 (точка-точка)", "багато на спільній шині"),
        ("дуплекс", "повний (TX+RX)", "напів (одна SDA)"),
        ("дроти", "2 на кожен лінк", "2 на всіх разом"),
        ("типова швидкість", "до ~1–3 Мбіт/с", "100 к…3.4 МГц"),
    ]
    bx, by, rw = 70, 92, 740
    s += rect(bx, by, rw, 36, "#f0f0f0", GREY, 1.3, 8)
    s += text(bx + 16, by + 23, "ознака", 12, INK, "start", "bold")
    s += text(bx + 270, by + 23, "UART (§35)", 12, INK, "start", "bold")
    s += text(bx + 520, by + 23, "I2C", 12, GREEN, "start", "bold")
    yy = by + 36
    for feat, u, i in rows:
        s += rect(bx, yy, rw, 40, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 25, feat, 12, INK, "start", "bold")
        s += text(bx + 270, yy + 25, u, 11.5, GREY, "start")
        s += text(bx + 520, yy + 25, i, 11.5, INK, "start")
        yy += 40

    s += rect(60, 354, W - 120, 50, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 379, "UART — для зв'язку «точка-точка» (модуль, ПК); I2C — щоб повісити багато дрібних чіпів на дві лінії.",
              11.5, INK, "middle", "bold")
    save("fig-36-1-7-vs-uart.svg", s)


# ============================================================================
#  §36.2 — Відкритий колектор і підтяжки
# ============================================================================
def _gnd(cx, y, color=INK):
    s = line(cx, y, cx, y + 10, color, 2)
    s += line(cx - 13, y + 10, cx + 13, y + 10, color, 2.2)
    s += line(cx - 8, y + 15, cx + 8, y + 15, color, 2.2)
    s += line(cx - 3, y + 20, cx + 3, y + 20, color, 2.2)
    return s


def _nmos(cx, top, bot, on):
    """Спрощений N-канальний ключ до землі: тягне вузол (cx,top) до GND (cx,bot)."""
    col = GREEN if on else GREY
    midy = (top + bot) / 2
    s = line(cx, top, cx, midy - 18, INK, 2)                 # drain
    s += line(cx, midy + 18, cx, bot, INK, 2)                # source
    s += line(cx - 4, midy - 20, cx - 4, midy + 20, INK, 3)  # канал
    s += line(cx - 18, midy, cx - 9, midy, INK, 2)           # затвор-провід
    s += line(cx - 9, midy - 16, cx - 9, midy + 16, INK, 2.4)  # затвор
    s += text(cx - 22, midy + 4, "G", 10.5, GREY, "end", "bold")
    if on:
        s += text(cx + 10, midy + 4, "ON → тягне 0", 10.5, GREEN, "start", "bold")
    else:
        s += text(cx + 10, midy + 4, "OFF → відпускає", 10.5, GREY, "start")
    s += _gnd(cx, bot, INK)
    return s


# ── Рис. 36.2.1 — чому не можна зводити звичайні виходи ───────────────────────
def fig21_contention():
    W, H = 880, 410
    s = header(W, H)
    s += text(W / 2, 34, "Чому не можна з'єднати звичайні (двотактні) виходи", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "якщо один жене «1» (VCC), а інший «0» (GND), струм тече навпростець — коротке замикання",
              12.5, GREY, "middle", style="italic")
    # дві двотактні виходи з'єднані
    s += rect(120, 150, 150, 120, "#fbfbfb", INK, 2, 10)
    s += text(195, 178, "пристрій A", 12, INK, "middle", "bold")
    s += text(195, 200, "жене «1»", 12, RED, "middle", "bold")
    s += text(195, 222, "(вихід на VCC)", 10, GREY, "middle")
    s += rect(610, 150, 150, 120, "#fbfbfb", INK, 2, 10)
    s += text(685, 178, "пристрій Б", 12, INK, "middle", "bold")
    s += text(685, 200, "жене «0»", 12, BLUE, "middle", "bold")
    s += text(685, 222, "(вихід на GND)", 10, GREY, "middle")
    s += line(270, 210, 610, 210, INK, 3)
    s += text(440, 196, "спільна лінія", 11, INK, "middle", "bold")
    # струм короткого
    s += arrow(300, 230, 560, 230, RED, 3)
    s += text(440, 250, "⚡ великий наскрізний струм VCC → GND", 12, RED, "middle", "bold")
    s += text(440, 268, "обидва виходи перегріваються й можуть згоріти", 10.5, GREY, "middle", style="italic")

    s += rect(60, 320, W - 120, 56, LRED, RED, 1.4, 10)
    s += text(W / 2, 344, "Двотактний (push-pull) вихід уміє і тягти вгору, і вниз — тому два таких на одній лінії конфліктують.",
              12, INK, "middle", "bold")
    s += text(W / 2, 364, "Спільна шина потребує виходів, що НЕ вміють тягти вгору. Це й є відкритий колектор.",
              11.5, GREY, "middle", style="italic")
    save("fig-36-2-1-contention.svg", s)


# ── Рис. 36.2.2 — відкритий колектор: тягне вниз або відпускає ────────────────
def fig22_opendrain():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Відкритий колектор/стік: вихід уміє лише тягти ВНИЗ або відпускати", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "це N-канальний ключ (Розділ 12): затвор увімкнув — лінія до нуля; вимкнув — лінія вільна (Z)",
              12.5, GREY, "middle", style="italic")
    # стан ON
    s += rect(70, 90, 360, 290, "none", FAINT, 2, 12)
    s += text(250, 116, "затвор ON", 13.5, GREEN, "middle", "bold")
    s += line(150, 150, 350, 150, INK, 3)
    s += text(250, 140, "лінія", 11, INK, "middle")
    s += _nmos(250, 150, 330, True)
    s += text(250, 360, "лінію притягнуто до 0", 11.5, GREEN, "middle", "bold")
    # стан OFF
    s += rect(470, 90, 360, 290, "none", FAINT, 2, 12)
    s += text(650, 116, "затвор OFF", 13.5, GREY, "middle", "bold")
    s += line(550, 150, 750, 150, INK, 3)
    s += text(650, 140, "лінія", 11, INK, "middle")
    s += _nmos(650, 150, 330, False)
    s += text(650, 360, "лінія «відпущена» (висок. імпеданс)", 11, GREY, "middle", "bold")
    # хрест на «штовхнути вгору»
    s += text(650, 200, "✗ вгору не штовхає", 11, RED, "middle", "bold")

    s += rect(60, 388, 1, 1, "none", "none", 0)
    save("fig-36-2-2-opendrain.svg", s)


# ── Рис. 36.2.3 — підтяжка й монтажне «І» ────────────────────────────────────
def fig23_wiredand():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Підтяжка тримає лінію високою; хто тягне вниз — той і перемагає", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "результат — монтажне «І» (wired-AND): лінія низька, якщо ХОЧ ОДИН тягне; висока — лише коли ВСІ відпустили",
              12, GREY, "middle", style="italic")
    # підтяжка
    s += text(150, 120, "+V", 12, RED, "middle", "bold")
    s += line(150, 128, 150, 150, INK, 2)
    s += rect(143, 150, 14, 28, "#fff", INK, 1.6, 3)
    s += text(170, 168, "Rp (підтяжка)", 11, GREY, "start")
    s += line(150, 178, 150, 230, INK, 2)
    s += line(150, 230, 700, 230, INK, 3)
    s += text(710, 234, "лінія", 12, INK, "start", "bold")
    # два ключі
    s += _nmos(320, 230, 320, False)
    s += text(320, 348, "A: відпустив", 10.5, GREY, "middle")
    s += _nmos(520, 230, 320, True)
    s += text(520, 348, "Б: тягне вниз", 10.5, GREEN, "middle", "bold")
    s += text(430, 214, "Б тягне → лінія = 0 (Б переміг)", 11.5, GREEN, "middle", "bold")
    # таблиця істинності
    s += rect(640, 120, 230, 130, "#fbfbfb", GREY, 1.4, 10)
    s += text(755, 144, "монтажне «І»", 12.5, INK, "middle", "bold")
    rows = [("усі відпустили", "1 (високо)", GREEN), ("хтось тягне", "0 (низько)", BLUE)]
    yy = 172
    for cond, res, col in rows:
        s += text(656, yy, cond, 11, INK, "start")
        s += text(864, yy, res, 11, col, "end", "bold")
        yy += 26
    s += text(755, 232, "0 завжди «сильніший» за 1", 10, GREY, "middle", style="italic")

    s += rect(60, 372, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 397, "Конфлікту нема в принципі: «тягнути вниз» завжди перемагає, «відпустити» нікому не заважає.",
              12, INK, "middle", "bold")
    save("fig-36-2-3-wiredand.svg", s)


# ── Рис. 36.2.4 — багато пристроїв на лінії ──────────────────────────────────
def fig24_manydev():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Багато пристроїв: лінія низька, якщо тягне хоч один", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усі ведені й ведучий ділять одну лінію — і ніколи не конфліктують",
              12.5, GREY, "middle", style="italic")
    # дві ситуації
    def panel(x0, title, states, result, rcol):
        out = rect(x0, 88, 380, 250, "none", FAINT, 2, 12)
        out += text(x0 + 190, 114, title, 13, INK, "middle", "bold")
        # підтяжка
        out += text(x0 + 40, 142, "+V", 10.5, RED, "middle", "bold")
        out += rect(x0 + 33, 150, 12, 22, "#fff", INK, 1.4, 3)
        out += line(x0 + 39, 172, x0 + 39, 200, INK, 2)
        out += line(x0 + 39, 200, x0 + 340, 200, INK, 3)
        for i, st in enumerate(states):
            dx = x0 + 110 + i * 80
            on = st
            out += line(dx, 200, dx, 230, INK, 2)
            out += rect(dx - 22, 230, 44, 40, ("#eef6ef" if on else "#fbfbfb"), (GREEN if on else GREY), 1.6, 5)
            out += text(dx, 248, "тягне" if on else "Z", 9.5, (GREEN if on else GREY), "middle", "bold")
            out += text(dx, 262, "0" if on else "—", 9.5, INK, "middle")
        out += text(x0 + 190, 300, "лінія = " + result, 13.5, rcol, "middle", "bold")
        return out
    s += panel(60, "хтось один тягне", [False, True, False], "0 (низько)", BLUE)
    s += panel(470, "усі відпустили", [False, False, False], "1 (високо)", GREEN)

    s += rect(60, 354, W - 120, 36, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 377, "Скільки б пристроїв не висіло на лінії, правило те саме: один «0» робить усю лінію «0».",
              12, INK, "middle", "bold")
    save("fig-36-2-4-manydev.svg", s)


# ── Рис. 36.2.5 — швидкий спад, повільний RC-підйом ──────────────────────────
def fig25_risefall():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Підпис I2C на осцилографі: різкий спад, заокруглений підйом", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "вниз тягне активно (швидко), а вгору — лише підтяжка через ємність шини (повільно, по RC)",
              12.5, GREY, "middle", style="italic")
    x0 = 150
    y_hi, y_lo = 130, 250
    # активний спад (різкий), RC-підйом
    s += line(x0, y_hi, x0 + 120, y_hi, INK, 2.8)
    s += line(x0 + 120, y_hi, x0 + 122, y_lo, INK, 2.8)  # різкий спад
    s += line(x0 + 122, y_lo, x0 + 280, y_lo, INK, 2.8)
    # RC-підйом (експонента)
    pts = []
    for i in range(0, 61):
        t = i / 60
        xx = x0 + 280 + t * 260
        yy = y_lo - (y_lo - y_hi) * (1 - math.exp(-3 * t))
        pts.append((xx, yy))
    path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    s += f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2.8"/>\n'
    s += line(x0 + 540, y_hi, x0 + 600, y_hi, INK, 2.8)
    # підписи
    s += text(x0 + 122, y_lo + 28, "активний спад (швидко)", 11, BLUE, "middle", "bold")
    s += text(x0 + 410, y_lo + 28, "RC-підйом через Rp·Cшини (повільно)", 11, RED, "middle", "bold")
    s += text(x0 + 410, y_hi - 10, "τ = Rp × Cшини", 12, INK, "middle", "bold")
    s += line(x0, y_hi - 24, x0 + 600, y_hi - 24, GREY, 1, dash="3,3")
    s += text(x0 - 8, y_hi - 20, "VCC", 10.5, GREY, "end")
    s += text(x0 - 8, y_lo + 4, "0", 10.5, GREY, "end")

    s += rect(60, 330, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 354, "Підйом — пасивний, тому повільний: він і обмежує максимальну швидкість шини.",
              12, INK, "middle", "bold")
    s += text(W / 2, 374, "Велика Cшини або велика Rp → довгий підйом → доводиться знижувати частоту SCL.",
              11.5, GREY, "middle", style="italic")
    save("fig-36-2-5-risefall.svg", s)


# ── Рис. 36.2.6 — як добирати підтяжку ───────────────────────────────────────
def fig26_pullup_sizing():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Як добирати підтяжку Rp: компроміс підйому й струму", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "велика Rp — повільний підйом, малий струм; мала Rp — швидкий підйом, але великий струм стоку",
              12.5, GREY, "middle", style="italic")
    # дві криві підйому
    ox, oy, axw, axh = 110, 250, 320, 150
    s += line(ox, oy, ox + axw, oy, INK, 1.6)
    s += line(ox, oy, ox, oy - axh, INK, 1.6)
    s += text(ox + axw, oy + 18, "час", 11, GREY, "start")
    s += text(ox - 6, oy - axh - 4, "V", 11, GREY, "end")
    for tau, col, lab in [(0.5, RED, "велика Rp: повільно"), (0.18, GREEN, "мала Rp: швидко")]:
        pts = []
        for i in range(0, 61):
            t = i / 60
            xx = ox + t * axw
            yy = oy - axh * (1 - math.exp(-t / tau))
            pts.append((xx, yy))
        path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        s += f'<path d="{path}" fill="none" stroke="{col}" stroke-width="2.4"/>\n'
        s += text(ox + axw + 4, pts[-1][1] + 4, lab, 10, col, "start", "bold")

    # таблиця типових
    bx, by = 540, 110
    s += rect(bx, by, 320, 150, "#fbfbfb", GREY, 1.4, 10)
    s += text(bx + 160, by + 26, "типові значення Rp", 12.5, INK, "middle", "bold")
    rows = [("100 кГц", "4.7 кОм"), ("400 кГц", "2.2 кОм"), ("1 МГц", "1 кОм (менше)")]
    yy = by + 54
    for f, r in rows:
        s += text(bx + 24, yy, f, 12, INK, "start", "bold")
        s += text(bx + 200, yy, r, 12, GREEN, "start", "bold")
        yy += 30

    # струм
    s += rect(110, 300, 750, 50, LGREY, GREY, 1.3, 8)
    s += text(130, 322, "струм стоку, коли лінію притягнуто: I = VCC / Rp", 12, INK, "start", "bold")
    s += text(130, 340, "3.3 В / 4.7 кОм ≈ 0.7 мА (норма)   ·   3.3 В / 1 кОм ≈ 3.3 мА (близько межі стоку ≈3 мА)",
              11, GREY, "start")

    s += rect(60, 364, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 390, "Rp добирають під ємність шини й швидкість: швидше → менша Rp, але не менше, ніж витримує стік.",
              11.5, INK, "middle", "bold")
    save("fig-36-2-6-pullup-sizing.svg", s)


# ── Рис. 36.2.7 — що дає відкритий колектор у I2C ────────────────────────────
def fig27_enables():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо все це: відкритий колектор — основа трюків I2C", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "усі ключові механізми шини працюють, бо «притягнути вниз» завжди перемагає",
              12.5, GREY, "middle", style="italic")
    panels = [
        ("ACK / NACK", "ведений тягне SDA вниз —", "«я почув» (§36.4)", BLUE),
        ("розтягування такту", "ведений тримає SCL внизу —", "«зачекай» (§36.6)", "#b08900"),
        ("арбітраж", "хто тягне 0, той виграє лінію —", "кілька ведучих (§36.6)", GREEN),
    ]
    x = 60
    for title, line1, line2, col in panels:
        s += rect(x, 96, 270, 150, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 126, title, 13.5, col, "middle", "bold")
        s += text(x + 135, 162, line1, 11, INK, "middle")
        s += text(x + 135, 184, line2, 11, INK, "middle", "bold")
        s += text(x + 135, 218, "→ «тягни вниз» вирішує", 10.5, GREY, "middle", style="italic")
        x += 290

    s += rect(60, 268, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 292, "Одне просте рішення — виходи лише «вниз» зі спільною підтяжкою — дає підтвердження, паузу й арбітраж.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Тому відкритий колектор — не дрібниця, а серце того, як I2C дає багатьом мирно ділити дві лінії.",
              11, GREY, "middle", style="italic")
    save("fig-36-2-7-enables.svg", s)


# ============================================================================
#  §36.3 — Адресація: багато пристроїв на двох дротах (7-біт адреси)
# ============================================================================
def _byterow(x, y, cells, cw=58, h=48):
    """cells: список (label, value, color, fill). Повертає svg."""
    s = ""
    for i, (lab, val, col, fill) in enumerate(cells):
        s += rect(x + i * cw, y, cw, h, fill, col, 1.8, 4)
        s += text(x + i * cw + cw / 2, y - 8, lab, 10.5, col, "middle", "bold")
        s += text(x + i * cw + cw / 2, y + h / 2 + 6, val, 14, INK, "middle", "bold")
    return s


# ── Рис. 36.3.1 — перший байт: 7 біт адреси + біт R/W ────────────────────────
def fig31_addrbyte():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Перший байт після СТАРТу: 7 біт адреси + біт напрямку", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ведучий «гукає» адресу веденого; восьмий біт каже, читати чи писати",
              12.5, GREY, "middle", style="italic")
    x0, cw = 130, 78
    cells = [("A6", "1", BLUE, LBLUE), ("A5", "1", BLUE, LBLUE), ("A4", "0", BLUE, LBLUE),
             ("A3", "1", BLUE, LBLUE), ("A2", "0", BLUE, LBLUE), ("A1", "0", BLUE, LBLUE),
             ("A0", "0", BLUE, LBLUE), ("R/W", "0", GREEN, LGRN)]
    s += _byterow(x0, 150, cells, cw, 56)
    # дужки
    s += arrow(x0 + 3.5 * cw, 230, x0, 230, BLUE, 1.6)
    s += arrow(x0 + 3.5 * cw, 230, x0 + 7 * cw, 230, BLUE, 1.6)
    s += text(x0 + 3.5 * cw, 250, "7 біт адреси = 0x68", 13, BLUE, "middle", "bold")
    s += arrow(x0 + 7.5 * cw, 230, x0 + 7 * cw, 230, GREEN, 1.6)
    s += arrow(x0 + 7.5 * cw, 230, x0 + 8 * cw, 230, GREEN, 1.6)
    s += text(x0 + 7.5 * cw, 250, "R/W", 12, GREEN, "middle", "bold")
    s += text(x0 + 4 * cw, 290, "0 = ведучий ПИШЕ   ·   1 = ведучий ЧИТАЄ", 12.5, INK, "middle", "bold")

    s += rect(60, 320, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 346, "7 біт → 2⁷ = 128 можливих адрес (кілька зарезервовано → ≈112 придатних).",
              12, INK, "middle", "bold")
    save("fig-36-3-1-addrbyte.svg", s)


# ── Рис. 36.3.2 — відгукується лише той, чия адреса збіглася ─────────────────
def fig32_select():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Адресу «чують» усі — відгукується лише потрібний", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ведучий шле 0x68; кожен ведений звіряє зі своєю адресою, відповідає тільки збіг",
              12.5, GREY, "middle", style="italic")
    sda_y = 150
    s += line(120, sda_y, 820, sda_y, RED, 3)
    s += text(150, sda_y - 10, "ведучий шле: 0x68 →", 12, INK, "start", "bold")
    devs = [("0x3C", 250, False), ("0x68", 430, True), ("0x76", 610, False), ("0x50", 760, False)]
    for addr, cx, match in devs:
        col = GREEN if match else GREY
        fill = LGRN if match else "#f4f4f4"
        s += line(cx, sda_y, cx, 230, INK, 2)
        s += rect(cx - 55, 230, 110, 70, fill, col, 2, 8)
        s += text(cx, 258, "адреса " + addr, 11.5, INK, "middle", "bold")
        if match:
            s += text(cx, 280, "✓ це я → ACK", 11.5, GREEN, "middle", "bold")
        else:
            s += text(cx, 280, "не я → мовчу", 10.5, GREY, "middle")

    s += rect(60, 332, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 358, "Адреса — це фільтр: на спільній лінії кожен слухає, та реагує лише власник адреси.",
              12, INK, "middle", "bold")
    save("fig-36-3-2-select.svg", s)


# ── Рис. 36.3.3 — біт R/W: той самий чіп, два напрямки ───────────────────────
def fig33_rw():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Біт R/W: одна адреса, два напрямки обміну", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "той самий ведений 0x68 — але ведучий може або писати в нього, або читати з нього",
              12.5, GREY, "middle", style="italic")
    # write
    s += rect(70, 100, 340, 110, LGRN, GREEN, 2, 12)
    s += text(240, 126, "R/W = 0 : ЗАПИС", 13.5, GREEN, "middle", "bold")
    s += rect(110, 140, 90, 50, "#fbfbfb", INK, 2, 8); s += text(155, 170, "ведучий", 11, INK, "middle", "bold")
    s += rect(280, 140, 90, 50, "#fbfbfb", INK, 2, 8); s += text(325, 170, "0x68", 11, INK, "middle", "bold")
    s += arrow(200, 165, 280, 165, BLUE, 2.4)
    s += text(240, 158, "дані →", 10, BLUE, "middle", "bold")
    # read
    s += rect(470, 100, 340, 110, LBLUE, BLUE, 2, 12)
    s += text(640, 126, "R/W = 1 : ЧИТАННЯ", 13.5, BLUE, "middle", "bold")
    s += rect(510, 140, 90, 50, "#fbfbfb", INK, 2, 8); s += text(555, 170, "ведучий", 11, INK, "middle", "bold")
    s += rect(680, 140, 90, 50, "#fbfbfb", INK, 2, 8); s += text(725, 170, "0x68", 11, INK, "middle", "bold")
    s += arrow(680, 175, 600, 175, RED, 2.4)
    s += text(640, 195, "← дані", 10, RED, "middle", "bold")

    s += rect(60, 250, W - 120, 100, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 276, "Адреса вибирає, З КИМ говорити; біт R/W — у який БІК ідуть дані наступними байтами.", 12, INK, "middle", "bold")
    s += text(W / 2, 300, "0x68 із R/W=0 → байт 0xD0 на лінії;  0x68 із R/W=1 → байт 0xD1.", 12, INK, "middle", "bold")
    s += text(W / 2, 324, "(саме звідси й виникає плутанина 7-біт проти 8-біт — див. далі)", 11, GREY, "middle", style="italic")
    save("fig-36-3-3-rw.svg", s)


# ── Рис. 36.3.4 — плутанина 7-біт проти 8-біт ────────────────────────────────
def fig34_7vs8():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Класична пастка: 0x68 чи 0xD0? — 7-біт проти 8-біт", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "та сама адреса в двох записах: «чиста» 7-бітна і «зсунута» 8-бітна з бітом R/W",
              12.5, GREY, "middle", style="italic")
    x0, cw = 200, 56
    # 7-бітна
    s += text(x0 - 16, 130, "7-біт адреса", 12, BLUE, "end", "bold")
    cells7 = [("", "1", BLUE, LBLUE), ("", "1", BLUE, LBLUE), ("", "0", BLUE, LBLUE),
              ("", "1", BLUE, LBLUE), ("", "0", BLUE, LBLUE), ("", "0", BLUE, LBLUE), ("", "0", BLUE, LBLUE)]
    s += _byterow(x0, 110, cells7, cw, 40)
    s += text(x0 + 7 * cw + 16, 134, "= 0x68", 14, BLUE, "start", "bold")
    # зсув
    s += arrow(x0 + 3.5 * cw, 162, x0 + 3.5 * cw + cw, 162, INK, 2)
    s += text(x0 + 4.2 * cw, 156, "зсув ліворуч на 1 + біт R/W", 11, GREY, "start", "bold")
    # 8-бітні
    s += text(x0 - 16, 240, "8-біт (запис)", 12, GREEN, "end", "bold")
    cells8w = [("", "1", BLUE, LBLUE), ("", "1", BLUE, LBLUE), ("", "0", BLUE, LBLUE),
               ("", "1", BLUE, LBLUE), ("", "0", BLUE, LBLUE), ("", "0", BLUE, LBLUE),
               ("", "0", BLUE, LBLUE), ("R/W", "0", GREEN, LGRN)]
    s += _byterow(x0, 220, cells8w, cw, 40)
    s += text(x0 + 8 * cw + 16, 244, "= 0xD0", 14, GREEN, "start", "bold")
    s += text(x0 - 16, 320, "8-біт (читання)", 12, GREEN, "end", "bold")
    cells8r = list(cells8w[:-1]) + [("R/W", "1", GREEN, LGRN)]
    s += _byterow(x0, 300, cells8r, cw, 40)
    s += text(x0 + 8 * cw + 16, 324, "= 0xD1", 14, GREEN, "start", "bold")

    s += rect(60, 370, W - 120, 42, LRED, RED, 1.4, 10)
    s += text(W / 2, 396, "Бібліотека часто хоче 7-бітну (0x68) і сама додає R/W; даташит інколи дає 8-бітну (0xD0). Це ОДНА адреса!",
              11.5, INK, "middle", "bold")
    save("fig-36-3-4-7vs8.svg", s)


# ── Рис. 36.3.5 — фіксована база + ніжки адреси ──────────────────────────────
def fig35_addrpins():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Кілька однакових чіпів на шині: ніжки адреси", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "частину адреси зашив виробник, кілька молодших біт задають ніжками A0/A1/A2",
              12.5, GREY, "middle", style="italic")
    # два однакові чіпи
    def chipA(x, a0, addr):
        out = rect(x, 120, 150, 120, "#fbfbfb", INK, 2, 10)
        out += text(x + 75, 146, "той самий", 11, GREY, "middle")
        out += text(x + 75, 164, "тип чіпа", 11, GREY, "middle")
        out += text(x + 75, 192, "адреса " + addr, 13, GREEN, "middle", "bold")
        # ніжка A0
        out += text(x + 30, 224, "A0 =", 11, INK, "start", "bold")
        out += text(x + 80, 224, ("VCC (1)" if a0 else "GND (0)"), 11, (RED if a0 else BLUE), "start", "bold")
        return out
    s += chipA(140, 0, "0x68")
    s += chipA(560, 1, "0x69")
    s += text(440, 150, "база 0x68", 12, INK, "middle", "bold")
    s += text(440, 172, "+ A0 = 0x68 / 0x69", 11.5, GREY, "middle")
    s += arrow(295, 180, 555, 180, GREY, 1.6, dash="4,3")

    s += rect(60, 270, W - 120, 100, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 296, "Так два-чотири однакові давачі живуть на одній шині: кожному дають свою адресу ніжками.",
              12, INK, "middle", "bold")
    s += text(W / 2, 320, "Бракує ніжок — ставлять I2C-мультиплексор (напр. TCA9548), що розводить шину на кілька гілок.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 344, "Дві однакові адреси на одній шині без цього — конфлікт: обидва відгукнуться разом.",
              11, RED, "middle", "bold")
    save("fig-36-3-5-addrpins.svg", s)


# ── Рис. 36.3.6 — карта адрес і зарезервовані ────────────────────────────────
def fig36_addrmap():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Карта 7-бітних адрес: 0x00…0x7F", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кілька діапазонів зарезервовано, лишається ≈112 придатних адрес",
              12.5, GREY, "middle", style="italic")
    ox, oy, cell = 120, 100, 44
    known = {0x3C: "дисплей", 0x50: "EEPROM", 0x68: "гіро", 0x76: "баро"}
    for r in range(8):
        for c in range(16):
            a = r * 16 + c
            reserved = (a <= 0x07) or (a >= 0x78)
            fill = "#f0d8d8" if reserved else ("#dfe7fb" if a in known else "#ffffff")
            col = RED if reserved else (BLUE if a in known else GREY)
            s += rect(ox + c * cell, oy + r * cell, cell, cell, fill, col, 1)
            s += text(ox + c * cell + cell / 2, oy + r * cell + cell / 2 + 4,
                      "%02X" % a, 9, (RED if reserved else INK), "middle",
                      "bold" if a in known else "normal")
    # легенда
    ly = oy + 8 * cell + 24
    s += rect(ox, ly, 16, 16, "#f0d8d8", RED, 1); s += text(ox + 24, ly + 13, "зарезервовано (0x00–0x07, 0x78–0x7F)", 11, INK, "start")
    s += rect(ox + 360, ly, 16, 16, "#dfe7fb", BLUE, 1); s += text(ox + 384, ly + 13, "приклади реальних давачів", 11, INK, "start")

    s += rect(60, ly + 36, W - 120, 30, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, ly + 56, "128 клітин − 16 зарезервованих = 112 придатних адрес на одну шину.",
              12, INK, "middle", "bold")
    save("fig-36-3-6-addrmap.svg", s)


# ── Рис. 36.3.7 — I2C-сканер ─────────────────────────────────────────────────
def fig37_scanner():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "I2C-сканер: «гукнути» кожну адресу й глянути, хто відгукнеться", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "найперший інструмент налагодження: перебрати 0x08…0x77 і записати, хто дав ACK",
              12.5, GREY, "middle", style="italic")
    # «термінал»
    s += rect(120, 90, 360, 230, "#1e2330", "#111", 2, 10)
    s += text(140, 120, "Scanning I2C bus...", 12.5, "#7fd0ff", "start", "bold")
    found = [("0x3C", "дисплей"), ("0x68", "гіроскоп"), ("0x76", "барометр")]
    yy = 150
    for addr, what in found:
        s += text(140, yy, "found device at " + addr, 12, "#9be39b", "start")
        yy += 26
    s += text(140, yy + 6, "3 devices found.", 12, "#e8e8e8", "start", "bold")
    s += text(140, yy + 30, "_", 13, "#7fd0ff", "start", "bold")

    # пояснення
    s += rect(520, 90, 300, 230, "#fbfbfb", GREY, 1.4, 10)
    s += text(670, 118, "як це працює", 12.5, INK, "middle", "bold")
    s += text(540, 146, "1. для кожної адреси —", 11, INK, "start")
    s += text(556, 164, "СТАРТ + адреса + W", 11, GREY, "start")
    s += text(540, 190, "2. є ACK → пристрій є", 11, GREEN, "start", "bold")
    s += text(540, 214, "3. NACK → нікого нема", 11, RED, "start", "bold")
    s += text(540, 244, "4. СТОП, наступна адреса", 11, INK, "start")
    s += text(540, 280, "(нічого не пишемо в чіп —", 10, GREY, "start", style="italic")
    s += text(540, 296, " лише перевіряємо відгук)", 10, GREY, "start", style="italic")

    s += rect(60, 336, W - 120, 36, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 359, "Не знаєш адресу давача чи лінія «мовчить»? Запусти сканер — це перший крок налагодження I2C.",
              12, INK, "middle", "bold")
    save("fig-36-3-7-scanner.svg", s)


# ============================================================================
#  §36.4 — Старт, стоп, ACK/NACK
# ============================================================================
def _strip(x, y, items, h=46):
    """Послідовність полів транзакції. items: (label, width, color, fill). Повертає (svg, x_end)."""
    s = ""
    cx = x
    for lab, wdt, col, fill in items:
        s += rect(cx, y, wdt, h, fill, col, 1.8, 5)
        s += text(cx + wdt / 2, y + h / 2 + 5, lab, 11.5, col, "middle", "bold")
        cx += wdt + 4
    return s, cx


# ── Рис. 36.4.1 — умови СТАРТ і СТОП ─────────────────────────────────────────
def fig41_startstop():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "СТАРТ і СТОП: зміна SDA саме тоді, коли SCL високий", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "СТАРТ = SDA падає при високому SCL; СТОП = SDA піднімається при високому SCL",
              12.5, GREY, "middle", style="italic")
    x0, unit = 130, 80
    # SCL
    s += text(x0 - 16, 135, "SCL", 12.5, BLUE, "end", "bold")
    scl = [(1, 1.0)] + [(0, 0.5), (1, 0.5)] * 3 + [(1, 1.0)]
    s += _wave(x0, 116, 154, unit, scl, BLUE, 2.6)[0]
    # SDA: високо, падіння (START), біти, підйом (STOP)
    s += text(x0 - 16, 225, "SDA", 12.5, RED, "end", "bold")
    sda = [(1, 0.7), (0, 0.3)] + [(1, 0.5), (1, 0.5), (0, 0.5), (0, 0.5), (1, 0.5), (0, 0.5)] + [(0, 0.4), (1, 0.6)]
    s += _wave(x0, 206, 244, unit, sda, RED, 2.6)[0]
    # позначки START/STOP
    sx_start = x0 + 0.7 * unit
    s += line(sx_start, 110, sx_start, 250, GREEN, 1.4, dash="4,3")
    s += text(sx_start, 100, "СТАРТ (S)", 12, GREEN, "middle", "bold")
    s += text(sx_start, 274, "SDA↓ при SCL=1", 10, GREEN, "middle")
    sx_stop = x0 + 3.6 * unit
    s += line(sx_stop, 110, sx_stop, 250, RED, 1.4, dash="4,3")
    s += text(sx_stop, 100, "СТОП (P)", 12, RED, "middle", "bold")
    s += text(sx_stop, 274, "SDA↑ при SCL=1", 10, RED, "middle")
    s += text(x0 - 30, 300, "у спокої обидві лінії високі", 11, GREY, "start", style="italic")

    s += rect(60, 320, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 344, "СТАРТ «захоплює» шину й починає обмін; СТОП завершує його й відпускає лінію.",
              12, INK, "middle", "bold")
    s += text(W / 2, 364, "Між ними дані міняються лише поки SCL низький (правило §36.1).",
              11.5, GREY, "middle", style="italic")
    save("fig-36-4-1-startstop.svg", s)


# ── Рис. 36.4.2 — чому їх не сплутати з даними ───────────────────────────────
def fig42_unmistakable():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому СТАРТ/СТОП не сплутати з даними", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "звичайний біт міняє SDA при НИЗЬКОМУ такті; СТАРТ/СТОП — навмисне при ВИСОКОМУ",
              12.5, GREY, "middle", style="italic")
    # ліворуч: звичайний біт
    s += rect(60, 90, 380, 230, "none", FAINT, 2, 12)
    s += text(250, 116, "звичайний біт даних", 13, INK, "middle", "bold")
    x0, unit = 110, 130
    s += text(x0 - 18, 165, "SCL", 11, BLUE, "end", "bold")
    s += _wave(x0, 150, 184, unit, [(0, 0.5), (1, 0.5), (0, 0.5), (1, 0.5)], BLUE, 2.4)[0]
    s += text(x0 - 18, 235, "SDA", 11, RED, "end", "bold")
    s += _wave(x0, 220, 254, unit, [(1, 1.0), (0, 1.0)], RED, 2.4)[0]
    s += line(x0 + 1.0 * unit, 144, x0 + 1.0 * unit, 260, GREY, 1.2, dash="3,3")
    s += text(250, 290, "SDA міняється, поки SCL низький → ОК", 11, GREY, "middle", "bold")
    # праворуч: START
    s += rect(460, 90, 380, 230, "none", FAINT, 2, 12)
    s += text(650, 116, "СТАРТ / СТОП", 13, GREEN, "middle", "bold")
    x1 = 510
    s += text(x1 - 18, 165, "SCL", 11, BLUE, "end", "bold")
    s += _wave(x1, 150, 184, unit, [(1, 2.0)], BLUE, 2.4)[0]
    s += text(x1 - 18, 235, "SDA", 11, RED, "end", "bold")
    s += _wave(x1, 220, 254, unit, [(1, 1.0), (0, 1.0)], RED, 2.4)[0]
    s += line(x1 + 1.0 * unit, 144, x1 + 1.0 * unit, 260, GREEN, 1.2, dash="3,3")
    s += text(650, 290, "SDA міняється, поки SCL ВИСОКИЙ → спецсигнал", 11, GREEN, "middle", "bold")

    s += rect(60, 336, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 361, "Порушення правила «дані лише при низькому такті» зроблено навмисно — щоб ці знаки були унікальні.",
              11.5, INK, "middle", "bold")
    save("fig-36-4-2-unmistakable.svg", s)


# ── Рис. 36.4.3 — дев'ятий біт: ACK / NACK ───────────────────────────────────
def fig43_ack():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "Дев'ятий такт: підтвердження ACK / NACK", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "після 8 біт даних — ще один такт; приймач тягне SDA вниз = ACK, лишає високим = NACK",
              12.5, GREY, "middle", style="italic")
    x0, unit = 120, 74
    s += text(x0 - 16, 135, "SCL", 12, BLUE, "end", "bold")
    s += _wave(x0, 116, 152, unit, [(0, 0.5), (1, 0.5)] * 9, BLUE, 2.2)[0]
    # позначки тактів
    for k in range(9):
        cxk = x0 + (k + 0.5) * unit
        lab = "ACK" if k == 8 else str(8 - k)
        s += text(cxk, 108, lab, 9.5, (GREEN if k == 8 else GREY), "middle", "bold")
    s += text(x0 - 16, 215, "SDA", 12, RED, "end", "bold")
    # 8 біт від передавача + 9-й від приймача (ACK=0)
    sda = [(1, 1.0), (0, 1.0), (1, 1.0), (1, 1.0), (0, 1.0), (1, 1.0), (0, 1.0), (0, 1.0), (0, 1.0)]
    s += _wave(x0, 196, 232, unit, sda, RED, 2.2)[0]
    s += rect(x0 + 8 * unit, 190, unit, 48, "#eef6ef", GREEN, 1.4)
    s += text(x0 + 8.5 * unit, 254, "приймач тягне 0 = ACK", 10.5, GREEN, "middle", "bold")
    s += text(x0 + 4 * unit, 254, "8 біт від передавача", 10.5, GREY, "middle")
    s += arrow(x0 + 8.5 * unit, 280, x0 + 8.5 * unit, 234, GREEN, 1.6)

    s += rect(60, 320, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 344, "Кожен байт на I2C — це насправді 9 тактів: 8 даних + 1 підтвердження.",
              12, INK, "middle", "bold")
    s += text(W / 2, 364, "ACK (0) — «прийняв, давай далі»; NACK (1, лінія сама піднялась) — «ні / досить».",
              11.5, GREY, "middle", style="italic")
    save("fig-36-4-3-ack.svg", s)


# ── Рис. 36.4.4 — хто підтверджує: запис проти читання ───────────────────────
def fig44_whoack():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Хто підтверджує: при записі — ведений, при читанні — ведучий", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ACK завжди дає ПРИЙМАЧ байта; при читанні ведучий NACK-ом каже «це останній»",
              12.5, GREY, "middle", style="italic")
    # запис
    s += rect(60, 90, 380, 250, "none", FAINT, 2, 12)
    s += text(250, 116, "ЗАПИС (ведучий пише)", 12.5, GREEN, "middle", "bold")
    items_w = [("дані", 90, INK, "#eef4ff"), ("A", 44, GREEN, LGRN), ("дані", 90, INK, "#eef4ff"), ("A", 44, GREEN, LGRN)]
    sw, _ = _strip(90, 150, items_w, 44)
    s += sw
    s += text(250, 230, "ведений ACK-ає кожен прийнятий байт", 11, INK, "middle", "bold")
    s += text(250, 252, "(приймач = ведений)", 10.5, GREY, "middle")
    # читання
    s += rect(460, 90, 380, 250, "none", FAINT, 2, 12)
    s += text(650, 116, "ЧИТАННЯ (ведучий читає)", 12.5, BLUE, "middle", "bold")
    items_r = [("дані", 90, INK, "#eef4ff"), ("A", 44, GREEN, LGRN), ("дані", 90, INK, "#eef4ff"), ("N", 44, RED, LRED)]
    sr, _ = _strip(490, 150, items_r, 44)
    s += sr
    s += text(650, 230, "ведучий ACK-ає, щоб просити ще,", 11, INK, "middle", "bold")
    s += text(650, 250, "а NACK-ом каже «досить» перед СТОП", 11, RED, "middle", "bold")
    s += text(650, 272, "(приймач = ведучий)", 10.5, GREY, "middle")

    s += rect(60, 356, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 381, "Правило просте: підтверджує той, хто щойно ПРИЙНЯВ байт. Напрямок задав біт R/W.",
              12, INK, "middle", "bold")
    save("fig-36-4-4-whoack.svg", s)


# ── Рис. 36.4.5 — повна проста транзакція ────────────────────────────────────
def fig45_transaction():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Повна проста транзакція запису: усі «розділові знаки»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "СТАРТ · адреса+W · ACK · байт даних · ACK · СТОП",
              12.5, GREY, "middle", style="italic")
    items = [
        ("S", 50, GREEN, LGRN),
        ("адреса + W", 150, BLUE, LBLUE),
        ("A", 44, GREEN, LGRN),
        ("байт даних", 150, INK, "#eef4ff"),
        ("A", 44, GREEN, LGRN),
        ("P", 50, RED, LRED),
    ]
    sv, _ = _strip(110, 150, items, 56)
    s += sv
    # підписи знизу
    labels = [(135, "старт", GREEN), (260, "кого + напрям", BLUE), (358, "ведений: «ок»", GREEN),
              (470, "що пишемо", INK), (586, "ведений: «ок»", GREEN), (660, "стоп", RED)]
    for x, t, c in labels:
        s += text(x, 230, t, 10.5, c, "middle", "bold")
    s += arrow(110, 130, 720, 130, GREY, 1.5)
    s += text(720, 122, "час →", 11, GREY, "start")

    s += rect(60, 270, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 294, "Кожен обмін I2C загорнутий між СТАРТ і СТОП, а кожен байт ведений квитує знаком A.",
              12, INK, "middle", "bold")
    s += text(W / 2, 314, "Читання має ту саму форму, лише з R замість W і даними у зворотний бік.",
              11.5, GREY, "middle", style="italic")
    save("fig-36-4-5-transaction.svg", s)


# ── Рис. 36.4.6 — повторний старт ────────────────────────────────────────────
def fig46_repeated_start():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 34, "Повторний СТАРТ (Sr): змінити напрям, не відпускаючи шину", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "написати адресу регістра, тоді Sr і читати — без СТОПу між ними, щоб ніхто не вклинився",
              12.5, GREY, "middle", style="italic")
    items = [
        ("S", 44, GREEN, LGRN),
        ("адр+W", 80, BLUE, LBLUE),
        ("A", 32, GREEN, LGRN),
        ("№ рег.", 80, INK, "#eef4ff"),
        ("A", 32, GREEN, LGRN),
        ("Sr", 50, "#b08900", "#fbf3df"),
        ("адр+R", 80, BLUE, LBLUE),
        ("A", 32, GREEN, LGRN),
        ("дані", 80, INK, "#eef4ff"),
        ("N", 32, RED, LRED),
        ("P", 44, RED, LRED),
    ]
    sv, xend = _strip(80, 150, items, 56)
    s += sv
    s += text(80 + 5 * 90, 130, "Sr замість P+S", 11, "#b08900", "middle", "bold")
    s += arrow(80, 232, xend, 232, GREY, 1.4)
    s += text(310, 252, "фаза запису (який регістр)", 10.5, GREY, "middle")
    s += text(640, 252, "фаза читання (дані звідти)", 10.5, GREY, "middle")

    s += rect(60, 280, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 304, "Повторний старт тримає шину «своєю» весь час — це робить «запис-потім-читання» неподільним.",
              12, INK, "middle", "bold")
    s += text(W / 2, 324, "Саме так звертаються до регістрів давачів (детально — §36.5).",
              11.5, GREY, "middle", style="italic")
    save("fig-36-4-6-repeated-start.svg", s)


# ── Рис. 36.4.7 — про що говорить NACK ───────────────────────────────────────
def fig47_nack_diag():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "NACK — корисний сигнал: про що він каже", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "відсутність ACK означає різне залежно від того, ДЕ вона сталася",
              12.5, GREY, "middle", style="italic")
    cases = [
        ("після АДРЕСИ", "на шині нема пристрою\nз такою адресою", RED, "→ перевір адресу/дроти"),
        ("після байта (запис)", "ведений не може прийняти\n(зайнятий / помилка)", "#b08900", "→ сповільни / перевір стан"),
        ("від ведучого (читання)", "«це був останній байт,\nдалі не треба»", GREEN, "→ нормальне завершення"),
    ]
    x = 60
    for title, mean, col, act in cases:
        s += rect(x, 96, 270, 180, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 124, title, 12.5, col, "middle", "bold")
        for j, ln in enumerate(mean.split("\n")):
            s += text(x + 135, 158 + j * 18, ln, 11, INK, "middle")
        s += text(x + 135, 230, act, 10.5, GREY, "middle", style="italic")
        x += 290

    s += rect(60, 296, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 320, "Тому реакція на ACK/NACK — основа надійного драйвера: за ними видно і відсутність чіпа, і його стан.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 340, "Бібліотеки повертають цей результат (напр. код помилки Wire.endTransmission()).",
              11, GREY, "middle", style="italic")
    save("fig-36-4-7-nack-diag.svg", s)


# ============================================================================
#  §36.5 — Транзакція в часі: запис і читання (доступ до регістрів)
# ============================================================================

# ── Рис. 36.5.1 — чіп як набір регістрів ─────────────────────────────────────
def fig51_registers():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Чіп зсередини — це набір пронумерованих регістрів", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "звертання до давача = запис/читання його регістрів за номером (як пам'ять з адресами, §20.3)",
              12.5, GREY, "middle", style="italic")
    # чіп
    s += rect(300, 90, 300, 290, "#23262b", "#111", 2, 10)
    s += text(450, 116, "давач  (адреса 0x68)", 13, "#e8e8e8", "middle", "bold")
    regs = [("0x00", "WHO_AM_I", "хто я (для перевірки)"),
            ("0x6B", "PWR_MGMT", "увімкнути / режим сну"),
            ("0x1B", "CONFIG", "діапазон, фільтр"),
            ("0x3B", "DATA_X_H", "вимір, старший байт"),
            ("0x3C", "DATA_X_L", "вимір, молодший байт"),
            ("0x75", "STATUS", "стан / готовність")]
    yy = 142
    for num, name, desc in regs:
        s += rect(316, yy, 268, 36, "#2c3038", "#3a3f48", 1, 4)
        s += text(326, yy + 23, num, 11.5, "#ffd479", "start", "bold")
        s += text(386, yy + 23, name, 11.5, "#9be39b", "start", "bold")
        s += text(580, yy + 16, desc, 8.6, "#b9b9b9", "end")
        yy += 40
    # стрілка доступу
    s += arrow(180, 235, 298, 235, BLUE, 2.4)
    s += text(180, 222, "ведучий: «дай 0x3B»", 11, BLUE, "start", "bold")

    s += rect(60, 388, W - 120, 1, "none", "none", 0)
    s += text(W / 2, 404, "Конфіг пишемо в одні регістри, виміри читаємо з інших — уся робота з I2C-чіпом саме така.",
              12, INK, "middle", "bold")
    save("fig-36-5-1-registers.svg", s)


# ── Рис. 36.5.2 — запис у регістр ────────────────────────────────────────────
def fig52_write():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Запис у регістр: куди (№) і що (дані)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "після адреси перший байт — НОМЕР регістра, далі — дані, що туди лягають",
              12.5, GREY, "middle", style="italic")
    items = [
        ("S", 46, GREEN, LGRN),
        ("0x68 + W", 130, BLUE, LBLUE),
        ("A", 38, GREEN, LGRN),
        ("№ рег. 0x6B", 140, "#b08900", "#fbf3df"),
        ("A", 38, GREEN, LGRN),
        ("дані 0x01", 130, INK, "#eef4ff"),
        ("A", 38, GREEN, LGRN),
        ("P", 46, RED, LRED),
    ]
    sv, _ = _strip(70, 150, items, 56)
    s += sv
    s += text(70 + 130, 230, "до кого", 10.5, BLUE, "middle", "bold")
    s += text(70 + 350, 230, "у який регістр", 10.5, "#b08900", "middle", "bold")
    s += text(70 + 590, 230, "що записати", 10.5, INK, "middle", "bold")

    s += rect(60, 262, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 286, "«Записати 0x01 у регістр 0x6B пристрою 0x68» — типове увімкнення давача (вихід зі сну).",
              12, INK, "middle", "bold")
    s += text(W / 2, 306, "Кілька байтів поспіль часто лягають у сусідні регістри (внутрішній лічильник +1).",
              11.5, GREY, "middle", style="italic")
    save("fig-36-5-2-write.svg", s)


# ── Рис. 36.5.3 — читання з регістра (дві фази) ──────────────────────────────
def fig53_read():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 34, "Читання з регістра: спершу скажи ЯКИЙ, тоді читай", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "фаза 1 — «вкажи покажчик» (короткий запис номера); фаза 2 — повторний старт і читання",
              12.5, GREY, "middle", style="italic")
    # фаза 1
    s += text(80, 120, "фаза 1: вказати регістр", 12, "#b08900", "start", "bold")
    items1 = [("S", 42, GREEN, LGRN), ("0x68+W", 100, BLUE, LBLUE), ("A", 32, GREEN, LGRN),
              ("№ рег. 0x3B", 130, "#b08900", "#fbf3df"), ("A", 32, GREEN, LGRN)]
    s1, x1 = _strip(80, 134, items1, 50)
    s += s1
    # фаза 2
    s += text(80, 234, "фаза 2: повторний старт і читання", 12, BLUE, "start", "bold")
    items2 = [("Sr", 50, "#b08900", "#fbf3df"), ("0x68+R", 100, BLUE, LBLUE), ("A", 32, GREEN, LGRN),
              ("дані", 110, INK, "#eef4ff"), ("N", 32, RED, LRED), ("P", 42, RED, LRED)]
    s2, x2 = _strip(80, 248, items2, 50)
    s += s2
    # зв'язок Sr
    s += arrow(x1 - 10, 184, 95, 248, "#b08900", 1.8, dash="4,3")
    s += text(300, 212, "без СТОПу між фазами → Sr (атомарно)", 11, "#b08900", "middle", "bold")

    s += rect(60, 318, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 342, "Чіп має «покажчик регістра»: фаза 1 встановлює його, фаза 2 читає з нього.",
              12, INK, "middle", "bold")
    s += text(W / 2, 362, "Повторний старт (§36.4) тримає шину, щоб між «вказав» і «читаю» ніхто не вклинився.",
              11.5, GREY, "middle", style="italic")
    save("fig-36-5-3-read.svg", s)


# ── Рис. 36.5.4 — пакетне читання з авто-інкрементом ─────────────────────────
def fig54_burst():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Пакетне читання: вказав регістр раз — читаєш поспіль", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "внутрішній покажчик сам зростає на 1 після кожного байта → одним махом беремо весь блок",
              12.5, GREY, "middle", style="italic")
    # покажчик і регістри
    regs = ["0x3B X_H", "0x3C X_L", "0x3D Y_H", "0x3E Y_L", "0x3F Z_H", "0x40 Z_L"]
    x0 = 110
    for i, r in enumerate(regs):
        s += rect(x0 + i * 120, 120, 110, 44, "#eef4ff", BLUE, 1.6, 5)
        s += text(x0 + i * 120 + 55, 147, r, 10.5, INK, "middle", "bold")
        s += arrow(x0 + i * 120 + 55, 196, x0 + i * 120 + 55, 168, GREEN, 1.6)
        s += text(x0 + i * 120 + 55, 214, "байт %d" % (i + 1), 9.5, GREEN, "middle", "bold")
    s += arrow(x0, 100, x0 + 5 * 120 + 110, 100, "#b08900", 2)
    s += text(x0 + 3 * 120, 90, "покажчик авто +1", 11, "#b08900", "middle", "bold")
    s += text(W / 2, 250, "один запит «читай 6 байтів від 0x3B» → усі три осі (X, Y, Z) за раз",
              12.5, INK, "middle", "bold")

    s += rect(60, 290, W - 120, 80, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 314, "Пакет економить час: замість шести окремих читань — одне з шістьма байтами.",
              12, INK, "middle", "bold")
    s += text(W / 2, 336, "І дані виходять узгодженими в часі — усі осі з одного моменту, а не «розмазані».",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 358, "Майже всі давачі підтримують авто-інкремент — дивись у даташиті «burst / auto-increment».",
              11, GREY, "middle", style="italic")
    save("fig-36-5-4-burst.svg", s)


# ── Рис. 36.5.5 — багатобайтове значення (старший+молодший) ──────────────────
def fig55_multibyte():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "16-бітне значення — у двох регістрах: старший і молодший байт", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "прочитати обидва й скласти: value = (старший << 8) | молодший",
              12.5, GREY, "middle", style="italic")
    # два байти
    s += rect(150, 110, 200, 70, LBLUE, BLUE, 2, 8)
    s += text(250, 134, "рег 0x3B", 11, GREY, "middle", "bold")
    s += text(250, 162, "0x12", 18, INK, "middle", "bold")
    s += text(250, 196, "старший байт", 10, BLUE, "middle")
    s += rect(420, 110, 200, 70, LBLUE, BLUE, 2, 8)
    s += text(520, 134, "рег 0x3C", 11, GREY, "middle", "bold")
    s += text(520, 162, "0x34", 18, INK, "middle", "bold")
    s += text(520, 196, "молодший байт", 10, BLUE, "middle")
    s += text(360, 150, "+", 22, INK, "middle", "bold")
    s += arrow(630, 145, 700, 145, GREEN, 2.4)
    s += rect(700, 120, 150, 56, LGRN, GREEN, 2, 8)
    s += text(775, 154, "0x1234", 18, GREEN, "middle", "bold")
    s += text(775, 196, "= 4660", 11, GREY, "middle")

    s += rect(60, 240, W - 120, 100, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 266, "value = (0x12 << 8) | 0x34 = 0x1234", 14, INK, "middle", "bold")
    s += text(W / 2, 292, "Увага на порядок байтів: одні чіпи дають старший першим, інші — молодший (дивись даташит).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 314, "А ще виміри часто ЗІ ЗНАКОМ (доповняльний код) — тоді 16 біт треба трактувати як int16.",
              11, GREY, "middle", style="italic")
    save("fig-36-5-5-multibyte.svg", s)


# ── Рис. 36.5.6 — ідіома Wire ↔ фази шини ────────────────────────────────────
def fig56_wire_code():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 34, "Код (Arduino Wire) ↔ що діється на шині", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ключ — endTransmission(false): «false» означає повторний старт замість СТОПу",
              12.5, GREY, "middle", style="italic")
    code = [
        ("Wire.beginTransmission(0x68);", "S + 0x68 + W"),
        ("Wire.write(0x3B);", "№ рег. 0x3B + A"),
        ("Wire.endTransmission(false);", "(БЕЗ СТОПу → буде Sr)"),
        ("Wire.requestFrom(0x68, 2);", "Sr + 0x68 + R + читання 2 байтів"),
        ("hi = Wire.read();", "1-й байт (+ ACK)"),
        ("lo = Wire.read();", "2-й байт (+ NACK) + P"),
    ]
    yy = 110
    for c, bus in code:
        s += rect(70, yy, 400, 40, "#1e2330", "#111", 1.4, 6)
        s += text(86, yy + 25, c, 11.5, "#9be39b", "start", "bold")
        s += arrow(478, yy + 20, 528, yy + 20, GREY, 1.8)
        s += rect(530, yy, 340, 40, "#fbfbfb", GREY, 1.3, 6)
        s += text(546, yy + 25, bus, 11, INK, "start", "bold")
        yy += 48

    s += rect(60, 400, W - 120, 1, "none", "none", 0)
    save("fig-36-5-6-wire-code.svg", s)


# ── Рис. 36.5.7 — таймінг транзакції й частота опитування ────────────────────
def fig57_timing():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Скільки триває читання й як часто можна опитувати", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "порахуймо такти типового читання двобайтового регістра",
              12.5, GREY, "middle", style="italic")
    s += rect(110, 96, 680, 130, LGREY, GREY, 1.4, 10)
    s += text(130, 122, "читання 2 байтів ≈ S + (адр+W) + рег + Sr + (адр+R) + 2 дані ≈ 5×9 + старти ≈ 50 тактів",
              11.5, INK, "start", "bold")
    s += text(130, 152, "100 кГц: 50 × 10 мкс ≈ 0.5 мс  →  теоретично до ~2000 читань/с", 12.5, INK, "start")
    s += text(130, 178, "400 кГц: 50 × 2.5 мкс ≈ 0.13 мс →  теоретично до ~8000 читань/с", 12.5, GREEN, "start", "bold")
    s += text(130, 204, "(реально менше — є паузи між викликами й обробка)", 10.5, GREY, "start", style="italic")

    s += rect(60, 250, W - 120, 100, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 276, "Висновок: I2C на 100 кГц легко тягне сотні опитувань давача за секунду — для більшості задач досить.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 298, "Треба швидше (IMU на 1 кГц із пакетами) — піднімаєш до 400 кГц або береш SPI (Розділ 37).",
              11.5, INK, "middle")
    s += text(W / 2, 320, "Пам'ятай: кожен байт — 9 тактів (8 + ACK), а старти й адреси теж їдять час.",
              11, GREY, "middle", style="italic")
    save("fig-36-5-7-timing.svg", s)


# ============================================================================
#  §36.6 — Розтягування такту й арбітраж (кілька master)
# ============================================================================

# ── Рис. 36.6.1 — розтягування такту ─────────────────────────────────────────
def fig61_stretch():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 34, "Розтягування такту: ведений притримує SCL внизу — «зачекай»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "якщо ведений не встиг (рахує, готує дані), він тримає SCL низьким, і ведучий мусить чекати",
              12.5, GREY, "middle", style="italic")
    x0, unit = 110, 64
    s += text(x0 - 16, 145, "SCL", 12.5, BLUE, "end", "bold")
    # кілька тактів, потім розтягнутий низький, потім продовження
    segs = [(0, 0.5), (1, 0.5), (0, 0.5), (1, 0.5), (0, 2.2), (1, 0.5), (0, 0.5), (1, 0.5)]
    s += _wave(x0, 124, 162, unit, segs, BLUE, 2.6)[0]
    # зона розтягування
    sx0 = x0 + 2 * unit
    sx1 = x0 + 4.2 * unit
    s += rect(sx0, 118, sx1 - sx0, 80, "#fbf3df", "#b08900", 1.4)
    s += text((sx0 + sx1) / 2, 210, "ведений ТРИМАЄ SCL внизу", 11.5, "#b08900", "middle", "bold")
    s += text((sx0 + sx1) / 2, 228, "(ведучий уже відпустив, та лінія не піднялась)", 10, GREY, "middle", style="italic")
    s += arrow((sx0 + sx1) / 2, 258, (sx0 + sx1) / 2, 200, "#b08900", 1.8)
    s += text(x0, 290, "ведучий чекає, поки SCL підніметься, і лише тоді веде далі", 12, INK, "start", "bold")

    s += rect(60, 320, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 344, "Розтягування — це «гальмо» з боку веденого: єдиний спосіб для повільного чіпа сказати «ще не готовий».",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 364, "Працює лише тому, що SCL — відкритий колектор (§36.2): притримати внизу може будь-хто.",
              11, GREY, "middle", style="italic")
    save("fig-36-6-1-stretch.svg", s)


# ── Рис. 36.6.2 — чому працює і де пастка ────────────────────────────────────
def fig62_stretch_why():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому розтягування працює — і де його пастка", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ведучий МУСИТЬ дивитися на реальний SCL, а не просто «цокати» за таймером",
              12.5, GREY, "middle", style="italic")
    # ліворуч: правильно
    s += rect(60, 90, 380, 230, "none", FAINT, 2, 12)
    s += text(250, 116, "правильний ведучий", 13, GREEN, "middle", "bold")
    s += text(80, 150, "1. відпускає SCL (хоче «1»)", 11, INK, "start")
    s += text(80, 176, "2. ЧИТАЄ реальний SCL", 11, INK, "start", "bold")
    s += text(80, 202, "3. ще «0»? → ведений тримає → чекаю", 11, GREEN, "start")
    s += text(80, 228, "4. став «1»? → веду далі", 11, INK, "start")
    s += text(250, 286, "поважає розтягування ✓", 11.5, GREEN, "middle", "bold")
    # праворуч: пастка
    s += rect(460, 90, 380, 230, "none", FAINT, 2, 12)
    s += text(650, 116, "наївний ведучий", 13, RED, "middle", "bold")
    s += text(480, 150, "цокає SCL за жорстким таймером,", 11, INK, "start")
    s += text(480, 176, "не дивлячись на реальну лінію", 11, RED, "start", "bold")
    s += text(480, 210, "→ «переїжджає» розтягування,", 11, INK, "start")
    s += text(480, 232, "  читає недоготовлені дані", 11, RED, "start", "bold")
    s += text(650, 286, "часта біда bit-bang та дешевих чіпів", 10.5, GREY, "middle", style="italic")

    s += rect(60, 336, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 361, "Якщо давач «іноді віддає сміття» — підозрюй, що ведучий не підтримує розтягування такту.",
              11.5, INK, "middle", "bold")
    save("fig-36-6-2-stretch-why.svg", s)


# ── Рис. 36.6.3 — кілька ведучих і вільна шина ───────────────────────────────
def fig63_multimaster():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Кілька ведучих на одній шині", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "два мікроконтролери ділять давачі; перш ніж почати, ведучий чекає, поки шина ВІЛЬНА",
              12.5, GREY, "middle", style="italic")
    sda_y, scl_y = 150, 186
    s += line(140, sda_y, 820, sda_y, RED, 3)
    s += line(140, scl_y, 820, scl_y, BLUE, 3)
    s += text(828, sda_y + 4, "SDA", 11.5, RED, "start", "bold")
    s += text(828, scl_y + 4, "SCL", 11.5, BLUE, "start", "bold")
    devs = [("MCU-1", 240, GREEN, "ведучий"), ("MCU-2", 400, GREEN, "ведучий"),
            ("давач", 560, INK, "ведений"), ("давач", 700, INK, "ведений")]
    for name, cx, col, role in devs:
        s += rect(cx - 50, 230, 100, 60, ("#eef6ef" if col == GREEN else "#fbfbfb"), col, 2, 8)
        s += text(cx, 256, name, 12, col, "middle", "bold")
        s += text(cx, 276, role, 10, GREY, "middle")
        s += line(cx - 14, 230, cx - 14, sda_y, RED, 2)
        s += line(cx + 14, 230, cx + 14, scl_y, BLUE, 2)

    s += rect(60, 320, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 344, "Виявлення вільної шини: ведучий стартує, лише коли обидві лінії високі (після СТОПу).",
              12, INK, "middle", "bold")
    s += text(W / 2, 364, "А якщо двоє стартують майже водночас — їх розсудить арбітраж (далі).",
              11.5, GREY, "middle", style="italic")
    save("fig-36-6-3-multimaster.svg", s)


# ── Рис. 36.6.4 — арбітраж: хто жене «0», той виграє ────────────────────────
def fig64_arbitration():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 34, "Арбітраж: двоє почали разом — біт за бітом на SDA", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "на першому ж біті, де вони різні, перемагає той, хто жене «0» (бо «тягни вниз» сильніший)",
              12.5, GREY, "middle", style="italic")
    x0, unit = 150, 90
    bitsA = [1, 0, 1, 0]   # ведучий A хоче слати 1010...
    bitsB = [1, 0, 0, 1]   # ведучий B хоче слати 1001... → різниця на 3-му біті
    # A
    s += text(x0 - 16, 130, "хоче A", 11.5, GREEN, "end", "bold")
    s += _wave(x0, 112, 146, unit, [(b, 1.0) for b in bitsA], GREEN, 2.4)[0]
    # B
    s += text(x0 - 16, 200, "хоче B", 11.5, "#b08900", "end", "bold")
    s += _wave(x0, 182, 216, unit, [(b, 1.0) for b in bitsB], "#b08900", 2.4)[0]
    # реальна лінія = wired-AND
    realline = [min(a, b) for a, b in zip(bitsA, bitsB)]
    s += text(x0 - 16, 280, "лінія SDA", 11.5, RED, "end", "bold")
    s += _wave(x0, 262, 296, unit, [(b, 1.0) for b in realline], RED, 2.8)[0]
    # позначка точки розходження (3-й біт)
    dx = x0 + 2 * unit
    s += line(dx, 106, dx, 300, INK, 1.2, dash="4,3")
    s += text(dx + unit / 2, 100, "тут A жене 0, B жене 1", 10.5, INK, "middle", "bold")
    s += text(dx + unit / 2, 320, "лінія = 0 (A переміг)", 11, GREEN, "middle", "bold")
    s += text(dx + unit / 2, 338, "B бачить 0, хоч хотів 1 → програв", 10.5, "#b08900", "middle", "bold")

    s += rect(60, 358, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 383, "Арбітраж недеструктивний: лінія сама = «І» обох, переможець навіть не помічає суперника.",
              11.5, INK, "middle", "bold")
    save("fig-36-6-4-arbitration.svg", s)


# ── Рис. 36.6.5 — як переможений розуміє програш ─────────────────────────────
def fig65_loser():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Як переможений дізнається про програш: жену «1», читаю «0»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен ведучий, женучи біт, ОДРАЗУ читає лінію назад; розбіжність = «я програв»",
              12.5, GREY, "middle", style="italic")
    # B
    s += rect(70, 100, 360, 200, "none", FAINT, 2, 12)
    s += text(250, 126, "ведучий B (програв)", 13, "#b08900", "middle", "bold")
    s += text(90, 158, "жене: 1 (відпускає SDA)", 11.5, INK, "start", "bold")
    s += text(90, 184, "читає: 0 (хтось тягне вниз)", 11.5, RED, "start", "bold")
    s += text(90, 214, "1 ≠ 0 → ПРОГРАВ", 12.5, RED, "start", "bold")
    s += text(90, 244, "→ негайно замовкає,", 11, INK, "start")
    s += text(90, 266, "  стає веденим / повторить пізніше", 11, INK, "start")
    # A
    s += rect(470, 100, 360, 200, "none", FAINT, 2, 12)
    s += text(650, 126, "ведучий A (переміг)", 13, GREEN, "middle", "bold")
    s += text(490, 158, "жене: 0 (тягне SDA вниз)", 11.5, INK, "start", "bold")
    s += text(490, 184, "читає: 0 (як і хотів)", 11.5, GREEN, "start", "bold")
    s += text(490, 214, "0 = 0 → усе гаразд", 12.5, GREEN, "start", "bold")
    s += text(490, 244, "→ веде далі, НЕ помітивши,", 11, INK, "start")
    s += text(490, 266, "  що поряд хтось був", 11, INK, "start")

    s += rect(60, 316, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 340, "Жодного зіпсованого байта: повідомлення переможця проходить ціле, переможений просто відступив.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 360, "Це і є «недеструктивний арбітраж» — ще один подарунок відкритого колектора.",
              11, GREY, "middle", style="italic")
    save("fig-36-6-5-loser.svg", s)


# ── Рис. 36.6.6 — синхронізація SCL кількох ведучих ──────────────────────────
def fig66_sclsync():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Синхронізація такту: кілька ведучих автоматично йдуть у ногу", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "спільний SCL = монтажне «І»: низько — поки ХОЧ ОДИН тримає; високо — лише коли всі відпустили",
              12.5, GREY, "middle", style="italic")
    x0, unit = 150, 80
    # A clock
    s += text(x0 - 16, 130, "SCL від A", 11, GREEN, "end", "bold")
    sa = [(1, 0.5), (0, 0.5), (1, 0.5), (0, 0.7), (1, 0.5)]
    s += _wave(x0, 112, 146, unit, sa, GREEN, 2.2)[0]
    # B clock
    s += text(x0 - 16, 200, "SCL від B", 11, "#b08900", "end", "bold")
    sb = [(1, 0.7), (0, 0.5), (1, 0.5), (0, 0.5), (1, 0.5)]
    s += _wave(x0, 182, 216, unit, sb, "#b08900", 2.2)[0]
    # combined (min)
    s += text(x0 - 16, 280, "реальний SCL", 11, BLUE, "end", "bold")
    # будуємо комбінований на дрібній сітці
    res = []
    grid = 0.1
    tA = [(1, 0.5), (0, 0.5), (1, 0.5), (0, 0.7), (1, 0.5)]
    def level_at(segs, t):
        acc = 0
        for lv, w in segs:
            if t < acc + w:
                return lv
            acc += w
        return segs[-1][0]
    total = 2.7
    n = int(total / grid)
    for i in range(n):
        t = i * grid
        res.append((min(level_at(sa, t), level_at(sb, t)), grid))
    s += _wave(x0, 262, 296, unit, res, BLUE, 2.6)[0]
    s += text(x0 + 2.7 * unit + 14, 280, "низько = найдовше низько", 10, GREY, "start")
    s += text(x0 + 2.7 * unit + 14, 296, "високо = найкоротше високо", 10, GREY, "start")

    s += rect(60, 326, W - 120, 50, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 350, "Тому під час арбітражу обидва ведучі бачать ОДНАКОВІ такти — і чесно порівнюють біти на SDA.",
              11.5, INK, "middle", "bold")
    save("fig-36-6-6-sclsync.svg", s)


# ── Рис. 36.6.7 — реальність: один ведучий чи кілька ─────────────────────────
def fig67_reality():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Що з цього треба насправді", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у житті більшість систем — з одним ведучим; складніше потрібне рідше",
              12.5, GREY, "middle", style="italic")
    s += rect(60, 90, 380, 200, LGRN, GREEN, 1.8, 12)
    s += text(250, 116, "один ведучий (майже завжди)", 12.5, GREEN, "middle", "bold")
    s += text(80, 146, "• один МК керує всіма давачами", 11, INK, "start")
    s += text(80, 170, "• арбітраж не потрібен зовсім", 11, INK, "start")
    s += text(80, 194, "• розтягування — ТАК, буває в давачів", 11, INK, "start", "bold")
    s += text(80, 218, "• перевір, чи МК його підтримує", 11, GREY, "start")
    s += text(250, 256, "це твій типовий випадок", 11, GREEN, "middle", "bold")
    s += rect(460, 90, 380, 200, "#fbfbfb", GREY, 1.8, 12)
    s += text(650, 116, "кілька ведучих (рідко)", 12.5, INK, "middle", "bold")
    s += text(480, 146, "• два МК на спільних давачах", 11, INK, "start")
    s += text(480, 170, "• хост + співпроцесор", 11, INK, "start")
    s += text(480, 194, "• ось тут і потрібні арбітраж", 11, INK, "start")
    s += text(480, 218, "  та виявлення вільної шини", 11, INK, "start")
    s += text(650, 256, "знати — корисно, вживати — нечасто", 11, GREY, "middle", style="italic")

    s += rect(60, 306, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 331, "Практичний підсумок: завжди пам'ятай про розтягування такту; про арбітраж — коли ведучих справді кілька.",
              11.5, INK, "middle", "bold")
    save("fig-36-6-7-reality.svg", s)


# ============================================================================
#  §36.7 — Типова регістрова карта давача (як «заговорити» з чіпом)
# ============================================================================

# ── Рис. 36.7.1 — як читати регістрову карту ─────────────────────────────────
def fig71_regmap():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "Регістрова карта з даташита: як її читати", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "таблиця регістрів — це «інструкція», як розмовляти саме з цим чіпом",
              12.5, GREY, "middle", style="italic")
    bx, by, rw = 70, 96, 780
    cols = [("адреса", 16), ("назва", 110), ("R/W", 300), ("скидання", 380), ("призначення", 500)]
    s += rect(bx, by, rw, 34, "#f0f0f0", GREY, 1.3, 6)
    for c, dx in cols:
        s += text(bx + dx, by + 22, c, 11.5, INK, "start", "bold")
    rows = [
        ("0x00", "WHO_AM_I", "R", "0x68", "сталий код чіпа — перевірити, що це він", BLUE),
        ("0x1B", "CONFIG", "R/W", "0x00", "діапазон і фільтр (по бітах)", "#b08900"),
        ("0x6B", "PWR_MGMT", "R/W", "0x40", "сон/пробудження, джерело такту", "#b08900"),
        ("0x3B", "DATA_X_H", "R", "0x00", "вимір осі X, старший байт", GREEN),
        ("0x3C", "DATA_X_L", "R", "0x00", "вимір осі X, молодший байт", GREEN),
        ("0x75", "STATUS", "R", "0x00", "готовність нового виміру", INK),
    ]
    yy = by + 34
    for addr, name, rwv, rst, desc, col in rows:
        s += rect(bx, yy, rw, 38, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 24, addr, 11.5, "#b06000", "start", "bold")
        s += text(bx + 110, yy + 24, name, 11.5, col, "start", "bold")
        s += text(bx + 300, yy + 24, rwv, 11.5, INK, "start")
        s += text(bx + 380, yy + 24, rst, 11.5, GREY, "start")
        s += text(bx + 500, yy + 24, desc, 10.8, INK, "start")
        yy += 38

    s += rect(60, 364, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 390, "Чотири типи рядків: ID (перевірка), CONFIG/PWR (налаштування), DATA (виміри), STATUS (стан).",
              11.5, INK, "middle", "bold")
    save("fig-36-7-1-regmap.svg", s)


# ── Рис. 36.7.2 — біти всередині регістра ────────────────────────────────────
def fig72_bitfields():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Один регістр — кілька налаштувань: бітові поля", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у байт CONFIG напхано кілька параметрів; кожне займає свої біти",
              12.5, GREY, "middle", style="italic")
    x0, cw = 150, 76
    bits = ["RST", "—", "—", "RNG", "RNG", "FLT", "FLT", "FLT"]
    cols = [RED, GREY, GREY, "#b08900", "#b08900", BLUE, BLUE, BLUE]
    for i in range(8):
        s += rect(x0 + i * cw, 110, cw, 50, "#ffffff", cols[i], 1.8, 4)
        s += text(x0 + i * cw + cw / 2, 140, bits[i], 11, cols[i], "middle", "bold")
        s += text(x0 + i * cw + cw / 2, 102, "b%d" % (7 - i), 10, GREY, "middle")
    # підписи полів
    s += text(x0 + 0.5 * cw, 184, "RST: скинути чіп", 10.5, RED, "middle", "bold")
    s += text(x0 + 3.5 * cw, 184, "RNG: діапазон (2 біти)", 10.5, "#b08900", "middle", "bold")
    s += text(x0 + 6 * cw, 184, "FLT: фільтр (3 біти)", 10.5, BLUE, "middle", "bold")

    s += rect(60, 220, W - 120, 130, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 246, "Щоб змінити ОДНЕ поле, не зачепивши інших, роблять «читай-зміни-запиши»:", 12, INK, "middle", "bold")
    s += text(80, 274, "1. прочитати поточний байт регістра", 11.5, INK, "start")
    s += text(80, 298, "2. замаскувати потрібні біти (AND з ~маска), вставити нове значення (OR)", 11.5, INK, "start")
    s += text(80, 322, "3. записати байт назад — решта налаштувань збереглася", 11.5, INK, "start")
    save("fig-36-7-2-bitfields.svg", s)


# ── Рис. 36.7.3 — рецепт «оживлення» чіпа ────────────────────────────────────
def fig73_recipe():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 34, "Універсальний рецепт «оживлення» будь-якого I2C-чіпа", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "ті самі чотири кроки працюють майже для кожного давача",
              12.5, GREY, "middle", style="italic")
    steps = [
        ("1. СКАН", "знайти адресу\n(§36.3)", BLUE),
        ("2. WHO_AM_I", "звірити ID —\nце справді він?", "#b08900"),
        ("3. НАЛАШТУВАТИ", "розбудити, задати\nдіапазон, частоту", GREEN),
        ("4. ЧИТАТИ", "пакетом виміри,\nскласти й масштабувати", INK),
    ]
    x0, bw, gap, y = 60, 195, 30, 130
    for i, (title, body, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        s += rect(x, y, bw, 90, "#fbfbfb", col, 2.2, 12)
        s += text(x + bw / 2, y + 28, title, 13, col, "middle", "bold")
        for j, ln in enumerate(body.split("\n")):
            s += text(x + bw / 2, y + 50 + j * 16, ln, 10.5, INK, "middle")
        if i < 3:
            s += arrow(x + bw, y + 45, x + bw + gap, y + 45, INK, 2)
    # цикл назад від 4 до 4
    s += f'<path d="M {x0+3*(bw+gap)+bw/2},{y+90} C {x0+3*(bw+gap)+bw/2},{y+140} {x0+3*(bw+gap)+bw-20},{y+140} {x0+3*(bw+gap)+bw-20},{y+92}" fill="none" stroke="{INK}" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#aInk)"/>\n'
    s += text(x0 + 3 * (bw + gap) + bw / 2, y + 156, "повторювати в циклі", 10.5, GREY, "middle", style="italic")

    s += rect(60, 300, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 326, "Перші три кроки — раз при старті; четвертий — у головному циклі стільки разів, скільки треба вимірів.",
              11.5, INK, "middle", "bold")
    save("fig-36-7-3-recipe.svg", s)


# ── Рис. 36.7.4 — перевірка WHO_AM_I ─────────────────────────────────────────
def fig74_whoami():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "WHO_AM_I: найперша перевірка перед будь-чим", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "прочитати сталий ID-регістр і звірити з очікуваним — переконатися, що чіп і дроти справні",
              12.5, GREY, "middle", style="italic")
    s += rect(80, 100, 320, 130, "none", FAINT, 2, 12)
    s += text(240, 126, "читаємо 0x00 (WHO_AM_I)", 12, INK, "middle", "bold")
    s += text(240, 160, "очікуємо: 0x68", 12.5, GREY, "middle")
    s += text(240, 196, "отримали: 0x68 ✓", 13, GREEN, "middle", "bold")
    s += arrow(410, 165, 480, 165, GREEN, 2.4)
    s += rect(490, 120, 330, 90, LGRN, GREEN, 2, 12)
    s += text(655, 150, "збіглося →", 12.5, GREEN, "middle", "bold")
    s += text(655, 174, "це той чіп, адреса й дроти ОК", 11.5, INK, "middle", "bold")
    s += text(655, 196, "можна налаштовувати далі", 10.5, GREY, "middle")

    s += rect(60, 250, W - 120, 80, LRED, RED, 1.4, 10)
    s += text(W / 2, 276, "Не збіглося (0x00, 0xFF, інше) → не починай налаштування: спершу розберись із дротами/адресою.",
              12, INK, "middle", "bold")
    s += text(W / 2, 298, "0xFF або 0x00 на всіх регістрах — типова ознака відсутнього живлення чи обірваної лінії.",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 318, "WHO_AM_I економить години: він одразу відділяє «чіп живий» від «щось із підключенням».",
              11, GREY, "middle", style="italic")
    save("fig-36-7-4-whoami.svg", s)


# ── Рис. 36.7.5 — читай-зміни-запиши одне поле ───────────────────────────────
def fig75_rmw():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Змінити одне поле, не зачепивши решти: читай-зміни-запиши", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "хочемо поставити діапазон RNG = 10, а біти фільтра й решту лишити як були",
              12.5, GREY, "middle", style="italic")
    def bitbox(x, y, bits, hl=()):
        out = ""
        for i, b in enumerate(bits):
            col = RED if i in hl else GREY
            fill = LRED if i in hl else "#ffffff"
            out += rect(x + i * 46, y, 46, 36, fill, col, 1.4)
            out += text(x + i * 46 + 23, y + 24, b, 12, (RED if i in hl else INK), "middle", "bold")
        return out
    x0 = 250
    s += text(x0 - 16, 118, "прочитали:", 11.5, INK, "end", "bold")
    s += bitbox(x0, 100, list("00011010"))
    s += text(x0 + 8 * 46 + 16, 124, "= 0x1A", 12, INK, "start", "bold")
    s += text(x0 - 16, 178, "маска RNG:", 11.5, INK, "end", "bold")
    s += bitbox(x0, 160, list("00011000"), hl=(3, 4))
    s += text(x0 + 8 * 46 + 16, 184, "біти 4:3", 11, "#b08900", "start", "bold")
    s += text(x0 - 16, 238, "результат:", 11.5, GREEN, "end", "bold")
    s += bitbox(x0, 220, list("00010010"), hl=(3, 4))
    s += text(x0 + 8 * 46 + 16, 244, "= 0x12 (RNG=10)", 12, GREEN, "start", "bold")

    s += rect(60, 280, W - 120, 56, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 304, "reg = (reg & ~0x18) | (0b10 « 3);  — обнулити старе поле, вставити нове, решта недоторкана.",
              12, INK, "middle", "bold")
    s += text(W / 2, 324, "Сліпо записати весь байт — означало б випадково перезатерти інші налаштування.",
              11, GREY, "middle", style="italic")
    save("fig-36-7-5-rmw.svg", s)


# ── Рис. 36.7.6 — сирий відлік → фізична величина ────────────────────────────
def fig76_scale():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Сирий відлік → фізична величина: масштаб із даташита", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "чіп віддає «голі» числа (counts); даташит дає чутливість, щоб перевести їх у g, °/с, °C…",
              12.5, GREY, "middle", style="italic")
    s += rect(120, 100, 200, 70, LBLUE, BLUE, 2, 8)
    s += text(220, 130, "сирий int16", 11, GREY, "middle")
    s += text(220, 154, "8192", 17, INK, "middle", "bold")
    s += arrow(322, 135, 392, 135, GREEN, 2.4)
    s += text(357, 122, "÷ чутливість", 10.5, GREEN, "middle", "bold")
    s += rect(400, 100, 230, 70, "#fbfbfb", GREY, 1.6, 8)
    s += text(515, 128, "16384 LSB/g", 12.5, INK, "middle", "bold")
    s += text(515, 152, "(з даташита)", 10, GREY, "middle")
    s += arrow(632, 135, 702, 135, GREEN, 2.4)
    s += rect(710, 100, 150, 70, LGRN, GREEN, 2, 8)
    s += text(785, 138, "0.5 g", 18, GREEN, "middle", "bold")

    s += rect(60, 200, W - 120, 130, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 226, "величина = сирий_відлік / чутливість = 8192 / 16384 = 0.5 g", 13.5, INK, "middle", "bold")
    s += text(W / 2, 252, "для гіроскопа — LSB/(°/с), для барометра — свої формули, для температури — зсув і масштаб.", 11.5, INK, "middle")
    s += text(W / 2, 276, "Часто ще треба КАЛІБРУВАННЯ (зсув нуля) — як ми бачили в давачах Модуля 5.", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, 300, "Без масштабу «8192» нічого не означає; саме даташит робить із відліку фізику.", 11, GREY, "middle", style="italic")
    save("fig-36-7-6-scale.svg", s)


# ── Рис. 36.7.7 — універсальний підхід ───────────────────────────────────────
def fig77_mindset():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Універсальне вміння: протокол + даташит = розмова з будь-яким чіпом", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "механіка I2C однакова для всіх; даташит лише підставляє адресу, регістри й масштаби",
              12.5, GREY, "middle", style="italic")
    s += rect(80, 100, 320, 120, LGRN, GREEN, 2, 12)
    s += text(240, 128, "протокол I2C", 13.5, GREEN, "middle", "bold")
    s += text(240, 150, "(цей розділ — універсальний)", 10.5, GREY, "middle")
    s += text(100, 176, "старт · адреса · R/W · ACK", 11, INK, "start")
    s += text(100, 198, "регістри · повторний старт · пакет", 11, INK, "start")
    s += text(420, 165, "+", 26, INK, "middle", "bold")
    s += rect(470, 100, 350, 120, LBLUE, BLUE, 2, 12)
    s += text(645, 128, "даташит чіпа", 13.5, BLUE, "middle", "bold")
    s += text(645, 150, "(специфічний для пристрою)", 10.5, GREY, "middle")
    s += text(490, 176, "адреса · карта регістрів", 11, INK, "start")
    s += text(490, 198, "біти налаштувань · масштаби", 11, INK, "start")

    s += rect(60, 244, W - 120, 80, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 270, "Знаючи протокол, нову мікросхему «вмикаєш» за пів години: відкрив даташит, знайшов адресу й регістри — і говориш.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 292, "Це і є ціль розділу: не завчити один давач, а вміти прочитати й «оживити» БУДЬ-ЯКИЙ.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Готові бібліотеки — зручність, але тепер ти розумієш, що саме вони роблять усередині.",
              11, GREY, "middle", style="italic")
    save("fig-36-7-7-mindset.svg", s)


if __name__ == "__main__":
    # — історія (секція 0) —
    fig_timeline()
    fig_problem()
    fig_solution()
    fig_naming()
    fig_evolution()
    # — §36.1 —
    fig11_topology()
    fig12_sync()
    fig13_datavalid()
    fig14_bit()
    fig15_roles()
    fig16_duplex()
    fig17_vs_uart()
    # — §36.2 —
    fig21_contention()
    fig22_opendrain()
    fig23_wiredand()
    fig24_manydev()
    fig25_risefall()
    fig26_pullup_sizing()
    fig27_enables()
    # — §36.3 —
    fig31_addrbyte()
    fig32_select()
    fig33_rw()
    fig34_7vs8()
    fig35_addrpins()
    fig36_addrmap()
    fig37_scanner()
    # — §36.4 —
    fig41_startstop()
    fig42_unmistakable()
    fig43_ack()
    fig44_whoack()
    fig45_transaction()
    fig46_repeated_start()
    fig47_nack_diag()
    # — §36.5 —
    fig51_registers()
    fig52_write()
    fig53_read()
    fig54_burst()
    fig55_multibyte()
    fig56_wire_code()
    fig57_timing()
    # — §36.6 —
    fig61_stretch()
    fig62_stretch_why()
    fig63_multimaster()
    fig64_arbitration()
    fig65_loser()
    fig66_sclsync()
    fig67_reality()
    # — §36.7 —
    fig71_regmap()
    fig72_bitfields()
    fig73_recipe()
    fig74_whoami()
    fig75_rmw()
    fig76_scale()
    fig77_mindset()
    print("done.")
