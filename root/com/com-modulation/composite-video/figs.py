# -*- coding: utf-8 -*-
"""Фігури до теми «Композитний відеосигнал (CVBS)».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import (
    INK, MUTED, POS, NEG, FIELD, LINE, FILL, BG, FONT,
    text, mtext, rect, line, arrow, circle, textbox, fitbox, render
)

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def polyline(pts, color=INK, sw=2.2):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (d, color, sw))


def hline(x1, x2, y, color=MUTED, sw=1.0, dash="4,4"):
    return line(x1, y, x2, y, color=color, sw=sw, dash=dash)


# ── фіг. 1: один рядок CVBS у шкалі IRE ────────────────────────────────────
def fig_cvbs_full_line():
    W, H = 880, 430
    x0, x1 = 120, 770
    
    y_white = 90       # +100 IRE (1.000 V)
    y_black_ped = 185  # +7.5 IRE (0.340 V)
    y_blank = 200      # 0 IRE (0.286 V)
    y_sync = 280       # -40 IRE (0.000 V)
    
    parts = [
        # Рівні
        hline(x0, x1, y_white, color=POS),
        text(x0 - 12, y_white + 4, "+100 IRE (1.000 В)", size=11, color=POS, anchor="end", bold=True),
        text(x1 + 12, y_white + 4, "Рівень білого (White)", size=11, color=POS, anchor="start"),
        
        hline(x0, x1, y_black_ped, color=MUTED, dash="3,3"),
        text(x0 - 12, y_black_ped + 4, "+7.5 IRE (0.340 В)", size=10, color=MUTED, anchor="end"),
        text(x1 + 12, y_black_ped + 4, "П'єдестал чорного NTSC", size=10, color=MUTED, anchor="start"),
        
        hline(x0, x1, y_blank, color=INK),
        text(x0 - 12, y_blank + 4, "0 IRE (0.286 В)", size=11, color=INK, anchor="end", bold=True),
        text(x1 + 12, y_blank + 4, "Рівень гасіння / Чорний PAL", size=11, color=INK, anchor="start"),
        
        hline(x0, x1, y_sync, color=NEG),
        text(x0 - 12, y_sync + 4, "-40 IRE (0.000 В)", size=11, color=NEG, anchor="end", bold=True),
        text(x1 + 12, y_sync + 4, "Дно синхро (Sync tip)", size=11, color=NEG, anchor="start"),
    ]
    
    # Інтервали по X
    x_fp_end = x0 + 25       # Front porch: 1.5 us
    x_sync_end = x_fp_end + 65 # Sync pulse: 4.7 us
    x_brz_end = x_sync_end + 12 # Breezeway: 0.6 us
    x_burst_end = x_brz_end + 50 # Colorburst: 2.5 us
    x_bp_end = x_burst_end + 35  # Back porch end (початок активного відео, 12.0 us)
    x_active_end = x1           # Кінець рядка (64.0 us)
    
    # Прямокутники для синхроімпульсу
    sig_pts = [
        (x0, y_blank),
        (x_fp_end, y_blank),
        (x_fp_end, y_sync),
        (x_sync_end, y_sync),
        (x_sync_end, y_blank),
        (x_brz_end, y_blank),
    ]
    parts.append(polyline(sig_pts, color=INK, sw=2.5))
    
    # Колірний спалах (Colorburst) на рівні y_blank
    burst_pts = []
    num_cycles = 8
    dx_b = (x_burst_end - x_brz_end) / (num_cycles * 16)
    for i in range(int(num_cycles * 16) + 1):
        bx = x_brz_end + i * dx_b
        phase = i * (2 * math.pi / 16)
        by = y_blank + 20 * math.sin(phase)
        burst_pts.append((bx, by))
    parts.append(polyline(burst_pts, color=FIELD, sw=2.0))
    
    # Залишок заднього майданчика
    parts.append(line(x_burst_end, y_blank, x_bp_end, y_blank, color=INK, sw=2.5))
    
    # Кольорові смуги активного відео
    bars = [
        ("Білий", 100, 0, "#e2e8f0"),
        ("Жовтий", 85, 30, "#fef08a"),
        ("Ціан", 70, 42, "#a5f3fc"),
        ("Зелений", 59, 41, "#bbf7d0"),
        ("Пурпур", 48, 41, "#fbcfe8"),
        ("Червоний", 35, 42, "#fecaca"),
        ("Синій", 20, 30, "#bfdbfe"),
        ("Чорний", 0, 0, "#1e293b"),
    ]
    dx_bar = (x_active_end - x_bp_end) / len(bars)
    
    for idx, (b_name, b_y_ire, b_c_ire, b_col) in enumerate(bars):
        bx_s = x_bp_end + idx * dx_bar
        bx_e = bx_s + dx_bar
        by_mid = y_blank - (b_y_ire / 100.0) * (y_blank - y_white)
        
        # Фоновий прямокутник смуги
        parts.append(f'<rect x="{bx_s:.1f}" y="{y_white}" width="{dx_bar:.1f}" height="{y_blank - y_white}" fill="{b_col}" opacity="0.35"/>')
        
        if b_c_ire == 0:
            parts.append(line(bx_s, by_mid, bx_e, by_mid, color=INK, sw=2.5))
        else:
            c_amp = (b_c_ire / 100.0) * (y_blank - y_white) * 0.45
            bar_pts = []
            steps = 24
            for s in range(steps + 1):
                cur_x = bx_s + s * (dx_bar / steps)
                phase = s * (4 * math.pi / steps)
                cur_y = by_mid + c_amp * math.sin(phase)
                bar_pts.append((cur_x, cur_y))
            parts.append(polyline(bar_pts, color=FIELD, sw=2.0))
            parts.append(line(bx_s, by_mid, bx_e, by_mid, color=MUTED, sw=1.0, dash="3,3"))
            
        parts.append(text(bx_s + dx_bar / 2, y_white - 8, b_name, size=10, color=INK, anchor="middle", bold=True))
        
    parts.append(line(x_active_end, y_blank, x_active_end + 10, y_blank, color=INK, sw=2.5))
    
    # Підписи інтервалів
    y_lbl = 330
    parts.append(line(x0, y_lbl, x_bp_end, y_lbl, color=MUTED, sw=1.5))
    parts.append(line(x0, y_lbl - 5, x0, y_lbl + 5, color=MUTED, sw=1.5))
    parts.append(line(x_bp_end, y_lbl - 5, x_bp_end, y_lbl + 5, color=MUTED, sw=1.5))
    parts.append(text((x0 + x_bp_end) / 2, y_lbl + 16, "Гасіння рядка H-Blanking (12.0 мкс)", size=10, color=INK, anchor="middle", bold=True))
    
    parts.append(line(x_bp_end, y_lbl, x_active_end, y_lbl, color=MUTED, sw=1.5))
    parts.append(line(x_active_end, y_lbl - 5, x_active_end, y_lbl + 5, color=MUTED, sw=1.5))
    parts.append(text((x_bp_end + x_active_end) / 2, y_lbl + 16, "Активне відео Active Video (52.0 мкс / 625 рядків)", size=10, color=INK, anchor="middle", bold=True))
    
    parts.append(text(x0 + 12, y_blank + 18, "FP 1.5мкс", size=9, color=MUTED, anchor="middle"))
    parts.append(text((x_fp_end + x_sync_end) / 2, y_sync + 18, "H-Sync 4.7мкс", size=10, color=NEG, anchor="middle", bold=True))
    parts.append(text((x_brz_end + x_burst_end) / 2, y_blank + 40, "Colorburst\n(8-10 періодів)", size=9, color=FIELD, anchor="middle"))
    parts.append(text((x_burst_end + x_bp_end) / 2, y_blank + 18, "BP 5.8мкс", size=9, color=MUTED, anchor="middle"))
    
    # Інформаційний бокс унизу
    box_y = 370
    parts.append(fitbox(x0, box_y, x1 - x0, 46, "140 IRE = 1.0 В Vpp на 75 Ом • Нижче 0 IRE: синхронізація • Вище 0 IRE: яскравість Y + піднесуча C", size=11, fill=FILL, stroke=LINE))
    
    return render(os.path.join(IMG, "cvbs-full-line-anatomy.svg"), W, H, *parts, title="Анатомія одного рядка сигналу CVBS (шкала IRE та часові інтервали)")


# ── фіг. 2: частотний спектр Y/C ──────────────────────────────────────────
def fig_cvbs_spectrum():
    W, H = 880, 370
    x_left = 90
    x_right = 790
    y_base = 250
    y_top = 70
    
    parts = [
        line(x_left, y_base, x_right + 30, y_base, color=INK, sw=2),
        arrow(x_right + 10, y_base, x_right + 30, y_base, color=INK),
        text(x_right + 35, y_base + 4, "f (МГц)", size=12, color=INK, anchor="start", bold=True),
        
        line(x_left, y_base, x_left, y_top - 10, color=INK, sw=2),
        arrow(x_left, y_top + 10, x_left, y_top - 10, color=INK),
        text(x_left, y_top - 18, "|S(f)|", size=12, color=INK, anchor="middle", bold=True),
    ]
    
    freqs = [
        (0, "0", x_left + 10),
        (1, "1.0", x_left + 120),
        (2, "2.0", x_left + 230),
        (3, "3.0", x_left + 340),
        (4.43, "4.43 (f_sc PAL)", x_left + 500),
        (5.5, "5.5 (Зріз Y)", x_left + 630),
        (6.0, "6.0 (Звук)", x_left + 690),
    ]
    
    for f_val, f_lbl, f_x in freqs:
        parts.append(line(f_x, y_base, f_x, y_base + 5, color=INK, sw=1.5))
        parts.append(text(f_x, y_base + 18, f_lbl, size=10, color=INK, anchor="middle", bold=(f_val in [4.43, 5.5, 6.0])))
        
    y_env_pts = [
        (x_left + 10, y_base - 140),
        (x_left + 100, y_base - 135),
        (x_left + 220, y_base - 115),
        (x_left + 350, y_base - 85),
        (x_left + 500, y_base - 50),
        (x_left + 620, y_base - 15),
        (x_left + 640, y_base),
    ]
    y_env_path = f"M {x_left + 10} {y_base} L " + " L ".join(f"{px} {py}" for px, py in y_env_pts) + f" L {x_left + 640} {y_base} Z"
    parts.append(f'<path d="{y_env_path}" fill="{NEG}" fill-opacity="0.12" stroke="{NEG}" stroke-width="2"/>')
    parts.append(text(x_left + 160, y_base - 110, "Спектр яскравості Y (0 – 5.5 МГц)", size=12, color=NEG, anchor="middle", bold=True))
    
    c_center = x_left + 500
    c_env_pts = [
        (c_center - 120, y_base),
        (c_center - 80, y_base - 40),
        (c_center, y_base - 100),
        (c_center + 80, y_base - 40),
        (c_center + 120, y_base),
    ]
    c_env_path = f"M {c_center - 120} {y_base} L " + " L ".join(f"{px} {py}" for px, py in c_env_pts) + " Z"
    parts.append(f'<path d="{c_env_path}" fill="{FIELD}" fill-opacity="0.25" stroke="{FIELD}" stroke-width="2"/>')
    parts.append(text(c_center, y_base - 110, "Колір C (QAM піднесуча)", size=12, color=FIELD, anchor="middle", bold=True))
    
    snd_center = x_left + 690
    snd_pts = [
        (snd_center - 25, y_base),
        (snd_center, y_base - 70),
        (snd_center + 25, y_base),
    ]
    snd_path = f"M {snd_center - 25} {y_base} L " + " L ".join(f"{px} {py}" for px, py in snd_pts) + " Z"
    parts.append(f'<path d="{snd_path}" fill="{POS}" fill-opacity="0.2" stroke="{POS}" stroke-width="1.5"/>')
    parts.append(text(snd_center, y_base - 78, "Звук (FM)", size=10, color=POS, anchor="middle", bold=True))
    
    # Врізка (Zoom): гребінчаста структура
    zoom_x, zoom_y, zoom_w, zoom_h = 100, 75, 290, 85
    parts.append(rect(zoom_x, zoom_y, zoom_w, zoom_h, fill=FILL, stroke=LINE, rx=4))
    parts.append(text(zoom_x + zoom_w / 2, zoom_y + 16, "Мікроструктура спектра (гребінчасте чергування)", size=10, color=INK, anchor="middle", bold=True))
    
    z_base = zoom_y + zoom_h - 15
    for i in range(5):
        hx_y = zoom_x + 35 + i * 50
        parts.append(line(hx_y, z_base, hx_y, z_base - 40, color=NEG, sw=2.5))
        parts.append(text(hx_y, z_base + 11, f"k·f_H", size=9, color=NEG, anchor="middle"))
        
        if i < 4:
            hx_c = hx_y + 25
            parts.append(line(hx_c, z_base, hx_c, z_base - 32, color=FIELD, sw=2.5, dash="3,2"))
            parts.append(text(hx_c, z_base - 36, "(k+½)f_H", size=9, color=FIELD, anchor="middle"))
            
    exp_y = 290
    parts.append(fitbox(x_left, exp_y, x_right - x_left + 20, 60,
                        "Гармоніки Y зосереджені на кратних частотах k·f_H • Піднесуча C зсунута на півкроку: лягає у проміжки між зубцями Y • Гребінчастий фільтр 1H розділяє Y/C без перехресних спотворень",
                        size=11, fill=FILL, stroke=LINE))
    
    return render(os.path.join(IMG, "cvbs-frequency-spectrum.svg"), W, H, *parts, title="Спектральне переплетення: яскравість (Y) та кольорова піднесуча (C)")


# ── фіг. 3: векторна площина U/V ──────────────────────────────────────────
def fig_cvbs_qam_vectors():
    W, H = 880, 440
    cx, cy = 290, 230
    radius = 140
    
    parts = [
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4,4"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{radius * 0.75}" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>',
        
        line(cx - radius - 30, cy, cx + radius + 30, cy, color=INK, sw=1.5),
        arrow(cx + radius + 15, cy, cx + radius + 30, cy, color=INK),
        text(cx + radius + 35, cy + 4, "+U (B-Y)", size=12, color=INK, anchor="start", bold=True),
        text(cx - radius - 35, cy + 4, "-U", size=12, color=INK, anchor="end", bold=True),
        
        line(cx, cy + radius + 30, cx, cy - radius - 30, color=INK, sw=1.5),
        arrow(cx, cy - radius - 15, cx, cy - radius - 30, color=INK),
        text(cx, cy - radius - 35, "+V (R-Y)", size=12, color=INK, anchor="middle", bold=True),
        text(cx, cy + radius + 42, "-V", size=12, color=INK, anchor="middle", bold=True),
    ]
    
    color_vectors = [
        ("Червоний (R)", -0.21, 0.70, "#e56b6f", "103.5°"),
        ("Пурпур (M)", 0.41, 0.58, "#b56576", "60.7°"),
        ("Синій (B)", 0.62, -0.14, "#457b9d", "347.1°"),
        ("Ціан (C)", 0.21, -0.70, "#2a9d8f", "283.5°"),
        ("Зелений (G)", -0.41, -0.58, "#588157", "240.7°"),
        ("Жовтий (Y)", -0.62, 0.14, "#e9c46a", "167.1°"),
    ]
    
    for c_name, u_val, v_val, col_hex, deg_str in color_vectors:
        vx = cx + u_val * radius * 1.35
        vy = cy - v_val * radius * 1.35
        parts.append(line(cx, cy, vx, vy, color=col_hex, sw=2.5))
        parts.append(circle(vx, vy, 5, fill=col_hex, stroke=INK, sw=1.0))
        tx = vx + (12 if u_val >= 0 else -12)
        ty = vy + (4 if abs(v_val) < 0.3 else (-8 if v_val > 0 else 16))
        anchor_val = "start" if u_val >= 0 else "end"
        parts.append(text(tx, ty, f"{c_name} {deg_str}", size=10, color=INK, anchor=anchor_val, bold=True))
        
    bx_ntsc = cx - radius * 0.7
    by_ntsc = cy
    parts.append(line(cx, cy, bx_ntsc, by_ntsc, color=POS, sw=3))
    parts.append(arrow(cx - 30, cy, bx_ntsc, by_ntsc, color=POS))
    parts.append(text(bx_ntsc - 10, by_ntsc - 8, "Burst NTSC (180°)", size=10, color=POS, anchor="end", bold=True))
    
    pal_rad = radius * 0.7
    bx_p1, by_p1 = cx - pal_rad * math.cos(math.radians(45)), cy - pal_rad * math.sin(math.radians(45))
    bx_p2, by_p2 = cx - pal_rad * math.cos(math.radians(45)), cy + pal_rad * math.sin(math.radians(45))
    
    parts.append(line(cx, cy, bx_p1, by_p1, color=FIELD, sw=2, dash="4,2"))
    parts.append(line(cx, cy, bx_p2, by_p2, color=FIELD, sw=2, dash="4,2"))
    parts.append(text(bx_p1 - 10, by_p1 - 4, "PAL Burst (+135°, рядок N)", size=9, color=FIELD, anchor="end"))
    parts.append(text(bx_p2 - 10, by_p2 + 12, "PAL Burst (-135°, рядок N+1)", size=9, color=FIELD, anchor="end"))
    
    panel_x = 560
    panel_y = 65
    panel_w = 290
    panel_h = 345
    
    panel_text = (
        "Математика квадратури QAM:\n"
        "C(t) = U·sin(ω_c t) + V·cos(ω_c t)\n"
        "     = A(t) · sin(ω_c t + φ(t))\n\n"
        "Параметри кольору:\n"
        "• Амплітуда A = √(U² + V²) → Насиченість\n"
        "• Фаза φ = arctan(V / U) → Колірний відтінок\n\n"
        "Придушена несуча (DSB-SC):\n"
        "• Чорно-біле відео: U=0, V=0 ⇒ C(t)=0\n"
        "  Несуча повністю зникає (немає шуму)\n\n"
        "Фазовий маятник PAL (Bruch):\n"
        "• Знак V інвертується щорядка: +V / -V\n"
        "• Фазова похибка каналу усереднюється\n"
        "  між двома рядками у 1H лінії затримки"
    )
    parts.append(fitbox(panel_x, panel_y, panel_w, panel_h, panel_text, size=11, fill=FILL, stroke=LINE, pad=12))
    
    return render(os.path.join(IMG, "cvbs-qam-constellation.svg"), W, H, *parts, title="Квадратурне кодування кольору: векторна площина (U, V) та колірний спалах")


# ── фіг. 4: кадрова синхронізація VBI ──────────────────────────────────────
def fig_cvbs_vbi_sync():
    W, H = 880, 380
    x_start = 60
    y_blank = 120
    y_sync = 190
    
    parts = [
        hline(x_start, W - 40, y_blank, color=MUTED, dash="2,2"),
        text(x_start - 10, y_blank + 4, "0 IRE", size=10, color=MUTED, anchor="end"),
        hline(x_start, W - 40, y_sync, color=MUTED, dash="2,2"),
        text(x_start - 10, y_sync + 4, "-40 IRE", size=10, color=MUTED, anchor="end"),
    ]
    
    cur_x = x_start
    h_len = 64
    
    # Звичайний рядок
    sig1 = [
        (cur_x, y_blank),
        (cur_x + 5, y_blank),
        (cur_x + 5, y_sync),
        (cur_x + 15, y_sync),
        (cur_x + 15, y_blank),
        (cur_x + h_len, y_blank)
    ]
    parts.append(polyline(sig1, color=INK, sw=2))
    parts.append(text(cur_x + h_len / 2, y_blank - 10, "Звичайний рядок", size=9, color=INK, anchor="middle"))
    cur_x += h_len
    
    # Вирівнювальні (5 шт)
    pre_start = cur_x
    for p in range(5):
        px0 = cur_x + p * 28
        p_pts = [
            (px0, y_blank),
            (px0 + 5, y_blank),
            (px0 + 5, y_sync),
            (px0 + 10, y_sync),
            (px0 + 10, y_blank),
            (px0 + 28, y_blank)
        ]
        parts.append(polyline(p_pts, color=NEG, sw=2))
    cur_x += 5 * 28
    pre_end = cur_x
    parts.append(text((pre_start + pre_end) / 2, y_blank - 14, "Вирівнювальні (5× 0.5H)", size=9, color=NEG, anchor="middle", bold=True))
    
    # Зубчастий V-Sync (5 шт)
    vsync_start = cur_x
    for v in range(5):
        vx0 = cur_x + v * 28
        v_pts = [
            (vx0, y_sync),
            (vx0 + 23, y_sync),
            (vx0 + 23, y_blank),
            (vx0 + 28, y_blank),
            (vx0 + 28, y_sync)
        ]
        parts.append(polyline(v_pts, color=POS, sw=2.5))
    cur_x += 5 * 28
    vsync_end = cur_x
    parts.append(text((vsync_start + vsync_end) / 2, y_blank - 14, "Зубчастий V-Sync (5× 0.5H)", size=9, color=POS, anchor="middle", bold=True))
    
    # Післявирівнювальні (5 шт)
    post_start = cur_x
    for p in range(5):
        px0 = cur_x + p * 28
        p_pts = [
            (px0, y_blank),
            (px0 + 5, y_blank),
            (px0 + 5, y_sync),
            (px0 + 10, y_sync),
            (px0 + 10, y_blank),
            (px0 + 28, y_blank)
        ]
        parts.append(polyline(p_pts, color=NEG, sw=2))
    cur_x += 5 * 28
    post_end = cur_x
    parts.append(text((post_start + post_end) / 2, y_blank - 14, "Після-вирівнювальні", size=9, color=NEG, anchor="middle", bold=True))
    
    # Рядки VBI (2 шт)
    vbi_start = cur_x
    for r in range(2):
        rx0 = cur_x + r * h_len
        r_pts = [
            (rx0, y_blank),
            (rx0 + 5, y_blank),
            (rx0 + 5, y_sync),
            (rx0 + 15, y_sync),
            (rx0 + 15, y_blank),
            (rx0 + h_len, y_blank)
        ]
        parts.append(polyline(r_pts, color=MUTED, sw=1.5))
    cur_x += 2 * h_len
    parts.append(text(vbi_start + h_len, y_blank - 10, "Рядки VBI (Телетекст, OSD)", size=9, color=MUTED, anchor="middle"))
    
    # Інтегратор
    y_int_base = 280
    parts.append(text(x_start, y_int_base - 35, "Напруга на інтегрувальному RC-ланцюзі сепаратора синхроімпульсів:", size=11, color=INK, anchor="start", bold=True))
    parts.append(line(x_start, y_int_base, W - 40, y_int_base, color=INK, sw=1.5))
    parts.append(hline(x_start, W - 40, y_int_base - 50, color=POS, dash="3,3"))
    parts.append(text(W - 35, y_int_base - 50, "Поріг V-Sync", size=9, color=POS, anchor="start"))
    
    int_pts = [
        (x_start, y_int_base),
        (pre_start, y_int_base - 2),
        (vsync_start, y_int_base - 5),
        (vsync_start + 40, y_int_base - 30),
        (vsync_start + 80, y_int_base - 55),
        (vsync_end, y_int_base - 65),
        (post_start + 50, y_int_base - 25),
        (post_end, y_int_base - 5),
        (cur_x, y_int_base),
    ]
    parts.append(polyline(int_pts, color=POS, sw=2.5))
    parts.append(text(vsync_start + 80, y_int_base - 70, "Спрацювання кадрової розгортки", size=10, color=POS, anchor="middle", bold=True))
    
    exp_y = 310
    parts.append(fitbox(x_start, exp_y, W - 2 * x_start, 55,
                        "Вирівнювальні імпульси (2·f_H = 31.25 кГц) зрівнюють заряд RC-ланцюга для парних і непарних полів • Широкі імпульси V-Sync насичують інтегратор, а короткі вирізи тримають синхронізацію рядкового PLL • Рядки 1..22 (VBI) передають телетекст та OSD",
                        size=10, fill=FILL, stroke=LINE))
    
    return render(os.path.join(IMG, "cvbs-vertical-interval-sync.svg"), W, H, *parts, title="Кадровий інтервал гасіння (VBI) та зубчастий синхроімпульс (V-Sync)")


if __name__ == "__main__":
    fig_cvbs_full_line()
    fig_cvbs_spectrum()
    fig_cvbs_qam_vectors()
    fig_cvbs_vbi_sync()
    print("Всі фігури згенеровано успішно.")
