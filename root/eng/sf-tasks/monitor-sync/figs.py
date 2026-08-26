# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

C_MUTEX  = "#c0392b"    # замок / м'ютекс (червоний)
C_THREAD = "#2457d6"    # потік (синій)
C_STATE  = "#27ae60"    # стан даних (зелений)
C_COND   = "#8e44ad"    # умовна змінна (фіолетовий)
C_QUEUE  = "#d35400"    # черга (помаранчевий)
C_BG_BOX = "#f8f9fa"


# ── Фігура 1: Архітектура монітора ──────────────────────────────────────────
def fig_monitor_architecture():
    W, H = 840, 480
    frags = []

    frags.append(text(W / 2, 28, "Архітектура монітора: м'ютекс, спільний стан та умовні змінні", size=15, bold=True))

    # Вхідна черга потоків до м'ютексу (зліва)
    frags.append(rect(20, 140, 150, 220, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=8))
    frags.append(text(95, 165, "Вхідна черга", size=13, bold=True, color=INK))
    frags.append(text(95, 185, "(чекають на м'ютекс)", size=10, color=MUTED))

    # Потоки у вхідній черзі
    frags.append(rect(30, 205, 130, 34, fill="#ebf3fd", stroke=C_THREAD, sw=1.5, rx=6))
    frags.append(text(95, 226, "Потік T₃", size=11, bold=True, color=C_THREAD))

    frags.append(rect(30, 248, 130, 34, fill="#ebf3fd", stroke=C_THREAD, sw=1.5, rx=6))
    frags.append(text(95, 269, "Потік T₄", size=11, bold=True, color=C_THREAD))

    frags.append(rect(30, 291, 130, 34, fill="#ebf3fd", stroke=C_THREAD, sw=1.5, rx=6))
    frags.append(text(95, 312, "Потік T₅", size=11, bold=True, color=C_THREAD))

    # Стрілка від вхідної черги до замка
    frags.append(arrow(170, 250, 188, 250, color=MUTED, sw=1.5))

    # Ворота замка (М'ютекс) між чергою і монітором
    frags.append(rect(190, 220, 55, 60, fill="#fdedec", stroke=C_MUTEX, sw=2, rx=6))
    frags.append(text(217, 245, "Замок", size=11, bold=True, color=C_MUTEX))
    frags.append(text(217, 263, "Mutex", size=10, color=C_MUTEX))

    # Стрілка від замка в монітор
    frags.append(arrow(245, 250, 265, 250, color=C_MUTEX, sw=2))

    # Зовнішня межа монітора (захищена область)
    frags.append(rect(265, 60, 555, 390, fill="#fdfefe", stroke=LINE, sw=2, rx=12))
    frags.append(text(542, 84, "Область монітора (взаємне виключення)", size=13, bold=True, color=LINE))

    # Активна зона монітора (потік всередині)
    frags.append(rect(285, 110, 225, 160, fill="#eaf2f8", stroke=C_THREAD, sw=2, rx=8))
    frags.append(text(397, 135, "Активна критична секція", size=12, bold=True, color=C_THREAD))
    frags.append(text(397, 155, "(максимум 1 потік)", size=10, color=MUTED))

    frags.append(rect(305, 175, 185, 42, fill="#ebf3fd", stroke=C_THREAD, sw=2, rx=6))
    frags.append(text(397, 201, "Потік T₁ (виконується)", size=11, bold=True, color=C_THREAD))

    frags.append(text(397, 245, "Викликає wait() / signal()", size=10, italic=True, color=LINE))

    # Спільний стан даних (внизу монітора)
    frags.append(rect(285, 295, 225, 135, fill="#eafaf1", stroke=C_STATE, sw=2, rx=8))
    frags.append(text(397, 320, "Спільний стан (Дані)", size=12, bold=True, color=C_STATE))
    frags.append(text(397, 345, "• Буфер завдань: queue", size=11, color=INK))
    frags.append(text(397, 368, "• Лічильник: count = 0", size=11, color=INK))
    frags.append(text(397, 391, "• Прапорець: shutdown = false", size=11, color=INK))
    frags.append(text(397, 414, "Захищений м'ютексом", size=10, italic=True, color=MUTED))

    # Черга умовної змінної 1: not_empty
    frags.append(rect(540, 110, 255, 150, fill="#f4ecf7", stroke=C_COND, sw=2, rx=8))
    frags.append(text(667, 135, "Умовна змінна: not_empty", size=12, bold=True, color=C_COND))
    frags.append(text(667, 155, "Черга сплячих споживачів", size=10, color=MUTED))

    frags.append(rect(560, 172, 215, 32, fill="#ffffff", stroke=C_COND, sw=1.5, rx=5))
    frags.append(text(667, 192, "Потік T₂ (чекає count > 0)", size=10, color=C_COND))

    frags.append(rect(560, 212, 215, 32, fill="#ffffff", stroke=C_COND, sw=1.5, rx=5))
    frags.append(text(667, 232, "Потік T₆ (чекає count > 0)", size=10, color=C_COND))

    # Черга умовної змінної 2: not_full
    frags.append(rect(540, 280, 255, 150, fill="#fef5e7", stroke=C_QUEUE, sw=2, rx=8))
    frags.append(text(667, 305, "Умовна змінна: not_full", size=12, bold=True, color=C_QUEUE))
    frags.append(text(667, 325, "Черга сплячих виробників", size=10, color=MUTED))

    frags.append(rect(560, 345, 215, 32, fill="#ffffff", stroke=C_QUEUE, sw=1.5, rx=5))
    frags.append(text(667, 365, "Потік T₇ (чекає count < N)", size=10, color=C_QUEUE))

    frags.append(text(667, 405, "[порожньо — місця вистачає]", size=10, italic=True, color=MUTED))

    # Стрілки взаємодії між зоною виконання та CV
    frags.append(arrow(510, 175, 540, 160, color=C_COND, sw=2))
    frags.append(text(525, 155, "wait()", size=9, bold=True, color=C_COND))

    frags.append(arrow(510, 215, 540, 225, color=FIELD, sw=2))
    frags.append(text(525, 240, "signal()", size=9, bold=True, color=FIELD))

    render(os.path.join(OUT, 'monitor-architecture.svg'), W, H, *frags)


# ── Фігура 2: Життєвий цикл cond_wait ───────────────────────────────────────
def fig_cond_wait_lifecycle():
    W, H = 820, 360
    frags = []

    frags.append(text(W / 2, 26, "Життєвий цикл виклику wait: атомарний перехід, сон і повторний замок", size=15, bold=True))

    step_w = 175
    step_h = 240
    y_top = 65

    # Крок 1: Перевірка предикату
    x1 = 30
    frags.append(rect(x1, y_top, step_w, step_h, fill="#ebf3fd", stroke=C_THREAD, sw=2, rx=8))
    frags.append(text(x1 + step_w / 2, y_top + 26, "Крок 1: Запит", size=13, bold=True, color=C_THREAD))
    frags.append(rect(x1 + 15, y_top + 45, step_w - 30, 48, fill="#ffffff", stroke=C_MUTEX, sw=1.5, rx=5))
    frags.append(text(x1 + step_w / 2, y_top + 65, "М'ютекс: УТРИМУЄТЬСЯ", size=10, bold=True, color=C_MUTEX))
    frags.append(text(x1 + step_w / 2, y_top + 82, "Потік у критичній секції", size=9, color=MUTED))
    frags.append(text(x1 + step_w / 2, y_top + 120, "Предикат хибний:", size=11, bold=True, color=INK))
    frags.append(text(x1 + step_w / 2, y_top + 140, "queue.empty() == true", size=10, color=POS))
    frags.append(text(x1 + step_w / 2, y_top + 175, "Виклик:", size=10, color=MUTED))
    frags.append(text(x1 + step_w / 2, y_top + 195, "cond_wait(&c, &m)", size=11, bold=True, color=C_THREAD))

    # Стрілка 1 -> 2
    frags.append(arrow(x1 + step_w, y_top + step_h / 2, x1 + step_w + 25, y_top + step_h / 2, color=LINE, sw=2))

    # Крок 2: Атомарне відпускання й сон
    x2 = 230
    frags.append(rect(x2, y_top, step_w, step_h, fill="#f4ecf7", stroke=C_COND, sw=2, rx=8))
    frags.append(text(x2 + step_w / 2, y_top + 26, "Крок 2: Засинання", size=13, bold=True, color=C_COND))
    frags.append(rect(x2 + 15, y_top + 45, step_w - 30, 48, fill="#ffffff", stroke=FIELD, sw=1.5, rx=5))
    frags.append(text(x2 + step_w / 2, y_top + 65, "М'ютекс: ВІДПУЩЕНО", size=10, bold=True, color=FIELD))
    frags.append(text(x2 + step_w / 2, y_top + 82, "Атомарно з переходом у сон", size=9, color=MUTED))
    frags.append(text(x2 + step_w / 2, y_top + 120, "Потік у черзі CV:", size=11, bold=True, color=C_COND))
    frags.append(text(x2 + step_w / 2, y_top + 140, "Стан: BLOCKED (сон)", size=10, color=MUTED))
    frags.append(text(x2 + step_w / 2, y_top + 175, "CPU не витрачається", size=10, bold=True, color=FIELD))
    frags.append(text(x2 + step_w / 2, y_top + 195, "Чекає на сигнал у ядрі", size=10, color=MUTED))

    # Стрілка 2 -> 3
    frags.append(arrow(x2 + step_w, y_top + step_h / 2, x2 + step_w + 25, y_top + step_h / 2, color=LINE, sw=2))

    # Крок 3: Сигнал і змагання за м'ютекс
    x3 = 430
    frags.append(rect(x3, y_top, step_w, step_h, fill="#fef5e7", stroke=C_QUEUE, sw=2, rx=8))
    frags.append(text(x3 + step_w / 2, y_top + 26, "Крок 3: Сигнал", size=13, bold=True, color=C_QUEUE))
    frags.append(rect(x3 + 15, y_top + 45, step_w - 30, 48, fill="#ffffff", stroke=C_QUEUE, sw=1.5, rx=5))
    frags.append(text(x3 + step_w / 2, y_top + 65, "cond_signal(&c)", size=10, bold=True, color=C_QUEUE))
    frags.append(text(x3 + step_w / 2, y_top + 82, "Виробник додав дані", size=9, color=MUTED))
    frags.append(text(x3 + step_w / 2, y_top + 120, "Потік прокинувся,", size=11, bold=True, color=INK))
    frags.append(text(x3 + step_w / 2, y_top + 140, "але НЕ працює!", size=11, bold=True, color=POS))
    frags.append(text(x3 + step_w / 2, y_top + 175, "Чекає в черзі м'ютексу", size=10, color=MUTED))
    frags.append(text(x3 + step_w / 2, y_top + 195, "pthread_mutex_lock(&m)", size=10, bold=True, color=C_MUTEX))

    # Стрілка 3 -> 4
    frags.append(arrow(x3 + step_w, y_top + step_h / 2, x3 + step_w + 25, y_top + step_h / 2, color=LINE, sw=2))

    # Крок 4: Повернення з wait()
    x4 = 630
    frags.append(rect(x4, y_top, step_w, step_h, fill="#eafaf1", stroke=C_STATE, sw=2, rx=8))
    frags.append(text(x4 + step_w / 2, y_top + 26, "Крок 4: Вихід", size=13, bold=True, color=C_STATE))
    frags.append(rect(x4 + 15, y_top + 45, step_w - 30, 48, fill="#ffffff", stroke=C_MUTEX, sw=1.5, rx=5))
    frags.append(text(x4 + step_w / 2, y_top + 65, "М'ютекс: ЗНОВУ ЗАХОПЛЕНО", size=10, bold=True, color=C_MUTEX))
    frags.append(text(x4 + step_w / 2, y_top + 82, "wait() завершив роботу", size=9, color=MUTED))
    frags.append(text(x4 + step_w / 2, y_top + 120, "Обов'язкова дія:", size=11, bold=True, color=INK))
    frags.append(text(x4 + step_w / 2, y_top + 140, "Повторна перевірка while!", size=10, bold=True, color=POS))
    frags.append(text(x4 + step_w / 2, y_top + 175, "Якщо готова — забирає,", size=10, color=MUTED))
    frags.append(text(x4 + step_w / 2, y_top + 195, "якщо ні — знову wait()", size=10, color=MUTED))

    # Нижній висновок
    frags.append(rect(30, 318, 775, 30, fill="#fdfefe", stroke=MUTED, sw=1, rx=4))
    frags.append(text(417, 338, "Ключова гарантія: вихід із wait() відбувається ВИКЛЮЧНО з захопленим м'ютексом", size=11, bold=True, color=INK))

    render(os.path.join(OUT, 'cond-wait-lifecycle.svg'), W, H, *frags)


# ── Фігура 3: Hoare vs Mesa ──────────────────────────────────────────────────
def fig_hoare_vs_mesa():
    W, H = 820, 390
    frags = []

    frags.append(text(W / 2, 26, "Порівняння семантики сповіщення: Хоар (1974) проти Mesa (1980)", size=15, bold=True))

    panel_w = 370
    panel_h = 320
    y_top = 55

    # Ліва колонка: Семантика Хоара (Signal-and-Wait)
    x_h = 30
    frags.append(rect(x_h, y_top, panel_w, panel_h, fill="#fbfcfc", stroke=C_THREAD, sw=2, rx=8))
    frags.append(text(x_h + panel_w / 2, y_top + 26, "Семантика Хоара (Signal-and-Wait)", size=13, bold=True, color=C_THREAD))
    frags.append(text(x_h + panel_w / 2, y_top + 46, "Негайна передача замка і контексту", size=10, color=MUTED))

    # Послідовність Хоара
    frags.append(rect(x_h + 20, y_top + 65, panel_w - 40, 50, fill="#ebf3fd", stroke=C_THREAD, sw=1.5, rx=5))
    frags.append(text(x_h + panel_w / 2, y_top + 86, "1. Потік A кличе signal()", size=11, bold=True, color=C_THREAD))
    frags.append(text(x_h + panel_w / 2, y_top + 104, "Миттєво блокується і віддає замок", size=10, color=MUTED))

    frags.append(arrow(x_h + panel_w / 2, y_top + 115, x_h + panel_w / 2, y_top + 135, color=C_MUTEX, sw=2))

    frags.append(rect(x_h + 20, y_top + 135, panel_w - 40, 50, fill="#eafaf1", stroke=C_STATE, sw=1.5, rx=5))
    frags.append(text(x_h + panel_w / 2, y_top + 156, "2. Потік B негайно виконується", size=11, bold=True, color=C_STATE))
    frags.append(text(x_h + panel_w / 2, y_top + 174, "Предикат гарантовано істинний!", size=10, bold=True, color=FIELD))

    frags.append(arrow(x_h + panel_w / 2, y_top + 185, x_h + panel_w / 2, y_top + 205, color=C_THREAD, sw=2))

    frags.append(rect(x_h + 20, y_top + 205, panel_w - 40, 45, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=5))
    frags.append(text(x_h + panel_w / 2, y_top + 225, "3. Потік A відновлюється після B", size=10, color=INK))
    frags.append(text(x_h + panel_w / 2, y_top + 241, "Висока ціна перемикання контексту", size=9, color=MUTED))

    frags.append(rect(x_h + 20, y_top + 260, panel_w - 40, 45, fill="#ebf3fd", stroke=C_THREAD, sw=1, rx=5))
    frags.append(text(x_h + panel_w / 2, y_top + 280, "Достатньо перевірки: if (!ready)", size=11, bold=True, color=C_THREAD))
    frags.append(text(x_h + panel_w / 2, y_top + 296, "Жоден інший потік не вклиниться", size=9, color=MUTED))

    # Права колонка: Семантика Mesa (Signal-and-Continue)
    x_m = 420
    frags.append(rect(x_m, y_top, panel_w, panel_h, fill="#fbfcfc", stroke=C_MUTEX, sw=2, rx=8))
    frags.append(text(x_m + panel_w / 2, y_top + 26, "Семантика Mesa (Signal-and-Continue)", size=13, bold=True, color=C_MUTEX))
    frags.append(text(x_m + panel_w / 2, y_top + 46, "Стандарт POSIX, C++, Java, C#, Go", size=10, color=MUTED))

    # Послідовність Mesa
    frags.append(rect(x_m + 20, y_top + 65, panel_w - 40, 50, fill="#fdedec", stroke=C_MUTEX, sw=1.5, rx=5))
    frags.append(text(x_m + panel_w / 2, y_top + 86, "1. Потік A кличе signal()", size=11, bold=True, color=C_MUTEX))
    frags.append(text(x_m + panel_w / 2, y_top + 104, "НЕ віддає замок! Продовжує роботу", size=10, bold=True, color=POS))

    frags.append(arrow(x_m + panel_w / 2, y_top + 115, x_m + panel_w / 2, y_top + 135, color=LINE, sw=2))

    frags.append(rect(x_m + 20, y_top + 135, panel_w - 40, 50, fill="#fef5e7", stroke=C_QUEUE, sw=1.5, rx=5))
    frags.append(text(x_m + panel_w / 2, y_top + 156, "2. Потік B переходить у чергу замка", size=11, bold=True, color=C_QUEUE))
    frags.append(text(x_m + panel_w / 2, y_top + 174, "Вікно гонки: потік C може вкрасти дані!", size=10, bold=True, color=POS))

    frags.append(arrow(x_m + panel_w / 2, y_top + 185, x_m + panel_w / 2, y_top + 205, color=C_MUTEX, sw=2))

    frags.append(rect(x_m + 20, y_top + 205, panel_w - 40, 45, fill="#f4f6f8", stroke=MUTED, sw=1.5, rx=5))
    frags.append(text(x_m + panel_w / 2, y_top + 225, "3. Потік B захоплює замок пізніше", size=10, color=INK))
    frags.append(text(x_m + panel_w / 2, y_top + 241, "Ефективно: немає зайвих context switch", size=9, color=FIELD))

    frags.append(rect(x_m + 20, y_top + 260, panel_w - 40, 45, fill="#fdedec", stroke=POS, sw=1.5, rx=5))
    frags.append(text(x_m + panel_w / 2, y_top + 280, "ОБОВ'ЯЗКОВО: while (!ready) wait()", size=11, bold=True, color=POS))
    frags.append(text(x_m + panel_w / 2, y_top + 296, "Захист від перехоплення та хибних пробуджень", size=9, color=MUTED))

    render(os.path.join(OUT, 'hoare-vs-mesa.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_monitor_architecture()
    fig_cond_wait_lifecycle()
    fig_hoare_vs_mesa()
    print("Figures generated successfully in img/")
