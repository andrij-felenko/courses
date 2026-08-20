# -*- coding: utf-8 -*-
"""Фігури до теми «Пороги часу відгуку інтерфейсу: 0.1 с, 1 с, 10 с»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"
COOL = "#eaf0fd"
GOOD = "#e8f6ee"
WARN = "#fef9e7"


# ── 1. Логарифмічна шкала порогів сприйняття ─────────────────────────────────
def three_thresholds_scale():
    W, H = 1080, 500
    f = []

    f.append(text(W / 2, 35, "Шкала часу реакції людини та архітектурні вимоги до інтерфейсу",
                  size=16, bold=True))

    x0, x1 = 90.0, 990.0
    y_axis = 140.0
    f.append(line(x0, y_axis, x1, y_axis, color=LINE, sw=2.5))

    # Ключові точки на логарифмічній шкалі (16мс, 100мс, 1000мс, 10000мс)
    ticks = [
        (140.0, "16.7 мс", "Кадр (60 Гц)", COOL),
        (370.0, "100 мс (0.1 с)", "Пряма маніпуляція", GOOD),
        (650.0, "1000 мс (1.0 с)", "Потік думок", WARN),
        (930.0, "10 000 мс (10 с)", "Межа уваги", WARM),
    ]

    for x, time_lbl, name_lbl, fill in ticks:
        f.append(line(x, y_axis - 15, x, y_axis + 15, color=LINE, sw=2.0))
        f.append(text(x, y_axis - 28, time_lbl, size=13, bold=True, color=INK))
        f.append(text(x, y_axis - 46, name_lbl, size=12, color=MUTED))

    # Зони між порогами
    zones = [
        (60.0, 240.0, 190.0, 260.0,
         "Зона неперервного руху\n(кінестетика)",
         "• Плавний скрол і перетягування\n• Бюджет коду на кадр: ≤10 мс\n• При затримці >16 мс — дрижання",
         COOL),
        (260.0, 500.0, 190.0, 260.0,
         "Зона причинності\n(пряма дія)",
         "• Відчуття фізичної кнопки\n• Відгук сприймається миттєвим\n• Понад 100 мс: відчуття «комп'ютер думає»",
         GOOD),
        (520.0, 780.0, 190.0, 260.0,
         "Зона збереження потоку\n(робоча пам'ять)",
         "• Користувач помічає затримку\n• Контекст задачі не втрачається\n• Понад 1 с: потрібен індикатор завантаження",
         WARN),
        (800.0, 1040.0, 190.0, 260.0,
         "Зона втрати фокусу\n(перемикання уваги)",
         "• Увага розсіюється на інші задачі\n• Штраф на відновлення контексту\n• Вимагає детермінованого прогрес-бару",
         WARM),
    ]

    for left, right, top, bottom, title_txt, body_txt, fill in zones:
        zw = right - left
        zh = bottom - top
        f.append(rect(left, top, zw, zh, fill=fill, stroke=LINE, sw=1.2, rx=6))
        
        t_lines = title_txt.split("\n")
        f.append(text(left + zw / 2, top + 24, t_lines[0], size=13, bold=True))
        if len(t_lines) > 1:
            f.append(text(left + zw / 2, top + 42, t_lines[1], size=11.5, color=MUTED))

        f.append(line(left + 15, top + 54, right - 15, top + 54, color=MUTED, sw=0.8, dash="3,3"))

        b_lines = body_txt.split("\n")
        for idx, bl in enumerate(b_lines):
            f.append(text(left + 14, top + 80 + idx * 26, bl, size=11.5, anchor="start"))

    render(os.path.join(OUT, "three-thresholds-scale.svg"), W, H, *f,
           title="Логарифмічна шкала порогів сприйняття та вимоги до інтерфейсу")


# ── 2. Model Human Processor (конвеєр сприйняття людини) ─────────────────────
def mhp_cycle_pipeline():
    W, H = 1080, 480
    f = []

    f.append(text(W / 2, 32, "Model Human Processor (Card, Moran, Newell): конвеєр когнітивної обробки",
                  size=15, bold=True))

    # Три процесори у вигляді блоків
    boxes = [
        (60.0, 100.0, 260.0, 220.0,
         "Перцептивний процесор", "Tp ≈ 100 мс [50–200 мс]",
         ["• Сенсорна зорова пам'ять",
          "  (час згасання ≈ 200 мс)",
          "• Кодування фізичного світла",
          "  у нейронні образи",
          "• Дискретизація вхідного потоку"],
         COOL),
        (410.0, 100.0, 260.0, 220.0,
         "Когнітивний процесор", "Tc ≈ 70 мс [25–170 мс]",
         ["• Робоча пам'ять (7±2 фрагменти,",
          "  час згасання ≈ 7–20 с)",
          "• Довгострокова пам'ять (LTM)",
          "• Розпізнавання та прийняття рішень",
          "• Зіставлення шаблонів"],
         GOOD),
        (760.0, 100.0, 260.0, 220.0,
         "Моторний процесор", "Tm ≈ 70 мс [30–100 мс]",
         ["• Формування моторних команд",
          "• Активація м'язів кисті й пальців",
          "• Фізичне натискання клавіші/миші",
          "• Контроль траєкторії руху"],
         WARN),
    ]

    for bx, by, bw, bh, header, cycle_time, items, fill in boxes:
        f.append(rect(bx, by, bw, bh, fill=fill, stroke=LINE, sw=1.4, rx=6))
        f.append(text(bx + bw / 2, by + 28, header, size=13.5, bold=True))
        f.append(text(bx + bw / 2, by + 48, cycle_time, size=12, color=NEG, bold=True))
        f.append(line(bx + 12, by + 60, bx + bw - 12, by + 60, color=MUTED, sw=0.8))
        for idx, it in enumerate(items):
            f.append(text(bx + 14, by + 86 + idx * 24, it, size=11.5, anchor="start"))

    # Стрілки прямого ходу між процесорами
    f.append(arrow(320, 210, 410, 210, color=LINE, sw=2))
    f.append(text(365, 198, "зорові образи", size=10.5, color=MUTED))

    f.append(arrow(670, 210, 760, 210, color=LINE, sw=2))
    f.append(text(715, 198, "намір дії", size=10.5, color=MUTED))

    # Зовнішнє коло зворотного зв'язку (Feedback Loop через екран)
    y_loop = 390.0
    f.append(line(890, 320, 890, y_loop, color=POS, sw=1.8, dash="4,4"))
    f.append(line(890, y_loop, 190, y_loop, color=POS, sw=1.8, dash="4,4"))
    f.append(arrow(190, y_loop, 190, 320, color=POS, sw=1.8))

    f.append(fitbox(400, y_loop - 25, 280, 50,
                    "Зовнішній контур: Екран інтерфейсу\nЦільовий відгук: ≤ 100 мс (T_sys ≤ Tp)",
                    size=12, bold=True, fill=WARM, stroke=POS))

    f.append(text(W / 2, 455,
                  "Якщо система повертає відгук за час T_sys ≤ Tp, мозок інтегрує реакцію в той самий цикл сприйняття",
                  size=12, color=INK))

    render(os.path.join(OUT, "mhp-cycle-pipeline.svg"), W, H, *f,
           title="Model Human Processor: перцептивний, когнітивний і моторний цикли")


# ── 3. Розподіл бюджету взаємодії (RAIL та кадровий слот) ────────────────────
def rail_budget_breakdown():
    W, H = 1080, 510
    f = []

    f.append(text(W / 2, 32, "Бюджети часу за моделлю RAIL та анатомія кадрового слота",
                  size=15, bold=True))

    # Секція 1: Відгук на ввід (Response budget = 100 мс)
    f.append(text(60, 75, "1. Бюджет реакції на клік / натискання (Response ≤ 100 мс)",
                  size=13.5, bold=True, anchor="start"))

    x_resp, y_resp, w_resp, h_resp = 60.0, 95.0, 960.0, 52.0
    f.append(rect(x_resp, y_resp, w_resp, h_resp, fill=FILL, stroke=LINE, sw=1.2, rx=4))

    # Поділ 100 мс на 50 мс очікування черги + 50 мс виконання
    f.append(rect(x_resp, y_resp, 480, h_resp, fill=WARN, stroke=LINE, sw=1.0))
    f.append(text(x_resp + 240, y_resp + 24, "Очікування черги подій (≤ 50 мс)", size=12, bold=True))
    f.append(text(x_resp + 240, y_resp + 42, "Попередня задача у циклі подій", size=10.5, color=MUTED))

    f.append(rect(x_resp + 480, y_resp, 480, h_resp, fill=GOOD, stroke=LINE, sw=1.0))
    f.append(text(x_resp + 720, y_resp + 24, "Обробка вводу + підготовка кадру (≤ 50 мс)", size=12, bold=True))
    f.append(text(x_resp + 720, y_resp + 42, "Обробник події, оновлення DOM/дерева", size=10.5, color=MUTED))

    f.append(text(x_resp + w_resp / 2, y_resp + h_resp + 24,
                  "Сумарно: 50 мс (черга) + 50 мс (код) = 100 мс → золотий поріг Long Task API (50 мс)",
                  size=11.5, color=INK))

    # Секція 2: Кадровий бюджет (Animation = 16.67 мс при 60 Гц)
    f.append(text(60, 220, "2. Бюджет кадру анімації (Animation: 16.67 мс при 60 Гц / 8.33 мс при 120 Гц)",
                  size=13.5, bold=True, anchor="start"))

    x_frame, y_frame, w_frame, h_frame = 60.0, 240.0, 960.0, 56.0
    f.append(rect(x_frame, y_frame, w_frame, h_frame, fill=FILL, stroke=LINE, sw=1.2, rx=4))

    # Сегменти всередині кадру 16.67 мс
    # Загальна ширина 960 px відповідає 16.67 мс (1 мс = 57.58 px)
    segs = [
        ("Скрипти застосунку", 8.0, GOOD, "Обробка стану, VDOM diff"),
        ("Стилі та розкладка", 3.2, COOL, "Recalculate Style, Layout"),
        ("Малювання шарів", 2.8, COOL, "Paint, Rasterization"),
        ("Композиція GPU", 2.67, WARM, "vsync обмін буферів"),
    ]

    cur_x = x_frame
    for name, dur_ms, fill_col, sub_txt in segs:
        seg_w = (dur_ms / 16.67) * w_frame
        f.append(rect(cur_x, y_frame, seg_w, h_frame, fill=fill_col, stroke=LINE, sw=1.0))
        f.append(text(cur_x + seg_w / 2, y_frame + 22, "%s (%.1f мс)" % (name, dur_ms), size=11.5, bold=True))
        f.append(text(cur_x + seg_w / 2, y_frame + 42, sub_txt, size=10, color=MUTED))
        cur_x += seg_w

    f.append(text(x_frame + w_frame / 2, y_frame + h_frame + 24,
                  "Для коду застосунку доступно лише ≈8–10 мс (при 60 Гц) або ≈3–4 мс (при 120 Гц)",
                  size=11.5, color=POS, bold=True))

    # Секція 3: Фонова квантована робота (Idle)
    f.append(text(60, 365, "3. Фонова робота квантами (Idle Blocks ≤ 50 мс)",
                  size=13.5, bold=True, anchor="start"))

    y_idle = 385.0
    for i in range(4):
        bx = 60.0 + i * 245.0
        f.append(rect(bx, y_idle, 220, 48, fill=FILL, stroke=LINE, sw=1.0, rx=4))
        f.append(text(bx + 110, y_idle + 20, "Квант роботи #%d (≤50 мс)" % (i + 1), size=11.5, bold=True))
        f.append(text(bx + 110, y_idle + 38, "scheduler.yield()", size=10.5, color=MUTED))

    f.append(text(W / 2, 475,
                  "Розбиття фонових обчислень на шматки ≤50 мс гарантує миттєву поступку потоку для обробки вводу",
                  size=12, color=INK))

    render(os.path.join(OUT, "rail-budget-breakdown.svg"), W, H, *f,
           title="Анатомія часових бюджетів: Response, Animation та Idle")


# ── 4. Песимістичний vs Оптимістичний UI ───────────────────────────────────────
def optimistic_vs_pessimistic_timeline():
    W, H = 1080, 520
    f = []

    f.append(text(W / 2, 32, "Порівняння реакції: Песимістичний vs Оптимістичний інтерфейс",
                  size=15, bold=True))

    # ── Верхня доріжка: Песимістичний UI
    y_pess = 80.0
    f.append(rect(40, y_pess, 1000, 180, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(60, y_pess + 28, "Песимістичний підхід (чекаємо сервер перед оновленням)",
                  size=13.5, bold=True, anchor="start", color=POS))

    # Часова шкала песимістичного UI
    f.append(fitbox(60, y_pess + 55, 120, 48, "Клік користувача\n(t = 0 мс)", size=11.5, fill=COOL))
    f.append(arrow(180, y_pess + 79, 230, y_pess + 79, color=LINE, sw=1.5))

    f.append(fitbox(230, y_pess + 55, 180, 48, "Показ спінера / disable\n(t = 20 мс)", size=11.5, fill=WARN))
    f.append(arrow(410, y_pess + 79, 460, y_pess + 79, color=LINE, sw=1.5))

    f.append(fitbox(460, y_pess + 55, 320, 48, "Мережевий RTT + обробка БД на сервері\n(t = 20...600 мс — користувач чекає)", size=11.5, fill=WARM, stroke=POS))
    f.append(arrow(780, y_pess + 79, 830, y_pess + 79, color=LINE, sw=1.5))

    f.append(fitbox(830, y_pess + 55, 190, 48, "Оновлення стану та UI\n(t = 620 мс)", size=11.5, fill=GOOD))

    f.append(text(60, y_pess + 145,
                  "✗ Порушено поріг 100 мс: користувач бачить блокування й розрив потоку думок (затримка 600+ мс)",
                  size=12, anchor="start", color=POS, bold=True))

    # ── Нижня доріжка: Оптимістичний UI
    y_opt = 290.0
    f.append(rect(40, y_opt, 1000, 195, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    f.append(text(60, y_opt + 28, "Оптимістичний підхід (миттєва локальна мутація + фоновий комміт)",
                  size=13.5, bold=True, anchor="start", color=NEG))

    # Часова шкала оптимістичного UI
    f.append(fitbox(60, y_opt + 55, 120, 48, "Клік користувача\n(t = 0 мс)", size=11.5, fill=COOL))
    f.append(arrow(180, y_opt + 79, 230, y_opt + 79, color=LINE, sw=1.5))

    f.append(fitbox(230, y_opt + 55, 230, 48, "Миттєва мутація стану та UI\n(t = 16...30 мс — поріг витримано)", size=11.5, fill=GOOD, stroke=FIELD, sw=1.8))
    f.append(arrow(460, y_opt + 79, 510, y_opt + 79, color=LINE, sw=1.5))

    f.append(fitbox(510, y_opt + 55, 270, 48, "Фоновий запит до API\n(t = 30...600 мс — UI повністю інтерактивний)", size=11.5, fill=FILL))
    f.append(arrow(780, y_opt + 79, 830, y_opt + 79, color=LINE, sw=1.5))

    # Дві гілки завершення: успіх або відкат
    f.append(fitbox(830, y_opt + 45, 190, 36, "Успіх: тиха фіксація", size=11, fill=GOOD))
    f.append(fitbox(830, y_opt + 88, 190, 36, "Помилка: відкат + тост", size=11, fill=WARM, stroke=POS))

    f.append(text(60, y_opt + 160,
                  "✓ Дотримано поріг < 100 мс: відчуття миттєвої прямої маніпуляції; інтерфейс не блокується",
                  size=12, anchor="start", color=FIELD, bold=True))

    render(os.path.join(OUT, "optimistic-vs-pessimistic-timeline.svg"), W, H, *f,
           title="Песимістичне очікування мережі проти оптимістичної мутації інтерфейсу")


def main():
    three_thresholds_scale()
    mhp_cycle_pipeline()
    rail_budget_breakdown()
    optimistic_vs_pessimistic_timeline()
    print("Усі 4 фігури успішно згенеровано.")

if __name__ == '__main__':
    main()
