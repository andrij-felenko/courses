# -*- coding: utf-8 -*-
"""Фігури до теми «Вузол без батареї: чи можливо і коли».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: Апаратна архітектура безбатарейного вузла ────────────────────────
def fig_batteryless_architecture():
    W, H = 840, 420
    f = [text(W / 2, 28, "Апаратна архітектура безбатарейного автономного вузла", size=15, bold=True)]

    # 1. Джерело енергії
    b1 = fitbox(30, 70, 150, 240,
                "ДЖЕРЕЛО ЕНЕРГІЇ\n\n• Сонячна панель\n• TEG (Зеєбек)\n• П'єзогенератор\n• RF-збирач\n\nP_in: 5–100 мкВт",
                size=11.5, fill="#fff7e6", stroke="#b8860b", sw=1.8, bold=True)
    f.append(b1)

    # Стрілка від джерела до PMIC
    f.append(arrow(180, 190, 230, 190, color=LINE))
    f.append(text(205, 178, "мікрострум", size=9.5, color=MUTED, anchor="middle"))

    # 2. EH PMIC велика рамка
    f.append(rect(230, 60, 260, 260, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    f.append(text(360, 84, "EH PMIC (BQ25570 / AEM10941)", size=12, bold=True, color=INK))

    # Внутрішні блоки PMIC
    f.append(fitbox(245, 100, 230, 38, "Холодний старт\n(Charge Pump / JFET)", size=10.5, fill="#eef1f4", stroke=MUTED))
    f.append(fitbox(245, 148, 230, 42, "MPPT Boost-перетворювач\n(динамічне узгодження R_in)", size=10.5, fill="#eaf0fd", stroke=NEG))
    f.append(fitbox(245, 200, 230, 42, "Гістерезисний супервізор\n(V_high = 3.3 В, V_low = 1.8 В)", size=10.5, fill="#fdecea", stroke=POS))
    f.append(fitbox(245, 252, 230, 52, "Силовий ключ VOUT_EN\n(комутація виходу навантаження)", size=10.5, fill="#eafaf1", stroke=FIELD))

    # 3. Накопичувач енергії зверху від лінії V_STOR
    f.append(line(475, 169, 540, 169, color=POS, sw=2))
    f.append(line(540, 169, 540, 90, color=POS, sw=2))
    f.append(arrow(540, 90, 570, 90, color=POS))
    f.append(text(507, 160, "V_STOR", size=10, bold=True, color=POS, anchor="middle"))

    b_store = fitbox(570, 60, 240, 75,
                     "БУФЕРНИЙ НАКОПИЧУВАЧ\n\n• Іоністор (0.1–1.0 Ф, 3.3 В)\n• Тантал / MLCC (100–470 мкФ)\nНизький струм витоку (I_leak < 1 мкА)",
                     size=10.5, fill="#fdecea", stroke=POS, sw=1.8, bold=True)
    f.append(b_store)

    # 4. Комутована лінія VOUT до МК і Радіо
    f.append(arrow(475, 278, 570, 278, color=FIELD, sw=2.2))
    f.append(text(522, 268, "V_OUT", size=11, bold=True, color=FIELD, anchor="middle"))
    f.append(text(522, 296, "3.3 В (імпульс)", size=9.5, color=FIELD, anchor="middle"))

    # Блок споживача
    f.append(rect(570, 160, 240, 160, fill="#ffffff", stroke=FIELD, sw=2, rx=8))
    f.append(text(690, 182, "СПЛАВ НАВАНТАЖЕННЯ (3–10 мс)", size=11, bold=True, color=FIELD))

    f.append(fitbox(585, 196, 210, 52, "ULP Мікроконтролер\n(Cortex-M0+ / M33)\n+ Вбудована пам'ять FRAM", size=10.5, fill="#eafaf1", stroke=FIELD))
    f.append(fitbox(585, 256, 210, 50, "Радіопередавач\n(BLE Adv / Sub-GHz / LoRa)\nI_peak = 15–30 мА", size=10.5, fill="#eaf0fd", stroke=NEG))

    # Нижня підсумкова плашка
    b_foot, _, _ = textbox(W / 2, 380,
                           "Повний розрив кіл: під час тривалого заряду накопичувача навантаження фізично відрізане силовим ключем;\n"
                           "після досягнення V_high ключ вмикається, навантаження виконує швидкий імпульс і знеструмлюється.",
                           size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b_foot)

    render(os.path.join(IMG, "batteryless-architecture.svg"), W, H, *f)


# ── Фігура 2: Профіль напруги та струму Run-to-Die ─────────────────────────────
def fig_run_to_die_profile():
    W, H = 840, 450
    f = [text(W / 2, 26, "Часовий профіль імпульсу Run-to-Die: фаза накопичення та сплеск активності", size=14.5, bold=True)]

    ox, oy = 80, 210
    tw = 700

    # Верхній графік: Напруга накопичувача V_cap(t)
    f.append(line(ox, oy, ox + tw, oy, color=LINE, sw=1.5))       # вісь t
    f.append(line(ox, oy, ox, 55, color=LINE, sw=1.5))            # вісь V
    f.append(text(ox - 10, 65, "V_cap", size=11, bold=True, color=POS, anchor="end"))

    # Рівні напруг: V_high (3.3V) та V_low (1.8V)
    y_high = 90
    y_low = 165
    f.append(line(ox, y_high, ox + tw, y_high, color=POS, sw=1.2, dash="4 4"))
    f.append(text(ox - 8, y_high + 4, "V_high (3.3 В)", size=10, color=POS, anchor="end"))

    f.append(line(ox, y_low, ox + tw, y_low, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(ox - 8, y_low + 4, "V_low (1.8 В)", size=10, color=MUTED, anchor="end"))

    # Межі імпульсу по осі X
    t_start = ox + 320
    t_end = ox + 370

    # Траєкторія напруги: повільний підйом -> різкий спад на імпульсі -> повільний підйом
    p1 = f"{ox},{oy}"
    p2 = f"{t_start},{y_high}"
    p3 = f"{t_end},{y_low}"
    p4 = f"{ox+tw},{105}"
    f.append(f'<path d="M {p1} Q {ox+160} {y_high+45} {p2} L {p3} Q {ox+530} {y_low+30} {p4}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Вертикальні пунктирні лінії меж активної фази (короткі, тільки між графіками і вгору)
    f.append(line(t_start, y_high - 18, t_start, 350, color=FIELD, sw=1.4, dash="3 3"))
    f.append(line(t_end, y_high - 18, t_end, 350, color=FIELD, sw=1.4, dash="3 3"))

    f.append(rect((t_start + t_end) / 2 - 28, y_high - 36, 56, 20, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    f.append(text((t_start + t_end) / 2, y_high - 22, "3–10 мс", size=9.5, bold=True, color=FIELD))

    # Нижній графік: Струм навантаження I_load(t)
    oy2 = 360
    f.append(line(ox, oy2, ox + tw, oy2, color=LINE, sw=1.5))     # вісь t
    f.append(line(ox, oy2, ox, 240, color=LINE, sw=1.5))          # вісь I
    f.append(text(ox - 10, 248, "I_load", size=11, bold=True, color=NEG, anchor="end"))

    # Струм: 0 мкА -> стрибок 20 мА -> 0 мкА
    f.append(f'<path d="M {ox},{oy2} L {t_start},{oy2} L {t_start},265 L {t_end},265 L {t_end},{oy2} L {ox+tw},{oy2}" fill="#eaf0fd" stroke="{NEG}" stroke-width="2"/>')
    f.append(text((t_start + t_end) / 2, 255, "20 мА", size=10, bold=True, color=NEG))
    f.append(text(ox + 140, oy2 - 8, "I_sleep ≈ 0 (ключ розімкнено)", size=10, color=MUTED))
    f.append(text(ox + 520, oy2 - 8, "Фаза відновлення заряду", size=10, color=MUTED))

    # Текстові пояснення фаз (розміщені у вільних зонах)
    f.append(text(ox + 140, 130, "Фаза накопичення\n(секунди / хвилини, P_in ≈ 20 мкВт)", size=10, color=INK, anchor="middle"))
    f.append(text(ox + 560, 150, "Повторне накопичення заряду до V_high", size=10, color=INK, anchor="middle"))

    # Етапи всередині імпульсу — розміщені праворуч зверху у вільній зоні над відновленням
    f.append(fitbox(ox + 410, 60, 220, 68, "Послідовність активного сплеску:\n1. Старт ядра МК (<10 мкс)\n2. Замір сенсора (АЦП / I²C, ~1 мс)\n3. BLE Advertisements (2–3 мс)\n4. Запис стану у FRAM (50 мкс)", size=9.5, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Підвал
    b_foot, _, _ = textbox(W / 2, 412,
                           "Енергія імпульсу: E = 1/2 · C · (V_high² − V_low²). Робота триває рівно стільки, на скільки вистачає заряду конденсатора.",
                           size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b_foot)

    render(os.path.join(IMG, "run-to-die-profile.svg"), W, H, *f)


# ── Фігура 3: Порівняння технологій накопичувачів енергії ───────────────────────
def fig_storage_comparison_matrix():
    W, H = 840, 400
    f = [text(W / 2, 28, "Порівняння буферних накопичувачів для безбатарейних вузлів", size=15, bold=True)]

    colx = 40
    rowh = 52
    w_tech = 160
    w_col = 145

    # Заголовки таблиці
    f.append(fitbox(colx, 56, w_tech, 36, "Технологія", size=12, fill="#eceff3", bold=True))
    f.append(fitbox(colx + w_tech + 8, 56, w_col, 36, "Струм витоку\n(I_leak)", size=11, fill="#eceff3", bold=True))
    f.append(fitbox(colx + w_tech + w_col + 16, 56, w_col, 36, "Еквівалентний опір\n(ESR)", size=11, fill="#eceff3", bold=True))
    f.append(fitbox(colx + w_tech + 2 * w_col + 24, 56, w_col, 36, "Ресурс циклів\n(Cyc. Life)", size=11, fill="#eceff3", bold=True))
    f.append(fitbox(colx + w_tech + 3 * w_col + 32, 56, w_col, 36, "Температурний\nдіапазон", size=11, fill="#eceff3", bold=True))

    rows = [
        ("Кераміка MLCC\n(X7R / X5R, 10–100 мкФ)", "< 10 нА (ідеально)", "< 10 мОм (ідеально)", "> 10¹⁰ (необмежено)", "−55 ... +125 °C", "#eafaf1", FIELD),
        ("Тантал полімерний\n(POSCAP, 100–470 мкФ)", "~ 0.1–0.5 мкА (добре)", "20–50 мОм (добре)", "> 10¹⁰ (необмежено)", "−55 ... +105 °C", "#eafaf1", FIELD),
        ("Іоністор EDLC\n(0.1–1.0 Ф, 3.3–5.5 В)", "1–5 мкА (критично)", "0.5–5 Ом (посередньо)", "> 10⁶ циклів", "−40 ... +70 °C", "#fff7e6", "#b8860b"),
        ("Li-Ion конденсатор (LiC)\n(10–100 Ф, 3.8 В)", "3–10 мкА (високий)", "50–200 мОм", "> 50 000 циклів", "−25 ... +60 °C", "#fff7e6", "#b8860b"),
        ("Первинна літієва батарея\n(CR2032, 220 мА·год)", "Саморозряд 1%/рік", "10–30 Ом (провали)", "1 (одноразова)", "−20 ... +60 °C", "#fdecea", POS),
    ]

    y = 100
    for name, ileak, esr, cyc, temp, fill, col in rows:
        f.append(fitbox(colx, y, w_tech, rowh - 6, name, size=11, fill=fill, stroke=col, bold=True))
        f.append(fitbox(colx + w_tech + 8, y, w_col, rowh - 6, ileak, size=11, fill="#ffffff", stroke=MUTED))
        f.append(fitbox(colx + w_tech + w_col + 16, y, w_col, rowh - 6, esr, size=11, fill="#ffffff", stroke=MUTED))
        f.append(fitbox(colx + w_tech + 2 * w_col + 24, y, w_col, rowh - 6, cyc, size=11, fill="#ffffff", stroke=MUTED))
        f.append(fitbox(colx + w_tech + 3 * w_col + 32, y, w_col, rowh - 6, temp, size=11, fill="#ffffff", stroke=MUTED))
        y += rowh

    b_foot, _, _ = textbox(W / 2, y + 26,
                           "Для мікрозбирачів (<50 мкВт) критичним є струм витоку: якщо I_leak > I_harvest, вузол ніколи не зарядиться.\n"
                           "Тантал і кераміка забезпечують надійний старт при слабкому освітленні, іоністори — ємність під важкі імпульси.",
                           size=10.5, fill="#f4f6f8", stroke=LINE)
    f.append(b_foot)

    render(os.path.join(IMG, "storage-comparison-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_batteryless_architecture()
    fig_run_to_die_profile()
    fig_storage_comparison_matrix()
    print("OK: 3 figures ->", IMG)
