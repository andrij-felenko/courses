# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_team_topologies_dh(filepath):
    elements = []
    
    # 1. Stream-aligned Team 1
    sa1_box, _, _ = textbox(210, 115, "Stream-aligned: Цифровий двійник і керування\n(Домени: Control.Device, Twin, Command Routing)", size=13, pad=12, fill="#e8f4fc", stroke="#2980b9", bold=True, min_w=370)
    elements.append(sa1_box)
    
    # 2. Stream-aligned Team 2
    sa2_box, _, _ = textbox(610, 115, "Stream-aligned: Автоматизації та сценарії\n(Домени: Rules Engine, Triggers, Scenes)", size=13, pad=12, fill="#e8f4fc", stroke="#2980b9", bold=True, min_w=370)
    elements.append(sa2_box)
    
    # 3. Complicated-subsystem Team
    sub_box, _, _ = textbox(410, 220, "Complicated-subsystem: Відео та медіа-стрімінг\n(H.264/H.265 кодеки, WebRTC, RTSP, WASM-плеєр)", size=13, pad=12, fill="#fef9e7", stroke="#f39c12", bold=True, min_w=770)
    elements.append(sub_box)
    
    # 4. Enabling Team
    ena_box, _, _ = textbox(210, 325, "Enabling: Безпека та стійкість системи\n(Threat modeling, Chaos testing, Fuzzing, Authz)", size=13, pad=12, fill="#f4ecf7", stroke="#8e44ad", bold=True, min_w=370)
    elements.append(ena_box)
    
    # 5. Platform Team
    plat_box, _, _ = textbox(610, 325, "Platform: Інфраструктура IoT та Golden Path\n(MQTT брокер, Telemetry DB, CI/CD, IDP portal)", size=13, pad=12, fill="#e8f8f5", stroke="#16a085", bold=True, min_w=370)
    elements.append(plat_box)
    
    # Connectors & Interaction annotations
    # Vertical Platform -> Stream-aligned Team 2
    elements.append(arrow(610, 280, 610, 160, color=FIELD, sw=2))
    elements.append(text(620, 215, "X-as-a-Service", size=11, color=FIELD, anchor="start", bold=True))
    
    # Platform -> Stream-aligned Team 1
    elements.append(arrow(430, 290, 230, 160, color=FIELD, sw=2))
    elements.append(text(370, 255, "X-as-a-Service", size=11, color=FIELD, anchor="start", bold=True))
    
    # Enabling -> Stream Team 1 (line at x=100)
    elements.append(line(100, 290, 100, 160, color="#8e44ad", sw=2, dash="5,5"))
    elements.append(text(108, 225, "Facilitating (тимчасово)", size=11, color="#8e44ad", anchor="start", italic=True))
    
    # Legend
    elements.append(rect(25, 400, 770, 45, fill="#fafafa", stroke="#d6dbdf", sw=1, rx=4))
    elements.append(circle(50, 422, 6, fill="#e8f4fc", stroke="#2980b9"))
    elements.append(text(63, 426, "Stream-aligned", size=11, anchor="start", bold=True))
    
    elements.append(circle(210, 422, 6, fill="#e8f8f5", stroke="#16a085"))
    elements.append(text(223, 426, "Platform", size=11, anchor="start", bold=True))
    
    elements.append(circle(330, 422, 6, fill="#f4ecf7", stroke="#8e44ad"))
    elements.append(text(343, 426, "Enabling", size=11, anchor="start", bold=True))
    
    elements.append(circle(460, 422, 6, fill="#fef9e7", stroke="#f39c12"))
    elements.append(text(473, 426, "Complicated-subsystem", size=11, anchor="start", bold=True))
    
    elements.append(line(640, 422, 670, 422, color=FIELD, sw=2))
    elements.append(text(675, 426, "X-as-a-Service", size=10, anchor="start"))
    
    return render(filepath, 820, 460, *elements, title="Топологія команд Digital Homes (Team Topologies)")


def generate_interaction_modes(filepath):
    elements = []
    
    # Mode 1: X-as-a-Service
    elements.append(rect(20, 60, 240, 290, fill="#f9f9f9", stroke="#cccccc", sw=1, rx=6))
    elements.append(text(140, 85, "1. X-as-a-Service", size=14, color=FIELD, bold=True))
    b1, _, _ = textbox(140, 140, "Stream Team\n(Споживач)", size=12, pad=8, fill="#e8f4fc", stroke="#2980b9")
    elements.append(b1)
    b2, _, _ = textbox(140, 260, "Platform Team\n(Постачальник)", size=12, pad=8, fill="#e8f8f5", stroke="#16a085")
    elements.append(b2)
    elements.append(arrow(140, 220, 140, 180, color=FIELD, sw=2.5))
    elements.append(text(140, 205, "Self-service API", size=11, color=FIELD, bold=True))
    elements.append(text(140, 325, "Чіткий SLA / Декларативність\nБез синхронних нарад", size=11, color=MUTED))
    
    # Mode 2: Facilitating
    elements.append(rect(280, 60, 240, 290, fill="#f9f9f9", stroke="#cccccc", sw=1, rx=6))
    elements.append(text(400, 85, "2. Facilitating", size=14, color="#8e44ad", bold=True))
    b3, _, _ = textbox(400, 140, "Stream Team\n(Практик)", size=12, pad=8, fill="#e8f4fc", stroke="#2980b9")
    elements.append(b3)
    b4, _, _ = textbox(400, 260, "Enabling Team\n(Ментор / Експерт)", size=12, pad=8, fill="#f4ecf7", stroke="#8e44ad")
    elements.append(b4)
    elements.append(line(400, 220, 400, 180, color="#8e44ad", sw=2, dash="4,4"))
    elements.append(text(400, 205, "Навчання / Впровадження", size=11, color="#8e44ad", bold=True))
    elements.append(text(400, 325, "Тимчасова участь (2-4 тижні)\nПередача знань у Stream", size=11, color=MUTED))
    
    # Mode 3: Collaboration
    elements.append(rect(540, 60, 240, 290, fill="#f9f9f9", stroke="#cccccc", sw=1, rx=6))
    elements.append(text(660, 85, "3. Collaboration", size=14, color=POS, bold=True))
    b5, _, _ = textbox(660, 140, "Stream Team A", size=12, pad=8, fill="#e8f4fc", stroke="#2980b9")
    elements.append(b5)
    b6, _, _ = textbox(660, 260, "Stream Team B / Subsystem", size=12, pad=8, fill="#fef9e7", stroke="#f39c12")
    elements.append(b6)
    elements.append(rect(590, 182, 140, 36, fill="#fdedec", stroke=POS, sw=1.5, rx=4))
    elements.append(text(660, 204, "Спільне відкриття", size=11, color=POS, bold=True))
    elements.append(text(660, 325, "Високий контекстний зв'язок\nОбов'язковий дедлайн виходу", size=11, color=MUTED))
    
    return render(filepath, 800, 380, *elements, title="Три режими взаємодії команд у Team Topologies")


def generate_cognitive_load_split(filepath):
    elements = []
    
    # Left: Monolithic functional silos
    elements.append(rect(30, 60, 340, 275, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=6))
    elements.append(text(200, 85, "До Team Topologies (Перевантаження)", size=13, color=POS, bold=True))
    
    # Stacked bar 1
    elements.append(rect(100, 110, 200, 110, fill="#fadbd8", stroke="#e74c3c", sw=1))
    elements.append(text(200, 165, "Стороннє (65%)\nK8s, IAM, YAML, CI/CD, DB ops", size=11, color="#78281f", bold=True))
    
    elements.append(rect(100, 220, 200, 40, fill="#fdebd0", stroke="#f39c12", sw=1))
    elements.append(text(200, 244, "Внутрішнє (20%) Мова/Синтаксис", size=10, color="#7e5109"))
    
    elements.append(rect(100, 260, 200, 30, fill="#d4efdf", stroke="#27ae60", sw=1))
    elements.append(text(200, 279, "Доречне (15%) Логіка домену", size=10, color="#145a32", bold=True))
    
    elements.append(text(200, 315, "Результат: вигорання, затримки релізів", size=11, color=POS, italic=True))
    
    # Right: Stream-aligned + Platform paved road
    elements.append(rect(410, 60, 340, 275, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=6))
    elements.append(text(580, 85, "Після Team Topologies + Golden Path", size=13, color=FIELD, bold=True))
    
    # Stacked bar 2
    elements.append(rect(480, 110, 200, 30, fill="#fadbd8", stroke="#e74c3c", sw=1))
    elements.append(text(580, 129, "Стороннє (15%) Self-service", size=10, color="#78281f"))
    
    elements.append(rect(480, 140, 200, 40, fill="#fdebd0", stroke="#f39c12", sw=1))
    elements.append(text(580, 164, "Внутрішнє (25%) Код та мова", size=10, color="#7e5109"))
    
    elements.append(rect(480, 180, 200, 110, fill="#d4efdf", stroke="#27ae60", sw=1))
    elements.append(text(580, 235, "Доречне (60%)\nІнваріанти домену та продукту", size=11, color="#145a32", bold=True))
    
    elements.append(text(580, 315, "Результат: фокус на цінності для клієнта", size=11, color=FIELD, italic=True))
    
    return render(filepath, 780, 360, *elements, title="Когнітивне навантаження команди інженерів Digital Homes")


def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    
    generate_team_topologies_dh(os.path.join(img_dir, "team-topologies-dh.svg"))
    generate_interaction_modes(os.path.join(img_dir, "interaction-modes.svg"))
    generate_cognitive_load_split(os.path.join(img_dir, "cognitive-load-split.svg"))
    
    print("SVGs generated successfully in img/")

if __name__ == "__main__":
    main()
