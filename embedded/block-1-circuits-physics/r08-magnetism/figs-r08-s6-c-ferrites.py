# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для вставки 🔌 §1.8.6c — «Осердя дроселів і трансформаторів: фізика феритів».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (префікс fig-8-6c-).
НЕ чіпає головний figs.py розділу. Стиль (AUTHORING §9): білий фон; '+' червоний,
'−' синій; поле зелене; sans-serif. Хелпери скопійовано з figs.py розділу (самодостатність).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPPER = "#cf8b5e"
ORANGE = "#e08030"
SLATE = "#42566b"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange"}


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


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, sw=2, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da} stroke-linecap="round" stroke-linejoin="round"/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 1.8.6c.1 — навіщо осердя: те саме коло витків, але магнітний шлях замкнений
# залізом → той самий струм дає в μ разів густіше поле (концентрація потоку)
# ─────────────────────────────────────────────────────────────────────────────
def fig1_core_concentrates():
    W, H = 780, 430
    s = header(W, H)
    s += text(W / 2, 30, "Що робить осердя: збирає розсіяне поле в щільний потік",
              17, INK, "middle", "bold")

    # ── ліворуч: котушка БЕЗ осердя — поле кволе й розпливається ────────────────
    ax = 195
    ay = 235
    s += text(ax, 66, "Повітря всередині", 14, INK, "middle", "bold")
    s += text(ax, 84, "(котушка без осердя)", 12, GREY, "middle", "normal", "italic")

    # витки збоку (овальні петлі), вертикальна вісь котушки
    coil_w, coil_h = 46, 150
    for i, yy in enumerate(range(int(ay - coil_h / 2), int(ay + coil_h / 2) + 1, 25)):
        s += path(f"M {ax - coil_w} {yy} A {coil_w} 10 0 0 0 {ax + coil_w} {yy}",
                  "none", COPPER, 4)
        s += path(f"M {ax - coil_w} {yy + 8} A {coil_w} 10 0 0 1 {ax + coil_w} {yy}",
                  "none", COPPER, 1.5, "2 3")
    # кволі, розпливчасті лінії поля (мало, розходяться)
    for dx in (-26, 0, 26):
        s += path(f"M {ax + dx} {ay - coil_h/2 - 4} "
                  f"C {ax + dx + 70} {ay - 120}, {ax + dx + 70} {ay + 120}, "
                  f"{ax + dx} {ay + coil_h/2 + 4}",
                  "none", GREEN, 1.6)
        s += path(f"M {ax + dx} {ay - coil_h/2 - 4} "
                  f"C {ax + dx - 70} {ay - 120}, {ax + dx - 70} {ay + 120}, "
                  f"{ax + dx} {ay + coil_h/2 + 4}",
                  "none", GREEN, 1.6)
    s += arrow(ax, ay + 14, ax, ay - 14, GREEN, 3)
    s += text(ax, ay - 22, "B (слабке)", 12.5, GREEN, "middle", "bold")
    s += text(ax, H - 36, "поле розпливається назовні,", 12, GREY, "middle")
    s += text(ax, H - 20, "більшість витків «не працює» разом", 12, GREY, "middle")

    # стрілка-перехід
    s += arrow(372, ay, 412, ay, INK, 2.4)
    s += text(392, ay - 12, "те саме I,", 11.5, INK, "middle", "bold")
    s += text(392, ay - 110, "ті самі витки", 11.5, INK, "middle")

    # ── праворуч: те саме коло на ЗАМКНЕНОМУ осерді — поле живе всередині заліза ─
    bx = 585
    by = 235
    s += text(bx, 66, "Залізне (феритове) осердя", 14, INK, "middle", "bold")
    s += text(bx, 84, "замкнений магнітний шлях", 12, GREY, "middle", "normal", "italic")

    # тороїдальне осердя (кільце) у перетині — два прямокутні стовпи + перемички
    ring_ox, ring_oy = bx - 70, by - 78        # лівий верхній кут зовнішнього
    ow, oh = 140, 156
    iw, ih = 64, 80                            # внутрішнє вікно
    inx = ring_ox + (ow - iw) / 2
    iny = ring_oy + (oh - ih) / 2
    # тіло осердя = зовнішній прямокутник зі скругленням мінус вікно (даємо двома П-подібними)
    s += rect(ring_ox, ring_oy, ow, oh, "#cdd6df", SLATE, 2.4, 14)
    s += rect(inx, iny, iw, ih, "#ffffff", SLATE, 2.0, 8)
    s += text(bx, by, "ферит", 12, SLATE, "middle", "bold")

    # витки мідного дроту на лівому стовпі
    leg_cx = ring_ox + (ow - iw) / 4 + 2
    for yy in range(int(iny - 2), int(iny + ih), 18):
        s += path(f"M {ring_ox - 6} {yy} A 18 9 0 0 0 {inx + 4} {yy + 4}",
                  "none", COPPER, 4)
    # сильні лінії поля — туго замкнені В МАТЕРІАЛІ осердя (по «середній лінії»)
    midx = ring_ox + ow / 2
    s += path(f"M {midx} {ring_oy + 16} "
              f"C {ring_ox + ow - 18} {ring_oy + 16}, {ring_ox + ow - 18} {ring_oy + oh - 16}, "
              f"{midx} {ring_oy + oh - 16} "
              f"C {ring_ox + 18} {ring_oy + oh - 16}, {ring_ox + 18} {ring_oy + 16}, "
              f"{midx} {ring_oy + 16} Z",
              "none", GREEN, 3.2)
    # стрілка напрямку потоку
    s += arrow(ring_ox + ow - 18, by + 6, ring_ox + ow - 18, by - 6, GREEN, 3)
    s += text(bx + 70, by, "B ×μ", 13, GREEN, "start", "bold")

    s += text(bx, H - 36, "поле «біжить» усередині осердя,", 12, GREY, "middle")
    s += text(bx, H - 20, "майже не виходячи назовні", 12, GREY, "middle")

    # нижня формула-зв'язок
    s += rect(40, H - 12, W - 80, 0.1, "none", "none", 0)  # placeholder (нічого)
    save("fig-8-6c-1-core-concentrates.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 1.8.6c.2 — карта матеріалів осердя: проникність μ проти робочої частоти
# (де живе ламіноване залізо, порошкове залізо, MnZn-ферит, NiZn-ферит)
# ─────────────────────────────────────────────────────────────────────────────
def fig2_material_map():
    W, H = 780, 460
    s = header(W, H)
    s += text(W / 2, 30, "Матеріали осердя: висока μ ↔ висока частота — завжди компроміс",
              16.5, INK, "middle", "bold")

    ox, oy = 95, 372            # початок осей
    axw, axh = 600, 300
    # осі
    s += arrow(ox, oy, ox + axw + 14, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh - 14, INK, 2)
    s += text(ox + axw + 18, oy + 5, "частота", 13, INK, "start", "bold")
    s += text(ox + axw + 18, oy + 21, "(лог)", 11, GREY, "start")
    s += text(ox - 12, oy - axh - 18, "μᵣ", 14, INK, "end", "bold", "italic")
    s += text(ox - 12, oy - axh - 2, "(відносна", 10.5, GREY, "end")
    s += text(ox - 12, oy - axh + 12, "проникність)", 10.5, GREY, "end")

    # сітка частот (декади)
    decades = [("50 Гц", 0.04), ("1 кГц", 0.20), ("100 кГц", 0.50),
               ("1 МГц", 0.66), ("10 МГц", 0.82), ("100 МГц", 0.98)]
    for lbl, fx in decades:
        x = ox + fx * axw
        s += line(x, oy, x, oy - axh, FAINT, 1)
        s += text(x, oy + 18, lbl, 11, GREY, "middle")

    # горизонтальні підписи μ (лог)
    for lbl, fy in [("10", 0.10), ("100", 0.40), ("1 000", 0.66), ("10 000", 0.92)]:
        y = oy - fy * axh
        s += line(ox, y, ox + axw, y, FAINT, 1)
        s += text(ox - 8, y + 4, lbl, 10.5, GREY, "end")

    def box(x0, x1, y0, y1, col, fillcol, name, sub):
        bx0 = ox + x0 * axw
        bx1 = ox + x1 * axw
        by0 = oy - y0 * axh
        by1 = oy - y1 * axh
        s_local = rect(bx0, by1, bx1 - bx0, by0 - by1, fillcol, col, 2, 10)
        s_local += text((bx0 + bx1) / 2, (by0 + by1) / 2 - 4, name, 13, col, "middle", "bold")
        s_local += text((bx0 + bx1) / 2, (by0 + by1) / 2 + 13, sub, 10.5, INK, "middle")
        return s_local

    # ламіноване залізо (силові 50 Гц, дуже висока μ, тільки низькі частоти)
    s += box(0.01, 0.24, 0.74, 0.99, SLATE, "#e3e8ee",
             "Ламіноване залізо", "силові транс. 50/60 Гц")
    # порошкове залізо (нижча μ, зате тримає підмагнічування — дроселі)
    s += box(0.18, 0.56, 0.18, 0.44, ORANGE, "#fbe6d6",
             "Порошкове залізо", "дроселі, м'яке насичення")
    # MnZn-ферит (висока μ, до ~МГц — імпульсні транс., EMI)
    s += box(0.30, 0.70, 0.50, 0.78, GREEN, "#dff0e4",
             "MnZn-ферит", "імпульсні джерела, до ~МГц")
    # NiZn-ферит (низька μ, зате до сотень МГц — ВЧ, бусини)
    s += box(0.66, 0.99, 0.06, 0.34, RED, "#f7dedb",
             "NiZn-ферит", "ВЧ і бусини, десятки МГц")

    # підпис діагональної межі компромісу
    s += text(ox + axw - 6, oy - axh + 20,
              "↘ що вища робоча частота, то нижча доступна μ", 11.5, GREY, "end", "normal", "italic")

    save("fig-8-6c-2-material-map.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 1.8.6c.3 — насичення: чому осердя має межу (B виходить на полицю)
# і навіщо повітряний зазор «вирівнює спину» кривій
# ─────────────────────────────────────────────────────────────────────────────
def fig3_saturation_gap():
    W, H = 780, 410
    s = header(W, H)
    s += text(W / 2, 30, "Межа осердя: насичення — і навіщо ріжуть повітряний зазор",
              16.5, INK, "middle", "bold")

    # ── ліва панель: B(H) — без зазору (різкий злам) і з зазором (полога пряма) ──
    ox, oy = 80, 320
    axw, axh = 300, 250
    s += arrow(ox, oy, ox + axw + 12, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh - 12, INK, 2)
    s += text(ox + axw + 14, oy + 5, "H ∝ I", 12.5, INK, "start", "bold", "italic")
    s += text(ox - 8, oy - axh - 14, "B", 13, INK, "end", "bold", "italic")
    s += text(ox + axw, oy - axh + 4, "(потік в осерді)", 10.5, GREY, "end")

    Bsat = axh * 0.80          # рівень насичення (полиця)
    s += line(ox, oy - Bsat, ox + axw, oy - Bsat, GREY, 1.4, "5 5")
    s += text(ox + 6, oy - Bsat - 6, "Bₛ — насичення", 11, GREY, "start", "bold")

    # крива без зазору: круто вгору, потім різко полиця
    n = 60
    pts = []
    for i in range(n + 1):
        f = i / n
        h = f * axw
        # насичувальна крива: швидкий ріст, насичення
        b = Bsat * math.tanh(3.1 * f)
        pts.append((ox + h, oy - b))
    s += polyline(pts, SLATE, 3)
    s += text(ox + axw * 0.42, oy - Bsat - 14, "без зазору", 11.5, SLATE, "middle", "bold")
    s += text(ox + axw * 0.62, oy - Bsat + 22, "(круто, але рано", 10.5, SLATE, "middle")
    s += text(ox + axw * 0.62, oy - Bsat + 36, "впирається в полицю)", 10.5, SLATE, "middle")

    # крива із зазором: майже пряма, далеко не доходить до Bs у тому ж діапазоні
    pts2 = []
    for i in range(n + 1):
        f = i / n
        h = f * axw
        b = min(Bsat, 0.62 * axh * f)
        pts2.append((ox + h, oy - b))
    s += polyline(pts2, GREEN, 3, "1 0")
    s += text(ox + axw - 4, oy - 0.50 * axh, "із зазором", 11.5, GREEN, "end", "bold")
    s += text(ox + axw - 4, oy - 0.50 * axh + 15, "(полога й лінійна —", 10.5, GREEN, "end")
    s += text(ox + axw - 4, oy - 0.50 * axh + 29, "тримає більший струм)", 10.5, GREEN, "end")

    # ── права панель: E-осердя із зазором у центральному керні ──────────────────
    cx = 560
    cy = 200
    # E-частина (ліворуч) + I-частина (праворуч) спрощено як рамка з центральним стовпом
    s += text(cx, 72, "E-осердя із зазором у центрі", 13, INK, "middle", "bold")
    fx0, fy0 = cx - 110, cy - 95
    fw, fh = 220, 190
    # зовнішня рамка осердя
    s += rect(fx0, fy0, fw, fh, "#cdd6df", SLATE, 2.4, 8)
    # два вікна (ліворуч і праворуч від центрального керна)
    win_w = 58
    win_h = 110
    wy = fy0 + (fh - win_h) / 2
    s += rect(fx0 + 30, wy, win_w, win_h, "#ffffff", SLATE, 2, 6)
    s += rect(fx0 + fw - 30 - win_w, wy, win_w, win_h, "#ffffff", SLATE, 2, 6)
    # центральний керн із зазором: розрив посередині
    kern_cx = cx
    gap_h = 14
    s += rect(kern_cx - 16, fy0 + 8, 32, (fh - 16 - gap_h) / 2, "#cdd6df", SLATE, 1.6, 3)
    s += rect(kern_cx - 16, fy0 + fh - 8 - (fh - 16 - gap_h) / 2, 32,
              (fh - 16 - gap_h) / 2, "#cdd6df", SLATE, 1.6, 3)
    # зазор (виділяємо червоним)
    gy = fy0 + 8 + (fh - 16 - gap_h) / 2
    s += rect(kern_cx - 16, gy, 32, gap_h, "#fbe3e0", RED, 1.8, 2)
    s += arrow(kern_cx + 40, gy + gap_h / 2, kern_cx + 18, gy + gap_h / 2, RED, 1.8)
    s += text(kern_cx + 44, gy + gap_h / 2 + 4, "повітряний зазор", 11.5, RED, "start", "bold")
    # обмотка на центральному керні (кілька витків поверх вікон)
    for yy in range(int(wy + 6), int(wy + win_h), 20):
        s += line(fx0 + 30, yy, kern_cx - 16, yy, COPPER, 4)
        s += line(kern_cx + 16, yy + 6, fx0 + fw - 30 - win_w, yy + 6, COPPER, 4)
    s += text(cx, fy0 + fh + 26, "зазор «розбавляє» осердя повітрям:", 11.5, GREY, "middle")
    s += text(cx, fy0 + fh + 42, "μ нижча, зате насичення настає пізніше", 11.5, GREY, "middle")

    save("fig-8-6c-3-saturation-gap.svg", s)


if __name__ == "__main__":
    fig1_core_concentrates()
    fig2_material_map()
    fig3_saturation_gap()
    print("done:", OUT)
