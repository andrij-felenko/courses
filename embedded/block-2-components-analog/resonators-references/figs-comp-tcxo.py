# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки 2.10.9c — «TCXO зсередини:
як влаштована термокомпенсація і де такий модуль стоїть».
НЕ чіпає головний figs.py розділу. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(fig-r10-s9c-*). Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій;
поле зелене; стрілки через marker; шрифт sans-serif. Допоміжні функції
скопійовано з figs.py розділу (єдиний вигляд між розділами).
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
COPP  = "#b5732e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def _box(x, y, w, h, title, sub, fill, stroke):
    """Підписаний блок: жирний заголовок + рядок-пояснення під ним."""
    s = rect(x, y, w, h, fill, stroke, 2.2, 8)
    s += text(x + w / 2, y + h / 2 - 4, title, 14, INK, "middle", "bold")
    if sub:
        s += text(x + w / 2, y + h / 2 + 15, sub, 11.5, GREY, "middle")
    return s


# ── Рис. 2.10.9c.1 — блок-схема аналогового TCXO ─────────────────────────────
def fig_tcxo_block():
    """Що сидить у корпусі TCXO: кварц у генераторі П'єрса, варикап як
    керована навантажувальна ємність, термодавач і компенсаційна мережа,
    що формує коригувальну напругу. Вихід — чистий такт; додатковий вхід VC
    дозволяє «підтягувати» частоту ззовні (VCTCXO)."""
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 34, "TCXO зсередини: кварц + варикап, яким керує термодавач",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "мережа компенсації «вгадує» дрейф кварцу за температурою і ледь підкручує його навантажувальну ємність CL",
              12.5, GREY, "middle", style="italic")

    # межа корпусу
    s += rect(40, 80, W - 80, H - 150, "#fdfdfd", FAINT, 2, 12)
    s += text(58, 102, "корпус TCXO (металокерамічний, 2×1.6 … 3.2×2.5 мм)", 12, GREY, "start", style="italic")

    # генератор П'єрса з кварцом (праве серце)
    gx, gy, gw, gh = 560, 150, 230, 120
    s += rect(gx, gy, gw, gh, LBLUE, BLUE, 2.2, 8)
    s += text(gx + gw / 2, gy - 8, "підтримувальний генератор (П'єрс, §2.10.5)", 12, BLUE, "middle", "bold")
    # інвертор-трикутник
    inv = [(gx + 30, gy + 36), (gx + 30, gy + 84), (gx + 78, gy + 60)]
    s += f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x,y in inv)} Z" fill="#fff" stroke="{INK}" stroke-width="2"/>\n'
    s += circle(gx + 84, gy + 60, 4, "#fff", INK, 2)
    # кварц (прямокутник із рисками)
    qx, qy = gx + 150, gy + 44
    s += rect(qx, qy, 34, 32, "#fff", INK, 2, 3)
    s += line(qx + 9, qy + 4, qx + 9, qy + 28, INK, 3)
    s += line(qx + 25, qy + 4, qx + 25, qy + 28, INK, 3)
    s += text(qx + 17, qy - 6, "кварц", 11, INK, "middle", "bold")
    s += line(gx + 88, gy + 60, qx, qy + 16, INK, 2)
    s += line(qx + 34, qy + 16, gx + 200, gy + 60, INK, 2)
    s += line(gx + 200, gy + 60, gx + 200, gy + 30, INK, 2)
    s += line(gx + 30, gy + 60, gx + 14, gy + 60, INK, 2)
    s += line(gx + 14, gy + 60, gx + 14, gy + 100, INK, 2)
    # варикап (діод зі стрілкою-конденсатором) під кварцом
    vx, vy = gx + 100, gy + 100
    s += text(vx, vy + 4, "варикап C(V)", 11.5, RED, "middle", "bold")
    s += line(gx + 14, gy + 100, gx + 200, gy + 100, RED, 2)
    s += circle(vx + 60, gy + 100, 5, LRED, RED, 2)

    # термодавач
    tx, ty, tw, th = 100, 150, 150, 60
    s += _box(tx, ty, tw, th, "термодавач", "T → напруга", LGRN, GREEN)

    # мережа компенсації
    cx, cy, cw, ch = 100, 250, 320, 78
    s += rect(cx, cy, cw, ch, "#fff", COPP, 2.2, 8)
    s += text(cx + cw / 2, cy + 22, "мережа компенсації", 14, COPP, "middle", "bold")
    s += text(cx + cw / 2, cy + 42, "аналогова: термісторний поліном на кубічну криву кварцу", 11, GREY, "middle")
    s += text(cx + cw / 2, cy + 60, "цифрова (DCXO): датчик → таблиця в EEPROM → ЦАП", 11, GREY, "middle")

    # вузол сумування напруги керування
    sumx, sumy = 470, 289
    s += circle(sumx, sumy, 16, "#fff", INK, 2)
    s += text(sumx, sumy + 5, "Σ", 16, INK, "middle", "bold")

    # стрілки сигналів
    s += arrow(tx + tw, ty + th / 2, cx + cw / 2, cy, GREEN, 2)        # давач → мережа
    s += arrow(cx + cw, cy + ch / 2, sumx - 16, sumy, COPP, 2)         # мережа → Σ
    s += arrow(sumx, sumy - 16, vx + 60, gy + 110, RED, 2)            # Σ → варикап (керує CL)
    s += text(sumx + 12, sumy - 26, "Vкор", 12, RED, "start", "bold")

    # зовнішній вхід VC (підтягування частоти)
    s += arrow(40, sumy + 36, sumx, sumy + 16, BLUE, 2, "5 4")
    s += text(60, sumy + 30, "VC (необов'язково): зовнішнє підтягування → VCTCXO", 11, BLUE, "start", style="italic")

    # вихід
    ox2 = gx + gw
    s += arrow(ox2, gy + 30, W - 50, gy + 30, INK, 2.4)
    s += text(W - 60, gy + 18, "OUT", 13, INK, "end", "bold")
    s += text(W - 60, gy + 50, "чистий такт", 11, GREY, "end", style="italic")

    # підпис-висновок
    s += text(W / 2, H - 26,
              "ціль — щоб сума «дрейф кварцу + поправка варикапом» була майже нульова в усьому діапазоні температур",
              12.5, INK, "middle", "bold")
    return s


# ── Рис. 2.10.9c.2 — компенсація кубічної кривої дрейфу ──────────────────────
def fig_compensation_curve():
    """Кубічна крива дрейфу AT-кварцу Δf/f(T), дзеркальна поправка від мережі
    компенсації і майже плаский залишок (TCXO). Показано, у скільки разів
    звужується відхилення проти голого кварцу."""
    W, H = 920, 480
    s = header(W, H)
    s += text(W / 2, 34, "Як компенсація «випрямляє» температурну криву кварцу",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "голий AT-кварц гуляє S-подібно; мережа додає дзеркальну поправку — лишається майже пряма",
              12.5, GREY, "middle", style="italic")

    ox, oy = 90, H - 96
    w, h = W - 230, H - 200
    yc = oy - h / 2
    # осі
    s += arrow(ox, oy + h / 2 + 4, ox, oy - h / 2 - 18, INK, 2)
    s += arrow(ox, yc, ox + w + 16, yc, INK, 2)
    s += text(ox + w + 20, yc + 4, "T, °C", 13, INK, "start", "bold")
    s += text(ox - 6, oy - h / 2 - 26, "Δf/f, ppm", 13, INK, "middle", "bold")
    # позначки температури
    for frac, lab in [(0.0, "−40"), (0.25, "0"), (0.5, "+25"), (0.75, "+55"), (1.0, "+85")]:
        x = ox + w * frac
        s += line(x, yc - 4, x, yc + 4, INK, 1.6)
        s += text(x, yc + 20, lab, 11, GREY, "middle")
    # нульова сітка ppm
    for ppm, fy in [(20, yc - h * 0.40), (-20, yc + h * 0.40)]:
        s += line(ox, fy, ox + w, fy, FAINT, 1.2, "4 4")
        s += text(ox - 8, fy + 4, f"{ppm:+d}", 11, GREY, "end")

    T0 = 0.5                      # точка повороту ≈ +25 °C (нормована)
    A = h * 0.40 / (0.5 ** 3)     # масштаб так, щоб на краю ≈ ±20 ppm

    def curve(scale, col, wv, dash=None):
        pts = []
        N = 200
        for j in range(N + 1):
            f = j / N
            d = f - T0
            y = yc - scale * A * (d ** 3)   # кубічна (S-подібна) залежність
            pts.append((ox + w * f, y))
        return _poly(pts, col, wv, dash)

    # голий кварц (велика амплітуда)
    s += curve(1.0, RED, 2.8)
    # дзеркальна поправка
    s += curve(-1.0, GREEN, 2.4, "6 4")
    # залишок після TCXO — майже пряма з дрібною брижею
    res = []
    N = 200
    for j in range(N + 1):
        f = j / N
        d = f - T0
        ripple = (h * 0.018) * math.sin(d * 9.0)   # дрібна неідеальність компенсації
        res.append((ox + w * f, yc + ripple))
    s += _poly(res, BLUE, 3.0)

    # легенда
    lx, ly = ox + 20, oy - h / 2 - 8
    s += rect(lx - 12, ly - 16, 360, 84, "#fff", FAINT, 1.4, 8)
    s += line(lx, ly, lx + 26, ly, RED, 2.8)
    s += text(lx + 32, ly + 4, "голий кварц (XO): ±20 ppm S-подібно", 12, RED, "start")
    s += line(lx, ly + 24, lx + 26, ly + 24, GREEN, 2.4, "6 4")
    s += text(lx + 32, ly + 28, "поправка мережі: дзеркальна крива", 12, GREEN, "start")
    s += line(lx, ly + 48, lx + 26, ly + 48, BLUE, 3.0)
    s += text(lx + 32, ly + 52, "залишок (TCXO): ±0.5 ppm — майже пряма", 12, BLUE, "start")

    # масштабна стрілка справа (у скільки разів вужче)
    rx = ox + w + 70
    s += line(rx, yc - h * 0.40, rx, yc + h * 0.40, RED, 1.6)
    s += line(rx - 5, yc - h * 0.40, rx + 5, yc - h * 0.40, RED, 1.6)
    s += line(rx - 5, yc + h * 0.40, rx + 5, yc + h * 0.40, RED, 1.6)
    s += text(rx + 10, yc, "≈ ×40", 12, RED, "start", "bold")
    s += text(rx + 10, yc + 16, "вужче", 11, RED, "start")

    s += text(W / 2, H - 22,
              "компенсація не робить кварц «ідеальним» — лишається дрібна брижа й старіння, але смуга дрейфу падає в десятки разів",
              12, GREY, "middle", style="italic")
    return s


if __name__ == "__main__":
    save("fig-r10-s9c-1-tcxo-block.svg", fig_tcxo_block())
    save("fig-r10-s9c-2-compensation-curve.svg", fig_compensation_curve())
    print("done.")
