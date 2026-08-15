import sys
import os

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
if os.path.exists(scripts_dir):
    sys.path.insert(0, scripts_dir)
else:
    sys.path.insert(0, r"E:\develop\courses\scripts")

from svgkit import *

def generate_hrtimer_architecture():
    # Figure 1: Comparison between Legacy Timer Wheel and Hrtimer RB-Tree
    w, h = 820, 400
    frags = []
    
    # Title
    frags.append(text(410, 25, "Еволюція підсистеми таймерів у ядрі Linux", size=16, bold=True))
    
    # Box 1: Legacy Timer Wheel
    frags.append(rect(20, 45, 380, 335, fill="#fff8f8", stroke="#e0b0b0", sw=1.5, rx=6))
    frags.append(text(210, 70, "Традиційні таймери (Timer Wheel)", size=14, bold=True, color="#901010"))
    
    frags.append(fitbox(35, 90, 350, 45, "Квантування за тиками HZ (1-10 мс)\nСпільне періодичне переривання ядра", size=12, fill="#ffffff", stroke="#d0d0d0"))
    
    # Wheel diagram / buckets
    frags.append(rect(35, 150, 350, 110, fill="#fdf0f0", stroke="#d8a8a8", sw=1, rx=4))
    frags.append(text(210, 170, "Масив кошиків (Wheel Buckets)", size=13, bold=True, color="#802020"))
    
    for i in range(5):
        bx = 50 + i * 65
        fill_col = "#e8b8b8" if i == 2 else "#ffffff"
        frags.append(rect(bx, 185, 55, 35, fill=fill_col, stroke="#a05050", sw=1, rx=3))
        frags.append(text(bx + 27.5, 207, f"tv{i+1}", size=11, color="#401010", bold=True))
        
    frags.append(fitbox(45, 230, 330, 22, "Каскадування кошиків: перерозподіл O(N)", size=11, fill="#fdf0f0", stroke="none"))
    
    # Bottom legacy summary
    frags.append(fitbox(35, 275, 350, 85, "Джиттер-відхилення до ±10 мс\nНеможливість субмілісекундного засинання\nНеперервні переривання в режимі Idle", size=11, fill="#f5e5e5", stroke="#c89898", color="#501010"))

    # Box 2: Hrtimers Subsystem
    frags.append(rect(420, 45, 380, 335, fill="#f4f9f4", stroke="#b0d8b0", sw=1.5, rx=6))
    frags.append(text(610, 70, "Таймери високої точності (hrtimers)", size=14, bold=True, color="#106010"))
    
    frags.append(fitbox(435, 90, 350, 45, "Наносекундна точність (ktime_t 64-bit)\nАпаратний режим One-Shot", size=12, fill="#ffffff", stroke="#d0d0d0"))
    
    # RB Tree
    frags.append(rect(435, 150, 350, 110, fill="#eaf4ea", stroke="#98c898", sw=1, rx=4))
    frags.append(text(610, 170, "Червоно-чорне дерево (timerqueue)", size=13, bold=True, color="#105010"))
    
    # RB Tree Nodes
    frags.append(circle(610, 195, 14, fill="#333333", stroke="#000000", sw=1.5))
    frags.append(text(610, 199, "T2", size=10, bold=True, color="#ffffff"))

    frags.append(circle(540, 230, 14, fill="#cc3333", stroke="#880000", sw=1.5))
    frags.append(text(540, 234, "T1", size=10, bold=True, color="#ffffff"))

    frags.append(circle(680, 230, 14, fill="#cc3333", stroke="#880000", sw=1.5))
    frags.append(text(680, 234, "T3", size=10, bold=True, color="#ffffff"))
    
    frags.append(line(598, 202, 552, 223, color="#404040", sw=1.5))
    frags.append(line(622, 202, 668, 223, color="#404040", sw=1.5))
    
    frags.append(text(610, 253, "Найлівіший вузол T1 (earliest) → O(1) доступ", size=11, bold=True, color="#106010"))

    # Bottom Hrtimers Summary
    frags.append(fitbox(435, 275, 350, 85, "Апаратне перепрограмування LAPIC / HPET\nМінімальний джиттер (< 10 мкс)\nІнтеграція з NOHZ для вимкнення тиків", size=11, fill="#e2f0e2", stroke="#88c088", color="#054005"))

    img_path = os.path.join(os.path.dirname(__file__), "img", "hrtimer-architecture.svg")
    render(img_path, w, h, *frags)

def generate_hrtimer_interrupt_flow():
    # Figure 2: Interrupt flow and reprogramming cycle of hrtimer_interrupt
    w, h = 820, 360
    frags = []
    
    frags.append(text(410, 25, "Цикл обробки переривання та перепрограмування clockevent пристрою", size=15, bold=True))
    
    # Step 1
    frags.append(fitbox(20, 55, 220, 80, "1. Апаратна подія\n\nAPIC / HPET генерує hardirq\nза досягненням часу", size=11, fill="#fef2f2", stroke="#fca5a5", color="#7f1d1d"))
    frags.append(arrow(240, 95, 275, 95, color="#6b7280", sw=2))
    
    # Step 2
    frags.append(fitbox(280, 55, 250, 80, "2. hrtimer_interrupt()\n\nЗчитування ktime_get()\nОбхід застарілих вузлів RB-дерева", size=11, fill="#eff6ff", stroke="#93c5fd", color="#1e3a8a"))
    frags.append(arrow(530, 95, 565, 95, color="#6b7280", sw=2))
    
    # Step 3
    frags.append(fitbox(570, 55, 230, 80, "3. Виклик function()\n\nВиконання callbacks\n(hardirq або HRTIMER_SOFTIRQ)", size=11, fill="#f0fdf4", stroke="#86efac", color="#14532d"))
    frags.append(arrow(685, 135, 685, 175, color="#6b7280", sw=2))
    
    # Step 4
    frags.append(fitbox(570, 180, 230, 80, "4. Оцінка наступного часу\n\nВизначення найближчого\nвузла T_next у RB-дереві", size=11, fill="#faf5ff", stroke="#d8b4fe", color="#581c87"))
    frags.append(arrow(570, 220, 535, 220, color="#6b7280", sw=2))
    
    # Step 5
    frags.append(fitbox(280, 180, 250, 80, "5. tick_program_event()\n\nЗапис розрахованого відліку\nв одноразовий регістр APIC", size=11, fill="#fff7ed", stroke="#fdba74", color="#7c2d12"))

    # Bottom Summary
    frags.append(fitbox(20, 280, 780, 55, "Результат: ядро не витрачає час на проміжні марні переривання та прокидається строго в момент T_next", size=12, fill="#f3f4f6", stroke="#d1d5db", color="#374151", bold=True))

    img_path = os.path.join(os.path.dirname(__file__), "img", "hrtimer-interrupt-flow.svg")
    render(img_path, w, h, *frags)

if __name__ == "__main__":
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    generate_hrtimer_architecture()
    generate_hrtimer_interrupt_flow()
