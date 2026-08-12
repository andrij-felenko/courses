import os

def render():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" width="100%" height="100%">
  <rect width="800" height="420" fill="#f8f9fa" rx="8"/>
  <text x="400" y="40" font-family="'Segoe UI', Arial, sans-serif" font-size="20" font-weight="bold" text-anchor="middle" fill="#1a1a1a">Обробка переривань: Ванільне ядро vs PREEMPT_RT</text>

  <!-- Panel 1: Standard Linux -->
  <rect x="40" y="70" width="340" height="320" fill="#ffffff" stroke="#ced4da" stroke-width="1.5" rx="6"/>
  <text x="210" y="100" font-family="'Segoe UI', Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#495057">Стандартний Linux (Mainline)</text>
  
  <rect x="60" y="120" width="300" height="55" fill="#f8d7da" stroke="#f5c6cb" stroke-width="1.5" rx="4"/>
  <text x="210" y="143" font-family="'Segoe UI', Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#721c24">Hard IRQ (Апаратний контекст)</text>
  <text x="210" y="162" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#721c24">Вимикає переривання/витіснення</text>

  <rect x="60" y="195" width="300" height="55" fill="#fff3cd" stroke="#ffebaba" stroke-width="1.5" rx="4"/>
  <text x="210" y="218" font-family="'Segoe UI', Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#856404">SoftIRQ / Tasklet (Нижня половина)</text>
  <text x="210" y="237" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#856404">Перешкоджає RT-завданням користувача</text>

  <rect x="60" y="270" width="300" height="55" fill="#d1ecf1" stroke="#bee5eb" stroke-width="1.5" rx="4"/>
  <text x="210" y="293" font-family="'Segoe UI', Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#0c5460">RT-завдання користувача (SCHED_FIFO)</text>
  <text x="210" y="312" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#0c5460">Змушене чекати завершення IRQ/SoftIRQ</text>

  <!-- Panel 2: PREEMPT_RT -->
  <rect x="420" y="70" width="340" height="320" fill="#ffffff" stroke="#ced4da" stroke-width="1.5" rx="6"/>
  <text x="590" y="100" font-family="'Segoe UI', Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#495057">Ядро з PREEMPT_RT</text>

  <rect x="440" y="120" width="300" height="45" fill="#f8d7da" stroke="#f5c6cb" stroke-width="1.5" rx="4"/>
  <text x="590" y="140" font-family="'Segoe UI', Arial, sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#721c24">Micro-ISR (Лише ACK і розбудження)</text>
  <text x="590" y="156" font-family="'Segoe UI', Arial, sans-serif" font-size="11" text-anchor="middle" fill="#721c24">Тривалість &lt; 1–2 мікросекунди</text>

  <rect x="440" y="185" width="300" height="55" fill="#d4edda" stroke="#c3e6cb" stroke-width="1.5" rx="4"/>
  <text x="590" y="208" font-family="'Segoe UI', Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#155724">RT-завдання користувача (Пріоритет 80)</text>
  <text x="590" y="227" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#155724">Витісняє потік переривань без затримок</text>

  <rect x="440" y="260" width="300" height="55" fill="#cce5ff" stroke="#b8daff" stroke-width="1.5" rx="4"/>
  <text x="590" y="283" font-family="'Segoe UI', Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#004085">Потік ядра irq/N-name (Пріоритет 50)</text>
  <text x="590" y="302" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#004085">Повноцінний потік (витіснюваний, може спати)</text>

  <path d="M 590 165 L 590 185" stroke="#28a745" stroke-width="2" marker-end="url(#arrow)"/>
</svg>"""

    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 440" width="100%" height="100%">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#495057"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc3545"/>
    </marker>
  </defs>

  <rect width="800" height="440" fill="#ffffff" rx="8"/>
  <text x="400" y="35" font-family="'Segoe UI', Arial, sans-serif" font-size="20" font-weight="bold" text-anchor="middle" fill="#1a1a1a">Механізм успадкування пріоритетів (Priority Inheritance)</text>

  <!-- Tasks Nodes -->
  <g transform="translate(80, 80)">
    <rect x="0" y="0" width="180" height="70" fill="#f8d7da" stroke="#dc3545" stroke-width="2" rx="6"/>
    <text x="90" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="15" font-weight="bold" text-anchor="middle" fill="#721c24">Task H (Високий)</text>
    <text x="90" y="52" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#721c24">SCHED_FIFO Prio 90</text>
  </g>

  <g transform="translate(310, 80)">
    <rect x="0" y="0" width="180" height="70" fill="#fff3cd" stroke="#ffc107" stroke-width="2" rx="6"/>
    <text x="90" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="15" font-weight="bold" text-anchor="middle" fill="#856404">Task M (Середній)</text>
    <text x="90" y="52" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#856404">SCHED_FIFO Prio 50</text>
  </g>

  <g transform="translate(540, 80)">
    <rect x="0" y="0" width="180" height="70" fill="#d4edda" stroke="#28a745" stroke-width="2" rx="6"/>
    <text x="90" y="30" font-family="'Segoe UI', Arial, sans-serif" font-size="15" font-weight="bold" text-anchor="middle" fill="#155724">Task L (Низький)</text>
    <text x="90" y="52" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#155724">Базовий Prio 10</text>
  </g>

  <!-- Lock Node -->
  <g transform="translate(310, 240)">
    <rect x="0" y="0" width="180" height="60" fill="#e2e3e5" stroke="#6c757d" stroke-width="2" rx="6"/>
    <text x="90" y="28" font-family="'Segoe UI', Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#383d41">rt_mutex</text>
    <text x="90" y="46" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#383d41">Захоплений Task L</text>
  </g>

  <!-- Arrows and Relationships -->
  <path d="M 170 150 L 170 270 L 310 270" fill="none" stroke="#dc3545" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow-red)"/>
  <text x="240" y="255" font-family="'Segoe UI', Arial, sans-serif" font-size="12" font-weight="bold" fill="#dc3545" text-anchor="middle">1. Чекає на лок</text>

  <path d="M 630 150 L 630 270 L 490 270" fill="none" stroke="#28a745" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="560" y="255" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#155724" text-anchor="middle">Володіє локом</text>

  <!-- Inheritance Banner -->
  <rect x="180" y="340" width="440" height="70" fill="#cce5ff" stroke="#004085" stroke-width="1.5" rx="6"/>
  <text x="400" y="368" font-family="'Segoe UI', Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#004085">2. Динамічне підняття пріоритету Task L до Prio 90</text>
  <text x="400" y="390" font-family="'Segoe UI', Arial, sans-serif" font-size="12" text-anchor="middle" fill="#004085">Task M не може витіснити Task L; Task L швидко виходить з секції</text>
</svg>"""

    with open(os.path.join(img_dir, 'fig-irq.svg'), 'w', encoding='utf-8') as f:
        f.write(svg1)
    with open(os.path.join(img_dir, 'fig-pi.svg'), 'w', encoding='utf-8') as f:
        f.write(svg2)

if __name__ == '__main__':
    render()
