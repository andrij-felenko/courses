# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Модем на платі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b9770e"
HOT    = "#c0392b"
COOL   = "#2457d6"
GND_C  = "#27ae60"

# ── 1. Часова діаграма передавального сплеску GSM/LTE та просадки напруги ──────
def fig_power_burst():
    W, H = 900, 480
    ox = 110
    p = []

    # Заголовок і підзаголовок
    p.append(text(W / 2, 28, "Імпульс передавача (Tx Burst) та динамічна просадка шини живлення", size=16, bold=True))
    p.append(text(W / 2, 50, "Піковий струм 2.0 А викликає просадку ΔV через активний опір ESR та розряд ємності", size=11, color=MUTED))

    # Секція струму I(t) зверху
    p.append(line(ox, 85, ox + 720, 85, color=LINE, sw=1.2))
    p.append(line(ox, 85, ox, 195, color=LINE, sw=1.2))
    p.append(text(ox - 15, 90, "Струм I", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 15, 115, "2.0 A", size=10.5, color=POS, anchor="end", bold=True))
    p.append(text(ox - 15, 185, "0.1 A", size=10.5, color=MUTED, anchor="end"))
    p.append(line(ox - 6, 110, ox, 110, color=MUTED, sw=1))
    p.append(line(ox - 6, 180, ox, 180, color=MUTED, sw=1))

    # Струмовий імпульс
    bx1, bx2 = ox + 180, ox + 450
    p.append(rect(bx1, 110, bx2 - bx1, 70, fill="#fdecea", stroke="none"))
    p.append('<path d="M %d,180 L %d,180 L %d,110 L %d,110 L %d,180 L %d,180" fill="none" stroke="%s" stroke-width="2.5"/>'
             % (ox, bx1, bx1, bx2, bx2, ox + 720, POS))

    p.append(text((bx1 + bx2) / 2, 145, "GSM/LTE Burst: 2.0 A (577 мкс)", size=11, color=POS, bold=True))

    # Стрілки тривалості пачки
    p.append(line(bx1, 205, bx2, 205, color=MUTED, sw=1.2))
    p.append(line(bx1, 200, bx1, 210, color=MUTED, sw=1.2))
    p.append(line(bx2, 200, bx2, 210, color=MUTED, sw=1.2))
    p.append(text((bx1 + bx2) / 2, 222, "t_burst = 577 мкс", size=10.5, color=MUTED))

    # Секція напруги VBAT(t) знизу
    vy_base = 250
    p.append(line(ox, vy_base, ox + 720, vy_base, color=LINE, sw=1.2))
    p.append(line(ox, vy_base, ox, vy_base + 170, color=LINE, sw=1.2))
    p.append(text(ox - 15, vy_base + 15, "Напруга V", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 15, vy_base + 35, "3.8 В", size=10.5, color=COOL, anchor="end", bold=True))
    p.append(text(ox - 15, vy_base + 90, "3.45 В", size=10.5, color=POS, anchor="end", bold=True))
    p.append(text(ox - 15, vy_base + 140, "3.3 В", size=10.5, color=MUTED, anchor="end"))

    # Лінія UVLO аварійного вимкнення
    p.append(line(ox, vy_base + 140, ox + 720, vy_base + 140, color=POS, sw=1.2, dash="4,4"))
    p.append(text(ox + 520, vy_base + 158, "Поріг UVLO (аварійне вимкнення: 3.3 В)", size=10.5, color=POS, bold=True))

    # Крива напруги з просадкою
    v_pts = [
        (ox, vy_base + 30),
        (bx1, vy_base + 30),
        (bx1 + 8, vy_base + 65),
        (bx1 + 80, vy_base + 90),
        (bx2, vy_base + 85),
        (bx2 + 15, vy_base + 55),
        (bx2 + 70, vy_base + 30),
        (ox + 720, vy_base + 30)
    ]
    p_str = " ".join("%.1f,%.1f" % pt for pt in v_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (p_str, COOL))

    # Пояснення стрибка ESR
    p.append(text(bx1 - 15, vy_base + 60, "Стрибок I·ESR", size=10, color=POS, anchor="end", bold=True))
    p.append(line(bx1 - 10, vy_base + 60, bx1 + 4, vy_base + 60, color=POS, sw=1))

    p.append(text((bx1 + bx2) / 2, vy_base + 115, "ΔV_drop ≤ 350 мВ (безпечний запас)", size=11, color=COOL, bold=True))

    # Вісь часу t
    p.append(arrow(ox + 670, vy_base + 180, ox + 740, vy_base + 180, color=LINE, sw=1.2))
    p.append(text(ox + 748, vy_base + 184, "t", size=11, color=LINE, anchor="start", italic=True))

    return render(os.path.join(OUT, "modem-power-burst.svg"), W, H, *p, title=None)


# ── 2. Схема силового живлення та батареї конденсаторів (PDN) ──────────────────
def fig_power_delivery():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 28, "Архітектура силового тракту живлення модема (PDN)", size=16, bold=True))
    p.append(text(W / 2, 50, "Понижувальний DC-DC Buck (≥3 А) + багатоступеневий конденсаторний буфер біля виводів VBAT", size=11, color=MUTED))

    # Блок DC-DC перетворювача зліва
    b1, _, _ = textbox(130, 150, "DC-DC Buck\nВхід: 5–24 В\nВихід: 3.8 В / 3.0 А\nI_sat ≥ 4.0 А", size=10.5, bold=True,
                       fill="#f4f6f8", stroke=LINE, pad=8)
    p.append(b1)

    # Силова шина VBAT
    p.append(line(230, 130, 730, 130, color=HOT, sw=4))
    p.append(text(480, 115, "Шина VBAT (ширина ≥ 2.0–3.0 мм, мідь 35 мкм)", size=11, color=HOT, bold=True))

    # Земляна шина знизу
    p.append(line(130, 320, 830, 320, color=GND_C, sw=3))
    p.append(text(480, 340, "Суцільний опорний полігон GND (шар L2 під шиною)", size=11, color=GND_C, bold=True))

    # З'єднання землі від DC-DC
    p.append(line(130, 205, 130, 320, color=GND_C, sw=2))

    # Конденсатори паралельно до землі
    caps = [
        (300, "470 мкФ POSCAP", "Low-ESR < 50 мОм"),
        (420, "100 мкФ MLCC", "X5R кераміка 0805"),
        (540, "100 нФ + 33 пФ", "MLCC RF 900 МГц"),
        (660, "10 пФ MLCC", "RF 1800 МГц Bypass")
    ]

    for cx, val, typ in caps:
        # Лінія від VBAT вниз до конденсатора
        p.append(line(cx, 130, cx, 180, color=HOT, sw=2))
        # Конденсатор
        p.append(rect(cx - 22, 180, 44, 26, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
        p.append(line(cx - 14, 189, cx + 14, 189, color=LINE, sw=2))
        p.append(line(cx - 14, 197, cx + 14, 197, color=LINE, sw=2))
        # Лінія від конденсатора до GND
        p.append(line(cx, 206, cx, 320, color=GND_C, sw=2))

        # Текстовий опис нижче лінії GND або акуратно праворуч
        p.append(text(cx, 375, val, size=10, bold=True, color=INK))
        p.append(text(cx, 395, typ, size=9.5, color=MUTED))

    # Блок модема справа
    b_modem, _, _ = textbox(830, 225, "Стільниковий\nмодем\n(Quectel / SIMCom)\nПік: 2.0 А\n3.4–4.2 В",
                            size=10.5, bold=True, fill="#eaf0fd", stroke=COOL, pad=8)
    p.append(b_modem)

    # З'єднання до модема
    p.append(arrow(730, 130, 755, 130, color=HOT, sw=3))
    p.append(line(755, 130, 765, 130, color=HOT, sw=3))
    p.append(line(755, 320, 765, 320, color=GND_C, sw=2))

    # Стрілка відстані
    p.append(line(670, 80, 765, 80, color=MUTED, sw=1.2))
    p.append(line(670, 75, 670, 85, color=MUTED, sw=1.2))
    p.append(line(765, 75, 765, 85, color=MUTED, sw=1.2))
    p.append(text(717, 70, "< 3–5 мм до піна", size=10, color=HOT, bold=True))

    return render(os.path.join(OUT, "power-delivery-schematic.svg"), W, H, *p, title=None)


# ── 3. Трасування 50-Ом радіотракту та Pi-узгоджувальний контур ────────────────
def fig_rf_layout():
    W, H = 920, 490
    p = []

    p.append(text(W / 2, 28, "Топологія радіочастотної лінії 50 Ом та Pi-подібний фільтр", size=16, bold=True))
    p.append(text(W / 2, 50, "Копланарний хвилевід із заземленням (GCPW), бар'єр перехідних отворів та Pi-контур", size=11, color=MUTED))

    # Ліва частина: переріз плати
    px, py = 50, 115
    p.append(text(px + 140, py, "Поперечний переріз GCPW (L1-L2)", size=12, bold=True))

    # Шар діелектрика FR-4
    p.append(rect(px, py + 35, 280, 70, fill="#d5e8d4", stroke="#82b366", sw=1.5, rx=3))
    p.append(text(px + 140, py + 75, "Діелектрик FR-4 (h = 0.2–0.5 мм)", size=10, color=INK))

    # Верхній шар міді (L1)
    p.append(rect(px, py + 15, 80, 20, fill="#f6ecd6", stroke=COPPER, sw=1.5, rx=2))
    p.append(text(px + 40, py + 29, "GND (L1)", size=9.5, color=COPPER, bold=True))

    p.append(rect(px + 105, py + 15, 70, 20, fill="#fdecea", stroke=HOT, sw=2, rx=2))
    p.append(text(px + 140, py + 29, "RF (50 Ом)", size=10, color=HOT, bold=True))

    p.append(rect(px + 200, py + 15, 80, 20, fill="#f6ecd6", stroke=COPPER, sw=1.5, rx=2))
    p.append(text(px + 240, py + 29, "GND (L1)", size=9.5, color=COPPER, bold=True))

    # Нижній шар міді (L2)
    p.append(rect(px, py + 105, 280, 20, fill="#f6ecd6", stroke=COPPER, sw=1.5, rx=2))
    p.append(text(px + 140, py + 119, "Опорний суцільний екран GND (L2)", size=10, color=COPPER, bold=True))

    # Перехідні отвори
    p.append(line(px + 30, py + 35, px + 30, py + 105, color=GND_C, sw=2.5, dash="2,2"))
    p.append(line(px + 250, py + 35, px + 250, py + 105, color=GND_C, sw=2.5, dash="2,2"))

    # Розміри s, w, s
    p.append(text(px + 92, py + 8, "зазор s", size=9.5, color=MUTED))
    p.append(text(px + 140, py + 8, "ширина w", size=9.5, color=MUTED))
    p.append(text(px + 192, py + 8, "зазор s", size=9.5, color=MUTED))

    # Права частина: Схема Pi-узгодження
    rx, ry = 420, 115
    p.append(text(rx + 230, ry, "Топологія узгоджувального фільтра біля роз'єму", size=12, bold=True))

    # Модуль зліва
    b_rf_out, _, _ = textbox(rx + 50, ry + 80, "RF_OUT\nмодема", size=10.5, bold=True, fill="#eaf0fd", stroke=COOL, pad=8)
    p.append(b_rf_out)

    # Центральна RF лінія
    p.append(line(rx + 90, ry + 80, rx + 400, ry + 80, color=HOT, sw=3.5))

    # Роз'єм антени справа
    b_ant, _, _ = textbox(rx + 440, ry + 80, "U.FL /\nSMA", size=10.5, bold=True, fill="#f4f6f8", stroke=LINE, pad=8)
    p.append(b_ant)

    # Pi-фільтр
    # C1
    p.append(line(rx + 160, ry + 80, rx + 160, ry + 120, color=HOT, sw=2))
    p.append(rect(rx + 148, ry + 120, 24, 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(rx + 160, ry + 134, "C1", size=10, bold=True))
    p.append(line(rx + 160, ry + 140, rx + 160, ry + 170, color=GND_C, sw=2))
    p.append(circle(rx + 160, ry + 170, 3, fill=GND_C, stroke=GND_C, sw=0))
    p.append(text(rx + 160, ry + 188, "GND (L2)", size=9.5, color=MUTED))

    # Послідовний елемент L/R
    p.append(rect(rx + 230, ry + 70, 44, 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(rx + 252, ry + 84, "L / 0R", size=9.5, bold=True))

    # C2
    p.append(line(rx + 340, ry + 80, rx + 340, ry + 120, color=HOT, sw=2))
    p.append(rect(rx + 328, ry + 120, 24, 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(rx + 340, ry + 134, "C2", size=10, bold=True))
    p.append(line(rx + 340, ry + 140, rx + 340, ry + 170, color=GND_C, sw=2))
    p.append(circle(rx + 340, ry + 170, 3, fill=GND_C, stroke=GND_C, sw=0))
    p.append(text(rx + 340, ry + 188, "GND (L2)", size=9.5, color=MUTED))

    # Віа-зшивка вздовж лінії
    p.append(text(rx + 240, ry + 245, "Захисний паркан перехідних отворів (Via Stitching крок ≤ 1.5 мм)", size=10, color=GND_C, bold=True))
    for i in range(11):
        p.append(circle(rx + 90 + i * 28, ry + 40, 3.5, fill="#f6ecd6", stroke=GND_C, sw=1.5))
        p.append(circle(rx + 90 + i * 28, ry + 215, 3.5, fill="#f6ecd6", stroke=GND_C, sw=1.5))

    # Пояснення знизу
    p.append(rect(50, 350, 820, 115, fill="#fcfcfb", stroke="#e0e0e0", sw=1.2, rx=6))
    p.append(text(70, 375, "Критичні правила трасування RF:", size=11, bold=True, color=INK, anchor="start"))
    p.append(text(70, 400, "• Жодних прямих кутів 90° (лише дуги або скоси 45° зі зрізом chamfer).", size=10.5, color=INK, anchor="start"))
    p.append(text(70, 422, "• Суцільний шар GND під лінією на L2 без розрізів, перетинів і сигнальних трас.", size=10.5, color=INK, anchor="start"))
    p.append(text(70, 444, "• Виріз міді (Keep-out) на опорному шарі L2 під контактними площадками пасивних SMD 0402.", size=10.5, color=INK, anchor="start"))

    return render(os.path.join(OUT, "rf-microstrip-matching.svg"), W, H, *p, title=None)


# ── 4. Схемотехніка USIM-інтерфейсу та ESD-захист ──────────────────────────────
def fig_usim_protection():
    W, H = 920, 460
    p = []

    p.append(text(W / 2, 28, "Схемотехнічний захист інтерфейсу USIM-карти від статичної електрики (ESD)", size=16, bold=True))
    p.append(text(W / 2, 50, "Багатоканальний TVS-масив (C_esd < 10 пФ) розміщується безпосередньо біля контактів слота", size=11, color=MUTED))

    # Блок модема зліва
    mx, my = 120, 230
    b_modem, _, _ = textbox(mx, my, "Модем\n(USIM контролер)\n1.8 В / 3.0 В\nЧутливий до >15 В",
                            size=10.5, bold=True, fill="#eaf0fd", stroke=COOL, pad=8)
    p.append(b_modem)

    # Слот SIM-карти справа
    sx, sy = 790, 230
    b_slot, _, _ = textbox(sx, sy, "Слот SIM-карти\n(зовнішній інтерфейс)\nIEC 61000-4-2\nESD до 15 кВ!",
                           size=10.5, bold=True, fill="#fdecea", stroke=POS, pad=8)
    p.append(b_slot)

    # Лінії інтерфейсу
    lines_info = [
        (130, "USIM_VDD", COOL, "100 нФ + 33 пФ до GND"),
        (180, "USIM_RST", INK, "22 пФ до GND"),
        (230, "USIM_CLK", INK, "22 пФ до GND (3.25 МГц)"),
        (280, "USIM_DATA", INK, "4.7 кОм Pull-Up + 22 пФ"),
        (330, "USIM_DET", MUTED, "Детекція картки")
    ]

    for ly, name, col, note in lines_info:
        p.append(line(200, ly, 700, ly, color=col, sw=1.8))
        p.append(text(250, ly - 8, name, size=10, color=col, bold=True))
        p.append(text(600, ly - 8, note, size=9.5, color=MUTED))

    # TVS масив по центру
    tx = 440
    p.append(rect(tx - 35, 105, 70, 250, fill="#ffffff", stroke=POS, sw=2, rx=4))
    p.append(text(tx, 90, "TVS Array (< 2 мм від слота)", size=10.5, color=POS, bold=True))
    p.append(text(tx, 375, "C_esd < 10 пФ, V_clamp < 8 В", size=10, color=POS))

    for ly, _, _, _ in lines_info:
        p.append(circle(tx, ly, 3.5, fill=POS, stroke=POS, sw=0))
        p.append(line(tx, ly, tx, ly + 14, color=POS, sw=1.2))
        p.append(line(tx - 8, ly + 14, tx + 8, ly + 14, color=POS, sw=1.5))
        p.append(line(tx - 8, ly + 14, tx - 10, ly + 18, color=POS, sw=1.2))
        p.append(line(tx + 8, ly + 14, tx + 10, ly + 10, color=POS, sw=1.2))

    # Земля TVS масиву
    p.append(line(tx, 355, tx, 405, color=GND_C, sw=2.5))
    p.append(circle(tx, 405, 4, fill=GND_C, stroke=GND_C, sw=0))
    p.append(text(tx + 12, 409, "GND (віа на суцільний полігон)", size=10, color=GND_C, anchor="start", bold=True))

    # Стрілка розряду ESD від слота
    p.append(arrow(730, 80, 490, 80, color=POS, sw=2))
    p.append(text(610, 70, "Струм ESD скидається в GND", size=10, color=POS, bold=True))

    return render(os.path.join(OUT, "usim-protection-schematic.svg"), W, H, *p, title=None)


# ── 5. Часова послідовність цифрового керування модемом ────────────────────────
def fig_control_timing():
    W, H = 940, 480
    ox = 130
    p = []

    p.append(text(W / 2, 28, "Часова діаграма сигналів цифрового керування модемом", size=16, bold=True))
    p.append(text(W / 2, 50, "Послідовність увімкнення (PWRKEY), готовність (STATUS), перехід у сон (DTR) та пробудження (RI)", size=11, color=MUTED))

    signals = [
        ("VBAT", 90, [(0, 1), (700, 1)], COOL, "Живлення 3.8 В"),
        ("PWRKEY", 150, [(0, 0), (60, 0), (60, -1), (180, -1), (180, 0), (700, 0)], POS, "Імпульс увімкнення (0.5–1.0 с, Open-Drain)"),
        ("STATUS", 210, [(0, -1), (320, -1), (320, 1), (700, 1)], GND_C, "Готовність ядра (HIGH = модуль активний)"),
        ("DTR", 270, [(0, -1), (420, -1), (420, 1), (580, 1), (580, -1), (700, -1)], INK, "Сон (HIGH = Sleep Mode, LOW = Active)"),
        ("RI", 330, [(0, 1), (620, 1), (620, -1), (660, -1), (660, 1), (700, 1)], HOT, "Ring Indicator (переривання пробудження МК)")
    ]

    for name, sy, waveform, col, desc in signals:
        p.append(text(ox - 15, sy + 5, name, size=11, bold=True, color=col, anchor="end"))
        p.append(text(ox + 460, sy - 18, desc, size=9.5, color=MUTED, anchor="start"))
        p.append(line(ox, sy + 15, ox + 680, sy + 15, color="#f0f0f0", sw=1))

        pts = []
        for dt, state in waveform:
            vy = sy - 12 if state >= 0 else sy + 12
            pts.append((ox + dt, vy))

        p_str = " ".join("%.1f,%.1f" % pt for pt in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (p_str, col))

    # Часові маркери
    # t_pwrkey
    p.append(line(ox + 60, 125, ox + 60, 175, color=MUTED, sw=1, dash="2,2"))
    p.append(line(ox + 180, 125, ox + 180, 175, color=MUTED, sw=1, dash="2,2"))
    p.append(text(ox + 120, 185, "t_pwrkey ≈ 1.0 с", size=9.5, color=POS, bold=True))

    # t_boot
    p.append(line(ox + 180, 185, ox + 180, 235, color=MUTED, sw=1, dash="2,2"))
    p.append(line(ox + 320, 185, ox + 320, 235, color=MUTED, sw=1, dash="2,2"))
    p.append(text(ox + 250, 245, "t_boot ≈ 2–5 с", size=9.5, color=GND_C, bold=True))

    # t_sleep
    p.append(text(ox + 500, 305, "eDRX / PSM (струм < 1 мА)", size=9.5, color=INK))

    # t_ri
    p.append(line(ox + 620, 305, ox + 620, 355, color=MUTED, sw=1, dash="2,2"))
    p.append(line(ox + 660, 305, ox + 660, 355, color=MUTED, sw=1, dash="2,2"))
    p.append(text(ox + 640, 365, "120 мс", size=9.5, color=HOT, bold=True))

    # Вісь часу знизу
    p.append(arrow(ox, 410, ox + 690, 410, color=LINE, sw=1.5))
    p.append(text(ox + 705, 414, "Час", size=11, color=LINE, anchor="start"))

    return render(os.path.join(OUT, "digital-control-timing.svg"), W, H, *p, title=None)


if __name__ == "__main__":
    fig_power_burst()
    fig_power_delivery()
    fig_rf_layout()
    fig_usim_protection()
    fig_control_timing()
    print("All figures generated successfully.")
