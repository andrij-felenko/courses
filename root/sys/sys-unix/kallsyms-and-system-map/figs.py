import sys
import os
from pathlib import Path

# Add scripts/ to sys.path to import svgkit
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts"))
from svgkit import (
    textbox, rect, line, arrow, text, mtext, circle, render,
    FILL, LINE, INK, MUTED, POS, NEG, FIELD, BG
)

def render_kallsyms_arch():
    frags = []
    
    # Header title background card
    frags.append(rect(20, 20, 860, 480, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    
    # Column 1: Build Time (vmlinux & mksysmap)
    frags.append(rect(40, 40, 250, 440, fill="#f3f4f6", stroke="#d1d5db", sw=1.2, rx=6))
    frags.append(text(165, 65, "Етап збірки ядра (Build Time)", size=14, bold=True, color="#1f2937"))
    
    b1, w1, h1 = textbox(165, 120, "vmlinux (ELF бінарник)\n.text / .rodata / .symtab", size=12, pad=10, fill="#ffffff", stroke="#9ca3af")
    frags.append(b1)
    
    frags.append(arrow(165, 150, 165, 190, color="#4b5563"))
    frags.append(text(175, 175, "nm / kallsyms.c", size=11, color=MUTED, anchor="left"))
    
    b2, w2, h2 = textbox(165, 230, "System.map\n(Статичний текстовий файл)", size=12, pad=10, fill="#eff6ff", stroke="#3b82f6")
    frags.append(b2)
    
    frags.append(arrow(165, 270, 165, 310, color="#4b5563"))
    frags.append(text(175, 295, "Pass 1 & Pass 2 link", size=11, color=MUTED, anchor="left"))
    
    b3, w3, h3 = textbox(165, 360, "kallsyms.S\nТаблиці зміщень і лексем", size=12, pad=10, fill="#f0fdf4", stroke="#22c55e")
    frags.append(b3)
    
    frags.append(arrow(165, 405, 165, 445, color="#15803d"))
    frags.append(text(175, 430, "Вбудовування в .rodata", size=11, color="#15803d", anchor="left"))
    
    # Connector Arrow: Build -> Kernel Runtime
    frags.append(arrow(290, 360, 330, 360, color="#15803d", sw=2.0))
    
    # Column 2: Kernel Space Runtime
    frags.append(rect(330, 40, 260, 440, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(460, 65, "Простір ядра (Kernel Space RAM)", size=14, bold=True, color="#14532d"))
    
    b4, w4, h4 = textbox(460, 130, "Вбудовані таблиці kallsyms\nkallsyms_offsets / kallsyms_names\nkallsyms_token_table", size=12, pad=10, fill="#ffffff", stroke="#22c55e")
    frags.append(b4)
    
    frags.append(arrow(460, 175, 460, 220, color="#16a34a"))
    
    b5, w5, h5 = textbox(460, 250, "Ядерний підсистемний API\nkallsyms_lookup()\nprintk(\"%pS\", addr)", size=12, pad=10, fill="#dcfce7", stroke="#16a34a")
    frags.append(b5)
    
    frags.append(arrow(460, 295, 460, 340, color="#16a34a"))
    
    b6, w6, h6 = textbox(460, 375, "Подї ядра\nOops / Stack Trace / dmesg\nvfs_read+0x43/0x140", size=12, pad=10, fill="#fef2f2", stroke="#ef4444")
    frags.append(b6)
    
    # Connector Arrow: Kernel -> User Space
    frags.append(arrow(590, 250, 630, 250, color="#2563eb", sw=2.0))
    
    # Column 3: User Space & Security
    frags.append(rect(630, 40, 230, 440, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=6))
    frags.append(text(745, 65, "Простір користувача", size=14, bold=True, color="#1e3a8a"))
    
    b7, w7, h7 = textbox(745, 130, "/proc/kallsyms\n(Віртуальний псевдофайл)", size=12, pad=10, fill="#ffffff", stroke="#3b82f6")
    frags.append(b7)
    
    frags.append(arrow(745, 170, 745, 210, color="#2563eb"))
    
    b8, w8, h8 = textbox(745, 250, "Перевірка доступу\nkptr_restrict = 1 / 2\nCAP_SYSLOG", size=12, pad=10, fill="#fef3c7", stroke="#d97706")
    frags.append(b8)
    
    frags.append(arrow(745, 290, 745, 330, color="#2563eb"))
    
    b9, w9, h9 = textbox(745, 380, "Утиліти відлагодження\ngdb / addr2line / perf\ndecode_stacktrace.sh", size=12, pad=10, fill="#ffffff", stroke="#2563eb")
    frags.append(b9)
    
    img_dir = Path(__file__).resolve().parent / "img"
    img_dir.mkdir(exist_ok=True)
    path1 = str(img_dir / "kallsyms-arch.svg")
    render(path1, 900, 520, *frags, title="Архітектура та потік даних підсистеми kallsyms")
    print(f"Generated {path1}")

def render_kallsyms_compression():
    frags = []
    
    frags.append(rect(20, 20, 860, 440, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    
    # Section A: Address Table (kallsyms_offsets)
    frags.append(rect(40, 50, 390, 180, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(235, 75, "Таблиця відносних зміщень (kallsyms_offsets)", size=13, bold=True, color="#14532d"))
    
    b1, w1, h1 = textbox(235, 115, "Базова адреса ядра: _stext = 0xffffffff81000000", size=11, pad=6, fill="#ffffff", stroke="#16a34a")
    frags.append(b1)
    
    b2, w2, h2 = textbox(135, 175, "Індекс 0: 0x00000000\n-> _stext", size=11, pad=6, fill="#dcfce7", stroke="#16a34a")
    frags.append(b2)
    
    b3, w3, h3 = textbox(335, 175, "Індекс 1024: 0x00043210\n-> vfs_read (+274.9 KB)", size=11, pad=6, fill="#dcfce7", stroke="#16a34a")
    frags.append(b3)
    
    # Section B: Token Compression Dictionary
    frags.append(rect(450, 50, 410, 180, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=6))
    frags.append(text(655, 75, "Словник стиснення лексем (kallsyms_token_table)", size=13, bold=True, color="#1e3a8a"))
    
    b4, w4, h4 = textbox(550, 120, "Токен 0x80 -> \"sys_\"\nТокен 0x81 -> \"__x64_sys_\"", size=11, pad=6, fill="#ffffff", stroke="#3b82f6")
    frags.append(b4)
    
    b5, w5, h5 = textbox(750, 120, "Токен 0x82 -> \"driver_\"\nТокен 0x83 -> \"__init_\"", size=11, pad=6, fill="#ffffff", stroke="#3b82f6")
    frags.append(b5)
    
    b6, w6, h6 = textbox(655, 180, "256 найчастіших підрядків замінено на 1 байт\nЗаощаджує понад 60% обсягу імен у пам'яті RAM", size=11, pad=6, fill="#dbeafe", stroke="#2563eb")
    frags.append(b6)
    
    # Section C: Reconstructed Name Stream
    frags.append(rect(40, 250, 820, 190, fill="#fefce8", stroke="#fde047", sw=1.2, rx=6))
    frags.append(text(450, 275, "Процес розпакування імені символу (kallsyms_expand_symbol)", size=13, bold=True, color="#713f12"))
    
    b7, w7, h7 = textbox(200, 330, "Стиснений потік байтів:\n[0x81, 'o', 'p', 'e', 'n']", size=11, pad=8, fill="#ffffff", stroke="#ca8a04")
    frags.append(b7)
    
    frags.append(arrow(320, 330, 380, 330, color="#ca8a04", sw=2.0))
    frags.append(text(350, 320, "Декодування", size=10, color="#854d0e"))
    
    b8, w8, h8 = textbox(490, 330, "Підстановка токена 0x81:\n\"__x64_sys_\" + \"open\"", size=11, pad=8, fill="#fef08a", stroke="#ca8a04")
    frags.append(b8)
    
    frags.append(arrow(600, 330, 660, 330, color="#ca8a04", sw=2.0))
    
    b9, w9, h9 = textbox(750, 330, "Фінальне ім'я символу:\n\"__x64_sys_open\"", size=11, pad=8, fill="#fef9c3", stroke="#a16207")
    frags.append(b9)
    
    b10, w10, h10 = textbox(450, 400, "Маркери kallsyms_markers розміщуються кожні 256 символів для прискорення бінарного пошуку", size=11, pad=6, fill="#ffffff", stroke="#d97706")
    frags.append(b10)
    
    img_dir = Path(__file__).resolve().parent / "img"
    img_dir.mkdir(exist_ok=True)
    path2 = str(img_dir / "kallsyms-compression.svg")
    render(path2, 900, 480, *frags, title="Механізм стиснення та розпакування імен у kallsyms")
    print(f"Generated {path2}")

def main():
    render_kallsyms_arch()
    render_kallsyms_compression()

if __name__ == "__main__":
    main()
