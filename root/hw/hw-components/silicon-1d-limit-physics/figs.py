# -*- coding: utf-8 -*-
"""Генератор фігур для теми silicon-limit (Кремнієва межа: питомий опір і напруга пробою)."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG):
    os.makedirs(IMG)

def fig_silicon_limit_curve():
    """silicon-limit-curve.svg: Логарифмічний графік залежності питомого опору від напруги пробою."""
    w, h = 760, 500
    parts = []
    
    parts.append(text(w/2, 26, "Теоретичні межі питомого опору: Si, Superjunction, SiC та GaN", size=15, bold=True))
    
    # Координатна сітка
    x0, y0 = 90, 55
    gw, gh = 630, 380
    
    # Контур сітки без заливки
    parts.append(rect(x0, y0, gw, gh, fill="none", stroke="#bbbbbb", sw=1.2, rx=0))
    
    def vx(v):
        # log10(10)=1, log10(3000)=3.4771
        lv = math.log10(v)
        return x0 + (lv - 1.0) / (3.4771 - 1.0) * gw
        
    def ry(r):
        # log10(1e-4)=-4, log10(1e3)=3
        lr = math.log10(r)
        return y0 + gh - (lr - (-4.0)) / (3.0 - (-4.0)) * gh
        
    # Горизонтальні лінії сітки
    r_ticks = [
        (1e-4, "10⁻⁴"),
        (1e-3, "10⁻³ (1 мОм·см²)"),
        (1e-2, "10⁻²"),
        (1e-1, "10⁻¹ (100 мОм·см²)"),
        (1.0, "1"),
        (10.0, "10"),
        (100.0, "100"),
        (1000.0, "1000")
    ]
    for rval, rlbl in r_ticks:
        y = ry(rval)
        parts.append(line(x0, y, x0 + gw, y, color="#ebebeb", sw=1.0))
        parts.append(text(x0 - 8, y + 4, rlbl, size=11, color=MUTED, anchor="end"))
        
    # Вертикальні лінії сітки
    v_ticks = [
        (10, "10"),
        (30, "30"),
        (60, "60"),
        (100, "100"),
        (200, "200"),
        (400, "400"),
        (600, "600"),
        (1000, "1000"),
        (1700, "1700"),
        (3000, "3000")
    ]
    for vval, vlbl in v_ticks:
        x = vx(vval)
        parts.append(line(x, y0, x, y0 + gh, color="#ebebeb", sw=1.0))
        parts.append(text(x, y0 + gh + 18, vlbl, size=11, color=MUTED, anchor="middle"))
        
    parts.append(text(x0 + gw/2, y0 + gh + 38, "Напруга лавинного пробою V_BR [В] (логарифмічна шкала)", size=12, bold=True))
    parts.append(text(22, y0 + gh/2, "R_DS(on)·A [Ом·см²]", size=12, bold=True, anchor="middle"))
    
    # 1. Лінія 1D Silicon Limit: Rsp = 8.3e-9 * V^2.5
    pts_si = []
    for v in [15, 20, 30, 50, 100, 200, 400, 600, 1000, 1500, 2000]:
        r = 8.3e-9 * (v ** 2.5)
        if r <= 1000:
            pts_si.append((vx(v), ry(r)))
    path_si = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_si)
    parts.append(f'<path d="{path_si}" fill="none" stroke="{POS}" stroke-width="2.8"/>')
    
    # 2. Лінія Superjunction Silicon: Rsp = 1.3e-5 * V^1.32
    pts_sj = []
    for v in [100, 200, 400, 600, 800, 1000, 1200]:
        r = 1.3e-5 * (v ** 1.32)
        pts_sj.append((vx(v), ry(r)))
    path_sj = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_sj)
    parts.append(f'<path d="{path_sj}" fill="none" stroke="{FIELD}" stroke-width="2.6" stroke-dasharray="6,3"/>')
    
    # 3. Лінія 4H-SiC 1D Limit: Rsp = 1.7e-12 * V^2.5
    pts_sic = []
    for v in [50, 100, 200, 400, 650, 1200, 1700, 3000]:
        r = 1.7e-12 * (v ** 2.5)
        pts_sic.append((vx(v), ry(r)))
    path_sic = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_sic)
    parts.append(f'<path d="{path_sic}" fill="none" stroke="{NEG}" stroke-width="2.8"/>')
    
    # 4. Лінія GaN Limit: Rsp = 4.5e-13 * V^2.4
    pts_gan = []
    for v in [30, 60, 100, 200, 400, 650, 1000]:
        r = 4.5e-13 * (v ** 2.4)
        pts_gan.append((vx(v), ry(r)))
    path_gan = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_gan)
    parts.append(f'<path d="{path_gan}" fill="none" stroke="#8e44ad" stroke-width="2.6"/>')
    
    # Маркер робочої точки 600 В
    x600 = vx(600)
    parts.append(line(x600, y0, x600, y0 + gh, color="#e67e22", sw=1.5, dash="4,4"))
    parts.append(circle(x600, ry(8.3e-9 * (600**2.5)), 5, fill=POS, stroke="#ffffff", sw=1.5))
    parts.append(circle(x600, ry(1.3e-5 * (600**1.32)), 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    parts.append(circle(x600, ry(1.7e-12 * (600**2.5)), 5, fill=NEG, stroke="#ffffff", sw=1.5))
    parts.append(circle(x600, ry(4.5e-13 * (600**2.4)), 5, fill="#8e44ad", stroke="#ffffff", sw=1.5))
    
    # Підписи до кривих з чіткими координатами, щоб не було перетинів
    parts.append(fitbox(x0 + 20, y0 + 15, 230, 48, "1D Кремнієва межа (Si Limit)\nR_sp ∝ V_BR^2.5 (класичний n-epi)", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True))
    parts.append(fitbox(x0 + 270, y0 + 110, 220, 44, "Superjunction Si (CoolMOS)\nR_sp ∝ V_BR^1.3 (компенсація)", size=11, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))
    parts.append(fitbox(x0 + 380, y0 + 240, 190, 42, "4H-SiC 1D межа\n~400× нижче за Si", size=11, fill="#ebf5fb", stroke=NEG, color=NEG, bold=True))
    parts.append(fitbox(x0 + 30, y0 + 310, 190, 42, "GaN HEMT 2DEG межа\n~1000× нижче за Si", size=11, fill="#f4ecf7", stroke="#8e44ad", color="#8e44ad", bold=True))
    
    parts.append(fitbox(x600 - 65, y0 + 5, 130, 24, "Перетин 600 В", size=11, fill="#fef5e7", stroke="#e67e22", color="#d35400", bold=True))
    
    render(os.path.join(IMG, 'silicon-limit-curve.svg'), w, h, *parts)

def fig_drift_electrostatics():
    """drift-electrostatics.svg: Порівняння електростатики планарної дрейфової зони та суперпереходу."""
    w, h = 760, 430
    parts = []
    
    parts.append(text(w/2, 24, "Електростатика збіднення: планарна 1D-зона проти суперпереходу (Superjunction)", size=14, bold=True))
    
    # Ліва панель: 1D планарний прилад
    p1_x, p1_y, p1_w, p1_h = 25, 48, 345, 360
    parts.append(rect(p1_x, p1_y, p1_w, p1_h, fill="none", stroke="#bbbbbb", sw=1.2))
    parts.append(text(p1_x + p1_w/2, p1_y + 22, "Класичний 1D MOSFET (n-epi)", size=13, bold=True, color=POS))
    
    # Фізична структура ліворуч
    sx0, sy0 = p1_x + 15, p1_y + 40
    parts.append(rect(sx0, sy0, 120, 24, fill="#fdecea", stroke=POS, sw=1.2))
    parts.append(text(sx0 + 60, sy0 + 16, "p-body (витік)", size=10, bold=True, color=POS))
    
    parts.append(rect(sx0, sy0 + 24, 120, 135, fill="#fbfcfc", stroke="#7f8c8d", sw=1.2))
    parts.append(mtext(sx0 + 60, sy0 + 75, ["n-дрейфовий", "шар (n-epi)", "товщина W", "низьке N_D"], size=10, color=MUTED))
    
    parts.append(rect(sx0, sy0 + 159, 120, 24, fill="#ebf5fb", stroke=NEG, sw=1.2))
    parts.append(text(sx0 + 60, sy0 + 175, "n⁺ підкладка (стік)", size=10, bold=True, color=NEG))
    
    # Епюра поля E(x) ліворуч
    gx0, gy0 = p1_x + 155, sy0 + 24
    parts.append(line(gx0, gy0, gx0, gy0 + 135, color=LINE, sw=1.5))
    parts.append(line(gx0, gy0 + 135, gx0 + 150, gy0 + 135, color=LINE, sw=1.5))
    parts.append(text(gx0 + 145, gy0 + 150, "x", size=11, italic=True))
    parts.append(text(gx0 - 10, gy0 + 15, "E", size=11, italic=True))
    
    # Трикутний профіль
    parts.append(f'<polygon points="{gx0},{gy0+10} {gx0+130},{gy0+135} {gx0},{gy0+135}" fill="#fadbd8" stroke="{POS}" stroke-width="2.0"/>')
    parts.append(text(gx0 + 40, gy0 + 95, "V_BR", size=12, bold=True, color=POS))
    parts.append(text(gx0 + 18, gy0 + 8, "E_crit", size=10, bold=True, color=POS))
    parts.append(text(gx0 + 130, gy0 + 150, "W_1D", size=10, color=MUTED))
    
    # Підсумок формули ліворуч
    parts.append(fitbox(p1_x + 15, p1_y + 235, p1_w - 30, 110,
                        "Трикутний профіль поля:\n"
                        "• V_BR = 1/2 · E_crit · W_1D\n"
                        "• N_D ∝ 1 / V_BR (знижується)\n"
                        "• W_1D ∝ V_BR (росте)\n"
                        "➔ R_sp ∝ V_BR^2.5 (подвійний удар)",
                        size=11, fill="#ffffff", stroke="#d5dbdb", color=INK))

    # Права панель: Superjunction
    p2_x, p2_y, p2_w, p2_h = 390, 48, 345, 360
    parts.append(rect(p2_x, p2_y, p2_w, p2_h, fill="none", stroke="#bbbbbb", sw=1.2))
    parts.append(text(p2_x + p2_w/2, p2_y + 22, "Суперперехід (Superjunction)", size=13, bold=True, color=FIELD))
    
    # Фізична структура праворуч
    sx1, sy1 = p2_x + 15, p2_y + 40
    parts.append(rect(sx1, sy1, 120, 24, fill="#fdecea", stroke=POS, sw=1.2))
    parts.append(text(sx1 + 60, sy1 + 16, "p-body (витік)", size=10, bold=True, color=POS))
    
    # n- і p-стовпчики
    col_w = 30
    for i in range(4):
        cx = sx1 + i * col_w
        if i % 2 == 0:
            parts.append(rect(cx, sy1 + 24, col_w, 135, fill="#eafaf1", stroke=FIELD, sw=1.0))
            parts.append(text(cx + col_w/2, sy1 + 95, "n", size=12, bold=True, color=FIELD))
        else:
            parts.append(rect(cx, sy1 + 24, col_w, 135, fill="#fdecea", stroke=POS, sw=1.0))
            parts.append(text(cx + col_w/2, sy1 + 95, "p", size=12, bold=True, color=POS))
            
    parts.append(rect(sx1, sy1 + 159, 120, 24, fill="#ebf5fb", stroke=NEG, sw=1.2))
    parts.append(text(sx1 + 60, sy1 + 175, "n⁺ підкладка (стік)", size=10, bold=True, color=NEG))
    
    # Епюра поля E(x) праворуч
    gx1, gy1 = p2_x + 155, sy1 + 24
    parts.append(line(gx1, gy1, gx1, gy1 + 135, color=LINE, sw=1.5))
    parts.append(line(gx1, gy1 + 135, gx1 + 150, gy1 + 135, color=LINE, sw=1.5))
    parts.append(text(gx1 + 145, gy1 + 150, "x", size=11, italic=True))
    parts.append(text(gx1 - 10, gy1 + 15, "E", size=11, italic=True))
    
    # Прямокутний профіль
    parts.append(f'<polygon points="{gx1},{gy1+10} {gx1+80},{gy1+10} {gx1+80},{gy1+135} {gx1},{gy1+135}" fill="#d5f5e3" stroke="{FIELD}" stroke-width="2.0"/>')
    parts.append(text(gx1 + 40, gy1 + 75, "V_BR", size=12, bold=True, color=FIELD))
    parts.append(text(gx1 + 18, gy1 + 8, "E_crit", size=10, bold=True, color=FIELD))
    parts.append(text(gx1 + 80, gy1 + 150, "W_SJ", size=10, color=FIELD, bold=True))
    
    # Підсумок формули праворуч
    parts.append(fitbox(p2_x + 15, p2_y + 235, p2_w - 30, 110,
                        "Прямокутний профіль (баланс Q_p=Q_n):\n"
                        "• V_BR = E_crit · W_SJ\n"
                        "• W_SJ вдвічі менша за W_1D\n"
                        "• N_D задається шириною стовпця (густе!)\n"
                        "➔ R_sp ∝ V_BR^1.0 (лінійна межа)",
                        size=11, fill="#ffffff", stroke="#d5dbdb", color=INK))
                        
    render(os.path.join(IMG, 'drift-electrostatics.svg'), w, h, *parts)

def fig_wbg_energy_bandgap():
    """wbg-energy-bandgap.svg: Фізичні властивості та товщина дрейфового шару Si, SiC і GaN на 600 В."""
    w, h = 760, 400
    parts = []
    
    parts.append(text(w/2, 24, "Широкозонні напівпровідники: фізика забороненої зони та критичного поля", size=14, bold=True))
    
    col_w = 226
    gap = 16
    start_x = 22
    
    mats = [
        {
            "name": "Кремній (Si)",
            "eg": "1.12 еВ",
            "ec": "0.3 МВ/см",
            "bfom": "1.0 (еталон)",
            "thick": "50 мкм",
            "thick_px": 100,
            "doping": "1.5 × 10¹⁴ см⁻³",
            "rsp": "100 мОм·см²",
            "color": POS,
            "fill": "#fdecea"
        },
        {
            "name": "Карбід кремнію (4H-SiC)",
            "eg": "3.26 еВ (3×)",
            "ec": "2.8 МВ/см (9.3×)",
            "bfom": "340–500×",
            "thick": "5.5 мкм (9× тонша)",
            "thick_px": 20,
            "doping": "1.5 × 10¹⁶ см⁻³ (100×)",
            "rsp": "0.25 мОм·см² (400×)",
            "color": NEG,
            "fill": "#ebf5fb"
        },
        {
            "name": "Нітрид галію (GaN HEMT)",
            "eg": "3.40 еВ (3×)",
            "ec": "3.3 МВ/см (11×)",
            "bfom": "870–1000×",
            "thick": "4.5 мкм (11× тонша)",
            "thick_px": 14,
            "doping": "2DEG (надвисока μ)",
            "rsp": "0.10 мОм·см² (1000×)",
            "color": "#8e44ad",
            "fill": "#f4ecf7"
        }
    ]
    
    for i, m in enumerate(mats):
        cx = start_x + i * (col_w + gap)
        cy = 48
        
        # Контур картки без суцільної заливки
        parts.append(rect(cx, cy, col_w, 335, fill="none", stroke=m["color"], sw=1.5, rx=6))
        
        # Шапка картки
        parts.append(rect(cx, cy, col_w, 34, fill=m["fill"], stroke=m["color"], sw=1.5, rx=6))
        parts.append(text(cx + col_w/2, cy + 22, m["name"], size=12, bold=True, color=m["color"]))
        
        # Параметри
        ty = cy + 56
        lh = 22
        parts.append(text(cx + 12, ty, f"Ширина зони Eg: {m['eg']}", size=11, anchor="start", bold=True))
        parts.append(text(cx + 12, ty + lh, f"Критичне поле Ec: {m['ec']}", size=11, anchor="start", bold=True, color=m["color"]))
        parts.append(text(cx + 12, ty + 2*lh, f"Фактор BFOM: {m['bfom']}", size=11, anchor="start"))
        parts.append(text(cx + 12, ty + 3*lh, f"Легування (600 В): {m['doping']}", size=11, anchor="start"))
        parts.append(text(cx + 12, ty + 4*lh, f"R_sp дрейфу: {m['rsp']}", size=11, anchor="start", bold=True))
        
        # Візуальне порівняння товщини кристала на 600 В
        vy = cy + 182
        parts.append(text(cx + col_w/2, vy, "Товщина дрейфового шару (600 В):", size=10, bold=True, color=MUTED))
        
        box_y = vy + 12
        parts.append(rect(cx + 18, box_y, col_w - 36, 120, fill="none", stroke="#d5dbdb", sw=1.0, rx=4))
        
        # Сам шар відповідної висоти
        th_h = m["thick_px"]
        parts.append(rect(cx + 28, box_y + (116 - th_h)/2, col_w - 56, th_h, fill=m["fill"], stroke=m["color"], sw=1.5, rx=2))
        parts.append(text(cx + col_w/2, box_y + 64, m["thick"], size=12, bold=True, color=m["color"]))
        
    render(os.path.join(IMG, 'wbg-energy-bandgap.svg'), w, h, *parts)

def fig_charge_imbalance_field():
    """charge-imbalance-field.svg: Вплив зарядового дисбалансу на профіль поля суперпереходу."""
    w, h = 760, 380
    parts = []
    
    parts.append(text(w/2, 24, "Чутливість суперпереходу до зарядового дисбалансу (Charge Imbalance)", size=14, bold=True))
    
    panel_w = 226
    gap = 16
    start_x = 22
    
    cases = [
        {
            "title": "Ідеальний баланс (Q_n = Q_p)",
            "desc": "Рівномірне прямокутне поле вздовж стовпця. Напруга пробою максимальна (V_BR = 100%).",
            "type": "rect",
            "color": FIELD,
            "fill": "#eafaf1"
        },
        {
            "title": "N-надлишок (Q_n > Q_p +2%)",
            "desc": "Недокомпенсація донорів: пік поля біля витоку (p-body). Передчасний пробій на поверхні (V_BR падає до 70%).",
            "type": "tilt_top",
            "color": POS,
            "fill": "#fdecea"
        },
        {
            "title": "P-надлишок (Q_p > Q_n +2%)",
            "desc": "Недокомпенсація акцепторів: пік поля біля підкладки (стік n⁺). Передчасний пробій на дні (V_BR падає до 68%).",
            "type": "tilt_bot",
            "color": "#e67e22",
            "fill": "#fef5e7"
        }
    ]
    
    for i, c in enumerate(cases):
        cx = start_x + i * (panel_w + gap)
        cy = 48
        
        # Контур картки без суцільної заливки
        parts.append(rect(cx, cy, panel_w, 315, fill="none", stroke=c["color"], sw=1.5, rx=6))
        parts.append(rect(cx, cy, panel_w, 32, fill=c["fill"], stroke=c["color"], sw=1.5, rx=6))
        parts.append(text(cx + panel_w/2, cy + 20, c["title"], size=11, bold=True, color=c["color"]))
        
        # Вісь E(x)
        ax_x = cx + 32
        ax_y = cy + 45
        ax_h = 105
        ax_w = panel_w - 64
        
        parts.append(line(ax_x, ax_y, ax_x, ax_y + ax_h, color=LINE, sw=1.2))
        parts.append(line(ax_x, ax_y + ax_h, ax_x + ax_w, ax_y + ax_h, color=LINE, sw=1.2))
        parts.append(text(ax_x - 8, ax_y + 12, "E", size=10, italic=True))
        parts.append(text(ax_x + ax_w + 10, ax_y + ax_h + 4, "x", size=10, italic=True))
        parts.append(text(ax_x + 5, ax_y + ax_h + 14, "Витік", size=9, color=MUTED))
        parts.append(text(ax_x + ax_w - 5, ax_y + ax_h + 14, "Стік", size=9, color=MUTED))
        
        # Форма поля
        if c["type"] == "rect":
            parts.append(f'<polygon points="{ax_x},{ax_y+20} {ax_x+ax_w-15},{ax_y+20} {ax_x+ax_w-15},{ax_y+ax_h} {ax_x},{ax_y+ax_h}" fill="{c["fill"]}" stroke="{c["color"]}" stroke-width="2"/>')
            parts.append(text(ax_x + ax_w/2 - 7, ax_y + 12, "E_crit", size=10, bold=True, color=c["color"]))
        elif c["type"] == "tilt_top":
            parts.append(f'<polygon points="{ax_x},{ax_y+10} {ax_x+ax_w-15},{ax_y+ax_h-20} {ax_x+ax_w-15},{ax_y+ax_h} {ax_x},{ax_y+ax_h}" fill="{c["fill"]}" stroke="{c["color"]}" stroke-width="2"/>')
            parts.append(text(ax_x + 18, ax_y + 8, "E_crit", size=10, bold=True, color=POS))
        elif c["type"] == "tilt_bot":
            parts.append(f'<polygon points="{ax_x},{ax_y+ax_h-20} {ax_x+ax_w-15},{ax_y+10} {ax_x+ax_w-15},{ax_y+ax_h} {ax_x},{ax_y+ax_h}" fill="{c["fill"]}" stroke="{c["color"]}" stroke-width="2"/>')
            parts.append(text(ax_x + ax_w - 18, ax_y + 8, "E_crit", size=10, bold=True, color="#e67e22"))
            
        # Опис наслідку
        parts.append(fitbox(cx + 10, cy + 180, panel_w - 20, 115, c["desc"], size=11, fill="#fcfcfc", stroke="#e5e7e9", color=INK))
        
    render(os.path.join(IMG, 'charge-imbalance-field.svg'), w, h, *parts)

def fig_coss_nonlinearity():
    """coss-nonlinearity.svg: Гіпернелінійність вихідної ємності Coss(Vds) у суперперехідних MOSFET."""
    w, h = 760, 490
    parts = []
    
    parts.append(text(w/2, 22, "Гіпернелінійність вихідної ємності Coss у суперперехідних MOSFET (CoolMOS)", size=14, bold=True))
    
    gx0, gy0 = 80, 85
    gw, gh = 620, 240
    parts.append(rect(gx0, gy0, gw, gh, fill="none", stroke="#bbbbbb", sw=1.2))
    
    # Легенда НАД графіком (повністю вільна від сітки)
    parts.append(rect(gx0 + 10, 42, 24, 4, fill=FIELD, stroke=FIELD, sw=0))
    parts.append(text(gx0 + 42, 47, "Superjunction MOSFET (CoolMOS)", size=11, bold=True, color=FIELD, anchor="start"))
    
    parts.append(line(gx0 + 380, 44, gx0 + 404, 44, color=MUTED, sw=2.0, dash="5,3"))
    parts.append(text(gx0 + 412, 47, "Класичний планарний MOSFET (C ∝ 1/√V)", size=11, color=MUTED, anchor="start"))
    
    def vx(v):
        v = max(v, 0.2)
        lv = math.log10(v)
        return gx0 + (lv - (-0.7)) / (2.8 - (-0.7)) * gw
        
    def cy(c):
        lc = math.log10(c)
        return gy0 + gh - (lc - 0.0) / (4.3 - 0.0) * gh
        
    # Сітка Y (Coss)
    c_ticks = [
        (1, "1 пФ"),
        (10, "10 пФ"),
        (100, "100 пФ"),
        (1000, "1 нФ (1000 пФ)"),
        (10000, "10 нФ")
    ]
    for cval, clbl in c_ticks:
        y = cy(cval)
        parts.append(line(gx0, y, gx0 + gw, y, color="#ebebeb", sw=1.0))
        parts.append(text(gx0 - 8, y + 4, clbl, size=11, color=MUTED, anchor="end"))
        
    # Сітка X (Vds)
    v_ticks = [
        (0.5, "0.5 В"),
        (2, "2 В"),
        (10, "10 В"),
        (30, "30 В"),
        (50, "50 В"),
        (100, "100 В"),
        (200, "200 В"),
        (400, "400 В"),
        (600, "600 В")
    ]
    for vval, vlbl in v_ticks:
        x = vx(vval)
        parts.append(line(x, gy0, x, gy0 + gh, color="#ebebeb", sw=1.0))
        parts.append(text(x, gy0 + gh + 16, vlbl, size=10, color=MUTED, anchor="middle"))
        
    parts.append(text(gx0 + gw/2, gy0 + gh + 34, "Напруга стік-витік V_DS [В] (логарифмічна шкала)", size=11, bold=True))
    parts.append(text(20, gy0 + gh/2, "C_oss", size=12, bold=True, anchor="middle"))
    
    # Виділення зони обвалу
    x_trans1 = vx(30)
    x_trans2 = vx(60)
    parts.append(line(x_trans1, gy0, x_trans1, gy0 + gh, color=POS, sw=1.2, dash="3,3"))
    parts.append(line(x_trans2, gy0, x_trans2, gy0 + gh, color=POS, sw=1.2, dash="3,3"))
    parts.append(text((x_trans1 + x_trans2)/2, gy0 + 15, "30–50 В", size=10, bold=True, color=POS))
    
    # Крива 1: Планарний MOSFET
    pts_plan = []
    for v in [0.5, 1, 2, 5, 10, 20, 50, 100, 200, 400, 600]:
        c = 1500 / math.sqrt(1 + v/0.8)
        pts_plan.append((vx(v), cy(c)))
    path_plan = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts_plan)
    parts.append(f'<path d="{path_plan}" fill="none" stroke="{MUTED}" stroke-width="2.2" stroke-dasharray="5,4"/>')
    
    # Крива 2: Суперперехідний MOSFET (CoolMOS)
    pts_sj = [
        (0.2, 12000),
        (0.5, 9500),
        (1.0, 7500),
        (5.0, 5000),
        (15.0, 3200),
        (30.0, 1800),
        (45.0, 300),
        (55.0, 45),
        (100.0, 22),
        (200.0, 12),
        (400.0, 7.5),
        (600.0, 5.0)
    ]
    path_sj = "M " + " L ".join(f"{vx(v):.1f},{cy(c):.1f}" for v, c in pts_sj)
    parts.append(f'<path d="{path_sj}" fill="none" stroke="{FIELD}" stroke-width="3.0"/>')
    
    # 2 картки з висновками внизу полотна під віссю X (повністю поза графіком)
    parts.append(fitbox(gx0, gy0 + gh + 48, 295, 78,
                        "Зона переходу 30–50 В:\n"
                        "• Стовпчики збіднюються вбік\n"
                        "• Обвал C_oss у ~1000 разів!\n"
                        "• Екстремальна швидкість dv/dt > 50 В/нс",
                        size=10, fill="#fdecea", stroke=POS, color=POS, bold=True))
                        
    parts.append(fitbox(gx0 + gw - 305, gy0 + gh + 48, 305, 78,
                        "Високі напруги V_DS > 50 В:\n"
                        "• Дрейфовий шар збіднений повністю\n"
                        "• Залишкова ємність C_oss < 10 пФ\n"
                        "• Мінімальна енергія перезаряджання E_oss",
                        size=10, fill="#eafaf1", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(IMG, 'coss-nonlinearity.svg'), w, h, *parts)

if __name__ == '__main__':
    fig_silicon_limit_curve()
    fig_drift_electrostatics()
    fig_wbg_energy_bandgap()
    fig_charge_imbalance_field()
    fig_coss_nonlinearity()
    print("All figures generated successfully.")
