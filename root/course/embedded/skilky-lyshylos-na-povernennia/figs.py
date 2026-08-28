import os

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def create_wind_asymmetry_svg(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 390" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #0f141c; }
      .card { fill: #161b22; stroke: #30363d; stroke-width: 1.5px; rx: 8px; }
      .card-warn { fill: #1c1516; stroke: #f85149; stroke-width: 1.5px; rx: 8px; }
      .card-ok { fill: #121d17; stroke: #2ea043; stroke-width: 1.5px; rx: 8px; }
      .title { font-family: system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 700; fill: #e6edf3; }
      .text { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #e6edf3; }
      .text-dim { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; fill: #8b949e; }
      .text-bold { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 700; fill: #e6edf3; }
      .val-ok { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 700; fill: #3fb950; }
      .val-warn { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 700; fill: #f85149; }
      .val-blue { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 700; fill: #58a6ff; }
      .val-amber { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 700; fill: #d29922; }
      .arrow { stroke-width: 2.5px; stroke-linecap: round; stroke-linejoin: round; }
    </style>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#58a6ff" />
    </marker>
    <marker id="arr-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#3fb950" />
    </marker>
    <marker id="arr-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#f85149" />
    </marker>
    <marker id="arr-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#d29922" />
    </marker>
  </defs>

  <rect width="820" height="390" class="bg" />

  <!-- Top Global Wind Banner -->
  <rect x="25" y="15" width="770" height="42" class="card" />
  <text x="45" y="41" class="title">Постійний фоновий вітер у зоні місії:</text>
  <text x="310" y="41" class="val-amber">V_wind = 10 м/с (попутно до цілі, зустрічно на поверненні)</text>
  <line x1="700" y1="36" x2="765" y2="36" stroke="#d29922" class="arrow" marker-end="url(#arr-amber)" />

  <!-- Left Card: Outbound (Політ туди з попутним вітром) -->
  <rect x="25" y="70" width="375" height="305" class="card-ok" />
  <text x="45" y="98" class="title" fill="#3fb950">1. Політ до цілі (попутний вітер)</text>

  <!-- Vector Diagram Outbound -->
  <text x="45" y="128" class="text-dim">Повітряна швидкість V_air:</text>
  <line x1="45" y1="142" x2="165" y2="142" stroke="#58a6ff" class="arrow" marker-end="url(#arr-blue)" />
  <text x="175" y="146" class="val-blue">15 м/с</text>

  <text x="45" y="172" class="text-dim">Попутний вітер V_wind:</text>
  <line x1="45" y1="186" x2="125" y2="186" stroke="#d29922" class="arrow" marker-end="url(#arr-amber)" />
  <text x="135" y="190" class="val-amber">+10 м/с</text>

  <text x="45" y="216" class="text-dim">Шляхова швидкість V_ground = V_air + V_wind:</text>
  <line x1="45" y1="230" x2="245" y2="230" stroke="#3fb950" class="arrow" marker-end="url(#arr-green)" />
  <text x="255" y="234" class="val-ok">25 м/с (90 км/год)</text>

  <!-- Metrics Outbound -->
  <rect x="40" y="252" width="345" height="110" fill="#0f141c" stroke="#233527" stroke-width="1px" rx="6px" />
  <text x="55" y="274" class="text">Дистанція польоту до цілі:</text>
  <text x="235" y="274" class="text-bold">10 000 м (10 км)</text>
  <text x="55" y="296" class="text">Час польоту до цілі:</text>
  <text x="235" y="296" class="val-ok">400 с (6 хв 40 с)</text>
  <text x="55" y="318" class="text">Витрата енергії:</text>
  <text x="235" y="318" class="val-ok">56 Вт·год (22% запасу)</text>
  <text x="55" y="342" class="text-dim">Потужність у крейсері: 140 Вт</text>

  <!-- Right Card: Return (Повернення проти зустрічного вітру) -->
  <rect x="420" y="70" width="375" height="305" class="card-warn" />
  <text x="440" y="98" class="title" fill="#f85149">2. Повернення на базу (зустрічний вітер)</text>

  <!-- Vector Diagram Return -->
  <text x="440" y="128" class="text-dim">Повітряна швидкість V_air:</text>
  <line x1="440" y1="142" x2="560" y2="142" stroke="#58a6ff" class="arrow" marker-end="url(#arr-blue)" />
  <text x="570" y="146" class="val-blue">15 м/с</text>

  <text x="440" y="172" class="text-dim">Зустрічний вітер V_wind (гальмує):</text>
  <line x1="520" y1="186" x2="440" y2="186" stroke="#d29922" class="arrow" marker-end="url(#arr-amber)" />
  <text x="535" y="190" class="val-amber">-10 м/с</text>

  <text x="440" y="216" class="text-dim">Шляхова швидкість V_ground = V_air - V_wind:</text>
  <line x1="440" y1="230" x2="480" y2="230" stroke="#f85149" class="arrow" marker-end="url(#arr-red)" />
  <text x="490" y="234" class="val-warn">5 м/с (18 км/год! 5x повільніше)</text>

  <!-- Metrics Return -->
  <rect x="435" y="252" width="345" height="110" fill="#0f141c" stroke="#3b1f22" stroke-width="1px" rx="6px" />
  <text x="450" y="274" class="text">Дистанція повернення:</text>
  <text x="630" y="274" class="text-bold">10 000 м (10 км)</text>
  <text x="450" y="296" class="text">Час повернення на базу:</text>
  <text x="630" y="296" class="val-warn">2000 с (33 хв 20 с!)</text>
  <text x="450" y="318" class="text">Потрібна енергія E_ret:</text>
  <text x="630" y="318" class="val-warn">178 Вт·год (71% запасу!)</text>
  <text x="450" y="342" class="text-dim">Потужність у крейсері: 320 Вт (тяга проти опору)</text>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_pnr_trajectory_svg(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 410" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #0f141c; }
      .grid { stroke: #21262d; stroke-width: 1px; stroke-dasharray: 2 4; }
      .axis { stroke: #484f58; stroke-width: 1.5px; }
      .text { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #e6edf3; }
      .text-title { font-family: system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 700; fill: #e6edf3; }
      .text-dim { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; fill: #8b949e; }
      .line-batt { stroke: #3fb950; stroke-width: 3px; fill: none; }
      .line-ret { stroke: #f85149; stroke-width: 3px; fill: none; }
      .line-res { stroke: #d29922; stroke-width: 2px; stroke-dasharray: 4 4; fill: none; }
      .zone-safe { fill: rgba(46, 160, 67, 0.08); }
      .zone-danger { fill: rgba(248, 81, 73, 0.08); }
      .pnr-box { fill: #1c1516; stroke: #f85149; stroke-width: 1.5px; rx: 6px; }
      .note-box { fill: #161b22; stroke: #30363d; stroke-width: 1px; rx: 4px; }
    </style>
  </defs>

  <rect width="840" height="410" class="bg" />

  <!-- Title -->
  <text x="35" y="28" class="text-title">Динамічна точка неповернення (Point of No Return) під час віддалення від бази</text>

  <!-- Zones -->
  <polygon points="80,50 80,310 430,310 430,50" class="zone-safe" />
  <polygon points="430,50 430,310 770,310 770,50" class="zone-danger" />

  <!-- Grid Lines Horizontal -->
  <line x1="80" y1="50" x2="770" y2="50" class="grid" />
  <line x1="80" y1="115" x2="770" y2="115" class="grid" />
  <line x1="80" y1="180" x2="770" y2="180" class="grid" />
  <line x1="80" y1="245" x2="770" y2="245" class="grid" />
  <line x1="80" y1="310" x2="770" y2="310" class="axis" />

  <!-- Grid Lines Vertical -->
  <line x1="80" y1="50" x2="80" y2="310" class="axis" />
  <line x1="245" y1="50" x2="245" y2="310" class="grid" />
  <line x1="430" y1="50" x2="430" y2="310" stroke="#f85149" stroke-width="1.5px" stroke-dasharray="3 3" />
  <line x1="600" y1="50" x2="600" y2="310" class="grid" />
  <line x1="770" y1="50" x2="770" y2="310" class="grid" />

  <!-- Y-Axis Labels (Energy %) -->
  <text x="30" y="55" class="text-dim">100%</text>
  <text x="35" y="120" class="text-dim">75%</text>
  <text x="35" y="185" class="text-dim">50%</text>
  <text x="35" y="250" class="text-dim">25%</text>
  <text x="45" y="315" class="text-dim">0%</text>
  <text x="20" y="180" transform="rotate(-90 20 180)" class="text-dim" text-anchor="middle">Запас енергії батареї (Wh / % SoC)</text>

  <!-- X-Axis Labels (Distance from Home) -->
  <text x="75" y="330" class="text-dim">0 км</text>
  <text x="235" y="330" class="text-dim">5 км</text>
  <text x="390" y="330" class="text-dim" fill="#f85149" font-weight="700">11.2 км (PNR)</text>
  <text x="590" y="330" class="text-dim">15 км</text>
  <text x="755" y="330" class="text-dim">20 км</text>
  <text x="425" y="355" class="text-dim" text-anchor="middle">Відстань від точки старту / прогрес польоту до цілі</text>

  <!-- Curves -->
  <!-- 1. E_batt (Remaining battery energy decreasing) -->
  <path d="M 80 50 Q 250 85 430 180 T 770 305" class="line-batt" />
  <!-- 2. E_return_required (Growing with distance against headwind) -->
  <path d="M 80 270 Q 250 240 430 180 T 770 70" class="line-ret" />
  <!-- 3. Landing Reserve Floor (E_reserve) -->
  <line x1="80" y1="270" x2="770" y2="270" class="line-res" />

  <!-- Intersection Point PNR -->
  <circle cx="430" cy="180" r="6" fill="#f85149" stroke="#ffffff" stroke-width="2px" />

  <!-- Top Legend in clear space -->
  <rect x="95" y="110" width="180" height="30" class="note-box" />
  <text x="105" y="130" class="text" fill="#3fb950">E_batt (залишок батареї)</text>

  <rect x="550" y="55" width="205" height="42" class="note-box" />
  <text x="560" y="74" class="text" fill="#f85149">E_return (потрібно назад)</text>
  <text x="560" y="89" class="text-dim">Ріст проти зустрічного вітру</text>

  <!-- PNR callout located safely in middle-left area -->
  <rect x="230" y="195" width="185" height="50" class="pnr-box" />
  <text x="240" y="216" class="text" font-weight="700" fill="#f85149">Точка неповернення</text>
  <text x="240" y="234" class="text-dim">E_batt(t) = E_return</text>

  <!-- Landing reserve note in bottom left empty space -->
  <rect x="95" y="280" width="240" height="24" class="note-box" />
  <text x="105" y="296" class="text-dim" fill="#d29922">E_land_reserve (резерв на посадку)</text>

  <!-- Zone Badges -->
  <rect x="180" y="370" width="165" height="24" class="note-box" />
  <text x="190" y="386" class="text" fill="#3fb950">✓ Зона безпечного польоту</text>

  <rect x="480" y="370" width="210" height="24" class="note-box" />
  <text x="490" y="386" class="text" fill="#f85149">✗ Зона втрати борту (Crash)</text>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_voltage_sag_svg(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 410" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #0f141c; }
      .grid { stroke: #21262d; stroke-width: 1px; stroke-dasharray: 2 4; }
      .axis { stroke: #484f58; stroke-width: 1.5px; }
      .text { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #e6edf3; }
      .text-title { font-family: system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 700; fill: #e6edf3; }
      .text-dim { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; fill: #8b949e; }
      .text-bold { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 700; fill: #e6edf3; }
      .line-ocv { stroke: #58a6ff; stroke-width: 2.5px; fill: none; }
      .line-cruise { stroke: #3fb950; stroke-width: 2.5px; fill: none; }
      .line-wind { stroke: #f85149; stroke-width: 3px; fill: none; }
      .line-cutoff { stroke: #d29922; stroke-width: 2px; stroke-dasharray: 4 4; fill: none; }
      .box { fill: #161b22; stroke: #30363d; stroke-width: 1px; rx: 4px; }
    </style>
  </defs>

  <rect width="840" height="410" class="bg" />

  <!-- Title -->
  <text x="35" y="28" class="text-title">Просідання напруги (Voltage Sag) під струмом повернення проти вітру</text>

  <!-- Grid Lines (stopping before legend box in top right) -->
  <line x1="90" y1="50" x2="490" y2="50" class="grid" />
  <line x1="90" y1="100" x2="490" y2="100" class="grid" />
  <line x1="90" y1="150" x2="490" y2="150" class="grid" />
  <line x1="90" y1="200" x2="770" y2="200" class="grid" />
  <line x1="90" y1="250" x2="520" y2="250" class="grid" />
  <line x1="90" y1="300" x2="770" y2="300" class="axis" />

  <line x1="90" y1="50" x2="90" y2="300" class="axis" />
  <line x1="260" y1="50" x2="260" y2="300" class="grid" />
  <line x1="430" y1="50" x2="430" y2="300" class="grid" />
  <line x1="600" y1="210" x2="600" y2="300" class="grid" />
  <line x1="770" y1="50" x2="770" y2="300" class="axis" />

  <!-- Y-Axis Labels (Voltage per cell) -->
  <text x="40" y="55" class="text-dim">4.20 В</text>
  <text x="40" y="105" class="text-dim">3.90 В</text>
  <text x="40" y="155" class="text-dim">3.60 В</text>
  <text x="40" y="205" class="text-dim">3.30 В</text>
  <text x="40" y="255" class="text-dim">3.00 В</text>
  <text x="40" y="305" class="text-dim">2.70 В</text>
  <text x="20" y="175" transform="rotate(-90 20 175)" class="text-dim" text-anchor="middle">Напруга комірки (В / cell)</text>

  <!-- X-Axis Labels (Discharge Capacity / SoC %) -->
  <text x="75" y="320" class="text-dim">100%</text>
  <text x="245" y="320" class="text-dim">75%</text>
  <text x="415" y="320" class="text-dim">50%</text>
  <text x="585" y="320" class="text-dim">25%</text>
  <text x="750" y="320" class="text-dim">0% SoC</text>
  <text x="430" y="350" class="text-dim" text-anchor="middle">Ступінь заряду батареї (State of Charge %)</text>

  <!-- Cutoff Voltage Threshold Line (3.0V per cell) ending at intersection -->
  <line x1="90" y1="250" x2="550" y2="250" class="line-cutoff" />

  <!-- Cutoff label in bottom left area -->
  <rect x="95" y="365" width="310" height="26" class="box" />
  <text x="105" y="382" class="text-dim" fill="#d29922">Поріг відсікання V_cutoff = 3.0 В (Brownout)</text>

  <!-- 1. OCV (Без навантаження I = 0) -->
  <path d="M 90 60 C 200 90 400 135 770 280" class="line-ocv" />

  <!-- 2. Light cruise load (I = 10A, слабкий струм за вітром) -->
  <path d="M 90 85 C 200 115 400 160 770 300" class="line-cruise" />

  <!-- 3. Heavy headwind return load (I = 45A, повна тяга проти вітру) -->
  <path d="M 90 140 C 200 175 400 245 550 250 T 600 300" class="line-wind" />

  <!-- Premature Cutoff Intersection -->
  <circle cx="550" cy="250" r="6" fill="#f85149" stroke="#ffffff" stroke-width="2px" />

  <!-- Legend & Callouts in top right box -->
  <rect x="510" y="55" width="260" height="135" class="box" />
  <line x1="525" y1="75" x2="545" y2="75" stroke="#58a6ff" stroke-width="2.5px" />
  <text x="555" y="79" class="text">V_OCV (ЕРС без струму)</text>

  <line x1="525" y1="97" x2="545" y2="97" stroke="#3fb950" stroke-width="2.5px" />
  <text x="555" y="101" class="text">V_load при I_cruise = 10 A</text>

  <line x1="525" y1="119" x2="545" y2="119" stroke="#f85149" stroke-width="3px" />
  <text x="555" y="123" class="text">V_load при I_wind = 45 A</text>

  <text x="525" y="147" class="text-dim">ΔV_sag = I · R_internal(T)</text>
  <text x="525" y="171" class="text-bold" fill="#f85149">Відсічка на 28% SoC замість 5%!</text>

  <!-- Voltage Sag Indicator Box in bottom area away from curves -->
  <rect x="420" y="365" width="270" height="26" class="box" stroke="#f85149" />
  <text x="430" y="382" class="text" fill="#f85149">Просідання напруги ΔV = 0.7-1.1 В</text>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_rtl_budget_fsm_svg(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 390" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #0f141c; }
      .node { fill: #161b22; stroke: #30363d; stroke-width: 1.5px; rx: 8px; }
      .node-ok { fill: #121d17; stroke: #2ea043; stroke-width: 2px; rx: 8px; }
      .node-warn { fill: #221b10; stroke: #d29922; stroke-width: 2px; rx: 8px; }
      .node-crit { fill: #281416; stroke: #f85149; stroke-width: 2px; rx: 8px; }
      .node-land { fill: #201328; stroke: #bc8cff; stroke-width: 2px; rx: 8px; }
      .title { font-family: system-ui, -apple-system, sans-serif; font-size: 13px; font-weight: 700; fill: #e6edf3; }
      .text { font-family: system-ui, -apple-system, sans-serif; font-size: 12px; fill: #e6edf3; }
      .text-dim { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; fill: #8b949e; }
      .edge { stroke: #58a6ff; stroke-width: 2px; fill: none; }
      .edge-red { stroke: #f85149; stroke-width: 2px; fill: none; }
      .edge-amber { stroke: #d29922; stroke-width: 2px; fill: none; }
    </style>
    <marker id="arr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#58a6ff" />
    </marker>
    <marker id="arr-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#f85149" />
    </marker>
    <marker id="arr-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#d29922" />
    </marker>
  </defs>

  <rect width="860" height="390" class="bg" />

  <!-- Sensor Inputs Layer (Left) -->
  <rect x="25" y="45" width="165" height="65" class="node" />
  <text x="35" y="68" class="title">Оцінка вітру (EKF)</text>
  <text x="35" y="85" class="text-dim">Вектор вітру (V_n, V_e)</text>
  <text x="35" y="100" class="text-dim">Швидкість повітря V_air</text>

  <rect x="25" y="130" width="165" height="65" class="node" />
  <text x="35" y="153" class="title">Геометрія місії</text>
  <text x="35" y="170" class="text-dim">Відстань до Home D</text>
  <text x="35" y="185" class="text-dim">Перепад висоти Δh</text>

  <rect x="25" y="215" width="165" height="65" class="node" />
  <text x="35" y="238" class="title">Батарея та Sag</text>
  <text x="35" y="255" class="text-dim">Напруга U_cell, I_load</text>
  <text x="35" y="270" class="text-dim">R_int(T), E_batt_usable</text>

  <!-- Central Estimator Block -->
  <rect x="230" y="105" width="180" height="120" class="node" style="stroke: #58a6ff; stroke-width: 2px;" />
  <text x="245" y="130" class="title" fill="#58a6ff">Return Budget</text>
  <text x="245" y="148" class="title" fill="#58a6ff">Estimator (1-10 Hz)</text>
  <text x="245" y="170" class="text-dim">• V_ground_ret(θ)</text>
  <text x="245" y="187" class="text-dim">• E_return = E_cr+E_cl+E_res</text>
  <text x="245" y="204" class="text-dim">• Низькочастотний фільтр</text>

  <!-- Arrows from Inputs to Estimator -->
  <path d="M 190 77 L 210 77 L 210 135 L 230 135" class="edge" marker-end="url(#arr)" />
  <path d="M 190 162 L 230 162" class="edge" marker-end="url(#arr)" />
  <path d="M 190 247 L 210 247 L 210 185 L 230 185" class="edge" marker-end="url(#arr)" />

  <!-- Decision State Machine (Right side) -->
  <!-- State 1: NORMAL MISSION -->
  <rect x="450" y="35" width="380" height="60" class="node-ok" />
  <text x="465" y="58" class="title" fill="#3fb950">1. Стан: MISSION_NORMAL</text>
  <text x="465" y="75" class="text-dim">E_batt &gt; E_return + E_margin (Запас достатній)</text>
  <text x="465" y="88" class="text-dim">Виконання завдання в штатному режимі</text>

  <!-- State 2: CAUTION -->
  <rect x="450" y="115" width="380" height="60" class="node-warn" />
  <text x="465" y="138" class="title" fill="#d29922">2. Стан: CAUTION_WIND_DEGRADED</text>
  <text x="465" y="155" class="text-dim">E_batt наближається до PNR (попередження на GCS)</text>
  <text x="465" y="168" class="text-dim">Заборона віддалення, скорочення маршруту</text>

  <!-- State 3: RTL TRIGGERED -->
  <rect x="450" y="195" width="380" height="60" class="node-crit" />
  <text x="465" y="218" class="title" fill="#f85149">3. Стан: RTL_MANDATORY (Point of No Return)</text>
  <text x="465" y="235" class="text-dim">E_batt &lt;= E_return (Примусове повернення на базу)</text>
  <text x="465" y="248" class="text-dim">Набір висоти RTL, розворот проти вітру</text>

  <!-- State 4: EMERGENCY LAND -->
  <rect x="450" y="280" width="380" height="60" class="node-land" />
  <text x="465" y="303" class="title" fill="#bc8cff">4. Стан: EMERGENCY_LAND_NOW</text>
  <text x="465" y="320" class="text-dim">U_cell &lt; V_cutoff або V_ground &lt;= 0 (Дім недосяжний)</text>
  <text x="465" y="333" class="text-dim">Аварійна посадка на запасний майданчик або в поле</text>

  <!-- Transitions between FSM states - routed cleanly around boxes -->
  <path d="M 410 165 L 430 165 L 430 65 L 450 65" class="edge" marker-end="url(#arr)" />
  <path d="M 410 165 L 450 145" class="edge-amber" marker-end="url(#arr-amber)" />
  <path d="M 410 165 L 430 165 L 430 225 L 450 225" class="edge-red" marker-end="url(#arr-red)" />
  <path d="M 640 255 L 640 280" class="edge-red" marker-end="url(#arr-red)" />
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    ensure_dir(img_dir)
    create_wind_asymmetry_svg(os.path.join(img_dir, 'wind-asymmetry-vector.svg'))
    create_pnr_trajectory_svg(os.path.join(img_dir, 'pnr-energy-trajectory.svg'))
    create_voltage_sag_svg(os.path.join(img_dir, 'voltage-sag-curve.svg'))
    create_rtl_budget_fsm_svg(os.path.join(img_dir, 'rtl-budget-fsm.svg'))
    print("Figures generated successfully.")

if __name__ == '__main__':
    main()
