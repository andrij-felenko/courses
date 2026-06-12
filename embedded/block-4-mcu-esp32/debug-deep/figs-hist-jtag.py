# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для JTAG-історії Розділу 4.14 — «Межовий скан і JTAG».
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Фігури:
  fig-14-0-1-boundary-scan.svg  — концепція межового скану
  fig-14-0-2-tap-scan-chain.svg — TAP і scan chain (4 дроти, кілька чипів)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.0.1 — Концепція межового скану (boundary scan)
# Показує: біля кожного виводу — реєстрова клітинка; у нормальному режимі
# прозора; у тестовому — перехоплює/виставляє; всі клітинки у ланцюгу.
# ══════════════════════════════════════════════════════════════════════════════
def fig_boundary_scan():
    W, H = 780, 420
    frags = []

    # ── Корпус чипа (центральний прямокутник) ──────────────────────────────
    chip_x, chip_y, chip_w, chip_h = 260, 90, 260, 240
    frags.append(rect(chip_x, chip_y, chip_w, chip_h,
                      fill="#e8edf5", stroke="#2457d6", sw=2.5, rx=8))
    frags.append(text(chip_x + chip_w / 2, chip_y + chip_h / 2 - 10,
                      "Ядро чипа", size=15, bold=True, color="#1a1a1a"))
    frags.append(text(chip_x + chip_w / 2, chip_y + chip_h / 2 + 12,
                      "(логіка, CPU, пам'ять)", size=11, color="#6b7280"))

    # ── Виводи (ліворуч і праворуч від корпусу) ───────────────────────────
    pin_pairs = [
        # (зовнішній x зліва, внутр. x зліва, y, label)
        (140, 260, 130, "PIN_A"),
        (140, 260, 170, "PIN_B"),
        (140, 260, 210, "PIN_C"),
        (140, 260, 250, "PIN_D"),
    ]
    pin_right_pairs = [
        (520, 640, 130, "PIN_E"),
        (520, 640, 170, "PIN_F"),
        (520, 640, 210, "PIN_G"),
        (520, 640, 250, "PIN_H"),
    ]

    def draw_pin_with_cell(frags, xin, xout, y, label, side="left"):
        # Дріт виводу
        frags.append(line(xin, y, xout, y, color=LINE, sw=1.5))
        # Клітинка (BSR cell): маленький прямокутник між ніжкою і ядром
        if side == "left":
            cx = xin + (xout - xin) * 0.55
        else:
            cx = xin + (xout - xin) * 0.45
        cell_w, cell_h = 28, 18
        frags.append(rect(cx - cell_w / 2, y - cell_h / 2, cell_w, cell_h,
                          fill="#fff8dc", stroke="#c0392b", sw=1.5, rx=3))
        frags.append(text(cx, y + 4, "BSR", size=8, color="#c0392b", bold=True))
        # Підпис ніжки зовні
        if side == "left":
            frags.append(text(xin - 8, y + 4, label, size=10,
                              color=INK, anchor="end"))
        else:
            frags.append(text(xout + 8, y + 4, label, size=10,
                              color=INK, anchor="start"))

    for xin, xout, y, lbl in pin_pairs:
        draw_pin_with_cell(frags, xin, xout, y, lbl, "left")
    for xin, xout, y, lbl in pin_right_pairs:
        draw_pin_with_cell(frags, xin, xout, y, lbl, "right")

    # ── Ланцюг (scan chain): вертикальні стрілки, що з'єднують клітинки ──
    # Ліва колонка BSR-клітинок — вертикальний ланцюг знизу вгору
    left_xs = [140 + (260 - 140) * 0.55] * 4
    left_ys = [130, 170, 210, 250]
    chain_color = "#27ae60"
    for i in range(len(left_ys) - 1):
        cx = left_xs[0]
        y1 = left_ys[i] + 9
        y2 = left_ys[i + 1] - 9
        frags.append(line(cx + 20, y1, cx + 20, y2,
                          color=chain_color, sw=1.5, dash="5,3"))

    # Права колонка BSR — ланцюг
    right_xs = [520 + (640 - 520) * 0.45] * 4
    right_ys = [130, 170, 210, 250]
    for i in range(len(right_ys) - 1):
        cx = right_xs[0]
        frags.append(line(cx + 20, right_ys[i] + 9,
                          cx + 20, right_ys[i + 1] - 9,
                          color=chain_color, sw=1.5, dash="5,3"))

    # Перехід ланцюга через корпус (верх і низ)
    # TDI → перша ліва клітинка (зверху)
    tdi_x = 100
    frags.append(line(tdi_x, 100, left_xs[0] + 20, 100,
                      color=chain_color, sw=2))
    frags.append(text(tdi_x - 6, 104, "TDI", size=11, bold=True,
                      color=chain_color, anchor="end"))

    # Ланцюг проходить «через ядро» (горизонтальна пунктирна лінія внизу)
    bottom_y = 280
    frags.append(line(left_xs[0] + 20, bottom_y,
                      right_xs[0] + 20, bottom_y,
                      color=chain_color, sw=1.5, dash="4,4"))
    frags.append(text((left_xs[0] + right_xs[0]) / 2 + 20, bottom_y + 14,
                      "scan chain (через ядро)", size=9, color=chain_color))

    # TDO ← остання права клітинка (внизу)
    tdo_x = 680
    frags.append(line(right_xs[0] + 20, 250,
                      tdo_x + 30, 250, color=chain_color, sw=2))
    frags.append(text(tdo_x + 36, 254, "TDO", size=11, bold=True,
                      color=chain_color, anchor="start"))

    # ── Позначки режимів (легенда) ────────────────────────────────────────
    leg_x, leg_y = 30, 340
    tb, _, _ = textbox(leg_x + 120, leg_y, "Нормальний режим:\nBSR прозора — сигнал\nпроходить наскрізь",
                       size=11, fill="#f0fff0", stroke=FIELD, pad=8)
    frags.append(tb)
    tb2, _, _ = textbox(leg_x + 380, leg_y, "Тестовий режим:\nBSR перехоплює вхід,\nвиставляє заданий рівень",
                        size=11, fill="#fff8dc", stroke="#c0392b", pad=8)
    frags.append(tb2)

    # ── Підпис-заголовок ──────────────────────────────────────────────────
    frags.append(text(W / 2, 38, "Boundary Scan: «цвяхи» всередині кремнію",
                      size=15, bold=True, color=INK))
    frags.append(text(W / 2, 58,
                      "Кожна ніжка — своя BSR-клітинка; зонд читає/задає стани по ланцюгу,",
                      size=11, color=MUTED))
    frags.append(text(W / 2, 72, "не торкаючись ніжок фізично.",
                      size=11, color=MUTED))

    render(os.path.join(OUT, "fig-14-0-1-boundary-scan.svg"), W, H, *frags)
    print("  fig-14-0-1-boundary-scan.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.14.0.2 — TAP + scan chain: 4 дроти, кілька чипів у ланцюгу
# ══════════════════════════════════════════════════════════════════════════════
def fig_tap_scan_chain():
    W, H = 820, 400
    frags = []

    chain_color = "#27ae60"
    tap_fill = "#e8edf5"

    # ── Заголовок ─────────────────────────────────────────────────────────
    frags.append(text(W / 2, 32, "TAP і скан-ланцюг: 4 дроти на будь-яку кількість ніжок",
                      size=15, bold=True, color=INK))

    # ── Хост / зонд зліва ────────────────────────────────────────────────
    host_cx = 80
    tb_host, hw, hh = textbox(host_cx, 200, "Зонд\n(ПК+\nOpenOCD)",
                              size=12, fill="#fff3cd", stroke="#c0392b",
                              bold=False, pad=10)
    frags.append(tb_host)

    # ── 4 службові дроти ─────────────────────────────────────────────────
    wire_labels = ["TCK", "TMS", "TDI", "TDO"]
    wire_colors = [INK, "#c0392b", "#27ae60", "#2457d6"]
    wire_ys = [130, 160, 190, 220]
    chip1_x = 240

    for i, (lbl, col, wy) in enumerate(zip(wire_labels, wire_colors, wire_ys)):
        frags.append(line(host_cx + hw / 2, wy, chip1_x - 2, wy,
                          color=col, sw=2))
        frags.append(text(host_cx + hw / 2 + 8, wy - 6, lbl,
                          size=10, color=col, bold=True, anchor="start"))

    # ── Чип 1 ─────────────────────────────────────────────────────────────
    def draw_chip(cx, cy, label, sub=""):
        cw, ch = 140, 160
        frags.append(rect(cx, cy - ch / 2, cw, ch,
                          fill=tap_fill, stroke="#2457d6", sw=2, rx=6))
        # TAP автомат
        tap_cx = cx + cw / 2
        tap_cy = cy - 20
        tb_tap, tw, th = textbox(tap_cx, tap_cy, "TAP\nавтомат",
                                 size=11, fill="#dde4f5", stroke="#2457d6",
                                 pad=6)
        frags.append(tb_tap)
        # Ядро / scan chain box
        tb_core, tcw, tch = textbox(tap_cx, cy + 45, "Scan chain\n(BSR-клітинки)",
                                    size=10, fill="#fff8dc", stroke="#c0392b",
                                    pad=5)
        frags.append(tb_core)
        frags.append(text(tap_cx, cy - ch / 2 + 14, label,
                          size=12, bold=True, color=INK))
        if sub:
            frags.append(text(tap_cx, cy - ch / 2 + 28, sub,
                              size=10, color=MUTED))

    draw_chip(chip1_x, 205, "Чип 1")

    chip2_x = 490
    draw_chip(chip2_x, 205, "Чип 2")

    # ── Горизонтальні дроти TCK/TMS (паралельно обом чипам) ─────────────
    # TCK і TMS йдуть до обох чипів
    for wy, col in zip([130, 160], [INK, "#c0392b"]):
        # вже намальовано до chip1; продовжуємо від правого краю chip1 до chip2
        frags.append(line(chip1_x + 140, wy, chip2_x - 2, wy, color=col, sw=2))
    # Вертикальні «відгалуження» всередину чипів (просто позначення)
    for cx_chip in [chip1_x, chip2_x]:
        for wy in [130, 160]:
            frags.append(circle(cx_chip + 2, wy, 4, fill=FILL, stroke=LINE, sw=1.5))

    # ── TDI → Чип 1 → (TDO₁ = TDI₂) → Чип 2 → TDO ─────────────────────
    # TDI до Чип 1 — вже намальовано (190)
    tdi_y = 190
    tdo_y = 220
    # TDO Чип 1 → TDI Чип 2 (зелений)
    link_y = 260
    frags.append(line(chip1_x + 140, tdi_y, chip1_x + 170, tdi_y,
                      color=chain_color, sw=2))
    frags.append(line(chip1_x + 170, tdi_y, chip1_x + 170, link_y,
                      color=chain_color, sw=2))
    frags.append(line(chip1_x + 170, link_y, chip2_x + 70, link_y,
                      color=chain_color, sw=2))
    frags.append(line(chip2_x + 70, link_y, chip2_x + 70, tdi_y,
                      color=chain_color, sw=2))
    frags.append(line(chip2_x + 70, tdi_y, chip2_x + 140, tdi_y,
                      color=chain_color, sw=2))
    tb_link, _, _ = textbox(chip1_x + 170 + (chip2_x + 70 - chip1_x - 170) / 2,
                             link_y + 16,
                             "TDO₁ → TDI₂",
                             size=10, fill="#f0fff0", stroke=chain_color, pad=5)
    frags.append(tb_link)

    # TDO Чип 2 → правий кінець (синій)
    tdo_end_x = chip2_x + 140 + 50
    frags.append(line(chip2_x + 140, tdo_y, tdo_end_x, tdo_y,
                      color="#2457d6", sw=2))
    frags.append(text(tdo_end_x + 6, tdo_y + 4, "TDO",
                      size=11, bold=True, color="#2457d6", anchor="start"))

    # ── Підпис знизу ─────────────────────────────────────────────────────
    tb_note, _, _ = textbox(W / 2, H - 36,
                            "Скільки б ніжок не мав чип — службових дротів завжди 4.\n"
                            "TDO одного чипа → TDI наступного: один тонкий канал бачить весь ланцюг.",
                            size=11, fill="#f4f6f8", stroke=MUTED, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-14-0-2-tap-scan-chain.svg"), W, H, *frags)
    print("  fig-14-0-2-tap-scan-chain.svg — OK")


if __name__ == "__main__":
    print("Генерація фігур для r14-history-jtag …")
    fig_boundary_scan()
    fig_tap_scan_chain()
    print("Готово.")
