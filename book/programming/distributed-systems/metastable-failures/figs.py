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


# ── Фігура 1: Фазовий простір та петля гістерезису метастабільної відмови ──────
def fig_hysteresis_curve():
    W, H = 960, 560
    frags = []

    # Заголовок
    frags.append(text(480, 30, "Фазовий перехід та петля гістерезису метастабільної відмови", size=16, bold=True))

    # Рамка графіка
    frags.append(rect(60, 60, 840, 470, fill="#ffffff", stroke="#e5e7eb", sw=1, rx=8))

    # Осі координат
    frags.append(line(120, 460, 850, 460, color=LINE, sw=2))  # X: Offered Load
    frags.append(line(120, 460, 120, 90, color=LINE, sw=2))   # Y: Goodput
    frags.append(arrow(120, 460, 860, 460, color=LINE, sw=2))
    frags.append(arrow(120, 460, 120, 80, color=LINE, sw=2))

    # Підписи осей
    frags.append(text(850, 490, "Зовнішній потік навантаження (L)", size=12, color=INK, anchor="end", bold=True))
    frags.append(text(110, 80, "Корисна продуктивність (Goodput)", size=12, color=INK, anchor="start", bold=True))

    # Рівень максимальної місткості
    frags.append(line(120, 160, 830, 160, color="#9ca3af", sw=1.5, dash="5,5"))
    frags.append(text(830, 150, "Номінальна місткість системи (C_max)", size=11, color=MUTED, anchor="end"))

    # Позначки на осі X (короткі вертикальні пунктири до кривих)
    # L_rec
    frags.append(line(260, 460, 260, 468, color=LINE, sw=1.5))
    frags.append(text(260, 485, "L_rec", size=12, bold=True, color=FIELD))
    frags.append(text(260, 502, "(поріг відновлення)", size=10, color=FIELD))
    frags.append(line(260, 460, 260, 440, color="#d1d5db", sw=1, dash="3,3"))

    # L_nominal
    frags.append(line(520, 460, 520, 468, color=LINE, sw=1.5))
    frags.append(text(520, 485, "L_nominal", size=12, bold=True, color=INK))
    frags.append(text(520, 502, "(штатний трафік)", size=10, color=MUTED))

    # L_crit
    frags.append(line(720, 460, 720, 468, color=LINE, sw=1.5))
    frags.append(text(720, 485, "L_crit", size=12, bold=True, color=POS))
    frags.append(text(720, 502, "(точка зриву/тригер)", size=10, color=POS))
    frags.append(line(720, 460, 720, 200, color="#d1d5db", sw=1, dash="3,3"))

    # 1. Нижня/стабільна гілка: від 0 до L_crit
    frags.append(path("M 120 460 L 420 160 L 680 160 Q 710 160 720 180", stroke=FIELD, sw=3.5, fill="none"))
    frags.append(text(400, 135, "Стабільна робоча гілка (Goodput = L)", size=12, bold=True, color=FIELD))

    # 2. Зрив у метастабільний колапс (перехід від L_crit до дна)
    frags.append(path("M 720 180 Q 730 260 735 440", stroke=POS, sw=3, fill="none", dash="5,3"))
    frags.append(arrow(725, 230, 735, 340, color=POS, sw=2.5))
    frags.append(text(750, 280, "Зрив у колапс", size=12, bold=True, color=POS, anchor="start"))
    frags.append(text(750, 298, "(активація петлі повторів)", size=10, color=POS, anchor="start"))

    # 3. Верхня/метастабільна гілка відмови: від L_crit вліво до L_rec на нульовому Goodput
    frags.append(path("M 735 440 L 260 440", stroke=POS, sw=3.5, fill="none"))
    frags.append(arrow(600, 440, 420, 440, color=POS, sw=2.5))
    frags.append(text(490, 420, "Метастабільна гілка відмови (Goodput ≈ 0, CPU 100%)", size=12, bold=True, color=POS))

    # 4. Вихід з метастабільного стану (скидання навантаження нижче L_rec)
    frags.append(path("M 260 440 Q 255 350 260 280 L 260 280", stroke=FIELD, sw=2.5, fill="none", dash="5,3"))
    frags.append(arrow(260, 390, 260, 270, color=FIELD, sw=2.5))
    frags.append(text(145, 330, "Відновлення", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(text(145, 346, "(дроп до L &lt; L_rec)", size=10, color=FIELD, anchor="start"))

    # Інформаційний блок: Пастка відновлення
    b_txt = ("ПАСТКА ГІСТЕРЕЗИСУ:\n"
             "При поверненні навантаження з L_crit до L_nominal\n"
             "система НЕ повертається на робочу гілку!\n"
             "Вона застрягає в точці краху (Goodput ≈ 0),\n"
             "доки трафік не зріжуть нижче порогу L_rec.")
    tbox, tw, th = textbox(520, 290, b_txt, size=11, pad=10, fill="#fef2f2", stroke=POS, sw=1.5, color="#991b1b")
    frags.append(tbox)

    render(os.path.join(IMG, "hysteresis-curve.svg"), W, H, *frags)


# ── Фігура 2: Петля позитивного зворотного зв'язку ─────────────────────────────
def fig_positive_feedback_loop():
    W, H = 960, 580
    frags = []

    frags.append(text(480, 28, "Петлі самопідсилення навантаження (Positive Feedback Loops)", size=16, bold=True))

    # Центральний вузол: Затримка черги / Деградація
    c_box = rect(360, 220, 240, 90, fill="#fef2f2", stroke=POS, sw=2.5, rx=8)
    c_txt = mtext(480, 250, ["ДЕГРАДАЦІЯ СЕРВІСУ", "Час у черзі > Дедлайн клієнта", "CPU 100%, Пам'ять вичерпано"], size=12, bold=True, color=POS)
    frags.append(c_box + c_txt)

    # Тригер (зовнішній вхід)
    trig_box = rect(40, 225, 200, 80, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=8)
    trig_txt = mtext(140, 252, ["КОРОТКОЧАСНИЙ ТРИГЕР", "• Сплеск трафіку ΔL", "• Рестарт кешу / GC пауза", "• Тимчасовий збій БД (2 с)"], size=10, bold=False, color="#92400e")
    frags.append(trig_box + trig_txt)
    frags.append(arrow(240, 265, 355, 265, color="#d97706", sw=2))
    frags.append(text(298, 255, "Ініціація", size=10, bold=True, color="#d97706"))

    # Петля 1: Шторм клієнтських повторів (Вгорі)
    p1_box = rect(360, 60, 240, 85, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    p1_txt = mtext(480, 88, ["1. ШТОРМ ПОВТОРІВ (RETRIES)", "Клієнт рве з'єднання за таймаутом", "та шле 2-3 повторні запити"], size=11, bold=False, color=INK)
    frags.append(p1_box + p1_txt)

    # Стрілки петлі 1
    frags.append(path("M 530 220 C 560 180 560 160 530 145", stroke=POS, sw=2, fill="none"))
    frags.append(arrow(535, 155, 500, 145, color=POS, sw=2))
    frags.append(text(585, 185, "Таймаут", size=10, bold=True, color=POS, anchor="start"))

    frags.append(path("M 430 145 C 400 160 400 180 430 220", stroke=POS, sw=2, fill="none"))
    frags.append(arrow(425, 195, 440, 218, color=POS, sw=2))
    frags.append(text(375, 185, "Вхідний потік ×3", size=10, bold=True, color=POS, anchor="end"))

    # Петля 2: Вимивання кешу та перевантаження БД (Праворуч)
    p2_box = rect(680, 220, 240, 90, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    p2_txt = mtext(800, 250, ["2. ВИМИВАННЯ КЕШУ", "Запити вилітають за таймаутом,", "кеш не наповнюється, HitRate → 0,", "БД отримує 50× навантаження"], size=10, bold=False, color=INK)
    frags.append(p2_box + p2_txt)

    frags.append(path("M 600 245 L 675 245", stroke=POS, sw=2, fill="none"))
    frags.append(arrow(600, 245, 675, 245, color=POS, sw=2))
    frags.append(text(640, 238, "Miss-шторм", size=9, bold=True, color=POS))

    frags.append(path("M 680 285 L 605 285", stroke=POS, sw=2, fill="none"))
    frags.append(arrow(680, 285, 605, 285, color=POS, sw=2))
    frags.append(text(640, 300, "БД лежить", size=9, bold=True, color=POS))

    # Петля 3: Спіраль збирача сміття та виснаження пам'яті (Внизу)
    p3_box = rect(360, 395, 240, 85, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    p3_txt = mtext(480, 423, ["3. СПІРАЛЬ GC ТА ПАМ'ЯТІ", "Черги ростуть → об'єкти виживають", "у старші покоління (Tenured Heap) →", "паузи GC 500-1000 мс"], size=10, bold=False, color=INK)
    frags.append(p3_box + p3_txt)

    frags.append(path("M 440 310 C 410 340 410 370 440 395", stroke=POS, sw=2, fill="none"))
    frags.append(arrow(430, 365, 445, 390, color=POS, sw=2))
    frags.append(text(390, 355, "Купа росте", size=10, bold=True, color=POS, anchor="end"))

    frags.append(path("M 520 395 C 550 370 550 340 520 310", stroke=POS, sw=2, fill="none"))
    frags.append(arrow(530, 340, 515, 315, color=POS, sw=2))
    frags.append(text(570, 355, "GC паузи", size=10, bold=True, color=POS, anchor="start"))

    # Висновок внизу
    ft_box = rect(140, 505, 680, 50, fill="#fef2f2", stroke=POS, sw=1, rx=6)
    ft_txt = text(480, 535, "РЕЗУЛЬТАТ: Навіть коли тригер зникає, петлі 1, 2 і 3 живлять одна одну самостійно.", size=11, bold=True, color="#991b1b")
    frags.append(ft_box + ft_txt)

    render(os.path.join(IMG, "positive-feedback-loop.svg"), W, H, *frags)


# ── Фігура 3: Спіраль марної роботи (Wasted Work Spiral) ───────────────────────
def fig_wasted_work_spiral():
    W, H = 960, 520
    frags = []

    frags.append(text(480, 28, "Хронологія марної роботи (Wasted Work) та розсинхронізація дедлайнів", size=16, bold=True))

    # Сценарій А: Штатний режим (зверху)
    frags.append(rect(40, 55, 880, 160, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(60, 80, "Штатний режим (Черги порожні, обробка швидка)", size=13, bold=True, color=FIELD, anchor="start"))

    # Часова вісь для А
    frags.append(line(80, 170, 880, 170, color=LINE, sw=1.5))
    frags.append(arrow(80, 170, 890, 170, color=LINE, sw=1.5))
    frags.append(text(890, 190, "Час (t)", size=10, color=MUTED, anchor="end"))

    # Подія А
    frags.append(circle(140, 170, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(140, 190, "t = 0 мс: Запит #1", size=10, bold=True, color=INK))

    # Блок обробки сервером (140 до 220)
    frags.append(rect(140, 115, 120, 35, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(200, 137, "Обробка (40 мс)", size=10, bold=True, color=FIELD))

    frags.append(circle(260, 170, 5, fill=FIELD, stroke=FIELD))
    frags.append(text(260, 190, "t = 40 мс: Відповідь 200 OK", size=10, bold=True, color=FIELD))

    # Таймаут клієнта (відмітка на 500 мс)
    frags.append(line(600, 105, 600, 170, color="#9ca3af", sw=1.2, dash="3,3"))
    frags.append(text(600, 100, "Дедлайн клієнта (500 мс)", size=10, color=MUTED))
    frags.append(text(400, 137, "Запит виконано в межах бюджету часу (Goodput = 100%)", size=11, color=FIELD))

    # Сценарій Б: Метастабільна спіраль (знизу)
    frags.append(rect(40, 235, 880, 260, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(60, 260, "Метастабільний колапс (Переповнена черга FIFO + клієнтські повтори)", size=13, bold=True, color=POS, anchor="start"))

    # Часова вісь для Б
    frags.append(line(80, 440, 880, 440, color=LINE, sw=1.5))
    frags.append(arrow(80, 440, 890, 440, color=LINE, sw=1.5))
    frags.append(text(890, 460, "Час (t)", size=10, color=MUTED, anchor="end"))

    # Запит 1 надходить
    frags.append(circle(120, 440, 5, fill=INK, stroke=INK))
    frags.append(text(120, 460, "t = 0 с: Запит #1", size=10, bold=True, color=INK))

    # Очікування в черзі (120 до 380)
    frags.append(rect(120, 340, 220, 30, fill="#fee2e2", stroke="#f87171", sw=1.2, rx=4))
    frags.append(text(230, 360, "Очікування в черзі FIFO (2.2 с)", size=10, color=POS))

    # Таймаут клієнта на 1.5 с
    frags.append(line(270, 310, 270, 440, color=POS, sw=1.8, dash="4,4"))
    frags.append(text(270, 300, "t = 1.5 с: ТАЙМАУТ КЛІЄНТА", size=10, bold=True, color=POS))
    frags.append(text(270, 475, "Клієнт рве TCP-сокет і шле Повтор #2", size=10, bold=True, color=POS))

    # Воркер бере Запит 1 і виконує МАРНУ роботу (340 до 480)
    frags.append(rect(340, 340, 160, 30, fill="#fca5a5", stroke=POS, sw=1.5, rx=4))
    frags.append(mtext(420, 355, ["МАРНА ОБРОБКА #1", "(клієнт уже відключився)"], size=9, bold=True, color="#7f1d1d"))

    frags.append(circle(500, 440, 5, fill=POS, stroke=POS))
    frags.append(text(500, 460, "t = 2.6 с: Відповідь у мертвий сокет", size=9, color=POS))

    # Повтор 2 очікує в черзі і теж протухає
    frags.append(rect(270, 385, 300, 25, fill="#fee2e2", stroke="#f87171", sw=1.2, rx=4))
    frags.append(text(420, 402, "Повтор #2 стоїть у черзі за мертвим Запитом #1", size=10, color=POS))

    # Таймаут Повтору 2 на 3.0 с
    frags.append(line(570, 310, 570, 440, color=POS, sw=1.8, dash="4,4"))
    frags.append(text(570, 300, "t = 3.0 с: ТАЙМАУТ ПОВТОРУ #2", size=10, bold=True, color=POS))

    # Висновок
    frags.append(text(720, 360, "100% CPU витрачено на запити,", size=11, bold=True, color=POS))
    frags.append(text(720, 380, "результат яких нікому не потрібен!", size=11, bold=True, color=POS))

    render(os.path.join(IMG, "wasted-work-spiral.svg"), W, H, *frags)


# ── Фігура 4: Архітектурні контури захисту ─────────────────────────────────────
def fig_mitigation_architecture():
    W, H = 960, 560
    frags = []

    frags.append(text(480, 28, "Ешелонований захист від метастабільних відмов", size=16, bold=True))

    # 4 захисні бар'єри (колонки)
    cols = [
        ("1. КЛІЄНТСЬКИЙ РІВЕНЬ", [
            "• Бюджет повторів (Retry Budget):",
            "  максимум 10% повторів від трафіку",
            "• Експоненційний відступ + Full Jitter",
            "• Запобіжник (Circuit Breaker)",
            "• Передача заголовка дедлайну"
        ], "#eff6ff", "#3b82f6"),

        ("2. ВХІДНИЙ ШЛЮЗ (GATEWAY)", [
            "• Відсікання запитів з простроченим",
            "  дедлайном (T_remain < T_exec)",
            "• CoDel / LIFO черги замість FIFO",
            "• Адаптивне скидання трафіку",
            "• Відхилення за HTTP 429 / 503"
        ], "#f0fdf4", FIELD),

        ("3. СЕРВЕР ТА КЕШ-ШАР", [
            "• Singleflight / Request Coalescing:",
            "  1 запит до БД на N однакових ключів",
            "• XFetch (раннє ймовірнісне оновлення)",
            "• Скасування виконання при закритті",
            "  клієнтського сокета (EPOLLRDHUP)"
        ], "#fefce8", "#ca8a04"),

        ("4. ПРОТОКОЛ ВІДНОВЛЕННЯ", [
            "• Жорсткий карантин трафіку (Throttle)",
            "• Прогрів кешу перед пуском клієнтів",
            "• Плавне ступеневе відкриття шлюзів",
            "  (Slow-Start Ramp-Up)",
            "• Ізоляція критичних тенантів"
        ], "#faf5ff", "#9333ea")
    ]

    for i, (title, items, f_color, s_color) in enumerate(cols):
        cx = 50 + i * 220
        # Рамка колонки
        frags.append(rect(cx, 65, 205, 410, fill=f_color, stroke=s_color, sw=1.8, rx=8))
        frags.append(rect(cx, 65, 205, 40, fill=s_color, stroke=s_color, sw=1.8, rx=8))
        frags.append(text(cx + 102, 90, title, size=11, bold=True, color="#ffffff"))

        # Вміст
        frags.append(mtext(cx + 12, 130, items, size=10, color=INK, anchor="start", lh=1.4))

    # Стрілки між рівнями
    frags.append(arrow(255, 260, 270, 260, color=LINE, sw=2))
    frags.append(arrow(475, 260, 490, 260, color=LINE, sw=2))
    frags.append(arrow(695, 260, 710, 260, color=LINE, sw=2))

    # Нижня панель підсумку
    p_box = rect(50, 490, 865, 50, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6)
    p_txt = text(480, 520, "Головний принцип: Не починати обчислення, якщо результат не буде доставлено вчасно.", size=12, bold=True, color=INK)
    frags.append(p_box + p_txt)

    render(os.path.join(IMG, "mitigation-architecture.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_hysteresis_curve()
    fig_positive_feedback_loop()
    fig_wasted_work_spiral()
    fig_mitigation_architecture()
    print("Figures generated successfully.")
