import os
import math

def ensure_img_dir(base_dir):
    img_dir = os.path.join(base_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    return img_dir

def create_kinetic_energy_svg(filepath):
    width, height = 880, 480
    
    # Coordinates of plot area
    ox, oy = 110, 390
    pw, ph = 700, 320
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    
    # Title
    svg.append(f'<text x="{width//2}" y="36" font-family="Segoe UI, Arial, sans-serif" font-size="18" font-weight="bold" fill="#1e293b" text-anchor="middle">Залежність кінетичної енергії від швидкості частинки</text>')
    svg.append(f'<text x="{width//2}" y="56" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#64748b" text-anchor="middle">Порівняння класичної механіки Ньютона та релятивістської механіки Ейнштейна</text>')
    
    # Grid lines
    for i in range(1, 10):
        vx = i / 10.0
        x = ox + vx * pw
        svg.append(f'<line x1="{x:.1f}" y1="{oy-ph}" x2="{x:.1f}" y2="{oy}" stroke="#f1f5f9" stroke-width="1.5"/>')
        svg.append(f'<text x="{x:.1f}" y="{oy+22}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#64748b" text-anchor="middle">{vx:.1f}</text>')

    for j in range(1, 6):
        ek_val = j * 0.5
        y = oy - (ek_val / 3.0) * ph
        if y >= oy - ph:
            svg.append(f'<line x1="{ox}" y1="{y:.1f}" x2="{ox+pw}" y2="{y:.1f}" stroke="#f1f5f9" stroke-width="1.5"/>')
            svg.append(f'<text x="{ox-12}" y="{y+4:.1f}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#64748b" text-anchor="end">{ek_val:.1f}</text>')

    # Axes
    svg.append(f'<line x1="{ox}" y1="{oy}" x2="{ox+pw+20}" y2="{oy}" stroke="#334155" stroke-width="2"/>')
    svg.append(f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ph-15}" stroke="#334155" stroke-width="2"/>')
    
    # Axis labels
    svg.append(f'<text x="{ox+pw+30}" y="{oy+5}" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#334155">v / c</text>')
    svg.append(f'<text x="{ox-10}" y="{oy-ph-22}" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#334155" text-anchor="end">E_k / (m₀ c²)</text>')
    
    # Asymptote at v/c = 1
    asym_x = ox + 1.0 * pw
    svg.append(f'<line x1="{asym_x}" y1="{oy-ph-10}" x2="{asym_x}" y2="{oy}" stroke="#ef4444" stroke-width="2" stroke-dasharray="6,4"/>')
    svg.append(f'<text x="{asym_x}" y="{oy-ph-18}" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#ef4444" text-anchor="middle">v = c (Межа)</text>')

    # Newtonian curve: E_k / m0 c^2 = 0.5 * (v/c)^2
    newton_pts = []
    for i in range(101):
        v = i / 100.0
        ek = 0.5 * v * v
        x = ox + v * pw
        y = oy - (ek / 3.0) * ph
        newton_pts.append(f"{x:.1f},{y:.1f}")
    
    svg.append(f'<polyline points="{" ".join(newton_pts)}" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-dasharray="7,4"/>')

    # Relativistic curve: E_k / m0 c^2 = 1/sqrt(1 - v^2/c^2) - 1
    rel_pts = []
    for i in range(99):
        v = i / 100.0
        gamma = 1.0 / math.sqrt(1.0 - v * v)
        ek = gamma - 1.0
        x = ox + v * pw
        y = oy - (ek / 3.0) * ph
        if y < oy - ph - 20:
            break
        rel_pts.append(f"{x:.1f},{y:.1f}")

    svg.append(f'<polyline points="{" ".join(rel_pts)}" fill="none" stroke="#059669" stroke-width="3"/>')

    # Annotations / Legend
    svg.append(f'<rect x="{ox+40}" y="{oy-ph+20}" width="340" height="90" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    
    # Legend items
    svg.append(f'<line x1="{ox+55}" y1="{oy-ph+45}" x2="{ox+95}" y2="{oy-ph+45}" stroke="#2563eb" stroke-width="2.5" stroke-dasharray="7,4"/>')
    svg.append(f'<text x="{ox+105}" y="{oy-ph+49}" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#1e293b">Класична теорія: E_k = ½ m₀ v²</text>')
    
    svg.append(f'<line x1="{ox+55}" y1="{oy-ph+75}" x2="{ox+95}" y2="{oy-ph+75}" stroke="#059669" stroke-width="3"/>')
    svg.append(f'<text x="{ox+105}" y="{oy-ph+79}" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#1e293b">Релятивістська теорія: E_k = (γ - 1) m₀ c²</text>')

    # Low speed agreement note
    svg.append(f'<circle cx="{ox+0.3*pw:.1f}" cy="{oy - (0.5*0.09/3.0)*ph:.1f}" r="6" fill="#f59e0b" stroke="#ffffff" stroke-width="2"/>')
    svg.append(f'<text x="{ox+0.3*pw+15:.1f}" y="{oy - (0.5*0.09/3.0)*ph + 15:.1f}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#b45309" font-weight="bold">v ≪ c: збіг з Ньютоном</text>')

    svg.append('</svg>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))

def create_energy_momentum_hyperbola_svg(filepath):
    width, height = 880, 500
    ox, oy = 440, 410
    scale_x = 210
    scale_y = 210
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    
    # Title
    svg.append(f'<text x="{width//2}" y="34" font-family="Segoe UI, Arial, sans-serif" font-size="18" font-weight="bold" fill="#1e293b" text-anchor="middle">Інваріантна гіпербола енергії-імпульсу у просторі Мінковського</text>')
    svg.append(f'<text x="{width//2}" y="54" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#64748b" text-anchor="middle">Співвідношення E² - (pc)² = (m₀ c²)² для масивних та безмасових частинок</text>')
    
    # Light cone lines E = |pc| starting from origin (ox, oy) up to y = 80
    max_pc = (oy - 80) / scale_y # ~1.57
    x_left = ox - max_pc * scale_x
    x_right = ox + max_pc * scale_x
    y_top = 80
    
    svg.append(f'<line x1="{ox}" y1="{oy}" x2="{x_right:.1f}" y2="{y_top}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="5,4"/>')
    svg.append(f'<line x1="{ox}" y1="{oy}" x2="{x_left:.1f}" y2="{y_top}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="5,4"/>')
    
    # Light cone text labels
    svg.append(f'<text x="{x_right + 10:.1f}" y="{y_top + 5}" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#64748b">E = pc (Фотон)</text>')
    svg.append(f'<text x="{x_left - 65:.1f}" y="{y_top + 5}" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#64748b">E = -pc</text>')

    # Axes
    svg.append(f'<line x1="{ox - 1.6*scale_x}" y1="{oy}" x2="{ox + 1.6*scale_x}" y2="{oy}" stroke="#334155" stroke-width="2"/>')
    svg.append(f'<line x1="{ox}" y1="{oy + 30}" x2="{ox}" y2="{oy - 1.6*scale_y}" stroke="#334155" stroke-width="2"/>')
    
    # Axis labels
    svg.append(f'<text x="{ox + 1.6*scale_x + 10}" y="{oy + 4}" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#334155">p c</text>')
    svg.append(f'<text x="{ox - 15}" y="{oy - 1.6*scale_y - 5}" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#334155" text-anchor="end">E</text>')

    # Massive particle hyperbola: E = sqrt((pc)^2 + (m0 c^2)^2)
    hyper_pts = []
    for i in range(-135, 136):
        pc_val = i / 100.0
        e_val = math.sqrt(pc_val * pc_val + 1.0)
        x = ox + pc_val * scale_x
        y = oy - e_val * scale_y
        hyper_pts.append(f"{x:.1f},{y:.1f}")
        
    svg.append(f'<polyline points="{" ".join(hyper_pts)}" fill="none" stroke="#2563eb" stroke-width="3"/>')

    # Point at rest: pc = 0, E = m0 c^2
    rest_x = ox
    rest_y = oy - 1.0 * scale_y
    svg.append(f'<circle cx="{rest_x}" cy="{rest_y}" r="7" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>')
    svg.append(f'<text x="{rest_x + 15}" y="{rest_y + 4}" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#ef4444">Стан спокою: p = 0, E = m₀ c²</text>')

    # Moving particle point
    mov_pc = 0.95
    mov_e = math.sqrt(mov_pc * mov_pc + 1.0)
    mov_x = ox + mov_pc * scale_x
    mov_y = oy - mov_e * scale_y
    svg.append(f'<circle cx="{mov_x:.1f}" cy="{mov_y:.1f}" r="6" fill="#059669" stroke="#ffffff" stroke-width="2"/>')
    
    # Dotted lines to axes
    svg.append(f'<line x1="{mov_x:.1f}" y1="{mov_y:.1f}" x2="{mov_x:.1f}" y2="{oy}" stroke="#059669" stroke-width="1.5" stroke-dasharray="4,3"/>')
    svg.append(f'<line x1="{mov_x:.1f}" y1="{mov_y:.1f}" x2="{ox}" y2="{mov_y:.1f}" stroke="#059669" stroke-width="1.5" stroke-dasharray="4,3"/>')
    
    svg.append(f'<text x="{mov_x + 12:.1f}" y="{mov_y - 8:.1f}" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#059669">Рухома частинка (E = γ m₀ c²)</text>')

    # Legend / Info box (top left corner)
    svg.append(f'<rect x="50" y="80" width="310" height="95" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>')
    svg.append(f'<text x="65" y="103" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#1e293b">Основні інваріанти:</text>')
    svg.append(f'<text x="65" y="125" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#2563eb">• Масивна частинка: E² - (pc)² = (m₀ c²)²</text>')
    svg.append(f'<text x="65" y="145" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#475569">• Безмасова (m₀ = 0): E = pc</text>')
    svg.append(f'<text x="65" y="163" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#ef4444">• Енергія спокою: E₀ = m₀ c²</text>')

    svg.append('</svg>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))

def create_mass_energy_balance_svg(filepath):
    width, height = 880, 460
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    
    # Title
    svg.append(f'<text x="{width//2}" y="34" font-family="Segoe UI, Arial, sans-serif" font-size="18" font-weight="bold" fill="#1e293b" text-anchor="middle">Дефект маси та баланс енергії при ядерному синтезі (D + T → ⁴He + n)</text>')
    svg.append(f'<text x="{width//2}" y="54" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#64748b" text-anchor="middle">Зменшення маси спокою Δm виділяється у формі кінетичної енергії продуктів реакції (17.6 МеВ)</text>')
    
    # Left container: Reactants
    svg.append('<rect x="60" y="90" width="330" height="310" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>')
    svg.append('<text x="225" y="120" font-family="Segoe UI, Arial, sans-serif" font-size="15" font-weight="bold" fill="#1e293b" text-anchor="middle">Вхідні ядра (До реакції)</text>')
    
    # Deuterium
    svg.append('<circle cx="150" cy="190" r="22" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>')
    svg.append('<text x="150" y="195" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">p</text>')
    svg.append('<circle cx="180" cy="190" r="22" fill="#94a3b8" stroke="#475569" stroke-width="2"/>')
    svg.append('<text x="180" y="195" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">n</text>')
    svg.append('<text x="165" y="235" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Дейтерій (²H)</text>')
    svg.append('<text x="165" y="255" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#64748b" text-anchor="middle">m = 2.014102 u</text>')

    # Tritium
    svg.append('<circle cx="280" cy="180" r="20" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>')
    svg.append('<text x="280" y="185" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">p</text>')
    svg.append('<circle cx="310" cy="175" r="20" fill="#94a3b8" stroke="#475569" stroke-width="2"/>')
    svg.append('<text x="310" y="180" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">n</text>')
    svg.append('<circle cx="295" cy="205" r="20" fill="#94a3b8" stroke="#475569" stroke-width="2"/>')
    svg.append('<text x="295" y="210" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">n</text>')
    svg.append('<text x="295" y="245" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Тритій (³H)</text>')
    svg.append('<text x="295" y="265" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#64748b" text-anchor="middle">m = 3.016049 u</text>')

    svg.append('<line x1="80" y1="290" x2="370" y2="290" stroke="#e2e8f0" stroke-width="1.5"/>')
    svg.append('<text x="225" y="320" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Сумарна маса початкова:</text>')
    svg.append('<text x="225" y="345" font-family="Segoe UI, Arial, sans-serif" font-size="16" font-weight="bold" fill="#2563eb" text-anchor="middle">M_in = 5.030151 u</text>')

    # Arrow
    svg.append('<defs>')
    svg.append('  <marker id="arrow" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">')
    svg.append('    <path d="M0,0 L0,6 L9,3 Z" fill="#059669" />')
    svg.append('  </marker>')
    svg.append('</defs>')
    svg.append('<line x1="405" y1="245" x2="475" y2="245" stroke="#059669" stroke-width="4" marker-end="url(#arrow)"/>')
    svg.append('<text x="440" y="225" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#059669" text-anchor="middle">Синтез</text>')

    # Right container: Products
    svg.append('<rect x="490" y="90" width="330" height="310" rx="12" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>')
    svg.append('<text x="655" y="120" font-family="Segoe UI, Arial, sans-serif" font-size="15" font-weight="bold" fill="#1e293b" text-anchor="middle">Продукти реакції (Після)</text>')

    # Helium-4
    svg.append('<circle cx="560" cy="180" r="18" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>')
    svg.append('<circle cx="585" cy="180" r="18" fill="#3b82f6" stroke="#1d4ed8" stroke-width="2"/>')
    svg.append('<circle cx="572" cy="162" r="18" fill="#94a3b8" stroke="#475569" stroke-width="2"/>')
    svg.append('<circle cx="572" cy="198" r="18" fill="#94a3b8" stroke="#475569" stroke-width="2"/>')
    svg.append('<text x="572" y="235" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Гелій-4 (⁴He)</text>')
    svg.append('<text x="572" y="255" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#64748b" text-anchor="middle">m = 4.001506 u</text>')

    # Neutron
    svg.append('<circle cx="715" cy="190" r="18" fill="#94a3b8" stroke="#475569" stroke-width="2"/>')
    svg.append('<text x="715" y="195" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">n</text>')
    svg.append('<text x="715" y="235" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Нейтрон (n)</text>')
    svg.append('<text x="715" y="255" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#64748b" text-anchor="middle">m = 1.008665 u</text>')

    svg.append('<line x1="510" y1="290" x2="800" y2="290" stroke="#e2e8f0" stroke-width="1.5"/>')
    svg.append('<text x="655" y="315" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="bold" fill="#1e293b" text-anchor="middle">Маса продуктів: M_out = 5.010171 u</text>')
    svg.append('<text x="655" y="340" font-family="Segoe UI, Arial, sans-serif" font-size="14" font-weight="bold" fill="#ef4444" text-anchor="middle">Дефект маси: Δm = 0.019980 u</text>')
    svg.append('<text x="655" y="365" font-family="Segoe UI, Arial, sans-serif" font-size="15" font-weight="bold" fill="#059669" text-anchor="middle">Виділена енергія: ΔE = 17.59 МеВ</text>')

    svg.append('</svg>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = ensure_img_dir(base_dir)
    
    create_kinetic_energy_svg(os.path.join(img_dir, "kinetic-energy-vs-velocity.svg"))
    create_energy_momentum_hyperbola_svg(os.path.join(img_dir, "energy-momentum-hyperbola.svg"))
    create_mass_energy_balance_svg(os.path.join(img_dir, "mass-energy-balance.svg"))
    print("SVG figures generated successfully.")

if __name__ == "__main__":
    main()
