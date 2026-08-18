# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_premature_abstraction_trap(filepath):
    elements = []
    
    # Title / Header background panel
    elements.append(rect(15, 15, 770, 410, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=8))
    
    # Left Box: Healthy Platform (Paved Road / Golden Path)
    elements.append(rect(30, 40, 360, 360, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    elements.append(text(210, 68, "Зріла платформа (Golden Path)", size=14, color="#15803d", bold=True))
    
    b1, _, _ = textbox(210, 115, "Stream-aligned Команда\n(Фокус на доменній логіці)", size=12, pad=10, fill="#ffffff", stroke="#16a34a", bold=True, min_w=280)
    elements.append(b1)
    
    elements.append(arrow(210, 150, 210, 195, color="#15803d", sw=2))
    elements.append(text(215, 175, "Самообслуговування", size=10, color="#15803d", bold=True, anchor="start"))
    
    b2, _, _ = textbox(210, 235, "Thinnest Viable Platform (TVP)\n• Готові IaC-шаблони та CI-пайплайни\n• Опціональне використання\n• Прямий доступ до примітивів", size=11, pad=10, fill="#e0f2fe", stroke="#0284c7", min_w=300)
    elements.append(b2)
    
    elements.append(arrow(210, 280, 210, 315, color="#0284c7", sw=2))
    
    b3, _, _ = textbox(210, 350, "Інфраструктурні примітиви\n(Cloud, K8s, DBs, Observability)", size=11, pad=8, fill="#ffffff", stroke="#475569", min_w=280)
    elements.append(b3)
    
    # Right Box: Premature Abstraction (Tollgate / Bottleneck)
    elements.append(rect(410, 40, 360, 360, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    elements.append(text(590, 68, "Передчасна платформа (Tollgate)", size=14, color="#b91c1c", bold=True))
    
    b4, _, _ = textbox(590, 115, "Stream-aligned Команда\n(Заблокована абстракцією)", size=12, pad=10, fill="#ffffff", stroke="#dc2626", bold=True, min_w=280)
    elements.append(b4)
    
    elements.append(arrow(590, 150, 590, 195, color="#b91c1c", sw=2))
    elements.append(text(595, 175, "Черги в Jira / Блокування", size=10, color="#b91c1c", bold=True, anchor="start"))
    
    b5, _, _ = textbox(590, 235, "Передчасний IDP-шлагбаум\n• Незрілі жорсткі CRD / CLI-обгортки\n• Обов'язкове узгодження змін\n• Неможливість вийти за межі", size=11, pad=10, fill="#fef3c7", stroke="#d97706", min_w=300)
    elements.append(b5)
    
    elements.append(arrow(590, 280, 590, 315, color="#d97706", sw=2))
    elements.append(text(600, 300, "Дірява абстракція", size=10, color="#dc2626", bold=True, anchor="start"))
    
    b6, _, _ = textbox(590, 350, "Тіньова інфраструктура (Shadow IT)\n(Побічні рішення в обхід платформи)", size=11, pad=8, fill="#ffffff", stroke="#991b1b", min_w=280)
    elements.append(b6)
    
    return render(filepath, 800, 440, *elements, title="Еволюційний спектр платформи: Golden Path проти Tollgate")


def generate_platform_roi_break_even(filepath):
    elements = []
    
    # Outer frame
    elements.append(rect(15, 15, 770, 390, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    
    # Graph Axes
    # X axis (Number of Stream-aligned Teams N)
    elements.append(line(80, 330, 730, 330, color="#475569", sw=2))
    elements.append(arrow(720, 330, 740, 330, color="#475569", sw=2))
    elements.append(text(745, 334, "Команди (N)", size=11, color="#334155", bold=True, anchor="start"))
    
    # Y axis (Cost / Value in arbitrary units)
    elements.append(line(80, 330, 80, 50, color="#475569", sw=2))
    elements.append(arrow(80, 60, 80, 40, color="#475569", sw=2))
    elements.append(text(80, 30, "Економічний ефект (Вартість / Економія)", size=11, color="#334155", bold=True, anchor="middle"))
    
    # Grid lines & Team markers on X axis
    team_points = [(150, "1-2"), (270, "3-4"), (420, "5-7"), (570, "8-12"), (690, "15+")]
    for x_pos, label in team_points:
        elements.append(line(x_pos, 325, x_pos, 335, color="#94a3b8", sw=1.5))
        elements.append(text(x_pos, 350, label, size=11, color="#64748b", bold=True))
    
    # Curve 1: Platform Overhead Cost (Fixed + slight growth) -> Red line
    pts1 = [(80, 290), (200, 270), (420, 250), (700, 220)]
    for i in range(len(pts1)-1):
        elements.append(line(pts1[i][0], pts1[i][1], pts1[i+1][0], pts1[i+1][1], color="#dc2626", sw=2.5))
    elements.append(text(620, 210, "Витрати на платформу (C_p)", size=11, color="#dc2626", bold=True, anchor="start"))
    
    # Curve 2: Value / Velocity Savings across N teams -> Green line
    pts2 = [(80, 320), (200, 300), (350, 250), (420, 210), (570, 130), (700, 70)]
    for i in range(len(pts2)-1):
        elements.append(line(pts2[i][0], pts2[i][1], pts2[i+1][0], pts2[i+1][1], color="#16a34a", sw=3))
    elements.append(text(640, 60, "Економія часу розробки (S_s)", size=11, color="#16a34a", bold=True, anchor="start"))
    
    # Intersection / Break-even point at X=420, Y=250
    elements.append(circle(420, 250, 7, fill="#f59e0b", stroke="#b45309", sw=2))
    elements.append(line(420, 250, 420, 330, color="#d97706", sw=1.5, dash="3,3"))
    
    # Annotation for Break-even Point
    b_be, _, _ = textbox(420, 175, "Точка окупності IDP\n(N ≈ 5 команд)", size=11, pad=6, fill="#fef3c7", stroke="#d97706", bold=True, min_w=150)
    elements.append(b_be)
    
    # Shaded Zones: Left = Deficit / Premature; Right = Positive ROI
    elements.append(rect(90, 60, 250, 40, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=4))
    elements.append(text(215, 84, "Зона передчасної платформи\n(Чисті збитки та оверхед)", size=11, color="#991b1b", bold=True))
    
    elements.append(rect(480, 260, 240, 40, fill="#dcfce7", stroke="#86efac", sw=1, rx=4))
    elements.append(text(600, 284, "Зона високої окупності IDP\n(Масштабування продуктивності)", size=11, color="#166534", bold=True))
    
    return render(filepath, 800, 400, *elements, title="Економіка платформи: крива окупності залежно від кількості команд")


def generate_golden_path_vs_tollgate(filepath):
    elements = []
    
    # Outer container
    elements.append(rect(15, 15, 770, 370, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=8))
    
    # Top subtitle
    elements.append(text(400, 45, "Порівняння архітектурних режимів доступності інфраструктури", size=14, color="#1e293b", bold=True))
    
    # Column 1: Golden Path (Paved Road)
    elements.append(rect(35, 70, 350, 290, fill="#f8fafc", stroke="#0284c7", sw=1.5, rx=6))
    elements.append(text(210, 98, "Асфальтована дорога (Golden Path)", size=13, color="#0369a1", bold=True))
    
    items_gp = [
        "• Самообслуговування через CLI / API / Portal",
        "• Опціональність: дорога за замовчуванням зручна",
        "• Право на вихід у 'оффроуд' з власною відповідальністю",
        "• Висока швидкість релізів (хвилини замість днів)",
        "• Платформа як внутрішній продукт з володінням"
    ]
    y_curr = 130
    for item in items_gp:
        elements.append(text(50, y_curr, item, size=10.5, color="#334155", anchor="start"))
        y_curr += 44
        
    # Column 2: Tollgate (Шлагбаум)
    elements.append(rect(415, 70, 350, 290, fill="#fffafb", stroke="#e11d48", sw=1.5, rx=6))
    elements.append(text(590, 98, "Обов'язковий шлагбаум (Tollgate)", size=13, color="#be123c", bold=True))
    
    items_tg = [
        "• Бюрократичне узгодження через ручні тікети",
        "• Примусовість: заборона будь-яких власних рішень",
        "• Жорсткі некоректні абстракції без виходів",
        "• Затримка релізів та накопичення черг передачі",
        "• Платформа як адміністративний контроль"
    ]
    y_curr = 130
    for item in items_tg:
        elements.append(text(430, y_curr, item, size=10.5, color="#334155", anchor="start"))
        y_curr += 44
        
    return render(filepath, 800, 400, *elements, title="Характеристики Golden Path проти Tollgate")


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    generate_premature_abstraction_trap(os.path.join(img_dir, "premature-abstraction-trap.svg"))
    generate_platform_roi_break_even(os.path.join(img_dir, "platform-roi-break-even.svg"))
    generate_golden_path_vs_tollgate(os.path.join(img_dir, "golden-path-vs-tollgate.svg"))
    
    print("SVGs generated successfully in img/")

if __name__ == "__main__":
    main()
