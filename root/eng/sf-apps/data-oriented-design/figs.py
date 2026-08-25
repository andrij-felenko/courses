# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми Data-Oriented Design (DOD)."""

import os
import sys

# Підключаємо svgkit із теки scripts у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig1_oop_vs_dod_memory():
    """Порівняння об'єктного підходу (Pointer Soup) та потокового Data-Oriented Design."""
    w, h = 920, 500
    frags = []

    # Заголовок секції ООП
    frags.append(textbox(230, 35, "Об'єктно-орієнтований підхід (AoS / Pointer Soup)", size=14, bold=True, fill="#fdecea", stroke=POS)[0])

    # Пам'ять ООП: розрізнені об'єкти в купі (Heap)
    frags.append(rect(30, 65, 400, 345, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(230, 88, "Оперативна пам'ять (фрагментована купа)", size=12, color=MUTED, bold=True))

    # Масив вказівників
    frags.append(rect(45, 105, 120, 180, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    frags.append(text(105, 123, "vector<Entity*>", size=11, bold=True))
    frags.append(line(45, 132, 165, 132, color=LINE, sw=1))
    
    ptr_y = [150, 185, 220, 255]
    for i, py in enumerate(ptr_y):
        frags.append(rect(50, py - 12, 110, 24, fill=FILL, stroke=LINE, sw=1, rx=3))
        frags.append(text(105, py + 4, f"ptr[{i}] 0x{1000 + i * 4096:04X}", size=10))

    # Розрізнені об'єкти в купі
    objs = [
        (220, 105, "Entity 0", ["vptr", "pos", "vel", "mesh*", "hp", "inv"]),
        (220, 175, "Entity 1", ["vptr", "pos", "vel", "mesh*", "hp", "inv"]),
        (220, 245, "Entity 2", ["vptr", "pos", "vel", "mesh*", "hp", "inv"]),
        (220, 315, "Entity 3", ["vptr", "pos", "vel", "mesh*", "hp", "inv"]),
    ]
    for ox, oy, name, fields in objs:
        frags.append(rect(ox, oy, 195, 60, fill="#fff", stroke=POS, sw=1.2, rx=4))
        frags.append(text(ox + 45, oy + 16, name, size=11, bold=True, color=POS))
        frags.append(text(ox + 140, oy + 16, "64 байти", size=10, color=MUTED))
        frags.append(line(ox, oy + 22, ox + 195, oy + 22, color=POS, sw=0.8))
        
        # Гарячі та холодні поля в об'єкті
        frags.append(rect(ox + 5, oy + 26, 55, 28, fill="#fdecea", stroke=POS, sw=0.8, rx=2))
        frags.append(text(ox + 32, oy + 44, "pos/vel", size=10, color=POS, bold=True))
        
        frags.append(rect(ox + 65, oy + 26, 125, 28, fill="#f4f6f8", stroke=MUTED, sw=0.8, rx=2))
        frags.append(text(ox + 127, oy + 44, "vptr, mesh*, hp, inv", size=10, color=MUTED))

    # Стрілки від вказівників до об'єктів
    for i, py in enumerate(ptr_y):
        frags.append(arrow(165, py, 218, objs[i][1] + 30, color=POS, sw=1.2))

    # Пояснення втрат ООП
    frags.append(textbox(230, 445, "Кеш-промахи: 75% завантажених байтів не потрібні для фізики", size=11, fill="#fdecea", stroke=POS, color=POS)[0])

    # Заголовок секції DOD
    frags.append(textbox(690, 35, "Data-Oriented Design (SoA / Лінійні потоки)", size=14, bold=True, fill="#e8f8f0", stroke=FIELD)[0])

    # Пам'ять DOD: суцільні масиви компонентів
    frags.append(rect(490, 65, 400, 345, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(690, 88, "Оперативна пам'ять (неперервні лінійні буфери)", size=12, color=MUTED, bold=True))

    # Потік позицій
    frags.append(rect(510, 105, 360, 55, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(565, 121, "Потік Positions:", size=11, bold=True, color=FIELD))
    frags.append(text(740, 121, "float x[N], y[N], z[N] — 100% щільність", size=10, color=MUTED))
    for i in range(5):
        frags.append(rect(515 + i * 70, 128, 65, 26, fill="#e8f8f0", stroke=FIELD, sw=1, rx=2))
        frags.append(text(547 + i * 70, 145, f"P[{i}]", size=10, bold=True, color=FIELD))

    # Потік швидкостей
    frags.append(rect(510, 170, 360, 55, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(565, 186, "Потік Velocities:", size=11, bold=True, color=FIELD))
    frags.append(text(740, 186, "float vx[N], vy[N], vz[N] — суміжно", size=10, color=MUTED))
    for i in range(5):
        frags.append(rect(515 + i * 70, 193, 65, 26, fill="#e8f8f0", stroke=FIELD, sw=1, rx=2))
        frags.append(text(547 + i * 70, 210, f"V[{i}]", size=10, bold=True, color=FIELD))

    # Холодні компоненти (окремий масив, не завантажується фізичним циклом)
    frags.append(rect(510, 235, 360, 55, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(text(580, 251, "Холодні компоненти (HP, Mesh, Inv):", size=11, bold=True, color=MUTED))
    frags.append(text(785, 251, "в окремому буфері", size=10, color=MUTED))
    for i in range(4):
        frags.append(rect(515 + i * 88, 258, 82, 26, fill=FILL, stroke=MUTED, sw=0.8, rx=2))
        frags.append(text(556 + i * 88, 275, f"ColdData[{i}]", size=10, color=MUTED))

    # Блок апаратного випереджального читання і SIMD
    frags.append(rect(510, 300, 360, 65, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(690, 318, "Апаратний Prefetcher + SIMD (AVX2 / NEON)", size=11, bold=True, color=NEG))
    frags.append(text(690, 335, "1 кеш-лінія (64B) = 4-5 суцільних векторів координат", size=10, color=INK))
    frags.append(text(690, 351, "0 промахів кешу в циклі, 100% завантаження ALU", size=10, color=FIELD, bold=True))

    # Пояснення переваг DOD
    frags.append(textbox(690, 445, "Ідеальна просторова локальність: передбачуваний лінійний доступ до DRAM", size=11, fill="#e8f8f0", stroke=FIELD, color=FIELD)[0])

    return render(os.path.join(IMG_DIR, "oop-pointer-soup-vs-dod-streams.svg"), w, h, *frags)


def fig2_hot_cold_splitting():
    """Схема розділення даних на гарячі та холодні потоки (Hot/Cold Splitting)."""
    w, h = 860, 400
    frags = []

    frags.append(text(430, 25, "Анатомія об'єкта та розділення на гарячий і холодний потоки", size=16, bold=True))

    # Монолітний об'єкт
    frags.append(rect(40, 55, 340, 315, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(210, 80, "Монолітна структура Entity (96 байтів)", size=13, bold=True))
    frags.append(text(210, 98, "Поля перемішані незалежно від частоти доступу", size=11, color=MUTED))

    fields = [
        ("pos: float[3]", "12B", "Оновлюється щокадру (60/120 Гц)", True),
        ("vel: float[3]", "12B", "Оновлюється щокадру (60/120 Гц)", True),
        ("radius: float", "4B", "Перевірка зіткнень щокадру", True),
        ("health: int", "4B", "Змінюється лише при влучанні", False),
        ("name: char[32]", "32B", "Потрібно лише для UI/діалогів", False),
        ("audio_id: int", "4B", "Звуковий тригер подій", False),
        ("model_asset_ptr", "8B", "Вказівник на ресурс рендеру", False),
        ("inventory_head", "8B", "Вказівник на список предметів", False),
    ]

    y_off = 112
    for name, sz, desc, is_hot in fields:
        col = POS if is_hot else MUTED
        bg = "#fdecea" if is_hot else FILL
        frags.append(rect(55, y_off, 310, 25, fill=bg, stroke=col, sw=1, rx=3))
        frags.append(text(125, y_off + 17, name, size=11, bold=is_hot, color=col))
        frags.append(text(220, y_off + 17, sz, size=10, color=MUTED))
        tag = "HOT" if is_hot else "COLD"
        frags.append(text(330, y_off + 17, tag, size=10, bold=True, color=col))
        y_off += 29

    # Стрілка трансформації
    frags.append(arrow(390, 210, 460, 210, color=INK, sw=2.5))
    frags.append(text(425, 195, "DOD", size=12, bold=True))
    frags.append(text(425, 230, "Розділ", size=11, color=MUTED))

    # Гарячий потік (Hot Buffer)
    frags.append(rect(470, 55, 350, 145, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(645, 78, "Гарячий буфер (Hot Component: 28 байтів)", size=12, bold=True, color=FIELD))
    frags.append(text(645, 96, "Щільно упакований масив [Transform & Physics]", size=10, color=MUTED))

    frags.append(rect(485, 106, 320, 35, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
    frags.append(text(645, 128, "pos[N] (12B) | vel[N] (12B) | radius[N] (4B)", size=11, bold=True, color=FIELD))
    frags.append(text(645, 160, "1 кеш-лінія (64B) вміщує дані понад 2 сутностей!", size=10, color=FIELD, bold=True))
    frags.append(text(645, 178, "Фізичний цикл читає 100% корисної інформації", size=10, color=INK))

    # Холодний потік (Cold Buffer)
    frags.append(rect(470, 225, 350, 145, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=6))
    frags.append(text(645, 248, "Холодний буфер (Cold Component: 56 байтів)", size=12, bold=True, color=MUTED))
    frags.append(text(645, 266, "Виділений масив або геш-таблиця метаданих", size=10, color=MUTED))

    frags.append(rect(485, 276, 320, 35, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    frags.append(text(645, 298, "health[N] | name[N] | audio[N] | asset[N] | inv[N]", size=10, color=MUTED))
    frags.append(text(645, 330, "Кеш L1/L2 НЕ захаращується іменами й інвентарем", size=10, bold=True, color=NEG))
    frags.append(text(645, 348, "Зчитується лише за рідкісними подіями (UI, смерть)", size=10, color=MUTED))

    return render(os.path.join(IMG_DIR, "hot-cold-splitting.svg"), w, h, *frags)


def fig3_sparse_set_ecs():
    """Схема роботи структури Sparse Set для зберігання та ітерації компонентів."""
    w, h = 880, 440
    frags = []

    frags.append(text(440, 25, "Механіка Sparse Set: O(1) пошук за Entity ID та щільна ітерація", size=16, bold=True))

    # Розріджений масив (Sparse Array)
    frags.append(rect(40, 55, 240, 360, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(160, 78, "Sparse Array (Індекс = Entity ID)", size=12, bold=True, color=NEG))
    frags.append(text(160, 95, "Пряма адресація, дозволені дірки", size=10, color=MUTED))

    sparse_data = [(0, "0", True), (1, "null", False), (2, "1", True), (3, "null", False), (4, "null", False), (5, "2", True), (6, "null", False), (7, "3", True)]
    for i, (eid, val, active) in enumerate(sparse_data):
        y = 110 + i * 34
        bg = "#eaf0fd" if active else "#ffffff"
        col = NEG if active else MUTED
        frags.append(rect(55, y, 210, 28, fill=bg, stroke=col, sw=1, rx=3))
        frags.append(text(95, y + 18, f"Entity #{eid}:", size=11, bold=True))
        frags.append(text(190, y + 18, f"idx = {val}", size=11, bold=active, color=col))

    # Стрілки мапінгу
    dense_targets = {0: 160, 2: 210, 5: 260, 7: 310}
    for eid, target_y in dense_targets.items():
        src_y = 110 + eid * 34 + 14
        frags.append(arrow(265, src_y, 370, target_y, color=NEG, sw=1.5))

    # Щільні масиви (Dense Arrays)
    frags.append(rect(360, 55, 480, 360, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(600, 78, "Dense Storage (Неперервні щільні масиви)", size=12, bold=True, color=FIELD))
    frags.append(text(600, 95, "Ідеальна щільність пам'яті: жодних дірок чи пропусків", size=10, color=MUTED))

    # Заголовки стовпців
    frags.append(rect(380, 110, 90, 24, fill=FILL, stroke=LINE, sw=1, rx=2))
    frags.append(text(425, 126, "Dense Entities", size=10, bold=True))
    frags.append(rect(480, 110, 170, 24, fill=FILL, stroke=LINE, sw=1, rx=2))
    frags.append(text(565, 126, "Position (Component Data)", size=10, bold=True))
    frags.append(rect(660, 110, 160, 24, fill=FILL, stroke=LINE, sw=1, rx=2))
    frags.append(text(740, 126, "Velocity (Component Data)", size=10, bold=True))

    dense_rows = [
        (0, "Entity #0", "{ x: 10.0, y: 5.0 }", "{ vx: 1.0, vy: 0.0 }"),
        (1, "Entity #2", "{ x: 25.0, y: 12.0 }", "{ vx: 0.0, vy: -1.0 }"),
        (2, "Entity #5", "{ x: -4.0, y: 80.0 }", "{ vx: 2.5, vy: 0.5 }"),
        (3, "Entity #7", "{ x: 100.0, y: 0.0 }", "{ vx: -0.5, vy: 1.2 }"),
    ]

    for i, (idx, ent, pos, vel) in enumerate(dense_rows):
        y = 140 + i * 50
        frags.append(rect(380, y, 90, 42, fill="#e8f8f0", stroke=FIELD, sw=1, rx=3))
        frags.append(text(425, y + 18, f"[{idx}]", size=10, color=MUTED))
        frags.append(text(425, y + 33, ent, size=10, bold=True, color=FIELD))

        frags.append(rect(480, y, 170, 42, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
        frags.append(text(565, y + 25, pos, size=10, bold=True))

        frags.append(rect(660, y, 160, 42, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
        frags.append(text(740, y + 25, vel, size=10, bold=True))

    # Блок операцій Swap-and-Pop
    frags.append(rect(380, 350, 440, 48, fill="#fff9db", stroke="#f59f00", sw=1.2, rx=4))
    frags.append(text(600, 368, "Видалення O(1) за схемою Swap-and-Pop:", size=11, bold=True, color="#d9480f"))
    frags.append(text(600, 386, "Останній елемент копіюється на місце видаленого, Sparse оновлюється", size=10, color=INK))

    return render(os.path.join(IMG_DIR, "sparse-set-dense-mapping.svg"), w, h, *frags)


def fig4_dataflow_system_pipeline():
    """Конвеєр систем та граф залежностей компонентів у багатопотоковому виконанні."""
    w, h = 880, 420
    frags = []

    frags.append(text(440, 25, "Паралельний конвеєр систем (Job System) на основі графів даних", size=16, bold=True))

    # Буфери компонентів
    comp_boxes = [
        (60, 65, "Positions [Array]", "#27ae60", "#e8f8f0"),
        (260, 65, "Velocities [Array]", "#2457d6", "#eaf0fd"),
        (460, 65, "Colliders [Array]", "#8e44ad", "#f4ecf7"),
        (660, 65, "Health / Damage [Array]", "#c0392b", "#fdecea"),
    ]
    for bx, by, title, col, bg in comp_boxes:
        frags.append(rect(bx, by, 160, 45, fill=bg, stroke=col, sw=1.5, rx=6))
        frags.append(text(bx + 80, by + 27, title, size=11, bold=True, color=col))

    # Системи першої фази (паралельні)
    frags.append(rect(80, 160, 220, 80, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(190, 185, "Movement System", size=13, bold=True))
    frags.append(text(190, 205, "READ: Velocities", size=10, color=NEG, bold=True))
    frags.append(text(190, 223, "WRITE: Positions", size=10, color=FIELD, bold=True))

    frags.append(rect(580, 160, 220, 80, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(690, 185, "AI Behavior System", size=13, bold=True))
    frags.append(text(690, 205, "READ: Positions, Health", size=10, color=NEG, bold=True))
    frags.append(text(690, 223, "WRITE: Velocities (Intent)", size=10, color=FIELD, bold=True))

    # Стрілки доступу першої фази
    frags.append(arrow(140, 110, 140, 160, color=FIELD, sw=1.5))  # Pos -> Movement
    frags.append(arrow(310, 110, 230, 160, color=NEG, sw=1.5))    # Vel -> Movement
    frags.append(arrow(690, 110, 690, 160, color=POS, sw=1.5))    # Health -> AI
    frags.append(arrow(630, 160, 360, 110, color=FIELD, sw=1.5))  # AI -> Vel

    # Бар'єр синхронізації фаз
    frags.append(line(40, 270, 840, 270, color=MUTED, sw=1.5, dash="6,6"))
    frags.append(textbox(440, 270, "Фазовий бар'єр (Frame Sync Point / Dependency Barrier)", size=11, fill="#ffffff", stroke=MUTED, color=MUTED)[0])

    # Системи другої фази (після оновлення координат)
    frags.append(rect(330, 305, 220, 80, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(440, 330, "Collision Resolution", size=13, bold=True))
    frags.append(text(440, 350, "READ: Positions, Colliders", size=10, color=NEG, bold=True))
    frags.append(text(440, 368, "WRITE: Health (Apply Damage)", size=10, color=POS, bold=True))

    # Стрілки другої фази
    frags.append(arrow(190, 240, 360, 305, color=LINE, sw=1.5))
    frags.append(arrow(540, 110, 450, 305, color="#8e44ad", sw=1.5))
    frags.append(arrow(520, 305, 690, 110, color=POS, sw=1.5))

    return render(os.path.join(IMG_DIR, "dataflow-system-pipeline.svg"), w, h, *frags)


if __name__ == "__main__":
    fig1_oop_vs_dod_memory()
    fig2_hot_cold_splitting()
    fig3_sparse_set_ecs()
    fig4_dataflow_system_pipeline()
    print("Всі фігури успішно згенеровано в img/")
