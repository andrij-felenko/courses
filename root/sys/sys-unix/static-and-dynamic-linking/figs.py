import os
import sys

# Add root scripts/ directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    render, rect, text, mtext, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG, FONT
)

def build_static_linking_diagram(path):
    w, h = 820, 420
    frags = []

    # Title card
    frags.append(text(w / 2, 28, "Статичне лінкування: вбудовування об'єктних модулів під час компіляції", size=16, bold=True))

    # Object Files Box (Left)
    frags.append(rect(30, 60, 220, 310, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(140, 85, "Власні об'єктні файли", size=14, bold=True, color="#1e293b"))
    frags.append(fitbox(45, 110, 190, 50, "main.o\n(викликає sin, cos)", size=13, fill="#e2e8f0", stroke="#cbd5e1"))
    frags.append(fitbox(45, 175, 190, 50, "utils.o\n(допоміжні функції)", size=13, fill="#e2e8f0", stroke="#cbd5e1"))
    frags.append(fitbox(45, 240, 190, 110, "Таблиця невирішених\nсимволів:\n• sin -> ???\n• cos -> ???", size=12, fill="#fff1f2", stroke="#fecdd3", color="#991b1b"))

    # Static Archive Box (Middle Bottom)
    frags.append(rect(290, 220, 240, 150, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(410, 245, "Статичний архів libmath.a", size=14, bold=True, color="#166534"))
    frags.append(fitbox(305, 265, 100, 40, "trig.o\n(sin, cos)", size=12, fill="#dcfce7", stroke="#4ade80", bold=True))
    frags.append(fitbox(415, 265, 100, 40, "matrix.o\n(det, inv)", size=12, fill="#f1f5f9", stroke="#cbd5e1", color=MUTED))
    frags.append(fitbox(305, 315, 210, 40, "Індекс символів (ranlib):\nsin -> trig.o, cos -> trig.o", size=11, fill="#ffffff", stroke="#bbf7d0"))

    # Linker ld (Middle Top)
    frags.append(fitbox(340, 80, 140, 80, "Компонувальник\nld\n(статичний режим)", size=14, fill="#e0f2fe", stroke="#0284c7", bold=True, color="#0369a1"))

    # Output Binary Box (Right)
    frags.append(rect(570, 60, 220, 310, fill="#fdf4ff", stroke="#f5d0fe", sw=1.5, rx=8))
    frags.append(text(680, 85, "Виконуваний файл (ELF)", size=14, bold=True, color="#701a75"))
    frags.append(fitbox(585, 110, 190, 45, "Заголовок ELF + Phdr", size=12, fill="#fae8ff", stroke="#e9d5ff"))
    frags.append(fitbox(585, 165, 190, 45, "Секція .text: main.o", size=12, fill="#e2e8f0", stroke="#cbd5e1"))
    frags.append(fitbox(585, 220, 190, 45, "Секція .text: utils.o", size=12, fill="#e2e8f0", stroke="#cbd5e1"))
    frags.append(fitbox(585, 275, 190, 45, "Вбудований trig.o\n(скопійовано з .a)", size=12, fill="#dcfce7", stroke="#22c55e", bold=True, color="#15803d"))
    frags.append(fitbox(585, 330, 190, 30, "Всі посилання вирішено!", size=11, fill="#f0fdf4", stroke="#86efac", color="#166534"))

    # Arrows
    frags.append(arrow(250, 120, 340, 120, color="#0284c7", sw=2))
    frags.append(arrow(410, 220, 410, 160, color="#166534", sw=2))
    frags.append(arrow(480, 120, 570, 120, color="#701a75", sw=2))

    render(path, w, h, *frags)

def build_dynamic_linking_diagram(path):
    w, h = 840, 440
    frags = []

    frags.append(text(w / 2, 26, "Динамічне лінкування: розділення фізичної пам'яті (Page Sharing)", size=16, bold=True))

    # Process 1 (Virtual Memory)
    frags.append(rect(30, 55, 230, 360, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(145, 80, "Процес A (PID 1001)", size=14, bold=True, color="#1e293b"))
    frags.append(text(145, 98, "Віртуальний адресний простір", size=11, color=MUTED))
    frags.append(fitbox(45, 115, 200, 50, "Код app_A (.text)\n[Read-Only]", size=12, fill="#e2e8f0", stroke="#cbd5e1"))
    frags.append(fitbox(45, 180, 200, 60, "Віртуальні сторінки коду\nlibc.so (.text)\n0x7f8a1000 - 0x7f8a3000", size=11, fill="#dbeafe", stroke="#3b82f6", bold=True, color="#1d4ed8"))
    frags.append(fitbox(45, 255, 200, 60, "Приватна GOT / .data\nlibc.so (Copy-on-Write)\nзмінні процесу A", size=11, fill="#fef3c7", stroke="#f59e0b", color="#b45309"))
    frags.append(fitbox(45, 330, 200, 70, "Стеки / Купа процесу A", size=12, fill="#f1f5f9", stroke="#cbd5e1"))

    # Physical RAM (Middle)
    frags.append(rect(305, 55, 230, 360, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=8))
    frags.append(text(420, 80, "Фізична ОЗУ (RAM)", size=14, bold=True, color="#15803d"))
    frags.append(text(420, 98, "Фізичні фрейми сторінок", size=11, color=MUTED))
    frags.append(fitbox(320, 115, 200, 50, "RAM Фрейм 0x1A40:\nКод app_A", size=12, fill="#f1f5f9", stroke="#cbd5e1"))
    frags.append(fitbox(320, 175, 200, 70, "ЄДИНИЙ ФІЗИЧНИЙ ФРЕЙМ:\nІнструкції libc.so (.text)\n(Завантажено 1 раз в ОЗУ)", size=12, fill="#bfdbfe", stroke="#2563eb", bold=True, color="#1e40af"))
    frags.append(fitbox(320, 260, 200, 60, "RAM Фрейм 0x2C10:\nДані libc (для Процесу A)", size=11, fill="#fef3c7", stroke="#f59e0b", color="#b45309"))
    frags.append(fitbox(320, 335, 200, 60, "RAM Фрейм 0x2C90:\nДані libc (для Процесу B)", size=11, fill="#ffedd5", stroke="#f97316", color="#c2410c"))

    # Process 2 (Virtual Memory)
    frags.append(rect(580, 55, 230, 360, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(695, 80, "Процес B (PID 1002)", size=14, bold=True, color="#1e293b"))
    frags.append(text(695, 98, "Віртуальний адресний простір", size=11, color=MUTED))
    frags.append(fitbox(595, 115, 200, 50, "Код app_B (.text)\n[Read-Only]", size=12, fill="#e2e8f0", stroke="#cbd5e1"))
    frags.append(fitbox(595, 180, 200, 60, "Віртуальні сторінки коду\nlibc.so (.text)\n0x7f3b4000 - 0x7f3b6000", size=11, fill="#dbeafe", stroke="#3b82f6", bold=True, color="#1d4ed8"))
    frags.append(fitbox(595, 255, 200, 60, "Приватна GOT / .data\nlibc.so (Copy-on-Write)\nзмінні процесу B", size=11, fill="#ffedd5", stroke="#f97316", color="#c2410c"))
    frags.append(fitbox(595, 330, 200, 70, "Стеки / Купа процесу B", size=12, fill="#f1f5f9", stroke="#cbd5e1"))

    # Page table mapping lines
    frags.append(arrow(245, 210, 320, 210, color="#2563eb", sw=2))
    frags.append(arrow(595, 210, 520, 210, color="#2563eb", sw=2))
    frags.append(line(245, 285, 320, 290, color="#d97706", sw=1.5, dash="4,4"))
    frags.append(line(595, 285, 520, 365, color="#ea580c", sw=1.5, dash="4,4"))

    render(path, w, h, *frags)

def build_linking_lifecycle_diagram(path):
    w, h = 840, 460
    frags = []

    frags.append(text(w / 2, 26, "Життєвий цикл запуску динамічного процесу Linux", size=16, bold=True))

    steps = [
        ("1. Виклик execve()", "Ядро аналізує ELF-заголовок бінарного файла.\nЗчитується сегмент PT_INTERP (/lib64/ld-linux-x86-64.so.2).", "#f1f5f9", "#94a3b8"),
        ("2. Завантаження ld.so", "Ядро відображає в пам'ять бінарник та динамічний завантажувач ld.so.\nУправління передається на entry point завантажувача.", "#e0f2fe", "#0284c7"),
        ("3. Парсинг залежностей", "ld.so вичитує секцію .dynamic і теги DT_NEEDED.\nЗнаходить і відкриває файли .so через LD_LIBRARY_PATH та ld.so.cache.", "#fef3c7", "#d97706"),
        ("4. Релокації та GOT/PLT", "ld.so виправляє адреси в GOT та PLT відповідно до реальних\nбазових адрес завантаження бібліотек у пам'ять (ASLR).", "#dcfce7", "#16a34a"),
        ("5. Ініціалізатори (.init)", "Виконуються функції з секцій .init та .init_array\n(глобальні конструктори C++ та ініціалізатори бібліотек).", "#fae8ff", "#c084fc"),
        ("6. Передача в main()", "ld.so передає управління на справжню точку входу програми (_start -> main).\nПрограма починає виконання власних інструкцій.", "#ecfdf5", "#059669")
    ]

    y_start = 65
    step_h = 55
    spacing = 10

    for i, (title_text, desc_text, fill_c, stroke_c) in enumerate(steps):
        curr_y = y_start + i * (step_h + spacing)
        # Step number badge
        frags.append(circle(65, curr_y + step_h / 2, 18, fill=stroke_c, stroke=stroke_c))
        frags.append(text(65, curr_y + step_h / 2 + 5, str(i + 1), size=14, color="#ffffff", bold=True))

        # Main step box
        frags.append(rect(100, curr_y, 700, step_h, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        frags.append(text(120, curr_y + 22, title_text, size=13, bold=True, anchor="start", color="#0f172a"))
        frags.append(mtext(320, curr_y + 20, desc_text, size=11, anchor="start", color="#334155"))

        # Connecting arrow to next step
        if i < len(steps) - 1:
            arrow_y1 = curr_y + step_h
            arrow_y2 = curr_y + step_h + spacing
            frags.append(arrow(65, arrow_y1, 65, arrow_y2, color="#64748b", sw=1.5))

    render(path, w, h, *frags)

def render_all():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(out_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    build_static_linking_diagram(os.path.join(img_dir, "static-linking.svg"))
    build_dynamic_linking_diagram(os.path.join(img_dir, "dynamic-linking.svg"))
    build_linking_lifecycle_diagram(os.path.join(img_dir, "linking-lifecycle.svg"))
    print("Generated figures in img/")

if __name__ == '__main__':
    render_all()
