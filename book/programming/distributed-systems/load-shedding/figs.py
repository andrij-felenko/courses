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


# ── Фігура 1: Пропускна здатність проти корисної роботи (Goodput vs Load) ──────
def fig_goodput_vs_load():
    W, H = 1000, 540
    frags = []

    # Заголовок
    frags.append(text(500, 28, "Корисна пропускна здатність (Goodput) проти загального навантаження", size=16, bold=True))

    # Графік 1: Без Load Shedding (зліва)
    frags.append(rect(40, 50, 440, 460, fill="#ffffff", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(260, 75, "Без скидання навантаження (катастрофа FIFO)", size=13, bold=True, color=POS))

    # Осі
    frags.append(line(80, 450, 450, 450, color=LINE, sw=1.5)) # X
    frags.append(line(80, 450, 80, 110, color=LINE, sw=1.5))  # Y
    frags.append(arrow(80, 450, 460, 450, color=LINE, sw=1.5))
    frags.append(arrow(80, 450, 80, 100, color=LINE, sw=1.5))

    frags.append(text(450, 475, "Вхідний трафік (Offered Load)", size=11, color=MUTED, anchor="end"))
    frags.append(text(75, 95, "Пропускна здатність (RPS)", size=11, color=MUTED, anchor="start"))

    # Пунктирна лінія номінальної ємності
    frags.append(line(80, 250, 440, 250, color="#9ca3af", sw=1.2, dash="4,4"))
    frags.append(text(435, 242, "Номінальна місткість (C)", size=11, color=MUTED, anchor="end"))

    # Крива загальної завантаженості (Throughput / CPU 100%)
    frags.append(polyline([(80, 450), (220, 250), (440, 250)], color="#4b5563", sw=2, dash="3,3"))
    frags.append(text(350, 268, "Сирий Throughput (CPU 100%)", size=10, color="#4b5563"))

    # Крива корисної пропускної здатності (Goodput) без скидання -> спадає до нуля
    frags.append(path("M 80 450 Q 180 300 220 250 Q 250 260 280 390 Q 330 440 440 444", stroke=POS, sw=3, fill="none"))
    frags.append(text(290, 350, "Goodput обвалюється до нуля", size=11, bold=True, color=POS, anchor="start"))
    frags.append(text(290, 368, "(марна робота над протухлими запитами)", size=10, color=POS, anchor="start"))

    # Зона колапсу
    frags.append(rect(225, 105, 240, 95, fill="#fef2f2", stroke=POS, sw=1, rx=6))
    frags.append(text(345, 125, "Колапс «Badput»:", size=11, bold=True, color=POS))
    frags.append(text(345, 145, "• Черга неконтрольовано росте", size=10, color=INK))
    frags.append(text(345, 163, "• Клієнти відпадають за таймаутом", size=10, color=INK))
    frags.append(text(345, 181, "• Сервер марнує 100% CPU на сміття", size=10, color=INK))


    # Графік 2: Із Load Shedding (справа)
    frags.append(rect(520, 50, 440, 460, fill="#ffffff", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(740, 75, "Зі скиданням навантаження (Load Shedding)", size=13, bold=True, color=FIELD))

    # Осі
    frags.append(line(560, 450, 930, 450, color=LINE, sw=1.5)) # X
    frags.append(line(560, 450, 560, 110, color=LINE, sw=1.5))  # Y
    frags.append(arrow(560, 450, 940, 450, color=LINE, sw=1.5))
    frags.append(arrow(560, 450, 560, 100, color=LINE, sw=1.5))

    frags.append(text(930, 475, "Вхідний трафік (Offered Load)", size=11, color=MUTED, anchor="end"))
    frags.append(text(555, 95, "Пропускна здатність (RPS)", size=11, color=MUTED, anchor="start"))

    # Пунктирна лінія номінальної ємності
    frags.append(line(560, 250, 920, 250, color="#9ca3af", sw=1.2, dash="4,4"))
    frags.append(text(915, 242, "Номінальна місткість (C)", size=11, color=MUTED, anchor="end"))

    # Крива Goodput зі скиданням -> залишається на рівні C
    frags.append(path("M 560 450 L 700 250 L 920 250", stroke=FIELD, sw=3, fill="none"))
    frags.append(text(805, 230, "Стабільний Goodput = C", size=11, bold=True, color=FIELD))

    # Область скинутих запитів (Shedded requests)
    frags.append(polyline([(700, 250), (920, 135), (920, 250)], color="#f59e0b", sw=1.5, dash="3,3"))
    frags.append(text(815, 175, "Швидко відхилені запити", size=11, bold=True, color="#d97706"))
    frags.append(text(815, 193, "(Fail-Fast: HTTP 503 / 429)", size=10, color="#d97706"))

    # Зона стабільності
    frags.append(rect(700, 95, 235, 65, fill="#f0fdf4", stroke=FIELD, sw=1, rx=6))
    frags.append(text(817, 115, "Самозахист системи:", size=11, bold=True, color=FIELD))
    frags.append(text(817, 133, "• Детермінований час відповіді", size=10, color=INK))
    frags.append(text(817, 149, "• 100% прийнятих запитів успішні", size=10, color=INK))

    return render(os.path.join(IMG, 'goodput-vs-load.svg'), W, H, *frags)


# ── Фігура 2: Черга FIFO проти LIFO під час перевантаження ───────────────────
def fig_fifo_vs_lifo_overload():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 28, "Порівняння обробки черги під час перевантаження: FIFO проти LIFO / CoDel", size=16, bold=True))

    # Секція 1: FIFO Death Spiral (зверху)
    frags.append(rect(30, 55, 940, 190, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(50, 80, "FIFO (First-In, First-Out) — Каскадна спіраль смерті", size=13, bold=True, color=POS, anchor="start"))
    frags.append(text(50, 100, "Черга заповнена. Воркери беруть найстаріші запити з голови, дедлайн яких уже вичерпано клієнтом.", size=11, color=INK, anchor="start"))

    # Елементи черги FIFO
    # Воркер зліва
    frags.append(rect(50, 125, 140, 95, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(120, 148, "Воркер CPU", size=12, bold=True, color=POS))
    frags.append(text(120, 168, "Обробляє Req #1", size=10, color=INK))
    frags.append(text(120, 188, "T_wait = 4.8s > 2.0s", size=10, bold=True, color=POS))
    frags.append(text(120, 204, "(Клієнт уже відпав)", size=10, italic=True, color=POS))

    frags.append(arrow(245, 172, 195, 172, color=POS, sw=2))

    # Черга FIFO (блоки)
    # req 1 (голови)
    frags.append(rect(250, 135, 125, 75, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(312, 156, "Req #2 (Голова)", size=11, bold=True, color=POS))
    frags.append(text(312, 175, "В черзі: 4.2 с", size=10, color=POS))
    frags.append(text(312, 193, "Статус: ПРОТУХ", size=10, bold=True, color=POS))

    # req 2
    frags.append(rect(385, 135, 125, 75, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    frags.append(text(447, 156, "Req #3", size=11, bold=True, color=POS))
    frags.append(text(447, 175, "В черзі: 3.5 с", size=10, color=POS))
    frags.append(text(447, 193, "Статус: ПРОТУХ", size=10, bold=True, color=POS))

    # req 3
    frags.append(rect(520, 135, 125, 75, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    frags.append(text(582, 156, "Req #4", size=11, bold=True, color="#d97706"))
    frags.append(text(582, 175, "В черзі: 2.1 с", size=10, color="#d97706"))
    frags.append(text(582, 193, "На межі таймауту", size=10, color="#d97706"))

    # req 4 (хвіст, свіжі)
    frags.append(rect(655, 135, 125, 75, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    frags.append(text(717, 156, "Req #5 (Хвіст)", size=11, bold=True, color=FIELD))
    frags.append(text(717, 175, "В черзі: 0.1 с", size=10, color=FIELD))
    frags.append(text(717, 193, "Свіжий, але чекає!", size=10, bold=True, color=FIELD))

    frags.append(arrow(830, 172, 785, 172, color=MUTED, sw=1.5))
    frags.append(text(890, 165, "Вхідний потік", size=11, bold=True, color=INK))
    frags.append(text(890, 183, "(додається в хвіст)", size=10, color=MUTED))


    # Секція 2: LIFO / Deadline Drop (знизу)
    frags.append(rect(30, 265, 940, 205, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(50, 290, "LIFO / CoDel / Deadline Shedding — Порятунок корисної пропускної здатності", size=13, bold=True, color=FIELD, anchor="start"))
    frags.append(text(50, 310, "Воркер бере найсвіжіший запит із хвоста; протухлі запити з голови негайно відсікаються без обробки.", size=11, color=INK, anchor="start"))

    # Воркер
    frags.append(rect(50, 335, 140, 105, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(120, 360, "Воркер CPU", size=12, bold=True, color=FIELD))
    frags.append(text(120, 380, "Бере Req #5 (хвіст)", size=10, bold=True, color=INK))
    frags.append(text(120, 400, "T_wait = 15ms < 2s", size=10, color=FIELD))
    frags.append(text(120, 420, "Успіх для клієнта!", size=10, bold=True, color=FIELD))

    # Стрілка від свіжого блоку до воркера
    frags.append(arrow(655, 385, 195, 385, color=FIELD, sw=2))

    # Свіжий запит
    frags.append(rect(655, 345, 125, 80, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(717, 368, "Req #5 (Свіжий)", size=11, bold=True, color=FIELD))
    frags.append(text(717, 388, "В черзі: 15 мс", size=10, color=FIELD))
    frags.append(text(717, 408, "Одразу в роботу", size=10, bold=True, color=FIELD))

    # Протухлі відкидаються
    frags.append(dashed_rect(250, 345, 375, 80, fill="#fee2e2", stroke=POS, sw=1.2, dash="4,4", rx=4))
    frags.append(text(437, 368, "Req #1, #2, #3, #4 (Застарілі запити в черзі)", size=11, bold=True, color=POS))
    frags.append(text(437, 388, "T_sojourn > поріг або дедлайн минув", size=10, color=POS))
    frags.append(text(437, 408, "ДІЯ: Миттєве скидання (Shed / Drop) без витрат CPU", size=10, bold=True, color=POS))

    frags.append(arrow(830, 385, 785, 385, color=FIELD, sw=1.5))
    frags.append(text(890, 377, "Нові запити", size=11, bold=True, color=FIELD))
    frags.append(text(890, 395, "Швидкий успіх", size=10, color=MUTED))

    return render(os.path.join(IMG, 'fifo-vs-lifo-overload.svg'), W, H, *frags)


# ── Фігура 3: Багаторівнева архітектура скидання навантаження ────────────────
def fig_load_shedding_architecture():
    W, H = 1040, 560
    frags = []

    frags.append(text(520, 26, "Багаторівневий конвеєр скидання навантаження (Multi-Stage Load Shedding Pipeline)", size=16, bold=True))

    # Блок 1: Вхідний трафік (Клієнти / Балансувальник)
    frags.append(rect(20, 60, 150, 460, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(95, 88, "Вхідний трафік", size=13, bold=True, color=INK))
    frags.append(text(95, 108, "(HTTP / gRPC)", size=11, color=MUTED))

    frags.append(rect(30, 135, 130, 55, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(95, 156, "Критичні T0/T1", size=11, bold=True, color=POS))
    frags.append(text(95, 175, "Health, Оплата", size=10, color=INK))

    frags.append(rect(30, 205, 130, 55, fill="#fef3c7", stroke="#d97706", sw=1, rx=4))
    frags.append(text(95, 226, "Звичайні T2", size=11, bold=True, color="#d97706"))
    frags.append(text(95, 245, "Пошук, Каталог", size=10, color=INK))

    frags.append(rect(30, 275, 130, 55, fill="#e0e7ff", stroke="#4338ca", sw=1, rx=4))
    frags.append(text(95, 296, "Фонові T3", size=11, bold=True, color="#4338ca"))
    frags.append(text(95, 315, "Аналітика, Логи", size=10, color=INK))

    frags.append(rect(30, 360, 130, 85, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(95, 380, "Дедлайни в заголовках:", size=10, bold=True, color=MUTED))
    frags.append(text(95, 400, "grpc-timeout", size=10, color=INK))
    frags.append(text(95, 420, "X-Request-Deadline", size=10, color=INK))

    frags.append(arrow(170, 280, 200, 280, color=LINE, sw=2))

    # Блок 2: Рівень 1 — Класифікатор пріоритетів та ранній фільтр
    frags.append(rect(200, 60, 185, 460, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(292, 88, "1. Класифікатор", size=13, bold=True, color=INK))
    frags.append(text(292, 108, "і перевірка дедлайну", size=11, color=MUTED))

    frags.append(rect(210, 135, 165, 80, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(292, 157, "Перевірка дедлайну:", size=10, bold=True, color=INK))
    frags.append(text(292, 177, "T_remain < T_min_exec?", size=10, color=POS))
    frags.append(text(292, 197, "→ Скинути одразу", size=10, bold=True, color=POS))

    frags.append(rect(210, 230, 165, 105, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(292, 252, "Пріоритизація:", size=10, bold=True, color=INK))
    frags.append(text(292, 272, "При навантаженні > 80%:", size=10, color=MUTED))
    frags.append(text(292, 292, "• Скинути Tier 3 (100%)", size=10, color="#4338ca"))
    frags.append(text(292, 312, "• Скинути Tier 2 (50%)", size=10, color="#d97706"))

    frags.append(rect(210, 350, 165, 85, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(292, 372, "Квоти токенів:", size=10, bold=True, color=INK))
    frags.append(text(292, 392, "Token Bucket per Tier", size=10, color=MUTED))
    frags.append(text(292, 412, "Резерв під Tier 0/1", size=10, bold=True, color=FIELD))

    frags.append(arrow(385, 280, 415, 280, color=LINE, sw=2))

    # Блок 3: Рівень 2 — Черга та монітор часу перебування (Sojourn Time / CoDel)
    frags.append(rect(415, 60, 195, 460, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(512, 88, "2. Черга завдань", size=13, bold=True, color=INK))
    frags.append(text(512, 108, "і монітор затримки", size=11, color=MUTED))

    frags.append(rect(425, 135, 175, 95, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(512, 157, "Контроль черги (CoDel):", size=10, bold=True, color=INK))
    frags.append(text(512, 177, "Вимір t_sojourn у вікні", size=10, color=MUTED))
    frags.append(text(512, 197, "Якщо min(t_wait) > 20ms", size=10, bold=True, color=POS))
    frags.append(text(512, 215, "→ Відсікання нових", size=10, color=POS))

    frags.append(rect(425, 245, 175, 95, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(512, 267, "Адаптивна місткість:", size=10, bold=True, color=INK))
    frags.append(text(512, 287, "TCP Vegas / Gradient limit", size=10, color=MUTED))
    frags.append(text(512, 307, "Динамічний ліміт воркерів", size=10, color=FIELD))
    frags.append(text(512, 325, "Limit_curr = f(RTT_min/RTT)", size=9, color=MUTED))

    frags.append(rect(425, 355, 175, 80, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(512, 377, "Політика вибірки:", size=10, bold=True, color=INK))
    frags.append(text(512, 397, "LIFO під час сплеску", size=10, bold=True, color=FIELD))
    frags.append(text(512, 417, "FIFO у спокійному стані", size=10, color=MUTED))

    frags.append(arrow(610, 280, 640, 280, color=FIELD, sw=2))

    # Блок 4: Рівень 3 — Виконання та плавна деградація
    frags.append(rect(640, 60, 190, 460, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(735, 88, "3. Пул воркерів", size=13, bold=True, color=FIELD))
    frags.append(text(735, 108, "і деградація (Fallback)", size=11, color=MUTED))

    frags.append(rect(650, 135, 170, 85, fill="#dcfce7", stroke=FIELD, sw=1, rx=4))
    frags.append(text(735, 157, "Пул виконання CPU/IO:", size=10, bold=True, color=FIELD))
    frags.append(text(735, 177, "Обмежене число воркерів", size=10, color=INK))
    frags.append(text(735, 195, "CPU < 90%, без блокувань", size=10, color=FIELD))

    frags.append(rect(650, 235, 170, 105, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(735, 257, "Сходинки деградації:", size=10, bold=True, color=INK))
    frags.append(text(735, 277, "1. Вимкнути персоналізацію", size=9, color=MUTED))
    frags.append(text(735, 297, "2. Відповідь зі старого кешу", size=9, color=MUTED))
    frags.append(text(735, 317, "3. Знизити якість медіа", size=9, color=MUTED))

    frags.append(rect(650, 355, 170, 80, fill="#ffffff", stroke="#9ca3af", sw=1, rx=4))
    frags.append(text(735, 377, "Успішна відповідь:", size=10, bold=True, color=FIELD))
    frags.append(text(735, 397, "HTTP 200 OK / gRPC OK", size=10, bold=True, color=FIELD))
    frags.append(text(735, 417, "Високий Goodput!", size=10, color=FIELD))

    # Блок 5: Відхилення (Fail-Fast відповіді) - Справа
    frags.append(rect(860, 60, 160, 460, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(940, 88, "Fail-Fast", size=13, bold=True, color=POS))
    frags.append(text(940, 108, "Відхилення", size=11, color=MUTED))

    frags.append(rect(870, 145, 140, 75, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(940, 167, "HTTP 503 / 429", size=10, bold=True, color=POS))
    frags.append(text(940, 187, "gRPC UNAVAILABLE", size=9, color=POS))
    frags.append(text(940, 203, "RESOURCE_EXHAUSTED", size=9, color=POS))

    frags.append(rect(870, 245, 140, 75, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(940, 267, "Retry-After:", size=10, bold=True, color=POS))
    frags.append(text(940, 287, "Затримка клієнта", size=10, color=INK))
    frags.append(text(940, 305, "Захист від шторму", size=10, color=INK))

    frags.append(rect(870, 345, 140, 75, fill="#fee2e2", stroke=POS, sw=1, rx=4))
    frags.append(text(940, 367, "Телеметрія:", size=10, bold=True, color=POS))
    frags.append(text(940, 387, "Метрики Prometheus", size=10, color=MUTED))
    frags.append(text(940, 405, "requests_shed_total", size=9, color=INK))

    # Стрілки відхилення від етапів 1 та 2
    frags.append(line(375, 175, 870, 175, color=POS, sw=1.2, dash="3,3"))
    frags.append(line(600, 182, 870, 182, color=POS, sw=1.2, dash="3,3"))

    return render(os.path.join(IMG, 'load-shedding-architecture.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_goodput_vs_load()
    fig_fifo_vs_lifo_overload()
    fig_load_shedding_architecture()
    print("All figures generated successfully.")
