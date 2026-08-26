# -*- coding: utf-8 -*-
"""Фігури теми «Перевірка оцінки: лог, графік, істина».
Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/ (не переписуємо)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Ілюзія гладкості — чому око обманює ────────────────────────────
def fig_visual_illusion():
    W, H = 760, 390
    L, R = 70, 720
    T, B = 50, 310
    parts = []

    parts.append(line(L, B, R, B, color=LINE, sw=1.5))
    parts.append(line(L, T, L, B, color=LINE, sw=1.5))
    parts.append(text(R, B + 22, "час t [с] →", size=12, color=MUTED, anchor="end"))
    parts.append(text(L - 10, T + 5, "кут θ [°]", size=12, color=MUTED, anchor="end"))

    for y_val in [0, 15, 30]:
        y_px = B - (y_val / 35.0) * (B - T)
        parts.append(line(L, y_px, R, y_px, color="#e5e7eb", sw=1, dash="4 4"))
        parts.append(text(L - 10, y_px + 4, str(y_val), size=11, color=MUTED, anchor="end"))

    def X(t): return L + (R - L) * (t / 4.0)
    def Y(val): return B - (val / 35.0) * (B - T)

    def true_angle(t):
        if t < 0.5:
            return 0.0
        elif t < 1.8:
            tau = (t - 0.5) / 1.3
            return 25.0 * (1.0 - math.exp(-4.5 * tau) * math.cos(3.0 * tau))
        else:
            tau = (t - 1.8) / 2.2
            return 25.0 - 15.0 * (1.0 - math.exp(-3.0 * tau))

    def est_angle(t):
        t_lag = max(0.0, t - 0.12)
        val = true_angle(t_lag)
        if 0.5 < t < 2.2:
            drift = -3.5 * math.sin((t - 0.5) / 1.7 * math.pi)
        else:
            drift = 0.0
        return val + drift

    import random
    rng = random.Random(42)
    for i in range(80):
        t = i * 4.0 / 80.0
        val = true_angle(t) + rng.gauss(0, 2.2)
        parts.append(circle(X(t), Y(val), 2.2, fill="#9ca3af", stroke="#6b7280", sw=0.8))

    pts_true = [f"{X(i*4.0/200):.1f} {Y(true_angle(i*4.0/200)):.1f}" for i in range(201)]
    parts.append(f'<path d="M {" L ".join(pts_true)}" fill="none" stroke="{FIELD}" stroke-width="3"/>')

    pts_est = [f"{X(i*4.0/200):.1f} {Y(est_angle(i*4.0/200)):.1f}" for i in range(201)]
    parts.append(f'<path d="M {" L ".join(pts_est)}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="6 3"/>')

    t_mid = 1.15
    y_mid = true_angle(t_mid)
    parts.append(line(X(t_mid), Y(y_mid), X(t_mid + 0.12), Y(y_mid), color=NEG, sw=1.8))
    parts.append(arrow(X(t_mid), Y(y_mid) - 15, X(t_mid + 0.12), Y(y_mid) - 15, color=NEG, sw=1.5))
    parts.append(text(X(t_mid + 0.06), Y(y_mid) - 25, "Фазовий лаг Δt = 120 мс", size=11, color=NEG, bold=True))

    t_drift = 1.45
    y_tr = true_angle(t_drift)
    y_es = est_angle(t_drift)
    parts.append(line(X(t_drift), Y(y_tr), X(t_drift), Y(y_es), color=POS, sw=1.8))
    parts.append(text(X(t_drift) + 15, (Y(y_tr) + Y(y_es)) / 2 + 4, "Дрейф −3.5°", size=11, color=POS, bold=True, anchor="start"))

    lx, ly = L + 30, T + 20
    parts.append(rect(lx - 10, ly - 12, 450, 48, fill="#ffffff", stroke="#d1d5db", sw=1, rx=4))
    parts.append(line(lx, ly, lx + 25, ly, color=FIELD, sw=3))
    parts.append(text(lx + 32, ly + 4, "Наземна істина (Ground Truth, енкодер)", size=11, color=INK, anchor="start"))
    parts.append(line(lx + 270, ly, lx + 295, ly, color=POS, sw=2.5, dash="6 3"))
    parts.append(text(lx + 302, ly + 4, "Оцінка фільтра", size=11, color=INK, anchor="start"))
    parts.append(circle(lx + 10, ly + 24, 3, fill="#9ca3af", stroke="#6b7280", sw=1))
    parts.append(text(lx + 32, ly + 28, "Сирі шуми давача (IMU)", size=11, color=MUTED, anchor="start"))

    parts.append(text((L + R) / 2, H - 15, "Око бачить гладку червону лінію і вважає її гарною; істина показує небезпечний фазовий лаг і дрейф", size=12, color=INK, bold=True))

    render(os.path.join(IMG, "visual-illusion-lag.svg"), W, H, *parts, title="Ілюзія гладкості оцінки")


# ── Фігура 2: Архітектура синхронного логування та верифікації ───────────────
def fig_sync_log_arch():
    W, H = 880, 380
    parts = []

    b1_body, w1, h1 = textbox(150, 95, "Бортовий контролер (MCU)\n• IMU (акселерометр, гіроскоп)\n• Алгоритм фільтрації (EKF)\n• Мітки системного таймера (μs)", size=11, fill="#f8fafc", stroke=NEG, pad=10)
    parts.append(b1_body)

    b2_body, w2, h2 = textbox(150, 265, "Еталонна система (Ground Truth)\n• Оптичний енкодер (20 біт) /\n  Vicon / OptiTrack (500 Hz)\n• Апаратний строб синхронізації (GPIO)", size=11, fill="#f0fdf4", stroke=FIELD, pad=10)
    parts.append(b2_body)

    b3_body, w3, h3 = textbox(440, 180, "Синхронний логер\n• Подвійний кільцевий буфер DMA\n• Потоковий бінарний пакет\n• Зведення міток часу t_MCU ↔ t_GT\n• Запис: High-Speed SD / USB-CDC", size=11, fill="#fffbeb", stroke="#d97706", pad=10)
    parts.append(b3_body)

    b4_body, w4, h4 = textbox(730, 180, "Конвеєр валідації (Python/C++)\n• Декодування логу й юстировка\n• Статистика інновацій (E[y], 2σ)\n• Автокореляція залишків\n• Метрики: RMSE, NEES, NIS, лаг\n• Автоматичний тюнінг (Q, R)", size=11, fill="#fdf2f8", stroke=POS, pad=10)
    parts.append(b4_body)

    parts.append(line(275, 95, 335, 95, color=NEG, sw=1.5))
    parts.append(arrow(335, 95, 335, 140, color=NEG, sw=1.5))
    parts.append(text(285, 82, "Оцінка x̂, P, y, S", size=10, color=NEG, anchor="start"))

    parts.append(line(275, 265, 335, 265, color=FIELD, sw=1.5))
    parts.append(arrow(335, 265, 335, 220, color=FIELD, sw=1.5))
    parts.append(text(285, 280, "Істина x_true, t_sync", size=10, color=FIELD, anchor="start"))

    parts.append(arrow(545, 180, 615, 180, color=LINE, sw=2))
    parts.append(text(580, 168, "Бінарний лог", size=11, color=INK))

    render(os.path.join(IMG, "sync-log-architecture.svg"), W, H, *parts, title="Архітектура стенда синхронного логування")


# ── Фігура 3: Інновація та коридори 2σ / 3σ ──────────────────────────────────
def fig_innovation_corridor():
    W, H = 760, 420
    parts = []

    L, R = 60, 710
    T1, B1 = 40, 180
    mid1 = (T1 + B1) / 2

    parts.append(rect(L, T1, R - L, B1 - T1, fill="#fafafa", stroke="#e5e7eb", sw=1))
    parts.append(line(L, mid1, R, mid1, color=LINE, sw=1.2))
    parts.append(text(L + 10, T1 + 18, "А. Оптимальний фільтр: білий шум у коридорі ±2σ (E[y] = 0)", size=12, color=FIELD, bold=True, anchor="start"))

    import random
    rng = random.Random(101)
    pts_upper1, pts_lower1, pts_y1 = [], [], []
    N = 100
    for i in range(N):
        t = i / float(N - 1)
        x = L + t * (R - L)
        sigma = 18.0 + 8.0 * math.sin(t * math.pi)
        y_val = rng.gauss(0, sigma * 0.48)
        pts_upper1.append(f"{x:.1f} {mid1 - sigma:.1f}")
        pts_lower1.append(f"{x:.1f} {mid1 + sigma:.1f}")
        pts_y1.append((x, mid1 - y_val))

    poly_pts = pts_upper1 + list(reversed(pts_lower1))
    parts.append(f'<polygon points="{" ".join(poly_pts)}" fill="#dcfce7" stroke="#86efac" stroke-width="1"/>')
    parts.append(line(L, mid1, R, mid1, color="#16a34a", sw=1, dash="4 4"))

    for x, y in pts_y1:
        parts.append(circle(x, y, 2.2, fill=NEG, stroke=NEG, sw=0.5))

    parts.append(text(R - 10, mid1 - 22, "+2√S (верхня межа)", size=10, color="#15803d", anchor="end"))
    parts.append(text(R - 10, mid1 + 28, "−2√S (нижня межа)", size=10, color="#15803d", anchor="end"))

    T2, B2 = 230, 370
    mid2 = (T2 + B2) / 2

    parts.append(rect(L, T2, R - L, B2 - T2, fill="#fafafa", stroke="#e5e7eb", sw=1))
    parts.append(line(L, mid2, R, mid2, color=LINE, sw=1.2))
    parts.append(text(L + 10, T2 + 18, "Б. Неузгоджений фільтр: постійний зсув нуля (bias) та вильоти за 2σ", size=12, color=POS, bold=True, anchor="start"))

    pts_upper2, pts_lower2 = [], []
    pts_y2 = []
    for i in range(N):
        t = i / float(N - 1)
        x = L + t * (R - L)
        sigma = 16.0
        drift = 12.0 + 8.0 * math.sin(t * 2 * math.pi)
        y_val = drift + rng.gauss(0, 14.0)
        pts_upper2.append(f"{x:.1f} {mid2 - sigma:.1f}")
        pts_lower2.append(f"{x:.1f} {mid2 + sigma:.1f}")
        pts_y2.append((x, mid2 - y_val))

    poly_pts2 = pts_upper2 + list(reversed(pts_lower2))
    parts.append(f'<polygon points="{" ".join(poly_pts2)}" fill="#fee2e2" stroke="#fca5a5" stroke-width="1"/>')
    parts.append(line(L, mid2, R, mid2, color=MUTED, sw=1, dash="4 4"))

    for x, y in pts_y2:
        col = POS if (y < mid2 - 16.0 or y > mid2 + 16.0) else NEG
        parts.append(circle(x, y, 2.4, fill=col, stroke=col, sw=0.5))

    parts.append(text(R - 10, mid2 - 20, "Коридор завузький (надмірна самовпевненість)", size=10, color=POS, anchor="end"))
    parts.append(text(L + 120, mid2 - 32, "Постійне додатне зміщення (E[y] ≠ 0)", size=11, color=POS, bold=True))

    parts.append(text((L + R) / 2, H - 15, "Інновація оптимального фільтра не має пам'яті (нульове середнє) і суворо лежить у межах ±2√S", size=12, color=INK, bold=True))

    render(os.path.join(IMG, "innovation-corridor.svg"), W, H, *parts, title="Коридори узгодженості інновації")


# ── Фігура 4: Автокореляція залишків ─────────────────────────────────────────
def fig_autocorrelation():
    W, H = 760, 360
    L, R = 70, 710
    T, B = 50, 300
    midY = B - (B - T) * 0.35
    parts = []

    parts.append(line(L, midY, R, midY, color=LINE, sw=1.5))
    parts.append(line(L, T, L, B, color=LINE, sw=1.5))
    parts.append(text(R, midY + 22, "Лаг m (кроки затримки) →", size=12, color=MUTED, anchor="end"))
    parts.append(text(L - 10, T + 5, "Автокореляція r_yy[m]", size=12, color=MUTED, anchor="end"))

    scaleY = (B - T) * 0.55
    def Y(val): return midY - val * scaleY

    for y_val in [1.0, 0.5, 0.0, -0.2]:
        y_px = Y(y_val)
        parts.append(line(L, y_px, R, y_px, color="#e5e7eb", sw=1, dash="4 4"))
        parts.append(text(L - 8, y_px + 4, f"{y_val:.1f}", size=11, color=MUTED, anchor="end"))

    ci = 0.12
    parts.append(rect(L, Y(ci), R - L, Y(-ci) - Y(ci), fill="#ecfdf5", stroke="#a7f3d0", sw=1))
    parts.append(text(R - 10, Y(ci) - 6, "95% довірчий інтервал білого шуму (±1.96 / √N)", size=10, color="#059669", anchor="end"))

    num_lags = 16
    def X(lag): return L + (R - L) * (lag / float(num_lags))

    r_optimal = [1.0, 0.04, -0.05, 0.03, 0.02, -0.04, 0.01, 0.03, -0.02, 0.01, 0.02, -0.01, 0.01, -0.02, 0.01, 0.00]
    r_bad = [1.0, 0.68, 0.46, 0.31, 0.21, 0.14, 0.09, 0.05, 0.03, 0.02, 0.01, 0.00, -0.01, 0.00, 0.01, 0.00]

    for m in range(num_lags):
        xm = X(m)
        parts.append(text(xm, midY + 16, str(m), size=11, color=INK))

        parts.append(line(xm - 4, midY, xm - 4, Y(r_bad[m]), color=POS, sw=3))
        parts.append(circle(xm - 4, Y(r_bad[m]), 3, fill=POS, stroke=POS, sw=1))

        parts.append(line(xm + 4, midY, xm + 4, Y(r_optimal[m]), color=FIELD, sw=3))
        parts.append(circle(xm + 4, Y(r_optimal[m]), 3, fill=FIELD, stroke=FIELD, sw=1))

    lx, ly = L + 180, T + 20
    parts.append(rect(lx - 10, ly - 10, 430, 42, fill="#ffffff", stroke="#d1d5db", sw=1, rx=4))
    parts.append(line(lx, ly + 2, lx + 20, ly + 2, color=FIELD, sw=3))
    parts.append(text(lx + 26, ly + 6, "Оптимальний Калман (білий шум, нема «пам'яті»)", size=11, color=INK, anchor="start"))

    parts.append(line(lx, ly + 22, lx + 20, ly + 22, color=POS, sw=3))
    parts.append(text(lx + 26, ly + 26, "Неналаштований фільтр (кольоровий шум, неврахована динаміка)", size=11, color=INK, anchor="start"))

    parts.append(text((L + R) / 2, H - 15, "Кореляція залишків на лагах m ≥ 1 означає, що фільтр «пропускає» корисну динаміку в смітник", size=12, color=INK, bold=True))

    render(os.path.join(IMG, "autocorrelation-residuals.svg"), W, H, *parts, title="Автокореляція залишків інновації")


# ── Фігура 5: Метрика NEES і перевірка статистичної узгодженості ───────────────
def fig_nees_consistency():
    W, H = 760, 370
    L, R = 70, 710
    T, B = 50, 310
    parts = []

    parts.append(line(L, B, R, B, color=LINE, sw=1.5))
    parts.append(line(L, T, L, B, color=LINE, sw=1.5))
    parts.append(text(R, B + 22, "номер кроку k →", size=12, color=MUTED, anchor="end"))
    parts.append(text(L - 10, T + 5, "NEES ε_x[k]", size=12, color=MUTED, anchor="end"))

    max_nees = 12.0
    def Y(val): return B - (val / max_nees) * (B - T)
    def X(k): return L + (R - L) * (k / 100.0)

    for val in [2, 4, 6, 8, 10]:
        y_px = Y(val)
        parts.append(line(L, y_px, R, y_px, color="#e5e7eb", sw=1, dash="4 4"))
        parts.append(text(L - 8, y_px + 4, str(val), size=11, color=MUTED, anchor="end"))

    # Довірчий інтервал хі-квадрат для n=2 станів: [0.05, 5.99] для 95%
    chi_lo, chi_hi = 0.05, 5.99
    parts.append(rect(L, Y(chi_hi), R - L, Y(chi_lo) - Y(chi_hi), fill="#ecfdf5", stroke="#86efac", sw=1))
    
    # 1. Узгоджений фільтр
    import random
    rng = random.Random(202)
    pts_good = []
    for k in range(101):
        val = rng.expovariate(0.5)
        pts_good.append(f"{X(k):.1f} {Y(min(val, 11.5)):.1f}")
    parts.append(f'<path d="M {" L ".join(pts_good)}" fill="none" stroke="{FIELD}" stroke-width="1.8"/>')

    # 2. Неузгоджений фільтр
    pts_bad = []
    for k in range(101):
        if k < 25:
            val = rng.expovariate(0.5)
        else:
            val = 2.0 + (k - 25) * 0.12 + rng.gauss(0, 1.2)
        pts_bad.append(f"{X(k):.1f} {Y(min(val, 11.8)):.1f}")
    parts.append(f'<path d="M {" L ".join(pts_bad)}" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="5 3"/>')

    # Легенда з параметрами
    lx, ly = L + 20, T + 15
    parts.append(rect(lx - 8, ly - 8, 480, 56, fill="#ffffff", stroke="#d1d5db", sw=1, rx=4))
    parts.append(line(lx, ly + 2, lx + 22, ly + 2, color=FIELD, sw=2))
    parts.append(text(lx + 28, ly + 6, "Узгоджений фільтр (коваріація P відповідає реальній похибці)", size=11, color=INK, anchor="start"))
    
    parts.append(line(lx, ly + 20, lx + 22, ly + 20, color=POS, sw=2, dash="5 3"))
    parts.append(text(lx + 28, ly + 24, "Оптимістичний фільтр (P занижена, розбіжність за межі χ²)", size=11, color=INK, anchor="start"))

    parts.append(line(lx, ly + 36, lx + 22, ly + 36, color="#16a34a", sw=1.5, dash="4 2"))
    parts.append(text(lx + 28, ly + 40, "Теоретичні межі: E[NEES] = 2.0, 95% довірча межа χ²(2) = 5.99", size=10, color="#15803d", anchor="start"))

    parts.append(text((L + R) / 2, H - 15, "NEES зіставляє фактичну похибку з внутрішньою матрицею P: вихід за межу χ² викриває розбіжність", size=12, color=INK, bold=True))

    render(os.path.join(IMG, "nees-consistency.svg"), W, H, *parts, title="Перевірка узгодженості NEES")


if __name__ == "__main__":
    fig_visual_illusion()
    fig_sync_log_arch()
    fig_innovation_corridor()
    fig_autocorrelation()
    fig_nees_consistency()
    print("Усі фігури згенеровано успішно.")
