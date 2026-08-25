# -*- coding: utf-8 -*-
import sys
import os

# Add scripts directory to path (4 levels up from topic dir: reference/unix-linux/observability/kernel-oops-panic)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))

from svgkit import (
    render, text, mtext, rect, line, arrow, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "img")
os.makedirs(IMG_DIR, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL = "#fdecea"
WARM_FILL = "#fff6e5"
GREY_FILL = "#f4f6f8"

def make_box(x, y, w, h, title, subtitle="", fill_color=FILL, border_color=LINE, title_color=INK):
    res = []
    res.append(rect(x, y, w, h, fill=fill_color, stroke=border_color, sw=1.5, rx=6))
    if subtitle:
        res.append(text(x + w / 2, y + 20, title, size=13, color=title_color, bold=True))
        lines = subtitle.split("\n")
        res.append(mtext(x + w / 2, y + 38, lines, size=11, color=MUTED))
    else:
        res.append(text(x + w / 2, y + h / 2 + 4, title, size=13, color=title_color, bold=True))
    return "".join(res)

def fig_oops_vs_panic_flow():
    w, h = 900, 560
    frags = []
    
    # Top box: Hardware Exception
    frags.append(make_box(330, 50, 240, 50, "Апаратне переривання", "Page Fault / Exception (x86 IDT)", WARM_FILL, POS, POS))
    
    # Arrow to Trap Handler
    frags.append(arrow(450, 100, 450, 130, color=LINE, sw=1.5))
    
    # Decision: Context Check
    frags.append(make_box(320, 135, 260, 55, "Обробник do_page_fault()", "Перевірка CS / контексту виконання", BLUE_FILL, NEG, NEG))
    
    # Left Branch: Userspace Fault
    frags.append(line(320, 162, 160, 162, color=LINE, sw=1.5))
    frags.append(arrow(160, 162, 160, 210, color=LINE, sw=1.5))
    frags.append(text(220, 155, "User Mode (Ring 3)", size=11, color=MUTED, bold=True))
    
    frags.append(make_box(60, 215, 200, 60, "Надсилання SIGSEGV", "Процес користувача падає\nCore dump (за наявності)", GREEN_FILL, FIELD, FIELD))
    frags.append(arrow(160, 275, 160, 310, color=LINE, sw=1.5))
    frags.append(make_box(60, 315, 200, 50, "Система продовжує роботу", "Інші процеси не постраждали", GREEN_FILL, FIELD, INK))
    
    # Right Branch: Kernelspace Fault
    frags.append(line(580, 162, 740, 162, color=LINE, sw=1.5))
    frags.append(arrow(740, 162, 740, 210, color=LINE, sw=1.5))
    frags.append(text(660, 155, "Kernel Mode (Ring 0)", size=11, color=POS, bold=True))
    
    # Kernel Die / Oops Procedure
    frags.append(make_box(630, 215, 220, 60, "Виклик die() -> Kernel Oops", "oops_enter(), лог dmesg,\nвивід CR2/RIP/Call Trace", RED_FILL, POS, POS))
    
    frags.append(arrow(740, 275, 740, 310, color=LINE, sw=1.5))
    
    # Decision: Panic on Oops / IRQ / Spinlock
    frags.append(make_box(610, 315, 260, 65, "Перевірка умов Panic", "panic_on_oops=1 чи context_in_interrupt()\nчи утримання spinlock/in_atomic()", WARM_FILL, LINE, INK))
    
    # Sub-branch NO: Only task dead
    frags.append(line(610, 347, 450, 347, color=LINE, sw=1.5))
    frags.append(arrow(450, 347, 450, 410, color=LINE, sw=1.5))
    frags.append(text(520, 340, "Ні (Ніжний Oops)", size=11, color=MUTED, bold=True))
    
    frags.append(make_box(350, 415, 200, 65, "make_task_dead()", "Вбито лише один потік;\nЯдро помічено Tainted (D)", WARM_FILL, LINE, INK))
    
    # Sub-branch YES: Kernel Panic!
    frags.append(arrow(740, 380, 740, 410, color=LINE, sw=1.5))
    frags.append(text(765, 395, "Так (Фатально)", size=11, color=POS, bold=True))
    
    frags.append(make_box(630, 415, 220, 65, "panic() -> crash_kexec()", "Вимкнення IRQ, smp_send_stop()\nЗапуск Kdump чи HLT/Reboot", RED_FILL, POS, POS))
    
    # Kdump outcome
    frags.append(arrow(740, 480, 740, 508, color=LINE, sw=1.5))
    frags.append(make_box(620, 508, 240, 42, "Збереження /proc/vmcore", "Аналіз у виправленому Crash Kernel", GREY_FILL, LINE, INK))
    
    render(os.path.join(IMG_DIR, "oops-vs-panic-flow.svg"), w, h, *frags, title="Шлях обробки апаратного винятку ядра Linux")

def fig_page_fault_registers():
    w, h = 860, 480
    frags = []
    
    # Register CR2 Box
    frags.append(rect(40, 55, 370, 130, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=6))
    frags.append(text(225, 80, "CR2 (Control Register 2)", size=14, color=NEG, bold=True))
    frags.append(text(225, 105, "0x0000000000000008", size=15, color=POS, bold=True))
    frags.append(mtext(225, 130, ["Адреса лінійної пам'яті, що спричинила Page Fault", "Близькість до 0 -> NULL dereference зі зміщенням"], size=11, color=INK))
    
    # Register RIP Box
    frags.append(rect(450, 55, 370, 130, fill=WARM_FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(635, 80, "RIP (Instruction Pointer)", size=14, color=INK, bold=True))
    frags.append(text(635, 105, "ffffffffc03b1022", size=14, color=NEG, bold=True))
    frags.append(mtext(635, 130, ["Символ: bad_driver_func+0x22/0x50 [bad_module]", "Конкретна інструкція MOV/CMP, де впало ядро"], size=11, color=INK))
    
    # Error Code Bitfield Header
    frags.append(text(w / 2, 215, "Розшифровка апаратного коду помилки (Page Fault Error Code)", size=14, bold=True))
    
    # Bitfield visual representation
    bits = [
        ("Bit 0: P", "0 = Page not present\n1 = Protection violation", RED_FILL, POS),
        ("Bit 1: W/R", "0 = Read operation\n1 = Write operation", BLUE_FILL, NEG),
        ("Bit 2: U/S", "0 = Supervisor (Ring 0)\n1 = User (Ring 3)", GREEN_FILL, FIELD),
        ("Bit 3: RSVD", "0 = Normal PTE\n1 = Reserved bit set", GREY_FILL, INK),
        ("Bit 4: I/D", "0 = Data fetch\n1 = Instruction fetch", WARM_FILL, LINE)
    ]
    
    bx_w = 145
    for i, (b_title, b_desc, b_fill, b_stroke) in enumerate(bits):
        bx_x = 40 + i * 155
        frags.append(rect(bx_x, 235, bx_w, 140, fill=b_fill, stroke=b_stroke, sw=1.5, rx=6))
        frags.append(text(bx_x + bx_w / 2, 260, b_title, size=13, color=b_stroke, bold=True))
        frags.append(line(bx_x + 10, 275, bx_x + bx_w - 10, 275, color=b_stroke, sw=1.0))
        lines = b_desc.split("\n")
        frags.append(mtext(bx_x + bx_w / 2, 295, lines, size=10.5, color=INK))
        
    # Example error code decoding banner
    frags.append(rect(40, 395, 780, 55, fill=GREY_FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(w / 2, 418, "Приклад логу Oops: error_code(0x0002) -> [P=0 (Not Present), W/R=1 (Write), U/S=0 (Kernel)]", size=12, color=POS, bold=True))
    frags.append(text(w / 2, 436, "Тлумачення: Спроба ЗАПИСУ в незадокументовану сторінку пам'яті у режимі ядра", size=11, color=MUTED))

    render(os.path.join(IMG_DIR, "page-fault-registers.svg"), w, h, *frags, title="Ключові регістри процесора під час аварії ядра (x86_64)")

def fig_kdump_architecture():
    w, h = 880, 500
    frags = []
    
    # Outer RAM container
    frags.append(rect(40, 55, 800, 400, fill=GREY_FILL, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(120, 80, "Фізична оперативна пам'ять (RAM)", size=13, color=MUTED, bold=True))
    
    # Production Kernel Region
    frags.append(rect(60, 95, 480, 340, fill=BLUE_FILL, stroke=NEG, sw=1.5, rx=6))
    frags.append(text(300, 125, "Основне ядро (Production Kernel)", size=14, color=NEG, bold=True))
    frags.append(mtext(300, 155, [
        "Виконує робоче навантаження, користувацькі процеси, VFS, мережу.",
        "При зверненні panic() зупиняє всі CPU через NMI IPI",
        "і передає управління через kexec без скидання апаратури (POST)."
    ], size=11, color=INK))
    
    # Production RAM Contents detail box
    frags.append(rect(80, 220, 440, 195, fill=BG, stroke=NEG, sw=1.0, rx=4))
    frags.append(text(300, 245, "Стан пам'яті при збої (Заморожено)", size=12, color=POS, bold=True))
    frags.append(mtext(300, 275, [
        "• Таблиці сторінок ядра та процесів",
        "• Спеціальні ELF-нотатки з записами регістрів CPU",
        "• Буфери сокетів, VFS-кеш та структури даних",
        "-> Доступно в Crash Kernel як файл /proc/vmcore"
    ], size=10.5, color=INK))
    
    # Reserved Crashkernel Region
    frags.append(rect(560, 95, 260, 340, fill=RED_FILL, stroke=POS, sw=1.5, rx=6))
    frags.append(text(690, 125, "Зарезервований простір", size=13, color=POS, bold=True))
    frags.append(text(690, 145, "crashkernel=512M", size=12, color=POS, bold=True))
    frags.append(line(575, 160, 805, 160, color=POS, sw=1.0))
    
    # Crash Kernel inside Reserved
    frags.append(rect(575, 175, 230, 240, fill=WARM_FILL, stroke=LINE, sw=1.2, rx=4))
    frags.append(text(690, 200, "Crash Kernel (Capture)", size=13, color=INK, bold=True))
    frags.append(mtext(690, 230, [
        "Ізольоване міні-ядро",
        "з власною initramfs",
        "---------------------",
        "1. Читає /proc/vmcore",
        "2. Запускає makedumpfile",
        "3. Стискає та зберігає",
        "   дамп у /var/crash/",
        "4. Виконує reboot"
    ], size=10.5, color=INK))
    
    # Transition Arrow
    frags.append(arrow(480, 180, 560, 180, color=POS, sw=2.5))
    frags.append(text(520, 170, "crash_kexec()", size=10, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "kdump-architecture.svg"), w, h, *frags, title="Архітектура Kdump: ізоляція Crash Kernel у зарезервованій пам'яті")

if __name__ == "__main__":
    fig_oops_vs_panic_flow()
    fig_page_fault_registers()
    fig_kdump_architecture()
    print("SVGs generated successfully.")
