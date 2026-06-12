# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для ⚙️-вставки §3.7.5a — «Перші проєкти на Verilog:
мигалка й UART-передавач» (Розділ 3.7, Модуль 3). Чистий Python, без залежностей.
Вивід → ./img/. Головний figs.py розділу НЕ чіпаємо — це окремий скрипт вставки.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; «висновок/дійсне» зелене;
стрілки через marker; шрифт sans-serif. Підписи у книзі — «Рис. 3.7.5a.k».
Допоміжні функції — копія спільних (щоб вигляд був єдиний між розділами).
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
PALE  = "#f4f6fb"
PALEG = "#eef7f0"
PALER = "#fdeeec"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── гліфи ────────────────────────────────────────────────────────────────────
def dff(x, y, w=58, h=70, label="D", q="Q"):
    """Тригер як прямокутник із трикутником-входом такту (як у §3.3)."""
    out = rect(x, y, w, h, fill="#fff", stroke=INK, sw=2, rx=3)
    out += text(x + 9, y + 22, label, 14, INK, weight="bold")
    out += text(x + w - 9, y + 22, q, 14, INK, anchor="end", weight="bold")
    # клиновий вхід такту
    cy = y + h - 16
    out += polyline([(x, cy - 8), (x + 11, cy), (x, cy + 8)], INK, 2)
    return out


def chip(x, y, w, h, title, fill=PALE, stroke=INK, sw=2, tsize=15):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=7)
    out += text(x + w / 2, y + 20, title, tsize, INK, anchor="middle", weight="bold")
    return out


def codebox(x, y, w, lines, lh=18, size=13, pad=12, title=None):
    """Моноширинний «лістинг» з кольоровим підсвічуванням за тегами."""
    head = 22 if title else 0
    h = head + pad + lh * len(lines) + pad - 4
    out = rect(x, y, w, h, fill="#fbfbfd", stroke=GREY, sw=1.5, rx=6)
    if title:
        out += rect(x, y, w, head, fill="#eceef3", stroke=GREY, sw=1.5, rx=6)
        out += text(x + 10, y + 15, title, 12.5, INK, weight="bold")
    ty = y + head + pad + 10
    for ln in lines:
        if isinstance(ln, tuple):
            s, col = ln
        else:
            s, col = ln, INK
        out += text(x + 11, ty, s, size, col, mono=True)
        ty += lh
    return out, h


def led(cx, cy, r=14, on=True):
    col = RED if on else "#d9d9d9"
    glow = ""
    if on:
        glow = circle(cx, cy, r + 7, fill="none", stroke="#f3b0aa", w=3)
    out = glow + circle(cx, cy, r, fill=col, stroke=INK, w=2)
    out += line(cx - r - 8, cy, cx - r, cy, INK, 2)
    return out


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 3.7.5a.1 — той самий опис мигалки: текст HDL → синтезоване залізо
# «описуємо схему, а не пишемо програму»: реєстр-лічильник + компаратор + тригер LED
# ══════════════════════════════════════════════════════════════════════════════
def fig1_blinker():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 30, "Мигалка на Verilog: той самий опис — це ТЕКСТ і це СХЕМА",
              19, INK, anchor="middle", weight="bold")

    # ── ліворуч: текст HDL ──
    lx, ly, lw = 28, 58, 396
    code = [
        ("module blink(", BLUE),
        ("    input  clk,", INK),
        ("    output reg led);", INK),
        ("  reg [23:0] cnt = 0;", RED),
        ("", INK),
        ("  always @(posedge clk)", GREEN),
        ("  begin", INK),
        ("    cnt <= cnt + 1;", INK),
        ("    led <= cnt[23];", INK),
        ("  end", INK),
        ("endmodule", BLUE),
    ]
    box, bh = codebox(lx, ly, lw, code, lh=22, size=15,
                      title="blink.v   — що ми НАПИСАЛИ (опис)")
    s += box
    s += text(lx + 6, ly + bh + 24, "11 рядків тексту описують поведінку,",
              13.5, GREY)
    s += text(lx + 6, ly + bh + 42, "а не послідовність команд для виконання.",
              13.5, GREY)

    # ── стрілка «синтез» ──
    ax = lx + lw + 18
    s += arrow(ax, H / 2 - 16, ax + 66, H / 2 - 16, INK, 3)
    s += text(ax + 33, H / 2 - 26, "синтез", 14, INK, anchor="middle", weight="bold")
    s += text(ax + 33, H / 2 + 2, "(synthesis)", 11.5, GREY, anchor="middle")

    # ── праворуч: синтезоване залізо ──
    rx0 = ax + 78
    rw = W - rx0 - 22
    s += chip(rx0, 58, rw, 348, "що З ЦЬОГО ВИЙДЕ в кремнії (схема)", fill=PALEG, tsize=14)

    cy = 178
    # такт
    s += text(rx0 + 18, cy - 58, "clk", 14, INK, weight="bold")
    s += arrow(rx0 + 18, cy - 52, rx0 + 18, cy + 30, GREY, 2)
    s += line(rx0 + 18, cy + 30, rx0 + 360, cy + 30, GREY, 2, dash="3,4")

    # реєстр-лічильник 24 біти (як банк тригерів, §3.3.7)
    crx, crw = rx0 + 36, 150
    s += rect(crx, cy - 40, crw, 64, fill="#fff", stroke=INK, sw=2, rx=4)
    s += text(crx + crw / 2, cy - 20, "лічильник", 14, INK, anchor="middle", weight="bold")
    s += text(crx + crw / 2, cy - 2, "cnt[23:0]", 13.5, RED, anchor="middle", mono=True)
    s += text(crx + crw / 2, cy + 16, "24 тригери  (§3.3.7)", 11.5, GREY, anchor="middle")
    # такт у лічильник
    s += line(rx0 + 18, cy + 30, crx + crw / 2, cy + 30, GREY, 2)
    s += arrow(crx + crw / 2, cy + 30, crx + crw / 2, cy + 24, GREY, 2)
    # +1 сумарник (петля)
    s += circle(crx + crw + 30, cy - 8, 17, fill="#fff", stroke=INK, w=2)
    s += text(crx + crw + 30, cy - 3, "+1", 14, INK, anchor="middle", weight="bold")
    s += arrow(crx + crw, cy - 8, crx + crw + 13, cy - 8, INK, 2)
    s += polyline([(crx + crw + 30, cy - 25), (crx + crw + 30, cy - 56),
                   (crx + 12, cy - 56), (crx + 12, cy - 40)], INK, 2)
    s += arrow(crx + 12, cy - 44, crx + 12, cy - 40, INK, 2)
    s += text(crx + crw / 2, cy - 64, "cnt ← cnt + 1  щотакту", 11.5, GREY, anchor="middle")

    # відведення старшого біта → тригер LED
    tby = cy + 92
    s += text(crx + crw / 2, tby - 22, "беремо лише старший біт  cnt[23]", 12, INK, anchor="middle")
    s += arrow(crx + crw / 2, cy + 24, crx + crw / 2, tby - 8, RED, 2.4)
    s += text(crx + crw / 2 + 8, (cy + 24 + tby) / 2, "cnt[23]", 12, RED, mono=True)

    # тригер виходу led
    s += dff(crx + crw / 2 - 29, tby, 58, 58, "D", "Q")
    s += text(crx + crw / 2, tby + 74, "тригер led", 12, INK, anchor="middle")
    # такт у тригер led
    s += line(rx0 + 18, cy + 30, rx0 + 18, tby + 42, GREY, 2)
    s += arrow(rx0 + 18, tby + 42, crx + crw / 2 - 29, tby + 42, GREY, 2)

    # LED світиться
    lcx = crx + crw + 70
    s += arrow(crx + crw / 2 + 29, tby + 22, lcx - 26, tby + 22, GREEN, 2.4)
    s += led(lcx, tby + 22, 15, on=True)
    s += text(lcx, tby + 56, "блимає", 13, GREEN, anchor="middle", weight="bold")
    # частота
    s += text(rx0 + rw / 2, 392, "старший біт перемикається у 2²⁴ разів повільніше за clk → око бачить блимання",
              11.5, INK, anchor="middle")

    # підпис-висновок
    s += text(W / 2, H - 14,
              "Один опис — дві іпостасі: ліворуч його ЧИТАЄ людина, праворуч його ВИКОНУЄ кремній. Синтез перекладає перше у друге.",
              13, GREEN, anchor="middle", weight="bold")
    save("fig-3-7-5a-1-blinker.svg", s)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 3.7.5a.2 — блок-схема UART-передавача:
# дільник бода (§3.3.7) + автомат (§3.3.9) + зсувний реєстр (§3.3.5) → лінія TX
# ══════════════════════════════════════════════════════════════════════════════
def fig2_uart():
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 30, "UART-передавач: три знайомі блоки, з'єднані в один модуль",
              19, INK, anchor="middle", weight="bold")

    # вхідні сигнали зліва
    s += text(40, 96, "clk", 14, INK, weight="bold")
    s += text(40, 150, "start", 14, INK, weight="bold")
    s += text(40, 178, "data[7:0]", 13.5, INK, weight="bold", mono=True)
    s += arrow(95, 92, 150, 92, GREY, 2)
    s += arrow(110, 146, 250, 146, INK, 2)
    s += arrow(110, 178, 360, 178, RED, 2)

    # ── блок 1: дільник бода (лічильник, §3.3.7) ──
    b1x, b1y, b1w, b1h = 150, 70, 168, 96
    s += chip(b1x, b1y, b1w, b1h, "дільник бода", fill=PALE, tsize=14)
    s += text(b1x + b1w / 2, b1y + 44, "лічильник÷N", 13, INK, anchor="middle", mono=True)
    s += text(b1x + b1w / 2, b1y + 64, "§3.3.7", 11.5, GREY, anchor="middle")
    s += text(b1x + b1w / 2, b1y + 82, "f_clk → 115200", 11, GREY, anchor="middle")
    # такт «бод» вниз до автомата
    s += text(b1x + b1w / 2 + 6, b1y + b1h + 22, "tick (1 такт на біт)", 11.5, GREEN)
    s += arrow(b1x + b1w / 2, b1y + b1h, b1x + b1w / 2, 258, GREEN, 2.4)

    # ── блок 2: автомат (FSM, §3.3.9) ──
    b2x, b2y, b2w, b2h = 250, 258, 250, 150
    s += chip(b2x, b2y, b2w, b2h, "автомат стану (FSM)  §3.3.9", fill=PALEG, tsize=13.5)
    # стани в рядок
    st = ["IDLE", "START", "DATA×8", "STOP"]
    sx = b2x + 24
    for i, nm in enumerate(st):
        col = AMBER if nm == "DATA×8" else "#fff"
        s += rect(sx, b2y + 52, 48, 34, fill=col, stroke=INK, sw=1.8, rx=4)
        s += text(sx + 24, b2y + 74, nm, 11, INK, anchor="middle", weight="bold")
        if i < 3:
            s += arrow(sx + 48, b2y + 69, sx + 56, b2y + 69, INK, 1.8)
        sx += 56
    s += text(b2x + b2w / 2, b2y + 112, "лічить, які біти вже відправлено,", 11.5, GREY, anchor="middle")
    s += text(b2x + b2w / 2, b2y + 130, "і коли вантажити / зсувати реєстр", 11.5, GREY, anchor="middle")
    # start заводить автомат
    s += arrow(250, 146, b2x + 40, b2y, INK, 2)

    # ── блок 3: зсувний реєстр (§3.3.5) ──
    b3x, b3y, b3w, b3h = 560, 120, 330, 150
    s += chip(b3x, b3y, b3w, b3h, "зсувний реєстр  §3.3.5", fill=PALE, tsize=14)
    # 10 клітинок кадру: start(0) + 8 даних + stop(1)
    frame = [("0", BLUE), ("d0", INK), ("d1", INK), ("d2", INK), ("d3", INK),
             ("d4", INK), ("d5", INK), ("d6", INK), ("d7", INK), ("1", RED)]
    cw = (b3w - 36) / len(frame)
    fx = b3x + 18
    for i, (lab, col) in enumerate(frame):
        bg = "#fff"
        if i == 0:
            bg = "#e7edfb"
        if i == len(frame) - 1:
            bg = PALER
        s += rect(fx + i * cw, b3y + 52, cw - 3, 40, fill=bg, stroke=INK, sw=1.6, rx=3)
        s += text(fx + i * cw + cw / 2, b3y + 77, lab, 12, col, anchor="middle",
                  weight="bold", mono=True)
    s += text(b3x + 18 + cw / 2, b3y + 108, "старт", 10.5, BLUE, anchor="middle")
    s += text(fx + 9 * cw + cw / 2, b3y + 108, "стоп", 10.5, RED, anchor="middle")
    s += text(b3x + b3w / 2, b3y + 130, "кадр = старт-біт + 8 даних + стоп-біт (§3.4 — порядок молодшим уперед)",
              11, GREY, anchor="middle")
    # дані вантажаться в реєстр
    s += arrow(360, 178, b3x, b3y + 72, RED, 2)
    s += text((360 + b3x) / 2, b3y + 40, "load", 11.5, RED, anchor="middle", mono=True)
    # автомат керує реєстром (зсув/вантаж)
    s += arrow(b2x + b2w, b2y + 40, b3x + 60, b3y + b3h, GREEN, 2.2)
    s += text((b2x + b2w + b3x) / 2 + 10, b2y + 8, "shift / load", 11, GREEN, anchor="middle", mono=True)

    # ── вихід TX ──
    txy = b3y + 72
    s += arrow(b3x + b3w, txy, b3x + b3w + 28, txy, RED, 2.6)
    s += text(b3x + b3w + 40, txy - 8, "TX", 16, RED, weight="bold")
    s += text(b3x + b3w + 40, txy + 12, "(один дріт)", 11, GREY)

    # ── часова діаграма кадру внизу ──
    wy = 392
    wx0, wx1 = 250, 700
    s += text(wx0 - 6, wy - 14, "Лінія TX у часі (один байт = 10 бітів):", 13, INK, weight="bold")
    n = 10
    step = (wx1 - wx0) / n
    bits = [0, 1, 0, 1, 1, 0, 0, 1, 0, 1]  # старт=0, дані, стоп=1
    hi, lo = wy + 6, wy + 46
    pts = [(wx0, lo)]  # лінія в спокої = 1 (high) до старту; почнемо з idle high
    # idle high до старту
    s += line(wx0 - 40, hi, wx0, hi, GREY, 2.2)
    s += text(wx0 - 40, hi - 6, "спокій=1", 10.5, GREY)
    prev = hi
    px = wx0
    for i, b in enumerate(bits):
        yv = hi if b else lo
        s += line(px, prev, px, yv, RED, 2.2) if prev != yv else ""
        s += line(px, yv, px + step, yv, RED, 2.2)
        prev = yv
        px += step
    # idle high після стопу
    s += line(px, prev, px, hi, GREY, 2.2) if prev != hi else ""
    s += line(px, hi, px + 40, hi, GREY, 2.2)
    s += text(px + 4, hi - 6, "спокій=1", 10.5, GREY)
    # підписи бітів
    labs = ["старт", "d0", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "стоп"]
    for i, lab in enumerate(labs):
        col = BLUE if i == 0 else (RED if i == 9 else GREY)
        s += line(wx0 + i * step, hi - 4, wx0 + i * step, lo + 6, FAINT, 1)
        s += text(wx0 + i * step + step / 2, wy + 64, lab, 10.5, col, anchor="middle")

    s += text(W / 2, H - 12,
              "Жоден блок не новий: дільник — це §3.3.7, автомат — §3.3.9, зсувний реєстр — §3.3.5. Verilog лише ОПИСУЄ, як їх з'єднати.",
              13, GREEN, anchor="middle", weight="bold")
    save("fig-3-7-5a-2-uart.svg", s)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 3.7.5a.3 — тестбенч: симулятор крутить DUT БЕЗ заліза;
# стимул → модуль → хвилі; помилку видно до прошивання
# ══════════════════════════════════════════════════════════════════════════════
def fig3_testbench():
    W, H = 920, 460
    s = header(W, H)
    s += text(W / 2, 30, "Тестбенч: перевіряємо модуль у симуляторі — ще до прошивання плати",
              19, INK, anchor="middle", weight="bold")

    # рамка симулятора
    sx, sy, sw, sh = 28, 52, 600, 300
    s += rect(sx, sy, sw, sh, fill="#fafbff", stroke=BLUE, sw=2, rx=10)
    s += text(sx + 16, sy + 24, "СИМУЛЯТОР  (комп'ютер, не плата)", 14, BLUE, weight="bold")

    # стимул-блок (testbench)
    tx, ty, tw, th = sx + 24, sy + 48, 200, 96
    s += chip(tx, ty, tw, th, "тестбенч (stimulus)", fill=PALEG, tsize=13.5)
    tb = [
        "clk = ~clk #5;",
        "data = 8'h41;",
        "start = 1;",
        "#... перевір TX",
    ]
    yy = ty + 42
    for ln in tb:
        s += text(tx + 14, yy, ln, 12, INK, mono=True)
        yy += 17
    s += text(tx + tw / 2, ty + th + 16, "несправжній світ:", 11, GREY, anchor="middle")
    s += text(tx + tw / 2, ty + th + 31, "сам даєш такт і вхід", 11, GREY, anchor="middle")

    # DUT
    dx, dy, dw, dh = tx + tw + 70, ty, 190, 96
    s += chip(dx, dy, dw, dh, "DUT", fill=PALE, tsize=15)
    s += text(dx + dw / 2, dy + 44, "uart_tx.v", 13.5, INK, anchor="middle", mono=True)
    s += text(dx + dw / 2, dy + 64, "модуль, який", 11, GREY, anchor="middle")
    s += text(dx + dw / 2, dy + 79, "перевіряємо", 11, GREY, anchor="middle")
    s += text(dx + dw / 2, dy + dh + 16, "device under test", 11, GREY, anchor="middle")

    # стрілки стимул → DUT (clk, start, data)
    s += arrow(tx + tw, ty + 40, dx, dy + 40, GREEN, 2.2)
    s += text((tx + tw + dx) / 2, ty + 32, "clk, start, data", 11, GREEN, anchor="middle", mono=True)
    # DUT → хвилі (TX)
    s += arrow(dx + dw, dy + 56, dx + dw + 18, dy + 56, RED, 2.4)

    # хвильовий вивід (waveform) у симуляторі
    wx, wy, ww, wh = dx, dy + dh + 36, dw + 8, 70
    s += text(wx, wy - 6, "вихід TX — як хвиля:", 11.5, INK, weight="bold")
    hi, lo = wy + 10, wy + 44
    bits = [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1]  # idle,старт,дані...,стоп
    step = ww / (len(bits))
    px = wx
    prev = hi if bits[0] else lo
    s += line(px - 0, prev, px, prev, RED, 2)
    for b in bits:
        yv = hi if b else lo
        if yv != prev:
            s += line(px, prev, px, yv, RED, 2)
        s += line(px, yv, px + step, yv, RED, 2)
        prev = yv
        px += step

    # стрілка «синтез/прошивка» назовні
    fx = sx + sw + 30
    s += arrow(sx + sw, H / 2 - 8, fx + 40, H / 2 - 8, INK, 3)
    s += text(fx + 20, H / 2 - 20, "аж тепер", 13, INK, anchor="middle", weight="bold")
    s += text(fx + 20, H / 2 + 6, "прошивка", 12, GREY, anchor="middle")

    # плата (реальне залізо)
    px0, py0, pw, ph = fx + 64, 80, W - (fx + 64) - 22, 260
    s += rect(px0, py0, pw, ph, fill="#eef7f0", stroke=GREEN, sw=2, rx=10)
    s += text(px0 + pw / 2, py0 + 26, "ПЛАТА FPGA", 14, GREEN, anchor="middle", weight="bold")
    s += rect(px0 + pw / 2 - 34, py0 + 50, 68, 68, fill="#cfe9d6", stroke=INK, sw=2, rx=4)
    s += text(px0 + pw / 2, py0 + 88, "iCE40", 12, INK, anchor="middle", weight="bold")
    s += text(px0 + pw / 2, py0 + 138, "TX → у термінал", 11.5, INK, anchor="middle")
    s += led(px0 + pw / 2, py0 + 178, 13, on=True)
    s += text(px0 + pw / 2, py0 + 212, "працює як у хвилях", 11, GREEN, anchor="middle")

    s += text(W / 2, H - 12,
              "Помилку в кадрі видно на хвилях за секунди — а не паянням і осцилографом. Тестбенч — твій перший і найдешевший прилад.",
              13, GREEN, anchor="middle", weight="bold")
    save("fig-3-7-5a-3-testbench.svg", s)


if __name__ == "__main__":
    fig1_blinker()
    fig2_uart()
    fig3_testbench()
    print("done:", OUT)
