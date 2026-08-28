# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для теми «Журнал дій оператора: хто, коли, що наказав».
"""

import os
import sys

# Підключаємо спільну бібліотеку svgkit з кореня репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

def generate_audit_record_chain(output_dir):
    """
    Фігура 1: Криптографічний ланцюжок хешів у журналі дій оператора.
    Показує зв'язок Record N-1 -> Record N -> Record N+1 через SHA-256.
    """
    w, h = 900, 360
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Криптографічний ланцюг невіддільності (Hash Chaining) у журналі аудиту", size=16, bold=True))

    # Створюємо три послідовні блоки записів
    cards = [
        {
            "x": 40, "y": 60, "cw": 240, "ch": 250,
            "title": "Запис N−1: ЗАПУСК ДВИГУНІВ",
            "seq": "Seq: #1042 | UTC: 12:04:15.102",
            "op": "Operator: ID #07 (Alpha)",
            "cmd": "Cmd: MAV_CMD_NAV_TAKEOFF",
            "params": "Alt=50m, Speed=5m/s",
            "ack": "Status: EXECUTED_OK (0)",
            "prev": "PrevHash: 7a8f...3c01",
            "hash": "Hash N−1: c4d9...e82a",
            "fill": "#f8fafc", "border": "#3b82f6"
        },
        {
            "x": 330, "y": 60, "cw": 240, "ch": 250,
            "title": "Запис N: АВАРІЙНИЙ ДІЗАРМ",
            "seq": "Seq: #1043 | UTC: 12:04:22.450",
            "op": "Operator: ID #07 (Alpha)",
            "cmd": "Cmd: MAV_CMD_COMPONENT_ARM_DISARM",
            "params": "Force=1 (Emergency Kill)",
            "ack": "Status: EXECUTED_OK (0)",
            "prev": "PrevHash: c4d9...e82a",
            "hash": "Hash N: 9f12...5b84",
            "fill": "#fef2f2", "border": "#ef4444"
        },
        {
            "x": 620, "y": 60, "cw": 240, "ch": 250,
            "title": "Запис N+1: ВІДПОВІДЬ БОРТУ",
            "seq": "Seq: #1044 | UTC: 12:04:22.458",
            "op": "Operator: ID #00 (Autopilot)",
            "cmd": "Cmd: NOTIFY_PARAM_CHANGE",
            "params": "Motors: DISARMED, Mode: CRASH",
            "ack": "Status: STATE_CHANGED",
            "prev": "PrevHash: 9f12...5b84",
            "hash": "Hash N+1: 1a5e...7d90",
            "fill": "#f8fafc", "border": "#3b82f6"
        }
    ]

    for c in cards:
        # Фон картки
        frags.append(rect(c["x"], c["y"], c["cw"], c["ch"], fill=c["fill"], stroke=c["border"], sw=2, rx=8))
        # Заголовок картки
        frags.append(rect(c["x"], c["y"], c["cw"], 32, fill=c["border"], stroke=c["border"], sw=1, rx=8))
        frags.append(text(c["x"] + c["cw"]/2, c["y"] + 21, c["title"], size=12, color="#ffffff", bold=True))
        
        # Поля
        frags.append(text(c["x"] + 12, c["y"] + 55, c["seq"], size=11, color=INK, anchor="start", bold=True))
        frags.append(text(c["x"] + 12, c["y"] + 77, c["op"], size=11, color=INK, anchor="start"))
        frags.append(text(c["x"] + 12, c["y"] + 99, c["cmd"], size=11, color=INK, anchor="start"))
        frags.append(text(c["x"] + 12, c["y"] + 121, c["params"], size=11, color=MUTED, anchor="start"))
        frags.append(text(c["x"] + 12, c["y"] + 143, c["ack"], size=11, color=INK, anchor="start"))

        # Блок PrevHash
        frags.append(rect(c["x"] + 10, c["y"] + 160, c["cw"] - 20, 30, fill="#edf2f7", stroke="#cbd5e1", sw=1, rx=4))
        frags.append(text(c["x"] + c["cw"]/2, c["y"] + 180, c["prev"], size=11, color="#1e293b", anchor="middle"))

        # Блок Current Hash
        frags.append(rect(c["x"] + 10, c["y"] + 200, c["cw"] - 20, 38, fill="#dbeafe", stroke="#93c5fd", sw=1.5, rx=4))
        frags.append(text(c["x"] + c["cw"]/2, c["y"] + 218, "SHA-256 (Record Data + PrevHash)", size=10, color=MUTED, anchor="middle"))
        frags.append(text(c["x"] + c["cw"]/2, c["y"] + 232, c["hash"], size=11, color="#1d4ed8", bold=True, anchor="middle"))

    # Стрілки хеш-зв'язку
    # Від Hash N-1 до PrevHash N
    frags.append(line(270, 275, 300, 275, color="#2563eb", sw=2))
    frags.append(line(300, 275, 300, 235, color="#2563eb", sw=2))
    frags.append(arrow(300, 235, 328, 235, color="#2563eb", sw=2))

    # Від Hash N до PrevHash N+1
    frags.append(line(560, 275, 590, 275, color="#2563eb", sw=2))
    frags.append(line(590, 275, 590, 235, color="#2563eb", sw=2))
    frags.append(arrow(590, 235, 618, 235, color="#2563eb", sw=2))

    # Пояснення знизу
    frags.append(text(w / 2, 340, "Будь-яка зміна або видалення команди N робить недійсними всі наступні хеші (Tamper-Evident Chain)", size=12, color="#b91c1c", bold=True))

    out_path = os.path.join(output_dir, "audit-record-chain.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def generate_flash_ring_buffer(output_dir):
    """
    Фігура 2: Структура енергонезалежного кільцевого буфера на Flash.
    Показує чергу 4KB-секторів: ERASED, ACTIVE WRITING, COMMITTED, FULL.
    """
    w, h = 900, 380
    frags = []

    frags.append(text(w / 2, 28, "Кільцевий енергонезалежний буфер аудиту на Flash-пам'яті (Flash Ring Buffer)", size=16, bold=True))

    # Відображення секторів Flash
    sectors = [
        {"x": 40, "y": 70, "w": 180, "h": 220, "name": "Сектор #0", "state": "FULL / COMMITTED", "fill": "#f1f5f9", "stroke": "#64748b", "info": "Записи #001..#032\nХеш сектора валідний\nЗахищено від запису"},
        {"x": 250, "y": 70, "w": 180, "h": 220, "name": "Сектор #1", "state": "FULL / COMMITTED", "fill": "#f1f5f9", "stroke": "#64748b", "info": "Записи #033..#064\nХеш сектора валідний\nЗахищено від запису"},
        {"x": 460, "y": 70, "w": 195, "h": 220, "name": "Сектор #2 (АКТИВНИЙ)", "state": "ACTIVE WRITING (HEAD)", "fill": "#eff6ff", "stroke": "#3b82f6", "info": "Записи #065..#082\nНаступний слот: Слот #83\nВільні сторінки: 0xFF..."},
        {"x": 680, "y": 70, "w": 180, "h": 220, "name": "Сектор #3 (ХВІСТ)", "state": "ERASED (0xFF) / TAIL", "fill": "#f0fdf4", "stroke": "#22c55e", "info": "Стерто до 0xFF\nГотовий під ротацію\nПокажчик TAIL"}
    ]

    for s in sectors:
        frags.append(rect(s["x"], s["y"], s["w"], s["h"], fill=s["fill"], stroke=s["stroke"], sw=2, rx=8))
        frags.append(rect(s["x"], s["y"], s["w"], 32, fill=s["stroke"], stroke=s["stroke"], sw=1, rx=8))
        frags.append(text(s["x"] + s["w"]/2, s["y"] + 21, s["name"], size=12, color="#ffffff", bold=True))
        
        # Стан
        frags.append(text(s["x"] + s["w"]/2, s["y"] + 55, s["state"], size=10, color=s["stroke"], bold=True))
        
        # Вміст
        lines = s["info"].split("\n")
        for idx, ln in enumerate(lines):
            frags.append(text(s["x"] + s["w"]/2, s["y"] + 85 + idx * 22, ln, size=11, color=INK))

        # Мініатюра структури 128B слотів усередині
        slot_y = s["y"] + 155
        frags.append(rect(s["x"] + 10, slot_y, s["w"] - 20, 50, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        frags.append(text(s["x"] + s["w"]/2, slot_y + 18, "Слоти 128Б (32 на 4KB)", size=10, color=MUTED))
        frags.append(text(s["x"] + s["w"]/2, slot_y + 36, "128B Page Program", size=10, color=LINE, bold=True))

    # Стрілка покажчиків Head і Tail
    # Вказівник HEAD
    frags.append(rect(470, 305, 175, 30, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=6))
    frags.append(text(557, 325, "HEAD Pointer: Сектор #2, Слот #83", size=10, color="#1e40af", bold=True))
    frags.append(arrow(557, 305, 557, 292, color="#2563eb", sw=2))

    # Вказівник TAIL
    frags.append(rect(685, 305, 170, 30, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(770, 325, "TAIL Pointer: Сектор #3", size=10, color="#15803d", bold=True))
    frags.append(arrow(770, 305, 770, 292, color="#16a34a", sw=2))

    # Пояснення знизу
    frags.append(text(w / 2, 360, "При переповненні TAIL-сектор стирається (ERASE 4KB), стаючи новим чистим буфером для запису", size=11, color=MUTED))

    out_path = os.path.join(output_dir, "flash-ring-buffer-layout.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def generate_command_timeline(output_dir):
    """
    Фігура 3: Часова шкала проходження, верифікації та виконання команди оператора.
    Від наземної станції (GCS) до бортового аудиту й польотного контролера.
    """
    w, h = 900, 340
    frags = []

    frags.append(text(w / 2, 28, "Хронологія проходження команди: від відправки оператором до фіксації в аудиті", size=16, bold=True))

    steps = [
        {"cx": 100, "cy": 100, "title": "1. Формування GCS", "desc": "Оператор тисне Disarm\nДодається мітка UTC\nПідпис Ed25519 / ID"},
        {"cx": 300, "cy": 100, "title": "2. Радіолінк", "desc": "MAVLink / COBS пакет\nТелеметричний канал\nПередача через UART"},
        {"cx": 500, "cy": 100, "title": "3. Бортовий аудит", "desc": "Запис у журнал (PENDING)\nРозрахунок SHA-256\nАтомарний запис у Flash"},
        {"cx": 700, "cy": 100, "title": "4. Виконання", "desc": "Перевірка інтерлоків\nВимкнення ШІМ двигунів\nЗапис ACK (SUCCESS)"}
    ]

    for s in steps:
        box_w, box_h = 160, 95
        x = s["cx"] - box_w/2
        y = s["cy"] - box_h/2
        frags.append(rect(x, y, box_w, box_h, fill="#f8fafc", stroke="#3b82f6", sw=1.5, rx=8))
        frags.append(rect(x, y, box_w, 28, fill="#3b82f6", stroke="#3b82f6", sw=1, rx=8))
        frags.append(text(s["cx"], y + 19, s["title"], size=11, color="#ffffff", bold=True))
        
        lines = s["desc"].split("\n")
        for idx, ln in enumerate(lines):
            frags.append(text(s["cx"], y + 46 + idx * 17, ln, size=10, color=INK))

    # Стрілки між етапами
    frags.append(arrow(180, 100, 220, 100, color="#2563eb", sw=2))
    frags.append(arrow(380, 100, 420, 100, color="#2563eb", sw=2))
    frags.append(arrow(580, 100, 620, 100, color="#2563eb", sw=2))

    # Часова вісь унизу
    axis_y = 200
    frags.append(line(50, axis_y, 850, axis_y, color="#64748b", sw=2))
    frags.append(arrow(850, axis_y, 865, axis_y, color="#64748b", sw=2))
    frags.append(text(870, axis_y + 4, "Час t", size=11, color="#64748b", bold=True, anchor="start"))

    time_ticks = [
        {"x": 100, "label": "T0 = 0 мс", "desc": "Клік у QGroundControl"},
        {"x": 300, "label": "T1 = +35 мс", "desc": "Прийом RF-модулем"},
        {"x": 500, "label": "T2 = +38 мс", "desc": "Аудит-лог заблоковано"},
        {"x": 700, "label": "T3 = +40 мс", "desc": "Двигуни зупинено"}
    ]

    for t_item in time_ticks:
        frags.append(line(t_item["x"], axis_y - 8, t_item["x"], axis_y + 8, color="#64748b", sw=2))
        frags.append(text(t_item["x"], axis_y + 24, t_item["label"], size=11, color="#1e293b", bold=True))
        frags.append(text(t_item["x"], axis_y + 42, t_item["desc"], size=10, color=MUTED))

    frags.append(text(w / 2, 295, "Фіксація команди в енергонезалежному журналі відбувається ДО фізичного виконання виконавчими механізмами", size=11, color="#0f766e", bold=True))

    out_path = os.path.join(output_dir, "command-execution-timeline.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def main():
    topic_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(topic_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    generate_audit_record_chain(img_dir)
    generate_flash_ring_buffer(img_dir)
    generate_command_timeline(img_dir)

if __name__ == "__main__":
    main()
