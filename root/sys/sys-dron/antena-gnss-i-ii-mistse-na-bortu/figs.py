# -*- coding: utf-8 -*-
"""Генератор векторних діаграм (SVG) для теми:
«Антена GNSS і її місце на борту»
"""
import sys, os

# Шлях до svgkit у scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_antenna_types():
    """Фігура 1: Порівняння керамічної патч-антени та спіральної антени QHA."""
    w, h = 880, 440
    frags = []

    # Заголовок / Підкладки панелей
    p1 = rect(25, 45, 400, 375, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8)
    p2 = rect(455, 45, 400, 375, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8)
    frags.extend([p1, p2])

    frags.append(text(225, 75, "Керамічна патч-антена (Patch)", size=16, bold=True, color="#0f172a"))
    frags.append(text(655, 75, "Спіральна антена (QHA / Helix)", size=16, bold=True, color="#0f172a"))

    # ── Панель 1: Патч ─────────────────────────────────────────────────────
    # Площина заземлення (Ground plane)
    frags.append(rect(65, 230, 320, 14, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(225, 260, "Площина заземлення (Ground Plane, 50–70 мм)", size=12, color="#475569", bold=True))

    # Керамічна підкладка (Substrate)
    frags.append(rect(135, 175, 180, 55, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=3))
    frags.append(text(225, 205, "Кераміка (ε_r ≈ 20...90)", size=13, color="#334155", bold=True))

    # Металевий патч (Patch metallization)
    frags.append(rect(145, 163, 160, 12, fill="#f59e0b", stroke="#d97706", sw=1.5, rx=2))
    frags.append(text(225, 150, "Металевий випромінювач (Patch)", size=12, color="#b45309", bold=True))

    # Фідерний штир (Coaxial feed pin)
    frags.append(line(185, 175, 185, 244, color="#dc2626", sw=2.5))
    frags.append(circle(185, 175, 3.5, fill="#dc2626", stroke="#991b1b", sw=1))
    frags.append(text(185, 276, "Точка запитки (50 Ом)", size=11, color="#dc2626", bold=True))

    # Промінь / Діаграма спрямованості патча
    frags.append('<path d="M 125,160 C 125,75 325,75 325,160 Z" fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="4,3"/>')
    frags.append(text(225, 105, "Зенітний конус (+4...5 dBic)", size=12, color="#1d4ed8", bold=True))
    frags.append(text(225, 122, "Ширина променя HPBW ≈ 100°", size=11, color="#64748b"))

    # Характеристики патча
    t1_box = fitbox(45, 298, 360, 105,
                    "• Високе підсилення в зеніті, але спад на кутах < 20°\n"
                    "• Критично залежить від розміру Ground Plane\n"
                    "• Компактна висота (4–8 мм), оптимальна для крил/коптерів",
                    size=12, pad=8, fill="#ffffff", stroke="#cbd5e1")
    frags.append(t1_box)

    # ── Панель 2: Спіраль QHA ──────────────────────────────────────────────
    # Основа / циліндр
    frags.append(rect(610, 140, 90, 115, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))

    # Спіральні рукави (4 скручені провідники зі зсувом фаз)
    frags.append('<path d="M 615,245 Q 635,195 695,150" fill="none" stroke="#2563eb" stroke-width="2.5"/>')
    frags.append('<path d="M 695,245 Q 675,195 615,150" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    frags.append('<path d="M 630,250 Q 655,200 680,145" fill="none" stroke="#16a34a" stroke-width="2" stroke-dasharray="3,2"/>')
    frags.append('<path d="M 680,250 Q 655,200 630,145" fill="none" stroke="#f59e0b" stroke-width="2" stroke-dasharray="3,2"/>')

    frags.append(rect(595, 250, 120, 20, fill="#334155", stroke="#1e293b", sw=1.5, rx=3))
    frags.append(text(655, 264, "Фазообертач 0°/90°/180°/270°", size=10, color="#ffffff", bold=True))

    # Діаграма спрямованості QHA (широка кардіоїда)
    frags.append('<path d="M 545,230 C 545,85 765,85 765,230 C 765,260 700,270 655,255 C 610,270 545,260 545,230 Z" fill="none" stroke="#16a34a" stroke-width="2" stroke-dasharray="4,3"/>')
    frags.append(text(655, 105, "Широка кардіоїда (+1...2 dBic)", size=12, color="#15803d", bold=True))
    frags.append(text(655, 122, "HPBW ≈ 150° (бачить горизонт)", size=11, color="#64748b"))

    # Характеристики QHA
    t2_box = fitbox(475, 298, 360, 105,
                    "• Зберігає RHCP (AR < 3 dB) при кутах нахилу до 60°\n"
                    "• Не вимагає додаткової площини заземлення\n"
                    "• Циліндрична форма, ідеальна для маневрених дронів",
                    size=12, pad=8, fill="#ffffff", stroke="#cbd5e1")
    frags.append(t2_box)

    render(os.path.join(OUT_DIR, "gnss-antenna-types-comparison.svg"), w, h, *frags)


def fig_rhcp_multipath():
    """Фігура 2: Придушення відбитих сигналів завдяки зміні поляризації з RHCP на LHCP."""
    w, h = 880, 440
    frags = []

    # Фон
    frags.append(rect(20, 20, 840, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Супутник GNSS
    frags.append(rect(60, 50, 160, 45, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=5))
    frags.append(text(140, 77, "Супутник GNSS", size=14, color="#ffffff", bold=True))
    frags.append(line(40, 72, 60, 72, color="#0284c7", sw=4))
    frags.append(line(220, 72, 240, 72, color="#0284c7", sw=4))

    # Прямий промінь (Direct Path) - RHCP
    frags.append(arrow(180, 95, 680, 165, color="#16a34a", sw=2.5))
    frags.append(text(420, 110, "Прямий сигнал: RHCP (Права кругова)", size=13, color="#15803d", bold=True))
    frags.append(text(420, 128, "Осьове відношення AR ≈ 1.5 dB, затухання 0 dB", size=11, color="#475569"))

    # Відбитий промінь (Reflected Path) - падаючий RHCP
    frags.append(arrow(140, 95, 340, 330, color="#2563eb", sw=2))
    frags.append(text(210, 200, "Падаючий RHCP", size=11, color="#2563eb", bold=True))

    # Поверхня відбиття (Земля / Вода / Дах)
    frags.append(rect(220, 340, 620, 25, fill="#cbd5e1", stroke="#64748b", sw=1.5, rx=2))
    frags.append(text(530, 357, "Підстильна поверхня (ґрунт, вода, метал, будівлі)", size=12, color="#334155", bold=True))

    # Точка відбиття
    frags.append(circle(340, 340, 6, fill="#f59e0b", stroke="#d97706", sw=2))
    frags.append(text(340, 385, "Стрибок фази 180° → реверс знака поляризації", size=11, color="#b45309", bold=True))

    # Відбитий промінь до антени - LHCP
    frags.append(arrow(340, 340, 690, 185, color="#dc2626", sw=2.5))

    # Написи для відбитого сигналу розведені нижче траєкторії променя
    frags.append(text(560, 290, "Відбитий сигнал: LHCP (Ліва кругова)", size=13, color="#dc2626", bold=True))
    frags.append(text(560, 308, "Послаблення антеною: −15...−25 dB (Cross-Pol Isolation)", size=11, color="#991b1b"))

    # Дрон та антена
    frags.append(rect(670, 160, 80, 18, fill="#f59e0b", stroke="#b45309", sw=1.5, rx=3))
    frags.append(rect(650, 178, 120, 10, fill="#475569", stroke="#1e293b", sw=1.5, rx=2))
    frags.append(text(710, 150, "RHCP антена", size=12, color="#b45309", bold=True))
    frags.append(line(710, 188, 710, 220, color="#1e293b", sw=3))
    frags.append(rect(680, 220, 60, 25, fill="#334155", stroke="#0f172a", sw=1.5, rx=4))
    frags.append(text(710, 236, "БПЛА", size=11, color="#ffffff", bold=True))

    # Резюме внизу зліва
    sum_box = fitbox(40, 245, 230, 85,
                     "Результат:\n"
                     "Приймач бачить чистий пік кореляції\n"
                     "без зсуву псевдодальності від\n"
                     "багатопроменевих запізнених копій.",
                     size=11, pad=6, fill="#ffffff", stroke="#cbd5e1")
    frags.append(sum_box)

    render(os.path.join(OUT_DIR, "rhcp-reflection-multipath.svg"), w, h, *frags)


def fig_ground_plane():
    """Фігура 3: Вплив розміру площини заземлення на діаграму спрямованості та екранування."""
    w, h = 880, 430
    frags = []

    p1 = rect(25, 40, 400, 370, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8)
    p2 = rect(455, 40, 400, 370, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8)
    frags.extend([p1, p2])

    frags.append(text(225, 68, "Мала площина заземлення (< 30 мм)", size=15, bold=True, color="#dc2626"))
    frags.append(text(655, 68, "Оптимальна площина заземлення (70×70 мм)", size=15, bold=True, color="#16a34a"))

    # ── Варіант А: Мала підкладка ──────────────────────────────────────────
    frags.append(rect(185, 210, 80, 10, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    frags.append(rect(205, 195, 40, 15, fill="#f59e0b", stroke="#d97706", sw=1.5, rx=2))
    frags.append(text(225, 238, "Патч 25×25 мм без екрана", size=11, color="#475569", bold=True))

    # Спотворена діаграма спрямованості
    frags.append('<path d="M 160,205 C 160,110 290,110 290,205 C 290,240 270,255 225,245 C 180,255 160,240 160,205 Z" fill="none" stroke="#dc2626" stroke-width="2.2" stroke-dasharray="4,3"/>')
    frags.append(text(225, 125, "Підсилення в зеніті: +0...−2 dBic", size=12, color="#dc2626", bold=True))
    frags.append(text(225, 142, "Задні пелюстки: F/B < 6 dB", size=11, color="#64748b"))

    # Завади знизу
    frags.append(arrow(225, 305, 225, 260, color="#dc2626", sw=2))
    frags.append(text(225, 320, "Завади від ESC / VTX потрапляють в антену", size=11, color="#dc2626", bold=True))

    t1_box = fitbox(45, 340, 360, 55,
                    "• Деградація підсилення на 4–6 dB\n"
                    "• Відсутність екранування від бортової електроніки",
                    size=11, pad=6, fill="#ffffff", stroke="#cbd5e1")
    frags.append(t1_box)

    # ── Варіант Б: Оптимальна підкладка ────────────────────────────────────
    frags.append(rect(535, 210, 240, 12, fill="#16a34a", stroke="#15803d", sw=1.5, rx=2))
    frags.append(rect(635, 195, 40, 15, fill="#f59e0b", stroke="#d97706", sw=1.5, rx=2))
    frags.append(text(655, 238, "Мідний екран (Ground Plane 70 мм)", size=11, color="#15803d", bold=True))

    # Спрямована діаграма спрямованості
    frags.append('<path d="M 525,205 C 525,90 785,90 785,205 Z" fill="none" stroke="#16a34a" stroke-width="2.5"/>')
    frags.append(text(655, 120, "Підсилення в зеніті: +4.5...+5.0 dBic", size=12, color="#16a34a", bold=True))
    frags.append(text(655, 137, "Відношення вперед/назад: F/B > 18 dB", size=11, color="#475569"))

    # Зона захисної тіні знизу
    frags.append(rect(535, 255, 240, 35, fill="#dcfce7", stroke="#86efac", sw=1.5, rx=4))
    frags.append(text(655, 277, "Зона захисної радіотіні (ізоляція > 20 dB)", size=12, color="#15803d", bold=True))

    t2_box = fitbox(475, 340, 360, 55,
                    "• Максимальний C/N0 (45–50 dB-Hz)\n"
                    "• Надійне блокування випромінювання силових шин",
                    size=11, pad=6, fill="#ffffff", stroke="#cbd5e1")
    frags.append(t2_box)

    render(os.path.join(OUT_DIR, "ground-plane-radiation-pattern.svg"), w, h, *frags)


def fig_emi_sources_isolation():
    """Фігура 4: Джерела радіочастотних завад на борту та заходи ізоляції (щогла, екранування)."""
    w, h = 880, 440
    frags = []

    frags.append(rect(20, 20, 840, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # ── Щогла з GNSS нагорі ────────────────────────────────────────────────
    frags.append(rect(400, 45, 80, 20, fill="#f59e0b", stroke="#b45309", sw=1.5, rx=3))
    frags.append(rect(380, 65, 120, 10, fill="#16a34a", stroke="#15803d", sw=1.5, rx=2))
    frags.append(text(440, 38, "GNSS + Компас", size=13, color="#b45309", bold=True))

    # Складна щогла
    frags.append(rect(435, 75, 10, 115, fill="#334155", stroke="#0f172a", sw=1.5, rx=2))
    frags.append(arrow(470, 185, 470, 75, color="#2563eb", sw=2))
    frags.append(arrow(470, 75, 470, 185, color="#2563eb", sw=2))
    frags.append(text(555, 130, "Щогла h = 100–150 мм", size=12, color="#2563eb", bold=True))
    frags.append(text(555, 147, "Послаблення EMI: −20...−30 dB", size=11, color="#64748b"))

    # ── Основна дека дрона ─────────────────────────────────────────────────
    frags.append(rect(140, 190, 600, 18, fill="#0f172a", stroke="#020617", sw=1.5, rx=3))
    frags.append(text(440, 203, "Карбонова верхня дека БПЛА", size=11, color="#94a3b8", bold=True))

    # Джерело 1: Камера + MIPI FFC
    frags.append(rect(60, 230, 140, 65, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=5))
    frags.append(text(130, 252, "Камера + MIPI", size=13, color="#b91c1c", bold=True))
    frags.append(text(130, 272, "Шлейф FFC (CSI-2)", size=11, color="#7f1d1d"))
    frags.append(text(130, 287, "Гармоніки до 1.6 ГГц", size=10, color="#991b1b"))

    # Джерело 2: Польотний контролер (FC)
    frags.append(rect(230, 230, 180, 65, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=5))
    frags.append(text(320, 252, "Польотний контролер", size=13, color="#b91c1c", bold=True))
    frags.append(text(320, 272, "STM32 / i.MX8 (SPI, Clock)", size=11, color="#7f1d1d"))
    frags.append(text(320, 287, "Випромінювання шин", size=10, color="#991b1b"))

    # Джерело 3: ESC + Силові дроти
    frags.append(rect(440, 230, 190, 65, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=5))
    frags.append(text(535, 252, "ESC 4-in-1 / Силові шини", size=13, color="#b91c1c", bold=True))
    frags.append(text(535, 272, "ШІМ 24–96 кГц, сплески di/dt", size=11, color="#7f1d1d"))
    frags.append(text(535, 287, "Магнітне поле струмів 80 А", size=10, color="#991b1b"))

    # Джерело 4: Відеопередавач VTX
    frags.append(rect(660, 230, 160, 65, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=5))
    frags.append(text(740, 252, "VTX 5.8G / 1.3G", size=13, color="#b91c1c", bold=True))
    frags.append(text(740, 272, "Потужність 1–2 Вт", size=11, color="#7f1d1d"))
    frags.append(text(740, 287, "Блокування вхідного LNA", size=10, color="#991b1b"))

    # ── Заходи захисту (Нижня панель) ──────────────────────────────────────
    frags.append(rect(40, 315, 800, 90, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    frags.append(text(440, 335, "Комплексний захист радіочастотного тракту GNSS", size=14, color="#15803d", bold=True))

    m1 = "1. Винос на щоглу 10–15 см (закон 1/r²)"
    m2 = "2. Мідний екран під модулем (Ground Plane 70 мм)"
    m3 = "3. Феритове кільце на джгуті UART/I2C"
    m4 = "4. Фільтр низьких частот (LPF) на виході VTX 1.3 ГГц"

    frags.append(text(230, 362, m1, size=11, color="#166534", anchor="middle"))
    frags.append(text(650, 362, m2, size=11, color="#166534", anchor="middle"))
    frags.append(text(230, 388, m3, size=11, color="#166534", anchor="middle"))
    frags.append(text(650, 388, m4, size=11, color="#166534", anchor="middle"))

    render(os.path.join(OUT_DIR, "uav-emi-sources-isolation.svg"), w, h, *frags)


def fig_ubx_mon_rf():
    """Фігура 5: Радіочастотний моніторинг UBX-MON-RF та динаміка метрик шуму."""
    w, h = 880, 430
    frags = []

    # Фон
    frags.append(rect(20, 20, 840, 390, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Верхня частина: Тракт приймача
    frags.append(rect(40, 45, 100, 45, fill="#f59e0b", stroke="#b45309", sw=1.5, rx=4))
    frags.append(text(90, 72, "Антена", size=13, color="#ffffff", bold=True))

    frags.append(arrow(140, 68, 175, 68, color="#475569", sw=2))

    frags.append(rect(175, 45, 110, 45, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    frags.append(text(230, 65, "SAW-фільтр", size=12, color="#1e293b", bold=True))
    frags.append(text(230, 80, "Смуга L1", size=10, color="#64748b"))

    frags.append(arrow(285, 68, 320, 68, color="#475569", sw=2))

    frags.append(rect(320, 45, 100, 45, fill="#3b82f6", stroke="#1d4ed8", sw=1.5, rx=4))
    frags.append(text(370, 65, "LNA", size=13, color="#ffffff", bold=True))
    frags.append(text(370, 80, "G ≈ 26 dB", size=10, color="#dbeafe"))

    frags.append(arrow(420, 68, 455, 68, color="#475569", sw=2))

    frags.append(rect(455, 45, 130, 45, fill="#8b5cf6", stroke="#6d28d9", sw=1.5, rx=4))
    frags.append(text(520, 65, "Змішувач + АРП", size=12, color="#ffffff", bold=True))
    frags.append(text(520, 80, "AGC Loop", size=10, color="#ede9fe"))

    frags.append(arrow(585, 68, 620, 68, color="#475569", sw=2))

    frags.append(rect(620, 45, 220, 45, fill="#0f172a", stroke="#020617", sw=1.5, rx=4))
    frags.append(text(730, 65, "Цифровий корелятор", size=12, color="#ffffff", bold=True))
    frags.append(text(730, 80, "Формування UBX-MON-RF", size=10, color="#38bdf8"))

    # Нижня частина: Графіки тесту з газом
    frags.append(rect(40, 110, 790, 280, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(435, 135, "Діагностичний тест «Gas Sweep» (прогін тяги 0% → 100%)", size=14, color="#0f172a", bold=True))

    # Вісь X та Y
    frags.append(line(80, 340, 780, 340, color="#64748b", sw=1.5))
    frags.append(line(80, 160, 80, 340, color="#64748b", sw=1.5))
    frags.append(text(780, 358, "Час / Тяга моторів (%)", size=11, color="#64748b", anchor="end"))

    # Позначки тяги
    frags.append(text(150, 355, "0% (Спокій)", size=10, color="#64748b"))
    frags.append(text(300, 355, "VTX ON", size=10, color="#64748b"))
    frags.append(text(460, 355, "Газ 50%", size=10, color="#64748b"))
    frags.append(text(650, 355, "Газ 100%", size=10, color="#64748b"))

    # Лінії сітки
    frags.append(line(240, 160, 240, 340, color="#f1f5f9", sw=1, dash="3,3"))
    frags.append(line(400, 160, 400, 340, color="#f1f5f9", sw=1, dash="3,3"))
    frags.append(line(580, 160, 580, 340, color="#f1f5f9", sw=1, dash="3,3"))

    # Крива 1: noisePerMS (Шум)
    frags.append('<path d="M 80,310 L 240,310 L 245,300 L 400,295 L 480,265 L 580,240 L 720,205 L 770,195" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    frags.append(text(730, 185, "noisePerMS (Шум зростає)", size=11, color="#dc2626", bold=True))

    # Крива 2: agcCnt (АРП)
    frags.append('<path d="M 80,180 L 240,180 L 245,210 L 400,215 L 480,240 L 580,260 L 720,285 L 770,295" fill="none" stroke="#2563eb" stroke-width="2.5"/>')
    frags.append(text(730, 310, "agcCnt (АРП душить підсилення)", size=11, color="#2563eb", bold=True))

    # Пояснення порогів
    frags.append(rect(100, 175, 230, 55, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=3))
    frags.append(text(110, 195, "Нормальний фон:", size=11, color="#16a34a", bold=True, anchor="start"))
    frags.append(text(110, 215, "noisePerMS ≈ 35...60, agcCnt ≈ 7500", size=10, color="#334155", anchor="start"))

    frags.append(rect(380, 175, 250, 55, fill="#fef2f2", stroke="#fca5a5", sw=1, rx=3))
    frags.append(text(390, 195, "Критичне зашумлення (100% газу):", size=11, color="#b91c1c", bold=True, anchor="start"))
    frags.append(text(390, 215, "noisePerMS > 120, agcCnt < 4000 (Jamming)", size=10, color="#7f1d1d", anchor="start"))

    render(os.path.join(OUT_DIR, "ubx-mon-rf-noise-floor.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_antenna_types()
    fig_rhcp_multipath()
    fig_ground_plane()
    fig_emi_sources_isolation()
    fig_ubx_mon_rf()
    print("Всі фігури згенеровано успішно в", OUT_DIR)
