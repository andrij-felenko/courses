# -*- coding: utf-8 -*-
"""Фігури до теми «Драбина власного заліза: девборда → готовий модуль → SoM → повністю своя».
Запуск: python figs.py  → записує SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


# ── 1. Чотири сходинки власного заліза (ladder-overview) ──────────────────────
def fig_ladder_overview():
    W, H = 840, 480
    el = []
    
    # 4 сходинки у вигляді блоків
    steps = [
        {
            "num": "Сходинка 1",
            "title": "Девборда + макетка",
            "subtitle": "Перевірка гіпотези за години",
            "nre": "NRE: $0",
            "bom": "BOM: дуже високий",
            "time": "Запуск: 1–3 дні",
            "risk": "Ризик: нульовий у розробці, критичний у полі",
            "color": "#8892b0",
            "bg": "#f8fafc",
            "border": "#cbd5e1"
        },
        {
            "num": "Сходинка 2",
            "title": "Модуль на носії",
            "subtitle": "Сертифікований MCU/RF модуль",
            "nre": "NRE: $1k – $3k",
            "bom": "BOM: помірний (+$1.5–$3)",
            "time": "Запуск: 2–4 тижні",
            "risk": "Ризик: мінімальний (ВЧ/EMC закриті)",
            "color": "#2563eb",
            "bg": "#eff6ff",
            "border": "#93c5fd"
        },
        {
            "num": "Сходинка 3",
            "title": "SoM на носії",
            "subtitle": "Linux, MPU, DDR, PMIC у SoM",
            "nre": "NRE: $4k – $12k",
            "bom": "BOM: $25 – $120 за SoM",
            "time": "Запуск: 1–3 місяці",
            "risk": "Ризик: помірний (DDR/HDI розведено)",
            "color": "#0d9488",
            "bg": "#f0fdfa",
            "border": "#99f6e4"
        },
        {
            "num": "Сходинка 4",
            "title": "Chip-Down (своя)",
            "subtitle": "Голі кристали BGA/MCU/RF/DDR",
            "nre": "NRE: $25k – $100k+",
            "bom": "BOM: мінімальний можливий",
            "time": "Запуск: 6–12 місяців",
            "risk": "Ризик: високий (EMC/DDR на вас)",
            "color": "#b91c1c",
            "bg": "#fef2f2",
            "border": "#fca5a5"
        }
    ]
    
    col_w = 185
    gap = 15
    start_x = 30
    
    for i, s in enumerate(steps):
        cx = start_x + i * (col_w + gap)
        h_box = 320
        y_box = 80 + (3 - i) * 15
        
        el.append(rect(cx, y_box, col_w, h_box, fill=s["bg"], stroke=s["border"], sw=2, rx=8))
        
        el.append(rect(cx, y_box, col_w, 42, fill=s["color"], stroke=s["color"], sw=1, rx=8))
        el.append(rect(cx, y_box + 20, col_w, 22, fill=s["color"], stroke=s["color"], sw=0, rx=0))
        el.append(text(cx + col_w/2, y_box + 26, s["num"], size=15, color="#ffffff", bold=True))
        
        el.append(text(cx + col_w/2, y_box + 66, s["title"], size=13, color=INK, bold=True))
        el.append(fitbox(cx + 6, y_box + 78, col_w - 12, 38, s["subtitle"], size=11, color=MUTED, fill=s["bg"], stroke=s["bg"]))
        
        el.append(line(cx + 12, y_box + 124, cx + col_w - 12, y_box + 124, color=s["border"], sw=1))
        
        el.append(text(cx + 12, y_box + 148, s["nre"], size=11, color=INK, anchor="start", bold=True))
        el.append(text(cx + 12, y_box + 172, s["bom"], size=11, color=INK, anchor="start"))
        el.append(text(cx + 12, y_box + 196, s["time"], size=11, color=INK, anchor="start"))
        
        el.append(rect(cx + 8, y_box + 215, col_w - 16, 92, fill="#ffffff", stroke=s["border"], sw=1, rx=6))
        el.append(fitbox(cx + 12, y_box + 220, col_w - 24, 82, s["risk"], size=11, color=INK, fill="#ffffff", stroke="#ffffff"))
    
    el.append(arrow(30, 445, 810, 445, color=POS, sw=2.5))
    el.append(text(420, 435, "Зростання вартості розробки (NRE), вимог до кваліфікації та ціни помилки →", size=12, color=POS, bold=True))
    
    el.append(arrow(810, 60, 30, 60, color=FIELD, sw=2.5))
    el.append(text(420, 52, "← Зниження собівартості одиниці (BOM) при великих партіях", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "ladder-overview.svg"), W, H, *el, title="Чотири сходинки архітектури власного заліза")


# ── 2. Плата-носій з модулем проти Chip-Down (carrier-vs-chipdown) ───────────
def fig_carrier_vs_chipdown():
    W, H = 820, 440
    el = []
    
    half_w = 370
    
    # ── Лівий блок: Модуль на платі-носії ──
    lx = 25
    el.append(rect(lx, 60, half_w, 360, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    el.append(rect(lx, 60, half_w, 36, fill="#2563eb", stroke="#2563eb", sw=1, rx=8))
    el.append(rect(lx, 80, half_w, 16, fill="#2563eb", stroke="#2563eb", sw=0, rx=0))
    el.append(text(lx + half_w/2, 84, "Плата-носій + модуль / SoM (Сходинки 2 і 3)", size=13, color="#ffffff", bold=True))
    
    el.append(rect(lx + 20, 110, half_w - 40, 290, fill="#e2e8f0", stroke="#64748b", sw=2, rx=6))
    el.append(text(lx + 30, 130, "Власна плата-носій (2–4 шари, FR-4)", size=11, color="#334155", anchor="start", bold=True))
    el.append(text(lx + 30, 146, "Дешева фабрика, прості доріжки 0.2 мм, без HDI", size=10, color=MUTED, anchor="start"))
    
    el.append(rect(lx + 35, 165, half_w - 70, 135, fill="#dbeafe", stroke="#3b82f6", sw=2, rx=6))
    el.append(text(lx + half_w/2, 185, "Готовий модуль / SoM (фабричний вузол)", size=11, color="#1e40af", bold=True))
    
    el.append(rect(lx + 48, 198, 70, 55, fill="#93c5fd", stroke="#1d4ed8", sw=1, rx=4))
    el.append(text(lx + 83, 222, "MCU/SoC", size=10, color="#1e3a8a", bold=True))
    el.append(text(lx + 83, 238, "BGA / QFN", size=9, color="#1e3a8a"))
    
    el.append(rect(lx + 128, 198, 70, 55, fill="#93c5fd", stroke="#1d4ed8", sw=1, rx=4))
    el.append(text(lx + 163, 222, "DDR/Flash", size=10, color="#1e3a8a", bold=True))
    el.append(text(lx + 163, 238, "Пам'ять", size=9, color="#1e3a8a"))
    
    el.append(rect(lx + 208, 198, 80, 55, fill="#bfdbfe", stroke="#1d4ed8", sw=1, rx=4))
    el.append(text(lx + 248, 218, "ВЧ-тракт", size=10, color="#1e3a8a", bold=True))
    el.append(text(lx + 248, 232, "Екран + 50Ω", size=9, color="#1e3a8a"))
    el.append(text(lx + 248, 245, "FCC/CE ID", size=9, color=POS, bold=True))
    
    el.append(text(lx + half_w/2, 285, "Високошвидкісні шини та ВЧ ізольовані на SoM", size=10, color="#1e40af", italic=True))
    
    el.append(rect(lx + 35, 315, 80, 45, fill="#f1f5f9", stroke="#475569", sw=1, rx=4))
    el.append(text(lx + 75, 335, "Живлення", size=10, color=INK, bold=True))
    el.append(text(lx + 75, 350, "DC-DC / LDO", size=9, color=MUTED))
    
    el.append(rect(lx + 130, 315, 100, 45, fill="#f1f5f9", stroke="#475569", sw=1, rx=4))
    el.append(text(lx + 180, 335, "Роз'єми I/O", size=10, color=INK, bold=True))
    el.append(text(lx + 180, 350, "USB / UART / CAN", size=9, color=MUTED))
    
    el.append(rect(lx + 245, 315, 80, 45, fill="#f1f5f9", stroke="#475569", sw=1, rx=4))
    el.append(text(lx + 285, 335, "Датчики", size=10, color=INK, bold=True))
    el.append(text(lx + 285, 350, "Клеми / I2C", size=9, color=MUTED))
    
    el.append(text(lx + half_w/2, 385, "Просте трасування: розводяться лише низькошвидкісні зв'язки", size=10, color=FIELD, bold=True))

    # ── Правий блок: Chip-Down ──
    rx = 425
    el.append(rect(rx, 60, half_w, 360, fill="#fef2f2", stroke="#f87171", sw=1.5, rx=8))
    el.append(rect(rx, 60, half_w, 36, fill="#b91c1c", stroke="#b91c1c", sw=1, rx=8))
    el.append(rect(rx, 80, half_w, 16, fill="#b91c1c", stroke="#b91c1c", sw=0, rx=0))
    el.append(text(rx + half_w/2, 84, "Повністю власна плата (Chip-Down, Сходинка 4)", size=13, color="#ffffff", bold=True))
    
    el.append(rect(rx + 20, 110, half_w - 40, 290, fill="#fee2e2", stroke="#dc2626", sw=2, rx=6))
    el.append(text(rx + 30, 130, "Власна складна PCB (6–10 шарів, HDI, microvia)", size=11, color="#991b1b", anchor="start", bold=True))
    el.append(text(rx + 30, 146, "Дороге виробництво, контроль імпедансу, вирівнювання ліній", size=10, color=MUTED, anchor="start"))
    
    el.append(rect(rx + 35, 165, 85, 75, fill="#fca5a5", stroke="#b91c1c", sw=1.5, rx=4))
    el.append(text(rx + 77, 192, "Голий SoC", size=10, color="#7f1d1d", bold=True))
    el.append(text(rx + 77, 207, "BGA 0.5mm", size=9, color="#7f1d1d"))
    el.append(text(rx + 77, 222, "400+ pins", size=9, color="#7f1d1d"))
    
    el.append(rect(rx + 130, 165, 85, 75, fill="#fca5a5", stroke="#b91c1c", sw=1.5, rx=4))
    el.append(text(rx + 172, 192, "DDR4 / eMMC", size=10, color="#7f1d1d", bold=True))
    el.append(text(rx + 172, 207, "Шина 3.2 Gbps", size=9, color="#7f1d1d"))
    el.append(text(rx + 172, 222, "Length match", size=9, color="#7f1d1d"))
    
    el.append(rect(rx + 225, 165, 100, 75, fill="#fecaca", stroke="#b91c1c", sw=1.5, rx=4))
    el.append(text(rx + 275, 188, "Дискретний ВЧ", size=10, color="#7f1d1d", bold=True))
    el.append(text(rx + 275, 202, "Балун + узгодж.", size=9, color="#7f1d1d"))
    el.append(text(rx + 275, 216, "Власна антена", size=9, color="#7f1d1d"))
    el.append(text(rx + 275, 230, "Повна сертиф.", size=9, color=POS, bold=True))
    
    el.append(rect(rx + 35, 255, 95, 50, fill="#ffffff", stroke="#dc2626", sw=1, rx=4))
    el.append(text(rx + 82, 277, "PMIC / Порядок", size=10, color="#7f1d1d", bold=True))
    el.append(text(rx + 82, 292, "Power sequencing", size=9, color=MUTED))
    
    el.append(rect(rx + 140, 255, 95, 50, fill="#ffffff", stroke="#dc2626", sw=1, rx=4))
    el.append(text(rx + 187, 277, "Тестові точки", size=10, color="#7f1d1d", bold=True))
    el.append(text(rx + 187, 292, "Boundary Scan", size=9, color=MUTED))
    
    el.append(rect(rx + 245, 255, 80, 50, fill="#ffffff", stroke="#dc2626", sw=1, rx=4))
    el.append(text(rx + 285, 277, "Роз'єми I/O", size=10, color="#7f1d1d", bold=True))
    el.append(text(rx + 285, 292, "ESD захист", size=9, color=MUTED))
    
    el.append(text(rx + half_w/2, 335, "Високий ризик: кожна помилка BGA/DDR вимагає респіну ($5k+)", size=10, color=POS, bold=True))
    el.append(text(rx + half_w/2, 385, "Максимальна компактність, мінімальний BOM при 50k+ шт.", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "carrier-vs-chipdown.svg"), W, H, *el, title="Плата-носій з готовим модулем/SoM проти Chip-Down проектування")


# ── 3. Криві сукупної вартості (cost-breakeven-curves) ───────────────────────
def fig_cost_breakeven():
    W, H = 820, 460
    el = []
    
    ox, oy = 90, 390
    gw, gh = 680, 310
    
    # Осі координат
    el.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    el.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    
    # Підписи осей
    el.append(text(ox + gw/2, oy + 42, "Обсяг виготовленої партії V (штук, логарифмічна шкала)", size=13, color=INK, bold=True))
    el.append(text(ox - 50, oy - gh/2, "Повна вартість за одиницю (NRE/V + BOM + тест), $", size=12, color=INK, bold=True, anchor="middle"))
    
    # Засічки по X
    x_ticks = [
        (10, 0.05, "10"),
        (50, 0.22, "50"),
        (300, 0.42, "300"),
        (2000, 0.65, "2 000"),
        (10000, 0.82, "10 000"),
        (50000, 0.98, "50 000+")
    ]
    for val, frac, label in x_ticks:
        tx = ox + frac * gw
        el.append(line(tx, oy, tx, oy + 5, color=MUTED, sw=1))
        el.append(line(tx, oy, tx, oy - gh, color="#f1f5f9", sw=1, dash="3,4"))
        el.append(text(tx, oy + 18, label, size=11, color=MUTED))
    
    # Засічки по Y
    y_ticks = [
        (0.15, "$15"),
        (0.35, "$35"),
        (0.55, "$70"),
        (0.75, "$150"),
        (0.95, "$350")
    ]
    for frac, label in y_ticks:
        ty = oy - frac * gh
        el.append(line(ox - 5, ty, ox, ty, color=MUTED, sw=1))
        el.append(line(ox, ty, ox + gw, ty, color="#f1f5f9", sw=1, dash="3,4"))
        el.append(text(ox - 10, ty + 4, label, size=11, color=MUTED, anchor="end"))
        
    # ── Криві 4-х сходинок ──
    # 1. Девборда + шилд
    pts1 = [(ox + 0.05*gw, oy - 0.72*gh), (ox + 0.22*gw, oy - 0.52*gh), (ox + 0.42*gw, oy - 0.50*gh), (ox + 0.65*gw, oy - 0.49*gh)]
    el.append(polyline(pts1, color="#64748b", sw=2.5, dash="5,4"))
    el.append(text(ox + 0.22*gw, oy - 0.56*gh, "Сходинка 1: Девборда", size=11, color="#475569", bold=True, anchor="start"))
    
    # 2. Модуль на платі-носії (MCU)
    pts2 = [(ox + 0.05*gw, oy - 0.96*gh), (ox + 0.22*gw, oy - 0.58*gh), (ox + 0.42*gw, oy - 0.26*gh), (ox + 0.65*gw, oy - 0.19*gh), (ox + 0.82*gw, oy - 0.18*gh)]
    el.append(polyline(pts2, color="#2563eb", sw=3))
    el.append(text(ox + 0.38*gw, oy - 0.21*gh, "Сходинка 2: Модуль на носії", size=11, color="#2563eb", bold=True, anchor="start"))
    
    # 3. SoM на платі-носії (MPU/Linux)
    pts3 = [(ox + 0.10*gw, oy - 0.98*gh), (ox + 0.25*gw, oy - 0.75*gh), (ox + 0.45*gw, oy - 0.48*gh), (ox + 0.68*gw, oy - 0.38*gh), (ox + 0.85*gw, oy - 0.36*gh)]
    el.append(polyline(pts3, color="#0d9488", sw=2.5, dash="6,3"))
    el.append(text(ox + 0.62*gw, oy - 0.44*gh, "Сходинка 3: SoM + носій", size=11, color="#0d9488", bold=True, anchor="start"))
    
    # 4. Chip-Down
    pts4 = [(ox + 0.30*gw, oy - 0.98*gh), (ox + 0.50*gw, oy - 0.65*gh), (ox + 0.68*gw, oy - 0.30*gh), (ox + 0.82*gw, oy - 0.16*gh), (ox + 0.98*gw, oy - 0.10*gh)]
    el.append(polyline(pts4, color="#b91c1c", sw=3))
    el.append(text(ox + 0.82*gw, oy - 0.05*gh, "Сходинка 4: Chip-Down", size=11, color="#b91c1c", bold=True, anchor="end"))
    
    # Точки перетину (Break-Even)
    bx1 = ox + 0.22*gw
    by1 = oy - 0.55*gh
    el.append(circle(bx1, by1, 5, fill="#f59e0b", stroke="#b45309", sw=2))
    el.append(text(bx1 + 10, by1 - 12, "V₁* ≈ 40 шт", size=10, color="#b45309", bold=True, anchor="start"))
    
    bx2 = ox + 0.76*gw
    by2 = oy - 0.18*gh
    el.append(circle(bx2, by2, 5, fill="#f59e0b", stroke="#b45309", sw=2))
    el.append(text(bx2 - 10, by2 - 14, "V₂* ≈ 5 000 – 8 000 шт", size=10, color="#b45309", bold=True, anchor="end"))
    
    # Пояснювальний бокс у правому верхньому куті (вільному від кривих)
    el.append(rect(ox + 0.50*gw, oy - gh + 15, 320, 65, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=6))
    el.append(text(ox + 0.50*gw + 12, oy - gh + 33, "Точка беззбитковості (Break-Even V*):", size=11, color=INK, anchor="start", bold=True))
    el.append(text(ox + 0.50*gw + 12, oy - gh + 51, "V* = (NRE₂ − NRE₁) / (BOM₁ − BOM₂)", size=11, color=POS, anchor="start", bold=True))
    el.append(text(ox + 0.50*gw + 12, oy - gh + 68, "Перехід виправданий при тиражі V > V*", size=10, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "cost-breakeven-curves.svg"), W, H, *el, title="Питома собівартість пристрою та точки економічного переходу")


if __name__ == "__main__":
    fig_ladder_overview()
    fig_carrier_vs_chipdown()
    fig_cost_breakeven()
    print("All figures generated successfully.")
