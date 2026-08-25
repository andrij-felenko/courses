import sys
import os

# Four parent levels to reach scripts/ in repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

from svgkit import render, rect, text, mtext, arrow, line, fitbox, textbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(IMG_DIR, exist_ok=True)

def fig_conditional_eval():
    w, h = 840, 310
    frags = []

    # Title label
    frags.append(text(420, 25, "Механізм умовного розгалуження в оболонці (POSIX vs Bash)", size=15, bold=True))

    # Top pipeline: POSIX Command Exit Status evaluation
    frags.append(fitbox(20, 50, 180, 75, "1. Команда умов\nif cmd / test / [\nРозбиття слів та розкриття", fill="#f4f6f8", stroke=LINE, size=11, bold=True))
    frags.append(arrow(200, 87, 260, 87, color=LINE, sw=1.8))
    frags.append(text(230, 77, "argv[]", size=10, color=MUTED))

    frags.append(fitbox(260, 50, 180, 75, "2. Виконання процесу\nВбудована або /bin/cmd\nПовертає код 0..255", fill="#eaf0fd", stroke=NEG, size=11, bold=True))
    frags.append(arrow(440, 87, 500, 87, color=LINE, sw=1.8))
    frags.append(text(470, 77, "wstatus / $?", size=10, color=MUTED))

    frags.append(fitbox(500, 45, 150, 85, "3. Оцінка статусу\n$? == 0 → Успіх\n$? != 0 → Помилка", fill="#fdecea", stroke=POS, size=11, bold=True))

    frags.append(arrow(650, 68, 710, 68, color=FIELD, sw=1.8))
    frags.append(fitbox(710, 45, 110, 42, "then гілка", fill="#eafaf1", stroke=FIELD, size=11, bold=True))

    frags.append(arrow(650, 108, 710, 108, color=POS, sw=1.8))
    frags.append(fitbox(710, 92, 110, 42, "else / fi", fill="#fdecea", stroke=POS, size=11, bold=True))

    # Separator
    frags.append(line(20, 155, 820, 155, color=MUTED, dash="4,4"))

    # Bottom pipeline: Bash Keyword Parsing evaluation [[ ... ]]
    frags.append(fitbox(20, 175, 180, 85, "1. Ключове слово [[\nСпеціальний синтаксис\nБез word splitting/glob", fill="#f4f6f8", stroke=LINE, size=11, bold=True))
    frags.append(arrow(200, 217, 260, 217, color=LINE, sw=1.8))
    frags.append(text(230, 207, "AST токени", size=10, color=MUTED))

    frags.append(fitbox(260, 175, 180, 85, "2. Внутрішній рушій\nПарсинг =~ (regex),\n== (glob), &&, ||", fill="#eafaf1", stroke=FIELD, size=11, bold=True))
    frags.append(arrow(440, 217, 500, 217, color=LINE, sw=1.8))
    frags.append(text(470, 207, "логічний підсумок", size=10, color=MUTED))

    frags.append(fitbox(500, 175, 150, 85, "3. Результат у пам'яті\nПряме повернення 0/1\n(без форку та exec)", fill="#eafaf1", stroke=FIELD, size=11, bold=True))

    frags.append(arrow(650, 198, 710, 198, color=FIELD, sw=1.8))
    frags.append(fitbox(710, 175, 110, 42, "then гілка", fill="#eafaf1", stroke=FIELD, size=11, bold=True))

    frags.append(arrow(650, 238, 710, 238, color=POS, sw=1.8))
    frags.append(fitbox(710, 222, 110, 42, "else / fi", fill="#fdecea", stroke=POS, size=11, bold=True))

    # Notes
    frags.append(text(420, 290, "Головний принцип: в оболонці 0 — це True (успіх), а ненульове число — False (помилка)", size=11, color=INK, italic=True))

    render(os.path.join(IMG_DIR, 'shell-conditional-eval.svg'), w, h, *frags, title="Оцінка умовних конструкцій в оболонці")

def fig_while_read_pipeline():
    w, h = 840, 280
    frags = []

    # Title label
    frags.append(text(420, 25, "Анатомія безпечного читання потоку: while IFS= read -r line || [ -n \"$line\" ]", size=14, bold=True))

    # Stage 1: Input stream
    frags.append(fitbox(20, 60, 150, 95, "Вхідний потік\nФайл / Pipe\nПобайтове читання\nдо \\n або EOF", fill="#f4f6f8", stroke=LINE, size=11, bold=True))
    frags.append(arrow(170, 107, 220, 107, color=LINE, sw=1.8))

    # Stage 2: read -r
    frags.append(fitbox(220, 60, 160, 95, "Прапорець -r\n(Raw Mode)\nЗворотні слеші \\\nне екранують \\n і char", fill="#eaf0fd", stroke=NEG, size=11, bold=True))
    frags.append(arrow(380, 107, 430, 107, color=LINE, sw=1.8))

    # Stage 3: IFS=
    frags.append(fitbox(430, 60, 170, 95, "Префікс IFS=\n(Internal Field Sep)\nВимкнено відтинання\nпробілів і табуляцій", fill="#eafaf1", stroke=FIELD, size=11, bold=True))
    frags.append(arrow(600, 107, 650, 107, color=LINE, sw=1.8))

    # Stage 4: Variable assignment
    frags.append(fitbox(650, 60, 170, 95, "Змінна $line\nОтримує точний\nоригінальний вміст\nрядка без викривлень", fill="#fdecea", stroke=POS, size=11, bold=True))

    # Stage 5: EOF handling fallback
    frags.append(line(20, 175, 820, 175, color=MUTED, dash="4,4"))

    frags.append(fitbox(120, 190, 270, 65, "Останній рядок БЕЗ \\n на кінці:\nread повертає $? = 1 (EOF),\nале в $line залишається текст!", fill="#fdecea", stroke=POS, size=11, bold=True))

    frags.append(arrow(390, 222, 450, 222, color=POS, sw=1.8))
    frags.append(text(420, 212, "||", size=13, bold=True, color=POS))

    frags.append(fitbox(450, 190, 270, 65, "Страхувальник [ -n \"$line\" ]:\nРятує останній рядок!\nЦикл обробляє залишок рядка\nі лише потім зупиняється", fill="#eafaf1", stroke=FIELD, size=11, bold=True))

    render(os.path.join(IMG_DIR, 'while-read-pipeline.svg'), w, h, *frags, title="Анатомія потокового читання рядків")

if __name__ == '__main__':
    fig_conditional_eval()
    fig_while_read_pipeline()
