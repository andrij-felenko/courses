# -*- coding: utf-8 -*-
"""Фігури для статті GY-271 / HMC5883L. Запуск: python figs.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: розводка GY-271 ↔ мікроконтролер (пін-у-пін) ──────────────────
def fig_wiring():
    W, H = 760, 430
    frags = []
    # Модуль GY-271 (ліворуч)
    mx, my, mw, mh = 60, 90, 200, 250
    frags.append(rect(mx, my, mw, mh, fill="#eef4fb", stroke=NEG, sw=2))
    frags.append(text(mx + mw / 2, my - 16, "Модуль GY-271", size=15, bold=True))
    frags.append(text(mx + mw / 2, my + 22, "(HMC5883L / QMC5883L)", size=12, color=MUTED))
    pins = ["VCC", "GND", "SCL", "SDA", "DRDY"]
    py0 = my + 60
    pstep = 38
    pin_y = {}
    for i, p in enumerate(pins):
        yy = py0 + i * pstep
        pin_y[p] = yy
        # контактна майданчик на правому краю модуля
        frags.append(circle(mx + mw, yy, 6, fill=BG, stroke=INK, sw=1.5))
        frags.append(text(mx + mw - 42, yy + 5, p, size=13, bold=True, anchor="middle"))

    # Мікроконтролер (праворуч)
    cx, cy, cw, ch = 520, 90, 190, 250
    frags.append(rect(cx, cy, cw, ch, fill="#eafaf0", stroke=FIELD, sw=2))
    frags.append(text(cx + cw / 2, cy - 16, "Мікроконтролер", size=15, bold=True))
    frags.append(text(cx + cw / 2, cy + 22, "(3.3 В логіка)", size=12, color=MUTED))
    mcu = ["3V3", "GND", "SCL", "SDA", "GPIO"]
    mcu_y = {}
    for i, p in enumerate(mcu):
        yy = py0 + i * pstep
        mcu_y[p] = yy
        frags.append(circle(cx, yy, 6, fill=BG, stroke=INK, sw=1.5))
        frags.append(text(cx + 46, yy + 5, p, size=13, bold=True, anchor="middle"))

    # Зʼєднання
    conn = [("VCC", "3V3", POS), ("GND", "GND", NEG),
            ("SCL", "SCL", INK), ("SDA", "SDA", INK), ("DRDY", "GPIO", MUTED)]
    for a, b, col in conn:
        y1 = pin_y[a]; y2 = mcu_y[b]
        dash = "5,4" if a == "DRDY" else None
        frags.append(line(mx + mw + 6, y1, cx - 6, y2, color=col, sw=2.2, dash=dash))

    # Підтяжки на шині (нагадування)
    frags.append(fitbox(230, 358, 300, 52,
                        "Підтяжки 4.7 кΩ на SDA і SCL до 3.3 В\n(на модулі часто вже стоять)",
                        size=12, fill="#fff8e1", stroke="#e0a800"))
    frags.append(text(W / 2, 25, "GY-271 на шині I²C: пʼять дротів", size=17, bold=True))
    render(os.path.join(OUT, "wiring.svg"), W, H, *frags)


# ── Фігура 2: магнетометр міряє напрям поля Землі → азимут ───────────────────
def fig_heading():
    W, H = 720, 430
    frags = []
    ox, oy, R = 250, 235, 150
    # Коло горизонту з осями X (вперед) і Y (ліворуч) модуля
    frags.append(circle(ox, oy, R, fill="#f7f9fc", stroke=LINE, sw=1.5))
    frags.append(arrow(ox, oy, ox + R + 20, oy, color=INK, sw=2))   # +X вперед
    frags.append(text(ox + R + 34, oy + 5, "X", size=14, bold=True))
    frags.append(arrow(ox, oy, ox, oy - R - 20, color=INK, sw=2))   # +Y (на екрані вгору)
    frags.append(text(ox, oy - R - 28, "Y", size=14, bold=True))

    # Вектор поля Землі під кутом (азимут heading від осі X)
    ang = math.radians(38)  # приклад азимута
    bx = ox + (R - 8) * math.cos(ang)
    by = oy - (R - 8) * math.sin(ang)
    frags.append(arrow(ox, oy, bx, by, color=FIELD, sw=3))
    frags.append(text(bx + 18, by - 6, "B (поле)", size=13, bold=True, color=FIELD))

    # Дуга кута heading
    steps = 22
    pts = []
    for i in range(steps + 1):
        a = ang * i / steps
        pts.append("%.1f,%.1f" % (ox + 46 * math.cos(a), oy - 46 * math.sin(a)))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>'
                 % (" ".join(pts), POS))
    frags.append(text(ox + 66, oy - 24, "θ", size=16, bold=True, color=POS))

    # Проєкції Bx, By
    frags.append(line(bx, by, bx, oy, color=MUTED, sw=1.4, dash="4,3"))
    frags.append(line(bx, by, ox, by, color=MUTED, sw=1.4, dash="4,3"))
    frags.append(text((ox + bx) / 2, oy + 18, "Bx", size=12, color=MUTED))
    frags.append(text(bx + 16, (oy + by) / 2, "By", size=12, color=MUTED))

    # Формула праворуч
    frags.append(fitbox(500, 150, 190, 70, "θ = atan2(By, Bx)",
                        size=15, fill="#fdecea", stroke=POS, bold=True))
    frags.append(fitbox(500, 240, 190, 96,
                        "θ — азимут відносно\nмагнітної півночі.\n+ поправка на\nмагнітне схилення\n= істинна північ.",
                        size=12, fill="#f4f6f8"))
    frags.append(text(W / 2, 25, "Азимут: кут вектора поля у площині модуля", size=16, bold=True))
    render(os.path.join(OUT, "heading.svg"), W, H, *frags)


# ── Фігура 3: одна плата — два різні чипи (як розрізнити) ─────────────────────
def fig_twins():
    W, H = 760, 360
    frags = []
    frags.append(text(W / 2, 26, "Однакова плата — два несумісні чипи", size=17, bold=True))

    def card(x, name, addr, idreg, marking, col):
        w, h = 300, 250
        y = 66
        frags.append(rect(x, y, w, h, fill="#fbfcfe", stroke=col, sw=2))
        frags.append(text(x + w / 2, y + 30, name, size=16, bold=True, color=col))
        rows = [("I²C-адреса", addr),
                ("ID-регістр", idreg),
                ("Маркування", marking)]
        ry = y + 70
        for lab, val in rows:
            frags.append(text(x + 20, ry, lab, size=13, bold=True, anchor="start"))
            frags.append(text(x + w - 20, ry, val, size=13, anchor="end", color=INK))
            frags.append(line(x + 20, ry + 12, x + w - 20, ry + 12, color="#e2e6ea", sw=1))
            ry += 46
        return y + h

    card(50, "HMC5883L", "0x1E", "0x0A→'H43'", "L883", NEG)
    card(410, "QMC5883L", "0x0D", "інша карта", "5883", POS)

    frags.append(fitbox(150, 330, 460, 26,
                        "Перше, що робить код: прочитати адресу / ID і обрати драйвер.",
                        size=12, fill="#fff8e1", stroke="#e0a800"))
    render(os.path.join(OUT, "twins.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_wiring()
    fig_heading()
    fig_twins()
    print("figs done")
