# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. macro-scenario-graph: граф виконання багатоетапного сценарію ──────────
def fig_scenario_graph():
    W, H = 1080, 640
    p = []

    # Тло
    p.append(rect(20, 20, 1040, 600, fill="#ffffff", stroke="#e5e7eb", sw=1.5, rx=10))

    # Заголовок
    p.append(text(540, 50, "Граф виконання багатоетапного сценарію: прямий хід, бар'єри та відкат", size=15, color=INK, bold=True))
    p.append(text(540, 72, "Кожен крок верифікує передумови/постумови та реєструє компенсатор у стеку", size=11, color=MUTED))

    # Вхідна подія
    b_start, w_start, _ = textbox(130, 140, "ВХІДНА КОМАНДА\n«Старт промивки»\n(Оператор / Мережа)", size=10.5, pad=8, fill="#eff6ff", stroke="#3b82f6", sw=1.8, bold=True)
    p.append(b_start)

    # Стрілка старт -> Крок 1
    p.append(arrow(215, 140, 255, 140, color=LINE, sw=1.5))

    # Крок 1
    b_step1, w_s1, _ = textbox(385, 140, "КРОК 1: ВІДКРИТТЯ КЛАПАНА V1\nПередумова: Тиск P == 0 бар\nДія: Подати сигнал GPIO_HIGH(V1)\nПостумова: Кінцевик V1_OPEN == 1\nВитримка: 500 мс стабілізації", size=10, pad=8, fill="#f0fdf4", stroke="#22c55e", sw=1.8, bold=True)
    p.append(b_step1)

    # Стрілка Крок 1 -> Крок 2
    p.append(arrow(515, 140, 565, 140, color="#16a34a", sw=1.5))
    p.append(text(540, 128, "OK", size=10, color="#16a34a", bold=True))

    # Крок 2
    b_step2, w_s2, _ = textbox(695, 140, "КРОК 2: ЗАПУСК ПОМПИ P1\nПередумова: V1_OPEN == 1\nДія: Запуск ШІМ PWM(P1, 80%)\nПостумова: Датчик потоку Q > 5 л/хв\nТаймаут: 3000 мс на розгін", size=10, pad=8, fill="#f0fdf4", stroke="#22c55e", sw=1.8, bold=True)
    p.append(b_step2)

    # Стрілка Крок 2 -> Крок 3 (вниз і вправо)
    p.append(line(825, 140, 875, 140, color="#16a34a", sw=1.5))
    p.append(line(875, 140, 875, 275, color="#16a34a", sw=1.5))
    p.append(arrow(875, 275, 825, 275, color="#16a34a", sw=1.5))
    p.append(text(885, 210, "OK", size=10, color="#16a34a", bold=True, anchor="start"))

    # Крок 3
    b_step3, w_s3, _ = textbox(695, 275, "КРОК 3: НАБІР ТИСКУ МАГІСТРАЛІ\nПередумова: Помпа P1 працює\nДія: Плавне прикриття байпаса\nПостумова: Тиск P >= 3.5 бар\nТаймаут: 4000 мс нагнітання", size=10, pad=8, fill="#f0fdf4", stroke="#22c55e", sw=1.8, bold=True)
    p.append(b_step3)

    # Стрілка Крок 3 -> Крок 4
    p.append(arrow(565, 275, 515, 275, color="#16a34a", sw=1.5))
    p.append(text(540, 263, "OK", size=10, color="#16a34a", bold=True))

    # Крок 4
    b_step4, w_s4, _ = textbox(385, 275, "КРОК 4: ГОЛОВНИЙ КЛАПАН V2\nПередумова: Тиск у межах 3.5..5.0 бар\nДія: Відкрити магістраль GPIO(V2, 1)\nПостумова: Сенсор V2_OPEN == 1\nТаймаут: 1000 мс на відкриття", size=10, pad=8, fill="#f0fdf4", stroke="#22c55e", sw=1.8, bold=True)
    p.append(b_step4)

    # Стрілка Крок 4 -> Фініш
    p.append(arrow(255, 275, 215, 275, color="#16a34a", sw=1.5))
    p.append(text(235, 263, "OK", size=10, color="#16a34a", bold=True))

    # Фініш успіху
    b_done, _, _ = textbox(130, 275, "УСПІШНИЙ ФІНІШ\nСтан: РОБОЧИЙ РЕЖИМ\nСистема готова до циклу\nСтек відкату очищено", size=10.5, pad=8, fill="#dcfce7", stroke="#15803d", sw=2.0, color="#14532d", bold=True)
    p.append(b_done)

    # Блок аварійного відкату (Rollback Engine)
    p.append(rect(45, 410, 990, 190, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    p.append(text(540, 435, "ТРАЄКТОРІЯ АВАРІЙНОГО ВІДКАТУ ТА КОМПЕНСАЦІЇ (ROLLBACK / SAFE ABORT)", size=12, color="#991b1b", bold=True))

    # Стрілки провалу з кроків 1, 2, 3, 4 до блоку відкату
    p.append(arrow(340, 195, 340, 405, color="#dc2626", sw=1.5))
    p.append(text(348, 350, "Провал Крок 1", size=9.5, color="#dc2626", bold=True, anchor="start"))

    p.append(line(760, 195, 760, 225, color="#dc2626", sw=1.5))
    p.append(line(760, 225, 920, 225, color="#dc2626", sw=1.5))
    p.append(arrow(920, 225, 920, 405, color="#dc2626", sw=1.5))
    p.append(text(928, 350, "Провал Крок 2", size=9.5, color="#dc2626", bold=True, anchor="start"))

    p.append(arrow(695, 330, 695, 405, color="#dc2626", sw=1.5))
    p.append(text(705, 370, "Провал Крок 3", size=9.5, color="#dc2626", bold=True, anchor="start"))

    p.append(arrow(430, 330, 430, 405, color="#dc2626", sw=1.5))
    p.append(text(438, 370, "Провал Крок 4", size=9.5, color="#dc2626", bold=True, anchor="start"))

    # Кроки компенсації всередині зони відкату
    b_rb1, _, _ = textbox(190, 510, "1. Закрити V2 (якщо відкрито)\nЗняття сигналу з клапана\nТаймаут 1000 мс", size=10, pad=8, fill="#fee2e2", stroke="#ef4444", sw=1.4, color="#7f1d1d", bold=True)
    p.append(b_rb1)

    p.append(arrow(300, 510, 350, 510, color="#dc2626", sw=1.5))

    b_rb2, _, _ = textbox(460, 510, "2. Зупинити помпу P1\nPWM(P1, 0%), блокування ШІМ\nКонтроль струму споживання", size=10, pad=8, fill="#fee2e2", stroke="#ef4444", sw=1.4, color="#7f1d1d", bold=True)
    p.append(b_rb2)

    p.append(arrow(570, 510, 620, 510, color="#dc2626", sw=1.5))

    b_rb3, _, _ = textbox(730, 510, "3. Скинути тиск через V1\nВідкрити байпас до P < 0.2 бар\nЗакрити V1 у фіналі", size=10, pad=8, fill="#fee2e2", stroke="#ef4444", sw=1.4, color="#7f1d1d", bold=True)
    p.append(b_rb3)

    p.append(arrow(840, 510, 890, 510, color="#dc2626", sw=1.5))

    b_safe, _, _ = textbox(955, 510, "БЕЗПЕЧНИЙ\nСТОП", size=10.5, pad=8, fill="#fca5a5", stroke="#991b1b", sw=1.8, color="#7f1d1d", bold=True)
    p.append(b_safe)

    render(os.path.join(OUT, "macro-scenario-graph.svg"), W, H, *p,
           title="Граф виконання багатоетапного сценарію: прямий хід, бар'єри та відкат")


# ── 2. asynchronous-step-lifecycle: життєвий цикл асинхронного кроку ──────────
def fig_step_lifecycle():
    W, H = 1000, 560
    p = []

    # Тло
    p.append(rect(20, 20, 960, 520, fill="#ffffff", stroke="#e5e7eb", sw=1.5, rx=10))

    # Заголовок
    p.append(text(500, 50, "Життєвий цикл асинхронного кроку в неблокуючому суперциклі", size=15, color=INK, bold=True))
    p.append(text(500, 72, "Функція scenario_tick() викликається періодично і квантує виконання без delay()", size=11, color=MUTED))

    # Стан 1: IDLE / PENDING
    b_idle, _, _ = textbox(140, 150, "1. PENDING\nОчікування черги\nКрок зареєстровано", size=10.5, pad=8, fill="#f3f4f6", stroke="#9ca3af", sw=1.5, bold=True)
    p.append(b_idle)

    # Стрілка 1 -> 2
    p.append(arrow(220, 150, 275, 150, color=LINE, sw=1.5))
    p.append(text(248, 138, "tick()", size=9.5, color=MUTED, bold=True))

    # Стан 2: PRECHECK
    b_pre, _, _ = textbox(380, 150, "2. PRECHECK\nПеревірка предикату\nprecondition() == true?", size=10.5, pad=8, fill="#eff6ff", stroke="#3b82f6", sw=1.5, bold=True)
    p.append(b_pre)

    # Гілка відмови Precondition -> FAIL
    p.append(arrow(380, 205, 380, 430, color="#dc2626", sw=1.5))
    p.append(text(390, 310, "false (Помилка передумови)", size=9.5, color="#dc2626", bold=True, anchor="start"))

    # Стрілка 2 -> 3 (OK)
    p.append(arrow(485, 150, 545, 150, color="#16a34a", sw=1.5))
    p.append(text(515, 138, "true", size=9.5, color="#16a34a", bold=True))

    # Стан 3: ACTION_ENTER
    b_enter, _, _ = textbox(660, 150, "3. ACTION_ENTER\nВиклик action_fn()\nФіксація start_ms\nРеєстрація undo_fn", size=10.5, pad=8, fill="#fefce8", stroke="#eab308", sw=1.5, bold=True)
    p.append(b_enter)

    # Стрілка 3 -> 4
    p.append(arrow(660, 210, 660, 265, color=LINE, sw=1.5))

    # Стан 4: EXECUTING (State Polling Loop)
    b_exec, _, _ = textbox(660, 330, "4. EXECUTING (Опитування)\n- Перевірка інваріантів безпеки\n- Перевірка постумови postcondition()\n- Перевірка таймауту: now - start >= T", size=10.5, pad=10, fill="#eff6ff", stroke="#2563eb", sw=1.8, bold=True)
    p.append(b_exec)

    # Петля опитування (Polling Loop)
    p.append(arrow(795, 310, 850, 310, color="#2563eb", sw=1.4))
    p.append(line(850, 310, 850, 350, color="#2563eb", sw=1.4))
    p.append(arrow(850, 350, 795, 350, color="#2563eb", sw=1.4))
    p.append(text(860, 334, "Умова не готова,\nчас < T: чекати", size=9.5, color="#1d4ed8", bold=True, anchor="start"))

    # Гілка успіху 4 -> 5 (SUCCESS)
    p.append(arrow(660, 395, 660, 445, color="#16a34a", sw=1.8))
    p.append(text(670, 420, "postcondition() == true", size=9.5, color="#16a34a", bold=True, anchor="start"))

    b_succ, _, _ = textbox(660, 480, "5. STEP_COMPLETED\nКрок успішно завершено\nПерехід до кроку N+1", size=10.5, pad=8, fill="#dcfce7", stroke="#15803d", sw=2.0, color="#14532d", bold=True)
    p.append(b_succ)

    # Гілки провалу з EXECUTING -> STEP_FAILED / TIMEOUT
    p.append(arrow(525, 330, 270, 330, color="#dc2626", sw=1.6))
    p.append(text(395, 318, "Таймаут сплив АБО порушено інваріант", size=9.5, color="#dc2626", bold=True))

    b_fail, _, _ = textbox(180, 430, "STEP_FAILED / TIMED_OUT\nГенерація коду помилки\nІніціалізація відкату (Rollback)", size=10.5, pad=8, fill="#fee2e2", stroke="#b91c1c", sw=2.0, color="#7f1d1d", bold=True)
    p.append(b_fail)

    p.append(arrow(180, 375, 180, 390, color="#dc2626", sw=1.5))

    render(os.path.join(OUT, "asynchronous-step-lifecycle.svg"), W, H, *p,
           title="Життєвий цикл асинхронного кроку в неблокуючому суперциклі")


# ── 3. rollback-compensation-stack: стек компенсацій та відкат ───────────────
def fig_rollback_stack():
    W, H = 980, 520
    p = []

    # Тло
    p.append(rect(20, 20, 940, 480, fill="#ffffff", stroke="#e5e7eb", sw=1.5, rx=10))

    # Заголовок
    p.append(text(490, 50, "Стек компенсацій (Rollback Sequence): розгортання дій у порядку LIFO", size=15, color=INK, bold=True))
    p.append(text(490, 72, "При аварії на будь-якому кроці рушій викликає зареєстровані компенсатори у зворотній послідовності", size=11, color=MUTED))

    # Ліва частина: Прямий хід (Push Undo Actions)
    p.append(rect(45, 105, 410, 370, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    p.append(text(250, 130, "ПРЯМИЙ ХІД СЦЕНАРІЮ (Forward Execution)", size=12, color="#166534", bold=True))

    p.append(rect(65, 155, 370, 60, fill="#ffffff", stroke="#22c55e", sw=1.4, rx=6))
    p.append(text(80, 178, "Крок 1: Відкрити клапан V1", size=10.5, color="#166534", bold=True, anchor="start"))
    p.append(text(80, 198, "↳ Push Undo: Закрити клапан V1", size=9.5, color="#15803d", anchor="start"))

    p.append(rect(65, 230, 370, 60, fill="#ffffff", stroke="#22c55e", sw=1.4, rx=6))
    p.append(text(80, 253, "Крок 2: Запустити помпу P1 (80%)", size=10.5, color="#166534", bold=True, anchor="start"))
    p.append(text(80, 273, "↳ Push Undo: Зупинити помпу P1 (0%)", size=9.5, color="#15803d", anchor="start"))

    p.append(rect(65, 305, 370, 60, fill="#ffffff", stroke="#22c55e", sw=1.4, rx=6))
    p.append(text(80, 328, "Крок 3: Відкрити магістраль V2", size=10.5, color="#166534", bold=True, anchor="start"))
    p.append(text(80, 348, "↳ Push Undo: Закрити клапан V2", size=9.5, color="#15803d", anchor="start"))

    p.append(rect(65, 380, 370, 75, fill="#fee2e2", stroke="#ef4444", sw=1.6, rx=6))
    p.append(text(80, 403, "Крок 4: Запалювання пальника / Нагрів", size=10.5, color="#991b1b", bold=True, anchor="start"))
    p.append(text(80, 423, "✖ АВАРІЯ: Збій полум'я / Датчик тиску!", size=10, color="#dc2626", bold=True, anchor="start"))
    p.append(text(80, 442, "Виконання сценарію негайно зупиняється", size=9.5, color="#7f1d1d", anchor="start"))

    # Центральна стрілка виклику відкату
    p.append(arrow(455, 417, 515, 417, color="#dc2626", sw=2.0))
    p.append(text(485, 405, "ABORT", size=9.5, color="#dc2626", bold=True))

    # Права частина: Зворотний відкат (LIFO Unwinding)
    p.append(rect(525, 105, 410, 370, fill="#fef2f2", stroke="#fca5a5", sw=1.5, rx=8))
    p.append(text(730, 130, "ВІДКАТ ТА КОМПЕНСАЦІЯ (LIFO Rollback)", size=12, color="#991b1b", bold=True))

    p.append(rect(545, 155, 370, 60, fill="#ffffff", stroke="#ef4444", sw=1.4, rx=6))
    p.append(text(560, 178, "1. Pop & Exec: Закрити клапан V2", size=10.5, color="#991b1b", bold=True, anchor="start"))
    p.append(text(560, 198, "Відсікання магістралі високого тиску", size=9.5, color="#7f1d1d", anchor="start"))

    p.append(arrow(730, 215, 730, 230, color="#dc2626", sw=1.5))

    p.append(rect(545, 230, 370, 60, fill="#ffffff", stroke="#ef4444", sw=1.4, rx=6))
    p.append(text(560, 253, "2. Pop & Exec: Зупинити помпу P1", size=10.5, color="#991b1b", bold=True, anchor="start"))
    p.append(text(560, 273, "Зняття силового живлення з двигуна", size=9.5, color="#7f1d1d", anchor="start"))

    p.append(arrow(730, 290, 730, 305, color="#dc2626", sw=1.5))

    p.append(rect(545, 305, 370, 60, fill="#ffffff", stroke="#ef4444", sw=1.4, rx=6))
    p.append(text(560, 328, "3. Pop & Exec: Закрити клапан V1", size=10.5, color="#991b1b", bold=True, anchor="start"))
    p.append(text(560, 348, "Повне знеструмлення гідравлічного контуру", size=9.5, color="#7f1d1d", anchor="start"))

    p.append(arrow(730, 365, 730, 385, color="#dc2626", sw=1.5))

    p.append(rect(545, 385, 370, 65, fill="#fee2e2", stroke="#b91c1c", sw=1.8, rx=6))
    p.append(text(560, 410, "ФІНІШ ВІДКА ТУ: БЕЗПЕЧНИЙ СТАН", size=11, color="#7f1d1d", bold=True, anchor="start"))
    p.append(text(560, 432, "Апарат готовий до діагностики без пошкоджень", size=9.5, color="#991b1b", anchor="start"))

    render(os.path.join(OUT, "rollback-compensation-stack.svg"), W, H, *p,
           title="Стек компенсацій (Rollback Sequence): розгортання дій у порядку LIFO")


if __name__ == "__main__":
    fig_scenario_graph()
    fig_step_lifecycle()
    fig_rollback_stack()
    print("All scenario figures generated successfully.")
