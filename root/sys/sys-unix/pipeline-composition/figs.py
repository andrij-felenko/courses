import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_pipe_kernel_buffer(path):
    frags = []
    # Writer process box
    b1, _, _ = textbox(110, 180, "Процес 1\n(письменник)\nwrite(fd, buf)", size=13, fill="#fff3e0", stroke="#e65100", bold=True)
    frags.append(b1)

    # Kernel Space Container
    frags.append(rect(230, 40, 340, 280, fill="#f1f8e9", stroke="#33691e", sw=2, rx=8))
    frags.append(text(400, 70, "Простір ядра (Kernel Space)", size=15, color="#33691e", bold=True))

    # Ring buffer inside kernel
    frags.append(rect(250, 95, 300, 205, fill="#ffffff", stroke="#558b2f", sw=1.5, rx=6))
    frags.append(text(400, 120, "struct pipe_inode_info", size=13, color="#2e7d32", bold=True))
    frags.append(text(400, 140, "Кільцевий буфер (64 KB FIFO)", size=12, color=MUTED))

    # Slots
    slot_colors = ["#c8e6c9", "#c8e6c9", "#c8e6c9", "#fff9c4", "#ffffff", "#ffffff"]
    slot_labels = ["Байт1", "Байт2", "Байт3", "Head", "Вільн", "Tail"]
    for i in range(6):
        bx = 265 + i * 45
        frags.append(rect(bx, 165, 40, 50, fill=slot_colors[i], stroke="#81c784", sw=1.2, rx=3))
        frags.append(text(bx + 20, 195, slot_labels[i], size=10, color="#2e7d32"))

    frags.append(text(400, 245, "Черга FIFO (Mutex + WaitQueue)", size=12, color=INK, bold=True))
    frags.append(text(400, 275, "Порожньо → read() спить | Повно → write() спить", size=11, color=POS))

    # Reader process box
    b2, _, _ = textbox(690, 180, "Процес 2\n(читач)\nread(fd, buf)", size=13, fill="#e8eaf6", stroke="#1a237e", bold=True)
    frags.append(b2)

    # Arrows
    frags.append(arrow(180, 180, 245, 180, color="#e65100", sw=2))
    frags.append(arrow(555, 180, 615, 180, color="#1a237e", sw=2))

    render(path, 800, 360, *frags)

def build_pipe_fd_redirection(path):
    frags = []

    # 1. Shell Parent
    frags.append(rect(20, 30, 230, 360, fill="#ffffff", stroke="#78909c", sw=2, rx=6))
    frags.append(text(135, 60, "1. Оболонка (Shell)", size=14, color="#37474f", bold=True))
    frags.append(text(135, 80, "pipe(fds) → 3, 4", size=12, color="#00838f"))

    frags.append(rect(35, 105, 200, 160, fill="#eceff1", stroke="#b0bec5", rx=4))
    frags.append(text(135, 130, "Дескриптори", size=12, color="#455a64", bold=True))
    frags.append(text(135, 155, "0: stdin (tty)", size=11, color=INK))
    frags.append(text(135, 180, "1: stdout (tty)", size=11, color=INK))
    frags.append(text(135, 205, "3: pipe[0] (читання)", size=11, color="#00695c"))
    frags.append(text(135, 230, "4: pipe[1] (запис)", size=11, color="#ad1457"))

    frags.append(text(135, 300, "2. fork() 2 дітей", size=12, color="#d84315", bold=True))
    frags.append(text(135, 325, "3. close(3, 4) у батька", size=11, color=POS))

    # 2. Child 1 (Writer)
    frags.append(rect(295, 30, 240, 360, fill="#ffffff", stroke="#ef6c00", sw=2, rx=6))
    frags.append(text(415, 60, "2. Дитина 1 (ls)", size=14, color="#ef6c00", bold=True))
    frags.append(text(415, 80, "dup2(pipe[1], 1)", size=12, color="#e65100"))

    frags.append(rect(315, 105, 200, 200, fill="#fff3e0", stroke="#ffe0b2", rx=4))
    frags.append(text(415, 130, "Нові дескриптори", size=12, color="#e65100", bold=True))
    frags.append(text(415, 155, "0: stdin", size=11, color=INK))
    frags.append(text(415, 185, "1: stdout → PIPE WRITE", size=11, color=POS, bold=True))
    frags.append(text(415, 215, "3: close(pipe[0])", size=11, color=MUTED))
    frags.append(text(415, 245, "4: close(pipe[1])", size=11, color=MUTED))
    frags.append(text(415, 280, "execvp(\"ls\", ...)", size=12, color="#ef6c00", bold=True))

    # 3. Child 2 (Reader)
    frags.append(rect(565, 30, 240, 360, fill="#ffffff", stroke="#283593", sw=2, rx=6))
    frags.append(text(685, 60, "3. Дитина 2 (wc)", size=14, color="#283593", bold=True))
    frags.append(text(685, 80, "dup2(pipe[0], 0)", size=12, color="#1a237e"))

    frags.append(rect(585, 105, 200, 200, fill="#e8eaf6", stroke="#c5cae9", rx=4))
    frags.append(text(685, 130, "Нові дескриптори", size=12, color="#1a237e", bold=True))
    frags.append(text(685, 155, "0: stdin → PIPE READ", size=11, color="#1a237e", bold=True))
    frags.append(text(685, 185, "1: stdout (tty)", size=11, color=INK))
    frags.append(text(685, 215, "3: close(pipe[0])", size=11, color=MUTED))
    frags.append(text(685, 245, "4: close(pipe[1])", size=11, color=MUTED))
    frags.append(text(685, 280, "execvp(\"wc\", ...)", size=12, color="#283593", bold=True))

    # Pipe connection arrow between child 1 stdout and child 2 stdin
    frags.append(arrow(515, 185, 580, 155, color=POS, sw=2))

    render(path, 820, 420, *frags)

def build_multi_stage_pipeline(path):
    frags = []

    # Process Group Box
    frags.append(rect(30, 40, 740, 250, fill="#f0f4c3", stroke="#9e9d24", sw=1.5, rx=8))
    frags.append(text(400, 65, "Група процесів (Foreground Process Group, PGID)", size=13, color="#827717", bold=True))

    # Process 1
    b1, _, _ = textbox(140, 175, "Процес 1: cat\nstdin: log.txt\nstdout: Pipe 1", size=12, fill="#ffffff", stroke="#f57f17", bold=True)
    frags.append(b1)

    # Pipe 1
    b_p1, _, _ = textbox(290, 175, "Pipe 1\n64 KB", size=11, fill="#ffe0b2", stroke="#ffb74d", bold=True)
    frags.append(b_p1)

    # Process 2
    b2, _, _ = textbox(440, 175, "Процес 2: grep\nstdin: Pipe 1\nstdout: Pipe 2", size=12, fill="#ffffff", stroke="#0288d1", bold=True)
    frags.append(b2)

    # Pipe 2
    b_p2, _, _ = textbox(590, 175, "Pipe 2\n64 KB", size=11, fill="#b3e5fc", stroke="#81d4fa", bold=True)
    frags.append(b_p2)

    # Process 3
    b3, _, _ = textbox(700, 175, "Процес 3: wc\nstdin: Pipe 2\nstdout: tty", size=12, fill="#ffffff", stroke="#388e3c", bold=True)
    frags.append(b3)

    # Arrows
    frags.append(arrow(210, 175, 250, 175, color="#f57f17", sw=1.8))
    frags.append(arrow(325, 175, 365, 175, color="#0288d1", sw=1.8))
    frags.append(arrow(510, 175, 550, 175, color="#0288d1", sw=1.8))
    frags.append(arrow(625, 175, 650, 175, color="#388e3c", sw=1.8))

    render(path, 800, 310, *frags)

def render_all():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    # Видаляємо застарілі варіанти, якщо вони є
    old_files = ['fork-dup2.svg', 'pipe-buffer.svg']
    for old in old_files:
        p = os.path.join(img_dir, old)
        if os.path.exists(p):
            os.remove(p)

    build_pipe_kernel_buffer(os.path.join(img_dir, 'pipe-kernel-buffer.svg'))
    build_pipe_fd_redirection(os.path.join(img_dir, 'pipe-fd-redirection.svg'))
    build_multi_stage_pipeline(os.path.join(img_dir, 'multi-stage-pipeline.svg'))

if __name__ == '__main__':
    render_all()
