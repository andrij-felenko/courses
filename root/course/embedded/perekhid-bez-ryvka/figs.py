# -*- coding: utf-8 -*-
"""Фігури до теми «Перехід без ривка: стан регулятора при зміні режиму».
Запуск: python figs.py  → генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os

# Додаємо шлях до спільного svgkit у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT = "#c0392b"
COLD = "#2457d6"
GREEN = "#27ae60"
AMBER = "#d35400"
PURPLE = "#8e44ad"


# ── 1. Стрибок керування (Control Bump / Glitch) ──────────────────────────────
def fig_control_bump():
    W, H = 880, 480
    f = [text(W / 2, 28, "Стрибок сигналу керування при наївному перемиканні режиму", size=16, bold=True)]

    gw = 360
    gh = 160
    gy1 = 80

    # ── Панель А: Наївне перемикання (Стрибок і просідання) ──
    x0_a = 60
    f.append(rect(x0_a, gy1, gw, gh + 140, fill="#fffaf9", stroke=HOT, sw=1.5, rx=8))
    f.append(text(x0_a + gw / 2, gy1 + 24, "Наївний старт: I = 0, стрибок на виході", size=13, bold=True, color=HOT))

    ts_x_a = x0_a + 170
    f.append(line(ts_x_a, gy1 + 40, ts_x_a, gy1 + gh + 120, color=HOT, sw=1.5, dash="4 4"))
    f.append(text(ts_x_a, gy1 + gh + 134, "t_перемикання", size=11, color=HOT, bold=True))

    f.append(line(x0_a + 30, gy1 + 100, x0_a + gw - 20, gy1 + 100, color=MUTED, sw=1.0))
    f.append(text(x0_a + 25, gy1 + 60, "Кермо u(t)", size=11, bold=True, color=INK, anchor="start"))
    f.append(line(x0_a + 40, gy1 + 65, ts_x_a, gy1 + 65, color=INK, sw=2.5))
    f.append(text(x0_a + 95, gy1 + 55, "Трим +4.2°", size=10.5, color=INK))
    f.append(line(ts_x_a, gy1 + 65, ts_x_a, gy1 + 100, color=HOT, sw=2.5, dash="3 3"))
    f.append(circle(ts_x_a, gy1 + 65, 3.5, fill=INK, stroke=INK))
    f.append(circle(ts_x_a, gy1 + 100, 3.5, fill=HOT, stroke=HOT))
    f.append('<path d="M %.1f %.1f Q %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (ts_x_a, gy1 + 100, ts_x_a + 80, gy1 + 95, x0_a + gw - 20, gy1 + 68, HOT))

    f.append(text(ts_x_a + 50, gy1 + 82, "Δu = −4.2° (удар)", size=10, color=HOT, bold=True))

    f.append(line(x0_a + 30, gy1 + 220, x0_a + gw - 20, gy1 + 220, color=MUTED, sw=1.0))
    f.append(text(x0_a + 25, gy1 + 175, "Тангаж / висота", size=11, bold=True, color=INK, anchor="start"))
    f.append(line(x0_a + 40, gy1 + 195, ts_x_a, gy1 + 195, color=INK, sw=2.5))
    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (ts_x_a, gy1 + 195, ts_x_a + 40, gy1 + 265, ts_x_a + 110, gy1 + 260, x0_a + gw - 20, gy1 + 205, HOT))
    f.append(text(ts_x_a + 75, gy1 + 278, "Просідання h(t) і перевантаження", size=10, color=HOT))

    # ── Панель Б: Безривковий перехід (Bumpless Transfer) ──
    x0_b = 460
    f.append(rect(x0_b, gy1, gw, gh + 140, fill="#f9fcf9", stroke=GREEN, sw=1.5, rx=8))
    f.append(text(x0_b + gw / 2, gy1 + 24, "Безривковий перехід: I_new = u_prev", size=13, bold=True, color=GREEN))

    ts_x_b = x0_b + 170
    f.append(line(ts_x_b, gy1 + 40, ts_x_b, gy1 + gh + 120, color=GREEN, sw=1.5, dash="4 4"))
    f.append(text(ts_x_b, gy1 + gh + 134, "t_перемикання", size=11, color=GREEN, bold=True))

    f.append(line(x0_b + 30, gy1 + 100, x0_b + gw - 20, gy1 + 100, color=MUTED, sw=1.0))
    f.append(text(x0_b + 25, gy1 + 60, "Кермо u(t)", size=11, bold=True, color=INK, anchor="start"))
    f.append(line(x0_b + 40, gy1 + 65, ts_x_b, gy1 + 65, color=INK, sw=2.5))
    f.append(circle(ts_x_b, gy1 + 65, 3.5, fill=GREEN, stroke=GREEN))
    f.append('<path d="M %.1f %.1f Q %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (ts_x_b, gy1 + 65, ts_x_b + 70, gy1 + 65, x0_b + gw - 20, gy1 + 65, GREEN))
    f.append(text(ts_x_b + 65, gy1 + 55, "Δu = 0 (неперервність)", size=10.5, color=GREEN, bold=True))

    f.append(line(x0_b + 30, gy1 + 220, x0_b + gw - 20, gy1 + 220, color=MUTED, sw=1.0))
    f.append(text(x0_b + 25, gy1 + 175, "Тангаж / висота", size=11, bold=True, color=INK, anchor="start"))
    f.append(line(x0_b + 40, gy1 + 195, ts_x_b, gy1 + 195, color=INK, sw=2.5))
    f.append(line(ts_x_b, gy1 + 195, x0_b + gw - 20, gy1 + 195, color=GREEN, sw=2.5))
    f.append(text(x0_b + gw / 2, gy1 + 210, "Стабільний горизонт без клювання", size=10.5, color=GREEN))

    f.append(text(W / 2, H - 25, "Перемикання без завантаження стану розриває механічну рівновагу приводу", size=12, color=MUTED))

    return render(os.path.join(IMG, "control-bump-glitch.svg"), W, H, *f)


# ── 2. Удар інтегратора: фізика втрати триму ─────────────────────────────────
def fig_integrator_shock():
    W, H = 880, 420
    f = [text(W / 2, 28, "Удар інтегратора (Integrator Shock): чому I=0 обвалює тягу", size=16, bold=True)]

    bx, by, bw, bh = 60, 65, 760, 115
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    f.append(text(bx + bw / 2, by + 24, "Рівновага сил у польоті: сталий трим (Trim) утримується виключно інтегратором", size=12.5, bold=True, color=INK))

    f.append(text(bx + 160, by + 58, "Ручний режим (Manual):", size=11.5, bold=True, color=INK))
    f.append(text(bx + 160, by + 80, "u_manual = 58% газу (утримання висоти)", size=11, color=MUTED))

    f.append(text(bx + bw / 2, by + 68, "➔ перемикання ➔", size=14, bold=True, color=LINE))

    f.append(text(bx + 580, by + 58, "Автоматичний режим (Alt-Hold):", size=11.5, bold=True, color=INK))
    f.append(text(bx + 580, by + 80, "u_pid = Kp·e + Ki·∫e dt   [якщо I = 0, e = 0 → u = 0%]", size=11, color=HOT))

    gy = 205
    gw = 760
    gh = 175
    f.append(rect(bx, gy, gw, gh, fill="#ffffff", stroke=LINE, sw=1.4, rx=8))

    f.append(line(bx + 40, gy + gh - 35, bx + gw - 40, gy + gh - 35, color=MUTED, sw=1.0))
    f.append(text(bx + gw - 35, gy + gh - 35, "t", size=11, color=MUTED))

    ts_x = bx + 220
    f.append(line(ts_x, gy + 15, ts_x, gy + gh - 15, color=AMBER, sw=1.5, dash="4 4"))
    f.append(text(ts_x, gy + 28, "t_перемикання", size=10.5, color=AMBER, bold=True))

    f.append(line(bx + 50, gy + 65, ts_x, gy + 65, color=INK, sw=2.5))
    f.append(text(bx + 130, gy + 55, "Тяга 58% (Hold)", size=11, color=INK, bold=True))

    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="3 3"/>'
             % (ts_x, gy + gh - 35, ts_x + 60, gy + 60, ts_x + 180, gy + 75, bx + gw - 50, gy + gh - 35, COLD))
    f.append(text(ts_x + 95, gy + 85, "P-складова (Kp·e)", size=10, color=COLD))

    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (ts_x, gy + gh - 35, ts_x + 140, gy + gh - 35, ts_x + 280, gy + 80, bx + gw - 50, gy + 65, GREEN))
    f.append(text(ts_x + 280, gy + 105, "I-складова (накопичує трим заново)", size=10.5, color=GREEN, bold=True))

    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (ts_x, gy + gh - 35, ts_x + 40, gy + 80, ts_x + 150, gy + 45, bx + gw - 50, gy + 65, HOT))
    f.append(text(ts_x + 145, gy + 40, "Сумарне u(t): провал до 0% і переліт!", size=11, color=HOT, bold=True))

    f.append(rect(ts_x + 10, gy + 120, 140, 32, fill="#fdecea", stroke=HOT, sw=1.0, rx=4))
    f.append(text(ts_x + 80, gy + 140, "Яма втрати тяги", size=10, color=HOT, bold=True))

    return render(os.path.join(IMG, "integrator-shock.svg"), W, H, *f)


# ── 3. Алгоритм безперервного переходу (Dataflow) ────────────────────────────
def fig_bumpless_algorithm():
    W, H = 880, 460
    f = [text(W / 2, 28, "Алгоритм безперервного переходу (Bumpless Handover)", size=16, bold=True)]

    b1_x, b1_y, b1_w, b1_h = 50, 70, 210, 85
    f.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f0f4f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(b1_x + b1_w / 2, b1_y + 26, "Попередній режим A", size=12, bold=True, color=INK))
    f.append(text(b1_x + b1_w / 2, b1_y + 48, "Останній керувальний", size=10.5, color=MUTED))
    f.append(text(b1_x + b1_w / 2, b1_y + 66, "сигнал: u_prev", size=11, bold=True, color=COLD))

    cb_x, cb_y, cb_w, cb_h = 330, 70, 490, 240
    f.append(rect(cb_x, cb_y, cb_w, cb_h, fill="#ffffff", stroke=GREEN, sw=1.8, rx=8))
    f.append(text(cb_x + cb_w / 2, cb_y + 26, "Ініціалізація стану нового регулятора B (в момент перемикання)", size=13, bold=True, color=GREEN))

    f.append(rect(cb_x + 20, cb_y + 45, cb_w - 40, 50, fill="#f9fbf9", stroke=GREEN, sw=1.0, rx=4))
    f.append(text(cb_x + 35, cb_y + 66, "Крок 1. Відстеження цілі (Setpoint Tracking):", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(cb_x + 35, cb_y + 84, "Setpoint_new = Measurement_current  ➔  e = 0  ➔  P_new = 0", size=11, color=GREEN, anchor="start"))

    f.append(rect(cb_x + 20, cb_y + 105, cb_w - 40, 48, fill="#f9fbf9", stroke=GREEN, sw=1.0, rx=4))
    f.append(text(cb_x + 35, cb_y + 125, "Крок 2. Скидання пам'яті похідної (D-kick prevent):", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(cb_x + 35, cb_y + 142, "meas_prev = Measurement_current  ➔  D_new = 0", size=11, color=GREEN, anchor="start"))

    f.append(rect(cb_x + 20, cb_y + 163, cb_w - 40, 62, fill="#eef8f1", stroke=GREEN, sw=1.4, rx=4))
    f.append(text(cb_x + 35, cb_y + 184, "Крок 3. Передзавантаження інтегратора (Pre-loading):", size=11.5, bold=True, color=GREEN, anchor="start"))
    f.append(text(cb_x + 35, cb_y + 208, "I_new = clamp(u_prev − P_new − D_new − FF_new, I_min, I_max)", size=12, bold=True, color=INK, anchor="start"))

    f.append(arrow(b1_x + b1_w, b1_y + 42, cb_x, cb_y + 195, color=COLD, sw=2.0))
    f.append(text(b1_x + b1_w + 35, b1_y + 110, "u_prev", size=11, bold=True, color=COLD))

    out_x, out_y, out_w, out_h = 330, 340, 490, 85
    f.append(rect(out_x, out_y, out_w, out_h, fill="#f3f9f4", stroke=GREEN, sw=1.5, rx=6))
    f.append(text(out_x + out_w / 2, out_y + 24, "Вихідний сигнал регулятора B на першому кроці t = 0+", size=12, bold=True, color=INK))
    f.append(text(out_x + out_w / 2, out_y + 50, "u_B(0+) = P_new + I_new + D_new + FF = 0 + (u_prev − FF) + 0 + FF = u_prev", size=12.5, bold=True, color=GREEN))
    f.append(text(out_x + out_w / 2, out_y + 70, "Механічний привід не відчуває перемикання (нульовий ривок: Δu = 0)", size=11, color=MUTED))

    f.append(arrow(cb_x + cb_w / 2, cb_y + cb_h, out_x + out_w / 2, out_y, color=GREEN, sw=2.0))

    return render(os.path.join(IMG, "bumpless-algorithm.svg"), W, H, *f)


# ── 4. Згладжування траєкторій (Ramping & Slew Rate Limiters) ─────────────────
def fig_trajectory_ramping():
    W, H = 880, 440
    f = [text(W / 2, 28, "Перехід до нового завдання: стрибок проти згладжування (Ramping)", size=16, bold=True)]

    pw = 360
    ph = 330
    py = 65

    # ── Панель А: Миттєвий стрибок завдання ──
    pa_x = 60
    f.append(rect(pa_x, py, pw, ph, fill="#fffaf9", stroke=HOT, sw=1.4, rx=8))
    f.append(text(pa_x + pw / 2, py + 24, "Без ремпінгу: стрибок завдання (Step)", size=13, bold=True, color=HOT))

    f.append(line(pa_x + 30, py + ph - 45, pa_x + pw - 20, py + ph - 45, color=MUTED, sw=1.0))
    f.append(text(pa_x + pw - 20, py + ph - 45, "t", size=11, color=MUTED))

    ts_x_a = pa_x + 100
    f.append(line(pa_x + 35, py + ph - 65, ts_x_a, py + ph - 65, color=MUTED, sw=2.0, dash="4 4"))
    f.append(line(ts_x_a, py + ph - 65, ts_x_a, py + 75, color=MUTED, sw=2.0, dash="4 4"))
    f.append(line(ts_x_a, py + 75, pa_x + pw - 25, py + 75, color=MUTED, sw=2.0, dash="4 4"))
    f.append(text(pa_x + pw - 75, py + 65, "Ціль (Target)", size=10.5, color=MUTED))

    f.append(line(pa_x + 35, py + ph - 65, ts_x_a, py + ph - 65, color=INK, sw=2.2))
    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="2.5"/>'
             % (ts_x_a, py + ph - 65, ts_x_a + 30, py + 45, ts_x_a + 80, py + 45, ts_x_a + 130, py + 75,
                ts_x_a + 170, py + 95, ts_x_a + 210, py + 75, pa_x + pw - 25, py + 75, HOT))
    f.append(text(ts_x_a + 55, py + 42, "Переліт і перевантаження", size=10, color=HOT, bold=True))

    # ── Панель Б: Плавний лінійний/S-подібний ремпінг ──
    pb_x = 460
    f.append(rect(pb_x, py, pw, ph, fill="#f9fcf9", stroke=GREEN, sw=1.4, rx=8))
    f.append(text(pb_x + pw / 2, py + 24, "Із ремпінгом: Slew Rate / S-Curve Trajectory", size=13, bold=True, color=GREEN))

    f.append(line(pb_x + 30, py + ph - 45, pb_x + pw - 20, py + ph - 45, color=MUTED, sw=1.0))
    f.append(text(pb_x + pw - 20, py + ph - 45, "t", size=11, color=MUTED))

    ts_x_b = pb_x + 80
    f.append(line(pb_x + 35, py + ph - 65, ts_x_b, py + ph - 65, color=GREEN, sw=2.0, dash="4 4"))
    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4 4"/>'
             % (ts_x_b, py + ph - 65, ts_x_b + 50, py + ph - 60, ts_x_b + 110, py + 80, ts_x_b + 160, py + 75, GREEN))
    f.append(line(ts_x_b + 160, py + 75, pb_x + pw - 25, py + 75, color=GREEN, sw=2.0, dash="4 4"))
    f.append(text(pb_x + pw - 95, py + 65, "Setpoint(t) згладжене", size=10.5, color=GREEN))

    f.append(line(pb_x + 35, py + ph - 65, ts_x_b, py + ph - 65, color=INK, sw=2.2))
    f.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f L %.1f %.1f" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (ts_x_b, py + ph - 65, ts_x_b + 60, py + ph - 55, ts_x_b + 120, py + 85, ts_x_b + 175, py + 75, pb_x + pw - 25, py + 75, GREEN))
    f.append(text(ts_x_b + 80, py + 140, "Плавний вихід без коливань", size=10.5, color=GREEN, bold=True))

    f.append(rect(pb_x + 20, py + ph - 105, pw - 40, 48, fill="#ffffff", stroke=LINE, sw=1.0, rx=4))
    f.append(text(pb_x + pw / 2, py + ph - 88, "d(Setpoint)/dt ≤ Rate_max", size=11, bold=True, color=INK))
    f.append(text(pb_x + pw / 2, py + ph - 68, "Обмежувач швидкості наростання (Slew Limiter)", size=10, color=MUTED))

    f.append(text(W / 2, H - 15, "Ремпінг розтягує перехід у часі, усуваючи удар по приводу та механіці", size=12, color=MUTED))

    return render(os.path.join(IMG, "trajectory-ramping.svg"), W, H, *f)


if __name__ == "__main__":
    fig_control_bump()
    fig_integrator_shock()
    fig_bumpless_algorithm()
    fig_trajectory_ramping()
    print("Всі фігури згенеровано успішно.")
