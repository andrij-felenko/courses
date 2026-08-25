# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Узгоджений та неузгоджений перерізи (Consistent vs Inconsistent Cut)
def fig_consistent_vs_inconsistent_cut():
    W, H = 960, 470
    p = []

    # Заголовок
    p.append(text(480, 28, "Поняття перерізу розподіленої системи (Global Cut)", size=16, bold=True))

    # Ліва панель: Неузгоджений переріз
    p.append(rect(20, 50, 450, 400, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(fitbox(30, 60, 430, 36, "Неузгоджений переріз (Inconsistent Cut)", size=13, fill="#fdf2ee", stroke=NEG, color=NEG, bold=True))

    # Лінії трьох процесів для лівої панелі
    p.append(text(35, 130, "P1", size=12, bold=True, color=INK, anchor="start"))
    p.append(line(60, 126, 450, 126, color=LINE, sw=1.8))

    p.append(text(35, 210, "P2", size=12, bold=True, color=INK, anchor="start"))
    p.append(line(60, 206, 450, 206, color=LINE, sw=1.8))

    p.append(text(35, 290, "P3", size=12, bold=True, color=INK, anchor="start"))
    p.append(line(60, 286, 450, 286, color=LINE, sw=1.8))

    # Події лівої панелі
    # Подія e11 на P1
    p.append(circle(110, 126, 5, fill=FIELD, stroke=INK, sw=1.2))
    # Подія e12 на P1 (відправка m1 ПІСЛЯ перерізу)
    p.append(circle(310, 126, 5, fill=NEG, stroke=INK, sw=1.2))
    p.append(text(310, 114, "send(m1)", size=10, color=NEG, bold=True))

    # Подія e21 на P2 (отримання m1 ДО перерізу)
    p.append(circle(200, 206, 5, fill=NEG, stroke=INK, sw=1.2))
    p.append(text(200, 194, "recv(m1)", size=10, color=NEG, bold=True))

    # Подія e31 на P3
    p.append(circle(140, 286, 5, fill=FIELD, stroke=INK, sw=1.2))

    # Повідомлення m1 (йде з майбутнього в минуле перерізу!)
    p.append(arrow(310, 126, 200, 206, color=NEG, sw=2))

    # Лінія неузгодженого перерізу Cut A
    p.append(line(240, 100, 260, 170, color=NEG, sw=2.5))
    p.append(line(260, 170, 240, 250, color=NEG, sw=2.5))
    p.append(line(240, 250, 270, 320, color=NEG, sw=2.5))
    p.append(text(255, 335, "Переріз A (хибний)", size=11, color=NEG, bold=True))

    p.append(fitbox(30, 350, 430, 85,
                    "Порушення причинності (наслідок без причини):\n"
                    "Подія recv(m1) потрапила у знімок на P2, але подія send(m1)\n"
                    "на P1 лишилася в майбутньому за межами перерізу.\n"
                    "Система зафіксувала отримання повідомлення-привида.",
                    size=11, fill="#fef8f6", stroke=NEG, color=INK))

    # Права панель: Узгоджений переріз
    p.append(rect(490, 50, 450, 400, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(fitbox(500, 60, 430, 36, "Узгоджений переріз (Consistent Cut)", size=13, fill="#f2f8f4", stroke=POS, color=POS, bold=True))

    # Лінії трьох процесів для правої панелі
    p.append(text(505, 130, "P1", size=12, bold=True, color=INK, anchor="start"))
    p.append(line(530, 126, 920, 126, color=LINE, sw=1.8))

    p.append(text(505, 210, "P2", size=12, bold=True, color=INK, anchor="start"))
    p.append(line(530, 206, 920, 206, color=LINE, sw=1.8))

    p.append(text(505, 290, "P3", size=12, bold=True, color=INK, anchor="start"))
    p.append(line(530, 286, 920, 286, color=LINE, sw=1.8))

    # Події правої панелі
    # Подія e11 на P1 (відправка m2 ДО перерізу)
    p.append(circle(580, 126, 5, fill=POS, stroke=INK, sw=1.2))
    p.append(text(580, 114, "send(m2)", size=10, color=POS, bold=True))

    # Подія e21 на P2 (отримання m2 ПІСЛЯ перерізу — транзитне повідомлення)
    p.append(circle(840, 206, 5, fill=FIELD, stroke=INK, sw=1.2))
    p.append(text(840, 194, "recv(m2)", size=10, color=FIELD, bold=True))

    # Подія e31 на P3
    p.append(circle(620, 286, 5, fill=FIELD, stroke=INK, sw=1.2))

    # Повідомлення m2 (перетинає лінію перерізу зліва направо — в каналі)
    p.append(arrow(580, 126, 840, 206, color=POS, sw=2))
    b_msg, _, _ = textbox(770, 140, "m2 у каналі C₁₂", size=10.5, pad=4, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_msg)

    # Лінія узгодженого перерізу Cut B
    p.append(line(660, 100, 690, 170, color=POS, sw=2.5))
    p.append(line(690, 170, 660, 250, color=POS, sw=2.5))
    p.append(line(660, 250, 690, 320, color=POS, sw=2.5))
    p.append(text(675, 335, "Переріз B (узгоджений)", size=11, color=POS, bold=True))

    p.append(fitbox(500, 350, 430, 85,
                    "Причинна замкненість (Causal Consistency):\n"
                    "Для кожної події в перерізі всі її причини також у перерізі.\n"
                    "Повідомлення m2 відправлене до перерізу, а отримане після нього,\n"
                    "тому m2 фіксується у стані каналу зв'язку C₁₂.",
                    size=11, fill="#f4faf6", stroke=POS, color=INK))

    render(os.path.join(OUT, "consistent-vs-inconsistent-cut.svg"), W, H, *p,
           title="Узгоджений та неузгоджений перерізи розподіленої системи")


# ── Фігура 2: Поширення маркерів Чанді-Лампорта (Marker Flow)
def fig_chandy_lamport_marker_flow():
    W, H = 960, 420
    p = []

    p.append(text(480, 26, "Алгоритм Чанді-Лампорта: поширення маркерів та фіксація станів", size=16, bold=True))

    # Три фази / кроки
    step_w = 295
    steps_x = [20, 330, 640]
    titles = [
        "1. Ініціація на вузлі P1",
        "2. Отримання на вузлі P2",
        "3. Завершення знімка"
    ]

    for i, (sx, stitle) in enumerate(zip(steps_x, titles)):
        p.append(rect(sx, 50, step_w, 350, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=6))
        p.append(fitbox(sx + 10, 60, step_w - 20, 32, stitle, size=12, fill="#f6f8fa", stroke="#d0d7de", color=INK, bold=True))

    # Крок 1
    p.append(circle(70, 150, 22, fill="#e1f5fe", stroke=FIELD, sw=2))
    p.append(text(70, 155, "P1", size=13, bold=True, color=FIELD))
    p.append(text(70, 190, "Стан P1 збережено", size=10.5, color=FIELD, bold=True))

    p.append(circle(250, 150, 22, fill="#ffffff", stroke=MUTED, sw=1.5))
    p.append(text(250, 155, "P2", size=13, bold=True, color=MUTED))

    p.append(circle(160, 270, 22, fill="#ffffff", stroke=MUTED, sw=1.5))
    p.append(text(160, 275, "P3", size=13, bold=True, color=MUTED))

    # P1 висилає маркери
    p.append(arrow(92, 150, 228, 150, color=POS, sw=2))
    b_m1, _, _ = textbox(160, 135, "Маркер M", size=10, pad=3, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_m1)

    p.append(arrow(85, 168, 145, 252, color=POS, sw=2))
    b_m2, _, _ = textbox(105, 220, "M", size=10, pad=3, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_m2)

    p.append(fitbox(30, 305, step_w - 20, 85,
                    "• P1 фіксує власний локальний стан.\n"
                    "• P1 надсилає Маркер M в усі\n"
                    "  вихідні канали (C₁₂, C₁₃).\n"
                    "• P1 починає запис вхідних каналів.",
                    size=10.5, fill="#fbfdff", stroke=FIELD, color=INK))

    # Крок 2
    p.append(circle(380, 150, 22, fill="#e1f5fe", stroke=FIELD, sw=2))
    p.append(text(380, 155, "P1", size=13, bold=True, color=FIELD))

    p.append(circle(560, 150, 22, fill="#e1f5fe", stroke=FIELD, sw=2))
    p.append(text(560, 155, "P2", size=13, bold=True, color=FIELD))
    p.append(text(560, 190, "Стан P2 збережено", size=10.5, color=FIELD, bold=True))

    p.append(circle(470, 270, 22, fill="#ffffff", stroke=MUTED, sw=1.5))
    p.append(text(470, 275, "P3", size=13, bold=True, color=MUTED))

    # Маркер прийшов на P2
    p.append(line(402, 150, 538, 150, color=LINE, sw=1.5, dash="3,3"))
    b_done, _, _ = textbox(470, 135, "C₁₂: стан = ∅", size=10, pad=3, fill="#f6f8fa", stroke=MUTED, color=MUTED)
    p.append(b_done)

    # P2 транслює маркери далі
    p.append(arrow(550, 168, 485, 252, color=POS, sw=2))
    b_m3, _, _ = textbox(530, 220, "Маркер M", size=10, pad=3, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_m3)

    p.append(fitbox(340, 305, step_w - 20, 85,
                    "• P2 вперше отримав M від P1.\n"
                    "• P2 фіксує свій локальний стан.\n"
                    "• Стан каналу C₁₂ фіксується як ∅.\n"
                    "• P2 ретранслює M у всі свої канали.",
                    size=10.5, fill="#fbfdff", stroke=FIELD, color=INK))

    # Крок 3
    p.append(circle(690, 150, 22, fill="#e8f5e9", stroke=POS, sw=2))
    p.append(text(690, 155, "P1", size=13, bold=True, color=POS))

    p.append(circle(870, 150, 22, fill="#e8f5e9", stroke=POS, sw=2))
    p.append(text(870, 155, "P2", size=13, bold=True, color=POS))

    p.append(circle(780, 270, 22, fill="#e8f5e9", stroke=POS, sw=2))
    p.append(text(780, 275, "P3", size=13, bold=True, color=POS))

    # Усі маркери повернулися
    p.append(line(712, 150, 848, 150, color=POS, sw=1.5))
    p.append(line(705, 168, 765, 252, color=POS, sw=1.5))
    p.append(line(855, 168, 795, 252, color=POS, sw=1.5))

    b_ok, _, _ = textbox(780, 195, "Глобальний знімок готовий", size=10.5, pad=4, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_ok)

    p.append(fitbox(650, 305, step_w - 20, 85,
                    "• Усі вузли зберегли локальні стани.\n"
                    "• Кожен вузол отримав M з усіх\n"
                    "  своїх вхідних каналів.\n"
                    "• Знімок завершено без блокування!",
                    size=10.5, fill="#f4faf6", stroke=POS, color=INK))

    render(os.path.join(OUT, "chandy-lamport-marker-flow.svg"), W, H, *p,
           title="Поширення маркерів та фіксація станів каналів за алгоритмом Чанді-Лампорта")


# ── Фігура 3: Фіксація стану FIFO-каналу в польоті (Channel In-Flight State)
def fig_channel_state_recording():
    W, H = 960, 420
    p = []

    p.append(text(480, 26, "Фіксація транзитних повідомлень у FIFO-каналі", size=16, bold=True))

    # Панель часової шкали
    p.append(rect(20, 50, 920, 350, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Лінії процесів відправника та отримувача
    p.append(text(40, 110, "Вузол A (відправник):", size=12.5, bold=True, color=INK, anchor="start"))
    p.append(line(40, 130, 900, 130, color=LINE, sw=2))

    p.append(text(40, 270, "Вузол B (отримувач):", size=12.5, bold=True, color=INK, anchor="start"))
    p.append(line(40, 290, 900, 290, color=LINE, sw=2))

    # Хронологія дій вузла A
    # Подія 1: Відправка msg1
    p.append(circle(120, 130, 5, fill=FIELD, stroke=INK, sw=1.2))
    p.append(text(120, 115, "send(msg1)", size=10.5, color=FIELD, bold=True))

    # Подія 2: Старт знімка на A + відправка Marker
    p.append(circle(260, 130, 6, fill=POS, stroke=INK, sw=1.5))
    b_snapA, _, _ = textbox(260, 95, "Знімок A + send(Marker)", size=11, pad=4, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_snapA)

    # Подія 3: Відправка msg2 (після маркера)
    p.append(circle(460, 130, 5, fill=MUTED, stroke=INK, sw=1.2))
    p.append(text(460, 115, "send(msg2)", size=10.5, color=MUTED))

    # Хронологія дій вузла B
    # Подія на B: Старт знімка на B раніше
    p.append(circle(160, 290, 6, fill=FIELD, stroke=INK, sw=1.5))
    b_snapB, _, _ = textbox(160, 325, "Знімок B (старт запису каналу C_AB)", size=11, pad=4, fill="#e1f5fe", stroke=FIELD, color=FIELD, bold=True)
    p.append(b_snapB)

    # Подія на B: Отримання msg1 (між знімком B і маркером від A)
    p.append(circle(360, 290, 5, fill=POS, stroke=INK, sw=1.2))
    p.append(text(360, 315, "recv(msg1)", size=10.5, color=POS, bold=True))

    # Подія на B: Отримання Marker від A (кінець запису каналу C_AB)
    p.append(circle(620, 290, 6, fill=POS, stroke=INK, sw=1.5))
    b_mrecv, _, _ = textbox(620, 325, "recv(Marker) — стоп запису C_AB", size=11, pad=4, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_mrecv)

    # Подія на B: Отримання msg2
    p.append(circle(780, 290, 5, fill=MUTED, stroke=INK, sw=1.2))
    p.append(text(780, 315, "recv(msg2)", size=10.5, color=MUTED))

    # Стрілки повідомлень
    # msg1: відправлено ДО маркера на A, отримано ПІСЛЯ знімка на B
    p.append(arrow(120, 130, 360, 290, color=POS, sw=2))
    b_tag1, _, _ = textbox(220, 200, "msg1 (у польоті під час знімка)", size=10.5, pad=3, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_tag1)

    # Marker від A до B
    p.append(arrow(260, 130, 620, 290, color=LINE, sw=2))
    b_tagM, _, _ = textbox(430, 215, "Маркер M (кордон між минулим і майбутнім)", size=10.5, pad=3, fill="#fff9db", stroke=LINE, color=INK, bold=True)
    p.append(b_tagM)

    # msg2: відправлено ПІСЛЯ маркера на A
    p.append(arrow(460, 130, 780, 290, color=MUTED, sw=1.8))
    b_tag2, _, _ = textbox(630, 200, "msg2 (після знімка)", size=10.5, pad=3, fill="#f6f8fa", stroke=MUTED, color=MUTED)
    p.append(b_tag2)

    # Зона запису каналу
    p.append(rect(160, 255, 460, 20, fill="#e8f5e9", stroke=POS, sw=1, rx=3))
    p.append(text(390, 269, "ІНТЕРВАЛ ЗАПИСУ КАНАЛУ C_AB: фіксується стан = { msg1 }", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "channel-state-in-flight.svg"), W, H, *p,
           title="Запис стану транзитних повідомлень у FIFO-каналі зв'язку")


# ── Фігура 4: Ґратка глобальних станів та досяжність (Lattice of Global States)
def fig_lattice_global_states():
    W, H = 960, 440
    p = []

    p.append(text(480, 26, "Ґратка узгоджених глобальних станів та траєкторія виконання", size=16, bold=True))

    # Фон
    p.append(rect(20, 50, 920, 370, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))

    # Вузли ґратки
    # Рівень 0 (Початковий стан)
    p.append(circle(120, 235, 24, fill="#f6f8fa", stroke=INK, sw=1.5))
    p.append(text(120, 240, "S₀₀", size=12, bold=True, color=INK))

    # Рівень 1
    p.append(circle(280, 140, 24, fill="#f6f8fa", stroke=INK, sw=1.5))
    p.append(text(280, 145, "S₁₀", size=12, bold=True, color=INK))

    p.append(circle(280, 330, 24, fill="#e1f5fe", stroke=FIELD, sw=2))
    p.append(text(280, 335, "S₀₁", size=12, bold=True, color=FIELD))

    # Рівень 2
    p.append(circle(480, 80, 24, fill="#f6f8fa", stroke=INK, sw=1.5))
    p.append(text(480, 85, "S₂₀", size=12, bold=True, color=INK))

    # Стан знімка S*
    p.append(circle(480, 235, 28, fill="#e8f5e9", stroke=POS, sw=2.5))
    p.append(text(480, 239, "S*", size=14, bold=True, color=POS))
    p.append(text(480, 275, "Знімок Чанді-Лампорта", size=10.5, color=POS, bold=True))

    p.append(circle(480, 380, 24, fill="#f6f8fa", stroke=INK, sw=1.5))
    p.append(text(480, 385, "S₀₂", size=12, bold=True, color=INK))

    # Рівень 3
    p.append(circle(680, 140, 24, fill="#e1f5fe", stroke=FIELD, sw=2))
    p.append(text(680, 145, "S₂₁", size=12, bold=True, color=FIELD))

    p.append(circle(680, 330, 24, fill="#f6f8fa", stroke=INK, sw=1.5))
    p.append(text(680, 335, "S₁₂", size=12, bold=True, color=INK))

    # Рівень 4 (Кінцевий стан)
    p.append(circle(840, 235, 24, fill="#f6f8fa", stroke=INK, sw=1.5))
    p.append(text(840, 240, "S₂₂", size=12, bold=True, color=INK))

    # Ребра ґратки (можливі переходи)
    # З S00
    p.append(arrow(142, 222, 258, 153, color=MUTED, sw=1.5))
    p.append(arrow(142, 248, 258, 317, color=FIELD, sw=2.2)) # Реальний шлях

    # З S10
    p.append(arrow(302, 131, 458, 89, color=MUTED, sw=1.5))
    p.append(arrow(302, 149, 455, 222, color=MUTED, sw=1.5))

    # З S01
    p.append(arrow(302, 321, 455, 248, color=POS, sw=2.5)) # Шлях до S*
    p.append(arrow(302, 338, 458, 372, color=MUTED, sw=1.5))

    # З S20
    p.append(arrow(502, 89, 658, 131, color=MUTED, sw=1.5))

    # З S* (S11)
    p.append(arrow(505, 222, 658, 149, color=POS, sw=2.5)) # Шлях від S*
    p.append(arrow(505, 248, 658, 321, color=MUTED, sw=1.5))

    # З S02
    p.append(arrow(502, 372, 658, 338, color=MUTED, sw=1.5))

    # До S22
    p.append(arrow(702, 153, 818, 222, color=FIELD, sw=2.2)) # Реальний шлях
    p.append(arrow(702, 317, 818, 248, color=MUTED, sw=1.5))

    # Позначення реального шляху виконання
    b_real, _, _ = textbox(240, 80, "Реальна траєкторія виконання: S₀₀ → S₀₁ → S₂₁ → S₂₂", size=11, pad=5, fill="#e1f5fe", stroke=FIELD, color=FIELD, bold=True)
    p.append(b_real)

    b_inv, _, _ = textbox(720, 80, "Інваріант досяжності: S_старт ⇝ S* ⇝ S_фінал", size=11, pad=5, fill="#e8f5e9", stroke=POS, color=POS, bold=True)
    p.append(b_inv)

    render(os.path.join(OUT, "lattice-global-states.svg"), W, H, *p,
           title="Ґратка глобальних станів та лінеаризовність знімка Чанді-Лампорта")


if __name__ == "__main__":
    fig_consistent_vs_inconsistent_cut()
    fig_chandy_lamport_marker_flow()
    fig_channel_state_recording()
    fig_lattice_global_states()
    print("All figures generated successfully.")
