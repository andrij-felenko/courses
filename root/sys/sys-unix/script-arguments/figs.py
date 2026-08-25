import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_positional_stack(img_dir):
    w, h = 760, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Масив позиційних параметрів та зсув через shift", size=16, bold=True))
    
    # execve initial argv mapping
    frags.append(rect(30, 55, 700, 110, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(380, 78, "Стек процесу ядра Linux (execve / argv)", size=13, color="#334155", bold=True))
    
    argv_boxes = [
        (45, "argv[0]", "\"/usr/bin/deploy\"", "#e2e8f0", "#475569"),
        (185, "argv[1]", "\"--prod\"", "#dbeafe", "#1e40af"),
        (325, "argv[2]", "\"web cluster\"", "#fef3c7", "#92400e"),
        (465, "argv[3]", "\"backup.tar.gz\"", "#dcfce7", "#166534"),
        (605, "argv[4]", "\"--force\"", "#fae8ff", "#86198f"),
    ]
    for x, label, val, bg, stroke in argv_boxes:
        frags.append(rect(x, 90, 125, 60, fill=bg, stroke=stroke, sw=1.2))
        frags.append(text(x + 62, 108, label, size=11, color=stroke, bold=True))
        frags.append(text(x + 62, 132, val, size=10, color=INK))
        
    # Shell positional variables: Before shift
    frags.append(rect(30, 185, 700, 110, fill="#ffffff", stroke="#0284c7", sw=1.5))
    frags.append(text(150, 208, "Початковий стан: $# = 4", size=13, color="#0369a1", bold=True))
    frags.append(text(490, 208, "$0 = /usr/bin/deploy (не зсувається)", size=11, color="#64748b", italic=True))
    
    pos_boxes_1 = [
        (45, "$0", "\"/usr/bin/deploy\"", "#e2e8f0", "#475569"),
        (185, "$1", "\"--prod\"", "#dbeafe", "#1e40af"),
        (325, "$2", "\"web cluster\"", "#fef3c7", "#92400e"),
        (465, "$3", "\"backup.tar.gz\"", "#dcfce7", "#166534"),
        (605, "$4", "\"--force\"", "#fae8ff", "#86198f"),
    ]
    for x, label, val, bg, stroke in pos_boxes_1:
        frags.append(rect(x, 220, 125, 60, fill=bg, stroke=stroke, sw=1.2))
        frags.append(text(x + 62, 238, label, size=12, color=stroke, bold=True))
        frags.append(text(x + 62, 262, val, size=10, color=INK))
        
    # Arrow for shift 2
    frags.append(line(380, 302, 380, 328, color="#c0392b", sw=2))
    frags.append(arrow(380, 302, 380, 332, color="#c0392b", sw=2))
    frags.append(text(460, 318, "shift 2 (відкидає 2 аргументи ліворуч)", size=12, color="#c0392b", bold=True))
    
    # Shell positional variables: After shift 2
    frags.append(rect(30, 340, 700, 115, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    frags.append(text(150, 363, "Після shift 2: $# = 2", size=13, color="#c2410c", bold=True))
    frags.append(text(490, 363, "$1 і $2 перезаписано значеннями з $3 і $4", size=11, color="#7c2d12", italic=True))
    
    pos_boxes_2 = [
        (45, "$0", "\"/usr/bin/deploy\"", "#e2e8f0", "#475569"),
        (185, "$1 (був $3)", "\"backup.tar.gz\"", "#dcfce7", "#166534"),
        (325, "$2 (був $4)", "\"--force\"", "#fae8ff", "#86198f"),
        (465, "[знищено]", "(порожньо)", "#f1f5f9", "#94a3b8"),
        (605, "[знищено]", "(порожньо)", "#f1f5f9", "#94a3b8"),
    ]
    for x, label, val, bg, stroke in pos_boxes_2:
        frags.append(rect(x, 375, 125, 60, fill=bg, stroke=stroke, sw=1.2))
        frags.append(text(x + 62, 393, label, size=11, color=stroke, bold=True))
        frags.append(text(x + 62, 417, val, size=10, color=INK))
        
    path = os.path.join(img_dir, "positional-parameters-stack.svg")
    svg_render(path, w, h, *frags)

def render_expansion_comparison(img_dir):
    w, h = 760, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Порівняння розкриття $* та $@ у лапках та без лапок", size=16, bold=True))
    frags.append(text(w / 2, 50, "Вхідні аргументи:  $1=\"fast copy\"   $2=\"data file.txt\"   $3=\"-v\"", size=12, color="#475569", italic=True))
    
    # 1. Unquoted $*
    frags.append(rect(30, 68, 695, 88, fill="#fef2f2", stroke="#ef4444", sw=1.3))
    frags.append(text(45, 90, "1. Неекранований $*", size=13, color="#991b1b", anchor="start", bold=True))
    frags.append(text(45, 108, "Склеювання через IFS + Word Splitting + Globbing", size=10, color="#7f1d1d", anchor="start"))
    tokens_1 = ["\"fast\"", "\"copy\"", "\"data\"", "\"file.txt\"", "\"-v\""]
    for i, t in enumerate(tokens_1):
        x = 45 + i * 135
        frags.append(rect(x, 116, 120, 32, fill="#fee2e2", stroke="#b91c1c", sw=1))
        frags.append(text(x + 60, 137, t, size=11, color="#7f1d1d"))
    frags.append(text(650, 100, "5 слів!", size=12, color="#b91c1c", bold=True))
    frags.append(text(650, 122, "(пробіли розбито)", size=10, color="#991b1b"))
    
    # 2. Unquoted $@
    frags.append(rect(30, 166, 695, 88, fill="#fef2f2", stroke="#ef4444", sw=1.3))
    frags.append(text(45, 188, "2. Неекранований $@", size=13, color="#991b1b", anchor="start", bold=True))
    frags.append(text(45, 206, "Розкриття на слова, але все одно Word Splitting + Globbing", size=10, color="#7f1d1d", anchor="start"))
    for i, t in enumerate(tokens_1):
        x = 45 + i * 135
        frags.append(rect(x, 214, 120, 32, fill="#fee2e2", stroke="#b91c1c", sw=1))
        frags.append(text(x + 60, 235, t, size=11, color="#7f1d1d"))
    frags.append(text(650, 198, "5 слів!", size=12, color="#b91c1c", bold=True))
    frags.append(text(650, 220, "(без лапок не рятує)", size=10, color="#991b1b"))
    
    # 3. Quoted "$*"
    frags.append(rect(30, 264, 695, 88, fill="#fffbeb", stroke="#f59e0b", sw=1.3))
    frags.append(text(45, 286, "3. Екранований \"$*\"", size=13, color="#92400e", anchor="start", bold=True))
    frags.append(text(45, 304, "Один суцільний рядок через перший символ IFS (за замовчуванням пробіл)", size=10, color="#78350f", anchor="start"))
    frags.append(rect(45, 312, 570, 32, fill="#fef3c7", stroke="#d97706", sw=1))
    frags.append(text(330, 333, "\"fast copy data file.txt -v\"", size=11, color="#78350f"))
    frags.append(text(650, 296, "1 слово!", size=12, color="#b45309", bold=True))
    frags.append(text(650, 318, "(склеєно в одне)", size=10, color="#92400e"))
    
    # 4. Quoted "$@"
    frags.append(rect(30, 362, 695, 95, fill="#f0fdf4", stroke="#22c55e", sw=1.5))
    frags.append(text(45, 384, "4. Екранований \"$@\" — ЕТАЛОН POSIX", size=13, color="#166534", anchor="start", bold=True))
    frags.append(text(45, 402, "Зберігає оригінальні межі кожного аргументу, захищає від розбиття та підстановок", size=10, color="#14532d", anchor="start"))
    tokens_4 = ["\"fast copy\"", "\"data file.txt\"", "\"-v\""]
    for i, t in enumerate(tokens_4):
        x = 45 + i * 195
        frags.append(rect(x, 410, 180, 36, fill="#dcfce7", stroke="#16a34a", sw=1.2))
        frags.append(text(x + 90, 433, t, size=11, color="#14532d", bold=True))
    frags.append(text(650, 396, "3 аргументи", size=12, color="#15803d", bold=True))
    frags.append(text(650, 418, "✓ Точний масив", size=11, color="#166534"))
    
    path = os.path.join(img_dir, "expansion-comparison-ifs.svg")
    svg_render(path, w, h, *frags)

def render_getopts_flow(img_dir):
    w, h = 760, 480
    frags = []
    
    frags.append(text(w / 2, 28, "Внутрішній автомат розбору опцій getopts", size=16, bold=True))
    
    # Start node
    frags.append(rect(40, 60, 160, 50, fill="#f1f5f9", stroke="#475569", sw=1.3))
    frags.append(text(120, 82, "Виклик getopts", size=12, color="#334155", bold=True))
    frags.append(text(120, 98, "\":f:vho:\" opt", size=10, color="#64748b"))
    
    frags.append(line(200, 85, 245, 85, color=LINE, sw=1.5))
    frags.append(arrow(200, 85, 250, 85, color=LINE, sw=1.5))
    
    # Check next arg
    frags.append(rect(250, 60, 230, 50, fill="#e0f2fe", stroke="#0284c7", sw=1.3))
    frags.append(text(365, 80, "Аналіз argv[OPTIND]", size=12, color="#0369a1", bold=True))
    frags.append(text(365, 98, "Починається з '-' і != \"--\"?", size=10, color="#0c4a6e"))
    
    # Branch: Not an option or '--'
    frags.append(line(480, 85, 545, 85, color=LINE, sw=1.5))
    frags.append(arrow(480, 85, 550, 85, color=LINE, sw=1.5))
    frags.append(text(510, 75, "Ні / \"--\"", size=10, color=MUTED))
    
    frags.append(rect(550, 60, 175, 50, fill="#fee2e2", stroke="#dc2626", sw=1.3))
    frags.append(text(637, 82, "Завершення (rc != 0)", size=12, color="#991b1b", bold=True))
    frags.append(text(637, 98, "shift $((OPTIND - 1))", size=10, color="#7f1d1d"))
    
    # Branch: Is option
    frags.append(line(365, 110, 365, 145, color=LINE, sw=1.5))
    frags.append(arrow(365, 110, 365, 150, color=LINE, sw=1.5))
    frags.append(text(385, 132, "Так ('-')", size=10, color="#0369a1"))
    
    # Check known option
    frags.append(rect(250, 150, 230, 55, fill="#fef3c7", stroke="#d97706", sw=1.3))
    frags.append(text(365, 172, "Символ у рядку optstring?", size=12, color="#92400e", bold=True))
    frags.append(text(365, 190, "відомий прапорець", size=10, color="#78350f"))
    
    # Branch: Unknown option
    frags.append(line(250, 177, 185, 177, color=LINE, sw=1.5))
    frags.append(arrow(250, 177, 180, 177, color=LINE, sw=1.5))
    frags.append(text(215, 168, "Ні", size=10, color="#dc2626"))
    
    frags.append(rect(30, 150, 150, 60, fill="#fee2e2", stroke="#b91c1c", sw=1.3))
    frags.append(text(105, 172, "Невідома опція", size=12, color="#991b1b", bold=True))
    frags.append(text(105, 192, "opt='?', OPTARG=символ", size=10, color="#7f1d1d"))
    
    # Branch: Known option -> Needs argument?
    frags.append(line(365, 205, 365, 245, color=LINE, sw=1.5))
    frags.append(arrow(365, 205, 365, 250, color=LINE, sw=1.5))
    frags.append(text(385, 230, "Так", size=10, color="#15803d"))
    
    frags.append(rect(250, 250, 230, 55, fill="#f3e8ff", stroke="#9333ea", sw=1.3))
    frags.append(text(365, 272, "Опція має двокрапку ':'?", size=12, color="#6b21a8", bold=True))
    frags.append(text(365, 290, "вимагає значення аргументу", size=10, color="#581c87"))
    
    # Simple flag
    frags.append(line(480, 277, 545, 277, color=LINE, sw=1.5))
    frags.append(arrow(480, 277, 550, 277, color=LINE, sw=1.5))
    frags.append(text(510, 268, "Ні (прапор)", size=10, color="#0c4a6e"))
    
    frags.append(rect(550, 250, 175, 55, fill="#dbeafe", stroke="#2563eb", sw=1.3))
    frags.append(text(637, 272, "opt = символ", size=12, color="#1e40af", bold=True))
    frags.append(text(637, 290, "OPTIND інкрементується", size=10, color="#1e3a8a"))
    
    # Argument required -> Has argument?
    frags.append(line(365, 305, 365, 345, color=LINE, sw=1.5))
    frags.append(arrow(365, 305, 365, 350, color=LINE, sw=1.5))
    frags.append(text(385, 330, "Так (потрібен арг)", size=10, color="#6b21a8"))
    
    frags.append(rect(250, 350, 230, 55, fill="#f0fdf4", stroke="#16a34a", sw=1.3))
    frags.append(text(365, 372, "Аргумент присутній?", size=12, color="#166534", bold=True))
    frags.append(text(365, 390, "-f file.txt або -ffile.txt", size=10, color="#14532d"))
    
    # Missing argument
    frags.append(line(250, 377, 185, 377, color=LINE, sw=1.5))
    frags.append(arrow(250, 377, 180, 377, color=LINE, sw=1.5))
    frags.append(text(215, 368, "Відсутній", size=10, color="#dc2626"))
    
    frags.append(rect(30, 350, 150, 60, fill="#fee2e2", stroke="#b91c1c", sw=1.3))
    frags.append(text(105, 372, "Пропущено арг", size=12, color="#991b1b", bold=True))
    frags.append(text(105, 392, "opt=':' (тихий) / '?'", size=10, color="#7f1d1d"))
    
    # Argument valid
    frags.append(line(480, 377, 545, 377, color=LINE, sw=1.5))
    frags.append(arrow(480, 377, 550, 377, color=LINE, sw=1.5))
    frags.append(text(510, 368, "Присутній", size=10, color="#15803d"))
    
    frags.append(rect(550, 350, 175, 55, fill="#dcfce7", stroke="#16a34a", sw=1.3))
    frags.append(text(637, 372, "OPTARG = значення", size=12, color="#166534", bold=True))
    frags.append(text(637, 390, "OPTIND += 1 (або 2)", size=10, color="#14532d"))
    
    # Loop back to next iteration
    frags.append(line(637, 405, 637, 440, color="#64748b", sw=1.5))
    frags.append(line(637, 440, 120, 440, color="#64748b", sw=1.5))
    frags.append(line(120, 440, 120, 115, color="#64748b", sw=1.5))
    frags.append(arrow(120, 125, 120, 115, color="#64748b", sw=1.5))
    frags.append(text(380, 455, "Наступна ітерація циклу while getopts ...", size=11, color="#475569", italic=True))
    
    path = os.path.join(img_dir, "getopts-state-machine.svg")
    svg_render(path, w, h, *frags)

def render():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        
    render_positional_stack(img_dir)
    render_expansion_comparison(img_dir)
    render_getopts_flow(img_dir)

if __name__ == '__main__':
    render()
