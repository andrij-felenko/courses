# -*- coding: utf-8 -*-
"""Фігури до теми «Електрика вітряка: генератор, випрямляч, баласт, гальмування».
Запуск:  py -3 figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Повна електрична топологія малої вітроустановки ────────────────────────
def fig_schematic():
    W, H = 880, 440
    f = [text(W / 2, 28, "Електрична схема та силова електроніка малої вітроустановки", size=15, bold=True)]

    # 1. PMSG (ліворуч)
    b_pmsg, _, _ = textbox(110, 150, "PMSG Генератор\n3~ Синхронний\nNdFeB 12-36p\nE = k_e · ω\nf = p · n / 60",
                           size=11.5, pad=12, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b_pmsg)

    # 2. Аварійне гальмо / Короткозамикач
    b_brk, _, _ = textbox(280, 150, "Аварійне гальмо\n3-фазне реле\nкороткого замикання\nабо MOSFET-краубар",
                          size=11, pad=10, fill="#fdecea", stroke=POS, bold=True)
    f.append(b_brk)

    # 3. Трифазний випрямляч
    b_rec, _, _ = textbox(440, 150, "Випрямляч\nМіст B6 або\nактивний MOSFET\n3~ AC → DC\nU_dc ≈ 1.35 · E",
                          size=11, pad=10, fill=FILL, stroke=LINE, bold=True)
    f.append(b_rec)

    # 4. MPPT DC-DC
    b_mppt, _, _ = textbox(600, 150, "MPPT DC-DC\nBuck-Boost / Buck\nСтеження за MPP\nP_opt = k_opt · ω³",
                           size=11, pad=10, fill="#e9f7ef", stroke=FIELD, bold=True)
    f.append(b_mppt)

    # 5. Баласт (Dump load)
    b_dump, _, _ = textbox(770, 150, "Баласт (Dump)\nТрубчасті ТЕНи /\nкерамічні резистори\nШІМ-скидання надлишку",
                           size=10.5, pad=10, fill="#fff8e6", stroke="#d4a72c", bold=True)
    f.append(b_dump)

    # 6. АКБ (справа внизу)
    b_bat, _, _ = textbox(770, 290, "АКБ / Шина живлення\n12 В / 24 В / 48 В\nБуферний накопичувач",
                          size=11, pad=10, fill=FILL, stroke=LINE, bold=True)
    f.append(b_bat)

    # 7. Контролер керування (FSM)
    b_mcu, _, _ = textbox(440, 290, "Мікроконтролер керування (FSM)\nДатчики: U_dc, I_gen, U_bat, I_bat, тахометр f_gen (ω)\nКерування: MPPT ШІМ, баластний ШІМ, аварійне реле",
                          size=11, pad=12, fill="#eaf0fd", stroke=NEG, bold=True)
    f.append(b_mcu)

    # З'єднувальні лінії
    # PMSG -> Brake
    f.append(line(180, 135, 215, 135, color="#8250df", sw=2))
    f.append(line(180, 150, 215, 150, color="#8250df", sw=2))
    f.append(line(180, 165, 215, 165, color="#8250df", sw=2))

    # Brake -> Rectifier
    f.append(line(345, 135, 380, 135, color="#8250df", sw=2))
    f.append(line(345, 150, 380, 150, color="#8250df", sw=2))
    f.append(line(345, 165, 380, 165, color="#8250df", sw=2))
    f.append(text(362, 125, "L1, L2, L3", size=10, color="#8250df", anchor="middle"))

    # Rectifier -> MPPT
    f.append(line(500, 135, 535, 135, color=POS, sw=2))
    f.append(line(500, 165, 535, 165, color=NEG, sw=2))
    f.append(text(517, 125, "DC+", size=10, color=POS, anchor="middle", bold=True))
    f.append(text(517, 180, "DC−", size=10, color=NEG, anchor="middle", bold=True))

    # MPPT -> Dump / Bat
    f.append(line(665, 135, 705, 135, color=POS, sw=2))
    f.append(line(665, 165, 705, 165, color=NEG, sw=2))

    # Відгалуження на АКБ
    f.append(line(685, 135, 685, 275, color=POS, sw=1.8))
    f.append(line(685, 275, 705, 275, color=POS, sw=1.8))
    f.append(line(695, 165, 695, 305, color=NEG, sw=1.8))
    f.append(line(695, 305, 705, 305, color=NEG, sw=1.8))

    # Сигнали керування від MCU
    f.append(line(280, 250, 280, 200, color=POS, sw=1.5, dash="4,3"))
    f.append(text(280, 225, "Стоп", size=10, color=POS, anchor="middle", bold=True))

    f.append(line(600, 250, 600, 200, color=FIELD, sw=1.5, dash="4,3"))
    f.append(text(600, 225, "MPPT ШІМ", size=10, color=FIELD, anchor="middle", bold=True))

    f.append(line(620, 290, 650, 290, color="#d4a72c", sw=1.5, dash="4,3"))
    f.append(line(650, 290, 650, 180, color="#d4a72c", sw=1.5, dash="4,3"))
    f.append(line(650, 180, 705, 180, color="#d4a72c", sw=1.5, dash="4,3"))
    f.append(text(650, 240, "Баласт ШІМ", size=10, color="#b08800", anchor="middle", bold=True))

    # Пояснювальний підвал
    b_note, _, _ = textbox(W / 2, 395,
                           "Трьохрівневий каскад захисту й оптимізації:\n1. MPPT стежить за вітром → 2. Баласт зрізає надлишок напруги → 3. Реле коротить фази при урагані",
                           size=11, fill="#f8fafc", stroke=MUTED)
    f.append(b_note)

    render(os.path.join(IMG, "wind-system-schematic.svg"), W, H, *f)


# ── 2. Характеристики PMSG: ЕРС та напруга DC під навантаженням ──────────────
def fig_pmsg_curves():
    W, H = 840, 420
    f = [text(W / 2, 28, "Характеристики синхронного генератора на постійних магнітах", size=15, bold=True)]

    # Ліва панель: ЕРС та U_dc на холостому ході
    ox1, oy1 = 90, 310
    span1_x, top1 = 280, 80
    f.append(text(ox1 + span1_x / 2, 60, "Холостий хід: ЕРС і випрямлена напруга", size=12, bold=True))
    f.append(line(ox1, oy1, ox1 + span1_x, oy1, color=MUTED, sw=1.4))
    f.append(line(ox1, oy1, ox1, top1, color=MUTED, sw=1.4))
    f.append(text(ox1 + span1_x, oy1 + 22, "оберти n (об/хв) →", size=10.5, color=MUTED, anchor="end"))
    f.append(text(ox1 + 10, top1 - 8, "Напруга U (В)", size=10.5, color=MUTED, anchor="start"))

    # U_dc = 1.35 * E (пряма синя)
    f.append(line(ox1, oy1, ox1 + span1_x, top1 + 15, color=NEG, sw=2.5))
    f.append(text(ox1 + span1_x - 10, top1 + 10, "U_dc = 1.35 · E", size=11, color=NEG, anchor="end", bold=True))

    # E_LL (пряма зелена)
    f.append(line(ox1, oy1, ox1 + span1_x, top1 + 75, color=FIELD, sw=2.2))
    f.append(text(ox1 + span1_x - 10, top1 + 70, "E_LL = k_e · ω", size=11, color=FIELD, anchor="end", bold=True))

    # Поріг U_bat
    v_bat_y = oy1 - (oy1 - top1) * 0.45
    f.append(line(ox1, v_bat_y, ox1 + span1_x, v_bat_y, color=POS, sw=1.5, dash="4,3"))
    f.append(text(ox1 + 15, v_bat_y - 6, "U_bat (початок заряду)", size=10, color=POS, bold=True))

    # Точка початку заряду
    cut_x = ox1 + (span1_x * 0.45) * ((oy1 - top1) / (oy1 - top1 - 15))
    f.append(circle(cut_x, v_bat_y, 4, fill=POS, stroke=BG, sw=1))
    f.append(text(cut_x, oy1 + 15, "n_cut-in", size=10, color=POS, anchor="middle", bold=True))

    # Права панель: Навантажувальне просідання U_dc(I)
    ox2, oy2 = 490, 310
    span2_x, top2 = 280, 80
    f.append(text(ox2 + span2_x / 2, 60, "Навантажувальне просідання U_dc(I)", size=12, bold=True))
    f.append(line(ox2, oy2, ox2 + span2_x, oy2, color=MUTED, sw=1.4))
    f.append(line(ox2, oy2, ox2, top2, color=MUTED, sw=1.4))
    f.append(text(ox2 + span2_x, oy2 + 22, "струм I_dc (А) →", size=10.5, color=MUTED, anchor="end"))
    f.append(text(ox2 + 10, top2 - 8, "Напруга U_dc (В)", size=10.5, color=MUTED, anchor="start"))

    # Крива при високих обертах (n_high)
    high_pts = []
    for i in range(0, 101):
        t = i / 100.0
        xx = ox2 + t * span2_x * 0.95
        yy = (top2 + 20) + (oy2 - (top2 + 20)) * (0.15 * t + 0.85 * t * t)
        high_pts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (" ".join("%.1f,%.1f" % p for p in high_pts), NEG))
    f.append(text(ox2 + span2_x * 0.45, top2 + 45, "Високі оберти", size=10.5, color=NEG, bold=True))

    # Крива при низьких обертах (n_low)
    low_pts = []
    for i in range(0, 101):
        t = i / 100.0
        xx = ox2 + t * span2_x * 0.60
        yy = (top2 + 120) + (oy2 - (top2 + 120)) * (0.2 * t + 0.8 * t * t)
        low_pts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join("%.1f,%.1f" % p for p in low_pts), FIELD))
    f.append(text(ox2 + span2_x * 0.25, top2 + 135, "Низькі оберти", size=10.5, color=FIELD, bold=True))

    # Пояснення опору статора
    b_imp, _, _ = textbox(W / 2, 385,
                          "Внутрішній опір обмоток R_s та індуктивність L_s викликають спад напруги:\nΔU = 2·V_f + I_dc · (2·R_s + 6·f·L_s / π). На холостому ході вітряк розганяється до небезпечної напруги.",
                          size=11, fill="#f8fafc", stroke=MUTED)
    f.append(b_imp)

    render(os.path.join(IMG, "pmsg-rectifier-characteristics.svg"), W, H, *f)


# ── 3. Аеродинамічні криві вітроколеса та кубічний MPPT ──────────────────────
def fig_mppt_inertia():
    W, H = 840, 440
    f = [text(W / 2, 28, "Механічна потужність вітроколеса P(ω) та оптимальна MPPT-траєкторія", size=15, bold=True)]

    ox, oy = 90, 330
    span_x, top = 680, 80

    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 22, "кутова швидкість ротора ω (рад/с) →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox + 10, top - 8, "Потужність P (Вт)", size=11, color=MUTED, anchor="start"))

    # 4 криві вітру (параболічні опуклі дзвони)
    winds = [
        (4, 0.25, 0.12, "4 м/с"),
        (6, 0.45, 0.32, "6 м/с"),
        (8, 0.70, 0.65, "8 м/с"),
        (10, 0.95, 0.95, "10 м/с")
    ]

    opt_pts = []
    for v, x_frac, p_frac, lbl in winds:
        peak_x = ox + span_x * x_frac
        peak_y = oy - (oy - top) * p_frac
        opt_pts.append((peak_x, peak_y))

        # Крива вітру
        pts = []
        for i in range(0, 101):
            t = i / 100.0
            cur_x = ox + span_x * (x_frac * 1.8) * t
            # Параболічний профіль від 0 до 0
            val = 4 * p_frac * t * (1.0 - t)
            cur_y = oy - (oy - top) * max(0.0, val)
            pts.append((cur_x, cur_y))
        f.append('<polyline points="%s" fill="none" stroke="#90cdf4" stroke-width="1.8"/>'
                 % (" ".join("%.1f,%.1f" % p for p in pts)))
        f.append(text(ox + span_x * (x_frac * 1.75), oy - 8, lbl, size=10, color=MUTED, anchor="middle"))

    # Оптимальна кубічна крива (зелена товста)
    opt_curve = []
    for i in range(0, 101):
        t = i / 100.0
        cur_x = ox + span_x * t
        cur_y = oy - (oy - top) * (t ** 3)
        opt_curve.append((cur_x, cur_y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in opt_curve), FIELD))
    f.append(text(ox + span_x * 0.85, top + 35, "P_opt = k_opt · ω³", size=13, color=FIELD, bold=True))

    # Точки MPP
    for i, (px, py) in enumerate(opt_pts, 1):
        f.append(circle(px, py, 4.5, fill=FIELD, stroke=BG, sw=1.5))
        f.append(text(px - 10, py - 8, f"MPP {i}", size=10, color=FIELD, anchor="end", bold=True))

    # Стрілка зриву ротора через інерцію
    p_stall_start = opt_pts[2]
    f.append(line(p_stall_start[0], p_stall_start[1], p_stall_start[0] - 120, p_stall_start[1] + 60,
                  color=POS, sw=2, dash="4,3"))
    f.append(text(p_stall_start[0] - 60, p_stall_start[1] + 80,
                  "Зрив ротора (Rotor Stall):\nнадто швидкий відбір потужності гальмує інерцію J",
                  size=10, color=POS, anchor="middle", bold=True))

    b_note, _, _ = textbox(W / 2, 405,
                           "Через механічну інерцію вітроколеса J·dω/dt алгоритм MPPT повинен витримувати паузи адаптації,\nінакше динамічний відбір енергії гальмує ротор у зону низького ККД.",
                           size=11, fill="#e9f7ef", stroke=FIELD)
    f.append(b_note)

    render(os.path.join(IMG, "wind-mppt-inertia-curve.svg"), W, H, *f)


# ── 4. Гальмівний момент при короткому замиканні статора PMSG ─────────────────
def fig_braking_torque():
    W, H = 840, 420
    f = [text(W / 2, 28, "Електромагнітний гальмівний момент при короткому замиканні генератора", size=15, bold=True)]

    ox, oy = 90, 320
    span_x, top = 680, 80

    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 22, "електрична швидкість ω_e = p · ω (рад/с) →", size=11, color=MUTED, anchor="end"))
    f.append(text(ox + 10, top - 8, "Гальмівний момент T_brk (Н·м)", size=11, color=MUTED, anchor="start"))

    # Крива гальмівного моменту: T = 3 * p * k_e^2 * omega_e * R_s / (R_s^2 + (omega_e * L_s)^2)
    # Peak is at omega_e = R_s / L_s
    pts_brk = []
    peak_idx = 20
    for i in range(0, 201):
        t = i / 20.0  # normalized omega_e / (R_s / L_s)
        # T_norm = 2 * t / (1 + t^2) -> peak at t=1, val=1
        val = 2.0 * t / (1.0 + t * t) if t > 0 else 0.0
        xx = ox + (i / 200.0) * span_x
        yy = oy - (oy - top) * 0.85 * val
        pts_brk.append((xx, yy))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts_brk), POS))

    # Пік моменту
    peak_x = ox + (20.0 / 200.0) * span_x
    peak_y = oy - (oy - top) * 0.85
    f.append(circle(peak_x, peak_y, 5, fill=POS, stroke=BG, sw=1.5))
    f.append(text(peak_x + 10, peak_y - 10, "Пік T_max (при ω_e = R_s / L_s)", size=11, color=POS, bold=True))

    # Крива аеродинамічного моменту при ураганному вітрі
    pts_aero = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ox + t * span_x
        yy = (oy - (oy - top) * 0.35) - (oy - top) * 0.25 * t
        pts_aero.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in pts_aero), NEG))
    f.append(text(ox + span_x - 10, top + 90, "Момент вітру T_aero (буря)", size=11, color=NEG, anchor="end", bold=True))

    # Зона 1 (Активна)
    f.append(text(ox + 45, oy - 40, "Активна зона:\nT ∝ ω · R_s\n(надійний стоп)", size=10, color=FIELD, bold=True))

    # Зона 2 (Індуктивна пастка)
    f.append(text(ox + span_x * 0.65, oy - 80,
                  "Індуктивна пастка:\nT ∝ R_s / (ω · L_s²) → спадає до нуля!\nСтрум відстає на 90°, фази плавляться, а ротор не зупиняється",
                  size=10.5, color=POS, bold=True))

    b_note, _, _ = textbox(W / 2, 385,
                           "Закорочувати генератор треба ДО виходу на ураганні оберти. Якщо вітряк уже пішов у рознос,\nіндуктивний опір L_s не дасть розвинути гальмівний момент — генератор просто згорить.",
                           size=11, fill="#fdecea", stroke=POS)
    f.append(b_note)

    render(os.path.join(IMG, "braking-torque-speed.svg"), W, H, *f)


def main():
    fig_schematic()
    fig_pmsg_curves()
    fig_mppt_inertia()
    fig_braking_torque()
    print("Всі 4 фігури успішно згенеровано у img/")


if __name__ == "__main__":
    main()
