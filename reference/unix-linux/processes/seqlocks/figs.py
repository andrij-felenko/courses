# -*- coding: utf-8 -*-
"""Фігури до теми «Послідовні замки: як читати без блокування письменників»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GREEN_BG = "#e6f5ec"
RED_BG = "#fdecea"
GREY_BG = "#eef0f3"
WARM_BG = "#fff4e0"
BLUE_BG = "#eaf0fd"

# ── 1. Послідовність дій письменника та читача (Seqlock Flow) ───────────────
def fig_seqlock_flow():
    W, H = 1240, 680
    P = []

    # Заголовок та колонки
    P.append(fitbox(40, 30, 520, 50, "Письменник (Writer)", size=16, bold=True, fill=WARM_BG, stroke="#b8860b", sw=2))
    P.append(fitbox(680, 30, 520, 50, "Читач (Reader — Оптимістичний цикл)", size=16, bold=True, fill=BLUE_BG, stroke=NEG, sw=2))

    # Стовпчик Письменника
    writer_steps = [
        ("1. spin_lock(&sl->lock)", "Захоплює спінлок для відсікання інших письменників", GREY_BG, MUTED),
        ("2. write_seqcount_begin()\nseq++ (стає НЕПАРНИМ)", "Оголошує початок запису + smp_wmb()", WARM_BG, "#b8860b"),
        ("3. Оновлення даних (payload)", "Запис у структуру даних (не містить вказівників)", RED_BG, POS),
        ("4. write_seqcount_end()\nseq++ (стає ПАРНИМ)", "Оголошує завершення запису + smp_wmb()", WARM_BG, "#b8860b"),
        ("5. spin_unlock(&sl->lock)", "Звільняє спінлок для наступних письменників", GREY_BG, MUTED),
    ]

    yw = 110
    for title, desc, bg, stroke in writer_steps:
        P.append(fitbox(40, yw, 230, 64, title, size=12, bold=True, fill=bg, stroke=stroke, sw=1.8))
        P.append(fitbox(280, yw, 280, 64, desc, size=11.5, fill=BG, stroke=MUTED, sw=1))
        if yw < 430:
            P.append(arrow(155, yw + 64, 155, yw + 84, color=MUTED, sw=1.5))
        yw += 84

    # Стовпчик Читача
    reader_steps = [
        ("1. seq = read_seqbegin()", "Прочитати seq + smp_rmb(). Якщо seq непарне, чекати у циклі", BLUE_BG, NEG),
        ("2. Читання даних (payload)", "Копіювати локально всі поля структури", GREEN_BG, FIELD),
        ("3. read_seqretry(seq)?", "smp_rmb() + перевірка: чи змінився seq від початку?", BLUE_BG, NEG),
    ]

    yr = 110
    for title, desc, bg, stroke in reader_steps:
        P.append(fitbox(680, yr, 230, 64, title, size=12, bold=True, fill=bg, stroke=stroke, sw=1.8))
        P.append(fitbox(920, yr, 280, 64, desc, size=11.5, fill=BG, stroke=MUTED, sw=1))
        if yr < 270:
            P.append(arrow(795, yr + 64, 795, yr + 84, color=MUTED, sw=1.5))
        yr += 84

    # Розгалуження після перевірки read_seqretry
    P.append(arrow(795, 346, 795, 420, color=MUTED, sw=1.8))
    
    # Гілка НІ (збіг / успіх)
    P.append(fitbox(680, 420, 230, 60, "Ні (seq не змінився)\nУСПІХ", size=12.5, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))
    P.append(fitbox(920, 420, 280, 60, "Дані цілісні й консистентні.\nВихід із циклу читання.", size=11.5, fill=BG, stroke=FIELD, sw=1))

    # Гілка ТАК (конфлікт / колізія - повернення нагору)
    P.append(arrow(795, 346, 610, 346, color=POS, sw=2))
    P.append(line(610, 346, 610, 142, color=POS, sw=2))
    P.append(arrow(610, 142, 676, 142, color=POS, sw=2))
    P.append(fitbox(575, 230, 70, 50, "Так\nповтор", size=11, bold=True, fill=RED_BG, stroke=POS, sw=1.5))

    # Нижня примітка
    P.append(fitbox(40, 560, 1160, 80,
                    "Ключовий момент: Читач НЕ захоплює атомарних замків і не модифікує спільно використовувану пам'ять.\n"
                    "При колізії (письменник вклинився під час читання) читач відкидає часткові дані й повторює цикл.",
                    size=12.5, bold=True, fill=GREY_BG, stroke=MUTED, sw=1.5))

    return render(os.path.join(OUT, "seqlock-flow.svg"), W, H, *P)


# ── 2. Порівняння кеш-ліній: RWLock vs Seqlock ──────────────────────────────
def fig_cache_lines():
    W, H = 1180, 600
    P = []

    # Ліва панель: RWLock
    P.append(fitbox(40, 30, 520, 50, "Звичайний RWLock (Read-Write Spinlock)", size=15, bold=True, fill=RED_BG, stroke=POS, sw=2))
    
    P.append(fitbox(60, 100, 480, 80, 
                    "Кожен читач виконує atomic_inc() / cmpxchg()\n"
                    "Рядок кеша переходить у стан Modified (M)",
                    size=12.5, fill=GREY_BG, stroke=MUTED))
    
    # Cores for RWLock
    for i in range(3):
        cx = 80 + i * 160
        P.append(fitbox(cx, 210, 130, 60, f"Ядро CPU {i+1}\n(Читач)", size=12, bold=True, fill=RED_BG, stroke=POS, sw=1.5))
        P.append(arrow(cx + 65, 270, cx + 65, 320, color=POS, sw=2))

    P.append(fitbox(60, 320, 480, 70, 
                    "Спільна лінія кеша з замком rwlock_t\n"
                    "Постійне анулювання (Cache-Line Bouncing)!", size=13, bold=True, fill=WARM_BG, stroke="#b8860b", sw=2))

    # Права панель: Seqlock
    P.append(fitbox(620, 30, 520, 50, "Послідовний замок (Seqlock)", size=15, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))

    P.append(fitbox(640, 100, 480, 80, 
                    "Читачі лише ЧИТАЮТЬ seqcount (Zero Write Overhead)\n"
                    "Рядок кеша залишається у стані Shared (S) на всіх ядрах",
                    size=12.5, fill=GREY_BG, stroke=MUTED))

    # Cores for Seqlock
    for i in range(3):
        cx = 660 + i * 160
        P.append(fitbox(cx, 210, 130, 60, f"Ядро CPU {i+1}\n(Читач)", size=12, bold=True, fill=GREEN_BG, stroke=FIELD, sw=1.5))
        P.append(arrow(cx + 65, 320, cx + 65, 270, color=FIELD, sw=2))

    P.append(fitbox(640, 320, 480, 70, 
                    "Спільна лінія кеша з seqcount_t\n"
                    "Тиша у шині когерентності кешів!", size=13, bold=True, fill=GREEN_BG, stroke=FIELD, sw=2))

    # Порівняльний підсумок знизу
    P.append(fitbox(40, 430, 1100, 130,
                    "Результат для масштабованості системи:\n"
                    "• RWLock: Додавання читачів масштабується погано через трафік когерентності (MESI invalidation) на кожен read_lock.\n"
                    "• Seqlock: Додавання тисяч читачів має майже нульову ціну для шини пам'яті. Письменник виконує оновлення без блокування читачами.",
                    size=13, fill=GREY_BG, stroke=MUTED, sw=1.5))

    return render(os.path.join(OUT, "cache-lines-seqlock-vs-rwlock.svg"), W, H, *P)


if __name__ == "__main__":
    for f in (fig_seqlock_flow, fig_cache_lines):
        print(f())
