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
# Фігура 1 — Будова комірки пам'яті: Floating Gate проти Charge Trap Flash
# ════════════════════════════════════════════════════════════════════════════
def fig_cell_structure():
    W, H = 840, 420
    f = []

    # Розділювальна лінія між панелями
    f.append(line(420, 25, 420, 395, color=MUTED, sw=1.5, dash="4 4"))

    # ── Ліва панель: Floating Gate (FG) ──
    f.append(text(210, 40, "Floating Gate (Плаваючий затвор)", size=14, bold=True, color=INK))
    f.append(text(210, 60, "Провідний полікремній, провідниковий шар", size=12, color=MUTED))

    # Керуючий затвор (Control Gate)
    f.append(rect(60, 90, 300, 35, fill="#ea4c89", stroke="#b82e63", sw=1.5, rx=3))
    f.append(text(210, 112, "Control Gate (Polysilicon / Metal)", size=12, bold=True, color="#ffffff"))

    # Межпетльовий діелектрик IPD (Inter-Poly Dielectric - ONO)
    f.append(rect(60, 125, 300, 25, fill="#f39c12", stroke="#d68910", sw=1.5, rx=2))
    f.append(text(210, 142, "Inter-Poly Dielectric (ONO: 10-15 нм)", size=11, bold=True, color="#ffffff"))

    # Плаваючий затвор (Floating Gate)
    f.append(rect(60, 150, 300, 45, fill="#3498db", stroke="#217dbb", sw=1.5, rx=3))
    f.append(text(210, 172, "Floating Gate (N+ Polysilicon)", size=12, bold=True, color="#ffffff"))

    # Накопичені електрони у FG
    for x_pos in [100, 140, 180, 220, 260, 300, 320]:
        f.append(circle(x_pos, 182, 5, fill="#2c3e50", stroke="#1a252f", sw=1))
        f.append(text(x_pos, 185, "-", size=10, bold=True, color="#ffffff"))

    # Тунельний оксид (Tunnel Oxide SiO2)
    f.append(rect(60, 195, 300, 20, fill="#e74c3c", stroke="#c0392b", sw=1.5, rx=2))
    f.append(text(210, 210, "Tunnel Oxide (SiO2: 7-9 нм)", size=11, bold=True, color="#ffffff"))

    # Підкладка (P-Si Substrate)
    f.append(rect(60, 215, 300, 130, fill="#ecf0f1", stroke="#bdc3c7", sw=1.5, rx=4))
    f.append(text(210, 325, "P-type Silicon Substrate", size=12, bold=True, color=DARK))

    # Стік та Витік (N+ Source / Drain)
    f.append(rect(80, 215, 60, 40, fill="#2ecc71", stroke="#27ae60", sw=1.5))
    f.append(text(110, 240, "N+ Source", size=11, bold=True, color="#ffffff"))

    f.append(rect(280, 215, 60, 40, fill="#2ecc71", stroke="#27ae60", sw=1.5))
    f.append(text(310, 240, "N+ Drain", size=11, bold=True, color="#ffffff"))

    # Інверсійний канал під діелектриком
    f.append(line(140, 217, 280, 217, color="#8e44ad", sw=4, dash="3 2"))
    f.append(text(210, 275, "Інверсійний n-канал", size=11, bold=True, color="#8e44ad"))

    # Витоковий витік заряду через дефект
    f.append(line(210, 195, 210, 215, color="#c0392b", sw=2, dash="2 2"))
    f.append(text(210, 375, "Дефект в оксиді розряджає ВЕСЬ плаваючий затвор", size=11, color="#c0392b"))

    # ── Права панель: Charge Trap Flash (CTF) ──
    f.append(text(630, 40, "Charge Trap Flash (CTF / 3D V-NAND)", size=14, bold=True, color=INK))
    f.append(text(630, 60, "Діелектричний нітрид Si3N4, лок. пастки", size=12, color=MUTED))

    # Затвор (Control / Metal Gate)
    f.append(rect(480, 90, 300, 35, fill="#ea4c89", stroke="#b82e63", sw=1.5, rx=3))
    f.append(text(630, 112, "Control Gate (Metal / High-k)", size=12, bold=True, color="#ffffff"))

    # Блокуючий оксид (Blocking Oxide Al2O3 / SiO2)
    f.append(rect(480, 125, 300, 25, fill="#9b59b6", stroke="#8e44ad", sw=1.5, rx=2))
    f.append(text(630, 142, "Blocking Oxide (Al2O3 / High-k: 10-15 нм)", size=11, bold=True, color="#ffffff"))

    # Локалізуючий шар пасток (Charge Trap Layer Si3N4)
    f.append(rect(480, 150, 300, 45, fill="#1abc9c", stroke="#16a085", sw=1.5, rx=3))
    f.append(text(630, 168, "Charge Trap Layer (Si3N4)", size=12, bold=True, color="#ffffff"))

    # Дискретні локалізовані електрони
    for x_pos in [510, 550, 590, 630, 670, 710, 750]:
        f.append(circle(x_pos, 183, 5, fill="#d35400", stroke="#a04000", sw=1))
        f.append(text(x_pos, 186, "-", size=10, bold=True, color="#ffffff"))

    # Тонкий тунельний оксид (Tunnel Oxide SiO2)
    f.append(rect(480, 195, 300, 20, fill="#e74c3c", stroke="#c0392b", sw=1.5, rx=2))
    f.append(text(630, 210, "Tunnel Oxide (SiO2: 3-4 нм)", size=11, bold=True, color="#ffffff"))

    # Підкладка (P-Si Substrate / Channel)
    f.append(rect(480, 215, 300, 130, fill="#ecf0f1", stroke="#bdc3c7", sw=1.5, rx=4))
    f.append(text(630, 325, "Silicon Channel (Macaroni structure)", size=12, bold=True, color=DARK))

    # Стік та Витік
    f.append(rect(500, 215, 60, 40, fill="#2ecc71", stroke="#27ae60", sw=1.5))
    f.append(text(530, 240, "N+ Source", size=11, bold=True, color="#ffffff"))

    f.append(rect(700, 215, 60, 40, fill="#2ecc71", stroke="#27ae60", sw=1.5))
    f.append(text(730, 240, "N+ Drain", size=11, bold=True, color="#ffffff"))

    # Інверсійний канал
    f.append(line(560, 217, 700, 217, color="#8e44ad", sw=4, dash="3 2"))
    f.append(text(630, 275, "Інверсійний n-канал", size=11, bold=True, color="#8e44ad"))

    # Локальний витік через дефект
    f.append(line(630, 195, 630, 215, color="#d35400", sw=2, dash="2 2"))
    f.append(text(630, 375, "Дефект витікає ЛИШЕ суміжні пастки (дискретний витік)", size=11, color="#16a085"))

    render(os.path.join(OUT, "cell-structure.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Розподіл порогових напруг SLC, MLC, TLC, QLC
# ════════════════════════════════════════════════════════════════════════════
def fig_vth_distributions():
    W, H = 840, 520
    f = []

    # Тло
    f.append(rect(10, 10, 820, 500, fill="#fafafa", stroke="#e0e0e0", sw=1, rx=6))
    f.append(text(420, 35, "Розподіл порогових напруг (V_th) комірок NAND", size=16, bold=True, color=INK))

    # Вісь X та Вісь Y
    f.append(line(60, 460, 800, 460, color=DARK, sw=2)) # V_th axis
    f.append(line(60, 460, 60, 60, color=DARK, sw=2))  # Probability density
    f.append(text(430, 495, "Порогова напруга V_th (Вольти)", size=13, bold=True, color=DARK))
    f.append(text(30, 250, "P(V_th)", size=13, bold=True, color=DARK))

    # ── SLC (2 стани: Erased '1', Programmed '0') ──
    f.append(text(75, 85, "SLC (1 біт/комірка — 2 стани)", size=12, bold=True, color="#2980b9"))
    # Erased state
    f.append(svg_path("M 70 460 Q 110 320 150 460", stroke="#2980b9", sw=2, fill="none"))
    f.append(text(110, 420, "E ('1')", size=11, bold=True, color="#2980b9"))

    # Programmed state
    f.append(svg_path("M 600 460 Q 670 320 740 460", stroke="#e74c3c", sw=2, fill="none"))
    f.append(text(670, 420, "P ('0')", size=11, bold=True, color="#e74c3c"))

    # Широке порогове вікно ΔV_th
    f.append(line(150, 350, 600, 350, color="#27ae60", sw=1.5, dash="4 4"))
    f.append(text(375, 340, "Широке порогове вікно ΔV_th ≈ 4-5 В (SLC)", size=11, bold=True, color="#27ae60"))

    # ── MLC (4 стани: E, P1, P2, P3) ──
    f.append(text(75, 175, "MLC (2 біти/комірка — 4 стани)", size=12, bold=True, color="#8e44ad"))
    for i, (name, col, x_c) in enumerate([("E ('11')", "#2980b9", 110), ("P1 ('10')", "#f39c12", 270), ("P2 ('01')", "#d35400", 430), ("P3 ('00')", "#c0392b", 590)]):
        d_str = "M %d 460 Q %d 360 %d 460" % (x_c - 40, x_c, x_c + 40)
        f.append(svg_path(d_str, stroke=col, sw=2, fill="none"))
        f.append(text(x_c, 440, name, size=10, bold=True, color=col))

    # ── TLC (8 станів) ──
    f.append(text(75, 255, "TLC (3 біти/комірка — 8 станів)", size=12, bold=True, color="#16a085"))
    for i in range(8):
        x_c = 100 + i * 85
        col = "#1abc9c" if i == 0 else "#e67e22" if i % 2 == 1 else "#e74c3c"
        d_str = "M %d 460 Q %d 390 %d 460" % (x_c - 25, x_c, x_c + 25)
        f.append(svg_path(d_str, stroke=col, sw=1.8, fill="none"))

    # ── QLC (16 станів) ──
    f.append(text(75, 305, "QLC (4 біти/комірка — 16 станів)", size=12, bold=True, color="#c0392b"))
    for i in range(16):
        x_c = 85 + i * 44
        col = "#3498db" if i == 0 else "#9b59b6" if i % 2 == 1 else "#e74c3c"
        d_str = "M %d 460 Q %d 410 %d 460" % (x_c - 14, x_c, x_c + 14)
        f.append(svg_path(d_str, stroke=col, sw=1.5, fill="none"))

    # Перекриття піків у QLC (шум, витік)
    f.append(circle(525, 440, 18, fill="none", stroke="#c0392b", sw=2))
    f.append(line(525, 420, 525, 370, color="#c0392b", sw=1.5))
    f.append(text(525, 355, "Перекриття станів внаслідок деградації (помилки RBER)", size=11, bold=True, color="#c0392b"))

    # Опорні напруги зчитування V_ref
    for x_ref in [190, 350, 510]:
        f.append(line(x_ref, 460, x_ref, 430, color="#7f8c8d", sw=1.5, dash="2 2"))
    f.append(text(190, 475, "V_R1", size=10, bold=True, color="#7f8c8d"))
    f.append(text(350, 475, "V_R2", size=10, bold=True, color="#7f8c8d"))
    f.append(text(510, 475, "V_R3", size=10, bold=True, color="#7f8c8d"))

    render(os.path.join(OUT, "vth-distributions.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Алгоритм покрокового програмування ISPP
# ════════════════════════════════════════════════════════════════════════════
def fig_ispp_programming():
    W, H = 840, 420
    f = []

    # Тло
    f.append(rect(10, 10, 820, 400, fill="#fafafa", stroke="#e0e0e0", sw=1, rx=6))
    f.append(text(420, 35, "Інкрементальне програмування імпульсами ISPP", size=16, bold=True, color=INK))

    # Вісі графіку V_control_gate(t)
    f.append(line(60, 350, 780, 350, color=DARK, sw=2)) # Time axis
    f.append(line(60, 350, 60, 70, color=DARK, sw=2))   # Voltage axis
    f.append(text(420, 385, "Час t (послідовність імпульсів програмування та верифікації)", size=12, bold=True, color=DARK))
    f.append(text(30, 200, "V_CG (В)", size=12, bold=True, color=DARK))

    # Пороговий рівень цільової верифікації V_verify
    f.append(line(60, 230, 780, 230, color="#27ae60", sw=1.5, dash="6 4"))
    f.append(text(710, 220, "V_verify (Ціль)", size=11, bold=True, color="#27ae60"))

    # Імпульси програмування (ISPP step pulses)
    pulse_x = [90, 180, 270, 360, 450, 540, 630]
    heights = [280, 250, 220, 190, 160, 130, 100]

    for i, (x, h) in enumerate(zip(pulse_x, heights)):
        # Programming pulse (high voltage)
        f.append(rect(x, h, 35, 350 - h, fill="#e74c3c", stroke="#c0392b", sw=1.5))
        f.append(text(x + 17, h - 10, "V_pgm_%d" % (i+1), size=10, bold=True, color="#e74c3c"))

        # Verify pulse (low voltage check)
        f.append(rect(x + 45, 230, 20, 120, fill="#3498db", stroke="#2980b9", sw=1.5))
        f.append(text(x + 55, 215, "V_vf", size=9, color="#2980b9"))

    # Покроковий приріст напруги ΔV_pgm
    f.append(line(125, 60, 215, 60, color="#f39c12", sw=1.5))
    f.append(text(170, 50, "ΔV_pgm (0.2-0.4 В)", size=10, bold=True, color="#d35400"))

    # Траєкторія порогової напруги V_th комірки
    vth_points = [(100, 330), (190, 305), (280, 280), (370, 255), (460, 230), (550, 205)]
    pts_str = " ".join("%d,%d" % p for p in vth_points)
    f.append(svg_path("M " + pts_str, stroke="#8e44ad", sw=3.0, fill="none"))

    for p in vth_points:
        f.append(circle(p[0], p[1], 4, fill="#8e44ad", stroke="#4a235a", sw=1.5))

    f.append(text(580, 190, "V_th досягає V_verify (Зупинка!)", size=11, bold=True, color="#8e44ad"))

    render(os.path.join(OUT, "ispp-programming.svg"), W, H, *f)

# ════════════════════════════════════════════════════════════════════════════
# Фігура 4 — Механізми деградації та витоку заряду
# ════════════════════════════════════════════════════════════════════════════
def fig_degradation_mechanisms():
    W, H = 840, 440
    f = []

    # Тло
    f.append(rect(10, 10, 820, 420, fill="#fafafa", stroke="#e0e0e0", sw=1, rx=6))
    f.append(text(420, 35, "Фізичні механізми деградації та розмиття V_th", size=16, bold=True, color=INK))

    # Схема зонного бар'єра з дефектами
    f.append(rect(60, 70, 720, 330, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=4))

    # Шар оксиду (SiO2) та пасток
    f.append(text(160, 95, "Підкладка Si", size=12, bold=True, color="#2c3e50"))
    f.append(text(420, 95, "Тунельний оксид SiO2 (Деградований)", size=12, bold=True, color="#e74c3c"))
    f.append(text(670, 95, "Затвор (FG / Si3N4)", size=12, bold=True, color="#2980b9"))

    # Вертикальні межі зон
    f.append(line(260, 110, 260, 370, color=DARK, sw=2))
    f.append(line(580, 110, 580, 370, color=DARK, sw=2))

    # Механізм 1: Trap-Assisted Tunnelling (TAT)
    f.append(text(420, 135, "1. Trap-Assisted Tunnelling (TAT)", size=12, bold=True, color="#c0392b"))
    # Заряджені пастки N_ot у об'ємі оксиду
    for y_trap in [160, 200, 240]:
        f.append(circle(360, y_trap, 6, fill="#f39c12", stroke="#d68910", sw=1.5))
        f.append(text(360, y_trap + 3, "*", size=14, bold=True, color="#ffffff"))
        f.append(circle(460, y_trap + 10, 6, fill="#f39c12", stroke="#d68910", sw=1.5))

    # Траєкторія витоку через пастки
    f.append(svg_path("M 640 160 L 460 170 L 360 160 L 180 160", stroke="#c0392b", sw=2, fill="none", dash="3 3"))
    f.append(polygon([(180, 156), (170, 160), (180, 164)], fill="#c0392b"))
    f.append(text(280, 145, "Витік електронів у підкладку", size=10, bold=True, color="#c0392b"))

    # Механізм 2: Random Telegraph Noise (RTN)
    f.append(text(420, 275, "2. Random Telegraph Noise (RTN)", size=12, bold=True, color="#8e44ad"))
    f.append(circle(300, 300, 8, fill="#9b59b6", stroke="#4a235a", sw=1.5))
    f.append(text(300, 304, "T", size=10, bold=True, color="#ffffff"))

    # Дискретні стрибки V_th у часі
    f.append(svg_path("M 350 330 L 410 330 L 410 290 L 480 290 L 480 330 L 550 330", stroke="#8e44ad", sw=2, fill="none"))
    f.append(text(445, 275, "Дискретний флуктуючий стрибок ΔV_th (10-50 мВ)", size=10, bold=True, color="#8e44ad"))

    # Механізм 3: Поверхневі стани N_it та перехресні наведення C_fg-fg
    f.append(line(260, 340, 260, 370, color="#d35400", sw=4))
    f.append(text(140, 355, "Поверхневі пастки (N_it)", size=11, bold=True, color="#d35400"))

    f.append(line(580, 330, 740, 330, color="#27ae60", sw=2, dash="4 4"))
    f.append(text(660, 355, "Паразитний зв'язок C_fg-fg", size=11, bold=True, color="#27ae60"))

    render(os.path.join(OUT, "degradation-mechanisms.svg"), W, H, *f)

if __name__ == "__main__":
    fig_cell_structure()
    fig_vth_distributions()
    fig_ispp_programming()
    fig_degradation_mechanisms()
    print("Усі 4 фігури успішно згенеровано у ./img/")
