# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Стенд протоколу: емулятор, фазинг, тест сумісності»
(root/course/embedded/stend-protokolu).
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os

# Додаємо шлях до scripts/ у корені репо (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Архітектура випробувального стенду ──────────────────────────────────────
def fig_testbed_architecture():
    W, H = 880, 520
    f = []

    f.append(text(W / 2, 28, "Архітектура випробувального стенду протоколу (Protocol Testbed)",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "ізольоване середовище: оркестратор тестів, віртуальний проксі-канал та тестований пристрій",
                  12, MUTED, "middle", italic=True))

    # Лівий блок: Тестовий оркестратор (Test Orchestrator)
    x_orch, y_orch, w_orch, h_orch = 40, 80, 240, 390
    f.append(rect(x_orch, y_orch, w_orch, h_orch, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    f.append(rect(x_orch, y_orch, w_orch, 36, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=8))
    f.append(text(x_orch + w_orch / 2, y_orch + 24, "Оркестратор тестів (Python/Pytest)", 12, INK, "middle", bold=True))

    f.append(rect(x_orch + 15, y_orch + 50, w_orch - 30, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(x_orch + w_orch / 2, y_orch + 70, "Генератор сценаріїв", 11, INK, "middle", bold=True))
    f.append(text(x_orch + w_orch / 2, y_orch + 86, "виклики, відповіді, таймаути", 9.5, MUTED, "middle"))

    f.append(rect(x_orch + 15, y_orch + 110, w_orch - 30, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(x_orch + w_orch / 2, y_orch + 130, "Керування конфігурацією", 11, INK, "middle", bold=True))
    f.append(text(x_orch + w_orch / 2, y_orch + 146, "параметри завад, сіди рандому", 9.5, MUTED, "middle"))

    f.append(rect(x_orch + 15, y_orch + 170, w_orch - 30, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(x_orch + w_orch / 2, y_orch + 190, "Емулятор бекенду / вузлів", 11, INK, "middle", bold=True))
    f.append(text(x_orch + w_orch / 2, y_orch + 206, "1..1000 віртуальних клієнтів", 9.5, MUTED, "middle"))

    f.append(rect(x_orch + 15, y_orch + 230, w_orch - 30, 48, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(x_orch + w_orch / 2, y_orch + 250, "Валідатор інваріантів", 11, FIELD, "middle", bold=True))
    f.append(text(x_orch + w_orch / 2, y_orch + 266, "контроль станів автоматів", 9.5, MUTED, "middle"))

    f.append(rect(x_orch + 15, y_orch + 290, w_orch - 30, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
    f.append(text(x_orch + w_orch / 2, y_orch + 312, "Збір метрик та журналів", 11, INK, "middle", bold=True))
    f.append(text(x_orch + w_orch / 2, y_orch + 330, "• Дампи трафіку (.pcap)", 9.5, MUTED, "middle"))
    f.append(text(x_orch + w_orch / 2, y_orch + 346, "• Затримки p50 / p95 / p99", 9.5, MUTED, "middle"))
    f.append(text(x_orch + w_orch / 2, y_orch + 362, "• Звіти збоїв (Crash dump)", 9.5, POS, "middle", bold=True))

    # Центральний блок: Проксі-канал з ін'єктором завад (Fault Injection Proxy)
    x_pxy, y_pxy, w_pxy, h_pxy = 315, 80, 250, 390
    f.append(rect(x_pxy, y_pxy, w_pxy, h_pxy, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=8))
    f.append(rect(x_pxy, y_pxy, w_pxy, 36, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 24, "Проксі-ін'єктор завад (Proxy)", 12, "#b45309", "middle", bold=True))

    f.append(rect(x_pxy + 15, y_pxy + 50, w_pxy - 30, 65, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 72, "Модуль втрат (Packet Drop)", 11, POS, "middle", bold=True))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 90, "• Бернуллі (випадкові втрати p)", 9.5, INK, "middle"))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 105, "• Модель Гілберта-Елліотта (пачки)", 9.5, MUTED, "middle"))

    f.append(rect(x_pxy + 15, y_pxy + 125, w_pxy - 30, 65, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 147, "Спотворення бітів (Bitflip)", 11, POS, "middle", bold=True))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 165, "• Інверсія бітів у тілі / CRC", 9.5, INK, "middle"))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 180, "• Псування байтів довжини", 9.5, MUTED, "middle"))

    f.append(rect(x_pxy + 15, y_pxy + 200, w_pxy - 30, 65, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 222, "Джитер та затримки (Delay)", 11, "#b45309", "middle", bold=True))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 240, "• Гаусовий джитер (±N мс)", 9.5, INK, "middle"))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 255, "• Перестановка пакетів (Reorder)", 9.5, MUTED, "middle"))

    f.append(rect(x_pxy + 15, y_pxy + 275, w_pxy - 30, 95, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 297, "Аномалії фреймінгу (Framing)", 11, "#b45309", "middle", bold=True))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 315, "• Обрізання кадру на середині", 9.5, INK, "middle"))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 331, "• Злиття двох кадрів (Stream fusion)", 9.5, INK, "middle"))
    f.append(text(x_pxy + w_pxy / 2, y_pxy + 347, "• Сміттєві байти між кадрами", 9.5, MUTED, "middle"))

    # Правий блок: Тестований об'єкт (DUT - Device Under Test)
    x_dut, y_dut, w_dut, h_dut = 595, 80, 245, 390
    f.append(rect(x_dut, y_dut, w_dut, h_dut, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(rect(x_dut, y_dut, w_dut, 36, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(x_dut + w_dut / 2, y_dut + 24, "Тестований пристрій (DUT)", 12, FIELD, "middle", bold=True))

    # Варіант А: Нативний бінарник
    f.append(rect(x_dut + 15, y_dut + 50, w_dut - 30, 140, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(x_dut + w_dut / 2, y_dut + 72, "Варіант А: Host-Native Build", 11.5, FIELD, "middle", bold=True))
    f.append(text(x_dut + w_dut / 2, y_dut + 92, "• Прошивка скомпільована під x86/ARM", 9.5, INK, "middle"))
    f.append(text(x_dut + w_dut / 2, y_dut + 108, "• Обмін через сокет / Pipe / PTY", 9.5, INK, "middle"))
    f.append(text(x_dut + w_dut / 2, y_dut + 126, "• AddressSanitizer (ASan)", 9.5, POS, "middle", bold=True))
    f.append(text(x_dut + w_dut / 2, y_dut + 142, "• UndefinedBehaviorSanitizer", 9.5, POS, "middle", bold=True))
    f.append(text(x_dut + w_dut / 2, y_dut + 162, "Швидкість: >10 000 кадрів/с", 9.5, FIELD, "middle", bold=True))

    # Варіант Б: Реальне залізо (HIL)
    f.append(rect(x_dut + 15, y_dut + 205, w_dut - 30, 165, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    f.append(text(x_dut + w_dut / 2, y_dut + 227, "Варіант Б: Hardware-in-the-Loop", 11.5, NEG, "middle", bold=True))
    f.append(text(x_dut + w_dut / 2, y_dut + 247, "• Реальна плата мікроконтролера", 9.5, INK, "middle"))
    f.append(text(x_dut + w_dut / 2, y_dut + 263, "• UART / CAN / RS-485 міст до ПК", 9.5, INK, "middle"))
    f.append(text(x_dut + w_dut / 2, y_dut + 281, "• Контроль живлення (Relay/Power)", 9.5, INK, "middle"))
    f.append(text(x_dut + w_dut / 2, y_dut + 299, "• Перевірка реальних таймерів/DMA", 9.5, MUTED, "middle"))
    f.append(text(x_dut + w_dut / 2, y_dut + 317, "• Виявлення HardFault / WDT скидів", 9.5, POS, "middle", bold=True))
    f.append(text(x_dut + w_dut / 2, y_dut + 340, "Швидкість: 50–500 кадрів/с", 9.5, NEG, "middle", bold=True))

    # Стрілки передачі даних між блоками
    # Оркестратор -> Проксі
    f.append(arrow(x_orch + w_orch, y_orch + 90, x_pxy, y_orch + 90, color=NEG, sw=2))
    f.append(text((x_orch + w_orch + x_pxy) / 2, y_orch + 80, "Tx кадри", 9.5, NEG, "middle", bold=True))

    # Проксі -> Оркестратор (зворотні дані)
    f.append(arrow(x_pxy, y_orch + 210, x_orch + w_orch, y_orch + 210, color=FIELD, sw=2))
    f.append(text((x_orch + w_orch + x_pxy) / 2, y_orch + 200, "Rx кадри", 9.5, FIELD, "middle", bold=True))

    # Проксі -> DUT
    f.append(arrow(x_pxy + w_pxy, y_orch + 90, x_dut, y_orch + 90, color=POS, sw=2))
    f.append(text((x_pxy + w_pxy + x_dut) / 2, y_orch + 80, "Спотворений трафік", 9.5, POS, "middle", bold=True))

    # DUT -> Проксі
    f.append(arrow(x_dut, y_orch + 210, x_pxy + w_pxy, y_orch + 210, color=FIELD, sw=2))
    f.append(text((x_pxy + w_pxy + x_dut) / 2, y_orch + 200, "Відповіді DUT", 9.5, FIELD, "middle", bold=True))

    # Нижній висновок
    f.append(line(40, H - 35, W - 40, H - 35, color=MUTED, sw=1, dash="4,4"))
    f.append(text(W / 2, H - 15,
                  "Стенд розділяє тестування на швидкий нативний рівень (санітайзери пам'яті) та HIL-рівень (реальне залізо й таймінги).",
                  11.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "protocol-testbed-architecture.svg"), W, H, *f)


# ── 2. Конвеєр ін'єкції несправностей ─────────────────────────────────────────
def fig_fault_injection_pipeline():
    W, H = 880, 460
    f = []

    f.append(text(W / 2, 28, "Конвеєр ін'єкції несправностей каналу зв'язку",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "поетапна трансформація чистого пакетного потоку у завадостійкий стрес-тест",
                  12, MUTED, "middle", italic=True))

    # Етап 1: Вхідний пакет
    x0, y0 = 30, 100
    f.append(rect(x0, y0, 120, 80, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=6))
    f.append(text(x0 + 60, y0 + 30, "Вхідний пакет", 11.5, INK, "middle", bold=True))
    f.append(text(x0 + 60, y0 + 50, "[Hdr | Payload | CRC]", 9.5, MUTED, "middle"))
    f.append(text(x0 + 60, y0 + 66, "Валідний кадр", 9.5, FIELD, "middle", bold=True))

    # Стрілка 0 -> 1
    f.append(arrow(x0 + 120, y0 + 40, x0 + 155, y0 + 40, color=NEG, sw=2))

    # Етап 1: Модель втрат Гілберта-Елліотта
    x1, y1 = 160, 85
    w1, h1 = 200, 130
    f.append(rect(x1, y1, w1, h1, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    f.append(text(x1 + w1 / 2, y1 + 22, "1. Модель втрат (Loss)", 12, POS, "middle", bold=True))
    f.append(text(x1 + w1 / 2, y1 + 38, "Gilbert-Elliott Markov Chain", 10, MUTED, "middle"))

    # Міні-діаграма станів Гілберта-Елліотта
    f.append(rect(x1 + 15, y1 + 50, 75, 40, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(x1 + 52.5, y1 + 68, "Good (G)", 10.5, FIELD, "middle", bold=True))
    f.append(text(x1 + 52.5, y1 + 82, "P(drop)=0%", 9, INK, "middle"))

    f.append(rect(x1 + 110, y1 + 50, 75, 40, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    f.append(text(x1 + 147.5, y1 + 68, "Bad (B)", 10.5, POS, "middle", bold=True))
    f.append(text(x1 + 147.5, y1 + 82, "P(drop)=80%", 9, INK, "middle"))

    f.append(text(x1 + w1 / 2, y1 + 110, "Імітація пачок завад (Burst loss)", 9.5, POS, "middle", bold=True))

    # Стрілка 1 -> 2
    f.append(arrow(x1 + w1, y0 + 40, x1 + w1 + 35, y0 + 40, color=NEG, sw=2))
    f.append(text(x1 + w1 + 17, y0 + 30, "Pass", 9, FIELD, "middle", bold=True))

    # Відгалуження: Drop
    f.append(arrow(x1 + w1 / 2, y1 + h1, x1 + w1 / 2, y1 + h1 + 30, color=POS, sw=2))
    f.append(text(x1 + w1 / 2, y1 + h1 + 45, "Drop (втрачено в каналі)", 10, POS, "middle", bold=True))

    # Етап 2: Мутація байтів і бітів
    x2, y2 = 400, 85
    w2, h2 = 210, 130
    f.append(rect(x2, y2, w2, h2, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(x2 + w2 / 2, y2 + 22, "2. Мутація байтів (Corruption)", 12, "#b45309", "middle", bold=True))
    f.append(text(x2 + 15, y2 + 45, "• Переворот біта (Bitflip 1..3 біти)", 9.5, INK, "start"))
    f.append(text(x2 + 15, y2 + 63, "• Псування байта довжини Len", 9.5, POS, "start", bold=True))
    f.append(text(x2 + 15, y2 + 81, "• Невалідна контрольна сума CRC", 9.5, INK, "start"))
    f.append(text(x2 + 15, y2 + 99, "• Обрізання кадру на половині", 9.5, INK, "start"))
    f.append(text(x2 + 15, y2 + 117, "• Дописування сміття (Garbage)", 9.5, MUTED, "start"))

    # Стрілка 2 -> 3
    f.append(arrow(x2 + w2, y0 + 40, x2 + w2 + 35, y0 + 40, color=NEG, sw=2))

    # Етап 3: Черга затримок та джитеру
    x3, y3 = 650, 85
    w3, h3 = 200, 130
    f.append(rect(x3, y3, w3, h3, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(x3 + w3 / 2, y3 + 22, "3. Джитер і черги (Timing)", 12, NEG, "middle", bold=True))
    f.append(text(x3 + 15, y3 + 45, "• Затримка: Base ± Jitter", 9.5, INK, "start"))
    f.append(text(x3 + 15, y3 + 63, "• Гаусовий розподіл затримок", 9.5, MUTED, "start"))
    f.append(text(x3 + 15, y3 + 83, "• Черга перестановки:", 9.5, NEG, "start", bold=True))
    f.append(text(x3 + 25, y3 + 100, "Packet 2 прибуває раніше 1", 9, POS, "start"))
    f.append(text(x3 + 15, y3 + 118, "• Залп після паузи (Burst release)", 9.5, INK, "start"))

    # Стрілка 3 -> Вихід
    f.append(arrow(x3 + w3 / 2, y3 + h3, x3 + w3 / 2, y3 + h3 + 40, color=NEG, sw=2))

    # Вихідний блок: Канал до приймача
    x_out, y_out = 580, 275
    f.append(rect(x_out, y_out, 270, 75, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(x_out + 135, y_out + 24, "Вихідний потік до парсера DUT", 11.5, INK, "middle", bold=True))
    f.append(text(x_out + 135, y_out + 44, "Реалістичний брудний фізичний канал", 10, MUTED, "middle"))
    f.append(text(x_out + 135, y_out + 62, "✔ Перевірка надійності автоматів станів", 10, FIELD, "middle", bold=True))

    # Панель порівняння моделей втрат
    py = 275
    f.append(rect(30, py, 520, 140, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(50, py + 24, "Порівняння моделей втрат каналу зв'язку:", 12, INK, "start", bold=True))
    f.append(text(50, py + 48, "• Бернуллі (Uniform Random): кожний пакет втрачається незалежно з ймовірністю p.", 10.5, INK, "start"))
    f.append(text(50, py + 66, "  Не враховує реальну фізику: в реальності завади (мотори, реле) діють пачками.", 10, MUTED, "start"))
    f.append(text(50, py + 88, "• Гілберт-Елліотт (2-state Markov): стан Good переходить у Bad за матрицею переходів.", 10.5, POS, "start", bold=True))
    f.append(text(50, py + 106, "  Ідеально моделює пропадання зв'язку під мостами, затухання в тунелях та EMI-пачки.", 10, INK, "start"))
    f.append(text(50, py + 126, "• Детерміновані сценарії: цільове вибивання кожного N-го ACK для тестування ARQ.", 10, FIELD, "start", bold=True))

    render(os.path.join(IMG, "fault-injection-pipeline.svg"), W, H, *f)


# ── 3. Цикл фазингу з контролем покриття ───────────────────────────────────────
def fig_fuzzing_coverage_feedback():
    W, H = 880, 480
    f = []

    f.append(text(W / 2, 28, "Фазинг парсерів із контролем покриття (Coverage-Guided Fuzzing)",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "еволюційний пошук вразливостей пам'яті та зависань за допомогою LLVM LibFuzzer / AFL++",
                  12, MUTED, "middle", italic=True))

    # Блок 1: Початковий корпус (Seed Corpus)
    x1, y1 = 40, 100
    w1, h1 = 170, 200
    f.append(rect(x1, y1, w1, h1, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x1 + w1 / 2, y1 + 28, "Корпус тестів", 12.5, INK, "middle", bold=True))
    f.append(text(x1 + w1 / 2, y1 + 46, "(Seed Corpus)", 11, MUTED, "middle"))

    f.append(rect(x1 + 15, y1 + 65, w1 - 30, 32, fill="#e0f2fe", stroke=NEG, sw=1, rx=4))
    f.append(text(x1 + w1 / 2, y1 + 85, "seed_01.bin (Heartbeat)", 9.5, INK, "middle"))

    f.append(rect(x1 + 15, y1 + 105, w1 - 30, 32, fill="#e0f2fe", stroke=NEG, sw=1, rx=4))
    f.append(text(x1 + w1 / 2, y1 + 125, "seed_02.bin (Telemetry)", 9.5, INK, "middle"))

    f.append(rect(x1 + 15, y1 + 145, w1 - 30, 32, fill="#e0f2fe", stroke=NEG, sw=1, rx=4))
    f.append(text(x1 + w1 / 2, y1 + 165, "seed_03.bin (ConfigSet)", 9.5, INK, "middle"))

    # Стрілка Корпус -> Мутатор
    f.append(arrow(x1 + w1, y1 + 100, x1 + w1 + 35, y1 + 100, color=NEG, sw=2))

    # Блок 2: Двигун мутацій (Mutation Engine)
    x2, y2 = 250, 100
    w2, h2 = 180, 200
    f.append(rect(x2, y2, w2, h2, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=8))
    f.append(text(x2 + w2 / 2, y2 + 28, "Двигун мутацій", 12.5, "#b45309", "middle", bold=True))
    f.append(text(x2 + w2 / 2, y2 + 46, "(Mutator Engine)", 11, MUTED, "middle"))

    f.append(text(x2 + 15, y2 + 75, "• Випадковий Bitflip", 10, INK, "start"))
    f.append(text(x2 + 15, y2 + 95, "• Вставка цікавих цілих:", 10, INK, "start"))
    f.append(text(x2 + 25, y2 + 112, "0, -1, 255, 0x7FFF, 0xFFFF", 9, "#b45309", "start", bold=True))
    f.append(text(x2 + 15, y2 + 132, "• Склеювання пакетів (Splice)", 10, INK, "start"))
    f.append(text(x2 + 15, y2 + 152, "• Видалення байтів стафінгу", 10, INK, "start"))
    f.append(text(x2 + 15, y2 + 172, "• Роздування розміру (Overflow)", 10, POS, "start", bold=True))

    # Стрілка Мутатор -> Харнес
    f.append(arrow(x2 + w2, y1 + 100, x2 + w2 + 35, y1 + 100, color=NEG, sw=2))

    # Блок 3: Fuzz Target Harness & Parser з Sanitizers
    x3, y3 = 470, 75
    w3, h3 = 210, 245
    f.append(rect(x3, y3, w3, h3, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(x3 + w3 / 2, y3 + 26, "LLVMFuzzerTestOneInput", 11.5, FIELD, "middle", bold=True))
    f.append(text(x3 + w3 / 2, y3 + 44, "Парсер прошивки з Clang інструментацією", 9.5, MUTED, "middle"))

    f.append(rect(x3 + 15, y3 + 60, w3 - 30, 42, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(x3 + w3 / 2, y3 + 78, "Кадрувальник (COBS/SLIP)", 10.5, INK, "middle", bold=True))
    f.append(text(x3 + w3 / 2, y3 + 94, "декодування потоку", 9, MUTED, "middle"))

    f.append(rect(x3 + 15, y3 + 110, w3 - 30, 42, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(x3 + w3 / 2, y3 + 128, "Валідатор заголовка & CRC", 10.5, INK, "middle", bold=True))
    f.append(text(x3 + w3 / 2, y3 + 144, "перевірка полів, версій, сум", 9, MUTED, "middle"))

    f.append(rect(x3 + 15, y3 + 160, w3 - 30, 42, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    f.append(text(x3 + w3 / 2, y3 + 178, "Розбір тіла (TLV / Struct)", 10.5, INK, "middle", bold=True))
    f.append(text(x3 + w3 / 2, y3 + 194, "заповнення структур даних", 9, MUTED, "middle"))

    f.append(rect(x3 + 15, y3 + 210, w3 - 30, 24, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    f.append(text(x3 + w3 / 2, y3 + 226, "ASan + UBSan + LibFuzzer", 10, POS, "middle", bold=True))

    # Стрілка аналізу результатів
    # Гілка А: Нове покриття (New Coverage) -> Стрілка назад у Корпус
    f.append(arrow(x3 + w3 / 2, y3 + h3, x3 + w3 / 2, y3 + h3 + 45, color=FIELD, sw=2))
    f.append(line(x3 + w3 / 2, y3 + h3 + 45, x1 + w1 / 2, y3 + h3 + 45, color=FIELD, sw=2))
    f.append(arrow(x1 + w1 / 2, y3 + h3 + 45, x1 + w1 / 2, y1 + h1, color=FIELD, sw=2))
    f.append(text((x1 + x3) / 2 + 50, y3 + h3 + 35,
                  "✔ Нове покриття гілок коду (New Edge Covered) -> Зберегти у корпус",
                  11, FIELD, "middle", bold=True))

    # Гілка Б: Збій (Crash / Hang) -> Crash Reporter
    x4, y4 = 720, 120
    w4, h4 = 135, 160
    f.append(arrow(x3 + w3, y1 + 100, x4, y1 + 100, color=POS, sw=2.5))
    f.append(text((x3 + w3 + x4) / 2, y1 + 90, "Аварія!", 10, POS, "middle", bold=True))

    f.append(rect(x4, y4, w4, h4, fill="#fee2e2", stroke=POS, sw=1.8, rx=8))
    f.append(text(x4 + w4 / 2, y4 + 26, "Звіт про падіння", 11.5, POS, "middle", bold=True))
    f.append(text(x4 + w4 / 2, y4 + 44, "(Crash Artifacts)", 10, POS, "middle"))

    f.append(text(x4 + 10, y4 + 70, "• Heap overflow", 9.5, INK, "start"))
    f.append(text(x4 + 10, y4 + 88, "• Stack buffer oob", 9.5, INK, "start"))
    f.append(text(x4 + 10, y4 + 106, "• Infinite loop", 9.5, INK, "start"))
    f.append(text(x4 + 10, y4 + 124, "• Null ptr deref", 9.5, INK, "start"))
    f.append(text(x4 + 10, y4 + 146, "crash-minimized.raw", 9, POS, "start", bold=True))

    # Нижній опис
    py = 410
    f.append(rect(40, py, 800, 50, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(W / 2, py + 22,
                  "Швидкість фазингу в пам'яті досягає 50 000 – 200 000 ітерацій/с на одне ядро CPU,",
                  11, INK, "middle"))
    f.append(text(W / 2, py + 38,
                  "що дозволяє за лічені хвилини протестувати мільйони аномальних комбінацій пакетів.",
                  11, FIELD, "middle", bold=True))

    render(os.path.join(IMG, "fuzzing-coverage-feedback.svg"), W, H, *f)


# ── 4. Матриця сумісності релізів у CI/CD ──────────────────────────────────────
def fig_compatibility_matrix_ci():
    W, H = 880, 480
    f = []

    f.append(text(W / 2, 28, "Матриця тестування сумісності версій протоколу в CI/CD",
                  17, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "автоматизована крос-версійна верифікація прошивок клієнтів і серверів перед кожним релізом",
                  12, MUTED, "middle", italic=True))

    # Матриця крос-версій
    ox, oy = 180, 85
    cell_w, cell_h = 145, 65

    # Заголовки стовпців (Сервер / Шлюз)
    cols = ["Сервер v1.0", "Сервер v1.1", "Сервер v2.0", "Сервер v2.1 (PR)"]
    for j, cname in enumerate(cols):
        cx = ox + j * cell_w
        f.append(text(cx + cell_w / 2, oy - 12, cname, 12, INK, "middle", bold=True))

    # Заголовки рядків (Клієнт / Прошивка МК)
    rows = ["Вузол v1.0", "Вузол v1.1", "Вузол v2.0", "Вузол v2.1 (PR)"]
    for i, rname in enumerate(rows):
        cy = oy + i * cell_h
        f.append(text(ox - 15, cy + cell_h / 2 + 5, rname, 12, INK, "end", bold=True))

    # Заповнення матриці комірок (4x4)
    # [i][j] where i=node, j=server
    matrix_data = [
        # Вузол v1.0
        [("✔ Сумісно", "v1.0 ↔ v1.0", "#dcfce7", FIELD),
         ("✔ Зворотна", "Дефолти v1.1", "#dcfce7", FIELD),
         ("✔ Зворотна", "Дефолти v2.0", "#dcfce7", FIELD),
         ("✔ Зворотна", "Дефолти v2.1", "#dcfce7", FIELD)],
        # Вузол v1.1
        [("✔ Пряма", "Сервер скидає хвіст", "#eff6ff", NEG),
         ("✔ Сумісно", "v1.1 ↔ v1.1", "#dcfce7", FIELD),
         ("✔ Зворотна", "Дефолти v2.0", "#dcfce7", FIELD),
         ("✔ Зворотна", "Дефолти v2.1", "#dcfce7", FIELD)],
        # Вузол v2.0 (Мажорна зміна фреймінгу!)
        [("✖ Відхилено", "v1.0 відкидає v2", "#fff1f2", POS),
         ("✖ Відхилено", "v1.1 відкидає v2", "#fff1f2", POS),
         ("✔ Сумісно", "v2.0 ↔ v2.0", "#dcfce7", FIELD),
         ("✔ Зворотна", "Дефолти v2.1", "#dcfce7", FIELD)],
        # Вузол v2.1 (PR)
        [("✖ Відхилено", "Major mismatch", "#fff1f2", POS),
         ("✖ Відхилено", "Major mismatch", "#fff1f2", POS),
         ("✔ Пряма", "Ігнорування опцій", "#eff6ff", NEG),
         ("✔ Сумісно", "Повний контракт", "#dcfce7", FIELD)]
    ]

    for i in range(4):
        for j in range(4):
            cx = ox + j * cell_w
            cy = oy + i * cell_h
            label, sub, bg, border_color = matrix_data[i][j]
            f.append(rect(cx + 4, cy + 4, cell_w - 8, cell_h - 8, fill=bg, stroke=border_color, sw=1.4, rx=6))
            f.append(text(cx + cell_w / 2, cy + 24, label, 11, border_color, "middle", bold=True))
            f.append(text(cx + cell_w / 2, cy + 44, sub, 9.5, INK, "middle"))

    # Пояснювальна легенда знизу
    ly = oy + 4 * cell_h + 20
    f.append(rect(40, ly, 800, 80, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(60, ly + 22, "Правила верифікації в CI конвеєрі:", 12, INK, "start", bold=True))
    f.append(text(60, ly + 42, "• Зелений (✔): Новий сервер коректно парсить пакети старих прошивок у полі (Зворотна сумісність).", 10.5, FIELD, "start", bold=True))
    f.append(text(60, ly + 58, "• Синій (✔): Старі сервери/вузли не падають від розширених пакетів нових релізів (Пряма сумісність).", 10.5, NEG, "start", bold=True))
    f.append(text(60, ly + 74, "• Червоний (✖): При мажорній зміні несумісні версії безпечно відхиляються за Ver Major без зависання.", 10.5, POS, "start", bold=True))

    render(os.path.join(IMG, "compatibility-matrix-ci.svg"), W, H, *f)


def main():
    fig_testbed_architecture()
    fig_fault_injection_pipeline()
    fig_fuzzing_coverage_feedback()
    fig_compatibility_matrix_ci()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
