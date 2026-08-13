# -*- coding: utf-8 -*-
"""Фігури до теми «Часовий розкид (delay spread) і частота когерентності».
Запуск: python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ACCENT = "#d35400"  # Помаранчевий для акцентів
BLUE_ACCENT = "#2980b9"
GREEN_ACCENT = "#27ae60"
RED_ACCENT = "#c0392b"
MUTED_GRID = "#eef1f5"

def svg_path(d, fill="none", stroke=LINE, sw=1.5, opacity=1.0, dash=None):
    op_str = f' opacity="{opacity:.2f}"' if opacity < 1.0 else ''
    dash_str = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{op_str}{dash_str}/>'

# ── 1. Профіль затримки потужності (PDP) та параметри розкиду ──────────────
def fig_pdp_concept():
    """PDP: імпульсна відповідь каналу, середня затримка tau_bar, RMS delay spread sigma_tau та tau_max."""
    W, H = 760, 430
    f = []

    f.append(text(W / 2, 28, "Профіль затримки потужності (PDP) та часові параметри каналу", size=15, bold=True, color=INK))

    gx0, gy0, gw, gh = 85, 340, 620, 240

    # Осі
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=MUTED, sw=1.5))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=MUTED, sw=1.5))
    f.append(text(gx0 + gw + 15, gy0 + 4, "τ (нс)", size=12, bold=True, color=INK))
    f.append(text(gx0 - 15, gy0 - gh - 12, "P(τ) (дБм)", size=12, bold=True, color=INK))

    # Сітка
    for i in range(1, 5):
        y = gy0 - i * (gh / 5)
        f.append(line(gx0, y, gx0 + gw, y, color=MUTED_GRID, sw=1.0, dash="4 4"))

    # Поріг відсічки
    y_thresh = gy0 - 35
    f.append(line(gx0, y_thresh, gx0 + gw, y_thresh, color="#bdc3c7", sw=1.2, dash="6 4"))
    f.append(text(gx0 + gw - 80, y_thresh - 6, "поріг відсічки (-20 дБ)", size=10, color=MUTED))

    # Компоненти багатопроменевості: (tau_x, power_height)
    rays = [
        (40,  210),
        (90,  150),
        (130, 180),
        (190, 110),
        (250, 75),
        (330, 48),
        (410, 38)
    ]

    for tau_x, p_h in rays:
        x = gx0 + tau_x
        y = gy0 - p_h
        # Вертикальна імпульсна лінія з кружечком нагорі
        f.append(line(x, gy0, x, y, color=BLUE_ACCENT, sw=2.5))
        f.append(circle(x, y, 4, fill=BLUE_ACCENT, stroke="#ffffff", sw=1.5))

    # Затінений обвід PDP (огинаюча)
    pdp_pts = [(gx0 + r[0], gy0 - r[1]) for r in rays]
    env_path = f"M {gx0},{gy0} L {pdp_pts[0][0]},{pdp_pts[0][1]} " + " ".join([f"L {pt[0]},{pt[1]}" for pt in pdp_pts]) + f" L {pdp_pts[-1][0]},{gy0} Z"
    f.append(svg_path(env_path, fill="#3498db", opacity=0.1, stroke="none"))

    # Маркування tau_bar (середня затримка) і sigma_tau (RMS delay spread)
    x_mean = gx0 + 160
    f.append(line(x_mean, gy0 + 5, x_mean, gy0 - gh + 30, color=ACCENT, sw=1.8, dash="5 3"))
    f.append(text(x_mean, gy0 - gh + 20, "τ̄ (середня затримка)", size=11, bold=True, color=ACCENT, anchor="middle"))

    # Двостороння стрілка для sigma_tau
    x_s1 = x_mean - 60
    x_s2 = x_mean + 60
    y_sig = gy0 - 160
    f.append(line(x_s1, y_sig, x_s2, y_sig, color=GREEN_ACCENT, sw=2.0))
    f.append(line(x_s1, y_sig - 5, x_s1, y_sig + 5, color=GREEN_ACCENT, sw=1.5))
    f.append(line(x_s2, y_sig - 5, x_s2, y_sig + 5, color=GREEN_ACCENT, sw=1.5))
    f.append(text(x_mean, y_sig - 8, "2 · σ_τ (RMS delay spread)", size=11, bold=True, color=GREEN_ACCENT, anchor="middle"))

    # Двостороння стрілка для tau_max (максимальний розкид)
    x_first = gx0 + rays[0][0]
    x_last = gx0 + rays[-1][0]
    y_max = gy0 + 25
    f.append(line(x_first, y_max, x_last, y_max, color=RED_ACCENT, sw=1.8))
    f.append(line(x_first, y_max - 5, x_first, y_max + 5, color=RED_ACCENT, sw=1.5))
    f.append(line(x_last, y_max - 5, x_last, y_max + 5, color=RED_ACCENT, sw=1.5))
    f.append(text((x_first + x_last) / 2, y_max + 18, "τ_max (максимальний розкид затримок)", size=11, bold=True, color=RED_ACCENT, anchor="middle"))

    render(os.path.join(IMG, "pdp-concept.svg"), W, H, *f)


# ── 2. Частотна характеристика каналу H(f) та когерентна смуга B_c ────────
def fig_frequency_selectivity():
    """Порівняння вузькосмугового (плоске завмирання) та широкосмугового (селективне завмирання) сигналу."""
    W, H = 760, 440
    f = []

    f.append(text(W / 2, 28, "Частотна передавальна функція каналу |H(f)| та смуга когерентності B_c", size=15, bold=True, color=INK))

    gx0, gy0, gw, gh = 85, 340, 620, 240

    # Осі
    f.append(line(gx0, gy0, gx0 + gw, gy0, color=MUTED, sw=1.5))
    f.append(line(gx0, gy0, gx0, gy0 - gh, color=MUTED, sw=1.5))
    f.append(text(gx0 + gw + 15, gy0 + 4, "f (МГц)", size=12, bold=True, color=INK))
    f.append(text(gx0 - 15, gy0 - gh - 12, "|H(f)|", size=12, bold=True, color=INK))

    # Генерація викривленої кривої H(f)
    pts = []
    steps = 200
    for i in range(steps + 1):
        x_val = i / steps
        x_px = gx0 + x_val * gw
        val = 0.55 + 0.3 * math.sin(2 * math.pi * x_val * 2.5) + 0.15 * math.cos(2 * math.pi * x_val * 5.0)
        val = max(0.08, min(0.95, val))
        y_px = gy0 - val * gh
        pts.append((x_px, y_px))

    path_h = "M " + " L ".join([f"{p[0]:.1f},{p[1]:.1f}" for p in pts])
    f.append(svg_path(path_h, fill="none", stroke=BLUE_ACCENT, sw=2.5))

    # Смуга когерентності B_c між першим піком і наступним
    x_peak1 = gx0 + gw * 0.1
    x_peak2 = gx0 + gw * 0.5
    y_bc = gy0 - gh - 5

    f.append(line(x_peak1, gy0, x_peak1, gy0 - gh, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(x_peak2, gy0, x_peak2, gy0 - gh, color=MUTED, sw=1.0, dash="3 3"))
    f.append(line(x_peak1, y_bc, x_peak2, y_bc, color=ACCENT, sw=2.0))
    f.append(line(x_peak1, y_bc - 4, x_peak1, y_bc + 4, color=ACCENT, sw=1.5))
    f.append(line(x_peak2, y_bc - 4, x_peak2, y_bc + 4, color=ACCENT, sw=1.5))
    f.append(text((x_peak1 + x_peak2) / 2, y_bc - 8, "B_c ≈ 1 / σ_τ (смуга когерентності)", size=11, bold=True, color=ACCENT, anchor="middle"))

    # Випадок 1: Вузькосмуговий сигнал B_s << B_c (плоске завмирання)
    xs1_center = gx0 + gw * 0.12
    bw1 = 45
    f.append(rect(xs1_center - bw1/2, gy0 - gh * 0.85, bw1, gh * 0.85, fill="#27ae60", stroke=GREEN_ACCENT, sw=1.5, rx=4))
    f.append(text(xs1_center, gy0 + 24, "Вузький сигнал (B_s << B_c)\nПлоске завмирання", size=10, bold=True, color=GREEN_ACCENT, anchor="middle"))

    # Випадок 2: Широкосмуговий сигнал B_s > B_c (частотно-селективне завмирання)
    xs2_center = gx0 + gw * 0.65
    bw2 = 280
    f.append(rect(xs2_center - bw2/2, gy0 - gh * 0.85, bw2, gh * 0.85, fill="#e74c3c", stroke=RED_ACCENT, sw=1.5, rx=4))
    f.append(text(xs2_center, gy0 + 24, "Широкий сигнал (B_s > B_c)\nЧастотно-селективне завмирання", size=10, bold=True, color=RED_ACCENT, anchor="middle"))

    render(os.path.join(IMG, "frequency-selectivity.svg"), W, H, *f)


# ── 3. Часовий розкид і виникнення міжсимвольної інтерференції (ISI) ──────
def fig_isi_mechanism():
    """Демонстрація виникнення ISI при скороченні періоду символу T_s порівняно з tau_max."""
    W, H = 760, 420
    f = []

    f.append(text(W / 2, 26, "Часовий розкид і виникнення міжсимвольної інтерференції (ISI)", size=15, bold=True, color=INK))

    # Верхня панель: Повільна передача (T_s >> tau_max)
    f.append(text(50, 60, "А. Повільна швидкість передачі (T_s >> τ_max): Немає ISI", size=12, bold=True, color=GREEN_ACCENT, anchor="start"))

    y_base1 = 150
    # Символ 1
    f.append(rect(60, y_base1 - 60, 150, 60, fill="#eafaf1", stroke=GREEN_ACCENT, sw=1.8))
    f.append(text(135, y_base1 - 30, "Символ 1 (T_s)", size=11, bold=True, color=GREEN_ACCENT, anchor="middle"))

    # Хвіст затримки символу 1 (луна)
    f.append(svg_path(f"M 210,{y_base1} L 210,{y_base1 - 50} Q 250,{y_base1 - 10} 290,{y_base1} Z", fill="#fef5e7", stroke=ACCENT, sw=1.5, opacity=0.8, dash="3 2"))
    f.append(text(250, y_base1 - 65, "луна (τ_max)", size=10, bold=True, color=ACCENT, anchor="middle"))

    # Символ 2
    f.append(rect(310, y_base1 - 60, 150, 60, fill="#eafaf1", stroke=GREEN_ACCENT, sw=1.8))
    f.append(text(385, y_base1 - 30, "Символ 2 (T_s)", size=11, bold=True, color=GREEN_ACCENT, anchor="middle"))

    # Пояснення
    f.append(text(500, y_base1 - 25, "Луна від Символу 1 згасає\nДО початку Символу 2", size=10, color=MUTED, anchor="start"))

    # Розділювальна лінія
    f.append(line(50, 185, 710, 185, color=MUTED, sw=1.0, dash="4 4"))

    # Нижня панель: Швидка передача (T_s < tau_max)
    f.append(text(50, 215, "Б. Висока швидкість передачі (T_s < τ_max): Сильна ISI", size=12, bold=True, color=RED_ACCENT, anchor="start"))

    y_base2 = 340
    # Символ 1
    f.append(rect(60, y_base2 - 60, 75, 60, fill="#fadbd8", stroke=RED_ACCENT, sw=1.8))
    f.append(text(97, y_base2 - 30, "Симв 1", size=11, bold=True, color=RED_ACCENT, anchor="middle"))

    # Довгий хвіст луни символу 1
    f.append(svg_path(f"M 135,{y_base2} L 135,{y_base2 - 50} C 175,{y_base2 - 40} 235,{y_base2 - 25} 315,{y_base2} Z", fill="#fdebd0", stroke=ACCENT, sw=1.5, opacity=0.8))

    # Символ 2
    f.append(rect(145, y_base2 - 60, 75, 60, fill="#fadbd8", stroke=RED_ACCENT, sw=1.8))
    f.append(text(182, y_base2 - 30, "Симв 2", size=11, bold=True, color=RED_ACCENT, anchor="middle"))

    # Символ 3
    f.append(rect(230, y_base2 - 60, 75, 60, fill="#fadbd8", stroke=RED_ACCENT, sw=1.8))
    f.append(text(267, y_base2 - 30, "Симв 3", size=11, bold=True, color=RED_ACCENT, anchor="middle"))

    # Текст пояснення праворуч
    f.append(text(340, y_base2 - 35, "Запізніла луна τ_max > T_s\nЗона ISI: хвіст Символу 1\nспотворює Символ 2 і Символ 3!", size=10, bold=True, color=RED_ACCENT, anchor="start"))

    render(os.path.join(IMG, "isi-mechanism.svg"), W, H, *f)


# ── 4. Захисний інтервал та циклічний префікс (CP) в OFDM ──────────────────
def fig_ofdm_cp_remedy():
    """Як циклічний префікс (CP) поглинає tau_max і усуває міжсимвольну інтерференцію."""
    W, H = 760, 380
    f = []

    f.append(text(W / 2, 28, "Подолання часового розкиду: Циклічний префікс (CP) в OFDM", size=15, bold=True, color=INK))

    # Переданий символ OFDM
    y0 = 120
    f.append(text(50, y0 - 30, "Структура переданого OFDM-символу (тривалість T_sym = T_CP + T_sub):", size=11, bold=True, color=INK, anchor="start"))

    # Блок CP
    f.append(rect(60, y0, 140, 55, fill="#fef5e7", stroke=ACCENT, sw=2.0))
    f.append(text(130, y0 + 33, "CP (копія хвоста)", size=11, bold=True, color=ACCENT, anchor="middle"))

    # Корисна частина T_sub
    f.append(rect(200, y0, 480, 55, fill="#ebf5fb", stroke=BLUE_ACCENT, sw=2.0))
    f.append(text(440, y0 + 33, "Корисна частина символу T_sub (відліки IFFT)", size=11, bold=True, color=BLUE_ACCENT, anchor="middle"))

    # Стрілка копіювання з хвоста в CP
    f.append(svg_path(f"M 620,{y0} C 620,{y0 - 25} 130,{y0 - 25} 130,{y0}", fill="none", stroke=ACCENT, sw=1.8, dash="4 3"))
    f.append(text(370, y0 - 22, "циклічне копіювання (захист ортогональності)", size=10, color=ACCENT, anchor="middle"))

    # Прийнятий символ з луною від попереднього символу
    y1 = 260
    f.append(text(50, y1 - 30, "Прийнятий символ у разі часового розкиду затримок τ_max ≤ T_CP:", size=11, bold=True, color=INK, anchor="start"))

    # Зона спотворення від запізнілої луни попереднього символу
    f.append(rect(60, y1, 100, 55, fill="#fadbd8", stroke=RED_ACCENT, sw=1.8))
    f.append(text(110, y1 + 33, "ISI від τ_max", size=10, bold=True, color=RED_ACCENT, anchor="middle"))

    # Решта CP
    f.append(rect(160, y1, 40, 55, fill="#fef5e7", stroke=ACCENT, sw=1.5))

    # Вікно ДПФ/FFT у приймачі
    f.append(rect(200, y1, 480, 55, fill="#eafaf1", stroke=GREEN_ACCENT, sw=2.2))
    f.append(text(440, y1 + 33, "Вікно обробки FFT приймача (абсолютно чисте від ISI!)", size=11, bold=True, color=GREEN_ACCENT, anchor="middle"))

    # Пояснення умови T_CP > tau_max
    f.append(line(60, y1 + 65, 160, y1 + 65, color=RED_ACCENT, sw=2.0))
    f.append(text(110, y1 + 82, "τ_max", size=11, bold=True, color=RED_ACCENT, anchor="middle"))

    f.append(line(60, y1 + 95, 200, y1 + 95, color=ACCENT, sw=2.0))
    f.append(text(130, y1 + 112, "T_CP (тривалість CP)", size=11, bold=True, color=ACCENT, anchor="middle"))

    f.append(text(380, y1 + 95, "Умова відсутності ISI: T_CP ≥ τ_max", size=12, bold=True, color=GREEN_ACCENT, anchor="start"))

    render(os.path.join(IMG, "ofdm-cp-remedy.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pdp_concept()
    fig_frequency_selectivity()
    fig_isi_mechanism()
    fig_ofdm_cp_remedy()
    print("Фігури успішно згенеровано у ./img/")
