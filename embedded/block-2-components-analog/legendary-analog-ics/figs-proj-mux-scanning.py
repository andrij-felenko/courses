# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для алгоритмічної вставки до теми 2.12.6 —
«Сканування входів через мультиплексор» (Модуль 2, Розділ 12, тема 6).

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
ОКРЕМИЙ скрипт: НЕ чіпає головний figs.py розділу й інші скрипти.
Імена SVG унікальні (префікс fig-r12-s6a-*), секція підписів — 2.12.6a.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Допоміжні функції скопійовано
з figs.py розділу 12 (єдиний вигляд між розділами).
"""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPP = "#b5732e"
SUN = "#e0a32e"
LRED = "#fbecec"
LBLUE = "#e9eefb"
LGRN = "#eef6ef"
LSUN = "#fbf3e0"
LGREY = "#f2f2f2"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{s}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def save(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Рис. 2.12.6a.1 — Часова діаграма одного проходу по каналу:
#   три адресні лінії (стрибок) → вихід MUX (експонента) → запуск ADC.
# Показуємо ДВА переходи каналів, щоб видно було залежність форми кривої
# від величини стрибка рівня (малий стрибок vs великий стрибок).
# ---------------------------------------------------------------------------
def fig_scan_timing():
    W, H = 940, 560
    body = header(W, H)
    body += text(W / 2, 30,
                 "Один прохід по каналу: виставив адресу → дав встановитися → узяв відлік",
                 size=19, anchor="middle", weight="bold")

    # Геометрія по горизонталі: три «вікна» каналів.
    x0 = 150               # початок осі часу
    x1 = 905               # кінець осі часу
    # межі перемикань каналів
    sw1 = 150              # старт каналу A (умовно)
    sw2 = 410              # перехід A→B
    sw3 = 690              # перехід B→C
    span = x1 - x0

    # ---- смуга 1: адресні лінії A2 A1 A0 ----
    addr_top = 70
    rowh = 30
    labels = ["A2", "A1", "A0"]
    # значення бітів для каналів: A=001(1), B=110(6), C=011(3)
    bits = {
        "A2": [0, 1, 0],
        "A1": [0, 1, 1],
        "A0": [1, 0, 1],
    }
    body += text(x0 - 12, addr_top - 8, "адресні лінії (цифрові виходи МК)",
                 size=12.5, anchor="start", color=GREY, style="italic")
    seg_x = [sw1, sw2, sw3, x1]
    for i, lab in enumerate(labels):
        yb = addr_top + i * rowh + rowh - 7   # рівень '0'
        yt = addr_top + i * rowh + 4          # рівень '1'
        body += text(x0 - 18, yb - 3, lab, size=13, anchor="end", weight="bold", color=BLUE)
        # будуємо ступінчасту лінію по трьох сегментах
        prev = None
        startx = sw1
        pts = []
        for s in range(3):
            val = bits[lab][s]
            y = yt if val else yb
            ex = seg_x[s + 1] if s < 2 else x1
            sx = [sw1, sw2, sw3][s]
            if prev is not None and prev != y:
                pts.append((sx, prev))
            pts.append((sx, y))
            pts.append((ex, y))
            prev = y
        body += polyline(pts, color=BLUE, w=2.4)
        # тонка сітка рівнів
        body += line(x0, yb, x1, yb, color=FAINT, w=1)

    # вертикальні лінії перемикань через усю діаграму
    grid_top = addr_top - 4
    grid_bot = 470
    for sx, name, hexv in [(sw2, "канал 6", "(110)"), (sw3, "канал 3", "(011)")]:
        body += line(sx, grid_top, sx, grid_bot, color=SUN, w=1.4, dash="5 4")
    body += line(sw1, grid_top, sw1, grid_bot, color=SUN, w=1.4, dash="5 4")
    body += text(sw1 + 6, grid_top + 2, "канал 1 (001)", size=11.5, color=COPP)
    body += text(sw2 + 6, grid_top + 2, "канал 6 (110)", size=11.5, color=COPP)
    body += text(sw3 + 6, grid_top + 2, "канал 3 (011)", size=11.5, color=COPP)

    # ---- смуга 2: напруга на спільному виході MUX (експонента) ----
    vtop = 210
    vbot = 360
    vmid = (vtop + vbot) / 2
    body += text(x0 - 18, vtop - 12, "напруга на спільному виході MUX (вхід ADC)",
                 size=12.5, anchor="start", color=GREY, style="italic")
    # рамка-осі
    body += line(x0, vtop, x0, vbot, color=INK, w=1.6)        # вісь V
    body += line(x0, vbot, x1, vbot, color=INK, w=1.6)        # вісь t (нуль)
    body += text(x0 - 6, vtop + 4, "VCC", size=11, anchor="end", color=GREY)
    body += text(x0 - 6, vbot + 4, "0", size=11, anchor="end", color=GREY)
    # рівні трьох каналів (частка від VCC)
    lvlA = 0.25
    lvlB = 0.85
    lvlC = 0.30

    def vy(frac):
        return vbot - frac * (vbot - vtop)

    def expo(seg_x0, seg_x1, start_frac, end_frac, tau_px):
        pts = []
        n = 60
        for k in range(n + 1):
            xx = seg_x0 + (seg_x1 - seg_x0) * k / n
            f = end_frac + (start_frac - end_frac) * math.exp(-(xx - seg_x0) / tau_px)
            pts.append((xx, vy(f)))
        return pts

    # пунктирні цільові рівні
    for sx, ex, lvl in [(sw1, sw2, lvlA), (sw2, sw3, lvlB), (sw3, x1, lvlC)]:
        body += line(sx, vy(lvl), ex, vy(lvl), color=FAINT, w=1.2, dash="3 3")

    # перший сегмент: канал 1 уже встановлений (рівна лінія)
    body += polyline([(sw1, vy(lvlA)), (sw2, vy(lvlA))], color=RED, w=2.6)
    # A→B: великий стрибок угору, повільна експонента
    tauB = 46
    body += polyline(expo(sw2, sw3, lvlA, lvlB, tauB), color=RED, w=2.6)
    # B→C: великий стрибок униз
    tauC = 46
    body += polyline(expo(sw3, x1, lvlB, lvlC, tauC), color=RED, w=2.6)

    # позначка «встановилось у межі точності» на сегменті B
    settleB = sw2 + 7 * tauB
    body += line(settleB, vtop - 2, settleB, vbot, color=GREEN, w=1.4, dash="4 3")
    body += text(settleB + 5, vtop + 14, "сів у ±½ LSB", size=11.5, color=GREEN, weight="bold")
    # дужка t_settle на сегменті B
    body += arrow(sw2 + 3, vbot + 22, settleB - 3, vbot + 22, color=GREEN, w=1.8)
    body += arrow(settleB - 3, vbot + 22, sw2 + 3, vbot + 22, color=GREEN, w=1.8)
    body += text((sw2 + settleB) / 2, vbot + 38, "t_settle ≈ 7·τ", size=12.5,
                 anchor="middle", color=GREEN, weight="bold")

    # стрілки «куди тягне», якщо міряти зарано (на стрибку B)
    early = sw2 + 16
    body += text(sw2 + 6, vy((lvlA + lvlB) / 2) - 4, "ще суміш", size=11, color=GREY, style="italic")

    # ---- смуга 3: моменти запуску ADC ----
    aty = 430
    body += text(x0 - 18, aty - 14, "запуск перетворення ADC (тільки після паузи)",
                 size=12.5, anchor="start", color=GREY, style="italic")
    body += line(x0, aty, x1, aty, color=FAINT, w=1)
    # правильні запуски: канал1 — на початку, канал6 — після t_settle, канал3 — після паузи
    for tx, lab in [(sw2 - 18, "вибірка 1"), (settleB + 18, "вибірка 6"),
                    (x1 - 22, "вибірка 3")]:
        body += arrow(tx, aty - 24, tx, aty - 4, color=INK, w=2.2)
        body += circle(tx, aty - 26, 4.5, fill=GREEN, stroke=GREEN, w=1)
        body += text(tx, aty + 16, lab, size=11.5, anchor="middle", color=INK)

    # «хибний» ранній запуск — перекреслений
    bad = sw2 + 22
    body += arrow(bad, aty - 24, bad, aty - 4, color=RED, w=2.2, dash="4 3")
    body += line(bad - 7, aty - 16, bad + 7, aty - 2, color=RED, w=2.2)
    body += line(bad - 7, aty - 2, bad + 7, aty - 16, color=RED, w=2.2)
    body += text(bad + 10, aty - 18, "зарано → хибно", size=11, color=RED, anchor="start")

    # вісь часу
    body += arrow(x0, 505, x1, 505, color=INK, w=2)
    body += text(x1, 524, "час", size=13, anchor="end", color=INK)

    # підпис-нагадка
    body += text(x0, 542,
                 "Адреса міняється стрибком; вихід MUX повзе по RC-експоненті; "
                 "ADC чекає, поки крива сяде в межі точності.",
                 size=12.5, color=GREY, style="italic")

    save("fig-r12-s6a-1-scan-timing.svg", body + footer())


# ---------------------------------------------------------------------------
# Рис. 2.12.6a.2 — Звідки береться пауза: RC-вузол (Rₒₙ ключа + R джерела)
# заряджає C вузла; графік «біти точності → скільки τ». Буфер скорочує τ.
# ---------------------------------------------------------------------------
def fig_settling_model():
    W, H = 940, 470
    body = header(W, H)
    body += text(W / 2, 30,
                 "Звідки пауза: відкритий ключ + ємність вузла = RC-ланка",
                 size=19, anchor="middle", weight="bold")

    # ---------- ЛІВА панель: схема еквівалента ----------
    Lx = 40
    body += rect(Lx, 56, 430, 372, fill="#ffffff", stroke=FAINT, sw=1.5, rx=12)
    body += text(Lx + 215, 80, "Еквівалент шляху сигналу", size=15,
                 anchor="middle", weight="bold")

    # джерело давача (батарейка-кружок) зліва
    sx = Lx + 40
    sy = 150
    body += circle(sx, sy, 16, fill=LGRN, stroke=GREEN, w=2)
    body += text(sx, sy + 5, "V", size=13, anchor="middle", weight="bold", color=GREEN)
    body += text(sx, sy - 26, "давач", size=12, anchor="middle", color=GREEN)

    # R джерела
    rsx0 = sx + 16
    body += line(rsx0, sy, rsx0 + 26, sy, color=INK, w=2)
    body += rect(rsx0 + 26, sy - 11, 56, 22, fill="#ffffff", stroke=INK, sw=2)
    body += text(rsx0 + 54, sy - 18, "R джерела", size=11, anchor="middle", color=INK)
    rsx1 = rsx0 + 26 + 56

    # ключ MUX (Ron) — як прямокутник-резистор з підписом «ключ Ron»
    body += line(rsx1, sy, rsx1 + 26, sy, color=INK, w=2)
    body += rect(rsx1 + 26, sy - 11, 64, 22, fill=LSUN, stroke=COPP, sw=2.4)
    body += text(rsx1 + 58, sy - 18, "ключ Rₒₙ", size=11.5, anchor="middle",
                 weight="bold", color=COPP)
    body += text(rsx1 + 58, sy + 38, "(≈ сотні Ом)", size=10.5, anchor="middle", color=COPP)
    nodex = rsx1 + 26 + 64 + 40   # спільний вузол

    # дріт до вузла
    body += line(rsx1 + 26 + 64, sy, nodex, sy, color=INK, w=2)
    body += circle(nodex, sy, 3.5, fill=INK, stroke=INK, w=1)
    body += text(nodex + 6, sy - 10, "спільний вузол", size=11, anchor="start", color=INK)

    # вхід ADC (трикутник-семпл) праворуч
    adx = nodex + 70
    body += line(nodex, sy, adx - 22, sy, color=INK, w=2)
    body += polyline([(adx - 22, sy - 16), (adx + 14, sy), (adx - 22, sy + 16),
                      (adx - 22, sy - 16)], color=BLUE, w=2, fill=LBLUE)
    body += text(adx - 2, sy + 4, "ADC", size=11, anchor="middle", color=BLUE)

    # C вузла (вхідна ємність ADC + монтаж) — вниз на землю
    cx = nodex
    body += line(cx, sy, cx, sy + 60, color=INK, w=2)
    body += line(cx - 18, sy + 60, cx + 18, sy + 60, color=BLUE, w=3)
    body += line(cx - 18, sy + 70, cx + 18, sy + 70, color=BLUE, w=3)
    body += line(cx, sy + 70, cx, sy + 88, color=INK, w=2)
    # земля
    for k, ww in enumerate([22, 14, 7]):
        body += line(cx - ww, sy + 88 + k * 5, cx + ww, sy + 88 + k * 5, color=INK, w=2)
    body += text(cx + 24, sy + 70, "C вузла", size=11.5, anchor="start",
                 weight="bold", color=BLUE)
    body += text(cx + 24, sy + 86, "(вхід ADC + монтаж)", size=10, anchor="start", color=BLUE)

    # формула τ
    body += rect(Lx + 30, 330, 370, 78, fill=LGREY, stroke=FAINT, sw=1.5, rx=8)
    body += text(Lx + 48, 358, "τ ≈ (Rₒₙ + R джерела) · C вузла", size=15,
                 weight="bold", color=INK)
    body += text(Lx + 48, 384, "вихід вузла повзе по e-експоненті", size=12.5, color=GREY)
    body += text(Lx + 48, 401, "до рівня нового каналу за час ≈ кілька τ", size=12.5, color=GREY)

    # ---------- ПРАВА панель: біти точності → скільки τ ----------
    Rx = 510
    body += rect(Rx, 56, 392, 372, fill="#ffffff", stroke=FAINT, sw=1.5, rx=12)
    body += text(Rx + 196, 80, "Скільки τ чекати на n бітів точності", size=15,
                 anchor="middle", weight="bold")

    # осі
    gx0 = Rx + 70
    gx1 = Rx + 360
    gy0 = 336         # низ (0 τ) — лишаємо місце під вісь до бокса формули
    gy1 = 118         # верх
    body += line(gx0, gy0, gx0, gy1, color=INK, w=1.6)   # вісь τ
    body += line(gx0, gy0, gx1, gy0, color=INK, w=1.6)   # вісь бітів
    body += text(gx0 - 10, gy1 - 6, "к = t_settle / τ", size=11.5, anchor="start", color=GREY)
    body += text(gx1 - 2, gy0 - 8, "n, біт", size=12, anchor="end", color=GREY)

    # дані: k = (n+1)·ln2
    ln2 = math.log(2)
    bitvals = [8, 10, 12, 14, 16]
    kmax = (16 + 1) * ln2     # ~11.8
    bx0, bx1 = 8, 16

    def bx(n):
        return gx0 + (gx1 - gx0) * (n - bx0) / (bx1 - bx0)

    def by(k):
        return gy0 - (gy0 - gy1) * (k / (kmax * 1.05))

    # горизонтальні рівні-сітка по τ
    for kk in [2, 4, 6, 8, 10]:
        yy = by(kk)
        body += line(gx0, yy, gx1, yy, color=FAINT, w=1)
        body += text(gx0 - 8, yy + 4, f"{kk}τ", size=10.5, anchor="end", color=GREY)

    # крива k(n)
    cpts = []
    n = bx0
    while n <= bx1 + 0.01:
        cpts.append((bx(n), by((n + 1) * ln2)))
        n += 0.25
    body += polyline(cpts, color=RED, w=2.6)

    # точки на цілих бітах + підписи значень
    for n in bitvals:
        k = (n + 1) * ln2
        px, py = bx(n), by(k)
        body += circle(px, py, 4.5, fill=RED, stroke=RED, w=1)
        body += text(px, gy0 + 20, str(n), size=11.5, anchor="middle", color=INK)
        # для крайньої правої точки підпис ставимо ліворуч від маркера,
        # щоб не впиратися в межу панелі
        if n == bitvals[-1]:
            body += text(px - 7, py - 7, f"{k:.1f}τ", size=11, anchor="end",
                         weight="bold", color=RED)
        else:
            body += text(px + 7, py - 7, f"{k:.1f}τ", size=11, anchor="start",
                         weight="bold", color=RED)

    # підпис формули
    body += rect(Rx + 30, 372, 332, 44, fill=LRED, stroke=RED, sw=1.4, rx=8)
    body += text(Rx + 196, 392, "k ≈ (n + 1) · ln 2", size=15, anchor="middle",
                 weight="bold", color=RED)
    body += text(Rx + 196, 409, "+1 біт точності ≈ +0.69·τ паузи", size=11.5,
                 anchor="middle", color=RED)

    save("fig-r12-s6a-2-settling-model.svg", body + footer())


if __name__ == "__main__":
    fig_scan_timing()
    fig_settling_model()
    print("done.")
