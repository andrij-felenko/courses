# -*- coding: utf-8 -*-
"""Генератор векторних діаграм (SVG) для теми:
«Джгут, обтиск і розвантаження натягу»
"""
import sys, os

# Шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_crimp_geometry():
    """Фігура 1: Геометрія та критерії якості обтискного контакту за IPC/WHMA-A-620."""
    w, h = 920, 520
    frags = []

    # Загальний контур
    frags.append(rect(15, 15, 890, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(460, 40, "Геометрія та критерії якості обтискного контакту за IPC/WHMA-A-620", size=16, bold=True, color="#0f172a"))

    # ── Ліва панель: Поперечний переріз B-crimp (F-crimp) ──
    frags.append(rect(30, 60, 415, 430, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(237, 84, "Поперечний переріз обтиску жили (B-crimp)", size=13, bold=True, color="#1e293b"))

    # Схематичне зображення обтиснутої гільзи (мідь/латунь контакт)
    frags.append('<path d="M 120 220 C 120 150, 180 140, 237 185 C 294 140, 354 150, 354 220 C 354 270, 320 295, 237 295 C 154 295, 120 270, 120 220 Z" fill="#e2e8f0" stroke="#475569" stroke-width="2"/>')
    frags.append('<path d="M 135 220 C 135 165, 185 155, 237 195 C 289 155, 339 165, 339 220 C 339 260, 310 280, 237 280 C 164 280, 135 260, 135 220 Z" fill="#fed7aa" stroke="#ea580c" stroke-width="1.5"/>')

    # Внутрішні щільно спресовані шестигранні мідні жили (газонепроникний контакт)
    strands = [
        (205, 210), (225, 210), (245, 210), (265, 210),
        (195, 225), (215, 225), (237, 225), (259, 225), (279, 225),
        (185, 240), (205, 240), (225, 240), (245, 240), (265, 240), (285, 240),
        (195, 255), (215, 255), (237, 255), (259, 255), (279, 255),
        (215, 270), (237, 270), (259, 270)
    ]
    for sx, sy in strands:
        frags.append(circle(sx, sy, 8, fill="#f97316", stroke="#c2410c", sw=1.0))

    # Вимірювальні лінії Crimp Height (CH) та Crimp Width (CW)
    frags.append(line(95, 150, 95, 295, color="#dc2626", sw=1.8))
    frags.append(line(90, 150, 130, 150, color="#dc2626", sw=1.2))
    frags.append(line(90, 295, 150, 295, color="#dc2626", sw=1.2))
    frags.append(text(80, 225, "CH", size=12, bold=True, color="#dc2626", anchor="end"))
    frags.append(text(80, 240, "(Висота)", size=10, color="#dc2626", anchor="end"))

    frags.append(line(120, 315, 354, 315, color="#2563eb", sw=1.8))
    frags.append(line(120, 290, 120, 320, color="#2563eb", sw=1.2))
    frags.append(line(354, 290, 354, 320, color="#2563eb", sw=1.2))
    frags.append(text(237, 335, "CW (Ширина обтиску)", size=11, bold=True, color="#2563eb"))

    # Виноски критеріїв якості перерізу
    frags.append(rect(45, 355, 385, 120, fill="#f8fafc", stroke="#e2e8f0", sw=1.0, rx=4))
    frags.append(text(55, 375, "Критерії газонепроникного обтиску:", size=11, bold=True, color="#0f172a", anchor="start"))
    frags.append(text(55, 395, "• Коефіцієнт ущільнення жил > 85–90% (без пустот)", size=10, color="#334155", anchor="start"))
    frags.append(text(55, 412, "• Симетричний підгин крил гільзи без задирок і тріщин", size=10, color="#334155", anchor="start"))
    frags.append(text(55, 429, "• Руйнування оксидної плівки та металічний контакт", size=10, color="#334155", anchor="start"))
    frags.append(text(55, 446, "• Товщина дна гільзи не стоншена нижче допустимої", size=10, color="#334155", anchor="start"))
    frags.append(text(55, 463, "• Відсутність підрізання або надлому окремих провідників", size=10, color="#dc2626", anchor="start"))

    # ── Права панель: Поздовжня геометрія контакту за IPC-620 ──
    frags.append(rect(460, 60, 445, 430, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(682, 84, "Поздовжній профіль та зони інспекції", size=13, bold=True, color="#1e293b"))

    # Послідовні сегменти без геометричного накладання:
    # 1. Дріт з ізоляцією: x: 475..555 (w=80, h=50)
    frags.append(rect(475, 160, 80, 50, fill="#3b82f6", stroke="#1d4ed8", sw=1.5, rx=3))
    frags.append(text(515, 190, "Ізоляція", size=11, bold=True, color="#ffffff"))

    # 2. Обтиск ізоляції (Insulation Crimp): x: 555..600 (w=45, h=66, y=152)
    frags.append(rect(555, 152, 45, 66, fill="#cbd5e1", stroke="#475569", sw=1.8, rx=2))
    frags.append(text(577, 138, "Обтиск", size=10, bold=True, color="#475569"))
    frags.append(text(577, 150, "ізоляції", size=10, bold=True, color="#475569"))

    # 3. Видимий зазор оголеної жили: x: 600..630 (w=30, h=36, y=167)
    frags.append(rect(600, 167, 30, 36, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=0))

    # 4. Задній розтруб: x: 630..640
    frags.append('<polygon points="630,155 640,160 640,210 630,215" fill="#94a3b8" stroke="#334155" stroke-width="1.2"/>')

    # 5. Обтиск жили (Conductor Crimp Barrel): x: 640..715 (w=75, h=50, y=160)
    frags.append(rect(640, 160, 75, 50, fill="#94a3b8", stroke="#334155", sw=1.8, rx=0))
    frags.append(text(677, 188, "Обтиск жили", size=10, bold=True, color="#0f172a"))

    # 6. Передній розтруб: x: 715..722
    frags.append('<polygon points="715,160 722,156 722,214 715,210" fill="#94a3b8" stroke="#334155" stroke-width="1.2"/>')

    # 7. Щітка жил (Conductor Brush): x: 722..744 (w=22, h=36, y=167)
    frags.append(rect(722, 167, 22, 36, fill="#f97316", stroke="#c2410c", sw=1.2, rx=0))

    # 8. Зазор переходу: x: 744..755
    frags.append(line(744, 185, 755, 185, color="#cbd5e1", sw=2.0))

    # 9. Контактна робоча зона (Mating Area / Pin): x: 755..880 (w=125, h=44, y=163)
    frags.append(rect(755, 163, 125, 44, fill="#e2e8f0", stroke="#475569", sw=1.8, rx=2))
    frags.append(text(817, 188, "Контактний пін", size=11, bold=True, color="#1e293b"))

    # Фіксуючий язичок (Locking Tang)
    frags.append('<polygon points="785,163 805,148 812,163" fill="#cbd5e1" stroke="#334155" stroke-width="1.2"/>')
    frags.append(text(798, 142, "Замок (Tang)", size=9, bold=True, color="#64748b"))

    # Виноски та розмірні лінії поздовжнього профілю
    # 1. Зазор ізоляції
    frags.append(line(615, 210, 615, 270, color="#059669", sw=1.5))
    frags.append(text(615, 285, "Зазор ізоляції", size=10, bold=True, color="#059669"))
    frags.append(text(615, 298, "0.1–0.5 мм", size=9, color="#059669"))

    # 2. Задній розтруб
    frags.append(line(635, 220, 635, 245, color="#2563eb", sw=1.5))
    frags.append(text(648, 258, "Задній розтруб", size=10, bold=True, color="#2563eb"))
    frags.append(text(648, 270, "0.1–0.4 мм", size=9, color="#2563eb"))

    # 3. Передній розтруб
    frags.append(line(718, 220, 718, 245, color="#2563eb", sw=1.5))
    frags.append(text(725, 258, "Передній", size=10, bold=True, color="#2563eb"))
    frags.append(text(725, 270, "0.05–0.25 мм", size=9, color="#2563eb"))

    # 4. Щітка жил
    frags.append(line(733, 210, 733, 295, color="#d97706", sw=1.5))
    frags.append(text(755, 310, "Щітка жил", size=10, bold=True, color="#d97706"))
    frags.append(text(755, 323, "0.1–0.5 мм", size=9, color="#d97706"))

    # 5. Заборона заходу жили в контактну зону
    frags.append(line(744, 155, 744, 225, color="#dc2626", sw=1.5, dash="3,3"))
    frags.append(text(817, 225, "Межа контактної зони", size=10, bold=True, color="#dc2626"))
    frags.append(text(817, 238, "(жили не доходять до піна)", size=9, color="#dc2626"))

    # Таблиця дефектів монтажу
    frags.append(rect(475, 355, 415, 120, fill="#fef2f2", stroke="#fecaca", sw=1.0, rx=4))
    frags.append(text(485, 375, "Типові дефекти та їхній наслідок на борту:", size=11, bold=True, color="#991b1b", anchor="start"))
    frags.append(text(485, 395, "• Недообтиск (CH завеликий) → виривання жили під вібрацією", size=10, color="#7f1d1d", anchor="start"))
    frags.append(text(485, 412, "• Переобтиск (CH замалий) → надріз жил, окрихчування дроту", size=10, color="#7f1d1d", anchor="start"))
    frags.append(text(485, 429, "• Відсутній задній розтруб → зріз жили об гострий край гільзи", size=10, color="#7f1d1d", anchor="start"))
    frags.append(text(485, 446, "• Ізоляція потрапила в гільзу → плаваючий опір шини I2C/CAN", size=10, color="#7f1d1d", anchor="start"))
    frags.append(text(485, 463, "• Довга щітка жил → заклинювання піна та відсутність контакту", size=10, color="#7f1d1d", anchor="start"))

    return render(os.path.join(OUT_DIR, "crimp-cross-section-geometry.svg"), w, h, *frags)


def fig_strain_relief():
    """Фігура 2: Методи механічного розвантаження натягу та захисту кабельних джгутів."""
    w, h = 920, 520
    frags = []

    # Загальний контур
    frags.append(rect(15, 15, 890, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(460, 40, "Механічне розвантаження натягу (Strain Relief) та захист джгута", size=16, bold=True, color="#0f172a"))

    # ── Блок А: Компенсаційна сервісна петля (Service Loop) ──
    frags.append(rect(30, 60, 275, 430, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(167, 84, "Компенсаційна петля", size=13, bold=True, color="#1e293b"))
    frags.append(text(167, 100, "(Service Loop перед демпфером)", size=10, color="#64748b"))

    # Плата політного контролера (x: 45..145)
    frags.append(rect(45, 130, 100, 70, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=4))
    frags.append(text(95, 160, "Плата FC", size=11, bold=True, color="#15803d"))
    frags.append(text(95, 175, "на демпферах", size=9, color="#166534"))

    # Роз'єм JST-GH (x: 145..170)
    frags.append(rect(145, 150, 25, 30, fill="#cbd5e1", stroke="#475569", sw=1.2, rx=2))

    # Сервісна петля S-подібна
    frags.append('<path d="M 170 165 C 220 165, 250 200, 220 240 C 190 280, 220 320, 250 320" fill="none" stroke="#2563eb" stroke-width="4"/>')

    # Рама дрона
    frags.append(rect(250, 310, 45, 40, fill="#334155", stroke="#0f172a", sw=1.5, rx=2))
    frags.append(text(272, 335, "Рама", size=10, bold=True, color="#ffffff"))

    # Точка жорсткої фіксації стяжкою до рами
    frags.append(circle(255, 320, 6, fill="#dc2626", stroke="#991b1b", sw=1.2))
    frags.append(text(235, 370, "Точка анкерного", size=10, bold=True, color="#dc2626"))
    frags.append(text(235, 384, "кріплення стяжкою", size=9, color="#dc2626"))

    # Пояснення механізму
    frags.append(rect(40, 400, 255, 80, fill="#eff6ff", stroke="#bfdbfe", sw=1.0, rx=4))
    frags.append(text(50, 418, "• Радіус вигину R ≥ 8–10 D", size=10, bold=True, color="#1e40af", anchor="start"))
    frags.append(text(50, 434, "• Нульове паразитне зусилля на FC", size=10, color="#1e3a8a", anchor="start"))
    frags.append(text(50, 450, "• Вільний хід демпферів при ударі", size=10, color="#1e3a8a", anchor="start"))
    frags.append(text(50, 466, "• Захист пінів JST-GH від втоми", size=10, color="#1e3a8a", anchor="start"))

    # ── Блок Б: Градієнт жорсткості (Клейова термозбіжка) ──
    frags.append(rect(320, 60, 280, 430, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(460, 84, "Градієнт жорсткості", size=13, bold=True, color="#1e293b"))
    frags.append(text(460, 100, "(Dual-Wall Adhesive Heatshrink)", size=10, color="#64748b"))

    # Жорсткий корпус роз'єму (x: 340..395)
    frags.append(rect(340, 160, 55, 90, fill="#e2e8f0", stroke="#334155", sw=1.8, rx=4))
    frags.append(text(367, 205, "Жорсткий", size=10, bold=True, color="#1e293b"))
    frags.append(text(367, 220, "роз'єм", size=10, bold=True, color="#1e293b"))

    # Двостінна термозбіжна трубка з клеєм (x: 395..495)
    frags.append(rect(395, 175, 100, 60, fill="#38bdf8", stroke="#0284c7", sw=1.5, rx=3))
    frags.append(text(445, 195, "Клейова", size=10, bold=True, color="#0369a1"))
    frags.append(text(445, 210, "термозбіжка", size=10, bold=True, color="#0369a1"))
    frags.append(text(445, 225, "(напівжорстка)", size=9, color="#0c4a6e"))

    # Внутрішній розплавлений клей (Hotmelt adhesive layer)
    frags.append(rect(395, 230, 100, 5, fill="#facc15", stroke="#ca8a04", sw=0.8, rx=1))

    # Гнучкий силіконовий кабель (x: 495..590)
    frags.append(rect(495, 185, 95, 40, fill="#f97316", stroke="#c2410c", sw=1.5, rx=2))
    frags.append(text(542, 205, "Гнучкий дріт", size=10, bold=True, color="#ffffff"))
    frags.append(text(542, 218, "силікон", size=9, color="#ffffff"))

    # Зони жорсткості та епюра напружень
    frags.append(rect(335, 290, 250, 90, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=4))
    frags.append(text(460, 310, "Перерозподіл згинальних напруг:", size=10, bold=True, color="#0f172a"))
    frags.append(text(460, 328, "1. Зона пайки/обтиску: 0% вигину", size=9, color="#15803d"))
    frags.append(text(460, 344, "2. Зона трубки: плавний перехід", size=9, color="#0369a1"))
    frags.append(text(460, 360, "3. Дріт: вільний безпечний вигин", size=9, color="#b45309"))

    frags.append(rect(335, 400, 250, 80, fill="#f0fdf4", stroke="#bbf7d0", sw=1.0, rx=4))
    frags.append(text(345, 418, "• Клей заповнює 100% порожнин", size=10, bold=True, color="#166534", anchor="start"))
    frags.append(text(345, 434, "• Бар'єр від вологи та конденсату", size=10, color="#14532d", anchor="start"))
    frags.append(text(345, 450, "• Зсув точки зламу з пайки на дріт", size=10, color="#14532d", anchor="start"))
    frags.append(text(345, 466, "• Коефіцієнт усадки 3:1 або 4:1", size=10, color="#14532d", anchor="start"))

    # ── Блок В: Захист від кромки карбону (Grommet & Sleeving) ──
    frags.append(rect(615, 60, 275, 430, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(752, 84, "Захист від кромки рами", size=13, bold=True, color="#1e293b"))
    frags.append(text(752, 100, "(Люверси та сітчасте обплетення)", size=10, color="#64748b"))

    # Вуглепластикова пластина (карбон з гострою кромкою)
    frags.append(rect(635, 140, 20, 50, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=1))
    frags.append(rect(635, 240, 20, 50, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=1))
    frags.append(text(645, 165, "C", size=11, bold=True, color="#ffffff"))
    frags.append(text(645, 265, "C", size=11, bold=True, color="#ffffff"))

    # Гумовий / силіконовий захисний люверс (Edge Grommet)
    frags.append(rect(630, 190, 30, 12, fill="#475569", stroke="#334155", sw=1.2, rx=3))
    frags.append(rect(630, 228, 30, 12, fill="#475569", stroke="#334155", sw=1.2, rx=3))
    frags.append(text(745, 175, "Силіконовий люверс", size=10, bold=True, color="#334155"))

    # Кабельний джгут у сітчастому обплетенні (PET Snake Skin)
    frags.append(rect(630, 202, 240, 26, fill="#a855f7", stroke="#7e22ce", sw=1.5, rx=2))
    frags.append(text(755, 219, "PET обплетення (Snake Skin)", size=10, bold=True, color="#ffffff"))

    # Текст про небезпеку карбону
    frags.append(text(745, 270, "Карбон = провідник та абразив!", size=10, bold=True, color="#dc2626"))
    frags.append(text(745, 285, "Питомий опір ~10⁴ См/м", size=9, color="#dc2626"))

    frags.append(rect(625, 400, 255, 80, fill="#fef2f2", stroke="#fecaca", sw=1.0, rx=4))
    frags.append(text(635, 418, "• Захист від КЗ силових ліній на раму", size=10, bold=True, color="#991b1b", anchor="start"))
    frags.append(text(635, 434, "• Стійкість PET до вібраційного тертя", size=10, color="#7f1d1d", anchor="start"))
    frags.append(text(635, 450, "• Номекс біля гарячих ESC (>200°C)", size=10, color="#7f1d1d", anchor="start"))
    frags.append(text(635, 466, "• Фіксація джгута кожні 100–150 мм", size=10, color="#7f1d1d", anchor="start"))

    return render(os.path.join(OUT_DIR, "cable-strain-relief-techniques.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_crimp_geometry()
    fig_strain_relief()
    print("Згенеровано фігури у", OUT_DIR)
