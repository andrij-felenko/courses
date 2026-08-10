import os

def render():
    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="800" height="400" fill="#f8f9fa"/>
    <text x="400" y="50" font-family="sans-serif" font-size="24" text-anchor="middle" fill="#333">Standard Linux vs PREEMPT_RT Interrupt Handling</text>
    <rect x="50" y="100" width="300" height="200" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="200" y="130" font-family="sans-serif" font-size="18" text-anchor="middle" fill="#495057">Standard (Mainline)</text>
    <rect x="70" y="150" width="260" height="40" fill="#ff9999"/>
    <text x="200" y="175" font-family="sans-serif" font-size="14" text-anchor="middle">Hard IRQ (Non-preemptible)</text>
    <rect x="70" y="200" width="260" height="40" fill="#ffcc99"/>
    <text x="200" y="225" font-family="sans-serif" font-size="14" text-anchor="middle">SoftIRQ (Tasklet/Bottom Half)</text>
    <rect x="70" y="250" width="260" height="40" fill="#cce5ff"/>
    <text x="200" y="275" font-family="sans-serif" font-size="14" text-anchor="middle">User Task</text>

    <rect x="450" y="100" width="300" height="200" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="600" y="130" font-family="sans-serif" font-size="18" text-anchor="middle" fill="#495057">PREEMPT_RT</text>
    <rect x="470" y="150" width="260" height="30" fill="#ff9999"/>
    <text x="600" y="170" font-family="sans-serif" font-size="14" text-anchor="middle">Hard IRQ (Minimal setup)</text>
    <rect x="470" y="190" width="260" height="50" fill="#99ccff"/>
    <text x="600" y="220" font-family="sans-serif" font-size="14" text-anchor="middle">IRQ Thread (Preemptible)</text>
    <rect x="470" y="250" width="260" height="40" fill="#cce5ff"/>
    <text x="600" y="275" font-family="sans-serif" font-size="14" text-anchor="middle">User Task</text>
</svg>"""

    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="800" height="400" fill="#ffffff"/>
    <text x="400" y="40" font-family="sans-serif" font-size="22" text-anchor="middle">Priority Inheritance in PREEMPT_RT</text>
    <circle cx="150" cy="150" r="40" fill="#ff9999"/>
    <text x="150" y="155" font-family="sans-serif" font-size="14" text-anchor="middle">Task H (Prio 90)</text>
    
    <circle cx="400" cy="150" r="40" fill="#ffcc99"/>
    <text x="400" y="155" font-family="sans-serif" font-size="14" text-anchor="middle">Task M (Prio 50)</text>
    
    <circle cx="650" cy="150" r="40" fill="#99ccff"/>
    <text x="650" y="155" font-family="sans-serif" font-size="14" text-anchor="middle">Task L (Prio 10)</text>
    
    <rect x="580" y="250" width="140" height="60" fill="#e2e3e5"/>
    <text x="650" y="285" font-family="sans-serif" font-size="14" text-anchor="middle">rt_mutex (Locked by L)</text>
    
    <path d="M 190 150 L 350 150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="270" y="140" font-family="sans-serif" font-size="12" text-anchor="middle">Blocks on H</text>
    
    <path d="M 650 190 L 650 250" stroke="black" stroke-width="2"/>
    <path d="M 150 190 L 150 280 L 580 280" stroke="red" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="365" y="270" font-family="sans-serif" font-size="12" text-anchor="middle" fill="red">H requests mutex</text>
    
    <text x="650" y="340" font-family="sans-serif" font-size="16" text-anchor="middle" fill="blue">L temporarily inherits Prio 90</text>
</svg>"""

    with open('fig_irq.svg', 'w') as f:
        f.write(svg1)
    with open('fig_pi.svg', 'w') as f:
        f.write(svg2)

if __name__ == '__main__':
    render()
