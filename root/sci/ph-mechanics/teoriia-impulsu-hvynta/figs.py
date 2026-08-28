# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми: Теорія імпульсу гвинта (teoriia-impulsu-hvynta)."""

import os
import sys
import math

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_streamtube():
    """Фігура 1: Струмна трубка ідеального актуаторного диска (Actuator Disk)."""
    w, h = 820, 520
    frags = []

    # Фон і сітка перерізів
    # Центральна вісь z (вертикальна вісь симетрії)
    cx = 410
    frags.append(line(cx, 40, cx, 470, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(cx + 8, 55, "вісь z (напрямок потоку)", size=12, color=MUTED, anchor="start", italic=True))

    # Струмна трубка (контур звуження)
    # Згори (z -> -inf) широкий вхід, на диску (z=0, y=250) радіус R=140, внизу (z -> +inf) радіус R/sqrt(2) = 99
    # Криві струмин (ліва й права)
    path_left = (
        "M 190,70 "
        "C 210,130 245,190 270,250 "
        "C 290,300 305,360 311,440"
    )
    path_right = (
        "M 630,70 "
        "C 610,130 575,190 550,250 "
        "C 530,300 515,360 509,440"
    )
    # Заливка струйної трубки
    stream_fill = (
        '<path d="' + path_left + ' L 509,440 ' +
        'C 515,360 530,300 550,250 ' +
        'C 575,190 610,130 630,70 Z" '
        'fill="#edf4fd" stroke="none" opacity="0.6"/>'
    )
    frags.append(stream_fill)
    frags.append('<path d="' + path_left + '" fill="none" stroke="#2457d6" stroke-width="2"/>')
    frags.append('<path d="' + path_right + '" fill="none" stroke="#2457d6" stroke-width="2"/>')

    # Додаткові внутрішні лінії течії
    frags.append('<path d="M 300,70 C 315,130 335,190 345,250 C 353,300 360,360 362,440" fill="none" stroke="#90b4f0" stroke-width="1.2" stroke-dasharray="3,3"/>')
    frags.append('<path d="M 520,70 C 505,130 485,190 475,250 C 467,300 460,360 458,440" fill="none" stroke="#90b4f0" stroke-width="1.2" stroke-dasharray="3,3"/>')

    # Стрілки напрямку течії
    frags.append(arrow(345, 170, 348, 205, color=NEG, sw=1.5))
    frags.append(arrow(410, 150, 410, 195, color=NEG, sw=1.5))
    frags.append(arrow(475, 170, 472, 205, color=NEG, sw=1.5))

    frags.append(arrow(360, 310, 362, 355, color=NEG, sw=1.5))
    frags.append(arrow(410, 310, 410, 360, color=NEG, sw=1.5))
    frags.append(arrow(460, 310, 458, 355, color=NEG, sw=1.5))

    # 1. Переріз 0 (далекий вхід): z << 0, y=70
    frags.append(line(160, 70, 660, 70, color=LINE, sw=1.2, dash="5,3"))
    box0, _, _ = textbox(110, 70, "Переріз 0 (вхід)\nv₀ = 0 (висіння)\np = p₀ (атмосферний)", size=12, fill="#f8fafc", stroke=MUTED, pad=6)
    frags.append(box0)

    # 2. Площина актуаторного диска: z = 0, y=250
    # Сам диск
    disk_y = 250
    disk_x1, disk_x2 = 270, 550
    frags.append(rect(disk_x1, disk_y - 6, disk_x2 - disk_x1, 12, fill="#fed7aa", stroke=POS, sw=2.2, rx=3))
    # Позначення лопатей / диска
    frags.append(text(cx, disk_y + 4, "Актуаторний диск (площа A = π R²)", size=13, color=POS, bold=True, anchor="middle"))

    # Вектор тяги T угору
    frags.append(arrow(cx, disk_y - 8, cx, disk_y - 68, color=POS, sw=3))
    frags.append(text(cx + 12, disk_y - 45, "Тяга T (вгору)", size=13, color=POS, bold=True, anchor="start"))

    # Стрибок тиску на диску
    box_disk, _, _ = textbox(110, 250, "Площина диска (z = 0)\nШвидкість: v_i\nЗверху: p⁻ = p₀ − ½ρ v_i²\nЗнизу: p⁺ = p₀ + ½ρ w² − ½ρ v_i²\nСтрибок: Δp = p⁺ − p⁻ = 2ρ v_i²", size=11, fill="#fff7ed", stroke=POS, pad=6)
    frags.append(box_disk)

    # 3. Переріз w (далекий слід / vena contracta): z >> 0, y=440
    frags.append(line(260, 440, 560, 440, color=LINE, sw=1.2, dash="5,3"))
    box_wake, _, _ = textbox(110, 440, "Далекий слід (z → +∞)\nШвидкість: w = 2·v_i\nТиск: p = p₀\nПлоща: A_w = A / 2", size=11, fill="#ecfdf5", stroke=FIELD, pad=6)
    frags.append(box_wake)

    # Права панель із висновками моделі
    right_box = fitbox(
        660, 160, 150, 200,
        "Ключові рівності:\n"
        "• ṁ = ρ·A·v_i\n"
        "• T = ṁ·w = 2·ρ·A·v_i²\n"
        "• w = 2·v_i\n"
        "• Δp = ½·ρ·w² = 2·ρ·v_i²\n"
        "• A_w = A / 2\n"
        "• P_i = T·v_i",
        size=11, pad=8, fill="#ffffff", stroke=LINE
    )
    frags.append(right_box)

    render(os.path.join(OUT_DIR, "actuator-disk-streamtube.svg"), w, h, *frags)


def fig_profiles():
    """Фігура 2: Розподіл швидкості v(z) та тиску p(z) вздовж струминної трубки."""
    w, h = 820, 480
    frags = []

    # Верхній графік: Швидкість v(z)
    top_y = 60
    top_h = 160
    # Вісь z
    frags.append(line(120, top_y + top_h - 20, 720, top_y + top_h - 20, color=LINE, sw=1.5))
    frags.append(arrow(700, top_y + top_h - 20, 735, top_y + top_h - 20, color=LINE, sw=1.5))
    frags.append(text(740, top_y + top_h - 16, "z", size=13, bold=True, anchor="start"))
    # Вісь v
    frags.append(line(160, top_y + top_h - 10, 160, top_y + 10, color=LINE, sw=1.5))
    frags.append(arrow(160, top_y + 20, 160, top_y - 5, color=LINE, sw=1.5))
    frags.append(text(150, top_y, "v(z)", size=13, bold=True, anchor="end"))

    # Лінія диска z = 0
    disc_x = 420
    frags.append(line(disc_x, top_y - 10, disc_x, 440, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(disc_x, top_y - 18, "диск (z = 0)", size=12, color=POS, bold=True, anchor="middle"))

    # Рівні швидкостей
    v0_y = top_y + top_h - 20
    vi_y = top_y + top_h - 80
    w_y = top_y + top_h - 140

    frags.append(line(155, vi_y, disc_x, vi_y, color=MUTED, sw=1, dash="2,2"))
    frags.append(text(150, vi_y + 4, "v_i", size=12, color=NEG, bold=True, anchor="end"))

    frags.append(line(155, w_y, 680, w_y, color=MUTED, sw=1, dash="2,2"))
    frags.append(text(150, w_y + 4, "w = 2·v_i", size=12, color=NEG, bold=True, anchor="end"))

    # Крива швидкості (плавна S-подібна крива від 0 до 2*v_i)
    curve_v = (
        f"M 160,{v0_y} "
        f"C 280,{v0_y} 340,{vi_y + 25} {disc_x},{vi_y} "
        f"C 500,{vi_y - 25} 560,{w_y} 680,{w_y}"
    )
    frags.append(f'<path d="{curve_v}" fill="none" stroke="#2457d6" stroke-width="2.8"/>')
    frags.append(circle(disc_x, vi_y, 4, fill=NEG, stroke=LINE, sw=1.2))
    frags.append(text(disc_x + 8, vi_y - 10, "v(0) = v_i (половина розгону)", size=11, color=NEG, anchor="start", bold=True))
    frags.append(text(680, w_y - 10, "w = 2·v_i (повний розгін)", size=11, color=NEG, anchor="end", bold=True))

    # Нижній графік: Тиск p(z)
    bot_y = 280
    bot_h = 160
    # Вісь z
    frags.append(line(120, bot_y + 80, 720, bot_y + 80, color=LINE, sw=1.5))
    frags.append(arrow(700, bot_y + 80, 735, bot_y + 80, color=LINE, sw=1.5))
    frags.append(text(740, bot_y + 84, "z", size=13, bold=True, anchor="start"))
    # Вісь p
    frags.append(line(160, bot_y + bot_h - 10, 160, bot_y + 10, color=LINE, sw=1.5))
    frags.append(arrow(160, bot_y + 20, 160, bot_y - 5, color=LINE, sw=1.5))
    frags.append(text(150, bot_y, "p(z)", size=13, bold=True, anchor="end"))

    # Атмосферний тиск p0 (горизонтальна лінія y = bot_y + 80)
    p0_y = bot_y + 80
    frags.append(line(155, p0_y, 700, p0_y, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(150, p0_y + 4, "p₀", size=12, color=INK, bold=True, anchor="end"))

    # Крива тиску до диска: падає від p0 до p- = p0 - 0.5*rho*vi^2
    p_minus_y = p0_y + 45
    p_plus_y = p0_y - 65

    curve_p_up = f"M 160,{p0_y} C 280,{p0_y} 350,{p_minus_y - 5} {disc_x},{p_minus_y}"
    frags.append(f'<path d="{curve_p_up}" fill="none" stroke="#c0392b" stroke-width="2.5"/>')

    # Стрибок тиску на диску (вертикальна пряма від p- до p+)
    frags.append(line(disc_x, p_minus_y, disc_x, p_plus_y, color=POS, sw=3))
    frags.append(circle(disc_x, p_minus_y, 4, fill=POS, stroke=LINE, sw=1.2))
    frags.append(circle(disc_x, p_plus_y, 4, fill=POS, stroke=LINE, sw=1.2))

    # Стрілка стрибка тиску Delta p
    frags.append(arrow(disc_x + 15, p_minus_y, disc_x + 15, p_plus_y, color=POS, sw=2))
    frags.append(text(disc_x + 24, (p_minus_y + p_plus_y) / 2 + 4, "Δp = 2·ρ·v_i²", size=12, color=POS, bold=True, anchor="start"))

    # Крива тиску після диска: спадає від p+ назад до p0
    curve_p_down = f"M {disc_x},{p_plus_y} C 490,{p_plus_y + 5} 570,{p0_y} 680,{p0_y}"
    frags.append(f'<path d="{curve_p_down}" fill="none" stroke="#c0392b" stroke-width="2.5"/>')

    # Пояснювальні підписи
    frags.append(text(disc_x - 12, p_minus_y + 16, "p⁻ = p₀ − ½ρ v_i² (розрідження)", size=11, color=POS, anchor="end"))
    frags.append(text(disc_x - 12, p_plus_y - 6, "p⁺ = p₀ + 3/2 ρ v_i² (підпір)", size=11, color=POS, anchor="end"))
    frags.append(text(680, p0_y - 12, "тиск відновлюється до p₀", size=11, color=MUTED, anchor="end"))

    render(os.path.join(OUT_DIR, "pressure-velocity-distribution.svg"), w, h, *frags)


def fig_power_vs_disk_loading():
    """Фігура 3: Питома тяга PL (Н/кВт) проти питомого навантаження на диск DL (Н/м²)."""
    w, h = 820, 520
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Питома тяга висіння залежно від навантаження на диск (DL = T / A)", size=15, bold=True))

    # Рамка графіка
    gx, gy, gw, gh = 100, 60, 660, 400
    frags.append(rect(gx, gy, gw, gh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=0))

    # Сітка (логарифмічний масштаб по обох осях)
    # X: DL від 1 до 100 000 Н/м² (5 декад: 1, 10, 100, 1000, 10000, 100000)
    x_decades = [1, 10, 100, 1000, 10000, 100000]
    for i, d in enumerate(x_decades):
        x = gx + i * (gw / 5)
        frags.append(line(x, gy, x, gy + gh, color="#e5e7eb", sw=1))
        frags.append(text(x, gy + gh + 18, f"{d}", size=11, color=INK, anchor="middle"))
    frags.append(text(gx + gw / 2, gy + gh + 38, "Навантаження на диск DL = T / A (Н/м²)", size=12, bold=True, anchor="middle"))

    # Y: PL від 1 до 1000 Н/кВт (3 декади: 1, 10, 100, 1000)
    y_decades = [1, 10, 100, 1000]
    for j, val in enumerate(y_decades):
        y = gy + gh - j * (gh / 3)
        frags.append(line(gx, y, gx + gw, y, color="#e5e7eb", sw=1))
        frags.append(text(gx - 10, y + 4, f"{val}", size=11, color=INK, anchor="end"))
    frags.append(text(gx - 45, gy + gh / 2, "Питома тяга PL = T / P (Н/кВт)", size=12, bold=True, anchor="middle"))

    # Функції відображення координат
    def map_coords(dl, pl):
        log_x = math.log10(dl)
        x = gx + (log_x / 5.0) * gw
        log_y = math.log10(pl)
        y = (gy + gh) - (log_y / 3.0) * gh
        return x, y

    # Теоретична крива ідеального диска
    pts = []
    for step in range(0, 101):
        log_dl = step * (5.0 / 100.0)
        dl = 10 ** log_dl
        pl_ideal = math.sqrt(2.0 * 1.225 / dl) * 1000.0
        x, y = map_coords(dl, pl_ideal)
        pts.append(f"{x:.1f},{y:.1f}")
    frags.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#2457d6" stroke-width="3"/>')

    # Реальна крива з FM = 0.65
    pts_real = []
    for step in range(0, 101):
        log_dl = step * (5.0 / 100.0)
        dl = 10 ** log_dl
        pl_real = 0.65 * math.sqrt(2.0 * 1.225 / dl) * 1000.0
        x, y = map_coords(dl, pl_real)
        pts_real.append(f"{x:.1f},{y:.1f}")
    frags.append(f'<polyline points="{" ".join(pts_real)}" fill="none" stroke="#c0392b" stroke-width="2.2" stroke-dasharray="5,4"/>')

    # Підписи до кривих
    x_lbl, y_lbl = map_coords(8, 550)
    frags.append(text(x_lbl, y_lbl - 6, "Ідеальна межа (FM = 1.0): PL = √(2ρ / DL)", size=12, color=NEG, bold=True, anchor="start"))
    x_lbl2, y_lbl2 = map_coords(15, 230)
    frags.append(text(x_lbl2, y_lbl2 + 16, "Реальні гвинти (FM ≈ 0.65)", size=12, color=POS, bold=True, anchor="start"))

    # Маркери типів апаратів
    data_points = [
        ("Мускулоліт\n(Gossamer Albatross)", 3.5, 480, "#16a34a"),
        ("Легкий вертоліт\n(Robinson R22)", 150, 75, "#0284c7"),
        ("Важкий вертоліт\n(Мі-26 / CH-53)", 550, 42, "#0369a1"),
        ("Квадрокоптер\n(DJI 15\" props)", 320, 52, "#d97706"),
        ("FPV-дрон\n(5\" props)", 2600, 18, "#ea580c"),
        ("Конвертоплан\n(V-22 Osprey)", 1300, 26, "#7c3aed"),
        ("СВВП з ТРД\n(Harrier / F-35B)", 45000, 4.2, "#b91c1c")
    ]

    for label, dl, pl, col in data_points:
        px, py = map_coords(dl, pl)
        frags.append(circle(px, py, 5, fill=col, stroke=LINE, sw=1.5))
        lines = label.split("\n")
        dx, dy = 8, -6
        anchor = "start"
        if dl > 10000:
            dx, dy = -10, -10
            anchor = "end"
        elif dl > 1000:
            dx, dy = 10, 12
        elif dl < 10:
            dx, dy = 12, 10

        frags.append(mtext(px + dx, py + dy, lines, size=10, color=col, bold=True, anchor=anchor))

    render(os.path.join(OUT_DIR, "power-loading-vs-disk-loading.svg"), w, h, *frags)


def fig_figure_of_merit():
    """Фігура 4: Баланс потужностей та структура втрат реального гвинта (Figure of Merit)."""
    w, h = 820, 460
    frags = []

    frags.append(text(w / 2, 28, "Структура потужності реального гвинта на висінні та Figure of Merit (FM)", size=15, bold=True))

    # Ліва частина: Стовпчикова діаграма розкладу потужності на валу P_shaft
    bx, by, bw, bh = 80, 70, 280, 350
    frags.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(bx + bw / 2, by + 26, "Баланс потужності на валу P_shaft", size=13, bold=True))

    # Стовпчик 100% потужності
    bar_x = bx + 40
    bar_w = 70
    bar_base_y = by + bh - 40

    # 1. Ідеальна індукована потужність P_i (65% = 156 px)
    h_pi = 156
    y_pi = bar_base_y - h_pi
    frags.append(rect(bar_x, y_pi, bar_w, h_pi, fill="#bfdbfe", stroke=NEG, sw=1.5, rx=0))
    frags.append(text(bar_x + bar_w / 2, y_pi + h_pi / 2 + 4, "P_i (65%)\n(ідеал)", size=11, color=NEG, bold=True, anchor="middle"))

    # 2. Кінцеві вихори та закрутка (κ-1)*P_i (12% = 29 px)
    h_tip = 29
    y_tip = y_pi - h_tip
    frags.append(rect(bar_x, y_tip, bar_w, h_tip, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=0))
    frags.append(text(bar_x + bar_w / 2, y_tip + h_tip / 2 + 4, "ΔP_ind (12%)", size=9, color="#9a3412", bold=True, anchor="middle"))

    # 3. Профільні втрати тертя лопатей P_0 (23% = 55 px)
    h_prof = 55
    y_prof = y_tip - h_prof
    frags.append(rect(bar_x, y_prof, bar_w, h_prof, fill="#fecaca", stroke=POS, sw=1.5, rx=0))
    frags.append(text(bar_x + bar_w / 2, y_prof + h_prof / 2 + 4, "P_0 (23%)\n(профіль)", size=10, color=POS, bold=True, anchor="middle"))

    # Пояснення поруч зі стовпчиком
    tx = bar_x + bar_w + 15
    frags.append(text(tx, y_prof + 20, "Профільний опір лопатей (P₀)", size=11, color=POS, bold=True, anchor="start"))
    frags.append(text(tx, y_tip + 16, "Кінцеві втрати й закрутка (κ ≈ 1.15)", size=10, color="#9a3412", anchor="start"))
    frags.append(text(tx, y_pi + 70, "Ідеальна індукована потужність:\nP_i = T^(3/2) / √(2·ρ·A)", size=11, color=NEG, bold=True, anchor="start"))

    # Формула FM знизу
    frags.append(rect(bx + 15, bar_base_y + 8, bw - 30, 24, fill="#eff6ff", stroke=NEG, sw=1, rx=3))
    frags.append(text(bx + bw / 2, bar_base_y + 24, "FM = P_ideal / P_actual ≈ 0.65", size=12, color=NEG, bold=True))

    # Права частина: Залежність Figure of Merit від навантаження лопаті C_T / sigma
    px, py, pw, ph = 400, 70, 380, 350
    frags.append(rect(px, py, pw, ph, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(px + pw / 2, py + 26, "Залежність FM від коефіцієнта тяги C_T", size=13, bold=True))

    # Осі графіка
    ax_x = px + 60
    ax_y = py + ph - 50
    ax_w = pw - 90
    ax_h = ph - 100

    frags.append(line(ax_x, ax_y, ax_x + ax_w, ax_y, color=LINE, sw=1.5))
    frags.append(arrow(ax_x + ax_w - 20, ax_y, ax_x + ax_w + 5, ax_y, color=LINE, sw=1.5))
    frags.append(text(ax_x + ax_w / 2, ax_y + 32, "Коефіцієнт тяги C_T (або кут установки лопатей)", size=11, bold=True, anchor="middle"))

    frags.append(line(ax_x, ax_y, ax_x, ax_y - ax_h, color=LINE, sw=1.5))
    frags.append(arrow(ax_x, ax_y - ax_h + 20, ax_x, ax_y - ax_h - 5, color=LINE, sw=1.5))
    frags.append(text(ax_x - 10, ax_y - ax_h - 6, "FM", size=12, bold=True, anchor="end"))

    # Позначки шкали FM: 0.0, 0.4, 0.8, 1.0
    for val, label in [(0.0, "0.0"), (0.4, "0.4"), (0.8, "0.8"), (1.0, "1.0 (ідеал)")]:
        y_pos = ax_y - (val / 1.0) * ax_h
        frags.append(line(ax_x - 4, y_pos, ax_x + ax_w, y_pos, color="#f1f5f9", sw=1))
        frags.append(text(ax_x - 8, y_pos + 4, label, size=10, color=MUTED, anchor="end"))

    # Теоретична верхня межа (пунктир на 1.0)
    y_ideal = ax_y - ax_h
    frags.append(line(ax_x, y_ideal, ax_x + ax_w, y_ideal, color=NEG, sw=1.2, dash="4,4"))

    # Крива FM(C_T)
    fm_curve = (
        f"M {ax_x},{ax_y} "
        f"C {ax_x + 40},{ax_y - 20} {ax_x + 90},{ax_y - 0.65 * ax_h} {ax_x + 140},{ax_y - 0.78 * ax_h} "
        f"C {ax_x + 190},{ax_y - 0.82 * ax_h} {ax_x + 230},{ax_y - 0.72 * ax_h} {ax_x + ax_w - 20},{ax_y - 0.35 * ax_h}"
    )
    frags.append(f'<path d="{fm_curve}" fill="none" stroke="#16a34a" stroke-width="2.8"/>')

    # Точка максимуму FM_max
    peak_x = ax_x + 155
    peak_y = ax_y - 0.79 * ax_h
    frags.append(circle(peak_x, peak_y, 4.5, fill="#16a34a", stroke=LINE, sw=1.5))
    frags.append(text(peak_x, peak_y - 12, "FM_max ≈ 0.75…0.80", size=11, color="#16a34a", bold=True, anchor="middle"))

    # Зони на графіку
    frags.append(text(ax_x + 45, ax_y - 45, "Домінує\nпрофільний опір P₀", size=9, color=MUTED, anchor="middle"))
    frags.append(text(ax_x + ax_w - 40, ax_y - 0.5 * ax_h, "Зрив потоку\nна лопатях", size=9, color=POS, anchor="middle"))

    render(os.path.join(OUT_DIR, "figure-of-merit-breakdown.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_streamtube()
    fig_profiles()
    fig_power_vs_disk_loading()
    fig_figure_of_merit()
    print("All figures generated successfully.")
