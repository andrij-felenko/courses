# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Маркери стрілок для різних кольорів
COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrO" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#d98a00"/></marker>'
    '</defs>' % (NEG, FIELD, POS)
)

def carrow(x1, y1, x2, y2, color, mid, sw=2.0, dash=None):
    """Лінія з кольоровим наконечником."""
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f"%s marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, d, mid))

def block(x, y, w, h, lines, fill=FILL, stroke=LINE, color=INK, size=12, bold=True, rx=8):
    """Рамка-блок із центрованим текстом."""
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=rx)
    if isinstance(lines, str):
        lines = [lines]
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * 1.25 / 2 + size * 0.35
    out += mtext(x + w / 2, cy, lines, size=size, color=color, bold=bold)
    return out

# ── Fig 1: Порівняння контуру телекерування та цілеорієнтованої автономії ────
def fig_command_vs_goal():
    W, H = 960, 500
    p = [COL_MARKERS]
    
    # Ліва колонка: Пряме телекерування
    p.append(rect(30, 55, 435, 420, fill="#fffaf9", stroke=POS, sw=1.5, rx=10))
    p.append(text(247, 80, "ПРЯМЕ ТЕЛЕКЕРУВАННЯ (КОМАНДА)", size=13, color=POS, bold=True))
    p.append(text(247, 100, "Людина всередині критичного контуру реального часу", size=11, color=MUTED))
    
    # Блоки лівої сторони
    p.append(block(50, 125, 395, 52, ["ОПЕРАТОР (людина)", "Сприйняття відео → рішення → рух стіків"],
                   fill="#ffffff", stroke=POS, color=POS, size=11))
    
    p.append(carrow(247, 177, 247, 213, POS, "R", sw=2.0))
    p.append(text(255, 198, "радіоканал (затримка 100-300 мс)", size=10, color=POS, anchor="start"))
    
    p.append(block(75, 215, 345, 48, ["АВТОПІЛОТ (виконавець)", "Сліпий прийом кутів/тяг (roll, pitch, yaw)"],
                   fill="#fdf2f2", stroke=LINE, color=INK, size=11))
    
    p.append(arrow(247, 263, 247, 299, color=LINE, sw=2.0))
    p.append(text(255, 283, "кутові уставки (50 Гц)", size=10, color=MUTED, anchor="start"))
    
    p.append(block(95, 301, 305, 48, ["РЕГУЛЯТОР ТА ПРИВОДИ", "Швидкісні моменти на мотори / сервоприводи"],
                   fill="#f4f4f5", stroke=LINE, color=INK, size=11))
    
    p.append(arrow(247, 349, 247, 385, color=LINE, sw=2.0))
    p.append(text(255, 369, "фізичний рух апарата", size=10, color=MUTED, anchor="start"))
    
    p.append(block(115, 387, 265, 42, ["СЕРЕДОВИЩЕ ТА ПЕРЕШКОДИ", "Раптові загрози, вітер, стіни"],
                   fill="#f4f6f8", stroke=LINE, color=INK, size=11))
    
    # Зворотний зв'язок на оператора (відеоканал)
    p.append(line(380, 408, 435, 408, color=POS, sw=1.8, dash="4 3"))
    p.append(line(435, 408, 435, 151, color=POS, sw=1.8, dash="4 3"))
    p.append(carrow(435, 151, 445, 151, POS, "R", sw=1.8, dash="4 3"))
    p.append(text(420, 280, "відеопотік (затримка, шум, РЕБ)", size=9.5, color=POS, anchor="end"))

    # Права колонка: Автономне цілепокладання
    p.append(rect(495, 55, 435, 420, fill="#f9fdfa", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(712, 80, "ЦІЛЕОРІЄНТОВАНА АВТОНОМІЯ (ЦІЛЬ)", size=13, color=FIELD, bold=True))
    p.append(text(712, 100, "Людина ставить задачу, борт вирішує виконання", size=11, color=MUTED))
    
    p.append(block(515, 125, 395, 52, ["ОПЕРАТОР / СИСТЕМА МІСІЇ", "Декларативна ціль: «Обстежити зону A на H=50м»"],
                   fill="#ffffff", stroke=FIELD, color=FIELD, size=11))
    
    p.append(carrow(712, 177, 712, 213, FIELD, "G", sw=2.0))
    p.append(text(720, 198, "асинхронна ціль (не чутлива до пінгів)", size=10, color=FIELD, anchor="start"))
    
    p.append(block(535, 215, 355, 52, ["БОРТОВИЙ ПЛАНУВАЛЬНИК ТА МОДЕЛЬ СВІТУ", "Модель світу + Глобальний план + Локальний обхід"],
                   fill="#eafaf1", stroke=FIELD, color=INK, size=11))
    
    p.append(arrow(712, 267, 712, 303, color=LINE, sw=2.0))
    p.append(text(720, 287, "локальні траєкторії (20-50 Гц)", size=10, color=MUTED, anchor="start"))
    
    p.append(block(560, 305, 305, 46, ["АВТОПІЛОТ / ШВИДКІСНИЙ РЕГУЛЯТОР", "Миттєве відпрацювання кінематики"],
                   fill="#f4f4f5", stroke=LINE, color=INK, size=11))
    
    p.append(arrow(712, 351, 712, 387, color=LINE, sw=2.0))
    p.append(text(720, 371, "керування моторами", size=10, color=MUTED, anchor="start"))
    
    p.append(block(580, 389, 265, 42, ["СЕРЕДОВИЩЕ ТА ПЕРЕШКОДИ", "Фізична взаємодія та сенсорика"],
                   fill="#f4f6f8", stroke=LINE, color=INK, size=11))
    
    # Локальний зворотний зв'язок (бортові сенсори прямо в модель світу)
    p.append(line(845, 410, 905, 410, color=FIELD, sw=1.8))
    p.append(line(905, 410, 905, 241, color=FIELD, sw=1.8))
    p.append(carrow(905, 241, 890, 241, FIELD, "G", sw=1.8))
    p.append(text(890, 325, "бортові сенсори (0-5 мс)", size=9.5, color=FIELD, anchor="end"))
    
    render(os.path.join(OUT, "command-vs-goal-hierarchy.svg"), W, H, *p,
           title="Порівняння контурів: пряме телекерування проти автономного цілепокладання")

# ── Fig 2: Три рівні внутрішньої моделі світу (World Model) ─────────────────
def fig_world_model_layers():
    W, H = 940, 480
    p = [COL_MARKERS]
    
    p.append(text(W / 2, 50, "Від сирих тривимірних вимірів до двовимірних карт вартості для планування",
                  size=12, color=MUTED))
    
    # Шар 1: 3D Октодерево
    p.append(rect(30, 75, 275, 380, fill="#f6f8fe", stroke=NEG, sw=1.5, rx=10))
    p.append(text(167, 102, "1. 3D ОКТОДЕРЕВО (OctoMap)", size=12, color=NEG, bold=True))
    p.append(text(167, 122, "Імовірнісна об'ємна сітка", size=10.5, color=MUTED))
    
    p.append(rect(50, 140, 235, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(rect(60, 150, 105, 42, fill="#e8eeff", stroke=NEG, sw=1.0, rx=4))
    p.append(rect(170, 150, 105, 42, fill="#e8eeff", stroke=NEG, sw=1.0, rx=4))
    p.append(rect(60, 198, 105, 42, fill="#e8eeff", stroke=NEG, sw=1.0, rx=4))
    p.append(rect(170, 198, 105, 42, fill="#c0392b", stroke=POS, sw=1.0, rx=4))
    p.append(text(112, 176, "вільно", size=11, color=NEG))
    p.append(text(222, 176, "невідомо", size=11, color=MUTED))
    p.append(text(112, 224, "вільно", size=11, color=NEG))
    p.append(text(222, 224, "зайнято", size=11, color="#ffffff", bold=True))
    
    p.append(mtext(167, 285, [
        "• Рекурсивний поділ на 8 октантів",
        "• Log-odds фільтрація шуму",
        "• Стиснення порожніх зон",
        "• Повна 3D-навігація дронів"
    ], size=11, color=INK, anchor="middle", lh=1.45))
    
    # Шар 2: 2.5D Карта висот рельєфу (DEM)
    p.append(rect(330, 75, 280, 380, fill="#fbf8f3", stroke="#d98a00", sw=1.5, rx=10))
    p.append(text(470, 102, "2. 2.5D КАРТА РЕЛЬЄФУ (DEM)", size=12, color="#d98a00", bold=True))
    p.append(text(470, 122, "Матриця висот та ухилів поверхні", size=10.5, color=MUTED))
    
    p.append(rect(350, 140, 240, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    for r_i in range(3):
        for c_i in range(3):
            val = ["12.4", "12.8", "15.2", "12.5", "13.1", "18.6", "12.6", "14.0", "22.1"][r_i*3 + c_i]
            col = "#fdf3e7" if float(val) < 16.0 else "#fadbd8"
            tc = INK if float(val) < 16.0 else POS
            p.append(rect(360 + c_i*72, 148 + r_i*34, 66, 28, fill=col, stroke=LINE, sw=0.8, rx=3))
            p.append(text(393 + c_i*72, 166 + r_i*34, val + " м", size=10.5, color=tc, bold=(float(val)>=16.0)))
            
    p.append(mtext(470, 285, [
        "• Сітка висот із дисперсією",
        "• Градієнти схилів (крутизна)",
        "• Прохідність наземних шасі",
        "• Огинання рельєфу для БПЛА"
    ], size=11, color=INK, anchor="middle", lh=1.45))
    
    # Шар 3: Векторне поле перешкод та Costmap
    p.append(rect(635, 75, 275, 380, fill="#f6fcf8", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(772, 102, "3. КАРТА ВАРТОСТЕЙ (Costmap)", size=12, color=FIELD, bold=True))
    p.append(text(772, 122, "Інфляція безпеки та ціна клітинок", size=10.5, color=MUTED))
    
    p.append(rect(655, 140, 235, 110, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(circle(772, 195, 44, fill="#ebfbee", stroke=FIELD, sw=1.0))
    p.append(circle(772, 195, 28, fill="#fef5e7", stroke="#d98a00", sw=1.0))
    p.append(circle(772, 195, 14, fill="#fadbd8", stroke=POS, sw=1.2))
    p.append(text(772, 199, "Стіна", size=10.5, color=POS, bold=True))
    p.append(text(772, 150, "буфер безпеки", size=10, color=FIELD))
    
    p.append(mtext(772, 285, [
        "• Роздмухування перешкод",
        "• Габарити робота в карті",
        "• Планування точки в просторі",
        "• Штрафні вартості біля стін"
    ], size=11, color=INK, anchor="middle", lh=1.45))
    
    render(os.path.join(OUT, "world-model-layers.svg"), W, H, *p,
           title="Ієрархія та шари внутрішньої моделі світу бортового комп'ютера")

# ── Fig 3: Пастка локального мінімуму в U-подібній перешкоді ──────────────────
def fig_u_obstacle_trap():
    W, H = 920, 460
    p = [COL_MARKERS]
    
    p.append(text(W / 2, 50, "Чому реактивне відштовхування застрягає, а планувальник знаходить вихід",
                  size=12, color=MUTED))
    
    # Ліва панель: Реактивне потенційне поле
    p.append(rect(30, 75, 415, 365, fill="#fffaf9", stroke=POS, sw=1.5, rx=10))
    p.append(text(237, 100, "РЕАКТИВНЕ ПОЛЕ (Potential Field)", size=12, color=POS, bold=True))
    p.append(text(237, 120, "Складання сил притягання та відштовхування", size=10.5, color=MUTED))
    
    # U-подібна стіна ліворуч
    p.append(rect(100, 190, 20, 120, fill="#7f8c8d", stroke=LINE, sw=1.5, rx=2))
    p.append(rect(100, 190, 240, 20, fill="#7f8c8d", stroke=LINE, sw=1.5, rx=2))
    p.append(rect(320, 190, 20, 120, fill="#7f8c8d", stroke=LINE, sw=1.5, rx=2))
    
    # Ціль угорі
    p.append(circle(220, 150, 12, fill="#e8f8f5", stroke=FIELD, sw=2.0))
    p.append(text(220, 154, "★", size=14, color=FIELD))
    p.append(text(240, 154, "Ціль (Goal)", size=10.5, color=FIELD, bold=True, anchor="start"))
    
    # Робот у пастці
    p.append(circle(220, 255, 14, fill="#ebf5fb", stroke=NEG, sw=2.0))
    p.append(text(220, 259, "R", size=11, color=NEG, bold=True))
    
    # Вектори сил
    p.append(carrow(220, 240, 220, 212, FIELD, "G", sw=2.2))
    p.append(text(238, 225, "F_attr (тягне до цілі)", size=10, color=FIELD, anchor="start"))
    
    p.append(carrow(220, 270, 220, 290, POS, "R", sw=2.2))
    p.append(text(238, 285, "F_rep (відштовхування)", size=10, color=POS, anchor="start"))
    
    p.append(carrow(205, 255, 175, 255, POS, "R", sw=1.5))
    p.append(carrow(235, 255, 265, 255, POS, "R", sw=1.5))
    
    # Підпис результату
    p.append(rect(45, 350, 385, 66, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(237, 372, "РІВНОДІЙНА СИЛА: F_total = F_attr + Σ F_rep ≈ 0", size=11, color=POS, bold=True))
    p.append(text(237, 395, "Апарат застрягає в локальному мінімумі або коливається", size=10.5, color=INK))

    # Права панель: Дворівневий планувальник
    p.append(rect(475, 75, 415, 365, fill="#f6fcf8", stroke=FIELD, sw=1.5, rx=10))
    p.append(text(682, 100, "ДВОРІВНЕВИЙ ПЛАНУВАЛЬНИК (Global + Local)", size=12, color=FIELD, bold=True))
    p.append(text(682, 120, "Глобальний пошук у графі бачить пастку наперед", size=10.5, color=MUTED))
    
    # U-подібна стіна праворуч
    p.append(rect(545, 190, 20, 120, fill="#7f8c8d", stroke=LINE, sw=1.5, rx=2))
    p.append(rect(545, 190, 240, 20, fill="#7f8c8d", stroke=LINE, sw=1.5, rx=2))
    p.append(rect(765, 190, 20, 120, fill="#7f8c8d", stroke=LINE, sw=1.5, rx=2))
    
    # Ціль угорі
    p.append(circle(665, 150, 12, fill="#e8f8f5", stroke=FIELD, sw=2.0))
    p.append(text(665, 154, "★", size=14, color=FIELD))
    p.append(text(685, 154, "Ціль (Goal)", size=10.5, color=FIELD, bold=True, anchor="start"))
    
    # Робот знизу
    p.append(circle(665, 290, 14, fill="#ebf5fb", stroke=NEG, sw=2.0))
    p.append(text(665, 294, "R", size=11, color=NEG, bold=True))
    
    # Глобальний спланований шлях навколо U-стіни
    p.append('<polyline points="665,290 665,325 815,325 815,150 682,150" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="6 4" stroke-linecap="round"/>' % FIELD)
    p.append(carrow(695, 150, 680, 150, FIELD, "G", sw=2.5))
    
    p.append(text(740, 342, "1. Глобальний обхід U-перешкоди", size=10, color=FIELD, bold=True))
    p.append(text(825, 235, "2. Віддалення від цілі", size=10, color=MUTED, anchor="start"))
    
    # Підпис результату
    p.append(rect(490, 360, 385, 54, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(682, 380, "ГЛОБАЛЬНИЙ ПЛАН: A* / Dijkstra знаходить топологічний вихід", size=10.5, color=FIELD, bold=True))
    p.append(text(682, 398, "Локальний контролер лише веде апарат уздовж знайденої гілки", size=10, color=INK))
    
    render(os.path.join(OUT, "u-shaped-obstacle-local-minimum.svg"), W, H, *p,
           title="Проблема локальних оптимумів: пастка U-подібної перешкоди")

if __name__ == "__main__":
    fig_command_vs_goal()
    fig_world_model_layers()
    fig_u_obstacle_trap()
    print("All figures generated successfully.")
