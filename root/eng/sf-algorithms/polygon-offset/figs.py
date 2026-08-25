# -*- coding: utf-8 -*-
"""Фігури до теми «Зсув контуру (еквідистанта)».
Генерує векторні схеми SVG у теці ./img/:
1. offset-concept-cnc.svg — зміщення траєкторії фрези (еквідистанта) відносно деталі
2. join-types.svg — типи кутових стиків: гострий (miter), скруглений (round) і фаска (bevel)
3. deflation-collapse-events.svg — топологічні події при звуженні: зникнення ребра та розкол контуру
4. straight-skeleton-propagation.svg — хвильовий фронт і прямий кістяк як неперервне звуження
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Компенсація радіуса фрези та еквідистанта
# ─────────────────────────────────────────────────────────────────────────────
def fig_offset_concept():
    W, H = 820, 320
    parts = []
    
    # Загальна підкладка
    parts.append(rect(15, 15, 790, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 42, "Компенсація радіуса інструмента: центр фрези рухається по еквідистанті", size=15, color=INK, bold=True))

    # Ліва частина: Помилка прямого руху (без зсуву)
    x1, y1, w1, h1 = 35, 65, 360, 225
    parts.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x1 + w1/2, y1 + 24, "Рух центром по контуру (помилка)", size=13, color=POS, bold=True))
    
    # Контур деталі (сходинка)
    p_bad = "M 70,240 L 70,140 L 180,140 L 180,240 Z"
    parts.append(f'<path d="{p_bad}" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>')
    parts.append(text(125, 200, "Деталь", size=12, color="#475569", bold=True))
    
    # Траєкторія без зсуву (червона лінія)
    parts.append(line(70, 140, 180, 140, color=POS, sw=2, dash="4,4"))
    
    # Фреза на контурі
    parts.append(circle(125, 140, 24, fill="#fee2e2", stroke=POS, sw=1.5))
    parts.append(circle(125, 140, 3, fill=POS, stroke=POS))
    parts.append(text(125, 128, "Фреза R", size=11, color=POS))
    
    # Заріз матеріалу (червона штрихована зона)
    parts.append(text(285, 130, "Заріз матеріалу:", size=12, color=POS, bold=True))
    parts.append(text(285, 150, "фреза радіусом R", size=11, color="#64748b"))
    parts.append(text(285, 168, "зрізає зайве на R", size=11, color="#64748b"))
    parts.append(text(285, 186, "всередину деталі", size=11, color="#64748b"))

    # Права частина: Правильний рух по еквідистанті (зсув на d = R)
    x2, y2, w2, h2 = 425, 65, 360, 225
    parts.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x2 + w2/2, y2 + 24, "Рух по зміщеній еквідистанті (норма)", size=13, color=FIELD, bold=True))
    
    # Контур деталі
    p_good = "M 460,240 L 460,160 L 570,160 L 570,240 Z"
    parts.append(f'<path d="{p_good}" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>')
    parts.append(text(515, 205, "Деталь", size=12, color="#475569", bold=True))
    
    # Зміщена траєкторія (еквідистанта на відстані d = 24px)
    p_offset = "M 436,240 L 436,136 L 594,136 L 594,240"
    parts.append(f'<path d="{p_offset}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="5,4"/>')
    
    # Фреза на еквідистанті
    parts.append(circle(515, 136, 24, fill="#dbeafe", stroke=NEG, sw=1.5))
    parts.append(circle(515, 136, 3, fill=NEG, stroke=NEG))
    parts.append(text(515, 120, "Центр фрези", size=11, color=NEG, bold=True))
    
    # Стрілка відстані d
    parts.append(arrow(515, 160, 515, 136, color=LINE, sw=1.2))
    parts.append(text(532, 150, "d = R", size=11, color=INK, bold=True))
    
    parts.append(text(675, 140, "Точний контур:", size=12, color=FIELD, bold=True))
    parts.append(text(675, 160, "кромка фрези точно", size=11, color="#64748b"))
    parts.append(text(675, 178, "дотикається деталі", size=11, color="#64748b"))
    parts.append(text(675, 196, "без пошкоджень", size=11, color="#64748b"))

    render(os.path.join(OUT, "offset-concept-cnc.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Типи кутових стиків при розширенні
# ─────────────────────────────────────────────────────────────────────────────
def fig_join_types():
    W, H = 840, 310
    parts = []
    
    parts.append(rect(15, 15, 810, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(420, 42, "Типи кутових з'єднань еквідистанти на опуклих вершинах", size=15, color=INK, bold=True))

    # 1. Miter (Гострий стик)
    x1, y1, w1, h1 = 35, 65, 240, 215
    parts.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x1 + w1/2, y1 + 24, "Гострий стик (Miter)", size=13, color=INK, bold=True))
    
    # Вхідний кут
    parts.append(line(x1 + 40, y1 + 180, x1 + 120, y1 + 110, color="#475569", sw=2.5))
    parts.append(line(x1 + 120, y1 + 110, x1 + 200, y1 + 180, color="#475569", sw=2.5))
    parts.append(circle(x1 + 120, y1 + 110, 3.5, fill="#475569", stroke="#475569"))
    
    # Зміщений контур Miter
    parts.append(line(x1 + 20, y1 + 160, x1 + 120, y1 + 72, color=NEG, sw=2))
    parts.append(line(x1 + 120, y1 + 72, x1 + 220, y1 + 160, color=NEG, sw=2))
    parts.append(circle(x1 + 120, y1 + 72, 3.5, fill=NEG, stroke=NEG))
    
    # Бісектриса
    parts.append(line(x1 + 120, y1 + 110, x1 + 120, y1 + 72, color=POS, sw=1.5, dash="3,3"))
    parts.append(text(x1 + 140, y1 + 92, "m", size=12, color=POS, bold=True))
    parts.append(text(x1 + w1/2, y1 + 198, "Перетин зміщених прямих", size=11, color="#64748b"))

    # 2. Round (Скруглення)
    x2, y2, w2, h2 = 300, 65, 240, 215
    parts.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x2 + w2/2, y2 + 24, "Скруглення (Round)", size=13, color=INK, bold=True))
    
    # Вхідний кут
    parts.append(line(x2 + 40, y2 + 180, x2 + 120, y2 + 110, color="#475569", sw=2.5))
    parts.append(line(x2 + 120, y2 + 110, x2 + 200, y2 + 180, color="#475569", sw=2.5))
    parts.append(circle(x2 + 120, y2 + 110, 3.5, fill="#475569", stroke="#475569"))
    
    # Зміщені ребра + дуга
    parts.append(line(x2 + 20, y2 + 160, x2 + 96, y2 + 89, color=NEG, sw=2))
    parts.append(line(x2 + 144, y2 + 89, x2 + 220, y2 + 160, color=NEG, sw=2))
    # Дуга радіусом d = 30
    p_arc = f"M {x2 + 96},{y2 + 89} A 32 32 0 0 1 {x2 + 144},{y2 + 89}"
    parts.append(f'<path d="{p_arc}" fill="none" stroke="{NEG}" stroke-width="2"/>')
    parts.append(line(x2 + 120, y2 + 110, x2 + 96, y2 + 89, color=MUTED, sw=1, dash="2,2"))
    parts.append(line(x2 + 120, y2 + 110, x2 + 144, y2 + 89, color=MUTED, sw=1, dash="2,2"))
    parts.append(text(x2 + 120, y2 + 98, "R = d", size=10, color=MUTED))
    parts.append(text(x2 + w2/2, y2 + 198, "Дуга кола радіусом d", size=11, color="#64748b"))

    # 3. Bevel (Фаска / зріз)
    x3, y3, w3, h3 = 565, 65, 240, 215
    parts.append(rect(x3, y3, w3, h3, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x3 + w3/2, y2 + 24, "Фаска (Bevel)", size=13, color=INK, bold=True))
    
    # Вхідний кут
    parts.append(line(x3 + 40, y3 + 180, x3 + 120, y3 + 110, color="#475569", sw=2.5))
    parts.append(line(x3 + 120, y3 + 110, x3 + 200, y3 + 180, color="#475569", sw=2.5))
    parts.append(circle(x3 + 120, y3 + 110, 3.5, fill="#475569", stroke="#475569"))
    
    # Зміщені ребра + прямий відрізок фаски
    parts.append(line(x3 + 20, y3 + 160, x3 + 96, y3 + 89, color=NEG, sw=2))
    parts.append(line(x3 + 144, y3 + 89, x3 + 220, y3 + 160, color=NEG, sw=2))
    parts.append(line(x3 + 96, y3 + 89, x3 + 144, y3 + 89, color=NEG, sw=2))
    parts.append(circle(x3 + 96, y3 + 89, 3, fill=NEG, stroke=NEG))
    parts.append(circle(x3 + 144, y3 + 89, 3, fill=NEG, stroke=NEG))
    parts.append(text(x3 + w3/2, y3 + 198, "Прямий відрізок-зріз", size=11, color="#64748b"))

    render(os.path.join(OUT, "join-types.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Топологічні колапси при звуженні контуру
# ─────────────────────────────────────────────────────────────────────────────
def fig_deflation_events():
    W, H = 820, 310
    parts = []
    
    parts.append(rect(15, 15, 790, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 42, "Топологічні події під час звуження (інфляції всередину)", size=15, color=INK, bold=True))

    # Ліва панель: Реберна подія (Edge Event)
    x1, y1, w1, h1 = 35, 65, 360, 215
    parts.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x1 + w1/2, y1 + 24, "Реберна подія (Edge Event)", size=13, color=POS, bold=True))
    
    # Вихідний трикутний виступ (трапеція)
    p_orig1 = f"M {x1+50},{y1+175} L {x1+100},{y1+100} L {x1+220},{y1+100} L {x1+270},{y1+175} Z"
    parts.append(f'<path d="{p_orig1}" fill="#f1f5f9" stroke="#64748b" stroke-width="1.8"/>')
    parts.append(text(x1 + 160, y1 + 90, "коротке ребро L", size=11, color=POS))
    
    # Звужений контур 1 (проміжний)
    p_mid1 = f"M {x1+70},{y1+160} L {x1+130},{y1+120} L {x1+190},{y1+120} L {x1+250},{y1+160} Z"
    parts.append(f'<path d="{p_mid1}" fill="none" stroke="{NEG}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    
    # Критична точка колапсу ребра (L -> 0)
    parts.append(circle(x1 + 160, y1 + 138, 4.5, fill=POS, stroke=POS))
    parts.append(line(x1 + 100, y1 + 100, x1 + 160, y1 + 138, color=MUTED, sw=1.2, dash="2,2"))
    parts.append(line(x1 + 220, y1 + 100, x1 + 160, y1 + 138, color=MUTED, sw=1.2, dash="2,2"))
    parts.append(text(x1 + 160, y1 + 158, "Ребро вироджується в точку", size=11, color=POS, bold=True))
    parts.append(text(x1 + w1/2, y1 + 195, "Довжина ребра падає до 0; суміжні вершини зливаються", size=11, color="#64748b"))

    # Права панель: Подія розколу (Split Event)
    x2, y2, w2, h2 = 425, 65, 360, 215
    parts.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x2 + w2/2, y2 + 24, "Подія розколу (Split Event)", size=13, color=FIELD, bold=True))
    
    # Контур у формі гантелі / метелика з увігнутим кутом
    p_orig2 = f"M {x2+40},{y2+70} L {x2+180},{y2+120} L {x2+320},{y2+70} L {x2+320},{y2+170} L {x2+40},{y2+170} Z"
    parts.append(f'<path d="{p_orig2}" fill="#f1f5f9" stroke="#64748b" stroke-width="1.8"/>')
    parts.append(circle(x2 + 180, y2 + 120, 3.5, fill=POS, stroke=POS))
    parts.append(text(x2 + 180, y2 + 110, "увігнута вершина V", size=11, color=POS))
    
    # Рух увігнутої вершини до протилежного ребра
    parts.append(arrow(x2 + 180, y2 + 120, x2 + 180, y2 + 170, color=POS, sw=1.5))
    parts.append(circle(x2 + 180, y2 + 155, 4, fill=FIELD, stroke=FIELD))
    
    # Звужені дві незалежні петлі після розколу
    parts.append(rect(x2 + 55, y2 + 125, 90, 35, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(x2 + 100, y2 + 147, "Контур 1", size=11, color="#15803d", bold=True))
    
    parts.append(rect(x2 + 215, y2 + 125, 90, 35, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    parts.append(text(x2 + 260, y2 + 147, "Контур 2", size=11, color="#15803d", bold=True))
    
    parts.append(text(x2 + w2/2, y2 + 195, "Вершина торкається ребра: контур розпадається на 2 частини", size=11, color="#64748b"))

    render(os.path.join(OUT, "deflation-collapse-events.svg"), W, H, *parts)

# ─────────────────────────────────────────────────────────────────────────────
# Фігура 4: Хвильовий фронт і прямий кістяк
# ─────────────────────────────────────────────────────────────────────────────
def fig_straight_skeleton():
    W, H = 820, 320
    parts = []
    
    parts.append(rect(15, 15, 790, 290, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    parts.append(text(410, 42, "Хвильовий фронт і прямий кістяк (Straight Skeleton)", size=15, color=INK, bold=True))

    # Ліва схема: Траєкторії бісектрис на площині
    x1, y1, w1, h1 = 35, 65, 360, 225
    parts.append(rect(x1, y1, w1, h1, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x1 + w1/2, y1 + 24, "Рух бісектрис та утворення кістяка", size=13, color=INK, bold=True))
    
    # Вихідний прямокутник з фаскою
    p_poly = f"M {x1+40},{y1+180} L {x1+40},{y1+80} L {x1+200},{y1+80} L {x1+300},{y1+140} L {x1+300},{y1+180} Z"
    parts.append(f'<path d="{p_poly}" fill="#f8fafc" stroke="#334155" stroke-width="2"/>')
    parts.append(text(x1 + 75, y1 + 170, "Базовий контур", size=11, color="#64748b"))
    
    # Зрізи на різних відстанях d (ізолінії)
    p_iso1 = f"M {x1+60},{y1+165} L {x1+60},{y1+100} L {x1+185},{y1+100} L {x1+270},{y1+145} L {x1+270},{y1+165} Z"
    parts.append(f'<path d="{p_iso1}" fill="none" stroke="{NEG}" stroke-width="1.2" stroke-dasharray="3,3"/>')
    parts.append(text(x1 + 130, y1 + 115, "Зріз d₁", size=10, color=NEG))
    
    p_iso2 = f"M {x1+80},{y1+150} L {x1+80},{y1+120} L {x1+170},{y1+120} L {x1+240},{y1+150} Z"
    parts.append(f'<path d="{p_iso2}" fill="none" stroke="{FIELD}" stroke-width="1.2" stroke-dasharray="3,3"/>')
    parts.append(text(x1 + 130, y1 + 135, "Зріз d₂", size=10, color=FIELD))

    # Гілки прямого кістяка (бісектриси, що сходяться)
    parts.append(line(x1 + 40, y1 + 80, x1 + 105, y1 + 145, color=POS, sw=2))
    parts.append(line(x1 + 40, y1 + 180, x1 + 105, y1 + 145, color=POS, sw=2))
    parts.append(line(x1 + 105, y1 + 145, x1 + 220, y1 + 145, color=POS, sw=2))
    parts.append(line(x1 + 200, y1 + 80, x1 + 220, y1 + 145, color=POS, sw=2))
    parts.append(line(x1 + 300, y1 + 140, x1 + 220, y1 + 145, color=POS, sw=2))
    parts.append(line(x1 + 300, y1 + 180, x1 + 220, y1 + 145, color=POS, sw=2))
    
    parts.append(circle(x1 + 105, y1 + 145, 4, fill=POS, stroke=POS))
    parts.append(circle(x1 + 220, y1 + 145, 4, fill=POS, stroke=POS))
    parts.append(text(x1 + 160, y1 + 160, "Ребро кістяка", size=11, color=POS, bold=True))

    # Права схема: 3D-інтерпретація «Дах споруди»
    x2, y2, w2, h2 = 425, 65, 360, 225
    parts.append(rect(x2, y2, w2, h2, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    parts.append(text(x2 + w2/2, y2 + 24, "Геометрична модель похилого даху", size=13, color=INK, bold=True))
    
    # 3D ізометрія схилів даху
    parts.append(rect(x2 + 40, y2 + 150, 280, 50, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    parts.append(text(x2 + 180, y2 + 180, "Площина основи (d = 0)", size=11, color="#64748b"))
    
    # Коник даху (ridge)
    parts.append(line(x2 + 100, y2 + 80, x2 + 260, y2 + 80, color=POS, sw=2.5))
    parts.append(text(x2 + 180, y2 + 70, "Коник даху (кінцеве злиття)", size=11, color=POS, bold=True))
    
    # Похилі грані (схили)
    parts.append(line(x2 + 40, y2 + 150, x2 + 100, y2 + 80, color="#334155", sw=1.5))
    parts.append(line(x2 + 40, y2 + 200, x2 + 100, y2 + 80, color="#334155", sw=1.5, dash="2,2"))
    parts.append(line(x2 + 320, y2 + 150, x2 + 260, y2 + 80, color="#334155", sw=1.5))
    parts.append(line(x2 + 320, y2 + 200, x2 + 260, y2 + 80, color="#334155", sw=1.5, dash="2,2"))
    
    # Горизонтальна січна площина (offset slice)
    parts.append(rect(x2 + 65, y2 + 115, 230, 25, fill="#dbeafe", stroke=NEG, sw=1.5, rx=3))
    parts.append(text(x2 + 180, y2 + 132, "Січна площина на висоті h = d", size=11, color=NEG, bold=True))
    
    render(os.path.join(OUT, "straight-skeleton-propagation.svg"), W, H, *parts)

if __name__ == "__main__":
    fig_offset_concept()
    fig_join_types()
    fig_deflation_events()
    fig_straight_skeleton()
    print("Фігури успішно згенеровано.")
