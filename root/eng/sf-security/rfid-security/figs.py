# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра відповідно до стилю курсу
COLOR_READER = FIELD       # Зчитувач (зелений)
COLOR_TAG    = "#8e44ad"   # Тег (фіолетовий)
COLOR_ATTACK = POS         # Атакуючий / Перехоплення (червоний)
COLOR_BUS    = NEG         # Шина / Лінк (синій)
COLOR_NEUT   = INK

# ── Фігура 1: Індуктивний зв'язок та зона перехоплення ───────────────────────
def fig_rfid_coupling_eavesdropping():
    W, H = 820, 360
    p = []

    # Заголовок / Пояснення нагорі
    b, _, _ = textbox(410, 32,
                      "Зв'язок RFID/NFC: індуктивне ближнє поле (5 см) проти перехоплення в дальній зоні (15 м)",
                      size=13, fill=BG, stroke=MUTED, bold=True)
    p.append(b)

    # Зчитувач (Reader)
    p.append(rect(40, 90, 160, 180, fill="#e8f8f5", stroke=COLOR_READER, sw=2, rx=8))
    p.append(text(120, 120, "Зчитувач (Reader)", size=14, color=COLOR_READER, bold=True))
    p.append(text(120, 145, "Генератор 13.56 МГц", size=11, color=INK))
    # Котушка зчитувача
    p.append(rect(180, 160, 12, 90, fill=COLOR_READER, stroke=COLOR_READER, rx=2))
    p.append(text(120, 200, "Потужність P_TX", size=11, color=INK))
    p.append(text(120, 220, "~100–500 мВт", size=11, color=MUTED))

    # Магнітні лінії ближнього поля H (Near-Field)
    for r in [35, 60, 85]:
        p.append(f'<path d="M 192 {205-r} A {r} {r*0.7} 0 0 1 192 {205+r}" fill="none" stroke="{COLOR_READER}" stroke-width="1.5" stroke-dasharray="4 3"/>')

    # Пасивний тег (Tag)
    p.append(rect(290, 110, 140, 140, fill="#f4ecf7", stroke=COLOR_TAG, sw=2, rx=8))
    p.append(rect(280, 160, 10, 70, fill=COLOR_TAG, stroke=COLOR_TAG, rx=2))
    p.append(text(360, 140, "Пасивний тег", size=14, color=COLOR_TAG, bold=True))
    p.append(text(360, 170, "LC-контур", size=11, color=INK))
    p.append(text(360, 195, "Живлення від H-поля", size=10, color=MUTED))
    p.append(text(360, 215, "Load Modulation", size=10, color=COLOR_TAG, bold=True))

    # Лінія робочої відстані
    p.append(line(192, 275, 280, 275, color=COLOR_READER, sw=1.5))
    p.append(arrow(220, 275, 192, 275, color=COLOR_READER, sw=1.5))
    p.append(arrow(250, 275, 280, 275, color=COLOR_READER, sw=1.5))
    p.append(text(236, 295, "d_read ≈ 2–5 см", size=12, color=COLOR_READER, bold=True))
    p.append(text(236, 312, "(Реактивне H-поле)", size=10, color=MUTED))

    # Радіаційне згасання в дальню зону (Far-Field leakage)
    for radius in [120, 180, 240, 300]:
        p.append(f'<path d="M 192 {205-radius*0.6} A {radius} {radius*0.6} 0 0 1 192 {205+radius*0.6}" fill="none" stroke="{COLOR_ATTACK}" stroke-width="1.2" stroke-dasharray="2 3"/>')

    # Атакуючий перехоплювач (SDR Sniffer)
    p.append(rect(580, 100, 190, 160, fill="#fadbd8", stroke=COLOR_ATTACK, sw=2, rx=8))
    p.append(text(675, 130, "Приймач зловмисника", size=13, color=COLOR_ATTACK, bold=True))
    p.append(text(675, 155, "Спрямована антена + SDR", size=11, color=INK))
    p.append(text(675, 180, "Малошумний підсилювач (LNA)", size=10, color=MUTED))
    p.append(text(675, 200, "Перехоплення випромінювання", size=10, color=COLOR_ATTACK))
    p.append(text(675, 220, "несучої та модуляції тега", size=10, color=COLOR_ATTACK))

    # Стрілка дальності перехоплення
    p.append(line(192, 330, 675, 330, color=COLOR_ATTACK, sw=1.8, dash="5 3"))
    p.append(arrow(350, 330, 192, 330, color=COLOR_ATTACK, sw=1.8))
    p.append(arrow(520, 330, 675, 330, color=COLOR_ATTACK, sw=1.8))
    p.append(text(433, 348, "d_eavesdrop ≈ 5–20 м (Перехоплення сигналу зчитувача й тега)", size=12, color=COLOR_ATTACK, bold=True))

    render(os.path.join(OUT, "rfid-coupling-eavesdropping.svg"), W, H, *p,
           title="Індуктивний зв'язок RFID та зона радіоперехоплення")

# ── Фігура 2: Топологія атаки ретрансляції (Relay Attack / Wormhole) ───────────
def fig_relay_attack_topology():
    W, H = 840, 320
    p = []

    p.append(text(420, 25, "Топологія атаки ретрансляції (Relay / Wormhole Attack)", size=14, color=INK, bold=True))

    # Жертва-Зчитувач (наприклад, Авто / Дверний замок)
    p.append(rect(30, 80, 150, 140, fill="#e8f8f5", stroke=COLOR_READER, sw=2, rx=8))
    p.append(text(105, 110, "Легітимний", size=13, color=COLOR_READER, bold=True))
    p.append(text(105, 130, "Зчитувач", size=13, color=COLOR_READER, bold=True))
    p.append(text(105, 160, "(Авто / Замок)", size=11, color=MUTED))
    p.append(text(105, 185, "Очікує d ≤ 5 см", size=10, color=COLOR_READER))

    # Посередник 1 (Proxy Tag - біля зчитувача)
    p.append(rect(230, 80, 150, 140, fill="#fadbd8", stroke=COLOR_ATTACK, sw=2, rx=8))
    p.append(text(305, 110, "Атакуючий 1", size=13, color=COLOR_ATTACK, bold=True))
    p.append(text(305, 130, "(Proxy Tag)", size=12, color=COLOR_ATTACK, bold=True))
    p.append(text(305, 160, "Емулює картку", size=10, color=INK))
    p.append(text(305, 185, "Біля замку", size=10, color=MUTED))

    # Канал ретрансляції (Fast Relay Link: Wi-Fi / 5G / RF)
    p.append(line(380, 150, 460, 150, color=COLOR_ATTACK, sw=3.0))
    p.append(arrow(410, 150, 460, 150, color=COLOR_ATTACK, sw=3.0))
    p.append(arrow(430, 150, 380, 150, color=COLOR_ATTACK, sw=3.0))
    p.append(text(420, 130, "Швидкісний радіоміст", size=11, color=COLOR_ATTACK, bold=True))
    p.append(text(420, 175, "Wi-Fi / 5G / Sub-GHz", size=10, color=MUTED))
    p.append(text(420, 195, "(Відстань сотні метрів)", size=10, color=COLOR_ATTACK))

    # Посередник 2 (Proxy Reader - біля жертви)
    p.append(rect(460, 80, 150, 140, fill="#fadbd8", stroke=COLOR_ATTACK, sw=2, rx=8))
    p.append(text(535, 110, "Атакуючий 2", size=13, color=COLOR_ATTACK, bold=True))
    p.append(text(535, 130, "(Proxy Reader)", size=12, color=COLOR_ATTACK, bold=True))
    p.append(text(535, 160, "Зчитує тег", size=10, color=INK))
    p.append(text(535, 185, "Біля кишені жертви", size=10, color=MUTED))

    # Легітимний тег (в кишені жертви)
    p.append(rect(660, 80, 150, 140, fill="#f4ecf7", stroke=COLOR_TAG, sw=2, rx=8))
    p.append(text(735, 110, "Легітимний", size=13, color=COLOR_TAG, bold=True))
    p.append(text(735, 130, "Тег / Ключ", size=13, color=COLOR_TAG, bold=True))
    p.append(text(735, 160, "Крипто-чип", size=11, color=INK))
    p.append(text(735, 185, "У кишені власника", size=10, color=MUTED))

    # Радіозв'язок на кінцях
    p.append(line(180, 150, 230, 150, color=COLOR_READER, sw=2, dash="3 3"))
    p.append(text(205, 135, "13.56 МГц", size=9, color=COLOR_READER))

    p.append(line(610, 150, 660, 150, color=COLOR_TAG, sw=2, dash="3 3"))
    p.append(text(635, 135, "13.56 МГц", size=9, color=COLOR_TAG))

    # Нижнє пояснення
    b, _, _ = textbox(420, 270,
                      "Криптографічний запит-відповідь проходить крізь міст БЕЗ ЗМІН.\n"
                      "Стандартна криптографія (AES/DES) без вимірювання часу прольоту НЕ ЗАХИЩАЄ від цієї атаки!",
                      size=12, fill=BG, stroke=COLOR_ATTACK, color=COLOR_ATTACK, bold=True)
    p.append(b)

    render(os.path.join(OUT, "relay-attack-topology.svg"), W, H, *p,
           title="Топологія атаки ретрансляції")

# ── Фігура 3: Архітектура LFSR CRYPTO1 та нелінійного фільтра ────────────────
def fig_crypto1_lfsr_keystream():
    W, H = 800, 320
    p = []

    p.append(text(400, 25, "Структура алгоритму CRYPTO1 (48-бітний LFSR та фільтруюча функція)", size=13, color=INK, bold=True))

    # Зсувний регістр 48 біт (LFSR)
    p.append(rect(60, 70, 680, 50, fill="#eaeded", stroke=LINE, sw=2, rx=6))
    p.append(text(400, 95, "48-бітний зсувний регістр з лінійним зворотним зв'язком (LFSR State: a₀ ... a₄₇)", size=12, color=INK, bold=True))

    # Блоки зсуву
    for i in range(8):
        x = 90 + i * 80
        p.append(rect(x, 78, 45, 34, fill=BG, stroke=MUTED, rx=3))
        p.append(text(x + 22.5, 99, f"a_{i*6}", size=11, color=INK))

    # Поліном зворотного зв'язку (Feedback polynomial)
    p.append(line(400, 120, 400, 160, color=COLOR_BUS, sw=1.8))
    p.append(arrow(400, 140, 400, 160, color=COLOR_BUS, sw=1.8))
    p.append(circle(400, 175, 15, fill="#ebf5fb", stroke=COLOR_BUS, sw=1.8))
    p.append(text(400, 179, "L", size=14, color=COLOR_BUS, bold=True))

    # Зворотній зв'язок на вхід регістру
    p.append(line(400, 190, 400, 210, color=COLOR_BUS, sw=1.8))
    p.append(line(400, 210, 40, 210, color=COLOR_BUS, sw=1.8))
    p.append(line(40, 210, 40, 95, color=COLOR_BUS, sw=1.8))
    p.append(arrow(40, 110, 60, 95, color=COLOR_BUS, sw=1.8))
    p.append(text(210, 225, "Поліном зворотного зв'язку f_a(state)", size=10, color=COLOR_BUS))

    # Нелінійна фільтруюча функція f_b
    p.append(rect(520, 150, 200, 70, fill="#fadbd8", stroke=COLOR_ATTACK, sw=2, rx=6))
    p.append(text(620, 175, "Нелінійний фільтр f_b", size=12, color=COLOR_ATTACK, bold=True))
    p.append(text(620, 198, "20 виходів LFSR → 1 біт", size=10, color=INK))

    # Відводи від LFSR до фільтра
    p.append(line(600, 120, 600, 150, color=COLOR_ATTACK, sw=1.5))
    p.append(arrow(600, 135, 600, 150, color=COLOR_ATTACK, sw=1.5))

    # Вихід гами (Keystream ks)
    p.append(line(720, 185, 770, 185, color=COLOR_ATTACK, sw=2.0))
    p.append(arrow(750, 185, 770, 185, color=COLOR_ATTACK, sw=2.0))
    p.append(text(745, 172, "Keystream bit", size=10, color=COLOR_ATTACK, bold=True))

    # Пояснення вразливості PRNG
    b, _, _ = textbox(400, 280,
                      "Вразливість: 48-бітний стан занадто малий для перебору на GPU.\n"
                      "Слабкий генератор PRNG (LFSR 16-біт) видає передбачувані одноразові числа nonces n_T, n_R.",
                      size=11, fill=BG, stroke=COLOR_ATTACK, color=COLOR_ATTACK)
    p.append(b)

    render(os.path.join(OUT, "crypto1-lfsr-keystream.svg"), W, H, *p,
           title="Структура алгоритму CRYPTO1")

# ── Фігура 4: Часова діаграма протоколу Distance Bounding ─────────────────────
def fig_distance_bounding_timeline():
    W, H = 840, 350
    p = []

    p.append(text(420, 20, "Часова діаграма протоколу обмеження відстані (Distance Bounding)", size=13, color=INK, bold=True))

    # Осі часу для Verifier та Prover
    y_v, y_p = 110, 200
    p.append(text(85, y_v + 4, "Зчитувач (Verifier)", size=11, color=COLOR_READER, bold=True))
    p.append(line(160, y_v, 790, y_v, color=LINE, sw=1.5))
    p.append(arrow(770, y_v, 790, y_v, color=LINE, sw=1.5))

    p.append(text(85, y_p + 4, "Тег (Prover)", size=11, color=COLOR_TAG, bold=True))
    p.append(line(160, y_p, 790, y_p, color=LINE, sw=1.5))
    p.append(arrow(770, y_p, 790, y_p, color=LINE, sw=1.5))

    # Фаза 1: Попереднє узгодження (Slow phase)
    p.append(rect(175, 48, 170, 185, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    p.append(text(260, 64, "Фаза 1: Узгодження", size=10, color=MUTED, bold=True))
    p.append(arrow(190, y_v + 10, 320, y_p - 10, color=MUTED, sw=1.2))
    p.append(text(260, 145, "Запит (N_V, Crypto)", size=9, color=MUTED))

    # Фаза 2: Швидкісний імпульсний обмін (Fast 1-bit Challenge-Response)
    p.append(rect(365, 48, 275, 185, fill="#eaf2f8", stroke=COLOR_BUS, sw=1.5, rx=4))
    p.append(text(502, 64, "Фаза 2: Бітові раунди (k раундів)", size=10, color=COLOR_BUS, bold=True))

    # Раунд i: Запит біта c_i
    x1 = 395
    p.append(circle(x1, y_v, 4, fill=COLOR_READER, stroke="none"))
    x2 = x1 + 55
    p.append(circle(x2, y_p, 4, fill=COLOR_TAG, stroke="none"))
    p.append(arrow(x1, y_v, x2, y_p, color=COLOR_READER, sw=1.8))
    p.append(text(415, 145, "c_i (1 біт)", size=9, color=COLOR_READER, bold=True))

    # Відповідь біта r_i
    x3 = x2 + 25
    x4 = x3 + 55
    p.append(circle(x3, y_p, 4, fill=COLOR_TAG, stroke="none"))
    p.append(circle(x4, y_v, 4, fill=COLOR_READER, stroke="none"))
    p.append(arrow(x3, y_p, x4, y_v, color=COLOR_TAG, sw=1.8))
    p.append(text(510, 168, "r_i (1 біт)", size=9, color=COLOR_TAG, bold=True))

    # Вимірювання часу RTT
    p.append(line(x1, y_v - 18, x1, y_v - 5, color=COLOR_ATTACK, sw=1.2))
    p.append(line(x4, y_v - 18, x4, y_v - 5, color=COLOR_ATTACK, sw=1.2))
    p.append(line(x1, y_v - 14, x4, y_v - 14, color=COLOR_ATTACK, sw=1.5))
    p.append(arrow(x1+15, y_v - 14, x1, y_v - 14, color=COLOR_ATTACK, sw=1.5))
    p.append(arrow(x4-15, y_v - 14, x4, y_v - 14, color=COLOR_ATTACK, sw=1.5))
    p.append(text((x1+x4)/2, y_v - 22, "t_RTT ≤ t_max", size=10, color=COLOR_ATTACK, bold=True))

    # Фаза 3: Перевірка підпису (Verification phase)
    p.append(rect(660, 48, 115, 185, fill="#f4ecf7", stroke=COLOR_TAG, sw=1, rx=4))
    p.append(text(717, 64, "Фаза 3: HMAC", size=10, color=COLOR_TAG, bold=True))
    p.append(text(717, 145, "Перевірка підпису", size=9, color=COLOR_TAG))

    # Фізична формула порогу
    b, _, _ = textbox(420, 292,
                      "Поріг часу прольоту: t_max = 2 · d_max / c. Для відстані d = 1 м: t_RTT ≈ 6.67 нс.\n"
                      "При ретрансляції через Wi-Fi/5G затримка Δt > 10–50 мс, що в 100 000 разів перевищує поріг t_max!",
                      size=11, fill=BG, stroke=COLOR_BUS, color=INK)
    p.append(b)

    render(os.path.join(OUT, "distance-bounding-timeline.svg"), W, H, *p,
           title="Часова діаграма Distance Bounding")

# ── Фігура 5: Архітектура апаратного Secure Element (SE) ──────────────────────
def fig_secure_element_architecture():
    W, H = 800, 340
    p = []

    p.append(text(400, 25, "Архітектура апаратного криптомодуля (Secure Element / SAM)", size=13, color=INK, bold=True))

    # Корпус Secure Element чипа
    p.append(rect(50, 55, 700, 220, fill="#fdfefe", stroke=COLOR_TAG, sw=2.5, rx=10))
    p.append(text(400, 80, "Апаратно захищений кристали (Secure Element Chip)", size=13, color=COLOR_TAG, bold=True))

    # Апаратний криптопроцесор (Cryptographic Accelerator)
    p.append(rect(80, 110, 180, 80, fill="#e8f8f5", stroke=COLOR_READER, sw=1.8, rx=6))
    p.append(text(170, 135, "Криптоакселератор", size=12, color=COLOR_READER, bold=True))
    p.append(text(170, 158, "AES-128/256, ECC, RSA", size=10, color=INK))
    p.append(text(170, 175, "Захист від DPA / SPA", size=10, color=MUTED))

    # Генератор випадкових чисел TRNG
    p.append(rect(290, 110, 180, 80, fill="#ebf5fb", stroke=COLOR_BUS, sw=1.8, rx=6))
    p.append(text(380, 135, "Апаратний TRNG", size=12, color=COLOR_BUS, bold=True))
    p.append(text(380, 158, "Аналоговий генератор", size=10, color=INK))
    p.append(text(380, 175, "фізичного шуму", size=10, color=MUTED))

    # Захищена пам'ять (Secure Storage)
    p.append(rect(500, 110, 220, 80, fill="#f4ecf7", stroke=COLOR_TAG, sw=1.8, rx=6))
    p.append(text(610, 135, "Захищена Flash/EEPROM", size=12, color=COLOR_TAG, bold=True))
    p.append(text(610, 158, "Шифрована шина даних", size=10, color=INK))
    p.append(text(610, 175, "Зберігання Master Keys", size=10, color=COLOR_TAG))

    # Активний захисний шар від розкриття (Active Tamper Mesh & Sensors)
    p.append(rect(80, 205, 640, 50, fill="#fadbd8", stroke=COLOR_ATTACK, sw=1.5, rx=6))
    p.append(text(400, 225, "Система активного антизламу (Active Tamper Mesh / Sensors)", size=11, color=COLOR_ATTACK, bold=True))
    p.append(text(400, 243, "Детектори напруги, температури, лазерного опромінення та сітка мікропроводів над кристалом", size=10, color=INK))

    # Зовнішній інтерфейс SWP / ISO 7816
    p.append(line(400, 275, 400, 310, color=LINE, sw=2))
    p.append(arrow(400, 275, 400, 310, color=LINE, sw=2))
    p.append(text(400, 325, "Зовнішня шина: ISO/IEC 7816 / Single Wire Protocol (SWP) / I2C", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "secure-element-architecture.svg"), W, H, *p,
           title="Архітектура Secure Element")

if __name__ == "__main__":
    fig_rfid_coupling_eavesdropping()
    fig_relay_attack_topology()
    fig_crypto1_lfsr_keystream()
    fig_distance_bounding_timeline()
    fig_secure_element_architecture()
    print("Figures generated successfully.")
