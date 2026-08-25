import os

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    # 1. vDSO vs syscall illustration
    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 440" width="850" height="440">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <!-- Title -->
    <text x="425" y="35" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" font-weight="bold" fill="#1e293b" text-anchor="middle">Порівняння виконання системного виклику та vDSO</text>
    
    <!-- User Space Box -->
    <rect x="40" y="60" width="350" height="340" fill="#f0f9ff" stroke="#0284c7" stroke-width="2" rx="12"/>
    <text x="215" y="88" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" font-weight="bold" fill="#0369a1" text-anchor="middle">User Space (Ring 3)</text>
    
    <!-- Kernel Space Box -->
    <rect x="460" y="60" width="350" height="340" fill="#fff7ed" stroke="#ea580c" stroke-width="2" rx="12"/>
    <text x="635" y="88" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="18" font-weight="bold" fill="#c2410c" text-anchor="middle">Kernel Space (Ring 0)</text>
    
    <!-- App Code Node -->
    <rect x="70" y="105" width="290" height="45" fill="#ffffff" stroke="#0284c7" stroke-width="1.5" rx="6"/>
    <text x="215" y="133" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">Застосунок: clock_gettime()</text>
    
    <!-- vDSO Box Node -->
    <rect x="70" y="275" width="290" height="100" fill="#dcfce7" stroke="#16a34a" stroke-width="2" rx="8"/>
    <text x="215" y="305" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" font-weight="bold" fill="#15803d" text-anchor="middle">Сторінки vDSO / vvar</text>
    <text x="215" y="330" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#166534" text-anchor="middle">Код читає час через seqlock + rdtsc</text>
    <text x="215" y="353" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#15803d" text-anchor="middle">Без перемикання контексту (~10-15 ns)</text>
    
    <!-- Kernel Syscall Handler Node -->
    <rect x="490" y="175" width="290" height="105" fill="#ffffff" stroke="#ea580c" stroke-width="1.5" rx="6"/>
    <text x="635" y="205" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" font-weight="bold" fill="#9a3412" text-anchor="middle">Ядро: do_sys_clock_gettime</text>
    <text x="635" y="233" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#c2410c" text-anchor="middle">Збереження pt_regs, KPTI, MSR</text>
    <text x="635" y="255" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#9a3412" text-anchor="middle">Перемикання контексту (~150-300 ns)</text>
    
    <!-- Traditional Syscall Path (Red) -->
    <path d="M 215 150 L 215 200 L 490 200" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="6,4" marker-end="url(#arrow-red)"/>
    <text x="425" y="188" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#dc2626" text-anchor="middle">syscall</text>
    
    <!-- Return from Kernel Syscall -->
    <path d="M 490 245 L 380 245 L 380 130 L 360 130" fill="none" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow-red)"/>
    
    <!-- vDSO Direct Path (Green) -->
    <path d="M 190 150 L 190 275" fill="none" stroke="#16a34a" stroke-width="3" marker-end="url(#arrow-green)"/>
    <text x="130" y="215" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#15803d">vDSO виклик</text>
    
    <!-- vDSO Return -->
    <path d="M 240 275 L 240 150" fill="none" stroke="#16a34a" stroke-width="2.5" marker-end="url(#arrow-green)"/>
    <text x="300" y="215" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#166534">Повернення</text>
    
    <!-- Markers -->
    <defs>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/>
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#16a34a"/>
        </marker>
    </defs>
</svg>"""

    # 2. Memory Layout vDSO / vvar / stack
    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 480" width="850" height="480">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <!-- Title -->
    <text x="425" y="35" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" font-weight="bold" fill="#1e293b" text-anchor="middle">Розміщення vDSO та vvar у віртуальному адресному просторі</text>
    
    <!-- Memory Outer Box -->
    <rect x="150" y="65" width="550" height="385" fill="#f8fafc" stroke="#475569" stroke-width="2" rx="10"/>
    <text x="425" y="92" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16" font-weight="bold" fill="#334155" text-anchor="middle">Адресний простір процесу (з ASLR рандомізацією)</text>
    
    <!-- High Addresses Arrow -->
    <text x="170" y="118" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#64748b">Високі адреси (0x7fff...)</text>
    
    <!-- Stack Block -->
    <rect x="200" y="130" width="450" height="75" fill="#e0e7ff" stroke="#4338ca" stroke-width="1.5" rx="6"/>
    <text x="425" y="155" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#3730a3" text-anchor="middle">Стек процесу ([stack])</text>
    <text x="425" y="180" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#312e81" text-anchor="middle">Auxiliary Vector: AT_SYSINFO_EHDR &#x2192; Вказівник на vDSO</text>
    
    <!-- vvar Block -->
    <rect x="200" y="230" width="450" height="70" fill="#fef3c7" stroke="#d97706" stroke-width="2" rx="6"/>
    <text x="425" y="255" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#b45309" text-anchor="middle">Сторінка [vvar] (Права доступу: r--p)</text>
    <text x="425" y="280" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#92400e" text-anchor="middle">Змінні часу ядра: sequence counter, wall_to_monotonic, mult, shift</text>
    
    <!-- vdso Block -->
    <rect x="200" y="325" width="450" height="70" fill="#dcfce7" stroke="#15803d" stroke-width="2" rx="6"/>
    <text x="425" y="350" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#15803d" text-anchor="middle">Сторінка [vdso] (Права доступу: r-xp)</text>
    <text x="425" y="375" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" fill="#166534" text-anchor="middle">Виконуваний ELF образ: __vdso_clock_gettime, __vdso_gettimeofday</text>
    
    <!-- Pointer Arrow from Stack to vDSO -->
    <path d="M 610 185 C 690 220, 690 320, 655 350" fill="none" stroke="#4338ca" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-indigo)"/>
    <text x="730" y="275" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#4338ca" text-anchor="middle">AT_SYSINFO_EHDR</text>
    
    <!-- Low Addresses Arrow -->
    <text x="170" y="435" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#64748b">Низькі адреси</text>
    
    <defs>
        <marker id="arrow-indigo" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#4338ca"/>
        </marker>
    </defs>
</svg>"""

    # 3. Seqlock Algorithm Flowchart
    svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 500" width="850" height="500">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <!-- Title -->
    <text x="425" y="35" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20" font-weight="bold" fill="#1e293b" text-anchor="middle">Алгоритм Seqlock читання часу у vDSO</text>
    
    <!-- Step 1: Read seq1 -->
    <rect x="275" y="65" width="300" height="50" fill="#f1f5f9" stroke="#475569" stroke-width="1.5" rx="6"/>
    <text x="425" y="95" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">1. Читання seq1 з vvar.seq</text>
    
    <!-- Step 2: Check sequence odd/even -->
    <polygon points="425,140 565,185 425,230 285,185" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
    <text x="425" y="180" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#92400e" text-anchor="middle">seq1 непарне?</text>
    <text x="425" y="198" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="11" fill="#b45309" text-anchor="middle">(Ядро саме зараз пише?)</text>
    
    <!-- Loop if odd -->
    <path d="M 565 185 L 630 185 L 630 90 L 580 90" fill="none" stroke="#d97706" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow-amber)"/>
    <text x="670" y="140" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#d97706">Так (Spin)</text>
    
    <!-- Step 3: Read hardware TSC & calculate time -->
    <rect x="275" y="260" width="300" height="60" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" rx="6"/>
    <text x="425" y="285" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#0369a1" text-anchor="middle">2. Читання rdtsc() та значень vvar</text>
    <text x="425" y="307" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="#075985" text-anchor="middle">Обчислення: base_time + (cycles * mult &gt;&gt; shift)</text>
    
    <path d="M 425 230 L 425 260" fill="none" stroke="#0284c7" stroke-width="2" marker-end="url(#arrow-blue)"/>
    <text x="435" y="248" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#0284c7">Ні</text>
    
    <!-- Step 4: Read seq2 & compare -->
    <rect x="275" y="350" width="300" height="50" fill="#f1f5f9" stroke="#475569" stroke-width="1.5" rx="6"/>
    <text x="425" y="380" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#0f172a" text-anchor="middle">3. Читання seq2 з vvar.seq</text>
    
    <path d="M 425 320 L 425 350" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow-dark)"/>
    
    <!-- Step 5: Check seq1 == seq2 -->
    <polygon points="425,420 545,455 425,490 305,455" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
    <text x="425" y="452" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#15803d" text-anchor="middle">seq1 == seq2?</text>
    <text x="425" y="468" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="11" fill="#166534" text-anchor="middle">(Дані консистентні?)</text>
    
    <path d="M 425 400 L 425 420" fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
    
    <!-- Loop if seq1 != seq2 -->
    <path d="M 305 455 L 170 455 L 170 90 L 270 90" fill="none" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow-red)"/>
    <text x="130" y="275" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#dc2626">Ні (Повтор)</text>
    
    <!-- Success Output -->
    <path d="M 545 455 L 680 455" fill="none" stroke="#16a34a" stroke-width="2.5" marker-end="url(#arrow-green)"/>
    <text x="610" y="445" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#15803d">Так</text>
    
    <rect x="685" y="430" width="140" height="50" fill="#15803d" rx="6"/>
    <text x="755" y="460" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">Повернути час</text>

    <!-- Markers -->
    <defs>
        <marker id="arrow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#d97706"/>
        </marker>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#0284c7"/>
        </marker>
        <marker id="arrow-dark" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569"/>
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#16a34a"/>
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/>
        </marker>
    </defs>
</svg>"""

    with open(os.path.join(img_dir, "vdso-vs-syscall.svg"), "w", encoding="utf-8") as f:
        f.write(svg1)
    
    with open(os.path.join(img_dir, "vdso-memory-layout.svg"), "w", encoding="utf-8") as f:
        f.write(svg2)
        
    with open(os.path.join(img_dir, "vdso-seqlock-flow.svg"), "w", encoding="utf-8") as f:
        f.write(svg3)

if __name__ == "__main__":
    render()
