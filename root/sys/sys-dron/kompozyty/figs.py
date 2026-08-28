# -*- coding: utf-8 -*-
"""Генератор векторних діаграм (SVG) для теми:
«Композити: вуглепластик і склопластик»
"""
import sys, os

# Шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_load_transfer():
    """Фігура 1: Мікроструктура волокно-матриця та розподіл напружень (модель shear-lag)."""
    w, h = 900, 430
    frags = []

    # Тло
    frags.append(rect(15, 15, 870, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Ліва панель: Схема волокна в матриці
    p1 = rect(35, 35, 410, 360, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(p1)
    frags.append(text(240, 65, "Передача напружень волокно–матриця", size=15, bold=True, color="#0f172a"))

    # Матриця (епоксид)
    frags.append(rect(55, 95, 370, 160, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=4))
    frags.append(text(75, 118, "Матриця (епоксидна смола)", size=12, bold=True, color="#b45309", anchor="start"))

    # Обірване волокно в центрі
    frags.append(rect(90, 160, 300, 32, fill="#334155", stroke="#0f172a", sw=1.5, rx=2))
    frags.append(text(240, 180, "Високомодульне волокно (CFRP / GFRP)", size=12, bold=True, color="#ffffff"))

    # Стрілки зовнішнього розтягу
    frags.append(arrow(390, 176, 430, 176, color="#dc2626", sw=2.5))
    frags.append(text(410, 165, "F_ext", size=12, bold=True, color="#dc2626"))

    # Дотичні напруження зсуву τ на границі
    for x_pos in [105, 125, 145, 165, 315, 335, 355, 375]:
        # верхня межа
        frags.append(line(x_pos, 152, x_pos + 12, 152, color="#2563eb", sw=1.8))
        frags.append(f'<polygon points="{x_pos + 15},152 {x_pos + 9},149 {x_pos + 9},155" fill="#2563eb"/>')
        # нижня межа
        frags.append(line(x_pos, 200, x_pos + 12, 200, color="#2563eb", sw=1.8))
        frags.append(f'<polygon points="{x_pos + 15},200 {x_pos + 9},197 {x_pos + 9},203" fill="#2563eb"/>')

    frags.append(text(240, 142, "Дотичні напруження зсуву τ_i на межі розділу", size=11, color="#1d4ed8", bold=True))

    # Зона критичної довжини l_c
    frags.append(line(90, 215, 90, 245, color="#64748b", sw=1, dash="3,2"))
    frags.append(line(240, 215, 240, 245, color="#64748b", sw=1, dash="3,2"))
    frags.append(line(390, 215, 390, 245, color="#64748b", sw=1, dash="3,2"))
    frags.append(arrow(165, 235, 90, 235, color="#475569", sw=1.2))
    frags.append(arrow(165, 235, 240, 235, color="#475569", sw=1.2))
    frags.append(text(165, 230, "l_c / 2", size=11, color="#475569", bold=True))

    desc_left = fitbox(55, 268, 370, 115,
                       "• Матриця сприймає поперечні сили та зсув\n"
                       "• Через дотичні напруження τ_i навантаження передається волокнам\n"
                       "• При довжині волокна l > l_c напруження досягає повної межі міцності",
                       size=11, pad=8, fill="#f1f5f9", stroke="#cbd5e1")
    frags.append(desc_left)

    # Права панель: Епюри напружень
    p2 = rect(460, 35, 405, 360, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(p2)
    frags.append(text(662, 65, "Розподіл напружень вздовж волокна", size=15, bold=True, color="#0f172a"))

    # Графік 1: Дотичне напруження τ(x)
    frags.append(line(490, 175, 830, 175, color="#94a3b8", sw=1.2))
    frags.append(line(490, 95, 490, 175, color="#94a3b8", sw=1.2))
    frags.append(text(835, 178, "x", size=12, color="#64748b", anchor="start"))
    frags.append(text(480, 105, "τ_i", size=12, color="#2563eb", bold=True, anchor="end"))

    # Крива τ(x)
    frags.append('<path d="M 510,115 Q 540,165 660,175 Q 780,165 810,115" fill="none" stroke="#2563eb" stroke-width="2.5"/>')
    frags.append(text(555, 130, "Максимум на краях (τ_max)", size=10, color="#1d4ed8", anchor="start"))

    # Графік 2: Нормальне напруження у волокні σ_f(x)
    frags.append(line(490, 275, 830, 275, color="#94a3b8", sw=1.2))
    frags.append(line(490, 195, 490, 275, color="#94a3b8", sw=1.2))
    frags.append(text(835, 278, "x", size=12, color="#64748b", anchor="start"))
    frags.append(text(480, 205, "σ_f", size=12, color="#dc2626", bold=True, anchor="end"))

    # Крива σ_f(x)
    frags.append('<path d="M 495,275 L 550,235 L 770,235 L 825,275" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    frags.append(text(660, 220, "Плато σ_f,max (повне завантаження)", size=10, color="#dc2626", bold=True))

    desc_right = fitbox(480, 295, 365, 88,
                        "Критична довжина передачі зусилля:\n"
                        "l_c = (σ_f * d) / (2 * τ_c)\n"
                        "Короткі волокна (l < l_c) висмикуються без розриву.",
                        size=11, pad=8, fill="#eff6ff", stroke="#bfdbfe")
    frags.append(desc_right)

    render(os.path.join(OUT_DIR, "composite-load-transfer.svg"), w, h, *frags)


def fig_layup_anisotropy():
    """Фігура 2: Структура плетіння та квазіізотропний пакет шарів."""
    w, h = 900, 440
    frags = []

    # Тло
    frags.append(rect(15, 15, 870, 410, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Ліва частина: Типи плетіння (UD, Plain, Twill)
    p1 = rect(35, 35, 410, 370, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(p1)
    frags.append(text(240, 65, "Форми напівфабрикатів волокна", size=15, bold=True, color="#0f172a"))

    # Блок 1: Односпрямована стрічка (UD)
    frags.append(rect(55, 85, 370, 85, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(70, 105, "Односпрямована стрічка (UD Tape, 0°)", size=12, bold=True, color="#1e293b", anchor="start"))
    for y_l in range(118, 160, 8):
        frags.append(line(70, y_l, 250, y_l, color="#334155", sw=2.5))
    frags.append(text(270, 130, "E_1 = 140 ГПа", size=11, bold=True, color="#0f172a", anchor="start"))
    frags.append(text(270, 148, "E_2 = 9 ГПа (анізотропія 15:1)", size=10, color="#64748b", anchor="start"))

    # Блок 2: Тканина Plain Weave 1x1
    frags.append(rect(55, 180, 370, 95, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(70, 200, "Полотняна тканина (Plain 1x1, 3K)", size=12, bold=True, color="#1e293b", anchor="start"))
    # Сітка 1x1
    for x_i in range(70, 170, 16):
        frags.append(rect(x_i, 212, 12, 50, fill="#475569", stroke="#1e293b", sw=0.8))
    for y_i in range(215, 260, 14):
        frags.append(rect(68, y_i, 105, 10, fill="#94a3b8", stroke="#334155", sw=0.8))
    frags.append(text(190, 225, "• Стабільна геометрія", size=10, color="#334155", anchor="start"))
    frags.append(text(190, 242, "• Високий вигин волокон (crimp)", size=10, color="#dc2626", anchor="start"))
    frags.append(text(190, 259, "• Міцність ~85% від UD", size=10, color="#475569", anchor="start"))

    # Блок 3: Тканина Twill Weave 2x2
    frags.append(rect(55, 285, 370, 105, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(70, 305, "Саржева тканина (Twill 2x2, 3K)", size=12, bold=True, color="#1e293b", anchor="start"))
    frags.append(text(190, 330, "• Менший вигин ниток", size=10, color="#16a34a", bold=True, anchor="start"))
    frags.append(text(190, 348, "• Легко драпує криволінійні форми", size=10, color="#334155", anchor="start"))
    frags.append(text(190, 366, "• Стандарт для пластин дронів", size=10, color="#0f172a", anchor="start"))
    # Діагональний візерунок саржі
    for xi in range(70, 165, 18):
        frags.append(rect(xi, 318, 14, 60, fill="#334155", stroke="#0f172a", sw=0.8))
    for yi in range(322, 375, 16):
        frags.append(rect(68, yi, 105, 11, fill="#64748b", stroke="#1e293b", sw=0.8))

    # Права частина: Квазіізотропна укладка
    p2 = rect(460, 35, 410, 370, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(p2)
    frags.append(text(665, 65, "Квазіізотропний ламінат [0/45/-45/90]_s", size=15, bold=True, color="#0f172a"))

    # Шари укладки (вигляд шарів під кутами)
    layers = [
        ("Шар 1: 0° (поздовжній вигин)", "#334155", 95),
        ("Шар 2: +45° (кручення / зсув)", "#475569", 125),
        ("Шар 3: -45° (кручення / зсув)", "#64748b", 155),
        ("Шар 4: 90° (поперечна жорсткість)", "#94a3b8", 185),
        ("Шар 5: 90° (симетрія пакета)", "#94a3b8", 215),
        ("Шар 6: -45° (симетрія пакета)", "#64748b", 245),
        ("Шар 7: +45° (симетрія пакета)", "#475569", 275),
        ("Шар 8: 0° (симетрія пакета)", "#334155", 305),
    ]
    for lbl, col, y_pos in layers:
        frags.append(rect(480, y_pos, 130, 22, fill=col, stroke="#0f172a", sw=0.8, rx=2))
        frags.append(text(620, y_pos + 15, lbl, size=11, color="#1e293b", anchor="start"))

    box_sym = fitbox(480, 335, 370, 58,
                     "Симетрична укладка відносно центру (індекс s)\n"
                     "гарантує B_ij = 0 (відсутність температурного короблення).",
                     size=10, pad=6, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(box_sym)

    render(os.path.join(OUT_DIR, "carbon-fiber-layup.svg"), w, h, *frags)


def fig_rf_behavior():
    """Фігура 3: Взаємодія радіохвиль з вуглепластиком та склопластиком."""
    w, h = 900, 430
    frags = []

    # Тло
    frags.append(rect(15, 15, 870, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Ліва панель: Вуглепластик (CFRP)
    p1 = rect(35, 35, 410, 360, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(p1)
    frags.append(text(240, 65, "Вуглепластик (CFRP): Екранування", size=15, bold=True, color="#0f172a"))

    # Антена над карбоном
    frags.append(rect(225, 95, 30, 30, fill="#f59e0b", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(240, 114, "TX", size=11, bold=True, color="#ffffff"))
    frags.append(text(240, 140, "Антена GNSS / VTX", size=11, color="#b45309", bold=True))

    # Хвилі вниз до карбону
    frags.append('<path d="M 210,150 C 230,165 250,165 270,150" fill="none" stroke="#f59e0b" stroke-width="2"/>')
    frags.append('<path d="M 195,165 C 230,185 250,185 285,165" fill="none" stroke="#f59e0b" stroke-width="2"/>')

    # Карбонова пластина
    frags.append(rect(65, 185, 350, 30, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=3))
    frags.append(text(240, 204, "Карбонова рама (σ_e ≈ 10⁴ См/м)", size=12, bold=True, color="#ffffff"))

    # Відбиті хвилі та вихрові струми
    frags.append('<path d="M 190,180 C 160,150 140,130 110,110" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="4,3"/>')
    frags.append('<path d="M 290,180 C 320,150 340,130 370,110" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="4,3"/>')
    frags.append(text(120, 100, "Відбиття хвилі", size=10, color="#dc2626", bold=True))
    frags.append(text(360, 100, "Багатопроменевість", size=10, color="#dc2626", bold=True))

    # Зона затінення внизу
    frags.append(rect(65, 225, 350, 40, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=3))
    frags.append(text(240, 248, "Радіотінь: затухання > 40–70 дБ (клітка Фарадея)", size=11, bold=True, color="#991b1b"))

    box_cfrp = fitbox(55, 280, 370, 100,
                      "• Карбон проводить струм і блокує радіосигнал\n"
                      "• Антени не можна розміщувати всередині карбонового фюзеляжу\n"
                      "• Силові плати (ESC/PDB) вимагають діелектричної ізоляції",
                      size=11, pad=8, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(box_cfrp)

    # Права панель: Склопластик (GFRP)
    p2 = rect(460, 35, 410, 360, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(p2)
    frags.append(text(665, 65, "Склопластик (GFRP): Радіопрозорість", size=15, bold=True, color="#0f172a"))

    # Антена над склопластиком
    frags.append(rect(650, 95, 30, 30, fill="#2563eb", stroke="#1d4ed8", sw=1.5, rx=3))
    frags.append(text(665, 114, "TX", size=11, bold=True, color="#ffffff"))
    frags.append(text(665, 140, "Вбудована антена", size=11, color="#1d4ed8", bold=True))

    # Склопластикова пластина / купол
    frags.append(rect(490, 185, 350, 30, fill="#dbeafe", stroke="#93c5fd", sw=1.5, rx=3))
    frags.append(text(665, 204, "Склопластик (GFRP: ε_r ≈ 4.5, діелектрик)", size=12, bold=True, color="#1e40af"))

    # Хвилі проходять крізь пластину
    frags.append('<path d="M 630,150 C 650,165 680,165 700,150" fill="none" stroke="#2563eb" stroke-width="2"/>')
    frags.append('<path d="M 620,180 C 650,195 680,195 710,180" fill="none" stroke="#2563eb" stroke-width="2"/>')
    frags.append('<path d="M 610,225 C 650,245 680,245 720,225" fill="none" stroke="#16a34a" stroke-width="2.5"/>')
    frags.append('<path d="M 590,245 C 650,270 680,270 740,245" fill="none" stroke="#16a34a" stroke-width="2.5"/>')

    frags.append(text(665, 260, "Пряме проходження (втрати < 0.5 дБ)", size=11, bold=True, color="#15803d"))

    box_gfrp = fitbox(480, 280, 370, 100,
                      "• Склопластик та кевлар є діелектриками\n"
                      "• Ідеально підходять для антенних обтічників (radomes)\n"
                      "• Дозволяють вбудовувати антени всередину конструкції променя",
                      size=11, pad=8, fill="#f0fdf4", stroke="#bbf7d0")
    frags.append(box_gfrp)

    render(os.path.join(OUT_DIR, "rf-behavior-carbon-vs-fiberglass.svg"), w, h, *frags)


def fig_failure_modes():
    """Фігура 4: Механізми руйнування композитів (розшарування, мікрозминання, тріщини смоли)."""
    w, h = 900, 440
    frags = []

    # Тло
    frags.append(rect(15, 15, 870, 410, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(450, 45, "Механізми руйнування шаруватих композитів", size=16, bold=True, color="#0f172a"))

    # 4 квадранти (панелі 2x2)
    # Квадрант 1: Міжшарове розшарування (Delamination)
    q1 = rect(35, 65, 400, 165, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(q1)
    frags.append(text(235, 88, "1. Міжшарове розшарування (Delamination)", size=13, bold=True, color="#b91c1c"))
    # Шари з розривом
    frags.append(rect(55, 105, 150, 14, fill="#475569", stroke="#1e293b", sw=1, rx=2))
    frags.append(rect(55, 125, 350, 14, fill="#475569", stroke="#1e293b", sw=1, rx=2))
    frags.append(rect(55, 145, 350, 14, fill="#475569", stroke="#1e293b", sw=1, rx=2))
    frags.append('<path d="M 205,105 Q 260,90 350,85" fill="none" stroke="#dc2626" stroke-width="3"/>')
    frags.append(text(280, 115, "Розрив смоли між шарами (Мода I/II)", size=10, color="#dc2626", bold=True))
    frags.append(text(235, 175, "Головний дефект при ударах та згині", size=11, color="#64748b"))
    frags.append(text(235, 195, "Знижує міцність на стиск на 50% (BVID)", size=10, color="#b91c1c", bold=True))

    # Квадрант 2: Матричне розтріскування (Matrix Cracking)
    q2 = rect(465, 65, 400, 165, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(q2)
    frags.append(text(665, 88, "2. Тріщини матриці (Matrix Cracking)", size=13, bold=True, color="#b45309"))
    frags.append(rect(485, 105, 360, 45, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=3))
    # Волокна
    frags.append(line(495, 118, 835, 118, color="#78350f", sw=2))
    frags.append(line(495, 138, 835, 138, color="#78350f", sw=2))
    # Поперечні тріщини в смолі
    for xc in [550, 620, 690, 760]:
        frags.append(line(xc, 105, xc + 10, 150, color="#dc2626", sw=2.5))
    frags.append(text(665, 175, "Тріщини в епоксиді перпендикулярно напруженню", size=11, color="#64748b"))
    frags.append(text(665, 195, "Відкриває шлях волозі, ініціює втому", size=10, color="#b45309", bold=True))

    # Квадрант 3: Втрата стійкості волокон при стиску (Microbuckling)
    q3 = rect(35, 245, 400, 165, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(q3)
    frags.append(text(235, 268, "3. Зминання волокон при стиску (Microbuckling)", size=13, bold=True, color="#4338ca"))
    # Вигнуті волокна під стиском
    frags.append(rect(55, 285, 360, 45, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=3))
    frags.append('<path d="M 65,300 L 160,300 Q 190,285 220,315 Q 250,285 280,300 L 405,300" fill="none" stroke="#334155" stroke-width="2.5"/>')
    frags.append('<path d="M 65,315 L 160,315 Q 190,300 220,330 Q 250,300 280,315 L 405,315" fill="none" stroke="#334155" stroke-width="2.5"/>')
    frags.append(arrow(60, 307, 100, 307, color="#dc2626", sw=2))
    frags.append(arrow(410, 307, 370, 307, color="#dc2626", sw=2))
    frags.append(text(235, 355, "Пластична смуга злому (kink-band)", size=11, color="#64748b"))
    frags.append(text(235, 375, "Міцність на стиск на 40% нижча за розтяг", size=10, color="#4338ca", bold=True))

    # Квадрант 4: Висмикування та розрив волокон (Pull-out)
    q4 = rect(465, 245, 400, 165, fill="#ffffff", stroke="#e2e8f0", sw=1.2, rx=6)
    frags.append(q4)
    frags.append(text(665, 268, "4. Визволення волокон (Fiber Pull-out)", size=13, bold=True, color="#15803d"))
    frags.append(rect(485, 285, 140, 45, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=3))
    frags.append(rect(705, 285, 140, 45, fill="#fef3c7", stroke="#f59e0b", sw=1.2, rx=3))
    # Волокно, що висмикнулося
    frags.append(rect(625, 298, 80, 18, fill="#1e293b", stroke="#0f172a", sw=1, rx=2))
    frags.append(arrow(655, 307, 490, 307, color="#dc2626", sw=1.5))
    frags.append(arrow(675, 307, 820, 307, color="#dc2626", sw=1.5))
    frags.append(text(665, 355, "Втрата адгезії волокна до смоли", size=11, color="#64748b"))
    frags.append(text(665, 375, "Поглинає енергію удару (в'язке руйнування)", size=10, color="#15803d", bold=True))

    render(os.path.join(OUT_DIR, "composite-failure-modes.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_load_transfer()
    fig_layup_anisotropy()
    fig_rf_behavior()
    fig_failure_modes()
    print("Всі 4 фігури успішно згенеровано.")
