import os

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    # 1. Pipeline architecture of man rendering
    svg1 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 480" width="920" height="480">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <!-- Title -->
    <text x="460" y="32" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="18" font-weight="bold" fill="#0f172a" text-anchor="middle">Конвеєр обробки та візуалізації сторінок man</text>
    
    <!-- Step 1: Storage -->
    <rect x="30" y="65" width="200" height="150" fill="#f8fafc" stroke="#64748b" stroke-width="1.5" rx="8"/>
    <text x="130" y="92" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#334155" text-anchor="middle">1. Файлова система</text>
    <rect x="45" y="108" width="170" height="42" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1" rx="4"/>
    <text x="130" y="126" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#0f172a" text-anchor="middle">/usr/share/man/</text>
    <text x="130" y="142" font-family="Consolas, monospace" font-size="11" fill="#475569" text-anchor="middle">man2/read.2.gz</text>
    <text x="130" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#64748b" text-anchor="middle">Стиснений вихідний текст</text>
    <text x="130" y="188" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#64748b" text-anchor="middle">з макросами roff / mdoc</text>

    <!-- Step 2: Formatter / Engine -->
    <rect x="260" y="65" width="200" height="150" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5" rx="8"/>
    <text x="360" y="92" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#1d4ed8" text-anchor="middle">2. Форматер (Engine)</text>
    <rect x="275" y="108" width="170" height="42" fill="#dbeafe" stroke="#60a5fa" stroke-width="1" rx="4"/>
    <text x="360" y="126" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#1e40af" text-anchor="middle">mandoc / groff</text>
    <text x="360" y="142" font-family="Consolas, monospace" font-size="10" fill="#2563eb" text-anchor="middle">troff -Tutf8 -mandoc</text>
    <text x="360" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">Розпакування gzip,</text>
    <text x="360" y="188" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">побудова AST та верстка</text>

    <!-- Step 3: Terminal Device Driver -->
    <rect x="490" y="65" width="190" height="150" fill="#fef3c7" stroke="#d97706" stroke-width="1.5" rx="8"/>
    <text x="585" y="92" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#b45309" text-anchor="middle">3. Драйвер пристрою</text>
    <rect x="505" y="108" width="160" height="42" fill="#fde68a" stroke="#f59e0b" stroke-width="1" rx="4"/>
    <text x="585" y="126" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#92400e" text-anchor="middle">grotty / mandoc-term</text>
    <text x="585" y="142" font-family="Consolas, monospace" font-size="10" fill="#b45309" text-anchor="middle">ANSI SGR / Overstrike</text>
    <text x="585" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#78350f" text-anchor="middle">Ґенерація escape-кодів:</text>
    <text x="585" y="188" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#78350f" text-anchor="middle">жирний (\\e[1m), підкреслення</text>

    <!-- Step 4: Pager & TTY -->
    <rect x="710" y="65" width="180" height="150" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5" rx="8"/>
    <text x="800" y="92" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#047857" text-anchor="middle">4. Пейджер / Термінал</text>
    <rect x="725" y="108" width="150" height="42" fill="#d1fae5" stroke="#34d399" stroke-width="1" rx="4"/>
    <text x="800" y="126" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#065f46" text-anchor="middle">less -R (PAGER)</text>
    <text x="800" y="142" font-family="Consolas, monospace" font-size="10" fill="#047857" text-anchor="middle">Термінальний емулятор</text>
    <text x="800" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#065f46" text-anchor="middle">Посторінкова навігація,</text>
    <text x="800" y="188" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#065f46" text-anchor="middle">підсвітка пошуку (/)</text>

    <!-- Horizontal Arrows -->
    <path d="M 230 140 L 260 140" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arrow-slate)"/>
    <path d="M 460 140 L 490 140" fill="none" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrow-blue)"/>
    <path d="M 680 140 L 710 140" fill="none" stroke="#d97706" stroke-width="2" marker-end="url(#arrow-amber)"/>

    <!-- Bottom Branch: Database Indexing for apropos / whatis -->
    <rect x="130" y="270" width="660" height="175" fill="#f8fafc" stroke="#475569" stroke-width="1.5" stroke-dasharray="6,4" rx="10"/>
    <text x="460" y="295" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="14" font-weight="bold" fill="#1e293b" text-anchor="middle">Паралельна підсистема індексації та швидкого пошуку: mandb / whatis</text>
    
    <!-- Sub-box 1: Parser -->
    <rect x="155" y="315" width="180" height="105" fill="#ffffff" stroke="#94a3b8" stroke-width="1" rx="6"/>
    <text x="245" y="338" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">mandb / makewhatis</text>
    <text x="245" y="358" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">Сканування секцій .SH NAME</text>
    <text x="245" y="375" font-family="Consolas, monospace" font-size="10" fill="#2563eb" text-anchor="middle">"read, readv - read from fd"</text>
    <text x="245" y="398" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#64748b" text-anchor="middle">Фонове оновлення cron/timer</text>

    <!-- Sub-box 2: DB Cache -->
    <rect x="370" y="315" width="180" height="105" fill="#ffffff" stroke="#94a3b8" stroke-width="1" rx="6"/>
    <text x="460" y="338" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">Індексна база даних</text>
    <text x="460" y="358" font-family="Consolas, monospace" font-size="10" fill="#0f172a" text-anchor="middle">/var/cache/man/index.db</text>
    <text x="460" y="378" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#475569" text-anchor="middle">GDBM / Berkeley DB хеш-таблиця</text>
    <text x="460" y="398" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#64748b" text-anchor="middle">Ключ: ім'я, Значення: рядок опису</text>

    <!-- Sub-box 3: Search CLI -->
    <rect x="585" y="315" width="180" height="105" fill="#f0fdf4" stroke="#16a34a" stroke-width="1" rx="6"/>
    <text x="675" y="338" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#15803d" text-anchor="middle">Інтерфейс запитів</text>
    <text x="675" y="358" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#166534" text-anchor="middle">apropos &lt;ключ&gt; / man -k</text>
    <text x="675" y="376" font-family="Consolas, monospace" font-size="11" fill="#166534" text-anchor="middle">whatis &lt;ім'я&gt; / man -f</text>
    <text x="675" y="398" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#15803d" text-anchor="middle">Миттєвий пошук без I/O диска</text>

    <!-- DB Arrows -->
    <path d="M 130 215 L 130 367 L 155 367" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arrow-slate)"/>
    <path d="M 335 367 L 370 367" fill="none" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow-slate)"/>
    <path d="M 550 367 L 585 367" fill="none" stroke="#16a34a" stroke-width="1.5" marker-end="url(#arrow-green)"/>

    <!-- Marker Definitions -->
    <defs>
        <marker id="arrow-slate" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/>
        </marker>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6"/>
        </marker>
        <marker id="arrow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#d97706"/>
        </marker>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#16a34a"/>
        </marker>
    </defs>
</svg>"""

    # 2. Synopsis Grammar Breakdown
    svg2 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 520" width="960" height="520">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <!-- Title -->
    <text x="480" y="32" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="18" font-weight="bold" fill="#0f172a" text-anchor="middle">Граматичні домовленості розділу SYNOPSIS</text>
    
    <!-- Example 1: CLI command syntax -->
    <rect x="25" y="55" width="910" height="215" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" rx="8"/>
    <text x="45" y="80" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#1e293b">1. Команди оболонки (Розділи 1 та 8)</text>
    
    <!-- Code Box -->
    <rect x="45" y="95" width="870" height="40" fill="#0f172a" rx="6"/>
    <text x="65" y="121" font-family="Consolas, monospace" font-size="15" fill="#ffffff">
        <tspan x="65" fill="#38bdf8" font-weight="bold">tar</tspan>
        <tspan x="115" fill="#f59e0b" font-weight="bold">{ -c | -x | -t }</tspan>
        <tspan x="290" fill="#94a3b8">[</tspan>
        <tspan x="300" fill="#f59e0b" font-weight="bold">-v</tspan>
        <tspan x="320" fill="#94a3b8">]</tspan>
        <tspan x="345" fill="#94a3b8">[</tspan>
        <tspan x="355" fill="#f59e0b" font-weight="bold">-f</tspan>
        <tspan x="380" fill="#4ade80" font-style="italic">ARCHIVE</tspan>
        <tspan x="445" fill="#94a3b8">]</tspan>
        <tspan x="475" fill="#94a3b8">[</tspan>
        <tspan x="485" fill="#4ade80" font-style="italic">FILE</tspan>
        <tspan x="520" fill="#fbbf24">...</tspan>
        <tspan x="545" fill="#94a3b8">]</tspan>
    </text>

    <!-- Annotations for CLI: 5 clear horizontal cards -->
    <!-- Card 1: tar -->
    <rect x="45" y="150" width="140" height="105" fill="#ffffff" stroke="#0284c7" stroke-width="1.5" rx="6"/>
    <text x="115" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#0369a1" text-anchor="middle">Жирний шрифт</text>
    <text x="115" y="195" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#0284c7" text-anchor="middle">tar, -c, -v</text>
    <text x="115" y="218" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">Дослівні назви,</text>
    <text x="115" y="234" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">команди й ключі</text>

    <!-- Card 2: { | } -->
    <rect x="200" y="150" width="165" height="105" fill="#ffffff" stroke="#d97706" stroke-width="1.5" rx="6"/>
    <text x="282" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#b45309" text-anchor="middle">Дужки { a | b }</text>
    <text x="282" y="195" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#d97706" text-anchor="middle">{ -c | -x | -t }</text>
    <text x="282" y="218" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">Виключний вибір:</text>
    <text x="282" y="234" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">рівно один варіант</text>

    <!-- Card 3: [ ] -->
    <rect x="380" y="150" width="160" height="105" fill="#ffffff" stroke="#64748b" stroke-width="1.5" rx="6"/>
    <text x="460" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#334155" text-anchor="middle">Квадратні дужки [ ]</text>
    <text x="460" y="195" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#475569" text-anchor="middle">[-v], [-f ARCHIVE]</text>
    <text x="460" y="218" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">Опційний блок:</text>
    <text x="460" y="234" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">можна опустити</text>

    <!-- Card 4: Italic -->
    <rect x="555" y="150" width="170" height="105" fill="#ffffff" stroke="#16a34a" stroke-width="1.5" rx="6"/>
    <text x="640" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#15803d" text-anchor="middle">Курсив / Підкреслення</text>
    <text x="640" y="195" font-family="Consolas, monospace" font-size="11" font-style="italic" fill="#16a34a" text-anchor="middle">ARCHIVE, FILE</text>
    <text x="640" y="218" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">Змінний параметр:</text>
    <text x="640" y="234" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">значення користувача</text>

    <!-- Card 5: ... -->
    <rect x="740" y="150" width="175" height="105" fill="#ffffff" stroke="#eab308" stroke-width="1.5" rx="6"/>
    <text x="827" y="172" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#a16207" text-anchor="middle">Трикрапка ...</text>
    <text x="827" y="195" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#ca8a04" text-anchor="middle">FILE...</text>
    <text x="827" y="218" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">Повторюваність:</text>
    <text x="827" y="234" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">1 або більше аргументів</text>

    <!-- Example 2: C API Signature -->
    <rect x="25" y="285" width="910" height="215" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5" rx="8"/>
    <text x="45" y="310" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#1e293b">2. C Сигнатури системних та бібліотечних викликів (Розділи 2 та 3)</text>
    
    <!-- Code Box for C -->
    <rect x="45" y="325" width="870" height="40" fill="#0f172a" rx="6"/>
    <text x="65" y="350" font-family="Consolas, monospace" font-size="14" fill="#ffffff">
        <tspan x="65" fill="#c084fc">ssize_t</tspan>
        <tspan x="135" fill="#38bdf8" font-weight="bold">read</tspan>
        <tspan x="175" fill="#ffffff">(</tspan>
        <tspan x="185" fill="#c084fc">int</tspan>
        <tspan x="218" fill="#4ade80" font-style="italic">fd</tspan>
        <tspan x="238" fill="#ffffff">, </tspan>
        <tspan x="255" fill="#c084fc">void</tspan>
        <tspan x="290" fill="#ffffff">*</tspan>
        <tspan x="300" fill="#4ade80" font-style="italic">buf</tspan>
        <tspan x="328" fill="#ffffff">, </tspan>
        <tspan x="345" fill="#c084fc">size_t</tspan>
        <tspan x="398" fill="#4ade80" font-style="italic">count</tspan>
        <tspan x="442" fill="#ffffff">);</tspan>
    </text>

    <!-- C API Cards: 4 structured cards -->
    <!-- C Card 1: Return Type -->
    <rect x="45" y="380" width="195" height="105" fill="#ffffff" stroke="#9333ea" stroke-width="1.5" rx="6"/>
    <text x="142" y="402" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#7e22ce" text-anchor="middle">Тип повернення ssize_t</text>
    <text x="142" y="425" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#15803d" font-weight="bold" text-anchor="middle">≥ 0: успішно (к-ть байтів)</text>
    <text x="142" y="445" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#dc2626" font-weight="bold" text-anchor="middle">-1: помилка (див. errno)</text>
    <text x="142" y="465" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">0 = кінець файлу (EOF)</text>

    <!-- C Card 2: Function Name -->
    <rect x="255" y="380" width="180" height="105" fill="#ffffff" stroke="#0284c7" stroke-width="1.5" rx="6"/>
    <text x="345" y="402" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#0369a1" text-anchor="middle">Ім'я функції: read</text>
    <text x="345" y="425" font-family="Consolas, monospace" font-size="11" font-weight="bold" fill="#0284c7" text-anchor="middle">read(2)</text>
    <text x="345" y="448" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">Системний виклик POSIX</text>
    <text x="345" y="465" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">Точка входу в ядро ОС</text>

    <!-- C Card 3: Parameters -->
    <rect x="450" y="380" width="225" height="105" fill="#ffffff" stroke="#16a34a" stroke-width="1.5" rx="6"/>
    <text x="562" y="402" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#15803d" text-anchor="middle">Параметри виклику</text>
    <text x="562" y="423" font-family="Consolas, monospace" font-size="10" fill="#166534" text-anchor="middle">int fd, void *buf, size_t count</text>
    <text x="562" y="445" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">fd: відкритий дескриптор</text>
    <text x="562" y="465" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">buf: ціль, count: ліміт байтів</text>

    <!-- C Card 4: Headers & Requirements -->
    <rect x="690" y="380" width="225" height="105" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5" rx="6"/>
    <text x="802" y="402" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#1d4ed8" text-anchor="middle">Вимоги до коду</text>
    <text x="802" y="423" font-family="Consolas, monospace" font-size="10" font-weight="bold" fill="#1e40af" text-anchor="middle">#include &lt;unistd.h&gt;</text>
    <text x="802" y="445" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">Стандарт: POSIX.1-2001,</text>
    <text x="802" y="465" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="10" fill="#475569" text-anchor="middle">POSIX.1-2008, SVr4, 4.3BSD</text>
</svg>"""

    # 3. Section collision resolution
    svg3 = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 480" width="920" height="480">
    <rect width="100%" height="100%" fill="#ffffff"/>
    
    <!-- Title -->
    <text x="460" y="32" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="18" font-weight="bold" fill="#0f172a" text-anchor="middle">Розв'язання колізій імен та порядок пошуку за розділами man</text>
    
    <!-- User Input Box -->
    <rect x="50" y="65" width="230" height="80" fill="#0f172a" rx="8"/>
    <text x="70" y="98" font-family="Consolas, monospace" font-size="14" fill="#94a3b8">$ <tspan fill="#38bdf8" font-weight="bold">man read</tspan></text>
    <text x="70" y="124" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#cbd5e1">Запит без вказівки номера розділу</text>

    <!-- Search Engine Order -->
    <rect x="330" y="65" width="540" height="80" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" rx="8"/>
    <text x="350" y="92" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#334155">Стандартний порядок перегляду розділів (SECTION_LIST):</text>
    
    <g font-family="Consolas, monospace" font-size="12" font-weight="bold">
        <!-- 1 -->
        <rect x="350" y="103" width="36" height="26" fill="#0284c7" rx="4"/>
        <text x="368" y="121" fill="#ffffff" text-anchor="middle">1</text>
        <text x="393" y="121" fill="#64748b">→</text>
        
        <!-- n -->
        <rect x="408" y="103" width="36" height="26" fill="#e2e8f0" rx="4"/>
        <text x="426" y="121" fill="#475569" text-anchor="middle">n</text>
        <text x="451" y="121" fill="#64748b">→</text>
        
        <!-- l -->
        <rect x="466" y="103" width="36" height="26" fill="#e2e8f0" rx="4"/>
        <text x="484" y="121" fill="#475569" text-anchor="middle">l</text>
        <text x="509" y="121" fill="#64748b">→</text>
        
        <!-- 8 -->
        <rect x="524" y="103" width="36" height="26" fill="#e2e8f0" rx="4"/>
        <text x="542" y="121" fill="#475569" text-anchor="middle">8</text>
        <text x="567" y="121" fill="#64748b">→</text>
        
        <!-- 3 -->
        <rect x="582" y="103" width="36" height="26" fill="#e2e8f0" rx="4"/>
        <text x="600" y="121" fill="#475569" text-anchor="middle">3</text>
        <text x="625" y="121" fill="#64748b">→</text>
        
        <!-- 2 -->
        <rect x="640" y="103" width="36" height="26" fill="#e2e8f0" rx="4"/>
        <text x="658" y="121" fill="#475569" text-anchor="middle">2</text>
        <text x="683" y="121" fill="#64748b">→</text>
        
        <!-- 5, 4, 7... -->
        <rect x="698" y="103" width="50" height="26" fill="#e2e8f0" rx="4"/>
        <text x="723" y="121" fill="#475569" text-anchor="middle">5,4,7</text>
    </g>

    <!-- Arrow from query to search -->
    <path d="M 280 105 L 330 105" fill="none" stroke="#0284c7" stroke-width="2" marker-end="url(#arrow-blue)"/>

    <!-- 3 Target Candidates for 'read' -->
    <!-- Candidate 1: Section 1 (Matched first!) -->
    <rect x="50" y="190" width="250" height="250" fill="#f0f9ff" stroke="#0284c7" stroke-width="2" rx="8"/>
    <rect x="65" y="205" width="220" height="30" fill="#0284c7" rx="4"/>
    <text x="175" y="225" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">Розділ 1: Команди оболонки</text>
    <text x="175" y="258" font-family="Consolas, monospace" font-size="14" font-weight="bold" fill="#0369a1" text-anchor="middle">read(1) [builtins]</text>
    <text x="75" y="285" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#334155">Вбудована команда Bash:</text>
    <text x="75" y="302" font-family="Consolas, monospace" font-size="11" fill="#0284c7">read [-ers] [-u fd] [name ...]</text>
    <text x="75" y="325" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#64748b">Зчитує рядок зі stdin у змінну</text>
    
    <rect x="65" y="355" width="220" height="65" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5" rx="4"/>
    <text x="175" y="378" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" fill="#15803d" text-anchor="middle">✓ Знайдено першим!</text>
    <text x="175" y="398" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#166534" text-anchor="middle">Відкриється за замовчуванням</text>

    <!-- Candidate 2: Section 2 (Kernel Syscall) -->
    <rect x="335" y="190" width="250" height="250" fill="#fff7ed" stroke="#ea580c" stroke-width="1.5" rx="8"/>
    <rect x="350" y="205" width="220" height="30" fill="#ea580c" rx="4"/>
    <text x="460" y="225" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">Розділ 2: Системні виклики</text>
    <text x="460" y="258" font-family="Consolas, monospace" font-size="14" font-weight="bold" fill="#c2410c" text-anchor="middle">read(2)</text>
    <text x="360" y="285" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#334155">Системний виклик ядра:</text>
    <text x="360" y="302" font-family="Consolas, monospace" font-size="11" fill="#c2410c">read(int fd, void *buf, ...)</text>
    <text x="360" y="325" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#64748b">Перемикання Ring 3 → Ring 0,</text>
    <text x="360" y="342" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#64748b">зчитування сирих байтів</text>

    <rect x="350" y="365" width="220" height="55" fill="#ffedd5" stroke="#f97316" stroke-width="1" rx="4"/>
    <text x="460" y="388" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#9a3412" text-anchor="middle">Явний виклик розробника:</text>
    <text x="460" y="406" font-family="Consolas, monospace" font-size="12" font-weight="bold" fill="#ea580c" text-anchor="middle">man 2 read</text>

    <!-- Candidate 3: Section 3 (Library functions) -->
    <rect x="620" y="190" width="250" height="250" fill="#faf5ff" stroke="#9333ea" stroke-width="1.5" rx="8"/>
    <rect x="635" y="205" width="220" height="30" fill="#9333ea" rx="4"/>
    <text x="745" y="225" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="13" font-weight="bold" fill="#ffffff" text-anchor="middle">Розділ 3: Бібліотеки С</text>
    <text x="745" y="258" font-family="Consolas, monospace" font-size="14" font-weight="bold" fill="#7e22ce" text-anchor="middle">fread(3) / readline(3)</text>
    <text x="645" y="285" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#334155">Виклики простору користувача:</text>
    <text x="645" y="302" font-family="Consolas, monospace" font-size="11" fill="#7e22ce">fread(..., FILE *stream)</text>
    <text x="645" y="325" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#64748b">Буферизація stdio, історія</text>
    <text x="645" y="342" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" fill="#64748b">введення через GNU Readline</text>

    <rect x="635" y="365" width="220" height="55" fill="#f3e8ff" stroke="#a855f7" stroke-width="1" rx="4"/>
    <text x="745" y="388" font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="bold" fill="#6b21a8" text-anchor="middle">Явний виклик розробника:</text>
    <text x="745" y="406" font-family="Consolas, monospace" font-size="12" font-weight="bold" fill="#9333ea" text-anchor="middle">man 3 readline</text>

    <!-- Dispatch Paths from search box -->
    <path d="M 370 145 L 370 170 L 175 170 L 175 190" fill="none" stroke="#0284c7" stroke-width="2" marker-end="url(#arrow-blue)"/>
    <path d="M 660 145 L 660 170 L 460 170 L 460 190" fill="none" stroke="#ea580c" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arrow-orange)"/>
    <path d="M 600 145 L 600 170 L 745 170 L 745 190" fill="none" stroke="#9333ea" stroke-width="1.5" stroke-dasharray="4,4" marker-end="url(#arrow-purple)"/>

    <defs>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#0284c7"/>
        </marker>
        <marker id="arrow-orange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#ea580c"/>
        </marker>
        <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#9333ea"/>
        </marker>
    </defs>
</svg>"""

    with open(os.path.join(img_dir, "man-rendering-pipeline.svg"), "w", encoding="utf-8") as f:
        f.write(svg1)
    
    with open(os.path.join(img_dir, "synopsis-anatomy.svg"), "w", encoding="utf-8") as f:
        f.write(svg2)
        
    with open(os.path.join(img_dir, "section-collision-resolution.svg"), "w", encoding="utf-8") as f:
        f.write(svg3)

if __name__ == "__main__":
    render()
