# -*- coding: utf-8 -*-
import sys, os
# 4 levels up to reach scripts/ in repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def polygon(points, fill=FILL, stroke=LINE, sw=1.5):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (pts, fill, stroke, sw)

def path(d, fill="none", stroke=LINE, sw=1.5):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>' % (d, fill, stroke, sw)

def circle(cx, cy, r, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (cx, cy, r, fill, stroke, sw, d))

def rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.5, rx=6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (x, y, w, h, rx, fill, stroke, sw, d))

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. mlcc-flex-crack-mechanism: Стандартний MLCC vs Soft-Termination під вигином ──
def fig_flex_crack_mechanism():
    W, H = 840, 430
    p = []

    # Фон лівої панелі (Стандартний MLCC)
    p.append(rect(15, 45, 395, 370, fill="#fdfaf8", stroke="#e2e8f0", sw=1.2, rx=8))
    p.append(text(212, 70, "Стандартний MLCC (жорстка металізація)", size=13, color=POS, bold=True))
    p.append(text(212, 88, "Механічний вигин плати → тріщина під кутом 45° → коротке замикання", size=9, color=MUTED))

    # Вигнута плата ліворуч (зелена FR-4)
    p.append(rect(35, 330, 355, 14, fill="#2e7d32", stroke="#1b5e20", sw=1.5, rx=2))
    p.append(text(212, 341, "FR-4 друкована плата (розтягнення поверхні)", size=9, color="#ffffff", bold=True))
    # Стрілки розтягнення плати
    p.append(arrow(110, 360, 60, 360, color=POS, sw=1.8))
    p.append(arrow(315, 360, 365, 360, color=POS, sw=1.8))
    p.append(text(212, 363, "Зусилля розтягу поверхні σ_розт", size=9, color=POS, bold=True))

    # Мідні контактні майданчики
    p.append(rect(70, 322, 65, 8, fill="#d97706", stroke="#b45309", sw=1.2, rx=1))
    p.append(rect(290, 322, 65, 8, fill="#d97706", stroke="#b45309", sw=1.2, rx=1))

    # Тіло конденсатора (кераміка)
    cx1, cy1 = 212, 230
    cw, ch = 190, 85
    term_w = 28
    # Керамічна серцевина
    p.append(rect(cx1 - cw/2 + term_w, cy1 - ch/2, cw - 2*term_w, ch, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=0))
    p.append(text(cx1, cy1 - 22, "Керамічне тіло BaTiO₃ (крихке)", size=10, color="#92400e", bold=True))

    # Внутрішні електроди (чергування)
    for i in range(-2, 3):
        ey = cy1 + i * 11
        p.append(line(cx1 - cw/2 + term_w, ey, cx1 + 25, ey, color="#475569", sw=1.6))
        p.append(line(cx1 - 25, ey + 5.5, cx1 + cw/2 - term_w, ey + 5.5, color="#475569", sw=1.6))

    # Жорсткі металеві виводи (Cu/Ni/Sn)
    p.append(rect(cx1 - cw/2, cy1 - ch/2, term_w, ch, fill="#94a3b8", stroke="#475569", sw=1.2, rx=2))
    p.append(rect(cx1 + cw/2 - term_w, cy1 - ch/2, term_w, ch, fill="#94a3b8", stroke="#475569", sw=1.2, rx=2))

    # Галтель припою (жорсткий якір)
    p.append(polygon([(70, 322), (cx1 - cw/2, cy1 + 15), (cx1 - cw/2 + 20, cy1 + ch/2), (135, 322)],
                     fill="#cbd5e1", stroke="#64748b", sw=1.2))
    p.append(polygon([(355, 322), (cx1 + cw/2, cy1 + 15), (cx1 + cw/2 - 20, cy1 + ch/2), (290, 322)],
                     fill="#cbd5e1", stroke="#64748b", sw=1.2))

    # Тріщина 45 градусів (червона лінія)
    p.append(line(cx1 - cw/2 + term_w, cy1 + ch/2, cx1 - cw/2 + term_w + 45, cy1 - 10, color=POS, sw=2.4))
    p.append(circle(cx1 - cw/2 + term_w + 45, cy1 - 10, 4, fill=POS, stroke=POS))
    p.append(text(cx1 - cw/2 + term_w + 65, cy1 + 8, "Тріщина 45°", size=10, color=POS, bold=True))
    p.append(text(cx1 - cw/2 + term_w + 65, cy1 + 22, "перетинає протилежні електроди", size=9, color=POS))

    # Точка концентрації напруги
    p.append(arrow(cx1 - cw/2 - 20, cy1 + ch/2 + 25, cx1 - cw/2 + 5, cy1 + ch/2 + 2, color=POS, sw=1.5))
    p.append(text(cx1 - cw/2 - 20, cy1 + ch/2 + 35, "Точка концентрації напруги", size=9, color=POS, bold=True))

    # Підсумок ліворуч
    p.append(rect(25, 385, 375, 24, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=4))
    p.append(text(212, 401, "Підсумок: проникнення вологи → дендрити Ni/Cu → КЗ і пожежа", size=9, color=POS, bold=True))


    # Фон правої панелі (Soft-Termination)
    p.append(rect(430, 45, 395, 370, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=8))
    p.append(text(627, 70, "Soft-Termination (еластичний шар)", size=13, color=FIELD, bold=True))
    p.append(text(627, 88, "Струмопровідний полімер поглинає зсувні напруження → кераміка ціла", size=9, color=MUTED))

    # Плата праворуч
    p.append(rect(450, 330, 355, 14, fill="#2e7d32", stroke="#1b5e20", sw=1.5, rx=2))
    p.append(text(627, 341, "FR-4 друкована плата (вигин 5–10 мм)", size=9, color="#ffffff", bold=True))
    p.append(arrow(525, 360, 475, 360, color=FIELD, sw=1.8))
    p.append(arrow(730, 360, 780, 360, color=FIELD, sw=1.8))
    p.append(text(627, 363, "Еластична компенсація зсуву", size=9, color=FIELD, bold=True))

    # Контактні майданчики праворуч
    p.append(rect(485, 322, 65, 8, fill="#d97706", stroke="#b45309", sw=1.2, rx=1))
    p.append(rect(705, 322, 65, 8, fill="#d97706", stroke="#b45309", sw=1.2, rx=1))

    # Тіло конденсатора праворуч
    cx2 = 627
    # Керамічна серцевина
    p.append(rect(cx2 - cw/2 + term_w, cy1 - ch/2, cw - 2*term_w, ch, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=0))
    p.append(text(cx2, cy1 - 22, "Керамічне тіло BaTiO₃ (захищене)", size=10, color="#92400e", bold=True))

    # Внутрішні електроди праворуч
    for i in range(-2, 3):
        ey = cy1 + i * 11
        p.append(line(cx2 - cw/2 + term_w, ey, cx2 + 25, ey, color="#475569", sw=1.6))
        p.append(line(cx2 - 25, ey + 5.5, cx2 + cw/2 - term_w, ey + 5.5, color="#475569", sw=1.6))

    # 4-шарові виводи праворуч (Cu + Ag-Epoxy + Ni/Sn)
    # Лівий вивід (складається з 3 смуг)
    p.append(rect(cx2 - cw/2 + term_w - 6, cy1 - ch/2, 6, ch, fill="#b45309", stroke="#78350f", sw=1, rx=0))
    p.append(rect(cx2 - cw/2 + term_w - 18, cy1 - ch/2, 12, ch, fill="#10b981", stroke="#047857", sw=1.2, rx=0))
    p.append(rect(cx2 - cw/2, cy1 - ch/2, term_w - 18, ch, fill="#94a3b8", stroke="#475569", sw=1.2, rx=1))

    # Правий вивід (складається з 3 смуг)
    p.append(rect(cx2 + cw/2 - term_w, cy1 - ch/2, 6, ch, fill="#b45309", stroke="#78350f", sw=1, rx=0))
    p.append(rect(cx2 + cw/2 - term_w + 6, cy1 - ch/2, 12, ch, fill="#10b981", stroke="#047857", sw=1.2, rx=0))
    p.append(rect(cx2 + cw/2 - term_w + 18, cy1 - ch/2, term_w - 18, ch, fill="#94a3b8", stroke="#475569", sw=1.2, rx=1))

    # Галтель припою праворуч
    p.append(polygon([(485, 322), (cx2 - cw/2, cy1 + 15), (cx2 - cw/2 + 20, cy1 + ch/2), (550, 322)],
                     fill="#cbd5e1", stroke="#64748b", sw=1.2))
    p.append(polygon([(770, 322), (cx2 + cw/2, cy1 + 15), (cx2 + cw/2 - 20, cy1 + ch/2), (705, 322)],
                     fill="#cbd5e1", stroke="#64748b", sw=1.2))

    # Позначення полімерного шару зі стрілкою
    p.append(arrow(cx2 - cw/2 - 35, cy1 - 2, cx2 - cw/2 + term_w - 12, cy1 + 10, color=FIELD, sw=1.5))
    p.append(text(cx2 - cw/2 - 35, cy1 - 8, "Шар Ag-епоксиду", size=9, color=FIELD, bold=True))
    p.append(text(cx2 - cw/2 - 35, cy1 + 4, "деформується на зсув", size=9, color=FIELD))

    # Тіло без тріщин
    p.append(text(cx2 + 10, cy1 + 15, "✓ Напруження не досягають", size=9, color=FIELD, bold=True))
    p.append(text(cx2 + 10, cy1 + 28, "межі міцності кераміки", size=9, color=MUTED))

    # Підсумок праворуч
    p.append(rect(440, 385, 375, 24, fill="#dcfce7", stroke="#86efac", sw=1, rx=4))
    p.append(text(627, 401, "Підсумок: стійкість до вигину 5–10 мм (AEC-Q200), повна безпека кіл", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "mlcc-flex-crack-mechanism.svg"), W, H, *p,
           title="Механізм утворення флекс-тріщини та захисна дія Soft-Termination")


# ── 2. soft-term-layer-structure: Будова металізації виводу з полімерним демпфером ──
def fig_soft_term_layers():
    W, H = 800, 390
    p = []

    p.append(rect(15, 45, 770, 330, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=8))
    p.append(text(400, 70, "Мікроструктура та пошарова металізація виводу Soft-Termination", size=14, color=INK, bold=True))
    p.append(text(400, 88, "Послідовність шарів від внутрішнього електрода до паяного з'єднання", size=10, color=MUTED))

    # Шари у вигляді вертикальних смуг зліва направо
    x0, y0, h0 = 50, 115, 185

    # 1. Кераміка з електродами
    w1 = 145
    p.append(rect(x0, y0, w1, h0, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=0))
    p.append(text(x0 + w1/2, y0 + 30, "Керамічне тіло", size=11, color="#92400e", bold=True))
    p.append(text(x0 + w1/2, y0 + 48, "BaTiO₃ (E ≈ 120 ГПа)", size=9, color=MUTED))
    # Внутрішні нікелеві електроди
    for ey in [y0 + 75, y0 + 110, y0 + 145]:
        p.append(line(x0, ey, x0 + w1, ey, color="#475569", sw=2.5))
        p.append(text(x0 + w1/2, ey - 6, "Внутрішній електрод Ni", size=9, color="#334155"))

    # 2. Базова металізація Cu / Ag
    x1 = x0 + w1
    w2 = 70
    p.append(rect(x1, y0, w2, h0, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=0))
    p.append(text(x1 + w2/2, y0 + 45, "Базовий шар", size=10, color="#9a3412", bold=True))
    p.append(text(x1 + w2/2, y0 + 62, "Cu / Ag", size=10, color="#9a3412", bold=True))
    p.append(text(x1 + w2/2, y0 + 90, "Спечений", size=9, color="#9a3412"))
    p.append(text(x1 + w2/2, y0 + 104, "склофритом", size=9, color="#9a3412"))
    p.append(text(x1 + w2/2, y0 + 138, "Товщина:", size=9, color=MUTED))
    p.append(text(x1 + w2/2, y0 + 152, "10–25 мкм", size=9, color=INK, bold=True))

    # 3. Еластичний шар Soft-Termination (Ag-Epoxy)
    x2 = x1 + w2
    w3 = 115
    p.append(rect(x2, y0, w3, h0, fill="#a7f3d0", stroke="#059669", sw=2, rx=0))
    p.append(text(x2 + w3/2, y0 + 35, "Soft-Termination", size=11, color="#065f46", bold=True))
    p.append(text(x2 + w3/2, y0 + 52, "Провідний полімер", size=10, color="#065f46", bold=True))
    p.append(text(x2 + w3/2, y0 + 80, "Епоксидна смола", size=9, color="#065f46"))
    p.append(text(x2 + w3/2, y0 + 95, "+ 75–85% Ag-лусочок", size=9, color="#065f46", bold=True))
    p.append(text(x2 + w3/2, y0 + 125, "E ≈ 2–5 ГПа (еластичн.)", size=9, color="#065f46"))
    p.append(text(x2 + w3/2, y0 + 148, "Товщина: 10–30 мкм", size=9, color="#065f46", bold=True))

    # 4. Бар'єрний шар нікелю Ni
    x3 = x2 + w3
    w4 = 65
    p.append(rect(x3, y0, w4, h0, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=0))
    p.append(text(x3 + w4/2, y0 + 45, "Бар'єр Ni", size=10, color="#1e293b", bold=True))
    p.append(text(x3 + w4/2, y0 + 72, "Гальванічний", size=9, color="#334155"))
    p.append(text(x3 + w4/2, y0 + 88, "нікель", size=9, color="#334155"))
    p.append(text(x3 + w4/2, y0 + 120, "Захист від", size=9, color="#334155"))
    p.append(text(x3 + w4/2, y0 + 135, "розчинення", size=9, color="#334155"))
    p.append(text(x3 + w4/2, y0 + 158, "2–5 мкм", size=9, color=INK, bold=True))

    # 5. Зовнішній шар олова Sn
    x4 = x3 + w4
    w5 = 65
    p.append(rect(x4, y0, w5, h0, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=0))
    p.append(text(x4 + w5/2, y0 + 45, "Шар Sn", size=10, color="#1e293b", bold=True))
    p.append(text(x4 + w5/2, y0 + 72, "Матове", size=9, color="#334155"))
    p.append(text(x4 + w5/2, y0 + 88, "чисте олово", size=9, color="#334155"))
    p.append(text(x4 + w5/2, y0 + 120, "Забезпечує", size=9, color="#334155"))
    p.append(text(x4 + w5/2, y0 + 135, "паяність", size=9, color="#334155"))
    p.append(text(x4 + w5/2, y0 + 158, "3–8 мкм", size=9, color=INK, bold=True))

    # 6. Паяний шов (SAC305)
    x5 = x4 + w5
    w6 = 185
    p.append(rect(x5, y0, w6, h0, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=0))
    p.append(text(x5 + w6/2, y0 + 35, "Паяне з'єднання", size=11, color="#334155", bold=True))
    p.append(text(x5 + w6/2, y0 + 52, "Припій SAC305 (Sn-Ag-Cu)", size=9, color=MUTED))
    p.append(text(x5 + w6/2, y0 + 85, "E_припою ≈ 40–50 ГПа", size=9, color="#334155"))
    p.append(text(x5 + w6/2, y0 + 110, "CTE_FR4 ≈ 15–17 ppm/K", size=9, color=POS, bold=True))
    p.append(text(x5 + w6/2, y0 + 128, "CTE_кераміки ≈ 9–10 ppm/K", size=9, color="#92400e", bold=True))
    p.append(text(x5 + w6/2, y0 + 158, "Δα створює термоциклічний зсув", size=9, color=MUTED))

    # Стрілка зсуву внизу
    p.append(rect(30, 315, 740, 48, fill="#edf2f7", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(400, 333, "Механізм передачі напруження: Паяний шов тягне олово/нікель → Епоксидний шар еластично зсувається (τ = G·γ)", size=9, color=INK, bold=True))
    p.append(text(400, 350, "Зниження напруження на межі кераміки у 3–5 разів порівняно з жорстким трьохшаровим виводом", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "soft-term-layer-structure.svg"), W, H, *p,
           title="Пошарова структура виводу Soft-Termination конденсатора")


# ── 3. failsafe-internal-architectures: Архітектури безпеки (Standard vs Open-Mode vs Floating) ──
def fig_failsafe_architectures():
    W, H = 840, 460
    p = []

    p.append(rect(15, 40, 810, 405, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=8))
    p.append(text(420, 65, "Порівняння внутрішніх електродних архітектур безпеки MLCC", size=14, color=INK, bold=True))
    p.append(text(420, 83, "Поведінка компонентів при виникненні кутової тріщини від механічного вигину", size=10, color=MUTED))

    kw, kh = 380, 155
    coords = [
        (30, 100, "(a) Стандартна архітектура (Full Overlap)", POS),
        (430, 100, "(b) Open-Mode (Зміщена активна зона)", FIELD),
        (30, 270, "(c) Floating Electrode (Послідовний поділ)", "#2563eb"),
        (430, 270, "(d) Soft-Term + Floating (Подвійний захист)", "#7c3aed")
    ]

    # (a) Стандарт
    x, y, title, col = coords[0]
    p.append(rect(x, y, kw, kh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(x + kw/2, y + 20, title, size=11, color=col, bold=True))
    # Тіло: лівий термінал, кераміка, правий термінал (абутовані)
    p.append(rect(x + 50, y + 35, 25, 65, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(rect(x + 75, y + 35, 230, 65, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=0))
    p.append(rect(x + 305, y + 35, 25, 65, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    # Електроди доходять до країв
    p.append(line(x + 75, y + 55, x + 285, y + 55, color="#334155", sw=1.8))
    p.append(line(x + 95, y + 70, x + 305, y + 70, color="#334155", sw=1.8))
    p.append(line(x + 75, y + 85, x + 285, y + 85, color="#334155", sw=1.8))
    # Тріщина кутова перетинає зону перекриття
    p.append(line(x + 75, y + 98, x + 120, y + 42, color=POS, sw=2.2))
    p.append(text(x + 105, y + 48, "⚡ КЗ!", size=10, color=POS, bold=True))
    p.append(text(x + kw/2, y + 122, "Наслідок: тріщина ріже протилежні обкладки", size=9, color=POS, bold=True))
    p.append(text(x + kw/2, y + 138, "Результат: низькоомне КЗ, тепловий розгін, спалах плати", size=9, color=POS))

    # (b) Open-Mode
    x, y, title, col = coords[1]
    p.append(rect(x, y, kw, kh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(x + kw/2, y + 20, title, size=11, color=col, bold=True))
    p.append(rect(x + 50, y + 35, 25, 65, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(rect(x + 75, y + 35, 230, 65, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=0))
    p.append(rect(x + 305, y + 35, 25, 65, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    # Електроди відсунуті від країв
    p.append(line(x + 75, y + 55, x + 255, y + 55, color="#334155", sw=1.8))
    p.append(line(x + 125, y + 70, x + 305, y + 70, color="#334155", sw=1.8))
    p.append(line(x + 75, y + 85, x + 255, y + 85, color="#334155", sw=1.8))
    # Зона буфера (пунктирні лінії меж)
    p.append(line(x + 120, y + 35, x + 120, y + 100, color=FIELD, sw=1, dash="2,2"))
    p.append(text(x + 95, y + 46, "Буфер", size=9, color=FIELD, bold=True))
    # Тріщина проходить тільки через пасивну кераміку
    p.append(line(x + 75, y + 98, x + 115, y + 42, color=FIELD, sw=2.2))
    p.append(text(x + 145, y + 48, "✓ Обірвано", size=9, color=FIELD, bold=True))
    p.append(text(x + kw/2, y + 122, "Наслідок: тріщина проходить через пасивну зону без електродів", size=9, color=FIELD, bold=True))
    p.append(text(x + kw/2, y + 138, "Результат: безпечний обрив (Open-circuit), короткого замикання нема", size=9, color=FIELD))

    # (c) Floating Electrode
    x, y, title, col = coords[2]
    p.append(rect(x, y, kw, kh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(x + kw/2, y + 20, title, size=11, color=col, bold=True))
    p.append(rect(x + 50, y + 35, 25, 65, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(rect(x + 75, y + 35, 230, 65, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=0))
    p.append(rect(x + 305, y + 35, 25, 65, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    # Лівий, правий, плаваючий електроди
    p.append(line(x + 75, y + 55, x + 140, y + 55, color="#334155", sw=1.8))
    p.append(line(x + 240, y + 55, x + 305, y + 55, color="#334155", sw=1.8))
    p.append(line(x + 115, y + 70, x + 265, y + 70, color=col, sw=2.2))
    p.append(line(x + 75, y + 85, x + 140, y + 85, color="#334155", sw=1.8))
    p.append(line(x + 240, y + 85, x + 305, y + 85, color="#334155", sw=1.8))
    p.append(text(x + 190, y + 64, "Плаваючий острівець", size=9, color=col, bold=True))
    # Тріщина ліворуч
    p.append(line(x + 75, y + 98, x + 120, y + 42, color=col, sw=2.2))
    p.append(text(x + 105, y + 48, "C → 50%", size=9, color=col, bold=True))
    p.append(text(x + kw/2, y + 122, "Наслідок: послідовна пара конденсаторів C1-C2 усередині чіпа", size=9, color=col, bold=True))
    p.append(text(x + kw/2, y + 138, "Результат: при КЗ лівої половини права утримує напругу; C спадає на 50%", size=9, color=col))

    # (d) Soft-Term + Floating
    x, y, title, col = coords[3]
    p.append(rect(x, y, kw, kh, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(x + kw/2, y + 20, title, size=11, color=col, bold=True))
    # Виводи Soft-term
    p.append(rect(x + 50, y + 35, 14, 65, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(rect(x + 64, y + 35, 11, 65, fill="#10b981", stroke="#047857", sw=1, rx=0))
    p.append(rect(x + 75, y + 35, 230, 65, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=0))
    p.append(rect(x + 305, y + 35, 11, 65, fill="#10b981", stroke="#047857", sw=1, rx=0))
    p.append(rect(x + 316, y + 35, 14, 65, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    # Плаваючий електрод
    p.append(line(x + 75, y + 55, x + 140, y + 55, color="#334155", sw=1.8))
    p.append(line(x + 240, y + 55, x + 305, y + 55, color="#334155", sw=1.8))
    p.append(line(x + 115, y + 70, x + 265, y + 70, color=col, sw=2.2))
    p.append(line(x + 75, y + 85, x + 140, y + 85, color="#334155", sw=1.8))
    p.append(line(x + 240, y + 85, x + 305, y + 85, color="#334155", sw=1.8))
    p.append(text(x + 190, y + 64, "Soft-Term + Floating", size=9, color=col, bold=True))
    p.append(text(x + 105, y + 48, "🛡️ Захищено", size=9, color=col, bold=True))
    p.append(text(x + kw/2, y + 122, "Наслідок: полімер демпфує вигин + плаваючий електрод страхує", size=9, color=col, bold=True))
    p.append(text(x + kw/2, y + 138, "Результат: максимальна надійність для шин АКБ 12V/48V в автоелектроніці", size=9, color=col))

    render(os.path.join(OUT, "failsafe-internal-architectures.svg"), W, H, *p,
           title="Архітектури безпеки керамічних конденсаторів: Standard, Open-Mode, Floating")


# ── 4. aec-q200-bend-test-and-orientation: Випробування AEC-Q200-005 та правила трасування ──
def fig_bend_test_and_orientation():
    W, H = 840, 430
    p = []

    # Ліва панель: Стенд випробування AEC-Q200-005
    p.append(rect(15, 45, 395, 370, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=8))
    p.append(text(212, 70, "Випробування на вигин AEC-Q200-005", size=13, color=INK, bold=True))
    p.append(text(212, 88, "Тест на вигин плати (Substrate Bending Test)", size=10, color=MUTED))

    # Стенд: нижні опори
    p.append(rect(55, 270, 20, 45, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    p.append(rect(350, 270, 20, 45, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    p.append(text(65, 330, "Опора", size=9, color=MUTED))
    p.append(text(360, 330, "Опора", size=9, color=MUTED))

    # Відстань між опорами L = 90 мм
    p.append(line(65, 345, 360, 345, color=LINE, sw=1.2))
    p.append(line(65, 340, 65, 350, color=LINE, sw=1.2))
    p.append(line(360, 340, 360, 350, color=LINE, sw=1.2))
    p.append(text(212, 340, "Проліт L = 90 мм (або 100 мм)", size=9, color=INK, bold=True))

    # Вигнута плата FR-4
    p.append(path("M 65,270 Q 212,305 360,270", fill="none", stroke="#16a34a", sw=6))

    # Конденсатор у центрі знизу (абутовані прямокутники)
    p.append(rect(194, 298, 6, 14, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(rect(200, 298, 24, 14, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=0))
    p.append(rect(224, 298, 6, 14, fill="#94a3b8", stroke="#475569", sw=1, rx=0))

    # Пуансон (індентор) зверху
    p.append(polygon([(212, 255), (197, 215), (227, 215)], fill="#dc2626", stroke="#991b1b", sw=1.5))
    p.append(rect(202, 160, 20, 55, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=2))
    p.append(arrow(212, 130, 212, 155, color=POS, sw=2.5))
    p.append(text(212, 122, "Швидкість натискання 1.0 мм/с", size=9, color=POS, bold=True))

    # Стрілка прогину h
    p.append(line(265, 270, 265, 302, color=POS, sw=1.5))
    p.append(line(260, 270, 270, 270, color=POS, sw=1.5))
    p.append(line(260, 302, 270, 302, color=POS, sw=1.5))
    p.append(text(300, 288, "Прогин h", size=10, color=POS, bold=True))

    # Порівняння лімітів прогину
    p.append(rect(30, 365, 365, 36, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(212, 381, "Стандартний MLCC: межа h = 2.0 мм (ΔC/C₀ < 5%)", size=9, color=POS, bold=True))
    p.append(text(212, 395, "Soft-Termination MLCC: межа h = 5.0–10.0 мм (AEC-Q200)", size=9, color=FIELD, bold=True))


    # Права панель: Правила розміщення та трасування на PCB
    p.append(rect(430, 45, 395, 370, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, rx=8))
    p.append(text(627, 70, "Правила орієнтації на друкованій платі", size=13, color=INK, bold=True))
    p.append(text(627, 88, "Зменшення напружень при скрайбуванні та монтажі", size=10, color=MUTED))

    # Лінія зламу (V-cut / скрайбування)
    p.append(line(460, 115, 460, 340, color="#ef4444", sw=2, dash="4,4"))
    p.append(text(468, 125, "Лінія розлому / V-cut", size=9, color=POS, bold=True, anchor="start"))
    p.append(arrow(475, 220, 505, 220, color=POS, sw=1.5))
    p.append(text(515, 224, "Вигин", size=9, color=POS, bold=True, anchor="start"))

    # Варіант 1: Погана орієнтація (перпендикулярно лінії зламу)
    p.append(rect(510, 135, 125, 65, fill="#fee2e2", stroke="#fca5a5", sw=1.2, rx=4))
    p.append(text(572, 150, "НЕБЕЗПЕЧНО ✕", size=9, color=POS, bold=True))
    # Конденсатор перпендикулярно (абутований)
    p.append(rect(542, 160, 8, 22, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(rect(550, 160, 44, 22, fill="#fef3c7", stroke="#d97706", sw=1, rx=0))
    p.append(rect(594, 160, 8, 22, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(text(572, 193, "Перпендикулярно: макс. напруга", size=9, color=POS))

    # Варіант 2: Правильна орієнтація (паралельно лінії зламу)
    p.append(rect(655, 135, 125, 65, fill="#dcfce7", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(717, 150, "ПРАВИЛЬНО ✓", size=9, color=FIELD, bold=True))
    # Конденсатор паралельно (абутований)
    p.append(rect(705, 158, 24, 6, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(rect(705, 164, 24, 18, fill="#fef3c7", stroke="#d97706", sw=1, rx=0))
    p.append(rect(705, 182, 24, 6, fill="#94a3b8", stroke="#475569", sw=1, rx=0))
    p.append(text(717, 193, "Паралельно: мін. напруга", size=9, color=FIELD))

    # Варіант 3: Відстань від гвинтів кріплення
    p.append(rect(510, 240, 270, 95, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(circle(545, 280, 16, fill="#e2e8f0", stroke="#475569", sw=2))
    p.append(line(535, 280, 555, 280, color="#475569", sw=2))
    p.append(line(545, 270, 545, 290, color="#475569", sw=2))
    p.append(text(545, 310, "Гвинт", size=9, color=MUTED))

    # Зона заборони d >= 5-10 мм
    p.append(circle(545, 280, 32, fill="none", stroke=POS, sw=1.2, dash="3,3"))
    p.append(text(660, 260, "Keep-out zone: d ≥ 5–10 мм", size=9, color=POS, bold=True))
    p.append(text(660, 276, "від гвинтів, роз'ємів та кутів", size=9, color=MUTED))
    p.append(text(660, 295, "При закручуванні гвинта", size=9, color=INK))
    p.append(text(660, 308, "плата зазнає локального вигину", size=9, color=INK))

    # Підсумок у правій панелі
    p.append(rect(445, 365, 365, 36, fill="#edf2f7", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(627, 381, "Орієнтація паралельно осі вигину знижує напругу на 60–70%", size=9, color=FIELD, bold=True))
    p.append(text(627, 395, "Soft-Termination усуває ризик навіть у разі порушення зон безпеки", size=9, color=INK, bold=True))

    render(os.path.join(OUT, "aec-q200-bend-test-and-orientation.svg"), W, H, *p,
           title="Методика випробувань AEC-Q200-005 та правила компонування MLCC на друкованій платі")


if __name__ == "__main__":
    fig_flex_crack_mechanism()
    fig_soft_term_layers()
    fig_failsafe_architectures()
    fig_bend_test_and_orientation()
    print("Всі 4 фігури згенеровано успішно.")
