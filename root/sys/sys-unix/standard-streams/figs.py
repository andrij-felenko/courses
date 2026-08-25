import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, text, mtext, rect, line, arrow, circle, textbox, fitbox

def render_fig_descriptors(img_dir):
    w, h = 760, 360
    frags = []
    
    # Заголовок
    frags.append(text(w / 2, 25, "Анатомія файлових дескрипторів 0, 1, 2 у структурах ядра Linux", size=15, bold=True))
    
    # Секція Процесу (User Space / task_struct)
    frags.append(rect(20, 50, 220, 280, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(130, 75, "Процес (task_struct)", size=13, bold=True, color="#0f172a"))
    frags.append(rect(35, 90, 190, 30, fill="#e2e8f0", stroke="#cbd5e1", rx=4))
    frags.append(text(130, 110, "files_struct -> fd_array", size=11, bold=True, color="#334155"))
    
    # Дескриптори в процесі
    box0, _, _ = textbox(130, 150, "FD 0 (stdin)", size=12, pad=6, fill="#eff6ff", stroke="#3b82f6", bold=True)
    box1, _, _ = textbox(130, 210, "FD 1 (stdout)", size=12, pad=6, fill="#f0fdf4", stroke="#22c55e", bold=True)
    box2, _, _ = textbox(130, 270, "FD 2 (stderr)", size=12, pad=6, fill="#fef2f2", stroke="#ef4444", bold=True)
    frags.extend([box0, box1, box2])
    
    # Секція Таблиці відкритих файлів ядра (Kernel Open File Table)
    frags.append(rect(270, 50, 240, 280, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(390, 75, "Таблиця файлів ядра (struct file)", size=13, bold=True, color="#0f172a"))
    
    of0, _, _ = textbox(390, 150, "file #10 (O_RDONLY)\npos: 0, refcount: 2", size=11, pad=6, fill="#ffffff", stroke="#94a3b8")
    of1, _, _ = textbox(390, 210, "file #11 (O_WRONLY)\npos: 1024, refcount: 1", size=11, pad=6, fill="#ffffff", stroke="#94a3b8")
    of2, _, _ = textbox(390, 270, "file #12 (O_WRONLY)\npos: 512, refcount: 1", size=11, pad=6, fill="#ffffff", stroke="#94a3b8")
    frags.extend([of0, of1, of2])
    
    # Секція VFS Inode / Пристроїв
    frags.append(rect(540, 50, 200, 280, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=8))
    frags.append(text(640, 75, "Об'єкти VFS (struct inode)", size=13, bold=True, color="#581c87"))
    
    in0, _, _ = textbox(640, 150, "TTY (/dev/pts/0)\nПристрій термінала", size=11, pad=6, fill="#ffffff", stroke="#c084fc")
    in1, _, _ = textbox(640, 210, "out.txt (ext4)\nЗзвичайний файл", size=11, pad=6, fill="#ffffff", stroke="#c084fc")
    in2, _, _ = textbox(640, 270, "TTY (/dev/pts/0)\nПристрій термінала", size=11, pad=6, fill="#ffffff", stroke="#c084fc")
    frags.extend([in0, in1, in2])
    
    # Стрілки зв'язку FD -> File -> Inode
    frags.append(arrow(190, 150, 310, 150, color="#3b82f6", sw=1.8))
    frags.append(arrow(190, 210, 310, 210, color="#22c55e", sw=1.8))
    frags.append(arrow(190, 270, 310, 270, color="#ef4444", sw=1.8))
    
    frags.append(arrow(470, 150, 570, 150, color="#64748b", sw=1.5))
    frags.append(arrow(470, 210, 570, 210, color="#64748b", sw=1.5))
    frags.append(arrow(470, 270, 570, 270, color="#64748b", sw=1.5))
    
    path = os.path.join(img_dir, "standard-descriptors-architecture.svg")
    render(path, w, h, *frags)


def render_fig_buffering(img_dir):
    w, h = 760, 340
    frags = []
    
    frags.append(text(w / 2, 25, "Режими буферизації libc у просторі користувача (Standard I/O)", size=15, bold=True))
    
    # Колонка 1: Unbuffered (_IONBF)
    frags.append(rect(20, 50, 225, 270, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    frags.append(text(132, 75, "Без буферизації (_IONBF)", size=12, bold=True, color="#991b1b"))
    frags.append(text(132, 92, "За замовчуванням для stderr", size=10, italic=True, color="#7f1d1d"))
    
    b1_app, _, _ = textbox(132, 130, "Програма (fprintf)", size=11, pad=6, fill="#ffffff", stroke="#ef4444")
    b1_buf, _, _ = textbox(132, 185, "Буфер libc: 0 байт\n(Прямий транзит)", size=10, pad=6, fill="#fee2e2", stroke="#f87171")
    b1_sys, _, _ = textbox(132, 265, "Ядро: write(2, ...)\nМиттєве виведення", size=11, pad=6, fill="#334155", stroke="#0f172a", color="#ffffff")
    frags.extend([b1_app, b1_buf, b1_sys])
    frags.append(arrow(132, 150, 132, 165, color="#ef4444"))
    frags.append(arrow(132, 205, 132, 240, color="#ef4444"))
    
    # Колонка 2: Line buffered (_IOLBF)
    frags.append(rect(265, 50, 225, 270, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(377, 75, "Рядкова (_IOLBF)", size=12, bold=True, color="#166534"))
    frags.append(text(377, 92, "stdout -> Термінал (TTY)", size=10, italic=True, color="#14532d"))
    
    b2_app, _, _ = textbox(377, 130, "Програма (printf)", size=11, pad=6, fill="#ffffff", stroke="#22c55e")
    b2_buf, _, _ = textbox(377, 185, "Буфер libc: ~1 КБ\nСкидання при '\\n'", size=10, pad=6, fill="#dcfce7", stroke="#4ade80")
    b2_sys, _, _ = textbox(377, 265, "Ядро: write(1, ...)\nВиклик при newline", size=11, pad=6, fill="#334155", stroke="#0f172a", color="#ffffff")
    frags.extend([b2_app, b2_buf, b2_sys])
    frags.append(arrow(377, 150, 377, 165, color="#22c55e"))
    frags.append(arrow(377, 205, 377, 240, color="#22c55e"))
    
    # Колонка 3: Full buffered (_IOFBF)
    frags.append(rect(515, 50, 225, 270, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(627, 75, "Повна / Блокова (_IOFBF)", size=12, bold=True, color="#1e40af"))
    frags.append(text(627, 92, "stdout -> Файл / Pipe", size=10, italic=True, color="#1e3a8a"))
    
    b3_app, _, _ = textbox(627, 130, "Програма (fwrite)", size=11, pad=6, fill="#ffffff", stroke="#3b82f6")
    b3_buf, _, _ = textbox(627, 185, "Буфер libc: 4КБ / 8КБ\nСкидання при заповненні", size=10, pad=6, fill="#dbeafe", stroke="#60a5fa")
    b3_sys, _, _ = textbox(627, 265, "Ядро: write(1, ...)\nРідкісний системний виклик", size=11, pad=6, fill="#334155", stroke="#0f172a", color="#ffffff")
    frags.extend([b3_app, b3_buf, b3_sys])
    frags.append(arrow(627, 150, 627, 165, color="#3b82f6"))
    frags.append(arrow(627, 205, 627, 240, color="#3b82f6"))
    
    path = os.path.join(img_dir, "stdio-buffering-modes.svg")
    render(path, w, h, *frags)


def render_fig_redirection(img_dir):
    w, h = 760, 360
    frags = []
    
    frags.append(text(w / 2, 25, "Механізм перенаправлення стандартного виведення через dup2()", size=15, bold=True))
    
    # Крок 1: Батьківський процес
    frags.append(rect(20, 60, 220, 270, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(130, 85, "Крок 1: fork()", size=12, bold=True, color="#0f172a"))
    s1_t1, _, _ = textbox(130, 130, "Дочірній процес\nуспадковує FD 0, 1, 2", size=10, pad=6, fill="#ffffff")
    s1_t2, _, _ = textbox(130, 220, "FD 0 -> TTY\nFD 1 -> TTY\nFD 2 -> TTY", size=10, pad=6, fill="#eff6ff", stroke="#3b82f6")
    frags.extend([s1_t1, s1_t2])
    
    # Крок 2: Відкриття файлу
    frags.append(rect(270, 60, 220, 270, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(380, 85, "Крок 2: open()", size=12, bold=True, color="#0f172a"))
    s2_t1, _, _ = textbox(380, 130, "open(\"out.txt\", O_WRONLY)\nотримує дескриптор 3", size=10, pad=6, fill="#ffffff")
    s2_t2, _, _ = textbox(380, 220, "FD 1 -> TTY\nFD 3 -> out.txt", size=10, pad=6, fill="#fef3c7", stroke="#f59e0b")
    frags.extend([s2_t1, s2_t2])
    
    # Крок 3: dup2 + exec
    frags.append(rect(520, 60, 220, 270, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    frags.append(text(630, 85, "Крок 3: dup2(3,1) + exec", size=12, bold=True, color="#166534"))
    s3_t1, _, _ = textbox(630, 130, "dup2(3, 1); close(3);\nexecve(\"target\", ...)", size=10, pad=6, fill="#ffffff")
    s3_t2, _, _ = textbox(630, 220, "FD 1 -> out.txt!\n(Програма не знає,\nщо пише у файл)", size=10, pad=6, fill="#dcfce7", stroke="#22c55e", bold=True)
    frags.extend([s3_t1, s3_t2])
    
    # Стрілки між кроками
    frags.append(arrow(240, 195, 270, 195, color="#64748b", sw=2))
    frags.append(arrow(490, 195, 520, 195, color="#22c55e", sw=2))
    
    path = os.path.join(img_dir, "fork-dup2-redirection-flow.svg")
    render(path, w, h, *frags)


def build_all():
    topic_dir = os.path.dirname(__file__)
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    
    render_fig_descriptors(img_dir)
    render_fig_buffering(img_dir)
    render_fig_redirection(img_dir)

if __name__ == "__main__":
    build_all()
