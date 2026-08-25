import os
import math

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

img_dir = os.path.join(os.path.dirname(__file__), "img")
ensure_dir(img_dir)

def create_svg(filename, width, height, elements):
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '  <style>',
        '    .bg { fill: #ffffff; }',
        '    .title { font-family: system-ui, sans-serif; font-size: 14px; font-weight: bold; fill: #1e293b; text-anchor: middle; }',
        '    .label { font-family: system-ui, sans-serif; font-size: 11px; fill: #334155; }',
        '    .label-center { font-family: system-ui, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; }',
        '    .label-small { font-family: system-ui, sans-serif; font-size: 10px; fill: #64748b; text-anchor: middle; }',
        '    .label-bold { font-family: system-ui, sans-serif; font-size: 11px; font-weight: bold; fill: #0f172a; }',
        '    .axis { stroke: #475569; stroke-width: 1.5; marker-end: url(#arrow); }',
        '    .grid { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 4,4; }',
        '    .line-blue { stroke: #0284c7; stroke-width: 2; fill: none; }',
        '    .line-red { stroke: #e11d48; stroke-width: 2; fill: none; }',
        '    .line-green { stroke: #059669; stroke-width: 2; fill: none; }',
        '    .box { fill: #f8fafc; stroke: #0284c7; stroke-width: 1.5; rx: 6; ry: 6; }',
        '    .box-green { fill: #f0fdf4; stroke: #16a34a; stroke-width: 1.5; rx: 6; ry: 6; }',
        '    .box-amber { fill: #fffbeb; stroke: #d97706; stroke-width: 1.5; rx: 6; ry: 6; }',
        '    .box-purple { fill: #faf5ff; stroke: #9333ea; stroke-width: 1.5; rx: 6; ry: 6; }',
        '    .level { stroke: #1e293b; stroke-width: 2; }',
        '    .transition { stroke: #dc2626; stroke-width: 1.5; stroke-dasharray: 3,3; marker-end: url(#arrow-red); }',
        '  </style>',
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#475569" />',
        '    </marker>',
        '    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626" />',
        '    </marker>',
        '    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0284c7" />',
        '    </marker>',
        '  </defs>',
        '  <rect width="100%" height="100%" class="bg" />',
        '  <g transform="translate(0, 0)">',
    ]
    svg.extend(elements)
    svg.append('  </g>')
    svg.append('</svg>')
    with open(os.path.join(img_dir, filename), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

# Fig 1: Energy Hyperfine Zeeman Splitting
def generate_fig1():
    elements = [
        '  <text x="425" y="25" class="title">Надтонка структура стану Cs-133 та розщеплення Зеемана</text>',
        
        # Left side: zero B field levels
        '  <line x1="40" y1="210" x2="140" y2="210" class="level" />',
        '  <text x="90" y="240" class="label-center">Основний стан ⁶S₁/₂</text>',
        '  <text x="90" y="258" class="label-small">(B = 0)</text>',
        
        # Splitting arrow to HFS
        '  <path d="M 140 210 L 220 130" stroke="#94a3b8" stroke-dasharray="3,3" />',
        '  <path d="M 140 210 L 220 290" stroke="#94a3b8" stroke-dasharray="3,3" />',
        
        # HFS levels
        '  <line x1="220" y1="130" x2="330" y2="130" class="level" />',
        '  <text x="275" y="112" class="label-center" font-weight="bold">F = 4</text>',
        '  <line x1="220" y1="290" x2="330" y2="290" class="level" />',
        '  <text x="275" y="312" class="label-center" font-weight="bold">F = 3</text>',
        
        # ΔE_hfs dimension
        '  <line x1="240" y1="138" x2="240" y2="190" stroke="#2563eb" stroke-width="1.5" marker-start="url(#arrow-blue)" />',
        '  <line x1="240" y1="230" x2="240" y2="282" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arrow-blue)" />',
        '  <rect x="248" y="195" width="134" height="30" fill="#eff6ff" rx="4" stroke="#bfdbfe" />',
        '  <text x="315" y="214" class="label-center" fill="#1e40af" font-weight="bold">ν₀ = 9.192 631 770 Гц</text>',
        
        # Splitting arrow to Zeeman field
        '  <path d="M 330 130 L 450 70" stroke="#94a3b8" stroke-dasharray="3,3" />',
        '  <path d="M 330 130 L 450 190" stroke="#94a3b8" stroke-dasharray="3,3" />',
        '  <path d="M 330 290 L 450 230" stroke="#94a3b8" stroke-dasharray="3,3" />',
        '  <path d="M 330 290 L 450 350" stroke="#94a3b8" stroke-dasharray="3,3" />',
        
        # Zeeman sublevels (F=4)
        '  <line x1="450" y1="70" x2="620" y2="50" stroke="#94a3b8" stroke-width="1" />',
        '  <text x="635" y="54" class="label">m_F = +4</text>',
        '  <line x1="450" y1="130" x2="620" y2="130" stroke="#2563eb" stroke-width="2.5" />',
        '  <text x="635" y="134" class="label-bold" fill="#1e40af">F = 4, m_F = 0</text>',
        '  <line x1="450" y1="190" x2="620" y2="210" stroke="#94a3b8" stroke-width="1" />',
        '  <text x="635" y="214" class="label">m_F = -4</text>',
        
        # Zeeman sublevels (F=3)
        '  <line x1="450" y1="230" x2="620" y2="220" stroke="#94a3b8" stroke-width="1" />',
        '  <text x="635" y="224" class="label">m_F = +3</text>',
        '  <line x1="450" y1="290" x2="620" y2="290" stroke="#2563eb" stroke-width="2.5" />',
        '  <text x="635" y="294" class="label-bold" fill="#1e40af">F = 3, m_F = 0</text>',
        '  <line x1="450" y1="350" x2="620" y2="360" stroke="#94a3b8" stroke-width="1" />',
        '  <text x="635" y="364" class="label">m_F = -3</text>',
        
        # Clock transition arrow
        '  <line x1="535" y1="285" x2="535" y2="224" class="transition" />',
        '  <line x1="535" y1="190" x2="535" y2="135" class="transition" />',
        '  <rect x="420" y="195" width="160" height="24" fill="#fef2f2" rx="4" stroke="#fca5a5" />',
        '  <text x="500" y="211" class="label-center" fill="#991b1b" font-weight="bold">Перехід годинника (Δm_F = 0)</text>',
        
        # Bottom annotation
        '  <text x="535" y="390" class="label-center">Зовнішнє магнітне поле B₀ (C-field)</text>',
    ]
    create_svg("fig1-energy-hyperfine.svg", 850, 410, elements)

# Fig 2: Ramsey Atomic Fountain Diagram
def generate_fig2():
    elements = [
        '  <text x="425" y="25" class="title">Будова цезієвого атомного фонтана (NIST-F1 / SYRTE)</text>',
        
        # Outer vacuum tube
        '  <rect x="300" y="50" width="220" height="340" fill="#f8fafc" stroke="#64748b" stroke-width="2" rx="10" />',
        '  <text x="410" y="72" class="label-center" font-weight="bold">Високовакуумна камера</text>',
        
        # Trapping region (bottom)
        '  <circle cx="410" cy="350" r="24" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" />',
        '  <circle cx="410" cy="350" r="6" fill="#e11d48" />',
        '  <text x="180" y="348" class="label" font-weight="bold">МОТ / Охолодження</text>',
        '  <text x="180" y="364" class="label-small">(T ≈ 1 мкК, 6 лазерів)</text>',
        
        # Upward trajectory arrow (split around cavity text)
        '  <path d="M 405 320 C 405 260 405 255 405 255" fill="none" stroke="#e11d48" stroke-width="2" stroke-dasharray="4,4" />',
        '  <path d="M 405 205 C 405 120 405 100 410 95 C 415 100 415 120 415 205" fill="none" stroke="#e11d48" stroke-width="2" stroke-dasharray="4,4" />',
        '  <path d="M 415 255 C 415 260 415 320 415 320" fill="none" stroke="#e11d48" stroke-width="2" stroke-dasharray="4,4" />',
        '  <text x="445" y="110" class="label-small">Апогей траєкторії (H ≈ 1 м)</text>',
        
        # Microwave cavity (Pass 1 & 2)
        '  <rect x="320" y="210" width="180" height="42" fill="#fef3c7" stroke="#d97706" stroke-width="2" rx="4" />',
        '  <text x="410" y="228" class="label-center" font-weight="bold">НВЧ-резонатор Рамзі</text>',
        '  <text x="410" y="243" class="label-small">Перший прохід (вгору) та другий (вниз)</text>',
        '  <text x="515" y="235" class="label" font-weight="bold">НВЧ 9.192 ГГц</text>',
        
        # State selection zone
        '  <rect x="340" y="275" width="140" height="25" fill="#f3e8ff" stroke="#9333ea" stroke-width="1.5" rx="3" />',
        '  <text x="410" y="291" class="label-center" font-weight="bold">Селекція (F=3, m_F=0)</text>',
        
        # Detection region (bottom right)
        '  <rect x="545" y="325" width="180" height="50" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5" rx="6" />',
        '  <text x="635" y="346" class="label-center" font-weight="bold">Детектор флуоресценції</text>',
        '  <text x="635" y="363" class="label-small">Вимірювання N(F=4) та N(F=3)</text>',
        '  <line x1="434" y1="350" x2="545" y2="350" stroke="#16a34a" stroke-width="1.5" marker-end="url(#arrow)" />',
        
        # C-field solenoid coil label
        '  <line x1="280" y1="130" x2="280" y2="190" stroke="#0284c7" stroke-width="2" />',
        '  <line x1="275" y1="130" x2="285" y2="130" stroke="#0284c7" stroke-width="2" />',
        '  <line x1="275" y1="190" x2="285" y2="190" stroke="#0284c7" stroke-width="2" />',
        '  <text x="140" y="155" class="label" font-weight="bold">Зовнішнє C-поле B₀</text>',
        '  <text x="140" y="172" class="label-small">Однорідний соленоїд</text>',
    ]
    create_svg("fig2-ramsey-fountain.svg", 850, 410, elements)

# Fig 3: Ramsey Fringes vs Rabi Profile
def generate_fig3():
    elements = [
        '  <text x="425" y="25" class="title">Порівняння спектрального відгуку Рабі та інтерференції Рамзі</text>',
        
        # Axes
        '  <line x1="60" y1="340" x2="740" y2="340" class="axis" />',
        '  <text x="740" y="360" class="label" font-weight="bold">Частота (ν - ν₀)</text>',
        '  <line x1="425" y1="340" x2="425" y2="50" class="axis" />',
        '  <text x="425" y="42" class="label-center" font-weight="bold">Ймовірність переходу P_ge</text>',
        
        # Center marker ν_0
        '  <line x1="425" y1="340" x2="425" y2="55" stroke="#94a3b8" stroke-dasharray="3,3" />',
        '  <text x="425" y="358" class="label-center" font-weight="bold">ν₀</text>',
    ]
    
    # Generate points for Rabi envelope
    rabi_pts = []
    ramsey_pts = []
    for px in range(70, 740, 2):
        x = (px - 425) / 50.0
        w_rabi = 1.2
        denom = x**2 + w_rabi**2
        p_rabi = (w_rabi**2 / denom) * (math.sin(math.sqrt(denom) * 1.5))**2
        py_rabi = 330 - p_rabi * 250
        rabi_pts.append(f"{px:.1f},{py_rabi:.1f}")
        
        T_ratio = 5.0
        p_ramsey = p_rabi * (math.cos(x * T_ratio))**2
        py_ramsey = 330 - p_ramsey * 250
        ramsey_pts.append(f"{px:.1f},{py_ramsey:.1f}")
        
    elements.append(f'  <polyline points="{" ".join(rabi_pts)}" stroke="#dc2626" stroke-width="2" stroke-dasharray="6,4" fill="none" />')
    elements.append(f'  <polyline points="{" ".join(ramsey_pts)}" stroke="#0284c7" stroke-width="2" fill="none" />')
    
    # Linewidth annotations
    elements.extend([
        '  <line x1="408" y1="120" x2="442" y2="120" stroke="#0284c7" stroke-width="1.5" marker-start="url(#arrow-blue)" marker-end="url(#arrow-blue)" />',
        '  <rect x="455" y="105" width="165" height="30" fill="#f0f9ff" rx="4" stroke="#bae6fd" />',
        '  <text x="537" y="124" class="label-center" fill="#0369a1" font-weight="bold">Δν_Ramsey = 1 / (2T) ≈ 1 Гц</text>',
        
        '  <line x1="290" y1="260" x2="560" y2="260" stroke="#dc2626" stroke-width="1.5" marker-start="url(#arrow-red)" marker-end="url(#arrow-red)" />',
        '  <rect x="575" y="245" width="155" height="30" fill="#fef2f2" rx="4" stroke="#fca5a5" />',
        '  <text x="652" y="264" class="label-center" fill="#991b1b" font-weight="bold">Δν_Rabi = 1 / τ ≈ 100 Гц</text>',
        
        '  <rect x="75" y="60" width="220" height="60" fill="#ffffff" rx="6" stroke="#cbd5e1" stroke-width="1.5" />',
        '  <line x1="85" y1="80" x2="115" y2="80" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,3" />',
        '  <text x="125" y="84" class="label">Оконтурення Рабі (1 зона)</text>',
        '  <line x1="85" y1="100" x2="115" y2="100" stroke="#0284c7" stroke-width="2" />',
        '  <text x="125" y="104" class="label" font-weight="bold">Плюмаж Рамзі (2 зони)</text>',
    ])
    create_svg("fig3-ramsey-fringes.svg", 850, 390, elements)

# Fig 4: Closed Loop Servo Feedback
def generate_fig4():
    elements = [
        '  <text x="425" y="25" class="title">Контур автопідстроювання частоти (Phase-Locked Servo Loop)</text>',
        
        # VCXO Block
        '  <rect x="50" y="140" width="130" height="60" class="box" />',
        '  <text x="115" y="165" class="label-center" font-weight="bold">Кварцовий</text>',
        '  <text x="115" y="185" class="label-center" font-weight="bold">генератор VCXO</text>',
        '  <text x="115" y="215" class="label-small">(f ≈ 10 МГц)</text>',
        
        # Arrow VCXO to Synthesizer
        '  <line x1="180" y1="170" x2="250" y2="170" class="axis" />',
        
        # Microwave Synthesizer
        '  <rect x="250" y="140" width="130" height="60" class="box-amber" />',
        '  <text x="315" y="165" class="label-center" font-weight="bold">НВЧ-синтезатор</text>',
        '  <text x="315" y="185" class="label-center" font-weight="bold">частоти</text>',
        '  <text x="315" y="215" class="label-small">(× 919.26...)</text>',
        
        # Arrow Synthesizer to Atomic Cavity
        '  <line x1="380" y1="170" x2="450" y2="170" class="axis" />',
        '  <text x="415" y="160" class="label-small">9.192 ГГц</text>',
        
        # Atomic Physics Cavity / Physics Package
        '  <rect x="450" y="130" width="140" height="80" class="box-green" />',
        '  <text x="520" y="160" class="label-center" font-weight="bold">Атомна комірка /</text>',
        '  <text x="520" y="177" class="label-center" font-weight="bold">Фонтан (Cs-133)</text>',
        '  <text x="520" y="194" class="label-small">Резонанс Рамзі</text>',
        
        # Arrow Physics to Detector
        '  <line x1="590" y1="170" x2="650" y2="170" class="axis" />',
        
        # Photodetector / Discriminator
        '  <rect x="650" y="140" width="130" height="60" class="box-purple" />',
        '  <text x="715" y="165" class="label-center" font-weight="bold">Детектор</text>',
        '  <text x="715" y="185" class="label-center" font-weight="bold">флуоресценції</text>',
        
        # Downward Arrow to Error Detector & PID
        '  <path d="M 715 200 L 715 290 L 600 290" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arrow)" />',
        '  <text x="670" y="260" class="label-small">Сигнал N₄ / N₃</text>',
        
        # PID Controller
        '  <rect x="430" y="260" width="170" height="60" class="box" />',
        '  <text x="515" y="285" class="label-center" font-weight="bold">Синхронний детектор</text>',
        '  <text x="515" y="302" class="label-center" font-weight="bold">&amp; PID-регулятор</text>',
        
        # Feedback Arrow back to VCXO
        '  <path d="M 430 290 L 115 290 L 115 200" fill="none" stroke="#0284c7" stroke-width="2" marker-end="url(#arrow-blue)" />',
        '  <rect x="220" y="275" width="160" height="26" fill="#eff6ff" rx="4" stroke="#bfdbfe" />',
        '  <text x="300" y="292" class="label-center" fill="#1e40af" font-weight="bold">Напруга помилки U_ctrl</text>',
        
        # Standard Frequency Output Arrow from VCXO
        '  <path d="M 115 140 L 115 75 L 220 75" fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow)" />',
        '  <rect x="225" y="60" width="180" height="30" fill="#f0fdf4" rx="4" stroke="#bbf7d0" />',
        '  <text x="315" y="80" class="label-center" fill="#15803d" font-weight="bold">Вихід 10 МГц / 1 PPS (SI)</text>',
    ]
    create_svg("fig4-feedback-loop.svg", 850, 360, elements)

if __name__ == "__main__":
    generate_fig1()
    generate_fig2()
    generate_fig3()
    generate_fig4()
    print("All figures successfully generated in img/")
