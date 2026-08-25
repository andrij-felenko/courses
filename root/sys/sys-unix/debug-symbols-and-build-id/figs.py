import sys
import os

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import rect, line, arrow, text, mtext, fitbox, FONT, INK, FILL, MUTED, POS, NEG, FIELD

def render_elf_symbols():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "elf-symbols-and-strip.svg")

    w, h = 860, 500
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.append('<defs>')
    parts.append('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    parts.append('    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>')
    parts.append('  </marker>')
    parts.append('</defs>')
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 28, "Розподіл символів в ELF: оперативний бінарник, strip та debuginfo-файл", size=15, bold=True))

    # Box 1: Full Unstripped Binary (Left)
    parts.append(rect(30, 50, 250, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(155, 75, "Повний бінарник (-g)", size=13, bold=True, color="#1e293b"))
    parts.append(text(155, 93, "Розмір: ~85 МБ (диск)", size=11, color=MUTED))

    # Sections inside Box 1
    # Allocatable
    parts.append(rect(45, 110, 220, 36, fill="#dbeafe", stroke="#3b82f6", sw=1.2))
    parts.append(text(155, 126, ".text / .rodata / .data", size=11, bold=True, color="#1d4ed8"))
    parts.append(text(155, 139, "Код і глобальні дані (SHF_ALLOC)", size=9, color="#1e40af"))

    parts.append(rect(45, 152, 220, 38, fill="#dcfce7", stroke="#22c55e", sw=1.2))
    parts.append(text(155, 168, ".dynsym / .dynstr", size=11, bold=True, color="#15803d"))
    parts.append(text(155, 182, "Динамічні символи для ld.so (SHF_ALLOC)", size=9, color="#166534"))

    # Non-allocatable
    parts.append(rect(45, 196, 220, 42, fill="#fef3c7", stroke="#f59e0b", sw=1.2))
    parts.append(text(155, 212, ".symtab / .strtab", size=11, bold=True, color="#b45309"))
    parts.append(text(155, 228, "Повна таблиця імен (non-alloc)", size=9, color="#92400e"))

    parts.append(rect(45, 244, 220, 110, fill="#fee2e2", stroke="#ef4444", sw=1.2))
    parts.append(text(155, 264, "Секції DWARF (.debug_*)", size=11, bold=True, color="#b91c1c"))
    parts.append(text(155, 282, ".debug_info (типи, змінні, DIE)", size=9, color="#991b1b"))
    parts.append(text(155, 298, ".debug_line (номери рядків сирців)", size=9, color="#991b1b"))
    parts.append(text(155, 314, ".debug_loc / .debug_ranges", size=9, color="#991b1b"))
    parts.append(text(155, 330, ".debug_frame (CFI розгортання)", size=9, color="#991b1b"))

    parts.append(rect(45, 360, 220, 34, fill="#f1f5f9", stroke="#64748b", sw=1.2))
    parts.append(text(155, 376, ".note.gnu.build-id", size=11, bold=True, color="#334155"))
    parts.append(text(155, 388, "SHA-1 хеш збірки (SHF_ALLOC)", size=9, color="#475569"))

    parts.append(rect(45, 400, 220, 28, fill="#e2e8f0", stroke="#94a3b8", sw=1))
    parts.append(text(155, 418, "Section Header Table", size=10, color="#475569"))

    # Arrows for Strip and Split
    parts.append(arrow(280, 200, 325, 200, color="#d97706", sw=2))
    parts.append(text(302, 190, "strip", size=11, bold=True, color="#b45309"))

    parts.append(arrow(280, 320, 605, 320, color="#2563eb", sw=2))
    parts.append(text(442, 310, "objcopy --only-keep-debug", size=11, bold=True, color="#1d4ed8"))

    # Box 2: Stripped Binary (Middle)
    parts.append(rect(330, 50, 250, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(455, 75, "Очищений бінарник (Strip)", size=13, bold=True, color="#1e293b"))
    parts.append(text(455, 93, "Розмір: ~4.2 МБ (диск)", size=11, color=FIELD))

    parts.append(rect(345, 110, 220, 36, fill="#dbeafe", stroke="#3b82f6", sw=1.2))
    parts.append(text(455, 126, ".text / .rodata / .data", size=11, bold=True, color="#1d4ed8"))
    parts.append(text(455, 139, "Код і глобальні дані (SHF_ALLOC)", size=9, color="#1e40af"))

    parts.append(rect(345, 152, 220, 38, fill="#dcfce7", stroke="#22c55e", sw=1.2))
    parts.append(text(455, 168, ".dynsym / .dynstr", size=11, bold=True, color="#15803d"))
    parts.append(text(455, 182, "Збережено для динамічного лінкера", size=9, color="#166534"))

    parts.append(rect(345, 196, 220, 158, fill="#f3f4f6", stroke="#d1d5db", sw=1))
    parts.append(text(455, 268, "ВИДАЛЕНО УТИЛІТОЮ STRIP:", size=11, bold=True, color="#9ca3af"))
    parts.append(text(455, 288, "• .symtab / .strtab", size=10, color="#9ca3af"))
    parts.append(text(455, 306, "• Усі секції DWARF (.debug_*)", size=10, color="#9ca3af"))

    parts.append(rect(345, 360, 220, 34, fill="#f1f5f9", stroke="#64748b", sw=1.2))
    parts.append(text(455, 376, ".note.gnu.build-id", size=11, bold=True, color="#334155"))
    parts.append(text(455, 388, "Збережено: незмінний SHA-1", size=9, color="#475569"))

    parts.append(rect(345, 400, 220, 32, fill="#fef9c3", stroke="#ca8a04", sw=1.2))
    parts.append(text(455, 414, ".gnu_debuglink", size=10, bold=True, color="#854d0e"))
    parts.append(text(455, 426, "Ім'я debug-файлу + CRC32", size=9, color="#854d0e"))

    # Box 3: Detached Debug File (Right)
    parts.append(rect(610, 50, 220, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(720, 75, "Окремий .debug файл", size=13, bold=True, color="#1e293b"))
    parts.append(text(720, 93, "Розмір: ~81 МБ (debuginfo)", size=11, color="#2563eb"))

    parts.append(rect(620, 110, 200, 36, fill="#f1f5f9", stroke="#cbd5e1", sw=1))
    parts.append(text(720, 125, ".text / .data (NOBITS)", size=10, color=MUTED))
    parts.append(text(720, 138, "Заголовки є, дані 0 байт на диску", size=9, color=MUTED))

    parts.append(rect(620, 152, 200, 38, fill="#fef3c7", stroke="#f59e0b", sw=1.2))
    parts.append(text(720, 168, ".symtab / .strtab", size=11, bold=True, color="#b45309"))
    parts.append(text(720, 182, "Повна таблиця імен", size=9, color="#92400e"))

    parts.append(rect(620, 196, 200, 158, fill="#fee2e2", stroke="#ef4444", sw=1.2))
    parts.append(text(720, 216, "Повні секції DWARF", size=11, bold=True, color="#b91c1c"))
    parts.append(text(720, 236, "• .debug_info", size=10, color="#991b1b"))
    parts.append(text(720, 254, "• .debug_line", size=10, color="#991b1b"))
    parts.append(text(720, 272, "• .debug_loc / .debug_ranges", size=10, color="#991b1b"))
    parts.append(text(720, 290, "• .debug_frame", size=10, color="#991b1b"))
    parts.append(text(720, 308, "• .debug_str", size=10, color="#991b1b"))

    parts.append(rect(620, 360, 200, 34, fill="#f1f5f9", stroke="#64748b", sw=1.2))
    parts.append(text(720, 376, ".note.gnu.build-id", size=11, bold=True, color="#334155"))
    parts.append(text(720, 388, "Ідентичний SHA-1 збірки", size=9, color="#475569"))

    parts.append(rect(620, 400, 200, 28, fill="#e2e8f0", stroke="#94a3b8", sw=1))
    parts.append(text(720, 418, "Section Header Table", size=10, color="#475569"))

    parts.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

def render_build_id_resolution():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "build-id-and-debuglink.svg")

    w, h = 860, 480
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.append('<defs>')
    parts.append('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    parts.append('    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>')
    parts.append('  </marker>')
    parts.append('</defs>')
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 28, "Механізми пошуку символів налагоджувачем: .gnu_debuglink vs Build ID", size=15, bold=True))

    # Top: Executable binary
    parts.append(rect(240, 55, 380, 80, fill="#f8fafc", stroke="#3b82f6", sw=1.5, rx=8))
    parts.append(text(430, 78, "Виконуваний бінарник: /usr/bin/daemon", size=13, bold=True, color="#1e293b"))
    parts.append(rect(255, 92, 165, 34, fill="#fef9c3", stroke="#ca8a04", sw=1.2))
    parts.append(text(337, 107, ".gnu_debuglink", size=10, bold=True, color="#854d0e"))
    parts.append(text(337, 120, "daemon.debug + CRC32", size=9, color="#854d0e"))

    parts.append(rect(435, 92, 170, 34, fill="#e0e7ff", stroke="#4f46e5", sw=1.2))
    parts.append(text(520, 107, ".note.gnu.build-id", size=10, bold=True, color="#3730a3"))
    parts.append(text(520, 120, "SHA-1: 7a9f1b2c4d8e...", size=9, color="#3730a3"))

    # Branch Left: Debuglink Resolution
    parts.append(arrow(337, 135, 200, 180, color="#ca8a04", sw=2))
    parts.append(rect(30, 180, 360, 270, fill="#fffbeb", stroke="#f59e0b", sw=1.5, rx=8))
    parts.append(text(210, 204, "Шлях А: Пошук за назвою (.gnu_debuglink)", size=12, bold=True, color="#92400e"))

    parts.append(rect(45, 220, 330, 36, fill="#ffffff", stroke="#fbbf24", sw=1))
    parts.append(text(210, 235, "1. Поруч із бінарником:", size=10, bold=True, color="#78350f"))
    parts.append(text(210, 248, "/usr/bin/daemon.debug", size=9, color=MUTED))

    parts.append(rect(45, 264, 330, 36, fill="#ffffff", stroke="#fbbf24", sw=1))
    parts.append(text(210, 279, "2. У підкаталозі .debug/:", size=10, bold=True, color="#78350f"))
    parts.append(text(210, 292, "/usr/bin/.debug/daemon.debug", size=9, color=MUTED))

    parts.append(rect(45, 308, 330, 36, fill="#ffffff", stroke="#fbbf24", sw=1))
    parts.append(text(210, 323, "3. У глобальному /usr/lib/debug/:", size=10, bold=True, color="#78350f"))
    parts.append(text(210, 336, "/usr/lib/debug/usr/bin/daemon.debug", size=9, color=MUTED))

    parts.append(rect(45, 354, 330, 82, fill="#fef3c7", stroke="#d97706", sw=1))
    parts.append(text(210, 372, "Перевірка цілісності: CRC32", size=10, bold=True, color="#92400e"))
    parts.append(text(210, 390, "• Обчислюється CRC-32 знайденого файлу", size=9, color="#78350f"))
    parts.append(text(210, 406, "• Порівнюється зі значенням у секції", size=9, color="#78350f"))
    parts.append(text(210, 422, "Недолік: чутливий до зміни шляхів і назв", size=9, color=POS, italic=True))

    # Branch Right: Build-ID Resolution
    parts.append(arrow(520, 135, 660, 180, color="#4f46e5", sw=2))
    parts.append(rect(470, 180, 360, 270, fill="#eef2ff", stroke="#6366f1", sw=1.5, rx=8))
    parts.append(text(650, 204, "Шлях Б: Адресація за вмістом (Build ID)", size=12, bold=True, color="#3730a3"))

    parts.append(rect(485, 220, 330, 44, fill="#ffffff", stroke="#818cf8", sw=1))
    parts.append(text(650, 236, "1. Читання 160-бітного SHA-1 хешу:", size=10, bold=True, color="#312e81"))
    parts.append(text(650, 252, "Build ID = 7a9f1b2c4d8e3f015a...", size=9, color="#4338ca"))

    parts.append(rect(485, 272, 330, 48, fill="#ffffff", stroke="#818cf8", sw=1))
    parts.append(text(650, 288, "2. Прямий канонічний шлях у сховищі:", size=10, bold=True, color="#312e81"))
    parts.append(text(650, 302, "Каталог перших 2 символів хешу:", size=9, color=MUTED))
    parts.append(text(650, 314, "/usr/lib/debug/.build-id/7a/9f1b2c4d8e....debug", size=9, bold=True, color="#1e1b4b"))

    parts.append(rect(485, 330, 330, 106, fill="#e0e7ff", stroke="#4f46e5", sw=1))
    parts.append(text(650, 348, "Переваги Build-ID архітектури", size=10, bold=True, color="#3730a3"))
    parts.append(text(650, 366, "• Детермінованість: 1 біт змін у коді = інший хеш", size=9, color="#312e81"))
    parts.append(text(650, 382, "• Незалежність від шляхів, імен файлів та версій", size=9, color="#312e81"))
    parts.append(text(650, 398, "• Нульовий ризик завантаження чужих символів", size=9, color="#312e81"))
    parts.append(text(650, 414, "• Прямий ключ для мережевого запиту в debuginfod", size=9, color=FIELD, bold=True))

    parts.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

def render_debuginfod_workflow():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "debuginfod-workflow.svg")

    w, h = 860, 490
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.append('<defs>')
    parts.append('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    parts.append('    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>')
    parts.append('  </marker>')
    parts.append('</defs>')
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 28, "Клієнт-серверна архітектура debuginfod: завантаження символів на льоту", size=15, bold=True))

    # Column 1: Client Applications (Left)
    parts.append(rect(30, 55, 230, 410, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(145, 80, "Клієнтські утиліти", size=13, bold=True, color="#1e293b"))
    parts.append(text(145, 98, "Діагностика / Трасування", size=11, color=MUTED))

    tools = ["GDB / LLDB (Налагодження)", "perf / bpftrace (Профілювання)", "valgrind (Аналіз пам'яті)", "systemd-coredump (Аварії)"]
    for i, t_name in enumerate(tools):
        parts.append(rect(45, 115 + i * 44, 200, 36, fill="#ffffff", stroke="#cbd5e1", sw=1))
        parts.append(text(145, 137 + i * 44, t_name, size=10, bold=True, color="#334155"))

    # Shared libdebuginfod box
    parts.append(rect(45, 300, 200, 75, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=6))
    parts.append(text(145, 320, "libdebuginfod.so", size=12, bold=True, color="#1d4ed8"))
    parts.append(text(145, 338, "Клієнтська бібліотека C", size=9, color="#1e40af"))
    parts.append(text(145, 354, "Перевірка кешу + HTTP-запит", size=9, color="#1e40af"))

    parts.append(rect(45, 385, 200, 65, fill="#f1f5f9", stroke="#64748b", sw=1))
    parts.append(text(145, 403, "Змінна середовища:", size=9, color=MUTED))
    parts.append(text(145, 420, "DEBUGINFOD_URLS", size=10, bold=True, color="#0f172a"))
    parts.append(text(145, 436, "https://debuginfod.org ...", size=9, color="#0284c7"))

    # Column 2: Local Cache (Middle)
    parts.append(rect(300, 55, 230, 410, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=8))
    parts.append(text(415, 80, "Локальний клієнтський кеш", size=13, bold=True, color="#14532d"))
    parts.append(text(415, 98, "~/.cache/debuginfod_client/", size=10, color="#15803d"))

    parts.append(rect(315, 120, 200, 100, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    parts.append(text(415, 142, "Сховище за Build ID", size=11, bold=True, color="#166534"))
    parts.append(text(415, 162, "{buildid}/debuginfo", size=9, color="#15803d"))
    parts.append(text(415, 180, "{buildid}/executable", size=9, color="#15803d"))
    parts.append(text(415, 198, "{buildid}/source/...", size=9, color="#15803d"))

    parts.append(rect(315, 235, 200, 110, fill="#dcfce7", stroke="#22c55e", sw=1))
    parts.append(text(415, 255, "Правила кешування", size=10, bold=True, color="#14532d"))
    parts.append(text(415, 273, "• Позитивний кеш (файли DWARF)", size=9, color="#166534"))
    parts.append(text(415, 290, "• Негативний кеш (404 Not Found)", size=9, color="#166534"))
    parts.append(text(415, 308, "  захищає від повторних запитів", size=9, color="#15803d"))
    parts.append(text(415, 326, "• Автоматична ротація за TTL", size=9, color="#166534"))

    parts.append(rect(315, 360, 200, 90, fill="#ffffff", stroke="#86efac", sw=1))
    parts.append(text(415, 380, "Повернення FD дескриптора", size=10, bold=True, color="#15803d"))
    parts.append(text(415, 400, "libdebuginfod передає GDB", size=9, color="#14532d"))
    parts.append(text(415, 416, "відкритий файловий дескриптор", size=9, color="#14532d"))
    parts.append(text(415, 432, "кешованого DWARF-файлу", size=9, color="#14532d"))

    # Column 3: Server & Distro Archives (Right)
    parts.append(rect(570, 55, 260, 410, fill="#fdf4ff", stroke="#c084fc", sw=1.5, rx=8))
    parts.append(text(700, 80, "Серверна служба debuginfod", size=13, bold=True, color="#581c87"))
    parts.append(text(700, 98, "HTTP REST / Індексатор", size=11, color="#7e22ce"))

    parts.append(rect(585, 120, 230, 90, fill="#ffffff", stroke="#e9d5ff", sw=1.2, rx=6))
    parts.append(text(700, 140, "REST Ендпоїнти:", size=11, bold=True, color="#6b21a8"))
    parts.append(text(700, 160, "GET /buildid/{id}/debuginfo", size=9, bold=True, color="#7e22ce"))
    parts.append(text(700, 178, "GET /buildid/{id}/executable", size=9, bold=True, color="#7e22ce"))
    parts.append(text(700, 196, "GET /buildid/{id}/source/{path}", size=9, bold=True, color="#7e22ce"))

    parts.append(rect(585, 220, 230, 95, fill="#fae8ff", stroke="#d8b4fe", sw=1))
    parts.append(text(700, 240, "Джерела індексації (SQLite DB)", size=10, bold=True, color="#581c87"))
    parts.append(text(700, 260, "• Репозиторії пакунків RPM / DEB", size=9, color="#6b21a8"))
    parts.append(text(700, 276, "• Каталоги збірки / Koji / OBS", size=9, color="#6b21a8"))
    parts.append(text(700, 292, "• Сирцеві git-репозиторії", size=9, color="#6b21a8"))

    parts.append(rect(585, 325, 230, 125, fill="#ffffff", stroke="#e9d5ff", sw=1))
    parts.append(text(700, 345, "Федерація та проксі", size=10, bold=True, color="#581c87"))
    parts.append(text(700, 365, "• Локальний debuginfod проксує", size=9, color="#6b21a8"))
    parts.append(text(700, 381, "  запити до upstream дистрибутивів", size=9, color="#6b21a8"))
    parts.append(text(700, 400, "• Корпоративні приватні сервери", size=9, color="#6b21a8"))
    parts.append(text(700, 416, "  для власних мікросервісів", size=9, color="#6b21a8"))
    parts.append(text(700, 434, "• Розпакування архіву на льоту", size=9, color=FIELD, bold=True))

    # Flow arrows
    parts.append(arrow(245, 335, 300, 170, color="#2563eb", sw=1.8))
    parts.append(text(275, 240, "1. Кеш?", size=9, bold=True, color="#1d4ed8"))

    parts.append(arrow(415, 120, 570, 150, color="#7e22ce", sw=1.8))
    parts.append(text(495, 126, "2. HTTP GET", size=9, bold=True, color="#7e22ce"))

    parts.append(arrow(585, 185, 515, 185, color="#16a34a", sw=1.8))
    parts.append(text(550, 176, "3. ELF", size=9, bold=True, color="#15803d"))

    parts.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

if __name__ == "__main__":
    render_elf_symbols()
    render_build_id_resolution()
    render_debuginfod_workflow()
