# -*- coding: utf-8 -*-
"""Генератор фігур для теми radioslid-prystroiu (Радіослід пристрою: як його знаходять)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. unintended-emissions-sources: Джерела ненавмисного радіовипромінювання на друкованій платі ──
def fig_unintended_emissions():
    W, H = 860, 520
    p = []

    # Заголовок блоку друкованої плати
    p.append(fitbox(30, 20, 800, 480, "", fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(430, 45, "Джерела ненавмисного електромагнітного випромінювання на друкованій платі (PCB)", size=13, bold=True))

    # 1. Дерево тактування
    b1 = fitbox(50, 70, 360, 190, 
                "1. Тактовий генератор та дерево PLL\n"
                "• Кварцовий резонатор (16-50 МГц) + PLL (до 1-2 ГГц)\n"
                "• Прямокутні імпульси генерують непарні гармоніки f_n = (2n+1)·f0\n"
                "• Високий dV/dt (фронти < 1 нс) збуджує паразитні ємності\n"
                "• Довгі тактові доріжки працюють як мікросмужкові антени\n"
                "• Випромінювання: вузькосмугові піки на кратних частотах",
                size=10, fill="#ffffff", stroke=POS, sw=1.5)
    p.append(b1)

    # 2. DC-DC перетворювач
    b2 = fitbox(450, 70, 360, 190,
                "2. Імпульсний перетворювач DC-DC (Buck / Boost)\n"
                "• Комутація силових MOSFET на частотах 100 кГц – 3 МГц\n"
                "• Струмові сплески di/dt > 1 А/нс у вузлі комутації (SW node)\n"
                "• Паразитний дзвін (ringing) індуктивності L і ємності C на 50-300 МГц\n"
                "• Магнітна петля між транзистором і діодом випромінює H-поле\n"
                "• Випромінювання: широкий гребінець гармонік у КХ/УКХ",
                size=10, fill="#ffffff", stroke=POS, sw=1.5)
    p.append(b2)

    # 3. Швидкісні шини
    b3 = fitbox(50, 280, 360, 200,
                "3. Швидкісні цифрові шини (SPI / QSPI / SDIO / DDR)\n"
                "• Частоти передачі даних: 40 МГц – 400+ МГц\n"
                "• Невідповідність хвильового опору траси (Z0 ≠ 50 Ом) -> відбиття\n"
                "• Спільний струм повернення через земляну площину (Ground Bounce)\n"
                "• Спектр модулюється даними: кореляція з оброблюваною інструкцією\n"
                "• TEMPEST-загроза: витік відкритого тексту шин безпосередньо в ефір",
                size=10, fill="#ffffff", stroke=NEG, sw=1.5)
    p.append(b3)

    # 4. GPIO та лінії інтерфейсів
    b4 = fitbox(450, 280, 360, 200,
                "4. Комутація GPIO та підключені кабелі\n"
                "• Перемикання виводів мікроконтролера з крутими фронтами\n"
                "• Кабелі живлення, датчиків та шлейфи діють як несиметричні диполі\n"
                "• Синфазні струми (Common-Mode Current) I_cm у земляній петлі\n"
                "• Навіть струм I_cm = 5-10 мкА створює помітний сигнал за 30-50 м\n"
                "• Випромінювання: квазіперіодичні спалахи під час активності ядра",
                size=10, fill="#ffffff", stroke=NEG, sw=1.5)
    p.append(b4)

    render(os.path.join(OUT, "unintended-emissions-sources.svg"), W, H, *p)


# ── 2. rf-fingerprint-constellation: Кремнієва сигнатура та неідеальності радіотракту ──
def fig_rf_fingerprint():
    W, H = 860, 480
    p = []

    # Ліва панель: Ідеальний передавач
    p.append(rect(40, 30, 370, 420, fill="#ffffff", stroke=MUTED, sw=1.4))
    p.append(text(225, 60, "Ідеальний передавач (Математична модель)", size=12, bold=True, color=FIELD))
    p.append(line(225, 90, 225, 330, color=MUTED, sw=1.0, dash="4,4"))
    p.append(line(85, 210, 365, 210, color=MUTED, sw=1.0, dash="4,4"))
    p.append(text(360, 202, "I (In-phase)", size=9, color=MUTED, anchor="end"))
    p.append(text(235, 100, "Q (Quadrature)", size=9, color=MUTED, anchor="start"))

    # 4 ідеальні точки QPSK
    pts_ideal = [(155, 140), (295, 140), (155, 280), (295, 280)]
    for x, y in pts_ideal:
        p.append(circle(x, y, 7, fill="#27ae60", stroke="#1e824c", sw=2))

    p.append(fitbox(55, 350, 340, 85,
                    "• Амплітуди I та Q строго рівні (alpha = 1.0)\n"
                    "• Фазовий зсув строго 90 градусів (phi = 0.0)\n"
                    "• Несуча частота збігається точно (CFO = 0 Гц)\n"
                    "• Відсутній фазовий шум PLL (точкові скупчення)",
                    size=9, fill="#f4fbf7", stroke=FIELD, sw=1.2))

    # Права панель: Реальний передавач із сигнатурою
    p.append(rect(450, 30, 370, 420, fill="#ffffff", stroke=MUTED, sw=1.4))
    p.append(text(635, 60, "Реальний кремній (Унікальний RF-відбиток)", size=12, bold=True, color=POS))
    p.append(line(635, 90, 635, 330, color=MUTED, sw=1.0, dash="4,4"))
    p.append(line(495, 210, 775, 210, color=MUTED, sw=1.0, dash="4,4"))
    p.append(text(770, 202, "I", size=9, color=MUTED, anchor="end"))
    p.append(text(645, 100, "Q", size=9, color=MUTED, anchor="start"))

    # 4 деформовані хмари точок реального передавача (IQ imbalance + CFO + Phase Noise)
    clouds = [
        (560, 130), (715, 150), (550, 270), (705, 290)
    ]
    for cx, cy in clouds:
        p.append(circle(cx, cy, 18, fill="#fdecea", stroke=POS, sw=1.2))
        p.append(circle(cx + 3, cy - 2, 4, fill=POS, stroke="#922b21", sw=1.5))
        p.append(circle(cx - 4, cy + 3, 3, fill=POS, stroke="#922b21", sw=1))
        p.append(circle(cx + 6, cy + 4, 3, fill=POS, stroke="#922b21", sw=1))
        p.append(circle(cx - 5, cy - 4, 3, fill=POS, stroke="#922b21", sw=1))

    # Позначки неідеальностей
    p.append(arrow(635, 210, 645, 195, color=POS, sw=1.5))
    p.append(text(652, 190, "Зсув нуля (DC-offset / LO leakage)", size=9, color=POS, bold=True, anchor="start"))

    p.append(fitbox(465, 350, 340, 85,
                    "• Дисбаланс гілок IQ: alpha ≠ 1.0 (масштаб), phi ≠ 0° (перекіс)\n"
                    "• CFO (зсув кварцу): обертання сузір'я зі швидкістю Delta_f\n"
                    "• Фазовий шум генератора: дугоподібне розмиття точок\n"
                    "• Нелінійність PA (AM/AM, AM/PM): спотворення крайових точок",
                    size=9, fill="#fdf2f2", stroke=POS, sw=1.2))

    render(os.path.join(OUT, "rf-fingerprint-constellation.svg"), W, H, *p)


# ── 3. tdoa-hyperbolic-localization: Різницево-далекомірна пеленгація TDoA ──
def fig_tdoa_localization():
    W, H = 860, 500
    p = []

    # Загальна рамка картини пеленгації
    p.append(rect(30, 20, 800, 460, fill="#fcfcfd", stroke=MUTED, sw=1.4))
    p.append(text(430, 45, "Принцип TDoA-пеленгації: перетин різницево-часових гіпербол", size=13, bold=True))

    # Базові станції (сенсори) A, B, C
    # Сенсор A
    p.append(circle(120, 160, 14, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(120, 165, "S1", size=11, bold=True, color=NEG))
    p.append(text(120, 190, "Станція 1 (t1)", size=10, bold=True, color=INK))

    # Сенсор B
    p.append(circle(720, 140, 14, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(720, 145, "S2", size=11, bold=True, color=NEG))
    p.append(text(720, 170, "Станція 2 (t2)", size=10, bold=True, color=INK))

    # Сенсор C
    p.append(circle(410, 410, 14, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(410, 415, "S3", size=11, bold=True, color=NEG))
    p.append(text(410, 440, "Станція 3 (t3)", size=10, bold=True, color=INK))

    # Ціль / Передавач (Tx)
    tx_x, tx_y = 360, 220
    p.append(circle(tx_x, tx_y, 10, fill="#fdecea", stroke=POS, sw=2.5))
    p.append(text(tx_x, tx_y - 18, "ЦІЛЬ (Tx)", size=11, bold=True, color=POS))
    p.append(text(tx_x, tx_y + 24, "Координати (x, y)", size=9, bold=True, color=MUTED))

    # Радіопромені від Tx до станцій
    p.append(line(tx_x, tx_y, 120, 160, color=POS, sw=1.5, dash="5,4"))
    p.append(line(tx_x, tx_y, 720, 140, color=POS, sw=1.5, dash="5,4"))
    p.append(line(tx_x, tx_y, 410, 410, color=POS, sw=1.5, dash="5,4"))

    # Підписи відстаней
    p.append(text(230, 175, "d1 = c · t1", size=10, color=POS, italic=True))
    p.append(text(545, 165, "d2 = c · t2", size=10, color=POS, italic=True))
    p.append(text(410, 305, "d3 = c · t3", size=10, color=POS, italic=True))

    # Гіперболи
    p.append(line(310, 80, 400, 360, color=NEG, sw=2.0, dash="6,3"))
    p.append(text(300, 75, "Гіпербола Delta_t(S2 - S1)", size=10, color=NEG, bold=True))

    p.append(line(180, 290, 560, 160, color="#8e44ad", sw=2.0, dash="6,3"))
    p.append(text(570, 155, "Гіпербола Delta_t(S3 - S1)", size=10, color="#8e44ad", bold=True))

    # Пояснювальний блок знизу
    p.append(fitbox(50, 360, 260, 100,
                    "Вимога TDoA:\n"
                    "• Синхронізація сенсорів: GPS / PTP (<= 1 нс)\n"
                    "• Похибка часу 1 нс = похибка положення 30 см\n"
                    "• Взаємна кореляція (Cross-Correlation, GCC-PHAT)\n"
                    "• Мінімум 3 станції для 2D, 4 для 3D",
                    size=9, fill="#ffffff", stroke=MUTED, sw=1.2))

    p.append(fitbox(550, 360, 260, 100,
                    "Математична суть:\n"
                    "d_i - d_j = sqrt((x - x_i)^2 + (y - y_i)^2) -\n"
                    "            sqrt((x - x_j)^2 + (y - y_j)^2) = c·Delta_t_ij\n"
                    "Розв'язок: нелінійний МНК (Gauss-Newton) або\n"
                    "прямий алгебраїчний метод Чана (Chan's method)",
                    size=8.5, fill="#ffffff", stroke=MUTED, sw=1.2))

    render(os.path.join(OUT, "tdoa-hyperbolic-localization.svg"), W, H, *p)


# ── 4. lpi-lpd-techniques: Методи маскування радіовипромінювання (LPI/LPD) ──
def fig_lpi_lpd():
    W, H = 860, 480
    p = []

    p.append(rect(30, 20, 800, 440, fill="#fcfcfd", stroke=MUTED, sw=1.4))
    p.append(text(430, 45, "Методи зниження ймовірності перехоплення та виявлення (LPI / LPD)", size=13, bold=True))

    # 1. Пакетний режим (Burst Transmission)
    b1 = fitbox(50, 75, 360, 175,
                "1. Пакетний режим (Ultra-Short Burst)\n"
                "• Стиснення даних у часі: передача триває 0.5 – 5 мс\n"
                "• Рандомізація інтервалів передачі (Jittering) без регулярного циклу\n"
                "• Швидкісні приймачі РЕР мають кінцевий час переналаштування\n"
                "• Радіомовчання 99.9% часу роботи пристрою\n"
                "• Ефект: мінімізація часового вікна для пеленгації",
                size=9.5, fill="#ffffff", stroke=FIELD, sw=1.5)
    p.append(b1)

    # 2. Пряме розширення спектра DSSS
    b2 = fitbox(450, 75, 360, 175,
                "2. Пряме розширення спектра (DSSS)\n"
                "• Множення сигналу на псевдовипадкову послідовність (PN chip)\n"
                "• Спектр сигналу розширюється в десятки/сотні разів\n"
                "• Спектральна густина потужності падає нижче рівня шумів (SNR < 0 dB)\n"
                "• Детектор енергії бачить лише плоский білий шум\n"
                "• Відновлення сигналу можливе лише зі знанням точного PN-ключа",
                size=9.5, fill="#ffffff", stroke=FIELD, sw=1.5)
    p.append(b2)

    # 3. Стрибки по частоті FHSS
    b3 = fitbox(50, 265, 360, 175,
                "3. Псевдовипадкові стрибки частоти (FHSS)\n"
                "• Зміна несучої частоти сотні або тисячі разів на секунду\n"
                "• Псевдовипадковий закон переходів, узгоджений між Tx та Rx\n"
                "• Вузькосмуговий пеленгатор встигає зафіксувати лише поодинокі стрибки\n"
                "• Захист від зосереджених завад та класичних сканерів ефіру\n"
                "• Спільне використання з DSSS (гібрид DSSS/FHSS)",
                size=9.5, fill="#ffffff", stroke=NEG, sw=1.5)
    p.append(b3)

    # 4. Адаптивна потужність та екранування
    b4 = fitbox(450, 265, 360, 175,
                "4. Адаптивна потужність (TPC) та екранування\n"
                "• Closed-loop TPC: потужність знижується до мінімально достатньої\n"
                "• Контроль фронтів GPIO (Slew Rate Limiting): зрізання гармонік\n"
                "• Екрануючі кришки (RF Can Shields) над генераторами та DC-DC\n"
                "• Феритові фільтри на лініях живлення та розв'язка шарів PCB\n"
                "• Ефект: придушення ненавмисних витоків на 40-60 дБ",
                size=9.5, fill="#ffffff", stroke=NEG, sw=1.5)
    p.append(b4)

    render(os.path.join(OUT, "lpi-lpd-techniques.svg"), W, H, *p)


if __name__ == "__main__":
    fig_unintended_emissions()
    fig_rf_fingerprint()
    fig_tdoa_localization()
    fig_lpi_lpd()
    print("Всі фігури згенеровано успішно.")
