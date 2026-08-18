# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми mavlink-events-protocol."""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_statustext_vs_events():
    """Порівняння старого підходу STATUSTEXT та нового протоколу MAVLink Events."""
    w, h = 820, 370
    frags = []

    # Заголовок блоку STATUSTEXT (старий підхід)
    frags.append(rect(15, 15, 790, 155, fill="#fdf7f7", stroke=POS, sw=1.5, rx=8))
    frags.append(text(35, 38, "СТАРИЙ ПІДХІД: Текстовий потік STATUSTEXT (#253)", size=14, color=POS, bold=True, anchor="start"))

    # Блоки STATUSTEXT
    tb1, _, _ = textbox(130, 95, "Бортовий контролер\nsprintf(buf, \"PreArm: Accel 1\")\n50 байтів ASCII у Flash", size=11, pad=8, fill="#ffffff", stroke=LINE)
    tb2, _, _ = textbox(410, 95, "Канал зв'язку (57600 бод)\n[char text[50]] + severity\nВисокі накладні витрати (54 B)", size=11, pad=8, fill="#ffffff", stroke=POS)
    tb3, _, _ = textbox(690, 95, "Наземна станція (GCS)\nСирий рядок без структури\nНемає локалізації та дій", size=11, pad=8, fill="#ffffff", stroke=LINE)

    frags.extend([tb1, tb2, tb3])
    frags.append(arrow(225, 95, 290, 95, color=POS))
    frags.append(arrow(530, 95, 595, 95, color=POS))
    frags.append(text(410, 150, "✖ Немає детекції втрат, монолітний текст англійською, перевитрата байтів у радіоканалі", size=11, color=POS, italic=True))

    # Заголовок блоку Events Protocol (новий підхід)
    frags.append(rect(15, 190, 790, 165, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(35, 213, "НОВИЙ СТАНДАРТ: Протокол подій MAVLink EVENT (#410)", size=14, color=FIELD, bold=True, anchor="start"))

    # Блоки Events Protocol
    tb4, _, _ = textbox(130, 275, "Бортовий контролер\nevents::send(ID, args)\nID: 0x8A12B4C0, Accel=1\nДвійковий буфер у RAM", size=11, pad=8, fill="#ffffff", stroke=LINE)
    tb5, _, _ = textbox(410, 275, "Канал зв'язку (57600 бод)\nevent_id (4B) + seq (2B) +\nlog_levels (1B) + args (1B)\nВсього 8 байтів корисних даних", size=11, pad=8, fill="#ffffff", stroke=FIELD)
    tb6, _, _ = textbox(690, 275, "Наземна станція (GCS)\nПошук у локальному JSON\nПереклад + кнопка дії:\n[Калібрувати сенсор]", size=11, pad=8, fill="#ffffff", stroke=LINE)

    frags.extend([tb4, tb5, tb6])
    frags.append(arrow(225, 275, 290, 275, color=FIELD))
    frags.append(arrow(530, 275, 595, 275, color=FIELD))
    frags.append(text(410, 335, "✔ Гарантована доставка (sequence gap recovery), нульові рядки у Flash, інтерактивні дії", size=11, color=FIELD, italic=True))

    return render(os.path.join(IMG_DIR, "statustext-vs-events.svg"), w, h, *frags)


def fig_event_packet_layout():
    """Двійкова розкладка кадру EVENT (#410) та CURRENT_EVENT_SEQUENCE (#411)."""
    w, h = 820, 390
    frags = []

    # Верхня панель: Структура повідомлення EVENT (#410)
    frags.append(rect(15, 15, 790, 205, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(35, 38, "Структура корисного навантаження повідомлення EVENT (ID #410, розмір до 53 байтів)", size=13, color=INK, bold=True, anchor="start"))

    # Поля кадру EVENT: (назва, тип_розмір, опис, x, w)
    fields = [
        ("event_time_boot_ms", "4B uint32", ["Час зі старту", "(мілісекунди)"], 30, 115),
        ("sequence", "2B uint16", ["Порядковий", "номер події"], 155, 85),
        ("id (event_id)", "4B uint32", ["Хеш простору", "та імені"], 250, 105),
        ("log_levels", "1B uint8", ["4b внутр. /", "4b зовн. severity"], 365, 95),
        ("dest_sys / comp", "2B 2×uint8", ["Адресація", "(0 = broadcast)"], 470, 95),
        ("arguments[40]", "до 40B uint8[]", ["Типізовані двійкові", "аргументи (LE)"], 575, 215),
    ]

    for name, sz, desc_lines, x, bw in fields:
        cx = x + bw / 2
        frags.append(rect(x, 50, bw, 36, fill="#e8f0fe", stroke=NEG, sw=1.2, rx=4))
        frags.append(text(cx, 66, name, size=9.5, color=NEG, bold=True))
        frags.append(text(cx, 80, sz, size=9.5, color=MUTED))
        frags.append(mtext(cx, 104, desc_lines, size=9.5, color=INK, lh=1.2))

    # Деталізація поля log_levels
    frags.append(rect(30, 145, 760, 60, fill="#ffffff", stroke=MUTED, sw=1.0, rx=5))
    frags.append(text(45, 168, "Поле log_levels (1 байт):", size=10.5, color=INK, bold=True, anchor="start"))
    frags.append(rect(205, 155, 265, 40, fill="#fdf0ed", stroke=POS, sw=1.0, rx=3))
    frags.append(mtext(337, 172, ["Старші 4 біти: Внутрішній рівень", "для Flash/SD-карти (0..7)"], size=9.5, color=POS, bold=True, lh=1.2))
    frags.append(rect(485, 155, 290, 40, fill="#edf5fd", stroke=NEG, sw=1.0, rx=3))
    frags.append(mtext(630, 172, ["Молодші 4 біти: Зовнішній рівень", "для станції QGroundControl (0..7)"], size=9.5, color=NEG, bold=True, lh=1.2))

    # Нижня панель: CURRENT_EVENT_SEQUENCE (#411)
    frags.append(rect(15, 235, 790, 140, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(35, 258, "Структура повідомлення CURRENT_EVENT_SEQUENCE (ID #411, періодичний стан)", size=13, color=INK, bold=True, anchor="start"))

    frags.append(rect(35, 275, 190, 36, fill="#edfdf5", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(130, 292, "sequence (2B uint16)", size=10.5, color=FIELD, bold=True))
    frags.append(text(130, 305, "Останній лічильник", size=9, color=MUTED))
    frags.append(text(130, 330, "Поточний виданий номер", size=9.5, color=INK))

    frags.append(rect(240, 275, 165, 36, fill="#edfdf5", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(322, 292, "flags (1B uint8)", size=10.5, color=FIELD, bold=True))
    frags.append(text(322, 305, "Прапорці стану", size=9, color=MUTED))
    frags.append(text(322, 330, "Ознака перезапуску буфера", size=9.5, color=INK))

    frags.append(rect(420, 270, 370, 90, fill="#ffffff", stroke=MUTED, sw=1.0, rx=5))
    frags.append(mtext(605, 292, [
        "Транслюється автопілотом періодично (1 Гц) або при появі нової події.",
        "GCS порівнює отриманий sequence із локальним лічильником:",
        "якщо є розрив — негайно запитує втрачені кадри через REQUEST_EVENT.",
        "Працює як легковагове серцебиття системи журналювання."
    ], size=9.5, color=INK, lh=1.35))

    return render(os.path.join(IMG_DIR, "event-packet-layout.svg"), w, h, *frags)


def fig_event_sequence_recovery():
    """Схема виявлення пропусків у послідовності та відновлення втрачених подій."""
    w, h = 820, 420
    frags = []

    # Вертикальні лінії часу для Автопілота та GCS
    frags.append(text(180, 30, "Польотний контролер (Автопілот)", size=13, color=INK, bold=True))
    frags.append(line(180, 45, 180, 395, color=LINE, sw=1.5, dash="4,4"))

    frags.append(text(640, 30, "Наземна станція керування (GCS)", size=13, color=INK, bold=True))
    frags.append(line(640, 45, 640, 395, color=LINE, sw=1.5, dash="4,4"))

    # Подія 1: Успішна доставка EVENT seq=12
    frags.append(arrow(180, 80, 640, 100, color=FIELD, sw=1.8))
    frags.append(text(410, 80, "EVENT #410 (sequence = 12, Arming Check OK)", size=10.5, color=FIELD, bold=True))
    frags.append(textbox(640, 100, "Отримано seq=12\nОчікується: 13", size=9.5, pad=5, fill="#eef9f2", stroke=FIELD)[0])

    # Подія 2: Втрата кадру EVENT seq=13
    frags.append(line(180, 140, 410, 155, color=POS, sw=1.8))
    frags.append(text(430, 155, "✖ ВТРАТА В ЕФІРІ", size=11, color=POS, bold=True))
    frags.append(text(300, 138, "EVENT #410 (seq = 13, Gyro High Bias)", size=10, color=POS))

    # Подія 3: Доставка EVENT seq=14 -> Детекція пропуску
    frags.append(arrow(180, 195, 640, 215, color=FIELD, sw=1.8))
    frags.append(text(410, 195, "EVENT #410 (sequence = 14, Mode Changed)", size=10.5, color=FIELD, bold=True))
    frags.append(textbox(640, 220, "Отримано seq=14!\nПропуск: seq=13", size=9.5, pad=5, fill="#fdf0ed", stroke=POS)[0])

    # Запит відновлення втраченої події: REQUEST_EVENT або MAV_CMD_REQUEST_MESSAGE
    frags.append(arrow(640, 265, 180, 285, color=NEG, sw=1.8))
    frags.append(text(410, 265, "REQUEST_EVENT (target_seq = 13)", size=10.5, color=NEG, bold=True))

    # Автопілот дістає подію з кільцевого буфера в RAM
    frags.append(textbox(180, 315, "Кільцевий буфер RAM:\nПошук seq=13 (знайдено)", size=9.5, pad=5, fill="#edf5fd", stroke=NEG)[0])

    # Повторна передача втраченої події
    frags.append(arrow(180, 345, 640, 365, color=FIELD, sw=1.8))
    frags.append(text(410, 345, "EVENT #410 (sequence = 13, Gyro High Bias) [Повтор]", size=10.5, color=FIELD, bold=True))
    frags.append(textbox(640, 370, "seq=13 відновлено!\nЧерга повна: 12, 13, 14", size=9.5, pad=5, fill="#eef9f2", stroke=FIELD)[0])

    return render(os.path.join(IMG_DIR, "event-sequence-recovery.svg"), w, h, *frags)


def fig_event_metadata_workflow():
    """Ланцюг метаданих Component Information: генерація, кешування та підстановка аргументів."""
    w, h = 820, 380
    frags = []

    # Фаза 1: Збирання прошивки
    frags.append(rect(15, 15, 240, 350, fill="#f9fbfd", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(135, 38, "1. ЕТАП ЗБИРАННЯ", size=13, color=NEG, bold=True))
    tb_src, _, _ = textbox(135, 90, "Код прошивки C++\n@event compass_cal_failed\nАргументи: [id: u8, dev: f32]", size=10.5, pad=8, fill="#ffffff", stroke=LINE)
    tb_tool, _, _ = textbox(135, 185, "Генератор libevents\n1. Обчислення хешу ID\n2. Збірка events.json\n3. Стиснення events.json.xz", size=10, pad=8, fill="#ffffff", stroke=NEG)
    tb_bin, _, _ = textbox(135, 290, "Бінарна прошивка\nМістить лише CRC хеші,\nнуль довгих рядків у Flash", size=10, pad=8, fill="#ffffff", stroke=LINE)

    frags.extend([tb_src, tb_tool, tb_bin])
    frags.append(arrow(135, 125, 135, 150, color=NEG))
    frags.append(arrow(135, 235, 135, 255, color=NEG))

    # Стрілка між фазами 1 та 2
    frags.append(arrow(255, 185, 295, 185, color=LINE, sw=1.8))
    frags.append(text(275, 175, "JSON", size=10, color=MUTED))

    # Фаза 2: Поширення та кешування
    frags.append(rect(295, 15, 240, 350, fill="#fbfdf9", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(415, 38, "2. КЕШУВАННЯ МЕТАДАНИХ", size=13, color=FIELD, bold=True))
    tb_meta, _, _ = textbox(415, 90, "Джерело метаданих\nMAVLink FTP з автопілота\nабо хмарний сервер за git-хешем", size=10, pad=8, fill="#ffffff", stroke=LINE)
    tb_crc, _, _ = textbox(415, 185, "Перевірка CRC32\nХеш у COMP_METADATA\nзбігається з локальним кешем?", size=10, pad=8, fill="#ffffff", stroke=FIELD)
    tb_cache, _, _ = textbox(415, 290, "Локальний SSD кеш GCS\nМиттєве завантаження\nсловника подій за 10 мс", size=10, pad=8, fill="#ffffff", stroke=LINE)

    frags.extend([tb_meta, tb_crc, tb_cache])
    frags.append(arrow(415, 125, 415, 155, color=FIELD))
    frags.append(arrow(415, 225, 415, 255, color=FIELD))

    # Стрілка між фазами 2 та 3
    frags.append(arrow(535, 185, 575, 185, color=LINE, sw=1.8))
    frags.append(text(555, 175, "Словник", size=10, color=MUTED))

    # Фаза 3: Виконання у польоті
    frags.append(rect(575, 15, 230, 350, fill="#fdfbf9", stroke=POS, sw=1.5, rx=8))
    frags.append(text(690, 38, "3. ДЕКОДУВАННЯ В GCS", size=13, color=POS, bold=True))
    tb_rx, _, _ = textbox(690, 90, "Прийом EVENT кадру\nID: 0x8A12B4C0\nRaw args: [0x01, 0xCD 0xCC 0x8C 0x40]", size=10, pad=8, fill="#ffffff", stroke=LINE)
    tb_fmt, _, _ = textbox(690, 185, "Підстановка шаблону\nID → \"Компас {1} збій\"\n{1} = 1, {2} = 4.4°\nМова: Українська", size=10, pad=8, fill="#ffffff", stroke=POS)
    tb_ui, _, _ = textbox(690, 290, "Інтерфейс оператора\nПовідомлення + порада:\n«Повторіть калібрування\nдалі від металу»", size=10, pad=8, fill="#ffffff", stroke=LINE)

    frags.extend([tb_rx, tb_fmt, tb_ui])
    frags.append(arrow(690, 125, 690, 155, color=POS))
    frags.append(arrow(690, 225, 690, 255, color=POS))

    return render(os.path.join(IMG_DIR, "event-metadata-workflow.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_statustext_vs_events()
    fig_event_packet_layout()
    fig_event_sequence_recovery()
    fig_event_metadata_workflow()
    print("All figures generated successfully.")
