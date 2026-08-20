# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Колбеки → проміси → async/await»."""

import os
import sys

# Шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_evolution_paradigms():
    """1. evolution-paradigms.svg — Порівняння трьох парадигм асинхронності."""
    w, h = 920, 360
    frags = []
    
    # Заголовок / фонові колони
    col_w = 270
    gap = 30
    x0 = 35
    
    # Колона 1: Колбеки
    x1 = x0
    frags.append(rect(x1, 20, col_w, 320, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x1 + col_w/2, 45, "1. Зворотні виклики (Callbacks)", size=14, bold=True, color=POS))
    
    t1, _, _ = textbox(x1 + col_w/2, 90, "Головний потік: запит вводу-виводу\n(передаємо функцію-колбек)", size=11, fill="#ffffff", min_w=240)
    frags.append(t1)
    frags.append(arrow(x1 + col_w/2, 115, x1 + col_w/2, 145, color=LINE))
    
    t2, _, _ = textbox(x1 + col_w/2, 175, "Цикл подій чекає на сокет/диск\n(стек викликів розмотано!)", size=11, fill="#fff5f5", stroke=POS, min_w=240)
    frags.append(t2)
    frags.append(arrow(x1 + col_w/2, 205, x1 + col_w/2, 235, color=LINE))
    
    t3, _, _ = textbox(x1 + col_w/2, 275, "Виклик колбека у свіжому стеку:\nпіраміда вкладень, втрата try/catch", size=11, fill="#ffffff", min_w=240)
    frags.append(t3)
    
    # Колона 2: Проміси
    x2 = x1 + col_w + gap
    frags.append(rect(x2, 20, col_w, 320, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x2 + col_w/2, 45, "2. Проміси (Promises / Futures)", size=14, bold=True, color=NEG))
    
    p1, _, _ = textbox(x2 + col_w/2, 90, "Запит повертає об'єкт-токен:\nPromise { <pending> }", size=11, fill="#ffffff", min_w=240)
    frags.append(p1)
    frags.append(arrow(x2 + col_w/2, 115, x2 + col_w/2, 145, color=LINE))
    
    p2, _, _ = textbox(x2 + col_w/2, 175, "Ланцюжок .then() / .catch():\nпасивна підписка на результат", size=11, fill="#eff6ff", stroke=NEG, min_w=240)
    frags.append(p2)
    frags.append(arrow(x2 + col_w/2, 205, x2 + col_w/2, 235, color=LINE))
    
    p3, _, _ = textbox(x2 + col_w/2, 275, "Автосплющення промісів:\nлінійний конвеєр, єдиний .catch", size=11, fill="#ffffff", min_w=240)
    frags.append(p3)
    
    # Колона 3: Async/Await
    x3 = x2 + col_w + gap
    frags.append(rect(x3, 20, col_w, 320, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x3 + col_w/2, 45, "3. Корутини (Async / Await)", size=14, bold=True, color=FIELD))
    
    a1, _, _ = textbox(x3 + col_w/2, 90, "Синхронний вигляд коду:\nval = await fetchAsync()", size=11, fill="#ffffff", min_w=240)
    frags.append(a1)
    frags.append(arrow(x3 + col_w/2, 115, x3 + col_w/2, 145, color=LINE))
    
    a2, _, _ = textbox(x3 + col_w/2, 175, "Призупинення корутини:\nстан у купі, потік вільний", size=11, fill="#f0fdf4", stroke=FIELD, min_w=240)
    frags.append(a2)
    frags.append(arrow(x3 + col_w/2, 205, x3 + col_w/2, 235, color=LINE))
    
    a3, _, _ = textbox(x3 + col_w/2, 275, "Відновлення з того ж рядка:\nрідний try/catch, цикли for/while", size=11, fill="#ffffff", min_w=240)
    frags.append(a3)
    
    render(os.path.join(IMG_DIR, "evolution-paradigms.svg"), w, h, *frags)


def fig_callback_stack_unwinding():
    """2. callback-stack-unwinding.svg — Руйнування стеку викликів при колбеках."""
    w, h = 880, 320
    frags = []
    
    # Ліва частина: Фаза 1 (Планування)
    frags.append(rect(30, 20, 390, 280, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(225, 45, "Фаза 1: Ініціація операції вводу-виводу", size=13, bold=True, color=INK))
    
    s1, _, _ = textbox(225, 90, "try { doRequest(onSuccess); }", size=11, fill="#ffffff", min_w=340)
    s2, _, _ = textbox(225, 140, "Стек викликів: main() → run() → doRequest()", size=11, fill="#ffffff", min_w=340)
    s3, _, _ = textbox(225, 200, "Ядро реєструє сокет в epoll / kqueue\nФункція doRequest() негайно завершується", size=11, fill="#eff6ff", stroke=NEG, min_w=340)
    s4, _, _ = textbox(225, 260, "Стек ПОВНІСТЮ РОЗМОТУЄТЬСЯ до циклу подій", size=11, fill="#fff5f5", stroke=POS, bold=True, min_w=340)
    
    frags.extend([s1, s2, s3, s4])
    
    # Стрілка між фазами
    frags.append(arrow(430, 160, 465, 160, color=LINE, sw=2.0))
    frags.append(text(448, 145, "Час", size=11, italic=True, color=MUTED))
    
    # Права частина: Фаза 2 (Спрацювання події)
    frags.append(rect(470, 20, 380, 280, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(660, 45, "Фаза 2: Спрацювання події вводу-виводу", size=13, bold=True, color=INK))
    
    r1, _, _ = textbox(660, 90, "Цикл подій витягує подію з черги", size=11, fill="#ffffff", min_w=330)
    r2, _, _ = textbox(660, 140, "Свіжий стек викликів: eventLoop() → onSuccess()", size=11, fill="#ffffff", min_w=330)
    r3, _, _ = textbox(660, 200, "Якщо всередині onSuccess() стається помилка:\nконтексту try { ... } з Фази 1 ВЖЕ НЕ ІСНУЄ!", size=11, fill="#fff5f5", stroke=POS, min_w=330)
    r4, _, _ = textbox(660, 260, "Наслідок: аварійне падіння процесу (Uncaught Exception)", size=11, fill="#fee2e2", stroke=POS, bold=True, min_w=330)
    
    frags.extend([r1, r2, r3, r4])
    
    render(os.path.join(IMG_DIR, "callback-stack-unwinding.svg"), w, h, *frags)


def fig_promise_state_machine():
    """3. promise-state-machine.svg — Життєвий цикл та автомат станів проміса."""
    w, h = 860, 300
    frags = []
    
    # Стан Pending (зліва)
    p_box, _, _ = textbox(180, 150, "Очікування (Pending)\n\n• Значення відсутнє\n• Збирає чергу реакцій:\n  - onFulfilled[]\n  - onRejected[]", size=12, fill="#f8fafc", stroke=LINE, sw=2, min_w=240)
    frags.append(p_box)
    
    # Стан Fulfilled (вгорі праворуч)
    f_box, _, _ = textbox(650, 75, "Виконано (Fulfilled)\n\n• Фіксоване значення (Value)\n• Стан незмінний (Імутабельність)\n• Виклик мікрозадач onFulfilled", size=12, fill="#f0fdf4", stroke=FIELD, sw=2, min_w=280)
    frags.append(f_box)
    
    # Стан Rejected (внизу праворуч)
    r_box, _, _ = textbox(650, 225, "Відхилено (Rejected)\n\n• Причина відхилення (Reason / Error)\n• Стан незмінний (Імутабельність)\n• Виклик мікрозадач onRejected", size=12, fill="#fef2f2", stroke=POS, sw=2, min_w=280)
    frags.append(r_box)
    
    # Стрілки переходів
    frags.append(arrow(310, 125, 500, 85, color=FIELD, sw=2))
    frags.append(text(395, 95, "resolve(value)", size=12, bold=True, color=FIELD))
    
    frags.append(arrow(310, 175, 500, 215, color=POS, sw=2))
    frags.append(text(395, 210, "reject(error)", size=12, bold=True, color=POS))
    
    # Позначка незворотності
    frags.append(text(720, 150, "Остаточний стан (Settled)", size=12, bold=True, color=MUTED))
    frags.append(line(505, 150, 630, 150, color=MUTED, sw=1, dash="4,4"))
    
    render(os.path.join(IMG_DIR, "promise-state-machine.svg"), w, h, *frags)


def fig_async_await_lowering():
    """4. async-await-lowering.svg — Трансформація async/await у скінченний автомат корутини."""
    w, h = 900, 350
    frags = []
    
    # Ліва колонка: Вихідний код async/await
    frags.append(rect(30, 20, 360, 310, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(210, 45, "Вихідний код (High-level)", size=13, bold=True, color=INK))
    
    src = (
        "async function fetchUser(id) {\n"
        "  const u = await httpGet('/u/' + id);\n"
        "  const p = await dbLoad(u.profileId);\n"
        "  return { u, p };\n"
        "}"
    )
    c1, _, _ = textbox(210, 160, src, size=11, fill="#ffffff", stroke=LINE, min_w=320)
    frags.append(c1)
    
    frags.append(text(210, 280, "Погляд програміста: послідовне виконання\nз паузами на операціях вводу-виводу", size=11, color=MUTED))
    
    # Стрілка трансформації
    frags.append(arrow(400, 170, 450, 170, color=LINE, sw=2))
    frags.append(text(425, 155, "Компілятор\n/ Рушій", size=10, bold=True, color=FIELD))
    
    # Права колонка: Автомат станів (Lowered State Machine)
    frags.append(rect(460, 20, 410, 310, fill="none", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(665, 45, "Автомат корутини (Низький рівень)", size=13, bold=True, color=INK))
    
    s0, _, _ = textbox(665, 90, "Стан 0: Початок → запуск httpGet → зберегти стан → yield", size=10, fill="#eff6ff", stroke=NEG, min_w=370)
    s1, _, _ = textbox(665, 150, "Стан 1: Відновлення → u = res0 → запуск dbLoad → yield", size=10, fill="#eff6ff", stroke=NEG, min_w=370)
    s2, _, _ = textbox(665, 210, "Стан 2: Відновлення → p = res1 → resolve Promise({ u, p })", size=10, fill="#f0fdf4", stroke=FIELD, min_w=370)
    
    frags.extend([s0, s1, s2])
    frags.append(arrow(665, 115, 665, 130, color=LINE))
    frags.append(arrow(665, 175, 665, 190, color=LINE))
    
    frags.append(text(665, 275, "Кадр корутини у купі зберігає:\n{ state: 0|1|2, id, u, p, promise }", size=11, bold=True, color=INK))
    
    render(os.path.join(IMG_DIR, "async-await-lowering.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_evolution_paradigms()
    fig_callback_stack_unwinding()
    fig_promise_state_machine()
    fig_async_await_lowering()
    print("Всі SVG-фігури згенеровано успішно.")
