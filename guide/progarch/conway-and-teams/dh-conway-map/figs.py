# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"


def fig1_conway_mismatch():
    """Організаційне розв'язання за шарами створює комунікаційний хаос при виконанні однієї бізнес-фічі."""
    W, H = 1000, 520
    f = []

    # Заголовок блоку команд
    f.append(fitbox(55, 20, 890, 32, "Організаційна структура за шарами (Layer-based Teams)", size=14, bold=True, fill=NEUT, stroke="#c8ced6"))

    # Чотири команди за технологічними шарами
    f.append(fitbox(55, 65, 205, 55, "Команда UI / Mobile\n(iOS & Android)", size=13, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(283, 65, 205, 55, "Команда Cloud Backend\n(Node.js & Go)", size=13, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(511, 65, 205, 55, "Команда Firmware / Hub\n(C++ & Zigbee)", size=13, fill=BLUE_T, stroke=NEG))
    f.append(fitbox(740, 65, 205, 55, "Команда Database / Infra\n(PostgreSQL & K8s)", size=13, fill=BLUE_T, stroke=NEG))

    # Центральна бізнес-вимога
    f.append(fitbox(250, 160, 500, 50, "Вимога бізнесу: «Тимчасові ПІН-коди для розумного замка»\nПотрібні узгоджені зміни у кожній із 4-х команд!", size=13, bold=True, fill=RED_T, stroke=POS))

    # Стрілки від команд до бізнес-вимоги
    f.append(arrow(157, 120, 300, 160, color=POS, sw=1.8))
    f.append(arrow(385, 120, 420, 160, color=POS, sw=1.8))
    f.append(arrow(613, 120, 580, 160, color=POS, sw=1.8))
    f.append(arrow(842, 120, 700, 160, color=POS, sw=1.8))

    # Заголовок доменних контекстів
    f.append(fitbox(55, 290, 890, 32, "Реальні межі зв'язаних контекстів (Bounded Contexts у коді)", size=14, bold=True, fill=NEUT, stroke="#c8ced6"))

    # Стрілки від вимоги до заголовка контекстів (закінчуються до блоку)
    f.append(arrow(300, 210, 200, 290, color=AMBER, sw=1.5))
    f.append(arrow(420, 210, 400, 290, color=AMBER, sw=1.5))
    f.append(arrow(580, 210, 600, 290, color=AMBER, sw=1.5))
    f.append(arrow(700, 210, 800, 290, color=AMBER, sw=1.5))

    # Доменні контексти, розірвані між командами
    f.append(fitbox(55, 335, 205, 60, "Контекст Керування\n(Lock Domain Model)", size=13, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(283, 335, 205, 60, "Контекст Твіна\n(Desired vs Reported)", size=13, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(511, 335, 205, 60, "Контекст Хаба & ACL\n(Zigbee Radio Packets)", size=13, fill=AMBER_T, stroke=AMBER))
    f.append(fitbox(740, 335, 205, 60, "Контекст Сповіщень\n(Push Notification)", size=13, fill=AMBER_T, stroke=AMBER))

    # Стрілки від заголовка контекстів до самих контекстів
    f.append(arrow(157, 322, 157, 335, color=AMBER, sw=1.5))
    f.append(arrow(385, 322, 385, 335, color=AMBER, sw=1.5))
    f.append(arrow(613, 322, 613, 335, color=AMBER, sw=1.5))
    f.append(arrow(842, 322, 842, 335, color=AMBER, sw=1.5))

    # Висновок на дні
    f.append(fitbox(55, 420, 890, 45, "Наслідок Закону Конвея: N(N-1)/2 комунікаційних затримок, розірвані інваріанти, монолітний DB-спільний шар.", size=12, italic=True, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'fig1-conway-mismatch.svg'), W, H, *f,
           title="Організаційне розв'язання за шарами створює комунікаційний хаос")


def fig2_inverse_conway_mapping():
    """Зворотний маневр Конвея в Digital Homes: потокові команди володіють повними контекстами."""
    W, H = 1040, 500
    f = []

    # Верхній опис
    f.append(fitbox(40, 20, 960, 35, "Зворотний маневр Конвея (Inverse Conway Maneuver): 1 Потокова команда = 1 Bounded Context", size=14, bold=True, fill=GREEN_T, stroke=FIELD))

    # Потокові команди (Stream-Aligned Teams): x1=40..245, x2=290..495, x3=540..745, x4=790..995
    t1 = fitbox(40, 75, 205, 110, "Команда «Край & Зв'язок»\n(Edge & Connectivity Team)\n\n• Володіє Хабом\n• Володіє Protocol ACL", size=12, fill=BLUE_T, stroke=NEG)
    t2 = fitbox(290, 75, 205, 110, "Команда «Ядро Дім & Твін»\n(Core Smart Home Team)\n\n• Володіє Lock Model\n• Володіє State Twin", size=12, fill=BLUE_T, stroke=NEG)
    t3 = fitbox(540, 75, 205, 110, "Команда «Автоматизації»\n(Automation Engine Team)\n\n• Володіє сценаріями\n• Двигун правил", size=12, fill=BLUE_T, stroke=NEG)
    t4 = fitbox(790, 75, 205, 110, "Команда «Медіа & Сенсори»\n(Media & Telemetry Team)\n\n• Video Streaming\n• Time-Series DB", size=12, fill=BLUE_T, stroke=NEG)
    f.extend([t1, t2, t3, t4])

    # Стрілки між потоковими командами у проміжках (245..290), (495..540), (745..790)
    f.append(arrow(245, 130, 290, 130, color=FIELD, sw=2))
    f.append(fitbox(248, 100, 38, 20, "ACL", size=10, bold=True, fill=BG, stroke=FIELD))

    f.append(arrow(495, 130, 540, 130, color=FIELD, sw=2))
    f.append(fitbox(498, 100, 38, 20, "Cust", size=10, bold=True, fill=BG, stroke=FIELD))

    f.append(arrow(745, 130, 790, 130, color=FIELD, sw=2))
    f.append(fitbox(748, 100, 38, 20, "Event", size=10, bold=True, fill=BG, stroke=FIELD))

    # Платформенний блок знизу (Platform Team & Enabling Teams)
    f.append(fitbox(40, 220, 955, 35, "Платформна команда та Команди сприяння (Platform & Enabling Teams)", size=14, bold=True, fill=NEUT, stroke="#c8ced6"))

    p1 = fitbox(40, 285, 450, 100, "Платформа Ідентичності та Брокера (Platform Team)\n\n• Ідентичність & JWT (Open Host Service / Published Language)\n• Event Bus (Kafka / NATS) та CI/CD шаблони сервісів", size=12, fill=AMBER_T, stroke=AMBER)
    p2 = fitbox(535, 285, 460, 100, "Команда архітектурного сприяння (Enabling Team)\n\n• Допомагає потоковим командам вирівнювати межі контекстів\n• Впроваджує Fitness Functions та аналіз залежностей коду", size=12, fill=AMBER_T, stroke=AMBER)
    f.extend([p1, p2])

    # Стрілки від платформи до потокових команд
    f.append(arrow(142, 285, 142, 255, color=AMBER, sw=1.6))
    f.append(arrow(392, 285, 392, 255, color=AMBER, sw=1.6))
    f.append(arrow(642, 285, 642, 255, color=AMBER, sw=1.6))
    f.append(arrow(892, 285, 892, 255, color=AMBER, sw=1.6))

    f.append(arrow(142, 220, 142, 185, color=AMBER, sw=1.6))
    f.append(arrow(392, 220, 392, 185, color=AMBER, sw=1.6))
    f.append(arrow(642, 220, 642, 185, color=AMBER, sw=1.6))
    f.append(arrow(892, 220, 892, 185, color=AMBER, sw=1.6))

    # Підпис
    f.append(fitbox(40, 420, 955, 45, "Результат: автономія команд, автономні релізи, автономне випробування меж, висока швидкість розробки.", size=12, italic=True, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'fig2-inverse-conway-mapping.svg'), W, H, *f,
           title="Зворотний маневр Конвея в Digital Homes")


def fig3_cognitive_load_boundary():
    """Когнітивне навантаження команди як регулятор розміру Bounded Context."""
    W, H = 960, 400
    f = []

    # Ліва частина: Перевантажена команда
    f.append(fitbox(40, 30, 420, 40, "ПЕРЕВАНТАЖЕНА КОМАНДА (Cognitive Overload)", size=14, bold=True, fill=RED_T, stroke=POS))
    f.append(fitbox(40, 80, 420, 210, "Команда «Супер-Ядро» (1 команда = 5 контекстів):\n\n• Device Control Model\n• State Twin Reconciliation\n• Automation Engine & Rules\n• Video Streaming & HLS\n• Billing & Subscriptions\n\nНаслідок: поверхневі рев'ю, високий час перемикання,\nвузькі місця у знаннях, сповільнення розгортань.", size=12, fill=BG, stroke=POS))

    # Стрілка поділу в центрі
    f.append(arrow(475, 185, 525, 185, color=AMBER, sw=2.5))
    f.append(fitbox(465, 120, 70, 45, "Поділ\nконтексту", size=11, bold=True, fill=AMBER_T, stroke=AMBER))

    # Права частина: Збалансовані потокові команди
    f.append(fitbox(540, 30, 380, 40, "ЗБАЛАНСОВАНІ ПОТОКОВІ КОМАНДИ", size=14, bold=True, fill=GREEN_T, stroke=FIELD))

    f.append(fitbox(540, 80, 380, 70, "Команда 1: Core Smart Home & Twin\n• Межа: лише пристрої та дзеркало стану\n• Оптимальний контекст під 5-7 осіб", size=12, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(540, 160, 380, 65, "Команда 2: Automation Engine\n• Межа: двигун обробки правил та сценаріїв\n• Висока фокусність на латентності правил", size=12, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(540, 235, 380, 55, "Команда 3: Video & Media\n• Межа: HLS, WebRTC, медіа-канали", size=12, fill=GREEN_T, stroke=FIELD))

    # Нижній висновок
    f.append(fitbox(40, 310, 880, 50, "Правило: Розмір Bounded Context обмежений когнітивним навантаженням однієї потокової команди.\nПеревищення навантаження — сигнал розбити контекст або виділити платформну службу.", size=12, italic=True, fill=BG, stroke=MUTED))

    render(os.path.join(OUT, 'fig3-cognitive-load-boundary.svg'), W, H, *f,
           title="Шкала когнітивного навантаження та точки розбиття контекстів")


if __name__ == '__main__':
    fig1_conway_mismatch()
    fig2_inverse_conway_mapping()
    fig3_cognitive_load_boundary()
    print("All figures generated successfully.")
