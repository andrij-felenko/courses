# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §1.10.3m «Крива Пашена».
Чистий Python, без залежностей. Вивід → ./img/.
Імена файлів УНІКАЛЬНІ (префікс fig-r10-s3m-pas-*); головний figs.py розділу
не чіпається. Стиль за AUTHORING §9: білий фон, sans-serif, спільні кольори.
"""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#eef1f4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"
MONO  = "Consolas, 'DejaVu Sans Mono', monospace"


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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREY: "aGrey", GREEN: "aGreen", RED: "aRed", BLUE: "aBlue"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", font=FONT):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, sw=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(pts, color=INK, w=2.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Модель Пашена для повітря ────────────────────────────────────────────────
# U(pd) = B·(pd) / ( ln(A·pd) − ln[ ln(1 + 1/γ) ] )
# Сталі A, B — для повітря (типові підручникові значення в одиницях
# 1/(Торр·см) та В/(Торр·см)); γ — коеф. вторинної емісії (беремо 0.01).
# Це не для точного інженерного розрахунку, а для форми кривої.
A_AIR = 15.0      # 1/(Торр·см)  — насичення іонізації
B_AIR = 365.0     # В/(Торр·см)  — енергетичний масштаб
GAMMA = 0.01      # вторинна емісія з катода


def paschen_V(pd):
    """pd у Торр·см → пробивна напруга, В (None ліворуч від асимптоти)."""
    denom = math.log(A_AIR * pd) - math.log(math.log(1.0 + 1.0 / GAMMA))
    if denom <= 1e-6:
        return None
    return B_AIR * pd / denom


# ── Рис. 1.10.3m.1 — крива Пашена: U(pd) з мінімумом ─────────────────────────
def fig_curve():
    W, H = 900, 620
    s = header(W, H)
    s += text(W / 2, 34, "Крива Пашена: пробивна напруга залежить від добутку p·d", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "не від зазору окремо — а від тиск × відстань; крива має мінімум",
              13, GREY, "middle", style="italic")

    # поле графіка (лог-вісь pd)
    L, R, T, Bm = 95, W - 50, 95, H - 110
    # діапазон pd у Торр·см: 0.05 … 760  (лог10: -1.3 … 2.88)
    lo, hi = math.log10(0.05), math.log10(760.0)
    # діапазон U: 100 … 5000 В (лог10: 2 … 3.70)
    vlo, vhi = math.log10(100.0), math.log10(5000.0)

    def X(pd):
        return L + (math.log10(pd) - lo) / (hi - lo) * (R - L)

    def Y(v):
        return Bm - (math.log10(v) - vlo) / (vhi - vlo) * (Bm - T)

    # осі
    s += line(L, T, L, Bm, INK, 2)
    s += line(L, Bm, R, Bm, INK, 2)
    s += text(L - 64, T - 22, "U,  В", 14, INK, "start", "bold")
    s += text(R, Bm + 52, "p·d,  Торр·см", 14, INK, "end", "bold")
    s += text(R, Bm + 70, "(тиск × зазор)", 11.5, GREY, "end", style="italic")

    # сітка X (декади)
    for e in range(-1, 3):
        pv = 10.0 ** e
        if pv < 0.05 or pv > 760:
            continue
        x = X(pv)
        s += line(x, T, x, Bm, FAINT, 1.4)
        lab = {0.1: "0.1", 1: "1", 10: "10", 100: "100"}.get(pv, f"{pv:g}")
        s += text(x, Bm + 22, lab, 12, GREY, "middle", font=MONO)
    # сітка Y
    for v in (100, 200, 500, 1000, 2000, 5000):
        y = Y(v)
        s += line(L, y, R, y, FAINT, 1.4)
        s += text(L - 10, y + 4, f"{v}", 12, GREY, "end", font=MONO)

    # сама крива
    pts = []
    pd = 0.05
    while pd <= 760:
        v = paschen_V(pd)
        if v is not None and 100 <= v <= 5000:
            pts.append((X(pd), Y(v)))
        pd *= 1.04
    s += polyline(pts, RED, 3.2)

    # мінімум кривої (числовий)
    best_pd, best_v = None, 1e18
    pd = 0.05
    while pd <= 760:
        v = paschen_V(pd)
        if v is not None and v < best_v:
            best_v, best_pd = v, pd
        pd *= 1.002
    mx, my = X(best_pd), Y(best_v)
    s += circle(mx, my, 6, "#fff", RED, 2.6)
    s += line(mx, my, mx, Bm, GREY, 1.6, dash="4 4")
    s += text(mx, my - 14, "мінімум Пашена", 12.5, RED, "middle", "bold")
    s += text(mx, my - 30, f"≈ {best_v:.0f} В  при  p·d ≈ {best_pd:.2f}", 11.5, RED, "middle", font=MONO)

    # дві гілки — підписи
    s += text(X(0.18), Y(2600), "ліва гілка:", 12.5, BLUE, "middle", "bold")
    s += text(X(0.18), Y(2150), "замало зіткнень", 11.5, BLUE, "middle")
    s += text(X(0.18), Y(1780), "(вакуум, малий зазор)", 10.5, BLUE, "middle", style="italic")

    s += text(X(220), Y(3200), "права гілка:", 12.5, GREEN, "middle", "bold")
    s += text(X(220), Y(2650), "коротка довжина", 11.5, GREEN, "middle")
    s += text(X(220), Y(2200), "вільного пробігу", 11.5, GREEN, "middle")
    s += text(X(220), Y(1820), "(норм. тиск, великий зазор)", 10.5, GREEN, "middle", style="italic")

    # робоча точка побуту: повітря 1 атм, зазор 1 мм → pd ≈ 76 Торр·см
    px, pv = X(76.0), paschen_V(76.0)
    py = Y(pv)
    s += circle(px, py, 5.5, AMBER, INK, 2)
    s += line(px, py, px, T + 6, AMBER, 1.6, dash="3 4")
    s += text(px, T - 4, "повітря, 1 атм, 1 мм", 11.5, "#8a6a14", "middle", "bold")
    s += text(px + 6, py + 22, "це вже права гілка", 11.5, "#8a6a14", "start", "bold")
    s += text(px + 6, py + 38, "реально ≈3 кВ/мм (§1.10.3)", 11, "#8a6a14", "start", font=MONO)

    # підпис про нахил правої гілки = напруженість поля стала
    s += rect(L + 12, T + 10, 268, 64, "#fbf7ec", AMBER, 1.8, rx=8)
    s += text(L + 22, T + 30, "права гілка майже пряма:", 11.5, "#8a6a14", "start", "bold")
    s += text(L + 22, T + 47, "U/d ≈ const  (поле пробою)", 12, "#8a6a14", "start", font=MONO)
    s += text(L + 22, T + 64, "для повітря ≈ 3 кВ/мм", 12, "#8a6a14", "start", font=MONO)

    save("fig-r10-s3m-pas-curve.svg", s)


# ── Рис. 1.10.3m.2 — чому мінімум: дві протилежні тенденції ───────────────────
# Зліва: розріджене (мало молекул — мало зіткнень-розгалужень).
# Справа: щільне (багато молекул, але короткий пробіг — мало енергії на удар).
def fig_why():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому крива має мінімум: лавині потрібні і зіткнення, і розгін", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "пробій — це лавина іонізації; вона глухне з обох боків від оптимуму",
              13, GREY, "middle", style="italic")

    panels = [
        (70,  "p·d мале  (вакуум / тонкий зазор)", BLUE,
         "молекул обмаль — електрон долітає",
         "до анода, не вдаривши нікого:",
         "лавини нема → потрібна ВИЩА U"),
        (W / 2 + 18, "p·d велике  (щільне / товстий зазор)", GREEN,
         "зіткнень багато, але пробіг короткий —",
         "між ударами електрон не встигає",
         "набрати енергію → потрібна ВИЩА U"),
    ]
    pw = (W - 70 - 18) / 2 - 18
    for px, title, col, l1, l2, l3 in panels:
        s += rect(px, 86, pw, 250, FAINT, col, 2, rx=10)
        s += text(px + pw / 2, 112, title, 13.5, col, "middle", "bold")

        # «камера» з молекулами й траєкторією електрона
        cx0, cy0 = px + 30, 150
        cw, ch = pw - 60, 120
        s += rect(cx0, cy0, cw, ch, "#ffffff", GREY, 1.6, rx=6)
        # катод/анод
        s += line(cx0, cy0, cx0, cy0 + ch, BLUE, 4)
        s += line(cx0 + cw, cy0, cx0 + cw, cy0 + ch, RED, 4)
        s += text(cx0 - 2, cy0 - 6, "−", 18, BLUE, "middle", "bold")
        s += text(cx0 + cw + 2, cy0 - 6, "+", 18, RED, "middle", "bold")

        if col == BLUE:
            # мало молекул — рідкі точки, довгий вільний політ
            mols = [(0.45, 0.65), (0.72, 0.30)]
            for fx, fy in mols:
                s += circle(cx0 + fx * cw, cy0 + fy * ch, 4, "#cfd6dd", GREY, 1.2)
            # довга траєкторія без зіткнень
            s += arrow(cx0 + 6, cy0 + ch * 0.5, cx0 + cw - 6, cy0 + ch * 0.38, INK, 2.2)
            s += text(cx0 + cw / 2, cy0 + ch + 18, "довгий пробіг, ~0 ударів", 11, BLUE, "middle", style="italic")
        else:
            # багато молекул — щільна сітка точок, дуже коротка ломана
            for i in range(5):
                for j in range(3):
                    s += circle(cx0 + cw * (0.18 + i * 0.16), cy0 + ch * (0.25 + j * 0.25),
                                3.4, "#cfd6dd", GREY, 1.1)
            # коротка зигзаг-траєкторія (часті удари, малий розгін)
            zz = [(cx0 + 6, cy0 + ch * 0.5)]
            for k in range(1, 7):
                zz.append((cx0 + 6 + k * 16, cy0 + ch * (0.5 + (0.12 if k % 2 else -0.12))))
            s += polyline(zz, INK, 2.0)
            s += text(cx0 + cw / 2, cy0 + ch + 18, "короткі стрибки, слабкі удари", 11, GREEN, "middle", style="italic")

        s += text(px + pw / 2, 300, l1, 11.5, INK, "middle")
        s += text(px + pw / 2, 317, l2, 11.5, INK, "middle")
        s += text(px + pw / 2, 334, l3, 12, col, "middle", "bold")

    # стрілки до спільного висновку
    s += arrow(70 + pw / 2, 340, W / 2 - 60, 392, BLUE, 2.2)
    s += arrow(W / 2 + 18 + pw / 2, 340, W / 2 + 60, 392, GREEN, 2.2)
    s += rect(W / 2 - 250, 392, 500, 56, "#fbf7ec", AMBER, 2.2, rx=10)
    s += text(W / 2, 416, "Десь посередині — найлегший пробій: мінімум кривої Пашена", 14, INK, "middle", "bold")
    s += text(W / 2, 438, "для повітря ≈ 330 В  (нижче за цю напругу суцільне повітря не пробити жодним зазором)",
              11.5, "#8a6a14", "middle", font=MONO)

    save("fig-r10-s3m-pas-why.svg", s)


if __name__ == "__main__":
    fig_curve()
    fig_why()
    print("done.")
