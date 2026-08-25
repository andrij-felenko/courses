# -*- coding: utf-8 -*-
"""Фігури до теми «Метрики якості каналу: SNR, SINR, LQI та BER».
Запуск: python figs.py → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ACCENT = "#d35400"
BLUE = "#2980b9"
PURPLE = "#8e44ad"

# ── 1. Спектральне розділення RSSI, SNR та SINR ─────────────────────────────
def fig_snr_sinr_spectrum():
    W, H = 760, 380
    f = []

    f.append(text(W / 2, 28, "Спектральний склад сигналу та різниця між RSSI, SNR і SINR", size=15, bold=True, color=INK))

    gx0, gy0, gw, gh = 80, 310, 620, 230

    # Осі
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=MUTED, sw=1.5))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=MUTED, sw=1.5))
    f.append(text(gx0 + gw + 15, gy0 + 4, "Частота", size=12, bold=True, color=INK))
    f.append(text(gx0 - 15, gy0 - gh - 10, "Потужність (дБм)", size=12, bold=True, color=INK))

    # Рівні
    y_n = gy0 - 40   # Noise floor (-105 dBm)
    y_i = gy0 - 110  # Interference (-85 dBm)
    y_s = gy0 - 190  # Signal (-65 dBm)

    # Пунктири рівнів
    f.append(line(gx0, y_n, gx0 + gw, y_n, color="#cbd5e1", sw=1.0, dash="4 4"))
    f.append(line(gx0, y_i, gx0 + gw, y_i, color="#fca5a5", sw=1.0, dash="4 4"))
    f.append(line(gx0, y_s, gx0 + gw, y_s, color="#93c5fd", sw=1.0, dash="4 4"))

    # Позначки рівнів на осі Y
    f.append(text(gx0 - 10, y_n + 4, "-105 дБм", size=10, color=MUTED, anchor="end"))
    f.append(text(gx0 - 10, y_i + 4, "-85 дБм", size=10, color=NEG, anchor="end"))
    f.append(text(gx0 - 10, y_s + 4, "-65 дБм", size=10, color=BLUE, anchor="end"))

    # Підлога шуму (заповнення через path)
    f.append(f'<path d="M {gx0} {y_n} L {gx0+gw} {y_n} L {gx0+gw} {gy0} L {gx0} {gy0} Z" fill="#f1f5f9" stroke="none"/>')
    f.append(text(gx0 + 20, y_n - 8, "Тепловий шум (Noise Floor)", size=11, color=MUTED, italic=True))

    # Завада (Interference peak)
    i_x, i_w = gx0 + 160, 90
    f.append(rect(i_x, y_i, i_w, gy0 - y_i, fill="#fee2e2", stroke=NEG, sw=1.5, rx=3))
    f.append(text(i_x + i_w/2, y_i + 20, "Завада (I)", size=11, bold=True, color=NEG, anchor="middle"))

    # Корисний сигнал (Signal peak)
    s_x, s_w = gx0 + 380, 110
    f.append(rect(s_x, y_s, s_w, gy0 - y_s, fill="#dbeafe", stroke=BLUE, sw=2.0, rx=3))
    f.append(text(s_x + s_w/2, y_s + 24, "Сигнал (S)", size=12, bold=True, color=BLUE, anchor="middle"))

    # Стрілки метрик
    # SNR arrow (S to N)
    snr_x = s_x + s_w + 25
    f.append(line(snr_x, y_s, snr_x, y_n, color=POS, sw=2.0))
    f.append(line(snr_x - 5, y_s + 6, snr_x, y_s, color=POS, sw=2.0))
    f.append(line(snr_x + 5, y_s + 6, snr_x, y_s, color=POS, sw=2.0))
    f.append(line(snr_x - 5, y_n - 6, snr_x, y_n, color=POS, sw=2.0))
    f.append(line(snr_x + 5, y_n - 6, snr_x, y_n, color=POS, sw=2.0))
    f.append(text(snr_x + 10, (y_s + y_n)/2 + 4, "SNR = 40 дБ", size=11, bold=True, color=POS))

    # SINR arrow (S to I)
    sinr_x = s_x - 30
    f.append(line(sinr_x, y_s, sinr_x, y_i, color=ACCENT, sw=2.0))
    f.append(line(sinr_x - 5, y_s + 6, sinr_x, y_s, color=ACCENT, sw=2.0))
    f.append(line(sinr_x + 5, y_s + 6, sinr_x, y_s, color=ACCENT, sw=2.0))
    f.append(line(sinr_x - 5, y_i - 6, sinr_x, y_i, color=ACCENT, sw=2.0))
    f.append(line(sinr_x + 5, y_i - 6, sinr_x, y_i, color=ACCENT, sw=2.0))
    f.append(text(sinr_x - 10, (y_s + y_i)/2 + 4, "SINR = 20 дБ", size=11, bold=True, color=ACCENT, anchor="end"))

    # Блок RSSI примітки
    rx, ry = gx0 + 10, y_s - 25
    f.append(rect(rx, ry, 210, 50, fill="#fffbeb", stroke="#f59e0b", sw=1.2, rx=4))
    f.append(text(rx + 10, ry + 20, "RSSI = P(S) + P(I) + P(N)", size=11, bold=True, color=INK))
    f.append(text(rx + 10, ry + 38, "Сумарна потужність у смузі", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "snr-sinr-noise-floor.svg"), W, H, *f)


# ── 2. Криві водоспаду BER(Eb/N0) ──────────────────────────────────────────
def fig_ber_waterfall():
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 28, "Криві залежності BER від Eb/N0 для різних типів модуляції", size=15, bold=True, color=INK))

    gx0, gy0, gw, gh = 80, 360, 620, 290

    # Сітка та осі
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=MUTED, sw=1.5))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=MUTED, sw=1.5))
    f.append(text(gx0 + gw/2, gy0 + 35, "Eb/N0 (дБ)", size=12, bold=True, color=INK, anchor="middle"))
    f.append(text(gx0 - 55, gy0 - gh/2, "BER", size=12, bold=True, color=INK))

    # Горизонтальні лінії для логарифмічних ступенів BER (10^0 до 10^-6)
    ber_labels = ["10⁰", "10⁻¹", "10⁻²", "10⁻³", "10⁻⁴", "10⁻⁵", "10⁻⁶"]
    for i in range(7):
        y = gy0 - i * (gh / 6)
        f.append(line(gx0, y, gx0 + gw, y, color="#e2e8f0", sw=1.0, dash="3 3"))
        f.append(text(gx0 - 10, y + 4, ber_labels[i], size=10, color=MUTED, anchor="end"))

    # Вертикальні лінії дБ (0 до 16 дБ)
    for db in range(0, 17, 2):
        x = gx0 + (db / 16.0) * gw
        f.append(line(x, gy0, x, gy0 - gh, color="#e2e8f0", sw=1.0, dash="3 3"))
        f.append(text(x, gy0 + 16, str(db), size=10, color=MUTED, anchor="middle"))

    # Порогі якісного зв'язку (BER = 10^-5)
    y_target = gy0 - 5 * (gh / 6)
    f.append(line(gx0, y_target, gx0 + gw, y_target, color=POS, sw=1.2, dash="6 3"))
    f.append(text(gx0 + gw - 10, y_target - 6, "Цільовий поріг BER = 10⁻⁵", size=10, color=POS, bold=True, anchor="end"))

    # Генерація кривих
    # BPSK: BER = 0.5 * erfc(sqrt(10^(ebn0/10)))
    def bpsk_ber(ebn0_db):
        x = math.sqrt(10**(ebn0_db / 10.0))
        if x < 0.1: return 0.5
        ber = 0.5 * math.erfc(x)
        return max(1e-6, ber)

    def qam16_ber(ebn0_db):
        x = math.sqrt(0.4 * 10**(ebn0_db / 10.0))
        ber = 0.375 * math.erfc(x)
        return max(1e-6, ber)

    def qam64_ber(ebn0_db):
        x = math.sqrt(0.1428 * 10**(ebn0_db / 10.0))
        ber = 0.29 * math.erfc(x)
        return max(1e-6, ber)

    def plot_ber(curve_fn, color, sw=2.2):
        pts = []
        for step in range(161):
            db = step * 0.1
            val = curve_fn(db)
            log_val = math.log10(val)
            x = gx0 + (db / 16.0) * gw
            y = gy0 - (-log_val / 6.0) * gh
            y = max(gy0 - gh, min(gy0, y))
            pts.append(f"{x:.1f},{y:.1f}")
        d_attr = "M " + " L ".join(pts)
        return f'<path d="{d_attr}" fill="none" stroke="{color}" stroke-width="{sw}"/>'

    f.append(plot_ber(bpsk_ber, POS, sw=2.5))
    f.append(plot_ber(qam16_ber, BLUE, sw=2.5))
    f.append(plot_ber(qam64_ber, ACCENT, sw=2.5))

    # Легенда
    lx, ly = gx0 + 380, gy0 - gh + 20
    f.append(rect(lx, ly, 220, 100, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(lx + 12, ly + 20, "Модуляції:", size=11, bold=True, color=INK))

    f.append(line(lx + 15, ly + 40, lx + 45, ly + 40, color=POS, sw=2.5))
    f.append(text(lx + 55, ly + 44, "BPSK / QPSK (стійка)", size=11, color=INK))

    f.append(line(lx + 15, ly + 62, lx + 45, ly + 62, color=BLUE, sw=2.5))
    f.append(text(lx + 55, ly + 66, "16-QAM (баланс)", size=11, color=INK))

    f.append(line(lx + 15, ly + 84, lx + 45, ly + 84, color=ACCENT, sw=2.5))
    f.append(text(lx + 55, ly + 88, "64-QAM (швидкісна)", size=11, color=INK))

    render(os.path.join(IMG, "ber-waterfall-curves.svg"), W, H, *f)


# ── 3. LQI та вимірювання векторної помилки EVM ────────────────────────────
def fig_lqi_evm():
    W, H = 780, 360
    f = []

    f.append(text(W / 2, 28, "Формування LQI на основі вектора помилки сузір'я (EVM)", size=15, bold=True, color=INK))

    # Ліва панель: Ідеальне сузір'я QPSK
    p1_x, p1_y, p_w, p_h = 40, 60, 210, 250
    f.append(rect(p1_x, p1_y, p_w, p_h, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=6))
    f.append(text(p1_x + p_w/2, p1_y + 24, "Ідеальний сигнал", size=12, bold=True, color=INK, anchor="middle"))
    f.append(text(p1_x + p_w/2, p1_y + 42, "LQI = 255 (EVM ≈ 0%)", size=11, color=POS, bold=True, anchor="middle"))

    cx1, cy1 = p1_x + p_w/2, p1_y + 150
    f.append(line(cx1 - 70, cy1, cx1 + 70, cy1, color="#cbd5e1", sw=1.0))
    f.append(line(cx1, cy1 - 70, cx1, cy1 + 70, color="#cbd5e1", sw=1.0))

    pts_ideal = [(-45, -45), (45, -45), (-45, 45), (45, 45)]
    for dx, dy in pts_ideal:
        f.append(circle(cx1 + dx, cy1 + dy, 6, fill=POS, stroke="#ffffff", sw=1.5))

    # Центральна панель: Сигнал із шумом та вектор EVM
    p2_x = 285
    f.append(rect(p2_x, p1_y, p_w, p_h, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=6))
    f.append(text(p2_x + p_w/2, p1_y + 24, "Зашумлений сигнал", size=12, bold=True, color=INK, anchor="middle"))
    f.append(text(p2_x + p_w/2, p1_y + 42, "LQI = 110 (Високий EVM)", size=11, color=ACCENT, bold=True, anchor="middle"))

    cx2, cy2 = p2_x + p_w/2, p1_y + 150
    f.append(line(cx2 - 70, cy2, cx2 + 70, cy2, color="#cbd5e1", sw=1.0))
    f.append(line(cx2, cy2 - 70, cx2, cy2 + 70, color="#cbd5e1", sw=1.0))

    # Точки хмари
    import random
    random.seed(42)
    for dx, dy in pts_ideal:
        f.append(circle(cx2 + dx, cy2 + dy, 5, fill="#cbd5e1", stroke="none"))
        for _ in range(8):
            rx = dx + random.gauss(0, 14)
            ry = dy + random.gauss(0, 14)
            f.append(circle(cx2 + rx, cy2 + ry, 3, fill=ACCENT, stroke="none"))

    # Вектор EVM для однієї точки
    t_dx, t_dy = 45, -45
    rx_evm, ry_evm = t_dx + 18, t_dy - 16
    f.append(line(cx2 + t_dx, cy2 + t_dy, cx2 + rx_evm, cy2 + ry_evm, color=NEG, sw=2.0))
    f.append(text(cx2 + rx_evm + 6, cy2 + ry_evm, "EVM", size=10, bold=True, color=NEG))

    # Права панель: Обчислення LQI у приймачі
    p3_x = 530
    p3_w = 210
    f.append(rect(p3_x, p1_y, p3_w, p_h, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=6))
    f.append(text(p3_x + p3_w/2, p1_y + 24, "Обчислення у чіпі", size=12, bold=True, color=INK, anchor="middle"))

    b1_y = p1_y + 60
    f.append(rect(p3_x + 15, b1_y, 180, 45, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(p3_x + 105, b1_y + 18, "Кореляція преамбули", size=11, bold=True, color=INK, anchor="middle"))
    f.append(text(p3_x + 105, b1_y + 34, "Перші 8 симв. кадру", size=10, color=MUTED, anchor="middle"))

    f.append(line(p3_x + 105, b1_y + 45, p3_x + 105, b1_y + 65, color=MUTED, sw=1.5))

    b2_y = b1_y + 65
    f.append(rect(p3_x + 15, b2_y, 180, 45, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(p3_x + 105, b2_y + 18, "Усереднення EVM", size=11, bold=True, color=INK, anchor="middle"))
    f.append(text(p3_x + 105, b2_y + 34, "Відхилення від сітки", size=10, color=MUTED, anchor="middle"))

    f.append(line(p3_x + 105, b2_y + 45, p3_x + 105, b2_y + 65, color=MUTED, sw=1.5))

    b3_y = b2_y + 65
    f.append(rect(p3_x + 15, b3_y, 180, 40, fill="#e0f2fe", stroke=BLUE, sw=1.5, rx=4))
    f.append(text(p3_x + 105, b3_y + 24, "Реєстр LQI (0...255)", size=11, bold=True, color=BLUE, anchor="middle"))

    render(os.path.join(IMG, "lqi-constellation-evm.svg"), W, H, *f)


# ── 4. Станція адаптації швидкісного режиму (MCS State Machine) ─────────────
def fig_link_adaptation():
    W, H = 760, 320
    f = []

    f.append(text(W / 2, 28, "Автомат адаптації модуляції та кодування (MCS) за метриками", size=15, bold=True, color=INK))

    # Стан 1: BPSK (Низька швидкість, висока надійність)
    s1_x, s1_y, s_w, s_h = 50, 100, 190, 140
    f.append(rect(s1_x, s1_y, s_w, s_h, fill="#f0fdf4", stroke=POS, sw=2.0, rx=8))
    f.append(text(s1_x + s_w/2, s1_y + 30, "MCS 0: BPSK", size=14, bold=True, color=POS, anchor="middle"))
    f.append(text(s1_x + s_w/2, s1_y + 55, "Максимальна стійкість", size=11, color=INK, anchor="middle"))
    f.append(text(s1_x + s_w/2, s1_y + 85, "Поріг SINR < 6 дБ", size=10, color=MUTED, anchor="middle"))
    f.append(text(s1_x + s_w/2, s1_y + 105, "або PER > 10%", size=10, color=NEG, bold=True, anchor="middle"))

    # Стан 2: QPSK (Середня швидкість)
    s2_x = 285
    f.append(rect(s2_x, s1_y, s_w, s_h, fill="#eff6ff", stroke=BLUE, sw=2.0, rx=8))
    f.append(text(s2_x + s_w/2, s1_y + 30, "MCS 1-2: QPSK", size=14, bold=True, color=BLUE, anchor="middle"))
    f.append(text(s2_x + s_w/2, s1_y + 55, "Базовий режим", size=11, color=INK, anchor="middle"))
    f.append(text(s2_x + s_w/2, s1_y + 85, "6 дБ ≤ SINR < 14 дБ", size=10, color=MUTED, anchor="middle"))
    f.append(text(s2_x + s_w/2, s1_y + 105, "PER < 3%", size=10, color=POS, bold=True, anchor="middle"))

    # Стан 3: 16-QAM (Висока швидкість)
    s3_x = 520
    f.append(rect(s3_x, s1_y, s_w, s_h, fill="#fff7ed", stroke=ACCENT, sw=2.0, rx=8))
    f.append(text(s3_x + s_w/2, s1_y + 30, "MCS 3-4: 16-QAM", size=14, bold=True, color=ACCENT, anchor="middle"))
    f.append(text(s3_x + s_w/2, s1_y + 55, "Висока пропускність", size=11, color=INK, anchor="middle"))
    f.append(text(s3_x + s_w/2, s1_y + 85, "SINR ≥ 14 дБ", size=10, color=MUTED, anchor="middle"))
    f.append(text(s3_x + s_w/2, s1_y + 105, "LQI > 200, PER < 1%", size=10, color=POS, bold=True, anchor="middle"))

    # Переходи (Стрілки підвищення і зниження)
    # S1 -> S2 (Підвищення)
    f.append(line(s1_x + s_w, s1_y + 45, s2_x, s1_y + 45, color=POS, sw=2.0))
    f.append(line(s2_x - 8, s1_y + 40, s2_x, s1_y + 45, color=POS, sw=2.0))
    f.append(line(s2_x - 8, s1_y + 50, s2_x, s1_y + 45, color=POS, sw=2.0))
    f.append(text(s1_x + s_w + 22, s1_y + 35, "SINR ↑", size=10, bold=True, color=POS))

    # S2 -> S1 (Зниження)
    f.append(line(s2_x, s1_y + 95, s1_x + s_w, s1_y + 95, color=NEG, sw=2.0))
    f.append(line(s1_x + s_w + 8, s1_y + 90, s1_x + s_w, s1_y + 95, color=NEG, sw=2.0))
    f.append(line(s1_x + s_w + 8, s1_y + 100, s1_x + s_w, s1_y + 95, color=NEG, sw=2.0))
    f.append(text(s1_x + s_w + 22, s1_y + 112, "PER ↑", size=10, bold=True, color=NEG))

    # S2 -> S3 (Підвищення)
    f.append(line(s2_x + s_w, s1_y + 45, s3_x, s1_y + 45, color=POS, sw=2.0))
    f.append(line(s3_x - 8, s1_y + 40, s3_x, s1_y + 45, color=POS, sw=2.0))
    f.append(line(s3_x - 8, s1_y + 50, s3_x, s1_y + 45, color=POS, sw=2.0))
    f.append(text(s2_x + s_w + 22, s1_y + 35, "LQI ↑", size=10, bold=True, color=POS))

    # S3 -> S2 (Зниження)
    f.append(line(s3_x, s1_y + 95, s2_x + s_w, s1_y + 95, color=NEG, sw=2.0))
    f.append(line(s2_x + s_w + 8, s1_y + 90, s2_x + s_w, s1_y + 95, color=NEG, sw=2.0))
    f.append(line(s2_x + s_w + 8, s1_y + 100, s2_x + s_w, s1_y + 95, color=NEG, sw=2.0))
    f.append(text(s2_x + s_w + 22, s1_y + 112, "SINR ↓", size=10, bold=True, color=NEG))

    render(os.path.join(IMG, "link-adaptation-state-machine.svg"), W, H, *f)


if __name__ == "__main__":
    fig_snr_sinr_spectrum()
    fig_ber_waterfall()
    fig_lqi_evm()
    fig_link_adaptation()
    print("Успішно згенеровано 4 SVG фігури у ./img/")
