#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми one-stack-many-bodies (Один стек — багато тіл).
Вивід у ./img/
"""

import sys
import os
import math

# Шлях до scripts/ у корені репо (4 рівні вгору від теми: sys-dron -> sys -> root -> repo)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_architecture_layers():
    """Фігура 1: Уніфікована архітектура польотного стека з чітким шаром абстракції."""
    w, h = 880, 480
    elements = []
    
    # Фон
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Заголовок блоку уніфікованих рівнів (спільний для всіх планерів)
    elements.append(rect(30, 20, 520, 430, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    elements.append(text(290, 48, "УНІФІКОВАНІ ШАРИ СТЕКА (80% коду, спільні для всіх тіл)", size=12, color="#475569", bold=True))
    
    # Рівень 1: Давачі
    b1 = rect(50, 70, 480, 55, fill=FILL, stroke=LINE, sw=1.5, rx=6)
    elements.append(b1)
    elements.append(text(290, 93, "1. Первинна обробка та калібрування давачів", size=12, color=INK, bold=True))
    elements.append(text(290, 112, "IMU (акселерометр/гіроскоп), GNSS, магнітометр, барометр, трубка Піто", size=10, color=MUTED))
    
    # Стрілка 1 -> 2
    elements.append(arrow(290, 125, 290, 145, color=LINE, sw=1.5))
    
    # Рівень 2: Оцінювач стану
    b2 = rect(50, 145, 480, 55, fill=FILL, stroke=LINE, sw=1.5, rx=6)
    elements.append(b2)
    elements.append(text(290, 168, "2. Оцінювач навігаційного стану (EKF2 / EKF3)", size=12, color=INK, bold=True))
    elements.append(text(290, 187, "Позиція [x, y, z], швидкість [vx, vy, vz], кватерніон q, вітрове знесення", size=10, color=MUTED))
    
    # Стрілка 2 -> 3
    elements.append(arrow(290, 200, 290, 220, color=LINE, sw=1.5))
    
    # Рівень 3: Навігація та місії
    b3 = rect(50, 220, 480, 55, fill=FILL, stroke=LINE, sw=1.5, rx=6)
    elements.append(b3)
    elements.append(text(290, 243, "3. Навігація, місії та траєкторне планування", size=12, color=INK, bold=True))
    elements.append(text(290, 262, "Політ по точках, ведення по лінії шляху, орбіта, обхід перешкод", size=10, color=MUTED))
    
    # Стрілка 3 -> 4
    elements.append(arrow(290, 275, 290, 295, color=LINE, sw=1.5))
    
    # Рівень 4: Регулятори орієнтації
    b4 = rect(50, 295, 480, 60, fill=FILL, stroke=LINE, sw=1.5, rx=6)
    elements.append(b4)
    elements.append(text(290, 318, "4. Каскадні регулятори орієнтації та швидкостей", size=12, color=INK, bold=True))
    elements.append(text(290, 337, "Формування віртуального вектора зусиль τ = [F_x, F_y, F_z, M_x, M_y, M_z]ᵀ", size=10, color=POS, bold=True))
    
    # Інтерфейсна межа абстракції
    elements.append(rect(50, 375, 480, 60, fill="#fee2e2", stroke=POS, sw=1.8, rx=6))
    elements.append(text(290, 398, "ІНТЕРФЕЙС АБСТРАКЦІЇ ПЛАНЕРА", size=12, color=POS, bold=True))
    elements.append(text(290, 420, "Узагальнений вектор сил і моментів τ (Wrench) + стан переходу", size=10, color=INK))
    
    # Стрілка від абстракції до планерного шару
    elements.append(arrow(530, 405, 580, 405, color=POS, sw=2.2))
    
    # Правий блок: Планерно-залежний шар
    elements.append(rect(580, 20, 270, 430, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    elements.append(text(715, 48, "ПЛАНЕРНИЙ ШАР", size=12, color=FIELD, bold=True))
    elements.append(text(715, 68, "Control Allocation & Mixing", size=11, color=INK, bold=True))
    
    # Планерні адаптери
    types = [
        ("Мультиротор", "Диференціальна тяга N роторів", 100),
        ("Літак (Fixed-Wing)", "Елерони, рулі V/N + тяга тягача", 165),
        ("VTOL (QuadPlane)", "Гібрид: 4 підйомні + 1 маршовий", 230),
        ("VTOL (Tilt-Rotor)", "Поворотні мотори θ + рулі", 295),
        ("Ровер / Човен / UUV", "Диф. тяга / Ackermann / 6-DOF", 360)
    ]
    
    for title, desc, y_pos in types:
        elements.append(rect(595, y_pos, 240, 52, fill=FILL, stroke=LINE, sw=1.2, rx=5))
        elements.append(text(715, y_pos + 20, title, size=11, color=INK, bold=True))
        elements.append(text(715, y_pos + 38, desc, size=9, color=MUTED))
    
    # Збірка SVG
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'architecture-layers.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_airframe_physics():
    """Фігура 2: Фізичні механізми створення сил і моментів на 4 типах планерів."""
    w, h = 880, 420
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    panels = [
        ("Мультиротор (Multi-Rotor)", 20, 20, [
            "Пряме векторне керування",
            "• Вертикальна тяга: F_z = -Σ T_i",
            "• Крен/Тангаж: різниця тяг роторів",
            "• Рискання: реактивний крутний момент",
            "• Статично нестійкий без обертання",
            "• Частота контуру: 400..1000 Гц"
        ], "#dbeafe", NEG),
        ("Літак (Fixed-Wing)", 450, 20, [
            "Аеродинамічні сили крила й рулів",
            "• Підйомна сила: L = 0.5·ρ·V²·S·C_L",
            "• Крен: елерони (δ_a)",
            "• Тангаж: кермо висоти (δ_e)",
            "• Рискання: кермо напрямку (δ_r)",
            "• Ефективність рулів росте з V²"
        ], "#fef3c7", "#b45309"),
        ("VTOL QuadPlane (SLT)", 20, 220, [
            "Роздільна тяга (Separate Lift-Thrust)",
            "• 4 несучі ротори для зависання",
            "• 1 штовхаючий/тягнучий маршовий",
            "• Перехід: плавне вимикання роторів",
            "• Проста логіка, але вага й опір",
            "• Стабільне зависання у вітрі"
        ], "#dcfce7", FIELD),
        ("VTOL Tilt-Rotor / Tailsitter", 450, 220, [
            "Векторизація тяги (Vectored Thrust)",
            "• Поворот мотора/крила на кут θ",
            "• Зависання: θ = 90° (вертикаль)",
            "• Крейсер: θ = 0° (горизонт)",
            "• Висока енергоефективність",
            "• Складний нелінійний мікшер"
        ], "#f3e8ff", "#7e22ce")
    ]
    
    for title, x_pos, y_pos, lines, fill_color, stroke_color in panels:
        elements.append(rect(x_pos, y_pos, 410, 180, fill=fill_color, stroke=stroke_color, sw=1.5, rx=8))
        elements.append(text(x_pos + 205, y_pos + 28, title, size=13, color=INK, bold=True))
        y_text = y_pos + 56
        for line in lines:
            elements.append(text(x_pos + 20, y_text, line, size=11, color=INK, anchor="start"))
            y_text += 22
            
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'airframe-physics-comparison.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_vtol_transition():
    """Фігура 3: Динаміка перехідного режиму VTOL — криві швидкості, підйомної сили та ваги блендингу."""
    w, h = 880, 430
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Заголовок
    elements.append(text(440, 30, "Динаміка прямого переходу VTOL: Hover → Transition → Fixed-Wing Cruise", size=13, color=INK, bold=True))
    
    # Область графіків
    ox, oy = 75, 340
    gw, gh = 700, 260
    
    # Тло координатної сітки
    elements.append(rect(ox, oy - gh, gw, gh, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    
    # Вертикальні зони
    # Зона 1: Hover (0 .. 170)
    elements.append(rect(ox, oy - gh, 170, gh, fill="#eff6ff", stroke="none"))
    elements.append(text(ox + 85, oy - gh + 22, "1. Зависання (Hover)", size=11, color=NEG, bold=True))
    elements.append(text(ox + 85, oy - gh + 40, "V_ias < V_min", size=10, color=MUTED))
    
    # Зона 2: Transition Blending (170 .. 490)
    elements.append(rect(ox + 170, oy - gh, 320, gh, fill="#fefce8", stroke="none"))
    elements.append(text(ox + 330, oy - gh + 22, "2. Перехідна фаза (Transition Blending)", size=11, color="#b45309", bold=True))
    elements.append(text(ox + 330, oy - gh + 40, "V_min ≤ V_ias ≤ V_trans (перерозподіл ваги)", size=10, color=MUTED))
    
    # Зона 3: Fixed-Wing Cruise (490 .. 700)
    elements.append(rect(ox + 490, oy - gh, 210, gh, fill="#f0fdf4", stroke="none"))
    elements.append(text(ox + 595, oy - gh + 22, "3. Літаковий політ (FW)", size=11, color=FIELD, bold=True))
    elements.append(text(ox + 595, oy - gh + 40, "V_ias > V_trans (ротори стоп)", size=10, color=MUTED))
    
    # Межі швидкостей (штрихові лінії)
    elements.append(line(ox + 170, oy - gh, ox + 170, oy, color="#94a3b8", sw=1.5, dash="4,4"))
    elements.append(line(ox + 350, oy - gh, ox + 350, oy, color=POS, sw=1.5, dash="4,4"))
    elements.append(line(ox + 490, oy - gh, ox + 490, oy, color=FIELD, sw=1.5, dash="4,4"))
    
    elements.append(text(ox + 170, oy + 18, "V_min", size=10, color=INK, bold=True))
    elements.append(text(ox + 350, oy + 18, "V_stall", size=10, color=POS, bold=True))
    elements.append(text(ox + 490, oy + 18, "V_trans", size=10, color=FIELD, bold=True))
    
    # Вісь часу / швидкості
    elements.append(arrow(ox, oy, ox + gw + 15, oy, color=LINE, sw=1.5))
    elements.append(text(ox + gw - 40, oy + 22, "Час t, швидкість V_ias", size=10, color=INK, anchor="end"))
    
    # Вісь зусиль
    elements.append(arrow(ox, oy, ox, oy - gh - 15, color=LINE, sw=1.5))
    elements.append(text(ox - 30, oy - gh + 5, "1.0", size=10, color=INK))
    elements.append(text(ox - 30, oy - gh/2, "0.5", size=10, color=INK))
    elements.append(text(ox - 30, oy, "0.0", size=10, color=INK))
    
    # Крива 1: Тяга підйомних моторів T_hover (синя лінія: 1.0 -> 0.0)
    path_hover = (
        f"M {ox} {oy - 190} "
        f"L {ox + 170} {oy - 190} "
        f"C {ox + 260} {oy - 180}, {ox + 390} {oy - 45}, {ox + 490} {oy} "
        f"L {ox + gw} {oy}"
    )
    elements.append(f'<path d="{path_hover}" fill="none" stroke="{NEG}" stroke-width="3"/>')
    elements.append(text(ox + 85, oy - 202, "Тяга роторів T_hover", size=10, color=NEG, bold=True))
    
    # Крива 2: Аеродинамічна підйомна сила крила L (зелена параболічна лінія)
    path_lift = (
        f"M {ox} {oy} "
        f"L {ox + 170} {oy} "
        f"C {ox + 260} {oy - 10}, {ox + 390} {oy - 145}, {ox + 490} {oy - 190} "
        f"L {ox + gw} {oy - 190}"
    )
    elements.append(f'<path d="{path_lift}" fill="none" stroke="{FIELD}" stroke-width="3"/>')
    elements.append(text(ox + 595, oy - 202, "Підйомна сила L(V²)", size=10, color=FIELD, bold=True))
    
    # Крива 3: Ваговий коефіцієнт блендингу w_fw (пурпурова штрихова)
    path_w = (
        f"M {ox} {oy} "
        f"L {ox + 170} {oy} "
        f"L {ox + 490} {oy - 190} "
        f"L {ox + gw} {oy - 190}"
    )
    elements.append(f'<path d="{path_w}" fill="none" stroke="#9333ea" stroke-width="2" stroke-dasharray="6,4"/>')
    
    # Напис w_fw розміщуємо у вільному місці вгорі зони переходу
    elements.append(text(ox + 330, oy - gh + 65, "Вага блендингу w_fw (пурпур)", size=10, color="#9333ea", bold=True))
    
    # Пояснення знизу
    elements.append(text(440, 395, "Сума T_hover + L(V) = m·g підтримує постійну висоту під час усього переходу", size=11, color=INK, italic=True))
    
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'vtol-transition-dynamics.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


def fig_allocation_matrix():
    """Фігура 4: Геометрична побудова матриці ефективності B та каскад пріоритетної десатурації."""
    w, h = 880, 380
    elements = []
    
    elements.append(rect(0, 0, w, h, fill=BG, stroke="none", rx=0))
    
    # Ліва частина: Матриця B для VTOL
    elements.append(rect(20, 20, 440, 340, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    elements.append(text(240, 48, "Узагальнена матриця ефективності B(θ, V)", size=13, color=INK, bold=True))
    
    # Таблиця компонентів B
    headers = ["Вісь", "Ротори 1..4", "Маршовий", "Елерони", "Р.Висоти", "Р.Напрямку"]
    hx = [35, 105, 185, 260, 330, 400]
    
    elements.append(rect(30, 70, 420, 25, fill="#e2e8f0", stroke=LINE, sw=1))
    for i, name in enumerate(headers):
        elements.append(text(hx[i] + 15, 87, name, size=9, color=INK, bold=True))
        
    rows = [
        ("F_x", "0 (або T·sinθ)", "c_t,push", "0", "0", "0"),
        ("F_y", "0", "0", "0", "0", "c_L,rudder"),
        ("F_z", "-c_t,i·cosθ", "0", "0", "0", "0"),
        ("M_x", "y_i·F_z,i", "0", "c_roll·q", "0", "0"),
        ("M_y", "-x_i·F_z,i", "z_push·F_x", "0", "c_pitch·q", "0"),
        ("M_z", "d_i·c_m,i", "0", "0", "0", "c_yaw·q")
    ]
    
    ry = 115
    for axis, r_rot, r_push, r_ail, r_elev, r_rud in rows:
        elements.append(rect(30, ry - 15, 420, 24, fill="#ffffff" if (ry // 24) % 2 == 0 else "#f8fafc", stroke="#cbd5e1", sw=0.8))
        elements.append(text(hx[0] + 15, ry, axis, size=10, color=POS, bold=True))
        elements.append(text(hx[1] + 15, ry, r_rot, size=9, color=INK))
        elements.append(text(hx[2] + 15, ry, r_push, size=9, color=INK))
        elements.append(text(hx[3] + 15, ry, r_ail, size=9, color=FIELD))
        elements.append(text(hx[4] + 15, ry, r_elev, size=9, color=FIELD))
        elements.append(text(hx[5] + 15, ry, r_rud, size=9, color=FIELD))
        ry += 24
        
    elements.append(text(240, 275, "q = 0.5·ρ·V_ias² — динамічний швидкісний напір", size=10, color=FIELD, bold=True))
    elements.append(text(240, 295, "θ — кут нахилу поворотних балок (Tilt-Rotor)", size=10, color=NEG, bold=True))
    elements.append(text(240, 335, "Розв'язання: u_raw = B⁺ · τ_sp (псевдообернення)", size=11, color=INK, italic=True))
    
    # Права частина: Сходи пріоритетів десатурації
    elements.append(rect(480, 20, 380, 340, fill="#fdf4ff", stroke="#a855f7", sw=1.5, rx=8))
    elements.append(text(670, 48, "Драбина пріоритетів десатурації (Sat Ladder)", size=12, color="#7e22ce", bold=True))
    
    ladder = [
        ("1. Стабілізація Roll / Pitch (M_x, M_y)", "Найвищий пріоритет: збереження просторової орієнтації", "#fee2e2", POS),
        ("2. Вертикальна тяга / Висота (F_z)", "Утримання висоти: жертвуємо швидкістю заради висоти", "#fef3c7", "#b45309"),
        ("3. Рискання / Курс (M_z)", "Утримання носа: при дефіциті тяги дозволяється дрейф курсу", "#e0f2fe", NEG),
        ("4. Маршова тяга / Прискорення (F_x)", "Найнижчий пріоритет: зниження газу для порятунку балансу", "#f1f5f9", MUTED)
    ]
    
    ly = 85
    for title, desc, bg_c, strk_c in ladder:
        elements.append(rect(500, ly, 340, 56, fill=bg_c, stroke=strk_c, sw=1.3, rx=6))
        elements.append(text(670, ly + 20, title, size=11, color=INK, bold=True))
        elements.append(text(670, ly + 40, desc, size=9, color=MUTED))
        ly += 68
        
    defs = '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#333333"/></marker></defs>'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n%s\n%s\n</svg>'
           % (w, h, w, h, defs, "\n".join(elements)))
    
    path = os.path.join(IMG_DIR, 'dynamic-allocation-matrix.svg')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Generated {path}")


if __name__ == '__main__':
    fig_architecture_layers()
    fig_airframe_physics()
    fig_vtol_transition()
    fig_allocation_matrix()
