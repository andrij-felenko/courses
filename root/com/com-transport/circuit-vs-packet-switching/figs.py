# -*- coding: utf-8 -*-
"""Фігури до теми «Комутація каналів проти комутації пакетів».
Запуск: python figs.py -> генерує SVG у ./img/
Стиль і помічники — зі спільного svgkit (scripts/svgkit.py)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Порівняння концепцій (Circuit vs Packet Switching) ────────────────────
def fig_circuit_vs_packet_concept():
    W, H = 880, 540
    f = [text(W / 2, 24, "Фундаментальні концепції: комутація каналів проти комутації пакетів", size=15, bold=True)]

    # Верхня панель: Комутація каналів
    f.append(rect(20, 45, 840, 230, fill="#fcfdfe", stroke=LINE, sw=1.2))
    f.append(text(40, 70, "1. Комутація каналів (Circuit Switching — PSTN, TDM, оптичні лямбди)", size=12, bold=True, color=NEG, anchor="start"))

    # Вузли комутації каналів
    f.append(fitbox(40, 95, 100, 45, "Абонент A\n(Вхід)", size=11, bold=True, fill="#eef3ff", stroke=NEG))
    f.append(fitbox(210, 95, 110, 45, "Комутатор 1\n(Вузол S1)", size=11, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(390, 95, 110, 45, "Комутатор 2\n(Вузол S2)", size=11, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(570, 95, 110, 45, "Комутатор 3\n(Вузол S3)", size=11, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(740, 95, 100, 45, "Абонент B\n(Вихід)", size=11, bold=True, fill="#eef3ff", stroke=NEG))

    # Виділений суцільний фізичний канал
    f.append(line(140, 117, 210, 117, color=POS, sw=3.5))
    f.append(line(320, 117, 390, 117, color=POS, sw=3.5))
    f.append(line(500, 117, 570, 117, color=POS, sw=3.5))
    f.append(line(680, 117, 740, 117, color=POS, sw=3.5))
    f.append(arrow(140, 117, 180, 117, color=POS, sw=3.5))
    f.append(arrow(320, 117, 360, 117, color=POS, sw=3.5))
    f.append(arrow(500, 117, 540, 117, color=POS, sw=3.5))
    f.append(arrow(680, 117, 715, 117, color=POS, sw=3.5))

    # Пояснення характеристик каналу
    f.append(fitbox(40, 155, 800, 105,
                    "• Фази: Встановлення каналу (Setup) → Неперервна передача даних (Data) → Розрив з'єднання (Teardown)\n"
                    "• Ресурси: Жорстко зарезервована смуга (наприклад, 64 кбіт/с DS0 або оптична довжина хвилі)\n"
                    "• Властивості: Затримка суворо детермінована, джитер дорівнює нулю, проміжні буфери відсутні\n"
                    "• Недолік: Під час пауз мовчання виділена смуга блокується і марнується для інших абонентів",
                    size=11, fill="#fffaf0", stroke="#d97706"))

    # Нижня панель: Комутація пакетів
    f.append(rect(20, 290, 840, 235, fill="#fcfdfe", stroke=LINE, sw=1.2))
    f.append(text(40, 315, "2. Комутація пакетів (Packet Switching — IP дейтаграми, MPLS, Ethernet)", size=12, bold=True, color=FIELD, anchor="start"))

    # Вузли комутації пакетів
    f.append(fitbox(40, 335, 95, 45, "Вузол A\n(Хост 1)", size=11, bold=True, fill="#eaf7ee", stroke=FIELD))
    f.append(fitbox(210, 335, 115, 45, "Маршрутизатор R1\n(Store & Forward)", size=10, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(410, 335, 115, 45, "Маршрутизатор R2\n(Store & Forward)", size=10, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(610, 335, 115, 45, "Маршрутизатор R3\n(Store & Forward)", size=10, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(755, 335, 85, 45, "Вузол B\n(Хост 2)", size=11, bold=True, fill="#eaf7ee", stroke=FIELD))

    # Спільні канали зв'язку та пакети в польоті
    f.append(line(135, 357, 210, 357, color=LINE, sw=1.5))
    f.append(line(325, 357, 410, 357, color=LINE, sw=1.5))
    f.append(line(525, 357, 610, 357, color=LINE, sw=1.5))
    f.append(line(725, 357, 755, 357, color=LINE, sw=1.5))

    # Візуалізація пакетів із заголовками на лінках
    f.append(rect(145, 345, 52, 24, fill="#dbeafe", stroke=NEG, sw=1.2, rx=3))
    f.append(text(171, 361, "Пакет 3", size=10, bold=True, color=NEG))

    f.append(rect(338, 345, 52, 24, fill="#dbeafe", stroke=NEG, sw=1.2, rx=3))
    f.append(text(364, 361, "Пакет 2", size=10, bold=True, color=NEG))

    f.append(rect(538, 345, 52, 24, fill="#dbeafe", stroke=NEG, sw=1.2, rx=3))
    f.append(text(564, 361, "Пакет 1", size=10, bold=True, color=NEG))

    # Пояснення характеристик пакетної мережі
    f.append(fitbox(40, 395, 800, 115,
                    "• Дискретизація: Повідомлення розбиваються на окремі пакети із заголовками (Header)\n"
                    "• Статистичне мультиплексування: Канал передачі динамічно ділиться між усіма активними потоками\n"
                    "• Буферизація (Store-and-Forward): Вузол повністю приймає пакет, перевіряє суму та ставить у чергу\n"
                    "• Компроміс: Висока ефективність утилізації смуги, але ризик переповнення буфера та змінна затримка",
                    size=11, fill="#f4fbf7", stroke=FIELD))

    render(os.path.join(IMG, "circuit-vs-packet-concept.svg"), W, H, *f)


# ── 2. Статичний TDM проти статистичного мультиплексування ───────────────────
def fig_multiplexing_tdm_vs_stat():
    W, H = 880, 500
    f = [text(W / 2, 24, "Механіка мультиплексування: Синхронний TDM проти Статистичного пакетного", size=15, bold=True)]

    # Верхня панель: TDM
    f.append(rect(20, 45, 840, 205, fill="#fcfdfe", stroke=LINE, sw=1.2))
    f.append(text(40, 68, "А. Синхронний поділ часу (TDM — Time Division Multiplexing)", size=12, bold=True, color=NEG, anchor="start"))

    # Джерела
    f.append(fitbox(40, 85, 120, 32, "Джерело A (Активне)", size=10, fill="#dbeafe", stroke=NEG))
    f.append(fitbox(40, 120, 120, 32, "Джерело B (Мовчить)", size=10, fill="#f3f4f6", stroke=MUTED))
    f.append(fitbox(40, 155, 120, 32, "Джерело C (Активне)", size=10, fill="#dbeafe", stroke=NEG))
    f.append(fitbox(40, 190, 120, 32, "Джерело D (Мовчить)", size=10, fill="#f3f4f6", stroke=MUTED))

    # Спільний канал з TDM-фреймами
    f.append(line(165, 142, 225, 142, color=LINE, sw=1.5))
    f.append(arrow(165, 142, 200, 142, color=LINE, sw=1.5))

    # Фрейм 1
    f.append(rect(235, 95, 275, 65, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(372, 88, "Цикл кадру TDM (Період 125 мкс)", size=10, bold=True, color=MUTED))
    f.append(rect(242, 105, 60, 46, fill="#dbeafe", stroke=NEG, sw=1))
    f.append(text(272, 132, "Слот A", size=10.5, bold=True, color=NEG))
    f.append(rect(309, 105, 60, 46, fill="#fee2e2", stroke=POS, sw=1, rx=2))
    f.append(text(339, 132, "ПОРОЖНЬО", size=9.5, bold=True, color=POS))
    f.append(rect(376, 105, 60, 46, fill="#dbeafe", stroke=NEG, sw=1))
    f.append(text(406, 132, "Слот C", size=10.5, bold=True, color=NEG))
    f.append(rect(443, 105, 60, 46, fill="#fee2e2", stroke=POS, sw=1, rx=2))
    f.append(text(473, 132, "ПОРОЖНЬО", size=9.5, bold=True, color=POS))

    # Фрейм 2
    f.append(rect(530, 95, 275, 65, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(667, 88, "Наступний кадр TDM", size=10, bold=True, color=MUTED))
    f.append(rect(537, 105, 60, 46, fill="#dbeafe", stroke=NEG, sw=1))
    f.append(text(567, 132, "Слот A", size=10.5, bold=True, color=NEG))
    f.append(rect(604, 105, 60, 46, fill="#fee2e2", stroke=POS, sw=1, rx=2))
    f.append(text(634, 132, "ПОРОЖНЬО", size=9.5, bold=True, color=POS))
    f.append(rect(671, 105, 60, 46, fill="#dbeafe", stroke=NEG, sw=1))
    f.append(text(701, 132, "Слот C", size=10.5, bold=True, color=NEG))
    f.append(rect(738, 105, 60, 46, fill="#fee2e2", stroke=POS, sw=1, rx=2))
    f.append(text(768, 132, "ПОРОЖНЬО", size=9.5, bold=True, color=POS))

    f.append(fitbox(235, 175, 595, 60,
                    "Жорстке закріплення таймслотів: Слоти B і D виділені, але не несуть корисних даних.\n"
                    "Утилізація фізичного каналу складає лише 50% від номінальної пропускної здатності.",
                    size=10.5, fill="#fffaf0", stroke="#d97706"))

    # Нижня панель: Статистичне мультиплексування
    f.append(rect(20, 265, 840, 220, fill="#fcfdfe", stroke=LINE, sw=1.2))
    f.append(text(40, 288, "Б. Статистичне мультиплексування пакетів (Statistical Multiplexing)", size=12, bold=True, color=FIELD, anchor="start"))

    # Джерела
    f.append(fitbox(40, 305, 120, 32, "Джерело A (Сплеск)", size=10, fill="#dbeafe", stroke=FIELD))
    f.append(fitbox(40, 340, 120, 32, "Джерело B (Пауза)", size=10, fill="#f3f4f6", stroke=MUTED))
    f.append(fitbox(40, 375, 120, 32, "Джерело C (Сплеск)", size=10, fill="#dbeafe", stroke=FIELD))
    f.append(fitbox(40, 410, 120, 32, "Джерело D (Пауза)", size=10, fill="#f3f4f6", stroke=MUTED))

    # Спільний буфер черги
    f.append(fitbox(180, 345, 100, 65, "Вхідний\nбуфер FIFO", size=10.5, bold=True, fill="#eaf7ee", stroke=FIELD))
    f.append(arrow(160, 321, 180, 340, color=FIELD, sw=1.5))
    f.append(arrow(160, 391, 180, 375, color=FIELD, sw=1.5))

    # Потік пакетів у каналі без дірок
    f.append(line(280, 377, 810, 377, color=LINE, sw=1.5))
    f.append(arrow(280, 377, 315, 377, color=LINE, sw=1.5))

    # Пакети в каналі
    f.append(rect(330, 352, 90, 48, fill="#dbeafe", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(375, 372, "Пакет A [1]", size=10, bold=True, color=FIELD))
    f.append(text(375, 388, "Hdr: A→B", size=9.5, color=MUTED))

    f.append(rect(430, 352, 90, 48, fill="#e0e7ff", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(475, 372, "Пакет C [1]", size=10, bold=True, color=FIELD))
    f.append(text(475, 388, "Hdr: C→D", size=9.5, color=MUTED))

    f.append(rect(530, 352, 90, 48, fill="#dbeafe", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(575, 372, "Пакет A [2]", size=10, bold=True, color=FIELD))
    f.append(text(575, 388, "Hdr: A→B", size=9.5, color=MUTED))

    f.append(rect(630, 352, 90, 48, fill="#dbeafe", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(675, 372, "Пакет A [3]", size=10, bold=True, color=FIELD))
    f.append(text(675, 388, "Hdr: A→B", size=9.5, color=MUTED))

    f.append(rect(730, 352, 90, 48, fill="#e0e7ff", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(775, 372, "Пакет C [2]", size=10, bold=True, color=FIELD))
    f.append(text(775, 388, "Hdr: C→D", size=9.5, color=MUTED))

    f.append(fitbox(290, 420, 550, 50,
                    "Динамічний розподіл: Немає заздалегідь закріплених порожніх слотів.\n"
                    "Канал на 100% заповнюється корисним трафіком активних джерел (A і C).",
                    size=10.5, fill="#f4fbf7", stroke=FIELD))

    render(os.path.join(IMG, "multiplexing-tdm-vs-stat.svg"), W, H, *f)


# ── 3. Часові діаграми затримок (Timeline Delay Comparison) ───────────────────
def fig_delay_timeline_comparison():
    W, H = 880, 540
    f = [text(W / 2, 24, "Часова шкала передачі (Timeline): комутація каналів проти дейтаграмних пакетів", size=15, bold=True)]

    # Ліва половина: Комутація каналів
    f.append(rect(20, 45, 410, 480, fill="#fcfdfe", stroke=LINE, sw=1.2))
    f.append(text(225, 68, "Комутація каналів (Circuit Switching)", size=12, bold=True, color=NEG))

    # Вертикальні осі
    x_src, x_sw1, x_sw2, x_dst = 50, 140, 230, 320
    f.append(line(x_src, 90, x_src, 420, color=MUTED, sw=1.5))
    f.append(line(x_sw1, 90, x_sw1, 420, color=MUTED, sw=1.5))
    f.append(line(x_sw2, 90, x_sw2, 420, color=MUTED, sw=1.5))
    f.append(line(x_dst, 90, x_dst, 420, color=MUTED, sw=1.5))

    f.append(text(x_src, 82, "Src", size=11, bold=True))
    f.append(text(x_sw1, 82, "SW1", size=11, bold=True))
    f.append(text(x_sw2, 82, "SW2", size=11, bold=True))
    f.append(text(x_dst, 82, "Dst", size=11, bold=True))

    # Фаза 1: Setup сигналізація
    f.append(arrow(x_src, 100, x_sw1, 120, color=POS, sw=1.8))
    f.append(arrow(x_sw1, 120, x_sw2, 140, color=POS, sw=1.8))
    f.append(arrow(x_sw2, 140, x_dst, 160, color=POS, sw=1.8))
    # Підтвердження Setup Ack назад
    f.append(line(x_dst, 160, x_sw2, 180, color=POS, sw=1.8, dash="4,3"))
    f.append(line(x_sw2, 180, x_sw1, 200, color=POS, sw=1.8, dash="4,3"))
    f.append(line(x_sw1, 200, x_src, 220, color=POS, sw=1.8, dash="4,3"))

    f.append(fitbox(335, 135, 85, 50, "Фаза Setup\n(Час RTT)", size=10, bold=True, fill="#fee2e2", stroke=POS))

    # Фаза 2: Передача даних (суцільний бітовий потік)
    f.append(rect(x_src - 3, 230, 6, 120, fill="#2457d6", stroke=NEG, sw=1))
    f.append(line(x_src, 230, x_dst, 250, color=NEG, sw=2))
    f.append(line(x_src, 350, x_dst, 370, color=NEG, sw=2))
    # Заливка тіла даних між фронтом і спадом
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#dbeafe" opacity="0.6"/>' %
             (x_src, 230, x_dst, 250, x_dst, 370, x_src, 350))
    f.append(text(185, 300, "Неперервний потік бітів (Data)", size=10.5, bold=True, color=NEG))

    # Фаза 3: Teardown
    f.append(line(x_src, 380, x_dst, 405, color=MUTED, sw=1.5, dash="3,2"))
    f.append(text(185, 395, "Teardown (розрив каналу)", size=10, color=MUTED))

    f.append(fitbox(35, 435, 380, 75,
                    "Повний час = T_setup + L_даних / C + t_поширення + T_teardown\n"
                    "• Неефективно для коротких повідомлень (T_setup >> T_передачі)\n"
                    "• Ідеально для довгих неперервних потоків (нульовий джитер)",
                    size=10, fill="#fffaf0", stroke="#d97706"))

    # Права половина: Комутація пакетів (Store-and-Forward)
    f.append(rect(450, 45, 410, 480, fill="#fcfdfe", stroke=LINE, sw=1.2))
    f.append(text(655, 68, "Комутація пакетів (Store-and-Forward)", size=12, bold=True, color=FIELD))

    # Вертикальні осі
    px_src, px_r1, px_r2, px_dst = 480, 570, 660, 750
    f.append(line(px_src, 90, px_src, 420, color=MUTED, sw=1.5))
    f.append(line(px_r1, 90, px_r1, 420, color=MUTED, sw=1.5))
    f.append(line(px_r2, 90, px_r2, 420, color=MUTED, sw=1.5))
    f.append(line(px_dst, 90, px_dst, 420, color=MUTED, sw=1.5))

    f.append(text(px_src, 82, "Src", size=11, bold=True))
    f.append(text(px_r1, 82, "R1", size=11, bold=True))
    f.append(text(px_r2, 82, "R2", size=11, bold=True))
    f.append(text(px_dst, 82, "Dst", size=11, bold=True))

    # Передача пакетів конвеєром (Pipelining)
    # Пакет 1
    f.append(rect(px_src - 3, 100, 6, 40, fill="#16a34a", stroke=FIELD, sw=1))
    f.append(line(px_src, 100, px_r1, 115, color=FIELD, sw=1.5))
    f.append(line(px_src, 140, px_r1, 155, color=FIELD, sw=1.5))
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#dcfce7" opacity="0.8"/>' %
             (px_src, 100, px_r1, 115, px_r1, 155, px_src, 140))
    f.append(text(525, 128, "Пакет 1", size=10, bold=True, color=FIELD))

    # R1 -> R2 для Pkt 1
    f.append(rect(px_r1 - 3, 155, 6, 40, fill="#16a34a", stroke=FIELD, sw=1))
    f.append(line(px_r1, 155, px_r2, 170, color=FIELD, sw=1.5))
    f.append(line(px_r1, 195, px_r2, 210, color=FIELD, sw=1.5))
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#dcfce7" opacity="0.8"/>' %
             (px_r1, 155, px_r2, 170, px_r2, 210, px_r1, 195))

    # R2 -> Dst для Pkt 1
    f.append(rect(px_r2 - 3, 210, 6, 40, fill="#16a34a", stroke=FIELD, sw=1))
    f.append(line(px_r2, 210, px_dst, 225, color=FIELD, sw=1.5))
    f.append(line(px_r2, 250, px_dst, 265, color=FIELD, sw=1.5))
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="#dcfce7" opacity="0.8"/>' %
             (px_r2, 210, px_dst, 225, px_dst, 265, px_r2, 250))

    # Пакет 2
    f.append(rect(px_src - 3, 140, 6, 40, fill="#2563eb", stroke=NEG, sw=1))
    f.append(line(px_src, 140, px_r1, 155, color=NEG, sw=1.5))
    f.append(line(px_src, 180, px_r1, 195, color=NEG, sw=1.5))
    f.append(text(525, 170, "Пакет 2", size=10, bold=True, color=NEG))

    # R1 -> R2 для Pkt 2
    f.append(rect(px_r1 - 3, 195, 6, 40, fill="#2563eb", stroke=NEG, sw=1))
    f.append(line(px_r1, 195, px_r2, 210, color=NEG, sw=1.5))
    f.append(line(px_r1, 235, px_r2, 250, color=NEG, sw=1.5))

    # R2 -> Dst для Pkt 2
    f.append(rect(px_r2 - 3, 250, 6, 40, fill="#2563eb", stroke=NEG, sw=1))
    f.append(line(px_r2, 250, px_dst, 265, color=NEG, sw=1.5))
    f.append(line(px_r2, 290, px_dst, 305, color=NEG, sw=1.5))

    # Пакет 3
    f.append(rect(px_src - 3, 180, 6, 40, fill="#d97706", stroke=POS, sw=1))
    f.append(text(525, 210, "Пакет 3", size=10, bold=True, color=POS))

    # Маркування затримки серіалізації та черги
    f.append(fitbox(765, 125, 85, 50, "Час серіа-\nлізації L / R", size=9.5, fill="#f3f4f6", stroke=MUTED))
    f.append(fitbox(765, 245, 85, 60, "Конвеєр\nпакетів\n(Pipelining)", size=10, bold=True, fill="#eaf7ee", stroke=FIELD))

    f.append(fitbox(465, 435, 380, 75,
                    "Повний час = (N_пакетів + K_хопів − 1) · (L / R) + K_хопів · t_поширення + ∑ W_q\n"
                    "• Немає затримки на встановлення з'єднання (Setup RTT = 0)\n"
                    "• Конвеєризація скорочує загальний час доставки порівняно з цілим файлом",
                    size=10, fill="#f4fbf7", stroke=FIELD))

    render(os.path.join(IMG, "delay-timeline-comparison.svg"), W, H, *f)


# ── 4. Дейтаграми проти Віртуальних каналів ──────────────────────────────────
def fig_packet_virtual_circuit_vs_datagram():
    W, H = 880, 520
    f = [text(W / 2, 24, "Архітектура пакетних мереж: Дейтаграми проти Віртуальних каналів", size=15, bold=True)]

    # Ліва панель: Дейтаграмні мережі (Datagram)
    f.append(rect(20, 45, 410, 460, fill="#fcfdfe", stroke=LINE, sw=1.2))
    f.append(text(225, 68, "А. Дейтаграмні мережі (Datagram — IP)", size=12, bold=True, color=FIELD))

    # Структура пакета IP
    f.append(fitbox(35, 85, 380, 42, "Формат пакета: [ IP: 198.51.100.42 | Дані ]\nКожен пакет несе повну глобальну адресу", size=10, fill="#eaf7ee", stroke=FIELD))

    # Схема маршрутизації
    f.append(fitbox(35, 138, 90, 36, "Хост A", size=10.5, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(175, 138, 100, 36, "Маршрутизатор\nR1", size=10, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(325, 138, 90, 36, "Хост B", size=10.5, bold=True, fill="#ffffff", stroke=LINE))
    f.append(arrow(125, 156, 175, 156, color=LINE, sw=1.5))
    f.append(arrow(275, 156, 325, 156, color=LINE, sw=1.5))

    # Таблиця маршрутизації R1
    f.append(fitbox(35, 185, 380, 75,
                    "Таблиця маршрутизації R1 (Stateless):\n"
                    "Префікс мережі       | Наступний вузол | Порт\n"
                    "198.51.100.0/24      | 203.0.113.2     | eth1\n"
                    "0.0.0.0/0 (Default)  | 192.0.2.1       | eth0",
                    size=9.5, fill="#f9fafb", stroke=MUTED))

    # Властивості дейтаграмної мережі
    f.append(fitbox(35, 270, 380, 220,
                    "• Без встановлення з'єднання (Connectionless)\n"
                    "• Автономна маршрутизація кожного пакета\n"
                    "• Стійкість до аварійних ситуацій: при падінні лінка\n"
                    "  динамічна маршрутизація пускає пакети в обхід\n"
                    "  без необхідності перезапуску сесії\n"
                    "• Простота й масштабованість вузлів:\n"
                    "  ядро мережі не зберігає стан з'єднань",
                    size=10, fill="#f4fbf7", stroke=FIELD))

    # Права панель: Віртуальні канали (Virtual Circuit)
    f.append(rect(450, 45, 410, 460, fill="#fcfdfe", stroke=LINE, sw=1.2))
    f.append(text(655, 68, "Б. Віртуальні канали (VC — X.25, ATM, MPLS)", size=12, bold=True, color=NEG))

    # Структура пакета VC
    f.append(fitbox(465, 85, 380, 42, "Формат пакета: [ Локальна мітка VC = 42 | Дані ]\nЗаголовок несе коротку локальну мітку", size=10, fill="#eef3ff", stroke=NEG))

    # Схема комутації VC
    f.append(fitbox(465, 138, 90, 36, "Хост A", size=10.5, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(605, 138, 100, 36, "Комутатор\nSW1", size=10, bold=True, fill="#ffffff", stroke=LINE))
    f.append(fitbox(755, 138, 90, 36, "Хост B", size=10.5, bold=True, fill="#ffffff", stroke=LINE))
    f.append(arrow(555, 156, 605, 156, color=LINE, sw=1.5))
    f.append(arrow(705, 156, 755, 156, color=LINE, sw=1.5))

    # Таблиця комутації VC SW1
    f.append(fitbox(465, 185, 380, 75,
                    "Таблиця трансляції міток SW1 (Stateful):\n"
                    "Вхідний порт | Вхідна мітка | Вихідний порт | Нова мітка\n"
                    "Port 1       | 42           | Port 3        | 107\n"
                    "Port 2       | 15           | Port 4        | 88",
                    size=9.5, fill="#f9fafb", stroke=MUTED))

    # Властивості віртуальних каналів
    f.append(fitbox(465, 270, 380, 220,
                    "• Орієнтація на з'єднання (Connection-Oriented):\n"
                    "  фаза Setup створює записи у комутаторах\n"
                    "• Швидка комутація: прямий індексний пошук\n"
                    "  замість довгого префіксного аналізу (LPM)\n"
                    "• Гарантії QoS та резервування смуги для потоку\n"
                    "• Чутливість до відмов: вихід вузла з ладу\n"
                    "  розриває VC і потребує нового Setup",
                    size=10, fill="#fffaf0", stroke="#d97706"))

    render(os.path.join(IMG, "packet-virtual-circuit-vs-datagram.svg"), W, H, *f)


if __name__ == "__main__":
    fig_circuit_vs_packet_concept()
    fig_multiplexing_tdm_vs_stat()
    fig_delay_timeline_comparison()
    fig_packet_virtual_circuit_vs_datagram()
    print("All figures successfully generated in ./img/")
