import sys
import os

# Add scripts directory to path for svgkit
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import rect, line, arrow, text, mtext, FONT, INK, FILL, MUTED, POS, NEG, FIELD

def render_layout():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tls-memory-layout.svg")

    w, h = 840, 520
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.append('<defs>')
    parts.append('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    parts.append('    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>')
    parts.append('  </marker>')
    parts.append('</defs>')
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 28, "Топологія пам'яті ELF TLS: Variant II (x86_64) vs Variant I (ARM/RISC-V)", size=16, bold=True, color="#0f172a"))

    # Panel 1: Variant II (x86_64)
    parts.append(rect(40, 55, 450, 440, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(265, 80, "ELF TLS Variant II (x86_64 / ELF ABI)", size=14, bold=True, color="#1e293b"))
    parts.append(text(265, 98, "Негативне зміщення відносно Thread Pointer (FS Base)", size=11, color=MUTED))

    # Memory Layout Stack Variant II
    # Memory Addresses grow upwards
    # .tbss (lowest address)
    parts.append(rect(70, 120, 200, 70, fill="#fef9c3", stroke="#ca8a04", sw=1.2, rx=4))
    parts.append(text(170, 145, ".tbss (Нульовий TLS)", size=12, bold=True, color="#854d0e"))
    parts.append(text(170, 168, "Від'ємне зміщення fs:-N", size=11, color="#a16207"))

    # .tdata
    parts.append(rect(70, 190, 200, 70, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=4))
    parts.append(text(170, 215, ".tdata (Шаблон даних)", size=12, bold=True, color="#15803d"))
    parts.append(text(170, 238, "Від'ємне зміщення fs:-M", size=11, color="#166534"))

    # TCB / struct pthread (FS points right here)
    parts.append(rect(70, 260, 200, 110, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=4))
    parts.append(text(170, 282, "TCB / struct pthread", size=13, bold=True, color="#1e40af"))
    parts.append(line(70, 292, 270, 292, color="#93c5fd", sw=1))
    parts.append(text(170, 310, "fs:0x00 -> Self pointer", size=11, color="#1d4ed8"))
    parts.append(text(170, 328, "fs:0x08 -> dtv_t *dtv", size=11, color="#1d4ed8"))
    parts.append(text(170, 346, "fs:0x10 -> self thread_id", size=11, color="#1d4ed8"))

    # Thread Pointer Pointer (FS Base)
    parts.append(arrow(380, 260, 275, 260, color="#ef4444", sw=2.5))
    parts.append(rect(340, 240, 130, 36, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    parts.append(text(405, 262, "FS Register (TP)", size=12, bold=True, color="#b91c1c"))

    # Callouts for offset direction
    parts.append(arrow(40, 260, 40, 130, color="#0284c7", sw=1.5))
    parts.append('<text x="30" y="195" font-family="\'Segoe UI\', sans-serif" font-size="11" fill="#0369a1" text-anchor="middle" transform="rotate(-90 30 195)">Зміщення від\'ємні (-)</text>')

    # Details on self pointer
    parts.append(line(270, 310, 310, 310, color="#2563eb", sw=1, dash="3 3"))
    parts.append(text(380, 315, "fs:[0] вказує на сам TCB", size=11, color="#1e40af"))

    # Panel 2: Variant I (ARM/RISC-V)
    parts.append(rect(510, 55, 290, 440, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(655, 80, "ELF TLS Variant I (ARM/RISC-V)", size=14, bold=True, color="#1e293b"))
    parts.append(text(655, 98, "Позитивне зміщення від TP", size=11, color=MUTED))

    # TCB at lowest position
    parts.append(rect(550, 130, 210, 70, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
    parts.append(text(655, 155, "TCB (Thread Control)", size=12, bold=True, color="#1e40af"))
    parts.append(text(655, 178, "TP вказує на початок", size=11, color="#1d4ed8"))

    # .tdata
    parts.append(rect(550, 200, 210, 70, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=4))
    parts.append(text(655, 225, ".tdata (Шаблон даних)", size=12, bold=True, color="#15803d"))
    parts.append(text(655, 248, "Позитивне зміщення tp+N", size=11, color="#166534"))

    # .tbss
    parts.append(rect(550, 270, 210, 70, fill="#fef9c3", stroke="#ca8a04", sw=1.2, rx=4))
    parts.append(text(655, 295, ".tbss (Нульовий TLS)", size=12, bold=True, color="#854d0e"))
    parts.append(text(655, 318, "Позитивне зміщення tp+M", size=11, color="#a16207"))

    # TP Arrow Variant I
    parts.append(arrow(520, 130, 545, 130, color="#ef4444", sw=2))
    parts.append(text(515, 115, "TP (Thread Pointer)", size=11, bold=True, color="#b91c1c"))

    parts.append(arrow(775, 130, 775, 330, color="#0284c7", sw=1.5))
    parts.append('<text x="785" y="230" font-family="\'Segoe UI\', sans-serif" font-size="11" fill="#0369a1" text-anchor="middle" transform="rotate(90 785 230)">Зміщення позитивні (+)</text>')

    parts.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

def render_dtv():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "dtv-and-dynamic-tls.svg")

    w, h = 840, 500
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.append('<defs>')
    parts.append('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    parts.append('    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>')
    parts.append('  </marker>')
    parts.append('</defs>')
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 28, "Динамічний вектор потоку (DTV) та адресація модулів dlopen()", size=16, bold=True, color="#0f172a"))

    # FS Base Box
    parts.append(rect(40, 70, 160, 70, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=6))
    parts.append(text(120, 95, "Регістр FS (TP Base)", size=13, bold=True, color="#b91c1c"))
    parts.append(text(120, 118, "fs:0x08 -> dtv", size=11, color="#991b1b"))

    # DTV Header Pointer
    parts.append(arrow(200, 105, 275, 105, color="#ef4444", sw=2))

    # DTV Array Structure Box
    parts.append(rect(280, 60, 240, 410, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    parts.append(text(400, 85, "DTV (Dynamic Thread Vector)", size=13, bold=True, color="#1e293b"))

    # DTV elements
    # dtv[0] - Generation Counter
    parts.append(rect(300, 110, 200, 50, fill="#e2e8f0", stroke="#64748b", sw=1, rx=4))
    parts.append(text(400, 130, "dtv[0]: Generation", size=11, bold=True, color="#334155"))
    parts.append(text(400, 148, "gen = 3 (версія модулів)", size=10, color="#475569"))

    # dtv[1] - Main Executable Static TLS
    parts.append(rect(300, 170, 200, 60, fill="#dbeafe", stroke="#2563eb", sw=1, rx=4))
    parts.append(text(400, 192, "dtv[1]: Module 1 (Executable)", size=11, bold=True, color="#1e40af"))
    parts.append(text(400, 212, "Вказівник на Static TLS", size=10, color="#1d4ed8"))

    # dtv[2] - Shared Library 1
    parts.append(rect(300, 240, 200, 60, fill="#dcfce7", stroke="#16a34a", sw=1, rx=4))
    parts.append(text(400, 262, "dtv[2]: Module 2 (liba.so)", size=11, bold=True, color="#15803d"))
    parts.append(text(400, 282, "Вказівник на TLS liba.so", size=10, color="#166534"))

    # dtv[3] - Dynamic dlopen Library (allocated lazily)
    parts.append(rect(300, 310, 200, 60, fill="#fef9c3", stroke="#ca8a04", sw=1, rx=4))
    parts.append(text(400, 332, "dtv[3]: Module 3 (libplugin.so)", size=11, bold=True, color="#854d0e"))
    parts.append(text(400, 352, "Алокований через __tls_get_addr", size=10, color="#a16207"))

    # dtv[4] - Unallocated entry (TLS_SLOT_UNALLOCATED)
    parts.append(rect(300, 380, 200, 60, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    parts.append(text(400, 402, "dtv[4]: Module 4 (Unallocated)", size=11, bold=True, color="#64748b"))
    parts.append(text(400, 422, "Вказівник == NULL (Lazy)", size=10, color="#64748b"))

    # Target Memory Blocks on the right
    # Block 1 (Main Exec)
    parts.append(rect(580, 170, 220, 50, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    parts.append(text(690, 190, "Static TLS Block (Main)", size=11, bold=True, color="#1d4ed8"))
    parts.append(text(690, 208, "Виділений при старті", size=10, color="#2563eb"))
    parts.append(arrow(500, 200, 575, 195, color="#2563eb", sw=1.5))

    # Block 2 (liba.so)
    parts.append(rect(580, 240, 220, 50, fill="#f0fdf4", stroke="#22c55e", sw=1, rx=4))
    parts.append(text(690, 260, "Dynamic TLS Block (liba.so)", size=11, bold=True, color="#15803d"))
    parts.append(text(690, 278, "Виділений при load/thread", size=10, color="#16a34a"))
    parts.append(arrow(500, 270, 575, 265, color="#16a34a", sw=1.5))

    # Block 3 (libplugin.so)
    parts.append(rect(580, 310, 220, 50, fill="#fefce8", stroke="#eab308", sw=1, rx=4))
    parts.append(text(690, 330, "Lazy TLS Block (libplugin.so)", size=11, bold=True, color="#854d0e"))
    parts.append(text(690, 348, "Виділений під час першого доступу", size=10, color="#ca8a04"))
    parts.append(arrow(500, 340, 575, 335, color="#ca8a04", sw=1.5))

    # Function call callout
    parts.append(rect(40, 220, 200, 100, fill="#faf5ff", stroke="#a855f7", sw=1.2, rx=6))
    parts.append(text(140, 245, "Виклик __tls_get_addr", size=12, bold=True, color="#7e22ce"))
    parts.append(text(140, 268, "Аргумент: tls_index", size=11, color="#6b21a8"))
    parts.append(text(140, 288, "{ti_module: 3, ti_offset: 0x10}", size=10, color="#6b21a8"))
    parts.append(text(140, 305, "Повертає: dtv[3] + 0x10", size=10, bold=True, color="#7e22ce"))

    parts.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

def render_models():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tls-relocation-models.svg")

    w, h = 840, 540
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.append('<defs>')
    parts.append('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    parts.append('    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>')
    parts.append('  </marker>')
    parts.append('</defs>')
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 28, "Моделі доступу до TLS та огляд релаксацій компонувальника (Linker Relaxations)", size=16, bold=True, color="#0f172a"))

    # 4 Access Model Boxes
    # 1. General Dynamic (GD)
    parts.append(rect(40, 60, 360, 190, fill="#fff1f2", stroke="#f43f5e", sw=1.5, rx=8))
    parts.append(text(220, 85, "1. General Dynamic (GD)", size=14, bold=True, color="#be123c"))
    parts.append(text(220, 105, "Найуніверсальніша модель (для dlopen)", size=11, color="#9f1239"))
    parts.append(rect(60, 120, 320, 50, fill="#ffffff", stroke="#fda4af", sw=1, rx=4))
    parts.append(text(220, 140, "lea rdi, [rip + x@tlsgd]", size=11, color="#881337"))
    parts.append(text(220, 158, "call __tls_get_addr@PLT", size=11, bold=True, color="#be123c"))
    parts.append(text(220, 188, "Накладність: Виклик функції + 2 елементи GOT", size=10, color="#be123c"))
    parts.append(text(220, 205, "Релокація: R_X86_64_TLSGD", size=10, bold=True, color="#881337"))

    # 2. Local Dynamic (LD)
    parts.append(rect(440, 60, 360, 190, fill="#fefce8", stroke="#eab308", sw=1.5, rx=8))
    parts.append(text(620, 85, "2. Local Dynamic (LD)", size=14, bold=True, color="#a16207"))
    parts.append(text(620, 105, "Декілька змінних в одній shared library", size=11, color="#854d0e"))
    parts.append(rect(460, 120, 320, 50, fill="#ffffff", stroke="#fef08a", sw=1, rx=4))
    parts.append(text(620, 138, "call __tls_get_addr (1 раз для модуля)", size=11, bold=True, color="#a16207"))
    parts.append(text(620, 156, "mov eax, [rax + var@dtpoff]", size=11, color="#713f12"))
    parts.append(text(620, 188, "Накладність: 1 виклик на модуль + розрахунок зміщення", size=10, color="#a16207"))
    parts.append(text(620, 205, "Релокація: R_X86_64_TLSLD / DTPOFF32", size=10, bold=True, color="#713f12"))

    # 3. Initial Exec (IE)
    parts.append(rect(40, 290, 360, 190, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    parts.append(text(220, 315, "3. Initial Exec (IE)", size=14, bold=True, color="#1d4ed8"))
    parts.append(text(220, 335, "Для змінних у бібліотеках завантажених при старті", size=11, color="#1e40af"))
    parts.append(rect(60, 350, 320, 50, fill="#ffffff", stroke="#bfdbfe", sw=1, rx=4))
    parts.append(text(220, 368, "mov rax, QWORD PTR fs:0", size=11, color="#1e3a8a"))
    parts.append(text(220, 386, "add rax, QWORD PTR [rip + x@gottpoff]", size=11, bold=True, color="#1d4ed8"))
    parts.append(text(220, 418, "Накладність: Без викликів функцій, 1 звернення до GOT", size=10, color="#1d4ed8"))
    parts.append(text(220, 435, "Релокація: R_X86_64_GOTTPOFF", size=10, bold=True, color="#1e3a8a"))

    # 4. Local Exec (LE)
    parts.append(rect(440, 290, 360, 190, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    parts.append(text(620, 315, "4. Local Exec (LE)", size=14, bold=True, color="#15803d"))
    parts.append(text(620, 335, "Для змінних у головному бінарнику (Main)", size=11, color="#166534"))
    parts.append(rect(460, 350, 320, 50, fill="#ffffff", stroke="#bbf7d0", sw=1, rx=4))
    parts.append(text(620, 377, "mov eax, DWORD PTR fs:-offset", size=12, bold=True, color="#15803d"))
    parts.append(text(620, 418, "Накладність: Мінімальна (1 інструкція, 0 GOT, 0 call)", size=10, color="#15803d"))
    parts.append(text(620, 435, "Релокація: R_X86_64_TPOFF32", size=10, bold=True, color="#14532d"))

    # Transition Arrows (Linker Relaxations)
    # GD -> IE Transition
    parts.append(line(220, 250, 220, 260, color="#d97706", sw=2))
    parts.append(rect(150, 260, 140, 22, fill="#fef3c7", stroke="#d97706", sw=1, rx=3))
    parts.append(text(220, 275, "Релаксація GD -> IE", size=10, bold=True, color="#b45309"))
    parts.append(arrow(220, 282, 220, 290, color="#d97706", sw=2))

    # GD -> LE Transition (Diagonal arrow)
    parts.append(arrow(360, 230, 450, 290, color="#16a34a", sw=2))
    parts.append(rect(370, 240, 120, 22, fill="#dcfce7", stroke="#16a34a", sw=1, rx=3))
    parts.append(text(430, 255, "Релаксація GD -> LE", size=10, bold=True, color="#15803d"))

    # LD -> LE Transition
    parts.append(line(620, 250, 620, 260, color="#16a34a", sw=2))
    parts.append(rect(550, 260, 140, 22, fill="#dcfce7", stroke="#16a34a", sw=1, rx=3))
    parts.append(text(620, 275, "Релаксація LD -> LE", size=10, bold=True, color="#15803d"))
    parts.append(arrow(620, 282, 620, 290, color="#16a34a", sw=2))

    # IE -> LE Transition (Horizontal arrow)
    parts.append(arrow(400, 385, 440, 385, color="#16a34a", sw=2))
    parts.append(text(420, 375, "IE -> LE", size=10, bold=True, color="#15803d"))

    parts.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

def main():
    render_layout()
    render_dtv()
    render_models()

if __name__ == "__main__":
    main()
