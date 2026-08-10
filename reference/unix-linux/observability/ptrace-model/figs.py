import os

def render_tracer_tracee():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <rect width="800" height="400" fill="#ffffff"/>
    <rect x="100" y="100" width="200" height="150" rx="10" fill="#cce5ff" stroke="#004085" stroke-width="2"/>
    <text x="200" y="140" font-family="Arial" font-size="20" font-weight="bold" text-anchor="middle" fill="#004085">Tracer</text>
    <text x="200" y="170" font-family="monospace" font-size="14" text-anchor="middle" fill="#004085">(gdb, strace)</text>
    
    <rect x="500" y="100" width="200" height="150" rx="10" fill="#d4edda" stroke="#155724" stroke-width="2"/>
    <text x="600" y="140" font-family="Arial" font-size="20" font-weight="bold" text-anchor="middle" fill="#155724">Tracee</text>
    <text x="600" y="170" font-family="monospace" font-size="14" text-anchor="middle" fill="#155724">(Target Process)</text>
    
    <path d="M 300 150 L 490 150" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="400" y="140" font-family="monospace" font-size="14" text-anchor="middle">ptrace(request, ...)</text>
    
    <path d="M 500 200 L 310 200" stroke="#dc3545" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrow-red)"/>
    <text x="400" y="225" font-family="monospace" font-size="14" text-anchor="middle" fill="#dc3545">SIGTRAP (waitpid)</text>
    
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#333"/>
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc3545"/>
        </marker>
    </defs>
</svg>
"""
    with open("fig-ptrace-arch.svg", "w", encoding="utf-8") as f:
        f.write(svg)

def render_breakpoint():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300">
    <rect width="800" height="300" fill="#ffffff"/>
    
    <rect x="50" y="50" width="300" height="200" fill="#f8f9fa" stroke="#6c757d" stroke-width="2"/>
    <text x="200" y="80" font-family="Arial" font-size="18" font-weight="bold" text-anchor="middle">Original Memory</text>
    <text x="80" y="120" font-family="monospace" font-size="16">0x400500: 48 c7 c0</text>
    <text x="80" y="150" font-family="monospace" font-size="16">0x400503: 01 00 00</text>
    <text x="80" y="180" font-family="monospace" font-size="16">0x400506: 0f 05</text>
    
    <path d="M 370 150 L 430 150" stroke="#007bff" stroke-width="3" marker-end="url(#arrow-blue)"/>
    <text x="400" y="140" font-family="Arial" font-size="14" text-anchor="middle" fill="#007bff">PTRACE_POKEDATA</text>
    
    <rect x="450" y="50" width="300" height="200" fill="#fff3cd" stroke="#856404" stroke-width="2"/>
    <text x="600" y="80" font-family="Arial" font-size="18" font-weight="bold" text-anchor="middle">Modified Memory</text>
    <text x="480" y="120" font-family="monospace" font-size="16">0x400500: 48 c7 c0</text>
    <text x="480" y="150" font-family="monospace" font-size="16" fill="#dc3545">0x400503: cc 00 00</text>
    <text x="480" y="180" font-family="monospace" font-size="16">0x400506: 0f 05</text>
    <text x="650" y="150" font-family="Arial" font-size="12" fill="#dc3545">&lt;-- int 3</text>
    
    <defs>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#007bff"/>
        </marker>
    </defs>
</svg>
"""
    with open("fig-breakpoint.svg", "w", encoding="utf-8") as f:
        f.write(svg)

def render():
    render_tracer_tracee()
    render_breakpoint()

if __name__ == "__main__":
    render()
