# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ═══════════════════════════════════════════════════════════════════════════
# Figure 1 — Спектральна чутливість ока V(λ) та ваги кольорів у яскравість
# ═══════════════════════════════════════════════════════════════════════════
def fig_spectral():
    W, H = 740, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Спектральна чутливість ока V(λ) та внесок кольорів у яскравість',
                  16, INK, 'middle', bold=True))

    # Ліва частина: крива V(λ)
    ox, oy = 60, 290
    gw, gh = 360, 220
    
    # Осі
    f.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.5))
    f.append(line(ox, oy, ox, oy - gh, color=LINE, sw=1.5))
    
    f.append(text(ox + gw / 2, oy + 36, 'Довжина хвилі λ (нм)', 12, INK, 'middle'))
    f.append(text(ox - 35, oy - gh / 2, 'V(λ)', 12, INK, 'middle', bold=True))

    # Сітка та мітки довжин хвиль
    ticks_x = [(400, '400'), (500, '500'), (555, '555'), (600, '600'), (700, '700')]
    for nm, lbl in ticks_x:
        px = ox + (nm - 380) / (740 - 380) * gw
        f.append(line(px, oy, px, oy + 4, color=MUTED, sw=1))
        f.append(line(px, oy, px, oy - gh, color='#e5e7eb', sw=1, dash='2,2'))
        f.append(text(px, oy + 18, lbl, 10, MUTED, 'middle'))

    # Крива V(λ) приблизно за Гаусом з піком на 555 нм
    pts = []
    for nm in range(380, 741, 5):
        px = ox + (nm - 380) / (740 - 380) * gw
        val = math.exp(-((nm - 555) ** 2) / (2 * 48 ** 2))
        py = oy - val * (gh - 20)
        pts.append((px, py))

    path_d = ["M %.1f %.1f" % pts[0]]
    for px, py in pts[1:]:
        path_d.append("L %.1f %.1f" % (px, py))
    
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(path_d), FIELD))

    # Точка піку 555 нм
    peak_x = ox + (555 - 380) / (740 - 380) * gw
    peak_y = oy - (gh - 20)
    f.append(circle(peak_x, peak_y, 4, fill=FIELD, stroke=INK, sw=1))
    f.append(text(peak_x, peak_y - 10, 'Пік 555 нм (зелений)', 11, FIELD, 'middle', bold=True))

    # Спектральні зони кольорів
    f.append(rect(ox + (400-380)/(740-380)*gw, oy - 12, (490-400)/(740-380)*gw, 10, fill='#3b82f6', stroke='none', rx=0))
    f.append(rect(ox + (490-380)/(740-380)*gw, oy - 12, (570-490)/(740-380)*gw, 10, fill='#22c55e', stroke='none', rx=0))
    f.append(rect(ox + (570-380)/(740-380)*gw, oy - 12, (700-570)/(740-380)*gw, 10, fill='#ef4444', stroke='none', rx=0))

    # Права частина: Порівняння внесків у яскравість (BT.601 vs BT.709)
    rx0 = 460
    f.append(text(rx0 + 120, 60, 'Внесок у яскравість Y', 14, INK, 'middle', bold=True))
    
    # Таблична рамка
    f.append(rect(rx0, 80, 250, 210, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    
    f.append(text(rx0 + 20, 105, 'Колір', 11, MUTED, 'start', bold=True))
    f.append(text(rx0 + 110, 105, 'BT.601 (SD)', 11, MUTED, 'middle', bold=True))
    f.append(text(rx0 + 195, 105, 'BT.709 (HD)', 11, MUTED, 'middle', bold=True))
    f.append(line(rx0 + 10, 115, rx0 + 240, 115, color=MUTED, sw=1))

    # Зелений
    f.append(rect(rx0 + 15, 128, 12, 12, fill='#22c55e', stroke=INK, sw=1, rx=2))
    f.append(text(rx0 + 35, 139, 'Зелений (G)', 12, INK, 'start'))
    f.append(text(rx0 + 110, 139, '58.7%', 12, INK, 'middle', bold=True))
    f.append(text(rx0 + 195, 139, '71.5%', 12, INK, 'middle', bold=True))

    # Червоний
    f.append(rect(rx0 + 15, 163, 12, 12, fill='#ef4444', stroke=INK, sw=1, rx=2))
    f.append(text(rx0 + 35, 174, 'Червоний (R)', 12, INK, 'start'))
    f.append(text(rx0 + 110, 174, '29.9%', 12, INK, 'middle', bold=True))
    f.append(text(rx0 + 195, 174, '21.3%', 12, INK, 'middle', bold=True))

    # Синій
    f.append(rect(rx0 + 15, 198, 12, 12, fill='#3b82f6', stroke=INK, sw=1, rx=2))
    f.append(text(rx0 + 35, 209, 'Синій (B)', 12, INK, 'start'))
    f.append(text(rx0 + 110, 209, '11.4%', 12, INK, 'middle', bold=True))
    f.append(text(rx0 + 195, 209, '7.2%', 12, INK, 'middle', bold=True))

    f.append(line(rx0 + 10, 225, rx0 + 240, 225, color=MUTED, sw=1))
    f.append(text(rx0 + 125, 250, 'Синій дає менше 12% яркості', 11, POS, 'middle', bold=True))
    f.append(text(rx0 + 125, 270, 'Зелений формує основу деталізації', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'spectral-sensitivity.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 2 — Розділення RGB на Y' (яскравість) та Cb, Cr (колірність)
# ═══════════════════════════════════════════════════════════════════════════
def fig_ycbcr_decomp():
    W, H = 740, 320
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Розділення кольорового сигналу RGB на яскравість Y\' та колірність Cb, Cr',
                  16, INK, 'middle', bold=True))

    # Вхідний RGB сигнал
    bx0, by0 = 40, 100
    f.append(rect(bx0, by0, 130, 140, fill='#f8fafc', stroke=LINE, sw=1.8, rx=8))
    f.append(text(bx0 + 65, by0 + 25, 'Сигнал RGB', 13, INK, 'middle', bold=True))
    
    f.append(rect(bx0 + 20, by0 + 45, 90, 22, fill='#ef4444', stroke='none', rx=3))
    f.append(text(bx0 + 65, by0 + 60, 'R (Red)', 11, '#ffffff', 'middle', bold=True))
    
    f.append(rect(bx0 + 20, by0 + 75, 90, 22, fill='#22c55e', stroke='none', rx=3))
    f.append(text(bx0 + 65, by0 + 90, 'G (Green)', 11, '#ffffff', 'middle', bold=True))
    
    f.append(rect(bx0 + 20, by0 + 105, 90, 22, fill='#3b82f6', stroke='none', rx=3))
    f.append(text(bx0 + 65, by0 + 120, 'B (Blue)', 11, '#ffffff', 'middle', bold=True))

    # Стрілка від RGB до Матриці
    f.append(arrow(bx0 + 130, by0 + 70, bx0 + 190, by0 + 70, color=LINE, sw=2))

    # Центр: Матричне перетворення
    mx0, my0 = 190, 75
    mw, mh = 250, 190
    f.append(rect(mx0, my0, mw, mh, fill='#eff6ff', stroke=NEG, sw=1.8, rx=8))
    f.append(text(mx0 + mw/2, my0 + 25, 'Матричне перетворення', 13, NEG, 'middle', bold=True))

    f.append(fitbox(mx0 + 15, my0 + 42, mw - 30, 42, 
                    'Y\' = 0.299·R\' + 0.587·G\' + 0.114·B\'', 
                    size=12, fill='#ffffff', stroke=LINE, bold=True, color=INK))
    
    f.append(fitbox(mx0 + 15, my0 + 90, mw - 30, 42, 
                    'Cb = 0.564·(B\' - Y\')', 
                    size=12, fill='#ffffff', stroke=LINE, bold=True, color='#2563eb'))
    
    f.append(fitbox(mx0 + 15, my0 + 138, mw - 30, 42, 
                    'Cr = 0.713·(R\' - Y\')', 
                    size=12, fill='#ffffff', stroke=LINE, bold=True, color='#dc2626'))

    # Стрілки виходу
    f.append(arrow(mx0 + mw, my0 + 35, mx0 + mw + 40, my0 + 35, color=INK, sw=2))
    f.append(arrow(mx0 + mw, my0 + 95, mx0 + mw + 40, my0 + 95, color='#2563eb', sw=2))
    f.append(arrow(mx0 + mw, my0 + 155, mx0 + mw + 40, my0 + 155, color='#dc2626', sw=2))

    # Вихідні канали
    ox0, oy0 = 480, 65
    ow, oh = 220, 50

    # Y' (Luma)
    f.append(rect(ox0, oy0, ow, oh, fill='#e2e8f0', stroke=INK, sw=1.8, rx=6))
    f.append(text(ox0 + 15, oy0 + 22, 'Y\' (Яскравість)', 13, INK, 'start', bold=True))
    f.append(text(ox0 + 15, oy0 + 39, 'Висока деталізація (100%)', 10, MUTED, 'start'))

    # Cb (Chroma Blue)
    f.append(rect(ox0, oy0 + 60, ow, oh, fill='#dbeafe', stroke='#2563eb', sw=1.8, rx=6))
    f.append(text(ox0 + 15, oy0 + 82, 'Cb (Різниця синього)', 13, '#1e40af', 'start', bold=True))
    f.append(text(ox0 + 15, oy0 + 99, 'Низька детальність (субдискретизація)', 10, MUTED, 'start'))

    # Cr (Chroma Red)
    f.append(rect(ox0, oy0 + 120, ow, oh, fill='#fee2e2', stroke='#dc2626', sw=1.8, rx=6))
    f.append(text(ox0 + 15, oy0 + 142, 'Cr (Різниця червоного)', 13, '#991b1b', 'start', bold=True))
    f.append(text(ox0 + 15, oy0 + 159, 'Низька детальність (субдискретизація)', 10, MUTED, 'start'))

    f.append(text(W / 2, H - 15, 'Яскравість Y\' зберігає структуру картинки; колірність Cb/Cr передає відтінок', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'ycbcr-decomposition.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Figure 3 — Схеми субдискретизації колірності (4:4:4, 4:2:2, 4:2:0)
# ═══════════════════════════════════════════════════════════════════════════
def fig_subsampling():
    W, H = 760, 330
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, 'Схеми субдискретизації колірності (Chroma Subsampling)',
                  16, INK, 'middle', bold=True))

    modes = [
        (45, '4:4:4', 'Повне розрізнення', '24 біт/піксель (100% зауважень)', '1 Y на 1 Cb/Cr'),
        (285, '4:2:2', 'Стиснення ×2 по горизонталі', '16 біт/піксель (економія 33%)', '2 Y на 1 Cb/Cr'),
        (525, '4:2:0', 'Стиснення ×2 H і ×2 V', '12 біт/піксель (економія 50%)', '4 Y на 1 Cb/Cr')
    ]

    pw, ph = 200, 220
    py0 = 65

    for px, title_str, sub_str, bit_str, ratio_str in modes:
        # Рамка режиму
        f.append(rect(px, py0, pw, ph, fill=FILL, stroke=LINE, sw=1.5, rx=8))
        f.append(text(px + pw/2, py0 + 22, title_str, 15, INK, 'middle', bold=True))
        f.append(text(px + pw/2, py0 + 38, sub_str, 10, MUTED, 'middle'))

        # Сітка 4x2 пікселів
        gx0, gy0 = px + 25, py0 + 50
        cs = 34

        if title_str == '4:4:4':
            for r in range(2):
                for c in range(4):
                    cx, cy = gx0 + c * cs, gy0 + r * cs
                    f.append(rect(cx, cy, cs - 2, cs - 2, fill='#ffffff', stroke=MUTED, sw=1, rx=3))
                    f.append(circle(cx + 10, cy + 16, 5, fill=INK, stroke='none'))
                    f.append(circle(cx + 23, cy + 16, 5, fill='#2563eb', stroke='none'))
        elif title_str == '4:2:2':
            for r in range(2):
                for c in range(4):
                    cx, cy = gx0 + c * cs, gy0 + r * cs
                    f.append(rect(cx, cy, cs - 2, cs - 2, fill='#ffffff', stroke=MUTED, sw=1, rx=3))
                    f.append(circle(cx + 16, cy + 16, 5, fill=INK, stroke='none'))
                for pair in range(2):
                    pcx = gx0 + pair * 2 * cs + cs
                    f.append(circle(pcx - 1, gy0 + r * cs + 25, 5, fill='#2563eb', stroke='none'))
        else:
            for r in range(2):
                for c in range(4):
                    cx, cy = gx0 + c * cs, gy0 + r * cs
                    f.append(rect(cx, cy, cs - 2, cs - 2, fill='#ffffff', stroke=MUTED, sw=1, rx=3))
                    f.append(circle(cx + 16, cy + 16, 5, fill=INK, stroke='none'))
            for block in range(2):
                bcx = gx0 + block * 2 * cs + cs
                bcy = gy0 + cs
                f.append(circle(bcx - 1, bcy - 1, 6, fill='#2563eb', stroke=INK, sw=1))

        f.append(line(px + 10, py0 + 135, px + pw - 10, py0 + 135, color=MUTED, sw=1))
        f.append(text(px + pw/2, py0 + 152, bit_str, 11, POS if '50%' in bit_str else INK, 'middle', bold=True))
        f.append(text(px + pw/2, py0 + 170, ratio_str, 10, MUTED, 'middle'))
        
        f.append(circle(px + 30, py0 + 195, 4, fill=INK, stroke='none'))
        f.append(text(px + 40, py0 + 198, 'Y (яскравість)', 9, INK, 'start'))
        f.append(circle(px + 120, py0 + 195, 4, fill='#2563eb', stroke='none'))
        f.append(text(px + 130, py0 + 198, 'Cb/Cr (колір)', 9, INK, 'start'))

    f.append(text(W / 2, H - 12, 'Формат 4:2:0 є стандартом у відео (JPEG, H.264, WebM) через невідчутність втрат для ока', 11, MUTED, 'middle'))

    render(os.path.join(IMG, 'chroma-subsampling.svg'), W, H, *f)


fig_spectral()
fig_ycbcr_decomp()
fig_subsampling()
print('Figures generated cleanly.')
