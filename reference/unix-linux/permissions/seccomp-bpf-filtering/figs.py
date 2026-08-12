import os
import sys

# Ensure scripts directory is in path to import svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../scripts")))

try:
    import svgkit
except ImportError:
    svgkit = None

def render():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "seccomp-arch.svg")
    
    if svgkit:
        elements = [
            # Background frame
            svgkit.rect(10, 10, 780, 380, fill="#f9fafb", stroke="#d1d5db", sw=1, rx=8),
            svgkit.text(400, 38, "Архітектура та потік виконання Seccomp-BPF у ядрі Linux", anchor="middle", size=17, bold=True, color="#111827"),

            # User Space Box
            svgkit.rect(30, 65, 230, 290, fill="#eff6ff", stroke="#3b82f6", sw=2, rx=6),
            svgkit.text(145, 92, "Простір користувача", anchor="middle", size=15, bold=True, color="#1e40af"),
            svgkit.text(145, 112, "(User Space)", anchor="middle", size=12, color="#3b82f6"),

            svgkit.rect(45, 135, 200, 50, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4),
            svgkit.text(145, 157, "Додаток / Контейнер", anchor="middle", size=13, bold=True, color="#1e3a8a"),
            svgkit.text(145, 173, "glibc wrapper / syscall()", anchor="middle", size=11, color="#4b5563"),

            svgkit.rect(45, 210, 200, 60, fill="#ffffff", stroke="#93c5fd", sw=1, rx=4),
            svgkit.text(145, 232, "Інструкція syscall", anchor="middle", size=13, bold=True, color="#1e3a8a"),
            svgkit.text(145, 252, "RAX=nr, RDI..R8=args", anchor="middle", size=11, color="#6b7280"),

            # Arrow User -> Kernel
            svgkit.arrow(260, 240, 315, 240, color="#1d4ed8", sw=2),
            svgkit.text(287, 230, "Syscall Trap", anchor="middle", size=11, color="#1d4ed8", bold=True),

            # Kernel Space Box
            svgkit.rect(320, 65, 450, 290, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=6),
            svgkit.text(545, 92, "Простір ядра Linux (Kernel Space)", anchor="middle", size=15, bold=True, color="#15803d"),

            # System Call Entry
            svgkit.rect(340, 115, 190, 45, fill="#ffffff", stroke="#86efac", sw=1, rx=4),
            svgkit.text(435, 135, "do_syscall_64()", anchor="middle", size=13, bold=True, color="#166534"),
            svgkit.text(435, 150, "Формування seccomp_data", anchor="middle", size=11, color="#4b5563"),

            # Arrow to Seccomp Filter
            svgkit.arrow(435, 160, 435, 190, color="#15803d", sw=2),

            # BPF Evaluator Box
            svgkit.rect(340, 190, 190, 75, fill="#dcfce7", stroke="#16a34a", sw=2, rx=4),
            svgkit.text(435, 212, "cBPF / JIT Evaluator", anchor="middle", size=13, bold=True, color="#14532d"),
            svgkit.text(435, 230, "Перевірка arch & nr", anchor="middle", size=11, color="#15803d"),
            svgkit.text(435, 248, "Аналіз args[6] (values)", anchor="middle", size=11, color="#15803d"),

            # Action evaluation arrow right
            svgkit.arrow(530, 227, 575, 227, color="#16a34a", sw=2),
            svgkit.text(552, 217, "Return", anchor="middle", size=11, color="#16a34a", bold=True),

            # Action Box
            svgkit.rect(580, 115, 175, 225, fill="#ffffff", stroke="#bbf7d0", sw=1, rx=4),
            svgkit.text(667, 137, "Дія (Return Code)", anchor="middle", size=13, bold=True, color="#166534"),

            svgkit.rect(592, 152, 150, 30, fill="#d1fae5", stroke="#10b981", sw=1, rx=3),
            svgkit.text(667, 171, "SECCOMP_RET_ALLOW", anchor="middle", size=11, bold=True, color="#065f46"),

            svgkit.rect(592, 188, 150, 30, fill="#fef3c7", stroke="#f59e0b", sw=1, rx=3),
            svgkit.text(667, 207, "SECCOMP_RET_ERRNO", anchor="middle", size=11, bold=True, color="#92400e"),

            svgkit.rect(592, 224, 150, 30, fill="#e0e7ff", stroke="#6366f1", sw=1, rx=3),
            svgkit.text(667, 243, "SECCOMP_RET_USER_NOTIF", anchor="middle", size=11, bold=True, color="#3730a3"),

            svgkit.rect(592, 260, 150, 30, fill="#fee2e2", stroke="#ef4444", sw=1, rx=3),
            svgkit.text(667, 279, "SECCOMP_RET_KILL_PROCESS", anchor="middle", size=11, bold=True, color="#991b1b"),

            svgkit.text(667, 320, "Системний виклик або вбито", anchor="middle", size=11, color="#6b7280")
        ]
        svgkit.render(out_path, 800, 400, *elements)
        print("Generated SVG using svgkit successfully.")
    else:
        # Fallback raw SVG with explicit viewBox
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
    <rect x="10" y="10" width="780" height="380" fill="#f9fafb" stroke="#d1d5db" stroke-width="1" rx="8"/>
    <text x="400" y="38" font-family="sans-serif" font-size="17" text-anchor="middle" font-weight="bold" fill="#111827">Архітектура та потік виконання Seccomp-BPF у ядрі Linux</text>
    <rect x="30" y="65" width="230" height="290" fill="#eff6ff" stroke="#3b82f6" stroke-width="2" rx="6"/>
    <text x="145" y="92" font-family="sans-serif" font-size="15" text-anchor="middle" font-weight="bold" fill="#1e40af">Простір користувача</text>
    <text x="145" y="112" font-family="sans-serif" font-size="12" text-anchor="middle" fill="#3b82f6">(User Space)</text>
    <rect x="45" y="135" width="200" height="50" fill="#ffffff" stroke="#93c5fd" stroke-width="1" rx="4"/>
    <text x="145" y="157" font-family="sans-serif" font-size="13" text-anchor="middle" font-weight="bold" fill="#1e3a8a">Додаток / Контейнер</text>
    <text x="145" y="173" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#4b5563">glibc wrapper / syscall()</text>
    <rect x="45" y="210" width="200" height="60" fill="#ffffff" stroke="#93c5fd" stroke-width="1" rx="4"/>
    <text x="145" y="232" font-family="sans-serif" font-size="13" text-anchor="middle" font-weight="bold" fill="#1e3a8a">Інструкція syscall</text>
    <text x="145" y="252" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#6b7280">RAX=nr, RDI..R8=args</text>
    <path d="M 260 240 L 315 240" stroke="#1d4ed8" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="287" y="230" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#1d4ed8" font-weight="bold">Syscall Trap</text>
    <rect x="320" y="65" width="450" height="290" fill="#f0fdf4" stroke="#22c55e" stroke-width="2" rx="6"/>
    <text x="545" y="92" font-family="sans-serif" font-size="15" text-anchor="middle" font-weight="bold" fill="#15803d">Простір ядра Linux (Kernel Space)</text>
    <rect x="340" y="115" width="190" height="45" fill="#ffffff" stroke="#86efac" stroke-width="1" rx="4"/>
    <text x="435" y="135" font-family="sans-serif" font-size="13" text-anchor="middle" font-weight="bold" fill="#166534">do_syscall_64()</text>
    <text x="435" y="150" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#4b5563">Формування seccomp_data</text>
    <path d="M 435 160 L 435 190" stroke="#15803d" stroke-width="2" marker-end="url(#arrow-green)"/>
    <rect x="340" y="190" width="190" height="75" fill="#dcfce7" stroke="#16a34a" stroke-width="2" rx="4"/>
    <text x="435" y="212" font-family="sans-serif" font-size="13" text-anchor="middle" font-weight="bold" fill="#14532d">cBPF / JIT Evaluator</text>
    <text x="435" y="230" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#15803d">Перевірка arch &amp; nr</text>
    <text x="435" y="248" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#15803d">Аналіз args[6] (values)</text>
    <path d="M 530 227 L 575 227" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
    <text x="552" y="217" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#16a34a" font-weight="bold">Return</text>
    <rect x="580" y="115" width="175" height="225" fill="#ffffff" stroke="#bbf7d0" stroke-width="1" rx="4"/>
    <text x="667" y="137" font-family="sans-serif" font-size="13" text-anchor="middle" font-weight="bold" fill="#166534">Дія (Return Code)</text>
    <rect x="592" y="152" width="150" height="30" fill="#d1fae5" stroke="#10b981" stroke-width="1" rx="3"/>
    <text x="667" y="171" font-family="sans-serif" font-size="11" text-anchor="middle" font-weight="bold" fill="#065f46">SECCOMP_RET_ALLOW</text>
    <rect x="592" y="188" width="150" height="30" fill="#fef3c7" stroke="#f59e0b" stroke-width="1" rx="3"/>
    <text x="667" y="207" font-family="sans-serif" font-size="11" text-anchor="middle" font-weight="bold" fill="#92400e">SECCOMP_RET_ERRNO</text>
    <rect x="592" y="224" width="150" height="30" fill="#e0e7ff" stroke="#6366f1" stroke-width="1" rx="3"/>
    <text x="667" y="243" font-family="sans-serif" font-size="11" text-anchor="middle" font-weight="bold" fill="#3730a3">SECCOMP_RET_USER_NOTIF</text>
    <rect x="592" y="260" width="150" height="30" fill="#fee2e2" stroke="#ef4444" stroke-width="1" rx="3"/>
    <text x="667" y="279" font-family="sans-serif" font-size="11" text-anchor="middle" font-weight="bold" fill="#991b1b">SECCOMP_RET_KILL_PROCESS</text>
    <text x="667" y="320" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#6b7280">Системний виклик або вбито</text>
    <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 z" fill="#1d4ed8" />
        </marker>
        <marker id="arrow-green" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 z" fill="#16a34a" />
        </marker>
    </defs>
</svg>"""
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print("Generated SVG fallback successfully.")

if __name__ == "__main__":
    render()
