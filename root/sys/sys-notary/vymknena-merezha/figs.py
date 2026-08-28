# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми vymknena-merezha (sys-notary).
Генерує 2 SVG-схеми в ./img/ за допомогою спільного svgkit.
"""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(SCRIPT_DIR, "img"), exist_ok=True)


# ── Фігура 1: Хронологія вимкнення стільникових мереж та рефармінг спектра ────
def fig_cellular_sunsetting_timeline():
    W, H = 1000, 580
    P = []
    P.append(text(W / 2, 28, "Хронологія вимкнення стандартів зв'язку та рефармінг частотного спектра", size=16, bold=True))

    # Верхній блок: Покоління мереж і життєвий цикл
    P.append(rect(30, 55, 940, 275, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(500, 78, "ЖИТТЄВИЙ ЦИКЛ СТІЛЬНИКОВИХ ТЕХНОЛОГІЙ ТА ПЕРІОДИ SUNSETTING", size=12, bold=True, color="#1e293b"))

    # Смуги поколінь
    gens = [
        ("2G (GSM / GPRS / EDGE)", "1991 — 2025/2030", "Спектральна ефективність: 0.1–0.2 біт/с/Гц\nСША: вимкнено (2017–2020); ЄС: тримається через eCall і лічильники (до 2026–2030)\nСтатус: критичний ризик раптового відключення", "#fee2e2", "#b91c1c", 98),
        ("3G (UMTS / HSPA+)", "2001 — 2022/2025", "Спектральна ефективність: 0.5–1.0 біт/с/Гц\nСША/ЄС/Азія: масове вимкнення завершено / на фінальній стадії\nЧастоти 2100/900 МГц повністю передані під LTE та 5G NR", "#ffedd5", "#c2410c", 154),
        ("4G (LTE / LTE-M / NB-IoT)", "2010 — 2040+", "Спектральна ефективність: 2.0–4.0 біт/с/Гц\nФундаментальний несучий шар для IoT (Rel 13–16). Гарантована робота в 2030-х\nПідтримка PSM, eDRX, автономність до 10–15 років на батареї", "#ecfdf5", "#047857", 210),
        ("5G & NTN (RedCap / 5G NR / Супутник)", "2020 — 2045+", "Спектральна ефективність: 5.0–10.0+ біт/с/Гц\n3GPP Rel 17/18: пряме підключення до супутників (NTN) та дешеві RedCap-модеми\nМасове розгортання та заміна вибулих стандартів", "#e0e7ff", "#4338ca", 266)
    ]

    for title, span, desc, fill_c, strk_c, y in gens:
        P.append(rect(45, y, 220, 46, fill=fill_c, stroke=strk_c, sw=1.5, rx=5))
        P.append(text(155, y + 18, title, size=10.5, bold=True, color=strk_c))
        P.append(text(155, y + 36, span, size=9.5, color=MUTED))

        P.append(rect(275, y, 680, 46, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
        P.append(mtext(615, y + 16, desc, size=9.5, color=INK, lh=1.25))

    # Нижній блок: Механізм рефармінгу спектра (800 / 900 / 1800 / 2100 МГц)
    P.append(rect(30, 345, 940, 215, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(500, 368, "РЕФАРМІНГ СПЕКТРА: МІГРАЦІЯ СМУГ ВІД 2G/3G ДО LTE-M, NB-IoT ТА 5G NR", size=12, bold=True, color="#1e293b"))

    bands = [
        ("Sub-1GHz (800 / 900 МГц)\nB8, B20, B28", "Раніше: GSM-900 (200 кГц канали)\nЗараз: NB-IoT (Guard-band/In-band) + LTE-M\nПеревага: проникнення крізь стіни та радіус до 15–35 км", "#dbeafe", "#1d4999"),
        ("Mid-band (1800 / 2100 МГц)\nB1, B3", "Раніше: DCS-1800, 3G UMTS-2100\nЗараз: LTE FDD (15–20 МГц) та 5G NR Band n1/n3\nПеревага: висока пропускна здатність", "#fef3c7", "#b45309"),
        ("Супутниковий S/L-band\n3GPP Rel 17 NTN", "Прямий канал модем ↔ супутник (LEO/GEO)\nКомпенсація доплерівського зсуву та RTT ~250–540 мс\nРезервний канал за повної відсутності вишок", "#ede9fe", "#6d28d9")
    ]

    bw = 285
    bgap = 25
    x_start = 55

    for i, (title, desc, fill_c, strk_c) in enumerate(bands):
        bx = x_start + i * (bw + bgap)
        by = 385
        P.append(rect(bx, by, bw, 155, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        P.append(mtext(bx + bw / 2, by + 22, title, size=11, bold=True, color=strk_c, lh=1.2))
        P.append(mtext(bx + bw / 2, by + 72, desc, size=9.5, color=INK, lh=1.3))

    render(os.path.join(SCRIPT_DIR, "img", "cellular-sunsetting-timeline.svg"), W, H, *P)


# ── Фігура 2: Архітектура циклічного буфера Store-and-Forward у Flash-пам'яті ──
def fig_store_and_forward_flash_ringbuffer():
    W, H = 1000, 580
    P = []
    P.append(text(W / 2, 28, "Архітектура циклічного Flash-буфера Store-and-Forward при втраті мережі", size=16, bold=True))

    # Верхній контур: Сектори кільцевого буфера
    P.append(rect(30, 55, 940, 245, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(500, 78, "СТАН СЕКТОРІВ FLASH-ПАМ'ЯТІ (4 КБ СЕКТОРИ З ВИРІВНЮВАННЯМ ЗНОСУ)", size=12, bold=True, color="#1e293b"))

    sectors = [
        ("Сектор #0 (DIRTY)", "Статус: 0x00\nВсі записи підтверджено\n(ACK отримано)\nОчікує background erase", "#f1f5f9", "#64748b"),
        ("Сектор #1 (TAIL)", "Статус: 0xFC (FULL)\nПоточний хвіст зчитування\nВивантаження в мережу\nЗчитування батчів", "#e0e7ff", "#4338ca"),
        ("Сектор #2 (QUEUED)", "Статус: 0xFC (FULL)\nЧерга невідправлених даних\nЗаписи з CRC-32\nОчікує своєї черги", "#fef3c7", "#b45309"),
        ("Сектор #3 (HEAD)", "Статус: 0xFE (ACTIVE)\nПоточна голова запису\nДописування телеметрії\nВказівник Write Head", "#ecfdf5", "#047857"),
        ("Сектор #4 (FREE)", "Статус: 0xFF (ERASED)\nСтертий сектор (0xFF)\nГотовий до ротації\nЗнос: N циклів", "#ffffff", "#059669")
    ]

    sw = 165
    sgap = 20
    sx_start = 55

    for i, (title, desc, fill_c, strk_c) in enumerate(sectors):
        bx = sx_start + i * (sw + sgap)
        by = 98
        P.append(rect(bx, by, sw, 140, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        P.append(text(bx + sw / 2, by + 20, title, size=10.5, bold=True, color=strk_c))
        P.append(mtext(bx + sw / 2, by + 48, desc, size=9.5, color=INK, lh=1.3))

        if i < len(sectors) - 1:
            P.append(arrow(bx + sw + 2, by + 70, bx + sw + sgap - 4, by + 70, color="#64748b", sw=2))

    # Зворотна стрілка кільця
    P.append(text(500, 268, "Циклічна ротація секторів (Tail Cursor вивантажує -> Sector Erase -> Head переходить до стертого)", size=10, italic=True, color="#475569"))

    # Нижній контур: Внутрішня структура сектора та атомарні переходи станів
    P.append(rect(30, 315, 940, 245, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(500, 338, "СТРУКТУРА ЗАПИСУ ТА АТОМАРНІ ПЕРЕХОДИ БІТІВ (1 -> 0 БЕЗ СТИРАННЯ)", size=12, bold=True, color="#1e293b"))

    # Блок заголовка сектора
    P.append(rect(55, 360, 260, 180, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=6))
    P.append(text(185, 382, "Заголовок сектора (16 байтів)", size=11, bold=True, color="#0284c7"))
    hdr_fields = "• Magic: 0x53464C53 ('SFLS')\n• Seq Number: uint32_t (монотонний)\n• Erase Count: uint32_t (лічильник зносу)\n• Sector State: 1 байт\n   0xFF (ERASED) -> 0xFE (ACTIVE)\n   -> 0xFC (FULL) -> 0x00 (DIRTY)\n• CRC-16 заголовка"
    P.append(mtext(185, 410, hdr_fields, size=9.5, color=INK, lh=1.35))

    # Блок структури запису телеметрії
    P.append(rect(340, 360, 300, 180, fill="#ffffff", stroke="#059669", sw=1.5, rx=6))
    P.append(text(490, 382, "Запис телеметрії (Frame Layout)", size=11, bold=True, color="#059669"))
    rec_fields = "• Magic Record: 0xAA55 (2 байти)\n• Record State: 0xFF -> 0xFE (Writing)\n   -> 0xFC (Committed) -> 0x00 (Acked)\n• Payload Length: uint16_t\n• Sequence ID: uint32_t\n• Timestamp Delta: Varint (1–4 байти)\n• Compressed Payload (Delta+Varint)\n• Checksum: CRC-32 (4 байти)"
    P.append(mtext(490, 410, rec_fields, size=9.5, color=INK, lh=1.35))

    # Блок атомарності при аварійному знеструмленні
    P.append(rect(665, 360, 280, 180, fill="#fff1f2", stroke="#e11d48", sw=1.5, rx=6))
    P.append(text(805, 382, "Аварійне знеструмлення (Power-Fail)", size=11, bold=True, color="#e11d48"))
    pf_fields = "1. Запис заголовка і даних у Flash\n2. Обчислення CRC-32 буфера даних\n3. Фінальний коміт: запис 0xFC у State\n\nПри раптовому вимиканні живлення:\n• Якщо State == 0xFE або CRC бітий:\n  запис вважається незавершеним,\n  ігнорується та затирається."
    P.append(mtext(805, 408, pf_fields, size=9.5, color=INK, lh=1.3))

    render(os.path.join(SCRIPT_DIR, "img", "store-and-forward-flash-ringbuffer.svg"), W, H, *P)


if __name__ == "__main__":
    fig_cellular_sunsetting_timeline()
    fig_store_and_forward_flash_ringbuffer()
    print("Фігури успішно згенеровано.")
