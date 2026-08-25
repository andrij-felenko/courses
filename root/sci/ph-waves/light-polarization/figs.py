# -*- coding: utf-8 -*-
import os
import sys

# Шлях до кореневого каталогу scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def generate_polarization_types():
    w, h = 760, 260
    frags = []

    # Заголовок панелі
    frags.append(text(w / 2, 25, "Основні види поляризації світлової хвилі", size=16, bold=True))

    # Панель 1: Лінійна поляризація
    frags.append(rect(20, 45, 230, 195, fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    frags.append(text(135, 70, "Лінійна поляризація", size=14, bold=True, color="#1e293b"))
    frags.append(line(50, 160, 220, 160, color="#94a3b8", sw=1, dash="4,4")) # x-axis
    frags.append(line(135, 90, 135, 225, color="#94a3b8", sw=1, dash="4,4")) # y-axis
    # Траєкторія лінійна під 45 градусів
    frags.append(line(85, 210, 185, 110, color=POS, sw=2.5))
    frags.append(arrow(135, 160, 170, 125, color=POS, sw=2))
    frags.append(circle(170, 125, 3.5, fill=POS, stroke=POS))
    frags.append(text(135, 238, "Δφ = 0 або π", size=12, color=MUTED))

    # Панель 2: Кругова поляризація
    frags.append(rect(265, 45, 230, 195, fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    frags.append(text(380, 70, "Кругова поляризація", size=14, bold=True, color="#1e293b"))
    frags.append(line(295, 160, 465, 160, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(380, 90, 380, 225, color="#94a3b8", sw=1, dash="4,4"))
    # Коло
    frags.append(circle(380, 160, 50, fill="none", stroke=NEG, sw=2.5))
    frags.append(arrow(380, 160, 415, 125, color=NEG, sw=2))
    frags.append(circle(415, 125, 3.5, fill=NEG, stroke=NEG))
    # Стрілка обертання
    frags.append(text(380, 238, "E₀x = E₀y, Δφ = ±π/2", size=12, color=MUTED))

    # Панель 3: Еліптична поляризація
    frags.append(rect(510, 45, 230, 195, fill="#f8fafc", stroke="#cbd5e1", sw=1.5))
    frags.append(text(625, 70, "Еліптична поляризація", size=14, bold=True, color="#1e293b"))
    frags.append(line(540, 160, 710, 160, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(line(625, 90, 625, 225, color="#94a3b8", sw=1, dash="4,4"))
    # Еліпс нахилений
    frags.append('<ellipse cx="625" cy="160" rx="60" ry="32" transform="rotate(-30 625 160)" fill="none" stroke="%s" stroke-width="2.5"/>' % FIELD)
    frags.append(arrow(625, 160, 665, 135, color=FIELD, sw=2))
    frags.append(circle(665, 135, 3.5, fill=FIELD, stroke=FIELD))
    frags.append(text(625, 238, "Загальний випадок Δφ", size=12, color=MUTED))

    render(os.path.join(IMG_DIR, "polarization-types.svg"), w, h, *frags)

def generate_malus_law():
    w, h = 740, 280
    frags = []

    # Неполяризоване світло
    frags.append(text(80, 35, "Неполяризоване світло", size=13, bold=True))
    frags.append(arrow(20, 150, 140, 150, color=LINE, sw=3))
    # Вектори неполяризованого світла (зірочка)
    frags.append(line(60, 120, 60, 180, color=POS, sw=1.8))
    frags.append(line(39, 130, 81, 170, color=POS, sw=1.8))
    frags.append(line(39, 170, 81, 130, color=POS, sw=1.8))
    frags.append(text(60, 200, "Інтенсивність I₀", size=12, color=INK))

    # Поляризатор P1 (вертикальний)
    box1, w1, h1 = textbox(190, 150, "Поляризатор P₁\n(0°)", size=13, pad=8, fill="#e2e8f0", stroke="#475569", bold=True)
    frags.append(box1)

    # Промінь після P1
    frags.append(arrow(235, 150, 390, 150, color=LINE, sw=2.5))
    frags.append(line(310, 120, 310, 180, color=POS, sw=2.5)) # тільки вертикальний вектор
    frags.append(text(310, 200, "I₁ = I₀ / 2\n(лінійна vertical)", size=12, color=INK))

    # Аналізатор P2 (під кутом θ)
    box2, w2, h2 = textbox(445, 150, "Аналізатор P₂\n(кут θ)", size=13, pad=8, fill="#e2e8f0", stroke="#475569", bold=True)
    frags.append(box2)

    # Промінь після P2
    frags.append(arrow(495, 150, 670, 150, color=LINE, sw=2))
    frags.append(line(580, 130, 605, 170, color=POS, sw=2.5)) # нахилений вектор
    frags.append(text(580, 200, "I₂ = I₁ · cos² θ", size=13, bold=True, color=POS))

    render(os.path.join(IMG_DIR, "malus-law.svg"), w, h, *frags)

def generate_brewster_angle():
    w, h = 720, 320
    frags = []

    # Межа двох середовищ
    frags.append(rect(40, 160, 640, 140, fill="#f1f5f9", stroke="none"))
    frags.append(line(40, 160, 680, 160, color="#475569", sw=2))
    frags.append(text(90, 140, "Середовище 1 (n₁)", size=13, bold=True, color="#334155"))
    frags.append(text(90, 190, "Середовище 2 (n₂)", size=13, bold=True, color="#334155"))

    # Нормаль
    frags.append(line(360, 30, 360, 290, color="#94a3b8", sw=1.5, dash="5,5"))
    frags.append(text(385, 45, "Нормаль", size=12, color=MUTED))

    # Падаючий промінь під кутом Брюстера
    frags.append(arrow(140, 40, 360, 160, color=LINE, sw=2.5))
    frags.append(text(210, 45, "Падаюче природне світло", size=12, color=INK))
    # Вектори s та p у падаючому
    frags.append(circle(250, 100, 4, fill=NEG, stroke=NEG))
    frags.append(line(242, 92, 258, 108, color=POS, sw=2))

    # Відбитий промінь (під тим же кутом до нормалі) -> (580, 40)
    frags.append(arrow(360, 160, 580, 40, color=POS, sw=2.5))
    frags.append(text(540, 60, "100% s-поляризоване", size=13, bold=True, color=POS))
    # Тільки крапки (s-поляризація, перпендикулярна до площини)
    frags.append(circle(440, 116, 4.5, fill=POS, stroke=POS))
    frags.append(circle(500, 83, 4.5, fill=POS, stroke=POS))

    # Заломлений промінь -> перпендикулярний до відбитого! Кут між відбитим і заломленим 90°
    frags.append(arrow(360, 160, 465, 290, color=NEG, sw=2.5))
    frags.append(text(490, 240, "Заломлений промінь\n(частково p-поляризований)", size=12, color=NEG))

    # Прямий кут між відбитим та заломленим
    frags.append(line(390, 144, 406, 173, color="#64748b", sw=1.5))
    frags.append(line(376, 189, 406, 173, color="#64748b", sw=1.5))
    frags.append(text(415, 162, "90°", size=12, bold=True, color="#475569"))

    # Формула Брюстера
    frags.append(text(210, 260, "tg θ_B = n₂ / n₁", size=14, bold=True, color=INK))

    render(os.path.join(IMG_DIR, "brewster-angle.svg"), w, h, *frags)

def generate_birefringence():
    w, h = 720, 280
    frags = []

    # Кристал (паралелепіпед / прямокутник)
    frags.append(rect(240, 50, 260, 180, fill="#e0f2fe", stroke="#0284c7", sw=2, rx=4))
    frags.append(text(370, 75, "Одновісний кристал\n(Ісландський шпат)", size=13, bold=True, color="#0369a1"))

    # Оптична вісь (пунктир)
    frags.append(line(260, 210, 480, 70, color="#0284c7", sw=1.5, dash="6,4"))
    frags.append(text(500, 65, "Оптична вісь", size=12, color="#0369a1", italic=True))

    # Падаючий промінь
    frags.append(arrow(40, 140, 240, 140, color=LINE, sw=2.5))
    frags.append(text(120, 120, "Неполяризоване світло", size=12, bold=True))
    frags.append(circle(140, 140, 4, fill=NEG, stroke=NEG))
    frags.append(line(140, 125, 140, 155, color=POS, sw=2))

    # Ззвичайний промінь (o-ray) - прямий
    frags.append(line(240, 140, 500, 140, color=NEG, sw=2))
    frags.append(arrow(500, 140, 660, 140, color=NEG, sw=2))
    frags.append(circle(580, 140, 4, fill=NEG, stroke=NEG))
    frags.append(text(600, 125, "Ззвичайний промінь (o-промінь, nₒ)", size=12, bold=True, color=NEG))

    # Незвичайний промінь (e-ray) - відхиляється
    frags.append(line(240, 140, 500, 90, color=POS, sw=2))
    frags.append(arrow(500, 90, 660, 90, color=POS, sw=2))
    frags.append(line(580, 78, 580, 102, color=POS, sw=2))
    frags.append(text(600, 75, "Незвичайний промінь (e-промінь, nₑ)", size=12, bold=True, color=POS))

    render(os.path.join(IMG_DIR, "birefringence-crystal.svg"), w, h, *frags)

def generate_waveplate():
    w, h = 740, 270
    frags = []

    # Тракт проходження крізь хвильову пластинку
    frags.append(text(370, 25, "Перетворення поляризації хвильовою пластинкою λ/4", size=15, bold=True))

    # Вхідне лінійно поляризоване світло (під 45°)
    frags.append(arrow(40, 140, 220, 140, color=POS, sw=2.5))
    frags.append(line(120, 115, 140, 165, color=POS, sw=2.5))
    frags.append(text(130, 185, "Лінійна (45°)", size=12, color=INK))

    # Фазова пластинка (прямокутник)
    box, bw, bh = textbox(330, 140, "Чвертьхвильова\nпластинка (λ/4)\nΔφ = π/2", size=13, pad=10, fill="#fef3c7", stroke="#d97706", bold=True)
    frags.append(box)

    # Осі пластинки - малюємо ПОЗА центральним прямокутником
    frags.append(line(330, 50, 330, 85, color="#d97706", sw=1.5, dash="4,3"))
    frags.append(line(330, 195, 330, 230, color="#d97706", sw=1.5, dash="4,3"))
    frags.append(text(380, 65, "Повільна вісь", size=11, color="#b45309"))

    # Вихідне кругово поляризоване світло
    frags.append(arrow(440, 140, 680, 140, color=NEG, sw=2.5))
    frags.append(circle(560, 140, 28, fill="none", stroke=NEG, sw=2.5))
    frags.append(arrow(560, 140, 580, 120, color=NEG, sw=2))
    frags.append(text(560, 195, "Кругова поляризація", size=13, bold=True, color=NEG))

    render(os.path.join(IMG_DIR, "waveplate-action.svg"), w, h, *frags)

if __name__ == "__main__":
    generate_polarization_types()
    generate_malus_law()
    generate_brewster_angle()
    generate_birefringence()
    generate_waveplate()
    print("Всі SVG-фігури успішно згенеровано.")
