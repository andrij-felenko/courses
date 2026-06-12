# -*- coding: utf-8 -*-
"""
Фігури для вставки 4.8.6a — «Двоточкове калібрування АЦП: зсув і нахил, збереження в NVS».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

fig-26-6a-1-two-point-fit.svg — дві відомі точки і пряма поправки на тлі реальної кривої ESP32.
fig-26-6a-2-calib-nvs-flow.svg — блок-схема: dev-калібрування (пишемо раз) і loop (застосовуємо щоразу).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.6a.1 — дві точки + пряма поправки поверх кривої ESP32
# ═══════════════════════════════════════════════════════════════════════════════
def fig_two_point_fit():
    W, H = 680, 400
    # Координати графічної ділянки
    LX, RX = 70, 610
    BY, TY = 350, 40
    GW = RX - LX   # 540
    GH = BY - TY   # 310

    def gx(raw):   return LX + raw / 4095 * GW
    def gy(v):     return BY - (v / 3.6) * GH

    # ── ESP32 реальна S-подібна крива (апроксимація через 7 точок) ──
    pts_real = [
        (0,    0.00), (200,  0.10), (600,  0.45),
        (1024, 0.90), (2048, 1.80), (3072, 2.75),
        (3500, 3.10), (4095, 3.30),
    ]
    def cubic_interp(pts_raw, n=300):
        """Лінійна інтерполяція між вузлами (досить для ілюстрації)."""
        result = []
        for i in range(len(pts_raw) - 1):
            r0, v0 = pts_raw[i]
            r1, v1 = pts_raw[i + 1]
            steps = max(1, int((r1 - r0) / 4095 * n))
            for s in range(steps + 1):
                t = s / steps
                result.append((r0 + t * (r1 - r0), v0 + t * (v1 - v0)))
        return result

    real_pts = cubic_interp(pts_real)

    # ── Ідеальна пряма (3.3 В / 4095 = 0.806 мВ/код) ──
    def v_ideal(r): return r / 4095 * 3.3

    # ── Калібрувальні точки (в середині шкали) ──
    raw_lo, V_lo = 600,  0.50
    raw_hi, V_hi = 3000, 2.50

    # ── Пряма поправки (двоточкова) ──
    slope = (V_hi - V_lo) / (raw_hi - raw_lo)
    def v_cal(r): return V_lo + slope * (r - raw_lo)

    # ═════ SVG ═════
    frags = []

    # Сітка (горизонтальні лінії + підписи вольтів)
    for v_grid in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        yg = gy(v_grid)
        frags.append(line(LX, yg, RX, yg, color=MUTED, sw=0.8, dash="4 3"))
        frags.append(text(LX - 6, yg + 5, "%.1f" % v_grid, size=11, color=MUTED, anchor="end"))

    # Вертикальні лінії (raw)
    for r_grid in [0, 1024, 2048, 3072, 4095]:
        xg = gx(r_grid)
        frags.append(line(xg, TY, xg, BY, color=MUTED, sw=0.8, dash="4 3"))
        frags.append(text(xg, BY + 18, str(r_grid), size=11, color=MUTED, anchor="middle"))

    # Осі
    frags.append(arrow(LX - 4, BY, LX - 4, TY - 10, color=INK, sw=1.6))
    frags.append(arrow(LX - 4, BY, RX + 12, BY, color=INK, sw=1.6))
    frags.append(text(LX - 12, TY - 16, "V, В", size=12, color=INK, anchor="middle"))
    frags.append(text(RX + 18, BY + 4, "raw", size=12, color=INK, anchor="start"))

    # Реальна крива ESP32 (сіра)
    path_real = " ".join("%.1f,%.1f" % (gx(r), gy(v)) for r, v in real_pts)
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
                 'stroke-dasharray="6 3"/>' % (path_real, MUTED))

    # Ідеальна пряма (пунктир, синя)
    x0, x1 = gx(0), gx(4095)
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.5" stroke-dasharray="3 4"/>' % (
                     x0, gy(v_ideal(0)), x1, gy(v_ideal(4095)), NEG))

    # Пряма поправки (два-точкова, червона, тільки в робочому діапазоні з запасом)
    r_left, r_right = 200, 3800
    frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2.8"/>' % (
                     gx(r_left), gy(v_cal(r_left)),
                     gx(r_right), gy(v_cal(r_right)),
                     POS))

    # Позначення «глухих країв» (заштриховані смуги)
    dead_lo = int(gx(0))
    dead_lo_r = int(gx(350))
    dead_hi_l = int(gx(3750))
    dead_hi_r = int(gx(4095))
    frags.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#ddd" opacity="0.35"/>' % (
        dead_lo, TY, dead_lo_r - dead_lo, GH))
    frags.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#ddd" opacity="0.35"/>' % (
        dead_hi_l, TY, dead_hi_r - dead_hi_l, GH))
    frags.append(text((dead_lo + dead_lo_r) / 2, BY - 12, "глухий\nкрай", size=10,
                       color=MUTED, anchor="middle"))
    frags.append(text((dead_hi_l + dead_hi_r) / 2, BY - 12, "глухий\nкрай", size=10,
                       color=MUTED, anchor="middle"))

    # Калібрувальні точки (зелені кружки)
    for rp, vp in [(raw_lo, V_lo), (raw_hi, V_hi)]:
        xp, yp = gx(rp), gy(vp)
        frags.append(circle(xp, yp, 7, fill=FIELD, stroke=FIELD, sw=2.5))
        frags.append(circle(xp, yp, 3, fill=BG, stroke=FIELD, sw=2))

    # Підписи точок
    tb, _, _ = textbox(gx(raw_lo) + 52, gy(V_lo) - 14,
                        "raw_lo=%d\nV_lo=%.2f В" % (raw_lo, V_lo),
                        size=11, fill="#eef6ef", stroke=FIELD, pad=7)
    frags.append(tb)
    tb2, _, _ = textbox(gx(raw_hi) - 56, gy(V_hi) - 14,
                         "raw_hi=%d\nV_hi=%.2f В" % (raw_hi, V_hi),
                         size=11, fill="#eef6ef", stroke=FIELD, pad=7)
    frags.append(tb2)

    # Легенда
    lx, ly, ldy = 430, 60, 22
    frags.append(line(lx, ly, lx + 30, ly, color=MUTED, sw=2, dash="6 3"))
    frags.append(text(lx + 36, ly + 5, "реальна крива ESP32", size=11, color=MUTED, anchor="start"))
    frags.append(line(lx, ly + ldy, lx + 30, ly + ldy, color=NEG, sw=1.5, dash="3 4"))
    frags.append(text(lx + 36, ly + ldy + 5, "ідеальна лінійна", size=11, color=NEG, anchor="start"))
    frags.append(line(lx, ly + 2*ldy, lx + 30, ly + 2*ldy, color=POS, sw=2.8))
    frags.append(text(lx + 36, ly + 2*ldy + 5, "пряма поправки (2 точки)", size=11, color=POS, anchor="start"))
    frags.append(circle(lx + 15, ly + 3*ldy, 7, fill=FIELD, stroke=FIELD, sw=2.5))
    frags.append(text(lx + 36, ly + 3*ldy + 5, "відомі V_lo, V_hi", size=11, color=FIELD, anchor="start"))

    # Підпис
    frags.append(text(W // 2, H - 12,
                       "Рис. 4.8.6a.1. Дві відомі напруги в надійній середині шкали задають пряму поправки",
                       size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-26-6a-1-two-point-fit.svg"), W, H, *frags,
           title="Двоточкове калібрування: пряма поправки поверх кривої ESP32")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.6a.2 — блок-схема: dev-калібрування (один раз) і loop (щоразу)
# ═══════════════════════════════════════════════════════════════════════════════
def fig_calib_nvs_flow():
    W, H = 680, 460

    frags = []

    # ── Лівий стовпець: DEV-калібрування ──
    lcx = 170
    # Заголовок
    GOLD = "#c8922a"
    frags.append(fitbox(30, 20, 280, 34, "DEV: калібрування (один раз)",
                         size=13, bold=True, fill="#fff6e0", stroke=GOLD, sw=2, rx=6))

    boxes_left = [
        (90, "Подати V_lo\n(точне джерело)"),
        (160, "analogRead → raw_lo\n(середнє N відліків)"),
        (230, "Ввести V_lo з Serial"),
        (300, "Повторити для\nV_hi / raw_hi"),
        (380, "Зібрати Calib\n{rawLo, rawHi, vLo, vHi}"),
        (450, "saveCalib() → NVS\n(Preferences.putInt/putFloat)"),
    ]

    box_w, box_h = 240, 44
    prev_y = None
    for (cy, label) in boxes_left:
        x0 = lcx - box_w // 2
        clr = FILL
        if "saveCalib" in label:
            clr = "#eef6ef"
        frags.append(fitbox(x0, cy - box_h // 2, box_w, box_h, label,
                             size=12, fill=clr, stroke=LINE, sw=1.5, rx=6))
        if prev_y is not None:
            frags.append(arrow(lcx, prev_y + box_h // 2 + 1,
                               lcx, cy - box_h // 2 - 1, color=INK, sw=1.5))
        prev_y = cy

    # ── Роздільник ──
    frags.append(line(340, 18, 340, H - 18, color=MUTED, sw=1.2, dash="6 4"))

    # ── Правий стовпець: setup() + loop() ──
    rcx = 510

    # setup() блок
    frags.append(fitbox(350, 20, 280, 34, "setup() — кожен старт",
                         size=13, bold=True, fill="#e9eefb", stroke=NEG, sw=2, rx=6))

    boxes_right_setup = [
        (90,  "analogSetPinAttenuation\n(ADC_11db)"),
        (160, "loadCalib() ← NVS"),
        (230, None),   # ромб (розгалуження)
    ]

    prev_y_r = None
    for cy, label in boxes_right_setup:
        if label is None:
            # Ромб «є ключі?»
            dx, dy_r = 36, 20
            pts = "%d,%d %d,%d %d,%d %d,%d" % (
                rcx, cy - dy_r, rcx + dx, cy, rcx, cy + dy_r, rcx - dx, cy)
            frags.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"/>' % (
                pts, FILL, LINE))
            frags.append(text(rcx, cy + 5, "є ключі?", size=11, color=INK, anchor="middle"))
            if prev_y_r is not None:
                frags.append(arrow(rcx, prev_y_r + 22, rcx, cy - dy_r - 1, color=INK, sw=1.5))
            prev_y_r = cy + dy_r
        else:
            x0 = rcx - box_w // 2
            frags.append(fitbox(x0, cy - box_h // 2, box_w, box_h, label,
                                 size=12, fill=FILL, stroke=LINE, sw=1.5, rx=6))
            if prev_y_r is not None:
                frags.append(arrow(rcx, prev_y_r, rcx, cy - box_h // 2 - 1, color=INK, sw=1.5))
            prev_y_r = cy + box_h // 2

    # Гілка «Так» (вниз)
    tb_yes, _, _ = textbox(rcx + 22, 246, "Так", size=11, fill="#eef6ef", stroke=FIELD, pad=4)
    frags.append(tb_yes)

    # Гілка «Ні» (вправо-вниз: fallback)
    frags.append(arrow(rcx + 36, 230, rcx + 100, 230, color=POS, sw=1.5))
    fb, _, _ = textbox(rcx + 140, 230, "fallback:\nсира шкала\n(raw·3.3/4095)", size=11,
                        fill="#fdecea", stroke=POS, pad=7)
    frags.append(fb)
    tb_no, _, _ = textbox(rcx + 68, 222, "Ні", size=11, fill="#fdecea", stroke=POS, pad=4)
    frags.append(tb_no)

    # Рахувати slope/offset у RAM
    ram_cy = 300
    frags.append(arrow(rcx, 250, rcx, ram_cy - box_h // 2 - 1, color=INK, sw=1.5))
    frags.append(fitbox(rcx - box_w // 2, ram_cy - box_h // 2, box_w, box_h,
                         "slope/offset у RAM\n(дешево, без флешу)",
                         size=12, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=6))

    # loop() блок
    frags.append(fitbox(350, 348, 280, 28, "loop() — щоразу",
                         size=13, bold=True, fill="#e9eefb", stroke=NEG, sw=2, rx=6))

    loop_cy = 410
    frags.append(arrow(rcx, ram_cy + box_h // 2 + 1, rcx, loop_cy - box_h // 2 - 1, color=INK, sw=1.5))
    frags.append(fitbox(rcx - box_w // 2, loop_cy - box_h // 2, box_w, box_h,
                         "raw = analogRead(PIN)\nv = applyCalib(cal, raw)",
                         size=12, fill=FILL, stroke=LINE, sw=1.5, rx=6))

    # Підпис
    frags.append(text(W // 2, H - 12,
                       "Рис. 4.8.6a.2. Два контури: рідкісне калібрування (ліворуч) і дешеве застосування при кожному читанні (праворуч)",
                       size=11, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "fig-26-6a-2-calib-nvs-flow.svg"), W, H, *frags,
           title="Калібрування АЦП: dev-сесія (пишемо раз) та щоразовий applyCalib()")


if __name__ == "__main__":
    fig_two_point_fit()
    print("fig-26-6a-1-two-point-fit.svg — OK")
    fig_calib_nvs_flow()
    print("fig-26-6a-2-calib-nvs-flow.svg — OK")
