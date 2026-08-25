# -*- coding: utf-8 -*-
"""Фігури до теми «Статистика завмирань: Рейлі, Райс та Накагамі-m».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ACCENT = "#d35400" # Помаранчевий для акцентів


# ── 1. Порівняння щільностей імовірності (PDF) ──────────────────────────────
def fig_pdf_comparison():
    """Графіки PDF для розподілів Релея, Райса (K=3, 10 дБ) та Накагамі-m (m=0.5, 3).
    Думка — наявність прямого променя (Райс) або високого m (Накагамі) стискає графік
    і відсуває його від нуля, зменшуючи ймовірність глибоких провалів."""
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 32, "Щільність імовірності амплітуди p(r) для різних моделей", size=15, bold=True, color=INK))

    gx0, gy0, gw, gh = 80, 350, 620, 270

    f.append(line(gx0, gy0, gx0 + gw, gy0, color=MUTED, sw=1.5))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=MUTED, sw=1.5))
    f.append(text(gx0 + gw + 15, gy0 + 4, "r", size=13, bold=True, color=INK))
    f.append(text(gx0 - 15, gy0 - gh - 10, "p(r)", size=13, bold=True, color=INK))

    for i in range(1, 5):
        y = gy0 - i * (gh / 4)
        f.append(line(gx0, y, gx0 + gw, y, color="#eef1f5", sw=1.0, dash="4 4"))

    for i in range(1, 6):
        x = gx0 + i * (gw / 6)
        f.append(line(x, gy0, x, gy0 - gh, color="#eef1f5", sw=1.0, dash="4 4"))

    def pdf_rayleigh(r):
        if r < 0: return 0.0
        return 2.0 * r * math.exp(-r * r)

    def pdf_nakagami_05(r):
        if r <= 0: return 1.5958
        return 1.5958 * math.exp(-0.5 * r * r)

    def pdf_rice_k2(r):
        if r < 0: return 0.0
        return 1.8 * r * math.exp(-1.5 * (r - 1.2)**2)

    def pdf_rice_k10(r):
        if r < 0: return 0.0
        return 3.2 * math.exp(-12.0 * (r - 1.0)**2)

    def plot_curve(pdf_fn, color, sw=2.2, dash=None):
        pts = []
        steps = 120
        r_max = 2.5
        for step in range(steps + 1):
            r = step * r_max / steps
            val = pdf_fn(r)
            x = gx0 + (r / r_max) * gw
            y = gy0 - (val / 2.0) * gh
            y = max(gy0 - gh, min(gy0, y))
            pts.append(f"{x:.1f},{y:.1f}")
        d_attr = "M " + " L ".join(pts)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<path d="{d_attr}" fill="none" stroke="{color}" stroke-width="{sw}"{dash_attr}/>'

    f.append(plot_curve(pdf_nakagami_05, POS, sw=2.2, dash="6 3"))
    f.append(plot_curve(pdf_rayleigh, ACCENT, sw=2.4))
    f.append(plot_curve(pdf_rice_k2, FIELD, sw=2.2))
    f.append(plot_curve(pdf_rice_k10, NEG, sw=2.4))

    lx, ly = 480, 75
    f.append(rect(lx, ly, 210, 140, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(lx + 10, ly + 22, "Легенда моделей:", size=11, bold=True, color=INK))

    f.append(line(lx + 15, ly + 45, lx + 45, ly + 45, color=POS, sw=2.2, dash="6 3"))
    f.append(text(lx + 55, ly + 49, "Накагамі (m = 0.5)", size=11, color=INK))

    f.append(line(lx + 15, ly + 70, lx + 45, ly + 70, color=ACCENT, sw=2.4))
    f.append(text(lx + 55, ly + 74, "Релей (m = 1, K = 0)", size=11, color=INK))

    f.append(line(lx + 15, ly + 95, lx + 45, ly + 95, color=FIELD, sw=2.2))
    f.append(text(lx + 55, ly + 99, "Райс (K = 3 дБ)", size=11, color=INK))

    f.append(line(lx + 15, ly + 120, lx + 45, ly + 120, color=NEG, sw=2.4))
    f.append(text(lx + 55, ly + 124, "Райс (K = 10 дБ)", size=11, color=INK))

    f.append(text(gx0 + 100, gy0 - 15, "Зона глибоких провалів (r → 0)", size=11, color=POS, italic=True))

    render(os.path.join(IMG, "pdf-comparison.svg"), W, H, *f)


# ── 2. Фізичні сценарії поширення ──────────────────────────────────────────
def fig_physical_scenarios():
    """Схематичне зображення трьох фізичних сценаріїв:
    1) Релей: суцільні перешкоди, лише відбиті промені (NLOS).
    2) Райс: потужний прямий промінь (LOS) + слабші відбитки.
    3) Суворий Накагамі (m < 1): додаткове затінення (shadowing) від дерев/будинків."""
    W, H = 760, 440
    f = []

    f.append(text(W / 2, 30, "Фізичні умови середовища та відповідні закони завмирань", size=15, bold=True, color=INK))

    box_w, box_h = 220, 340
    gap = 20
    x0 = 30

    # 1) Релей (NLOS)
    bx1 = x0
    f.append(rect(bx1, 60, box_w, box_h, fill="#fbfcfd", stroke=ACCENT, sw=1.6, rx=8))
    f.append(text(bx1 + box_w/2, 90, "Розподіл Релея", size=14, bold=True, color=ACCENT))
    f.append(text(bx1 + box_w/2, 112, "Немає прямої видимості (NLOS)", size=10, italic=True, color=MUTED))

    f.append(circle(bx1 + 35, 160, 16, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(bx1 + 35, 164, "TX", size=10, bold=True, color=POS))
    f.append(circle(bx1 + box_w - 35, 160, 16, fill="#eef3ff", stroke=NEG, sw=1.8))
    f.append(text(bx1 + box_w - 35, 164, "RX", size=10, bold=True, color=NEG))

    f.append(rect(bx1 + 85, 130, 50, 60, fill="#e2e7ec", stroke=MUTED, sw=1.4))
    f.append(text(bx1 + 110, 164, "Будинок", size=9, color=MUTED))

    f.append(line(bx1 + 45, 150, bx1 + 110, 85, color=ACCENT, sw=1.4, dash="4 3"))
    f.append(line(bx1 + 110, 85, bx1 + box_w - 45, 150, color=ACCENT, sw=1.4, dash="4 3"))

    f.append(line(bx1 + 45, 170, bx1 + 110, 235, color=ACCENT, sw=1.4, dash="4 3"))
    f.append(line(bx1 + 110, 235, bx1 + box_w - 45, 170, color=ACCENT, sw=1.4, dash="4 3"))

    f.append(text(bx1 + 15, 270, "• Більше 10 розсіяних променів", size=10, color=INK, anchor="start"))
    f.append(text(bx1 + 15, 290, "• Рівномірний розподіл фаз", size=10, color=INK, anchor="start"))
    f.append(text(bx1 + 15, 310, "• Середнє складових I, Q = 0", size=10, color=INK, anchor="start"))
    f.append(text(bx1 + 15, 330, "• Типово для міст та кімнат", size=10, color=INK, anchor="start"))
    f.append(text(bx1 + 15, 375, "Параметри: m = 1, K = 0", size=11, bold=True, color=ACCENT, anchor="start"))

    # 2) Райс (LOS + NLOS)
    bx2 = bx1 + box_w + gap
    f.append(rect(bx2, 60, box_w, box_h, fill="#fbfcfd", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(bx2 + box_w/2, 90, "Розподіл Райса", size=14, bold=True, color=FIELD))
    f.append(text(bx2 + box_w/2, 112, "Є пряма видимість (LOS)", size=10, italic=True, color=MUTED))

    f.append(circle(bx2 + 35, 160, 16, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(bx2 + 35, 164, "TX", size=10, bold=True, color=POS))
    f.append(circle(bx2 + box_w - 35, 160, 16, fill="#eef3ff", stroke=NEG, sw=1.8))
    f.append(text(bx2 + box_w - 35, 164, "RX", size=10, bold=True, color=NEG))

    f.append(line(bx2 + 51, 160, bx2 + box_w - 51, 160, color=FIELD, sw=3.2))
    f.append(text(bx2 + box_w/2, 145, "Прямий промінь (LOS)", size=10, bold=True, color=FIELD))

    f.append(line(bx2 + 45, 150, bx2 + 110, 95, color=MUTED, sw=1.2, dash="4 3"))
    f.append(line(bx2 + 110, 95, bx2 + box_w - 45, 150, color=MUTED, sw=1.2, dash="4 3"))

    f.append(text(bx2 + 15, 270, "• Панівний прямий сигнал", size=10, color=INK, anchor="start"))
    f.append(text(bx2 + 15, 290, "• Слабкі відбиті копії", size=10, color=INK, anchor="start"))
    f.append(text(bx2 + 15, 310, "• Немає глибоких нулів", size=10, color=INK, anchor="start"))
    f.append(text(bx2 + 15, 330, "• Відкрита місцевість / вежі", size=10, color=INK, anchor="start"))
    f.append(text(bx2 + 15, 375, "Параметри: K > 0 (до 15 дБ)", size=11, bold=True, color=FIELD, anchor="start"))

    # 3) Накагамі m < 1 (Severe Fading)
    bx3 = bx2 + box_w + gap
    f.append(rect(bx3, 60, box_w, box_h, fill="#fbfcfd", stroke=POS, sw=1.6, rx=8))
    f.append(text(bx3 + box_w/2, 90, "Накагамі (m < 1)", size=14, bold=True, color=POS))
    f.append(text(bx3 + box_w/2, 112, "Затінення та втрата променів", size=10, italic=True, color=MUTED))

    f.append(circle(bx3 + 35, 160, 16, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(bx3 + 35, 164, "TX", size=10, bold=True, color=POS))
    f.append(circle(bx3 + box_w - 35, 160, 16, fill="#eef3ff", stroke=NEG, sw=1.8))
    f.append(text(bx3 + box_w - 35, 164, "RX", size=10, bold=True, color=NEG))

    f.append(circle(bx3 + 110, 150, 25, fill="#e8f5e9", stroke="#388e3c", sw=1.4))
    f.append(text(bx3 + 110, 154, "Затінення", size=9, color="#2e7d32"))

    f.append(line(bx3 + 48, 160, bx3 + 85, 160, color=POS, sw=1.4, dash="3 3"))
    f.append(line(bx3 + 135, 160, bx3 + box_w - 48, 160, color=POS, sw=1.0, dash="2 4"))

    f.append(text(bx3 + 15, 270, "• Блокування частин променів", size=10, color=INK, anchor="start"))
    f.append(text(bx3 + 15, 290, "• Тимчасове затінення", size=10, color=INK, anchor="start"))
    f.append(text(bx3 + 15, 310, "• Провали частіші за Релей", size=10, color=INK, anchor="start"))
    f.append(text(bx3 + 15, 330, "• Супутники / рухоме авто", size=10, color=INK, anchor="start"))
    f.append(text(bx3 + 15, 375, "Параметри: m < 1 (до 0.5)", size=11, bold=True, color=POS, anchor="start"))

    render(os.path.join(IMG, "physical-scenarios.svg"), W, H, *f)


# ── 3. Частота перетинів рівня та середня тривалість провалу ────────────────
def fig_lcr_afd_concept():
    """Динаміка завмирань у часі: коливання огинаючої r(t) відносно порогового рівня R_th.
    Показує точки перетинів (LCR) та тривалість перебування під порогом (AFD)."""
    W, H = 760, 380
    f = []

    f.append(text(W / 2, 30, "Динамічні характеристики завмирань: LCR та AFD", size=15, bold=True, color=INK))

    gx0, gy0, gw, gh = 70, 320, 640, 240

    f.append(line(gx0, gy0, gx0 + gw, gy0, color=MUTED, sw=1.5))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=MUTED, sw=1.5))
    f.append(text(gx0 + gw + 15, gy0 + 4, "Час (t)", size=12, bold=True, color=INK))
    f.append(text(gx0 - 20, gy0 - gh - 5, "Амплітуда r(t)", size=12, bold=True, color=INK))

    y_th = gy0 - gh * 0.45
    f.append(line(gx0, y_th, gx0 + gw, y_th, color=POS, sw=1.8, dash="6 4"))
    f.append(text(gx0 + 15, y_th - 8, "Пороговий рівень R_th (поріг чутливості)", size=11, bold=True, color=POS, anchor="start"))

    t_points = [
        (0.0, 0.7), (0.08, 0.9), (0.15, 0.5), (0.22, 0.2), (0.28, 0.15), (0.35, 0.4),
        (0.42, 0.8), (0.50, 0.95), (0.58, 0.6), (0.65, 0.35), (0.72, 0.1), (0.78, 0.2),
        (0.84, 0.5), (0.92, 0.85), (1.0, 0.75)
    ]

    pts = []
    for t, val in t_points:
        x = gx0 + t * gw
        y = gy0 - val * gh
        pts.append(f"{x:.1f},{y:.1f}")

    x_p1_start = gx0 + 0.17 * gw
    x_p1_end = gx0 + 0.35 * gw
    f.append(rect(x_p1_start, y_th, x_p1_end - x_p1_start, gy0 - y_th, fill="#fdecea", stroke="none"))

    x_p2_start = gx0 + 0.62 * gw
    x_p2_end = gx0 + 0.82 * gw
    f.append(rect(x_p2_start, y_th, x_p2_end - x_p2_start, gy0 - y_th, fill="#fdecea", stroke="none"))

    f.append(f'<path d="M {" L ".join(pts)}" fill="none" stroke="{ACCENT}" stroke-width="2.6"/>')

    x_cross1 = gx0 + 0.35 * gw
    f.append(circle(x_cross1, y_th, 6, fill="#ffffff", stroke=FIELD, sw=2.2))
    f.append(line(x_cross1, y_th + 12, x_cross1, y_th + 35, color=FIELD, sw=1.4))
    f.append(text(x_cross1, y_th + 50, "Перетин (LCR)", size=10, bold=True, color=FIELD))

    x_cross2 = gx0 + 0.82 * gw
    f.append(circle(x_cross2, y_th, 6, fill="#ffffff", stroke=FIELD, sw=2.2))

    y_afd = y_th + 30
    f.append(line(x_p2_start, y_afd, x_p2_end, y_afd, color=POS, sw=1.8))
    f.append(line(x_p2_start, y_afd - 5, x_p2_start, y_afd + 5, color=POS, sw=1.8))
    f.append(line(x_p2_end, y_afd - 5, x_p2_end, y_afd + 5, color=POS, sw=1.8))
    f.append(text((x_p2_start + x_p2_end)/2, y_afd - 8, "Тривалість провалу τ (AFD)", size=11, bold=True, color=POS))

    render(os.path.join(IMG, "lcr-afd-concept.svg"), W, H, *f)


if __name__ == '__main__':
    fig_pdf_comparison()
    fig_physical_scenarios()
    fig_lcr_afd_concept()
    print("Усі фігури згенеровано успішно у ./img/")
