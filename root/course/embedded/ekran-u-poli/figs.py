# -*- coding: utf-8 -*-
"""Генератор векторних схем для теми «Екран у полі: сонце, рукавиці, одна рука»."""

import os
import sys

# Підключаємо svgkit із scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_optical_bonding():
    """Порівняння оптичного склеювання (Optical Bonding) та повітряного проміжку (Air Gap)."""
    w, h = 980, 480
    frags = []

    frags.append(text(w / 2, 26, "Оптичне склеювання (Optical Bonding) проти повітряного проміжку (Air Gap)", size=15, bold=True))

    # Ліва колонка: Air Gap (повітряний проміжок)
    frags.append(rect(30, 50, 445, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(252, 76, "Повітряний проміжок (Air Gap)", size=13, bold=True, color=POS))
    frags.append(text(252, 95, "Сумарне відбиття сонця: 12–15 % (екран вимивається)", size=11, color=MUTED))

    # Стек шарів Air Gap
    # 1. Захисне скло
    frags.append(rect(50, 115, 405, 40, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=4))
    frags.append(text(252, 140, "Захисне скло (Cover Glass, n = 1.52)", size=11, bold=True, color="#334155"))

    # 2. Повітряний проміжок
    frags.append(rect(50, 165, 405, 50, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    frags.append(text(252, 186, "Повітряний проміжок (Air Gap, n = 1.00)", size=11, bold=True, color=POS))
    frags.append(text(252, 204, "Стрибок n: 1.52 → 1.00 → 1.50 (відбиття Френеля на обох межах)", size=10, color=POS))

    # 3. Поляризатор + Сенсорна сітка
    frags.append(rect(50, 225, 405, 35, fill="#cbd5e1", stroke="#64748b", sw=1.2, rx=4))
    frags.append(text(252, 247, "Поляризатор + сенсорна сітка (n = 1.50)", size=10.5, color="#334155"))

    # 4. РК-матриця
    frags.append(rect(50, 270, 405, 45, fill="#94a3b8", stroke="#475569", sw=1.2, rx=4))
    frags.append(text(252, 298, "Рідкокристалічна матриця (TFT Cell, n = 1.52)", size=11, bold=True, color="#0f172a"))

    # 5. Підсвітка
    frags.append(rect(50, 325, 405, 35, fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=4))
    frags.append(text(252, 347, "Підсвічування дисплея (350–500 nit)", size=11, bold=True, color="#854d0e"))

    # Опис наслідку зліва
    frags.append(rect(50, 375, 405, 70, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    frags.append(text(252, 396, "Результат під сонцем 100 000 lx:", size=11, bold=True, color=POS))
    frags.append(text(252, 414, "Відбитий блік ~4000 nit перекриває корисні 400 nit.", size=10, color="#7f1d1d"))
    frags.append(text(252, 430, "Контраст CR ≈ 1.1:1 — суцільне біле дзеркало.", size=10, bold=True, color="#7f1d1d"))

    # Права колонка: Optical Bonding
    frags.append(rect(505, 50, 445, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(727, 76, "Оптичне склеювання (Optical Bonding)", size=13, bold=True, color=FIELD))
    frags.append(text(727, 95, "Сумарне відбиття сонця: <0.5–1 % (чисте зображення)", size=11, color=MUTED))

    # Стек шарів Optical Bonding
    # 1. Захисне скло з AR/AG покриттям
    frags.append(rect(525, 115, 405, 40, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
    frags.append(text(727, 133, "Скло з покриттям AR + AG (n = 1.52)", size=11, bold=True, color="#1e40af"))
    frags.append(text(727, 149, "Антивідблиск + матове мікротравлення", size=10, color="#1e40af"))

    # 2. Оптичний клей (LOCA / OCA)
    frags.append(rect(525, 165, 405, 50, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(727, 186, "Оптичний клей LOCA / OCA (n = 1.51)", size=11, bold=True, color=FIELD))
    frags.append(text(727, 204, "Ідеальне узгодження n: немає меж розділу зі стрибком коефіцієнта", size=10, color="#14532d"))

    # 3. Поляризатор + Сенсорна сітка
    frags.append(rect(525, 225, 405, 35, fill="#cbd5e1", stroke="#64748b", sw=1.2, rx=4))
    frags.append(text(727, 247, "Поляризатор + сенсорна сітка (n = 1.50)", size=10.5, color="#334155"))

    # 4. РК-матриця
    frags.append(rect(525, 270, 405, 45, fill="#94a3b8", stroke="#475569", sw=1.2, rx=4))
    frags.append(text(727, 298, "Рідкокристалічна матриця (TFT Cell, n = 1.52)", size=11, bold=True, color="#0f172a"))

    # 5. Підсвітка високої яскравості
    frags.append(rect(525, 325, 405, 35, fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=4))
    frags.append(text(727, 347, "Підсвічування High-Brightness (>1000–1500 nit)", size=11, bold=True, color="#854d0e"))

    # Опис наслідку справа
    frags.append(rect(525, 375, 405, 70, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(727, 396, "Результат під сонцем 100 000 lx:", size=11, bold=True, color=FIELD))
    frags.append(text(727, 414, "Паразитний блік <250 nit, корисний сигнал 1200 nit.", size=10, color="#14532d"))
    frags.append(text(727, 430, "Контраст CR > 6:1 — телеметрію видно бездоганно.", size=10, bold=True, color="#14532d"))

    render(os.path.join(IMG_DIR, "optical-bonding-vs-airgap.svg"), w, h, *frags)


def fig_touch_technologies():
    """Порівняння ємнісного сенсора, резистивного та фізичних органів керування."""
    w, h = 980, 440
    frags = []

    frags.append(text(w / 2, 26, "Введення в польових умовах: ємнісний екран, резистивний та фізичні кнопки", size=15, bold=True))

    cards = [
        {
            "title": "Ємнісний PCAP (Glove Mode)",
            "subtitle": "Підвищена чутливість сенсора",
            "x": 30, "w": 285,
            "pros": [
                "Прозорість скла 90–92 %",
                "Підтримка жестів (Pinch-to-zoom)",
                "Висока зносостійкість (тверде скло)",
                "Швидкий відгук і точність"
            ],
            "cons": [
                "Хибні кліки від дощу й поту",
                "Зниження SNR у товстих рукавицях",
                "Потребує автокалібрування"
            ],
            "color": "#2563eb",
            "badge": "Сучасні планшети / пульти"
        },
        {
            "title": "Резистивний 4/5-провідний",
            "subtitle": "Спрацьовування від тиску (Force)",
            "x": 345, "w": 285,
            "pros": [
                "100% робота в будь-яких рукавицях",
                "Імунітет до води, бруду та олив",
                "Можливість натискання стилусом",
                "Низька ціна контролера"
            ],
            "cons": [
                "Світлопропускання лише 75–80 %",
                "Механічне стирання плівки ITO",
                "Немає справжнього мультитачу"
            ],
            "color": "#d97706",
            "badge": "Промислові термінали"
        },
        {
            "title": "Фізичні органи (Енкодер + Клавіші)",
            "subtitle": "Тактильний механічний зворотний зв'язок",
            "x": 660, "w": 290,
            "pros": [
                "Робота наосліп без погляду на екран",
                "Хід клавіш 1.5–2.5 мм підтверджує клік",
                "Надійність під час вібрацій і стресу",
                "Неможливо зірвати водою чи снігом"
            ],
            "cons": [
                "Потребує герметизації корпусу IP67",
                "Обмежена гнучкість конфігурації",
                "Збільшує масу та габарити пульта"
            ],
            "color": "#16a34a",
            "badge": "Тактичні станції й авіоніка"
        }
    ]

    for c in cards:
        cx = c["x"]
        cw = c["w"]
        frags.append(rect(cx, 55, cw, 365, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
        frags.append(rect(cx, 55, cw, 54, fill=FILL, stroke="#cbd5e1", sw=1.5, rx=8))
        frags.append(text(cx + cw / 2, 78, c["title"], size=12, bold=True, color=c["color"]))
        frags.append(text(cx + cw / 2, 96, c["subtitle"], size=10, color=MUTED))

        frags.append(text(cx + 14, 126, "Переваги в полі:", size=11, bold=True, color=FIELD, anchor="start"))
        y_cur = 146
        for p in c["pros"]:
            frags.append(circle(cx + 20, y_cur - 4, 3, fill=FIELD, stroke=FIELD))
            frags.append(text(cx + 28, y_cur, p, size=10.5, anchor="start"))
            y_cur += 22

        frags.append(line(cx + 14, y_cur + 2, cx + cw - 14, y_cur + 2, color="#e2e8f0", sw=1))
        y_cur += 20

        frags.append(text(cx + 14, y_cur, "Обмеження та вразливості:", size=11, bold=True, color=POS, anchor="start"))
        y_cur += 20
        for cn in c["cons"]:
            frags.append(circle(cx + 20, y_cur - 4, 3, fill=POS, stroke=POS))
            frags.append(text(cx + 28, y_cur, cn, size=10.5, anchor="start"))
            y_cur += 22

        # Плашка призначення внизу
        frags.append(rect(cx + 10, 375, cw - 20, 32, fill=FILL, stroke="#e2e8f0", sw=1, rx=4))
        frags.append(text(cx + cw / 2, 396, c["badge"], size=10, bold=True, color="#475569"))

    render(os.path.join(IMG_DIR, "touch-technologies-field.svg"), w, h, *frags)


def fig_thumb_zone_and_targets():
    """Зони досяжності великого пальця (Thumb Zone) та розмір польових кнопок."""
    w, h = 980, 490
    frags = []

    frags.append(text(w / 2, 26, "Ергономіка однорукого хвату (Thumb Zone) та розміри польових кнопок", size=15, bold=True))

    # Ліва половина: Схема екрана з зонами досяжності під правий хват
    frags.append(rect(40, 50, 420, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(250, 75, "Карта зон екрана при хваті однією рукою", size=13, bold=True, color="#0f172a"))

    # Корпус планшета / смартфона
    frags.append(rect(80, 95, 340, 355, fill="#1e293b", stroke="#0f172a", sw=2, rx=12))
    # Дисплей всередині
    frags.append(rect(95, 110, 310, 325, fill="#0f172a", stroke="#334155", sw=1, rx=6))

    # Червона зона (Hard / Danger Zone) — верхній лівий та верхній сектори
    frags.append(rect(100, 115, 300, 100, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    frags.append(text(250, 145, "Заборонена зона (Hard-to-Reach Zone)", size=11, bold=True, color="#991b1b"))
    frags.append(text(250, 166, "Статична телеметрія, статус-бар, системні індикатори.", size=10, color="#7f1d1d"))
    frags.append(text(250, 186, "Ніяких інтерактивних або критичних кнопок!", size=10, bold=True, color="#991b1b"))

    # Жовта зона (Stretch Zone) — середина
    frags.append(rect(100, 222, 300, 88, fill="#fef9c3", stroke="#eab308", sw=1.2, rx=4))
    frags.append(text(250, 248, "Зона розтягування (Stretch Zone)", size=11, bold=True, color="#854d0e"))
    frags.append(text(250, 268, "Вторинні налаштування, перемикання вкладок, списки.", size=10, color="#713f12"))
    frags.append(text(250, 288, "Потребує невеликого напруження кисті.", size=10, color="#713f12"))

    # Зелена зона (Natural Zone / Sweet Spot) — нижній правий сектор (дуга пальця)
    frags.append(rect(100, 318, 300, 110, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=4))
    frags.append(text(250, 342, "Природна зона (Natural Thumb Zone)", size=12, bold=True, color="#14532d"))
    frags.append(text(250, 362, "Головні органи: Arm/Disarm, зміна режиму, спуск, скидання.", size=10, color="#14532d"))
    frags.append(text(250, 380, "Швидкий доступ без зміни хвату і без ризику впустити пристрій.", size=9.5, bold=True, color="#14532d"))
    frags.append(text(250, 398, "Критичні дії — тільки з утриманням (Hold-to-Confirm)!", size=9.5, color="#15803d"))

    # Права половина: Порівняння розмірів кнопок і захисних інтервалів
    frags.append(rect(490, 50, 450, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(715, 75, "Розміри активних зон та захисні інтервали", size=13, bold=True, color="#0f172a"))

    # Варіант А: Офісна кнопка (помилка в полі)
    frags.append(rect(515, 105, 400, 145, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(715, 126, "Офісний / Мобільний стандарт (7–8 мм)", size=11.5, bold=True, color=POS))

    # Дві маленькі кнопки поруч
    frags.append(rect(540, 145, 80, 50, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(580, 174, "7 мм", size=10.5, bold=True, color=POS))
    frags.append(rect(630, 145, 80, 50, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(670, 174, "7 мм", size=10.5, bold=True, color=POS))

    # Пляма пальця в рукавиці перекриває обидві
    frags.append(circle(625, 170, 24, fill="none", stroke="#dc2626", sw=2))
    frags.append(text(800, 160, "Пляма рукавиці (18–20 мм)", size=10.5, bold=True, color=POS))
    frags.append(text(800, 178, "Перекриває 2 кнопки разом!", size=10, color=POS))
    frags.append(text(715, 230, "Результат: випадкове вмикання сусідніх функцій при тремтінні.", size=10, color="#7f1d1d"))

    # Варіант Б: Польовий тактильний стандарт
    frags.append(rect(515, 265, 400, 190, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(715, 287, "Польовий тактильний стандарт (14–16 мм + зазор)", size=11.5, bold=True, color=FIELD))

    # Дві великі кнопки з відчутним зазором
    frags.append(rect(540, 310, 140, 65, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(610, 340, "Кнопка 15 мм", size=11, bold=True, color=FIELD))
    frags.append(text(610, 358, "(90×65 px)", size=9.5, color="#15803d"))

    # Захисний інтервал
    frags.append(rect(685, 325, 30, 35, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=3))
    frags.append(text(700, 346, "4 мм", size=9.5, bold=True, color="#475569"))

    frags.append(rect(720, 310, 140, 65, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(790, 340, "Кнопка 15 мм", size=11, bold=True, color=FIELD))
    frags.append(text(790, 358, "(90×65 px)", size=9.5, color="#15803d"))

    frags.append(text(715, 398, "Мертва зона 3–5 мм запобігає одночасному спрацьовуванню.", size=10, color="#14532d"))
    frags.append(text(715, 416, "Закон Фіттса: збільшення площі компенсує тремор 2–5 Гц.", size=10, bold=True, color="#14532d"))
    frags.append(text(715, 434, "Чіткі контрастні рамки та колірна зміна при натисканні.", size=9.5, color=MUTED))

    render(os.path.join(IMG_DIR, "thumb-zone-and-targets.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_optical_bonding()
    fig_touch_technologies()
    fig_thumb_zone_and_targets()
    print("All figures generated successfully.")
