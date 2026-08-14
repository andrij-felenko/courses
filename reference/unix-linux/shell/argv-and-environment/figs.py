import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_stack_layout(img_dir):
    w, h = 680, 520
    frags = []
    
    frags.append(text(w / 2, 25, "Макет верхівки стека при вході в _start (x86_64 ABI)", size=15, bold=True))
    
    frags.append(line(50, 50, 50, 480, color=MUTED, sw=2))
    frags.append(arrow(50, 480, 50, 45, color=MUTED, sw=2))
    frags.append(text(35, 60, "Високі адреси", size=11, color=MUTED, anchor="start", bold=True))
    frags.append(text(35, 495, "Низькі адреси", size=11, color=MUTED, anchor="start", bold=True))
    
    frags.append(rect(120, 50, 500, 90, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(370, 72, "Інформаційний блок (Information Block)", size=13, color="#92400e", bold=True))
    frags.append(mtext(370, 93, ["Символьні рядки: \"PATH=/usr/bin\\0\", \"USER=alex\\0\", \"/bin/ls\\0\", \"-l\\0\", \"/tmp\\0\"", "Апаратна платформа, 16 випадкових байтів для canary, вирівнювання (16 байт)"], size=11, color="#78350f"))
    
    frags.append(rect(120, 150, 500, 90, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(text(370, 172, "Допоміжний вектор (Auxiliary Vector — auxv)", size=13, color="#075985", bold=True))
    frags.append(mtext(370, 193, ["Пари Elf64_auxv_t { a_type, a_val/a_ptr }", "AT_PHDR, AT_ENTRY, AT_PAGESZ, AT_RANDOM, AT_SECURE ... завершується AT_NULL (0)"], size=11, color="#0c4a6e"))
    
    frags.append(rect(120, 250, 500, 75, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(370, 270, "Масив покажчиків середовища (envp[])", size=13, color="#166534", bold=True))
    frags.append(mtext(370, 291, ["char *envp[0] ──► \"PATH=...\",  char *envp[1] ──► \"USER=...\"", "Завершується покажчиком NULL (0x0)"], size=11, color="#14532d"))
    
    frags.append(rect(120, 335, 500, 75, fill="#f3e8ff", stroke="#9333ea", sw=1.5))
    frags.append(text(370, 355, "Масив покажчиків аргументів (argv[])", size=13, color="#6b21a8", bold=True))
    frags.append(mtext(370, 376, ["char *argv[0] ──► \"ls\",  char *argv[1] ──► \"-l\",  char *argv[2] ──► \"/tmp\"", "Завершується покажчиком NULL (0x0)"], size=11, color="#581c87"))
    
    frags.append(rect(120, 420, 500, 45, fill="#ffe4e6", stroke="#e11d48", sw=1.5))
    frags.append(text(370, 447, "Кількість аргументів argc (uint64_t = 3)", size=13, color="#9f1239", bold=True))
    
    frags.append(line(50, 442, 110, 442, color=POS, sw=2))
    frags.append(arrow(110, 442, 118, 442, color=POS, sw=2))
    frags.append(text(80, 432, "%rsp", size=12, color=POS, bold=True))
    
    path = os.path.join(img_dir, "initial-stack-layout.svg")
    svg_render(path, w, h, *frags)

def render_inheritance(img_dir):
    w, h = 720, 440
    frags = []
    
    frags.append(text(w / 2, 25, "Успадкування стану між fork() та execve()", size=15, bold=True))
    
    frags.append(rect(30, 50, 315, 360, fill="#f0f9ff", stroke="#0284c7", sw=1.5))
    frags.append(text(187, 75, "Системний виклик fork()", size=14, color="#0369a1", bold=True))
    frags.append(line(45, 88, 330, 88, color="#0284c7", sw=1))
    
    fork_items = [
        "• Точне клонування адресного простору (COW)",
        "• Збереження покажчиків argv та environ",
        "• Збереження відкритих файлових дескрипторів",
        "• Копіювання обробників сигналів",
        "• Новий PID, але той самий PPID",
        "• Збереження стану C-бібліотеки"
    ]
    frags.append(mtext(45, 115, fork_items, size=11, color="#0c4a6e", anchor="start", lh=1.8))
    
    frags.append(rect(375, 50, 315, 360, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    frags.append(text(532, 75, "Системний виклик execve()", size=14, color="#c2410c", bold=True))
    frags.append(line(390, 88, 675, 88, color="#ea580c", sw=1))
    
    exec_items = [
        "• Очищення старого адресного простору",
        "• Новий стек з нуля: argc, argv, envp, auxv",
        "• Дескриптори: зберігаються (якщо не O_CLOEXEC)",
        "• Сигнали: скидаються до SIG_DFL",
        "• Той самий PID, PPID, session/group ID",
        "• Збереження umask, cwd, rlimits",
        "• Credentials: UID/GID збережені"
    ]
    frags.append(mtext(390, 115, exec_items, size=11, color="#7c2d12", anchor="start", lh=1.8))
    
    path = os.path.join(img_dir, "inheritance-fork-exec.svg")
    svg_render(path, w, h, *frags)

def render():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    render_stack_layout(img_dir)
    render_inheritance(img_dir)

if __name__ == '__main__':
    render()
