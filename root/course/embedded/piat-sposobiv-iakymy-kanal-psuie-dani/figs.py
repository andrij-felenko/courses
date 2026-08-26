# -*- coding: utf-8 -*-
"""Фігури до теми «П'ять способів, якими канал псує дані»
(root/course/embedded/piat-sposobiv-iakymy-kanal-psuie-dani).
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def svg_path(d, stroke=LINE, fill="none", sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'


# ── 1. П'ять способів псування даних ──────────────────────────────────────────
def fig_flaws_overview():
    W, H = 880, 520
    f = []
    f.append(text(W / 2, 28, "П'ять руйнівних режимів фізичного каналу зв'язку",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "кожен тип пошкодження вимагає окремого алгоритмічного захисту на рівні протоколу",
                  11.5, MUTED, "middle", italic=True))

    cards = [
        ("1. Спотворення бітів",
         "Шум, наводки dI/dt, спалахи",
         "0x55 0xAA 0x12 -> 0x55 0xBA 0x12 (інверсія бітів)",
         "Захист: CRC-16/32, коди Хеммінга, Reed-Solomon",
         POS, "#fdf2f2"),
        ("2. Втрата пакетів",
         "Згасання сигналу, колізії, переповнення FIFO",
         "Кадр №4 надіслано -> у приймач не дійшов нічого",
         "Захист: квитування (ACK/NACK), таймери та ARQ",
         NEG, "#eef4ff"),
        ("3. Дублювання повідомлень",
         "Втрата зворотного ACK -> повторне надсилання",
         "Кадр №2 виконано -> ACK втрачено -> повтор №2",
         "Захист: монотонні порядкові номери (Sequence Numbers)",
         "#d97706", "#fffbeb"),
        ("4. Перевпорядкування",
         "Різні шляхи в mesh-мережі, затримки повторів",
         "Надіслано [1, 2, 3] -> отримано [1, 3, 2]",
         "Захист: приймальне вікно та буфер впорядкування",
         "#7c3aed", "#f5f3ff"),
        ("5. Фрагментація та склеювання",
         "Потокові шини (UART/TCP) без меж повідомлень",
         "Пакет 64Б ріжеться [18Б + 46Б] або 2 пакети злипаються",
         "Захист: демаркація меж (COBS / байт-стафінг)",
         FIELD, "#eafaf0")
    ]

    y_start = 68
    card_h = 78
    gap = 10

    for i, (title, cause, symptom, defense, col, bg_col) in enumerate(cards):
        y = y_start + i * (card_h + gap)
        # card background
        f.append(rect(40, y, W - 80, card_h, fill=bg_col, stroke=col, sw=1.6, rx=6))
        # left accent bar
        f.append(rect(40, y, 6, card_h, fill=col, stroke=col, sw=0, rx=2))

        # Title
        f.append(text(60, y + 20, title, 13.0, col, "start", bold=True))
        # Cause & Symptom
        f.append(text(60, y + 42, f"Причина: {cause}", 11.0, INK, "start"))
        f.append(text(60, y + 62, f"Прояв: {symptom}", 11.0, MUTED, "start", italic=True))
        # Defense (right side)
        f.append(rect(W - 420, y + 14, 360, 50, fill="#ffffff", stroke=col, sw=1.0, rx=4))
        f.append(text(W - 410, y + 33, "Рівень захисту:", 10.5, MUTED, "start", italic=True))
        f.append(text(W - 410, y + 51, defense, 11.0, col, "start", bold=True))

    f.append(text(W / 2, H - 12,
                  "Ілюзія «труби» руйнується: одна контрольна сума не здатна вирішити проблеми 2, 3, 4 та 5.",
                  11.0, INK, "middle", italic=True))

    render(os.path.join(IMG, "five-channel-modes.svg"), W, H, *f)


# ── 2. COBS кадрування: усунення нулів та демаркація ──────────────────────────
def fig_cobs_framing():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 28, "COBS-кадрування: гарантована відсутність нулів усередині кадру",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "байт 0x00 стає унікальним прапорцем межі; оверхед становить лише 1 байт на 254 байти",
                  11.5, MUTED, "middle", italic=True))

    # Input payload
    y_in = 90
    f.append(text(60, y_in + 20, "Вихідні дані (з нулями):", 12.5, INK, "start", bold=True))

    raw_bytes = [
        ("0x41", "'A'", False),
        ("0x00", "ZERO", True),
        ("0x42", "'B'", False),
        ("0x43", "'C'", False),
        ("0x00", "ZERO", True),
        ("0x44", "'D'", False)
    ]

    bx = 270
    bw = 64
    bh = 46
    bgap = 8

    for i, (val, label, is_zero) in enumerate(raw_bytes):
        x = bx + i * (bw + bgap)
        col = POS if is_zero else NEG
        bg = "#fdecea" if is_zero else "#eaf0fd"
        f.append(rect(x, y_in, bw, bh, fill=bg, stroke=col, sw=1.8, rx=4))
        f.append(text(x + bw / 2, y_in + 20, val, 12.0, col, "middle", bold=True))
        f.append(text(x + bw / 2, y_in + 36, label, 10.0, MUTED, "middle"))

    # Arrow down
    f.append(arrow(W / 2, y_in + bh + 14, W / 2, y_in + bh + 48, color=FIELD, sw=2.2))
    f.append(text(W / 2 + 12, y_in + bh + 34, "COBS-кодування (покажчики зміщення до наступного 0x00)",
                  11.0, FIELD, "start", bold=True))

    # Encoded payload
    y_out = y_in + bh + 62
    f.append(text(60, y_out + 20, "Закодований кадр:", 12.5, INK, "start", bold=True))

    enc_bytes = [
        ("0x02", "Зсув 2", FIELD, "#eafaf0"),
        ("0x41", "'A'", NEG, "#eaf0fd"),
        ("0x03", "Зсув 3", FIELD, "#eafaf0"),
        ("0x42", "'B'", NEG, "#eaf0fd"),
        ("0x43", "'C'", NEG, "#eaf0fd"),
        ("0x02", "Зсув 2", FIELD, "#eafaf0"),
        ("0x44", "'D'", NEG, "#eaf0fd"),
        ("0x00", "МЕЖА", POS, "#fdecea")
    ]

    bx_out = 230
    for i, (val, label, col, bg) in enumerate(enc_bytes):
        x = bx_out + i * (bw + bgap)
        f.append(rect(x, y_out, bw, bh, fill=bg, stroke=col, sw=2.0, rx=4))
        f.append(text(x + bw / 2, y_out + 20, val, 12.0, col, "middle", bold=True))
        f.append(text(x + bw / 2, y_out + 36, label, 10.0, col if col == POS else MUTED, "middle", bold=(col == POS)))

    # Pointer arches
    p0_x = bx_out + bw / 2
    p1_x = bx_out + 2 * (bw + bgap) + bw / 2
    p2_x = bx_out + 5 * (bw + bgap) + bw / 2
    p3_x = bx_out + 7 * (bw + bgap) + bw / 2

    # Arch 1
    f.append(svg_path(f"M {p0_x} {y_out + bh + 4} Q {(p0_x + p1_x)/2} {y_out + bh + 30} {p1_x} {y_out + bh + 4}",
                      stroke=FIELD, fill="none", sw=1.6))
    f.append(text((p0_x + p1_x)/2, y_out + bh + 38, "+2 байти", 10.0, FIELD, "middle", bold=True))

    # Arch 2
    f.append(svg_path(f"M {p1_x} {y_out + bh + 4} Q {(p1_x + p2_x)/2} {y_out + bh + 36} {p2_x} {y_out + bh + 4}",
                      stroke=FIELD, fill="none", sw=1.6))
    f.append(text((p1_x + p2_x)/2, y_out + bh + 44, "+3 байти", 10.0, FIELD, "middle", bold=True))

    # Arch 3
    f.append(svg_path(f"M {p2_x} {y_out + bh + 4} Q {(p2_x + p3_x)/2} {y_out + bh + 30} {p3_x} {y_out + bh + 4}",
                      stroke=FIELD, fill="none", sw=1.6))
    f.append(text((p2_x + p3_x)/2, y_out + bh + 38, "+2 (кінець)", 10.0, FIELD, "middle", bold=True))

    f.append(text(W / 2, H - 14,
                  "Жоден байт тіла не дорівнює 0x00. Нульовий байт надійно демаркує кінець кадру в будь-якому потоці.",
                  11.0, INK, "middle", italic=True))

    render(os.path.join(IMG, "cobs-framing.svg"), W, H, *f)


# ── 3. Конвеєр надійного канального приймача ──────────────────────────────────
def fig_rx_pipeline():
    W, H = 880, 360
    f = []
    f.append(text(W / 2, 28, "Модульний конвеєр надійного канального приймача",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "послідовна обробка: демаркація -> розпакування -> цілісність -> дедуплікація -> застосунок",
                  11.5, MUTED, "middle", italic=True))

    stages = [
        ("UART / DMA", "Сирий потік", "Кільцевий буфер байтів", MUTED, "#f4f6f8"),
        ("Демаркатор", "Пошук 0x00", "Виділення пачки кадру", FIELD, "#eafaf0"),
        ("COBS декодер", "Unstuffing", "Відновлення сирих байтів", NEG, "#eaf0fd"),
        ("Перевірка CRC-16", "Детекція збоїв", "Поліном 0x1021", POS, "#fdf2f2"),
        ("Дедуплікатор", "Seq Number", "Фільтр повторів кадру", "#7c3aed", "#f5f3ff"),
        ("Застосунок", "Корисні дані", "Виконання команди", FIELD, "#eafaf0")
    ]

    bw = 120
    bh = 110
    gap = 22
    x_start = (W - (len(stages) * bw + (len(stages) - 1) * gap)) / 2
    y_stage = 88

    for i, (title, sub, detail, col, bg) in enumerate(stages):
        x = x_start + i * (bw + gap)
        # Box
        f.append(rect(x, y_stage, bw, bh, fill=bg, stroke=col, sw=2.0, rx=6))
        # Step number circle
        f.append(circle(x + 18, y_stage + 18, 10, fill=col, stroke=col, sw=1))
        f.append(text(x + 18, y_stage + 22, str(i + 1), 10.0, "#ffffff", "middle", bold=True))

        # Title
        f.append(text(x + bw / 2, y_stage + 44, title, 11.5, col, "middle", bold=True))
        # Sub
        f.append(text(x + bw / 2, y_stage + 68, sub, 10.5, INK, "middle"))
        # Detail
        f.append(text(x + bw / 2, y_stage + 90, detail, 9.5, MUTED, "middle", italic=True))

        # Arrow to next
        if i < len(stages) - 1:
            ax = x + bw + 2
            f.append(arrow(ax, y_stage + bh / 2, ax + gap - 4, y_stage + bh / 2, color=MUTED, sw=1.8))

    # Failure arrows dropping down
    # CRC Drop
    crc_x = x_start + 3 * (bw + gap) + bw / 2
    f.append(arrow(crc_x, y_stage + bh + 4, crc_x, y_stage + bh + 46, color=POS, sw=1.8))
    f.append(rect(crc_x - 55, y_stage + bh + 48, 110, 26, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    f.append(text(crc_x, y_stage + bh + 65, "Бітий кадр -> Скидання", 9.5, POS, "middle", bold=True))

    # Duplicate Drop
    dup_x = x_start + 4 * (bw + gap) + bw / 2
    f.append(arrow(dup_x, y_stage + bh + 4, dup_x, y_stage + bh + 46, color="#7c3aed", sw=1.8))
    f.append(rect(dup_x - 65, y_stage + bh + 48, 130, 26, fill="#f5f3ff", stroke="#7c3aed", sw=1.2, rx=3))
    f.append(text(dup_x, y_stage + bh + 65, "Дублікат -> Скидання + ACK", 9.5, "#7c3aed", "middle", bold=True))

    f.append(text(W / 2, H - 14,
                  "Конвеєрна обробка ізолює кожну проблему: CRC відсікає шум, Seq Number усуває дублікати, COBS тримає межі.",
                  11.0, INK, "middle", italic=True))

    render(os.path.join(IMG, "rx-pipeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_flaws_overview()
    fig_cobs_framing()
    fig_rx_pipeline()
    print("OK: all figures generated")
