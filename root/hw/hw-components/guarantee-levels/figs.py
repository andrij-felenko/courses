# -*- coding: utf-8 -*-
"""Фігури до теми «Рівні гарантій параметрів: tested, sampled, design».
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5).
Усі підписи в SVG — без номерів і без «Рис.».
Запуск: python figs.py -> пише в ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_four_levels_pyramid():
    """Метрологічна ієрархія 4 рівнів гарантій: охоплення, собівартість та ризик."""
    W, H = 760, 420
    f = []
    f.append(text(W / 2, 28, "Чотири рівні гарантії параметрів у даташитах", size=16, bold=True))

    # Сходинки/шари піраміди
    # Рівень 1: 100% Tested
    f.append(rect(60, 60, 640, 65, fill="#eaf7ee", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(200, 86, "1. 100% Production Tested (Суцільний контроль)", size=14, color="#1e7e45", bold=True))
    f.append(text(200, 108, "Фізичний замір кожного чіпа на ATE-тестері при 25 °C", size=12, color=INK))
    f.append(rect(500, 72, 185, 42, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(592, 88, "Охоплення: 100%", size=11, color="#1e7e45", bold=True))
    f.append(text(592, 104, "Ризик споживача: нульовий", size=11, color=MUTED))

    # Рівень 2: Sample Tested
    f.append(rect(60, 135, 640, 65, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(200, 161, "2. Sample Tested / AQL (Вибірковий контроль)", size=14, color=NEG, bold=True))
    f.append(text(200, 183, "Статистична вибірка (MIL-STD-105E / ANSI Z1.4, напр. 1:100)", size=12, color=INK))
    f.append(rect(500, 147, 185, 42, fill="#ffffff", stroke=NEG, sw=1.2, rx=4))
    f.append(text(592, 163, "Охоплення: 0.1–1%", size=11, color=NEG, bold=True))
    f.append(text(592, 179, "Руйнівні / довгі тести", size=11, color=MUTED))

    # Рівень 3: Guaranteed by Characterization
    f.append(rect(60, 210, 640, 65, fill="#fff8e1", stroke="#d4a017", sw=1.8, rx=6))
    f.append(text(200, 236, "3. Guaranteed by Characterization (Кваліфікація)", size=14, color="#b37400", bold=True))
    f.append(text(200, 258, "Підтверджено на кваліфікаційних партіях за 6-Sigma (Cp/Cpk)", size=12, color=INK))
    f.append(rect(500, 222, 185, 42, fill="#ffffff", stroke="#d4a017", sw=1.2, rx=4))
    f.append(text(592, 238, "Охоплення в партії: 0%", size=11, color="#b37400", bold=True))
    f.append(text(592, 254, "Гарантія меж: -40..+125 °C", size=11, color=MUTED))

    # Рівень 4: Guaranteed by Design
    f.append(rect(60, 285, 640, 65, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    f.append(text(200, 311, "4. Guaranteed by Design (Гарантовано топологією)", size=14, color=POS, bold=True))
    f.append(text(200, 333, "Симуляція Monte Carlo, симетрія кристала, не вимірюється на ATE", size=12, color=INK))
    f.append(rect(500, 297, 185, 42, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    f.append(text(592, 313, "Охоплення: 0%", size=11, color=POS, bold=True))
    f.append(text(592, 329, "Ризик при зміні ревізії чіпа", size=11, color=MUTED))

    # Стрілка знизу вгору: витрати на тестування
    f.append(rect(60, 365, 310, 38, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    f.append(text(215, 388, "Витрати фабрики на тест: від $0 до максимуму", size=12, color=INK, bold=True))

    f.append(rect(390, 365, 310, 38, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    f.append(text(545, 388, "Ризик відхилення параметра: зростає донизу", size=12, color=POS, bold=True))

    return render(os.path.join(OUT, "four-levels-pyramid.svg"), W, H, *f)


def fig_ate_test_flow():
    """Технологічний маршрут тестування мікросхем на фабриці."""
    W, H = 760, 320
    f = []
    f.append(text(W / 2, 26, "Маршрут фабричного тестування: де знімаються гарантії", size=16, bold=True))

    # Блок 1: Кремнієва пластина
    f.append(rect(30, 65, 150, 95, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(105, 92, "1. Wafer Probe", size=13, bold=True))
    f.append(text(105, 114, "Сортування на пластині", size=11, color=MUTED))
    f.append(text(105, 132, "Голчастий контакт при 25 °C", size=10, color=INK))
    f.append(text(105, 148, "Відсікання грубого браку", size=10, color="#1e7e45"))

    # Стрілка 1 -> 2
    f.append(arrow(180, 112, 215, 112, color=LINE, sw=1.8))

    # Блок 2: Корпусування
    f.append(rect(220, 65, 140, 95, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    f.append(text(290, 92, "2. Assembly", size=13, bold=True))
    f.append(text(290, 114, "Різка пластини та", size=11, color=MUTED))
    f.append(text(290, 132, "монтаж у корпус", size=11, color=MUTED))
    f.append(text(290, 148, "Термомеханічний стрес", size=10, color=POS))

    # Стрілка 2 -> 3
    f.append(arrow(360, 112, 395, 112, color=LINE, sw=1.8))

    # Блок 3: Final Package Test
    f.append(rect(400, 65, 160, 95, fill="#eaf7ee", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(480, 90, "3. Final Test (ATE)", size=13, color="#1e7e45", bold=True))
    f.append(text(480, 110, "100% тест при +25 °C", size=11, color="#1e7e45", bold=True))
    f.append(text(480, 130, "Iq, Vref, зміщення, скан", size=10, color=INK))
    f.append(text(480, 148, "Guardbanding меж Min/Max", size=10, color=MUTED))

    # Стрілка 3 -> 4
    f.append(arrow(560, 112, 595, 112, color=LINE, sw=1.8))

    # Блок 4: Sample QA
    f.append(rect(600, 65, 130, 95, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    f.append(text(665, 92, "4. Sample QA", size=13, color=NEG, bold=True))
    f.append(text(665, 114, "Вибірка AQL", size=11, color=MUTED))
    f.append(text(665, 132, "Тест гаряче/холодно", size=10, color=INK))
    f.append(text(665, 148, "Перевірка 6-Sigma", size=10, color=MUTED))

    # Нижні пояснення
    f.append(rect(30, 185, 345, 105, fill="#ffffff", stroke="#d4a017", sw=1.5, rx=6))
    f.append(text(202, 210, "Параметри 100% Tested:", size=13, color="#b37400", bold=True))
    f.append(text(202, 232, "Вимірюються фізично на етапі 3 для КОЖНОГО чіпа.", size=11, color=INK))
    f.append(text(202, 252, "Займають мілісекунди на швидкісному ATE-тестері.", size=11, color=INK))
    f.append(text(202, 272, "Похибка тестера компенсується захисною смугою.", size=11, color=MUTED))

    f.append(rect(385, 185, 345, 105, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    f.append(text(557, 210, "Параметри Characterized / Design:", size=13, color=POS, bold=True))
    f.append(text(557, 232, "На етапі 3 НЕ ВИМІРЮЮТЬСЯ для масових партій.", size=11, color=INK))
    f.append(text(557, 252, "Поведінка при -40 °C..+125 °C гарантована статистикою,", size=11, color=INK))
    f.append(text(557, 272, "знятою під час попередньої кваліфікації кремнію.", size=11, color=MUTED))

    return render(os.path.join(OUT, "ate-test-flow.svg"), W, H, *f)


def fig_six_sigma_cpk_bounds():
    """Гаусовий розподіл параметра, межі специфікації та індекс Cpk."""
    W, H = 760, 360
    f = []
    f.append(text(W / 2, 28, "Статистичні межі Six Sigma: зв'язок розкиду кристалів і меж даташита", size=16, bold=True))

    # Вісь X
    f.append(line(80, 250, 680, 250, color=LINE, sw=1.5))
    f.append(text(675, 270, "Значення параметра", size=12, anchor="end", color=INK))

    # Гаусіана (полілінія)
    pts = [
        (120, 248), (160, 246), (200, 240), (240, 226), (280, 195),
        (320, 145), (350, 95), (380, 65), (410, 95), (440, 145),
        (480, 195), (520, 226), (560, 240), (600, 246), (640, 248)
    ]
    path_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    f.append(f'<path d="{path_d}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Центр: Середнє значення (mu)
    f.append(line(380, 65, 380, 250, color=NEG, sw=1.5, dash="4,3"))
    f.append(text(380, 268, "Середнє (μ)", size=12, color=NEG, bold=True))

    # Межі сигм: -3s, +3s, -6s, +6s
    f.append(line(260, 180, 260, 250, color=MUTED, sw=1.0, dash="2,2"))
    f.append(line(500, 180, 500, 250, color=MUTED, sw=1.0, dash="2,2"))
    f.append(text(260, 268, "−3σ", size=11, color=MUTED))
    f.append(text(500, 268, "+3σ", size=11, color=MUTED))

    # Межі даташита: LSL (Min) та USL (Max)
    f.append(line(140, 45, 140, 250, color=POS, sw=2.0))
    f.append(line(620, 45, 620, 250, color=POS, sw=2.0))
    f.append(text(140, 38, "LSL (Datasheet Min)", size=12, color=POS, bold=True))
    f.append(text(620, 38, "USL (Datasheet Max)", size=12, color=POS, bold=True))

    # Стрілка діапазону 6-Sigma
    f.append(line(140, 110, 620, 110, color=FIELD, sw=1.5))
    f.append(circle(140, 110, 3, fill=FIELD, stroke=FIELD))
    f.append(circle(620, 110, 3, fill=FIELD, stroke=FIELD))
    f.append(text(380, 104, "Ширина допуску = 12·σ (Cpk ≥ 2.0)", size=12, color="#1e7e45", bold=True))

    # Пояснення знизу
    f.append(rect(80, 290, 600, 55, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(380, 312, "Guaranteed by Characterization: межі Min/Max ставляться на відстані 6·σ від центру.", size=12, bold=True))
    f.append(text(380, 332, "Ймовірність виходу чіпа за ці рамки становить менше 3.4 дефектів на мільйон (3.4 DPM).", size=11, color=MUTED))

    return render(os.path.join(OUT, "six-sigma-cpk-bounds.svg"), W, H, *f)


def fig_pat_outlier_rejection():
    """Динамічний контроль Part Average Testing (AEC-Q001) для відсікання аномалій."""
    W, H = 760, 340
    f = []
    f.append(text(W / 2, 28, "Part Average Testing (AEC-Q001): динамічне відсікання аномалій", size=16, bold=True))

    # Загальна вісь параметрів
    f.append(line(60, 190, 700, 190, color=LINE, sw=1.5))

    # Межі даташита (Datasheet Limits)
    f.append(line(100, 55, 100, 200, color=POS, sw=2.0))
    f.append(line(660, 55, 660, 200, color=POS, sw=2.0))
    f.append(text(100, 48, "Datasheet Min (LSL)", size=12, color=POS, bold=True))
    f.append(text(660, 48, "Datasheet Max (USL)", size=12, color=POS, bold=True))

    # Локальний розподіл поточної партії пластин (вузька гаусіана)
    pts_pat = [
        (260, 188), (290, 185), (320, 170), (350, 130), (380, 80),
        (410, 130), (440, 170), (470, 185), (500, 188)
    ]
    path_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_pat)
    f.append(f'<path d="{path_d}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Межі PAT (Part Average Testing limits)
    f.append(line(270, 75, 270, 200, color=FIELD, sw=1.8, dash="4,3"))
    f.append(line(490, 75, 490, 200, color=FIELD, sw=1.8, dash="4,3"))
    f.append(text(270, 68, "PAT Min (μ − 3·σ_p)", size=11, color="#1e7e45", bold=True))
    f.append(text(490, 68, "PAT Max (μ + 3·σ_p)", size=11, color="#1e7e45", bold=True))

    # Чіп-викид (Outlier) у зоні між PAT Max та Datasheet Max
    f.append(circle(580, 188, 7, fill="#fdecea", stroke=POS, sw=2.0))
    f.append(text(580, 160, "Кристал-аномалія (Outlier)", size=11, color=POS, bold=True))
    f.append(arrow(580, 166, 580, 178, color=POS, sw=1.5))

    # Підписи зон
    f.append(rect(300, 215, 160, 36, fill="#eaf7ee", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(380, 237, "Придатні чіпи партії (PASS)", size=11, color="#1e7e45", bold=True))

    f.append(rect(515, 215, 180, 48, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    f.append(text(605, 233, "БРАК за PAT (REJECT)", size=11, color=POS, bold=True))
    f.append(text(605, 251, "Формально в межах даташита!", size=10, color=MUTED))

    # Нижній висновок
    f.append(rect(60, 275, 640, 50, fill="#fff8e1", stroke="#d4a017", sw=1.5, rx=6))
    f.append(text(380, 296, "Стандарт AEC-Q001 вимагає відсікати чіпи з аномальними значеннями відносно своєї партії,", size=12, bold=True))
    f.append(text(380, 314, "навіть якщо вони повністю вкладаються в паспортні рамки даташита (ризик ранньої відмови).", size=11, color=MUTED))

    return render(os.path.join(OUT, "pat-outlier-rejection.svg"), W, H, *f)


def fig_datasheet_notes_anatomy():
    """Анатомія таблиці Electrical Characteristics зі стовпчиком Test Level та виносками."""
    W, H = 760, 350
    f = []
    f.append(text(W / 2, 26, "Анатомія таблиці даташита: колонки гарантій та виноски", size=16, bold=True))

    # Шапка таблиці
    f.append(rect(40, 55, 200, 30, fill="#eef1f4", stroke=LINE, sw=1.2, rx=0))
    f.append(text(140, 75, "Parameter", size=12, bold=True))

    f.append(rect(240, 55, 80, 30, fill="#eef1f4", stroke=LINE, sw=1.2, rx=0))
    f.append(text(280, 75, "Min", size=12, bold=True))

    f.append(rect(320, 55, 80, 30, fill="#eef1f4", stroke=LINE, sw=1.2, rx=0))
    f.append(text(360, 75, "Typ", size=12, bold=True))

    f.append(rect(400, 55, 80, 30, fill="#eef1f4", stroke=LINE, sw=1.2, rx=0))
    f.append(text(440, 75, "Max", size=12, bold=True))

    f.append(rect(480, 55, 90, 30, fill="#eef1f4", stroke=LINE, sw=1.2, rx=0))
    f.append(text(525, 75, "Test Level", size=12, color=NEG, bold=True))

    f.append(rect(570, 55, 150, 30, fill="#eef1f4", stroke=LINE, sw=1.2, rx=0))
    f.append(text(645, 75, "Conditions", size=12, bold=True))

    # Рядок 1: Offset Voltage (100% Tested)
    f.append(rect(40, 85, 200, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(140, 106, "Input Offset Voltage (Vos)", size=11, color=INK))

    f.append(rect(240, 85, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(280, 106, "-5", size=11, color=INK))

    f.append(rect(320, 85, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(360, 106, "±1", size=11, color=MUTED))

    f.append(rect(400, 85, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(440, 106, "+5", size=11, color=INK))

    f.append(rect(480, 85, 90, 32, fill="#eaf7ee", stroke=FIELD, sw=1.2, rx=0))
    f.append(text(525, 106, "I (100%)", size=11, color="#1e7e45", bold=True))

    f.append(rect(570, 85, 150, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(645, 106, "TA = +25 °C", size=11, color=INK))

    # Рядок 2: Drift over temp (Characterized)
    f.append(rect(40, 117, 200, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(140, 138, "Offset Drift vs Temp (1)", size=11, color=INK))

    f.append(rect(240, 117, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(280, 138, "—", size=11, color=MUTED))

    f.append(rect(320, 117, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(360, 138, "0.05", size=11, color=MUTED))

    f.append(rect(400, 117, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(440, 138, "0.2", size=11, color=INK))

    f.append(rect(480, 117, 90, 32, fill="#fff8e1", stroke="#d4a017", sw=1.2, rx=0))
    f.append(text(525, 138, "II (Char)", size=11, color="#b37400", bold=True))

    f.append(rect(570, 117, 150, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(645, 138, "-40 °C ≤ TA ≤ +125 °C", size=10, color=INK))

    # Рядок 3: Slew Rate (Guaranteed by design)
    f.append(rect(40, 149, 200, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(140, 170, "Slew Rate (SR) (2)", size=11, color=INK))

    f.append(rect(240, 149, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(280, 170, "8", size=11, color=INK))

    f.append(rect(320, 149, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(360, 170, "12", size=11, color=MUTED))

    f.append(rect(400, 149, 80, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(440, 170, "—", size=11, color=MUTED))

    f.append(rect(480, 149, 90, 32, fill="#fdecea", stroke=POS, sw=1.2, rx=0))
    f.append(text(525, 170, "IV (Design)", size=11, color=POS, bold=True))

    f.append(rect(570, 149, 150, 32, fill="#ffffff", stroke=LINE, sw=1.0, rx=0))
    f.append(text(645, 170, "CL = 50 pF, G = +1", size=10, color=INK))

    # Виноски під таблицею
    f.append(rect(40, 195, 680, 135, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(60, 218, "Розшифровка виносок даташита:", size=12, bold=True, anchor="start"))
    f.append(text(60, 240, "• Level I: 100% production tested at +25 °C. Гарантовані межі Min/Max для кожного екземпляра.", size=11, anchor="start", color=INK))
    f.append(text(60, 262, "• Note 1 (Level II): Guaranteed by characterization over full temperature range; not tested in production.", size=11, anchor="start", color="#b37400"))
    f.append(text(60, 284, "• Note 2 (Level IV): Parameter is guaranteed by design and SPICE simulation; physically not measured on ATE.", size=11, anchor="start", color=POS))
    f.append(text(60, 306, "• Колонка Typ: типове значення для модальної партії; НЕ є гарантією виробника і не має юридичної сили.", size=11, anchor="start", color=MUTED))

    return render(os.path.join(OUT, "datasheet-notes-anatomy.svg"), W, H, *f)


def main():
    fig_four_levels_pyramid()
    fig_ate_test_flow()
    fig_six_sigma_cpk_bounds()
    fig_pat_outlier_rejection()
    fig_datasheet_notes_anatomy()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
