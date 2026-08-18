# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Порівняння планарного осередку 2D NAND та вертикального 3D NAND
# ════════════════════════════════════════════════════════════════════════════
def fig_planar_vs_3d():
    W, H = 860, 430
    f = []

    # Розділювальна лінія між панелями
    f.append(line(430, 25, 430, 405, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: 2D Planar Floating Gate ──
    f.append(text(215, 40, "2D Планарна Flash (Floating Gate)", size=14, bold=True, color=INK))
    f.append(text(215, 60, "Паразитичне ємнісне зчеплення при < 15 нм", size=12, color=MUTED))

    # Схема плоских осередків 2D NAND
    # Осередок 1 (Control Gate + Floating Gate + Substrate)
    f.append(rect(60, 100, 130, 35, fill="#d6eaf8", stroke="#2980b9", sw=2)) # CG1
    f.append(text(125, 122, "Control Gate 1", size=11, bold=True, color="#1b4f72"))

    f.append(rect(60, 140, 130, 15, fill="#ebf5fb", stroke="#7fb3d5", sw=1.5)) # Inter-poly Oxide
    f.append(text(125, 152, "IPD (ONO)", size=9.5, color="#5499c7"))

    f.append(rect(60, 160, 130, 35, fill="#fdebd0", stroke="#d35400", sw=2)) # FG1 (Conductive Poly-Si)
    f.append(text(125, 182, "Floating Gate 1", size=11, bold=True, color="#7e5109"))
    # Заряджені електрони у FG1
    for ex in [75, 95, 115, 135, 155, 175]:
        f.append(circle(ex, 170, 3.5, fill="#c0392b", stroke="#7b241c", sw=1))

    f.append(rect(60, 200, 130, 15, fill="#f9ebea", stroke="#e74c3c", sw=1.5)) # Tunnel Oxide
    f.append(text(125, 212, "Tunnel SiO₂ (< 6 нм)", size=9.5, color="#c0392b"))

    # Осередок 2 (сусідній)
    f.append(rect(240, 100, 130, 35, fill="#d6eaf8", stroke="#2980b9", sw=2)) # CG2
    f.append(text(305, 122, "Control Gate 2", size=11, bold=True, color="#1b4f72"))

    f.append(rect(240, 140, 130, 15, fill="#ebf5fb", stroke="#7fb3d5", sw=1.5))
    f.append(text(305, 152, "IPD (ONO)", size=9.5, color="#5499c7"))

    f.append(rect(240, 160, 130, 35, fill="#fdebd0", stroke="#d35400", sw=2)) # FG2
    f.append(text(305, 182, "Floating Gate 2", size=11, bold=True, color="#7e5109"))

    f.append(rect(240, 200, 130, 15, fill="#f9ebea", stroke="#e74c3c", sw=1.5))
    f.append(text(305, 212, "Tunnel SiO₂", size=9.5, color="#c0392b"))

    # Загальна кремнієва підкладка p-Si
    f.append(rect(40, 220, 350, 45, fill="#e8daef", stroke="#8e44ad", sw=2))
    f.append(text(215, 247, "Кремнієва підкладка (p-Si Substrate)", size=11, bold=True, color="#512e5f"))

    # Паразитична ємність між FG1 та FG2
    f.append(line(190, 177, 240, 177, color="#c0392b", sw=2, dash="3 3"))
    f.append(text(215, 168, "C_xy", size=12, bold=True, color="#c0392b"))
    f.append(text(215, 300, "Недоліки 2D:", size=11.5, bold=True, color="#c0392b"))
    f.append(text(215, 320, "• Паразитична перехресна завада C_xy", size=10.5, color=DARK))
    f.append(text(215, 338, "• Утримання витоків: < 20 електронів у FG", size=10.5, color=DARK))
    f.append(text(215, 356, "• Тунельний пробій при витонченні SiO₂", size=10.5, color=DARK))
    f.append(text(215, 374, "• Межа фізичного масштабування: ~15 нм", size=10.5, color=DARK))


    # ── Права панель: 3D Vertical Channel (Charge Trap / GAA) ──
    f.append(text(645, 40, "3D Вертикальний канал (BiCS Charge Trap)", size=14, bold=True, color=INK))
    f.append(text(645, 60, "Круговий затвор (GAA) та пастка Si₃N₄", size=12, color=MUTED))

    # Вертикальний стек затворів (WL3, WL2, WL1)
    f.append(rect(470, 95, 350, 30, fill="#d6eaf8", stroke="#2980b9", sw=2)) # Gate WL3
    f.append(text(510, 114, "Word Line 3 (Metal Gate W)", size=10.5, bold=True, color="#1b4f72"))

    f.append(rect(470, 130, 350, 25, fill="#f2f4f4", stroke="#bdc3c7", sw=1.5)) # Oxide Isolator
    f.append(text(510, 146, "SiO₂ Ізолятор шару", size=9.5, color="#7f8c8d"))

    f.append(rect(470, 160, 350, 30, fill="#d6eaf8", stroke="#2980b9", sw=2)) # Gate WL2
    f.append(text(510, 179, "Word Line 2 (Metal Gate W)", size=10.5, bold=True, color="#1b4f72"))

    f.append(rect(470, 195, 350, 25, fill="#f2f4f4", stroke="#bdc3c7", sw=1.5)) # Oxide Isolator
    f.append(text(510, 211, "SiO₂ Ізолятор шару", size=9.5, color="#7f8c8d"))

    f.append(rect(470, 225, 350, 30, fill="#d6eaf8", stroke="#2980b9", sw=2)) # Gate WL1
    f.append(text(510, 244, "Word Line 1 (Metal Gate W)", size=10.5, bold=True, color="#1b4f72"))

    # Вертикальний циліндричний канал (проходить крізь усі шари)
    cx = 730
    f.append(rect(cx - 35, 85, 70, 180, fill="#e8f8f5", stroke="#16a085", sw=2)) # Charge Trap ONO Structure
    f.append(rect(cx - 25, 85, 50, 180, fill="#fef9e7", stroke="#f1c40f", sw=1.5)) # Poly-Si Channel
    f.append(rect(cx - 12, 85, 24, 180, fill="#ffffff", stroke="#bdc3c7", sw=1)) # Core SiO2
    f.append(text(cx, 175, "Канал", size=10, bold=True, color="#16a085"))

    # Локалізовані пастки в Si3N4 на рівні WL2
    f.append(circle(cx - 30, 175, 3.5, fill="#c0392b", stroke="#7b241c", sw=1))
    f.append(circle(cx + 30, 175, 3.5, fill="#c0392b", stroke="#7b241c", sw=1))

    f.append(text(645, 300, "Переваги 3D BiCS:", size=11.5, bold=True, color="#27ae60"))
    f.append(text(645, 320, "• Пастка Si₃N₄ ізолює електрони (немає витоку всього осередку)", size=10.5, color=DARK))
    f.append(text(645, 338, "• Кругове охоплення (GAA): ідеальний підпороговий нахил", size=10.5, color=DARK))
    f.append(text(645, 356, "• Масштабування за висотою (Z): 64 → 128 → 232+ шарів", size=10.5, color=DARK))
    f.append(text(645, 374, "• Збільшений об'єм осередку → висока надійність утримання", size=10.5, color=DARK))

    render(os.path.join(OUT, "planar-vs-3d-scaling.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Будова вертикального каналу Macaroni (радіальний розріз)
# ════════════════════════════════════════════════════════════════════════════
def fig_macaroni_structure():
    W, H = 820, 440
    f = []

    # Центр циліндричної структури
    cx, cy = 260, 220

    # Концентричні шари (від зовнішнього металевого затвора до внутрішнього ядра)
    # 1. Metal Gate W/TiN (найзовнішній)
    f.append(circle(cx, cy, 185, fill="#d6eaf8", stroke="#1b4f72", sw=2))
    # 2. Blocking High-k Al2O3 / SiO2
    f.append(circle(cx, cy, 145, fill="#ebf5fb", stroke="#2980b9", sw=2))
    # 3. Charge Trap Layer Si3N4
    f.append(circle(cx, cy, 115, fill="#fdebd0", stroke="#d35400", sw=2))
    # 4. Tunnel Oxide SiO2
    f.append(circle(cx, cy, 85, fill="#f9ebea", stroke="#c0392b", sw=2))
    # 5. Poly-Si Channel (тонке кільце)
    f.append(circle(cx, cy, 60, fill="#e8f8f5", stroke="#16a085", sw=2))
    # 6. Oxide Core SiO2 (внутрішнє ядро)
    f.append(circle(cx, cy, 35, fill="#ffffff", stroke="#7f8c8d", sw=1.5))

    # Локалізовані заповнені пастки у шарі Si3N4
    trap_coords = [(cx + 98, cy + 20), (cx - 98, cy - 20), (cx + 20, cy + 98), (cx - 20, cy - 98),
                   (cx + 70, cy - 70), (cx - 70, cy + 70)]
    for tx, ty in trap_coords:
        f.append(circle(tx, ty, 4.5, fill="#c0392b", stroke="#7b241c", sw=1))

    # Виносні виносні лінії-вказівники праворуч з текстовими блоками
    labels = [
        (170, 90, "1. Metal Control Gate (W / TiN)", "Керувальний затвор Word Line", "#1b4f72"),
        (130, 150, "2. Blocking Dielectric (Al₂O₃ / SiO₂)", "Запобігає витоку електронів у затвор", "#2980b9"),
        (100, 210, "3. Charge Trap Layer (Si₃N₄)", "Нітридна матриця пасток заряду", "#d35400"),
        (72, 270, "4. Tunnel Oxide (SiO₂)", "Бар'єр для тунелювання FN/PF", "#c0392b"),
        (48, 330, "5. Poly-Si Channel (6–10 нм)", "Тонка плівка вертикального каналу", "#16a085"),
        (18, 390, "6. Oxide Core SiO₂ (Macaroni Core)", "Центральне діелектричне ядро", "#7f8c8d")
    ]

    for r_radius, y_pos, title_txt, desc_txt, col in labels:
        # Провезення виносного відрізка
        lx_start = cx + r_radius * 0.707
        ly_start = cy - r_radius * 0.707
        lx_mid = 480
        f.append(line(lx_start, ly_start, lx_mid, y_pos, color=col, sw=1.5, dash="2 2"))
        f.append(circle(lx_start, ly_start, 3, fill=col))
        f.append(line(lx_mid, y_pos, 510, y_pos, color=col, sw=1.5))

        f.append(text(520, y_pos - 4, title_txt, size=11, bold=True, color=col))
        f.append(text(520, y_pos + 12, desc_txt, size=10, color=MUTED))

    render(os.path.join(OUT, "macaroni-channel-structure.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Зонна діаграма та тунельний транспорт Френкеля — Пуля
# ════════════════════════════════════════════════════════════════════════════
def fig_poole_frenkel():
    W, H = 820, 420
    f = []

    # Позначки зонних меж
    f.append(text(410, 35, "Зонна діаграма Charge Trap Flash при витоку / утриманні", size=14, bold=True, color=INK))
    f.append(text(410, 55, "Поле знижує кулонівський потенціальний бар'єр: ΔΦ = √(qE / π ε_i)", size=12, color=MUTED))

    # Зонний профіль зліва направо: Channel -> Tunnel SiO2 -> Trap Si3N4 -> Blocking Al2O3 -> Metal Gate
    f.append(rect(60, 80, 120, 270, fill="#e8f8f5", stroke="none")) # Channel
    f.append(text(120, 335, "Канал Poly-Si", size=11, bold=True, color="#16a085"))

    f.append(rect(180, 80, 120, 270, fill="#f9ebea", stroke="none")) # Tunnel SiO2
    f.append(text(240, 335, "Tunnel SiO₂", size=11, bold=True, color="#c0392b"))

    f.append(rect(300, 80, 220, 270, fill="#fdebd0", stroke="none")) # Si3N4 Trap
    f.append(text(410, 335, "Пастка Si₃N₄", size=11, bold=True, color="#d35400"))

    f.append(rect(520, 80, 120, 270, fill="#ebf5fb", stroke="none")) # Blocking Al2O3
    f.append(text(580, 335, "Al₂O₃ / SiO₂", size=11, bold=True, color="#2980b9"))

    f.append(rect(640, 80, 120, 270, fill="#d6eaf8", stroke="none")) # Metal Gate
    f.append(text(700, 335, "Затвор W", size=11, bold=True, color="#1b4f72"))

    # Дно зони провідності Ec під електричним полем E
    f.append(svg_path("M 60 140 L 180 140 L 180 90 L 300 130 L 300 170 M 300 170 L 520 210 L 520 100 L 640 140 L 760 140", stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(120, 130, "E_c (Канал)", size=10, bold=True, color="#c0392b"))

    # Кулонівська потенціальна яма в Si3N4 під дією поля E
    trap_x, trap_y = 410, 240
    f.append(svg_path("M 350 200 Q 400 280 410 285 Q 420 280 470 220", stroke="#d35400", sw=2, fill="none"))

    # Початковий бар'єр Φ_B
    f.append(line(350, 200, 470, 200, color=MUTED, sw=1.2, dash="3 3"))
    f.append(text(410, 190, "Глибина ями Φ_B", size=10.5, color=MUTED))

    # Знижений бар'єр під полем E: ΔΦ
    f.append(line(470, 200, 470, 220, color="#8e44ad", sw=1.5))
    f.append(line(465, 200, 475, 200, color="#8e44ad", sw=1.5))
    f.append(line(465, 220, 475, 220, color="#8e44ad", sw=1.5))
    f.append(text(485, 212, "ΔΦ", size=11, bold=True, color="#8e44ad"))

    # Електрон у ямі пастки
    f.append(circle(trap_x, trap_y + 20, 5, fill="#c0392b", stroke="#7b241c", sw=1.5))

    # Термічна збудженість та виліт електрона
    f.append(svg_path("M 410 255 C 410 225 430 215 460 215 C 480 215 500 200 540 190", stroke="#27ae60", sw=2.5, fill="none", dash="4 2"))
    f.append(polygon([(540, 186), (550, 190), (540, 194)], fill="#27ae60"))
    f.append(text(460, 245, "Термічне вивільнення (Poole-Frenkel)", size=11, bold=True, color="#27ae60"))

    # Стрілка електричного поля E
    f.append(line(180, 380, 640, 380, color=DARK, sw=1.5))
    f.append(polygon([(640, 376), (650, 380), (640, 384)], fill=DARK))
    f.append(text(410, 400, "Напруженість електричного поля E (MV/cm)", size=11.5, bold=True, color=DARK))

    render(os.path.join(OUT, "poole-frenkel-energy-diagram.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Технологічні виклики масштабування: HAR etching та String Stacking
# ════════════════════════════════════════════════════════════════════════════
def fig_har_etching_stacking():
    W, H = 840, 440
    f = []

    # Лінія розділу двох процесів
    f.append(line(420, 25, 420, 415, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Дефекти HAR травлення (Single Deck > 80:1) ──
    f.append(text(210, 40, "Дефекти HAR Травлення (Single Deck)", size=14, bold=True, color=INK))
    f.append(text(210, 60, "Аспектне співвідношення > 80:1 в одного захода", size=12, color=MUTED))

    f.append(rect(40, 80, 340, 280, fill="#f2f4f4", stroke="#bdc3c7", sw=1.5))

    # Форма отвору з Bowing та Tapering
    f.append(svg_path("M 175 80 Q 160 200 192 360 L 228 360 Q 260 200 245 80 Z", stroke="#c0392b", sw=2, fill="#ffffff"))

    f.append(line(175, 80, 245, 80, color="#2980b9", sw=1.5))
    f.append(text(210, 95, "Top Dia ≈ 80 нм", size=10, bold=True, color="#2980b9"))

    f.append(line(162, 210, 110, 210, color="#d35400", sw=1.5, dash="2 2"))
    f.append(text(105, 200, "Bowing (роздуття)", size=10.5, bold=True, color="#d35400"))
    f.append(text(105, 218, "Зміна C_gate", size=9.5, color=MUTED))

    f.append(line(192, 350, 120, 350, color="#c0392b", sw=1.5, dash="2 2"))
    f.append(text(115, 340, "Tapering (конусність)", size=10.5, bold=True, color="#c0392b"))
    f.append(text(115, 358, "Високий опір R_string", size=9.5, color=MUTED))

    f.append(text(210, 390, "Проблема: Неоднорідність V_th уздовж каналу", size=11, bold=True, color="#c0392b"))


    # ── Права панель: Технологія String Stacking (Dual-Deck / Multi-Tier) ──
    f.append(text(630, 40, "Багатодекова Архітектура (String Stacking)", size=14, bold=True, color=INK))
    f.append(text(630, 60, "З'єднання деків (Tier 1 + Tier 2) через Joint", size=12, color=MUTED))

    # Верхній дек Tier 2
    f.append(rect(470, 80, 320, 130, fill="#e8f8f5", stroke="#16a085", sw=1.5))
    f.append(svg_path("M 600 80 L 590 210 L 670 210 L 660 80 Z", stroke="#16a085", sw=2, fill="#ffffff"))
    f.append(text(720, 140, "Tier 2 Deck", size=11, bold=True, color="#16a085"))

    # Проміжне з'єднання (Tier Joint Interface)
    f.append(rect(470, 210, 320, 20, fill="#fdebd0", stroke="#d35400", sw=1.5))
    f.append(circle(630, 220, 6, fill="#e74c3c", stroke="#7b241c", sw=1.5))
    f.append(text(720, 224, "Inter-Tier Joint", size=10.5, bold=True, color="#d35400"))

    # Нижній дек Tier 1
    f.append(rect(470, 230, 320, 130, fill="#ebf5fb", stroke="#2980b9", sw=1.5))
    f.append(svg_path("M 595 230 L 585 360 L 675 360 L 665 230 Z", stroke="#2980b9", sw=2, fill="#ffffff"))
    f.append(text(720, 290, "Tier 1 Deck", size=11, bold=True, color="#2980b9"))

    # Підкладка під Tier 1
    f.append(rect(470, 360, 320, 25, fill="#e8daef", stroke="#8e44ad", sw=1.5))
    f.append(text(630, 377, "CUA Peripheral Circuits (під масивом)", size=10, bold=True, color="#512e5f"))

    f.append(text(630, 410, "Перевага: Контрольований діаметр отвору в кожному деку", size=10.5, bold=True, color="#27ae60"))

    render(os.path.join(OUT, "har-etching-string-stacking.svg"), W, H, *f)


if __name__ == '__main__':
    fig_planar_vs_3d()
    fig_macaroni_structure()
    fig_poole_frenkel()
    fig_har_etching_stacking()
    print("Figures generated successfully.")
