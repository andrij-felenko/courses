import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

from svgkit import render, rect, text, line, arrow, textbox, INK, FIELD, POS, NEG, MUTED

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

def draw_kprobes():
    frags = []
    
    # Kernel Memory Container
    frags.append(rect(40, 40, 310, 240, fill="#f9fafb", stroke="#d1d5db"))
    frags.append(text(195, 30, "Пам'ять ядра (Kernel Code & OOL Buffer)", bold=True, color=INK))
    
    # Original Code Sequence
    frags.append(rect(65, 60, 260, 32, fill="#ffffff", stroke="#9ca3af"))
    frags.append(text(195, 81, "mov %rdi, %rax  (Інструкція 1)", color=MUTED, size=13))
    
    # INT3 Trapped Instruction
    frags.append(rect(65, 98, 260, 32, fill="#fef2f2", stroke=POS))
    frags.append(text(195, 119, "INT3 (0xCC) [замість push %rbp]", color=POS, bold=True, size=13))
    
    frags.append(rect(65, 136, 260, 32, fill="#ffffff", stroke="#9ca3af"))
    frags.append(text(195, 157, "sub $0x20, %rsp (Інструкція 3)", color=MUTED, size=13))
    
    # OOL Buffer
    frags.append(rect(65, 195, 260, 65, fill="#eff6ff", stroke=NEG))
    frags.append(text(195, 215, "OOL Буфер (Out-Of-Line Exec)", color=NEG, bold=True, size=13))
    frags.append(text(195, 235, "push %rbp (Оригінальна інструкція 2)", size=12, color=INK))
    frags.append(text(195, 250, "[наступна: jmp назад у оригінал]", size=11, color=MUTED))

    # Kprobes Framework Box (wide enough to contain textbox fully)
    frags.append(rect(420, 40, 300, 240, fill="#f0fdf4", stroke=FIELD))
    frags.append(text(570, 65, "kprobe_handler() (Ring 0)", bold=True, size=15, color=FIELD))
    
    # Handler Steps
    h_steps = "1. Виклик pre_handler(regs)\n2. Зчитування регістрів (RDI, RSI)\n3. Коригування RIP на OOL Буфер\n4. Single-step виконання"
    tb, w, h = textbox(570, 165, h_steps, fill="#ffffff", stroke="#86efac")
    frags.append(tb)

    # Arrows
    # INT3 to Handler
    frags.append(arrow(325, 114, 415, 114, color=POS, sw=2))
    frags.append(text(370, 104, "#BP Trap", size=12, color=POS, bold=True))
    
    # Handler to OOL Buffer
    frags.append(arrow(415, 227, 330, 227, color=FIELD, sw=2))
    frags.append(text(372, 217, "Set RIP", size=12, color=FIELD))
    
    # OOL back to next instruction
    frags.append(arrow(65, 227, 25, 227, color=NEG, sw=2))
    frags.append(line(25, 227, 25, 152, color=NEG, sw=2))
    frags.append(arrow(25, 152, 60, 152, color=NEG, sw=2))
    frags.append(text(38, 185, "Jump RIP+1", size=11, color=NEG, anchor="start"))
    
    render(os.path.join(IMG, 'kprobes-int3-insertion.svg'), 750, 310, *frags, title="Архітектура Kprobes: вставка INT3 та OOL-буфер")

def draw_uprobes_cow():
    frags = []
    
    # Title / Top boundary
    frags.append(rect(30, 40, 320, 250, fill="#f8fafc", stroke="#cbd5e1"))
    frags.append(text(190, 30, "Простір користувача (Ring 3)", bold=True, color=INK))
    
    # Shared Library Page
    frags.append(rect(55, 60, 270, 45, fill="#ffffff", stroke="#94a3b8"))
    frags.append(text(190, 80, "libc.so (Спільна сторінка)", size=13, color=MUTED))
    frags.append(text(190, 95, "Фізична пам'ять: Read-Only", size=11, color=MUTED))
    
    # Process A Virtual Memory
    frags.append(rect(55, 130, 270, 65, fill="#fef2f2", stroke=POS))
    frags.append(text(190, 150, "Процес А: Модифікована сторінка", size=13, color=POS, bold=True))
    frags.append(text(190, 170, "Copy-on-Write (CoW) -> INT3 (0xCC)", size=12, color=POS))
    frags.append(text(190, 185, "Приватна фізична сторінка", size=11, color=MUTED))
    
    # Process B Virtual Memory
    frags.append(rect(55, 215, 270, 55, fill="#f0fdf4", stroke=FIELD))
    frags.append(text(190, 235, "Процес Б: Оригінальний мапінг", size=13, color=FIELD))
    frags.append(text(190, 255, "Без зонда (Оригінальний код)", size=11, color=MUTED))
    
    # Kernel Space (Ring 0)
    frags.append(rect(410, 40, 310, 250, fill="#f1f5f9", stroke="#94a3b8"))
    frags.append(text(565, 30, "Ядро Linux (Ring 0)", bold=True, color=INK))
    
    # Context switch box
    frags.append(rect(435, 70, 260, 70, fill="#ffffff", stroke=POS))
    frags.append(text(565, 95, "Перемикання контексту", bold=True, size=14, color=POS))
    frags.append(text(565, 115, "Ring 3 -> Ring 0 (#BP trap)", size=12, color=MUTED))
    frags.append(text(565, 130, "Високі накладні витрати!", size=11, color=POS))
    
    # eBPF / uprobe handler
    frags.append(rect(435, 160, 260, 110, fill="#eff6ff", stroke=NEG))
    frags.append(text(565, 185, "uprobe_dispatcher()", bold=True, size=14, color=NEG))
    frags.append(text(565, 210, "Виконання eBPF програми", size=12, color=INK))
    frags.append(text(565, 230, "OOL Single-step у [uprobes]", size=12, color=INK))
    frags.append(text(565, 250, "Повернення у Ring 3", size=11, color=MUTED))
    
    # Arrows
    frags.append(arrow(325, 162, 430, 105, color=POS, sw=2))
    frags.append(text(378, 125, "#BP trap", size=11, color=POS, bold=True))
    
    frags.append(arrow(565, 140, 565, 155, color=NEG, sw=2))
    
    render(os.path.join(IMG, 'uprobes-cow-paging.svg'), 750, 310, *frags, title="Механізм Uprobes: Copy-on-Write та перемикання контексту Ring 3 -> Ring 0")

def draw_kretprobe_stack():
    frags = []
    
    # Call Stack Container
    frags.append(rect(40, 40, 310, 250, fill="#fcfcfc", stroke="#cbd5e1"))
    frags.append(text(195, 30, "Стек викликів (Call Stack)", bold=True, color=INK))
    
    # Stack Frames
    frags.append(rect(65, 60, 260, 40, fill="#ffffff", stroke="#94a3b8"))
    frags.append(text(195, 85, "Аргументи функції (RDI, RSI...)", size=12, color=MUTED))
    
    # Return Address Frame - Swapped
    frags.append(rect(65, 105, 260, 50, fill="#fef2f2", stroke=POS))
    frags.append(text(195, 125, "Підмінена адреса повернення", size=13, color=POS, bold=True))
    frags.append(text(195, 143, "&kretprobe_trampoline", size=12, color=POS))
    
    frags.append(rect(65, 160, 260, 40, fill="#ffffff", stroke="#94a3b8"))
    frags.append(text(195, 185, "Локальні змінні функції", size=12, color=MUTED))
    
    frags.append(rect(65, 205, 260, 65, fill="#eff6ff", stroke=NEG))
    frags.append(text(195, 225, "Справжня адреса (збережена):", size=12, color=NEG, bold=True))
    frags.append(text(195, 245, "task->kretprobe_instances", size=12, color=INK))
    frags.append(text(195, 260, "0x7fff81234567 (caller)", size=11, color=MUTED))
    
    # Trampoline Execution Box (wide enough for inner textbox)
    frags.append(rect(420, 40, 300, 250, fill="#f0fdf4", stroke=FIELD))
    frags.append(text(570, 65, "Виконання kretprobe_trampoline", bold=True, size=15, color=FIELD))
    
    t_steps = "1. Процесор виконує RET\n2. Стрибок на kretprobe_trampoline\n3. Виклик kretprobe_handler()\n   (інспекція RAX / retval)\n4. Пошук справжньої адреси в task\n5. Стрибок на справжню адресу"
    tb, w, h = textbox(570, 170, t_steps, fill="#ffffff", stroke="#86efac")
    frags.append(tb)
    
    # Arrows
    frags.append(arrow(325, 130, 415, 100, color=POS, sw=2))
    frags.append(text(370, 105, "RET jumps", size=11, color=POS, bold=True))
    
    frags.append(arrow(325, 237, 415, 237, color=NEG, sw=2))
    frags.append(text(370, 227, "Restore RIP", size=11, color=NEG))
    
    render(os.path.join(IMG, 'kretprobe-stack-trampoline.svg'), 750, 310, *frags, title="Перехоплення виходу з функції: підміна стеку kretprobe / uretprobe")

if __name__ == '__main__':
    draw_kprobes()
    draw_uprobes_cow()
    draw_kretprobe_stack()
