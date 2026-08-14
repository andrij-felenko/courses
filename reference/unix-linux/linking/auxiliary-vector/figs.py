import sys
import os

# Add scripts folder to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
import svgkit as sk

def render_stack():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "stack.svg")
    
    frags = []
    
    # Title & Subtitle
    frags.append(sk.text(290, 25, "Анатомія стека процесу при виконанні execve", size=16, bold=True))
    frags.append(sk.text(290, 48, "Напрямок росту стека: від вищих адрес (0x7FFF...) до нижчих", size=12, color=sk.MUTED, italic=True))
    
    # Address Markers
    frags.append(sk.text(40, 75, "Вищі адреси", size=11, color=sk.MUTED, anchor="start"))
    frags.append(sk.arrow(40, 85, 40, 560, color=sk.MUTED))
    frags.append(sk.text(40, 575, "Низькі адреси", size=11, color=sk.MUTED, anchor="start"))
    
    # Blocks (top to bottom)
    # 1. Information Block
    box1, _, _ = sk.textbox(310, 105, "Інформаційний блок рядків\n(Аргументи, змінні середовища, AT_EXECFN, AT_PLATFORM, AT_RANDOM 16B)", size=12, fill="#f5f5f5", stroke="#888888", min_w=440)
    frags.append(box1)
    
    # 2. Null paddings and auxv
    box2, _, _ = sk.textbox(310, 195, "Допоміжний вектор auxv (масив Elf64_auxv_t)\n[AT_SYSINFO_EHDR, AT_PHDR, AT_PAGESZ, AT_RANDOM, ..., AT_NULL]", size=12, fill="#d0e0ff", stroke="#3b82f6", bold=True, min_w=440)
    frags.append(box2)
    
    # 3. NULL separator
    box3, _, _ = sk.textbox(310, 265, "Термінатор NULL (0x0000000000000000)", size=11, fill="#e5e7eb", stroke="#9ca3af", min_w=440)
    frags.append(box3)
    
    # 4. envp pointers
    box4, _, _ = sk.textbox(310, 335, "Масив вказівників середовища: envp[0], envp[1], ..., envp[N]", size=12, fill="#d1fae5", stroke="#10b981", min_w=440)
    frags.append(box4)
    
    # 5. NULL separator
    box5, _, _ = sk.textbox(310, 405, "Термінатор NULL (0x0000000000000000)", size=11, fill="#e5e7eb", stroke="#9ca3af", min_w=440)
    frags.append(box5)
    
    # 6. argv pointers
    box6, _, _ = sk.textbox(310, 475, "Масив вказівників аргументів: argv[0], argv[1], ..., argv[argc-1]", size=12, fill="#fee2e2", stroke="#ef4444", min_w=440)
    frags.append(box6)
    
    # 7. argc
    box7, _, _ = sk.textbox(310, 545, "Кількість аргументів: argc (uint64_t)", size=13, fill="#fef3c7", stroke="#f59e0b", bold=True, min_w=440)
    frags.append(box7)
    
    # Pointer RSP
    frags.append(sk.arrow(40, 545, 80, 545, color=sk.POS, sw=2.5))
    frags.append(sk.text(35, 532, "%rsp", size=14, color=sk.POS, bold=True, anchor="end"))
    
    sk.render(path, 580, 620, *frags)

def render_auxv_structure():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "auxv-structure.svg")
    
    frags = []
    frags.append(sk.text(290, 25, "Структура елемента Elf64_auxv_t (16 байтів)", size=16, bold=True))
    
    box_type, _, _ = sk.textbox(170, 110, "a_type (uint64_t)\nКлюч запису (наприклад, AT_PAGESZ = 6)\n8 байтів [Зсув +0x00]", size=12, fill="#dbeafe", stroke="#2563eb", min_w=230)
    frags.append(box_type)
    
    box_un, _, _ = sk.textbox(410, 110, "a_un (union)\na_val (число) / a_ptr (вказівник)\n8 байтів [Зсув +0x08]", size=12, fill="#dcfce7", stroke="#16a34a", min_w=230)
    frags.append(box_un)
    
    frags.append(sk.line(55, 175, 525, 175, color=sk.LINE, sw=1.5, dash="4,4"))
    frags.append(sk.text(290, 205, "Запис закінчується елементом із типом AT_NULL (a_type = 0, a_val = 0)", size=12, color=sk.MUTED, italic=True))
    
    sk.render(path, 580, 260, *frags)

def render_auxv_flow():
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "auxv-flow.svg")
    
    frags = []
    frags.append(sk.text(310, 25, "Передача та обробка допоміжного вектора", size=16, bold=True))
    
    box1, _, _ = sk.textbox(150, 90, "1. Ядро Linux (execve)\ncreate_elf_tables()\nФормує auxv на стеку", size=12, fill="#fef3c7", stroke="#d97706", min_w=220)
    frags.append(box1)
    
    box2, _, _ = sk.textbox(470, 90, "2. Стек процесу (RAM)\n[argc, argv, envp, auxv]\nФізичні дані в пам'яті", size=12, fill="#e0e7ff", stroke="#4f46e5", min_w=220)
    frags.append(box2)
    
    frags.append(sk.arrow(265, 90, 355, 90, color=sk.LINE, sw=2.0))
    
    box3, _, _ = sk.textbox(150, 240, "3. Динамічний лінкер\nld-linux.so (_dl_sysdep_start)\nПеревіряє AT_SECURE, vDSO", size=12, fill="#dcfce7", stroke="#15803d", min_w=220)
    frags.append(box3)
    
    box4, _, _ = sk.textbox(470, 240, "4. Користувацький код\ngetauxval() / /proc/self/auxv\nЧитання параметрів у main()", size=12, fill="#fee2e2", stroke="#dc2626", min_w=220)
    frags.append(box4)
    
    frags.append(sk.arrow(470, 145, 470, 185, color=sk.LINE, sw=2.0))
    frags.append(sk.arrow(265, 240, 355, 240, color=sk.LINE, sw=2.0))
    
    sk.render(path, 620, 360, *frags)

def render():
    render_stack()
    render_auxv_structure()
    render_auxv_flow()

if __name__ == "__main__":
    render()
