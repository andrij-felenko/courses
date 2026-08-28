# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Геометрія мінімальних зазорів плати: Trace/Space, Mask Expansion, Mask Dam, Edge ──
def gen_pcb_clearances_geometry():
    W, H = 840, 480
    f = []

    # Заголовок
    f.append(text(W / 2, 24, "Геометрія технологічних зазорів друкованої плати", size=16, bold=True))

    # Основна плата-підкладка
    bx, by = 40, 56
    bw, bh = 760, 395
    f.append(rect(bx, by, bw, bh, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=6))

    # Ліва секція: Трасування та зазори маски (SMD-майданчики та доріжки)
    f.append(rect(bx + 15, by + 15, 470, 365, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    f.append(text(bx + 250, by + 36, "Поперечний профіль: мідь, діелектрик та паяльна маска", size=12, bold=True, color=INK))

    # Шар склотекстоліту FR-4 (основа)
    cy = by + 210
    f.append(rect(bx + 30, cy, 440, 80, fill="#eef2f6", stroke="#94a3b8", sw=1.2, rx=2))
    f.append(text(bx + 250, cy + 45, "Діелектрик FR-4 (товщина h = 1.6 мм)", size=11, color=MUTED))

    # Мідні провідники на поверхні FR-4
    # Майданчик 1 (Pad 1)
    p1_x, p1_w, cu_h = bx + 50, 105, 24
    f.append(rect(p1_x, cy - cu_h, p1_w, cu_h, fill="#d35400", stroke="#a04000", sw=1.5, rx=1))
    f.append(text(p1_x + p1_w / 2, cy - 8, "SMD-майданчик 1", size=10, color="#ffffff", bold=True))

    # Майданчик 2 (Pad 2)
    p2_x, p2_w = p1_x + p1_w + 60, 105
    f.append(rect(p2_x, cy - cu_h, p2_w, cu_h, fill="#d35400", stroke="#a04000", sw=1.5, rx=1))
    f.append(text(p2_x + p2_w / 2, cy - 8, "SMD-майданчик 2", size=10, color="#ffffff", bold=True))

    # Сигнальна доріжка 1 (Trace 1)
    t1_x, t1_w = p2_x + p2_w + 45, 35
    f.append(rect(t1_x, cy - cu_h, t1_w, cu_h, fill="#d35400", stroke="#a04000", sw=1.5, rx=1))
    f.append(text(t1_x + t1_w / 2, cy - 8, "Доріжка", size=9, color="#ffffff", bold=True))

    # Сигнальна доріжка 2 (Trace 2)
    t2_x, t2_w = t1_x + t1_w + 35, 35
    f.append(rect(t2_x, cy - cu_h, t2_w, cu_h, fill="#d35400", stroke="#a04000", sw=1.5, rx=1))
    f.append(text(t2_x + t2_w / 2, cy - 8, "Доріжка", size=9, color="#ffffff", bold=True))

    # Зелена паяльна маска (LPI Solder Mask) - не перекриває мідь частково
    # Маска ліворуч від Pad 1
    f.append(rect(bx + 30, cy - cu_h - 6, (p1_x - 10) - (bx + 30), cu_h + 6, fill="#27ae60", stroke="#1e8449", sw=1, rx=1))
    # Місток маски між Pad 1 та Pad 2 (Solder Mask Dam)
    dam_x = p1_x + p1_w + 10
    dam_w = (p2_x - 10) - dam_x
    f.append(rect(dam_x, cy - cu_h - 6, dam_w, cu_h + 6, fill="#27ae60", stroke="#1e8449", sw=1, rx=1))
    # Маска між Pad 2 та Trace 1
    m2_x = p2_x + p2_w + 10
    m2_w = (t1_x - 6) - m2_x
    f.append(rect(m2_x, cy - cu_h - 6, m2_w, cu_h + 6, fill="#27ae60", stroke="#1e8449", sw=1, rx=1))
    # Маска між Trace 1 та Trace 2
    m3_x = t1_x + t1_w + 6
    m3_w = (t2_x - 6) - m3_x
    f.append(rect(m3_x, cy - cu_h - 6, m3_w, cu_h + 6, fill="#27ae60", stroke="#1e8449", sw=1, rx=1))
    # Маска праворуч від Trace 2
    m4_x = t2_x + t2_w + 6
    m4_w = (bx + 470) - m4_x
    f.append(rect(m4_x, cy - cu_h - 6, m4_w, cu_h + 6, fill="#27ae60", stroke="#1e8449", sw=1, rx=1))

    # Вимірювальні лінії та розміри зверху
    # 1. Solder Mask Expansion
    f.append(line(p1_x, cy - cu_h - 2, p1_x, cy - 65, color=NEG, sw=1, dash="2,2"))
    f.append(line(p1_x - 10, cy - cu_h - 8, p1_x - 10, cy - 65, color=NEG, sw=1, dash="2,2"))
    f.append(line(p1_x - 10, cy - 58, p1_x, cy - 58, color=NEG, sw=1.2))
    f.append(text(p1_x + 5, cy - 70, "Expansion (2 mil)", size=9, color=NEG, anchor="start", bold=True))

    # 2. Solder Mask Dam
    f.append(line(dam_x, cy - cu_h - 8, dam_x, cy - 90, color=FIELD, sw=1, dash="2,2"))
    f.append(line(dam_x + dam_w, cy - cu_h - 8, dam_x + dam_w, cy - 90, color=FIELD, sw=1, dash="2,2"))
    f.append(line(dam_x, cy - 82, dam_x + dam_w, cy - 82, color=FIELD, sw=1.5))
    f.append(text(dam_x + dam_w / 2, cy - 95, "Mask Dam (≥ 4 mil / 0.1 мм)", size=10, color=FIELD, bold=True))

    # 3. Trace / Space
    sp_x1 = t1_x + t1_w
    sp_x2 = t2_x
    f.append(line(sp_x1, cy - cu_h - 8, sp_x1, cy - 65, color=POS, sw=1, dash="2,2"))
    f.append(line(sp_x2, cy - cu_h - 8, sp_x2, cy - 65, color=POS, sw=1, dash="2,2"))
    f.append(line(sp_x1, cy - 58, sp_x2, cy - 58, color=POS, sw=1.5))
    f.append(text((sp_x1 + sp_x2) / 2, cy - 70, "Space (6 mil)", size=9, color=POS, bold=True))

    # 4. Trace Width
    f.append(line(t1_x, cy - cu_h - 8, t1_x, cy - 40, color=INK, sw=1, dash="2,2"))
    f.append(line(t1_x + t1_w, cy - cu_h - 8, t1_x + t1_w, cy - 40, color=INK, sw=1, dash="2,2"))
    f.append(line(t1_x, cy - 35, t1_x + t1_w, cy - 35, color=INK, sw=1.2))
    f.append(text(t1_x + t1_w / 2, cy - 45, "Width", size=9, color=INK, bold=True))

    # Пояснення внизу лівої секції
    f.append(rect(bx + 25, cy + 95, 450, 68, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    f.append(text(bx + 35, cy + 115, "• Trace / Space: 6/6 mil (стандарт) проти 3.5/3.5 mil (advanced)", size=10, color=INK, anchor="start"))
    f.append(text(bx + 35, cy + 133, "• Solder Mask Dam: запобігає припійним перемичкам при пайці", size=10, color=INK, anchor="start"))
    f.append(text(bx + 35, cy + 151, "• Solder Mask Expansion: компенсація похибки оптичного суміщення", size=10, color=INK, anchor="start"))

    # Права секція: Механічна обробка та відступ міді до краю плати (Edge Clearance)
    rx, ry = bx + 500, by + 15
    rw, rh = 245, 365
    f.append(rect(rx, ry, rw, rh, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    f.append(text(rx + rw / 2, ry + 22, "Відступ міді до краю (Edge)", size=12, bold=True, color=INK))

    # 1. Фрезерування (Milling / Routing)
    f.append(rect(rx + 15, ry + 42, rw - 30, 140, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    f.append(text(rx + 25, ry + 60, "Фрезерування (CNC Routing)", size=11, bold=True, color=INK, anchor="start"))

    # Текстоліт
    f.append(rect(rx + 25, ry + 75, 140, 45, fill="#eef2f6", stroke="#94a3b8", sw=1.2, rx=1))
    # Мідний полігон (без накладання, лежить на текстоліті)
    f.append(rect(rx + 25, ry + 75, 95, 12, fill="#d35400", stroke="#a04000", sw=1, rx=1))
    f.append(text(rx + 72, ry + 85, "Мідь (GND)", size=9, color="#ffffff", bold=True))
    # Край фрези (вертикальна лінія зрізу)
    f.append(line(rx + 165, ry + 70, rx + 165, ry + 125, color=POS, sw=1.8, dash="4,2"))
    f.append(text(rx + 172, ry + 95, "Край плати", size=9, color=POS, anchor="start"))

    # Розмір відступу фрезерування
    f.append(line(rx + 120, ry + 72, rx + 165, ry + 72, color=NEG, sw=1.2))
    f.append(text(rx + 142, ry + 66, "≥ 0.25 мм (10 mil)", size=9, color=NEG, bold=True))

    # Пояснення до фрезерування
    f.append(text(rx + 25, ry + 138, "Захист від задирок фрези", size=9.5, color=MUTED, anchor="start"))
    f.append(text(rx + 25, ry + 152, "та оголення торцевої міді.", size=9.5, color=MUTED, anchor="start"))

    # 2. Скрайбування (V-cut / V-scoring)
    f.append(rect(rx + 15, ry + 195, rw - 30, 170, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    f.append(text(rx + 25, ry + 215, "Скрайбування (V-cut Scoring)", size=11, bold=True, color=INK, anchor="start"))

    # Текстоліт з V-подібним надрізом
    f.append(rect(rx + 25, ry + 230, 100, 60, fill="#eef2f6", stroke="#94a3b8", sw=1.2, rx=1))
    f.append(rect(rx + 25, ry + 230, 65, 12, fill="#d35400", stroke="#a04000", sw=1, rx=1))
    f.append(text(rx + 57, ry + 240, "Мідь", size=9, color="#ffffff", bold=True))

    # V-подібний надріз
    f.append(line(rx + 125, ry + 230, rx + 135, ry + 250, color=POS, sw=1.5))
    f.append(line(rx + 145, ry + 230, rx + 135, ry + 250, color=POS, sw=1.5))
    f.append(line(rx + 125, ry + 290, rx + 135, ry + 270, color=POS, sw=1.5))
    f.append(line(rx + 145, ry + 290, rx + 135, ry + 270, color=POS, sw=1.5))
    # Осьова лінія V-cut
    f.append(line(rx + 135, ry + 225, rx + 135, ry + 295, color=POS, sw=1, dash="3,2"))

    # Розмір відступу V-cut
    f.append(line(rx + 90, ry + 228, rx + 135, ry + 228, color=NEG, sw=1.2))
    f.append(text(rx + 112, ry + 222, "≥ 0.4–0.5 мм (16–20 mil)", size=9.5, color=NEG, bold=True))

    # Пояснення до V-cut
    f.append(text(rx + 25, ry + 312, "Широкий V-надріз руйнує", size=9.5, color=MUTED, anchor="start"))
    f.append(text(rx + 25, ry + 326, "мідь ближче ніж 0.4 мм.", size=9.5, color=MUTED, anchor="start"))
    f.append(text(rx + 25, ry + 342, "Ризик КЗ на корпус.", size=9.5, color=POS, bold=True, anchor="start"))

    render(os.path.join(IMG, "pcb-clearances-geometry.svg"), W, H, *f)


# ── 2. Структура перехідного отвору: свердло, поясок металізації та зміщення ──
def gen_via_annular_ring_structure():
    W, H = 840, 480
    f = []

    # Заголовок
    f.append(text(W / 2, 24, "Структура перехідного отвору (Via) та поясок металізації (Annular Ring)", size=16, bold=True))

    # Підкладка
    bx, by = 40, 56
    bw, bh = 760, 395
    f.append(rect(bx, by, bw, bh, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=6))

    # Ліва секція: Поперечний розріз металізованого отвору (PTH Via)
    f.append(rect(bx + 15, by + 15, 360, 365, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    f.append(text(bx + 195, by + 36, "Поперечний розріз (PTH Via)", size=12, bold=True, color=INK))

    vx, vy = bx + 40, by + 70
    vw, vh = 310, 200
    pad_w = 170
    pad_cx = vx + 155
    drill_dia = 80
    barrel_th = 14
    hole_dia = drill_dia - 2 * barrel_th

    # Лівий діелектрик FR-4
    f.append(rect(vx, vy, (pad_cx - drill_dia / 2) - vx, vh, fill="#eef2f6", stroke="#94a3b8", sw=1.2, rx=1))
    f.append(text(vx + 35, vy + 95, "Діелектрик", size=10, color=MUTED))
    f.append(text(vx + 35, vy + 110, "FR-4", size=10, color=MUTED))

    # Правий діелектрик FR-4
    f.append(rect(pad_cx + drill_dia / 2, vy, (vx + vw) - (pad_cx + drill_dia / 2), vh, fill="#eef2f6", stroke="#94a3b8", sw=1.2, rx=1))
    f.append(text(vx + vw - 35, vy + 95, "Діелектрик", size=10, color=MUTED))
    f.append(text(vx + vw - 35, vy + 110, "FR-4", size=10, color=MUTED))

    # Мідні контактні майданчики (лівий і правий сегменти, без закриття отвору)
    ar_w = (pad_w - drill_dia) / 2
    # Верхній лівий і правий майданчики
    f.append(rect(pad_cx - pad_w / 2, vy - 16, ar_w, 16, fill="#d35400", stroke="#a04000", sw=1.2, rx=1))
    f.append(rect(pad_cx + drill_dia / 2, vy - 16, ar_w, 16, fill="#d35400", stroke="#a04000", sw=1.2, rx=1))

    # Нижній лівий і правий майданчики
    f.append(rect(pad_cx - pad_w / 2, vy + vh, ar_w, 16, fill="#d35400", stroke="#a04000", sw=1.2, rx=1))
    f.append(rect(pad_cx + drill_dia / 2, vy + vh, ar_w, 16, fill="#d35400", stroke="#a04000", sw=1.2, rx=1))

    # Внутрішній шар міді (лівий і правий)
    f.append(rect(pad_cx - pad_w / 2, vy + 92, ar_w, 14, fill="#b9770e", stroke="#7e5109", sw=1, rx=1))
    f.append(rect(pad_cx + drill_dia / 2, vy + 92, ar_w, 14, fill="#b9770e", stroke="#7e5109", sw=1, rx=1))

    # Гальванічні стінки металізації (ліва і права мідні трубки)
    f.append(rect(pad_cx - drill_dia / 2, vy - 16, barrel_th, vh + 32, fill="#d35400", stroke="#a04000", sw=1.2))
    f.append(rect(pad_cx + drill_dia / 2 - barrel_th, vy - 16, barrel_th, vh + 32, fill="#d35400", stroke="#a04000", sw=1.2))

    # Повітряний отвір у центрі
    f.append(rect(pad_cx - hole_dia / 2, vy - 16, hole_dia, vh + 32, fill="#ffffff", stroke="#cbd5e1", sw=1))

    # Розмірні лінії для розрізу
    # 1. Діаметр свердла
    f.append(line(pad_cx - drill_dia / 2, vy - 28, pad_cx + drill_dia / 2, vy - 28, color=POS, sw=1.2))
    f.append(line(pad_cx - drill_dia / 2, vy - 18, pad_cx - drill_dia / 2, vy - 34, color=POS, sw=1, dash="2,2"))
    f.append(line(pad_cx + drill_dia / 2, vy - 18, pad_cx + drill_dia / 2, vy - 34, color=POS, sw=1, dash="2,2"))
    f.append(text(pad_cx, vy - 38, "Діаметр свердла D_drill (0.3 мм)", size=9.5, color=POS, bold=True))

    # 2. Поясок металізації (Annular Ring)
    f.append(line(pad_cx + drill_dia / 2, vy + vh + 24, pad_cx + pad_w / 2, vy + vh + 24, color=NEG, sw=1.5))
    f.append(line(pad_cx + drill_dia / 2, vy + vh + 16, pad_cx + drill_dia / 2, vy + vh + 30, color=NEG, sw=1, dash="2,2"))
    f.append(line(pad_cx + pad_w / 2, vy + vh + 16, pad_cx + pad_w / 2, vy + vh + 30, color=NEG, sw=1, dash="2,2"))
    f.append(text(pad_cx + drill_dia / 2 + ar_w / 2, vy + vh + 40, "Поясок AR (≥ 0.15 мм)", size=9, color=NEG, bold=True))

    # 3. Товщина стінки металізації
    f.append(arrow(pad_cx - drill_dia / 2 - 25, vy + 50, pad_cx - drill_dia / 2 + 5, vy + 50, color=FIELD, sw=1.5))
    f.append(text(pad_cx - drill_dia / 2 - 30, vy + 54, "Мідь 20–25 мкм", size=9, color=FIELD, anchor="end", bold=True))

    # Формула пояска внизу лівої секції
    f.append(rect(bx + 25, by + 310, 340, 60, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    f.append(text(bx + 195, by + 330, "AR = (D_pad − D_drill) / 2", size=11, bold=True, color=INK))
    f.append(text(bx + 195, by + 352, "D_pad = 0.6 мм, D_drill = 0.3 мм → AR = 0.15 мм (6 mil)", size=9.5, color=MUTED))

    # Права секція: Вигляд зверху — зміщення свердла, ризик обриву та краплеподібний майданчик
    rx, ry = bx + 390, by + 15
    rw, rh = 355, 365
    f.append(rect(rx, ry, rw, rh, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    f.append(text(rx + rw / 2, ry + 22, "Вигляд зверху: допуски суміщення та Breakout", size=12, bold=True, color=INK))

    # Варіант А: Ідеальне суміщення
    c1_x, c1_y = rx + 85, ry + 95
    # Доріжка
    f.append(rect(c1_x - 70, c1_y - 12, 70, 24, fill="#d35400", stroke="#a04000", sw=1.2))
    # Мідний майданчик
    f.append(circle(c1_x, c1_y, 45, fill="#d35400", stroke="#a04000", sw=1.5))
    # Отвір свердління
    f.append(circle(c1_x, c1_y, 22, fill="#ffffff", stroke="#334155", sw=1.2))
    f.append(text(c1_x, ry + 160, "Ідеальне центрування", size=10, bold=True, color=FIELD))
    f.append(text(c1_x, ry + 175, "Рівномірний поясок AR", size=9, color=MUTED))

    # Варіант Б: Зміщення свердла
    c2_x, c2_y = rx + 255, ry + 95
    # Доріжка
    f.append(rect(c2_x - 70, c2_y - 12, 70, 24, fill="#d35400", stroke="#a04000", sw=1.2))
    # Мідний майданчик
    f.append(circle(c2_x, c2_y, 45, fill="#d35400", stroke="#a04000", sw=1.5))
    # Зміщений отвір
    f.append(circle(c2_x + 22, c2_y - 10, 22, fill="#ffffff", stroke=POS, sw=1.5))
    f.append(text(c2_x, ry + 160, "Зміщення (Breakout)", size=10, bold=True, color=POS))
    f.append(text(c2_x, ry + 175, "Розрив кільця металізації", size=9, color=POS))

    # Варіант В: Захист краплеподібним підсиленням (Teardrop Pad)
    c3_x, c3_y = rx + 175, ry + 250
    # Плавний перехід-крапля (Teardrop)
    pts = f"{c3_x - 85:.1f},{c3_y - 12:.1f} {c3_x - 25:.1f},{c3_y - 38:.1f} {c3_x + 40:.1f},{c3_y:.1f} {c3_x - 25:.1f},{c3_y + 38:.1f} {c3_x - 85:.1f},{c3_y + 12:.1f}"
    f.append(f'<polygon points="{pts}" fill="#d35400" stroke="#a04000" stroke-width="1.2"/>')
    # Мідний майданчик
    f.append(circle(c3_x, c3_y, 42, fill="#d35400", stroke="#a04000", sw=1.2))
    # Зміщений отвір
    f.append(circle(c3_x - 18, c3_y - 10, 22, fill="#ffffff", stroke="#334155", sw=1.2))
    f.append(text(c3_x, ry + 315, "Краплеподібне підсилення (Teardrop)", size=10.5, bold=True, color=FIELD))
    f.append(text(c3_x, ry + 332, "Захищає стик доріжки й отвору від розриву при зміщенні", size=9, color=MUTED))

    render(os.path.join(IMG, "via-annular-ring-structure.svg"), W, H, *f)


def main():
    gen_pcb_clearances_geometry()
    print("Generated pcb-clearances-geometry.svg")
    gen_via_annular_ring_structure()
    print("Generated via-annular-ring-structure.svg")

if __name__ == "__main__":
    main()
