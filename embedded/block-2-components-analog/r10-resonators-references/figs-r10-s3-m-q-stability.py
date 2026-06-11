# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.10.3m — «Q = 10⁴…10⁶:
зв'язок добротності зі стабільністю частоти».
НЕ чіпає головний figs.py розділу. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(fig-r10-s3m-*). Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій;
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


def _axes(ox, oy, w, h, xlab, ylab):
    s = arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 18, oy + 4, xlab, 13, INK, "start", "bold")
    s += text(ox - 4, oy - h - 22, ylab, 13, INK, "middle", "bold")
    return s


# ── Рис. 2.10.3m.1 — нахил фази як «жорсткість» утримання частоти ────────────
def fig_phase_slope():
    """Дві фазові характеристики φ(f) поблизу f₀: крутий нахил (висока Q)
    і пологий (низька Q). Однакове збурення фази Δφ зсуває частоту на маленьке
    Δf за крутого нахилу і на велике — за пологого. Це механізм стабільності."""
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 34, "Чому висока Q «тримає» частоту: нахил фази = жорсткість",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "генератор сидить там, де фаза петлі = 0; те саме збурення Δφ зсуває f тим менше, чим крутіша φ(f)",
              12.5, GREY, "middle", style="italic")

    ox, oy = 100, H - 96
    w, h = W - 210, H - 220
    yc = oy - h / 2                       # лінія φ = 0 посередині
    s += _axes(ox, oy, w, h, "частота f", "фаза φ петлі")
    # вісь φ=0
    s += line(ox, yc, ox + w, yc, GREY, 1.4, "5 4")
    s += text(ox - 8, yc + 4, "0", 12, GREY, "end")
    # позначка f₀ по центру
    xf0 = ox + w * 0.5
    s += line(xf0, oy, xf0, oy - h, FAINT, 1.4, "3 4")
    s += text(xf0, oy + 20, "f₀", 13, INK, "middle", "bold")

    # дві характеристики φ(f), що перетинають 0 у f₀ з різним нахилом
    def phase_curve(slope, col, wv):
        pts = []
        N = 160
        for j in range(N + 1):
            x = ox + w * j / N
            df = (x - xf0) / (w * 0.5)       # нормована відстань (−1..+1)
            # арктангенс-подібний спад фази (як у резонатора)
            y = yc + (h * 0.46) * math.atan(slope * df) / (math.pi / 2)
            pts.append((x, y))
        return _poly(pts, col, wv)

    # висока Q — крутий нахил
    s += phase_curve(6.0, RED, 2.8)
    # низька Q — пологий нахил
    s += phase_curve(1.1, GREEN, 2.6)

    # збурення фази: однакове Δφ для обох → різний зсув частоти
    dphi = h * 0.20
    yhi = yc - dphi                          # робоча точка зсунулась по фазі вгору
    # для крутої кривої: знайти f, де φ = +Δφ
    def f_at_phase(slope, target_phi):
        # target_phi у пікселях відносно yc (від'ємний угору)
        ratio = (-target_phi) / (h * 0.46)   # = atan(slope*df)/(pi/2)
        a = math.tan(ratio * math.pi / 2)
        df = a / slope
        return xf0 + df * (w * 0.5)

    x_hi = f_at_phase(6.0, -dphi)            # висока Q
    x_lo = f_at_phase(1.1, -dphi)            # низька Q

    # горизонтальна лінія рівня збуреної фази
    s += line(ox, yhi, max(x_hi, x_lo) + 10, yhi, BLUE, 1.6, "4 3")
    s += text(ox - 8, yhi + 4, "+Δφ", 12, BLUE, "end", "bold")
    s += text(ox + 8, yhi - 8, "те саме збурення фази", 11.5, BLUE, "start", style="italic")

    # вертикальні зноси на вісь частоти
    s += arrow(xf0, oy - 4, x_hi, oy - 4, RED, 2)
    s += text((xf0 + x_hi) / 2, oy - 10, "Δf мала", 11.5, RED, "middle", "bold")
    s += line(x_hi, yhi, x_hi, oy, RED, 1.4, "3 3")

    s += arrow(xf0, oy + 38, x_lo, oy + 38, GREEN, 2)
    s += text((xf0 + x_lo) / 2, oy + 52, "Δf велика", 11.5, GREEN, "middle", "bold")
    s += line(x_lo, yhi, x_lo, oy + 44, GREEN, 1.4, "3 3")

    # легенда
    lx, ly = ox + 18, oy - h + 16
    s += rect(lx - 12, ly - 18, 300, 64, "#fff", FAINT, 1.4, 8)
    s += line(lx, ly, lx + 26, ly, RED, 2.8)
    s += text(lx + 32, ly + 4, "висока Q — крута φ(f): зсув частоти крихітний", 12, RED, "start")
    s += line(lx, ly + 24, lx + 26, ly + 24, GREEN, 2.6)
    s += text(lx + 32, ly + 28, "низька Q — полога φ(f): частота гуляє широко", 12, GREEN, "start")

    # формула-висновок
    fy = H - 22
    s += text(W / 2, fy, "нахил dφ/df ∝ Q   →   Δf / f₀ = −Δφ / (2Q):  удвічі більша Q — удвічі менший відхід частоти",
              13, INK, "middle", "bold")
    return s


# ── Рис. 2.10.3m.2 — піраміда Q і відповідна стабільність ────────────────────
def fig_q_pyramid():
    """Сходинки джерел частоти за зростанням Q: RC → LC → кераміка → кварц →
    кварц у термостаті. Праворуч — у що це виливається (короткочасна
    стабільність ~ 1/Q як орієнтир)."""
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Сходи добротності: від RC-генератора до кварцу — і що це дає",
              20, INK, "middle", "bold")
    s += text(W / 2, 56, "що вища Q, то вужча смуга «дозволених» частот навколо f₀ — і то стабільніша нота",
              12.5, GREY, "middle", style="italic")

    rows = [
        # (назва, Q-діапазон, відносна стабільність-орієнтир, колір, ширина бруска 0..1)
        ("RC-ланцюжок у чипі",        "Q ≈ 1",            "± кілька %",       GREY,  0.16),
        ("LC-контур (§2.3.6)",        "Q ≈ 10²",          "≈ 1%  (10⁴ ppm)",  GREEN, 0.30),
        ("Керамічний резонатор",      "Q ≈ 10³",          "≈ 0.5%  (5000 ppm)", COPP, 0.46),
        ("Кварцовий резонатор",       "Q ≈ 10⁴…10⁶",      "10…100 ppm",       BLUE,  0.74),
        ("Кварц у термостаті (OCXO)", "Q дуже висока",    "< 0.01 ppm",       RED,   0.96),
    ]

    ox = 70
    bx = 250                                  # старт брусків
    bw = 420                                  # повна ширина шкали брусків
    top = 96
    rh = 60
    gap = 8
    for i, (name, q, stab, col, frac) in enumerate(rows):
        y = top + i * (rh + gap)
        # назва ліворуч
        s += text(ox, y + rh / 2 - 4, name, 14, INK, "start", "bold")
        s += text(ox, y + rh / 2 + 15, q, 12.5, col, "start")
        # брусок (довжина ∝ log Q — більша Q, довший)
        bwi = bw * frac
        fillc = {GREY: "#efefef", GREEN: LGRN, COPP: "#f6ede2", BLUE: LBLUE, RED: LRED}[col]
        s += rect(bx, y + 8, bwi, rh - 16, fillc, col, 2.2, 6)
        s += text(bx + bwi - 10, y + rh / 2 + 4, "Q", 13, col, "end", "bold")
        # стабільність праворуч
        s += text(bx + bw + 18, y + rh / 2 + 4, stab, 13, col, "start", "bold")

    # стрілка зростання Q
    s += arrow(bx - 18, top + len(rows) * (rh + gap) - 4, bx - 18, top - 6, INK, 2.4)
    s += text(bx - 30, top + len(rows) * (rh + gap) / 2, "зростання Q", 12, INK, "middle",
              style="italic")
    # вертикальний підпис через rotate
    s = s.replace(
        f'>{_esc("зростання Q")}<',
        f' transform="rotate(-90 {bx - 30:.1f} {top + len(rows) * (rh + gap) / 2:.1f})">{_esc("зростання Q")}<',
        1,
    )

    # шапки колонок
    s += text(bx + bw / 2, top - 14, "відносна добротність (брусок ∝ log Q)", 12, GREY, "middle", style="italic")
    s += text(bx + bw + 18, top - 14, "орієнтир стабільності", 12, GREY, "start", style="italic")

    # нижня примітка
    fy = H - 20
    s += text(W / 2, fy,
              "Q сама не задає точність абсолютно — але задає, наскільки міцно генератор тримається своєї f₀ проти шуму й збурень",
              11.5, GREY, "middle", style="italic")
    return s


if __name__ == "__main__":
    save("fig-r10-s3m-1-phase-slope.svg", fig_phase_slope())
    save("fig-r10-s3m-2-q-pyramid.svg", fig_q_pyramid())
    print("done.")
