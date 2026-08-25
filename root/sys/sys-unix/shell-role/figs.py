import sys
import os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, textbox, fitbox, arrow, line, rect, text, mtext, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def generate_repl_cycle(img_dir):
    w, h = 850, 360
    frags = []

    # Тло та заголовок
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    # Блоки циклу
    # 1. Prompt / Read Line
    b1, w1, h1 = textbox(110, 120, "1. Read\nВведення рядка\nReadline / prompt", size=13, pad=12, fill="#eef6ff", stroke="#3b82f6", bold=True)
    frags.append(b1)

    # 2. Tokenize & Parse AST
    b2, w2, h2 = textbox(280, 120, "2. Parse\nЛексер та парсер\nПобудова AST", size=13, pad=12, fill="#f0fdf4", stroke="#22c55e", bold=True)
    frags.append(b2)

    # 3. Expansion Pipeline
    b3, w3, h3 = textbox(450, 120, "3. Expand\n7 фаз розширення\n$, glob, quotes", size=13, pad=12, fill="#fefce8", stroke="#eab308", bold=True)
    frags.append(b3)

    # 4. Fork & FD Plumbing
    b4, w4, h4 = textbox(620, 120, "4. Orchestrate\nfork(), pipe(), dup2()\nПеренаправлення", size=13, pad=12, fill="#faf5ff", stroke="#a855f7", bold=True)
    frags.append(b4)

    # 5. Exec & Wait Status
    b5, w5, h5 = textbox(770, 120, "5. Exec & Wait\nexecve(), waitpid()\nКод виходу $?", size=13, pad=12, fill="#fff1f2", stroke="#f43f5e", bold=True)
    frags.append(b5)

    # Горизонтальні стрілки між кроками
    frags.append(arrow(110 + w1/2, 120, 280 - w2/2, 120, color="#3b82f6", sw=2))
    frags.append(arrow(280 + w2/2, 120, 450 - w3/2, 120, color="#22c55e", sw=2))
    frags.append(arrow(450 + w3/2, 120, 620 - w4/2, 120, color="#eab308", sw=2))
    frags.append(arrow(620 + w4/2, 120, 770 - w5/2, 120, color="#a855f7", sw=2))

    # Зворотний зв'язок (Loop back to Read)
    # Лінія вниз від 5, вліво до 1, вгору до 1
    frags.append(line(770, 120 + h5/2, 770, 280, color="#64748b", sw=1.5, dash="4,4"))
    frags.append(line(770, 280, 110, 280, color="#64748b", sw=1.5, dash="4,4"))
    frags.append(arrow(110, 280, 110, 120 + h1/2, color="#64748b", sw=1.5))

    # Пояснення зворотного шляху
    frags.append(rect(340, 260, 200, 36, fill="#f8fafc", stroke="#cbd5e1", rx=4))
    frags.append(text(440, 282, "Повернення у REPL (Prompt)", size=12, color="#475569", anchor="middle", bold=True))

    path = os.path.join(img_dir, "repl-cycle.svg")
    render(path, w, h, *frags, title="Цикл REPL та етапи обробки команди в оболонці")

def generate_pipeline_fd_wiring(img_dir):
    w, h = 820, 380
    frags = []

    # Тло
    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=8))

    # Крок 1: Батьківська оболонка робить pipe()
    b_shell, ws, hs = textbox(180, 90, "Батьківська оболонка (PID 1000)\n1. pipe(pfd) -> pfd[0]=3, pfd[1]=4\n2. fork() -> Child 1 & Child 2", size=13, pad=10, fill="#f0f9ff", stroke="#0284c7", bold=True)
    frags.append(b_shell)

    # Крок 2: Дочірній 1 (cmd1)
    b_c1, wc1, hc1 = textbox(220, 260, "Дочірній 1: cmd1 (PID 1001)\ndup2(pfd[1], 1)  [stdout -> pipe write]\nclose(pfd[0]); execve(\"/bin/cmd1\")", size=12, pad=10, fill="#f0fdf4", stroke="#16a34a", bold=True)
    frags.append(b_c1)

    # Крок 3: Дочірній 2 (cmd2)
    b_c2, wc2, hc2 = textbox(600, 260, "Дочірній 2: cmd2 (PID 1002)\ndup2(pfd[0], 0)  [stdin <- pipe read]\nfd_out=open(\"out.txt\"); dup2(fd_out, 1)\nexecve(\"/bin/cmd2\")", size=12, pad=10, fill="#faf5ff", stroke="#9333ea", bold=True)
    frags.append(b_c2)

    # Буфер каналу (Kernel Pipe Buffer)
    b_pipe, wp, hp = textbox(410, 170, "Kernel Pipe Buffer\n(Кільцевий буфер 64 KB)", size=12, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(b_pipe)

    # Файл призначення
    b_file, wf, hf = textbox(740, 90, "Файл на диску\nout.txt", size=12, pad=8, fill="#f1f5f9", stroke="#475569", bold=True)
    frags.append(b_file)

    # Стрілки зв'язку
    # Батько -> Дочірній 1
    frags.append(arrow(180, 90 + hs/2, 220, 260 - hc1/2, color="#0284c7", sw=1.5))

    # Батько -> Дочірній 2
    frags.append(arrow(180 + ws/4, 90 + hs/2, 600 - wc2/4, 260 - hc2/2, color="#0284c7", sw=1.5))

    # Дочірній 1 -> Pipe Buffer (Write)
    frags.append(arrow(220 + wc1/2, 260, 410 - wp/2, 170 + hp/4, color="#16a34a", sw=2))

    # Pipe Buffer -> Дочірній 2 (Read)
    frags.append(arrow(410 + wp/2, 170 + hp/4, 600 - wc2/2, 260, color="#9333ea", sw=2))

    # Дочірній 2 -> File (Redirect stdout)
    frags.append(arrow(600 + wc2/4, 260 - hc2/2, 740, 90 + hf/2, color="#9333ea", sw=2))

    path = os.path.join(img_dir, "pipeline-fd-wiring.svg")
    render(path, w, h, *frags, title="Комутація файлових дескрипторів ядра для конвеєра: cmd1 | cmd2 > out.txt")

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    generate_repl_cycle(img_dir)
    generate_pipeline_fd_wiring(img_dir)

if __name__ == "__main__":
    main()
