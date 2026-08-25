# -*- coding: utf-8 -*-
"""Фігури до теми «Метод усереднення Боголюбова — Митропольського».
Запуск: python figs.py → генерує SVG файли у ./img/
Стиль та допоміжні функції — зі спільного svgkit.
"""
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

MAIN = "#2457d6"
ACCENT = "#c0392b"
GREEN = "#27ae60"
BORDER = "#d0d7de"

def head_at(x, y, dx, dy, color=INK, size=8):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.4, by + ny * size * 0.4,
               bx - nx * size * 0.4, by - ny * size * 0.4, color))

def varrow(x1, y1, x2, y2, color=LINE, sw=2.0, head=9):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)

# ── Фігура 1: Принцип усереднення — швидкі осциляції та повільна огинаюча ──────
def fig_averaging_principle():
    W, H = 820, 400
    f = []

    f.append(text(W / 2, 28, "Принцип усереднення: відокремлення швидких осциляцій від повільної еволюції", size=15, bold=True))

    # Лівий графік: x(t) зі швидкими осциляціями та повільною огинаючою a(t)
    x0, y0 = 50, 65
    w_p, h_p = 340, 300
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x0 + w_p / 2, y0 + 24, "Динаміка осцилятора x(t) та амплітуда a(t)", size=12, bold=True))

    cx1, cy1 = x0 + 40, y0 + 160

    # Осі
    f.append(varrow(x0 + 30, cy1, x0 + w_p - 20, cy1, color=MUTED, sw=1.5))
    f.append(text(x0 + w_p - 15, cy1 + 18, "t", size=12, color=MUTED, anchor="end"))
    f.append(varrow(cx1, y0 + h_p - 20, cx1, y0 + 40, color=MUTED, sw=1.5))
    f.append(text(cx1 - 12, y0 + 48, "x", size=12, color=MUTED, anchor="end"))

    pts_exact = []
    pts_env_plus = []
    pts_env_minus = []

    a0 = 0.5
    eps = 0.15
    omega = 2.5

    for i in range(201):
        t_val = i * 0.1
        px = cx1 + t_val * 13.5
        if px > x0 + w_p - 25:
            break
        a_val = 2.0 / math.sqrt(1.0 + (4.0 / (a0*a0) - 1.0) * math.exp(-eps * t_val))
        x_val = a_val * math.cos(omega * t_val)

        py_exact = cy1 - x_val * 55.0
        py_env_p = cy1 - a_val * 55.0
        py_env_m = cy1 + a_val * 55.0

        pts_exact.append((px, py_exact))
        pts_env_plus.append((px, py_env_p))
        pts_env_minus.append((px, py_env_m))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_env_plus), ACCENT))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_env_minus), ACCENT))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_exact), MAIN))

    # Позначки періодів
    f.append(line(cx1 + 10, y0 + 265, cx1 + 10 + 2*math.pi/omega*13.5, y0 + 265, color=GREEN, sw=2.0))
    f.append(text(cx1 + 10 + math.pi/omega*13.5, y0 + 282, "T = 2π/ω₀ (швидкий)", size=10, color=GREEN, bold=True))

    # Правий графік: Фазовий портрет (x, dx/dt)
    x1, y1 = 430, 65
    f.append(rect(x1, y1, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x1 + w_p / 2, y1 + 24, "Фазова спіраль та граничний цикл (a* = 2)", size=12, bold=True))

    cx2, cy2 = x1 + w_p / 2, y1 + 160

    # Осі фазової площини
    f.append(varrow(x1 + 25, cy2, x1 + w_p - 25, cy2, color=MUTED, sw=1.5))
    f.append(text(x1 + w_p - 20, cy2 + 18, "x", size=12, color=MUTED, anchor="end"))
    f.append(varrow(cx2, y1 + h_p - 20, cx2, y1 + 40, color=MUTED, sw=1.5))
    f.append(text(cx2 - 12, y1 + 48, "dx/dt", size=12, color=MUTED, anchor="end"))

    # Граничний цикл (коло a=2)
    pts_limit = []
    for i in range(101):
        phi = i * 2.0 * math.pi / 100.0
        px = cx2 + 2.0 * 55.0 * math.cos(phi)
        py = cy2 - 2.0 * 55.0 * math.sin(phi)
        pts_limit.append((px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="5,4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_limit), ACCENT))

    # Фазова спіраль розгортання від a0=0.5
    pts_spiral = []
    for i in range(301):
        t_val = i * 0.08
        a_val = 2.0 / math.sqrt(1.0 + (4.0 / (a0*a0) - 1.0) * math.exp(-eps * t_val))
        phi = omega * t_val
        px = cx2 + a_val * 55.0 * math.cos(phi)
        py = cy2 - a_val * 55.0 * math.sin(phi)
        pts_spiral.append((px, py))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_spiral), MAIN))

    f.append(text(cx2 + 75, cy2 - 75, "Граничний цикл", size=11, color=ACCENT, bold=True))

    out_file = os.path.join(IMG, "averaging-principle.svg")
    render(out_file, W, H, *f)

# ── Фігура 2: Заміна змінних Боголюбова — Митропольського ──────────────────
def fig_coordinate_transformation():
    W, H = 820, 360
    f = []

    f.append(text(W / 2, 28, "Геометрія заміни змінних Боголюбова: x = ξ + ε u₁(t, ξ)", size=15, bold=True))

    # Блок вихідних осцилюючих змінних x
    b1, w1, h1 = textbox(180, 160, "Вихідний простір змінних x(t)\n\ndx/dt = ε X(t, x)\n(Містить швидкі осциляції)",
                         size=13, pad=14, fill="#FFF5F5", stroke=ACCENT, sw=2.0)
    f.append(b1)

    # Блок усереднених згладжених змінних \xi
    b2, w2, h2 = textbox(640, 160, "Усереднений простір змінних ξ(t)\n\ndξ/dt = ε A₁(ξ) + ε² A₂(ξ)\n(Автономна згладжена динаміка)",
                         size=13, pad=14, fill="#F0F9FF", stroke=MAIN, sw=2.0)
    f.append(b2)

    # Стрілка прямого перетворення
    f.append(varrow(310, 130, 500, 130, color=GREEN, sw=2.5))
    f.append(text(405, 118, "Заміна Боголюбова x = ξ + ε u₁(t, ξ)", size=12, color=GREEN, bold=True))

    # Стрілка зворотного зв'язку / усереднення
    f.append(varrow(500, 190, 310, 190, color=MUTED, sw=2.0))
    f.append(text(405, 210, "Оператор усереднення ⟨X(t, ξ)⟩", size=12, color=MUTED, bold=True))

    # Нижня пояснювальна картка
    b3, w3, h3 = textbox(W / 2, 300, "Функція u₁(t, ξ) виключає пульсації: ∂u₁/∂t = X(t, ξ) - A₁(ξ)\nУсереднене векторне поле A₁(ξ) = (1/T) ∫ X(t, ξ) dt описує системний дрейф",
                         size=12, pad=12, fill="#FAFBFD", stroke=BORDER, sw=1.2)
    f.append(b3)

    out_file = os.path.join(IMG, "coordinate-transformation.svg")
    render(out_file, W, H, *f)


# ── Фігура 3: Ефективний потенціал маятника Капіци ─────────────────────────
def fig_kapitza_potential():
    W, H = 820, 420
    f = []

    f.append(text(W / 2, 28, "Ефективний потенціал V_eff(θ) маятника Капіци з вібруючим підвісом", size=15, bold=True))

    # Лівий графік: потенціал з вібрацією та без
    x0, y0 = 50, 65
    w_p, h_p = 370, 320
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x0 + w_p / 2, y0 + 24, "Потенційні криві V(θ)", size=12, bold=True))

    cx1, cy1 = x0 + w_p / 2, y0 + 170

    # Осі
    f.append(varrow(x0 + 25, cy1, x0 + w_p - 25, cy1, color=MUTED, sw=1.5))
    f.append(text(x0 + w_p - 20, cy1 + 18, "θ", size=12, color=MUTED, anchor="end"))
    f.append(varrow(cx1, y0 + h_p - 20, cx1, y0 + 40, color=MUTED, sw=1.5))
    f.append(text(cx1 - 12, y0 + 48, "V_eff", size=12, color=MUTED, anchor="end"))

    # Крива звичайного потенціалу V_0 = mgl (1 - cos \theta)
    pts_v0 = []
    pts_veff = []

    for i in range(101):
        theta = (i - 50) * math.pi / 45.0
        px = cx1 + (i - 50) * 3.2

        v0 = 1.0 - math.cos(theta)
        py0 = cy1 - v0 * 60.0 + 40.0
        pts_v0.append((px, py0))

        veff = (1.0 - math.cos(theta)) + 0.95 * (math.sin(theta)**2)
        pyeff = cy1 - veff * 60.0 + 40.0
        pts_veff.append((px, pyeff))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4,4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_v0 if y0+40 <= p[1] <= y0+h_p-20), MUTED))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_veff if y0+40 <= p[1] <= y0+h_p-20), ACCENT))

    # Легенда
    f.append(line(x0 + 35, y0 + 290, x0 + 65, y0 + 290, color=MUTED, sw=2.0, dash="4,4"))
    f.append(text(x0 + 72, y0 + 294, "Без вібрації (нестійкий при θ=π)", size=11, color=INK, anchor="start"))

    f.append(line(x0 + 210, y0 + 290, x0 + 240, y0 + 290, color=ACCENT, sw=2.5))
    f.append(text(x0 + 247, y0 + 294, "З вібрацією V_eff (стійка яма при θ=π)", size=11, color=INK, anchor="start"))

    # Правий схематичний малюнок маятника Капіци
    x1, y1 = 460, 65
    w_p2 = 310
    f.append(rect(x1, y1, w_p2, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))
    f.append(text(x1 + w_p2 / 2, y1 + 24, "Вертикальна стабілізація маятника", size=12, bold=True))

    cx2, cy2 = x1 + w_p2 / 2, y1 + 130

    # Шарнір підвісу з вібрацією z(t) = a cos(nu t)
    f.append(varrow(cx2, cy2 + 35, cx2, cy2 - 35, color=GREEN, sw=2.5))
    f.append(text(cx2 + 25, cy2, "z(t) = a cos(νt)", size=11, color=GREEN, bold=True, anchor="start"))

    # Шарнір
    f.append(circle(cx2, cy2, 6, fill=INK, stroke=INK))

    # Стрижень маятника вгору (θ = π) з малими коливаннями
    l_len = 110
    theta_val = 0.15
    px_bob = cx2 + l_len * math.sin(theta_val)
    py_bob = cy2 - l_len * math.cos(theta_val)

    f.append(line(cx2, cy2, px_bob, py_bob, color=MAIN, sw=3.0))
    f.append(circle(px_bob, py_bob, 14, fill=ACCENT, stroke=INK, sw=1.5))
    f.append(text(px_bob + 22, py_bob + 4, "m", size=12, color=INK, bold=True))

    # Позначка стійкої кутової ями
    f.append(text(cx2, cy2 - l_len - 25, "Стійка вертикальна позиція (θ = π)", size=11, color=ACCENT, bold=True))

    out_file = os.path.join(IMG, "kapitza-potential.svg")
    render(out_file, W, H, *f)


# ── Фігура 4: Проходження через нелінійний резонанс ─────────────────────────
def fig_resonance_passage():
    W, H = 820, 380
    f = []

    f.append(text(W / 2, 28, "Проходження через нелінійний резонанс за теорією Митропольського", size=15, bold=True))

    x0, y0 = 60, 65
    w_p, h_p = 700, 290
    f.append(rect(x0, y0, w_p, h_p, fill='#FAFBFD', stroke=BORDER, sw=1.2, rx=6))

    cx0, cy0 = x0 + 50, y0 + 230

    # Осі графіку амплітуди від зовнішньої частоти ν(τ)
    f.append(varrow(x0 + 30, cy0, x0 + w_p - 30, cy0, color=MUTED, sw=1.5))
    f.append(text(x0 + w_p - 25, cy0 + 18, "Зовнішня частота ν(τ)", size=12, color=MUTED, anchor="end"))
    f.append(varrow(cx0, y0 + h_p - 20, cx0, y0 + 35, color=MUTED, sw=1.5))
    f.append(text(cx0 - 12, y0 + 42, "Амплітуда a", size=12, color=MUTED, anchor="end"))

    # Стаціонарна АЧХ нелінійного осцилятора (з нахилом скелетної кривої)
    pts_skelet = []

    for i in range(101):
        a_val = i * 0.02
        nu_res = 1.0 + 0.3 * a_val * a_val
        px = cx0 + (nu_res - 0.7) * 450.0
        py = cy0 - a_val * 90.0
        pts_skelet.append((px, py))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_skelet if x0+30 <= p[0] <= x0+w_p-30), MUTED))
    f.append(text(cx0 + 260, cy0 - 165, "Скелетна крива ν = ω₀(a)", size=11, color=MUTED))

    # Динамічні траєкторії при повільному розгоні частоти (теорія Митропольського)
    pts_dyn_slow = []

    for i in range(151):
        nu_val = 0.7 + i * 0.006
        px = cx0 + (nu_val - 0.7) * 450.0

        if nu_val < 1.0:
            a_dyn = 0.3 + 0.2 / (1.0 + (1.0 - nu_val)**2 * 40.0)
        elif nu_val < 1.35:
            a_dyn = 0.5 + (nu_val - 1.0) * 3.2 - (nu_val - 1.0)**2 * 4.0
        else:
            a_dyn = 0.3 + 0.1 / (1.0 + (nu_val - 1.35)**2 * 30.0)

        py_dyn = cy0 - a_dyn * 90.0
        pts_dyn_slow.append((px, py_dyn))

    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' %
             (" ".join("%.1f,%.1f" % p for p in pts_dyn_slow), ACCENT))

    # Захоплення частоти та максимальний пік
    f.append(circle(cx0 + 290, cy0 - 150, 6, fill=ACCENT, stroke=INK))
    f.append(text(cx0 + 290, cy0 - 168, "Динамічний пік (запізнення зриву)", size=11, color=ACCENT, bold=True))

    f.append(varrow(cx0 + 100, cy0 - 30, cx0 + 230, cy0 - 30, color=MAIN, sw=2.0))
    f.append(text(cx0 + 165, cy0 - 42, "Повільний розгон dν/dt = ε γ", size=11, color=MAIN, bold=True))

    out_file = os.path.join(IMG, "resonance-passage.svg")
    render(out_file, W, H, *f)


def main():
    fig_averaging_principle()
    fig_coordinate_transformation()
    fig_kapitza_potential()
    fig_resonance_passage()
    print("Фігури успішно створені в ./img/")

if __name__ == "__main__":
    main()
