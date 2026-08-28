# -*- coding: utf-8 -*-
import sys, os
import math

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_gnss_vs_imu_characteristics():
    """Порівняння спектральної та часової поведінки IMU та GNSS: накопичення похибок та комплементарність."""
    W, H = 840, 360
    p = []

    # Заголовок
    p.append(text(W / 2, 28, "Взаємодоповнюваність GNSS та ІВБ: часовий дрейф і частотний спектр", size=15, bold=True))

    # Панель 1: Накопичення похибки позиції з часом
    cx1, cy1 = 220, 190
    p.append(rect(20, 55, 385, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(cx1, 80, "Накопичення просторової похибки", size=13, bold=True, color=INK))
    p.append(text(cx1, 98, "Дрейф інтегрування IMU проти обмеженого шуму GNSS", size=11, color=MUTED))

    # Осі графіка 1
    gx0, gy0 = 65, 290
    gw, gh = 310, 160
    p.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=1.2))
    p.append(line(gx0, gy0, gx0, gy0 - gh, color=LINE, sw=1.2))
    p.append(text(gx0 + gw - 15, gy0 + 18, "Час t", size=11, color=MUTED))
    p.append(text(gx0 - 15, gy0 - gh + 15, "Похибка Δp", size=11, color=MUTED, anchor="end"))

    # Крива IMU (кубічне / квадратичне зростання похибки)
    imu_pts = []
    for i in range(40):
        t_val = i / 39.0
        px = gx0 + t_val * (gw - 30)
        # y зростає нелінійно
        py = gy0 - (t_val ** 2.3) * (gh - 20)
        imu_pts.append("%.1f,%.1f" % (px, py))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(imu_pts), POS))
    p.append(text(gx0 + 140, gy0 - 125, "ІВБ (чиста інерція): ~ t²...t³", size=11, bold=True, color=POS))

    # Смуга шуму GNSS (константне коливання біля істини)
    gnss_pts = []
    for i in range(40):
        t_val = i / 39.0
        px = gx0 + t_val * (gw - 30)
        noise = math.sin(i * 1.7) * 9 + math.cos(i * 3.1) * 6
        py = gy0 - 45 + noise
        gnss_pts.append("%.1f,%.1f" % (px, py))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,2"/>' % (" ".join(gnss_pts), NEG))
    p.append(text(gx0 + 195, gy0 - 62, "GNSS: обмежений шум (2–3 м)", size=11, bold=True, color=NEG))

    # Крива Fusion (EKF)
    fusion_pts = []
    for i in range(40):
        t_val = i / 39.0
        px = gx0 + t_val * (gw - 30)
        noise = math.sin(i * 1.7) * 2.5
        py = gy0 - 45 + noise
        fusion_pts.append("%.1f,%.1f" % (px, py))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(fusion_pts), FIELD))
    p.append(text(gx0 + 185, gy0 - 25, "Комплекс GNSS+ІВБ: висока гладкість і 0 дрейфу", size=11, bold=True, color=FIELD))

    # Панель 2: Частотний спектр і комплементарність
    cx2, cy2 = 625, 190
    p.append(rect(425, 55, 395, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(cx2, 80, "Частотний спектр та взаємодія", size=13, bold=True, color=INK))
    p.append(text(cx2, 98, "Розподіл смуг достовірності вимірювальних каналів", size=11, color=MUTED))

    # Блоки сенсорів
    p.append(fitbox(445, 120, 165, 80, "ІВБ (IMU)\n100–1000 Гц\nВисокі частоти (HPF)\nШвидка динаміка", size=11, fill="#fee2e2", stroke=POS))
    p.append(fitbox(635, 120, 165, 80, "GNSS (Супутники)\n5–20 Гц\nНизькі частоти (LPF)\nАбсолютна прив'язка", size=11, fill="#e0e7ff", stroke=NEG))

    # Стрілки злиття
    p.append(arrow(527, 205, 595, 240, color=POS, sw=2.0))
    p.append(arrow(717, 205, 655, 240, color=NEG, sw=2.0))

    # Центральний блок фільтрації
    p.append(fitbox(495, 245, 260, 75, "Розширений фільтр Калмана (EKF)\nОцінка [p, v, q] + дрейфи (bias)\nЧастота виходу: 250–400 Гц", size=11, bold=True, fill="#dcfce7", stroke=FIELD))

    render(os.path.join(OUT, "gnss-vs-imu-characteristics.svg"), W, H, *p)


def fig_loose_vs_tight_coupling():
    """Архітектури комплексування: Loosely Coupled, Tightly Coupled, Deeply Coupled."""
    W, H = 840, 420
    p = []

    # Заголовок
    p.append(text(W / 2, 26, "Архітектури комплексування супутникових та інерціальних вимірювань", size=15, bold=True))

    # 1. Loosely Coupled
    p.append(rect(20, 50, 800, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(95, 75, "Слабкозв'язана (Loose)", size=12, bold=True, color=INK))
    p.append(text(95, 93, "≥ 4 супутники (PVT)", size=10, color=MUTED))

    p.append(fitbox(180, 65, 130, 45, "GNSS Антена +\nКорелятор", size=10, fill="#f1f5f9", stroke=LINE))
    p.append(arrow(310, 87, 345, 87, color=LINE, sw=1.5))
    p.append(fitbox(345, 65, 135, 45, "Внутрішній PVT\nприймача (5 Гц)", size=10, fill="#e0e7ff", stroke=NEG))
    p.append(arrow(480, 87, 520, 87, color=NEG, sw=1.8))
    p.append(text(500, 78, "p, v", size=10, bold=True, color=NEG))

    p.append(fitbox(520, 60, 155, 85, "Бортовий EKF\n(15 станів: p, v, q, ba, bg)\nВисока частота", size=10, bold=True, fill="#dcfce7", stroke=FIELD))

    p.append(fitbox(345, 115, 135, 30, "IMU (250–1000 Гц)", size=10, fill="#fee2e2", stroke=POS))
    p.append(arrow(480, 130, 520, 115, color=POS, sw=1.5))

    p.append(arrow(675, 95, 715, 95, color=FIELD, sw=1.8))
    p.append(fitbox(715, 72, 95, 45, "Навігація\n[p, v, q]", size=10, bold=True, fill="#f8fafc", stroke=LINE))

    # 2. Tightly Coupled
    p.append(rect(20, 165, 800, 115, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(95, 195, "Сильнозв'язана (Tight)", size=12, bold=True, color=INK))
    p.append(text(95, 213, "Працює при 1–3 супутниках", size=10, color=MUTED))

    p.append(fitbox(180, 185, 130, 45, "GNSS Антена +\nКорелятор", size=10, fill="#f1f5f9", stroke=LINE))
    p.append(arrow(310, 207, 360, 207, color=NEG, sw=1.8))
    p.append(text(335, 198, "ρ, ρ̇", size=11, bold=True, color=NEG))

    p.append(fitbox(360, 180, 130, 55, "Сирі виміри:\nпсевдодальність ρ,\nдоплер ρ̇ кожної SV", size=9.5, fill="#e0e7ff", stroke=NEG))
    p.append(arrow(490, 207, 520, 207, color=NEG, sw=1.8))

    p.append(fitbox(520, 175, 155, 95, "Бортовий TC-EKF\n(17 станів: + δt_rx, δṫ_rx)\nПряма нев'язка променів", size=9.5, bold=True, fill="#dcfce7", stroke=FIELD))

    p.append(fitbox(360, 245, 130, 28, "IMU (250–1000 Гц)", size=10, fill="#fee2e2", stroke=POS))
    p.append(arrow(490, 259, 520, 240, color=POS, sw=1.5))

    p.append(arrow(675, 215, 715, 215, color=FIELD, sw=1.8))
    p.append(fitbox(715, 192, 95, 45, "Навігація\n[p, v, q]", size=10, bold=True, fill="#f8fafc", stroke=LINE))

    # 3. Deeply Coupled
    p.append(rect(20, 290, 800, 115, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(95, 320, "Глибокозв'язана (Deep)", size=12, bold=True, color=INK))
    p.append(text(95, 338, "Екстремальне REB / РЕБ", size=10, color=MUTED))

    p.append(fitbox(180, 310, 130, 45, "GNSS Антена +\nI/Q семпли ВЧ", size=10, fill="#f1f5f9", stroke=LINE))
    p.append(arrow(310, 332, 360, 332, color=LINE, sw=1.5))

    p.append(fitbox(360, 310, 130, 45, "Банк цифрових\nкореляторів NCO", size=10, fill="#e0e7ff", stroke=NEG))
    p.append(arrow(490, 332, 520, 332, color=NEG, sw=1.8))

    p.append(fitbox(520, 300, 155, 95, "Єдиний навігаційно-\nслідкуючий EKF\nПряме керування NCO", size=9.5, bold=True, fill="#dcfce7", stroke=FIELD))

    # Зворотний зв'язок на корелятори
    p.append(arrow(520, 375, 425, 375, color="#d97706", sw=1.8))
    p.append(arrow(425, 375, 425, 355, color="#d97706", sw=1.8))
    p.append(text(475, 390, "Допомога стеженню (NCO feedback)", size=9, bold=True, color="#d97706"))

    p.append(arrow(675, 340, 715, 340, color=FIELD, sw=1.8))
    p.append(fitbox(715, 317, 95, 45, "Навігація\n[p, v, q]", size=10, bold=True, fill="#f8fafc", stroke=LINE))

    render(os.path.join(OUT, "loose-vs-tight-coupling.svg"), W, H, *p)


def fig_delayed_fusion_ring_buffer():
    """Кільцевий буфер часового узгодження вимірювань (Time-Delayed Measurement Fusion)."""
    W, H = 840, 380
    p = []

    # Заголовок
    p.append(text(W / 2, 26, "Часове узгодження в EKF: ретроспективне злиття затриманих даних GNSS", size=15, bold=True))

    # Вісь часу
    gx0, gy0 = 50, 120
    gw = 740
    p.append(line(gx0, gy0, gx0 + gw, gy0, color=LINE, sw=2.0))
    p.append(arrow(gx0 + gw - 30, gy0, gx0 + gw, gy0, color=LINE, sw=2.0))
    p.append(text(gx0 + gw, gy0 + 20, "Час (Time)", size=12, bold=True, color=MUTED, anchor="end"))

    # Часові позначки
    t_meas_x = 260
    t_now_x = 680

    p.append(line(t_meas_x, gy0 - 45, t_meas_x, gy0 + 75, color=NEG, sw=1.5, dash="3,3"))
    p.append(circle(t_meas_x, gy0, 5.0, fill=NEG, stroke=NEG))
    p.append(text(t_meas_x, gy0 - 55, "t_meas (Момент спостереження)", size=11, bold=True, color=NEG))
    p.append(text(t_meas_x, gy0 - 70, "Фізичний прихід сигналу на антену", size=9.5, color=MUTED))

    p.append(line(t_now_x, gy0 - 45, t_now_x, gy0 + 75, color=POS, sw=1.5, dash="3,3"))
    p.append(circle(t_now_x, gy0, 5.0, fill=POS, stroke=POS))
    p.append(text(t_now_x, gy0 - 55, "t_now (Поточний такт)", size=11, bold=True, color=POS))
    p.append(text(t_now_x, gy0 - 70, "Прихід UBX-пакета через UART", size=9.5, color=MUTED))

    # Затримка (Latency)
    p.append(line(t_meas_x, gy0 - 25, t_now_x, gy0 - 25, color=MUTED, sw=1.2))
    p.append(arrow(t_meas_x + 15, gy0 - 25, t_meas_x, gy0 - 25, color=MUTED, sw=1.2))
    p.append(arrow(t_now_x - 15, gy0 - 25, t_now_x, gy0 - 25, color=MUTED, sw=1.2))
    p.append(text((t_meas_x + t_now_x) / 2, gy0 - 32, "Затримка передачі та обчислень Δt_delay ≈ 150–250 мс", size=10.5, bold=True, color=MUTED))

    # Кільцевий буфер вибірок IMU
    p.append(rect(40, 160, 760, 95, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(145, 185, "Кільцевий буфер станів / IMU (Ring Buffer)", size=12, bold=True, color=INK))
    p.append(text(145, 202, "Глибина буфера: 250 кадрів (1 секунда)", size=10, color=MUTED))

    # Клітинки буфера
    slot_w, slot_h = 36, 42
    start_bx = 230
    for idx in range(13):
        bx = start_bx + idx * 42
        by = 175
        is_target = (idx == 1)
        is_current = (idx == 11)
        bg_col = "#e0e7ff" if is_target else ("#fee2e2" if is_current else "#f1f5f9")
        st_col = NEG if is_target else (POS if is_current else "#cbd5e1")
        p.append(rect(bx, by, slot_w, slot_h, fill=bg_col, stroke=st_col, sw=1.5 if (is_target or is_current) else 1.0, rx=4))
        lbl = "t_m" if is_target else ("t_now" if is_current else f"k-{11-idx}")
        p.append(text(bx + slot_w / 2, by + 25, lbl, size=9.5, bold=(is_target or is_current), color=INK))

    # Пояснення кроків алгоритму внизу
    p.append(fitbox(40, 275, 235, 85, "1. Зіставлення в часі\nПошук кадру x̂(t_meas) у буфері\nта інтерполяція стану\nдо мітки вимірювання", size=10, fill="#f8fafc", stroke=LINE))
    p.append(fitbox(295, 275, 245, 85, "2. Інновація та гейтинг\ny = z_gnss − H · x̂(t_meas)\nМахаланобіс: yᵀ S⁻¹ y ≤ γ²\nЗахист від мультишляховості", size=10, fill="#f8fafc", stroke=LINE))
    p.append(fitbox(560, 275, 240, 85, "3. Корекція та ретроспектива\nОбчислення поправки δx = K · y\nНакочування поправки до t_now\n(Error-State Feedback)", size=10, bold=True, fill="#dcfce7", stroke=FIELD))

    p.append(arrow(275, 317, 295, 317, color=LINE, sw=1.5))
    p.append(arrow(540, 317, 560, 317, color=LINE, sw=1.5))

    render(os.path.join(OUT, "delayed-fusion-ring-buffer.svg"), W, H, *p)


def fig_in_flight_bias_observability():
    """Геометрія спостережуваності зміщення нуля давачів (Bias Observability) під час маневрів."""
    W, H = 840, 360
    p = []

    # Заголовок
    p.append(text(W / 2, 26, "Спостережуваність зміщень ІВБ (Bias Observability): статика проти маневру", size=15, bold=True))

    # Панель 1: Статика (Зависання)
    p.append(rect(20, 50, 385, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(212, 75, "1. Статичне зависання: невизначеність", size=12, bold=True, color=INK))
    p.append(text(212, 93, "Зміщення b_a_z невіддільне від гравітації g", size=10.5, color=MUTED))

    # Схема дрона в статиці
    p.append(line(130, 160, 290, 160, color=LINE, sw=3.0)) # Рама
    p.append(circle(130, 155, 12, fill="#e2e8f0", stroke=LINE))
    p.append(circle(290, 155, 12, fill="#e2e8f0", stroke=LINE))
    p.append(rect(190, 145, 44, 30, fill="#fee2e2", stroke=POS, rx=4))
    p.append(text(212, 163, "IMU", size=10, bold=True, color=POS))

    # Вектори
    p.append(arrow(212, 175, 212, 240, color=LINE, sw=2.0))
    p.append(text(225, 215, "g (9.81 м/с²)", size=10.5, bold=True, color=LINE))

    p.append(arrow(202, 175, 202, 210, color=POS, sw=1.5))
    p.append(text(150, 195, "b_a_z (зсув)", size=10, bold=True, color=POS))

    p.append(fitbox(35, 250, 355, 75, "Рівняння виміру: a_z = g + b_a_z\nGNSS бачить v = 0, p = const.\nНеможливо розділити: чи це g = 9.81, чи це b_a_z ≠ 0.\nЗміщення вертикальної осі НЕ спостережуване!", size=10, fill="#fee2e2", stroke=POS))

    # Панель 2: Динамічний маневр (Розгін / Віраж)
    p.append(rect(425, 50, 395, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(622, 75, "2. Динамічний маневр: повна спостережуваність", size=12, bold=True, color=INK))
    p.append(text(622, 93, "Зміна орієнтації та прискорення розкривають зміщення", size=10.5, color=MUTED))

    # Схема нахиленого дрона
    cx_d, cy_d = 620, 160
    ang = math.radians(-22)
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    l_arm = 80
    p.append(line(cx_d - l_arm * cos_a, cy_d - l_arm * sin_a, cx_d + l_arm * cos_a, cy_d + l_arm * sin_a, color=LINE, sw=3.0))
    p.append(circle(cx_d - l_arm * cos_a, cy_d - l_arm * sin_a - 5, 12, fill="#e2e8f0", stroke=LINE))
    p.append(circle(cx_d + l_arm * cos_a, cy_d + l_arm * sin_a - 5, 12, fill="#e2e8f0", stroke=LINE))
    p.append(rect(cx_d - 22, cy_d - 15, 44, 30, fill="#dcfce7", stroke=FIELD, rx=4))
    p.append(text(cx_d, cy_d + 3, "IMU", size=10, bold=True, color=FIELD))

    # Вектор тяги / прискорення
    p.append(arrow(cx_d, cy_d - 15, cx_d + 55, cy_d - 45, color=FIELD, sw=2.0))
    p.append(text(cx_d + 65, cy_d - 50, "a_kin (рух)", size=10, bold=True, color=FIELD))

    # Вектор GNSS швидкості
    p.append(arrow(cx_d + 30, cy_d + 30, cx_d + 110, cy_d + 30, color=NEG, sw=2.0))
    p.append(text(cx_d + 75, cy_d + 45, "v_gnss (росте)", size=10, bold=True, color=NEG))

    p.append(fitbox(440, 250, 365, 75, "Прискорення створює крос-кореляцію в EKF:\n1) GNSS дає істинну похідну швидкості dv/dt;\n2) IMU вимірює R(q)ᵀ · (a + g) + b_a;\n3) Маневр розділяє кутову похибку δθ та зміщення b_a!", size=10, bold=True, fill="#dcfce7", stroke=FIELD))

    render(os.path.join(OUT, "in-flight-bias-observability.svg"), W, H, *p)


if __name__ == "__main__":
    fig_gnss_vs_imu_characteristics()
    fig_loose_vs_tight_coupling()
    fig_delayed_fusion_ring_buffer()
    fig_in_flight_bias_observability()
    print("Figures generated successfully.")
