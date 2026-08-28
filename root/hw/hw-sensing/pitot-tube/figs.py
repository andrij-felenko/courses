# -*- coding: utf-8 -*-
"""Фігури до теми «Трубка Піто–Прандтля та вимірювання швидкості потоку».
Запуск: python figs.py   → створює SVG у ./img/
Спільні помічники та стиль — зі scripts/svgkit.py.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Анатомія трубки Піто–Прандтля: повний і статичний тиск ─────────────────
def fig_pitot_prandtl_tube():
    W, H = 840, 480
    f = [text(W / 2, 26, "Конструкція комбінованої трубки Піто–Прандтля", size=16, bold=True)]

    # Тло та межі потоку
    f.append(rect(30, 55, 780, 400, fill="#fcfdfe", stroke="#e2e8f0", sw=1.2, rx=8))

    # Лінії набігаючого потоку повітря
    flow_y = [90, 130, 170, 210, 250, 290, 330]
    for y in flow_y:
        f.append(line(45, y, 130, y, color="#94a3b8", sw=1.5, dash="4,4"))
        f.append(arrow(130, y, 175, y, color=NEG, sw=1.8))
    f.append(text(85, 75, "Набігаючий потік v", size=12.5, color=NEG, bold=True))

    # Зовнішній корпус (статична сорочка)
    # Верхня стінка
    f.append('<path d="M 220 160 C 220 130, 250 120, 280 120 L 580 120 L 580 160 L 540 160 L 540 380 L 485 380 L 485 180 L 280 180 C 255 180, 245 170, 240 160 Z" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>')
    # Нижня стінка
    f.append('<path d="M 220 240 C 220 270, 250 280, 280 280 L 580 280 L 580 240 L 540 240 L 540 220 L 485 220 L 485 380 L 440 380 L 440 220 L 280 220 C 255 220, 245 230, 240 240 Z" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>')

    # Внутрішня трубка повного тиску (центральний канал)
    # Горизонтальна секція
    f.append(rect(195, 185, 345, 30, fill="#fee2e2", stroke=POS, sw=2, rx=0))
    # Вертикальний відвід P_tot до датчика
    f.append(rect(510, 215, 30, 165, fill="#fee2e2", stroke=POS, sw=2, rx=0))

    # Статична камера (порожнина між оболонками)
    f.append(rect(280, 140, 205, 40, fill="#eff6ff", stroke=NEG, sw=1.2, rx=0))
    f.append(rect(280, 220, 160, 40, fill="#eff6ff", stroke=NEG, sw=1.2, rx=0))
    f.append(rect(440, 260, 45, 120, fill="#eff6ff", stroke=NEG, sw=1.2, rx=0))

    # Центральний отвір повного тиску (Stagnation inlet)
    f.append(circle(195, 200, 7, fill="#ffffff", stroke=POS, sw=2.5))
    f.append(arrow(135, 200, 185, 200, color=POS, sw=2.5))
    f.append(text(120, 222, "Точка гальмування (v = 0)", size=11.5, color=POS, bold=True))

    # Радіальні отвори статичного тиску на бічній поверхні
    stat_x = [370, 395, 420]
    for x in stat_x:
        # Верхні отвори
        f.append(circle(x, 120, 4, fill="#dbeafe", stroke=NEG, sw=1.8))
        f.append(line(x, 95, x, 115, color=NEG, sw=1.4, dash="2,2"))
        # Нижні отвори
        f.append(circle(x, 280, 4, fill="#dbeafe", stroke=NEG, sw=1.8))
        f.append(line(x, 305, x, 285, color=NEG, sw=1.4, dash="2,2"))

    # Дренажний отвір для видалення вологи
    f.append(circle(260, 205, 3.5, fill="#94a3b8", stroke="#334155", sw=1.5))
    f.append(line(260, 205, 260, 280, color="#64748b", sw=1.5, dash="2,2"))
    f.append(text(260, 300, "Дренаж вологи", size=10.5, color="#475569", anchor="middle"))

    # Нагрівальний елемент (Pitot Heat)
    for k in range(5):
        hx = 225 + k * 18
        f.append('<path d="M %d 130 Q %d 145 %d 130" fill="none" stroke="#ea580c" stroke-width="2.2"/>' % (hx, hx + 9, hx + 18))
        f.append('<path d="M %d 270 Q %d 255 %d 270" fill="none" stroke="#ea580c" stroke-width="2.2"/>' % (hx, hx + 9, hx + 18))
    f.append(text(270, 105, "Обігрів проти льоду (PTC / ніхром)", size=11, color="#ea580c", bold=True))

    # Диференціальний датчик тиску (MEMS)
    sensor_x, sensor_y = 660, 320
    f.append(rect(sensor_x - 70, sensor_y - 45, 140, 90, fill="#ffffff", stroke="#0f172a", sw=2, rx=6))
    f.append(text(sensor_x, sensor_y - 22, "MEMS-давач ΔP", size=12.5, bold=True))
    f.append(text(sensor_x, sensor_y - 4, "MS4525DO / DLHR", size=11, color=MUTED))
    f.append(text(sensor_x, sensor_y + 16, "ΔP = P_tot − P_stat", size=12, color=POS, bold=True))
    f.append(text(sensor_x, sensor_y + 32, "= ½ ρ v²", size=11.5, color=NEG, bold=True))

    # Гнучкі силіконові трубки до датчика
    # Повний тиск (Port 1 / High)
    f.append('<path d="M 525 380 L 525 415 L 620 415 L 620 365" fill="none" stroke="%s" stroke-width="2.5"/>' % POS)
    f.append(text(560, 432, "Канал P_tot (+)", size=11.5, color=POS, bold=True))

    # Статичний тиск (Port 2 / Low)
    f.append('<path d="M 460 380 L 460 445 L 700 445 L 700 365" fill="none" stroke="%s" stroke-width="2.5"/>' % NEG)
    f.append(text(620, 462, "Канал P_stat (−)", size=11.5, color=NEG, bold=True))

    # Пояснювальні виноски
    b1, _, _ = textbox(400, 68, "Радіальні отвори статичного тиску P_stat (перпендикулярні до потоку)", size=11.5, fill="#eff6ff", stroke=NEG)
    f.append(b1)
    b2, _, _ = textbox(690, 150, "Повний тиск:\nP_tot = P_stat + P_dyn", size=11.5, fill="#fef2f2", stroke=POS)
    f.append(b2)

    render(os.path.join(IMG, "pitot-prandtl-tube.svg"), W, H, *f)


# ── 2. Фізика гальмування потоку: закон Бернуллі ───────────────────────────────
def fig_bernoulli_stagnation():
    W, H = 820, 440
    f = [text(W / 2, 26, "Гальмування потоку та розподіл тиску біля трубки Піто", size=16, bold=True)]

    f.append(rect(30, 50, 760, 365, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))

    # Тіло трубки (напівсферичний ніс)
    f.append('<path d="M 460 140 L 320 140 C 270 140, 240 170, 240 210 C 240 250, 270 280, 320 280 L 460 280 Z" fill="#e2e8f0" stroke="#334155" stroke-width="2.4"/>')
    # Центральний отвір
    f.append(rect(240, 198, 90, 24, fill="#ffffff", stroke=POS, sw=2, rx=0))

    # Лінії течії (Streamlines)
    # 1. Центральна лінія, яка впирається в точку гальмування
    f.append(line(60, 210, 235, 210, color=POS, sw=2.4))
    f.append(arrow(140, 210, 195, 210, color=POS, sw=2.4))
    f.append(circle(240, 210, 4.5, fill=POS, stroke="#ffffff", sw=1.5))

    # 2. Верхні обтічні лінії течії
    f.append('<path d="M 60 170 C 180 170, 210 135, 260 120 C 310 105, 380 115, 460 115" fill="none" stroke="#3b82f6" stroke-width="2"/>')
    f.append('<path d="M 60 130 C 180 130, 220 95, 290 85 C 360 75, 410 85, 460 85" fill="none" stroke="#60a5fa" stroke-width="1.6"/>')

    # 3. Нижні обтічні лінії течії
    f.append('<path d="M 60 250 C 180 250, 210 285, 260 300 C 310 315, 380 305, 460 305" fill="none" stroke="#3b82f6" stroke-width="2"/>')
    f.append('<path d="M 60 290 C 180 290, 220 325, 290 335 C 360 345, 410 335, 460 335" fill="none" stroke="#60a5fa" stroke-width="1.6"/>')

    # Підписи зон на лініях
    f.append(text(140, 192, "Швидкість падає: v → 0", size=11.5, color=POS, bold=True))
    f.append(text(330, 95, "Розгін над плечем: v > v_∞", size=11, color="#2563eb", bold=True))

    # Статичні отвори на відстані від носа
    f.append(circle(410, 140, 4, fill="#2563eb", stroke="#1d4ed8", sw=1.6))
    f.append(circle(410, 280, 4, fill="#2563eb", stroke="#1d4ed8", sw=1.6))
    f.append(line(410, 115, 410, 140, color=NEG, sw=1.4, dash="2,2"))
    f.append(text(410, 70, "Отвори P_stat", size=11.5, color=NEG, bold=True))
    f.append(text(410, 83, "(l ≈ 3..6 діаметрів D)", size=10, color=MUTED))

    # Права панель: графік розподілу тиску вздовж стінки
    gx, gy, gw, gh = 520, 100, 240, 200
    f.append(rect(gx, gy, gw, gh, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(line(gx + 30, gy + gh - 25, gx + gw - 15, gy + gh - 25, color="#475569", sw=1.5)) # вісь X (відстань x/D)
    f.append(line(gx + 30, gy + gh - 25, gx + 30, gy + 20, color="#475569", sw=1.5))          # вісь Y (коефіцієнт тиску Cp)
    f.append(text(gx + gw - 15, gy + gh - 10, "x / D", size=11, color="#475569", anchor="end"))
    f.append(text(gx + 20, gy + 18, "C_p", size=12, color="#475569", bold=True, anchor="middle"))

    # Лінія базового статичного тиску Cp = 0
    f.append(line(gx + 30, gy + 105, gx + gw - 15, gy + 105, color="#64748b", sw=1.2, dash="3,3"))
    f.append(text(gx + gw - 10, gy + 100, "C_p = 0 (P_stat = P_∞)", size=9.5, color="#64748b", anchor="end"))

    # Крива коефіцієнта тиску Cp від носа до циліндричної частини
    # ніс: Cp = +1 (P_tot), плече: Cp < 0 (розрідження), стабілізація: Cp -> 0
    cp_curve = [
        (gx + 30, gy + 35),   # x=0: Cp = +1
        (gx + 55, gy + 70),
        (gx + 80, gy + 145),  # розрідження над скругленням
        (gx + 120, gy + 130),
        (gx + 160, gy + 110),
        (gx + 200, gy + 105), # x ≈ 5D: Cp = 0
        (gx + 225, gy + 105)
    ]
    pts = " ".join("%.1f,%.1f" % pt for pt in cp_curve)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (pts, POS))

    f.append(circle(gx + 30, gy + 35, 4, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(gx + 40, gy + 32, "C_p = +1 (P_tot)", size=10.5, color=POS, bold=True, anchor="start"))

    f.append(circle(gx + 200, gy + 105, 4, fill=NEG, stroke="#ffffff", sw=1.5))
    f.append(text(gx + 195, gy + 135, "Оптимальне місце\nстатичних отворів", size=10, color=NEG, bold=True, anchor="middle"))

    # Нижня плашка з рівнянням Бернуллі
    b_eq, _, _ = textbox(W / 2, 385,
                         "Рівняння Бернуллі: P_tot = P_stat + ½ ρ v²  ==>  v = √ ( 2 · (P_tot − P_stat) / ρ )",
                         size=13, fill="#fef3c7", stroke="#d97706", bold=True)
    f.append(b_eq)

    render(os.path.join(IMG, "bernoulli-stagnation.svg"), W, H, *f)


# ── 3. Каскад швидкостей: від сирого тиску до TAS ─────────────────────────────
def fig_airspeed_pipeline():
    W, H = 840, 460
    f = [text(W / 2, 26, "Каскад обчислення повітряних швидкостей (IAS → CAS → EAS → TAS)", size=16, bold=True)]

    f.append(rect(30, 52, 780, 385, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))

    # 4 основні блоки конвеєра
    # Блок 1: Сирий тиск -> IAS
    f.append(rect(50, 80, 160, 220, fill="#ffffff", stroke="#0284c7", sw=1.8, rx=6))
    f.append(text(130, 105, "1. Приладова (IAS)", size=13, color="#0284c7", bold=True))
    f.append(text(130, 125, "Indicated Airspeed", size=10.5, color=MUTED))
    f.append(line(65, 138, 195, 138, color="#e2e8f0", sw=1.2))
    f.append(text(130, 160, "Давач: ΔP = P_tot − P_stat", size=10.5, color=INK))
    f.append(text(130, 180, "ρ₀ = 1.225 кг/м³ (МСА)", size=10.5, color=MUTED))
    f.append(rect(65, 200, 130, 42, fill="#f0f9ff", stroke="#0284c7", sw=1.2, rx=4))
    f.append(text(130, 225, "v_ias = √(2·ΔP / ρ₀)", size=11, color="#0284c7", bold=True))
    f.append(text(130, 265, "Визначає звалювання\nта підйомну силу крила", size=10, color="#0369a1"))

    f.append(arrow(215, 190, 245, 190, color="#475569", sw=2))

    # Блок 2: Калібрована CAS
    f.append(rect(248, 80, 160, 220, fill="#ffffff", stroke="#2563eb", sw=1.8, rx=6))
    f.append(text(328, 105, "2. Калібрована (CAS)", size=13, color="#2563eb", bold=True))
    f.append(text(328, 125, "Calibrated Airspeed", size=10.5, color=MUTED))
    f.append(line(263, 138, 393, 138, color="#e2e8f0", sw=1.2))
    f.append(text(328, 160, "Поправки трубки:", size=10.5, color=INK))
    f.append(text(328, 180, "• Похибка монтажу (α, β)", size=10, color=MUTED))
    f.append(text(328, 195, "• Аеродинаміка фюзеляжу", size=10, color=MUTED))
    f.append(rect(263, 215, 130, 42, fill="#eff6ff", stroke="#2563eb", sw=1.2, rx=4))
    f.append(text(328, 240, "CAS = IAS + ΔV_pos", size=11, color="#2563eb", bold=True))
    f.append(text(328, 278, "Таблиця / поліном\nпродувки в трубі", size=10, color="#1d4ed8"))

    f.append(arrow(413, 190, 443, 190, color="#475569", sw=2))

    # Блок 3: Еквівалентна EAS
    f.append(rect(446, 80, 160, 220, fill="#ffffff", stroke="#7c3aed", sw=1.8, rx=6))
    f.append(text(526, 105, "3. Еквівалентна (EAS)", size=13, color="#7c3aed", bold=True))
    f.append(text(526, 125, "Equivalent Airspeed", size=10.5, color=MUTED))
    f.append(line(461, 138, 591, 138, color="#e2e8f0", sw=1.2))
    f.append(text(526, 160, "Стисливість повітря:", size=10.5, color=INK))
    f.append(text(526, 180, "Важлива при M > 0.3", size=10.5, color=MUTED))
    f.append(rect(461, 200, 130, 42, fill="#f5f3ff", stroke="#7c3aed", sw=1.2, rx=4))
    f.append(text(526, 225, "EAS = CAS · f_comp(M)", size=11, color="#7c3aed", bold=True))
    f.append(text(526, 265, "Враховує хвилю тиску\nстисливого газу", size=10, color="#6d28d9"))

    f.append(arrow(611, 190, 641, 190, color="#475569", sw=2))

    # Блок 4: Істинна TAS
    f.append(rect(644, 80, 160, 220, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    f.append(text(724, 105, "4. Істинна (TAS)", size=13, color=POS, bold=True))
    f.append(text(724, 125, "True Airspeed", size=10.5, color=MUTED))
    f.append(line(659, 138, 789, 138, color="#e2e8f0", sw=1.2))
    f.append(text(724, 160, "Густина на висоті ρ(P,T):", size=10.5, color=INK))
    f.append(text(724, 180, "P_stat (барометр), T (OAT)", size=10, color=MUTED))
    f.append(rect(659, 200, 130, 42, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    f.append(text(724, 225, "TAS = EAS · √(ρ₀ / ρ)", size=11, color=POS, bold=True))
    f.append(text(724, 265, "Справжня швидкість\nвідносно маси повітря", size=10, color="#991b1b"))

    # Нижня частина: навігаційний синтез із вітром (Ground Speed)
    f.append(rect(50, 320, 754, 95, fill="#ffffff", stroke="#0f172a", sw=1.6, rx=6))
    f.append(text(150, 348, "Навігаційний векторний трикутник:", size=12.5, bold=True))
    f.append(text(150, 372, "Вектор шляхової швидкості (Ground Speed):", size=11.5, color=MUTED))
    f.append(text(150, 395, "V_ground = V_tas + V_wind", size=13, color=FIELD, bold=True))

    # Схема трикутника швидкостей праворуч
    tx, ty = 480, 370
    f.append(arrow(tx, ty, tx + 120, ty - 25, color=POS, sw=2.2))
    f.append(text(tx + 55, ty - 22, "V_tas (курс)", size=11, color=POS, bold=True))

    f.append(arrow(tx + 120, ty - 25, tx + 180, ty + 15, color="#0284c7", sw=2.2))
    f.append(text(tx + 175, ty - 5, "V_wind", size=11, color="#0284c7", bold=True))

    f.append(arrow(tx, ty, tx + 180, ty + 15, color=FIELD, sw=2.5))
    f.append(text(tx + 95, ty + 30, "V_ground (GNSS трек)", size=11.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "ias-cas-tas-pipeline.svg"), W, H, *f)


# ── 4. Відмови трубки Піто: обмерзання, дренаж і поведінка висотоміра ──────────
def fig_pitot_failures_icing():
    W, H = 840, 440
    f = [text(W / 2, 26, "Діагностика відмов та сценарії закупорювання трубки Піто", size=16, bold=True)]

    f.append(rect(30, 52, 780, 365, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=8))

    # 3 сценарії закупорювання
    box_w, box_h = 240, 320
    scenarios = [
        (50, "Сценарій 1: Забитий ніс, дренаж ВІДКРИТИЙ", [
            ("Причина:", "Лід / комаха вхідного отвору P_tot"),
            ("Фізика:", "Повітря стікає через дренаж"),
            ("Тиск:", "P_вхід стравлюється до P_stat"),
            ("ΔP давача:", "ΔP → 0 Па"),
            ("Показ швидкості:", "IAS стрімко падає до 0"),
            ("Небезпека:", "Автопілот дає повний газ,\nрозганяючи літак до руйнування")
        ], "#fee2e2", POS),
        (300, "Сценарій 2: Забитий ніс І дренаж (Пастка)", [
            ("Причина:", "Повне обмерзання / замерзла вода"),
            ("Фізика:", "Тиск P_tot замкнений у трубці"),
            ("У наборі висоти:", "P_stat падає, а P_tot лишається"),
            ("ΔP давача:", "ΔP = P_tot(замк) − P_stat(h) ↑ РОСТЕ"),
            ("Показ швидкості:", "IAS зростає при наборі висоти!"),
            ("Небезпека:", "Трубка стає фальшивим\nвисотоміром; пілот задирає ніс")
        ], "#fef3c7", "#d97706"),
        (550, "Сценарій 3: Забиті СТАТИЧНІ отвори", [
            ("Причина:", "Лід на бортах / заклеєні порти"),
            ("Фізика:", "P_stat замкнений на рівні землі"),
            ("У наборі висоти:", "P_stat(замк) > P_stat(реальний)"),
            ("ΔP давача:", "ΔP занижується при наборі"),
            ("Показ швидкості:", "IAS показує менше за реальну"),
            ("У зниженні:", "IAS завищується (небезпека\nперевищення V_ne)")
        ], "#eff6ff", NEG)
    ]

    for bx, title, rows, bg_col, border_col in scenarios:
        f.append(rect(bx, 75, box_w, box_h, fill=bg_col, stroke=border_col, sw=1.8, rx=6))
        # Заголовок сценарію
        f.append(rect(bx, 75, box_w, 42, fill="#ffffff", stroke=border_col, sw=1.4, rx=6))
        f.append(mtext(bx + box_w / 2, 92, title.replace(": ", ":\n"), size=11, color=border_col, bold=True))

        ry = 135
        for label, val in rows:
            f.append(text(bx + 12, ry, label, size=10.5, color="#475569", anchor="start", bold=True))
            if "\n" in val:
                lines = val.split("\n")
                f.append(text(bx + 12, ry + 15, lines[0], size=10.5, color=INK, anchor="start"))
                f.append(text(bx + 12, ry + 29, lines[1], size=10.5, color=POS if border_col == POS else INK, anchor="start", bold=True))
                ry += 42
            else:
                f.append(text(bx + 12, ry + 15, val, size=10.5, color=INK, anchor="start"))
                ry += 30

    render(os.path.join(IMG, "pitot-failures-icing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pitot_prandtl_tube()
    fig_bernoulli_stagnation()
    fig_airspeed_pipeline()
    fig_pitot_failures_icing()
    print("All 4 Pitot figures generated successfully in ./img/")
