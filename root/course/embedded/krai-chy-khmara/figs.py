# -*- coding: utf-8 -*-
"""Фігури для статті krai-chy-khmara («Край чи хмара: що рахувати на місці»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_tradeoff_quadrant():
    W, H = 820, 420
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "Тріумвірат обмежень: чому розподіл обов'язків є фізичною необхідністю", size=15, bold=True))

    # Ліва половина: Край (Edge)
    p.append(rect(30, 55, 365, 335, fill="#f8fafc", stroke="#2563eb", sw=1.8, rx=8))
    p.append(text(212, 85, "КРАЙ (Локальний вузол / MCU)", size=14, color="#1e40af", bold=True))

    # Картки на Краю
    b1, _, _ = textbox(212, 130, "Затримка 1–10 мс: детерміновані замкнені контури\n(ПІД-регулятори, аварійна зупинка, ШІМ двигуна)", size=11, color=INK, fill="#eff6ff", stroke="#93c5fd", min_w=335)
    p.append(b1)

    b2, _, _ = textbox(212, 195, "Енергетична вигода: мікроконтролер витрачає\nнаноджоулі на інструкцію в режимі сну та обробки", size=11, color=INK, fill="#eff6ff", stroke="#93c5fd", min_w=335)
    p.append(b2)

    b3, _, _ = textbox(212, 260, "Первинна компресія: фільтрація шумів, FFT,\nвідсікання надлишкових 99.9% сирих вибірок датчика", size=11, color=INK, fill="#eff6ff", stroke="#93c5fd", min_w=335)
    p.append(b3)

    b4, _, _ = textbox(212, 330, "Повна автономність: робота без доступу до інтернету,\nконфіденційність сирих чутливих даних на місці", size=11, color=INK, fill="#eff6ff", stroke="#93c5fd", min_w=335)
    p.append(b4)

    # Права половина: Хмара (Cloud Backend)
    p.append(rect(425, 55, 365, 335, fill="#fdfbf7", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(607, 85, "ХМАРА (Серверний бекенд / Fleet)", size=14, color="#b45309", bold=True))

    # Картки в Хмарі
    c1, _, _ = textbox(607, 130, "Макроаналіз парку: крос-кореляція тисяч вузлів,\nвиявлення глобальних тенденцій деградації обладнання", size=11, color=INK, fill="#fef3c7", stroke="#fcd34d", min_w=335)
    p.append(c1)

    c2, _, _ = textbox(607, 195, "Машинне навчання: важке навчання моделей,\nкластеризація та оновлення профілів для вузлів", size=11, color=INK, fill="#fef3c7", stroke="#fcd34d", min_w=335)
    p.append(c2)

    c3, _, _ = textbox(607, 260, "Довготривалий архів: гігабайти історичних зведень,\nюридичний аудит, звітність за місяці й роки", size=11, color=INK, fill="#fef3c7", stroke="#fcd34d", min_w=335)
    p.append(c3)

    c4, _, _ = textbox(607, 330, "Глобальне керування: бізнес-панелі оператора,\nоновлення прошивок по повітрю (FOTA), білінг", size=11, color=INK, fill="#fef3c7", stroke="#fcd34d", min_w=335)
    p.append(c4)

    # Зв'язок між ними
    p.append(arrow(395, 222, 425, 222, color=LINE, sw=2.0))
    p.append(arrow(425, 238, 395, 238, color=MUTED, sw=1.5))
    p.append(text(410, 212, "події", size=10, color=LINE, bold=True))
    p.append(text(410, 253, "моделі", size=10, color=MUTED))

    render(os.path.join(OUT, "tradeoff-quadrant.svg"), W, H, *p)


def fig_energy_silicon_vs_radio():
    W, H = 800, 360
    p = []

    p.append(text(W / 2, 26, "Енергетична прірва: обчислення на кремнії проти радіоефіру", size=15, bold=True))

    ox = 210
    bars = [
        ("1 000 інструкцій Cortex-M4", 0.0003, "0.0003 мкДж (30 пДж/інструкція)", FIELD, 65),
        ("1 000 000 інструкцій (FFT 1024)", 0.3, "0.3 мкДж (300 нДж на обчислення)", FIELD, 105),
        ("Передача 1 кБ: BLE 5.0 (2 Мбіт/с)", 25.0, "25 мкДж (TX @ 0 dBm)", "#2563eb", 155),
        ("Передача 1 кБ: Wi-Fi 802.11n", 120.0, "120 мкДж (TX @ 15 dBm)", "#2563eb", 195),
        ("Передача 1 кБ: LoRaWAN (SF7)", 850.0, "850 мкДж (TX @ 14 dBm)", POS, 245),
        ("Передача 1 кБ: LTE-M / NB-IoT", 3500.0, "3 500 мкДж (TX @ 23 dBm + синхронізація)", POS, 285),
    ]

    # Шкала внизу (логарифмічна візуалізація)
    p.append(line(ox, 48, ox, 310, color=LINE, sw=1.5))
    p.append(line(ox, 310, ox + 540, 310, color=LINE, sw=1.5))
    p.append(text(ox + 540, 328, "Енергія на операцію (логарифмічна шкала)", size=11, color=MUTED, anchor="end"))

    # Стовпчики
    import math
    for label, val, note, col, y in bars:
        p.append(text(ox - 10, y + 10, label, size=11, color=INK, anchor="end", bold=True))
        # log scale mapping for visual width: 0.0001 -> 15px, 10000 -> 500px
        log_val = math.log10(val)  # from -3.5 to +3.5
        w_bar = max(12, min(500, int((log_val + 4.0) / 7.5 * 500)))
        p.append(rect(ox + 2, y - 4, w_bar, 20, fill=col, stroke=col, sw=1.0, rx=3))
        p.append(text(ox + w_bar + 8, y + 10, note, size=10, color=INK, anchor="start"))

    p.append(text(W / 2, 348, "Висновок: обчислити повне віконне FFT на кристалі у сотні разів дешевше, ніж передати сирий масив у радіоефір", size=11, color=POS, bold=True, italic=True))

    render(os.path.join(OUT, "energy-silicon-vs-radio.svg"), W, H, *p)


def fig_edge_pipeline_flow():
    W, H = 840, 330
    p = []

    p.append(text(W / 2, 24, "Архітектура бортового конвеєра: від сирого сигналу до адаптивної передачі", size=14, bold=True))

    # Крок 1: Датчик
    b1, w1, h1 = textbox(95, 80, "Сенсорний потік\n(ADC @ 10 кГц,\nвібрація, струм)", size=11, fill="#f1f5f9", stroke="#64748b", min_w=140)
    p.append(b1)

    # Крок 2: Локальний контур
    b2, w2, h2 = textbox(275, 80, "Локальний контур\n(1–5 мс: ПІД, захист,\nаварійне реле)", size=11, fill="#eff6ff", stroke="#3b82f6", min_w=150)
    p.append(b2)
    p.append(arrow(95 + w1 / 2, 80, 275 - w2 / 2, 80, color=LINE, sw=1.8))

    # Дія на привід
    p.append(arrow(275, 80 + h2 / 2, 275, 175, color=POS, sw=1.8))
    b_act, _, _ = textbox(275, 195, "Виконавчий орган\n(ШІМ, контактор, гальмо)", size=10, fill="#fee2e2", stroke=POS, min_w=150)
    p.append(b_act)

    # Крок 3: Статистична обробка
    b3, w3, h3 = textbox(475, 80, "Фільтр Велфорда\n(Біжуче середнє μ,\nдисперсія σ², Z-score)", size=11, fill="#ecfdf5", stroke="#10b981", min_w=150)
    p.append(b3)
    p.append(arrow(275 + w2 / 2, 80, 475 - w3 / 2, 80, color=LINE, sw=1.8))

    # Крок 4: Кільцевий буфер передісторії
    b_buf, _, _ = textbox(475, 195, "Кільцевий RAM-буфер\n(знімок останніх 5 сек)", size=10, fill="#fefce8", stroke="#eab308", min_w=150)
    p.append(b_buf)
    p.append(arrow(475, 80 + h3 / 2, 475, 195 - 20, color=LINE, sw=1.5))

    # Крок 5: Детектор та адаптивний вибір
    b4, w4, h4 = textbox(695, 80, "Адаптивний диспетчер\n(Поріг аномалії\n|x − μ| > 3σ)", size=11, fill="#fef3c7", stroke="#f59e0b", min_w=150)
    p.append(b4)
    p.append(arrow(475 + w3 / 2, 80, 695 - w4 / 2, 80, color=LINE, sw=1.8))

    # Вихід на радіо
    b_out1, _, _ = textbox(695, 195, "Аномалія: терміновий пакет\n+ знімок з RAM-буфера", size=10, color=POS, fill="#fef2f2", stroke=POS, bold=True, min_w=180)
    p.append(b_out1)
    p.append(arrow(695, 80 + h4 / 2, 695, 195 - 20, color=POS, sw=1.8))

    b_out2, _, _ = textbox(695, 275, "Норма: Deadband-компресія\n(зведення 1 раз на годину)", size=10, color=FIELD, fill="#f0fdf4", stroke=FIELD, min_w=180)
    p.append(b_out2)
    p.append(arrow(695, 195 + 20, 695, 275 - 20, color=FIELD, sw=1.5))

    render(os.path.join(OUT, "edge-pipeline-flow.svg"), W, H, *p)


if __name__ == "__main__":
    fig_tradeoff_quadrant()
    fig_energy_silicon_vs_radio()
    fig_edge_pipeline_flow()
    print("SVG figures generated successfully.")
