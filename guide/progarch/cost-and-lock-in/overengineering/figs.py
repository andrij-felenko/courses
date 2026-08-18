# -*- coding: utf-8 -*-
import os, sys

# sys.path for svgkit (4 levels up from guide/progarch/cost-and-lock-in/overengineering)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def generate_overengineering_spectrum():
    # viewBox: 0 0 800 320
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="800" height="320">')
    out.append(rect(0, 0, 800, 320, fill=BG, stroke="none"))
    
    # Title
    out.append(text(400, 30, "Спектр системної складності: від найпростішого до перепроєктованого", size=16, bold=True))
    
    # Axis arrow
    out.append(line(50, 270, 750, 270, color=LINE, sw=2))
    out.append(line(740, 265, 750, 270, color=LINE, sw=2))
    out.append(line(740, 275, 750, 270, color=LINE, sw=2))
    out.append(text(400, 295, "Зростання випадкової складності та операційного боргу →", size=13, color=MUTED, italic=True))
    
    # Box 1: Prprimitive / Naive
    tb1, w1, h1 = textbox(150, 140, "Примітивне рішення\n• Весь код в одному файлі\n• Немає розділення меж\n• Швидкий старт, хаос згодом", size=13, fill="#fef9e7", stroke="#f39c12", rx=8)
    out.append(tb1)
    out.append(text(150, 65, "Примітивність", size=14, bold=True, color="#d35400"))
    
    # Box 2: Pragmatic Optimum
    tb2, w2, h2 = textbox(400, 140, "Прагматичний оптимум\n• Модульний моноліт з чіткими межами\n• Адекватно потребам сьогодення\n• Простий деплоймент, пряма відладка", size=13, fill="#eafaf1", stroke=FIELD, rx=8)
    out.append(tb2)
    out.append(text(400, 65, "Зрілий оптимум (YAGNI)", size=14, bold=True, color=FIELD))
    
    # Box 3: Overengineered
    tb3, w3, h3 = textbox(650, 140, "Перепроєктування\n• 15 мікросервісів на 10rps\n• Спекулятивні фабрики й шини\n• Операційний податок > доменний код", size=13, fill="#fadbd8", stroke=POS, rx=8)
    out.append(tb3)
    out.append(text(650, 65, "Надмірна складність", size=14, bold=True, color=POS))
    
    # Connectors / indicators below
    out.append(line(150, 220, 150, 270, color="#f39c12", sw=1.5, dash="4,4"))
    out.append(line(400, 220, 400, 270, color=FIELD, sw=2))
    out.append(line(650, 220, 650, 270, color=POS, sw=1.5, dash="4,4"))
    
    out.append("</svg>")
    return "\n".join(out)

def generate_change_amplification():
    # viewBox: 0 0 800 360
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360" width="800" height="360">')
    out.append(rect(0, 0, 800, 360, fill=BG, stroke="none"))
    
    # Title
    out.append(text(400, 30, "Коефіцієнт підсилення змін: додавання одного поля в бізнес-вимогу", size=16, bold=True))
    
    # Left side: Overengineered Architecture (High Amplification)
    out.append(rect(30, 60, 350, 270, fill="#fdf2e9", stroke=POS, sw=1.5, rx=8))
    out.append(text(205, 85, "Перепроєктована система (Каскадні зміни)", size=14, bold=True, color=POS))
    
    # Steps in left side
    tb_l1, _, _ = textbox(205, 125, "1. Схема БД сервісу A + міграція", size=12, fill="#ffffff", stroke=POS)
    tb_l2, _, _ = textbox(205, 165, "2. Protobuf / gRPC контракт сервісів", size=12, fill="#ffffff", stroke=POS)
    tb_l3, _, _ = textbox(205, 205, "3. Event Schema у Kafka / RabbitMQ", size=12, fill="#ffffff", stroke=POS)
    tb_l4, _, _ = textbox(205, 245, "4. DTO і мапери у 4 суміжних сервісах", size=12, fill="#ffffff", stroke=POS)
    tb_l5, _, _ = textbox(205, 285, "5. Оновлення версій API та Gateway", size=12, fill="#ffffff", stroke=POS)
    out.extend([tb_l1, tb_l2, tb_l3, tb_l4, tb_l5])
    out.append(text(205, 318, "Загалом: 5 репозиторіїв, 18 файлів, 3 дні PR-ів", size=11, color=POS, bold=True))
    
    # Right side: Pragmatic Architecture (Low Amplification)
    out.append(rect(420, 60, 350, 270, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=8))
    out.append(text(595, 85, "Прагматична система (Локалізовані зміни)", size=14, bold=True, color=FIELD))
    
    # Steps in right side
    tb_r1, _, _ = textbox(595, 140, "1. Колонка в таблиці + міграція БД", size=12, fill="#ffffff", stroke=FIELD)
    tb_r2, _, _ = textbox(595, 190, "2. Поле в доменній сутності та DTO", size=12, fill="#ffffff", stroke=FIELD)
    tb_r3, _, _ = textbox(595, 240, "3. Відображення у представленні (UI/API)", size=12, fill="#ffffff", stroke=FIELD)
    out.extend([tb_r1, tb_r2, tb_r3])
    out.append(text(595, 318, "Загалом: 1 репозиторій, 3 файли, 30 хвилин PR", size=11, color=FIELD, bold=True))
    
    out.append("</svg>")
    return "\n".join(out)

def generate_accidental_vs_essential():
    # viewBox: 0 0 800 320
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 320" width="800" height="320">')
    out.append(rect(0, 0, 800, 320, fill=BG, stroke="none"))
    
    out.append(text(400, 30, "Структура кодової бази: Істотна проти Випадкової складності", size=16, bold=True))
    
    # Left bar: Overengineered system
    out.append(text(220, 65, "Перепроєктована система", size=14, bold=True, color=POS))
    # Stacked rectangles
    out.append(rect(120, 85, 200, 45, fill="#fadbd8", stroke=POS, sw=1.5, rx=4))
    out.append(text(220, 112, "Випадкова складність (75%)\n(абстракції, IPC, IPC-трапки)", size=11, color=POS))
    
    out.append(rect(120, 135, 200, 60, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=4))
    out.append(text(220, 170, "Операційний податок (15%)\n(конфіги, k8s, retry, serialization)", size=11, color=NEG))
    
    out.append(rect(120, 200, 200, 45, fill="#d4efdf", stroke=FIELD, sw=1.5, rx=4))
    out.append(text(220, 227, "Істотна складність (10%)\n(бізнес-правила домену)", size=11, color=FIELD, bold=True))
    
    out.append(text(220, 275, "90% коду НЕ створює бізнес-цінності", size=12, color=POS, italic=True))

    # Right bar: Pragmatic system
    out.append(text(580, 65, "Прагматична система", size=14, bold=True, color=FIELD))
    # Stacked rectangles
    out.append(rect(480, 85, 200, 30, fill="#fadbd8", stroke=POS, sw=1.5, rx=4))
    out.append(text(580, 104, "Випадкова складність (10%)", size=11, color=POS))
    
    out.append(rect(480, 120, 200, 35, fill="#ebf5fb", stroke=NEG, sw=1.5, rx=4))
    out.append(text(580, 142, "Операційний податок (15%)", size=11, color=NEG))
    
    out.append(rect(480, 160, 200, 85, fill="#d4efdf", stroke=FIELD, sw=1.5, rx=4))
    out.append(text(580, 207, "Істотна складність (75%)\n(чиста доменна логіка)", size=12, color=FIELD, bold=True))
    
    out.append(text(580, 275, "Більшість зусиль витрачається на продукт", size=12, color=FIELD, italic=True))

    out.append("</svg>")
    return "\n".join(out)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), 'img')
    os.makedirs(img_dir, exist_ok=True)
    
    files = {
        'overengineering-spectrum.svg': generate_overengineering_spectrum(),
        'change-amplification.svg': generate_change_amplification(),
        'accidental-vs-essential.svg': generate_accidental_vs_essential(),
    }
    
    for filename, content in files.items():
        filepath = os.path.join(img_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated {filepath}")

if __name__ == '__main__':
    main()
