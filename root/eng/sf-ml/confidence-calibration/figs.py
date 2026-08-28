# -*- coding: utf-8 -*-
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. reliability-diagram.svg: Некалібрована проти каліброваної моделі ─────────
def fig_reliability_diagram():
    W, H = 880, 430
    frags = []

    # Загальне тло
    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок зверху
    frags.append(text(W / 2, 28, "Діаграма надійності: оцінка впевненості проти реальної точності", size=16, bold=True, color=INK))

    # Параметри двох панелей
    pw, ph = 330, 270
    p1_x, p1_y = 70, 75
    p2_x, p2_y = 480, 75

    # Дані для 10 бінів: (bin_center, conf_uncal, acc_uncal, conf_cal, acc_cal)
    # Некалібрована модель: типова overconfidence (conf >> acc у високих бінах)
    bins_data = [
        (0.05, 0.08, 0.05, 0.06, 0.06),
        (0.15, 0.16, 0.12, 0.15, 0.14),
        (0.25, 0.27, 0.19, 0.24, 0.25),
        (0.35, 0.36, 0.26, 0.34, 0.35),
        (0.45, 0.46, 0.33, 0.45, 0.44),
        (0.55, 0.57, 0.39, 0.54, 0.55),
        (0.65, 0.67, 0.48, 0.64, 0.65),
        (0.75, 0.77, 0.56, 0.75, 0.74),
        (0.85, 0.87, 0.66, 0.85, 0.86),
        (0.95, 0.96, 0.73, 0.94, 0.93),
    ]

    def draw_panel(px, py, title, ece_text, is_calibrated):
        p_frags = []
        # Тло панелі
        p_frags.append(rect(px, py, pw, ph, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))

        # Заголовок панелі
        p_frags.append(text(px + pw / 2, py + 24, title, size=14, bold=True, color=INK))
        p_frags.append(text(px + pw / 2, py + 42, ece_text, size=13, bold=True, color=POS if not is_calibrated else FIELD))

        # Область графіка
        gx, gy = px + 45, py + 55
        gw, gh = pw - 65, ph - 95

        # Координатна сітка та осі
        p_frags.append(rect(gx, gy, gw, gh, fill=BG, stroke="#94a3b8", sw=1.0, rx=0))
        for step in [0.25, 0.50, 0.75]:
            sy = gy + gh * (1.0 - step)
            sx = gx + gw * step
            p_frags.append(line(gx, sy, gx + gw, sy, color="#e2e8f0", sw=0.8, dash="3,3"))
            p_frags.append(line(sx, gy, sx, gy + gh, color="#e2e8f0", sw=0.8, dash="3,3"))

        # Ідеальна діагональ калібрування (Acc = Conf)
        p_frags.append(line(gx, gy + gh, gx + gw, gy, color="#64748b", sw=1.5, dash="5,4"))

        # Стовпчики бінів
        bin_w = gw / 10.0
        for i, (b_center, conf_u, acc_u, conf_c, acc_c) in enumerate(bins_data):
            conf = conf_c if is_calibrated else conf_u
            acc = acc_c if is_calibrated else acc_u

            bx = gx + i * bin_w + 2
            bw = bin_w - 4
            bh_acc = gh * acc
            bh_conf = gh * conf

            by_acc = gy + gh - bh_acc
            by_conf = gy + gh - bh_conf

            if not is_calibrated:
                # Похибка калібрування (Calibration Gap) — червоний штрихований прямокутник
                gap_h = abs(bh_conf - bh_acc)
                gap_y = min(by_acc, by_conf)
                p_frags.append(rect(bx, gap_y, bw, gap_h, fill="#fee2e2", stroke=POS, sw=0.8, rx=2))
                # Фактична точність — синій стовпчик
                p_frags.append(rect(bx, by_acc, bw, bh_acc, fill="#93c5fd", stroke=NEG, sw=1.0, rx=2))
            else:
                # Калібрована модель — стовпчик збігається з діагоналлю
                p_frags.append(rect(bx, by_acc, bw, bh_acc, fill="#86efac", stroke=FIELD, sw=1.0, rx=2))

        # Позначки осей
        p_frags.append(text(gx - 8, gy + gh + 4, "0.0", size=10, color=MUTED, anchor="end"))
        p_frags.append(text(gx - 8, gy + gh * 0.5 + 4, "0.5", size=10, color=MUTED, anchor="end"))
        p_frags.append(text(gx - 8, gy + 4, "1.0", size=10, color=MUTED, anchor="end"))

        p_frags.append(text(gx, gy + gh + 16, "0.0", size=10, color=MUTED, anchor="middle"))
        p_frags.append(text(gx + gw * 0.5, gy + gh + 16, "0.5", size=10, color=MUTED, anchor="middle"))
        p_frags.append(text(gx + gw, gy + gh + 16, "1.0", size=10, color=MUTED, anchor="middle"))

        p_frags.append(text(gx + gw / 2, gy + gh + 30, "Впевненість (Confidence)", size=11, color=INK, anchor="middle", bold=True))
        p_frags.append(text(gx - 32, gy + gh / 2, "Точність", size=11, color=INK, anchor="middle", bold=True))

        return "".join(p_frags)

    frags.append(draw_panel(p1_x, p1_y, "Некалібрована модель", "ECE = 18.4% (Надмірна впевненість)", False))
    frags.append(draw_panel(p2_x, p2_y, "Калібрована (Temperature Scaling)", "ECE = 1.9% (Ідеально узгоджена)", True))

    # Легенда внизу
    leg_y = H - 35
    frags.append(rect(140, leg_y - 12, 16, 12, fill="#93c5fd", stroke=NEG, sw=1.0, rx=2))
    frags.append(text(164, leg_y, "Точність у біні", size=11, color=INK, anchor="start"))

    frags.append(rect(300, leg_y - 12, 16, 12, fill="#fee2e2", stroke=POS, sw=0.8, rx=2))
    frags.append(text(324, leg_y, "Похибка (Calibration Gap)", size=11, color=INK, anchor="start"))

    frags.append(rect(520, leg_y - 12, 16, 12, fill="#86efac", stroke=FIELD, sw=1.0, rx=2))
    frags.append(text(544, leg_y, "Калібрована точність", size=11, color=INK, anchor="start"))

    frags.append(line(710, leg_y - 6, 735, leg_y - 6, color="#64748b", sw=1.5, dash="5,4"))
    frags.append(text(744, leg_y, "Ідеал (Acc = Conf)", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "reliability-diagram.svg"), W, H, *frags)


# ── 2. temperature-scaling-pipeline.svg: Конвеєр перетворення логітів ─────────
def fig_temperature_scaling_pipeline():
    W, H = 880, 360
    frags = []

    frags.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    frags.append(text(W / 2, 26, "Конвеєр калібрування логітів та прийняття рішень на борту", size=16, bold=True, color=INK))

    # 4 послідовні блоки у верхньому ряду
    # Блок 1: Сирі логіти
    b1_x, b1_y, b1_w, b1_h = 40, 65, 160, 95
    frags.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(b1_x + b1_w / 2, b1_y + 24, "Вихід нейромережі", size=13, bold=True, color=INK))
    frags.append(text(b1_x + b1_w / 2, b1_y + 46, "Сирі логіти z ∈ ℝᴷ", size=12, color=NEG, bold=True))
    frags.append(text(b1_x + b1_w / 2, b1_y + 72, "[ 4.8,  1.2, -0.9 ]", size=11, color=MUTED))

    # Стрілка 1 -> 2
    frags.append(arrow(b1_x + b1_w, b1_y + b1_h / 2, b1_x + b1_w + 35, b1_y + b1_h / 2, color="#475569", sw=1.8))

    # Блок 2: Температурне масштабування
    b2_x, b2_y, b2_w, b2_h = 235, 65, 175, 95
    frags.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(b2_x + b2_w / 2, b2_y + 24, "Масштабування T", size=13, bold=True, color=INK))
    frags.append(text(b2_x + b2_w / 2, b2_y + 46, "z' = z / T  (T = 2.4)", size=12, color=NEG, bold=True))
    frags.append(text(b2_x + b2_w / 2, b2_y + 72, "[ 2.0,  0.5, -0.375 ]", size=11, color=MUTED))

    # Стрілка 2 -> 3
    frags.append(arrow(b2_x + b2_w, b2_y + b2_h / 2, b2_x + b2_w + 35, b2_y + b2_h / 2, color="#475569", sw=1.8))

    # Блок 3: Softmax
    b3_x, b3_y, b3_w, b3_h = 445, 65, 175, 95
    frags.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(b3_x + b3_w / 2, b3_y + 24, "Стабільний Softmax", size=13, bold=True, color=INK))
    frags.append(text(b3_x + b3_w / 2, b3_y + 46, "pᵢ = e^(z'ᵢ) / ∑ e^(z'ⱼ)", size=12, color=FIELD, bold=True))
    frags.append(text(b3_x + b3_w / 2, b3_y + 72, "Впевненість p̂ = max(p)", size=11, color=MUTED))

    # Стрілка 3 -> 4
    frags.append(arrow(b3_x + b3_w, b3_y + b3_h / 2, b3_x + b3_w + 35, b3_y + b3_h / 2, color="#475569", sw=1.8))

    # Блок 4: Результат калібрування
    b4_x, b4_y, b4_w, b4_h = 655, 65, 185, 95
    frags.append(rect(b4_x, b4_y, b4_w, b4_h, fill="#faf5ff", stroke="#9333ea", sw=1.5, rx=6))
    frags.append(text(b4_x + b4_w / 2, b4_y + 24, "Калібровані ймовірності", size=13, bold=True, color=INK))
    frags.append(text(b4_x + b4_w / 2, b4_y + 46, "p̂ = 0.76  (було 0.97)", size=12, color="#9333ea", bold=True))
    frags.append(text(b4_x + b4_w / 2, b4_y + 72, "Клас: «Перешкода»", size=11, color=MUTED))

    # Нижній рівень: Логіка безпеки та порогового контролю
    # Стрілка вниз від Блоку 4 до блоку порівняння з порогом
    split_x = 747
    frags.append(arrow(split_x, b4_y + b4_h, split_x, 210, color="#475569", sw=1.8))

    # Блок порівняння з порогом
    dec_x, dec_y, dec_w, dec_h = 620, 215, 250, 50
    frags.append(rect(dec_x, dec_y, dec_w, dec_h, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(dec_x + dec_w / 2, dec_y + 22, "Перевірка порогу безпеки", size=12, bold=True, color=INK))
    frags.append(text(dec_x + dec_w / 2, dec_y + 39, "Чи виконується p̂ ≥ τ_safe (0.85)?", size=11, color="#b45309", bold=True))

    # Дві гілки рішень:
    # Гілка 1: ТАК (зелена, ліворуч)
    # Лінія вліво-вниз
    frags.append(line(dec_x, dec_y + dec_h / 2, 490, dec_y + dec_h / 2, color=FIELD, sw=1.8))
    frags.append(arrow(490, dec_y + dec_h / 2, 490, 290, color=FIELD, sw=1.8))
    frags.append(text(555, dec_y + dec_h / 2 - 8, "ТАК (p̂ ≥ 0.85)", size=11, bold=True, color=FIELD))

    act_x, act_y, act_w, act_h = 370, 295, 240, 50
    frags.append(rect(act_x, act_y, act_w, act_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(act_x + act_w / 2, act_y + 20, "Штатне виконання маневру", size=12, bold=True, color=INK))
    frags.append(text(act_x + act_w / 2, act_y + 38, "Керування віддано ML-моделі", size=11, color=FIELD))

    # Гілка 2: НІ (червона, праворуч)
    frags.append(arrow(split_x, dec_y + dec_h, split_x, 290, color=POS, sw=1.8))
    frags.append(text(split_x + 12, dec_y + dec_h + 18, "НІ (p̂ < 0.85)", size=11, bold=True, color=POS, anchor="start"))

    fb_x, fb_y, fb_w, fb_h = 635, 295, 230, 50
    frags.append(rect(fb_x, fb_y, fb_w, fb_h, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(fb_x + fb_w / 2, fb_y + 20, "Активація бекап-сенсорів", size=12, bold=True, color=INK))
    frags.append(text(fb_x + fb_w / 2, fb_y + 38, "Лідар / Сонар / Захисна зупинка", size=11, color=POS))

    # Додатковий інформаційний блок зліва знизу
    info_x, info_y, info_w, info_h = 40, 215, 300, 130
    frags.append(rect(info_x, info_y, info_w, info_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(info_x + info_w / 2, info_y + 22, "Ключова властивість T-Scaling", size=12, bold=True, color=INK))
    frags.append(text(info_x + 15, info_y + 46, "• Точність (argmax) не змінюється:", size=11, color=INK, anchor="start"))
    frags.append(text(info_x + 25, info_y + 64, "argmax(z/T) ≡ argmax(z)", size=11, color=NEG, anchor="start", bold=True))
    frags.append(text(info_x + 15, info_y + 86, "• Усуває фальшиву впевненість:", size=11, color=INK, anchor="start"))
    frags.append(text(info_x + 25, info_y + 104, "захищає від хибних спрацювань", size=11, color=POS, anchor="start"))

    render(os.path.join(OUT, "temperature-scaling-pipeline.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_reliability_diagram()
    fig_temperature_scaling_pipeline()
