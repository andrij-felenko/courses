# -*- coding: utf-8 -*-
"""Генератор векторних діаграм (SVG) для теми:
«Компонування борту: розміщення, джгут, розв'язка»
"""
import sys, os

# Шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_spatial_zoning():
    """Фігура 1: Трирівневе просторове зонування борту БПЛА."""
    w, h = 900, 480
    frags = []

    # Загальний фон
    frags.append(rect(15, 15, 870, 450, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(450, 42, "Трирівневе просторове зонування безпілотного апарата", size=16, bold=True, color="#0f172a"))

    # ── Рівень 1 (Верхній / Щогли): Радіочастотна зона ──
    frags.append(rect(35, 60, 830, 110, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=6))
    frags.append(text(155, 82, "РАДІОЧАСТОТНА ЗОНА (RF Zone)", size=13, bold=True, color="#1e40af"))
    frags.append(text(155, 98, "Винос на щогли та законцівки", size=11, color="#3b82f6"))

    # Модуль GNSS
    frags.append(rect(290, 72, 160, 85, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(370, 92, "Модуль GNSS + Компас", size=12, bold=True, color="#1e3a8a"))
    frags.append(text(370, 110, "Піднятий на щоглі 12–20 см", size=10, color="#475569"))
    frags.append(text(370, 126, "Екран Ground Plane 50 мм", size=10, color="#64748b"))
    frags.append(text(370, 142, "Вихідний потік: CAN / UART", size=10, color="#2563eb"))

    # Приймач RC (ELRS / Crossfire)
    frags.append(rect(470, 72, 175, 85, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(557, 92, "Приймач RC (868 / 2400 МГц)", size=12, bold=True, color="#1e3a8a"))
    frags.append(text(557, 110, "Т-антена на передньому промені", size=10, color="#475569"))
    frags.append(text(557, 126, "Вертикальна поляризація", size=10, color="#64748b"))
    frags.append(text(557, 142, "Чутливість: −120 dBm", size=10, color="#059669"))

    # Передавач відео VTX
    frags.append(rect(665, 72, 185, 85, fill="#ffffff", stroke="#60a5fa", sw=1.2, rx=4))
    frags.append(text(757, 92, "Відеопередавач VTX (5.8 ГГц)", size=12, bold=True, color="#1e3a8a"))
    frags.append(text(757, 110, "Антена винесена назад / вниз", size=10, color="#475569"))
    frags.append(text(757, 126, "Випромінювання: +30 dBm (1 Вт)", size=10, color="#dc2626"))
    frags.append(text(757, 142, "RHCP кругова поляризація", size=10, color="#64748b"))

    # ── Рівень 2 (Центральний дек): Чутлива сенсорна зона ──
    frags.append(rect(35, 185, 830, 130, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(155, 208, "СЕНСОРНА ЗОНА (Sensor Zone)", size=13, bold=True, color="#166534"))
    frags.append(text(155, 224, "Центр мас та вібророзв'язка", size=11, color="#22c55e"))

    # Політний контролер
    frags.append(rect(290, 198, 260, 105, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(420, 218, "Політний контролер (FC / IMU)", size=12, bold=True, color="#14532d"))
    frags.append(text(420, 236, "• Силіконові демпфери (M3 ізолятори)", size=10, color="#334155"))
    frags.append(text(420, 252, "• IMU точно в центрі жорсткості рами", size=10, color="#334155"))
    frags.append(text(420, 268, "• Барометр під світлозахисним поролоном", size=10, color="#334155"))
    frags.append(text(420, 284, "• Окреме стабілізоване живлення BEC 5V", size=10, color="#059669"))

    # Бортовий комп'ютер Companion
    frags.append(rect(570, 198, 280, 105, fill="#ffffff", stroke="#4ade80", sw=1.2, rx=4))
    frags.append(text(710, 218, "Бортовий комп'ютер (Companion SBC)", size=12, bold=True, color="#14532d"))
    frags.append(text(710, 236, "• Екранований металевий кожух (EMI Shield)", size=10, color="#334155"))
    frags.append(text(710, 252, "• Зв'язок з FC через ізольований UART/CAN", size=10, color="#334155"))
    frags.append(text(710, 268, "• Віддалений від антени GNSS на ≥ 15 см", size=10, color="#dc2626"))
    frags.append(text(710, 284, "• Живлення від окремого DC-DC з фільтром", size=10, color="#059669"))

    # ── Рівень 3 (Нижній дек / Промені): Силова зона ──
    frags.append(rect(35, 330, 830, 120, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=6))
    frags.append(text(155, 355, "СИЛОВА ЗОНА (Power Zone)", size=13, bold=True, color="#991b1b"))
    frags.append(text(155, 371, "Струми 50–200 А, комутація", size=11, color="#ef4444"))

    # Батарея LiPo
    frags.append(rect(290, 342, 160, 95, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    frags.append(text(370, 362, "Акумулятор (LiPo 6S/12S)", size=12, bold=True, color="#7f1d1d"))
    frags.append(text(370, 380, "Головний масовий центр", size=10, color="#475569"))
    frags.append(text(370, 396, "Короткі силові дроти AWG 10", size=10, color="#dc2626"))
    frags.append(text(370, 412, "Конектор XT90-S (Anti-Spark)", size=10, color="#334155"))
    frags.append(text(370, 428, "Струми віддачі до 150–200 А", size=10, color="#7f1d1d"))

    # PDB та ESC
    frags.append(rect(470, 342, 175, 95, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    frags.append(text(557, 362, "Плата PDB / 4-in-1 ESC", size=12, bold=True, color="#7f1d1d"))
    frags.append(text(557, 380, "ШІМ-комутація 24–48 кГц", size=10, color="#475569"))
    frags.append(text(557, 396, "Low-ESR конденсатори 1000 мкФ", size=10, color="#059669"))
    frags.append(text(557, 412, "Товсті мідні полігони 3–4 oz", size=10, color="#334155"))
    frags.append(text(557, 428, "Інтенсивне поле dI/dt", size=10, color="#dc2626"))

    # Мотори BLDC
    frags.append(rect(665, 342, 185, 95, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    frags.append(text(757, 362, "Двигуни BLDC на променях", size=12, bold=True, color="#7f1d1d"))
    frags.append(text(757, 380, "Трифазні кабелі сплетені в джгут", size=10, color="#475569"))
    frags.append(text(757, 396, "Мінімізація площі магнітної петлі", size=10, color="#059669"))
    frags.append(text(757, 412, "Захист від кромки карбону", size=10, color="#dc2626"))
    frags.append(text(757, 428, "Вібраційне джерело 100–500 Гц", size=10, color="#334155"))

    render(os.path.join(OUT_DIR, "spatial-zoning-and-interference.svg"), w, h, *frags)


def fig_ground_loop():
    """Фігура 2: Утворення земляної петлі та правильна зіркова топологія заземлення."""
    w, h = 900, 460
    frags = []

    # Фон
    frags.append(rect(15, 15, 870, 430, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Ліва панель: Дефект (Земляна петля)
    frags.append(rect(30, 35, 405, 395, fill="#fff1f2", stroke="#fda4af", sw=1.5, rx=6))
    frags.append(text(232, 60, "ДЕФЕКТ: Земляна петля (Ground Loop)", size=14, bold=True, color="#9f1239"))

    # PDB / Батарея ліворуч
    frags.append(rect(50, 85, 100, 60, fill="#ffffff", stroke="#e11d48", sw=1.2, rx=4))
    frags.append(text(100, 110, "PDB / Живлення", size=11, bold=True, color="#881337"))
    frags.append(text(100, 130, "Шумна PGND", size=10, color="#e11d48"))

    # FC
    frags.append(rect(200, 85, 100, 60, fill="#ffffff", stroke="#e11d48", sw=1.2, rx=4))
    frags.append(text(250, 110, "FC (Політний)", size=11, bold=True, color="#881337"))
    frags.append(text(250, 130, "OSD / Відеовхід", size=10, color="#475569"))

    # VTX
    frags.append(rect(315, 205, 100, 60, fill="#ffffff", stroke="#e11d48", sw=1.2, rx=4))
    frags.append(text(365, 230, "VTX (Відео)", size=11, bold=True, color="#881337"))
    frags.append(text(365, 250, "Потужний RF", size=10, color="#475569"))

    # Камера
    frags.append(rect(50, 205, 100, 60, fill="#ffffff", stroke="#e11d48", sw=1.2, rx=4))
    frags.append(text(100, 230, "Камера", size=11, bold=True, color="#881337"))
    frags.append(text(100, 250, "Чутливий сенсор", size=10, color="#475569"))

    # Лінії живлення та замкнена петля
    # PDB -> FC GND
    frags.append(line(150, 120, 200, 120, color="#dc2626", sw=2))
    frags.append(text(175, 112, "GND 1", size=9, color="#dc2626", bold=True))

    # PDB -> VTX GND
    frags.append('<path d="M 100,145 L 100,180 L 365,180 L 365,205" fill="none" stroke="#dc2626" stroke-width="2"/>')
    frags.append(text(230, 172, "GND 2 (Силовий мінус VTX)", size=9, color="#dc2626", bold=True))

    # FC -> VTX Video GND
    frags.append(line(300, 120, 365, 120, color="#dc2626", sw=2))
    frags.append(line(365, 120, 365, 205, color="#dc2626", sw=2))
    frags.append(text(335, 112, "Video GND", size=9, color="#dc2626", bold=True))

    # Сигнальне коло камери
    frags.append(line(100, 205, 100, 145, color="#2563eb", sw=1.5, dash="3,2"))
    frags.append(line(150, 235, 200, 135, color="#2563eb", sw=1.5, dash="3,2"))

    # Замкнений контур виділено
    frags.append(rect(170, 275, 240, 135, fill="#ffffff", stroke="#e11d48", sw=1, rx=4))
    frags.append(text(290, 298, "НАСЛІДОК ПЕТЛІ:", size=11, bold=True, color="#9f1239"))
    frags.append(text(290, 318, "• Силовий зворотний струм ESC", size=10, color="#475569"))
    frags.append(text(290, 334, "  протікає по сигнальному Video GND", size=10, color="#dc2626"))
    frags.append(text(290, 350, "• Падіння напруги ΔV = I·R створює", size=10, color="#475569"))
    frags.append(text(290, 366, "  смуги на відео (Video Noise)", size=10, color="#dc2626"))
    frags.append(text(290, 382, "• Ризик збою SPI/I2C шин FC", size=10, color="#475569"))
    frags.append(text(290, 398, "  через стрибки потенціалу GND", size=10, color="#7f1d1d"))

    # Права панель: Рішення (Зірка)
    frags.append(rect(465, 35, 405, 395, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(667, 60, "РІШЕННЯ: Зіркова топологія (Star Ground)", size=14, bold=True, color="#14532d"))

    # Центральна точка зірки (Star Point)
    frags.append(circle(667, 210, 18, fill="#16a34a", stroke="#14532d", sw=2))
    frags.append(text(667, 214, "★", size=16, color="#ffffff", bold=True))
    frags.append(text(667, 242, "Головна точка зірки (PDB Ground)", size=10, bold=True, color="#166534"))

    # Модулі навколо зірки
    # ESC / Мотори
    frags.append(rect(485, 90, 95, 55, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(532, 115, "ESC / Мотори", size=11, bold=True, color="#14532d"))
    frags.append(text(532, 133, "Силова PGND", size=10, color="#dc2626"))

    # FC
    frags.append(rect(755, 90, 95, 55, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(802, 115, "FC (Логіка)", size=11, bold=True, color="#14532d"))
    frags.append(text(802, 133, "Чиста DGND", size=10, color="#059669"))

    # Камера
    frags.append(rect(485, 275, 95, 55, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(532, 300, "Камера", size=11, bold=True, color="#14532d"))
    frags.append(text(532, 318, "AGND від FC", size=10, color="#2563eb"))

    # VTX
    frags.append(rect(755, 275, 95, 55, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=4))
    frags.append(text(802, 300, "VTX (Відео)", size=11, bold=True, color="#14532d"))
    frags.append(text(802, 318, "Фільтроване", size=10, color="#059669"))

    # Зіркові промені
    # ESC -> Star
    frags.append(line(555, 145, 652, 200, color="#16a34a", sw=2.5))
    frags.append(text(585, 170, "Силовий зворот", size=9, color="#dc2626", bold=True))

    # FC -> Star
    frags.append(line(775, 145, 682, 200, color="#16a34a", sw=2))
    frags.append(text(745, 170, "Окремий BEC GND", size=9, color="#059669", bold=True))

    # Камера живиться ТІЛЬКИ від FC
    frags.append(line(580, 290, 755, 130, color="#2563eb", sw=1.5, dash="4,2"))
    frags.append(text(670, 160, "Відео + AGND (без петлі)", size=9, color="#2563eb", bold=True))

    # VTX -> Star
    frags.append(line(775, 275, 682, 220, color="#16a34a", sw=2))

    # Переваги
    frags.append(rect(585, 340, 270, 75, fill="#ffffff", stroke="#16a34a", sw=1, rx=4))
    frags.append(text(720, 360, "ПЕРЕВАГИ ТОПОЛОГІЇ ЗІРКИ:", size=11, bold=True, color="#14532d"))
    frags.append(text(720, 378, "• Струми моторів не зачіпають аналог", size=10, color="#334155"))
    frags.append(text(720, 394, "• Стабільний потенціал сенсорів і OSD", size=10, color="#334155"))
    frags.append(text(720, 408, "• Відсутність замкнених контурів завад", size=10, color="#059669"))

    render(os.path.join(OUT_DIR, "ground-loop-and-star-topology.svg"), w, h, *frags)


def fig_mass_distribution():
    """Фігура 3: Оптимізація центру мас (CG) та тензора інерції (I_xx, I_yy, I_zz)."""
    w, h = 900, 450
    frags = []

    # Фон
    frags.append(rect(15, 15, 870, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(450, 40, "Розподіл мас: централізація проти рознесеного компонування", size=15, bold=True, color="#0f172a"))

    # Панель 1: Централізована маса (Концентрована)
    frags.append(rect(30, 60, 405, 360, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(232, 85, "Концентрована маса (Оптимум)", size=14, bold=True, color="#14532d"))

    # Схема дрона (вид зверху)
    # Промені
    frags.append(line(130, 160, 330, 240, color="#64748b", sw=3))
    frags.append(line(130, 240, 330, 160, color="#64748b", sw=3))

    # Мотори на краях
    for mx, my in [(130, 160), (330, 160), (130, 240), (330, 240)]:
        frags.append(circle(mx, my, 12, fill="#e2e8f0", stroke="#475569", sw=1.5))

    # Центральне ядро маси (Батарея + Стек в центрі)
    frags.append(rect(195, 170, 75, 60, fill="#22c55e", stroke="#15803d", sw=2, rx=4))
    frags.append(text(232, 195, "Батарея + FC", size=11, bold=True, color="#ffffff"))
    frags.append(text(232, 215, "r ≈ 0 мм", size=10, color="#ffffff"))

    # Центр мас CG
    frags.append(circle(232, 200, 5, fill="#dc2626", stroke="#991b1b", sw=1))
    frags.append(text(232, 250, "Центр мас CG збігається з CT", size=10, bold=True, color="#14532d"))

    # Радіус інерції стрілка
    frags.append(arrow(232, 200, 160, 172, color="#16a34a", sw=1.5))
    frags.append(text(180, 195, "Малий r_i", size=9, color="#16a34a", bold=True))

    # Характеристики
    frags.append(rect(45, 275, 375, 130, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    frags.append(text(232, 298, "ДИНАМІЧНІ ХАРАКТЕРИСТИКИ:", size=11, bold=True, color="#14532d"))
    frags.append(text(232, 318, "• Тензор інерції I = ∑ m_i·r_i² — МІНІМАЛЬНИЙ", size=10, color="#166534", bold=True))
    frags.append(text(232, 334, "• Кутове прискорення α = τ / I — максимальне", size=10, color="#334155"))
    frags.append(text(232, 350, "• Смуга пропускання PID контуру: 35–50 рад/с", size=10, color="#334155"))
    frags.append(text(232, 366, "• Мотори не перегріваються при маневрах", size=10, color="#334155"))
    frags.append(text(232, 382, "• Миттєвий відгук на збурення вітру", size=10, color="#059669"))

    # Панель 2: Рознесена маса (Децентралізована)
    frags.append(rect(465, 60, 405, 360, fill="#fff1f2", stroke="#fda4af", sw=1.5, rx=6))
    frags.append(text(667, 85, "Рознесена маса (Нераціонально)", size=14, bold=True, color="#9f1239"))

    # Схема дрона
    frags.append(line(565, 160, 765, 240, color="#64748b", sw=3))
    frags.append(line(565, 240, 765, 160, color="#64748b", sw=3))

    for mx, my in [(565, 160), (765, 160), (565, 240), (765, 240)]:
        frags.append(circle(mx, my, 12, fill="#e2e8f0", stroke="#475569", sw=1.5))

    # Винесені маси (Батарея на хвості, камера на носі)
    frags.append(rect(637, 185, 60, 30, fill="#cbd5e1", stroke="#64748b", sw=1.2, rx=3))
    frags.append(text(667, 204, "FC", size=10, bold=True, color="#334155"))

    # Важка камера спереду
    frags.append(rect(637, 120, 60, 32, fill="#ef4444", stroke="#b91c1c", sw=1.5, rx=3))
    frags.append(text(667, 140, "Payload (250 г)", size=10, color="#ffffff"))

    # Важка батарея ззаду
    frags.append(rect(637, 250, 60, 32, fill="#ef4444", stroke="#b91c1c", sw=1.5, rx=3))
    frags.append(text(667, 270, "Батарея (450 г)", size=10, color="#ffffff"))

    # Стрілка великого плеча
    frags.append(arrow(667, 200, 667, 155, color="#dc2626", sw=1.5))
    frags.append(arrow(667, 200, 667, 245, color="#dc2626", sw=1.5))
    frags.append(text(725, 175, "Велике плече r", size=9, color="#dc2626", bold=True))
    frags.append(text(725, 225, "I_yy зростає в 3–5 разів", size=9, color="#dc2626", bold=True))

    # Характеристики рознесеної
    frags.append(rect(480, 290, 375, 115, fill="#ffffff", stroke="#fda4af", sw=1, rx=4))
    frags.append(text(667, 310, "ДИНАМІЧНІ ПРОБЛЕМИ:", size=11, bold=True, color="#9f1239"))
    frags.append(text(667, 328, "• Момент інерції I_pitch / I_roll в рази більший", size=10, color="#dc2626", bold=True))
    frags.append(text(667, 344, "• Фазове запізнення в контурі керування PID", size=10, color="#334155"))
    frags.append(text(667, 360, "• Насичення моторів при спробі швидкого гальмування", size=10, color="#334155"))
    frags.append(text(667, 376, "• Зниження стійкості до поривів вітру та автоколивання", size=10, color="#7f1d1d"))

    render(os.path.join(OUT_DIR, "mass-distribution-and-inertia-tensor.svg"), w, h, *frags)


def fig_carbon_chafing():
    """Фігура 4: Механічний захист джгута від перетирання об кромки карбону та розвантаження натягу."""
    w, h = 900, 450
    frags = []

    # Фон
    frags.append(rect(15, 15, 870, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Заголовок
    frags.append(text(450, 40, "Механічний захист джгута від абразивних кромок вуглепластику", size=15, bold=True, color="#0f172a"))

    # Ліва панель: Аварійний контакт без захисту
    frags.append(rect(30, 60, 405, 360, fill="#fff1f2", stroke="#fda4af", sw=1.5, rx=6))
    frags.append(text(232, 85, "АВАРІЙНИЙ СТАН: Прямий контакт", size=14, bold=True, color="#9f1239"))

    # Карбонова пластина (гостра кромка 90°)
    frags.append(rect(50, 160, 160, 90, fill="#1e293b", stroke="#0f172a", sw=2, rx=1))
    frags.append(text(130, 205, "Карбон (CFRP)", size=12, bold=True, color="#ffffff"))
    frags.append(text(130, 225, "Провідний! σ ≈ 10⁴ См/м", size=10, color="#cbd5e1"))

    # Гостра кромка маркер
    frags.append(circle(210, 160, 6, fill="#ef4444", stroke="#991b1b", sw=1.5))
    frags.append(text(275, 150, "Гостра 90° кромка фрези", size=10, bold=True, color="#dc2626"))

    # Силовий провід, що перетерся
    # Мідна жила
    frags.append(line(150, 120, 210, 160, color="#f59e0b", sw=6))
    frags.append(line(210, 160, 360, 230, color="#f59e0b", sw=6))
    # Пошкоджена силіконова ізоляція
    frags.append(line(150, 120, 200, 153, color="#ef4444", sw=10))
    frags.append(line(220, 166, 360, 230, color="#ef4444", sw=10))

    # Іскра КЗ
    frags.append(text(210, 185, "⚡ КЗ на раму!", size=11, bold=True, color="#dc2626"))

    # Опис наслідків
    frags.append(rect(45, 275, 375, 130, fill="#ffffff", stroke="#fda4af", sw=1, rx=4))
    frags.append(text(232, 298, "МЕХАНІЗМ АВАРІЇ ТА НАСЛІДКИ:", size=11, bold=True, color="#9f1239"))
    frags.append(text(232, 318, "• Вібрація двигунів (100–400 Гц) притискає дріт", size=10, color="#334155"))
    frags.append(text(232, 334, "• Гостра карбонова кромка зрізає м'який силікон", size=10, color="#dc2626"))
    frags.append(text(232, 350, "• Струм +24V замикається на карбонову раму", size=10, color="#dc2626"))
    frags.append(text(232, 366, "• Згорання PDB, FC та підключених камер", size=10, color="#7f1d1d"))
    frags.append(text(232, 382, "• Повна втрата живлення в польоті", size=10, color="#991b1b", bold=True))

    # Права панель: Інженерний захист
    frags.append(rect(465, 60, 405, 360, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(667, 85, "ІНЖЕНЕРНИЙ ЗАХИСТ: Комплекс заходів", size=14, bold=True, color="#14532d"))

    # Карбонова пластина з фаскою / отвором
    frags.append(rect(485, 160, 150, 90, fill="#1e293b", stroke="#0f172a", sw=2, rx=1))
    frags.append(text(560, 205, "Карбон з фаскою 45°", size=11, bold=True, color="#ffffff"))

    # Гумовий люверс (Grommet) в отворі
    frags.append(rect(635, 145, 25, 120, fill="#3b82f6", stroke="#1d4ed8", sw=1.5, rx=6))
    frags.append(text(647, 280, "Люверс TPU", size=9, bold=True, color="#1d4ed8"))

    # Дріт у «зміїній шкірі» та термозбіжці
    frags.append(line(550, 110, 647, 195, color="#10b981", sw=12))
    frags.append(line(647, 195, 780, 200, color="#10b981", sw=12))

    # Капельна компенсаційна петля (Service Loop)
    frags.append('<path d="M 780,200 C 830,200 840,250 790,260 L 710,260" fill="none" stroke="#10b981" stroke-width="12"/>')

    # Стяжка кріплення на раму
    frags.append(rect(730, 245, 12, 30, fill="#0f172a", stroke="#475569", sw=1, rx=2))
    frags.append(text(736, 290, "Стяжка (Strain relief)", size=9, bold=True, color="#0f172a"))

    # Опис захисту
    frags.append(rect(480, 310, 375, 95, fill="#ffffff", stroke="#86efac", sw=1, rx=4))
    frags.append(text(667, 328, "ЕЛЕМЕНТИ НАДІЙНОГО МОНТАЖУ:", size=11, bold=True, color="#14532d"))
    frags.append(text(667, 346, "1. Зняття фаски 45° або радіусний край на ЧПК", size=10, color="#334155"))
    frags.append(text(667, 362, "2. Гумові / TPU люверси в прохідних отворах", size=10, color="#334155"))
    frags.append(text(667, 378, "3. Обплетення «зміїна шкіра» (PET Braided Sleeve)", size=10, color="#059669"))
    frags.append(text(667, 394, "4. Сервісна петля: радіус вигину R ≥ 5·d_кабелю", size=10, color="#166534", bold=True))

    render(os.path.join(OUT_DIR, "carbon-chafing-and-strain-relief.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_spatial_zoning()
    fig_ground_loop()
    fig_mass_distribution()
    fig_carbon_chafing()
    print("All 4 figures generated successfully in img/")
