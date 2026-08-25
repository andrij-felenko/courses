import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
try:
    from svgkit import *
except ImportError:
    print("WARNING: svgkit not found")
    sys.exit(0)

def draw_cpufreq_arch():
    w, h = 850, 490
    frags = []

    # Layers / Containers
    frags.append(rect(20, 45, 810, 80, fill="#f4f6f8", stroke="#95a5a6", sw=1.5, rx=8))
    frags.append(text(40, 65, "Користувацький простір / Процеси", size=12, bold=True, color="#7f8c8d", anchor="start"))
    
    frags.append(rect(20, 145, 810, 200, fill="#eaf2f8", stroke="#2980b9", sw=1.5, rx=8))
    frags.append(text(40, 165, "Підсистема ядра Linux (cpufreq framework)", size=12, bold=True, color="#2980b9", anchor="start"))

    frags.append(rect(20, 365, 810, 95, fill="#fdf2e9", stroke="#d35400", sw=1.5, rx=8))
    frags.append(text(40, 385, "Апаратний рівень (CPU Hardware / PCU)", size=12, bold=True, color="#d35400", anchor="start"))

    # Userspace box
    bx_apps, _, _ = textbox(160, 95, "Застосунки та потоки\n(створюють навантаження)", bold=True, fill="#ffffff", stroke="#7f8c8d")
    frags.append(bx_apps)

    bx_sysfs, _, _ = textbox(440, 95, "Інтерфейс sysfs\n/sys/.../cpufreq/", bold=True, fill="#ffffff", stroke="#7f8c8d")
    frags.append(bx_sysfs)

    bx_pmqos, _, _ = textbox(700, 95, "PM QoS Запити\n/dev/cpu_dma_latency", bold=True, fill="#ffffff", stroke="#7f8c8d")
    frags.append(bx_pmqos)

    # Kernel boxes
    bx_gov, _, _ = textbox(160, 255, "Cpufreq Governor\n(schedutil / performance)", bold=True, fill="#e8f8f5", stroke="#16a085")
    frags.append(bx_gov)

    bx_core, _, _ = textbox(440, 255, "Ядро cpufreq\n(cpufreq core)", bold=True, fill="#d4efdf", stroke="#27ae60")
    frags.append(bx_core)

    bx_drv, _, _ = textbox(700, 255, "Драйвер cpufreq\n(intel_pstate / amd-pstate)", bold=True, fill="#ebdef0", stroke="#8e44ad")
    frags.append(bx_drv)

    # Hardware boxes
    bx_msr, _, _ = textbox(250, 425, "Регістри MSR / CPPC\n(IA32_HWP_REQUEST)", bold=True, fill="#ffffff", stroke="#d35400")
    frags.append(bx_msr)

    bx_pcu, _, _ = textbox(600, 425, "Power Control Unit (PCU)\nТактовий генератор & VRM", bold=True, fill="#ffffff", stroke="#d35400")
    frags.append(bx_pcu)

    # Arrows (start at Y=180, below title text at Y=165)
    frags.append(arrow(160, 180, 160, 225, color="#16a085"))
    frags.append(arrow(440, 180, 440, 225, color="#27ae60"))
    frags.append(arrow(700, 180, 700, 225, color="#8e44ad"))

    frags.append(arrow(235, 255, 365, 255, color="#16a085"))
    frags.append(arrow(515, 255, 615, 255, color="#27ae60"))

    frags.append(arrow(700, 285, 600, 400, color="#8e44ad"))
    frags.append(arrow(440, 285, 250, 400, color="#27ae60"))
    frags.append(arrow(345, 425, 480, 425, color="#d35400"))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "cpufreq-architecture.svg"), w, h, *frags, title="Архітектура підсистеми cpufreq у Linux")

def draw_cpuidle_cstates():
    w, h = 860, 440
    frags = []

    # Columns for C-states
    states = [
        ("C0 Active", "Виконання інструкцій\nP-стани (DVFS)\n100% споживання", "#fbeee6", "#e67e22", "0 мкс"),
        ("C1 / C1E Halt", "Інструкція HLT / WFI\nЗупинка конвеєра\nКеші когерентні", "#fef9e7", "#f1c40f", "1-2 мкс"),
        ("C3 Sleep", "Зупинка такту ядра\nВимкнено L1/L2 snoop\nЗбереження контексту", "#eafaf1", "#2ecc71", "20-50 мкс"),
        ("C6 Deep Sleep", "Power Gating (0 В)\nКонтекст у SRAM\nВимкнено живлення", "#ebf5fb", "#3498db", "100-200 мкс"),
        ("PC-states", "Вимкнено Uncore / L3\nМодуль пам'яті в Self-Refresh\nМінімальне споживання", "#f4ecf7", "#9b59b6", "> 500 мкс")
    ]

    col_w = 155
    start_x = 30
    top_y = 70

    for i, (name, desc, bg, st_col, lat) in enumerate(states):
        cx = start_x + i * (col_w + 12)
        # Header box
        frags.append(rect(cx, top_y, col_w, 40, fill=st_col, stroke=st_col, rx=6))
        frags.append(text(cx + col_w/2, top_y + 24, name, size=13, bold=True, color="#ffffff"))

        # Details box
        frags.append(rect(cx, top_y + 48, col_w, 230, fill=bg, stroke=st_col, rx=6))
        lines = desc.split("\n")
        for j, line_txt in enumerate(lines):
            frags.append(text(cx + col_w/2, top_y + 85 + j * 24, line_txt, size=11, color="#2c3e50"))

        # Latency pill
        frags.append(rect(cx + 10, top_y + 240, col_w - 20, 26, fill="#ffffff", stroke=st_col, rx=13))
        frags.append(text(cx + col_w/2, top_y + 257, f"Затримка: {lat}", size=11, bold=True, color=st_col))

    # Bottom Axis / Legend
    frags.append(rect(30, 360, 803, 50, fill="#f8f9f9", stroke="#bdc3c7", rx=6))
    frags.append(arrow(50, 385, 410, 385, color="#e67e22", sw=2.5))
    frags.append(text(230, 403, "Енергозбереження зростає →", size=12, bold=True, color="#e67e22"))

    frags.append(arrow(810, 385, 450, 385, color="#c0392b", sw=2.5))
    frags.append(text(630, 403, "← Затримка пробудження зростає", size=12, bold=True, color="#c0392b"))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    render(os.path.join(out_dir, "cpuidle-cstates-hierarchy.svg"), w, h, *frags, title="Ієрархія станів простою CPU (C-states та PC-states)")

def draw_cstate_residency():
    w, h = 820, 420
    frags = []

    # Axis
    frags.append(line(80, 340, 760, 340, color="#2c3e50", sw=2)) # X Time
    frags.append(line(80, 340, 80, 70, color="#2c3e50", sw=2))  # Y Power
    frags.append(text(760, 360, "Час (t)", size=12, bold=True, color="#2c3e50", anchor="end"))
    frags.append(text(75, 60, "Потужність (P)", size=12, bold=True, color="#2c3e50", anchor="start"))

    # Active power level
    frags.append(line(80, 110, 740, 110, color="#e74c3c", sw=1.5, dash="4,4"))
    frags.append(text(85, 102, "P_active (активний стан C0)", size=11, bold=True, color="#e74c3c", anchor="start"))

    # Idle C-state power level
    frags.append(line(80, 290, 740, 290, color="#27ae60", sw=1.5, dash="4,4"))
    frags.append(text(85, 282, "P_idle (глибокий C-стан C6)", size=11, bold=True, color="#27ae60", anchor="start"))

    # Power curve during transition
    pts = [(80, 110), (200, 110), (220, 75), (260, 290), (540, 290), (570, 75), (620, 110), (740, 110)]
    path_d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
    frags.append(f'<path d="{path_d}" fill="none" stroke="#2980b9" stroke-width="2.5"/>')

    # Shaded penalty regions
    frags.append('<polygon points="200,110 220,75 260,290 200,290" fill="#fadbd8" opacity="0.6"/>')
    frags.append(text(225, 170, "E_entry", size=11, bold=True, color="#c0392b"))

    frags.append('<polygon points="540,290 570,75 620,110 620,290" fill="#fadbd8" opacity="0.6"/>')
    frags.append(text(575, 170, "E_exit", size=11, bold=True, color="#c0392b"))

    # Saved energy region
    frags.append('<polygon points="260,110 540,110 540,290 260,290" fill="#d4efdf" opacity="0.6"/>')
    frags.append(text(400, 200, "Зекономлена енергія в C-стані", size=12, bold=True, color="#1e8449"))

    # Target residency annotation
    frags.append(line(260, 340, 260, 355, color="#2980b9", sw=1.5))
    frags.append(line(540, 340, 540, 355, color="#2980b9", sw=1.5))
    frags.append(arrow(260, 350, 540, 350, color="#2980b9"))
    frags.append(arrow(540, 350, 260, 350, color="#2980b9"))
    frags.append(text(400, 370, "Мінімальний час перебування (Target Residency)", size=11, bold=True, color="#2980b9"))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    render(os.path.join(out_dir, "cstate-residency-energy.svg"), w, h, *frags, title="Енергетичний баланс та Target Residency при переході в C-стан")

def draw_eas_energy_model():
    w, h = 840, 440
    frags = []

    # Left: Task scheduler & EAS decision
    frags.append(rect(20, 60, 380, 350, fill="#fcf3cf", stroke="#f1c40f", rx=8))
    frags.append(text(210, 85, "Планувальник EAS (select_task_rq_fair)", size=13, bold=True, color="#b7950b"))

    bx_task, _, _ = textbox(210, 135, "Нове / Пробуджене завдання\nМетрика завантаження PELT (util)", bold=True, fill="#ffffff", stroke="#f39c12")
    frags.append(bx_task)

    bx_calc, _, _ = textbox(210, 230, "Розрахунок ΔE (Energy Delta)\nE_system(LITTLE) vs E_system(big)", bold=True, fill="#fef9e7", stroke="#d68910")
    frags.append(bx_calc)

    bx_decision, _, _ = textbox(210, 340, "Вибір оптимального ядра\nз мінімальним споживанням", bold=True, fill="#f9e79f", stroke="#b7950b")
    frags.append(bx_decision)

    frags.append(arrow(210, 165, 210, 200, color="#f39c12"))
    frags.append(arrow(210, 260, 210, 310, color="#d68910"))

    # Right: Energy Model & Clusters
    frags.append(rect(430, 60, 390, 350, fill="#ebf5fb", stroke="#3498db", rx=8))
    frags.append(text(625, 85, "Енергетична Модель (Energy Model)", size=13, bold=True, color="#2980b9"))

    # LITTLE cluster
    frags.append(rect(450, 110, 350, 110, fill="#e8f8f5", stroke="#1ea27a", rx=6))
    frags.append(text(465, 132, "Кластер LITTLE (Енергоефективний)", size=12, bold=True, color="#1ea27a", anchor="start"))
    frags.append(text(465, 160, "• Низька пікова потужність (Capacity: 350)", size=11, color="#2c3e50", anchor="start"))
    frags.append(text(465, 182, "• Висока ефективність на малих частотах", size=11, color="#2c3e50", anchor="start"))
    frags.append(text(465, 204, "• Таблиця: [Freq, Cap, Power]", size=11, italic=True, color="#7f8c8d", anchor="start"))

    # big cluster
    frags.append(rect(450, 240, 350, 150, fill="#fadbd8", stroke="#e74c3c", rx=6))
    frags.append(text(465, 262, "Кластер big (Високопродуктивний)", size=12, bold=True, color="#c0392b", anchor="start"))
    frags.append(text(465, 290, "• Висока обчислювальна здатність (1024)", size=11, color="#2c3e50", anchor="start"))
    frags.append(text(465, 312, "• Кубічний ріст потужності з частотою (P ∝ f³)", size=11, color="#2c3e50", anchor="start"))
    frags.append(text(465, 334, "• Використовується для важких задач", size=11, color="#2c3e50", anchor="start"))
    frags.append(text(465, 356, "• Інтеграція з cpufreq schedutil", size=11, italic=True, color="#7f8c8d", anchor="start"))

    # Inter-box arrow
    frags.append(arrow(310, 230, 445, 165, color="#2980b9"))
    frags.append(arrow(310, 230, 445, 310, color="#2980b9"))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    render(os.path.join(out_dir, "eas-energy-model.svg"), w, h, *frags, title="Модель Energy-Aware Scheduling (EAS) та завантаження ядер")

if __name__ == "__main__":
    draw_cpufreq_arch()
    draw_cpuidle_cstates()
    draw_cstate_residency()
    draw_eas_energy_model()
    print("SVG figures generated successfully.")
