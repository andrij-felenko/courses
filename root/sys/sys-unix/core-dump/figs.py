import sys
import os

# Add scripts directory to path to import svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def generate_core_flow():
    # viewBox width=850, height=520
    w_canvas, h_canvas = 850, 520
    svg_parts = []
    
    # Title
    svg_parts.append(text(425, 30, "Архітектура обробки аварійного дампа (Core Dump Flow)", size=18, bold=True))
    
    # Outer containers: User Space Top, Kernel Space Middle, Systemd / Storage Bottom
    svg_parts.append(rect(30, 55, 790, 110, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    svg_parts.append(text(790, 75, "User Space (Простір користувача)", size=12, color=MUTED, anchor="end", bold=True))
    
    svg_parts.append(rect(30, 180, 790, 135, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=8))
    svg_parts.append(text(790, 200, "Kernel Space (Ядро Linux)", size=12, color=MUTED, anchor="end", bold=True))
    
    svg_parts.append(rect(30, 350, 790, 145, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    svg_parts.append(text(790, 370, "Storage & Analysis", size=12, color=MUTED, anchor="end", bold=True))
    
    # Nodes in User Space Top
    b1, w1, h1 = textbox(160, 110, "Процес / Потік\n(SIGSEGV / SIGABRT)", size=12, fill="#fee2e2", stroke=POS, bold=True)
    svg_parts.append(b1)
    
    # Nodes in Kernel Space Middle
    b2, w2, h2 = textbox(160, 245, "do_coredump()\n1. zap_threads()\n2. RLIMIT_CORE check\n3. suid_dumpable check", size=11, fill="#e2e8f0", stroke="#475569")
    svg_parts.append(b2)
    
    b3, w3, h3 = textbox(445, 245, "/proc/sys/kernel/core_pattern\nПеревірка шаблону або pipe '|'", size=11, fill="#e0f2fe", stroke="#0284c7", bold=True)
    svg_parts.append(b3)
    
    # Nodes in Bottom Space
    b4, w4, h4 = textbox(340, 425, "Прямий запис у файл\n/var/coredumps/core.%p", size=11, fill="#ffffff", stroke="#64748b")
    svg_parts.append(b4)
    
    b5, w5, h5 = textbox(570, 425, "systemd-coredump (pipe)\nСтискання zstd/lz4 +\nзапис у journald", size=11, fill="#f0fdf4", stroke=FIELD, bold=True)
    svg_parts.append(b5)
    
    b6, w6, h6 = textbox(740, 425, "coredumpctl /\nDebugger GDB\nbt / info regs", size=11, fill="#fef3c7", stroke="#d97706", bold=True)
    svg_parts.append(b6)
    
    # Connections / Arrows
    # Process -> do_coredump
    svg_parts.append(arrow(160, 145, 160, 205, color=POS, sw=2))
    svg_parts.append(text(175, 175, "Trap / Signal", size=10, color=POS, anchor="start"))
    
    # do_coredump -> core_pattern
    svg_parts.append(arrow(260, 245, 315, 245, color="#475569", sw=2))
    
    # core_pattern -> direct file
    svg_parts.append(arrow(400, 285, 360, 385, color="#64748b", sw=1.8))
    svg_parts.append(text(340, 330, "Файл (core.%p)", size=10, color=MUTED, anchor="end"))
    
    # core_pattern -> systemd-coredump pipe
    svg_parts.append(arrow(490, 285, 540, 385, color=FIELD, sw=2))
    svg_parts.append(text(545, 330, "Pipe '|systemd-coredump'", size=10, color=FIELD, anchor="start"))
    
    # systemd-coredump -> GDB / coredumpctl
    svg_parts.append(arrow(650, 425, 675, 425, color="#d97706", sw=1.8))
    
    # Direct File -> GDB
    svg_parts.append(line(415, 425, 435, 425, color=MUTED, sw=1.5, dash="4,4"))
    svg_parts.append(arrow(435, 425, 675, 470, color=MUTED, sw=1.5))
    
    # Assembly SVG file
    svg_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_canvas} {h_canvas}" width="{w_canvas}" height="{h_canvas}">',
        '  <defs>',
        '    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '      <path d="M0,0 L0,6 L9,3 z" fill="#333" />',
        '    </marker>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        '\n'.join(svg_parts),
        '</svg>'
    ]
    
    out_path = os.path.join(IMG, "core-flow.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_content))
    print(f"Generated {out_path}")


def generate_elf_core_structure():
    w_canvas, h_canvas = 850, 480
    svg_parts = []
    
    # Title
    svg_parts.append(text(425, 30, "Структура ELF Core-файлу (ET_CORE Layout)", size=18, bold=True))
    
    # Main container block
    svg_parts.append(rect(40, 60, 770, 390, fill="#f8fafc", stroke="#64748b", sw=2, rx=8))
    
    # ELF Header Box
    b_hdr, w_hdr, h_hdr = textbox(130, 110, "ELF Header\ne_type = ET_CORE\ne_machine = EM_X86_64", size=11, fill="#e0e7ff", stroke="#4f46e5", bold=True)
    svg_parts.append(b_hdr)
    
    # Program Headers Table Box
    b_ph, w_ph, h_ph = textbox(380, 110, "Program Headers Table\n1x PT_NOTE segment\nNx PT_LOAD segments", size=11, fill="#fef3c7", stroke="#d97706", bold=True)
    svg_parts.append(b_ph)
    
    # PT_NOTE details Box
    svg_parts.append(rect(60, 180, 340, 240, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=6))
    svg_parts.append(text(230, 205, "Сегмент PT_NOTE (Метадані процесів)", size=12, color="#1e40af", bold=True))
    
    n1, _, _ = textbox(230, 245, "NT_PRSTATUS: registers (RIP, RSP, RAX...)\nsiginfo, PID, pr_cursig", size=10, fill="#ffffff", stroke="#3b82f6")
    n2, _, _ = textbox(230, 305, "NT_PRPSINFO: comm name, args, UID/GID", size=10, fill="#ffffff", stroke="#3b82f6")
    n3, _, _ = textbox(230, 355, "NT_SIGINFO: si_signo, si_code, si_addr", size=10, fill="#ffffff", stroke="#3b82f6")
    n4, _, _ = textbox(230, 400, "NT_FILE: mapped files & mmap offsets", size=10, fill="#ffffff", stroke="#3b82f6")
    svg_parts.extend([n1, n2, n3, n4])
    
    # PT_LOAD details Box
    svg_parts.append(rect(440, 180, 340, 240, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    svg_parts.append(text(610, 205, "Сегменти PT_LOAD (Зліпки пам'яті VMA)", size=12, color="#166534", bold=True))
    
    l1, _, _ = textbox(610, 250, "PT_LOAD #1: Стек потоку 1 (Thread Stack)\n[RSP-offset ... RSP-base]", size=10, fill="#ffffff", stroke=FIELD)
    l2, _, _ = textbox(610, 310, "PT_LOAD #2: Купа процесу (Heap Segment)\nанонімні модифіковані сторінки", size=10, fill="#ffffff", stroke=FIELD)
    l3, _, _ = textbox(610, 370, "PT_LOAD #3: Глобальні дані (.data / .bss)\nанонімні приватні мапінги", size=10, fill="#ffffff", stroke=FIELD)
    svg_parts.extend([l1, l2, l3])
    
    # Arrow connections
    svg_parts.append(arrow(200, 110, 290, 110, color="#4f46e5", sw=1.8))
    svg_parts.append(arrow(340, 140, 230, 180, color="#d97706", sw=1.8))
    svg_parts.append(arrow(430, 140, 610, 180, color="#d97706", sw=1.8))
    
    svg_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_canvas} {h_canvas}" width="{w_canvas}" height="{h_canvas}">',
        '  <defs>',
        '    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '      <path d="M0,0 L0,6 L9,3 z" fill="#333" />',
        '    </marker>',
        '  </defs>',
        '  <rect width="100%" height="100%" fill="#ffffff"/>',
        '\n'.join(svg_parts),
        '</svg>'
    ]
    
    out_path = os.path.join(IMG, "elf-core-structure.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_content))
    print(f"Generated {out_path}")


if __name__ == "__main__":
    generate_core_flow()
    generate_elf_core_structure()
