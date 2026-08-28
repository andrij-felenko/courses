# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '</defs>' % (NEG, FIELD, POS)
)

def carrow(x1, y1, x2, y2, color, mid, sw=2.0):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, mid))


def fig_paradigm_hierarchy():
    W, H = 1000, 520
    p = [COL_MARKERS]
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff"))
    
    p.append(text(W / 2, 28, "Точки входу трьох парадигм у вкладені контури керування", size=16, bold=True))
    
    # Оператор зліва окремо від контурів
    p.append(rect(25, 200, 140, 90, fill="#f8fafc", stroke=LINE, sw=1.8, rx=6))
    p.append(text(95, 235, "ОПЕРАТОР", size=13, bold=True, color=INK))
    p.append(text(95, 255, "Пульт / GCS", size=11, color=MUTED))
    p.append(text(95, 273, "Радіолінк", size=10, color=MUTED))
    
    # 4 вкладені рівні контурів керування (колонки від 200 до 960)
    tiers = [
        ("МІСІЙНИЙ КОНТУР (0.5–2 Гц)", "Планувальник місій, вейпойнти, геозона, обхід перешкод", 195, 100, 185, 360, "#eff6ff", "#93c5fd"),
        ("НАВІГАЦІЙНИЙ (20–50 Гц)", "Позиція [X, Y, Z], шляхова швидкість у NED, баро/GNSS", 395, 130, 185, 330, "#f0fdf4", "#86efac"),
        ("КУТОВИЙ КОНТУР (100–400 Гц)", "Кути орієнтації [крен φ, тангаж θ, курс ψ], горизонт", 595, 160, 185, 300, "#fefce8", "#fde047"),
        ("ШВИДКІСНИЙ КОНТУР (1–8 кГц)", "Кутові швидкості ω, PID-моменти, мікшер, мотори", 795, 190, 185, 270, "#fef2f2", "#fca5a5"),
    ]
    
    for title, desc, x, y, w, h, bg, border in tiers:
        p.append(rect(x, y, w, h, fill=bg, stroke=border, sw=2.0, rx=8))
        p.append(text(x + w / 2, y + 24, title, size=10.5, bold=True, color=INK))
        p.append(fitbox(x + 8, y + 36, w - 16, 42, desc, size=9.5, color=MUTED, fill=bg, stroke=bg))
    
    # 1. Наглядове керування (Supervisory) -> Місійний контур
    p.append(rect(205, 50, 165, 36, fill="#dbeafe", stroke=NEG, sw=1.5, rx=5))
    p.append(text(287, 66, "3. Наглядове (Supervisory)", size=10.5, bold=True, color=NEG))
    p.append(text(287, 78, "Ціль: вейпойнт [X,Y,Z]", size=9.5, color=INK))
    p.append(carrow(165, 220, 205, 68, NEG, "B", sw=2.0))
    p.append(carrow(287, 86, 287, 100, NEG, "B", sw=2.0))
    
    # 2. Підтримка / FBW (Assisted) -> Кутовий контур
    p.append(rect(605, 105, 165, 36, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=5))
    p.append(text(687, 121, "2. З підтримкою (FBW)", size=10.5, bold=True, color="#854d0e"))
    p.append(text(687, 133, "Ціль: кут нахилу / швидкість", size=9.5, color=INK))
    p.append(carrow(165, 245, 605, 123, "#ca8a04", "G", sw=2.0))
    p.append(carrow(687, 141, 687, 160, "#ca8a04", "G", sw=2.0))
    
    # 3. Пряме керування (Direct Manual / Acro) -> Швидкісний контур
    p.append(rect(805, 140, 165, 36, fill="#fee2e2", stroke=POS, sw=1.5, rx=5))
    p.append(text(887, 156, "1. Пряме (Acro / Rate)", size=10.5, bold=True, color=POS))
    p.append(text(887, 168, "Ціль: швидкість ω / момент", size=9.5, color=INK))
    p.append(carrow(165, 270, 805, 158, POS, "R", sw=2.0))
    p.append(carrow(887, 176, 887, 190, POS, "R", sw=2.0))
    
    # Внутрішній каскад між контурами автопілота
    p.append(carrow(287, 240, 395, 240, INK, "G", sw=1.8))
    p.append(text(341, 230, "швидкість", size=9.5, color=MUTED))
    
    p.append(carrow(487, 280, 595, 280, INK, "G", sw=1.8))
    p.append(text(541, 270, "кут", size=9.5, color=MUTED))
    
    p.append(carrow(687, 320, 795, 320, INK, "G", sw=1.8))
    p.append(text(741, 310, "швидкість ω", size=9.5, color=MUTED))
    
    # Зворотні зв'язки від давачів
    p.append(line(887, 430, 887, 480, color=MUTED, sw=1.5, dash="4,3"))
    p.append(line(887, 480, 287, 480, color=MUTED, sw=1.5, dash="4,3"))
    p.append(carrow(287, 480, 287, 460, MUTED, "B", sw=1.5))
    p.append(text(587, 495, "Зворотний зв'язок: гіроскоп (1–8 кГц) → IMU (400 Гц) → GNSS/баро (50 Гц)", size=11, color=MUTED))
    
    return render(os.path.join(OUT, "paradigm-hierarchy.svg"), W, H, *p)


def fig_latency_vs_cognitive():
    W, H = 940, 480
    p = [COL_MARKERS]
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff"))
    
    p.append(text(W / 2, 28, "Компроміс: допустима затримка лінка проти когнітивного навантаження", size=16, bold=True))
    
    ox, oy = 120, 410
    gw, gh = 750, 340
    
    # Осі
    p.append(line(ox, oy, ox + gw, oy, color=LINE, sw=2))
    p.append(line(ox, oy, ox, oy - gh, color=LINE, sw=2))
    
    # Стрілки осей
    p.append(arrow(ox + gw - 10, oy, ox + gw, oy, color=LINE, sw=2))
    p.append(arrow(ox, oy - gh + 10, ox, oy - gh, color=LINE, sw=2))
    
    # Підписи осей
    p.append(text(ox + gw / 2, oy + 42, "Допустима затримка каналу зв'язку (RTT / Latency, логарифмічна шкала)", size=12, bold=True))
    p.append(text(ox - 65, oy - gh / 2, "Когнітивне навантаження / темп дій", size=12, bold=True, anchor="middle"))
    
    # Поділки X
    x_ticks = [
        (ox + 45, "10 мс"),
        (ox + 155, "30 мс"),
        (ox + 285, "100 мс"),
        (ox + 425, "500 мс"),
        (ox + 565, "2 с"),
        (ox + 695, "10+ с"),
    ]
    for xt, lab in x_ticks:
        p.append(line(xt, oy, xt, oy + 5, color=LINE, sw=1.5))
        p.append(text(xt, oy + 20, lab, size=11, color=MUTED))
        p.append(line(xt, oy, xt, oy - gh, color="#f1f5f9", sw=1, dash="3,3"))
        
    # Поділки Y
    y_ticks = [
        (oy - 50, "Стратегічний нагляд (0.05 Гц)"),
        (oy - 140, "Тактичне коригування (0.5 Гц)"),
        (oy - 230, "Динамічне стеження (2 Гц)"),
        (oy - 310, "Рефлекторна стабілізація (10 Гц)"),
    ]
    for yt, lab in y_ticks:
        p.append(line(ox - 5, yt, ox, yt, color=LINE, sw=1.5))
        p.append(text(ox - 10, yt + 4, lab, size=10.5, color=MUTED, anchor="end"))
        p.append(line(ox, yt, ox + gw, yt, color="#f1f5f9", sw=1, dash="3,3"))
        
    # Зона 1: Acro / Direct Manual
    p.append(rect(ox + 15, oy - 330, 160, 310, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(ox + 95, oy - 305, "ПРЯМЕ РУЧНЕ (ACRO)", size=11, bold=True, color=POS))
    p.append(text(ox + 95, oy - 285, "Людина в контурі моменту", size=10, color=INK))
    p.append(text(ox + 95, oy - 265, "Лаг > 50–80 мс = аварія", size=10, bold=True, color=POS))
    p.append(text(ox + 95, oy - 80, "Критично до джитера", size=9.5, color=MUTED))
    
    # Зона 2: Fly-by-Wire / Assisted
    p.append(rect(ox + 195, oy - 250, 200, 230, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=6))
    p.append(text(ox + 295, oy - 225, "З ПІДТРИМКОЮ (FBW)", size=11, bold=True, color="#854d0e"))
    p.append(text(ox + 295, oy - 205, "Автовирівнювання, ліміти кутів", size=10, color=INK))
    p.append(text(ox + 295, oy - 185, "Стійке до лагу 100–300 мс", size=10, bold=True, color="#854d0e"))
    p.append(text(ox + 295, oy - 60, "Відпустив стік — завис", size=9.5, color=MUTED))
    
    # Зона 3: Supervisory Control
    p.append(rect(ox + 415, oy - 160, 320, 140, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(ox + 575, oy - 135, "НАГЛЯДОВЕ (SUPERVISORY)", size=11, bold=True, color=NEG))
    p.append(text(ox + 575, oy - 115, "Маршрутні точки, інспекції, Click-to-Go", size=10, color=INK))
    p.append(text(ox + 575, oy - 95, "Стійке до лагів від секунд до годин", size=10, bold=True, color=NEG))
    p.append(text(ox + 575, oy - 45, "Автономне виконання на борту", size=9.5, color=MUTED))
    
    # Межа розгойдування оператором (PIO boundary)
    p.append(line(ox + 180, oy, ox + 180, oy - 330, color=POS, sw=2, dash="4,4"))
    p.append(text(ox + 180, oy - 335, "Поріг PIO (розгойдування)", size=10, color=POS, bold=True))
    
    return render(os.path.join(OUT, "latency-vs-cognitive-load.svg"), W, H, *p)


def fig_bumpless_transfer():
    W, H = 940, 460
    p = [COL_MARKERS]
    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#ffffff"))
    
    p.append(text(W / 2, 28, "Безударне перемикання парадигм керування (Bumpless Transfer)", size=16, bold=True))
    
    # Ліва колонка: без вирівнювання (стрибок)
    p.append(rect(40, 60, 410, 360, fill="#fff1f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(245, 90, "БЕЗ БЕЗУДАРНОГО ПЕРЕХОДУ (КРАХ)", size=13, bold=True, color=POS))
    p.append(text(245, 110, "Стрибок уставки й застарілий інтегратор PID", size=10.5, color=MUTED))
    
    # Графік зліва
    lx, ly = 80, 360
    lw, lh = 330, 200
    p.append(line(lx, ly, lx + lw, ly, color=LINE, sw=1.5))
    p.append(line(lx, ly, lx, ly - lh, color=LINE, sw=1.5))
    p.append(line(lx + 150, ly, lx + 150, ly - lh, color=POS, sw=1.5, dash="3,3"))
    p.append(text(lx + 150, ly - lh - 10, "Перемикання режиму", size=10, color=POS, bold=True))
    
    # Траєкторія зі стрибком
    p.append('<path d="M %d %d L %d %d L %d %d L %d %d L %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' % 
             (lx, ly - 60, lx + 150, ly - 60, lx + 150, ly - 170, lx + 180, ly - 20, lx + 220, ly - 150, lx + 300, ly - 30, POS))
    p.append(text(lx + 70, ly - 70, "Автопілот (5 м/с)", size=10, color=MUTED))
    p.append(text(lx + 230, ly - 180, "Ударний ривок / зрив", size=10.5, bold=True, color=POS))
    
    # Права колонка: з безударним переходом
    p.append(rect(490, 60, 410, 360, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(695, 90, "З БЕЗУДАРНИМ ПЕРЕХОДОМ (НОРМА)", size=13, bold=True, color=FIELD))
    p.append(text(695, 110, "Синхронізація інтегратора, плавний рамп уставки", size=10.5, color=MUTED))
    
    # Графік справа
    rx, ry = 530, 360
    rw, rh = 330, 200
    p.append(line(rx, ry, rx + rw, ry, color=LINE, sw=1.5))
    p.append(line(rx, ry, rx, ry - rh, color=LINE, sw=1.5))
    p.append(line(rx + 150, ry, rx + 150, ry - rh, color=FIELD, sw=1.5, dash="3,3"))
    p.append(text(rx + 150, ry - rh - 10, "Перемикання режиму", size=10, color=FIELD, bold=True))
    
    # Траєкторія плавна
    p.append('<path d="M %d %d L %d %d C %d %d, %d %d, %d %d L %d %d" fill="none" stroke="%s" stroke-width="2.5"/>' % 
             (rx, ry - 60, rx + 150, ry - 60, rx + 180, ry - 60, rx + 220, ry - 110, rx + 260, ry - 110, rx + 300, ry - 110, FIELD))
    p.append(text(rx + 70, ry - 70, "Автопілот (5 м/с)", size=10, color=MUTED))
    p.append(text(rx + 240, ry - 125, "Плавний перехід на стік", size=10.5, bold=True, color=FIELD))
    
    return render(os.path.join(OUT, "bumpless-transfer.svg"), W, H, *p)


if __name__ == "__main__":
    fig_paradigm_hierarchy()
    fig_latency_vs_cognitive()
    fig_bumpless_transfer()
    print("Figures generated successfully.")
