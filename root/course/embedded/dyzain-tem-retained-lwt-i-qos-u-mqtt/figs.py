# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. topic-hierarchy-tree: простір назв та межі доступу в IoT-парку ─────────
def fig_topic_hierarchy():
    W, H = 940, 480
    p = []

    # Заголовок / Кореневий рівень
    p.append(rect(340, 20, 260, 44, fill="#e9eefb", stroke=NEG, sw=2, rx=8))
    p.append(text(470, 46, "Організація / Підприємство (agro-corp)", size=12, color=NEG, bold=True))

    # Стрілка вниз до об'єкта
    p.append(arrow(470, 64, 470, 96, color=LINE, sw=1.5))

    # Рівень об'єкта (Site / Location)
    p.append(rect(360, 96, 220, 38, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    p.append(text(470, 120, "Локація: site-kyiv-01", size=12, color=INK, bold=True))

    # Стрілка вниз до ідентифікатора пристрою
    p.append(arrow(470, 134, 470, 166, color=LINE, sw=1.5))

    # Рівень пристрою (Device ID)
    p.append(rect(340, 166, 260, 40, fill="#fdf0e6", stroke="#c07a2e", sw=2, rx=6))
    p.append(text(470, 191, "Вузол: dev-stm32-8f2a", size=13, color="#c07a2e", bold=True))

    # Розгалуження на 4 функціональні гілки
    xs = [110, 330, 570, 800]
    labels = [
        ("telemetry/...", "Телеметрія (QoS 0/1)", "sensor/temp, soil_moist\nПотік подій без Retain", "#eef6ef", FIELD),
        ("state", "Стан вузла (QoS 1)", "online / offline\nLWT + Retain = 1", "#fdf0e6", "#c07a2e"),
        ("cmd/...", "Команди (QoS 1/2)", "valve/open, restart\nБекенд -> Вузол (No Retain)", "#fbebee", POS),
        ("config/...", "Конфігурація (QoS 1)", "sample_rate, threshold\nRetain = 1 (Бажаний стан)", "#e9eefb", NEG),
    ]

    # Лінії розгалуження
    p.append(line(xs[0], 230, xs[3], 230, color=LINE, sw=1.5))
    p.append(line(470, 206, 470, 230, color=LINE, sw=1.5))

    for i, x in enumerate(xs):
        p.append(arrow(x, 230, x, 256, color=LINE, sw=1.5))
        topic_hdr, role_title, desc, bg_col, border_col = labels[i]
        
        bw = 190
        p.append(rect(x - bw/2, 256, bw, 130, fill=bg_col, stroke=border_col, sw=1.8, rx=6))
        p.append(text(x, 280, topic_hdr, size=13, color=border_col, bold=True))
        p.append(text(x, 302, role_title, size=11, color=INK, bold=True))
        p.append(mtext(x, 328, desc, size=10, color=MUTED, lh=1.3))

    # Нижній блок: Маски підписок (Wildcards) та ACL
    p.append(rect(30, 410, 880, 56, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(470, 430, "Шаблони підписок (Wildcards) та контроль прав (ACL):", size=11, color=INK, bold=True))
    p.append(text(240, 452, "Дашборд моніторингу: agro-corp/+/+/telemetry/# (Тільки читання)", size=10.5, color=FIELD))
    p.append(text(680, 452, "Сервіс команд: agro-corp/site-kyiv-01/+/cmd/+ (Запис дозволено)", size=10.5, color=POS))

    render(os.path.join(OUT, "topic-hierarchy-tree.svg"), W, H, *p,
           title="Ієрархія простору назв MQTT: функціональне розділення топіків та межі прав")


# ── 2. lwt-lifecycle-state-machine: життєвий цикл LWT та виявлення аварій ─────
def fig_lwt_lifecycle():
    W, H = 940, 490
    p = []

    # Колони учасників: Клієнт (Вузол), Брокер, Передплатник (Бекенд)
    cx_node = 160
    cx_broker = 470
    cx_sub = 780

    # Шапки
    p.append(rect(cx_node - 80, 16, 160, 36, fill="#fdf0e6", stroke="#c07a2e", sw=1.8, rx=6))
    p.append(text(cx_node, 39, "Вузол (Client)", size=12, color=INK, bold=True))

    p.append(rect(cx_broker - 80, 16, 160, 36, fill="#e9eefb", stroke=NEG, sw=1.8, rx=6))
    p.append(text(cx_broker, 39, "MQTT-брокер", size=12, color=INK, bold=True))

    p.append(rect(cx_sub - 80, 16, 160, 36, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(cx_sub, 39, "Бекенд (Subscriber)", size=12, color=INK, bold=True))

    # Вертикальні лінії життя
    p.append(line(cx_node, 52, cx_node, 460, color="#d0d5dd", sw=1.5, dash="4,4"))
    p.append(line(cx_broker, 52, cx_broker, 460, color="#d0d5dd", sw=1.5, dash="4,4"))
    p.append(line(cx_sub, 52, cx_sub, 460, color="#d0d5dd", sw=1.5, dash="4,4"))

    # 1. Підписка бекенду
    y1 = 80
    p.append(arrow(cx_sub, y1, cx_broker, y1, color=FIELD, sw=1.6))
    p.append(text(625, y1 - 8, "SUBSCRIBE node/+/state", size=10.5, color=FIELD))

    # 2. Вузол надсилає CONNECT з LWT
    y2 = 120
    p.append(arrow(cx_node, y2, cx_broker, y2, color="#c07a2e", sw=1.6))
    p.append(text(315, y2 - 8, "CONNECT (Will: topic=state, msg='offline', Retain=1, QoS=1)", size=10, color="#c07a2e"))

    # 3. CONNACK від брокера
    y3 = 155
    p.append(arrow(cx_broker, y3, cx_node, y3, color=NEG, sw=1.6))
    p.append(text(315, y3 - 8, "CONNACK (З'єднання прийнято, LWT зареєстровано)", size=10, color=NEG))

    # 4. Вузол публікує свій онлайн-статус
    y4 = 195
    p.append(arrow(cx_node, y4, cx_broker, y4, color=FIELD, sw=1.6))
    p.append(text(315, y4 - 8, "PUBLISH node/state 'online' (Retain=1)", size=10.5, color=FIELD))

    p.append(arrow(cx_broker, y4 + 15, cx_sub, y4 + 15, color=FIELD, sw=1.6))
    p.append(text(625, y4 + 7, "PUBLISH node/state 'online'", size=10.5, color=FIELD))

    # 5. Аварія: Раптове знеструмлення або падіння модему
    y5 = 265
    p.append(rect(cx_node - 90, y5 - 14, 180, 28, fill="#fbebee", stroke=POS, sw=1.5, rx=4))
    p.append(text(cx_node, y5 + 4, "Раптовий обрив TCP / Живлення", size=10.5, color=POS, bold=True))

    # Таймаут KeepAlive на брокері
    y6 = 325
    p.append(rect(cx_broker - 100, y6 - 16, 200, 32, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    p.append(text(cx_broker, y6 + 4, "KeepAlive таймаут (1.5 * t)", size=10.5, color=INK, bold=True))

    # 6. Брокер самостійно публікує LWT
    y7 = 385
    p.append(arrow(cx_broker, y7, cx_sub, y7, color=POS, sw=2.0))
    p.append(text(625, y7 - 10, "Брокер надсилає LWT: node/state 'offline' (Retain=1)", size=11, color=POS, bold=True))

    # 7. Результат для нового підписника
    y8 = 435
    p.append(rect(cx_sub - 120, y8 - 14, 240, 26, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    p.append(text(cx_sub, y8 + 4, "Бекенд миттєво фіксує аварію вузла", size=10, color=INK))

    render(os.path.join(OUT, "lwt-lifecycle-state-machine.svg"), W, H, *p,
           title="Життєвий цикл Last Will and Testament: виявлення аварійного відключення вузла")


# ── 3. retained-state-pattern: збереження стану проти потоку подій ─────────────
def fig_retained_state():
    W, H = 920, 420
    p = []

    # Лівий блок: Звичайний потік подій (Retain = 0)
    p.append(rect(40, 30, 400, 360, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))
    p.append(rect(40, 30, 400, 40, fill="#fbebee", stroke=POS, sw=1.5, rx=8))
    p.append(text(240, 55, "Потік телеметрії (Retain = 0)", size=13, color=POS, bold=True))

    p.append(text(240, 95, "Вузол публікує раз на 15 хв: temp = 22.4", size=11, color=INK))
    p.append(line(80, 130, 400, 130, color="#e3e6ec", sw=1))
    
    p.append(text(240, 160, "12:00 -> Публікація #1 (Отримали активні підписники)", size=10, color=MUTED))
    p.append(text(240, 200, "12:07 -> Новий клієнт підписався на тему", size=10.5, color=POS, bold=True))
    p.append(text(240, 240, "Брокер нічого не надсилає (пам'ять порожня)", size=11, color=POS))
    p.append(text(240, 275, "Клієнт чекає 8 хвилин у повній невідомості!", size=10.5, color=MUTED, italic=True))
    
    p.append(rect(70, 315, 340, 50, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    p.append(text(240, 336, "Призначення: безперервний потік часових рядів,", size=10, color=INK))
    p.append(text(240, 354, "де втрата проміжного відліку допустима", size=10, color=MUTED))

    # Правий блок: Патерн стану з Retained (Retain = 1)
    p.append(rect(480, 30, 400, 360, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))
    p.append(rect(480, 30, 400, 40, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(680, 55, "Патерн стану (Retain = 1)", size=13, color=FIELD, bold=True))

    p.append(text(680, 95, "Вузол публікує зміну стану: mode = 'AUTO'", size=11, color=INK))
    p.append(line(520, 130, 840, 130, color="#e3e6ec", sw=1))
    
    p.append(text(680, 160, "Брокер кешує останнє повідомлення в пам'яті", size=10.5, color=INK))
    p.append(text(680, 200, "12:07 -> Новий клієнт підписався на тему", size=10.5, color=FIELD, bold=True))
    p.append(text(680, 240, "Брокер МИТТЄВО надсилає останній стан!", size=11, color=FIELD, bold=True))
    p.append(text(680, 275, "Клієнт одразу знає поточний режим роботи пристрою", size=10.5, color=MUTED, italic=True))

    p.append(rect(510, 315, 340, 50, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    p.append(text(680, 336, "Призначення: цифровий двійник, реле, статус LWT,", size=10, color=INK))
    p.append(text(680, 354, "очищення: публікація порожнього payload (len=0)", size=10, color=MUTED))

    render(os.path.join(OUT, "retained-state-pattern.svg"), W, H, *p,
           title="Порівняння звичайного потоку повідомлень та збереженого стану (Retained)")


# ── 4. qos-exchange-sequences: рівні гарантії QoS 0, 1, 2 та оверхед ──────────
def fig_qos_sequences():
    W, H = 940, 470
    p = []

    # 3 блоки під QoS 0, QoS 1, QoS 2
    cols = [
        ("QoS 0: At most once", "Надіслав і забув", 40, 270, "#f4f6f8", MUTED),
        ("QoS 1: At least once", "Щонайменше один раз", 335, 270, "#e9eefb", NEG),
        ("QoS 2: Exactly once", "Рівно один раз (4 фази)", 630, 270, "#eef6ef", FIELD),
    ]

    for title, sub, x, w, bg_col, stroke_col in cols:
        p.append(rect(x, 20, w, 430, fill="#ffffff", stroke="#d0d5dd", sw=1.5, rx=8))
        p.append(rect(x, 20, w, 44, fill=bg_col, stroke=stroke_col, sw=1.5, rx=8))
        p.append(text(x + w/2, 42, title, size=12, color=stroke_col, bold=True))
        p.append(text(x + w/2, 57, sub, size=10, color=INK))

    # QoS 0 деталі
    q0_x1, q0_x2 = 75, 275
    p.append(text(q0_x1, 90, "Клієнт", size=11, color=INK, bold=True))
    p.append(text(q0_x2, 90, "Брокер", size=11, color=INK, bold=True))
    p.append(line(q0_x1, 105, q0_x1, 330, color="#d0d5dd", sw=1.2, dash="3,3"))
    p.append(line(q0_x2, 105, q0_x2, 330, color="#d0d5dd", sw=1.2, dash="3,3"))

    p.append(arrow(q0_x1, 140, q0_x2, 160, color=LINE, sw=1.8))
    p.append(text(175, 138, "PUBLISH (без ID)", size=10.5, color=INK))
    p.append(text(175, 210, "Немає квитування", size=10.5, color=MUTED, italic=True))
    p.append(text(175, 230, "Пам'ять RAM = 0", size=10.5, color=FIELD, bold=True))
    p.append(text(175, 250, "Обертів RTT = 0.5", size=10.5, color=INK))

    p.append(rect(50, 350, 250, 85, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(175, 372, "Втрати при обриві TCP: ТАК", size=10, color=POS, bold=True))
    p.append(text(175, 392, "Дублікати: НІ", size=10, color=INK))
    p.append(text(175, 412, "Застосування: сенсори 10 Гц", size=10, color=MUTED))

    # QoS 1 деталі
    q1_x1, q1_x2 = 370, 570
    p.append(text(q1_x1, 90, "Клієнт", size=11, color=INK, bold=True))
    p.append(text(q1_x2, 90, "Брокер", size=11, color=INK, bold=True))
    p.append(line(q1_x1, 105, q1_x1, 330, color="#d0d5dd", sw=1.2, dash="3,3"))
    p.append(line(q1_x2, 105, q1_x2, 330, color="#d0d5dd", sw=1.2, dash="3,3"))

    p.append(arrow(q1_x1, 140, q1_x2, 160, color=NEG, sw=1.8))
    p.append(text(470, 138, "PUBLISH (ID = 101)", size=10.5, color=NEG))
    
    p.append(arrow(q1_x2, 195, q1_x1, 215, color=NEG, sw=1.8))
    p.append(text(470, 193, "PUBACK (ID = 101)", size=10.5, color=NEG))
    
    p.append(text(470, 250, "Обертів RTT = 1.0", size=10.5, color=INK))
    p.append(text(470, 270, "Буфер у RAM до PUBACK", size=10.5, color="#c07a2e", bold=True))

    p.append(rect(345, 350, 250, 85, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(470, 372, "Втрати: НІ (перевідправка)", size=10, color=FIELD, bold=True))
    p.append(text(470, 392, "Дублікати: МОЖЛИВІ (DUP=1)", size=10, color=POS, bold=True))
    p.append(text(470, 412, "Застосування: тривоги, стан", size=10, color=MUTED))

    # QoS 2 деталі
    q2_x1, q2_x2 = 665, 865
    p.append(text(q2_x1, 90, "Клієнт", size=11, color=INK, bold=True))
    p.append(text(q2_x2, 90, "Брокер", size=11, color=INK, bold=True))
    p.append(line(q2_x1, 105, q2_x1, 330, color="#d0d5dd", sw=1.2, dash="3,3"))
    p.append(line(q2_x2, 105, q2_x2, 330, color="#d0d5dd", sw=1.2, dash="3,3"))

    p.append(arrow(q2_x1, 125, q2_x2, 140, color=FIELD, sw=1.6))
    p.append(text(765, 123, "1. PUBLISH (ID = 102)", size=10, color=FIELD))
    
    p.append(arrow(q2_x2, 165, q2_x1, 180, color=FIELD, sw=1.6))
    p.append(text(765, 163, "2. PUBREC (Отримано)", size=10, color=FIELD))

    p.append(arrow(q2_x1, 205, q2_x2, 220, color=FIELD, sw=1.6))
    p.append(text(765, 203, "3. PUBREL (Звільнити)", size=10, color=FIELD))

    p.append(arrow(q2_x2, 245, q2_x1, 260, color=FIELD, sw=1.6))
    p.append(text(765, 243, "4. PUBCOMP (Завершено)", size=10, color=FIELD))

    p.append(text(765, 290, "Обертів RTT = 2.0 (4 кадри)", size=10.5, color=POS, bold=True))

    p.append(rect(640, 350, 250, 85, fill="#f4f6f8", stroke=LINE, sw=1, rx=6))
    p.append(text(765, 372, "Втрати: НІ, Дублікати: НІ", size=10, color=FIELD, bold=True))
    p.append(text(765, 392, "Оверхед: у 4 рази більше пакетів", size=10, color=POS, bold=True))
    p.append(text(765, 412, "Застосування: транзакції, білінг", size=10, color=MUTED))

    render(os.path.join(OUT, "qos-exchange-sequences.svg"), W, H, *p,
           title="Послідовності квитування для рівнів QoS 0, QoS 1 та QoS 2 у протоколі MQTT")


if __name__ == "__main__":
    fig_topic_hierarchy()
    fig_lwt_lifecycle()
    fig_retained_state()
    fig_qos_sequences()
    print("All figures generated successfully.")
