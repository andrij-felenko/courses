# -*- coding: utf-8 -*-
"""Фігури до теми «Потоки виконання й черги: де конвеєр міняє потік»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

T1, T2, T3 = NEG, FIELD, POS


def pad_square(cx, cy, color=INK):
    return rect(cx - 7, cy - 7, 14, 14, fill="#ffffff", stroke=color, sw=2, rx=2)


def task_dot(cx, cy, color):
    return circle(cx, cy, 9, fill="#ffffff", stroke=color, sw=3)


# ── 1. Мапа ниток у конвеєрі ────────────────────────────────────────────────
def fig_thread_map():
    W, H = 1080, 400
    f = []
    names = [["udpsrc", "джерело"],
             ["rtpjitterbuffer", "витримка за часом"],
             ["rtph264depay", "збірка кадру"],
             ["avdec_h264", "декодер"],
             ["queue", "межа ниток"],
             ["videoconvert", "формат кольору"],
             ["autovideosink", "показ"]]
    n = len(names)
    bw, bh, top = 126, 70, 110
    gap = (W - 80 - n * bw) / (n - 1.0)
    xs = [40 + i * (bw + gap) for i in range(n)]
    mid = top + bh / 2

    for i, x in enumerate(xs):
        f.append(fitbox(x, top, bw, bh, names[i], size=13, pad=8))
    for i, x in enumerate(xs):
        if i > 0:
            f.append(pad_square(x + 12, mid))
        if i < n - 1:
            f.append(pad_square(x + bw - 12, mid))
    for i in range(n - 1):
        f.append(arrow(xs[i] + bw + 3, mid, xs[i + 1] - 3, mid))

    # задачі живуть на вихідних падах цих трьох елементів
    for i, col in ((0, T1), (1, T2), (4, T3)):
        f.append(task_dot(xs[i] + bw - 12, mid, col))

    # смуги ниток: межа проходить серединою елемента, що має задачу
    by, bhh = 225, 30
    edges = [xs[0] - 6, xs[1] + bw / 2, xs[4] + bw / 2, xs[n - 1] + bw + 6]
    labels = ["нитка 1: задача udpsrc",
              "нитка 2: задача rtpjitterbuffer",
              "нитка 3: задача queue"]
    cols = [T1, T2, T3]
    for i in range(3):
        x0, x1 = edges[i] + (0 if i == 0 else 4), edges[i + 1] - (0 if i == 2 else 4)
        f.append(fitbox(x0, by, x1 - x0, bhh, labels[i], size=12, pad=8,
                        fill="#ffffff", stroke=cols[i], sw=2))

    f.append(text(40, 300,
                  "Кружок — вихідний пад, на якому крутиться GstTask. Межа ниток проходить УСЕРЕДИНІ такого елемента:",
                  size=12, color=MUTED, anchor="start"))
    f.append(text(40, 322,
                  "його вхідний пад працює в чужій нитці, вихідний — у власній.",
                  size=12, color=MUTED, anchor="start"))
    f.append(text(40, 352,
                  "Понад ці три: внутрішні робочі нитки декодера й нитка застосунку, що читає шину.",
                  size=12, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "thread-map.svg"), W, H, *f,
           title="Три нитки на семи елементах")


# ── 2. Чому tee без черг заклинює ───────────────────────────────────────────
def fig_tee_deadlock():
    W, H = 1020, 620
    f = []

    # ── панель А: без черг
    f.append(text(40, 70, "без черг на гілках", size=15, bold=True, anchor="start", color=POS))
    f.append(fitbox(40, 130, 130, 60, "tee", size=14, pad=8))
    f.append(fitbox(250, 92, 190, 56, ["стік A", "autovideosink"], size=12, pad=8, stroke=POS, sw=2))
    f.append(fitbox(250, 176, 190, 56, ["стік B", "filesink"], size=12, pad=8, stroke=MUTED))
    f.append(arrow(172, 150, 248, 122))
    f.append(arrow(172, 172, 248, 202))

    notes_a = [(100, "① стік A взяв перший буфер і став чекати на PLAYING"),
               (163, "② tee не повернувся з push, гілка B нічого не отримала"),
               (226, "③ без буфера в B конвеєр не доходить до PAUSED, отже PLAYING не настане")]
    for y, s in notes_a:
        body, w, h = textbox(740, y, s, size=12, pad=10, min_w=520, stroke=POS)
        f.append(body)
    f.append(rect(468, 74, 546, 178, fill="none", stroke=POS, sw=2, rx=10))
    f.append(text(741, 272, "коло очікування замкнулося: ніхто нікого не відпустить",
                  size=12, color=POS, bold=True))

    f.append(line(30, 310, W - 30, 310, color=MUTED, sw=1.2, dash="6,6"))

    # ── панель Б: з чергами
    f.append(text(40, 360, "черга на кожній гілці", size=15, bold=True, anchor="start", color=FIELD))
    f.append(fitbox(40, 420, 130, 60, "tee", size=14, pad=8))
    f.append(fitbox(210, 382, 110, 56, "queue", size=13, pad=8, stroke=FIELD, sw=2))
    f.append(fitbox(210, 466, 110, 56, "queue", size=13, pad=8, stroke=FIELD, sw=2))
    f.append(fitbox(360, 382, 180, 56, ["стік A", "autovideosink"], size=12, pad=8))
    f.append(fitbox(360, 466, 180, 56, ["стік B", "filesink"], size=12, pad=8))
    f.append(arrow(172, 440, 208, 412))
    f.append(arrow(172, 462, 208, 492))
    f.append(arrow(322, 410, 358, 410))
    f.append(arrow(322, 494, 358, 494))

    notes_b = [(400, "① черга бере буфер у свій список і повертається негайно"),
               (463, "② кожна гілка далі йде власною ниткою"),
               (526, "③ обидва стоки префролять незалежно, конвеєр стає PLAYING")]
    for y, s in notes_b:
        body, w, h = textbox(740, y, s, size=12, pad=10, min_w=520, stroke=FIELD)
        f.append(body)

    render(os.path.join(IMG, "tee-deadlock.svg"), W, H, *f,
           title="Розгалуження без межі ниток заклинює ще до першого кадру")


# ── 3. Черга зсередини ──────────────────────────────────────────────────────
def fig_queue_inside():
    W, H = 1020, 470
    f = []

    f.append(rect(250, 110, 470, 215, fill="#ffffff", stroke=LINE, sw=2, rx=10))
    f.append(text(485, 136, "елемент queue", size=13, bold=True))

    for i in range(8):
        f.append(rect(292 + i * 44, 158, 34, 28, fill=FILL, stroke=LINE, sw=1.2, rx=3))
    f.append(text(485, 212, "список буферів під замком", size=12, color=MUTED))

    body, _, _ = textbox(485, 252, "повна → chain() чекає на «щось забрали»",
                         size=12, pad=8, stroke=MUTED, min_w=400)
    f.append(body)
    body, _, _ = textbox(485, 296, "порожня → loop() чекає на «щось поклали»",
                         size=12, pad=8, stroke=MUTED, min_w=400)
    f.append(body)

    f.append(fitbox(30, 145, 190, 76, ["chain()", "у нитці того,", "хто штовхнув"],
                    size=12, pad=8, stroke=T1, sw=2))
    f.append(fitbox(760, 145, 220, 76, ["loop()", "власна нитка:", "GstTask на вихідному паді"],
                    size=12, pad=8, stroke=T3, sw=2))
    f.append(arrow(224, 172, 288, 172))
    f.append(arrow(722, 172, 756, 172))
    f.append(text(870, 250, "далі: gst_pad_push()", size=12, color=MUTED))

    body, _, _ = textbox(510, 372,
                         ["межі; спрацьовує будь-яка з трьох:",
                          "200 буферів · 10 МіБ · 1 секунда даних"],
                         size=13, pad=10, stroke=FIELD, sw=2)
    f.append(body)
    f.append(text(510, 435,
                  "Код потоку від нижнього сусіда черга запам'ятовує й віддає верхньому вже з наступним буфером.",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "queue-inside.svg"), W, H, *f,
           title="Черга: дві функції, дві нитки, один список")


# ── 4. multiqueue й непід'єднана гілка ──────────────────────────────────────
def fig_multiqueue():
    W, H = 1040, 450
    f = []
    ys = [170, 228, 286]

    f.append(fitbox(40, 130, 140, 190, ["qtdemux", "", "розбирач", "контейнера"], size=12, pad=8))
    for y in ys:
        f.append(pad_square(180 - 12, y))

    f.append(rect(270, 108, 300, 235, fill="#ffffff", stroke=LINE, sw=2, rx=10))
    f.append(text(420, 134, "multiqueue", size=13, bold=True))
    inner = [("відео — власна нитка", T1), ("звук — власна нитка", T2), ("субтитри — власна нитка", T3)]
    for i, y in enumerate(ys):
        f.append(fitbox(292, y - 22, 256, 44, inner[i][0], size=12, pad=8,
                        stroke=inner[i][1], sw=2))

    f.append(fitbox(650, ys[0] - 22, 300, 44, "avdec_h264 → стік", size=12, pad=8, stroke=FIELD))
    f.append(fitbox(650, ys[1] - 22, 300, 44, "avdec_aac → стік", size=12, pad=8, stroke=FIELD))
    f.append(fitbox(650, ys[2] - 22, 300, 44, "пад ще нікуди не веде", size=12, pad=8, stroke=POS, sw=2))

    for y in ys:
        f.append(arrow(182, y, 268, y))
        f.append(arrow(572, y, 646, y))

    body, _, _ = textbox(520, 396,
                         ["Звичайна черга на такій гілці дістала б NOT_LINKED і спинила потік.",
                          "multiqueue приймає її дані ще 250 мс наперед і не дає їй спинити сусідів."],
                         size=13, pad=10, stroke=POS, sw=2)
    f.append(body)

    render(os.path.join(IMG, "multiqueue-not-linked.svg"), W, H, *f,
           title="Багато гілок: власна нитка на кожен вихідний пад")


# ── 5. Стеки: співпрограми 0.8 проти ниток ОС 0.10 (вставка hist) ───────────
def fig_cothread_stacks():
    W, H = 1020, 520
    f = []

    f.append(text(255, 40, "0.8: один стек, порізаний на частини", size=17, bold=True, color=POS))
    f.append(text(765, 40, "0.10: власний стек на кожну нитку", size=17, bold=True, color=FIELD))

    f.append(line(510, 66, 510, 500, color=MUTED, sw=1.5, dash="6,6"))

    # ── ліворуч: одна нитка ОС, стек порізаний ──
    f.append(rect(120, 78, 270, 322, fill="#ffffff", stroke=POS, sw=2.5, rx=8))
    f.append(text(255, 100, "одна нитка операційної системи", size=12, color=MUTED))

    slices = [("стек sink", 116), ("стек filter", 208), ("стек src", 300)]
    for name, y in slices:
        f.append(fitbox(140, y, 230, 78, name, size=13, pad=8, stroke=POS, sw=1.8))

    # стрибки між шматками
    f.append(arrow(392, 155, 392, 235, color=POS))
    f.append(arrow(392, 325, 392, 245, color=POS))
    f.append(text(452, 200, "longjmp", size=12, color=POS, bold=True))

    body, _, _ = textbox(255, 440,
                         ["Розмір кожного шматка вибрано наперед.",
                          "Налагоджувач бачить один стек — не той,",
                          "у якому справді сталася помилка."],
                         size=12.5, pad=10, stroke=POS, sw=2)
    f.append(body)

    # ── праворуч: три нитки, три стеки ──
    xs = (570, 700, 830)
    for x, name in zip(xs, ("src", "filter", "sink")):
        f.append(rect(x, 78, 110, 322, fill="#ffffff", stroke=FIELD, sw=2.5, rx=8))
        f.append(text(x + 55, 100, name, size=13, bold=True))
        f.append(fitbox(x + 12, 118, 86, 264, "стек\nросте\nсам", size=12, pad=6,
                        stroke=FIELD, sw=1.5))

    f.append(text(765, 424, "перемикає ядро, а не бібліотека", size=12.5, color=MUTED))
    body, _, _ = textbox(765, 470,
                         ["Блокувальний виклик усередині чужої бібліотеки",
                          "спиняє лише свою нитку — решта йде далі."],
                         size=12.5, pad=10, stroke=FIELD, sw=2)
    f.append(body)

    render(os.path.join(IMG, "cothread-stacks.svg"), W, H, *f,
           title="Співпрограми 0.8 проти ниток ОС 0.10")


# ── 6. Де в стеку сидить проба (вставка proj) ───────────────────────────────
def fig_probe_in_stack():
    W, H = 1040, 470
    f = []

    f.append(text(535, 44, "нитка задачі queue0:src — стек росте вниз",
                  size=13.5, color=MUTED))

    f.append(fitbox(60, 80, 700, 46, "gst_task_func → queue_loop() на паді queue0:src",
                    size=13, stroke=NEG, sw=2.5))
    f.append(fitbox(88, 136, 660, 46, "gst_pad_push (queue0:src)",
                    size=13, stroke=NEG, sw=2))
    f.append(fitbox(112, 192, 210, 46, "ваша проба: queue0 > src",
                    size=12, stroke=POS, sw=2.5))
    f.append(fitbox(340, 192, 396, 46, "gst_pad_chain_data (jpegenc0:sink)",
                    size=13, stroke=NEG, sw=2))
    f.append(fitbox(364, 248, 200, 46, "ваша проба: jpegenc0 < sink",
                    size=12, stroke=POS, sw=2.5))
    f.append(fitbox(582, 248, 142, 46, "gst_jpegenc_chain ()",
                    size=12, stroke=NEG, sw=2))

    body, _, _ = textbox(895, 116, ["замок потоку queue0:src",
                                    "тримає задача — від самого",
                                    "верхнього рядка й донизу"],
                         size=11.5, pad=10, stroke=NEG, sw=2, min_w=230)
    f.append(body)
    body, _, _ = textbox(895, 232, ["замок потоку jpegenc0:sink",
                                    "бере gst_pad_chain_data —",
                                    "ще ДО вашої проби"],
                         size=11.5, pad=10, stroke=NEG, sw=2, min_w=230)
    f.append(body)

    body, _, _ = textbox(300, 390, ["Проба — звичайний кадр цього стеку.",
                                    "Поки вона рахує, увесь ланцюг над нею стоїть."],
                         size=12.5, pad=10, stroke=MUTED, sw=1.5, min_w=460)
    f.append(body)
    body, _, _ = textbox(770, 390, ["set_state() звідси — нитка чекає на себе.",
                                    "Вихід — gst_element_call_async()."],
                         size=12.5, pad=10, stroke=POS, sw=2, min_w=420)
    f.append(body)

    render(os.path.join(IMG, "probe-in-stack.svg"), W, H, *f,
           title="Проба виконується всередині чужого стеку, під замком потоку")


# ── Життя задачі пада й повідомлення STREAM_STATUS ─────────────────────────
def fig_task_lifecycle():
    W, H = 1000, 680
    f = []
    L, R = 262, 730

    f.append(text(L, 76, "нитка, що активує пад", size=15, bold=True))
    f.append(text(R, 76, "нитка потоку — з пулу задач", size=15, bold=True))

    rows = [
        (L, 145, ["gst_pad_start_task (pad, func, …)"], INK, 2.0),
        (L, 225, ["STREAM_STATUS · CREATE",
                  "синхронний обробник: gst_task_set_pool()"], POS, 2.5),
        (L, 305, ["STREAM_STATUS · START"], POS, 2.0),
        (R, 405, ["STREAM_STATUS · ENTER",
                  "тут виставляють пріоритет нитки"], FIELD, 2.5),
        (R, 490, ["func() у циклі, замок потоку взято"], INK, 2.0),
        (R, 570, ["STREAM_STATUS · LEAVE",
                  "нитка вертається в пул"], FIELD, 2.5),
    ]
    geom = []
    for cx, cy, lines, col, sw in rows:
        body, w, h = textbox(cx, cy, lines, size=13.5, pad=11, stroke=col, sw=sw)
        f.append(body)
        geom.append((cx, cy, w, h))

    for i in (0, 1, 3, 4):
        _, cy, _, h = geom[i]
        _, cy2, _, h2 = geom[i + 1]
        if geom[i][0] == geom[i + 1][0]:
            f.append(arrow(geom[i][0], cy + h / 2 + 3, geom[i][0], cy2 - h2 / 2 - 3))

    # перехід у нову нитку: задача стартувала — нитку дав пул
    f.append(arrow(L + 60, geom[2][1] + geom[2][3] / 2 + 4,
                   R - geom[3][2] / 2 - 8, geom[3][1] - 14))

    f.append(text(W / 2, 646,
                  "PAUSE і STOP приходять з нитки, яка міняє стан задачі: "
                  "gst_pad_pause_task() / gst_pad_stop_task()",
                  size=12.5, color=MUTED))

    render(os.path.join(IMG, "task-lifecycle.svg"), W, H, *f,
           title="Хто посилає STREAM_STATUS і в якій нитці")


if __name__ == "__main__":
    fig_thread_map()
    fig_tee_deadlock()
    fig_queue_inside()
    fig_multiqueue()
    fig_cothread_stacks()
    fig_probe_in_stack()
    fig_task_lifecycle()
    print("ok")
