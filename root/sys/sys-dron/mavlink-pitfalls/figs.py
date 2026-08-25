# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми mavlink-pitfalls (Підводні камені MAVLink)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_v1_v2_compat():
    """Фігура 1: Порівняння кадрів MAVLink v1 і v2, підпис, zero-trimming та розширений заголовок."""
    W, H = 820, 360
    p = []

    # Заголовок блоку v1
    p.append(rect(20, 20, 780, 130, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(35, 45, "MAVLink 1 (Максимум 263 байти)", size=13, color=INK, anchor="start", bold=True))
    p.append(text(780, 45, "Фіксований заголовок 6 байтів, без прапорців і підпису", size=11, color=MUTED, anchor="end"))

    # Поля v1
    v1_fields = [
        ("STX\n0xFE", 55, POS),
        ("LEN\n0..255", 65, FIELD),
        ("SEQ\n0..255", 55, NEG),
        ("SYS\n1..255", 55, INK),
        ("COMP\n1..255", 60, INK),
        ("MSG ID\n0..255 (8-біт)", 110, POS),
        ("PAYLOAD (Корисні дані)\n0..255 байтів (без обрізання нулів)", 240, FILL),
        ("CRC\n2 байти", 80, FIELD)
    ]
    x_cur = 35
    for name, w_box, col in v1_fields:
        p.append(rect(x_cur, 60, w_box, 50, fill="#ffffff", stroke=col, sw=1.5, rx=4))
        p.append(mtext(x_cur + w_box / 2, 80, name, size=10, color=col if col != FILL else INK, bold=True))
        x_cur += w_box + 5

    p.append(text(35, 132, "⚠ Пастка v1: MSG ID обмежений 255; буфери парсера розраховані максимум на 263 байти", size=11, color=POS, anchor="start", italic=True))

    # Заголовок блоку v2
    p.append(rect(20, 175, 780, 165, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(35, 200, "MAVLink 2 (Максимум 280 байтів)", size=13, color=INK, anchor="start", bold=True))
    p.append(text(780, 200, "Заголовок 10 байтів, 24-біт MSG ID, zero-trimming, підпис", size=11, color=MUTED, anchor="end"))

    # Поля v2
    v2_fields = [
        ("STX\n0xFD", 42, POS),
        ("LEN\n0..255", 46, FIELD),
        ("INC\nflags", 42, POS),
        ("CMP\nflags", 42, MUTED),
        ("SEQ\nnum", 42, NEG),
        ("SYS\nid", 42, INK),
        ("COMP\nid", 42, INK),
        ("MSG ID\n24-біт (3 B)", 78, POS),
        ("PAYLOAD (Zero-trimmed)\nХвостові нулі відтято!", 190, FIELD),
        ("CRC\n2 B", 48, FIELD),
        ("SIGNATURE\n13 B (опція)", 90, POS)
    ]
    x_cur = 35
    for name, w_box, col in v2_fields:
        p.append(rect(x_cur, 215, w_box, 52, fill="#ffffff", stroke=col, sw=1.5, rx=4))
        p.append(mtext(x_cur + w_box / 2, 235, name, size=9.5, color=col if col != FILL else INK, bold=True))
        x_cur += w_box + 4

    p.append(text(35, 290, "⚠ Пастка Zero-Trimming: перед розпакуванням обов'язковий memset(&msg, 0, sizeof(msg))!", size=11, color=POS, anchor="start", bold=True))
    p.append(text(35, 312, "⚠ Пастка Signed: невідомий біт у INC flags (0x01) змушує v1-парсери відкидати пакет або ламатися на хвості", size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "v1-v2-compat.svg"), W, H, *p)


def fig_uart_dma_blocking():
    """Фігура 2: Блокувальний ввід-вивід проти DMA з кільцевим буфером у реальному часі."""
    W, H = 820, 370
    p = []

    # Ліва колонка: Блокувальний підхід
    p.append(rect(20, 20, 380, 330, fill="#fdfefe", stroke=POS, sw=1.5, rx=8))
    p.append(text(210, 48, "Блокувальний TX (Катастрофа реального часу)", size=12.5, color=POS, bold=True))

    # Шкала часу блокування
    p.append(rect(40, 75, 340, 45, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(210, 95, "Головний цикл PID (400 Гц, період 2.5 мс)", size=11, color=POS, bold=True))
    p.append(text(210, 110, "uart_write_blocking(280 байтів)", size=10, color=INK))

    p.append(arrow(210, 120, 210, 150, color=POS, sw=1.8))

    p.append(rect(40, 150, 340, 65, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(mtext(210, 172, "Швидкість 57600 бод:\n280 Б × 10 біт / 57600 = 48.6 мс затримки!\n(Пропуск 19 ітерацій стабілізації!)", size=10.5, color=POS, bold=True))

    p.append(arrow(210, 215, 210, 245, color=POS, sw=1.8))

    p.append(rect(40, 245, 340, 85, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    p.append(mtext(210, 268, "Наслідки блокування:\n• Зрив оцінювача EKF і розбіжність орієнтації\n• Спрацьовування Watchdog таймера (HardFault)\n• Падіння апарата або втрата керованості", size=10.5, color=INK, anchor="middle"))

    # Права колонка: Неблокувальний DMA + Кільцевий буфер
    p.append(rect(420, 20, 380, 330, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(610, 48, "DMA + Кільцевий буфер (Надійна архітектура)", size=12.5, color=FIELD, bold=True))

    p.append(rect(440, 75, 340, 45, fill="#ecfdf5", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(610, 95, "Головний цикл PID (Виконується без пауз)", size=11, color=FIELD, bold=True))
    p.append(text(610, 110, "ring_buffer_push() — час O(1), менше 1 мкс", size=10, color=INK))

    p.append(arrow(610, 120, 610, 150, color=FIELD, sw=1.8))

    p.append(rect(440, 150, 340, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(mtext(610, 172, "Кільцевий буфер TX + Апаратний DMA:\nДані течуть у фоні без участі ядра CPU;\nЧерга повна → дроп телеметрії, збереження команд", size=10.5, color=INK, bold=True))

    p.append(arrow(610, 215, 610, 245, color=FIELD, sw=1.8))

    p.append(rect(440, 245, 340, 85, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(mtext(610, 268, "Переваги DMA-схеми:\n• Частота PID-контуру суворо фіксована (400 Гц)\n• Дроп низькопріоритетних пакетів при заторах\n• Повний облік помилок (TX drop counter)", size=10.5, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(OUT, "uart-dma-blocking.svg"), W, H, *p)


def fig_routing_loop():
    """Фігура 3: Маршрутні петлі та колізії ідентифікаторів у мульти-інтерфейсних мережах."""
    W, H = 820, 350
    p = []

    # Фон
    p.append(rect(20, 20, 780, 310, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(410, 45, "Топологія з кількома інтерфейсами та ризик маршрутної петлі", size=13, color=INK, bold=True))

    # Вузли
    # Автопілот
    p.append(rect(40, 80, 200, 75, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(mtext(140, 105, "Автопілот (FC)\nSYS 1, COMP 1\nUART1 (57600/921600)", size=11, color=NEG, bold=True))

    # Бортовий комп'ютер
    p.append(rect(310, 80, 200, 75, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(mtext(410, 105, "Бортовий комп'ютер (SBC)\nSYS 1, COMP 191 (mavlink-router)\nUART ↔ UDP ↔ USB", size=10.5, color=FIELD, bold=True))

    # Радіомодем / Телеметрія
    p.append(rect(580, 80, 200, 75, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(mtext(680, 105, "Телеметричний модем\nSYS 1, COMP 158\nРадіолінія (57600 бод)", size=11, color=POS, bold=True))

    # Наземна станція
    p.append(rect(580, 215, 200, 75, fill="#ffffff", stroke=INK, sw=1.5, rx=6))
    p.append(mtext(680, 240, "Наземна станція (GCS)\nSYS 255, COMP 190\nQGroundControl / MissionPlanner", size=10.5, color=INK, bold=True))

    # З'єднання між вузлами
    p.append(line(240, 117, 310, 117, color=LINE, sw=1.8))
    p.append(line(510, 117, 580, 117, color=LINE, sw=1.8))
    p.append(line(680, 155, 680, 172, color=LINE, sw=1.8, dash="4,3"))
    p.append(text(680, 185, "Радіоканал (RF)", size=10, color=MUTED))
    p.append(line(680, 196, 680, 215, color=LINE, sw=1.8, dash="4,3"))

    # Прямий міст (UDP/USB)
    p.append(line(410, 155, 410, 230, color=LINE, sw=1.8, dash="4,3"))
    p.append(text(495, 242, "Wi-Fi / 4G UDP", size=10, color=MUTED))
    p.append(line(410, 252, 580, 252, color=LINE, sw=1.8, dash="4,3"))

    # Червоне кільце зациклення
    p.append(circle(495, 160, 36, fill="none", stroke=POS, sw=2))
    p.append(text(495, 157, "ПЕТЛЯ!", size=11, color=POS, bold=True))
    p.append(text(495, 172, "Broadcast storm", size=9.5, color=POS))

    # Пояснення знизу
    p.append(rect(40, 215, 340, 85, fill="#fef2f2", stroke=POS, sw=1.2, rx=6))
    p.append(mtext(210, 238, "Причина: у MAVLink немає поля TTL!\nШирокомовний HEARTBEAT із SBC дублюється в UART і UDP,\nповертається назад і розмножується лавиноподібно.\nЗахист: Split-Horizon + таблиця маршрутизації за sys/comp.", size=10, color=INK))

    render(os.path.join(OUT, "routing-loop.svg"), W, H, *p)


def fig_float_vs_inte7():
    """Фігура 4: Порівняння точності float32 проти int32 degE7 на поверхні Землі."""
    W, H = 820, 360
    p = []

    p.append(rect(20, 20, 780, 320, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    p.append(text(410, 48, "Роздільна здатність географічних координат: float32 проти int32 (degE7)", size=13, color=INK, bold=True))

    # Лівий блок: float32 (IEEE-754)
    p.append(rect(40, 75, 355, 245, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(217, 100, "float32 (24 біти мантиси)", size=12, color=POS, bold=True))

    p.append(mtext(217, 125, "Формат: 1 біт знак, 8 біт експонента, 23 біти мантиса\nКількість рівнів дискретизації: 2²⁴ = 16 777 216\nДіапазон довготи: −180.0° .. +180.0°", size=10.5, color=INK))

    # Шкала з великим кроком
    p.append(line(60, 185, 370, 185, color=POS, sw=2))
    for x_tick, val in [(80, "179.99°"), (190, "+1.69 м"), (300, "+3.38 м")]:
        p.append(line(x_tick, 178, x_tick, 192, color=POS, sw=2))
        p.append(text(x_tick, 205, val, size=10, color=POS, bold=True))

    p.append(mtext(217, 238, "Крок квантування при λ ≈ 180°:\nΔλ = 180° / 2²³ ≈ 2.15 × 10⁻⁵ градуса\nПохибка на екваторі: ≈ 2.39 метра!\n(Непридатно для автопосадки та RTK!)", size=10.5, color=POS, bold=True))

    # Правий блок: int32 degE7 (MAVLink v2 standard)
    p.append(rect(425, 75, 355, 245, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(602, 100, "int32_t (degE7 = градуси × 10⁷)", size=12, color=FIELD, bold=True))

    p.append(mtext(602, 125, "Формат: 32-бітне ціле число зі знаком\nКількість рівнів: 2³² ≈ 4.29 × 10⁹\nМасштабування: 1 одиниця = 10⁻⁷ градуса (0.0000001°)", size=10.5, color=INK))

    # Дрібна регулярна сітка
    p.append(line(445, 185, 755, 185, color=FIELD, sw=2))
    for x_tick, val in [(465, "0 см"), (525, "1.1 см"), (585, "2.2 см"), (645, "3.3 см"), (705, "4.4 см")]:
        p.append(line(x_tick, 180, x_tick, 190, color=FIELD, sw=1.5))
        p.append(text(x_tick, 205, val, size=9.5, color=FIELD, bold=True))

    p.append(mtext(602, 238, "Крок квантування фіксований скрізь:\nΔλ = 10⁻⁷ градуса (стала цілочисельна сітка)\nПохибка на екваторі: 1.11 сантиметра!\n(Повна підтримка сантиметрового RTK GNSS)", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "float-vs-inte7.svg"), W, H, *p)


if __name__ == "__main__":
    fig_v1_v2_compat()
    fig_uart_dma_blocking()
    fig_routing_loop()
    fig_float_vs_inte7()
    print("Всі фігури успішно згенеровано.")
