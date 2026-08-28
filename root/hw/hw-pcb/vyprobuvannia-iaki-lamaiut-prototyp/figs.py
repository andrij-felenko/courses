# -*- coding: utf-8 -*-
"""Фігури теми «Випробування, які ламають прототип». Запуск: python figs.py -> ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_halt_stress_margins_envelope():
    """Конверт експлуатаційної та деструктивної надійності HALT і вікно скринінгу HASS."""
    f = []
    w, h = 900, 520
    
    # Заголовок / фонова підкладка
    f.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    f.append(text(w / 2, 38, "Конверт граничних навантажень HALT та формування запасу міцності", size=15, bold=True))
    f.append(text(w / 2, 56, "Ступінчасте навантаження до відмови, пошук експлуатаційних (UOL/LOL) та деструктивних (UDL/LDL) меж", size=11, color=MUTED))

    # Ліва панель: Температурний та комбінований стрес-профіль (вісь часу і навантаження)
    f.append(rect(25, 75, 460, 420, fill="#fbfcfd", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(255, 98, "Ступінчастий стрес HALT (Step-Stress Timeline)", size=12, color="#1e293b", bold=True))

    # Зони на лівому графіку:
    # 1. Зона специфікації (Spec Window)
    f.append(rect(66, 330, 405, 65, fill="#ecfdf5", stroke="#10b981", sw=1, rx=0))
    f.append(text(268, 366, "Діапазон ТЗ (Specification: −40 °C ... +85 °C / 3g)", size=10, color="#047857", bold=True))

    # 2. Зона експлуатаційної стабільності (LOL - UOL)
    f.append(rect(66, 240, 405, 90, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=0))
    f.append(text(268, 288, "Запас стабільності (Operating Margin: до LOL / UOL)", size=10, color="#1d4ed8", bold=True))

    # 3. Зона пластичних деформацій та деструкції (UDL / LDL)
    f.append(rect(66, 140, 405, 100, fill="#fef2f2", stroke="#ef4444", sw=1, rx=0))
    f.append(text(268, 195, "Руйнівна зона HALT (Destruct Margin: до LDL / UDL)", size=10, color="#b91c1c", bold=True))

    # Вісь координат для степ-стресу
    # Y-вісь (стрес)
    f.append(line(65, 440, 65, 125, color="#475569", sw=1.5))
    f.append(arrow(65, 130, 65, 120, color="#475569", sw=1.5))
    f.append(text(60, 116, "Рівень стресу (+T, −T, Vib, V)", size=10, color="#475569", anchor="start", bold=True))
    
    # X-вісь (час)
    f.append(line(65, 440, 465, 440, color="#475569", sw=1.5))
    f.append(arrow(460, 440, 470, 440, color="#475569", sw=1.5))
    f.append(text(465, 456, "Час тесту (t)", size=10, color="#475569", anchor="end"))

    # Ступінчаста крива HALT (Step-stress curve)
    steps = [
        (65, 385), (105, 385), (105, 355), (145, 355), (145, 315), (185, 315),
        (185, 275), (225, 275), (225, 235), (265, 235), (265, 195), (305, 195),
        (305, 160), (345, 160), (345, 135), (395, 135)
    ]
    step_path = ["M %.1f,%.1f" % steps[0]]
    for pt in steps[1:]:
        step_path.append("L %.1f,%.1f" % pt)
    f.append('<path d="%s" fill="none" stroke="#0f172a" stroke-width="2.5"/>' % " ".join(step_path))

    # Точки відмов - плашки повністю всередині відповідних зон
    # Оборотна відмова (UOL / LOL)
    f.append(circle(265, 235, 5, fill="#2563eb", stroke="#ffffff", sw=1.5))
    f.append(rect(145, 248, 115, 32, fill="#ffffff", stroke="#2563eb", sw=1, rx=3))
    f.append(text(202, 262, "UOL: Оборотний збій", size=9.5, color="#1e40af", bold=True))
    f.append(text(202, 274, "PLL / RAM timing drift", size=9, color=MUTED))

    # Необоротна руйнівна відмова (UDL / LDL)
    f.append(circle(345, 160, 5, fill="#dc2626", stroke="#ffffff", sw=1.5))
    f.append(rect(340, 146, 120, 32, fill="#ffffff", stroke="#dc2626", sw=1, rx=3))
    f.append(text(400, 160, "UDL: Руйнування", size=9.5, color="#991b1b", bold=True))
    f.append(text(400, 172, "BGA shear / Via crack", size=9, color=MUTED))

    # Права панель: Конверт запасу надійності (Таблиця осей стресу)
    f.append(rect(500, 75, 375, 420, fill="#fbfcfd", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(687, 98, "Порівняння меж запасу міцності", size=12, color="#1e293b", bold=True))

    # Таблиця 5 осей стресу
    axes_data = [
        ("Холодний стрес", "−40 °C", "−65 °C (LOL)", "−90 °C (LDL)", "#2457d6"),
        ("Гарячий стрес", "+85 °C", "+125 °C (UOL)", "+155 °C (UDL)", "#c0392b"),
        ("Вібрація 6DoF", "3 g_rms", "28 g_rms (UOL)", "48 g_rms (UDL)", "#d97706"),
        ("Швидкість Т-циклу", "5 °C/хв", "40 °C/хв (UOL)", "65 °C/хв (UDL)", "#7c3aed"),
        ("Напруга живлення", "±10%", "±22% (UOL)", "+45% OVP (UDL)", "#059669")
    ]

    # Шапка таблиці осей
    f.append(rect(512, 120, 350, 26, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=3))
    f.append(text(560, 137, "Параметр", size=9.5, color="#334155", bold=True))
    f.append(text(648, 137, "Специфікація", size=9.5, color="#047857", bold=True))
    f.append(text(730, 137, "Межа UOL/LOL", size=9.5, color="#1d4ed8", bold=True))
    f.append(text(815, 137, "Межа UDL/LDL", size=9.5, color="#b91c1c", bold=True))

    y_pos = 154
    for name, spec, op_lim, des_lim, col in axes_data:
        f.append(rect(512, y_pos, 350, 50, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=3))
        f.append(circle(524, y_pos + 25, 4.5, fill=col, stroke="none"))
        f.append(text(572, y_pos + 30, name, size=9.5, color="#0f172a", bold=True))
        f.append(text(648, y_pos + 30, spec, size=9.5, color="#047857"))
        f.append(text(730, y_pos + 30, op_lim, size=9.5, color="#1d4ed8", bold=True))
        f.append(text(815, y_pos + 30, des_lim, size=9.5, color="#b91c1c", bold=True))
        y_pos += 56

    # Нижній інформаційний блок: Вікно виробничого скринінгу HASS
    f.append(rect(512, 442, 350, 42, fill="#fefce8", stroke="#eab308", sw=1, rx=4))
    f.append(text(687, 459, "Вікно HASS = 50% між Специфікацією та UOL", size=9.5, color="#854d0e", bold=True))
    f.append(text(687, 474, "Виявляє прихований брак пайки без вичерпання ресурсу втоми", size=9, color="#a16207"))

    return "\n".join(f)


def fig_vibration_resonance_spectral_density():
    """Спектральна густина потужності випадкової вібрації (PSD) та резонансні моди плати."""
    f = []
    w, h = 900, 500
    
    # Підкладка
    f.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    f.append(text(w / 2, 38, "Спектральна густина випадкової вібрації (PSD) та механічний резонанс плати", size=15, bold=True))
    f.append(text(w / 2, 56, "Профіль збудження за MIL-STD-810H, власні частоти вигину текстоліту та концентрація напружень у BGA", size=11, color=MUTED))

    # Лівий графік: Профіль PSD (Power Spectral Density)
    f.append(rect(25, 75, 490, 395, fill="#fbfcfd", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(270, 98, "Спектр випадкової вібрації (Random Vibration Profile)", size=12, color="#1e293b", bold=True))

    # Координатна сітка
    # Y-вісь (PSD, g^2/Hz)
    f.append(line(80, 420, 80, 130, color="#475569", sw=1.5))
    f.append(arrow(80, 135, 80, 125, color="#475569", sw=1.5))
    f.append(text(75, 120, "PSD (g²/Hz)", size=10, color="#475569", anchor="start", bold=True))
    
    # X-вісь (Частота, Гц)
    f.append(line(80, 420, 495, 420, color="#475569", sw=1.5))
    f.append(arrow(490, 420, 500, 420, color="#475569", sw=1.5))
    f.append(text(495, 436, "Частота f (Гц)", size=10, color="#475569", anchor="end"))

    # Сітка частот та підписи
    grid_x = [(135, "20"), (230, "100"), (325, "500"), (415, "1000"), (475, "2000")]
    for gx, lab in grid_x:
        f.append(line(gx, 420, gx, 135, color="#e2e8f0", sw=1, dash="2,2"))
        f.append(text(gx, 435, lab, size=9, color=MUTED))

    grid_y = [(380, "0.001"), (320, "0.01"), (245, "0.04"), (180, "0.2")]
    for gy, lab in grid_y:
        f.append(line(80, gy, 485, gy, color="#e2e8f0", sw=1, dash="2,2"))
        f.append(text(75, gy + 3, lab, size=9, color=MUTED, anchor="end"))

    # Базовий профіль збудження MIL-STD-810H (трапеція)
    f.append('<polygon points="100,420 135,335 325,335 475,420" fill="#eff6ff" opacity="0.6"/>')
    f.append('<polyline points="100,420 135,335 325,335 475,420" fill="none" stroke="#2563eb" stroke-width="2"/>')
    f.append(text(230, 325, "Плато вхідного стенду: 0.04 g²/Hz", size=9.5, color="#1d4ed8", bold=True))
    f.append(text(130, 375, "+3 dB/oct", size=9, color="#2563eb"))
    f.append(text(420, 375, "−6 dB/oct", size=9, color="#2563eb"))

    # Резонансний відгук плати (передаточна функція з піками)
    res_path = [
        "M 100,418", "Q 115,365 135,332",
        "Q 155,310 165,260", "Q 185,150 195,150", "Q 205,150 220,285",  # f1 peak
        "Q 250,330 295,332",
        "Q 315,325 335,245", "Q 345,235 355,305",  # f2 peak
        "Q 395,365 475,418"
    ]
    f.append('<path d="%s" fill="none" stroke="#dc2626" stroke-width="2.5"/>' % " ".join(res_path))

    # Стрілка та маркер на f1
    f.append(circle(195, 150, 4.5, fill="#dc2626", stroke="#ffffff", sw=1.5))
    f.append(rect(205, 135, 175, 34, fill="#ffffff", stroke="#dc2626", sw=1, rx=3))
    f.append(text(292, 149, "Основний резонанс f₁ ≈ 140 Гц", size=9.5, color="#991b1b", bold=True))
    f.append(text(292, 161, "Добротність Q ≈ 15 (прогин плати)", size=9, color=MUTED))

    # Формула площі під кривою (g_rms)
    f.append(rect(90, 145, 95, 38, fill="#f8fafc", stroke="#64748b", sw=1, rx=3))
    f.append(text(137, 161, "g_rms = √(∫ PSD df)", size=9.5, color="#0f172a", bold=True))
    f.append(text(137, 174, "Сумарна енергія", size=9, color=MUTED))

    # Права панель: Механіка деформації плати та зріз пайки BGA
    f.append(rect(530, 75, 345, 395, fill="#fbfcfd", stroke="#94a3b8", sw=1.2, rx=6))
    f.append(text(702, 98, "Модальний прогин та напруження BGA", size=12, color="#1e293b", bold=True))

    # 1. Схема вигину плати на стійках
    f.append(rect(545, 115, 315, 135, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(702, 132, "Динамічний вигин у моді f₁", size=10, color="#334155", bold=True))

    # Опори (стійки кріплення)
    f.append(rect(560, 185, 18, 28, fill="#64748b", stroke="#334155", sw=1, rx=1))
    f.append(rect(826, 185, 18, 28, fill="#64748b", stroke="#334155", sw=1, rx=1))
    f.append(text(569, 227, "Стійка", size=9, color=MUTED))
    f.append(text(835, 227, "Стійка", size=9, color=MUTED))

    # Вигнута лінія друкованої плати (синусоїдальний прогин)
    f.append('<path d="M 569,185 Q 702,218 835,185" fill="none" stroke="#059669" stroke-width="3.5"/>')

    # BGA мікросхема по центру (найбільший градієнт кривини на краях)
    f.append(rect(660, 188, 85, 14, fill="#1e293b", stroke="#0f172a", sw=1, rx=1))
    f.append(text(702, 198, "BGA Корпус", size=9, color="#ffffff", bold=True))

    # Стрілки зсувних напружень на крайніх кульках BGA
    f.append(arrow(660, 203, 650, 210, color="#dc2626", sw=1.5))
    f.append(arrow(745, 203, 755, 210, color="#dc2626", sw=1.5))
    f.append(text(702, 158, "Максимальний прогин z(t)", size=9.5, color="#059669", bold=True))
    f.append(arrow(702, 164, 702, 202, color="#059669", sw=1.5))

    # 2. Збільшений зріз кутової кульки BGA (Detail view)
    f.append(rect(545, 260, 315, 195, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(702, 278, "Зріз паяного з'єднання (Pad Cratering)", size=10, color="#334155", bold=True))

    # Текстоліт друкованої плати знизу
    f.append(rect(560, 408, 285, 32, fill="#dcfce7", stroke="#15803d", sw=1.2, rx=2))
    f.append(text(702, 428, "Текстоліт друкованої плати (FR4)", size=9.5, color="#14532d", bold=True))

    # Мідний контактний майданчик (Pad)
    f.append(rect(655, 398, 95, 10, fill="#f97316", stroke="#c2410c", sw=1, rx=1))
    f.append(text(702, 406, "Мідний пад", size=9, color="#ffffff", bold=True))

    # Паяна кулька SAC305
    f.append('<ellipse cx="702.0" cy="358.0" rx="44.0" ry="36.0" fill="#e2e8f0" stroke="#475569" stroke-width="1.5"/>')
    f.append(text(702, 362, "SAC305", size=9.5, color="#334155", bold=True))

    # Корпус BGA зверху
    f.append(rect(645, 310, 115, 14, fill="#1e293b", stroke="#0f172a", sw=1, rx=1))
    f.append(text(702, 320, "Підкладка компонента", size=9, color="#ffffff"))

    # Тріщина втомного відриву (Pad cratering crack в FR4 під падом)
    f.append('<path d="M 655,408 Q 642,416 630,422 Q 648,428 665,422" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    f.append(text(595, 390, "Втомна тріщина", size=9, color="#dc2626", bold=True))
    f.append(text(595, 402, "у смолі FR4", size=9, color="#dc2626"))
    f.append(arrow(610, 405, 642, 417, color="#dc2626", sw=1.2))

    return "\n".join(f)


def main():
    figures = [
        ("halt-stress-margins-envelope.svg", fig_halt_stress_margins_envelope, 900, 520),
        ("vibration-resonance-spectral-density.svg", fig_vibration_resonance_spectral_density, 900, 500),
    ]
    for name, func, w, h in figures:
        p = os.path.join(OUT, name)
        content = func()
        render(p, w, h, content)
        print(f"Generated {p} ({w}x{h})")


if __name__ == "__main__":
    main()
