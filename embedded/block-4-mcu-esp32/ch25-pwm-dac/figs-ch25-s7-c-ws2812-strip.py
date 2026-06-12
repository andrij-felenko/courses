# -*- coding: utf-8 -*-
"""
Фігури для 🔌 вставки ch25-s7-c-ws2812-strip.md (тема §4.7.7).
Два SVG:
  fig-25-7c-1-power-injection.svg  — топологія живлення з інжекцією
  fig-25-7c-2-current-budget.svg   — бюджет струму і просадка напруги
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Локальні кольори (узгоджені з figs.py розділу) ────────────────────────────
RED    = "#c0271e"
BLUE   = "#1f47b5"
GREEN  = "#1f8a3b"
GOLD   = "#caa24a"
GREY   = "#8a8a8a"
FAINT  = "#e4e4e4"
LRED   = "#fbecec"
LGRN   = "#eef6ef"
LAMB   = "#fff6e0"
LBLUE  = "#e9eefb"
ORANGE = "#d4691e"

# ── Спільний header/footer (inline, не через svgkit.render, щоб залишити маркери) ──
def _hdr(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
        f'<rect width="{w}" height="{h}" fill="{BG}"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGold" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GOLD}"/></marker>\n'
        f'</defs>\n'
    )

def _ftr():
    return "</svg>\n"

def _arr(x1, y1, x2, y2, color=INK, w=2):
    m = {"#c0271e": "aRed", "#1f47b5": "aBlue", "#1f8a3b": "aGreen", "#caa24a": "aGold"}.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}" marker-end="url(#{m})" stroke-linecap="round"/>\n')

def _line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')

def _rect(x, y, w, h, fill=FILL, stroke=INK, sw=1.5, rx=6):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')

def _txt(x, y, s, size=13, color=INK, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}"{w}>{esc(s)}</text>\n')

def _gnd(cx, cy):
    """Символ землі (три горизонтальні штрихи)."""
    s = _line(cx, cy, cx, cy + 10, INK, 1.8)
    s += _line(cx - 12, cy + 10, cx + 12, cy + 10, INK, 2.2)
    s += _line(cx - 8,  cy + 16, cx + 8,  cy + 16, INK, 1.8)
    s += _line(cx - 4,  cy + 22, cx + 4,  cy + 22, INK, 1.4)
    return s


# ════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.7c.1 — Топологія живлення з інжекцією
# ════════════════════════════════════════════════════════════════════════════
def fig_25_7c_1_power_injection():
    W, H = 1000, 500
    s = _hdr(W, H)

    # ── Заголовок ─────────────────────────────────────────────────────────
    s += _txt(W/2, 28, "Живлення WS2812-стрічки з інжекцією", 17, INK, bold=True)
    s += _txt(W/2, 48, "окремий БЖ 5 В, товсті дроти до кожної інжекційної точки, спільна земля з МК", 10.5, GREY)

    # ── Блок живлення 5В (ліворуч) ────────────────────────────────────────
    bx, by = 38, 185
    bw, bh = 90, 70
    s += _rect(bx, by, bw, bh, LBLUE, BLUE, 2, 8)
    s += _txt(bx + bw/2, by + 24, "БЖ", 14, BLUE, bold=True)
    s += _txt(bx + bw/2, by + 42, "5 В", 12, BLUE)
    s += _txt(bx + bw/2, by + 60, "окремий", 9, GREY)

    # ── ESP32 (унизу ліворуч) ─────────────────────────────────────────────
    ex, ey = 38, 350
    ew, eh = 90, 60
    s += _rect(ex, ey, ew, eh, LGRN, GREEN, 2, 8)
    s += _txt(ex + ew/2, ey + 24, "ESP32", 13, GREEN, bold=True)
    s += _txt(ex + ew/2, ey + 42, "GPIO 3.3 В", 9, GREY)

    # ── Рівнезсувач (level shifter) ───────────────────────────────────────
    lx, ly = 175, 345
    lw, lh = 88, 52
    s += _rect(lx, ly, lw, lh, LAMB, GOLD, 2, 8)
    s += _txt(lx + lw/2, ly + 20, "LS", 13, "#8a6d1a", bold=True)
    s += _txt(lx + lw/2, ly + 36, "3.3→5 В", 9.5, "#8a6d1a")

    # дріт ESP32 → рівнезсувач
    s += _arr(ex + ew, ey + 30, lx, ly + 26, GREEN, 1.8)
    s += _txt(lx - 18, ly + 15, "DIN 3.3V", 8, GREEN, "end")

    # ── Резистор 330 Ω (після LS, перед 1-м пікселем) ─────────────────────
    rx_, ry_ = 280, 354
    s += _rect(rx_, ry_, 52, 26, "#fff", GOLD, 1.8, 4)
    s += _txt(rx_ + 26, ry_ + 10, "330 Ω", 10, "#8a6d1a", bold=True)
    s += _txt(rx_ + 26, ry_ + 22, "серійно DIN", 7.5, GREY)
    s += _arr(lx + lw, ly + 26, rx_, ry_ + 13, GOLD, 1.8)

    # ── Рядок стрічки (3 пікселі) ─────────────────────────────────────────
    STRIP_Y = 190
    px_start = 180
    px_w, px_h = 115, 60
    px_gap = 20
    px_positions = []
    for i in range(4):
        px = px_start + i * (px_w + px_gap)
        px_positions.append(px)
        fill_ = LGRN if i < 3 else FAINT
        stroke_ = GREEN if i < 3 else GREY
        label = f"піксель {i+1}" if i < 3 else "… далі"
        s += _rect(px, STRIP_Y, px_w, px_h, fill_, stroke_, 2, 8)
        s += _txt(px + px_w/2, STRIP_Y + 27, label, 10.5, stroke_, bold=(i < 3))
        if i < 3:
            s += _txt(px + px_w/2, STRIP_Y + 44, "RGB ШІМ", 8.5, GREY)
        else:
            s += _txt(px + px_w/2, STRIP_Y + 38, "(продовження)", 8.5, GREY)

    # ── Шина даних (DIN→DOUT між пікселями) ──────────────────────────────
    for i in range(3):
        x1 = px_positions[i] + px_w
        x2 = px_positions[i+1]
        s += _arr(x1, STRIP_Y + 30, x2, STRIP_Y + 30, INK, 1.8)
    # рядок від резистора до пікселя 1
    s += _line(rx_ + 52, ry_ + 13, px_positions[0], STRIP_Y + 30, GOLD, 1.8)
    s += _line(px_positions[0], ry_ + 13, px_positions[0], STRIP_Y + 30, GOLD, 1.8)

    # ── Шина живлення +5В (горизонтальна лінія вгорі) ─────────────────────
    VCC_Y = 152
    s += _line(bx + bw, by + 15, 720, VCC_Y, RED, 3)
    s += _txt(105, VCC_Y - 6, "+5 В (товстий дріт)", 9.5, RED, "start", bold=True)

    # стовбури до пікселів (інжекційні точки: початок, середина~пікс2, кінець~пікс4)
    inject_pts = [px_positions[0] + px_w/2,
                  px_positions[1] + px_w/2,
                  px_positions[3] + px_w/2]
    inject_labels = ["ПОЧАТОК", "СЕРЕДИНА", "КІНЕЦЬ"]
    for idx, (xp, lab) in enumerate(zip(inject_pts, inject_labels)):
        s += _line(xp, VCC_Y, xp, STRIP_Y, RED, 2.5)
        s += _rect(xp - 32, VCC_Y - 22, 64, 18, LRED, RED, 1.4, 4)
        s += _txt(xp, VCC_Y - 10, lab, 8.5, RED, bold=True)

    # ── Шина GND (горизонтальна лінія знизу) ──────────────────────────────
    GND_Y = 290
    s += _line(bx + bw, by + 55, 720, GND_Y, BLUE, 2.5)
    s += _txt(105, GND_Y + 11, "GND (товстий дріт)", 9.5, BLUE, "start", bold=True)
    for xp in inject_pts:
        s += _line(xp, STRIP_Y + px_h, xp, GND_Y, BLUE, 2)
    # земля від ESP32
    s += _line(ex + ew/2, ey + eh, ex + ew/2, GND_Y + 10, BLUE, 2)
    s += _gnd(ex + ew/2, GND_Y + 10)
    # земля від LS
    s += _line(lx + lw/2, ly + lh, lx + lw/2, GND_Y + 10, BLUE, 1.5)
    s += _gnd(lx + lw/2, GND_Y + 10)

    # ── Конденсатор 1000 мкФ (біля вхідних 5V/GND) ────────────────────────
    cx_c, cy_c = 152, 200
    s += _rect(cx_c - 18, cy_c - 24, 36, 48, "#fff", GOLD, 2, 4)
    s += _txt(cx_c, cy_c - 10, "1000", 9, "#8a6d1a", bold=True)
    s += _txt(cx_c, cy_c + 4,  "мкФ", 8.5, "#8a6d1a")
    s += _txt(cx_c, cy_c + 18, "+  10В", 7.5, GREY)
    s += _line(bx + bw, by + 15, cx_c + 18, cy_c - 24, RED, 1.5, "3,2")
    s += _line(bx + bw, by + 55, cx_c + 18, cy_c + 24, BLUE, 1.5, "3,2")

    # ── Порівняння: з інжекцією vs без (угорі справа) ─────────────────────
    cpx, cpy = 720, 60
    cpw, cph = 250, 110
    s += _rect(cpx, cpy, cpw, cph, "#f9f9fb", INK, 1.4, 8)
    s += _txt(cpx + cpw/2, cpy + 18, "Напруга вздовж стрічки", 10.5, INK, bold=True)

    # БЕЗ інжекції: градієнт 5.0 → 3.6 В (червона лінія вниз)
    gx0, gx1 = cpx + 18, cpx + cpw - 18
    g_y0, g_y1 = cpy + 38, cpy + 88
    s += _line(gx0, g_y0, gx1, g_y1, RED, 2.5)
    s += _txt(cpx + cpw/2 + 18, cpy + 34, "без інжекції: 5.0→3.6 В ⚠", 8.5, RED, bold=True)
    s += _txt(gx0 - 4, g_y0 + 4, "5.0 В", 8, RED, "end")
    s += _txt(gx1 + 4, g_y1 + 4, "3.6 В", 8, RED, "start")

    # З інжекцією: рівна лінія (зелена)
    s += _line(gx0, (g_y0 + g_y1)/2 - 6, gx1, (g_y0 + g_y1)/2 - 6, GREEN, 2.5)
    s += _txt(cpx + cpw/2, (g_y0 + g_y1)/2 - 14, "з інжекцією: рівне ~5 В ✓", 8.5, GREEN, bold=True)

    # ── Підпис фігури ──────────────────────────────────────────────────────
    s += _txt(W/2, H - 14, "Рис. 4.7.7c.1. Топологія живлення з інжекцією: БЖ 5 В, інжекція на початку/середині/кінці, рівнезсувач і обв'язка.", 9.5, GREY)

    s += _ftr()
    path = os.path.join(OUT, "fig-25-7c-1-power-injection.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)
    print("wrote", os.path.basename(path))


# ════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.7c.2 — Бюджет струму і просадка напруги
# ════════════════════════════════════════════════════════════════════════════
def fig_25_7c_2_current_budget():
    W, H = 940, 440
    s = _hdr(W, H)

    # ── Заголовок ─────────────────────────────────────────────────────────
    s += _txt(W/2, 28, "Бюджет струму і просадка напруги по доріжці", 17, INK, bold=True)
    s += _txt(W/2, 47, "піковий струм — лінійний за пікселями; тонка мідь дає падіння → товстий дріт + інжекція", 10.5, GREY)

    # ═══════════════════════════════════════
    # ЛІВА ПАНЕЛЬ — стовпчики струму
    # ═══════════════════════════════════════
    s += _rect(30, 58, 420, 350, "#f7f8fc", FAINT, 1.2, 8)
    s += _txt(240, 78, "Піковий струм (повна білизна)", 11.5, INK, bold=True)
    s += _txt(240, 94, "I = N × 60 мА", 10, GREY)

    bars = [
        (30,  1.8,  "30 пікс",  "≈ 1.8 А",  "запоб. 2.5 А",  GREEN),
        (100, 6.0,  "100 пікс", "≈ 6 А",    "запоб. 7.5 А",  GOLD),
        (300, 18.0, "300 пікс", "≈ 18 А",   "запоб. 25 А",   RED),
    ]
    max_I = 18.0
    bbar_x = [90, 210, 330]
    bbar_w = 80
    bar_bot = 380
    bar_max_h = 240

    for (npx, cur, lab_n, lab_i, lab_f, col), bx_ in zip(bars, bbar_x):
        bh_ = int(bar_max_h * cur / max_I)
        # стовпчик
        s += _rect(bx_, bar_bot - bh_, bbar_w, bh_, col + "33", col, 1.8, 4)
        # підпис зверху
        frag, fw, fh = textbox(bx_ + bbar_w/2, bar_bot - bh_ - 22, lab_i, size=10, fill=col+"22", stroke=col, sw=1.2, color=col, bold=True, pad=6)
        s += frag
        # підпис знизу
        s += _txt(bx_ + bbar_w/2, bar_bot + 14, lab_n, 9.5, INK)
        s += _txt(bx_ + bbar_w/2, bar_bot + 27, lab_f, 8, GREY)

    # Вісь Y (А)
    s += _arr(58, bar_bot + 4, 58, bar_bot - bar_max_h - 8, INK, 1.5)
    s += _txt(58, bar_bot - bar_max_h - 14, "А", 9, INK)
    for tick_I, tick_label in [(6, "6 А"), (12, "12 А"), (18, "18 А")]:
        ty = bar_bot - int(bar_max_h * tick_I / max_I)
        s += _line(54, ty, 62, ty, GREY, 1)
        s += _txt(50, ty + 4, tick_label, 8, GREY, "end")

    # ═══════════════════════════════════════
    # ПРАВА ПАНЕЛЬ — просадка напруги
    # ═══════════════════════════════════════
    s += _rect(470, 58, 440, 350, "#f7f8fc", FAINT, 1.2, 8)
    s += _txt(690, 78, "Падіння напруги по довжині стрічки", 11.5, INK, bold=True)
    s += _txt(690, 94, "ΔU = I · R; доріжка ≈ 1.5–3 Ω/м (тонка мідь)", 10, GREY)

    # Вісь X — довжина 0..2 м, вісь Y — ΔU 0..1.4 В
    ox2, oy2 = 510, 380
    pw2, ph2 = 370, 240
    s += _arr(ox2, oy2, ox2 + pw2 + 10, oy2, INK, 1.5)
    s += _arr(ox2, oy2, ox2, oy2 - ph2 - 8, INK, 1.5)
    s += _txt(ox2 + pw2 + 14, oy2 + 4, "м", 9, INK, "start")
    s += _txt(ox2 - 4, oy2 - ph2 - 14, "ΔU (В)", 9, INK, "end")

    # Тіки X
    for xm, xl in [(0.5, "0.5"), (1.0, "1"), (1.5, "1.5"), (2.0, "2")]:
        tx = ox2 + xm / 2.0 * pw2
        s += _line(tx, oy2 - 3, tx, oy2 + 3, GREY, 1)
        s += _txt(tx, oy2 + 13, xl, 8.5, GREY)

    # Тіки Y
    for dU, dl in [(0.5, "0.5"), (1.0, "1.0")]:
        ty2 = oy2 - dU / 1.4 * ph2
        s += _line(ox2 - 3, ty2, ox2 + 3, ty2, GREY, 1)
        s += _txt(ox2 - 6, ty2 + 4, dl, 8.5, GREY, "end")

    # Криві: R = 2 Ω/м (гірший випадок, червоний) і R = 0.5 Ω/м (товстий дріт, зелений)
    # Використовуємо I = 6 А (100 пікс)
    I_base = 6.0
    R_bad  = 2.0  # Ω/м (тонка доріжка стрічки)
    R_good = 0.3  # Ω/м (товстий зовнішній дріт)

    def x_px(m):  return ox2 + m / 2.0 * pw2
    def y_px(dU): return oy2 - min(dU, 1.4) / 1.4 * ph2

    # Погана крива (тонкий дріт / лише доріжка)
    bad_pts = " ".join(f"{x_px(m):.1f},{y_px(I_base*R_bad*m):.1f}" for m in [i*0.1 for i in range(21)])
    s += f'<polyline points="{bad_pts}" fill="none" stroke="{RED}" stroke-width="2.4" stroke-linejoin="round"/>\n'
    s += _txt(x_px(1.2), y_px(I_base*R_bad*1.2) - 10, "тонка мідь (≈2 Ω/м)", 8.5, RED, bold=True)

    # Хороша крива (товстий дріт)
    good_pts = " ".join(f"{x_px(m):.1f},{y_px(I_base*R_good*m):.1f}" for m in [i*0.1 for i in range(21)])
    s += f'<polyline points="{good_pts}" fill="none" stroke="{GREEN}" stroke-width="2.4" stroke-linejoin="round"/>\n'
    s += _txt(x_px(1.6), y_px(I_base*R_good*1.6) + 12, "товстий дріт (≈0.3 Ω/м)", 8.5, GREEN, bold=True)

    # Небезпечна межа ΔU = 0.5 В (стрічка не гарантує роботу нижче 4.5 В)
    s += _line(ox2, y_px(0.5), ox2 + pw2, y_px(0.5), GOLD, 1.6, "5,3")
    s += _txt(ox2 + pw2 + 4, y_px(0.5) + 3, "0.5 В = ліміт", 8, "#8a6d1a", "start")

    # ── Підсумкова рамка ───────────────────────────────────────────────────
    frag2, fw2, fh2 = textbox(W/2, H - 36,
        "Правило: посилений дріт + запобіжник + інжекція кожні ~50–100 пікс (~1–1.5 м)",
        size=10.5, fill=LAMB, stroke=GOLD, sw=1.6, color="#5a4010", bold=True, pad=9)
    s += frag2

    # ── Підпис фігури ──────────────────────────────────────────────────────
    s += _txt(W/2, H - 14, "Рис. 4.7.7c.2. Бюджет струму (ліворуч) і просадка напруги по довжині (праворуч).", 9.5, GREY)

    s += _ftr()
    path = os.path.join(OUT, "fig-25-7c-2-current-budget.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)
    print("wrote", os.path.basename(path))


if __name__ == "__main__":
    fig_25_7c_1_power_injection()
    fig_25_7c_2_current_budget()
    print("OK — фігури 4.7.7c.1 і 4.7.7c.2 готові у", OUT)
