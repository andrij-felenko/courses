# -*- coding: utf-8 -*-
"""Генератор векторних діаграм (SVG) для теми:
«Захват: типи, сила, утримання»
"""
import sys, os

# Шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_mechanisms_taxonomy():
    """Фігура 1: Класифікація та кінематика захватних пристроїв маніпуляторів."""
    w, h = 900, 480
    frags = []

    # Загальний фон
    frags.append(rect(15, 15, 870, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(450, 42, "Основні типи захватних механізмів маніпуляторів БПЛА", size=16, bold=True, color="#0f172a"))

    # ── Блок 1: Двопальцевий паралельний ──
    frags.append(rect(30, 65, 200, 385, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(130, 90, "Паралельний двопальцевий", size=12, bold=True, color="#1e40af"))
    frags.append(text(130, 106, "Parallel Jaw Gripper", size=10, color="#3b82f6"))

    # Схема механізму
    frags.append(rect(60, 125, 140, 30, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(130, 144, "Сервопривід + Гвинт", size=10, bold=True, color="#1e3a8a"))
    # Губки
    frags.append(rect(65, 165, 25, 60, fill="#3b82f6", stroke="#1d4ed8", sw=1.5, rx=3))
    frags.append(rect(170, 165, 25, 60, fill="#3b82f6", stroke="#1d4ed8", sw=1.5, rx=3))
    # Вантаж
    frags.append(rect(100, 175, 60, 40, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=2))
    frags.append(text(130, 199, "Вантаж", size=10, color="#334155"))
    # Стрілки зусилля
    frags.append(arrow(60, 195, 88, 195, color="#dc2626", sw=2))
    frags.append(arrow(200, 195, 172, 195, color="#dc2626", sw=2))
    frags.append(text(130, 242, "Сили притискання F_grip", size=9, bold=True, color="#dc2626"))

    # Опис властивостей
    frags.append(rect(40, 260, 180, 175, fill="#ffffff", stroke="#bfdbfe", sw=1, rx=4))
    frags.append(text(130, 280, "ХАРАКТЕРИСТИКИ:", size=10, bold=True, color="#1e40af"))
    frags.append(text(130, 300, "• Жорсткі паралельні губки", size=9, color="#334155"))
    frags.append(text(130, 318, "• Сталість осі центрування", size=9, color="#334155"))
    frags.append(text(130, 336, "• Рейковий / гвинтовий рух", size=9, color="#334155"))
    frags.append(text(130, 354, "• Висока точність позиції", size=9, color="#059669"))
    frags.append(text(130, 372, "• Обмежений для складних тіл", size=9, color="#dc2626"))
    frags.append(text(130, 390, "• Фрикційне замикання", size=9, color="#475569"))
    frags.append(text(130, 412, "ККД зусилля: 70–85%", size=9, bold=True, color="#1e40af"))

    # ── Блок 2: Багатопальцевий адаптивний ──
    frags.append(rect(245, 65, 200, 385, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(345, 90, "Адаптивний неповний", size=12, bold=True, color="#166534"))
    frags.append(text(345, 106, "Underactuated Multi-finger", size=10, color="#22c55e"))

    # Схема адаптивного обхвату
    frags.append(rect(275, 125, 140, 30, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(345, 144, "Тросовий / Whippletree", size=10, bold=True, color="#14532d"))
    # Шарнірні фаланги
    frags.append('<path d="M 285,165 L 275,200 L 305,225" fill="none" stroke="#16a34a" stroke-width="4"/>')
    frags.append('<path d="M 405,165 L 415,200 L 385,225" fill="none" stroke="#16a34a" stroke-width="4"/>')
    # Круглий вантаж (обтиснутий)
    frags.append(circle(345, 195, 24, fill="#e2e8f0", stroke="#64748b", sw=1.5))
    frags.append(text(345, 199, "Вантаж", size=10, color="#334155"))
    frags.append(text(345, 242, "Облягання форми (Enveloping)", size=9, bold=True, color="#166534"))

    # Опис властивостей
    frags.append(rect(255, 260, 180, 175, fill="#ffffff", stroke="#bbf7d0", sw=1, rx=4))
    frags.append(text(345, 280, "ХАРАКТЕРИСТИКИ:", size=10, bold=True, color="#166534"))
    frags.append(text(345, 300, "• 1 мотор на 3–4 фаланги", size=9, color="#334155"))
    frags.append(text(345, 318, "• Пасивна адаптація контуру", size=9, color="#334155"))
    frags.append(text(345, 336, "• Еластомерні шарніри TPU", size=9, color="#334155"))
    frags.append(text(345, 354, "• Захист крихких предметів", size=9, color="#059669"))
    frags.append(text(345, 372, "• Формове обтискання", size=9, color="#059669"))
    frags.append(text(345, 390, "• Менша жорсткість утримання", size=9, color="#dc2626"))
    frags.append(text(345, 412, "Маса конструкції: мала", size=9, bold=True, color="#166534"))

    # ── Блок 3: Вакуумні присоски ──
    frags.append(rect(460, 65, 200, 385, fill="#fffbeb", stroke="#fde68a", sw=1.5, rx=6))
    frags.append(text(560, 90, "Вакуумний сильфонний", size=12, bold=True, color="#92400e"))
    frags.append(text(560, 106, "Vacuum Suction Cup", size=10, color="#d97706"))

    # Схема присоски
    frags.append(rect(490, 125, 140, 30, fill="#ffffff", stroke="#fcd34d", sw=1.2, rx=4))
    frags.append(text(560, 144, "Ежектор / DC помпа", size=10, bold=True, color="#78350f"))
    # Сильфон (хвилястий)
    frags.append('<path d="M 545,155 L 535,165 L 555,175 L 530,190 L 590,190 L 565,175 L 585,165 L 575,155 Z" fill="#fbbf24" stroke="#d97706" stroke-width="1.5"/>')
    # Листовий вантаж знизу
    frags.append(rect(505, 192, 110, 14, fill="#cbd5e1", stroke="#64748b", sw=1.5, rx=1))
    frags.append(text(560, 203, "Листова поверхня", size=9, color="#334155"))
    frags.append(arrow(560, 235, 560, 212, color="#b45309", sw=2))
    frags.append(text(560, 242, "Сила відриву F_vac = ΔP·S", size=9, bold=True, color="#b45309"))

    # Опис властивостей
    frags.append(rect(470, 260, 180, 175, fill="#ffffff", stroke="#fef3c7", sw=1, rx=4))
    frags.append(text(560, 280, "ХАРАКТЕРИСТИКИ:", size=10, bold=True, color="#92400e"))
    frags.append(text(560, 300, "• Односторонній підхід", size=9, color="#334155"))
    frags.append(text(560, 318, "• Робота з гладкими листами", size=9, color="#334155"))
    frags.append(text(560, 336, "• Сильфон компенсує кут ±15°", size=9, color="#059669"))
    frags.append(text(560, 354, "• Миттєве схоплювання (<50 мс)", size=9, color="#059669"))
    frags.append(text(560, 372, "• Чутливий до пористості/пилу", size=9, color="#dc2626"))
    frags.append(text(560, 390, "• Потребує витрати повітря", size=9, color="#dc2626"))
    frags.append(text(560, 412, "Тиск: ΔP = −60...−85 кПа", size=9, bold=True, color="#92400e"))

    # ── Блок 4: Електропостійний магнітний ──
    frags.append(rect(675, 65, 195, 385, fill="#fdf2f8", stroke="#fbcfe8", sw=1.5, rx=6))
    frags.append(text(772, 90, "Електропостійний магніт", size=12, bold=True, color="#9d174d"))
    frags.append(text(772, 106, "Electropermanent (EPM)", size=10, color="#db2777"))

    # Схема магніту
    frags.append(rect(705, 125, 135, 30, fill="#ffffff", stroke="#f472b6", sw=1.2, rx=4))
    frags.append(text(772, 144, "Котушка імпульсу (1 мс)", size=10, bold=True, color="#831843"))
    # Сердечник Alnico + NdFeB
    frags.append(rect(720, 160, 45, 32, fill="#ef4444", stroke="#991b1b", sw=1.2, rx=2))
    frags.append(text(742, 180, "N", size=11, bold=True, color="#ffffff"))
    frags.append(rect(775, 160, 45, 32, fill="#3b82f6", stroke="#1d4ed8", sw=1.2, rx=2))
    frags.append(text(797, 180, "S", size=11, bold=True, color="#ffffff"))
    # Феромагнітний вантаж
    frags.append(rect(715, 196, 115, 14, fill="#475569", stroke="#1e293b", sw=1.2, rx=1))
    frags.append(text(772, 207, "Сталевий вантаж", size=9, color="#f8fafc"))
    frags.append(text(772, 242, "B_sat ≥ 1.5 Тл (Fe/Сталь)", size=9, bold=True, color="#9d174d"))

    # Опис властивостей
    frags.append(rect(683, 260, 178, 175, fill="#ffffff", stroke="#fce7f3", sw=1, rx=4))
    frags.append(text(772, 280, "ХАРАКТЕРИСТИКИ:", size=10, bold=True, color="#9d174d"))
    frags.append(text(772, 300, "• Нульове споживання струму", size=9, bold=True, color="#059669"))
    frags.append(text(772, 318, "• Імпульс лише на ON / OFF", size=9, color="#334155"))
    frags.append(text(772, 336, "• Величезна сила (до 500 Н)", size=9, color="#059669"))
    frags.append(text(772, 354, "• Немає рухомих деталей", size=9, color="#334155"))
    frags.append(text(772, 372, "• Тільки феромагнітні цілі", size=9, color="#dc2626"))
    frags.append(text(772, 390, "• Чутливий до повітряного зазору", size=9, color="#dc2626"))
    frags.append(text(772, 412, "Струм утримання: 0.0 А", size=9, bold=True, color="#059669"))

    render(os.path.join(OUT_DIR, "gripper-mechanisms-taxonomy.svg"), w, h, *frags)


def fig_form_vs_friction():
    """Фігура 2: Порівняння принципів фіксації: Friction Closure vs Form Closure."""
    w, h = 900, 460
    frags = []

    # Фон
    frags.append(rect(15, 15, 870, 430, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(450, 40, "Механіка утримання: фрикційне замикання проти геометричного", size=15, bold=True, color="#0f172a"))

    # ── Ліва панель: Friction Closure ──
    frags.append(rect(30, 60, 405, 370, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(232, 85, "Фрикційне замикання (Friction Closure)", size=13, bold=True, color="#1e40af"))

    # Графічна схема
    # Губка ліва і права
    frags.append(rect(80, 120, 20, 90, fill="#93c5fd", stroke="#1d4ed8", sw=1.5, rx=2))
    frags.append(rect(365, 120, 20, 90, fill="#93c5fd", stroke="#1d4ed8", sw=1.5, rx=2))
    # Об'єкт
    frags.append(rect(150, 130, 165, 70, fill="#ffffff", stroke="#475569", sw=1.5, rx=3))
    frags.append(text(232, 168, "Об'єкт контакту", size=11, bold=True, color="#334155"))

    # Сили стискання F_N
    frags.append(arrow(50, 165, 145, 165, color="#dc2626", sw=2.5))
    frags.append(text(75, 153, "F_N", size=11, bold=True, color="#dc2626"))
    frags.append(arrow(415, 165, 320, 165, color="#dc2626", sw=2.5))
    frags.append(text(390, 153, "F_N", size=11, bold=True, color="#dc2626"))

    # Сили тертя F_f
    frags.append(arrow(150, 185, 150, 135, color="#059669", sw=2))
    frags.append(text(130, 140, "F_f", size=10, bold=True, color="#059669"))
    frags.append(arrow(315, 185, 315, 135, color="#059669", sw=2))
    frags.append(text(335, 140, "F_f", size=10, bold=True, color="#059669"))

    # Зовнішнє навантаження вниз (гравітація + інерція)
    frags.append(arrow(232, 175, 232, 230, color="#d97706", sw=2.5))
    frags.append(text(250, 222, "F_ext", size=11, bold=True, color="#d97706"))

    # Конус тертя (Friction Cone)
    frags.append('<polygon points="150,165 110,135 110,195" fill="#fef08a" opacity="0.6" stroke="#ca8a04" stroke-width="1"/>')
    frags.append(text(125, 208, "Конус тертя α", size=9, color="#854d0e"))

    # Опис умов
    frags.append(rect(45, 245, 375, 170, fill="#ffffff", stroke="#bfdbfe", sw=1, rx=4))
    frags.append(text(232, 265, "ФІЗИЧНИЙ МЕХАНІЗМ І ОБМЕЖЕННЯ:", size=10, bold=True, color="#1e40af"))
    frags.append(text(232, 285, "• Утримання за рахунок сили тертя: F_f = μ · F_N", size=10, bold=True, color="#1e40af"))
    frags.append(text(232, 303, "• Умова рівноваги зсуву: ∑ F_f ≥ k_safe · F_ext", size=9, color="#334155"))
    frags.append(text(232, 321, "• Вектор контактної сили лежить всередині конуса тертя", size=9, color="#334155"))
    frags.append(text(232, 339, "• Вимагає потужного постійного стискання сервоприводу", size=9, color="#dc2626"))
    frags.append(text(232, 357, "• Ризик прослизання при масляній плівці або вібраціях", size=9, color="#dc2626"))
    frags.append(text(232, 375, "• Необхідний запас безпеки k_safe ≥ 2.0...3.0", size=9, bold=True, color="#166534"))
    frags.append(text(232, 398, "Чутливість до коефіцієнта тертя μ: КРИТИЧНА", size=9, bold=True, color="#b91c1c"))

    # ── Права панель: Form Closure ──
    frags.append(rect(465, 60, 405, 370, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(667, 85, "Геометричне замикання (Form Closure)", size=13, bold=True, color="#14532d"))

    # Графічна схема фігурних губок
    # Профільні губки з виступом (замком)
    frags.append('<path d="M 515,115 L 540,115 L 540,140 L 555,140 L 555,190 L 540,190 L 540,215 L 515,215 Z" fill="#86efac" stroke="#16a34a" stroke-width="1.5"/>')
    frags.append('<path d="M 820,115 L 795,115 L 795,140 L 780,140 L 780,190 L 795,190 L 795,215 L 820,215 Z" fill="#86efac" stroke="#16a34a" stroke-width="1.5"/>')
    # Т-подібний вантаж, що ідеально замкнений
    frags.append('<path d="M 560,145 L 775,145 L 775,185 L 560,185 Z" fill="#ffffff" stroke="#475569" stroke-width="1.5"/>')
    frags.append(text(667, 168, "Замкнений об'єкт (T-профіль)", size=11, bold=True, color="#334155"))

    # Нормальні реакції опори на виступах
    frags.append(arrow(548, 120, 548, 142, color="#16a34a", sw=2))
    frags.append(text(532, 133, "N_1", size=10, bold=True, color="#16a34a"))
    frags.append(arrow(787, 120, 787, 142, color="#16a34a", sw=2))
    frags.append(text(802, 133, "N_2", size=10, bold=True, color="#16a34a"))
    frags.append(arrow(548, 210, 548, 188, color="#16a34a", sw=2))
    frags.append(text(532, 203, "N_3", size=10, bold=True, color="#16a34a"))
    frags.append(arrow(787, 210, 787, 188, color="#16a34a", sw=2))
    frags.append(text(802, 203, "N_4", size=10, bold=True, color="#16a34a"))

    # Зовнішнє навантаження
    frags.append(arrow(667, 175, 667, 230, color="#d97706", sw=2.5))
    frags.append(text(685, 222, "F_ext", size=11, bold=True, color="#d97706"))

    # Опис умов
    frags.append(rect(480, 245, 375, 170, fill="#ffffff", stroke="#bbf7d0", sw=1, rx=4))
    frags.append(text(667, 265, "ФІЗИЧНИЙ МЕХАНІЗМ І ПЕРЕВАГИ:", size=10, bold=True, color="#14532d"))
    frags.append(text(667, 285, "• Повне обмеження ступенів вільності (6-DoF блокування)", size=10, bold=True, color="#14532d"))
    frags.append(text(667, 303, "• Утримання діє навіть при абсолютно слизькій поверхні (μ = 0)", size=9, color="#059669"))
    frags.append(text(667, 321, "• Зовнішні сили сприймаються жорсткими нормальними реакціями N_i", size=9, color="#334155"))
    frags.append(text(667, 339, "• Сила стискання потрібна мінімальна (лише для вибору зазору)", size=9, color="#059669"))
    frags.append(text(667, 357, "• Абсолютна стійкість до ударів, вібрацій та бічних ривків", size=9, color="#059669"))
    frags.append(text(667, 375, "• Вимагає точного збігу геометрії губок та пазів вантажу", size=9, color="#475569"))
    frags.append(text(667, 398, "Енергоспоживання приводу: МІНІМАЛЬНЕ", size=9, bold=True, color="#166534"))

    render(os.path.join(OUT_DIR, "form-vs-friction-closure.svg"), w, h, *frags)


def fig_dynamic_load():
    """Фігура 3: Динамічний векторний баланс сил і моментів під час маневрів БПЛА."""
    w, h = 900, 480
    frags = []

    # Фон
    frags.append(rect(15, 15, 870, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(450, 40, "Динамічні навантаження на захват при маневруванні БПЛА", size=15, bold=True, color="#0f172a"))

    # ── Ліва частина: Векторна діаграма сил ──
    frags.append(rect(30, 60, 420, 390, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(240, 85, "Просторовий баланс сил на вантажі", size=13, bold=True, color="#0f172a"))

    # Губки захвату зверху
    frags.append(rect(160, 110, 30, 70, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    frags.append(rect(290, 110, 30, 70, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    frags.append(rect(190, 95, 100, 20, fill="#64748b", stroke="#334155", sw=1.5, rx=2))
    frags.append(text(240, 109, "Основа захвату", size=9, color="#ffffff"))

    # Вантаж (прямокутник із центром мас)
    frags.append(rect(190, 130, 100, 110, fill="#e2e8f0", stroke="#334155", sw=1.8, rx=4))
    frags.append(circle(240, 185, 6, fill="#ef4444", stroke="#991b1b", sw=1.5))
    frags.append(text(240, 205, "Центр мас m", size=10, bold=True, color="#991b1b"))

    # Нормальні сили стискання
    frags.append(arrow(140, 150, 188, 150, color="#2563eb", sw=2.5))
    frags.append(text(155, 142, "F_grip", size=10, bold=True, color="#2563eb"))
    frags.append(arrow(340, 150, 292, 150, color="#2563eb", sw=2.5))
    frags.append(text(325, 142, "F_grip", size=10, bold=True, color="#2563eb"))

    # Сили тертя
    frags.append(arrow(190, 170, 190, 130, color="#059669", sw=2))
    frags.append(text(175, 138, "F_f1", size=9, bold=True, color="#059669"))
    frags.append(arrow(290, 170, 290, 130, color="#059669", sw=2))
    frags.append(text(305, 138, "F_f2", size=9, bold=True, color="#059669"))

    # Вектор ваги: m·g
    frags.append(arrow(240, 185, 240, 255, color="#dc2626", sw=2))
    frags.append(text(250, 248, "m·g", size=10, bold=True, color="#dc2626"))

    # Вектор лінійного прискорення: m·a_trans (наприклад, поворот / ривок)
    frags.append(arrow(240, 185, 160, 220, color="#ea580c", sw=2))
    frags.append(text(180, 230, "m·a_trans", size=10, bold=True, color="#ea580c"))

    # Сумарна динамічна сила F_dyn
    frags.append(arrow(240, 185, 175, 275, color="#b91c1c", sw=2.5))
    frags.append(text(195, 285, "F_dyn = m(g + a)", size=10, bold=True, color="#b91c1c"))

    # Обертальний момент (кручення вантажу)
    frags.append('<path d="M 270,165 A 30 30 0 0 1 270,205" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#arrow)"/>')
    frags.append(text(305, 190, "M_iner = I·ε", size=9, bold=True, color="#7c3aed"))

    # Формульний блок ліворуч
    frags.append(rect(45, 305, 390, 130, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(240, 325, "УМОВА НЕПРОСЛИЗАННЯ ВАНТАЖУ:", size=10, bold=True, color="#0f172a"))
    frags.append(text(240, 345, "F_grip ≥ (k_safe · m · √( (g + a_z)² + a_xy² )) / (n_fingers · μ)", size=9, bold=True, color="#1e40af"))
    frags.append(text(240, 365, "M_friction = 2 · μ · F_grip · r_contact ≥ k_safe · M_iner", size=9, bold=True, color="#7c3aed"))
    frags.append(text(240, 385, "• a_trans: маневрені перевантаження дрона (до 2–4 g)", size=9, color="#475569"))
    frags.append(text(240, 403, "• μ: коефіцієнт тертя контакту (гума/метал: 0.5–0.8)", size=9, color="#475569"))
    frags.append(text(240, 421, "• k_safe: динамічний коефіцієнт запасу (2.0–3.0)", size=9, color="#059669"))

    # ── Права частина: Таблиця впливу матеріалів і коефіцієнтів ──
    frags.append(rect(465, 60, 405, 390, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(667, 85, "Вплив пари тертя та динамічного запасу", size=13, bold=True, color="#0f172a"))

    # Таблиця коефіцієнтів тертя μ
    frags.append(rect(480, 105, 375, 140, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))
    frags.append(text(667, 123, "ТИПОВІ КОЕФІЦІЄНТИ ТЕРТЯ СПОКОЮ (μ):", size=10, bold=True, color="#1e293b"))

    frags.append(text(500, 145, "Пара контакту (губка — вантаж)", size=9, bold=True, color="#475569", anchor="start"))
    frags.append(text(835, 145, "μ (сухий)", size=9, bold=True, color="#475569", anchor="end"))
    frags.append(line(495, 152, 840, 152, color="#cbd5e1", sw=1))

    frags.append(text(500, 168, "• Сталь по сталі (гладка)", size=9, color="#334155", anchor="start"))
    frags.append(text(835, 168, "0.15 – 0.20", size=9, bold=True, color="#dc2626", anchor="end"))

    frags.append(text(500, 186, "• Алюміній по алюмінію", size=9, color="#334155", anchor="start"))
    frags.append(text(835, 186, "0.25 – 0.35", size=9, color="#d97706", anchor="end"))

    frags.append(text(500, 204, "• Поліуретан (TPU 95A) по металу", size=9, color="#334155", anchor="start"))
    frags.append(text(835, 204, "0.45 – 0.60", size=9, bold=True, color="#059669", anchor="end"))

    frags.append(text(500, 222, "• Силіконова гума (40A) по пластику", size=9, color="#334155", anchor="start"))
    frags.append(text(835, 222, "0.70 – 0.90", size=9, bold=True, color="#166534", anchor="end"))

    frags.append(text(500, 240, "• Насічка / мікрозубці (Form Closure)", size=9, color="#334155", anchor="start"))
    frags.append(text(835, 240, "Формовий замок", size=9, bold=True, color="#2563eb", anchor="end"))

    # Блок запасу безпеки
    frags.append(rect(480, 255, 375, 180, fill="#fef2f2", stroke="#fca5a5", sw=1, rx=4))
    frags.append(text(667, 275, "ВИМОГИ ДО КОЕФІЦІЄНТА ЗАПАСУ k_safe:", size=10, bold=True, color="#991b1b"))

    frags.append(text(500, 298, "k_safe = 1.5 — Лабораторний стенд (плавний рух)", size=9, color="#334155", anchor="start"))
    frags.append(text(500, 318, "k_safe = 2.0 — Стандартний дрон при вітрі до 5 м/с", size=9, color="#334155", anchor="start"))
    frags.append(text(500, 338, "k_safe = 3.0 — Агресивний пілотаж, ривки до 30 м/с²", size=9, bold=True, color="#b91c1c", anchor="start"))
    frags.append(text(500, 358, "k_safe = 4.0+ — Вологі/забруднені поверхні, лід", size=9, color="#7f1d1d", anchor="start"))

    frags.append(line(495, 375, 840, 375, color="#fca5a5", sw=1))
    frags.append(text(667, 395, "ВИСНОВОК: Гумові накладки знижують", size=9, bold=True, color="#166534"))
    frags.append(text(667, 412, "необхідне зусилля мотора у 3–4 рази!", size=10, bold=True, color="#166534"))

    render(os.path.join(OUT_DIR, "dynamic-load-and-forces.svg"), w, h, *frags)


def fig_vacuum_circuit():
    """Фігура 4: Пневматична та електрична схема вакуумної системи маніпулятора."""
    w, h = 900, 470
    frags = []

    # Фон
    frags.append(rect(15, 15, 870, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(450, 40, "Пневмоелектрична схема та фізика ежекторного вакуумного захвату", size=15, bold=True, color="#0f172a"))

    # ── Панель 1: Принцип ежектора Вентурі ──
    frags.append(rect(30, 60, 410, 380, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(235, 85, "Генерація вакууму: Ежектор Вентурі", size=13, bold=True, color="#0f172a"))

    # Схема сопла Вентурі
    # Вхід стисненого повітря
    frags.append(rect(50, 115, 75, 35, fill="#dbeafe", stroke="#3b82f6", sw=1.2, rx=2))
    frags.append(text(87, 136, "P_in = 4..6 бар", size=9, bold=True, color="#1e40af"))
    frags.append(arrow(125, 132, 160, 132, color="#2563eb", sw=2))

    # Конвергентно-дивергентне сопло
    frags.append('<path d="M 160,115 L 210,128 L 260,110 L 260,155 L 210,137 L 160,150 Z" fill="#93c5fd" stroke="#1d4ed8" stroke-width="1.5"/>')
    frags.append(text(210, 120, "Критичне звуження", size=9, color="#1e3a8a"))

    # Вихід відпрацьованого повітря (глушник)
    frags.append(rect(260, 115, 60, 35, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=2))
    frags.append(text(290, 136, "Вихлоп", size=9, color="#475569"))
    frags.append(arrow(320, 132, 350, 132, color="#64748b", sw=1.5))

    # Вакуумний порт (перпендикулярне відведення)
    frags.append(rect(195, 145, 30, 55, fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=2))
    frags.append(arrow(210, 220, 210, 180, color="#b45309", sw=2))
    frags.append(text(210, 235, "Вакуумний порт P_vac", size=9, bold=True, color="#b45309"))

    # Графік закону Бернуллі
    frags.append(rect(45, 255, 380, 170, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=4))
    frags.append(text(235, 275, "ТЕРМОДИНАМІЧНИЙ ПРИНЦИП БЕРНУЛЛІ:", size=10, bold=True, color="#0f172a"))
    frags.append(text(235, 295, "P_static + 0.5·ρ·v² = const  [рівняння нестисливого струменя]", size=9, bold=True, color="#1e40af"))
    frags.append(text(235, 315, "1. Стиснене повітря розганяється у звуженні до v > 300 м/с", size=9, color="#334155"))
    frags.append(text(235, 333, "2. Динамічний напір 0.5·ρ·v² різко зростає", size=9, color="#334155"))
    frags.append(text(235, 351, "3. Статичний тиск P_static падає нижче атмосферного:", size=9, color="#334155"))
    frags.append(text(235, 369, "   P_vac = P_atm − ΔP = 101.3 − 80 = 21.3 кПа (абсолютний)", size=9, bold=True, color="#b45309"))
    frags.append(text(235, 389, "4. Повітря з присоски захоплюється швидкісним струменем", size=9, color="#059669"))
    frags.append(text(235, 412, "Час утворення вакууму: 15–40 мс", size=9, bold=True, color="#059669"))

    # ── Панель 2: Бортова схема підключення та керування ──
    frags.append(rect(460, 60, 410, 380, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(665, 85, "Бортова пневматична лінія з клапанами", size=13, bold=True, color="#0f172a"))

    # Блоки схеми
    # Мікрокомпресор / Балон
    frags.append(rect(475, 110, 85, 45, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=3))
    frags.append(text(517, 128, "Джерело P_in", size=9, bold=True, color="#1e40af"))
    frags.append(text(517, 144, "Помпа / CO₂", size=9, color="#64748b"))

    # Електроклапан подачі (Valve 1)
    frags.append(rect(590, 110, 75, 45, fill="#ffffff", stroke="#64748b", sw=1.2, rx=3))
    frags.append(text(627, 128, "Клапан V1", size=9, bold=True, color="#334155"))
    frags.append(text(627, 144, "Подача вакууму", size=9, color="#059669"))
    frags.append(arrow(560, 132, 590, 132, color="#3b82f6", sw=1.5))

    # Ежектор
    frags.append(rect(695, 110, 65, 45, fill="#fef08a", stroke="#ca8a04", sw=1.2, rx=3))
    frags.append(text(727, 128, "Ежектор", size=9, bold=True, color="#854d0e"))
    frags.append(text(727, 144, "Вентурі", size=9, color="#854d0e"))
    frags.append(arrow(665, 132, 695, 132, color="#3b82f6", sw=1.5))

    # Лінія до присоски
    frags.append(line(727, 155, 727, 210, color="#b45309", sw=2))

    # Датчик тиску (Pressure Sensor)
    frags.append(rect(775, 175, 80, 40, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=3))
    frags.append(text(815, 192, "Датчик тиску", size=9, bold=True, color="#166534"))
    frags.append(text(815, 206, "I2C / Аналог", size=9, color="#166534"))
    frags.append(line(727, 195, 775, 195, color="#22c55e", sw=1.5, dash="3,2"))

    # Клапан продувки / скидання (Blow-off valve V2)
    frags.append(rect(590, 175, 75, 40, fill="#fff1f2", stroke="#f43f5e", sw=1.2, rx=3))
    frags.append(text(627, 192, "Клапан V2", size=9, bold=True, color="#9f1239"))
    frags.append(text(627, 206, "Скидання (Blow)", size=9, color="#9f1239"))
    frags.append(line(665, 195, 727, 195, color="#f43f5e", sw=1.5))

    # Присоска з вантажем
    frags.append('<path d="M 710,210 L 695,235 L 760,235 L 745,210 Z" fill="#fbbf24" stroke="#d97706" stroke-width="1.5"/>')
    frags.append(rect(670, 237, 115, 12, fill="#94a3b8", stroke="#475569", sw=1.2, rx=1))
    frags.append(text(727, 246, "Вантаж", size=9, color="#ffffff"))

    # Схема станів контролера
    frags.append(rect(475, 260, 380, 165, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(665, 280, "АЛГОРИТМ КЕРУВАННЯ ВАКУУМОМ:", size=10, bold=True, color="#0f172a"))
    frags.append(text(490, 302, "1. ЗАХВАТ: Відкрити V1 → потік через ежектор → розрідження", size=9, color="#166534", anchor="start"))
    frags.append(text(490, 320, "2. ВАЛІДАЦІЯ: Датчик фіксує P < −50 кПа → статус GRIPPED", size=9, bold=True, color="#059669", anchor="start"))
    frags.append(text(490, 338, "3. АВАРІЯ ВИТОКУ: P > −30 кПа → тривога SLIP_ALARM", size=9, bold=True, color="#dc2626", anchor="start"))
    frags.append(text(490, 356, "4. СКИНУТИ: Закрити V1 + імпульс V2 (20 мс) → миттєвий відрив", size=9, color="#1e40af", anchor="start"))
    frags.append(text(490, 374, "5. Розрахунок сили: F = ΔP · S_cup = 75 кПа · 0.002 м² = 150 Н", size=9, color="#475569", anchor="start"))
    frags.append(text(665, 410, "Зсувне навантаження: F_shear = μ_гума · F_vac ≈ 0.6 · 150 = 90 Н", size=9, bold=True, color="#1e40af"))

    render(os.path.join(OUT_DIR, "vacuum-ejector-circuit.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_mechanisms_taxonomy()
    fig_form_vs_friction()
    fig_dynamic_load()
    fig_vacuum_circuit()
    print("All 4 figures generated successfully in img/")
