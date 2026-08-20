# -*- coding: utf-8 -*-
"""Фігури до теми «Спектр консистентності»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"    # слабкі гарантії / аномалії / висока доступність
COOL = "#eaf0fd"    # заголовки / нейтральні блоки
GOOD = "#e8f6ee"    # сильні гарантії / лінеаризовність
WARN_BG = "#fff9db" # причинна / сесійна узгодженість
ACCENT = "#9b51e0"  # спеціальні позначки


# ── 1. Спектр та ієрархія моделей консистентності ───────────────────────────
def consistency_spectrum_hierarchy():
    W, H = 1080, 690
    f = []

    f.append(text(W / 2, 32, "Спектр моделей консистентності: від суворих гарантій до високої доступності",
                  size=16, bold=True))

    # Ліва вісь: Сила гарантій і ціна координації
    f.append(arrow(60, 600, 60, 70, color=POS, sw=2.5))
    f.append(text(60, 58, "Сила гарантій / Ціна координації (RTT)", size=12, color=POS, bold=True))

    # Права вісь: Доступність і стійкість до затримок
    f.append(arrow(W - 60, 70, W - 60, 600, color=FIELD, sw=2.5))
    f.append(text(W - 60, 618, "Доступність (HA) / Швидкість відгуку", size=12, color=FIELD, bold=True))

    # Рівні спектру (ієрархічні блоки зверху вниз)
    boxes = [
        ("Сувора серіалізовність (Strict Serializability / External Consistency)",
         "Транзакційна ізоляція Serializable + Лінеаризовність операцій у фізичному часі.\nПриклади: Google Spanner (TrueTime), CockroachDB.",
         GOOD, POS, 80),
        ("Лінеаризовність (Linearizability / Strong Consistency)",
         "Одиночні операції над одним об'єктом. Кожна операція фіксується в точці лінеаризації в реальному часі.\nКомпозиційна властивість. Приклади: Raft (etcd), Paxos, ZAB (ZooKeeper sync-writes).",
         GOOD, POS, 170),
        ("Послідовна консистентність (Sequential Consistency, Lamport 1979)",
         "Існує єдиний глобальний порядок для всіх вузлів, що зберігає локальний порядок процесів.\nНе вимагає реального часу. Не має властивості композиційності.",
         COOL, LINE, 260),
        ("Причинна консистентність (Causal Consistency / Causal+)",
         "Зберігає зв'язки «спричинено раніше» (happens-before, a → b). Конкурентні оновлення дозволені.\nНайсильніша модель, досяжна при повній доступності (AP). Приклади: COPS, Bolt-on.",
         WARN_BG, LINE, 350),
        ("Сесійні гарантії (Session Consistency: RYW, Monotonic Reads/Writes)",
         "Гарантії для окремого клієнта в межах його сесії. Різні клієнти можуть бачити розбіжності.\nПриклади: Azure Cosmos DB (Session), MongoDB (causal sessions).",
         WARN_BG, LINE, 440),
        ("Кінцева узгодженість (Eventual Consistency / SEC через CRDT)",
         "За відсутності нових записів усі репліки збігаються до однакового стану.\nМінімальна латентність читання/запису. Приклади: DynamoDB, Cassandra (ONE), Amazon S3.",
         WARM, FIELD, 530)
    ]

    bx, bw, bh = 110, W - 220, 72
    for title, desc, bg, border, y in boxes:
        f.append(rect(bx, y, bw, bh, fill=bg, stroke=border, sw=1.8, rx=6))
        f.append(text(bx + 16, y + 24, title, size=13, bold=True, color=border, anchor="start"))
        lines = desc.split("\n")
        f.append(text(bx + 16, y + 44, lines[0], size=11, color=INK, anchor="start"))
        f.append(text(bx + 16, y + 60, lines[1], size=10.5, color=MUTED, anchor="start"))

    # Стрілки переходу між блоками
    for i in range(len(boxes) - 1):
        y_arrow = boxes[i][4] + bh
        f.append(arrow(W / 2, y_arrow + 2, W / 2, y_arrow + 16, color=LINE, sw=1.5))

    # Нижній підсумок
    f.append(fitbox(W / 2 - 380, 626, 760, 46,
                    "Правило вибору: кожне посилення гарантій консистентності вимагає синхронних мережевих раундів (RTT),\nзнижуючи стійкість системи до мережевих розділень (CAP-теорема).",
                    size=10.5, pad=5, fill=COOL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "consistency-spectrum-hierarchy.svg"), W, H, *f)


# ── 2. Лінеаризовність проти Послідовної консистентності ────────────────────
def linearizability_vs_sequential_timeline():
    W, H = 1100, 680
    f = []

    f.append(text(W / 2, 32, "Лінеаризовність проти Послідовної консистентності на часовій осі",
                  size=16, bold=True))

    # Ліва колонка: Лінеаризовність (вимагає реального часу)
    col1_x, col1_w = 40, 480
    f.append(rect(col1_x, 60, col1_w, 480, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(text(col1_x + col1_w / 2, 85, "ЛІНЕАРИЗОВНІСТЬ (Linearizability)", size=13.5, bold=True, color=POS))
    f.append(text(col1_x + col1_w / 2, 105, "Фізичний час: якщо W1 завершився ДО початку R1, R1 зобов'язаний бачити W1",
                  size=10, color=MUTED))

    # Процеси для лінеаризовності
    pA_y, pB_y = 170, 270
    f.append(text(col1_x + 35, pA_y + 4, "Вузол A", size=11, bold=True, anchor="start"))
    f.append(line(col1_x + 90, pA_y, col1_x + col1_w - 30, pA_y, color=LINE, sw=1.5))

    f.append(text(col1_x + 35, pB_y + 4, "Вузол B", size=11, bold=True, anchor="start"))
    f.append(line(col1_x + 90, pB_y, col1_x + col1_w - 30, pB_y, color=LINE, sw=1.5))

    # Операція Write(x, 1) на Вузлі A
    w_start, w_end = col1_x + 110, col1_x + 230
    f.append(rect(w_start, pA_y - 14, w_end - w_start, 28, fill=GOOD, stroke=POS, sw=1.5, rx=4))
    f.append(text((w_start + w_end) / 2, pA_y + 4, "Write(x, 1)", size=10.5, bold=True, color=POS))
    # Точка лінеаризації
    lp1 = w_start + (w_end - w_start) * 0.6
    f.append(circle(lp1, pA_y, 4, fill=POS, stroke=POS, sw=1.5))
    f.append(text(lp1, pA_y - 20, "LP(W)", size=9.5, color=POS, bold=True))

    # Операція Read(x) -> 1 на Вузлі B після завершення Write
    r_start, r_end = col1_x + 270, col1_x + 390
    f.append(rect(r_start, pB_y - 14, r_end - r_start, 28, fill=GOOD, stroke=POS, sw=1.5, rx=4))
    f.append(text((r_start + r_end) / 2, pB_y + 4, "Read(x) -> 1", size=10.5, bold=True, color=POS))
    lp2 = r_start + (r_end - r_start) * 0.5
    f.append(circle(lp2, pB_y, 4, fill=POS, stroke=POS, sw=1.5))
    f.append(text(lp2, pB_y + 26, "LP(R)", size=9.5, color=POS, bold=True))

    # Інтервал реального часу
    f.append(line(w_end, pA_y + 16, w_end, pB_y + 40, color=MUTED, sw=1, dash="3,3"))
    f.append(line(r_start, pA_y - 25, r_start, pB_y - 16, color=MUTED, sw=1, dash="3,3"))
    f.append(arrow(w_end + 4, pA_y + 35, r_start - 4, pA_y + 35, color=POS, sw=1.5))
    f.append(text((w_end + r_start) / 2, pA_y + 50, "Δt > 0 (реальний час)", size=9.5, color=POS))

    # Пояснення вердикту
    f.append(fitbox(col1_x + 20, 360, col1_w - 40, 160,
                    "Глобальний порядок: Write(x, 1) → Read(x) -> 1.\n"
                    "Оскільки Read почався після завершення Write у реальному часі,\n"
                    "повернення значення 0 було б грубим порушенням лінеаризовності.\n"
                    "Кожна операція здається миттєвою в точці лінеаризації (LP).",
                    size=10.5, pad=6, fill=GOOD, stroke=POS, sw=1.2))

    # Права колонка: Послідовна консистентність (без прив'язки до фізичного часу)
    col2_x, col2_w = 580, 480
    f.append(rect(col2_x, 60, col2_w, 480, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(col2_x + col2_w / 2, 85, "ПОСЛІДОВНА КОНСИСТЕНТНІСТЬ (Sequential)", size=13.5, bold=True, color=FIELD))
    f.append(text(col2_x + col2_w / 2, 105, "Допускає затримку: існує порядок, спільний для всіх, що поважає локальний потік",
                  size=10, color=MUTED))

    # Процеси для послідовної
    f.append(text(col2_x + 35, pA_y + 4, "Вузол A", size=11, bold=True, anchor="start"))
    f.append(line(col2_x + 90, pA_y, col2_x + col2_w - 30, pA_y, color=LINE, sw=1.5))

    f.append(text(col2_x + 35, pB_y + 4, "Вузол B", size=11, bold=True, anchor="start"))
    f.append(line(col2_x + 90, pB_y, col2_x + col2_w - 30, pB_y, color=LINE, sw=1.5))

    # Операція Write(x, 1) на Вузлі A
    f.append(rect(col2_x + 110, pA_y - 14, 120, 28, fill=COOL, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(col2_x + 170, pA_y + 4, "Write(x, 1)", size=10.5, bold=True, color=FIELD))

    # Операція Read(x) -> 0 на Вузлі B після фізичного завершення Write(x, 1)
    f.append(rect(col2_x + 270, pB_y - 14, 120, 28, fill=WARN_BG, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(col2_x + 330, pB_y + 4, "Read(x) -> 0", size=10.5, bold=True, color=INK))

    # Пізніша операція Read(x) -> 1 на Вузлі B
    f.append(rect(col2_x + 400, pB_y - 14, 60, 28, fill=GOOD, stroke=POS, sw=1.5, rx=4))
    f.append(text(col2_x + 430, pB_y + 4, "R(x)->1", size=9.5, bold=True, color=POS))

    # Пояснення вердикту
    f.append(fitbox(col2_x + 20, 360, col2_w - 40, 160,
                    "Еквівалентний глобальний порядок:\n"
                    "Read(x) -> 0  →  Write(x, 1)  →  Read(x) -> 1.\n"
                    "Цей порядок є повністю легальним у послідовній консистентності,\n"
                    "оскільки він не порушує локальний порядок жодного з вузлів,\n"
                    "хоча у фізичному часі Write(x, 1) завершився раніше за перший Read!",
                    size=10.5, pad=6, fill=COOL, stroke=FIELD, sw=1.2))

    # Підсумкове порівняння знизу
    f.append(fitbox(W / 2 - 450, 560, 900, 95,
                    "Головна відмінність: Лінеаризовність прив'язана до глобального стрілочного годинника (Global Real-Time Order),\n"
                    "тому застаріле читання після завершення запису є порушенням.\n"
                    "Послідовна консистентність вимагає лише існування єдиного логічного чергування (Total Order), що зберігає порядок операцій кожного процесу.",
                    size=10.5, pad=6, fill="#f8f9fa", stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "linearizability-vs-sequential-timeline.svg"), W, H, *f)


# ── 3. Причинно-наслідкові залежності та векторні годинники ─────────────────
def causal_dependency_graph():
    W, H = 1080, 580
    f = []

    f.append(text(W / 2, 32, "Причинна консистентність: відстеження зв'язків «спричинено раніше»",
                  size=16, bold=True))

    y1, y2, y3 = 110, 230, 350
    x0, x1 = 180, 1000

    # Три вузли
    f.append(fitbox(20, y1 - 22, 140, 44, "Вузол 1\n(Аліса)", size=11, bold=True, fill=COOL))
    f.append(line(x0, y1, x1, y1, color=LINE, sw=1.5))

    f.append(fitbox(20, y2 - 22, 140, 44, "Вузол 2\n(Боб)", size=11, bold=True, fill=COOL))
    f.append(line(x0, y2, x1, y2, color=LINE, sw=1.5))

    f.append(fitbox(20, y3 - 22, 140, 44, "Вузол 3\n(Керол)", size=11, bold=True, fill=COOL))
    f.append(line(x0, y3, x1, y3, color=LINE, sw=1.5))

    # Подія 1: Аліса пише пост a: "Завтра свято!"
    xa = x0 + 60
    f.append(circle(xa, y1, 6, fill=POS, stroke=POS, sw=2))
    b_a, _, _ = textbox(xa, y1 - 38, "a = Write(\"Завтра свято!\")\nVC: [1, 0, 0]",
                        size=10, pad=4, fill=GOOD, stroke=POS, sw=1.2, color=POS, bold=True)
    f.append(b_a)

    # Реплікація повідомлення a від Вузла 1 до Вузла 2
    xb_recv = x0 + 260
    f.append(line(xa + 5, y1 + 5, xb_recv - 5, y2 - 5, color=POS, sw=1.8, dash="4,3"))
    f.append(arrow(xb_recv - 15, y2 - 12, xb_recv, y2, color=POS, sw=1.8))

    # Подія 2: Боб читає 'a' і пише відповідь b: "О котрій зустріч?"
    f.append(circle(xb_recv, y2, 6, fill=POS, stroke=POS, sw=2))
    b_b, _, _ = textbox(xb_recv, y2 + 42, "b = Write(\"О котрій зустріч?\")\nспричинено подією 'a'!\nVC: [1, 1, 0]",
                        size=10, pad=4, fill=GOOD, stroke=POS, sw=1.2, color=POS, bold=True)
    f.append(b_b)

    # Причинний зв'язок a -> b
    f.append(line(xa, y1 + 10, xb_recv, y2 - 10, color=POS, sw=2))

    # Подія 3: Паралельний незалежний пост c від Вузла 3: "Хтось бачив мої ключі?"
    xc = x0 + 180
    f.append(circle(xc, y3, 6, fill=ACCENT, stroke=ACCENT, sw=2))
    b_c, _, _ = textbox(xc, y3 + 40, "c = Write(\"Де мої ключі?\")\nконкурентна подія (c || a, c || b)\nVC: [0, 0, 1]",
                        size=10, pad=4, fill=WARN_BG, stroke=ACCENT, sw=1.2, color=ACCENT, bold=True)
    f.append(b_c)

    # Передача подій до Керол (Вузол 3): якщо 'b' приходить раніше за 'a'
    x_b_arrive = x0 + 580
    f.append(line(xb_recv + 10, y2 + 10, x_b_arrive, y3 - 10, color=MUTED, sw=1.5, dash="4,3"))
    f.append(arrow(x_b_arrive - 12, y3 - 18, x_b_arrive, y3 - 5, color=MUTED, sw=1.5))

    # Буфер відкладеної доставки на Вузлі 3
    f.append(rect(x_b_arrive - 15, y3 - 18, 30, 36, fill=WARM, stroke=POS, sw=1.5))
    b_buf, _, _ = textbox(x_b_arrive + 80, y3 - 55,
                          "Отримано 'b', але VC[0]=0 < 1!\n'b' залежить від 'a', якої ще немає.\nПОДІЮ 'b' БУФЕРИЗОВАНО.",
                          size=9.5, pad=5, fill=WARM, stroke=POS, sw=1.2, color=POS, bold=True)
    f.append(b_buf)

    # Прибуття 'a' на Вузол 3
    x_a_arrive = x0 + 720
    f.append(line(xa + 20, y1 + 10, x_a_arrive, y3 - 10, color=FIELD, sw=1.5, dash="4,3"))
    f.append(arrow(x_a_arrive - 12, y3 - 18, x_a_arrive, y3 - 5, color=FIELD, sw=1.5))

    # Розблокування доставки на Вузлі 3
    f.append(circle(x_a_arrive, y3, 6, fill=FIELD, stroke=FIELD, sw=2))
    b_deliv, _, _ = textbox(x_a_arrive, y3 + 45,
                            "Отримано 'a' (VC: [1,0,0]).\nДоставляється 'a', потім розблоковується 'b'!\nПорядок збережено: a → b.",
                            size=10, pad=5, fill=GOOD, stroke=FIELD, sw=1.2, color=FIELD, bold=True)
    f.append(b_deliv)

    # Пояснення правила причинності знизу
    f.append(fitbox(W / 2 - 460, 465, 920, 75,
                    "Правило причинної узгодженості (Causal Consistency):\n"
                    "1. Якщо a → b (подія b причинно залежить від a), жоден вузол не має права побачити b раніше за a.\n"
                    "2. Якщо a || c (події незалежні), різні вузли можуть бачити їх у довільному відносному порядку (a перед c або c перед a).",
                    size=11, pad=6, fill=COOL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "causal-dependency-graph.svg"), W, H, *f)


# ── 4. Порушення композиційності послідовної консистентності ─────────────────
def composability_violation():
    W, H = 1080, 580
    f = []

    f.append(text(W / 2, 30, "Чому лінеаризовність є композиційною, а послідовна консистентність — ні",
                  size=15, bold=True))

    col1_x, col1_w = 40, 470
    col2_x, col2_w = 570, 470

    # Лівий блок: Лінеаризовність (композиційна)
    f.append(rect(col1_x, 60, col1_w, 420, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(text(col1_x + col1_w / 2, 85, "ЛІНЕАРИЗОВНІСТЬ: Композиційна (Local)", size=13, bold=True, color=POS))
    f.append(text(col1_x + col1_w / 2, 105, "Властивість локальності (Herlihy & Wing, 1990)", size=10.5, color=MUTED))

    f.append(fitbox(col1_x + 20, 125, col1_w - 40, 80,
                    "Теорема про локальність:\n"
                    "Історія виконання H над множиною об'єктів {x, y, z...}\n"
                    "є лінеаризовною тоді й лише тоді, коли проекція H|x\n"
                    "є лінеаризовною для кожного окремого об'єкта x.",
                    size=10.5, pad=5, fill=GOOD, stroke=POS, sw=1.2))

    f.append(fitbox(col1_x + 20, 220, col1_w - 40, 110,
                    "Практичний наслідок для інженера:\n"
                    "Можна розробити окремий лінеаризовний регістр X,\n"
                    "окремий лінеаризовний регістр Y і об'єднати їх у спільну систему.\n"
                    "Вся композитна система гарантовано залишиться лінеаризовною\n"
                    "без потреби в додатковій глобальній синхронізації між X та Y.",
                    size=10.5, pad=6, fill=COOL, stroke=LINE, sw=1.2))

    f.append(circle(col1_x + 70, 375, 20, fill=GOOD, stroke=POS, sw=2))
    f.append(text(col1_x + 70, 380, "X", size=13, bold=True, color=POS))
    f.append(text(col1_x + 115, 380, "+", size=16, bold=True, color=LINE))
    f.append(circle(col1_x + 160, 375, 20, fill=GOOD, stroke=POS, sw=2))
    f.append(text(col1_x + 160, 380, "Y", size=13, bold=True, color=POS))
    f.append(text(col1_x + 210, 380, "=", size=16, bold=True, color=LINE))
    f.append(rect(col1_x + 240, 355, 180, 40, fill=GOOD, stroke=POS, sw=1.8, rx=6))
    f.append(text(col1_x + 330, 380, "Лінеаризовна система", size=11, bold=True, color=POS))

    # Правий блок: Послідовна консистентність (НЕ композиційна)
    f.append(rect(col2_x, 60, col2_w, 420, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(text(col2_x + col2_w / 2, 85, "ПОСЛІДОВНА КОНСИСТЕНТНІСТЬ: Некомпозиційна", size=13, bold=True, color=POS))
    f.append(text(col2_x + col2_w / 2, 105, "Порушення композиції двох коректних підсистем", size=10.5, color=MUTED))

    f.append(fitbox(col2_x + 20, 125, col2_w - 40, 80,
                    "Контрприклад взаємної несумісності:\n"
                    "Історія проекції H|x є послідовно консистентною.\n"
                    "Історія проекції H|y є послідовно консистентною.\n"
                    "Але спільна історія H над {x, y} НЕ є послідовно консистентною!",
                    size=10.5, pad=5, fill=WARM, stroke=POS, sw=1.2))

    f.append(fitbox(col2_x + 20, 220, col2_w - 40, 110,
                    "Чому так відбувається:\n"
                    "Для об'єкта X існує валідна послідовність S_x (де Вузол 1 випереджає Вузол 2).\n"
                    "Для об'єкта Y існує валідна послідовність S_y (де Вузол 2 випереджає Вузол 1).\n"
                    "Неможливо знайти ЖОДНОГО єдиного глобального порядку S,\n"
                    "який би одночасно задовольнив вимоги порядку для обох об'єктів!",
                    size=10.5, pad=6, fill=COOL, stroke=LINE, sw=1.2))

    f.append(circle(col2_x + 70, 375, 20, fill=COOL, stroke=FIELD, sw=2))
    f.append(text(col2_x + 70, 380, "X", size=13, bold=True, color=FIELD))
    f.append(text(col2_x + 115, 380, "+", size=16, bold=True, color=LINE))
    f.append(circle(col2_x + 160, 375, 20, fill=COOL, stroke=FIELD, sw=2))
    f.append(text(col2_x + 160, 380, "Y", size=13, bold=True, color=FIELD))
    f.append(text(col2_x + 210, 380, "=", size=16, bold=True, color=LINE))
    f.append(rect(col2_x + 240, 355, 180, 40, fill=WARM, stroke=POS, sw=1.8, rx=6))
    f.append(text(col2_x + 330, 380, "НЕ послідовна!", size=11, bold=True, color=POS))

    # Нижній висновок
    f.append(fitbox(W / 2 - 450, 495, 900, 65,
                    "Інженерний висновок: Лінеаризовність дозволяє модульну композицію розподілених сервісів без глобального координатора.\n"
                    "Послідовна консистентність не масштабується модульно: композиція двох коректних сервісів може зламати глобальну консистентність.",
                    size=10.5, pad=6, fill=WARN_BG, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "composability-violation.svg"), W, H, *f)


def main():
    consistency_spectrum_hierarchy()
    linearizability_vs_sequential_timeline()
    causal_dependency_graph()
    composability_violation()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
