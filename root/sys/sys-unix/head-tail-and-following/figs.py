import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_lseek_vs_ringbuf(img_dir):
    w, h = 740, 420
    frags = []
    
    frags.append(text(w / 2, 25, "Анатомія tail: прямий реверсивний lseek проти кільцевого буфера в RAM", size=15, bold=True))
    
    # Left Box: Seekable File
    frags.append(rect(25, 50, 335, 345, fill="#f0f9ff", stroke="#0284c7", sw=1.5))
    frags.append(text(192, 75, "Регулярний файл (Seekable)", size=14, color="#0369a1", bold=True))
    frags.append(line(40, 88, 345, 88, color="#0284c7", sw=1))
    
    frags.append(rect(50, 105, 285, 70, fill="#ffffff", stroke="#38bdf8", sw=1))
    frags.append(text(192, 125, "Великий файл на диску (наприклад, 100 ГБ)", size=11, color="#0369a1", bold=True))
    frags.append(text(192, 145, "[Початок ... 99.99 ГБ даних ... Кінець (EOF)]", size=10, color=MUTED))
    frags.append(text(192, 162, "lseek(fd, 0, SEEK_END) ──► дізнаємося розмір", size=10, color="#0284c7"))
    
    frags.append(arrow(192, 180, 192, 205, color="#0284c7", sw=1.5))
    
    frags.append(rect(50, 210, 285, 75, fill="#e0f2fe", stroke="#0284c7", sw=1.2))
    frags.append(text(192, 230, "Зсув назад: lseek(fd, -BUFSIZ, SEEK_CUR)", size=11, color="#075985", bold=True))
    frags.append(text(192, 250, "Сканування блоку 8 КіБ реверсивно на '\\n'", size=10, color="#0c4a6e"))
    frags.append(text(192, 268, "Знайдено N рядків ──► зсув вперед на точний офсет", size=10, color="#0c4a6e"))
    
    frags.append(rect(50, 300, 285, 80, fill="#f0fdf4", stroke="#16a34a", sw=1.2))
    frags.append(text(192, 320, "Результат: Час виконання O(K)", size=12, color="#15803d", bold=True))
    frags.append(mtext(192, 340, ["• Читання лише останніх кількох кілобайтів", "• Нуль навантаження на диск і RAM", "• Миттєва відповідь незалежно від обсягу"], size=10, color="#166534", lh=1.3))
    
    # Right Box: Non-seekable Stream
    frags.append(rect(380, 50, 335, 345, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    frags.append(text(547, 75, "Канал / сокет / stdin (Non-seekable)", size=14, color="#c2410c", bold=True))
    frags.append(line(395, 88, 700, 88, color="#ea580c", sw=1))
    
    frags.append(rect(405, 105, 285, 70, fill="#ffffff", stroke="#fb923c", sw=1))
    frags.append(text(547, 125, "Вхідний потік через pipe (безкінечний)", size=11, color="#c2410c", bold=True))
    frags.append(text(547, 145, "lseek() повертає -1 (errno = ESPIPE)", size=10, color=POS, bold=True))
    frags.append(text(547, 162, "Потік можна читати лише послідовно вперед", size=10, color=MUTED))
    
    frags.append(arrow(547, 180, 547, 205, color="#ea580c", sw=1.5))
    
    frags.append(rect(405, 210, 285, 75, fill="#ffedd5", stroke="#ea580c", sw=1.2))
    frags.append(text(547, 230, "Кільцевий буфер (Ring Buffer) у RAM", size=11, color="#9a3412", bold=True))
    frags.append(text(547, 250, "Збереження останніх N рядків у пам'яті", size=10, color="#7c2d12"))
    frags.append(text(547, 268, "Новий рядок витісняє найстаріший у буфері", size=10, color="#7c2d12"))
    
    frags.append(rect(405, 300, 285, 80, fill="#fef2f2", stroke="#dc2626", sw=1.2))
    frags.append(text(547, 320, "Результат: Час O(N), Пам'ять O(K)", size=12, color="#b91c1c", bold=True))
    frags.append(mtext(547, 340, ["• Прокачування 100% обсягу вхідного потоку", "• Споживання RAM обмежене розміром буфера", "• Вивід на stdout лише після отримання EOF"], size=10, color="#991b1b", lh=1.3))
    
    path = os.path.join(img_dir, "tail-lseek-vs-ringbuf.svg")
    svg_render(path, w, h, *frags)

def render_follow_rotation(img_dir):
    w, h = 740, 420
    frags = []
    
    frags.append(text(w / 2, 25, "Механіка стеження за логами: tail -f проти tail -F при ротації", size=15, bold=True))
    
    # Left Panel: tail -f
    frags.append(rect(25, 50, 335, 345, fill="#fef2f2", stroke="#ef4444", sw=1.5))
    frags.append(text(192, 75, "tail -f (--follow=descriptor)", size=14, color="#b91c1c", bold=True))
    frags.append(line(40, 88, 345, 88, color="#ef4444", sw=1))
    
    frags.append(rect(45, 100, 295, 55, fill="#ffffff", stroke="#f87171", sw=1))
    frags.append(text(192, 118, "1. Відкриття файлу app.log", size=11, color="#991b1b", bold=True))
    frags.append(text(192, 138, "Прив'язка fd ──► Inode #1042 (app.log)", size=10, color=MUTED))
    
    frags.append(arrow(192, 160, 192, 175, color="#ef4444", sw=1.5))
    
    frags.append(rect(45, 180, 295, 85, fill="#fee2e2", stroke="#ef4444", sw=1))
    frags.append(text(192, 198, "2. Відбувається ротація logrotate", size=11, color="#991b1b", bold=True))
    frags.append(text(192, 218, "rename(\"app.log\", \"app.log.1\")", size=10, color="#7f1d1d"))
    frags.append(text(192, 235, "Сервіс відкриває новий файл Inode #2099", size=10, color="#7f1d1d"))
    frags.append(text(192, 252, "Inode #1042 перейменовано на app.log.1", size=10, color="#7f1d1d"))
    
    frags.append(arrow(192, 270, 192, 285, color="#ef4444", sw=1.5))
    
    frags.append(rect(45, 290, 295, 90, fill="#ffffff", stroke="#dc2626", sw=1.2))
    frags.append(text(192, 310, "3. Наслідок: втрата потоку подій", size=12, color="#991b1b", bold=True))
    frags.append(mtext(192, 330, ["• tail -f утримує старий fd до Inode #1042", "• Нові записи у свіжий app.log ігноруються", "• Стеження зависає на заархівованому лозі"], size=10, color="#7f1d1d", lh=1.3))
    
    # Right Panel: tail -F
    frags.append(rect(380, 50, 335, 345, fill="#f0fdf4", stroke="#22c55e", sw=1.5))
    frags.append(text(547, 75, "tail -F (--follow=name --retry)", size=14, color="#15803d", bold=True))
    frags.append(line(395, 88, 700, 88, color="#22c55e", sw=1))
    
    frags.append(rect(400, 100, 295, 55, fill="#ffffff", stroke="#4ade80", sw=1))
    frags.append(text(547, 118, "1. Відкриття файлу app.log + inotify", size=11, color="#166534", bold=True))
    frags.append(text(547, 138, "Стеження за Inode #1042 та каталогом", size=10, color=MUTED))
    
    frags.append(arrow(547, 160, 547, 175, color="#22c55e", sw=1.5))
    
    frags.append(rect(400, 180, 295, 85, fill="#dcfce7", stroke="#22c55e", sw=1))
    frags.append(text(547, 198, "2. Відбувається ротація logrotate", size=11, color="#166534", bold=True))
    frags.append(text(547, 218, "inotify ловить IN_MOVE_SELF / IN_CREATE", size=10, color="#14532d"))
    frags.append(text(547, 235, "tail -F виявляє зміну Inode або видалення", size=10, color="#14532d"))
    frags.append(text(547, 252, "Закриття старого fd, очікування за іменем", size=10, color="#14532d"))
    
    frags.append(arrow(547, 270, 547, 285, color="#22c55e", sw=1.5))
    
    frags.append(rect(400, 290, 295, 90, fill="#ffffff", stroke="#16a34a", sw=1.2))
    frags.append(text(547, 310, "3. Наслідок: безперервний моніторинг", size=12, color="#15803d", bold=True))
    frags.append(mtext(547, 330, ["• Перевідкриття нового файлу Inode #2099", "• Скидання зміщення на 0 байт", "• Логування продовжується без зупинки"], size=10, color="#14532d", lh=1.3))
    
    path = os.path.join(img_dir, "tail-follow-rotation.svg")
    svg_render(path, w, h, *frags)

def render_pipeline_sigpipe(img_dir):
    w, h = 740, 360
    frags = []
    
    frags.append(text(w / 2, 25, "Переривання конвеєра: вихід head та надсилання SIGPIPE", size=15, bold=True))
    
    # Stage 1: Producer
    frags.append(rect(30, 60, 180, 100, fill="#eff6ff", stroke="#3b82f6", sw=1.5))
    frags.append(text(120, 85, "Процес-генератор", size=13, color="#1d4ed8", bold=True))
    frags.append(text(120, 105, "yes / cat / seq / find", size=11, color="#1e40af"))
    frags.append(text(120, 130, "write(pipefd[1], buf, sz)", size=10, color=MUTED))
    
    # Arrow to pipe
    frags.append(arrow(210, 110, 265, 110, color="#3b82f6", sw=2))
    frags.append(text(237, 98, "Потік", size=10, color="#3b82f6"))
    
    # Stage 2: Pipe Buffer in Kernel
    frags.append(rect(270, 60, 190, 100, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(365, 85, "Ядерний буфер pipe", size=13, color="#334155", bold=True))
    frags.append(text(365, 105, "Кільце сторінок (64 КіБ)", size=11, color="#475569"))
    frags.append(text(365, 130, "Черга передачі байтів", size=10, color=MUTED))
    
    # Arrow to Consumer
    frags.append(arrow(460, 110, 515, 110, color="#10b981", sw=2))
    frags.append(text(487, 98, "read()", size=10, color="#10b981"))
    
    # Stage 3: Consumer (head)
    frags.append(rect(520, 60, 190, 100, fill="#ecfdf5", stroke="#10b981", sw=1.5))
    frags.append(text(615, 85, "head -n 10", size=13, color="#047857", bold=True))
    frags.append(text(615, 105, "Отримано 10 рядків", size=11, color="#065f46"))
    frags.append(text(615, 130, "Виклик exit(0)", size=11, color=POS, bold=True))
    
    # Step 2: Broken Pipe & Signal
    frags.append(rect(30, 190, 680, 140, fill="#fff1f2", stroke="#f43f5e", sw=1.5))
    frags.append(text(370, 215, "Послідовність розриву каналу (Broken Pipe)", size=13, color="#be123c", bold=True))
    
    steps = [
        "1. head завершує роботу ──► ядро автоматично закриває читацький дескриптор pipefd[0]",
        "2. У каналі не залишається жодного відкритого дескриптора на читання",
        "3. Генератор виконує черговий виклик write() ──► ядро генерує сигнал SIGPIPE (13)",
        "4. За замовчуванням генератор миттєво завершується; write() повертає -1 (errno = EPIPE)"
    ]
    frags.append(mtext(50, 240, steps, size=11, color="#881337", anchor="start", lh=1.4))
    
    path = os.path.join(img_dir, "pipeline-sigpipe-flow.svg")
    svg_render(path, w, h, *frags)

def render():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    render_lseek_vs_ringbuf(img_dir)
    render_follow_rotation(img_dir)
    render_pipeline_sigpipe(img_dir)

if __name__ == '__main__':
    render()
