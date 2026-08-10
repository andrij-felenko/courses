import os
import sys

def render_svg(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
    <!-- Тло -->
    <rect width="800" height="500" fill="#f8f9fa"/>
    
    <!-- Ядро -->
    <rect x="50" y="250" width="700" height="200" rx="10" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="400" y="280" font-family="sans-serif" font-size="20" font-weight="bold" text-anchor="middle" fill="#495057">Kernel Space (VFS &amp; fanotify)</text>

    <!-- Користувацький простір -->
    <rect x="50" y="50" width="700" height="150" rx="10" fill="#e9ecef" stroke="#ced4da" stroke-width="2"/>
    <text x="400" y="80" font-family="sans-serif" font-size="20" font-weight="bold" text-anchor="middle" fill="#495057">User Space</text>

    <!-- Процес-клієнт -->
    <rect x="100" y="100" width="180" height="70" rx="5" fill="#cce5ff" stroke="#b8daff" stroke-width="2"/>
    <text x="190" y="140" font-family="sans-serif" font-size="16" text-anchor="middle" fill="#004085">User Process</text>
    
    <!-- Антивірусний Демон -->
    <rect x="520" y="100" width="180" height="70" rx="5" fill="#d4edda" stroke="#c3e6cb" stroke-width="2"/>
    <text x="610" y="140" font-family="sans-serif" font-size="16" text-anchor="middle" fill="#155724">AV Daemon</text>

    <!-- Системний виклик -->
    <path d="M 190 170 L 190 320" fill="none" stroke="#0056b3" stroke-width="3" marker-end="url(#arrow-blue)"/>
    <text x="200" y="230" font-family="sans-serif" font-size="14" fill="#0056b3">1. open("/etc/shadow")</text>

    <!-- Перехоплення -->
    <rect x="140" y="320" width="520" height="100" rx="5" fill="#fff3cd" stroke="#ffeeba" stroke-width="2"/>
    <text x="400" y="350" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#856404">fanotify subsystem (hooked)</text>

    <!-- Подія до демона -->
    <path d="M 560 320 L 560 170" fill="none" stroke="#d39e00" stroke-width="3" stroke-dasharray="5,5" marker-end="url(#arrow-yellow)"/>
    <text x="570" y="240" font-family="sans-serif" font-size="14" fill="#856404">2. FAN_OPEN_PERM event</text>

    <!-- Відповідь від демона -->
    <path d="M 660 170 L 660 320" fill="none" stroke="#28a745" stroke-width="3" marker-end="url(#arrow-green)"/>
    <text x="670" y="240" font-family="sans-serif" font-size="14" fill="#155724">3. FAN_ALLOW / FAN_DENY</text>

    <!-- Повернення результату -->
    <path d="M 140 370 L 80 370 L 80 135 L 100 135" fill="none" stroke="#0056b3" stroke-width="3" marker-end="url(#arrow-blue)"/>
    <text x="90" y="250" font-family="sans-serif" font-size="14" fill="#0056b3" transform="rotate(-90 90 250)">4. return fd or -EPERM</text>

    <defs>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#0056b3"/>
        </marker>
        <marker id="arrow-yellow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#d39e00"/>
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#28a745"/>
        </marker>
    </defs>
</svg>"""
    render_svg('fanotify-arch.svg', svg_content)
    print("Generated fanotify-arch.svg")

if __name__ == '__main__':
    main()
