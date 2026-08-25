import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def build_sed_execution_cycle(path):
    frags = []

    # Outer Container / Main Loop Box
    frags.append(rect(20, 20, 760, 430, fill="#f8fafc", stroke="#64748b", sw=2, rx=8))
    frags.append(text(400, 50, "Головний цикл потокового редактора (sed Execution Engine)", size=15, color="#1e293b", bold=True))

    # Step 1: Input Stream
    b_in, _, _ = textbox(110, 120, "Вхідний потік\n(stdin / file)\nЛінія з \\n", size=12, fill="#ffffff", stroke="#0284c7", bold=True)
    frags.append(b_in)

    # Step 2: Strip \n
    b_strip, _, _ = textbox(270, 120, "Відсікання \\n\n(стрипінг роздільника)", size=12, fill="#e0f2fe", stroke="#0284c7")
    frags.append(b_strip)

    # Step 3: Pattern Space
    frags.append(rect(400, 85, 200, 70, fill="#fef3c7", stroke="#d97706", sw=2, rx=6))
    frags.append(text(500, 115, "Pattern Space", size=14, color="#b45309", bold=True))
    frags.append(text(500, 140, "Робочий рядок у RAM", size=11, color="#78350f"))

    # Arrows for input
    frags.append(arrow(180, 120, 200, 120, color="#0284c7", sw=1.8))
    frags.append(arrow(340, 120, 395, 120, color="#0284c7", sw=1.8))

    # Step 4: Hold Space (Auxiliary buffer)
    frags.append(rect(400, 205, 200, 70, fill="#ede9fe", stroke="#7c3aed", sw=2, rx=6))
    frags.append(text(500, 235, "Hold Space", size=14, color="#5b21b6", bold=True))
    frags.append(text(500, 260, "Допоміжний регістр", size=11, color="#4c1d95"))

    # Dual arrow between Pattern Space and Hold Space
    frags.append(arrow(470, 160, 470, 200, color="#7c3aed", sw=1.8))
    frags.append(arrow(530, 200, 530, 160, color="#7c3aed", sw=1.8))
    frags.append(text(445, 183, "h / H", size=10, color="#5b21b6", bold=True))
    frags.append(text(555, 183, "g / G / x", size=10, color="#5b21b6", bold=True))

    # Step 5: Command Evaluation Pipeline
    frags.append(rect(60, 310, 480, 110, fill="#ffffff", stroke="#059669", sw=1.8, rx=6))
    frags.append(text(300, 335, "Ланцюжок команд сценарію (sed Script Evaluation)", size=13, color="#065f46", bold=True))
    frags.append(text(300, 360, "Перевірка адреси (/regex/, 1,5, $) → Виконання дій", size=11, color=INK))
    frags.append(text(300, 390, "s/// (заміна) · d/D (видалення) · N/P · b/t (переходи)", size=11, color="#047857", bold=True))

    # Arrow from Pattern space to Command Pipeline
    frags.append(arrow(605, 120, 670, 120, color="#d97706", sw=1.8))
    frags.append(line(670, 120, 670, 365, color="#d97706", sw=1.8))
    frags.append(arrow(670, 365, 545, 365, color="#d97706", sw=1.8))

    # Step 6: Output Gate & Auto-print
    b_out_gate, _, _ = textbox(110, 240, "Авто-друк (stdout)\n+ відновлення \\n\n(якщо немає -n)", size=12, fill="#dcfce7", stroke="#16a34a", bold=True)
    frags.append(b_out_gate)

    # Arrow from Command Pipeline to Output Gate
    frags.append(arrow(60, 365, 35, 365, color="#16a34a", sw=1.8))
    frags.append(line(35, 365, 35, 240, color="#16a34a", sw=1.8))
    frags.append(arrow(35, 240, 50, 240, color="#16a34a", sw=1.8))

    # Arrow from Output Gate back to next line reader
    frags.append(arrow(110, 200, 110, 165, color="#64748b", sw=1.8))
    frags.append(text(155, 185, "Наступний рядок", size=10, color=MUTED, italic=True))

    render(path, 800, 470, *frags)

def build_sed_hold_pattern_exchange(path):
    frags = []

    # Background frame
    frags.append(rect(20, 20, 760, 370, fill="#f8fafc", stroke="#64748b", sw=2, rx=8))
    frags.append(text(400, 50, "Операції передачі даних між Pattern Space та Hold Space", size=15, color="#1e293b", bold=True))

    # Pattern Space Box
    frags.append(rect(50, 100, 260, 130, fill="#fef3c7", stroke="#d97706", sw=2, rx=6))
    frags.append(text(180, 130, "Pattern Space (PS)", size=14, color="#b45309", bold=True))
    frags.append(text(180, 155, "Поточний робочий рядок", size=11, color="#78350f"))
    frags.append(rect(70, 175, 220, 35, fill="#ffffff", stroke="#f59e0b", rx=4))
    frags.append(text(180, 198, "рядок_А (активний)", size=12, color=INK))

    # Hold Space Box
    frags.append(rect(490, 100, 260, 130, fill="#ede9fe", stroke="#7c3aed", sw=2, rx=6))
    frags.append(text(620, 130, "Hold Space (HS)", size=14, color="#5b21b6", bold=True))
    frags.append(text(620, 155, "Допоміжна пам'ять", size=11, color="#4c1d95"))
    frags.append(rect(510, 175, 220, 35, fill="#ffffff", stroke="#8b5cf6", rx=4))
    frags.append(text(620, 198, "рядок_Б (збережений)", size=12, color=INK))

    # Commands mapping table / arrows
    # h: PS -> HS (overwrite)
    frags.append(arrow(315, 120, 485, 120, color="#d97706", sw=1.8))
    frags.append(text(400, 112, "h  (копіювати: HS = PS)", size=11, color="#b45309", bold=True))

    # H: PS -> HS (append with \n)
    frags.append(arrow(315, 145, 485, 145, color="#b45309", sw=1.8))
    frags.append(text(400, 138, "H  (додати: HS = HS + '\\n' + PS)", size=11, color="#b45309", bold=True))

    # g: HS -> PS (overwrite)
    frags.append(arrow(485, 175, 315, 175, color="#7c3aed", sw=1.8))
    frags.append(text(400, 168, "g  (відновити: PS = HS)", size=11, color="#5b21b6", bold=True))

    # G: HS -> PS (append with \n)
    frags.append(arrow(485, 200, 315, 200, color="#5b21b6", sw=1.8))
    frags.append(text(400, 193, "G  (додати: PS = PS + '\\n' + HS)", size=11, color="#5b21b6", bold=True))

    # x: exchange PS <-> HS
    frags.append(line(315, 225, 485, 225, color="#059669", sw=2))
    frags.append(arrow(330, 225, 315, 225, color="#059669", sw=2))
    frags.append(arrow(470, 225, 485, 225, color="#059669", sw=2))
    frags.append(text(400, 218, "x  (атомарний обмін: PS ↔ HS)", size=11, color="#047857", bold=True))

    # Summary box at bottom
    frags.append(rect(50, 260, 700, 100, fill="#ffffff", stroke="#94a3b8", rx=6))
    frags.append(text(400, 285, "Типовий патерн багаторядкової агрегації або реверсу тексту:", size=12, color=INK, bold=True))
    frags.append(text(400, 310, "1) 1!G  — додати накопичений стек з Hold Space до поточного рядка", size=11, color="#334155"))
    frags.append(text(400, 330, "2) h    — зберегти отриманий перевернутий стек назад у Hold Space", size=11, color="#334155"))
    frags.append(text(400, 350, "3) $p   — на останньому рядку вивести повний перевернутий файл", size=11, color="#334155"))

    render(path, 800, 410, *frags)

def build_sed_inplace_inodes(path):
    frags = []

    # Container
    frags.append(rect(20, 20, 760, 420, fill="#f8fafc", stroke="#64748b", sw=2, rx=8))
    frags.append(text(400, 50, "Механіка редагування на місці: чому sed -i змінює inode файлу", size=15, color="#1e293b", bold=True))

    # Left: State BEFORE
    frags.append(rect(40, 80, 320, 330, fill="#ffffff", stroke="#0284c7", sw=1.8, rx=6))
    frags.append(text(200, 110, "1. До виконання sed -i", size=13, color="#0369a1", bold=True))

    # Directory entry
    frags.append(rect(60, 130, 280, 45, fill="#f0f9ff", stroke="#bae6fd", rx=4))
    frags.append(text(200, 158, "Ім'я: config.conf → Inode #10523", size=12, color="#0c4a6e", bold=True))

    # Inode & Disk data
    frags.append(rect(60, 190, 280, 95, fill="#e0f2fe", stroke="#7dd3fc", rx=4))
    frags.append(text(200, 215, "Inode #10523 (Оригінал)", size=12, color="#0369a1", bold=True))
    frags.append(text(200, 240, "Власник: root:root | Права: 0644", size=11, color=INK))
    frags.append(text(200, 265, "Посилання (nlink): 2 (є Hard Link)", size=11, color="#b91c1c", bold=True))

    frags.append(rect(60, 300, 280, 85, fill="#fef2f2", stroke="#fca5a5", rx=4))
    frags.append(text(200, 325, "Hardlink: backup.conf", size=12, color="#991b1b", bold=True))
    frags.append(text(200, 350, "Вказує на той самий Inode #10523", size=11, color="#7f1d1d"))
    frags.append(text(200, 370, "Symlink: app.lnk → config.conf", size=11, color="#7f1d1d"))

    # Right: State AFTER sed -i
    frags.append(rect(440, 80, 320, 330, fill="#ffffff", stroke="#059669", sw=1.8, rx=6))
    frags.append(text(600, 110, "2. Після виконання sed -i", size=13, color="#065f46", bold=True))

    # Temp file creation and rename
    frags.append(rect(460, 130, 280, 45, fill="#f0fdf4", stroke="#bbf7d0", rx=4))
    frags.append(text(600, 158, "Ім'я: config.conf → Inode #88941", size=12, color="#14532d", bold=True))

    # New Inode
    frags.append(rect(460, 190, 280, 95, fill="#dcfce7", stroke="#86efac", rx=4))
    frags.append(text(600, 215, "Inode #88941 (Новий файл sedXXXX)", size=12, color="#15803d", bold=True))
    frags.append(text(600, 240, "rename('sedXXXX', 'config.conf')", size=11, color="#166534", bold=True))
    frags.append(text(600, 265, "Посилання (nlink): 1 (новий Inode)", size=11, color=INK))

    # Consequences
    frags.append(rect(460, 300, 280, 85, fill="#fff1f2", stroke="#fecdd3", rx=4))
    frags.append(text(600, 325, "Наслідки для зв'язків:", size=12, color="#be123c", bold=True))
    frags.append(text(600, 350, "1) Hardlink лишився на старому #10523", size=11, color="#9f1239"))
    frags.append(text(600, 370, "2) Зв'язок розірвано (стали різними)", size=11, color="#9f1239", bold=True))

    # Transformation Arrow in the middle
    frags.append(arrow(370, 240, 430, 240, color="#d97706", sw=2.5))
    frags.append(text(400, 220, "sed -i", size=12, color="#b45309", bold=True))

    render(path, 800, 460, *frags)

def render_all():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)

    build_sed_execution_cycle(os.path.join(img_dir, 'sed-execution-cycle.svg'))
    build_sed_hold_pattern_exchange(os.path.join(img_dir, 'sed-hold-pattern-exchange.svg'))
    build_sed_inplace_inodes(os.path.join(img_dir, 'sed-inplace-inodes.svg'))

if __name__ == '__main__':
    render_all()
