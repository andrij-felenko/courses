# -*- coding: utf-8 -*-
# Фігури теми «Лирп-модуляція (CSS) і розширення спектра»
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACCENT = "#b08900"


def chirp_waveform(cx, base_y, width, amp, f_start, f_end, color, sw=2.0, n=200):
    """Генерує часову хвилю чирпа з лінійною зміною частоти."""
    pts = []
    for i in range(n + 1):
        t = i / float(n)  # 0..1
        x = cx + t * width
        # Миттєва фаза phi(t) = 2*pi*(f_start*t + 0.5*(f_end - f_start)*t^2)
        phase = 2.0 * math.pi * (f_start * t + 0.5 * (f_end - f_start) * t * t)
        y = base_y - amp * math.sin(phase)
        pts.append("%.1f,%.1f" % (x, y))
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (" ".join(pts), color, sw)


def fig_chirp_time_freq():
    """Фігура 1: Часово-частотна характеристика up-chirp і down-chirp."""
    W, H = 760, 360
    p = []

    # Заголовок блоків
    p.append(fitbox(190, 35, 340, 30, "Висхідний чирп (Up-Chirp)", size=13, fill="#eef6ef", stroke=FIELD, bold=True))
    p.append(fitbox(570, 35, 340, 30, "Низхідний чирп (Down-Chirp)", size=13, fill="#eebfbe", stroke=POS, bold=True))

    # --- Ліва панель: Up-Chirp ---
    # Часова хвиля
    p.append(line(40, 110, 340, 110, color=MUTED, sw=1.0, dash="3 3"))
    p.append(chirp_waveform(40, 110, 300, 30, 2.0, 10.0, FIELD, sw=2.0))
    p.append(text(190, 65, "Часовий сигнал s(t)", size=10.5, color=INK))

    # Спектрограма (час-частота)
    ox1, oy1, gw, gh = 60, 290, 260, 120
    p.append(line(ox1, oy1, ox1 + gw, oy1, color=INK, sw=1.5))
    p.append(line(ox1, oy1, ox1, oy1 - gh, color=INK, sw=1.5))
    p.append(text(ox1 + gw / 2, oy1 + 22, "час t →", size=10, color=INK))
    p.append(text(ox1 - 25, oy1 - gh / 2, "f", size=11, color=INK, bold=True))
    p.append(line(ox1, oy1 - 10, ox1 + gw, oy1 - gh + 10, color=FIELD, sw=3.0))
    p.append(text(ox1 - 15, oy1 - 10, "f_min", size=9.5, color=MUTED))
    p.append(text(ox1 - 15, oy1 - gh + 10, "f_max", size=9.5, color=MUTED))
    p.append(line(ox1, oy1 - gh + 10, ox1 + gw, oy1 - gh + 10, color=MUTED, sw=0.8, dash="2 2"))
    p.append(line(ox1 + gw, oy1, ox1 + gw, oy1 - gh, color=MUTED, sw=0.8, dash="2 2"))
    p.append(text(ox1 + gw, oy1 + 14, "T", size=10, color=INK, bold=True))

    # --- Права панель: Down-Chirp ---
    # Часова хвиля
    p.append(line(420, 110, 720, 110, color=MUTED, sw=1.0, dash="3 3"))
    p.append(chirp_waveform(420, 110, 300, 30, 10.0, 2.0, POS, sw=2.0))
    p.append(text(570, 65, "Часовий сигнал s(t)", size=10.5, color=INK))

    # Спектрограма (час-частота)
    ox2, oy2 = 440, 290
    p.append(line(ox2, oy2, ox2 + gw, oy2, color=INK, sw=1.5))
    p.append(line(ox2, oy2, ox2, oy2 - gh, color=INK, sw=1.5))
    p.append(text(ox2 + gw / 2, oy2 + 22, "час t →", size=10, color=INK))
    p.append(text(ox2 - 25, oy2 - gh / 2, "f", size=11, color=INK, bold=True))
    p.append(line(ox2, oy2 - gh + 10, ox2 + gw, oy2 - 10, color=POS, sw=3.0))
    p.append(text(ox2 - 15, oy2 - 10, "f_min", size=9.5, color=MUTED))
    p.append(text(ox2 - 15, oy2 - gh + 10, "f_max", size=9.5, color=MUTED))

    # Підсумок
    p.append(fitbox(380, 335, 700, 26, "Частота змінюється лінійно від f_min до f_max зі швидкістю μ = B / T [Гц/с].", size=11.5, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, "chirp-time-freq.svg"), W, H, *p,
           title="Часово-частотна характеристика up-chirp і down-chirp")


def fig_pulse_compression():
    """Фігура 2: Стиснення імпульсу узгодженим фільтром."""
    W, H = 760, 320
    p = []

    # Вхідний чирп
    p.append(text(110, 45, "Тривалий чирп s(t)", size=12, color=INK, bold=True))
    p.append(text(110, 65, "тривалість T, амплітуда A", size=10, color=MUTED))
    p.append(line(30, 140, 190, 140, color=MUTED, sw=1.0, dash="3 3"))
    p.append(chirp_waveform(30, 140, 160, 25, 2.0, 8.0, FIELD, sw=1.8))
    p.append(arrow(30, 175, 190, 175, color=MUTED, sw=1.2))
    p.append(text(110, 190, "Ширина T", size=10, color=MUTED, bold=True))

    # Перехід / Блок фільтра
    p.append(arrow(200, 140, 240, 140, color=INK, sw=2.0))
    fb, _, _ = textbox(340, 140, "Узгоджений фільтр\nh(t) = s(T - t)", size=12, pad=12, fill="#e9eefb", stroke=NEG, bold=True)
    p.append(fb)
    p.append(arrow(440, 140, 480, 140, color=INK, sw=2.0))

    # Вихідний стиснений імпульс (sinc)
    p.append(text(620, 45, "Стиснений імпульс y(t)", size=12, color=POS, bold=True))
    p.append(text(620, 65, "амплітуда A · √(B·T)", size=10, color=POS))
    p.append(line(490, 140, 750, 140, color=MUTED, sw=1.0, dash="3 3"))

    # Крива sinc
    pts = []
    for i in range(120):
        t = -4.0 + 8.0 * i / 119.0
        x = 620 + t * 20
        # sinc(x) = sin(pi*x)/(pi*x)
        if abs(t) < 1e-4:
            val = 1.0
        else:
            val = math.sin(math.pi * t) / (math.pi * t)
        y = 140 - val * 75
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (" ".join(pts), POS))

    # Позначки виграшу
    p.append(arrow(620, 140, 620, 68, color=POS, sw=1.5))
    p.append(text(645, 100, "Пік × (B·T)", size=10.5, color=POS, bold=True))
    p.append(line(600, 155, 640, 155, color=MUTED, sw=1.2))
    p.append(text(620, 172, "Ширина τ = 1/B", size=10, color=INK, bold=True))

    # Підсумок
    p.append(fitbox(380, 275, 710, 32,
                    "Коефіцієнт стиснення імпульсу = T / τ = B · T. Енергія накопичується в вузькому піку.",
                    size=12, fill="#eef6ef", stroke=FIELD, bold=True))

    render(os.path.join(OUT, "pulse-compression.svg"), W, H, *p,
           title="Стиснення імпульсу узгодженим фільтром")


def fig_lora_cyclic_css():
    """Фігура 3: Циклична чирп-модуляція (LoRa CSS) та дечирпінг."""
    W, H = 760, 380
    p = []

    # А) Передавач: Символ -> Циклічний чирп
    p.append(text(130, 25, "1. Передавач: Зсув частоти", size=12, color=INK, bold=True))
    ox1, oy1, gw, gh = 40, 160, 180, 100
    p.append(line(ox1, oy1, ox1 + gw, oy1, color=INK, sw=1.2))
    p.append(line(ox1, oy1, ox1, oy1 - gh, color=INK, sw=1.2))
    # Циклічно зсунута лінія частоти
    p.append(line(ox1, oy1 - 35, ox1 + 117, oy1 - gh, color=FIELD, sw=2.5))
    p.append(line(ox1 + 117, oy1, ox1 + gw, oy1 - 35, color=FIELD, sw=2.5))
    p.append(line(ox1 + 117, oy1, ox1 + 117, oy1 - gh, color=MUTED, sw=0.8, dash="2 2"))
    p.append(text(ox1 - 15, oy1 - 35, "f_start", size=9, color=FIELD, bold=True))
    p.append(text(ox1 + 90, oy1 + 16, "Символ k", size=10, color=FIELD, bold=True))

    # Стрілка множення (De-chirping)
    p.append(arrow(230, 110, 270, 110, color=INK, sw=1.8))

    # Б) Приймач: De-chirping (множення на опорний down-chirp)
    p.append(text(380, 25, "2. Приймач: De-Chirping", size=12, color=INK, bold=True))
    ox2, oy2 = 280, 160
    p.append(line(ox2, oy2, ox2 + gw, oy2, color=INK, sw=1.2))
    p.append(line(ox2, oy2, ox2, oy2 - gh, color=INK, sw=1.2))
    # Вхідний зсунутий + опорний down-chirp
    p.append(line(ox2, oy2 - 35, ox2 + 117, oy2 - gh, color=FIELD, sw=1.5, dash="4 2"))
    p.append(line(ox2 + 117, oy2, ox2 + gw, oy2 - 35, color=FIELD, sw=1.5, dash="4 2"))
    p.append(line(ox2, oy2 - gh, ox2 + gw, oy2, color=POS, sw=2.0))
    p.append(text(ox2 + 130, oy2 - 80, "Down-chirp", size=9.5, color=POS))

    # Стрілка до результату змішування
    p.append(arrow(470, 110, 510, 110, color=INK, sw=1.8))

    # В) Постійна тональна частота після змішування
    p.append(text(620, 25, "3. Биттєвий сигнал", size=12, color=INK, bold=True))
    ox3, oy3 = 520, 160
    p.append(line(ox3, oy3, ox3 + gw, oy3, color=INK, sw=1.2))
    p.append(line(ox3, oy3, ox3, oy3 - gh, color=INK, sw=1.2))
    p.append(line(ox3, oy3 - 35, ox3 + gw, oy3 - 35, color=NEG, sw=2.5))
    p.append(text(ox3 - 15, oy3 - 35, "f_beat", size=9.5, color=NEG, bold=True))
    p.append(text(ox3 + gw / 2, oy3 + 16, "Постійна f_beat = k·B/2^SF", size=9.5, color=NEG))

    # Г) Нижній блок: FFT аналіз
    p.append(arrow(610, 185, 610, 225, color=INK, sw=1.8))
    p.append(text(610, 208, "БПФ (FFT)", size=10, color=INK, anchor="west", bold=True))

    ox4, oy4, gw4, gh4 = 160, 330, 440, 90
    p.append(line(ox4, oy4, ox4 + gw4, oy4, color=INK, sw=1.5))
    p.append(line(ox4, oy4, ox4, oy4 - gh4, color=INK, sw=1.5))
    p.append(text(ox4 + gw4 + 25, oy4 + 4, "частота f", size=10, color=INK))
    p.append(text(ox4 - 25, oy4 - gh4 / 2, "Ампл.", size=10, color=INK))

    # Шум на дні FFT та один високий пік
    noise_pts = []
    for i in range(45):
        x = ox4 + gw4 * i / 44.0
        val = 5 + (i * 7 % 11)
        if abs(i - 18) <= 1:
            val = 75 if i == 18 else 20
        noise_pts.append((x, oy4 - val))

    for i in range(len(noise_pts) - 1):
        x1, y1 = noise_pts[i]
        x2, y2 = noise_pts[i + 1]
        c = NEG if (i == 17 or i == 18) else MUTED
        sw_l = 2.5 if (i == 17 or i == 18) else 1.0
        p.append(line(x1, y1, x2, y2, color=c, sw=sw_l))

    peak_x = ox4 + gw4 * 18 / 44.0
    p.append(text(peak_x, oy4 - 82, "Пік на відліку k", size=11, color=NEG, bold=True))
    p.append(line(peak_x, oy4, peak_x, oy4 - gh4, color=NEG, sw=0.8, dash="2 2"))

    render(os.path.join(OUT, "lora-cyclic-css.svg"), W, H, *p,
           title="Циклічна чирп-модуляція (LoRa CSS) та дечирпінг")


def fig_processing_gain_noise():
    """Фігура 4: Спектральне розширення та виграш обробки під рівнем шуму."""
    W, H = 760, 320
    p = []

    # Ліва панель: Сигнал у каналі (до despreading)
    p.append(fitbox(190, 35, 340, 28, "Вхідний RF-сигнал у каналі", size=12, fill="#eebfbe", stroke=POS, bold=True))
    ox1, oy1, gw, gh = 40, 240, 300, 160
    p.append(line(ox1, oy1, ox1 + gw, oy1, color=INK, sw=1.5))
    p.append(line(ox1, oy1, ox1, oy1 - gh, color=INK, sw=1.5))
    p.append(text(ox1 + gw / 2, oy1 + 20, "частота f →", size=10, color=INK))

    # Рівень шуму (високий прямокутник)
    p.append(rect(ox1 + 10, oy1 - 120, gw - 20, 120, fill="#fcedec", stroke=POS, sw=1.2, rx=2))
    p.append(line(ox1 + 10, oy1 - 120, ox1 + gw - 10, oy1 - 120, color=POS, sw=1.8, dash="4 2"))
    p.append(text(ox1 + gw / 2, oy1 - 130, "Рівень шуму P_noise", size=10, color=POS, bold=True))

    # Низький чирп під шумом
    p.append(rect(ox1 + 30, oy1 - 35, gw - 60, 35, fill="#d5e8d4", stroke=FIELD, sw=1.5, rx=2))
    p.append(text(ox1 + gw / 2, oy1 - 18, "Чирп P_signal (SNR < 0 dB)", size=10, color=FIELD, bold=True))

    # Центр: Операція De-chirping & FFT
    p.append(arrow(360, 160, 410, 160, color=INK, sw=2.2))
    p.append(text(385, 142, "De-chirping", size=10, color=INK, bold=True))
    p.append(text(385, 178, "+ FFT", size=10, color=INK, bold=True))

    # Права панель: Спектр після FFT (після despreading)
    p.append(fitbox(580, 35, 300, 28, "Спектр після FFT (Декодування)", size=12, fill="#eef6ef", stroke=FIELD, bold=True))
    ox2, oy2 = 430, 240
    p.append(line(ox2, oy2, ox2 + gw, oy2, color=INK, sw=1.5))
    p.append(line(ox2, oy2, ox2, oy2 - gh, color=INK, sw=1.5))
    p.append(text(ox2 + gw / 2, oy2 + 20, "індекс бін $k$ →", size=10, color=INK))

    # Рівень шуму розмазаний по бінах (низька планка)
    p.append(rect(ox2 + 10, oy2 - 30, gw - 20, 30, fill="#fcedec", stroke=POS, sw=1.0, rx=2))
    p.append(text(ox2 + gw / 2 - 40, oy2 - 15, "Шум у бінах", size=9.5, color=POS))

    # Вся енергія чирпа зібрана в один бін
    peak_x = ox2 + 180
    p.append(rect(peak_x - 12, oy2 - 145, 24, 145, fill="#27ae60", stroke=FIELD, sw=1.8, rx=2))
    p.append(text(peak_x, oy2 - 152, "Сигнальний пік", size=10, color=FIELD, bold=True))

    p.append(arrow(ox2 + gw - 30, oy2 - 30, ox2 + gw - 30, oy2 - 145, color=NEG, sw=1.5))
    p.append(text(ox2 + gw - 25, oy2 - 85, "Виграш PG = 10·lg(B·T)", size=9.5, color=NEG, anchor="west", bold=True))

    # Підсумок
    p.append(fitbox(380, 285, 710, 28,
                    "Виграш обробки PG стискає сигнал в один бін FFT, дозволяючи впевнено декодувати дані при SNR до -20 dB.",
                    size=11, fill=FILL, stroke=LINE))

    render(os.path.join(OUT, "processing-gain-noise.svg"), W, H, *p,
           title="Спектральне розширення та виграш обробки під рівнем шуму")


if __name__ == "__main__":
    fig_chirp_time_freq()
    fig_pulse_compression()
    fig_lora_cyclic_css()
    fig_processing_gain_noise()
    print("Всі фігури згенеровано успішно.")
