# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми:
«Версія повідомлення й сумісність в обидва боки»
(root/course/embedded/versiia-povidomlennia-i-sumisnist-v-obydva-boky).
"""

import sys
import os

# scripts/ у корені репо — 4 рівні вгору від теми
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_fleet_version_mismatch():
    """Фігура 1: Гетерогенний парк IoT-пристроїв різних версій прошивки на зв'язку з хмарою."""
    w, h = 820, 360
    f = []

    # Заголовок / фон зон
    f.append(rect(15, 45, 490, 295, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(260, 70, "Розподілений парк польових пристроїв (IoT Fleet)", size=14, bold=True, color=INK))

    f.append(rect(535, 45, 270, 295, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=8))
    f.append(text(670, 70, "Хмарний сервер / Шлюз", size=14, bold=True, color=FIELD))

    # Три вузли різного віку
    # Вузол 1 (v1.0)
    tb1, _, _ = textbox(140, 125, "Вузол #104 (v1.0, 2021 рік)\nГлибокий сон 99.9% часу\nСтруктура: ID + Temp + Volt (12 Б)", size=11, fill="#ffffff", stroke=LINE, min_w=220)
    f.append(tb1)

    # Вузол 2 (v1.4)
    tb2, _, _ = textbox(140, 205, "Вузол #582 (v1.4, 2023 рік)\nКанаркове оновлення OTA\nСтруктура: + Humid + Flags (16 Б)", size=11, fill="#ffffff", stroke=LINE, min_w=220)
    f.append(tb2)

    # Вузол 3 (v2.0)
    tb3, _, _ = textbox(140, 285, "Вузол #911 (v2.0, 2026 рік)\nНова апаратна ревізія\nСтруктура: + GPS + EC (28 Б)", size=11, fill="#ffffff", stroke=LINE, min_w=220)
    f.append(tb3)

    # Сервер і парсер v2.0
    tb_srv, _, _ = textbox(670, 160, "Бекенд-парсер (v2.0)\nЧитає всі покоління повідомлень\nЗаповнює пропущені поля дефолтами\nБез збоїв при відсутності нових тегів", size=11, fill="#ffffff", stroke=FIELD, min_w=240)
    f.append(tb_srv)

    tb_cmd, _, _ = textbox(670, 265, "Генератор команд (v2.0)\nШле розширені конфігурації\nСтарі вузли ігнорують нові опції,\nне зависаючи від зайвих байтів", size=11, fill="#ffffff", stroke=FIELD, min_w=240)
    f.append(tb_cmd)

    # Стрілки телеметрії (Uplink)
    f.append(arrow(260, 125, 540, 145, color=NEG, sw=1.8))
    f.append(text(400, 130, "Uplink v1.0 (12 Б)", size=10, color=NEG, bold=True))

    f.append(arrow(260, 205, 540, 165, color=NEG, sw=1.8))
    f.append(text(400, 180, "Uplink v1.4 (16 Б)", size=10, color=NEG, bold=True))

    f.append(arrow(260, 285, 540, 185, color=NEG, sw=1.8))
    f.append(text(400, 230, "Uplink v2.0 (28 Б)", size=10, color=NEG, bold=True))

    # Стрілка конфігурації (Downlink)
    f.append(arrow(540, 265, 260, 140, color=POS, sw=1.8))
    f.append(text(400, 290, "Downlink v2.0 config (нові поля ігноруються v1.0)", size=10, color=POS, bold=True))

    render(os.path.join(OUT_DIR, "fleet-version-mismatch.svg"), w, h, *f)


def fig_forward_backward_compat():
    """Фігура 2: Двосторонній вектор сумісності — Backward (назад) та Forward (вперед)."""
    w, h = 820, 360
    f = []

    # Верхній блок: Зворотна сумісність (Backward Compatibility)
    f.append(rect(15, 35, 790, 145, fill="#eff6ff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(410, 60, "Зворотна сумісність (Backward Compatibility): Новий приймач читає старі повідомлення", size=13, bold=True, color=NEG))

    tb_old_tx, _, _ = textbox(150, 110, "Старий відправник (v1.0)\nПакет: [ID, Temp, Volt]", size=11, fill="#ffffff", stroke=LINE, min_w=200)
    f.append(tb_old_tx)

    f.append(arrow(260, 110, 430, 110, color=NEG, sw=2.0))
    f.append(text(345, 98, "Кадр v1 (8 байтів)", size=10, color=NEG, bold=True))

    tb_new_rx, _, _ = textbox(590, 110, "Новий парсер (v2.0)\nЗчитує: ID, Temp, Volt\nДля поля «Humidity» ставить дефолт (NAN)\nПомилки відсутності поля немає!", size=11, fill="#ffffff", stroke=NEG, min_w=280)
    f.append(tb_new_rx)

    # Нижній блок: Пряма сумісність (Forward Compatibility)
    f.append(rect(15, 195, 790, 150, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=8))
    f.append(text(410, 220, "Пряма сумісність (Forward Compatibility): Старий приймач безпечно ігнорує нові поля", size=13, bold=True, color="#854d0e"))

    tb_new_tx, _, _ = textbox(150, 275, "Новий відправник (v2.0)\nПакет: [ID, Temp, Volt, GPS, EC]", size=11, fill="#ffffff", stroke=LINE, min_w=200)
    f.append(tb_new_tx)

    f.append(arrow(260, 275, 430, 275, color="#ca8a04", sw=2.0))
    f.append(text(345, 263, "Кадр v2 (24 байти)", size=10, color="#ca8a04", bold=True))

    tb_old_rx, _, _ = textbox(590, 275, "Старий парсер (v1.0)\nЗчитує: ID, Temp, Volt\nНевідомі поля GPS та EC безпечно переступає\nПристрій НЕ зависає і не скидає кадр!", size=11, fill="#ffffff", stroke="#ca8a04", min_w=280)
    f.append(tb_old_rx)

    render(os.path.join(OUT_DIR, "forward-backward-compat.svg"), w, h, *f)


def fig_binary_schema_evolution():
    """Фігура 3: Порівняння трьох підходів до бінарної еволюції (Struct tail, TLV, CBOR/Protobuf)."""
    w, h = 820, 390
    f = []

    f.append(text(410, 25, "Формати бінарних повідомлень та механіка розширення полів", size=14, bold=True, color=INK))

    # Схема A: Позиційна структура з хвостовим доповненням
    f.append(rect(15, 45, 790, 95, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(35, 70, "A. C-структура (хвостове розширення):", size=11, bold=True, anchor="start"))
    f.append(fitbox(270, 55, 120, 30, "Base v1 (8 B)", size=10, fill="#e2e8f0", stroke=LINE))
    f.append(fitbox(395, 55, 120, 30, "Ext v1.2 (4 B)", size=10, fill="#fed7aa", stroke="#ea580c"))
    f.append(fitbox(520, 55, 120, 30, "Ext v2.0 (8 B)", size=10, fill="#bbf7d0", stroke=FIELD))
    f.append(text(270, 115, "Розбір: перевірка len >= sizeof(Base). Нові поля тільки в кінець; видалення неможливе.", size=10, anchor="start", color=MUTED))

    # Схема B: TLV (Tag-Length-Value)
    f.append(rect(15, 150, 790, 105, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(35, 175, "B. TLV (Tag-Length-Value):", size=11, bold=True, anchor="start"))

    f.append(fitbox(200, 160, 50, 32, "Tag 1\n(1B)", size=9, fill="#e2e8f0", stroke=LINE))
    f.append(fitbox(252, 160, 50, 32, "Len\n(1B)", size=9, fill="#e2e8f0", stroke=LINE))
    f.append(fitbox(304, 160, 75, 32, "Value\n(Temp: 4B)", size=9, fill="#ffffff", stroke=LINE))

    f.append(fitbox(390, 160, 50, 32, "Tag 8\n(1B)", size=9, fill="#fed7aa", stroke="#ea580c"))
    f.append(fitbox(442, 160, 50, 32, "Len\n(1B)", size=9, fill="#fed7aa", stroke="#ea580c"))
    f.append(fitbox(494, 160, 110, 32, "Невідоме поле\n(Новий сенсор: 6B)", size=9, fill="#fff7ed", stroke="#ea580c"))

    f.append(fitbox(615, 160, 50, 32, "Tag 2\n(1B)", size=9, fill="#e2e8f0", stroke=LINE))
    f.append(fitbox(667, 160, 50, 32, "Len\n(1B)", size=9, fill="#e2e8f0", stroke=LINE))
    f.append(fitbox(719, 160, 75, 32, "Value\n(Volt: 2B)", size=9, fill="#ffffff", stroke=LINE))

    f.append(arrow(415, 205, 595, 205, color=POS, sw=1.8))
    f.append(text(505, 222, "Пропуск невідомого тегу: ptr += Len (без парсингу)", size=10, color=POS, bold=True))

    f.append(text(200, 243, "Довільний порядок, будь-які опційні поля, пропуск невідомих тегів за вказівником довжини.", size=10, anchor="start", color=MUTED))

    # Схема C: Protobuf / CBOR (Цілочисельні ключі + типи дроту)
    f.append(rect(15, 265, 790, 110, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(35, 290, "C. Protobuf / CBOR Map:", size=11, bold=True, anchor="start"))

    f.append(fitbox(200, 275, 130, 32, "Key 1: Varint (Temp)", size=9, fill="#e2e8f0", stroke=LINE))
    f.append(fitbox(340, 275, 150, 32, "Key 2: Fixed32 (Volt)", size=9, fill="#e2e8f0", stroke=LINE))
    f.append(fitbox(500, 275, 180, 32, "Key 9: Невідомий WireType 2", size=9, fill="#fed7aa", stroke="#ea580c"))

    f.append(arrow(520, 320, 670, 320, color=POS, sw=1.8))
    f.append(text(595, 335, "WireType 2 → прочитати varint len і пропустити N байтів", size=10, color=POS, bold=True))

    f.append(text(200, 360, "Тип дроту (Wire Type) вказує точну кількість байтів для пропуску навіть без .proto схеми.", size=10, anchor="start", color=MUTED))

    render(os.path.join(OUT_DIR, "binary-schema-evolution.svg"), w, h, *f)


def fig_safe_parser_flow():
    """Фігура 4: Послідовність станів та перевірок безпечного версіонованого парсера."""
    w, h = 820, 370
    f = []

    f.append(text(410, 25, "Конвеєр відмовостійкого розбору версіонованого пакета", size=14, bold=True, color=INK))

    # Крок 1: Перевірка заголовка
    tb1, _, _ = textbox(110, 90, "1. Валідація заголовка\nMagic == 0xAA55\nCRC8 заголовка\nMajor_Ver == SUPPORTED", size=10, fill="#eff6ff", stroke=NEG, min_w=170)
    f.append(tb1)

    f.append(arrow(195, 90, 245, 90, color=LINE, sw=1.5))

    # Крок 2: Ініціалізація структури дефолтами
    tb2, _, _ = textbox(340, 90, "2. Ініціалізація результату\nmemset(&msg, 0, sizeof)\nTemp = NAN, Volt = 0\npresent_mask = 0", size=10, fill="#ffffff", stroke=LINE, min_w=170)
    f.append(tb2)

    f.append(arrow(425, 90, 475, 90, color=LINE, sw=1.5))

    # Крок 3: Цикл TLV по корисних даних
    tb3, _, _ = textbox(600, 90, "3. Цикл розбору полів\nПоки (offset < payload_len):\nПеревірка залишку буфера\nЗчитування Tag + Len", size=10, fill="#fefce8", stroke="#ca8a04", min_w=200)
    f.append(tb3)

    # Розгалуження з Кроку 3 вниз
    f.append(arrow(600, 135, 340, 195, color=FIELD, sw=1.8))
    f.append(text(440, 160, "Тег відомий", size=10, color=FIELD, bold=True))

    f.append(arrow(600, 135, 600, 195, color="#ea580c", sw=1.8))
    f.append(text(610, 165, "Тег невідомий", size=10, color="#ea580c", bold=True))

    f.append(arrow(700, 115, 760, 115, color=POS, sw=1.8))
    f.append(text(730, 95, "Збій len", size=9, color=POS))
    tb_err, _, _ = textbox(770, 160, "Аварійне скидання\nPARSE_ERR_BOUNDS\nПакет відхилено", size=9, fill="#fdecea", stroke=POS, min_w=90)
    f.append(tb_err)
    f.append(arrow(760, 115, 770, 130, color=POS, sw=1.5))

    # Гілка: Відомий тег
    tb_known, _, _ = textbox(340, 240, "4A. Розбір значення\nВалідація Len == expected\nread_le32/16 (без UB)\nmsg.field = val\npresent_mask |= FLAG", size=10, fill="#f0fdf4", stroke=FIELD, min_w=190)
    f.append(tb_known)

    # Гілка: Невідомий тег
    tb_unknown, _, _ = textbox(600, 240, "4B. Перевірка прапорця критичності\nЯкщо Tag & CRITICAL_BIT:\n  → ПОМИЛКА: невідоме обов'язкове поле!\nІнакше:\n  offset += Len (безпечний пропуск)\n  skipped_tags_count++", size=10, fill="#fff7ed", stroke="#ea580c", min_w=220)
    f.append(tb_unknown)

    # Завершення
    f.append(arrow(340, 285, 470, 335, color=FIELD, sw=1.5))
    f.append(arrow(600, 285, 470, 335, color=FIELD, sw=1.5))

    tb_done, _, _ = textbox(470, 335, "5. Успішний результат (PARSE_OK)\nПовідомлення готове до обробки прикладною логікою;\nВсі відомі поля заповнені, нові коректно пропущені.", size=10, fill="#f0fdf4", stroke=FIELD, min_w=340)
    f.append(tb_done)

    render(os.path.join(OUT_DIR, "safe-parser-state-machine.svg"), w, h, *f)


if __name__ == "__main__":
    fig_fleet_version_mismatch()
    fig_forward_backward_compat()
    fig_binary_schema_evolution()
    fig_safe_parser_flow()
    print("Усі 4 фігури успішно згенеровано.")
