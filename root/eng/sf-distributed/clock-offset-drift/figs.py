# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

def path_el(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw:.1f}" fill="{fill}"{d_attr}/>'


# ── Фігура 1: Розкладання похибки годинника: зсув, хід, дрейф і шум ──────────
def fig_offset_skew_drift():
    W, H = 760, 420
    parts = []
    parts.append(text(W/2, 24, "Складові часової похибки: зсув x₀, швидкість ходу α, дрейф β та шум", size=15, bold=True))

    ox, oy = 80, 360
    w_ax, h_ax = 620, 300
    parts.append(line(ox, oy, ox + w_ax, oy, color=MUTED, sw=1.5))
    parts.append(line(ox, oy, ox, oy - h_ax, color=MUTED, sw=1.5))
    parts.append(text(ox + w_ax + 8, oy + 4, "t", size=13, color=MUTED, anchor="start"))
    parts.append(text(ox, oy - h_ax - 10, "x(t) = T(t) − t", size=13, color=MUTED, anchor="middle"))

    x0_val = 50
    parts.append(circle(ox, oy - x0_val, 4, fill=POS, stroke=POS, sw=1))
    parts.append(line(ox - 6, oy - x0_val, ox + 6, oy - x0_val, color=POS, sw=1.5))
    b_x0, _, _ = textbox(ox + 85, oy - x0_val - 18, "Зсув x₀ (Clock Offset, с)", size=11.5,
                         fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b_x0)

    # 1. Тільки лінійний хід (alpha * t)
    pts_linear = []
    for px in range(0, 560, 10):
        t_norm = px / 550.0
        val = x0_val + 110 * t_norm
        pts_linear.append((ox + px, oy - val))
    d_linear = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_linear)
    parts.append(path_el(d_linear, stroke=NEG, sw=1.8, dash="5 4"))

    # 2. Хід + квадратичний дрейф (alpha * t + 0.5 * beta * t^2)
    pts_quad = []
    for px in range(0, 560, 10):
        t_norm = px / 550.0
        val = x0_val + 110 * t_norm + 115 * (t_norm ** 2)
        pts_quad.append((ox + px, oy - val))
    d_quad = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_quad)
    parts.append(path_el(d_quad, stroke=FIELD, sw=2, dash="7 3"))

    # 3. Реальна траєкторія з шумом epsilon(t)
    pts_real = []
    noise_pattern = [0, 3.2, -2.1, 4.5, 1.2, -3.8, 2.0, 5.1, -1.4, 3.7,
                     -4.2, 1.8, 6.0, 0.5, -3.1, 4.8, 1.1, -2.5, 3.9, 6.2,
                     -1.8, 4.0, 7.3, 2.1, -2.9, 5.0, 1.4, -4.1, 3.6, 6.5,
                     -0.9, 4.7, 8.1, 2.9, -1.7, 5.4, 2.2, -3.0, 4.1, 7.8,
                     0.3, 5.8, 9.2, 3.4, -2.1, 6.0, 2.7, -1.9, 5.0, 8.5,
                     1.2, 6.3, 10.1, 4.0, -1.5, 6.7]
    for i, px in enumerate(range(0, 560, 10)):
        t_norm = px / 550.0
        n = noise_pattern[i % len(noise_pattern)]
        val = x0_val + 110 * t_norm + 115 * (t_norm ** 2) + n
        pts_real.append((ox + px, oy - val))
    d_real = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_real)
    parts.append(path_el(d_real, stroke=POS, sw=2.2))

    b_skew, _, _ = textbox(360, oy - 90, "Швидкість ходу α·t (лінійний нахил)", size=11,
                           fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(b_skew)
    parts.append(line(360, oy - 105, 330, oy - 120, color=NEG, sw=1.2, dash="3 2"))

    b_drift, _, _ = textbox(520, oy - 190, "Дрейф ½·β·t² (квадратичний вигин)", size=11,
                            fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b_drift)
    parts.append(line(520, oy - 205, 490, oy - 225, color=FIELD, sw=1.2, dash="3 2"))

    b_noise, _, _ = textbox(470, oy - 295, "Реальний час: x₀ + α·t + ½·β·t² + ε(t)", size=11.5,
                            fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b_noise)
    parts.append(line(470, oy - 280, 485, oy - 255, color=POS, sw=1.2))

    exp_y = oy + 32
    b1, _, _ = textbox(160, exp_y, "x₀ — фазовий зсув (с)", size=11, fill=FILL, stroke=MUTED, color=INK)
    b2, _, _ = textbox(380, exp_y, "α — відхилення частоти (ppm)", size=11, fill=FILL, stroke=MUTED, color=INK)
    b3, _, _ = textbox(600, exp_y, "β — дрейф частоти (ppm/добу)", size=11, fill=FILL, stroke=MUTED, color=INK)
    parts.append(b1)
    parts.append(b2)
    parts.append(b3)

    render(os.path.join(IMG, "offset-skew-drift.svg"), W, H, *parts)


# ── Фігура 2: Температурні характеристики різних типів генераторів ──────────
def fig_temp_characteristics():
    W, H = 760, 400
    parts = []
    parts.append(text(W/2, 24, "Температурна нестабільність: камертонний кварц, AT-зріз, TCXO та OCXO", size=15, bold=True))

    ox, oy = 90, 200
    w_ax = 600
    parts.append(line(ox, oy, ox + w_ax, oy, color=MUTED, sw=1.2))
    parts.append(line(ox, 50, ox, 370, color=MUTED, sw=1.2))
    x_25 = ox + int(w_ax * (25 - (-40)) / (85 - (-40)))
    parts.append(line(x_25, 50, x_25, 370, color="#d0d7de", sw=1, dash="4 4"))
    parts.append(text(x_25, 385, "+25 °C", size=11, color=MUTED, anchor="middle"))

    for t_c in [-40, -20, 0, 50, 75, 85]:
        tx = ox + int(w_ax * (t_c - (-40)) / 125.0)
        parts.append(line(tx, oy - 3, tx, oy + 3, color=MUTED, sw=1))
        parts.append(text(tx, 385, f"{t_c:+d}°C", size=10, color=MUTED, anchor="middle"))

    for ppm_val in [20, 0, -20, -40, -60, -80]:
        py = oy - ppm_val * 2.1
        parts.append(line(ox - 3, py, ox + 3, py, color=MUTED, sw=1))
        parts.append(text(ox - 8, py + 4, f"{ppm_val:+d}", size=10, color=MUTED, anchor="end"))
    parts.append(text(ox - 8, 48, "Δf/f (ppm)", size=11, color=MUTED, anchor="end", bold=True))

    # 1. Камертонний кварц 32.768 кГц
    pts_fork = []
    for px in range(0, w_ax + 1, 6):
        t_c = -40 + (px / float(w_ax)) * 125.0
        df_ppm = -0.035 * ((t_c - 25.0) ** 2)
        py = oy - df_ppm * 2.1
        pts_fork.append((ox + px, py))
    d_fork = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_fork)
    parts.append(path_el(d_fork, stroke=POS, sw=2.2))

    # 2. Кварц AT-зрізу
    pts_at = []
    for px in range(0, w_ax + 1, 6):
        t_c = -40 + (px / float(w_ax)) * 125.0
        dt = t_c - 25.0
        df_ppm = -0.15 * dt + 0.00012 * (dt ** 3)
        py = oy - df_ppm * 2.1
        pts_at.append((ox + px, py))
    d_at = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_at)
    parts.append(path_el(d_at, stroke=NEG, sw=2.2))

    # 3. TCXO
    pts_tcxo = []
    for px in range(0, w_ax + 1, 6):
        t_c = -40 + (px / float(w_ax)) * 125.0
        dt = t_c - 25.0
        df_ppm = 1.2 * math.sin(dt * 0.08)
        py = oy - df_ppm * 2.1
        pts_tcxo.append((ox + px, py))
    d_tcxo = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_tcxo)
    parts.append(path_el(d_tcxo, stroke=FIELD, sw=2.5))

    # 4. OCXO
    parts.append(line(ox, oy, ox + w_ax, oy, color="#e67e22", sw=3))

    b_f, _, _ = textbox(190, 315, "32.768 кГц камертон: парабола (−80 ppm)", size=11,
                        fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b_f)

    b_a, _, _ = textbox(210, 115, "AT-зріз XTAL: кубічна S-крива (±20 ppm)", size=11,
                        fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(b_a)

    b_tc, _, _ = textbox(570, 160, "TCXO: компенсація (±1 ppm)", size=11,
                         fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b_tc)

    b_oc, _, _ = textbox(570, 75, "OCXO: термостат 75 °C (±0.01 ppm)", size=11,
                         fill="#fef5e7", stroke="#e67e22", color="#e67e22", bold=True)
    parts.append(b_oc)

    render(os.path.join(IMG, "temp-characteristics.svg"), W, H, *parts)


# ── Фігура 3: Дисперсія / девіація Аллана σ_y(τ) на логарифмічній шкалі ─────
def fig_allan_variance_curve():
    W, H = 760, 420
    parts = []
    parts.append(text(W/2, 24, "Девіація Аллана σ_y(τ): спектральні режими шуму та оптимальне вікно синхронізації", size=14.5, bold=True))

    ox, oy = 90, 340
    w_ax, h_ax = 600, 270

    parts.append(line(ox, oy, ox + w_ax, oy, color=MUTED, sw=1.5))
    parts.append(line(ox, oy, ox, oy - h_ax, color=MUTED, sw=1.5))
    parts.append(text(ox + w_ax + 10, oy + 4, "τ (с)", size=12, color=MUTED, anchor="start", bold=True))
    parts.append(text(ox, oy - h_ax - 10, "σ_y(τ)", size=12, color=MUTED, anchor="middle", bold=True))

    dec_x = ["10⁻³", "10⁻²", "10⁻¹", "1", "10", "10²", "10³", "10⁴"]
    for i, label in enumerate(dec_x):
        lx = ox + int(i * (w_ax / 7.0))
        parts.append(line(lx, oy, lx, oy - h_ax, color="#edf2f7", sw=1))
        parts.append(line(lx, oy - 3, lx, oy + 3, color=MUTED, sw=1))
        parts.append(text(lx, oy + 18, label, size=11, color=MUTED, anchor="middle"))

    dec_y = ["10⁻¹²", "10⁻¹¹", "10⁻¹⁰", "10⁻⁹", "10⁻⁸", "10⁻⁷"]
    for j, label in enumerate(dec_y):
        ly = oy - int(j * (h_ax / 5.0))
        parts.append(line(ox, ly, ox + w_ax, ly, color="#edf2f7", sw=1))
        parts.append(line(ox - 3, ly, ox + 3, ly, color=MUTED, sw=1))
        parts.append(text(ox - 8, ly + 4, label, size=11, color=MUTED, anchor="end"))

    pts_allan = [
        (ox + 0, oy - 230),
        (ox + 45, oy - 190),
        (ox + 85, oy - 155),
        (ox + 130, oy - 125),
        (ox + 171, oy - 100),
        (ox + 215, oy - 80),
        (ox + 257, oy - 65),
        (ox + 300, oy - 55),
        (ox + 342, oy - 50),
        (ox + 385, oy - 50),
        (ox + 428, oy - 58),
        (ox + 471, oy - 80),
        (ox + 514, oy - 115),
        (ox + 557, oy - 165),
        (ox + 600, oy - 225)
    ]
    d_allan = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts_allan)
    parts.append(path_el(d_allan, stroke=NEG, sw=3))

    tau_opt_x = ox + 360
    parts.append(line(tau_opt_x, oy, tau_opt_x, oy - 240, color=POS, sw=1.5, dash="4 4"))
    b_opt, _, _ = textbox(tau_opt_x, oy - 255, "τ_opt: точка зшивання з GNSS / PPS", size=11,
                          fill="#fdecea", stroke=POS, color=POS, bold=True)
    parts.append(b_opt)

    b_wpm, _, _ = textbox(ox + 90, oy - 215, "Білий шум фази (τ⁻¹)", size=10.5,
                          fill="#f4f6f8", stroke=MUTED, color=INK)
    parts.append(b_wpm)

    b_wfm, _, _ = textbox(ox + 180, oy - 130, "Білий шум частоти (τ⁻¹/²)", size=10.5,
                          fill="#f4f6f8", stroke=MUTED, color=INK)
    parts.append(b_wfm)

    b_flk, _, _ = textbox(ox + 360, oy - 25, "Флікер-плато (τ⁰, дно)", size=10.5,
                          fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True)
    parts.append(b_flk)

    b_rwf, _, _ = textbox(ox + 510, oy - 60, "Блукання частоти (τ⁺¹/²)", size=10.5,
                          fill="#f4f6f8", stroke=MUTED, color=INK)
    parts.append(b_rwf)

    b_drf, _, _ = textbox(ox + 550, oy - 195, "Дрейф і старіння (τ⁺¹)", size=10.5,
                          fill="#fdecea", stroke=POS, color=POS)
    parts.append(b_drf)

    render(os.path.join(IMG, "allan-variance-curve.svg"), W, H, *parts)


# ── Фігура 4: Цифровий PI-сервоконтролер синхронізації годинника ───────────
def fig_clock_servo_loop():
    W, H = 760, 360
    parts = []
    parts.append(text(W/2, 24, "Структура цифрового PI-сервоконтролера: синхронізація фази та швидкості ходу", size=14.5, bold=True))

    b_ref, _, _ = textbox(110, 90, "Еталонний час\nT_ref(k) [PPS/PTP]", size=12,
                          fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(b_ref)

    parts.append(circle(250, 90, 18, fill=BG, stroke=INK, sw=2))
    parts.append(text(250, 95, "−", size=20, color=POS, bold=True))
    parts.append(line(170, 90, 232, 90, color=INK, sw=1.8))
    parts.append(line(226, 86, 232, 90, color=INK, sw=1.8))
    parts.append(line(226, 94, 232, 90, color=INK, sw=1.8))

    parts.append(text(305, 75, "Похибка e_k", size=11, color=POS, bold=True))
    parts.append(line(268, 90, 350, 90, color=POS, sw=2))

    parts.append(circle(350, 90, 3.5, fill=INK, stroke=INK))
    parts.append(line(350, 90, 350, 60, color=INK, sw=1.5))
    parts.append(line(350, 60, 390, 60, color=INK, sw=1.5))
    b_p, _, _ = textbox(440, 60, "Пропорційна: K_p · e_k\n(корекція фазового зсуву)", size=10.5,
                        fill="#fdecea", stroke=POS, color=POS)
    parts.append(b_p)

    parts.append(line(350, 90, 350, 130, color=INK, sw=1.5))
    parts.append(line(350, 130, 390, 130, color=INK, sw=1.5))
    b_i, _, _ = textbox(440, 130, "Інтегральна: K_i · Σ e_j\n(оцінка швидкості ходу α̂)", size=10.5,
                        fill="#eafaf1", stroke=FIELD, color=FIELD)
    parts.append(b_i)

    parts.append(line(520, 60, 560, 60, color=INK, sw=1.5))
    parts.append(line(560, 60, 560, 80, color=INK, sw=1.5))
    parts.append(line(520, 130, 560, 130, color=INK, sw=1.5))
    parts.append(line(560, 130, 560, 100, color=INK, sw=1.5))

    parts.append(circle(560, 90, 14, fill=BG, stroke=INK, sw=1.8))
    parts.append(text(560, 95, "+", size=16, color=FIELD, bold=True))

    parts.append(line(574, 90, 610, 90, color=INK, sw=1.8))
    b_slewer, _, _ = textbox(670, 90, "Підстроювання темпу\nі фазовий акумулятор", size=11,
                             fill="#fef5e7", stroke="#e67e22", color="#e67e22", bold=True)
    parts.append(b_slewer)

    parts.append(line(670, 125, 670, 220, color=INK, sw=1.8))
    b_out, _, _ = textbox(670, 245, "Синхронізована шкала\nчасу T_local(t)", size=12,
                          fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    parts.append(b_out)

    parts.append(line(610, 245, 250, 245, color=NEG, sw=1.8))
    parts.append(line(250, 245, 250, 108, color=NEG, sw=1.8))
    parts.append(line(246, 114, 250, 108, color=NEG, sw=1.8))
    parts.append(line(254, 114, 250, 108, color=NEG, sw=1.8))
    parts.append(text(380, 230, "Зворотний зв'язок: поточний час місцевого годинника T_local", size=11, color=NEG))

    exp_y = 315
    b_ft1, _, _ = textbox(210, exp_y, "P-ланка усуває миттєвий розрив міток", size=10.5, fill=FILL, stroke=MUTED, color=INK)
    b_ft2, _, _ = textbox(540, exp_y, "I-ланка вчиться компенсувати постійний нахил кварцу (ppm)", size=10.5, fill=FILL, stroke=MUTED, color=INK)
    parts.append(b_ft1)
    parts.append(b_ft2)

    render(os.path.join(IMG, "clock-servo-loop.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_offset_skew_drift()
    fig_temp_characteristics()
    fig_allan_variance_curve()
    fig_clock_servo_loop()
    print("All figures generated successfully.")
