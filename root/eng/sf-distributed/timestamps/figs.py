# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Точки фіксування міток часу та накопичення джитеру ───────────
def fig_hw_vs_sw_timestamp_points():
    W, H = 840, 480
    parts = []
    parts.append(text(W/2, 26, "Точки фіксування міток часу в мережевому стеку та джерело невизначеності", size=16, bold=True))

    # Стовпчик шарів стека (зверху вниз: User -> Kernel Socket -> Driver/DMA -> MAC -> PHY)
    layers = [
        ("Користувацька програма", "gettimeofday() / clock_gettime()", "Джитер: 50–500 мкс (планувальник ОС, кванти CPU)", POS),
        ("Сокетний буфер ядра (sk_buff)", "SOF_TIMESTAMPING_TX_SOFTWARE (сокети)", "Джитер: 10–50 мкс (стек протоколів, блокування)", POS),
        ("Драйвер мережевої карти та NAPI", "SOF_TIMESTAMPING_TX_SCHED / DMA ring", "Джитер: 2–15 мкс (черги дескрипторів, переривання)", "#d35400"),
        ("MAC-контролер мережевої карти", "Апаратна мітка на межі SFD (IEEE 1588 PHC)", "Точність: 5–20 нс (тактові цикли MAC)", FIELD),
        ("Фізичний трансивер (PHY)", "Апаратна мітка на MII/MDI інтерфейсі", "Точність: < 1–5 нс (безпосередньо на міді/оптиці)", FIELD),
    ]

    top_y = 65
    box_h = 58
    box_w = 480
    box_x = 40
    gap = 20

    for i, (title_str, sub_str, jitter_str, col) in enumerate(layers):
        cy = top_y + i * (box_h + gap) + box_h/2
        # Прямокутник шару
        b = fitbox(box_x, top_y + i * (box_h + gap), box_w, box_h,
                   f"{title_str}\n{sub_str}", size=12.5,
                   fill="#f9fafb" if col == FIELD else "#ffffff",
                   stroke=col, sw=1.8, bold=True)
        parts.append(b)

        # Блок оцінки похибки/джитеру праворуч
        jb = fitbox(box_x + box_w + 30, top_y + i * (box_h + gap), 260, box_h,
                    jitter_str, size=11.5,
                    fill="#fdecea" if col == POS else ("#fef5e7" if col == "#d35400" else "#eafaf1"),
                    stroke=col, color=col, bold=True)
        parts.append(jb)

        # Стрілка між шарами (якщо не останній)
        if i < len(layers) - 1:
            arrow_y1 = top_y + (i + 1) * box_h + i * gap
            arrow_y2 = arrow_y1 + gap
            parts.append(arrow(box_x + box_w/2, arrow_y1, box_x + box_w/2, arrow_y2, color=LINE, sw=1.5))

    render(os.path.join(IMG, "hw-vs-sw-timestamp-points.svg"), W, H, *parts)


# ── Фігура 2: Структура форматів міток часу (NTP, PTP, RTP) ────────────────
def fig_timestamp_formats_comparison():
    W, H = 840, 460
    parts = []
    parts.append(text(W/2, 26, "Бітова структура основних форматів часових міток", size=16, bold=True))

    # 1. NTP 64-bit Format
    y_ntp = 60
    parts.append(text(40, y_ntp + 15, "1. NTP 64-бітний формат (RFC 5905, шкала з 1900 року, квант 232.8 пс):", size=13, bold=True, anchor="start"))
    w_sec_ntp = 370
    w_frac_ntp = 370
    b_ntp_sec = fitbox(40, y_ntp + 28, w_sec_ntp, 42, "32 біти: Цілі секунди\nДіапазон: 0 .. 4 294 967 295 с (~136 років)", size=11.5, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    b_ntp_frac = fitbox(40 + w_sec_ntp + 10, y_ntp + 28, w_frac_ntp, 42, "32 біти: Дробова частина секунди\nКвант: 2⁻³² с ≈ 0.2328 нс (двійковий фіксований дріб)", size=11.5, fill="#f4f6f8", stroke=LINE, color=INK, bold=True)
    parts.extend([b_ntp_sec, b_ntp_frac])

    # 2. PTP (IEEE 1588) 80-bit Timestamp + 64-bit Correction Field
    y_ptp = 170
    parts.append(text(40, y_ptp + 15, "2. PTP IEEE 1588 80-бітний формат (шкала TAI з 1970 року) + CorrectionField:", size=13, bold=True, anchor="start"))
    w_ptp_sec = 440
    w_ptp_ns = 300
    b_ptp_sec = fitbox(40, y_ptp + 28, w_ptp_sec, 42, "48 бітів: Секунди TAI (UInt48)\nДіапазон: ~8.9 млн років без переповнення", size=11.5, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    b_ptp_ns = fitbox(40 + w_ptp_sec + 10, y_ptp + 28, w_ptp_ns, 42, "32 біти: Наносекунди (UInt32)\nДіапазон: 0 .. 999 999 999 нс", size=11.5, fill="#f4f6f8", stroke=LINE, color=INK, bold=True)
    
    # Correction field row
    b_ptp_corr = fitbox(40, y_ptp + 76, 750, 36, "CorrectionField (64 біти): Наносекунди, масштабовані на 2¹⁶ (48 бітів цілих нс + 16 бітів суб-нс дробу)", size=11.5, fill="#fef5e7", stroke="#d35400", color="#d35400", bold=True)
    parts.extend([b_ptp_sec, b_ptp_ns, b_ptp_corr])

    # 3. RTP 32-bit Media Timestamp
    y_rtp = 325
    parts.append(text(40, y_rtp + 15, "3. RTP 32-бітний формат (RFC 3550, такти медіа-кодека):", size=13, bold=True, anchor="start"))
    b_rtp = fitbox(40, y_rtp + 28, 750, 48, "32 біти: Лічильник тактів квантування медіапотоку (RTP Timestamp)\nВідео (90 кГц): 1 такт = 11.11 мкс (період переповнення ~13.2 години)\nАудіо (48 кГц): 1 такт = 20.83 мкс (період переповнення ~24.8 години)", size=11.5, fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b_rtp)

    render(os.path.join(IMG, "timestamp-formats-comparison.svg"), W, H, *parts)


# ── Фігура 3: Перехресне фіксування (Cross-timestamping) ───────────────────
def fig_cross_timestamping_sandwich():
    W, H = 840, 430
    parts = []
    parts.append(text(W/2, 26, "Перехресне фіксування часу: Програмний «сендвіч» проти апаратного Cross-TS", size=16, bold=True))

    # Ліва колонка: Програмний сендвіч
    left_x = 40
    col_w = 365
    parts.append(fitbox(left_x, 60, col_w, 35, "Програмне опитування (PTP_SYS_OFFSET)", size=13, fill="#f4f6f8", stroke=LINE, bold=True))

    # Схема сендвіча
    sy = 110
    parts.append(fitbox(left_x + 20, sy, 325, 34, "1. Зчитування CPU TSC₁ (t_cpu1)", size=11.5, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    parts.append(arrow(left_x + 182, sy + 34, left_x + 182, sy + 52, color=LINE))
    
    parts.append(fitbox(left_x + 20, sy + 52, 325, 34, "2. Читання PHC через PCIe шину (t_phc)", size=11.5, fill="#fdecea", stroke=POS, color=POS, bold=True))
    parts.append(arrow(left_x + 182, sy + 86, left_x + 182, sy + 104, color=LINE))
    
    parts.append(fitbox(left_x + 20, sy + 104, 325, 34, "3. Зчитування CPU TSC₂ (t_cpu2)", size=11.5, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))

    res_box_l = fitbox(left_x, sy + 155, col_w, 90,
                       "Оцінка часу CPU: t_cpu ≈ (t_cpu1 + t_cpu2) / 2\n"
                       "Похибка: ±(t_cpu2 − t_cpu1) / 2\n"
                       "Затримка шини PCIe: 500 нс – 5 мкс\n"
                       "(несиметричні черги транзакцій PCIe)",
                       size=11.5, fill="#fdecea", stroke=POS, color=POS, bold=False)
    parts.append(res_box_l)

    # Права колонка: Апаратний Cross-timestamping
    right_x = 435
    parts.append(fitbox(right_x, 60, col_w, 35, "Апаратне фіксування (PTP_SYS_OFFSET_PRECISE / PTM)", size=13, fill="#eafaf1", stroke=FIELD, bold=True))

    hy = 110
    parts.append(fitbox(right_x + 20, hy, 325, 42, "Апаратний тригер / Сигнал PCIe PTM\n(Спільний фронт стробування)", size=11.5, fill="#fef5e7", stroke="#d35400", color="#d35400", bold=True))
    
    parts.append(arrow(right_x + 182, hy + 42, right_x + 90, hy + 75, color=FIELD))
    parts.append(arrow(right_x + 182, hy + 42, right_x + 275, hy + 75, color=FIELD))

    parts.append(fitbox(right_x + 10, hy + 75, 160, 48, "Регістр CPU\n(TSC / ART)\nОдночасна фіксація", size=11.5, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    parts.append(fitbox(right_x + 195, hy + 75, 160, 48, "Регістр PHC\n(IEEE 1588 Clock)\nОдночасна фіксація", size=11.5, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))

    res_box_r = fitbox(right_x, hy + 155, col_w, 90,
                       "Зіставлення: (t_cpu, t_phc) фіксуються в один такт\n"
                       "Похибка прив'язки: < 5–10 нс\n"
                       "Повністю усуває вплив затримок ОС,\n"
                       "шини PCIe та переривань процесора",
                       size=11.5, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=False)
    parts.append(res_box_r)

    render(os.path.join(IMG, "cross-timestamping-sandwich.svg"), W, H, *parts)


# ── Фігура 4: Модульне розгортання лічильників при Wraparound ──────────────
def fig_wraparound_modular_unwrapping():
    W, H = 840, 420
    parts = []
    parts.append(text(W/2, 26, "Модульне розгортання 32-бітного лічильника у монотонну 64-бітну шкалу", size=16, bold=True))

    # Вісь циклічного простору 0 .. 2^32 - 1
    cx, cy, r = 220, 225, 110
    parts.append(circle(cx, cy, r, fill="#f8fafc", stroke=LINE, sw=2))
    parts.append(text(cx, cy - r - 12, "0 / 2³²", size=12, bold=True))
    parts.append(text(cx + r + 24, cy + 4, "2³¹ - 1", size=11.5, color=MUTED))
    parts.append(text(cx, cy + r + 16, "2³¹", size=11.5, color=MUTED))
    parts.append(text(cx - r - 24, cy + 4, "3 · 2³⁰", size=11.5, color=MUTED))

    # Точки t_prev та t_curr на колі (перехід через 0)
    px, py = cx - 40, cy - r + 8
    qx, qy = cx + 45, cy - r + 10
    parts.append(circle(px, py, 5, fill=POS, stroke=POS))
    parts.append(text(px - 10, py - 12, "t_prev (0xFFFFF800)", size=11, color=POS, bold=True, anchor="end"))
    
    parts.append(circle(qx, qy, 5, fill=FIELD, stroke=FIELD))
    parts.append(text(qx + 10, qy - 12, "t_curr (0x00000800)", size=11, color=FIELD, bold=True, anchor="start"))

    # Стрілка прогресу вздовж кола через нуль
    parts.append(arrow(px, py, qx, qy, color=FIELD, sw=2.5))
    parts.append(textbox(cx, cy + 5, "Перехід через 0\nt_curr < t_prev,\nале Δt > 0", size=11.5, fill="#ffffff", stroke=FIELD, color=FIELD, bold=True)[0])

    # Права частина: математична формула розгортання
    rx = 450
    parts.append(fitbox(rx, 80, 350, 42, "Формула знакової різниці в доповняльному коді:", size=12, fill="#f4f6f8", stroke=LINE, bold=True))

    calc_lines = (
        "int32_t delta = (int32_t)(t_curr - t_prev);\n"
        "// 0x00000800 - 0xFFFFF800 = 0x00001000 (+4096)\n\n"
        "int64_t unwrapped_t += (int64_t)delta;\n\n"
        "Умова однозначності (теорема дискретизації):\n"
        "|справжня зміна часу| < 2³¹ тактів\n"
        "• delta > 0: звичайний хід часу вперед\n"
        "• delta < 0: перевпорядкування пакетів у мережі"
    )
    parts.append(fitbox(rx, 135, 350, 180, calc_lines, size=11.5, fill="#ffffff", stroke=FIELD, color=INK, bold=False))

    parts.append(fitbox(rx, 330, 350, 55, "Гарантія: 64-бітна шкала лишається суворо монотонною\nі захищеною від збоїв при переповненні лічильника.", size=11.5, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(IMG, "wraparound-modular-unwrapping.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_hw_vs_sw_timestamp_points()
    fig_timestamp_formats_comparison()
    fig_cross_timestamping_sandwich()
    fig_wraparound_modular_unwrapping()
    print("All figures generated successfully.")
