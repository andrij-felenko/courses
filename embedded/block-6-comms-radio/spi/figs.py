# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 37 — «Шина SPI» (Модуль 6).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; висновок зелений;
стрілки через marker; шрифт sans-serif. Підписи посекційно (Рис. 37.S.N).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
METAL = "#9a9aa0"
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


def _wave(x0, y_hi, y_lo, unit, segs, color=INK, w=2.6):
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


def sreg(x, y, bits, cw=34, h=38, label="", col=INK):
    """Зсувний регістр: рядок бітових клітин."""
    s = ""
    for i, b in enumerate(bits):
        s += rect(x + i * cw, y, cw, h, ("#dfe7fb" if b == "1" else "#ffffff"),
                  (BLUE if b == "1" else GREY), 1.4)
        s += text(x + i * cw + cw / 2, y + h - 12, b, 12.5, (BLUE if b == "1" else GREY), "middle", "bold")
    if label:
        s += text(x + len(bits) * cw / 2, y - 8, label, 12, col, "middle", "bold")
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ============================================================================
#  §37.1 — SPI: швидка повнодуплексна шина
# ============================================================================

# ── Рис. 37.1.1 — чотири лінії й ролі ────────────────────────────────────────
def fig11_lines():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "SPI: чотири лінії між ведучим і веденим", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "такт SCK, дані «туди» MOSI, дані «звідти» MISO, вибір CS — кожна зі своєю роллю",
              12.5, GREY, "middle", style="italic")
    s += rect(90, 120, 180, 180, "#eef6ef", GREEN, 2.2, 12)
    s += text(180, 150, "ВЕДУЧИЙ", 14, GREEN, "middle", "bold")
    s += text(180, 170, "(master)", 10.5, GREY, "middle")
    s += rect(630, 120, 180, 180, "#fbfbfb", INK, 2.2, 12)
    s += text(720, 150, "ВЕДЕНИЙ", 14, INK, "middle", "bold")
    s += text(720, 170, "(slave)", 10.5, GREY, "middle")
    lines = [
        ("SCK", 200, BLUE, "такт (від ведучого)", "→"),
        ("MOSI", 232, RED, "Master Out, Slave In", "→"),
        ("MISO", 264, GREEN, "Master In, Slave Out", "←"),
        ("CS", 296, "#b08900", "вибір (активний 0)", "→"),
    ]
    for nm, y, col, desc, d in lines:
        s += text(255, y - 4, nm, 11.5, col, "end", "bold")
        s += text(645, y - 4, nm, 11.5, col, "start", "bold")
        if d == "→":
            s += arrow(270, y, 630, y, col, 2.2)
        else:
            s += arrow(630, y, 270, y, col, 2.2)
        s += text(450, y - 6, desc, 9.5, GREY, "middle")

    s += rect(60, 330, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 354, "Три спільні лінії (SCK, MOSI, MISO) — на всіх ведених; CS — окрема на КОЖНОГО веденого.",
              12, INK, "middle", "bold")
    s += text(W / 2, 374, "Жодних адрес: ведучий вибирає веденого, опускаючи саме його CS.",
              11.5, GREY, "middle", style="italic")
    save("fig-37-1-1-lines.svg", s)


# ── Рис. 37.1.2 — кільце зсувних регістрів ───────────────────────────────────
def fig12_shiftring():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Серце SPI: два зсувні регістри в кільці", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен такт SCK зсуває обидва на 1 біт: біт ведучого йде MOSI у веденого, біт веденого — MISO у ведучого",
              12, GREY, "middle", style="italic")
    s += sreg(130, 150, list("10100101"), 44, 44, "регістр ВЕДУЧОГО", GREEN)
    s += sreg(490, 150, list("00111100"), 44, 44, "регістр ВЕДЕНОГО", INK)
    # MOSI: вихід ведучого (правий край) → вхід веденого (лівий)
    s += arrow(130 + 8 * 44, 172, 490, 172, RED, 2.4)
    s += text((130 + 8 * 44 + 490) / 2, 162, "MOSI", 11, RED, "middle", "bold")
    # MISO: вихід веденого (правий) → назад у ведучого (петля знизу)
    s += line(490 + 8 * 44, 194, 490 + 8 * 44 + 20, 194, GREEN, 2.4)
    s += line(490 + 8 * 44 + 20, 194, 490 + 8 * 44 + 20, 250, GREEN, 2.4)
    s += line(490 + 8 * 44 + 20, 250, 110, 250, GREEN, 2.4)
    s += line(110, 250, 110, 194, GREEN, 2.4)
    s += arrow(110, 194, 130, 194, GREEN, 2.4)
    s += text(400, 264, "MISO (назад у ведучого)", 11, GREEN, "middle", "bold")
    # SCK
    s += text(W / 2, 300, "SCK цокає → обидва регістри зсуваються синхронно", 12.5, BLUE, "middle", "bold")

    s += rect(60, 330, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 354, "SPI — це, по суті, одне велике кільце з 16 біт, яке ведучий «прокручує» тактом.",
              12, INK, "middle", "bold")
    s += text(W / 2, 374, "Передача й прийом — той самий зсув, тому йдуть ОДНОЧАСНО (повний дуплекс).",
              11.5, GREY, "middle", style="italic")
    save("fig-37-1-2-shiftring.svg", s)


# ── Рис. 37.1.3 — після 8 тактів байти помінялися ────────────────────────────
def fig13_exchange():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Обмін байтом: після 8 тактів вони ПОМІНЯЛИСЯ місцями", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "ведучий «віддав» свій байт і водночас «отримав» байт веденого — за ту саму операцію",
              12.5, GREY, "middle", style="italic")
    # до
    s += text(180, 110, "до 8 тактів", 12.5, INK, "middle", "bold")
    s += sreg(90, 124, list("10100101"), 24, 30, "ведучий 0xA5", GREEN)
    s += sreg(330, 124, list("00111100"), 24, 30, "ведений 0x3C", INK)
    # стрілка
    s += arrow(W / 2 - 40, 200, W / 2 + 40, 200, GREEN, 3)
    s += text(W / 2, 192, "8 тактів SCK", 11.5, BLUE, "middle", "bold")
    # після
    s += text(180, 250, "після 8 тактів", 12.5, INK, "middle", "bold")
    s += sreg(90, 264, list("00111100"), 24, 30, "ведучий 0x3C", GREEN)
    s += sreg(330, 264, list("10100101"), 24, 30, "ведений 0xA5", INK)
    # пояснення праворуч
    s += rect(600, 120, 270, 200, "#fbfbfb", GREY, 1.4, 10)
    s += text(735, 146, "повний дуплекс", 13, GREEN, "middle", "bold")
    s += text(620, 176, "за одну операцію:", 11, INK, "start", "bold")
    s += text(620, 200, "• надіслав 0xA5 →", 11, RED, "start")
    s += text(620, 222, "• ← прийняв 0x3C", 11, GREEN, "start")
    s += text(620, 252, "якщо дані треба лише в", 10.5, GREY, "start")
    s += text(620, 270, "один бік — інший напрям", 10.5, GREY, "start")
    s += text(620, 288, "усе одно «крутиться»", 10.5, GREY, "start")
    s += text(620, 306, "(шлють пусте, ігнорують)", 10, GREY, "start", style="italic")
    save("fig-37-1-3-exchange.svg", s)


# ── Рис. 37.1.4 — вибір кристала замість адрес ───────────────────────────────
def fig14_cs():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Без адрес: вибір веденого окремою лінією CS", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ведучий опускає CS того, з ким говорить; решта — у високому імпедансі й мовчать",
              12.5, GREY, "middle", style="italic")
    s += rect(70, 130, 150, 170, "#eef6ef", GREEN, 2.2, 12)
    s += text(145, 158, "ВЕДУЧИЙ", 12.5, GREEN, "middle", "bold")
    # спільні лінії
    for nm, y, col in [("SCK", 330, BLUE), ("MOSI", 352, RED), ("MISO", 374, GREEN)]:
        s += line(220, y, 820, y, col, 2)
        s += text(60, y + 4, nm, 9.5, col, "end", "bold")
    devs = [("ведений A", 360, True), ("ведений B", 560, False), ("ведений C", 760, False)]
    for name, cx, sel in devs:
        col = GREEN if sel else GREY
        s += rect(cx - 70, 130, 140, 110, ("#eef6ef" if sel else "#f4f4f4"), col, 2, 10)
        s += text(cx, 162, name, 12, col, "middle", "bold")
        s += text(cx, 186, ("CS=0 → обраний" if sel else "CS=1 → мовчить"), 10.5, (GREEN if sel else GREY), "middle", "bold")
        s += text(cx, 206, ("активний" if sel else "MISO = Z"), 10, GREY, "middle")
    # CS лінії окремо
    s += text(145, 286, "CS_A CS_B CS_C", 9.5, "#b08900", "middle", "bold")
    s += arrow(170, 270, 360, 250, "#b08900", 1.6)
    s += arrow(180, 278, 560, 250, "#b08900", 1.4, dash="3,3")
    s += arrow(190, 286, 760, 250, "#b08900", 1.4, dash="3,3")

    s += rect(60, 322, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 346, "Замість адреси (як у I2C) — окрема ніжка CS на кожного веденого: просто й швидко.",
              12, INK, "middle", "bold")
    s += text(W / 2, 366, "Ціна: на N ведених треба N ліній CS — більше ніжок, ніж у I2C.",
              11.5, GREY, "middle", style="italic")
    save("fig-37-1-4-cs.svg", s)


# ── Рис. 37.1.5 — двотактний вихід → швидко ──────────────────────────────────
def fig15_pushpull():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому SPI швидкий: двотактні виходи, а не відкритий колектор", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "SPI активно жене лінію і вгору, і вниз → різкі фронти; I2C тягне вгору лише підтяжкою (повільно)",
              12.5, GREY, "middle", style="italic")
    # SPI — різкі
    s += text(160, 110, "SPI (push-pull)", 12.5, GREEN, "middle", "bold")
    s += _wave(80, 130, 180, 50, [(0, 0.5), (1, 1), (0, 1), (1, 1), (0, 0.5)], GREEN, 2.8)[0]
    s += text(160, 210, "різкі фронти ↑↓ → десятки МГц", 11, INK, "middle", "bold")
    # I2C — заокруглені вгору
    s += text(620, 110, "I2C (open-drain)", 12.5, "#b08900", "middle", "bold")
    x0, y_hi, y_lo, unit = 480, 130, 180, 50
    # ручний сигнал із RC-підйомами
    s += line(x0, y_lo, x0 + 0.5 * unit, y_lo, INK, 2.6)
    px = x0 + 0.5 * unit
    for lv in [1, 0, 1, 0]:
        if lv == 1:
            pts = []
            for i in range(0, 31):
                t = i / 30
                pts.append((px + t * unit, y_lo - (y_lo - y_hi) * (1 - math.exp(-3.2 * t))))
            s += '<path d="M ' + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.6"/>\n'
            px += unit
        else:
            s += line(px, y_hi, px + 1, y_lo, INK, 2.6)
            s += line(px + 1, y_lo, px + unit, y_lo, INK, 2.6)
            px += unit
    s += text(620, 210, "повільний RC-підйом → стеля швидкості", 11, INK, "middle", "bold")

    s += rect(60, 260, W - 120, 110, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 286, "Двотактний вихід заряджає лінію активно — фронт різкий, можна тактувати дуже швидко.",
              12, INK, "middle", "bold")
    s += text(W / 2, 310, "Тому SPI тягне десятки МГц проти 0.1…3.4 МГц у I2C.",
              12, INK, "middle", "bold")
    s += text(W / 2, 334, "Зворотний бік: двотактні виходи НЕ можна просто зводити разом — звідси окремі лінії й CS.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 356, "(саме та несумісність двотактних виходів, що ми бачили в §36.2)",
              10.5, GREY, "middle", style="italic")
    save("fig-37-1-5-pushpull.svg", s)


# ── Рис. 37.1.6 — мінімальний протокол → швидко ──────────────────────────────
def fig16_minimal():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Мінімум церемоній: ні адрес, ні ACK, ні старт-стопу", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у I2C байт обвішаний службовими бітами; у SPI — лише CS вниз, тактуй байти, CS вгору",
              12.5, GREY, "middle", style="italic")
    # I2C
    s += text(80, 110, "I2C:", 13, "#b08900", "start", "bold")
    items_i = [("S", BLUE), ("адр+W", BLUE), ("A", GREEN), ("дані", INK), ("A", GREEN), ("P", RED)]
    x = 140
    for lab, col in items_i:
        w = 70 if len(lab) > 2 else 44
        s += rect(x, 96, w, 34, "#f6f6f6", col, 1.4, 4)
        s += text(x + w / 2, 118, lab, 10.5, col, "middle", "bold")
        x += w + 4
    s += text(x + 16, 118, "← багато службового", 10.5, GREY, "start", style="italic")
    # SPI
    s += text(80, 180, "SPI:", 13, GREEN, "start", "bold")
    items_s = [("CS↓", "#b08900"), ("байт", INK), ("байт", INK), ("байт", INK), ("CS↑", "#b08900")]
    x = 140
    for lab, col in items_s:
        w = 64
        s += rect(x, 166, w, 34, "#eef6ef" if col == INK else "#fbf3df", col, 1.4, 4)
        s += text(x + w / 2, 188, lab, 10.5, col, "middle", "bold")
        x += w + 4
    s += text(x + 16, 188, "← самі дані, без обгортки", 10.5, GREEN, "start", "bold")

    s += rect(60, 236, W - 120, 100, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 262, "Немає адрес (є CS), немає підтвердження кожного байта, немає старт-стопу.", 12, INK, "middle", "bold")
    s += text(W / 2, 286, "Тому корисна частка майже 100%: 8 тактів = 8 біт даних, без 9-го такту ACK.", 12, INK, "middle", "bold")
    s += text(W / 2, 310, "Ціна простоти — жодного вбудованого контролю помилок (його, за потреби, додають зверху).",
              11.5, GREY, "middle", style="italic")
    save("fig-37-1-6-minimal.svg", s)


# ── Рис. 37.1.7 — характер SPI одним поглядом ────────────────────────────────
def fig17_character():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Характер SPI одним поглядом", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "за що його люблять — і чим за це платять",
              12.5, GREY, "middle", style="italic")
    s += rect(70, 90, 380, 200, LGRN, GREEN, 2, 12)
    s += text(260, 116, "сильні сторони", 13, GREEN, "middle", "bold")
    pros = ["швидко — десятки МГц", "повний дуплекс (туди й назад разом)", "простий протокол, мала затримка",
            "немає адрес і підтяжок"]
    for i, p in enumerate(pros):
        s += circle(96, 144 + i * 30, 4, GREEN, GREEN, 0)
        s += text(110, 148 + i * 30, p, 11.5, INK, "start")
    s += rect(470, 90, 380, 200, LRED, RED, 2, 12)
    s += text(660, 116, "ціна", 13, RED, "middle", "bold")
    cons = ["більше дротів (3 + CS на кожного)", "немає вбудованого ACK / контролю",
            "розрахований на КОРОТКІ відстані", "немає стандарту на формат пакета"]
    for i, c in enumerate(cons):
        s += circle(496, 144 + i * 30, 4, RED, RED, 0)
        s += text(510, 148 + i * 30, c, 11.5, INK, "start")

    s += rect(60, 306, W - 120, 40, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 331, "Коротко: SPI — про ШВИДКІСТЬ і простоту впритул; деталі ліній і режимів — у наступних темах.",
              12, INK, "middle", "bold")
    save("fig-37-1-7-character.svg", s)


# ============================================================================
#  §37.2 — Лінії: MOSI, MISO, SCK, CS (ролі)
# ============================================================================

# ── Рис. 37.2.1 — хто жене кожну лінію й коли ────────────────────────────────
def fig21_whodrives():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чотири лінії: хто жене кожну й коли", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "три лінії завжди від тих самих, а MISO «оживає» лише в обраного веденого",
              12.5, GREY, "middle", style="italic")
    bx, by, rw = 80, 96, 740
    cols = [("лінія", 16), ("напрям", 150), ("хто жене", 320), ("коли", 520)]
    s += rect(bx, by, rw, 34, "#f0f0f0", GREY, 1.3, 6)
    for c, dx in cols:
        s += text(bx + dx, by + 22, c, 11.5, INK, "start", "bold")
    rows = [
        ("SCK", "ведучий → ведений", "ведучий", "завжди (це він тактує)", BLUE),
        ("MOSI", "ведучий → ведений", "ведучий", "завжди", RED),
        ("MISO", "ведений → ведучий", "ведений", "ЛИШЕ коли його CS = 0", GREEN),
        ("CS", "ведучий → ведений", "ведучий", "опускає, щоб обрати", "#b08900"),
    ]
    yy = by + 34
    for nm, dirn, who, when, col in rows:
        s += rect(bx, yy, rw, 44, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 28, nm, 13, col, "start", "bold")
        s += text(bx + 150, yy + 28, dirn, 11, INK, "start")
        s += text(bx + 320, yy + 28, who, 11, INK, "start")
        s += text(bx + 520, yy + 28, when, 11, (GREEN if nm == "MISO" else GREY), "start", "bold" if nm == "MISO" else "normal")
        yy += 44

    s += rect(60, 320, W - 120, 44, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 346, "Ключ до спільної шини: необраний ведений ВІДПУСКАЄ MISO (високий імпеданс), щоб не заважати.",
              12, INK, "middle", "bold")
    save("fig-37-2-1-whodrives.svg", s)


# ── Рис. 37.2.2 — MISO у високому імпедансі ──────────────────────────────────
def fig22_miso_tristate():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Спільний MISO без конфлікту: необрані ведені «відключаються»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "лише обраний (CS=0) жене MISO; решта тримають вихід у високому імпедансі (Z) — наче від'єднані",
              12.5, GREY, "middle", style="italic")
    miso_y = 160
    s += line(120, miso_y, 820, miso_y, GREEN, 3)
    s += text(70, miso_y + 4, "MISO", 11.5, GREEN, "end", "bold")
    s += text(845, miso_y + 4, "→ ведучий", 10.5, GREY, "start")
    devs = [("ведений A", 250, True), ("ведений B", 470, False), ("ведений C", 690, False)]
    for name, cx, sel in devs:
        col = GREEN if sel else GREY
        s += rect(cx - 75, 220, 150, 100, ("#eef6ef" if sel else "#f4f4f4"), col, 2, 10)
        s += text(cx, 248, name, 12, col, "middle", "bold")
        s += text(cx, 272, ("CS = 0 (обраний)" if sel else "CS = 1"), 10.5, col, "middle", "bold")
        if sel:
            s += text(cx, 294, "жене MISO", 11, GREEN, "middle", "bold")
            s += line(cx, 220, cx, miso_y, GREEN, 2.4)
            s += circle(cx, miso_y, 4, GREEN, GREEN, 0)
        else:
            s += text(cx, 294, "вихід = Z (відпущено)", 10.5, GREY, "middle", "bold")
            s += line(cx, 232, cx, 220, GREY, 2, dash="3,3")
            s += text(cx, 210, "✗ Z", 11, RED, "middle", "bold")

    s += rect(60, 340, W - 120, 44, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 366, "Високий імпеданс — те, що дає багатьом веденим ділити один MISO: говорить лише обраний.",
              12, INK, "middle", "bold")
    save("fig-37-2-2-miso-tristate.svg", s)


# ── Рис. 37.2.3 — CS обрамляє транзакцію ─────────────────────────────────────
def fig23_cs_framing():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "CS обрамляє обмін: опустив — почав, підняв — завершив", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "роль, схожа на старт/стоп у I2C, але це фізична лінія, а не хитрий сигнал на даних",
              12.5, GREY, "middle", style="italic")
    x0, unit = 130, 60
    # CS низький протягом обміну
    s += text(x0 - 16, 130, "CS", 12, "#b08900", "end", "bold")
    s += _wave(x0, 112, 150, unit, [(1, 0.6), (0, 8.2), (1, 0.6)], "#b08900", 2.6)[0]
    # SCK 8 тактів усередині
    s += text(x0 - 16, 210, "SCK", 12, BLUE, "end", "bold")
    scl = [(0, 0.6)] + [(1, 0.5), (0, 0.5)] * 8 + [(0, 0.6)]
    s += _wave(x0, 192, 230, unit, scl, BLUE, 2.4)[0]
    # дужки
    s += line(x0 + 0.6 * unit, 100, x0 + 0.6 * unit, 240, GREEN, 1.2, dash="3,3")
    s += line(x0 + 8.8 * unit, 100, x0 + 8.8 * unit, 240, GREEN, 1.2, dash="3,3")
    s += text(x0 + 0.6 * unit, 92, "CS↓ старт", 10.5, GREEN, "middle", "bold")
    s += text(x0 + 8.8 * unit, 92, "CS↑ кінець", 10.5, GREEN, "middle", "bold")
    s += text(x0 + 4.7 * unit, 268, "поки CS = 0 — ведений активний, тактуються байти", 11.5, INK, "middle", "bold")

    s += rect(60, 300, W - 120, 44, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 326, "Підняти CS між байтами чи ні — залежить від чіпа: одні хочуть CS на весь обмін, інші — на кожне слово.",
              11.5, INK, "middle", "bold")
    save("fig-37-2-3-cs-framing.svg", s)


# ── Рис. 37.2.4 — повна часова діаграма обміну ───────────────────────────────
def fig24_waveform():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 34, "Повна картина в часі: CS, SCK, MOSI, MISO за один байт", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "ведучий жене MOSI, ведений — MISO, обидва біти знімають по фронту SCK — і так 8 разів",
              12.5, GREY, "middle", style="italic")
    x0, unit = 150, 78
    mosi = [1, 0, 1, 0, 0, 1, 0, 1]
    miso = [0, 0, 1, 1, 1, 1, 0, 0]
    # CS
    s += text(x0 - 16, 110, "CS", 11.5, "#b08900", "end", "bold")
    s += _wave(x0, 96, 124, unit, [(1, 0.4), (0, 8.2), (1, 0.4)], "#b08900", 2.2)[0]
    # SCK
    s += text(x0 - 16, 185, "SCK", 11.5, BLUE, "end", "bold")
    scl = [(0, 0.4)] + [(1, 0.5), (0, 0.5)] * 8 + [(0, 0.4)]
    bodyc, c = _wave(x0, 168, 200, unit, scl, BLUE, 2.2)
    s += bodyc
    # MOSI
    s += text(x0 - 16, 258, "MOSI", 11.5, RED, "end", "bold")
    s += _wave(x0 + 0.4 * unit, 240, 272, unit, [(b, 1.0) for b in mosi], RED, 2.4)[0]
    # MISO
    s += text(x0 - 16, 330, "MISO", 11.5, GREEN, "end", "bold")
    s += _wave(x0 + 0.4 * unit, 312, 344, unit, [(b, 1.0) for b in miso], GREEN, 2.4)[0]
    # точки вибірки на висхідних фронтах SCK
    for k in range(8):
        sx = x0 + 0.4 * unit + (k + 0.5) * unit
        s += line(sx, 168, sx, 344, GREY, 0.8, dash="2,3")
    s += text(x0 + 4.4 * unit, 372, "пунктир — моменти вибірки (тут по фронту SCK; який саме фронт — §37.3)",
              11, GREY, "middle", style="italic")

    s += rect(60, 392, W - 120, 36, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 415, "Усі чотири лінії разом і дають один обмін: вибрав (CS), протактував 8 біт у кожен бік.",
              11.5, INK, "middle", "bold")
    save("fig-37-2-4-waveform.svg", s)


# ── Рис. 37.2.5 — зоопарк назв ───────────────────────────────────────────────
def fig25_naming():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Зоопарк назв: ті самі лінії — різні позначення в даташитах", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "не дай збити себе з пантелику: дивись на РОЛЬ (хто жене, куди), а не лише на букви",
              12.5, GREY, "middle", style="italic")
    bx, by, rw = 90, 96, 720
    s += rect(bx, by, rw, 34, "#f0f0f0", GREY, 1.3, 6)
    heads = [("роль", 16), ("класично", 230), ("інклюзивно", 400), ("на чіпі-веденому", 560)]
    for h, dx in heads:
        s += text(bx + dx, by + 22, h, 11, INK, "start", "bold")
    rows = [
        ("дані до веденого", "MOSI", "COPI / SDO", "SDI / DIN", RED),
        ("дані від веденого", "MISO", "CIPO / SDI", "SDO / DOUT", GREEN),
        ("такт", "SCK / SCLK", "SCK", "SCK / CLK", BLUE),
        ("вибір", "CS / SS", "CS", "CS / nCS / SS", "#b08900"),
    ]
    yy = by + 34
    for role, cl, incl, slave, col in rows:
        s += rect(bx, yy, rw, 44, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 27, role, 11, INK, "start")
        s += text(bx + 230, yy + 27, cl, 12, col, "start", "bold")
        s += text(bx + 400, yy + 27, incl, 11.5, col, "start")
        s += text(bx + 560, yy + 27, slave, 11.5, GREY, "start")
        yy += 44

    s += rect(60, 320, W - 120, 36, LRED, RED, 1.3, 10)
    s += text(W / 2, 343, "Пастка: на ВЕДЕНОМУ чіпі SDO — це його ВИХІД, тобто MISO; SDI — його вхід, тобто MOSI. Дивись напрям!",
              11.5, INK, "middle", "bold")
    save("fig-37-2-5-naming.svg", s)


# ── Рис. 37.2.6 — CS робить більше, ніж вибір ────────────────────────────────
def fig26_cs_more():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "CS — це не лише «вибір»: він ще й обрамляє команду", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "багато чіпів за фронтом CS скидають внутрішній стан або «засувають» результат",
              12.5, GREY, "middle", style="italic")
    panels = [
        ("кадр команди", "CS↓ — початок нової команди;\nкоманда має вкластися, поки CS=0", BLUE),
        ("скидання стану", "CS↑ між словами скидає\nвнутрішній лічильник/автомат чіпа", "#b08900"),
        ("CS на кожне слово", "деякі АЦП хочуть CS-імпульс\nна КОЖЕН вимір (засувка)", GREEN),
    ]
    x = 60
    for title, body, col in panels:
        s += rect(x, 96, 270, 150, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 124, title, 12.5, col, "middle", "bold")
        for j, ln in enumerate(body.split("\n")):
            s += text(x + 135, 156 + j * 20, ln, 10.5, INK, "middle")
        x += 290

    s += rect(60, 266, W - 120, 80, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 292, "Тому CS не можна тримати завжди опущеним «про запас»: для багатьох чіпів важливі саме його ФРОНТИ.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 314, "Завжди звіряйся з даташитом: тримати CS на весь обмін чи смикати на кожне слово.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 334, "Неправильна робота з CS — другий за частотою (після режиму, §37.3) глюк SPI.",
              11, GREY, "middle", style="italic")
    save("fig-37-2-6-cs-more.svg", s)


# ── Рис. 37.2.7 — варіант на 3 дроти ─────────────────────────────────────────
def fig27_3wire():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Економний варіант: 3-дротовий SPI (одна лінія даних)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "MOSI і MISO зливають в одну двонапрямлену лінію — менше дротів, але вже напівдуплекс",
              12.5, GREY, "middle", style="italic")
    # 4-дротовий
    s += rect(70, 100, 360, 140, "none", FAINT, 2, 12)
    s += text(250, 124, "4-дротовий (звичайний)", 12.5, INK, "middle", "bold")
    for nm, y, col in [("SCK", 150, BLUE), ("MOSI", 174, RED), ("MISO", 198, GREEN), ("CS", 222, "#b08900")]:
        s += line(110, y, 390, y, col, 2)
        s += text(100, y + 4, nm, 9, col, "end", "bold")
    s += text(250, 236, "повний дуплекс, 4 лінії", 10.5, GREY, "middle")
    # 3-дротовий
    s += rect(470, 100, 360, 140, "none", FAINT, 2, 12)
    s += text(650, 124, "3-дротовий", 12.5, INK, "middle", "bold")
    for nm, y, col in [("SCK", 156, BLUE), ("SDIO", 186, "#7a2bd6"), ("CS", 216, "#b08900")]:
        s += line(510, y, 790, y, col, 2)
        s += text(500, y + 4, nm, 9, col, "end", "bold")
    s += text(650, 200, "↔ дані в обидва боки по черзі", 9.5, "#7a2bd6", "middle", "bold")
    s += text(650, 236, "напівдуплекс, 3 лінії", 10.5, GREY, "middle")

    s += rect(60, 262, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 286, "3-дротовий SPI економить ніжку там, де дані й так ідуть по черзі (багато дисплеїв, дрібні чіпи).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 306, "Це той самий компроміс «менше дротів ↔ менше одночасності», що й I2C проти SPI.",
              11, GREY, "middle", style="italic")
    save("fig-37-2-7-3wire.svg", s)


# ============================================================================
#  §37.3 — Режими CPOL/CPHA (4 режими; типова пастка)
# ============================================================================
def _clock(x0, y_hi, y_lo, unit, n, cpol, w=2.4):
    """n повних тактів. cpol=0 → спокій низько; cpol=1 → спокій високо."""
    segs = []
    for _ in range(n):
        if cpol == 0:
            segs += [(1, 0.5), (0, 0.5)]
        else:
            segs += [(0, 0.5), (1, 0.5)]
    # додати спокій з боків
    idle = cpol
    segs = [(idle, 0.3)] + segs + [(idle, 0.3)]
    return _wave(x0, y_hi, y_lo, unit, segs, BLUE, w)


# ── Рис. 37.3.1 — CPOL: рівень спокою такту ──────────────────────────────────
def fig31_cpol():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "CPOL — полярність такту: який рівень SCK у спокої", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "CPOL=0 — у спокої SCK низький; CPOL=1 — у спокої високий",
              12.5, GREY, "middle", style="italic")
    x0, unit = 200, 76
    s += text(x0 - 16, 130, "CPOL=0", 12.5, GREEN, "end", "bold")
    s += _clock(x0, 112, 152, unit, 4, 0)[0]
    s += text(x0 + 4 * unit + 30, 132, "спокій низько", 11, GREY, "start")
    s += text(x0 - 16, 230, "CPOL=1", 12.5, "#b08900", "end", "bold")
    s += _clock(x0, 212, 252, unit, 4, 1)[0]
    s += text(x0 + 4 * unit + 30, 232, "спокій високо", 11, GREY, "start")

    s += rect(60, 290, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 314, "CPOL лише «перевертає» такт. Сам по собі він нешкідливий — аби ведучий і ведений збіглися.",
              12, INK, "middle", "bold")
    s += text(W / 2, 334, "Разом із CPHA (далі) він задає, по якому ФІЗИЧНОМУ фронту знімають дані.",
              11.5, GREY, "middle", style="italic")
    save("fig-37-3-1-cpol.svg", s)


# ── Рис. 37.3.2 — CPHA: по якому фронту вибірка ──────────────────────────────
def fig32_cpha():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "CPHA — фаза: на якому фронті знімають біт", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "CPHA=0 — вибірка на ПЕРШОМУ фронті такту; CPHA=1 — на ДРУГОМУ (зсув на пів-біта)",
              12, GREY, "middle", style="italic")
    x0, unit = 170, 95
    bits = [1, 0, 1, 1]
    # CPHA=0 (вибірка на 1-му фронті)
    s += text(x0 - 14, 122, "SCK", 11, BLUE, "end", "bold")
    s += _clock(x0, 106, 136, unit, 4, 0)[0]
    s += text(x0 - 14, 180, "MOSI", 11, RED, "end", "bold")
    s += _wave(x0 + 0.3 * unit, 162, 192, unit, [(b, 1.0) for b in bits], RED, 2.2)[0]
    for k in range(4):
        sx = x0 + 0.3 * unit + k * unit
        s += line(sx, 106, sx, 200, GREEN, 1, dash="3,3")
        s += arrow(sx, 216, sx, 194, GREEN, 1.6)
    s += text(x0 + 2 * unit, 236, "CPHA=0: знімаємо на 1-му фронті біта (дані вже стоять)", 10.5, GREEN, "middle", "bold")
    # CPHA=1 (вибірка на 2-му фронті)
    s += text(x0 - 14, 296, "SCK", 11, BLUE, "end", "bold")
    s += _clock(x0, 280, 310, unit, 4, 0)[0]
    s += text(x0 - 14, 354, "MOSI", 11, RED, "end", "bold")
    s += _wave(x0 + 0.3 * unit, 336, 366, unit, [(b, 1.0) for b in bits], RED, 2.2)[0]
    for k in range(4):
        sx = x0 + 0.3 * unit + (k + 0.5) * unit
        s += line(sx, 280, sx, 374, "#b08900", 1, dash="3,3")
        s += arrow(sx, 390, sx, 368, "#b08900", 1.6)
    s += text(x0 + 2.1 * unit, 268, "CPHA=1: знімаємо на 2-му фронті (дані міняються на 1-му)", 10.5, "#b08900", "middle", "bold")
    save("fig-37-3-2-cpha.svg", s)


# ── Рис. 37.3.3 — чотири режими ──────────────────────────────────────────────
def fig33_fourmodes():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чотири режими SPI = (CPOL, CPHA)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "дві двійкові опції дають чотири комбінації; найпоширеніші — 0 і 3",
              12.5, GREY, "middle", style="italic")
    bx, by, rw = 110, 96, 680
    s += rect(bx, by, rw, 34, "#f0f0f0", GREY, 1.3, 6)
    heads = [("режим", 16), ("CPOL", 150), ("CPHA", 260), ("спокій SCK", 380), ("вибірка по фронту", 540)]
    for h, dx in heads:
        s += text(bx + dx, by + 22, h, 11, INK, "start", "bold")
    rows = [
        ("Mode 0", "0", "0", "низько", "передній (наростання)", GREEN),
        ("Mode 1", "0", "1", "низько", "задній (спадання)", INK),
        ("Mode 2", "1", "0", "високо", "передній (спадання)", INK),
        ("Mode 3", "1", "1", "високо", "задній (наростання)", GREEN),
    ]
    yy = by + 34
    for nm, cpol, cpha, idle, edge, col in rows:
        s += rect(bx, yy, rw, 42, ("#eef6ef" if col == GREEN else "#ffffff"), GREY, 1)
        s += text(bx + 16, yy + 26, nm, 12, col, "start", "bold")
        s += text(bx + 150, yy + 26, cpol, 12, INK, "start")
        s += text(bx + 260, yy + 26, cpha, 12, INK, "start")
        s += text(bx + 380, yy + 26, idle, 11, INK, "start")
        s += text(bx + 540, yy + 26, edge, 11, INK, "start")
        yy += 42

    s += rect(60, 312, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 336, "Найчастіше — Mode 0 (спокій низько, вибірка по наростанню). Mode 3 — теж дуже поширений.",
              12, INK, "middle", "bold")
    s += text(W / 2, 356, "Головне: ведучий і ведений мусять стояти на ОДНОМУ режимі.",
              11.5, GREY, "middle", style="italic")
    save("fig-37-3-3-fourmodes.svg", s)


# ── Рис. 37.3.4 — Mode 0 докладно ────────────────────────────────────────────
def fig34_mode0():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Mode 0 докладно: спокій низько, вибірка по наростанню", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "найпоширеніший режим: дані виставляють заздалегідь, знімають на передньому фронті SCK",
              12.5, GREY, "middle", style="italic")
    x0, unit = 170, 100
    bits = [1, 0, 0, 1, 1, 0]
    s += text(x0 - 16, 130, "SCK", 11.5, BLUE, "end", "bold")
    s += _clock(x0, 112, 146, unit, 6, 0)[0]
    s += text(x0 - 16, 200, "MOSI", 11.5, RED, "end", "bold")
    s += _wave(x0 + 0.3 * unit, 182, 216, unit, [(b, 1.0) for b in bits], RED, 2.4)[0]
    for k in range(6):
        sx = x0 + 0.3 * unit + k * unit  # передній фронт
        s += line(sx, 112, sx, 224, GREEN, 0.9, dash="3,3")
        s += arrow(sx, 244, sx, 218, GREEN, 1.5)
        s += text(sx, 260, str(bits[k]), 11, GREEN, "middle", "bold")
    s += text(x0 + 3 * unit, 286, "↑ зелене — наростання SCK = момент вибірки", 11, GREEN, "middle", "bold")

    s += rect(60, 306, W - 120, 44, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 332, "Дані стають дійсними ще до фронту (виставлені на спаді/при CS↓), а знімаються рівно на наростанні.",
              11.5, INK, "middle", "bold")
    save("fig-37-3-4-mode0.svg", s)


# ── Рис. 37.3.5 — пастка: різні режими → сміття ──────────────────────────────
def fig35_mismatch():
    W, H = 920, 390
    s = header(W, H)
    s += text(W / 2, 34, "Типова пастка: ведучий і ведений у РІЗНИХ режимах → сміття", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "дроти з'єднані правильно, а дані — нісенітниця: приймач знімає біт не в той момент",
              12.5, GREY, "middle", style="italic")
    x0, unit = 170, 100
    bits = [1, 0, 0, 1, 1, 0]
    s += text(x0 - 16, 128, "SCK", 11.5, BLUE, "end", "bold")
    s += _clock(x0, 110, 144, unit, 6, 0)[0]
    s += text(x0 - 16, 196, "MOSI", 11.5, RED, "end", "bold")
    s += _wave(x0 + 0.3 * unit, 178, 212, unit, [(b, 1.0) for b in bits], RED, 2.4)[0]
    # правильні точки (наростання) — зелені
    for k in range(6):
        sx = x0 + 0.3 * unit + k * unit
        s += arrow(sx, 234, sx, 214, GREEN, 1.5)
    s += text(x0 + 3 * unit, 250, "правильно (Mode 0): знімаємо на наростанні — чіткі біти", 10.5, GREEN, "middle", "bold")
    # неправильні точки (спадання) — червоні, на переходах
    for k in range(6):
        sx = x0 + 0.3 * unit + (k + 0.5) * unit
        s += line(sx, 110, sx, 290, RED, 0.8, dash="2,3")
        s += arrow(sx, 300, sx, 214, RED, 1.5)
    s += text(x0 + 3 * unit, 318, "неправильно (Mode 1): знімаємо на спаді — часто потрапляємо на ПЕРЕХІД даних", 10.5, RED, "middle", "bold")

    s += rect(60, 336, W - 120, 44, LRED, RED, 1.4, 10)
    s += text(W / 2, 362, "Якщо SPI «не той» режим — біти зсуваються або ловляться на переході: класичне «дроти ок, дані сміття».",
              11.5, INK, "middle", "bold")
    save("fig-37-3-5-mismatch.svg", s)


# ── Рис. 37.3.6 — як визначити режим із даташита ─────────────────────────────
def fig36_datasheet():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Як визначити режим із даташита (за часовою діаграмою)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "дивись дві речі: рівень SCK у спокої (→ CPOL) і на якому фронті стоїть стрілка вибірки (→ CPHA)",
              12, GREY, "middle", style="italic")
    x0, unit = 200, 110
    s += text(x0 - 16, 130, "SCK", 11.5, BLUE, "end", "bold")
    s += _clock(x0, 112, 146, unit, 3, 0)[0]
    # позначка 1: спокій
    s += circle(x0 + 6, 146, 7, "none", "#b08900", 2)
    s += text(x0 + 6, 172, "1", 12, "#b08900", "middle", "bold")
    s += arrow(x0 - 40, 188, x0 + 6, 150, "#b08900", 1.4)
    s += text(x0 - 200, 192, "спокій низько → CPOL=0", 11.5, "#b08900", "start", "bold")
    s += text(x0 - 16, 220, "дані", 11.5, RED, "end", "bold")
    s += _wave(x0 + 0.3 * unit, 202, 236, unit, [(1, 1), (0, 1), (1, 1)], RED, 2.4)[0]
    # позначка 2: стрілка вибірки на наростанні
    sx = x0 + 0.3 * unit
    s += arrow(sx, 270, sx, 238, GREEN, 1.8)
    s += circle(sx, 270, 7, "none", GREEN, 2)
    s += text(sx, 290, "2", 12, GREEN, "middle", "bold")
    s += text(sx + 130, 290, "вибірка на наростанні (1-й фронт) → CPHA=0", 11.5, GREEN, "start", "bold")

    s += rect(60, 308, W - 120, 44, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 334, "CPOL=0 + CPHA=0 = Mode 0. Будь-яку часову діаграму SPI читають саме цими двома поглядами.",
              12, INK, "middle", "bold")
    save("fig-37-3-6-datasheet.svg", s)


# ── Рис. 37.3.7 — задати режим у коді + порада ───────────────────────────────
def fig37_code():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Задати режим у коді — і порада з налагодження", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "режим виставляють разом зі швидкістю й порядком біт; режимів лише 4 — у крайньому разі перебери",
              12.5, GREY, "middle", style="italic")
    s += rect(80, 96, 470, 120, "#1e2330", "#111", 1.6, 8)
    s += text(100, 124, "// швидкість, порядок біт, режим", 11, "#7f9cc0", "start")
    s += text(100, 150, "SPISettings cfg(8000000, MSBFIRST, SPI_MODE0);", 12, "#9be39b", "start", "bold")
    s += text(100, 176, "SPI.beginTransaction(cfg);", 12, "#9be39b", "start")
    s += text(100, 198, "uint8_t r = SPI.transfer(0x9F);  // обмін", 12, "#9be39b", "start")
    # таблиця режимів
    s += rect(580, 96, 270, 120, "#fbfbfb", GREY, 1.4, 8)
    s += text(715, 120, "SPI_MODE0 = (0,0)", 11.5, GREEN, "middle", "bold")
    s += text(715, 142, "SPI_MODE1 = (0,1)", 11.5, INK, "middle")
    s += text(715, 164, "SPI_MODE2 = (1,0)", 11.5, INK, "middle")
    s += text(715, 186, "SPI_MODE3 = (1,1)", 11.5, GREEN, "middle", "bold")
    s += text(715, 206, "(CPOL, CPHA)", 10, GREY, "middle", style="italic")

    s += rect(60, 240, W - 120, 80, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 266, "Перша підозра, коли SPI віддає сміття: НЕ ТОЙ режим. Звір CPOL/CPHA із даташита веденого.",
              12, INK, "middle", "bold")
    s += text(W / 2, 290, "Режимів лише чотири — якщо немає часу читати, просто перебери MODE0…MODE3 і знайди робочий.",
              11.5, INK, "middle")
    s += text(W / 2, 310, "Те саме стосується й порядку біт (MSB чи LSB першим) — теж звіряй із даташитом.",
              11, GREY, "middle", style="italic")
    save("fig-37-3-7-code.svg", s)


# ============================================================================
#  §37.4 — Вибір кристала (CS) і кілька пристроїв
# ============================================================================

# ── Рис. 37.4.1 — зіркова топологія: окремий CS на кожного ───────────────────
def fig41_star():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Стандартна схема: спільні SCK/MOSI/MISO + окремий CS на кожного", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "три лінії спільні для всіх ведених, а ліній вибору CS — стільки, скільки пристроїв",
              12.5, GREY, "middle", style="italic")
    s += rect(70, 150, 150, 180, "#eef6ef", GREEN, 2.2, 12)
    s += text(145, 178, "ВЕДУЧИЙ", 12.5, GREEN, "middle", "bold")
    # спільні лінії
    for nm, y, col in [("SCK", 360, BLUE), ("MOSI", 380, RED), ("MISO", 400, GREEN)]:
        s += line(220, y, 820, y, col, 2)
        s += text(60, y + 4, nm, 9, col, "end", "bold")
    devs = [("ведений 0", 360, "#b08900"), ("ведений 1", 560, "#b08900"), ("ведений 2", 760, "#b08900")]
    for i, (name, cx, col) in enumerate(devs):
        s += rect(cx - 70, 150, 140, 120, "#fbfbfb", INK, 2, 10)
        s += text(cx, 178, name, 12, INK, "middle", "bold")
        # спільні лінії до пристрою
        for y, c in [(214, BLUE), (230, RED), (246, GREEN)]:
            s += line(cx, 270, cx, 360 if c == BLUE else (380 if c == RED else 400), c, 1.2)
        # окрема CS
        s += text(cx, 204, "CS%d" % i, 11, col, "middle", "bold")
    # CS лінії від ведучого
    s += text(145, 300, "CS0  CS1  CS2", 10, "#b08900", "middle", "bold")
    s += arrow(160, 290, 290, 204, "#b08900", 1.5)
    s += arrow(175, 296, 490, 204, "#b08900", 1.4, dash="3,3")
    s += arrow(190, 302, 690, 204, "#b08900", 1.4, dash="3,3")

    s += rect(60, 350, W - 120, 1, "none", "none", 0)
    s += text(W / 2, 372, "На N ведених треба 3 + N ніжок: три спільні лінії й по одній CS на кожного.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 392, "Ведучий вибирає, опускаючи рівно одну CS; решта ведених сплять.",
              11.5, GREY, "middle", style="italic")
    save("fig-37-4-1-star.svg", s)


# ── Рис. 37.4.2 — лише одна CS активна водночас ──────────────────────────────
def fig42_onecs():
    W, H = 900, 390
    s = header(W, H)
    s += text(W / 2, 34, "Правило: лише ОДНА CS активна водночас", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "опустити дві CS = два ведені женуть MISO разом = конфлікт (як двотактні виходи в §36.2)",
              12, GREY, "middle", style="italic")
    # правильно
    s += rect(70, 100, 360, 200, "none", FAINT, 2, 12)
    s += text(250, 126, "правильно: одна CS = 0", 12.5, GREEN, "middle", "bold")
    s += line(110, 200, 390, 200, GREEN, 2.4)
    s += text(250, 192, "MISO", 10, GREEN, "middle", "bold")
    for cx, sel in [(160, True), (250, False), (340, False)]:
        col = GREEN if sel else GREY
        s += rect(cx - 30, 220, 60, 50, ("#eef6ef" if sel else "#f4f4f4"), col, 1.6, 6)
        s += text(cx, 240, ("CS=0" if sel else "CS=1"), 9.5, col, "middle", "bold")
        s += text(cx, 256, ("жене" if sel else "Z"), 9, GREY, "middle")
        if sel:
            s += line(cx, 220, cx, 200, GREEN, 2.2)
    s += text(250, 290, "говорить рівно один", 10.5, GREEN, "middle", "bold")
    # неправильно
    s += rect(470, 100, 360, 200, "none", FAINT, 2, 12)
    s += text(650, 126, "помилка: дві CS = 0", 12.5, RED, "middle", "bold")
    s += line(510, 200, 790, 200, RED, 2.4)
    s += text(650, 192, "MISO", 10, RED, "middle", "bold")
    for cx, sel in [(560, True), (650, True), (740, False)]:
        col = RED if sel else GREY
        s += rect(cx - 30, 220, 60, 50, ("#fdeeee" if sel else "#f4f4f4"), col, 1.6, 6)
        s += text(cx, 240, ("CS=0" if sel else "CS=1"), 9.5, col, "middle", "bold")
        s += text(cx, 256, ("жене!" if sel else "Z"), 9, (RED if sel else GREY), "middle", "bold")
        if sel:
            s += line(cx, 220, cx, 200, RED, 2.2)
    s += text(650, 290, "⚡ двоє женуть MISO — конфлікт", 10.5, RED, "middle", "bold")

    s += rect(60, 322, W - 120, 44, LRED, RED, 1.4, 10)
    s += text(W / 2, 348, "Ведучий мусить тримати ВСІ CS високими й опускати рівно одну на час обміну.",
              12, INK, "middle", "bold")
    save("fig-37-4-2-onecs.svg", s)


# ── Рис. 37.4.3 — ціна в ніжках проти I2C ────────────────────────────────────
def fig43_pincost():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Ціна SPI — ніжки: 3 + N проти двох у I2C", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "що більше пристроїв, то відчутніша різниця: у SPI ніжки ростуть, у I2C — ні",
              12.5, GREY, "middle", style="italic")
    ox, oy, axw, axh = 130, 300, 640, 200
    s += line(ox, oy, ox + axw, oy, INK, 1.6)
    s += line(ox, oy, ox, oy - axh, INK, 1.6)
    s += text(ox + axw, oy + 20, "к-ть пристроїв N", 11, GREY, "end")
    s += text(ox - 8, oy - axh, "ніжки", 11, GREY, "end")
    ns = [1, 3, 5, 8, 10]
    # SPI = 3+N
    ptsS = [(ox + 40 + i * 120, oy - (3 + n) * 11) for i, n in enumerate(ns)]
    ptsI = [(ox + 40 + i * 120, oy - 2 * 11) for i, n in enumerate(ns)]
    s += '<path d="M ' + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ptsS) + f'" fill="none" stroke="{RED}" stroke-width="2.6"/>\n'
    s += '<path d="M ' + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ptsI) + f'" fill="none" stroke="{GREEN}" stroke-width="2.6"/>\n'
    for i, n in enumerate(ns):
        x = ox + 40 + i * 120
        s += text(x, oy + 18, str(n), 11, GREY, "middle")
        s += circle(ptsS[i][0], ptsS[i][1], 4, RED, RED, 0)
        s += text(ptsS[i][0], ptsS[i][1] - 10, str(3 + n), 10, RED, "middle", "bold")
    s += circle(ptsI[-1][0], ptsI[-1][1], 4, GREEN, GREEN, 0)
    s += text(ptsS[-1][0] + 10, ptsS[-1][1], "SPI = 3 + N", 11.5, RED, "start", "bold")
    s += text(ptsI[-1][0] + 10, ptsI[-1][1] + 4, "I2C = 2 (завжди)", 11.5, GREEN, "start", "bold")

    s += rect(60, 326, W - 120, 40, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 351, "5 SPI-ведених = 8 ніжок; ті самі 5 на I2C = 2 ніжки. Ось головний козир I2C при багатьох пристроях.",
              11.5, INK, "middle", "bold")
    save("fig-37-4-3-pincost.svg", s)


# ── Рис. 37.4.4 — ланцюжкове з'єднання (daisy-chain) ─────────────────────────
def fig44_daisy():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Ланцюжок (daisy-chain): один CS на всіх, дані течуть наскрізь", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ведені з'єднані послідовно, як одне довге кільце; економить CS, але треба «прокрутити» всіх",
              12.5, GREY, "middle", style="italic")
    s += rect(60, 150, 110, 90, "#eef6ef", GREEN, 2, 10)
    s += text(115, 182, "ВЕДУЧИЙ", 11, GREEN, "middle", "bold")
    chain = [("S0", 280), ("S1", 470), ("S2", 660)]
    prevx = 170
    for name, cx in chain:
        s += rect(cx - 55, 150, 110, 70, "#fbfbfb", INK, 2, 8)
        s += text(cx, 190, name, 12, INK, "middle", "bold")
        s += arrow(prevx, 175, cx - 55, 175, RED, 2)
        prevx = cx + 55
    s += arrow(prevx, 175, 830, 175, GREEN, 2)
    s += line(830, 175, 830, 270, GREEN, 2)
    s += line(830, 270, 115, 270, GREEN, 2)
    s += arrow(115, 270, 115, 240, GREEN, 2)
    s += text(115, 196, "MOSI→", 9, RED, "middle", "bold")
    s += text(470, 256, "MISO повертається в ведучого", 11, GREEN, "middle", "bold")
    s += text(470, 130, "SCK і ОДИН CS — спільні на всіх", 11.5, "#b08900", "middle", "bold")

    s += rect(60, 296, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 320, "Дані ведучого прошивають усі ведені поспіль — наче один довгий зсувний регістр.",
              12, INK, "middle", "bold")
    s += text(W / 2, 340, "Економить ніжки CS, та вимагає підтримки daisy-chain і надсилання даних ДЛЯ ВСІХ за раз (LED-драйвери, регістри).",
              10.5, GREY, "middle", style="italic")
    save("fig-37-4-4-daisy.svg", s)


# ── Рис. 37.4.5 — дешифратор розширює CS ─────────────────────────────────────
def fig45_decoder():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Бракує ніжок? Дешифратор робить багато CS з кількох ліній", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "3 лінії вибору → дешифратор 3-у-8 → 8 окремих CS (з них активна завжди одна)",
              12.5, GREY, "middle", style="italic")
    s += rect(90, 150, 130, 90, "#eef6ef", GREEN, 2, 10)
    s += text(155, 182, "ВЕДУЧИЙ", 11, GREEN, "middle", "bold")
    s += text(155, 204, "3 лінії", 10, GREY, "middle")
    s += arrow(220, 195, 320, 195, INK, 2.2)
    s += text(270, 184, "A B C", 10, INK, "middle", "bold")
    s += rect(320, 140, 130, 120, "#fbf3df", "#b08900", 2, 10)
    s += text(385, 184, "3→8", 16, "#b08900", "middle", "bold")
    s += text(385, 206, "дешифратор", 10, GREY, "middle")
    for i in range(8):
        yy = 150 + i * 14
        s += line(450, yy, 510, yy, "#b08900", 1.4)
        s += text(522, yy + 4, "CS%d" % i, 8.5, INK, "start")
    s += text(560, 200, "8 ведених", 12, INK, "start", "bold")

    s += rect(60, 290, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 314, "3 ніжки замість 8: дешифратор торгує трохи логіки за купу зекономлених CS.",
              12, INK, "middle", "bold")
    s += text(W / 2, 334, "Зворотний бік: не можна «не вибрати нікого» простим способом — потрібен ще один дозвільний біт.",
              11, GREY, "middle", style="italic")
    save("fig-37-4-5-decoder.svg", s)


# ── Рис. 37.4.6 — налаштування на кожного + патерн транзакції ─────────────────
def fig46_settings():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "У кожного веденого — свої налаштування й своя CS", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "різні ведені можуть хотіти різний режим і швидкість; обмін обрамляють своєю CS",
              12.5, GREY, "middle", style="italic")
    code = [
        "// дисплей: швидкий, режим 0",
        "SPISettings disp(20000000, MSBFIRST, SPI_MODE0);",
        "// АЦП: повільніший, режим 3",
        "SPISettings adc(1000000, MSBFIRST, SPI_MODE3);",
        "",
        "digitalWrite(CS_ADC, LOW);        // обрали АЦП",
        "SPI.beginTransaction(adc);",
        "v = SPI.transfer16(0x0000);       // обмін",
        "SPI.endTransaction();",
        "digitalWrite(CS_ADC, HIGH);       // відпустили",
    ]
    s += rect(110, 90, 700, 230, "#1e2330", "#111", 1.6, 10)
    yy = 116
    for ln in code:
        col = "#7f9cc0" if ln.strip().startswith("//") else "#9be39b"
        s += text(130, yy, ln, 12, col, "start", "bold" if not ln.strip().startswith("//") else "normal")
        yy += 21

    s += rect(60, 334, W - 120, 36, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 357, "Патерн: опусти CS → beginTransaction(свої налаштування) → обмін → endTransaction → підніми CS.",
              11.5, INK, "middle", "bold")
    save("fig-37-4-6-settings.svg", s)


# ── Рис. 37.4.7 — пастки з CS ────────────────────────────────────────────────
def fig47_pitfalls():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Часті пастки з лінією CS", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "більшість «непрацюючих» SPI-шин — саме через CS",
              12.5, GREY, "middle", style="italic")
    pits = [
        ("плаваюча CS", "ніжку лишили «у повітрі» —", "ведений ловить хибний вибір", RED, "тримай CS визначеною (HIGH)"),
        ("дві опущені CS", "обрали двох разом —", "конфлікт на MISO", "#b08900", "опускай рівно одну"),
        ("CS не піднято", "забули підняти між обмінами —", "наступна команда «злипається»", RED, "піднімай CS після кожного"),
    ]
    x = 60
    for title, l1, l2, col, fix in pits:
        s += rect(x, 92, 270, 170, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 120, title, 12.5, col, "middle", "bold")
        s += text(x + 135, 150, l1, 10.5, INK, "middle")
        s += text(x + 135, 170, l2, 10.5, INK, "middle", "bold")
        s += text(x + 135, 206, "→ " + fix, 10.5, GREEN, "middle", "bold")
        x += 290

    s += rect(60, 282, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 308, "Золоте правило: усі CS за замовчуванням високі; рівно одну опускаєш на час обміну й одразу піднімаєш.",
              11.5, INK, "middle", "bold")
    save("fig-37-4-7-pitfalls.svg", s)


# ============================================================================
#  §37.5 — Швидкість і відстань (чому SPI швидкий; близько)
# ============================================================================

# ── Рис. 37.5.1 — чотири причини швидкості ───────────────────────────────────
def fig51_whyfast():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Чому SPI швидкий: чотири причини разом", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожна окремо допомагає, а разом дають десятки мегагерц",
              12.5, GREY, "middle", style="italic")
    cards = [
        ("двотактний вихід", "активно жене вгору й вниз →\nрізкі фронти (не RC §36.2)", GREEN),
        ("такт у дроті", "не треба передискретизації\nй ресинхрону, як у UART", BLUE),
        ("мінімум протоколу", "ні адрес, ні ACK, ні старт-стопу →\n8 тактів = 8 біт", "#b08900"),
        ("окремі лінії", "MOSI й MISO роздільні →\nповний дуплекс без міжлінійного перекосу", RED),
    ]
    bw, gap, x0, y = 205, 18, 55, 110
    for i, (t, b, col) in enumerate(cards):
        x = x0 + i * (bw + gap)
        s += rect(x, y, bw, 150, "#fbfbfb", col, 2, 12)
        s += text(x + bw / 2, y + 30, t, 12.5, col, "middle", "bold")
        for j, ln in enumerate(b.split("\n")):
            s += text(x + bw / 2, y + 60 + j * 18, ln, 9.8, INK, "middle")
    s += rect(60, 290, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 315, "Підсумок: швидкі фронти + чесний такт + майже нуль накладних = найшвидша з простих шин.",
              12, INK, "middle", "bold")
    save("fig-37-5-1-whyfast.svg", s)


# ── Рис. 37.5.2 — діапазон швидкостей проти I2C/UART ─────────────────────────
def fig52_speedrange():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Діапазон швидкостей: SPI на порядок випереджає", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "логарифмічна шкала частоти такту/символів (приблизні типові межі)",
              12.5, GREY, "middle", style="italic")
    ox, oy, axw = 120, 250, 680
    s += line(ox, oy, ox + axw, oy, INK, 1.8)
    # шкала: 0.01..100 МГц лог
    marks = [(0.01, "10 к"), (0.1, "100 к"), (1, "1 М"), (10, "10 М"), (100, "100 М")]
    import math as _m
    def xof(f):
        return ox + axw * (_m.log10(f) - _m.log10(0.01)) / (_m.log10(100) - _m.log10(0.01))
    for f, lab in marks:
        x = xof(f)
        s += line(x, oy, x, oy + 6, INK, 1.4)
        s += text(x, oy + 22, lab, 10.5, GREY, "middle")
    bars = [("UART", 0.01, 0.5, INK, 110), ("I2C", 0.1, 3.4, "#b08900", 150), ("SPI", 1, 60, GREEN, 190)]
    for name, f0, f1, col, y in bars:
        s += rect(xof(f0), y, xof(f1) - xof(f0), 28, ("#eef6ef" if col == GREEN else "#f4f4f4"), col, 1.8, 5)
        s += text(xof(f0) - 10, y + 20, name, 12, col, "end", "bold")
        s += text((xof(f0) + xof(f1)) / 2, y + 19, "%g…%g МГц" % (f0, f1), 10, INK, "middle", "bold")

    s += rect(60, 282, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 308, "SPI тягне десятки МГц там, де I2C ледь дотягує до одиниць — але цю швидкість треба ще «довезти».",
              11.5, INK, "middle", "bold")
    save("fig-37-5-2-speedrange.svg", s)


# ── Рис. 37.5.3 — перекіс такт-дані на відстані ──────────────────────────────
def fig53_skew():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому близько: на відстані такт і дані «розповзаються»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "SCK і дані летять дротом із затримкою; що довший дріт і вищий темп, то гірше вони вирівняні",
              12.5, GREY, "middle", style="italic")
    # біля джерела — вирівняні
    s += text(160, 110, "біля ведучого: вирівняні", 12, GREEN, "middle", "bold")
    x0, unit = 70, 90
    s += text(x0 - 14, 145, "SCK", 10, BLUE, "end", "bold")
    s += _clock(x0, 130, 158, unit, 2, 0)[0]
    s += text(x0 - 14, 200, "дані", 10, RED, "end", "bold")
    s += _wave(x0 + 0.3 * unit, 184, 212, unit, [(1, 1), (0, 1)], RED, 2.2)[0]
    s += line(x0 + 0.3 * unit, 124, x0 + 0.3 * unit, 218, GREEN, 1, dash="3,3")
    s += text(x0 + 0.3 * unit, 234, "фронт = край біта ✓", 9.5, GREEN, "middle", "bold")
    # на кінці — зсунуті
    s += text(640, 110, "на дальньому кінці: зсунуті", 12, RED, "middle", "bold")
    x1 = 510
    s += text(x1 - 14, 145, "SCK", 10, BLUE, "end", "bold")
    s += _clock(x1, 130, 158, unit, 2, 0)[0]
    s += text(x1 - 14, 200, "дані", 10, RED, "end", "bold")
    s += _wave(x1 + 0.3 * unit + 26, 184, 212, unit, [(1, 1), (0, 1)], RED, 2.2)[0]   # дані спізнились
    s += line(x1 + 0.3 * unit, 124, x1 + 0.3 * unit, 218, RED, 1, dash="3,3")
    s += text(x1 + 0.3 * unit, 234, "фронт ловить ПЕРЕХІД ✗", 9.5, RED, "middle", "bold")
    s += arrow(x1 + 0.3 * unit, 250, x1 + 0.3 * unit + 26, 250, RED, 1.6)
    s += text(x1 + 0.3 * unit + 80, 254, "зсув даних", 9.5, RED, "start")

    s += rect(60, 290, W - 120, 80, LRED, RED, 1.4, 10)
    s += text(W / 2, 314, "Сигнал біжить ~15 см/нс по платі; при 50 МГц біт триває лише 20 нс.", 12, INK, "middle", "bold")
    s += text(W / 2, 336, "Уже кілька десятків сантиметрів зсувають фронт відносно даних — і вибірка влучає в перехід.",
              11.5, INK, "middle")
    s += text(W / 2, 356, "Тому високошвидкісний SPI — це сантиметри на платі, а не метри по кабелю.",
              11, GREY, "middle", style="italic")
    save("fig-37-5-3-skew.svg", s)


# ── Рис. 37.5.4 — ємнісне навантаження ───────────────────────────────────────
def fig54_loading():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Ємнісне навантаження теж тисне на швидкість", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "довгі доріжки й багато пристроїв додають ємність; навіть двотактний вихід заряджає її не миттєво",
              12.5, GREY, "middle", style="italic")
    # легке навантаження — різкий фронт
    s += text(230, 110, "мала ємність — фронт різкий", 12, GREEN, "middle", "bold")
    s += _wave(90, 130, 180, 70, [(0, 0.4), (1, 1.4)], GREEN, 2.8)[0]
    # велике — повільніший
    s += text(670, 110, "велика ємність — фронт «завалений»", 12, RED, "middle", "bold")
    x0, y_hi, y_lo, unit = 530, 130, 180, 70
    s += line(x0, y_lo, x0 + 0.4 * unit, y_lo, INK, 2.6)
    pts = []
    for i in range(0, 31):
        t = i / 30
        pts.append((x0 + 0.4 * unit + t * 1.4 * unit, y_lo - (y_lo - y_hi) * (1 - math.exp(-2.6 * t))))
    s += '<path d="M ' + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.8"/>\n'
    s += text(230, 210, "встигає за швидким тактом", 10.5, GREEN, "middle")
    s += text(670, 210, "не встигає → доводиться знизити SCK", 10.5, RED, "middle", "bold")

    s += rect(60, 250, W - 120, 80, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 276, "Кожен пристрій і кожен сантиметр доріжки додають ємність C; час фронту ~ R×C росте.",
              12, INK, "middle", "bold")
    s += text(W / 2, 298, "Тому навіть на платі max-швидкість падає з довжиною ліній і числом ведених на шині.",
              11.5, INK, "middle")
    s += text(W / 2, 318, "Практично: коротші доріжки й менше навантаження = вища доступна частота.",
              11, GREY, "middle", style="italic")
    save("fig-37-5-4-loading.svg", s)


# ── Рис. 37.5.5 — затримка туди-назад на MISO ────────────────────────────────
def fig55_roundtrip():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Затримка туди-назад: чому MISO «спізнюється»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "такт біжить до веденого, відповідь MISO — назад; на великій відстані вона приходить запізно",
              12.5, GREY, "middle", style="italic")
    s += rect(80, 130, 130, 90, "#eef6ef", GREEN, 2, 10)
    s += text(145, 170, "ВЕДУЧИЙ", 11, GREEN, "middle", "bold")
    s += rect(690, 130, 130, 90, "#fbfbfb", INK, 2, 10)
    s += text(755, 170, "ВЕДЕНИЙ", 11, INK, "middle", "bold")
    # SCK туди
    s += arrow(210, 150, 690, 150, BLUE, 2.2)
    s += text(450, 140, "1) фронт SCK летить туди (затримка t)", 10.5, BLUE, "middle", "bold")
    # MISO назад
    s += arrow(690, 190, 210, 190, GREEN, 2.2)
    s += text(450, 210, "2) ведений жене MISO, вона летить назад (ще t)", 10.5, GREEN, "middle", "bold")
    s += text(450, 246, "разом ≈ 2t затримки, перш ніж ведучий зможе зняти MISO", 11.5, INK, "middle", "bold")

    s += rect(60, 268, W - 120, 80, LRED, RED, 1.4, 10)
    s += text(W / 2, 292, "На високій частоті 2t стає сумірним із бітом — і MISO не встигає усталитися до вибірки.",
              12, INK, "middle", "bold")
    s += text(W / 2, 314, "Це окрема, ще жорсткіша межа на «швидко + далеко», ніж простий перекіс такт-дані.",
              11.5, INK, "middle")
    s += text(W / 2, 334, "Тому довгі лінії змушують або знижувати SCK, або зовсім відмовитися від SPI.",
              11, GREY, "middle", style="italic")
    save("fig-37-5-5-roundtrip.svg", s)


# ── Рис. 37.5.6 — однополюсність і відбиття ──────────────────────────────────
def fig56_singleended():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "SPI однополюсний і без узгодження → не для довгих ліній", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "сигнали міряються відносно спільної землі й нічим не «гасяться»; на довгому дроті — відбиття й завади",
              12.5, GREY, "middle", style="italic")
    # однополюсний з дзвоном
    s += text(250, 108, "однополюсний (SPI)", 12, "#b08900", "middle", "bold")
    x0, y_hi, y_lo, unit = 90, 130, 180, 60
    s += line(x0, y_lo, x0 + unit, y_lo, INK, 2.4)
    # фронт із дзвоном
    s += line(x0 + unit, y_lo, x0 + unit, y_hi, INK, 2.4)
    pts = []
    for i in range(0, 41):
        t = i / 40
        ring = math.exp(-4 * t) * math.sin(2 * math.pi * t * 3) * 12
        pts.append((x0 + unit + t * 2 * unit, y_hi - ring))
    s += '<path d="M ' + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts) + f'" fill="none" stroke="{INK}" stroke-width="2.4"/>\n'
    s += text(250, 210, "дзвін/відбиття від кінця дроту", 10.5, RED, "middle", "bold")
    s += text(250, 228, "+ ловить завади (нема чим гасити)", 10, GREY, "middle")
    # диференційний — стійкий
    s += text(670, 108, "диференційний (для метрів)", 12, GREEN, "middle", "bold")
    s += _wave(530, 130, 170, unit, [(0, 0.5), (1, 1), (0, 1), (1, 0.5)], GREEN, 2.4)[0]
    s += _wave(530, 150, 190, unit, [(1, 0.5), (0, 1), (1, 1), (0, 0.5)], BLUE, 2.0)[0]
    s += text(670, 222, "дві протифазні лінії: завада однакова на обох → гаситься", 9.5, GREEN, "middle", "bold")

    s += rect(60, 252, W - 120, 90, LGREY, GREY, 1.3, 10)
    s += text(W / 2, 278, "SPI — однополюсний і неузгоджений: чудово на короткій платі, погано на метрах кабелю.",
              12, INK, "middle", "bold")
    s += text(W / 2, 300, "Для довгих відстаней беруть диференційні шини (RS-485 тощо), де завада гаситься різницею.",
              11.5, INK, "middle")
    s += text(W / 2, 322, "Висновок: SPI житель ПЛАТИ — між сусідніми чіпами, а не між приладами через кабель.",
              11, GREY, "middle", style="italic")
    save("fig-37-5-6-singleended.svg", s)


# ── Рис. 37.5.7 — карта «швидкість × відстань» ───────────────────────────────
def fig57_map():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Карта «швидкість × відстань»: де живе SPI", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "можна мати ШВИДКО або ДАЛЕКО, але не одне й друге простими засобами",
              12.5, GREY, "middle", style="italic")
    ox, oy = 130, 320
    axw, axh = 660, 230
    s += arrow(ox, oy, ox + axw, oy, INK, 1.8)
    s += arrow(ox, oy, ox, oy - axh, INK, 1.8)
    s += text(ox + axw, oy + 22, "відстань →", 11.5, INK, "end")
    s += text(ox - 10, oy - axh - 4, "швидкість", 11.5, INK, "end")
    s += text(ox + 80, oy + 20, "см (плата)", 10, GREY, "middle")
    s += text(ox + axw - 120, oy + 20, "метри (кабель)", 10, GREY, "middle")
    # SPI зона — швидко+близько (верх-ліво)
    s += rect(ox + 6, oy - axh + 6, 260, 110, "#eef6ef", GREEN, 2, 10)
    s += text(ox + 136, oy - axh + 50, "SPI", 17, GREEN, "middle", "bold")
    s += text(ox + 136, oy - axh + 74, "швидко + близько", 11, INK, "middle", "bold")
    # I2C — повільно+близько (низ-ліво)
    s += rect(ox + 6, oy - 90, 260, 84, "#fbf3df", "#b08900", 1.8, 10)
    s += text(ox + 136, oy - 56, "I2C", 14, "#b08900", "middle", "bold")
    s += text(ox + 136, oy - 34, "повільно, теж близько", 10, INK, "middle")
    # диференційні — далеко (право)
    s += rect(ox + 300, oy - axh + 6, 340, 230 - 12, "#e9eefb", BLUE, 1.8, 10)
    s += text(ox + 470, oy - axh + 50, "диференційні шини", 13, BLUE, "middle", "bold")
    s += text(ox + 470, oy - axh + 74, "(RS-485, CAN, LVDS…)", 11, INK, "middle")
    s += text(ox + 470, oy - 80, "для метрів і завад", 11, INK, "middle", "bold")

    s += rect(60, 348, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 374, "Практика: SPI — десятки МГц на сантиметрах плати; на кабель чи метри бери диференційну шину.",
              11.5, INK, "middle", "bold")
    save("fig-37-5-7-map.svg", s)


# ============================================================================
#  §37.6 — SPI vs I2C: коли що (піни/швидкість/відстань)
# ============================================================================

# ── Рис. 37.6.1 — порівняльна таблиця ────────────────────────────────────────
def fig61_table():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "SPI проти I2C: по кожному критерію", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "зелене — де ця шина має перевагу; вибір — за тим, що для проєкту важливіше",
              12.5, GREY, "middle", style="italic")
    bx, by, rw = 90, 92, 720
    s += rect(bx, by, rw, 32, "#f0f0f0", GREY, 1.3, 6)
    s += text(bx + 16, by + 21, "критерій", 11.5, INK, "start", "bold")
    s += text(bx + 360, by + 21, "I2C", 12, "#b08900", "middle", "bold")
    s += text(bx + 560, by + 21, "SPI", 12, GREEN, "middle", "bold")
    rows = [
        ("ніжки", "2 на всіх", True, "3 + N", False),
        ("швидкість", "≤ 3.4 МГц", False, "десятки МГц", True),
        ("дуплекс", "напів", False, "повний", True),
        ("додати пристрій", "дати адресу", True, "ще лінія CS", False),
        ("контроль помилок", "є ACK", True, "немає", False),
        ("накладні витрати", "адреса+ACK", False, "майже нуль", True),
        ("кілька ведучих", "так (арбітраж)", True, "зазвичай ні", False),
        ("відстань", "коротко", None, "коротко", None),
    ]
    yy = by + 32
    for feat, iv, iwin, sv, swin in rows:
        s += rect(bx, yy, rw, 36, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 23, feat, 11, INK, "start", "bold")
        s += rect(bx + 250, yy + 3, 220, 30, "#eef6ef" if iwin else "#ffffff", "none", 0) if iwin else ""
        s += rect(bx + 470, yy + 3, 220, 30, "#eef6ef" if swin else "#ffffff", "none", 0) if swin else ""
        s += text(bx + 360, yy + 23, iv, 11, ("#1f8a3b" if iwin else INK), "middle", "bold" if iwin else "normal")
        s += text(bx + 560, yy + 23, sv, 11, ("#1f8a3b" if swin else INK), "middle", "bold" if swin else "normal")
        yy += 36

    s += rect(60, by + 32 + 8 * 36 + 8, W - 120, 1, "none", "none", 0)
    save("fig-37-6-1-table.svg", s)


# ── Рис. 37.6.2 — дерево рішень ──────────────────────────────────────────────
def fig62_flowchart():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Як обрати: коротке дерево рішень", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "три питання здебільшого вирішують усе",
              12.5, GREY, "middle", style="italic")
    def q(x, y, w, t, col=INK):
        out = rect(x, y, w, 50, "#fbfbfb", col, 2, 10)
        out += text(x + w / 2, y + 30, t, 11.5, col, "middle", "bold")
        return out
    def res(x, y, w, t, col):
        out = rect(x, y, w, 44, ("#eef6ef" if col == GREEN else "#fbf3df"), col, 2, 10)
        out += text(x + w / 2, y + 28, t, 13, col, "middle", "bold")
        return out
    s += q(330, 92, 240, "потрібна ВИСОКА швидкість / великий потік?")
    s += arrow(450, 142, 700, 170, GREEN, 1.8); s += text(600, 150, "так", 10.5, GREEN, "middle", "bold")
    s += res(640, 170, 130, "SPI", GREEN)
    s += arrow(420, 142, 300, 170, INK, 1.8); s += text(345, 150, "ні", 10.5, GREY, "middle", "bold")
    s += q(150, 170, 300, "багато дрібних пристроїв, мало ніжок?")
    s += arrow(180, 220, 120, 256, "#b08900", 1.8); s += text(135, 240, "так", 10, "#b08900", "middle", "bold")
    s += res(60, 256, 130, "I2C", "#b08900")
    s += arrow(360, 220, 430, 256, INK, 1.8); s += text(405, 240, "ні", 10, GREY, "middle", "bold")
    s += q(300, 256, 280, "потрібен дуплекс / нема ACK-контролю?")
    s += arrow(520, 306, 660, 320, GREEN, 1.8); s += text(600, 300, "дуплекс→", 9.5, GREEN, "middle", "bold")
    s += res(660, 306, 110, "SPI", GREEN)
    s += arrow(360, 306, 230, 320, "#b08900", 1.8); s += text(290, 300, "ACK→", 9.5, "#b08900", "middle", "bold")
    s += res(150, 306, 110, "I2C", "#b08900")

    s += rect(60, 356, W - 120, 1, "none", "none", 0)
    save("fig-37-6-2-flowchart.svg", s)


# ── Рис. 37.6.3 — типові пристрої на кожній шині ─────────────────────────────
def fig63_devices():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Що зазвичай вішають на кожну шину", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "не правило, а звичай: дрібне й повільне — на I2C; швидке й об'ємне — на SPI",
              12.5, GREY, "middle", style="italic")
    s += rect(70, 90, 360, 250, "#fbf3df", "#b08900", 2, 12)
    s += text(250, 118, "I2C — дрібні давачі", 13.5, "#b08900", "middle", "bold")
    i2c = ["IMU (гіро/акселерометр)", "барометр, давач світла", "годинник реального часу (RTC)",
           "невелика пам'ять EEPROM", "малий OLED-дисплей", "багато адрес — мало ніжок"]
    for i, t in enumerate(i2c):
        s += circle(96, 150 + i * 30, 4, "#b08900", "#b08900", 0)
        s += text(110, 154 + i * 30, t, 11.5, INK, "start")
    s += rect(470, 90, 360, 250, "#eef6ef", GREEN, 2, 12)
    s += text(650, 118, "SPI — швидке й об'ємне", 13.5, GREEN, "middle", "bold")
    spi = ["кольоровий TFT-дисплей", "SD-карта (файли)", "флеш-пам'ять", "швидкий АЦП/ЦАП",
           "деякі радіомодулі", "великі потоки на сантиметрах"]
    for i, t in enumerate(spi):
        s += circle(496, 150 + i * 30, 4, GREEN, GREEN, 0)
        s += text(510, 154 + i * 30, t, 11.5, INK, "start")

    s += rect(60, 350, W - 120, 1, "none", "none", 0)
    save("fig-37-6-3-devices.svg", s)


# ── Рис. 37.6.4 — обидві шини на одній платі ─────────────────────────────────
def fig64_coexist():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Часто на платі — ОБИДВІ шини одразу", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "повільні давачі на I2C, швидкий дисплей і пам'ять на SPI — і все від одного мікроконтролера",
              12.5, GREY, "middle", style="italic")
    s += rect(390, 130, 130, 110, "#eef6ef", GREEN, 2.2, 12)
    s += text(455, 175, "МК", 15, GREEN, "middle", "bold")
    # I2C ліворуч
    s += line(390, 165, 230, 165, "#b08900", 2.4)
    s += line(390, 185, 230, 185, "#b08900", 2.4)
    s += text(310, 156, "I2C (2 дроти)", 10.5, "#b08900", "middle", "bold")
    for i, nm in enumerate(["IMU", "баро", "RTC"]):
        s += rect(110, 130 + i * 38, 90, 30, "#fbf3df", "#b08900", 1.6, 6)
        s += text(155, 150 + i * 38, nm, 10.5, INK, "middle", "bold")
        s += line(200, 145 + i * 38, 230, 175, "#b08900", 1.2)
    # SPI праворуч
    for nm, y, col in [("SCK", 150, BLUE), ("MOSI", 168, RED), ("MISO", 186, GREEN)]:
        s += line(520, y, 690, y, col, 2)
    s += text(605, 140, "SPI (швидко)", 10.5, GREEN, "middle", "bold")
    for i, (nm, addr) in enumerate([("TFT", "CS0"), ("SD", "CS1")]):
        s += rect(700, 132 + i * 56, 110, 44, "#eef6ef", GREEN, 1.6, 6)
        s += text(755, 152 + i * 56, nm, 11.5, INK, "middle", "bold")
        s += text(755, 167 + i * 56, addr, 9, "#b08900", "middle")
        s += line(690, 168, 700, 154 + i * 56, "#b08900", 1.2)

    s += rect(60, 280, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 304, "Обидві шини чудово вживаються: кожна робить те, у чому сильна. Це норма, а не виняток.",
              12, INK, "middle", "bold")
    s += text(W / 2, 324, "I2C економить ніжки на гроні давачів; SPI везе швидкий потік на дисплей і картку.",
              11.5, GREY, "middle", style="italic")
    save("fig-37-6-4-coexist.svg", s)


# ── Рис. 37.6.5 — три дротові шини модуля разом ──────────────────────────────
def fig65_threebuses():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Три дротові шини модуля: кожна про своє", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "UART, I2C і SPI — не конкуренти, а інструменти під різні задачі",
              12.5, GREY, "middle", style="italic")
    cards = [
        ("UART (§35)", "точка-точка, асинхронно", ["2 лінії на лінк", "без спільного такту", "модуль ↔ ПК, GPS, радіомодем"], INK),
        ("I2C (§36)", "багато дрібних, 2 дроти", ["адреси на спільній шині", "повільно, ощадить ніжки", "давачі, RTC, пам'ять"], "#b08900"),
        ("SPI (§37)", "кілька швидких, на платі", ["окремі лінії + CS", "десятки МГц, повний дуплекс", "дисплей, SD, флеш, АЦП"], GREEN),
    ]
    bw, gap, x0, y = 280, 14, 25, 100
    for i, (t, sub, pts, col) in enumerate(cards):
        x = x0 + i * (bw + gap)
        s += rect(x, y, bw, 180, "#fbfbfb", col, 2.2, 12)
        s += text(x + bw / 2, y + 30, t, 14, col, "middle", "bold")
        s += text(x + bw / 2, y + 50, sub, 10.5, GREY, "middle", style="italic")
        for j, p in enumerate(pts):
            s += circle(x + 24, y + 80 + j * 28, 3.5, col, col, 0)
            s += text(x + 38, y + 84 + j * 28, p, 10.8, INK, "start")

    s += rect(60, 300, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 325, "Дротовий зв'язок модуля повний: вибрав шину під задачу — і знаєш її до фізики.",
              12, INK, "middle", "bold")
    save("fig-37-6-5-threebuses.svg", s)


# ── Рис. 37.6.6 — бюджет ніжок на прикладі ───────────────────────────────────
def fig66_pinbudget():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Бюджет ніжок на прикладі реального проєкту", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "3 давачі + дисплей + SD-картка: змішаний підхід економить найбільше",
              12.5, GREY, "middle", style="italic")
    bx, by = 110, 96
    s += rect(bx, by, 680, 200, "#fbfbfb", GREY, 1.4, 10)
    s += text(bx + 20, by + 30, "пристрої: IMU, баро, магнітометр (давачі) + TFT-дисплей + SD-картка", 12, INK, "start", "bold")
    lines = [
        ("усе на SPI:", "3 спільні + 5 CS = 8 ніжок", RED),
        ("усе на I2C:", "2 ніжки — але TFT і SD по I2C повільні/незручні ✗", RED),
        ("змішано (розумно):", "I2C: 3 давачі = 2 ніжки;  SPI: дисплей+SD = 3+2 = 5 ніжок", GREEN),
        ("разом змішано:", "2 + 5 = 7 ніжок — і кожен пристрій на «своїй» шині", GREEN),
    ]
    yy = by + 64
    for lab, val, col in lines:
        s += text(bx + 24, yy, lab, 12, col, "start", "bold")
        s += text(bx + 220, yy, val, 11.5, INK, "start")
        yy += 32

    s += rect(60, 312, W - 120, 44, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 338, "Висновок: не «або-або», а РОЗПОДІЛ — повільні давачі на I2C, швидке на SPI. Так найменше ніжок і клопоту.",
              11.5, INK, "middle", "bold")
    save("fig-37-6-6-pinbudget.svg", s)


# ── Рис. 37.6.7 — підсумкові «за замовчуванням» ──────────────────────────────
def fig67_summary():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Підсумок: типові «за замовчуванням»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "немає єдиного переможця — є правильний інструмент під кожен випадок",
              12.5, GREY, "middle", style="italic")
    rows = [
        ("дрібний давач, мало ніжок", "→ I2C", "#b08900"),
        ("швидкий дисплей / SD / флеш", "→ SPI", GREEN),
        ("зв'язок із модулем, ПК, GPS, радіо", "→ UART", INK),
        ("і давачі, і дисплей на одній платі", "→ I2C + SPI разом", GREEN),
        ("метри або кабель, завади", "→ ні те, ні те: диференційна шина", BLUE),
    ]
    yy = 100
    for case, pick, col in rows:
        s += text(150, yy, case, 12.5, INK, "start")
        s += text(620, yy, pick, 12.5, col, "start", "bold")
        yy += 34

    s += rect(60, 286, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 311, "Уміти зважити ніжки, швидкість, відстань і дуплекс — і є практичний підсумок усього розділу.",
              12, INK, "middle", "bold")
    save("fig-37-6-7-summary.svg", s)


if __name__ == "__main__":
    # — §37.1 —
    fig11_lines()
    fig12_shiftring()
    fig13_exchange()
    fig14_cs()
    fig15_pushpull()
    fig16_minimal()
    fig17_character()
    # — §37.2 —
    fig21_whodrives()
    fig22_miso_tristate()
    fig23_cs_framing()
    fig24_waveform()
    fig25_naming()
    fig26_cs_more()
    fig27_3wire()
    # — §37.3 —
    fig31_cpol()
    fig32_cpha()
    fig33_fourmodes()
    fig34_mode0()
    fig35_mismatch()
    fig36_datasheet()
    fig37_code()
    # — §37.4 —
    fig41_star()
    fig42_onecs()
    fig43_pincost()
    fig44_daisy()
    fig45_decoder()
    fig46_settings()
    fig47_pitfalls()
    # — §37.5 —
    fig51_whyfast()
    fig52_speedrange()
    fig53_skew()
    fig54_loading()
    fig55_roundtrip()
    fig56_singleended()
    fig57_map()
    # — §37.6 —
    fig61_table()
    fig62_flowchart()
    fig63_devices()
    fig64_coexist()
    fig65_threebuses()
    fig66_pinbudget()
    fig67_summary()
    print("done.")
