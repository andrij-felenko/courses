import os

def create_svg_active_passive(filepath):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 420" width="100%" height="100%">
  <style>
    .bg { fill: #fcfcfc; }
    .box-bg { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1.5; rx: 6px; }
    .box-active { fill: #eff6ff; stroke: #3b82f6; stroke-width: 1.5; rx: 6px; }
    .box-passive { fill: #f0fdf4; stroke: #22c55e; stroke-width: 1.5; rx: 6px; }
    .title { font-family: system-ui, sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
    .node-title { font-family: system-ui, sans-serif; font-size: 13px; font-weight: bold; fill: #1e293b; text-anchor: middle; }
    .label { font-family: system-ui, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; }
    .wire-pos { stroke: #dc2626; stroke-width: 2.5; fill: none; }
    .wire-neg { stroke: #2563eb; stroke-width: 2.5; fill: none; }
    .comp-box { fill: #fef08a; stroke: none; rx: 3px; }
    .comp-text { font-family: system-ui, sans-serif; font-size: 11px; font-weight: bold; fill: #854d0e; text-anchor: middle; }
    .opto-box { fill: #fed7aa; stroke: none; rx: 4px; }
    .opto-text { font-family: system-ui, sans-serif; font-size: 11px; font-weight: bold; fill: #9a3412; text-anchor: middle; }
  </style>
  <rect width="100%" height="100%" class="bg"/>
  <text x="700" y="28" class="title">Топологія цифрової струмової петлі 20 мА: Активний та Пасивний вузли</text>

  <!-- Active Transmitter Node -->
  <rect x="40" y="55" width="400" height="310" class="box-active"/>
  <text x="240" y="80" class="node-title" style="fill:#1d4ed8;">Активний передавач (Active TX)</text>
  <text x="240" y="100" class="label">Джерело живлення VCC та генератор струму</text>

  <!-- Power Source inside Active Node -->
  <line x1="60" y1="140" x2="130" y2="140" stroke="#dc2626" stroke-width="2"/>
  <text x="95" y="122" class="label" style="font-weight:bold; fill:#dc2626;">+24 В (VCC)</text>
  
  <!-- Current Source Box -->
  <rect x="130" y="115" width="180" height="50" class="comp-box"/>
  <text x="220" y="144" class="comp-text">Джерело 20 мА</text>

  <!-- Switch Transistor inside Active Node -->
  <rect x="110" y="180" width="220" height="80" class="box-bg"/>
  <text x="220" y="210" class="node-title" style="font-size:11px;">Ключ TX (NPN)</text>
  <text x="220" y="232" class="label" style="font-size:10px;">UART TX (Mark/Space)</text>

  <line x1="310" y1="140" x2="340" y2="140" stroke="#dc2626" stroke-width="2"/>
  <line x1="340" y1="140" x2="340" y2="180" stroke="#dc2626" stroke-width="2"/>
  <line x1="340" y1="260" x2="340" y2="300" stroke="#dc2626" stroke-width="2"/>
  <line x1="340" y1="300" x2="440" y2="300" class="wire-pos"/>

  <!-- Output terminals Active -->
  <circle cx="440" cy="140" r="4" fill="#dc2626"/>
  <text x="415" y="122" class="label" style="font-weight:bold; fill:#dc2626;">+LOOP</text>

  <circle cx="440" cy="300" r="4" fill="#2563eb"/>
  <text x="415" y="328" class="label" style="font-weight:bold; fill:#2563eb;">-LOOP</text>
  <line x1="310" y1="140" x2="440" y2="140" class="wire-pos"/>

  <!-- Long Cable -->
  <line x1="440" y1="140" x2="920" y2="140" class="wire-pos"/>
  <line x1="440" y1="300" x2="920" y2="300" class="wire-neg"/>

  <text x="680" y="118" class="label" style="fill:#dc2626; font-weight:bold;">Кабель: струм I = 20 мА (Mark) або 0 мА (Space)</text>
  <text x="680" y="328" class="label" style="fill:#2563eb; font-weight:bold;">Зворотна жила струмової петлі (замкнений контур)</text>

  <!-- Passive Receiver Node -->
  <rect x="920" y="55" width="440" height="310" class="box-passive"/>
  <text x="1140" y="80" class="node-title" style="fill:#15803d;">Пасивний приймач (Passive RX)</text>
  <text x="1140" y="100" class="label">Без власного живлення (опторозв'язка)</text>

  <!-- Optocoupler inside Passive Node -->
  <rect x="960" y="170" width="340" height="100" class="opto-box"/>
  <text x="1130" y="205" class="opto-text">Оптопара (6N137 / PC817)</text>
  <text x="1130" y="232" class="label" style="fill:#7c2d12;">Світлодіод увімкнено в петлю</text>

  <!-- Input terminals Passive -->
  <circle cx="920" cy="140" r="4" fill="#dc2626"/>
  <circle cx="920" cy="300" r="4" fill="#2563eb"/>

  <line x1="920" y1="140" x2="990" y2="140" class="wire-pos"/>
  <line x1="990" y1="140" x2="990" y2="170" class="wire-pos"/>

  <!-- Protection Diode & LED in Optocoupler -->
  <line x1="990" y1="270" x2="990" y2="300" class="wire-neg"/>
  <line x1="990" y1="300" x2="920" y2="300" class="wire-neg"/>

  <!-- Local Isolated Output -->
  <line x1="1300" y1="220" x2="1330" y2="220" stroke="#1e293b" stroke-width="2"/>
  <text x="1315" y="245" class="label" style="font-weight:bold;">UART RX</text>

  <!-- Ground Potential difference notice (text without rect border) -->
  <text x="680" y="205" class="label" style="font-weight:bold; fill:#c2410c;">Різниця потенціалів земель ΔV_GND</text>
  <text x="680" y="225" class="label" style="font-size:10px;">Оптопара повністю ізолює GND1 від GND2</text>
  <text x="680" y="243" class="label" style="font-size:10px;">Гальванічна міцність: 2500…5000 В</text>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_svg_midi_circuit(filepath):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 380" width="100%" height="100%">
  <style>
    .bg { fill: #fcfcfc; }
    .box-bg { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1.5; rx: 6px; }
    .title { font-family: system-ui, sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
    .node-title { font-family: system-ui, sans-serif; font-size: 12px; font-weight: bold; fill: #1e293b; text-anchor: middle; }
    .label { font-family: system-ui, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; }
    .resistor { fill: #fef08a; stroke: #ca8a04; stroke-width: 1.5; rx: 3px; }
    .res-text { font-family: system-ui, sans-serif; font-size: 11px; font-weight: bold; fill: #854d0e; text-anchor: middle; }
    .wire { stroke: #2563eb; stroke-width: 2; fill: none; }
    .wire-red { stroke: #dc2626; stroke-width: 2; fill: none; }
    .opto-box { fill: #fed7aa; stroke: none; rx: 4px; }
  </style>
  <rect width="100%" height="100%" class="bg"/>
  <text x="620" y="28" class="title">Електрична схема стандарту MIDI (5 мА струмова петля з опторозв'язкою)</text>

  <!-- MIDI OUT Section -->
  <rect x="40" y="50" width="300" height="300" class="box-bg"/>
  <text x="190" y="75" class="node-title">Пристрій MIDI OUT (Передавач)</text>

  <!-- VCC + 220 Ohm -->
  <text x="90" y="105" class="label" style="font-weight:bold; fill:#dc2626;">+5V VCC</text>
  <line x1="90" y1="110" x2="90" y2="125" stroke="#dc2626" stroke-width="2"/>
  <rect x="60" y="125" width="60" height="30" class="resistor"/>
  <text x="90" y="144" class="res-text">220 Ω</text>
  <line x1="90" y1="155" x2="90" y2="175" stroke="#dc2626" stroke-width="2"/>
  <line x1="90" y1="175" x2="300" y2="175" class="wire-red"/>
  <text x="300" y="160" class="label" style="font-size:10px;">Pin 4 DIN-5</text>

  <!-- Inverter / Buffer + 220 Ohm -->
  <text x="80" y="250" class="label" style="font-weight:bold;">UART TXD</text>
  <line x1="110" y1="245" x2="130" y2="245" stroke="#1e293b" stroke-width="2"/>
  <!-- Buffer symbol -->
  <polygon points="130,230 130,260 160,245" fill="#e2e8f0" stroke="#475569" stroke-width="1.5"/>
  <line x1="160" y1="245" x2="180" y2="245" stroke="#1e293b" stroke-width="2"/>
  <rect x="180" y="230" width="60" height="30" class="resistor"/>
  <text x="210" y="249" class="res-text">220 Ω</text>
  <line x1="240" y1="245" x2="300" y2="245" class="wire"/>
  <text x="300" y="265" class="label" style="font-size:10px;">Pin 5 DIN-5</text>

  <!-- Ground on Pin 2 -->
  <text x="300" y="295" class="label" style="font-size:10px; fill:#64748b;">Pin 2 (Shield GND)</text>

  <!-- Cable section -->
  <rect x="380" y="135" width="300" height="150" fill="#f1f5f9" stroke="#94a3b8" stroke-dasharray="4,4" rx="4"/>
  <text x="530" y="155" class="label" style="font-weight:bold;">Екранована вита пара MIDI</text>
  <line x1="340" y1="175" x2="720" y2="175" class="wire-red"/>
  <line x1="340" y1="245" x2="720" y2="245" class="wire"/>
  <text x="530" y="210" class="label" style="fill:#dc2626; font-size:10px;">Струм I = 5 мА (при TXD = 0)</text>
  <text x="530" y="270" class="label" style="fill:#64748b; font-size:10px;">Shield підключено ЛИШЕ на MIDI OUT</text>

  <!-- MIDI IN Section -->
  <rect x="760" y="50" width="380" height="300" class="box-bg"/>
  <text x="950" y="75" class="node-title">Пристрій MIDI IN (Приймач)</text>

  <!-- Optocoupler 6N138 -->
  <rect x="850" y="155" width="240" height="120" class="opto-box"/>
  <text x="970" y="185" class="label" style="font-weight:bold; fill:#9a3412;">Оптопара (6N138)</text>

  <line x1="720" y1="175" x2="870" y2="175" class="wire-red"/>
  <line x1="870" y1="175" x2="870" y2="195" class="wire-red"/>

  <line x1="720" y1="245" x2="870" y2="245" class="wire"/>

  <!-- Protection Diode 1N4148 parallel -->
  <line x1="810" y1="175" x2="810" y2="245" stroke="#059669" stroke-width="1.5"/>
  <polygon points="805,215 815,215 810,205" fill="#059669"/>
  <line x1="803" y1="205" x2="817" y2="205" stroke="#059669" stroke-width="1.5"/>
  <text x="760" y="214" class="label" style="font-size:9px; fill:#059669; text-anchor:end;">1N4148</text>

  <!-- Opto output -->
  <line x1="1090" y1="215" x2="1120" y2="215" stroke="#1e293b" stroke-width="2"/>
  <text x="1105" y="198" class="label" style="font-weight:bold; fill:#1e293b;">UART RXD</text>
  <text x="950" y="325" class="label" style="fill:#059669; font-weight:bold;">Земля MIDI IN повністю від'єднана!</text>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)

def create_svg_hart_overlay(filepath):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1340 390" width="100%" height="100%">
  <style>
    .bg { fill: #fcfcfc; }
    .box-bg { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 1.5; rx: 6px; }
    .title { font-family: system-ui, sans-serif; font-size: 14px; font-weight: bold; fill: #0f172a; text-anchor: middle; }
    .label { font-family: system-ui, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; }
    .axis { stroke: #64748b; stroke-width: 1.5; }
    .dc-line { stroke: #2563eb; stroke-width: 2.5; stroke-dasharray: 6,4; fill: none; }
    .hart-wave { stroke: #dc2626; stroke-width: 2; fill: none; }
    .val-text { font-family: system-ui, sans-serif; font-size: 11px; font-weight: bold; fill: #0f172a; text-anchor: end; }
  </style>
  <rect width="100%" height="100%" class="bg"/>
  <text x="670" y="28" class="title">Протокол HART: Накладання цифрового сигналу Bell 202 FSK поверх аналогового струму 4–20 мА</text>

  <!-- Graph Container -->
  <rect x="40" y="50" width="1260" height="300" class="box-bg"/>

  <!-- Axes -->
  <line x1="180" y1="90" x2="180" y2="310" class="axis"/>
  <line x1="180" y1="200" x2="1240" y2="200" class="axis"/>

  <text x="110" y="90" class="label" style="font-weight:bold;">Струм (мА)</text>
  <text x="1230" y="225" class="label" style="font-weight:bold;">Час (t)</text>

  <text x="120" y="130" class="val-text" style="fill:#2563eb;">12.5 мА</text>
  <text x="120" y="204" class="val-text" style="fill:#2563eb;">12.0 мА (DC)</text>
  <text x="120" y="270" class="val-text" style="fill:#2563eb;">11.5 мА</text>

  <!-- DC Current Line -->
  <line x1="180" y1="200" x2="1240" y2="200" class="dc-line"/>

  <!-- Combined HART Signal (Sinusoids of 1200 Hz and 2200 Hz over DC) -->
  <path d="M 180,200 
           C 200,130 220,130 240,200 C 260,270 280,270 300,200 
           C 320,130 340,130 360,200 C 380,270 400,270 420,200 
           C 430,150 440,150 450,200 C 460,250 470,250 480,200 
           C 490,150 500,150 510,200 C 520,250 530,250 540,200 
           C 550,150 560,150 570,200 C 580,250 590,250 600,200 
           C 620,130 640,130 660,200 C 680,270 700,270 720,200 
           C 740,130 760,130 780,200 C 800,270 820,270 840,200
           C 850,150 860,150 870,200 C 880,250 890,250 900,200 H 1220" class="hart-wave"/>

  <!-- Annotations (no background rects to avoid box contour intersection) -->
  <text x="320" y="80" class="label" style="font-weight:bold; fill:#1d4ed8;">1200 Гц = Логічна «1» (Mark)</text>
  <text x="320" y="96" class="label" style="font-size:10px; fill:#1e40af;">Низька частота FSK</text>

  <text x="550" y="80" class="label" style="font-weight:bold; fill:#b91c1c;">2200 Гц = Логічний «0» (Space)</text>
  <text x="550" y="96" class="label" style="font-size:10px; fill:#991b1b;">Висока частота FSK</text>

  <text x="780" y="80" class="label" style="font-weight:bold; fill:#1d4ed8;">1200 Гц = Логічна «1» (Mark)</text>
  <text x="780" y="96" class="label" style="font-size:10px; fill:#1e40af;">Низька частота FSK</text>

  <!-- Amplitude indicator with text anchored at x=1140 (well away from x=1200) -->
  <line x1="1200" y1="130" x2="1200" y2="270" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="1140" y="165" class="label" style="fill:#dc2626; font-weight:bold; text-anchor:end;">+0.5 мА</text>
  <text x="1140" y="240" class="label" style="fill:#dc2626; font-weight:bold; text-anchor:end;">−0.5 мА</text>

  <text x="670" y="335" class="label" style="font-weight:bold; fill:#059669;">Середнє значення синусоїди = 0 мА. Аналогове значення 12.0 мА не змінюється!</text>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)

def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(out_dir, exist_ok=True)
    create_svg_active_passive(os.path.join(out_dir, 'current-loop-active-passive.svg'))
    create_svg_midi_circuit(os.path.join(out_dir, 'midi-circuit.svg'))
    create_svg_hart_overlay(os.path.join(out_dir, 'hart-fsk-overlay.svg'))
    print("Generated SVGs in", out_dir)

if __name__ == '__main__':
    main()
