# -*- coding: utf-8 -*-
"""Фігури до статті «Рівні RAID».
Генерує векторні схеми SVG у теці ./img/:
1. raid0-raid1-layout.svg — порівняння компонування блоків у RAID 0 (чередування) та RAID 1 (дзеркалювання)
2. raid5-raid6-parity.svg — розподіл ротаційного паритету P (RAID 5) та подвійного паритету P/Q (RAID 6)
3. raid10-raid50-nested.svg — ієрархічне вкладене компонування RAID 10 (1+0) проти RAID 0+1
4. raid-rebuild-mtbf.svg — динаміка відбудови масиву та зростання ризику URE залежно від обсягу дисків
"""
import sys, os
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: RAID 0 vs RAID 1
# ─────────────────────────────────────────────────────────────────────────────
def fig_raid0_raid1():
    W, H = 840, 420
    parts = []
    
    # Background card
    parts.append(rect(10, 10, 820, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 38, "Структура дискових масивів RAID 0 (Чередування) та RAID 1 (Дзеркалювання)", size=16, color=INK, bold=True))
    
    # Panel RAID 0
    parts.append(rect(30, 60, 375, 335, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(217, 88, "RAID 0 (Data Striping)", size=15, color="#1e40af", bold=True))
    parts.append(text(217, 108, "Максимальна швидкість, 0% резервування", size=12, color=MUTED))
    
    # Disks RAID 0
    d_w, d_h = 75, 200
    y_disk = 135
    
    for i, title in enumerate(["Диск 0", "Диск 1", "Диск 2", "Диск 3"]):
        x_d = 50 + i * 85
        parts.append(rect(x_d, y_disk, d_w, d_h, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
        parts.append(text(x_d + d_w/2, y_disk + 24, title, size=13, color="#334155", bold=True))
        parts.append(line(x_d, y_disk + 35, x_d + d_w, y_disk + 35, color="#94a3b8", sw=1))
        
        # Blocks inside disk
        blocks = [f"Блок A{i+1}", f"Блок A{i+5}", f"Блок A{i+9}", f"Блок A{i+13}"]
        for b_idx, b_text in enumerate(blocks):
            yb = y_disk + 45 + b_idx * 36
            parts.append(rect(x_d + 5, yb, d_w - 10, 30, fill="#dbeafe", stroke="#3b82f6", sw=1, rx=3))
            parts.append(text(x_d + d_w/2, yb + 19, b_text, size=11, color="#1e3a8a", bold=True))
            
    parts.append(text(217, 375, "Ємність: N * C  |  Відмова при поломці 1 диска", size=11, color="#b91c1c", bold=True))
    
    # Panel RAID 1
    parts.append(rect(435, 60, 375, 335, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(622, 88, "RAID 1 (Disk Mirroring)", size=15, color="#15803d", bold=True))
    parts.append(text(622, 108, "100% дублювання даних, відмовостійкість", size=12, color=MUTED))
    
    # Disks RAID 1 (2 pairs)
    for i, title in enumerate(["Диск 0 (Main)", "Диск 1 (Mirror)"]):
        x_d = 465 + i * 160
        parts.append(rect(x_d, y_disk, 125, d_h, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=4))
        parts.append(text(x_d + 62.5, y_disk + 24, title, size=12, color="#334155", bold=True))
        parts.append(line(x_d, y_disk + 35, x_d + 125, y_disk + 35, color="#94a3b8", sw=1))
        
        blocks = ["Блок A1", "Блок A2", "Блок A3", "Блок A4"]
        for b_idx, b_text in enumerate(blocks):
            yb = y_disk + 45 + b_idx * 36
            fill_c = "#dcfce7" if i == 0 else "#fef9c3"
            stroke_c = "#16a34a" if i == 0 else "#ca8a04"
            text_c = "#14532d" if i == 0 else "#713f12"
            parts.append(rect(x_d + 8, yb, 109, 30, fill=fill_c, stroke=stroke_c, sw=1, rx=3))
            parts.append(text(x_d + 62.5, yb + 19, b_text, size=11, color=text_c, bold=True))

    parts.append(arrow(598, 190, 620, 190, color="#16a34a", sw=1.5))
    parts.append(arrow(620, 226, 598, 226, color="#ca8a04", sw=1.5))
    parts.append(text(622, 375, "Ємність: C  |  Витримує відмову N-1 дисків у парі", size=11, color="#15803d", bold=True))

    render(os.path.join(OUT, "raid0-raid1-layout.svg"), W, H, "\n".join(parts))

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: RAID 5 vs RAID 6 Parity Distribution
# ─────────────────────────────────────────────────────────────────────────────
def fig_raid5_raid6():
    W, H = 840, 440
    parts = []
    
    parts.append(rect(10, 10, 820, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 36, "Розподіл паритету у RAID 5 (Одинарний) та RAID 6 (Подвійний P+Q)", size=16, color=INK, bold=True))
    
    # RAID 5 section
    parts.append(rect(30, 55, 780, 170, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(420, 78, "RAID 5: Ротаційний одинарний XOR-паритет (P) по 4 дисках", size=14, color="#1e40af", bold=True))
    
    headers_5 = ["Диск 0", "Диск 1", "Диск 2", "Диск 3"]
    stripes_5 = [
        ["Блок A1", "Блок A2", "Блок A3", "Паритет P(A)"],
        ["Блок B1", "Блок B2", "Паритет P(B)", "Блок B3"],
        ["Блок C1", "Паритет P(C)", "Блок C2", "Блок C3"],
        ["Паритет P(D)", "Блок D1", "Блок D2", "Блок D3"]
    ]
    
    y_start_5 = 92
    for j, h in enumerate(headers_5):
        x_col = 140 + j * 155
        parts.append(text(x_col + 55, y_start_5, h, size=12, color="#334155", bold=True))
        
    for r_idx, row in enumerate(stripes_5):
        y_r = 104 + r_idx * 28
        parts.append(text(80, y_r + 18, f"Stripe {r_idx}:", size=11, color=MUTED, bold=True))
        for c_idx, val in enumerate(row):
            x_c = 140 + c_idx * 155
            is_p = "Паритет" in val
            fill_c = "#fee2e2" if is_p else "#dbeafe"
            stroke_c = "#ef4444" if is_p else "#3b82f6"
            text_c = "#991b1b" if is_p else "#1e3a8a"
            parts.append(rect(x_c, y_r, 110, 24, fill=fill_c, stroke=stroke_c, sw=1, rx=3))
            parts.append(text(x_c + 55, y_r + 16, val, size=10.5, color=text_c, bold=True))

    # RAID 6 section
    parts.append(rect(30, 235, 780, 180, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(420, 258, "RAID 6: Подвійний ротаційний паритет P (XOR) та Q (Reed-Solomon GF(2⁸))", size=14, color="#7c3aed", bold=True))
    
    headers_6 = ["Диск 0", "Диск 1", "Диск 2", "Диск 3", "Диск 4"]
    stripes_6 = [
        ["Блок A1", "Блок A2", "Блок A3", "Паритет P(A)", "Паритет Q(A)"],
        ["Блок B1", "Блок B2", "Паритет P(B)", "Паритет Q(B)", "Блок B3"],
        ["Блок C1", "Паритет P(C)", "Паритет Q(C)", "Блок C2", "Блок C3"],
        ["Паритет P(D)", "Паритет Q(D)", "Блок D1", "Блок D2", "Блок D3"]
    ]
    
    y_start_6 = 272
    for j, h in enumerate(headers_6):
        x_col = 110 + j * 135
        parts.append(text(x_col + 50, y_start_6, h, size=12, color="#334155", bold=True))
        
    for r_idx, row in enumerate(stripes_6):
        y_r = 284 + r_idx * 28
        parts.append(text(60, y_r + 18, f"Stripe {r_idx}:", size=11, color=MUTED, bold=True))
        for c_idx, val in enumerate(row):
            x_c = 110 + c_idx * 135
            is_p = "P(" in val
            is_q = "Q(" in val
            if is_p:
                fill_c, stroke_c, text_c = "#fee2e2", "#ef4444", "#991b1b"
            elif is_q:
                fill_c, stroke_c, text_c = "#f3e8ff", "#a855f7", "#6b21a8"
            else:
                fill_c, stroke_c, text_c = "#dbeafe", "#3b82f6", "#1e3a8a"
            parts.append(rect(x_c, y_r, 100, 24, fill=fill_c, stroke=stroke_c, sw=1, rx=3))
            parts.append(text(x_c + 50, y_r + 16, val, size=10, color=text_c, bold=True))

    render(os.path.join(OUT, "raid5-raid6-parity.svg"), W, H, "\n".join(parts))

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: RAID 10 vs RAID 0+1 Nested Layout
# ─────────────────────────────────────────────────────────────────────────────
def fig_raid10_raid01():
    W, H = 840, 420
    parts = []
    
    parts.append(rect(10, 10, 820, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 36, "Порівняння архітектур RAID 10 (Stripe of Mirrors) та RAID 0+1 (Mirror of Stripes)", size=15, color=INK, bold=True))
    
    # RAID 10
    parts.append(rect(30, 55, 375, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(217, 80, "RAID 10 (RAID 1+0): Stripe по дзеркалах", size=13.5, color="#15803d", bold=True))
    parts.append(text(217, 98, "Вищий рівень відмовостійкості", size=11.5, color="#166534"))
    
    # Top level stripe RAID 0
    parts.append(rect(50, 115, 335, 35, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    parts.append(text(217, 137, "RAID 0 (Top Level Striping)", size=12, color="#0369a1", bold=True))
    
    parts.append(arrow(132, 150, 132, 175, color="#0284c7", sw=1.5))
    parts.append(arrow(302, 150, 302, 175, color="#0284c7", sw=1.5))
    
    # Sub-mirrors
    parts.append(rect(50, 175, 165, 175, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=4))
    parts.append(text(132, 195, "Mirror Set 1 (RAID 1)", size=11, color="#15803d", bold=True))
    
    parts.append(rect(60, 210, 68, 125, fill="#ffffff", stroke="#86efac", sw=1, rx=3))
    parts.append(text(94, 226, "D0", size=11, bold=True))
    for b_i, b_t in enumerate(["A1", "A3", "A5"]):
        parts.append(rect(64, 235 + b_i*30, 60, 24, fill="#dcfce7", stroke="#22c55e", sw=1))
        parts.append(text(94, 251 + b_i*30, b_t, size=10, color="#14532d"))
        
    parts.append(rect(137, 210, 68, 125, fill="#ffffff", stroke="#86efac", sw=1, rx=3))
    parts.append(text(171, 226, "D1", size=11, bold=True))
    for b_i, b_t in enumerate(["A1", "A3", "A5"]):
        parts.append(rect(141, 235 + b_i*30, 60, 24, fill="#dcfce7", stroke="#22c55e", sw=1))
        parts.append(text(171, 251 + b_i*30, b_t, size=10, color="#14532d"))

    parts.append(rect(220, 175, 165, 175, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=4))
    parts.append(text(302, 195, "Mirror Set 2 (RAID 1)", size=11, color="#15803d", bold=True))
    
    parts.append(rect(230, 210, 68, 125, fill="#ffffff", stroke="#86efac", sw=1, rx=3))
    parts.append(text(264, 226, "D2", size=11, bold=True))
    for b_i, b_t in enumerate(["A2", "A4", "A6"]):
        parts.append(rect(234, 235 + b_i*30, 60, 24, fill="#dcfce7", stroke="#22c55e", sw=1))
        parts.append(text(264, 251 + b_i*30, b_t, size=10, color="#14532d"))

    parts.append(rect(307, 210, 68, 125, fill="#ffffff", stroke="#86efac", sw=1, rx=3))
    parts.append(text(341, 226, "D3", size=11, bold=True))
    for b_i, b_t in enumerate(["A2", "A4", "A6"]):
        parts.append(rect(311, 235 + b_i*30, 60, 24, fill="#dcfce7", stroke="#22c55e", sw=1))
        parts.append(text(341, 251 + b_i*30, b_t, size=10, color="#14532d"))

    parts.append(text(217, 375, "Відмова D0 не впливає на Set 2", size=11, color="#15803d", bold=True))

    # RAID 0+1
    parts.append(rect(435, 55, 375, 340, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    parts.append(text(622, 80, "RAID 0+1: Mirror по страйпах", size=13.5, color="#b91c1c", bold=True))
    parts.append(text(622, 98, "Критична вразливість при відбудові", size=11.5, color="#991b1b"))

    parts.append(rect(455, 115, 335, 35, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=4))
    parts.append(text(622, 137, "RAID 1 (Top Level Mirroring)", size=12, color="#b91c1c", bold=True))
    
    parts.append(arrow(537, 150, 537, 175, color="#ef4444", sw=1.5))
    parts.append(arrow(707, 150, 707, 175, color="#ef4444", sw=1.5))

    parts.append(rect(455, 175, 165, 175, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(text(537, 195, "Stripe Set 1 (RAID 0)", size=11, color="#1d4ed8", bold=True))
    
    parts.append(rect(465, 210, 68, 125, fill="#ffffff", stroke="#93c5fd", sw=1, rx=3))
    parts.append(text(499, 226, "D0", size=11, bold=True))
    for b_i, b_t in enumerate(["A1", "A3", "A5"]):
        parts.append(rect(469, 235 + b_i*30, 60, 24, fill="#dbeafe", stroke="#3b82f6", sw=1))
        parts.append(text(499, 251 + b_i*30, b_t, size=10, color="#1e3a8a"))

    parts.append(rect(542, 210, 68, 125, fill="#ffffff", stroke="#93c5fd", sw=1, rx=3))
    parts.append(text(576, 226, "D1", size=11, bold=True))
    for b_i, b_t in enumerate(["A2", "A4", "A6"]):
        parts.append(rect(546, 235 + b_i*30, 60, 24, fill="#dbeafe", stroke="#3b82f6", sw=1))
        parts.append(text(576, 251 + b_i*30, b_t, size=10, color="#1e3a8a"))

    parts.append(rect(625, 175, 165, 175, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=4))
    parts.append(text(707, 195, "Stripe Set 2 (RAID 0)", size=11, color="#1d4ed8", bold=True))

    parts.append(rect(635, 210, 68, 125, fill="#ffffff", stroke="#93c5fd", sw=1, rx=3))
    parts.append(text(669, 226, "D2", size=11, bold=True))
    for b_i, b_t in enumerate(["A1", "A3", "A5"]):
        parts.append(rect(639, 235 + b_i*30, 60, 24, fill="#dbeafe", stroke="#3b82f6", sw=1))
        parts.append(text(669, 251 + b_i*30, b_t, size=10, color="#1e3a8a"))

    parts.append(rect(712, 210, 68, 125, fill="#ffffff", stroke="#93c5fd", sw=1, rx=3))
    parts.append(text(746, 226, "D3", size=11, bold=True))
    for b_i, b_t in enumerate(["A2", "A4", "A6"]):
        parts.append(rect(716, 235 + b_i*30, 60, 24, fill="#dbeafe", stroke="#3b82f6", sw=1))
        parts.append(text(746, 251 + b_i*30, b_t, size=10, color="#1e3a8a"))

    parts.append(text(622, 375, "Відмова D0 руйнує весь Stripe Set 1", size=11, color="#b91c1c", bold=True))

    render(os.path.join(OUT, "raid10-raid50-nested.svg"), W, H, "\n".join(parts))

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: RAID Rebuild & URE Risk vs Disk Size
# ─────────────────────────────────────────────────────────────────────────────
def fig_raid_rebuild_mtbf():
    W, H = 840, 380
    parts = []
    
    parts.append(rect(10, 10, 820, 360, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 36, "Зростання ймовірності URE при відбудові масивів RAID 5 та RAID 6", size=15, color=INK, bold=True))
    
    # Graph area
    gx, gy, gw, gh = 90, 70, 480, 240
    parts.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke="#94a3b8", sw=1.5))
    
    # Grid lines
    for i in range(1, 5):
        y_l = gy + i * (gh / 5)
        parts.append(line(gx, y_l, gx + gw, y_l, color="#e2e8f0", sw=1, dash="4,4"))
    for j in range(1, 4):
        x_l = gx + j * (gw / 4)
        parts.append(line(x_l, gy, x_l, gy + gh, color="#e2e8f0", sw=1, dash="4,4"))
        
    # Y-axis labels (% URE risk)
    y_labels = ["100%", "80%", "60%", "40%", "20%", "0%"]
    for i, lbl in enumerate(y_labels):
        parts.append(text(gx - 25, gy + i * (gh / 5) + 4, lbl, size=11, color=MUTED, anchor="end"))
    parts.append(text(30, gy + gh/2, "Ймовірність помилки (URE)", size=11, color=INK, bold=True))

    # X-axis labels (Disk size in TB)
    x_labels = ["1 TB", "4 TB", "8 TB", "12 TB", "20 TB"]
    for j, lbl in enumerate(x_labels):
        parts.append(text(gx + j * (gw / 4), gy + gh + 22, lbl, size=11, color=MUTED))
    parts.append(text(gx + gw/2, gy + gh + 42, "Обсяг одного диска масиву (TB)", size=11, color=INK, bold=True))

    # RAID 5 Curve (Red exponential)
    pts_r5 = [
        (gx, gy + gh - 0.08*gh),
        (gx + 0.25*gw, gy + gh - 0.28*gh),
        (gx + 0.50*gw, gy + gh - 0.52*gh),
        (gx + 0.75*gw, gy + gh - 0.70*gh),
        (gx + gw, gy + gh - 0.92*gh)
    ]
    path_r5 = "M " + " L ".join([f"{x:.1f},{y:.1f}" for x, y in pts_r5])
    parts.append(f'<path d="{path_r5}" fill="none" stroke="#dc2626" stroke-width="3"/>')
    for x, y in pts_r5:
        parts.append(circle(x, y, 4, fill="#dc2626", stroke="#ffffff", sw=1.5))

    # RAID 6 Curve (Green flat/low)
    pts_r6 = [
        (gx, gy + gh - 0.01*gh),
        (gx + 0.25*gw, gy + gh - 0.02*gh),
        (gx + 0.50*gw, gy + gh - 0.04*gh),
        (gx + 0.75*gw, gy + gh - 0.07*gh),
        (gx + gw, gy + gh - 0.12*gh)
    ]
    path_r6 = "M " + " L ".join([f"{x:.1f},{y:.1f}" for x, y in pts_r6])
    parts.append(f'<path d="{path_r6}" fill="none" stroke="#16a34a" stroke-width="3"/>')
    for x, y in pts_r6:
        parts.append(circle(x, y, 4, fill="#16a34a", stroke="#ffffff", sw=1.5))

    # Legend & Info Card
    parts.append(rect(590, 70, 225, 240, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    parts.append(text(702, 92, "Легенда та висновки", size=13, color=INK, bold=True))
    
    parts.append(line(605, 118, 635, 118, color="#dc2626", sw=3))
    parts.append(circle(620, 118, 4, fill="#dc2626", stroke="#ffffff", sw=1))
    parts.append(text(645, 122, "RAID 5 (1 disk failure)", size=11, color="#991b1b", bold=True, anchor="start"))

    parts.append(line(605, 148, 635, 148, color="#16a34a", sw=3))
    parts.append(circle(620, 148, 4, fill="#16a34a", stroke="#ffffff", sw=1))
    parts.append(text(645, 152, "RAID 6 (2 disk failures)", size=11, color="#14532d", bold=True, anchor="start"))

    info_lines = [
        "URE rate = 10^-14 bit",
        "(1 failure per 12.5 TB)",
        "Rebuild 8x12TB reads",
        "approx 84 TB of data",
        "RAID 5 loses array!",
        "RAID 6 protects array",
        "via 2nd parity P+Q"
    ]
    for idx, il in enumerate(info_lines):
        parts.append(text(605, 175 + idx*17, il, size=10.5, color="#334155", anchor="start"))

    render(os.path.join(OUT, "raid-rebuild-mtbf.svg"), W, H, "\n".join(parts))

if __name__ == "__main__":
    fig_raid0_raid1()
    fig_raid5_raid6()
    fig_raid10_raid01()
    fig_raid_rebuild_mtbf()
    print("SVG figures generated successfully in ./img/")
