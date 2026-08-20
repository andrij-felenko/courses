# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def path(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{d_attr}/>'

def polyline(pts, color=LINE, sw=1.5, dash=None):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts_str}" stroke="{color}" stroke-width="{sw}" fill="none"{d_attr}/>'

def dashed_rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.5, rx=6, dash="4,4"):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>' % (x, y, w, h, rx, fill, stroke, sw, dash))


# ── Фігура 1: Монополізація FIFO проти чесного планування черг ───────────────
def fig_fifo_vs_fair_queuing():
    W, H = 1000, 520
    frags = []

    # Заголовок
    frags.append(text(500, 28, "Монополізація черги FIFO галасливим сусідом проти справедливого розподілу (Fair Queuing)", size=15, bold=True))

    # Секція 1: Спільна черга FIFO (зверху)
    frags.append(rect(30, 55, 940, 205, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(50, 80, "Спільна черга FIFO: проблема «галасливого сусіда» (Noisy Neighbor)", size=13, bold=True, color=POS, anchor="start"))
    frags.append(text(50, 100, "Клієнт A генерує шторм важких запитів; критичний клієнт B блокується в хвості й падає за таймаутом.", size=11, color=INK, anchor="start"))

    # Вхідний потік зліва
    frags.append(rect(45, 125, 160, 115, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(125, 145, "Вхідний потік:", size=11, bold=True, color=INK))
    frags.append(text(125, 168, "• Клієнт A: 50 000 RPS", size=10, bold=True, color=POS))
    frags.append(text(125, 188, "• Клієнт B: 10 RPS", size=10, bold=True, color=FIELD))
    frags.append(text(125, 208, "• Клієнт C: 50 RPS", size=10, color=MUTED))
    frags.append(text(125, 226, "(Спільний сокет / буфер)", size=9, italic=True, color=MUTED))

    frags.append(arrow(210, 180, 245, 180, color=LINE, sw=1.5))

    # Єдина черга FIFO (блокування)
    frags.append(rect(250, 125, 520, 115, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    frags.append(text(510, 145, "Спільна буферизована черга FIFO (10 000 слотів)", size=11, bold=True, color=POS))

    # Елементи в черзі: суцільний потік A і один загублений B
    frags.append(rect(265, 160, 65, 65, fill="#fca5a5", stroke=POS, sw=1, rx=4))
    frags.append(text(297, 187, "Req A", size=10, bold=True, color=POS))
    frags.append(text(297, 207, "Голова", size=9, color=INK))

    frags.append(rect(335, 160, 65, 65, fill="#fca5a5", stroke=POS, sw=1, rx=4))
    frags.append(text(367, 187, "Req A", size=10, bold=True, color=POS))
    frags.append(text(367, 207, "№ 2", size=9, color=INK))

    frags.append(rect(405, 160, 65, 65, fill="#fca5a5", stroke=POS, sw=1, rx=4))
    frags.append(text(437, 187, "Req A", size=10, bold=True, color=POS))
    frags.append(text(437, 207, "№ 3", size=9, color=INK))

    frags.append(rect(475, 160, 75, 65, fill="#fca5a5", stroke=POS, sw=1, rx=4))
    frags.append(text(512, 187, "... 99.8% A ...", size=10, bold=True, color=POS))
    frags.append(text(512, 207, "9 980 шт.", size=9, color=INK))

    frags.append(rect(555, 160, 65, 65, fill="#fca5a5", stroke=POS, sw=1, rx=4))
    frags.append(text(587, 187, "Req A", size=10, bold=True, color=POS))
    frags.append(text(587, 207, "№ 9998", size=9, color=INK))

    # Маленький заблокований B у хвості
    frags.append(rect(625, 160, 65, 65, fill="#bbf7d0", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(657, 187, "Req B", size=10, bold=True, color=FIELD))
    frags.append(text(657, 207, "Застряг!", size=9, bold=True, color=POS))

    frags.append(rect(695, 160, 65, 65, fill="#fca5a5", stroke=POS, sw=1, rx=4))
    frags.append(text(727, 187, "Req A", size=10, bold=True, color=POS))
    frags.append(text(727, 207, "Хвіст", size=9, color=INK))

    frags.append(arrow(775, 180, 810, 180, color=LINE, sw=1.5))

    # Результат FIFO справа
    frags.append(rect(815, 125, 140, 115, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    frags.append(text(885, 145, "Наслідки FIFO:", size=11, bold=True, color=POS))
    frags.append(text(885, 168, "• Затримка B > 4.5 с", size=10, color=POS))
    frags.append(text(885, 188, "• Клієнт B падає (504)", size=10, bold=True, color=POS))
    frags.append(text(885, 208, "• Порушення SLA B", size=10, color=POS))
    frags.append(text(885, 226, "• Голодування (Starvation)", size=9, italic=True, color=POS))


    # Секція 2: Справедливий розподіл із ізольованими чергами (знизу)
    frags.append(rect(30, 275, 940, 225, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(50, 300, "Справедливе планування (Fair Queuing / DRR): повна ізоляція та чесні кванти", size=13, bold=True, color=FIELD, anchor="start"))
    frags.append(text(50, 320, "Кожен клієнт має незалежну чергу. Планувальник чергує обробку, гарантуючи мікросекундну затримку для легких клієнтів.", size=11, color=INK, anchor="start"))

    # Вхідний потік
    frags.append(rect(45, 340, 160, 145, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(125, 360, "Класифікатор потоків", size=11, bold=True, color=INK))
    frags.append(text(125, 380, "(Tenant ID / API Key)", size=10, color=MUTED))
    frags.append(text(125, 405, "Потік A → Черга Q_A", size=9, bold=True, color=POS))
    frags.append(text(125, 425, "Потік B → Черга Q_B", size=9, bold=True, color=FIELD))
    frags.append(text(125, 445, "Потік C → Черга Q_C", size=9, bold=True, color="#4338ca"))
    frags.append(text(125, 468, "Хешування / Селектор", size=9, italic=True, color=MUTED))

    # Стрілки маршрутизації
    frags.append(arrow(210, 375, 245, 365, color=POS, sw=1.2))
    frags.append(arrow(210, 412, 245, 412, color=FIELD, sw=1.5))
    frags.append(arrow(210, 450, 245, 460, color="#4338ca", sw=1.2))

    # Три ізольовані черги
    # Черга A (переповнена, скидає надлишок)
    frags.append(rect(250, 340, 280, 42, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(285, 365, "Q_A:", size=10, bold=True, color=POS))
    frags.append(rect(310, 345, 30, 32, fill="#fca5a5", stroke=POS, sw=1, rx=2))
    frags.append(text(325, 365, "A1", size=9, color=INK))
    frags.append(rect(345, 345, 30, 32, fill="#fca5a5", stroke=POS, sw=1, rx=2))
    frags.append(text(360, 365, "A2", size=9, color=INK))
    frags.append(rect(380, 345, 30, 32, fill="#fca5a5", stroke=POS, sw=1, rx=2))
    frags.append(text(395, 365, "A3", size=9, color=INK))
    frags.append(text(460, 365, "(Хвіст A скидається)", size=9, bold=True, color=POS))

    # Черга B (майже порожня, миттєвий прохід)
    frags.append(rect(250, 392, 280, 42, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(285, 417, "Q_B:", size=10, bold=True, color=FIELD))
    frags.append(rect(310, 397, 30, 32, fill="#86efac", stroke=FIELD, sw=1, rx=2))
    frags.append(text(325, 417, "B1", size=9, bold=True, color=INK))
    frags.append(text(420, 417, "(Порожня: час у черзі < 1 мс)", size=9, bold=True, color=FIELD))

    # Черга C
    frags.append(rect(250, 444, 280, 42, fill="#e0e7ff", stroke="#4338ca", sw=1.2, rx=4))
    frags.append(text(285, 469, "Q_C:", size=10, bold=True, color="#4338ca"))
    frags.append(rect(310, 449, 30, 32, fill="#c7d2fe", stroke="#4338ca", sw=1, rx=2))
    frags.append(text(325, 469, "C1", size=9, color=INK))
    frags.append(rect(345, 449, 30, 32, fill="#c7d2fe", stroke="#4338ca", sw=1, rx=2))
    frags.append(text(360, 469, "C2", size=9, color=INK))
    frags.append(text(420, 469, "(Штатна затримка 2 мс)", size=9, color="#4338ca"))

    # Шедулер по центру
    frags.append(rect(560, 340, 210, 145, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(665, 362, "Справедливий арбітр", size=11, bold=True, color=FIELD))
    frags.append(text(665, 380, "(DRR / WFQ Scheduler)", size=10, color=MUTED))
    frags.append(text(665, 405, "• Кванти пропорційні вазі", size=9, color=INK))
    frags.append(text(665, 423, "• Раунд-робін вибірка", size=9, color=INK))
    frags.append(text(665, 441, "• A не витісняє B і C", size=9, bold=True, color=FIELD))
    frags.append(text(665, 465, "Вихід: [B1] → [A1] → [C1] ...", size=9, bold=True, color=INK))

    frags.append(arrow(535, 412, 555, 412, color=LINE, sw=1.5))
    frags.append(arrow(775, 412, 810, 412, color=FIELD, sw=1.8))

    # Результат Fair Queuing
    frags.append(rect(815, 340, 140, 145, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(885, 362, "Результат:", size=11, bold=True, color=FIELD))
    frags.append(text(885, 385, "• Затримка B: 2 мс", size=10, bold=True, color=FIELD))
    frags.append(text(885, 405, "• SLA B збережено", size=10, color=FIELD))
    frags.append(text(885, 425, "• Шторм A локалізовано", size=10, color=INK))
    frags.append(text(885, 445, "• Справедливий поділ CPU", size=9, color=INK))
    frags.append(text(885, 468, "• 100% захист сусідів", size=9, bold=True, color=FIELD))

    return render(os.path.join(IMG, 'fifo-monopolization-vs-fair-queuing.svg'), W, H, *frags)


# ── Фігура 2: Покроковий цикл Deficit Round Robin (DRR) ──────────────────────
def fig_drr_cycle():
    W, H = 1000, 540
    frags = []

    frags.append(text(500, 26, "Покроковий цикл алгоритму Deficit Round Robin (DRR): кванти та лічильники дефіциту", size=15, bold=True))

    # Стан черг на початку раунду (зліва)
    frags.append(rect(30, 55, 450, 460, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(255, 82, "Раунд R: Нарахування кванта (Quantum) і вибірка", size=12, bold=True, color=INK))
    frags.append(text(255, 102, "Кожен активний потік отримує Quantum = 500 байт (ваги однакові)", size=10, color=MUTED))

    # Черга 1 у раунді R
    frags.append(rect(45, 125, 420, 105, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(120, 147, "Потік 1 (Q1)", size=11, bold=True, color=INK))
    frags.append(text(120, 167, "Початковий Deficit = 0", size=10, color=MUTED))
    frags.append(text(120, 187, "+ Quantum = 500", size=10, bold=True, color=FIELD))
    frags.append(text(120, 207, "Новий Deficit = 500", size=10, bold=True, color=INK))

    # Пакети Q1: Пакет 600 байт
    frags.append(rect(235, 140, 110, 75, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(290, 165, "Пакет P1_1", size=10, bold=True, color=POS))
    frags.append(text(290, 185, "Розмір = 600 B", size=10, color=POS))
    frags.append(text(290, 203, "600 > 500 Deficit!", size=9, bold=True, color=POS))

    frags.append(rect(355, 140, 95, 75, fill="#f3f4f6", stroke="#d1d5db", sw=1, rx=4))
    frags.append(text(402, 172, "Рішення:", size=10, bold=True, color=INK))
    frags.append(text(402, 190, "Пакет чекає.", size=9, color=POS))
    frags.append(text(402, 206, "Deficit = 500", size=9, italic=True, color=MUTED))

    # Черга 2 у раунді R
    frags.append(rect(45, 245, 420, 125, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(120, 267, "Потік 2 (Q2)", size=11, bold=True, color=INK))
    frags.append(text(120, 287, "Початковий Deficit = 0", size=10, color=MUTED))
    frags.append(text(120, 307, "+ Quantum = 500", size=10, bold=True, color=FIELD))
    frags.append(text(120, 327, "Новий Deficit = 500", size=10, bold=True, color=INK))
    frags.append(text(120, 347, "Обробка: 500 - 200 = 300", size=9, color=FIELD))

    # Пакети Q2: Пакет 200 байт та 400 байт
    frags.append(rect(235, 260, 100, 95, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(285, 285, "Пакет P2_1", size=10, bold=True, color=FIELD))
    frags.append(text(285, 305, "Розмір = 200 B", size=10, color=FIELD))
    frags.append(text(285, 325, "200 ≤ 500: ГОТОВО", size=9, bold=True, color=FIELD))
    frags.append(text(285, 343, "Залишок: 300 B", size=9, bold=True, color=INK))

    frags.append(rect(345, 260, 110, 95, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(400, 285, "Пакет P2_2 (400 B)", size=9, bold=True, color=POS))
    frags.append(text(400, 305, "400 > 300 (Deficit)", size=9, color=POS))
    frags.append(text(400, 325, "P2_2 чекає раунд R+1", size=9, color=INK))
    frags.append(text(400, 343, "Deficit = 300", size=9, italic=True, color=MUTED))

    # Черга 3 у раунді R (порожня)
    frags.append(rect(45, 385, 420, 115, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(120, 410, "Потік 3 (Q3)", size=11, bold=True, color=INK))
    frags.append(text(120, 430, "Черга порожня", size=10, italic=True, color=MUTED))
    frags.append(text(120, 452, "Правило обнулення:", size=10, bold=True, color=POS))
    frags.append(text(120, 472, "Deficit скидається в 0!", size=10, bold=True, color=POS))

    frags.append(rect(235, 400, 220, 85, fill="#fef2f2", stroke=POS, sw=1, rx=4))
    frags.append(text(345, 425, "Захист від накопичення боргу:", size=10, bold=True, color=POS))
    frags.append(text(345, 445, "Потік не має права збирати дефіцит,", size=9, color=INK))
    frags.append(text(345, 463, "коли він не має роботи (No Free Lunch)", size=9, bold=True, color=POS))


    # Стан черг у наступному раунді R+1 (справа)
    frags.append(rect(515, 55, 455, 460, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(742, 82, "Раунд R+1: Використання збереженого дефіциту", size=12, bold=True, color=FIELD))
    frags.append(text(742, 102, "Збережений дефіцит компенсує великі пакети без затримок", size=10, color=MUTED))

    # Черга 1 у раунді R+1
    frags.append(rect(530, 125, 425, 155, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(615, 150, "Потік 1 (Q1)", size=11, bold=True, color=INK))
    frags.append(text(615, 172, "Було з раунду R: 500", size=10, color=MUTED))
    frags.append(text(615, 192, "+ Quantum = 500", size=10, bold=True, color=FIELD))
    frags.append(text(615, 212, "Сумарний Deficit = 1000", size=10, bold=True, color=FIELD))
    frags.append(text(615, 235, "Відправка P1_1 (600 B):", size=10, bold=True, color=INK))
    frags.append(text(615, 255, "Залишок: 1000 - 600 = 400 B", size=9, bold=True, color=FIELD))

    frags.append(rect(735, 140, 205, 125, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(837, 168, "Пакет P1_1 (600 B)", size=11, bold=True, color=FIELD))
    frags.append(text(837, 192, "УСПІШНО ВІДПРАВЛЕНО!", size=10, bold=True, color=FIELD))
    frags.append(text(837, 215, "600 ≤ 1000 (Deficit)", size=9, color=INK))
    frags.append(text(837, 235, "Великий пакет пройшов", size=9, color=MUTED))
    frags.append(text(837, 250, "без шкоди іншим потокам", size=9, italic=True, color=MUTED))

    # Черга 2 у раунді R+1
    frags.append(rect(530, 295, 425, 145, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(615, 320, "Потік 2 (Q2)", size=11, bold=True, color=INK))
    frags.append(text(615, 342, "Було з раунду R: 300", size=10, color=MUTED))
    frags.append(text(615, 362, "+ Quantum = 500", size=10, bold=True, color=FIELD))
    frags.append(text(615, 382, "Сумарний Deficit = 800", size=10, bold=True, color=FIELD))
    frags.append(text(615, 405, "Відправка P2_2 (400 B):", size=10, bold=True, color=INK))
    frags.append(text(615, 425, "Залишок: 800 - 400 = 400 B", size=9, bold=True, color=FIELD))

    frags.append(rect(735, 305, 205, 120, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(837, 335, "Пакет P2_2 (400 B)", size=11, bold=True, color=FIELD))
    frags.append(text(837, 360, "УСПІШНО ВІДПРАВЛЕНО!", size=10, bold=True, color=FIELD))
    frags.append(text(837, 385, "400 ≤ 800 (Deficit)", size=9, color=INK))
    frags.append(text(837, 407, "Швидкість виконання: O(1)", size=10, bold=True, color=FIELD))

    # Підсумок властивостей DRR знизу
    frags.append(rect(530, 450, 425, 55, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=6))
    frags.append(text(742, 472, "Властивості DRR: складність O(1) на пакет, ідеальна асимптотична чесність,", size=9, bold=True, color="#1e40af"))
    frags.append(text(742, 490, "підтримка пакетів довільної довжини без сортування подій.", size=9, color="#1e40af"))

    return render(os.path.join(IMG, 'drr-deficit-round-robin-cycle.svg'), W, H, *frags)


# ── Фігура 3: Архітектура розподіленого квотування (Distributed Quotas) ──────
def fig_distributed_quota_architecture():
    W, H = 1020, 560
    frags = []

    frags.append(text(510, 26, "Дворівнева архітектура розподіленого квотування з асинхронним лізингом токенів", size=15, bold=True))

    # Верхній рівень: Вхідний трафік та API-шлюзи (Edge Gateways)
    frags.append(rect(30, 55, 960, 220, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(510, 80, "Рівень даних (Data Plane): Вхідні шлюзи Envoy / API Gateway з локальними бакетами", size=13, bold=True, color=INK))

    # Gateway 1 (AZ-1)
    frags.append(rect(50, 100, 285, 160, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(192, 122, "API Gateway #1 (Зона AZ-a)", size=11, bold=True, color=INK))
    frags.append(rect(65, 135, 255, 55, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(192, 155, "Локальний Token Bucket (L1)", size=10, bold=True, color=FIELD))
    frags.append(text(192, 175, "Оренда: 300 токенів / 500 мс", size=9, color=INK))
    frags.append(text(192, 210, "Перевірка в пам'яті: < 10 мкс", size=10, bold=True, color=FIELD))
    frags.append(text(192, 230, "Рішення приймається локально", size=9, color=MUTED))
    frags.append(text(192, 248, "0 мережевих RTT до сховища", size=9, italic=True, color=FIELD))

    # Gateway 2 (AZ-2)
    frags.append(rect(365, 100, 285, 160, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(507, 122, "API Gateway #2 (Зона AZ-b)", size=11, bold=True, color=INK))
    frags.append(rect(380, 135, 255, 55, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(507, 155, "Локальний Token Bucket (L1)", size=10, bold=True, color=FIELD))
    frags.append(text(507, 175, "Оренда: 400 токенів / 500 мс", size=9, color=INK))
    frags.append(text(507, 210, "Перевірка в пам'яті: < 10 мкс", size=10, bold=True, color=FIELD))
    frags.append(text(507, 230, "Рішення приймається локально", size=9, color=MUTED))
    frags.append(text(507, 248, "0 мережевих RTT до сховища", size=9, italic=True, color=FIELD))

    # Gateway 3 (AZ-3)
    frags.append(rect(685, 100, 285, 160, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(827, 122, "API Gateway #3 (Зона AZ-c)", size=11, bold=True, color=INK))
    frags.append(rect(700, 135, 255, 55, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(827, 155, "Локальний Token Bucket (L1)", size=10, bold=True, color=POS))
    frags.append(text(827, 175, "Залишок: 0 токенів (вичерпано)", size=9, color=POS))
    frags.append(text(827, 210, "Fail-Fast відповідь: 429 Too Many", size=10, bold=True, color=POS))
    frags.append(text(827, 230, "RateLimit-Reset: 350ms", size=9, color=POS))
    frags.append(text(827, 248, "Захист бекенду від сплеску", size=9, italic=True, color=POS))


    # Зв'язок між рівнями: Асинхронний лізинг
    frags.append(line(192, 260, 280, 320, color="#3b82f6", sw=1.5, dash="4,4"))
    frags.append(line(507, 260, 510, 320, color="#3b82f6", sw=1.5, dash="4,4"))
    frags.append(line(827, 260, 740, 320, color="#3b82f6", sw=1.5, dash="4,4"))

    frags.append(rect(340, 282, 340, 30, fill="#eff6ff", stroke="#3b82f6", sw=1, rx=4))
    frags.append(text(510, 302, "Фоновий асинхронний лізинг (gRPC Batch Lease)", size=10, bold=True, color="#1e40af"))


    # Нижній рівень: Площина управління та центральний координатор квот (Control Plane)
    frags.append(rect(30, 325, 960, 215, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(510, 350, "Площина контролю (Control Plane): Центральний координатор глобальних квот (L2)", size=13, bold=True, color=INK))

    # Центральний Quota Server / Redis Cluster
    frags.append(rect(50, 370, 440, 150, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(270, 392, "Центральний Quota Service (Redis / Raft)", size=11, bold=True, color=INK))
    frags.append(text(270, 415, "• Глобальний ліміт Tenant A = 1 000 RPS", size=10, bold=True, color=FIELD))
    frags.append(text(270, 435, "• Розподіл пулів лізингу: AZ-a (30%), AZ-b (40%), AZ-c (30%)", size=9, color=INK))
    frags.append(text(270, 455, "• Автоматичне повернення невикористаних токенів за TTL", size=9, color=MUTED))
    frags.append(text(270, 475, "• Захист від подвійних витрат через Redis Lua / Cas", size=9, color=INK))
    frags.append(text(270, 498, "Консистентність квот без гальмування запитів", size=9, bold=True, color=FIELD))

    # Правила квотування та деградація
    frags.append(rect(520, 370, 450, 150, fill="#ffffff", stroke="#9ca3af", sw=1.2, rx=6))
    frags.append(text(745, 392, "Стратегії відмови координатора квот", size=11, bold=True, color=INK))
    frags.append(rect(535, 405, 205, 100, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    frags.append(text(637, 425, "Fail-Open (Низький ризик):", size=10, bold=True, color=FIELD))
    frags.append(text(637, 445, "При падінні Redis шлюзи", size=9, color=INK))
    frags.append(text(637, 463, "пропускають штатний трафік.", size=9, color=INK))
    frags.append(text(637, 485, "Пріоритет: Доступність бізнесу", size=9, bold=True, color=FIELD))

    frags.append(rect(750, 405, 205, 100, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(852, 425, "Fail-Closed (Фінанси/LLM):", size=10, bold=True, color=POS))
    frags.append(text(852, 445, "При падінні Redis шлюзи", size=9, color=INK))
    frags.append(text(852, 463, "блокують нові виклики.", size=9, color=INK))
    frags.append(text(852, 485, "Пріоритет: Захист бюджету", size=9, bold=True, color=POS))

    return render(os.path.join(IMG, 'distributed-quota-leasing-architecture.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_fifo_vs_fair_queuing()
    fig_drr_cycle()
    fig_distributed_quota_architecture()
    print("All figures generated successfully.")
