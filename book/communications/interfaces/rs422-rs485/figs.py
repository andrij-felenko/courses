import os

def create_svg_rs422_vs_rs485(filepath):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" width="100%" height="100%">
  <style>
    .bg { fill: #fcfcfc; }
    .box-bg { fill: #f0f4f8; stroke: #cbd5e1; stroke-width: 1.5; rx: 6px; }
    .node-title { font-family: system-ui, sans-serif; font-size: 13px; font-weight: bold; fill: #1e293b; text-anchor: middle; }
    .label { font-family: system-ui, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; }
    .wire-tx { stroke: #2563eb; stroke-width: 2; fill: none; }
    .wire-bus { stroke: #059669; stroke-width: 2.5; fill: none; }
    .term { fill: #ef4444; stroke: #991b1b; stroke-width: 1.5; rx: 3px; }
    .term-text { font-family: system-ui, sans-serif; font-size: 11px; font-weight: bold; fill: #ffffff; text-anchor: middle; }
    .section-header { font-family: system-ui, sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
  </style>
  <rect width="100%" height="100%" class="bg"/>

  <!-- RS-422 Section -->
  <text x="480" y="28" class="section-header">RS-422: 4-провідний дуплекс (один передавач, кілька приймачів)</text>
  
  <!-- Master Driver -->
  <rect x="30" y="55" width="150" height="95" class="box-bg"/>
  <text x="105" y="78" class="node-title">Ведучий (TX)</text>
  <text x="105" y="118" class="label">Драйвер D</text>
  <text x="105" y="136" class="label">(активний)</text>

  <!-- Lines -->
  <line x1="185" y1="68" x2="825" y2="68" class="wire-tx"/>
  <line x1="185" y1="138" x2="825" y2="138" class="wire-tx"/>
  <text x="280" y="52" class="label" style="fill:#2563eb; font-weight:bold;">TX+ (лінія Y)</text>
  <text x="280" y="156" class="label" style="fill:#2563eb; font-weight:bold;">TX- (лінія Z)</text>

  <!-- Receiver 1 -->
  <rect x="410" y="78" width="130" height="50" class="box-bg"/>
  <text x="475" y="98" class="node-title">Приймач 1</text>
  <text x="475" y="116" class="label">R (RxD)</text>
  <line x1="475" y1="68" x2="475" y2="78" stroke="#2563eb" stroke-width="1.5"/>
  <line x1="475" y1="128" x2="475" y2="138" stroke="#2563eb" stroke-width="1.5"/>

  <!-- Receiver 2 -->
  <rect x="650" y="78" width="130" height="50" class="box-bg"/>
  <text x="715" y="98" class="node-title">Приймач 2</text>
  <text x="715" y="116" class="label">R (RxD)</text>
  <line x1="715" y1="68" x2="715" y2="78" stroke="#2563eb" stroke-width="1.5"/>
  <line x1="715" y1="128" x2="715" y2="138" stroke="#2563eb" stroke-width="1.5"/>

  <!-- Terminator RS-422 -->
  <rect x="830" y="92" width="55" height="22" class="term"/>
  <text x="857" y="107" class="term-text">120 Ω</text>
  <line x1="825" y1="68" x2="857" y2="68" stroke="#2563eb" stroke-width="1.5"/>
  <line x1="857" y1="68" x2="857" y2="92" stroke="#2563eb" stroke-width="1.5"/>
  <line x1="825" y1="138" x2="857" y2="138" stroke="#2563eb" stroke-width="1.5"/>
  <line x1="857" y1="138" x2="857" y2="114" stroke="#2563eb" stroke-width="1.5"/>

  <line x1="20" y1="170" x2="940" y2="170" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="6,4"/>

  <!-- RS-485 Section -->
  <text x="480" y="200" class="section-header">RS-485: 2-провідний напівдуплекс (мультиточкова шина, керування DE)</text>

  <!-- Bus Lines -->
  <line x1="85" y1="265" x2="855" y2="265" class="wire-bus"/>
  <line x1="85" y1="295" x2="855" y2="295" class="wire-bus"/>
  <text x="330" y="250" class="label" style="fill:#059669; font-weight:bold;">Лінія A (Non-inverting)</text>
  <text x="330" y="312" class="label" style="fill:#059669; font-weight:bold;">Лінія B (Inverting)</text>

  <!-- Left Terminator RS-485 -->
  <rect x="25" y="269" width="55" height="22" class="term"/>
  <text x="52" y="284" class="term-text">120 Ω</text>
  <line x1="85" y1="265" x2="85" y2="269" class="wire-bus"/>
  <line x1="85" y1="295" x2="85" y2="291" class="wire-bus"/>

  <!-- Right Terminator RS-485 -->
  <rect x="855" y="269" width="55" height="22" class="term"/>
  <text x="882" y="284" class="term-text">120 Ω</text>
  <line x1="855" y1="265" x2="855" y2="269" class="wire-bus"/>
  <line x1="855" y1="295" x2="855" y2="291" class="wire-bus"/>

  <!-- Node 1 -->
  <rect x="110" y="350" width="170" height="95" class="box-bg"/>
  <text x="195" y="375" class="node-title">Вузол 1</text>
  <text x="195" y="398" class="label">Трансивер D/R</text>
  <text x="195" y="418" class="label" style="fill:#dc2626; font-size:10px;">Сигнал DE/RE</text>
  <line x1="160" y1="265" x2="160" y2="350" stroke="#059669" stroke-width="1.5"/>
  <line x1="230" y1="295" x2="230" y2="350" stroke="#059669" stroke-width="1.5"/>

  <!-- Node 2 -->
  <rect x="385" y="350" width="170" height="95" class="box-bg"/>
  <text x="470" y="375" class="node-title">Вузол 2</text>
  <text x="470" y="398" class="label">Трансивер D/R</text>
  <text x="470" y="418" class="label" style="fill:#dc2626; font-size:10px;">Сигнал DE/RE</text>
  <line x1="435" y1="265" x2="435" y2="350" stroke="#059669" stroke-width="1.5"/>
  <line x1="505" y1="295" x2="505" y2="350" stroke="#059669" stroke-width="1.5"/>

  <!-- Node 3 -->
  <rect x="660" y="350" width="170" height="95" class="box-bg"/>
  <text x="745" y="375" class="node-title">Вузол N</text>
  <text x="745" y="398" class="label">Трансивер D/R</text>
  <text x="745" y="418" class="label" style="fill:#dc2626; font-size:10px;">Сигнал DE/RE</text>
  <line x1="710" y1="265" x2="710" y2="350" stroke="#059669" stroke-width="1.5"/>
  <line x1="780" y1="295" x2="780" y2="350" stroke="#059669" stroke-width="1.5"/>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_svg_failsafe_biasing(filepath):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" width="100%" height="100%">
  <style>
    .bg { fill: #fcfcfc; }
    .box-bg { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1.5; rx: 6px; }
    .title { font-family: system-ui, sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
    .node-title { font-family: system-ui, sans-serif; font-size: 12px; font-weight: bold; fill: #1e293b; text-anchor: middle; }
    .label { font-family: system-ui, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; }
    .wire-a { stroke: #2563eb; stroke-width: 2.5; fill: none; }
    .wire-b { stroke: #dc2626; stroke-width: 2.5; fill: none; }
    .resistor { fill: #fef08a; stroke: #ca8a04; stroke-width: 1.5; rx: 3px; }
    .res-text { font-family: system-ui, sans-serif; font-size: 11px; font-weight: bold; fill: #854d0e; text-anchor: middle; }
    .vcc-gnd { font-family: system-ui, sans-serif; font-size: 11px; font-weight: bold; fill: #1e293b; text-anchor: middle; }
  </style>
  <rect width="100%" height="100%" class="bg"/>
  <text x="480" y="28" class="title">Схема захисного зсуву (Fail-Safe Biasing) та термінування RS-485</text>

  <!-- VCC Top -->
  <line x1="250" y1="42" x2="250" y2="55" stroke="#1e293b" stroke-width="2"/>
  <text x="250" y="38" class="vcc-gnd">VCC (+5V / +3.3V)</text>
  <rect x="200" y="60" width="100" height="32" class="resistor"/>
  <text x="250" y="80" class="res-text">R_pull-up</text>
  <line x1="250" y1="95" x2="250" y2="130" stroke="#2563eb" stroke-width="2"/>

  <!-- Line A -->
  <line x1="60" y1="130" x2="640" y2="130" class="wire-a"/>
  <text x="130" y="98" class="label" style="fill:#2563eb; font-weight:bold;">Лінія A (Non-Inverting)</text>

  <!-- Line B -->
  <line x1="60" y1="240" x2="640" y2="240" class="wire-b"/>
  <text x="130" y="268" class="label" style="fill:#dc2626; font-weight:bold;">Лінія B (Inverting)</text>

  <!-- Termination Resistor -->
  <line x1="470" y1="130" x2="470" y2="165" stroke="#1e293b" stroke-width="1.5"/>
  <rect x="420" y="170" width="100" height="32" class="resistor" style="fill:#fca5a5; stroke:#b91c1c;"/>
  <text x="470" y="190" class="res-text" style="fill:#7f1d1d;">R_T 120 Ω</text>
  <line x1="470" y1="205" x2="470" y2="240" stroke="#1e293b" stroke-width="1.5"/>

  <!-- GND Bottom -->
  <line x1="250" y1="240" x2="250" y2="270" stroke="#dc2626" stroke-width="2"/>
  <rect x="200" y="275" width="100" height="32" class="resistor"/>
  <text x="250" y="295" class="res-text">R_pull-dn</text>
  <line x1="250" y1="310" x2="250" y2="330" stroke="#1e293b" stroke-width="2"/>
  <!-- GND Symbol -->
  <line x1="230" y1="330" x2="270" y2="330" stroke="#1e293b" stroke-width="2"/>
  <line x1="238" y1="336" x2="262" y2="336" stroke="#1e293b" stroke-width="2"/>
  <line x1="245" y1="342" x2="255" y2="342" stroke="#1e293b" stroke-width="2"/>
  <text x="250" y="360" class="vcc-gnd">GND</text>

  <!-- Receiver Comparator Box -->
  <rect x="640" y="110" width="260" height="150" class="box-bg"/>
  <text x="770" y="135" class="node-title">Приймач RS-485</text>

  <!-- Comparator Triangle inside box -->
  <polygon points="680,150 680,210 740,180" fill="#e2e8f0" stroke="#475569" stroke-width="1.5"/>
  <text x="688" y="167" class="label" style="font-size:13px; font-weight:bold;">+</text>
  <text x="688" y="202" class="label" style="font-size:13px; font-weight:bold;">−</text>
  <line x1="640" y1="130" x2="660" y2="130" stroke="#2563eb" stroke-width="2"/>
  <line x1="660" y1="130" x2="660" y2="165" stroke="#2563eb" stroke-width="1.5"/>
  <line x1="660" y1="165" x2="680" y2="165" stroke="#2563eb" stroke-width="1.5"/>

  <line x1="640" y1="240" x2="660" y2="240" stroke="#dc2626" stroke-width="2"/>
  <line x1="660" y1="240" x2="660" y2="195" stroke="#dc2626" stroke-width="1.5"/>
  <line x1="660" y1="195" x2="680" y2="195" stroke="#dc2626" stroke-width="1.5"/>

  <line x1="740" y1="180" x2="800" y2="180" stroke="#1e293b" stroke-width="2"/>
  <text x="840" y="184" class="label" style="font-weight:bold;">RO (RxD)</text>
  <text x="770" y="238" class="label" style="fill:#059669; font-size:11px; font-weight:bold;">V_AB &gt; +200 мВ → «1»</text>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_svg_common_mode(filepath):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" width="100%" height="100%">
  <style>
    .bg { fill: #fcfcfc; }
    .title { font-family: system-ui, sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
    .box-bg { fill: #f1f5f9; stroke: #cbd5e1; stroke-width: 1.5; rx: 6px; }
    .label-hdr { font-family: system-ui, sans-serif; font-size: 13px; font-weight: bold; fill: #1e293b; text-anchor: middle; }
    .label { font-family: system-ui, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; }
    .axis { stroke: #64748b; stroke-width: 1.5; }
    .range-rs422 { fill: #dbeafe; stroke: #3b82f6; stroke-width: 2; rx: 4px; }
    .range-rs485 { fill: #dcfce7; stroke: #16a34a; stroke-width: 2; rx: 4px; }
    .val-text { font-family: system-ui, sans-serif; font-size: 12px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
  </style>
  <rect width="100%" height="100%" class="bg"/>
  <text x="480" y="28" class="title">Діапазон синфазної напруги (Common-Mode Voltage V_cm) та зсув земель</text>

  <!-- Diagram Left: RS-422 Voltage Range -->
  <rect x="50" y="55" width="400" height="290" class="box-bg"/>
  <text x="250" y="80" class="label-hdr">RS-422: Синфазне вікно</text>

  <!-- Voltage Axis -->
  <line x1="120" y1="100" x2="120" y2="310" class="axis"/>
  <!-- RS-422 range: -7V to +7V -->
  <rect x="150" y="130" width="270" height="140" class="range-rs422"/>
  <text x="285" y="155" class="val-text" style="fill:#1d4ed8;">+7 В</text>
  <text x="285" y="190" class="label" style="font-weight:bold;">Допустиме V_cm</text>
  <text x="285" y="210" class="label">(відносно GND приймача)</text>
  <text x="285" y="250" class="val-text" style="fill:#1d4ed8;">−7 В</text>

  <!-- Axis ticks -->
  <text x="95" y="134" class="label">+7В</text>
  <line x1="115" y1="130" x2="125" y2="130" stroke="#64748b" stroke-width="1.5"/>
  <text x="98" y="204" class="label">0В</text>
  <line x1="115" y1="200" x2="125" y2="200" stroke="#64748b" stroke-width="1.5"/>
  <text x="95" y="274" class="label">−7В</text>
  <line x1="115" y1="270" x2="125" y2="270" stroke="#64748b" stroke-width="1.5"/>

  <!-- Diagram Right: RS-485 Voltage Range -->
  <rect x="510" y="55" width="400" height="290" class="box-bg"/>
  <text x="710" y="80" class="label-hdr">RS-485: Синфазне вікно</text>

  <!-- Voltage Axis -->
  <line x1="580" y1="100" x2="580" y2="310" class="axis"/>
  <!-- RS-485 range: -7V to +12V -->
  <rect x="610" y="110" width="270" height="180" class="range-rs485"/>
  <text x="745" y="135" class="val-text" style="fill:#15803d;">+12 В</text>
  <text x="745" y="180" class="label" style="font-weight:bold;">Розширене V_cm</text>
  <text x="745" y="200" class="label">(витримує великий зсув ΔV_GND)</text>
  <text x="745" y="275" class="val-text" style="fill:#15803d;">−7 В</text>

  <!-- Axis ticks -->
  <text x="550" y="114" class="label">+12В</text>
  <line x1="575" y1="110" x2="585" y2="110" stroke="#64748b" stroke-width="1.5"/>
  <text x="558" y="204" class="label">0В</text>
  <line x1="575" y1="200" x2="585" y2="200" stroke="#64748b" stroke-width="1.5"/>
  <text x="555" y="294" class="label">−7В</text>
  <line x1="575" y1="290" x2="585" y2="290" stroke="#64748b" stroke-width="1.5"/>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)

def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    create_svg_rs422_vs_rs485(os.path.join(out_dir, 'rs422-vs-rs485-topologies.svg'))
    create_svg_failsafe_biasing(os.path.join(out_dir, 'failsafe-biasing-circuit.svg'))
    create_svg_common_mode(os.path.join(out_dir, 'common-mode-range.svg'))
    print("Generated 3 SVGs in", out_dir)

if __name__ == '__main__':
    main()
