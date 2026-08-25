# -*- coding: utf-8 -*-
"""Фігури до теми «Senders і Receivers: асинхронна модель P2300»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

LIVE = "#e8f6ee"
WARM = "#fdecea"
COOL = "#eef2fb"

def fig_triad_lifecycle():
    W, H = 940, 480
    f = []

    # Фаза 1: Опис і планування
    f.append(fitbox(30, 40, 200, 70, "1. Scheduler\n(Планувальник)\nschedule(sch)", size=12, fill=COOL, stroke=NEG, bold=True))
    f.append(arrow(130, 110, 130, 170, color=NEG, sw=2))

    f.append(fitbox(30, 170, 200, 80, "2. Sender (Описувач)\nЛінивий вираз роботи\n(Value Type / Lazy)", size=12, fill=LIVE, stroke=FIELD, bold=True))

    f.append(fitbox(30, 310, 200, 80, "Receiver (Приймач)\nСпоживач сигналів\nget_env(rcvr)", size=12, fill=FILL, stroke=LINE, bold=True))

    # Зв'язування connect()
    f.append(arrow(230, 210, 350, 250, color=FIELD, sw=2))
    f.append(arrow(230, 350, 350, 270, color=LINE, sw=2))
    f.append(text(285, 220, "connect(snd, rcvr)", size=11, color=INK, bold=True))

    # Фаза 2: Стан операції
    f.append(rect(350, 140, 240, 240, fill=BG, stroke=LINE, sw=2, rx=8))
    f.append(text(470, 170, "Operation State", size=14, bold=True))
    f.append(text(470, 190, "(Стан операції на стеку)", size=11, color=MUTED, italic=True))
    f.append(line(370, 205, 570, 205, color=LINE, sw=1))
    f.append(fitbox(370, 215, 200, 45, "Проміжні буфери значень", size=11, fill=LIVE, stroke=FIELD))
    f.append(fitbox(370, 268, 200, 45, "Посилання на Receiver / Env", size=11, fill=COOL, stroke=NEG))
    f.append(fitbox(370, 321, 200, 45, "stop_callback реєстрація", size=11, fill=WARM, stroke=POS))

    # Фаза 3: Запуск start()
    f.append(arrow(590, 260, 690, 260, color=POS, sw=2.5))
    f.append(text(640, 245, "start(op_state)", size=12, color=POS, bold=True))

    # Три канали завершення
    f.append(arrow(690, 260, 740, 100, color=FIELD, sw=2))
    f.append(fitbox(740, 65, 170, 70, "set_value(rcvr, args...)\nКанал успіху\n(0..N значень)", size=11, fill=LIVE, stroke=FIELD, bold=True))

    f.append(arrow(690, 260, 740, 260, color=POS, sw=2))
    f.append(fitbox(740, 225, 170, 70, "set_error(rcvr, err)\nКанал помилки\n(exception_ptr / code)", size=11, fill=WARM, stroke=POS, bold=True))

    f.append(arrow(690, 260, 740, 410, color=NEG, sw=2))
    f.append(fitbox(740, 375, 170, 70, "set_stopped(rcvr)\nКанал зупинки\n(Кооперативне скасування)", size=11, fill=COOL, stroke=NEG, bold=True))

    # Пояснювальний підпис
    f.append(text(470, 450, "Концептуальна тріада P2300: Фази складання, зв'язування та три канали завершення", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'p2300-triad-lifecycle.svg'), W, H, *f,
           title="Життєвий цикл та три канали завершення P2300")

def fig_zero_alloc_stack():
    W, H = 940, 460
    f = []

    # Ліва колонка: Eager / Heap Allocation (std::future & raw coroutine)
    f.append(rect(30, 40, 410, 360, fill="#fffaf9", stroke=POS, sw=1.5, rx=8))
    f.append(text(235, 70, "Традиційний підхід: std::future / Promise", size=13, color=POS, bold=True))
    f.append(text(235, 90, "Численні динамічні алокації у купі (Heap)", size=11, color=MUTED, italic=True))

    f.append(fitbox(55, 110, 360, 60, "Shared State 1 (new shared_state<int>)\nЛічильник посилань + mutex + condition_variable", size=11, fill=WARM, stroke=POS))
    f.append(arrow(235, 170, 235, 200, color=POS, sw=1.5))
    f.append(text(300, 185, ".then() алокація", size=10, color=POS))

    f.append(fitbox(55, 200, 360, 60, "Shared State 2 (new shared_state<string>)\nОкремий блок пам'яті + окрема синхронізація", size=11, fill=WARM, stroke=POS))
    f.append(arrow(235, 260, 235, 290, color=POS, sw=1.5))
    f.append(text(300, 275, "динамічний міст", size=10, color=POS))

    f.append(fitbox(55, 290, 360, 60, "Фрейм корутини (operator new(size))\nВиділення в купі за відсутності оптимізації HALO", size=11, fill=WARM, stroke=POS))
    f.append(text(235, 380, "Високі накладні витрати пам'яті, кеш-промахи", size=11, color=POS, italic=True))

    # Права колонка: Zero-allocation P2300 execution
    f.append(rect(490, 40, 420, 360, fill="#f9fdfa", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(700, 70, "Модель P2300: std::execution", size=13, color=FIELD, bold=True))
    f.append(text(700, 90, "Єдиний монолітний об'єкт на стеку (Zero Alloc)", size=11, color=MUTED, italic=True))

    # Вкладений OperationState
    f.append(rect(515, 110, 370, 240, fill=LIVE, stroke=FIELD, sw=2, rx=6))
    f.append(text(700, 135, "struct then_operation_state (Стек)", size=12, color=FIELD, bold=True))
    f.append(text(700, 153, "sizeof(...) визначено під час компіляції", size=10, color=MUTED))

    f.append(fitbox(535, 168, 330, 50, "struct schedule_operation_state\n(Вкладений стан базового сендера)", size=11, fill=BG, stroke=LINE))
    f.append(fitbox(535, 226, 330, 50, "Function Object f (Замикання lambda / args)\n(Зберігається за значенням in-place)", size=11, fill=BG, stroke=LINE))
    f.append(fitbox(535, 284, 330, 50, "Receiver & Sub-Receiver зв'язки\n(Посилання без динамічного захоплення)", size=11, fill=BG, stroke=LINE))

    f.append(text(700, 380, "0 виділень у купі, максимальна кеш-локальність", size=11, color=FIELD, italic=True))

    # Загальний підпис
    f.append(text(470, 435, "Структура пам'яті: фрагментація купи при традиційних futures проти монолітного стеку P2300", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'p2300-zero-alloc-stack.svg'), W, H, *f,
           title="Порівняння структур пам'яті: динамічна купа проти монолітного стеку")

def fig_pipeline_composition():
    W, H = 940, 420
    f = []

    # Етап 1: Планувальник потоків
    f.append(fitbox(30, 120, 155, 90, "1. schedule(pool)\n(Початок на пулі)\nWorker Thread", size=11, fill=COOL, stroke=NEG, bold=True))

    f.append(arrow(185, 165, 215, 165, color=LINE, sw=2))

    # Етап 2: Синхронна обробка then
    f.append(fitbox(215, 120, 155, 90, "2. then(parse_json)\n(Трансформація)\nIn-place обчислення", size=11, fill=LIVE, stroke=FIELD, bold=True))

    f.append(arrow(370, 165, 400, 165, color=POS, sw=2))
    f.append(text(385, 150, "transfer", size=10, color=POS, bold=True))

    # Етап 3: Перенесення на GPU
    f.append(fitbox(400, 120, 160, 90, "3. continues_on(gpu)\n(Зміна контексту)\nGPU Stream Queue", size=11, fill=WARM, stroke=POS, bold=True))

    f.append(arrow(560, 165, 590, 165, color=LINE, sw=2))

    # Етап 4: Обчислення на GPU
    f.append(fitbox(590, 120, 160, 90, "4. then(gemm_kernel)\n(Обчислення на GPU)\nCUDA / Vulkan Compute", size=11, fill=LIVE, stroke=FIELD, bold=True))

    f.append(arrow(750, 165, 780, 165, color=FIELD, sw=2))

    # Етап 5: Синхронне зчитування sync_wait
    f.append(fitbox(780, 120, 130, 90, "5. sync_wait()\n(Збір результату)\nMain Thread", size=11, fill=FILL, stroke=LINE, bold=True))

    # Хронологічна шкала внизу
    f.append(line(50, 290, 890, 290, color=LINE, sw=1.5))
    f.append(arrow(870, 290, 900, 290, color=LINE, sw=1.5))
    f.append(text(470, 315, "Декларативний потік керування від ініціалізації до отримання результату", size=11, color=MUTED))

    f.append(circle(107, 290, 5, fill=NEG, stroke=LINE))
    f.append(text(107, 275, "CPU Pool", size=10, color=NEG, bold=True))

    f.append(circle(480, 290, 5, fill=POS, stroke=LINE))
    f.append(text(480, 275, "GPU Driver Context", size=10, color=POS, bold=True))

    f.append(circle(845, 290, 5, fill=INK, stroke=LINE))
    f.append(text(845, 275, "Main Thread", size=10, color=INK, bold=True))

    f.append(text(470, 380, "Ланцюжок виразів P2300: декларативне перемикання між гетерогенними обчислювальними вузлами", size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, 'p2300-pipeline-composition.svg'), W, H, *f,
           title="Асинхронний конвеєр P2300 та перемикання контекстів")

if __name__ == '__main__':
    fig_triad_lifecycle()
    fig_zero_alloc_stack()
    fig_pipeline_composition()
    print("Figures generated successfully.")
