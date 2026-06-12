# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для 🔌-вставки §3.4.7c — «Endianness у даташитах давачів».
Клас давача середовища (BME-клас: температура/тиск/вологість).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація фігур вставки: Рис. 3.4.7c.k → файли fig-17-7c-k-*.svg (унікальні, не чіпають fig-17-7-*).
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
PAPER = "#f3f5f8"
AMBER = "#b9791f"
VIOLET = "#7a3ea8"
TEAL = "#1f7e8a"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"
MONO = "Consolas, 'DejaVu Sans Mono', monospace"


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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = MONO if mono else FONT
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


# ── Рис. 3.4.7c.1 — карта регістрів давача: одна величина у двох регістрах ─────
def fig_register_map():
    W, H = 950, 520
    s = header(W, H)
    s += text(W / 2, 34, "Карта регістрів давача середовища: одна величина — кілька регістрів",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен регістр тримає лише 8 бітів, тож 16- і 20-бітні результати «розрізані» на сусідні адреси",
              12.5, GREY, "middle", style="italic")

    # Колонки таблиці
    x_addr = 70
    x_name = 200
    x_byte = 430
    x_role = 600
    row_h = 36
    y0 = 92

    # Заголовок таблиці
    s += rect(x_addr, y0, 760, 30, PAPER, GREY, 1.4)
    s += text(x_addr + 18, y0 + 20, "Адреса", 13.5, INK, "start", "bold")
    s += text(x_name + 10, y0 + 20, "Регістр (даташит)", 13.5, INK, "start", "bold")
    s += text(x_byte + 10, y0 + 20, "Вміст (8 бітів)", 13.5, INK, "start", "bold")
    s += text(x_role + 10, y0 + 20, "Роль байта", 13.5, INK, "start", "bold")

    rows = [
        ("0xF7", "press_msb",  "P[19:12]", "старший байт тиску",   RED,   "тиск"),
        ("0xF8", "press_lsb",  "P[11:4]",  "молодший байт тиску",  RED,   "тиск"),
        ("0xF9", "press_xlsb", "P[3:0]·0000", "додаткові 4 біти",  RED,   "тиск"),
        ("0xFA", "temp_msb",   "T[19:12]", "старший байт темпер.", BLUE,  "темп."),
        ("0xFB", "temp_lsb",   "T[11:4]",  "молодший байт темпер.",BLUE,  "темп."),
        ("0xFC", "temp_xlsb",  "T[3:0]·0000", "додаткові 4 біти",  BLUE,  "темп."),
        ("0xFD", "hum_msb",    "H[15:8]",  "старший байт вологості",GREEN,"волог."),
        ("0xFE", "hum_lsb",    "H[7:0]",   "молодший байт вологості",GREEN,"волог."),
    ]
    y = y0 + 30
    for (addr, name, content, role, col, grp) in rows:
        tint = {RED: "#fbeceb", BLUE: "#eaeefb", GREEN: "#e8f5ec"}[col]
        s += rect(x_addr, y, 760, row_h, tint, FAINT, 1.0)
        s += text(x_addr + 18, y + row_h / 2 + 5, addr, 14, INK, "start", "bold", mono=True)
        s += text(x_name + 10, y + row_h / 2 + 5, name, 14, col, "start", "bold", mono=True)
        s += text(x_byte + 10, y + row_h / 2 + 5, content, 13, INK, "start", mono=True)
        s += text(x_role + 10, y + row_h / 2 + 5, role, 12.5, INK, "start")
        y += row_h

    s += rect(x_addr, y0 + 30, 760, row_h * len(rows), "none", GREY, 1.6)

    # Дужка: 16-бітна вологість = два регістри
    bx = x_addr + 760 + 14
    yt = y0 + 30 + row_h * 6
    yb = y0 + 30 + row_h * 8
    s += line(bx, yt + 4, bx + 12, yt + 4, GREEN, 2)
    s += line(bx + 12, yt + 4, bx + 12, yb - 4, GREEN, 2)
    s += line(bx + 12, yb - 4, bx, yb - 4, GREEN, 2)
    s += text(bx + 20, (yt + yb) / 2 - 6, "16 бітів", 13, GREEN, "start", "bold")
    s += text(bx + 20, (yt + yb) / 2 + 12, "вологості", 12, GREEN, "start")

    # Підпис унизу: MSB-first у просторі регістрів
    s += text(x_addr, y + 30,
              "MSB-байт — за МЕНШОЮ адресою (0xF7), молодший — за більшою: у даташиті регістри впорядковані big-endian,",
              12.5, INK, "start")
    s += text(x_addr, y + 50,
              "хоч сам мікроконтролер (ESP32, ARM) — little-endian. Порядок диктує ДАВАЧ, а не процесор.",
              12.5, AMBER, "start", "bold")
    save("fig-17-7c-1-register-map.svg", s)


# ── Рис. 3.4.7c.2 — пакетне читання: один указівник, потік байтів ─────────────
def fig_burst_read():
    W, H = 860, 470
    s = header(W, H)
    s += text(W / 2, 34, "Пакетне читання: один указівник регістра — потік байтів поспіль",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "контролер ставить указівник на 0xF7 і читає 8 байтів підряд; давач сам збільшує адресу",
              12.5, GREY, "middle", style="italic")

    # МК ліворуч, давач праворуч
    s += rect(40, 110, 150, 90, PAPER, INK, 2, 8)
    s += text(115, 142, "Мікро-", 15, INK, "middle", "bold")
    s += text(115, 162, "контролер", 15, INK, "middle", "bold")
    s += text(115, 184, "(little-endian)", 11.5, GREY, "middle")

    s += rect(670, 110, 150, 90, PAPER, INK, 2, 8)
    s += text(745, 142, "Давач", 15, INK, "middle", "bold")
    s += text(745, 162, "середовища", 13, INK, "middle")
    s += text(745, 184, "автоінкремент", 11.5, TEAL, "middle")

    # Крок 1: запис указівника
    s += arrow(190, 138, 670, 138, INK, 2.2)
    s += text(430, 128, "1) запиши адресу указівника = 0xF7", 13, INK, "middle", "bold")

    # Крок 2: потік 8 байтів назад
    s += arrow(670, 176, 190, 176, GREEN, 2.2)
    s += text(430, 200, "2) читай — давач віддає байт за байтом, адреса росте сама", 13, GREEN, "middle", "bold")

    # Стрічка байтів
    bx0 = 70
    by = 280
    bw = 84
    bh = 64
    cells = [
        ("0xF7", "press_msb", RED),
        ("0xF8", "press_lsb", RED),
        ("0xF9", "press_xlsb", RED),
        ("0xFA", "temp_msb", BLUE),
        ("0xFB", "temp_lsb", BLUE),
        ("0xFC", "temp_xlsb", BLUE),
        ("0xFD", "hum_msb", GREEN),
        ("0xFE", "hum_lsb", GREEN),
    ]
    for i, (addr, name, col) in enumerate(cells):
        x = bx0 + i * (bw + 6)
        tint = {RED: "#fbeceb", BLUE: "#eaeefb", GREEN: "#e8f5ec"}[col]
        s += rect(x, by, bw, bh, tint, col, 1.8, 5)
        s += text(x + bw / 2, by - 8, addr, 11.5, GREY, "middle", mono=True)
        s += text(x + bw / 2, by + 26, f"байт {i}", 12.5, INK, "middle", "bold")
        s += text(x + bw / 2, by + 46, name, 10.5, col, "middle", mono=True)

    # Порядок надходження
    s += arrow(bx0, by + bh + 26, bx0 + 7 * (bw + 6) + bw, by + bh + 26, GREY, 1.8)
    s += text(bx0, by + bh + 50, "порядок у часі →", 12, GREY, "start", style="italic")
    s += text(W / 2, by + bh + 50,
              "три величини за одне читання — і всі байти зчитані з ОДНОГО зрізу часу (без «розриву» між темпер. і тиском)",
              12, INK, "middle")
    save("fig-17-7c-2-burst-read.svg", s)


# ── Рис. 3.4.7c.3 — складання 20-бітного результату зсувами проти приведення ──
def fig_reassembly():
    W, H = 860, 540
    s = header(W, H)
    s += text(W / 2, 34, "Складання результату: явні зсуви проти «приведення вказівника»",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "три байти 0xFA–0xFC треба зібрати в одне 20-бітне ціле T — порозрядно, не покладаючись на пам'ять",
              12.5, GREY, "middle", style="italic")

    # Три вхідні байти
    bx0 = 120
    by = 92
    bw = 150
    bh = 52
    parts = [
        ("temp_msb", "T[19:12]", "<< 12", "0xFA"),
        ("temp_lsb", "T[11:4]",  "<< 4",  "0xFB"),
        ("temp_xlsb","T[3:0]",   ">> 4",  "0xFC"),
    ]
    for i, (name, bits, op, addr) in enumerate(parts):
        x = bx0 + i * (bw + 40)
        s += rect(x, by, bw, bh, "#eaeefb", BLUE, 1.8, 5)
        s += text(x + bw / 2, by - 8, addr, 11.5, GREY, "middle", mono=True)
        s += text(x + bw / 2, by + 22, name, 13, BLUE, "middle", "bold", mono=True)
        s += text(x + bw / 2, by + 42, bits, 12, INK, "middle", mono=True)
        # операція зсуву
        s += text(x + bw / 2, by + bh + 26, op, 16, RED, "middle", "bold", mono=True)
        s += arrow(x + bw / 2, by + bh + 36, x + bw / 2, by + bh + 64, RED, 2)

    # Об'єднувач OR
    oy = by + bh + 78
    s += rect(bx0, oy, bw * 3 + 80, 40, "#fbeceb", RED, 1.6, 6)
    s += text(bx0 + (bw * 3 + 80) / 2, oy + 25,
              "int32_t T = (msb << 12) | (lsb << 4) | (xlsb >> 4);", 15.5, INK, "middle", "bold", mono=True)

    # Результат: 20-бітне число
    ry = oy + 70
    s += text(W / 2, ry, "20-бітний «сирий» результат T (raw ADC value)", 13.5, GREEN, "middle", "bold")
    # бітова лінійка 20 біт — три смуги джерел
    cell = 33
    total = 20
    rx0 = (W - cell * total) / 2
    ry2 = ry + 14
    seg = [("T[19:12] ← msb", 8, "#eaeefb", BLUE),
           ("T[11:4] ← lsb", 8, "#fbeceb", RED),
           ("T[3:0] ← xlsb", 4, "#e8f5ec", GREEN)]
    xx = rx0
    for (lab, n, tint, col) in seg:
        w = cell * n
        s += rect(xx, ry2, w, 34, tint, col, 1.6)
        s += text(xx + w / 2, ry2 + 22, lab, 12, col, "middle", "bold", mono=True)
        xx += w
    s += rect(rx0, ry2, cell * total, 34, "none", INK, 1.8)
    s += text(W / 2, ry2 + 56, "✓ той самий результат на БУДЬ-ЯКІЙ машині — little- чи big-endian",
              13, GREEN, "middle", "bold")

    # Антипатерн праворуч унизу
    ay = ry2 + 86
    s += rect(70, ay, 720, 56, "#fff4f4", RED, 1.6, 6)
    s += text(90, ay + 22, "✗  int32_t T = *(int32_t*)buf;",
              14.5, RED, "start", "bold", mono=True)
    s += text(310, ay + 22,
              "— читає байти «як лежать»: ламається на чужій ендіанності,", 12.5, INK, "start")
    s += text(310, ay + 42,
              "а ще — невирівняна адреса (alignment) і суворе аліасування (strict aliasing). Не робіть так.",
              12.5, INK, "start")
    save("fig-17-7c-3-reassembly.svg", s)


if __name__ == "__main__":
    fig_register_map()
    fig_burst_read()
    fig_reassembly()
    print("done")
