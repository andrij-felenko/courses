# -*- coding: utf-8 -*-
"""Фігури до теми «LTE-M і NB-IoT».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER  = "#b9770e"    # бурштиновий: таймери / проміжні стани
PURPLE = "#7c3aed"    # фіолетовий: LTE-M / протокольні структури
CYAN   = "#0891b2"    # бірюзовий: NB-IoT / радіоканали


# ── 1. Спектральне розміщення NB-IoT та LTE-M ─────────────────────────────────
def fig_spectrum_allocation():
    W, H = 880, 480
    elements = []

    # Заголовок блоків
    elements.append(text(W / 2, 25, "Спектральне розміщення каналів NB-IoT та смуги LTE-M", size=15, bold=True))

    # Верхній блок: Режими розгортання NB-IoT (180 кГц = 1 PRB)
    y_nb = 55
    elements.append(rect(20, y_nb, 840, 195, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=8))
    elements.append(text(40, y_nb + 22, "Три режими розгортання NB-IoT (смуга 180 кГц = 1 PRB LTE):", size=12, color=INK, bold=True, anchor="start"))

    # 1.1 Standalone
    x1, y1 = 40, y_nb + 40
    elements.append(rect(x1, y1, 240, 135, fill="#ecfeff", stroke=CYAN, sw=1.5, rx=6))
    elements.append(text(x1 + 120, y1 + 22, "1. Автономний (Standalone)", size=11, color=CYAN, bold=True))
    elements.append(rect(x1 + 20, y1 + 40, 200, 40, fill="#cffafe", stroke=CYAN, sw=1.2, rx=4))
    elements.append(text(x1 + 120, y1 + 62, "GSM 200 кГц (Refarming)", size=10.5, color=INK, bold=True))
    elements.append(rect(x1 + 35, y1 + 45, 170, 30, fill="#0891b2", stroke="#0e7490", sw=1.0, rx=3))
    elements.append(text(x1 + 120, y1 + 64, "NB-IoT 180 кГц", size=10, color="#ffffff", bold=True))
    elements.append(mtext(x1 + 120, y1 + 96, "Окремий канал 200 кГц\nпоза спектром LTE (2G/3G)", size=9.5, color=MUTED, lh=1.2))

    # 1.2 Guard-Band
    x2 = 320
    elements.append(rect(x2, y1, 240, 135, fill="#f5f3ff", stroke=PURPLE, sw=1.5, rx=6))
    elements.append(text(x2 + 120, y1 + 22, "2. Захисна смуга (Guard-Band)", size=11, color=PURPLE, bold=True))
    elements.append(rect(x2 + 15, y1 + 40, 80, 40, fill="#e2e8f0", stroke=MUTED, sw=1.0, rx=3))
    elements.append(text(x2 + 55, y1 + 64, "LTE несуча", size=9.5, color=MUTED))
    elements.append(rect(x2 + 100, y1 + 42, 60, 36, fill="#7c3aed", stroke="#6d28d9", sw=1.0, rx=3))
    elements.append(text(x2 + 130, y1 + 64, "180 кГц", size=9.5, color="#ffffff", bold=True))
    elements.append(rect(x2 + 165, y1 + 40, 60, 40, fill="#f1f5f9", stroke=MUTED, sw=1.0, rx=3))
    elements.append(text(x2 + 195, y1 + 64, "Захист", size=9.5, color=MUTED))
    elements.append(mtext(x2 + 120, y1 + 96, "У невикористаній захисній\nсмузі LTE-носія (≥10 МГц)", size=9.5, color=MUTED, lh=1.2))

    # 1.3 In-Band
    x3 = 600
    elements.append(rect(x3, y1, 240, 135, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    elements.append(text(x3 + 120, y1 + 22, "3. Усередині смуги (In-Band)", size=11, color=FIELD, bold=True))
    elements.append(rect(x3 + 15, y1 + 40, 210, 40, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=4))
    elements.append(rect(x3 + 85, y1 + 42, 70, 36, fill="#16a34a", stroke="#15803d", sw=1.0, rx=3))
    elements.append(text(x3 + 120, y1 + 64, "1 PRB IoT", size=9.5, color="#ffffff", bold=True))
    elements.append(text(x3 + 50, y1 + 64, "PRB LTE", size=9.5, color=MUTED))
    elements.append(text(x3 + 190, y1 + 64, "PRB LTE", size=9.5, color=MUTED))
    elements.append(mtext(x3 + 120, y1 + 96, "Виділення 1 PRB (180 кГц)\nіз проколюванням CRS LTE", size=9.5, color=MUTED, lh=1.2))

    # Нижній блок: LTE-M (eMTC) — 1.4 МГц (6 PRBs)
    y_m = 265
    elements.append(rect(20, y_m, 840, 195, fill="#fdf4ff", stroke=PURPLE, sw=1.2, rx=8))
    elements.append(text(40, y_m + 24, "Смуга LTE-M (eMTC / Cat-M1) — 1.4 МГц (6 PRB) у широкосмуговому LTE-каналі:", size=12, color=PURPLE, bold=True, anchor="start"))

    # Широка несуча LTE 20 МГц (100 PRB)
    x_lte = 40
    w_lte = 800
    elements.append(rect(x_lte, y_m + 48, w_lte, 65, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    elements.append(text(x_lte + 100, y_m + 68, "Широкосмуговий канал LTE (5 / 10 / 20 МГц — до 100 PRB)", size=10.5, color=MUTED, anchor="start"))

    # Вузкосмугові блоки (Narrowbands) по 6 PRB
    for i, nb_x in enumerate([80, 240, 480, 680]):
        is_active = (i == 1)
        col = PURPLE if is_active else "#94a3b8"
        bg = "#ddd6fe" if is_active else "#f8fafc"
        elements.append(rect(nb_x, y_m + 78, 120, 30, fill=bg, stroke=col, sw=1.5 if is_active else 1.0, rx=4))
        lbl = "Вузькосмуга #%d (6 PRB)" % (i + 1)
        elements.append(text(nb_x + 60, y_m + 97, lbl, size=9.5, color=col, bold=is_active))

    # Стрілки стрибків частоти (Frequency Hopping)
    elements.append(arrow(200, y_m + 93, 235, y_m + 93, color=PURPLE, sw=1.5))
    elements.append(arrow(365, y_m + 93, 475, y_m + 93, color=PURPLE, sw=1.5))
    elements.append(arrow(605, y_m + 93, 675, y_m + 93, color=PURPLE, sw=1.5))

    elements.append(mtext(W / 2, y_m + 138,
                          "LTE-M оперує вузькою смугою 1.4 МГц (6 ресурсних блоків PRB = 1.08 МГц даних + захисні інтервали),\n"
                          "виконуючи динамічний стрибок частоти (Frequency Hopping) між різними ділянками широкого спектра LTE.",
                          size=10, color=INK, anchor="middle", lh=1.3))

    return render(os.path.join(IMG, "lte-m-vs-nb-iot-spectrum.svg"), W, H, *elements)


# ── 2. Часова діаграма станів та таймерів PSM і eDRX ───────────────────────────
def fig_psm_edrx_timeline():
    W, H = 880, 440
    elements = []

    elements.append(text(W / 2, 24, "Часова діаграма станів модема та таймерів PSM і eDRX", size=15, bold=True))

    # Часова вісь
    y_axis = 160
    elements.append(line(40, y_axis, 840, y_axis, color=LINE, sw=2.0))
    elements.append(arrow(830, y_axis, 845, y_axis, color=LINE, sw=2.0))
    elements.append(text(840, y_axis + 18, "Час t", size=11, color=MUTED))

    # Стан 1: RRC Connected (Передача даних)
    x_conn = 50
    w_conn = 120
    elements.append(rect(x_conn, y_axis - 70, w_conn, 70, fill="#fee2e2", stroke=POS, sw=1.8, rx=4))
    elements.append(text(x_conn + w_conn / 2, y_axis - 45, "RRC Connected", size=11, color=POS, bold=True))
    elements.append(text(x_conn + w_conn / 2, y_axis - 25, "Tx/Rx (100–350 мА)", size=9.5, color=POS))

    # Стан 2: RRC Inactivity Timer (Очікування вивільнення мережею)
    x_inact = x_conn + w_conn
    w_inact = 90
    elements.append(rect(x_inact, y_axis - 45, w_inact, 45, fill="#ffedd5", stroke=AMBER, sw=1.5, rx=4))
    elements.append(text(x_inact + w_inact / 2, y_axis - 28, "RRC Inactivity", size=10, color=AMBER, bold=True))
    elements.append(text(x_inact + w_inact / 2, y_axis - 12, "C-DRX (10–20 мА)", size=9, color=AMBER))

    # Момент RRC Release
    elements.append(line(x_inact + w_inact, y_axis - 80, x_inact + w_inact, y_axis + 30, color=MUTED, sw=1.0, dash="3,3"))
    elements.append(text(x_inact + w_inact, y_axis + 42, "RRC Release", size=9.5, color=MUTED))

    # Стан 3: Active Timer T3324 (RRC Idle з eDRX)
    x_t3324 = x_inact + w_inact
    w_t3324 = 250
    elements.append(rect(x_t3324, y_axis - 35, w_t3324, 35, fill="#f3e8ff", stroke=PURPLE, sw=1.5, rx=4))
    elements.append(text(x_t3324 + w_t3324 / 2, y_axis - 18, "RRC Idle з розширеним eDRX (періодичний моніторинг пейджингу)", size=9.5, color=PURPLE, bold=True))

    # Пульсації пейджингу всередині eDRX (PTW)
    for ptw_x in [x_t3324 + 30, x_t3324 + 100, x_t3324 + 170]:
        elements.append(rect(ptw_x, y_axis - 55, 34, 20, fill="#c084fc", stroke=PURPLE, sw=1.0, rx=2))
        elements.append(text(ptw_x + 17, y_axis - 41, "PTW", size=9, color="#ffffff", bold=True))
        elements.append(line(ptw_x + 17, y_axis - 35, ptw_x + 17, y_axis - 20, color=PURPLE, sw=1.0))

    # Стан 4: PSM Deep Sleep
    x_psm = x_t3324 + w_t3324
    w_psm = 260
    elements.append(rect(x_psm, y_axis - 12, w_psm, 12, fill="#ecfdf5", stroke=FIELD, sw=1.5, rx=3))
    elements.append(text(x_psm + w_psm / 2, y_axis - 24, "Глибокий сон PSM (< 5 мкА, радіотракт вимкнено)", size=10, color=FIELD, bold=True))

    # Наступне пробудження (Periodic TAU)
    x_wake = x_psm + w_psm
    elements.append(rect(x_wake, y_axis - 60, 45, 60, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    elements.append(text(x_wake + 22, y_axis - 28, "TAU", size=9.5, color=POS, bold=True))

    # Дужки і розмітки таймерів (знизу осі)
    y_timer = 235

    # Дужка Active Timer T3324
    elements.append(line(x_t3324, y_timer, x_t3324 + w_t3324, y_timer, color=PURPLE, sw=2.0))
    elements.append(line(x_t3324, y_timer - 6, x_t3324, y_timer + 6, color=PURPLE, sw=2.0))
    elements.append(line(x_t3324 + w_t3324, y_timer - 6, x_t3324 + w_t3324, y_timer + 6, color=PURPLE, sw=2.0))
    elements.append(text(x_t3324 + w_t3324 / 2, y_timer + 20, "Активний таймер T3324 (Active Time: від 2 с до 18.6 год)", size=10.5, color=PURPLE, bold=True))
    elements.append(text(x_t3324 + w_t3324 / 2, y_timer + 36, "Приймач слухає пейджинг у вікнах PTW; пристрій досяжний з мережі", size=9.5, color=MUTED))

    # Дужка Periodic TAU Timer T3412 (повний цикл)
    y_tau = 310
    elements.append(line(x_t3324, y_tau, x_wake, y_tau, color=CYAN, sw=2.0))
    elements.append(line(x_t3324, y_tau - 6, x_t3324, y_tau + 6, color=CYAN, sw=2.0))
    elements.append(line(x_wake, y_tau - 6, x_wake, y_tau + 6, color=CYAN, sw=2.0))
    elements.append(text((x_t3324 + x_wake) / 2, y_tau + 20, "Періодичний таймер TAU T3412 / T3412-ext (до 413 днів)", size=11, color=CYAN, bold=True))
    elements.append(text((x_t3324 + x_wake) / 2, y_tau + 38, "Модем зберігає реєстрацію в MME/HSS без потреби повторного Attach при пробудженні", size=9.5, color=MUTED))

    # Нижня плашка з підсумком
    elements.append(rect(40, 375, 800, 48, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=6))
    elements.append(mtext(W / 2, 393,
                          "PSM мінімізує струм до мікроампер під час простою, а eDRX скорочує витрати під час очікування вхідних даних.\n"
                          "Пристрій сам ініціює вихід із PSM у будь-який момент за апаратним перериванням від датчика.",
                          size=9.5, color=INK, anchor="middle", lh=1.25))

    return render(os.path.join(IMG, "psm-edrx-timeline.svg"), W, H, *elements)


# ── 3. Профіль споживання струму під час сесії передачі ────────────────────────
def fig_power_profile_session():
    W, H = 880, 450
    elements = []

    elements.append(text(W / 2, 24, "Профіль споживання струму модема під час циклу передачі телеметрії", size=15, bold=True))

    # Осі координат
    x0, y0 = 60, 360
    w_ax, h_ax = 780, 290
    elements.append(line(x0, y0, x0 + w_ax, y0, color=LINE, sw=2.0))
    elements.append(arrow(x0 + w_ax - 10, y0, x0 + w_ax + 5, y0, color=LINE, sw=2.0))
    elements.append(text(x0 + w_ax, y0 + 20, "Час (с)", size=11, color=MUTED))

    elements.append(line(x0, y0, x0, y0 - h_ax, color=LINE, sw=2.0))
    elements.append(arrow(x0, y0 - h_ax + 10, x0, y0 - h_ax - 5, color=LINE, sw=2.0))
    elements.append(text(x0 - 25, y0 - h_ax, "Струм I (мА)", size=11, color=MUTED, anchor="middle"))

    # Позначки шкали струму
    for mA, y_pos in [(300, y0 - 260), (150, y0 - 140), (50, y0 - 55), (10, y0 - 20)]:
        elements.append(line(x0 - 5, y_pos, x0 + w_ax - 20, y_pos, color="#e2e8f0", sw=1.0, dash="3,3"))
        elements.append(text(x0 - 10, y_pos + 4, str(mA), size=9.5, color=MUTED, anchor="end"))

    # Фази передачі (точки графіка)
    pts = [
        (60, y0 - 1),
        (85, y0 - 1),
        (88, y0 - 30),      # Старт MCU / UART
        (130, y0 - 30),
        (135, y0 - 90),     # Синхронізація соти (NPSS/NSSS)
        (220, y0 - 90),
        (225, y0 - 260),    # Tx Burst (23 дБм)
        (250, y0 - 240),
        (260, y0 - 270),
        (285, y0 - 260),
        (290, y0 - 65),     # Rx Downlink / ACK
        (330, y0 - 65),
        (335, y0 - 28),     # RRC Inactivity
        (480, y0 - 28),
        (485, y0 - 5),      # Idle sleep
        (540, y0 - 5),
        (545, y0 - 35),     # PTW Paging check
        (565, y0 - 35),
        (570, y0 - 5),
        (640, y0 - 5),
        (645, y0 - 35),     # PTW Paging check #2
        (665, y0 - 35),
        (670, y0 - 1),      # PSM Sleep
        (820, y0 - 1)
    ]

    # Створення полігону під кривою для заливки
    poly_pts = " ".join("%.1f,%.1f" % pt for pt in pts)
    poly_fill = "%s %.1f,%.1f %.1f,%.1f" % (poly_pts, pts[-1][0], y0, pts[0][0], y0)
    elements.append('<polygon points="%s" fill="#fee2e2" opacity="0.6"/>' % poly_fill)

    # Лінія графіка
    line_svg = ' '.join('%.1f,%.1f' % pt for pt in pts)
    elements.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (line_svg, POS))

    # Текстові мітки фаз
    elements.append(text(105, y0 - 45, "Пробудження\n(UART)", size=9, color=INK))
    elements.append(text(175, y0 - 105, "Синхронізація\nі RRC Setup", size=9.5, color=INK))
    elements.append(text(260, y0 - 285, "Uplink Tx\n(250–350 мА)", size=10, color=POS, bold=True))
    elements.append(text(310, y0 - 80, "Rx ACK", size=9, color=CYAN, bold=True))
    elements.append(text(410, y0 - 42, "RRC Inactivity (таймер базової станції ~10 с)", size=9.5, color=AMBER))
    elements.append(text(600, y0 - 50, "eDRX PTW перевірки", size=9, color=PURPLE))
    elements.append(text(740, y0 - 15, "PSM Deep Sleep (< 5 мкА)", size=9.5, color=FIELD, bold=True))

    # Нижній аналіз енергії
    elements.append(rect(60, 385, 780, 50, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=6))
    elements.append(mtext(W / 2, 402,
                          "Левова частка заряду батареї (до 80%) витрачається не на саму передачу корисних байтів (Uplink Tx),\n"
                          "а на очікування відключення від соти під час RRC Inactivity Timer та процедуру повторної синхронізації.",
                          size=9.5, color=INK, anchor="middle", lh=1.25))

    return render(os.path.join(IMG, "power-profile-session.svg"), W, H, *elements)


# ── 4. CIoT EPS Optimizations (Control Plane vs User Plane) ───────────────────
def fig_ciot_architecture():
    W, H = 880, 460
    elements = []

    elements.append(text(W / 2, 24, "Оптимізації передачі даних CIoT: Control Plane (DoNAS) проти User Plane", size=15, bold=True))

    # Ліва колонка: Control Plane (CP) CIoT Optimization (Data over NAS)
    x_cp = 40
    w_col = 385
    elements.append(rect(x_cp, 50, w_col, 340, fill="#ecfeff", stroke=CYAN, sw=1.5, rx=8))
    elements.append(text(x_cp + w_col / 2, 75, "1. Control Plane CIoT (Data over NAS)", size=12, color=CYAN, bold=True))
    elements.append(text(x_cp + w_col / 2, 92, "Пакет даних упаковано в сигнальні повідомлення NAS", size=9.5, color=MUTED))

    # Вузли CP
    nodes_cp = [
        ("Термінал (UE)", 125, FIELD),
        ("Базова станція (eNodeB)", 190, INK),
        ("Сервер керування (MME)", 255, PURPLE),
        ("SGW / SCEF (Шлюз)", 320, CYAN)
    ]
    for name, y_n, col in nodes_cp:
        elements.append(rect(x_cp + 40, y_n, 305, 36, fill="#ffffff", stroke=col, sw=1.2, rx=6))
        elements.append(text(x_cp + 192, y_n + 22, name, size=10.5, color=col, bold=True))

    # Стрілки шляху CP
    elements.append(arrow(x_cp + 192, 161, x_cp + 192, 188, color=CYAN, sw=2.0))
    elements.append(text(x_cp + 270, 178, "RRC (NAS PDU)", size=9.5, color=CYAN))

    elements.append(arrow(x_cp + 192, 226, x_cp + 192, 253, color=CYAN, sw=2.0))
    elements.append(text(x_cp + 265, 243, "S1-MME (S1-AP)", size=9.5, color=CYAN))

    elements.append(arrow(x_cp + 192, 291, x_cp + 192, 318, color=CYAN, sw=2.0))
    elements.append(text(x_cp + 275, 308, "S11 (GTP-C / T6a)", size=9.5, color=CYAN))

    # Переваги CP
    elements.append(rect(x_cp + 15, 362, w_col - 30, 22, fill="#cffafe", stroke=CYAN, sw=1.0, rx=4))
    elements.append(text(x_cp + w_col / 2, 377, "Мінімум сигналізації: без встановлення Data Radio Bearer (DRB)", size=9.5, color=CYAN, bold=True))

    # Права колонка: User Plane (UP) CIoT Optimization (Suspend / Resume)
    x_up = 455
    elements.append(rect(x_up, 50, w_col, 340, fill="#fdf4ff", stroke=PURPLE, sw=1.5, rx=8))
    elements.append(text(x_up + w_col / 2, 75, "2. User Plane CIoT (Suspend / Resume)", size=12, color=PURPLE, bold=True))
    elements.append(text(x_up + w_col / 2, 92, "Збереження контексту безпеки та відновлення RRC", size=9.5, color=MUTED))

    # Вузли UP
    nodes_up = [
        ("Термінал (UE)", 125, FIELD),
        ("Базова станція (eNodeB)", 190, INK),
        ("Сервер керування (MME)", 255, MUTED),
        ("Шлюз даних (SGW / PGW)", 320, PURPLE)
    ]
    for name, y_n, col in nodes_up:
        elements.append(rect(x_up + 40, y_n, 305, 36, fill="#ffffff", stroke=col, sw=1.2, rx=6))
        elements.append(text(x_up + 192, y_n + 22, name, size=10.5, color=col, bold=True))

    # Стрілки шляху UP
    elements.append(arrow(x_up + 192, 161, x_up + 192, 188, color=PURPLE, sw=2.0))
    elements.append(text(x_up + 285, 178, "RRC Resume (DRB)", size=9.5, color=PURPLE))

    # Прямий тунель даних від eNB до SGW
    elements.append(arrow(x_up + 120, 226, x_up + 120, 318, color=PURPLE, sw=2.0))
    elements.append(text(x_up + 185, 275, "S1-U (GTP-U трафік)", size=9.5, color=PURPLE, bold=True))

    # Сигналізація MME на фоні (пунктир)
    elements.append(line(x_up + 270, 226, x_up + 270, 253, color=MUTED, sw=1.2, dash="3,3"))
    elements.append(text(x_up + 325, 243, "Без MME", size=9, color=MUTED))

    # Переваги UP
    elements.append(rect(x_up + 15, 362, w_col - 30, 22, fill="#fae8ff", stroke=PURPLE, sw=1.0, rx=4))
    elements.append(text(x_up + w_col / 2, 377, "Висока швидкість: прямий тракт даних без навантаження на MME", size=9.5, color=PURPLE, bold=True))

    # Загальний підсумок
    elements.append(rect(40, 400, 800, 48, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=6))
    elements.append(mtext(W / 2, 418,
                          "Control Plane (DoNAS) ідеальний для поодиноких телеметричних звітів (≤ 100 байтів у NB-IoT),\n"
                          "тоді як User Plane оптимізація переважає при передачі пачок даних, оновленні прошивки (FOTA) та в LTE-M.",
                          size=9.5, color=INK, anchor="middle", lh=1.25))

    return render(os.path.join(IMG, "ciot-data-transport-plane.svg"), W, H, *elements)


if __name__ == "__main__":
    fig_spectrum_allocation()
    fig_psm_edrx_timeline()
    fig_power_profile_session()
    fig_ciot_architecture()
    print("Всі 4 фігури згенеровано у ./img/")
