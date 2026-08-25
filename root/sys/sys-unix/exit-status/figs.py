import sys
import os

# Four parent levels to reach scripts/ in repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))

from svgkit import render, rect, text, mtext, arrow, line, fitbox, textbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG

IMG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))
os.makedirs(IMG_DIR, exist_ok=True)

def fig_flow():
    w, h = 820, 260
    frags = []

    # Process block
    frags.append(fitbox(20, 70, 160, 100, "Дочірній процес\nexit(code) або\nсигнал (SIGSEGV)", fill="#eaf0fd", stroke=NEG, size=13, bold=True))

    # Arrow 1: to Kernel
    frags.append(arrow(180, 120, 240, 120, color=LINE, sw=1.8))
    frags.append(text(210, 110, "sys_exit", size=11, color=MUTED))

    # Kernel block
    frags.append(fitbox(240, 70, 170, 100, "Ядро Linux\ntask_struct.exit_code\n(упаковка status word)", fill="#fdecea", stroke=POS, size=13, bold=True))

    # Arrow 2: to waitpid
    frags.append(arrow(410, 120, 470, 120, color=LINE, sw=1.8))
    frags.append(text(440, 110, "waitpid()", size=11, color=MUTED))

    # Waitpid / Macro block
    frags.append(fitbox(470, 60, 170, 120, "Батьківський процес\nwstatus (16 біт)\n- WIFEXITED → WEXITSTATUS\n- WIFSIGNALED → WTERMSIG", fill="#eafaf1", stroke=FIELD, size=12, bold=True))

    # Arrow 3: to Shell $?
    frags.append(arrow(640, 120, 700, 120, color=LINE, sw=1.8))

    # Shell block
    frags.append(fitbox(700, 65, 105, 110, "Оболонка\nЗмінна $?\n0..125 або\n128 + N", fill="#f4f6f8", stroke=INK, size=13, bold=True))

    # Explanatory bottom notes
    frags.append(text(300, 220, "1. Нормальний exit(N) → $? = N", size=12, color=INK, anchor="start", bold=True))
    frags.append(text(300, 240, "2. Вбито сигналом S → $? = 128 + S (напр. SIGKILL: 128+9 = 137)", size=12, color=POS, anchor="start", bold=True))

    render(os.path.join(IMG_DIR, 'exit-status-flow.svg'), w, h, *frags, title="Шлях коду виходу: від exit() ядра до змінної $? оболонки")

def fig_wstatus():
    w, h = 820, 240
    frags = []

    # Title / Label for 16-bit word
    frags.append(text(410, 55, "Структура 16-бітного wstatus у waitpid() (Linux x86/ARM)", size=14, bold=True))

    # High byte (bits 8..15)
    frags.append(rect(60, 80, 340, 65, fill="#eafaf1", stroke=FIELD, sw=2))
    frags.append(text(230, 105, "Старший байт (біти 15..8)", size=13, bold=True, color=FIELD))
    frags.append(text(230, 130, "Код виходу exit status (0..255), якщо WIFEXITED", size=11, color=INK))

    # Bit 7: Core dump flag
    frags.append(rect(400, 80, 80, 65, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(440, 105, "Біт 7", size=13, bold=True, color=POS))
    frags.append(text(440, 130, "Core Dump", size=10, color=INK))

    # Low 7 bits (bits 0..6)
    frags.append(rect(480, 80, 280, 65, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(620, 105, "Молодші 7 бітів (біти 6..0)", size=13, bold=True, color=NEG))
    frags.append(text(620, 130, "Номер сигналу S, якщо WIFSIGNALED (0 = normal)", size=11, color=INK))

    # Annotations below
    frags.append(line(60, 160, 760, 160, color=MUTED, dash="4,4"))

    frags.append(text(70, 185, "• WIFEXITED(w): (w & 0x7f) == 0", size=12, anchor="start", color=INK))
    frags.append(text(70, 210, "• WEXITSTATUS(w): (w >> 8) & 0xff", size=12, anchor="start", color=FIELD))

    frags.append(text(440, 185, "• WIFSIGNALED(w): ((w & 0x7f) + 1) >> 1 > 0", size=12, anchor="start", color=INK))
    frags.append(text(440, 210, "• WTERMSIG(w): w & 0x7f", size=12, anchor="start", color=NEG))

    render(os.path.join(IMG_DIR, 'wstatus-bit-layout.svg'), w, h, *frags, title="Бітове кодування статусу завершення wstatus")

if __name__ == '__main__':
    fig_flow()
    fig_wstatus()
