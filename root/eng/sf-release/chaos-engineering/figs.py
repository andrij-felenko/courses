# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Порівняння контрольної та експериментальної груп зі стійким станом ──
def fig_steady_state_and_blast_radius():
    W, H = 960, 480
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок зверху
    p.append(text(30, 36, "Експеримент над стійким станом: контрольна vs експериментальна група", size=14, color=INK, bold=True, anchor="start"))
    
    # Ліва колонка: Архітектура розподілу трафіку (когорти)
    arch_x, arch_y, arch_w, arch_h = 25.0, 55.0, 340.0, 400.0
    p.append(rect(arch_x, arch_y, arch_w, arch_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(arch_x + arch_w/2, arch_y + 24, "Розподіл трафіку та радіус ураження", size=12.5, color=INK, bold=True))
    
    # Вхідний трафік
    p.append(rect(arch_x + 70, arch_y + 45, 200, 38, fill="#ffffff", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(arch_x + 170, arch_y + 69, "Вхідний трафік (100%)", size=11.5, color=INK, bold=True))
    
    # Розгалуження
    p.append(arrow(arch_x + 130, arch_y + 83, arch_x + 85, arch_y + 120, color=LINE, sw=1.4))
    p.append(arrow(arch_x + 210, arch_y + 83, arch_x + 255, arch_y + 120, color=LINE, sw=1.4))
    p.append(text(arch_x + 80, arch_y + 105, "95%", size=10.5, color=MUTED, bold=True))
    p.append(text(arch_x + 260, arch_y + 105, "5% (Canary)", size=10.5, color=POS, bold=True))
    
    # Контрольна група
    ctrl_x, ctrl_y = arch_x + 20, arch_y + 125
    p.append(rect(ctrl_x, ctrl_y, 140, 110, fill="#f0fdf4", stroke="#86efac", sw=1.4, rx=6))
    p.append(text(ctrl_x + 70, ctrl_y + 22, "Контрольна група", size=11.5, color="#15803d", bold=True))
    p.append(mtext(ctrl_x + 70, ctrl_y + 46, ["Базовий пул вузлів", "Без ін'єкцій збоїв", "Еталон SLI (p99)"], size=10, color=INK, lh=1.35))
    
    # Експериментальна група
    exp_x, exp_y = arch_x + 180, arch_y + 125
    p.append(rect(exp_x, exp_y, 140, 110, fill="#fef2f2", stroke="#fca5a5", sw=1.4, rx=6))
    p.append(text(exp_x + 70, exp_y + 22, "Група ін'єкції", size=11.5, color="#b91c1c", bold=True))
    p.append(mtext(exp_x + 70, exp_y + 46, ["Обмежений радіус", "+200ms delay / loss", "Перевірка fallback"], size=10, color=INK, lh=1.35))
    
    # Блок аварійного вимикача під когортами
    p.append(rect(arch_x + 20, arch_y + 260, 300, 120, fill="#fff8e6", stroke="#d97706", sw=1.3, rx=6))
    p.append(text(arch_x + 170, arch_y + 284, "Автоматичний вимикач (Kill Switch)", size=11.5, color="#b45309", bold=True))
    p.append(mtext(arch_x + 170, arch_y + 308, [
        "1. Безперервний моніторинг SLI",
        "2. Якщо помилки > 1% або p99 > 500ms:",
        "   → Негайний Rollback правил ін'єкції",
        "3. Сторожовий таймер (Watchdog TTL)"
    ], size=10, color=INK, lh=1.35))
    
    # Права колонка: Графік метрик стійкого стану
    chart_x, chart_y, chart_w, chart_h = 385.0, 55.0, 550.0, 400.0
    p.append(rect(chart_x, chart_y, chart_w, chart_h, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(chart_x + 20, chart_y + 24, "Метрики стійкого стану (Steady State) та поріг зупинки", size=12.5, color=INK, bold=True, anchor="start"))
    
    # Осі графіка
    ox, oy, gw, gh = chart_x + 50, chart_y + 320, 460.0, 240.0
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5)) # X вісь
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5)) # Y вісь
    p.append(arrow(ox + gw - 30, oy, ox + gw, oy, color=LINE, sw=1.5))
    p.append(arrow(ox, oy - gh + 30, ox, oy - gh, color=LINE, sw=1.5))
    p.append(text(ox + gw - 5, oy + 18, "Час (t) →", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 10, oy - gh + 15, "SLI: Latency p99 / Error Rate", size=11, color=INK, bold=True, anchor="end"))
    
    # Зони на графіку
    inj_start, inj_stop = ox + 140, ox + 320
    p.append(rect(inj_start, oy - gh + 30, inj_stop - inj_start, gh - 30, fill="#fef2f2", stroke="none"))
    p.append(line(inj_start, oy, inj_start, oy - gh + 30, color="#ef4444", sw=1.2, dash="4 3"))
    p.append(line(inj_stop, oy, inj_stop, oy - gh + 30, color="#ef4444", sw=1.2, dash="4 3"))
    p.append(text(inj_start + (inj_stop - inj_start)/2, oy - gh + 45, "Вікно ін'єкції збою", size=11, color="#b91c1c", bold=True))
    
    # Поріг SLO (червона лінія)
    slo_y = oy - 180
    p.append(line(ox, slo_y, ox + gw - 20, slo_y, color="#dc2626", sw=1.4, dash="6 3"))
    p.append(text(ox + gw - 25, slo_y - 8, "Критичний поріг аварійної зупинки (SLO Breach)", size=10, color="#dc2626", bold=True, anchor="end"))
    
    # Крива стійкого стану (Контрольна група - зелена рівна лінія з легким шумом)
    ctrl_pts = [(ox, oy - 60), (ox + 70, oy - 62), (ox + 140, oy - 58), (ox + 210, oy - 63), (ox + 280, oy - 59), (ox + 350, oy - 61), (ox + 420, oy - 60)]
    for i in range(len(ctrl_pts) - 1):
        x1, y1 = ctrl_pts[i]
        x2, y2 = ctrl_pts[i+1]
        p.append(line(x1, y1, x2, y2, color="#16a34a", sw=2.2))
    p.append(text(ox + 425, oy - 60, "Контрольна група (Steady State)", size=10, color="#15803d", bold=True, anchor="start"))
    
    # Крива експериментальної групи (синя, що зростає під час ін'єкції, але лишається нижче порогу)
    exp_pts = [(ox, oy - 55), (ox + 70, oy - 57), (ox + 140, oy - 55), (ox + 180, oy - 120), (ox + 250, oy - 140), (ox + 320, oy - 135), (ox + 350, oy - 70), (ox + 420, oy - 56)]
    for i in range(len(exp_pts) - 1):
        x1, y1 = exp_pts[i]
        x2, y2 = exp_pts[i+1]
        p.append(line(x1, y1, x2, y2, color="#2563eb", sw=2.2))
    p.append(text(ox + 250, oy - 150, "Експеримент: деградація в межах норми", size=10, color="#1d4ed8", bold=True))
    
    # Нижня панель легенди
    leg_y = chart_y + 345
    p.append(rect(chart_x + 20, leg_y, chart_w - 40, 45, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
    p.append(circle(chart_x + 35, leg_y + 22, 5, fill="#16a34a", stroke="#16a34a", sw=1))
    p.append(text(chart_x + 48, leg_y + 26, "Стійкий стан (Baseline)", size=10.5, color=INK, anchor="start"))
    p.append(circle(chart_x + 200, leg_y + 22, 5, fill="#2563eb", stroke="#2563eb", sw=1))
    p.append(text(chart_x + 213, leg_y + 26, "Поведінка під навантаженням", size=10.5, color=INK, anchor="start"))
    p.append(line(chart_x + 380, leg_y + 22, chart_x + 405, leg_y + 22, color="#dc2626", sw=1.8, dash="4 2"))
    p.append(text(chart_x + 412, leg_y + 26, "SLO Rollback Trigger", size=10.5, color="#dc2626", bold=True, anchor="start"))
    
    render(os.path.join(OUT, "steady-state-and-blast-radius.svg"), W, H, *p)

# ── Фіг. 2: Архітектурні рівні ін'єкції збоїв ──────────────────────────────────
def fig_fault_injection_layers():
    W, H = 960, 490
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(30, 36, "Архітектурні рівні ін'єкції збоїв: від заліза до коду застосунку", size=14, color=INK, bold=True, anchor="start"))
    
    layers = [
        ("Рівень 5: Застосунок і RPC", "Chaos Middleware / Interceptors", "Ін'єкція винятків, затримка методів, підміна відповідей кешу, chaos headers", "#eef2ff", "#4f46e5"),
        ("Рівень 4: Service Mesh & Проксі", "Envoy Fault Injection / Istio", "Штучні HTTP 503/504, таймаути міжсервісних викликів, розрив gRPC стрімів", "#f0fdf4", "#16a34a"),
        ("Рівень 3: Оркестратор і Контейнери", "Kubernetes / Chaos Mesh / Litmus", "Знищення Pod (SIGKILL), відмова DNS, блокування NetworkPolicy, зависання API", "#fff8e6", "#d97706"),
        ("Рівень 2: Ядро ОС та Мережевий стек", "Linux TC (netem) / cgroups / eBPF", "Втрата пакетів, jitter, throttling CPU/пам'яті, перехоплення системних викликів", "#fef2f2", "#dc2626"),
        ("Рівень 1: Інфраструктура та Хмара", "AWS / GCP / Hypervisor Control Plane", "Аварія Availability Zone, відключення дисків EBS, знеструмлення хоста", "#f8fafc", "#475569")
    ]
    
    layer_w = 900.0
    layer_h = 68.0
    start_x = 30.0
    start_y = 58.0
    gap_y = 12.0
    
    for i, (l_title, l_tool, l_desc, bg_col, stroke_col) in enumerate(layers):
        y = start_y + i * (layer_h + gap_y)
        
        # Основний прямокутник рівня
        p.append(rect(start_x, y, layer_w, layer_h, fill=bg_col, stroke=stroke_col, sw=1.5, rx=6))
        
        # Ліва колонка: Назва рівня
        p.append(rect(start_x + 10, y + 10, 240, layer_h - 20, fill="#ffffff", stroke=stroke_col, sw=1.0, rx=4))
        p.append(text(start_x + 130, y + 28, l_title, size=12, color=stroke_col, bold=True))
        p.append(text(start_x + 130, y + 46, l_tool, size=10.5, color=MUTED))
        
        # Права колонка: Опис методів ін'єкції
        p.append(text(start_x + 270, y + 39, l_desc, size=11.5, color=INK, anchor="start"))
        
        # Стрілка вниз між рівнями (якщо не останній)
        if i < len(layers) - 1:
            arrow_x = start_x + layer_w - 40
            p.append(arrow(arrow_x, y + layer_h - 2, arrow_x, y + layer_h + gap_y + 2, color=LINE, sw=1.4))
            
    # Примітка внизу
    foot_y = start_y + len(layers) * (layer_h + gap_y) + 8
    p.append(text(start_x + 10, foot_y + 14, "← Ближче до бізнес-логіки (висока точність)", size=10.5, color="#4f46e5", bold=True, anchor="start"))
    p.append(text(start_x + layer_w - 10, foot_y + 14, "Ближче до фізичного оточення (широкий радіус) →", size=10.5, color="#475569", bold=True, anchor="end"))
    
    render(os.path.join(OUT, "fault-injection-layers.svg"), W, H, *p)

# ── Фіг. 3: Скінченний автомат життєвого циклу експерименту ─────────────────────
def fig_experiment_lifecycle():
    W, H = 960, 480
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(30, 36, "Життєвий цикл хаос-експерименту: скінченний автомат переходів", size=14, color=INK, bold=True, anchor="start"))
    
    # Блоки станів
    states = [
        ("1. Гіпотеза і базовий стан", "Вимірювання стійкого стану\nФормулювання очікувань SLI\nОбмеження радіуса ураження", 60, 80, 200, 110, "#f8fafc", "#64748b"),
        ("2. Активація і підготовка", "Перевірка здоров'я системи\nЗапуск сторожового таймера\nВстановлення перехоплювачів", 300, 80, 200, 110, "#eef2ff", "#4f46e5"),
        ("3. Активна ін'єкція збою", "Внесення затримки / помилок\nЗнищення вузла чи каналу\nСпостереження реакції метрик", 540, 80, 200, 110, "#fef2f2", "#dc2626"),
        ("4. Валідація стійкого стану", "Порівняння метрик із порогом\nПеревірка спрацювання fallback\nТест збереження цілісності", 700, 240, 200, 110, "#fff8e6", "#d97706"),
        ("5. Відкат і згортання (Rollback)", "Зняття мережевих правил tc\nВідновлення контейнерів\nЗвільнення дескрипторів", 420, 330, 220, 100, "#f0fdf4", "#16a34a"),
        ("Аварійний Stop (Kill Switch)", "SLO порушено або panic\nЕкстрене скидання правил\nЗахист продуктивного трафіку", 100, 260, 220, 100, "#fef2f2", "#991b1b")
    ]
    
    for s_title, s_desc, x, y, w, h, bg_col, stroke_col in states:
        p.append(rect(x, y, w, h, fill=bg_col, stroke=stroke_col, sw=1.6, rx=6))
        p.append(text(x + w/2, y + 22, s_title, size=11.5, color=stroke_col, bold=True))
        lines = s_desc.split("\n")
        p.append(mtext(x + w/2, y + 46, lines, size=10, color=INK, lh=1.35))
        
    # Стрілки нормального потоку
    p.append(arrow(262, 135, 298, 135, color=LINE, sw=1.6)) # 1 -> 2
    p.append(arrow(502, 135, 538, 135, color=LINE, sw=1.6)) # 2 -> 3
    p.append(arrow(742, 135, 800, 135, color=LINE, sw=1.6)) # 3 -> кут
    p.append(line(800, 135, 800, 238, color=LINE, sw=1.6))
    p.append(arrow(800, 238, 800, 238, color=LINE, sw=1.6)) # -> 4
    
    # 4 -> 5 (Успіх)
    p.append(arrow(700, 295, 642, 350, color="#16a34a", sw=1.6))
    p.append(text(685, 335, "Гіпотеза підтверджена", size=9.5, color="#15803d", bold=True))
    
    # 3 -> Аварійний Stop (Спрацював поріг помилок)
    p.append(arrow(580, 192, 280, 260, color="#dc2626", sw=1.8))
    p.append(text(460, 215, "SLI < Поріг (Автоматичний Abort)", size=9.5, color="#dc2626", bold=True))
    
    # Аварійний Stop -> 5 (Екстрений Rollback)
    p.append(arrow(322, 310, 418, 360, color="#991b1b", sw=1.6))
    p.append(text(345, 355, "Очищення", size=9.5, color="#991b1b", bold=True))
    
    # 5 -> 1 (Аналіз результатів і закриття циклу)
    p.append(line(420, 380, 160, 380, color=MUTED, sw=1.4, dash="4 3"))
    p.append(line(160, 380, 160, 192, color=MUTED, sw=1.4, dash="4 3"))
    p.append(arrow(160, 200, 160, 192, color=MUTED, sw=1.4))
    p.append(text(280, 395, "Ретроспектива та усунення слабкостей → повторний тест", size=10, color=MUTED))
    
    render(os.path.join(OUT, "experiment-lifecycle-state-machine.svg"), W, H, *p)

if __name__ == "__main__":
    fig_steady_state_and_blast_radius()
    fig_fault_injection_layers()
    fig_experiment_lifecycle()
    print("Generated 3 SVG figures successfully.")
