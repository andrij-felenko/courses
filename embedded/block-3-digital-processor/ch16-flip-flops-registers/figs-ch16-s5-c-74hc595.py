# -*- coding: utf-8 -*-
"""
SVG-фігури для 🔌-вставки §3.3.5c — «74HC595: три ніжки → вісім виходів».
Окремий генератор (головний figs.py не чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1» червоний, «0» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.
Імена SVG унікальні (префікс fig-16-5c595-…), щоб не зіткнутися з 74HC165.

Фігури:
  fig-16-5c595-1-concept.svg   — три лінії МК → зсувний регістр + латч → 8 виходів (LED)
  fig-16-5c595-2-wiring.svg    — розпіновка DIP-16, 3 лінії, OE/SRCLR, каскад Q7'→SER
  fig-16-5c595-3-firstbyte.svg — «перший байт»: 8 фронтів SRCLK, потім один RCLK-засув
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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: світлодіод зі станом (горить/згас) ────────────────────────────
def led(cx, cy, on, label):
    """Схематичний світлодіод: коло + підпис стану під ним."""
    fill = "#ffe6e3" if on else "#eef1f7"
    edge = RED if on else GREY
    out = circle(cx, cy, 12, fill, edge, 2)
    # промінчики, якщо горить
    if on:
        for dx, dy in ((0, -1), (0.9, -0.5), (-0.9, -0.5)):
            out += line(cx + dx * 16, cy + dy * 16, cx + dx * 22, cy + dy * 22, RED, 2)
        out += text(cx, cy + 30, "1", 14, RED, "middle", "bold")
    else:
        out += text(cx, cy + 30, "0", 14, BLUE, "middle", "bold")
    out += text(cx, cy - 18, label, 11, GREY, "middle")
    return out


# ── Фігура 1: концепція SIPO — 3 лінії → зсувний регістр + латч → 8 виходів ───
def fig1_concept():
    W, H = 780, 480
    b = header(W, H)
    b += text(W/2, 30, "74HC595: три лінії від МК — вісім незалежних виходів",
              17, INK, "middle", "bold")

    # МК зліва, три керівні лінії
    mx, my, mw, mh = 36, 150, 104, 150
    b += rect(mx, my, mw, mh, "#eef7ee", GREEN, 2, 8)
    b += text(mx + mw/2, my + 26, "МК", 16, GREEN, "middle", "bold")
    b += text(mx + mw/2, my + 46, "(3 ніжки)", 11, GREY, "middle")
    b += text(mx + mw/2, my + 74, "SER  →", 12, INK, "middle")
    b += text(mx + mw/2, my + 98, "SRCLK →", 12, INK, "middle")
    b += text(mx + mw/2, my + 122, "RCLK →", 12, INK, "middle")

    # три стрілки до корпусу
    rx, ry, rw, rh = 250, 120, 250, 210
    b += arrow(mx + mw, my + 70, rx, ry + 40, INK, 2)
    b += arrow(mx + mw, my + 94, rx, ry + 95, INK, 2)
    b += arrow(mx + mw, my + 118, rx, ry + 150, GREEN, 2.2)
    b += text((mx + mw + rx) / 2 + 6, ry + 30, "дані", 10, GREY, "middle")
    b += text((mx + mw + rx) / 2 + 6, ry + 88, "такт зсуву", 10, GREY, "middle")
    b += text((mx + mw + rx) / 2 + 2, ry + 168, "засув (latch)", 10, GREEN, "middle")

    # корпус: два яруси — зсувний регістр (верх) і вихідний латч (низ)
    b += rect(rx, ry, rw, rh, "#fbfbff", BLUE, 2, 10)
    b += text(rx + rw/2, ry - 8, "74HC595 усередині", 13, BLUE, "middle", style="italic")

    bits = [1, 0, 1, 1, 0, 0, 1, 0]                 # приклад: 0b10110010
    cell_x0 = rx + 18
    cell_dx = (rw - 36) / 8

    # верхній ярус — зсувний регістр (8 тригерів), сюди «затікають» біти
    sy = ry + 22
    b += text(rx + rw/2, sy - 4, "зсувний регістр (засуваємо біти по черзі)", 10, GREY, "middle")
    for i, v in enumerate(bits):
        cx = cell_x0 + i * cell_dx + cell_dx/2
        col = RED if v else BLUE
        b += rect(cx - 13, sy + 6, 26, 34, "#fff", col, 1.8, 5)
        b += text(cx, sy + 30, str(v), 16, col, "middle", "bold")

    # стрілки-«засув» зверху вниз: зсувний регістр → латч
    ly = ry + 120
    for i, v in enumerate(bits):
        cx = cell_x0 + i * cell_dx + cell_dx/2
        b += arrow(cx, sy + 42, cx, ly + 4, GREEN, 1.4)
    b += text(rx + rw + 6, (sy + 42 + ly) / 2, "RCLK", 10, GREEN, "start", "bold")
    b += text(rx + rw + 6, (sy + 42 + ly) / 2 + 14, "копіює", 9, GREEN, "start")

    # нижній ярус — вихідний латч (фіксує показ)
    b += text(rx + rw/2, ly - 2, "вихідний латч (показує — не мерехтить під час засування)",
              10, GREY, "middle")
    for i, v in enumerate(bits):
        cx = cell_x0 + i * cell_dx + cell_dx/2
        col = RED if v else BLUE
        b += rect(cx - 13, ly + 6, 26, 34, "#fff", col, 1.8, 5)
        b += text(cx, ly + 30, str(v), 16, col, "middle", "bold")

    # вісім виходів вниз до світлодіодів
    qy = 420
    names = ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
    for i, v in enumerate(bits):
        cx = cell_x0 + i * cell_dx + cell_dx/2
        col = RED if v else BLUE
        b += arrow(cx, ly + 42, cx, qy - 14, col, 1.8)
        b += led(cx, qy, v, names[i])

    # підсумок
    b += text(W/2, 462, "3 ніжки МК → 8 виходів водночас (а каскад — 16, 24, 32…)",
              13, GREEN, "middle", "bold")
    save("fig-16-5c595-1-concept.svg", b)


# ── Фігура 2: розпіновка DIP-16 і підключення (+ OE/SRCLR, каскад) ───────────
def fig2_wiring():
    W, H = 790, 530
    b = header(W, H)
    b += text(W/2, 30, "Розпіновка (DIP-16) і три лінії від МК (+ OE, SRCLR, каскад)",
              16, INK, "middle", "bold")

    cx, cy, cw, ch = 280, 78, 140, 372
    b += rect(cx, cy, cw, ch, "#fbfbfb", INK, 2, 8)
    b += circle(cx + cw/2, cy + 14, 7, "#fff", INK, 1.6)          # ключ-виїмка
    b += text(cx + cw/2, cy + 40, "74HC595", 15, INK, "middle", "bold")
    b += text(cx + cw/2, cy + 58, "8-біт SIPO", 11, GREY, "middle")

    # ніжки за даташитом 595 (ліва 1..8 згори вниз, права 16..9)
    left  = [("Q1", "вихід"), ("Q2", "вихід"), ("Q3", "вихід"), ("Q4", "вихід"),
             ("Q5", "вихід"), ("Q6", "вихід"), ("Q7", "вихід"), ("GND", "земля")]
    right = [("VCC", "живлення"), ("Q0", "вихід"), ("SER", "дані"), ("OE", "дозвіл вих."),
             ("RCLK", "засув"), ("SRCLK", "такт"), ("SRCLR", "скид"), ("Q7'", "каскад")]

    n = 8
    pitch = (ch - 44) / (n - 1)
    py0 = cy + 32
    for i, (nm, role) in enumerate(left):
        y = py0 + i * pitch
        b += line(cx - 26, y, cx, y, INK, 2)
        b += circle(cx - 26, y, 3, INK, INK, 1)
        col = RED if nm.startswith("Q") else (BLUE if nm == "GND" else INK)
        b += text(cx - 32, y - 4, f"{i+1}", 10, GREY, "end")
        b += text(cx + 6, y + 4, nm, 12, col, "start", "bold")
    for i, (nm, role) in enumerate(right):
        y = py0 + i * pitch
        b += line(cx + cw, y, cx + cw + 26, y, INK, 2)
        b += circle(cx + cw + 26, y, 3, INK, INK, 1)
        ctrl = nm in ("SER", "RCLK", "SRCLK")
        col = GREEN if ctrl else (RED if nm.startswith("Q") or nm == "VCC" else AMBER if nm in ("OE", "SRCLR") else INK)
        b += text(cx + cw + 32, y - 4, f"{16-i}", 10, GREY, "start")
        b += text(cx + cw - 6, y + 4, nm, 12, col, "end", "bold")
        b += text(cx + cw + 32, y + 9, role, 9, GREY, "start")

    # МК зліва
    mx, my, mw, mh = 44, 250, 100, 132
    b += rect(mx, my, mw, mh, "#eef7ee", GREEN, 2, 8)
    b += text(mx + mw/2, my + 24, "МК", 15, GREEN, "middle", "bold")
    b += text(mx + mw/2, my + 42, "(SPI-хост)", 10, GREY, "middle")
    b += text(mx + mw/2, my + 66, "SER  →", 11, INK, "middle")
    b += text(mx + mw/2, my + 88, "SRCLK →", 11, GREEN, "middle")
    b += text(mx + mw/2, my + 110, "RCLK →", 11, GREEN, "middle")

    # три лінії МК → ніжки 14 (SER), 11 (SRCLK), 12 (RCLK) на правому боці
    ySER   = py0 + 2 * pitch     # right index 2 → ніжка 14
    yOE    = py0 + 3 * pitch     # ніжка 13
    yRCLK  = py0 + 4 * pitch     # ніжка 12
    ySRCLK = py0 + 5 * pitch     # ніжка 11
    ySRCLR = py0 + 6 * pitch     # ніжка 10
    # ведемо їх знизу під корпусом до правого боку, кожну до своєї ніжки
    b += polyline([(mx + mw, my + 70), (cx + cw + 96, my + 70),
                   (cx + cw + 96, ySER), (cx + cw + 26, ySER)], INK, 1.8)
    b += arrow(cx + cw + 30, ySER, cx + cw + 26, ySER, INK, 1.8)
    b += polyline([(mx + mw, my + 92), (cx + cw + 120, my + 92),
                   (cx + cw + 120, ySRCLK), (cx + cw + 26, ySRCLK)], GREEN, 1.8)
    b += arrow(cx + cw + 30, ySRCLK, cx + cw + 26, ySRCLK, GREEN, 1.8)
    b += polyline([(mx + mw, my + 114), (cx + cw + 108, my + 114),
                   (cx + cw + 108, yRCLK), (cx + cw + 26, yRCLK)], GREEN, 1.8)
    b += arrow(cx + cw + 30, yRCLK, cx + cw + 26, yRCLK, GREEN, 1.8)

    # фіксовані рівні: OE на землю, SRCLR на живлення
    b += text(cx + cw + 150, ySER, "SER: дані по черзі", 10, INK, "start")
    b += text(cx + cw + 150, yRCLK, "RCLK: 1 засув — показати байт", 10, GREEN, "start")
    b += text(cx + cw + 150, ySRCLK, "SRCLK: 8 фронтів — засунути байт", 10, GREEN, "start")
    b += text(cx + cw + 150, yOE, "OE → GND (виходи увімкнені)", 10, AMBER, "start")
    b += text(cx + cw + 150, ySRCLR, "SRCLR → VCC (не скидати)", 10, AMBER, "start")

    # живлення/земля
    b += text(cx + cw + 32, py0 - 4, "→ +VCC (з C 0.1 µF)", 10, RED, "start")
    b += text(cx - 34, py0 + 7 * pitch + 4, "GND", 10, BLUE, "end")

    # каскад: Q7' → SER наступного
    b += rect(560, 430, 200, 78, "#fff7ec", AMBER, 2, 8)
    b += text(660, 452, "Каскад", 12, AMBER, "middle", "bold")
    b += text(660, 470, "Q7' (ніжка 9) одного → SER наступного.", 9, INK, "middle")
    b += text(660, 484, "SRCLK і RCLK — спільні для всіх.", 9, GREEN, "middle")
    b += text(660, 498, "Так у ланцюг стають 16, 24, 32… виходи.", 9, GREY, "middle")
    b += line(cx + cw + 26, py0 + 7 * pitch, 560, 452, AMBER, 1.8, "5,4")

    b += text(W/2, 512, "Три дроти (SER, SRCLK, RCLK) — і неважливо, скільки чипів у ланцюзі та скільки виходів",
              12, GREEN, "middle", "bold")
    save("fig-16-5c595-2-wiring.svg", b)


# ── Фігура 3: «перший байт» — 8 фронтів SRCLK, далі один RCLK; роль латча ─────
def fig3_firstbyte():
    W, H = 800, 500
    b = header(W, H)
    b += text(W/2, 28, "«Перший байт»: 8 фронтів SRCLK засувають біти, один RCLK — показує",
              15, INK, "middle", "bold")

    x0, x1 = 165, 740
    span = x1 - x0
    nclk = 8
    edges = [x0 + 50 + i * ((span - 70) / nclk) for i in range(nclk)]

    def track(y, label, sub):
        b_ = text(x0 - 12, y + 5, label, 13, INK, "end", "bold")
        b_ += text(x0 - 12, y + 22, sub, 9, GREY, "end")
        b_ += line(x0, y - 24, x0, y + 24, FAINT, 1)
        return b_

    # — SER: рівень даних, що його МК виставляє перед кожним фронтом, старший першим
    ySER = 80
    b += track(ySER, "SER", "(дані)")
    byte = [1, 0, 1, 1, 0, 0, 1, 0]   # D7..D0
    labels = ["D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0"]
    seg = (span - 70) / nclk
    prev = ySER + 16
    spts = [(x0, prev)]
    for i, (v, ex) in enumerate(zip(byte, edges)):
        lvl = ySER - 16 if v else ySER + 16
        col = RED if v else BLUE
        x_lo = ex - seg/2
        if lvl != prev:
            spts.append((x_lo, prev)); spts.append((x_lo, lvl))
        x_hi = ex + seg/2 if i < nclk - 1 else x1
        spts.append((x_hi, lvl)); prev = lvl
        b += text(ex, ySER + (34 if not v else -22), labels[i], 9, col, "middle", "bold")
        b += text(ex, ySER + (47 if not v else -35), str(v), 10, col, "middle", "bold")
    b += polyline(spts, INK, 2.2)

    # — SRCLK: 8 імпульсів; на фронті засувається біт у зсувний регістр
    ySR = 175
    b += track(ySR, "SRCLK", "(8 фронтів)")
    pts = [(x0, ySR + 16)]
    pw = 16
    for i, ex in enumerate(edges):
        pts += [(ex, ySR + 16), (ex, ySR - 16), (ex + pw, ySR - 16), (ex + pw, ySR + 16)]
        b += text(ex + pw/2, ySR + 34, f"{i+1}", 9, GREY, "middle")
        b += circle(ex, ySR - 16, 3, GREEN, GREEN, 1)
    pts += [(x1, ySR + 16)]
    b += polyline(pts, INK, 2.2)
    b += text(x1, ySR - 24, "↑ — засув біта", 10, GREEN, "end")

    # — внутрішній зсувний регістр (не видно на виходах!)
    yREG = 268
    b += track(yREG, "регістр", "(усередині)")
    b += text((x0 + x1) / 2, yREG - 6, "біти вже всередині, але виходи ще тримають СТАРЕ значення",
              10, GREY, "middle")
    # показуємо «затікання» байта стовпчиком після 8-го фронту
    for i, v in enumerate(byte):
        col = RED if v else BLUE
        bx = x0 + 40 + i * 26
        b += rect(bx, yREG + 4, 22, 26, "#fff", col, 1.6, 4)
        b += text(bx + 11, yREG + 23, str(v), 13, col, "middle", "bold")

    # — RCLK: один імпульс ПІСЛЯ восьми фронтів; тут виходи оновлюються разом
    yRC = 350
    b += track(yRC, "RCLK", "(1 засув)")
    rcx = edges[-1] + 70
    b += polyline([(x0, yRC + 16), (rcx, yRC + 16), (rcx, yRC - 16),
                   (rcx + pw, yRC - 16), (rcx + pw, yRC + 16), (x1, yRC + 16)], GREEN, 2.4)
    b += circle(rcx, yRC - 16, 3, GREEN, GREEN, 1)
    b += arrow(rcx, yRC - 40, rcx, yRC - 18, GREEN, 1.8)
    b += text(rcx, yRC - 46, "тут — і тільки тут — виходи стрибають разом", 10, GREEN, "middle")

    # — виходи Q: тримають старе, доки RCLK не клацне
    yQ = 430
    b += track(yQ, "виходи Q", "(латч)")
    b += polyline([(x0, yQ), (rcx, yQ)], GREY, 3, "5,4")
    b += text((x0 + rcx) / 2, yQ - 8, "старе значення (не мерехтить!)", 10, GREY, "middle")
    b += arrow(rcx, yQ, rcx + 16, yQ, INK, 2)
    # після RCLK — новий байт стовпчиком
    for i, v in enumerate(byte):
        col = RED if v else BLUE
        bx = rcx + 30 + i * 26
        b += rect(bx, yQ - 13, 22, 26, "#fff", col, 1.6, 4)
        b += text(bx + 11, yQ + 6, str(v), 13, col, "middle", "bold")
    b += text(rcx + 30 + 8 * 26 + 6, yQ + 6, "= 0xB2", 11, INK, "start", "bold")

    b += text(W/2, 482, "Латч і дає головну рису: поки 8 бітів «затікають», виходи стоять; "
                        "один RCLK — і весь байт з'являється водночас.",
              12, GREEN, "middle", "bold")
    save("fig-16-5c595-3-firstbyte.svg", b)


if __name__ == "__main__":
    fig1_concept()
    fig2_wiring()
    fig3_firstbyte()
    print("ch16-s5-c-74hc595 figures done.")
