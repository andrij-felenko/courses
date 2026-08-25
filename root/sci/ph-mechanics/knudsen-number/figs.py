# -*- coding: utf-8 -*-
"""Фігури до теми «Число Кнудсена».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def fig_knudsen_concept():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Середній вільний пробіг λ проти характерного розміру L", size=18, bold=True))

    # --- Ліва панель: Суцільний режим (Kn << 0.01) ---
    x1, y1, w1, h1 = 35, 65, 360, 380
    f.append(rect(x1, y1, w1, h1, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x1 + w1 / 2, y1 + 25, "Суцільне середовище (Kn ≪ 0.01)", size=15, bold=True, color=NEG))
    f.append(text(x1 + w1 / 2, y1 + 45, "λ ≪ L: густі зіткнення між молекулами", size=12, color=MUTED))

    # Стінки каналу
    f.append(rect(x1 + 30, y1 + 75, w1 - 60, 20, fill="#d1d5db", stroke=LINE, sw=1.2, rx=2))
    f.append(text(x1 + w1 / 2, y1 + 89, "Верхня стінка каналу", size=11, color=INK))
    f.append(rect(x1 + 30, y1 + 275, w1 - 60, 20, fill="#d1d5db", stroke=LINE, sw=1.2, rx=2))
    f.append(text(x1 + w1 / 2, y1 + 289, "Нижня стінка каналу", size=11, color=INK))

    # Розмір L
    f.append(line(x1 + 40, y1 + 95, x1 + 40, y1 + 275, color=POS, sw=1.8, dash="4,3"))
    f.append(text(x1 + 25, y1 + 190, "L", size=16, bold=True, color=POS))

    # Молекули та зигзагоподібні шляхи (багато молекулярних зіткнень)
    pts_dense = [
        (x1 + 70, y1 + 120), (x1 + 85, y1 + 140), (x1 + 100, y1 + 125),
        (x1 + 120, y1 + 155), (x1 + 135, y1 + 130), (x1 + 150, y1 + 170),
        (x1 + 175, y1 + 150), (x1 + 190, y1 + 185), (x1 + 210, y1 + 160),
        (x1 + 230, y1 + 210), (x1 + 255, y1 + 190), (x1 + 280, y1 + 240)
    ]
    p_str = " ".join("%.1f,%.1f" % p for p in pts_dense)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (p_str, NEG))
    for px, py in pts_dense:
        f.append(circle(px, py, 4, fill=NEG, stroke=LINE, sw=1))

    # Підпис лямбда в лівій панелі
    f.append(line(x1 + 85, y1 + 140, x1 + 100, y1 + 125, color=POS, sw=2.5))
    f.append(text(x1 + 95, y1 + 115, "малий λ", size=12, bold=True, color=POS))

    f.append(fitbox(x1 + 20, y1 + 310, w1 - 40, 55,
                    "Суцільний режим: молекули безнастанно\nзіштовхуються одна з одною в об'ємі.\nДіють рівняння Нав'є-Стокса.",
                    size=12, pad=6, fill="#eef1fb", stroke=NEG))

    # --- Права панель: Вільномолекулярний режим (Kn >> 10) ---
    x2, y2, w2, h2 = 425, 65, 360, 380
    f.append(rect(x2, y2, w2, h2, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(x2 + w2 / 2, y2 + 25, "Вільномолекулярний потік (Kn ≫ 10)", size=15, bold=True, color=POS))
    f.append(text(x2 + w2 / 2, y2 + 45, "λ ≫ L: балістичний політ від стінки до стінки", size=12, color=MUTED))

    # Стінки каналу
    f.append(rect(x2 + 30, y2 + 75, w2 - 60, 20, fill="#d1d5db", stroke=LINE, sw=1.2, rx=2))
    f.append(text(x2 + w2 / 2, y2 + 89, "Верхня стінка каналу", size=11, color=INK))
    f.append(rect(x2 + 30, y2 + 275, w2 - 60, 20, fill="#d1d5db", stroke=LINE, sw=1.2, rx=2))
    f.append(text(x2 + w2 / 2, y2 + 289, "Нижня стінка каналу", size=11, color=INK))

    # Прямолінійні балістичні траєкторії
    bal1 = [(x2 + 60, y2 + 275), (x2 + 140, y2 + 95), (x2 + 220, y2 + 275), (x2 + 300, y2 + 95)]
    p_str1 = " ".join("%.1f,%.1f" % p for p in bal1)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" stroke-dasharray="6,3"/>' % (p_str1, POS))
    for px, py in bal1:
        f.append(circle(px, py, 5, fill=POS, stroke=LINE, sw=1))

    f.append(text(x2 + 150, y2 + 175, "великий λ ≫ L", size=13, bold=True, color=POS))

    f.append(fitbox(x2 + 20, y2 + 310, w2 - 40, 55,
                    "Розріджений режим: зіткнення в газі відсутні.\nМолекули летять прямолінійно від стінки до стінки.\nКінетична теорія Кнудсена.",
                    size=12, pad=6, fill="#fdecea", stroke=POS))

    render(os.path.join(IMG, 'knudsen-concept.svg'), W, H, *f)


def fig_knudsen_regimes():
    W, H = 840, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Чотири режими течії за числом Кнудсена Kn", size=18, bold=True))

    # Спектр чисел Kn
    f.append(line(50, 80, 790, 80, color=LINE, sw=2.5))
    
    # Відмітки шкали
    ticks = [
        (80, "10⁻⁴"), (230, "0.01"), (410, "0.1"), (590, "10"), (750, "10²")
    ]
    for tx, label in ticks:
        f.append(line(tx, 73, tx, 87, color=LINE, sw=2))
        f.append(text(tx, 65, label, size=12, bold=True))

    # 4 Блоки режимів
    # 1. Суцільний
    f.append(fitbox(60, 105, 160, 240,
                    "Суцільний\nKn < 0.01\n\nМодель:\nНав'є-Стовкс з умовою\nприлипання (v_slip=0)\n\nПриклади:\nЛітак біля землі,\nтрубопроводи",
                    size=12, pad=8, fill="#eef1fb", stroke=NEG, sw=1.8))

    # 2. З ковзанням
    f.append(fitbox(240, 105, 160, 240,
                    "З ковзанням\n0.01 ≤ Kn < 0.1\n\nМодель:\nНав'є-Стовкс з умовою\nМаксвелла (v_slip ≠ 0)\nта стрибком T_jump\n\nПриклади:\nМікроканали, МЕМС",
                    size=12, pad=8, fill="#eef8f2", stroke=FIELD, sw=1.8))

    # 3. Перехідний
    f.append(fitbox(420, 105, 160, 240,
                    "Перехідний\n0.1 ≤ Kn < 10\n\nМодель:\nРівняння Больцмана,\nметод DSMC\n(Монте-Карло)\n\nПриклади:\nГоловка HDD (10 нм),\nвакуумний опір",
                    size=12, pad=8, fill="#fff8eb", stroke="#e67e22", sw=1.8))

    # 4. Вільномолекулярний
    f.append(fitbox(600, 105, 160, 240,
                    "Вільномолекулярний\nKn ≥ 10\n\nМодель:\nБеззіткнувальна\nкінетика, ефузія\nКнудсена\n\nПриклади:\nСупутники термосфери,\nвисокий вакуум",
                    size=12, pad=8, fill="#fdecea", stroke=POS, sw=1.8))

    # Нижній узагальнювальний блок
    f.append(fitbox(60, 365, 700, 80,
                    "Фізичний зміст переходу:\nІз зростанням Kn тонка пристінкова область (шар Кнудсена товщиною ~λ) розростається й заповнює весь переріз.\nКласична гідродинаміка втрачає силу, і опис переходить від суцільних полів v, P до кінетичної теорії молекул.",
                    size=12, pad=10, fill=FILL, stroke=LINE, sw=1.5))

    render(os.path.join(IMG, 'knudsen-regimes.svg'), W, H, *f)


def fig_knudsen_triad():
    W, H = 820, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Трикутник газової динаміки: Kn, Ma та Re", size=18, bold=True))

    # Три вершини трикутника
    # Верхня: Kn
    b1, w1, h1 = textbox(W / 2, 100, "Число Кнудсена\nKn = λ / L\n(Розрідженість)", size=14, pad=10, fill="#fdecea", stroke=POS, sw=2, bold=True)
    f.append(b1)

    # Нижня ліва: Ma
    b2, w2, h2 = textbox(180, 340, "Число Маха\nMa = v / a\n(Стисливість)", size=14, pad=10, fill="#eef1fb", stroke=NEG, sw=2, bold=True)
    f.append(b2)

    # Нижня права: Re
    b3, w3, h3 = textbox(640, 340, "Число Рейнольдса\nRe = ρ·v·L / μ\n(В'язкість та інерція)", size=14, pad=10, fill="#eef8f2", stroke=FIELD, sw=2, bold=True)
    f.append(b3)

    # Зв'язувальні лінії-стрілки
    f.append(line(W / 2 - 60, 135, 230, 290, color=LINE, sw=2))
    f.append(line(W / 2 + 60, 135, 590, 290, color=LINE, sw=2))
    f.append(line(270, 340, 540, 340, color=LINE, sw=2))

    # Формула фон Кармана в центрі
    f.append(fitbox(290, 195, 240, 95,
                    "Співвідношення фон Кармана:\n\nKn ≈ (Ma / Re) · √(γ·π / 2)\n\nKn зростає при високому Ma\nабо при малому Re",
                    size=13, pad=8, fill="#fff8eb", stroke="#e67e22", sw=1.8, bold=True))

    # Пояснення
    f.append(fitbox(60, 400, 700, 55,
                    "Практичний висновок: під час гіперзвукового входу в атмосферу (велике Ma) на високих альтернативах (мала густина ρ → мале Re)\nгаз стає сильно розрідженим (велике Kn), навіть якщо геометричний розмір апарата L становить кілька метрів.",
                    size=11.5, pad=6, fill=FILL, stroke=LINE, sw=1.2))

    render(os.path.join(IMG, 'knudsen-triad.svg'), W, H, *f)


if __name__ == '__main__':
    fig_knudsen_concept()
    fig_knudsen_regimes()
    fig_knudsen_triad()
    print("Фігури успішно згенеровано у ./img/")
