import os
import math

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_geometric_distortion():
    """
    Generates SVG showing mapping of unit sphere into hyperellipsoid via matrix A,
    illustrating singular values sigma_max, sigma_min and perturbation amplification.
    Width: 800, Height: 480
    """
    width, height = 800, 480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append(f'<text x="{width/2}" y="32" font-family="sans-serif" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">Геометричний зміст числа обумовленості: деформація сфери в еліпсоїд</text>')
    
    # Left Panel: Domain space (unit circle ||x|| = 1)
    cx1, cy1 = 200, 240
    r1 = 110
    
    svg.append(f'<rect x="30" y="55" width="340" height="370" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />')
    svg.append(f'<text x="{cx1}" y="85" font-family="sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">Простір розв\'язків x (прообраз)</text>')
    svg.append(f'<text x="{cx1}" y="105" font-family="sans-serif" font-size="12" fill="#64748b" text-anchor="middle">Одинична сфера ‖x‖₂ = 1</text>')
    
    # Axes Left
    svg.append(f'<line x1="{cx1 - 130}" y1="{cy1}" x2="{cx1 + 130}" y2="{cy1}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="4,4" />')
    svg.append(f'<line x1="{cx1}" y1="{cy1 - 125}" x2="{cx1}" y2="{cy1 + 125}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="4,4" />')
    
    # Unit Circle
    svg.append(f'<circle cx="{cx1}" cy="{cy1}" r="{r1}" fill="#e0f2fe" fill-opacity="0.5" stroke="#0284c7" stroke-width="2.5" />')
    
    # Vectors in left panel (v1, v2)
    ang = math.radians(25)
    v1x = cx1 + r1 * math.cos(ang)
    v1y = cy1 - r1 * math.sin(ang)
    v2x = cx1 - r1 * math.sin(ang)
    v2y = cy1 - r1 * math.cos(ang)
    
    # Vector v1
    svg.append(f'<line x1="{cx1}" y1="{cy1}" x2="{v1x}" y2="{v1y}" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)" />')
    svg.append(f'<text x="{v1x + 12}" y="{v1y - 2}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#16a34a">v₁</text>')
    
    # Vector v2
    svg.append(f'<line x1="{cx1}" y1="{cy1}" x2="{v2x}" y2="{v2y}" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow-red)" />')
    svg.append(f'<text x="{v2x - 18}" y="{v2y - 6}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#dc2626">v₂</text>')
    
    # Perturbation vector dx in left space
    svg.append(f'<line x1="{cx1 + 25}" y1="{cy1 - 15}" x2="{cx1 + 25 - 65*math.sin(ang)}" y2="{cy1 - 15 - 65*math.cos(ang)}" stroke="#b91c1c" stroke-width="2" stroke-dasharray="3,3" />')
    svg.append(f'<text x="{cx1 - 50}" y="{cy1 + 45}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">Похибка ‖δx‖</text>')
    
    # Middle arrow (Transformation A)
    svg.append(f'<path d="M 385 230 L 415 230" stroke="#334155" stroke-width="2.5" marker-end="url(#arrow-dark)" />')
    svg.append(f'<text x="400" y="218" font-family="sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">A · x</text>')
    svg.append(f'<path d="M 415 255 L 385 255" stroke="#64748b" stroke-width="2" marker-end="url(#arrow-gray)" />')
    svg.append(f'<text x="400" y="275" font-family="sans-serif" font-size="12" fill="#64748b" text-anchor="middle">A⁻¹ · b</text>')
    
    # Right Panel: Image space (hyperellipsoid ||b||)
    cx2, cy2 = 600, 240
    a_axis = 145 # sigma_max
    b_axis = 22  # sigma_min (strongly squashed)
    
    svg.append(f'<rect x="430" y="55" width="340" height="370" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" />')
    svg.append(f'<text x="{cx2}" y="85" font-family="sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">Простір образів b = Ax</text>')
    svg.append(f'<text x="{cx2}" y="105" font-family="sans-serif" font-size="12" fill="#64748b" text-anchor="middle">Еліпсоїд: півосі σ_max та σ_min</text>')
    
    # Axes Right
    svg.append(f'<line x1="{cx2 - 150}" y1="{cy2}" x2="{cx2 + 150}" y2="{cy2}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="4,4" />')
    svg.append(f'<line x1="{cx2}" y1="{cy2 - 125}" x2="{cx2}" y2="{cy2 + 125}" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="4,4" />')
    
    # Rotated Ellipse
    svg.append(f'<ellipse cx="{cx2}" cy="{cy2}" rx="{a_axis}" ry="{b_axis}" transform="rotate(-25 {cx2} {cy2})" fill="#fef2f2" fill-opacity="0.6" stroke="#ef4444" stroke-width="2.5" />')
    
    # Major axis (sigma_max * u1)
    u1_end_x = cx2 + a_axis * math.cos(ang)
    u1_end_y = cy2 - a_axis * math.sin(ang)
    svg.append(f'<line x1="{cx2}" y1="{cy2}" x2="{u1_end_x}" y2="{u1_end_y}" stroke="#16a34a" stroke-width="2.5" />')
    svg.append(f'<circle cx="{u1_end_x}" cy="{u1_end_y}" r="4" fill="#16a34a" />')
    
    # Minor axis (sigma_min * u2)
    u2_end_x = cx2 - b_axis * math.sin(ang)
    u2_end_y = cy2 - b_axis * math.cos(ang)
    svg.append(f'<line x1="{cx2}" y1="{cy2}" x2="{u2_end_x}" y2="{u2_end_y}" stroke="#dc2626" stroke-width="2.5" />')
    svg.append(f'<circle cx="{u2_end_x}" cy="{u2_end_y}" r="4" fill="#dc2626" />')
    
    # Small perturbation delta_b along minor axis
    db_start_x = cx2 + 70 * math.cos(ang)
    db_start_y = cy2 - 70 * math.sin(ang)
    db_end_x = db_start_x - 30 * math.sin(ang)
    db_end_y = db_start_y - 30 * math.cos(ang)
    svg.append(f'<line x1="{db_start_x}" y1="{db_start_y}" x2="{db_end_x}" y2="{db_end_y}" stroke="#2563eb" stroke-width="2.5" />')
    svg.append(f'<text x="{db_end_x + 10}" y="{db_end_y + 4}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#2563eb">δb</text>')
    
    # Labels in Right Panel
    svg.append(f'<text x="{cx2 + 100}" y="{cy2 - 45}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#16a34a">σ_max · u₁</text>')
    svg.append(f'<text x="{cx2 - 80}" y="{cy2 - 30}" font-family="sans-serif" font-size="12" font-weight="bold" fill="#dc2626">σ_min · u₂</text>')
    svg.append(f'<text x="{cx2}" y="{cy2 + 85}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#7f1d1d" text-anchor="middle">cond₂(A) = σ_max / σ_min ≫ 1</text>')
    svg.append(f'<text x="{cx2}" y="{cy2 + 105}" font-family="sans-serif" font-size="11" fill="#475569" text-anchor="middle">Мізерне збурення δb уздовж σ_min</text>')
    svg.append(f'<text x="{cx2}" y="{cy2 + 120}" font-family="sans-serif" font-size="11" fill="#475569" text-anchor="middle">породжує гігантське зміщення δx</text>')
    
    # Bottom summary bar
    svg.append(f'<rect x="30" y="435" width="740" height="34" rx="6" fill="#f1f5f9" stroke="#e2e8f0" />')
    svg.append(f'<text x="{width/2}" y="457" font-family="sans-serif" font-size="12" fill="#334155" text-anchor="middle">Чим сильніше сплюснутий еліпсоїд (менше σ_min), тим більша чутливість розв\'язку до похибок</text>')
    
    # Marker definitions
    svg.append('<defs>')
    svg.append('<marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#16a34a" /></marker>')
    svg.append('<marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626" /></marker>')
    svg.append('<marker id="arrow-dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" /></marker>')
    svg.append('<marker id="arrow-gray" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" /></marker>')
    svg.append('</defs>')
    
    svg.append('</svg>')
    return "\n".join(svg)

def generate_precision_loss():
    """
    Generates SVG showing degradation of decimal precision in float32 and float64
    as a function of log10(cond(A)).
    Width: 800, Height: 480
    """
    width, height = 800, 480
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append(f'<text x="{width/2}" y="30" font-family="sans-serif" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">Втрата десяткових знаків точності: правило log₁₀(cond(A))</text>')
    
    # Table Header
    y_start = 55
    row_h = 38
    
    svg.append(f'<rect x="40" y="{y_start}" width="720" height="32" fill="#0f172a" rx="4" />')
    svg.append(f'<text x="110" y="{y_start + 21}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">cond(A)</text>')
    svg.append(f'<text x="210" y="{y_start + 21}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">Втрата знаків</text>')
    svg.append(f'<text x="395" y="{y_start + 21}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#38bdf8" text-anchor="middle">float32 (~7 знаків)</text>')
    svg.append(f'<text x="630" y="{y_start + 21}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#a7f3d0" text-anchor="middle">float64 (~16 знаків)</text>')
    
    data = [
        ("10⁰ = 1", "0", 7, 16, "#16a34a"),
        ("10²", "2 знаки", 5, 14, "#16a34a"),
        ("10⁴", "4 знаки", 3, 12, "#ca8a04"),
        ("10⁶", "6 знаків", 1, 10, "#ea580c"),
        ("10⁸", "8 знаків", 0, 8, "#dc2626"),
        ("10¹²", "12 знаків", 0, 4, "#dc2626"),
        ("10¹⁶", "16 знаків", 0, 0, "#991b1b"),
    ]
    
    curr_y = y_start + 36
    for cond_str, loss_str, f32_rem, f64_rem, status_color in data:
        bg = "#f8fafc" if (data.index((cond_str, loss_str, f32_rem, f64_rem, status_color)) % 2 == 0) else "#ffffff"
        svg.append(f'<rect x="40" y="{curr_y}" width="720" height="{row_h}" fill="{bg}" stroke="#e2e8f0" stroke-width="1" />')
        
        svg.append(f'<text x="110" y="{curr_y + 24}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">{cond_str}</text>')
        svg.append(f'<text x="210" y="{curr_y + 24}" font-family="sans-serif" font-size="12" fill="{status_color}" font-weight="bold" text-anchor="middle">{loss_str}</text>')
        
        # Draw digits bar for float32 (7 slots)
        start_f32_x = 315
        box_w = 18
        box_h = 20
        box_y = curr_y + 9
        for i in range(7):
            bx = start_f32_x + i * 22
            if i < f32_rem:
                f_color = "#bae6fd"
                b_border = "#0284c7"
                t_color = "#0369a1"
                txt = "✓"
            else:
                f_color = "#fee2e2"
                b_border = "#ef4444"
                t_color = "#b91c1c"
                txt = "✕"
            svg.append(f'<rect x="{bx}" y="{box_y}" width="{box_w}" height="{box_h}" rx="3" fill="{f_color}" stroke="{b_border}" stroke-width="1" />')
            svg.append(f'<text x="{bx + 9}" y="{box_y + 15}" font-family="sans-serif" font-size="10" font-weight="bold" fill="{t_color}" text-anchor="middle">{txt}</text>')
            
        # Draw digits bar for float64 (16 slots)
        start_f64_x = 520
        box_w64 = 11
        for i in range(16):
            bx = start_f64_x + i * 14
            if i < f64_rem:
                f_color = "#dcfce7"
                b_border = "#22c55e"
            else:
                f_color = "#fee2e2"
                b_border = "#ef4444"
            svg.append(f'<rect x="{bx}" y="{box_y}" width="{box_w64}" height="{box_h}" rx="2" fill="{f_color}" stroke="{b_border}" stroke-width="1" />')
            
        curr_y += row_h + 3
        
    # Legend at bottom
    svg.append(f'<rect x="40" y="{curr_y + 6}" width="720" height="52" rx="6" fill="#f1f5f9" stroke="#cbd5e1" />')
    svg.append(f'<circle cx="65" cy="{curr_y + 24}" r="5" fill="#0284c7" />')
    svg.append(f'<text x="78" y="{curr_y + 28}" font-family="sans-serif" font-size="12" fill="#334155">Достовірні цифри</text>')
    svg.append(f'<circle cx="215" cy="{curr_y + 24}" r="5" fill="#ef4444" />')
    svg.append(f'<text x="228" y="{curr_y + 28}" font-family="sans-serif" font-size="12" fill="#334155">Знищені похибкою цифри</text>')
    svg.append(f'<text x="740" y="{curr_y + 28}" font-family="sans-serif" font-size="12" font-style="italic" fill="#475569" text-anchor="end">Втрачено знаків: s ≈ log₁₀(cond(A))</text>')
    svg.append(f'<text x="{width/2}" y="{curr_y + 46}" font-family="sans-serif" font-size="11" fill="#64748b" text-anchor="middle">Якщо cond(A) ≥ 10⁷ для float32 або 10¹⁶ для float64 — розв\'язок перетворюється на числовий шум</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)

def generate_tikhonov_filtering():
    """
    Generates SVG showing Tikhonov regularization spectral filter factor
    f(sigma) = sigma / (sigma^2 + lambda^2) vs standard inversion 1 / sigma.
    Width: 800, Height: 460
    """
    width, height = 800, 460
    margin_left, margin_right = 75, 45
    margin_top, margin_bottom = 85, 65
    
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    
    def map_x(sigma):
        return margin_left + (sigma / 2.5) * plot_w
        
    def map_y(val):
        return margin_top + (3.5 - val) / 3.5 * plot_h
        
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff" />')
    
    # Title
    svg.append(f'<text x="{width/2}" y="30" font-family="sans-serif" font-size="16" font-weight="bold" fill="#1e293b" text-anchor="middle">Спектральна фільтрація Тихонова: придушення шумів малих сингулярних чисел</text>')
    
    lam = 0.4
    x_lam = map_x(lam)
    
    # Zone banners ABOVE the plot to avoid line crossing
    svg.append(f'<rect x="{margin_left}" y="50" width="{x_lam - margin_left}" height="28" rx="4" fill="#fee2e2" stroke="#fca5a5" />')
    svg.append(f'<text x="{(margin_left + x_lam)/2}" y="68" font-family="sans-serif" font-size="11" font-weight="bold" fill="#991b1b" text-anchor="middle">Зона придушення шуму (σ &lt; λ)</text>')
    
    svg.append(f'<rect x="{x_lam + 6}" y="50" width="{margin_left + plot_w - x_lam - 6}" height="28" rx="4" fill="#dcfce7" stroke="#86efac" />')
    svg.append(f'<text x="{(x_lam + 6 + margin_left + plot_w)/2}" y="68" font-family="sans-serif" font-size="11" font-weight="bold" fill="#166534" text-anchor="middle">Зона збереження сигналу (σ ≫ λ : інверсія 1/σ)</text>')
    
    # Background zones inside plot
    svg.append(f'<rect x="{margin_left}" y="{margin_top}" width="{x_lam - margin_left}" height="{plot_h}" fill="#fef2f2" fill-opacity="0.5" />')
    svg.append(f'<rect x="{x_lam}" y="{margin_top}" width="{margin_left + plot_w - x_lam}" height="{plot_h}" fill="#f0fdf4" fill-opacity="0.5" />')
    
    # Grid & Axes
    for s_val in [0.5, 1.0, 1.5, 2.0, 2.5]:
        px = map_x(s_val)
        svg.append(f'<line x1="{px}" y1="{margin_top}" x2="{px}" y2="{height - margin_bottom}" stroke="#e2e8f0" stroke-width="1" />')
        svg.append(f'<text x="{px}" y="{height - margin_bottom + 18}" font-family="sans-serif" font-size="12" fill="#64748b" text-anchor="middle">{s_val}</text>')
        
    for v_val in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        py = map_y(v_val)
        svg.append(f'<line x1="{margin_left}" y1="{py}" x2="{width - margin_right}" y2="{py}" stroke="#e2e8f0" stroke-width="1" />')
        svg.append(f'<text x="{margin_left - 10}" y="{py + 4}" font-family="sans-serif" font-size="12" fill="#64748b" text-anchor="end">{v_val}</text>')
        
    # Plot frame
    svg.append(f'<rect x="{margin_left}" y="{margin_top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#94a3b8" stroke-width="1.5" />')
    
    # Axis labels
    svg.append(f'<text x="{width/2}" y="{height - margin_bottom + 42}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">Сингулярне число σ</text>')
    svg.append(f'<text x="24" y="{margin_top + plot_h/2}" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle" transform="rotate(-90 24 {margin_top + plot_h/2})">Ваговий множник інверсії</text>')
    
    # Regularization parameter line lambda
    svg.append(f'<line x1="{x_lam}" y1="{margin_top}" x2="{x_lam}" y2="{height - margin_bottom}" stroke="#6366f1" stroke-width="2" stroke-dasharray="5,5" />')
    svg.append(f'<text x="{x_lam + 6}" y="{margin_top + plot_h - 15}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#4338ca">Параметр λ = 0.4</text>')
    
    # Curve 1: Unregularized 1 / sigma
    pts_unreg = []
    for step in range(1, 251):
        s = step * 0.01
        val = 1.0 / s
        if val <= 3.5:
            pts_unreg.append(f"{map_x(s):.1f},{map_y(val):.1f}")
            
    svg.append(f'<polyline points="{" ".join(pts_unreg)}" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="6,4" />')
    
    # Curve 2: Tikhonov filter sigma / (sigma^2 + lambda^2)
    pts_tikh = []
    for step in range(0, 251):
        s = step * 0.01
        val = s / (s**2 + lam**2)
        if val <= 3.5:
            pts_tikh.append(f"{map_x(s):.1f},{map_y(val):.1f}")
            
    svg.append(f'<polyline points="{" ".join(pts_tikh)}" fill="none" stroke="#2563eb" stroke-width="3" />')
    
    # Peak point annotation at sigma = lambda
    peak_s = lam
    peak_v = 1.0 / (2.0 * lam) # 1 / 0.8 = 1.25
    px_peak = map_x(peak_s)
    py_peak = map_y(peak_v)
    svg.append(f'<circle cx="{px_peak}" cy="{py_peak}" r="5" fill="#2563eb" />')
    svg.append(f'<text x="{px_peak + 12}" y="{py_peak - 8}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1d4ed8">Пік: 1/(2λ) при σ = λ</text>')
    
    # Legend
    leg_x = width - margin_right - 265
    leg_y = margin_top + 15
    svg.append(f'<rect x="{leg_x}" y="{leg_y}" width="255" height="64" rx="5" fill="#ffffff" fill-opacity="0.9" stroke="#cbd5e1" stroke-width="1" />')
    
    svg.append(f'<line x1="{leg_x + 12}" y1="{leg_y + 20}" x2="{leg_x + 38}" y2="{leg_y + 20}" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="6,4" />')
    svg.append(f'<text x="{leg_x + 46}" y="{leg_y + 24}" font-family="sans-serif" font-size="11" fill="#1e293b">Звичайна інверсія 1/σ (шум)</text>')
    
    svg.append(f'<line x1="{leg_x + 12}" y1="{leg_y + 44}" x2="{leg_x + 38}" y2="{leg_y + 44}" stroke="#2563eb" stroke-width="3" />')
    svg.append(f'<text x="{leg_x + 46}" y="{leg_y + 48}" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1e293b">Тихонов: σ / (σ² + λ²)</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    ensure_dir(img_dir)
    
    with open(os.path.join(img_dir, 'geometric-distortion.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_geometric_distortion())
        
    with open(os.path.join(img_dir, 'precision-loss.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_precision_loss())
        
    with open(os.path.join(img_dir, 'tikhonov-filtering.svg'), 'w', encoding='utf-8') as f:
        f.write(generate_tikhonov_filtering())
        
    print("SVGs successfully generated in ./img/")

if __name__ == '__main__':
    main()
