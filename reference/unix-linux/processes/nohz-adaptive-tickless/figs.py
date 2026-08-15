import sys
import os

# Path to scripts directory for svgkit import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../scripts')))

from svgkit import render, text, line, rect, textbox, fitbox, arrow, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def generate_timeline():
    frags = []
    
    # 1. Periodic Tick
    frags.append(text(400, 25, "Періодичний системний тик (CONFIG_HZ = 1000 Гц)", size=14, bold=True))
    frags.append(line(50, 55, 750, 55, sw=2, color=LINE))
    
    # Process bar
    frags.append(rect(50, 45, 700, 20, fill="#e1f5fe", stroke="#0288d1"))
    frags.append(text(400, 59, "Процес користувача (переривання кожні 1 мс)", size=11, color="#01579b"))
    
    for i in range(1, 15):
        x = 50 + i * 46
        frags.append(line(x, 40, x, 70, color=NEG, sw=2))
    frags.append(text(96, 33, "Тик 1мс", size=9, color=NEG))

    # 2. NO_HZ_IDLE
    frags.append(text(400, 115, "Динамічний тик у простої (CONFIG_NO_HZ_IDLE)", size=14, bold=True))
    frags.append(line(50, 145, 750, 145, sw=2, color=LINE))
    
    # Active process with ticks
    frags.append(rect(50, 135, 230, 20, fill="#e1f5fe", stroke="#0288d1"))
    frags.append(text(165, 149, "Активний процес (тики є)", size=11, color="#01579b"))
    for i in range(1, 5):
        x = 50 + i * 46
        frags.append(line(x, 130, x, 160, color=NEG, sw=2))
        
    # Idle block without ticks
    frags.append(rect(280, 135, 240, 20, fill="#f5f5f5", stroke="#bdbdbd"))
    frags.append(text(400, 149, "Простій CPU Idle (тиків немає)", size=11, color="#616161", italic=True))
    
    # Resume process with ticks
    frags.append(rect(520, 135, 230, 20, fill="#e1f5fe", stroke="#0288d1"))
    frags.append(text(635, 149, "Активний процес (тики є)", size=11, color="#01579b"))
    for i in range(11, 15):
        x = 50 + i * 46
        frags.append(line(x, 130, x, 160, color=NEG, sw=2))

    # 3. NO_HZ_FULL
    frags.append(text(400, 205, "Адаптивне ядро без тиків (CONFIG_NO_HZ_FULL)", size=14, bold=True))
    frags.append(line(50, 235, 750, 235, sw=2, color=LINE))
    
    # Full monopoly process without ticks
    frags.append(rect(50, 225, 700, 20, fill="#e8f5e9", stroke="#388e3c"))
    frags.append(text(400, 239, "Один процес на ізольованому ядрі (тиків немає, 100% CPU)", size=11, color="#1b5e20", bold=True))
    
    # Only boot/first tick
    frags.append(line(96, 220, 96, 250, color=NEG, sw=2))
    frags.append(text(96, 213, "Останній тик", size=9, color=NEG))

    render(os.path.join(IMG_DIR, 'nohz-timeline.svg'), 800, 280, *frags)

def generate_architecture():
    frags = []
    
    frags.append(text(400, 22, "Архітектура розділення ядер при NO_HZ_FULL", size=15, bold=True))
    
    # Left box: Housekeeping CPU
    frags.append(rect(40, 45, 340, 310, fill="#fff3e0", stroke="#f57c00", sw=2, rx=6))
    frags.append(text(210, 70, "Housekeeping CPU (CPU 0)", size=14, bold=True, color="#e65100"))
    
    frags.append(fitbox(60, 90, 300, 50, "Періодичний системний тик\nCONFIG_HZ (1000 Гц)", size=12, fill="#ffe0b2", stroke="#ffb74d"))
    frags.append(fitbox(60, 155, 300, 50, "Оновлення jiffies, wall clock\nта системної статистики", size=12, fill="#ffe0b2", stroke="#ffb74d"))
    frags.append(fitbox(60, 220, 300, 50, "Обробка апаратних IRQ\n(irqaffinity=0)", size=12, fill="#ffe0b2", stroke="#ffb74d"))
    frags.append(fitbox(60, 285, 300, 55, "RCU Offloading threads (rcuop/1)\nОбслуговування RCU колбеків", size=12, fill="#ffe0b2", stroke="#ffb74d"))
    
    # Arrow between CPUs
    frags.append(arrow(385, 312, 415, 312, sw=2, color="#757575"))
    frags.append(text(400, 300, "RCU колбеки", size=10, color=MUTED, bold=True))
    
    # Right box: Isolated CPU
    frags.append(rect(420, 45, 340, 310, fill="#e8f5e9", stroke="#388e3c", sw=2, rx=6))
    frags.append(text(590, 70, "Isolated CPU (CPU 1..N)", size=14, bold=True, color="#1b5e20"))
    
    frags.append(fitbox(440, 90, 300, 50, "NO_HZ_FULL активний:\nСистемний тик вимкнено", size=12, fill="#c8e6c9", stroke="#81c784"))
    frags.append(fitbox(440, 155, 300, 50, "Монополія одного процесу\n(Runnable task count = 1)", size=12, fill="#c8e6c9", stroke="#81c784"))
    frags.append(fitbox(440, 220, 300, 50, "Апаратні переривання відсутні\n(IRQ routed to CPU 0)", size=12, fill="#c8e6c9", stroke="#81c784"))
    frags.append(fitbox(440, 285, 300, 55, "Делегування RCU станів спокою\nбез зупинки виконання", size=12, fill="#c8e6c9", stroke="#81c784"))
    
    render(os.path.join(IMG_DIR, 'nohz-architecture.svg'), 800, 375, *frags)

if __name__ == '__main__':
    generate_timeline()
    generate_architecture()
    print("Figures generated successfully.")
