import os
import sys

# 4 levels up to reach scripts/ from root/sys/sys-unix/command-history
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD, BG

def render_memory_vs_file(img_dir):
    w, h = 760, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Дворівнева архітектура історії: буфер пам'яті та файл на диску", size=15, bold=True))
    
    # Left container: Process memory
    frags.append(rect(30, 55, 330, 395, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(text(195, 82, "Простір пам'яті оболонки (Heap)", size=13, color="#1d4ed8", bold=True))
    frags.append(line(45, 95, 345, 95, color="#93c5fd", sw=1))
    
    # In-memory history structure
    frags.append(rect(45, 110, 300, 75, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=5))
    frags.append(text(195, 130, "Масив покажчиків the_history[]", size=12, color="#1e40af", bold=True))
    frags.append(mtext(195, 150, [
        "HIST_ENTRY** — динамічний масив покажчиків",
        "Обмеження: HISTSIZE (наприклад, 1000 елементів)"
    ], size=10, color="#1e3a8a", lh=1.3))
    
    # Entries list
    entries = [
        "the_history[0] ──► \"git status\"  (t = 1724589001)",
        "the_history[1] ──► \"make -j8\"     (t = 1724589015)",
        "the_history[2] ──► \"./app test\"    (t = 1724589042)",
        "...              ──► (поточні команди сесії)",
        "the_history[N] ──► \"exit\"         (t = 1724589110)"
    ]
    frags.append(rect(45, 200, 300, 130, fill="#ffffff", stroke="#93c5fd", sw=1, rx=5))
    frags.append(mtext(60, 222, entries, size=10, color="#1e293b", anchor="start", lh=1.4))
    
    frags.append(rect(45, 345, 300, 85, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(195, 365, "GNU History API (libhistory)", size=11, color="#334155", bold=True))
    frags.append(mtext(195, 385, [
        "add_history(line) — додавання в пам'ять",
        "history_get(offset) — вибірка за індексом",
        "history_search() — пошук (Ctrl+R)"
    ], size=10, color="#475569", lh=1.3))

    # Right container: Persistent file
    frags.append(rect(400, 55, 330, 395, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=8))
    frags.append(text(565, 82, "Постійне сховище (VFS / Диск)", size=13, color="#15803d", bold=True))
    frags.append(line(415, 95, 715, 95, color="#86efac", sw=1))
    
    frags.append(rect(415, 110, 300, 75, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=5))
    frags.append(text(565, 130, "Файл історії: ~/.bash_history", size=12, color="#166534", bold=True))
    frags.append(mtext(565, 150, [
        "Текстовий лог команд з мітками часу",
        "Обмеження: HISTFILESIZE (ліміт рядків файлу)"
    ], size=10, color="#14532d", lh=1.3))
    
    file_lines = [
        "#1724580000",
        "sudo apt update",
        "#1724580012",
        "vim /etc/hosts",
        "#1724589001",
        "git status"
    ]
    frags.append(rect(415, 200, 300, 130, fill="#ffffff", stroke="#86efac", sw=1, rx=5))
    frags.append(mtext(430, 222, file_lines, size=10, color="#1e293b", anchor="start", lh=1.35))
    
    frags.append(rect(415, 345, 300, 85, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=5))
    frags.append(text(565, 365, "Системні виклики синхронізації", size=11, color="#334155", bold=True))
    frags.append(mtext(565, 385, [
        "read_history() ──► open(), read()",
        "write_history() ──► open(O_TRUNC), write()",
        "append_history() ──► open(O_APPEND), write()"
    ], size=10, color="#475569", lh=1.3))

    # Center transition arrows
    # Startup arrow (File -> Memory)
    frags.append(arrow(415, 140, 350, 140, color="#2563eb", sw=2))
    frags.append(text(382, 130, "Старт", size=9, color="#2563eb", bold=True))

    # Exit arrow (Memory -> File)
    frags.append(arrow(345, 260, 410, 260, color="#16a34a", sw=2))
    frags.append(text(380, 250, "Вихід", size=9, color="#16a34a", bold=True))

    path = os.path.join(img_dir, "history-memory-vs-file.svg")
    render(path, w, h, *frags, title="Дворівнева архітектура історії команд")

def render_session_sync(img_dir):
    w, h = 760, 460
    frags = []
    
    frags.append(text(w / 2, 28, "Конкуренція терміналів та синхронізація через PROMPT_COMMAND", size=15, bold=True))
    
    # Left column: Session A
    frags.append(rect(30, 60, 210, 370, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(135, 85, "Термінал 1 (PID 1042)", size=12, color="#0f172a", bold=True))
    frags.append(line(45, 95, 225, 95, color="#cbd5e1", sw=1))
    
    frags.append(rect(45, 110, 180, 50, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    frags.append(text(135, 130, "Введення: $ cmd_A1", size=10, color="#1e40af"))
    frags.append(text(135, 145, "history -a (append)", size=9, color="#2563eb", bold=True))
    
    frags.append(rect(45, 220, 180, 50, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    frags.append(text(135, 240, "Введення: $ cmd_A2", size=10, color="#1e40af"))
    frags.append(text(135, 255, "history -a (append)", size=9, color="#2563eb", bold=True))
    
    frags.append(rect(45, 340, 180, 65, fill="#dbeafe", stroke="#1d4ed8", sw=1.2, rx=4))
    frags.append(text(135, 360, "PROMPT_COMMAND", size=10, color="#1e40af", bold=True))
    frags.append(text(135, 375, "history -n (read new)", size=9, color="#1d4ed8"))
    frags.append(text(135, 390, "Отримано cmd_B1", size=9, color="#15803d", bold=True))

    # Center column: ~/.bash_history
    frags.append(rect(275, 60, 210, 370, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(380, 85, "Файл ~/.bash_history", size=12, color="#15803d", bold=True))
    frags.append(line(290, 95, 470, 95, color="#86efac", sw=1))
    
    frags.append(rect(290, 115, 180, 295, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    history_file_content = [
        "1: [початкові команди]",
        "2: ...",
        "3: cmd_A1  (від PID 1042)",
        "4: cmd_B1  (від PID 2088)",
        "5: cmd_A2  (від PID 1042)",
        "6: cmd_B2  (від PID 2088)"
    ]
    frags.append(mtext(300, 145, history_file_content, size=10, color="#1e293b", anchor="start", lh=1.8))

    # Right column: Session B
    frags.append(rect(520, 60, 210, 370, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(625, 85, "Термінал 2 (PID 2088)", size=12, color="#0f172a", bold=True))
    frags.append(line(535, 95, 715, 95, color="#cbd5e1", sw=1))
    
    frags.append(rect(535, 165, 180, 50, fill="#fef2f2", stroke="#ef4444", sw=1, rx=4))
    frags.append(text(625, 185, "Введення: $ cmd_B1", size=10, color="#991b1b"))
    frags.append(text(625, 200, "history -a (append)", size=9, color="#dc2626", bold=True))
    
    frags.append(rect(535, 280, 180, 50, fill="#fef2f2", stroke="#ef4444", sw=1, rx=4))
    frags.append(text(625, 300, "Введення: $ cmd_B2", size=10, color="#991b1b"))
    frags.append(text(625, 315, "history -a (append)", size=9, color="#dc2626", bold=True))

    # Append arrows to center
    frags.append(arrow(225, 135, 285, 175, color="#2563eb", sw=1.5))
    frags.append(arrow(535, 190, 475, 205, color="#dc2626", sw=1.5))
    frags.append(arrow(225, 245, 285, 235, color="#2563eb", sw=1.5))
    frags.append(arrow(535, 305, 475, 265, color="#dc2626", sw=1.5))

    # Read new arrow back to Session A
    frags.append(arrow(290, 215, 225, 360, color="#15803d", sw=1.5))

    path = os.path.join(img_dir, "history-session-sync.svg")
    render(path, w, h, *frags, title="Синхронізація історії між термінальними сесіями")

def render_expansion_pipeline(img_dir):
    w, h = 760, 440
    frags = []
    
    frags.append(text(w / 2, 28, "Конвеєр обробки рядка введення: місце історії та фільтрації", size=15, bold=True))
    
    # Stage 1: Raw input
    frags.append(rect(30, 70, 150, 80, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    frags.append(text(105, 95, "1. Сире введення", size=12, color="#0f172a", bold=True))
    frags.append(mtext(105, 115, ["Рядок від Readline:", "\"sudo !!; echo $?\""], size=10, color="#334155", lh=1.3))
    
    # Arrow 1 -> 2
    frags.append(arrow(180, 110, 215, 110, color="#64748b", sw=1.8))
    
    # Stage 2: History Expansion
    frags.append(rect(220, 70, 170, 80, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(305, 95, "2. History Expansion", size=12, color="#92400e", bold=True))
    frags.append(mtext(305, 115, ["Розкриття !, !!, !$, ^old^new", "Виконується ПЕРШИМ"], size=10, color="#b45309", lh=1.3))
    
    # Arrow 2 -> 3
    frags.append(arrow(390, 110, 425, 110, color="#64748b", sw=1.8))
    
    # Stage 3: History Filtering
    frags.append(rect(430, 70, 160, 80, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=6))
    frags.append(text(510, 95, "3. Фільтрація історії", size=12, color="#991b1b", bold=True))
    frags.append(mtext(510, 115, ["HISTCONTROL (space/dups)", "HISTIGNORE (маски)"], size=10, color="#b91c1c", lh=1.3))
    
    # Arrow 3 -> 4 (Memory save) and Arrow 3 -> 5 (Execution)
    frags.append(arrow(510, 150, 510, 195, color="#ef4444", sw=1.5))
    frags.append(arrow(590, 110, 625, 110, color="#64748b", sw=1.8))
    
    # Stage 4: Add to buffer
    frags.append(rect(430, 200, 160, 75, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(510, 225, "add_history()", size=12, color="#1e40af", bold=True))
    frags.append(mtext(510, 245, ["Запис у кільцевий", "буфер пам'яті"], size=10, color="#2563eb", lh=1.3))

    # Stage 5: Normal shell parsing
    frags.append(rect(630, 70, 100, 340, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(680, 95, "4. Синтаксис", size=11, color="#15803d", bold=True))
    frags.append(mtext(680, 130, [
        "Alias",
        "───",
        "Brace",
        "───",
        "Tilde",
        "───",
        "Parameter",
        "───",
        "Command sub",
        "───",
        "Arithmetic",
        "───",
        "Word split",
        "───",
        "Path glob",
        "───",
        "Quote removal",
        "───",
        "EXECVE()"
    ], size=9, color="#166534", lh=1.2))

    # Explanation text box at the bottom
    frags.append(rect(30, 290, 360, 120, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(210, 312, "Важливий порядок виконання:", size=11, color="#0f172a", bold=True))
    frags.append(mtext(45, 335, [
        "• Розкриття історії (!) відбувається ДО того, як оболонка",
        "  розпізнає лапки, змінні чи підстановку команд.",
        "• Рядок із подвійними лапками \"echo !$\" все одно розкриється.",
        "• Рядок із одинарними лапками 'echo !$' НЕ розкривається.",
        "• ignorespace ігнорує рядок, якщо перший символ — пробіл."
    ], size=10, color="#334155", anchor="start", lh=1.4))

    path = os.path.join(img_dir, "history-expansion-ast.svg")
    render(path, w, h, *frags, title="Послідовність розкриття історії та фільтрації")

def render_all():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    
    render_memory_vs_file(img_dir)
    render_session_sync(img_dir)
    render_expansion_pipeline(img_dir)

if __name__ == '__main__':
    render_all()
