# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фіг. 1: Нелінійне зростання затримки та коліно черги (Hockey Stick) ──────
def fig_utilization_latency_hockey_stick():
    W, H = 960, 500
    p = []
    
    # Фон полотна
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 38, "Нелінійна деградація затримки: фізика насичення ресурсів і коліно черги", size=15, color=INK, bold=True))
    
    # Область графіка
    gx, gy, gw, gh = 100, 80, 520, 340
    
    # Зони навантаження (кольорові вертикальні смуги)
    # Зона 1: Безпечна зона (0% - 70%)
    w_safe = gw * 0.70
    p.append(rect(gx, gy, w_safe, gh, fill="#f0fdf4", stroke="none", rx=0))
    p.append(text(gx + w_safe / 2, gy + 25, "Безпечна зона (0–70%)", size=11.5, color="#166534", bold=True))
    p.append(text(gx + w_safe / 2, gy + 42, "Затримка стабільна, черги мізерні", size=10, color="#15803d"))
    
    # Зона 2: Зона ризику / буфер Headroom (70% - 85%)
    w_warn = gw * 0.15
    p.append(rect(gx + w_safe, gy, w_warn, gh, fill="#fffbeb", stroke="none", rx=0))
    p.append(text(gx + w_safe + w_warn / 2, gy + 25, "Зона Headroom (70–85%)", size=11, color="#b45309", bold=True))
    p.append(text(gx + w_safe + w_warn / 2, gy + 42, "Початок росту черг", size=9.5, color="#d97706"))
    
    # Зона 3: Зона насичення та колапсу (85% - 100%)
    w_crit = gw * 0.15
    p.append(rect(gx + w_safe + w_warn, gy, w_crit, gh, fill="#fef2f2", stroke="none", rx=0))
    p.append(text(gx + w_safe + w_warn + w_crit / 2, gy + 25, "Колапс (85–100%)", size=11, color="#991b1b", bold=True))
    p.append(text(gx + w_safe + w_warn + w_crit / 2, gy + 42, "Експоненційний стрибок", size=9.5, color="#dc2626"))
    
    # Сітка графіка
    for u in [0.2, 0.4, 0.6, 0.8, 1.0]:
        x = gx + gw * u
        p.append(line(x, gy, x, gy + gh, color="#e2e8f0", sw=1, dash="4,4"))
        p.append(text(x, gy + gh + 18, "%d%%" % int(u * 100), size=10.5, color=MUTED))
        
    for l_val, l_text in [(0.25, "100 мс"), (0.5, "500 мс"), (0.75, "2 с"), (1.0, "10 с+")]:
        y = gy + gh - gh * l_val
        p.append(line(gx, y, gx + gw, y, color="#e2e8f0", sw=1, dash="4,4"))
        p.append(text(gx - 12, y + 4, l_text, size=10.5, color=MUTED, anchor="end"))
        
    # Осі
    p.append(line(gx, gy + gh, gx + gw + 15, gy + gh, color=INK, sw=1.8))
    p.append(line(gx, gy + gh, gx, gy - 15, color=INK, sw=1.8))
    p.append(text(gx + gw / 2, gy + gh + 42, "Утилізація ресурсів вузла або кластера (U = λ / C)", size=12, color=INK, bold=True))
    
    # Вертикальний підпис осі затримки
    p.append(text(gx - 45, gy - 8, "Затримка відповіді (Latency / RT)", size=11.5, color=INK, bold=True, anchor="start"))
    
    # Крива затримки (hockey stick)
    pts = []
    # W_q = S / (1 - U)
    # Нормалізуємо для відображення: при U=0 -> y_rel=0.05, U=0.7 -> y_rel=0.15, U=0.85 -> y_rel=0.35, U=0.95 -> y_rel=0.95
    for i in range(101):
        u = i / 100.0
        if u < 0.96:
            # Модель M/M/1: T = 1 / (1 - u)
            t_val = 1.0 / (1.0 - u * 0.95)
            # масштабування під висоту gh
            y_rel = (t_val - 1.0) / 19.0 * 0.92 + 0.04
            px = gx + u * gw
            py = gy + gh - min(y_rel * gh, gh)
            pts.append((px, py))
            
    path_d = "M " + " L ".join(["%.1f,%.1f" % pt for pt in pts])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (path_d, "#dc2626"))
    
    # Точка коліна (Knee of the curve)
    knee_x = gx + gw * 0.75
    knee_y = gy + gh - 0.22 * gh
    p.append(circle(knee_x, knee_y, 5, fill="#dc2626", stroke="#ffffff", sw=2))
    
    # Блок пояснення праворуч
    bx, by, bw, bh = 660, 80, 270, 340
    p.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(bx + bw / 2, by + 24, "Висновки для планування", size=13, color=INK, bold=True))
    
    insights = [
        "1. Коліно затримки (Knee):",
        "При U > 70–75% швидкість",
        "росту черги вибухає.",
        "",
        "2. Нелінійний ефект:",
        "Навантаження +20% при U=80%",
        "збільшує затримку на 400–800%,",
        "а не на 20%.",
        "",
        "3. Цільовий Headroom:",
        "Тримати середнє U ≤ 65–70%,",
        "щоб сплески не перетинали",
        "критичну точку насичення.",
        "",
        "4. Формула Кінгмана:",
        "Коли U → 100%, час черги",
        "прямує до нескінченності."
    ]
    p.append(mtext(bx + 16, by + 50, insights, size=10.5, color=INK, anchor="start", lh=1.35))
    
    render(os.path.join(OUT, "utilization-latency-hockey-stick.svg"), W, H, *p)


# ── Фіг. 2: Анатомія Headroom — розкладання шарів ємності ─────────────────────
def fig_headroom_layer_breakdown():
    W, H = 960, 520
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 36, "Анатомія Headroom: з яких інженерних шарів складається загальна потужність", size=15, color=INK, bold=True))
    
    # Загальний стовпчик місткості (Stack breakdown)
    sx, sy, sw_col = 80, 75, 240
    
    # Шари стовпчика (знизу вгору)
    # 1. Базове навантаження (100 RPS / 40%)
    # 2. Добовий пік (+50 RPS / 20%)
    # 3. Спалахи та дисперсія трафіку (+25 RPS / 10%)
    # 4. N+1 резерв відмови вузла (+50 RPS / 20%)
    # 5. Буфер на час постачання (+25 RPS / 10%)
    
    h1 = 120  # Базове
    h2 = 70   # Добовий пік
    h3 = 45   # Спалахи
    h4 = 75   # N+1 відмова
    h5 = 50   # Буфер Lead Time
    
    total_h = h1 + h2 + h3 + h4 + h5 # 360 px
    
    y_base5 = sy
    y_base4 = y_base5 + h5
    y_base3 = y_base4 + h4
    y_base2 = y_base3 + h3
    y_base1 = y_base2 + h2
    
    # Малюємо шари
    p.append(rect(sx, y_base1, sw_col, h1, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=0))
    p.append(text(sx + sw_col / 2, y_base1 + h1 / 2 - 8, "1. Базове навантаження (Baseline)", size=11.5, color="#1e40af", bold=True))
    p.append(text(sx + sw_col / 2, y_base1 + h1 / 2 + 12, "Постійний нічний/денний мінімум трафіку", size=10, color="#3b82f6"))
    
    p.append(rect(sx, y_base2, sw_col, h2, fill="#dbeafe", stroke="#1d4ed8", sw=1.5, rx=0))
    p.append(text(sx + sw_col / 2, y_base2 + h2 / 2 - 8, "2. Добові коливання (Diurnal Peak)", size=11.5, color="#1e3a8a", bold=True))
    p.append(text(sx + sw_col / 2, y_base2 + h2 / 2 + 12, "Прогнозований денний пік активності", size=10, color="#2563eb"))
    
    p.append(rect(sx, y_base3, sw_col, h3, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=0))
    p.append(text(sx + sw_col / 2, y_base3 + h3 / 2 - 6, "3. Дисперсія і спалахи (Burst Factor)", size=11, color="#92400e", bold=True))
    p.append(text(sx + sw_col / 2, y_base3 + h3 / 2 + 12, "Короткі стрибки (акції, розсилки, пуші)", size=9.5, color="#b45309"))
    
    p.append(rect(sx, y_base4, sw_col, h4, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=0))
    p.append(text(sx + sw_col / 2, y_base4 + h4 / 2 - 8, "4. Резерв відмов (N+1 / Multi-AZ)", size=11.5, color="#991b1b", bold=True))
    p.append(text(sx + sw_col / 2, y_base4 + h4 / 2 + 12, "Запас на випадання вузла чи цілої зони", size=10, color="#dc2626"))
    
    p.append(rect(sx, y_base5, sw_col, h5, fill="#f3e8ff", stroke="#9333ea", sw=1.5, rx=0))
    p.append(text(sx + sw_col / 2, y_base5 + h5 / 2 - 6, "5. Буфер лагу постачання (Lead Time)", size=11, color="#6b21a8", bold=True))
    p.append(text(sx + sw_col / 2, y_base5 + h5 / 2 + 12, "Запас на час створення нових VM/серверів", size=9.5, color="#7e22ce"))
    
    # Фігурні дужки / виділення зон зліва та справа
    # Зліва: Фактичний робочий попит (шари 1 + 2 + 3) проти Headroom (шари 3 + 4 + 5)
    p.append(line(sx - 15, y_base1 + h1, sx - 15, y_base2, color="#2563eb", sw=2))
    p.append(text(sx - 25, (y_base1 + h1 + y_base2) / 2, "Регулярний попит (60%)", size=11, color="#2563eb", bold=True, anchor="end"))
    
    p.append(line(sx - 15, y_base3 + h3, sx - 15, y_base5, color="#dc2626", sw=2))
    p.append(text(sx - 25, (y_base3 + h3 + y_base5) / 2, "Динамічний Headroom (40%)", size=11, color="#dc2626", bold=True, anchor="end"))
    
    # Права частина: детальні картки пояснення кожного рівня
    cx, cw = 360, 560
    
    cards = [
        ("5. Час закупівлі й розгортання", y_base5, h5, "#faf5ff", "#9333ea", 
         "Автоскейлу потрібні 2–5 хв на старт подів і до 10 хв на підйом VM. Без запасу сервіс ляже до появи нод."),
        ("4. Відмовостійкість інфраструктури", y_base4, h4, "#fef2f2", "#dc2626", 
         "Якщо кластер із 3 вузлів працює на 80%, падіння 1 вузла підніме навантаження на решту до 120% (крах)."),
        ("3. Мікросплески та флуктуації", y_base3, h3, "#fffbeb", "#d97706", 
         "Реальний трафік не є ламінарним: пуш-сповіщення генерують миттєвий 3–5-кратний сплеск на 30–60 секунд."),
        ("2. Добова ритміка бізнесу", y_base2, h2, "#eff6ff", "#1d4ed8", 
         "Різниця між нічним мінімумом (04:00) та вечірнім піком (20:00) у споживчих сервісах сягає 300–600%."),
        ("1. Базове ядро системи", y_base1, h1, "#f8fafc", "#2563eb", 
         "Мінімальна постійна місткість, необхідна для фонових задач, реплікації сховищ та чергового трафіку.")
    ]
    
    for title, cy, ch, bg_c, border_c, desc in cards:
        p.append(rect(cx, cy, cw, ch, fill=bg_c, stroke=border_c, sw=1.4, rx=6))
        p.append(text(cx + 16, cy + 20, title, size=11.5, color=border_c, bold=True, anchor="start"))
        p.append(text(cx + 16, cy + ch - 14, desc, size=10, color=INK, anchor="start"))
        # Стрілка зв'язку
        p.append(line(sx + sw_col + 8, cy + ch / 2, cx - 8, cy + ch / 2, color=border_c, sw=1.2, dash="3,3"))
        
    render(os.path.join(OUT, "headroom-layer-breakdown.svg"), W, H, *p)


# ── Фіг. 3: Горизонти планування та час реакції (Lead Time Spectrum) ──────────
def fig_capacity_lead_time_horizons():
    W, H = 960, 500
    p = []
    
    # Фон
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Заголовок
    p.append(text(W / 2, 36, "Горизонти планування місткості: лаг постачання ресурсів проти темпу реакції", size=15, color=INK, bold=True))
    
    col_w = 265
    col_h = 390
    y_top = 70
    
    # Колонка 1: Швидкий рівень (Реактивний / Автоскейл)
    x1 = 40
    p.append(rect(x1, y_top, col_w, col_h, fill="#eff6ff", stroke="#2563eb", sw=1.6, rx=8))
    p.append(rect(x1, y_top, col_w, 42, fill="#2563eb", stroke="none", rx=0))
    p.append(text(x1 + col_w / 2, y_top + 26, "Швидкий контур (Секунди — Хвилини)", size=12, color="#ffffff", bold=True))
    
    items1 = [
        ("Механізм:", "HPA, KEDA, Serverless FaaS"),
        ("Одиниця ресурсу:", "Контейнери, процеси, поди"),
        ("Час надання (Lag):", "500 мс — 3 хвилини"),
        ("Ціль планування:", "Поглинання добових піків"),
        ("Головний ризик:", "Холодний старт (Cold Start),"),
        ("", "тротлінг до розігріву пулу,"),
        ("", "вичерпання пулу з'єднань БД.")
    ]
    cy = y_top + 65
    for label, val in items1:
        if label:
            p.append(text(x1 + 14, cy, label, size=11, color="#1e40af", bold=True, anchor="start"))
            p.append(text(x1 + 14, cy + 18, val, size=10.5, color=INK, anchor="start"))
            cy += 40
        else:
            p.append(text(x1 + 14, cy - 22 + 16, val, size=10.5, color=INK, anchor="start"))
            cy += 18
            
    # Колонка 2: Середній рівень (Тактичний / Хмарна інфраструктура)
    x2 = 345
    p.append(rect(x2, y_top, col_w, col_h, fill="#fdf4ff", stroke="#c026d3", sw=1.6, rx=8))
    p.append(rect(x2, y_top, col_w, 42, fill="#c026d3", stroke="none", rx=0))
    p.append(text(x2 + col_w / 2, y_top + 26, "Тактичний контур (Години — Дні)", size=12, color="#ffffff", bold=True))
    
    items2 = [
        ("Механізм:", "Cluster Autoscaler, Karpenter, Spot/On-demand VM"),
        ("Одиниця ресурсу:", "Віртуальні машини, дискові масиви"),
        ("Час надання (Lag):", "2 хвилини — 48 годин"),
        ("Ціль планування:", "Підготовка до промо-акцій"),
        ("Головний ризик:", "Вичерпання хмарних квот"),
        ("", "(Cloud Service Quotas), нестача"),
        ("", "інстансів потрібного типу в регіоні.")
    ]
    cy = y_top + 65
    for label, val in items2:
        if label:
            p.append(text(x2 + 14, cy, label, size=11, color="#86198f", bold=True, anchor="start"))
            p.append(text(x2 + 14, cy + 18, val, size=10.5, color=INK, anchor="start"))
            cy += 40
        else:
            p.append(text(x2 + 14, cy - 22 + 16, val, size=10.5, color=INK, anchor="start"))
            cy += 18

    # Колонка 3: Повільний рівень (Стратегічний / Bare-Metal та закупівлі)
    x3 = 655
    p.append(rect(x3, y_top, col_w, col_h, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=8))
    p.append(rect(x3, y_top, col_w, 42, fill="#d97706", stroke="none", rx=0))
    p.append(text(x3 + col_w / 2, y_top + 26, "Стратегічний контур (Тижні — Місяці)", size=12, color="#ffffff", bold=True))
    
    items3 = [
        ("Механізм:", "Закупівлі заліза, оренда стійок, оптичні лінки"),
        ("Одиниця ресурсу:", "Серверні шафи, SAN, мережевий транзит"),
        ("Час надання (Lag):", "4 тижні — 6 місяців"),
        ("Ціль планування:", "Річний бюджетний прогноз росту"),
        ("Головний ризик:", "Затримки в ланцюгах постачання,"),
        ("", "заморожування капіталу (CAPEX),"),
        ("", "недовантаження або дефіцит заліза.")
    ]
    cy = y_top + 65
    for label, val in items3:
        if label:
            p.append(text(x3 + 14, cy, label, size=11, color="#92400e", bold=True, anchor="start"))
            p.append(text(x3 + 14, cy + 18, val, size=10.5, color=INK, anchor="start"))
            cy += 40
        else:
            p.append(text(x3 + 14, cy - 22 + 16, val, size=10.5, color=INK, anchor="start"))
            cy += 18

    render(os.path.join(OUT, "capacity-lead-time-horizons.svg"), W, H, *p)

if __name__ == "__main__":
    fig_utilization_latency_hockey_stick()
    fig_headroom_layer_breakdown()
    fig_capacity_lead_time_horizons()
    print("All figures generated successfully.")
