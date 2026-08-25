# -*- coding: utf-8 -*-
"""Фігури до теми «Без замків» (Lock-Free).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Додаткові кольори
CLR_TH1 = NEG       # потік 1
CLR_TH2 = POS       # потік 2 / конфлікт
CLR_OK  = FIELD     # успіх / safe
CLR_WARN = "#c0392b"
CLR_MEM = "#4b5563"
BG_CARD = "#f9fafb"

def boxlabel(f, x, y, w, h, s, fill=FILL, stroke=LINE, tcol=INK, size=12, sw=1.5):
    """Прямокутник із підписом по центру; багаторядковий через \\n."""
    if "\n" in s:
        f.append(fitbox(x, y, w, h, s.split("\n"), size=size, fill=fill,
                        stroke=stroke, sw=sw, color=tcol, bold=True, pad=6))
        return
    f.append(rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=6))
    fs = fit_font(s, w - 12, size, bold=True)
    f.append(text(x + w / 2, y + h / 2 + fs * 0.35, s, size=fs, color=tcol, bold=True))


def note(f, cx, y, w, lines, fill="#fff8e6", stroke="#caa24a", size=11):
    """Рамка-висновок знизу фігури."""
    f.append(fitbox(cx - w / 2, y, w, 18 + size * 1.3 * len(lines), lines,
                    size=size, fill=fill, stroke=stroke))


# ── 1. Проблема блокувань: зупинка під замком паралізує всіх ─────────────────
def fig_lock_thread_stall():
    W, H = 880, 420
    f = [text(W / 2, 28, "Блокування: коли потік зупиняється під замком, уся черга замерзає",
              size=16, bold=True)]
    f.append(text(W / 2, 48, "Потік A захопив м'ютекс і був витіснений ОС (context switch) — Потік B і C безпорадно блокуються",
                  size=11, color=MUTED, italic=True))

    yA = 110
    f.append(text(80, yA + 16, "Потік A (Low Pri)", size=11, color=CLR_TH1, bold=True, anchor="start"))
    boxlabel(f, 220, yA, 130, 32, "Lock(mutex) OK", fill="#eaf0fd", stroke=CLR_TH1, size=11, tcol=CLR_TH1)
    boxlabel(f, 370, yA, 240, 32, "⚡ ВИТІСНЕННЯ ОС (сон 10 мс)", fill="#fdecea", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    boxlabel(f, 630, yA, 140, 32, "Unlock(mutex)", fill="#eaf0fd", stroke=CLR_TH1, size=11, tcol=CLR_TH1)
    f.append(arrow(350, yA + 16, 370, yA + 16, color=CLR_TH1))
    f.append(arrow(610, yA + 16, 630, yA + 16, color=CLR_TH1))

    yB = 200
    f.append(text(80, yB + 16, "Потік B (Audio RT)", size=11, color=CLR_TH2, bold=True, anchor="start"))
    boxlabel(f, 290, yB, 110, 32, "Обчислення", fill="#f4f6f8", stroke=LINE, size=11)
    boxlabel(f, 420, yB, 220, 32, "❌ Блокується на м'ютексі...", fill="#fbecec", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    boxlabel(f, 660, yB, 140, 32, "Пропуск дедлайну!", fill="#fdecea", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    f.append(arrow(400, yB + 16, 420, yB + 16, color=CLR_TH2))
    f.append(arrow(640, yB + 16, 660, yB + 16, color=CLR_WARN))

    yC = 280
    f.append(text(80, yC + 16, "Потік C (Core 2)", size=11, color=INK, bold=True, anchor="start"))
    boxlabel(f, 320, yC, 110, 32, "Обчислення", fill="#f4f6f8", stroke=LINE, size=11)
    boxlabel(f, 450, yC, 190, 32, "❌ Чекає у черзі futex", fill="#fbecec", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    f.append(arrow(430, yC + 16, 450, yC + 16, color=LINE))

    f.append(line(370, yA + 32, 370, yC + 35, color=CLR_WARN, sw=1.5, dash="3,3"))
    f.append(line(630, yA + 32, 630, yC + 35, color=CLR_OK, sw=1.5, dash="3,3"))

    note(f, W / 2, 350, 780,
         ["Замки передають контроль над прогресом усієї системи ОДНОМУ потоку.",
          "Якщо потік засинає, зазнає page fault або гине — усі залежні потоки зависають разом із ним."])
    render(os.path.join(IMG, "lock-thread-stall.svg"), W, H, *f)


# ── 2. Механізм Compare-And-Swap (CAS) ──────────────────────────────────────
def fig_cas_step_mechanism():
    W, H = 880, 400
    f = [text(W / 2, 28, "Принцип дії Compare-And-Swap (CAS): неподільна операція в кремнії",
              size=16, bold=True)]
    f.append(text(W / 2, 48, "Апаратна перевірка: якщо значення в пам'яті дорівнює очікуваному — записуємо нове. Інакше відхиляємо.",
                  size=11, color=MUTED, italic=True))

    # Ліва колонка: УСПІХ
    f.append(text(230, 85, "Сценарій 1: Успіх (Match)", size=13, bold=True, color=CLR_OK))
    boxlabel(f, 80, 110, 300, 36, "Пам'ять [ptr]: 42  |  Expected: 42", fill="#f4f6f8", stroke=LINE, size=11)
    boxlabel(f, 80, 170, 300, 44, "Порівняння [ptr] == Expected (42 == 42) -> ТАК\n[ptr] := Desired (99)", fill="#eaf7ed", stroke=CLR_OK, size=11, tcol=CLR_OK)
    boxlabel(f, 80, 240, 300, 36, "Повертає: TRUE (пам'ять оновлено на 99)", fill="#eaf7ed", stroke=CLR_OK, size=11, tcol=CLR_OK)
    f.append(arrow(230, 146, 230, 170, color=CLR_OK))
    f.append(arrow(230, 214, 230, 240, color=CLR_OK))

    # Розділювач
    f.append(line(W / 2, 75, W / 2, 310, color="#d1d5db", sw=1.5, dash="4,4"))

    # Права колонка: НЕВДАЧА
    f.append(text(650, 85, "Сценарій 2: Конфлікт (Mismatch)", size=13, bold=True, color=CLR_WARN))
    boxlabel(f, 500, 110, 300, 36, "Пам'ять [ptr]: 50 (хтось змінив!) | Expected: 42", fill="#f4f6f8", stroke=LINE, size=11)
    boxlabel(f, 500, 170, 300, 44, "Порівняння [ptr] == Expected (50 != 42) -> НІ\nЗапис блокується кремнієм!", fill="#fdecea", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    boxlabel(f, 500, 240, 300, 36, "Повертає: FALSE | Expected оновлено на 50", fill="#fdecea", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    f.append(arrow(650, 146, 650, 170, color=CLR_WARN))
    f.append(arrow(650, 214, 650, 240, color=CLR_WARN))

    note(f, W / 2, 330, 780,
         ["CAS виконується на шині процесора як одна неподільна дія (x86: LOCK CMPXCHG, ARM: LDREX/STREX).",
          "Жоден інший потік не може вклинитися між перевіркою та записом."])
    render(os.path.join(IMG, "cas-step-mechanism.svg"), W, H, *f)


# ── 3. Цикл CAS (CAS retry loop) ─────────────────────────────────────────────
def fig_cas_retry_loop():
    W, H = 880, 420
    f = [text(W / 2, 28, "Класичний цикл оновлення на базі CAS (Optimistic Retry Loop)",
              size=16, bold=True)]
    f.append(text(W / 2, 48, "Оптимістична спроба: читаємо стан, рахуємо зміну локально, намагаємося зафіксувати через CAS",
                  size=11, color=MUTED, italic=True))

    boxlabel(f, 320, 80, 240, 36, "1. Читаємо поточний стан (old)", fill="#f4f6f8", stroke=LINE, size=11)
    boxlabel(f, 320, 145, 240, 36, "2. Рахуємо новий стан (new) у регістрах", fill="#f4f6f8", stroke=LINE, size=11)
    boxlabel(f, 290, 210, 300, 44, "3. CAS(&target, expected=old, desired=new)\n[Атомарна спроба запису]", fill="#eaf0fd", stroke=CLR_TH1, size=11, tcol=CLR_TH1)

    f.append(arrow(440, 116, 440, 145, color=LINE))
    f.append(arrow(440, 181, 440, 210, color=LINE))

    # Гілка успіху
    boxlabel(f, 120, 290, 220, 40, "УСПІХ (true):\nДію зафіксовано, вихід", fill="#eaf7ed", stroke=CLR_OK, size=11, tcol=CLR_OK)
    f.append(arrow(340, 254, 230, 290, color=CLR_OK))
    f.append(text(255, 265, "Конфлікту не було", size=9.5, color=CLR_OK, bold=True))

    # Гілка невдачі (retry)
    boxlabel(f, 540, 290, 240, 40, "НЕВДАЧА (false):\nХтось встиг змінити target раніше", fill="#fdecea", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    f.append(arrow(540, 254, 630, 290, color=CLR_WARN))
    f.append(text(625, 265, "Конфлікт оновлення", size=9.5, color=CLR_WARN, bold=True))

    # Петля повернення на крок 1
    f.append(line(780, 310, 820, 310, color=CLR_WARN, sw=1.5))
    f.append(line(820, 310, 820, 98, color=CLR_WARN, sw=1.5))
    f.append(arrow(820, 98, 560, 98, color=CLR_WARN))
    f.append(text(825, 200, "Повтор зі свіжим станом", size=9.5, color=CLR_WARN, anchor="start", bold=True))

    note(f, W / 2, 360, 780,
         ["Невдача в CAS означає, що ЯКИЙСЬ ІНШИЙ потік успішно завершив свою роботу.",
          "Отже, вся система гарантовано робить поступ (lock-free прогрес)."])
    render(os.path.join(IMG, "cas-retry-loop.svg"), W, H, *f)


# ── 4. Стек Трайбера (Treiber Stack Push / Pop) ──────────────────────────────
def fig_treiber_stack_race():
    W, H = 880, 420
    f = [text(W / 2, 28, "Стек Трайбера: конкурентне додавання вузла (Push) через CAS",
              size=16, bold=True)]
    f.append(text(W / 2, 48, "Потік готує новий вузол локально, скеровує його next на поточний Head і атомарно перемикає Head",
                  size=11, color=MUTED, italic=True))

    # Початковий стан стека
    f.append(text(160, 80, "Початковий стек:", size=12, bold=True))
    boxlabel(f, 60, 110, 90, 34, "Head", fill="#eaf0fd", stroke=CLR_TH1, size=11)
    boxlabel(f, 190, 110, 90, 34, "Node A", fill="#f4f6f8", stroke=LINE, size=11)
    boxlabel(f, 320, 110, 90, 34, "Node B", fill="#f4f6f8", stroke=LINE, size=11)
    f.append(arrow(150, 127, 190, 127, color=CLR_TH1))
    f.append(arrow(280, 127, 320, 127, color=LINE))

    # Новий вузол локально
    f.append(text(650, 80, "Новий вузол (локально у Потоку 1):", size=12, bold=True, color=CLR_OK))
    boxlabel(f, 570, 110, 110, 34, "New Node X", fill="#eaf7ed", stroke=CLR_OK, size=11, tcol=CLR_OK)
    f.append(text(680, 165, "1. Node X->next = Node A (старий Head)", size=10.5, color=INK, anchor="end"))
    f.append(arrow(570, 127, 280, 127, color=CLR_OK))

    # Дія CAS
    f.append(line(50, 200, 830, 200, color="#e5e7eb", sw=1.5, dash="4,4"))
    f.append(text(W / 2, 225, "2. CAS(&Head, expected=Node A, desired=Node X)", size=12, bold=True, color=CLR_TH1))

    # Результат після успішного CAS
    boxlabel(f, 100, 260, 90, 34, "Head", fill="#eaf0fd", stroke=CLR_TH1, size=11)
    boxlabel(f, 250, 260, 110, 34, "Node X", fill="#eaf7ed", stroke=CLR_OK, size=11, tcol=CLR_OK)
    boxlabel(f, 420, 260, 90, 34, "Node A", fill="#f4f6f8", stroke=LINE, size=11)
    boxlabel(f, 570, 260, 90, 34, "Node B", fill="#f4f6f8", stroke=LINE, size=11)
    f.append(arrow(190, 277, 250, 277, color=CLR_OK))
    f.append(arrow(360, 277, 420, 277, color=LINE))
    f.append(arrow(510, 277, 570, 277, color=LINE))

    note(f, W / 2, 340, 780,
         ["Якщо інший потік встиг вставити свій вузол між кроками 1 і 2, Head вже не дорівнює Node A.",
          "CAS повертає false, Node X переприв'язується до нового Head, і спроба повторюється без дедлоків."])
    render(os.path.join(IMG, "treiber-stack-race.svg"), W, H, *f)


# ── 5. Проблема ABA ─────────────────────────────────────────────────────────
def fig_aba_problem():
    W, H = 880, 440
    f = [text(W / 2, 26, "Проблема ABA: зміна стану маскується повторною адресою",
              size=16, bold=True)]
    f.append(text(W / 2, 46, "Потік 1 бачить ту саму адресу 'A' і вважає, що стек не змінювався, хоча вузол 'B' уже видалено!",
                  size=11, color=MUTED, italic=True))

    # Крок 1
    y1 = 80
    f.append(text(70, y1 + 16, "Крок 1", size=11, bold=True, anchor="start"))
    boxlabel(f, 150, y1, 80, 30, "Head: A", fill="#eaf0fd", stroke=CLR_TH1, size=10.5)
    boxlabel(f, 260, y1, 70, 30, "Node A", fill="#f4f6f8", stroke=LINE, size=10.5)
    boxlabel(f, 360, y1, 70, 30, "Node B", fill="#f4f6f8", stroke=LINE, size=10.5)
    f.append(arrow(230, y1 + 15, 260, y1 + 15, color=CLR_TH1))
    f.append(arrow(330, y1 + 15, 360, y1 + 15, color=LINE))
    f.append(text(460, y1 + 18, "Потік 1 готує Pop: бачить top=A, next=B. Засинає перед CAS!", size=10, color=CLR_TH1, anchor="start"))

    # Крок 2
    y2 = 145
    f.append(text(70, y2 + 16, "Крок 2", size=11, bold=True, color=CLR_TH2, anchor="start"))
    boxlabel(f, 150, y2, 80, 30, "Head: C", fill="#fdecea", stroke=CLR_TH2, size=10.5)
    boxlabel(f, 260, y2, 70, 30, "Node C", fill="#f4f6f8", stroke=LINE, size=10.5)
    f.append(arrow(230, y2 + 15, 260, y2 + 15, color=CLR_TH2))
    f.append(text(360, y2 + 18, "Потік 2 видаляє A і B (B звільнено в купу!), додає C.", size=10, color=CLR_TH2, anchor="start"))

    # Крок 3
    y3 = 210
    f.append(text(70, y3 + 16, "Крок 3", size=11, bold=True, color=CLR_TH2, anchor="start"))
    boxlabel(f, 150, y3, 80, 30, "Head: A*", fill="#fdecea", stroke=CLR_TH2, size=10.5)
    boxlabel(f, 260, y3, 70, 30, "Node A*", fill="#fff2db", stroke="#caa24a", size=10.5)
    boxlabel(f, 360, y3, 70, 30, "Node C", fill="#f4f6f8", stroke=LINE, size=10.5)
    f.append(arrow(230, y3 + 15, 260, y3 + 15, color=CLR_TH2))
    f.append(arrow(330, y3 + 15, 360, y3 + 15, color=LINE))
    f.append(text(460, y3 + 18, "Алокатор виділяє для нового вузла ТУ САМУ адресу A! Стек: [A* -> C].", size=10, color=INK, anchor="start"))

    # Крок 4 (Катастрофа)
    y4 = 280
    f.append(text(70, y4 + 16, "Крок 4", size=11, bold=True, color=CLR_WARN, anchor="start"))
    boxlabel(f, 150, y4, 80, 30, "Head: B ❌", fill="#fdecea", stroke=CLR_WARN, size=10.5, tcol=CLR_WARN)
    boxlabel(f, 260, y4, 90, 30, "Node B (Trash!)", fill="#fdecea", stroke=CLR_WARN, size=10, tcol=CLR_WARN)
    f.append(arrow(230, y4 + 15, 260, y4 + 15, color=CLR_WARN))
    f.append(text(380, y4 + 18, "Потік 1 прокидається: CAS(Head, A, B) успішний! Head стає B (сміття/краш). Node C загублено!", size=10, color=CLR_WARN, anchor="start", bold=True))

    note(f, W / 2, 365, 780,
         ["Розв'язання ABA: Tagged Pointers (лічильник генерації разом із покажчиком) або",
          "безпечне керування пам'яттю (Hazard Pointers / Epoch-Based Reclamation)."])
    render(os.path.join(IMG, "aba-problem.svg"), W, H, *f)


# ── 6. Безпечне звільнення пам'яті (Hazard Pointers) ────────────────────────
def fig_hazard_pointers():
    W, H = 880, 420
    f = [text(W / 2, 28, "Безпечне звільнення пам'яті: механізм Hazard Pointers",
              size=16, bold=True)]
    f.append(text(W / 2, 48, "Потік оголошує захищений покажчик перед читанням; звільнення видалених вузлів відкладається",
                  size=11, color=MUTED, italic=True))

    # Слот Hazard Pointer
    f.append(text(180, 85, "Глобальний масив Hazard Pointers:", size=12, bold=True, color=CLR_TH1))
    boxlabel(f, 80, 110, 200, 34, "Thread 1 HP: [ Node X ]", fill="#eaf0fd", stroke=CLR_TH1, size=11, tcol=CLR_TH1)
    boxlabel(f, 80, 155, 200, 34, "Thread 2 HP: [ nullptr ]", fill="#f4f6f8", stroke=LINE, size=11)
    f.append(text(180, 210, "Потік 1 наразі читає Node X!", size=10, color=CLR_TH1))

    # Відставлені вузли
    f.append(text(620, 85, "Список відкладеного звільнення (Retire List):", size=12, bold=True, color=CLR_WARN))
    boxlabel(f, 500, 110, 240, 34, "Retire: [ Node X ] (вилучений зі стека)", fill="#fdecea", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    boxlabel(f, 500, 155, 240, 34, "Retire: [ Node Y ] (вилучений зі стека)", fill="#fdecea", stroke=CLR_WARN, size=11)

    # Процес сканування
    f.append(line(50, 240, 830, 240, color="#e5e7eb", sw=1.5, dash="4,4"))
    f.append(text(W / 2, 265, "Фаза очищення (Reclamation Scan):", size=12, bold=True))

    boxlabel(f, 100, 290, 310, 44, "Node X: є в масиві HP (Thread 1 HP == Node X)\n-> ЗАБОРОНЕНО звільняти (чекаємо)", fill="#fdecea", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    boxlabel(f, 470, 290, 310, 44, "Node Y: відсутній у всіх HP слотах\n-> БЕЗПЕЧНО: free(Node Y)!", fill="#eaf7ed", stroke=CLR_OK, size=11, tcol=CLR_OK)

    note(f, W / 2, 360, 780,
         ["Hazard Pointers виключають помилки Use-After-Free без блокування читачів.",
          "Читач лише публікує адресу, а письменник перевіряє її перед викликом free()."])
    render(os.path.join(IMG, "hazard-pointers.svg"), W, H, *f)


# ── 7. Ієрархія гарантій поступу (Progress Guarantees) ──────────────────────
def fig_progress_guarantees():
    W, H = 880, 410
    f = [text(W / 2, 28, "Ієрархія гарантій поступу в паралельних алгоритмах (М. Герліхі)",
              size=16, bold=True)]
    f.append(text(W / 2, 48, "Від блокуючих замків до сильних гарантій реального часу: що отримує система та окремий потік",
                  size=11, color=MUTED, italic=True))

    y = 80
    h_box = 52

    # 1. Blocking
    boxlabel(f, 80, y, 160, h_box, "Блокуючі (Locks)\nМ'ютекси, спінлоки", fill="#fdecea", stroke=CLR_WARN, size=11, tcol=CLR_WARN)
    boxlabel(f, 260, y, 540, h_box, "Немає гарантій: потік під замком може зависнути або заснути,\nповністю зупинивши всіх інших учасників системи.", fill="#fdecea", stroke=CLR_WARN, size=10.5)

    # 2. Obstruction-Free
    y += 66
    boxlabel(f, 80, y, 160, h_box, "Obstruction-Free\n(Без перешкод)", fill="#fff8e6", stroke="#caa24a", size=11, tcol="#92400e")
    boxlabel(f, 260, y, 540, h_box, "Поступ одного потоку гарантовано за умови, що всі інші потоки\nтимчасово зупинилися (немає конкуренції за ресурс).", fill="#fff8e6", stroke="#caa24a", size=10.5)

    # 3. Lock-Free
    y += 66
    boxlabel(f, 80, y, 160, h_box, "Lock-Free\n(Без блокувань)", fill="#eaf0fd", stroke=CLR_TH1, size=11, tcol=CLR_TH1)
    boxlabel(f, 260, y, 540, h_box, "Системний поступ: щонайменше один потік завжди завершує операцію\nза скінченну кількість кроків. Окремі потоки можуть голодувати.", fill="#eaf0fd", stroke=CLR_TH1, size=10.5)

    # 4. Wait-Free
    y += 66
    boxlabel(f, 80, y, 160, h_box, "Wait-Free\n(Без очікування)", fill="#eaf7ed", stroke=CLR_OK, size=11, tcol=CLR_OK)
    boxlabel(f, 260, y, 540, h_box, "Індивідуальний поступ: КОЖЕН потік гарантовано завершує операцію\nза обмежену зверху кількість кроків O(1) / O(N), без повторів.", fill="#eaf7ed", stroke=CLR_OK, size=10.5, tcol=CLR_OK)

    render(os.path.join(IMG, "progress-guarantees.svg"), W, H, *f)


if __name__ == "__main__":
    fig_lock_thread_stall()
    fig_cas_step_mechanism()
    fig_cas_retry_loop()
    fig_treiber_stack_race()
    fig_aba_problem()
    fig_hazard_pointers()
    fig_progress_guarantees()
    print("Усі 7 фігур успішно згенеровано.")
