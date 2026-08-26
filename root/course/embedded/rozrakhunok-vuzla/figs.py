# -*- coding: utf-8 -*-
"""Фігури до теми «Розрахунок вузла: панель, банка, N діб без сонця».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Сталі кольори системи
C_SOLAR = "#d97706" # сонячна генерація — бурштиновий
C_BATT  = "#2563eb" # накопичувач LiFePO4 — синій
C_CTRL  = "#7c3aed" # контролер заряду MPPT — фіолетовий
C_LOAD  = "#059669" # навантаження вузла — смарагдовий
C_LOSS  = "#dc2626" # втрати/делейтинг — червоний
C_WARN  = "#d97706" # попередження/DoD — бурштиновий


# ── 1. Архітектура та енергетичний потік автономного вузла ────────────────────
def fig_system_energy_flow():
    """Енергетичний ланцюг: фотопанель -> MPPT -> батарея -> DC-DC -> навантаження.
    Показано коефіцієнти ККД та місця витоків енергії на кожному етапі."""
    W, H = 840, 430
    f = [text(W / 2, 28, "Енергетичний потік автономного сонячного комплексу", size=16, bold=True)]

    # 4 головні блоки в горизонтальний ланцюг
    cards = [
        ("Фотопанель (PV)", "P_pv = G · A · η_pv\nВтрати: бруд, кут,\nтемпература", C_SOLAR, 40),
        ("Контролер MPPT", "ККД η_mppt ≈ 95–98%\nСтеження за MPP\nI_batt = P_mpp/V_batt", C_CTRL, 240),
        ("Батарея LiFePO4", "Ємність C_batt, DoD 80%\nККД η_batt ≈ 95%\nСаморозряд ~1%/міс", C_BATT, 440),
        ("Живлення вузла", "DC-DC (η_conv ≈ 90%)\nМікроконтролер + радіо\nE_day = ∫ V·I(t) dt", C_LOAD, 640),
    ]

    bw, bh = 160, 150
    cy = 135

    for title, desc, col, x in cards:
        f.append(rect(x, cy - bh / 2, bw, bh, fill="#ffffff", stroke=col, sw=2, rx=8))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="32" rx="6" fill="%s" fill-opacity="0.15"/>'
                 % (x, cy - bh / 2, bw, col))
        f.append(text(x + bw / 2, cy - bh / 2 + 21, title, size=12, color=col, bold=True))
        f.append(mtext(x + bw / 2, cy - bh / 2 + 58, desc, size=10, color=INK, lh=1.35))

    # Стрілки передачі енергії між блоками
    f.append(arrow(40 + bw, cy, 240, cy, color=C_SOLAR, sw=2.4))
    f.append(text(200, cy - 10, "P_pv", size=10, color=C_SOLAR, bold=True))

    f.append(arrow(240 + bw, cy, 440, cy, color=C_CTRL, sw=2.4))
    f.append(text(400, cy - 10, "P_charge", size=10, color=C_CTRL, bold=True))

    f.append(arrow(440 + bw, cy, 640, cy, color=C_BATT, sw=2.4))
    f.append(text(600, cy - 10, "P_bus", size=10, color=C_BATT, bold=True))

    # Блок нижніх приміток щодо делейтингу та втрат
    loss_y = 260
    f.append(rect(40, loss_y, W - 80, 130, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(W / 2, loss_y + 24, "Коефіцієнти балансу потужності та делейтингу системи", size=12, bold=True, color=INK))

    subcards = [
        ("Втрати поля (η_field)", "Бруд/пил: 0.92–0.95\nКут/сніг: 0.85–0.95\nДроти: 0.98–0.99", C_SOLAR, 60),
        ("Контролер (η_ctrl)", "MPPT: 0.95–0.98\nPWM (зима): 0.65–0.70\nВласне спож.: <2 мА", C_CTRL, 250),
        ("Акумулятор (η_batt)", "ККД заряду: 0.95\nDoD ліміт: 0.80 (LFP)\nХолод (-20°C): 0.70", C_BATT, 440),
        ("Споживач (η_load)", "DC-DC бак: 0.88–0.92\nСон: 15–50 мкА\nПередача: 150–300 мА", C_LOAD, 630),
    ]

    for stitle, sdesc, scol, sx in subcards:
        f.append(rect(sx, loss_y + 38, 150, 78, fill="#ffffff", stroke=scol, sw=1.2, rx=6))
        f.append(text(sx + 75, loss_y + 54, stitle, size=10.5, color=scol, bold=True))
        f.append(mtext(sx + 75, loss_y + 72, sdesc, size=9, color=MUTED, lh=1.3))

    render(os.path.join(IMG, "system-energy-flow.svg"), W, H, *f)


# ── 2. Динаміка заряду батареї під час N діб автономності ────────────────────
def fig_battery_autonomy_discharge():
    """Графік SoC (%) у часі: штатний режим -> 5 діб без сонця -> відновлення заряду."""
    W, H = 840, 430
    f = [text(W / 2, 28, "Динаміка заряду акумулятора під час N діб повної хмарності", size=16, bold=True)]

    ox, oy = 80, 340
    pw, ph = 710, 240

    # Осі координат
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    f.append(text(ox + pw / 2, oy + 42, "Час у добах (день / ніч) →", size=11, color=MUTED))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">Рівень заряду (SoC, %%)</text>'
             % (ox - 44, oy - ph / 2, FONT, MUTED, ox - 44, oy - ph / 2))

    # Шкала SoC по Y
    for soc in (0, 20, 50, 80, 100):
        yy = oy - (soc / 100.0) * ph
        f.append(line(ox - 5, yy, ox, yy, color=INK, sw=1))
        f.append(text(ox - 10, yy + 4, "%d%%" % soc, size=10, color=MUTED, anchor="end"))
        if soc in (20, 100):
            col_dash = C_LOSS if soc == 20 else FIELD
            f.append(line(ox, yy, ox + pw, yy, color=col_dash, sw=1, dash="4 4"))

    # Фази на графіку по X
    total_days = 10.0
    def dx(day): return ox + (day / total_days) * pw
    def dy(soc): return oy - (soc / 100.0) * ph

    # Стовпчики фаз зверху
    f.append(line(dx(2), oy - ph, dx(2), oy, color=MUTED, sw=1, dash="2 2"))
    f.append(line(dx(7), oy - ph, dx(7), oy, color=MUTED, sw=1, dash="2 2"))

    f.append(text((dx(0) + dx(2)) / 2, oy - ph - 10, "Штатний цикл", size=10.5, color=FIELD, bold=True))
    f.append(text((dx(2) + dx(7)) / 2, oy - ph - 10, "N_autonomy = 5 діб хмарності", size=10.5, color=C_LOSS, bold=True))
    f.append(text((dx(7) + dx(10)) / 2, oy - ph - 10, "N_recovery = 3 доби сонця", size=10.5, color=C_SOLAR, bold=True))

    # Складна крива SoC
    pts = [
        (0.0, 100), (0.5, 92), (1.0, 100), (1.5, 92), (2.0, 100),
        (2.5, 87), (3.0, 84),
        (3.5, 71), (4.0, 68),
        (4.5, 55), (5.0, 52),
        (5.5, 39), (6.0, 36),
        (6.5, 23), (7.0, 20),
        (7.5, 52), (8.0, 46),
        (8.5, 78), (9.0, 72),
        (9.5, 98), (10.0, 93)
    ]

    p_str = " ".join("%.1f,%.1f" % (dx(d), dy(s)) for d, s in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (p_str, C_BATT))

    # Точки перегину
    for d, s in [(2.0, 100), (7.0, 20), (10.0, 93)]:
        col_pt = FIELD if s > 80 else (C_LOSS if s <= 20 else C_SOLAR)
        f.append(circle(dx(d), dy(s), 4.5, fill=col_pt, stroke="#ffffff", sw=1.5))

    f.append(text(dx(2.0) - 16, dy(100) - 8, "100%", size=10, color=FIELD, bold=True, anchor="end"))
    f.append(text(dx(7.0) + 12, dy(20) + 18, "20% (DoD max 80%)", size=10, color=C_LOSS, bold=True, anchor="start"))
    f.append(text(dx(10.0) - 14, dy(93) - 8, "~100%", size=10, color=FIELD, bold=True, anchor="end"))

    # Пояснювальна картка безпеки вгорі праворуч (де порожній простір)
    f.append(fitbox(ox + pw - 290, 50, 270, 42,
                    "Нижня межа: залишок 20% SoC\n(DoD = 80% для збереження ресурсу LFP)",
                    size=9.5, fill="#fef2f2", stroke=C_LOSS, sw=1.1))

    # Підписи діб по осі X
    for day in range(0, 11):
        f.append(line(dx(day), oy, dx(day), oy + 5, color=INK, sw=1))
        f.append(text(dx(day), oy + 20, "%d д" % day, size=9.5, color=MUTED))

    render(os.path.join(IMG, "battery-autonomy-discharge.svg"), W, H, *f)


# ── 3. Порівняння ВАХ та потужності: MPPT проти PWM ─────────────────────────
def fig_mppt_vs_pwm():
    """ВАХ фотопанелі при -10°C (зима) та +45°C (літо).
    Показано робочі точки MPPT та PWM, що наочно пояснює різницю ККД у 35% взимку."""
    W, H = 840, 420
    f = [text(W / 2, 28, "Порівняння MPPT і PWM на вольт-амперній характеристиці панелі", size=16, bold=True)]

    ox, oy = 80, 330
    pw, ph = 460, 250

    # Осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    f.append(text(ox + pw / 2, oy + 40, "Напруга панелі V_pv (В) →", size=11, color=MUTED))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">Струм I_pv (А)</text>'
             % (ox - 46, oy - ph / 2, FONT, MUTED, ox - 46, oy - ph / 2))

    # Шкала напруг (0..24 В), струму (0..1.5 А)
    vmax, imax = 24.0, 1.4
    def vx(v): return ox + (v / vmax) * pw
    def iy(i): return oy - (i / imax) * ph

    for v in range(0, 25, 4):
        f.append(line(vx(v), oy, vx(v), oy + 5, color=INK, sw=1))
        f.append(text(vx(v), oy + 20, "%d" % v, size=9.5, color=MUTED))

    for cur in (0.0, 0.5, 1.0):
        f.append(line(ox - 5, iy(cur), ox, iy(cur), color=INK, sw=1))
        f.append(text(ox - 10, iy(cur) + 4, "%.1f" % cur, size=9.5, color=MUTED, anchor="end"))

    # Лінія напруги акумулятора 12.8–13.6 В (V_batt)
    v_batt = 13.2
    f.append(line(vx(v_batt), oy, vx(v_batt), oy - ph, color=C_BATT, sw=1.5, dash="4 4"))
    f.append(text(vx(v_batt), oy - ph - 6, "V_batt = 13.2 В", size=10, color=C_BATT, bold=True))

    # ВАХ при -10°C (холодна панель: Voc ~ 23.5 В, Vmp ~ 19.5 В, Imp ~ 1.00 А)
    pts_cold = [(0, 1.08), (12, 1.07), (16, 1.05), (19.5, 1.00), (21.5, 0.80), (23.5, 0.0)]
    pth_cold = " ".join("%.1f,%.1f" % (vx(v), iy(i)) for v, i in pts_cold)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>'
             % (pth_cold, NEG))

    # Робочі точки взимку (-10°C)
    # MPPT: V=19.5, I=1.00 -> P = 19.5 Вт
    f.append(circle(vx(19.5), iy(1.00), 5.5, fill=C_CTRL, stroke="#ffffff", sw=1.5))
    f.append(text(vx(19.5) + 10, iy(1.00) - 10, "MPPT: 19.5 Вт", size=10.5, color=C_CTRL, bold=True, anchor="start"))
    f.append(text(vx(19.5) + 10, iy(1.00) + 6, "(19.5 В × 1.0 А)", size=9, color=MUTED, anchor="start"))

    # PWM: прибиває до V_batt = 13.2 В -> I=1.06 А -> P = 13.2 * 1.06 = 14.0 Вт
    f.append(circle(vx(13.2), iy(1.06), 5.5, fill=C_LOSS, stroke="#ffffff", sw=1.5))
    f.append(text(vx(13.2) - 10, iy(1.06) - 10, "PWM: 14.0 Вт", size=10.5, color=C_LOSS, bold=True, anchor="end"))
    f.append(text(vx(13.2) - 10, iy(1.06) + 6, "(13.2 В × 1.06 А)", size=9, color=MUTED, anchor="end"))

    # Втрачена енергія PWM (прямокутник різниці)
    f.append(line(vx(13.2), iy(1.06), vx(19.5), iy(1.00), color=C_LOSS, sw=1.5, dash="3 3"))

    # ВАХ при +45°C (гаряча панель: Voc ~ 19.5 В, Vmp ~ 15.5 В, Imp ~ 1.05 А)
    pts_hot = [(0, 1.10), (10, 1.09), (13.5, 1.06), (15.5, 0.98), (17.5, 0.70), (19.5, 0.0)]
    pth_hot = " ".join("%.1f,%.1f" % (vx(v), iy(i)) for v, i in pts_hot)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round" stroke-dasharray="6 4"/>'
             % (pth_hot, POS))

    # Легенда та порівняльна таблиця праворуч
    rx = 570
    f.append(rect(rx, 70, 240, 270, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(rx + 120, 94, "Порівняння ККД у полі", size=12, bold=True, color=INK))

    f.append(line(rx + 15, 122, rx + 45, 122, color=NEG, sw=2.6))
    f.append(text(rx + 55, 126, "Зима (-10 °C):", size=10, color=NEG, bold=True, anchor="start"))
    f.append(text(rx + 20, 144, "• MPPT збирає: 19.5 Вт (100%)", size=9.5, color=C_CTRL, anchor="start"))
    f.append(text(rx + 20, 162, "• PWM збирає: 14.0 Вт (71.8%)", size=9.5, color=C_LOSS, anchor="start"))
    f.append(text(rx + 20, 180, "• Втрати PWM: 28.2% енергії!", size=9.5, color=C_LOSS, bold=True, anchor="start"))

    f.append(line(rx + 15, 206, rx + 45, 206, color=POS, sw=2.2, dash="5 3"))
    f.append(text(rx + 55, 210, "Літо (+45 °C):", size=10, color=POS, bold=True, anchor="start"))
    f.append(text(rx + 20, 228, "• MPPT збирає: 15.2 Вт", size=9.5, color=INK, anchor="start"))
    f.append(text(rx + 20, 246, "• PWM збирає: 14.0 Вт (92%)", size=9.5, color=INK, anchor="start"))
    f.append(text(rx + 20, 264, "• Різниця нівелюється", size=9.5, color=MUTED, anchor="start"))

    f.append(fitbox(rx + 10, 284, 220, 46, "Висновок: MPPT критичний\nсаме взимку, коли кожен ват\nна вагу золота.", size=9.5, fill="#fef2f2", stroke=C_LOSS, sw=1.1))

    render(os.path.join(IMG, "mppt-vs-pwm-iv-power.svg"), W, H, *f)


# ── 4. Сезонна інсоляція PSH та баланс енергії за місяцями ───────────────────
def fig_monthly_psh():
    """Стовпчиковий графік сонячних годин (PSH) за 12 місяців для широти 50°N.
    Показує зимове «пляшкове горло» (грудень 1.1 PSH проти червня 5.8 PSH)."""
    W, H = 840, 420
    f = [text(W / 2, 28, "Сезонний розподіл сонячної енергії (PSH) на широті 50°N", size=16, bold=True)]

    ox, oy = 80, 330
    pw, ph = 710, 230

    # Осі
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
    f.append(text(ox + pw / 2, oy + 42, "Місяці року (1 — Січень .. 12 — Грудень) →", size=11, color=MUTED))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">Пікові сонячні години (PSH, год/доба)</text>'
             % (ox - 46, oy - ph / 2, FONT, MUTED, ox - 46, oy - ph / 2))

    max_psh = 7.0
    for p in range(0, 8):
        yy = oy - (p / max_psh) * ph
        f.append(line(ox - 5, yy, ox, yy, color=INK, sw=1))
        f.append(text(ox - 10, yy + 4, "%d" % p, size=10, color=MUTED, anchor="end"))

    # Дані PSH для 50°N (Київ / Центральна Європа), оптимальний зимовий нахил 60°
    months = ["Січ", "Лют", "Бер", "Кві", "Тра", "Чер", "Лип", "Сер", "Вер", "Жов", "Лис", "Гру"]
    psh_val = [1.25, 2.10, 3.40, 4.60, 5.40, 5.80, 5.70, 5.10, 3.90, 2.60, 1.40, 1.10]

    n = len(psh_val)
    step = pw / n
    bw = 36

    for i, (m_name, psh) in enumerate(zip(months, psh_val)):
        cx = ox + step * (i + 0.5)
        bh_bar = (psh / max_psh) * ph
        cy_bar = oy - bh_bar

        if psh < 2.0:
            col_bar = C_LOSS
        elif psh < 4.0:
            col_bar = C_SOLAR
        else:
            col_bar = FIELD

        f.append(rect(cx - bw / 2, cy_bar, bw, bh_bar, fill=col_bar, stroke=col_bar, sw=1.2, rx=4))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s" fill-opacity="0.25"/>'
                 % (cx - bw / 2, cy_bar, bw, bh_bar, col_bar))

        f.append(text(cx, cy_bar - 8, "%.1f" % psh, size=9.5, color=col_bar, bold=True))
        f.append(text(cx, oy + 18, m_name, size=9.5, color=INK))

    # Пояснювальний бейдж угорі зліва
    f.append(fitbox(ox + 20, 52, 350, 38,
                    "Розрахунок автономного вузла ЗАВЖДИ\nведеться за найгіршим місяцем (грудень: 1.1 PSH).",
                    size=9.5, fill="#fef2f2", stroke=C_LOSS, sw=1.2))

    render(os.path.join(IMG, "monthly-psh-energy-balance.svg"), W, H, *f)


if __name__ == "__main__":
    fig_system_energy_flow()
    fig_battery_autonomy_discharge()
    fig_mppt_vs_pwm()
    fig_monthly_psh()
    print("OK: 4 figures generated into", IMG)
