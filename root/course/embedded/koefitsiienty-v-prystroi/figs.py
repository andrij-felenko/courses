# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_cal_lifecycle():
    w, h = 820, 360
    p = []

    # Три основні фази
    p.append(fitbox(20, 50, 240, 270, "", fill="#f9fafb", stroke="#9ca3af", sw=1.2))
    p.append(textbox(140, 75, "1. Заводський стенд (EOL)", size=13, bold=True, color="#1e3a8a", fill="#dbeafe", stroke="#3b82f6")[0])
    p.append(mtext(140, 115, [
        "• Еталонна термокамера / гирі",
        "• Вимірювання Gain і Offset₀",
        "• Підгонка полінома термокомпенсації",
        "• Запис у OTP / захищену Flash",
        "• Незмінна метрологічна база"
    ], size=11, color=INK, anchor="middle", lh=1.5))

    p.append(fitbox(290, 50, 240, 270, "", fill="#f9fafb", stroke="#9ca3af", sw=1.2))
    p.append(textbox(410, 75, "2. Старт пристрою (Boot)", size=13, bold=True, color="#065f46", fill="#d1fae5", stroke="#10b981")[0])
    p.append(mtext(410, 115, [
        "• Тарування нуля (Zero Tare)",
        "• Зняття механічних напружень",
        "• Вимірювання температури T_boot",
        "• Перевірка цілісності CRC32",
        "• Завантаження в робоче ОЗП"
    ], size=11, color=INK, anchor="middle", lh=1.5))

    p.append(fitbox(560, 50, 240, 270, "", fill="#f9fafb", stroke="#9ca3af", sw=1.2))
    p.append(textbox(680, 75, "3. Польовий режим (Runtime)", size=13, bold=True, color="#92400e", fill="#fef3c7", stroke="#f59e0b")[0])
    p.append(mtext(680, 115, [
        "• Компенсація дрейфу від T(t)",
        "• Фоновий трекінг нуля (Auto-Zero)",
        "• Відстеження старіння елементів",
        "• Атомарне оновлення A/B слотів",
        "• Резервування при brownout"
    ], size=11, color=INK, anchor="middle", lh=1.5))

    # Стрілки між фазами
    p.append(arrow(260, 170, 288, 170, color="#4b5563", sw=2.0))
    p.append(arrow(530, 170, 558, 170, color="#4b5563", sw=2.0))

    # Нижні акценти
    p.append(textbox(140, 285, "Один раз на життя\n(Висока точність)", size=10, color=MUTED, fill=BG, stroke="#9ca3af", pad=4)[0])
    p.append(textbox(410, 285, "При кожному вмиканні\n(Секунди на тарування)", size=10, color=MUTED, fill=BG, stroke="#9ca3af", pad=4)[0])
    p.append(textbox(680, 285, "Неперервно у циклі\n(Атомарний NVS запис)", size=10, color=MUTED, fill=BG, stroke="#9ca3af", pad=4)[0])

    render(os.path.join(OUT, "cal-lifecycle.svg"), w, h, *p,
           title="Життєвий цикл калібрувальних коефіцієнтів у пристрої")


def fig_binary_layout():
    w, h = 820, 380
    p = []

    # Загальний контейнер пам'яті
    p.append(textbox(410, 60, "Структура калібрувального блоку (64 байти, вирівнювання 4 байти)", size=13, bold=True, fill="#e5e7eb", stroke="#4b5563")[0])

    # Заголовок (Header)
    p.append(fitbox(40, 95, 230, 190, "", fill="#eff6ff", stroke="#3b82f6", sw=1.5))
    p.append(text(155, 118, "Заголовок (Header: 16 B)", size=12, bold=True, color="#1d4ed8"))
    p.append(mtext(155, 142, [
        "0x00: magic [4B] (0x43414C42)",
        "0x04: schema_version [2B]",
        "0x06: flags [2B] (Valid, Fact, Cal)",
        "0x08: sequence_id [4B] (Епоха A/B)",
        "0x0C: timestamp / station [4B]"
    ], size=10.5, color=INK, anchor="middle", lh=1.45))

    # Корисне навантаження (Payload)
    p.append(fitbox(285, 95, 330, 190, "", fill="#f0fdf4", stroke="#16a34a", sw=1.5))
    p.append(text(450, 118, "Корисні коефіцієнти (Payload: 44 B)", size=12, bold=True, color="#15803d"))
    p.append(mtext(450, 142, [
        "0x10..0x18: offset_x, y, z [3 × float 4B]",
        "0x1C..0x24: gain_x, y, z [3 × float 4B]",
        "0x28..0x30: poly_t0, t1, t2 [3 × float 4B]",
        "0x34: temp_ref [float 4B]",
        "0x38: serial_id [uint32 4B]",
        "0x3C: reserved_pad [4B] (Zero-filled)"
    ], size=10.5, color=INK, anchor="middle", lh=1.45))

    # Підвал (Footer)
    p.append(fitbox(630, 95, 150, 190, "", fill="#fef2f2", stroke="#dc2626", sw=1.5))
    p.append(text(705, 118, "Підвал (4 B)", size=12, bold=True, color="#b91c1c"))
    p.append(mtext(705, 148, [
        "0x3C..0x3F:",
        "crc32 [4B]",
        "IEEE 802.3",
        "over 0x00..0x3B"
    ], size=10.5, color=INK, anchor="middle", lh=1.45))

    # Пояснення захисту
    p.append(fitbox(40, 300, 740, 55, "", fill="#f9fafb", stroke="#9ca3af", sw=1.0))
    p.append(mtext(410, 322, [
        "• magic 0x43414C42 ('CALB') відсікає стерту Flash (0xFF) та чисту SRAM (0x00)",
        "• schema_version захищає від несумісних структур при OTA-оновленні прошивки",
        "• CRC32 покриває всі попередні 60 байтів, унеможливлюючи роботу з битими даними"
    ], size=10.5, color="#374151", anchor="middle", lh=1.35))

    render(os.path.join(OUT, "binary-layout.svg"), w, h, *p,
           title="Бінарне розміщення полів калібрувального блоку")


def fig_media_hierarchy():
    w, h = 820, 370
    p = []

    # 4 колонки носіїв
    cols = [
        ("OTP / eFuse", "#fef2f2", "#ef4444", "#991b1b", [
            "• Розміщення: кристал MCU",
            "• Ресурс: 1 запис (незворотно)",
            "• Час запису: одиниці мс",
            "• Захист: апаратний замок",
            "• Призначення: заводська",
            "  метрологічна база (Root)"
        ]),
        ("Внутрішня Flash (NVS)", "#eff6ff", "#3b82f6", "#1e40af", [
            "• Розміщення: сектор Flash",
            "• Ресурс: 10k–100k циклів",
            "• Стирається секторами (1–128 КБ)",
            "• Flash Stall блокує шину",
            "• Призначення: конфігурація",
            "  з A/B подвійним буфером"
        ]),
        ("Зовнішня EEPROM", "#f0fdf4", "#22c55e", "#166534", [
            "• Шина: I2C або SPI",
            "• Ресурс: ~1 000 000 циклів",
            "• Посторінковий запис (3–5 мс)",
            "• Апаратний пін WP (Write Protect)",
            "• Призначення: надійне польове",
            "  зберігання з захистом WP"
        ]),
        ("Сегнетоелектрична FRAM", "#fefce8", "#eab308", "#854d0e", [
            "• Шина: I2C або SPI",
            "• Ресурс: 10¹⁴ циклів (без меж)",
            "• Миттєвий запис на швидкості шини",
            "• Без затримок і без стирання",
            "• Призначення: часте польове",
            "  тарування та аварійний стан"
        ])
    ]

    for i, (name, bg, stroke, text_color, items) in enumerate(cols):
        cx = 110 + i * 200
        p.append(fitbox(cx - 90, 55, 180, 285, "", fill=bg, stroke=stroke, sw=1.5))
        p.append(textbox(cx, 80, name, size=11.5, bold=True, color=text_color, fill=BG, stroke=stroke, pad=4)[0])
        p.append(mtext(cx, 118, items, size=10, color=INK, anchor="middle", lh=1.45))

    render(os.path.join(OUT, "media-hierarchy.svg"), w, h, *p,
           title="Порівняння носіїв для калібрувальних параметрів")


def fig_ping_pong_storage():
    w, h = 820, 390
    p = []

    # Слот A
    p.append(fitbox(40, 60, 340, 200, "", fill="#f0fdf4", stroke="#16a34a", sw=2.0))
    p.append(textbox(210, 85, "СЛОТ A (Сектор / Сторінка 0)", size=13, bold=True, color="#15803d", fill="#dcfce7", stroke="#22c55e")[0])
    p.append(mtext(210, 125, [
        "magic: 0x43414C42 ('CALB')  [OK]",
        "schema_version: 1            [OK]",
        "sequence_id: 104            [ЧИННА ЕПОХА]",
        "payload: {offset, gain, ...} [ВАЛІДНО]",
        "crc32: 0x8F3A12C5           [ЗБІГАЄТЬСЯ]"
    ], size=10.5, color=INK, anchor="middle", lh=1.4))
    p.append(textbox(210, 230, "СТАТУС: АКТИВНИЙ РОБОЧИЙ СЛОТ", size=11, bold=True, color="#15803d", fill="#bbf7d0", stroke="#16a34a")[0])

    # Слот B
    p.append(fitbox(440, 60, 340, 200, "", fill="#fef2f2", stroke="#dc2626", sw=2.0))
    p.append(textbox(610, 85, "СЛОТ B (Сектор / Сторінка 1)", size=13, bold=True, color="#b91c1c", fill="#fee2e2", stroke="#ef4444")[0])
    p.append(mtext(610, 125, [
        "magic: 0x43414C42 ('CALB')  [OK]",
        "schema_version: 1            [OK]",
        "sequence_id: 105            [НОВИЙ ЗАПИС]",
        "payload: {0x12, 0xFF, 0x00...} [ОБРИВ ПРИ BROWNOUT]",
        "crc32: 0x00000000           [НЕ ЗБІГАЄТЬСЯ!]"
    ], size=10.5, color=INK, anchor="middle", lh=1.4))
    p.append(textbox(610, 230, "СТАТУС: ПОШКОДЖЕНО (ВІДХИЛЕНО)", size=11, bold=True, color="#b91c1c", fill="#fecaca", stroke="#dc2626")[0])

    # Стрілка аварії
    p.append(arrow(385, 140, 435, 140, color="#dc2626", sw=2.0))
    p.append(textbox(410, 115, "Збій живлення\nпід час запису", size=9.5, bold=True, color="#b91c1c", fill="#fee2e2", stroke="#ef4444", pad=3)[0])

    # Нижня панель логіки
    p.append(fitbox(40, 280, 740, 85, "", fill="#f8fafc", stroke="#64748b", sw=1.2))
    p.append(mtext(410, 305, [
        "1. Нове калібрування завжди пишеться у неактивний слот з інкрементом sequence_id.",
        "2. CRC32 записується останнім байтом після повного запису та перевірки даних.",
        "3. При старті читаються обидва слоти: якщо слот B має битий CRC, система прозоро обирає слот A.",
        "4. Дані не втрачаються навіть при раптовому вимиканні живлення в середині операції!"
    ], size=10.5, color="#1e293b", anchor="middle", lh=1.4))

    render(os.path.join(OUT, "ping-pong-storage.svg"), w, h, *p,
           title="Атомарна подвійна буферизація (A/B Ping-Pong)")


def fig_state_machine_recovery():
    w, h = 820, 390
    p = []

    # Блок 1: Старт
    p.append(textbox(410, 50, "Старт системи: читання Слота A та Слота B з NVS", size=12, bold=True, color="#1e293b", fill="#e2e8f0", stroke="#475569")[0])
    p.append(arrow(410, 70, 410, 100, color="#475569", sw=1.8))

    # Блок 2: Ромб рішень
    p.append(textbox(410, 120, "Верифікація: magic == 'CALB' && версія підтримується && CRC32 валідний?", size=11, bold=True, color="#1e3a8a", fill="#dbeafe", stroke="#3b82f6")[0])

    # Гілка 1: Обидва валідні
    p.append(arrow(260, 140, 150, 185, color="#16a34a", sw=1.8))
    p.append(textbox(150, 160, "Обидва слоти валідні", size=9.5, bold=True, color="#166534", fill="#dcfce7", stroke="#22c55e", pad=3)[0])
    p.append(textbox(150, 215, "Вибір слота з\nmax(sequence_id)\n(Свіжа калібровка)", size=10.5, bold=True, color="#166534", fill="#f0fdf4", stroke="#16a34a")[0])
    p.append(arrow(150, 250, 150, 290, color="#16a34a", sw=1.8))
    p.append(textbox(150, 315, "СТАТУС: OK\nПовна точність приладу", size=11, bold=True, color="#14532d", fill="#bbf7d0", stroke="#15803d")[0])

    # Гілка 2: Один валідний
    p.append(arrow(410, 140, 410, 185, color="#2563eb", sw=1.8))
    p.append(textbox(410, 160, "Один слот валідний", size=9.5, bold=True, color="#1e40af", fill="#dbeafe", stroke="#3b82f6", pad=3)[0])
    p.append(textbox(410, 215, "Вибір єдиного цілого\nслота + планування\nфонового відновлення", size=10.5, bold=True, color="#1e40af", fill="#eff6ff", stroke="#2563eb")[0])
    p.append(arrow(410, 250, 410, 290, color="#2563eb", sw=1.8))
    p.append(textbox(410, 315, "СТАТУС: RECOVERED\nТочність збережено", size=11, bold=True, color="#1e3a8a", fill="#bfdbfe", stroke="#1d4ed8")[0])

    # Гілка 3: Обидва пошкоджені -> Fallback
    p.append(arrow(560, 140, 670, 185, color="#dc2626", sw=1.8))
    p.append(textbox(670, 160, "Обидва пошкоджені / Чип чистий", size=9.5, bold=True, color="#991b1b", fill="#fee2e2", stroke="#ef4444", pad=3)[0])
    p.append(textbox(670, 215, "Fallback: Читання OTP\nабо зашитих дефолтів\n(Gain=1.0, Offset=0.0)", size=10.5, bold=True, color="#991b1b", fill="#fef2f2", stroke="#dc2626")[0])
    p.append(arrow(670, 250, 670, 290, color="#dc2626", sw=1.8))
    p.append(textbox(670, 315, "СТАТУС: DEGRADED\nПрапорець 'Потрібна калібровка'", size=11, bold=True, color="#7f1d1d", fill="#fecaca", stroke="#b91c1c")[0])

    render(os.path.join(OUT, "state-machine-recovery.svg"), w, h, *p,
           title="Автомат завантаження та багаторівневе відновлення")


if __name__ == "__main__":
    fig_cal_lifecycle()
    fig_binary_layout()
    fig_media_hierarchy()
    fig_ping_pong_storage()
    fig_state_machine_recovery()
    print("Усі 5 фігур успішно згенеровано!")
