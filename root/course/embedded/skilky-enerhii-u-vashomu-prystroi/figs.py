# -*- coding: utf-8 -*-
"""Фігури для статті skilky-enerhii-u-vashomu-prystroi («Скільки енергії у вашому пристрої»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. three-energy-reservoirs: три резервуари енергії в електроніці ──────────
def fig_three_reservoirs():
    W, H = 820, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=8))

    cards = [
        {
            "x": 30, "w": 235,
            "title": "Електричне поле",
            "subtitle": "Конденсатори",
            "formula": "E = 0.5 · C · V²",
            "items": [
                "Носій: розділені заряди q",
                "Час розряду: 1 нс … 100 мкс",
                "Пікова потужність: до мегаватів",
                "Небезпека: удар струмом,",
                "електрична дуга, вибух"
            ],
            "accent": NEG,
            "badge": "Миттєвий розряд (мкс)"
        },
        {
            "x": 290, "w": 240,
            "title": "Магнітне поле",
            "subtitle": "Індуктивності, мотори, реле",
            "formula": "E = 0.5 · L · I²",
            "items": [
                "Носій: магнітний потік Φ",
                "Час розряду: 10 нс … 10 мс",
                "Пікова напруга: сотні / тисячі В",
                "Небезпека: пробій ключів,",
                "дуга на контактах (V = -L·di/dt)"
            ],
            "accent": FIELD,
            "badge": "Високовольтний сплеск"
        },
        {
            "x": 555, "w": 235,
            "title": "Хімічний зв'язок",
            "subtitle": "Акумулятори (Li-ion, LiPo)",
            "formula": "E = V · Q  (кВт·год / Дж)",
            "items": [
                "Носій: хімічна реакція",
                "Час розряду: хвилини … години",
                "Густина енергії: колосальна",
                "Небезпека: тепловий розгін,",
                "струми КЗ до 200–500 А, пожежа"
            ],
            "accent": POS,
            "badge": "Гігантська ємність (кДж)"
        }
    ]

    for c in cards:
        x, y, w, h = c["x"], 30, c["w"], 300
        p.append(rect(x, y, w, h, fill="#ffffff", stroke=c["accent"], sw=1.8, rx=6))

        p.append(rect(x, y, w, 42, fill=c["accent"], stroke=c["accent"], sw=1.0, rx=0))
        p.append(text(x + w / 2, y + 26, c["title"], size=15, color="#ffffff", bold=True))

        p.append(text(x + w / 2, y + 64, c["subtitle"], size=12, color=INK, bold=True))

        b, bw, bh = textbox(x + w / 2, y + 96, c["formula"], size=13, color=c["accent"],
                            bold=True, fill="#f4f6f8", stroke=c["accent"], sw=1.2, pad=6)
        p.append(b)

        cur_y = y + 138
        for it in c["items"]:
            p.append(circle(x + 16, cur_y - 4, 3, fill=c["accent"], stroke=c["accent"]))
            p.append(text(x + 28, cur_y, it, size=11, color=INK, anchor="start"))
            cur_y += 24

        p.append(rect(x + 12, y + h - 34, w - 24, 24, fill="#edf2f7", stroke=MUTED, sw=1.0, rx=4))
        p.append(text(x + w / 2, y + h - 18, c["badge"], size=11, color=c["accent"], bold=True))

    render(os.path.join(OUT, "three-energy-reservoirs.svg"), W, H, *p,
           title="Три фізичні резервуари накопиченої енергії в електроніці")


# ── 2. capacitor-hazard-scale: шкала енергії конденсаторів і діелектрична абсорбція ──
def fig_capacitor_hazard():
    W, H = 820, 370
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=8))

    # Ліва частина: шкала енергії (x: 25..460)
    p.append(text(240, 36, "Шкала накопиченої енергії E = 0.5 · C · V²", size=14, color=INK, bold=True))

    bars = [
        {"label": "1000 мкФ @ 3.3 В (Логіка)", "val": "5.4 мДж", "w": 40, "col": FIELD, "note": "Безпечно, не відчутно"},
        {"label": "1000 мкФ @ 24 В (Пром. шина)", "val": "288 мДж", "w": 90, "col": "#2980b9", "note": "Легкий укол, іскра"},
        {"label": "10000 мкФ @ 50 В (Аудіо / БЖ)", "val": "12.5 Дж", "w": 220, "col": "#d35400", "note": "Болісний спазм, опік дугою"},
        {"label": "470 мкФ @ 400 В (DC-Bus 230 В)", "val": "37.6 Дж", "w": 320, "col": POS, "note": "Смертельний ризик фібриляції"},
        {"label": "1000 мкФ @ 800 В (Тяговий інвертор)", "val": "320 Дж", "w": 380, "col": "#7b1113", "note": "Вибух, важка електротравма"}
    ]

    start_y = 65
    for i, b in enumerate(bars):
        y = start_y + i * 54
        p.append(text(25, y + 14, b["label"], size=11, color=INK, anchor="start", bold=True))
        p.append(rect(25, y + 20, 390, 16, fill="#edf2f7", stroke="#cbd5e0", sw=1.0, rx=3))
        p.append(rect(25, y + 20, b["w"], 16, fill=b["col"], stroke=b["col"], sw=1.0, rx=3))
        p.append(text(25 + b["w"] + 8, y + 33, b["val"], size=11, color=b["col"], anchor="start", bold=True))
        p.append(text(418, y + 33, b["note"], size=10, color=MUTED, anchor="end", italic=True))

    p.append(line(450, 25, 450, H - 25, color="#cbd5e0", sw=1.2, dash="4 4"))

    # Права частина: ефект діелектричної абсорбції (x: 470..795)
    p.append(text(630, 36, "Діелектрична абсорбція (Dielectric Soakage)", size=13, color=INK, bold=True))

    ox, oy = 500, 250
    gw, gh = 280, 180

    p.append(arrow(ox, oy, ox + gw + 15, oy, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox, oy - gh - 10, color=INK, sw=1.4))
    p.append(text(ox + gw + 10, oy + 18, "час t", size=11, color=INK, italic=True))
    p.append(text(ox - 8, oy - gh - 4, "Напруга V", size=11, color=INK, bold=True, italic=True, anchor="end"))

    # Графік: заряд 400В -> швидкий розряд до 0 -> відновлення напруги до 45В
    p.append(line(ox, oy - 150, ox + 60, oy - 150, color=POS, sw=2.0))
    p.append(text(ox + 30, oy - 158, "400 В", size=11, color=POS, bold=True))

    p.append(line(ox + 60, oy - 150, ox + 75, oy, color=POS, sw=2.0))
    p.append(text(ox + 75, oy + 16, "розряд", size=10, color=MUTED, italic=True))

    pts = []
    for step in range(0, 101):
        t_norm = step / 100.0
        v_rec = 45 * (1 - math.exp(-t_norm * 3.5))
        px = ox + 75 + t_norm * 190
        py = oy - v_rec
        pts.append("%.1f,%.1f" % (px, py))

    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts), "#d35400"))

    p.append(line(ox + 75, oy - 45, ox + 270, oy - 45, color="#d35400", sw=1.0, dash="3 3"))
    p.append(text(ox + 275, oy - 42, "+45 В (rebound)", size=11, color="#d35400", anchor="start", bold=True))

    tb, tbw, tbh = textbox(635, 315, "Релаксація диполів діелектрика відновлює 10–25% напруги!\nБезпечне знеструмлення вимагає постійного шунта (Bleeder).",
                           size=10, color=INK, fill="#fff8e1", stroke="#f39c12", sw=1.2, pad=6)
    p.append(tb)

    render(os.path.join(OUT, "capacitor-hazard-scale.svg"), W, H, *p,
           title="Шкала енергії конденсаторів та явище діелектричної абсорбції")


# ── 3. inductive-flyback-clamp: індуктивний викид і методи фіксації ──────────
def fig_inductive_clamp():
    W, H = 840, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=8))

    modes = [
        {
            "x": 25, "w": 250,
            "title": "1. Без захисту (Аварія)",
            "subtitle": "V = -L · (di/dt) → сотні вольт",
            "accent": POS,
            "peak_v": "Пік: 800–1500 В",
            "decay_t": "Час: наносекунди",
            "desc": "Лавинний пробій MOSFET\nабо дуга на контактах реле.\nКлюч вигорає за 1–10 сплесків."
        },
        {
            "x": 295, "w": 250,
            "title": "2. Діод вільного ходу",
            "subtitle": "Flyback Diode паралельно котушці",
            "accent": "#2980b9",
            "peak_v": "Пік: Vcc + 0.7 В",
            "decay_t": "Час: повільно (3..5 · L/R)",
            "desc": "Захищає ключ надійно,\nале затягує відпускання реле.\nКонтакти тягнуть дугу й горять."
        },
        {
            "x": 565, "w": 250,
            "title": "3. Діод + Стабілітрон / TVS",
            "subtitle": "Zener Clamp для швидкого скидання",
            "accent": FIELD,
            "peak_v": "Пік: Vcc + Vz (наприклад 36 В)",
            "decay_t": "Час: швидко (t ≈ L·I₀/Vz)",
            "desc": "Ідеальний компроміс: швидке\nгасіння магнітного поля без дуги\nй безпечна напруга для ключа."
        }
    ]

    for m in modes:
        x, y, w, h = m["x"], 30, m["w"], 300
        p.append(rect(x, y, w, h, fill="#ffffff", stroke=m["accent"], sw=1.8, rx=6))

        p.append(rect(x, y, w, 38, fill=m["accent"], stroke=m["accent"], sw=1.0, rx=0))
        p.append(text(x + w / 2, y + 24, m["title"], size=13, color="#ffffff", bold=True))
        p.append(text(x + w / 2, y + 58, m["subtitle"], size=10, color=INK, italic=True))

        # Осцилограма (внутрішнє віконце)
        ox, oy = x + 25, y + 175
        gw, gh = w - 50, 95
        p.append(rect(ox, oy - gh, gw, gh, fill="#1a202c", stroke="#4a5568", sw=1.0, rx=4))

        if m["x"] == 25:
            # Сплеск 1000В
            p.append(line(ox + 10, oy - 20, ox + 35, oy - 20, color="#48bb78", sw=1.8))
            p.append(line(ox + 35, oy - 20, ox + 42, oy - gh + 8, color=POS, sw=2.2))
            p.append(line(ox + 42, oy - gh + 8, ox + 55, oy - 20, color=POS, sw=1.8))
            p.append(line(ox + 55, oy - 20, ox + gw - 10, oy - 20, color="#48bb78", sw=1.8))
            p.append(text(ox + gw / 2, oy - gh + 22, "V_spike > 1000 В!", size=10, color=POS, bold=True))
        elif m["x"] == 295:
            # Затиснуто до Vcc+0.7, довгий спад струму
            p.append(line(ox + 10, oy - 20, ox + 35, oy - 20, color="#48bb78", sw=1.8))
            p.append(line(ox + 35, oy - 20, ox + 38, oy - 38, color="#63b3ed", sw=2.0))
            p.append(line(ox + 38, oy - 38, ox + gw - 25, oy - 38, color="#63b3ed", sw=2.0))
            p.append(line(ox + gw - 25, oy - 38, ox + gw - 10, oy - 20, color="#48bb78", sw=1.8))
            p.append(text(ox + gw / 2, oy - gh + 22, "Vcc + 0.7 В (повільно)", size=10, color="#63b3ed", bold=True))
        else:
            # Затиснуто до Vcc+Vz, швидкий спад
            p.append(line(ox + 10, oy - 20, ox + 35, oy - 20, color="#48bb78", sw=1.8))
            p.append(line(ox + 35, oy - 20, ox + 38, oy - 65, color="#68d391", sw=2.0))
            p.append(line(ox + 38, oy - 65, ox + 95, oy - 65, color="#68d391", sw=2.0))
            p.append(line(ox + 95, oy - 65, ox + 100, oy - 20, color="#68d391", sw=2.0))
            p.append(line(ox + 100, oy - 20, ox + gw - 10, oy - 20, color="#48bb78", sw=1.8))
            p.append(text(ox + gw / 2, oy - gh + 22, "Vcc + Vz (швидко)", size=10, color="#68d391", bold=True))

        p.append(text(x + 16, y + 200, m["peak_v"], size=11, color=INK, anchor="start", bold=True))
        p.append(text(x + 16, y + 218, m["decay_t"], size=11, color=m["accent"], anchor="start", bold=True))

        lines = m["desc"].split("\n")
        for idx, ln in enumerate(lines):
            p.append(text(x + 16, y + 242 + idx * 16, ln, size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "inductive-flyback-clamp.svg"), W, H, *p,
           title="Порівняння методів гасіння індуктивного викиду та швидкості спаду струму")


# ── 4. battery-thermal-runaway: ланцюгова реакція теплового розгону Li-ion ────
def fig_thermal_runaway():
    W, H = 840, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=8))

    p.append(text(W / 2, 34, "Фізика та хімія теплового розгону (Thermal Runaway) у Li-ion",
                  size=14, color=INK, bold=True))

    stages = [
        {
            "temp": "< 60 °C",
            "title": "Норма / Нагрів",
            "desc": "Робочий стан або\nструмове перевантаження (I²·R).",
            "col": FIELD,
            "bg": "#f0fff4"
        },
        {
            "temp": "80–120 °C",
            "title": "Розпад пасивації (SEI)",
            "desc": "Руйнування плівки SEI.\nЕкзотермічна реакція анода\nз органічним розчинником.",
            "col": "#d69e2e",
            "bg": "#fffaf0"
        },
        {
            "temp": "130–170 °C",
            "title": "Плавлення сепаратора",
            "desc": "ПЕ/ПП мембрана плавиться.\nМасивне внутрішнє КЗ\nміж катодом і анодом.",
            "col": "#dd6b20",
            "bg": "#fffaf0"
        },
        {
            "temp": "180–220 °C",
            "title": "Розпад катода + O₂",
            "desc": "Оксид металу виділяє кисень!\nГоріння електроліту\nне потребує зовнішнього повітря.",
            "col": POS,
            "bg": "#fff5f5"
        },
        {
            "temp": "> 600–900 °C",
            "title": "Тепловий вибух",
            "desc": "Струмінь полум'я, тиск газів,\nвикид розплавленого металу,\nланцюговий розгін батареї.",
            "col": "#742a2a",
            "bg": "#fff5f5"
        }
    ]

    card_w = 148
    gap = 12
    start_x = 26

    for i, st in enumerate(stages):
        x = start_x + i * (card_w + gap)
        y = 60
        h = 260

        p.append(rect(x, y, card_w, h, fill=st["bg"], stroke=st["col"], sw=1.8, rx=6))

        p.append(rect(x, y, card_w, 36, fill=st["col"], stroke=st["col"], sw=1.0, rx=0))
        p.append(text(x + card_w / 2, y + 23, st["temp"], size=13, color="#ffffff", bold=True))

        p.append(text(x + card_w / 2, y + 60, st["title"], size=11, color=st["col"], bold=True))

        lines = st["desc"].split("\n")
        for idx, ln in enumerate(lines):
            p.append(text(x + 10, y + 95 + idx * 20, ln, size=10, color=INK, anchor="start"))

        if i < len(stages) - 1:
            arr_x1 = x + card_w + 2
            arr_x2 = x + card_w + gap - 2
            p.append(arrow(arr_x1, y + h / 2, arr_x2, y + h / 2, color=POS, sw=2.0))

    render(os.path.join(OUT, "battery-thermal-runaway.svg"), W, H, *p,
           title="Каскадні температурні фази теплового розгону літієвого акумулятора")


# ── 5. bleeder-discharge-circuit: схемотехніка розряду та крива V(t) ─────────
def fig_bleeder_circuit():
    W, H = 840, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fdfefe", stroke=MUTED, sw=1.0, rx=8))

    # Ліва частина: схеми пасивного та активного розрядника (x: 25..420)
    p.append(text(220, 34, "Схемотехніка безпечного розряду (Bleeder)", size=13, color=INK, bold=True))

    p.append(rect(25, 55, 385, 125, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(35, 75, "Пасивний резистор (постійні втрати)", size=11, color=INK, anchor="start", bold=True))
    p.append(text(35, 96, "• Формула розряду: V(t) = V₀ · exp(-t / (R · C))", size=10, color=MUTED, anchor="start"))
    p.append(text(35, 116, "• Постійні втрати тепла під час роботи: P = V² / R", size=10, color=POS, anchor="start", bold=True))
    p.append(text(35, 136, "• Для 400 В і R=100 кОм: P_loss = 1.6 Вт постійно!", size=10, color=INK, anchor="start"))
    p.append(text(35, 156, "• Час до 50 В (безпечно): t_safe ≈ 2.1 · R · C ≈ 100 с", size=10, color=FIELD, anchor="start"))

    p.append(rect(25, 195, 385, 140, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(35, 216, "Активний розрядник (Zero Standby Loss)", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(35, 238, "• Ключ (MOSFET / Depletion / IC типу CAPZero).", size=10, color=INK, anchor="start"))
    p.append(text(35, 258, "• При наявності мережі ключ закритий: P_loss ≈ 0 мВт.", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(35, 278, "• При зникненні мережі ключ відкривається миттєво.", size=10, color=INK, anchor="start"))
    p.append(text(35, 298, "• Малий опір розряду R_act = 5–10 кОм → розряд < 1 с!", size=10, color=POS, anchor="start", bold=True))
    p.append(text(35, 318, "• Виконує вимоги IEC 62368-1 / UL 60950.", size=10, color=MUTED, anchor="start"))

    # Права частина: графік експоненційного розряду (x: 440..815)
    p.append(text(625, 34, "Крива розряду конденсатора V(t)", size=13, color=INK, bold=True))

    ox, oy = 475, 290
    gw, gh = 320, 220

    p.append(arrow(ox, oy, ox + gw + 15, oy, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox, oy - gh - 10, color=INK, sw=1.4))
    p.append(text(ox + gw + 10, oy + 18, "час t (с)", size=11, color=INK, italic=True))
    p.append(text(ox - 8, oy - gh - 4, "Напруга V", size=11, color=INK, bold=True, italic=True, anchor="end"))

    # Рівні напруги: 400 В, 50 В (безпечний поріг SELV)
    p.append(line(ox, oy - 200, ox + gw, oy - 200, color=POS, sw=1.0, dash="3 3"))
    p.append(text(ox - 6, oy - 196, "400 В", size=10, color=POS, anchor="end", bold=True))

    v_safe_y = oy - 25  # 50 В
    p.append(line(ox, v_safe_y, ox + gw, v_safe_y, color=FIELD, sw=1.2, dash="4 3"))
    p.append(text(ox + gw + 4, v_safe_y + 4, "50 В (SELV)", size=10, color=FIELD, anchor="start", bold=True))

    # Крива 1: Пасивний розряд
    pts_pass = []
    for step in range(0, 101):
        t_norm = step / 100.0
        v = 200 * math.exp(-t_norm * 2.2)
        pts_pass.append("%.1f,%.1f" % (ox + t_norm * 300, oy - v))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
             'stroke-linejoin="round"/>' % (" ".join(pts_pass), "#d35400"))
    p.append(text(ox + 160, oy - 110, "Пасивний розряд R=100 кОм", size=10, color="#d35400", bold=True))

    # Крива 2: Активний розряд
    pts_act = []
    for step in range(0, 101):
        t_norm = step / 100.0
        v = 200 * math.exp(-t_norm * 14.0)
        pts_act.append("%.1f,%.1f" % (ox + t_norm * 300, oy - v))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (" ".join(pts_act), FIELD))
    p.append(text(ox + 45, oy - 45, "Активний розряд (< 1 с)", size=10, color=FIELD, bold=True))

    p.append(circle(ox + 15, v_safe_y, 4, fill=FIELD, stroke=INK))
    p.append(text(ox + 22, v_safe_y - 10, "t_safe ≤ 1 с", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "bleeder-discharge-circuit.svg"), W, H, *p,
           title="Схеми розрядників та часові діаграми пасивного й активного знеструмлення")


def main():
    fig_three_reservoirs()
    fig_capacitor_hazard()
    fig_inductive_clamp()
    fig_thermal_runaway()
    fig_bleeder_circuit()
    print("Всі 5 фігур успішно згенеровано у ./img/")


if __name__ == "__main__":
    main()
