# -*- coding: utf-8 -*-
"""Фігури до статті «Дискретне перетворення Фур'є над скінченними полями»."""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Порівняння комплексного ДПФ (неперервне коло) та NTT (дискретне поле)
# ─────────────────────────────────────────────────────────────────────────────
def fig_ntt_vs_fft_circle():
    W, H = 840, 430
    frby = []

    # Фон
    frby.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    # Панель 1 (Ліва): Комплексне ДПФ над C
    bx1, by1, bw, bh = 30, 40, 370, 360
    frby.append(rect(bx1, by1, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(bx1 + bw / 2, by1 + 28, "Комплексне ДПФ над полем C", size=14, bold=True, color=INK))

    cx1, cy1, r1 = bx1 + bw / 2, by1 + 175, 95
    # Осі координат
    frby.append(line(cx1 - 120, cy1, cx1 + 120, cy1, color=MUTED, sw=1.2))
    frby.append(line(cx1, cy1 + 120, cx1, cy1 - 120, color=MUTED, sw=1.2))
    frby.append(text(cx1 + 128, cy1 + 4, "Re", size=12, bold=True, color=MUTED))
    frby.append(text(cx1 - 4, cy1 - 126, "Im", size=12, bold=True, color=MUTED))

    # Коло
    frby.append(f'<circle cx="{cx1}" cy="{cy1}" r="{r1}" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 4"/>')

    # 8 точок комплексних коренів
    pts_labels = [
        "1.0",
        "0.707 - 0.707i",
        "-i",
        "-0.707 - 0.707i",
        "-1.0",
        "-0.707 + 0.707i",
        "i",
        "0.707 + 0.707i"
    ]
    for k in range(8):
        angle = -2 * math.pi * k / 8
        px = cx1 + r1 * math.cos(angle)
        py = cy1 + r1 * math.sin(angle)
        frby.append(circle(px, py, 4.5, fill=NEG, stroke=INK, sw=1.2))

    # Пояснення проблем під колом
    frby.append(text(bx1 + bw / 2, by1 + bh - 48, "Експоненти e^(-i 2pi k / n) трансцендентні", size=12, color=POS))
    frby.append(text(bx1 + bw / 2, by1 + bh - 28, "Похибка округлення IEEE 754 накопичується", size=11, color=MUTED))
    frby.append(text(bx1 + bw / 2, by1 + bh - 12, "Непридатне для точної криптографії", size=11, bold=True, color=POS))

    # Панель 2 (Права): Теоретико-числове перетворення (NTT) над GF(p)
    bx2, by2 = 440, 40
    frby.append(rect(bx2, by2, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(bx2 + bw / 2, by2 + 28, "NTT над скінченним полем GF(17)", size=14, bold=True, color=INK))

    cx2, cy2 = bx2 + bw / 2, by1 + 175
    # Дискретне циклічне кільце
    frby.append(circle(cx2, cy2, r1, fill="none", stroke=FIELD, sw=2))

    # 4 точки коренів степеня n = 4 у GF(17), де w = 4
    ntt_pts = [
        (0, "w^0 = 1", 1, 0, "#1e293b"),
        (1, "w^1 = 4", 0, 1, FIELD),
        (2, "w^2 = 16", -1, 0, POS),
        (3, "w^3 = 13", 0, -1, NEG)
    ]
    for idx, lbl, dx, dy, col in ntt_pts:
        px = cx2 + r1 * dx
        py = cy2 + r1 * dy
        frby.append(circle(px, py, 6, fill=col, stroke=INK, sw=1.5))
        # Зсув мітки
        lx = px + dx * 34
        ly = py + dy * 20 + 4
        frby.append(text(lx, ly, lbl, size=12, bold=True, color=col))

    # Стрілка напрямку циклу
    frby.append(text(cx2, cy2, "w^4 = 1 mod 17", size=13, bold=True, color=INK))

    frby.append(text(bx2 + bw / 2, by2 + bh - 48, "Первісний корінь w = 4 породжує групу", size=12, color=FIELD))
    frby.append(text(bx2 + bw / 2, by2 + bh - 28, "Суворо точна модульна арифметика", size=11, color=MUTED))
    frby.append(text(bx2 + bw / 2, by2 + bh - 12, "Нульова похибка обчислень: 100% точність", size=11, bold=True, color=FIELD))

    render(os.path.join(OUT, "ntt-vs-fft-circle.svg"), W, H, *frby,
           title="Порівняння комплексного ДПФ та числового перетворення над скінченним полем")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Метелики Кулі — Тьюкі над скінченним полем (DIF та DIT)
# ─────────────────────────────────────────────────────────────────────────────
def fig_ntt_butterfly_dif_dit():
    W, H = 840, 360
    frby = []

    # Фон
    frby.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    # Заголовок
    frby.append(text(W / 2, 36, "Базові обчислювальні метелики алгоритму Кулі — Тьюкі над полем GF(p)", size=15, bold=True, color=INK))

    # Блок 1: DIT (Decimation-in-Time)
    bx1, by1, bw, bh = 40, 60, 360, 265
    frby.append(rect(bx1, by1, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(bx1 + bw / 2, by1 + 26, "Метелик DIT (проріджування за часом)", size=13, bold=True, color=INK))

    # Лінії DIT
    y_top = by1 + 75
    y_bot = by1 + 165
    x_in = bx1 + 45
    x_mid = bx1 + 180
    x_out = bx1 + 315

    # Вхідні мітки
    frby.append(text(x_in - 12, y_top + 4, "u", size=14, bold=True, color=INK))
    frby.append(text(x_in - 12, y_bot + 4, "v", size=14, bold=True, color=INK))

    # Лінії
    frby.append(line(x_in, y_top, x_mid, y_top, color=LINE, sw=1.8))
    frby.append(line(x_in, y_bot, x_in + 60, y_bot, color=LINE, sw=1.8))

    # Множення на поворотний коефіцієнт
    frby.append(rect(x_in + 60, y_bot - 16, 55, 32, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
    frby.append(text(x_in + 87, y_bot + 5, "x w^k", size=12, bold=True, color=NEG))
    frby.append(line(x_in + 115, y_bot, x_mid, y_bot, color=LINE, sw=1.8))

    # Перехрестя
    frby.append(line(x_mid, y_top, x_out - 45, y_top, color=LINE, sw=1.8))
    frby.append(line(x_mid, y_bot, x_out - 45, y_top, color=LINE, sw=1.8))
    frby.append(line(x_mid, y_top, x_out - 45, y_bot, color=LINE, sw=1.8))
    frby.append(line(x_mid, y_bot, x_out - 45, y_bot, color=LINE, sw=1.8))

    frby.append(text(x_mid + 75, y_bot + 18, "-1", size=12, bold=True, color=POS))

    # Вихідні мітки
    frby.append(line(x_out - 45, y_top, x_out, y_top, color=LINE, sw=1.8))
    frby.append(line(x_out - 45, y_bot, x_out, y_bot, color=LINE, sw=1.8))

    frby.append(text(x_out + 4, y_top - 8, "u + v * w^k mod p", size=11, bold=True, color=FIELD, anchor="start"))
    frby.append(text(x_out + 4, y_bot + 16, "u - v * w^k mod p", size=11, bold=True, color=POS, anchor="start"))

    frby.append(text(bx1 + bw / 2, by1 + bh - 24, "Використовується в прямому NTT", size=11, color=MUTED))
    frby.append(text(bx1 + bw / 2, by1 + bh - 8, "1 множення, 1 додавання, 1 віднімання", size=11, color=MUTED))

    # Блок 2: DIF (Decimation-in-Frequency)
    bx2, by2 = 440, 60
    frby.append(rect(bx2, by2, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(bx2 + bw / 2, by2 + 26, "Метелик DIF (проріджування за частотою)", size=13, bold=True, color=INK))

    x2_in = bx2 + 45
    x2_mid = bx2 + 155
    x2_mul = bx2 + 230
    x2_out = bx2 + 315

    # Вхідні мітки
    frby.append(text(x2_in - 12, y_top + 4, "u", size=14, bold=True, color=INK))
    frby.append(text(x2_in - 12, y_bot + 4, "v", size=14, bold=True, color=INK))

    # Перехрестя спочатку
    frby.append(line(x2_in, y_top, x2_mid, y_top, color=LINE, sw=1.8))
    frby.append(line(x2_in, y_bot, x2_mid, y_top, color=LINE, sw=1.8))
    frby.append(line(x2_in, y_top, x2_mid, y_bot, color=LINE, sw=1.8))
    frby.append(line(x2_in, y_bot, x2_mid, y_bot, color=LINE, sw=1.8))

    frby.append(text(x2_in + 75, y_bot + 18, "-1", size=12, bold=True, color=POS))

    # Верхня гілка прямо
    frby.append(line(x2_mid, y_top, x2_out, y_top, color=LINE, sw=1.8))

    # Нижня гілка через блок множення
    frby.append(line(x2_mid, y_bot, x2_mul - 25, y_bot, color=LINE, sw=1.8))
    frby.append(rect(x2_mul - 25, y_bot - 16, 55, 32, fill="#eef2f7", stroke=LINE, sw=1.2, rx=4))
    frby.append(text(x2_mul + 2, y_bot + 5, "x w^k", size=12, bold=True, color=NEG))
    frby.append(line(x2_mul + 30, y_bot, x2_out, y_bot, color=LINE, sw=1.8))

    # Вихідні мітки
    frby.append(text(x2_out + 4, y_top - 8, "u + v mod p", size=11, bold=True, color=FIELD, anchor="start"))
    frby.append(text(x2_out + 4, y_bot + 16, "(u - v) * w^k mod p", size=11, bold=True, color=POS, anchor="start"))

    frby.append(text(bx2 + bw / 2, by2 + bh - 24, "Використовується в оберненому INTT", size=11, color=MUTED))
    frby.append(text(bx2 + bw / 2, by2 + bh - 8, "Пара DIF + DIT усуває перестановку бітів", size=11, color=MUTED))

    render(os.path.join(OUT, "ntt-butterfly-dif-dit.svg"), W, H, *frby,
           title="Базові метелики DIT та DIF для обчислення NTT")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Конвеєр швидкого множення многочленів через NTT
# ─────────────────────────────────────────────────────────────────────────────
def fig_polynomial_mult_flow():
    W, H = 840, 430
    frby = []

    # Фон
    frby.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))

    frby.append(text(W / 2, 38, "Конвеєр швидкого множення многочленів за теоремою про згортку", size=15, bold=True, color=INK))

    # Крок 1: Вхідні многочлени
    frby.append(rect(35, 75, 175, 95, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frby.append(text(122, 102, "Вхідні коефіцієнти", size=12, bold=True, color=INK))
    frby.append(text(122, 125, "A(x) = [a_0, ..., a_d]", size=11, color=MUTED))
    frby.append(text(122, 145, "B(x) = [b_0, ..., b_d]", size=11, color=MUTED))

    # Стрілка 1 -> Доповнення нулями
    frby.append(arrow(210, 122, 245, 122, color=LINE, sw=1.8))

    # Крок 2: Доповнення нулями (Zero-padding)
    frby.append(rect(245, 75, 155, 95, fill="#eef2f7", stroke=LINE, sw=1.2, rx=6))
    frby.append(text(322, 102, "Доповнення N >= 2d+1", size=12, bold=True, color=POS))
    frby.append(text(322, 125, "Паддинг нулями", size=11, color=MUTED))
    frby.append(text(322, 145, "усуває циклічність", size=11, color=MUTED))

    # Стрілка 2 -> Пряме NTT
    frby.append(arrow(400, 122, 435, 122, color=LINE, sw=1.8))

    # Крок 3: Пряме NTT
    frby.append(rect(435, 75, 170, 95, fill="#eaf6ee", stroke=FIELD, sw=1.5, rx=6))
    frby.append(text(520, 102, "Пряме перетворення", size=12, bold=True, color=FIELD))
    frby.append(text(520, 125, "NTT(A) -> A_hat", size=11, bold=True, color=INK))
    frby.append(text(520, 145, "NTT(B) -> B_hat", size=11, bold=True, color=INK))

    # Стрілка 3 -> Спектральне множення
    frby.append(arrow(605, 122, 640, 122, color=LINE, sw=1.8))

    # Крок 4: Поточкове множення
    frby.append(rect(640, 75, 165, 95, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=6))
    frby.append(text(722, 102, "Частотна область", size=12, bold=True, color="#c026d3"))
    frby.append(text(722, 125, "C_hat[k] = A_hat[k] * B_hat[k]", size=10, bold=True, color=INK))
    frby.append(text(722, 145, "O(N) множень у GF(p)", size=11, color=FIELD))

    # Стрілка вниз до оберненого перетворення
    frby.append(arrow(722, 170, 722, 235, color=LINE, sw=1.8))

    # Крок 5: Обернене INTT
    frby.append(rect(435, 235, 370, 85, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frby.append(text(620, 262, "Обернене перетворення INTT", size=13, bold=True, color=NEG))
    frby.append(text(620, 285, "c = INTT(C_hat) = [c_0, c_1, ..., c_{2d}] mod p", size=11, bold=True, color=INK))
    frby.append(text(620, 305, "Складова відновлення: ділення на N mod p", size=11, color=MUTED))

    # Стрілка вліво до фінального результату
    frby.append(arrow(435, 277, 260, 277, color=LINE, sw=1.8))

    # Крок 6: Фінальний многочлен
    frby.append(rect(35, 235, 225, 85, fill="#f8fafc", stroke=FIELD, sw=1.8, rx=6))
    frby.append(text(147, 262, "Добуток многочленів", size=13, bold=True, color=FIELD))
    frby.append(text(147, 285, "C(x) = A(x) * B(x) mod p", size=12, bold=True, color=INK))
    frby.append(text(147, 305, "Загальна складність O(N log N)", size=11, bold=True, color=FIELD))

    # Нижній банер складності
    frby.append(rect(35, 345, 770, 55, fill="#f1f5f9", stroke=LINE, sw=1, rx=6))
    frby.append(text(W / 2, 368, "Порівняння: наївне множення O(N^2) проти NTT-множення O(N log N)", size=12, bold=True, color=INK))
    frby.append(text(W / 2, 386, "Для N = 4096: ~16 700 000 операцій скорочуються до ~49 000 операцій (прискорення > 340 разів)", size=11, color=MUTED))

    render(os.path.join(OUT, "polynomial-mult-flow.svg"), W, H, *frby,
           title="Конвеєр множення многочленів за теоремою про згортку")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: NTT у постквантовій криптографії та кільцях Z_q[x]/(x^n + 1)
# ─────────────────────────────────────────────────────────────────────────────
def fig_lattice_ring_ntt():
    W, H = 840, 390
    frby = []

    frby.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frby.append(text(W / 2, 38, "Кільцевий NTT (Negacyclic NTT) у схемах ML-KEM (Kyber) та ML-DSA (Dilithium)", size=14, bold=True, color=INK))

    # Лівий блок: Кільце R_q
    bx1, by1, bw1, bh1 = 40, 70, 320, 270
    frby.append(rect(bx1, by1, bw1, bh1, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(bx1 + bw1 / 2, by1 + 26, "Кільце многочленів R_q", size=13, bold=True, color=INK))
    frby.append(text(bx1 + bw1 / 2, by1 + 48, "R_q = Z_q[x] / (x^n + 1)", size=12, bold=True, color=POS))

    frby.append(line(bx1 + 20, by1 + 62, bx1 + bw1 - 20, by1 + 62, color=LINE, sw=1))

    frby.append(text(bx1 + bw1 / 2, by1 + 88, "Коефіцієнти многочлена a(x):", size=11, color=MUTED))
    frby.append(text(bx1 + bw1 / 2, by1 + 108, "a_0 + a_1 x + ... + a_{n-1} x^{n-1}", size=11, bold=True, color=INK))

    frby.append(text(bx1 + bw1 / 2, by1 + 140, "Множення містить редукцію:", size=11, color=MUTED))
    frby.append(text(bx1 + bw1 / 2, by1 + 160, "x^n = -1 (негациклічна згортка)", size=12, bold=True, color=POS))

    frby.append(text(bx1 + bw1 / 2, by1 + 200, "Параметри Kyber: n = 256, q = 3329", size=11, bold=True, color=FIELD))
    frby.append(text(bx1 + bw1 / 2, by1 + 220, "256-вимірний ґратковий простір", size=11, color=MUTED))
    frby.append(text(bx1 + bw1 / 2, by1 + 245, "Пряме множення: 65 536 операцій", size=11, color=MUTED))

    # Стрілка між блоками (Ізоморфізм за китайською теоремою про залишки)
    frby.append(arrow(360, 205, 480, 205, color=FIELD, sw=2))
    frby.append(text(420, 185, "Ізоморфізм CRT", size=12, bold=True, color=FIELD))
    frby.append(text(420, 225, "через NTT", size=11, color=MUTED))

    # Правий блок: Розклад на лінійні/квадратичні множники
    bx2, by2, bw2, bh2 = 480, 70, 320, 270
    frby.append(rect(bx2, by2, bw2, bh2, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    frby.append(text(bx2 + bw2 / 2, by2 + 26, "Спектральна база (NTT-образ)", size=13, bold=True, color=INK))
    frby.append(text(bx2 + bw2 / 2, by2 + 48, "Прямий добуток полів GF(q)", size=12, bold=True, color=FIELD))

    frby.append(line(bx2 + 20, by2 + 62, bx2 + bw2 - 20, by2 + 62, color=LINE, sw=1))

    frby.append(text(bx2 + bw2 / 2, by2 + 88, "n незалежних точок оцінки:", size=11, color=MUTED))
    frby.append(text(bx2 + bw2 / 2, by2 + 108, "(a_hat_0, a_hat_1, ..., a_hat_{n-1})", size=11, bold=True, color=INK))

    frby.append(text(bx2 + bw2 / 2, by2 + 140, "Множення стає паралельним:", size=11, color=MUTED))
    frby.append(text(bx2 + bw2 / 2, by2 + 160, "c_hat_i = a_hat_i * b_hat_i mod q", size=12, bold=True, color=FIELD))

    frby.append(text(bx2 + bw2 / 2, by2 + 200, "256 скалярних множень mod 3329", size=11, bold=True, color=FIELD))
    frby.append(text(bx2 + bw2 / 2, by2 + 220, "Повна відсутність залежностей даних", size=11, color=MUTED))
    frby.append(text(bx2 + bw2 / 2, by2 + 245, "Ідеальна векторна оптимізація AVX2 / NEON", size=11, bold=True, color=NEG))

    render(os.path.join(OUT, "lattice-ring-ntt.svg"), W, H, *frby,
           title="Негациклічний NTT у постквантовій ґратковій криптографії")


if __name__ == "__main__":
    fig_ntt_vs_fft_circle()
    fig_ntt_butterfly_dif_dit()
    fig_polynomial_mult_flow()
    fig_lattice_ring_ntt()
    print("Всі 4 фігури успішно згенеровано.")
