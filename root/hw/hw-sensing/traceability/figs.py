# -*- coding: utf-8 -*-
"""Фігури до теми «Простежуваність і повірка за еталоном».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Ланцюг метрологічної простежуваності ──
def fig_traceability_chain():
    W, H = 880, 470
    f = [
        text(W / 2, 28, "Ланцюг метрологічної простежуваності (Traceability Chain)", size=16, bold=True),
        text(W / 2, 48, "від фундаментальних квантових констант SI до робочих цехових приладів",
             size=11, color=MUTED, italic=True)
    ]

    # Рівні піраміди зверху вниз
    levels = [
        ("Визначення SI та квантові еталони", "Константи h, e, c, Δν_Cs • ефект Джозефсона (KJ), квантовий холлівський опір (RK)", "u ~ 10⁻⁸–10⁻¹⁰", POS),
        ("Національні метрологічні інститути (NMI)", "BIPM, NIST, PTB, Укрметртестстандарт • первинні лабораторні квантові системи", "u ~ 10⁻⁷–10⁻⁸", "#d35400"),
        ("Акредитовані калібрувальні лабораторії (ISO/IEC 17025)", "Опорні міри напруги (Fluke 732B/C, LTZ1000), прецизійні міри опору (Thomas 1 Ω)", "u ~ 10⁻⁶ (ppm)", "#2980b9"),
        ("Робочі еталони та цехові калібратори", "Прецизійні мультиметри 8.5 розрядів (3458A), калібратори (Fluke 5730A)", "u ~ 10–50 ppm", FIELD),
        ("Робочі вимірювальні прилади та кінцеві давачі", "Промислові давачі (4–20 мА, I2C/SPI), щитові вольтметри, вбудовані АЦП", "u ~ 0.1%–1%", INK)
    ]

    box_w = 610
    start_y = 75
    row_h = 66
    gap_y = 10

    for i, (title, desc, unc, col) in enumerate(levels):
        y = start_y + i * (row_h + gap_y)
        f.append(rect(140, y, box_w, row_h, fill=FILL, stroke=col, sw=2, rx=6))
        f.append(text(155, y + 22, title, size=12.5, color=col, bold=True, anchor="start"))
        f.append(text(155, y + 42, desc, size=10, color=INK, anchor="start"))
        f.append(rect(625, y + 10, 115, 24, fill="#ffffff", stroke=col, sw=1.2, rx=4))
        f.append(text(682, y + 26, unc, size=10.5, color=col, bold=True, anchor="middle"))

        if i < len(levels) - 1:
            arrow_y1 = y + row_h
            arrow_y2 = arrow_y1 + gap_y
            f.append(arrow(445, arrow_y1, 445, arrow_y2, color=LINE, sw=1.6))

    # Ліва вертикальна стрілка: калібрування стікає вниз
    f.append(arrow(75, 80, 75, 435, color=FIELD, sw=2.2))
    f.append(text(75, 455, "Калібрування ↓", size=11, color=FIELD, bold=True))
    f.append(text(75, 70, "Передача міри", size=10, color=FIELD, bold=True))

    # Права вертикальна стрілка: невизначеність зростає вниз / накопичується
    f.append(arrow(805, 435, 805, 80, color=POS, sw=2.2))
    f.append(text(805, 455, "Невизначеність", size=10, color=POS, bold=True))
    f.append(text(805, 70, "U зростає ↑", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "traceability-chain.svg"), W, H, *f)


# ── Фігура 2: Калібрування проти повірки ──
def fig_cal_vs_verif():
    W, H = 860, 360
    f = [
        text(W / 2, 28, "Калібрування проти повірки: вимірювання проти оцінки відповідності", size=16, bold=True),
        text(W / 2, 48, "калібрування знаходить функцію й невизначеність; повірка виносить юридичний вердикт допуску",
             size=11, color=MUTED, italic=True),
        line(W / 2, 70, W / 2, 335, color="#dcdcdc", sw=1.5, dash="4,4")
    ]

    # Лівий блок: Калібрування
    cx1 = 220
    f.append(textbox(cx1, 95, "Калібрування (Calibration)\nISO/IEC 17025", size=13, bold=True, fill="#eaf2f8", stroke="#2980b9", pad=12)[0])
    
    f.append(rect(45, 140, 350, 185, fill=BG, stroke="#2980b9", sw=1.5, rx=6))
    f.append(text(60, 165, "• Визначає фактичний відгук y = f(x)", size=11.5, color=INK, anchor="start", bold=True))
    f.append(text(60, 190, "• Розраховує зміщення: Δ(x) = y_вим − x_етал", size=11, color=INK, anchor="start"))
    f.append(text(60, 215, "• Оцінює розширену невизначеність: U(k=2)", size=11, color=INK, anchor="start"))
    f.append(text(60, 240, "• Видає: Калібрувальний сертифікат з таблицею", size=11, color=INK, anchor="start"))
    f.append(text(60, 265, "• Результат: математична модель поправки", size=11, color="#2980b9", anchor="start", bold=True))
    f.append(text(60, 295, "НЕ виносить вердикту «придатний / непридатний»", size=10.5, color=MUTED, italic=True, anchor="start"))

    # Правий блок: Повірка
    cx2 = 640
    f.append(textbox(cx2, 95, "Повірка / Оцінка відповідності\nVerification / Legal Metrology", size=13, bold=True, fill="#fdedec", stroke=POS, pad=12)[0])

    f.append(rect(465, 140, 350, 185, fill=BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(480, 165, "• Порівнює похибку з допуском: |Δ| ≤ MPE", size=11.5, color=INK, anchor="start", bold=True))
    f.append(text(480, 190, "• Враховує правила прийняття рішень (ILAC-G8)", size=11, color=INK, anchor="start"))
    f.append(text(480, 215, "• Застосовує захисні смуги проти хибного ризику", size=11, color=INK, anchor="start"))
    f.append(text(480, 240, "• Видає: Свідоцтво про повірку або тавро", size=11, color=INK, anchor="start"))
    f.append(text(480, 265, "• Результат: Бінарне рішення (Pass / Fail)", size=11, color=POS, anchor="start", bold=True))
    f.append(text(480, 295, "Юридичний дозвіл на комерційне використання", size=10.5, color=MUTED, italic=True, anchor="start"))

    render(os.path.join(IMG, "cal-vs-verif.svg"), W, H, *f)


# ── Фігура 3: Коефіцієнт запасу невизначеності TUR та захисна смуга ──
def fig_tur_guardband():
    W, H = 880, 380
    f = [
        text(W / 2, 28, "Коефіцієнт запасу TUR (≥ 4:1) та захисна смуга (Guard Band)", size=16, bold=True),
        text(W / 2, 48, "чим вужча невизначеність еталона, тим менший ризик помилково забракувати або прийняти прилад",
             size=11, color=MUTED, italic=True)
    ]

    # Графічна візуалізація допуску
    axis_y = 190
    x_lsl = 120
    x_usl = 760
    mid_x = (x_lsl + x_usl) / 2

    # Фон допуску
    f.append(rect(x_lsl, axis_y - 70, x_usl - x_lsl, 140, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=4))
    
    # Зони виходу за допуск (червоні)
    f.append(rect(40, axis_y - 70, x_lsl - 40, 140, fill="#fdf2f0", stroke=POS, sw=1.5, rx=4))
    f.append(rect(x_usl, axis_y - 70, 840 - x_usl, 140, fill="#fdf2f0", stroke=POS, sw=1.5, rx=4))

    # Лінії допусків
    f.append(line(x_lsl, axis_y - 85, x_lsl, axis_y + 85, color=POS, sw=2.5))
    f.append(line(x_usl, axis_y - 85, x_usl, axis_y + 85, color=POS, sw=2.5))
    f.append(text(x_lsl, axis_y - 95, "Нижня межа (−MPE)", size=11, color=POS, bold=True))
    f.append(text(x_usl, axis_y - 95, "Верхня межа (+MPE)", size=11, color=POS, bold=True))

    # Центральна номінальна лінія
    f.append(line(mid_x, axis_y - 70, mid_x, axis_y + 70, color=MUTED, sw=1, dash="4,4"))
    f.append(text(mid_x, axis_y - 78, "Номінал (0)", size=11, color=MUTED))

    # Захисна смуга Guard Band (w = U)
    gb_w = 70
    f.append(rect(x_usl - gb_w, axis_y - 65, gb_w, 130, fill="#fff8e7", stroke="#d35400", sw=1.5))
    f.append(text(x_usl - gb_w / 2, axis_y - 45, "Захисна", size=10, color="#d35400", bold=True))
    f.append(text(x_usl - gb_w / 2, axis_y - 32, "смуга w=U", size=10, color="#d35400", bold=True))
    f.append(text(x_usl - gb_w / 2, axis_y + 50, "Зона ризику", size=9.5, color="#d35400"))

    # Зона безумовного прийняття
    f.append(text(mid_x, axis_y + 35, "Зона безумовного прийняття (Acceptance Zone)", size=12, color=FIELD, bold=True))
    f.append(text(mid_x, axis_y + 52, "Похибка гарантовано в межах допуску з PFA < 2%", size=10, color=MUTED))

    # Порівняння TUR
    f.append(rect(60, 290, 360, 65, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(240, 312, "TUR ≥ 4:1 (Стандарт)", size=12, color=FIELD, bold=True))
    f.append(text(240, 332, "Невизначеність U ≤ 25% допуску MPE • Ризик < 2%", size=10, color=INK))

    f.append(rect(460, 290, 360, 65, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(640, 312, "TUR < 2:1 (Неприпустимо без захисних смуг)", size=12, color=POS, bold=True))
    f.append(text(640, 332, "Невизначеність U перекриває межу • Високий ризик браку", size=10, color=INK))

    render(os.path.join(IMG, "tur-guardband.svg"), W, H, *f)


# ── Фігура 4: Часовий дрейф і міжповірочний інтервал ──
def fig_drift_recal_interval():
    W, H = 860, 360
    f = [
        text(W / 2, 28, "Часовий дрейф компонентів і міжповірочний інтервал (Recalibration Interval)", size=16, bold=True),
        text(W / 2, 48, "конус невизначеності зростає з часом; перекалібрування скидає систематичний зсув до нуля",
             size=11, color=MUTED, italic=True)
    ]

    # Осі координат
    ox, oy = 90, 200
    f.append(line(ox, oy, 780, oy, color=LINE, sw=1.5))       # Вісь часу t
    f.append(line(ox, 60, ox, 310, color=LINE, sw=1.5))       # Вісь похибки Δ

    f.append(text(780, oy + 22, "Час t (місяці)", size=11, color=INK, bold=True))
    f.append(text(ox - 10, 75, "+MPE", size=11, color=POS, bold=True, anchor="end"))
    f.append(text(ox - 10, 305, "−MPE", size=11, color=POS, bold=True, anchor="end"))
    f.append(text(ox - 10, oy + 4, "0", size=11, color=MUTED, anchor="end"))

    # Горизонтальні границі MPE
    f.append(line(ox, 90, 760, 90, color=POS, sw=1.5, dash="5,5"))
    f.append(line(ox, 290, 760, 290, color=POS, sw=1.5, dash="5,5"))

    # Перший інтервал: дрейф від t=0 до t=12 міс (T_cal)
    # Конус невизначеності
    t_recal1 = 410
    # Верхня межа конуса
    f.append(line(ox, 185, t_recal1, 100, color="#2980b9", sw=1.8))
    # Нижня межа конуса
    f.append(line(ox, 215, t_recal1, 230, color="#2980b9", sw=1.8))
    # Середня лінія дрейфу
    f.append(line(ox, oy, t_recal1, 165, color=INK, sw=2))

    # Світла заливка конуса (полігон)
    poly_pts = "%d,%d %d,%d %d,%d %d,%d" % (ox, 185, t_recal1, 100, t_recal1, 230, ox, 215)
    f.append('<polygon points="%s" fill="#ebf5fb" opacity="0.6"/>' % poly_pts)

    # Точка перекалібрування 1
    f.append(line(t_recal1, 60, t_recal1, 310, color=FIELD, sw=2, dash="4,3"))
    f.append(text(t_recal1, 330, "t = 12 міс (T_cal)", size=11, color=FIELD, bold=True))
    f.append(textbox(t_recal1, 75, "Перекалібрування:\nзсув скинуто на 0", size=10, bold=True, fill="#e8f8f5", stroke=FIELD)[0])

    # Скидання зсуву вниз
    f.append(arrow(t_recal1, 165, t_recal1, oy, color=FIELD, sw=2.5))

    # Другий інтервал: від t=12 міс до t=24 міс
    t_recal2 = 730
    f.append(line(t_recal1, 185, t_recal2, 105, color="#2980b9", sw=1.8))
    f.append(line(t_recal1, 215, t_recal2, 235, color="#2980b9", sw=1.8))
    f.append(line(t_recal1, oy, t_recal2, 170, color=INK, sw=2))
    poly_pts2 = "%d,%d %d,%d %d,%d %d,%d" % (t_recal1, 185, t_recal2, 105, t_recal2, 235, t_recal1, 215)
    f.append('<polygon points="%s" fill="#ebf5fb" opacity="0.6"/>' % poly_pts2)

    # Підписи
    f.append(text(250, 150, "Середній дрейф D·t", size=10.5, color=INK, bold=True))
    f.append(text(250, 245, "Конус розширеної невизначеності U(t)", size=10, color="#2980b9", italic=True))
    f.append(text(570, 150, "Новий цикл старіння", size=10.5, color=INK, bold=True))

    render(os.path.join(IMG, "drift-recal-interval.svg"), W, H, *f)


if __name__ == "__main__":
    fig_traceability_chain()
    fig_cal_vs_verif()
    fig_tur_guardband()
    fig_drift_recal_interval()
    print("All figures generated successfully.")
