import os

def render_got_plt():
    svg = '''<svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
    <rect width="100%" height="100%" fill="#f8f9fa"/>
    <g transform="translate(50, 50)">
        <rect x="0" y="0" width="200" height="300" fill="#e9ecef" stroke="#ced4da" stroke-width="2" rx="5"/>
        <text x="100" y="30" text-anchor="middle" font-weight="bold">Код (Text Segment)</text>
        
        <rect x="20" y="80" width="160" height="40" fill="#fff" stroke="#adb5bd" rx="3"/>
        <text x="100" y="105" text-anchor="middle" font-size="14">call printf@PLT</text>
        
        <rect x="20" y="200" width="160" height="80" fill="#e3f2fd" stroke="#90caf9" rx="3"/>
        <text x="100" y="225" text-anchor="middle" font-weight="bold">PLT</text>
        <text x="100" y="245" text-anchor="middle" font-size="12">jmp *printf@GOT</text>
    </g>

    <g transform="translate(350, 50)">
        <rect x="0" y="0" width="150" height="300" fill="#e9ecef" stroke="#ced4da" stroke-width="2" rx="5"/>
        <text x="75" y="30" text-anchor="middle" font-weight="bold">Дані (Data Seg)</text>
        
        <rect x="20" y="200" width="110" height="80" fill="#fce4ec" stroke="#f48fb1" rx="3"/>
        <text x="75" y="225" text-anchor="middle" font-weight="bold">GOT</text>
        <text x="75" y="245" text-anchor="middle" font-size="12">printf: &lt;addr&gt;</text>
    </g>

    <g transform="translate(600, 50)">
        <rect x="0" y="0" width="150" height="300" fill="#e9ecef" stroke="#ced4da" stroke-width="2" rx="5"/>
        <text x="75" y="30" text-anchor="middle" font-weight="bold">libc.so</text>
        
        <rect x="20" y="100" width="110" height="40" fill="#e8f5e9" stroke="#81c784" rx="3"/>
        <text x="75" y="125" text-anchor="middle" font-size="14">printf()</text>
    </g>

    <!-- Arrows -->
    <path d="M 150 170 L 150 200" stroke="#495057" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
    <path d="M 230 280 L 370 280" stroke="#495057" stroke-width="2" fill="none" marker-end="url(#arrow)"/>
    <path d="M 460 250 L 620 150" stroke="#495057" stroke-width="2" fill="none" marker-end="url(#arrow)" stroke-dasharray="5,5"/>

    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#495057"/>
        </marker>
    </defs>
</svg>'''
    with open("got_plt.svg", "w", encoding="utf-8") as f:
        f.write(svg)

def render_aslr():
    svg = '''<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <!-- Without PIE/ASLR -->
    <text x="200" y="40" text-anchor="middle" font-size="16" font-weight="bold">Без PIE (Фіксована адреса)</text>
    <rect x="50" y="60" width="300" height="40" fill="#ffcdd2" stroke="#ef5350" rx="3"/>
    <text x="200" y="85" text-anchor="middle">Executable (завжди 0x400000)</text>
    
    <rect x="50" y="110" width="300" height="40" fill="#c8e6c9" stroke="#66bb6a" rx="3"/>
    <text x="200" y="135" text-anchor="middle">libc.so (рандомізовано)</text>

    <!-- With PIE/ASLR -->
    <text x="600" y="40" text-anchor="middle" font-size="16" font-weight="bold">З PIE (Повна ASLR)</text>
    <rect x="450" y="160" width="300" height="40" fill="#bbdefb" stroke="#42a5f5" rx="3"/>
    <text x="600" y="185" text-anchor="middle">Executable (рандомізовано)</text>
    
    <rect x="450" y="80" width="300" height="40" fill="#c8e6c9" stroke="#66bb6a" rx="3"/>
    <text x="600" y="105" text-anchor="middle">libc.so (рандомізовано)</text>

</svg>'''
    with open("aslr_pie.svg", "w", encoding="utf-8") as f:
        f.write(svg)

def render():
    render_got_plt()
    render_aslr()

if __name__ == "__main__":
    # Move to the script's directory before generating files
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    render()
