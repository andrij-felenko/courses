# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_sticky_vs_stateless():
    """Порівняння: прив'язка до пам'яті (sticky) проти спільного сховища (stateless)."""
    W, H = 1000, 480
    frags = []
    frags.append(text(W / 2, 28, "Сесійна прив'язка (stateful) проти бездержавного пулу (stateless)",
                      size=16, bold=True))

    # ── Ліва частина: Stateful / Sticky Sessions
    frags.append(rect(20, 55, 465, 385, fill="#fdfaf6", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(252, 82, "Прив'язка до вузла (Sticky Sessions)", size=14, bold=True, color="#92400e"))
    frags.append(text(252, 102, "стан замкнено в пам'яті конкретного процесу", size=11, color=MUTED))

    # Клієнти ліворуч
    c1, _, _ = textbox(80, 155, "Клієнт 1\n(Сесія A)", size=11, min_w=95, fill=BG, stroke=LINE)
    c2, _, _ = textbox(80, 245, "Клієнт 2\n(Сесія B)", size=11, min_w=95, fill=BG, stroke=LINE)
    c3, _, _ = textbox(80, 335, "Клієнт 3\n(Сесія C)", size=11, min_w=95, fill=BG, stroke=LINE)
    frags += [c1, c2, c3]

    # Балансувальник
    lb1, _, _ = textbox(215, 245, "Балансувальник\nL7 (Affinity Cookie\nабо IP-Hash)", size=11, min_w=125, fill="#fef3c7", stroke="#d97706")
    frags.append(lb1)

    # Стрілки клієнт -> LB
    frags.append(arrow(135, 155, 160, 220, color=LINE, sw=1.5))
    frags.append(arrow(135, 245, 150, 245, color=LINE, sw=1.5))
    frags.append(arrow(135, 335, 160, 270, color=LINE, sw=1.5))

    # Вузли
    n1, _, _ = textbox(390, 160, "Вузол 1 (Crash ✖)\nПам'ять: [Сесія A, B]", size=11, min_w=145, fill="#fee2e2", stroke=POS)
    n2, _, _ = textbox(390, 310, "Вузол 2 (Idle)\nПам'ять: [Сесія C]", size=11, min_w=145, fill=BG, stroke=LINE)
    frags += [n1, n2]

    # Стрілки LB -> Вузли
    frags.append(arrow(280, 225, 315, 175, color=POS, sw=1.8))
    frags.append(arrow(280, 265, 315, 305, color=FIELD, sw=1.8))

    frags.append(text(252, 400, "Падіння Вузла 1 знищує сесії A і B безповоротно", size=11, color=POS, bold=True))
    frags.append(text(252, 422, "Нерівномірний перекіс навантаження між вузлами", size=10, color=MUTED))

    # ── Права частина: Stateless + External Shared Store
    frags.append(rect(515, 55, 465, 385, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(747, 82, "Бездержавний пул (Stateless Architecture)", size=14, bold=True, color="#166534"))
    frags.append(text(747, 102, "будь-який запит обробляється будь-яким вузлом", size=11, color=MUTED))

    # Клієнти праворуч
    kc1, _, _ = textbox(575, 155, "Клієнт 1\n(sid=a8f3)", size=11, min_w=90, fill=BG, stroke=LINE)
    kc2, _, _ = textbox(575, 245, "Клієнт 2\n(sid=b71c)", size=11, min_w=90, fill=BG, stroke=LINE)
    kc3, _, _ = textbox(575, 335, "Клієнт 3\n(sid=5d90)", size=11, min_w=90, fill=BG, stroke=LINE)
    frags += [kc1, kc2, kc3]

    # Балансувальник Round-Robin
    lb2, _, _ = textbox(695, 245, "Балансувальник\n(Round-Robin /\nLeast-Conn)", size=11, min_w=115, fill="#dcfce7", stroke=FIELD)
    frags.append(lb2)

    # Стрілки клієнт -> LB
    frags.append(arrow(625, 155, 645, 220, color=LINE, sw=1.5))
    frags.append(arrow(625, 245, 635, 245, color=LINE, sw=1.5))
    frags.append(arrow(625, 335, 645, 270, color=LINE, sw=1.5))

    # Бездержавні воркери
    w1, _, _ = textbox(815, 155, "Воркер 1\n(Без стану)", size=10, min_w=85, fill=BG, stroke=LINE)
    w2, _, _ = textbox(815, 245, "Воркер 2\n(Без стану)", size=10, min_w=85, fill=BG, stroke=LINE)
    w3, _, _ = textbox(815, 335, "Воркер 3\n(Без стану)", size=10, min_w=85, fill=BG, stroke=LINE)
    frags += [w1, w2, w3]

    # Стрілки LB -> Воркери
    frags.append(arrow(755, 225, 770, 175, color=FIELD, sw=1.5))
    frags.append(arrow(755, 245, 770, 245, color=FIELD, sw=1.5))
    frags.append(arrow(755, 265, 770, 315, color=FIELD, sw=1.5))

    # Спільне сховище (Redis / DB)
    store, _, _ = textbox(930, 245, "Спільне\nсховище\n(Redis / DB)\n[a8f3...]\n[b71c...]\n[5d90...]", size=9, min_w=80, fill="#e0e7ff", stroke=NEG)
    frags.append(store)

    # Стрілки воркери <-> сховище
    frags.append(arrow(860, 165, 890, 215, color=NEG, sw=1.5))
    frags.append(arrow(860, 245, 888, 245, color=NEG, sw=1.5))
    frags.append(arrow(860, 325, 890, 275, color=NEG, sw=1.5))

    frags.append(text(747, 400, "Падіння будь-якого воркера непомітне: стан збережено", size=11, color=FIELD, bold=True))
    frags.append(text(747, 422, "Ідеальне масштабування: додавання воркерів лінійне", size=10, color=MUTED))

    render(os.path.join(IMG, "sticky-vs-stateless.svg"), W, H, *frags)


def fig_concurrency_race():
    """Гонка паралельних запитів: втрачене оновлення проти оптимістичного блокування з версією."""
    W, H = 960, 430
    frags = []
    frags.append(text(W / 2, 26, "Гонка паралельних запитів: колізія запису та її вирішення версіонуванням",
                      size=16, bold=True))

    # ── Ліворуч: Неконтрольований перезапис (Lost Update)
    frags.append(rect(20, 52, 445, 345, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(242, 78, "Аномалія «останній запис перемагає» (Lost Update)", size=13, bold=True, color=POS))

    # Вісь часу
    frags.append(arrow(60, 105, 60, 350, color=MUTED, sw=1.5))
    frags.append(text(60, 368, "час", size=10, color=MUTED))

    # Запит 1 і Запит 2
    r1, _, _ = textbox(165, 120, "Запит 1: читає кошик [A]\n(t = 0 мс)", size=10, min_w=150, fill=BG, stroke=LINE)
    r2, _, _ = textbox(340, 145, "Запит 2: читає кошик [A]\n(t = 5 мс)", size=10, min_w=150, fill=BG, stroke=LINE)
    w1, _, _ = textbox(165, 230, "Запит 1: додає B\nпише [A, B] (t = 20 мс)", size=10, min_w=150, fill="#eafaf1", stroke=FIELD)
    w2, _, _ = textbox(340, 290, "Запит 2: додає C\nпише [A, C] (t = 30 мс)", size=10, min_w=150, fill="#fee2e2", stroke=POS)
    frags += [r1, r2, w1, w2]

    frags.append(arrow(165, 150, 165, 205, color=MUTED, sw=1.2))
    frags.append(arrow(340, 175, 340, 265, color=MUTED, sw=1.2))

    frags.append(text(242, 350, "Товар B безповоротно втрачено!", size=12, bold=True, color=POS))
    frags.append(text(242, 372, "Запит 2 сліпо затер результат Запиту 1", size=10, color=MUTED))

    # ── Праворуч: Оптимістичне блокування з версією (CAS)
    frags.append(rect(495, 52, 445, 345, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(717, 78, "Захист через оптимістичну версію (Compare-And-Swap)", size=13, bold=True, color="#166534"))

    # Вісь часу
    frags.append(arrow(535, 105, 535, 350, color=MUTED, sw=1.5))
    frags.append(text(535, 368, "час", size=10, color=MUTED))

    # Запит 1 і Запит 2 з версіями
    vr1, _, _ = textbox(640, 120, "Запит 1: читає кошик [A]\nверсія = 1", size=10, min_w=150, fill=BG, stroke=LINE)
    vr2, _, _ = textbox(815, 145, "Запит 2: читає кошик [A]\nверсія = 1", size=10, min_w=150, fill=BG, stroke=LINE)
    vw1, _, _ = textbox(640, 230, "Запит 1: CAS(v1 → v2)\nУСПІХ: записано [A, B]", size=10, min_w=150, fill="#eafaf1", stroke=FIELD)
    vw2, _, _ = textbox(815, 290, "Запит 2: CAS(v1 → v2)\nКОНФЛІКТ 409: версія вже 2!", size=10, min_w=155, fill="#fee2e2", stroke=POS)
    frags += [vr1, vr2, vw1, vw2]

    frags.append(arrow(640, 150, 640, 205, color=MUTED, sw=1.2))
    frags.append(arrow(815, 175, 815, 265, color=MUTED, sw=1.2))

    frags.append(text(717, 350, "Колізію спіймано: повторне читання збереже обидва товари", size=11, bold=True, color=FIELD))
    frags.append(text(717, 372, "Запит 2 перечитує версію 2 й записує [A, B, C] як версію 3", size=10, color=MUTED))

    render(os.path.join(IMG, "concurrency-race.svg"), W, H, *frags)


def fig_graceful_drain():
    """Штатне оновлення та виведення вузла: блокування прив'язкою проти миттєвого дренажу."""
    W, H = 940, 390
    frags = []
    frags.append(text(W / 2, 26, "Штатне виведення вузла (Drain): сесійна прив'язка проти бездержавності",
                      size=16, bold=True))

    # ── Верхній блок: Stateful / Sticky Sessions
    frags.append(rect(20, 52, 900, 145, fill="#fdfaf6", stroke="#d97706", sw=1.5, rx=8))
    frags.append(text(160, 75, "Вузол із сесіями в пам'яті (Stateful):", size=12, bold=True, color="#92400e"))

    # Часова шкала дренажу stateful
    frags.append(arrow(290, 75, 880, 75, color=LINE, sw=1.5))
    frags.append(circle(320, 75, 6, fill=POS, stroke=POS, sw=1))
    frags.append(text(320, 95, "SIGTERM", size=10, bold=True, color=POS))

    sb1, _, _ = textbox(520, 130, "Очікування згасання сесій (Session Drain Time)\nТривалість: від 30 хвилин до кількох годин!", size=10, min_w=340, fill="#fef3c7", stroke="#d97706")
    frags.append(sb1)

    frags.append(circle(750, 75, 6, fill="#d97706", stroke="#d97706", sw=1))
    frags.append(text(750, 95, "Зупинка", size=10, color=MUTED))
    frags.append(text(850, 130, "Деплой паралізовано", size=11, bold=True, color=POS))

    # ── Нижній блок: Stateless
    frags.append(rect(20, 215, 900, 145, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(160, 238, "Бездержавний воркер (Stateless):", size=12, bold=True, color="#166534"))

    # Часова шкала дренажу stateless
    frags.append(arrow(290, 238, 880, 238, color=LINE, sw=1.5))
    frags.append(circle(320, 238, 6, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(320, 258, "SIGTERM", size=10, bold=True, color=FIELD))

    sb2, _, _ = textbox(420, 295, "Завершення активних HTTP-запитів\nТривалість: 2–5 секунд", size=10, min_w=200, fill="#dcfce7", stroke=FIELD)
    frags.append(sb2)

    frags.append(circle(530, 238, 6, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(530, 258, "Повна зупинка", size=10, color=FIELD))

    frags.append(text(730, 295, "Нові запити миттєво підхоплюють сусідні вузли", size=11, bold=True, color=FIELD))
    frags.append(text(730, 315, "Безперервний деплой (Zero-Downtime Rolling Update)", size=10, color=MUTED))

    render(os.path.join(IMG, "graceful-drain.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_sticky_vs_stateless()
    fig_concurrency_race()
    fig_graceful_drain()
    print("All figures generated successfully.")
