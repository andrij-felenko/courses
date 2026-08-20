# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=9, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Активно-активний багаторегіональний запис та виникнення конфлікту ─
def fig_datacenter_writes():
    W, H = 940, 520
    frags = []

    # Заголовок
    frags.append(text(470, 30, "Мультилідерна реплікація: локальні записи та асинхронні перегони через WAN", size=15, bold=True))

    # Датацентр 1 (Регіон Франкфурт)
    frags.append(rect(30, 60, 390, 420, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(225, 90, "РЕГІОН 1: Європа (Франкфурт)", size=13, bold=True, color=NEG))

    # Клієнт 1
    frags.append(box(225, 140, "Клієнт A (Берлін)\nЗапит: UPDATE order #101 SET status='paid'", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=280))
    frags.append(arrow(225, 168, 225, 205, color=NEG, sw=1.5))
    frags.append(text(275, 190, "RTT ~ 2 мс", size=10, color=FIELD, bold=True))

    # Лідер 1
    frags.append(rect(60, 210, 330, 160, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(225, 235, "Лідер 1 (PostgreSQL / Node A)", size=12, bold=True, color=NEG))
    frags.append(box(225, 275, "1. Локальна фіксація (Commit)\n2. Запис у WAL-журнал [v1: paid]\n3. Відповідь клієнту: HTTP 200 OK", size=11, fill="#eaf0fd", stroke=NEG, min_w=290))
    frags.append(text(225, 355, "Запис зафіксовано локально за 3 мс", size=10, color=FIELD, italic=True))

    # Статус у DC1
    frags.append(box(225, 430, "Локальний стан вузла A:\norder #101 = 'paid' (v1.0)", size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=260))

    # Датацентр 2 (Регіон Токіо)
    frags.append(rect(520, 60, 390, 420, fill="#f8fafc", stroke=POS, sw=1.5, rx=8))
    frags.append(text(715, 90, "РЕГІОН 2: Азія (Токіо)", size=13, bold=True, color=POS))

    # Клієнт 2
    frags.append(box(715, 140, "Клієнт B (Кіото)\nЗапит: UPDATE order #101 SET status='cancelled'", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=280))
    frags.append(arrow(715, 168, 715, 205, color=POS, sw=1.5))
    frags.append(text(765, 190, "RTT ~ 2 мс", size=10, color=FIELD, bold=True))

    # Лідер 2
    frags.append(rect(550, 210, 330, 160, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    frags.append(text(715, 235, "Лідер 2 (PostgreSQL / Node B)", size=12, bold=True, color=POS))
    frags.append(box(715, 275, "1. Локальна фіксація (Commit)\n2. Запис у WAL-журнал [v1: cancelled]\n3. Відповідь клієнту: HTTP 200 OK", size=11, fill="#fdf0ed", stroke=POS, min_w=290))
    frags.append(text(715, 355, "Запис зафіксовано локально за 3 мс", size=10, color=FIELD, italic=True))

    # Статус у DC2
    frags.append(box(715, 430, "Локальний стан вузла B:\norder #101 = 'cancelled' (v0.1)", size=11, bold=True, fill="#fdf0ed", stroke=POS, min_w=260))

    # Транзит через WAN (Міжрегіональний канал)
    frags.append(arrow(390, 260, 550, 260, color=NEG, sw=2))
    frags.append(text(470, 248, "WAL потік A → B", size=10, bold=True, color=NEG))

    frags.append(arrow(550, 310, 390, 310, color=POS, sw=2))
    frags.append(text(470, 325, "WAL потік B → A", size=10, bold=True, color=POS))

    # Блок пояснення конфлікту в центрі
    frags.append(box(470, 430, "Зіткнення у WAN\n(RTT ~ 230 мс)\nПаралельні записи!", size=10, bold=True, fill="#fff9db", stroke="#e67e22", min_w=140))

    render(os.path.join(IMG, 'multi-leader-datacenter-writes.svg'), W, H, *frags)


# ── Фігура 2: Порівняння топологій мультилідерної реплікації ───────────────────
def fig_topologies():
    W, H = 960, 500
    frags = []

    # Заголовок
    frags.append(text(480, 28, "Топології передачі оновлень між лідерами та їхні критичні вразливості", size=15, bold=True))

    # Секція 1: Кільцева топологія
    frags.append(rect(20, 55, 290, 420, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(165, 80, "1. Кільцева (Ring)", size=13, bold=True, color=INK))

    frags.append(box(165, 130, "Вузол A", size=11, bold=True, fill="#ffffff", stroke=NEG, min_w=80))
    frags.append(box(90, 220, "Вузол B", size=11, bold=True, fill="#ffffff", stroke=NEG, min_w=80))
    frags.append(box(240, 220, "Вузол C", size=11, bold=True, fill="#ffffff", stroke=NEG, min_w=80))

    frags.append(arrow(135, 145, 95, 195, color=NEG, sw=1.5))
    frags.append(arrow(125, 220, 205, 220, color=NEG, sw=1.5))
    frags.append(arrow(235, 195, 195, 145, color=NEG, sw=1.5))

    frags.append(box(165, 330, "Властивості та ризики:\n• Пересилка по ланцюжку\n• Потрібна луп-детекція\n  (список вузлів у заголовку)\n• Збій одного вузла розриває\n  реплікацію в усьому кільці!", size=10, fill="#f8fafc", stroke=MUTED, min_w=260))

    # Секція 2: Зіркова топологія
    frags.append(rect(335, 55, 290, 420, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(480, 80, "2. Зіркова (Star)", size=13, bold=True, color=INK))

    frags.append(box(480, 180, "Центральний\nВузол (Hub)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=100))
    frags.append(box(390, 120, "Вузол A", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=70))
    frags.append(box(570, 120, "Вузол B", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=70))
    frags.append(box(480, 250, "Вузол C", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=70))

    frags.append(arrow(415, 135, 450, 160, color=LINE, sw=1.5))
    frags.append(arrow(545, 135, 510, 160, color=LINE, sw=1.5))
    frags.append(arrow(480, 205, 480, 230, color=LINE, sw=1.5))

    frags.append(box(480, 330, "Властивості та ризики:\n• Центр маршрутизує всі логи\n• Просте керування конфліктами\n• Центральний хаб — вузьке місце\n• Збій хабу паралізує обмін між\n  усіма іншими лідерами", size=10, fill="#f8fafc", stroke=MUTED, min_w=260))

    # Секція 3: Повнозв'язна топологія (All-to-All / Mesh)
    frags.append(rect(650, 55, 290, 420, fill="#fcfdfe", stroke=FIELD, sw=1.2, rx=8))
    frags.append(text(795, 80, "3. Повнозв'язна (Mesh)", size=13, bold=True, color=FIELD))

    frags.append(box(795, 130, "Вузол A", size=11, bold=True, fill="#ffffff", stroke=FIELD, min_w=80))
    frags.append(box(720, 220, "Вузол B", size=11, bold=True, fill="#ffffff", stroke=FIELD, min_w=80))
    frags.append(box(870, 220, "Вузол C", size=11, bold=True, fill="#ffffff", stroke=FIELD, min_w=80))

    frags.append(arrow(770, 145, 735, 195, color=FIELD, sw=1.5))
    frags.append(arrow(820, 145, 855, 195, color=FIELD, sw=1.5))
    frags.append(arrow(755, 220, 835, 220, color=FIELD, sw=1.5))

    frags.append(box(795, 330, "Властивості та ризики:\n• Максимальна відмовостійкість\n• Немає єдиної точки відмови\n• Мережеві перегони: порушення\n  причинності (UPDATE випереджає\n  INSERT на віддаленому вузлі)", size=10, fill="#eafaf0", stroke=FIELD, min_w=260))

    render(os.path.join(IMG, 'replication-topologies-and-loops.svg'), W, H, *frags)


# ── Фігура 3: Детекція паралельних правок та стратегії збіжності ───────────────
def fig_conflict_resolution():
    W, H = 960, 540
    frags = []

    # Заголовок
    frags.append(text(480, 28, "Детекція паралельних правок через версійні вектори та шляхи збіжності", size=15, bold=True))

    # Верхній блок: перегони версій
    frags.append(rect(30, 55, 900, 175, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(480, 78, "Детекція конкурентності: векторні мітки V = [v_A, v_B]", size=12, bold=True, color=INK))

    frags.append(box(180, 130, "Стан A: [1, 0]\nЗапис: 'Alice'\n(Вузол A не бачив дій B)", size=11, bold=True, fill="#ffffff", stroke=NEG, min_w=220))
    frags.append(box(780, 130, "Стан B: [0, 1]\nЗапис: 'Bob'\n(Вузол B не бачив дій A)", size=11, bold=True, fill="#ffffff", stroke=POS, min_w=220))

    frags.append(arrow(295, 130, 380, 130, color=NEG, sw=1.5))
    frags.append(arrow(665, 130, 580, 130, color=POS, sw=1.5))

    frags.append(box(480, 130, "Порівняння векторів:\n[1, 0] vs [0, 1]\nЖоден не домінує!\n→ КОНКУРЕНТНІ (Concurrent)", size=10, bold=True, fill="#fff9db", stroke="#e67e22", min_w=180))
    frags.append(text(480, 205, "Потрібне детерміноване правило злиття (збіжність до однакового стану на обох вузлах)", size=10, italic=True, color=MUTED))

    # Нижній блок: 3 стратегії розв'язання
    frags.append(text(480, 255, "СТРАТЕГІЇ ЗБІЖНОСТІ (CONVERGENCE)", size=13, bold=True, color=INK))

    # Стратегія 1: LWW
    frags.append(rect(30, 275, 280, 240, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(170, 300, "1. Last Write Wins (LWW)", size=12, bold=True, color=POS))
    frags.append(box(170, 385, "• Порівняння міток часу (NTP)\n• Запис із більшим t перемагає\n• Альтернативний запис тихо\n  викидається без сліду!\n• Ризик: похибка годинника\n  знищує новіші бізнес-дані", size=10, fill="#fdf0ed", stroke=POS, min_w=250))
    frags.append(box(170, 485, "Результат: 'Bob' (v[1,1])\nПравку 'Alice' втрачено!", size=10, bold=True, fill="#ffffff", stroke=POS, min_w=240))

    # Стратегія 2: Siblings (Multi-Value)
    frags.append(rect(340, 275, 280, 240, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    frags.append(text(480, 300, "2. Збереження версій (Siblings)", size=12, bold=True, color=NEG))
    frags.append(box(480, 385, "• Зберігаються обидва значення\n• Дерево ревізій (_rev у CouchDB)\n• При читанні клієнт отримує\n  список конфліктних копій\n• Обов'язок злиття покладено\n  на застосунок або людину", size=10, fill="#eaf0fd", stroke=NEG, min_w=250))
    frags.append(box(480, 485, "Результат: {'Alice', 'Bob'}\nЧесно, але складніше API", size=10, bold=True, fill="#ffffff", stroke=NEG, min_w=240))

    # Стратегія 3: CRDT / Field Merge
    frags.append(rect(650, 275, 280, 240, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(790, 300, "3. Безконфліктні типи (CRDT)", size=12, bold=True, color=FIELD))
    frags.append(box(790, 385, "• Алгебраїчна напівґратка\n• Операції комутують або\n  злиття полів є детермінованим\n• Лічильники PN-Counter, множини\n  OR-Set, злиття JSON по ключах\n• Немає втрати правок", size=10, fill="#eafaf0", stroke=FIELD, min_w=250))
    frags.append(box(790, 485, "Результат: об'єднання правок\nБез втрат і блокувань", size=10, bold=True, fill="#ffffff", stroke=FIELD, min_w=240))

    render(os.path.join(IMG, 'conflict-detection-vector-clocks.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_datacenter_writes()
    fig_topologies()
    fig_conflict_resolution()
    print("All figures generated successfully.")
