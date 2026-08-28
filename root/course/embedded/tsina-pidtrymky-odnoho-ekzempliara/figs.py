# -*- coding: utf-8 -*-
"""Фігури для статті tsina-pidtrymky-odnoho-ekzempliara.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_lifecycle_cost_waterfall():
    """Фінансовий водоспад собівартості та пост-продажного обслуговування пристрою за 5 років."""
    W, H = 840, 500
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Юніт-економіка життєвого циклу: разова маржа проти 5 років OpEx", size=16, color=INK, bold=True))

    # Лівий блок: Традиційний наївний розрахунок (помилка разового продажу)
    p.append(rect(30, 55, 370, 415, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(215, 82, "Наївна модель: прибуток у мінусі (-18 $)", size=14, color=POS, bold=True))
    p.append(text(215, 102, "Ціна продажу: +120 $ | Виробничий COGS: -60 $", size=11, color=MUTED))

    # Стовпчики / блоки витрат наївного підходу
    # Початкова маржа
    p.append(rect(50, 120, 330, 38, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(215, 138, "Початкова валова маржа при продажу: +60 $", size=11, color=FIELD, bold=True))
    p.append(text(215, 152, "Ціна 120 $ мінус BOM і складання 60 $", size=9.5, color=MUTED))

    # Витрати зв'язку
    p.append(rect(50, 166, 330, 48, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 184, "Стільниковий зв'язок (0.40 $/міс × 60 міс): -24 $", size=11, color=POS, bold=True))
    p.append(text(215, 202, "Постійні keep-alive, часті JSON-пакети, SIM-пул", size=9.5, color=INK))

    # Хмарна інфраструктура
    p.append(rect(50, 222, 330, 48, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 240, "Хмара та збереження (0.30 $/міс × 60 міс): -18 $", size=11, color=POS, bold=True))
    p.append(text(215, 258, "MQTT-брокер, гаряче сховище Timeseries, API запити", size=9.5, color=INK))

    # Сервісна підтримка
    p.append(rect(50, 278, 330, 48, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 296, "Тікети підтримки (0.08 тікета/рік × 30 $): -12 $", size=11, color=POS, bold=True))
    p.append(text(215, 314, "Хибні тривоги, незрозумілі помилки, робота L1/L2", size=9.5, color=INK))

    # Гарантія та RMA
    p.append(rect(50, 334, 330, 48, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 352, "Гарантійний ремонт і RMA (2.5 % відмов): -16 $", size=11, color=POS, bold=True))
    p.append(text(215, 370, "Логістика туди-назад, заміна плати, No Defect Found", size=9.5, color=INK))

    # OTA та безпека
    p.append(rect(50, 390, 330, 38, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 408, "OTA-оновлення та сервери безпеки: -8 $", size=11, color=POS, bold=True))
    p.append(text(215, 422, "Повні бінарні образи без дельт, CDN трафік", size=9.5, color=INK))

    # Підсумок ліворуч
    p.append(rect(45, 436, 340, 26, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 453, "Кумулятивний підсумок: 60 $ − 78 $ = −18 $ (Збиток)", size=11, color=POS, bold=True))

    # Правий блок: Оптимізована архітектура (контрольований OpEx)
    p.append(rect(440, 55, 370, 415, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(625, 82, "Оптимізована модель: чистий прибуток (+38 $)", size=14, color=FIELD, bold=True))
    p.append(text(625, 102, "Ціна продажу: +120 $ | Виробничий COGS: -60 $", size=11, color=MUTED))

    # Початкова маржа
    p.append(rect(460, 120, 330, 38, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(625, 138, "Початкова валова маржа при продажу: +60 $", size=11, color=FIELD, bold=True))
    p.append(text(625, 152, "Ціна 120 $ мінус BOM і складання 60 $", size=9.5, color=MUTED))

    # Витрати зв'язку
    p.append(rect(460, 166, 330, 48, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(625, 184, "Стільниковий зв'язок (0.08 $/міс × 60 міс): -4.80 $", size=11, color="#0369a1", bold=True))
    p.append(text(625, 202, "Пакетування, бінарний Protobuf/CBOR, дельта-зрізи", size=9.5, color=INK))

    # Хмарна інфраструктура
    p.append(rect(460, 222, 330, 48, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(625, 240, "Хмара та збереження (0.07 $/міс × 60 міс): -4.20 $", size=11, color="#0369a1", bold=True))
    p.append(text(625, 258, "Батчинг MQTT, 7 днів Hot -> Cold S3 Parquet", size=9.5, color=INK))

    # Сервісна підтримка
    p.append(rect(460, 278, 330, 48, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(625, 296, "Тікети підтримки (0.02 тікета/рік × 25 $): -2.50 $", size=11, color="#0369a1", bold=True))
    p.append(text(625, 314, "Вбудована самодіагностика, зрозумілі статус-коди", size=9.5, color=INK))

    # Гарантія та RMA
    p.append(rect(460, 334, 330, 48, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(625, 352, "Гарантійний ремонт і RMA (1.2 % відмов): -8.50 $", size=11, color="#0369a1", bold=True))
    p.append(text(625, 370, "Превентивний моніторинг зносу, відсікання NDF", size=9.5, color=INK))

    # OTA та безпека
    p.append(rect(460, 390, 330, 38, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(625, 408, "OTA-оновлення та безпека: -2.00 $", size=11, color="#0369a1", bold=True))
    p.append(text(625, 422, "Дельта-патчі BSDiff/Courgette (200 КБ замість 32 МБ)", size=9.5, color=INK))

    # Підсумок праворуч
    p.append(rect(455, 436, 340, 26, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(625, 453, "Кумулятивний підсумок: 60 $ − 22 $ = +38 $ (Прибуток)", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "lifecycle-cost-waterfall.svg"), W, H, *p)


def fig_support_cost_drivers_map():
    """Карта чотирьох головних драйверів пост-продажної вартості підтримки залізного флоту."""
    W, H = 840, 480
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Чотири стовпи пост-продажних експлуатаційних витрат (OpEx)", size=16, color=INK, bold=True))

    # 1. Зв'язок і телеметрія
    p.append(rect(30, 60, 370, 185, fill="#f8fafc", stroke="#0284c7", sw=1.5, rx=8))
    p.append(text(215, 88, "1. Зв'язок і радіотрафік (Connectivity)", size=13, color="#0369a1", bold=True))
    p.append(text(215, 110, "• Оплата за мегабайти / сесії у стільникових мережах", size=10.5, color=INK))
    p.append(text(215, 130, "• Оверхед протоколів (TLS handshake, MQTT, TCP ACK)", size=10.5, color=INK))
    p.append(text(215, 150, "• Квантування трафіку (округлення до 1 або 10 КБ на сесію)", size=10.5, color=INK))
    p.append(text(215, 170, "• Енергетична ціна ретрансмісій при слабкому сигналі", size=10.5, color=INK))
    p.append(text(215, 215, "Важіль: Deadband-фільтрація, бінарний формат, батчинг", size=10, color="#0369a1", bold=True))

    # 2. Хмарна інфраструктура
    p.append(rect(440, 60, 370, 185, fill="#f8fafc", stroke="#7c3aed", sw=1.5, rx=8))
    p.append(text(625, 88, "2. Хмарна обробка та сховище (Cloud Ingestion)", size=13, color="#6d28d9", bold=True))
    p.append(text(625, 110, "• Оплата брокера за кількість прийнятих повідомлень", size=10.5, color=INK))
    p.append(text(625, 130, "• IOPS та ресурси читання/запису Time-series БД", size=10.5, color=INK))
    p.append(text(625, 150, "• Вартість зберігання гігабайтів сирих нестиснутих логів", size=10.5, color=INK))
    p.append(text(625, 170, "• Обчислювальні витрати бекенду на розбір JSON", size=10.5, color=INK))
    p.append(text(625, 215, "Важіль: Багаторівневе сховище (Hot -> Cold), S3 Parquet", size=10, color="#6d28d9", bold=True))

    # 3. Сервісні звернення та інженери
    p.append(rect(30, 265, 370, 185, fill="#f8fafc", stroke="#ea580c", sw=1.5, rx=8))
    p.append(text(215, 293, "3. Сервісні звернення (Customer Support)", size=13, color="#c2410c", bold=True))
    p.append(text(215, 315, "• Час роботи операторів L1 та інженерів ескалації L2/L3", size=10.5, color=INK))
    p.append(text(215, 335, "• Хибні скарги через незрозумілу поведінку інтерфейсу", size=10.5, color=INK))
    p.append(text(215, 355, "• Відсутність віддаленого діагностичного знімка стану", size=10.5, color=INK))
    p.append(text(215, 375, "• Спроби повторної конфігурації заблокованих вузлів", size=10.5, color=INK))
    p.append(text(215, 420, "Важіль: Автодіагностика, однозначні статус-коди", size=10, color="#c2410c", bold=True))

    # 4. Гарантійна заміна та логістика
    p.append(rect(440, 265, 370, 185, fill="#f8fafc", stroke=POS, sw=1.5, rx=8))
    p.append(text(625, 293, "4. Гарантія, RMA та польовий ремонт (Field RMA)", size=13, color=POS, bold=True))
    p.append(text(625, 315, "• Логістика доставки дефектного вузла в сервісний центр", size=10.5, color=INK))
    p.append(text(625, 335, "• Час техніка на стендову перевірку та дефектовку", size=10.5, color=INK))
    p.append(text(625, 355, "• Витрати на випадки «Дефекту не виявлено» (NDF ~30-40%)", size=10.5, color=INK))
    p.append(text(625, 375, "• Фізичний знос: електроліти, реле, флеш-пам'ять", size=10.5, color=INK))
    p.append(text(625, 420, "Важіль: Самотестування на борту, предиктивний моніторинг", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "support-cost-drivers-map.svg"), W, H, *p)


def fig_edge_optimization_levers():
    """Архітектурний ланцюг оптимізації вартості: від сенсора на мікроконтролері до холодного архіву."""
    W, H = 840, 460
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Інженерні важелі зниження TCO на рівні прошивки та хмари", size=16, color=INK, bold=True))

    # Крок 1: Периферія та зняття даних
    p.append(rect(30, 65, 230, 360, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(145, 95, "Рівень прошивки MCU", size=13, color=FIELD, bold=True))
    p.append(text(145, 115, "Фільтрація та батчинг", size=10.5, color=MUTED))

    p.append(rect(45, 135, 200, 60, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(145, 155, "Deadband / Swing Door", size=11, color=INK, bold=True))
    p.append(text(145, 172, "Відсікання шуму сенсорів", size=9.5, color=MUTED))
    p.append(text(145, 186, "-80% зайвих точок вимірів", size=9.5, color=FIELD, bold=True))

    p.append(rect(45, 205, 200, 60, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(145, 225, "Компактний Protobuf/CBOR", size=11, color=INK, bold=True))
    p.append(text(145, 242, "Бінарні поля замість JSON", size=9.5, color=MUTED))
    p.append(text(145, 256, "Зменшення кадру у 6-10 разів", size=9.5, color=FIELD, bold=True))

    p.append(rect(45, 275, 200, 60, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(145, 295, "Flash Кільцевий буфер", size=11, color=INK, bold=True))
    p.append(text(145, 312, "Накопичення пакетів у Flash", size=9.5, color=MUTED))
    p.append(text(145, 326, "Зниження числа сесій зв'язку", size=9.5, color=FIELD, bold=True))

    p.append(rect(45, 345, 200, 65, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(145, 365, "Бортова діагностика", size=11, color=INK, bold=True))
    p.append(text(145, 382, "POST & Crash dump у Flash", size=9.5, color=MUTED))
    p.append(text(145, 396, "Усунення хибних повернень NDF", size=9.5, color=FIELD, bold=True))

    # Стрілка 1 -> 2
    p.append(arrow(265, 245, 300, 245, color=LINE, sw=2.0))

    # Крок 2: Мережевий шлюз та радіоканал
    p.append(rect(305, 65, 230, 360, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=8))
    p.append(text(420, 95, "Транспортний рівень", size=13, color="#0369a1", bold=True))
    p.append(text(420, 115, "Оптимізація сесій", size=10.5, color=MUTED))

    p.append(rect(320, 135, 200, 60, fill="#ffffff", stroke="#0284c7", sw=1.0, rx=4))
    p.append(text(420, 155, "Об'єднання передач", size=11, color=INK, bold=True))
    p.append(text(420, 172, "1 сесія на 20 вимірювань", size=9.5, color=MUTED))
    p.append(text(420, 186, "-90% витрат на TLS Handshake", size=9.5, color="#0369a1", bold=True))

    p.append(rect(320, 205, 200, 60, fill="#ffffff", stroke="#0284c7", sw=1.0, rx=4))
    p.append(text(420, 225, "Адаптивний Keep-Alive", size=11, color=INK, bold=True))
    p.append(text(420, 242, "Динамічний пінг під NAT", size=9.5, color=MUTED))
    p.append(text(420, 256, "Зменшення фонового трафіку", size=9.5, color="#0369a1", bold=True))

    p.append(rect(320, 275, 200, 60, fill="#ffffff", stroke="#0284c7", sw=1.0, rx=4))
    p.append(text(420, 295, "Дельта-оновлення OTA", size=11, color=INK, bold=True))
    p.append(text(420, 312, "Передача лише бінарного diff", size=9.5, color=MUTED))
    p.append(text(420, 326, "Економія 95% трафіку OTA", size=9.5, color="#0369a1", bold=True))

    p.append(rect(320, 345, 200, 65, fill="#ffffff", stroke="#0284c7", sw=1.0, rx=4))
    p.append(text(420, 365, "SIM Data Pooling", size=11, color=INK, bold=True))
    p.append(text(420, 382, "Спільний пул мегабайтів флоту", size=9.5, color=MUTED))
    p.append(text(420, 396, "Захист від штрафів overage", size=9.5, color="#0369a1", bold=True))

    # Стрілка 2 -> 3
    p.append(arrow(540, 245, 575, 245, color=LINE, sw=2.0))

    # Крок 3: Хмарний бекенд та сховище
    p.append(rect(580, 65, 230, 360, fill="#faf5ff", stroke="#7c3aed", sw=1.5, rx=8))
    p.append(text(695, 95, "Хмарна платформа", size=13, color="#6d28d9", bold=True))
    p.append(text(695, 115, "Каскадне сховище", size=10.5, color=MUTED))

    p.append(rect(595, 135, 200, 60, fill="#ffffff", stroke="#7c3aed", sw=1.0, rx=4))
    p.append(text(695, 155, "Hot Tier (0-7 днів)", size=11, color=INK, bold=True))
    p.append(text(695, 172, "Швидка пам'ять для алертингу", size=9.5, color=MUTED))
    p.append(text(695, 186, "Висока швидкість, обмежений обсяг", size=9.5, color="#6d28d9", bold=True))

    p.append(rect(595, 205, 200, 60, fill="#ffffff", stroke="#7c3aed", sw=1.0, rx=4))
    p.append(text(695, 225, "Warm Tier (8-90 днів)", size=11, color=INK, bold=True))
    p.append(text(695, 242, "Агреговані погодинні зрізи", size=9.5, color=MUTED))
    p.append(text(695, 256, "Стиснення даних на 90%", size=9.5, color="#6d28d9", bold=True))

    p.append(rect(595, 275, 200, 60, fill="#ffffff", stroke="#7c3aed", sw=1.0, rx=4))
    p.append(text(695, 295, "Cold Archive (3-10 років)", size=11, color=INK, bold=True))
    p.append(text(695, 312, "S3 Glacier / Parquet стовпці", size=9.5, color=MUTED))
    p.append(text(695, 326, "Ціна: 0.001 $ за ГБ/міс", size=9.5, color="#6d28d9", bold=True))

    p.append(rect(595, 345, 200, 65, fill="#ffffff", stroke="#7c3aed", sw=1.0, rx=4))
    p.append(text(695, 365, "Triage Автоматизація", size=11, color=INK, bold=True))
    p.append(text(695, 382, "Авто-аналіз телеметрії перед L1", size=9.5, color=MUTED))
    p.append(text(695, 396, "-70% витрат на сервісні тікети", size=9.5, color="#6d28d9", bold=True))

    render(os.path.join(OUT, "edge-optimization-levers.svg"), W, H, *p)


if __name__ == "__main__":
    fig_lifecycle_cost_waterfall()
    fig_support_cost_drivers_map()
    fig_edge_optimization_levers()
    print("All figures generated successfully.")
