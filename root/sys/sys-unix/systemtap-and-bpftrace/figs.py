import os
import sys

# Додаємо шлях до scripts для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def create_systemtap_pipeline():
    frags = []
    
    # Pass blocks
    passes = [
        ("Pass 1: Parse", "Аналіз .stp скрипта\nРозгортання tapsets", 30, 70, 140, 100),
        ("Pass 2: Elaborate", "DWARF & vmlinux\nРозв'язання типів", 190, 70, 140, 100),
        ("Pass 3: Translate", "Генерація C-коду\nRuntime перевірки", 350, 70, 140, 100),
        ("Pass 4: Compile", "kbuild компіляція\nСтворення .ko", 510, 70, 140, 100),
        ("Pass 5: Execute", "staprun завантаження\nРежим збору даних", 670, 70, 140, 100)
    ]

    for title, desc, x, y, w, h in passes:
        frags.append(rect(x, y, w, h, fill="#ffffff", stroke="#0288d1", rx=6))
        frags.append(rect(x, y, w, 28, fill="#e1f5fe", stroke="#0288d1", rx=6))
        frags.append(text(x + w / 2, y + 19, title, size=13, bold=True, color="#01579b"))
        lines = desc.split("\n")
        frags.append(text(x + w / 2, y + 54, lines[0], size=11, color="#37474f"))
        frags.append(text(x + w / 2, y + 78, lines[1], size=11, color="#37474f"))

    # Arrows between passes
    for i in range(4):
        x1 = 30 + i * 160 + 140
        x2 = 30 + (i + 1) * 160
        y = 120
        frags.append(arrow(x1, y, x2, y, color="#0288d1", sw=2))

    # Lower Section: User Space vs Kernel Space
    # User space container
    frags.append(rect(30, 210, 380, 210, fill="#f3e5f5", stroke="#7b1fa2", rx=8))
    frags.append(text(45, 235, "Простір користувача (User Space)", size=14, bold=True, color="#4a148c", anchor="start"))
    
    frags.append(rect(50, 255, 160, 65, fill="#ffffff", stroke="#7b1fa2", rx=4))
    frags.append(text(130, 280, "CLI: stap / staprun", size=12, bold=True, color="#4a148c"))
    frags.append(text(130, 302, "Керування сесією", size=11, color="#4a148c"))

    frags.append(rect(230, 255, 160, 65, fill="#ffffff", stroke="#7b1fa2", rx=4))
    frags.append(text(310, 280, "stapio process", size=12, bold=True, color="#4a148c"))
    frags.append(text(310, 302, "Збір логів та вивід", size=11, color="#4a148c"))

    frags.append(rect(50, 340, 340, 60, fill="#ffffff", stroke="#7b1fa2", rx=4))
    frags.append(text(220, 375, "Tapsets Library (/usr/share/systemtap/tapset)", size=11, color="#4a148c"))

    # Kernel space container
    frags.append(rect(440, 210, 380, 210, fill="#ffebee", stroke="#c62828", rx=8))
    frags.append(text(455, 235, "Простір ядра (Kernel Space / Ring 0)", size=14, bold=True, color="#b71c1c", anchor="start"))

    frags.append(rect(460, 255, 160, 65, fill="#ffffff", stroke="#c62828", rx=4))
    frags.append(text(540, 280, "Generated .ko Module", size=12, bold=True, color="#b71c1c"))
    frags.append(text(540, 302, "Kprobes / Tracepoints", size=11, color="#b71c1c"))

    frags.append(rect(640, 255, 160, 65, fill="#ffffff", stroke="#c62828", rx=4))
    frags.append(text(720, 280, "RelayFS / DebugFS", size=12, bold=True, color="#b71c1c"))
    frags.append(text(720, 302, "Буфери обміну даних", size=11, color="#b71c1c"))

    frags.append(rect(460, 340, 340, 60, fill="#ffffff", stroke="#c62828", rx=4))
    frags.append(text(630, 375, "Safety Checks (Safety Limits & Guru Mode)", size=11, color="#b71c1c"))

    # Connection lines between spaces
    frags.append(arrow(390, 287, 460, 287, color="#0288d1", sw=2))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "systemtap-pipeline.svg")
    render(out_path, 850, 450, *frags, title="Пайплайн компіляції та виконання SystemTap (Pass 1 - Pass 5)")

def create_bpftrace_architecture():
    frags = []

    # User space container
    frags.append(rect(30, 60, 790, 175, fill="#e8f5e9", stroke="#2e7d32", rx=8))
    frags.append(text(45, 85, "Простір користувача (User Space)", size=14, bold=True, color="#1b5e20", anchor="start"))

    frags.append(rect(50, 105, 160, 110, fill="#ffffff", stroke="#2e7d32", rx=6))
    frags.append(text(130, 130, "bpftrace Script (.bt)", size=12, bold=True, color="#1b5e20"))
    frags.append(text(130, 160, "DSL парсер & AST", size=11, color="#37474f"))
    frags.append(text(130, 185, "kprobe / tracepoint", size=11, color="#37474f"))

    frags.append(rect(260, 105, 180, 110, fill="#ffffff", stroke="#2e7d32", rx=6))
    frags.append(text(350, 130, "LLVM / Clang CodeGen", size=12, bold=True, color="#1b5e20"))
    frags.append(text(350, 160, "BTF & CO-RE підтримка", size=11, color="#37474f"))
    frags.append(text(350, 185, "Генерація eBPF байткоду", size=11, color="#37474f"))

    frags.append(rect(490, 105, 160, 110, fill="#ffffff", stroke="#2e7d32", rx=6))
    frags.append(text(570, 130, "libbpf / bpf() syscall", size=12, bold=True, color="#1b5e20"))
    frags.append(text(570, 160, "Завантаження програм", size=11, color="#37474f"))
    frags.append(text(570, 185, "Створення BPF Maps", size=11, color="#37474f"))

    frags.append(rect(690, 105, 110, 110, fill="#ffffff", stroke="#2e7d32", rx=6))
    frags.append(text(745, 130, "Output", size=12, bold=True, color="#1b5e20"))
    frags.append(text(745, 160, "hist() / count()", size=11, color="#37474f"))
    frags.append(text(745, 180, "Форматоване", size=11, color="#37474f"))

    # Arrows user space
    frags.append(arrow(210, 160, 260, 160, color="#2e7d32", sw=2))
    frags.append(arrow(440, 160, 490, 160, color="#2e7d32", sw=2))

    # Kernel space container
    frags.append(rect(30, 260, 790, 195, fill="#fff3e0", stroke="#e65100", rx=8))
    frags.append(text(45, 285, "Простір ядра (Kernel Space / eBPF Runtime)", size=14, bold=True, color="#bf360c", anchor="start"))

    frags.append(rect(50, 305, 170, 130, fill="#ffffff", stroke="#e65100", rx=6))
    frags.append(text(135, 330, "eBPF Verifier", size=12, bold=True, color="#bf360c"))
    frags.append(text(135, 360, "Перевірка CFG графа", size=11, color="#37474f"))
    frags.append(text(135, 380, "Валідація пам'яті", size=11, color="#37474f"))
    frags.append(text(135, 400, "Заборони зациклення", size=11, color="#37474f"))

    frags.append(rect(250, 305, 170, 130, fill="#ffffff", stroke="#e65100", rx=6))
    frags.append(text(335, 330, "eBPF JIT Compiler", size=12, bold=True, color="#bf360c"))
    frags.append(text(335, 360, "Перетворення байткоду", size=11, color="#37474f"))
    frags.append(text(335, 380, "в інструкції ЦПУ", size=11, color="#37474f"))
    frags.append(text(335, 400, "x86_64 / ARM64", size=11, color="#37474f"))

    frags.append(rect(450, 305, 170, 130, fill="#ffffff", stroke="#e65100", rx=6))
    frags.append(text(535, 330, "Probes & Execution", size=12, bold=True, color="#bf360c"))
    frags.append(text(535, 360, "kprobe / kretprobe", size=11, color="#37474f"))
    frags.append(text(535, 380, "BPF Trampolines", size=11, color="#37474f"))
    frags.append(text(535, 400, "Tracepoints / USDT", size=11, color="#37474f"))

    frags.append(rect(650, 305, 150, 130, fill="#ffffff", stroke="#e65100", rx=6))
    frags.append(text(725, 330, "BPF Maps", size=12, bold=True, color="#bf360c"))
    frags.append(text(725, 360, "Hash / Array Maps", size=11, color="#37474f"))
    frags.append(text(725, 380, "Ring Buffer", size=11, color="#37474f"))
    frags.append(text(725, 400, "In-kernel Aggregation", size=11, color="#37474f"))

    # Connecting arrows user to kernel and kernel internal
    frags.append(arrow(570, 215, 135, 305, color="#e65100", sw=2))
    frags.append(arrow(220, 370, 250, 370, color="#e65100", sw=2))
    frags.append(arrow(420, 370, 450, 370, color="#e65100", sw=2))
    frags.append(arrow(620, 370, 650, 370, color="#e65100", sw=2))
    frags.append(arrow(725, 305, 745, 215, color="#2e7d32", sw=2))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "bpftrace-architecture.svg")
    render(out_path, 850, 480, *frags, title="Архітектура bpftrace та взаємодія з eBPF верифікатором")

def create_usdt_mechanism():
    frags = []

    # Column 1: ELF Binary File
    frags.append(rect(30, 60, 240, 370, fill="#e3f2fd", stroke="#1565c0", rx=8))
    frags.append(text(150, 85, "ELF виконуваний файл", size=14, bold=True, color="#0d47a1"))

    frags.append(rect(50, 110, 200, 135, fill="#ffffff", stroke="#1565c0", rx=6))
    frags.append(text(150, 135, "Секція .text (Інструкції)", size=12, bold=True, color="#0d47a1"))
    frags.append(text(150, 165, "Код програми...", size=11, color="#37474f"))
    frags.append(rect(65, 185, 170, 45, fill="#fff9c4", stroke="#fbc02d", rx=4))
    frags.append(text(150, 212, "NOP3 (0x90 0x90 0x90)", size=11, bold=True, color="#f57f17"))

    frags.append(rect(50, 265, 200, 145, fill="#ffffff", stroke="#1565c0", rx=6))
    frags.append(text(150, 290, "Секція .note.stapsdt", size=12, bold=True, color="#0d47a1"))
    frags.append(text(150, 320, "Provider: my_app", size=11, color="#37474f"))
    frags.append(text(150, 345, "Probe Name: request_start", size=11, color="#37474f"))
    frags.append(text(150, 370, "Arg Location: -8(%rbp)", size=11, color="#37474f"))

    # Column 2: Dynamic Activation
    frags.append(rect(305, 60, 240, 370, fill="#fff8e1", stroke="#ff8f00", rx=8))
    frags.append(text(425, 85, "Активація проби", size=14, bold=True, color="#e65100"))

    frags.append(rect(325, 110, 200, 135, fill="#ffffff", stroke="#ff8f00", rx=6))
    frags.append(text(425, 135, "Приєднання Трасувальника", size=12, bold=True, color="#e65100"))
    frags.append(text(425, 165, "Зчитування .note.stapsdt", size=11, color="#37474f"))
    frags.append(text(425, 190, "Пошук віртуальної адреси", size=11, color="#37474f"))

    frags.append(rect(325, 265, 200, 145, fill="#ffffff", stroke="#ff8f00", rx=6))
    frags.append(text(425, 290, "Патчинг пам'яті (Patching)", size=12, bold=True, color="#e65100"))
    frags.append(rect(340, 315, 170, 45, fill="#ffcdd2", stroke="#e53935", rx=4))
    frags.append(text(425, 342, "Заміна NOP3 на INT 3", size=11, bold=True, color="#c62828"))
    frags.append(text(425, 385, "або BPF Trampoline hook", size=11, color="#37474f"))

    # Column 3: Kernel Handler & Trace Result
    frags.append(rect(580, 60, 240, 370, fill="#f1f8e9", stroke="#558b2f", rx=8))
    frags.append(text(700, 85, "Обробка в ядрі", size=14, bold=True, color="#33691e"))

    frags.append(rect(600, 110, 200, 135, fill="#ffffff", stroke="#558b2f", rx=6))
    frags.append(text(700, 135, "Перехоплення Trap (INT 3)", size=12, bold=True, color="#33691e"))
    frags.append(text(700, 165, "Збереження контексту ЦПУ", size=11, color="#37474f"))
    frags.append(text(700, 190, "Зчитування аргументів", size=11, color="#37474f"))

    frags.append(rect(600, 265, 200, 145, fill="#ffffff", stroke="#558b2f", rx=6))
    frags.append(text(700, 290, "Виконання Дій (Action)", size=12, bold=True, color="#33691e"))
    frags.append(text(700, 320, "Запис у BPF Map", size=11, color="#37474f"))
    frags.append(text(700, 345, "Агрегація гістограми", size=11, color="#37474f"))
    frags.append(text(700, 370, "Повернення керування (IRET)", size=11, color="#37474f"))

    # Connection lines between columns
    frags.append(arrow(250, 177, 325, 177, color="#ff8f00", sw=2))
    frags.append(arrow(250, 337, 325, 337, color="#ff8f00", sw=2))
    frags.append(arrow(525, 337, 600, 177, color="#558b2f", sw=2))

    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out_path = os.path.join(img_dir, "usdt-mechanism.svg")
    render(out_path, 850, 460, *frags, title="Механізм статичної інструментації USDT у користувацькому коді")

def render_all():
    create_systemtap_pipeline()
    create_bpftrace_architecture()
    create_usdt_mechanism()

if __name__ == "__main__":
    render_all()
