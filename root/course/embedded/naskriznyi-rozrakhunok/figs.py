# -*- coding: utf-8 -*-
"""Фігури теми «Наскрізний розрахунок: мідь, зазор, падіння, запобіжник».
Запуск: python figs.py -> ./img/*.svg
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фіг. 1: Наскрізний силовий ланцюг (Power Path Chain) ──
def fig_power_path_chain():
    W, H = 880, 420
    frs = []

    # Заголовок / фон
    frs.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Блоки ланцюга (X-координати)
    blocks = [
        {"x": 25,  "w": 100, "title": "Джерело DC", "sub": "24 В (18..32 В)", "col": "#f0f4f8", "bcol": "#3b82f6"},
        {"x": 145, "w": 100, "title": "Роз'єм XT30", "sub": "Rc = 5 мОм", "col": "#fef8ee", "bcol": "#d97706"},
        {"x": 265, "w": 100, "title": "TVS + Запобіжник", "sub": "SMBJ28A + 7A", "col": "#fef2f2", "bcol": POS},
        {"x": 385, "w": 110, "title": "Захист переполюсовки", "sub": "P-MOS (12 мОм)", "col": "#f5f3ff", "bcol": "#7c3aed"},
        {"x": 515, "w": 100, "title": "Мідна шина", "sub": "2 oz / 4 мм", "col": "#ecfdf5", "bcol": FIELD},
        {"x": 635, "w": 100, "title": "Шунт + Фільтр", "sub": "10 мОм + LC", "col": "#f0fdf4", "bcol": "#16a34a"},
        {"x": 755, "w": 105, "title": "Навантаження", "sub": "POL + Мотор 10A", "col": "#f8fafc", "bcol": INK},
    ]

    y_box = 110
    h_box = 75

    # Малюємо блоки
    for i, b in enumerate(blocks):
        frs.append(rect(b["x"], y_box, b["w"], h_box, fill=b["col"], stroke=b["bcol"], sw=2, rx=6))
        frs.append(text(b["x"] + b["w"] / 2, y_box + 28, b["title"], size=11, color=INK, bold=True))
        frs.append(text(b["x"] + b["w"] / 2, y_box + 52, b["sub"], size=10, color=MUTED))

        # Стрілка зв'язку до наступного
        if i < len(blocks) - 1:
            x_start = b["x"] + b["w"]
            x_next = blocks[i+1]["x"]
            y_mid = y_box + h_box / 2
            frs.append(line(x_start, y_mid, x_next, y_mid, color=LINE, sw=2))
            frs.append(f'<polygon points="{x_next},{y_mid} {x_next-5},{y_mid-4} {x_next-5},{y_mid+4}" fill="{LINE}"/>')

    # Пояснювальні зони знизу
    # Зона 1: Вхідний вузол і захист
    frs.append(rect(25, 225, 340, 160, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frs.append(text(195, 250, "Вхідний вузол і захист", size=13, color=POS, bold=True))
    frs.append(text(195, 275, "• TVS зрізає перенапруги (Vc < 45 В)", size=11, color=INK))
    frs.append(text(195, 300, "• Запобіжник ізолює КЗ (I²t селективність)", size=11, color=INK))
    frs.append(text(195, 325, "• Контактний опір роз'єму гріється струмом", size=11, color=INK))
    frs.append(text(195, 350, "• Зазор (Clearance/Creepage) проти пробою", size=11, color=INK))

    # Зона 2: Розподіл живлення і втрати
    frs.append(rect(385, 225, 475, 160, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frs.append(text(622, 250, "Трасування, комутація та спад напруги", size=13, color=FIELD, bold=True))
    frs.append(text(622, 275, "• MOSFET R_DS(on) росте на +40% при Tj = 100°C", size=11, color=INK))
    frs.append(text(622, 300, "• Ширина міді 2 oz за IPC-2152 обмежує ΔT <= 15°C", size=11, color=INK))
    frs.append(text(622, 325, "• Сумарний IR-спад не дає шині провалитись нижче 18 В", size=11, color=INK))
    frs.append(text(622, 350, "• Кераміка й електроліти гасять індуктивні викиди", size=11, color=INK))

    # Шина живлення зверху як анотація
    frs.append(line(75, 50, 805, 50, color=POS, sw=3))
    frs.append(text(440, 38, "Силовий тракт живлення (Power Path): послідовне накопичення втрат і захист", size=13, color=POS, bold=True))

    render(os.path.join(IMG, "power-path-chain.svg"), W, H, *frs, title="Наскрізний силовий тракт живлення")


# ── Фіг. 2: Теплова модель доріжки друкованої плати за IPC-2152 ──
def fig_trace_heating():
    W, H = 840, 460
    frs = []
    frs.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Заголовок
    frs.append(text(W / 2, 35, "Тепловий баланс силової доріжки: IPC-2221 проти IPC-2152", size=15, color=INK, bold=True))

    # Ліва частина: IPC-2221 (ізольована доріжка в повітрі)
    frs.append(rect(35, 65, 365, 365, fill="#fef8f8", stroke="#fca5a5", sw=1.5, rx=6))
    frs.append(text(217, 95, "Модель IPC-2221 (1954/1998)", size=13, color=POS, bold=True))
    frs.append(text(217, 118, "Ізольований провідник на чистому FR-4", size=11, color=MUTED))

    # Малюємо доріжку IPC-2221
    frs.append(rect(100, 160, 235, 120, fill="#d97706", stroke="#92400e", sw=2, rx=4)) # FR-4
    frs.append(text(217, 225, "FR-4 діелектрик (k = 0.25 Вт/м·К)", size=11, color="#ffffff", bold=True))
    # Мідна смуга зверху
    frs.append(rect(170, 145, 95, 15, fill="#ea580c", stroke="#9a3412", sw=1.5, rx=1))
    frs.append(text(217, 135, "Мідь 1 oz (I²R тепло)", size=10, color=POS, bold=True))

    # Стрілки тепловіддачі
    for ax in (185, 217, 250):
        frs.append(line(ax, 130, ax, 105, color=POS, sw=1.5))
        frs.append(f'<polygon points="{ax},{100} {ax-3},{107} {ax+3},{107}" fill="{POS}"/>')

    frs.append(text(217, 310, "• Тепловідвід ТІЛЬКИ через конвекцію/випромінювання", size=11, color=INK))
    frs.append(text(217, 335, "• Немає масивних внутрішніх шарів міді", size=11, color=INK))
    frs.append(text(217, 360, "• Завищує розрахований перегрів у 1.5..2.5 раза", size=11, color=POS, bold=True))
    frs.append(text(217, 385, "• Придатна лише для одношарових плат", size=11, color=MUTED))

    # Права частина: IPC-2152 (реальна багатошарова плата)
    frs.append(rect(435, 65, 370, 365, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frs.append(text(620, 95, "Сучасна модель IPC-2152 (2009)", size=13, color=FIELD, bold=True))
    frs.append(text(620, 118, "Зв'язок із суцільними мідними полігонами", size=11, color=MUTED))

    # Малюємо 4-шарову структуру
    frs.append(rect(490, 150, 260, 130, fill="#d97706", stroke="#92400e", sw=2, rx=4)) # FR-4
    # Верхня доріжка
    frs.append(rect(540, 138, 70, 12, fill="#ea580c", stroke="#9a3412", sw=1.5, rx=1))
    frs.append(text(575, 130, "Силова мідь", size=10, color=POS, bold=True))
    # Внутрішній полігон GND (Layer 2)
    frs.append(rect(495, 185, 250, 8, fill="#2563eb", stroke="#1d4ed8", sw=1, rx=1))
    frs.append(text(620, 180, "Внутрішній екран GND (Мідь розсіює тепло)", size=10, color="#2563eb", bold=True))
    # Теплові перехідні отвори
    for vx in (550, 575, 600):
        frs.append(rect(vx, 150, 4, 130, fill="#cbd5e1", stroke="#475569", sw=1))
        frs.append(line(vx+2, 140, vx+2, 280, color=POS, sw=1.5))
    frs.append(text(660, 240, "Теплові via", size=10, color="#475569"))
    # Нижній полігон (Layer 4)
    frs.append(rect(495, 272, 250, 8, fill="#2563eb", stroke="#1d4ed8", sw=1, rx=1))

    frs.append(text(620, 310, "• Тепло стікає в площини GND через діелектрик та via", size=11, color=INK))
    frs.append(text(620, 335, "• Велика площа плати ефективно розсіює тепло", size=11, color=INK))
    frs.append(text(620, 360, "• Дозволяє меншу ширину доріжки при тому ж ΔT", size=11, color=FIELD, bold=True))
    frs.append(text(620, 385, "• Враховує товщину плати, шари та охолодження", size=11, color=MUTED))

    render(os.path.join(IMG, "trace-heating-ipc.svg"), W, H, *frs, title="Тепловий баланс силової доріжки")


# ── Фіг. 3: Електричні зазори Clearance і Creepage та прорізи ──
def fig_creepage_clearance():
    W, H = 820, 440
    frs = []
    frs.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    frs.append(text(W / 2, 35, "Електричні зазори на платі: Clearance, Creepage та захисний проріз", size=15, color=INK, bold=True))

    # Верхній блок: Без прорізу
    frs.append(rect(40, 65, 740, 165, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frs.append(text(60, 90, "Стандартна поверхня плати", size=12, color=INK, bold=True, anchor="start"))

    # Текстоліт
    frs.append(rect(80, 145, 660, 45, fill="#d97706", stroke="#92400e", sw=2, rx=2))
    frs.append(text(410, 172, "Діелектрик FR-4 (Поверхня піддається пилу, волозі, солям)", size=11, color="#ffffff", bold=True))

    # Два високовольтні контакти
    frs.append(rect(140, 125, 100, 20, fill="#ea580c", stroke="#9a3412", sw=1.5, rx=2))
    frs.append(text(190, 139, "Провідник А (+230 В)", size=10, color="#ffffff", bold=True))

    frs.append(rect(580, 125, 100, 20, fill="#2563eb", stroke="#1d4ed8", sw=1.5, rx=2))
    frs.append(text(630, 139, "Провідник В (GND)", size=10, color="#ffffff", bold=True))

    # Лінія Clearance (повітря)
    frs.append(line(240, 115, 580, 115, color=POS, sw=2))
    frs.append(f'<polygon points="240,115 248,111 248,119" fill="{POS}"/>')
    frs.append(f'<polygon points="580,115 572,111 572,119" fill="{POS}"/>')
    frs.append(text(410, 105, "Clearance (Зазор через повітря) — найкоротша пряма відстань", size=11, color=POS, bold=True))

    # Лінія Creepage (по поверхні)
    frs.append(line(240, 147, 580, 147, color="#d97706", sw=2.5))
    frs.append(text(410, 137, "Creepage (Шлях витоку по поверхні FR-4) = Clearance (якщо плата плоска)", size=10, color="#b45309", bold=True))

    # Нижній блок: З фрезерованим прорізом (Milling slot)
    frs.append(rect(40, 245, 740, 175, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frs.append(text(60, 270, "Збільшення шляху витоку через фрезерований проріз (Isolation Slot)", size=12, color=FIELD, bold=True, anchor="start"))

    # Текстоліт з діркою
    frs.append(rect(80, 325, 270, 45, fill="#d97706", stroke="#92400e", sw=2, rx=2))
    frs.append(rect(470, 325, 270, 45, fill="#d97706", stroke="#92400e", sw=2, rx=2))
    # Проріз
    frs.append(rect(350, 315, 120, 65, fill="#ffffff", stroke="#64748b", sw=1.5, rx=1))
    frs.append(text(410, 350, "Проріз (Slot)", size=11, color="#64748b", bold=True))

    # Контакти
    frs.append(rect(140, 305, 100, 20, fill="#ea580c", stroke="#9a3412", sw=1.5, rx=2))
    frs.append(text(190, 319, "Провідник А", size=10, color="#ffffff", bold=True))

    frs.append(rect(580, 305, 100, 20, fill="#2563eb", stroke="#1d4ed8", sw=1.5, rx=2))
    frs.append(text(630, 319, "Провідник В", size=10, color="#ffffff", bold=True))

    # Creepage огинає паз
    pts = "240,327 350,327 350,370 470,370 470,327 580,327"
    frs.append(f'<polyline points="{pts}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    frs.append(text(410, 395, "Ефективний Creepage збільшено на 2 × глибину паза без розширення плати", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "creepage-clearance-boundary.svg"), W, H, *frs, title="Електричні зазори Clearance і Creepage")


# ── Фіг. 4: Координація захисту та селективність I²t ──
def fig_protection_coordination():
    W, H = 820, 480
    frs = []
    frs.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    frs.append(text(W / 2, 35, "Селективність та координація ланок силового захисту на площині t(I)", size=15, color=INK, bold=True))

    x0, y0 = 90, 70
    gw, gh = 660, 340
    xb, yb = x0, y0 + gh

    # Осі log-log
    frs.append(line(xb, y0, xb, yb, color=INK, sw=2))
    frs.append(line(xb, yb, xb + gw, yb, color=INK, sw=2))
    frs.append(text(xb + gw / 2, yb + 42, "Струм аварії / Номінальний струм (log)", size=12, color=INK, bold=True))
    frs.append(text(x0 - 45, y0 + gh / 2, "Час спрацювання (log)", size=12, color=INK, bold=True, anchor="middle"))

    # Сітка по Y (від 1 нс до 100 с)
    y_marks = [
        (0.05, "1 нс"),
        (0.20, "1 мкс"),
        (0.40, "1 мс"),
        (0.60, "100 мс"),
        (0.80, "10 с"),
        (0.98, "1000 с"),
    ]
    for frac, lab in y_marks:
        yy = yb - frac * gh
        frs.append(line(xb, yy, xb + gw, yy, color="#f1f5f9", sw=1))
        frs.append(text(xb - 8, yy + 4, lab, size=10, color=MUTED, anchor="end"))

    # Сітка по X (від 1x до 100x)
    x_marks = [
        (0.05, "1× (номінал)"),
        (0.30, "2× (перевантаження)"),
        (0.60, "10× (тяжке КЗ)"),
        (0.90, "50× (пікове КЗ)"),
    ]
    for frac, lab in x_marks:
        xx = xb + frac * gw
        frs.append(line(xx, y0, xx, yb, color="#f1f5f9", sw=1))
        frs.append(text(xx, yb + 20, lab, size=10, color=MUTED))

    # 1. Зона TVS супресора (зрізає напругу за наносекунди)
    frs.append(rect(xb + 0.3 * gw, yb - 0.12 * gh, 0.65 * gw, 0.08 * gh, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    frs.append(text(xb + 0.62 * gw, yb - 0.08 * gh + 4, "TVS-діод (зрізання піків напруги: 1..10 нс)", size=11, color=POS, bold=True))

    # 2. Крива руйнування ключа MOSFET / плавлення мідної доріжки (I²t_damage)
    pts_damage = []
    for step in range(20):
        t_val = step / 19.0
        xx = xb + (0.2 + 0.75 * t_val) * gw
        yy = yb - (0.85 - 0.55 * (t_val ** 0.8)) * gh
        pts_damage.append(f"{xx:.1f},{yy:.1f}")
    frs.append(f'<polyline points="{" ".join(pts_damage)}" fill="none" stroke="{POS}" stroke-width="3" stroke-dasharray="6,4"/>')
    frs.append(text(xb + 0.72 * gw, yb - 0.48 * gh, "Межа пошкодження міді / MOSFET (I²t кристала)", size=10, color=POS, bold=True))

    # 3. Крива плавкого запобіжника (Головний захист)
    pts_fuse = []
    for step in range(20):
        t_val = step / 19.0
        xx = xb + (0.2 + 0.75 * t_val) * gw
        yy = yb - (0.75 - 0.55 * (t_val ** 0.8)) * gh
        pts_fuse.append(f"{xx:.1f},{yy:.1f}")
    frs.append(f'<polyline points="{" ".join(pts_fuse)}" fill="none" stroke="{FIELD}" stroke-width="3"/>')
    frs.append(text(xb + 0.55 * gw, yb - 0.36 * gh, "Плавкий запобіжник (I²t_clear < I²t_damage)", size=11, color=FIELD, bold=True))

    # 4. Крива самовідновного запобіжника (PPTC)
    pts_pptc = []
    for step in range(20):
        t_val = step / 19.0
        xx = xb + (0.1 + 0.5 * t_val) * gw
        yy = yb - (0.92 - 0.45 * (t_val ** 0.7)) * gh
        pts_pptc.append(f"{xx:.1f},{yy:.1f}")
    frs.append(f'<polyline points="{" ".join(pts_pptc)}" fill="none" stroke="#2563eb" stroke-width="2.5"/>')
    frs.append(text(xb + 0.32 * gw, yb - 0.72 * gh, "PPTC PolySwitch (тепловий захист)", size=10, color="#2563eb", bold=True))

    render(os.path.join(IMG, "protection-coordination-i2t.svg"), W, H, *frs, title="Селективність та координація ланок силового захисту")


# ── Фіг. 5: Водоспад спаду напруги (Voltage Drop Budget) ──
def fig_voltage_drop_budget():
    W, H = 840, 440
    frs = []
    frs.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    frs.append(text(W / 2, 35, "Бюджет спаду напруги (IR Drop Waterfall) при піковому струмі 10 А", size=15, color=INK, bold=True))

    x0, y0 = 80, 80
    gw, gh = 680, 310
    xb, yb = x0, y0 + gh

    items = [
        {"name": "Джерело 24 В", "v_drop": 0.00, "r": 0, "cum": 24.00, "col": "#3b82f6", "w": 80},
        {"name": "Роз'єм XT30", "v_drop": 0.05, "r": 5, "cum": 23.95, "col": "#d97706", "w": 80},
        {"name": "Запобіжник 7A", "v_drop": 0.15, "r": 15, "cum": 23.80, "col": POS, "w": 80},
        {"name": "P-MOS FET", "v_drop": 0.12, "r": 12, "cum": 23.68, "col": "#7c3aed", "w": 80},
        {"name": "Мідні доріжки", "v_drop": 0.22, "r": 22, "cum": 23.46, "col": FIELD, "w": 80},
        {"name": "Шунт струму", "v_drop": 0.10, "r": 10, "cum": 23.36, "col": "#059669", "w": 80},
        {"name": "Навантаження", "v_drop": 0.00, "r": 0, "cum": 23.36, "col": INK, "w": 95},
    ]

    vmin, vmax = 23.00, 24.20
    def val_to_y(v):
        return yb - (v - vmin) / (vmax - vmin) * gh

    for v in (23.00, 23.20, 23.40, 23.60, 23.80, 24.00, 24.20):
        yy = val_to_y(v)
        frs.append(line(xb, yy, xb + gw, yy, color="#f1f5f9", sw=1))
        frs.append(text(xb - 8, yy + 4, f"{v:.2f} В", size=11, color=MUTED, anchor="end"))

    cur_x = xb + 30
    for i, it in enumerate(items):
        y_val = val_to_y(it["cum"])
        if i == 0:
            h_bar = yb - y_val
            frs.append(rect(cur_x, y_val, it["w"], h_bar, fill="#e0f2fe", stroke="#0284c7", sw=2, rx=4))
            frs.append(text(cur_x + it["w"]/2, y_val - 10, "24.00 В", size=11, color="#0284c7", bold=True))
        elif i == len(items) - 1:
            h_bar = yb - y_val
            frs.append(rect(cur_x, y_val, it["w"], h_bar, fill="#f1f5f9", stroke=INK, sw=2, rx=4))
            frs.append(text(cur_x + it["w"]/2, y_val - 10, f"{it['cum']:.2f} В", size=11, color=INK, bold=True))
        else:
            prev_cum = items[i-1]["cum"]
            y_prev = val_to_y(prev_cum)
            h_drop = val_to_y(it["cum"]) - y_prev
            frs.append(rect(cur_x, y_prev, it["w"], max(h_drop, 4), fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
            frs.append(text(cur_x + it["w"]/2, y_prev + h_drop/2 + 4, f"-{it['v_drop']:.2f} В", size=10, color=POS, bold=True))
            frs.append(text(cur_x + it["w"]/2, y_val - 8, f"{it['cum']:.2f} В", size=10, color=MUTED))

        frs.append(text(cur_x + it["w"]/2, yb + 20, it["name"], size=10, color=INK, bold=True))
        if it["r"] > 0:
            frs.append(text(cur_x + it["w"]/2, yb + 35, f"{it['r']} мОм", size=9, color=MUTED))

        cur_x += it["w"] + 15

    y_crit = val_to_y(23.20)
    frs.append(line(xb, y_crit, xb + gw, y_crit, color=POS, sw=1.5, dash="4 4"))
    frs.append(text(xb + gw - 10, y_crit - 6, "Граничний допустимий поріг стабільності (23.20 В)", size=10, color=POS, anchor="end", bold=True))

    render(os.path.join(IMG, "voltage-drop-budget.svg"), W, H, *frs, title="Бюджет спаду напруги при піковому струмі 10 А")


if __name__ == "__main__":
    fig_power_path_chain()
    fig_trace_heating()
    fig_creepage_clearance()
    fig_protection_coordination()
    fig_voltage_drop_budget()
