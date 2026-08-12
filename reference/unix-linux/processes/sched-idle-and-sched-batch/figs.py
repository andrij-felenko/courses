import sys
import os

# Four steps up to repo root scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import render, rect, text, line, arrow, fitbox, textbox, FILL, BG, MUTED, POS, NEG, FIELD, INK

def generate_sched_comparison():
    w, h = 820, 320
    frags = []
    
    y_other = 70
    y_batch = 150
    y_idle = 230
    
    # Class labels
    frags.append(textbox(90, y_other + 15, "SCHED_OTHER\n(nice=0)", size=12, fill="#e8f5e9", stroke="#2e7d32", bold=True)[0])
    frags.append(textbox(90, y_batch + 15, "SCHED_BATCH\n(nice=0)", size=12, fill="#fff3e0", stroke="#ef6c00", bold=True)[0])
    frags.append(textbox(90, y_idle + 15, "SCHED_IDLE\n(weight=3)", size=12, fill="#eceff1", stroke="#455a64", bold=True)[0])
    
    # Timeline axes
    for y in [y_other + 15, y_batch + 15, y_idle + 15]:
        frags.append(line(170, y, 780, y, color="#b0bec5", sw=1.5))
        frags.append(arrow(770, y, 785, y, color="#78909c", sw=1.5))
    
    frags.append(text(760, y_other - 8, "Час (t)", size=11, color=MUTED, italic=True))
    
    # SCHED_OTHER: frequent context switches (interactive responsiveness)
    x = 175
    for i in range(5):
        frags.append(fitbox(x, y_other, 45, 30, "A", size=12, fill="#c8e6c9", stroke="#388e3c", bold=True))
        frags.append(fitbox(x + 50, y_other, 45, 30, "B", size=12, fill="#bbdefb", stroke="#1976d2", bold=True))
        x += 105
    frags.append(text(600, y_other - 8, "Часті перемикання (низька затримка)", size=11, color="#2e7d32", italic=True))
    
    # SCHED_BATCH: long continuous slices, no wakeup preemption (high throughput)
    x = 175
    frags.append(fitbox(x, y_batch, 240, 30, "Пакетна задача A (тривалий квант)", size=12, fill="#ffe0b2", stroke="#f57c00", bold=True))
    frags.append(fitbox(x + 250, y_batch, 240, 30, "Пакетна задача B (без витискання)", size=12, fill="#e1bee7", stroke="#8e24aa", bold=True))
    frags.append(text(600, y_batch - 8, "Збереження кешу CPU (високий throughput)", size=11, color="#ef6c00", italic=True))
    
    # SCHED_IDLE: runs only when system idle
    frags.append(fitbox(175, y_idle, 320, 30, "Процесор зайнятий (OTHER / BATCH)", size=12, fill="#cfd8dc", stroke="#90a4ae", color="#455a64"))
    frags.append(fitbox(505, y_idle, 220, 30, "IDLE задача (фонові обчислення)", size=12, fill="#b2ebf2", stroke="#00acc1", bold=True))
    frags.append(text(600, y_idle - 8, "Виконання лише при простої CPU", size=11, color="#00838f", italic=True))
    
    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig-sched-comparison.svg")
    
    render(out_path, w, h, *frags, title="Порівняння поведінки класів планування CFS")
    print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_sched_comparison()
