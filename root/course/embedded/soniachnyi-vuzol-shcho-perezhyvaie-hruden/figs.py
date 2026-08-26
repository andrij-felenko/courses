# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Сонячний вузол, що переживає грудень'."""

import sys
import os

# scripts/ у корені репо: 4 рівні вгору від root/course/embedded/soniachnyi-vuzol-shcho-perezhyvaie-hruden
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_winter_insolation():
    """Фігура 1: Геометрія сонячного дефіциту, атмосфера AM та кут нахилу панелі."""
    w, h = 920, 480
    frags = []

    # Фон секцій
    frags.append(rect(20, 20, 280, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(320, 20, 280, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(rect(620, 20, 280, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Секція 1: Геометрія сонця та атмосфера
    frags.append(text(160, 48, "1. Сонячний кут і атмосфера", size=14, bold=True, color=INK))
    frags.append(text(160, 70, "Широта 50° пн. ш. (Київ / Львів)", size=11, color=MUTED))

    # Земля й горизонт
    frags.append(line(40, 230, 280, 230, color="#64748b", sw=2))
    frags.append(text(160, 248, "Горизонт (земля)", size=11, color=MUTED))

    # Атмосфера
    frags.append(line(40, 130, 280, 130, color="#94a3b8", sw=1, dash="4,4"))
    frags.append(text(230, 122, "Межа атмосфери", size=10, color=MUTED))

    # Літнє сонце (63.5°)
    frags.append(circle(90, 100, 14, fill="#fef08a", stroke="#eab308", sw=2))
    frags.append(text(90, 104, "Чер", size=10, bold=True, color="#854d0e"))
    frags.append(arrow(90, 115, 150, 230, color="#eab308", sw=2))
    frags.append(text(110, 160, "63.5°", size=11, bold=True, color="#854d0e"))
    frags.append(text(85, 180, "AM 1.12", size=11, bold=True, color=FIELD))

    # Зимове сонце (16.5°)
    frags.append(circle(255, 185, 14, fill="#fed7aa", stroke="#f97316", sw=2))
    frags.append(text(255, 189, "Гру", size=10, bold=True, color="#9a3412"))
    frags.append(arrow(255, 195, 155, 230, color="#f97316", sw=2))
    frags.append(text(220, 205, "16.5°", size=11, bold=True, color="#9a3412"))
    frags.append(text(215, 222, "AM 3.51", size=11, bold=True, color=POS))

    # Підсумок секції 1
    t1, _, _ = textbox(160, 350, "Оптичний шлях в атмосфері\nу 3.1 раза довший у грудні.\nІнтенсивність прямих променів\nпадає навіть у ясний день.",
                       size=11, pad=8, min_w=250, fill="#ffffff", stroke="#e2e8f0")
    frags.append(t1)

    # Секція 2: Дефіцит PSH та хмарність
    frags.append(text(460, 48, "2. Провал генерації (PSH)", size=14, bold=True, color=INK))
    frags.append(text(460, 70, "Пікові сонячні години (кВт·год/м²·добу)", size=11, color=MUTED))

    # Стовпчики PSH
    # Червень
    frags.append(rect(360, 100, 50, 140, fill="#fde047", stroke="#ca8a04", sw=1.5, rx=4))
    frags.append(text(385, 125, "5.4", size=13, bold=True, color="#854d0e"))
    frags.append(text(385, 142, "PSH", size=10, color="#854d0e"))
    frags.append(text(385, 255, "Червень", size=11, bold=True, color=INK))
    frags.append(text(385, 270, "Ясно", size=10, color=MUTED))

    # Грудень ясний
    frags.append(rect(435, 195, 50, 45, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=4))
    frags.append(text(460, 215, "1.5", size=12, bold=True, color="#9a3412"))
    frags.append(text(460, 255, "Грудень", size=11, bold=True, color=INK))
    frags.append(text(460, 270, "Ясно", size=10, color=MUTED))

    # Грудень реальний (хмари)
    frags.append(rect(510, 224, 50, 16, fill="#fca5a5", stroke="#dc2626", sw=1.5, rx=4))
    frags.append(text(535, 220, "0.5", size=12, bold=True, color=POS))
    frags.append(text(535, 255, "Грудень", size=11, bold=True, color=INK))
    frags.append(text(535, 270, "Хмарно", size=10, color=POS))

    # Стрілка провалу
    frags.append(arrow(385, 90, 535, 90, color=POS, sw=2))
    frags.append(text(460, 84, "Падіння у 10.8 раза!", size=11, bold=True, color=POS))

    t2, _, _ = textbox(460, 350, "Суцільна хмарність у грудні\nзнижує потік до 50–100 Вт/м².\nПанель на 10 Вт генерує\nлише 0.3–0.6 Вт миттєво.",
                       size=11, pad=8, min_w=250, fill="#ffffff", stroke="#e2e8f0")
    frags.append(t2)

    # Секція 3: Кут нахилу та сніг
    frags.append(text(760, 48, "3. Нахил панелі й сніг", size=14, bold=True, color=INK))
    frags.append(text(760, 70, "Боротьба із засніженням", size=11, color=MUTED))

    # Панель 30 град (погано)
    frags.append(line(650, 170, 710, 140, color=POS, sw=4))
    frags.append(line(650, 137, 710, 137, color="#cbd5e1", sw=6)) # сніг
    frags.append(text(680, 130, "Сніг 5 мм (глухий нуль)", size=10, bold=True, color=POS))
    frags.append(text(680, 190, "Нахил 30° (літній)", size=11, bold=True, color=INK))
    frags.append(text(680, 205, "Вихід = 0.0 Вт", size=11, bold=True, color=POS))

    # Панель 70-90 град (добре)
    frags.append(line(770, 185, 800, 115, color=FIELD, sw=4))
    frags.append(arrow(750, 145, 785, 150, color="#f97316", sw=1.5)) # промінь
    frags.append(text(835, 140, "Сніг злітає", size=10, bold=True, color=FIELD))
    frags.append(text(835, 155, "Прямий кут до грудневого сонця", size=9, color=MUTED))
    frags.append(text(835, 190, "Нахил 70°–90°", size=11, bold=True, color=INK))
    frags.append(text(835, 205, "Вихід = 100% можливого", size=11, bold=True, color=FIELD))

    t3, _, _ = textbox(760, 350, "Вертикальний або крутий нахил\n(65°–75°) не дає снігу затримуватись\nі нормалізує кут падіння променів\nнизького зимового сонця.",
                       size=11, pad=8, min_w=250, fill="#ffffff", stroke="#e2e8f0")
    frags.append(t3)

    render(os.path.join(IMG_DIR, "winter-insolation-drop.svg"), w, h, *frags)


def fig_lithium_plating():
    """Фігура 2: Механізм літієвого платування, дендрити та порівняння хімій."""
    w, h = 920, 480
    frags = []

    # Ліва секція: Електрохімія при T > 0 та T < 0
    frags.append(rect(20, 20, 440, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(240, 48, "Фізика дендритоутворення (Графітовий анод)", size=14, bold=True, color=INK))

    # Стан 1: Нормальна інтеркаляція T > 0 C
    frags.append(rect(35, 75, 410, 160, fill="#ffffff", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(120, 98, "Норма (T > 0 °C): Інтеркаляція", size=12, bold=True, color=FIELD))
    frags.append(rect(50, 115, 80, 105, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(90, 160, "Графіт", size=12, bold=True, color="#334155"))
    frags.append(text(90, 178, "(шари C₆)", size=10, color=MUTED))

    # Іони літію заходять всередину
    frags.append(arrow(210, 135, 135, 135, color=FIELD, sw=2))
    frags.append(arrow(210, 165, 135, 165, color=FIELD, sw=2))
    frags.append(arrow(210, 195, 135, 195, color=FIELD, sw=2))
    frags.append(circle(225, 135, 9, fill="#bbf7d0", stroke=FIELD, sw=1.5))
    frags.append(text(225, 139, "Li⁺", size=10, bold=True, color=FIELD))
    frags.append(circle(225, 165, 9, fill="#bbf7d0", stroke=FIELD, sw=1.5))
    frags.append(text(225, 169, "Li⁺", size=10, bold=True, color=FIELD))
    frags.append(circle(225, 195, 9, fill="#bbf7d0", stroke=FIELD, sw=1.5))
    frags.append(text(225, 199, "Li⁺", size=10, bold=True, color=FIELD))

    frags.append(rect(250, 115, 180, 105, fill="#f0fdf4", stroke="#bbf7d0", sw=1, rx=4))
    frags.append(text(340, 145, "Швидка дифузія", size=11, bold=True, color=FIELD))
    frags.append(text(340, 165, "Потенціал анода > 0 В", size=10, color=INK))
    frags.append(text(340, 185, "C₆ + Li⁺ + e⁻ → LiC₆", size=11, bold=True, color="#1e293b"))

    # Стан 2: Платування літію T < 0 C
    frags.append(rect(35, 250, 410, 195, fill="#ffffff", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(text(160, 273, "Мороз (T < 0 °C): Lithium Plating", size=12, bold=True, color=POS))
    frags.append(rect(50, 290, 80, 140, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(90, 355, "Графіт", size=12, bold=True, color="#334155"))

    # Металевий літій та голки дендритів
    frags.append(rect(130, 290, 14, 140, fill="#94a3b8", stroke="#475569", sw=1))
    # Дендрит що проростає
    frags.append(line(144, 340, 210, 340, color=POS, sw=3))
    frags.append(line(210, 340, 235, 330, color=POS, sw=3))
    frags.append(text(190, 325, "Дендрит", size=10, bold=True, color=POS))

    # Сепаратор
    frags.append(line(240, 290, 240, 430, color="#f59e0b", sw=2, dash="4,3"))
    frags.append(text(240, 282, "Сепаратор", size=9, color="#b45309"))

    frags.append(rect(255, 295, 180, 135, fill="#fef2f2", stroke="#fecaca", sw=1, rx=4))
    frags.append(text(345, 320, "Повільна дифузія в кристалі", size=10, color=POS))
    frags.append(text(345, 340, "Потенціал анода < 0 В", size=10, bold=True, color=POS))
    frags.append(text(345, 365, "Li⁺ + e⁻ → Li⁰ (метал)", size=11, bold=True, color=POS))
    frags.append(text(345, 390, "Прокол сепаратора", size=10, bold=True, color=POS))
    frags.append(text(345, 410, "→ Внутрішнє КЗ й пожежа", size=10, color=POS))

    # Права секція: Порівняння стійких хімій
    frags.append(rect(480, 20, 420, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(690, 48, "Вибір акумуляторної хімії на зиму", size=14, bold=True, color=INK))

    # Картка Li-Ion (LCO / NMC)
    frags.append(rect(495, 75, 390, 80, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=6))
    frags.append(text(555, 98, "Li-Ion / LiPo (NMC/LCO)", size=12, bold=True, color=INK))
    frags.append(text(780, 98, "Заряд < 0 °C ЗАБОРОНЕНО", size=10, bold=True, color=POS))
    frags.append(text(690, 122, "Розряд: −20..+60 °C | Ресурс: 500–1000 циклів", size=10, color=MUTED))
    frags.append(text(690, 140, "У грудні потребує повного вимкнення зарядного тракту", size=10, color=POS))

    # Картка LiFePO4
    frags.append(rect(495, 165, 390, 85, fill="#ffffff", stroke="#e2e8f0", sw=1.5, rx=6))
    frags.append(text(540, 188, "LiFePO4 (LFP)", size=12, bold=True, color=INK))
    frags.append(text(775, 188, "Тільки з підігрівом", size=10, bold=True, color="#b45309"))
    frags.append(text(690, 212, "Розряд: −20..+60 °C | Ресурс: 3000–5000 циклів", size=10, color=MUTED))
    frags.append(text(690, 232, "Зарядний струм спершу гріє PTC-мат до +5 °C, далі заряд", size=10, color=FIELD))

    # Картка LTO
    frags.append(rect(495, 260, 390, 90, fill="#ffffff", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(560, 283, "LTO (Літій-титанат)", size=12, bold=True, color=FIELD))
    frags.append(text(790, 283, "Ідеально для морозу", size=10, bold=True, color=FIELD))
    frags.append(text(690, 307, "Заряд: −30..+55 °C без підігріву | Ресурс: 20000+ циклів", size=10, bold=True, color=FIELD))
    frags.append(text(690, 327, "Потенціал анода 1.55 В (платування неможливе)", size=10, color=MUTED))
    frags.append(text(690, 343, "Мінус: нижча ємність (2.3 В номінал, 70 Вт·год/кг)", size=10, color=MUTED))

    # Картка Na-Ion
    frags.append(rect(495, 360, 390, 85, fill="#ffffff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(555, 383, "Na-Ion (Натрій-іон)", size=12, bold=True, color="#1d4ed8"))
    frags.append(text(785, 383, "Стійкий і дешевий", size=10, bold=True, color="#1d4ed8"))
    frags.append(text(690, 407, "Заряд: −20..+50 °C (струм 0.2C) | Ресурс: 2000–4000 циклів", size=10, color=MUTED))
    frags.append(text(690, 427, "Анод із твердого вуглецю, десольватація Na⁺ швидша за Li⁺", size=10, color=FIELD))

    render(os.path.join(IMG_DIR, "lithium-plating-dendrites.svg"), w, h, *frags)


def fig_adaptive_profile():
    """Фігура 3: Адаптивне регулювання шпаруватості (Dynamic Power Throttling) за рівнем заряду SoC."""
    w, h = 920, 460
    frags = []

    frags.append(rect(20, 20, 880, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(460, 48, "Адаптивне регулювання шпаруватості (Dynamic Duty Cycling)", size=15, bold=True, color=INK))

    # Осі графіка
    frags.append(line(100, 360, 840, 360, color="#475569", sw=2)) # Вісь X (SoC)
    frags.append(line(100, 360, 100, 90, color="#475569", sw=2))  # Вісь Y (Період сну)

    frags.append(text(460, 395, "Рівень заряду акумулятора (State of Charge, SoC %)", size=12, bold=True, color=INK))
    frags.append(text(55, 120, "Період\nсну", size=11, bold=True, color=INK))

    # Розмітка зон
    # Зона 4: Глибока консервація (0..10%)
    frags.append(rect(100, 90, 140, 270, fill="#fee2e2", stroke="none"))
    frags.append(text(170, 115, "Консервація", size=12, bold=True, color=POS))
    frags.append(text(170, 135, "(Hibernate)", size=10, color=POS))
    frags.append(text(170, 280, "I_sleep < 2 мкА", size=11, bold=True, color=POS))
    frags.append(text(170, 300, "Таймер 24 год", size=10, color=POS))

    # Зона 3: Критичний режим (10..30%)
    frags.append(rect(240, 90, 160, 270, fill="#ffedd5", stroke="none"))
    frags.append(text(320, 115, "Виживання", size=12, bold=True, color="#c2410c"))
    frags.append(text(320, 135, "(Survival)", size=10, color="#c2410c"))
    frags.append(text(320, 280, "Сон: 6–12 год", size=11, bold=True, color="#c2410c"))
    frags.append(text(320, 300, "Лише маяк (Heartbeat)", size=10, color="#c2410c"))

    # Зона 2: Економічний режим (30..70%)
    frags.append(rect(400, 90, 240, 270, fill="#fef9c3", stroke="none"))
    frags.append(text(520, 115, "Економічний режим", size=12, bold=True, color="#854d0e"))
    frags.append(text(520, 135, "(Eco / Throttled)", size=10, color="#854d0e"))
    frags.append(text(520, 280, "Сон: 30–60 хв", size=11, bold=True, color="#854d0e"))
    frags.append(text(520, 300, "Пакетування даних", size=10, color="#854d0e"))

    # Зона 1: Звичайний режим (70..100%)
    frags.append(rect(640, 90, 200, 270, fill="#dcfce7", stroke="none"))
    frags.append(text(740, 115, "Звичайний режим", size=12, bold=True, color=FIELD))
    frags.append(text(740, 135, "(Normal)", size=10, color=FIELD))
    frags.append(text(740, 280, "Сон: 5–10 хв", size=11, bold=True, color=FIELD))
    frags.append(text(740, 300, "Усі сенсори активні", size=10, color=FIELD))

    # Поділки SoC
    frags.append(line(240, 360, 240, 368, color="#475569", sw=1.5))
    frags.append(text(240, 380, "10%", size=11, bold=True, color=INK))

    frags.append(line(400, 360, 400, 368, color="#475569", sw=1.5))
    frags.append(text(400, 380, "30%", size=11, bold=True, color=INK))

    frags.append(line(640, 360, 640, 368, color="#475569", sw=1.5))
    frags.append(text(640, 380, "70%", size=11, bold=True, color=INK))

    frags.append(line(840, 360, 840, 368, color="#475569", sw=1.5))
    frags.append(text(840, 380, "100%", size=11, bold=True, color=INK))

    # Крива зміни інтервалу сну (ступінчаста з гістерезисом)
    frags.append(line(100, 150, 240, 150, color=POS, sw=3))
    frags.append(line(240, 150, 240, 210, color=POS, sw=2, dash="3,3"))
    frags.append(line(240, 210, 400, 210, color="#ea580c", sw=3))
    frags.append(line(400, 210, 400, 280, color="#ea580c", sw=2, dash="3,3"))
    frags.append(line(400, 280, 640, 280, color="#ca8a04", sw=3))
    frags.append(line(640, 280, 640, 340, color="#ca8a04", sw=2, dash="3,3"))
    frags.append(line(640, 340, 840, 340, color=FIELD, sw=3))

    # Позначення гістерезису
    t_hyst, _, _ = textbox(520, 240, "Гістерезис переходів: Δ = 5% SoC", size=10, pad=4, fill="#ffffff", stroke="#94a3b8")
    frags.append(t_hyst)

    render(os.path.join(IMG_DIR, "adaptive-power-profile.svg"), w, h, *frags)


def fig_blackout_recovery_fsm():
    """Фігура 4: Скінченний автомат енергетичного менеджера та вихід із блекауту."""
    w, h = 940, 480
    frags = []

    frags.append(rect(20, 20, 900, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(470, 46, "Скінченний автомат живлення (Power Governor FSM)", size=15, bold=True, color=INK))

    # Вузли автомата
    # 1. NORMAL
    b_norm, _, _ = textbox(160, 130, "STATE_NORMAL\nSoC > 70%\nT_sleep = 5 хв\nУсі давачі ON",
                           size=11, pad=10, fill="#dcfce7", stroke=FIELD, min_w=150)
    frags.append(b_norm)

    # 2. ECO
    b_eco, _, _ = textbox(470, 130, "STATE_ECO\n30% < SoC ≤ 70%\nT_sleep = 45 хв\nПакетування ON",
                          size=11, pad=10, fill="#fef9c3", stroke="#ca8a04", min_w=150)
    frags.append(b_eco)

    # 3. SURVIVAL
    b_surv, _, _ = textbox(780, 130, "STATE_SURVIVAL\n10% < SoC ≤ 30%\nT_sleep = 8 год\nЛише Heartbeat",
                           size=11, pad=10, fill="#ffedd5", stroke="#ea580c", min_w=150)
    frags.append(b_surv)

    # 4. HIBERNATE
    b_hib, _, _ = textbox(780, 340, "STATE_HIBERNATE\nSoC ≤ 10% (V < 3.20 В)\nСон 24 год / I < 2 мкА\nНавантаження OFF",
                          size=11, pad=10, fill="#fee2e2", stroke=POS, min_w=160)
    frags.append(b_hib)

    # 5. BLACKOUT_RECOVERY
    b_rec, _, _ = textbox(300, 340, "STATE_RECOVERY\nV_bat > 3.45 В (SoC > 25%)\nСонячний заряд > 15 хв\nГістерезисний фільтр",
                          size=11, pad=10, fill="#eff6ff", stroke=NEG, min_w=180)
    frags.append(b_rec)

    # Переходи між станами
    # Normal -> Eco
    frags.append(arrow(240, 115, 390, 115, color="#ca8a04", sw=1.8))
    frags.append(text(315, 105, "SoC ≤ 70%", size=10, color="#854d0e"))

    # Eco -> Normal
    frags.append(arrow(390, 145, 240, 145, color=FIELD, sw=1.8))
    frags.append(text(315, 160, "SoC > 75%", size=10, color=FIELD))

    # Eco -> Survival
    frags.append(arrow(550, 115, 700, 115, color="#ea580c", sw=1.8))
    frags.append(text(625, 105, "SoC ≤ 30%", size=10, color="#9a3412"))

    # Survival -> Eco
    frags.append(arrow(700, 145, 550, 145, color="#ca8a04", sw=1.8))
    frags.append(text(625, 160, "SoC > 35%", size=10, color="#854d0e"))

    # Survival -> Hibernate
    frags.append(arrow(780, 185, 780, 285, color=POS, sw=2))
    frags.append(text(840, 235, "SoC ≤ 10%", size=10, bold=True, color=POS))

    # Hibernate -> Recovery
    frags.append(arrow(690, 340, 400, 340, color=NEG, sw=2))
    frags.append(text(545, 328, "V_bat > 3.40 В + Сонце є", size=10, bold=True, color=NEG))

    # Recovery -> Eco
    frags.append(arrow(340, 285, 430, 185, color=FIELD, sw=2))
    frags.append(text(340, 230, "Стабільний заряд 15 хв\n(SoC > 25%)", size=10, bold=True, color=FIELD))

    # Пастка перезавантаження (пояснювальний блок)
    frags.append(rect(40, 405, 860, 40, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(470, 428, "Захист від Reboot Loop: при низькому заряді старт передавача просаджує напругу → Reset. "
                                "Recovery чекає повного накопичення заряду!", size=10, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "blackout-recovery-fsm.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_winter_insolation()
    fig_lithium_plating()
    fig_adaptive_profile()
    fig_blackout_recovery_fsm()
    print("All figures generated successfully.")
