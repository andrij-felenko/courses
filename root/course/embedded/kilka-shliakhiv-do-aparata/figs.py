# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_multi_link_topology():
    W, H = 940, 480
    p = []

    # Бортовий комплекс (зліва)
    p.append(rect(20, 20, 220, 440, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(130, 48, "Бортовий комплекс (UAV)", size=14, bold=True, color=INK))
    
    # Внутрішні компоненти борту
    tb_fc, _, _ = textbox(130, 95, "Автопілот (FC)\nArduPilot / PX4\nUART MAVLink", size=11, fill="#e2e8f0", stroke="#64748b", pad=8)
    p.append(tb_fc)
    
    tb_comp, _, _ = textbox(130, 185, "Бортовий комп'ютер (SBC)\nMAVLink Multi-Router\n(Дедуплікатор і шейпер)", size=11, fill="#dbeafe", stroke=NEG, pad=8)
    p.append(tb_comp)
    
    p.append(arrow(130, 135, 130, 155, color=LINE, sw=1.5))
    
    # Бортові модеми
    tb_m1, _, _ = textbox(130, 265, "1. RF-модем (Point-to-Point)\n915 МГц / 2.4 ГГц (SiK / RFD900)", size=10, fill="#ecfdf5", stroke=FIELD, pad=6)
    tb_m2, _, _ = textbox(130, 335, "2. 4G/5G LTE USB-модем\nWireGuard тунель", size=10, fill="#eff6ff", stroke=NEG, pad=6)
    tb_m3, _, _ = textbox(130, 405, "3. Супутниковий модуль\nIridium SBD / Short Burst Data", size=10, fill="#fef2f2", stroke=POS, pad=6)
    p.append(tb_m1)
    p.append(tb_m2)
    p.append(tb_m3)
    
    p.append(arrow(130, 218, 130, 240, color=LINE, sw=1.2))
    p.append(arrow(90, 218, 70, 310, color=LINE, sw=1.2))
    p.append(arrow(70, 218, 50, 380, color=LINE, sw=1.2))

    # Середня частина: фізичні канали
    # Канал 1: Пряма радіолінія
    p.append(rect(270, 245, 380, 46, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(460, 265, "Канал 1: Пряма радіолінія (LoS RF)", size=11, bold=True, color=FIELD))
    p.append(text(460, 281, "RTT 20-40 мс · 64-250 кбіт/с · Безкоштовний · Обмежений рельєфом", size=9, color=MUTED))
    p.append(arrow(240, 268, 270, 268, color=FIELD, sw=1.5))
    p.append(arrow(650, 268, 680, 268, color=FIELD, sw=1.5))

    # Канал 2: Стільниковий інтернет через VPN-шлюз
    p.append(rect(270, 315, 380, 46, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(460, 335, "Канал 2: Стільниковий 4G/5G VPN (WireGuard)", size=11, bold=True, color=NEG))
    p.append(text(460, 351, "RTT 50-120 мс · 1-20 Мбіт/с · Покриття веж · Релей із білою IP", size=9, color=MUTED))
    p.append(arrow(240, 338, 270, 338, color=NEG, sw=1.5))
    p.append(arrow(650, 338, 680, 338, color=NEG, sw=1.5))

    # Канал 3: Супутник
    p.append(rect(270, 385, 380, 46, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(460, 405, "Канал 3: Супутниковий Satcom (Iridium L-Band)", size=11, bold=True, color=POS))
    p.append(text(460, 421, "RTT 1500-4000 мс · 340 байт/пакет · Глобальний · Платний трафік", size=9, color=MUTED))
    p.append(arrow(240, 408, 270, 408, color=POS, sw=1.5))
    p.append(arrow(650, 408, 680, 408, color=POS, sw=1.5))

    # Хмарний релей зверху посередині
    tb_vps, _, _ = textbox(460, 110, "Хмарний сервер-релей (VPS)\nWireGuard шлюз з публічною IP\n(З'єднує клієнтів за CGNAT)", size=11, fill="#f8fafc", stroke="#64748b", pad=8)
    p.append(tb_vps)
    p.append(line(460, 145, 460, 315, color=NEG, sw=1.2, dash="4,4"))

    # Наземний комплекс (справа)
    p.append(rect(680, 20, 240, 440, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    p.append(text(800, 48, "Наземна станція (GCS)", size=14, bold=True, color=INK))

    # Модеми станції
    tb_g1, _, _ = textbox(800, 265, "Наземний RF-модем\nUART / USB до ПК", size=10, fill="#ecfdf5", stroke=FIELD, pad=6)
    tb_g2, _, _ = textbox(800, 335, "Інтернет-зв'язок (LTE/LAN)\nКлієнт WireGuard тунелю", size=10, fill="#eff6ff", stroke=NEG, pad=6)
    tb_g3, _, _ = textbox(800, 405, "Супутниковий веб-шлюз\nTCP/UDP API Iridium", size=10, fill="#fef2f2", stroke=POS, pad=6)
    p.append(tb_g1)
    p.append(tb_g2)
    p.append(tb_g3)

    # Інтелектуальний маршрутизатор
    tb_grouter, _, _ = textbox(800, 185, "Multi-Link Failover Router\n• Моніторинг LQ / RTT\n• Анти-брязкання (гістерезис)\n• Дедуплікація MAVLink", size=11, fill="#fef3c7", stroke="#d97706", pad=8)
    p.append(tb_grouter)

    p.append(arrow(800, 240, 800, 222, color=LINE, sw=1.2))
    p.append(arrow(750, 312, 770, 222, color=LINE, sw=1.2))
    p.append(arrow(730, 382, 750, 222, color=LINE, sw=1.2))

    # Єдиний локальний віртуальний порт
    tb_gcs, _, _ = textbox(800, 95, "QGroundControl / Mission Planner\nЄдиний endpoint: UDP 127.0.0.1:14550\n(Прозора робота оператора)", size=11, fill="#e2e8f0", stroke="#475569", pad=8)
    p.append(tb_gcs)
    p.append(arrow(800, 148, 800, 128, color=LINE, sw=1.5))

    render(os.path.join(OUT, "multi-link-topology.svg"), W, H, *p)


def fig_failover_fsm_hysteresis():
    W, H = 940, 470
    p = []

    # Верхня половина: Графік зміни Link Quality з порогами гістерезису
    x0, y0 = 80, 220
    xw, yh = 780, 160

    # Сітка та рівні
    # 100%
    p.append(line(x0, y0 - yh, x0 + xw, y0 - yh, color="#e2e8f0", sw=1))
    p.append(text(x0 - 10, y0 - yh + 4, "100%", size=9, color=MUTED, anchor="end"))

    # Повернення (Recovery Threshold = 75%)
    y_rec = y0 - yh * 0.75
    p.append(line(x0, y_rec, x0 + xw, y_rec, color=FIELD, sw=1.2, dash="4,4"))
    p.append(text(x0 - 10, y_rec + 4, "75% Поріг повернення", size=9, color=FIELD, anchor="end", bold=True))

    # Скидання (Drop Threshold = 30%)
    y_drop = y0 - yh * 0.30
    p.append(line(x0, y_drop, x0 + xw, y_drop, color=POS, sw=1.2, dash="4,4"))
    p.append(text(x0 - 10, y_drop + 4, "30% Поріг скидання", size=9, color=POS, anchor="end", bold=True))

    # 0%
    p.append(line(x0, y0, x0 + xw, y0, color=INK, sw=1.5))
    p.append(text(x0 - 10, y0 + 4, "0%", size=9, color=MUTED, anchor="end"))
    p.append(text(x0 + xw, y0 + 18, "Час (секунди) →", size=10, color=MUTED, anchor="end"))

    # Вісь Y
    p.append(line(x0, y0, x0, y0 - yh - 10, color=INK, sw=1.5))
    p.append(text(x0, y0 - yh - 16, "Якість основного каналу (LQ)", size=11, bold=True, color=INK, anchor="start"))

    # Траєкторія сигналу LQ (плавне падіння, потім стрибки і відновлення)
    pts = [
        (x0, y0 - yh * 0.95),
        (x0 + 100, y0 - yh * 0.90),
        (x0 + 180, y0 - yh * 0.60),
        (x0 + 240, y0 - yh * 0.25), # нижче 30% -> Failover!
        (x0 + 300, y0 - yh * 0.15),
        (x0 + 360, y0 - yh * 0.40), # тимчасовий сплеск (не перемикаємось, бо < 75%)
        (x0 + 420, y0 - yh * 0.20),
        (x0 + 480, y0 - yh * 0.82), # перевищив 75% -> старт Hold-off timer!
        (x0 + 560, y0 - yh * 0.85), # тримається стабільно
        (x0 + 640, y0 - yh * 0.92), # таймер сплив -> перемикання на основний (Failback)!
        (x0 + xw, y0 - yh * 0.95)
    ]
    poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly, NEG))

    # Зони активного каналу на графіку
    # Зона 1: Основний RF активний
    p.append(rect(x0, 25, 240, 24, fill="#ecfdf5", stroke=FIELD, sw=1, rx=4))
    p.append(text(x0 + 120, 41, "Активний: Основний канал (RF)", size=10, bold=True, color=FIELD))

    # Маркер точки Failover
    p.append(circle(x0 + 240, y0 - yh * 0.25, 5, fill=POS, stroke="#ffffff", sw=1.5))
    tb_fo, _, _ = textbox(x0 + 240, 85, "LQ < 30%\nПеремикання на 4G LTE", size=9, fill="#fef2f2", stroke=POS, pad=5)
    p.append(tb_fo)
    # З'єднувальна лінія від маркеру до бокса
    p.append(line(x0 + 240, 102, x0 + 240, y0 - yh * 0.25 - 5, color=POS, sw=1.2, dash="3,3"))
    p.append(line(x0 + 240, y0 - yh * 0.25 + 5, x0 + 240, y0, color=POS, sw=1.2, dash="3,3"))

    # Зона 2: Резервний LTE активний
    p.append(rect(x0 + 240, 25, 400, 24, fill="#eff6ff", stroke=NEG, sw=1, rx=4))
    p.append(text(x0 + 440, 41, "Активний: Резервний канал (4G LTE VPN)", size=10, bold=True, color=NEG))

    # Зона витримки (Hold-off time)
    p.append(rect(x0 + 480, 85, 160, 34, fill="#fef3c7", stroke="#d97706", sw=1, rx=4))
    p.append(text(x0 + 560, 100, "Hold-off таймер (T = 5 c)", size=9, bold=True, color="#92400e"))
    p.append(text(x0 + 560, 113, "Захист від брязкання", size=9, color="#92400e"))
    p.append(line(x0 + 480, 120, x0 + 480, y0, color="#d97706", sw=1.2, dash="3,3"))
    p.append(line(x0 + 640, 120, x0 + 640, y0, color=FIELD, sw=1.2, dash="3,3"))

    # Зона 3: Повернення на RF
    p.append(rect(x0 + 640, 25, xw - 640, 24, fill="#ecfdf5", stroke=FIELD, sw=1, rx=4))
    p.append(text(x0 + 640 + (xw - 640) / 2, 41, "Повернення на RF", size=10, bold=True, color=FIELD))

    # Нижня частина: Кінцевий автомат (FSM)
    y_fsm = 370
    tb_s1, _, _ = textbox(160, y_fsm, "СТАН 1: PRIMARY_ACTIVE\n• Весь трафік через RF\n• LTE в режимі Standby (ping 1 Гц)", size=10, fill="#ecfdf5", stroke=FIELD, pad=8)
    tb_s2, _, _ = textbox(470, y_fsm, "СТАН 2: BACKUP_ACTIVE\n• Трафік переведено на 4G LTE\n• Шейпінг важкої телеметрії", size=10, fill="#eff6ff", stroke=NEG, pad=8)
    tb_s3, _, _ = textbox(780, y_fsm, "СТАН 3: RECOVERY_HOLD\n• LQ RF > 75%, працює таймер\n• Трафік ще в LTE, захист від flapping", size=10, fill="#fef3c7", stroke="#d97706", pad=8)
    
    p.append(tb_s1)
    p.append(tb_s2)
    p.append(tb_s3)

    # Стрілки FSM
    p.append(arrow(280, y_fsm - 15, 350, y_fsm - 15, color=POS, sw=1.5))
    p.append(text(315, y_fsm - 23, "LQ_RF < 30%", size=9, bold=True, color=POS))

    p.append(arrow(590, y_fsm - 15, 660, y_fsm - 15, color="#d97706", sw=1.5))
    p.append(text(625, y_fsm - 23, "LQ_RF > 75%", size=9, bold=True, color="#d97706"))

    # Повернення зі стану 3 у стан 1
    p.append(arrow(780, y_fsm + 38, 780, y_fsm + 65, color=FIELD, sw=1.5))
    p.append(line(780, y_fsm + 65, 160, y_fsm + 65, color=FIELD, sw=1.5))
    p.append(arrow(160, y_fsm + 65, 160, y_fsm + 38, color=FIELD, sw=1.5))
    p.append(text(470, y_fsm + 58, "Таймер стабілізації T_hold сплив успішно → Повернення на основний RF", size=9, bold=True, color=FIELD))

    # Скидання зі стану 3 назад у стан 2 при зриві сигналу
    p.append(arrow(670, y_fsm + 22, 580, y_fsm + 22, color=POS, sw=1.2))
    p.append(text(625, y_fsm + 34, "Зрив LQ < 75%", size=9, color=POS))

    render(os.path.join(OUT, "failover-fsm-hysteresis.svg"), W, H, *p)


def fig_deduplication_pipeline():
    W, H = 940, 420
    p = []

    # Конвеєр дедуплікації та розумної маршрутизації
    # Зліва: Вхідні пакети з двох фізичних лінків
    tb_in1, _, _ = textbox(110, 100, "Вхідний лінк 1 (RF)\n[sys=1, comp=1, seq=42]\nMSG: GLOBAL_POSITION_INT", size=10, fill="#ecfdf5", stroke=FIELD, pad=6)
    tb_in2, _, _ = textbox(110, 200, "Вхідний лінк 2 (LTE)\n[sys=1, comp=1, seq=42]\nMSG: GLOBAL_POSITION_INT\n(Дублікат із затримкою +35мс)", size=10, fill="#eff6ff", stroke=NEG, pad=6)
    tb_in3, _, _ = textbox(110, 320, "Вхідний лінк 2 (LTE)\n[sys=1, comp=1, seq=43]\nMSG: COMMAND_ACK", size=10, fill="#eff6ff", stroke=NEG, pad=6)
    p.append(tb_in1)
    p.append(tb_in2)
    p.append(tb_in3)

    # Блок екстракції ключа MAVLink
    tb_key, _, _ = textbox(320, 200, "Екстрактор MAVLink заголовка\nФормування ключа пакета:\nKey = (sysid, compid, msgid, seq)\nПеревірка CRC extra", size=11, fill="#f1f5f9", stroke="#64748b", pad=8)
    p.append(tb_key)

    p.append(arrow(215, 100, 260, 160, color=FIELD, sw=1.5))
    p.append(arrow(220, 200, 240, 200, color=NEG, sw=1.5))
    p.append(arrow(215, 320, 260, 240, color=NEG, sw=1.5))

    # Блок дедуплікатора (LRU / Sliding Window)
    tb_dedup, _, _ = textbox(540, 200, "Ковзне вікно дедуплікації\n(LRU Ring Buffer, N = 256)\nЧи є ключ у вікні останніх T мс?", size=11, fill="#fef3c7", stroke="#d97706", pad=8)
    p.append(tb_dedup)
    p.append(arrow(400, 200, 440, 200, color=LINE, sw=1.5))

    # Гілка ДУБЛІКАТ -> DROP
    p.append(arrow(540, 140, 540, 80, color=POS, sw=1.5))
    tb_drop, _, _ = textbox(540, 60, "ДУБЛІКАТ: ПАКЕТ ВЖЕ ОБРОБЛЕНО\nСкидання (DROP) без навантаження шини", size=10, fill="#fef2f2", stroke=POS, pad=6)
    p.append(tb_drop)
    p.append(text(555, 115, "ТАК (знайдено)", size=9, bold=True, color=POS))

    # Гілка УНІКАЛЬНИЙ -> Шейпінг і Маршрутизація
    p.append(arrow(640, 200, 690, 200, color=FIELD, sw=1.5))
    p.append(text(665, 188, "НІ (новий)", size=9, bold=True, color=FIELD))

    # Блок політик трафіку та шейпінгу
    tb_policy, _, _ = textbox(810, 200, "Фільтр політик трафіку\nта обмеження смуги:\n• High-rate IMU → пропуск лише в RF\n• Критичні команди → найвищий пріоритет\n• Оновлення вікна LRU", size=10, fill="#e0e7ff", stroke="#4338ca", pad=8)
    p.append(tb_policy)

    # Вихід до споживача (GCS / FC)
    p.append(arrow(810, 280, 810, 340, color=FIELD, sw=1.8))
    tb_out, _, _ = textbox(810, 370, "Вихідний сокет до споживача\n(QGroundControl / Автопілот)\nОчищений потік без дублікатів і провалів", size=10, fill="#ecfdf5", stroke=FIELD, pad=6)
    p.append(tb_out)

    render(os.path.join(OUT, "deduplication-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_multi_link_topology()
    fig_failover_fsm_hysteresis()
    fig_deduplication_pipeline()
    print("Figures generated successfully.")
