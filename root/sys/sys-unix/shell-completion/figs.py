import os
import sys

# Add scripts/ to sys.path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render as svg_render, rect, text, mtext, line, arrow, FILL, INK, LINE, MUTED, POS, NEG, FIELD

def render_readline_flow(img_dir):
    w, h = 820, 500
    frags = []

    frags.append(text(w / 2, 25, "Конвеєр обробки клавіші Tab у бібліотеці GNU Readline", size=15, bold=True))

    # Step 1: Keystroke & Dispatch
    frags.append(rect(30, 60, 220, 110, fill="#f8fafc", stroke="#64748b", sw=1.5))
    frags.append(text(140, 85, "1. Ввід термінала", size=13, color="#1e293b", bold=True))
    frags.append(mtext(140, 108, [
        "Користувач натискає <Tab>",
        "ASCII 0x09 ('\\t')",
        "Функція rl_complete()",
        "Перехоплення події вводу"
    ], size=11, color="#334155", lh=1.4))

    # Arrow 1->2
    frags.append(arrow(250, 115, 290, 115, color=LINE, sw=1.8))

    # Step 2: Hook Check & Word Tokenization
    frags.append(rect(290, 60, 240, 110, fill="#fef3c7", stroke="#d97706", sw=1.5))
    frags.append(text(410, 85, "2. Перевірка хука оболонки", size=13, color="#92400e", bold=True))
    frags.append(mtext(410, 108, [
        "rl_attempted_completion_function",
        "Токенізація за word break chars",
        "Визначення start та end слова"
    ], size=11, color="#78350f", lh=1.4))

    # Branch: Hook Present vs Default Fallback
    frags.append(arrow(410, 170, 410, 230, color=POS, sw=1.8))
    frags.append(text(465, 200, "Хук встановлено", size=11, color=POS, bold=True))

    frags.append(arrow(530, 115, 590, 115, color=MUTED, sw=1.8))
    frags.append(text(560, 100, "NULL", size=11, color=MUTED, bold=True))

    # Step 2b: Default Fallback
    frags.append(rect(590, 60, 200, 110, fill="#f1f5f9", stroke="#94a3b8", sw=1.5))
    frags.append(text(690, 85, "Стандартний генератор", size=13, color="#475569", bold=True))
    frags.append(mtext(690, 108, [
        "rl_filename_completion_function",
        "Сканування через opendir/readdir",
        "Доповнення імен файлів"
    ], size=11, color="#475569", lh=1.4))

    # Step 3: Bash Hook Execution
    frags.append(rect(200, 230, 420, 110, fill="#e0f2fe", stroke="#0284c7", sw=1.5))
    frags.append(text(410, 255, "3. Програмоване доповнення (Bash / Zsh)", size=13, color="#0369a1", bold=True))
    frags.append(mtext(410, 278, [
        "Виклик генератора (complete -F / _arguments)",
        "Ініціалізація COMP_WORDS, COMP_CWORD, COMP_LINE",
        "Генерація варіантів та заповнення масиву COMPREPLY"
    ], size=11, color="#0c4a6e", lh=1.4))

    # Arrow 3->4
    frags.append(arrow(410, 340, 410, 380, color=LINE, sw=1.8))

    # Step 4: Decision & Readline Output
    frags.append(rect(50, 380, 720, 95, fill="#dcfce7", stroke="#16a34a", sw=1.5))
    frags.append(text(410, 405, "4. Формування результату в буфері редагування", size=13, color="#15803d", bold=True))
    frags.append(mtext(410, 427, [
        "0 збігів: звуковий/візуальний сигнал (bell) | 1 збір: автопідстановка суфікса в рядок",
        "Декілька збігів: підстановка найдовшого спільного префікса (LCP); при повторному Tab — пейджер варіантів"
    ], size=11, color="#14532d", lh=1.4))

    # Arrow from Default Fallback to Step 4
    frags.append(line(690, 170, 690, 360, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(arrow(690, 360, 690, 380, color=MUTED, sw=1.5))

    path = os.path.join(img_dir, "readline-completion-flow.svg")
    svg_render(path, w, h, *frags)

def render_bash_architecture(img_dir):
    w, h = 820, 520
    frags = []

    frags.append(text(w / 2, 25, "Архітектура системи програмованого доповнення Bash", size=15, bold=True))

    # Left Column: User Input & Registration
    frags.append(rect(30, 60, 240, 200, fill="#fdf4ff", stroke="#c084fc", sw=1.5))
    frags.append(text(150, 85, "Реєстрація та стан", size=13, color="#7e22ce", bold=True))
    frags.append(mtext(150, 112, [
        "Таблиця complete (BASH hash table):",
        "  cmd ──► func / flags / list",
        "• complete -F _git git",
        "• complete -f -X '*.o' gcc",
        "• complete -W 'start stop' srv",
        "",
        "Динамічний завантажувач:",
        "/usr/share/bash-completion/..."
    ], size=11, color="#581c87", lh=1.4, anchor="middle"))

    # Middle Column: Execution Context
    frags.append(rect(300, 60, 240, 200, fill="#fef9c3", stroke="#ca8a04", sw=1.5))
    frags.append(text(420, 85, "Контекстні змінні", size=13, color="#854d0e", bold=True))
    frags.append(mtext(420, 112, [
        "COMP_LINE = 'git check '",
        "COMP_POINT = 10",
        "COMP_WORDS = ('git' 'check')",
        "COMP_CWORD = 1",
        "COMP_KEY = 9",
        "COMP_TYPE = 9",
        "COMP_WORDBREAKS = ' \\t\\n\"'><=;|&(:'"
    ], size=11, color="#713f12", lh=1.4, anchor="middle"))

    # Right Column: compgen engine
    frags.append(rect(570, 60, 220, 200, fill="#ecfdf5", stroke="#10b981", sw=1.5))
    frags.append(text(680, 85, "Вбудований compgen", size=13, color="#047857", bold=True))
    frags.append(mtext(680, 112, [
        "Фільтрація слів за префіксом:",
        "compgen -W 'checkout commit' -- 'c'",
        "  └──► 'checkout', 'commit'",
        "",
        "compgen -f -- 'sr'",
        "compgen -v -- 'PA'",
        "compgen -u -- 'ro'"
    ], size=11, color="#064e3b", lh=1.4, anchor="middle"))

    # Arrows between top boxes
    frags.append(arrow(270, 160, 300, 160, color=LINE, sw=1.8))
    frags.append(arrow(420, 260, 420, 300, color=LINE, sw=1.8))
    frags.append(arrow(680, 260, 540, 330, color=LINE, sw=1.8))

    # Bottom Area: Completion Script Logic & COMPREPLY
    frags.append(rect(30, 300, 760, 190, fill="#f0f9ff", stroke="#0284c7", sw=1.5))
    frags.append(text(410, 325, "Виконання сценарію доповнення та повернення результату", size=13, color="#0369a1", bold=True))
    frags.append(mtext(410, 352, [
        "_git() {",
        "    local cur prev words cword",
        "    _get_comp_words_by_ref -n \":=\" cur prev words cword",
        "    case \"${words[1]}\" in",
        "        checkout) COMPREPLY=( $(compgen -W \"$(git branch --list)\" -- \"$cur\") ) ;;",
        "        *)        COMPREPLY=( $(compgen -W \"clone fetch checkout status\" -- \"$cur\") ) ;;",
        "    esac",
        "}"
    ], size=11, color="#075985", lh=1.35, anchor="middle"))
    frags.append(text(410, 472, "Повернення результату через глобальний масив COMPREPLY у Readline", size=11, color="#0c4a6e", bold=True))

    path = os.path.join(img_dir, "bash-completion-architecture.svg")
    svg_render(path, w, h, *frags)

def render_bash_vs_zsh(img_dir):
    w, h = 820, 480
    frags = []

    frags.append(text(w / 2, 25, "Порівняння архітектури доповнення: Текстовий Bash проти Типізованого Zsh", size=15, bold=True))

    # Left Box: Bash model
    frags.append(rect(30, 60, 365, 390, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    frags.append(text(212, 85, "Bash: Лінійно-рядкова модель", size=14, color="#c2410c", bold=True))
    frags.append(line(45, 98, 380, 98, color="#ea580c", sw=1))

    bash_points = [
        "• Модель даних: одновимірний масив рядків COMPREPLY.",
        "• Розбиття на слова: фіксований COMP_WORDBREAKS.",
        "  Проблема: символи ':', '=' ламають індексацію",
        "  і вимагають обхідних викликів __ltrim_colon_completions.",
        "• Відсутність метаданих: Readline бачить лише рядки,",
        "  немає опису аргументів чи типу опції.",
        "• Візуалізація: моноширинний плоский список варіантів,",
        "  відсутність інтерактивного вибору стрілками.",
        "• Продуктивність: запуск подоболонок $(...) та зовнішніх",
        "  утиліт у bash-функціях на кожне натискання Tab."
    ]
    frags.append(mtext(45, 125, bash_points, size=11, color="#7c2d12", anchor="start", lh=1.65))

    # Right Box: Zsh model
    frags.append(rect(425, 60, 365, 390, fill="#f0fdf4", stroke="#16a34a", sw=1.5))
    frags.append(text(607, 85, "Zsh: Контекстно-типізована модель (compsys)", size=14, color="#15803d", bold=True))
    frags.append(line(440, 98, 775, 98, color="#16a34a", sw=1))

    zsh_points = [
        "• Модель даних: типізовані теги, опис (descriptions), групи.",
        "• Парсер _arguments: декларативний опис синтаксису:",
        "  '(-v --verbose)'{-v,--verbose}'[Детальний вивід]'",
        "  '1:команда:(start stop restart)' '2:сервіс:_services'",
        "• Автоматична обробка роздільників та лапок без збоїв.",
        "• Інтерактивне меню (menu-select) з навігацією стрілками,",
        "  кольоровим групуванням та підказками призначень.",
        "• Функції-хелпери: _describe, _values, _multi_parts,",
        "  кешування важких обчислень через _cache_invalid."
    ]
    frags.append(mtext(440, 125, zsh_points, size=11, color="#14532d", anchor="start", lh=1.65))

    path = os.path.join(img_dir, "bash-vs-zsh-pipeline.svg")
    svg_render(path, w, h, *frags)

def render():
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    render_readline_flow(img_dir)
    render_bash_architecture(img_dir)
    render_bash_vs_zsh(img_dir)

if __name__ == '__main__':
    render()
