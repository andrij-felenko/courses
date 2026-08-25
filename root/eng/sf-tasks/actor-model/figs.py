# -*- coding: utf-8 -*-
"""Фігури до теми «Модель акторів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори ролей
ACTOR_FILL  = "#eaf2fd"
ACTOR_LINE  = "#2457d6"
STATE_FILL  = "#fef5e7"
STATE_LINE  = "#d35400"
QUEUE_FILL  = "#eafaf1"
QUEUE_LINE  = "#27ae60"
FAIL_FILL   = "#fdecea"
FAIL_LINE   = "#c0392b"
WARN_FILL   = "#fff6e0"
WARN_LINE   = "#caa24a"

def boxlabel(f, x, y, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=12, sw=1.5, rx=6):
    """Прямокутник із підписом по центру; багаторядковий через список або \\n."""
    if isinstance(s, str) and "\n" in s:
        s = s.split("\n")
    if isinstance(s, list):
        f.append(fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke, sw=sw, color=tcol, rx=rx))
        return
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx))
    fs = fit_font(s, w - 14, size, bold=True)
    f.append(text(x + w / 2, y + h / 2 + fs * 0.35, s, size=fs, color=tcol, bold=True))

def note(f, cx, y, w, lines, fill=WARN_FILL, stroke=WARN_LINE, size=11):
    """Рамка-висновок знизу фігури."""
    f.append(fitbox(cx - w / 2, y, w, 18 + size * 1.35 * len(lines), lines,
                    size=size, fill=fill, stroke=stroke))


# ── 1. Анатомія актора ───────────────────────────────────────────────────────
def fig_actor_anatomy():
    W, H = 880, 430
    f = [text(W / 2, 28, "Анатомія актора: повна ізоляція стану та поштова скринька", size=16, bold=True)]
    f.append(text(W / 2, 48, "Ніякого спільного доступу до пам'яті: взаємодія виключно через неблокувальні повідомлення",
                  size=11, color=MUTED, italic=True))

    # Зовнішній контур актора
    f.append(rect(240, 75, 590, 265, fill="#f8faff", stroke=ACTOR_LINE, sw=2, rx=10))
    f.append(text(535, 100, "Межа ізоляції актора (Actor Boundary / PID)", size=13, color=ACTOR_LINE, bold=True))

    # Поштова скринька (Mailbox)
    f.append(rect(265, 120, 190, 200, fill=QUEUE_FILL, stroke=QUEUE_LINE, sw=1.6, rx=6))
    f.append(text(360, 142, "Поштова скринька (Mailbox)", size=11, color=QUEUE_LINE, bold=True))
    f.append(text(360, 158, "FIFO черга повідомлень", size=10, color=MUTED))

    # Елементи черги
    boxlabel(f, 280, 172, 160, 28, "Повідомлення #3", fill="#ffffff", stroke=QUEUE_LINE, size=10)
    boxlabel(f, 280, 208, 160, 28, "Повідомлення #2", fill="#ffffff", stroke=QUEUE_LINE, size=10)
    boxlabel(f, 280, 244, 160, 28, "Повідомлення #1 (голова)", fill="#d5f5e3", stroke=QUEUE_LINE, size=10, tcol=QUEUE_LINE)
    f.append(text(360, 295, "Послідовне вилучення", size=10, color=MUTED, italic=True))

    # Вхідні стрілки ззовні
    boxlabel(f, 30, 130, 150, 42, ["Клієнт / Інший актор", "Відправка msg"], fill="#ffffff", stroke=LINE, size=10)
    boxlabel(f, 30, 230, 150, 42, ["Мережевий сокет", "Відправка msg"], fill="#ffffff", stroke=LINE, size=10)
    f.append(arrow(180, 151, 260, 190, color=LINE, sw=1.6))
    f.append(arrow(180, 251, 260, 210, color=LINE, sw=1.6))
    f.append(text(215, 162, "send(!)", size=10, color=MUTED, bold=True))

    # Внутрішній стан (Private State)
    f.append(rect(480, 120, 155, 200, fill=STATE_FILL, stroke=STATE_LINE, sw=1.6, rx=6))
    f.append(text(557, 142, "Приватний стан", size=11, color=STATE_LINE, bold=True))
    f.append(text(557, 158, "(Private State)", size=10, color=MUTED))
    boxlabel(f, 495, 175, 125, 26, "count = 42", fill="#ffffff", stroke=STATE_LINE, size=10)
    boxlabel(f, 495, 207, 125, 26, "session_id = 0x9A", fill="#ffffff", stroke=STATE_LINE, size=10)
    boxlabel(f, 495, 239, 125, 26, "peers = [Pid1, ...]", fill="#ffffff", stroke=STATE_LINE, size=10)
    f.append(text(557, 295, "Прямий доступ ззовні ЗАБОРОНЕНО", size=9.5, color=STATE_LINE, bold=True))

    # Поведінка (Behavior)
    f.append(rect(655, 120, 155, 200, fill=ACTOR_FILL, stroke=ACTOR_LINE, sw=1.6, rx=6))
    f.append(text(732, 142, "Поведінка (Behavior)", size=11, color=ACTOR_LINE, bold=True))
    f.append(text(732, 158, "Обробник повідомлень", size=10, color=MUTED))
    boxlabel(f, 670, 175, 125, 46, ["receive(msg) ->", "нова поведінка"], fill="#ffffff", stroke=ACTOR_LINE, size=9.5)
    boxlabel(f, 670, 230, 125, 46, ["become(new_state)", "зміна логіки"], fill="#ffffff", stroke=ACTOR_LINE, size=9.5)
    f.append(text(732, 295, "Однопотокова обробка", size=9, color=ACTOR_LINE, italic=True))

    # Стрілки між компонентами
    f.append(arrow(455, 258, 478, 258, color=LINE, sw=1.6))
    f.append(arrow(635, 220, 653, 220, color=LINE, sw=1.6))

    note(f, W / 2, 355, 800,
         ["Актор складається з трьох частин: поштової скриньки, ізольованого приватного стану та поточної поведінки.",
          "Повідомлення обробляються строго по одному — це усуває стан гонки без застосування замків чи блокувань."])
    render(os.path.join(IMG, "actor-anatomy.svg"), W, H, *f)


# ── 2. Три аксіоми Г'юїтта ──────────────────────────────────────────────────
def fig_hewitt_axioms():
    W, H = 880, 420
    f = [text(W / 2, 28, "Три аксіоми Карла Г'юїтта: реакція на вхідне повідомлення", size=16, bold=True)]
    f.append(text(W / 2, 48, "У відповідь на кожне вилучене повідомлення актор може виконати виключно ці три дії",
                  size=11, color=MUTED, italic=True))

    # Центральний вузол: Актор опрацьовує одне повідомлення
    boxlabel(f, 60, 175, 200, 70, ["Актор опрацьовує", "вхідне повідомлення M", "(одиничний крок)"],
             fill=ACTOR_FILL, stroke=ACTOR_LINE, size=11.5, tcol=ACTOR_LINE)

    # 3 розгалуження праворуч
    # Дія 1: Відправка повідомлень
    boxlabel(f, 370, 80, 220, 64, ["1. Надіслати повідомлення", "скінченній кількості", "відомих адрес (PID)"],
             fill=QUEUE_FILL, stroke=QUEUE_LINE, size=11, tcol=QUEUE_LINE)
    boxlabel(f, 640, 80, 200, 64, ["send(pid_b, Msg1)", "send(pid_c, Msg2)"],
             fill="#ffffff", stroke=QUEUE_LINE, size=10.5)
    f.append(arrow(260, 190, 368, 115, color=QUEUE_LINE, sw=1.8))
    f.append(arrow(590, 112, 638, 112, color=QUEUE_LINE, sw=1.5))

    # Дія 2: Створення нових акторів
    boxlabel(f, 370, 178, 220, 64, ["2. Створити акторів", "скінченне число нових", "акторів (Spawn child)"],
             fill=STATE_FILL, stroke=STATE_LINE, size=11, tcol=STATE_LINE)
    boxlabel(f, 640, 178, 200, 64, ["new_pid = spawn(Actor)", "ієрархія потомків"],
             fill="#ffffff", stroke=STATE_LINE, size=10.5)
    f.append(arrow(260, 210, 368, 210, color=STATE_LINE, sw=1.8))
    f.append(arrow(590, 210, 638, 210, color=STATE_LINE, sw=1.5))

    # Дія 3: Зміна поведінки
    boxlabel(f, 370, 276, 220, 64, ["3. Змінити поведінку", "визначити нову логіку/стан", "для наступного msg"],
             fill=FAIL_FILL, stroke=FAIL_LINE, size=11, tcol=FAIL_LINE)
    boxlabel(f, 640, 276, 200, 64, ["become(next_behavior)", "state' = f(state, M)"],
             fill="#ffffff", stroke=FAIL_LINE, size=10.5)
    f.append(arrow(260, 230, 368, 305, color=FAIL_LINE, sw=1.8))
    f.append(arrow(590, 308, 638, 308, color=FAIL_LINE, sw=1.5))

    note(f, W / 2, 358, 800,
         ["Ніяких додаткових побічних дій на спільну пам'ять: стан оновлюється лише переходом у нову поведінку.",
          "Усі породжені повідомлення й нові актори стають активними після завершення поточного кроку."])
    render(os.path.join(IMG, "hewitt-axioms.svg"), W, H, *f)


# ── 3. Планування M:N ───────────────────────────────────────────────────────
def fig_actor_scheduling():
    W, H = 880, 420
    f = [text(W / 2, 28, "Планування M:N: мільйони легковагих акторів на пулі системних потоків", size=16, bold=True)]
    f.append(text(W / 2, 48, "Рантайм диспетчеризує акторів із непорожніми скриньками на фіксовану кількість ядер CPU",
                  size=11, color=MUTED, italic=True))

    # Черга готових акторів (Ready Queue)
    f.append(rect(40, 80, 800, 75, fill=QUEUE_FILL, stroke=QUEUE_LINE, sw=1.6, rx=8))
    f.append(text(160, 105, "Черга готових акторів (Ready Queue):", size=11.5, color=QUEUE_LINE, bold=True))
    f.append(text(160, 125, "актори, які мають повідомлення у скриньках", size=9.5, color=MUTED))

    # Значки готових акторів
    boxlabel(f, 320, 95, 90, 44, ["Актор #101", "(3 msg)"], fill="#ffffff", stroke=QUEUE_LINE, size=9.5)
    boxlabel(f, 430, 95, 90, 44, ["Актор #404", "(1 msg)"], fill="#ffffff", stroke=QUEUE_LINE, size=9.5)
    boxlabel(f, 540, 95, 90, 44, ["Актор #12", "(14 msg)"], fill="#ffffff", stroke=QUEUE_LINE, size=9.5)
    boxlabel(f, 650, 95, 90, 44, ["Актор #88", "(2 msg)"], fill="#ffffff", stroke=QUEUE_LINE, size=9.5)
    f.append(text(770, 122, "... +100k", size=11, color=MUTED, bold=True))

    # Стрілки диспетчеризації вниз
    f.append(arrow(365, 155, 230, 205, color=ACTOR_LINE, sw=1.6))
    f.append(arrow(475, 155, 440, 205, color=ACTOR_LINE, sw=1.6))
    f.append(arrow(585, 155, 650, 205, color=ACTOR_LINE, sw=1.6))

    # Системні воркери (M потоків ОС)
    workers = [
        ("Воркер 1 (Ядро 0 CPU)", 120, "Обробляє Актор #101\n(квант: 2000 reductions)"),
        ("Воркер 2 (Ядро 1 CPU)", 330, "Обробляє Актор #404\n(завершив msg -> Ready)"),
        ("Воркер 3 (Ядро 2 CPU)", 540, "Обробляє Актор #12\n(квант вичерпано -> назад)"),
    ]
    for title_w, xw, status_w in workers:
        f.append(rect(xw, 205, 210, 90, fill=ACTOR_FILL, stroke=ACTOR_LINE, sw=1.6, rx=6))
        f.append(text(xw + 105, 226, title_w, size=11, color=ACTOR_LINE, bold=True))
        boxlabel(f, xw + 10, 240, 190, 44, status_w, fill="#ffffff", stroke=ACTOR_LINE, size=9.5)

    # Зворотні стрілки після кванта
    f.append(arrow(645, 295, 710, 335, color=MUTED, sw=1.4))
    f.append(line(710, 335, 780, 335, color=MUTED, sw=1.4))
    f.append(arrow(780, 335, 780, 160, color=MUTED, sw=1.4))
    f.append(text(745, 325, "Кооперативна поступка", size=9, color=MUTED))

    note(f, W / 2, 355, 800,
         ["Актор не блокує потік ОС: після обробки невеликої порції повідомлень (або витрати кванта редукцій)",
          "він поступається потоком, повертаючись у чергу готових. Пасивні актори пам'ять не навантажують."])
    render(os.path.join(IMG, "actor-scheduling.svg"), W, H, *f)


# ── 4. Ізоляція збоїв та нагляд ──────────────────────────────────────────────
def fig_failure_isolation():
    W, H = 880, 420
    f = [text(W / 2, 28, "Ізоляція збоїв: принцип «Нехай падає» (Let It Crash) і дерево нагляду", size=16, bold=True)]
    f.append(text(W / 2, 48, "Аварія в одному акторі не корумпує стан сусідів і перехоплюється наглядачем",
                  size=11, color=MUTED, italic=True))

    # Наглядач угорі
    boxlabel(f, 320, 80, 240, 52, ["Наглядач (Supervisor)", "Стратегія: one_for_one"],
             fill=ACTOR_FILL, stroke=ACTOR_LINE, size=12, tcol=ACTOR_LINE)

    # Три підлеглі актори внизу
    # Актор 1: Працює стабільно
    boxlabel(f, 60, 210, 210, 80, ["Воркер A (PID: 101)", "Стан: OK", "Обробка черги..."],
             fill=QUEUE_FILL, stroke=QUEUE_LINE, size=11, tcol=QUEUE_LINE)

    # Актор 2: Зазнав збою
    boxlabel(f, 335, 210, 210, 80, ["Воркер B (PID: 102)", "CRASH: Divide by zero", "Стек очищено!"],
             fill=FAIL_FILL, stroke=FAIL_LINE, size=11, tcol=FAIL_LINE)

    # Актор 3: Працює стабільно
    boxlabel(f, 610, 210, 210, 80, ["Воркер C (PID: 103)", "Стан: OK", "Обробка черги..."],
             fill=QUEUE_FILL, stroke=QUEUE_LINE, size=11, tcol=QUEUE_LINE)

    # Зв'язки нагляду
    f.append(arrow(370, 132, 165, 208, color=ACTOR_LINE, sw=1.4))
    f.append(arrow(440, 132, 440, 208, color=ACTOR_LINE, sw=1.4))
    f.append(arrow(510, 132, 715, 208, color=ACTOR_LINE, sw=1.4))

    # Сигнал аварії та перезапуск
    f.append(arrow(455, 208, 485, 134, color=FAIL_LINE, sw=1.8))
    f.append(text(545, 170, "1. Сигнал {'EXIT', Pid, Reason}", size=9.5, color=FAIL_LINE, bold=True))

    # Стрілка перезапуску
    f.append(arrow(415, 134, 385, 208, color=FIELD, sw=1.8))
    f.append(text(310, 170, "2. Restart: spawn(B_new)", size=9.5, color=FIELD, bold=True))

    note(f, W / 2, 355, 800,
         ["Кожен актор володіє власним ізольованим стеком і купою: аварія у Воркері B не зачіпає Воркерів A та C.",
          "Наглядач отримує сигнал про падіння й перезапускає актор у чистому початковому стані."])
    render(os.path.join(IMG, "failure-isolation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_actor_anatomy()
    fig_hewitt_axioms()
    fig_actor_scheduling()
    fig_failure_isolation()
    print("Всі фігури згенеровано успішно.")
