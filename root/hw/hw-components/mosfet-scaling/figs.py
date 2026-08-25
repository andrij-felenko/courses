# -*- coding: utf-8 -*-
"""Фігури теми «Масштабування MOSFET і закон Денарда» (book/electronics/microelectronics/mosfet-scaling).
Запуск: python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Принцип масштабування постійного поля Денарда ────────────────────────
def fig_dennard_principle():
    W, H = 760, 360
    out = []

    # Ліва колонка: Базовий транзистор
    cx1 = 190
    out.append(text(cx1, 32, "Покоління N (вихідний MOSFET)", size=14, color=INK, bold=True))
    out.append(text(cx1, 50, "Розміри: L, W, tox | Напруга: Vdd", size=11, color=MUTED))

    # Корпус/підкладка ліворуч
    out.append(rect(cx1 - 140, 75, 280, 160, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    out.append(text(cx1 - 100, 215, "p-підкладка (Na)", size=11, color=MUTED))

    # Витік і стік
    out.append(rect(cx1 - 130, 75, 60, 45, fill="#d6e4ff", stroke=NEG, sw=1.4, rx=2))
    out.append(text(cx1 - 100, 102, "n+ (витік)", size=10.5, color=NEG, bold=True))

    out.append(rect(cx1 + 70, 75, 60, 45, fill="#d6e4ff", stroke=NEG, sw=1.4, rx=2))
    out.append(text(cx1 + 100, 102, "n+ (стік)", size=10.5, color=NEG, bold=True))

    # Оксид і затвор
    out.append(rect(cx1 - 60, 68, 120, 7, fill="#ffe8cc", stroke="#d97706", sw=1.2, rx=1))
    out.append(text(cx1, 62, "SiO2 (tox)", size=10, color="#d97706", bold=True))

    out.append(rect(cx1 - 55, 38, 110, 30, fill="#e2e8f0", stroke="#475569", sw=1.4, rx=2))
    out.append(text(cx1, 57, "Затвор (Gate)", size=11, color="#334155", bold=True))

    # Канал
    out.append(line(cx1 - 70, 75, cx1 + 70, 75, color=POS, sw=2.5, dash="4,2"))
    out.append(text(cx1, 95, "довжина каналу L", size=10.5, color=POS, bold=True))

    # Збіднена область
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,3"/>' % (cx1 - 135, 120, 270, 45, FIELD))
    out.append(text(cx1, 150, "глибина збіднення xd", size=10, color=FIELD))

    # Поле внизу зліва
    box1, _, _ = textbox(cx1, 280, "Поле E = Vdd / L\nГустина потужності P / A = 1.0", size=11.5, pad=8,
                         fill="#f8fafc", stroke=LINE, sw=1.2)
    out.append(box1)

    # Стрілка масштабування
    out.append(arrow(345, 155, 410, 155, color=POS, sw=2.2))
    out.append(text(378, 142, "Масштаб", size=11, color=POS, bold=True))
    out.append(text(378, 172, "фактор κ > 1", size=10.5, color=INK))

    # Права колонка: Масштабований транзистор
    cx2 = 565
    out.append(text(cx2, 32, "Покоління N+1 (масштаб Денарда)", size=14, color=INK, bold=True))
    out.append(text(cx2, 50, "Розміри: L/κ, tox/κ | Напруга: Vdd/κ", size=11, color=MUTED))

    # Корпус/підкладка праворуч (менший розмір)
    out.append(rect(cx2 - 100, 95, 200, 120, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    out.append(text(cx2 - 60, 200, "p-підкладка (κ·Na)", size=10.5, color=MUTED))

    # Витік і стік
    out.append(rect(cx2 - 92, 95, 42, 32, fill="#d6e4ff", stroke=NEG, sw=1.4, rx=2))
    out.append(text(cx2 - 71, 114, "n+", size=10, color=NEG, bold=True))

    out.append(rect(cx2 + 50, 95, 42, 32, fill="#d6e4ff", stroke=NEG, sw=1.4, rx=2))
    out.append(text(cx2 + 71, 114, "n+", size=10, color=NEG, bold=True))

    # Оксид і затвор
    out.append(rect(cx2 - 42, 90, 84, 5, fill="#ffe8cc", stroke="#d97706", sw=1.1, rx=1))
    out.append(text(cx2, 85, "tox / κ", size=9.5, color="#d97706", bold=True))

    out.append(rect(cx2 - 38, 68, 76, 22, fill="#e2e8f0", stroke="#475569", sw=1.3, rx=2))
    out.append(text(cx2, 82, "Затвор", size=10, color="#334155", bold=True))

    # Канал
    out.append(line(cx2 - 50, 95, cx2 + 50, 95, color=POS, sw=2.2, dash="3,2"))
    out.append(text(cx2, 110, "L / κ", size=10, color=POS, bold=True))

    # Збіднена область
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="none" stroke="%s" stroke-width="1.1" stroke-dasharray="3,3"/>' % (cx2 - 95, 127, 190, 32, FIELD))
    out.append(text(cx2, 148, "xd / κ (легування κ·Na)", size=9.5, color=FIELD))

    # Поле внизу справа
    box2, _, _ = textbox(cx2, 280, "Поле E' = (Vdd/κ)/(L/κ) = E = const\nГустина потужності P' / A' = 1.0 (стала!)",
                         size=11.5, pad=8, fill="#eaf7ed", stroke=FIELD, sw=1.4, color="#166534")
    out.append(box2)

    return render(os.path.join(IMG, "dennard-scaling-principle.svg"), W, H, *out,
                  title="Класичне пропорційне масштабування Денарда (Constant-Field)")


# ── 2. Таблиця зміни параметрів під час масштабування ───────────────────────
def fig_scaling_trends():
    W, H = 760, 350
    out = []

    out.append(text(W / 2, 40, "Як змінюються параметри кола при коефіцієнті зменшення κ > 1", size=13, color=MUTED))

    # Заголовок таблиці
    headers = ["Параметр схеми", "Формула зв'язку", "Масштаб (CFS)", "Фізичний наслідок"]
    col_w = [180, 160, 130, 230]
    col_x = [30, 210, 370, 500]
    y0 = 65
    rh = 34

    # Шапка
    out.append(rect(30, y0, 700, rh, fill="#e2e8f0", stroke=LINE, sw=1.4, rx=3))
    for i, h in enumerate(headers):
        out.append(text(col_x[i] + col_w[i] / 2, y0 + 22, h, size=12, color=INK, bold=True))

    rows = [
        ("Розміри (L, W, tox)", "Геометрія приладу", "1 / κ (↓)", "Зменшення площі у κ² разів", False),
        ("Напруга живлення Vdd", "Електричний потенціал", "1 / κ (↓)", "Збереження поля E = const", False),
        ("Ємність затвора Cg", "ε·W·L / tox", "1 / κ (↓)", "Швидший перезаряд ємності", False),
        ("Затримка ключа τ", "Cg · Vdd / Id", "1 / κ (↓)", "Зростання частоти f ∝ κ (↑)", True),
        ("Потужність транзистора P", "Cg · Vdd² · f", "1 / κ² (↓)", "Кожен ключ споживає вдвічі менше", False),
        ("Щільність транзисторів", "Кількість / Площа", "κ² (↑)", "Подвоєння за законом Мура", True),
        ("Густина потужності P/A", "P_total / Площа чипа", "1.0 (const)", "Температура чипа не зростає!", True),
    ]

    for idx, (p_name, p_form, p_scale, p_res, highlight) in enumerate(rows):
        y = y0 + (idx + 1) * rh
        fill = "#eaf7ed" if highlight else (FILL if idx % 2 == 0 else BG)
        stroke = FIELD if highlight else "#cbd5e1"
        sw = 1.3 if highlight else 1.0

        out.append(rect(30, y, 700, rh, fill=fill, stroke=stroke, sw=sw, rx=0))
        out.append(text(col_x[0] + 12, y + 21, p_name, size=11.5, color=INK, anchor="start", bold=highlight))
        out.append(text(col_x[1] + col_w[1] / 2, y + 21, p_form, size=11, color=MUTED))
        out.append(text(col_x[2] + col_w[2] / 2, y + 21, p_scale, size=11.5,
                        color=POS if "κ²" in p_scale or "const" in p_scale else INK, bold=True))
        out.append(text(col_x[3] + 12, y + 21, p_res, size=11.5,
                        color="#166534" if highlight else INK, anchor="start", bold=highlight))

    return render(os.path.join(IMG, "scaling-trends.svg"), W, H, *out,
                  title="Правила масштабування Денарда: золоте співвідношення 1974–2005 років")


# ── 3. Підпороговий витік і межа 60 мВ/декаду ──────────────────────────────
def fig_subthreshold_limit():
    W, H = 760, 360
    out = []

    # Вісі координат
    ax_x0, ax_y0 = 90, 290
    ax_w, ax_h = 360, 230

    out.append(line(ax_x0, ax_y0, ax_x0 + ax_w + 30, ax_y0, color=INK, sw=1.5))  # X
    out.append(line(ax_x0, ax_y0, ax_x0, ax_y0 - ax_h - 15, color=INK, sw=1.5))  # Y

    out.append(text(ax_x0 + ax_w + 25, ax_y0 + 20, "Напруга затвора Vgs (В)", size=11.5, color=INK, anchor="end"))
    out.append(text(ax_x0 - 15, ax_y0 - ax_h - 10, "lg(Струм стоку Id)", size=11.5, color=INK, anchor="start"))

    # Позначки осі Y (логарифмічні порядки)
    y_ticks = [
        (0, "1 мА (ON)"),
        (55, "1 мкА"),
        (110, "1 нА"),
        (165, "1 пА"),
        (220, "1 фА (OFF)"),
    ]
    for dy, lbl in y_ticks:
        y = ax_y0 - ax_h + dy
        out.append(line(ax_x0 - 4, y, ax_x0, y, color=MUTED, sw=1.2))
        out.append(line(ax_x0, y, ax_x0 + ax_w, y, color="#f1f5f9", sw=1.0))
        out.append(text(ax_x0 - 10, y + 4, lbl, size=10, color=MUTED, anchor="end"))

    # Позначки осі X
    x_ticks = [(0, "0 В"), (90, "0.3 В"), (180, "0.6 В"), (270, "0.9 В"), (360, "1.2 В")]
    for dx, lbl in x_ticks:
        x = ax_x0 + dx
        out.append(line(x, ax_y0, x, ax_y0 + 4, color=MUTED, sw=1.2))
        out.append(text(x, ax_y0 + 18, lbl, size=10.5, color=MUTED))

    # Крива 1: Старий техпроцес (Vth = 0.7 В)
    # Від (90, 270) вгору до (300, 60)
    out.append(line(ax_x0, ax_y0 - 10, ax_x0 + 210, ax_y0 - 210, color=NEG, sw=2.2))
    out.append(line(ax_x0 + 210, ax_y0 - 210, ax_x0 + 360, ax_y0 - 230, color=NEG, sw=2.2))
    out.append(circle(ax_x0, ax_y0 - 10, 4, fill=NEG, stroke=BG, sw=1.5))
    out.append(text(ax_x0 + 210, ax_y0 - 225, "Vth = 0.7 В", size=10.5, color=NEG, bold=True))
    out.append(text(ax_x0 + 15, ax_y0 - 22, "I_off ≈ 10⁻¹⁴ А", size=9.5, color=NEG))

    # Крива 2: Масштабований техпроцес (Vth = 0.25 В)
    # Зсунута ліворуч!
    out.append(line(ax_x0, ax_y0 - 120, ax_x0 + 100, ax_y0 - 210, color=POS, sw=2.2))
    out.append(line(ax_x0 + 100, ax_y0 - 210, ax_x0 + 250, ax_y0 - 230, color=POS, sw=2.2))
    out.append(circle(ax_x0, ax_y0 - 120, 4, fill=POS, stroke=BG, sw=1.5))
    out.append(text(ax_x0 + 100, ax_y0 - 225, "Vth = 0.25 В", size=10.5, color=POS, bold=True))
    out.append(text(ax_x0 + 45, ax_y0 - 130, "I_off ≈ 10⁻⁸ А (катастрофа!)", size=10, color=POS, bold=True))

    # Стрілка нахилу підпорогової області (Subthreshold Swing)
    out.append(arrow(ax_x0 + 80, ax_y0 - 45, ax_x0 + 130, ax_y0 - 95, color=FIELD, sw=1.8))
    out.append(text(ax_x0 + 160, ax_y0 - 65, "Підпороговий нахил S ≥ 60 мВ/дек", size=10.5, color=FIELD, bold=True))
    out.append(text(ax_x0 + 160, ax_y0 - 50, "S = ln(10)·(kB·T/q) — фізична стала", size=9.5, color=MUTED))

    # Пояснювальний блок праворуч
    bx0, by0 = 500, 75
    out.append(rect(bx0, by0, 235, 215, fill="#fef2f2", stroke=POS, sw=1.5, rx=5))
    out.append(text(bx0 + 117, by0 + 22, "Чому Vth не можна знижувати", size=12, color=POS, bold=True))

    p_lines = [
        "1. Нахил S обмежений",
        "термічним розподілом",
        "Больцмана (kB·T/q).",
        "",
        "2. Щоб закрити ключ",
        "(I_on/I_off > 10⁶), треба",
        "діапазон Vgs не менше 0.4 В.",
        "",
        "3. При Vth < 0.3 В струм",
        "витоку в спокої зростає",
        "експоненційно — чип кипить!"
    ]
    for i, line_str in enumerate(p_lines):
        if line_str:
            out.append(text(bx0 + 14, by0 + 46 + i * 14.5, line_str, size=10.5,
                            color=INK if not line_str.startswith("3.") else POS,
                            anchor="start", bold=line_str.startswith(("1.", "2.", "3."))))

    return render(os.path.join(IMG, "subthreshold-limit.svg"), W, H, *out,
                  title="Фундаментальний тепловий бар'єр підпорогового струму витоку")


# ── 4. Колапс закону Денарда та Power Wall ─────────────────────────────────
def fig_power_wall_collapse():
    W, H = 760, 360
    out = []

    ax_x0, ax_y0 = 80, 290
    ax_w, ax_h = 630, 220

    out.append(line(ax_x0, ax_y0, ax_x0 + ax_w + 20, ax_y0, color=INK, sw=1.5))  # X
    out.append(line(ax_x0, ax_y0, ax_x0, ax_y0 - ax_h - 15, color=INK, sw=1.5))  # Y

    # Позначки років
    years = [(0, "1980"), (130, "1990"), (260, "2000"), (320, "2005"), (450, "2015"), (580, "2025")]
    for dx, yr in years:
        x = ax_x0 + dx
        out.append(line(x, ax_y0, x, ax_y0 + 5, color=MUTED, sw=1.2))
        out.append(text(x, ax_y0 + 18, yr, size=11, color=INK, bold=(yr == "2005")))

    # Вертикальна лінія краху Денарда (~2005 рік)
    cx_split = ax_x0 + 320
    out.append(line(cx_split, ax_y0, cx_split, ax_y0 - ax_h - 10, color=POS, sw=1.8, dash="5,3"))
    out.append(rect(cx_split - 70, ax_y0 - ax_h - 5, 140, 24, fill="#fdecea", stroke=POS, sw=1.3, rx=3))
    out.append(text(cx_split, ax_y0 - ax_h + 11, "2004–2005: Power Wall", size=10.5, color=POS, bold=True))

    # Зона 1: Ера Денарда (зліва)
    out.append(rect(ax_x0 + 10, ax_y0 - ax_h + 25, 180, 38, fill="#eaf7ed", stroke=FIELD, sw=1.2, rx=3))
    out.append(text(ax_x0 + 100, ax_y0 - ax_h + 40, "Ера класичного Денарда", size=11, color="#166534", bold=True))
    out.append(text(ax_x0 + 100, ax_y0 - ax_h + 55, "Частота ↑, Потужність/мм² ≈ const", size=9.5, color="#166534"))

    # Зона 2: Ера після Денарда (справа)
    out.append(rect(cx_split + 40, ax_y0 - ax_h + 25, 230, 38, fill="#f8fafc", stroke=LINE, sw=1.2, rx=3))
    out.append(text(cx_split + 155, ax_y0 - ax_h + 40, "Ера після краху Денарда", size=11, color=INK, bold=True))
    out.append(text(cx_split + 155, ax_y0 - ax_h + 55, "Багатоядерність, FinFET, Dark Silicon", size=9.5, color=MUTED))

    # Крива 1: Транзистори (Закон Мура) — експонента вгору без зупинки
    m_pts = [(0, 270), (130, 225), (260, 160), (320, 125), (450, 65), (580, 20)]
    for i in range(len(m_pts) - 1):
        x1, y1 = ax_x0 + m_pts[i][0], ax_y0 - (290 - m_pts[i][1])
        x2, y2 = ax_x0 + m_pts[i+1][0], ax_y0 - (290 - m_pts[i+1][1])
        out.append(line(x1, y1, x2, y2, color="#2563eb", sw=2.5))
    out.append(text(ax_x0 + 580, ax_y0 - 275, "Транзистори (Мур)", size=11, color="#2563eb", bold=True))

    # Крива 2: Тактова частота одноядерного процесора (GHz) — стрімкий ріст, потім плато на 3.5–5 GHz
    f_pts = [(0, 285), (130, 260), (260, 180), (320, 115), (380, 110), (450, 105), (580, 95)]
    for i in range(len(f_pts) - 1):
        x1, y1 = ax_x0 + f_pts[i][0], ax_y0 - (290 - f_pts[i][1])
        x2, y2 = ax_x0 + f_pts[i+1][0], ax_y0 - (290 - f_pts[i+1][1])
        out.append(line(x1, y1, x2, y2, color=FIELD, sw=2.5))
    out.append(text(ax_x0 + 490, ax_y0 - 195, "Тактова частота (плато ~4-5 ГГц)", size=11, color="#15803d", bold=True))

    # Крива 3: Питома потужність / Тепловиділення чипа (Вт) — стабілізація на межі охолодження (100–250 Вт)
    p_pts = [(0, 288), (130, 275), (260, 210), (320, 140), (380, 135), (450, 130), (580, 125)]
    for i in range(len(p_pts) - 1):
        x1, y1 = ax_x0 + p_pts[i][0], ax_y0 - (290 - p_pts[i][1])
        x2, y2 = ax_x0 + p_pts[i+1][0], ax_y0 - (290 - p_pts[i+1][1])
        out.append(line(x1, y1, x2, y2, color=POS, sw=2.2, dash="4,2"))
    out.append(text(ax_x0 + 490, ax_y0 - 155, "Тепловий ліміт (Power Wall ≈ 100-250 Вт)", size=11, color=POS, bold=True))

    return render(os.path.join(IMG, "power-wall-collapse.svg"), W, H, *out,
                  title="Хронологія розвитку мікроелектроніки: зіткнення з енергетичним бар'єром")


def main():
    fig_dennard_principle()
    fig_scaling_trends()
    fig_subthreshold_limit()
    fig_power_wall_collapse()
    print("Всі 4 фігури згенеровано в img/")

if __name__ == "__main__":
    main()
