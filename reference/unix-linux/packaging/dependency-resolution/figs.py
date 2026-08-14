import os

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def render_dependency_graph():
    svg_content = """<svg viewBox="0 0 840 420" xmlns="http://www.w3.org/2000/svg">
    <rect width="840" height="420" fill="#f8f9fa" rx="10" stroke="#dee2e6" stroke-width="2"/>
    <text x="420" y="32" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#212529">Модель графа залежностей, віртуальних пакунків та конфліктів</text>
    
    <!-- Target Package -->
    <g transform="translate(40, 160)">
        <rect width="180" height="90" fill="#0d6efd" stroke="#0a58ca" stroke-width="2" rx="8"/>
        <text x="90" y="38" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#ffffff">web-server-app</text>
        <text x="90" y="60" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#e7f1ff">Depends: libssl (>= 1.1)</text>
        <text x="90" y="76" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#e7f1ff">Depends: mail-agent</text>
    </g>
    
    <!-- Direct Dependency: libssl -->
    <g transform="translate(300, 60)">
        <rect width="200" height="80" fill="#198754" stroke="#146c43" stroke-width="2" rx="8"/>
        <text x="100" y="36" font-family="sans-serif" font-size="15" font-weight="bold" text-anchor="middle" fill="#ffffff">libssl1.1 (v1.1.1k)</text>
        <text x="100" y="58" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#d1e7dd">Provides: libssl</text>
    </g>

    <!-- Virtual Package Node -->
    <g transform="translate(300, 240)">
        <rect width="200" height="80" fill="#6f42c1" stroke="#59359a" stroke-width="2" rx="8" stroke-dasharray="6,4"/>
        <text x="100" y="36" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#ffffff">mail-transport-agent</text>
        <text x="100" y="58" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#e2d9f3">(Віртуальний пакунок)</text>
    </g>

    <!-- Provider 1: Postfix -->
    <g transform="translate(590, 180)">
        <rect width="210" height="80" fill="#ffffff" stroke="#198754" stroke-width="2" rx="8"/>
        <text x="105" y="34" font-family="sans-serif" font-size="15" font-weight="bold" text-anchor="middle" fill="#0F5132">postfix</text>
        <text x="105" y="54" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#146c43">Provides: mail-agent</text>
        <text x="105" y="68" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#dc3545">Conflicts: sendmail, exim4</text>
    </g>

    <!-- Provider 2: Sendmail -->
    <g transform="translate(590, 300)">
        <rect width="210" height="80" fill="#ffffff" stroke="#dc3545" stroke-width="2" rx="8"/>
        <text x="105" y="34" font-family="sans-serif" font-size="15" font-weight="bold" text-anchor="middle" fill="#842029">sendmail</text>
        <text x="105" y="54" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#842029">Provides: mail-agent</text>
        <text x="105" y="68" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#dc3545">Conflicts: postfix, exim4</text>
    </g>

    <!-- Arrows -->
    <!-- App -> libssl -->
    <path d="M 220 185 Q 260 100 292 100" fill="none" stroke="#0d6efd" stroke-width="2" marker-end="url(#arrow-blue)"/>
    <text x="240" y="130" font-family="sans-serif" font-size="11" fill="#0d6efd">Depends</text>

    <!-- App -> Virtual -->
    <path d="M 220 225 Q 260 280 292 280" fill="none" stroke="#0d6efd" stroke-width="2" marker-end="url(#arrow-blue)"/>
    <text x="240" y="270" font-family="sans-serif" font-size="11" fill="#0d6efd">Depends</text>

    <!-- Virtual -> Postfix -->
    <path d="M 500 270 Q 545 220 582 220" fill="none" stroke="#6f42c1" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow-purple)"/>
    
    <!-- Virtual -> Sendmail -->
    <path d="M 500 290 Q 545 340 582 340" fill="none" stroke="#6f42c1" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow-purple)"/>

    <!-- Conflict Line between Postfix and Sendmail -->
    <path d="M 695 260 L 695 292" fill="none" stroke="#dc3545" stroke-width="2.5" stroke-dasharray="3,3" marker-end="url(#arrow-red)"/>
    <rect x="645" y="266" width="100" height="20" fill="#f8d7da" rx="4"/>
    <text x="695" y="280" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#842029">Conflicts!</text>

    <!-- Markers -->
    <defs>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#0d6efd"/>
        </marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#6f42c1"/>
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc3545"/>
        </marker>
    </defs>
</svg>"""

    out_path = os.path.join(IMG_DIR, 'dependency-graph.svg')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {out_path}")

def render_sat_cdcl_flow():
    svg_content = """<svg viewBox="0 0 840 400" xmlns="http://www.w3.org/2000/svg">
    <rect width="840" height="400" fill="#f8f9fa" rx="10" stroke="#dee2e6" stroke-width="2"/>
    <text x="420" y="32" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#212529">Алгоритм CDCL у розв'язанні залежностей (libsolv)</text>

    <!-- Step 1: CNF Load -->
    <g transform="translate(30, 60)">
        <rect width="180" height="70" fill="#ffffff" stroke="#6c757d" stroke-width="2" rx="6"/>
        <text x="90" y="30" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#212529">1. Вхідний вираз</text>
        <text x="90" y="50" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#495057">Правила CNF з репозиторію</text>
    </g>

    <!-- Step 2: Unit Propagation -->
    <g transform="translate(250, 60)">
        <rect width="180" height="70" fill="#0d6efd" stroke="#0a58ca" stroke-width="2" rx="6"/>
        <text x="90" y="30" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#ffffff">2. Unit Propagation</text>
        <text x="90" y="50" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#e7f1ff">Виведення обов'язкових виборів</text>
    </g>

    <!-- Step 3: Decision -->
    <g transform="translate(470, 60)">
        <rect width="180" height="70" fill="#198754" stroke="#146c43" stroke-width="2" rx="6"/>
        <text x="90" y="30" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#ffffff">3. Decision</text>
        <text x="90" y="50" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#d1e7dd">Здогадка / Евристика версії</text>
    </g>

    <!-- Step 4: Decision Check / Conflict -->
    <g transform="translate(470, 190)">
        <polygon points="90,0 180,45 90,90 0,45" fill="#ffc107" stroke="#d39e00" stroke-width="2"/>
        <text x="90" y="42" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#212529">Виник конфлікт?</text>
    </g>

    <!-- Step 5: Conflict Analysis & Clause Learning -->
    <g transform="translate(250, 200)">
        <rect width="180" height="70" fill="#dc3545" stroke="#b02a37" stroke-width="2" rx="6"/>
        <text x="90" y="30" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#ffffff">4. Clause Learning</text>
        <text x="90" y="50" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#f8d7da">Додавання правила-заборонити</text>
    </g>

    <!-- Step 6: Backjump -->
    <g transform="translate(30, 200)">
        <rect width="180" height="70" fill="#6f42c1" stroke="#59359a" stroke-width="2" rx="6"/>
        <text x="90" y="30" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#ffffff">5. Non-chronological</text>
        <text x="90" y="50" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#e2d9f3">Backjump на рівень рішення</text>
    </g>

    <!-- Success Outcome -->
    <g transform="translate(680, 200)">
        <rect width="130" height="70" fill="#198754" stroke="#146c43" stroke-width="2" rx="6"/>
        <text x="65" y="30" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#ffffff">УСПІХ (SAT)</text>
        <text x="65" y="50" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#d1e7dd">План транзакції</text>
    </g>

    <!-- Arrows -->
    <!-- 1 -> 2 -->
    <path d="M 210 95 L 242 95" fill="none" stroke="#495057" stroke-width="2" marker-end="url(#arrow-dark)"/>

    <!-- 2 -> 3 -->
    <path d="M 430 95 L 462 95" fill="none" stroke="#495057" stroke-width="2" marker-end="url(#arrow-dark)"/>

    <!-- 3 -> 4 (Check) -->
    <path d="M 560 130 L 560 182" fill="none" stroke="#495057" stroke-width="2" marker-end="url(#arrow-dark)"/>

    <!-- Check -> Conflict (Yes) -->
    <path d="M 470 235 L 438 235" fill="none" stroke="#dc3545" stroke-width="2" marker-end="url(#arrow-red-cdcl)"/>
    <text x="454" y="225" font-family="sans-serif" font-size="11" font-weight="bold" fill="#dc3545">Так</text>

    <!-- Check -> Success (No, all assigned) -->
    <path d="M 650 235 L 672 235" fill="none" stroke="#198754" stroke-width="2" marker-end="url(#arrow-green-cdcl)"/>
    <text x="660" y="225" font-family="sans-serif" font-size="11" font-weight="bold" fill="#198754">Ні</text>

    <!-- Conflict -> Backjump -->
    <path d="M 250 235 L 218 235" fill="none" stroke="#6f42c1" stroke-width="2" marker-end="url(#arrow-purple-cdcl)"/>

    <!-- Backjump -> Unit Propagation -->
    <path d="M 120 200 L 120 160 Q 120 95 242 95" fill="none" stroke="#6f42c1" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow-purple-cdcl)"/>

    <defs>
        <marker id="arrow-dark" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#495057"/>
        </marker>
        <marker id="arrow-red-cdcl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc3545"/>
        </marker>
        <marker id="arrow-green-cdcl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#198754"/>
        </marker>
        <marker id="arrow-purple-cdcl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#6f42c1"/>
        </marker>
    </defs>
</svg>"""

    out_path = os.path.join(IMG_DIR, 'sat-cdcl-flow.svg')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {out_path}")

def render_diamond_dependency_and_soname():
    svg_content = """<svg viewBox="0 0 840 420" xmlns="http://www.w3.org/2000/svg">
    <rect width="840" height="420" fill="#f8f9fa" rx="10" stroke="#dee2e6" stroke-width="2"/>
    <text x="420" y="32" font-family="sans-serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#212529">Діамантова залежність та її розв'язання через soname</text>

    <!-- LEFT PANEL: Diamond Conflict -->
    <g transform="translate(20, 50)">
        <rect width="380" height="350" fill="#ffffff" stroke="#dc3545" stroke-width="1.5" rx="8"/>
        <text x="190" y="28" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#dc3545">Конфлікт: Єдине ім'я пакунка (libfoo)</text>
        
        <!-- App -->
        <rect x="130" y="45" width="120" height="45" fill="#0d6efd" rx="5"/>
        <text x="190" y="72" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#ffffff">App</text>

        <!-- LibA and LibB -->
        <rect x="35" y="130" width="120" height="45" fill="#6c757d" rx="5"/>
        <text x="95" y="157" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#ffffff">LibA (req v1.0)</text>

        <rect x="225" y="130" width="120" height="45" fill="#6c757d" rx="5"/>
        <text x="285" y="157" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#ffffff">LibB (req v2.0)</text>

        <!-- Shared Lib Target Conflict -->
        <rect x="110" y="235" width="160" height="60" fill="#f8d7da" stroke="#f5c2c7" stroke-width="2" rx="5"/>
        <text x="190" y="258" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#842029">libfoo (файл libfoo.so)</text>
        <text x="190" y="278" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#842029">Неможливо поставити v1 й v2 разом!</text>

        <!-- Arrows Left -->
        <path d="M 160 90 L 115 125" fill="none" stroke="#495057" stroke-width="1.5" marker-end="url(#arrow-dia)"/>
        <path d="M 220 90 L 265 125" fill="none" stroke="#495057" stroke-width="1.5" marker-end="url(#arrow-dia)"/>
        <path d="M 115 175 L 160 228" fill="none" stroke="#dc3545" stroke-width="1.5" marker-end="url(#arrow-red-dia)"/>
        <path d="M 265 175 L 220 228" fill="none" stroke="#dc3545" stroke-width="1.5" marker-end="url(#arrow-red-dia)"/>
    </g>

    <!-- RIGHT PANEL: Resolution via soname -->
    <g transform="translate(440, 50)">
        <rect width="380" height="350" fill="#ffffff" stroke="#198754" stroke-width="1.5" rx="8"/>
        <text x="190" y="28" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="#198754">Розв'язок: Розділення за soname</text>
        
        <!-- App -->
        <rect x="130" y="45" width="120" height="45" fill="#0d6efd" rx="5"/>
        <text x="190" y="72" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#ffffff">App</text>

        <!-- LibA and LibB -->
        <rect x="35" y="130" width="120" height="45" fill="#6c757d" rx="5"/>
        <text x="95" y="157" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#ffffff">LibA</text>

        <rect x="225" y="130" width="120" height="45" fill="#6c757d" rx="5"/>
        <text x="285" y="157" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="#ffffff">LibB</text>

        <!-- Co-existing packages -->
        <rect x="25" y="235" width="140" height="60" fill="#d1e7dd" stroke="#badbcc" stroke-width="1.5" rx="5"/>
        <text x="95" y="258" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#0f5132">libfoo1</text>
        <text x="95" y="278" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#146c43">/usr/lib/libfoo.so.1</text>

        <rect x="215" y="235" width="140" height="60" fill="#d1e7dd" stroke="#badbcc" stroke-width="1.5" rx="5"/>
        <text x="285" y="258" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle" fill="#0f5132">libfoo2</text>
        <text x="285" y="278" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#146c43">/usr/lib/libfoo.so.2</text>

        <!-- Arrows Right -->
        <path d="M 160 90 L 115 125" fill="none" stroke="#495057" stroke-width="1.5" marker-end="url(#arrow-dia)"/>
        <path d="M 220 90 L 265 125" fill="none" stroke="#495057" stroke-width="1.5" marker-end="url(#arrow-dia)"/>
        <path d="M 95 175 L 95 228" fill="none" stroke="#198754" stroke-width="1.5" marker-end="url(#arrow-green-dia)"/>
        <path d="M 285 175 L 285 228" fill="none" stroke="#198754" stroke-width="1.5" marker-end="url(#arrow-green-dia)"/>
    </g>

    <defs>
        <marker id="arrow-dia" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#495057"/>
        </marker>
        <marker id="arrow-red-dia" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc3545"/>
        </marker>
        <marker id="arrow-green-dia" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#198754"/>
        </marker>
    </defs>
</svg>"""

    out_path = os.path.join(IMG_DIR, 'diamond-dependency-and-soname.svg')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated {out_path}")

def generate():
    render_dependency_graph()
    render_sat_cdcl_flow()
    render_diamond_dependency_and_soname()

if __name__ == '__main__':
    generate()
