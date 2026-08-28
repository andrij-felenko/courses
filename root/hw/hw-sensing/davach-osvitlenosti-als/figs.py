# -*- coding: utf-8 -*-
"""Фігури до теми «Давач освітленості (ALS)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# ── Допоміжні кольори ────────────────────────────────────────────────────────
COLOR_IR = "#b91c1c"      # Глибокий червоний / ІЧ
COLOR_VIS = "#15803d"     # Зелений / видиме світло V(lambda)
COLOR_SI = "#4b5563"      # Сірий / кремній
COLOR_CH0 = "#2563eb"     # Синій / канал CH0
COLOR_CH1 = "#d97706"     # Помаранчевий / канал CH1
LIGHT_BG = "#f8fafc"
PANEL_BG = "#f1f5f9"


# ── 1. Спектральна чутливість кремнію vs крива V(λ) ──────────────────────────
def fig_spectral_response():
    W, H = 760, 420
    f = []

    # Рамка графіка
    ox, oy = 75, 340
    gw, gh = 635, 260
    right = ox + gw
    top = oy - gh

    # Підкладка сітки
    f.append(rect(ox, top, gw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1))

    def wl_to_x(wl):
        return ox + (wl - 350) / (1150 - 350) * gw

    x_vis_start = wl_to_x(380)
    x_vis_end = wl_to_x(750)
    x_ir_end = wl_to_x(1100)

    # Верхні індикаторні смуги спектральних зон
    f.append(line(x_vis_start, top + 15, x_vis_end, top + 15, color="#16a34a", sw=3))
    f.append(text((x_vis_start + x_vis_end)/2, top + 30, "Видиме світло (380–750 нм)", size=10.5, color="#15803d", bold=True))

    f.append(line(x_vis_end, top + 15, x_ir_end, top + 15, color="#dc2626", sw=3))
    f.append(text((x_vis_end + x_ir_end)/2, top + 30, "Ближнє ІЧ (750–1100 нм)", size=10.5, color="#b91c1c", bold=True))

    # Вертикальні лінії довжин хвиль: 380, 555, 750, 900, 1100 нм
    wl_points = [
        (380, "380 нм", "#94a3b8"),
        (555, "555 нм", "#16a34a"),
        (750, "750 нм", "#dc2626"),
        (900, "900 нм", "#64748b"),
        (1100, "1100 нм", "#94a3b8")
    ]

    for wl, label, col in wl_points:
        x = wl_to_x(wl)
        f.append(line(x, top + 40, x, oy, color=col, sw=1, dash="3,3"))
        f.append(text(x, oy + 16, label, size=10, color=INK, bold=True))

    # Горизонтальні рівні відгуку (0, 0.5, 1.0)
    for level, label in [(0.0, "0.0"), (0.5, "0.5"), (1.0, "1.0")]:
        y = oy - level * (gh - 60)
        f.append(line(ox, y, right, y, color="#e2e8f0", sw=1))
        f.append(text(ox - 8, y + 4, label, size=10, color=MUTED, anchor="end"))

    # Осі координат
    f.append(line(ox, oy, right, oy, color=INK, sw=1.5))
    f.append(line(ox, oy, ox, top, color=INK, sw=1.5))
    f.append(text(right, oy + 32, "Довжина хвилі λ (нм)", size=11, anchor="end", bold=True))
    f.append(text(ox - 6, top - 8, "Відносна чутливість S(λ)", size=11, anchor="start", bold=True))

    # 1. Крива кремнію Si (підйом від 400 до піку 900 нм, спад до 1100 нм)
    pts_si = []
    for wl in range(360, 1150, 15):
        if wl < 400:
            val = 0.05 * (wl - 350) / 50
        elif wl <= 900:
            val = 0.05 + 0.95 * ((wl - 400) / 500) ** 0.9
        elif wl <= 1100:
            val = 1.0 - ((wl - 900) / 200) ** 1.3
        else:
            val = 0.0
        val = max(0.0, min(1.0, val))
        x = wl_to_x(wl)
        y = oy - val * (gh - 60)
        pts_si.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_si)}" fill="none" stroke="{COLOR_SI}" stroke-width="2.4" stroke-dasharray="4,3"/>')

    # 2. Фотопічна крива V(λ) (гаусоїда з центром 555 нм, сигма ~ 48 нм)
    pts_v = []
    for wl in range(380, 760, 10):
        val = math.exp(-0.5 * ((wl - 555) / 48) ** 2)
        x = wl_to_x(wl)
        y = oy - val * (gh - 60)
        pts_v.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_v)}" fill="none" stroke="{COLOR_VIS}" stroke-width="3.2"/>')

    # 3. Крива каналу CH1 (IR-канал, фільтр від 700 до 1050 нм)
    pts_ch1 = []
    for wl in range(700, 1120, 15):
        if wl < 720:
            val = 0.1 * (wl - 700) / 20
        elif wl <= 880:
            val = 0.1 + 0.65 * ((wl - 720) / 160)
        elif wl <= 1080:
            val = 0.75 * (1.0 - (wl - 880) / 200)
        else:
            val = 0.0
        val = max(0.0, val)
        x = wl_to_x(wl)
        y = oy - val * (gh - 60)
        pts_ch1.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_ch1)}" fill="none" stroke="{COLOR_CH1}" stroke-width="2.2" stroke-dasharray="6,2"/>')

    # Легенда (без важкого суцільного rect, чисті написи)
    lx = right - 280
    ly = top + 55
    f.append(line(lx, ly, lx + 30, ly, color=COLOR_VIS, sw=3.2))
    f.append(text(lx + 38, ly + 4, "Людське око V(λ) — цільова реакція", size=10, color=COLOR_VIS, anchor="start", bold=True))

    f.append(line(lx, ly + 22, lx + 30, ly + 22, color=COLOR_SI, sw=2.4, dash="4,3"))
    f.append(text(lx + 38, ly + 26, "Голий кремній (Si) — сильна ІЧ-помилка", size=10, color=COLOR_SI, anchor="start"))

    f.append(line(lx, ly + 44, lx + 30, ly + 44, color=COLOR_CH1, sw=2.2, dash="6,2"))
    f.append(text(lx + 38, ly + 48, "ІЧ-канал ALS (CH1) — для віднімання", size=10, color=COLOR_CH1, anchor="start"))

    return render(os.path.join(IMG, "fig-als-spectral-response.svg"), W, H, *f)


# ── 2. Внутрішня архітектура інтегрального ALS ─────────────────────────────────
def fig_internal_architecture():
    W, H = 780, 460
    f = []

    # Загальний корпус мікросхеми IC
    f.append(rect(15, 20, 750, 420, fill="#ffffff", stroke=LINE, sw=2, rx=8))
    f.append(text(390, 44, "Архітектура інтегрального цифрового давача освітленості (ALS IC)", size=14, bold=True))

    # 1. Оптичний блок (зліва)
    f.append(rect(35, 65, 175, 355, fill=PANEL_BG, stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(122, 90, "Оптичний фронтенд", size=12, bold=True, color="#1e293b"))

    # Фотодіод CH0
    f.append(rect(48, 110, 150, 80, fill="#ffffff", stroke=COLOR_CH0, sw=1.8, rx=4))
    f.append(text(123, 130, "Канал CH0 (Visible+IR)", size=10.5, bold=True, color=COLOR_CH0))
    f.append(text(123, 148, "Фотодіод + фільтр V(λ)", size=9.5, color=MUTED))
    f.append(text(123, 165, "I_ph0 = f(E_vis + E_ir)", size=9.5, bold=True))

    # Фотодіод CH1
    f.append(rect(48, 205, 150, 80, fill="#ffffff", stroke=COLOR_CH1, sw=1.8, rx=4))
    f.append(text(123, 225, "Канал CH1 (IR Reference)", size=10.5, bold=True, color=COLOR_CH1))
    f.append(text(123, 243, "Фотодіод + ІЧ-фільтр", size=9.5, color=MUTED))
    f.append(text(123, 260, "I_ph1 = f(E_ir)", size=9.5, bold=True))

    # Темновий компенсаційний фотодіод
    f.append(rect(48, 300, 150, 65, fill="#f8fafc", stroke="#64748b", sw=1.4, rx=4))
    f.append(text(123, 320, "Темновий діод (Dark)", size=10, bold=True, color="#475569"))
    f.append(text(123, 337, "Затемнений екран (метал)", size=9, color=MUTED))
    f.append(text(123, 352, "Компенсація I_dark(T)", size=9, color=MUTED))

    # 2. Аналоговий тракт: MUX + TIA/PGA + Integrator
    f.append(rect(230, 65, 185, 355, fill=PANEL_BG, stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(322, 90, "Аналоговий тракт", size=12, bold=True, color="#1e293b"))

    # MUX
    f.append(rect(245, 125, 45, 180, fill="#ffffff", stroke=LINE, sw=1.4, rx=4))
    f.append(text(267, 218, "M\nU\nX", size=11, bold=True, color="#334155"))

    # З'єднання від діодів до MUX
    f.append(arrow(198, 150, 245, 150, color=COLOR_CH0, sw=1.6))
    f.append(arrow(198, 245, 245, 245, color=COLOR_CH1, sw=1.6))
    f.append(arrow(198, 332, 245, 285, color="#64748b", sw=1.4))

    # PGA / Інтегратор заряду
    f.append(rect(305, 145, 95, 140, fill="#ffffff", stroke="#0284c7", sw=1.6, rx=4))
    f.append(text(352, 170, "PGA Gain", size=11, bold=True, color="#0284c7"))
    f.append(text(352, 190, "1x ... 128x", size=10, color=MUTED))
    f.append(line(315, 205, 390, 205, color="#cbd5e1", sw=1))
    f.append(text(352, 225, "Інтегратор", size=10.5, bold=True, color="#0369a1"))
    f.append(text(352, 245, "заряду Q = ∫I dt", size=9.5, color=MUTED))
    f.append(text(352, 265, "T_int регульований", size=9, color=MUTED))

    f.append(arrow(290, 215, 305, 215, color=LINE, sw=1.6))

    # 3. АЦП та цифровий блок обробки
    f.append(rect(435, 65, 165, 355, fill=PANEL_BG, stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(517, 90, "АЦП та цифрова FSM", size=12, bold=True, color="#1e293b"))

    # Блок ADC
    f.append(rect(450, 115, 135, 75, fill="#ffffff", stroke="#7c3aed", sw=1.6, rx=4))
    f.append(text(517, 138, "16-біт / 24-біт АЦП", size=11, bold=True, color="#7c3aed"))
    f.append(text(517, 156, "Σ-Δ або Dual-Slope", size=9.5, color=MUTED))
    f.append(text(517, 173, "Висока лінійність", size=9, color=MUTED))

    f.append(arrow(400, 215, 450, 152, color=LINE, sw=1.6))

    # Блок цифрової корекції та Flicker Engine
    f.append(rect(450, 210, 135, 110, fill="#ffffff", stroke="#059669", sw=1.6, rx=4))
    f.append(text(517, 233, "Digital DSP Engine", size=10.5, bold=True, color="#059669"))
    f.append(text(517, 252, "• Auto-Range FSM", size=9.5, color=INK))
    f.append(text(517, 270, "• Flicker (100/120Hz)", size=9.5, color=INK))
    f.append(text(517, 288, "• E_v = a·CH0 - b·CH1", size=9, bold=True, color="#047857"))
    f.append(text(517, 305, "• Корекція скла K_g", size=9, color=MUTED))

    f.append(arrow(517, 190, 517, 210, color=LINE, sw=1.6))

    # 4. Інтерфейс шини (справа)
    f.append(rect(620, 65, 130, 355, fill=PANEL_BG, stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(685, 90, "Шина I2C / INT", size=12, bold=True, color="#1e293b"))

    # Регістри
    f.append(rect(632, 115, 106, 120, fill="#ffffff", stroke=LINE, sw=1.4, rx=4))
    f.append(text(685, 135, "Регістри", size=10.5, bold=True))
    f.append(text(685, 155, "CONFIG", size=9, color=MUTED))
    f.append(text(685, 172, "DATA_CH0", size=9, color=MUTED))
    f.append(text(685, 189, "DATA_CH1", size=9, color=MUTED))
    f.append(text(685, 206, "THRESHOLD", size=9, color=MUTED))
    f.append(text(685, 223, "STATUS / INT", size=9, color=MUTED))

    f.append(arrow(585, 265, 632, 175, color=LINE, sw=1.6))

    # Виводи мікросхеми
    pins = [
        (280, "SDA (Дані I2C)"),
        (320, "SCL (Тактування)"),
        (360, "INT (Переривання)"),
        (400, "VDD / GND")
    ]
    for py, plabel in pins:
        f.append(line(738, py, 755, py, color="#b91c1c", sw=2.5))
        f.append(text(685, py + 4, plabel, size=9.5, bold=True, color="#334155"))

    return render(os.path.join(IMG, "fig-als-internal-architecture.svg"), W, H, *f)


# ── 3. Двоканальна компенсація ІЧ-завади ──────────────────────────────────────
def fig_dual_channel_compensation():
    W, H = 760, 420
    f = []

    # Заголовок
    f.append(text(380, 26, "Матрична компенсація ІЧ-завади для джерел з різною колірною температурою", size=13, bold=True))

    # Три джерела світла: LED, Лампа розжарювання, Сонце
    sources = [
        {
            "x": 30, "title": "1. Білий LED (Холодний)", "temp": "T = 6500 K",
            "spec": "Суто видиме світло (420–680 нм), ІЧ-складова майже нульова.",
            "ch0": 100, "ch1": 2, "lux_calc": "E_v = 1.0·100 - 1.8·2 ≈ 96.4 лк",
            "ch0_val": "CH0 = 100", "ch1_val": "CH1 = 2 (ІЧ ≈ 0)"
        },
        {
            "x": 270, "title": "2. Лампа розжарювання", "temp": "T = 2700 K",
            "spec": "90% енергії в ІЧ-діапазоні (750–2000 нм), слабке синє світло.",
            "ch0": 450, "ch1": 195, "lux_calc": "E_v = 1.0·450 - 1.8·195 ≈ 99.0 лк",
            "ch0_val": "CH0 = 450 (величезна ІЧ)", "ch1_val": "CH1 = 195 (високий ІЧ)"
        },
        {
            "x": 510, "title": "3. Пряме сонячне світло", "temp": "T = 5800 K (AM1.5)",
            "spec": "Потужний неперервний спектр: видиме світло + потужне ІЧ.",
            "ch0": 1000, "ch1": 420, "lux_calc": "E_v = 1.0·1000 - 1.8·420 ≈ 244 лк*",
            "ch0_val": "CH0 = 1000", "ch1_val": "CH1 = 420"
        }
    ]

    for s in sources:
        sx = s["x"]
        f.append(rect(sx, 48, 220, 295, fill=PANEL_BG, stroke="#cbd5e1", sw=1.5, rx=6))
        f.append(text(sx + 110, 72, s["title"], size=11.5, bold=True, color="#0f172a"))
        f.append(text(sx + 110, 90, s["temp"], size=10, color=MUTED, italic=True))
        
        # Опис спектра
        f.append(fitbox(sx + 8, 102, 204, 46, s["spec"], size=9.5, fill="#ffffff", stroke="#e2e8f0"))

        # Відгук каналів
        f.append(rect(sx + 8, 156, 204, 78, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
        f.append(text(sx + 110, 174, "Відгук каналів ALS:", size=10, bold=True, color="#334155"))
        f.append(text(sx + 16, 194, s["ch0_val"], size=9.5, bold=True, color=COLOR_CH0, anchor="start"))
        f.append(text(sx + 16, 214, s["ch1_val"], size=9.5, bold=True, color=COLOR_CH1, anchor="start"))

        # Обчислення
        f.append(rect(sx + 8, 242, 204, 48, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=4))
        f.append(text(sx + 110, 258, "Результат після корекції:", size=9.5, bold=True, color="#15803d"))
        f.append(text(sx + 110, 276, s["lux_calc"], size=9, bold=True, color="#166534"))

    # Нижній блок формули
    f.append(rect(30, 352, 700, 56, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    f.append(text(380, 372, "Загальне матричне рівняння відсікання: E_v = a · CH0 − b · CH1", size=12, bold=True, color="#1e40af"))
    f.append(text(380, 393, "Коефіцієнти a та b калібруються за відношенням Ratio = CH1 / CH0 для різних джерел світла", size=10, color="#1e3a8a"))

    return render(os.path.join(IMG, "fig-dual-channel-compensation.svg"), W, H, *f)


# ── 4. Динамічний діапазон: PGA Gain та Integration Time ─────────────────────
def fig_dynamic_range():
    W, H = 760, 400
    f = []

    f.append(text(380, 25, "Охоплення динамічного діапазону 100+ dB: перемикання PGA Gain та T_int", size=13, bold=True))

    # Стовпчики діапазонів (від темряви до сонця)
    ranges = [
        {
            "name": "Глибока темрява",
            "lux": "0.01 – 1 лк",
            "env": "Ніч, зоряне небо,\nкінозал",
            "gain": "Gain: 128x (Max)",
            "tint": "T_int: 800 мс",
            "lsb": "LSB: 0.0014 лк",
            "color": "#1e1b4b", "bg": "#e0e7ff"
        },
        {
            "name": "Сутінки / Кімната",
            "lux": "1 – 100 лк",
            "env": "Житлова кімната,\nвечірнє світло",
            "gain": "Gain: 16x ... 32x",
            "tint": "T_int: 400 мс",
            "lsb": "LSB: 0.012 лк",
            "color": "#1e3a8a", "bg": "#dbeafe"
        },
        {
            "name": "Офісне освітлення",
            "lux": "100 – 1 000 лк",
            "env": "Офіс, лабораторія,\nпасмурний день",
            "gain": "Gain: 4x ... 8x",
            "tint": "T_int: 100 мс",
            "lsb": "LSB: 0.096 лк",
            "color": "#065f46", "bg": "#d1fae5"
        },
        {
            "name": "Денне світло",
            "lux": "1 000 – 15 000 лк",
            "env": "Тінь на вулиці,\nвікно вдень",
            "gain": "Gain: 1x ... 2x",
            "tint": "T_int: 50 мс",
            "lsb": "LSB: 0.77 лк",
            "color": "#b45309", "bg": "#fef3c7"
        },
        {
            "name": "Пряме сонце",
            "lux": "15 000 – 120 000 лк",
            "env": "Пряме сонце в полудень,\nснігове поле",
            "gain": "Gain: 1/4x (Min)",
            "tint": "T_int: 12.5 мс",
            "lsb": "LSB: 6.14 лк",
            "color": "#991b1b", "bg": "#fee2e2"
        }
    ]

    col_w = 136
    gap = 10
    start_x = 20

    for i, r in enumerate(ranges):
        cx = start_x + i * (col_w + gap)
        f.append(rect(cx, 48, col_w, 280, fill=r["bg"], stroke=r["color"], sw=1.5, rx=6))
        
        f.append(text(cx + col_w/2, 70, r["name"], size=11, bold=True, color=r["color"]))
        f.append(text(cx + col_w/2, 90, r["lux"], size=10.5, bold=True, color="#0f172a"))

        # Опис оточення
        f.append(fitbox(cx + 6, 102, col_w - 12, 44, r["env"], size=9.5, fill="#ffffff", stroke="#cbd5e1"))

        # Параметри конфігурації
        f.append(rect(cx + 6, 154, col_w - 12, 114, fill="#ffffff", stroke=r["color"], sw=1, rx=4))
        f.append(text(cx + col_w/2, 172, "Налаштування:", size=9.5, bold=True, color="#334155"))
        f.append(text(cx + col_w/2, 192, r["gain"], size=9.5, bold=True, color=r["color"]))
        f.append(text(cx + col_w/2, 212, r["tint"], size=9.5, bold=True, color="#0369a1"))
        f.append(line(cx + 12, 226, cx + col_w - 12, 226, color="#e2e8f0", sw=1))
        f.append(text(cx + col_w/2, 244, r["lsb"], size=9.5, bold=True, color="#475569"))
        f.append(text(cx + col_w/2, 258, "(крок шкали)", size=9, color=MUTED))

    # Стрілка динамічного діапазону внизу
    f.append(arrow(30, 355, 730, 355, color="#1e293b", sw=2.5))
    f.append(text(380, 375, "Динамічний діапазон ALS: від 0.001 лк до 120 000 лк (понад 160 dB еквівалентно)", size=11, bold=True))
    f.append(text(40, 342, "0.01 лк", size=9.5, bold=True, color="#1e1b4b", anchor="start"))
    f.append(text(720, 342, "120 000 лк", size=9.5, bold=True, color="#991b1b", anchor="end"))

    return render(os.path.join(IMG, "fig-dynamic-range-pga-tint.svg"), W, H, *f)


# ── 5. Мерехтіння штучного освітлення (Flicker 100/120 Hz) ────────────────────
def fig_flicker_integration():
    W, H = 760, 420
    f = []

    f.append(text(380, 24, "Придушення мерехтіння 100/120 Гц вибором часу інтегрування T_int", size=13, bold=True))

    # Лівий графік: часова форма сигналу та вікно інтегрування
    lx, ly = 40, 60
    lw, lh = 330, 260
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(lx + lw/2, ly + 20, "Часова область: пульсація 100 Гц (T = 10 мс)", size=10.5, bold=True, color="#1e293b"))

    # Синусоїда пульсації світла 100 Гц
    pts_sin = []
    for px in range(20, 300, 4):
        val = 140 + 35 * math.sin(2 * math.pi * (px - 20) / 50)
        pts_sin.append(f"{lx + px:.1f},{ly + val:.1f}")
    f.append(f'<polyline points="{" ".join(pts_sin)}" fill="none" stroke="#d97706" stroke-width="2"/>')

    # Написи до синусоїди
    f.append(text(lx + 165, ly + 50, "Миттєвий фотострум з пульсацією 100 Гц", size=9.5, color="#d97706", bold=True))

    # Вікно T_int = 100 мс
    f.append(line(lx + 30, ly + 195, lx + 280, ly + 195, color="#16a34a", sw=2))
    f.append(text(lx + 155, ly + 215, "Вікно T_int = 100 мс (10 повних періодів)", size=9.5, bold=True, color="#15803d"))
    f.append(text(lx + 155, ly + 230, "Інтеграл заряду Q = const (0% ripple)", size=9.5, color="#166534"))

    # Коротке випадкове вікно
    f.append(line(lx + 30, ly + 90, lx + 95, ly + 90, color="#dc2626", sw=2))
    f.append(text(lx + 62, ly + 80, "T_int = 13 мс", size=9.5, bold=True, color="#b91c1c"))
    f.append(text(lx + 62, ly + 105, "Похибка ±30%", size=9, color="#991b1b"))

    # Правий графік: АЧХ фільтра інтегрування |sinc(π f T_int)|
    rx, ry = 390, 60
    rw, rh = 330, 260
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(rx + rw/2, ry + 20, "Частотна характеристика |sinc(π · f · T_int)|", size=10.5, bold=True, color="#1e293b"))

    # Осі АЧХ
    a_ox, a_oy = rx + 35, ry + 220
    f.append(line(a_ox, a_oy, rx + rw - 15, a_oy, color=INK, sw=1.2))
    f.append(line(a_ox, a_oy, a_ox, ry + 40, color=INK, sw=1.2))
    f.append(text(rx + rw - 15, a_oy + 16, "Частота f (Гц)", size=9.5, anchor="end", bold=True))
    f.append(text(a_ox - 6, ry + 46, "|H(f)|", size=9.5, anchor="end", bold=True))

    # Точки частоти 0, 50, 100, 150, 200 Гц
    pts_sinc = []
    for f_hz in range(1, 220, 2):
        x = a_ox + (f_hz / 220) * 260
        arg = math.pi * f_hz * 0.02
        val = abs(math.sin(arg) / arg) if arg != 0 else 1.0
        y = a_oy - val * 160
        pts_sinc.append(f"{x:.1f},{y:.1f}")
    f.append(f'<polyline points="{" ".join(pts_sinc)}" fill="none" stroke="#2563eb" stroke-width="2.2"/>')

    # Нулі на 50 Гц, 100 Гц, 150 Гц
    for f_hz, flabel in [(50, "50 Гц"), (100, "100 Гц"), (150, "150 Гц")]:
        x = a_ox + (f_hz / 220) * 260
        f.append(line(x, a_oy, x, a_oy - 165, color="#94a3b8", sw=1, dash="2,2"))
        f.append(circle(x, a_oy, 3.5, fill="#dc2626", stroke="#dc2626", sw=1))
        f.append(text(x, a_oy + 14, flabel, size=9.5, bold=True, color="#1e293b"))

    f.append(text(a_ox + 130, ry + 90, "Глибокі нулі придушення", size=9.5, bold=True, color="#dc2626"))
    f.append(text(a_ox + 130, ry + 106, "на частотах 50/100/120 Гц", size=9, color="#991b1b"))

    # Нижній пояснювальний блок
    f.append(rect(40, 335, 680, 65, fill=PANEL_BG, stroke="#cbd5e1", sw=1.5, rx=6))
    f.append(text(380, 355, "Правило антифлікеру: T_int має бути кратним періоду пульсацій 100 Гц / 120 Гц", size=11, bold=True, color="#0f172a"))
    f.append(text(380, 375, "T_int = 100 мс містить 10 періодів 100 Гц (мережа 50 Гц) та 12 періодів 120 Гц (мережа 60 Гц) → придушення > 60 dB", size=9.5, color="#334155"))

    return render(os.path.join(IMG, "fig-flicker-and-integration.svg"), W, H, *f)


# ── 6. Оптична інтеграція під захисне скло або дисплей ───────────────────────
def fig_glass_attenuation():
    W, H = 760, 430
    f = []

    f.append(text(380, 24, "Оптичний стек: затухання у склі, кут зору (FOV) та паразитна перехресна завада", size=13, bold=True))

    # Скло (верхній шар)
    f.append(rect(60, 55, 640, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.8, rx=4))
    f.append(text(380, 75, "Захисне скло / Екран (Gorilla Glass, тонування T_glass = 5% ... 15%)", size=11.5, bold=True, color="#0369a1"))
    f.append(text(380, 92, "Коефіцієнт корекції скла: K_glass = 1 / T_glass (наприклад, 1 / 0.10 = 10.0x)", size=9.5, color="#075985"))

    # Чорна рамка (bezel / ink aperture)
    f.append(rect(60, 100, 230, 20, fill="#1e293b", stroke=LINE, sw=1))
    f.append(rect(470, 100, 230, 20, fill="#1e293b", stroke=LINE, sw=1))
    f.append(text(175, 114, "Чорне маскувальне чорнило", size=9.5, color="#ffffff", bold=True))
    f.append(text(585, 114, "Чорне маскувальне чорнило", size=9.5, color="#ffffff", bold=True))

    # Оптична апертура (отвір у чорнилі)
    f.append(text(380, 115, "Оптична апертура (Aperture: 1.5–2.5 мм)", size=10, bold=True, color="#b45309"))

    # Повітряний зазор (Air Gap)
    f.append(rect(60, 120, 640, 130, fill="#f8fafc", stroke="#cbd5e1", sw=1.2))
    f.append(text(130, 150, "Повітряний зазор (Air Gap: 0.5–1.2 мм)", size=9.5, color=MUTED))

    # Конус огляду FOV (±45°..±55°)
    f.append('<polygon points="290,120 470,120 405,230 355,230" fill="#fef9c3" stroke="#eab308" stroke-width="1.2" opacity="0.6"/>')
    f.append(text(380, 175, "Конус прийому світла", size=10, bold=True, color="#854d0e"))
    f.append(text(380, 192, "FOV ≈ ±50°", size=9.5, bold=True, color="#a16207"))

    # Оптичний бар'єр / гумовий ущільнювач (Rubber Boot / Gasket)
    f.append(rect(310, 120, 30, 130, fill="#334155", stroke=LINE, sw=1.5))
    f.append(rect(420, 120, 30, 130, fill="#334155", stroke=LINE, sw=1.5))
    f.append(text(250, 205, "Оптичний\nбар'єр", size=9.5, bold=True, color="#1e293b"))
    f.append(text(505, 205, "Оптичний\nбар'єр", size=9.5, bold=True, color="#1e293b"))

    # Чіп ALS на платі
    f.append(rect(340, 230, 80, 20, fill="#0f172a", stroke="#38bdf8", sw=1.6, rx=3))
    f.append(text(380, 244, "ALS IC", size=10, bold=True, color="#38bdf8"))

    # Паразитне світло від сусіднього дисплея / IR LED
    f.append(rect(560, 225, 70, 25, fill="#ef4444", stroke="#b91c1c", sw=1.5, rx=3))
    f.append(text(595, 241, "OLED / LED", size=9.5, bold=True, color="#ffffff"))

    # Плата PCB (під чіпами)
    f.append(rect(60, 250, 640, 35, fill="#15803d", stroke="#14532d", sw=1.8, rx=2))
    f.append(text(150, 272, "Друкована плата (Main PCB)", size=10.5, bold=True, color="#ffffff"))

    # Промінь паразитного відбиття
    f.append(line(595, 225, 520, 65, color="#dc2626", sw=1.8, dash="4,2"))
    f.append(line(520, 65, 450, 140, color="#dc2626", sw=1.8, dash="4,2"))
    f.append(text(575, 145, "Паразитне внутрішнє відбиття\n(відсікається бар'єром)", size=9.5, bold=True, color="#b91c1c"))

    # Нижній інформаційний блок
    f.append(rect(60, 305, 640, 105, fill=PANEL_BG, stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(380, 325, "Три золоті правила механічної та оптичної інтеграції ALS:", size=11, bold=True, color="#0f172a"))
    f.append(text(380, 345, "1. Мінімальний Air Gap (< 0.8 мм): збільшення зазору звужує FOV і вимагає ширшої апертури.", size=9.5, color="#334155"))
    f.append(text(380, 365, "2. Оптичний бар'єр (Gasket): виключає засвічення від сусідніх пікселів екрана крізь товщу скла.", size=9.5, color="#334155"))
    f.append(text(380, 385, "3. Калібрування затемненого скла: чорнило сильніше пропускає ІЧ, тому формула вимагає нового зважування.", size=9.5, color="#334155"))

    return render(os.path.join(IMG, "fig-glass-attenuation-stack.svg"), W, H, *f)


def main():
    fig_spectral_response()
    fig_internal_architecture()
    fig_dual_channel_compensation()
    fig_dynamic_range()
    fig_flicker_integration()
    fig_glass_attenuation()
    print("All 6 figures generated successfully.")


if __name__ == "__main__":
    main()
