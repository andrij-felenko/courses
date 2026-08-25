# -*- coding: utf-8 -*-
"""Фігури до теми «Протитиск у локальних системах (Backpressure)».
Запуск: python figs.py  → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори ролей
PROD_FILL  = "#eaf2fd"
PROD_LINE  = "#2457d6"
CONS_FILL  = "#eafaf1"
CONS_LINE  = "#27ae60"
QUEUE_FILL = "#fef5e7"
QUEUE_LINE = "#d35400"
FAIL_FILL  = "#fdecea"
FAIL_LINE  = "#c0392b"
WARN_FILL  = "#fff6e0"
WARN_LINE  = "#caa24a"

def boxlabel(f, x, y, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=12, sw=1.5, rx=6):
    """Прямокутник із підписом по центру; багаторядковий через список або \\n."""
    if isinstance(s, str) and "\n" in s:
        s = s.split("\n")
    if isinstance(s, list):
        f.append(fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke, sw=sw, color=tcol, rx=rx))
        return
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx))
    fs = fit_font(s, w - 14, size, bold=True)
    f.append(text(x + w / 2, y + h / 2 + fs * 0.35, s, size=fs, color=tcol, bold=True))

def note(f, cx, y, w, lines, fill=WARN_FILL, stroke=WARN_LINE, size=11):
    """Рамка-висновок знизу фігури."""
    f.append(fitbox(cx - w / 2, y, w, 18 + size * 1.35 * len(lines), lines,
                    size=size, fill=fill, stroke=stroke))


# ── 1. Чотири стратегії реакції на перевантаження ────────────────────────────
def fig_backpressure_strategies():
    W, H = 940, 520
    f = [text(W / 2, 28, "Стратегії реакції на переповнення буфера в системі", size=16, bold=True)]
    f.append(text(W / 2, 48, "Дисбаланс швидкостей (Виробник > Споживач) вимагає свідомого архітектурного вибору",
                  size=11, color=MUTED, italic=True))

    col_w = 210
    col_gap = 18
    start_x = 24
    card_h = 390
    card_y = 68

    # 1. Необмежена черга (Катастрофа)
    x1 = start_x
    f.append(rect(x1, card_y, col_w, card_h, fill="#fffaf9", stroke=FAIL_LINE, sw=1.6, rx=8))
    f.append(text(x1 + col_w / 2, card_y + 24, "1. Необмежена черга", size=12, color=FAIL_LINE, bold=True))
    f.append(text(x1 + col_w / 2, card_y + 40, "(Unbounded Queue)", size=10, color=MUTED))
    boxlabel(f, x1 + 15, card_y + 55, col_w - 30, 42, ["Виробник: 100 тис/с", "Безперервний push"], fill=PROD_FILL, stroke=PROD_LINE, size=10)
    f.append(arrow(x1 + col_w / 2, card_y + 102, x1 + col_w / 2, card_y + 128, color=LINE, sw=1.5))
    boxlabel(f, x1 + 15, card_y + 130, col_w - 30, 95, ["Буфер: std::queue", "Пам'ять: +70 МБ/с", "Розмір: нескінченний", "Затримка: зростає"], fill=FAIL_FILL, stroke=FAIL_LINE, size=10)
    f.append(arrow(x1 + col_w / 2, card_y + 230, x1 + col_w / 2, card_y + 256, color=LINE, sw=1.5))
    boxlabel(f, x1 + 15, card_y + 258, col_w - 30, 42, ["Споживач: 30 тис/с", "Не встигає"], fill=CONS_FILL, stroke=CONS_LINE, size=10)
    boxlabel(f, x1 + 12, card_y + 315, col_w - 24, 60, ["Наслідок:", "OOM Killer вбиває процес;", "втрата всіх даних у черзі"], fill="#fdecea", stroke=FAIL_LINE, tcol=FAIL_LINE, size=9.5)

    # 2. Блокування джерела
    x2 = x1 + col_w + col_gap
    f.append(rect(x2, card_y, col_w, card_h, fill="#f8faff", stroke=PROD_LINE, sw=1.6, rx=8))
    f.append(text(x2 + col_w / 2, card_y + 24, "2. Блокування джерела", size=12, color=PROD_LINE, bold=True))
    f.append(text(x2 + col_w / 2, card_y + 40, "(Blocking / Push-back)", size=10, color=MUTED))
    boxlabel(f, x2 + 15, card_y + 55, col_w - 30, 42, ["Виробник блокується", "на cond_wait / write()"], fill=PROD_FILL, stroke=PROD_LINE, size=10)
    f.append(arrow(x2 + col_w / 2, card_y + 102, x2 + col_w / 2, card_y + 128, color=LINE, sw=1.5))
    boxlabel(f, x2 + 15, card_y + 130, col_w - 30, 95, ["Обмежений буфер", "Ємність N = 1000", "Пам'ять: стабільна", "Затримка: обмежена"], fill=QUEUE_FILL, stroke=QUEUE_LINE, size=10)
    f.append(arrow(x2 + col_w / 2, card_y + 230, x2 + col_w / 2, card_y + 256, color=LINE, sw=1.5))
    boxlabel(f, x2 + 15, card_y + 258, col_w - 30, 42, ["Споживач звільняє місце", "і будить виробника"], fill=CONS_FILL, stroke=CONS_LINE, size=10)
    boxlabel(f, x2 + 12, card_y + 315, col_w - 24, 60, ["Властивість:", "Нульова втрата даних;", "швидкість вирівнюється", "за найповільнішим вузлом"], fill="#ebf5fb", stroke=PROD_LINE, tcol=PROD_LINE, size=9.5)

    # 3. Відкидання даних
    x3 = x2 + col_w + col_gap
    f.append(rect(x3, card_y, col_w, card_h, fill="#fffdfa", stroke=WARN_LINE, sw=1.6, rx=8))
    f.append(text(x3 + col_w / 2, card_y + 24, "3. Скидання даних", size=12, color=WARN_LINE, bold=True))
    f.append(text(x3 + col_w / 2, card_y + 40, "(Dropping / Shedding)", size=10, color=MUTED))
    boxlabel(f, x3 + 15, card_y + 55, col_w - 30, 42, ["Виробник працює без", "синхронних пауз"], fill=PROD_FILL, stroke=PROD_LINE, size=10)
    f.append(arrow(x3 + col_w / 2, card_y + 102, x3 + col_w / 2, card_y + 128, color=LINE, sw=1.5))
    boxlabel(f, x3 + 15, card_y + 130, col_w - 30, 95, ["Кільцевий буфер", "Drop-Tail / Drop-Head", "Перезапис старого", "Свіжість даних"], fill=WARN_FILL, stroke=WARN_LINE, size=10)
    f.append(arrow(x3 + col_w / 2, card_y + 230, x3 + col_w / 2, card_y + 256, color=LINE, sw=1.5))
    boxlabel(f, x3 + 15, card_y + 258, col_w - 30, 42, ["Споживач читає лише", "найсвіжіші кадри"], fill=CONS_FILL, stroke=CONS_LINE, size=10)
    boxlabel(f, x3 + 12, card_y + 315, col_w - 24, 60, ["Властивість:", "Ідеально для відео/телеметрії;", "пропуск старих пакетів", "заради низької затримки"], fill="#fef9e7", stroke=WARN_LINE, tcol=WARN_LINE, size=9.5)

    # 4. Модель тягни / квоти
    x4 = x3 + col_w + col_gap
    f.append(rect(x4, card_y, col_w, card_h, fill="#fafefb", stroke=CONS_LINE, sw=1.6, rx=8))
    f.append(text(x4 + col_w / 2, card_y + 24, "4. Модель «Тягни» / Кредити", size=12, color=CONS_LINE, bold=True))
    f.append(text(x4 + col_w / 2, card_y + 40, "(Pull / Demand-driven)", size=10, color=MUTED))
    boxlabel(f, x4 + 15, card_y + 55, col_w - 30, 42, ["Виробник генерує дані", "ЛИШЕ за запитом"], fill=PROD_FILL, stroke=PROD_LINE, size=10)
    f.append(arrow(x4 + col_w / 2, card_y + 128, x4 + col_w / 2, card_y + 102, color=CONS_LINE, sw=1.5))
    boxlabel(f, x4 + 15, card_y + 130, col_w - 30, 95, ["Кредитний баланс", "Запит: request(N)", "Виробник видає ≤ N", "Буфер не переповнюється"], fill=CONS_FILL, stroke=CONS_LINE, size=10)
    f.append(arrow(x4 + col_w / 2, card_y + 230, x4 + col_w / 2, card_y + 256, color=LINE, sw=1.5))
    boxlabel(f, x4 + 15, card_y + 258, col_w - 30, 42, ["Споживач контролює", "темп надходження"], fill=CONS_FILL, stroke=CONS_LINE, size=10)
    boxlabel(f, x4 + 12, card_y + 315, col_w - 24, 60, ["Властивість:", "Повна відсутність черг;", "нульовий ризик OOM,", "зворотне керування потоком"], fill="#eafaf1", stroke=CONS_LINE, tcol=CONS_LINE, size=9.5)

    note(f, W / 2, 472, 890,
         ["Необмежена черга — це відтермінована аварія пам'яті (OOM).",
          "Стійка система обирає або блокуючий протитиск (надійність), або скидання застарілих даних (реальний час), або модель «тягни»."])

    render(os.path.join(IMG, "backpressure-strategies.svg"), W, H, *f)


# ── 2. Гістерезис водяних знаків ─────────────────────────────────────────────
def fig_watermark_hysteresis():
    W, H = 900, 460
    f = [text(W / 2, 28, "Динаміка заповнення буфера: гістерезис водяних знаків (HWM / LWM)", size=16, bold=True)]
    f.append(text(W / 2, 48, "Гістерезисна зона запобігає високочастотному деренчанню перемикань (thrashing) між блокуванням і розблокуванням",
                  size=11, color=MUTED, italic=True))

    # Графік заповнення
    gx, gy, gw, gh = 70, 80, 520, 260
    f.append(rect(gx, gy, gw, gh, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))

    # Лінії сітки та водяних знаків
    y_max = gy + 20
    y_hwm = gy + 70
    y_lwm = gy + 190
    y_zero = gy + gh - 20

    # Зона гістерезису
    f.append(rect(gx + 1, y_hwm, gw - 2, y_lwm - y_hwm, fill="#fff9e6", stroke="none"))
    f.append(line(gx, y_hwm, gx + gw, y_hwm, color=FAIL_LINE, sw=1.6, dash="5,3"))
    f.append(line(gx, y_lwm, gx + gw, y_lwm, color=CONS_LINE, sw=1.6, dash="5,3"))
    f.append(line(gx, y_max, gx + gw, y_max, color="#888888", sw=1.2, dash="3,3"))

    f.append(text(gx - 8, y_max + 4, "Ємність N (100%)", size=9.5, color=MUTED, anchor="end"))
    f.append(text(gx - 8, y_hwm + 4, "HWM (80%)", size=10, color=FAIL_LINE, anchor="end", bold=True))
    f.append(text(gx - 8, y_lwm + 4, "LWM (30%)", size=10, color=CONS_LINE, anchor="end", bold=True))
    f.append(text(gx - 8, y_zero + 4, "0", size=10, color=MUTED, anchor="end"))

    f.append(text(gx + gw - 15, y_hwm - 8, "Зупинка виробника (Pause / Block)", size=10, color=FAIL_LINE, anchor="end", bold=True))
    f.append(text(gx + gw - 15, y_lwm + 16, "Відновлення виробника (Resume / Unblock)", size=10, color=CONS_LINE, anchor="end", bold=True))

    # Крива траєкторії черги (Sawtooth curve)
    path_d = [
        f"M {gx+20} {y_zero}",
        f"L {gx+130} {y_hwm}",
        f"L {gx+250} {y_lwm}",
        f"L {gx+370} {y_hwm}",
        f"L {gx+490} {y_lwm}"
    ]
    f.append(f'<path d="{" ".join(path_d)}" fill="none" stroke="{PROD_LINE}" stroke-width="2.6"/>')

    # Точки перемикання
    f.append(circle(gx + 130, y_hwm, 5, fill=FAIL_LINE, stroke="#ffffff", sw=1.5))
    f.append(circle(gx + 250, y_lwm, 5, fill=CONS_LINE, stroke="#ffffff", sw=1.5))
    f.append(circle(gx + 370, y_hwm, 5, fill=FAIL_LINE, stroke="#ffffff", sw=1.5))
    f.append(circle(gx + 490, y_lwm, 5, fill=CONS_LINE, stroke="#ffffff", sw=1.5))

    # Підписи фаз
    f.append(text(gx + 75, gy + 165, "Наповнення", size=10, color=PROD_LINE, bold=True))
    f.append(text(gx + 75, gy + 182, "(Виробник > Споживач)", size=9.5, color=MUTED))

    f.append(text(gx + 190, gy + 120, "Дренаж (Drain)", size=10, color=CONS_LINE, bold=True))
    f.append(text(gx + 190, gy + 137, "(Виробник спить)", size=9.5, color=MUTED))

    # Справа: блок пояснення структури кільцевого буфера
    rx = 620
    f.append(rect(rx, gy, 245, gh, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    f.append(text(rx + 122, gy + 24, "Структура кільцевого буфера", size=11.5, bold=True))

    boxlabel(f, rx + 15, gy + 45, 215, 34, "Head (Споживач читає)", fill=CONS_FILL, stroke=CONS_LINE, size=10)
    boxlabel(f, rx + 15, gy + 88, 215, 34, "Tail (Виробник пише)", fill=PROD_FILL, stroke=PROD_LINE, size=10)
    boxlabel(f, rx + 15, gy + 131, 215, 42, ["Заповнення:", "occupancy = (tail - head) & mask"], fill=FILL, stroke=LINE, size=9.5)
    boxlabel(f, rx + 15, gy + 182, 215, 62, ["Правило HWM:", "occupancy ≥ 80% → pause", "Правило LWM:", "occupancy ≤ 30% → resume"], fill=WARN_FILL, stroke=WARN_LINE, size=9.5)

    note(f, W / 2, 365, 830,
         ["Без LWM (якщо будити джерело одразу при HWM - 1) потік прокидається на кожне вилучене повідомлення —",
          "це генерує тисячі непотрібних перемикань контексту ядра (context switches) та інвалідацій процесорного кешу.",
          "Гістерезис гарантує пакетну обробку даних і стабільну роботу планувальника."])

    render(os.path.join(IMG, "watermark-hysteresis.svg"), W, H, *f)


# ── 3. Асинхронний протитиск у циклі подій ────────────────────────────────────
def fig_event_loop_backpressure():
    W, H = 920, 480
    f = [text(W / 2, 28, "Асинхронний протитиск у циклі подій (Reactor / epoll / Event Loop)", size=16, bold=True)]
    f.append(text(W / 2, 48, "Керування масками дескрипторів EPOLLIN / EPOLLOUT без блокування робочого потоку",
                  size=11, color=MUTED, italic=True))

    # Схема 3 вузлів: Вхідний сокет -> Локальний буфер черги -> Вихідний сокет
    bx, by = 50, 80
    node_w, node_h = 240, 265

    # 1. Вхідне джерело (Source Socket)
    f.append(rect(bx, by, node_w, node_h, fill=PROD_FILL, stroke=PROD_LINE, sw=1.6, rx=8))
    f.append(text(bx + node_w / 2, by + 24, "Вхідний дескриптор", size=12, color=PROD_LINE, bold=True))
    f.append(text(bx + node_w / 2, by + 40, "(Source Socket / fd_in)", size=10, color=MUTED))

    boxlabel(f, bx + 15, by + 58, node_w - 30, 40, ["epoll_ctl(EPOLL_CTL_MOD)", "Маска: EPOLLIN"], fill="#ffffff", stroke=PROD_LINE, size=9.5)
    boxlabel(f, bx + 15, by + 108, node_w - 30, 52, ["Реакція на переповнення:", "Зняти EPOLLIN з fd_in;", "ядро перестає будити цикл"], fill=FAIL_FILL, stroke=FAIL_LINE, size=9.5)
    boxlabel(f, bx + 15, by + 170, node_w - 30, 52, ["Реакція на дренаж (LWM):", "Повернути EPOLLIN;", "відновити читання байтів"], fill=CONS_FILL, stroke=CONS_LINE, size=9.5)
    f.append(text(bx + node_w / 2, by + 246, "Ядро затримує TCP вікно (Zero-Window)", size=9.5, color=MUTED, italic=True))

    # Стрілка 1 -> 2
    f.append(arrow(bx + node_w, by + 120, bx + node_w + 50, by + 120, color=LINE, sw=1.8))
    f.append(text(bx + node_w + 25, by + 110, "read()", size=10, color=MUTED, bold=True))

    # 2. Локальний буфер користувацького простору (User-space Buffer)
    bx2 = bx + node_w + 50
    f.append(rect(bx2, by, node_w, node_h, fill=QUEUE_FILL, stroke=QUEUE_LINE, sw=1.6, rx=8))
    f.append(text(bx2 + node_w / 2, by + 24, "Буфер застосунку", size=12, color=QUEUE_LINE, bold=True))
    f.append(text(bx2 + node_w / 2, by + 40, "(User-space Stream Queue)", size=10, color=MUTED))

    boxlabel(f, bx2 + 15, by + 58, node_w - 30, 40, ["write(chunk) -> false", "Буфер досяг HWM (64 KB)"], fill=FAIL_FILL, stroke=FAIL_LINE, size=9.5)
    boxlabel(f, bx2 + 15, by + 108, node_w - 30, 52, ["Сигнал протитиску:", "Джерело призупиняється", "stream.pause()"], fill="#ffffff", stroke=QUEUE_LINE, size=9.5)
    boxlabel(f, bx2 + 15, by + 170, node_w - 30, 52, ["Подія 'drain':", "Буфер спорожнів < LWM", "stream.resume()"], fill="#ffffff", stroke=QUEUE_LINE, size=9.5)
    f.append(text(bx2 + node_w / 2, by + 246, "Пам'ять процесу під строгим контролем", size=9.5, color=MUTED, italic=True))

    # Стрілка 2 -> 3
    f.append(arrow(bx2 + node_w, by + 120, bx2 + node_w + 50, by + 120, color=LINE, sw=1.8))
    f.append(text(bx2 + node_w + 25, by + 110, "write()", size=10, color=MUTED, bold=True))

    # 3. Вихідний дескриптор (Sink Socket)
    bx3 = bx2 + node_w + 50
    f.append(rect(bx3, by, node_w, node_h, fill=CONS_FILL, stroke=CONS_LINE, sw=1.6, rx=8))
    f.append(text(bx3 + node_w / 2, by + 24, "Вихідний дескриптор", size=12, color=CONS_LINE, bold=True))
    f.append(text(bx3 + node_w / 2, by + 40, "(Sink Socket / fd_out)", size=10, color=MUTED))

    boxlabel(f, bx3 + 15, by + 58, node_w - 30, 40, ["write() повертає EAGAIN", "Буфер сокета ядра повний"], fill=FAIL_FILL, stroke=FAIL_LINE, size=9.5)
    boxlabel(f, bx3 + 15, by + 108, node_w - 30, 52, ["Реєстрація EPOLLOUT:", "Чекати готовності сокета", "на запис нових байтів"], fill="#ffffff", stroke=CONS_LINE, size=9.5)
    boxlabel(f, bx3 + 15, by + 170, node_w - 30, 52, ["Скидання даних у мережу:", "Видалити EPOLLOUT після", "повного спустошення черги"], fill="#ffffff", stroke=CONS_LINE, size=9.5)
    f.append(text(bx3 + node_w / 2, by + 246, "Асинхронне виштовхування без зависання", size=9.5, color=MUTED, italic=True))

    # Зворотна пунктирна стрілка протитиску
    f.append(line(bx3 + 20, by + node_h - 40, bx + node_w - 20, by + node_h - 40, color=FAIL_LINE, sw=1.8, dash="6,4"))
    f.append(arrow(bx + node_w - 20, by + node_h - 40, bx + node_w - 45, by + node_h - 40, color=FAIL_LINE, sw=1.8))
    f.append(text(W / 2, by + node_h - 26, "Ланцюг зворотного протитиску (Backpressure Chain)", size=10.5, color=FAIL_LINE, bold=True))

    note(f, W / 2, 380, 840,
         ["В асинхронних однопотокових циклах (Node.js, Tokio, libuv, epoll) блокувати потік викликом sleep() заборонено.",
          "Протитиск реалізується через маніпуляцію прапорцями подій ядра (EPOLLIN/EPOLLOUT) та подію вичерпання черги (drain)."])

    render(os.path.join(IMG, "event-loop-backpressure.svg"), W, H, *f)


# ── 4. Порівняння моделей Push, Pull та Hybrid (Credit) ──────────────────────
def fig_push_vs_pull_flow():
    W, H = 920, 480
    f = [text(W / 2, 28, "Порівняння моделей передачі: «Штовхай» (Push), «Тягни» (Pull) та Кредити", size=16, bold=True)]
    f.append(text(W / 2, 48, "Розподіл контролю за швидкістю передачі між джерелом та приймачем даних",
                  size=11, color=MUTED, italic=True))

    col_w = 265
    col_gap = 25
    start_x = 35
    card_h = 345
    card_y = 70

    # 1. Push
    x1 = start_x
    f.append(rect(x1, card_y, col_w, card_h, fill="#fffaf9", stroke=FAIL_LINE, sw=1.6, rx=8))
    f.append(text(x1 + col_w / 2, card_y + 24, "Модель «Штовхай» (Push)", size=12, color=FAIL_LINE, bold=True))
    f.append(text(x1 + col_w / 2, card_y + 40, "Ініціатор — Виробник", size=10, color=MUTED))

    boxlabel(f, x1 + 15, card_y + 55, col_w - 30, 34, "Виробник: emit(data)", fill=PROD_FILL, stroke=PROD_LINE, size=10)
    f.append(arrow(x1 + col_w / 2, card_y + 92, x1 + col_w / 2, card_y + 115, color=PROD_LINE, sw=1.6))
    boxlabel(f, x1 + 15, card_y + 118, col_w - 30, 34, "Черга / Буфер пам'яті", fill=QUEUE_FILL, stroke=QUEUE_LINE, size=10)
    f.append(arrow(x1 + col_w / 2, card_y + 155, x1 + col_w / 2, card_y + 178, color=LINE, sw=1.6))
    boxlabel(f, x1 + 15, card_y + 180, col_w - 30, 34, "Споживач: onData(data)", fill=CONS_FILL, stroke=CONS_LINE, size=10)

    # Пунктирна стрілка зворотного тиску
    f.append(line(x1 + 30, card_y + 218, x1 + 30, card_y + 85, color=FAIL_LINE, sw=1.6, dash="4,3"))
    f.append(arrow(x1 + 30, card_y + 85, x1 + 30, card_y + 60, color=FAIL_LINE, sw=1.6))
    f.append(text(x1 + 45, card_y + 140, "Сигнал паузи", size=9, color=FAIL_LINE, anchor="start", bold=True))

    boxlabel(f, x1 + 12, card_y + 235, col_w - 24, 90,
             ["Властивості:", "• Потребує великих буферів", "• Ризик переповнення OOM", "• Складні канали сигналізації", "• Висока пропускна здатність"],
             fill="#ffffff", stroke=FAIL_LINE, size=9.5)

    # 2. Pull
    x2 = x1 + col_w + col_gap
    f.append(rect(x2, card_y, col_w, card_h, fill="#fafefb", stroke=CONS_LINE, sw=1.6, rx=8))
    f.append(text(x2 + col_w / 2, card_y + 24, "Модель «Тягни» (Pull)", size=12, color=CONS_LINE, bold=True))
    f.append(text(x2 + col_w / 2, card_y + 40, "Ініціатор — Споживач (Ітератор)", size=10, color=MUTED))

    boxlabel(f, x2 + 15, card_y + 55, col_w - 30, 34, "Споживач: next() / read()", fill=CONS_FILL, stroke=CONS_LINE, size=10)
    f.append(arrow(x2 + col_w / 2, card_y + 92, x2 + col_w / 2, card_y + 115, color=CONS_LINE, sw=1.6))
    boxlabel(f, x2 + 15, card_y + 118, col_w - 30, 34, "Синхронний генератор", fill=FILL, stroke=LINE, size=10)
    f.append(arrow(x2 + col_w / 2, card_y + 155, x2 + col_w / 2, card_y + 178, color=PROD_LINE, sw=1.6))
    boxlabel(f, x2 + 15, card_y + 180, col_w - 30, 34, "Виробник: return value", fill=PROD_FILL, stroke=PROD_LINE, size=10)

    boxlabel(f, x2 + 12, card_y + 235, col_w - 24, 90,
             ["Властивості:", "• Буфери непотрібні (0 байтів)", "• Фізична неможливість OOM", "• Простій виробника під час", "  обчислень споживача", "• Нижча пропускна здатність"],
             fill="#ffffff", stroke=CONS_LINE, size=9.5)

    # 3. Hybrid / Credit
    x3 = x2 + col_w + col_gap
    f.append(rect(x3, card_y, col_w, card_h, fill="#f8faff", stroke=PROD_LINE, sw=1.6, rx=8))
    f.append(text(x3 + col_w / 2, card_y + 24, "Гібрид: Кредити (Demand)", size=12, color=PROD_LINE, bold=True))
    f.append(text(x3 + col_w / 2, card_y + 40, "Динамічний баланс (Reactive)", size=10, color=MUTED))

    boxlabel(f, x3 + 15, card_y + 55, col_w - 30, 34, "Споживач: request(N)", fill=CONS_FILL, stroke=CONS_LINE, size=10)
    f.append(arrow(x3 + col_w / 2, card_y + 92, x3 + col_w / 2, card_y + 115, color=CONS_LINE, sw=1.6))
    boxlabel(f, x3 + 15, card_y + 118, col_w - 30, 34, "Кредитний лічильник: N", fill=WARN_FILL, stroke=WARN_LINE, size=10)
    f.append(arrow(x3 + col_w / 2, card_y + 155, x3 + col_w / 2, card_y + 178, color=PROD_LINE, sw=1.6))
    boxlabel(f, x3 + 15, card_y + 180, col_w - 30, 34, "Виробник: emit N елементів", fill=PROD_FILL, stroke=PROD_LINE, size=10)

    boxlabel(f, x3 + 12, card_y + 235, col_w - 24, 90,
             ["Властивості:", "• Пакетизація передачі (batch)", "• Максимальна швидкість CPU", "• Гарантований ліміт пам'яті", "• Спільний стандарт реактивності"],
             fill="#ffffff", stroke=PROD_LINE, size=9.5)

    note(f, W / 2, 430, 850,
         ["Модель «Тягни» ідеальна для послідовних локальних ітераторів, але втрачає продуктивність у конкурентних пайплайнах.",
          "Кредитна модель (Reactive Streams / Demand) поєднує безпеку Pull з високою швидкістю пакетного Push."])

    render(os.path.join(IMG, "push-vs-pull-flow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_backpressure_strategies()
    fig_watermark_hysteresis()
    fig_event_loop_backpressure()
    fig_push_vs_pull_flow()
    print("OK: all figures generated")
