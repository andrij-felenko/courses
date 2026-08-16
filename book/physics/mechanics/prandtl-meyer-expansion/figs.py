# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

def nu_deg(M, gamma=1.4):
    if M <= 1.000001:
        return 0.0
    g_ratio = (gamma - 1.0) / (gamma + 1.0)
    term1 = math.sqrt((gamma + 1.0) / (gamma - 1.0)) * math.atan(math.sqrt(g_ratio * (M*M - 1.0)))
    term2 = math.atan(math.sqrt(M*M - 1.0))
    return math.degrees(term1 - term2)

def mu_deg(M):
    if M <= 1.000001:
        return 90.0
    return math.degrees(math.asin(1.0 / M))


# ── Фігура 1: Геометрія віяла розширення Прандтля — Майєра ─────────────────────
def fig_expansion_fan_geometry():
    W, H = 820, 520
    body = []
    
    body.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(W / 2, 38, "Геометрія веєра розширення Прандтля — Майєра біля опуклого кута", size=15, color=INK, bold=True))
    
    vx, vy = 320, 240
    
    body.append(line(50, vy, vx, vy, color="#334155", sw=3.5))
    for x_h in range(60, vx, 20):
        body.append(line(x_h, vy, x_h - 10, vy + 12, color="#94a3b8", sw=1.5))
        
    theta_deg = 20.0
    theta_rad = math.radians(theta_deg)
    wall_len = 340
    wx2 = vx + wall_len * math.cos(theta_rad)
    wy2 = vy + wall_len * math.sin(theta_rad)
    body.append(line(vx, vy, wx2, wy2, color="#334155", sw=3.5))
    for s in range(20, int(wall_len), 20):
        px = vx + s * math.cos(theta_rad)
        py = vy + s * math.sin(theta_rad)
        nx = px - 12 * math.sin(theta_rad) + 6 * math.cos(theta_rad)
        ny = py + 12 * math.cos(theta_rad) + 6 * math.sin(theta_rad)
        body.append(line(px, py, nx, ny, color="#94a3b8", sw=1.5))

    body.append(circle(vx, vy, 5, fill=NEG, stroke=INK))
    body.append(text(vx - 15, vy + 22, "Вершина V", size=11, color=NEG, bold=True))

    M1 = 1.5
    mu1_rad = math.asin(1.0 / M1)
    
    line1_len = 260
    lx1 = vx + line1_len * math.cos(mu1_rad)
    ly1 = vy - line1_len * math.sin(mu1_rad)
    body.append(line(vx, vy, lx1, ly1, color=POS, sw=2.2))
    
    M2 = 2.2
    mu2_rad = math.asin(1.0 / M2)
    line2_angle = mu2_rad - theta_rad
    line2_len_val = 300
    lx2 = vx + line2_len_val * math.cos(line2_angle)
    ly2 = vy - line2_len_val * math.sin(line2_angle)
    body.append(line(vx, vy, lx2, ly2, color=POS, sw=2.2))

    n_fan = 6
    for i in range(1, n_fan):
        frac = i / float(n_fan)
        ang = mu1_rad - frac * (mu1_rad - line2_angle)
        flen = 270 + i * 4
        fx = vx + flen * math.cos(ang)
        fy = vy - flen * math.sin(ang)
        body.append(line(vx, vy, fx, fy, color="#94a3b8", sw=1.2, dash="4,3"))

    body.append(text(vx + 150, vy - 100, "Віяло хвиль Маха", size=12, color=POS, bold=True))
    body.append(text(vx + 150, vy - 84, "(безперервне розширення)", size=11, color=MUTED))

    body.append(arrow(80, vy - 60, 200, vy - 60, color=POS, sw=2.0))
    body.append(arrow(80, vy - 120, 200, vy - 120, color=POS, sw=2.0))
    
    body.append(text(120, vy - 140, "Набігаючий потік", size=12, color=INK, bold=True))
    body.append(text(120, vy - 80, "M₁ = 1.5 > 1", size=12, color=POS, bold=True))
    body.append(text(120, vy - 40, "p₁, T₁, ρ₁", size=11, color=INK))

    arr2_x1 = vx + 140 * math.cos(theta_rad)
    arr2_y1 = vy + 140 * math.sin(theta_rad) - 60
    arr2_x2 = arr2_x1 + 120 * math.cos(theta_rad)
    arr2_y2 = arr2_y1 + 120 * math.sin(theta_rad)
    body.append(arrow(arr2_x1, arr2_y1, arr2_x2, arr2_y2, color=POS, sw=2.0))
    
    txt2_x = arr2_x1 + 40
    txt2_y = arr2_y1 + 45
    body.append(text(txt2_x + 60, txt2_y - 20, "Повернений потік", size=12, color=INK, bold=True))
    body.append(text(txt2_x + 60, txt2_y, "M₂ = 2.2 > M₁", size=12, color=POS, bold=True))
    body.append(text(txt2_x + 60, txt2_y + 20, "p₂ < p₁, T₂ < T₁", size=11, color=INK))
    body.append(text(txt2_x + 60, txt2_y + 40, "s₂ = s₁ (ізоентропійний)", size=11, color="#16a34a", bold=True))

    body.append(text(lx1 + 10, ly1 + 5, "Перша лінія Маха (μ₁)", size=11, color=POS, bold=True))
    body.append(text(lx2 + 10, ly2 + 5, "Остання лінія Маха (μ₂)", size=11, color=POS, bold=True))

    body.append(line(vx, vy, vx + 180, vy, color=MUTED, sw=1.0, dash="3,3"))
    body.append(text(vx + 140, vy + 24, f"Δθ = {int(theta_deg)}°", size=12, color=NEG, bold=True))

    box = fitbox(40, H - 90, W - 80, 70,
                 "Ключові властивості течії Прандтля — Майєра:\n"
                 "• Течія повертає у бік опуклого кута без утворення скачка ущільнення.\n"
                 "• Розширення є гладким, ізоентропійним (Δs = 0) та супроводжується розгоном потоку (M₂ > M₁).\n"
                 "• Повний тиск не змінюється: p₀₂ = p₀₁.",
                 size=11.5, fill="#f1f5f9", stroke="#64748b", pad=8)
    body.append(box)

    render(os.path.join(OUT, "expansion-fan-geometry.svg"), W, H, *body,
           title="Геометрія веєра розширення Прандтля — Майєра біля опуклого кута")


# ── Фігура 2: Зміна термодинамічних параметрів ───────────────────────────────
def fig_thermodynamic_state_fan():
    W, H = 820, 500
    body = []
    
    body.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(W / 2, 36, "Зміна термодинамічних параметрів газу вздовж веєра розширення", size=15, color=INK, bold=True))

    gx, gy, gw, gh = 90, 80, 680, 320
    
    body.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.0))
    for i in range(1, 5):
        y_grid = gy + i * (gh / 5)
        body.append(line(gx, y_grid, gx + gw, y_grid, color="#f1f5f9", sw=1.0))
    for j in range(1, 5):
        x_grid = gx + j * (gw / 5)
        body.append(line(x_grid, gy, x_grid, gy + gh, color="#f1f5f9", sw=1.0))

    M1 = 1.5
    nu1 = nu_deg(M1)
    
    def p_ratio(M):
        return ( (1.0 + 0.2*M1*M1) / (1.0 + 0.2*M*M) ) ** 3.5
    def T_ratio(M):
        return (1.0 + 0.2*M1*M1) / (1.0 + 0.2*M*M)

    pts_M = []
    pts_p = []
    pts_T = []
    pts_p0 = []
    
    n_pts = 60
    for k in range(n_pts + 1):
        dtheta = (k / float(n_pts)) * 30.0
        nu_k = nu1 + dtheta
        M_k = max(1.001, M1 + dtheta * 0.045)
        for _ in range(10):
            f_val = nu_deg(M_k) - nu_k
            df_dM = math.sqrt(max(1.0001, M_k*M_k) - 1.0) / (M_k * (1.0 + 0.2*M_k*M_k))
            M_k = max(1.0001, M_k - f_val / df_dM)
            
        x_pixel = gx + (dtheta / 30.0) * gw
        
        y_M = gy + gh - ((M_k - 1.0) / 2.2) * gh
        y_p = gy + gh - (p_ratio(M_k)) * (gh * 0.8)
        y_T = gy + gh - (T_ratio(M_k)) * (gh * 0.8)
        y_p0 = gy + gh - 1.0 * (gh * 0.8)
        
        pts_M.append(f"{x_pixel:.1f},{y_M:.1f}")
        pts_p.append(f"{x_pixel:.1f},{y_p:.1f}")
        pts_T.append(f"{x_pixel:.1f},{y_T:.1f}")
        pts_p0.append(f"{x_pixel:.1f},{y_p0:.1f}")

    body.append(f'<polyline points="{" ".join(pts_p0)}" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-dasharray="6,3"/>')
    body.append(f'<polyline points="{" ".join(pts_M)}" fill="none" stroke="{POS}" stroke-width="3.0"/>')
    body.append(f'<polyline points="{" ".join(pts_p)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')
    body.append(f'<polyline points="{" ".join(pts_T)}" fill="none" stroke="#d97706" stroke-width="2.5"/>')

    body.append(rect(gx + 20, gy + 15, 230, 115, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    body.append(line(gx + 30, gy + 32, gx + 60, gy + 32, color=POS, sw=3.0))
    body.append(text(gx + 70, gy + 36, "Число Маха M (зростає)", size=11, color=POS, bold=True))
    
    body.append(line(gx + 30, gy + 57, gx + 60, gy + 57, color=NEG, sw=2.5))
    body.append(text(gx + 70, gy + 61, "Статичний тиск p / p₁ (падає)", size=11, color=NEG, bold=True))
    
    body.append(line(gx + 30, gy + 82, gx + 60, gy + 82, color="#d97706", sw=2.5))
    body.append(text(gx + 70, gy + 86, "Статична температура T / T₁", size=11, color="#d97706", bold=True))
    
    body.append(line(gx + 30, gy + 107, gx + 60, gy + 107, color="#16a34a", sw=2.5, dash="6,3"))
    body.append(text(gx + 70, gy + 111, "Повний тиск p₀ / p₀₁ = 1 (const)", size=11, color="#16a34a", bold=True))

    body.append(text(gx + gw / 2, gy + gh + 35, "Поточний кут повороту потоку θ (градуси)", size=12, color=INK, bold=True))
    body.append(text(gx - 45, gy + gh / 2, "Параметри потоку", size=12, color=INK, bold=True))

    for theta_val in [0, 5, 10, 15, 20, 25, 30]:
        x_t = gx + (theta_val / 30.0) * gw
        body.append(line(x_t, gy + gh, x_t, gy + gh + 5, color=INK, sw=1.2))
        body.append(text(x_t, gy + gh + 20, f"{theta_val}°", size=11, color=INK))

    body.append(text(W / 2, H - 15, "При розширенні кінетична енергія спрямованого руху зростає за рахунок спаду внутрішньої теплової енергії.", size=11, color=MUTED))

    render(os.path.join(OUT, "thermodynamic-state-fan.svg"), W, H, *body,
           title="Зміна термодинамічних параметрів газу впродовж веєра розширення")


# ── Фігура 3: Графік функції Прандтля — Майєра ──────────────────────────────
def fig_prandtl_meyer_function_graph():
    W, H = 820, 520
    body = []
    
    body.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(W / 2, 36, "Функція Прандтля — Майєра ν(M) та кут Маха μ(M)", size=15, color=INK, bold=True))

    gx, gy, gw, gh = 80, 75, 700, 340
    body.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.0))

    for i in range(1, 7):
        y_g = gy + i * (gh / 7)
        body.append(line(gx, y_g, gx + gw, y_g, color="#f1f5f9", sw=1.0))
    for j in range(1, 9):
        x_g = gx + j * (gw / 8)
        body.append(line(x_g, gy, x_g, gy + gh, color="#f1f5f9", sw=1.0))

    M_min, M_max = 1.0, 5.0
    ang_min, ang_max = 0.0, 140.0

    pts_nu = []
    pts_mu = []
    
    n_pts = 100
    for k in range(n_pts + 1):
        M_val = M_min + (k / float(n_pts)) * (M_max - M_min)
        nu_val = nu_deg(M_val)
        mu_val = mu_deg(M_val)
        
        x_p = gx + ((M_val - M_min) / (M_max - M_min)) * gw
        y_nu = gy + gh - ((nu_val - ang_min) / (ang_max - ang_min)) * gh
        y_mu = gy + gh - ((mu_val - ang_min) / (ang_max - ang_min)) * gh
        
        pts_nu.append(f"{x_p:.1f},{y_nu:.1f}")
        pts_mu.append(f"{x_p:.1f},{y_mu:.1f}")

    y_asymptote = gy + gh - ((130.45 - ang_min) / (ang_max - ang_min)) * gh
    body.append(line(gx, y_asymptote, gx + gw, y_asymptote, color=NEG, sw=1.5, dash="6,4"))
    body.append(text(gx + gw - 140, y_asymptote - 8, "ν_max ≈ 130.45° (для γ = 1.4)", size=11, color=NEG, bold=True))

    body.append(f'<polyline points="{" ".join(pts_nu)}" fill="none" stroke="{POS}" stroke-width="3.0"/>')
    body.append(f'<polyline points="{" ".join(pts_mu)}" fill="none" stroke="#d97706" stroke-width="2.5"/>')

    check_M = [1.0, 2.0, 3.0, 4.0, 5.0]
    for m_c in check_M:
        x_c = gx + ((m_c - M_min) / (M_max - M_min)) * gw
        nu_c = nu_deg(m_c)
        mu_c = mu_deg(m_c)
        
        y_c_nu = gy + gh - ((nu_c - ang_min) / (ang_max - ang_min)) * gh
        y_c_mu = gy + gh - ((mu_c - ang_min) / (ang_max - ang_min)) * gh
        
        body.append(circle(x_c, y_c_nu, 4, fill=POS, stroke=INK))
        body.append(circle(x_c, y_c_mu, 4, fill="#d97706", stroke=INK))
        
        if m_c == 1.0:
            body.append(text(x_c + 15, y_c_nu - 10, "ν(1) = 0°", size=10.5, color=POS, bold=True))
            body.append(text(x_c + 15, y_c_mu - 10, "μ(1) = 90°", size=10.5, color="#d97706", bold=True))
        elif m_c == 2.0:
            body.append(text(x_c + 10, y_c_nu - 10, f"ν = {nu_c:.1f}°", size=10.5, color=POS, bold=True))
            body.append(text(x_c + 10, y_c_mu + 18, f"μ = {mu_c:.1f}°", size=10.5, color="#d97706", bold=True))
        elif m_c == 3.0:
            body.append(text(x_c - 35, y_c_nu - 10, f"ν = {nu_c:.1f}°", size=10.5, color=POS, bold=True))
            body.append(text(x_c + 10, y_c_mu + 18, f"μ = {mu_c:.1f}°", size=10.5, color="#d97706", bold=True))

    body.append(text(gx + gw / 2, gy + gh + 35, "Число Маха M", size=12, color=INK, bold=True))
    body.append(text(gx - 40, gy + gh / 2, "Кут (градуси)", size=12, color=INK, bold=True))

    for m_val in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
        x_t = gx + ((m_val - M_min) / (M_max - M_min)) * gw
        body.append(line(x_t, gy + gh, x_t, gy + gh + 5, color=INK, sw=1.2))
        body.append(text(x_t, gy + gh + 20, f"{m_val:.1f}", size=11, color=INK))

    for a_val in range(0, 141, 20):
        y_t = gy + gh - ((a_val - ang_min) / (ang_max - ang_min)) * gh
        body.append(line(gx - 5, y_t, gx, y_t, color=INK, sw=1.2))
        body.append(text(gx - 20, y_t + 4, f"{a_val}°", size=10.5, color=INK))

    body.append(rect(gx + 30, gy + 20, 260, 60, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    body.append(line(gx + 40, gy + 38, gx + 70, gy + 38, color=POS, sw=3.0))
    body.append(text(gx + 80, gy + 42, "Функція Прандтля — Майєра ν(M)", size=11, color=POS, bold=True))
    body.append(line(gx + 40, gy + 60, gx + 70, gy + 60, color="#d97706", sw=2.5))
    body.append(text(gx + 80, gy + 64, "Кут Маха μ(M) = arcsin(1/M)", size=11, color="#d97706", bold=True))

    body.append(text(W / 2, H - 15, "Функція ν(M) визначає кут повороту звукового потоку (M=1) до досягнення даного числа Маха M.", size=11, color=MUTED))

    render(os.path.join(OUT, "prandtl-meyer-function-graph.svg"), W, H, *body,
           title="Функція Прандтля — Майєра ν(M) та кут Маха μ(M)")


# ── Фігура 4: Обтікання ромбоподібного надзвукового профілю ───────────────────
def fig_supersonic_airfoil_flow():
    W, H = 820, 500
    body = []
    
    body.append(rect(10, 10, W - 20, H - 20, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(W / 2, 36, "Структура течії при обтіканні надзвукового ромбоподібного профілю", size=15, color=INK, bold=True))

    lex, ley = 180, 230
    midx = 420
    t_half = 45
    mid_up_y = ley - t_half
    mid_down_y = ley + t_half
    tex, tey = 660, 230

    pts_airfoil = f"{lex},{ley} {midx},{mid_up_y} {tex},{tey} {midx},{mid_down_y}"
    body.append(f'<polygon points="{pts_airfoil}" fill="#cbd5e1" stroke="{INK}" stroke-width="2.5"/>')
    body.append(line(midx, mid_up_y, midx, mid_down_y, color="#64748b", sw=1.5, dash="4,3"))

    # Скачки передні
    body.append(line(lex, ley, lex - 110, ley - 130, color=NEG, sw=2.5))
    body.append(line(lex, ley, lex - 110, ley + 130, color=NEG, sw=2.5))
    body.append(text(lex - 130, ley - 135, "Косий скачок p ↑", size=11, color=NEG, bold=True))
    body.append(text(lex - 130, ley + 145, "Косий скачок p ↑", size=11, color=NEG, bold=True))

    # Віяла розширення
    for da in range(-25, 30, 10):
        rad = math.radians(da - 65)
        fx = midx + 120 * math.cos(rad)
        fy = mid_up_y + 120 * math.sin(rad)
        body.append(line(midx, mid_up_y, fx, fy, color=POS, sw=1.5, dash="3,2"))
    body.append(text(midx - 90, mid_up_y - 115, "Віяло Прандтля — Майєра (p ↓, M ↑)", size=11, color=POS, bold=True))

    for da in range(-25, 30, 10):
        rad = math.radians(da + 65)
        fx = midx + 120 * math.cos(rad)
        fy = mid_down_y + 120 * math.sin(rad)
        body.append(line(midx, mid_down_y, fx, fy, color=POS, sw=1.5, dash="3,2"))
    body.append(text(midx - 90, mid_down_y + 75, "Віяло Прандтля — Майєра (p ↓, M ↑)", size=11, color=POS, bold=True))

    # Скачки задні
    body.append(line(tex, tey, tex + 110, tey - 75, color=NEG, sw=2.0))
    body.append(line(tex, tey, tex + 110, tey + 75, color=NEG, sw=2.0))
    body.append(text(tex + 20, tey - 85, "Задній скачок", size=11, color=NEG, bold=True))
    body.append(text(tex + 20, tey + 95, "Задній скачок", size=11, color=NEG, bold=True))

    # Набігаючий потік
    body.append(arrow(30, ley, 120, ley, color=POS, sw=2.5))
    body.append(text(40, ley - 25, "M∞ > 1", size=13, color=POS, bold=True))

    # Епюра тиску
    body.append(text(lex + 80, ley - t_half / 2 - 10, "+ Δp", size=11, color=NEG, bold=True))
    body.append(text(midx + 80, ley - t_half / 2 - 10, "- Δp", size=11, color=POS, bold=True))

    box = fitbox(40, H - 85, W - 80, 65,
                 "Утворення хвильового опору надзвукового профілю:\n"
                 "• На передньому клині тиск підвищується через косий скачок ущільнення (+Δp).\n"
                 "• У зломі профілю тиск різко падає через віяло розширення Прандтля — Майєра (-Δp).\n"
                 "• Різниця тисків між передньою та задньою поверхнями створює хвильовий опір (Wave Drag).",
                 size=11.5, fill="#f1f5f9", stroke="#64748b", pad=8)
    body.append(box)

    render(os.path.join(OUT, "supersonic-airfoil-flow.svg"), W, H, *body,
           title="Обтікання ромбоподібного надзвукового профілю")


if __name__ == "__main__":
    fig_expansion_fan_geometry()
    fig_thermodynamic_state_fan()
    fig_prandtl_meyer_function_graph()
    fig_supersonic_airfoil_flow()
    print("Figures generated successfully.")
