# -*- coding: utf-8 -*-
"""
Генератор SVG для 🧮-вставки §3.6.1m — «Розрядність адреси: 2ᴺ комірок і чому
32 біти бачать 4 ГіБ» (Модуль 3, Розділ 3.6, до теми 3.6.1).

Окремий скрипт вставки (головний figs.py розділу НЕ чіпаємо). Чистий Python,
без сторонніх залежностей. Вивід → ./img/ тієї самої папки розділу.
Імена файлів унікальні: fig-19-1m-*.svg (1m = вставка до теми 3.6.1).

Стиль (AUTHORING §9): білий фон; sans-serif; стрілки через marker; єдиний
вигляд із рештою розділу — допоміжні функції скопійовано з figs.py розділу.
Підписи у тексті — «Рис. 3.6.1m.k».
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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.1m.1 — драбина 2ᴺ: кожен біт адреси подвоює кількість комірок
# ════════════════════════════════════════════════════════════════════════════
def fig_ladder():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 34, "N бітів адреси → 2ᴺ комірок: кожен біт ПОДВОЮЄ простір", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ширина адреси задає стелю пам'яті; додав один біт — подвоїв кількість адресованих байтів",
              12, GREY, "middle", style="italic")

    # рядки драбини: (N, формула 2^N, людська назва, підсвітка)
    rows = [
        (8,  "2⁸",  "256 байтів", False),
        (10, "2¹⁰", "1 024 = 1 КіБ", False),
        (16, "2¹⁶", "65 536 = 64 КіБ", False),
        (20, "2²⁰", "1 048 576 = 1 МіБ", False),
        (24, "2²⁴", "16 МіБ", False),
        (32, "2³²", "4 294 967 296 = 4 ГіБ", True),
    ]
    x0 = 70
    colN = x0 + 60      # "N бітів"
    colF = x0 + 250     # "2^N"
    colV = x0 + 410     # значення
    top = 110
    dy = 66
    # заголовки стовпців
    s += text(colN, top - 26, "біти адреси (N)", 12.5, GREY, "middle", "bold")
    s += text(colF, top - 26, "комірок = 2ᴺ", 12.5, GREY, "middle", "bold")
    s += text(colV + 30, top - 26, "скільки це байтів", 12.5, GREY, "middle", "bold")

    for i, (n, f, v, hl) in enumerate(rows):
        y = top + i * dy
        col = RED if hl else INK
        # картка-біти: маленькі квадратики, що ростуть числом — образ «ще один біт»
        bx = x0
        cell = 13
        shown = min(n, 12)
        for b in range(shown):
            fillc = "#fbe6e4" if hl else FAINT
            s += rect(bx + b * (cell + 2), y - cell / 2 - 4, cell, cell, fillc, col if hl else GREY, 1.4)
        if n > shown:
            s += text(bx + shown * (cell + 2) + 4, y + 1, "…", 14, GREY, "start", "bold")
        s += text(colN, y + 5, f"{n} біт", 14.5, col, "middle", "bold")
        # 2^N
        s += text(colF, y + 5, f, 17, col, "middle", "bold")
        s += text(colV, y + 5, "=", 15, GREY, "start")
        s += text(colV + 22, y + 5, v, 15, col, "start", "bold" if hl else "normal")
        # стрілка «×2» між сусідніми відомими щаблями (8→10 пропускаємо у написі)
        if i > 0:
            pn = rows[i - 1][0]
            factor = 2 ** (n - pn)
            lab = f"×{factor:,}".replace(",", " ") if factor < 100000 else f"×2^{n-pn}"
            s += arrow(colF + 70, y - dy + 12, colF + 70, y - 12, GREEN, 1.6)
            s += text(colF + 80, y - dy / 2 + 4, f"+{n-pn} біт → {lab}", 11, GREEN, "start", style="italic")

    # нижній підсумок
    s += line(x0, top + len(rows) * dy - 30, W - 60, top + len(rows) * dy - 30, FAINT, 1.5)
    s += text(W / 2, H - 22, "правило: +1 біт адреси = ×2 простору; 8→16 біт це не «вдвічі», а ×256",
              13, RED, "middle", "bold")
    save("fig-19-1m-1-ladder.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.1m.2 — двійкові (1024) проти десяткових (1000) префіксів
# ════════════════════════════════════════════════════════════════════════════
def fig_prefixes():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 34, "Два «кіло»: десяткове (×1000) і двійкове (×1024)", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "пам'ять росте степенями двійки, тож має власні префікси — КіБ/МіБ/ГіБ (IEC); розрив із кіло/мега/гіга накопичується",
              11.5, GREY, "middle", style="italic")

    # дві колонки
    lx, rx = 235, 685
    s += rect(lx - 175, 80, 350, 250, "#f3f6fb", BLUE, 1.6, 10)
    s += rect(rx - 175, 80, 350, 250, "#fbf4f3", RED, 1.6, 10)
    s += text(lx, 106, "ДЕСЯТКОВІ (СІ): крок ×1000", 14.5, BLUE, "middle", "bold")
    s += text(lx, 124, "диски, швидкості, «маркетингові» байти", 11, GREY, "middle", style="italic")
    s += text(rx, 106, "ДВІЙКОВІ (IEC): крок ×1024", 14.5, RED, "middle", "bold")
    s += text(rx, 124, "адреси, RAM, розміри в пам'яті", 11, GREY, "middle", style="italic")

    dec = [
        ("кБ  (kB)", "10³", "= 1 000"),
        ("МБ  (MB)", "10⁶", "= 1 000 000"),
        ("ГБ  (GB)", "10⁹", "= 1 000 000 000"),
    ]
    binr = [
        ("КіБ (KiB)", "2¹⁰", "= 1 024"),
        ("МіБ (MiB)", "2²⁰", "= 1 048 576"),
        ("ГіБ (GiB)", "2³⁰", "= 1 073 741 824"),
    ]
    y0 = 158
    for i, (a, b, c) in enumerate(dec):
        y = y0 + i * 52
        s += text(lx - 160, y, a, 14, INK, "start", "bold")
        s += text(lx - 50, y, b, 15, BLUE, "start", "bold")
        s += text(lx - 15, y, c, 13, INK, "start")
    for i, (a, b, c) in enumerate(binr):
        y = y0 + i * 52
        s += text(rx - 160, y, a, 14, INK, "start", "bold")
        s += text(rx - 48, y, b, 15, RED, "start", "bold")
        s += text(rx - 12, y, c, 13, INK, "start")

    # смужка «розрив, що росте»
    gy = 380
    s += text(W / 2, gy - 18, "Розрив росте з кожним щаблем (двійкове більше за десяткове):", 13, INK, "middle", "bold")
    gaps = [("кіло", "+2.4 %"), ("мега", "+4.9 %"), ("гіга", "+7.4 %"), ("тера", "+10 %")]
    gx0 = 150
    bw = 150
    for i, (nm, g) in enumerate(gaps):
        x = gx0 + i * bw
        h = 18 + i * 16
        s += rect(x, gy + 50 - h, 70, h, "#fde9c8", AMBER, 1.4)
        s += text(x + 35, gy + 66, nm, 12, INK, "middle", "bold")
        s += text(x + 35, gy + 50 - h - 6, g, 12.5, RED, "middle", "bold")
    s += text(W / 2, H - 16, "тому «250 ГБ» диск показується системою як ≈ 232 ГіБ — байти ті самі, лінійка інша",
              12.5, GREY, "middle", style="italic")
    save("fig-19-1m-2-prefixes.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.6.1m.3 — головний підсумок: 2³² = 4 ГіБ (4 294 967 296 байтів)
# ════════════════════════════════════════════════════════════════════════════
def fig_fourgig():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому 32-бітна адреса бачить рівно 4 ГіБ", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "розклад степеня: 2³² = 2² · 2³⁰ = 4 × (1 ГіБ) — звідси «магічне» число 4",
              12, GREY, "middle", style="italic")

    # центральне рівняння у плитці
    bx, by, bw2, bh2 = 110, 92, 700, 92
    s += rect(bx, by, bw2, bh2, "#f3f6fb", BLUE, 2, 12)
    cy = by + 40
    s += text(bx + 28, cy, "2³²", 30, BLUE, "start", "bold")
    s += text(bx + 95, cy, "=", 24, GREY, "start")
    s += text(bx + 130, cy, "2²", 24, INK, "start", "bold")
    s += text(bx + 168, cy, "·", 22, GREY, "start")
    s += text(bx + 185, cy, "2³⁰", 24, RED, "start", "bold")
    s += text(bx + 250, cy, "=", 24, GREY, "start")
    s += text(bx + 285, cy, "4", 26, INK, "start", "bold")
    s += text(bx + 312, cy, "×", 20, GREY, "start")
    s += text(bx + 338, cy, "1 ГіБ", 24, RED, "start", "bold")
    s += text(bx + 470, cy, "=", 24, GREY, "start")
    s += text(bx + 505, cy, "4 ГіБ", 28, GREEN, "start", "bold")
    # підписи під множниками
    s += text(bx + 150, cy + 26, "= 4", 12, INK, "start", style="italic")
    s += text(bx + 200, cy + 26, "= 1 073 741 824 Б", 12, RED, "start", style="italic")

    # рядок точного числа байтів
    s += text(W / 2, 232, "точно в байтах:", 14, INK, "middle", "bold")
    s += rect(230, 246, 460, 44, "#fbf4f3", RED, 1.6, 8)
    s += text(W / 2, 274, "2³² = 4 294 967 296 байтів", 21, RED, "middle", "bold")

    # три ремарки-висновки
    notes = [
        ("Стеля, не обіцянка", "32 біти АДРЕСУЮТЬ 4 ГіБ — це максимум; скільки RAM реально стоїть, окреме питання"),
        ("Звідси перехід на 64 біти", "4 ГіБ стали тісними для ПК → 2⁶⁴ це 16 ЕіБ, межа зникла на десятиліття"),
        ("На МК межа геть інша", "адреса там широка, та фізичної SRAM лиш кілобайти — стелю ставить залізо, не біти"),
    ]
    ny = 322
    cwd = (W - 80) / 3
    for i, (h, body) in enumerate(notes):
        x = 40 + i * cwd
        s += rect(x, ny, cwd - 20, 110, "#fcfcfc", FAINT, 1.4, 8)
        s += text(x + 16, ny + 26, h, 13.5, INK, "start", "bold")
        # перенос тексту вручну
        words = body.split()
        ln, cur, yy = [], "", ny + 50
        for w in words:
            if len(cur) + len(w) + 1 <= 34:
                cur = (cur + " " + w).strip()
            else:
                ln.append(cur); cur = w
        if cur:
            ln.append(cur)
        for j, t in enumerate(ln[:4]):
            s += text(x + 16, yy + j * 18, t, 11.5, INK, "start")
    save("fig-19-1m-3-fourgig.svg", s)


if __name__ == "__main__":
    fig_ladder()
    fig_prefixes()
    fig_fourgig()
    print("ch19 §3.6.1m insert figures done.")
