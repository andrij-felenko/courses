import os
import sys

# Ensure repo scripts/ directory is in path for svgkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def generate_arena_arch():
    frags = []
    
    # Outer frame / Background
    w, h = 900, 480
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    
    # Section 1: Userspace Process
    frags.append(rect(30, 40, 380, 210, fill="#f6f8fa", stroke="#0969da", sw=2, rx=6))
    frags.append(text(220, 68, "Простір користувача (Userspace Process)", size=15, color="#0969da", bold=True))
    
    b1, _, _ = textbox(220, 115, "Віртуальний адресний простір\nuser_vm_start + offset", size=13, fill="#ddf4ff", stroke="#54aef5")
    frags.append(b1)
    
    b2, _, _ = textbox(220, 185, "Пряме розіменування C-вказівника\nstruct node *p = arena_ptr;\nint val = p->value;", size=12, fill="#ffffff", stroke="#0969da")
    frags.append(b2)
    
    # Section 2: Kernel eBPF Execution Context
    frags.append(rect(490, 40, 380, 210, fill="#f6f8fa", stroke="#1a7f37", sw=2, rx=6))
    frags.append(text(680, 68, "Простір ядра (eBPF JIT Engine)", size=15, color="#1a7f37", bold=True))
    
    b3, _, _ = textbox(680, 115, "Віртуальний адресний простір\nkern_vm_start + offset", size=13, fill="#dafbe1", stroke="#4ac26b")
    frags.append(b3)
    
    b4, _, _ = textbox(680, 185, "Інструкції BPF JIT з маскуванням\nstruct node __arena *p = ...;\np->value++;", size=12, fill="#ffffff", stroke="#1a7f37")
    frags.append(b4)
    
    # Section 3: Physical Memory & MMU Page Tables
    frags.append(rect(100, 300, 700, 150, fill="#fff8c5", stroke="#d4a72c", sw=2, rx=6))
    frags.append(text(450, 328, "Фізична оперативна пам'ять (Physical RAM / Page Cache)", size=15, color="#9a6700", bold=True))
    
    b5, _, _ = textbox(270, 385, "Фізичні сторінки (4 KB Page 0..N)\nВиділення bpf_arena_alloc_pages()", size=12, fill="#ffffff", stroke="#d4a72c")
    frags.append(b5)
    
    b6, _, _ = textbox(630, 385, "Спільні сторінки пам'яті (Sparse Memory)\nZero-Copy відображення у mmap()", size=12, fill="#ffffff", stroke="#d4a72c")
    frags.append(b6)
    
    # Connecting Arrows
    frags.append(arrow(220, 225, 270, 355, color="#0969da", sw=2))
    frags.append(arrow(680, 225, 630, 355, color="#1a7f37", sw=2))
    
    # Bidirectional zero-copy line between Userspace & eBPF
    frags.append(line(410, 140, 490, 140, color="#8250df", sw=2, dash="4,4"))
    frags.append(text(450, 130, "Zero-Copy", size=11, color="#8250df", bold=True))
    
    render(os.path.join(IMG, 'arena-arch.svg'), w, h, *frags, title="Архітектура BPF Arena")

def generate_arena_pointers():
    frags = []
    
    w, h = 880, 440
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    
    # Title inside SVG frame
    frags.append(text(440, 40, "Механізм трансляції вказівників та маскування JIT у BPF Arena", size=15, color="#1f2328", bold=True))
    
    # Step 1: 64-bit Pointer structure
    frags.append(rect(40, 70, 800, 90, fill="#f6f8fa", stroke="#8c959f", sw=1.5, rx=6))
    frags.append(text(440, 92, "Структура 64-бітного вказівника BPF Arena", size=13, color="#24292f", bold=True))
    
    # High 32 bits vs Low 32 bits
    b1, _, _ = textbox(230, 125, "Старші 32 біти: Базовий регіон Арени\n(kern_vm_start або user_vm_start)", size=12, fill="#ddf4ff", stroke="#54aef5")
    frags.append(b1)
    
    b2, _, _ = textbox(630, 125, "Молодші 32 біти: Зміщення у регіоні (Offset)\nДіапазон 0 .. 4 ГБ (Sparse Memory)", size=12, fill="#dafbe1", stroke="#4ac26b")
    frags.append(b2)
    
    # Step 2: JIT Masking Pipeline
    frags.append(rect(40, 190, 380, 210, fill="#fff8c5", stroke="#d4a72c", sw=1.5, rx=6))
    frags.append(text(230, 215, "Верифікатор BPF та JIT на x86-64 / arm64", size=13, color="#9a6700", bold=True))
    
    b3, _, _ = textbox(230, 265, "1. Перевірка атрибута __arena\nLLVM address_space(1)", size=12, fill="#ffffff", stroke="#d4a72c")
    frags.append(b3)
    
    b4, _, _ = textbox(230, 345, "2. Вставка маскування інструкцій:\nmov %eax, %eax (обнулення верхніх 32 біт)\nadd %r12, %rax (додавання kern_vm_start)", size=11, fill="#ffffff", stroke="#d4a72c")
    frags.append(b4)
    
    # Step 3: Page Fault Handling & Allocator
    frags.append(rect(460, 190, 380, 210, fill="#f6f8fa", stroke="#0969da", sw=1.5, rx=6))
    frags.append(text(650, 215, "Динамічне виділення та BPF Exception", size=13, color="#0969da", bold=True))
    
    b5, _, _ = textbox(650, 265, "Виклик bpf_arena_alloc_pages()\nВиділення фізичних сторінок у ядрі", size=12, fill="#ddf4ff", stroke="#54aef5")
    frags.append(b5)
    
    b6, _, _ = textbox(650, 345, "Спроба розіменування невидимої сторінки:\nБезпечне перехоплення BPF Exception\n(Захист від Kernel Panic / Fault)", size=11, fill="#ffebe9", stroke="#ff8182")
    frags.append(b6)
    
    # Arrow between JIT & Page Fault
    frags.append(arrow(420, 295, 460, 295, color="#8c959f", sw=2))
    
    render(os.path.join(IMG, 'arena-pointers.svg'), w, h, *frags, title="Трансляція вказівників у BPF Arena")

def main():
    generate_arena_arch()
    generate_arena_pointers()
    print("All figures successfully rendered.")

if __name__ == "__main__":
    main()
