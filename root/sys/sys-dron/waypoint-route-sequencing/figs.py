# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми waypoint-route-sequencing."""

import os
import sys

# Підключення svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_acceptance_criteria():
    """Фігура 1: Куля досягнення (Acceptance Radius) та площина прольоту (Passing Plane)."""
    W, H = 760, 420
    frags = []

    # Фон-сітка / розмежувачі
    frags.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#e1e4e8", sw=1, rx=8))

    # Точки маршруту
    w1_x, w1_y = 80, 310
    w2_x, w2_y = 380, 130
    w3_x, w3_y = 680, 310

    # Сегменти маршруту (бажана траєкторія)
    frags.append(line(w1_x, w1_y, w2_x, w2_y, color="#9ca3af", sw=2, dash="5,5"))
    frags.append(line(w2_x, w2_y, w3_x, w3_y, color="#9ca3af", sw=2, dash="5,5"))

    # Куля досягнення (Acceptance Sphere / Circle) навколо W_k
    r_acc = 65
    frags.append(circle(w2_x, w2_y, r_acc, fill="#e8f5e9", stroke=FIELD, sw=1.8))
    frags.append(line(w2_x, w2_y, w2_x + r_acc * 0.707, w2_y - r_acc * 0.707, color=FIELD, sw=1.5))
    frags.append(text(w2_x + 36, w2_y - 30, "R_acc", size=11, color=FIELD, bold=True))

    # Площина прольоту (Passing Plane / Half-Plane) через W_k
    pp_x1, pp_y1 = w2_x - 55, w2_y - 95
    pp_x2, pp_y2 = w2_x + 55, w2_y + 95
    frags.append(line(pp_x1, pp_y1, pp_x2, pp_y2, color=POS, sw=2, dash="6,4"))

    # Пояснення площини прольоту (через textbox, щоб гарантовано мати фон)
    t_box, _, _ = textbox(w2_x + 130, w2_y - 80, "Площина прольоту\n(P − W_k) · u ≥ 0", size=11, fill="#fff5f5", stroke=POS, pad=6)
    frags.append(t_box)

    # Траєкторія 1: Номінальне влучання в кулю
    path_nom = (
        f'<path d="M {w1_x} {w1_y} Q {w2_x - 30} {w2_y + 40} {w2_x + 10} {w2_y - 10} '
        f'T {w3_x} {w3_y}" fill="none" stroke="{NEG}" stroke-width="2.5"/>'
    )
    frags.append(path_nom)
    t1_box, _, _ = textbox(190, 180, "Траєкторія 1:\nвхід у R_acc", size=10, fill="#eff6ff", stroke=NEG, pad=5)
    frags.append(t1_box)

    # Траєкторія 2: Промах повз R_acc (знос вітром/велика швидкість), але перетин площини
    path_drift = (
        f'<path d="M {w1_x} {w1_y + 25} C {w2_x - 80} {w2_y + 130} {w2_x + 50} {w2_y + 95} '
        f'{w2_x + 90} {w2_y + 90} S {w3_x - 30} {w3_y + 20} {w3_x} {w3_y}" fill="none" stroke="{POS}" stroke-width="2.2" stroke-dasharray="7,3"/>'
    )
    frags.append(path_drift)
    t2_box, _, _ = textbox(570, 180, "Траєкторія 2: промах повз R_acc,\nперетин площини запобігає зацикленню", size=10, fill="#fff5f5", stroke=POS, pad=5)
    frags.append(t2_box)

    # Точки W1, W2, W3
    for px, py, name, sub in [(w1_x, w1_y, "W", "k−1"), (w2_x, w2_y, "W", "k"), (w3_x, w3_y, "W", "k+1")]:
        frags.append(circle(px, py, 6, fill=INK, stroke="#ffffff", sw=2))
        frags.append(text(px, py + 22, f"{name}_{sub}", size=12, color=INK, bold=True))

    # Вектор сегмента u
    frags.append(arrow(w2_x - 90, w2_y + 90, w2_x - 40, w2_y + 60, color="#4b5563", sw=2))
    frags.append(text(w2_x - 75, w2_y + 60, "вектор u", size=10, color="#4b5563", italic=True))

    # Інформаційний бейдж унизу
    info_box, _, _ = textbox(
        W / 2, 385,
        "Умова спрацьовування: ||P − W_k|| ≤ R_acc  АБО  (P − W_k) · u ≥ 0 (перетин площини)",
        size=11, fill="#ffffff", stroke="#cbd5e1", pad=6
    )
    frags.append(info_box)

    render(os.path.join(OUT, "acceptance-criteria.svg"), W, H, *frags)


def fig_fly_over_vs_fly_through():
    """Фігура 2: Зупинка в точці (Fly-Over) проти плавного обльоту (Fly-Through / Spline)."""
    W, H = 760, 390
    frags = []

    # Розділювач панелей
    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=8))
    frags.append(line(W / 2, 15, W / 2, H - 15, color="#e5e7eb", sw=1.5, dash="4,4"))

    # ── Ліва панель: Fly-Over (Stop at Waypoint) ──
    frags.append(text(W / 4, 38, "Fly-Over (Зупинка в точці)", size=14, color=INK, bold=True))

    lx1, ly1 = 50, 180
    lx2, ly2 = 200, 75
    lx3, ly3 = 330, 180

    # Опорні відрізки
    frags.append(line(lx1, ly1, lx2, ly2, color="#9ca3af", sw=1.5, dash="4,4"))
    frags.append(line(lx2, ly2, lx3, ly3, color="#9ca3af", sw=1.5, dash="4,4"))

    # Траєкторія польоту: пряма до W2, зупинка, поворот на місці, пряма до W3
    frags.append(arrow(lx1, ly1, lx2 - 5, ly2 + 4, color=POS, sw=2.5))
    frags.append(arrow(lx2, ly2, lx3, ly3, color=POS, sw=2.5))

    # Точки
    frags.append(circle(lx1, ly1, 5, fill=INK, stroke="#fff", sw=1.5))
    frags.append(circle(lx2, ly2, 6, fill=POS, stroke="#fff", sw=2))
    frags.append(circle(lx3, ly3, 5, fill=INK, stroke="#fff", sw=1.5))

    frags.append(text(lx1, ly1 + 18, "W_k−1", size=11, color=INK))
    frags.append(text(lx2, ly2 - 14, "W_k (v = 0)", size=11, color=POS, bold=True))
    frags.append(text(lx3, ly3 + 18, "W_k+1", size=11, color=INK))

    # Опис фази зависання
    box_hold, _, _ = textbox(lx2, ly2 + 48, "Гальмування → v = 0\nЗатримка t_hold\nПоворот курсу на місці", size=10, fill="#fef2f2", stroke=POS, pad=5)
    frags.append(box_hold)

    # Профіль швидкості v(t) ліворуч
    frags.append(rect(45, 275, 290, 85, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(60, 292, "v(t)", size=11, color=MUTED, bold=True))
    # Вісь
    frags.append(line(75, 345, 315, 345, color="#64748b", sw=1))
    frags.append(line(75, 345, 75, 295, color="#64748b", sw=1))
    # Графік гальмування до нуля
    frags.append(line(75, 305, 140, 305, color=POS, sw=2))
    frags.append(line(140, 305, 185, 345, color=POS, sw=2))
    frags.append(line(185, 345, 215, 345, color=POS, sw=2.5))  # v=0
    frags.append(line(215, 345, 260, 305, color=POS, sw=2))
    frags.append(line(260, 305, 310, 305, color=POS, sw=2))
    frags.append(text(200, 335, "v = 0", size=10, color=POS, bold=True))

    # ── Права панель: Fly-Through (Spline / Corner Cutting) ──
    frags.append(text(3 * W / 4, 38, "Fly-Through (Плавний обліт)", size=14, color=INK, bold=True))

    rx1, ry1 = 430, 180
    rx2, ry2 = 580, 75
    rx3, ry3 = 710, 180

    # Опорні відрізки
    frags.append(line(rx1, ry1, rx2, ry2, color="#9ca3af", sw=1.5, dash="4,4"))
    frags.append(line(rx2, ry2, rx3, ry3, color="#9ca3af", sw=1.5, dash="4,4"))

    # Плавна дуга (Spline cornering)
    spline_path = (
        f'<path d="M {rx1} {ry1} L {rx2 - 55} {ry2 + 42} Q {rx2} {ry2 + 10} {rx2 + 55} {ry2 + 42} '
        f'L {rx3} {ry3}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>'
    )
    frags.append(spline_path)

    # Точки
    frags.append(circle(rx1, ry1, 5, fill=INK, stroke="#fff", sw=1.5))
    frags.append(circle(rx2, ry2, 6, fill="#9ca3af", stroke="#fff", sw=2))
    frags.append(circle(rx3, ry3, 5, fill=INK, stroke="#fff", sw=1.5))

    frags.append(text(rx1, ry1 + 18, "W_k−1", size=11, color=INK))
    frags.append(text(rx2, ry2 - 14, "W_k (обліт)", size=11, color=MUTED, bold=True))
    frags.append(text(rx3, ry3 + 18, "W_k+1", size=11, color=INK))

    # Радіус зрізання кута
    frags.append(f'<circle cx="{rx2}" cy="{ry2 + 50}" r="40" fill="none" stroke="#10b981" stroke-width="1.2" stroke-dasharray="3,3"/>')
    frags.append(text(rx2 + 46, ry2 + 35, "R_corner", size=10, color=FIELD, bold=True))

    box_spline, _, _ = textbox(rx2, ry2 + 105, "Швидкість стала (v > 0)\nЗрізання кута за радіусом\na_lat = v² / R ≤ a_max", size=10, fill="#f0fdf4", stroke=FIELD, pad=5)
    frags.append(box_spline)

    # Профіль швидкості v(t) праворуч
    frags.append(rect(425, 275, 290, 85, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(440, 292, "v(t)", size=11, color=MUTED, bold=True))
    frags.append(line(455, 345, 695, 345, color="#64748b", sw=1))
    frags.append(line(455, 345, 455, 295, color="#64748b", sw=1))
    # Стала швидкість без зупинок
    frags.append(line(455, 305, 695, 305, color=FIELD, sw=2.5))
    frags.append(text(575, 298, "v_cruise = const", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "fly-over-vs-fly-through.svg"), W, H, *frags)


def fig_yaw_modes():
    """Фігура 3: Три режими узгодження курсу (Yaw Coordination)."""
    W, H = 760, 360
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=8))

    # Три колонки: 1) Фіксований, 2) За маршрутом, 3) Наведення на ROI
    col_w = (W - 40) / 3
    c1 = 20 + col_w / 2
    c2 = 20 + col_w + col_w / 2
    c3 = 20 + 2 * col_w + col_w / 2

    # Розділювальні лінії
    frags.append(line(20 + col_w, 20, 20 + col_w, H - 20, color="#e5e7eb", sw=1.2, dash="4,4"))
    frags.append(line(20 + 2 * col_w, 20, 20 + 2 * col_w, H - 20, color="#e5e7eb", sw=1.2, dash="4,4"))

    # ── Режим 1: Фіксований курс ──
    frags.append(text(c1, 38, "1. Фіксований курс", size=13, color=INK, bold=True))
    frags.append(text(c1, 56, "Yaw = const (задано в param4)", size=10, color=MUTED))

    # Траєкторія
    frags.append(line(40, 230, 120, 100, color="#9ca3af", sw=1.5, dash="3,3"))
    frags.append(line(120, 100, 220, 180, color="#9ca3af", sw=1.5, dash="3,3"))

    # Дрони вздовж траєкторії (корпус дивиться завжди вгору: 0 град)
    for dx, dy in [(65, 190), (120, 100), (170, 140)]:
        frags.append(circle(dx, dy, 12, fill="#f1f5f9", stroke=LINE, sw=1.5))
        frags.append(arrow(dx, dy, dx, dy - 20, color=POS, sw=2))

    b1, _, _ = textbox(c1, 280, "Апарат летить боком/кутом,\nніс тримає фіксований азимут\n(для камер 360° або LiDAR)", size=10, fill="#f8fafc", stroke="#cbd5e1", pad=6)
    frags.append(b1)

    # ── Режим 2: Курс на наступну точку ──
    frags.append(text(c2, 38, "2. Курс за маршрутом", size=13, color=INK, bold=True))
    frags.append(text(c2, 56, "Yaw = atan2(Δy, Δx)", size=10, color=MUTED))

    # Траєкторія
    frags.append(line(280, 230, 380, 100, color="#9ca3af", sw=1.5, dash="3,3"))
    frags.append(line(380, 100, 480, 180, color="#9ca3af", sw=1.5, dash="3,3"))

    # Дрон на першому сегменті (ніс уздовж лінії 1)
    frags.append(circle(320, 180, 12, fill="#f1f5f9", stroke=LINE, sw=1.5))
    frags.append(arrow(320, 180, 335, 160, color=FIELD, sw=2))

    # Дрон на другому сегменті (ніс уздовж лінії 2)
    frags.append(circle(430, 140, 12, fill="#f1f5f9", stroke=LINE, sw=1.5))
    frags.append(arrow(430, 140, 448, 154, color=FIELD, sw=2))

    b2, _, _ = textbox(c2, 280, "Ніс апарата завжди націлений\nна поточну точку цілі W_k\n(мінімальний аеродинамічний опір)", size=10, fill="#f8fafc", stroke="#cbd5e1", pad=6)
    frags.append(b2)

    # ── Режим 3: Region of Interest (ROI) ──
    frags.append(text(c3, 38, "3. Наведення на ROI", size=13, color=INK, bold=True))
    frags.append(text(c3, 56, "Yaw = atan2(y_roi − y, x_roi − x)", size=10, color=MUTED))

    # Точка ROI в центрі знизу
    roi_x, roi_y = c3, 195
    frags.append(circle(roi_x, roi_y, 7, fill=POS, stroke="#ffffff", sw=2))
    frags.append(text(roi_x, roi_y + 18, "Ціль (ROI)", size=11, color=POS, bold=True))

    # Дуга польоту навколо ROI
    frags.append(line(540, 140, 630, 90, color="#9ca3af", sw=1.5, dash="3,3"))
    frags.append(line(630, 90, 720, 140, color="#9ca3af", sw=1.5, dash="3,3"))

    # Дрони спрямовані на ROI
    for dx, dy in [(560, 130), (630, 90), (700, 130)]:
        frags.append(circle(dx, dy, 12, fill="#f1f5f9", stroke=LINE, sw=1.5))
        vx = roi_x - dx
        vy = roi_y - dy
        vlen = (vx * vx + vy * vy) ** 0.5
        frags.append(arrow(dx, dy, dx + 22 * (vx / vlen), dy + 22 * (vy / vlen), color=NEG, sw=2))
        frags.append(line(dx, dy, roi_x, roi_y, color="#93c5fd", sw=1, dash="2,2"))

    b3, _, _ = textbox(c3, 280, "Апарат обертає корпус або підвіс\nна фіксовану точку інтересу ROI\nпід час польоту по дузі/галсах", size=10, fill="#f8fafc", stroke="#cbd5e1", pad=6)
    frags.append(b3)

    render(os.path.join(OUT, "yaw-modes.svg"), W, H, *frags)


def fig_sequencer_fsm():
    """Фігура 4: Автомат станів секвенсера місії (Mission Sequencer FSM)."""
    W, H = 760, 320
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#e1e4e8", sw=1, rx=8))

    # Блоки станів
    b_idle, _, _ = textbox(80, 90, "ST_IDLE\nОчікування", size=12, fill="#f1f5f9", stroke="#64748b", pad=8)
    frags.append(b_idle)

    b_nav, _, _ = textbox(250, 90, "ST_NAVIGATING\nРух до W_k", size=12, fill="#eff6ff", stroke=NEG, pad=8)
    frags.append(b_nav)

    b_hold, _, _ = textbox(450, 90, "ST_LOITER_HOLD\nЗатримка t_hold", size=12, fill="#fefce8", stroke="#ca8a04", pad=8)
    frags.append(b_hold)

    b_act, _, _ = textbox(650, 90, "ST_EXEC_ACTION\nДія (фото/скид)", size=12, fill="#fdf2f8", stroke="#db2777", pad=8)
    frags.append(b_act)

    b_adv, _, _ = textbox(450, 230, "ST_ADVANCE_WP\nseq++ / наступна точка", size=12, fill="#f0fdf4", stroke=FIELD, pad=8)
    frags.append(b_adv)

    b_done, _, _ = textbox(150, 230, "ST_MISSION_DONE\nКінець місії / RTL", size=12, fill="#f8fafc", stroke="#475569", pad=8)
    frags.append(b_done)

    # Стрілки переходів
    frags.append(arrow(130, 90, 185, 90, color=LINE, sw=1.8))
    frags.append(text(158, 76, "Старт", size=10, color=MUTED))

    frags.append(arrow(315, 90, 375, 90, color=LINE, sw=1.8))
    frags.append(text(345, 76, "Досягнуто W_k", size=9, color=MUTED))

    frags.append(arrow(525, 90, 575, 90, color=LINE, sw=1.8))
    frags.append(text(550, 76, "Таймаут", size=10, color=MUTED))

    frags.append(arrow(270, 125, 375, 215, color=FIELD, sw=1.8))
    frags.append(text(285, 175, "Плавний обліт", size=9, color=FIELD, bold=True))

    frags.append(arrow(650, 125, 520, 215, color=LINE, sw=1.8))
    frags.append(text(620, 175, "Дію виконано", size=9, color=MUTED))

    frags.append(arrow(430, 205, 275, 125, color=NEG, sw=1.8))
    frags.append(text(380, 155, "seq < N", size=9, color=NEG, bold=True))

    frags.append(arrow(370, 230, 235, 230, color=LINE, sw=1.8))
    frags.append(text(300, 218, "seq == N", size=9, color=MUTED))

    render(os.path.join(OUT, "sequencer-fsm.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_acceptance_criteria()
    fig_fly_over_vs_fly_through()
    fig_yaw_modes()
    fig_sequencer_fsm()
    print("Всі 4 фігури успішно згенеровано у", OUT)
