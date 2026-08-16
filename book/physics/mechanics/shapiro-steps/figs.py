#!/usr/bin/env python3
"""
figs.py — Generates clean SVG diagrams for 'shapiro-steps' topic.
"""
import os
import math

def ensure_img_dir(base_dir):
    img_dir = os.path.join(base_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    return img_dir

def create_svg_header(width, height):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" style="background-color: #1e1e2e; font-family: system-ui, -apple-system, sans-serif;">\n'
        '<defs>\n'
        '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#a6adc8" />\n'
        '  </marker>\n'
        '  <marker id="arrow-cyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#89dceb" />\n'
        '  </marker>\n'
        '  <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">\n'
        '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#f38ba8" />\n'
        '  </marker>\n'
        '</defs>\n'
    )

def generate_rcsj_diagram(filepath):
    svg = create_svg_header(900, 420)
    svg += '<rect x="15" y="15" width="870" height="390" rx="12" fill="#181825" stroke="#313244" stroke-width="2" />\n'
    svg += '<text x="450" y="45" fill="#cdd6f4" font-size="20" font-weight="bold" text-anchor="middle">Еквівалентна електрична схема RCSJ моделі Джозефсонівського переходу</text>\n'
    svg += '<path d="M 80 100 L 620 100" stroke="#a6adc8" stroke-width="3" fill="none" />\n'
    svg += '<path d="M 80 340 L 620 340" stroke="#a6adc8" stroke-width="3" fill="none" />\n'
    svg += '<path d="M 80 100 L 80 180 M 80 240 L 80 340" stroke="#89b4fa" stroke-width="3" fill="none" />\n'
    svg += '<circle cx="80" cy="210" r="28" fill="#1e1e2e" stroke="#89b4fa" stroke-width="3" />\n'
    svg += '<path d="M 80 225 L 80 195" stroke="#89b4fa" stroke-width="2.5" marker-end="url(#arrow-cyan)" />\n'
    svg += '<text x="70" y="215" fill="#89b4fa" font-size="14" font-weight="bold" text-anchor="end">I(t)</text>\n'
    svg += '<text x="120" y="205" fill="#89b4fa" font-size="13">I(t) = I_dc + I_ac·sin(ω_rf·t)</text>\n'
    svg += '<path d="M 260 100 L 260 195 M 260 225 L 260 340" stroke="#f9e2af" stroke-width="3" fill="none" />\n'
    svg += '<line x1="240" y1="195" x2="280" y2="195" stroke="#f9e2af" stroke-width="4" />\n'
    svg += '<line x1="240" y1="225" x2="280" y2="225" stroke="#f9e2af" stroke-width="4" />\n'
    svg += '<text x="295" y="215" fill="#f9e2af" font-size="15" font-weight="bold">C (ємність)</text>\n'
    svg += '<path d="M 430 100 L 430 170 M 430 250 L 430 340" stroke="#a6e3a1" stroke-width="3" fill="none" />\n'
    svg += '<rect x="415" y="170" width="30" height="80" fill="#1e1e2e" stroke="#a6e3a1" stroke-width="3" rx="4" />\n'
    svg += '<text x="460" y="215" fill="#a6e3a1" font-size="15" font-weight="bold">R (опір)</text>\n'
    svg += '<path d="M 580 100 L 580 185 M 580 235 L 580 340" stroke="#f38ba8" stroke-width="3" fill="none" />\n'
    svg += '<line x1="565" y1="195" x2="595" y2="225" stroke="#f38ba8" stroke-width="4" />\n'
    svg += '<line x1="565" y1="225" x2="595" y2="195" stroke="#f38ba8" stroke-width="4" />\n'
    svg += '<text x="615" y="200" fill="#f38ba8" font-size="15" font-weight="bold">I_c · sin(φ)</text>\n'
    svg += '<text x="615" y="225" fill="#f38ba8" font-size="12">(Джозефсонівський елемент)</text>\n'
    svg += '<circle cx="620" cy="100" r="5" fill="#89dceb" />\n'
    svg += '<circle cx="620" cy="340" r="5" fill="#89dceb" />\n'
    svg += '<path d="M 730 115 L 730 325" stroke="#89dceb" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow-cyan)" marker-start="url(#arrow-cyan)" />\n'
    svg += '<text x="870" y="215" fill="#89dceb" font-size="14" font-weight="bold" text-anchor="end">V(t) = (ħ/2e)·dφ/dt</text>\n'
    svg += '<rect x="200" y="360" width="500" height="35" rx="6" fill="#313244" stroke="#45475a" />\n'
    svg += '<text x="450" y="383" fill="#cdd6f4" font-size="14" font-family="monospace" text-anchor="middle">C·d²φ/dt² + (1/R)·dφ/dt + I_c·sin(φ) = I_dc + I_ac·sin(ω_rf·t)</text>\n'
    svg += '</svg>'
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)

def generate_pendulum_diagram(filepath):
    svg = create_svg_header(850, 440)
    svg += '<rect x="15" y="15" width="820" height="410" rx="12" fill="#181825" stroke="#313244" stroke-width="2" />\n'
    svg += '<text x="425" y="45" fill="#cdd6f4" font-size="20" font-weight="bold" text-anchor="middle">Механічна аналогія: обертальний маятник із в&apos;язким тертям і змінним моментом</text>\n'
    cx, cy = 260, 210
    svg += f'<circle cx="{cx}" cy="{cy}" r="8" fill="#f9e2af" stroke="#fab387" stroke-width="3" />\n'
    svg += f'<line x1="{cx}" y1="80" x2="{cx}" y2="340" stroke="#585b70" stroke-width="2" stroke-dasharray="6,6" />\n'
    rad = math.radians(40)
    length = 120
    px = cx + length * math.sin(rad)
    py = cy + length * math.cos(rad)
    svg += f'<line x1="{cx}" y1="{cy}" x2="{px}" y2="{py}" stroke="#89b4fa" stroke-width="5" />\n'
    svg += f'<circle cx="{px}" cy="{py}" r="22" fill="#f38ba8" stroke="#f5e0dc" stroke-width="3" />\n'
    svg += f'<text x="{px}" y="{py+5}" fill="#11111b" font-size="14" font-weight="bold" text-anchor="middle">m</text>\n'
    svg += f'<path d="M {cx} 270 A 60 60 0 0 0 {cx+40} 255" stroke="#f9e2af" stroke-width="2.5" fill="none" marker-end="url(#arrow)" />\n'
    svg += f'<text x="{cx+45}" y="280" fill="#f9e2af" font-size="16" font-weight="bold">φ (кут)</text>\n'
    svg += '<path d="M 190 170 Q 170 210 190 250" stroke="#a6e3a1" stroke-width="3" fill="none" stroke-dasharray="4,4" />\n'
    svg += '<text x="50" y="215" fill="#a6e3a1" font-size="14" font-weight="bold">В&apos;язке тертя γ (1/R)</text>\n'
    svg += f'<line x1="{px}" y1="{py}" x2="{px}" y2="{py+45}" stroke="#f38ba8" stroke-width="2.5" marker-end="url(#arrow-red)" />\n'
    svg += f'<text x="{px+10}" y="{py+40}" fill="#f38ba8" font-size="13">m·g·sin(φ)</text>\n'
    svg += '<rect x="500" y="110" width="310" height="220" rx="10" fill="#313244" stroke="#45475a" stroke-width="2" />\n'
    svg += '<text x="655" y="140" fill="#89dceb" font-size="16" font-weight="bold" text-anchor="middle">Зовнішні крутильні моменти</text>\n'
    svg += '<text x="520" y="180" fill="#cdd6f4" font-size="14">1. Постійний момент (DC):</text>\n'
    svg += '<text x="540" y="205" fill="#f9e2af" font-size="15" font-family="monospace">T_dc ↔ I_dc</text>\n'
    svg += '<text x="540" y="225" fill="#a6adc8" font-size="12">(змушує маятник обертатися)</text>\n'
    svg += '<text x="520" y="260" fill="#cdd6f4" font-size="14">2. Змінний момент (AC/ВЧ):</text>\n'
    svg += '<text x="540" y="285" fill="#89b4fa" font-size="14" font-family="monospace">T_ac·sin(Ω·t) ↔ I_ac·sin(ω_rf·t)</text>\n'
    svg += '<text x="540" y="305" fill="#a6adc8" font-size="12">(періодичне "струшування" осі)</text>\n'
    svg += '<rect x="60" y="365" width="730" height="40" rx="8" fill="#181825" stroke="#f9e2af" stroke-width="1.5" />\n'
    svg += '<text x="425" y="390" fill="#f9e2af" font-size="14" font-weight="bold" text-anchor="middle">Фазове захоплення: середня швидкість обертання ⟨dφ/dt⟩ строго "залипає" на n·Ω</text>\n'
    svg += '</svg>'
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)

def generate_shapiro_iv_diagram(filepath):
    svg = create_svg_header(850, 460)
    svg += '<rect x="15" y="15" width="820" height="430" rx="12" fill="#181825" stroke="#313244" stroke-width="2" />\n'
    svg += '<text x="425" y="45" fill="#cdd6f4" font-size="20" font-weight="bold" text-anchor="middle">Вольт-амперна характеристика з квантованими сходинками Шапіро</text>\n'
    ox, oy = 160, 375
    svg += f'<path d="M {ox} {oy} L 780 {oy}" stroke="#a6adc8" stroke-width="2.5" marker-end="url(#arrow)" />\n'
    svg += f'<path d="M {ox} {oy} L {ox} 70" stroke="#a6adc8" stroke-width="2.5" marker-end="url(#arrow)" />\n'
    svg += f'<text x="790" y="405" fill="#cdd6f4" font-size="14" font-weight="bold" text-anchor="end">Напруга ⟨V⟩</text>\n'
    svg += f'<text x="150" y="55" fill="#cdd6f4" font-size="15" font-weight="bold" text-anchor="middle">Струм I_dc</text>\n'
    svg += '<path d="M 160 375 L 160 310 C 170 300 220 280 300 240 C 380 200 500 150 720 100" stroke="#585b70" stroke-width="2" stroke-dasharray="6,6" fill="none" />\n'
    svg += '<text x="630" y="140" fill="#6c7086" font-size="13">Без НВЧ випромінювання (I_ac = 0)</text>\n'
    v0, v1, v2, v3 = 160, 310, 470, 630
    svg += f'<line x1="{v1}" y1="70" x2="{v1}" y2="375" stroke="#313244" stroke-width="1.5" stroke-dasharray="4,4" />\n'
    svg += f'<line x1="{v2}" y1="70" x2="{v2}" y2="375" stroke="#313244" stroke-width="1.5" stroke-dasharray="4,4" />\n'
    svg += f'<line x1="{v3}" y1="70" x2="{v3}" y2="375" stroke="#313244" stroke-width="1.5" stroke-dasharray="4,4" />\n'
    svg += f'<text x="{v0}" y="400" fill="#a6e3a1" font-size="13" font-weight="bold" text-anchor="middle">V = 0</text>\n'
    svg += f'<text x="{v1}" y="400" fill="#89dceb" font-size="13" font-weight="bold" text-anchor="middle">V₁ = ħ·ω_rf / 2e</text>\n'
    svg += f'<text x="{v2}" y="400" fill="#89dceb" font-size="13" font-weight="bold" text-anchor="middle">V₂ = 2·V₁</text>\n'
    svg += f'<text x="{v3}" y="400" fill="#89dceb" font-size="13" font-weight="bold" text-anchor="middle">V₃ = 3·V₁</text>\n'
    path_data = (
        f"M {v0} 375 L {v0} 290 "
        f"C {v0+30} 285 {v1-30} 265 {v1} 260 "
        f"L {v1} 200 "
        f"C {v1+30} 195 {v2-30} 185 {v2} 180 "
        f"L {v2} 130 "
        f"C {v2+30} 125 {v3-30} 120 {v3} 115 "
        f"L {v3} 80"
    )
    svg += f'<path d="{path_data}" stroke="#89dceb" stroke-width="3.5" fill="none" />\n'
    svg += f'<line x1="{v1-15}" y1="200" x2="{v1-15}" y2="260" stroke="#f9e2af" stroke-width="2" marker-end="url(#arrow)" marker-start="url(#arrow)" />\n'
    svg += f'<text x="{v1-25}" y="235" fill="#f9e2af" font-size="13" font-weight="bold" text-anchor="end">Ширина сходинки ΔI₁</text>\n'
    svg += f'<text x="{v0-12}" y="335" fill="#a6e3a1" font-size="14" font-weight="bold" text-anchor="end">n = 0</text>\n'
    svg += f'<text x="{v1+12}" y="235" fill="#89dceb" font-size="14" font-weight="bold">n = 1</text>\n'
    svg += f'<text x="{v2+12}" y="155" fill="#89dceb" font-size="14" font-weight="bold">n = 2</text>\n'
    svg += f'<text x="{v3+12}" y="100" fill="#89dceb" font-size="14" font-weight="bold">n = 3</text>\n'
    svg += '<rect x="520" y="170" width="290" height="80" rx="8" fill="#313244" stroke="#45475a" />\n'
    svg += '<text x="665" y="195" fill="#f5e0dc" font-size="14" font-weight="bold" text-anchor="middle">Квантування напруги Шапіро:</text>\n'
    svg += '<text x="665" y="225" fill="#89dceb" font-size="17" font-weight="bold" font-family="monospace" text-anchor="middle">V_n = n · (h · f_rf / 2e)</text>\n'
    svg += '</svg>'
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)

def generate_arnold_tongues_diagram(filepath):
    svg = create_svg_header(850, 440)
    svg += '<rect x="15" y="15" width="820" height="410" rx="12" fill="#181825" stroke="#313244" stroke-width="2" />\n'
    svg += '<text x="425" y="45" fill="#cdd6f4" font-size="20" font-weight="bold" text-anchor="middle">Язики Арнольда та області фазового захоплення у просторі параметрів</text>\n'
    ox, oy = 120, 350
    svg += f'<path d="M {ox} {oy} L 780 {oy}" stroke="#a6adc8" stroke-width="2.5" marker-end="url(#arrow)" />\n'
    svg += f'<path d="M {ox} {oy} L {ox} 70" stroke="#a6adc8" stroke-width="2.5" marker-end="url(#arrow)" />\n'
    svg += f'<text x="790" y="380" fill="#cdd6f4" font-size="14" font-weight="bold" text-anchor="end">Постійний струм I_dc / ω_rf</text>\n'
    svg += f'<text x="110" y="55" fill="#cdd6f4" font-size="15" font-weight="bold" text-anchor="middle">Амплітуда НВЧ струму I_ac</text>\n'
    tongues = [
        (200, "n = 0", "#a6e3a1"),
        (350, "n = 1", "#89dceb"),
        (500, "n = 2", "#b4befe"),
        (650, "n = 3", "#f9e2af")
    ]
    for cx, label, color in tongues:
        path_d = f"M {cx} {oy} L {cx-45} 100 L {cx+45} 100 Z"
        svg += f'<path d="{path_d}" fill="{color}" fill-opacity="0.25" stroke="{color}" stroke-width="2.5" />\n'
        svg += f'<text x="{cx}" y="150" fill="{color}" font-size="16" font-weight="bold" text-anchor="middle">{label}</text>\n'
        svg += f'<circle cx="{cx}" cy="{oy}" r="4" fill="{color}" />\n'
    svg += '<text x="270" y="110" fill="#6c7086" font-size="13">Квазіперіодичний рух / розсинхронізація</text>\n'
    svg += '<line x1="120" y1="200" x2="760" y2="200" stroke="#f38ba8" stroke-width="2" stroke-dasharray="6,4" />\n'
    svg += '<text x="765" y="190" fill="#f38ba8" font-size="12" text-anchor="end">Перетин при фіксованій НВЧ потужності</text>\n'
    svg += '<rect x="160" y="370" width="530" height="35" rx="6" fill="#313244" stroke="#45475a" />\n'
    svg += '<text x="425" y="392" fill="#cdd6f4" font-size="13" text-anchor="middle">Всередині кожного "язика" середня частота ⟨dφ/dt⟩ строго дорівнює n·ω_rf</text>\n'
    svg += '</svg>'
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)

def generate_bessel_widths_diagram(filepath):
    svg = create_svg_header(850, 440)
    svg += '<rect x="15" y="15" width="820" height="410" rx="12" fill="#181825" stroke="#313244" stroke-width="2" />\n'
    svg += '<text x="425" y="45" fill="#cdd6f4" font-size="20" font-weight="bold" text-anchor="middle">Залежність ширин сходинок Шапіро від амплітуди НВЧ напруги (функції Бесселя)</text>\n'
    ox, oy = 120, 240
    svg += f'<path d="M 120 {oy} L 780 {oy}" stroke="#a6adc8" stroke-width="2.5" marker-end="url(#arrow)" />\n'
    svg += f'<path d="M {ox} 390 L {ox} 70" stroke="#a6adc8" stroke-width="2.5" marker-end="url(#arrow)" />\n'
    svg += f'<text x="790" y="270" fill="#cdd6f4" font-size="14" font-weight="bold" text-anchor="end">x = 2e·V_ac / (ħ·ω_rf)</text>\n'
    svg += f'<text x="110" y="55" fill="#cdd6f4" font-size="14" font-weight="bold" text-anchor="middle">ΔI_n / (2·I_c)</text>\n'
    def j0(x):
        val = 0
        for m in range(12):
            val += ((-1)**m * (x/2)**(2*m)) / (math.factorial(m)**2)
        return val
    def j1(x):
        val = 0
        for m in range(12):
            val += ((-1)**m * (x/2)**(2*m+1)) / (math.factorial(m) * math.factorial(m+1))
        return val
    def j2(x):
        val = 0
        for m in range(12):
            val += ((-1)**m * (x/2)**(2*m+2)) / (math.factorial(m) * math.factorial(m+2))
        return val
    def get_path(func):
        pts = []
        for i in range(101):
            xv = i * 0.1
            yv = abs(func(xv))
            px = ox + xv * 62
            py = oy - yv * 140
            pts.append(f"{px:.1f},{py:.1f}")
        return "M " + " L ".join(pts)
    p_j0 = get_path(j0)
    p_j1 = get_path(j1)
    p_j2 = get_path(j2)
    svg += f'<path d="{p_j0}" stroke="#a6e3a1" stroke-width="3" fill="none" />\n'
    svg += f'<path d="{p_j1}" stroke="#89dceb" stroke-width="3" fill="none" />\n'
    svg += f'<path d="{p_j2}" stroke="#f9e2af" stroke-width="3" fill="none" />\n'
    svg += '<rect x="540" y="80" width="260" height="110" rx="8" fill="#313244" stroke="#45475a" />\n'
    svg += '<line x1="560" y1="105" x2="600" y2="105" stroke="#a6e3a1" stroke-width="3" />\n'
    svg += '<text x="610" y="110" fill="#a6e3a1" font-size="14" font-weight="bold">|J₀(x)| (n = 0, надструм)</text>\n'
    svg += '<line x1="560" y1="135" x2="600" y2="135" stroke="#89dceb" stroke-width="3" />\n'
    svg += '<text x="610" y="140" fill="#89dceb" font-size="14" font-weight="bold">|J₁(x)| (1-ша сходинка)</text>\n'
    svg += '<line x1="560" y1="165" x2="600" y2="165" stroke="#f9e2af" stroke-width="3" />\n'
    svg += '<text x="610" y="170" fill="#f9e2af" font-size="14" font-weight="bold">|J₂(x)| (2-га сходинка)</text>\n'
    svg += '<rect x="200" y="380" width="450" height="35" rx="6" fill="#313244" stroke="#45475a" />\n'
    svg += '<text x="425" y="402" fill="#cdd6f4" font-size="14" font-family="monospace" text-anchor="middle">ΔI_n(V_ac) = 2 · I_c · |J_n(2e·V_ac / ħ·ω_rf)|</text>\n'
    svg += '</svg>'
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = ensure_img_dir(base_dir)
    generate_rcsj_diagram(os.path.join(img_dir, "josephson-junction-rcsj.svg"))
    generate_pendulum_diagram(os.path.join(img_dir, "pendulum-analogy.svg"))
    generate_shapiro_iv_diagram(os.path.join(img_dir, "shapiro-iv-characteristic.svg"))
    generate_arnold_tongues_diagram(os.path.join(img_dir, "arnold-tongues-shapiro.svg"))
    generate_bessel_widths_diagram(os.path.join(img_dir, "bessel-step-widths.svg"))
    print("Successfully generated all SVGs in img/")

if __name__ == "__main__":
    main()
