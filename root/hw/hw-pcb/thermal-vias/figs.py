# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'Теплові перехідні отвори (thermal vias)'."""

import os
import sys

# Підключення svgkit із кореневої теки scripts (4 рівні вгору від root/hw/hw-pcb/thermal-vias)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_conduction_contrast():
    """Фігура 1: Контраст теплопровідності міді й FR-4: тепловий затор без via проти дренажу з via."""
    w, h = 820, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Фізика теплопередачі крізь плату: діелектрик FR-4 проти мідних via", size=16, bold=True))

    # Ліва панель: БЕЗ перехідних отворів (Тепловий затор)
    frags.append(rect(35, 65, 360, 240, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    frags.append(text(215, 88, "БЕЗ ТЕПЛОВИХ VIA: Тепловий затор", size=13, color=POS, bold=True))

    # Чіп / джерело тепла зверху
    frags.append(rect(140, 105, 150, 30, fill="#fee2e2", stroke=POS, sw=2, rx=3))
    frags.append(text(215, 124, "QFN Chip (P = 3 Вт)", size=11, color=POS, bold=True))

    # Верхній шар міді (Pad)
    frags.append(rect(120, 135, 190, 8, fill="#f59e0b", stroke="#b45309", sw=1, rx=1))
    frags.append(text(340, 142, "Мідь 35 мкм", size=10, color="#b45309", anchor="start"))

    # Тіло FR-4
    frags.append(rect(55, 143, 320, 75, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=2))
    frags.append(text(215, 168, "Діелектрик FR-4 (h = 1.6 мм)", size=12, color="#047857", bold=True))
    frags.append(text(215, 186, "k_z ≈ 0.28 Вт/(м·К) — ТЕПЛОІЗОЛЯТОР!", size=10.5, color=POS, bold=True))
    frags.append(text(215, 204, "R_th(FR-4) ≈ 60 К/Вт (заблоковано)", size=10, color=POS))

    # Нижній шар міді
    frags.append(rect(55, 218, 320, 8, fill="#cbd5e1", stroke="#64748b", sw=1, rx=1))
    frags.append(text(215, 245, "Нижня мідь лишається холодною", size=10, color=MUTED))

    # Температурний маркер зліва
    frags.append(rect(55, 105, 75, 30, fill="#fef2f2", stroke=POS, sw=1, rx=3))
    frags.append(text(92, 124, "T_J > 165 °C", size=10.5, color=POS, bold=True))

    # Права панель: З масивом VIA (Тепловий дренаж)
    frags.append(rect(425, 65, 360, 240, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(605, 88, "З МАТРИЦЕЮ VIA: Вертикальний дренаж", size=13, color=FIELD, bold=True))

    # Чіп
    frags.append(rect(530, 105, 150, 30, fill="#e0f2fe", stroke="#0284c7", sw=2, rx=3))
    frags.append(text(605, 124, "QFN Chip (P = 3 Вт)", size=11, color="#0369a1", bold=True))

    # Верхній шар міді
    frags.append(rect(510, 135, 190, 8, fill="#f59e0b", stroke="#b45309", sw=1, rx=1))

    # Окремі сегменти діелектрика FR-4 між отворами
    frags.append(rect(445, 143, 60, 75, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=0))
    frags.append(rect(523, 143, 29, 75, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=0))
    frags.append(rect(570, 143, 70, 75, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=0))
    frags.append(rect(658, 143, 29, 75, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=0))
    frags.append(rect(705, 143, 60, 75, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=0))

    # 4 перехідні отвори
    via_xs = [514, 561, 649, 696]
    for vx in via_xs:
        # Мідна гільза
        frags.append(rect(vx - 7, 135, 14, 91, fill="#f59e0b", stroke="#b45309", sw=1, rx=0))
        # Порожнистий центр
        frags.append(rect(vx - 3, 143, 6, 75, fill="#ffffff", stroke="#94a3b8", sw=0.8, rx=0))
        # Стрілка теплового потоку
        frags.append(arrow(vx, 145, vx, 215, color=POS, sw=1.8))

    # Центральний напис у просторі між via 2 і 3 (x=605)
    frags.append(text(605, 172, "k_Cu ≈ 385", size=10, color="#b45309", bold=True))
    frags.append(text(605, 187, "Вт/(м·К)", size=9.5, color="#b45309"))
    frags.append(text(605, 204, "R_th ≈ 12 К/Вт", size=10.5, color=FIELD, bold=True))

    # Нижня мідна площина (гаряча, відводить тепло)
    frags.append(rect(445, 218, 320, 8, fill="#f59e0b", stroke="#b45309", sw=1, rx=1))
    frags.append(text(605, 245, "Тепло розтікається по нижній площині GND", size=10, color="#b45309", bold=True))

    # Температурний маркер справа
    frags.append(rect(445, 105, 75, 30, fill="#f0fdf4", stroke=FIELD, sw=1, rx=3))
    frags.append(text(482, 124, "T_J ≈ 68 °C", size=10.5, color=FIELD, bold=True))

    # Нижній висновок
    box_summary, _, _ = textbox(w / 2, 355,
                                "Фізичний принцип: Теплопровідність міді (385 Вт/(м·К)) у 1370 разів вища за поперечну провідність FR-4 (0.28 Вт/(м·К)).\n"
                                "• Без отворів склотекстоліт товщиною 1.6 мм працює як термобар'єр: кристал швидко перегрівається та виходить з ладу.\n"
                                "• Металізовані гільзи via прошивають діелектрик і створюють вертикальні теплові магістралі з низьким опором до нижніх шарів.",
                                size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=760)
    frags.append(box_summary)

    render(os.path.join(IMG_DIR, "pcb-thermal-conduction-contrast.svg"), w, h, *frags)


def fig_single_via_anatomy():
    """Фігура 2: Анатомія перехідного отвору в розрізі та геометричний розрахунок площі гільзи."""
    w, h = 820, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Геометрія та тепловий опір одиничного перехідного отвору", size=16, bold=True))

    # Ліва панель: Вертикальний розріз плати з отвором
    frags.append(rect(35, 65, 360, 240, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(215, 84, "Поздовжній розріз перехідного отвору", size=13, bold=True))

    # Верхній і нижній пади міді (розміщені строго вище та нижче осердя)
    frags.append(rect(145, 106, 140, 12, fill="#f59e0b", stroke="#b45309", sw=1.2, rx=1))
    frags.append(rect(145, 238, 140, 12, fill="#f59e0b", stroke="#b45309", sw=1.2, rx=1))

    # Лівий і правий діелектрик FR-4 (від y=118 до y=238)
    frags.append(rect(55, 118, 120, 120, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=2))
    frags.append(text(115, 180, "Діелектрик FR-4", size=11, color="#047857"))
    frags.append(rect(255, 118, 120, 120, fill="#ecfdf5", stroke="#10b981", sw=1.2, rx=2))
    frags.append(text(315, 180, "Діелектрик FR-4", size=11, color="#047857"))

    # Металізована мідна стінка отвору (від y=118 до y=238)
    frags.append(rect(175, 118, 80, 120, fill="#f59e0b", stroke="#b45309", sw=1.5, rx=0))
    # Порожнисте осердя (свердління)
    frags.append(rect(195, 118, 40, 120, fill="#ffffff", stroke="#64748b", sw=1.2, rx=0))

    # Розмірні стрілки товщини плати h
    frags.append(line(340, 118, 340, 238, color=INK, sw=1.5))
    frags.append(arrow(340, 100, 340, 118, color=INK, sw=1.5))
    frags.append(arrow(340, 256, 340, 238, color=INK, sw=1.5))
    frags.append(text(362, 178, "h\n(1.6 мм)", size=10, bold=True))

    # Розмірні стрілки діаметра свердла d (рознесено від тексту)
    frags.append(text(215, 94, "d = 0.3 мм", size=10.5, bold=True))
    frags.append(line(175, 102, 255, 102, color=INK, sw=1.2))
    frags.append(arrow(155, 102, 175, 102, color=INK, sw=1.2))
    frags.append(arrow(275, 102, 255, 102, color=INK, sw=1.2))

    # Розмірні стрілки товщини міднення t
    frags.append(line(175, 262, 195, 262, color="#b45309", sw=1.2))
    frags.append(arrow(160, 262, 175, 262, color="#b45309", sw=1.2))
    frags.append(arrow(210, 262, 195, 262, color="#b45309", sw=1.2))
    frags.append(text(185, 278, "t = 25 мкм", size=10, color="#b45309", bold=True))

    # Тепловий потік через стінки
    frags.append(arrow(185, 122, 185, 234, color=POS, sw=2))
    frags.append(arrow(245, 122, 245, 234, color=POS, sw=2))

    # Права панель: Поперечний переріз трубки та формули
    frags.append(rect(425, 65, 360, 240, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(605, 84, "Поперечний переріз мідної гільзи", size=13, bold=True))

    # Кільце міді
    frags.append(circle(605, 150, 48, fill="#f59e0b", stroke="#b45309", sw=2))
    frags.append(circle(605, 150, 36, fill="#ffffff", stroke="#64748b", sw=1.5))

    frags.append(text(605, 153, "Повітря", size=10, color=MUTED))
    frags.append(text(685, 130, "Мідна стінка t", size=10.5, color="#b45309", bold=True))
    frags.append(arrow(665, 136, 642, 144, color="#b45309", sw=1.2))

    # Формули площі та опору
    frags.append(text(605, 222, "A_Cu = π · (d · t − t²)  [площа перерізу]", size=11, bold=True))
    frags.append(text(605, 246, "R_th,via = h / (k_Cu · A_Cu)  [тепловий опір]", size=11, color=POS, bold=True))
    frags.append(text(605, 270, "Для d=0.3 мм, t=25 мкм, h=1.6 мм  →  R_th ≈ 193 К/Вт", size=10, color="#047857"))

    # Нижній висновок
    box_calc, _, _ = textbox(w / 2, 355,
                             "Аналітичний розрахунок одиничного отвору (thermal via):\n"
                             "• Площа кільця: A_Cu = π · (0.3 · 0.025 − 0.025²) мм² = π · (0.0075 − 0.000625) ≈ 0.0216 мм² = 2.16·10⁻⁸ м²\n"
                             "• Опір гільзи: R_th,via = 0.0016 м / (385 Вт/(м·К) · 2.16·10⁻⁸ м²) ≈ 192.5 К/Вт (або ~120 К/Вт для плати товщиною 1.0 мм)\n"
                             "• Оскільки один отвір має високий опір (~193 К/Вт), під силові мікросхеми встановлюють паралельний масив з 9–25 via.",
                             size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=760)
    frags.append(box_calc)

    render(os.path.join(IMG_DIR, "thermal-via-anatomy-formula.svg"), w, h, *frags)


def fig_via_matrix_wicking():
    """Фігура 3: Матриця отворів під PowerPAD, трафаретні віконця та ризик solder wicking."""
    w, h = 820, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Матриця теплових отворів під PowerPAD та проблема витікання припою", size=16, bold=True))

    # Ліва панель: Вигляд зверху: Footprint з матрицею 4x4 та віконним трафаретом
    frags.append(rect(35, 65, 360, 240, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(215, 86, "Топологія PowerPAD (матриця 4×4)", size=13, bold=True))

    # Exposed Copper Pad (5x5 mm)
    frags.append(rect(115, 105, 200, 140, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=3))
    frags.append(text(215, 120, "Мідний майданчик 5.0 × 5.0 мм", size=10, color="#b45309", bold=True))

    # 4 віконця паяльної пасти (Windowed Stencil 60% coverage)
    frags.append('<rect x="125" y="130" width="80" height="50" rx="2" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,2"/>')
    frags.append('<rect x="225" y="130" width="80" height="50" rx="2" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,2"/>')
    frags.append('<rect x="125" y="185" width="80" height="50" rx="2" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,2"/>')
    frags.append('<rect x="225" y="185" width="80" height="50" rx="2" fill="#e2e8f0" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,2"/>')

    # Масив отворів via
    for row in range(3):
        for col in range(4):
            vx = 140 + col * 50
            vy = 145 + row * 40
            frags.append(circle(vx, vy, 6, fill="#f59e0b", stroke="#b45309", sw=1.2))
            frags.append(circle(vx, vy, 3.5, fill="#ffffff", stroke="#64748b", sw=0.8))

    frags.append(text(215, 260, "Крок отворів (Pitch) = 1.0–1.2 мм", size=10, bold=True))
    frags.append(text(215, 275, "Трафарет: 4 вікна (50–70% покриття пастою)", size=9.5, color=MUTED))

    # Права панель: Solder Wicking (d > 0.35 мм) vs Оптимум (d = 0.3 мм)
    frags.append(rect(425, 65, 360, 240, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(605, 86, "Вплив діаметра via на пайку (Solder Wicking)", size=13, bold=True))

    # Верхній підблок: Помилка (d = 0.5 мм)
    frags.append(rect(440, 105, 330, 85, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(605, 120, "НЕПРАВИЛЬНО: Діаметр d ≥ 0.5 мм (Wicking)", size=11, color=POS, bold=True))
    # Схема витікання
    frags.append(rect(460, 130, 60, 8, fill="#3b82f6", stroke="#1d4ed8", sw=1)) # чіп
    frags.append(rect(460, 138, 20, 4, fill="#94a3b8", stroke="#64748b", sw=0.8)) # тонкий припій (голодування)
    frags.append(rect(500, 138, 20, 4, fill="#fef2f2", stroke=POS, sw=0.8)) # порожнина / void
    frags.append(text(510, 150, "Пустота > 50%!", size=9.5, color=POS, bold=True))
    frags.append(rect(475, 142, 14, 35, fill="#f59e0b", stroke="#b45309", sw=1))
    # Припій стік у via
    frags.append(rect(477, 142, 10, 25, fill="#94a3b8", stroke="#475569", sw=1))
    frags.append(circle(482, 175, 6, fill="#94a3b8", stroke="#475569", sw=1)) # крапля знизу
    frags.append(text(555, 172, "Крапля знизу (solder ball)", size=9.5, color=POS))

    # Нижній підблок: Норма (d = 0.3 мм)
    frags.append(rect(440, 195, 330, 95, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(605, 210, "ПРАВИЛЬНО: Діаметр d ≤ 0.3 мм (Поверхневий натяг)", size=11, color=FIELD, bold=True))
    # Схема нормальної пайки
    frags.append(rect(460, 222, 60, 8, fill="#3b82f6", stroke="#1d4ed8", sw=1))
    frags.append(rect(460, 230, 60, 5, fill="#94a3b8", stroke="#475569", sw=0.8)) # рівномірний шов
    frags.append(rect(478, 235, 10, 35, fill="#f59e0b", stroke="#b45309", sw=1))
    frags.append(rect(480, 235, 6, 8, fill="#94a3b8", stroke="#475569", sw=0.8)) # легкий меніск
    frags.append(text(555, 245, "Суцільний шов припою", size=9.5, color=FIELD, bold=True))
    frags.append(text(555, 260, "Меніск блокує витікання", size=9.5, color=MUTED))

    # Нижній блок правил
    box_rules, _, _ = textbox(w / 2, 355,
                              "Правила проектування теплової матриці (Design Rules):\n"
                              "1. Оптимальний діаметр свердла d = 0.3 мм (12 mil). Отвори > 0.35 мм засмоктують припій всередину (solder wicking).\n"
                              "2. Крок сітки (Pitch) = 1.0–1.2 мм. Згущення менше 0.8 мм веде до перекриття зон розтікання і спадної віддачі.\n"
                              "3. Трафаретний друк: віконна матриця (Windowing) із заповненням 50–70% запобігає вибуховому кипінню флюсу та порожнинам.",
                              size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=760)
    frags.append(box_rules)

    render(os.path.join(IMG_DIR, "via-matrix-solder-wicking.svg"), w, h, *frags)


def fig_ipc4761_vippo():
    """Фігура 4: Класифікація переходів за IPC-4761 та технологія VIPPO (Type VII)."""
    w, h = 820, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Технології захисту та заповнення переходів за IPC-4761 і VIPPO", size=16, bold=True))

    types = [
        ("Type I (Tented)", "Тентування маскою", "#3b82f6", False),
        ("Type III (Plugged)", "Заповнення отвору", "#8b5cf6", False),
        ("Type VII (VIPPO)", "Заповнено + Міднення", FIELD, True)
    ]

    for idx, (title, subtitle, col, is_vippo) in enumerate(types):
        bx = 40 + idx * 250
        by = 65
        bw = 240
        bh = 245

        frags.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=col, sw=1.8 if is_vippo else 1.2, rx=6))
        frags.append(text(bx + bw / 2, by + 22, title, size=13, color=col, bold=True))
        frags.append(text(bx + bw / 2, by + 38, subtitle, size=10.5, color=MUTED))

        # Пади зверху і знизу (y = by + 60 для верхнього, y = by + 148 для нижнього)
        frags.append(rect(bx + 65, by + 60, 110, 8, fill="#f59e0b", stroke="#b45309", sw=1))
        frags.append(rect(bx + 65, by + 148, 110, 8, fill="#f59e0b", stroke="#b45309", sw=1))

        # Окремі лівий і правий діелектрики (від y = by + 68 до y = by + 148)
        frags.append(rect(bx + 15, by + 68, 75, 80, fill="#ecfdf5", stroke="#10b981", sw=1, rx=0))
        frags.append(rect(bx + 150, by + 68, 75, 80, fill="#ecfdf5", stroke="#10b981", sw=1, rx=0))

        # Мідна гільза (від y = by + 68 до y = by + 148)
        frags.append(rect(bx + 90, by + 68, 60, 80, fill="#f59e0b", stroke="#b45309", sw=1.2))

        if idx == 0:
            # Type I: Порожнистий центр + маска знизу
            frags.append(rect(bx + 102, by + 68, 36, 80, fill="#ffffff", stroke="#64748b", sw=0.8))
            # Маска (зелена) закриває отвір знизу
            frags.append(rect(bx + 60, by + 156, 120, 6, fill="#15803d", stroke="#166534", sw=1, rx=1))
            frags.append(text(bx + bw / 2, by + 185, "Тентування зі зворотного боку", size=10, bold=True))
            frags.append(text(bx + bw / 2, by + 202, "Верх відкритий під пайку", size=9.5, color=MUTED))
            frags.append(text(bx + bw / 2, by + 220, "Ризик: витікання припою", size=9.5, color=POS))

        elif idx == 1:
            # Type III: Заповнений неелектропровідною смолою/маскою (сіра)
            frags.append(rect(bx + 102, by + 68, 36, 80, fill="#64748b", stroke="#334155", sw=0.8))
            frags.append(text(bx + bw / 2, by + 185, "Заповнено епоксидною смолою", size=10, bold=True))
            frags.append(text(bx + bw / 2, by + 202, "Запобігає wicking", size=9.5, color=MUTED))
            frags.append(text(bx + bw / 2, by + 220, "Поглиблення на паді (дирочка)", size=9.5, color="#b45309"))

        elif idx == 2:
            # Type VII: VIPPO (Заповнено смолою + покритий пласкою міддю зверху)
            frags.append(rect(bx + 102, by + 68, 36, 80, fill="#64748b", stroke="#334155", sw=0.8))
            # Мідне гальванічне покриття зверху (Cap plating)
            frags.append(rect(bx + 65, by + 54, 110, 6, fill="#f59e0b", stroke="#b45309", sw=1.2))
            frags.append(text(bx + bw / 2, by + 185, "Планарне міднення паду (Cap)", size=10, color=FIELD, bold=True))
            frags.append(text(bx + bw / 2, by + 202, "Ідеальна площина під BGA/QFN", size=9.5, color=MUTED))
            frags.append(text(bx + bw / 2, by + 220, "Нуль пустот при пайці!", size=9.5, color=FIELD, bold=True))

    # Нижній висновок
    box_vippo, _, _ = textbox(w / 2, 355,
                              "Порівняння конструкцій за стандартом IPC-4761:\n"
                              "• IPC-4761 Type I/II (Tented): Найдешевше рішення; підходить для відкритих полігонів, але не гарантує герметичності паду.\n"
                              "• IPC-4761 Type VII (VIPPO / POFV): Via-in-Pad Plated Over — заповнення епоксидною пастою, полірування та міднення зверху.\n"
                              "• VIPPO є обов'язковим для BGA з кроком ≤ 0.8 мм та дрібних QFN: усуває втягування припою та забезпечує 100% площу теплового контакту.",
                              size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=760)
    frags.append(box_vippo)

    render(os.path.join(IMG_DIR, "ipc4761-via-types-vippo.svg"), w, h, *frags)


def fig_thermal_equivalent_circuit():
    """Фігура 5: Повний еквівалентний тепловий ланцюг Кристал-Плата-Радіатор з графіком спаду температури."""
    w, h = 820, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.5, rx=8))
    frags.append(text(w / 2, 36, "Еквівалентний тепловий ланцюг: Кристал → Плата → Радіатор → Середовище", size=16, bold=True))

    # Ліва схема: Електричний тепловий ланцюг
    frags.append(rect(35, 65, 450, 240, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(260, 86, "Теплова еквівалентна схема (R_th ланцюг)", size=13, bold=True))

    # Вузли схеми
    nodes = [
        ("T_J (110°C)", "Кристал"),
        ("T_Case (104°C)", "Корпус"),
        ("T_TopPad (103°C)", "Верхня мідь"),
        ("T_BotPad (82°C)", "Нижня мідь"),
        ("T_HS (54°C)", "Радіатор"),
        ("T_A (25°C)", "Повітря")
    ]

    resistors = [
        ("R_θ,JC", "2.0 К/Вт"),
        ("R_θ,solder", "0.3 К/Вт"),
        ("R_θ,vias", "7.0 К/Вт"),
        ("R_θ,TIM", "3.0 К/Вт"),
        ("R_θ,SA", "6.0 К/Вт")
    ]

    # Малювання послідовних резисторів
    for i in range(5):
        rx = 55 + i * 80
        ry = 140

        # Вузол точка
        frags.append(circle(rx, ry, 4, fill=POS if i < 3 else FIELD, stroke=INK, sw=1.5))
        frags.append(text(rx, ry - 14, nodes[i][0].split()[0], size=10, bold=True))

        # Резистор блок
        frags.append(rect(rx + 8, ry - 12, 64, 24, fill="#f8fafc", stroke=INK, sw=1.2, rx=2))
        frags.append(text(rx + 40, ry + 3, resistors[i][0], size=9.5, bold=True))
        frags.append(text(rx + 40, ry + 26, resistors[i][1], size=9.5, color=MUTED))

        # Лінія зв'язку
        frags.append(line(rx + 4, ry, rx + 8, ry, color=INK, sw=1.5))
        frags.append(line(rx + 72, ry, rx + 80, ry, color=INK, sw=1.5))

    # Останній вузол
    last_x = 55 + 5 * 80
    frags.append(circle(last_x, ry, 4, fill=NEG, stroke=INK, sw=1.5))
    frags.append(text(last_x, ry - 14, "T_A", size=10, bold=True))

    # Стрілка теплового потоку P
    frags.append(arrow(55, 205, 435, 205, color=POS, sw=2))
    frags.append(text(250, 192, "Тепловий потік P_diss = 4.6 Вт", size=11, color=POS, bold=True))
    frags.append(text(260, 245, "Сумарний опір: R_θ,JA = 2.0 + 0.3 + 7.0 + 3.0 + 6.0 = 18.3 К/Вт", size=10, bold=True))
    frags.append(text(260, 265, "Перегрів: ΔT = 4.6 Вт · 18.3 К/Вт = 84.2 °C  →  T_J = 25 + 84.2 = 109.2 °C", size=10, color=FIELD, bold=True))

    # Права панель: Температурний профіль (графік спаду T)
    frags.append(rect(500, 65, 285, 240, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(642, 86, "Температурний профіль", size=13, bold=True))

    # Осі графіка
    frags.append(line(530, 250, 760, 250, color=INK, sw=1.2)) # X
    frags.append(line(530, 250, 530, 110, color=INK, sw=1.2)) # Y
    frags.append(text(750, 265, "Шлях", size=10, color=MUTED))
    frags.append(text(525, 105, "T (°C)", size=10, color=MUTED))

    # Точки температурного графіка
    temps = [
        (530, 120, "110°"), # T_J
        (560, 130, "104°"), # T_Case
        (590, 132, "103°"), # T_Top
        (650, 180, "82°"),  # T_Bot
        (700, 205, "54°"),  # T_HS
        (750, 245, "25°")   # T_A
    ]

    # Лінії спаду
    for i in range(len(temps) - 1):
        x1, y1, _ = temps[i]
        x2, y2, _ = temps[i + 1]
        frags.append(line(x1, y1, x2, y2, color=POS if i < 3 else FIELD, sw=2))
        frags.append(circle(x1, y1, 3, fill=POS if i < 3 else FIELD, stroke=INK, sw=1))
        frags.append(text(x1, y1 - 8, temps[i][2], size=9.5, bold=True))

    frags.append(circle(temps[-1][0], temps[-1][1], 3, fill=NEG, stroke=INK, sw=1))
    frags.append(text(temps[-1][0], temps[-1][1] - 8, temps[-1][2], size=9.5, bold=True))

    # Нижній висновок
    box_calc, _, _ = textbox(w / 2, 355,
                             "Інженерний розрахунок загального теплового кола:\n"
                             "• Рівняння теплового балансу: T_J = T_A + P · (R_θ,JC + R_θ,solder + R_θ,vias + R_θ,TIM + R_θ,SA)\n"
                             "• Перехідні отвори (R_θ,vias) усувають головне «вузьке горло» плати, знижуючи опір діелектрика з 60 К/Вт до 7 К/Вт.\n"
                             "• Завдяки цьому потужність 4.6 Вт ефективно передається на радіатор, утримуючи кристал у безпечній зоні 109 °C.",
                             size=11.5, pad=12, fill="#f8fafc", stroke="#cbd5e1", min_w=760)
    frags.append(box_calc)

    render(os.path.join(IMG_DIR, "thermal-equivalent-circuit.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_conduction_contrast()
    fig_single_via_anatomy()
    fig_via_matrix_wicking()
    fig_ipc4761_vippo()
    fig_thermal_equivalent_circuit()
    print("Всі 5 фігур для thermal-vias успішно згенеровано в img/")
