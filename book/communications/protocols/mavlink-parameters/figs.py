# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми mavlink-parameters (Параметри MAVLink)."""

import os
import sys

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_param_value_format():
    """Фігура 1: Анатомія повідомлення PARAM_VALUE та бітове відображення (bit-cast)."""
    W, H = 840, 480
    p = []

    # Заголовок
    p.append(text(420, 36, "Анатомія кадру PARAM_VALUE та пакування 32-бітних даних", size=15, color=INK, bold=True))

    # Блок 1: Структура корисного навантаження (Payload Layout, 25 байтів)
    p.append(rect(25, 55, 790, 135, fill="#ffffff", stroke=LINE, sw=1.0, rx=6))
    p.append(text(420, 75, "Корисне навантаження повідомлення PARAM_VALUE (MAVLink ID #22, 25 байтів)", size=11, color=MUTED, bold=True))

    # Поля корисного навантаження
    # param_value (4B float)
    p.append(rect(40, 95, 170, 55, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(mtext(125, 117, "param_value (4 байти)\nТип: float (IEEE 754) / контейнер", size=9.5, color=NEG, bold=True))

    # param_count (2B uint16)
    p.append(rect(220, 95, 110, 55, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    p.append(mtext(275, 117, "param_count (2B)\nВсього параметрів", size=9.5, color=FIELD, bold=True))

    # param_index (2B uint16)
    p.append(rect(340, 95, 110, 55, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    p.append(mtext(395, 117, "param_index (2B)\nІндекс (0..count-1)", size=9.5, color=FIELD, bold=True))

    # param_id (16B char)
    p.append(rect(460, 95, 230, 55, fill="#fff7ed", stroke=POS, sw=1.5, rx=4))
    p.append(mtext(575, 117, "param_id (16 байтів)\nASCII-рядок (символьна назва)", size=9.5, color=POS, bold=True))

    # param_type (1B uint8)
    p.append(rect(700, 95, 100, 55, fill="#faf5ff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(750, 117, "param_type (1B)\nMAV_PARAM_TYPE", size=9.5, color=INK, bold=True))

    # Текстова підказка про пастку 16-го символу
    p.append(text(420, 172, "Пастка param_id: при довжині рівно 16 символів кінцевий нуль '\\0' відсутній!", size=10, color=POS, bold=True))

    # Блок 2: Порівняння приведення типу (Каст vs Bit-cast)
    p.append(rect(25, 205, 790, 255, fill="#ffffff", stroke=LINE, sw=1.0, rx=6))
    p.append(text(420, 226, "Небезпека математичного перетворення (float)val vs побітове відображення (Bit-cast)", size=11, color=MUTED, bold=True))

    # Ліва колонка: Помилкове перетворення (Каст)
    p.append(rect(40, 245, 365, 195, fill="#fef2f2", stroke=POS, sw=1.2, rx=5))
    p.append(text(222, 268, "Небезпечно: Стандартний каст (float)integer", size=10.5, color=POS, bold=True, anchor="middle"))
    p.append(text(55, 296, "uint32_t val = 0x80000001 (2 147 483 649)", size=9.5, color=INK, anchor="start"))
    p.append(text(55, 318, "Каст: float f = (float)val;", size=9.5, color=INK, anchor="start"))
    p.append(text(55, 340, "Мантиса float має лише 24 біти точності!", size=9.5, color=POS, bold=True, anchor="start"))
    p.append(text(55, 362, "Молодші 8 бітів стираються округленням:", size=9.5, color=INK, anchor="start"))
    p.append(text(55, 384, "Результат: 2 147 483 648.0f (втрата молодшого біта)", size=9.5, color=POS, anchor="start"))
    p.append(text(55, 414, "Наслідок: спотворення масок портів і прапорців!", size=9.5, color=POS, bold=True, anchor="start"))

    # Права колонка: Коректне побітове копіювання (Bit-cast)
    p.append(rect(435, 245, 365, 195, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    p.append(text(617, 268, "Коректно: Побітове відображення memcpy / bit_cast", size=10.5, color=FIELD, bold=True, anchor="middle"))
    p.append(text(450, 296, "uint32_t val = 0x80000001 (2 147 483 649)", size=9.5, color=INK, anchor="start"))
    p.append(text(450, 318, "Копіювання: memcpy(&f, &val, sizeof(float));", size=9.5, color=INK, anchor="start"))
    p.append(text(450, 340, "Всі 32 біти двійкового стану переносяться 1:1", size=9.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(450, 362, "Приймач читає тип MAV_PARAM_TYPE_UINT32:", size=9.5, color=INK, anchor="start"))
    p.append(text(450, 384, "Розпакування: memcpy(&res, &f, sizeof(uint32_t));", size=9.5, color=INK, anchor="start"))
    p.append(text(450, 414, "Результат: точне відновлення 0x80000001!", size=9.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "param-value-format.svg"), W, H, *p)


def fig_param_sync_lifecycle():
    """Фігура 2: Повне вичитування параметрів, виявлення втрат і точкове дозавантаження."""
    W, H = 840, 520
    p = []

    p.append(text(420, 36, "Життєвий цикл синхронізації параметрів над ненадійним каналом", size=15, color=INK, bold=True))

    # Лінії учасників (GCS та Autopilot)
    gcs_x = 180
    mav_x = 660

    p.append(rect(gcs_x - 85, 55, 170, 35, fill="#eff6ff", stroke=NEG, sw=1.5, rx=5))
    p.append(text(gcs_x, 77, "Наземна станція (GCS)", size=11, color=NEG, bold=True))

    p.append(rect(mav_x - 85, 55, 170, 35, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(mav_x, 77, "Автопілот (Vehicle)", size=11, color=FIELD, bold=True))

    # Вертикальні лінії життя
    p.append(line(gcs_x, 90, gcs_x, 485, color=NEG, sw=1.2, dash="4,4"))
    p.append(line(mav_x, 90, mav_x, 485, color=FIELD, sw=1.2, dash="4,4"))

    # Крок 1: Запит повного списку
    p.append(arrow(gcs_x, 120, mav_x, 120, color=NEG, sw=1.5))
    p.append(text(420, 112, "PARAM_REQUEST_LIST (target_system, target_component)", size=9.5, color=NEG, bold=True))

    # Крок 2: Потік відповідей PARAM_VALUE
    # Пакет 0
    p.append(arrow(mav_x, 150, gcs_x, 150, color=FIELD, sw=1.2))
    p.append(text(420, 143, "PARAM_VALUE (index=0, count=1200, id='SYS_AUTOSTART')", size=9, color=INK))

    # Пакет 1
    p.append(arrow(mav_x, 180, gcs_x, 180, color=FIELD, sw=1.2))
    p.append(text(420, 173, "PARAM_VALUE (index=1, count=1200, id='BAT1_N_CELLS')", size=9, color=INK))

    # Пакет 2 - Втрачено
    p.append(line(mav_x, 210, 420, 210, color=POS, sw=1.2, dash="3,3"))
    p.append(text(420, 206, "PARAM_VALUE (index=2) ─── ВТРАЧЕНО В ЕФІРІ ─── ✖", size=9, color=POS, bold=True))

    # Пакет 3
    p.append(arrow(mav_x, 240, gcs_x, 240, color=FIELD, sw=1.2))
    p.append(text(420, 233, "PARAM_VALUE (index=3, count=1200, id='MC_ROLLRATE_P')", size=9, color=INK))

    # Пакет N-1
    p.append(arrow(mav_x, 275, gcs_x, 275, color=FIELD, sw=1.2))
    p.append(text(420, 268, "PARAM_VALUE (index=1199, count=1200, id='EKF2_MAG_TYPE')", size=9, color=INK))

    # Фаза аналізу в GCS
    p.append(rect(65, 300, 230, 40, fill="#fff7ed", stroke=POS, sw=1.2, rx=4))
    p.append(mtext(180, 318, "Аналіз отриманих індексів:\nВиявлено пропуск index=2", size=9, color=POS, bold=True))

    # Крок 3: Точкове дозавантаження пропущеного індексу
    p.append(arrow(gcs_x, 365, mav_x, 365, color=NEG, sw=1.5))
    p.append(text(420, 357, "PARAM_REQUEST_READ (param_index=2, param_id='')", size=9.5, color=NEG, bold=True))

    # Відповідь на точковий запит
    p.append(arrow(mav_x, 400, gcs_x, 400, color=FIELD, sw=1.5))
    p.append(text(420, 392, "PARAM_VALUE (index=2, count=1200, id='BAT1_V_EMPTY')", size=9.5, color=FIELD, bold=True))

    # Завершення
    p.append(rect(65, 430, 230, 40, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(mtext(180, 448, "Всі 1200 параметрів отримано!\nСинхронізацію завершено успішно", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "param-sync-lifecycle.svg"), W, H, *p)


def fig_param_set_transaction():
    """Фігура 3: Транзакція запису параметра PARAM_SET та перевірка обмежень."""
    W, H = 840, 460
    p = []

    p.append(text(420, 36, "Транзакція зміни параметра: запис, валідація та підтвердження", size=15, color=INK, bold=True))

    gcs_x = 180
    mav_x = 660

    p.append(rect(gcs_x - 85, 55, 170, 35, fill="#eff6ff", stroke=NEG, sw=1.5, rx=5))
    p.append(text(gcs_x, 77, "Наземна станція (GCS)", size=11, color=NEG, bold=True))

    p.append(rect(mav_x - 85, 55, 170, 35, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(mav_x, 77, "Автопілот (Vehicle)", size=11, color=FIELD, bold=True))

    p.append(line(gcs_x, 90, gcs_x, 425, color=NEG, sw=1.2, dash="4,4"))
    p.append(line(mav_x, 90, mav_x, 425, color=FIELD, sw=1.2, dash="4,4"))

    # 1. Надсилання PARAM_SET
    p.append(arrow(gcs_x, 120, mav_x, 120, color=NEG, sw=1.5))
    p.append(text(420, 112, "PARAM_SET (id='MPC_XY_VEL_MAX', val=25.0f, type=REAL32)", size=9.5, color=NEG, bold=True))

    # Внутрішня логіка автопілота
    p.append(rect(mav_x - 120, 145, 240, 75, fill="#faf5ff", stroke=LINE, sw=1.2, rx=5))
    p.append(text(mav_x, 163, "Перевірка діапазону в автопілоті:", size=9.5, color=INK, bold=True))
    p.append(text(mav_x, 183, "Межі: min=0.5, max=20.0, def=12.0", size=9, color=MUTED))
    p.append(text(mav_x, 203, "Значення 25.0 > max → обрізка до 20.0!", size=9, color=POS, bold=True))

    # 2. Відповідь PARAM_VALUE
    p.append(arrow(mav_x, 255, gcs_x, 255, color=FIELD, sw=1.5))
    p.append(text(420, 247, "PARAM_VALUE (id='MPC_XY_VEL_MAX', val=20.0f, type=REAL32)", size=9.5, color=FIELD, bold=True))

    # Обробка в GCS
    p.append(rect(gcs_x - 110, 280, 220, 55, fill="#fff7ed", stroke=POS, sw=1.2, rx=5))
    p.append(text(gcs_x, 298, "Порівняння відправленого і прийнятого:", size=9, color=INK, bold=True))
    p.append(text(gcs_x, 318, "Запитували: 25.0 ≠ Збережено: 20.0", size=9, color=POS))

    # Повідомлення оператору
    p.append(rect(180, 360, 480, 45, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=5))
    p.append(mtext(420, 379, "GCS оновлює інтерфейс фактичним збереженим значенням (20.0 м/с)\nта інформує оператора про застосування апаратного ліміту", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "param-set-transaction.svg"), W, H, *p)


def fig_param_ext_protocol():
    """Фігура 4: Архітектура Parameter Protocol Ext для 64-бітних та розширених типів."""
    W, H = 840, 460
    p = []

    p.append(text(420, 36, "Архітектура розширеного протоколу параметрів (Parameter Protocol Ext)", size=15, color=INK, bold=True))

    # Блок 1: Структура PARAM_EXT_VALUE (128-байтовий буфер)
    p.append(rect(25, 55, 790, 125, fill="#ffffff", stroke=LINE, sw=1.0, rx=6))
    p.append(text(420, 75, "Структура корисного навантаження PARAM_EXT_VALUE (149 байтів)", size=11, color=MUTED, bold=True))

    # Поля EXT
    p.append(rect(40, 95, 340, 45, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(mtext(210, 115, "param_value[128] (128 байтів)\nПідтримка UINT64, INT64, REAL64, CUSTOM/ARRAY", size=9, color=NEG, bold=True))

    p.append(rect(390, 95, 110, 45, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(mtext(445, 115, "param_count (2B)\nКількість", size=9, color=FIELD, bold=True))

    p.append(rect(510, 95, 110, 45, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(mtext(565, 115, "param_index (2B)\nІндекс", size=9, color=FIELD, bold=True))

    p.append(rect(630, 95, 100, 45, fill="#fff7ed", stroke=POS, sw=1.2, rx=4))
    p.append(mtext(680, 115, "param_id (16B)\nІм'я", size=9, color=POS, bold=True))

    p.append(rect(740, 95, 65, 45, fill="#faf5ff", stroke=LINE, sw=1.2, rx=4))
    p.append(mtext(772, 115, "type (1B)\nEXT_TYPE", size=9.5, color=INK, bold=True))

    p.append(text(420, 160, "Перевага: позбавлення від обмеження 4 байтів та надійна передача 64-бітних цілих і double", size=9.5, color=FIELD, bold=True))

    # Блок 2: Схема квитування через PARAM_EXT_ACK
    p.append(rect(25, 195, 790, 235, fill="#ffffff", stroke=LINE, sw=1.0, rx=6))
    p.append(text(420, 215, "Явне квитування запису: PARAM_EXT_SET → PARAM_EXT_ACK", size=11, color=MUTED, bold=True))

    gcs_x = 200
    mav_x = 640

    p.append(rect(gcs_x - 70, 230, 140, 30, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(gcs_x, 249, "Клієнт (GCS)", size=10, color=NEG, bold=True))

    p.append(rect(mav_x - 70, 230, 140, 30, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(mav_x, 249, "Автопілот (Vehicle)", size=10, color=FIELD, bold=True))

    p.append(line(gcs_x, 260, gcs_x, 415, color=NEG, sw=1.2, dash="3,3"))
    p.append(line(mav_x, 260, mav_x, 415, color=FIELD, sw=1.2, dash="3,3"))

    # Стрілка PARAM_EXT_SET
    p.append(arrow(gcs_x, 290, mav_x, 290, color=NEG, sw=1.5))
    p.append(text(420, 282, "PARAM_EXT_SET (id, param_value[128], param_type)", size=9.5, color=NEG, bold=True))

    # Стрілка PARAM_EXT_ACK
    p.append(arrow(mav_x, 340, gcs_x, 340, color=FIELD, sw=1.5))
    p.append(text(420, 332, "PARAM_EXT_ACK (param_result: ACCEPTED / DENIED / FAILED / UNSUPPORTED)", size=9.5, color=FIELD, bold=True))

    # Статус коди
    p.append(rect(200, 365, 440, 45, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(420, 382, "Статус: PARAM_ACK_ACCEPTED (0), PARAM_ACK_VALUE_UNSUPPORTED (1),", size=9.5, color=INK))
    p.append(text(420, 398, "PARAM_ACK_FAILED (2), PARAM_ACK_IN_PROGRESS (3)", size=9.5, color=INK))

    render(os.path.join(OUT, "param-ext-protocol.svg"), W, H, *p)


def main():
    fig_param_value_format()
    fig_param_sync_lifecycle()
    fig_param_set_transaction()
    fig_param_ext_protocol()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
