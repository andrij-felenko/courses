# -*- coding: utf-8 -*-
"""Фігури до теми «call_once і once_flag: одноразова ініціалізація»
(reference/cpp-standards/concurrency/call-once-lazy-init)."""
import sys, os

# 4 рівні вгору до кореня репо -> scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

FREEZE_FILL = "#fdecea"
OPEN_FILL   = "#eaf7ee"
BLUE_FILL   = "#eaf0fd"
WARN_FILL   = "#fff9db"

def svg_path(d, color=LINE, sw=1.5, fill="none", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="{fill}"{da}/>'

# ── 1. Скінченний автомат станів std::once_flag ──────────────────────────────
def fig_state_machine():
    W, H = 960, 380
    f = []

    f.append(text(W / 2, 35, "Автомат переходів внутрішнього стану std::once_flag", size=16, bold=True, color=INK))

    # Стан 1: Uninitialized
    b1 = fitbox(60, 140, 200, 90, ["Неініціалізовано", "(Uninitialized / 0)", "Початковий стан", "constexpr-конструктор"], size=12, fill=FILL, stroke=LINE)
    
    # Стан 2: In-Progress
    b2 = fitbox(380, 140, 200, 90, ["Виконується", "(In-Progress / Running)", "Один потік-лідер ініціалізує,", "інші чекають на futex"], size=12, fill=BLUE_FILL, stroke=NEG)

    # Стан 3: Initialized
    b3 = fitbox(700, 140, 200, 90, ["Ініціалізовано", "(Done / Initialized)", "Швидкий шлях: Acquire-load,", "без блокувань та системних викликів"], size=12, fill=OPEN_FILL, stroke=FIELD)

    f += [b1, b2, b3]

    # Стрілка 1 -> 2: CAS (0 -> Running)
    f.append(arrow(260, 170, 380, 170, color=NEG, sw=2))
    f.append(text(320, 158, "CAS: 0 → 1", size=11, bold=True, color=NEG))
    f.append(text(320, 185, "Потік виграв гонитву", size=11, color=MUTED))

    # Стрілка 2 -> 3: Успіх (Release Store + Wake)
    f.append(arrow(580, 170, 700, 170, color=FIELD, sw=2))
    f.append(text(640, 158, "Успішне завершення", size=11, bold=True, color=FIELD))
    f.append(text(640, 185, "Release store + futex_wake", size=11, color=MUTED))

    # Стрілка 2 -> 1 (дуга назад при винятку)
    f.append(svg_path("M 480,140 C 480,75 200,75 160,140", color=POS, sw=2, fill="none"))
    f.append(arrow(165, 130, 160, 140, color=POS, sw=2))
    f.append(text(320, 70, "Виняток (Exception) у функції ініціалізації", size=12, bold=True, color=POS))
    f.append(text(320, 88, "Стан скидається в 0, виняток прокидається далі, інші потоки пробують знову", size=11, color=MUTED))

    # Швидкий шлях на 3
    f.append(svg_path("M 800,230 C 800,300 860,300 860,230", color=FIELD, sw=1.8, fill="none"))
    f.append(arrow(858, 240, 856, 230, color=FIELD, sw=1.8))
    f.append(text(800, 320, ["Усі наступні виклики:", "Acquire load бачить Done", "і повертаються миттєво"], size=11, color=FIELD))

    # Пояснення знизу
    f.append(line(60, 260, 900, 260, color=MUTED, sw=1, dash="4 4"))
    f.append(text(W / 2, 290, "Стан Done є фінальним і незворотним: після успішної ініціалізації call_once працює як безпечний read-only бар'єр", size=12, color=INK))
    f.append(text(W / 2, 310, "Гарантується строгий порядок пам'яті: writes усередині ініціалізатора happens-before повернення з будь-якого call_once", size=11, color=MUTED))

    render(os.path.join(IMG, "call-once-state-machine.svg"), W, H, *f,
           title="Автомат переходів стану std::once_flag")


# ── 2. Розв'язання гонитви та таймлайн потоків ───────────────────────────────
def fig_race_resolution():
    W, H = 960, 420
    f = []

    f.append(text(W / 2, 30, "Часова шкала розв'язання конкуренції між потоками у std::call_once", size=16, bold=True, color=INK))

    # Лінії часу для 3 потоків
    # Потік 1 (переможець)
    f.append(text(100, 90, "Потік A (Лідер)", size=13, bold=True, color=FIELD))
    f.append(arrow(180, 85, 920, 85, color=LINE, sw=1.5))

    # Потік 2 (очікувач)
    f.append(text(100, 200, "Потік B (Очікувач 1)", size=13, bold=True, color=NEG))
    f.append(arrow(180, 195, 920, 195, color=LINE, sw=1.5))

    # Потік 3 (пізній гість)
    f.append(text(100, 310, "Потік C (Пізній виклик)", size=13, bold=True, color=MUTED))
    f.append(arrow(180, 305, 920, 305, color=LINE, sw=1.5))

    # Потік A події
    f += fitbox(210, 60, 140, 50, ["call_once()", "CAS: 0 → Running"], size=11, fill=BLUE_FILL, stroke=NEG)
    f += fitbox(400, 60, 190, 50, ["Виконання ініціалізатора", "Конструювання об'єкта T"], size=11, fill=OPEN_FILL, stroke=FIELD)
    f += fitbox(640, 60, 170, 50, ["Release store (Done)", "futex_wake(ALL)"], size=11, fill=OPEN_FILL, stroke=FIELD, bold=True)
    f += fitbox(830, 60, 80, 50, ["Повернення", "з call_once"], size=11, fill=FILL, stroke=LINE)

    # Потік B події
    f += fitbox(250, 170, 130, 50, ["call_once()", "CAS зазнає невдачі"], size=11, fill=WARN_FILL, stroke=POS)
    f += fitbox(430, 170, 180, 50, ["Сон у ядрі ОС", "sys_futex(WAIT, Running)"], size=11, fill=FREEZE_FILL, stroke=POS)
    f += fitbox(660, 170, 140, 50, ["Пробудження", "Acquire load → Done"], size=11, fill=BLUE_FILL, stroke=NEG)
    f += fitbox(830, 170, 80, 50, ["Повернення", "без запуску!"], size=11, fill=OPEN_FILL, stroke=FIELD)

    # Потік C події (пізній шлях)
    f += fitbox(730, 280, 150, 50, ["call_once()", "Acquire load: Done!"], size=11, fill=OPEN_FILL, stroke=FIELD, bold=True)
    f += fitbox(890, 280, 70, 50, ["Миттєве", "повернення"], size=11, fill=OPEN_FILL, stroke=FIELD)

    # Зв'язки між подіями
    f.append(line(280, 85, 280, 170, color=POS, sw=1.5, dash="3 3"))
    f.append(line(725, 85, 725, 170, color=FIELD, sw=1.8, dash="3 3"))
    f.append(text(745, 130, "futex wake", size=10, bold=True, color=FIELD))

    f.append(line(60, 360, 920, 360, color=MUTED, sw=1, dash="4 4"))
    f.append(text(W / 2, 385, "Потік B не витрачає ресурси процесора в очікуванні, а Потік C оминає будь-які блокування (Fast Path)", size=12, color=INK))

    render(os.path.join(IMG, "call-once-race-resolution.svg"), W, H, *f,
           title="Таймлайн конкурентного виконання std::call_once")


# ── 3. Поведінка при виникненні винятку (Exception Safety Flow) ─────────────
def fig_exception_flow():
    W, H = 960, 400
    f = []

    f.append(text(W / 2, 30, "Транзакційне відновлення при винятку в std::call_once", size=16, bold=True, color=INK))

    # Стовпчик 1: Потік 1 генерує виняток
    f.append(text(250, 65, "Перша спроба (Потік 1)", size=14, bold=True, color=POS))
    f += fitbox(150, 90, 200, 45, "1. std::call_once(flag, init)", size=11, fill=BLUE_FILL, stroke=NEG)
    f += fitbox(150, 150, 200, 50, ["2. init() виконується...", "throw std::runtime_error()"], size=11, fill=FREEZE_FILL, stroke=POS, bold=True)
    f += fitbox(150, 220, 200, 55, ["3. Розгортання стеку:", "flag скидається в 0,", "пробуджуються очікувачі"], size=11, fill=WARN_FILL, stroke=POS)
    f += fitbox(150, 295, 200, 45, "4. Виняток вилітає назовні", size=11, fill=FREEZE_FILL, stroke=POS)

    f.append(arrow(250, 135, 250, 150, color=POS, sw=1.5))
    f.append(arrow(250, 200, 250, 220, color=POS, sw=1.5))
    f.append(arrow(250, 275, 250, 295, color=POS, sw=1.5))

    # Розділювач
    f.append(line(480, 60, 480, 360, color=MUTED, sw=1.5, dash="4 4"))

    # Стовпчик 2: Потік 2 підхоплює ініціалізацію
    f.append(text(710, 65, "Повторна спроба (Потік 2)", size=14, bold=True, color=FIELD))
    f += fitbox(610, 90, 200, 45, "1. Пробудження з futex", size=11, fill=BLUE_FILL, stroke=NEG)
    f += fitbox(610, 150, 200, 50, ["2. Стан flag == 0!", "CAS переводить flag в 1"], size=11, fill=WARN_FILL, stroke=LINE)
    f += fitbox(610, 220, 200, 50, ["3. init() викликається вдруге", "Успішна ініціалізація!"], size=11, fill=OPEN_FILL, stroke=FIELD, bold=True)
    f += fitbox(610, 295, 200, 45, "4. flag = Done, коректний вихід", size=11, fill=OPEN_FILL, stroke=FIELD)

    f.append(arrow(710, 135, 710, 150, color=FIELD, sw=1.5))
    f.append(arrow(710, 200, 710, 220, color=FIELD, sw=1.5))
    f.append(arrow(710, 270, 710, 295, color=FIELD, sw=1.5))

    # Міжстовпчиковий зв'язок (передача естафети)
    f.append(arrow(350, 245, 610, 112, color=POS, sw=1.8))
    f.append(text(480, 175, "Прапорець лишився відкритим", size=11, bold=True, color=POS))

    f.append(text(W / 2, 380, "Якщо ініціалізатор кинув виняток, статус Done НЕ встановлюється. Ресурс отримує шанс відновитися.", size=12, color=INK))

    render(os.path.join(IMG, "call-once-exception-flow.svg"), W, H, *f,
           title="Обробка винятків та транзакційне відновлення у call_once")


# ── 4. Порівняння підходів до лінивої ініціалізації ───────────────────────────
def fig_comparison():
    W, H = 960, 360
    f = []

    f.append(text(W / 2, 30, "Порівняння механізмів одноразової ініціалізації у C++", size=16, bold=True, color=INK))

    cols = [(30, 180), (220, 170), (400, 180), (590, 170), (770, 160)]
    heads = ["Механізм", "Потокобезпека", "Вартість Fast Path", "Сфера застосування", "Стійкість до винятків"]

    for (x, w), h in zip(cols, heads):
        f.append(fitbox(x, 60, w, 36, h, size=12, bold=True, fill="#eef1f5", stroke=MUTED))

    rows = [
        ("Рання ініціалізація\n(Eager / main)", "Повна (до старту ниток)", "0 (звичайна змінна)", "Глобальні незмінні конфігурації", "Крах програми до запуску"),
        ("М'ютекс на кожен доступ\n(std::mutex)", "Повна (через замок)", "Висока (atomic lock/unlock)", "Динамічні структури даних", "Потрібен RAII-замок"),
        ("Локальні статики\n(Magic Statics)", "Повна (C++11 §6.7)", "Мінімальна (Acquire load)", "Одинаки (Meyer's Singleton)", "Виняток дозволяє повтор"),
        ("std::call_once +\nonce_flag", "Повна (Acquire-Release + futex)", "Мінімальна (1 Acquire load)", "Члени класів, пули, повторювані ініціалізації", "Транзакційне відновлення"),
    ]

    y = 105
    for t1, t2, t3, t4, t5 in rows:
        is_call_once = "call_once" in t1
        bg = OPEN_FILL if is_call_once else FILL
        strk = FIELD if is_call_once else MUTED

        f.append(fitbox(cols[0][0], y, cols[0][1], 54, t1, size=11, bold=True, fill=bg, stroke=strk))
        f.append(fitbox(cols[1][0], y, cols[1][1], 54, t2, size=11, fill=BG, stroke=MUTED))
        f.append(fitbox(cols[2][0], y, cols[2][1], 54, t3, size=11, fill=BG, stroke=MUTED))
        f.append(fitbox(cols[3][0], y, cols[3][1], 54, t4, size=11, fill=BG, stroke=MUTED))
        f.append(fitbox(cols[4][0], y, cols[4][1], 54, t5, size=11, fill=BG, stroke=MUTED))
        y += 58

    f.append(text(W / 2, 345, "std::call_once надає таку ж швидкість, як Magic Statics, але з гнучкістю прив'язки до екземплярів об'єктів", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "lazy-init-comparison.svg"), W, H, *f,
           title="Порівняльна таблиця механізмів ініціалізації")


if __name__ == "__main__":
    fig_state_machine()
    fig_race_resolution()
    fig_exception_flow()
    fig_comparison()
    print("All figures generated successfully.")
