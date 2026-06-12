# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 9 — «Шум і завади: фізичні джерела» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — кожен розділ самодостатній).
Нумерація: теми — Рис. 9.T.k (перша цифра імені файла «9» = розділ 9 модуля 1).
Імена файлів: fig-9-<тема>-<k>-<slug>.svg.
"""
import os
import math
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED    = "#c0271e"   # додатний (+), гарячий
BLUE   = "#1f47b5"   # від'ємний (−), холодний
GREEN  = "#1f8a3b"   # поле (E і B), корисний сигнал
INK    = "#1b1b1b"   # основний текст/лінії
GREY   = "#8a8a8a"   # допоміжне
FAINT  = "#e4e4e4"   # дуже бліде тло
COPPER = "#cf8b5e"   # мідь (провідник, екран)
IRON   = "#9aa3ad"   # метал/корпус
ORANGE = "#e08030"   # шум/завада (акцент-небезпека)
PURPLE = "#7a3fb0"   # струм завади / спільний шлях
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'  <marker id="aCopper" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{COPPER}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         ORANGE: "aOrange", PURPLE: "aPurple", COPPER: "aCopper", GREY: "aGrey"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None, marker=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{_MARK.get(marker, "aInk")})"' if marker else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}{mk}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── допоміжні примітиви ───────────────────────────────────────────────────────
def arc(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.4, marker=None, dash=None):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{_MARK.get(marker, "aInk")})"' if marker else ""
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{da}{mk}/>\n')


def resistor(x, y, w=66, h=22, label="R", lbl_color=INK):
    out = rect(x, y - h / 2, w, h, "#ffffff", INK, 2, 3)
    if label:
        out += text(x + w / 2, y - h / 2 - 7, label, 12.5, lbl_color, "middle", "bold", "italic")
    return out


def cap_v(cx, cy, gap=8, plate=22, label="C", lbl_color=INK):
    """Вертикальний конденсатор (дві горизонтальні пластини)."""
    out = line(cx - plate / 2, cy - gap / 2, cx + plate / 2, cy - gap / 2, INK, 2.6)
    out += line(cx - plate / 2, cy + gap / 2, cx + plate / 2, cy + gap / 2, INK, 2.6)
    if label:
        out += text(cx + plate / 2 + 6, cy + 4, label, 12.5, lbl_color, "start", "bold", "italic")
    return out


def cap_h(cx, cy, gap=8, plate=22, label="C", lbl_color=INK):
    """Горизонтальний конденсатор (дві вертикальні пластини)."""
    out = line(cx - gap / 2, cy - plate / 2, cx - gap / 2, cy + plate / 2, INK, 2.6)
    out += line(cx + gap / 2, cy - plate / 2, cx + gap / 2, cy + plate / 2, INK, 2.6)
    if label:
        out += text(cx, cy - plate / 2 - 6, label, 12.5, lbl_color, "middle", "bold", "italic")
    return out


def gnd(x, y, color=INK, w=2):
    """Символ землі вниз від (x,y)."""
    out = line(x, y, x, y + 8, color, w)
    out += line(x - 12, y + 8, x + 12, y + 8, color, w)
    out += line(x - 7.5, y + 13, x + 7.5, y + 13, color, w)
    out += line(x - 3.5, y + 18, x + 3.5, y + 18, color, w)
    return out


def scope_box(x, y, w, h, label="осцилограф"):
    """Корпус осцилографа з екраном; повертає (svg, (sx,sy,sw,sh)) межі екрана."""
    out = rect(x, y, w, h, "#f4f5f7", INK, 2.2, 10)
    pad = 14
    sx, sy = x + pad, y + pad
    sw, sh = w - 2 * pad, h - 2 * pad - 16
    out += rect(sx, sy, sw, sh, "#0d1f17", GREEN, 1.6, 4)
    out += text(x + w / 2, y + h - 7, label, 10.5, GREY, "middle", "bold")
    return out, (sx, sy, sw, sh)


def grid(sx, sy, sw, sh, nx=10, ny=8, color="#143b2b"):
    out = ""
    for i in range(1, nx):
        gx = sx + sw * i / nx
        out += line(gx, sy, gx, sy + sh, color, 1)
    for j in range(1, ny):
        gy = sy + sh * j / ny
        out += line(sx, gy, sx + sw, gy, color, 1)
    # центральні осі
    out += line(sx + sw / 2, sy, sx + sw / 2, sy + sh, "#1f5740", 1.2)
    out += line(sx, sy + sh / 2, sx + sw, sy + sh / 2, "#1f5740", 1.2)
    return out


def _sine(x0, y0, width, amp, cycles=1.0, phase=0.0, n=160):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * width
        y = y0 - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((x, y))
    return pts


def _noisy(x0, y0, width, amp, sigma, seed=1, n=240, base=0.0):
    """Лінія з гаусовим шумом навколо рівня y0 (base — постійне зміщення вгору)."""
    rnd = random.Random(seed)
    pts = []
    smooth = 0.0
    for i in range(n + 1):
        t = i / n
        x = x0 + t * width
        # легке згладжування, щоб шум був «товстим», а не голчастим
        nz = rnd.gauss(0, 1)
        smooth = 0.6 * smooth + 0.4 * nz
        y = y0 - base - sigma * (0.5 * nz + 1.4 * smooth) - amp * 0  # amp заведено для сумісності
        pts.append((x, y))
    return pts


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.1 — Шум і завада: чому жоден сигнал не ідеальний.  Рис. 9.1.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.1.1 — два роди «бруду»: внутрішній шум vs зовнішня наводка ──────────
def fig_noise_vs_interference():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Два роди завад на сигналі: внутрішній шум і зовнішня наводка",
              19, INK, "middle", "bold")
    s += text(W / 2, 52, "шум народжується в самій деталі (випадковий, широкосмуговий); наводка приходить ззовні (часто з впізнаваним джерелом)",
              11.5, GREY, "middle", style="italic")

    # центр — наш сигнальний ланцюг
    chy = 250
    s += rect(W / 2 - 90, chy - 34, 180, 68, "#eef7f0", GREEN, 2.2, 10)
    s += text(W / 2, chy - 6, "наш сигнал", 13.5, GREEN, "middle", "bold")
    s += text(W / 2, chy + 16, "(давач → дріт → вхід)", 10.5, INK, "middle")

    # ── ЛІВО: внутрішній шум ──
    s += rect(40, 96, 360, 300, "#fff6ee", ORANGE, 1.8, 12)
    s += text(220, 122, "ВНУТРІШНІЙ ШУМ (noise)", 14, ORANGE, "middle", "bold")
    s += text(220, 142, "джерело — теплова й квантова фізика всередині", 10.3, GREY, "middle", style="italic")
    items = [("теплова тряска електронів", 172),
             ("дискретність заряду (струм — це порції)", 198),
             ("повільні дрейфи (шум 1/f)", 224)]
    for lab, yy in items:
        s += circle(70, yy - 4, 3.4, ORANGE, ORANGE, 1)
        s += text(84, yy, lab, 11, INK, "start")
    # маленький осцилоскоп-фрагмент: «трава»
    s += rect(70, 244, 300, 130, "#0d1f17", ORANGE, 1.6, 6)
    base = _sine(80, 309, 280, 26, 1.6, 0.0)
    rnd = random.Random(7)
    nz = [(x, y + rnd.gauss(0, 5.5)) for (x, y) in base]
    s += polyline(nz, "#ffd9b3", 1.6)
    s += polyline(base, GREEN, 1.4, "4,3")
    s += text(220, 366, "товста «трава» поверх сигналу", 10, "#ffd9b3", "middle", "bold")
    s += arrow(404, 250, 446, 250, ORANGE, 2.6)
    s += text(425, 240, "зсередини", 9.5, ORANGE, "middle", "bold")

    # ── ПРАВО: зовнішня наводка ──
    s += rect(540, 96, 360, 300, "#f3eefb", PURPLE, 1.8, 12)
    s += text(720, 122, "ЗОВНІШНЯ НАВОДКА (interference)", 13, PURPLE, "middle", "bold")
    s += text(720, 142, "джерело — світ навколо, через поле або спільний дріт", 10.3, GREY, "middle", style="italic")
    items2 = [("мережа 50 Гц (проводка в стіні)", 172),
              ("імпульси від моторів, реле, ключів", 198),
              ("радіо, передавачі, switching-БЖ", 224)]
    for lab, yy in items2:
        s += circle(570, yy - 4, 3.4, PURPLE, PURPLE, 1)
        s += text(584, yy, lab, 11, INK, "start")
    s += rect(570, 244, 300, 130, "#0d1f17", PURPLE, 1.6, 6)
    hum = _sine(580, 309, 280, 24, 1.0, 0.0)            # чистий 50 Гц гул
    sig = _sine(580, 309, 280, 10, 6.0, 0.4)
    mix = [(hum[i][0], hum[i][1] + (sig[i][1] - 309)) for i in range(len(hum))]
    s += polyline(mix, "#d9c2f2", 1.8)
    s += text(720, 366, "впізнаваний гул 50 Гц", 10, "#d9c2f2", "middle", "bold")
    s += arrow(496, 250, 538, 250, PURPLE, 2.6)
    s += text(517, 240, "ззовні", 9.5, PURPLE, "middle", "bold")

    # підпис-висновок
    s += rect(250, 414, 440, 42, "#f4f5f7", INK, 1.6, 9)
    s += text(W / 2, 434, "Шум прибирають фільтром і усередненням; наводку —", 11, INK, "middle", "bold")
    s += text(W / 2, 450, "екраном, геометрією і правильною «землею». Лікують по-різному.", 11, INK, "middle", "bold")
    save("fig-9-1-1-noise-vs-interference.svg", s)


# ── Рис. 9.1.2 — відношення сигнал/шум (SNR): той самий шум на двох сигналах ───
def fig_snr():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Важить не сам шум, а відношення сигнал/шум (SNR)",
              19, INK, "middle", "bold")
    s += text(W / 2, 52, "однаковий рівень шуму губить слабкий сигнал і майже не псує сильний — тому борються за SNR, а не «за тишу»",
              11.5, GREY, "middle", style="italic")

    rnd = random.Random(3)

    def panel(x0, title, amp, col, ok):
        out = rect(x0, 86, 410, 250, "#0d1f17", INK, 1.8, 8)
        sx, sy, sw, sh = x0 + 16, 100, 378, 200
        out2 = ""
        for j in range(1, 6):
            out2 += line(sx, sy + sh * j / 6, sx + sw, sy + sh * j / 6, "#143b2b", 1)
        mid = sy + sh / 2
        base = _sine(sx, mid, sw, amp, 2.0, 0.0)
        noisy = [(xx, yy + rnd.gauss(0, 16)) for (xx, yy) in base]
        out2 += polyline(noisy, col, 1.7)
        out2 += polyline(base, GREEN, 1.6, "5,3")
        out += out2
        out += text(x0 + 205, 110, title, 12.5, "#cfe9d8", "middle", "bold")
        # індикатор амплітуди сигналу
        out += line(sx + 40, mid, sx + 40, mid - amp, GREEN, 2.0)
        out += text(sx + 46, mid - amp / 2, "сигнал", 9.5, GREEN, "start", "bold")
        verdict = "✓ читається" if ok else "✗ тоне в шумі"
        vcol = GREEN if ok else ORANGE
        out += rect(x0 + 110, 308, 190, 24, "#ffffff", vcol, 1.6, 7)
        out += text(x0 + 205, 325, verdict, 11.5, vcol, "middle", "bold")
        return out

    s += panel(40, "СИЛЬНИЙ сигнал — високий SNR", 78, "#ffd9b3", True)
    s += panel(490, "СЛАБКИЙ сигнал — низький SNR", 18, "#ffd9b3", False)

    s += rect(260, 356, 420, 56, "#f4f5f7", INK, 1.6, 9)
    s += text(W / 2, 378, "SNR = потужність сигналу / потужність шуму", 12.5, INK, "middle", "bold")
    s += text(W / 2, 398, "у децибелах: SNR(дБ) = 10·log₁₀(Pс/Pш) = 20·log₁₀(Uс/Uш)", 11.5, INK, "middle")
    save("fig-9-1-2-snr.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.2 — Тепловий шум Джонсона—Найквіста.  Рис. 9.2.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.2.1 — механізм: теплова тряска електронів → флуктуація напруги ─────
def fig_thermal_mechanism():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Звідки тепловий шум: гаряча тряска електронів стає напругою",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "за §1.2.9 електрони безперервно товчуться від теплоти; навіть без струму їхній хаотичний рух дає мізерну змінну напругу на кінцях резистора",
              11, GREY, "middle", style="italic")

    # резистор як «коробка» з електронами, що хаотично рухаються
    bx, by, bw, bh = 70, 120, 380, 210
    s += rect(bx, by, bw, bh, "#fbe9e1", INK, 2.2, 8)
    s += text(bx + bw / 2, by - 10, "резистор при температурі T (нічого не під'єднано)", 11.5, INK, "middle", "bold")
    s += text(bx + bw / 2, by + bh + 22, "що гарячіше — то шаленіша тряска", 10.5, RED, "middle", "bold")
    # виводи
    s += line(bx, by + bh / 2, bx - 34, by + bh / 2, COPPER, 3)
    s += line(bx + bw, by + bh / 2, bx + bw + 34, by + bh / 2, COPPER, 3)

    rnd = random.Random(11)
    for _ in range(26):
        ex = bx + 22 + rnd.random() * (bw - 44)
        ey = by + 22 + rnd.random() * (bh - 44)
        ang = rnd.random() * 2 * math.pi
        ln = 16 + rnd.random() * 14
        s += circle(ex, ey, 4.6, "#e2e9f7", BLUE, 1.4)
        s += text(ex, ey + 3.4, "−", 9, BLUE, "middle", "bold")
        s += arrow(ex, ey, ex + ln * math.cos(ang), ey + ln * math.sin(ang), GREY, 1.3)
    s += text(bx + 18, by + 20, "хаотичний рух (немає переважного напрямку)", 9.5, GREY, "start", "bold")

    # вольтметр / осцилограф показує крихітні флуктуації
    s += arrow(bx + bw + 34, by + bh / 2 - 30, 540, by + 40, INK, 2.0)
    s += rect(540, 96, 360, 240, "#0d1f17", INK, 1.8, 8)
    sx, sy, sw, sh = 556, 112, 328, 184
    for j in range(1, 6):
        s += line(sx, sy + sh * j / 6, sx + sw, sy + sh * j / 6, "#143b2b", 1)
    mid = sy + sh / 2
    s += line(sx, mid, sx + sw, mid, "#1f5740", 1.2)
    base = [(sx + sw * i / 240, mid) for i in range(241)]
    noisy = [(xx, yy + rnd.gauss(0, 22)) for (xx, yy) in base]
    s += polyline(noisy, "#ffb380", 1.6)
    s += text(720, 110, "напруга на відкритих кінцях", 11, "#cfe9d8", "middle", "bold")
    s += text(720, 320, "середнє = 0, але «не нуль» щомиті: це шумова напруга", 10, "#ffb380", "middle", "bold")
    save("fig-9-2-1-thermal-mechanism.svg", s)


# ── Рис. 9.2.2 — формула √(4kTRB): від чого залежить тепловий шум ──────────────
def fig_thermal_formula():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 30, "Скільки шуму: закон Джонсона—Найквіста",
              19, INK, "middle", "bold")
    s += text(W / 2, 52, "шумова напруга залежить лише від температури, опору і смуги — і ні від чого більше; матеріал та форма резистора не важать",
              11, GREY, "middle", style="italic")

    # центральна формула
    s += rect(270, 80, 400, 64, "#eef2fb", BLUE, 2.0, 12)
    s += text(W / 2, 110, "Uш(rms) = √(4 · k · T · R · B)", 21, INK, "middle", "bold")
    s += text(W / 2, 132, "k = 1.38×10⁻²³ Дж/К — стала Больцмана", 10.5, GREY, "middle", style="italic")

    # чотири «ручки», кожна зі стрілкою росту
    knobs = [("T — температура", "охолоди → тихіше", "K", 90, RED),
             ("R — опір", "менший R → тихіше", "Ω", 320, COPPER),
             ("B — смуга частот", "вужча смуга → тихіше", "Гц", 550, GREEN),
             ("k — стала Больцмана", "фундамент, не крутиться", "—", 780, GREY)]
    for lab, hint, unit, xc, col in knobs:
        s += rect(xc - 95, 180, 190, 110, "#ffffff", col, 1.8, 10)
        s += text(xc, 204, lab, 11.5, col, "middle", "bold")
        s += text(xc, 224, f"[{unit}]", 10, GREY, "middle", "italic")
        # стрілочка «корінь»: росте як √
        s += arrow(xc - 60, 270, xc + 60, 252, col, 2.2)
        s += text(xc, 282, hint, 9.6, INK, "middle")

    s += rect(180, 320, 580, 76, "#fff6ee", ORANGE, 1.7, 10)
    s += text(W / 2, 344, "Ключове: шум росте як КОРІНЬ. Учетверо ширша смуга → лише вдвічі",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 363, "більше шуму. Учетверо більший опір → теж лише вдвічі.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 384, "Тому головні важелі тиші — звузити смугу B і знизити R джерела.",
              11, ORANGE, "middle", "bold")
    save("fig-9-2-2-thermal-formula.svg", s)


# ── Рис. 9.2.3 — смуга вирішує: широка vs вузька → скільки шуму впускаємо ──────
def fig_bandwidth():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 30, "Чому смуга B головна: фільтр впускає шум лише зі своєї смуги",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "тепловий шум «білий» — рівний на всіх частотах; скільки смуги відкрив, стільки шумової потужності й зібрав",
              11, GREY, "middle", style="italic")

    # вісь частоти зі сталою спектральною густиною шуму (білий шум)
    ax, ay, aw = 70, 300, 800
    s += arrow(ax - 8, ay, ax + aw + 14, ay, INK, 1.8)
    s += text(ax + aw + 10, ay + 22, "частота f", 11.5, INK, "middle", "bold")
    s += arrow(ax, ay + 8, ax, 96, INK, 1.8)
    s += text(ax - 8, 92, "густина шуму", 10.5, INK, "end", "bold")
    # рівна «полиця» білого шуму
    level = 130
    s += line(ax, level, ax + aw, level, ORANGE, 2.0, "6,4")
    s += text(ax + aw - 6, level - 8, "білий шум: однаково на всіх f", 10, ORANGE, "end", "bold")

    # широка смуга
    bw1 = 470
    s += rect(ax, level, bw1, ay - level, "#ffe6d1", ORANGE, 1.4)
    s += arrow(ax, ay + 40, ax + bw1, ay + 40, GREEN, 2.0)
    s += arrow(ax + bw1, ay + 40, ax, ay + 40, GREEN, 2.0)
    s += text(ax + bw1 / 2, ay + 58, "широка смуга B₁ — багато шуму", 10.5, GREEN, "middle", "bold")

    # вузька смуга
    bw2 = 120
    s += rect(ax, level - 0, bw2, ay - level, "#ffcf9e", "#b35a13", 2.0)
    s += text(ax + bw2 / 2, level - 12, "B₂", 12, "#b35a13", "middle", "bold")
    s += text(ax + bw2 + 8, level + 24, "вузька смуга B₂ — мало шуму", 10.5, "#b35a13", "start", "bold")

    s += rect(300, 86, 360, 52, "#f4f5f7", INK, 1.6, 9)
    s += text(W / 2 - 30, 108, "площа під полицею = шумова потужність", 11, INK, "middle", "bold")
    s += text(W / 2 - 30, 126, "Uш ∝ √B  →  вужча смуга, тихіше", 11, BLUE, "middle", "bold")
    save("fig-9-2-3-bandwidth.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.3 — Дробовий шум і шум 1/f.  Рис. 9.3.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.3.1 — дробовий шум: струм — це дощ окремих зарядів ──────────────────
def fig_shot_noise():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Дробовий шум: струм — не рівна ріка, а дощ окремих зарядів",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "заряд дискретний (§1.1.1): носії долають бар'єр поодинці й у випадкові миті — тому навіть рівний у середньому струм дрібно тремтить",
              11, GREY, "middle", style="italic")

    # ліворуч: бар'єр, крізь який «крапають» заряди
    bx = 90
    s += line(bx, 110, bx, 330, INK, 2.4)
    s += text(bx, 100, "бар'єр (p-n перехід)", 10.5, INK, "middle", "bold")
    rnd = random.Random(5)
    for _ in range(16):
        ey = 120 + rnd.random() * 200
        ex = bx - 50 - rnd.random() * 30
        s += circle(ex, ey, 4.4, "#e2e9f7", BLUE, 1.3)
        s += arrow(ex + 6, ey, bx - 6, ey + rnd.gauss(0, 4), GREY, 1.2)
    s += text(bx - 70, 348, "носії підходять у випадкові миті", 9.6, GREY, "middle", "bold")

    # праворуч: струм у часі — рівний середній + дрібні «сходинки/тремтіння»
    ax, ay, aw = 230, 250, 640
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.4)
    s += arrow(ax, ay + 10, ax, 110, GREY, 1.4)
    s += text(ax + aw + 8, ay + 20, "час", 11, GREY, "middle", "bold")
    s += text(ax - 8, 106, "струм I", 11, GREY, "end", "bold")
    Iavg = ay - 110
    s += line(ax, Iavg, ax + aw, Iavg, GREEN, 1.8, "6,4")
    s += text(ax + aw - 6, Iavg - 8, "середній струм I", 10.5, GREEN, "end", "bold")
    # тремтливий струм навколо середнього
    pts = []
    val = 0.0
    for i in range(241):
        x = ax + aw * i / 240
        # пуассонівські «удари»: випадкові підскоки + спад
        if rnd.random() < 0.10:
            val += rnd.random() * 26
        val *= 0.82
        pts.append((x, Iavg - val + 8))
    s += polyline(pts, ORANGE, 1.7)
    s += text(ax + aw / 2, 130, "кожен заряд — крихітний «удар»; сума тремтить навколо середнього",
              10.5, ORANGE, "middle", "bold")

    s += rect(300, 356, 420, 52, "#eef2fb", BLUE, 1.6, 9)
    s += text(W / 2, 378, "Iш(rms) = √(2 · q · I · B)", 15, INK, "middle", "bold")
    s += text(W / 2, 397, "більший струм — більший шум, але відносно (Iш/I) він спадає",
              10, GREY, "middle", "italic")
    save("fig-9-3-1-shot-noise.svg", s)


# ── Рис. 9.3.2 — спектри: білий (тепловий/дробовий) vs 1/f (флікер) ───────────
def fig_one_over_f():
    W, H = 940, 410
    s = header(W, H)
    s += text(W / 2, 30, "Шум 1/f: чим повільніше міряєш, тим більше його",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "білий шум рівний на всіх частотах; флікер-шум (1/f) злітає на низьких — саме він дає повільний «дрейф» нуля",
              11, GREY, "middle", style="italic")

    ax, ay, aw, ah = 90, 320, 760, 210
    s += arrow(ax - 8, ay, ax + aw + 14, ay, INK, 1.8)
    s += arrow(ax, ay + 8, ax, ay - ah, INK, 1.8)
    s += text(ax + aw + 8, ay + 22, "частота (log)", 11, INK, "middle", "bold")
    s += text(ax - 8, ay - ah - 4, "густина шуму (log)", 10.5, INK, "end", "bold")
    # мітки декад
    for k, lab in enumerate(["0.1", "1", "10", "10²", "10³", "10⁴", "10⁵"]):
        gx = ax + aw * k / 6
        s += line(gx, ay - 4, gx, ay + 4, INK, 1.4)
        s += text(gx, ay + 20, lab, 9.5, GREY, "middle")
    s += text(ax + aw / 2, ay + 38, "Гц", 9.5, GREY, "middle", "italic")

    # біла полиця
    white = ay - 70
    s += line(ax, white, ax + aw, white, ORANGE, 2.2)
    s += text(ax + aw - 6, white - 8, "білий шум (тепловий + дробовий)", 10, ORANGE, "end", "bold")

    # 1/f крива: на низьких частотах злітає, потім зливається з полицею
    pts = []
    for k in range(0, 121):
        t = k / 120.0           # 0..1 по декадах
        gx = ax + aw * t
        # log-log: 1/f → пряма з нахилом; нижче кутової частоти зливається з білою
        extra = max(0.0, (0.42 - t)) * 360   # підйом ліворуч
        gy = white - extra
        pts.append((gx, gy))
    s += polyline(pts, PURPLE, 2.6)
    s += text(ax + 70, white - 150, "1/f (флікер)", 11, PURPLE, "start", "bold")
    # кутова частота
    fc = ax + aw * 0.42
    s += line(fc, ay, fc, white - 6, GREY, 1.3, "4,3")
    s += text(fc, ay - 6, "fc", 10, GREY, "middle", "bold", "italic")

    # зона повільних вимірювань
    s += rect(ax, ay - ah + 6, aw * 0.25, ah - 6, "#f3eefb", "none", 0)
    s += text(ax + aw * 0.12, ay - ah + 24, "повільні вимірювання", 10, PURPLE, "middle", "bold")
    s += text(ax + aw * 0.12, ay - ah + 40, "(сюди потрапляє дрейф)", 9.3, PURPLE, "middle")

    s += text(W / 2, 88, "Поради: усереднюй швидко (не «довго й повільно»); калібруй нуль;",
              10.5, INK, "middle", "bold")
    s += text(W / 2, 104, "вимірюй різницю двох близьких відліків — спільний дрейф вирахується.",
              10.5, INK, "middle", "bold")
    save("fig-9-3-2-one-over-f.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.4 — Наводка через електричне поле: ємнісний зв'язок.  Рис. 9.4.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.4.1 — ємнісний зв'язок: паразитна ємність як «дріт» для змінного ────
def fig_capacitive_coupling():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Ємнісний зв'язок: два провідники поряд — це маленький конденсатор",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "змінне поле (§1.1.3) джерела наводить заряд на сусідній провід через паразитну ємність Cпар — і тим сильніше, чим вища частота",
              11, GREY, "middle", style="italic")

    # джерело завади (силовий провід) угорі
    s += line(120, 110, 700, 110, RED, 4)
    s += text(120, 100, "мережевий провід ~230 В, 50 Гц", 11, RED, "start", "bold")
    # E-поле вниз до сигнального проводу
    for x in range(180, 661, 80):
        s += arrow(x, 118, x, 196, GREEN, 1.5, "5,3")
    s += text(420, 160, "змінне E-поле", 10.5, GREEN, "middle", "bold", "italic")

    # сигнальний провід (високоомний вхід) знизу
    s += line(120, 210, 700, 210, BLUE, 3)
    s += text(120, 232, "сигнальний провід до високоомного входу", 11, BLUE, "start", "bold")

    # паразитна ємність між ними (символ)
    s += cap_v(420, 160, gap=10, plate=0, label="")
    s += line(420, 118, 420, 155, GREY, 1.6, "3,3")
    s += line(420, 165, 420, 208, GREY, 1.6, "3,3")
    s += text(452, 150, "Cпар (паразитна ємність)", 10.5, GREY, "start", "bold")

    # еквівалентна схема праворуч: дільник Cпар–Rвх
    ex0 = 760
    s += rect(ex0 - 40, 96, 150, 250, "#f4f5f7", INK, 1.6, 10)
    s += text(ex0 + 35, 116, "що виходить", 11, INK, "middle", "bold")
    # верх: джерело 50 Гц
    s += circle(ex0 + 35, 150, 16, "#fff", RED, 2)
    s += text(ex0 + 35, 155, "~", 16, RED, "middle", "bold")
    s += text(ex0 + 35, 138, "50 Гц", 8.5, RED, "middle", "bold")
    s += line(ex0 + 35, 166, ex0 + 35, 184, INK, 2)
    # Cпар
    s += cap_h(ex0 + 35, 196, gap=9, plate=18, label="Cпар")
    s += line(ex0 + 35, 205, ex0 + 35, 224, INK, 2)
    # вузол виходу
    s += circle(ex0 + 35, 224, 3, INK, INK, 1)
    s += text(ex0 + 80, 226, "вхід", 9.5, BLUE, "start", "bold")
    # Rвх вниз
    s += resistor(ex0 + 24, 224 + 34, w=22, h=44, label="")
    s += text(ex0 + 60, 224 + 56, "Rвх (великий)", 9.3, INK, "start")
    s += line(ex0 + 35, 224, ex0 + 35, 224, INK, 2)
    s += gnd(ex0 + 35, 318)
    s += text(ex0 + 35, 338, "дільник Cпар–Rвх", 9.6, GREY, "middle", "bold")

    s += rect(150, 360, 520, 70, "#fff6ee", ORANGE, 1.7, 10)
    s += text(410, 384, "Великий вхідний опір = слабка ланка: навіть пФ ємності",
              11.5, INK, "middle", "bold")
    s += text(410, 403, "пропускає помітний гул. Тому «рука біля щупа» дає 50 Гц на екрані,",
              11, INK, "middle", "bold")
    s += text(410, 421, "а низькоомний вузол майже не наводиться.",
              11, ORANGE, "middle", "bold")
    save("fig-9-4-1-capacitive-coupling.svg", s)


# ── Рис. 9.4.2 — лікування ємнісної наводки: екран + менший опір ──────────────
def fig_capacitive_cure():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 30, "Як прибрати ємнісний гул: перехопити поле і знизити опір",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "заземлений екран ловить силові лінії E на себе (заряд стікає в землю); а менший опір вузла «коротить» наведений струм",
              11, GREY, "middle", style="italic")

    # ЛІВО — без екрана (наводиться)
    s += text(235, 92, "БЕЗ ЕКРАНА — наводиться", 12.5, ORANGE, "middle", "bold")
    s += line(80, 118, 390, 118, RED, 4)
    s += text(235, 110, "джерело завади", 9.6, RED, "middle", "bold")
    for x in range(120, 361, 60):
        s += arrow(x, 124, x, 196, GREEN, 1.5, "5,3")
    s += line(80, 210, 390, 210, BLUE, 3)
    s += text(235, 230, "сигнальний провід ловить поле", 9.6, BLUE, "middle", "bold")

    # ПРАВО — з екраном (поле перехоплено)
    s += text(700, 92, "З ЕКРАНОМ — поле перехоплено", 12.5, GREEN, "middle", "bold")
    s += line(540, 118, 850, 118, RED, 4)
    s += text(700, 110, "джерело завади", 9.6, RED, "middle", "bold")
    for x in range(580, 821, 60):
        s += arrow(x, 124, x, 156, GREEN, 1.5, "5,3")
    # екран-труба над сигнальним проводом
    s += rect(545, 160, 300, 18, "#dfe3e8", IRON, 2.0, 6)
    s += text(695, 152, "заземлений екран (метал)", 9.6, IRON, "middle", "bold")
    s += line(845, 169, 875, 169, IRON, 2)
    s += gnd(875, 169, IRON)
    # сигнальний провід під екраном — поля майже нема
    s += line(560, 210, 830, 210, BLUE, 3)
    s += text(695, 230, "сигнал «у тіні» — гулу майже нема", 9.6, GREEN, "middle", "bold")
    # заряд стікає
    s += arrow(620, 178, 620, 168, ORANGE, 1.8)
    s += text(660, 192, "наведений заряд → у землю", 9.3, ORANGE, "start", "bold")

    s += rect(150, 286, 640, 76, "#f4f5f7", INK, 1.6, 10)
    s += text(W / 2, 310, "Два важелі проти ємнісної наводки:", 11.5, INK, "middle", "bold")
    s += text(W / 2, 330, "1) ЗАЗЕМЛЕНИЙ ЕКРАН навколо сигналу — перехоплює E-поле (детально §1.9.7);",
              11, INK, "middle")
    s += text(W / 2, 350, "2) НИЖЧИЙ ОПІР вузла й коротший провід — наведений струм дає меншу напругу.",
              11, INK, "middle")
    save("fig-9-4-2-capacitive-cure.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.5 — Наводка через магнітне поле: індуктивний зв'язок.  Рис. 9.5.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.5.1 — змінне B крізь петлю наводить ЕРС (площа петлі вирішує) ───────
def fig_inductive_coupling():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Індуктивний зв'язок: змінне магнітне поле крізь петлю наводить напругу",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "струм у сусідньому проводі (§1.8.4) родить змінне B; воно пронизує площу нашої сигнальної петлі та наводить ЕРС ∝ площа × швидкість зміни B",
              10.5, GREY, "middle", style="italic")

    # провід-агресор зі змінним струмом
    s += line(90, 110, 470, 110, RED, 4)
    s += arrow(330, 110, 430, 110, RED, 3)
    s += text(90, 100, "провід-агресор: змінний струм Iзав", 11, RED, "start", "bold")

    # концентричні лінії B навколо проводу (входять у площину праворуч)
    for r in (34, 58, 84):
        s += circle(280, 110, r, "none", GREEN, 1.4, "4,3")
    s += text(280, 110 - 96, "змінне поле B навколо проводу", 10, GREEN, "middle", "bold", "italic")

    # сигнальна петля (велика площа): прямокутний контур із двох проводів
    lx, ly, lw, lh = 150, 200, 330, 150
    s += rect(lx, ly, lw, lh, "#eef7f0", GREEN, 2.4)
    s += text(lx + lw / 2, ly + lh / 2, "площа петлі A", 12.5, GREEN, "middle", "bold", "italic")
    s += text(lx + lw / 2, ly + lh / 2 + 20, "(сигнал «туди» і «назад»)", 9.6, INK, "middle")
    # давач і вхід на кінцях петлі
    s += circle(lx, ly + lh / 2, 12, "#fff", INK, 2)
    s += text(lx, ly + lh / 2 + 4, "Д", 11, INK, "middle", "bold")
    s += text(lx, ly + lh / 2 + 30, "давач", 9.3, INK, "middle")
    s += rect(lx + lw - 14, ly + lh / 2 - 16, 28, 32, "#fff", BLUE, 2, 4)
    s += text(lx + lw, ly + lh / 2 + 34, "вхід", 9.3, BLUE, "middle")
    # наведена ЕРС
    s += text(lx + lw / 2, ly - 10, "B пронизує цю площу → наводить ЕРС у петлі", 10, GREEN, "middle", "bold")

    # формула праворуч
    s += rect(560, 120, 320, 130, "#eef2fb", BLUE, 1.8, 12)
    s += text(720, 146, "наведена ЕРС", 11.5, BLUE, "middle", "bold")
    s += text(720, 178, "Uнав ≈ A · (dB/dt)", 17, INK, "middle", "bold")
    s += text(720, 206, "A — площа петлі", 11, INK, "middle")
    s += text(720, 226, "dB/dt — швидкість зміни поля", 11, INK, "middle")

    s += rect(150, 372, 640, 56, "#fff6ee", ORANGE, 1.7, 10)
    s += text(W / 2, 396, "Головний важіль — ПЛОЩА петлі. Зведи площу до нуля (проводи поруч),",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 416, "і наводити нема куди. Звідси — вита пара (§1.9.8): площа майже зникає.",
              11, ORANGE, "middle", "bold")
    save("fig-9-5-1-inductive-coupling.svg", s)


# ── Рис. 9.5.2 — велика петля vs мала: чому площа — це антена для завад ────────
def fig_loop_area():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 30, "Площа петлі — це розмір «антени» для магнітної наводки",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "та сама завада, дві розводки: широко розведені проводи ловлять багато поля, притиснуті один до одного — майже нічого",
              11, GREY, "middle", style="italic")

    # фон поля: рівномірні B-лінії (точки — поле з площини)
    def field(x0, y0, w, h):
        out = ""
        for gx in range(int(x0) + 22, int(x0 + w) - 10, 30):
            for gy in range(int(y0) + 22, int(y0 + h) - 10, 30):
                out += circle(gx, gy, 2.0, GREEN, GREEN, 1)
        return out

    # ЛІВО — велика петля
    s += text(235, 92, "ВЕЛИКА петля — багато наводки", 12.5, ORANGE, "middle", "bold")
    s += field(70, 110, 330, 200)
    s += rect(120, 140, 230, 130, "none", PURPLE, 3)
    s += text(235, 205, "велика A", 12, PURPLE, "middle", "bold", "italic")
    s += text(235, 290, "Uнав велике", 11, ORANGE, "middle", "bold")
    s += text(122, 132, "сигнал →", 9, INK, "start")
    s += text(122, 282, "← назад", 9, INK, "start")

    # стрілка
    s += arrow(415, 200, 470, 200, INK, 2.6)
    s += text(442, 188, "притисни", 9.5, INK, "middle", "bold")

    # ПРАВО — мала петля
    s += text(700, 92, "МАЛА петля — наводки майже нема", 12.5, GREEN, "middle", "bold")
    s += field(540, 110, 360, 200)
    # два проводи майже впритул
    s += line(580, 150, 860, 150, INK, 2.6)
    s += line(580, 162, 860, 162, INK, 2.6)
    s += line(860, 150, 860, 162, INK, 2.6)
    s += line(580, 150, 580, 162, INK, 2.6)
    s += text(720, 142, "сигнал →", 9, INK, "middle")
    s += text(720, 178, "← назад (поруч)", 9, INK, "middle")
    s += text(720, 250, "A ≈ 0  →  Uнав ≈ 0", 12, GREEN, "middle", "bold", "italic")

    s += rect(220, 330, 500, 56, "#f4f5f7", INK, 1.6, 9)
    s += text(W / 2, 354, "Правило: прямий і зворотний провід тримай разом —", 11.5, INK, "middle", "bold")
    s += text(W / 2, 373, "не розводь сигнал і «землю» широкою петлею.", 11, INK, "middle", "bold")
    save("fig-9-5-2-loop-area.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.6 — Спільний шлях повернення: земляні петлі.  Рис. 9.6.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.6.1 — спільний імпеданс: чужий струм робить напругу на «землі» ──────
def fig_common_impedance():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Спільний імпеданс: чужий струм перетворює «землю» на джерело завади",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "коли сильний і слабкий струми течуть назад одним дротом, його крихітний опір (за §1.3.2) дає падіння напруги, що домішується до сигналу",
              10.5, GREY, "middle", style="italic")

    # верх: сильне навантаження (мотор) із великим струмом
    s += rect(110, 96, 150, 60, "#fbe9e1", RED, 2, 8)
    s += text(185, 122, "силове навантаження", 10.5, RED, "middle", "bold")
    s += text(185, 140, "(мотор, велике Iсил)", 9.5, INK, "middle")
    # сигнальний блок
    s += rect(110, 196, 150, 60, "#eef7f0", GREEN, 2, 8)
    s += text(185, 222, "слабкий сигнал", 10.5, GREEN, "middle", "bold")
    s += text(185, 240, "(давач, малий Iсиг)", 9.5, INK, "middle")
    # вхід (приймач сигналу)
    s += rect(620, 196, 150, 60, "#eef2fb", BLUE, 2, 8)
    s += text(695, 226, "вхід (АЦП)", 11, BLUE, "middle", "bold")

    # верхні прямі проводи до спільного вузла A
    nodeA = (560, 126)
    nodeB = (560, 226)
    s += line(260, 126, nodeA[0], nodeA[1], RED, 3)
    s += line(260, 226, nodeB[0], nodeB[1], GREEN, 3)
    s += line(770, 226, 800, 226, BLUE, 3)
    s += line(800, 226, 800, 126, BLUE, 2.4)
    s += line(800, 126, nodeA[0], nodeA[1], BLUE, 2.4)

    # СПІЛЬНИЙ зворотний провід з опором Rg від вузла до «справжньої» землі
    s += line(nodeA[0], nodeA[1], 560, 196, INK, 3)        # звести обидва на одну точку
    jx = 560
    s += circle(jx, 196, 4, INK, INK, 1)
    s += text(jx + 10, 188, "тут струми зливаються", 9.5, INK, "start", "bold")
    s += line(jx, 196, jx, 300, PURPLE, 3)
    s += resistor(jx - 11, 300 + 33, w=22, h=44, label="")
    # повернути на горизонталь
    s += text(jx + 16, 326, "Rg — опір спільного зворотного дроту", 10, PURPLE, "start", "bold")
    s += gnd(jx, 392, INK)
    s += text(jx, 410, "істинна земля (0 В)", 9.6, GREY, "middle", "bold")

    # струми по спільному дроту
    s += arrow(jx + 30, 230, jx + 30, 290, PURPLE, 2.4)
    s += text(jx + 36, 262, "Iсил + Iсиг", 10, PURPLE, "start", "bold")

    # напруга, що з'являється
    s += rect(640, 296, 280, 96, "#fff6ee", ORANGE, 1.7, 10)
    s += text(780, 318, "Uпом = (Iсил+Iсиг)·Rg", 13, INK, "middle", "bold")
    s += text(780, 340, "ця напруга піднімає «землю» сигналу", 9.8, INK, "middle")
    s += text(780, 358, "над істинним нулем — і додається", 9.8, INK, "middle")
    s += text(780, 376, "просто до корисного сигналу", 9.8, ORANGE, "middle", "bold")
    save("fig-9-6-1-common-impedance.svg", s)


# ── Рис. 9.6.2 — земляна петля: дві «землі» з різницею потенціалів ────────────
def fig_ground_loop():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 30, "Земляна петля: два прилади заземлені в різних точках",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "«земля» в різних розетках — НЕ той самий потенціал; різниця Uзем жене струм по екрану/землі сигналу й домішується до нього",
              11, GREY, "middle", style="italic")

    # прилад 1 (ліворуч) і прилад 2 (праворуч)
    s += rect(90, 130, 160, 110, "#eef2fb", BLUE, 2, 10)
    s += text(170, 122, "прилад A", 11, BLUE, "middle", "bold")
    s += rect(690, 130, 160, 110, "#eef2fb", BLUE, 2, 10)
    s += text(770, 122, "прилад B", 11, BLUE, "middle", "bold")

    # сигнальний кабель між ними (сигнал + екран)
    s += line(250, 165, 690, 165, GREEN, 3)
    s += text(470, 156, "сигнал", 10, GREEN, "middle", "bold")
    s += line(250, 200, 690, 200, COPPER, 3)
    s += text(470, 216, "екран / земля сигналу", 10, COPPER, "middle", "bold")

    # кожен прилад заземлений у свою розетку
    s += line(170, 240, 170, 300, INK, 2.4)
    s += gnd(170, 300, INK)
    s += text(170, 332, "земля розетки 1", 9.6, GREY, "middle", "bold")
    s += line(770, 240, 770, 300, INK, 2.4)
    s += gnd(770, 300, INK)
    s += text(770, 332, "земля розетки 2", 9.6, GREY, "middle", "bold")

    # різниця потенціалів між двома землями (через проводку будівлі)
    s += line(190, 312, 750, 312, GREY, 2, "5,4")
    s += circle(190, 312, 14, "#fff", ORANGE, 2)
    s += text(190, 317, "~", 14, ORANGE, "middle", "bold")
    s += text(470, 304, "Uзем — різниця «земель» (мережеві струми в проводці будівлі)",
              10, ORANGE, "middle", "bold")

    # петля струму завади: екран → прилад B → земля2 → проводка → земля1 → прилад A → екран
    s += arrow(440, 200, 360, 200, PURPLE, 2.6)
    s += text(400, 192, "Iзав по екрану", 9.6, PURPLE, "middle", "bold")
    s += text(470, 248, "ЗАМКНЕНА ПЕТЛЯ: екран + обидві землі + проводка будівлі",
              10.5, PURPLE, "middle", "bold")

    s += rect(180, 356, 580, 56, "#f4f5f7", INK, 1.6, 10)
    s += text(W / 2, 378, "Розрив петлі: заземлюй екран лише з ОДНОГО кінця (§1.9.7),",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 398, "або розв'яжи входи (диференційний прийом, оптрон, трансформатор).",
              11, INK, "middle", "bold")
    save("fig-9-6-2-ground-loop.svg", s)


# ── Рис. 9.6.3 — зірка проти ланцюжка: як розводити «землю» ────────────────────
def fig_star_ground():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 30, "Розводка «землі»: ланцюжок (погано) проти зірки (добре)",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "у ланцюжку струм одного блока тече крізь землю іншого; у зірці кожен блок має власний шлях до спільної точки",
              11, GREY, "middle", style="italic")

    # ЛІВО — ланцюжок (daisy-chain)
    s += text(235, 92, "ЛАНЦЮЖОК — спільний імпеданс", 12, ORANGE, "middle", "bold")
    y0 = 150
    s += line(70, y0, 400, y0, PURPLE, 3)
    pts = [(120, "A"), (220, "B"), (330, "C")]
    for x, lab in pts:
        s += rect(x - 22, y0 - 56, 44, 36, "#eef2fb", BLUE, 1.8, 6)
        s += text(x, y0 - 33, lab, 11, BLUE, "middle", "bold")
        s += line(x, y0 - 20, x, y0, INK, 2)
    s += gnd(400, y0, INK)
    # ділянки опору між блоками
    for x0, x1 in [(70, 120), (120, 220), (220, 330)]:
        s += text((x0 + x1) / 2, y0 + 16, "r", 10, PURPLE, "middle", "bold", "italic")
    s += arrow(95, y0 + 30, 380, y0 + 30, PURPLE, 2)
    s += text(235, y0 + 48, "струм C тече крізь землю A і B → їхні нулі «їдуть»",
              9.6, ORANGE, "middle", "bold")

    # ПРАВО — зірка (star / single point)
    s += text(700, 92, "ЗІРКА — спільна точка", 12, GREEN, "middle", "bold")
    star = (700, 200)
    s += circle(star[0], star[1], 5, INK, INK, 1)
    s += gnd(star[0], star[1] + 8, INK)
    s += text(star[0], star[1] + 44, "одна спільна точка «землі»", 9.6, GREY, "middle", "bold")
    for ang, lab in [(-130, "A"), (-90, "B"), (-50, "C")]:
        ex = star[0] + 120 * math.cos(math.radians(ang))
        ey = star[1] + 120 * math.sin(math.radians(ang))
        s += line(star[0], star[1], ex, ey, GREEN, 2.4)
        s += rect(ex - 20, ey - 18, 40, 34, "#eef2fb", BLUE, 1.8, 6)
        s += text(ex, ey + 4, lab, 11, BLUE, "middle", "bold")
    s += text(700, 130, "кожен блок — власний шлях, струми не змішуються",
              9.6, GREEN, "middle", "bold")

    s += rect(230, 330, 480, 42, "#f4f5f7", INK, 1.6, 9)
    s += text(W / 2, 356, "Силову й сигнальну «землю» зводь в одну точку — і нарізно до неї.",
              11.5, INK, "middle", "bold")
    save("fig-9-6-3-star-ground.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.7 — Екран у дії: клітка Фарадея для сигналу.  Рис. 9.7.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.7.1 — екран перехоплює E-поле; заземлений з одного кінця ───────────
def fig_shield_action():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Екран у дії: метал навколо сигналу перехоплює поле (з §1.1.8)",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "силові лінії E з джерела завади обриваються на провідному екрані; всередині поля майже нема, тож сигнальна жила «у тіні»",
              10.5, GREY, "middle", style="italic")

    # джерело завади
    s += line(120, 100, 760, 100, RED, 4)
    s += text(120, 90, "джерело завади (E-поле)", 11, RED, "start", "bold")
    for x in range(170, 741, 70):
        s += arrow(x, 108, x, 150, GREEN, 1.5, "5,3")

    # екран — труба (метал) із заземленням з одного кінця
    s += rect(150, 156, 600, 70, "none", IRON, 3, 10)
    s += text(450, 148, "екран (металева оплітка/фольга)", 10.5, IRON, "middle", "bold")
    # лінії E обриваються на екрані (стрілки впираються у верх труби)
    # сигнальна жила всередині
    s += line(180, 191, 720, 191, COPPER, 3)
    s += text(450, 211, "сигнальна жила — поля майже нема", 10, GREEN, "middle", "bold")

    # заземлення екрана з ОДНОГО кінця
    s += line(150, 226, 150, 300, IRON, 2.6)
    s += gnd(150, 300, IRON)
    s += text(150, 332, "екран заземлено ТУТ (один кінець)", 9.6, IRON, "middle", "bold")
    # інший кінець — НЕ заземлено (хрестик)
    s += line(750, 226, 750, 270, IRON, 2.0, "5,4")
    s += line(742, 278, 758, 294, ORANGE, 2.4)
    s += line(758, 278, 742, 294, ORANGE, 2.4)
    s += text(750, 312, "інший кінець — НЕ заземлювати", 9.6, ORANGE, "middle", "bold")
    s += text(750, 328, "(інакше — земляна петля §1.9.6)", 8.8, GREY, "middle")

    # стікання заряду в землю
    s += arrow(300, 168, 220, 285, ORANGE, 1.8, "4,3")
    s += text(360, 250, "наведений заряд стікає в землю", 9.5, ORANGE, "start", "bold")

    s += rect(210, 356, 520, 64, "#f4f5f7", INK, 1.6, 10)
    s += text(W / 2, 378, "Від ЄМНІСНОЇ (E) наводки: заземлюй екран з ОДНОГО кінця.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 398, "Від МАГНІТНОЇ (B): екран має сам бути зворотним провідником",
              11, INK, "middle", "bold")
    s += text(W / 2, 414, "(коаксіал — струм назад тече по екрані; деталі §1.9.8).",
              10, GREY, "middle")
    save("fig-9-7-1-shield-action.svg", s)


# ── Рис. 9.7.2 — куди вмикати екран: один кінець / коаксіал / помилка ──────────
def fig_shield_grounding():
    W, H = 940, 410
    s = header(W, H)
    s += text(W / 2, 30, "Де з'єднувати екран із землею: три випадки",
              19, INK, "middle", "bold")
    s += text(W / 2, 52, "правило залежить від того, з чим боремося — з електричним полем, з магнітним, чи з обома",
              11, GREY, "middle", style="italic")

    def case(x0, title, tcol):
        out = rect(x0, 84, 280, 250, "#ffffff", tcol, 1.8, 10)
        out += text(x0 + 140, 108, title, 12, tcol, "middle", "bold")
        return out

    # 1) один кінець — від E
    s += case(40, "Один кінець → від E-поля", GREEN)
    s += rect(70, 150, 220, 16, "none", IRON, 2.4, 5)
    s += line(90, 158, 270, 158, COPPER, 2.4)
    s += line(70, 166, 70, 210, IRON, 2.2)
    s += gnd(70, 210, IRON)
    s += line(290, 166, 290, 196, IRON, 1.8, "5,4")
    s += text(180, 240, "екран ловить E,", 10, INK, "middle", "bold")
    s += text(180, 256, "заряд стікає в землю", 10, INK, "middle")
    s += text(180, 280, "✓ немає земляної петлі", 10, GREEN, "middle", "bold")
    s += text(180, 300, "(тиха аналогова лінія)", 9.3, GREY, "middle")

    # 2) коаксіал — від E і B (екран = зворотний провід)
    s += case(330, "Коаксіал → від E і B", BLUE)
    s += rect(360, 150, 220, 16, "none", IRON, 2.4, 5)
    s += line(380, 158, 560, 158, COPPER, 2.4)
    s += line(360, 166, 360, 210, IRON, 2.2)
    s += gnd(360, 210, IRON)
    s += line(580, 166, 580, 210, IRON, 2.2)
    s += gnd(580, 210, IRON)
    s += arrow(470, 158, 410, 158, GREEN, 2)        # сигнал туди
    s += arrow(420, 158 + 0, 470, 158, GREEN, 0)    # (для балансу)
    s += text(470, 240, "струм назад тече", 10, INK, "middle", "bold")
    s += text(470, 256, "по екрані поруч із жилою", 10, INK, "middle")
    s += text(470, 280, "✓ мала петля → від B теж", 10, BLUE, "middle", "bold")
    s += text(470, 300, "(ВЧ-сигнали, обидва кінці)", 9.3, GREY, "middle")

    # 3) помилка — обидва кінці на низькій частоті
    s += case(620, "Обидва кінці (НЧ) → помилка", ORANGE)
    s += rect(650, 150, 220, 16, "none", IRON, 2.4, 5)
    s += line(670, 158, 850, 158, COPPER, 2.4)
    s += line(650, 166, 650, 210, IRON, 2.2)
    s += gnd(650, 210, IRON)
    s += line(870, 166, 870, 210, IRON, 2.2)
    s += gnd(870, 210, IRON)
    s += arrow(760, 200, 690, 200, PURPLE, 2.2)
    s += text(760, 196, "Iпетлі", 9, PURPLE, "middle", "bold")
    s += text(760, 240, "дві землі ≠ один потенціал", 9.6, INK, "middle", "bold")
    s += text(760, 256, "→ струм по екрану", 9.6, INK, "middle")
    s += text(760, 280, "✗ земляна петля, гул 50 Гц", 9.6, ORANGE, "middle", "bold")

    s += rect(220, 356, 500, 42, "#f4f5f7", INK, 1.6, 9)
    s += text(W / 2, 382, "НЧ-аналог: один кінець. ВЧ/коаксіал: обидва. Ніколи — «навмання».",
              11.5, INK, "middle", "bold")
    save("fig-9-7-2-shield-grounding.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.8 — Вита пара: геометрія проти наводок.  Рис. 9.8.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.8.1 — звивання ділить петлю й перевертає знак наводки ──────────────
def fig_twisted_pair():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Вита пара: звивання розбиває велику петлю на малі з протилежним знаком",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "у сусідніх півскрутках поле пронизує петлю «з різних боків», тож наведені ЕРС майже однакові й протилежні — і гасять одна одну",
              10.5, GREY, "middle", style="italic")

    # фон поля
    for gx in range(110, 831, 36):
        for gy in range(110, 200, 30):
            s += circle(gx, gy, 1.8, GREEN, GREEN, 1)
    s += text(470, 100, "однорідне змінне поле B (з площини)", 10, GREEN, "middle", "bold", "italic")

    # ВЕРХ: пряма пара з великою петлею (погано)
    s += text(110, 232, "ПРЯМА пара — велика петля:", 11.5, ORANGE, "start", "bold")
    yA, yB = 150, 178
    s += line(150, yA, 760, yA, BLUE, 2.6)
    s += line(150, yB, 760, yB, RED, 2.6)
    s += line(760, yA, 760, yB, INK, 2.0)
    s += text(455, 168, "наводка з усієї площі складається", 9.6, ORANGE, "middle", "bold")

    # НИЗ: звита пара (добре) — синусоїдні переплетіння
    s += text(110, 268, "ЗВИТА пара — петлі чергуються знаком:", 11.5, GREEN, "start", "bold")
    yc = 330
    amp = 26
    n = 8
    aw = 610
    a = []
    b = []
    for i in range(241):
        t = i / 240.0
        x = 150 + t * aw
        ph = 2 * math.pi * n * t
        a.append((x, yc - amp * math.sin(ph)))
        b.append((x, yc + amp * math.sin(ph)))
    s += polyline(a, BLUE, 2.6)
    s += polyline(b, RED, 2.6)
    # позначити чергування знаків + / − у вічках
    seg = aw / n
    for kk in range(n):
        cx = 150 + seg * (kk + 0.5)
        sign = "+" if kk % 2 == 0 else "−"
        col = RED if kk % 2 == 0 else BLUE
        s += text(cx, yc + (4 if True else 0), sign, 13, col, "middle", "bold")
    s += text(455, 386, "сусідні вічка дають +ЕРС і −ЕРС → у сумі ≈ 0",
              10.5, GREEN, "middle", "bold")

    s += rect(220, 404, 500, 32, "#f4f5f7", INK, 1.6, 8)
    s += text(W / 2, 425, "Що дрібніший крок звивання, то повніше компенсація.",
              11.5, INK, "middle", "bold")
    save("fig-9-8-1-twisted-pair.svg", s)


# ── Рис. 9.8.2 — диференційний прийом: вита пара + віднімання входів ──────────
def fig_differential():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 30, "Чому вита пара особливо сильна з диференційним входом",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "наводка лягає на ОБИДВА проводи однаково (спільний сигнал); приймач бере РІЗНИЦЮ — і спільна наводка зникає",
              11, GREY, "middle", style="italic")

    # джерело сигналу зліва (диференційне)
    s += circle(110, 160, 16, "#fff", GREEN, 2)
    s += text(110, 165, "Д", 12, GREEN, "middle", "bold")
    s += text(110, 130, "давач", 9.5, INK, "middle")

    # дві лінії (вита пара) до приймача
    def twist(y0, col):
        pts = []
        for i in range(201):
            t = i / 200.0
            x = 140 + t * 540
            pts.append((x, y0 - 8 * math.sin(2 * math.pi * 9 * t)))
        return polyline(pts, col, 2.4)
    s += twist(150, BLUE)
    s += twist(210, RED)
    s += text(410, 120, "наводка однакова на ОБИДВА проводи (синфазно)", 10, ORANGE, "middle", "bold")
    for x in range(200, 621, 70):
        s += arrow(x, 96, x, 134, ORANGE, 1.5, "5,3")

    # приймач: різницевий підсилювач
    s += polygon([(700, 130), (700, 230), (790, 180)], "#eef2fb", INK, 2)
    s += text(728, 168, "+", 14, RED, "middle", "bold")
    s += text(728, 200, "−", 14, BLUE, "middle", "bold")
    s += line(680, 150, 700, 150, RED, 2.4)
    s += line(680, 210, 700, 210, BLUE, 2.4)
    s += line(790, 180, 850, 180, GREEN, 2.6)
    s += text(850, 174, "вихід", 10, GREEN, "start", "bold")
    s += text(745, 252, "бере РІЗНИЦЮ (+) − (−)", 10.5, INK, "middle", "bold")

    # підпис-висновок
    s += rect(180, 300, 580, 100, "#eef7f0", GREEN, 1.7, 10)
    s += text(W / 2, 324, "Корисний сигнал іде як РІЗНИЦЯ проводів — він зберігається.", 11.5, INK, "middle", "bold")
    s += text(W / 2, 346, "Наводка лягає на обидва ОДНАКОВО (синфазно) — різниця її ВИДАЛЯЄ.", 11.5, INK, "middle", "bold")
    s += text(W / 2, 372, "Звивання робить наводку справді однаковою на обох; різницевий вхід її відкидає.",
              10.5, GREEN, "middle", "bold")
    s += text(W / 2, 390, "Так працюють USB, Ethernet, CAN, RS-485, мікрофонні лінії. (Докладно — у Модулі 6.)",
              9.6, GREY, "middle", "italic")
    save("fig-9-8-2-differential.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.9.9 — Полювання на заваду з осцилографом.  Рис. 9.9.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 9.9.1 — впізнати заваду за формою: гул, імпульси, трава ───────────────
def fig_signatures():
    W, H = 960, 470
    s = header(W, H)
    s += text(W / 2, 30, "Упізнати заваду за формою на екрані осцилографа (з §1.6.7)",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "форма й частота завади видають її джерело: плавний гул — мережа; рідкі піки — комутація; суцільна «трава» — широкосмуговий шум",
              10.5, GREY, "middle", style="italic")

    rnd = random.Random(21)

    def scr(x0, y0, w, h, title, tcol):
        out = rect(x0, y0, w, h, "#0d1f17", INK, 1.8, 8)
        sx, sy, sw, sh = x0 + 12, y0 + 28, w - 24, h - 44
        for j in range(1, 6):
            out += line(sx, sy + sh * j / 6, sx + sw, sy + sh * j / 6, "#143b2b", 1)
        for i in range(1, 8):
            out += line(sx + sw * i / 8, sy, sx + sw * i / 8, sy + sh, "#143b2b", 1)
        out += line(sx, sy + sh / 2, sx + sw, sy + sh / 2, "#1f5740", 1.2)
        out += text(x0 + w / 2, y0 + 18, title, 11.5, tcol, "middle", "bold")
        return out, (sx, sy, sw, sh)

    # 1) гул 50 Гц — чистий повільний синус
    body, (sx, sy, sw, sh) = scr(40, 86, 270, 170, "гул мережі 50 Гц", "#cfe9d8")
    s += body
    s += polyline(_sine(sx, sy + sh / 2, sw, sh * 0.34, 2.0, 0.0), "#ffd9b3", 2.0)
    s += text(175, 268, "плавний синус, період 20 мс", 10, ORANGE, "middle", "bold")
    s += text(175, 284, "→ мережа: проводка, БЖ, ємнісна наводка", 9.3, GREY, "middle")

    # 2) імпульсні викиди — рідкі гострі піки
    body, (sx, sy, sw, sh) = scr(345, 86, 270, 170, "імпульсні викиди", "#cfe9d8")
    s += body
    base = [(sx + sw * i / 200, sy + sh / 2) for i in range(201)]
    base = [(x, y + rnd.gauss(0, 2)) for (x, y) in base]
    # вставити кілька гострих піків
    for frac in (0.18, 0.5, 0.78):
        idx = int(frac * 200)
        base[idx] = (base[idx][0], sy + sh * 0.12)
        base[idx + 1] = (base[idx + 1][0], sy + sh * 0.9)
    s += polyline(base, "#ffd9b3", 1.8)
    s += text(480, 268, "рідкі гострі піки, прив'язані до подій", 10, ORANGE, "middle", "bold")
    s += text(480, 284, "→ комутація: реле, мотор, ключі, іскри", 9.3, GREY, "middle")

    # 3) трава — суцільний широкосмуговий шум
    body, (sx, sy, sw, sh) = scr(650, 86, 270, 170, "«трава» (broadband)", "#cfe9d8")
    s += body
    base = [(sx + sw * i / 240, sy + sh / 2 + rnd.gauss(0, sh * 0.16)) for i in range(241)]
    s += polyline(base, "#ffd9b3", 1.5)
    s += text(785, 268, "суцільна товста смуга без форми", 10, ORANGE, "middle", "bold")
    s += text(785, 284, "→ тепловий/дробовий шум, ВЧ-сміття", 9.3, GREY, "middle")

    # нижній блок — алгоритм полювання
    s += rect(60, 310, 840, 150, "#f4f5f7", INK, 1.8, 12)
    s += text(W / 2, 334, "Як полювати: міняй одне — дивись на екран", 13, INK, "middle", "bold")
    steps = [
        "1) Замкни вхід щупа накоротко (на його ж землю) — якщо «бруд» зник, він наводився; якщо лишився, він у приладі.",
        "2) Виміряй ПЕРІОД завади: 20 мс → 50 Гц мережа; 16.7 мс → 60 Гц; синхронна з ШІМ/мотором → звідти.",
        "3) Поворуши/вийми кабелі по черзі, вимикай по одному споживачу (мотор, БЖ, лампу) — стеж, коли впаде амплітуда.",
        "4) Стисни сигнальну петлю, скороти проводи, додай екран/витку пару — і дивись, що саме допомогло.",
    ]
    yy = 356
    for st in steps:
        s += text(78, yy, st, 10.3, INK, "start")
        yy += 24
    s += text(78, yy + 2, "Тригер по фронту (§1.6.7) «зупиняє» повторювану заваду — так її видно стабільно, а не як розмиту пляму.",
              10.3, GREEN, "start", "bold")
    save("fig-9-9-1-signatures.svg", s)


# ── Рис. 9.9.2 — усереднення витягує сигнал із шуму (σ/√N) ─────────────────────
def fig_averaging():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 30, "Остання зброя проти шуму: усереднення (режим Average)",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "шум випадковий і в середньому нульовий, сигнал — ні; усереднивши N однакових розгорток, шум спадає як 1/√N, а сигнал лишається",
              10.5, GREY, "middle", style="italic")

    rnd = random.Random(2)

    def scr(x0, title, sigma, navg):
        out = rect(x0, 86, 410, 210, "#0d1f17", INK, 1.8, 8)
        sx, sy, sw, sh = x0 + 14, 100, 382, 168
        for j in range(1, 6):
            out += line(sx, sy + sh * j / 6, sx + sw, sy + sh * j / 6, "#143b2b", 1)
        mid = sy + sh / 2
        # «істинний» сигнал — невеликий синус
        sig = _sine(sx, mid, sw, sh * 0.18, 2.0, 0.0)
        # середнє N зашумлених копій
        avg = []
        for i in range(len(sig)):
            acc = 0.0
            for _ in range(navg):
                acc += rnd.gauss(0, sigma)
            avg.append((sig[i][0], sig[i][1] + acc / navg))
        out += polyline(avg, "#ffd9b3", 1.8)
        out += polyline(sig, GREEN, 1.5, "5,3")
        out += text(x0 + 205, 110, title, 12, "#cfe9d8", "middle", "bold")
        return out

    s += scr(40, "одна розгортка (N = 1)", 26, 1)
    s += scr(490, "усереднено N = 64", 26, 64)
    s += arrow(455, 190, 488, 190, INK, 2.6)

    s += rect(250, 312, 440, 76, "#eef2fb", BLUE, 1.7, 10)
    s += text(W / 2, 336, "шум ↓ як 1/√N", 14, INK, "middle", "bold")
    s += text(W / 2, 358, "N = 64 → шум менший у 8 разів (√64 = 8)", 11, INK, "middle")
    s += text(W / 2, 378, "працює лише для ПОВТОРЮВАНОГО сигналу з тригером", 10, GREY, "middle", "italic")
    save("fig-9-9-2-averaging.svg", s)


# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # 1.9.1
    fig_noise_vs_interference()
    fig_snr()
    # 1.9.2
    fig_thermal_mechanism()
    fig_thermal_formula()
    fig_bandwidth()
    # 1.9.3
    fig_shot_noise()
    fig_one_over_f()
    # 1.9.4
    fig_capacitive_coupling()
    fig_capacitive_cure()
    # 1.9.5
    fig_inductive_coupling()
    fig_loop_area()
    # 1.9.6
    fig_common_impedance()
    fig_ground_loop()
    fig_star_ground()
    # 1.9.7
    fig_shield_action()
    fig_shield_grounding()
    # 1.9.8
    fig_twisted_pair()
    fig_differential()
    # 1.9.9
    fig_signatures()
    fig_averaging()
    print("OK — усі фігури згенеровано")
