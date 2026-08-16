# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)

def gen_domain_structure():
    """Фігура 1: Перехід фаз та доменна структура сегнетоелектрика (BaTiO3)."""
    w, h = 800, 360
    frags = []
    
    # Заголовок / розділення на 2 панелі
    frags.append(rect(10, 40, 380, 300, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(200, 65, "Кристалічна ґратка BaTiO₃", size=15, bold=True, anchor="middle", color=INK))
    
    # Сліва: T > Tc (кубічна)
    frags.append(rect(30, 90, 160, 160, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(110, 115, "T > T_c (Параелектрик)", size=12, bold=True, anchor="middle", color=MUTED))
    # Вершини Барій / Кишеньки Оксиген / Титан
    frags.append(circle(50, 140, 10, fill="#3b82f6", stroke="#1d4ed8")) # Ba
    frags.append(circle(170, 140, 10, fill="#3b82f6", stroke="#1d4ed8"))
    frags.append(circle(50, 220, 10, fill="#3b82f6", stroke="#1d4ed8"))
    frags.append(circle(170, 220, 10, fill="#3b82f6", stroke="#1d4ed8"))
    frags.append(circle(110, 140, 7, fill="#ef4444", stroke="#b91c1c")) # O
    frags.append(circle(110, 220, 7, fill="#ef4444", stroke="#b91c1c"))
    frags.append(circle(50, 180, 7, fill="#ef4444", stroke="#b91c1c"))
    frags.append(circle(170, 180, 7, fill="#ef4444", stroke="#b91c1c"))
    frags.append(circle(110, 180, 8, fill="#10b981", stroke="#047857")) # Ti в центрі
    frags.append(text(110, 275, "Центросиметрична", size=11, anchor="middle", color=INK))
    frags.append(text(110, 290, "P = 0", size=12, bold=True, anchor="middle", color=POS))

    # Справа: T < Tc (тетрагональна зі зсувом Ti4+)
    frags.append(rect(210, 90, 160, 160, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(290, 115, "T < T_c (Сегнетоелектрик)", size=12, bold=True, anchor="middle", color=MUTED))
    frags.append(circle(230, 140, 10, fill="#3b82f6", stroke="#1d4ed8"))
    frags.append(circle(350, 140, 10, fill="#3b82f6", stroke="#1d4ed8"))
    frags.append(circle(230, 220, 10, fill="#3b82f6", stroke="#1d4ed8"))
    frags.append(circle(350, 220, 10, fill="#3b82f6", stroke="#1d4ed8"))
    frags.append(circle(290, 140, 7, fill="#ef4444", stroke="#b91c1c"))
    frags.append(circle(290, 220, 7, fill="#ef4444", stroke="#b91c1c"))
    frags.append(circle(230, 180, 7, fill="#ef4444", stroke="#b91c1c"))
    frags.append(circle(350, 180, 7, fill="#ef4444", stroke="#b91c1c"))
    # Ti4+ зсунутий вгору на 12px
    frags.append(circle(290, 168, 8, fill="#10b981", stroke="#047857"))
    frags.append(arrow(290, 195, 290, 150, color=POS, sw=2.2))
    frags.append(text(290, 275, "Зсув Ti⁴⁺ вгору", size=11, anchor="middle", color=INK))
    frags.append(text(290, 290, "P_s > 0", size=12, bold=True, anchor="middle", color=POS))

    # Права панель: Доменна структура
    frags.append(rect(410, 40, 380, 300, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(600, 65, "Доменна структура монокристала", size=15, bold=True, anchor="middle", color=INK))
    
    # 4 домени зі стінками 180° та 90°
    frags.append(rect(440, 90, 320, 180, fill="#ffffff", stroke="#475569", sw=2, rx=4))
    
    # Домен 1 (ліворуч, вгору)
    frags.append(rect(440, 90, 80, 180, fill="#eff6ff", stroke="#93c5fd", sw=1))
    frags.append(arrow(480, 230, 480, 120, color=NEG, sw=2.5))
    frags.append(text(480, 105, "Домен A", size=11, anchor="middle", color=MUTED))
    
    # Лінія 180° стінки
    frags.append(line(520, 90, 520, 270, color=POS, sw=2, dash="4,4"))
    
    # Домен 2 (вниз)
    frags.append(rect(520, 90, 80, 180, fill="#fef2f2", stroke="#fca5a5", sw=1))
    frags.append(arrow(560, 130, 560, 240, color=POS, sw=2.5))
    frags.append(text(560, 105, "Домен B", size=11, anchor="middle", color=MUTED))
    
    # Лінія 90° стінки (діагональна)
    frags.append(line(600, 90, 760, 270, color="#8b5cf6", sw=2, dash="4,4"))
    
    # Домен 3 (праворуч вгорі, вправо)
    frags.append(arrow(620, 140, 720, 140, color=FIELD, sw=2.5))
    frags.append(text(670, 120, "Домен C (90°)", size=11, anchor="middle", color=MUTED))
    
    # Домен 4 (праворуч внизу, вниз)
    frags.append(arrow(660, 200, 660, 255, color=POS, sw=2.5))
    
    frags.append(text(520, 290, "180° стінка", size=11, bold=True, anchor="middle", color=POS))
    frags.append(text(680, 290, "90° стінка", size=11, bold=True, anchor="middle", color="#8b5cf6"))
    frags.append(text(600, 320, "Мінімізація деполяризаційного поля та пружної енергії", size=12, anchor="middle", color=INK))

    render(os.path.join(IMG_DIR, "ferroelectric-domain-structure.svg"), w, h, *frags)

def gen_hysteresis_loop():
    """Фігура 2: Петля сегнетоелектричного гістерезису P(E)."""
    w, h = 640, 480
    frags = []
    
    # Осі координат
    cx, cy = 320, 240
    frags.append(arrow(60, cy, 580, cy, color=LINE, sw=1.8)) # E
    frags.append(arrow(cx, 440, cx, 40, color=LINE, sw=1.8))  # P
    frags.append(text(570, cy + 25, "Напруженість поля E", size=13, bold=True, anchor="end", color=INK))
    frags.append(text(cx + 15, 55, "Поляризація P", size=13, bold=True, anchor="start", color=INK))
    
    # Петля (path)
    frags.append('<path d="M 320 240 Q 380 230, 420 180 T 480 100" fill="none" stroke="#94a3b8" stroke-width="1.8" stroke-dasharray="5,5"/>')
    frags.append(text(390, 220, "Первинна крива", size=11, italic=True, color=MUTED))

    # Головна петля
    path_d = ("M 480 100 C 400 105, 340 115, 320 130 "
              "C 280 160, 230 200, 200 240 "
              "C 180 270, 165 340, 160 380 "
              "C 240 375, 300 365, 320 350 "
              "C 360 320, 410 280, 440 240 "
              "C 460 210, 475 140, 480 100 Z")
    frags.append('<path d="%s" fill="rgba(39, 174, 96, 0.08)" stroke="%s" stroke-width="2.8"/>' % (path_d, FIELD))
    
    # Ключові точки та пунктири
    # P_r
    frags.append(circle(cx, 130, 5, fill=POS, stroke="#ffffff", sw=1))
    frags.append(line(cx, 130, cx - 120, 130, color=POS, sw=1, dash="3,3"))
    frags.append(text(cx - 10, 125, "+P_r (Залишкова поляризація)", size=12, bold=True, anchor="end", color=POS))
    
    # -P_r
    frags.append(circle(cx, 350, 5, fill=POS, stroke="#ffffff", sw=1))
    frags.append(text(cx + 10, 358, "-P_r", size=12, bold=True, anchor="start", color=POS))

    # E_c
    frags.append(circle(440, cy, 5, fill=NEG, stroke="#ffffff", sw=1))
    frags.append(text(440, cy + 20, "+E_c", size=12, bold=True, anchor="middle", color=NEG))
    frags.append(text(440, cy + 35, "(Коерцитивне поле)", size=11, anchor="middle", color=NEG))
    
    # -E_c
    frags.append(circle(200, cy, 5, fill=NEG, stroke="#ffffff", sw=1))
    frags.append(text(200, cy - 12, "-E_c", size=12, bold=True, anchor="middle", color=NEG))

    # P_s / P_sat
    frags.append(circle(480, 100, 5, fill=INK, stroke="#ffffff", sw=1))
    frags.append(line(480, 100, cx, 100, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(cx - 10, 98, "P_s (Спонтанна / Насичена)", size=12, bold=True, anchor="end", color=INK))

    tb, _, _ = textbox(500, 400, "Площа петлі W = ∮ E dP\n(Енергетичні втрати\nна один цикл)", size=11, pad=8, fill="#ffffff", stroke="#cbd5e1")
    frags.append(tb)

    render(os.path.join(IMG_DIR, "hysteresis-loop.svg"), w, h, *frags)

def gen_landau_potential():
    """Фігура 3: Термодинамічний потенціал Ландау F(P) для різних температур."""
    w, h = 720, 420
    frags = []
    
    # Панель 1: T > Tc
    frags.append(rect(20, 50, 210, 320, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(125, 75, "T > T_c", size=14, bold=True, anchor="middle", color=NEG))
    frags.append(text(125, 95, "Параелектрична фаза", size=11, anchor="middle", color=MUTED))
    frags.append(arrow(125, 330, 125, 110, color=LINE, sw=1.2))
    frags.append(arrow(35, 290, 215, 290, color=LINE, sw=1.2))
    frags.append(text(210, 308, "P", size=12, bold=True, anchor="end", color=INK))
    frags.append(text(135, 120, "F(P)", size=12, bold=True, anchor="start", color=INK))
    frags.append('<path d="M 45 140 Q 125 290, 205 140" fill="none" stroke="%s" stroke-width="2.5"/>' % NEG)
    frags.append(circle(125, 290, 5, fill=NEG, stroke="#ffffff", sw=1))
    frags.append(text(125, 355, "Єдиний мінімум\nпри P = 0", size=11, anchor="middle", color=INK))

    # Панель 2: T = Tc
    frags.append(rect(255, 50, 210, 320, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(360, 75, "T = T_c", size=14, bold=True, anchor="middle", color=FIELD))
    frags.append(text(360, 95, "Критична точка", size=11, anchor="middle", color=MUTED))
    frags.append(arrow(360, 330, 360, 110, color=LINE, sw=1.2))
    frags.append(arrow(270, 290, 450, 290, color=LINE, sw=1.2))
    frags.append(text(445, 308, "P", size=12, bold=True, anchor="end", color=INK))
    frags.append(text(370, 120, "F(P)", size=12, bold=True, anchor="start", color=INK))
    frags.append('<path d="M 280 140 C 330 288, 330 290, 360 290 C 390 290, 390 288, 440 140" fill="none" stroke="%s" stroke-width="2.5"/>' % FIELD)
    frags.append(text(360, 355, "Незбуджена сприйнятливість\nχ → ∞", size=11, anchor="middle", color=INK))

    # Панель 3: T < Tc
    frags.append(rect(490, 50, 210, 320, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(595, 75, "T < T_c", size=14, bold=True, anchor="middle", color=POS))
    frags.append(text(595, 95, "Сегнетоелектрична фаза", size=11, anchor="middle", color=MUTED))
    frags.append(arrow(595, 330, 595, 110, color=LINE, sw=1.2))
    frags.append(arrow(505, 290, 685, 290, color=LINE, sw=1.2))
    frags.append(text(680, 308, "P", size=12, bold=True, anchor="end", color=INK))
    frags.append(text(605, 120, "F(P)", size=12, bold=True, anchor="start", color=INK))
    w_path = ("M 515 140 C 530 240, 535 295, 545 295 "
              "C 560 295, 575 240, 595 240 "
              "C 615 240, 630 295, 645 295 "
              "C 655 295, 665 240, 675 140")
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (w_path, POS))
    frags.append(circle(545, 295, 5, fill=POS, stroke="#ffffff", sw=1))
    frags.append(circle(645, 295, 5, fill=POS, stroke="#ffffff", sw=1))
    frags.append(text(545, 315, "-P_s", size=11, bold=True, anchor="middle", color=POS))
    frags.append(text(645, 315, "+P_s", size=11, bold=True, anchor="middle", color=POS))
    frags.append(text(595, 355, "Двоямний потенціал:\n2 стійкі стани (0 та 1)", size=11, anchor="middle", color=INK))

    render(os.path.join(IMG_DIR, "landau-potential.svg"), w, h, *frags)

def gen_feram_cell():
    """Фігура 4: Схема та принцип дії 1T1C комірки FeRAM."""
    w, h = 680, 400
    frags = []
    
    # Word Line
    frags.append(line(80, 80, 580, 80, color=NEG, sw=2.5))
    frags.append(text(70, 85, "Word Line (WL)", size=12, bold=True, anchor="end", color=NEG))
    
    # Bit Line
    frags.append(line(160, 40, 160, 360, color=POS, sw=2.5))
    frags.append(text(160, 30, "Bit Line (BL)", size=12, bold=True, anchor="middle", color=POS))
    
    # Plate Line
    frags.append(line(80, 300, 580, 300, color=FIELD, sw=2.5))
    frags.append(text(70, 305, "Plate Line (PL)", size=12, bold=True, anchor="end", color=FIELD))

    # Селекторний MOSFET (T)
    frags.append(circle(160, 180, 4, fill=INK))
    frags.append(line(160, 180, 240, 180, color=LINE, sw=2))
    
    frags.append(rect(240, 140, 60, 80, fill="#ffffff", stroke=LINE, sw=2, rx=4))
    frags.append(text(270, 185, "NMOS\n(T)", size=12, bold=True, anchor="middle", color=INK))
    frags.append(line(270, 140, 270, 80, color=NEG, sw=2))
    frags.append(circle(270, 80, 4, fill=NEG))
    
    frags.append(line(300, 180, 380, 180, color=LINE, sw=2))
    frags.append(text(340, 170, "Вузол SN", size=11, color=MUTED, anchor="middle"))

    # C_fe
    frags.append(rect(380, 140, 100, 80, fill="#fef3c7", stroke="#d97706", sw=2, rx=6))
    frags.append(line(395, 155, 395, 205, color="#b45309", sw=3))
    frags.append(line(465, 155, 465, 205, color="#b45309", sw=3))
    frags.append(text(430, 175, "C_fe", size=13, bold=True, anchor="middle", color="#b45309"))
    frags.append(text(430, 195, "PZT/HfO₂", size=10, anchor="middle", color=MUTED))

    frags.append(line(480, 180, 520, 180, color=LINE, sw=2))
    frags.append(line(520, 180, 520, 300, color=FIELD, sw=2))
    frags.append(circle(520, 300, 4, fill=FIELD))

    frags.append(fitbox(450, 320, 210, 65, "Логічна '1': +P_r\nЛогічна '0': -P_r\nПеремикання видає ΔQ", size=11, fill="#ffffff", stroke="#cbd5e1"))
    frags.append(fitbox(240, 320, 180, 65, "Руйнівне зчитування:\nІмпульс на PL створює\nструм переполяризації", size=11, fill="#ffffff", stroke="#cbd5e1"))

    render(os.path.join(IMG_DIR, "feram-cell-circuit.svg"), w, h, *frags)

if __name__ == "__main__":
    gen_domain_structure()
    gen_hysteresis_loop()
    gen_landau_potential()
    gen_feram_cell()
    print("Всі фігури згенеровано успішно.")
