import os
import sys

# Ensure img directory exists
os.makedirs("img", exist_ok=True)

def render_lock_graph():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 380" width="800" height="380">
  <rect width="800" height="380" fill="#f8f9fa" rx="8"/>
  <g font-family="system-ui, -apple-system, sans-serif" font-size="13">

    <!-- Title / Banner -->
    <rect x="20" y="16" width="760" height="36" rx="6" fill="#e9ecef" stroke="#ced4da" stroke-width="1"/>
    <text x="400" y="39" text-anchor="middle" font-weight="bold" fill="#212529" font-size="14">Побудова графа залежностей класів блокувань (Lockdep DAG)</text>

    <!-- Node A -->
    <rect x="60" y="130" width="160" height="75" rx="8" fill="#d1e7dd" stroke="#0f5132" stroke-width="2"/>
    <text x="140" y="158" text-anchor="middle" fill="#0f5132" font-weight="bold" font-size="13">Клас A</text>
    <text x="140" y="176" text-anchor="middle" fill="#0f5132" font-size="11">sb-&gt;s_type-&gt;i_mutex_key</text>
    <text x="140" y="192" text-anchor="middle" fill="#495057" font-size="10">[Взято першим]</text>

    <!-- Node B -->
    <rect x="320" y="130" width="160" height="75" rx="8" fill="#cfe2ff" stroke="#084298" stroke-width="2"/>
    <text x="400" y="158" text-anchor="middle" fill="#084298" font-weight="bold" font-size="13">Клас B</text>
    <text x="400" y="176" text-anchor="middle" fill="#084298" font-size="11">mapping-&gt;i_mmap_rwsem</text>
    <text x="400" y="192" text-anchor="middle" fill="#495057" font-size="10">[Взято другим]</text>

    <!-- Node C -->
    <rect x="580" y="130" width="160" height="75" rx="8" fill="#e2d9f3" stroke="#59359a" stroke-width="2"/>
    <text x="660" y="158" text-anchor="middle" fill="#59359a" font-weight="bold" font-size="13">Клас C</text>
    <text x="660" y="176" text-anchor="middle" fill="#59359a" font-size="11">page_table_lock</text>
    <text x="660" y="192" text-anchor="middle" fill="#495057" font-size="10">[Взято третім]</text>

    <!-- Arrow A -> B -->
    <path d="M 220 167 L 308 167" fill="none" stroke="#198754" stroke-width="2.5" marker-end="url(#arrow-green)"/>
    <text x="264" y="155" text-anchor="middle" fill="#198754" font-weight="bold" font-size="11">Потік 1: A → B</text>

    <!-- Arrow B -> C -->
    <path d="M 480 167 L 568 167" fill="none" stroke="#0d6efd" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
    <text x="524" y="155" text-anchor="middle" fill="#0d6efd" font-weight="bold" font-size="11">Потік 2: B → C</text>

    <!-- Cycle Attempt Arrow C -> A (Bottom curved path) -->
    <path d="M 660 215 C 660 310, 140 310, 140 217" fill="none" stroke="#dc3545" stroke-width="3" stroke-dasharray="6,4" marker-end="url(#arrow-red)"/>

    <!-- Warning badge on cycle -->
    <rect x="290" y="270" width="220" height="40" rx="6" fill="#f8d7da" stroke="#842029" stroke-width="1.5"/>
    <text x="400" y="288" text-anchor="middle" fill="#842029" font-weight="bold" font-size="11">Потік 3 спробував C → A!</text>
    <text x="400" y="302" text-anchor="middle" fill="#842029" font-size="10">Виявлено цикл A → B → C → A</text>

    <!-- Explanation footer -->
    <rect x="20" y="332" width="760" height="32" rx="4" fill="#ffffff" stroke="#dee2e6" stroke-width="1"/>
    <text x="400" y="352" text-anchor="middle" fill="#6c757d" font-size="11">Lockdep зупиняє операцію та генерує dmesg звіт до того, як потік 3 спричинить реальний дедлок.</text>

  </g>

  <defs>
    <marker id="arrow-green" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 9 3.5, 0 7" fill="#198754"/>
    </marker>
    <marker id="arrow-blue" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 9 3.5, 0 7" fill="#0d6efd"/>
    </marker>
    <marker id="arrow-red" markerWidth="9" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 9 3.5, 0 7" fill="#dc3545"/>
    </marker>
  </defs>
</svg>"""
    with open("img/lock-graph.svg", "w", encoding="utf-8") as f:
        f.write(svg)

def render_irq_deadlock():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="800" height="360">
  <rect width="800" height="360" fill="#f8f9fa" rx="8"/>
  <g font-family="system-ui, -apple-system, sans-serif" font-size="13">

    <!-- Header -->
    <rect x="20" y="16" width="760" height="36" rx="6" fill="#e9ecef" stroke="#ced4da" stroke-width="1"/>
    <text x="400" y="39" text-anchor="middle" font-weight="bold" fill="#212529" font-size="14">Виявлення інваріанту IRQ-контексту (Process Context vs HardIRQ)</text>

    <!-- Process Context Lane -->
    <rect x="30" y="65" width="740" height="135" rx="8" fill="#ffffff" stroke="#ced4da" stroke-width="1"/>
    <text x="50" y="90" font-weight="bold" fill="#0d6efd" font-size="12">Контекст процесу (CPU 0)</text>

    <!-- Step 1 Box -->
    <rect x="50" y="125" width="180" height="60" rx="6" fill="#e7f1ff" stroke="#0d6efd" stroke-width="1.5"/>
    <text x="140" y="150" text-anchor="middle" fill="#084298" font-weight="bold" font-size="11">1. spin_lock(&amp;lock_A)</text>
    <text x="140" y="168" text-anchor="middle" fill="#495057" font-size="10">IRQ залишаються увімкненими</text>

    <!-- Interrupt Line -->
    <path d="M 285 105 L 285 185" fill="none" stroke="#dc3545" stroke-width="2" stroke-dasharray="4,4"/>
    <rect x="245" y="75" width="80" height="24" rx="4" fill="#dc3545"/>
    <text x="285" y="91" text-anchor="middle" fill="#ffffff" font-weight="bold" font-size="10">Апаратне IRQ</text>

    <!-- Step 2 Box (HardIRQ Context) -->
    <rect x="320" y="125" width="230" height="60" rx="6" fill="#f8d7da" stroke="#dc3545" stroke-width="1.5"/>
    <text x="435" y="150" text-anchor="middle" fill="#842029" font-weight="bold" font-size="11">2. Обробник: spin_lock(&amp;lock_A)</text>
    <text x="435" y="168" text-anchor="middle" fill="#842029" font-size="10">Марне очікування звільнення lock_A</text>

    <!-- Step 3 Box (Deadlock) -->
    <rect x="580" y="125" width="170" height="60" rx="6" fill="#842029"/>
    <text x="665" y="150" text-anchor="middle" fill="#ffffff" font-weight="bold" font-size="11">3. МЕРТВА ПЕТЛЯ</text>
    <text x="665" y="168" text-anchor="middle" fill="#f8d7da" font-size="10">CPU0 чекає на сам себе</text>

    <!-- Safe Pattern Lane -->
    <rect x="30" y="215" width="740" height="130" rx="8" fill="#ffffff" stroke="#198754" stroke-width="1.5"/>
    <text x="50" y="240" font-weight="bold" fill="#198754" font-size="12">Безпечний шаблон (Safe Pattern)</text>

    <rect x="50" y="260" width="270" height="65" rx="6" fill="#d1e7dd" stroke="#198754" stroke-width="1.5"/>
    <text x="185" y="285" text-anchor="middle" fill="#0f5132" font-weight="bold" font-size="11">spin_lock_irqsave(&amp;lock_A, flags)</text>
    <text x="185" y="305" text-anchor="middle" fill="#0f5132" font-size="10">Переривання локально вимкнені</text>

    <rect x="350" y="260" width="400" height="65" rx="6" fill="#e9ecef" stroke="#6c757d" stroke-width="1"/>
    <text x="550" y="285" text-anchor="middle" fill="#212529" font-weight="bold" font-size="11">Обробка IRQ відкладається до spin_unlock_irqrestore()</text>
    <text x="550" y="305" text-anchor="middle" fill="#495057" font-size="10">Lockdep відстежує стан: IRQ-safe клас блокування у безпеці</text>

  </g>
</svg>"""
    with open("img/irq-deadlock-state.svg", "w", encoding="utf-8") as f:
        f.write(svg)

def render():
    render_lock_graph()
    render_irq_deadlock()
    print("SVG figures generated successfully.")

if __name__ == '__main__':
    render()
