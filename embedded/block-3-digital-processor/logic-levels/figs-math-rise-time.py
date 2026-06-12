# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для МАТЕМАТИЧНОЇ вставки до теми §3.1.5
(«Фронт і смуга: BW ≈ 0.35/tr, RC-модель фронту й чому швидкі фронти шумлять»).
Головний figs.py розділу НЕ чіпаємо (AUTHORING §16: фігури вставки — той самий стиль,
але тут — окремий скрипт за вимогою задачі). Чистий Python, без залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '1'/HIGH/'+' червоний, '0'/LOW/'−' синій;
«дійсне/корисне» зелене; шум/ВЧ — бурштиновий; стрілки через marker; шрифт sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 кожен скрипт самодостатній).

Нумерація підписів у вставці — Рис. 3.1.5m.k (k = 1..2).
Імена файлів на диску: fig-14-5m-<k>-<slug>.svg.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (як у figs.py розділу) ───────────────────────────────────────────
RED   = "#c0271e"   # HIGH / '1' / +
BLUE  = "#1f47b5"   # LOW / '0' / −
GREEN = "#1f8a3b"   # дійсне / корисне
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"   # шум / ВЧ-енергія
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
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


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


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def polygon(points, fill, stroke="none", sw=0, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    op = f' fill-opacity="{opacity}"' if opacity != 1.0 else ""
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    return f'<polygon points="{pts}" fill="{fill}"{op}{st}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.1.5m.1 — звідки береться множник 2.2: експонента 1−e^(−t/τ) у «сітці τ»,
# з горизонталями 10% і 90% та зчитуванням t10 = 0.105τ і t90 = 2.303τ, tr = 2.2τ.
# ─────────────────────────────────────────────────────────────────────────────
def fig1_factor_2p2():
    W, H = 760, 470
    s = header(W, H)
    # рамка осей
    x0, y0 = 96, 60          # лівий-верх області графіка
    xW, yH = 560, 300        # ширина/висота області
    yb = y0 + yH             # вісь t (низ)
    # рівні: 0..1 у частках розмаху, наносимо як y
    def Y(frac):             # frac 0..1 (0 = низ, 1 = верх повного розмаху)
        return yb - frac * yH
    # часова шкала: 0..5τ по ширині
    TMAX = 5.0
    def X(t):                # t у одиницях τ
        return x0 + (t / TMAX) * xW

    s += text(W / 2, 30, "Звідки множник 2.2: 10–90 % експоненти", 18, INK, "middle", "bold")

    # світла сітка по τ (вертикалі) і по 25% (горизонталі)
    for k in range(0, 6):
        gx = X(k)
        s += line(gx, y0, gx, yb, FAINT, 1)
        s += text(gx, yb + 20, f"{k}τ", 13, GREY, "middle")
    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = Y(f)
        s += line(x0, gy, x0 + xW, gy, FAINT, 1)

    # осі
    s += arrow(x0, yb, x0 + xW + 22, yb, INK, 2)          # t →
    s += arrow(x0, yb, x0, y0 - 18, INK, 2)               # V →
    s += text(x0 + xW + 30, yb + 5, "t", 15, INK, "start", "italic")
    s += text(x0 - 12, y0 - 24, "V / Vdd", 14, INK, "middle")

    # повний рівень (ціль) = 1.0
    s += line(x0, Y(1.0), x0 + xW, Y(1.0), GREY, 1.6, "5,4")
    s += text(x0 + xW + 6, Y(1.0) + 4, "100 %", 12, GREY, "start")

    # експонента 1 - e^(-t/τ)
    pts = []
    n = 240
    for i in range(n + 1):
        t = TMAX * i / n
        v = 1.0 - math.exp(-t)
        pts.append((X(t), Y(v)))
    s += polyline(pts, GREEN, 3.0)
    s += text(X(3.05), Y(1.0 - math.exp(-3.05)) - 10, "1 − e^(−t/τ)", 14, GREEN, "start", "bold")

    # горизонталі 10% і 90%
    for f, lab in ((0.10, "10 %"), (0.90, "90 %")):
        s += line(x0, Y(f), x0 + xW, Y(f), INK, 1.4, "2,3")
        s += text(x0 - 8, Y(f) + 4, lab, 12, INK, "end")

    # точки перетину: t10 = ln(1/0.9)=0.105τ ; t90 = ln(10)=2.303τ
    t10 = math.log(1 / 0.9)   # 0.1054
    t90 = math.log(10)        # 2.3026
    for t, f, c in ((t10, 0.10, BLUE), (t90, 0.90, RED)):
        s += line(X(t), yb, X(t), Y(f), c, 1.4, "3,3")
        s += circle(X(t), Y(f), 4.5, c, c, 1)
    s += text(X(t10), yb + 38, "t₁₀ ≈ 0.105τ", 12, BLUE, "middle", "bold")
    s += text(X(t90), yb + 38, "t₉₀ ≈ 2.303τ", 12, RED, "middle", "bold")

    # дужка tr між t10 і t90 (трохи нижче від 90%-лінії)
    yb2 = Y(0.5)
    s += arrow(X(t10), yb2, X(t90), yb2, INK, 1.8)
    s += arrow(X(t90), yb2, X(t10), yb2, INK, 1.8)
    s += rect(X((t10 + t90) / 2) - 86, yb2 - 18, 172, 26, "#ffffff", "none", 0)
    s += text(X((t10 + t90) / 2), yb2 - 1, "tr = t₉₀ − t₁₀ ≈ 2.2 τ", 14, INK, "middle", "bold")

    # бічна виноска з виведенням
    bx, by = x0 + xW + 56, y0 + 8
    s += text(bx, by, "Виведення:", 13, INK, "start", "bold")
    s += text(bx, by + 22, "0.9 = 1 − e^(−t₉₀/τ)", 12, INK, "start")
    s += text(bx, by + 40, "⇒ t₉₀ = τ·ln 10", 12, INK, "start")
    s += text(bx, by + 58, "0.1 = 1 − e^(−t₁₀/τ)", 12, INK, "start")
    s += text(bx, by + 76, "⇒ t₁₀ = τ·ln(10/9)", 12, INK, "start")
    s += line(bx, by + 90, bx + 150, by + 90, GREY, 1)
    s += text(bx, by + 110, "tr = τ·ln 9", 13, GREEN, "start", "bold")
    s += text(bx, by + 128, "ln 9 = 2.197", 12, GREEN, "start")
    s += text(bx, by + 146, "≈ 2.2", 13, GREEN, "start", "bold")

    save("fig-14-5m-1-factor-2p2.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.1.5m.2 — спектр фронту: один RC-фільтр з частотою зрізу f_BW = 1/(2πRC),
# «коліно» f_knee ≈ 0.5/tr, і чому КРУТИЙ фронт тягне за собою ВЧ-енергію (EMI).
# Логарифмічна вісь частоти; дві обвідні: повільний (вузький) і крутий (широкий).
# ─────────────────────────────────────────────────────────────────────────────
def fig2_spectrum_knee():
    W, H = 760, 470
    s = header(W, H)
    x0, y0 = 86, 70
    xW, yH = 600, 300
    yb = y0 + yH

    s += text(W / 2, 30, "Спектр фронту: чому крутіший фронт «світить» вище", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "амплітуда гармонік від частоти (лог-вісь)", 13, GREY, "middle")

    # лог-вісь частоти: декади від 1 до 1e4 (умовні, у «×f₀»)
    DECS = 4
    def X(dec):              # dec у декадах 0..DECS
        return x0 + (dec / DECS) * xW
    def Y(db):               # db: 0 (верх, повний рівень) .. -40 (низ)
        return y0 + (-db / 40.0) * yH

    # осі
    s += arrow(x0, yb, x0 + xW + 22, yb, INK, 2)
    s += arrow(x0, yb, x0, y0 - 16, INK, 2)
    s += text(x0 + xW + 30, yb + 5, "f", 15, INK, "start", "italic")
    s += text(x0 - 8, y0 - 22, "рівень", 13, INK, "middle")

    # сітка декад
    dec_labels = ["f₀", "10·f₀", "100·f₀", "1k·f₀", "10k·f₀"]
    for d in range(DECS + 1):
        gx = X(d)
        s += line(gx, y0, gx, yb, FAINT, 1)
        s += text(gx, yb + 20, dec_labels[d], 12, GREY, "middle")
    for db in (0, -10, -20, -30, -40):
        gy = Y(db)
        s += line(x0, gy, x0 + xW, gy, FAINT, 1)
        s += text(x0 - 8, gy + 4, f"{db}", 11, GREY, "end")

    # ── модель: огинаюча спектра прямокутного сигналу з обмеженим фронтом ──
    # |коеф| ~ 1/f до f_knee, далі ~ 1/f^2 (спад −40 дБ/дек) — класична апроксимація.
    # f виражаємо в декадах від f0; обвідну будуємо як −20·log10 нахилу.
    def envelope(f_knee_dec, n=260):
        pts = []
        for i in range(n + 1):
            dec = DECS * i / n
            # відносна частота у «декадах від f0»
            # перша ділянка: −20 дБ/дек (1/f); після коліна додатково ще −20 дБ/дек
            db = -20.0 * dec
            if dec > f_knee_dec:
                db += -20.0 * (dec - f_knee_dec)
            if db < -40:
                db = -40
            pts.append((X(dec), Y(db)))
        return pts

    # повільний фронт: низьке коліно (енергія швидко гасне) — синій
    knee_slow = 1.3
    s += polyline(envelope(knee_slow), BLUE, 2.8)
    # крутий фронт: коліно далеко вправо (ВЧ-енергія тримається) — бурштиновий
    knee_fast = 2.8
    fast = envelope(knee_fast)
    s += polyline(fast, AMBER, 3.0)

    # заштрихувати «зайву» ВЧ-енергію між двома обвідними праворуч від knee_slow
    band = []
    n = 160
    for i in range(n + 1):
        dec = knee_slow + (DECS - knee_slow) * i / n
        db = -20.0 * dec + (-20.0 * (dec - knee_fast) if dec > knee_fast else 0.0)
        if db < -40:
            db = -40
        band.append((X(dec), Y(db)))
    for i in range(n, -1, -1):
        dec = knee_slow + (DECS - knee_slow) * i / n
        db = -20.0 * dec + (-20.0 * (dec - knee_slow) if dec > knee_slow else 0.0)
        if db < -40:
            db = -40
        band.append((X(dec), Y(db)))
    s += polygon(band, AMBER, "none", 0, 0.16)

    # вертикалі-коліна
    s += line(X(knee_slow), Y(0) + 4, X(knee_slow), yb, BLUE, 1.4, "4,3")
    s += line(X(knee_fast), Y(0) + 4, X(knee_fast), yb, AMBER, 1.6, "4,3")
    s += text(X(knee_slow), y0 - 0, "коліно (повільний)", 11, BLUE, "middle", "bold")
    s += text(X(knee_fast), y0 - 0, "коліно (крутий)", 11, AMBER, "middle", "bold")

    # підписи обвідних
    s += text(X(0.18), Y(-3) - 6, "крутий фронт", 13, AMBER, "start", "bold")
    s += text(X(0.18), Y(-3) + 12, "(малий tr)", 12, AMBER, "start")
    s += text(X(2.55), Y(-34), "повільний", 12, BLUE, "start", "bold")
    s += text(X(2.55), Y(-34) + 16, "фронт", 12, BLUE, "start")

    # стрілка на «зайву ВЧ-енергію»
    s += arrow(X(3.55), Y(-9), X(3.15), Y(-19), AMBER, 1.8)
    s += text(X(3.6), Y(-7), "зайва ВЧ-енергія", 12, AMBER, "start", "bold")
    s += text(X(3.6), Y(-7) + 16, "→ EMI, дзвін", 12, AMBER, "start")

    # формула коліна
    s += rect(X(0.12), Y(-31) - 4, 250, 50, "#ffffff", GREY, 1.2, 6)
    s += text(X(0.12) + 12, Y(-31) + 14, "f_knee ≈ 0.5 / tr", 14, INK, "start", "bold")
    s += text(X(0.12) + 12, Y(-31) + 33, "f_BW ≈ 0.35 / tr = 1/(2πRC)", 12.5, INK, "start")

    save("fig-14-5m-2-spectrum-knee.svg", s)


if __name__ == "__main__":
    fig1_factor_2p2()
    fig2_spectrum_knee()
    print("done.")
