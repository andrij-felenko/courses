# -*- coding: utf-8 -*-
"""Фігури до теми «Живлення антен: балун, гама-узгоджувач, узгодження імпедансів».
Запуск: python figs.py  → створює SVG у ./img/
Стиль та помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Додаткові кольори палітри
WAVE      = "#c0392b"  # падаюча хвиля / струм сигнальний
WAVE_CM   = "#e67e22"  # струм спільної моди (помаранчевий)
ACCENT    = "#8e44ad"  # реактивність / балун / гама-узгоджувач
FERRITE   = "#4a5568"  # ферит (темно-сірий)
COAX_SH   = "#718096"  # екран коаксіалу
BORDER    = INK        # межа карточок


# ── 1. Струми спільної моди при прямому підключенні та пригнічення балуном ─────
def fig_common_mode_current():
    W, H = 820, 420
    f = [text(W / 2, 26, "Виникнення струмів спільної моди та дія струмового балуна", size=15, bold=True)]

    # Ліва частина (без балуна - проблема)
    f.append(rect(20, 50, 380, 290, fill="#fdfefe", stroke=MUTED, sw=1, rx=8))
    f.append(text(210, 75, "Пряме підключення (без балуна)", size=13, bold=True, color=POS))
    
    # Диполь ліворуч
    f.append(line(70, 120, 200, 120, color=POS, sw=3))   # Ліве плече
    f.append(line(220, 120, 350, 120, color=POS, sw=3))  # Праве плече
    f.append(circle(200, 120, 4, fill=POS, stroke=POS))
    f.append(circle(220, 120, 4, fill=POS, stroke=POS))
    f.append(text(135, 105, "Плече A (I_A)", size=11, bold=True, color=POS))
    f.append(text(285, 105, "Плече B (I_B)", size=11, bold=True, color=POS))

    # Коаксіал ліворуч
    f.append(rect(190, 140, 40, 150, fill="#edf2f7", stroke=COAX_SH, sw=1.5, rx=3))
    f.append(line(200, 120, 200, 140, color=POS, sw=2))  # Центр жила до плеча A
    f.append(line(220, 120, 220, 140, color=COAX_SH, sw=2)) # Екран до плеча B
    f.append(text(210, 220, "Коаксіал", size=11, color=MUTED))

    # Струми ліворуч
    f.append(arrow(200, 180, 200, 145, color=POS, sw=2))
    f.append(text(175, 165, "I_in", size=10, bold=True, color=POS))
    
    # Витік струму спільної моди I_cm на зовнішню поверхню
    f.append(arrow(235, 150, 235, 270, color=WAVE_CM, sw=2.5))
    f.append(text(290, 210, "Струм I_cm на", size=11, bold=True, color=WAVE_CM))
    f.append(text(290, 226, "зовнішньому екрані!", size=11, bold=True, color=WAVE_CM))
    f.append(text(210, 320, "Результат: I_A ≠ I_B, випромінювання кабелю", size=10, bold=True, color=POS))

    # Права частина (з балуном Гуанелла - рішення)
    f.append(rect(420, 50, 380, 290, fill="#fcfdfd", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(610, 75, "Зі струмовим балуном (Guanella 1:1)", size=13, bold=True, color=FIELD))

    # Диполь праворуч
    f.append(line(470, 120, 600, 120, color=FIELD, sw=3))
    f.append(line(620, 120, 750, 120, color=FIELD, sw=3))
    f.append(circle(600, 120, 4, fill=FIELD, stroke=FIELD))
    f.append(circle(620, 120, 4, fill=FIELD, stroke=FIELD))
    f.append(text(535, 105, "I_A", size=11, bold=True, color=FIELD))
    f.append(text(685, 105, "I_B = -I_A", size=11, bold=True, color=FIELD))

    # Кабель і феритове кільце (балун)
    f.append(rect(590, 210, 40, 110, fill="#edf2f7", stroke=COAX_SH, sw=1.5, rx=3))
    # Ферит
    f.append(rect(575, 150, 70, 45, fill=FERRITE, stroke=INK, sw=1.5, rx=6))
    f.append(text(610, 177, "Ферит (Z_cm)", size=11, bold=True, color=BG))
    
    f.append(line(600, 120, 600, 150, color=FIELD, sw=2))
    f.append(line(620, 120, 620, 150, color=FIELD, sw=2))

    # Блокування I_cm
    f.append(line(635, 195, 635, 230, color=MUTED, sw=1.5, dash="3,3"))
    f.append(text(710, 175, "Високий Z_cm", size=11, bold=True, color=FIELD))
    f.append(text(710, 192, "блокує I_cm", size=11, color=MUTED))

    f.append(text(610, 320, "Симетрію відновлено: I_A = I_B, I_cm ≈ 0", size=10, bold=True, color=FIELD))

    # Пояснювальна картка
    f.append(fitbox(20, 350, 780, 55,
                    "Струмовий балун створює високий опір Z_cm для ВЧ-струмів на зовнішній поверхні екрана,\n"
                    "усуваючи паразитивне випромінювання фідера та спотворення діаграми спрямованості.",
                    size=11, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "common-mode-current.svg"), W, H, *f)


# ── 2. Топології Вольтного та Струмового балунів ──────────────────────────────
def fig_balun_topologies():
    W, H = 800, 380
    f = [text(W / 2, 26, "Схеми вольтного (Рутроф) та струмового (Гуанелла) балунів", size=15, bold=True)]

    # Ліва схема: Вольтний балун 1:1
    f.append(rect(20, 50, 370, 240, fill="#fcfcfd", stroke=MUTED, sw=1, rx=8))
    f.append(text(205, 75, "Вольтний балун 1:1 (Рутроф)", size=13, bold=True, color=ACCENT))
    f.append(text(205, 93, "Фіксує рівність напруг V_A = -V_B", size=11, color=MUTED))

    # Схема автотрансформатора
    f.append(rect(170, 115, 70, 110, fill=FILL, stroke=ACCENT, sw=1.8, rx=6))
    f.append(text(205, 170, "Осердя", size=11, bold=True, color=ACCENT))
    
    # Котушки
    f.append(line(70, 135, 170, 135, color=INK, sw=2)) # Вхід несиметричний
    f.append(text(100, 125, "50 Ом вхід", size=10, color=INK))
    f.append(line(70, 205, 170, 205, color=INK, sw=2)) # Земля
    f.append(line(120, 205, 120, 235, color=INK, sw=2)) # Позначка землі
    f.append(line(105, 235, 135, 235, color=INK, sw=2))

    # Виходи
    f.append(line(240, 135, 340, 135, color=POS, sw=2))
    f.append(line(240, 205, 340, 205, color=POS, sw=2))
    f.append(text(310, 122, "Клема A (+V)", size=10, bold=True, color=POS))
    f.append(text(310, 192, "Клема B (-V)", size=10, bold=True, color=POS))
    f.append(text(205, 268, "Недолік: при несиметрії навантаження I_A ≠ I_B", size=10, color=POS))

    # Права схема: Струмовий балун 1:1 Гуанелла
    f.append(rect(410, 50, 370, 240, fill="#fcfdfd", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(595, 75, "Струмовий балун 1:1 (Гуанелла)", size=13, bold=True, color=FIELD))
    f.append(text(595, 93, "Фіксує рівність струмів I_A = -I_B", size=11, color=MUTED))

    # Лінія передачі на осерді
    f.append(rect(540, 115, 110, 110, fill=FERRITE, stroke=INK, sw=1.8, rx=6))
    f.append(text(595, 170, "Феритове", size=11, bold=True, color=BG))
    f.append(text(595, 185, "осердя", size=11, bold=True, color=BG))

    # Вхідні провідники
    f.append(line(440, 135, 540, 135, color=INK, sw=2.5))
    f.append(line(440, 205, 540, 205, color=COAX_SH, sw=2.5))
    f.append(text(485, 122, "Жила", size=10, color=INK))
    f.append(text(485, 220, "Екран", size=10, color=COAX_SH))

    # Вихідні провідники
    f.append(line(650, 135, 750, 135, color=FIELD, sw=2.5))
    f.append(line(650, 205, 750, 205, color=FIELD, sw=2.5))
    f.append(text(715, 122, "Клема A (I_A)", size=10, bold=True, color=FIELD))
    f.append(text(715, 220, "Клема B (I_B)", size=10, bold=True, color=FIELD))

    f.append(text(595, 268, "Перевага: високе пригнічення струмів спільної моди", size=10, bold=True, color=FIELD))

    # Нижня картка
    f.append(fitbox(20, 305, 760, 60,
                    "Вольтний балун задає потенціали на клемах, але пропускає струм спільної моди при асиметрії землеємностей.\n"
                    "Струмовий балун (дросель) гарантує рівність струмів у плечах антени за будь-яких умов.",
                    size=11, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "balun-topologies.svg"), W, H, *f)


# ── 3. Конструкція та еквівалентна схема Гама-узгоджувача ──────────────────────
def fig_gamma_match_circuit():
    W, H = 820, 420
    f = [text(W / 2, 26, "Конструкція та еквівалентна електрична схема гама-узгоджувача", size=15, bold=True)]

    # Верхня частина: Фізична конструкція
    f.append(rect(20, 50, 780, 180, fill="#fdfefe", stroke=INK, sw=1.5, rx=8))
    f.append(text(410, 72, "Фізичне влаштування гама-узгоджувача на вібраторі", size=13, bold=True, color=INK))

    # Головний елемент антени (суцільна труба)
    f.append(rect(60, 100, 700, 20, fill="#e2e8f0", stroke="#4a5568", sw=2, rx=4))
    f.append(text(410, 114, "Нерозрізний випромінювальний елемент антени (заземлений на бум)", size=11, bold=True, color=INK))

    # Гама-стрижень (Gamma Rod)
    f.append(rect(220, 145, 260, 10, fill="#cbd5e0", stroke="#4a5568", sw=1.5, rx=2))
    f.append(text(350, 140, "Гама-стрижень (Gamma Rod)", size=10, bold=True, color=ACCENT))

    # Замикальна перемичка (Shorting Strap) — проведена лінією
    f.append(line(480, 110, 480, 150, color="#ed8936", sw=6))
    f.append(text(545, 130, "Рухома перемичка (L_γ)", size=10, bold=True, color="#c05621"))

    # Конденсатор C_γ і коаксіальний роз'єм
    f.append(rect(160, 138, 60, 24, fill="#feb2b2", stroke=POS, sw=1.5, rx=4))
    f.append(text(190, 154, "C_γ", size=11, bold=True, color=POS))

    # Коаксіальний кабель від роз'єму
    f.append(line(80, 150, 160, 150, color=INK, sw=2.5))
    f.append(line(80, 110, 80, 150, color=COAX_SH, sw=2)) # Земля екрану на центр випромінювача
    f.append(circle(80, 110, 4, fill=INK, stroke=INK))
    f.append(text(110, 172, "Вхід 50 Ом (коаксіал)", size=10, bold=True, color=INK))

    # Нижня частина: Еквівалентна електрична схема
    f.append(rect(20, 245, 780, 160, fill="#fcfdfd", stroke=ACCENT, sw=1.5, rx=8))
    f.append(text(410, 267, "Еквівалентна електрична схема", size=13, bold=True, color=ACCENT))

    # Елементи схеми
    f.append(line(60, 340, 140, 340, color=INK, sw=2)) # Вхід
    f.append(text(90, 328, "Вхід (50 Ом)", size=10, color=INK))

    # Послідовний C_γ
    f.append(line(140, 325, 140, 355, color=POS, sw=2))
    f.append(line(155, 325, 155, 355, color=POS, sw=2))
    f.append(line(155, 340, 220, 340, color=INK, sw=2))
    f.append(text(147, 312, "C_γ (компенсація)", size=10, bold=True, color=POS))

    # Індуктивність петлі L_γ
    f.append(rect(220, 330, 60, 20, fill="#e9d8fd", stroke=ACCENT, sw=1.5, rx=3))
    f.append(text(250, 344, "+j X_L", size=10, bold=True, color=ACCENT))
    f.append(line(280, 340, 380, 340, color=INK, sw=2))

    # Автотрансформаторний вузол (1:m)
    f.append(rect(380, 310, 80, 60, fill="#edf2f7", stroke=INK, sw=1.5, rx=4))
    f.append(text(420, 335, "Автотрансф.", size=10, bold=True, color=INK))
    f.append(text(420, 350, "m = (1+u)²", size=10, bold=True, color=ACCENT))

    f.append(line(460, 340, 560, 340, color=INK, sw=2))
    
    # Опір випромінювача R_ant
    f.append(rect(560, 325, 80, 30, fill="#feebc8", stroke="#c05621", sw=1.5, rx=4))
    f.append(text(600, 344, "Z_ant (15..25 Ом)", size=10, bold=True, color="#c05621"))
    
    f.append(line(640, 340, 720, 340, color=INK, sw=2))
    f.append(line(720, 340, 720, 380, color=INK, sw=2)) # Земля

    f.append(text(410, 395, "L_γ задає активний опір 50 Ом; C_γ обнуляє реактивність (+jX_L + -jX_C = 0)", size=10, bold=True, color=FIELD))

    render(os.path.join(IMG, "gamma-match-circuit.svg"), W, H, *f)


# ── 4. Схеми Т-узгоджувача, Дельта-узгоджувача та Бета-узгоджувача (Hairpin) ───
def fig_hairpin_t_delta_feed():
    W, H = 820, 400
    f = [text(W / 2, 26, "Альтернативні системи живлення: Т-узгоджувач, Дельта та Бета (Hairpin)", size=15, bold=True)]

    # 1. Т-узгоджувач (T-Match)
    f.append(rect(20, 50, 250, 280, fill="#fdfefe", stroke=INK, sw=1.5, rx=8))
    f.append(text(145, 75, "Т-узгоджувач (T-Match)", size=13, bold=True, color=ACCENT))
    f.append(line(40, 110, 250, 110, color=INK, sw=2.5)) # Елемент
    # Двохсторонні гама-стрижні
    f.append(line(70, 140, 220, 140, color=ACCENT, sw=2))
    f.append(line(70, 110, 70, 140, color=INK, sw=1.5))
    f.append(line(220, 110, 220, 140, color=INK, sw=1.5))
    # Конденсатори
    f.append(rect(100, 132, 20, 16, fill="#feb2b2", stroke=POS, sw=1, rx=2))
    f.append(rect(170, 132, 20, 16, fill="#feb2b2", stroke=POS, sw=1, rx=2))
    f.append(text(110, 170, "C_1", size=10, color=POS))
    f.append(text(180, 170, "C_2", size=10, color=POS))
    f.append(text(145, 210, "Симетричний аналог", size=11, bold=True, color=INK))
    f.append(text(145, 228, "гама-узгоджувача", size=11, color=MUTED))
    f.append(text(145, 305, "Потребує симетричного фідера або балуна", size=10, color=MUTED))

    # 2. Дельта-узгоджувач (Delta Match)
    f.append(rect(285, 50, 250, 280, fill="#fcfdfd", stroke=INK, sw=1.5, rx=8))
    f.append(text(410, 75, "Дельта-узгоджувач", size=13, bold=True, color=FIELD))
    f.append(line(305, 110, 515, 110, color=INK, sw=2.5)) # Елемент
    # Трикутник дельта
    f.append(line(350, 110, 410, 180, color=FIELD, sw=2))
    f.append(line(470, 110, 410, 180, color=FIELD, sw=2))
    f.append(circle(350, 110, 3, fill=FIELD, stroke=FIELD))
    f.append(circle(470, 110, 3, fill=FIELD, stroke=FIELD))
    f.append(text(410, 210, "Безконденсаторна", size=11, bold=True, color=FIELD))
    f.append(text(410, 228, "трансформація", size=11, color=MUTED))
    f.append(text(410, 305, "Простий, але можливі випромінювання трикутника", size=10, color=MUTED))

    # 3. Бета-узгоджувач (Hairpin Match)
    f.append(rect(550, 50, 250, 280, fill="#fffaf0", stroke="#c05621", sw=1.5, rx=8))
    f.append(text(675, 75, "Hairpin / Бета", size=13, bold=True, color="#c05621"))
    # Розрізаний вкорочений елемент
    f.append(line(570, 110, 660, 110, color=POS, sw=2.5))
    f.append(line(690, 110, 780, 110, color=POS, sw=2.5))
    f.append(text(675, 100, "(-j X_C)", size=10, bold=True, color=POS))
    # U-шлейф hairpin
    f.append(line(660, 110, 660, 170, color="#c05621", sw=2))
    f.append(line(690, 110, 690, 170, color="#c05621", sw=2))
    f.append(line(660, 170, 690, 170, color="#c05621", sw=2))
    f.append(text(675, 145, "+j X_L", size=10, bold=True, color="#c05621"))
    f.append(text(675, 210, "L-подібна схема", size=11, bold=True, color="#c05621"))
    f.append(text(675, 228, "на клемах вібратора", size=11, color=MUTED))
    f.append(text(675, 305, "Піднімає низький R_A (15 Ом) до 50 Ом", size=10, color=MUTED))

    # Інформаційна картка внизу
    f.append(fitbox(20, 345, 780, 45,
                    "Порівняння: Т-узгоджувач симетричний, Дельта-узгоджувач не має реактивних компонентів,\n"
                    "а Бета-узгоджувач (Hairpin) формує L-вузол узгодження за рахунок незначного вкорочення елемента.",
                    size=11, fill="#fcfcfd", stroke=BORDER))

    render(os.path.join(IMG, "hairpin-t-delta-feed.svg"), W, H, *f)


if __name__ == "__main__":
    fig_common_mode_current()
    fig_balun_topologies()
    fig_gamma_match_circuit()
    fig_hairpin_t_delta_feed()
    print("Фігури успішно згенеровано в ./img/")
