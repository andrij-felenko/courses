# -*- coding: utf-8 -*-
"""Фігури до теми «Оптимістичне оновлення інтерфейсу й відкат невдалої зміни» (client-architecture)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def panel(x, y, w, h, head, sub=None):
    """Панель із заголовком угорі; повертає (svg, внутрішній верх)."""
    s = rect(x, y, w, h, fill="#ffffff", stroke="#b8c2cc", sw=1.6, rx=10)
    s += text(x + w / 2, y + 26, head, size=15, bold=True)
    if sub:
        s += text(x + w / 2, y + 44, sub, size=12, color=MUTED)
        return s, y + 56
    return s, y + 42


# ── 1. Порівняння: песимістичне проти оптимістичного оновлення ────────────────
def fig_pessimistic_vs_optimistic():
    W, H = 1060, 500
    P, PW, PH, PY = [40, 550], 470, 410, 60
    s = ""

    # Ліва панель: Песимістичне оновлення
    px = P[0]
    p, top = panel(px, PY, PW, PH, "Песимістичне оновлення", "блокування та очікування мережі")
    s += p
    cx = px + PW / 2

    b1, _, _ = textbox(cx, top + 35, "1. Клік користувача (намір)", size=13, min_w=360, fill="#eef3f8")
    s += b1
    s += arrow(cx, top + 55, cx, top + 90, color=LINE)

    b2, _, _ = textbox(cx, top + 115, "2. Блокування UI + спінер завантаження\n(інтерфейс заморожено на 150–500 мс)", size=12, min_w=360, fill="#fdecea", stroke=POS)
    s += b2
    s += arrow(cx, top + 145, cx, top + 180, color=LINE)

    b3, _, _ = textbox(cx, top + 205, "3. Відповідь сервера (HTTP 200 OK)\nдані зафіксовано в базі", size=12, min_w=360, fill="#eaf0fd", stroke=NEG)
    s += b3
    s += arrow(cx, top + 235, cx, top + 270, color=LINE)

    b4, _, _ = textbox(cx, top + 295, "4. Оновлення стану й розблокування UI\n(відчутна затримка реакції)", size=12, min_w=360, fill="#f4f6f8")
    s += b4

    # Права панель: Оптимістичне оновлення
    px = P[1]
    p, top = panel(px, PY, PW, PH, "Оптимістичне оновлення", "миттєва мутація з фоновим підтвердженням")
    s += p
    cx = px + PW / 2

    b1, _, _ = textbox(cx, top + 35, "1. Клік користувача (намір)", size=13, min_w=360, fill="#eef3f8")
    s += b1
    s += arrow(cx, top + 55, cx, top + 90, color=FIELD)

    b2, _, _ = textbox(cx, top + 115, "2. Миттєве оновлення UI (<16 мс)\nкористувач одразу бачить результат дії", size=12, min_w=360, fill="#eafaf1", stroke=FIELD)
    s += b2
    s += arrow(cx, top + 145, cx, top + 180, color=LINE)

    b3, _, _ = textbox(cx, top + 205, "3. Фонові перегони мережі (In-Flight)\nHTTP-запит виконується асинхронно", size=12, min_w=360, fill="#f4f6f8")
    s += b3

    # Розгалуження на успіх / відкат
    s += arrow(cx - 90, top + 235, cx - 90, top + 270, color=FIELD)
    s += arrow(cx + 90, top + 235, cx + 90, top + 270, color=POS)

    b4a, _, _ = textbox(cx - 95, top + 300, "Успіх: тихе узгодження\n(закріплення ID)", size=11, min_w=180, fill="#eafaf1", stroke=FIELD)
    b4b, _, _ = textbox(cx + 95, top + 300, "Збій: відкат стану\n(повідомлення)", size=11, min_w=180, fill="#fdecea", stroke=POS)
    s += b4a + b4b

    render(os.path.join(OUT, "pessimistic-vs-optimistic.svg"), W, H, s,
           title="Песимістичний та оптимістичний цикли оновлення інтерфейсу")


# ── 2. Тришарова архітектура клієнтського стану ──────────────────────────────
def fig_three_layer_state():
    W, H = 1060, 520
    s = ""

    # Блок 1: Канонічний серверний стан
    b1 = rect(50, 70, 960, 100, fill="#f4f8fb", stroke="#2457d6", sw=1.8, rx=8)
    b1 += text(530, 98, "Канонічний серверний стан (Canonical Server State — S_server)", size=15, bold=True, color=NEG)
    b1 += text(530, 126, "Підтверджений бекендом стан сутностей: перевірені ID, збережені версії, дійсні права доступу", size=13, color=MUTED)
    b1 += text(530, 150, "Оновлюється ТІЛЬКИ відповідями сервера (GET / WS / ACK мутацій)", size=12, bold=True)
    s += b1

    s += arrow(530, 175, 530, 215, color=LINE)
    s += text(545, 198, "+", size=18, bold=True, anchor="start")

    # Блок 2: Черга оптимістичних мутацій (патчів)
    b2 = rect(50, 220, 960, 115, fill="#fdfbf7", stroke="#d97706", sw=1.8, rx=8)
    b2 += text(530, 248, "Черга локальних оптимістичних мутацій (Pending Mutation Queue — [Δ₁, Δ₂, ...])", size=15, bold=True, color="#b45309")
    
    # Картки мутацій усередині
    c1, _, _ = textbox(210, 292, "Δ₁: Like (temp-id: 101)", size=12, min_w=200, fill="#ffffff", stroke="#d97706")
    c2, _, _ = textbox(480, 292, "Δ₂: Edit text (id: 42)", size=12, min_w=200, fill="#ffffff", stroke="#d97706")
    c3, _, _ = textbox(750, 292, "Δ₃: Move card (id: 88)", size=12, min_w=200, fill="#ffffff", stroke="#d97706")
    b2 += c1 + c2 + c3
    s += b2

    s += arrow(530, 340, 530, 380, color=FIELD)
    s += text(545, 363, "reduce()", size=12, bold=True, anchor="start", color=FIELD)

    # Блок 3: Похідний стан подання (View State)
    b3 = rect(50, 385, 960, 95, fill="#eafaf1", stroke="#27ae60", sw=1.8, rx=8)
    b3 += text(530, 415, "Похідний стан подання (Derived View State — S_view)", size=15, bold=True, color=FIELD)
    b3 += text(530, 442, "S_view = reduce(S_server, [Δ₁, Δ₂, ...]) — стан, який бачить рендерер UI просто зараз", size=13, bold=True)
    b3 += text(530, 464, "Відкат збійної дії Δ₂ — це видалення її з черги та миттєвий перерахунок S_view без втрати Δ₁ і Δ₃", size=12, color=MUTED)
    s += b3

    render(os.path.join(OUT, "three-layer-state.svg"), W, H, s,
           title="Тришарова модель: канонічний стан, черга намірів та стан подання")


# ── 3. Життєвий цикл тимчасових ідентифікаторів (Temp-ID) ───────────────────
def fig_temp_id_lifecycle():
    W, H = 1060, 510
    s = ""

    # Крок 1: Клієнт генерує temp-id
    b1, _, _ = textbox(190, 110, "1. Створення сутності\nКлієнт генерує temp-id:\n`temp_task_9a2f`", size=12, min_w=250, fill="#f4f8fb", stroke=NEG)
    s += b1

    s += arrow(325, 110, 415, 110, color=LINE)

    # Крок 2: Відображення в UI та зв'язування дій
    b2, _, _ = textbox(550, 110, "2. UI рендерить елемент\nДозволено дочірні дії:\n`parent_id: temp_task_9a2f`", size=12, min_w=240, fill="#eafaf1", stroke=FIELD)
    s += b2

    s += arrow(680, 110, 770, 110, color=LINE)

    # Крок 3: Відправка на сервер
    b3, _, _ = textbox(900, 110, "3. POST /api/tasks\nЗапит несе намір і\nклієнтський temp-id", size=12, min_w=210, fill="#fdfbf7", stroke="#d97706")
    s += b3

    s += arrow(900, 155, 900, 240, color=LINE)

    # Крок 4: Відповідь сервера
    b4, _, _ = textbox(900, 280, "4. Сервер призначає ID\nHTTP 201 Created\n`{ tempId: '...', serverId: 7812 }`", size=12, min_w=230, fill="#eef3f8", stroke=NEG)
    s += b4

    s += arrow(775, 280, 685, 280, color=FIELD)

    # Крок 5: Таблиця підміни (Identity Map Reconciliation)
    b5, _, _ = textbox(450, 280, "5. Таблиця трансляції ID (Temp-to-Server Mapping)\n`temp_task_9a2f`  ↦  `7812`\nПідміна ключів у кеші, черзі залежних мутацій та URL", size=12, min_w=380, fill="#ffffff", stroke=FIELD, sw=2)
    s += b5

    s += arrow(250, 280, 190, 280, color=FIELD)

    # Крок 6: Канонічний стан
    b6, _, _ = textbox(190, 390, "6. Повне узгодження\nСутність зафіксована;\nтимчасовий ключ видалено", size=12, min_w=250, fill="#eafaf1", stroke=FIELD)
    s += arrow(190, 315, 190, 350, color=FIELD)
    s += b6

    # Примітка внизу
    note = rect(350, 370, 640, 75, fill="#f4f6f8", stroke="#b8c2cc", sw=1.2, rx=6)
    note += text(670, 398, "Захист від розриву зв'язків: якщо дочірня мутація відправилась до отримання serverId,", size=12, color=INK)
    note += text(670, 422, "клієнтський диспетчер оновлює payload наступного запиту перед його виходом у мережу.", size=12, color=MUTED)
    s += note

    render(os.path.join(OUT, "temp-id-lifecycle.svg"), W, H, s,
           title="Життєвий цикл тимчасового ідентифікатора (Temp-ID) та трансляція ключів")


# ── 4. Гонки відповідей та неупорядковані запити ─────────────────────────────
def fig_out_of_order_race():
    W, H = 1060, 520
    s = ""

    # Ліва сторона: Наївне перезаписування (Аномалія)
    p1, top1 = panel(40, 60, 475, 420, "Наївне перезаписування (Аномалія)", "застаріла відповідь ламає актуальний стан")
    s += p1
    c1 = 40 + 475 / 2

    # Часова шкала наївна
    s += line(c1 - 180, top1 + 30, c1 + 180, top1 + 30, color=LINE, sw=1.2)
    s += text(c1 - 170, top1 + 22, "t = 0 мс", size=11, color=MUTED)
    s += text(c1, top1 + 22, "t = 100 мс", size=11, color=MUTED)
    s += text(c1 + 170, top1 + 22, "t = 500 мс", size=11, color=MUTED)

    b_a1, _, _ = textbox(c1, top1 + 75, "Дія 1 (t=0): Вмикач ON (повільна мережа, RTT=500 мс)\nUI оптимістично: ON", size=11, min_w=430, fill="#eafaf1")
    b_a2, _, _ = textbox(c1, top1 + 155, "Дія 2 (t=100): Вмикач OFF (швидка мережа, RTT=80 мс)\nUI оптимістично: OFF", size=11, min_w=430, fill="#eef3f8")
    b_a3, _, _ = textbox(c1, top1 + 235, "t = 180 мс: Прийшов ACK на Дію 2 -> сервер повернув OFF\nUI стан: OFF (правильно)", size=11, min_w=430, fill="#eef3f8")
    b_a4, _, _ = textbox(c1, top1 + 320, "t = 500 мс: Прийшов ACK на Дію 1 -> сервер повернув ON!\nUI помилково стає ON (застарілий запис затер свіжий!)", size=11, min_w=430, fill="#fdecea", stroke=POS, sw=2)
    s += b_a1 + b_a2 + b_a3 + b_a4

    # Права сторона: Захист версіями / скасуванням
    p2, top2 = panel(545, 60, 475, 420, "Захист версіями та чергою", "монотонні ревізії або скасування запитів")
    s += p2
    c2 = 545 + 475 / 2

    # Часова шкала правильна
    s += line(c2 - 180, top2 + 30, c2 + 180, top2 + 30, color=LINE, sw=1.2)
    s += text(c2 - 170, top2 + 22, "t = 0 мс", size=11, color=MUTED)
    s += text(c2, top2 + 22, "t = 100 мс", size=11, color=MUTED)
    s += text(c2 + 170, top2 + 22, "t = 500 мс", size=11, color=MUTED)

    b_b1, _, _ = textbox(c2, top2 + 75, "Дія 1 (t=0): Запит seq=1 (AbortController #1)\nUI оптимістично: ON (версія v1)", size=11, min_w=430, fill="#eafaf1")
    b_b2, _, _ = textbox(c2, top2 + 155, "Дія 2 (t=100): Запит seq=2 -> abort(#1) скасовує Запит 1\nUI оптимістично: OFF (версія v2)", size=11, min_w=430, fill="#eef3f8")
    b_b3, _, _ = textbox(c2, top2 + 235, "t = 180 мс: Прийшов ACK seq=2 -> застосовано версію v2\nUI стан: OFF (підтверджено)", size=11, min_w=430, fill="#eafaf1", stroke=FIELD)
    b_b4, _, _ = textbox(c2, top2 + 320, "t = 500 мс: Запит 1 або скасовано в сокеті, або проігноровано\nбо seq=1 < seq_latest(2). Стан лишається OFF!", size=11, min_w=430, fill="#eafaf1", stroke=FIELD, sw=2)
    s += b_b1 + b_b2 + b_b3 + b_b4

    render(os.path.join(OUT, "out-of-order-race.svg"), W, H, s,
           title="Гонка відповідей мережі: застаріле перезаписування проти версіонування")


# ── 5. Стейт-машина оптимістичної мутації ────────────────────────────────────
def fig_mutation_state_machine():
    W, H = 1060, 520
    s = ""

    # Стан 1: IDLE
    b_idle, _, _ = textbox(130, 250, "IDLE\n(стан спокою)", size=13, min_w=150, fill="#ffffff", stroke="#b8c2cc")
    s += b_idle

    s += arrow(210, 250, 290, 250, color=LINE)
    s += text(250, 235, "Клік / Дія", size=11, bold=True)

    # Стан 2: OPTIMISTIC_APPLIED
    b_opt, _, _ = textbox(410, 250, "OPTIMISTIC_APPLIED\n1. Патч у черзі\n2. Знімок / ребаз збережено\n3. UI миттєво оновлено", size=11, min_w=210, fill="#eafaf1", stroke=FIELD, sw=1.8)
    s += b_opt

    s += arrow(520, 250, 590, 250, color=LINE)
    s += text(555, 235, "Fetch()", size=11, bold=True)

    # Стан 3: IN_FLIGHT
    b_flight, _, _ = textbox(690, 250, "IN_FLIGHT\nЗапит у мережі\n(idempotency-key,\nabort-signal)", size=11, min_w=170, fill="#fdfbf7", stroke="#d97706")
    s += b_flight

    # Гілка вгору: Успіх (SETTLED_SUCCESS)
    s += arrow(780, 220, 870, 130, color=FIELD)
    s += text(835, 160, "HTTP 2xx", size=11, bold=True, color=FIELD)

    b_succ, _, _ = textbox(930, 110, "SETTLED_SUCCESS\n1. S_server оновлено\n2. Патч знято з черги\n3. Temp-ID узгоджено", size=11, min_w=190, fill="#eafaf1", stroke=FIELD, sw=2)
    s += b_succ

    # Гілка прямо: Тимчасова помилка мережі (RETRYING_OFFLINE)
    s += arrow(780, 250, 840, 250, color="#b45309")
    s += text(810, 235, "Offline / 5xx", size=10, bold=True, color="#b45309")

    b_retry, _, _ = textbox(930, 250, "RETRYING_OFFLINE\n1. UI лишається зміненим\n2. Бейдж «збереження...»\n3. Exponential backoff", size=11, min_w=190, fill="#fdfbf7", stroke="#d97706", sw=1.8)
    s += b_retry

    # Гілка вниз: Фатальна помилка (ROLLBACK_ERROR)
    s += arrow(780, 280, 870, 390, color=POS)
    s += text(835, 350, "HTTP 4xx", size=11, bold=True, color=POS)

    b_roll, _, _ = textbox(930, 410, "ROLLBACK_ERROR\n1. Видалення патча з черги\n2. Rebase S_view = reduce()\n3. Пояснювальний тост у UI", size=11, min_w=190, fill="#fdecea", stroke=POS, sw=2)
    s += b_roll

    # Стрілки повернення в IDLE
    s += arrow(930, 60, 130, 60, color=FIELD)
    s += line(930, 80, 930, 60, color=FIELD)
    s += line(130, 60, 130, 215, color=FIELD)
    s += text(530, 48, "Очищення черги та повернення в стан спокою", size=11, color=MUTED)

    render(os.path.join(OUT, "mutation-state-machine.svg"), W, H, s,
           title="Скінченний автомат життєвого циклу оптимістичної мутації")


if __name__ == "__main__":
    fig_pessimistic_vs_optimistic()
    fig_three_layer_state()
    fig_temp_id_lifecycle()
    fig_out_of_order_race()
    fig_mutation_state_machine()
    print("Всі фігури згенеровано успішно.")
