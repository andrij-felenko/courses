# -*- coding: utf-8 -*-
"""Генератор фігур для теми 'Три форми системи: дім, парк трекерів, апарат і станція'"""

import sys, os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_three_archetypes():
    """Фігура 1: Три архетипи підключених систем — порівняльна архітектура."""
    w, h = 920, 480
    frags = []

    # Колонка 1: Розумний дім (Smart Home)
    col1_x = 160
    frags.append(rect(20, 20, 280, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    b1, _, _ = textbox(col1_x, 50, "1. Розумний дім (LAN)", size=15, bold=True, color="#1e3a8a", fill="#e0f2fe", stroke="#0284c7")
    frags.append(b1)
    
    # Схема Smart Home
    b_hub, _, _ = textbox(col1_x, 110, "Локальний хаб / Шлюз\n(Home Assistant / Matter)", size=12, pad=6, fill="#ffffff", stroke="#0284c7")
    frags.append(b_hub)
    
    b_s1, _, _ = textbox(col1_x - 65, 185, "Давач руху\n(CR2032, Zigbee)", size=11, pad=5, fill="#ffffff", stroke="#94a3b8")
    b_s2, _, _ = textbox(col1_x + 65, 185, "Реле світла\n(230V, Thread)", size=11, pad=5, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_s1)
    frags.append(b_s2)
    frags.append(arrow(col1_x - 65, 160, col1_x - 25, 130, color="#0284c7", sw=1.5))
    frags.append(arrow(col1_x + 25, 130, col1_x + 65, 160, color="#0284c7", sw=1.5))
    
    char1 = (
        "Характеристики:\n"
        "• Масштаб: 10–100 вузлів / приміщення\n"
        "• Живлення: Мережа 230 В + батарейки\n"
        "• Затримка: <50–100 мс (людський фактор)\n"
        "• Топологія: Чарунка (Mesh) / Зірка\n"
        "• Автономія: Повна робота без Інтернету\n"
        "• Протоколи: Zigbee, Thread, Matter, Wi-Fi"
    )
    frags.append(rect(30, 240, 260, 205, fill="#ffffff", stroke="#e2e8f0", rx=6))
    frags.append(mtext(40, 265, char1.split("\n"), size=11, anchor="start", color="#334155", lh=1.4))

    # Колонка 2: Парк трекерів (Fleet Telematics)
    col2_x = 460
    frags.append(rect(320, 20, 280, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    b2, _, _ = textbox(col2_x, 50, "2. Парк трекерів (WAN)", size=15, bold=True, color="#14532d", fill="#dcfce7", stroke="#16a34a")
    frags.append(b2)
    
    # Схема Fleet
    b_cloud, _, _ = textbox(col2_x, 110, "Хмарний сервер / Брокер\n(MQTT / CoAP / HTTPS)", size=12, pad=6, fill="#ffffff", stroke="#16a34a")
    frags.append(b_cloud)
    
    b_t1, _, _ = textbox(col2_x - 65, 185, "Трекер #1 (Сон 99%)\nNB-IoT / LTE-M", size=11, pad=5, fill="#ffffff", stroke="#94a3b8")
    b_t2, _, _ = textbox(col2_x + 65, 185, "Трекер #N (Сон 99%)\nLoRaWAN / GNSS", size=11, pad=5, fill="#ffffff", stroke="#94a3b8")
    frags.append(b_t1)
    frags.append(b_t2)
    frags.append(arrow(col2_x - 65, 160, col2_x - 25, 130, color="#16a34a", sw=1.5))
    frags.append(arrow(col2_x + 65, 160, col2_x + 25, 130, color="#16a34a", sw=1.5))
    
    char2 = (
        "Характеристики:\n"
        "• Масштаб: 1 000 – 1 000 000+ вузлів\n"
        "• Живлення: Li-SOCl2 батарея (3–10 років)\n"
        "• Трафік: 99% Uplink (асиметричний)\n"
        "• Топологія: Зірка через вежі оператора\n"
        "• Буфер: Flash-пам'ять на випадок офлайну\n"
        "• Протоколи: NB-IoT, LoRaWAN, CoAP, UDP"
    )
    frags.append(rect(330, 240, 260, 205, fill="#ffffff", stroke="#e2e8f0", rx=6))
    frags.append(mtext(340, 265, char2.split("\n"), size=11, anchor="start", color="#334155", lh=1.4))

    # Колонка 3: Апарат і станція (Machine-to-Station / P2P)
    col3_x = 760
    frags.append(rect(620, 20, 280, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    b3, _, _ = textbox(col3_x, 50, "3. Апарат і станція (P2P)", size=15, bold=True, color="#7f1d1d", fill="#fee2e2", stroke="#dc2626")
    frags.append(b3)
    
    # Схема P2P
    b_gcs, _, _ = textbox(col3_x - 55, 130, "Пульт / GCS\n(Станція)", size=12, pad=6, fill="#ffffff", stroke="#dc2626")
    b_uav, _, _ = textbox(col3_x + 55, 130, "Апарат / БПЛА\n(Борт)", size=12, pad=6, fill="#ffffff", stroke="#dc2626")
    frags.extend([b_gcs, b_uav])
    frags.append(arrow(col3_x - 10, 120, col3_x + 15, 120, color="#dc2626", sw=1.8))
    frags.append(arrow(col3_x + 15, 140, col3_x - 10, 140, color="#dc2626", sw=1.8))
    frags.append(text(col3_x + 2, 110, "Керування (<20 мс)", size=9, color="#dc2626", bold=True))
    frags.append(text(col3_x + 2, 155, "Телеметрія + Відео", size=9, color="#dc2626", bold=True))
    
    char3 = (
        "Характеристики:\n"
        "• Масштаб: Точно 2 вузли (двоточковий лінк)\n"
        "• Живлення: Бортовий LiPo / акумулятор\n"
        "• Затримка: Жорсткий реал-тайм (<10–30 мс)\n"
        "• Топологія: Прямий P2P без інфраструктури\n"
        "• Безпека: Стійкість до РЕБ, FHSS, Fail-safe\n"
        "• Протоколи: MAVLink, CRSF, ESP-NOW, RTP"
    )
    frags.append(rect(630, 240, 260, 205, fill="#ffffff", stroke="#e2e8f0", rx=6))
    frags.append(mtext(640, 265, char3.split("\n"), size=11, anchor="start", color="#334155", lh=1.4))

    render(os.path.join(IMG_DIR, "three-archetypes-overview.svg"), w, h, *frags)


def fig_smart_home_latency():
    """Фігура 2: Затримка в розумному домі — локальний контур проти хмарного."""
    w, h = 880, 420
    frags = []

    # Заголовок зверху
    frags.append(text(w/2, 25, "Порівняння контурів керування в розумному домі", size=16, bold=True, color="#0f172a"))

    # Локальний контур (Local Loop) - Зелений/Синій
    frags.append(rect(30, 55, 820, 160, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    frags.append(text(150, 80, "Локальний контур (LAN / Zigbee / Thread)", size=14, bold=True, color="#15803d", anchor="start"))
    
    b_sw1, _, _ = textbox(110, 140, "Настінний вимикач\n(Вхід користувача)", size=11, pad=6, fill="#ffffff", stroke="#16a34a")
    b_hub1, _, _ = textbox(360, 140, "Локальний хаб\n(Обробка автоматизації)", size=11, pad=6, fill="#ffffff", stroke="#16a34a")
    b_act1, _, _ = textbox(610, 140, "Світильник / Реле\n(Виконавчий механізм)", size=11, pad=6, fill="#ffffff", stroke="#16a34a")
    b_res1, _, _ = textbox(775, 140, "Затримка:\n~20–45 мс\n(Миттєво)", size=11, pad=6, fill="#dcfce7", stroke="#15803d", bold=True)
    
    frags.extend([b_sw1, b_hub1, b_act1, b_res1])
    frags.append(arrow(190, 140, 270, 140, color="#16a34a", sw=1.8))
    frags.append(text(230, 130, "10 мс", size=10, color="#16a34a", bold=True))
    frags.append(arrow(450, 140, 520, 140, color="#16a34a", sw=1.8))
    frags.append(text(485, 130, "15 мс", size=10, color="#16a34a", bold=True))
    frags.append(arrow(700, 140, 725, 140, color="#16a34a", sw=1.8))
    
    frags.append(text(150, 195, "✓ Працює без зв'язку з Інтернетом  ✓ Людина не відчуває затримки (<100 мс)", size=11, color="#166534", anchor="start"))

    # Хмарний контур (Cloud Loop) - Червоний/Помаранчевий
    frags.append(rect(30, 235, 820, 160, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    frags.append(text(150, 260, "Хмарний контур (Wi-Fi → Інтернет → Хмара → Wi-Fi)", size=14, bold=True, color="#b91c1c", anchor="start"))
    
    b_sw2, _, _ = textbox(100, 320, "Wi-Fi вимикач\n(MQTT Client)", size=11, pad=5, fill="#ffffff", stroke="#ef4444")
    b_rtr, _, _ = textbox(270, 320, "Домашній роутер\n(NAT / Wi-Fi AP)", size=11, pad=5, fill="#ffffff", stroke="#ef4444")
    b_cld, _, _ = textbox(470, 320, "Хмарний сервер\n(AWS / Azure / Tuya)", size=11, pad=5, fill="#ffffff", stroke="#ef4444")
    b_act2, _, _ = textbox(660, 320, "Wi-Fi лампа\n(MQTT Client)", size=11, pad=5, fill="#ffffff", stroke="#ef4444")
    b_res2, _, _ = textbox(780, 320, "Затримка:\n350–1200 мс\n(Дратує!)", size=11, pad=5, fill="#fee2e2", stroke="#b91c1c", bold=True)
    
    frags.extend([b_sw2, b_rtr, b_cld, b_act2, b_res2])
    frags.append(arrow(165, 320, 195, 320, color="#ef4444", sw=1.5))
    frags.append(arrow(345, 320, 385, 320, color="#ef4444", sw=1.5))
    frags.append(text(365, 310, "WAN", size=9, color="#ef4444", bold=True))
    frags.append(arrow(555, 320, 595, 320, color="#ef4444", sw=1.5))
    frags.append(text(575, 310, "WAN", size=9, color="#ef4444", bold=True))
    frags.append(arrow(725, 320, 735, 320, color="#ef4444", sw=1.5))
    
    frags.append(text(150, 375, "✗ Падає при обриві провайдера  ✗ Затримка помітна оку  ✗ Трафік і сертифікати TLS", size=11, color="#991b1b", anchor="start"))

    render(os.path.join(IMG_DIR, "smart-home-latency-flow.svg"), w, h, *frags)


def fig_tracker_energy_profile():
    """Фігура 3: Енергетичний профіль автономного трекера — цикл сну та передачі."""
    w, h = 880, 420
    frags = []

    frags.append(text(w/2, 25, "Профіль споживання струму польового трекера під час сесії зв'язку", size=15, bold=True, color="#0f172a"))

    # Графік: вісь X (Час), вісь Y (Струм)
    gx, gy, gw, gh = 80, 60, 760, 240
    frags.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", rx=4))

    # Сітка та мітки по Y
    frags.append(line(gx, gy + gh * 0.2, gx + gw, gy + gh * 0.2, color="#f1f5f9", sw=1))
    frags.append(line(gx, gy + gh * 0.5, gx + gw, gy + gh * 0.5, color="#f1f5f9", sw=1))
    frags.append(line(gx, gy + gh * 0.8, gx + gw, gy + gh * 0.8, color="#f1f5f9", sw=1))
    
    frags.append(text(gx - 10, gy + gh * 0.1, "300 мА", size=10, anchor="end", color="#64748b"))
    frags.append(text(gx - 10, gy + gh * 0.5, "30 мА", size=10, anchor="end", color="#64748b"))
    frags.append(text(gx - 10, gy + gh * 0.85, "5 мА", size=10, anchor="end", color="#64748b"))
    frags.append(text(gx - 10, gy + gh - 5, "2.5 мкА", size=10, anchor="end", color="#16a34a", bold=True))

    y_sleep = gy + gh - 6
    y_mcu = gy + gh * 0.85
    y_gnss = gy + gh * 0.5
    y_tx = gy + gh * 0.12
    y_rx = gy + gh * 0.45

    poly_pts = [
        (80, y_sleep), (160, y_sleep),
        (160, y_mcu), (230, y_mcu),
        (230, y_gnss), (430, y_gnss),
        (430, y_tx), (460, y_tx), (480, y_mcu), (510, y_tx), (540, y_tx), (560, y_mcu), (590, y_tx), (630, y_tx),
        (630, y_rx), (700, y_rx),
        (700, y_sleep), (840, y_sleep)
    ]
    
    # Малюємо заливку кривої
    svg_poly = " ".join(["%.1f,%.1f" % pt for pt in poly_pts]) + (" %.1f,%.1f 80,%.1f" % (840, gy+gh, gy+gh))
    frags.append('<polygon points="%s" fill="#eff6ff" stroke="none"/>' % svg_poly)
    
    # Лінія профілю
    svg_line = " ".join(["%.1f,%.1f" % pt for pt in poly_pts])
    frags.append('<polyline points="%s" fill="none" stroke="#2563eb" stroke-width="2.5"/>' % svg_line)

    # Вертикальні роздільники фаз і підписи
    frags.append(line(160, gy, 160, gy + gh, color="#cbd5e1", sw=1, dash="3,3"))
    frags.append(line(230, gy, 230, gy + gh, color="#cbd5e1", sw=1, dash="3,3"))
    frags.append(line(430, gy, 430, gy + gh, color="#cbd5e1", sw=1, dash="3,3"))
    frags.append(line(700, gy, 700, gy + gh, color="#cbd5e1", sw=1, dash="3,3"))

    frags.append(text(120, gy + 20, "Глибокий сон", size=10, bold=True, color="#16a34a"))
    frags.append(text(120, gy + 35, "99.9% часу", size=9, color="#64748b"))

    frags.append(text(195, gy + 20, "МК активний", size=10, bold=True, color="#1e293b"))
    frags.append(text(195, gy + 35, "~50 мс", size=9, color="#64748b"))

    frags.append(text(330, gy + 20, "GNSS фіксація координат", size=10, bold=True, color="#d97706"))
    frags.append(text(330, gy + 35, "~12–25 с (25 мА)", size=9, color="#64748b"))

    frags.append(text(565, gy + 20, "Модем LTE-M / NB-IoT передача", size=10, bold=True, color="#dc2626"))
    frags.append(text(565, gy + 35, "Імпульси до 350 мА (~4–8 с)", size=9, color="#64748b"))

    frags.append(text(770, gy + 20, "Глибокий сон", size=10, bold=True, color="#16a34a"))
    frags.append(text(770, gy + 35, "I_sleep = 2.5 мкА", size=9, color="#64748b"))

    # Блок резюме внизу
    frags.append(rect(80, 315, 760, 90, fill="#f8fafc", stroke="#e2e8f0", rx=6))
    summary_text = (
        "Енергетичний підсумок: 1 передача на годину витрачає ~0.15 мА·год енергії.\n"
        "Батарея Li-SOCl2 ємністю 8500 мА·год забезпечує: 8500 / (0.15 + 0.0025·24·30.5) ≈ 5.5 років автономної роботи.\n"
        "Якщо модем не може знайти мережу і шукає вежу 2 хвилини — батарея виснажується у 20 разів швидше!"
    )
    frags.append(mtext(95, 335, summary_text.split("\n"), size=11, anchor="start", color="#334155", lh=1.4))

    render(os.path.join(IMG_DIR, "tracker-energy-profile.svg"), w, h, *frags)


def fig_p2p_pipeline():
    """Фігура 4: Магістраль зв'язку апарат-станція — пріоритетні канали та Fail-Safe."""
    w, h = 940, 440
    frags = []

    frags.append(text(w/2, 25, "Архітектура каналу апарат-станція (P2P Link & Fail-Safe)", size=16, bold=True, color="#0f172a"))

    # Ліва колонка: Наземна станція (GCS)
    frags.append(rect(15, 55, 250, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    b_gcs_hdr, _, _ = textbox(140, 85, "Наземна станція (GCS / Пульт)", size=12, bold=True, color="#1e293b", fill="#e2e8f0", stroke="#94a3b8")
    frags.append(b_gcs_hdr)
    
    b_g1, _, _ = textbox(140, 140, "Джойстики керування\n(50 Гц, RT-потік)", size=11, pad=5, fill="#fee2e2", stroke="#ef4444")
    b_g2, _, _ = textbox(140, 205, "Екран телеметрії\n(MAVLink парсер)", size=11, pad=5, fill="#fef3c7", stroke="#f59e0b")
    b_g3, _, _ = textbox(140, 270, "Відеодекодер H.264\n(FPV дисплей / шолом)", size=11, pad=5, fill="#e0f2fe", stroke="#0284c7")
    frags.extend([b_g1, b_g2, b_g3])
    
    b_mux1, _, _ = textbox(140, 355, "Пріоритетний мультиплексор\n(QoS: Команди > Дані > Відео)", size=10, pad=5, fill="#ffffff", stroke="#475569")
    frags.append(b_mux1)

    # Центральна колонка: Радіоефір / P2P Лінк
    frags.append(rect(280, 55, 380, 365, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(470, 85, "Прямий радіолінк (868/915 МГц / 2.4/5.8 ГГц)", size=12, bold=True, color="#334155"))

    # Стрілки каналів
    frags.append(arrow(240, 140, 700, 140, color="#dc2626", sw=2.2))
    frags.append(text(470, 128, "Канал 1: Команди RC (Затримка <15 мс, Loss-Tolerant)", size=10, bold=True, color="#dc2626"))

    frags.append(arrow(700, 205, 240, 205, color="#d97706", sw=2.0))
    frags.append(text(470, 193, "Канал 2: Телеметрія борту (10–20 Гц, Heartbeat)", size=10, bold=True, color="#d97706"))

    frags.append(arrow(700, 270, 240, 270, color="#0284c7", sw=1.8))
    frags.append(text(470, 258, "Канал 3: Цифрове відео (1–5 Мбіт/с, UDP стрим)", size=10, bold=True, color="#0284c7"))

    # Блок завад / РЕБ
    frags.append(rect(310, 310, 320, 95, fill="#ffffff", stroke="#cbd5e1", rx=6))
    frags.append(text(470, 330, "Захист у ворожому ефірі (РЕБ / Завади):", size=11, bold=True, color="#475569"))
    reb_text = (
        "• FHSS: стрибки по 50–100 каналах за секунду\n"
        "• FEC: випереджальне виправлення помилок (Reed-Solomon)\n"
        "• Адаптивний бітрейт при падінні SNR"
    )
    frags.append(mtext(320, 350, reb_text.split("\n"), size=9, anchor="start", color="#475569", lh=1.3))

    # Права колонка: Бортовий комп'ютер / БПЛА
    frags.append(rect(675, 55, 250, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    b_uav_hdr, _, _ = textbox(800, 85, "Борт апарата (Автопілот / МК)", size=12, bold=True, color="#1e293b", fill="#e2e8f0", stroke="#94a3b8")
    frags.append(b_uav_hdr)

    b_u1, _, _ = textbox(800, 140, "Контролер польоту\n(Мікшер моторів / PID)", size=11, pad=5, fill="#fee2e2", stroke="#ef4444")
    b_u2, _, _ = textbox(800, 205, "Сенсори та GNSS\n(Генератор MAVLink)", size=11, pad=5, fill="#fef3c7", stroke="#f59e0b")
    b_u3, _, _ = textbox(800, 270, "Камера + Енкодер\n(RTP транслятор)", size=11, pad=5, fill="#e0f2fe", stroke="#0284c7")
    frags.extend([b_u1, b_u2, b_u3])

    # Fail-safe блок
    b_fs, _, _ = textbox(800, 355, "Таймер Fail-Safe Watchdog\n(Втрата лінка > 1.5 с → Повернення)", size=10, pad=5, fill="#fee2e2", stroke="#dc2626", bold=True)
    frags.append(b_fs)

    render(os.path.join(IMG_DIR, "p2p-telemetry-control-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_three_archetypes()
    fig_smart_home_latency()
    fig_tracker_energy_profile()
    fig_p2p_pipeline()
    print("Усі 4 фігури успішно згенеровано.")
