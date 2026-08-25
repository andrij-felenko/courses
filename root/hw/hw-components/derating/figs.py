# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра
AMBER   = "#d97706"
AMBERBG = "#fffbeb"
REDBG   = "#fef2f2"
GRNBG   = "#f0fdf4"
BLUEBG  = "#eff6ff"
BORDER  = "#cbd5e1"
GRAYBG  = "#f8fafc"

# ── 1. derating-zones: зони навантаження компонента ─────────────────────────
def fig_derating_zones():
    W, H = 760, 360
    p = []

    p.append(rect(40, 40, 680, 260, fill=GRAYBG, stroke=BORDER, sw=1.5, rx=8))

    # Зона 1: Дератована робоча область (0% - 60%) - зелена
    p.append(rect(60, 80, 240, 160, fill=GRNBG, stroke=FIELD, sw=2, rx=6))
    p.append(text(180, 110, "Зона дератингу (≤ 50–70 %)", size=13, color=FIELD, bold=True))
    p.append(text(180, 135, "Робоча область надійної схеми", size=10, color=INK))
    p.append(text(180, 160, "Низька інтенсивність відмов λ", size=10, color=INK))
    p.append(text(180, 185, "Стійкість до кидків і старіння", size=10, color=FIELD, bold=True))
    p.append(text(180, 210, "Гарантований багаторічний ресурс", size=10, color=INK))

    # Зона 2: Паспортний запас (60% - 100%) - бурштинова
    p.append(rect(310, 80, 200, 160, fill=AMBERBG, stroke=AMBER, sw=2, rx=6))
    p.append(text(410, 110, "Паспортна зона (70–100 %)", size=12, color=AMBER, bold=True))
    p.append(text(410, 135, "Формально дозволено", size=10, color=INK))
    p.append(text(410, 160, "Але стрімко росте λ", size=10, color=POS))
    p.append(text(410, 185, "Прискорене старіння", size=10, color=INK))
    p.append(text(410, 210, "Немає запасу на викиди", size=10, color=AMBER, bold=True))

    # Зона 3: Зона руйнування (> 100% / Absolute Max) - червона
    p.append(rect(520, 80, 180, 160, fill=REDBG, stroke=POS, sw=2, rx=6))
    p.append(text(610, 110, "Absolute Max (> 100 %)", size=12, color=POS, bold=True))
    p.append(text(610, 135, "Межа знищення", size=10, color=POS, bold=True))
    p.append(text(610, 160, "Електричний пробій", size=10, color=INK))
    p.append(text(610, 185, "Теплове руйнування", size=10, color=INK))
    p.append(text(610, 210, "Негайний вихід з ладу", size=10, color=POS))

    # Нижня стрілка навантаження
    p.append(arrow(60, 275, 690, 275, color=LINE, sw=2))
    p.append(text(70, 265, "0 %", size=10, color=INK, anchor="start", bold=True))
    p.append(text(300, 265, "50–70 % (Номінал дератингу)", size=10, color=FIELD, anchor="middle", bold=True))
    p.append(text(510, 265, "100 % (Паспортний рейтинг)", size=10, color=AMBER, anchor="middle", bold=True))
    p.append(text(690, 265, "Max Rating", size=10, color=POS, anchor="end", bold=True))

    p.append(text(380, 335, "Рівні навантаження компонента: безпечний інженерний коридор проти паспортних меж", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "derating-zones.svg"), W, H, *p, title="Зони дератингу компонентів")


# ── 2. thermal-derating-curve: крива теплового зниження потужності ───────────
def fig_thermal_derating_curve():
    W, H = 760, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    ox, oy = 90, 340
    gw, gh = 600, 260

    for y_val, label in [(0, "0 %"), (0.25, "25 %"), (0.5, "50 %"), (0.75, "75 %"), (1.0, "100 %")]:
        y_pos = oy - y_val * gh
        p.append(line(ox, y_pos, ox + gw, y_pos, color="#e2e8f0", sw=1))
        p.append(text(ox - 12, y_pos + 4, label, size=10, color=MUTED, anchor="end"))

    for temp, x_ratio in [(25, 0.0), (70, 0.36), (105, 0.64), (125, 0.78), (155, 1.0)]:
        x_pos = ox + x_ratio * gw
        p.append(line(x_pos, oy, x_pos, oy - gh, color="#e2e8f0", sw=1))
        p.append(text(x_pos, oy + 20, f"+{temp} °C", size=10, color=MUTED, anchor="middle"))

    p.append(arrow(ox, oy, ox + gw + 40, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=1.8))
    p.append(text(ox + gw + 40, oy + 32, "Температура середовища Ta", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - gh - 15, "Допустима потужність P / P_rated", size=11, color=INK, anchor="start", bold=True))

    x70 = ox + 0.36 * gw
    x155 = ox + 1.0 * gw
    y100 = oy - gh

    p.append(line(ox, y100, x70, y100, color=POS, sw=2.5))
    p.append(line(x70, y100, x155, oy, color=POS, sw=2.5))

    p.append(circle(x70, y100, 4, fill=POS))
    p.append(circle(x155, oy, 4, fill=POS))
    p.append(text(x70 + 8, y100 - 10, "Точка перегину (+70 °C, 100 %)", size=10, color=POS, anchor="start", bold=True))
    p.append(text(x155, oy - 10, "Tmax (+155 °C)", size=10, color=POS, anchor="middle", bold=True))

    y50 = oy - 0.5 * gh
    x125 = ox + 0.78 * gw
    p.append(line(ox, y50, x70, y50, color=FIELD, sw=2.5))
    p.append(line(x70, y50, x125, oy, color=FIELD, sw=2.5))
    p.append(circle(x70, y50, 4, fill=FIELD))
    p.append(circle(x125, oy, 4, fill=FIELD))

    p.append(text(ox + 0.18 * gw, (y100 + y50) / 2 + 4, "Запас надійності (50 % дератинг)", size=10, color=FIELD, anchor="middle", bold=True))

    x105 = ox + 0.64 * gw
    y_pass_105 = oy - 0.588 * gh
    y_der_105 = oy - 0.182 * gh

    p.append(line(x105, oy, x105, y_pass_105, color=AMBER, sw=1.5, dash="4,4"))
    p.append(circle(x105, y_pass_105, 4, fill=POS))
    p.append(circle(x105, y_der_105, 4, fill=FIELD))
    p.append(text(x105 + 8, y_pass_105 - 6, "Паспортна межа: ~59 %", size=9, color=POS, anchor="start"))
    p.append(text(x105 + 8, y_der_105 - 6, "Дератована межа: ~18 %", size=9, color=FIELD, anchor="start", bold=True))

    p.append(rect(450, 45, 270, 70, fill=GRAYBG, stroke=BORDER, sw=1, rx=4))
    p.append(line(465, 65, 495, 65, color=POS, sw=2.5))
    p.append(text(505, 69, "Паспортна крива (Datasheet Max)", size=10, color=INK, anchor="start"))
    p.append(line(465, 95, 495, 95, color=FIELD, sw=2.5))
    p.append(text(505, 99, "Дератована крива (MIL/IPC-9592B)", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "thermal-derating-curve.svg"), W, H, *p, title="Температурний дератинг потужності")


# ── 3. arrhenius-failure-rate: інтенсивність відмов λ та закон Арреніуса ─────
def fig_arrhenius_failure_rate():
    W, H = 760, 380
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    ox, oy = 90, 310
    gw, gh = 600, 220

    for i in range(5):
        y = oy - i * (gh / 4)
        p.append(line(ox, y, ox + gw, y, color="#e2e8f0", sw=1))

    p.append(text(ox - 12, oy + 4, "1× (База)", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 12, oy - gh * 0.25 + 4, "4×", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 12, oy - gh * 0.5 + 4, "16×", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 12, oy - gh * 0.75 + 4, "64×", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 12, oy - gh + 4, "256×", size=10, color=MUTED, anchor="end"))

    temps = [25, 45, 65, 85, 105, 125, 150]
    for idx, t_val in enumerate(temps):
        x = ox + idx * (gw / (len(temps) - 1))
        p.append(line(x, oy, x, oy - gh, color="#e2e8f0", sw=1))
        p.append(text(x, oy + 20, f"+{t_val} °C", size=10, color=MUTED, anchor="middle"))

    p.append(arrow(ox, oy, ox + gw + 40, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=1.8))
    p.append(text(ox + gw + 40, oy + 32, "Температура кристала / діелектрика Tj", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - gh - 15, "Відносна інтенсивність відмов λ(T) / λ₀", size=11, color=INK, anchor="start", bold=True))

    points = []
    for step in range(101):
        frac = step / 100.0
        y_val = (math.exp(frac * 4.2) - 1) / (math.exp(4.2) - 1) * gh
        points.append((ox + frac * gw, oy - y_val))

    for i in range(len(points) - 1):
        p.append(line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], color=POS, sw=3))

    x85 = ox + 3 * (gw / 6)
    y85_val = (math.exp(0.5 * 4.2) - 1) / (math.exp(4.2) - 1) * gh
    p.append(circle(x85, oy - y85_val, 5, fill=FIELD))
    p.append(line(x85, oy, x85, oy - y85_val, color=FIELD, sw=1.5, dash="3,3"))
    p.append(text(x85 - 10, oy - y85_val - 12, "Дератинг: Tj ≤ 85 °C (Низька λ, довгий ресурс)", size=10, color=FIELD, anchor="end", bold=True))

    x150 = ox + gw
    p.append(circle(x150, oy - gh, 5, fill=POS))
    p.append(text(x150 - 10, oy - gh + 15, "Tj_max = 150 °C (λ зростає у сотні разів)", size=10, color=POS, anchor="end", bold=True))

    p.append(rect(110, 45, 340, 75, fill=GRAYBG, stroke=BORDER, sw=1, rx=4))
    p.append(text(120, 68, "Модель Арреніуса: AF = exp( (Ea/k) · (1/T₁ − 1/T₂) )", size=10, color=INK, anchor="start", bold=True))
    p.append(text(120, 90, "Правило 10 °C: кожні 10 °C зниження температури", size=9, color=FIELD, anchor="start"))
    p.append(text(120, 108, "кристала збільшують напрацювання MTBF удвічі", size=9, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "arrhenius-failure-rate.svg"), W, H, *p, title="Інтенсивність відмов та закон Арреніуса")


# ── 4. soa-derating: дератинг області безпечної роботи MOSFET (SOA) ──────────
def fig_soa_derating():
    W, H = 760, 440
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    ox, oy = 90, 360
    gw, gh = 600, 280

    for v_val, label in [(1, "1 В"), (10, "10 В"), (100, "100 В")]:
        x = ox + (math.log10(v_val) / 2.0) * gw
        p.append(line(x, oy, x, oy - gh, color="#e2e8f0", sw=1))
        p.append(text(x, oy + 20, label, size=10, color=MUTED, anchor="middle"))

    for i_val, label in [(0.1, "0.1 А"), (1, "1 А"), (10, "10 А"), (100, "100 А")]:
        y = oy - ((math.log10(i_val) + 1.0) / 3.0) * gh
        p.append(line(ox, y, ox + gw, y, color="#e2e8f0", sw=1))
        p.append(text(ox - 12, y + 4, label, size=10, color=MUTED, anchor="end"))

    p.append(arrow(ox, oy, ox + gw + 40, oy, color=LINE, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - gh - 25, color=LINE, sw=1.8))
    p.append(text(ox + gw + 40, oy + 32, "Напруга стік-витік Vds", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - gh - 15, "Струм стоку Id", size=11, color=INK, anchor="start", bold=True))

    def get_x(v): return ox + (math.log10(v) / 2.0) * gw
    def get_y(i): return oy - ((math.log10(i) + 1.0) / 3.0) * gh

    p_soa = [
        (get_x(1.0), get_y(30.0)),
        (get_x(2.0), get_y(60.0)),
        (get_x(5.0), get_y(60.0)),
        (get_x(20.0), get_y(7.5)),
        (get_x(45.0), get_y(1.2)),
        (get_x(60.0), get_y(0.4)),
        (get_x(60.0), get_y(0.1)),
        (get_x(1.0), get_y(0.1)),
    ]

    path_d = f"M {p_soa[0][0]:.1f} {p_soa[0][1]:.1f} " + " ".join([f"L {pt[0]:.1f} {pt[1]:.1f}" for pt in p_soa[1:]]) + " Z"
    p.append(f'<path d="{path_d}" fill="{REDBG}" stroke="{POS}" stroke-width="2"/>')

    p_soa_der = [
        (get_x(1.0), get_y(25.0)),
        (get_x(1.4), get_y(36.0)),
        (get_x(3.5), get_y(36.0)),
        (get_x(15.0), get_y(3.3)),
        (get_x(35.0), get_y(0.5)),
        (get_x(48.0), get_y(0.2)),
        (get_x(48.0), get_y(0.1)),
        (get_x(1.0), get_y(0.1)),
    ]

    path_der_d = f"M {p_soa_der[0][0]:.1f} {p_soa_der[0][1]:.1f} " + " ".join([f"L {pt[0]:.1f} {pt[1]:.1f}" for pt in p_soa_der[1:]]) + " Z"
    p.append(f'<path d="{path_der_d}" fill="{GRNBG}" stroke="{FIELD}" stroke-width="2"/>')

    p.append(text(get_x(1.2), get_y(45.0), "Межа Rds(on)", size=9, color=INK, anchor="start", bold=True))
    p.append(text(get_x(3.0), get_y(68.0), "Межа струму виводів (Id max)", size=9, color=POS, anchor="start"))
    p.append(text(get_x(14.0), get_y(15.0), "Теплова межа потужності", size=9, color=POS, anchor="start"))
    p.append(text(get_x(32.0), get_y(3.2), "Нестабільність (Spirito)", size=9, color=POS, anchor="start"))
    p.append(text(get_x(60.0) + 4, get_y(1.0), "Vds max (60 В)", size=9, color=POS, anchor="start", bold=True))

    p.append(rect(430, 45, 290, 80, fill=GRAYBG, stroke=BORDER, sw=1, rx=4))
    p.append(line(445, 68, 475, 68, color=POS, sw=2))
    p.append(text(485, 72, "Паспортна SOA (Tc = 25 °C, DC)", size=10, color=INK, anchor="start"))
    p.append(line(445, 98, 475, 98, color=FIELD, sw=2))
    p.append(text(485, 102, "Дератована SOA (Tc = 100 °C, 80 % Vds)", size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "soa-derating.svg"), W, H, *p, title="Дератинг області безпечної роботи MOSFET")


# ── 5. capacitor-voltage-derating: дератинг конденсаторів за напругою ─────────
def fig_capacitor_voltage_derating():
    W, H = 760, 360
    p = []

    p.append(rect(0, 0, W, H, fill=BG))

    cards = [
        {
            "title": "Тантал (MnO₂)",
            "derating": "≤ 50 % (0.50)",
            "color": POS,
            "bg": REDBG,
            "reason": "Екзотермічний пробій діелектрика Ta₂O₅;",
            "sub": "горіння MnO₂ катода при стрибках напруги."
        },
        {
            "title": "Тантал (Полімер)",
            "derating": "≤ 70–80 % (0.70)",
            "color": AMBER,
            "bg": AMBERBG,
            "reason": "Полімерний провідний катод не підтримує",
            "sub": "горіння; вища стійкість до кидків струму."
        },
        {
            "title": "Кераміка (MLCC X7R/X5R)",
            "derating": "≤ 60–70 % (0.60)",
            "color": FIELD,
            "bg": GRNBG,
            "reason": "Врахування ефекту DC-bias (падіння C на 50–80 %);",
            "sub": "захист від мікротріщин та п'єзо-ефекту."
        },
        {
            "title": "Алюмінієвий електроліт",
            "derating": "≤ 70–80 % (0.70)",
            "color": NEG,
            "bg": BLUEBG,
            "reason": "Запас за напругою + жорсткий дератинг струму",
            "sub": "пульсацій I_ripple (≤ 70 %) для запобігання висиханню."
        },
    ]

    card_w = 680
    card_h = 60
    start_x = 40
    start_y = 40

    for i, c in enumerate(cards):
        y = start_y + i * 72
        p.append(rect(start_x, y, card_w, card_h, fill=c["bg"], stroke=c["color"], sw=1.8, rx=6))

        p.append(text(start_x + 16, y + 25, c["title"], size=12, color=INK, anchor="start", bold=True))
        p.append(text(start_x + 230, y + 25, f"V_раб / V_ном {c['derating']}", size=11, color=c["color"], anchor="start", bold=True))
        p.append(text(start_x + 16, y + 48, c["reason"] + " " + c["sub"], size=9.5, color=INK, anchor="start"))

    p.append(text(380, 340, "Правила дератингу напруги для основних класів конденсаторів за стандартами MIL-HDBK-338B та IPC-9592B", size=9.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "capacitor-voltage-derating.svg"), W, H, *p, title="Дератинг конденсаторів за типами діелектрика")


if __name__ == "__main__":
    fig_derating_zones()
    fig_thermal_derating_curve()
    fig_arrhenius_failure_rate()
    fig_soa_derating()
    fig_capacitor_voltage_derating()
    print("All figures generated successfully.")
