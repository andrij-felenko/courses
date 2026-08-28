# -*- coding: utf-8 -*-
"""Фігури теми «Обмін між механікою й САПР плати: STEP, DXF, контур».
Запуск: python figs.py -> ./img/*.svg
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_workflow():
    """Двосторонній робочий процес узгодження між ECAD та MCAD."""
    f = []
    
    # ── Загальні панелі доменів ──
    # 1. ECAD домен (ліворуч)
    f.append(rect(20, 40, 260, 420, fill="#f8fafc", stroke=NEG, sw=1.8, rx=8))
    f.append(text(150, 65, "ECAD Домен (САПР Плати)", size=13, color=NEG, bold=True))
    f.append(text(150, 82, "KiCad / Altium / Allegro", size=10, color=MUTED))
    
    # Вузли всередині ECAD
    f.append(rect(35, 100, 230, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(150, 120, "Шар Edge.Cuts / Контур", size=11, bold=True))
    f.append(text(150, 136, "Фрезерований край, вирізи, отвори", size=9, color=MUTED))
    
    f.append(rect(35, 160, 230, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(150, 180, "Посадкові місця + 3D STEP", size=11, bold=True))
    f.append(text(150, 196, "Прив'язка твердотілих моделей деталей", size=9, color=MUTED))
    
    f.append(rect(35, 220, 230, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(150, 240, "Правила трасування й DRC", size=11, bold=True))
    f.append(text(150, 256, "Зони заборони (Keepout), зазори міді", size=9, color=MUTED))
    
    f.append(rect(35, 280, 230, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(150, 300, "Транзакційний клієнт IDX/EDMD", size=11, bold=True))
    f.append(text(150, 316, "Прийом/відхилення змін ECO від MCAD", size=9, color=MUTED))

    f.append(rect(35, 345, 230, 95, fill="#eef3fb", stroke=NEG, sw=1.2, rx=4))
    f.append(text(150, 365, "Технологічний нуль ECAD", size=11, color=NEG, bold=True))
    f.append(text(150, 383, "Origin (0,0) = Центр отвору H1", size=10, bold=True))
    f.append(text(150, 400, "Z = 0: Верхня мідь Top Layer", size=9, color=MUTED))
    f.append(text(150, 417, "Товщина плати: Z < 0 (FR-4)", size=9, color=MUTED))

    # 2. Формати та протоколи обміну (Центр)
    f.append(rect(310, 40, 280, 420, fill="#fbfcfd", stroke="#64748b", sw=1.5, rx=8))
    f.append(text(450, 65, "Формати й Протоколи Обміну", size=13, color=INK, bold=True))
    f.append(text(450, 82, "Безшовний міст даних (Bridge)", size=10, color=MUTED))

    # 2D DXF / DWG
    f.append(rect(325, 100, 250, 65, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    f.append(text(450, 118, "2D DXF / DWG", size=11, color="#0f766e", bold=True))
    f.append(text(450, 134, "LWPOLYLINE, CIRCLE (Edge.Cuts)", size=9, color=INK))
    f.append(text(450, 150, "Базовий контур, кріплення, пази", size=9, color=MUTED))

    # 3D STEP AP214 / AP242
    f.append(rect(325, 180, 250, 75, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    f.append(text(450, 198, "3D STEP (AP214 / AP242)", size=11, color="#b45309", bold=True))
    f.append(text(450, 214, "Точна B-Rep твердотіла геометрія", size=9, color=INK))
    f.append(text(450, 230, "Повна 3D-збірка плати з деталями", size=9, color=MUTED))
    f.append(text(450, 244, "Колізійний аналіз зазорів у 3D", size=9, color=MUTED))

    # IDX / IDF
    f.append(rect(325, 270, 250, 85, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=5))
    f.append(text(450, 288, "IDX (EDMD v3.0) / IDF v3.0", size=11, color="#4338ca", bold=True))
    f.append(text(450, 304, "Інкрементний XML-обмін змінами ECO", size=9, color=INK))
    f.append(text(450, 320, "MCAD: Зсув USB-C -> ECAD: Затверджено", size=9, color=FIELD))
    f.append(text(450, 336, "Історія транзакцій без перезавантаження", size=9, color=MUTED))

    # Стандарти
    f.append(rect(325, 370, 250, 70, fill="#f4fbf7", stroke=FIELD, sw=1.2, rx=5))
    f.append(text(450, 390, "Стандартизація IPC / ISO", size=10, color=FIELD, bold=True))
    f.append(text(450, 408, "ISO 10303-214/242 · IPC-2581", size=9, color=INK))
    f.append(text(450, 424, "ProSTEP iViP EDMD Recommendation", size=9, color=MUTED))

    # 3. MCAD домен (праворуч)
    f.append(rect(620, 40, 260, 420, fill="#f8fafc", stroke=POS, sw=1.8, rx=8))
    f.append(text(750, 65, "MCAD Домен (Конструктор)", size=13, color=POS, bold=True))
    f.append(text(750, 82, "SolidWorks / Fusion 360 / NX", size=10, color=MUTED))

    f.append(rect(635, 100, 230, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(750, 120, "3D Корпус / Литво / ЧПК", size=11, bold=True))
    f.append(text(750, 136, "Стінки, ребра, галтелі, стійки", size=9, color=MUTED))

    f.append(rect(635, 160, 230, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(750, 180, "Колізії (Clearance Checking)", size=11, bold=True))
    f.append(text(750, 196, "Зазори радіаторів, кнопок, роз'ємів", size=9, color=MUTED))

    f.append(rect(635, 220, 230, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(750, 240, "Вирізи панелей під інтерфейси", size=11, bold=True))
    f.append(text(750, 256, "Отвори USB-C, RJ45, світловоди LED", size=9, color=MUTED))

    f.append(rect(635, 280, 230, 48, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))
    f.append(text(750, 300, "Ініціатор пропозицій змін ECO", size=11, bold=True))
    f.append(text(750, 316, "Корекція контуру під прес-форму", size=9, color=MUTED))

    f.append(rect(635, 345, 230, 95, fill="#fdf8f6", stroke=POS, sw=1.2, rx=4))
    f.append(text(750, 365, "Система координат MCAD", size=11, color=POS, bold=True))
    f.append(text(750, 383, "Origin (0,0) = Базова бобишка", size=10, bold=True))
    f.append(text(750, 400, "Повний збіг осей X, Y та Z з ECAD", size=9, color=MUTED))
    f.append(text(750, 417, "Єдина одиниця: міліметри (mm)", size=9, color=MUTED))

    # ── Стрілки передачі даних ──
    # Зліва направо (ECAD -> Bridge)
    f.append(arrow(265, 124, 325, 124, color=NEG, sw=1.8))
    f.append(arrow(265, 190, 325, 210, color=NEG, sw=1.8))
    f.append(arrow(265, 304, 325, 304, color=NEG, sw=1.8))

    # Справа наліво (MCAD -> Bridge)
    f.append(arrow(635, 124, 575, 124, color=POS, sw=1.8))
    f.append(arrow(635, 304, 575, 304, color=POS, sw=1.8))

    # Від мосту до доменів
    f.append(arrow(575, 210, 635, 184, color="#b45309", sw=1.8))
    f.append(arrow(325, 320, 265, 320, color=FIELD, sw=1.8))

    # Підписи процесів зверху і знизу
    f.append(rect(20, 475, 860, 40, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    f.append(text(450, 492, "Ітераційний цикл: Контур DXF -> Трасування -> Експорт STEP -> Перевірка колізій -> Інкрементний IDX ECO", size=10, bold=True))
    f.append(text(450, 506, "Забезпечує 100% перший збіг плати з корпусом без доопрацювання напилком чи повторного замовлення плат", size=9, color=MUTED))

    svg_content = "\n".join(f)
    body = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 530" width="900" height="530">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#333333"/></marker></defs>\n'
            '<rect width="100%" height="100%" fill="#ffffff"/>\n'
            + svg_content + '\n</svg>')
    
    with open(os.path.join(OUT, 'ecad-mcad-data-exchange-workflow.svg'), 'w', encoding='utf-8') as fp:
        fp.write(body)
    print("Generated: ecad-mcad-data-exchange-workflow.svg")


def fig_collision_check():
    """Тривимірний розріз та колізійний аналіз зазорів у збірці плати та корпусу."""
    f = []

    # ── Заголовок розрізу ──
    f.append(rect(20, 15, 860, 35, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(text(450, 37, "3D Розріз механічної збірки: аналіз зазорів, висот та зон заборони", size=12, bold=True))

    # ── Корпус приладу (Алюмінієвий профіль / фрезерована кришка) ──
    # Верхня кришка корпусу
    f.append(rect(30, 60, 840, 25, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=2))
    f.append(text(450, 77, "Верхня кришка корпусу (Aluminum Chassis Lid)", size=11, color="#334155", bold=True))

    # Внутрішній теплопровідний пілон (Heat Post) від кришки
    f.append(rect(275, 85, 120, 45, fill="#cbd5e1", stroke="#475569", sw=1.5, rx=0))
    f.append(text(335, 104, "Охолоджувальний", size=10, bold=True))
    f.append(text(335, 118, "пілон кришки", size=10, bold=True))

    # Ліва стінка з отвором під роз'єм
    f.append(rect(30, 85, 25, 90, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=0))
    f.append(rect(30, 225, 25, 95, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=0))

    # Права стінка корпусу
    f.append(rect(845, 85, 25, 235, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=0))

    # Нижня частина корпусу (дно)
    f.append(rect(30, 320, 840, 25, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=2))
    f.append(text(450, 337, "Дно корпусу з різьбовими бобишками", size=11, color="#334155", bold=True))

    # Механічні стійки кріплення (Standoffs) знизу
    # Ліва стійка
    f.append(rect(100, 270, 40, 50, fill="#94a3b8", stroke="#334155", sw=1.5, rx=0))
    f.append(text(120, 298, "Стійка", size=10, color="#ffffff", bold=True))
    # Права стійка
    f.append(rect(760, 270, 40, 50, fill="#94a3b8", stroke="#334155", sw=1.5, rx=0))
    f.append(text(780, 298, "Стійка", size=10, color="#ffffff", bold=True))

    # ── Друкована плата (FR-4 Substrate) ──
    # Зелений діелектрик плати (Top на Z=0)
    f.append(rect(65, 250, 770, 20, fill="#2e7d32", stroke="#1b5e20", sw=2, rx=1))
    f.append(text(450, 264, "Друкована плата FR-4 (Товщина T = 1.6 мм)", size=11, color="#ffffff", bold=True))

    # Кріпильні гвинти M3 через плату в стійку (головки гвинтів)
    f.append(rect(110, 235, 20, 15, fill="#475569", stroke=INK, sw=1.2, rx=1)) # Ліва головка
    f.append(rect(770, 235, 20, 15, fill="#475569", stroke=INK, sw=1.2, rx=1)) # Права головка

    # Зона заборони довкола гвинта M3 (Keepout Area)
    f.append(line(95, 235, 95, 270, color=POS, sw=1.5, dash="3,3"))
    f.append(line(145, 235, 145, 270, color=POS, sw=1.5, dash="3,3"))
    f.append(text(120, 222, "Keepout r = 3.5 мм", size=9, color=POS, bold=True))

    # ── Компоненти на Top-шарі (Верхня сторона) ──
    # 1. Роз'єм USB-C (проходить крізь фасад у відкритому пазі y=175..225)
    f.append(rect(20, 182, 55, 32, fill="#3b82f6", stroke="#1d4ed8", sw=1.5, rx=2))
    f.append(text(47, 202, "USB-C", size=10, color="#ffffff", bold=True))

    # Позначення вильоту роз'єму
    f.append(rect(80, 186, 95, 24, fill="#eff6ff", stroke=NEG, sw=1, rx=3))
    f.append(text(127, 202, "Виліт = 0.8 мм", size=9, color=NEG, bold=True))

    # 2. Процесор SoC / BGA
    f.append(rect(290, 236, 90, 14, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=1))
    f.append(text(335, 247, "SoC / BGA", size=10, color="#ffffff", bold=True))
    # Теплопровідна прокладка (TIM) між SoC та пілоном
    f.append(rect(295, 130, 80, 106, fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=1))
    f.append(text(335, 180, "TIM Термопрокладка", size=9, color="#854d0e", bold=True))
    f.append(text(335, 196, "Зазор = 1.0 мм", size=9, color="#854d0e"))

    # 3. Високий електролітичний конденсатор
    f.append(rect(430, 115, 60, 135, fill="#64748b", stroke="#334155", sw=1.5, rx=3))
    f.append(text(460, 178, "Cap 1000uF", size=10, color="#ffffff", bold=True))
    f.append(text(460, 195, "H = 15.0 мм", size=9, color="#e2e8f0"))

    # 4. Світловод LED (Light Pipe)
    f.append(rect(540, 85, 18, 140, fill="#bae6fd", stroke="#0284c7", sw=1.2, rx=1))
    f.append(rect(537, 225, 24, 25, fill="#38bdf8", stroke="#0284c7", sw=1.2, rx=1))
    f.append(text(549, 150, "Light Pipe", size=9, color="#0369a1", bold=True))

    # 5. Тактова кнопка (Tactile Switch) з товкачем у кришці
    f.append(rect(620, 210, 45, 40, fill="#f59e0b", stroke="#b45309", sw=1.5, rx=2))
    f.append(text(642, 232, "Button", size=10, color="#ffffff", bold=True))
    f.append(rect(637, 190, 11, 20, fill="#d97706", stroke="#78350f", sw=1.2, rx=1)) # Шток
    # Отвір під шток у верхній кришці
    f.append(rect(633, 60, 19, 25, fill="#ffffff", stroke="#94a3b8", sw=1, rx=0))

    # ── Компоненти на Bottom-шарі (Нижня сторона) ──
    f.append(rect(230, 270, 40, 14, fill="#475569", stroke=INK, sw=1, rx=1))
    f.append(text(250, 281, "SMD 0805", size=9, color="#ffffff"))

    f.append(rect(320, 270, 65, 18, fill="#334155", stroke=INK, sw=1, rx=1))
    f.append(text(352, 283, "Flash SOIC-8", size=9, color="#ffffff"))

    f.append(rect(440, 270, 50, 16, fill="#475569", stroke=INK, sw=1, rx=1))
    f.append(text(465, 282, "LDO SOT-223", size=9, color="#ffffff"))

    # ── Маркери аналізу зазорів (Clearance Measurements) ──
    # Зазор над конденсатором (Headroom clearance)
    f.append(line(430, 85, 490, 85, color=POS, sw=1.2))
    f.append(line(460, 85, 460, 115, color=POS, sw=1.5, dash="2,2"))
    f.append(rect(500, 93, 115, 24, fill="#fef2f2", stroke=POS, sw=1, rx=3))
    f.append(text(557, 109, "Верхній зазор delta Z >= 1.5 мм", size=9, color=POS, bold=True))

    # Зазор під платою (Bottom clearance)
    f.append(line(310, 288, 310, 320, color=FIELD, sw=1.5, dash="2,2"))
    f.append(rect(315, 295, 115, 24, fill="#f0fdf4", stroke=FIELD, sw=1, rx=3))
    f.append(text(372, 311, "Нижній зазор delta Z = 3.2 мм", size=9, color=FIELD, bold=True))

    # ── Легенда внизу ──
    f.append(rect(30, 360, 840, 75, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(450, 378, "Результати автоматичного Clearance Check у 3D САПР (SolidWorks / Altium MCAD CoDesigner):", size=10, bold=True))
    f.append(circle(60, 400, 6, fill="#22c55e", stroke=FIELD, sw=1.2))
    f.append(text(155, 404, "Зазори компонентів Top/Bottom: В НОРМІ", size=9, color="#15803d", bold=True))
    
    f.append(circle(330, 400, 6, fill="#22c55e", stroke=FIELD, sw=1.2))
    f.append(text(425, 404, "Співвісність кріпильних отворів M3: В НОРМІ", size=9, color="#15803d", bold=True))

    f.append(circle(600, 400, 6, fill="#22c55e", stroke=FIELD, sw=1.2))
    f.append(text(695, 404, "Стиснення термопрокладки TIM: 30% (ОПТИМАЛЬНО)", size=9, color="#15803d", bold=True))

    f.append(text(450, 424, "Координатний нуль збірки: X=0, Y=0 по осі лівого отвору H1; Z=0 по верхній грані плати Top", size=9, color=MUTED))

    svg_content = "\n".join(f)
    body = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 450" width="900" height="450">\n'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#333333"/></marker></defs>\n'
            '<rect width="100%" height="100%" fill="#ffffff"/>\n'
            + svg_content + '\n</svg>')

    with open(os.path.join(OUT, 'step-3d-collision-clearance-check.svg'), 'w', encoding='utf-8') as fp:
        fp.write(body)
    print("Generated: step-3d-collision-clearance-check.svg")


if __name__ == '__main__':
    fig_workflow()
    fig_collision_check()
