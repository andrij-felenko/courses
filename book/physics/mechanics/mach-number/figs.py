# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Конус Маха на різних швидкостях ────────────────────────────────
def fig_mach_cone():
    W, H = 820, 520
    body = []
    
    # 4 панелі: M=0, M=0.5, M=1.0, M=1.8
    panels = [
        ("M = 0 (нерухоме)", 0.0, 110, 150),
        ("M = 0.5 (дозвук)", 0.5, 310, 150),
        ("M = 1.0 (звук)", 1.0, 510, 150),
        ("M = 1.8 (надзвук)", 1.8, 710, 150)
    ]
    
    for title_str, M, cx, cy in panels:
        # Фон панелі (без stroke, щоб не було перетинів рамок із текстом)
        body.append(rect(cx - 90, cy - 110, 180, 250, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
        body.append(text(cx, cy - 88, title_str, size=12.5, color=INK, bold=True))
        
        scale = 15.0
        n_steps = 4
        
        if M == 0.0:
            for i in range(1, n_steps + 1):
                r = i * scale
                body.append(circle(cx, cy, r, fill="none", stroke=NEG, sw=1.2))
            body.append(circle(cx, cy, 4, fill=POS, stroke=POS))
            body.append(text(cx, cy + 85, "сферичні хвилі", size=11, color=MUTED))
            body.append(text(cx, cy + 102, "симетричні", size=11, color=MUTED))
            
        elif M == 0.5:
            for k in range(n_steps + 1):
                x_k = cx - (n_steps - k) * M * scale
                r_k = (n_steps - k) * scale
                if r_k > 0:
                    body.append(circle(x_k, cy, r_k, fill="none", stroke=NEG, sw=1.2))
            x_curr = cx
            body.append(arrow(cx - 40, cy, cx + 25, cy, color=POS, sw=1.5))
            body.append(circle(x_curr, cy, 4, fill=POS, stroke=POS))
            body.append(text(cx, cy + 85, "збурення біжать", size=11, color=MUTED))
            body.append(text(cx, cy + 102, "попереду тіла", size=11, color=MUTED))
            
        elif M == 1.0:
            for k in range(n_steps + 1):
                x_k = cx - (n_steps - k) * M * scale
                r_k = (n_steps - k) * scale
                if r_k > 0:
                    body.append(circle(x_k, cy, r_k, fill="none", stroke=NEG, sw=1.2))
            x_curr = cx
            body.append(line(x_curr, cy - 65, x_curr, cy + 65, color=POS, sw=2.0))
            body.append(circle(x_curr, cy, 4, fill=POS, stroke=POS))
            body.append(text(cx, cy + 85, "фронт звукового", size=11, color=POS, bold=True))
            body.append(text(cx, cy + 102, "бар'єра (M = 1)", size=11, color=POS, bold=True))
            
        elif M == 1.8:
            for k in range(n_steps + 1):
                x_k = cx - 35 - (n_steps - k) * 0.8 * scale
                r_k = (n_steps - k) * (0.8 / M) * scale
                if r_k > 0:
                    body.append(circle(x_k, cy, r_k, fill="none", stroke=NEG, sw=1.0))
            
            x_curr = cx + 35
            mu_rad = math.asin(1.0 / M)
            length = 90
            dx = length * math.cos(mu_rad)
            dy = length * math.sin(mu_rad)
            
            poly_pts = f"{x_curr},{cy} {x_curr - dx},{cy - dy} {x_curr - dx},{cy + dy}"
            body.append(f'<polygon points="{poly_pts}" fill="#fee2e2" opacity="0.6"/>')
            
            body.append(line(x_curr, cy, x_curr - dx, cy - dy, color=POS, sw=2.0))
            body.append(line(x_curr, cy, x_curr - dx, cy + dy, color=POS, sw=2.0))
            body.append(circle(x_curr, cy, 5, fill=POS, stroke=POS))
            
            mu_deg = math.degrees(mu_rad)
            body.append(text(x_curr - 48, cy - 6, f"μ = {mu_deg:.1f}°", size=11, color=POS, bold=True))
            body.append(text(cx, cy + 85, "конус Маха", size=11, color=POS, bold=True))
            body.append(text(cx, cy + 102, "sin(μ) = 1/M", size=11, color=INK))

    # Нижній підсумковий блок
    summary_box = fitbox(W / 2 - 340, 325, 680, 160,
                         "Геометричний зміст числа Маха:\n"
                         "• При M < 1 акустичні збурення випереджають тіло та попереджають середовище.\n"
                         "• При M = 1 сферичні фронти стискаються у плоский звуковий бар'єр.\n"
                         "• При M > 1 збурення замикаються у конус Маха з напівкутом μ = arcsin(1/M).",
                         size=13, fill="#f1f5f9", stroke="#64748b", pad=14)
    body.append(summary_box)

    render(os.path.join(OUT, "mach-cone.svg"), W, H, *body,
           title="Поширення звукових хвиль та формування конуса Маха")


# ── Фігура 2: Класифікація режимів за числом Маха ───────────────────────────
def fig_compressible_regimes():
    W, H = 840, 480
    body = []
    
    axis_y = 100
    body.append(line(40, axis_y, 800, axis_y, color=LINE, sw=2.5))
    
    regimes = [
        ("Нестислий", 40, 180, "#e0f2fe", "#0284c7", "M < 0.3", "Зміна густини < 5%\nРівняння Бернуллі"),
        ("Стислий дозвук", 190, 330, "#dbeafe", "#2563eb", "0.3 ≤ M < 0.8", "Помітна стисливість\nПоправка Прандтля"),
        ("Трансзвук", 340, 480, "#fef3c7", "#d97706", "0.8 ≤ M ≤ 1.2", "Змішані зони (M>1)\nВолновий опір"),
        ("Надзвук", 490, 630, "#fee2e2", "#dc2626", "1.2 < M ≤ 5.0", "Суцільний надзвук\nКосі й прямі скачки"),
        ("Гіперзвук", 640, 780, "#f3e8ff", "#9333ea", "M > 5.0", "Високі температури\nДисоціація газів")
    ]
    
    # Помітки на осі (межі між блоками)
    boundary_ticks = [
        (40, "0.0"),
        (185, "0.3"),
        (335, "0.8"),
        (485, "1.2"),
        (635, "5.0"),
        (780, ">5.0")
    ]
    for x_pos, label in boundary_ticks:
        body.append(line(x_pos, axis_y - 8, x_pos, axis_y + 8, color=LINE, sw=1.8))
        body.append(text(x_pos, axis_y - 14, label, size=12, color=INK, bold=True))

    box_y = 135
    box_h = 175
    
    for r_name, x1, x2, bg_col, border_col, m_range, desc in regimes:
        w = x2 - x1
        full_text = f"{r_name}\n{m_range}\n\n{desc}"
        box_elem = fitbox(x1, box_y, w, box_h, full_text, size=12, fill=bg_col, stroke=border_col, pad=8)
        body.append(box_elem)

    bot_box = fitbox(W / 2 - 370, 335, 740, 110,
                     "Критичне значення M = 1 ділить газодинаміку на два фундаментально різні світи:\n"
                     "• Дозвуковий потік розширюється у розширюваних каналах і прискорюється у звужуваних.\n"
                     "• Надзвуковий потік прискорюється у розширюваних каналах (сопло Лаваля) і створює скачки ущільнення.",
                     size=12.5, fill="#ffffff", stroke="#475569", pad=12)
    body.append(bot_box)

    render(os.path.join(OUT, "compressible-regimes.svg"), W, H, *body,
           title="Спектр режимів течії за числом Маха")


# ── Фігура 3: Залежність термодинамічних параметрів та факторів стисливості ──
def fig_prandtl_glauert():
    W, H = 800, 460
    body = []
    
    ox, oy = 90, 360
    gx_w, gy_h = 640, 280
    
    def to_pixel(m_val, val):
        px = ox + (m_val / 2.0) * gx_w
        py = oy - (val / 3.5) * gy_h
        return px, py

    body.append(rect(ox, oy - gy_h, gx_w, gy_h, fill="#fafafa", stroke="#e2e8f0", sw=1.0, rx=4))
    
    for val in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
        _, py = to_pixel(0, val)
        body.append(line(ox, py, ox + gx_w, py, color="#e2e8f0", sw=1.0))
        body.append(text(ox - 12, py + 4, f"{val:.1f}", size=11, color=MUTED, anchor="end"))
        
    for m_val in [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]:
        px, _ = to_pixel(m_val, 0)
        body.append(line(px, oy - gy_h, px, oy, color="#e2e8f0", sw=1.0))
        body.append(text(px, oy + 18, f"{m_val:.1f}", size=11, color=MUTED))

    body.append(arrow(ox, oy, ox + gx_w + 20, oy, color=LINE, sw=1.8))
    body.append(arrow(ox, oy, ox, oy - gy_h - 20, color=LINE, sw=1.8))
    body.append(text(ox + gx_w + 10, oy + 32, "Число Маха (M)", size=12, color=INK, bold=True))
    body.append(text(ox - 45, oy - gy_h - 10, "Відношення / Фактор", size=11, color=INK, bold=True, anchor="start"))

    pts_p0 = []
    for step in range(0, 101):
        m_val = step * 0.02
        p0_ratio = (1.0 + 0.2 * m_val**2)**3.5
        if p0_ratio <= 3.5:
            px, py = to_pixel(m_val, p0_ratio)
            pts_p0.append(f"{px:.1f},{py:.1f}")
    body.append(f'<polyline points="{" ".join(pts_p0)}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    pts_t0 = []
    for step in range(0, 101):
        m_val = step * 0.02
        t0_ratio = 1.0 + 0.2 * m_val**2
        if t0_ratio <= 3.5:
            px, py = to_pixel(m_val, t0_ratio)
            pts_t0.append(f"{px:.1f},{py:.1f}")
    body.append(f'<polyline points="{" ".join(pts_t0)}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    pts_pg = []
    for step in range(0, 48):
        m_val = step * 0.02
        if m_val < 0.95:
            pg_val = 1.0 / math.sqrt(1.0 - m_val**2)
            if pg_val <= 3.5:
                px, py = to_pixel(m_val, pg_val)
                pts_pg.append(f"{px:.1f},{py:.1f}")
    body.append(f'<polyline points="{" ".join(pts_pg)}" fill="none" stroke="{FIELD}" stroke-width="2.0" stroke-dasharray="4 3"/>')

    m1_px, _ = to_pixel(1.0, 0)
    body.append(line(m1_px, oy - gy_h, m1_px, oy, color="#dc2626", sw=1.5, dash="4 4"))
    body.append(text(m1_px + 6, oy - gy_h + 16, "M = 1.0 (звуковий бар'єр)", size=11.5, color="#dc2626", bold=True, anchor="start"))

    leg_x, leg_y = 120, 110
    body.append(rect(leg_x, leg_y, 290, 85, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    
    body.append(line(leg_x + 12, leg_y + 20, leg_x + 40, leg_y + 20, color=POS, sw=2.5))
    body.append(text(leg_x + 48, leg_y + 24, "p₀ / p (тиск гальмування)", size=11.5, color=INK, anchor="start"))
    
    body.append(line(leg_x + 12, leg_y + 44, leg_x + 40, leg_y + 44, color=NEG, sw=2.5))
    body.append(text(leg_x + 48, leg_y + 48, "T₀ / T (температура гальмування)", size=11.5, color=INK, anchor="start"))
    
    body.append(line(leg_x + 12, leg_y + 68, leg_x + 40, leg_y + 68, color=FIELD, sw=2.0, dash="4 3"))
    body.append(text(leg_x + 48, leg_y + 72, "1 / √(1−M²) (корекція Прандтля)", size=11.5, color=INK, anchor="start"))

    bot_box = fitbox(W / 2 - 350, 395, 700, 50,
                     "При зростанні M тиск гальмування p₀ зростає експоненційно за степеневим законом,\n"
                     "а фактор Прандтля-Ґлауерта прямує до нескінченності біля M = 1 (акустична сингулярність).",
                     size=12, fill="#f8fafc", stroke="#64748b", pad=8)
    body.append(bot_box)

    render(os.path.join(OUT, "prandtl-glauert-compressibility.svg"), W, H, *body,
           title="Газодинамічні функції тиску, температури та стисливості")


if __name__ == "__main__":
    fig_mach_cone()
    fig_compressible_regimes()
    fig_prandtl_glauert()
    print("Figures generated successfully.")
