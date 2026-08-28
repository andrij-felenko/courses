# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_pipeline_architecture():
    W, H = 880, 400
    p = []

    # 5 блоків у горизонтальний ланцюг
    # Вузол -> Шлюз -> Брокер -> Служба -> Сховище та UI
    cols = [
        ("ВУЗОЛ (Node)", ["Вимірювання давача", "Локальний буфер", "Керування сном", "LoRa / NB-IoT / 485"], "#eafaf0", FIELD),
        ("ШЛЮЗ (Gateway)", ["Концентратор радіо", "Міст у TCP/IP", "Офлайн-черга", "TLS-клієнт"], "#eaf0fd", NEG),
        ("БРОКЕР (Broker)", ["Декупулювання", "Маршрутизація тем", "Сесії та LWT", "Черги доставки"], "#fff7e6", "#b8860b"),
        ("СЛУЖБА (Service)", ["Дедуплікація", "Валідація пакетів", "Правила й алерти", "Декодування одиниць"], "#f3e8fd", "#7c3aed"),
        ("СХОВИЩЕ + UI", ["TSDB (телеметрія)", "PostgreSQL (метадані)", "REST / WebSocket", "Панель оператора"], "#fef2f2", POS),
    ]

    bw = 145
    bh = 190
    gap = 25
    x_start = 20
    y_box = 80

    for i, (title_text, items, fill_c, stroke_c) in enumerate(cols):
        bx = x_start + i * (bw + gap)
        p.append(rect(bx, y_box, bw, bh, fill=fill_c, stroke=stroke_c, sw=2, rx=6))
        p.append(text(bx + bw / 2, y_box + 26, title_text, size=12, color=stroke_c, bold=True))
        p.append(line(bx + 10, y_box + 38, bx + bw - 10, y_box + 38, color=stroke_c, sw=1))
        
        for j, item in enumerate(items):
            p.append(text(bx + 12, y_box + 62 + j * 32, "• " + item, size=11, color=INK, anchor="start"))

        # Стрілка до наступного
        if i < len(cols) - 1:
            ax1 = bx + bw + 4
            ax2 = bx + bw + gap - 4
            ay = y_box + bh / 2
            p.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=1.8))

    # Підписи під шарами / інтерфейсами зв'язку
    p.append(rect(x_start, 290, bw + gap + bw, 65, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
    p.append(text(x_start + (bw + gap + bw) / 2, 312, "ПОЛЬОВИЙ КРАЙ (Field Edge)", size=12, color=INK, bold=True))
    p.append(text(x_start + (bw + gap + bw) / 2, 336, "Нестабільний зв'язок · жорсткий енергобюджет", size=10, color=MUTED))

    p.append(rect(x_start + 2 * (bw + gap), 290, 3 * bw + 2 * gap, 65, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
    p.append(text(x_start + 2 * (bw + gap) + (3 * bw + 2 * gap) / 2, 312, "ХМАРНЕ / СЕРВЕРНЕ ЯДРО (Cloud & Core)", size=12, color=INK, bold=True))
    p.append(text(x_start + 2 * (bw + gap) + (3 * bw + 2 * gap) / 2, 336, "Постійне живлення · масштабованість · збереження історії", size=10, color=MUTED))

    render(os.path.join(IMG, 'pipeline-architecture.svg'), W, H, *p,
           title="Наскрізний конвеєр IoT: розподіл обов'язків від вузла до панелі")


def fig_energy_duty_cycle():
    W, H = 840, 360
    p = []

    # Графік струму в часі
    gx, gy, gw, gh = 70, 70, 710, 180
    
    # Осі
    p.append(line(gx, gy + gh, gx + gw, gy + gh, color=INK, sw=2)) # X axis
    p.append(line(gx, gy, gx, gy + gh, color=INK, sw=2))           # Y axis
    
    # Підписи осей
    p.append(text(gx + gw - 20, gy + gh + 35, "Час t", size=12, color=INK, bold=True))
    p.append(text(gx - 35, gy + 15, "Струм I", size=12, color=INK, bold=True))

    # Рівні струму на осі Y
    p.append(text(gx - 8, gy + gh - 4, "15 мкА", size=10, color=MUTED, anchor="end"))
    p.append(text(gx - 8, gy + gh - 45, "15 мА", size=10, color=MUTED, anchor="end"))
    p.append(text(gx - 8, gy + 30, "120 мА", size=10, color=MUTED, anchor="end"))
    
    # Пунктирні горизонталі
    p.append(line(gx, gy + gh - 45, gx + gw, gy + gh - 45, color="#e2e8f0", sw=1, dash="4 4"))
    p.append(line(gx, gy + 30, gx + gw, gy + 30, color="#e2e8f0", sw=1, dash="4 4"))

    # Фази:
    # 1) Сон (0 -> 120px)
    # 2) Пробудження і сенсор (120 -> 200px)
    # 3) Радіо TX (200 -> 340px)
    # 4) Радіо RX (340 -> 420px)
    # 5) Сон (420 -> 680px)
    y_sleep = gy + gh - 6
    y_sense = gy + gh - 45
    y_tx = gy + 30
    y_rx = gy + gh - 70

    poly_pts = [
        (gx, y_sleep),
        (gx + 120, y_sleep),
        (gx + 120, y_sense),
        (gx + 200, y_sense),
        (gx + 200, y_tx),
        (gx + 340, y_tx),
        (gx + 340, y_rx),
        (gx + 420, y_rx),
        (gx + 420, y_sleep),
        (gx + 680, y_sleep)
    ]
    
    # Малюємо ступінчастий профіль
    for k in range(len(poly_pts) - 1):
        x1, y1 = poly_pts[k]
        x2, y2 = poly_pts[k+1]
        p.append(line(x1, y1, x2, y2, color=POS, sw=2.5))

    # Світлі заливки під активними зонами
    # Сенсор
    p.append(rect(gx + 120, y_sense, 80, gy + gh - y_sense, fill="#eafaf0", stroke="#27ae60", sw=1, rx=0))
    p.append(text(gx + 160, gy + gh - 22, "Сенсор", size=10, color=FIELD, bold=True))
    p.append(text(gx + 160, gy + gh - 8, "40 мс", size=9, color=MUTED))

    # TX
    p.append(rect(gx + 200, y_tx, 140, gy + gh - y_tx, fill="#fdecea", stroke=POS, sw=1, rx=0))
    p.append(text(gx + 270, gy + 65, "Передача TX", size=11, color=POS, bold=True))
    p.append(text(gx + 270, gy + 85, "120 мА · 800 мс", size=10, color=POS))

    # RX
    p.append(rect(gx + 340, y_rx, 80, gy + gh - y_rx, fill="#eaf0fd", stroke=NEG, sw=1, rx=0))
    p.append(text(gx + 380, gy + gh - 45, "Прийом RX", size=10, color=NEG, bold=True))
    p.append(text(gx + 380, gy + gh - 28, "150 мс", size=9, color=MUTED))

    # Сон зліва і справа
    p.append(text(gx + 60, gy + gh - 20, "Глибокий сон (15 мкА)", size=10, color=MUTED))
    p.append(text(gx + 550, gy + gh - 20, "Глибокий сон (99.8% усього життєвого циклу)", size=11, color=FIELD, bold=True))

    # Нижній висновок
    p.append(rect(gx, 280, gw, 55, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    p.append(text(gx + gw / 2, 302, "Середній струм I_avg ≈ 35 мкА → автономність 8+ років від елемента Li-SOCl2 (19 А·год)", size=12, color=INK, bold=True))
    p.append(text(gx + gw / 2, 322, "Кожна зайва мілісекунда роботи радіо скорочує життя батареї більше, ніж години сну", size=10, color=POS))

    render(os.path.join(IMG, 'energy-duty-cycle.svg'), W, H, *p,
           title="Профіль споживання струму автономного вузла у часі")


def fig_reliability_boundaries():
    W, H = 840, 380
    p = []

    # 3 колонки ізоляції відмов
    layers = [
        ("АПАРАТНИЙ ЗАХИСТ (Hardware)", [
            "Brown-out Reset (BOR): блок запису Flash при просіданні U",
            "Independent Watchdog (IWDG): апаратне скидання при зависанні",
            "TVS-діоди й ESD-фільтри на лініях сенсорів",
            "Вимикання живлення сенсорів через P-MOSFET ключ"
        ], "#fef2f2", POS),
        ("ПРОШИВКА ТА КРАЙ (Firmware & Edge)", [
            "Автомат станів (FSM) без блокувальних очікувань",
            "Кільцевий буфер у Flash (Store-and-Forward на 30 днів)",
            "Fail-Safe стан: збереження безпечних дефолтів при аварії",
            "Захист від шторму перезапусків (Boot loop backoff)"
        ], "#eafaf0", FIELD),
        ("МЕРЕЖА Й СЕРВЕР (Protocol & Cloud)", [
            "Ідемпотентність: унікальні UUID та порядкові номери пакетів",
            "Експоненційний відступ (Exponential Backoff) із джитером",
            "Last Will and Testament (LWT) для виявлення мертвого вузла",
            "Дедуплікація на рівні сервісу обробки (Service Layer)"
        ], "#eaf0fd", NEG),
    ]

    col_w = 245
    col_h = 240
    gap = 25
    x0 = 35
    y0 = 80

    for i, (title_text, items, fill_c, stroke_c) in enumerate(layers):
        cx = x0 + i * (col_w + gap)
        p.append(rect(cx, y0, col_w, col_h, fill=fill_c, stroke=stroke_c, sw=2, rx=6))
        p.append(fitbox(cx + 8, y0 + 10, col_w - 16, 32, title_text, size=11, bold=True, fill=fill_c, stroke=stroke_c))
        
        for j, item in enumerate(items):
            iy = y0 + 56 + j * 45
            p.append(rect(cx + 8, iy, col_w - 16, 38, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
            p.append(fitbox(cx + 10, iy + 2, col_w - 20, 34, item, size=9.5, color=INK, fill="#ffffff", stroke="#ffffff"))

    # Нижній банер
    p.append(rect(x0, 335, 3 * col_w + 2 * gap, 32, fill="#f8fafc", stroke=LINE, sw=1, rx=4))
    p.append(text(W / 2, 355, "Принцип ізоляції: збій на вищому рівні ніколи не повинен призводити до втрати даних на нижчому", size=11, color=INK, bold=True))

    render(os.path.join(IMG, 'reliability-boundaries.svg'), W, H, *p,
           title="Три ешелони надійності та захисту автономної системи")


if __name__ == '__main__':
    fig_pipeline_architecture()
    fig_energy_duty_cycle()
    fig_reliability_boundaries()
    print("All figures generated successfully.")
