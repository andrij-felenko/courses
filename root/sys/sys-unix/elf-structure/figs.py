import sys
import os

# Add scripts directory to path for svgkit
scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from svgkit import rect, line, arrow, text, mtext, FONT, INK, FILL, MUTED, POS, NEG, FIELD

def render():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "elf-structure-diagram.svg")

    w, h = 820, 520
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    parts.append('<defs>')
    parts.append('  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    parts.append('    <path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/>')
    parts.append('  </marker>')
    parts.append('</defs>')
    parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # Title
    parts.append(text(w / 2, 30, "Двоїста структура ELF-файлу: компонувальник vs завантажувач ядра", size=16, bold=True))

    # Left Container (Linker View)
    parts.append(rect(40, 50, 290, 440, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(185, 75, "Компонування (Linker View)", size=14, bold=True, color="#1e293b"))
    parts.append(text(185, 93, "Файл на диску (Секції)", size=11, color=MUTED))

    # Sections inside left container
    parts.append(rect(55, 110, 260, 32, fill="#e2e8f0", stroke="#64748b", sw=1))
    parts.append(text(185, 131, "ELF Header (Заголовок)", size=12, bold=True))

    parts.append(rect(55, 147, 260, 32, fill="#fed7aa", stroke="#f97316", sw=1))
    parts.append(text(185, 168, "Program Header Table (PHT)", size=12, bold=True, color="#c2410c"))

    parts.append(rect(55, 184, 260, 34, fill="#dbeafe", stroke="#3b82f6", sw=1))
    parts.append(text(185, 205, ".text (Машинний код, AX)", size=12, color="#1d4ed8"))

    parts.append(rect(55, 223, 260, 34, fill="#e0e7ff", stroke="#6366f1", sw=1))
    parts.append(text(185, 244, ".rodata (Константи, рядки, A)", size=12, color="#4338ca"))

    parts.append(rect(55, 262, 260, 34, fill="#dcfce7", stroke="#22c55e", sw=1))
    parts.append(text(185, 283, ".data (Ініціалізовані змінні, WA)", size=12, color="#15803d"))

    parts.append(rect(55, 301, 260, 34, fill="#fef9c3", stroke="#eab308", sw=1))
    parts.append(text(185, 322, ".bss (Нульові змінні, NOBITS)", size=12, color="#a16207"))

    parts.append(rect(55, 340, 260, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1))
    parts.append(text(185, 361, ".symtab / .strtab (Символи)", size=12, color="#475569"))

    parts.append(rect(55, 377, 260, 32, fill="#cbd5e1", stroke="#475569", sw=1))
    parts.append(text(185, 398, "Section Header Table (SHT)", size=12, bold=True))

    # Right Container (Execution View)
    parts.append(rect(470, 50, 310, 440, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    parts.append(text(625, 75, "Виконання у пам'яті (Loader View)", size=14, bold=True, color="#1e293b"))
    parts.append(text(625, 93, "Віртуальний адресний простір (mmap)", size=11, color=MUTED))

    # Segments inside right container
    parts.append(rect(485, 115, 280, 40, fill="#fee2e2", stroke="#ef4444", sw=1.2))
    parts.append(text(625, 133, "PT_INTERP / PT_PHDR", size=12, bold=True, color="#b91c1c"))
    parts.append(text(625, 148, "Інтерпретатор ld-linux.so", size=10, color="#b91c1c"))

    parts.append(rect(485, 165, 280, 110, fill="#eff6ff", stroke="#2563eb", sw=1.5))
    parts.append(text(625, 188, "PT_LOAD #1 (Код та читання)", size=13, bold=True, color="#1d4ed8"))
    parts.append(text(625, 208, "Права: R-E (PROT_READ | PROT_EXEC)", size=11, color="#1e40af"))
    parts.append(rect(500, 218, 250, 45, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=4))
    parts.append(text(625, 245, "Опкод коду (.text) + Таблиці (.rodata)", size=11, color="#1e3a8a"))

    parts.append(rect(485, 285, 280, 125, fill="#f0fdf4", stroke="#16a34a", sw=1.5))
    parts.append(text(625, 308, "PT_LOAD #2 (Дані та стан)", size=13, bold=True, color="#15803d"))
    parts.append(text(625, 328, "Права: RW- (PROT_READ | PROT_WRITE)", size=11, color="#166534"))
    parts.append(rect(500, 338, 250, 60, fill="#dcfce7", stroke="#22c55e", sw=1, rx=4))
    parts.append(text(625, 360, "Файлові дані (.data)", size=11, color="#14532d"))
    parts.append(text(625, 382, "+ Алокація нулів у RAM (.bss)", size=11, color="#854d0e", bold=True))

    # Connection lines / arrows from left to right
    parts.append(arrow(315, 163, 485, 135, color="#f97316", sw=2))

    # Bracket / Mapping arrows from sections to segments
    parts.append(arrow(315, 201, 485, 210, color="#2563eb", sw=1.5))
    parts.append(arrow(315, 240, 485, 230, color="#2563eb", sw=1.5))

    parts.append(arrow(315, 279, 485, 345, color="#16a34a", sw=1.5))
    parts.append(arrow(315, 318, 485, 375, color="#ca8a04", sw=1.5))

    parts.append("</svg>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

if __name__ == "__main__":
    render()
