# -*- coding: utf-8 -*-
"""Фігури теми «Канал повідомлень». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"
GRAY_F  = "#f8f9fa"

# ── 1. channel-decoupling-dimensions: 4 виміри розчеплення ──────────────────
def fig_decoupling_dimensions():
    W, H = 1000, 480
    f = []

    f.append(rect(10, 10, 980, 460, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Чотири виміри розчеплення розподілених систем через канал повідомлень", size=14, bold=True))

    # Ліва колонка: Продюсери
    p_box, _, _ = textbox(110, 240, "ВІДПРАВНИКИ\n(Producers)\n\n• Вебсервери\n• Фонові воркери\n• IoT-шлюзи",
                          size=11, bold=True, min_w=130, pad=8, fill=BLUE_F, stroke=NEG, sw=1.5)
    f.append(p_box)

    # Центр: Канал повідомлень
    ch_box, _, _ = textbox(500, 240, "КАНАЛ ПОВІДОМЛЕНЬ (Message Channel)\n\n[Буфер пам'яті / Дисковий журнал WAL]\n\n• Інкапсуляція маршруту й транспорту\n• Управління потоком і черговістю\n• Ізоляція відмов і згладжування піків",
                           size=11.5, bold=True, min_w=280, pad=10, fill=WARN_F, stroke=LINE, sw=1.8)
    f.append(ch_box)

    # Права колонка: Споживачі
    c_box, _, _ = textbox(890, 240, "ОТРИМУВАЧІ\n(Consumers)\n\n• Обробники замовлень\n• Бази даних / Сховища\n• ML-аналітика",
                          size=11, bold=True, min_w=130, pad=8, fill=GREEN_F, stroke=FIELD, sw=1.5)
    f.append(c_box)

    # Стрілки до і від каналу
    f.append(arrow(180, 240, 350, 240, color=NEG, sw=2))
    f.append(text(265, 225, "write / send", size=10, color=NEG, bold=True))

    f.append(arrow(650, 240, 820, 240, color=FIELD, sw=2))
    f.append(text(735, 225, "read / poll", size=10, color=FIELD, bold=True))

    # 4 плашки розчеплення (2 зверху, 2 знизу)
    cards = [
        ("1. Просторове розчеплення (Space)", "Відправник не знає IP/порт отримувача;\nобидва прив'язані лише до імені каналу.", 280, 95),
        ("2. Часове розчеплення (Time)", "Учасники не мусять працювати одночасно;\nбуфер каналу зберігає дані під час збоїв.", 720, 95),
        ("3. Синхронізаційне розчеплення (Execution)", "Відправник не блокує свій потік;\nспоживач вичитує дані у власному темпі.", 280, 395),
        ("4. Типове розчеплення (Datatype)", "Канал фіксує схему передачі (DTO);\nізоляція версій і форматів повідомлень.", 720, 395)
    ]

    for title_txt, desc_txt, cx, cy in cards:
        b, _, _ = textbox(cx, cy, title_txt + "\n" + desc_txt, size=10, bold=False, min_w=280, pad=6, fill=GRAY_F, stroke=MUTED, sw=1)
        f.append(b)

    render(out("channel-decoupling-dimensions.svg"), W, H, *f,
           title="Чотири виміри розчеплення через канал повідомлень")


# ── 2. channel-taxonomy: таксономія 4 типів каналів ─────────────────────────
def fig_channel_taxonomy():
    W, H = 1000, 520
    f = []

    f.append(rect(10, 10, 980, 500, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Архітектурна таксономія каналів повідомлень (Enterprise Integration Patterns)", size=14, bold=True))

    # 4 квадранти
    # 1. Point-to-Point
    f.append(rect(25, 60, 455, 205, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(252, 85, "1. Точка-точка (Point-to-Point / Queue Channel)", size=12, bold=True, color=POS))
    b_p1, _, _ = textbox(95, 160, "Продюсер", size=10, min_w=75, pad=5, fill=BLUE_F, stroke=NEG)
    b_ch1, _, _ = textbox(252, 160, "Черга P2P\n(1:1 адресація)", size=10.5, bold=True, min_w=110, pad=6, fill=WARN_F, stroke=LINE)
    b_c1a, _, _ = textbox(410, 130, "Воркер A (ACK)", size=9.5, min_w=85, pad=4, fill=GREEN_F, stroke=FIELD)
    b_c1b, _, _ = textbox(410, 190, "Воркер B (очікує)", size=9.5, min_w=85, pad=4, fill=FILL, stroke=MUTED)
    f.extend([b_p1, b_ch1, b_c1a, b_c1b])
    f.append(arrow(135, 160, 190, 160, color=NEG, sw=1.3))
    f.append(arrow(315, 160, 360, 130, color=FIELD, sw=1.3))
    f.append(text(252, 245, "Кожне повідомлення дістається лише 1 воркеру з пулу", size=9.5, color=FIELD, italic=True))

    # 2. Publish-Subscribe
    f.append(rect(520, 60, 455, 205, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(747, 85, "2. Публікація-підписка (Publish-Subscribe Channel)", size=12, bold=True, color=POS))
    b_p2, _, _ = textbox(590, 160, "Видавець", size=10, min_w=75, pad=5, fill=BLUE_F, stroke=NEG)
    b_ch2, _, _ = textbox(747, 160, "Тема Pub/Sub\n(1:N копіювання)", size=10.5, bold=True, min_w=110, pad=6, fill=WARN_F, stroke=LINE)
    b_c2a, _, _ = textbox(905, 125, "Підписник 1", size=9.5, min_w=80, pad=4, fill=GREEN_F, stroke=FIELD)
    b_c2b, _, _ = textbox(905, 160, "Підписник 2", size=9.5, min_w=80, pad=4, fill=GREEN_F, stroke=FIELD)
    b_c2c, _, _ = textbox(905, 195, "Підписник 3", size=9.5, min_w=80, pad=4, fill=GREEN_F, stroke=FIELD)
    f.extend([b_p2, b_ch2, b_c2a, b_c2b, b_c2c])
    f.append(arrow(630, 160, 685, 160, color=NEG, sw=1.3))
    f.append(arrow(810, 160, 860, 125, color=FIELD, sw=1.3))
    f.append(arrow(810, 160, 860, 160, color=FIELD, sw=1.3))
    f.append(arrow(810, 160, 860, 195, color=FIELD, sw=1.3))
    f.append(text(747, 245, "Окремий примірник події надходить усім активним підписникам", size=9.5, color=FIELD, italic=True))

    # 3. Datatype Channel
    f.append(rect(25, 280, 455, 205, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(252, 305, "3. Типізований канал (Datatype Channel)", size=12, bold=True, color=POS))
    b_p3, _, _ = textbox(95, 380, "Клієнтський\nсервіс", size=10, min_w=75, pad=5, fill=BLUE_F, stroke=NEG)
    b_ch3a, _, _ = textbox(252, 350, "Канал OrderCreated (V2)", size=9.5, min_w=140, pad=4, fill=BLUE_F, stroke=NEG)
    b_ch3b, _, _ = textbox(252, 410, "Канал PaymentFailed (V1)", size=9.5, min_w=140, pad=4, fill=WARN_F, stroke=LINE)
    b_c3a, _, _ = textbox(410, 350, "Склад (Orders)", size=9.5, min_w=85, pad=4, fill=GREEN_F, stroke=FIELD)
    b_c3b, _, _ = textbox(410, 410, "Білінг (Payments)", size=9.5, min_w=85, pad=4, fill=GREEN_F, stroke=FIELD)
    f.extend([b_p3, b_ch3a, b_ch3b, b_c3a, b_c3b])
    f.append(arrow(135, 375, 175, 350, color=NEG, sw=1.3))
    f.append(arrow(135, 385, 175, 410, color=NEG, sw=1.3))
    f.append(arrow(330, 350, 360, 350, color=FIELD, sw=1.3))
    f.append(arrow(330, 410, 360, 410, color=FIELD, sw=1.3))
    f.append(text(252, 465, "Сувора ізоляція схем DTO: кожен тип даних має власний канал", size=9.5, color=FIELD, italic=True))

    # 4. Dead Letter Channel
    f.append(rect(520, 280, 455, 205, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(747, 305, "4. Канал недійсних повідомлень (Dead Letter Channel)", size=12, bold=True, color=POS))
    b_p4, _, _ = textbox(590, 380, "Головний\nканал", size=10, min_w=75, pad=5, fill=WARN_F, stroke=LINE)
    b_c4, _, _ = textbox(747, 350, "Воркер\n(Збій парсингу)", size=9.5, min_w=85, pad=4, fill=RED_F, stroke=POS)
    b_dlq, _, _ = textbox(747, 425, "Канал DLQ (Помилки)", size=10, bold=True, min_w=125, pad=5, fill=RED_F, stroke=POS)
    b_ops, _, _ = textbox(905, 425, "Аналіз і\nаудит (Ops)", size=9.5, min_w=80, pad=4, fill=FILL, stroke=MUTED)
    f.extend([b_p4, b_c4, b_dlq, b_ops])
    f.append(arrow(630, 375, 695, 350, color=LINE, sw=1.3))
    f.append(arrow(747, 378, 747, 395, color=POS, sw=1.3))
    f.append(arrow(815, 425, 860, 425, color=MUTED, sw=1.3))
    f.append(text(747, 465, "Отруйні та биті повідомлення ізолюються від робочого трафіку", size=9.5, color=POS, italic=True))

    render(out("channel-taxonomy.svg"), W, H, *f,
           title="Архітектурна таксономія каналів повідомлень")


# ── 3. buffering-and-backpressure: буферизація та зворотний тиск ─────────────
def fig_buffering_and_backpressure():
    W, H = 1000, 460
    f = []

    f.append(rect(10, 10, 980, 440, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Моделі місткості каналу: синхронна передача, обмежений буфер та загроза переповнення", size=13.5, bold=True))

    # Панель 1: Rendezvous (0-capacity)
    f.append(rect(25, 60, 295, 370, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(172, 85, "А. Нульова місткість (Rendezvous)", size=11, bold=True, color=POS))
    b_pA, _, _ = textbox(172, 140, "Продюсер\n(Блокується під час send)", size=10, min_w=160, pad=6, fill=BLUE_F, stroke=NEG)
    b_chA, _, _ = textbox(172, 230, "Канал без буфера\n(Capacity = 0)\nПряма передача з рук у руки", size=10, bold=True, min_w=170, pad=6, fill=WARN_F, stroke=LINE)
    b_cA, _, _ = textbox(172, 320, "Споживач\n(Блокується під час recv)", size=10, min_w=160, pad=6, fill=GREEN_F, stroke=FIELD)
    f.extend([b_pA, b_chA, b_cA])
    f.append(arrow(172, 175, 172, 195, color=NEG, sw=1.5))
    f.append(arrow(172, 265, 172, 285, color=FIELD, sw=1.5))
    f.append(text(172, 395, "✓ Нульова латентність у буфері\n✗ Жорстке часове зчеплення", size=9.5, color=POS, italic=True))

    # Панель 2: Bounded Buffer + Backpressure
    f.append(rect(350, 60, 295, 370, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(497, 85, "Б. Обмежений буфер (Bounded)", size=11, bold=True, color=FIELD))
    b_pB, _, _ = textbox(497, 140, "Продюсер\n(Кредитне вікно / Пауза)", size=10, min_w=160, pad=6, fill=BLUE_F, stroke=NEG)
    b_chB, _, _ = textbox(497, 230, "Кільцевий буфер (N = 1000)\n[Елемент 1] [Елемент 2] [Вільне]\nСигнал зворотного тиску (Pause)", size=10, bold=True, min_w=185, pad=6, fill=GREEN_F, stroke=FIELD)
    b_cB, _, _ = textbox(497, 320, "Споживач\n(Видача кредитів / ACK)", size=10, min_w=160, pad=6, fill=GREEN_F, stroke=FIELD)
    f.extend([b_pB, b_chB, b_cB])
    f.append(arrow(497, 175, 497, 195, color=NEG, sw=1.5))
    f.append(arrow(497, 265, 497, 285, color=FIELD, sw=1.5))
    f.append(text(497, 395, "✓ Захист від OOM і згладжування піків\n✓ Контрольована затримка", size=9.5, color=FIELD, italic=True))

    # Панель 3: Unbounded Buffer
    f.append(rect(675, 60, 300, 370, fill=GRAY_F, stroke=MUTED, sw=1, rx=6))
    f.append(text(825, 85, "В. Необмежений буфер (Unbounded)", size=11, bold=True, color=POS))
    b_pC, _, _ = textbox(825, 140, "Продюсер\n(λ = 50 000 msg/s)", size=10, min_w=160, pad=6, fill=BLUE_F, stroke=NEG)
    b_chC, _, _ = textbox(825, 230, "Буфер без ліміту (N → ∞)\n[10 млн накопичених msg]\nЛатентність зростає до хвилин", size=10, bold=True, min_w=180, pad=6, fill=RED_F, stroke=POS)
    b_cC, _, _ = textbox(825, 320, "Споживач\n(μ = 10 000 msg/s — відстає)", size=10, min_w=160, pad=6, fill=FILL, stroke=MUTED)
    f.extend([b_pC, b_chC, b_cC])
    f.append(arrow(825, 175, 825, 195, color=NEG, sw=1.5))
    f.append(arrow(825, 265, 825, 285, color=MUTED, sw=1.5))
    f.append(text(825, 395, "✗ Ризик аварії OOM Killer у пам'яті\n✗ Некерована затримка (Lag)", size=9.5, color=POS, italic=True))

    render(out("buffering-and-backpressure.svg"), W, H, *f,
           title="Моделі місткості каналу та зворотний тиск")


# ── 4. channel-multiplexing: мультиплексування каналів у TCP ─────────────────
def fig_channel_multiplexing():
    W, H = 1000, 450
    f = []

    f.append(rect(10, 10, 980, 430, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 35, "Мультиплексування логічних каналів у єдиному фізичному з'єднанні (TCP Connection)", size=13.5, bold=True))

    # Ліва частина: 3 логічні канали клієнта
    b_l1, _, _ = textbox(110, 110, "Канал #1: Замовлення\n(OrderService)", size=10, bold=True, min_w=140, pad=5, fill=BLUE_F, stroke=NEG)
    b_l2, _, _ = textbox(110, 215, "Канал #2: Телеметрія\n(TelemetryStream)", size=10, bold=True, min_w=140, pad=5, fill=WARN_F, stroke=LINE)
    b_l3, _, _ = textbox(110, 320, "Канал #3: Heartbeat\n(Ping / Status)", size=10, bold=True, min_w=140, pad=5, fill=GREEN_F, stroke=FIELD)
    f.extend([b_l1, b_l2, b_l3])

    # Мультиплексор
    mux_box, _, _ = textbox(285, 215, "МУЛЬТИПЛЕКСОР\n(Framer / Mux)\n\n• Додавання ChID\n• Кадрування (Frames)\n• Чергування часток",
                            size=10, bold=True, min_w=125, pad=6, fill=GRAY_F, stroke=MUTED)
    f.append(mux_box)
    f.append(arrow(185, 110, 215, 185, color=NEG, sw=1.3))
    f.append(arrow(185, 215, 215, 215, color=LINE, sw=1.3))
    f.append(arrow(185, 320, 215, 245, color=FIELD, sw=1.3))

    # Фізичний канал (TCP Connection)
    f.append(rect(365, 175, 270, 80, fill="#2c3e50", stroke="#1a252f", sw=1.5, rx=6))
    f.append(text(500, 195, "Єдиний TCP Socket (Port 5672 / AMQP)", size=10.5, bold=True, color="#ecf0f1"))

    # Кадри всередині TCP
    f.append(rect(380, 215, 75, 30, fill=BLUE_F, stroke=NEG, sw=1, rx=3))
    f.append(text(417, 233, "Ch:1 | 256B", size=9, bold=True, color=NEG))

    f.append(rect(462, 215, 75, 30, fill=WARN_F, stroke=LINE, sw=1, rx=3))
    f.append(text(499, 233, "Ch:2 | 128B", size=9, bold=True, color=LINE))

    f.append(rect(545, 215, 75, 30, fill=GREEN_F, stroke=FIELD, sw=1, rx=3))
    f.append(text(582, 233, "Ch:3 | 32B", size=9, bold=True, color=FIELD))

    f.append(arrow(350, 215, 365, 215, color=MUTED, sw=1.5))
    f.append(arrow(635, 215, 650, 215, color=MUTED, sw=1.5))

    # Демультиплексор
    demux_box, _, _ = textbox(715, 215, "ДЕМУЛЬТИПЛЕКСОР\n(Demux / Parser)\n\n• Зчитування ChID\n• Маршрутизація в буфер\n• Збірка повідомлень",
                              size=10, bold=True, min_w=125, pad=6, fill=GRAY_F, stroke=MUTED)
    f.append(demux_box)

    # Права частина: 3 цільові буфери брокера
    b_r1, _, _ = textbox(890, 110, "Буфер каналу #1\n(Черга замовлень)", size=10, bold=True, min_w=140, pad=5, fill=BLUE_F, stroke=NEG)
    b_r2, _, _ = textbox(890, 215, "Буфер каналу #2\n(Потік телеметрії)", size=10, bold=True, min_w=140, pad=5, fill=WARN_F, stroke=LINE)
    b_r3, _, _ = textbox(890, 320, "Буфер каналу #3\n(Диспетчер Ping)", size=10, bold=True, min_w=140, pad=5, fill=GREEN_F, stroke=FIELD)
    f.extend([b_r1, b_r2, b_r3])

    f.append(arrow(785, 185, 815, 110, color=NEG, sw=1.3))
    f.append(arrow(785, 215, 815, 215, color=LINE, sw=1.3))
    f.append(arrow(785, 245, 815, 320, color=FIELD, sw=1.3))

    f.append(text(500, 405, "Економія ресурсів ОС: замість тисяч важких TCP-з'єднань працює єдиний потік із віртуальними каналами", size=10.5, color=FIELD, italic=True))

    render(out("channel-multiplexing.svg"), W, H, *f,
           title="Мультиплексування логічних каналів у фізичному з'єднанні")


if __name__ == "__main__":
    fig_decoupling_dimensions()
    fig_channel_taxonomy()
    fig_buffering_and_backpressure()
    fig_channel_multiplexing()
    print("Done generating 4 figures.")
