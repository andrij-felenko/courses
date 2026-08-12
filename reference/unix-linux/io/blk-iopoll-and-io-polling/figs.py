import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
import svgkit

def render_figs():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    svg_path = os.path.join(img_dir, "fig-interrupt-vs-polling.svg")
    
    frags = []
    # Title
    frags.append(svgkit.text(400, 30, "Порівняння обробки I/O: Переривання проти IO Polling", size=15, bold=True))
    
    # Column 1: Interrupt-driven
    frags.append(svgkit.rect(30, 50, 350, 350, fill="#fdfcfb", stroke="#d9d9d9", rx=8))
    frags.append(svgkit.text(205, 75, "Апаратні переривання (IRQ-driven)", size=13, color=svgkit.POS, bold=True))
    
    steps_irq = [
        "1. Застосунок робить I/O системний виклик",
        "2. Ядро додає команду в SQ і подзвонить у Doorbell",
        "3. Потік засинає (TASK_UNINTERRUPTIBLE)",
        "4. Контекст перемикається на інший процес",
        "5. Пристрій завершує I/O і шле MSI-X IRQ",
        "6. CPU обробляє ISR / SoftIRQ та пробуджує потік",
        "7. Контекст перемикається назад (затримка 2-5 мкс)"
    ]
    y_pos = 110
    for step in steps_irq:
        tb, w, h = svgkit.textbox(205, y_pos, step, size=11, pad=6, fill="#f4f6f8", stroke="#cccccc", min_w=320)
        frags.append(tb)
        y_pos += 40

    # Column 2: Polling-driven
    frags.append(svgkit.rect(420, 50, 350, 350, fill="#f6f9fc", stroke="#d9d9d9", rx=8))
    frags.append(svgkit.text(595, 75, "Активне опитування (IO Polling)", size=13, color=svgkit.NEG, bold=True))
    
    steps_poll = [
        "1. Застосунок подає запит (RWF_HIPRI / IOPOLL)",
        "2. Ядро додає команду у Poll-чергу (без IRQ)",
        "3. Потік НЕ засинає і не робить context switch",
        "4. CPU активно перевіряє (spins) NVMe CQ у пам'яті",
        "5. Пристрій записує completion у CQ (без IRQ)",
        "6. CPU миттєво виявляє запис у пам'яті",
        "7. Виконання повертається в користувацький код"
    ]
    y_pos = 110
    for step in steps_poll:
        tb, w, h = svgkit.textbox(595, y_pos, step, size=11, pad=6, fill="#e8f0fe", stroke="#aecbfa", min_w=320)
        frags.append(tb)
        y_pos += 40

    svgkit.render(svg_path, 800, 420, *frags, title="Interrupts vs Polling")

if __name__ == "__main__":
    render_figs()
