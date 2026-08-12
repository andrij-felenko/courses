import os
import sys

# Path to scripts/ directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts")))
from svgkit import render, rect, text, line, arrow, mtext, textbox, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG

def draw_eas_architecture():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    path = os.path.join(img_dir, "eas-architecture.svg")

    frags = []
    w, h = 800, 440

    # Title
    frags.append(text(w / 2, 25, "Архітектурна схема Energy-Aware Scheduling (EAS)", size=16, bold=True))

    # High-level component boxes
    # Top box: Scheduler & PELT
    frags.append(rect(40, 50, 720, 75, fill="#eef2f7", stroke="#2c3e50", sw=1.5, rx=8))
    frags.append(text(400, 72, "Планувальник CFS та оцінка навантаження PELT", size=15, bold=True, color="#2c3e50"))
    frags.append(text(400, 98, "Обчислення util_avg та capacity_of(cpu) для кожного ядра", size=13, color=MUTED))

    # Middle Left: EAS placement engine
    frags.append(rect(40, 150, 340, 110, fill="#e8f8f5", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(210, 175, "EAS (Energy-Aware Scheduling)", size=15, bold=True, color=FIELD))
    frags.append(text(210, 200, "select_task_rq_fair()", size=13, bold=True, color=INK))
    frags.append(text(210, 222, "find_energy_efficient_cpu()", size=12, color=MUTED))
    frags.append(text(210, 242, "Мінімізація дельти енергії ΔE", size=12, bold=True, color=POS))

    # Middle Right: Energy Model & OPP
    frags.append(rect(420, 150, 340, 110, fill="#fef9e7", stroke="#f39c12", sw=1.8, rx=8))
    frags.append(text(590, 175, "Energy Model (EM Framework)", size=15, bold=True, color="#d35400"))
    frags.append(text(590, 200, "struct em_perf_domain", size=13, bold=True, color=INK))
    frags.append(text(590, 222, "Таблиці OPP (Частота f, Напруга V, Потужність P)", size=12, color=MUTED))
    frags.append(text(590, 242, "Коефіцієнти споживання для кожного кластера", size=12, color=MUTED))

    # Bottom Left: cpufreq & schedutil
    frags.append(rect(40, 285, 720, 50, fill="#f4f6f7", stroke="#7f8c8d", sw=1.5, rx=6))
    frags.append(text(400, 315, "Інтеграція з cpufreq (schedutil governor) → Прогнозування частоти OPP", size=13, bold=True, color="#34495e"))

    # Bottom Cores: LITTLE vs BIG
    frags.append(rect(40, 355, 340, 65, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(210, 380, "Енергоефективні ядра (LITTLE)", size=14, bold=True, color=NEG))
    frags.append(text(210, 402, "Низьке базове споживання, низька місткість", size=12, color=MUTED))

    frags.append(rect(420, 355, 340, 65, fill="#fdedec", stroke=POS, sw=1.5, rx=6))
    frags.append(text(590, 380, "Продуктивні ядра (big / Super)", size=14, bold=True, color=POS))
    frags.append(text(590, 402, "Висока обчислювальна потужність, високі питомі витрати", size=12, color=MUTED))

    # Connecting arrows
    frags.append(arrow(210, 125, 210, 150, color=LINE))
    frags.append(arrow(590, 125, 590, 150, color=LINE))
    frags.append(arrow(420, 205, 380, 205, color=FIELD, sw=2.0))
    frags.append(arrow(210, 260, 210, 285, color=LINE))
    frags.append(arrow(210, 335, 210, 355, color=NEG, sw=2.0))
    frags.append(arrow(590, 335, 590, 355, color=POS, sw=2.0))

    render(path, w, h, *frags)
    print(f"Generated {path}")

def draw_eas_wakeup_flow():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    path = os.path.join(img_dir, "eas-wakeup-flow.svg")

    frags = []
    w, h = 800, 420

    frags.append(text(w / 2, 25, "Алгоритм вибору ядра при пробудженні задачі (EAS Wake-Up Flow)", size=16, bold=True))

    # Box 1: Wake up event
    frags.append(rect(50, 60, 200, 50, fill="#eef2f7", stroke="#2c3e50", sw=1.5, rx=6))
    frags.append(text(150, 90, "Пробудження задачі", size=13, bold=True))

    # Arrow 1
    frags.append(arrow(250, 85, 300, 85, color=LINE))

    # Box 2: Overutilized decision
    frags.append(rect(300, 60, 200, 50, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    frags.append(text(400, 82, "Система over-utilized?", size=13, bold=True))
    frags.append(text(400, 100, "(util > 80% capacity)", size=11, color=MUTED))

    # Branch YES -> CFS fast path
    frags.append(arrow(400, 110, 400, 170, color=POS, sw=1.8))
    frags.append(text(415, 140, "ТАК", size=12, bold=True, color=POS))
    frags.append(rect(300, 170, 200, 50, fill="#fdedec", stroke=POS, sw=1.5, rx=6))
    frags.append(text(400, 192, "Класичний CFS Path", size=13, bold=True, color=POS))
    frags.append(text(400, 210, "Балансування навантаження", size=11, color=MUTED))

    # Branch NO -> Enter EAS
    frags.append(arrow(500, 85, 550, 85, color=FIELD, sw=1.8))
    frags.append(text(525, 75, "НІ", size=12, bold=True, color=FIELD))

    frags.append(rect(550, 60, 200, 50, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(650, 82, "EAS Active Path", size=13, bold=True, color=FIELD))
    frags.append(text(650, 100, "find_energy_efficient_cpu()", size=11, color=MUTED))

    # Down from EAS Path
    frags.append(arrow(650, 110, 650, 170, color=LINE))

    # Step 3: Compute candidate energy
    frags.append(rect(530, 170, 240, 60, fill="#f4f6f7", stroke="#34495e", sw=1.5, rx=6))
    frags.append(text(650, 192, "Обчислення compute_energy()", size=13, bold=True))
    frags.append(text(650, 212, "E_candidate = ∑ Power(OPP) · Util", size=12, color=MUTED))

    # Arrow left to Step 4
    frags.append(arrow(650, 230, 650, 280, color=LINE))

    # Step 4: Min delta calculation
    frags.append(rect(530, 280, 240, 60, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(650, 302, "Обчислення ΔE = E_with - E_without", size=12, bold=True, color=NEG))
    frags.append(text(650, 322, "Вибір ядра з мінімальним ΔE", size=12, bold=True, color=NEG))

    # Arrow left to Enqueue
    frags.append(arrow(530, 310, 300, 310, color=FIELD, sw=2.0))

    # Step 5: Enqueue
    frags.append(rect(100, 280, 200, 60, fill="#e8f8f5", stroke=FIELD, sw=2.0, rx=6))
    frags.append(text(200, 305, "Призначення задачі на ядро", size=14, bold=True, color=FIELD))
    frags.append(text(200, 325, "enqueue_task_fair()", size=12, color=MUTED))

    render(path, w, h, *frags)
    print(f"Generated {path}")

def draw_overutilized_state():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    path = os.path.join(img_dir, "overutilized-state.svg")

    frags = []
    w, h = 800, 380

    frags.append(text(w / 2, 25, "Порівняння режимів: Енергоефективне пакування vs Перевантаження", size=16, bold=True))

    # Mode 1: Normal Energy-Efficient (Packing)
    frags.append(rect(30, 60, 350, 290, fill="#f4f9f4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(205, 88, "Режим 1: Низьке навантаження (EAS Active)", size=14, bold=True, color=FIELD))
    frags.append(text(205, 110, "Сумарне util < 80% capacity", size=12, color=MUTED))

    # LITTLE cores box
    frags.append(rect(50, 130, 310, 90, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(205, 152, "Кластер LITTLE (Задачі згруповано)", size=13, bold=True, color=NEG))
    frags.append(rect(65, 165, 60, 40, fill="#d4e6f1", stroke=NEG, sw=1.0))
    frags.append(text(95, 190, "Task 1", size=11))
    frags.append(rect(135, 165, 60, 40, fill="#d4e6f1", stroke=NEG, sw=1.0))
    frags.append(text(165, 190, "Task 2", size=11))
    frags.append(rect(205, 165, 60, 40, fill="#d4e6f1", stroke=NEG, sw=1.0))
    frags.append(text(235, 190, "Task 3", size=11))
    frags.append(rect(275, 165, 75, 40, fill="#abebc6", stroke=FIELD, sw=1.0))
    frags.append(text(312, 190, "Task 4", size=11, bold=True))

    # big cores box (idle)
    frags.append(rect(50, 240, 310, 85, fill="#f5f5f5", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(205, 270, "Кластер big — СПИТЬ (C-state / CPU Idle)", size=13, bold=True, color=MUTED))
    frags.append(text(205, 295, "0 мВт споживання струму", size=12, color=POS, bold=True))

    # Mode 2: Overutilized (Spreading)
    frags.append(rect(420, 60, 350, 290, fill="#fdf2e9", stroke=POS, sw=1.8, rx=8))
    frags.append(text(595, 88, "Режим 2: Перевантаження (Over-Utilized)", size=14, bold=True, color=POS))
    frags.append(text(595, 110, "Будь-яке ядро util > 80% capacity → EAS Bypass", size=12, color=MUTED))

    # LITTLE cores box
    frags.append(rect(440, 130, 310, 90, fill="#eaf2f8", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(595, 152, "Кластер LITTLE (Максимальна частота)", size=13, bold=True, color=NEG))
    frags.append(rect(455, 165, 130, 40, fill="#d4e6f1", stroke=NEG, sw=1.0))
    frags.append(text(520, 190, "Task 1 + Task 2", size=11))
    frags.append(rect(600, 165, 135, 40, fill="#d4e6f1", stroke=NEG, sw=1.0))
    frags.append(text(667, 190, "Task 3 (Full Util)", size=11))

    # big cores box (active)
    frags.append(rect(440, 240, 310, 85, fill="#fdedec", stroke=POS, sw=1.5, rx=6))
    frags.append(text(595, 262, "Кластер big — АКТИВОВАНО", size=13, bold=True, color=POS))
    frags.append(rect(455, 275, 280, 40, fill="#f5b7b1", stroke=POS, sw=1.0))
    frags.append(text(595, 300, "Heavy Task 4 (High Compute Power)", size=12, bold=True, color="#78281f"))

    render(path, w, h, *frags)
    print(f"Generated {path}")

def render_all():
    draw_eas_architecture()
    draw_eas_wakeup_flow()
    draw_overutilized_state()

if __name__ == '__main__':
    render_all()
