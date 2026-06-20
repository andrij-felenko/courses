# -*- coding: utf-8 -*-
"""Фігури до теми «Класи перетворювачів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

WARM = "#e08a3c"


def zigzag(x1, x2, y, n=6, amp=8, color=INK, sw=2.2):
    """Резистор-«пилка» між x1 і x2 на висоті y."""
    step = (x2 - x1) / (n + 1)
    pts = [(x1, y)]
    for i in range(1, n + 1):
        pts.append((x1 + (i - 0.5) * step, y - amp if i % 2 else y + amp))
    pts.append((x2, y))
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (s, color, sw))


def coil(x1, x2, y, n=6, r=11, color=INK, sw=2):
    """Котушка з n півкіл між x1 і x2."""
    step = (x2 - x1) / n
    out = []
    for i in range(n):
        cx = x1 + i * step
        out.append('<path d="M %.1f,%.1f A %.1f,%.1f 0 1 1 %.1f,%.1f" '
                   'fill="none" stroke="%s" stroke-width="%.1f"/>'
                   % (cx, y, r, r, cx + step, y, color, sw))
    return "".join(out)


# ── 1. Єдина ідея: R = ρ·L/A, C = ε·A/d, L = μ·N²·A/ℓ — матеріал/геометрія ─────
def fig_three_handles():
    W, H = 700, 290
    f = [text(W / 2, 26, "Одна ідея на три родини: світ крутить ручку в R, C або L",
              size=16, bold=True)]
    f.append(text(W / 2, 46, "матеріальні члени (ρ, ε, μ) і геометричні — саме їх "
                  "змінює фізична величина", size=11, color=MUTED, italic=True))

    rows = [
        ("резистор",    "R = ", "ρ", " · L / A",        "нагрів, світло → ρ;   розтяг → L, A"),
        ("конденсатор", "C = ", "ε", " · A / d",        "волога → ε;   тиск → d;   зсув → A"),
        ("котушка",     "L = ", "μ", " · N² · A / ℓ",   "метал, рух осердя → μ та магнітний шлях"),
    ]
    y = 70
    for name, lhs, mat, geo, note in rows:
        f.append(rect(28, y, W - 56, 58, fill=FILL, stroke=LINE, sw=1.2, rx=8))
        f.append(text(48, y + 35, name, size=13, color=INK, anchor="start", bold=True))
        f.append(text(176, y + 36, lhs, size=17, anchor="start", bold=True))
        f.append(text(218, y + 36, mat, size=19, color=POS, anchor="start", bold=True))
        f.append(text(236, y + 36, geo, size=17, color=NEG, anchor="start", bold=True))
        f.append(text(398, y + 36, note, size=11, color=MUTED, anchor="start", italic=True))
        y += 68
    render(os.path.join(IMG, 'three-handles.svg'), W, H, *f)


# ── 2. Резистивні: терморезистор, фоторезистор, тензодавач, потенціометр ──────
def fig_resistive():
    W, H = 720, 250
    f = [text(W / 2, 26, "Резистивні давачі: чотири способи змінити опір", size=16, bold=True)]

    def cell(x0, name, knob, kc):
        f.append(rect(x0, 48, 155, 178, fill=FILL, stroke=LINE, sw=1.2, rx=8))
        f.append(text(x0 + 77.5, 70, name, size=12.5, bold=True))
        f.append(text(x0 + 77.5, 212, knob, size=13, color=kc, bold=True))

    # терморезистор: пилка + полум'я
    cell(20, "терморезистор", "ρ(T)", FIELD)
    f.append(zigzag(50, 145, 144))
    f.append('<path d="M 97.5,190 C 87.7,183.6 90.6,165.8 97.5,157.8 '
             'C 104.4,165.8 107.3,183.6 97.5,190 Z" fill="%s"/>' % WARM)
    f.append('<path d="M 97.5,186.1 C 92.6,180.3 94.1,170 97.5,164.9 '
             'C 100.9,170 102.4,180.3 97.5,186.1 Z" fill="#f6c84a"/>')

    # фоторезистор: пилка + промені
    cell(195, "фоторезистор", "ρ(світло)", FIELD)
    f.append(zigzag(225, 320, 144))
    for dx in (-12, 0, 12):
        f.append(arrow(260.5 + dx, 108, 268.5 + dx, 130, color="#caa24a", sw=1.6))

    # тензодавач: фольгова змійка + розтяг
    cell(370, "тензодавач", "L · A", FIELD)
    f.append(rect(394, 140, 108, 30, fill="#eef0f2", stroke=MUTED, sw=1, rx=3))
    serp = [(404, 146), (404, 162), (416.6, 162), (416.6, 146), (429.1, 146),
            (429.1, 162), (441.7, 162), (441.7, 146), (454.3, 146), (454.3, 162),
            (466.9, 162), (466.9, 146), (479.4, 146), (479.4, 162), (492, 162), (492, 146)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-linejoin="round" stroke-linecap="round"/>'
             % (" ".join("%.1f,%.1f" % p for p in serp), POS))
    f.append(arrow(400, 184, 378, 184))
    f.append(arrow(495, 184, 517, 184))
    f.append(text(447.5, 200, "розтяг", size=10.5, color=MUTED, italic=True))

    # потенціометр: пилка + повзунок
    cell(545, "потенціометр", "положення", FIELD)
    f.append(zigzag(575, 670, 144))
    f.append(arrow(622.5, 110, 622.5, 136, color=NEG, sw=2))
    f.append(text(622.5, 104, "повзунок", size=10, color=NEG, bold=True))
    render(os.path.join(IMG, 'resistive.svg'), W, H, *f)


# ── 3. Міст Вітстона: збалансований дає 0; ΔR дає чисту різницю ───────────────
def fig_wheatstone():
    W, H = 700, 320
    f = [text(W / 2, 26, "Міст Вітстона: прибрати велику базу, лишити чисту ΔR",
              size=16, bold=True)]

    def bridge(x0, w, title, tc, fill, active_label, vout, vc):
        cx = x0 + w / 2
        f.append(rect(x0, 44, w, 256, fill=fill, stroke=tc, sw=1.4, rx=8))
        f.append(text(cx, 64, title, size=13, color=tc, bold=True))
        lx, rx = cx - 85, cx + 85
        topy, boty, midy = 98, 270, 184
        # шини
        f.append(line(lx, topy, rx, topy, color=INK, sw=2))
        f.append(line(lx, boty, rx, boty, color=INK, sw=2))
        f.append(text(cx, topy - 8, "V_зб", size=11, bold=True))
        # земля
        f.append(line(cx - 10, boty + 8, cx + 10, boty + 8, color=INK, sw=2))
        f.append(line(cx - 6, boty + 12, cx + 6, boty + 12, color=INK, sw=1.6))
        # ліве плече (два резистори R/R)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>'
                 % (vzig(lx, topy + 6, midy - 6), INK))
        f.append(circle(lx, midy, 4, fill=INK, stroke=INK))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>'
                 % (vzig(lx, midy + 6, boty - 6), INK))
        # праве плече (верх R, низ — активний)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
                 'stroke-linejoin="round" stroke-linecap="round"/>'
                 % (vzig(rx, topy + 6, midy - 6), INK))
        f.append(circle(rx, midy, 4, fill=INK, stroke=INK))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
                 'stroke-linejoin="round" stroke-linecap="round"/>'
                 % (vzig(rx, midy + 6, boty - 6), FIELD))
        f.append(text(rx + 16, midy + 34, active_label, size=11, color=FIELD,
                      anchor="start", bold=True))
        # гальванометр у діагоналі
        f.append(line(lx, midy, cx - 19, midy, color=INK, sw=2))
        f.append(line(rx, midy, cx + 19, midy, color=INK, sw=2))
        f.append(circle(cx, midy, 19, fill=BG, stroke=INK, sw=2))
        f.append(text(cx, midy + 6, "V", size=15, color=vc, bold=True))
        f.append(text(cx, midy + 40, vout, size=12, color=vc, bold=True))

    bridge(24, 326, "збалансований", MUTED, "#f6f9f6", "R", "V = 0", MUTED)
    bridge(360, 316, "давач змінив опір на ΔR", FIELD, "#f1f7f1", "R+ΔR", "V = ΔV", FIELD)
    render(os.path.join(IMG, 'wheatstone.svg'), W, H, *f)


def vzig(x, y1, y2, n=4, amp=8):
    """Вертикальний резистор-пилка між y1 і y2 на стовпчику x."""
    step = (y2 - y1) / (n + 1)
    pts = [(x, y1)]
    for i in range(1, n + 1):
        pts.append((x - amp if i % 2 else x + amp, y1 + (i - 0.5) * step))
    pts.append((x, y2))
    return " ".join("%.1f,%.1f" % p for p in pts)


# ── 4. Ємнісний: три ручки d, A, ε ───────────────────────────────────────────
def fig_capacitive():
    W, H = 720, 250
    f = [text(W / 2, 26, "Ємнісний давач: три ручки формули C = ε·A/d", size=16, bold=True)]

    # зазор d
    f.append(rect(30, 48, 180, 180, fill="#eef4fb", stroke=NEG, sw=1.3, rx=8))
    f.append(text(120, 70, "зазор d", size=13, color=NEG, bold=True))
    f.append(text(120, 214, "тиск, наближення", size=11, italic=True))
    f.append(line(92, 114, 92, 174, color=INK, sw=3))
    f.append(line(120, 114, 120, 174, color=INK, sw=3))
    f.append(arrow(150, 144, 126, 144, color=POS, sw=2))
    f.append(text(170, 148, "d↓", size=13, color=POS, bold=True))

    # площа A
    f.append(rect(270, 48, 180, 180, fill="#eef4fb", stroke=NEG, sw=1.3, rx=8))
    f.append(text(360, 70, "площа A", size=13, color=NEG, bold=True))
    f.append(text(360, 214, "положення, зсув", size=11, italic=True))
    f.append(line(320, 114, 370, 114, color=INK, sw=3))
    f.append(line(350, 174, 400, 174, color=INK, sw=3))
    f.append(arrow(354, 192, 390, 192, color=POS, sw=2))
    f.append(text(372, 100, "зсув → A", size=11, color=POS, bold=True))

    # діелектрик ε
    f.append(rect(510, 48, 180, 180, fill="#eef4fb", stroke=NEG, sw=1.3, rx=8))
    f.append(text(600, 70, "діелектрик ε", size=13, color=NEG, bold=True))
    f.append(text(600, 214, "волога, рівень рідини", size=11, italic=True))
    f.append(line(578, 114, 578, 174, color=INK, sw=3))
    f.append(line(622, 114, 622, 174, color=INK, sw=3))
    f.append(rect(582, 116, 36, 56, fill="#cfe3f7", stroke=NEG, sw=1, rx=2))
    f.append(text(600, 152, "ε", size=18, color=NEG, bold=True))
    render(os.path.join(IMG, 'capacitive.svg'), W, H, *f)


# ── 5. Індуктивні: рухоме осердя (LVDT) та вихрові струми ─────────────────────
def fig_inductive():
    W, H = 700, 260
    f = [text(W / 2, 26, "Індуктивні давачі: рухоме осердя та вихрові струми",
              size=16, bold=True)]

    # ліворуч: рухоме осердя
    f.append(rect(28, 48, 318, 188, fill="#fbf6ee", stroke="#caa24a", sw=1.3, rx=8))
    f.append(text(187, 70, "рухоме осердя → L", size=13, color="#9a7a1e", bold=True))
    f.append(line(70, 150, 95, 150, color=INK, sw=2))
    f.append(coil(95, 255, 150, n=6, r=13.3))
    f.append(line(255, 150, 280, 150, color=INK, sw=2))
    f.append(rect(120, 158, 70, 16, fill="#d9c08a", stroke="#9a7a1e", sw=1.4, rx=0))
    f.append(arrow(150, 200, 200, 200, color="#9a7a1e", sw=2))
    f.append(text(165, 220, "осердя рухається", size=11, color="#9a7a1e", italic=True))

    # праворуч: вихрові струми
    f.append(rect(360, 48, 312, 188, fill="#eef4fb", stroke=NEG, sw=1.3, rx=8))
    f.append(text(516, 70, "метал поряд → вихрові струми", size=12, color=NEG, bold=True))
    f.append(line(400, 150, 420, 150, color=INK, sw=2))
    f.append(coil(420, 530, 150, n=5, r=11))
    f.append(line(530, 150, 545, 150, color=INK, sw=2))
    f.append(rect(575, 110, 60, 80, fill="#cfd6de", stroke=MUTED, sw=1.4, rx=3))
    f.append(text(605, 104, "метал", size=10.5, color=MUTED, bold=True))
    f.append('<path d="M 590,135 a 12,8 0 1 1 0.1,0" fill="none" stroke="%s" stroke-width="1.6"/>' % NEG)
    f.append('<path d="M 590,160 a 12,8 0 1 1 0.1,0" fill="none" stroke="%s" stroke-width="1.6"/>' % NEG)
    f.append(arrow(548, 150, 568, 150, color=NEG, sw=1.8))
    f.append(text(516, 214, "L і добротність змінюються", size=11, color=NEG, italic=True))
    render(os.path.join(IMG, 'inductive.svg'), W, H, *f)


# ── 6. Спільний знаменник: R — постійний струм; C і L — змінний ───────────────
def fig_dc_vs_ac():
    W, H = 700, 270
    f = [text(W / 2, 26, "R виявляє постійний струм; C і L — лише змінний",
              size=16, bold=True)]

    # ЛІВОРУЧ: резистивний — DC
    f.append(rect(28, 46, 318, 196, fill="#fbf2f1", stroke=POS, sw=1.3, rx=8))
    f.append(text(187, 68, "резистивний → постійний струм", size=12, color=POS, bold=True))
    # джерело DC
    f.append(circle(80, 150, 18, fill=BG, stroke=INK, sw=2))
    f.append(text(80, 146, "+", size=15, color=POS, bold=True))
    f.append(line(73, 158, 87, 158, color=NEG, sw=2.4))
    f.append(text(80, 124, "DC", size=11, bold=True))
    # контур
    f.append(line(80, 132, 80, 110, color=INK, sw=2))
    f.append(line(80, 110, 200, 110, color=INK, sw=2))
    f.append(line(200, 110, 200, 130, color=INK, sw=2))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round" stroke-linecap="round"/>'
             % (vzig(200, 130, 170, n=4, amp=8), FIELD))
    f.append(text(220, 154, "R(вимір.)", size=10.5, color=FIELD, anchor="start", bold=True))
    f.append(line(200, 170, 200, 190, color=INK, sw=2))
    f.append(line(80, 168, 80, 190, color=INK, sw=2))
    f.append(line(80, 190, 200, 190, color=INK, sw=2))
    f.append(circle(290, 130, 18, fill=BG, stroke=INK, sw=2))
    f.append(text(290, 136, "V", size=14, color=FIELD, bold=True))
    f.append(line(245, 110, 290, 110, color=INK, sw=2))
    f.append(line(290, 110, 290, 112, color=INK, sw=2))
    f.append(text(187, 224, "дільник / міст — і одразу на АЦП", size=11, italic=True))

    # ПРАВОРУЧ: ємнісний / індуктивний — AC
    f.append(rect(360, 46, 312, 196, fill="#eef4fb", stroke=NEG, sw=1.3, rx=8))
    f.append(text(516, 68, "ємнісний / індуктивний → змінний", size=12, color=NEG, bold=True))
    # джерело AC (синус у колі)
    f.append(circle(420, 150, 18, fill=BG, stroke=INK, sw=2))
    sine = []
    for i in range(26):
        t = i / 25.0
        sine.append((410 + 20 * t, 150 - 6 * math.sin(2 * math.pi * t)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
             'stroke-linejoin="round" stroke-linecap="round"/>'
             % (" ".join("%.1f,%.1f" % p for p in sine), INK))
    f.append(text(420, 124, "AC", size=11, bold=True))
    # провід → конденсатор → котушка
    f.append(line(438, 150, 480, 150, color=INK, sw=2))
    f.append(line(486, 132, 486, 168, color=INK, sw=3))
    f.append(line(504, 132, 504, 168, color=INK, sw=3))
    f.append(coil(520, 580, 150, n=3, r=10))
    f.append(line(580, 150, 600, 150, color=INK, sw=2))
    f.append(text(516, 196, "Xc = 1/(2·π·f·C)    XL = 2·π·f·L", size=11.5, color=NEG, bold=True))
    f.append(text(516, 224, "реактивні — вимір на змінному сигналі", size=11, italic=True))
    render(os.path.join(IMG, 'dc-vs-ac.svg'), W, H, *f)


# ── 7. Порівняння трьох родин — мапа вибору ──────────────────────────────────
def fig_compare():
    W, H = 720, 300
    f = [text(W / 2, 26, "Резистивні · ємнісні · індуктивні — стисла мапа вибору",
              size=16, bold=True)]

    cols = [144, 332, 520]          # ліві краї стовпців даних
    cw = 188
    head = [("Резистивні", POS), ("Ємнісні", NEG), ("Індуктивні", "#9a7a1e")]
    rows = [
        ("ручка",      ["ρ або L, A", "d, A, ε", "μ, магнітний шлях"]),
        ("контакт",    ["зазвичай так", "ні", "ні (метал)"]),
        ("зчитування", ["дільник / міст (DC)", "AC / частота", "AC / добротність"]),
        ("сильне",     ["просто, дешево", "чутл., безконтакт.", "стійкий до бруду"]),
        ("слабке",     ["самонагрів, дрейф", "паразити, волога", "лише метал, AC"]),
        ("де",         ["темп., тензо, світло", "наближення, дотик", "наближення, LVDT"]),
    ]
    # заголовки стовпців
    y0 = 48
    f.append(rect(24, y0, 120, 36, fill="#eef1f6", stroke=MUTED, sw=1, rx=0))
    for (name, c), x in zip(head, cols):
        f.append(rect(x, y0, cw, 36, fill="#eef1f6", stroke=MUTED, sw=1, rx=0))
        f.append(text(x + cw / 2, y0 + 23, name, size=13, color=c, bold=True))
    # рядки
    y = y0 + 36
    for label, vals in rows:
        f.append(rect(24, y, 120, 36, fill="#fafafa", stroke=MUTED, sw=0.8, rx=0))
        f.append(text(34, y + 23, label, size=11.5, anchor="start", bold=True))
        for v, x in zip(vals, cols):
            f.append(rect(x, y, cw, 36, fill=BG, stroke=MUTED, sw=0.8, rx=0))
            f.append(text(x + cw / 2, y + 23, v, size=11))
        y += 36
    render(os.path.join(IMG, 'compare.svg'), W, H, *f)


if __name__ == "__main__":
    fig_three_handles()
    fig_resistive()
    fig_wheatstone()
    fig_capacitive()
    fig_inductive()
    fig_dc_vs_ac()
    fig_compare()
    print("OK: 7 фігур у", IMG)
