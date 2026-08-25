import os

def create_svg_fig1(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%">
  <rect width="800" height="450" fill="#ffffff"/>
  
  <!-- Title -->
  <text x="400" y="32" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Спин-орбітальний механізм магнітокристалічної анізотропії</text>
  
  <!-- Panel 1: Crystal Field & Orbitals -->
  <g transform="translate(40, 60)">
    <rect width="320" height="340" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
    <text x="160" y="30" font-family="sans-serif" font-size="15" font-weight="bold" text-anchor="middle" fill="#0f172a">1. Кристалічне поле іонів ґратки</text>
    
    <!-- Lattice Ions -->
    <circle cx="60" cy="120" r="16" fill="#ef4444" opacity="0.85"/>
    <text x="60" y="125" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#ffffff">Z+</text>
    <circle cx="260" cy="120" r="16" fill="#ef4444" opacity="0.85"/>
    <text x="260" y="125" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#ffffff">Z+</text>
    <circle cx="160" cy="260" r="16" fill="#ef4444" opacity="0.85"/>
    <text x="160" y="265" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#ffffff">Z+</text>
    <circle cx="160" cy="60" r="16" fill="#ef4444" opacity="0.85"/>
    <text x="160" y="65" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#ffffff">Z+</text>

    <!-- Electron Orbital (d-orbital lobe) -->
    <ellipse cx="160" cy="160" rx="22" ry="55" fill="#3b82f6" opacity="0.4" transform="rotate(0 160 160)"/>
    <ellipse cx="160" cy="160" rx="22" ry="55" fill="#3b82f6" opacity="0.4" transform="rotate(90 160 160)"/>
    <circle cx="160" cy="160" r="8" fill="#1e3a8a"/>

    <!-- Orbital Angular Momentum L -->
    <line x1="160" y1="160" x2="160" y2="85" stroke="#2563eb" stroke-width="3" marker-end="url(#arrow-blue)"/>
    <text x="175" y="105" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1d4ed8">L (орбіталь)</text>

    <text x="160" y="305" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#334155">Електростатичне поле ґратки</text>
    <text x="160" y="322" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#334155">орієнтує електронну хмару L</text>
  </g>

  <!-- Middle Arrow: Spin-Orbit Coupling -->
  <g transform="translate(370, 180)">
    <rect width="60" height="90" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1"/>
    <text x="30" y="28" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#0f172a">Зв'язок</text>
    <text x="30" y="48" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#2563eb">λ L · S</text>
    <text x="30" y="70" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#64748b">спін-орбіта</text>
  </g>

  <!-- Panel 2: Spin & Magnetization Vector -->
  <g transform="translate(440, 60)">
    <rect width="320" height="340" rx="10" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
    <text x="160" y="30" font-family="sans-serif" font-size="15" font-weight="bold" text-anchor="middle" fill="#0f172a">2. Фіксація спіна до осей ґратки</text>

    <!-- Crystal Axes -->
    <line x1="160" y1="230" x2="160" y2="70" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>
    <line x1="90" y1="170" x2="230" y2="170" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>
    <text x="165" y="80" font-family="sans-serif" font-size="12" fill="#64748b">Вісь c [0001]</text>

    <!-- Easy Axis Spin S -->
    <line x1="160" y1="170" x2="160" y2="90" stroke="#059669" stroke-width="4" marker-end="url(#arrow-green)"/>
    <text x="175" y="120" font-family="sans-serif" font-size="14" font-weight="bold" fill="#047857">S (легка вісь)</text>

    <!-- Hard Axis Spin S' (Rotated) -->
    <line x1="160" y1="170" x2="225" y2="115" stroke="#dc2626" stroke-width="3.5" stroke-dasharray="6,3" marker-end="url(#arrow-red)"/>
    <text x="220" y="105" font-family="sans-serif" font-size="13" font-weight="bold" fill="#b91c1c">S' (важка вісь)</text>

    <!-- Angle Arc -->
    <path d="M 160 120 A 50 50 0 0 1 195 135" fill="none" stroke="#d97706" stroke-width="2"/>
    <text x="180" y="115" font-family="sans-serif" font-size="13" font-weight="bold" fill="#d97706">θ</text>

    <text x="160" y="280" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#334155">Поворот спіна S на кут θ вимагає</text>
    <text x="160" y="298" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#334155">деформації орбіти L проти поля ґратки</text>
    <text x="160" y="320" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#b91c1c">Енергетичні витрати = E_A(θ)</text>
  </g>

  <!-- Markers -->
  <defs>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/>
    </marker>
  </defs>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_svg_fig2(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 420" width="100%" height="100%">
  <rect width="850" height="420" fill="#ffffff"/>
  
  <!-- Title -->
  <text x="425" y="30" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Криві намагнічування M(H) для одноосьових та кубічних кристалів</text>

  <!-- Left Panel: Uniaxial Cobalt -->
  <g transform="translate(40, 50)">
    <rect width="360" height="340" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="180" y="26" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">Одноосьовий кобальт (Co, гексагональний)</text>

    <!-- Axes -->
    <line x1="50" y1="270" x2="330" y2="270" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>
    <line x1="50" y1="270" x2="50" y2="50" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>
    
    <text x="330" y="295" font-family="sans-serif" font-size="13" font-weight="bold" fill="#334155">H (A/м)</text>
    <text x="25" y="45" font-family="sans-serif" font-size="13" font-weight="bold" fill="#334155">M/M_s</text>

    <!-- M_s dashed line -->
    <line x1="50" y1="90" x2="310" y2="90" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>
    <text x="25" y="95" font-family="sans-serif" font-size="12" fill="#64748b">1.0</text>

    <!-- Easy axis curve [0001] -->
    <path d="M 50 270 Q 55 90 75 90 L 310 90" fill="none" stroke="#059669" stroke-width="3"/>
    <text x="85" y="80" font-family="sans-serif" font-size="12" font-weight="bold" fill="#047857">Легка вісь [0001]</text>

    <!-- Hard axis curve [1000] -->
    <line x1="50" y1="270" x2="250" y2="90" stroke="#dc2626" stroke-width="3"/>
    <line x1="250" y1="90" x2="310" y2="90" stroke="#dc2626" stroke-width="3"/>
    <text x="180" y="190" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">Важка площина [1000]</text>

    <!-- H_A Marker -->
    <line x1="250" y1="270" x2="250" y2="90" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,3"/>
    <text x="250" y="290" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#b91c1c">H_A = 2 K_1 / (μ_0 M_s)</text>

    <!-- Shaded area for anisotropy work -->
    <path d="M 50 270 L 250 90 L 50 90 Z" fill="#dc2626" opacity="0.12"/>
    <text x="110" y="160" font-family="sans-serif" font-size="11" font-weight="bold" fill="#991b1b">Робота = K_1</text>
  </g>

  <!-- Right Panel: Cubic Iron -->
  <g transform="translate(440, 50)">
    <rect width="370" height="340" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="185" y="26" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">Кубічне залізо (Fe, ОЦК, K_1 &gt; 0)</text>

    <!-- Axes -->
    <line x1="50" y1="270" x2="340" y2="270" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>
    <line x1="50" y1="270" x2="50" y2="50" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>
    
    <text x="340" y="295" font-family="sans-serif" font-size="13" font-weight="bold" fill="#334155">H (A/м)</text>
    <text x="25" y="45" font-family="sans-serif" font-size="13" font-weight="bold" fill="#334155">M/M_s</text>

    <!-- M_s dashed line -->
    <line x1="50" y1="90" x2="320" y2="90" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,4"/>
    <text x="25" y="95" font-family="sans-serif" font-size="12" fill="#64748b">1.0</text>

    <!-- Easy axis [100] -->
    <path d="M 50 270 Q 55 90 70 90 L 320 90" fill="none" stroke="#059669" stroke-width="3"/>
    <text x="80" y="80" font-family="sans-serif" font-size="12" font-weight="bold" fill="#047857">Легка [100]</text>

    <!-- Intermediate axis [110] -->
    <path d="M 50 270 Q 120 180 180 144 L 180 90 L 320 90" fill="none" stroke="#d97706" stroke-width="2.5"/>
    <text x="185" y="135" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b45309">Проміжна [110]</text>

    <!-- Hard axis [111] -->
    <path d="M 50 270 Q 150 210 240 120 L 280 90 L 320 90" fill="none" stroke="#dc2626" stroke-width="2.5"/>
    <text x="250" y="115" font-family="sans-serif" font-size="12" font-weight="bold" fill="#b91c1c">Важка [111]</text>
  </g>

  <!-- Markers -->
  <defs>
    <marker id="arrow-dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569"/>
    </marker>
  </defs>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_svg_fig3(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" width="100%" height="100%">
  <rect width="800" height="420" fill="#ffffff"/>
  
  <!-- Title -->
  <text x="400" y="30" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Полярні кутові діаграми густини енергії анізотропії E_A(θ)</text>

  <!-- Panel 1: Uniaxial Polar Plot -->
  <g transform="translate(50, 50)">
    <rect width="330" height="340" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="165" y="26" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">Одноосьова анізотропія (K_1 &gt; 0)</text>

    <!-- Polar Grid -->
    <circle cx="165" cy="180" r="110" fill="none" stroke="#e2e8f0" stroke-width="1.5"/>
    <circle cx="165" cy="180" r="75" fill="none" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3,3"/>
    <circle cx="165" cy="180" r="40" fill="none" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3,3"/>

    <!-- Axis lines -->
    <line x1="165" y1="40" x2="165" y2="320" stroke="#64748b" stroke-width="1.5"/>
    <line x1="35" y1="180" x2="295" y2="180" stroke="#64748b" stroke-width="1.5"/>

    <text x="172" y="55" font-family="sans-serif" font-size="12" font-weight="bold" fill="#059669">θ = 0° (Легка вісь)</text>
    <text x="172" y="315" font-family="sans-serif" font-size="12" font-weight="bold" fill="#059669">θ = 180°</text>
    <text x="235" y="172" font-family="sans-serif" font-size="12" font-weight="bold" fill="#dc2626">θ = 90° (Важка)</text>

    <!-- Energy surface r(θ) = r0 + r1 * sin^2(θ) -->
    <!-- Peanut / dumbbell shape along equator -->
    <path d="M 165 140
             C 210 140, 265 150, 265 180
             C 265 210, 210 220, 165 220
             C 120 220, 65 210, 65 180
             C 65 150, 120 140, 165 140 Z" 
          fill="#3b82f6" fill-opacity="0.25" stroke="#1d4ed8" stroke-width="2.5"/>

    <circle cx="165" cy="140" r="5" fill="#059669"/>
    <circle cx="165" cy="220" r="5" fill="#059669"/>
    <circle cx="265" cy="180" r="5" fill="#dc2626"/>
    <circle cx="65" cy="180" r="5" fill="#dc2626"/>
  </g>

  <!-- Panel 2: Cubic Polar Plot (001 plane) -->
  <g transform="translate(420, 50)">
    <rect width="330" height="340" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="165" y="26" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">Кубічна анізотропія Fe (K_1 &gt; 0)</text>

    <!-- Polar Grid -->
    <circle cx="165" cy="180" r="110" fill="none" stroke="#e2e8f0" stroke-width="1.5"/>
    <line x1="165" y1="40" x2="165" y2="320" stroke="#64748b" stroke-width="1.5"/>
    <line x1="35" y1="180" x2="295" y2="180" stroke="#64748b" stroke-width="1.5"/>
    <line x1="66" y1="81" x2="264" y2="279" stroke="#cbd5e1" stroke-dasharray="3,3"/>
    <line x1="66" y1="279" x2="264" y2="81" stroke="#cbd5e1" stroke-dasharray="3,3"/>

    <text x="172" y="55" font-family="sans-serif" font-size="12" font-weight="bold" fill="#059669">[010] Легка</text>
    <text x="240" y="172" font-family="sans-serif" font-size="12" font-weight="bold" fill="#059669">[100] Легка</text>
    <text x="230" y="100" font-family="sans-serif" font-size="11" font-weight="bold" fill="#dc2626">[110] Важка</text>

    <!-- 4-fold rose shape for cubic energy -->
    <!-- Maxima along 45 degree diagonals -->
    <path d="M 165 130
             Q 210 135 225 120
             Q 200 170 215 180
             Q 200 190 225 240
             Q 210 225 165 230
             Q 120 225 105 240
             Q 130 190 115 180
             Q 130 170 105 120
             Q 120 135 165 130 Z"
          fill="#ef4444" fill-opacity="0.25" stroke="#b91c1c" stroke-width="2.5"/>

    <!-- Minima dots along axes -->
    <circle cx="165" cy="130" r="5" fill="#059669"/>
    <circle cx="215" cy="180" r="5" fill="#059669"/>
    <circle cx="165" cy="230" r="5" fill="#059669"/>
    <circle cx="115" cy="180" r="5" fill="#059669"/>

    <!-- Maxima dots along diagonals -->
    <circle cx="225" cy="120" r="4" fill="#dc2626"/>
    <circle cx="225" cy="240" r="4" fill="#dc2626"/>
    <circle cx="105" cy="240" r="4" fill="#dc2626"/>
    <circle cx="105" cy="120" r="4" fill="#dc2626"/>
  </g>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_svg_fig4(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" width="100%" height="100%">
  <rect width="800" height="420" fill="#ffffff"/>
  
  <!-- Title -->
  <text x="400" y="30" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#1e293b">Перемагнічування за моделлю Стонера — Вольфарта</text>

  <!-- Left Panel: Vector diagram -->
  <g transform="translate(40, 50)">
    <rect width="340" height="340" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="170" y="26" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">Геометрія полів та векторів</text>

    <!-- Easy Axis n -->
    <line x1="170" y1="300" x2="170" y2="60" stroke="#059669" stroke-width="2.5" stroke-dasharray="6,3"/>
    <text x="175" y="75" font-family="sans-serif" font-size="13" font-weight="bold" fill="#047857">Вісь легкого намагнічування (EA)</text>

    <!-- Magnetization M -->
    <line x1="170" y1="200" x2="245" y2="110" stroke="#2563eb" stroke-width="4" marker-end="url(#arrow-blue)"/>
    <text x="245" y="105" font-family="sans-serif" font-size="14" font-weight="bold" fill="#1d4ed8">M</text>

    <!-- Angle theta -->
    <path d="M 170 140 A 60 60 0 0 1 210 152" fill="none" stroke="#2563eb" stroke-width="2"/>
    <text x="195" y="140" font-family="sans-serif" font-size="13" font-weight="bold" fill="#1d4ed8">θ</text>

    <!-- External Field H -->
    <line x1="170" y1="200" x2="80" y2="100" stroke="#dc2626" stroke-width="3" marker-end="url(#arrow-red)"/>
    <text x="65" y="95" font-family="sans-serif" font-size="14" font-weight="bold" fill="#b91c1c">H</text>

    <!-- Angle psi -->
    <path d="M 170 130 A 70 70 0 0 0 130 155" fill="none" stroke="#dc2626" stroke-width="2"/>
    <text x="135" y="135" font-family="sans-serif" font-size="13" font-weight="bold" fill="#b91c1c">ψ</text>

    <text x="170" y="315" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#334155">Умова рівноваги: ∂E/∂θ = 0</text>
  </g>

  <!-- Right Panel: Hysteresis loop & switching -->
  <g transform="translate(420, 50)">
    <rect width="340" height="340" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="170" y="26" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#0f172a">Необоротне стрибкоподібне переключення</text>

    <!-- Axes -->
    <line x1="40" y1="180" x2="300" y2="180" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>
    <line x1="170" y1="310" x2="170" y2="50" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>

    <text x="300" y="205" font-family="sans-serif" font-size="12" font-weight="bold" fill="#334155">H</text>
    <text x="145" y="45" font-family="sans-serif" font-size="12" font-weight="bold" fill="#334155">M_H</text>

    <!-- Hysteresis loop rectangle with switching jumps -->
    <!-- Forward branch -->
    <path d="M 50 270 L 110 270 L 110 90 L 290 90" fill="none" stroke="#2563eb" stroke-width="2.5"/>
    <!-- Backward branch -->
    <path d="M 290 90 L 230 90 L 230 270 L 50 270" fill="none" stroke="#2563eb" stroke-width="2.5"/>

    <!-- Switching field arrows -->
    <line x1="110" y1="250" x2="110" y2="110" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-red)"/>
    <line x1="230" y1="110" x2="230" y2="250" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-red)"/>

    <text x="110" y="290" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#b91c1c">-H_sw</text>
    <text x="230" y="290" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#b91c1c">+H_sw</text>
  </g>

  <!-- Markers -->
  <defs>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/>
    </marker>
    <marker id="arrow-dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569"/>
    </marker>
  </defs>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    create_svg_fig1(os.path.join(img_dir, 'fig1-spin-orbit-coupling-mechanism.svg'))
    create_svg_fig2(os.path.join(img_dir, 'fig2-uniaxial-cubic-anisotropy.svg'))
    create_svg_fig3(os.path.join(img_dir, 'fig3-anisotropy-energy-surface.svg'))
    create_svg_fig4(os.path.join(img_dir, 'fig4-stoner-wohlfarth-reversal.svg'))
    print("Figures generated successfully.")

if __name__ == '__main__':
    main()
