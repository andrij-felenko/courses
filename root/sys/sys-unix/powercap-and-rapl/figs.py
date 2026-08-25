import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
try:
    from svgkit import *
except ImportError:
    print("WARNING: svgkit not found")
    sys.exit(0)

def draw_rapl_sliding_window():
    w, h = 860, 470
    frags = []

    # Background canvas elements
    frags.append(rect(15, 15, 830, 440, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    frags.append(text(430, 42, "Модель ковзного вікна потужності RAPL (PL1, PL2 та бюджет енергії)", size=14, bold=True, color="#2c3e50"))

    # Coordinate Axes
    origin_x, origin_y = 90, 360
    axis_w, axis_h = 720, 280

    # Axes
    frags.append(line(origin_x, origin_y, origin_x + axis_w, origin_y, color="#2c3e50", sw=2)) # X axis (Time)
    frags.append(line(origin_x, origin_y, origin_x, origin_y - axis_h, color="#2c3e50", sw=2)) # Y axis (Power)

    frags.append(text(origin_x + axis_w, origin_y + 25, "Час (t)", size=12, bold=True, color="#2c3e50", anchor="end"))
    frags.append(text(origin_x - 15, origin_y - axis_h + 10, "Потужність (Вт)", size=12, bold=True, color="#2c3e50", anchor="end"))

    # Power Limit Horizontal Lines
    # PL2 (Short term / Burst)
    y_pl2 = origin_y - 230
    frags.append(line(origin_x, y_pl2, origin_x + axis_w - 20, y_pl2, color="#c0392b", sw=2, dash="5,4"))
    frags.append(text(origin_x + axis_w - 15, y_pl2 + 4, "PL2 (Короткотривалий ліміт / Turbo Burst)", size=11, bold=True, color="#c0392b", anchor="end"))

    # PL1 (Long term / Sustained TDP)
    y_pl1 = origin_y - 130
    frags.append(line(origin_x, y_pl1, origin_x + axis_w - 20, y_pl1, color="#d35400", sw=2, dash="5,4"))
    frags.append(text(origin_x + axis_w - 15, y_pl1 + 4, "PL1 (Довготривалий ліміт / Базовий TDP)", size=11, bold=True, color="#d35400", anchor="end"))

    # Idle power
    y_idle = origin_y - 30
    frags.append(line(origin_x, y_idle, origin_x + axis_w - 20, y_idle, color="#27ae60", sw=1.5, dash="3,3"))
    frags.append(text(origin_x + axis_w - 15, y_idle + 4, "P_idle (Стан простою)", size=10, bold=True, color="#27ae60", anchor="end"))

    # Actual Power Curve (Polyline / Path)
    # Phase 1: Idle (0 to 60) -> Burst jump to PL2 (60 to 180) -> Decaying to PL1 (180 to 260) -> Sustained at PL1 (260 to 460) -> Drop to idle (460 to 520) -> Short spike within PL2 (520 to 600) -> Idle (600 to 700)
    pts = [
        (origin_x, y_idle),
        (origin_x + 60, y_idle),
        (origin_x + 70, y_pl2),
        (origin_x + 190, y_pl2),
        (origin_x + 250, y_pl1),
        (origin_x + 440, y_pl1),
        (origin_x + 470, y_idle),
        (origin_x + 530, y_idle),
        (origin_x + 545, y_pl2 - 15),
        (origin_x + 590, y_pl2 - 15),
        (origin_x + 610, y_idle),
        (origin_x + 700, y_idle)
    ]
    path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    
    # Area under curve (Energy integral)
    poly_pts = f"{origin_x},{origin_y} " + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f" {origin_x+700},{origin_y}"
    frags.append(f'<polygon points="{poly_pts}" fill="#3498db" opacity="0.15"/>')
    frags.append(f'<path d="{path_d}" fill="none" stroke="#2980b9" stroke-width="3"/>')

    # Shaded Burst Energy Area above PL1
    burst_poly = f"{origin_x+70},{y_pl1} {origin_x+70},{y_pl2} {origin_x+190},{y_pl2} {origin_x+250},{y_pl1}"
    frags.append(f'<polygon points="{burst_poly}" fill="#e74c3c" opacity="0.35"/>')
    frags.append(text(origin_x + 150, y_pl2 + 45, "Використаний запас енергії (Burst Credit)", size=10, bold=True, color="#922b21"))

    # Time window annotations
    # Tau 2 (Short window)
    frags.append(line(origin_x + 70, origin_y + 8, origin_x + 70, origin_y + 25, color="#c0392b", sw=1.5))
    frags.append(line(origin_x + 250, origin_y + 8, origin_x + 250, origin_y + 25, color="#c0392b", sw=1.5))
    frags.append(arrow(origin_x + 160, origin_y + 18, origin_x + 70, origin_y + 18, color="#c0392b", sw=1.5))
    frags.append(arrow(origin_x + 160, origin_y + 18, origin_x + 250, origin_y + 18, color="#c0392b", sw=1.5))
    frags.append(text(origin_x + 160, origin_y + 35, "Tau_2 (Time Window PL2: ~2.4–10 мс)", size=10, bold=True, color="#c0392b"))

    # Tau 1 (Long window / Sliding average)
    frags.append(line(origin_x + 70, origin_y + 45, origin_x + 70, origin_y + 65, color="#d35400", sw=1.5))
    frags.append(line(origin_x + 440, origin_y + 45, origin_x + 440, origin_y + 65, color="#d35400", sw=1.5))
    frags.append(arrow(origin_x + 255, origin_y + 55, origin_x + 70, origin_y + 55, color="#d35400", sw=1.5))
    frags.append(arrow(origin_x + 255, origin_y + 55, origin_x + 440, origin_y + 55, color="#d35400", sw=1.5))
    frags.append(text(origin_x + 255, origin_y + 72, "Tau_1 (Time Window PL1: ~28–32 с)", size=10, bold=True, color="#d35400"))

    # Formula Box
    bx_f, _, _ = textbox(570, 105, "Математична умова RAPL:\n(1 / Tau) ∫ P(t) dt ≤ P_limit\nPCU обмежує DVFS при вичерпанні бюджету", size=10.5, pad=8, fill="#fcf3cf", stroke="#f39c12")
    frags.append(bx_f)

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "rapl-sliding-window.svg"), w, h, *frags, title="Модель ковзного вікна потужності RAPL")

def draw_powercap_sysfs_hierarchy():
    w, h = 870, 480
    frags = []

    frags.append(rect(15, 15, 840, 450, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    frags.append(text(435, 42, "Ієрархія зон powercap sysfs та відповідність апаратним доменам CPU", size=14, bold=True, color="#2c3e50"))

    # Root Sysfs Directory Box
    bx_root, _, _ = textbox(435, 80, "Корінь підсистеми: /sys/class/powercap/intel-rapl/", size=11, bold=True, fill="#eaeded", stroke="#7f8c8d")
    frags.append(bx_root)

    # Package Zone (intel-rapl:0)
    frags.append(rect(35, 125, 800, 320, fill="#ebf5fb", stroke="#2980b9", sw=1.8, rx=8))
    frags.append(text(55, 148, "Зона сокета: intel-rapl:0 (Package / SoC)", size=12, bold=True, color="#1b4f72", anchor="start"))
    frags.append(text(55, 168, "Файли: name (\"package-0\"), enabled, energy_uj, max_energy_range_uj", size=10.5, color="#2c3e50", anchor="start"))
    frags.append(text(55, 186, "Обмеження: constraint_0 (PL1 / long_term), constraint_1 (PL2 / short_term)", size=10.5, bold=True, color="#2980b9", anchor="start"))

    # Subzones (Core, DRAM, Uncore, Psys)
    subzones = [
        ("intel-rapl:0:0", "Домен ядер (Core / PP0)", "name: \"core\"\nenergy_uj\nconstraint_0_power_limit_uw\nconstraint_0_time_window_us", "#e8f8f5", "#16a085"),
        ("intel-rapl:0:1", "Домен пам'яті (DRAM)", "name: \"dram\"\nenergy_uj\nconstraint_0_power_limit_uw\nconstraint_0_time_window_us", "#fef9e7", "#f39c12"),
        ("intel-rapl:0:2", "Незв'язані блоки (Uncore/PP1)", "name: \"uncore\"\nenergy_uj\n(вбудована графіка iGPU / L3)", "#f4ecf7", "#8e44ad"),
        ("intel-rapl:0:3", "Платформа (Psys / SoC)", "name: \"psys\"\nenergy_uj\n(повне живлення материнки)", "#fadbd8", "#c0392b")
    ]

    col_w = 185
    start_x = 48
    top_y = 210

    for i, (slug_name, title_name, details, bg, st_col) in enumerate(subzones):
        cx = start_x + i * (col_w + 14)
        # Header
        frags.append(rect(cx, top_y, col_w, 36, fill=st_col, stroke=st_col, rx=5))
        frags.append(text(cx + col_w/2, top_y + 16, slug_name, size=11, bold=True, color="#ffffff"))
        frags.append(text(cx + col_w/2, top_y + 30, title_name, size=9.5, color="#f4f6f7"))

        # Details body
        frags.append(rect(cx, top_y + 40, col_w, 180, fill=bg, stroke=st_col, rx=5))
        lines = details.split("\n")
        for j, line_txt in enumerate(lines):
            frags.append(text(cx + col_w/2, top_y + 65 + j * 24, line_txt, size=10, color="#2c3e50"))

    # Connect root to Package
    frags.append(arrow(435, 96, 435, 125, color="#2980b9", sw=1.8))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    render(os.path.join(out_dir, "powercap-sysfs-hierarchy.svg"), w, h, *frags, title="Ієрархія зон powercap у sysfs")

def draw_powercap_kernel_architecture():
    w, h = 860, 500
    frags = []

    frags.append(rect(15, 15, 830, 470, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    frags.append(text(430, 42, "Архітектура підсистеми Power Capping у ядрі Linux", size=14, bold=True, color="#2c3e50"))

    # Layers
    # Layer 1: Userspace
    frags.append(rect(30, 65, 800, 85, fill="#f8f9fa", stroke="#7f8c8d", sw=1.5, rx=6))
    frags.append(text(45, 85, "Простір користувача (Userspace)", size=11, bold=True, color="#7f8c8d", anchor="start"))

    bx_u1, _, _ = textbox(150, 115, "Утиліта turbostat\n(читання MSR/sysfs)", size=10, bold=True, fill="#ffffff", stroke="#7f8c8d")
    frags.append(bx_u1)
    bx_u2, _, _ = textbox(340, 115, "Пакет powercap-utils\n(powercap-info/set)", size=10, bold=True, fill="#ffffff", stroke="#7f8c8d")
    frags.append(bx_u2)
    bx_u3, _, _ = textbox(530, 115, "Демони енергопрофілів\n(power-profiles-daemon)", size=10, bold=True, fill="#ffffff", stroke="#7f8c8d")
    frags.append(bx_u3)
    bx_u4, _, _ = textbox(720, 115, "Підсистема perf\n(power/energy-pkg/)", size=10, bold=True, fill="#ffffff", stroke="#7f8c8d")
    frags.append(bx_u4)

    # Layer 2: Kernel Space
    frags.append(rect(30, 165, 800, 185, fill="#eaf2f8", stroke="#2980b9", sw=1.5, rx=6))
    frags.append(text(45, 185, "Простір ядра Linux (Power Capping Framework)", size=11, bold=True, color="#2980b9", anchor="start"))

    bx_k_sysfs, _, _ = textbox(430, 215, "Інтерфейс sysfs: /sys/class/powercap/ (powercap_sys.c)\nУправління зонами powercap_zone та обмеженнями powercap_constraint", size=10.5, bold=True, fill="#ffffff", stroke="#2980b9")
    frags.append(bx_k_sysfs)

    # Backends
    bx_b1, _, _ = textbox(170, 295, "intel_rapl_common.c\nЗагальна логіка доменів", size=10, bold=True, fill="#d4efdf", stroke="#27ae60")
    frags.append(bx_b1)
    bx_b2, _, _ = textbox(380, 295, "intel_rapl_msr.c\nДоступ через MSR 0x606/0x610", size=10, bold=True, fill="#d4efdf", stroke="#27ae60")
    frags.append(bx_b2)
    bx_b3, _, _ = textbox(580, 295, "intel_rapl_tpmi.c\nІнтерфейс TPMI (Xeon MMIO)", size=10, bold=True, fill="#d4efdf", stroke="#27ae60")
    frags.append(bx_b3)
    bx_b4, _, _ = textbox(740, 295, "amd_energy.c\nZen RAPL MSR", size=10, bold=True, fill="#d4efdf", stroke="#27ae60")
    frags.append(bx_b4)

    # Layer 3: Hardware
    frags.append(rect(30, 365, 800, 105, fill="#fdf2e9", stroke="#d35400", sw=1.5, rx=6))
    frags.append(text(45, 385, "Апаратний рівень (CPU Hardware / Microcode)", size=11, bold=True, color="#d35400", anchor="start"))

    bx_hw1, _, _ = textbox(220, 425, "MSR Регістри керування\nMSR_PKG_POWER_LIMIT (0x610)\nMSR_PKG_ENERGY_STATUS (0x611)", size=9.5, bold=True, fill="#ffffff", stroke="#d35400")
    frags.append(bx_hw1)

    bx_hw2, _, _ = textbox(580, 425, "Power Control Unit (PCU) / SMU\nЗамкнений контур регулювання: DVFS, T-states, Clock Gating, Throttling", size=9.5, bold=True, fill="#ffffff", stroke="#d35400")
    frags.append(bx_hw2)

    # Arrows
    frags.append(arrow(430, 140, 430, 195, color="#2980b9", sw=1.8))
    frags.append(arrow(340, 235, 170, 275, color="#27ae60", sw=1.5))
    frags.append(arrow(410, 235, 380, 275, color="#27ae60", sw=1.5))
    frags.append(arrow(470, 235, 580, 275, color="#27ae60", sw=1.5))
    frags.append(arrow(520, 235, 740, 275, color="#27ae60", sw=1.5))

    frags.append(arrow(380, 318, 220, 395, color="#d35400", sw=1.8))
    frags.append(arrow(380, 425, 460, 425, color="#d35400", sw=1.8))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    render(os.path.join(out_dir, "powercap-kernel-architecture.svg"), w, h, *frags, title="Архітектура ядра powercap")

def draw_platypus_side_channel():
    w, h = 860, 470
    frags = []

    frags.append(rect(15, 15, 830, 440, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    frags.append(text(430, 42, "Схема витоку даних Platypus через RAPL та бар'єри безпеки ядра", size=14, bold=True, color="#2c3e50"))

    # Left: Victim Domain / Target computation
    frags.append(rect(35, 70, 360, 360, fill="#fdf2e9", stroke="#e74c3c", sw=1.5, rx=6))
    frags.append(text(215, 95, "Жертва: Захищене середовище", size=12, bold=True, color="#c0392b"))

    bx_sgx, _, _ = textbox(215, 140, "Intel SGX Enclave / Ядро Linux / TLS\nВиконання криптографічних операцій\n(AES-NI, RSA, вибірка ключів)", size=10, bold=True, fill="#ffffff", stroke="#e74c3c")
    frags.append(bx_sgx)

    bx_hw, _, _ = textbox(215, 240, "Апаратна фізика КМОН-транзисторів:\nДинамічна енергія залежить від\nваги Хеммінга операндів (HW(Data))\nБіт '1' споживає більше заряду, ніж '0'", size=10, bold=True, fill="#fadbd8", stroke="#c0392b")
    frags.append(bx_hw)

    bx_counter, _, _ = textbox(215, 360, "Апаратний лічильник RAPL\nMSR_PKG_ENERGY_STATUS (0x611)\nОновлення ~1000 разів на секунду", size=10, bold=True, fill="#ffffff", stroke="#e74c3c")
    frags.append(bx_counter)

    frags.append(arrow(215, 175, 215, 205, color="#c0392b", sw=1.5))
    frags.append(arrow(215, 285, 215, 335, color="#c0392b", sw=1.5))

    # Right: Attacker & Defenses
    frags.append(rect(435, 70, 390, 360, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=6))
    frags.append(text(630, 95, "Атака Platypus та захист ядра", size=12, bold=True, color="#1b4f72"))

    bx_atk, _, _ = textbox(630, 145, "Непривілейований процес зловмисника\nВисокочастотний вимір енергії (20 кГц)\nВідновлення приватного ключа біт за бітом", size=10, bold=True, fill="#ffffff", stroke="#e74c3c")
    frags.append(bx_atk)

    bx_def1, _, _ = textbox(630, 245, "Захист ядра Linux (CVE-2020-8694):\nПрава доступу /sys/class/powercap/.../energy_uj\nзмінено з 0444 (world) на 0400 (root-only)\nCAP_SYS_RAWIO для читання MSR", size=10, bold=True, fill="#d4efdf", stroke="#27ae60")
    frags.append(bx_def1)

    bx_def2, _, _ = textbox(630, 360, "Апаратний захист (Оновлення мікрокоду):\nДодавання шуму та фільтрація\nчастоти оновлення MSR лічильників", size=10, bold=True, fill="#e8f8f5", stroke="#16a085")
    frags.append(bx_def2)

    # Cross arrow
    frags.append(arrow(345, 360, 485, 170, color="#c0392b", sw=2))
    frags.append(text(415, 250, "Витік", size=11, bold=True, color="#c0392b"))

    out_dir = os.path.join(os.path.dirname(__file__), "img")
    render(os.path.join(out_dir, "platypus-side-channel.svg"), w, h, *frags, title="Схема витоку Platypus та захист ядра")

if __name__ == "__main__":
    draw_rapl_sliding_window()
    draw_powercap_sysfs_hierarchy()
    draw_powercap_kernel_architecture()
    draw_platypus_side_channel()
    print("All powercap SVG figures generated successfully.")
