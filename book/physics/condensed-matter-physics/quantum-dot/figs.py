# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK = INK
BORDER = "#dcdde1"

def svg_path(d_str, stroke="#c0392b", sw=2.5, fill="none", dash=None):
    d_attr = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" stroke="%s" stroke-width="%.1f" fill="%s"%s/>' % (d_str, stroke, sw, fill, d_attr)

def polygon(points, fill=DARK, stroke="none", sw=1.0):
    pts_str = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    st = ' stroke="%s" stroke-width="%.1f"' % (stroke, sw) if stroke != "none" else ''
    return '<polygon points="%s" fill="%s"%s/>' % (pts_str, fill, st)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Розмірне квантування та залежність спектра від радіуса точки
# ════════════════════════════════════════════════════════════════════════════
def fig_bandgap_vs_size():
    W, H = 840, 420
    f = []

    # Тло та розділювач
    f.append(line(420, 30, 420, 390, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Енергетичні рівні для трьох розмірів (6 нм, 3.5 нм, 2 нм) ──
    f.append(text(210, 45, "Квантове обмеження та розсунення зон", size=14, bold=True, color=INK))
    f.append(text(210, 65, "E_g(R) зростає при зменшенні радіуса R (∝ 1/R²)", size=11, color=MUTED))

    # Стовпчики для трьох точок
    # Точка 1: R = 6.0 нм (Червона)
    f.append(rect(50, 100, 90, 240, fill="#fdfefe", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(95, 120, "R = 6.0 нм", size=12, bold=True, color=DARK))
    f.append(line(60, 160, 130, 160, color="#c0392b", sw=2.5)) # 1Se
    f.append(line(60, 145, 130, 145, color="#e74c3c", sw=1.5, dash="2 2")) # 1Pe
    f.append(line(60, 280, 130, 280, color="#2980b9", sw=2.5)) # 1Sh
    f.append(line(60, 295, 130, 295, color="#3498db", sw=1.5, dash="2 2")) # 1Ph
    f.append(text(72, 175, "1S_e", size=10, color="#c0392b"))
    f.append(text(72, 270, "1S_h", size=10, color="#2980b9"))
    # Стрілка оптичного переходу hν1
    f.append(line(115, 275, 115, 165, color="#e74c3c", sw=2.0))
    f.append(polygon([(111, 170), (115, 160), (119, 170)], fill="#e74c3c"))
    f.append(text(75, 220, "hν₁ (630нм)", size=10, bold=True, color="#c0392b"))

    # Точка 2: R = 3.5 нм (Зелена)
    f.append(rect(165, 100, 90, 240, fill="#fdfefe", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(210, 120, "R = 3.5 нм", size=12, bold=True, color=DARK))
    f.append(line(175, 140, 245, 140, color="#27ae60", sw=2.5)) # 1Se
    f.append(line(175, 122, 245, 122, color="#2ecc71", sw=1.5, dash="2 2")) # 1Pe
    f.append(line(175, 300, 245, 300, color="#2980b9", sw=2.5)) # 1Sh
    f.append(line(175, 318, 245, 318, color="#3498db", sw=1.5, dash="2 2")) # 1Ph
    f.append(text(187, 155, "1S_e", size=10, color="#27ae60"))
    f.append(text(187, 290, "1S_h", size=10, color="#2980b9"))
    # Стрілка оптичного переходу hν2
    f.append(line(230, 295, 230, 145, color="#27ae60", sw=2.0))
    f.append(polygon([(226, 150), (230, 140), (234, 150)], fill="#27ae60"))
    f.append(text(190, 220, "hν₂ (530нм)", size=10, bold=True, color="#27ae60"))

    # Точка 3: R = 2.0 нм (Синя)
    f.append(rect(280, 100, 90, 240, fill="#fdfefe", stroke=BORDER, sw=1.5, rx=6))
    f.append(text(325, 120, "R = 2.0 нм", size=12, bold=True, color=DARK))
    f.append(line(290, 118, 360, 118, color="#2980b9", sw=2.5)) # 1Se
    f.append(line(290, 322, 360, 322, color="#8e44ad", sw=2.5)) # 1Sh
    f.append(text(302, 133, "1S_e", size=10, color="#2980b9"))
    f.append(text(302, 312, "1S_h", size=10, color="#8e44ad"))
    # Стрілка оптичного переходу hν3
    f.append(line(345, 317, 345, 123, color="#2980b9", sw=2.0))
    f.append(polygon([(341, 128), (345, 118), (349, 128)], fill="#2980b9"))
    f.append(text(305, 220, "hν₃ (460нм)", size=10, bold=True, color="#2980b9"))

    f.append(text(210, 360, "Об'ємна заборонена зона E_g,0 (CdSe = 1.74 еВ)", size=11, color=MUTED))

    # ── Права панель: Спектри люмінесценції та колби розчинів ──
    f.append(text(630, 45, "Спектр люмінесценції та зсув колірності", size=14, bold=True, color=INK))
    f.append(text(630, 65, "Вузькі піки випромінювання (FWHM ≈ 25 нм)", size=11, color=MUTED))

    # Вісі спектра
    f.append(line(460, 260, 800, 260, color=DARK, sw=1.5)) # Довжина хвилі λ
    f.append(line(460, 260, 460, 100, color=DARK, sw=1.5)) # Інтенсивність I
    f.append(text(800, 278, "λ, нм", size=11, bold=True, color=DARK))
    f.append(text(450, 90, "Інтенсивність PL", size=11, bold=True, color=DARK))

    # Гаусові піки
    # Синій пік 460 нм (центр x = 520)
    f.append(svg_path("M 465 260 Q 520 100 575 260", stroke="#2980b9", sw=2.5, fill="none"))
    f.append(text(520, 278, "460", size=10, color="#2980b9"))

    # Зелений пік 530 нм (центр x = 620)
    f.append(svg_path("M 565 260 Q 620 100 675 260", stroke="#27ae60", sw=2.5, fill="none"))
    f.append(text(620, 278, "530", size=10, color="#27ae60"))

    # Червоний пік 630 нм (центр x = 730)
    f.append(svg_path("M 675 260 Q 730 100 785 260", stroke="#c0392b", sw=2.5, fill="none"))
    f.append(text(730, 278, "630", size=10, color="#c0392b"))

    # Візуалізація квантових точок у формі колбочок унизу праворуч
    # Синя колба
    f.append(rect(500, 310, 40, 50, fill="#3498db", stroke="#2980b9", sw=1.5, rx=4))
    f.append(circle(520, 335, 12, fill="#ebf5fb", stroke="none"))
    f.append(text(520, 378, "2 нм", size=11, bold=True, color="#2980b9"))

    # Зелена колба
    f.append(rect(600, 310, 40, 50, fill="#2ecc71", stroke="#27ae60", sw=1.5, rx=4))
    f.append(circle(620, 335, 14, fill="#e8f8f5", stroke="none"))
    f.append(text(620, 378, "3.5 нм", size=11, bold=True, color="#27ae60"))

    # Червона колба
    f.append(rect(710, 310, 40, 50, fill="#e74c3c", stroke="#c0392b", sw=1.5, rx=4))
    f.append(circle(730, 335, 16, fill="#fadbd8", stroke="none"))
    f.append(text(730, 378, "6 нм", size=11, bold=True, color="#c0392b"))

    render(os.path.join(OUT, "bandgap-vs-size.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Кулонівська облокада та одноелектронний транзистор
# ════════════════════════════════════════════════════════════════════════════
def fig_coulomb_blockade():
    W, H = 840, 400
    f = []

    # Тло та розділювач
    f.append(line(420, 30, 420, 370, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Одноелектронний транзистор (SET) та потенціальний профіль ──
    f.append(text(210, 45, "Енергетична діаграма одноелектронного транзистора", size=13, bold=True, color=INK))
    f.append(text(210, 65, "Кулонівська енергія перезарядки U_C = e²/2C", size=11, color=MUTED))

    # Витоку (Source) та Витоку (Drain)
    f.append(rect(30, 140, 100, 160, fill="#eaeded", stroke="#bdc3c7", sw=1.5, rx=4))
    f.append(text(80, 210, "Source (V_S)", size=12, bold=True, color=DARK))
    f.append(line(30, 240, 130, 240, color="#2980b9", sw=2.5)) # Фермі витоку E_FS

    f.append(rect(290, 140, 100, 160, fill="#eaeded", stroke="#bdc3c7", sw=1.5, rx=4))
    f.append(text(340, 210, "Drain (V_D)", size=12, bold=True, color=DARK))
    f.append(line(290, 260, 390, 260, color="#2980b9", sw=2.5)) # Фермі стоку E_FD

    # Тунельні бар'єри (товщина d)
    f.append(rect(130, 120, 25, 200, fill="#d5dbdb", stroke="#95a5a6", sw=1.5))
    f.append(rect(265, 120, 25, 200, fill="#d5dbdb", stroke="#95a5a6", sw=1.5))
    f.append(text(142, 335, "Бар'єр 1", size=10, color=MUTED))
    f.append(text(277, 335, "Бар'єр 2", size=10, color=MUTED))

    # Квантова точка посередині
    f.append(rect(155, 120, 110, 200, fill="#fef9e7", stroke="#f1c40f", sw=2.0, rx=6))
    f.append(text(210, 140, "Квантова точка", size=11, bold=True, color="#b7950b"))

    # Дискретні рівні з кулонівською щілиною U_C
    f.append(line(165, 280, 255, 280, color="#c0392b", sw=2.0)) # Рівень N
    f.append(line(165, 200, 255, 200, color="#c0392b", sw=2.0, dash="3 3")) # Рівень N+1
    f.append(text(210, 292, "E_N (заповнений)", size=10, color="#c0392b"))
    f.append(text(210, 190, "E_(N+1) (порожній)", size=10, color="#c0392b"))

    # Стрілка кулонівської енергії U_C
    f.append(line(245, 280, 245, 200, color="#8e44ad", sw=1.5))
    f.append(line(240, 280, 250, 280, color="#8e44ad", sw=1.5))
    f.append(line(240, 200, 250, 200, color="#8e44ad", sw=1.5))
    f.append(text(225, 240, "U_C + ΔE", size=10, bold=True, color="#8e44ad"))

    # Електростатичний затвор (Gate)
    f.append(rect(170, 340, 80, 25, fill="#ebf5fb", stroke="#2980b9", sw=1.5, rx=3))
    f.append(text(210, 357, "Gate (V_g)", size=11, bold=True, color="#2980b9"))
    f.append(line(210, 320, 210, 340, color="#2980b9", sw=1.5, dash="2 2"))

    # ── Права панель: Кулонівські ромби (Coulomb Diamonds) V_bias vs V_gate ──
    f.append(text(630, 45, "Кулонівські ромби та сходинки струму", size=13, bold=True, color=INK))
    f.append(text(630, 65, "Облокада провідності при |eV_bias| < U_C", size=11, color=MUTED))

    # Вісі графіку V_bias vs V_gate
    f.append(line(460, 220, 800, 220, color=DARK, sw=1.5)) # V_gate
    f.append(line(460, 340, 460, 100, color=DARK, sw=1.5)) # V_bias
    f.append(text(800, 238, "V_gate", size=11, bold=True, color=DARK))
    f.append(text(450, 90, "V_bias", size=11, bold=True, color=DARK))

    # Ромби кулонівської облокади (зони з I = 0)
    # Ромб 1: N електронів (центр x = 540)
    f.append(polygon([(480, 220), (540, 140), (600, 220), (540, 300)], fill="#eaeded", stroke="#7f8c8d", sw=2.0))
    f.append(text(540, 220, "N e⁻ (I = 0)", size=11, bold=True, color="#7f8c8d"))

    # Ромб 2: N+1 електронів (центр x = 660)
    f.append(polygon([(600, 220), (660, 140), (720, 220), (660, 300)], fill="#eaeded", stroke="#7f8c8d", sw=2.0))
    f.append(text(660, 220, "(N+1) e⁻", size=11, bold=True, color="#7f8c8d"))

    # Піки провідності на стиках ромбів (хрестовини)
    f.append(circle(600, 220, 5, fill="#e74c3c", stroke="none"))
    f.append(text(600, 205, "пік G", size=10, bold=True, color="#e74c3c"))
    f.append(circle(720, 220, 5, fill="#e74c3c", stroke="none"))

    f.append(text(630, 335, "Затвор V_g зміщує рівні точки відносно E_F", size=11, color=MUTED))

    render(os.path.join(OUT, "coulomb-blockade.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Структури квантових точок: Колоїдні проти Епітаксійних
# ════════════════════════════════════════════════════════════════════════════
def fig_synthesis_structure():
    W, H = 840, 380
    f = []

    # Тло та розділювач
    f.append(line(420, 30, 420, 350, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Колоїдна квантова точка Ядро-Оболонка (Core-Shell CQD) ──
    f.append(text(210, 45, "Колоїдна квантова точка (Core-Shell)", size=13, bold=True, color=INK))
    f.append(text(210, 65, "Синтез у розчині, ядро CdSe + оболонка ZnS", size=11, color=MUTED))

    # Оболонка ZnS (зовнішнє коло)
    f.append(circle(210, 200, 85, fill="#e8f8f5", stroke="#27ae60", sw=2.5))
    f.append(text(210, 135, "Оболонка ZnS (E_g = 3.6 еВ)", size=11, bold=True, color="#27ae60"))

    # Ядро CdSe (внутрішнє коло)
    f.append(circle(210, 200, 45, fill="#fadbd8", stroke="#c0392b", sw=2.5))
    f.append(text(210, 200, "Ядро CdSe\n(R ≈ 3 нм)", size=11, bold=True, color="#c0392b"))

    # Органічні ліганди (промені з паличок та кульок)
    import math
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = 210 + 85 * math.cos(rad)
        y1 = 200 + 85 * math.sin(rad)
        x2 = 210 + 115 * math.cos(rad)
        y2 = 200 + 115 * math.sin(rad)
        f.append(line(x1, y1, x2, y2, color="#8e44ad", sw=1.5))
        f.append(circle(x2, y2, 3, fill="#8e44ad", stroke="none"))

    f.append(text(210, 335, "Органічні ліганди (олеїнова кислота / TOPO)", size=11, color="#8e44ad"))

    # ── Права панель: Епітаксійна точка Странського — Крастанова (SK QD) ──
    f.append(text(630, 45, "Епітаксійна точка (Странського — Крастанова)", size=13, bold=True, color=INK))
    f.append(text(630, 65, "Самозбирання через деформацію решітки InAs/GaAs", size=11, color=MUTED))

    # Підкладка GaAs
    f.append(rect(460, 240, 340, 70, fill="#eaeded", stroke="#7f8c8d", sw=1.5))
    f.append(text(630, 280, "Підкладка GaAs (матриця)", size=12, bold=True, color=DARK))

    # Змочувальний шар (Wetting Layer InAs, товщина 1-2 моношари)
    f.append(rect(460, 230, 340, 10, fill="#f5b041", stroke="#d35400", sw=1.0))
    f.append(text(490, 222, "Змочувальний шар InAs (~1.5 ML)", size=10, bold=True, color="#d35400"))

    # Наноострівець / Піраміда InAs (Квантова точка)
    f.append(polygon([(560, 230), (630, 145), (700, 230)], fill="#e67e22", stroke="#d35400", sw=2.0))
    f.append(text(630, 195, "Острівець InAs (15-20 нм)", size=10, bold=True, color="#ffffff"))

    # Верхнє покриття (Cap Layer GaAs)
    f.append(svg_path("M 460 230 C 560 230 570 140 630 140 C 690 140 700 230 800 230", stroke="#7f8c8d", sw=1.5, fill="none", dash="3 3"))
    f.append(text(630, 125, "Захисний шар GaAs (поховання точки)", size=10, color=MUTED))

    f.append(text(630, 335, "Розкарбування напруги решітки (7% неузгодженість)", size=11, color=MUTED))

    render(os.path.join(OUT, "synthesis-structure.svg"), W, H, *f)

if __name__ == "__main__":
    fig_bandgap_vs_size()
    fig_coulomb_blockade()
    fig_synthesis_structure()
    print("All figures created successfully!")
