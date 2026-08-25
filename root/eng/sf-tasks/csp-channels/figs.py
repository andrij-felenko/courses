# -*- coding: utf-8 -*-
"""Фігури до теми «Канали і CSP (Communicating Sequential Processes)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Кольори ролей
PROC_FILL   = "#eaf2fd"
PROC_LINE   = "#2457d6"
CHAN_FILL   = "#eafaf1"
CHAN_LINE   = "#27ae60"
SYNC_FILL   = "#fef5e7"
SYNC_LINE   = "#d35400"
QUEUE_FILL  = "#f4f6f8"
QUEUE_LINE  = "#555555"
FAIL_FILL   = "#fdecea"
FAIL_LINE   = "#c0392b"
WARN_FILL   = "#fff6e0"
WARN_LINE   = "#caa24a"
MUTED_FILL  = "#f8f9fa"

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


# ── 1. Синхронне рандеву проти буферизованого каналу ─────────────────────────
def fig_csp_rendezvous():
    W, H = 880, 440
    f = [text(W / 2, 26, "Семантика каналів: синхронне рандеву та буферизація", size=16, bold=True)]
    f.append(text(W / 2, 46, "Рандеву синхронізує час виконання процесів; буфер розв'язує їх у часі до заповнення",
                  size=11, color=MUTED, italic=True))

    # Ліва панель: Синхронний канал (Рандеву)
    f.append(rect(30, 70, 395, 305, fill="#fafbfc", stroke=SYNC_LINE, sw=1.6, rx=8))
    f.append(text(227, 95, "Синхронний канал (Unbuffered / Rendezvous)", size=13, color=SYNC_LINE, bold=True))
    f.append(text(227, 113, "Місткість буфера = 0 (точка зустрічі)", size=10.5, color=MUTED))

    # Процес A
    boxlabel(f, 50, 140, 105, 55, ["Процес A", "(Відправник)"], fill=PROC_FILL, stroke=PROC_LINE, size=11)
    # Процес B
    boxlabel(f, 300, 140, 105, 55, ["Процес B", "(Отримувач)"], fill=PROC_FILL, stroke=PROC_LINE, size=11)

    # Точка рандеву посередині
    f.append(rect(180, 135, 95, 65, fill=SYNC_FILL, stroke=SYNC_LINE, sw=2, rx=6))
    f.append(text(227, 160, "Рандеву", size=12, color=SYNC_LINE, bold=True))
    f.append(text(227, 180, "Бар'єр синхр.", size=10, color=MUTED))

    f.append(arrow(155, 167, 180, 167, color=PROC_LINE, sw=2))
    f.append(arrow(275, 167, 300, 167, color=PROC_LINE, sw=2))

    boxlabel(f, 50, 220, 355, 60,
             ["Відправник блокується, доки отримувач не викличе recv()",
              "Отримувач блокується, доки відправник не викличе send()",
              "Дані копіюються безпосередньо стек-у-стек"],
             fill="#ffffff", stroke="#cccccc", size=10)

    boxlabel(f, 50, 295, 355, 65,
             ["Гарантія: у момент завершення передачі",
              "обидва процеси гарантовано дійшли до точки зв'язку,",
              "повна синхронізація станів у часі"],
             fill=SYNC_FILL, stroke=SYNC_LINE, size=10)

    # Права панель: Буферизований канал
    f.append(rect(455, 70, 395, 305, fill="#fafbfc", stroke=CHAN_LINE, sw=1.6, rx=8))
    f.append(text(652, 95, "Буферизований канал (Buffered Channel)", size=13, color=CHAN_LINE, bold=True))
    f.append(text(652, 113, "Кільцевий буфер місткістю N > 0", size=10.5, color=MUTED))

    # Процес A
    boxlabel(f, 475, 140, 105, 55, ["Процес A", "(Відправник)"], fill=PROC_FILL, stroke=PROC_LINE, size=11)
    # Процес B
    boxlabel(f, 725, 140, 105, 55, ["Процес B", "(Отримувач)"], fill=PROC_FILL, stroke=PROC_LINE, size=11)

    # Буфер по центру
    f.append(rect(600, 135, 105, 65, fill=CHAN_FILL, stroke=CHAN_LINE, sw=1.8, rx=6))
    f.append(text(652, 155, "Буфер [N=4]", size=11, color=CHAN_LINE, bold=True))
    # Комірки буфера
    f.append(rect(608, 168, 20, 22, fill="#ffffff", stroke=CHAN_LINE, sw=1))
    f.append(text(618, 183, "D1", size=9, bold=True))
    f.append(rect(630, 168, 20, 22, fill="#ffffff", stroke=CHAN_LINE, sw=1))
    f.append(text(640, 183, "D2", size=9, bold=True))
    f.append(rect(652, 168, 20, 22, fill="#ffffff", stroke="#aaaaaa", sw=1))
    f.append(text(662, 183, "·", size=9, color=MUTED))
    f.append(rect(674, 168, 20, 22, fill="#ffffff", stroke="#aaaaaa", sw=1))
    f.append(text(684, 183, "·", size=9, color=MUTED))

    f.append(arrow(580, 167, 600, 167, color=PROC_LINE, sw=2))
    f.append(arrow(705, 167, 725, 167, color=PROC_LINE, sw=2))

    boxlabel(f, 475, 220, 355, 60,
             ["Відправник не блокується, поки в буфері є вільне місце",
              "Отримувач не блокується, поки в буфері є хоч один елемент",
              "Розв'язка за швидкістю та згладжування сплесків"],
             fill="#ffffff", stroke="#cccccc", size=10)

    boxlabel(f, 475, 295, 355, 65,
             ["Зворотний тиск (Backpressure): коли буфер заповнений,",
              "відправник примусово блокується, що запобігає",
              "неконтрольованому вичерпанню оперативної пам'яті"],
             fill=CHAN_FILL, stroke=CHAN_LINE, size=10)

    # Висновок знизу
    note(f, W / 2, 390, 820,
         ["Висновок: Рандеву створює жорсткий спільний часовий бар'єр без витрат пам'яті; "
          "буферизація вводить керований зворотний тиск і усуває затримки коротких сплесків."],
         fill=WARN_FILL, stroke=WARN_LINE, size=10.5)

    render(os.path.join(IMG, "csp-rendezvous.svg"), W, H, *f)


# ── 2. Внутрішня анатомія каналу в рантаймі ──────────────────────────────────
def fig_channel_internals():
    W, H = 880, 470
    f = [text(W / 2, 26, "Внутрішня анатомія каналу в пам'яті рантайму", size=16, bold=True)]
    f.append(text(W / 2, 46, "Структура керування, кільцевий буфер та черги очікування заблокованих потоків/корутин",
                  size=11, color=MUTED, italic=True))

    # Головна структура каналу
    f.append(rect(40, 70, 800, 335, fill="#fdfefe", stroke=CHAN_LINE, sw=2, rx=10))
    f.append(text(440, 95, "Дескриптор каналу (Channel Object / hchan)", size=14, color=CHAN_LINE, bold=True))

    # Секція 1: М'ютекс / Замок структури
    f.append(rect(65, 115, 220, 110, fill=FAIL_FILL, stroke=FAIL_LINE, sw=1.5, rx=6))
    f.append(text(175, 137, "М'ютекс захисту (Lock)", size=12, color=FAIL_LINE, bold=True))
    f.append(text(175, 157, "Спінлок або futex м'ютекс", size=10, color=MUTED))
    f.append(text(175, 175, "Захищає лічильники та черги", size=10, color=MUTED))
    f.append(text(175, 195, "closed = 0 (прапорець закриття)", size=10, color=FAIL_LINE, bold=True))

    # Секція 2: Кільцевий буфер елементів
    f.append(rect(305, 115, 400, 110, fill=CHAN_FILL, stroke=CHAN_LINE, sw=1.5, rx=6))
    f.append(text(505, 137, "Кільцевий буфер елементів (Ring Buffer)", size=12, color=CHAN_LINE, bold=True))
    f.append(text(505, 155, "elemsize: 8 байтів | dataqsiz: 8 | qcount: 3", size=10, color=MUTED))

    # Комірки буфера в рядок
    slots = ["D1", "D2", "D3", "—", "—", "—", "—", "—"]
    for i, s in enumerate(slots):
        sx = 325 + i * 45
        cfill = "#d5f5e3" if i < 3 else "#ffffff"
        cstroke = CHAN_LINE if i < 3 else "#aaaaaa"
        f.append(rect(sx, 170, 40, 32, fill=cfill, stroke=cstroke, sw=1.2, rx=4))
        f.append(text(sx + 20, 190, s, size=10.5, bold=True, color=INK if i < 3 else MUTED))
        f.append(text(sx + 20, 215, "[%d]" % i, size=9, color=MUTED))

    # Секція 3: Індикатори recvx та sendx
    boxlabel(f, 720, 115, 100, 50, ["sendx = 3", "(запис)"], fill="#ffffff", stroke=CHAN_LINE, size=10)
    boxlabel(f, 720, 175, 100, 50, ["recvx = 0", "(читання)"], fill="#ffffff", stroke=CHAN_LINE, size=10)

    # Нижня частина: Черги очікування
    # Черга заблокованих читачів (recvq)
    f.append(rect(65, 245, 360, 140, fill=PROC_FILL, stroke=PROC_LINE, sw=1.5, rx=6))
    f.append(text(245, 268, "recvq: Черга очікування читачів (FIFO)", size=12, color=PROC_LINE, bold=True))
    f.append(text(245, 286, "Коли qcount == 0, отримувачі блокуються тут", size=10, color=MUTED))

    boxlabel(f, 85, 300, 145, 36, "Потік G1 (адреса &dest1)", fill="#ffffff", stroke=PROC_LINE, size=9.5)
    f.append(arrow(230, 318, 255, 318, color=PROC_LINE, sw=1.5))
    boxlabel(f, 255, 300, 145, 36, "Потік G2 (адреса &dest2)", fill="#ffffff", stroke=PROC_LINE, size=9.5)
    f.append(text(245, 360, "Відправник копіює напряму в &dest першого в черзі", size=9.5, color=PROC_LINE, italic=True))

    # Черга заблокованих письменників (sendq)
    f.append(rect(460, 245, 360, 140, fill=SYNC_FILL, stroke=SYNC_LINE, sw=1.5, rx=6))
    f.append(text(640, 268, "sendq: Черга очікування відправників (FIFO)", size=12, color=SYNC_LINE, bold=True))
    f.append(text(640, 286, "Коли qcount == dataqsiz, відправники чекають тут", size=10, color=MUTED))

    boxlabel(f, 480, 300, 145, 36, "Потік G5 (значення ValA)", fill="#ffffff", stroke=SYNC_LINE, size=9.5)
    f.append(arrow(625, 318, 650, 318, color=SYNC_LINE, sw=1.5))
    boxlabel(f, 650, 300, 145, 36, "Потік G6 (значення ValB)", fill="#ffffff", stroke=SYNC_LINE, size=9.5)
    f.append(text(640, 360, "Отримувач забирає з буфера і будить G5, вносячи ValA", size=9.5, color=SYNC_LINE, italic=True))

    # Висновок
    note(f, W / 2, 420, 800,
         ["Канал координує пам'ять без прямого обміну між потоками: спільний лок захищає лише метадані, "
          "а перехід стану перетворює блокування в перемикання планувальника рантайму."],
         fill=WARN_FILL, stroke=WARN_LINE, size=10.5)

    render(os.path.join(IMG, "channel-internals.svg"), W, H, *f)


# ── 3. Мультиплексування через select / alt ──────────────────────────────────
def fig_select_multiplexing():
    W, H = 880, 440
    f = [text(W / 2, 26, "Мультиплексування каналів: примітив select / alt", size=16, bold=True)]
    f.append(text(W / 2, 46, "Недетермінований вибір готової події вводу-виводу, тайм-аути та кооперативне скасування",
                  size=11, color=MUTED, italic=True))

    # Ліва сторона: Вхідні канали
    f.append(text(130, 85, "Джерела повідомлень", size=13, bold=True))

    boxlabel(f, 30, 105, 200, 50, ["ch_data (Дані датчика)", "Готовий до читання"], fill=CHAN_FILL, stroke=CHAN_LINE, size=10.5)
    boxlabel(f, 30, 175, 200, 50, ["ch_control (Команди)", "Порожній (блокований)"], fill=MUTED_FILL, stroke="#aaaaaa", size=10.5)
    boxlabel(f, 30, 245, 200, 50, ["time.After(50ms) (Таймер)", "Спрацює при затримці"], fill=WARN_FILL, stroke=WARN_LINE, size=10.5)
    boxlabel(f, 30, 315, 200, 50, ["ctx.Done() (Скасування)", "Сигнал зупинки потоку"], fill=FAIL_FILL, stroke=FAIL_LINE, size=10.5)

    # Центр: Блок мультиплексора select
    f.append(rect(290, 90, 280, 290, fill="#f8faff", stroke=PROC_LINE, sw=2, rx=10))
    f.append(text(430, 120, "Оператор select / alt", size=15, color=PROC_LINE, bold=True))
    f.append(text(430, 140, "Атомарне опитування всіх гілок", size=10.5, color=MUTED))

    # Стрілки від джерел до селектора
    f.append(arrow(230, 130, 290, 150, color=CHAN_LINE, sw=2))
    f.append(line(230, 200, 290, 200, color="#aaaaaa", sw=1.5, dash="4,3"))
    f.append(arrow(230, 270, 290, 250, color=WARN_LINE, sw=1.5))
    f.append(arrow(230, 340, 290, 300, color=FAIL_LINE, sw=2))

    boxlabel(f, 310, 165, 240, 75,
             ["1. Блокує всі залучені канали",
              "2. Якщо готово кілька —",
              "   випадковий псевдовибір (fair)",
              "3. Якщо жоден не готовий —",
              "   потік спить у чергах усіх гілок"],
             fill="#ffffff", stroke=PROC_LINE, size=9.5)

    boxlabel(f, 310, 255, 240, 105,
             ["Гілка default (опціонально):",
              "• Перетворює select на",
              "  неблокувальний запит (polling)",
              "• Виконується миттєво,",
              "  якщо жоден канал не готовий"],
             fill="#f4f6f8", stroke="#888888", size=9.5)

    # Права сторона: Обробники подій
    f.append(text(720, 85, "Виконання обраної гілки", size=13, bold=True))

    boxlabel(f, 630, 105, 220, 50, ["Обробка пакета даних", "v := <-ch_data"], fill=CHAN_FILL, stroke=CHAN_LINE, size=10.5)
    boxlabel(f, 630, 175, 220, 50, ["Обробка команди", "cmd := <-ch_control"], fill=MUTED_FILL, stroke="#aaaaaa", size=10.5)
    boxlabel(f, 630, 245, 220, 50, ["Логіка таймауту", "лог помилки та ретрай"], fill=WARN_FILL, stroke=WARN_LINE, size=10.5)
    boxlabel(f, 630, 315, 220, 50, ["Коректне завершення", "звільнення ресурсів"], fill=FAIL_FILL, stroke=FAIL_LINE, size=10.5)

    # Стрілки від селектора до дій
    f.append(arrow(570, 160, 630, 130, color=CHAN_LINE, sw=2))
    f.append(line(570, 210, 630, 200, color="#aaaaaa", sw=1.2, dash="4,3"))
    f.append(arrow(570, 260, 630, 270, color=WARN_LINE, sw=1.5))
    f.append(arrow(570, 310, 630, 340, color=FAIL_LINE, sw=2))

    # Висновок
    note(f, W / 2, 395, 820,
         ["Принцип: select об'єднує незалежні канали зв'язку в єдину реактивну систему; "
          "випадковий арбітраж запобігає голодуванню (starvation) швидких каналів."],
         fill=WARN_FILL, stroke=WARN_LINE, size=10.5)

    render(os.path.join(IMG, "select-multiplexing.svg"), W, H, *f)


# ── 4. Порівняння: Модель CSP проти Моделі Акторів ───────────────────────────
def fig_csp_vs_actors():
    W, H = 880, 440
    f = [text(W / 2, 26, "Архітектурне порівняння: Модель CSP проти Моделі Акторів", size=16, bold=True)]
    f.append(text(W / 2, 46, "Канали як незалежні сутності першого класу (CSP) проти прямої адресації поштових скриньок (Актори)",
                  size=11, color=MUTED, italic=True))

    # Ліва колонка: CSP (Канали)
    f.append(rect(30, 70, 395, 305, fill="#fdfefe", stroke=CHAN_LINE, sw=1.8, rx=8))
    f.append(text(227, 95, "Модель CSP (Go, Occam, Clojure core.async)", size=13, color=CHAN_LINE, bold=True))
    f.append(text(227, 113, "Фокус на КАНАЛАХ (першокласні об'єкти)", size=10.5, color=MUTED))

    # Візуалізація топології CSP
    boxlabel(f, 45, 135, 90, 45, "Процес P1", fill=PROC_FILL, stroke=PROC_LINE, size=10)
    boxlabel(f, 45, 195, 90, 45, "Процес P2", fill=PROC_FILL, stroke=PROC_LINE, size=10)

    # Канал по центру
    f.append(rect(170, 150, 115, 65, fill=CHAN_FILL, stroke=CHAN_LINE, sw=1.8, rx=6))
    f.append(text(227, 175, "Канал C", size=12, color=CHAN_LINE, bold=True))
    f.append(text(227, 195, "Анонімний конвеєр", size=9.5, color=MUTED))

    boxlabel(f, 320, 160, 90, 45, "Процес P3", fill=PROC_FILL, stroke=PROC_LINE, size=10)

    f.append(arrow(135, 157, 170, 170, color=PROC_LINE, sw=1.6))
    f.append(arrow(135, 217, 170, 190, color=PROC_LINE, sw=1.6))
    f.append(arrow(285, 182, 320, 182, color=CHAN_LINE, sw=1.6))

    boxlabel(f, 45, 270, 365, 90,
             ["• Анонімність: процеси не знають ідентифікаторів один одного",
              "• Канал можна передавати як значення через інший канал",
              "• Синхронізація: природне рандеву та мультиплексування select",
              "• Гнучка N:M топологія (багато відправників, багато отримувачів)"],
             fill=CHAN_FILL, stroke=CHAN_LINE, size=9.5)

    # Права колонка: Модель Акторів
    f.append(rect(455, 70, 395, 305, fill="#fdfefe", stroke=PROC_LINE, sw=1.8, rx=8))
    f.append(text(652, 95, "Модель Акторів (Erlang, Elixir, Akka)", size=13, color=PROC_LINE, bold=True))
    f.append(text(652, 113, "Фокус на СУТНОСТЯХ (пряма адресація через PID)", size=10.5, color=MUTED))

    # Візуалізація топології Акторів
    boxlabel(f, 470, 140, 100, 45, ["Актор A", "PID: <0.41.0>"], fill=PROC_FILL, stroke=PROC_LINE, size=9.5)

    # Актор B зі скринькою
    f.append(rect(610, 135, 225, 95, fill=PROC_FILL, stroke=PROC_LINE, sw=1.5, rx=6))
    f.append(text(722, 153, "Актор B (PID: <0.82.0>)", size=11, color=PROC_LINE, bold=True))
    boxlabel(f, 620, 163, 105, 55, ["Поштова", "скринька FIFO"], fill="#ffffff", stroke=PROC_LINE, size=9)
    boxlabel(f, 735, 163, 90, 55, ["Приватний", "стан"], fill=SYNC_FILL, stroke=SYNC_LINE, size=9)

    f.append(arrow(570, 162, 620, 185, color=PROC_LINE, sw=1.8))
    f.append(text(595, 150, "send(PID_B, msg)", size=9.5, color=PROC_LINE))

    boxlabel(f, 470, 270, 365, 90,
             ["• Адресація: повідомлення шлеться на конкретний PID актора",
              "• Поштова скринька жорстко прив'язана до життєвого циклу актора",
              "• Асинхронність: відправник ніколи не чекає отримувача (fire & forget)",
              "• Відмовостійкість: вбудовані дерева нагляду та ізоляція крахів"],
             fill=PROC_FILL, stroke=PROC_LINE, size=9.5)

    # Висновок
    note(f, W / 2, 390, 820,
         ["Узагальнення: CSP структурує потік передачі даних через незалежні канали; "
          "модель акторів структурує життєвий цикл, стан та відмовостійкість обчислювальних одиниць."],
         fill=WARN_FILL, stroke=WARN_LINE, size=10.5)

    render(os.path.join(IMG, "csp-vs-actors.svg"), W, H, *f)


if __name__ == "__main__":
    fig_csp_rendezvous()
    fig_channel_internals()
    fig_select_multiplexing()
    fig_csp_vs_actors()
    print("Згенеровано 4 фігури.")
