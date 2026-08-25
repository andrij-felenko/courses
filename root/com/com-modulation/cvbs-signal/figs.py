# -*- coding: utf-8 -*-
"""Фігури до теми «Композитний відеосигнал CVBS: рівні, тайминг, IRE».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.2):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (d, color, sw))


def hline(x1, x2, y, color=MUTED, sw=1.0, dash="4,4"):
    return line(x1, y, x2, y, color=color, sw=sw, dash=dash)


# ── фіг. 1: один рядок CVBS у шкалі IRE ────────────────────────────────────
def fig_cvbs_line_ire():
    W, H = 840, 440
    x0, x1 = 110, 780
    
    # y-координати для рівнів IRE
    # +100 IRE (Белый) = 90
    # +7.5 IRE (Педестал) = 225
    # 0 IRE (Гашение) = 240
    # -20 IRE (Нижняя буburst) = 270
    # -40 IRE (Синхро) = 300
    
    y_white = 90
    y_black_ped = 225
    y_blank = 240
    y_sync = 300
    
    parts = [
        # Сітка рівнів та текстові мітки ліворуч
        hline(x0, x1, y_white),
        text(x0 - 12, y_white + 4, "+100 IRE (+0.714 В)", size=11, color=NEG, anchor="end", bold=True),
        text(x1 + 10, y_white + 4, "Рівень білого", size=11, color=NEG, anchor="start"),
        
        hline(x0, x1, y_black_ped, color="#999999", dash="2,3"),
        text(x0 - 12, y_black_ped + 4, "+7.5 IRE (NTSC black)", size=10, color=MUTED, anchor="end"),
        
        hline(x0, x1, y_blank),
        text(x0 - 12, y_blank + 4, "0 IRE (0.000 В)", size=11, color=INK, anchor="end", bold=True),
        text(x1 + 10, y_blank + 4, "Рівень гасіння / PAL black", size=11, color=INK, anchor="start"),
        
        hline(x0, x1, y_sync),
        text(x0 - 12, y_sync + 4, "-40 IRE (-0.286 В)", size=11, color=POS, anchor="end", bold=True),
        text(x1 + 10, y_sync + 4, "Дно синхро (Sync tip)", size=11, color=POS, anchor="start"),
    ]
    
    # Генерація форми сигналу
    # Х-координати точок часових інтервалів:
    # Front Porch: 110 -> 145 (1.5 us)
    # Sync Pulse: 145 -> 220 (4.7 us)
    # Back Porch start: 220
    # Color Burst: 245 -> 325 (8-10 періодів синусоїди)
    # Back Porch end / Active Video start: 350
    # Active Video end: 740 (52.65 us)
    # Line end: 780
    
    pts = [(x0, y_blank), (145, y_blank), (145, y_sync), (220, y_sync), (220, y_blank), (245, y_blank)]
    
    # Color Burst (спалах 9 періодів синусоїди амплітудою +-20 IRE навколо 0 IRE)
    burst_n = 50
    for i in range(burst_n + 1):
        t = i / burst_n
        bx = 245 + (325 - 245) * t
        by = y_blank - 30 * math.sin(t * 9 * 2 * math.pi)
        pts.append((bx, by))
        
    pts.append((350, y_blank))
    
    # Active Video (яскравосний сходинковий рівень + модульована колірність)
    act_n = 120
    for i in range(act_n + 1):
        t = i / act_n
        ax = 350 + (740 - 350) * t
        # Яскравісний профіль (сходинки від темного до світлого)
        lum_v = 0.15 + 0.70 * t + 0.08 * math.sin(t * 5 * math.pi)
        lum_y = y_blank - lum_v * (y_blank - y_white)
        # Піднесуча хроми (амплітуда модулюється)
        chroma_a = 22 * math.sin(t * 3 * math.pi)
        chroma_y = chroma_a * math.sin(t * 45 * math.pi)
        pts.append((ax, lum_y + chroma_y))
        
    pts.append((740, y_blank))
    pts.append((x1, y_blank))
    
    parts.append(polyline(pts, color=NEG, sw=2.2))
    
    # Розмітка часових інтервалів знизу
    y_time = 350
    line_t = line(x0, y_time, x1, y_time, color=MUTED, sw=1.0)
    parts.append(line_t)
    
    # Вертикальні пунктири розділювачі зон
    for vx, label_str, w_str in [
        (145, "Передній майданчик", "1.5 мкс"),
        (220, "Синхроімпульс", "4.7 мкс"),
        (350, "Задній майданчик + Burst", "5.8 мкс"),
        (740, "Активне відео", "52.65 мкс"),
    ]:
        parts.append(hline(vx, vx, 360, color="#cccccc", dash="3,3"))
        
    # Текстові підписи зон таймінгу під графіком
    parts += [
        text(127, y_time + 20, "Front porch", size=10, color=INK),
        text(127, y_time + 34, "1.5 мкс", size=10, color=MUTED),
        
        text(182, y_sync + 18, "Sync pulse", size=10, color=POS, bold=True),
        text(182, y_sync + 30, "4.7 мкс", size=10, color=MUTED),
        
        text(285, y_blank - 55, "Color Burst (спалах)", size=10, color=POS, bold=True),
        text(285, y_blank - 42, "8-10 пер. (40 IRE p-p)", size=9, color=MUTED),
        
        text(285, y_time + 20, "Back porch", size=10, color=INK),
        text(285, y_time + 34, "5.8 мкс", size=10, color=MUTED),
        
        text(545, y_white - 18, "Активний рядок відео (Luminance + Chroma)", size=11, color=NEG, bold=True),
        text(545, y_time + 20, "Активне зображення", size=11, color=INK, bold=True),
        text(545, y_time + 34, "52.65 мкс (NTSC) / 52.0 мкс (PAL)", size=10, color=MUTED),
        
        text((x0 + x1) / 2, H - 12, "Повний рядок T_H = 63.555 мкс (NTSC) / 64.0 мкс (PAL)  →", size=11, color=INK, bold=True),
    ]
    
    render(os.path.join(IMG, "cvbs-line-ire.svg"), W, H, *parts)


# ── фіг. 2: структура кадрового інтервалу гасіння VBI ─────────────────────
def fig_vbi_structure():
    W, H = 840, 380
    x0, x1 = 90, 770
    
    parts = []
    
    # Панель А: Непарне поле (Field 1)
    y_a = 90
    parts.append(rect(x0 - 20, y_a - 40, W - 140, 110, fill="#f8f9fa", stroke="#d1d5db", sw=1.0))
    parts.append(text(x0 - 10, y_a - 24, "Поле 1 (Непарне): кадровий синхро збігається з початком рядка", size=11, color=INK, anchor="start", bold=True))
    
    # Рядки Панелі А: Pre-equalizing (3 рядки), Vertical Sync (3 рядки), Post-equalizing (3 рядки)
    # Змальовуємо імпульси 2*fH
    pts_a = [(x0, y_a)]
    cur_x = x0
    
    # 6 коротких зрівняльних імпульсів (2.3 us кожен, період 0.5 TH)
    for _ in range(6):
        pts_a.extend([(cur_x, y_a), (cur_x, y_a + 30), (cur_x + 15, y_a + 30), (cur_x + 15, y_a), (cur_x + 50, y_a)])
        cur_x += 50
        
    # 6 широких кадрових синхроімпульсів з прорізами (27 us, проріз 4.7 us)
    for _ in range(6):
        pts_a.extend([(cur_x, y_a), (cur_x, y_a + 30), (cur_x + 35, y_a + 30), (cur_x + 35, y_a), (cur_x + 50, y_a)])
        cur_x += 50
        
    # 6 коротких пост-зрівняльних імпульсів
    for _ in range(6):
        pts_a.extend([(cur_x, y_a), (cur_x, y_a + 30), (cur_x + 15, y_a + 30), (cur_x + 15, y_a), (cur_x + 50, y_a)])
        cur_x += 50
        
    parts.append(polyline(pts_a, color=POS, sw=2.0))
    
    # Позначки зон для Панелі А
    parts += [
        text(x0 + 75, y_a + 52, "Pre-equalizing (6 × 0.5T_H)", size=9, color=MUTED),
        text(x0 + 225, y_a + 52, "Serrated V-Sync (6 × 0.5T_H)", size=9, color=POS, bold=True),
        text(x0 + 375, y_a + 52, "Post-equalizing (6 × 0.5T_H)", size=9, color=MUTED),
    ]
    
    # Панель Б: Парне поле (Field 2) із зсувом на 0.5 TH
    y_b = 250
    parts.append(rect(x0 - 20, y_b - 40, W - 140, 110, fill="#f8f9fa", stroke="#d1d5db", sw=1.0))
    parts.append(text(x0 - 10, y_b - 24, "Поле 2 (Парне): кадровий синхро зсунутий на 0.5 T_H (піврядка)", size=11, color=INK, anchor="start", bold=True))
    
    # Зсув на 25px (0.5 TH)
    pts_b = [(x0, y_b), (x0 + 25, y_b)]
    cur_x = x0 + 25
    
    for _ in range(6):
        pts_b.extend([(cur_x, y_b), (cur_x, y_b + 30), (cur_x + 15, y_b + 30), (cur_x + 15, y_b), (cur_x + 50, y_b)])
        cur_x += 50
        
    for _ in range(6):
        pts_b.extend([(cur_x, y_b), (cur_x, y_b + 30), (cur_x + 35, y_b + 30), (cur_x + 35, y_b), (cur_x + 50, y_b)])
        cur_x += 50
        
    for _ in range(6):
        pts_b.extend([(cur_x, y_b), (cur_x, y_b + 30), (cur_x + 15, y_b + 30), (cur_x + 15, y_b), (cur_x + 50, y_b)])
        cur_x += 50
        
    parts.append(polyline(pts_b, color=NEG, sw=2.0))
    
    parts += [
        text(x0 + 100, y_b + 52, "Зсув 0.5 T_H дає чергування непарних і парних рядків у розгортці", size=10, color=NEG, bold=True),
        text((x0 + x1) / 2, H - 12, "Кадровий інтервал гасіння (VBI) зберігає захват PLL рядкової частоти 2×f_H", size=11, color=INK, bold=True),
    ]
    
    render(os.path.join(IMG, "vbi-structure.svg"), W, H, *parts)


# ── фіг. 3: спектральне переплетення Y і C ─────────────────────────────────
def fig_spectral_interleaving():
    W, H = 840, 360
    x0, x1 = 80, 760
    y_base = 280
    
    parts = [
        line(x0, y_base, x1 + 20, y_base, color=INK, sw=1.8),
        arrow(x1 + 20, y_base, x1 + 35, y_base, color=INK, sw=1.8),
        text(x1 + 40, y_base + 4, "Частота f", size=11, color=INK, anchor="start", bold=True),
    ]
    
    # Спектральні піки яскравості Y (синій колір) на кратних частотах k*fH
    # k = 0, 1, 2, ..., n
    y_peaks = [110, 190, 270, 350, 430, 510, 590, 670]
    for i, px in enumerate(y_peaks):
        # Пік Y
        h = 160 if i in (1, 2, 4) else (120 if i in (0, 3, 5) else 80)
        parts.append(line(px, y_base, px, y_base - h, color=NEG, sw=2.5))
        parts.append(circle(px, y_base - h, 3, fill=NEG, stroke=NEG))
        parts.append(text(px, y_base + 18, f"{i}·f_H", size=10, color=NEG))
        
    # Спектральні піки колірності C (червоний колір) на напівкратних частотах (m + 0.5)*fH
    c_peaks = [470, 550, 630, 710]
    for i, px in enumerate(c_peaks):
        h = 130 if i in (1, 2) else 90
        parts.append(line(px, y_base, px, y_base - h, color=POS, sw=2.5))
        parts.append(circle(px, y_base - h, 3, fill=POS, stroke=POS))
        
    # Маркери колірності
    parts.append(text(550, y_base - 145, "Піднесуча f_sc = (n + 0.5)·f_H", size=11, color=POS, bold=True))
    parts.append(text(550, y_base + 34, "Частота піднесучої колірності", size=10, color=POS))
    
    # Огинаюча гребінчастого фільтра (Comb Filter response)
    comb_pts = []
    for x_i in range(x0, x1, 5):
        # Періодична огинаюча з вузлами у k*fH та максимумами у (m+0.5)*fH
        phase = (x_i - 110) / 80.0 * math.pi
        comb_y = y_base - 180 + 40 * math.cos(2 * phase)
        comb_pts.append((x_i, comb_y))
        
    parts.append(polyline(comb_pts, color=FIELD, sw=1.5))
    
    parts += [
        text(270, y_base - 180, "Спектр яскравості Y (гармоніки k·f_H)", size=11, color=NEG, bold=True),
        text(630, y_base - 180, "Спектр колірності C (гармоніки (m+0.5)·f_H)", size=11, color=POS, bold=True),
        text(420, 50, "Гребінчастий фільтр (Comb Filter) розділяє Y і C за точками спектра", size=12, color=FIELD, bold=True),
        text((x0 + x1) / 2, H - 12, "Спектральне переплетення усуває взаємні завади та ефект 'dot crawl'", size=11, color=INK, bold=True),
    ]
    
    render(os.path.join(IMG, "spectral-interleaving.svg"), W, H, *parts)


if __name__ == '__main__':
    fig_cvbs_line_ire()
    fig_vbi_structure()
    fig_spectral_interleaving()
    print("Фігури CVBS успішно згенеровано.")
