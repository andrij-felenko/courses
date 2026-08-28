# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_control_plane():
    W, H = 820, 460
    p = []
    
    # Header & Zones
    p.append(rect(15, 15, 245, 430, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(137, 42, "ВЕБ-ПАНЕЛЬ (UI)", size=14, color=INK, bold=True))
    p.append(text(137, 60, "Операторський браузер", size=11, color=MUTED))

    p.append(rect(285, 15, 250, 430, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(410, 42, "СЕРВЕР КЕРУВАННЯ", size=14, color=INK, bold=True))
    p.append(text(410, 60, "FastAPI / WebSocket / Mailbox", size=11, color=MUTED))

    p.append(rect(560, 15, 245, 430, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(682, 42, "ПРИСТРІЙ / ВУЗОЛ", size=14, color=INK, bold=True))
    p.append(text(682, 60, "Firmware (ESP32 / RTOS)", size=11, color=MUTED))

    # Blocks in UI
    p.append(rect(30, 85, 215, 65, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(137, 112, "Віджет керування", size=13, color=INK, bold=True))
    p.append(text(137, 134, "Стан: IDLE → PENDING → OK", size=11, color=MUTED))

    p.append(rect(30, 175, 215, 65, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(137, 202, "WebSocket Client", size=13, color=INK, bold=True))
    p.append(text(137, 224, "Команди, стрім телеметрії", size=11, color=MUTED))

    p.append(rect(30, 265, 215, 65, fill="#ffffff", stroke=POS, sw=1.5))
    p.append(text(137, 292, "Панель тривог (Alarms)", size=13, color=POS, bold=True))
    p.append(text(137, 314, "Квитування оператором", size=11, color=MUTED))

    p.append(rect(30, 355, 215, 70, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(137, 382, "Command Tracker", size=13, color=INK, bold=True))
    p.append(text(137, 404, "UUID, таймаути, історія", size=11, color=MUTED))

    # Blocks in Server
    p.append(rect(300, 85, 220, 65, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(410, 112, "WS & REST Ingest", size=13, color=INK, bold=True))
    p.append(text(410, 134, "Валідація JWT та прав RBAC", size=11, color=MUTED))

    p.append(rect(300, 175, 220, 65, fill="#eafaf0", stroke=FIELD, sw=1.5))
    p.append(text(410, 202, "Mailbox / Downlink Queue", size=13, color=FIELD, bold=True))
    p.append(text(410, 224, "TTL, черга сплячих вузлів", size=11, color=MUTED))

    p.append(rect(300, 265, 220, 65, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(410, 292, "State & Alarm Engine", size=13, color=INK, bold=True))
    p.append(text(410, 314, "Облік статусів виконання", size=11, color=MUTED))

    p.append(rect(300, 355, 220, 70, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(410, 382, "MQTT / Radio Bridge", size=13, color=INK, bold=True))
    p.append(text(410, 404, "Публікація cmd/{id}/req", size=11, color=MUTED))

    # Blocks in Device
    p.append(rect(575, 85, 215, 65, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(682, 112, "Network Dispatcher", size=13, color=INK, bold=True))
    p.append(text(682, 134, "MQTT / Сокет / Підписка", size=11, color=MUTED))

    p.append(rect(575, 175, 215, 65, fill="#eaf0fd", stroke=NEG, sw=1.5))
    p.append(text(682, 202, "Дедуплікатор і TTL", size=13, color=NEG, bold=True))
    p.append(text(682, 224, "Кільцевий буфер Command ID", size=11, color=MUTED))

    p.append(rect(575, 265, 215, 65, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(682, 292, "Апаратний виконавець", size=13, color=INK, bold=True))
    p.append(text(682, 314, "Реле, ШІМ, сервопривід", size=11, color=MUTED))

    p.append(rect(575, 355, 215, 70, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(682, 382, "Status & ACK Reporter", size=13, color=INK, bold=True))
    p.append(text(682, 404, "Квитування ACK та EXEC", size=11, color=MUTED))

    # Inter-zone connections
    # UI to Server: Command Downlink
    p.append(arrow(245, 117, 300, 117, color=NEG, sw=2))
    p.append(text(272, 107, "Команда", size=10, color=NEG, bold=True))

    # Server to UI: Status Updates & Telemetry
    p.append(arrow(300, 207, 245, 207, color=FIELD, sw=2))
    p.append(text(272, 197, "WS стрім", size=10, color=FIELD, bold=True))

    # Server to Device: MQTT Downlink
    p.append(arrow(520, 390, 575, 390, color=NEG, sw=2))
    p.append(text(547, 380, "cmd/req", size=10, color=NEG, bold=True))

    # Device to Server: ACK & Status
    p.append(arrow(575, 117, 520, 117, color=FIELD, sw=2))
    p.append(text(547, 107, "cmd/ack", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "dashboard-control-plane.svg"), W, H, *p)


def fig_two_phase_ack():
    W, H = 800, 430
    p = []

    # Columns (Lifelines)
    ui_x = 100
    srv_x = 350
    dev_x = 650

    p.append(line(ui_x, 60, ui_x, 400, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(srv_x, 60, srv_x, 400, color=MUTED, sw=1.5, dash="4 4"))
    p.append(line(dev_x, 60, dev_x, 400, color=MUTED, sw=1.5, dash="4 4"))

    p.append(fitbox(ui_x - 70, 20, 140, 36, "Веб-панель (UI)", size=13, bold=True, fill="#eaf0fd", stroke=NEG))
    p.append(fitbox(srv_x - 70, 20, 140, 36, "Бекенд / Брокер", size=13, bold=True, fill="#f4f6f8", stroke=LINE))
    p.append(fitbox(dev_x - 70, 20, 140, 36, "Вузол (Залізо)", size=13, bold=True, fill="#eafaf0", stroke=FIELD))

    # Step 1: User click -> send cmd
    y = 80
    p.append(arrow(ui_x, y, srv_x, y + 25, color=INK, sw=1.8))
    p.append(text((ui_x + srv_x) / 2, y + 8, "1. POST /command (UUID, op, params)", size=11, color=INK))
    p.append(text(ui_x - 8, y + 20, "UI: PENDING", size=10, color=MUTED, anchor="end", bold=True))

    # Step 2: Server forward to device
    y = 125
    p.append(arrow(srv_x, y, dev_x, y + 25, color=NEG, sw=1.8))
    p.append(text((srv_x + dev_x) / 2, y + 8, "2. MQTT cmd/{id}/req (QoS 1)", size=11, color=NEG))

    # Step 3: Phase 1 Transport ACK
    y = 175
    p.append(arrow(dev_x, y, srv_x, y + 20, color=FIELD, sw=1.8))
    p.append(text((srv_x + dev_x) / 2, y + 8, "3. Фаза 1: ACK_RECEIVED (перевірено, в черзі)", size=11, color=FIELD))

    # Step 4: Server pushes ACK to UI
    y = 215
    p.append(arrow(srv_x, y, ui_x, y + 20, color=FIELD, sw=1.8))
    p.append(text((ui_x + srv_x) / 2, y + 8, "4. WS: Status = ACK_RECEIVED", size=11, color=FIELD))
    p.append(text(ui_x - 8, y + 20, "UI: RECEIVED", size=10, color=FIELD, anchor="end", bold=True))

    # Step 5: Hardware execution box
    y = 250
    p.append(rect(dev_x - 12, y, 24, 60, fill="#fdecea", stroke=POS, sw=1.5))
    p.append(text(dev_x + 20, y + 25, "Фізичний рух / дія", size=11, color=POS, anchor="start", bold=True))
    p.append(text(dev_x + 20, y + 42, "перемикання реле, оберт вала", size=10, color=MUTED, anchor="start"))

    # Step 6: Phase 2 Execution Completion
    y = 330
    p.append(arrow(dev_x, y, srv_x, y + 20, color=POS, sw=1.8))
    p.append(text((srv_x + dev_x) / 2, y + 8, "5. Фаза 2: EXEC_STATUS = COMPLETED", size=11, color=POS))

    # Step 7: Push Final Status to UI
    y = 370
    p.append(arrow(srv_x, y, ui_x, y + 20, color=POS, sw=1.8))
    p.append(text((ui_x + srv_x) / 2, y + 8, "6. WS: Status = COMPLETED (телеметрія)", size=11, color=POS))
    p.append(text(ui_x - 8, y + 20, "UI: CONFIRMED", size=10, color=POS, anchor="end", bold=True))

    render(os.path.join(IMG, "downlink-two-phase-ack.svg"), W, H, *p)


def fig_mailbox_sleeping():
    W, H = 820, 390
    p = []

    # Timeline bar
    y_time = 60
    p.append(line(50, y_time, 770, y_time, color=LINE, sw=2))
    p.append(text(770, y_time - 12, "Час (t)", size=12, color=INK, anchor="end", bold=True))

    # Server Queue / Mailbox
    p.append(rect(50, 95, 230, 90, fill="#f8fafc", stroke=MUTED, sw=1.5))
    p.append(text(165, 120, "1. Команда в чергу", size=13, color=INK, bold=True))
    p.append(text(165, 140, "Оператор надсилає команду", size=11, color=MUTED))
    p.append(text(165, 160, "Mailbox: {cmd_id, TTL=300s}", size=11, color=NEG, bold=True))

    # Sleeping Device State
    p.append(rect(50, 220, 320, 110, fill="#eaf0fd", stroke=NEG, sw=1.5))
    p.append(text(210, 250, "Вузол у режимі Deep Sleep", size=13, color=NEG, bold=True))
    p.append(text(210, 275, "Радіо знеструмлене, струм ≈ 10 мкА", size=11, color=MUTED))
    p.append(text(210, 300, "Прямий пуш неможливий", size=11, color=NEG))

    # Wakeup & Beacon
    p.append(rect(400, 220, 370, 110, fill="#eafaf0", stroke=FIELD, sw=1.5))
    p.append(text(585, 248, "Сесія активності (вікно 500 мс)", size=13, color=FIELD, bold=True))
    p.append(text(585, 270, "1. Uplink + Poll Mailbox", size=11, color=INK))
    p.append(text(585, 290, "2. Отримання команди з черги", size=11, color=INK))
    p.append(text(585, 310, "3. Перевірка TTL → Виконання → Сон", size=11, color=FIELD, bold=True))

    # Arrows indicating flow
    p.append(arrow(165, 185, 165, 220, color=NEG, sw=1.8))
    p.append(text(175, 205, "Осідає в Mailbox", size=10, color=NEG, anchor="start"))

    p.append(arrow(370, 275, 400, 275, color=FIELD, sw=2))
    p.append(text(385, 260, "Пробудження", size=10, color=FIELD, anchor="middle", bold=True))

    p.append(arrow(280, 140, 480, 220, color=FIELD, sw=2))
    p.append(text(410, 165, "Видача команди з черги", size=11, color=FIELD, bold=True))

    # TTL expiration warning box
    p.append(rect(550, 95, 220, 90, fill="#fdecea", stroke=POS, sw=1.5))
    p.append(text(660, 120, "Захист від застарілих дій", size=12, color=POS, bold=True))
    p.append(text(660, 140, "Якщо час сну > TTL:", size=11, color=INK))
    p.append(text(660, 160, "Статус: EXPIRED (без виконання)", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "mailbox-sleeping-node.svg"), W, H, *p)


if __name__ == '__main__':
    fig_control_plane()
    fig_two_phase_ack()
    fig_mailbox_sleeping()
    print("Figures generated successfully.")
