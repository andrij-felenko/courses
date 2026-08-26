# -*- coding: utf-8 -*-
"""Генератор векторних SVG-ілюстрацій для теми «Форми сигналу й шпаруватість»."""

import os
import sys
import math

# Підключення svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_waveform_shapes():
    """1. waveform-shapes.svg — П'ять класичних періодичних форм коливань."""
    w, h = 820, 560
    frags = []

    # Тло та заголовок панелі
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#e1e4e8", sw=1.5, rx=8))

    wave_types = [
        ("Синусоїда (Гармонічний синус)", "#2457d6", "sine"),
        ("Меандр (Симетричний прямокутник, D = 50%)", "#c0392b", "square"),
        ("Трикутний сигнал (Симетричний пил)", "#27ae60", "triangle"),
        ("Пилкоподібний сигнал (Sawtooth)", "#8e44ad", "sawtooth"),
        ("Імпульсна послідовність (Pulse Train, D = 25%)", "#d35400", "pulse25"),
    ]

    start_y = 55
    channel_h = 95
    plot_x = 260
    plot_w = 520
    period_px = 240  # 1 період = 240px (показуємо трохи більше 2 періодів)

    # Вертикальні лінії сітки періодів для всіх каналів
    for p_idx in range(3):
        gx = plot_x + p_idx * period_px
        frags.append(line(gx, start_y, gx, start_y + len(wave_types) * channel_h - 10, color="#d0d7de", sw=1, dash="4,4"))
        if p_idx < 2:
            mid_gx = gx + period_px / 2
            frags.append(line(mid_gx, start_y, mid_gx, start_y + len(wave_types) * channel_h - 10, color="#e8ecf0", sw=1, dash="2,3"))

    for idx, (title_text, color, wtype) in enumerate(wave_types):
        cy = start_y + idx * channel_h + 40
        y_amp = 30  # +/- 30 px

        # Рамка каналу
        frags.append(rect(20, start_y + idx * channel_h, w - 40, channel_h - 10, fill="#ffffff", stroke="#d0d7de", sw=1, rx=6))

        # Назва форми сигналу
        frags.append(text(30, cy - 8, title_text, size=13, color=color, anchor="start", bold=True))
        if wtype == "sine":
            frags.append(text(30, cy + 14, "Єдина чиста частота f0, нульові гармоніки", size=11, color=MUTED, anchor="start"))
        elif wtype == "square":
            frags.append(text(30, cy + 14, "Непарні гармоніки (1, 3, 5...), спад 1/n", size=11, color=MUTED, anchor="start"))
        elif wtype == "triangle":
            frags.append(text(30, cy + 14, "Непарні гармоніки (1, 3, 5...), спад 1/n²", size=11, color=MUTED, anchor="start"))
        elif wtype == "sawtooth":
            frags.append(text(30, cy + 14, "Усі гармоніки (парні й непарні), спад 1/n", size=11, color=MUTED, anchor="start"))
        elif wtype == "pulse25":
            frags.append(text(30, cy + 14, "Коефіцієнт заповнення D = 0.25 (S = 4)", size=11, color=MUTED, anchor="start"))

        # Нульова лінія (вісь часу)
        frags.append(line(plot_x - 10, cy, plot_x + plot_w + 10, cy, color="#8c959f", sw=1.2))
        frags.append(text(plot_x + plot_w + 16, cy + 4, "t", size=12, color=INK, anchor="start", italic=True))

        # Позначки амплітуди +A / -A
        frags.append(text(plot_x - 18, cy - y_amp + 4, "+A", size=10, color=MUTED, anchor="end"))
        frags.append(text(plot_x - 18, cy + y_amp + 4, "−A" if wtype != "pulse25" else "0", size=10, color=MUTED, anchor="end"))

        # Генерація точок форми хвилі
        pts = []
        if wtype == "sine":
            for px in range(plot_w + 1):
                t_rad = (px / period_px) * 2.0 * math.pi
                y_val = cy - y_amp * math.sin(t_rad)
                pts.append((plot_x + px, y_val))
            d_str = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            frags.append(f'<path d="{d_str}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')

        elif wtype == "square":
            d_parts = []
            for p_i in range(3):
                x0 = plot_x + p_i * period_px
                x_mid = x0 + period_px / 2
                x1 = x0 + period_px
                if p_i == 0:
                    d_parts.append(f"M {x0:.1f},{cy - y_amp:.1f}")
                d_parts.append(f"L {x_mid:.1f},{cy - y_amp:.1f}")
                d_parts.append(f"L {x_mid:.1f},{cy + y_amp:.1f}")
                d_parts.append(f"L {x1:.1f},{cy + y_amp:.1f}")
                if p_i < 2:
                    d_parts.append(f"L {x1:.1f},{cy - y_amp:.1f}")
            frags.append(f'<path d="{" ".join(d_parts)}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')

        elif wtype == "triangle":
            d_parts = []
            for p_i in range(3):
                x0 = plot_x + p_i * period_px
                x_q1 = x0 + period_px / 4
                x_q3 = x0 + 3 * period_px / 4
                x1 = x0 + period_px
                if p_i == 0:
                    d_parts.append(f"M {x0:.1f},{cy:.1f}")
                d_parts.append(f"L {x_q1:.1f},{cy - y_amp:.1f}")
                d_parts.append(f"L {x_q3:.1f},{cy + y_amp:.1f}")
                d_parts.append(f"L {x1:.1f},{cy:.1f}")
            frags.append(f'<path d="{" ".join(d_parts)}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')

        elif wtype == "sawtooth":
            d_parts = []
            for p_i in range(3):
                x0 = plot_x + p_i * period_px
                x1 = x0 + period_px
                if p_i == 0:
                    d_parts.append(f"M {x0:.1f},{cy + y_amp:.1f}")
                d_parts.append(f"L {x1:.1f},{cy - y_amp:.1f}")
                d_parts.append(f"L {x1:.1f},{cy + y_amp:.1f}")
            frags.append(f'<path d="{" ".join(d_parts)}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')

        elif wtype == "pulse25":
            d_parts = []
            for p_i in range(3):
                x0 = plot_x + p_i * period_px
                x_th = x0 + period_px * 0.25
                x1 = x0 + period_px
                if p_i == 0:
                    d_parts.append(f"M {x0:.1f},{cy - y_amp:.1f}")
                d_parts.append(f"L {x_th:.1f},{cy - y_amp:.1f}")
                d_parts.append(f"L {x_th:.1f},{cy + y_amp:.1f}")
                d_parts.append(f"L {x1:.1f},{cy + y_amp:.1f}")
                if p_i < 2:
                    d_parts.append(f"L {x1:.1f},{cy - y_amp:.1f}")
            frags.append(f'<path d="{" ".join(d_parts)}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')

    # Позначка періоду зверху
    top_y = 48
    frags.append(arrow(plot_x, top_y, plot_x + period_px, top_y, color=INK, sw=1.5))
    frags.append(arrow(plot_x + period_px, top_y, plot_x, top_y, color=INK, sw=1.5))
    frags.append(text(plot_x + period_px / 2, top_y - 6, "Період T = 1 / f", size=12, color=INK, bold=True))

    render(os.path.join(IMG_DIR, "waveform-shapes.svg"), w, h, *frags, title="Класичні форми періодичних коливань")


def fig_pulse_timing():
    """2. pulse-timing.svg — Часові параметри реального імпульсу (tr, tf, th, tl, T, рівні 10%-90%)."""
    w, h = 820, 520
    frags = []

    # Рамка полотна
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#e1e4e8", sw=1.5, rx=8))

    ox = 110
    oy = 390
    plot_w = 640
    amp_px = 240  # 100% амплітуда

    # Рівні у %
    levels = [
        (0.0, "0%", "Рівень нуля / паузи (Base)"),
        (0.1, "10%", "Нижній поріг перемикання (10%)"),
        (0.5, "50%", "Опорний поріг вимірювання тривалості (50%)"),
        (0.9, "90%", "Верхній поріг перемикання (90%)"),
        (1.0, "100%", "Усталена амплітуда A (Top)"),
    ]

    for frac, label_pct, desc in levels:
        ly = oy - frac * amp_px
        dash = "3,3" if frac in (0.1, 0.5, 0.9) else None
        color = "#8c959f" if frac in (0.1, 0.5, 0.9) else "#57606a"
        frags.append(line(ox - 30, ly, ox + plot_w + 30, ly, color=color, sw=1.2, dash=dash))
        frags.append(text(ox - 38, ly + 4, label_pct, size=11, color=color, anchor="end", bold=True))

    # Вісь часу
    frags.append(arrow(ox - 30, oy, ox + plot_w + 40, oy, color=INK, sw=1.8))
    frags.append(text(ox + plot_w + 45, oy + 4, "t", size=13, color=INK, anchor="start", italic=True))

    # Часові координати переходу
    t_start = ox + 40
    t_10_r = ox + 80
    t_50_r = ox + 105
    t_90_r = ox + 130
    t_peak_r = ox + 155

    t_fall_start = ox + 360
    t_90_f = ox + 385
    t_50_f = ox + 410
    t_10_f = ox + 435
    t_fall_end = ox + 465

    t_next_pulse = ox + 560

    # Побудова реальної форми імпульсу
    path_d = [
        f"M {ox - 20:.1f},{oy:.1f}",
        f"L {t_start:.1f},{oy:.1f}",
        f"C {t_start + 25:.1f},{oy:.1f} {t_10_r - 10:.1f},{oy - 0.1 * amp_px:.1f} {t_10_r:.1f},{oy - 0.1 * amp_px:.1f}",
        f"C {t_50_r - 15:.1f},{oy - 0.35 * amp_px:.1f} {t_50_r + 15:.1f},{oy - 0.65 * amp_px:.1f} {t_90_r:.1f},{oy - 0.9 * amp_px:.1f}",
        f"C {t_90_r + 10:.1f},{oy - 0.98 * amp_px:.1f} {t_peak_r - 10:.1f},{oy - 1.06 * amp_px:.1f} {t_peak_r:.1f},{oy - 1.06 * amp_px:.1f}",
        f"C {t_peak_r + 20:.1f},{oy - 1.06 * amp_px:.1f} {t_peak_r + 40:.1f},{oy - 0.98 * amp_px:.1f} {t_peak_r + 60:.1f},{oy - 1.0 * amp_px:.1f}",
        f"L {t_fall_start:.1f},{oy - 1.0 * amp_px:.1f}",
        f"C {t_fall_start + 15:.1f},{oy - 1.0 * amp_px:.1f} {t_90_f - 10:.1f},{oy - 0.9 * amp_px:.1f} {t_90_f:.1f},{oy - 0.9 * amp_px:.1f}",
        f"C {t_50_f - 15:.1f},{oy - 0.65 * amp_px:.1f} {t_50_f + 15:.1f},{oy - 0.35 * amp_px:.1f} {t_10_f:.1f},{oy - 0.1 * amp_px:.1f}",
        f"C {t_10_f + 10:.1f},{oy - 0.02 * amp_px:.1f} {t_fall_end - 10:.1f},{oy + 0.04 * amp_px:.1f} {t_fall_end:.1f},{oy + 0.04 * amp_px:.1f}",
        f"C {t_fall_end + 15:.1f},{oy + 0.04 * amp_px:.1f} {t_fall_end + 30:.1f},{oy:.1f} {t_fall_end + 50:.1f},{oy:.1f}",
        f"L {t_next_pulse:.1f},{oy:.1f}",
        f"C {t_next_pulse + 25:.1f},{oy:.1f} {t_next_pulse + 40:.1f},{oy - 0.2 * amp_px:.1f} {t_next_pulse + 55:.1f},{oy - 0.7 * amp_px:.1f}",
    ]
    frags.append(f'<path d="{" ".join(path_d)}" fill="none" stroke="#2457d6" stroke-width="3" stroke-linejoin="round"/>')

    # Вертикальні пунктири
    calipers_v = [
        (t_10_r, oy - 0.1 * amp_px, 440, "#c0392b"),
        (t_90_r, oy - 0.9 * amp_px, 440, "#c0392b"),
        (t_50_r, oy - 0.5 * amp_px, 475, "#27ae60"),
        (t_90_f, oy - 0.9 * amp_px, 440, "#8e44ad"),
        (t_10_f, oy - 0.1 * amp_px, 440, "#8e44ad"),
        (t_50_f, oy - 0.5 * amp_px, 475, "#27ae60"),
        (t_next_pulse + (t_50_r - t_start), oy - 0.5 * amp_px, 500, "#1a1a1a"),
    ]
    for vx, vy_top, vy_bot, vcol in calipers_v:
        frags.append(line(vx, vy_top, vx, vy_bot, color=vcol, sw=1, dash="3,3"))

    # 1. Час наростання tr
    tr_y = 430
    frags.append(arrow(t_10_r, tr_y, t_90_r, tr_y, color="#c0392b", sw=1.5))
    frags.append(arrow(t_90_r, tr_y, t_10_r, tr_y, color="#c0392b", sw=1.5))
    frags.append(text((t_10_r + t_90_r) / 2, tr_y - 6, "tr (10% → 90%)", size=11, color="#c0392b", bold=True))

    # 2. Час спаду tf
    tf_y = 430
    frags.append(arrow(t_90_f, tf_y, t_10_f, tf_y, color="#8e44ad", sw=1.5))
    frags.append(arrow(t_10_f, tf_y, t_90_f, tf_y, color="#8e44ad", sw=1.5))
    frags.append(text((t_90_f + t_10_f) / 2, tf_y - 6, "tf (90% → 10%)", size=11, color="#8e44ad", bold=True))

    # 3. Тривалість імпульсу th
    th_y = 465
    frags.append(arrow(t_50_r, th_y, t_50_f, th_y, color="#27ae60", sw=1.6))
    frags.append(arrow(t_50_f, th_y, t_50_r, th_y, color="#27ae60", sw=1.6))
    frags.append(text((t_50_r + t_50_f) / 2, th_y - 6, "th (Тривалість імпульсу на рівні 50%)", size=12, color="#27ae60", bold=True))

    # 4. Тривалість паузи tl
    t_next_50 = t_next_pulse + (t_50_r - t_start)
    tl_y = 465
    frags.append(arrow(t_50_f, tl_y, t_next_50, tl_y, color="#d35400", sw=1.6))
    frags.append(arrow(t_next_50, tl_y, t_50_f, tl_y, color="#d35400", sw=1.6))
    frags.append(text((t_50_f + t_next_50) / 2, tl_y - 6, "tl (Пауза)", size=12, color="#d35400", bold=True))

    # 5. Повний період T
    t_period_y = 495
    frags.append(arrow(t_50_r, t_period_y, t_next_50, t_period_y, color=INK, sw=1.8))
    frags.append(arrow(t_next_50, t_period_y, t_50_r, t_period_y, color=INK, sw=1.8))
    frags.append(text((t_50_r + t_next_50) / 2, t_period_y - 6, "Повний період T = th + tl", size=12, color=INK, bold=True))

    # Викид (overshoot)
    frags.append(line(t_peak_r, oy - 1.06 * amp_px, t_peak_r + 40, oy - 1.06 * amp_px - 25, color="#c0392b", sw=1.2))
    frags.append(text(t_peak_r + 45, oy - 1.06 * amp_px - 25, "Викид (Overshoot)", size=11, color="#c0392b", anchor="start", bold=True))

    # Інформаційна плашка
    info_box, _, _ = textbox(660, 95, "D = th / T (Коефіцієнт заповнення)\nS = T / th = 1 / D (Шпаруватість)\nBW ≈ 0.35 / tr (Смуга частот)", size=12, pad=10, fill="#f0f4f8", stroke="#2457d6", color=INK, bold=True)
    frags.append(info_box)

    render(os.path.join(IMG_DIR, "pulse-timing.svg"), w, h, *frags, title="Часові параметри та геометрія імпульсу")


def fig_duty_cycle_pwm():
    """3. duty-cycle-pwm.svg — Шпаруватість і коефіцієнт заповнення у формуванні середньої напруги (ШІМ)."""
    w, h = 820, 520
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#e1e4e8", sw=1.5, rx=8))

    panels = [
        ("D = 10% (Шпаруватість S = 10) — Мала середня потужність", 0.10, "#d35400"),
        ("D = 50% (Шпаруватість S = 2, Меандр) — Половина максимальної напруги", 0.50, "#2457d6"),
        ("D = 90% (Шпаруватість S = 1.11) — Висока середня потужність", 0.90, "#27ae60"),
    ]

    start_y = 50
    panel_h = 145
    plot_x = 80
    plot_w = 460
    period_px = 200
    v_max_px = 60

    for idx, (p_title, duty, color) in enumerate(panels):
        py = start_y + idx * panel_h
        cy = py + 95
        top_y = cy - v_max_px

        frags.append(rect(20, py, w - 40, panel_h - 10, fill="#ffffff", stroke="#d0d7de", sw=1, rx=6))
        frags.append(text(35, py + 22, p_title, size=13, color=color, anchor="start", bold=True))

        frags.append(line(plot_x - 10, cy, plot_x + plot_w + 15, cy, color="#8c959f", sw=1.2))
        frags.append(line(plot_x, cy + 10, plot_x, top_y - 15, color="#8c959f", sw=1.2))
        frags.append(text(plot_x - 12, top_y + 4, "Vmax", size=11, color=INK, anchor="end", bold=True))
        frags.append(text(plot_x - 12, cy + 4, "0", size=11, color=MUTED, anchor="end"))

        th_px = period_px * duty
        for p_i in range(2):
            x0 = plot_x + p_i * period_px
            x_th = x0 + th_px
            x1 = x0 + period_px

            frags.append(rect(x0, top_y, th_px, v_max_px, fill="#e8f0fe" if color == "#2457d6" else "#fef3eb" if color == "#d35400" else "#edf7ed", stroke="none"))

            frags.append(line(x0, cy, x0, top_y, color=color, sw=2))
            frags.append(line(x0, top_y, x_th, top_y, color=color, sw=2.2))
            frags.append(line(x_th, top_y, x_th, cy, color=color, sw=2))
            frags.append(line(x_th, cy, x1, cy, color=color, sw=2.2))

        avg_y = cy - duty * v_max_px
        frags.append(line(plot_x - 5, avg_y, plot_x + plot_w + 10, avg_y, color="#c0392b", sw=1.8, dash="5,3"))
        frags.append(circle(plot_x + plot_w + 10, avg_y, 3, fill="#c0392b", stroke="#c0392b"))

        val_pct = int(duty * 100)
        v_avg_str = f"Vavg = {duty:.2f} · Vmax ({val_pct}%)"
        v_rms_str = f"Vrms = {math.sqrt(duty):.3f} · Vmax"
        p_rel_str = f"P = {duty:.2f} · Pmax"
        f_box, _, _ = textbox(675, py + 65, f"{v_avg_str}\n{v_rms_str}\n{p_rel_str}", size=11, pad=8, fill="#f8fafc", stroke="#c0392b" if idx == 1 else "#d0d7de", color=INK, bold=True)
        frags.append(f_box)

    render(os.path.join(IMG_DIR, "duty-cycle-pwm.svg"), w, h, *frags, title="Регулювання середнього рівня напруги через коефіцієнт заповнення (ШІМ)")


def fig_harmonic_decay_spectrum():
    """4. harmonic-decay-spectrum.svg — Спектральний склад за Фур'є для меандру, пилки та трикутника."""
    w, h = 820, 500
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#e1e4e8", sw=1.5, rx=8))

    columns = [
        ("Меандр (Square Wave)", "Тільки непарні: 1, 3, 5, 7, 9...\nАмплітуди спадають як 1/n", "#c0392b", "square"),
        ("Пилкоподібний (Sawtooth)", "Усі гармоніки: 1, 2, 3, 4, 5...\nАмплітуди спадають як 1/n", "#8e44ad", "sawtooth"),
        ("Трикутний (Triangle Wave)", "Тільки непарні: 1, 3, 5, 7, 9...\nАмплітуди спадають швидко: 1/n²", "#27ae60", "triangle"),
    ]

    col_w = 245
    start_x = 30
    base_y = 380

    for c_idx, (col_title, col_sub, color, wtype) in enumerate(columns):
        cx = start_x + c_idx * (col_w + 15)

        frags.append(rect(cx, 45, col_w, h - 70, fill="#ffffff", stroke="#d0d7de", sw=1, rx=6))

        frags.append(text(cx + col_w / 2, 70, col_title, size=13, color=color, bold=True))
        frags.append(mtext(cx + col_w / 2, 92, col_sub, size=10, color=MUTED, lh=1.25))

        ox = cx + 30
        oy = base_y
        max_bar_h = 180

        frags.append(line(ox - 10, oy, ox + col_w - 45, oy, color="#8c959f", sw=1.2))
        frags.append(arrow(ox, oy + 5, ox, oy - max_bar_h - 25, color="#8c959f", sw=1.2))
        frags.append(text(ox - 6, oy - max_bar_h - 20, "An", size=11, color=INK, anchor="end", italic=True))
        frags.append(text(ox + col_w - 40, oy + 14, "f", size=11, color=INK, anchor="start", italic=True))

        harmonics = range(1, 10)
        env_pts = []
        bar_step = 18

        for n in harmonics:
            bx = ox + n * bar_step
            bar_amp = 0.0

            if wtype == "square":
                if n % 2 == 1:
                    bar_amp = 1.0 / n
            elif wtype == "sawtooth":
                bar_amp = 1.0 / n
            elif wtype == "triangle":
                if n % 2 == 1:
                    bar_amp = 1.0 / (n * n)

            bh = bar_amp * max_bar_h

            if bh > 0.5:
                frags.append(line(bx, oy, bx, oy - bh, color=color, sw=3))
                frags.append(circle(bx, oy - bh, 2.5, fill=color, stroke=color))
                if n <= 5:
                    lbl = "1" if n == 1 else f"1/{n}" if wtype != "triangle" else f"1/{n*n}"
                    frags.append(text(bx, oy - bh - 6, lbl, size=9, color=color, bold=True))

            if n <= 7:
                frags.append(text(bx, oy + 14, f"{n}f0" if n > 1 else "f0", size=9, color=INK if bar_amp > 0 else MUTED))

            if wtype == "sawtooth":
                env_h = (1.0 / n) * max_bar_h
                env_pts.append((bx, oy - env_h))
            elif wtype in ("square", "triangle") and n % 2 == 1:
                env_pts.append((bx, oy - bh))

        if len(env_pts) > 1:
            d_env = "M " + " L ".join(f"{ex:.1f},{ey:.1f}" for ex, ey in env_pts)
            frags.append(f'<path d="{d_env}" fill="none" stroke="{color}" stroke-width="1.2" stroke-dasharray="3,3"/>')

        if wtype == "square":
            summary = "Парні = 0 | Спад: −20 дБ/дек"
        elif wtype == "sawtooth":
            summary = "Парні ≠ 0 | Спад: −20 дБ/дек"
        elif wtype == "triangle":
            summary = "Парні = 0 | Спад: −40 дБ/дек"
        frags.append(rect(cx + 12, oy + 32, col_w - 24, 26, fill="#f8fafc", stroke="#d0d7de", sw=1, rx=4))
        frags.append(text(cx + col_w / 2, oy + 49, summary, size=10, color=color, bold=True))

    render(os.path.join(IMG_DIR, "harmonic-decay-spectrum.svg"), w, h, *frags, title="Спектральний розподіл гармонік за Фур'є та швидкість їх спадання")


if __name__ == "__main__":
    fig_waveform_shapes()
    fig_pulse_timing()
    fig_duty_cycle_pwm()
    fig_harmonic_decay_spectrum()
    print("Усі 4 фігури згенеровано успішно.")
