# -*- coding: utf-8 -*-
"""Фігури теми «Режими живлення й темп вимірювання». Запуск: python figs.py  → ./img/*.svg"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фіг.1 — Профілі живлення: Continuous vs Single-shot (Forced) ──────────────
def fig_power_profiles():
    W, H = 760, 440
    frs = []

    # Заголовок / фон
    frs.append(rect(20, 20, 720, 400, fill="#ffffff", stroke=LINE, sw=1.2))

    # Ліва половина: Continuous Mode
    frs.append(fitbox(40, 35, 320, 38, "Continuous Mode (безперервне вимірювання)", size=12,
                      fill="#fdecea", stroke=POS, color=POS, bold=True))

    # Вісь часу та струму для лівої частини
    ox1, oy1 = 60, 230
    w1, h1 = 280, 140
    frs.append(line(ox1, oy1, ox1 + w1, oy1, color=INK, sw=1.8))  # вісь t
    frs.append(line(ox1, oy1, ox1, oy1 - h1, color=INK, sw=1.8))  # вісь I
    frs.append(arrow(ox1 + w1 - 5, oy1, ox1 + w1 + 10, oy1, color=INK, sw=1.8))
    frs.append(arrow(ox1, oy1 - h1 + 5, ox1, oy1 - h1 - 10, color=INK, sw=1.8))
    frs.append(text(ox1 + w1 + 15, oy1 + 4, "t", size=12, color=INK, anchor="start"))
    frs.append(text(ox1 - 10, oy1 - h1 - 6, "I, мА", size=12, color=INK, anchor="end"))

    # Постійний високий струм
    act_y1 = oy1 - 100
    frs.append(rect(ox1 + 1, act_y1, w1 - 10, 100, fill="#fdecea", stroke="none"))
    frs.append(line(ox1, act_y1, ox1 + w1 - 10, act_y1, color=POS, sw=2.6))
    frs.append(line(ox1 - 4, act_y1, ox1, act_y1, color=POS, sw=1.5))
    frs.append(text(ox1 - 8, act_y1 + 4, "2.5 мА", size=11, color=POS, bold=True, anchor="end"))

    frs.append(fitbox(50, 255, 300, 145,
                      "Аналоговий тракт і АЦП увімкнені постійно.\n\n"
                      "• Струм I_avg ≈ 2.5 мА\n"
                      "• Батарея CR2032 (220 мА·год) сідає за:\n"
                      "   220 / 2.5 = 88 годин (менше 4 діб!)\n"
                      "• Швидке оновлення, але марнування заряду",
                      size=11, fill=FILL, stroke=POS))

    # Права половина: Single-shot / Duty-cycled Mode
    frs.append(fitbox(400, 35, 320, 38, "Single-shot / Duty-Cycled Mode (циклічний сон)", size=12,
                      fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))

    ox2, oy2 = 420, 230
    w2, h2 = 280, 140
    frs.append(line(ox2, oy2, ox2 + w2, oy2, color=INK, sw=1.8))
    frs.append(line(ox2, oy2, ox2, oy2 - h2, color=INK, sw=1.8))
    frs.append(arrow(ox2 + w2 - 5, oy2, ox2 + w2 + 10, oy2, color=INK, sw=1.8))
    frs.append(arrow(ox2, oy2 - h2 + 5, ox2, oy2 - h2 - 10, color=INK, sw=1.8))
    frs.append(text(ox2 + w2 + 15, oy2 + 4, "t", size=12, color=INK, anchor="start"))
    frs.append(text(ox2 - 10, oy2 - h2 - 6, "I, мА", size=12, color=INK, anchor="end"))

    # Імпульси струму
    # Період T = 1 с, активна фаза t_act = 5 мс (масштабовано для наочності)
    pulses = [ox2 + 20, ox2 + 140, ox2 + 260]
    pw = 25
    act_y2 = oy2 - 100
    sleep_y2 = oy2 - 4

    for px in pulses:
        frs.append(rect(px, act_y2, pw, 100, fill="#eafaf0", stroke=FIELD, sw=1.5))
        frs.append(text(px + pw / 2, act_y2 - 8, "5 мс", size=10, color=FIELD, bold=True))

    # Лінія сну
    frs.append(line(ox2, sleep_y2, ox2 + w2 - 10, sleep_y2, color=NEG, sw=2))
    frs.append(text(ox2 + w2 - 5, sleep_y2 - 6, "0.5 мкА (сон)", size=10, color=NEG, anchor="start"))

    # Позначка періоду T
    frs.append(line(pulses[0], oy2 + 15, pulses[1], oy2 + 15, color=MUTED, sw=1.2))
    frs.append(line(pulses[0], oy2 + 10, pulses[0], oy2 + 20, color=MUTED, sw=1.2))
    frs.append(line(pulses[1], oy2 + 10, pulses[1], oy2 + 20, color=MUTED, sw=1.2))
    frs.append(text((pulses[0] + pulses[1]) / 2, oy2 + 30, "Період вибірки T_sample (1 с)", size=10, color=MUTED))

    frs.append(fitbox(410, 255, 300, 145,
                      "Давач спить 99.5% часу й прокидається на 5 мс.\n\n"
                      "• I_avg = (2.5 мА × 5 мс + 0.5 мкА × 995 мс) / 1000 мс\n"
                      "• I_avg ≈ 12.5 мкА + 0.5 мкА = 13.0 мкА\n"
                      "• Ресурс CR2032: 220 мА·год / 13 мкА ≈ 1.9 року!\n"
                      "• Економія заряду: у 192 рази",
                      size=11, fill=FILL, stroke=FIELD))

    render(os.path.join(IMG, "sensor-power-profiles.svg"), W, H, *frs,
           title="Профілі струму: Continuous проти Single-shot режиму")


# ── Фіг.2 — Компроміс оверсемплінгу: шум проти тривалості та енергії ───────────
def fig_oversampling_tradeoff():
    W, H = 760, 420
    frs = []

    frs.append(rect(20, 20, 720, 380, fill="#ffffff", stroke=LINE, sw=1.2))

    # Поле графіка
    ox, oy = 90, 320
    gw, gh = 450, 240
    frs.append(line(ox, oy, ox + gw, oy, color=INK, sw=2))
    frs.append(line(ox, oy, ox, oy - gh, color=INK, sw=2))
    frs.append(text(ox + gw / 2, oy + 42, "Коефіцієнт оверсемплінгу (OSR)  →", size=12, color=INK, bold=True))
    frs.append(text(ox - 50, oy - gh / 2, "Рівень величини", size=12, color=INK, anchor="middle"))

    osr_labels = ["×1", "×2", "×4", "×8", "×16"]
    N = len(osr_labels)
    xs = [ox + (i + 0.6) / N * (gw - 30) for i in range(N)]

    for x, lbl in zip(xs, osr_labels):
        frs.append(line(x, oy, x, oy + 5, color=INK, sw=1.5))
        frs.append(text(x, oy + 20, lbl, size=11, color=INK, bold=True))

    # Крива шуму (падає як 1 / sqrt(OSR))
    noise_vals = [1.0, 1.0 / math.sqrt(2), 1.0 / math.sqrt(4), 1.0 / math.sqrt(8), 1.0 / math.sqrt(16)]
    pts_noise = []
    for x, nv in zip(xs, noise_vals):
        y = oy - (nv * 0.8 + 0.1) * gh
        pts_noise.append((x, y))
        frs.append(circle(x, y, 4, fill=NEG, stroke=NEG))

    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
               % (" ".join("%.1f,%.1f" % p for p in pts_noise), NEG))

    # Крива тривалості та енергії перетворення (росте лінійно з OSR)
    time_vals = [0.1, 0.2, 0.4, 0.7, 1.0]
    pts_time = []
    for x, tv in zip(xs, time_vals):
        y = oy - (tv * 0.85 + 0.05) * gh
        pts_time.append((x, y))
        frs.append(circle(x, y, 4, fill=POS, stroke=POS))

    frs.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="7 4"/>'
               % (" ".join("%.1f,%.1f" % p for p in pts_time), POS))

    # Підписи точок для крайніх значень
    frs.append(text(pts_noise[0][0] + 10, pts_noise[0][1] - 8, "Макс. шум (1.0)", size=10, color=NEG, anchor="start"))
    frs.append(text(pts_noise[-1][0], pts_noise[-1][1] - 12, "Шум = 0.25 (-75%)", size=10, color=NEG, anchor="middle"))

    frs.append(text(pts_time[0][0] + 10, pts_time[0][1] + 14, "t = 1.5 мс", size=10, color=POS, anchor="start"))
    frs.append(text(pts_time[-1][0], pts_time[-1][1] - 12, "t = 24 мс (×16 енергії)", size=10, color=POS, anchor="middle"))

    # Зона оптимуму (OSR ×4 .. ×8)
    opt_x1 = xs[1] + 10
    opt_x2 = xs[3] + 15
    frs.append(rect(opt_x1, oy - gh + 20, opt_x2 - opt_x1, gh - 25, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=4))
    frs.append(text((opt_x1 + opt_x2) / 2, oy - gh + 40, "Інженерний оптимум", size=11, color=FIELD, bold=True))
    frs.append(text((opt_x1 + opt_x2) / 2, oy - gh + 56, "(компроміс шум/енергія)", size=10, color=FIELD))

    # Легенда праворуч
    frs.append(fitbox(560, 50, 165, 140,
                      "ЛЕГЕНДА:\n\n"
                      "—— Шум RMS (1/√OSR)\n"
                      "   зменшується в 2 рази\n"
                      "   на кожні ×4 вибірок\n\n"
                      "- - Час і енергія\n"
                      "   E = V × I × t_act\n"
                      "   ростуть лінійно",
                      size=10, fill=FILL, stroke=LINE))

    # Висновок унизу праворуч
    frs.append(fitbox(560, 205, 165, 160,
                      "ВИСНОВОК:\n\n"
                      "Перехід від ×1 до ×16\n"
                      "зменшує шум у 4 рази,\n"
                      "але збільшує енергію\n"
                      "перетворення у 16 разів.\n\n"
                      "IIR-фільтр згладжує\n"
                      "без росту енергії,\n"
                      "але додає затримку.",
                      size=10, fill="#fff7e6", stroke="#b7791f", color="#8a5a00"))

    render(os.path.join(IMG, "oversampling-tradeoff.svg"), W, H, *frs,
           title="Компроміс оверсемплінгу: зниження шуму проти витрат заряду")


# ── Фіг.3 — Апаратний буфер FIFO: зчитування кожного відліку vs пакетний Burst ─
def fig_fifo_burst():
    W, H = 760, 450
    frs = []

    frs.append(rect(20, 20, 720, 410, fill="#ffffff", stroke=LINE, sw=1.2))

    # Верхній сценарій: Постійне пробудження МК на кожен відлік (без FIFO)
    frs.append(fitbox(40, 35, 680, 32, "Сценарій А: Зчитування на кожен відлік (100 Гц без FIFO) — неефективно",
                      size=12, fill="#fdecea", stroke=POS, color=POS, bold=True))

    ox1, oy1 = 175, 180
    w_line = 525
    frs.append(line(ox1, oy1, ox1 + w_line, oy1, color=INK, sw=1.5))
    frs.append(text(ox1 + w_line + 10, oy1 + 4, "t", size=12, color=INK))

    # Часті пробудження МК кожні 10 мс
    for i in range(14):
        px = ox1 + 15 + i * 36
        # Імпульс пробудження МК: підйом частоти, PLL, обробка переривання, шина
        frs.append(rect(px, oy1 - 55, 12, 55, fill="#fdecea", stroke=POS, sw=1))
        # Стрілка переривання DRDY
        frs.append(arrow(px + 6, oy1 + 18, px + 6, oy1 + 2, color=NEG, sw=1.2))

    frs.append(text(ox1 + 100, oy1 + 32, "Переривання DRDY кожні 10 мс (100 разів/сек)", size=10, color=NEG))
    frs.append(fitbox(40, 95, 120, 75, "МК витрачає\nенергію на старт\nPLL та вихід\nзі сну 100 р/с!",
                      size=9, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # Нижній сценарій: Пакетне зчитування через FIFO Watermark
    frs.append(fitbox(40, 240, 680, 32, "Сценарій Б: Накопичення у FIFO (32 семпли) + пакетний Burst Read — оптимум",
                      size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))

    ox2, oy2 = 60, 380
    frs.append(line(ox2, oy2, ox2 + w_line + 115, oy2, color=INK, sw=1.5))
    frs.append(text(ox2 + w_line + 125, oy2 + 4, "t", size=12, color=INK))

    # Період накопичення: давач сам пише у FIFO, МК у глибокому Stop/Standby (1.5 мкА)
    t_batch = 320  # пікселів = 32 семпли = 320 мс
    frs.append(rect(ox2 + 20, oy2 - 12, t_batch, 12, fill="#eaf0fd", stroke=NEG, sw=1))
    frs.append(text(ox2 + 20 + t_batch / 2, oy2 - 20, "МК у глибокому сні (Stop mode ~1.5 мкА) протягом 320 мс",
                    size=11, color=NEG, bold=True))

    # Переривання Watermark
    int_x = ox2 + 20 + t_batch
    frs.append(arrow(int_x, oy2 + 22, int_x, oy2 + 2, color=FIELD, sw=2))
    frs.append(text(int_x, oy2 + 34, "INT: FIFO Watermark (32 семпли)", size=10, color=FIELD, bold=True))

    # Короткий потужний Burst SPI/DMA зчитування
    burst_w = 28
    frs.append(rect(int_x, oy2 - 75, burst_w, 75, fill="#eafaf0", stroke=FIELD, sw=1.5))
    frs.append(text(int_x + burst_w / 2, oy2 - 82, "Burst DMA\n(~1.5 мс)", size=10, color=FIELD, bold=True))

    # Наступний період сну
    frs.append(rect(int_x + burst_w, oy2 - 12, 220, 12, fill="#eaf0fd", stroke=NEG, sw=1))
    frs.append(text(int_x + burst_w + 110, oy2 - 20, "Знову глибокий сон...", size=10, color=NEG))

    # Підсумок економії праворуч
    frs.append(fitbox(ox2 + 420, oy2 - 100, 220, 70,
                      "РЕЗУЛЬТАТ:\n"
                      "МК прокидається лише 3 рази/с\n"
                      "замість 100 разів/с.\n"
                      "Енерговитрати ядра падають у 8–12 разів!",
                      size=10, fill="#eafaf0", stroke=FIELD, color=FIELD))

    render(os.path.join(IMG, "fifo-burst-vs-per-sample.svg"), W, H, *frs,
           title="FIFO-буферизація: пакетне вичитування проти частих пробуджень")


# ── Фіг.4 — Подійно-орієнтоване пробудження: DRDY проти Any-Motion ─────────────
def fig_event_wakeup_fsm():
    W, H = 760, 420
    frs = []

    frs.append(rect(20, 20, 720, 380, fill="#ffffff", stroke=LINE, sw=1.2))

    # Лівий блок: Стан 1 - Глибокий сон системи
    frs.append(fitbox(40, 60, 200, 100,
                      "1. СПОКІЙ\n(Ultra Low Power)\n\n"
                      "• МК: Deep Sleep (1 мкА)\n"
                      "• Давач: Low-Power ODR (10 Гц)\n"
                      "• Струм давача: ~3 мкА",
                      size=11, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))

    # Стрілка переходу 1 -> 2
    frs.append(arrow(240, 110, 280, 110, color=INK, sw=2))
    frs.append(text(260, 95, "подія", size=10, color=MUTED))

    # Центральний блок: Стан 2 - Апаратний детектор події в чипі
    frs.append(fitbox(280, 60, 210, 100,
                      "2. АПАРАТНИЙ ДЕТЕКТОР\n(Внутрішня логіка чипа)\n\n"
                      "• Перевірка: |Δa| > Поріг\n"
                      "• Тривалість > N відліків\n"
                      "• МК все ще спить!",
                      size=11, fill="#fff7e6", stroke="#b7791f", color="#8a5a00", bold=True))

    # Стрілка переходу 2 -> 3
    frs.append(arrow(490, 110, 530, 110, color=POS, sw=2.2))
    frs.append(text(510, 95, "INT pin", size=10, color=POS, bold=True))

    # Правий блок: Стан 3 - Пробудження хоста
    frs.append(fitbox(530, 60, 190, 100,
                      "3. ПРОБУДЖЕННЯ МК\n(Active Processing)\n\n"
                      "• Сигнал на EXTI піні\n"
                      "• МК прокидається\n"
                      "• Зчитує джерело події\n"
                      "• Запускає радіо/алгоритм",
                      size=11, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # Зворотна стрілка очищення переривання
    frs.append(line(625, 160, 625, 210, color=MUTED, sw=1.5, dash="4 4"))
    frs.append(line(625, 210, 140, 210, color=MUTED, sw=1.5, dash="4 4"))
    frs.append(arrow(140, 210, 140, 160, color=MUTED, sw=1.5))
    frs.append(text(380, 200, "Читання регістру статусу (Clear Latch) → Повернення у сон",
                    size=10, color=MUTED))

    # Порівняльна таблиця типів переривань унизу
    frs.append(fitbox(40, 235, 680, 150,
                      "ПОРІВНЯННЯ ТИПІВ ПЕРЕРИВАНЬ ДАВАЧІВ:\n\n"
                      "• Data Ready (DRDY): Спрацьовує на КОЖЕН новий відлік АЦП. Застосування: потокова обробка, фільтрація, БПФ.\n"
                      "• Watermark / FIFO Full: Спрацьовує при накопиченні N відліків. Застосування: пакетна енергоефективна передача.\n"
                      "• Threshold / Any-Motion: Спрацьовує ЛИШЕ при перевищенні порогу прискорення/температури/тиску. "
                      "МК спить днями, доки об'єкт не зрушить з місця.\n"
                      "• Free-Fall / Significant Motion: Спеціалізовані апаратні конфігурації для реєстрації падіння або кроків.",
                      size=10, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "sensor-interrupt-fsm.svg"), W, H, *frs,
           title="Подійно-орієнтоване пробудження: ланцюг обробки від сну до реакції")


def main():
    fig_power_profiles()
    fig_oversampling_tradeoff()
    fig_fifo_burst()
    fig_event_wakeup_fsm()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
