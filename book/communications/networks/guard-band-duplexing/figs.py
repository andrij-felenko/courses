# -*- coding: utf-8 -*-
"""Фігури до теми «Захисні смуги і дуплекс» (FDD, TDD, Guard Bands, Duplex Gap, ACLR).
Запуск: python figs.py  → створює SVG у ./img/
Стиль та помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Додаткові кольори
TX_COLOR  = "#c0392b"  # червоний (Downlink / Tx високої потужності)
RX_COLOR  = "#2457d6"  # синій (Uplink / Rx чутливий прийом)
GAP_COLOR = "#e67e22"  # помаранчевий (захисний інтервал / смуга)
SPEC_MASK = "#8e44ad"  # фіолетовий (спектральна маска)

def svg_path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    d_dash = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d_dash}/>'

# ── 1. Порівняння принципів FDD та TDD ────────────────────────────────────────
def fig_duplex_fdd_vs_tdd():
    W, H = 840, 480
    f = [text(W / 2, 26, "Частотний (FDD) та часовий (TDD) дуплекс", size=16, bold=True)]

    # Лівий блок: FDD (Frequency Division Duplexing)
    f.append(rect(20, 50, 390, 350, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(215, 76, "FDD: Розділення за частотою", size=14, bold=True, color=POS))
    f.append(text(215, 96, "Парний спектр: одночасна неперервна передача й прийом", size=10, color=MUTED))

    # Спектральна вісь FDD
    f.append(line(45, 160, 385, 160, color=LINE, sw=1.5))
    f.append(arrow(360, 160, 390, 160, color=LINE, sw=1.5))
    f.append(text(380, 178, "f", size=12, bold=True, color=LINE))

    # Смуги UL, Gap, DL
    f.append(rect(60, 120, 95, 40, fill="#eaf0fd", stroke=RX_COLOR, sw=1.8, rx=4))
    f.append(text(107, 145, "Uplink (UL)", size=11, bold=True, color=RX_COLOR))

    f.append(rect(160, 128, 90, 32, fill="#fef5e7", stroke=GAP_COLOR, sw=1.5, rx=3))
    f.append(text(205, 148, "Duplex Gap", size=10, bold=True, color=GAP_COLOR))

    f.append(rect(255, 120, 95, 40, fill="#fdecea", stroke=TX_COLOR, sw=1.8, rx=4))
    f.append(text(302, 145, "Downlink (DL)", size=11, bold=True, color=TX_COLOR))

    # Часова діаграма FDD
    f.append(line(45, 260, 385, 260, color=LINE, sw=1.5))
    f.append(arrow(360, 260, 390, 260, color=LINE, sw=1.5))
    f.append(text(380, 278, "t", size=12, bold=True, color=LINE))

    f.append(rect(60, 205, 300, 24, fill="#fdecea", stroke=TX_COLOR, sw=1.5, rx=3))
    f.append(text(210, 221, "Downlink Tx: неперервний потік у часі", size=10, bold=True, color=TX_COLOR))

    f.append(rect(60, 233, 300, 24, fill="#eaf0fd", stroke=RX_COLOR, sw=1.5, rx=3))
    f.append(text(210, 249, "Uplink Rx: неперервний потік у часі", size=10, bold=True, color=RX_COLOR))

    # Характеристики FDD
    f.append(fitbox(35, 290, 360, 95,
                    "• Потрібен ВЧ-дуплексер (ізоляція Tx/Rx > 50 дБ)\n"
                    "• Симетричний парний спектр (наприклад, 2×20 МГц)\n"
                    "• Мінімальна детермінована затримка (RTT)\n"
                    "• Неможливо динамічно перерозподілити смугу DL/UL",
                    size=10, fill="#f8fafc", stroke=MUTED))

    # Правий блок: TDD (Time Division Duplexing)
    f.append(rect(430, 50, 390, 350, fill="#fdfefe", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(625, 76, "TDD: Розділення за часом", size=14, bold=True, color=NEG))
    f.append(text(625, 96, "Непарний спектр: спільна смуга, чергування слотів", size=10, color=MUTED))

    # Спектральна вісь TDD
    f.append(line(455, 160, 795, 160, color=LINE, sw=1.5))
    f.append(arrow(770, 160, 800, 160, color=LINE, sw=1.5))
    f.append(text(790, 178, "f", size=12, bold=True, color=LINE))

    f.append(rect(510, 120, 230, 40, fill="#edf2f7", stroke=INK, sw=1.8, rx=4))
    f.append(text(625, 145, "Єдина спільна смуга f_0 (DL + UL)", size=11, bold=True, color=INK))

    # Часова діаграма TDD
    f.append(line(455, 260, 795, 260, color=LINE, sw=1.5))
    f.append(arrow(770, 260, 800, 260, color=LINE, sw=1.5))
    f.append(text(790, 278, "t", size=12, bold=True, color=LINE))

    # Слоти DL, GP, UL
    f.append(rect(470, 210, 105, 45, fill="#fdecea", stroke=TX_COLOR, sw=1.5, rx=3))
    f.append(text(522, 237, "DL (Tx)", size=11, bold=True, color=TX_COLOR))

    f.append(rect(578, 210, 38, 45, fill="#fef5e7", stroke=GAP_COLOR, sw=1.5, rx=3))
    f.append(text(597, 237, "GP", size=10, bold=True, color=GAP_COLOR))

    f.append(rect(619, 210, 65, 45, fill="#eaf0fd", stroke=RX_COLOR, sw=1.5, rx=3))
    f.append(text(651, 237, "UL (Rx)", size=11, bold=True, color=RX_COLOR))

    f.append(rect(687, 210, 95, 45, fill="#fdecea", stroke=TX_COLOR, sw=1.5, rx=3))
    f.append(text(734, 237, "DL (Tx)", size=11, bold=True, color=TX_COLOR))

    # Характеристики TDD
    f.append(fitbox(445, 290, 360, 95,
                    "• Замість дуплексера — швидкий комутатор SPDT\n"
                    "• Гнучка асиметрія трафіку (наприклад, 4:1 DL/UL)\n"
                    "• Взаємність каналу (Reciprocity) для Massive MIMO\n"
                    "• Вимагає суворої фазової синхронізації базових станцій",
                    size=10, fill="#f8fafc", stroke=MUTED))

    # Підсумкова картка знизу
    f.append(fitbox(20, 415, 800, 50,
                    "FDD забезпечує ізоляцію дуплексним розносом частот і фільтрами, працюючи без пауз.\n"
                    "TDD економить спектр і апаратуру, розділяючи передачу й прийом захисними інтервалами GP у часі.",
                    size=11, fill="#fcfcfd", stroke=INK))

    render(os.path.join(IMG, "duplex-fdd-vs-tdd.svg"), W, H, *f)


# ── 2. Захисні смуги, спад фільтра, маска спектра (ACLR / OOBE) ───────────────
def fig_guard_bands_spectral_mask():
    W, H = 840, 440
    f = [text(W / 2, 26, "Захисні смуги (Guard Bands), позасмугові випромінювання та ACLR", size=16, bold=True)]

    # Вісь координат спектра
    f.append(line(50, 340, 790, 340, color=LINE, sw=1.5))
    f.append(arrow(760, 340, 795, 340, color=LINE, sw=1.5))
    f.append(text(790, 358, "Частота (f)", size=11, bold=True, color=LINE))

    f.append(line(50, 340, 50, 60, color=LINE, sw=1.5))
    f.append(arrow(50, 80, 50, 55, color=LINE, sw=1.5))
    f.append(text(45, 50, "PSD (дБм/Гц)", size=11, bold=True, color=LINE, anchor="start"))

    # Основний канал: Зайнята смуга (Occupied Bandwidth)
    f.append(rect(240, 90, 320, 250, fill="#eaf2f8", stroke="#2980b9", sw=1.5, rx=2))
    f.append(text(400, 115, "Корисний сигнал (Зайнята смуга / OBW)", size=12, bold=True, color="#1b4f72"))
    f.append(text(400, 133, "наприклад, 100 піднесучих OFDM (18 МГц із 20 МГц каналу)", size=10, color=MUTED))

    # Спектральна маска випромінювання (SEM - Spectral Emission Mask)
    f.append(line(70, 290, 180, 290, color=SPEC_MASK, sw=2, dash="4,3"))
    f.append(line(180, 290, 230, 80, color=SPEC_MASK, sw=2, dash="4,3"))
    f.append(line(230, 80, 570, 80, color=SPEC_MASK, sw=2, dash="4,3"))
    f.append(line(570, 80, 620, 290, color=SPEC_MASK, sw=2, dash="4,3"))
    f.append(line(620, 290, 760, 290, color=SPEC_MASK, sw=2, dash="4,3"))
    f.append(text(500, 72, "Спектральна маска (SEM)", size=10, bold=True, color=SPEC_MASK))

    # Захисні смуги (Guard Bands) ліворуч і праворуч від корисного сигналу
    f.append(rect(190, 140, 50, 200, fill="#fef5e7", stroke=GAP_COLOR, sw=1.5, rx=2))
    f.append(text(215, 230, "Guard", size=10, bold=True, color=GAP_COLOR))
    f.append(text(215, 245, "Band", size=10, bold=True, color=GAP_COLOR))

    f.append(rect(560, 140, 50, 200, fill="#fef5e7", stroke=GAP_COLOR, sw=1.5, rx=2))
    f.append(text(585, 230, "Guard", size=10, bold=True, color=GAP_COLOR))
    f.append(text(585, 245, "Band", size=10, bold=True, color=GAP_COLOR))

    # Межі номінального каналу (Channel Bandwidth = 20 MHz)
    f.append(line(190, 85, 190, 340, color=MUTED, sw=1, dash="3,3"))
    f.append(line(610, 85, 610, 340, color=MUTED, sw=1, dash="3,3"))
    f.append(line(190, 355, 610, 355, color=INK, sw=1.5))
    f.append(text(400, 370, "Номінальна смуга каналу (Channel Bandwidth, наприклад 20 МГц)", size=10, bold=True, color=INK))

    # Сусідній канал (Adjacent Channel) праворуч
    f.append(rect(630, 220, 130, 120, fill="#fdedec", stroke=POS, sw=1.2, rx=3))
    f.append(text(695, 255, "Сусідній канал", size=11, bold=True, color=POS))
    f.append(text(695, 272, "(Інший оператор)", size=10, color=MUTED))

    # Стрілка нелінійного просочування (ACLR / OOBE)
    f.append(arrow(580, 200, 640, 240, color=POS, sw=2))
    f.append(text(655, 195, "OOBE / Спад", size=10, bold=True, color=POS))

    # Визначення ACLR картка
    f.append(fitbox(50, 385, 740, 48,
                    "ACLR = P_корисного_каналу / P_витоку_в_сусідній_канал (норматив 3GPP: ACLR ≥ 45 дБ).\n"
                    "Захисна смуга (Guard Band) дає аналоговим і цифровим фільтрам смугу переходу для згасання OOBE.",
                    size=10, fill="#fcfcfd", stroke=MUTED))

    render(os.path.join(IMG, "guard-bands-spectral-mask.svg"), W, H, *f)


# ── 3. Часове вирівнювання (Timing Advance) та захисний інтервал (GP) у TDD ───
def fig_tdd_timing_advance_guard_period():
    W, H = 840, 470
    f = [text(W / 2, 26, "Геометрія поширення хвилі, Timing Advance та захисний період (GP)", size=16, bold=True)]

    # Блок базової станції (gNB)
    f.append(rect(30, 55, 780, 135, fill="#fcfdfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(50, 78, "Часова шкала базової станції (gNB)", size=12, bold=True, color=TX_COLOR, anchor="start"))

    # Вісь часу gNB
    f.append(line(60, 135, 770, 135, color=LINE, sw=1.5))
    f.append(arrow(740, 135, 775, 135, color=LINE, sw=1.5))
    f.append(text(770, 153, "t", size=11, bold=True, color=LINE))

    # Слоти на gNB
    f.append(rect(60, 95, 240, 40, fill="#fdecea", stroke=TX_COLOR, sw=1.8, rx=4))
    f.append(text(180, 120, "DL Передача (Tx)", size=12, bold=True, color=TX_COLOR))

    # Захисний інтервал GP на gNB
    f.append(rect(300, 95, 160, 40, fill="#fef5e7", stroke=GAP_COLOR, sw=1.8, rx=4))
    f.append(text(380, 114, "Guard Period (GP)", size=11, bold=True, color=GAP_COLOR))
    f.append(text(380, 128, "GP ≥ 2·d_max/c + T_switch", size=9, bold=True, color=INK))

    # UL Слот на gNB
    f.append(rect(460, 95, 240, 40, fill="#eaf0fd", stroke=RX_COLOR, sw=1.8, rx=4))
    f.append(text(580, 120, "UL Прийом (Rx від усіх UE)", size=12, bold=True, color=RX_COLOR))

    # Блок термінала на краю стільника (Edge UE)
    f.append(rect(30, 210, 780, 135, fill="#fcfdfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(50, 233, "Часова шкала мобільного термінала (Edge UE, відстань d_max)", size=12, bold=True, color=RX_COLOR, anchor="start"))

    # Вісь часу UE
    f.append(line(60, 290, 770, 290, color=LINE, sw=1.5))
    f.append(arrow(740, 290, 775, 290, color=LINE, sw=1.5))
    f.append(text(770, 308, "t", size=11, bold=True, color=LINE))

    # Затримка прибуття DL до UE: tau = d/c
    f.append(rect(140, 250, 220, 40, fill="#fdecea", stroke=TX_COLOR, sw=1.5, rx=4))
    f.append(text(250, 275, "DL Прийом (Rx, затримка τ)", size=11, bold=True, color=TX_COLOR))

    # Позначення затримки поширення DL
    f.append(line(60, 135, 140, 250, color=TX_COLOR, sw=1.5, dash="3,3"))
    f.append(line(300, 135, 360, 250, color=TX_COLOR, sw=1.5, dash="3,3"))
    f.append(rect(75, 185, 125, 24, fill="#ffffff", stroke=TX_COLOR, sw=1, rx=3))
    f.append(text(137, 201, "Затримка τ = d/c", size=10, bold=True, color=TX_COLOR))

    # Час перемикання UE Rx->Tx
    f.append(rect(360, 250, 45, 40, fill="#e2e8f0", stroke=MUTED, sw=1, rx=2))
    f.append(text(382, 275, "Rx/Tx", size=10, bold=True, color=MUTED))

    # UL передача з випередженням (Timing Advance)
    f.append(rect(405, 250, 240, 40, fill="#eaf0fd", stroke=RX_COLOR, sw=1.8, rx=4))
    f.append(text(525, 275, "UL Tx (з випередженням TA = 2τ)", size=10, bold=True, color=RX_COLOR))

    # Позначення затримки прибуття UL до gNB
    f.append(line(405, 250, 460, 135, color=RX_COLOR, sw=1.5, dash="3,3"))
    f.append(rect(435, 185, 125, 24, fill="#ffffff", stroke=RX_COLOR, sw=1, rx=3))
    f.append(text(497, 201, "Затримка τ = d/c", size=10, bold=True, color=RX_COLOR))

    # Пояснення знизу
    f.append(fitbox(30, 365, 780, 85,
                    "Механізм: термінал надсилає сигнал раніше на час TA = 2·d/c, щоб його пакет прибув на базову станцію синхронно з іншими.\n"
                    "Захисний період GP на gNB гарантує, що останні відлуння DL згасли і приймач встиг перемкнутися до прибуття першого UL-пакета.\n"
                    "Максимальний радіус стільника R_max обмежується тривалістю GP: R_max ≈ c · (GP - T_switch) / 2.",
                    size=10, fill="#f8fafc", stroke=MUTED))

    render(os.path.join(IMG, "tdd-timing-advance-guard-period.svg"), W, H, *f)


# ── 4. АЧХ та розв'язка радіочастотного дуплексера ─────────────────────────────
def fig_duplexer_isolation_response():
    W, H = 840, 440
    f = [text(W / 2, 26, "Амплітудно-частотна характеристика та розв'язка ВЧ-дуплексера (FDD)", size=16, bold=True)]

    # Вісь координат
    f.append(line(60, 330, 780, 330, color=LINE, sw=1.5))
    f.append(arrow(750, 330, 785, 330, color=LINE, sw=1.5))
    f.append(text(780, 348, "Частота (f)", size=11, bold=True, color=LINE))

    f.append(line(60, 330, 60, 50, color=LINE, sw=1.5))
    f.append(arrow(60, 70, 60, 45, color=LINE, sw=1.5))
    f.append(text(55, 40, "Коефіцієнт передачі |S_ij| (дБ)", size=11, bold=True, color=LINE, anchor="start"))

    # Сітка дБ
    for y_val, label in [(80, "0 дБ (пропускання)"), (150, "-20 дБ"), (220, "-40 дБ"), (290, "-60 дБ (ізоляція)")]:
        f.append(line(60, y_val, 770, y_val, color="#e2e8f0", sw=1, dash="2,2"))
        f.append(text(52, y_val + 4, label, size=9, color=MUTED, anchor="end"))

    # Tx смуговий фільтр (червоний, S21: Tx -> Ant)
    f.append(svg_path("M 80,310 L 150,300 L 190,85 L 290,85 L 330,300 L 760,310", fill="none", stroke=TX_COLOR, sw=2.5))
    f.append(text(240, 70, "Смуга Tx (|S_21|)", size=11, bold=True, color=TX_COLOR))

    # Rx смуговий фільтр (синій, S31: Ant -> Rx)
    f.append(svg_path("M 80,310 L 510,310 L 550,85 L 650,85 L 690,300 L 760,310", fill="none", stroke=RX_COLOR, sw=2.5))
    f.append(text(600, 70, "Смуга Rx (|S_31|)", size=11, bold=True, color=RX_COLOR))

    # Дуплексний рознос (Duplex Gap)
    f.append(rect(330, 85, 180, 225, fill="#fef5e7", stroke=GAP_COLOR, sw=1.5, rx=3))
    f.append(text(420, 180, "Дуплексний рознос", size=12, bold=True, color=GAP_COLOR))
    f.append(text(420, 198, "(Duplex Gap / Δf)", size=11, bold=True, color=GAP_COLOR))
    f.append(text(420, 218, "Зона перехідного спаду фільтрів", size=9, color=MUTED))

    # Стрілка ізоляції між Tx та Rx
    f.append(arrow(600, 100, 600, 290, color=POS, sw=2))
    f.append(text(660, 200, "Ізоляція Tx→Rx", size=10, bold=True, color=POS))
    f.append(text(660, 215, "> 50..60 дБ", size=11, bold=True, color=POS))

    # Пояснювальний блок
    f.append(fitbox(60, 360, 720, 65,
                    "Дуплексер захищає надчутливий малошумний підсилювач (LNA) приймача від вигорання та блокування\n"
                    "потужним сигналом власного передавача (+30..+46 дБм). Чим менший дуплексний рознос Δf, тим вищий\n"
                    "порядок фільтрів (SAW/BAW або об'ємних резонаторів) і тим більші втрати на внесення (Insertion Loss).",
                    size=10, fill="#f8fafc", stroke=MUTED))

    render(os.path.join(IMG, "duplexer-isolation-response.svg"), W, H, *f)


if __name__ == "__main__":
    fig_duplex_fdd_vs_tdd()
    fig_guard_bands_spectral_mask()
    fig_tdd_timing_advance_guard_period()
    fig_duplexer_isolation_response()
    print("Усі 4 фігури успішно згенеровано у ./img/")
