# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для ⚙️-вставки до теми §3.4.5 — «CORDIC: синус, косинус і
atan2 самими зсувами й додаваннями». Окремий скрипт (головний figs.py не чіпаємо).
Чистий Python, без залежностей. Вивід → ./img/.
Імена файлів: fig-17-5a-cordic-k-<slug>.svg (slug «cordic-» відрізняє від
fig-17-5a-k-*.svg вставки про фіксовану кому). Підписи — Рис. 3.4.5a.k.

Стиль (AUTHORING §9) узгоджений із figs.py розділу: білий фон; додатне/«1»
червоний, від'ємне/«0» синій; правильний результат/ціль зелений; стрілки через
marker; шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділу
(розділи не ділять коду, щоб loop'и не конфліктували).
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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=15, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def dot(cx, cy, r, fill=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def arc(cx, cy, r, a0, a1, color=INK, w=2, dash=None):
    """Дуга в екранних координатах (y вниз). Кути в радіанах, проти годинника
    в математичному сенсі (екран дзеркалить по вертикалі)."""
    x0 = cx + r * math.cos(a0)
    y0 = cy - r * math.sin(a0)
    x1 = cx + r * math.cos(a1)
    y1 = cy - r * math.sin(a1)
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 0 if a1 > a0 else 1   # екранний y перевернутий
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} {sweep} {x1:.1f},{y1:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 3.4.5a.1 — один крок: обертання вектора на ±atan(2^-i) самим зсувом ──
def fig_one_step():
    W, H = 940, 590
    s = header(W, H)
    s += text(W / 2, 34, "Один крок CORDIC: повернути вектор на крихітний кут — без множень",
              21, INK, "middle", "bold")
    s += text(W / 2, 56, "точне обертання вимагає cos/sin; CORDIC бере «майже-обертання», де множники — це зсуви 2⁻ⁱ, а ще одне множення прибирають геть",
              12.3, GREY, "middle", style="italic")

    # ── ліва панель: справжнє обертання (дорого) ───────────────────────────
    cx, cy, R = 250, 330, 150
    s += text(cx, 96, "Справжнє обертання на кут φ", 15, INK, "middle", "bold")
    s += text(cx, 116, "(те, що хочемо)", 12.5, GREY, "middle", style="italic")
    # осі
    s += arrow(cx - R - 16, cy, cx + R + 20, cy, INK, 1.6)
    s += arrow(cx, cy + R + 16, cx, cy - R - 22, INK, 1.6)
    s += text(cx + R + 24, cy + 4, "x", 13, INK, "start")
    s += text(cx + 10, cy - R - 24, "y", 13, INK, "start")
    s += circle(cx, cy, R, "none", FAINT, 1.4, "4 4")
    # вхідний вектор під кутом a0
    a0 = math.radians(20)
    a1 = math.radians(20 + 30)
    vx0, vy0 = cx + R * math.cos(a0), cy - R * math.sin(a0)
    vx1, vy1 = cx + R * math.cos(a1), cy - R * math.sin(a1)
    s += arrow(cx, cy, vx0, vy0, BLUE, 3.0)
    s += text(vx0 + 8, vy0 + 4, "(x, y)", 13, BLUE, "start", "bold")
    s += arrow(cx, cy, vx1, vy1, RED, 3.0)
    s += text(vx1 + 6, vy1 - 6, "(x′, y′)", 13, RED, "start", "bold")
    s += arc(cx, cy, 54, a0, a1, INK, 2.0)
    s += text(cx + 64 * math.cos((a0 + a1) / 2), cy - 64 * math.sin((a0 + a1) / 2) + 4,
              "φ", 15, INK, "middle", "bold")
    # формула справжнього обертання
    s += rect(cx - R - 6, cy + R + 30, 2 * R + 26, 64, "#fdeceb", RED, 1.6, 6)
    s += mono(cx - R + 2, cy + R + 52, "x′ = x·cos φ − y·sin φ", 12.5, INK, "start")
    s += mono(cx - R + 2, cy + R + 72, "y′ = x·sin φ + y·cos φ", 12.5, INK, "start")
    s += text(cx, cy + R + 90, "чотири множення на кожен кут — задорого без FPU", 11.5, RED, "middle", style="italic")

    # ── права панель: крок CORDIC (псевдо-обертання зсувом) ─────────────────
    cx2 = 690
    s += text(cx2, 96, "Крок CORDIC на kᵢ = atan(2⁻ⁱ)", 15, INK, "middle", "bold")
    s += text(cx2, 116, "(те, що рахуємо)", 12.5, GREY, "middle", style="italic")
    s += arrow(cx2 - R - 16, cy, cx2 + R + 20, cy, INK, 1.6)
    s += arrow(cx2, cy + R + 16, cx2, cy - R - 22, INK, 1.6)
    s += text(cx2 + R + 24, cy + 4, "x", 13, INK, "start")
    s += text(cx2 + 10, cy - R - 24, "y", 13, INK, "start")
    s += circle(cx2, cy, R, "none", FAINT, 1.4, "4 4")
    # для i=0 кут atan(1)=45°; для наочності беремо i=1 → atan(0.5)=26.57°
    aa0 = math.radians(20)
    katan = math.degrees(math.atan(0.5))  # ≈ 26.57°
    aa1 = math.radians(20 + katan)
    # вектор до: трохи коротший, бо псевдо-обертання його ще й видовжує
    Rin = R / math.sqrt(1 + 0.5 * 0.5)    # щоб «після» лягло на коло R
    wx0, wy0 = cx2 + Rin * math.cos(aa0), cy - Rin * math.sin(aa0)
    wx1, wy1 = cx2 + R * math.cos(aa1), cy - R * math.sin(aa1)
    s += arrow(cx2, cy, wx0, wy0, BLUE, 3.0)
    s += text(wx0 - 6, wy0 + 16, "(x, y)", 13, BLUE, "end", "bold")
    s += arrow(cx2, cy, wx1, wy1, RED, 3.0)
    s += text(wx1 + 6, wy1 - 6, "(x′, y′)", 13, RED, "start", "bold")
    s += arc(cx2, cy, 54, aa0, aa1, GREEN, 2.2)
    s += text(cx2 + 70 * math.cos((aa0 + aa1) / 2), cy - 70 * math.sin((aa0 + aa1) / 2) + 4,
              "kᵢ", 14, GREEN, "middle", "bold")
    # видовження: пунктир від кінчика «після» до кола меншого радіуса
    s += line(wx1, wy1, cx2 + Rin * math.cos(aa1), cy - Rin * math.sin(aa1), GREY, 1.4, "3 3")
    s += text(cx2 + (R + 8) * math.cos(aa1), cy - (R + 8) * math.sin(aa1), "вектор", 10.5, GREY, "start")
    s += text(cx2 + (R + 8) * math.cos(aa1), cy - (R + 8) * math.sin(aa1) + 13, "ще й довшає ×Aᵢ", 10.5, GREY, "start")
    # формула кроку
    s += rect(cx2 - R - 6, cy + R + 30, 2 * R + 26, 64, "#eef9ee", GREEN, 1.8, 6)
    s += mono(cx2 - R + 2, cy + R + 52, "x′ = x ∓ (y >> i)", 13, INK, "start")
    s += mono(cx2 - R + 2, cy + R + 72, "y′ = y ± (x >> i)", 13, INK, "start")
    s += text(cx2, cy + R + 90, "лише зсуви й додавання — жодного множення", 11.5, GREEN, "middle", style="italic")

    save("fig-17-5a-cordic-1-one-step.svg", s)


# ── Рис. 3.4.5a.2 — двійковий пошук кута: ±atan(2^-i), що зменшуються ────────
def fig_angle_search():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 34, "Чому достатньо лише «+» і «−»: кут набирають половинками, що тануть",
              21, INK, "middle", "bold")
    s += text(W / 2, 56, "на кожному кроці лишок кута z штовхають до нуля фіксованим кроком kᵢ = atan(2⁻ⁱ); знак z вирішує, додати чи відняти",
              12.3, GREY, "middle", style="italic")

    # таблиця кутів атангенсів (ліворуч)
    tx, ty = 70, 110
    s += text(tx, ty - 16, "Таблиця кроків (зберігається в ПЗП):", 13.5, INK, "start", "bold")
    rows = [
        ("i", "2⁻ⁱ", "kᵢ = atan(2⁻ⁱ)"),
        ("0", "1.0", "45.000°"),
        ("1", "0.5", "26.565°"),
        ("2", "0.25", "14.036°"),
        ("3", "0.125", "7.125°"),
        ("4", "0.0625", "3.576°"),
        ("…", "…", "…"),
    ]
    rw = [44, 92, 150]
    rh = 27
    for r, row in enumerate(rows):
        yy = ty + r * rh
        fill = "#f0f4ff" if r == 0 else ("#ffffff" if r % 2 else "#fafafa")
        xx = tx
        for c, val in enumerate(row):
            s += rect(xx, yy, rw[c], rh, fill if r else "#e8eeff", INK, 1.1)
            col = INK if r else INK
            wt = "bold" if r == 0 else "normal"
            fnt = mono if (r > 0 and c < 2) else text
            s += fnt(xx + rw[c] / 2, yy + rh * 0.66, val, 12.5, col, "middle", wt)
            xx += rw[c]
    s += text(tx, ty + len(rows) * rh + 22, "кроки фіксовані наперед —", 11.5, GREY, "start", style="italic")
    s += text(tx, ty + len(rows) * rh + 38, "у циклі їх лише читають по черзі", 11.5, GREY, "start", style="italic")

    # графік збіжності лишку кута z до нуля (праворуч)
    gx, gy = 410, 120          # лівий-верх
    gw, gh = 470, 300
    target = 30.0              # шуканий кут, наприклад 30°
    # симулюємо режим обертання: z починає з target, віднімаємо ±kᵢ
    atans = [math.degrees(math.atan(2.0 ** -i)) for i in range(8)]
    z = target
    seq = [(0, z)]
    for i, k in enumerate(atans):
        d = +1 if z >= 0 else -1     # σ = sign(z)
        z = z - d * k
        seq.append((i + 1, z))
    # осі графіка: x = крок 0..8, y = кут -50..+50
    ymin, ymax = -50.0, 50.0
    def GX(i): return gx + gw * (i / 8.0)
    def GY(v): return gy + gh * (ymax - v) / (ymax - ymin)
    # сітка нуля й цілі
    s += rect(gx, gy, gw, gh, "none", FAINT, 1.4)
    s += line(gx, GY(0), gx + gw, GY(0), INK, 1.6)
    s += text(gx + gw + 6, GY(0) + 4, "0", 12, INK, "start")
    s += line(gx, GY(target), gx + gw, GY(target), GREEN, 1.4, "5 4")
    s += text(gx + 4, GY(target) - 6, "стартовий кут z₀ = 30°", 11.5, GREEN, "start", "bold")
    # вісь кроків
    for i in range(9):
        s += line(GX(i), gy + gh, GX(i), gy + gh + 5, INK, 1.2)
        s += text(GX(i), gy + gh + 19, str(i), 11, INK, "middle")
    s += text(gx + gw / 2, gy + gh + 38, "номер кроку i", 12.5, INK, "middle")
    s += text(gx - 8, gy - 10, "лишок кута z (°)", 12.5, INK, "start")
    # підписи знаків ±
    pts = [(GX(i), GY(v)) for i, v in seq]
    s += polyline(pts, BLUE, 2.6)
    for i, (xx, yy) in enumerate(pts):
        col = RED if seq[i][1] >= 0 else BLUE
        s += dot(xx, yy, 3.6, col)
    # позначити перші кілька знаків рішення
    for i in range(5):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        sign = "−" if seq[i][1] >= 0 else "+"   # z>0 → віднімаємо kᵢ
        col = RED if seq[i][1] >= 0 else BLUE
        s += text((x0 + x1) / 2, min(y0, y1) - 8, sign, 16, col, "middle", "bold")
    # рамка-висновок
    s += rect(gx, gy + gh + 50, gw, 34, "#f7f7f7", GREY, 1.4, 8)
    s += text(gx + gw / 2, gy + gh + 72,
              "Кожна половинка вдвічі менша — як двійковий пошук: 8 кроків дають ~8 правильних бітів.",
              11.6, INK, "middle")
    save("fig-17-5a-cordic-2-angle-search.svg", s)


# ── Рис. 3.4.5a.3 — два режими + посилення K (звідки беруться cos/sin/atan2) ─
def fig_modes_gain():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 34, "Два режими одного циклу — і єдина «плата» за псевдо-обертання",
              21, INK, "middle", "bold")
    s += text(W / 2, 56, "напрям рішення (за z чи за y) перемикає, що CORDIC обчислює; накопичене видовження Aᵢ зводять в одну сталу K",
              12.3, GREY, "middle", style="italic")

    # ── ліва картка: режим обертання ──────────────────────────────────────
    bx, by, bw, bh = 50, 92, 405, 250
    s += rect(bx, by, bw, bh, "#eef3ff", BLUE, 2.0, 10)
    s += text(bx + bw / 2, by + 26, "Режим обертання (rotation)", 16, BLUE, "middle", "bold")
    s += text(bx + bw / 2, by + 46, "задано кут — крутимо вектор до нього", 12, INK, "middle", style="italic")
    s += mono(bx + 22, by + 78, "σ = sign(z)          // женемо z → 0", 12.5, INK, "start")
    s += mono(bx + 22, by + 100, "x −= σ·(y >> i)", 12.5, INK, "start")
    s += mono(bx + 22, by + 122, "y += σ·(x >> i)", 12.5, INK, "start")
    s += mono(bx + 22, by + 144, "z −= σ·atan(2⁻ⁱ)", 12.5, INK, "start")
    s += line(bx + 18, by + 162, bx + bw - 18, by + 162, FAINT, 1.6)
    s += text(bx + 22, by + 184, "старт (x,y,z) = (1/K, 0, θ)  →", 12, INK, "start")
    s += mono(bx + 22, by + 206, "x → cos θ", 13, GREEN, "start", "bold")
    s += mono(bx + 175, by + 206, "y → sin θ", 13, GREEN, "start", "bold")
    s += text(bx + 22, by + 230, "один прохід дає синус і косинус відразу", 11.5, GREY, "start", style="italic")

    # ── права картка: режим векторизації ──────────────────────────────────
    cx0 = 485
    s += rect(cx0, by, bw, bh, "#fdeceb", RED, 2.0, 10)
    s += text(cx0 + bw / 2, by + 26, "Режим векторизації (vectoring)", 16, RED, "middle", "bold")
    s += text(cx0 + bw / 2, by + 46, "задано вектор — складаємо його кут", 12, INK, "middle", style="italic")
    s += mono(cx0 + 22, by + 78, "σ = −sign(y)         // женемо y → 0", 12.5, INK, "start")
    s += mono(cx0 + 22, by + 100, "x −= σ·(y >> i)", 12.5, INK, "start")
    s += mono(cx0 + 22, by + 122, "y += σ·(x >> i)", 12.5, INK, "start")
    s += mono(cx0 + 22, by + 144, "z −= σ·atan(2⁻ⁱ)", 12.5, INK, "start")
    s += line(cx0 + 18, by + 162, cx0 + bw - 18, by + 162, FAINT, 1.6)
    s += text(cx0 + 22, by + 184, "старт (x,y,z) = (x₀, y₀, 0)  →", 12, INK, "start")
    s += mono(cx0 + 22, by + 206, "z → atan2(y₀, x₀)", 13, GREEN, "start", "bold")
    s += mono(cx0 + 22, by + 228, "x → K·√(x₀² + y₀²)", 12.5, GREEN, "start", "bold")

    # ── нижня смуга: посилення K ───────────────────────────────────────────
    ky = by + bh + 26
    s += rect(50, ky, W - 100, 150, "#fff6e6", AMBER, 2.0, 10)
    s += text(W / 2, ky + 26, "Чому вектор довшає — і чому це не біда", 16, INK, "middle", "bold")
    s += text(70, ky + 52,
              "Кожне псевдо-обертання множить довжину на Aᵢ = √(1 + 2⁻²ⁱ) > 1. За багато кроків ці множники",
              12.5, INK, "start")
    s += text(70, ky + 72,
              "зливаються в одну сталу — посилення K. Воно НЕ залежить від кута, тож його знають наперед:",
              12.5, INK, "start")
    s += mono(W / 2, ky + 100, "K = Π √(1 + 2⁻²ⁱ)  ≈  1.64676   (для багатьох кроків)",
              14, AMBER, "middle", "bold")
    s += text(70, ky + 126,
              "Лікують двома способами: або стартують з x = 1/K ≈ 0.60725 (тоді cos/sin виходять уже масштабованими),",
              12, INK, "start")
    s += text(70, ky + 144,
              "або множать результат на 1/K в кінці — одне-єдине множення на весь алгоритм замість сотень.",
              12, INK, "start")
    save("fig-17-5a-cordic-3-modes-gain.svg", s)


if __name__ == "__main__":
    fig_one_step()
    fig_angle_search()
    fig_modes_gain()
    print("ch17 s5a (CORDIC) figures done.")
