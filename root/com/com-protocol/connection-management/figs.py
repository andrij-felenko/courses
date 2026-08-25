# -*- coding: utf-8 -*-
"""Фігури до теми «Керування з'єднаннями, пулінг та keep-alive».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"    # тепле виділення (таймер, увага)
SOFT_B = "#eef3fd"   # світло-синє тло
SOFT_G = "#eaf7ef"   # світло-зелене тло
SOFT_A = "#fff6e0"   # світло-бурштинове тло
SOFT_R = "#fdecea"   # світло-червоне тло


# ── 1. Життєвий цикл керованого з'єднання ─────────────────────────────────────
def fig_lifecycle():
    W, H = 940, 360
    f = [text(W / 2, 28, "Життєвий цикл з'єднання: від відкриття до пулінгу й закриття",
              size=15, bold=True)]

    # Стан 1: Створення
    b1, _, _ = textbox(130, 100, "CONNECTING\nрукостискання\nSYN / TLS ClientHello",
                       size=11.5, fill=SOFT_B, stroke=NEG, bold=True)
    # Стан 2: Активне (орендоване)
    b2, _, _ = textbox(410, 100, "ACTIVE (Оренда)\nпередача даних\nзапит / відповідь",
                       size=11.5, fill=SOFT_G, stroke=FIELD, bold=True)
    # Стан 3: У пулі (очікування)
    b3, _, _ = textbox(730, 100, "IDLE (У пулі)\nочікує повторного запиту\nLIFO-стек",
                       size=11.5, fill=SOFT_A, stroke=AMBER, bold=True)
    # Стан 4: Перевірка здоров'я
    b4, _, _ = textbox(570, 250, "VALIDATION\nперевірка MSG_PEEK\nживе чи закрите?",
                       size=11.5, fill=FILL, stroke=LINE, bold=True)
    # Стан 5: Закриття / TIME_WAIT
    b5, _, _ = textbox(190, 250, "CLOSING / TIME_WAIT\nзавершення (FIN/ACK)\nзвільнення ресурсів",
                       size=11.5, fill=SOFT_R, stroke=POS, bold=True)

    f += [b1, b2, b3, b4, b5]

    # Стрілки переходів
    # CONNECTING -> ACTIVE
    f.append(arrow(210, 100, 310, 100, color=FIELD, sw=2.0))
    f.append(text(260, 85, "з'єднано", size=10.5, color=FIELD, italic=True))

    # ACTIVE -> IDLE (повернення в пул)
    f.append(arrow(510, 90, 630, 90, color=AMBER, sw=1.8))
    f.append(text(570, 75, "повернення в пул", size=10.5, color=AMBER, italic=True))

    # IDLE -> VALIDATION -> ACTIVE (оренда з пулу)
    f.append(arrow(730, 150, 730, 250, color=LINE, sw=1.6))
    f.append(text(795, 200, "нова оренда", size=10.5, color=LINE, italic=True))

    f.append(arrow(650, 250, 490, 250, color=FIELD, sw=1.8))
    f.append(arrow(410, 220, 410, 155, color=FIELD, sw=1.8))
    f.append(text(445, 235, "живе", size=10.5, color=FIELD, italic=True))

    # IDLE / VALIDATION -> CLOSING (таймаут або віддалений FIN)
    f.append(arrow(500, 275, 295, 275, color=POS, sw=1.8))
    f.append(text(400, 295, "таймаут / помилка / FIN", size=10.5, color=POS, italic=True))

    # ACTIVE -> CLOSING (помилка під час передачі)
    f.append(arrow(340, 140, 230, 215, color=POS, sw=1.6))
    f.append(text(265, 160, "збій зв'язку", size=10.5, color=POS, italic=True))

    return render(os.path.join(IMG, "lifecycle.svg"), W, H, *f)


# ── 2. Внутрішня архітектура пулу з'єднань ──────────────────────────────────────
def fig_pooling_arch():
    W, H = 940, 370
    f = [text(W / 2, 28, "Архітектура пулу з'єднань: LIFO-стек очікування та контроль оренди",
              size=15, bold=True)]

    # Клієнтські потоки
    t1, _, _ = textbox(120, 85, "Потік 1\nacquire()", size=11, fill=SOFT_B, stroke=NEG)
    t2, _, _ = textbox(120, 165, "Потік 2\nacquire()", size=11, fill=SOFT_B, stroke=NEG)
    t3, _, _ = textbox(120, 245, "Потік 3\n(чекає слот)", size=11, fill=SOFT_R, stroke=POS)
    f += [t1, t2, t3]

    # Семафор / Обмежувач
    sem_box, _, _ = textbox(310, 165, "Семафор / М'ютекс\nліміт MaxActive (напр. 10)\nчерга очікування",
                            size=11, fill=FILL, stroke=LINE, bold=True)
    f.append(sem_box)

    f.append(arrow(185, 85, 230, 140, color=NEG, sw=1.6))
    f.append(arrow(185, 165, 230, 165, color=NEG, sw=1.6))
    f.append(arrow(185, 245, 230, 190, color=POS, sw=1.6))

    # LIFO Стек idle-з'єднань
    stack_x, stack_y, stack_w, stack_h = 440, 95, 200, 210
    f.append(rect(stack_x, stack_y, stack_w, stack_h, fill=SOFT_A, stroke=AMBER, sw=1.5))
    f.append(text(stack_x + stack_w / 2, stack_y - 12, "Стек вільних з'єднань (LIFO)",
                  size=11.5, color=AMBER, bold=True))

    # Елементи стека
    f.append(fitbox(stack_x + 15, stack_y + 15, stack_w - 30, 36, "Сокет #4 (щойно повернений)",
                    size=10.5, fill="#ffffff", stroke=AMBER))
    f.append(fitbox(stack_x + 15, stack_y + 60, stack_w - 30, 36, "Сокет #3 (простій 2 с)",
                    size=10.5, fill="#ffffff", stroke=AMBER))
    f.append(fitbox(stack_x + 15, stack_y + 105, stack_w - 30, 36, "Сокет #2 (простій 15 с)",
                    size=10.5, fill="#ffffff", stroke=MUTED))
    f.append(fitbox(stack_x + 15, stack_y + 150, stack_w - 30, 36, "Сокет #1 (простій 45 с → таймаут)",
                    size=10.5, fill=SOFT_R, stroke=POS))

    # Стрілка видачі із вершини стека
    f.append(arrow(390, 150, 440, 120, color=FIELD, sw=1.8))
    f.append(arrow(640, 120, 720, 120, color=FIELD, sw=1.8))

    # Блок активної оренди (Lease)
    lease_box, _, _ = textbox(810, 120, "RAII Lease\n`ConnectionLease`\nвикористання в запиті",
                              size=11, fill=SOFT_G, stroke=FIELD, bold=True)
    f.append(lease_box)

    # Зворотна стрілка повернення в пул
    f.append(arrow(810, 170, 810, 325, color=NEG, sw=1.8))
    f.append(line(810, 325, 540, 325, color=NEG, sw=1.8))
    f.append(arrow(540, 325, 540, 305, color=NEG, sw=1.8))
    f.append(text(675, 340, "деструктор Lease: повернення у верхівку LIFO", size=10.5, color=NEG, italic=True))

    return render(os.path.join(IMG, "pooling-architecture.svg"), W, H, *f)


# ── 3. Гонитва застарілого з'єднання (Stale connection race) ─────────────────
def fig_stale_race():
    W, H = 940, 370
    f = [text(W / 2, 28, "Гонітва застарілого з'єднання: перетин клієнтського запиту й серверного FIN",
              size=15, bold=True)]

    # Вертикальні осі часу
    c_x, s_x = 220, 720
    f.append(text(c_x, 65, "Клієнт (Пул з'єднань)", size=13, bold=True, color=NEG))
    f.append(text(s_x, 65, "Сервер (Бекенд)", size=13, bold=True, color=FIELD))

    f.append(line(c_x, 80, c_x, 340, color=LINE, sw=1.5))
    f.append(line(s_x, 80, s_x, 340, color=LINE, sw=1.5))

    # Події по часу
    # t1: Сервер вирішує закрити через idle timeout
    f.append(text(s_x + 12, 115, "1. Спрацював idle-таймаут (30 с)", size=10.5, color=POS, anchor="start"))
    f.append(text(s_x + 12, 130, "   Сервер надсилає TCP FIN", size=10.5, color=POS, anchor="start"))

    # t2: Клієнт бере сокет із пулу
    f.append(text(c_x - 12, 135, "2. Потік орендує сокет із пулу", size=10.5, color=NEG, anchor="end"))
    f.append(text(c_x - 12, 150, "   Клієнт викликає send(HTTP_REQ)", size=10.5, color=NEG, anchor="end"))

    # Перетин у дорозі
    # Серверний FIN летить ліворуч (t=130 -> t=220)
    f.append(arrow(s_x, 135, c_x, 225, color=POS, sw=1.8))
    f.append(text(480, 160, "TCP FIN (закриття сервера)", size=11, color=POS, bold=True))

    # Клієнтський запит летить праворуч (t=150 -> t=240)
    f.append(arrow(c_x, 155, s_x, 245, color=NEG, sw=1.8))
    f.append(text(480, 220, "HTTP POST /api/data (запит клієнта)", size=11, color=NEG, bold=True))

    # Точка зіткнення
    f.append(circle(470, 190, 8, fill="#ffffff", stroke=POS, sw=2.0))
    f.append(text(470, 194, "!", size=11, color=POS, bold=True))

    # Сервер отримує дані на закритому сокеті -> надсилає RST
    f.append(text(s_x + 12, 255, "3. Дані на закритому сокеті!", size=10.5, color=POS, anchor="start"))
    f.append(text(s_x + 12, 270, "   Сервер надсилає TCP RST", size=10.5, color=POS, anchor="start"))

    f.append(arrow(s_x, 275, c_x, 315, color=POS, sw=2.0))
    f.append(text(480, 290, "TCP RST (ECONNRESET)", size=11, color=POS, bold=True))

    # Клієнт отримує помилку і робить повтор
    f.append(text(c_x - 12, 320, "4. Пул бачить помилку на старому сокеті,", size=10.5, color=FIELD, anchor="end"))
    f.append(text(c_x - 12, 335, "   прозоро відкриває новий і повторює", size=10.5, color=FIELD, anchor="end", bold=True))

    return render(os.path.join(IMG, "stale-race.svg"), W, H, *f)


# ── 4. Рівні Keep-Alive: транспортний проти прикладного ───────────────────────
def fig_keepalive_layers():
    W, H = 940, 360
    f = [text(W / 2, 28, "Рівні Keep-Alive: чому зонд ядра не гарантує працездатність процесу",
              size=15, bold=True)]

    # Ліва колонка: TCP Keep-Alive (Ядро <-> Ядро)
    f.append(text(240, 65, "Транспортний рівень (TCP Keep-Alive)", size=13, bold=True, color=NEG))
    f.append(rect(50, 85, 380, 240, fill=SOFT_B, stroke=NEG, sw=1.5))

    # Схема ядро-ядро
    k1, _, _ = textbox(130, 140, "Ядро ОС\nКлієнт", size=11, fill="#ffffff", stroke=NEG)
    k2, _, _ = textbox(350, 140, "Ядро ОС\nСервер", size=11, fill="#ffffff", stroke=NEG)
    app2_dead, _, _ = textbox(350, 240, "Застосунок сервера\nDEADLOCK / ЗАВИС",
                              size=11, fill=SOFT_R, stroke=POS, bold=True)
    f += [k1, k2, app2_dead]

    f.append(arrow(180, 130, 300, 130, color=NEG, sw=1.6))
    f.append(text(240, 120, "ACK-зонд ядра", size=10, color=NEG))
    f.append(arrow(300, 150, 180, 150, color=NEG, sw=1.6))
    f.append(text(240, 165, "ACK-відповідь ядра", size=10, color=NEG))

    f.append(text(240, 290, "Ядро відповідає автоматично, навіть коли\nзастосунок повністю заблокований!",
                  size=10.5, color=POS, bold=True))

    # Права колонка: Прикладний Keep-Alive (Застосунок <-> Застосунок)
    f.append(text(700, 65, "Прикладний рівень (Heartbeat / HTTP/2 PING)", size=13, bold=True, color=FIELD))
    f.append(rect(510, 85, 380, 240, fill=SOFT_G, stroke=FIELD, sw=1.5))

    a1, _, _ = textbox(590, 140, "Застосунок\nКлієнт", size=11, fill="#ffffff", stroke=FIELD)
    a2, _, _ = textbox(810, 140, "Застосунок\nСервер (робочий)", size=11, fill="#ffffff", stroke=FIELD)
    f += [a1, a2]

    f.append(arrow(645, 130, 750, 130, color=FIELD, sw=1.6))
    f.append(text(700, 120, "PING / Heartbeat", size=10, color=FIELD))
    f.append(arrow(750, 150, 645, 150, color=FIELD, sw=1.6))
    f.append(text(700, 165, "PONG / Відповідь", size=10, color=FIELD))

    f.append(text(700, 260, "Перевіряє весь наскрізний шлях:\nі мережу, і чергу циклу подій застосунку.",
                  size=10.5, color=FIELD, bold=True))

    return render(os.path.join(IMG, "keepalive-layers.svg"), W, H, *f)


def main():
    fig_lifecycle()
    fig_pooling_arch()
    fig_stale_race()
    fig_keepalive_layers()
    print("Всі 4 фігури згенеровано успішно.")

if __name__ == "__main__":
    main()
