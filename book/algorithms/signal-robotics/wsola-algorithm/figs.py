# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. wsola-vs-sola-synthesis: порівняння архітектури SOLA та WSOLA ──────────
# У SOLA шаблон береться з вихідного сигналу (накопичення похибки й фазовий дрейф),
# у WSOLA шаблон завжди береться з первинного входу (збереження природного кроку).
def fig_wsola_vs_sola_synthesis():
    W, H = 760, 430
    p = []

    # Заголовок та фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # ── Верхній блок: SOLA ──
    p.append(rect(25, 25, W - 50, 180, fill="#fff8f8", stroke=POS, sw=1.4, rx=6))
    p.append(text(45, 52, "SOLA (Synchronized Overlap-Add): шаблон береться з накопиченого виходу", size=13, color=POS, bold=True, anchor="start"))

    # Вхідний потік SOLA
    p.append(rect(45, 75, 140, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(115, 96, "Вхід x[n]", size=12, color=INK, bold=True))
    p.append(text(115, 110, "кадр аналізу k·Ha", size=10, color=MUTED))

    # Блок пошуку зсуву SOLA
    p.append(rect(250, 75, 200, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(350, 95, "Пошук максимуму кореляції", size=11, color=INK, bold=True))
    p.append(text(350, 110, "між входом x[n] та виходом y[n]", size=10, color=POS))

    # Вихідний акумулятор SOLA
    p.append(rect(510, 75, 200, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(610, 96, "Вихідний буфер y[n]", size=12, color=INK, bold=True))
    p.append(text(610, 110, "накопичення overlap-add", size=10, color=MUTED))

    # Стрілки SOLA
    p.append(arrow(185, 96, 250, 96, color=LINE, sw=1.5))
    p.append(arrow(450, 96, 510, 96, color=LINE, sw=1.5))

    # Зворотний зв'язок SOLA (петля похибки)
    p.append('<path d="M 610 117 L 610 155 L 350 155 L 350 117" stroke="%s" stroke-width="1.6" fill="none"/>' % POS)
    p.append(arrow(350, 125, 350, 117, color=POS, sw=1.6))
    p.append(rect(400, 142, 230, 26, fill="#fdecea", stroke=POS, sw=1, rx=3))
    p.append(text(515, 159, "Петля накопичення похибок та дрейфу тону", size=10, color=POS, bold=True))

    # ── Нижній блок: WSOLA ──
    p.append(rect(25, 225, W - 50, 185, fill="#f4faf6", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(45, 252, "WSOLA (Waveform Similarity OLA): шаблон завжди береться з чистого входу", size=13, color=FIELD, bold=True, anchor="start"))

    # Вхідний потік WSOLA
    p.append(rect(45, 275, 140, 42, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(115, 296, "Вхід x[n]", size=12, color=INK, bold=True))
    p.append(text(115, 310, "потоковий масив аудіо", size=10, color=MUTED))

    # Блок еталона з входу
    p.append(rect(240, 270, 220, 52, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(350, 290, "Еталонний шаблон x[τ_{k-1} + Hs]", size=11, color=FIELD, bold=True))
    p.append(text(350, 308, "ідеальне природне продовження фази", size=10, color=MUTED))

    # Блок кореляції WSOLA
    p.append(rect(240, 340, 220, 52, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(350, 360, "Кореляція у вікні ±Δ", size=11, color=INK, bold=True))
    p.append(text(350, 378, "пошук відрізка x[k·Ha + δ]", size=10, color=LINE))

    # Вихідний акумулятор WSOLA
    p.append(rect(520, 305, 190, 52, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(615, 326, "Вихідний буфер y[n]", size=12, color=INK, bold=True))
    p.append(text(615, 344, "зшивання без зворотного зв'язку", size=10, color=FIELD))

    # Стрілки WSOLA
    p.append(arrow(185, 296, 240, 296, color=LINE, sw=1.5))
    p.append(arrow(185, 305, 240, 366, color=LINE, sw=1.5))
    p.append(arrow(350, 322, 350, 340, color=FIELD, sw=1.5))
    p.append(arrow(460, 366, 520, 331, color=LINE, sw=1.5))

    render(os.path.join(OUT, "wsola-vs-sola-synthesis.svg"), W, H, *p,
           title="Порівняння архітектури SOLA та WSOLA: походження опорного шаблону")


# ── 2. search-tolerance-window: вікно допуску та пошук максимальної кореляції ─
def fig_search_tolerance_window():
    W, H = 760, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Верхня інформаційна панель
    p.append(text(W / 2, 38, "Пошук зміщення δ у вікні допуску навколо номінальної точки k·Ha", size=13, color=INK, bold=True))

    # 1. Часова вісь вхідного сигналу
    axis_y = 85
    p.append(line(50, axis_y, 710, axis_y, color=LINE, sw=1.6))
    p.append(arrow(700, axis_y, 715, axis_y, color=LINE, sw=1.6))
    p.append(text(715, axis_y - 12, "Вхід x[n]", size=11, color=INK, anchor="end", bold=True))

    # Номінальна точка k*Ha
    kx = 380
    p.append(line(kx, axis_y - 15, kx, axis_y + 15, color=POS, sw=1.8))
    p.append(text(kx, axis_y - 20, "Номінальна точка k·Ha", size=11, color=POS, bold=True))

    # 2. Область допуску [-Δ, +Δ]
    delta_px = 160
    band_y = 125
    p.append(rect(kx - delta_px, band_y, delta_px * 2, 42, fill="#ebf5fb", stroke=NEG, sw=1.2, rx=4))
    p.append(text(kx, band_y + 26, "Область пошуку зсуву: [k·Ha − Δ,  k·Ha + Δ]", size=11, color=NEG, bold=True))
    p.append(text(kx - delta_px - 8, band_y + 26, "−Δ", size=11, color=NEG, anchor="end", bold=True))
    p.append(text(kx + delta_px + 8, band_y + 26, "+Δ", size=11, color=NEG, anchor="start", bold=True))

    # 3. Знайдена оптимальна точка зміщення δ_k та вирізаний кадр
    opt_delta = 55
    opt_x = kx + opt_delta
    frame_y = 195
    frame_len = 240
    p.append(rect(opt_x, frame_y, frame_len, 42, fill="#d5f5e3", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(opt_x + frame_len / 2, frame_y + 26, "Кадр аналізу завдовжки N від точки τ_k", size=11, color=FIELD, bold=True))

    # Зв'язок між вікном пошуку та вибраним кадром
    p.append(line(opt_x, band_y + 42, opt_x, frame_y, color=FIELD, sw=1.5, dash="3 3"))
    p.append(arrow(opt_x, frame_y - 10, opt_x, frame_y, color=FIELD, sw=1.5))
    p.append(text(opt_x - 10, frame_y - 12, "τ_k = k·Ha + δ_k", size=11, color=FIELD, anchor="end", bold=True))

    # 4. Графік крос-кореляції знизу
    corr_y = 350
    p.append(line(kx - delta_px, corr_y, kx + delta_px, corr_y, color=MUTED, sw=1))
    p.append(text(kx - delta_px - 15, corr_y - 25, "Кореляція C(δ)", size=11, color=INK, bold=True, anchor="end"))

    # Крива кореляції
    pts = []
    for d in range(-delta_px, delta_px + 1, 2):
        x = kx + d
        val = math.exp(-((d - opt_delta) ** 2) / (2 * (22 ** 2))) * 55 + math.cos(d * 0.12) * 10
        y = corr_y - val
        pts.append("%.1f,%.1f" % (x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    # Маркер максимуму
    max_y = corr_y - 65
    p.append(circle(opt_x, max_y, 4.5, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(line(opt_x, max_y, opt_x, corr_y, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(opt_x, corr_y + 22, "Пік кореляції при δ = δ_k", size=11, color=FIELD, bold=True))

    # Параметри ліворуч знизу
    p.append(rect(30, 310, 160, 52, fill="#f8f9fa", stroke="#d0d7de", sw=1, rx=4))
    p.append(text(110, 330, "L — шаблон", size=10, color=MUTED))
    p.append(text(110, 348, "2Δ+1 — зсувів", size=10, color=MUTED))

    render(os.path.join(OUT, "search-tolerance-window.svg"), W, H, *p,
           title="Область допуску пошуку та знаходження оптимального зсуву фази")


# ── 3. ola-reconstruction-crossfade: перекриття вікон та умова COLA ───────────
def fig_ola_reconstruction_crossfade():
    W, H = 760, 370
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Часова вісь вихідного сигналу
    axis_y = 180
    p.append(line(45, axis_y, 715, axis_y, color=LINE, sw=1.4))
    p.append(arrow(705, axis_y, 720, axis_y, color=LINE, sw=1.4))
    p.append(text(720, axis_y + 20, "Час синтезу m (відліки)", size=11, color=INK, anchor="end"))

    # Позиції вікон на вихідній осі
    x0 = 80
    Hs_px = 160
    N_px = 320

    # Вікно k-1 (сіре/пунктир)
    w_km1 = []
    for i in range(N_px + 1):
        x = (x0 - Hs_px) + i
        if 45 <= x <= 715:
            # Hann window
            val = 0.5 * (1 - math.cos(2 * math.pi * i / N_px)) * 90
            w_km1.append("%.1f,%.1f" % (x, axis_y - val))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="4 3"/>' % (" ".join(w_km1), MUTED))

    # Вікно k (синій колір)
    w_k = []
    for i in range(N_px + 1):
        x = x0 + i
        if 45 <= x <= 715:
            val = 0.5 * (1 - math.cos(2 * math.pi * i / N_px)) * 90
            w_k.append("%.1f,%.1f" % (x, axis_y - val))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(w_k), NEG))
    p.append(text(x0 + N_px / 2, axis_y - 98, "Вікно k: w[m − k·Hs]", size=11, color=NEG, bold=True))

    # Вікно k+1 (зелений колір)
    w_kp1 = []
    for i in range(N_px + 1):
        x = (x0 + Hs_px) + i
        if 45 <= x <= 715:
            val = 0.5 * (1 - math.cos(2 * math.pi * i / N_px)) * 90
            w_kp1.append("%.1f,%.1f" % (x, axis_y - val))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(w_kp1), FIELD))
    p.append(text(x0 + Hs_px + N_px / 2, axis_y - 98, "Вікно k+1: w[m − (k+1)·Hs]", size=11, color=FIELD, bold=True))

    # Маркери кроків синтезу
    p.append(line(x0, axis_y - 10, x0, axis_y + 15, color=LINE, sw=1.5))
    p.append(text(x0, axis_y + 30, "k·Hs", size=11, color=INK, bold=True))

    p.append(line(x0 + Hs_px, axis_y - 10, x0 + Hs_px, axis_y + 15, color=LINE, sw=1.5))
    p.append(text(x0 + Hs_px, axis_y + 30, "(k+1)·Hs", size=11, color=INK, bold=True))

    # Стрілка кроку Hs
    p.append(line(x0, axis_y + 48, x0 + Hs_px, axis_y + 48, color=LINE, sw=1.2))
    p.append(arrow(x0 + 20, axis_y + 48, x0, axis_y + 48, color=LINE, sw=1.2))
    p.append(arrow(x0 + Hs_px - 20, axis_y + 48, x0 + Hs_px, axis_y + 48, color=LINE, sw=1.2))
    p.append(text(x0 + Hs_px / 2, axis_y + 64, "Крок синтезу Hs = N / 2", size=11, color=INK))

    # Зона перекриття (Cross-fade)
    cross_start = x0 + Hs_px
    cross_end = x0 + N_px
    p.append(rect(cross_start, axis_y - 90, cross_end - cross_start, 90, fill="#fdf2e9", stroke=POS, sw=1, rx=2))
    p.append(text((cross_start + cross_end) / 2, axis_y - 45, "Зона перекриття (Cross-fade)", size=10, color=POS, bold=True))

    # Лінія постійної суми COLA (Constant Overlap-Add)
    p.append(line(x0 + 40, axis_y - 90, x0 + Hs_px * 2 + 80, axis_y - 90, color=POS, sw=1.8, dash="5 4"))
    p.append(rect(370, 35, 340, 36, fill="#fbeee6", stroke=POS, sw=1.2, rx=4))
    p.append(text(540, 58, "Умова COLA: сума вікон ∑ w[m − k·Hs] ≡ 1.0 (без пульсацій амплітуди)", size=10, color=POS, bold=True))

    # Пояснення внизу
    p.append(text(W / 2, 335, "При кроці Hs = N/2 вікно Ганна ідеально доповнює сусіднє: w_k(m) + w_{k+1}(m) = 1", size=11, color=MUTED))

    render(os.path.join(OUT, "ola-reconstruction-crossfade.svg"), W, H, *p,
           title="Перекриття та плавне зшивання вікон із збереженням постійної амплітуди")


# ── 4. buffer-latency-pipeline: конвеєр потокової обробки та затримка ────────
def fig_buffer_latency_pipeline():
    W, H = 760, 380
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Блоки конвеєра
    # 1. Кільцевий буфер входу
    p.append(rect(30, 45, 180, 130, fill="#f8f9fa", stroke=LINE, sw=1.4, rx=6))
    p.append(text(120, 70, "Вхідний буфер", size=12, color=INK, bold=True))
    p.append(rect(45, 88, 150, 26, fill="#e8f8f5", stroke=FIELD, sw=1, rx=3))
    p.append(text(120, 105, "Історія (N відліків)", size=10, color=FIELD))
    p.append(rect(45, 120, 150, 26, fill="#fef9e7", stroke=POS, sw=1, rx=3))
    p.append(text(120, 137, "Lookahead (N + Δ відліків)", size=10, color=POS, bold=True))
    p.append(text(120, 163, "Мінімум: N + Δ для пошуку", size=9, color=MUTED))

    # Стрілка 1 -> 2
    p.append(arrow(210, 110, 270, 110, color=LINE, sw=1.6))

    # 2. Модуль кореляційного пошуку
    p.append(rect(270, 45, 210, 130, fill="#ebf5fb", stroke=NEG, sw=1.4, rx=6))
    p.append(text(375, 70, "Кореляційний рушій", size=12, color=NEG, bold=True))
    p.append(text(375, 95, "Опорний шаблон з чистого входу", size=10, color=INK))
    p.append(text(375, 115, "Сканування зсувів δ ∈ [−Δ, +Δ]", size=10, color=INK))
    p.append(rect(285, 130, 180, 30, fill="#ffffff", stroke=NEG, sw=1, rx=3))
    p.append(text(375, 149, "Знайдено зміщення δ_k", size=11, color=NEG, bold=True))

    # Стрілка 2 -> 3
    p.append(arrow(480, 110, 540, 110, color=LINE, sw=1.6))

    # 3. Модуль зважування вікном та OLA
    p.append(rect(540, 45, 190, 130, fill="#f4faf6", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(635, 70, "Зважування та OLA", size=12, color=FIELD, bold=True))
    p.append(text(635, 95, "Множення на вікно w[n]", size=10, color=INK))
    p.append(text(635, 115, "Накладання у вихідний буфер", size=10, color=INK))
    p.append(rect(555, 130, 160, 30, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
    p.append(text(635, 149, "y[m] += w[n] · x[τ_k + n]", size=10, color=FIELD, bold=True))

    # Нижня панель: Часові затримки та буферизація
    p.append(rect(30, 205, W - 60, 150, fill="#fbfcfc", stroke="#d0d7de", sw=1.2, rx=6))
    p.append(text(50, 230, "Структура затримок у реальному часі (Streaming Latency)", size=12, color=INK, bold=True, anchor="start"))

    # Шкала затримок
    lat_y = 280
    p.append(line(50, lat_y, 710, lat_y, color=MUTED, sw=1.2))

    # Відрізок алгоритмічної затримки
    p.append(rect(50, lat_y - 25, 360, 40, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    p.append(text(230, lat_y - 5, "Алгоритмічна затримка заглядання вперед: N + Δ", size=11, color=POS, bold=True))
    p.append(text(230, lat_y + 10, "~25–35 мс (залежно від вибору N і Δ)", size=10, color=MUTED))

    # Відрізок кроку видачі
    p.append(rect(410, lat_y - 25, 300, 40, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(560, lat_y - 5, "Крок видачі блоків: Hs відліків", size=11, color=FIELD, bold=True))
    p.append(text(560, lat_y + 10, "~10–15 мс між викликами wsola_step()", size=10, color=MUTED))

    p.append(text(W / 2, 340, "Загальна затримка конвеєра: T_lat = (N + Δ) / fs — час очікування нових відліків перед обробкою", size=11, color=INK))

    render(os.path.join(OUT, "buffer-latency-pipeline.svg"), W, H, *p,
           title="Потоковий конвеєр обробки WSOLA та оцінка алгоритмічної затримки")


if __name__ == "__main__":
    fig_wsola_vs_sola_synthesis()
    fig_search_tolerance_window()
    fig_ola_reconstruction_crossfade()
    fig_buffer_latency_pipeline()
    print("Усі 4 фігури згенеровано успішно.")
