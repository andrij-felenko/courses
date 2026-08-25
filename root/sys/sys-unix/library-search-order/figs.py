import os
import sys

def generate_search_order_svg(filepath):
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 560" font-family="sans-serif">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <text x="420" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#111827">Алгоритм пошуку розділюваних бібліотек (ld.so)</text>

    <!-- Step 1: DT_RPATH -->
    <rect x="120" y="65" width="600" height="65" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
    <text x="140" y="93" font-size="15" font-weight="bold" fill="#1e40af">1. DT_RPATH</text>
    <text x="140" y="115" font-size="13" fill="#1e3a8a">Перевіряється першим, ЯКЩО у файлі ВІДСУТНІЙ тег DT_RUNPATH. Ігнорується для SUID/SGID.</text>

    <!-- Down arrow 1 -->
    <path d="M 420 130 L 420 155" stroke="#6b7280" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- Step 2: LD_LIBRARY_PATH -->
    <rect x="120" y="160" width="600" height="65" rx="8" fill="#fff7ed" stroke="#f97316" stroke-width="2"/>
    <text x="140" y="188" font-size="15" font-weight="bold" fill="#c2410c">2. LD_LIBRARY_PATH</text>
    <text x="140" y="210" font-size="13" fill="#9a3412">Змінна середовища зі списком шляхів. Повністю ІГНОРУЄТЬСЯ в режимі AT_SECURE (SUID/SGID).</text>

    <!-- Down arrow 2 -->
    <path d="M 420 225 L 420 250" stroke="#6b7280" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- Step 3: DT_RUNPATH -->
    <rect x="120" y="255" width="600" height="65" rx="8" fill="#f0fdf4" stroke="#22c55e" stroke-width="2"/>
    <text x="140" y="283" font-size="15" font-weight="bold" fill="#15803d">3. DT_RUNPATH</text>
    <text x="140" y="305" font-size="13" fill="#166534">Зашиті шляхи нижчого пріоритету. Дозволяє оверрайд через LD_LIBRARY_PATH.</text>

    <!-- Down arrow 3 -->
    <path d="M 420 320 L 420 345" stroke="#6b7280" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- Step 4: Cache -->
    <rect x="120" y="350" width="600" height="65" rx="8" fill="#fcf4ff" stroke="#a855f7" stroke-width="2"/>
    <text x="140" y="378" font-size="15" font-weight="bold" fill="#7e22ce">4. /etc/ld.so.cache</text>
    <text x="140" y="400" font-size="13" fill="#6b21a8">Бінарний кеш оновлюється через ldconfig. Ігнорується, якщо ввімкнено -z nodeflib.</text>

    <!-- Down arrow 4 -->
    <path d="M 420 415 L 420 440" stroke="#6b7280" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- Step 5: System Default Paths -->
    <rect x="120" y="445" width="600" height="65" rx="8" fill="#f8fafc" stroke="#64748b" stroke-width="2"/>
    <text x="140" y="473" font-size="15" font-weight="bold" fill="#334155">5. Стандартні системні каталоги</text>
    <text x="140" y="495" font-size="13" fill="#475569">Fallback: /lib64, /usr/lib64 (або multiarch /lib/x86_64-linux-gnu).</text>

    <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M 0 0 L 8 4 L 0 8 z" fill="#6b7280"/>
        </marker>
    </defs>
</svg>"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)

def generate_rpath_runpath_svg(filepath):
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 400" font-family="sans-serif">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <text x="420" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#111827">Порівняння DT_RPATH та DT_RUNPATH у ланцюжку пошуку</text>

    <!-- Scenario A: DT_RPATH present without DT_RUNPATH -->
    <g transform="translate(40, 70)">
        <rect x="0" y="0" width="760" height="120" rx="8" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
        <text x="20" y="30" font-size="16" font-weight="bold" fill="#991b1b">Сценарій А: Лише DT_RPATH (застаріла поведінка SVR4)</text>
        
        <rect x="30" y="50" width="180" height="45" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
        <text x="120" y="77" text-anchor="middle" font-size="14" font-weight="bold" fill="#7f1d1d">1. DT_RPATH</text>

        <path d="M 210 72.5 L 260 72.5" stroke="#991b1b" stroke-width="2" marker-end="url(#arrow-red)"/>

        <rect x="265" y="50" width="200" height="45" rx="6" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1.5"/>
        <text x="365" y="77" text-anchor="middle" font-size="14" fill="#4b5563">2. LD_LIBRARY_PATH</text>

        <path d="M 465 72.5 L 515 72.5" stroke="#991b1b" stroke-width="2" marker-end="url(#arrow-red)"/>

        <rect x="520" y="50" width="200" height="45" rx="6" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1.5"/>
        <text x="620" y="77" text-anchor="middle" font-size="14" fill="#4b5563">3. Cache &amp; System</text>

        <text x="20" y="108" font-size="12" fill="#b91c1c">Результат: LD_LIBRARY_PATH НЕ МОЖЕ перевизначити DT_RPATH!</text>
    </g>

    <!-- Scenario B: DT_RUNPATH present -->
    <g transform="translate(40, 220)">
        <rect x="0" y="0" width="760" height="130" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
        <text x="20" y="30" font-size="16" font-weight="bold" fill="#14532d">Сценарій Б: Наявний DT_RUNPATH (сучасний стандарт ELF)</text>

        <rect x="30" y="50" width="180" height="45" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
        <text x="110" y="77" text-anchor="middle" font-size="14" font-weight="bold" fill="#92400e">1. LD_LIBRARY_PATH</text>

        <path d="M 210 72.5 L 260 72.5" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>

        <rect x="265" y="50" width="200" height="45" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
        <text x="365" y="77" text-anchor="middle" font-size="14" font-weight="bold" fill="#14532d">2. DT_RUNPATH</text>

        <path d="M 465 72.5 L 515 72.5" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>

        <rect x="520" y="50" width="200" height="45" rx="6" fill="#f3f4f6" stroke="#9ca3af" stroke-width="1.5"/>
        <text x="620" y="77" text-anchor="middle" font-size="14" fill="#4b5563">3. Cache &amp; System</text>

        <text x="20" y="112" font-size="12" fill="#15803d">Результат: DT_RPATH повністю ігнорується, LD_LIBRARY_PATH отримує вищий пріоритет.</text>
    </g>

    <defs>
        <marker id="arrow-red" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M 0 0 L 8 4 L 0 8 z" fill="#991b1b"/>
        </marker>
        <marker id="arrow-green" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M 0 0 L 8 4 L 0 8 z" fill="#16a34a"/>
        </marker>
    </defs>
</svg>"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg)

def render():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    generate_search_order_svg(os.path.join(img_dir, 'search-order.svg'))
    generate_rpath_runpath_svg(os.path.join(img_dir, 'rpath-vs-runpath.svg'))

if __name__ == '__main__':
    render()
